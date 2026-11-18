import random
from collections.abc import Mapping
from copy import deepcopy
from itertools import combinations
from types import MappingProxyType

import pytest
from pydantic import ValidationError
from support import INVALID_REQUEST_CASES, make_request, make_world, override_tables

from tome import tables as built_in_tables
from tome.engine import errors, gates, mechanics, models, text


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


@pytest.mark.parametrize(
    "case",
    [
        "non-mapping",
        "missing",
        "extra",
        "blank",
        "quoted-empty",
        "source-type",
        "zero-pros",
        "three-pros",
        "tuple-pros",
    ],
)
def test_proposal_shape_errors(case):
    draft = {
        "world_change_statement": "New event.",
        "supporting_pros": [{"source_type": "canon_fact", "source_ref": "Fact 1.", "argument": ""}],
    }
    if case == "non-mapping":
        draft = "not a mapping"
    elif case == "missing":
        del draft["world_change_statement"]
    elif case == "extra":
        draft["active_actor_id"] = "actor_a"
    elif case == "blank":
        draft["world_change_statement"] = "  "
    elif case == "quoted-empty":
        draft["world_change_statement"] = '""'
    elif case == "source-type":
        draft["supporting_pros"][0]["source_type"] = "actor_trait"
    elif case == "zero-pros":
        draft["supporting_pros"] = []
    elif case == "three-pros":
        draft["supporting_pros"] *= 3
    else:
        draft["supporting_pros"] = tuple(draft["supporting_pros"])
    cues = mechanics.TurnCues(1, "Obvious", ("Action", "Focus"), (11, 11), ("Action:X", "Focus:Y"))
    with pytest.raises(errors.ProposalGenerationError):
        gates.build_proposal(draft, active_actor_id="actor_a", cues=cues, canon_facts=["Fact 1."])


@pytest.mark.parametrize("statement", ["Fact 1.", '  "Fact 1."  ', "'Fact 1.'"])
def test_proposal_duplicating_canon_rejected(statement):
    cues = mechanics.TurnCues(1, "Obvious", ("Action", "Focus"), (11, 11), ("Action:X", "Focus:Y"))
    draft = {
        "world_change_statement": statement,
        "supporting_pros": [{"source_type": "canon_fact", "source_ref": "Fact 1.", "argument": ""}],
    }
    with pytest.raises(errors.InvalidProposalError):
        gates.build_proposal(draft, active_actor_id="actor_a", cues=cues, canon_facts=["Fact 1."])
    draft["supporting_pros"] *= 3
    with pytest.raises(errors.ProposalGenerationError):
        gates.build_proposal(draft, active_actor_id="actor_a", cues=cues, canon_facts=["Fact 1."])


def test_proposal_pruning_and_attachment():
    cues = mechanics.TurnCues(6, "Odd", ("Focus", "Method"), (66, 13), ("Focus:X", "Method:Y"))
    draft = {
        "world_change_statement": '  "New event."  ',
        "supporting_pros": [
            {"source_type": "canon_fact", "source_ref": "Invented", "argument": "Prune me."},
            {"source_type": "canon_fact", "source_ref": ' "Fact 1." ', "argument": "Keep me."},
        ],
    }
    before = deepcopy(draft)
    result = gates.build_proposal(
        MappingProxyType(draft), active_actor_id="actor_a", cues=cues, canon_facts=["Fact 1."]
    )
    assert result.model_dump() == {
        "active_actor_id": "actor_a",
        "posture_roll": 6,
        "trio_tier": "Odd",
        "spark_tags": ["Focus:X", "Method:Y"],
        "world_change_statement": '  "New event."  ',
        "supporting_pros": [draft["supporting_pros"][1]],
    }
    assert draft == before


def test_proposal_without_grounded_pros_rejected():
    cues = mechanics.TurnCues(1, "Obvious", ("Action", "Focus"), (11, 11), ("Action:X", "Focus:Y"))
    draft = {
        "world_change_statement": "New event.",
        "supporting_pros": [
            {"source_type": "canon_fact", "source_ref": "Invented", "argument": ""}
        ],
    }
    with pytest.raises(errors.InvalidProposalError):
        gates.build_proposal(draft, active_actor_id="actor_a", cues=cues, canon_facts=["Fact 1."])


