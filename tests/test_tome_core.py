import asyncio
import concurrent.futures
import inspect
import random
from collections.abc import Mapping
from copy import deepcopy
from itertools import combinations
from types import MappingProxyType

import pytest
from pydantic import ValidationError
from support import (
    INVALID_REQUEST_CASES,
    ScriptedCallbacks,
    make_request,
    make_world,
    override_tables,
    seed_for_base_roll,
)

import tome
from tome import tables as built_in_tables
from tome.engine import errors, gates, mechanics, models, protocols, runner, text


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


def test_required_callables_checked_first(monkeypatch):
    callbacks = ScriptedCallbacks()
    rng_calls = []
    real_random = random.Random

    def spy(*args, **kwargs):
        rng_calls.append((args, kwargs))
        return real_random(*args, **kwargs)

    monkeypatch.setattr(runner.random, "Random", spy)
    valid = {
        "proposal_generator": callbacks.proposal_generator,
        "peer_reviewer": callbacks.peer_reviewer,
        "failure_resolver": callbacks.failure_resolver,
        "umpire_review": None,
    }
    for name in valid:
        for bad in [None, "x"]:
            if name == "umpire_review" and bad is None:
                continue
            with pytest.raises(errors.InvalidRunRequestError):
                runner.run(make_request(), **{**valid, name: bad})
            assert not rng_calls
            assert not any(
                [
                    callbacks.proposal_calls,
                    callbacks.peer_calls,
                    callbacks.failure_calls,
                    callbacks.umpire_calls,
                ]
            )
    runner.run(make_request(seed=20), **valid)
    assert len(rng_calls) == 1


@pytest.mark.parametrize(
    "case_id,mutator", INVALID_REQUEST_CASES, ids=lambda x: x if isinstance(x, str) else None
)
def test_run_rejects_invalid_request_before_callbacks(case_id, mutator, monkeypatch):
    request = make_request()
    mutator(request)
    before = deepcopy(request)
    callbacks = ScriptedCallbacks()
    rng_calls = []
    monkeypatch.setattr(runner.random, "Random", lambda *args: rng_calls.append(args))
    with pytest.raises(errors.InvalidRunRequestError) as caught:
        runner.run(
            request,
            callbacks.proposal_generator,
            callbacks.peer_reviewer,
            callbacks.failure_resolver,
        )
    assert request == before
    assert not rng_calls
    assert not any(
        [
            callbacks.proposal_calls,
            callbacks.peer_calls,
            callbacks.umpire_calls,
            callbacks.failure_calls,
        ]
    )
    assert not hasattr(caught.value, "partial_result")


def test_run_accepts_mapping_and_model():
    request = make_request(seed=20, first_round_order=["actor_a", "actor_b"])
    results = []
    for value in [request, MappingProxyType(request), models.RunRequest.model_validate(request)]:
        callbacks = ScriptedCallbacks()
        results.append(
            runner.run(
                value,
                callbacks.proposal_generator,
                callbacks.peer_reviewer,
                callbacks.failure_resolver,
            ).model_dump(mode="json")
        )
    assert results[0] == results[1] == results[2]


@pytest.mark.parametrize("request", ['{"contract_version": "1.1.0"}', [], None])
def test_run_rejects_non_mapping_request(request, monkeypatch):
    callbacks = ScriptedCallbacks()
    rng_calls = []
    monkeypatch.setattr(runner.random, "Random", lambda *args: rng_calls.append(args))
    with pytest.raises(errors.InvalidRunRequestError):
        runner.run(
            request,
            callbacks.proposal_generator,
            callbacks.peer_reviewer,
            callbacks.failure_resolver,
        )
    assert not callbacks.proposal_calls and not callbacks.peer_calls and not callbacks.failure_calls
    assert not rng_calls


