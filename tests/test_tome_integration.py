from copy import deepcopy

import pytest
from support import ScriptedCallbacks, make_request, make_world, override_tables, seed_for_base_roll

from tome.engine import errors, runner


def test_worked_example_reproduces_spec_result():
    callbacks = ScriptedCallbacks(
        proposal=lambda *args: {
            "world_change_statement": "Actor A achieves outcome X.",
            "supporting_pros": [
                {
                    "source_type": "canon_fact",
                    "source_ref": "Fact 1.",
                    "argument": "Fact 1 makes outcome X possible for Actor A.",
                }
            ],
        },
        peer=lambda *args: {
            "voter_actor_id": "actor_b",
            "baseline_plausibility": -1,
            "biased_shift_applied": False,
            "cited_anchor": None,
            "final_vote": -1,
            "public_argument": "Actor B could prevent outcome X.",
        },
        failure=lambda *args: {
            "source_voter_actor_id": "actor_b",
            "world_change_statement": "Actor B prevents outcome X.",
            "rationale": "The only peer has the lowest final vote; the umpire restates its argument as a concrete event.",
        },
    )
    request = make_request(
        spark_tables=override_tables(
            {("Focus", 66): "Resource access", ("Method", 13): "Public declaration"}
        ),
        seed=20,
        first_round_order=["actor_a", "actor_b"],
    )
    result = runner.run(
        request, callbacks.proposal_generator, callbacks.peer_reviewer, callbacks.failure_resolver
    )
    assert result.model_dump(mode="json") == {
        "contract_version": "1.1.0",
        "spark_table_source": "request",
        "final_world_state": {
            "session_index": 0,
            "turn_index": 1,
            "canon_facts": ["Fact 1.", "Actor B prevents outcome X."],
            "actors": [
                {"id": "actor_a", "name": "Actor A", "agenda": "Agenda A"},
                {"id": "actor_b", "name": "Actor B", "agenda": "Agenda B"},
            ],
        },
        "turn_records": [
            {
                "turn_index": 1,
                "session_index": 0,
                "active_actor_id": "actor_a",
                "proposal": {
                    "active_actor_id": "actor_a",
                    "posture_roll": 6,
                    "trio_tier": "Odd",
                    "spark_tags": ["Focus:Resource access", "Method:Public declaration"],
                    "world_change_statement": "Actor A achieves outcome X.",
                    "supporting_pros": [
                        {
                            "source_type": "canon_fact",
                            "source_ref": "Fact 1.",
                            "argument": "Fact 1 makes outcome X possible for Actor A.",
                        }
                    ],
                },
                "peer_evaluations": [
                    {
                        "voter_actor_id": "actor_b",
                        "baseline_plausibility": -1,
                        "biased_shift_applied": False,
                        "cited_anchor": None,
                        "final_vote": -1,
                        "public_argument": "Actor B could prevent outcome X.",
                    }
                ],
                "umpire_rejections": [],
                "net_vote_modifier": -1,
                "resolution_roll": 7,
                "adjusted_total": 6,
                "outcome": "Failure",
                "failure_resolution": {
                    "source_voter_actor_id": "actor_b",
                    "world_change_statement": "Actor B prevents outcome X.",
                    "rationale": "The only peer has the lowest final vote; the umpire restates its argument as a concrete event.",
                },
                "state_changes": [
                    {
                        "path": "/canon_facts",
                        "before": ["Fact 1."],
                        "after": ["Fact 1.", "Actor B prevents outcome X."],
                        "reason": "failure-consequence",
                    },
                    {"path": "/turn_index", "before": 0, "after": 1, "reason": "turn-tick"},
                ],
            }
        ],
    }


