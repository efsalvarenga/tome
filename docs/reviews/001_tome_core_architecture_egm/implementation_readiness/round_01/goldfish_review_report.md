# Goldfish Annotated Review Report: Stage 9 Round 1

**Status:** resolved
**Date:** 2026-11-17
**Target:** [Implementation plan](../../../../plans/001_tome_core_architecture_plan.md), Detailed Implementation Plan, lines 15-475
**Reviewed SHA-256:** `677122edc137a7e1f642f3899a265610b3f0a33614273919ad0b2ef3c4d1a8ef`
**Post-resolution SHA-256:** `6c28bf0617aabdd989d4de1e3ef237e9bf474aa0bdbbf50f9256b7241713631b`
**Raw findings:** [Complete round-one reviewer reports](reviewer_report.md)
**Loop state:** [Stage 9 report](../implementation_readiness_report.md)

## Round Decision Before Edits

All three requested reviewers completed.
They reported 30 findings: 0 Blocker, 15 Major, and 15 Nit.
Round 1 is **not clean** because it contains unsettled Major findings.
Consecutive clean rounds: **0 of 2**.

All 30 findings are classified PROPOSE FIX, and every original severity is unchanged.
No finding is contested, escalated, or declined.
No finding reopens a settled decision: D1 to D4 and D12 stand, and the findings that touch D12 concern its precision and tests, not its direction.
Overlapping findings share one of 20 edit groups, so each change is applied once.

The coordinator verified the following reviewer claims with probes on Python 3.11 and Pydantic 2.14.3 before classifying them:

*   A nested instance created with `model_construct` passes validation under the default settings; `revalidate_instances="always"` rejects an invalid nested instance and accepts a valid one.
*   Strict-mode `model_validate` rejects a non-`dict` `Mapping` at the top level.
*   `re.match(r"^[1-6][1-6]$", "11\n")` succeeds; `re.fullmatch(r"[1-6][1-6]", "11\n")` fails.
*   `concurrent.futures.CancelledError` is an `Exception` subclass; `asyncio.CancelledError` is not.
*   A computed `__all__` triggers Ruff F401; literal imports with a literal `__all__` pass.
    A star import also passed this probe, so the claim that it triggers F403 under the repository's settings is not confirmed; the literal form is still required, because it is the only form both reviewers accept and it keeps the export list explicit.

## Findings by Severity

Each finding below maps to one edit group in the next section.

### Major