def test_spark_table_source_and_tags():
    results = []
    for optional in [{}, {"spark_tables": override_tables()}]:
        callbacks = ScriptedCallbacks()
        results.append(
            runner.run(
                make_request(seed=20, first_round_order=["actor_a", "actor_b"], **optional),
                callbacks.proposal_generator,
                callbacks.peer_reviewer,
                callbacks.failure_resolver,
            )
        )
    default, override = results
    assert default.spark_table_source == "trio-d66-v1"
    assert override.spark_table_source == "request"
    a, b = default.turn_records[0], override.turn_records[0]
    assert a.proposal.spark_tags == [
        f"Focus:{built_in_tables.TABLE_FOCUS[66]}",
        f"Method:{built_in_tables.TABLE_METHOD[13]}",
    ]
    assert b.proposal.spark_tags == ["Focus:Focus 66", "Method:Method 13"]
    assert a.proposal.posture_roll == b.proposal.posture_roll == 6
    assert [tag.split(":")[0] for tag in a.proposal.spark_tags] == [
        tag.split(":")[0] for tag in b.proposal.spark_tags
    ]
    assert a.resolution_roll == b.resolution_roll == 7


def test_generator_receives_tier_and_both_tags():
    callbacks = ScriptedCallbacks()
    result = runner.run(
        make_request(seed=20),
        callbacks.proposal_generator,
        callbacks.peer_reviewer,
        callbacks.failure_resolver,
    )
    actor, tier, tags, state = callbacks.proposal_calls[0]
    proposal = result.turn_records[0].proposal
    assert actor.id == proposal.active_actor_id
    assert tier == proposal.trio_tier
    assert tags == proposal.spark_tags and len(tags) == 2
    assert state == models.WorldState.model_validate(make_world())


def test_one_ordered_evaluation_per_peer():
    callbacks = ScriptedCallbacks()
    result = runner.run(
        make_request(
            world=make_world(("actor_c", "actor_a", "actor_b")),
            seed=20,
            first_round_order=["actor_a", "actor_b", "actor_c"],
        ),
        callbacks.proposal_generator,
        callbacks.peer_reviewer,
        callbacks.failure_resolver,
    )
    assert [call[0].id for call in callbacks.peer_calls] == ["actor_c", "actor_b"]
    assert [e.voter_actor_id for e in result.turn_records[0].peer_evaluations] == [
        "actor_c",
        "actor_b",
    ]
    assert all(call[1] == result.turn_records[0].proposal for call in callbacks.peer_calls)


def test_new_proposal_rejected_before_peers_and_dice(monkeypatch):
    callbacks = ScriptedCallbacks(
        proposal=lambda *args: {
            "world_change_statement": ' "Fact 1." ',
            "supporting_pros": [
                {"source_type": "canon_fact", "source_ref": "Fact 1.", "argument": ""}
            ],
        }
    )
    dice_calls = []
    monkeypatch.setattr(runner, "roll_resolution", lambda rng: dice_calls.append(rng))
    request = make_request(seed=20)
    before = deepcopy(request)
    with pytest.raises(errors.InvalidProposalError):
        runner.run(
            request,
            callbacks.proposal_generator,
            callbacks.peer_reviewer,
            callbacks.failure_resolver,
        )
    assert len(callbacks.proposal_calls) == 1
    assert not callbacks.peer_calls and not callbacks.failure_calls and not dice_calls
    assert request == before


@pytest.mark.parametrize("mode", ["absent", "no-shift", "invalid-shift", "empty", "reject"])
def test_umpire_review_invocation_rules(mode):
    def peer(actor, proposal, state):
        return {
            "voter_actor_id": actor.id,
            "baseline_plausibility": 0,
            "final_vote": 0 if mode == "no-shift" else 1,
            "biased_shift_applied": False,
            "cited_anchor": None if mode == "invalid-shift" else "Fact 1.",
            "public_argument": "",
        }

    def umpire(turn, proposal, evaluations, state):
        return (
            [{"voter_actor_id": evaluations[0].voter_actor_id, "reason": "Illogical."}]
            if mode == "reject"
            else []
        )

    callbacks = ScriptedCallbacks(peer=peer, umpire=umpire)
    result = runner.run(
        make_request(world=make_world(("actor_a", "actor_b", "actor_c")), turn_count=3, seed=20),
        callbacks.proposal_generator,
        callbacks.peer_reviewer,
        callbacks.failure_resolver,
        None if mode == "absent" else callbacks.umpire_review,
    )
    eligible = mode in {"empty", "reject"}
    assert len(callbacks.umpire_calls) == (3 if eligible else 0)
    if eligible:
        assert [call[0] for call in callbacks.umpire_calls] == [1, 2, 3]
        assert all(len(call[2]) == 2 for call in callbacks.umpire_calls)
        assert all(all(e.biased_shift_applied for e in call[2]) for call in callbacks.umpire_calls)
    expected_modifier = 0 if mode in {"no-shift", "invalid-shift"} else 1 if mode == "reject" else 2
    assert all(record.net_vote_modifier == expected_modifier for record in result.turn_records)
    assert all(
        len(record.umpire_rejections) == (1 if mode == "reject" else 0)
        for record in result.turn_records
    )


