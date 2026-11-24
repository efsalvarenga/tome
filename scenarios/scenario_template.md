# Scenario Playtest: [Scenario title]

Replace the bracketed prompts with your scenario.
Keep the run defaults for a first test, and add or remove actor sections and fact bullets as needed.
You do not need to prepare proposals, votes, dice rolls, or failure outcomes in advance.

This Markdown file is an authoring aid for an assisted playtest, not a file the engine loads directly.
During the playtest, a caller translates its contents into a `WorldState`, a `RunRequest`, and caller-supplied callback inputs as defined in the [core architecture specification](../docs/designs/001_tome_core_architecture.md).
See [README.md](README.md) for the `scenarios/` workspace layout, public examples, and `scenarios/private/` handling rules.

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
- Failure adjudication: The human umpire supplies a new, concrete consequence informed by a lowest-voted peer argument, or an independent consequence if there are no peers.
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

## Licence & Attribution

This public scenario template is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International Licence (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).
It accompanies game mechanics derived from [Triple-O](https://capacle.itch.io/triple-o) by Cezar Capacle (CC BY-SA 4.0) and Engle Matrix Games, invented by Chris Engle (CC BY-SA 4.0).
