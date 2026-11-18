from copy import deepcopy

import pytest
from pydantic import ValidationError
from support import INVALID_REQUEST_CASES, make_request, make_world, override_tables
from tome.engine import errors, models, text


def test_normalization_vectors():
    assert text.matches('  "Fact"  ', "Fact")
    assert text.matches("'Fact'", "Fact")
    assert not text.is_non_whitespace('""')
    assert not text.is_non_whitespace("  ")
    assert not text.matches("“Fact”", "Fact")
    assert text.normalize('""Fact""') == '"Fact"'
    assert not text.matches("fact", "Fact")
    assert text.normalize(" ' Fact ' ") == "Fact"
    assert text.find_match('"Fact"', ["Other", " Fact "]) == " Fact "
    assert text.find_match("missing", ["Fact"]) is None
    assert text.has_matching_pair(["Fact", '"Fact"'])
    assert not text.has_matching_pair(["Fact", "fact"])


@pytest.mark.parametrize(
    "case_id,mutator", INVALID_REQUEST_CASES, ids=lambda x: x if isinstance(x, str) else None
)
def test_run_request_model_rejects_invalid_values(case_id, mutator):
    request = make_request()
    mutator(request)
    with pytest.raises(ValidationError):
        models.RunRequest.model_validate(request)


def test_nested_model_instances_revalidated():
    state = models.WorldState.model_construct(**make_world(canon=("  ",)))
    with pytest.raises(ValidationError):
        models.RunRequest.model_validate(make_request(world=state))
    actor = models.Actor.model_construct(id='""', name="Actor A", agenda="Agenda A")
    world = make_world()
    world["actors"][0] = actor
    with pytest.raises(ValidationError):
        models.WorldState.model_validate(world)


@pytest.mark.parametrize("level", ["world", "actor"])
def test_closed_schemas_reject_unknown_fields(level):
    world = make_world()
    target = world if level == "world" else world["actors"][0]
    target["unknown"] = "value"
    with pytest.raises(ValidationError):
        models.WorldState.model_validate(world)


@pytest.mark.parametrize(
    "field", ["traits", "posture", "exhausted_traits", "active_rumors", "goal_alignment"]
)
def test_removed_fields_rejected(field):
    if field == "goal_alignment":
        value = {
            "voter_actor_id": "actor_b",
            "baseline_plausibility": 0,
            "biased_shift_applied": False,
            "cited_anchor": None,
            "final_vote": 0,
            "public_argument": "",
            "goal_alignment": 0,
        }
        with pytest.raises(ValidationError):
            models.PeerEvaluation.model_validate(value)
    else:
        world = make_world()
        target = world if field == "active_rumors" else world["actors"][0]
        target[field] = []
        with pytest.raises(ValidationError):
            models.WorldState.model_validate(world)


def test_spark_tables_validation():
    tables = override_tables()
    expected_keys = {str(10 * t + u) for t in range(1, 7) for u in range(1, 7)}
    strings = models.SparkTables.model_validate(tables)
    integers = models.SparkTables.model_validate(
        {name: {int(k): v for k, v in table.items()} for name, table in tables.items()}
    )
    assert strings == integers
    assert strings.model_dump(mode="json") == tables
    assert all(set(table) == expected_keys for table in strings.model_dump(mode="json").values())
    invalid = []
    for bad_key in [11, True, "17", "011", "11\n"]:
        changed = deepcopy(tables)
        changed["Action"][bad_key] = changed["Action"].pop("11")
        invalid.append(changed)
    missing_key = deepcopy(tables)
    del missing_key["Action"]["11"]
    invalid.append(missing_key)
    invalid.append({k: v for k, v in tables.items() if k != "Action"})
    invalid.append({**tables, "Other": tables["Action"]})
    invalid.append({**tables, "Action": None})
    invalid.append({**tables, "Action": list(tables["Action"].items())})
    for value in [" ", '""', 1, None]:
        invalid.append(override_tables({("Action", 11): value}))
    for value in invalid:
        with pytest.raises(ValidationError):
            models.SparkTables.model_validate(value)


@pytest.mark.parametrize(
    "field,value",
    [
        ("session_index", True),
        ("turn_index", True),
        ("session_index", -1),
        ("turn_index", -1),
        ("canon_facts", ("Fact 1.",)),
        ("canon_facts", [1]),
        ("actors", tuple(make_world()["actors"])),
    ],
)
def test_world_strict_python_values(field, value):
    world = make_world()
    world[field] = value
    with pytest.raises(ValidationError):
        models.WorldState.model_validate(world)


def test_optional_defaults_and_verbatim_text():
    request = models.RunRequest.model_validate(
        make_request(
            world=make_world((" actor_a ",), canon=('  "Fact 1."  ',)),
        )
    )
    assert request.spark_tables is request.first_round_order is request.seed is None
    assert request.world_state.canon_facts == ['  "Fact 1."  ']
    assert request.world_state.actors[0].id == " actor_a "
    assert (
        models.RunRequest.model_validate(
            make_request(world=make_world(canon=()))
        ).world_state.canon_facts
        == []
    )
    for bad in [True, 1.0, "1"]:
        with pytest.raises(ValidationError):
            models.RunRequest.model_validate(make_request(turn_count=bad))


@pytest.mark.parametrize(
    "error_cls,code",
    [
        (errors.InvalidRunRequestError, "INVALID_RUN_REQUEST"),
        (errors.ProposalGenerationError, "PROPOSAL_GENERATION_FAILED"),
        (errors.InvalidProposalError, "INVALID_PROPOSAL"),
        (errors.PeerReviewError, "PEER_REVIEW_FAILED"),
        (errors.UmpireReviewError, "UMPIRE_REVIEW_FAILED"),
        (errors.UmpireResolutionError, "UMPIRE_RESOLUTION_FAILED"),
        (errors.MechanicsError, "MECHANICS_FAILED"),
    ],
)
def test_error_codes_and_failure_payload(error_cls, code):
    error = error_cls("Explanation.")
    assert isinstance(error, errors.RunError)
    assert error.code == code
    assert error.message == str(error) == "Explanation."
    assert error.to_failure().model_dump() == {
        "contract_version": "1.1.0",
        "code": code,
        "message": "Explanation.",
    }