def test_umpire_error_aborts_without_result():
    callbacks = ScriptedCallbacks(
        peer=lambda actor, proposal, state: {
            "voter_actor_id": actor.id,
            "baseline_plausibility": 0,
            "final_vote": 1,
            "biased_shift_applied": True,
            "cited_anchor": "Fact 1.",
            "public_argument": "",
        },
        umpire=lambda *args: None,
    )
    request = make_request(seed=20)
    before = deepcopy(request)
    with pytest.raises(errors.UmpireReviewError) as caught:
        runner.run(
            request,
            callbacks.proposal_generator,
            callbacks.peer_reviewer,
            callbacks.failure_resolver,
            callbacks.umpire_review,
        )
    assert request == before
    assert not callbacks.failure_calls and not hasattr(caught.value, "partial_result")


def test_umpire_review_receives_validated_evaluation():
    callbacks = ScriptedCallbacks(
        peer=lambda actor, proposal, state: {
            "voter_actor_id": actor.id,
            "baseline_plausibility": 1,
            "final_vote": 0,
            "biased_shift_applied": False,
            "cited_anchor": '  "Fact 1."  ',
            "public_argument": "Original.",
        },
        umpire=lambda *args: [{"voter_actor_id": "actor_b", "reason": "Illogical."}],
    )
    result = runner.run(
        make_request(seed=20, first_round_order=["actor_a", "actor_b"]),
        callbacks.proposal_generator,
        callbacks.peer_reviewer,
        callbacks.failure_resolver,
        callbacks.umpire_review,
    )
    before = callbacks.umpire_calls[0][2][0]
    assert before.biased_shift_applied is True and before.cited_anchor == "Fact 1."
    assert before == result.turn_records[0].umpire_rejections[0].evaluation_before_reversion
    assert result.turn_records[0].peer_evaluations[0].final_vote == 1


def test_success_appends_proposal():
    callbacks = ScriptedCallbacks()
    result = runner.run(
        make_request(seed=seed_for_base_roll(7), first_round_order=["actor_a", "actor_b"]),
        callbacks.proposal_generator,
        callbacks.peer_reviewer,
        callbacks.failure_resolver,
    )
    record = result.turn_records[0]
    assert (record.resolution_roll, record.adjusted_total, record.outcome) == (7, 7, "Success")
    assert result.final_world_state.canon_facts == [
        "Fact 1.",
        record.proposal.world_change_statement,
    ]
    assert record.failure_resolution is None and not callbacks.failure_calls


def test_failure_appends_consequence():
    callbacks = ScriptedCallbacks()
    result = runner.run(
        make_request(seed=seed_for_base_roll(6), first_round_order=["actor_a", "actor_b"]),
        callbacks.proposal_generator,
        callbacks.peer_reviewer,
        callbacks.failure_resolver,
    )
    record = result.turn_records[0]
    assert (record.resolution_roll, record.adjusted_total, record.outcome) == (6, 6, "Failure")
    assert result.final_world_state.canon_facts == ["Fact 1.", "Consequence 1."]
    assert record.proposal.world_change_statement not in result.final_world_state.canon_facts
    assert record.failure_resolution.world_change_statement == "Consequence 1."
    assert record.turn_index == 1 and len(callbacks.failure_calls) == 1