@pytest.mark.parametrize("reference", ["Actor A", "Agenda A", "Action:X", "X"])
def test_sparks_and_actor_metadata_do_not_ground(reference):
    cues = mechanics.TurnCues(1, "Obvious", ("Action", "Focus"), (11, 11), ("Action:X", "Focus:Y"))
    draft = {
        "world_change_statement": "New event.",
        "supporting_pros": [{"source_type": "canon_fact", "source_ref": reference, "argument": ""}],
    }
    with pytest.raises(errors.InvalidProposalError):
        gates.build_proposal(draft, active_actor_id="actor_a", cues=cues, canon_facts=["Fact 1."])
    evaluation = models.PeerEvaluation(
        voter_actor_id="actor_b",
        baseline_plausibility=0,
        final_vote=1,
        biased_shift_applied=True,
        cited_anchor=reference,
        public_argument="",
    )
    assert (
        gates.validate_peer_evaluation(
            evaluation, voter_actor_id="actor_b", canon_facts=["Fact 1."]
        ).final_vote
        == 0
    )
    assert (
        gates.validate_peer_evaluation(
            evaluation, voter_actor_id="actor_b", canon_facts=[reference]
        ).final_vote
        == 1
    )


def test_canon_fact_reusable_across_turns():
    canon = ["Fact 1."]
    cues = mechanics.TurnCues(1, "Obvious", ("Action", "Focus"), (11, 11), ("Action:X", "Focus:Y"))
    for i in range(3):
        proposal = gates.build_proposal(
            {
                "world_change_statement": f"Event {i}.",
                "supporting_pros": [
                    {"source_type": "canon_fact", "source_ref": "Fact 1.", "argument": ""}
                ],
            },
            active_actor_id="actor_a",
            cues=cues,
            canon_facts=canon,
        )
        assert proposal.supporting_pros[0].source_ref == "Fact 1."
    assert canon == ["Fact 1."]


def test_historical_canon_grounding():
    canon = ["Actor A has capability X", "Actor A loses capability X"]
    cues = mechanics.TurnCues(1, "Obvious", ("Action", "Focus"), (11, 11), ("Action:X", "Focus:Y"))
    for fact in canon:
        draft = {
            "world_change_statement": "New event.",
            "supporting_pros": [
                {
                    "source_type": "canon_fact",
                    "source_ref": fact,
                    "argument": "Historical reference.",
                },
            ],
        }
        assert (
            gates.build_proposal(draft, active_actor_id="actor_a", cues=cues, canon_facts=canon)
            .supporting_pros[0]
            .source_ref
            == fact
        )
        draft["world_change_statement"] = f' "{fact}" '
        with pytest.raises(errors.InvalidProposalError):
            gates.build_proposal(draft, active_actor_id="actor_a", cues=cues, canon_facts=canon)
        with pytest.raises(errors.UmpireResolutionError):
            gates.validate_failure_resolution(
                {
                    "source_voter_actor_id": None,
                    "world_change_statement": f' "{fact}" ',
                    "rationale": "Reason.",
                },
                candidate_voter_ids=[],
                canon_facts=canon,
                rejected_statement="Proposal.",
            )
    evaluation = gates.validate_peer_evaluation(
        {
            "voter_actor_id": "actor_b",
            "baseline_plausibility": 0,
            "final_vote": 1,
            "biased_shift_applied": False,
            "cited_anchor": canon[0],
            "public_argument": "History.",
        },
        voter_actor_id="actor_b",
        canon_facts=canon,
    )
    assert evaluation.final_vote == 1
    after, records = gates.apply_umpire_rejections(
        [
            {
                "voter_actor_id": "actor_b",
                "reason": "No longer relevant.",
            }
        ],
        evaluations=[evaluation],
    )
    assert after[0].final_vote == 0
    assert records[0].evaluation_before_reversion == evaluation
    assert canon == ["Actor A has capability X", "Actor A loses capability X"]


@pytest.mark.parametrize("baseline,final", [(1, -1), (-1, 1)])
def test_two_step_shift_reverts(baseline, final):
    evaluation = gates.validate_peer_evaluation(
        {
            "voter_actor_id": "actor_b",
            "baseline_plausibility": baseline,
            "final_vote": final,
            "biased_shift_applied": True,
            "cited_anchor": "Fact 1.",
            "public_argument": "Original.",
        },
        voter_actor_id="actor_b",
        canon_facts=["Fact 1."],
    )
    assert evaluation.final_vote == baseline
    assert evaluation.biased_shift_applied is False
    assert evaluation.cited_anchor is None
    assert evaluation.public_argument == "Original."


@pytest.mark.parametrize("baseline", [-1, 0, 1])
@pytest.mark.parametrize("final", [-1, 0, 1])
def test_votes_stay_in_range(baseline, final):
    evaluation = gates.validate_peer_evaluation(
        {
            "voter_actor_id": "actor_b",
            "baseline_plausibility": baseline,
            "final_vote": final,
            "biased_shift_applied": False,
            "cited_anchor": "Fact 1.",
            "public_argument": "",
        },
        voter_actor_id="actor_b",
        canon_facts=["Fact 1."],
    )
    assert evaluation.final_vote in {-1, 0, 1}
    assert abs(evaluation.final_vote - baseline) <= 1


