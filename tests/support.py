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
