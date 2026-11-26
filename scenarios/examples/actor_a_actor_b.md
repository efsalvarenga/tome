# Scenario Playtest: Standing Supply Offer Between Actor A and Actor B

This Markdown file is a neutral public example following [`scenario_template.md`](../scenario_template.md).
It is an authoring aid for a human or assisted playtest and is not loaded natively by `tome`.
A caller translates its sections into a `WorldState`, a `RunRequest`, and callback inputs as defined in the [core architecture specification](../../docs/designs/001_tome_core_architecture.md).
See [`scenarios/README.md`](../README.md) for workspace conventions and private playtest boundaries.

## Run Settings

| Setting | Value |
| :--- | :--- |
| Contract version | `1.1.0` |
| Number of turns | `4` |
| Random seed | `42` |
| Actor order | `["actor_a", "actor_b"]` |
| Starting session index | `0` |
| Starting turn index | `0` |
| Spark tables | Built-in defaults |

The actor order contains both actor IDs once and alternates across the four turns.
The random seed fixes engine-owned posture, spark-table, and resolution rolls while leaving narrative callbacks under caller control.

## Actors (Required)

Each actor has a unique identifier, a neutral display name, and an explicit agenda.
Agendas express preferences and aims rather than established capabilities or canon citations.

### Actor A

- ID: `actor_a`
- Name: Actor A
- Agenda: Wants to maintain continuity of supply while preserving cancellation flexibility.

### Actor B

- ID: `actor_b`
- Name: Actor B
- Agenda: Wants to secure a bounded supply agreement with a minimum purchase commitment and no early-cancellation right.

## Starting Canon Facts (Required)

Each bullet below is an established starting canon fact that supporting arguments and vote shifts may cite verbatim.

- Actor B has made a standing offer to Actor A for three months of supply, conditional on a minimum purchase commitment and with no early-cancellation right.
- Actor A can accept the standing offer without obtaining further approval from Actor B.
- Actor A needs continuity of supply but prefers cancellation flexibility.
- Actor A has not yet accepted a replacement supply agreement.

## Scenario Framing (Optional, Not Canon)

Two counterparties weigh short-term certainty of supply against contractual commitment over a bounded four-turn horizon.
Keep proposals and peer arguments concise, commercial, and grounded strictly in the canon facts above rather than inventing external counterparties or unstated remedies.

## Questions to Explore (Optional)

These questions guide inspection of the resulting trajectory rather than prescribing an outcome.

- Does Actor A accept the standing offer as written, seek modified terms, or defer commitment?
- How do minimum purchase and cancellation constraints shape peer objections and failure consequences across four turns?

## Umpire Guidance (Optional)

- Pre-roll review of shifted votes: Disabled for this baseline four-turn example.
- Failure adjudication: On a failed roll, restate a suitable lowest-voted peer objection as a concrete commercial consequence (`source_voter_actor_id` set to that peer), or supply an independent commercial consequence (`source_voter_actor_id: null`) when the peer vote is `0` or `+1` yet the roll falls below `7` and the peer's argument offers no usable failure reason, ensuring the statement matches neither existing `canon_facts` nor the failed proposal's `world_change_statement`.
- Additional plausibility guidance: Treat any modification to the standing offer's commitment or cancellation terms as requiring Actor B's agreement rather than unilateral acceptance.

## Before the Playtest

- [x] Replace the title, actor names, agendas, and starting fact prompts.
- [x] Remove unused prompts or optional sections.
- [x] Check that every actor has a unique ID and appears exactly once in the actor order.
- [x] Check that facts provide the grounding needed for the actors to act.
- [x] Keep the turn count positive and the seed and starting indices non-negative integers.
- [x] Keep the first run short so its proposals, votes, consequences, and final canon are easy to inspect.
- [x] Adjust relative links for `scenarios/examples/` depth and confirm `## Licence & Attribution` matches this public example.

## Licence & Attribution

This public example scenario is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International Licence (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).
It accompanies game mechanics derived from [Triple-O](https://capacle.itch.io/triple-o) by Cezar Capacle (CC BY-SA 4.0) and Engle Matrix Games, invented by Chris Engle (CC BY-SA 4.0).
