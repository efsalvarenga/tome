# EGM Stage 9 Round 1: Reviewer Reports

**Date:** 2026-11-17
**Target:** [Implementation plan](../../../../plans/001_tome_core_architecture_plan.md), Detailed Implementation Plan, lines 15-475
**Target SHA-256:** `677122edc137a7e1f642f3899a265610b3f0a33614273919ad0b2ef3c4d1a8ef`
**Specification:** [Spec 001, version 1.1.2](../../../../designs/001_tome_core_architecture.md), auto-included as linked context
**Additional context:** `src/`, `tests/`, `pyproject.toml`, `AGENTS.md`, `README.md`
**Execution:** Three separate, fresh general-purpose task contexts using the installed official personas

| Reviewer | Standard | Status | Findings |
| :--- | :--- | :--- | :--- |
| `implementation_readiness` | `implementation-readiness-standard` | Completed | 0 Blocker, 4 Major, 2 Nit |
| `codebase_details` | `implementation-readiness-standard` | Completed | 0 Blocker, 4 Major, 4 Nit |
| `style` | Official style persona | Completed | 0 Blocker, 7 Major, 9 Nit (the reviewer's summary line says 8; it lists nine) |

No reviewer failed or required a retry.
The reports below are the reviewers' verbatim output, preserved without editing.

## Implementation Readiness: Complete Report

Status: completed

I reviewed round 1 against the implementation-readiness standard, covering plan lines 15–475 (SHA-256 verified). The plan is mostly ready to implement. Phasing, the file boundary and the per-file steps are strong. Six findings remain: four Major, two Nit. Two of them are spec gaps the plan leaves unassigned. No Blockers.

**implementation_readiness-1-1: Major. D13 (line 47) and runner error handling (line 353)**
- **Hurdle:** D13 turns "any exception … that is not a `RunError` or `MemoryError`" into `MechanicsError`. Callbacks run inside that same `try` block (steps 3–8).
  - D12 (line 46) requires `KeyboardInterrupt` from a callback to propagate unchanged. Read literally (`except BaseException`), D13 would convert it to `MechanicsError`.
  - The same reading would also relabel `SystemExit` and similar exceptions as `MechanicsError`. Spec 2.8 forbids relabelling environmental limits that way, and Invariant 15 reserves `MechanicsError` for engine defects.
  - The implementer has to decide which exception classes the outer handler catches.
- **Guidance:** State that D13 catches `Exception` only. `RunError` and `MemoryError` are re-raised, and non-`Exception` `BaseException`s propagate unchanged.

**implementation_readiness-1-2: Major. Traceability for callback "cancellation" (lines 428, 430, 443; D12)**
- **Hurdle:** Spec Section 7 (Umpire Audit and Errors; Failure Resolver Errors) and Edge Case 14 require tests showing that callback "failure/cancellation" raises `UmpireReviewError` or `UmpireResolutionError`. No row in the plan tests cancellation, and the plan never says what represents cancellation.
  - Under D12, `asyncio.CancelledError` (a `BaseException`) propagates untyped.
  - `concurrent.futures.CancelledError` (an `Exception`) would be wrapped.
  - So a spec-mandated test cannot be written without choosing an exception type and its expected result.
- **Guidance:** Name the exception class that stands for cancellation in this contract and its expected outcome under D12. Add that case to `test_callback_exceptions_wrapped`, or record that the Section 7 cancellation bullet is satisfied by D12's documented propagation.

**implementation_readiness-1-3: Major. Some malformed inputs bypass validation or end up as `MechanicsError` (lines 44, 48, 285, 328)**
- **Hurdle 1 (nested model instances):** D10 and D14 re-validate top-level model instances, but a `Mapping` can contain nested model instances. Examples are `{"world_state": WorldState.model_construct(...)}` or a pros list holding `SupportingPro.model_construct(source_type="actor_trait")`.
  - Pydantic's default `revalidate_instances="never"` accepts those instances without validation.
  - Blank or duplicate canon facts, or an invalid source type, would then pass. That violates Section 3.0 ("applies to every contract value") and Edge Cases 5 and 17.
- **Hurdle 2 (conversion errors):** `_validate_output` maps only `ValidationError` to the callback error. A non-`ValidationError` from `dict(raw)` or `raw.model_dump()` falls into D13 as `MechanicsError`, which Invariant 15 reserves for engine defects. The same applies in step 2 (line 328), which is outside the `try` block, so a raw exception can escape untyped.
- **Hurdle 3 (non-dict `Mapping`):** Line 328 does not say to convert a non-`dict` `Mapping` request with `dict(...)`. In strict mode, `model_validate` rejects such a request, contradicting D14.
- **Guidance:**
  - Add `revalidate_instances="always"` to `ContractModel.model_config`, or require recursive dumping.
  - In `_validate_output` and runner step 2, map any `Exception` raised during conversion to the corresponding error type.
  - State `RunRequest.model_validate(dict(request))` for the `Mapping` path.

**implementation_readiness-1-4: Major. `SparkTable` key pattern (line 250)**
- **Hurdle:** "match `^[1-6][1-6]$`" implemented with `re.match` or `re.search` accepts `"11\n"`, because `$` also matches before a trailing newline. `int("11\n") == 11`, so a table using that key passes the 36-key check. The spec's D66 definition (exactly the decimal-string keys) forbids this, and the plan's `"17"`/`"011"` tests would not catch it.
- **Guidance:** Specify `re.fullmatch(r"[1-6][1-6]", key)` and add `"11\n"` to the rejection cases in `test_spark_tables_validation`.

**implementation_readiness-1-5: Nit. Test helpers (lines 121, 127, 372–387)**
- Phase 3 step 1 asks for "gate-level helpers in `tests/conftest.py`", but Section 15 defines none. `seed_for_base_roll` is not assigned to any phase.
- With "no fixtures", the plan does not say how tests reach the helpers (for example, `from conftest import …`).
- **Guidance:** List the Phase 3 helpers (or remove the phrase), assign `seed_for_base_roll` to Phase 4, and state how tests access the helpers.

**implementation_readiness-1-6: Nit. Small traceability and API gaps (lines 275, 367, 414, 423, 430)**
- **Golden vectors:** `roll_resolution` returns only the sum, so `test_golden_vector_*` cannot check the individual resolution dice (6/6 and 4/5) that Invariant 14 gives. State whether asserting the sum is enough.
- **Historical canon:** The `test_historical_canon_grounding` row omits Section 7's check that novelty covers the entire history.
- **Missing decision:** The `test_failure_resolution_validation` row omits Section 7's "missing decision" case (resolver returns `None`).
- **Package exports:** Line 367 should require explicit imports. `from tome.engine import *` fails Ruff's default F403 rule.

**Files read**
- **Review instructions:** the implementation-readiness persona and standard.
- **Target and spec:** `docs/plans/001_tome_core_architecture_plan.md` (all lines) and `docs/designs/001_tome_core_architecture.md` (lines 1–1123 in full; lines 1124–1141 only partly seen).
- **Repository files:**
  - Read in full: `pyproject.toml`, `README.md`, `AGENTS.md`, `src/tome/__init__.py`.
  - Checked only by grep, import lines and file listings: the other `src/tome/` modules, `tests/test_tome_core.py`, and `src/tome/__pycache__`.

**Limitations**
- I did not run any tests or execute code. Pydantic behaviour (strict-mode `Mapping` handling and instance revalidation) is judged from documented v2 semantics, not probes.
- The worked-example dice for seed 20 were not independently verified; I took the approved spec's values as given.

## Codebase Details: Complete Report

Status: completed

**Codebase-details Goldfish review, round 1**
- Mode: REVIEW
- Target: `docs/plans/001_tome_core_architecture_plan.md`, lines 15–475
- SHA-256 verified: `677122ed…a8ef`
- Repository state: branch `feat/trio-engine-1.1` at `7d3fef1`

**Verified as accurate:**
- Baseline facts that could be checked:
  - Python versions: `python3` is 3.9.6; `python3.11` (3.11.18) and `uv` (0.13.8) are installed.
  - Absent files: there is no `uv.lock`, `.python-version`, `scripts/`, or `.github/`.
  - Legacy tests: there are 8 legacy tests (the pytest cache lists 8 node IDs and has no `lastfailed`).
  - `tables.py`: it has no imports and defines five `dict[int, str]` tables, `TABLE_ACTION`, `TABLE_FOCUS`, `TABLE_METHOD`, `TABLE_DISPOSITION` and `TABLE_MOTIVATION`, keyed 11–66.
  - Removed fields: the legacy fields the plan treats as removed exist in `src/tome/models.py`: `traits`, `posture`, `exhausted_traits`, `active_rumors` and `goal_alignment`.
- `pyproject.toml`:
  - `requires-python>=3.11`.
  - Dependencies: `pydantic>=2.0.0`, with a `dev` extra containing pytest and ruff.
  - Build: hatchling, with the `src/tome` layout auto-detected.
  - Ruff: `line-length` is 100, the target is py311, and there is no `select`, so the default rules E4, E7, E9 and F apply.
  - Pytest: `testpaths` and `python_files` are set; there is no `pythonpath` or `import-mode`.
- `src/tome/__init__.py` has a docstring and `__version__ = "0.1.0"`.
- Every README section the plan edits exists: Status, Project Structure, Prerequisites, Setup, Running the Test Suite, and Formatting & Static Analysis.
- `AGENTS.md` Section 3 exists, and its merge prohibition supports D17.
- Deletion list is complete:
  - Running the Phase 5 grep now returns exactly 8 hits.
  - All 8 hits are in the five files the plan deletes: `dice.py`, `validator.py`, `runner.py`, and the legacy test file (which imports `tome.runner` inside a function).
  - Nothing else in `src/` or `tests/` imports a legacy module.
- Nothing worth reusing:
  - The legacy `sanitize_anchor_string` differs from the Section 3.0 rule: it strips a lone `"`.
  - The legacy dice helpers create a new `Random` on every call.
  - So not reusing them is correct; `tables.py` is reused as planned.
- No file the plan creates is git-ignored, and `core.fileMode=true`, so the `755` mode on `lint.sh` will be tracked.

**Findings:**

- **codebase_details-1-1 — Major.** The stated baseline does not match the current worktree.
  - Plan locations: lines 19, 35, 71, 97–105 and 462.
  - Line 19 says the baseline is `7d3fef1` "with a clean worktree".
    - `git status` actually shows ` M AGENTS.md` and `?? docs/plans/`.
  - D1 (line 35) says "`AGENTS.md` documents the `docs/plans/` convention."
    - That text exists only as an uncommitted change (`AGENTS.md` lines 31–35 in the worktree); it is absent at `7d3fef1`.
  - The `AGENTS.md` row in the file boundary (line 71) and Target File 5 (line 178) cover only the Section 3 verification-gate bullet.
  - No phase step says who commits the existing Section 2 edit or the plan file itself, or that Phase 0 starts from this dirty tree.

- **codebase_details-1-2 — Major.** The re-export in `src/tome/__init__.py` can conflict with the existing Ruff configuration.
  - Plan locations: lines 82 and 365–367.
  - "Re-export every name in `tome.engine.__all__`, and set `__all__` to those names plus `__version__`" leaves the mechanism undecided.
  - Ruff's default rules (`pyproject.toml` lines 23–25, which set no `select`) include F:
    - `from .engine import *` triggers F403.
    - Explicit imports with a computed `__all__` (for example `[*engine.__all__, "__version__"]`) trigger F401.
  - Only a literal import list plus a literal `__all__` passes `ruff check`, and therefore the Phase 4 gate. The plan should require that.

- **codebase_details-1-3 — Major.** The plan does not say how tests get the `tests/conftest.py` helpers.
  - Plan locations: lines 41, 370–387, 109, 121 and 127.
  - The helpers (`make_world`, `make_request`, `override_tables`, `INVALID_REQUEST_CASES`, `ScriptedCallbacks`, `seed_for_base_roll`) are plain objects, and line 372 rules out fixtures.
  - Test modules would therefore need `from conftest import …`. That relies on pytest's default `prepend` import mode and on there being no `tests/__init__.py`.
  - Neither is configured or stated: `pyproject.toml` lines 27–29 set no `pythonpath` or `--import-mode`, and pytest discourages importing `conftest`.
  - The plan does not fix the import form or forbid adding `tests/__init__.py`, so the implementer has to make that choice.

- **codebase_details-1-4 — Major.** Some test helpers are referenced but never specified or scheduled.
  - Plan locations: line 121 against lines 370–387.
  - Phase 3 says to add "the gate-level helpers in `tests/conftest.py`". Target File 15 defines no gate-level helpers.
  - The phase when `seed_for_base_roll` and `override_tables` are added is not stated. `override_tables` is needed by the Phase 2 tests at lines 418 and 422.

- **codebase_details-1-5 — Nit.** The Phase 5 grep (line 135) has scope gaps.
  - It scans untracked `src/tome/__pycache__/*.pyc` and `tests/__pycache__/*.pyc`.
    - Those files contain `tome.models` and `tome.dice`.
    - They escape a match today only because the next byte (for example `r`) defeats `\b`.
  - It misses forms like `from tome import tables, models`, and relative imports such as `from .. import models` or `from ..models import`.
  - `git grep` over tracked files, with a broader pattern, would be deterministic.

- **codebase_details-1-6 — Nit.** The export count is ambiguous.
  - Plan locations: line 361 against line 215.
  - Line 361 says "the 15 model classes in `models.py`", but `models.py` also defines `ContractModel(BaseModel)`, making 16 `BaseModel` subclasses.
  - The plan does not say whether `ContractModel` is exported.

- **codebase_details-1-7 — Nit.** The README edits leave some current lines unaddressed.
  - Plan locations: lines 167–173. The README lines in question are 124–128, 94 and 102.
  - Phase 0 replaces `uv venv` and `uv pip install`, but does not say what to do with `source .venv/bin/activate` (README line 125).
  - After the Phase 0 rename, the project tree still shows the stale `tests/test_tome_core.py  # Deterministic test suite` until Phase 5.
  - The `src/tome/` comment "(legacy implementation; Spec 1.1.2 approved)" is not mentioned.
  - The Phase 5 list does not say whether to keep the existing `docs/designs/`, `docs/reviews/`, `AGENTS.md`, `pyproject.toml` and `LICENSE` entries.

- **codebase_details-1-8 — Nit.** The Pydantic version used by the probes is not tied to the lockfile.
  - Plan locations: lines 22, 246 and 101; `pyproject.toml` line 9.
  - The probe results are stated as verified on Pydantic 2.14.3.
  - `uv lock` will resolve the latest version satisfying `pydantic>=2.0.0`, and the plan does not require checking that the locked version matches 2.14.3.
  - The baseline also does not record which environment or command produced the passing run; no `.venv` exists.

**Files read:**
- The persona file and the implementation-readiness standard
- The target plan, in full
- `docs/designs/001_tome_core_architecture.md`: lines 118–135, 530–600, 870–905, 1028–1100, plus greps
- `src/tome/__init__.py`, `dice.py`, `models.py`, `runner.py`, `tables.py` and `validator.py`
- `tests/test_tome_core.py`: grep of its imports and definitions, plus two long lines
- `pyproject.toml`, `README.md`, `AGENTS.md` (worktree copy and its diff), `.gitignore` and the `.pytest_cache` node IDs

**Limitations:**
- I did not run tests or Ruff, so the claims that the tests pass on Pydantic 2.14.3 and that Ruff passes are unverified. Manual inspection found only docstring or comment lines over 100 characters, and E501 is not in Ruff's default rules.
- I could not locate the installed Pydantic version.
- I did not read `docs/reviews/` contents or anything outside the repository, including `validate_egm.py`.
## Style: Complete Report

Status: completed

The SHA-256 matched `677122ed…a8ef`. I audited lines 15–475 and found 7 Major, 8 Nit and 0 Blocker findings.

**style-1-1 — Major — lines 30–31**
- **Wording:** "The human developer made the first four decisions during drafting." and "The remaining decisions follow from the specification, the repository conventions, or a single defensible option".
- **Problem:** D12 (line 46) is attributed to "Author, 2026-11-17", and the header (line 10) says the author confirmed it. So "the remaining decisions" is wrong about how D12 was made. "A single defensible option" is a subjective judgement, and no row in the Source column uses that label.
- **Action:** CALIBRATE.
  - Line 30 becomes "The human developer made decisions D1 to D4 and D12."
  - Line 31 becomes "The other decisions follow from the specification (Source `Spec`), the specification's wording (Source `Interpretation`), repository conventions (Source `AGENTS.md`), or this plan (Source `Plan`)."

**style-1-2 — Major — lines 53–54**
- **Wording:** "Interpretations D10 to D14 do not add behaviour to the contract. They fix choices the specification leaves to the implementation".
- **Problem:** Line 55 says "D12 departs from Edge Case 6". So D12 is not a choice the specification leaves open. A reader gets two contradictory statements about D12's status.
- **Action:** CALIBRATE.
  - Line 53 becomes "Interpretations D10, D11, D13, and D14 do not add behaviour to the contract."
  - Line 54 becomes "They fix choices the specification leaves to the implementation; the implementation-readiness review should challenge them if they conflict with the specification."
  - Leave D12 to lines 55–57.

**style-1-3 — Major — line 56**
- **Wording:** "Section 2.8 already states that memory exhaustion and interrupts can prevent delivery of a typed `RunFailure`."
- **Problem:** Spec Section 2.8 (spec line 263) says "Memory exhaustion, interpreter failure, or forced process termination". It does not mention interrupts. This sentence is the stated reason for departing from the specification, so it should quote the specification accurately.
- **Action:** CALIBRATE.
  - Use "Section 2.8 states that memory exhaustion, interpreter failure, or forced process termination can prevent delivery of a typed `RunFailure`."
  - If interrupts (`KeyboardInterrupt`) are part of the reason, state that as the author's own reading.

**style-1-4 — Major — line 47 (D13), with line 353**
- **Wording:** "any exception raised by engine code that is not a `RunError` or `MemoryError` becomes `MechanicsError`".
- **Problem:** "Any exception" can be read as `BaseException`. Under that reading, a `KeyboardInterrupt` raised inside the line 353 `try` block becomes `MechanicsError`. D12 (line 46) says the opposite for non-`Exception` types, and the test row at line 443 expects `KeyboardInterrupt` to propagate.
- **Action:** Use "any `Exception` subclass raised by engine code, other than `RunError` or `MemoryError`, becomes `MechanicsError`, chained with `from`; exceptions that are not `Exception` subclasses propagate unchanged."

**style-1-5 — Major — lines 109, 121, 127 against Section 15 (lines 370–387)**
- **Wording:** "the builders in `tests/conftest.py`" (line 109), "the gate-level helpers in `tests/conftest.py`" (line 121), "the scripted callbacks" (line 127).
- **Problem:** Section 15 never uses the terms "builders" or "gate-level helpers". It also does not say which phase adds which helper.
  - No listed helper fits "gate-level", yet the File Boundary schedules a Phase 3 change to `conftest.py`.
  - `seed_for_base_roll` has no phase.
- **Consequence:** The implementer must decide what Phase 3 adds.
- **Action:** Tag each Section 15 bullet with its phase, for example "(Phase 1)". Then either name the Phase 3 helpers or remove Phase 3 from the `tests/conftest.py` row and from line 121.

**style-1-6 — Major — lines 129, 402, 405, 459**
- **Wording:** "every Section 7 bullet in the traceability table has a passing test" (line 129), "Every Spec Section 7 bullet maps to at least one named test" (line 402), the column header "Spec Section 7 bullet" (line 405), and "Every row of the traceability table has at least one passing test" (line 459).
- **Problem:** Bullets and rows are not the same thing.
  - Some rows merge several bullets (lines 422 and 433).
  - Some rows split one bullet across several rows ("(table independence)", "(run)").
  - Some rows are not Section 7 bullets at all: "Explicit failure types" (lines 412 and 444, which is Invariant 15), "Spark table identity" (line 419), "Callback boundary (D10 to D12)" (line 443) and "Integration: worked example" (line 445).
- **Consequence:** The Phase 4 exit gate (bullets) and the coverage requirement (rows) can be read as two different checks.
- **Action:**
  - Rename the column to "Requirement (Spec Section 7 bullet, invariant, or plan decision)".
  - Make lines 129 and 459 both say "every row of the traceability table".

**style-1-7 — Major — lines 61–62 against line 461**
- **Wording:** "may create, modify, rename, or delete only these files. Any other file change … is out of bounds" against "lists only files from the file-boundary table, plus this plan and its review records".
- **Problem:** The plan file and its review records are allowed changes at line 461 but forbidden by lines 61–62. Their paths are not given.
- **Action:** At line 62, add "This plan and its review records under `docs/reviews/001_tome_core_architecture_egm/` are outside this boundary and may change." Point line 461 to that sentence.

**style-1-8 — Nit — line 37 (D3)**
- **Wording:** "Phase 5 is pure deletion with no renames".
- **Problem:** Phase 5 also edits `README.md` (line 134).
- **Action:** CALIBRATE to "Phase 5 deletes legacy files and renames none".

**style-1-9 — Nit — line 46 (D12)**
- **Wording:** "Any `Exception` raised by a callback, including a `RunError`, becomes that callback's error type".
- **Problem:** The next sentence makes `MemoryError`, which is an `Exception` subclass, an exception to this rule. The first sentence is therefore broader than intended.
- **Action:** Use "Any `Exception` other than `MemoryError` raised by a callback, including a `RunError`, becomes…".

**style-1-10 — Nit — lines 95 and 105**
- **Wording:** "Commit messages use Conventional Commit types with the scope `engine`" against Phase 0's `build(tooling): …`.
- **Action:** Limit line 95 to "Commit messages for Phases 1 to 5 use…", or change line 105 to the `engine` scope.

**style-1-11 — Nit — line 93**
- **Wording:** "the `code-author` cycle".
- **Problem:** The term is not defined in the repository context.
- **Action:** Drop the agent name and keep the definition that follows: "Phases 1 to 4 use a red test commit, a green feature commit, and an optional refactor commit."

**style-1-12 — Nit — line 170**
- **Wording:** "run the three tools directly".
- **Problem:** The gate uses two tools (Ruff and pytest) to run three commands.
- **Action:** Use "run the three gate commands directly".

**style-1-13 — Nit — lines 246 and 258**
- **Wording:** "(probe-verified on Pydantic 2.14.3)" and "(probe-verified)".
- **Problem:** The two qualifiers differ, and the `uv lock` in Phase 0 may resolve a different Pydantic version.
- **Action:** CALIBRATE line 258 to "(probe-verified on Pydantic 2.14.3)". Optionally add a Phase 0 step that records the locked Pydantic version.

**style-1-14 — Nit — line 361**
- **Wording:** "the 15 model classes in `models.py`".
- **Problem:** `models.py` also defines `ContractModel`, so it has 16 model classes. A reader may ask whether the base class is exported.
- **Action:** Use "the 15 models in the table above (not `ContractModel`)".

**style-1-15 — Nit — lines 329 and 386**
- **Wording:** "before this point" (line 329) and "base roll" (line 386).
- **Problem:** "This point" has no exact anchor. "Base roll" is undefined in the plan and appears only once in the spec.
- **Action:** Use "before step 3" and "`resolution_roll`".

**style-1-16 — Nit — lines 455, 457–458**
- **Problem:**
  - Line 458 (Static analysis) repeats line 457, since the lint script already runs Ruff.
  - Line 455 uses `python3`, which line 25 records as 3.9.6.
  - The specification gate does not appear in the Phase 0 or Phase 1 steps.
- **Action:**
  - DROP line 458, or merge it into line 457.
  - RELOCATE the specification gate into the Phase 1 steps, before "Red", and name the interpreter to use.

**One sentence per source line:** No violations in the target range. Tables, code and headings were excluded.

**Files read**
- `/Users/Estevao.alvarenga/.vscode/agent-plugins/github.com/google/elephant-goldfish-model/agents/style.md`
- `docs/plans/001_tome_core_architecture_plan.md` (whole file)
- `docs/designs/001_tome_core_architecture.md` (headings, Section 2.8, Edge Case 6, Invariants 14 and 15, Sections 3.4, 3.5 and 7)
- `AGENTS.md`, `pyproject.toml`
- `src/tome/` listing, `src/tome/tables.py`, `src/tome/dice.py` and `src/tome/models.py` (via grep)
- `tests/` listing and test count
- `.gitignore`, `git log`, current branch

**Limitations**
- I did not re-measure the version facts on lines 22 and 25 (Python, Pydantic, Ruff results), because that would mean running interpreters or tests.
- I did not read `README.md` in full.