@pytest.mark.parametrize(
    "baseline,final,flag,anchor,expected",
    [
        (0, 1, False, '  "Fact 1."  ', 1),
        (1, 0, False, "Fact 1.", 0),
        (0, 1, True, None, 0),
        (0, -1, True, "Invented", 0),
        (1, 1, True, "Fact 1.", 1),
    ],
)
def test_shift_metadata_follows_numeric_shift(baseline, final, flag, anchor, expected):
    evaluation = gates.validate_peer_evaluation(
        {
            "voter_actor_id": "actor_b",
            "baseline_plausibility": baseline,
            "final_vote": final,
            "biased_shift_applied": flag,
            "cited_anchor": anchor,
            "public_argument": "Unchanged.",
        },
        voter_actor_id="actor_b",
        canon_facts=["Fact 1."],
    )
    assert evaluation.final_vote == expected
    assert evaluation.biased_shift_applied is (expected != baseline)
    assert evaluation.cited_anchor == ("Fact 1." if expected != baseline else None)
    assert evaluation.baseline_plausibility == baseline
    assert evaluation.public_argument == "Unchanged."


def test_peer_voter_id_compared_exactly():
    with pytest.raises(errors.PeerReviewError):
        gates.validate_peer_evaluation(
            {
                "voter_actor_id": '"actor_b"',
                "baseline_plausibility": 0,
                "final_vote": 0,
                "biased_shift_applied": False,
                "cited_anchor": None,
                "public_argument": "",
            },
            voter_actor_id="actor_b",
            canon_facts=["Fact 1."],
        )


@pytest.mark.parametrize("case", ["missing", "extra", "bool", "out-of-range", "non-mapping"])
def test_peer_shape_errors(case):
    raw = {
        "voter_actor_id": "actor_b",
        "baseline_plausibility": 0,
        "final_vote": 0,
        "biased_shift_applied": False,
        "cited_anchor": None,
        "public_argument": "",
    }
    if case == "missing":
        del raw["biased_shift_applied"]
    elif case == "extra":
        raw["goal_alignment"] = 0
    elif case == "bool":
        raw["final_vote"] = True
    elif case == "out-of-range":
        raw["final_vote"] = 2
    else:
        raw = None
    with pytest.raises(errors.PeerReviewError):
        gates.validate_peer_evaluation(raw, voter_actor_id="actor_b", canon_facts=["Fact 1."])


@pytest.mark.parametrize("baseline", [1, -1])
def test_umpire_rejection_reverts_and_records(baseline):
    evaluation = gates.validate_peer_evaluation(
        {
            "voter_actor_id": "actor_b",
            "baseline_plausibility": baseline,
            "final_vote": 0,
            "biased_shift_applied": False,
            "cited_anchor": '  "Fact 1."  ',
            "public_argument": "Keep original.",
        },
        voter_actor_id="actor_b",
        canon_facts=["Fact 1."],
    )
    assert evaluation.biased_shift_applied is True
    after, records = gates.apply_umpire_rejections(
        [
            {
                "voter_actor_id": "actor_b",
                "reason": "Illogical.",
            }
        ],
        evaluations=[evaluation],
    )
    assert after[0].final_vote == baseline
    assert after[0].biased_shift_applied is False and after[0].cited_anchor is None
    assert after[0].public_argument == "Keep original."
    assert after[0].baseline_plausibility == baseline
    assert records[0].reason == "Illogical."
    assert records[0].evaluation_before_reversion == evaluation
    assert records[0].evaluation_before_reversion is not evaluation
    after[0].public_argument = "Mutated."
    assert records[0].evaluation_before_reversion.public_argument == "Keep original."
    assert evaluation.final_vote == 0


def test_umpire_records_in_peer_order():
    evaluations = [
        models.PeerEvaluation(
            voter_actor_id=actor_id,
            baseline_plausibility=0,
            final_vote=1,
            biased_shift_applied=True,
            cited_anchor="Fact 1.",
            public_argument=actor_id,
        )
        for actor_id in ["actor_c", "actor_b", "actor_d"]
    ]
    after, records = gates.apply_umpire_rejections(
        [
            {"voter_actor_id": "actor_b", "reason": "B."},
            {"voter_actor_id": "actor_c", "reason": "C."},
        ],
        evaluations=evaluations,
    )
    assert [r.voter_actor_id for r in records] == ["actor_c", "actor_b"]
    assert [e.final_vote for e in after] == [0, 0, 1]
    assert [e.final_vote for e in evaluations] == [1, 1, 1]
    assert all(a is not b for a, b in zip(after, evaluations))


