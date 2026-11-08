# Triple-O Matrix Engine (TOME)

[![CI](https://github.com/efsalvarenga/tome/actions/workflows/tome-cycle.yml/badge.svg)](https://github.com/efsalvarenga/tome/actions)
[![License: MIT](https://img.shields.io/badge/Code_License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/Content_License-CC_BY--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

A standalone, serverless, turn-based faction simulation engine and companion Progressive Web App (PWA) client for tabletop roleplaying campaigns.

TOME simulates faction initiatives during campaign downtime without relying on conversational consensus or unconstrained LLM hallucinations. It models world evolution as a pure state transformer:

$$f(\text{WorldState}_{t}, \text{InputParameters}) \longrightarrow \text{WorldState}_{t+1} + \text{DowntimeDossier}_{\text{Tier 2}}$$

---

## Theoretical Foundation

TOME fuses two pioneering tabletop roleplaying game frameworks:

1. **Chris Engle Matrix Games:**
   Actions are formulated as structured arguments rather than freeform narrative prompts:
   * **World-Change Statement:** A single declarative assertion specifying an altered fact in the world.
   * **Supporting Arguments (Pros):** Claims grounded strictly in existing canon facts or intrinsic faction traits.
   * **Peer Adjudication:** Non-active factions evaluate baseline plausibility, apply strategic shifts (The Cheeky Pivot), and cast weighted votes determining the resolution modifier.

2. **Cezar Capacle's Triple-O Framework:**
   Faction behavior and divergence are driven by structural posture and spark tables:
   * **Posture Step-Dice:** Faction structural integrity dictates its posture die: `Stable` ($1d4$), `Pressured` ($1d6$), or `Cornered` ($1d8$).
   * **The Triple-O Split:**
     * **1–3 (The Obvious):** Predictable initiatives aligning with core traits ($75\%$ Stable, $50\%$ Pressured, $37.5\%$ Cornered).
     * **4–5 (The Option):** Lateral, strategically logical alternatives ($25\%$ Stable, $33.3\%$ Pressured, $25\%$ Cornered).
     * **6+ (The Odd):** Volatile gambits, doctrinal shifts, or radical escalations ($0\%$ Stable, $16.7\%$ Pressured, $37.5\%$ Cornered).
   * **Dual Spark Table Seeding:** Paired $d66$ rolls across Action, Focus, Method, Disposition, and Motivation tables force semantic divergence and prevent LLM mode-collapse.

---

## Architectural Principles

* **Zero Recurring Infrastructure Cost:** Executes entirely on free-tier serverless orchestration (GitHub Actions runners for compute, GitHub Pages for static client hosting).
* **Deterministic Mechanical Core:** Dice mechanics, spark table selections, posture step transitions, and validation gates run in pure, deterministic Python with zero network dependencies.
* **Strict Epistemic Grounding (The Linter Gate):** Peer reviewers cannot invent setting details or apply arbitrary voting modifiers. Any vote shift must cite an exact, unexhausted canon fact or faction trait; invalid or hallucinated citations revert immediately to baseline.
* **Air-Gapped Access Control & Cost Containment:** 4-layer defense in depth: client-side Personal Access Token (PAT) storage, workflow execution passcode gate, concurrency execution locks, and provider-level budget spend ceilings.
* **Elephant-Goldfish Model (EGM) Governance:** All architectural stages and state schemas follow formal specifications (`docs/designs/`) verified by zero-context adversarial reviews (`docs/reviews/`) and mechanical contract linters.

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
│   └── tome/               # Core Python engine package
│       ├── __init__.py     # Package entrypoint & version
│       ├── dice.py         # Step-dice (1d4, 1d6, 1d8), d66, and 2d6 resolution
│       ├── models.py       # Pydantic v2 schemas (WorldState, Faction, Proposal, PeerEvaluation)
│       ├── runner.py       # Turn orchestration loop & state transformer
│       ├── tables.py       # Canonical d66 Triple-O spark tables
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

### Installation

Clone the repository and set up a development environment:

```bash
git clone https://github.com/efsalvarenga/tome.git
cd tome

# Create and activate virtual environment with uv
uv venv
source .venv/bin/activate

# Install package in editable mode with development dependencies
uv pip install -e ".[dev]"
```

### Running Tests

Execute the deterministic mechanical test suite:

```bash
pytest
```

### Code Formatting & Linting

Verify formatting and linting compliance with `ruff`:

```bash
ruff check .
ruff format --check .
```

### Validating EGM Specification Contracts

If `artifice` is available in your environment, validate specification contracts:

```bash
python3 path/to/artifice/scripts/validate_egm.py .
```

---

## Attribution & Acknowledgements

This software implements game mechanics derived from:
- Triple-O by Cezar Capacle (https://capacle.itch.io/triple-o), licensed under CC BY-SA 4.0.
- Engle Matrix Games, invented by Chris Engle, licensed under CC BY-SA 4.0. Matrix Games were invented by Chris Engle.

---

## License

TOME is an open-source project licensed under a dual-license structure:

* **Source Code:** Licensed under the [MIT License](LICENSE) — free for use, modification, and distribution.
* **Game Mechanics, Spark Tables & Textual Documentation:** Licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).
