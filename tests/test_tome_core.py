import random
from copy import deepcopy
from itertools import combinations

import pytest
from pydantic import ValidationError
from support import INVALID_REQUEST_CASES, make_request, make_world, override_tables

from tome import tables as built_in_tables
from tome.engine import errors, mechanics, models, text


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


@pytest.mark.parametrize(
    "roll,tier",
    [
        (1, "Obvious"),
        (2, "Obvious"),
        (3, "Obvious"),
        (4, "Option"),
        (5, "Option"),
        (6, "Odd"),
    ],
)
def test_tier_mapping_exhaustive(roll, tier):
    assert mechanics.tier_for_roll(roll) == tier


@pytest.mark.parametrize("roll", [0, 7, True, 1.0])
def test_tier_mapping_rejects_invalid_faces(roll):
    with pytest.raises(errors.MechanicsError):
        mechanics.tier_for_roll(roll)


def test_golden_vector_seed_42():
    rng = random.Random(42)
    assert mechanics.first_round_order(rng, ["actor_a", "actor_b"], None) == ["actor_b", "actor_a"]
    cues = mechanics.draw_turn_cues(rng, mechanics.default_spark_tables())
    assert (cues.posture_roll, cues.trio_tier) == (1, "Obvious")
    assert cues.table_names == ("Method", "Focus")
    assert cues.d66_keys == (22, 61)
    assert mechanics.roll_resolution(rng) == (6, 6)


def test_golden_vector_unsorted_seed_4():
    rng = random.Random(4)
    assert mechanics.first_round_order(rng, ["actor_c", "actor_a", "actor_b"], None) == [
        "actor_b",
        "actor_a",
        "actor_c",
    ]
    cues = mechanics.draw_turn_cues(rng, mechanics.default_spark_tables())
    assert (cues.posture_roll, cues.trio_tier) == (1, "Obvious")
    assert cues.table_names == ("Disposition", "Motivation")
    assert cues.d66_keys == (21, 11)
    assert mechanics.roll_resolution(rng) == (4, 5)


@pytest.mark.parametrize("supplied", [None, ["actor_b", "actor_c", "actor_a"]])
def test_draw_sequence_matches_reference(supplied):
    tables = mechanics.default_spark_tables()
    actors = ["actor_c", "actor_a", "actor_b"]
    for seed in range(200):
        expected_rng, actual_rng = random.Random(seed), random.Random(seed)
        expected_order = list(actors if supplied is None else supplied)
        if supplied is None:
            expected_rng.shuffle(expected_order)
        actual_order = mechanics.first_round_order(actual_rng, actors, supplied)
        assert actual_order == expected_order
        assert actual_order is not actors and actual_order is not supplied
        for _ in range(3):
            roll = expected_rng.randint(1, 6)
            names = expected_rng.sample(
                ["Action", "Focus", "Method", "Disposition", "Motivation"], 2
            )
            keys = tuple(
                10 * expected_rng.randint(1, 6) + expected_rng.randint(1, 6) for _ in names
            )
            cues = mechanics.draw_turn_cues(actual_rng, tables)
            assert cues.posture_roll == roll
            assert cues.table_names == tuple(names)
            assert cues.d66_keys == keys
            assert cues.spark_tags == tuple(
                f"{name}:{getattr(tables, name)[key]}" for name, key in zip(names, keys)
            )
            dice = (expected_rng.randint(1, 6), expected_rng.randint(1, 6))
            assert mechanics.roll_resolution(actual_rng) == dice
        assert actors == ["actor_c", "actor_a", "actor_b"]


def test_draws_ignore_table_contents_and_key_order():
    override = override_tables()
    reversed_tables = {
        name: dict(reversed(list(table.items())))
        for name, table in reversed(list(override.items()))
    }
    sources = [
        mechanics.default_spark_tables(),
        models.SparkTables.model_validate(override),
        models.SparkTables.model_validate(reversed_tables),
    ]
    for seed in range(200):
        results = []
        for tables in sources:
            rng = random.Random(seed)
            cues = mechanics.draw_turn_cues(rng, tables)
            results.append(
                (cues.posture_roll, cues.table_names, cues.d66_keys, mechanics.roll_resolution(rng))
            )
        assert results[0] == results[1] == results[2]


def test_all_table_pairs_eligible_for_every_tier():
    seen = set()
    tables = mechanics.default_spark_tables()
    for seed in range(5000):
        cues = mechanics.draw_turn_cues(random.Random(seed), tables)
        assert len(set(cues.table_names)) == 2
        seen.add((cues.trio_tier, frozenset(cues.table_names)))
    assert seen == {
        (tier, frozenset(pair))
        for tier in ("Obvious", "Option", "Odd")
        for pair in combinations(("Action", "Focus", "Method", "Disposition", "Motivation"), 2)
    }


def test_tables_reusable_across_turns():
    rng = random.Random(42)
    tables = mechanics.default_spark_tables()
    names = []
    for _ in range(20):
        names.extend(mechanics.draw_turn_cues(rng, tables).table_names)
        mechanics.roll_resolution(rng)
    assert len(set(names)) == 5
    assert all(names.count(name) > 1 for name in set(names))


@pytest.mark.parametrize("vote_sum", range(-6, 7))
def test_net_modifier_clamps(vote_sum):
    votes = [1 if vote_sum > 0 else -1] * abs(vote_sum)
    assert mechanics.net_vote_modifier(iter(votes)) == max(-3, min(3, vote_sum))


@pytest.mark.parametrize(
    "total,outcome", [(-1, "Failure"), (6, "Failure"), (7, "Success"), (15, "Success")]
)
def test_outcome_boundaries(total, outcome):
    assert mechanics.resolve_outcome(total) == outcome


def test_default_tables_are_trio_d66_v1():
    assert mechanics.DEFAULT_TABLE_SET_ID == "trio-d66-v1"
    assert mechanics.default_spark_tables().model_dump() == {
        name: getattr(built_in_tables, f"TABLE_{name.upper()}")
        for name in ("Action", "Focus", "Method", "Disposition", "Motivation")
    }


def test_mechanics_checks_dice_and_table_lookups(monkeypatch):
    class BadDie(random.Random):
        def randint(self, a, b):
            return 0

    with pytest.raises(errors.MechanicsError):
        mechanics.draw_turn_cues(BadDie(), mechanics.default_spark_tables())
    with pytest.raises(errors.MechanicsError):
        mechanics.roll_resolution(BadDie())
    tables = mechanics.default_spark_tables()
    tables.Action.clear()
    tables.Focus.clear()
    tables.Method.clear()
    tables.Disposition.clear()
    tables.Motivation.clear()
    with pytest.raises(errors.MechanicsError):
        mechanics.draw_turn_cues(random.Random(0), tables)
    monkeypatch.setattr(mechanics, "TABLE_ACTION", {})
    with pytest.raises(errors.MechanicsError):
        mechanics.default_spark_tables()