def test_every_turn_adds_exactly_one_fact(monkeypatch):
    dice = iter([(4, 4), (1, 1)] * 5)
    monkeypatch.setattr(runner, "roll_resolution", lambda rng: next(dice))
    callbacks = ScriptedCallbacks()
    result = runner.run(
        make_request(turn_count=10, seed=20),
        callbacks.proposal_generator,
        callbacks.peer_reviewer,
        callbacks.failure_resolver,
    )
    assert {record.outcome for record in result.turn_records} == {"Success", "Failure"}
    for i, record in enumerate(result.turn_records):
        change = record.state_changes[0]
        assert len(change.before) == i + 1 and len(change.after) == i + 2
        assert change.after[:-1] == change.before
    assert len(result.final_world_state.canon_facts) == 11


@pytest.mark.parametrize("case", ["unique", "tied", "rejection"])
def test_failure_resolver_called_on_every_failure(case):
    def peer(actor, proposal, state):
        baseline = (
            -1
            if case == "unique" and actor.id == "actor_b"
            else 1
            if case == "rejection" and actor.id == "actor_b"
            else 0
        )
        return {
            "voter_actor_id": actor.id,
            "baseline_plausibility": baseline,
            "final_vote": 0 if case == "rejection" else baseline,
            "biased_shift_applied": False,
            "cited_anchor": "Fact 1.",
            "public_argument": f"Original argument from {actor.id}.",
        }

    callbacks = ScriptedCallbacks(
        peer=peer,
        umpire=lambda *args: [{"voter_actor_id": "actor_b", "reason": "Illogical."}],
        failure=lambda turn, proposal, evaluations, candidates, total, state: {
            "source_voter_actor_id": candidates[-1],
            "world_change_statement": "Restated consequence.",
            "rationale": "Umpire choice.",
        },
    )
    result = runner.run(
        make_request(
            world=make_world(("actor_a", "actor_b", "actor_c")),
            seed=seed_for_base_roll(2),
            first_round_order=["actor_a", "actor_b", "actor_c"],
        ),
        callbacks.proposal_generator,
        callbacks.peer_reviewer,
        callbacks.failure_resolver,
        callbacks.umpire_review if case == "rejection" else None,
    )
    expected = (
        ["actor_b"]
        if case == "unique"
        else ["actor_b", "actor_c"]
        if case == "tied"
        else ["actor_c"]
    )
    assert len(callbacks.failure_calls) == 1
    turn, proposal, evaluations, candidates, total, state = callbacks.failure_calls[0]
    record = result.turn_records[0]
    assert proposal == record.proposal
    assert turn == 1 and candidates == expected
    assert total == record.adjusted_total == 2 + sum(e.final_vote for e in evaluations)
    assert state.turn_index == 0 and state.canon_facts == ["Fact 1."]
    assert record.failure_resolution.source_voter_actor_id == expected[-1]
    assert all(
        e.public_argument == f"Original argument from {e.voter_actor_id}."
        for e in record.peer_evaluations
    )
    assert result.final_world_state.canon_facts == ["Fact 1.", "Restated consequence."]


@pytest.mark.parametrize("source", [None, "actor_a"])
def test_one_actor_failure_requires_null_source(source):
    callbacks = ScriptedCallbacks(
        failure=lambda *args: {
            "source_voter_actor_id": source,
            "world_change_statement": "Consequence.",
            "rationale": "No peers.",
        }
    )
    request = make_request(
        world=make_world(("actor_a",)), seed=seed_for_base_roll(2), first_round_order=["actor_a"]
    )
    before = deepcopy(request)
    if source is not None:
        with pytest.raises(errors.UmpireResolutionError):
            runner.run(
                request,
                callbacks.proposal_generator,
                callbacks.peer_reviewer,
                callbacks.failure_resolver,
            )
    else:
        result = runner.run(
            request,
            callbacks.proposal_generator,
            callbacks.peer_reviewer,
            callbacks.failure_resolver,
        )
        assert result.turn_records[0].net_vote_modifier == 0
        assert result.turn_records[0].peer_evaluations == []
        assert result.final_world_state.session_index == 1
        assert callbacks.failure_calls[0][3] == []
    assert not callbacks.peer_calls and request == before