| Finding | Scope | Summary | Suggestion | Edit |
| :--- | :--- | :--- | :--- | :--- |
| `implementation_readiness-1-1` | D13, runner error handling | `except` scope could turn `KeyboardInterrupt` or `SystemExit` into `MechanicsError`. | PROPOSE FIX | [E01](#e01) |
| `implementation_readiness-1-2` | D12, test rows | No defined representation or test for callback cancellation required by Section 7 and Edge Case 14. | PROPOSE FIX | [E03](#e03) |
| `implementation_readiness-1-3` | D10, D14, `_validate_output`, runner step 2 | Nested `model_construct` instances bypass validation; conversion errors fall into `MechanicsError`; a non-`dict` `Mapping` request fails strict validation. | PROPOSE FIX | [E04](#e04) |
| `implementation_readiness-1-4` | `SparkTable` validator | `^[1-6][1-6]$` with `re.match` accepts `"11\n"`. | PROPOSE FIX | [E05](#e05) |
| `codebase_details-1-1` | Baseline, D1, file boundary, Phase 0 | Baseline claims a clean worktree; the plan and the `AGENTS.md` plans convention are uncommitted, and no step commits them. | PROPOSE FIX | [E10](#e10) |
| `codebase_details-1-2` | `src/tome/__init__.py`, `src/tome/engine/__init__.py` | Re-export mechanism undecided; a computed `__all__` fails Ruff F401. | PROPOSE FIX | [E07](#e07) |
| `codebase_details-1-3` | D7, test helpers | How tests import the helpers is undecided; importing from `conftest` is discouraged and depends on the import mode. | PROPOSE FIX | [E06](#e06) |
| `codebase_details-1-4` | Phase 3 step 1, helpers | "Gate-level helpers" are undefined; `override_tables` and `seed_for_base_roll` have no phase. | PROPOSE FIX | [E06](#e06) |
| `style-1-1` | Decisions preamble | "First four decisions" omits D12; "single defensible option" is not a Source label. | PROPOSE FIX | [E02](#e02) |
| `style-1-2` | Interpretations paragraph | "D10 to D14 … leave to the implementation" contradicts D12's departure from Edge Case 6. | PROPOSE FIX | [E02](#e02) |
| `style-1-3` | D12 rationale | Section 2.8 names memory exhaustion, interpreter failure, and forced process termination, not interrupts. | PROPOSE FIX | [E02](#e02) |
| `style-1-4` | D13, runner error handling | "Any exception" can be read as `BaseException`, contradicting D12 and its test. | PROPOSE FIX | [E01](#e01) |
| `style-1-5` | Phases 1, 3, 4 and helpers | Helper terms are undefined, and helpers are not tagged by phase. | PROPOSE FIX | [E06](#e06) |
| `style-1-6` | Traceability headings and gates | "Bullet" and "row" are used interchangeably, and some rows are not Section 7 bullets. | PROPOSE FIX | [E09](#e09) |
| `style-1-7` | File boundary, verification | The boundary forbids the plan and its review records that the verification step allows. | PROPOSE FIX | [E11](#e11) |

### Nit

| Finding | Scope | Summary | Suggestion | Edit |
| :--- | :--- | :--- | :--- | :--- |
| `implementation_readiness-1-5` | Helpers | Same helper gaps as `codebase_details-1-4`. | PROPOSE FIX | [E06](#e06) |
| `implementation_readiness-1-6` | Mechanics, traceability, exports | Summed resolution roll hides the golden-vector dice; historical-novelty and missing-decision cases absent; explicit exports. | PROPOSE FIX | [E09](#e09), [E07](#e07) |
| `codebase_details-1-5` | Phase 5 grep | Scans `__pycache__`; misses multi-name and relative imports. | PROPOSE FIX | [E19](#e19) |
| `codebase_details-1-6` | Export count | "15 model classes" is ambiguous because `ContractModel` also exists. | PROPOSE FIX | [E08](#e08) |
| `codebase_details-1-7` | README edits | Activate line, stale tree entry after the rename, the source comment, and retained entries are not addressed. | PROPOSE FIX | [E20](#e20) |
| `codebase_details-1-8` | Probe version, baseline command | Probe results are not tied to the locked Pydantic version; the baseline command is unrecorded. | PROPOSE FIX | [E16](#e16) |
| `style-1-8` | D3 | "Phase 5 is pure deletion" although Phase 5 edits `README.md`. | PROPOSE FIX | [E12](#e12) |
| `style-1-9` | D12 | The first sentence includes `MemoryError`, which the next sentence excludes. | PROPOSE FIX | [E01](#e01) |
| `style-1-10` | Commit convention | `engine` scope conflicts with Phase 0's `build(tooling)`. | PROPOSE FIX | [E13](#e13) |
| `style-1-11` | Phase preamble | `code-author` is undefined in the repository. | PROPOSE FIX | [E14](#e14) |
| `style-1-12` | README edits | "Three tools" should be "three gate commands". | PROPOSE FIX | [E15](#e15) |
| `style-1-13` | Probe qualifiers | The two probe qualifiers differ; the lock may resolve a different Pydantic version. | PROPOSE FIX | [E16](#e16) |
| `style-1-14` | Export count | Same as `codebase_details-1-6`. | PROPOSE FIX | [E08](#e08) |
| `style-1-15` | Runner step 2, `seed_for_base_roll` | "Before this point" and "base roll" are unanchored. | PROPOSE FIX | [E17](#e17) |
| `style-1-16` | Verification plan | Duplicate static-analysis line; specification gate is not in a phase step; `python3` is 3.9. | PROPOSE FIX | [E18](#e18) |

## Proposed Edit Groups

Line numbers refer to the reviewed plan revision.
No edit changes the specification, the interface contract, `src/tome/tables.py`, or `pyproject.toml`.

### E01

**Findings:** `implementation_readiness-1-1`, `style-1-4`, `style-1-9`.

*   D12 Choice: replace the first sentence with "Any `Exception` other than `MemoryError` raised by a callback, including a `RunError`, becomes that callback's error type, chained with `from`."
*   D13 Choice: replace with "After request validation, any `Exception` raised by engine code, other than a `RunError` or `MemoryError`, becomes `MechanicsError`, chained with `from`. `RunError` and `MemoryError` are re-raised unchanged. Exceptions that are not `Exception` subclasses propagate unchanged."
*   Runner "Error handling" bullet: replace with "Steps 3 to 8 run inside one `try` block whose handlers are, in order: `except (RunError, MemoryError): raise`, then `except Exception as exc: raise MechanicsError(...) from exc`. No handler catches `BaseException`."

### E02

**Findings:** `style-1-1`, `style-1-2`, `style-1-3`.

*   Decisions preamble, replace both sentences with:
    "The human developer made decisions D1 to D4 and confirmed D12."
    "The other decisions follow from the specification (Source `Spec`), interpretations of its wording (Source `Interpretation`), repository conventions (Source `AGENTS.md`), or this plan (Source `Plan`), and are recorded so the implementer does not make them."
*   Interpretations paragraph, replace the first two sentences with:
    "Interpretations D10, D11, D13, and D14 do not add behaviour to the contract."
    "They fix choices the specification leaves to the implementation; the implementation-readiness review should challenge them if they conflict with the specification."
*   Replace the D12 rationale sentence with:
    "The author kept D12 because Section 2.8 states that memory exhaustion, interpreter failure, or forced process termination can prevent delivery of a typed `RunFailure`, and reads a keyboard interrupt as forced termination."

### E03

**Finding:** `implementation_readiness-1-2`.

*   Append to D12 Choice: "A callback signals cancellation by raising an `Exception` subclass, such as `concurrent.futures.CancelledError` or a caller-defined cancellation exception; it is wrapped like any other failure. `asyncio.CancelledError` is not an `Exception` subclass and propagates unchanged."
*   Traceability, callback-boundary row: add "`concurrent.futures.CancelledError` from `umpire_review` raises `UmpireReviewError`, and from `failure_resolver` raises `UmpireResolutionError`; `asyncio.CancelledError` propagates."

### E04

**Finding:** `implementation_readiness-1-3`.

*   D9 Choice: change to "Pydantic v2 models with `ConfigDict(strict=True, extra="forbid", revalidate_instances="always")`."
*   `models.py`, base class bullet: use the same `ConfigDict`, and add "`revalidate_instances="always"` makes nested model instances, including ones built with `model_construct`, pass full validation (probe-verified)."
*   `gates.py`, `_validate_output`: replace the description with "If `raw` is an instance of `model_cls`, validate `raw.model_dump()`; if `raw` is a `Mapping`, validate `dict(raw)`; otherwise raise `error_cls`. Any `Exception` other than `MemoryError` raised while dumping, converting, or validating becomes `error_cls`, chained with `from`."
*   D14 Choice: add "A `Mapping` is converted with `dict(request)` before validation."
*   Runner step 2: replace with "**Request:** convert a `Mapping` with `dict(request)` or a `RunRequest` with `request.model_dump(exclude_none=True)`, then call `RunRequest.model_validate(...)`. Any `Exception` other than `MemoryError` raised during conversion or validation becomes `InvalidRunRequestError`, chained with `from`."
*   Traceability: add to the Phase 4 request-validation row "a `MappingProxyType` request is accepted", and add a Phase 1 row assertion "a nested `model_construct` instance with an invalid value is rejected".

### E05

**Finding:** `implementation_readiness-1-4`.

*   `SparkTable` before-validator: replace "require each key to match `^[1-6][1-6]$`" with "require `re.fullmatch(r"[1-6][1-6]", key)` for each key".
*   Traceability, spark-table validation row: add `"11\n"` to the rejected keys.

### E06

**Findings:** `codebase_details-1-3`, `codebase_details-1-4`, `style-1-5`, `implementation_readiness-1-5`.

*   Replace `tests/conftest.py` with `tests/support.py` everywhere: D7, the file-boundary row, the phase steps, Target File 15, and the README Phase 5 list.
*   D7 Choice: "`tests/test_tome_integration.py`, and the plain helper module `tests/support.py`, imported as `from support import ...`. This relies on pytest's default `prepend` import mode; `tests/` must not contain `__init__.py`. `INVALID_REQUEST_CASES` feeds `pytest.mark.parametrize`, which fixtures cannot supply."
*   File-boundary row: `tests/support.py`, Create, Phases 1 and 4, "Plain helper module imported by both test files."
*   Target File 15: rename the heading to `tests/support.py`; change the scope line to "Plain test helper module; no pytest fixtures"; tag `make_world`, `make_request`, `override_tables`, and `INVALID_REQUEST_CASES` with "(Phase 1)", and `ScriptedCallbacks` and `seed_for_base_roll` with "(Phase 4)".
*   Phase 1 step 1: "add the Phase 1 tests and the Phase 1 helpers in `tests/support.py`."
*   Phase 3 step 1: "add the Phase 3 tests; they construct `TurnCues` and peer evaluations directly and need no new helpers."
*   Phase 4 step 1: "add the Phase 4 unit tests, `tests/test_tome_integration.py`, and the Phase 4 helpers in `tests/support.py`."

### E07

**Findings:** `codebase_details-1-2`, part of `implementation_readiness-1-6`.

*   Target File 13, Phase 4: "Use explicit `from tome.engine.<module> import <name>` statements and a literal `__all__` list. Do not use star imports or a computed `__all__`, which fails Ruff F401."
*   Target File 14: "Use one explicit `from tome.engine import ...` statement naming every public name, and a literal `__all__` list containing those names and `__version__`. Do not use star imports or a computed `__all__`."

### E08

**Findings:** `codebase_details-1-6`, `style-1-14`.

*   Target File 13: replace "the 15 model classes in `models.py`" with "the 15 models in the Target File 8 table; `ContractModel` is not exported".

### E09

**Findings:** `style-1-6`, part of `implementation_readiness-1-6`.

*   Rename the traceability column to "Requirement (Spec Section 7 bullet, invariant, or plan decision)".
*   Replace the section's first sentence with "Every row maps a requirement to at least one named test; every Spec Section 7 bullet appears in at least one row."
*   Phase 4 exit gate and Verification coverage line: "every row of the traceability table has a passing test".
*   `mechanics.py`: change `roll_resolution` to return `tuple[int, int]`, the two dice in draw order; the runner sums them for `resolution_roll`.
*   Golden-vector row: "including resolution dice (6, 6) for seed 42 and (4, 5) for seed 4".
*   Historical-canon row: add "proposal and failure-consequence novelty checks cover the entire canon history".
*   Failure-resolution validation row: add "a `None` return, the missing decision, raises `UmpireResolutionError`".

### E10

**Finding:** `codebase_details-1-1`.

*   Starting Baseline first sentence: "These facts were measured on 2026-11-17 on branch `feat/trio-engine-1.1` at commit `7d3fef1`, before this plan was written."
*   Add a baseline bullet: "Legacy tests were run with `uv run --isolated --no-project --python 3.11 --with 'pydantic>=2' --with 'pytest>=8' python -m pytest`, because no project environment exists yet."
*   Phase 0, new step 0: "Precondition: this plan, its Stage 9 review records, and the `AGENTS.md` `docs/plans/` convention are committed, and the worktree is clean."

### E11

**Finding:** `style-1-7`.

*   File boundary, after its second sentence: "This plan and its review records under `docs/reviews/001_tome_core_architecture_egm/implementation_readiness/` are outside this boundary and may change only through the EGM review workflow."
*   Verification, file-boundary line: "… lists only files from the file-boundary table and the documents named in the File Boundary exception."

### E12

**Finding:** `style-1-8`.

*   D3 Choice: replace "Phase 5 is pure deletion with no renames" with "Phase 5 deletes the legacy files and renames none".

### E13

**Finding:** `style-1-10`.

*   Phase preamble: "Commit messages for Phases 1 to 5 use Conventional Commit types with the scope `engine`; Phase 0 uses `build(tooling)`."

### E14

**Finding:** `style-1-11`.

*   Phase preamble: replace "follow the `code-author` cycle:" with "follow a test-first cycle:".

### E15

**Finding:** `style-1-12`.

*   README Phase 0 Prerequisites bullet: replace "run the three tools directly" with "run the three gate commands directly".

### E16

**Findings:** `style-1-13`, `codebase_details-1-8`.

*   Both probe qualifiers: "(probe-verified on Pydantic 2.14.3; the Phase 1 tests re-check this behaviour on the locked version)".
*   Phase 0 step 3: add "Record the locked Pydantic version in the commit message body."
*   Phase 1 traceability: add the assertions "a `bool` for an integer field is rejected", "an explicit `null` for `spark_tables`, `first_round_order`, or `seed` is rejected", and "a tuple for a list field is rejected" to the request-validation row, if not already covered by `INVALID_REQUEST_CASES`.

### E17

**Finding:** `style-1-15`.

*   Runner step 2: "No callable has been invoked and no `random.Random` exists before step 3."
*   `seed_for_base_roll`: replace "base roll" with "`resolution_roll`".

### E18

**Finding:** `style-1-16`.

*   Delete the Verification "Static analysis" line; the gate line already covers Ruff.
*   Move the specification gate into Phase 1 as step 0: "Run `python3 "${ARTIFICE_ROOT:-$HOME/.local/share/artifice}/scripts/validate_egm.py" . --spec 001` and confirm exit code 0. The validator runs on the system Python 3.9."
*   Replace the Verification specification-gate line with "Specification gate: Phase 1 step 0."

### E19

**Finding:** `codebase_details-1-5`.

*   Phase 5 step 3: replace the `grep` with `git grep -nE 'tome\.(models|dice|validator|runner)\b|from tome import [^#]*\b(models|dice|validator|runner)\b|from \.\.(models|dice|validator|runner)\b|from \.\. import [^#]*\b(models|dice|validator|runner)\b' -- src tests`.
    `git grep` searches tracked files only, so `__pycache__` is excluded.
    Relative imports inside `tome.engine`, such as `from .models import`, are not matched, because they refer to the new modules.

### E20

**Finding:** `codebase_details-1-7`.

*   README Phase 0: also remove `source .venv/bin/activate`, and update the project-tree test entry to `tests/test_legacy_engine.py  # Legacy tests, removed in Phase 5`.
*   README Phase 5: replace the `src/tome/` comment with "Simulation engine (Spec 1.1.2)"; keep the existing `docs/designs/`, `docs/reviews/`, `AGENTS.md`, `pyproject.toml`, and `LICENSE` entries.

## Approval Boundary

The human selected "auto accept" on 2026-11-17.
All 20 edit groups were applied to the plan in one batch.
This does not change the specification, approve the plan, or authorize implementation.

## Applied Resolution and Verification

*   Accepted and applied findings: 30.
*   Contested: 0.
*   Escalated: 0.
*   Declined: 0.
*   Unaddressed approved fixes: 0.
*   Round-one clean status remains **No**; the clean streak remains **0 of 2**.
*   Post-resolution plan: 491 lines; the Detailed Implementation Plan still starts at line 15.

**E19 correction:** the approved E19 pattern used `\b`, which `git grep -E` does not support on macOS.
Before applying, the coordinator ran it against the current tree: it returned 0 matches although 9 legacy imports exist, so the Phase 5 check would have passed falsely.
The plan instead uses an equivalent pattern built from `([^A-Za-z0-9_]|$)` boundaries, with the same intent and scope as E19.
It returns the 9 current legacy imports, and it gives the expected result for 13 synthetic cases, including `from tome import models`, `from .. import dice`, and the non-matches `from .models import Actor` and `from tome.engine.models import Actor`.
The plan states why `\b` is avoided.
Round 2 reviewers will assess this text independently.

Checks after applying:

*   Every applied text is present, and none of the replaced text remains.
*   Plan tables keep consistent column counts; fences, links, and whitespace pass; `git diff --check` passes.
*   The specification, `src/`, `tests/`, and `pyproject.toml` are unchanged from `7d3fef1`.
*   The targeted EGM validator still passes.
