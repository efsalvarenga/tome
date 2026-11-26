# Scenarios Workspace

This directory holds the public playtest authoring template, neutral public examples, and the local boundary for non-public playtests.
Markdown files in `scenarios/` are human and assisted-playtest authoring aids rather than a file format loaded natively by `tome`.
A caller or playtest harness translates a scenario document into a `WorldState`, a `RunRequest`, and caller-supplied callback inputs (`proposal_generator`, `peer_reviewer`, `failure_resolver`, and optional `umpire_review`) as defined in the [core architecture specification](../docs/designs/001_tome_core_architecture.md).

## Workspace Layout

```text
scenarios/
  README.md                 # Workspace guide, private-handling policy, and licensing
  scenario_template.md      # Canonical blank authoring template (CC BY-SA 4.0)
  examples/
    actor_a_actor_b.md      # Neutral runnable public example (CC BY-SA 4.0)
  private/                  # Local-only directory; entire subtree ignored via /scenarios/private/
```

* [`scenario_template.md`](scenario_template.md) provides the single canonical template for defining run settings, actors, starting canon facts, and optional umpire guidance.
* [`examples/actor_a_actor_b.md`](examples/actor_a_actor_b.md) provides a complete, domain-neutral two-actor scenario that callers and tests can translate into a deterministic `tome.run(...)` invocation.
* `private/` is reserved for local, confidential, proprietary, or client-specific scenarios and is never tracked in Git.

## Running a Local Private Playtest

Git does not track empty ignored directories, so a fresh clone will not contain `scenarios/private/` until you create it locally.

```bash
mkdir -p scenarios/private/my_case
cp scenarios/scenario_template.md scenarios/private/my_case/scenario.md
```

* Create `scenarios/private/` with `mkdir -p scenarios/private` and add a dedicated subdirectory for your local scenario.
* Copy [`scenario_template.md`](scenario_template.md) into that subdirectory under `scenarios/private/` and fill in your run settings, actors, and starting canon facts.
* Adjust or remove relative links for the `scenarios/private/<case>/` directory depth, and replace the template's public CC BY-SA 4.0 notice under `## Licence & Attribution` with appropriate private handling or ownership terms.
* Translate the scenario into `WorldState`, `RunRequest`, and callback inputs in your local runner to execute the playtest.
* Write every derived artefact inside the same subdirectory under `scenarios/private/`, including serialised JSON requests and states, turn logs such as `log.jsonl`, checkpoints, rendered prompts, raw model responses, attachments, and replay reports.

## Private Handling & Derived Outputs

Outputs derived from a private scenario inherit the private handling of their source scenario unless the content owner explicitly approves a sanitised publication.
Do not copy excerpts, actor names, canon facts, logs, or trajectory summaries from `scenarios/private/` into tracked documentation, issue comments, pull requests, commit messages, or automated tests.
Public examples, documentation, and repository tests may reference only approved public inputs under `scenarios/` and neutral synthetic paths.

## Limitations of `.gitignore`

The `/scenarios/private/` rule in `.gitignore` is a convenience safeguard against accidental staging, not a security boundary.

* `.gitignore` reduces the risk of staging local files during ordinary `git add` workflows, but it is not encryption, access control, a licence grant, or a restriction on local tools reading files on disk.
* `.gitignore` does not protect files that are already tracked by Git, and a user or script can still bypass it by force-adding paths with `git add -f`.
* `.gitignore` does not prevent an agent, script, or caller from reading local files or sending content to an external service, so any external model invocation, remote processing, or publication of private material requires separate authorisation.
* If sensitive or restricted material is ever already tracked in Git, stop immediately and raise that fact with the repository owner rather than assuming `.gitignore` removes it or rewriting Git history without explicit permission.

## Licence & Attribution

Public scenario templates, documentation, and public examples tracked in `scenarios/` are licensed under the [Creative Commons Attribution-ShareAlike 4.0 International Licence (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/), distinct from the [MIT License](../LICENSE) that governs the repository's software code (including `src/tome/`).

These public playtest materials accompany game mechanics derived from:

* [Triple-O](https://capacle.itch.io/triple-o) by Cezar Capacle, licensed under CC BY-SA 4.0.
* Engle Matrix Games, invented by Chris Engle, licensed under CC BY-SA 4.0.

Placing third-party, client, or proprietary material inside your local `scenarios/private/` directory does not publish it to this repository or relicense it under CC BY-SA 4.0 or MIT.
