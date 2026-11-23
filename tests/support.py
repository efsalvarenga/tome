import random


def make_world(actor_ids=("actor_a", "actor_b"), canon=("Fact 1.",), session_index=0, turn_index=0):
    return {
        "session_index": session_index,
        "turn_index": turn_index,
        "canon_facts": list(canon),
        "actors": [
            {"id": actor_id, "name": f"Actor {chr(65 + i)}", "agenda": f"Agenda {chr(65 + i)}"}
            for i, actor_id in enumerate(actor_ids)
        ],
    }


def make_request(world=None, turn_count=1, **optional):
    return {
        "contract_version": "1.1.0",
        "world_state": make_world() if world is None else world,
        "turn_count": turn_count,
        **optional,
    }


def override_tables(overrides: dict[tuple[str, int], str] | None = None) -> dict:
    overrides = {} if overrides is None else overrides
    return {
        name: {
            str(key): overrides.get((name, key), f"{name} {key}")
            for tens in range(1, 7)
            for units in range(1, 7)
            for key in [10 * tens + units]
        }
        for name in ("Action", "Focus", "Method", "Disposition", "Motivation")
    }


INVALID_REQUEST_CASES = [
    ("zero-turns", lambda r: r.update(turn_count=0)),
    ("negative-turns", lambda r: r.update(turn_count=-1)),
    ("bool-turns", lambda r: r.update(turn_count=True)),
    ("negative-seed", lambda r: r.update(seed=-1)),
    ("bool-seed", lambda r: r.update(seed=True)),
    ("null-seed", lambda r: r.update(seed=None)),
    ("null-tables", lambda r: r.update(spark_tables=None)),
    ("null-order", lambda r: r.update(first_round_order=None)),
    ("empty-actors", lambda r: r["world_state"].update(actors=[])),
    ("blank-id", lambda r: r["world_state"]["actors"][0].update(id="  ")),
    ("quoted-empty-id", lambda r: r["world_state"]["actors"][0].update(id='""')),
    (
        "matching-ids",
        lambda r: r["world_state"].update(actors=make_world(("a", " a "))["actors"]),
    ),
    ("blank-fact", lambda r: r["world_state"].update(canon_facts=["  "])),
    ("matching-facts", lambda r: r["world_state"].update(canon_facts=["Fact", '"Fact"'])),
    ("old-contract", lambda r: r.update(contract_version="1.0.0")),
    ("extra-request-field", lambda r: r.update(transport="x")),
    ("active-rumours", lambda r: r["world_state"].update(active_rumors=[])),
    ("traits", lambda r: r["world_state"]["actors"][0].update(traits=[])),
    ("missing-order-actor", lambda r: r.update(first_round_order=["actor_a"])),
    ("repeated-order-actor", lambda r: r.update(first_round_order=["actor_a", "actor_a"])),
    ("unknown-order-actor", lambda r: r.update(first_round_order=["actor_a", "unknown"])),
    ("inexact-order-actor", lambda r: r.update(first_round_order=["actor_a ", "actor_b"])),
    ("tuple-order", lambda r: r.update(first_round_order=("actor_a", "actor_b"))),
]


class ScriptedCallbacks:
    def __init__(self, proposal=None, peer=None, umpire=None, failure=None):
        self.proposal = proposal
        self.peer = peer
        self.umpire = umpire
        self.failure = failure
        self.proposal_calls = []
        self.peer_calls = []
        self.umpire_calls = []
        self.failure_calls = []

    def proposal_generator(self, active_actor, trio_tier, spark_tags, world_state, /):
        args = (active_actor, trio_tier, spark_tags, world_state)
        self.proposal_calls.append(args)
        if self.proposal is not None:
            return self.proposal(*args)
        return {
            "world_change_statement": f"{active_actor.name} achieves outcome {world_state.turn_index + 1}.",
            "supporting_pros": [
                {
                    "source_type": "canon_fact",
                    "source_ref": world_state.canon_facts[0],
                    "argument": "Scripted supporting argument.",
                }
            ],
        }

    def peer_reviewer(self, voter_actor, proposal, world_state, /):
        args = (voter_actor, proposal, world_state)
        self.peer_calls.append(args)
        if self.peer is not None:
            return self.peer(*args)
        return {
            "voter_actor_id": voter_actor.id,
            "baseline_plausibility": 0,
            "final_vote": 0,
            "biased_shift_applied": False,
            "cited_anchor": None,
            "public_argument": f"{voter_actor.name} is uncertain.",
        }

    def umpire_review(self, turn_index, proposal, peer_evaluations, world_state, /):
        args = (turn_index, proposal, peer_evaluations, world_state)
        self.umpire_calls.append(args)
        return [] if self.umpire is None else self.umpire(*args)

    def failure_resolver(
        self,
        turn_index,
        proposal,
        peer_evaluations,
        candidate_voter_ids,
        adjusted_total,
        world_state,
        /,
    ):
        args = (
            turn_index,
            proposal,
            peer_evaluations,
            candidate_voter_ids,
            adjusted_total,
            world_state,
        )
        self.failure_calls.append(args)
        if self.failure is not None:
            return self.failure(*args)
        return {
            "source_voter_actor_id": candidate_voter_ids[0] if candidate_voter_ids else None,
            "world_change_statement": f"Consequence {turn_index}.",
            "rationale": "Scripted test decision.",
        }


def seed_for_base_roll(target: int) -> int:
    for seed in range(10_000):
        rng = random.Random(seed)
        rng.randint(1, 6)
        rng.sample(["Action", "Focus", "Method", "Disposition", "Motivation"], 2)
        for _ in range(4):
            rng.randint(1, 6)
        if rng.randint(1, 6) + rng.randint(1, 6) == target:
            return seed
    raise AssertionError(f"No seed produces base roll {target}.")