def test_invalid_failure_decision_aborts():
    callbacks = ScriptedCallbacks(failure=lambda *args: None)
    request = make_request(seed=seed_for_base_roll(2), first_round_order=["actor_a", "actor_b"])
    before = deepcopy(request)
    with pytest.raises(errors.UmpireResolutionError) as caught:
        runner.run(
            request,
            callbacks.proposal_generator,
            callbacks.peer_reviewer,
            callbacks.failure_resolver,
        )
    assert request == before
    assert not hasattr(caught.value, "partial_result")


def test_state_change_records(monkeypatch):
    monkeypatch.setattr(runner, "roll_resolution", lambda rng: (4, 4))
    callbacks = ScriptedCallbacks()
    result = runner.run(
        make_request(
            world=make_world(("actor_a", "actor_b", "actor_c"), session_index=3, turn_index=7),
            turn_count=4,
            seed=20,
        ),
        callbacks.proposal_generator,
        callbacks.peer_reviewer,
        callbacks.failure_resolver,
    )
    canon = ["Fact 1."]
    for i, record in enumerate(result.turn_records):
        after = [*canon, record.proposal.world_change_statement]
        expected = [
            {
                "path": "/canon_facts",
                "before": canon,
                "after": after,
                "reason": "proposal-succeeded",
            }
        ]
        if i == 2:
            expected.append(
                {"path": "/session_index", "before": 3, "after": 4, "reason": "round-complete"}
            )
        expected.append(
            {"path": "/turn_index", "before": 7 + i, "after": 8 + i, "reason": "turn-tick"}
        )
        assert [change.model_dump() for change in record.state_changes] == expected
        assert [change.path for change in record.state_changes] == sorted(
            {change.path for change in record.state_changes}
        )
        canon = after
    result.final_world_state.canon_facts.append("Later caller change.")
    assert "Later caller change." not in result.turn_records[-1].state_changes[0].after


def test_actors_unchanged_and_only_consequence_enters_canon():
    request = make_request(
        world=make_world(("actor_a", "actor_b", "actor_c")),
        seed=seed_for_base_roll(2),
        first_round_order=["actor_a", "actor_b", "actor_c"],
    )
    callbacks = ScriptedCallbacks()
    result = runner.run(
        request, callbacks.proposal_generator, callbacks.peer_reviewer, callbacks.failure_resolver
    )
    assert (
        result.final_world_state.actors
        == models.WorldState.model_validate(request["world_state"]).actors
    )
    assert result.final_world_state.canon_facts == ["Fact 1.", "Consequence 1."]
    assert result.final_world_state.model_dump().keys() == {
        "actors",
        "canon_facts",
        "session_index",
        "turn_index",
    }


@pytest.mark.parametrize(
    "kind,error_cls",
    [
        ("proposal", errors.ProposalGenerationError),
        ("peer", errors.PeerReviewError),
        ("umpire", errors.UmpireReviewError),
        ("failure", errors.UmpireResolutionError),
    ],
)
@pytest.mark.parametrize(
    "exception",
    [
        ValueError,
        RecursionError,
        SystemError,
        MemoryError,
        KeyboardInterrupt,
        errors.InvalidProposalError,
    ],
)
def test_callback_exceptions_wrapped(kind, error_cls, exception):
    original = exception("Callback failed.")

    def fail(*args):
        raise original

    def peer(actor, proposal, state):
        return {
            "voter_actor_id": actor.id,
            "baseline_plausibility": 0,
            "final_vote": 1,
            "biased_shift_applied": False,
            "cited_anchor": "Fact 1.",
            "public_argument": "",
        }

    callbacks = ScriptedCallbacks(**{"peer": peer, kind: fail})
    request = make_request(seed=seed_for_base_roll(2), first_round_order=["actor_a", "actor_b"])
    before = deepcopy(request)
    expected = exception if exception in (MemoryError, KeyboardInterrupt) else error_cls
    with pytest.raises(expected) as caught:
        runner.run(
            request,
            callbacks.proposal_generator,
            callbacks.peer_reviewer,
            callbacks.failure_resolver,
            callbacks.umpire_review,
        )
    assert request == before
    if expected is error_cls:
        assert caught.value.__cause__ is original
    else:
        assert caught.value is original


