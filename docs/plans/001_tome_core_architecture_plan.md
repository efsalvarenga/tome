# Implementation Plan: TOME Core Architecture (Spec 1.1.2)

*   **Author:** efsalvarenga
*   **Status:** Approved
*   **Date:** 2026-11-17
*   **Approved:** 2026-11-18 by the human developer, accepting the plan after the Stage 9 implementation-readiness review stopped past its five-round cap with no open findings; see the [review record](../reviews/001_tome_core_architecture_egm/implementation_readiness/implementation_readiness_report.md)
*   **Amended:** 2026-11-23 by the human developer; see [Amendment A1](#amendment-a1-post-review-simplifications-2026-11-23) for approved code changes and [Amendment A2](#amendment-a2-delivery-and-process-deviations-2026-11-23) for every other deviation from this plan, recorded for final human review
*   **Implements:** [Spec 001, version 1.1.2, Interface Contract 1.1.0](../designs/001_tome_core_architecture.md), approved 2026-11-17 at commit `7d3fef1`

This document decides how to implement the approved specification.
It does not restate or change the specification's goals, alternatives, schemas, invariants, or tests.
Where this plan and the specification disagree, the specification wins, except for decision D12, which the human developer confirmed on 2026-11-17.
An implementer who finds such a disagreement, or a question this plan does not answer, stops and raises it with the human developer instead of choosing.

--------------------------------------------------------------------------------

## Detailed Implementation Plan

### Starting Baseline

These facts were measured on 2026-11-17 on branch `feat/trio-engine-1.1` at commit `7d3fef1`, before this plan was written.

*   The legacy engine in `src/tome/` implements an earlier design: step-dice postures, traits and exhaustion, outcome bands, rumours, and urgency ordering.
*   Its 8 tests in `tests/test_tome_core.py` pass on Python 3.11 with Pydantic 2.14.3, and Ruff lint and format checks pass.
*   The 8 legacy tests check the legacy mechanics, not Spec 1.1.2.
*   Those tests were run with `PYTHONPATH=src uv run --isolated --no-project --python 3.11 --with 'pydantic>=2' --with 'pytest>=8' python -m pytest -p no:cacheprovider`, because no project environment exists yet; without `PYTHONPATH=src`, collection fails because `tome` is not importable.
*   Ruff was run as `uvx ruff check --no-cache .` and `uvx ruff format --no-cache --check .`.
*   Pydantic behaviours this plan relies on were checked with throwaway scripts outside the repository, run by `uv run --isolated --no-project --python 3.11 --with 'pydantic>=2' python <script>`, which resolved Pydantic 2.14.3: an explicit `null` is rejected for a field annotated without `None`; nested model instances, including ones built with `model_construct`, are fully validated under `revalidate_instances="always"`; and `model_dump(mode="json")` writes integer dictionary keys as decimal strings.
*   The same method confirmed the draw values of the Invariant 14 golden vectors and of the Section 3.4 worked example: seed 20 gives posture 6, tables Focus then Method, keys 66 and 13, and dice 5 and 2.
*   In a temporary copy of the repository at `7d3fef1`, with `.python-version` set to `3.11`, `uv lock` resolved Pydantic 2.14.3, `uv sync --locked --extra dev` installed `tome` in editable mode through the existing Hatchling build backend, and the three `scripts/lint.sh` commands (Target File 3) passed on the 8 legacy tests without `PYTHONPATH`.
*   In the same temporary copy, `uv lock` pinned Ruff 0.17.5, whose `ruff format --check` also covers Markdown files: it fails if the code in a `python`-fenced block would be reformatted, and it does not edit files.
*   On 2026-11-18, none of the 29 Markdown files in the worktree, tracked and untracked, including this plan and its review records, contained a `python` or `py` fence, and the format check passed on all checked files.
*   `python3 "$HOME/.local/share/artifice/scripts/validate_egm.py" . --spec 001` exits 0 at `7d3fef1` on the default `python3`.
*   `src/tome/tables.py` defines the five `trio-d66-v1` tables and has no imports.
*   The default `python3` on the development machine is 3.9.6; `python3.11` and `uv` are installed.
*   There is no `uv.lock`, no `.python-version`, no `scripts/` directory, and no CI workflow.

### Decisions Fixed by This Plan

The human developer (Source `Author`) made decisions D1 to D4 and confirmed D12.
The other decisions follow from the specification (Source `Spec`), interpretations of its wording (Source `Interpretation`), repository conventions (Source `AGENTS.md`), or this plan (Source `Plan`), and are recorded so the implementer does not make them.

| # | Decision | Choice | Source |
| :--- | :--- | :--- | :--- |
| D1 | Plan location | This file, `docs/plans/001_tome_core_architecture_plan.md`; `AGENTS.md` documents the `docs/plans/` convention. | Author |
| D2 | Legacy engine | Build the new engine alongside the legacy engine; the legacy engine stays importable and its tests stay green until Phase 5 deletes it. | Author |
| D3 | Module layout | New subpackage `src/tome/engine/`; Phase 5 deletes the legacy files and renames none; `tome/__init__.py` re-exports the public API. | Author |
| D4 | Verification gate | New executable `scripts/lint.sh` running Ruff lint, Ruff format check, and pytest through `uv run --locked --extra dev`; `uv.lock` is committed. | Author |
| D5 | Python version | New `.python-version` containing `3.11`, so `uv` uses the interpreter named by the golden vectors (Invariant 14). | Spec |
| D6 | Unit test file | `tests/test_tome_core.py`, as named in Spec Section 7; Phase 0 renames the legacy tests to `tests/test_legacy_engine.py` to free the name. | Spec |
| D7 | Integration test file and helpers | `tests/test_tome_integration.py`, and the plain helper module `tests/support.py`, imported as `from support import ...`. This relies on pytest's default `prepend` import mode; `tests/` must not contain `__init__.py`. A plain module is used because `INVALID_REQUEST_CASES` feeds `pytest.mark.parametrize`, which fixtures cannot supply. | Plan |
| D8 | Default table assembly | `tome.engine.mechanics` builds the default `SparkTables` from the `TABLE_*` constants; `src/tome/tables.py` is not edited, so the `trio-d66-v1` mappings cannot drift. | Spec Section 2.2 |
| D9 | Schema technology | Pydantic v2 models with `ConfigDict(strict=True, extra="forbid", revalidate_instances="always")`. | `AGENTS.md`, Spec Section 3.0 |
| D10 | Accepted callback return values | A `dict` or other `Mapping`, or an object for which `isinstance(raw, model_cls)` holds, so subclasses are accepted; such an instance is re-validated from `model_dump()`. Any other type, including an unrelated model class, is malformed. | Interpretation of Spec Section 3.5, "plain mapping or an equivalent model" |
| D11 | Callback invocation | Positional arguments in the order of the Spec Section 3.5 signatures. | Interpretation of Spec Section 3.5 |
| D12 | Callback exceptions | Any `Exception` other than `MemoryError` raised by a callback, including a `RunError`, becomes that callback's error type, chained with `from`. `MemoryError` propagates unchanged. Exceptions that are not `Exception` subclasses, such as `KeyboardInterrupt`, propagate unchanged. A callback signals cancellation by raising an `Exception` subclass, such as `concurrent.futures.CancelledError` or a caller-defined cancellation exception; it is wrapped like any other failure. `asyncio.CancelledError` is not an `Exception` subclass and propagates unchanged. | Author, 2026-11-17: interpretation of Spec Sections 2.8 and 3.5, kept over the broader wording of the specification passages listed after this table |
| D13 | Unexpected engine-internal exceptions | After request validation, any `Exception` raised by engine code and not already converted to a callback error type by `_validate_output` (Target File 10), other than a `RunError`, `MemoryError`, `RecursionError`, or `SystemError`, becomes `MechanicsError`, chained with `from`. A `RunError` is re-raised unchanged because it is already typed; the other three are re-raised unchanged because Section 2.8 forbids relabelling resource exhaustion or interpreter failure as `MechanicsError`. Exceptions that are not `Exception` subclasses propagate unchanged. | Interpretation of Invariant 15 and Section 2.8 |
| D14 | Request input forms | `run()` accepts a `Mapping` or an object for which `isinstance(request, RunRequest)` holds; a `Mapping` is converted with `dict(request)` before validation, and an instance is re-validated from `model_dump(exclude_none=True)`. Any other type, including a JSON string, raises `InvalidRunRequestError`. | Interpretation of Spec Sections 3.5 and Edge Case 5 |
| D15 | Coverage target | No numeric coverage gate and no coverage dependency; the requirement is the Section 7 traceability table below. | Plan |
| D16 | New dependencies | None. Pydantic, pytest, and Ruff are already declared in `pyproject.toml`. | Plan |
| D17 | Branch and merge | Work continues on `feat/trio-engine-1.1`; merging into `main` is reserved for the human developer. | `AGENTS.md` |

Interpretations D10, D11, D13, and D14 fix choices the specification leaves open and change no behaviour it defines.
D12 narrows every specification passage that says a callback failure or cancellation raises a typed error, including the two Section 3.5 sentences for the umpire review and the failure resolver, Edge Cases 6, 11, and 14, Invariant 15, and the Section 7 "Umpire Audit and Errors" and "Failure Resolver Errors" bullets.
`MemoryError` propagates because Section 2.8 states that memory exhaustion can prevent delivery of a typed `RunFailure`.
Among `Exception` subclasses, D12 exempts only `MemoryError`, so a callback's `RecursionError` or `SystemError` becomes that callback's error type; D13 re-raises engine-raised ones unchanged, because Section 2.8 forbids only relabelling them as `MechanicsError`.
Exceptions that are not `Exception` subclasses propagate because Python reserves them for stopping or cancelling execution: wrapping `KeyboardInterrupt`, `SystemExit`, or `asyncio.CancelledError` would stop Ctrl+C, `sys.exit()`, and asyncio task cancellation from behaving normally.
A future specification revision should align those passages with D12.

### File Boundary

The implementer may create, modify, rename, or delete only these files.
Any other file change, including to `pyproject.toml`, `src/tome/tables.py`, `.gitignore`, or the specification, is out of bounds.
File Boundary exception: this plan and its review records under `docs/reviews/001_tome_core_architecture_egm/implementation_readiness/` may change only through the EGM review workflow.

| Path | Action | Phase | Rationale |
| :--- | :--- | :--- | :--- |
| `.python-version` | Create | 0 | Pins `uv` to Python 3.11 (D5). |
| `uv.lock` | Create with `uv lock` | 0 | Reproducible runtime and development dependency versions for the gate (D4); the Hatchling build backend is not pinned by `uv.lock`, and a build failure follows the `scripts/lint.sh` stop-and-raise rule. |
| `scripts/lint.sh` | Create, executable | 0 | Single verification gate (D4). |
| `tests/test_tome_core.py` | Rename to `tests/test_legacy_engine.py` | 0 | Frees the name the specification assigns to the new unit tests (D6). |
| `README.md` | Modify | 0, 5 | Phase 0: development commands. Phase 5: status and project structure. |
| `AGENTS.md` | Modify | 0 | Documents the verification gate and lockfile. |
| `src/tome/engine/__init__.py` | Create | 1, 4 | Phase 1: package docstring only. Phase 4: public exports. |
| `src/tome/engine/errors.py` | Create | 1 | `RunError` hierarchy. |
| `src/tome/engine/text.py` | Create | 1 | Section 3.0 normalization and matching. |
| `src/tome/engine/models.py` | Create | 1 | Contract schemas from Sections 3.1 to 3.5. |
| `tests/support.py` | Create | 1, 4 | Plain helper module imported by both test files (D7). |
| `tests/test_tome_core.py` | Create | 1 to 4 | Section 7 unit tests. |
| `src/tome/engine/mechanics.py` | Create | 2 | Dice, tiers, spark draws, resolution arithmetic. |
| `src/tome/engine/gates.py` | Create | 3 | Validation gates for callback outputs. |
| `src/tome/engine/protocols.py` | Create | 4 | Callback protocol types. |
| `src/tome/engine/runner.py` | Create | 4 | The `run` entry point. |
| `src/tome/__init__.py` | Modify | 4 | Re-exports the public API; keeps `__version__ = "0.1.0"`. |
| `tests/test_tome_integration.py` | Create | 4 | Section 7 integration tests. |
| `src/tome/models.py` | Delete | 5 | Legacy schemas. |
| `src/tome/dice.py` | Delete | 5 | Legacy step-dice. |
| `src/tome/validator.py` | Delete | 5 | Legacy gates and outcome bands. |
| `src/tome/runner.py` | Delete | 5 | Legacy cycle runner. |
| `tests/test_legacy_engine.py` | Delete | 5 | Legacy tests. |

### Phases and Checkpoints

Every phase ends with `./scripts/lint.sh` exiting 0.
Phases 1 to 4 follow a test-first cycle: a red test commit, a green feature commit, and an optional refactor commit.
The red commit is the only point where the gate is expected to fail.
Commit messages for Phases 1 to 5 use Conventional Commit types with the scope `engine`, for example `test(engine): assert contract models for spec 001`; Phase 0 uses `build(tooling)`.

#### Phase 0: Tooling Baseline

0.  Precondition: this plan, its review records under `docs/reviews/001_tome_core_architecture_egm/implementation_readiness/`, and the `AGENTS.md` `docs/plans/` convention are committed, and the worktree is clean.
1.  Create `.python-version` containing the single line `3.11`.
2.  Rename `tests/test_tome_core.py` to `tests/test_legacy_engine.py` with `git mv`; do not change its content.
3.  Run `uv lock` and stage the resulting `uv.lock`.
4.  Create `scripts/lint.sh` as described under Target File Details and make it executable with `chmod +x`.
5.  Update `README.md` and `AGENTS.md` as described under Target File Details.
6.  Exit gate: `./scripts/lint.sh` passes with the 8 legacy tests.
7.  Commit all Phase 0 changes in one commit with subject `build(tooling): add locked uv verification gate`; its body records the Pydantic and Ruff versions that `uv.lock` resolved.

#### Phase 1: Contract Models, Errors, and Normalization

0.  Run `python3 "$HOME/.local/share/artifice/scripts/validate_egm.py" . --spec 001` and confirm exit code 0.
    Use the default `python3`; the validator does not need the project environment.
1.  Red: add the Phase 1 tests listed in the traceability table, plus the Phase 1 helpers in `tests/support.py`.
2.  Green: create `src/tome/engine/__init__.py`, `errors.py`, `text.py`, and `models.py`.
3.  Exit gate: lint script passes with legacy and Phase 1 tests.

#### Phase 2: Mechanics

1.  Red: add the Phase 2 tests.
2.  Green: create `src/tome/engine/mechanics.py`.
3.  Exit gate: lint script passes.

#### Phase 3: Validation Gates

1.  Red: add the Phase 3 tests; they construct `TurnCues` and peer evaluations directly and need no new helpers.
2.  Green: create `src/tome/engine/gates.py`.
3.  Exit gate: lint script passes.

#### Phase 4: Runner and Public API

1.  Red: add the Phase 4 unit tests, `tests/test_tome_integration.py`, and the Phase 4 helpers in `tests/support.py`.
2.  Green: create `protocols.py` and `runner.py`, complete `src/tome/engine/__init__.py`, and update `src/tome/__init__.py`.
3.  Exit gate: lint script passes; every row of the traceability table has a passing test.

#### Phase 5: Legacy Removal and Documentation

1.  Delete the five legacy files listed in the file boundary.
2.  Update `README.md` status and project structure.
3.  Confirm that `git grep -nE 'tome\.(models|dice|validator|runner)([^A-Za-z0-9_]|$)|from (tome|\.\.) import ([^#]*[^A-Za-z0-9_])?(models|dice|validator|runner)([^A-Za-z0-9_]|$)|from \.\.(models|dice|validator|runner)([^A-Za-z0-9_]|$)' -- src tests` returns nothing.
    The pattern avoids `\b`, because `git grep -E` on macOS does not support it and a pattern using it silently matches nothing.
    At `7d3fef1` it reports 9 matching legacy import lines in `src/tome/` and `tests/`, which confirms that it works.
    `git grep` searches tracked files only, so `__pycache__` is excluded.
    Relative imports inside `tome.engine`, such as `from .models import`, are not matched, because they refer to the new modules.
    The search checks single lines; a package-relative import such as `from . import models`, or a module name on a later line of a multi-line import, is caught by the exit gate instead, because importing a deleted module fails when `tome` and the test modules load.
4.  Exit gate: lint script passes with only the new tests.
5.  Commit: `refactor(engine): remove legacy engine superseded by spec 001`.

### Target File Details

#### 1. `.python-version` (Create)

*   **Type / Scope:** `uv` interpreter pin.
*   **Proposed Changes:** One line, `3.11`.

#### 2. `uv.lock` (Create)

*   **Type / Scope:** Generated lockfile.
*   **Proposed Changes:** Produced by `uv lock` from the unchanged `pyproject.toml`; never edited by hand.

#### 3. `scripts/lint.sh` (Create)

*   **Type / Scope:** Bash verification gate, mode `755`.
*   **Proposed Changes:**
    *   Shebang `#!/usr/bin/env bash` and `set -euo pipefail`.
    *   Change to the repository root, resolved from the script's own location.
    *   Run, in order, stopping at the first failure:
        1.  `uv run --locked --extra dev ruff check .`
        2.  `uv run --locked --extra dev ruff format --check .`
        3.  `uv run --locked --extra dev pytest`
    *   The script does not call `validate_egm.py`, because that validator lives outside the repository.
    *   `uv run` installs the project in editable mode through the existing Hatchling build backend, so the gate needs no `PYTHONPATH`; if that build fails, stop and raise it with the human developer, because `pyproject.toml` is outside the file boundary.
    *   With the locked Ruff, the format check also covers Markdown files and fails if the code in a `python`-fenced block would be reformatted; it does not edit files.
        No Markdown file contained such a block when this plan was written (see Starting Baseline).
        If the format check fails on a Markdown file, stop and raise it with the human developer, because documents outside the file boundary may not be edited.

#### 4. `README.md` (Modify)

*   **Type / Scope:** Project documentation.
*   **Proposed Changes, Phase 0:**
    *   Setup: replace the `uv venv`, `source .venv/bin/activate`, and `uv pip install -e ".[dev]"` steps with `uv sync --locked --extra dev`.
    *   Testing and formatting: replace the "Running the Test Suite" and "Formatting & Static Analysis" subsections with one subsection, `### Verification`, that runs `./scripts/lint.sh` and states that it runs Ruff lint, the Ruff format check, and pytest.
    *   Prerequisites: state that `uv` is required for the gate; `pip` users can still install `-e ".[dev]"` and run `ruff check .`, `ruff format --check .`, and `pytest` directly.
    *   Project structure: change the test entry to `tests/test_legacy_engine.py  # Legacy tests, to be removed`.
*   **Proposed Changes, Phase 5:**
    *   Status block: state that `src/tome/` implements Spec 1.1.2 and is checked by tests derived from Section 7 of the specification, linking "specification" to `docs/designs/001_tome_core_architecture.md`.
    *   Project structure: list `docs/plans/`, `scripts/lint.sh`, `.python-version`, `uv.lock`, `src/tome/tables.py`, the eight `src/tome/engine/` files, `tests/support.py`, `tests/test_tome_core.py`, and `tests/test_tome_integration.py`; remove the four legacy modules and `tests/test_legacy_engine.py`; change the `src/tome/` comment to "Simulation engine (Spec 1.1.2)"; change the `src/tome/__init__.py` comment to "Package entry point, version, and public API"; keep the existing `docs/designs/`, `docs/reviews/`, `AGENTS.md`, `pyproject.toml`, and `LICENSE` entries.

#### 5. `AGENTS.md` (Modify, Phase 0)

*   **Type / Scope:** Agent conventions.
*   **Proposed Changes:** In Section 3, add a verification bullet: `./scripts/lint.sh` is the green-baseline gate; `uv.lock` is committed and refreshed with `uv lock` when dependencies change; `.python-version` pins Python 3.11 for the golden vectors.

#### 6. `src/tome/engine/errors.py` (Create)

*   **Type / Scope:** Error hierarchy for Spec Section 3.4 `RunError` and Invariant 15.
*   **Proposed Changes:**
    *   `class RunError(Exception)` with class attribute `code: ClassVar[str]`, constructor `__init__(self, message: str)` storing `self.message`, and method `to_failure(self) -> RunFailure` returning `RunFailure(contract_version="1.1.0", code=self.code, message=self.message)`.
    *   Seven subclasses, each setting only `code`:

        | Class | `code` |
        | :--- | :--- |
        | `InvalidRunRequestError` | `INVALID_RUN_REQUEST` |
        | `ProposalGenerationError` | `PROPOSAL_GENERATION_FAILED` |
        | `InvalidProposalError` | `INVALID_PROPOSAL` |
        | `PeerReviewError` | `PEER_REVIEW_FAILED` |
        | `UmpireReviewError` | `UMPIRE_REVIEW_FAILED` |
        | `UmpireResolutionError` | `UMPIRE_RESOLUTION_FAILED` |
        | `MechanicsError` | `MECHANICS_FAILED` |

    *   `errors.py` imports `RunFailure` from `models.py`; `models.py` never imports `errors.py`.
    *   Message text is free-form; only `code` is stable (Spec Section 3.5).

#### 7. `src/tome/engine/text.py` (Create)

*   **Type / Scope:** Spec Section 3.0 normalization; imports no other `tome` module.
*   **Proposed Changes:**
    *   `normalize(value: str) -> str`: apply `str.strip()`; if the result has at least two characters and starts and ends with the same character, and that character is `"` or `'`, remove that one pair; apply `str.strip()` again.
    *   `is_non_whitespace(value: str) -> bool`: `normalize(value) != ""`.
    *   `matches(left: str, right: str) -> bool`: `normalize(left) == normalize(right)`.
    *   `find_match(value: str, candidates: Sequence[str]) -> str | None`: return the first candidate whose normalized form equals `normalize(value)`, in its original text, or `None`.
    *   `has_matching_pair(values: Sequence[str]) -> bool`: whether any two values match.

#### 8. `src/tome/engine/models.py` (Create)

*   **Type / Scope:** Pydantic v2 contract schemas for Spec Sections 3.1 to 3.5.
*   **Proposed Changes:**
    *   `CONTRACT_VERSION: Final = "1.1.0"`.
    *   Base class `ContractModel(BaseModel)` with `model_config = ConfigDict(strict=True, extra="forbid", revalidate_instances="always")`; every model below inherits it.
        `revalidate_instances="always"` subjects nested model instances, including ones built with `model_construct`, to full validation (see Starting Baseline; re-checked by a Phase 1 test).
    *   Reusable types:
        *   `NonWhitespaceStr = Annotated[str, AfterValidator(...)]`, rejecting values for which `text.is_non_whitespace` is false.
        *   `Vote = Annotated[int, Field(ge=-1, le=1)]`.
        *   `TrioTier = Literal["Obvious", "Option", "Odd"]`.
        *   `Outcome = Literal["Success", "Failure"]`.
        *   `ReasonCode = Literal["proposal-succeeded", "failure-consequence", "turn-tick", "round-complete"]`.
        *   `ErrorCode = Literal[...]` with the seven `code` strings from the Target File 6 table, written as literals.
        *   `D66_KEYS: Final = frozenset(10 * tens + units for tens in range(1, 7) for units in range(1, 7))`.
        *   `SparkTable = dict[int, NonWhitespaceStr]`.
    *   Models and fields, matching the specification exactly:

        | Model | Fields and constraints |
        | :--- | :--- |
        | `Actor` | `id: NonWhitespaceStr`, `name: str`, `agenda: str` |
        | `WorldState` | `session_index: int >= 0`, `turn_index: int >= 0`, `canon_facts: list[NonWhitespaceStr]`, `actors: list[Actor]` |
        | `SupportingPro` | `source_type: Literal["canon_fact"]`, `source_ref: str`, `argument: str` |
        | `ProposalDraft` | `world_change_statement: NonWhitespaceStr`, `supporting_pros: list[SupportingPro]` with length 1 to 2 |
        | `Proposal` | `active_actor_id: str`, `posture_roll: int` 1 to 6, `trio_tier: TrioTier`, `spark_tags: list[str]` length exactly 2, `world_change_statement: NonWhitespaceStr`, `supporting_pros: list[SupportingPro]` length 1 to 2 |
        | `PeerEvaluation` | `voter_actor_id: str`, `baseline_plausibility: Vote`, `biased_shift_applied: bool`, `cited_anchor: str \| None`, `final_vote: Vote`, `public_argument: str` |
        | `UmpireRejection` | `voter_actor_id: str`, `reason: NonWhitespaceStr` |
        | `UmpireRejectionRecord` | `voter_actor_id: str`, `reason: NonWhitespaceStr`, `evaluation_before_reversion: PeerEvaluation` |
        | `FailureResolution` | `source_voter_actor_id: str \| None`, `world_change_statement: NonWhitespaceStr`, `rationale: NonWhitespaceStr` |
        | `StateChange` | `path: Literal["/canon_facts", "/session_index", "/turn_index"]`, `before: list[str] \| int`, `after: list[str] \| int`, `reason: ReasonCode` |
        | `TurnRecord` | `turn_index: int >= 1`, `session_index: int >= 0`, `active_actor_id: str`, `proposal: Proposal`, `peer_evaluations: list[PeerEvaluation]`, `umpire_rejections: list[UmpireRejectionRecord]`, `net_vote_modifier: int` -3 to 3, `resolution_roll: int` 2 to 12, `adjusted_total: int` -1 to 15, `outcome: Outcome`, `failure_resolution: FailureResolution \| None`, `state_changes: list[StateChange]` |
        | `SparkTables` | `Action`, `Focus`, `Method`, `Disposition`, `Motivation`, each `SparkTable` |
        | `RunRequest` | `contract_version: Literal["1.1.0"]`, `world_state: WorldState`, `turn_count: int >= 1`, `spark_tables: SparkTables = None`, `first_round_order: list[str] = None`, `seed: int >= 0 = None` |
        | `RunResult` | `contract_version: Literal["1.1.0"]`, `final_world_state: WorldState`, `spark_table_source: Literal["trio-d66-v1", "request"]`, `turn_records: list[TurnRecord]` |
        | `RunFailure` | `contract_version: Literal["1.1.0"]`, `code: ErrorCode`, `message: str` |

    *   The three optional `RunRequest` fields are annotated without `None` and default to `None`.
        Pydantic does not validate defaults, so omitting a field yields `None`, while sending `null` is rejected (see Starting Baseline; re-checked by a Phase 1 test).
        A code comment states this intent.
    *   `SparkTable` before-validator, applied to each of the five fields:
        *   Leave a non-`dict` value unchanged so strict validation rejects it.
        *   If every key has type exactly `str`, require `re.fullmatch(r"[1-6][1-6]", key)` for each key and convert it to `int`.
        *   If every key has type exactly `int`, keep it; `bool` keys fail this test because their type is `bool`.
        *   Raise `ValueError` for mixed or other key types.
        *   Raise `ValueError` unless the key set equals `D66_KEYS`.
    *   `WorldState` after-validator: raise `ValueError` if `text.has_matching_pair(canon_facts)` or if two actor IDs match under normalization.
    *   `RunRequest` after-validator:
        *   Raise `ValueError` if `world_state.actors` is empty.
        *   If `first_round_order` is not `None`, raise `ValueError` unless it has the same length as the actor list, has no repeated entry, and its entries equal the actor IDs as a set, compared exactly without normalization.
    *   `model_dump(mode="json")` serializes `SparkTable` keys as decimal strings (see Starting Baseline; re-checked by a Phase 1 test).

#### 9. `src/tome/engine/mechanics.py` (Create)

*   **Type / Scope:** Deterministic mechanics for Spec Sections 2.1, 2.2, 2.5 and Invariants 2, 7, 8, 14, 16.
*   **Proposed Changes:**
    *   `TABLE_NAMES: Final = ("Action", "Focus", "Method", "Disposition", "Motivation")`, the canonical sampling list from Invariant 14.
    *   `DEFAULT_TABLE_SET_ID: Final = "trio-d66-v1"`.
    *   `default_spark_tables() -> SparkTables`: validate `{"Action": dict(TABLE_ACTION), ..., "Motivation": dict(TABLE_MOTIVATION)}` from `tome.tables`; a `ValidationError` becomes `MechanicsError`.
    *   `tier_for_roll(roll: int) -> TrioTier`: 1 to 3 is `"Obvious"`, 4 to 5 is `"Option"`, 6 is `"Odd"`; any other value raises `MechanicsError`.
    *   `TurnCues`, a frozen dataclass with `posture_roll: int`, `trio_tier: TrioTier`, `table_names: tuple[str, str]`, `d66_keys: tuple[int, int]`, and `spark_tags: tuple[str, str]`.
    *   `first_round_order(rng: random.Random, actor_ids: Sequence[str], supplied: Sequence[str] | None) -> list[str]`: return `list(supplied)` without drawing when supplied; otherwise copy `actor_ids` in `WorldState.actors` order, call `rng.shuffle` on the copy, and return it.
    *   `draw_turn_cues(rng: random.Random, tables: SparkTables) -> TurnCues`, drawing in exactly this order:
        1.  `posture_roll = rng.randint(1, 6)`.
        2.  `table_names = rng.sample(list(TABLE_NAMES), 2)`, keeping sample order.
        3.  For each name in that order: `tens = rng.randint(1, 6)`, then `units = rng.randint(1, 6)`, then `key = 10 * tens + units`.
        4.  For each name and key: `entry = getattr(tables, name)[key]`, and tag `f"{name}:{entry}"`.
    *   `roll_resolution(rng: random.Random) -> tuple[int, int]`: two `rng.randint(1, 6)` calls, returned in draw order; the runner sums them for `resolution_roll`.
    *   `net_vote_modifier(final_votes: Iterable[int]) -> int`: `max(-3, min(3, sum(final_votes)))`.
    *   `resolve_outcome(adjusted_total: int) -> Outcome`: `"Success"` if at least 7, otherwise `"Failure"`.
    *   Every die result is checked to be from 1 to 6, and every table lookup is checked to succeed; a failed check raises `MechanicsError`.
        Checks use explicit `if` statements, not `assert`, so they survive `python -O`.

#### 10. `src/tome/engine/gates.py` (Create)

*   **Type / Scope:** Validation of callback outputs for Spec Sections 2.4, 2.6, and 3.5, and Edge Case 17.
*   **Proposed Changes:**
    *   `_validate_output(raw, model_cls, error_cls)`: if `isinstance(raw, model_cls)`, validate `raw.model_dump()`; if `raw` is a `Mapping`, validate `dict(raw)`; otherwise raise `error_cls`.
        Any `Exception` other than `MemoryError` raised while dumping, converting, or validating becomes `error_cls`, chained with `from`.
        This conversion includes `RecursionError` and `SystemError`, because they are raised while validating callback output; D13 applies only outside `_validate_output`.
    *   `build_proposal(raw, *, active_actor_id: str, cues: TurnCues, canon_facts: Sequence[str]) -> Proposal`, checking in this order:
        1.  Shape: `_validate_output(raw, ProposalDraft, ProposalGenerationError)`.
        2.  Novelty: if `text.find_match(statement, canon_facts)` is not `None`, raise `InvalidProposalError`.
        3.  Grounding: keep the pros whose `source_ref` matches a canon fact, in their original order and original text; if none remain, raise `InvalidProposalError`.
        4.  Construction: build `Proposal` from `active_actor_id`, `cues.posture_roll`, `cues.trio_tier`, `list(cues.spark_tags)`, the original statement, and the kept pros.
    *   `validate_peer_evaluation(raw, *, voter_actor_id: str, canon_facts: Sequence[str]) -> PeerEvaluation`, returning the mechanically validated evaluation:
        1.  Shape: `evaluation = _validate_output(raw, PeerEvaluation, PeerReviewError)`.
        2.  If `evaluation.voter_actor_id != voter_actor_id`, compared exactly, raise `PeerReviewError`.
        3.  `shift = final_vote - baseline_plausibility`.
        4.  If `shift == 0`: set `biased_shift_applied` (the flag) to `False` and `cited_anchor` (the anchor) to `None`.
        5.  If `abs(shift) > 1`: revert the vote to baseline, with the flag `False` and the anchor `None`.
        6.  Otherwise: `match = text.find_match(cited_anchor, canon_facts)` when the anchor is not `None`.
            Without a match, revert as in step 5.
            With a match, set the flag to `True` and the anchor to `match`.
        7.  Leave `baseline_plausibility` and `public_argument` unchanged, and ignore the adapter's submitted flag.
    *   `apply_umpire_rejections(raw, *, evaluations: list[PeerEvaluation]) -> tuple[list[PeerEvaluation], list[UmpireRejectionRecord]]`:
        1.  If `raw` is not a `list`, raise `UmpireReviewError`.
        2.  Validate each element with `_validate_output(element, UmpireRejection, UmpireReviewError)`.
        3.  Raise `UmpireReviewError` if any `voter_actor_id` is repeated, matches no evaluation exactly, or names an evaluation whose `final_vote` equals its `baseline_plausibility`.
        4.  For each evaluation in peer order that was rejected: record `UmpireRejectionRecord(voter_actor_id=…, reason=…, evaluation_before_reversion=evaluation.model_copy(deep=True))`, using the rejection's `voter_actor_id` and `reason`, then revert `final_vote` to baseline, set the flag to `False`, and set the anchor to `None`.
        5.  Return new evaluation objects and the records in peer-evaluation order, regardless of the callback's return order.
    *   `lowest_vote_candidates(evaluations: list[PeerEvaluation]) -> list[str]`: the `voter_actor_id` of every evaluation whose `final_vote` equals the minimum, in peer order, or `[]` when there are no evaluations.
    *   `validate_failure_resolution(raw, *, candidate_voter_ids: list[str], canon_facts: Sequence[str], rejected_statement: str) -> FailureResolution`:
        1.  Shape: `_validate_output(raw, FailureResolution, UmpireResolutionError)`.
        2.  If `source_voter_actor_id` is not `None` and is not exactly in `candidate_voter_ids`, raise `UmpireResolutionError`; when there are no peers, the candidate list is empty, so any non-null source fails.
        3.  If the statement matches a canon fact or `rejected_statement`, raise `UmpireResolutionError`.

#### 11. `src/tome/engine/protocols.py` (Create)

*   **Type / Scope:** `typing.Protocol` callback types for Spec Section 3.5.
*   **Proposed Changes:** Four protocols with positional-only `__call__` parameters in the specified order:
    *   `ProposalGenerator(active_actor: Actor, trio_tier: TrioTier, spark_tags: list[str], world_state: WorldState, /) -> ProposalDraft | Mapping[str, Any]`.
    *   `PeerReviewer(voter_actor: Actor, proposal: Proposal, world_state: WorldState, /) -> PeerEvaluation | Mapping[str, Any]`.
    *   `UmpireReview(turn_index: int, proposal: Proposal, peer_evaluations: list[PeerEvaluation], world_state: WorldState, /) -> list[UmpireRejection | Mapping[str, Any]]`.
    *   `FailureResolver(turn_index: int, proposal: Proposal, peer_evaluations: list[PeerEvaluation], candidate_voter_ids: list[str], adjusted_total: int, world_state: WorldState, /) -> FailureResolution | Mapping[str, Any]`.

#### 12. `src/tome/engine/runner.py` (Create)

*   **Type / Scope:** The `run` entry point for Spec Sections 3.5 and 5.
*   **Proposed Changes:** `run(request, proposal_generator, peer_reviewer, failure_resolver, umpire_review=None) -> RunResult`, in this order:
    1.  **Callables:** if any of `proposal_generator`, `peer_reviewer`, or `failure_resolver` is `None` or not callable, or `umpire_review` is neither `None` nor callable, raise `InvalidRunRequestError`.
    2.  **Request:** convert a `Mapping` with `dict(request)` or an object for which `isinstance(request, RunRequest)` holds with `request.model_dump(exclude_none=True)`, then call `RunRequest.model_validate(...)`; any other type raises `InvalidRunRequestError`.
        Any `Exception` other than `MemoryError` raised during conversion or validation becomes `InvalidRunRequestError`, chained with `from`.
        Steps 1 and 2 invoke no callable and construct no `random.Random`.
    3.  **Tables:** set `tables` and `source` to `request.spark_tables` and `"request"`, or to `default_spark_tables()` and `"trio-d66-v1"`.
    4.  **Random generator:** `rng = random.Random(request.seed)` when a seed is supplied, otherwise `random.Random()`, which seeds from system entropy.
    5.  **Order:** `order = first_round_order(rng, actor ids in WorldState.actors order, request.first_round_order)`.
    6.  **Working state:** `state = request.world_state.model_copy(deep=True)`.
        Start with `records = []`.
    7.  For each offset `i` from `0` to `request.turn_count - 1`, with `active_id = order[i % len(order)]` and `turn_number = state.turn_index + 1`:
        1.  `cues = draw_turn_cues(rng, tables)`.
        2.  Invoke `proposal_generator(actor snapshot, cues.trio_tier, list(cues.spark_tags), state snapshot)` under D12 with `ProposalGenerationError`, then `build_proposal`.
        3.  For each non-active actor in `state.actors` order: invoke `peer_reviewer(voter snapshot, proposal snapshot, state snapshot)` under D12 with `PeerReviewError`, then `validate_peer_evaluation`.
            Collect the results, in that order, as `evaluations`.
        4.  If `umpire_review` is not `None` and any evaluation's `final_vote` differs from its baseline: invoke `umpire_review(turn_number, proposal snapshot, evaluation snapshots, state snapshot)` once under D12 with `UmpireReviewError`, then `evaluations, umpire_rejections = apply_umpire_rejections(raw, evaluations=evaluations)`.
            Otherwise, `umpire_rejections` is `[]`.
        5.  `modifier = net_vote_modifier(final votes)`, `first_die, second_die = roll_resolution(rng)`, `roll = first_die + second_die`, `total = roll + modifier`, `outcome = resolve_outcome(total)`.
        6.  On Success: the new fact is the proposal statement, the canon reason is `"proposal-succeeded"`, and `failure_resolution` is `None`.
        7.  On Failure: `candidates = lowest_vote_candidates(evaluations)`; invoke `failure_resolver(turn_number, proposal snapshot, evaluation snapshots, list(candidates), total, state snapshot)` under D12 with `UmpireResolutionError`, then `validate_failure_resolution`.
            The new fact is the resolution statement, and the canon reason is `"failure-consequence"`.
        8.  Record `before` values, append the new fact to `state.canon_facts`, and increment `state.turn_index`.
            If `(i + 1) % len(order) == 0`, increment `state.session_index`.
        9.  Build `state_changes` sorted by path: `/canon_facts` with the canon reason, `/session_index` with `"round-complete"` only when it changed, and `/turn_index` with `"turn-tick"`.
            `before` and `after` are complete copies of each field.
        10. Append a `TurnRecord` built from the values above; its `turn_index` and `session_index` are read from `state` after sub-step 8 of step 7.
    8.  Return `RunResult(contract_version="1.1.0", final_world_state=state, spark_table_source=source, turn_records=records)`.
    *   **Callback wrapping:** for each callback invocation in step 7, build all snapshot and list arguments first; the D12 `try` wraps only the callable invocation expression, and the gate function named after "then" is called after and outside that `try`.
    *   **Imports:** import `draw_turn_cues`, `roll_resolution`, and the other mechanics and gate functions by name, so tests can replace them through `tome.engine.runner`.
        `runner.py` uses `import random` and calls `random.Random`.
    *   **Snapshots:** every model argument is a fresh `model_copy(deep=True)`; every list argument is a new list, and a list of models holds a fresh `model_copy(deep=True)` of each element, made for that call.
    *   **Invariant checks:** after each turn, raise `MechanicsError` unless the canon grew by exactly one entry and `turn_index` grew by exactly one.
        Before returning, raise `MechanicsError` unless the record count equals `turn_count`.
    *   **Error handling:** steps 3 to 8 run inside one `try` block whose handlers are, in order: `except (RunError, MemoryError, RecursionError, SystemError): raise`, then `except Exception as exc: raise MechanicsError(...) from exc`.
        No handler catches `BaseException`, so exceptions that are not `Exception` subclasses propagate unchanged (D12, D13).
        Any `RunError` propagates without a result, and the caller's input is never mutated.

#### 13. `src/tome/engine/__init__.py` (Create)

*   **Type / Scope:** Package entry point.
*   **Proposed Changes:**
    *   Phase 1: a module docstring only.
    *   Phase 4: import and list in `__all__`: `run`; `CONTRACT_VERSION` and `DEFAULT_TABLE_SET_ID`; the 15 models in the Target File 8 table (`ContractModel` is not exported); `RunError` and its seven subclasses; and the four protocols.
    *   Use explicit `from tome.engine.<module> import <name>` statements and a literal `__all__` list.
        Do not use star imports, which hide the export list, or a computed `__all__`, which Ruff reports as F401.

#### 14. `src/tome/__init__.py` (Modify, Phase 4)

*   **Type / Scope:** Top-level package.
*   **Proposed Changes:** Keep the docstring and `__version__ = "0.1.0"`.
    Re-export every name in `tome.engine.__all__` with one explicit `from tome.engine import ...` statement naming each public name, and set a literal `__all__` list containing those names and `__version__`.
    Do not use star imports, which hide the export list, or a computed `__all__`, which Ruff reports as F401.
    The legacy submodules remain importable by their module paths until Phase 5.

#### 15. `tests/support.py` (Create)

*   **Type / Scope:** Plain test helper module; no pytest fixtures (D7).
*   **Proposed Changes:**
    *   (Phase 1) `make_world(actor_ids=("actor_a", "actor_b"), canon=("Fact 1.",), session_index=0, turn_index=0) -> dict`, naming the actors by list position: the first is `Actor A` with agenda `Agenda A`, the second `Actor B` with agenda `Agenda B`, and so on, whatever their IDs.
    *   (Phase 1) `make_request(world=None, turn_count=1, **optional) -> dict`, with `contract_version` `"1.1.0"`.
    *   (Phase 1) `override_tables(overrides: dict[tuple[str, int], str] | None = None) -> dict`: every entry is `f"{name} {key}"` with decimal-string keys, except the overridden entries.
    *   (Phase 1) `INVALID_REQUEST_CASES`: a list of `(case_id, mutator)` pairs, where each mutator edits a fresh `make_request()` dict to produce one Edge Case 5 or Section 3.4 request violation.
        Cases: `turn_count` of `0`, `-1`, and `True`; `seed` of `-1`, `True`, and `None`; `spark_tables` of `None`; `first_round_order` of `None`; empty actor list; actor ID `"  "`; actor ID `'""'`; actor IDs `"a"` and `" a "`; canon fact `"  "`; canon facts `"Fact"` and `'"Fact"'`; `contract_version` of `"1.0.0"`; an undeclared top-level field; an undeclared world-state field `active_rumors`; an undeclared actor field `traits`; `first_round_order` missing an actor, repeating an actor, naming an unknown actor, containing `"actor_a "`, or supplied as a tuple.
    *   (Phase 4) `ScriptedCallbacks(proposal=None, peer=None, umpire=None, failure=None)`: each argument is an optional function with the matching protocol signature that replaces the default.
        It exposes the bound methods `proposal_generator`, `peer_reviewer`, `umpire_review`, and `failure_resolver`, which tests pass to `run`.
        Each method appends a tuple of the positional arguments it received to `proposal_calls`, `peer_calls`, `umpire_calls`, or `failure_calls`, then returns the function's result or the default.
        Defaults:
        *   Proposal: statement `f"{active_actor.name} achieves outcome {world_state.turn_index + 1}."`, with one supporting pro citing `world_state.canon_facts[0]` with argument `"Scripted supporting argument."`.
        *   Peer: `voter_actor_id` `voter_actor.id`, `baseline_plausibility` 0, `final_vote` 0, flag `False`, anchor `None`, argument `f"{voter_actor.name} is uncertain."`.
        *   Umpire review: `[]`.
        *   Failure: source `candidate_voter_ids[0]`, or `None` when empty; statement `f"Consequence {turn_index}."`, where `turn_index` is the callback's first parameter, equal to `world_state.turn_index + 1`; rationale `"Scripted test decision."`.
    *   (Phase 4) `seed_for_base_roll(target: int) -> int`: the smallest seed from 0 to 9,999 for which a one-turn run with a supplied order produces `resolution_roll` equal to `target`.
        It replicates Invariant 14 with `random.Random` directly, not with engine code, so it acts as an independent oracle: one `randint` for posture, one `sample`, four `randint` for d66, then two `randint` for resolution.
        If no seed matches, it raises `AssertionError` naming the target.

#### 16. `tests/test_tome_core.py` (Create)

*   **Type / Scope:** Section 7 unit tests; contents are listed in the traceability table below.

#### 17. `tests/test_tome_integration.py` (Create)

*   **Type / Scope:** Section 7 integration tests; contents are listed in the traceability table below.
*   **Proposed Changes:** The worked-example test builds the Section 3.4 request with `override_tables({("Focus", 66): "Resource access", ("Method", 13): "Public declaration"})`, seed 20, and order `["actor_a", "actor_b"]`.
    It scripts the proposal, peer evaluation, and failure resolution shown in the specification.
    It asserts that `run(...).model_dump(mode="json")` equals the specification's result JSON, written as a Python literal in the test.

### Test Plan and Section 7 Traceability

Every row maps a requirement to at least one named test; every Spec Section 7 bullet appears in at least one row.
Unit tests live in `tests/test_tome_core.py`, and integration tests in `tests/test_tome_integration.py`.

| Requirement (Spec Section 7 bullet, invariant, or plan decision) | Test functions and required assertions | Phase |
| :--- | :--- | :---: |
| Normalization | `test_normalization_vectors`: `'  "Fact"  '` and `"'Fact'"` match `"Fact"`; `'""'` and `"  "` are blank; typographic quotes do not match; `'""Fact""'` loses one pair; case is preserved. | 1 |
| Request Validation | `test_run_request_model_rejects_invalid_values`, parametrized over `INVALID_REQUEST_CASES`, raising `pydantic.ValidationError`; this checks on the locked Pydantic version that a `bool` for an integer, an explicit `null` for an optional field, and a tuple for a list are rejected, re-checking the explicit-`null` behaviour recorded in Starting Baseline. `test_nested_model_instances_revalidated`: a `WorldState` built with `model_construct` holding a blank canon fact, nested in a request mapping, is rejected. | 1 |
| Closed State Schema | `test_closed_schemas_reject_unknown_fields` at world-state and actor level. | 1 |
| Deferred and Removed Fields | `test_removed_fields_rejected`: actor `traits`, `posture`, `exhausted_traits`; world-state `active_rumors`; peer `goal_alignment`. | 1 |
| Spark Table Defaults and Overrides (validation) | `test_spark_tables_validation`: string keys and integer keys accepted; mixed keys, `bool` keys, keys `"17"`, `"011"`, and `"11\n"`, 35 keys, a missing table, an extra table, a `null` table, and blank or non-string entries rejected; `SparkTables.model_dump(mode="json")` serializes every table's keys as decimal strings `"11"` to `"66"`. | 1 |
| Invariant 15 (Explicit Failure Types) | `test_error_codes_and_failure_payload`: each class's `code`, and `to_failure()` fields. | 1 |
| Posture Die to TriO Tier Mapping | `test_tier_mapping_exhaustive` for faces 1 to 6; faces 0 and 7 raise `MechanicsError`. | 2 |
| Seeded Random Sequence | `test_golden_vector_seed_42` and `test_golden_vector_unsorted_seed_4` with the exact Invariant 14 values, including resolution dice (6, 6) for seed 42 and (4, 5) for seed 4; `test_draw_sequence_matches_reference` against a direct `random.Random` reference for seeds 0 to 199. | 2 |
| Seeded Random Sequence (table independence) | `test_draws_ignore_table_contents_and_key_order`: defaults, an override, and the same override with the five table names in reverse order and each table's d66 keys in reverse order give identical posture rolls, table names, and keys. | 2 |
| Narrative Spark Selection | `test_all_table_pairs_eligible_for_every_tier`: within seeds 0 to 4,999, all 30 combinations of tier and unordered table pair occur, and the two names always differ. `test_tables_reusable_across_turns`. | 2 |
| Net Modifier Clamping | `test_net_modifier_clamps` for vote sums from -6 to 6. | 2 |
| Binary Resolution (arithmetic) | `test_outcome_boundaries`: totals -1 and 6 fail; 7 and 15 succeed. | 2 |
| D8 (default table identity) | `test_default_tables_are_trio_d66_v1`: `default_spark_tables()` equals the five `tome.tables` mappings exactly. | 2 |
| Non-Blank Proposals; Proposal and Evaluation Schemas; Error Classification | `test_proposal_shape_errors`, parametrized: non-mapping return, missing field, extra field such as `active_actor_id`, blank statement, `'""'` statement, source type `"actor_trait"`, zero pros, three pros, and a tuple of pros raise `ProposalGenerationError`. | 3 |
| New Proposals | `test_proposal_duplicating_canon_rejected`, including padded and quoted variants, raising `InvalidProposalError`; a duplicate statement with three pros raises `ProposalGenerationError`, because shape is checked first. | 3 |
| Grounding Gate Verification | `test_proposal_pruning_and_attachment`; `test_proposal_without_grounded_pros_rejected`; `test_sparks_and_actor_metadata_do_not_ground`; `test_canon_fact_reusable_across_turns`. | 3 |
| Historical Canon Grounding | `test_historical_canon_grounding`: both capability statements remain citable and neither is removed; proposal and failure-consequence novelty checks cover the entire canon history; a shift citing "Actor A has capability X" is kept by `validate_peer_evaluation` and can still be rejected by `apply_umpire_rejections`. | 3 |
| Linter Gate Shift Bounds | `test_two_step_shift_reverts`; `test_votes_stay_in_range`. | 3 |
| Voting Metadata | `test_shift_metadata_follows_numeric_shift`: an inconsistent adapter flag is ignored; the anchor `'  "Fact 1."  '` is stored as `"Fact 1."`; a missing or invented anchor reverts; an unchanged vote clears the anchor. | 3 |
| Exact Actor-ID References | `test_peer_voter_id_compared_exactly`: `'"actor_b"'` raises `PeerReviewError`. The `first_round_order` case is covered by the request-validation tests. | 3 |
| Error Classification (peer) | `test_peer_shape_errors`: missing `biased_shift_applied`, extra `goal_alignment`, a `bool` vote, `final_vote` of 2, and a non-mapping return raise `PeerReviewError`. | 3 |
| Umpire Rejection; Umpire Audit and Errors | `test_umpire_rejection_reverts_and_records`, using the Section 7 vector of baseline 1, final 0, adapter flag `False`, and anchor `'  "Fact 1."  '`; and the upward vector of baseline -1, final 0, and anchor `"Fact 1."`, which reverts to -1; `test_umpire_records_in_peer_order`; `test_umpire_rejection_errors`: duplicate, unknown, or active-actor voter IDs, a vote at baseline, a blank reason, an extra field, and a non-list return raise `UmpireReviewError`. | 3 |
| Lowest-Vote Failure Candidates | `test_lowest_vote_candidates`: tied, all neutral, all positive, single, and empty. | 3 |
| New Failure State; Failure Resolver Errors | `test_failure_resolution_validation`: a direct-use decision whose statement equals the source peer's `public_argument`, a restated decision, and a null-source decision are accepted and stored verbatim; a non-lowest or unknown source, a non-null source with no peers, blank fields, a statement matching canon or the rejected proposal, an extra field, and a `None` return (the missing decision) raise `UmpireResolutionError`. | 3 |
| Required Callables | `test_required_callables_checked_first`: each required callable as `None` or a non-callable value raises `InvalidRunRequestError` with no invocation and no `random.Random` constructed, checked by `monkeypatch.setattr(tome.engine.runner.random, "Random", spy)`; as a positive control, a valid run calls the spy exactly once; `umpire_review=None` is accepted; `umpire_review="x"` is rejected. | 4 |
| Request Validation (through `run`) | `test_run_rejects_invalid_request_before_callbacks`, parametrized over `INVALID_REQUEST_CASES`: `InvalidRunRequestError`, no callback calls, no `random.Random` constructed, and an unchanged input dict. `test_run_accepts_mapping_and_model`: a `dict`, a `MappingProxyType`, and a `RunRequest` instance give identical results. `test_run_rejects_non_mapping_request`: a JSON string, a `list`, and `None` as `request` each raise `InvalidRunRequestError` with no callback calls. | 4 |
| Spark Table Defaults and Overrides (run) | `test_spark_table_source_and_tags`: an omitted field gives `"trio-d66-v1"` with default-table tags; an override gives `"request"` with override tags; with the same seed and supplied order, a default-table run and an override run give identical `posture_roll`, table-name prefixes of `spark_tags`, and `resolution_roll`. | 4 |
| Narrative Spark Selection (run) | `test_generator_receives_tier_and_both_tags`. | 4 |
| Proposal and Evaluation Schemas (run) | `test_one_ordered_evaluation_per_peer`; `test_new_proposal_rejected_before_peers_and_dice`, with no peer calls and no call to `tome.engine.runner.roll_resolution`, replaced with a spy. | 4 |
| Optional Pre-Roll Callback | `test_umpire_review_invocation_rules`: absent; not called when no shift remains; called once per eligible turn with all evaluations; `[]` leaves shifts unchanged; rejections change the modifier. | 4 |
| Umpire Audit and Errors (run) | `test_umpire_error_aborts_without_result`, with unchanged input. `test_umpire_review_receives_validated_evaluation`: the Section 7 vector run through `run` with `ScriptedCallbacks`; `umpire_calls[0][2][0]` has `biased_shift_applied` `True` and `cited_anchor` `"Fact 1."`, and equals the turn record's `evaluation_before_reversion`. | 4 |
| Binary Resolution (run) | `test_success_appends_proposal` and `test_failure_appends_consequence`, using `seed_for_base_roll`; `test_every_turn_adds_exactly_one_fact`. | 4 |
| Lowest-Vote Failure Candidates; Umpire Failure Resolution | `test_failure_resolver_called_on_every_failure`: called with a unique candidate; the arguments are `turn_number`, candidates in peer order, and the adjusted total; tied candidates use the umpire's chosen source; a pre-roll rejection changes the candidate set; after a restated consequence, `peer_evaluations` keeps the source peer's original `public_argument`, `failure_resolution.source_voter_actor_id` names that peer, and canon receives only the restated statement. | 4 |
| Failure Resolver Errors (run) | `test_one_actor_failure_requires_null_source`; `test_invalid_failure_decision_aborts`. | 4 |
| State-Change Records | `test_state_change_records`: one entry per changed field, ascending path order, complete before and after values, exact reason codes, and `round-complete` on round-ending turns. | 4 |
| Narrative State Preservation | `test_actors_unchanged_and_only_consequence_enters_canon`. | 4 |
| Callback boundary (D10 to D12) | `test_callback_exceptions_wrapped`: `ValueError` from each callback becomes its error; `MemoryError` and `KeyboardInterrupt` propagate; an `InvalidProposalError` raised by `peer_reviewer` becomes `PeerReviewError`; a callback's `RecursionError` and `SystemError` each become that callback's error type, with the original as `__cause__`. `test_callback_cancellation`: `concurrent.futures.CancelledError` from `umpire_review` raises `UmpireReviewError`, and from `failure_resolver` raises `UmpireResolutionError`; `asyncio.CancelledError` propagates. `test_callbacks_receive_isolated_snapshots`: callbacks that append to `world_state.canon_facts`, rename an actor, append to `proposal.supporting_pros`, set `peer_evaluations[0].final_vote`, and append to `spark_tags` and `candidate_voter_ids` leave the result identical to an unmutated run. `test_model_instance_returns_accepted`. | 4 |
| D13 (engine-internal exceptions) | `test_engine_internal_exceptions`: replacing `tome.engine.runner.draw_turn_cues` with a function raising `ValueError` gives `MechanicsError`; raising `RecursionError` or `SystemError` propagates unchanged. | 4 |
| D3 (public API) | `test_public_api_exports`: `tome.engine.__all__` contains exactly the names listed in Target File 13; `set(tome.__all__) == set(tome.engine.__all__) \| {"__version__"}`; and `tome.run is tome.engine.runner.run`. | 4 |
| Invariant 15 (Explicit Failure Types, run) | `test_run_error_exposes_failure_code`. | 4 |
| Integration: worked example | `test_worked_example_reproduces_spec_result`. | 4 |
| Integration: exact counts, cycling, seeded order, records, counters, partial rounds, final state | `test_end_to_end_cycling_and_counters`, with three actors and five turns: one completed round, `turn_index` +5, and the order repeated; each record's `turn_index` and `session_index` equal the state after that turn, so the third record shows the incremented `session_index` and the fourth and fifth records keep it; `test_seeded_order_matches_golden_vector`. | 4 |
| Integration: rejection changes outcome, not dice | `test_rejection_changes_outcome_not_dice`. | 4 |
| Integration: next actor sees failure consequence | `test_next_actor_sees_failure_consequence`. | 4 |
| Integration: partial round exports last consequence | `test_partial_round_exports_last_consequence`. | 4 |
| Integration: run-wide atomicity | `test_invalid_decision_after_resolved_turn_is_atomic`: with a two-actor supplied order, `tome.engine.runner.roll_resolution` is replaced with a function returning `(4, 4)` then `(1, 1)`, so turn 1 succeeds and turn 2 fails; the failure resolver returns an invalid decision on turn 2, and `run` raises `UmpireResolutionError` with no result and an unchanged input. | 4 |
| Integration: input unchanged | `test_input_unchanged_on_success_and_failure`; `test_seeded_runs_are_reproducible`. | 4 |

### Verification Plan

*   **Specification gate:** Phase 1 step 0.
*   **Build and environment:** `uv sync --locked --extra dev` succeeds on Python 3.11 after every phase.
*   **Unit tests, integration tests, and lint:** `./scripts/lint.sh` exits 0 at the end of every phase; it runs the Ruff lint and format checks with the existing `pyproject.toml` configuration.
*   **Coverage requirement:** Every row of the traceability table has at least one passing test (D15).
*   **Contract preservation:** `git diff --exit-code 7d3fef1 -- src/tome/tables.py docs/designs/001_tome_core_architecture.md pyproject.toml` exits 0 after every phase.
*   **File boundary:** after every phase, `git diff --name-status 7d3fef1` lists only files from the file-boundary table and the plan and review records named in the File Boundary exception.
*   **Whitespace:** `git diff --check 7d3fef1` exits 0 after every phase.
*   **Legacy removal:** the Phase 5 `git grep` returns no matches.

### Explicitly Out of Scope

*   Any change to the specification, the interface contract, or the `trio-d66-v1` mappings.
*   A UI, execution bridge, persistence, provider adapter, or LLM integration.
*   CI workflows, packaging or publishing, and version bumps beyond `0.1.0`.
*   Effective-seed output, table-digest pinning, compact audit records, resumable rounds, and engine-owned peer metadata, which the specification defers or declines.
*   Engine-enforced resource quotas (Spec Section 2.8 assigns budgeting to the caller).

### Amendment A1: Post-Review Simplifications (2026-11-23)

The human developer approved these changes on 2026-11-23 after the zero-context review of PR #12 (trace `pr-12-2f571609`).
For every draw that `random.Random` can produce, none changes the result or error type of `run()`; where they conflict with the text above, this amendment wins.

*   **Runner (Target File 12):** step 4 always calls `random.Random(request.seed)`, which seeds from system entropy when the seed is `None`.
    The four callback invocations share one `_invoke` helper that applies D12.
    The two post-condition invariant checks are removed, because they cannot fail by construction.
*   **Mechanics (Target File 9):** only `tier_for_roll` checks the d6 range, and `draw_turn_cues` samples from the `TABLE_NAMES` tuple directly.
    `draw_turn_cues`, `roll_resolution`, and `default_spark_tables` no longer catch errors, so a table-lookup or built-in-table defect reaches the D13 handler in `run()` and still raises `MechanicsError`.
    Resolution dice are bounded only through `TurnRecord.resolution_roll` (2 to 12), so an impossible pair such as `(0, 7)` is no longer detected; `random.Random.randint(1, 6)` cannot produce one.
*   **Gates (Target File 10):** `apply_umpire_rejections` copies only rejected evaluations; the rejection record relies on model revalidation for its independent copy.
*   **Models and errors (Target Files 6 and 8):** the first-round-order check compares sorted lists, and `RunError.to_failure` uses `CONTRACT_VERSION`.
*   **Public API (Target Files 13 and 14):** `TrioTier` is exported, because it appears in the `ProposalGenerator` signature.
    `run`, `PeerEvaluation`, and the four protocols gain short docstrings.
*   **Documentation (Target Files 4 and 5):** the README project structure lists top-level directories only and states that a failed run raises `RunError`; `AGENTS.md` points to the README's execution contract instead of repeating it.
*   **Tests:** `test_net_modifier_clamps` covers the vote sums -6, -4, -3, 0, 3, 4, and 6.
    `test_run_reports_mechanics_defects` replaces the direct mechanics checks with table-entry and built-in-table defects raised through `run()`; `test_tier_mapping_rejects_invalid_faces` still covers the d6 range check.
    `test_seeded_runs_are_reproducible` runs with seeds 0 and 42 and asserts that turn draws vary within one run (issue #9).
    `test_umpire_records_in_peer_order` no longer requires unrejected evaluations to be copied.

### Amendment A2: Delivery and Process Deviations (2026-11-23)

This amendment records every remaining deviation from the plan as approved on 2026-11-18, for the human developer's final review before merge.
Items 1 to 5 and 7 change no engine behaviour; item 6 records where A1 departs from the specification's wording.

1.  **Branch and commit identities (D17, Starting Baseline, Verification Plan):** the work was done on `feat/trio-engine-1.1` as D17 requires.
    PR #5 had already squash-merged that branch's earlier commits into `main` as `7c71a29`, so on 2026-11-23 the 13 later commits were rebased, with identical trees, onto `main` as `feat/spec-1.1.2-engine` for PR #12.
    Commit identifiers in this plan refer to the original branch; their PR #12 equivalents are below, and a squash merge will leave neither on `main`.

    | Original (`feat/trio-engine-1.1`) | PR #12 (`feat/spec-1.1.2-engine`) | Commit |
    | :--- | :--- | :--- |
    | `3d03f61` | `58d6a87` | Consolidated EGM architecture review |
    | `7d3fef1` | `32a4813` | Spec 1.1.2 approval; the baseline for every Verification Plan check |
    | `7133460` | `dd5ded2` | This plan |
    | `49eed13` to `ff5241a` | `77245d3` to `2f57160` | Phases 0 to 5 |

2.  **Specification gate (Phase 1 step 0, Verification Plan):** no commit records a run of `validate_egm.py`.
    The validator was removed from the shared tooling on 2026-11-17, when EGM moved to an upstream plugin that ships no equivalent, so the gate cannot be re-run.
    The specification is byte-identical to its approved state: `git diff --exit-code 32a4813 -- docs/designs/001_tome_core_architecture.md` exits 0.
3.  **File Boundary exception:** Amendments A1 and A2 were added, and EGM review records were edited, outside the EGM review workflow, at the human developer's direction on 2026-11-23.
    The record edits are editorial only: six machine-specific paths became plugin-relative, two of them in `comprehension_report.md` and `zoom_out_report.md`, which lie outside the exception's `implementation_readiness/` directory, and ten headings gained their missing blank line.
    No finding, verdict, or round outcome changed.
4.  **Test-first cycle (Phases and Checkpoints):** the Phase 4 green commit `1f3032e` renamed the parameter of `test_run_rejects_non_mapping_request` from `request` to `value`, because pytest reserves `request` and the red commit could not reveal this while collection failed.
    No other green commit changed a test.
5.  **Tests beyond the traceability table:** six tests are not named in the table: `test_world_strict_python_values`, `test_optional_defaults_and_verbatim_text`, `test_request_conversion_exception_boundaries`, `test_callback_output_conversion_exception_boundaries`, `test_callback_model_shapes_revalidated`, and `test_callback_wrapping_excludes_snapshot_preparation_and_gates`.
    `test_tier_mapping_rejects_invalid_faces` holds the faces 0 and 7 assertions that the table assigns to `test_tier_mapping_exhaustive`, and also rejects `True` and `1.0`.
6.  **Relationship to the specification:** besides D12, A1 narrows how Invariant 15 is detected.
    Invariant 15 describes `MechanicsError` as signalling a die result, table lookup, or counter outside its defined range.
    After A1, the posture die and every table lookup are still checked, counters stay bounded by `WorldState` and `TurnRecord` validation, and the two resolution dice are bounded only through their sum.
    The specification text is unchanged; issue #13 tracks aligning it with D12 and with this narrowing.
7.  **EGM working records removed:** at the human developer's direction on 2026-11-23, and outside the EGM review workflow, 22 intermediate records were removed from `docs/reviews/001_tome_core_architecture_egm/`.
    They are the critic, comprehension, zoom-out, and intermediate zoom-out reports, and the 18 round reports under `review_loop/round_*/` and `implementation_readiness/round_*/`.
    The five summary records that the specification and this plan link to are kept: `001_tome_core_architecture_review.md`, `consolidated_review_report.md`, `goldfish_review_report.md`, `review_loop/review_loop_report.md`, and `implementation_readiness/implementation_readiness_report.md`.
    Their 49 links to removed records now point to permanent GitHub links at commit `88df7b6`, which stays reachable through PR #12 after a squash merge.
    `AGENTS.md` now states this as the convention for future EGM records.

At the PR #12 head, the Verification Plan checks against `32a4813` pass: contract preservation exits 0, `git diff --check` exits 0, the Phase 5 legacy-import search finds nothing, and the file-boundary listing shows only the table's files, this plan, and the record changes described in items 3 and 7.

--------------------------------------------------------------------------------

*Drafted with EGM*