@pytest.mark.parametrize(
    "raw",
    [
        [{"voter_actor_id": "actor_b", "reason": "Reason."}] * 2,
        [{"voter_actor_id": "unknown", "reason": "Reason."}],
        [{"voter_actor_id": "actor_a", "reason": "Reason."}],
        [{"voter_actor_id": "actor_c", "reason": "At baseline."}],
        [{"voter_actor_id": '"actor_b"', "reason": "Inexact."}],
        [{"voter_actor_id": "actor_b", "reason": " "}],
        [{"voter_actor_id": "actor_b", "reason": "Reason.", "extra": 1}],
        (),
        None,
        {},
    ],
)
def test_umpire_rejection_errors(raw):
    evaluations = [
        models.PeerEvaluation(
            voter_actor_id=actor_id,
            baseline_plausibility=0,
            final_vote=vote,
            biased_shift_applied=bool(vote),
            cited_anchor="Fact 1." if vote else None,
            public_argument="",
        )
        for actor_id, vote in [("actor_b", 1), ("actor_c", 0)]
    ]
    with pytest.raises(errors.UmpireReviewError):
        gates.apply_umpire_rejections(raw, evaluations=evaluations)


@pytest.mark.parametrize(
    "votes,expected",
    [
        ([-1, -1, 0], ["v0", "v1"]),
        ([0, 0], ["v0", "v1"]),
        ([1, 1], ["v0", "v1"]),
        ([1], ["v0"]),
        ([], []),
    ],
)
def test_lowest_vote_candidates(votes, expected):
    evaluations = [
        models.PeerEvaluation(
            voter_actor_id=f"v{i}",
            baseline_plausibility=vote,
            final_vote=vote,
            biased_shift_applied=False,
            cited_anchor=None,
            public_argument="",
        )
        for i, vote in enumerate(votes)
    ]
    assert gates.lowest_vote_candidates(evaluations) == expected


def test_failure_resolution_validation():
    for source, statement in [
        ("actor_b", "Original peer argument."),
        ("actor_b", "Restated event."),
        (None, ' "New event." '),
    ]:
        raw = {
            "source_voter_actor_id": source,
            "world_change_statement": statement,
            "rationale": " Umpire decision. ",
        }
        assert (
            gates.validate_failure_resolution(
                raw,
                candidate_voter_ids=["actor_b"],
                canon_facts=["Fact 1."],
                rejected_statement="Proposal.",
            ).model_dump()
            == raw
        )
    invalid = [
        {"source_voter_actor_id": "actor_c"},
        {"source_voter_actor_id": "unknown"},
        {"source_voter_actor_id": '"actor_b"'},
        {"world_change_statement": ""},
        {"world_change_statement": '""'},
        {"world_change_statement": ' "Fact 1." '},
        {"world_change_statement": ' "Proposal." '},
        {"rationale": " "},
        {"rationale": '""'},
        {"extra": 1},
    ]
    for changes in invalid:
        raw = {
            "source_voter_actor_id": "actor_b",
            "world_change_statement": "New event.",
            "rationale": "Reason.",
            **changes,
        }
        with pytest.raises(errors.UmpireResolutionError):
            gates.validate_failure_resolution(
                raw,
                candidate_voter_ids=["actor_b"],
                canon_facts=["Fact 1."],
                rejected_statement="Proposal.",
            )
    for raw in [
        None,
        {
            "source_voter_actor_id": "actor_b",
            "world_change_statement": "New event.",
            "rationale": "Reason.",
        },
    ]:
        with pytest.raises(errors.UmpireResolutionError):
            gates.validate_failure_resolution(
                raw, candidate_voter_ids=[], canon_facts=["Fact 1."], rejected_statement="Proposal."
            )


@pytest.mark.parametrize(
    "exception", [ValueError, RecursionError, SystemError, MemoryError, KeyboardInterrupt]
)
@pytest.mark.parametrize("kind", ["mapping", "model"])
def test_callback_output_conversion_exception_boundaries(exception, kind):
    original = exception("Conversion failed.")

    class BrokenMapping(Mapping):
        def __iter__(self):
            raise original

        def __len__(self):
            return 1

        def __getitem__(self, key):
            raise original

    class BrokenDraft(models.ProposalDraft):
        def model_dump(self, **kwargs):
            raise original

    raw = BrokenMapping() if kind == "mapping" else BrokenDraft.model_construct()
    expected = (
        exception
        if exception in (MemoryError, KeyboardInterrupt)
        else errors.ProposalGenerationError
    )
    with pytest.raises(expected) as caught:
        gates._validate_output(raw, models.ProposalDraft, errors.ProposalGenerationError)
    if expected is errors.ProposalGenerationError:
        assert caught.value.__cause__ is original
    else:
        assert caught.value is original
