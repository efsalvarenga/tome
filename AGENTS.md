# AGENTS.md — TriO Matrix Engine (TOME) Agent Conventions

This document specifies repository calibration, architectural invariants, and agent interaction contracts for developing **TOME** (`efsalvarenga/tome`).

## 1. Project Overview & Architectural Boundaries

* **Repository Identity:** `tome` is a standalone, turn-based simulation engine for multi-actor systems whose behavioural rules are incomplete or uncertain.
  It lets a human umpire explore plausible outcomes of interactions between actors.
* **Scenario-Agnostic Engine:** The engine describes no particular setting, cast of actors, or application domain.
  Callers supply the actors, canon facts, and generators.
  Examples and test fixtures use neutral placeholders (Actor A, Actor B, "Fact 1.", "outcome X").
* **Parent Concept:** Integrates **Chris Engle Matrix Games** (structured argumentation and probability resolution under uncertainty) with **Cezar Capacle's Triple-O framework** (the Obvious / Option / Odd tier and d66 spark tables for divergent narrative cues).
* **Authoritative Design:** [`docs/designs/001_tome_core_architecture.md`](docs/designs/001_tome_core_architecture.md) defines the mechanics and the interface contract.
  Where this file and the specification differ, the specification wins.
* **State Flow:** The engine is a library with one entry point, `run(request, proposal_generator, peer_reviewer, failure_resolver, umpire_review=None)`:
  $$\mathcal{M}(\text{WorldState}_{t}, \text{RunRequest}) \longrightarrow (\text{WorldState}_{t+n}, \text{TurnRecord}_{1..n})$$
* **Core Philosophy:**
  1. *Deterministic Mechanical Core:* Pure Python handles the posture die, spark-table draws, vote validation, and 2d6 resolution without network or LLM dependencies; a supplied seed reproduces every engine-controlled draw.
  2. *Strict Epistemic Grounding:* Supporting arguments and vote shifts must cite existing canon facts; the human umpire may additionally reject illogical vote shifts.
  3. *Narrative-Only State:* There are no mechanical trackers; actor conditions exist only as canon facts, and every resolved turn adds exactly one new fact.
  4. *Transport-Neutral Boundary:* The caller owns transport, authorisation, persistence, presentation, and the choice of LLM provider.
  5. *Umpire Trajectory Exploration:* Empowers the human simulation umpire to inspect emergent complications, friction between actors, and alternative outcomes across stochastic runs.
* **Out of Scope:** A UI, hosting, deployment, and execution bridge belong in a separate repository; see the deferred scope in the specification's changelog.

## 2. Specification & Governance Protocols

* All major architectural features, schema changes, and engine stages must adhere to the **Elephant-Goldfish Model (EGM)**:
  * Specifications live in `docs/designs/<NNN>_<feature_slug>.md` using the EGM design template.
  * Zero-context adversarial critiques live in `docs/reviews/<NNN>_<feature_slug>_review.md`.
  * Specifications must pass `validate_egm.py` before core production implementation commences.
* **Strict No-Code Rule during Elephant Drafting:** Design specifications focus on contracts, state schemas, invariants, and edge cases before code is written.
* **One Sentence per Line:** In Markdown prose, write each sentence on its own source line for cleaner diffs; code blocks, tables, and headings are exempt.

## 3. Technology Stack & Standards

* **Language & Runtime:** Python 3.11+
* **Package & Environment Management:** `uv` (`pyproject.toml`)
* **Core Libraries:**
  * `pydantic` (v2) for strict runtime schema validation and serialization.
  * `pytest` for deterministic mechanical test suites.
  * `ruff` for linting and formatting.
* **LLM Integration:** Provider-agnostic; LLM calls live in the caller-supplied `proposal_generator` and `peer_reviewer`, never in the engine core.

## 4. Branching & Pull Request Protocols

* `main` is protected: PR required, force pushes blocked, deletions blocked, auto-branch deletion enabled.
* Development branches use clear prefixes: `feat/`, `fix/`, `docs/`, `chore/`.
* Commits should be atomic with clear semantic messages.
* **Autonomous Merge Prohibition [HUMAN-ONLY]:** Under NO circumstances may any autonomous agent call `gh pr merge`, invoke GitHub REST merge API endpoints, or merge topic branches directly into `main`. Merging PRs into `main` is strictly reserved for the human developer. Agents must push topic branches, open Pull Requests with verification proofs, present the PR URL to the user, and stop.