@pytest.mark.parametrize(
    "kind,error_cls",
    [("umpire", errors.UmpireReviewError), ("failure", errors.UmpireResolutionError)],
)
@pytest.mark.parametrize("exception", [concurrent.futures.CancelledError, asyncio.CancelledError])
def test_callback_cancellation(kind, error_cls, exception):
    original = exception("Cancelled.")

    def cancel(*args):
        raise original

    callbacks = ScriptedCallbacks(
        **{
            "peer": lambda actor, proposal, state: {
                "voter_actor_id": actor.id,
                "baseline_plausibility": 0,
                "final_vote": 1,
                "biased_shift_applied": True,
                "cited_anchor": "Fact 1.",
                "public_argument": "",
            },
            kind: cancel,
        }
    )
    request = make_request(seed=seed_for_base_roll(2), first_round_order=["actor_a", "actor_b"])
    before = deepcopy(request)
    expected = exception if exception is asyncio.CancelledError else error_cls
    with pytest.raises(expected) as caught:
        runner.run(
            request,
            callbacks.proposal_generator,
            callbacks.peer_reviewer,
            callbacks.failure_resolver,
            callbacks.umpire_review,
        )
    assert request == before
    if expected is error_cls:
        assert caught.value.__cause__ is original
    else:
        assert caught.value is original


def test_callbacks_receive_isolated_snapshots():
    defaults = ScriptedCallbacks(
        peer=lambda actor, proposal, state: {
            "voter_actor_id": actor.id,
            "baseline_plausibility": 0,
            "final_vote": 1,
            "biased_shift_applied": True,
            "cited_anchor": "Fact 1.",
            "public_argument": "Reason.",
        }
    )
    request = make_request(seed=seed_for_base_roll(2), first_round_order=["actor_a", "actor_b"])
    before = deepcopy(request)
    expected = runner.run(
        request,
        defaults.proposal_generator,
        defaults.peer_reviewer,
        defaults.failure_resolver,
        defaults.umpire_review,
    )

    def proposal(actor, tier, tags, state):
        raw = defaults.proposal_generator(actor, tier, tags, state)
        assert actor is not state.actors[0]
        actor.name = "Renamed."
        state.actors[0].agenda = "Changed."
        state.canon_facts.append("Injected by generator.")
        tags.append("Extra tag.")
        return raw

    def peer(actor, proposal, state):
        raw = defaults.peer_reviewer(actor, proposal, state)
        actor.name = "Renamed peer."
        proposal.supporting_pros.append(proposal.supporting_pros[0].model_copy(deep=True))
        proposal.world_change_statement = "Injected proposal."
        state.canon_facts.append("Injected by peer.")
        return raw

    def umpire(turn, proposal, evaluations, state):
        proposal.supporting_pros.clear()
        evaluations[0].final_vote = -1
        state.canon_facts.append("Injected by umpire.")
        return []

    def failure(turn, proposal, evaluations, candidates, total, state):
        raw = defaults.failure_resolver(turn, proposal, evaluations, candidates, total, state)
        proposal.supporting_pros.clear()
        evaluations[0].final_vote = -1
        candidates.append("unknown")
        state.actors[0].name = "Changed again."
        state.canon_facts.append("Injected by resolver.")
        return raw

    callbacks = ScriptedCallbacks(proposal=proposal, peer=peer, umpire=umpire, failure=failure)
    actual = runner.run(
        request,
        callbacks.proposal_generator,
        callbacks.peer_reviewer,
        callbacks.failure_resolver,
        callbacks.umpire_review,
    )
    assert actual == expected and request == before
    assert (
        len(callbacks.proposal_calls)
        == len(callbacks.peer_calls)
        == len(callbacks.umpire_calls)
        == len(callbacks.failure_calls)
        == 1
    )
    states = [
        callbacks.proposal_calls[0][3],
        callbacks.peer_calls[0][2],
        callbacks.umpire_calls[0][3],
        callbacks.failure_calls[0][5],
    ]
    assert len({id(state) for state in states}) == 4
    assert len({id(state.canon_facts) for state in states}) == 4
    assert callbacks.umpire_calls[0][2][0] is not callbacks.failure_calls[0][2][0]
    assert callbacks.peer_calls[0][1] is not callbacks.umpire_calls[0][1]


