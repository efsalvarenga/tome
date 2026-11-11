# TriO Matrix Engine (TOME)

[![License: MIT](https://img.shields.io/badge/Code_License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/Content_License-CC_BY--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

A serverless, turn-based simulation engine and companion exploration dashboard for modeling **complex, multi-agent systems where fundamental behavioral dynamics are incomplete, uncertain, or emergent**.

TOME provides a formal computational framework for analysts and human umpires to explore **plausible realisations of multi-actor interactions** across geopolitical, strategic, institutional, and socio-technical domains.

$$\mathcal{M}(\text{WorldState}_{t}, \text{Interventions}) \longrightarrow \text{WorldState}_{t+1} + \text{SimulationDossier}$$

---

## The Problem: Simulating Under Incomplete Behavioral Knowledge

Traditional multi-agent simulations rely on closed-form mathematical equations, utility optimization functions, or rigid heuristic state machines. In complex human, organizational, and strategic systems, these models frequently break down because:

1. **The fundamentals of agent behavior are not all known:** Human and institutional actors do not act according to fixed differential equations; they adapt creatively, perceive situations through motivated biases, and change doctrines under stress.
2. **Generative LLMs suffer from ungrounded mode collapse:** Pure conversational LLM rollouts either drift into unconstrained hallucinations (inventing non-existent facts and capabilities) or collapse into generic, bland consensus.
3. **The Umpire requires observable, stochastic realisations:** Rather than seeking a single "optimal" trajectory, an analyst or simulation umpire needs to observe the *envelope of plausible realisations*—including institutional friction, unexpected complications, and counter-realities.

TOME solves this by wedding **Chris Engle Matrix Games** with **Cezar Capacle's Triple-O framework** inside a strictly grounded, deterministic state transformer.

---

## Theoretical Architecture

```text
                                  ┌────────────────────────┐
                                  │   Structural Posture   │
                                  │  Stable / Pressured /  │
                                  │        Cornered        │
                                  └───────────┬────────────┘
                                              │ Step-Die (d4, d6, d8)
                                              ▼
┌───────────────────────┐         ┌────────────────────────┐
│   Dual Spark Tables   ├────────►│    TriO Action Tier    │
│ Paired d66 Divergence │         │ Obvious / Option / Odd │
└───────────────────────┘         └───────────┬────────────┘
                                              │
                                              ▼
                                  ┌────────────────────────┐
                                  │ Structured Proposal    │
                                  │ Statement + Grounded   │
                                  │ Pros (Traits & Canon)  │
                                  └───────────┬────────────┘
                                              │
                                              ▼
                                  ┌────────────────────────┐
                                  │ Subagent Peer Review   │
                                  │ Plausibility + Motivated│
                                  │ Reasoning Pivot        │
                                  └───────────┬────────────┘
                                              │
                                              ▼
                                  ┌────────────────────────┐
                                  │ Epistemic Linter Gate  │
                                  │ (Revert Hallucinations)│
                                  └───────────┬────────────┘
                                              │ Net Modifier [-3, +3]
                                              ▼
                                  ┌────────────────────────┐
                                  │ 2d6 Resolution Matrix  │
                                  │ 10+: Ratified Reality  │
                                  │ 7-9: Fractured Reality │
                                  │ 4-6: Contested Friction│
                                  │ <=3: Counter-Reality   │
                                  └────────────────────────┘
```

### 1. Engle Matrix Argumentation
Originally developed for professional wargaming, policy analysis, and strategic conflict studies, Matrix Games model reality through **structured epistemic argumentation** rather than physical calculations:
* **World-Change Statement:** A declarative claim that an actor alters a state variable or geopolitical/institutional reality.
* **Supporting Arguments (Pros):** Concrete arguments grounded strictly in established canon facts or intrinsic actor traits.
* **Adversarial Peer Review:** Other actors in the system evaluate baseline plausibility from their operational perspectives, apply strategic motivated shifts (*The Cheeky Pivot*), and argue complications or counter-arguments.

### 2. TriO Behavioral Posture & Divergence
Actors shift behavioral modes based on their internal structural integrity:
* **Structural Posture:**
  * **Stable ($1d4$):** Institutionally secure. $75\%$ predictable doctrinal moves (*The Obvious*), $25\%$ lateral innovations (*The Option*), $0\%$ radical gambits.
  * **Pressured ($1d6$):** Under operational friction or resource strain. $50\%$ Obvious, $33.3\%$ Option, $16.7\%$ volatile gambits (*The Odd*).
  * **Cornered ($1d8$):** Existential threat or institutional crisis. $37.5\%$ Obvious, $25\%$ Option, $37.5\%$ radical gambits (*The Odd*).
* **Dual Spark Seeding ($d66$):** Paired stochastic seeds across Action, Focus, Method, Disposition, and Motivation force semantic divergence and prevent the engine from settling into predictable LLM attractors.

### 3. Epistemic Linter Gate (Anti-Hallucination Invariant)
To prevent generative agents from fabricating capabilities or inventing non-existent historical precedents:
* Any actor attempting to shift its vote must cite an **exact, unexhausted canon fact or faction trait**.
* If the citation fails string verification or cites an already exhausted capability, the linter gate **reverts the vote to baseline**.
* Validly cited traits are flagged as exhausted for the simulation cycle, preventing infinite leverage.

### 4. Matrix Resolution Bands
The net peer consensus modifier ($\text{clamp}(\sum \text{votes}, -3, 3)$) adjusts a $2d6$ dice roll against Target Number 7:
* **$10+$ (Ratified Reality):** The proposed change manifests into canon facts; the actor improves posture; the highest supporting peer gains secondary leverage.
* **$7\text{–}9$ (Fractured Reality):** The change manifests, but the sharpest counter-argument crystallizes into an active complication hook.
* **$4\text{–}6$ (Contested Friction):** The change fails to manifest; both the proposal and opposing arguments become ambient intelligence/rumors.
* **$\le 3$ (Counter-Reality):** The initiative catastrophically backfires; the strongest counter-argument crystallizes as the new reality; the active actor degrades in posture.

---

## Architectural Principles

* **Deterministic Mechanical Core:** All dice rolls, spark table lookups, posture transitions, linter gates, and resolution matrices execute in pure, reproducible Python with zero network calls.
* **Zero Recurring Infrastructure Cost:** Serverless GitOps architecture running on GitHub Actions for compute and GitHub Pages for static exploration client interfaces.
* **Air-Gapped Access Control & Cost Containment:** 4-layer defense in depth: client-side Personal Access Token (PAT) storage, workflow execution passcodes, concurrency execution locks, and cloud spend limits.
* **Umpire Dossier Emission:** Every simulation cycle outputs both an updated machine-readable state ledger (`world_state.json`, `history.jsonl`) and an analytical briefing dossier (`_sessions/_downtime/cycle_XX.md`) detailing actor rationales, peer challenges, and emergent friction.

---

## Project Structure

```text
tome/
├── docs/
│   ├── designs/            # Formal EGM architecture specifications
│   │   └── 001_tome_core_architecture.md
│   └── reviews/            # Adversarial zero-context Goldfish reviews
│       └── 001_tome_core_architecture_review.md
├── src/
│   └── tome/               # Core Python simulation engine
│       ├── __init__.py     # Package entrypoint & version
│       ├── dice.py         # Step-dice (1d4, 1d6, 1d8), d66, and 2d6 resolution
│       ├── models.py       # Pydantic v2 schemas (WorldState, Faction, Proposal, PeerEvaluation)
│       ├── runner.py       # Turn orchestration loop & state transformer
│       ├── tables.py       # Canonical d66 TriO spark tables
│       └── validator.py    # Epistemic Linter Gate, tie-breakers, and outcome mutators
├── tests/
│   └── test_tome_core.py   # Deterministic unit and integration test suite
├── AGENTS.md               # Repository conventions and agent interaction contracts
├── pyproject.toml          # Project metadata, dependencies, and tooling configuration
└── LICENSE                 # Dual MIT & CC BY-SA 4.0 licenses
```

---

## Quickstart & Development

### Prerequisites

* Python 3.11 or later
* [`uv`](https://docs.astral.sh/uv/) (recommended) or standard `pip`

### Setup

```bash
git clone https://github.com/efsalvarenga/tome.git
cd tome

# Create and activate virtual environment with uv
uv venv
source .venv/bin/activate

# Install package in editable mode with development dependencies
uv pip install -e ".[dev]"
```

### Running the Mechanical Verification Suite

Execute the deterministic test suite:

```bash
pytest
```

### Code Formatting & Static Analysis

```bash
ruff check .
ruff format --check .
```

---

## Attribution & Acknowledgements

This software implements game mechanics derived from:
- Triple-O by Cezar Capacle (https://capacle.itch.io/triple-o), licensed under CC BY-SA 4.0.
- Engle Matrix Games, invented by Chris Engle, licensed under CC BY-SA 4.0. Matrix Games were invented by Chris Engle.

---

## License

TOME is an open-source project licensed under a dual-license structure:

* **Simulation Engine & Software Code:** Licensed under the [MIT License](LICENSE) — freely available for analytical, research, educational, and commercial integration.
* **Game Mechanics, Spark Tables & Content:** Licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).
