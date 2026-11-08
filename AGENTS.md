# AGENTS.md — Triple-O Matrix Engine (TOME) Agent Conventions

This document specifies repository calibration, architectural invariants, and agent interaction contracts for developing **TOME** (`efsalvarenga/tome`).

## 1. Project Overview & Architectural Boundaries

* **Repository Identity:** `tome` is a standalone, serverless, turn-based faction simulation engine and companion PWA client.
* **Parent Concept:** Integrates **Chris Engle Matrix Games** (structured arguments and probability resolution) with **Cezar Capacle's Triple-O framework** (posture step-dice and dual spark tables).
* **GitOps State Flow:** Pure state transformer:
  $$f(\text{WorldState}_{t}, \text{InputParameters}) \longrightarrow \text{WorldState}_{t+1} + \text{DowntimeDossier}_{\text{Tier 2}}$$
* **Core Philosophy:**
  1. *Zero Recurring Infrastructure Cost:* Runs on GitHub Actions and GitHub Pages.
  2. *Deterministic Mechanical Core:* Pure Python handles dice rolls, spark tables, posture shifts, and validation gates without network or LLM dependencies.
  3. *Strict Epistemic Grounding:* The Grounding / Linter Gate strictly prevents LLM hallucinations from introducing ungrounded canon facts or invalid voter shifts.
  4. *Air-Gapped Access Control:* Workflow passcode fail-gate, Personal Access Token (PAT) client storage, and concurrency locks prevent unauthorized spend.

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