def test_model_instance_returns_accepted():
    class Draft(models.ProposalDraft):
        pass

    callbacks = ScriptedCallbacks(
        proposal=lambda *args: Draft(
            world_change_statement="New event.",
            supporting_pros=[
                models.SupportingPro(
                    source_type="canon_fact", source_ref="Fact 1.", argument="Reason."
                )
            ],
        ),
        peer=lambda actor, proposal, state: models.PeerEvaluation(
            voter_actor_id=actor.id,
            baseline_plausibility=1,
            final_vote=0,
            biased_shift_applied=False,
            cited_anchor=' "Fact 1." ',
            public_argument="Original.",
        ),
        umpire=lambda *args: [
            models.UmpireRejection(voter_actor_id="actor_b", reason="Illogical.")
        ],
        failure=lambda *args: models.FailureResolution(
            source_voter_actor_id="actor_b",
            world_change_statement="Consequence.",
            rationale="Reason.",
        ),
    )
    result = runner.run(
        make_request(seed=seed_for_base_roll(2), first_round_order=["actor_a", "actor_b"]),
        callbacks.proposal_generator,
        callbacks.peer_reviewer,
        callbacks.failure_resolver,
        callbacks.umpire_review,
    )
    assert result.final_world_state.canon_facts == ["Fact 1.", "Consequence."]
    record = result.turn_records[0]
    assert record.proposal.world_change_statement == "New event."
    assert record.peer_evaluations[0].final_vote == 1
    assert record.umpire_rejections[0].evaluation_before_reversion.cited_anchor == "Fact 1."


def test_callback_model_shapes_revalidated():
    for raw in [
        models.Actor(id="actor_a", name="Actor A", agenda="Agenda A"),
        models.ProposalDraft.model_construct(world_change_statement=" ", supporting_pros=[]),
        models.ProposalDraft.model_construct(
            world_change_statement="New event.",
            supporting_pros=[
                models.SupportingPro.model_construct(
                    source_type="canon_fact", source_ref=None, argument=""
                ),
            ],
        ),
    ]:
        callbacks = ScriptedCallbacks(proposal=lambda *args, raw=raw: raw)
        with pytest.raises(errors.ProposalGenerationError):
            runner.run(
                make_request(seed=20),
                callbacks.proposal_generator,
                callbacks.peer_reviewer,
                callbacks.failure_resolver,
            )


@pytest.mark.parametrize(
    "exception", [ValueError, RecursionError, SystemError, MemoryError, KeyboardInterrupt]
)
@pytest.mark.parametrize("kind", ["mapping", "model"])
def test_request_conversion_exception_boundaries(exception, kind, monkeypatch):
    original = exception("Request conversion failed.")

    class BrokenMapping(Mapping):
        def __iter__(self):
            raise original

        def __len__(self):
            return 1

        def __getitem__(self, key):
            raise original

    class BrokenRequest(models.RunRequest):
        def model_dump(self, **kwargs):
            raise original

    request = BrokenMapping() if kind == "mapping" else BrokenRequest.model_construct()
    callbacks = ScriptedCallbacks()
    draws = []
    monkeypatch.setattr(runner.random, "Random", lambda *args: draws.append(args))
    expected = (
        exception
        if exception in (MemoryError, KeyboardInterrupt)
        else errors.InvalidRunRequestError
    )
    with pytest.raises(expected) as caught:
        runner.run(
            request,
            callbacks.proposal_generator,
            callbacks.peer_reviewer,
            callbacks.failure_resolver,
        )
    assert not draws and not callbacks.proposal_calls
    if expected is errors.InvalidRunRequestError:
        assert caught.value.__cause__ is original
    else:
        assert caught.value is original