def test_end_to_end_cycling_and_counters():
    callbacks = ScriptedCallbacks()
    request = make_request(
        world=make_world(("actor_a", "actor_b", "actor_c"), session_index=2, turn_index=10),
        turn_count=5,
        seed=20,
        first_round_order=["actor_c", "actor_a", "actor_b"],
    )
    result = runner.run(
        request, callbacks.proposal_generator, callbacks.peer_reviewer, callbacks.failure_resolver
    )
    records = result.turn_records
    assert len(records) == 5
    assert [record.active_actor_id for record in records] == [
        "actor_c",
        "actor_a",
        "actor_b",
        "actor_c",
        "actor_a",
    ]
    assert [record.turn_index for record in records] == [11, 12, 13, 14, 15]
    assert [record.session_index for record in records] == [2, 2, 3, 3, 3]
    assert result.final_world_state.turn_index == 15
    assert result.final_world_state.session_index == 3
    assert len(result.final_world_state.canon_facts) == 6
    assert len(callbacks.proposal_calls) == 5 and len(callbacks.peer_calls) == 10
    assert result.final_world_state.canon_facts == records[-1].state_changes[0].after
    for i, record in enumerate(records):
        state = callbacks.proposal_calls[i][3]
        assert state.turn_index == 10 + i and len(state.canon_facts) == 1 + i
        assert [peer.voter_actor_id for peer in record.peer_evaluations] == [
            actor["id"]
            for actor in request["world_state"]["actors"]
            if actor["id"] != record.active_actor_id
        ]


@pytest.mark.parametrize(
    "seed,actor_ids,order,names,keys,roll",
    [
        (42, ("actor_a", "actor_b"), ["actor_b", "actor_a"], ["Method", "Focus"], [22, 61], 12),
        (
            4,
            ("actor_c", "actor_a", "actor_b"),
            ["actor_b", "actor_a", "actor_c"],
            ["Disposition", "Motivation"],
            [21, 11],
            9,
        ),
    ],
)
def test_seeded_order_matches_golden_vector(seed, actor_ids, order, names, keys, roll):
    callbacks = ScriptedCallbacks()
    result = runner.run(
        make_request(
            world=make_world(actor_ids), turn_count=5, spark_tables=override_tables(), seed=seed
        ),
        callbacks.proposal_generator,
        callbacks.peer_reviewer,
        callbacks.failure_resolver,
    )
    assert [record.active_actor_id for record in result.turn_records] == [
        order[i % len(order)] for i in range(5)
    ]
    first = result.turn_records[0]
    assert first.proposal.posture_roll == 1 and first.proposal.trio_tier == "Obvious"
    assert first.proposal.spark_tags == [f"{name}:{name} {key}" for name, key in zip(names, keys)]
    assert first.resolution_roll == roll


def test_rejection_changes_outcome_not_dice():
    def peer(actor, proposal, state):
        return {
            "voter_actor_id": actor.id,
            "baseline_plausibility": 1,
            "final_vote": 0,
            "biased_shift_applied": False,
            "cited_anchor": ' "Fact 1." ',
            "public_argument": "Reason.",
        }

    results = []
    for review in [False, True]:
        callbacks = ScriptedCallbacks(
            peer=peer,
            umpire=lambda *args: [{"voter_actor_id": "actor_b", "reason": "Illogical."}],
        )
        results.append(
            runner.run(
                make_request(seed=seed_for_base_roll(6), first_round_order=["actor_a", "actor_b"]),
                callbacks.proposal_generator,
                callbacks.peer_reviewer,
                callbacks.failure_resolver,
                callbacks.umpire_review if review else None,
            )
        )
    a, b = [result.turn_records[0] for result in results]
    assert a.proposal == b.proposal and a.resolution_roll == b.resolution_roll == 6
    assert (a.net_vote_modifier, a.adjusted_total, a.outcome) == (0, 6, "Failure")
    assert (b.net_vote_modifier, b.adjusted_total, b.outcome) == (1, 7, "Success")
    assert results[0].final_world_state.canon_facts[-1] == "Consequence 1."
    assert results[1].final_world_state.canon_facts[-1] == b.proposal.world_change_statement


