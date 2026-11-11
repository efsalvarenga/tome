# AGENTS.md — TriO Matrix Engine (TOME) Agent Conventions

This document specifies repository calibration, architectural invariants, and agent interaction contracts for developing **TOME** (`efsalvarenga/tome`).

## 1. Project Overview & Architectural Boundaries

* **Repository Identity:** `tome` is a standalone, serverless simulation engine for multi-agent complex systems where fundamental behavioral laws are incomplete or uncertain, providing a formal computational testbed for human umpires and analysts to explore plausible realisations of multi-actor interactions.
* **Parent Concept:** Integrates **Chris Engle Matrix Games** (structured epistemic argumentation and probability resolution under uncertainty) with **Cezar Capacle's Triple-O framework** (structural posture step-dice and dual spark tables for non-mode-collapsing divergence).
* **GitOps State Flow:** Pure state transformer:
  $$\mathcal{M}(\text{WorldState}_{t}, \text{Interventions}) \longrightarrow \text{WorldState}_{t+1} + \text{SimulationDossier}$$
* **Core Philosophy:**
  1. *Zero Recurring Infrastructure Cost:* Runs on GitHub Actions and GitHub Pages.
  2. *Deterministic Mechanical Core:* Pure Python handles dice rolls, spark tables, posture shifts, and validation gates without network or LLM dependencies.
  3. *Strict Epistemic Grounding:* The Grounding / Linter Gate strictly prevents LLM hallucinations from introducing ungrounded facts or invalid voter shifts.
  4. *Air-Gapped Access Control:* Workflow passcode fail-gate, Personal Access Token (PAT) client storage, and concurrency locks prevent unauthorized spend.
  5. *Umpire Trajectory Exploration:* Empowers the human simulation umpire to inspect emergent complications, institutional friction, and counter-realities across stochastic runs.

## 2. Specification & Governance Protocols

* All major architectural features, schema changes, and engine stages must adhere to the **Elephant-Goldfish Model (EGM)**:
  * Specifications live in `docs/designs/<NNN>_<feature_slug>.md` using the EGM design template.
  * Zero-context adversarial critiques live in `docs/reviews/<NNN>_<feature_slug>_review.md`.
  * Specifications must pass `validate_egm.py` before core production implementation commences.
* **Strict No-Code Rule during Elephant Drafting:** Design specifications focus on contracts, state schemas, invariants, and edge cases before code is written.

## 3. Technology Stack & Standards

* **Language & Runtime:** Python 3.11+
* **Package & Environment Management:** `uv` (`pyproject.toml`)
* **Core Libraries:**
  * `pydantic` (v2) for strict runtime schema validation and serialization.
  * `pytest` for deterministic mechanical test suites.
  * `ruff` for linting and formatting.
* **Frontier LLM Integration:** Google Gemini (`google-genai`) with structured JSON schema output enforcement.
* **Client / UI:** Minimalist static PWA (`pwa/`) hosted on GitHub Pages communicating via GitHub REST API.

## 4. Branching & Pull Request Protocols

* `main` is protected: PR required, force pushes blocked, deletions blocked, auto-branch deletion enabled.
* Development branches use clear prefixes: `feat/`, `fix/`, `docs/`, `chore/`.
* Commits should be atomic with clear semantic messages.
* **Autonomous Merge Prohibition [HUMAN-ONLY]:** Under NO circumstances may any autonomous agent call `gh pr merge`, invoke GitHub REST merge API endpoints, or merge topic branches directly into `main`. Merging PRs into `main` is strictly reserved for the human developer. Agents must push topic branches, open Pull Requests with verification proofs, present the PR URL to the user, and stop.