@pytest.mark.parametrize(
    "target",
    [
        "snapshot",
        "build_proposal",
        "validate_peer_evaluation",
        "apply_umpire_rejections",
        "validate_failure_resolution",
    ],
)
def test_callback_wrapping_excludes_snapshot_preparation_and_gates(target, monkeypatch):
    original = ValueError("Internal preparation or gate failed.")

    def fail(*args, **kwargs):
        raise original

    callbacks = ScriptedCallbacks(
        peer=lambda actor, proposal, state: {
            "voter_actor_id": actor.id,
            "baseline_plausibility": 0,
            "final_vote": 1,
            "biased_shift_applied": True,
            "cited_anchor": "Fact 1.",
            "public_argument": "",
        }
    )
    if target == "snapshot":
        monkeypatch.setattr(models.Actor, "model_copy", fail)
    else:
        monkeypatch.setattr(runner, target, fail)
    with pytest.raises(errors.MechanicsError) as caught:
        runner.run(
            make_request(seed=seed_for_base_roll(2), first_round_order=["actor_a", "actor_b"]),
            callbacks.proposal_generator,
            callbacks.peer_reviewer,
            callbacks.failure_resolver,
            callbacks.umpire_review,
        )
    assert caught.value.__cause__ is original


@pytest.mark.parametrize(
    "exception",
    [
        ValueError,
        RecursionError,
        SystemError,
        MemoryError,
        KeyboardInterrupt,
        errors.InvalidProposalError,
    ],
)
def test_engine_internal_exceptions(exception, monkeypatch):
    original = exception("Internal failure.")

    def fail(*args):
        raise original

    monkeypatch.setattr(runner, "draw_turn_cues", fail)
    callbacks = ScriptedCallbacks()
    expected = errors.MechanicsError if exception is ValueError else exception
    with pytest.raises(expected) as caught:
        runner.run(
            make_request(seed=20),
            callbacks.proposal_generator,
            callbacks.peer_reviewer,
            callbacks.failure_resolver,
        )
    if exception is ValueError:
        assert caught.value.__cause__ is original
    else:
        assert caught.value is original


def test_public_api_exports():
    expected = {
        "run",
        "CONTRACT_VERSION",
        "DEFAULT_TABLE_SET_ID",
        "Actor",
        "WorldState",
        "SupportingPro",
        "ProposalDraft",
        "Proposal",
        "PeerEvaluation",
        "UmpireRejection",
        "UmpireRejectionRecord",
        "FailureResolution",
        "StateChange",
        "TurnRecord",
        "SparkTables",
        "RunRequest",
        "RunResult",
        "RunFailure",
        "RunError",
        "InvalidRunRequestError",
        "ProposalGenerationError",
        "InvalidProposalError",
        "PeerReviewError",
        "UmpireReviewError",
        "UmpireResolutionError",
        "MechanicsError",
        "ProposalGenerator",
        "PeerReviewer",
        "UmpireReview",
        "FailureResolver",
    }
    assert set(tome.engine.__all__) == expected
    assert len(tome.engine.__all__) == len(expected)
    assert set(tome.__all__) == expected | {"__version__"}
    assert tome.run is runner.run is tome.engine.run
    assert tome.CONTRACT_VERSION == "1.1.0" and tome.__version__ == "0.1.0"
    assert all(getattr(tome, name) is getattr(tome.engine, name) for name in expected)
    for protocol in [
        protocols.ProposalGenerator,
        protocols.PeerReviewer,
        protocols.UmpireReview,
        protocols.FailureResolver,
    ]:
        parameters = list(inspect.signature(protocol.__call__).parameters.values())[1:]
        assert all(parameter.kind is inspect.Parameter.POSITIONAL_ONLY for parameter in parameters)


def test_run_error_exposes_failure_code():
    callbacks = ScriptedCallbacks(
        proposal=lambda *args: {
            "world_change_statement": "Fact 1.",
            "supporting_pros": [
                {"source_type": "canon_fact", "source_ref": "Fact 1.", "argument": ""},
            ],
        }
    )
    with pytest.raises(errors.InvalidProposalError) as caught:
        runner.run(
            make_request(seed=20),
            callbacks.proposal_generator,
            callbacks.peer_reviewer,
            callbacks.failure_resolver,
        )
    failure = caught.value.to_failure()
    assert failure.code == "INVALID_PROPOSAL"
    assert failure.contract_version == "1.1.0" and failure.message == caught.value.message