def test_next_actor_sees_failure_consequence(monkeypatch):
    monkeypatch.setattr(runner, "roll_resolution", lambda rng: (1, 1))
    callbacks = ScriptedCallbacks()
    result = runner.run(
        make_request(turn_count=2, seed=20, first_round_order=["actor_a", "actor_b"]),
        callbacks.proposal_generator,
        callbacks.peer_reviewer,
        callbacks.failure_resolver,
    )
    assert callbacks.proposal_calls[1][0].id == "actor_b"
    assert callbacks.proposal_calls[1][3].canon_facts == ["Fact 1.", "Consequence 1."]
    assert callbacks.peer_calls[1][2].canon_facts == ["Fact 1.", "Consequence 1."]
    assert result.final_world_state.canon_facts == ["Fact 1.", "Consequence 1.", "Consequence 2."]
    assert callbacks.proposal_calls[0][3].canon_facts == ["Fact 1."]


def test_partial_round_exports_last_consequence(monkeypatch):
    monkeypatch.setattr(runner, "roll_resolution", lambda rng: (1, 1))
    callbacks = ScriptedCallbacks()
    result = runner.run(
        make_request(world=make_world(("actor_a", "actor_b", "actor_c")), turn_count=2, seed=20),
        callbacks.proposal_generator,
        callbacks.peer_reviewer,
        callbacks.failure_resolver,
    )
    assert result.final_world_state.session_index == 0 and result.final_world_state.turn_index == 2
    assert result.final_world_state.canon_facts[-1] == "Consequence 2."
    assert result.turn_records[-1].state_changes[0].after == result.final_world_state.canon_facts


def test_invalid_decision_after_resolved_turn_is_atomic(monkeypatch):
    dice = iter([(4, 4), (1, 1)])
    monkeypatch.setattr(runner, "roll_resolution", lambda rng: next(dice))
    callbacks = ScriptedCallbacks(
        failure=lambda *args: {
            "source_voter_actor_id": "unknown",
            "world_change_statement": "Invalid consequence.",
            "rationale": "Reason.",
        }
    )
    request = make_request(turn_count=2, seed=20, first_round_order=["actor_a", "actor_b"])
    before = deepcopy(request)
    result = None
    with pytest.raises(errors.UmpireResolutionError) as caught:
        result = runner.run(
            request,
            callbacks.proposal_generator,
            callbacks.peer_reviewer,
            callbacks.failure_resolver,
        )
    assert result is None and request == before
    assert len(callbacks.proposal_calls) == 2 and len(callbacks.failure_calls) == 1
    assert callbacks.proposal_calls[1][3].canon_facts == ["Fact 1.", "Actor A achieves outcome 1."]
    assert callbacks.failure_calls[0][0] == 2
    assert not hasattr(caught.value, "partial_result") and not hasattr(caught.value, "turn_records")


@pytest.mark.parametrize("base_roll", [2, 8])
def test_input_unchanged_on_success_and_failure(base_roll):
    callbacks = ScriptedCallbacks()
    request = make_request(
        seed=seed_for_base_roll(base_roll), first_round_order=["actor_a", "actor_b"]
    )
    before = deepcopy(request)
    result = runner.run(
        request, callbacks.proposal_generator, callbacks.peer_reviewer, callbacks.failure_resolver
    )
    assert request == before
    assert result.turn_records[0].outcome == ("Success" if base_roll >= 7 else "Failure")
    result.final_world_state.actors[0].name = "Caller edit."
    result.final_world_state.canon_facts.append("Caller fact.")
    assert request == before


def test_seeded_runs_are_reproducible():
    request = make_request(
        world=make_world(("actor_c", "actor_a", "actor_b")), turn_count=10, seed=42
    )
    results = []
    for _ in range(3):
        callbacks = ScriptedCallbacks()
        results.append(
            runner.run(
                request,
                callbacks.proposal_generator,
                callbacks.peer_reviewer,
                callbacks.failure_resolver,
            ).model_dump(mode="json")
        )
    assert results[0] == results[1] == results[2]
