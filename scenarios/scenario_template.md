# Scenario Playtest: [Scenario title]

Replace the bracketed prompts with your scenario.
Keep the run defaults for a first test, and add or remove actor sections and fact bullets as needed.
You do not need to prepare proposals, votes, dice rolls, or failure outcomes in advance.

This Markdown file is an authoring aid for an assisted playtest, not a file the engine loads directly.
During the playtest, a caller translates its contents into a `WorldState`, a `RunRequest`, and caller-supplied callback inputs as defined in the [core architecture specification](../docs/designs/001_tome_core_architecture.md).
See [`scenarios/README.md`](README.md) for the `scenarios/` workspace layout, public examples, and `scenarios/private/` handling rules.

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

These rows map to `WorldState` (`session_index`, `turn_index`) and `RunRequest` (`contract_version`, `turn_count`, `seed`, `first_round_order`, and omitting `spark_tables` for built-in defaults; omit `seed` or `first_round_order` rather than passing `null` when unseeded or engine-shuffled).
The actor order must contain every actor ID exactly once and repeats throughout this run.
With the two actors below, four turns gives each actor two turns.
The seed controls engine-owned random draws, not narrative generation.
Reproducing a complete outcome also requires the same callback outputs, umpire decisions, and engine/runtime versions.

## Actors (Required)

Use at least one actor, with a unique, non-blank ID for each.
An agenda describes what the actor wants; it does not establish a capability or count as a canon citation.

### Actor A

- ID: `actor_a`
- Name: [Display name for Actor A.]
- Agenda: [What Actor A wants to achieve or prevent.]

### Actor B

- ID: `actor_b`
- Name: [Display name for Actor B.]
- Agenda: [What Actor B wants to achieve or prevent.]

## Starting Canon Facts (Required)

Write at least one concrete, established fact, with one fact per bullet.
Add enough facts to support plausible actions and disagreements between the actors.
Include relevant capabilities, conditions, relationships, and constraints here rather than assuming them from an actor's name or agenda.
Facts must be non-blank and distinct, including after trimming surrounding whitespace and quotation marks.
During play, supporting arguments and vote shifts cite the full text of an existing canon fact.

- [An established fact about Actor A.]
- [An established fact about Actor B.]
- [An established shared condition, relationship, or constraint.]

## Scenario Framing (Optional, Not Canon)

[Briefly describe the interaction you want to explore and the desired narrative tone.]

If a detail should count as established reality, include it in the starting canon facts above.
This section is guidance for the playtest, not an additional engine state field or citation source.

## Questions to Explore (Optional)

These questions guide evaluation of the run, not predetermined outcomes.

- [What uncertainty or interaction do you want to explore?]
- [What would you like to inspect in the resulting trajectory?]

## Umpire Guidance (Optional)

- Pre-roll review of shifted votes: Disabled for this first playtest.
- Failure adjudication: On a failed roll, the human umpire supplies one new canon fact derived from a suitable lowest-vote peer `public_argument` (`source_voter_actor_id` set to that voter) or an independent consequence (`source_voter_actor_id: null`) when there are no peers or when no lowest-vote candidate offers a usable failure source (for example when all peer votes are `0` or `+1`), ensuring the statement matches neither existing `canon_facts` nor the failed proposal's `world_change_statement`.
- Additional plausibility guidance: [Optional guidance for narrative judgement, not a new mechanical rule.]

Failure consequences are decided after reviewing the failed turn, rather than filled in here.
Every resolved turn adds one new canon fact, whether the proposal succeeds or fails.
Plausibility guidance is interpreted by the narrative callbacks and umpire; the engine does not automatically enforce it.

## Before the Playtest

- [ ] Replace the title, actor names, agendas, and starting fact prompts.
- [ ] Remove unused prompts or optional sections.
- [ ] Check that every actor has a unique ID and appears exactly once in the actor order.
- [ ] Check that facts provide the grounding needed for the actors to act.
- [ ] Keep the turn count positive and the seed and starting indices non-negative integers.
- [ ] Keep the first run short so its proposals, votes, consequences, and final canon are easy to inspect.
- [ ] When copying this template into `scenarios/examples/` or `scenarios/private/<case>/`, adjust or remove relative links for the target directory depth and update `## Licence & Attribution` (replacing the public CC BY-SA 4.0 template notice on restricted private scenarios).

## Licence & Attribution

This public scenario template is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International Licence (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).
It accompanies game mechanics derived from [Triple-O](https://capacle.itch.io/triple-o) by Cezar Capacle (CC BY-SA 4.0) and Engle Matrix Games, invented by Chris Engle (CC BY-SA 4.0).
If you copy this template into `scenarios/private/` for a restricted scenario, replace the CC BY-SA 4.0 template notice above with the scenario's applicable confidentiality or ownership terms while keeping engine and framework attribution accurate.
