# TriO Matrix Engine (TOME)

[![License: MIT](https://img.shields.io/badge/Code_License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/Content_License-CC_BY--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

A turn-based simulation engine for **multi-actor systems whose behavioural rules are incomplete, uncertain, or emergent**.

TOME lets a human umpire explore **plausible outcomes of interactions between actors**.
It is scenario-agnostic: the caller supplies the actors, the established facts, and the generators that propose and review changes.

$$\mathcal{M}(\text{WorldState}_{t}, \text{RunRequest}) \longrightarrow (\text{WorldState}_{t+n}, \text{TurnRecord}_{1..n})$$

> **Status:** The [core architecture specification](docs/designs/001_tome_core_architecture.md) (Spec 1.1.1, Interface Contract 1.1.0) is approved.
> The code in `src/tome/` still implements an earlier design and is being rewritten to match it.

---

## The Problem: Simulating Under Incomplete Behavioural Knowledge

Many multi-agent simulations rely on closed-form equations, utility functions, or fixed state machines.
These break down when:

1. **Actor behaviour is not fully known:** actors adapt, reason from their own interests, and change course under pressure.
2. **Language models are left unconstrained:** free-running LLM rollouts either invent facts and capabilities or settle into bland consensus.
3. **One trajectory is not enough:** an umpire needs to see a range of plausible outcomes, including complications and failures.

TOME combines **Chris Engle's Matrix Games** with **Cezar Capacle's Triple-O framework** in a grounded, reproducible state transformer.

---

## How a Turn Works

```text
 posture die (d6) ──► TriO tier: Obvious (1-3) / Option (4-5) / Odd (6)
 spark tables     ──► two tables drawn at random, one d66 entry from each
        │
        ▼
 proposal         ──► a new world-change statement, supported by canon facts
        │
        ▼
 peer review      ──► every other actor votes -1 / 0 / +1, may shift one step,
                      and must cite a canon fact to shift
        │
        ▼
 umpire review    ──► (optional) reject illogical shifts before the roll
        │
        ▼
 resolution       ──► 2d6 + clamped vote sum (-3..+3) against 7
        │
        ├── 7+      Success: the proposal becomes a canon fact
        └── below 7 Failure: the umpire turns the lowest-voted argument
                    into a new canon fact explaining why it failed
```

* **TriO tier:** each turn rolls a d6 posture die; the tier is a narrative cue, not a persistent tracker.
* **Spark tables:** two distinct d66 tables are chosen at random each turn, independently of the tier, and their entries become narrative cues for the proposal.
  The engine ships the Triple-O template tables by default, and a caller may replace them with a complete set of its own.
* **Grounding:** supporting arguments and vote shifts must cite an existing canon fact.
  Citations are checked mechanically; the human umpire may still reject illogical reasoning.
* **Every turn changes the world:** each resolved turn adds exactly one new canon fact, on success or failure, and advances time.
* **No mechanical trackers:** actor conditions exist only as narrative facts in canon.

---

## Execution Contract

The engine is a library with one entry point:

```text
run(request, proposal_generator, peer_reviewer, failure_resolver, umpire_review=None) -> RunResult
```

* **Input:** a complete world state, a number of turns, and optional spark tables, first-round order, and random seed.
* **Callables:** the caller supplies the proposal generator and peer reviewer (typically wrapping an LLM) and the umpire's failure resolver; the pre-roll umpire review is optional.
* **Output:** the final world state and one audit record per turn.
* **Guarantees:** the input is never mutated, a failed run returns no partial result, and a seeded run reproduces every engine-controlled draw.
* **Caller's responsibility:** transport, authorisation, persistence, and presentation.

See the [specification](docs/designs/001_tome_core_architecture.md) for the full contract, invariants, and test requirements.

---

## Project Structure

```text
tome/
├── docs/
│   ├── designs/            # EGM design specifications
│   │   └── 001_tome_core_architecture.md
│   └── reviews/            # Zero-context Goldfish reviews
│       └── 001_tome_core_architecture_review.md
├── src/
│   └── tome/               # Simulation engine (being rewritten to Spec 1.1.1)
│       ├── __init__.py     # Package entry point and version
│       ├── dice.py         # Dice mechanics
│       ├── models.py       # Pydantic v2 schemas
│       ├── runner.py       # Turn orchestration
│       ├── tables.py       # Default d66 spark tables (Triple-O template)
│       └── validator.py    # Grounding and adjudication rules
├── tests/
│   └── test_tome_core.py   # Deterministic test suite
├── AGENTS.md               # Repository conventions for agents
├── pyproject.toml          # Project metadata, dependencies, and tooling
└── LICENSE                 # Dual MIT and CC BY-SA 4.0 licences
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

# Create and activate a virtual environment with uv
uv venv
source .venv/bin/activate

# Install the package in editable mode with development dependencies
uv pip install -e ".[dev]"
```

### Running the Test Suite

```bash
pytest
```

### Formatting & Static Analysis

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
