# EGM Stage 9 Round 5: Reviewer Reports

**Date:** 2026-11-18
**Target:** [Implementation plan](../../../../plans/001_tome_core_architecture_plan.md), Detailed Implementation Plan, lines 15-506
**Target SHA-256:** `713caa27483e578bfa27cbd559627e72fd01d5efe72f488ba672176f6115a20b`
**Specification:** [Spec 001, version 1.1.2](../../../../designs/001_tome_core_architecture.md)
**Additional context:** `src/`, `tests/`, `pyproject.toml`, `AGENTS.md`, `README.md`
**Execution:** Three separate, fresh general-purpose task contexts using the installed official personas; earlier findings were not supplied

| Reviewer | Standard | Status | Findings |
| :--- | :--- | :--- | :--- |
| `implementation_readiness` | `implementation-readiness-standard` | Completed | 0 Blocker, 0 Major, 1 Nit |
| `codebase_details` | `implementation-readiness-standard` | Completed | None |
| `style` | Official style persona | Completed | 0 Blocker, 2 Major, 4 Nit |

No reviewer failed or required a retry.
The reports below are the reviewers' output, preserved without editing.

## Implementation Readiness: Complete Report

Status: completed

**Implementation Readiness Goldfish, Round 5, Mode: REVIEW**

Target: `docs/plans/001_tome_core_architecture_plan.md`, lines 15–506. I read lines 1–14 for context only. The SHA-256 matched `713caa27…115a20b`.

**Verdict:** I could implement every phase on the first attempt from the plan plus the specification, without making a design or architectural choice. The one gap is a small test-fixture choice, rated Nit below.

Checks against the standard:
- **Phasing:** Phases 0–5 each end with `./scripts/lint.sh` passing. The red test commit in Phases 1–4 is the only planned failure.
- **Phase dependency order holds:**
  - Phase 1: `text` feeds `models`, and `models` feeds `errors`.
  - Phase 2: `mechanics` builds on Phase 1.
  - Phase 3: `gates` uses `TurnCues` from Phase 2.
  - Phase 4: `runner`, `protocols` and the public exports.
- **Import cycles:** `tome/__init__` imports `tome.engine`, which reaches `tome.tables`. Python allows importing a submodule of a package that is still initialising, so this does not break.
- **File boundary:** the file list is exact and matches the phase steps.
- **Phase 5 grep count:** the plan says the pattern finds 9 legacy imports before Phase 5. A read-only search confirmed 9.
- **New code and the grep:** new code that imports `tome.engine.*` does not match the pattern.
- **Actionable steps:** every Target File section gives signatures, check order, error mapping and draw order. Callback wrapping, snapshot rules and the error-handler order are all fixed.
- **Spec coverage:** every Section 7 unit bullet and all six integration bullets map to named tests. I found no spec-required behaviour without a file, step or test.
- **D12:** the plan applies it consistently in runner step 7, `_validate_output`, `test_callback_exceptions_wrapped` and `test_callback_cancellation`. The concrete effect is that `asyncio.CancelledError`, `KeyboardInterrupt` and `MemoryError` from a callback escape untyped. The plan states this and tests it.
- **Other decisions:** D10, D13 and D14 do not contradict the specification.
- **Worked example:** it lines up with runner steps 7.5–7.9. Seed 20 gives a roll of 7, the vote modifier is -1, and the total is 6, so the turn fails. The two state changes are `/canon_facts` with `failure-consequence` and `/turn_index`; `session_index` does not change.

**Findings**

- **ID:** implementation_readiness-5-1
- **Severity:** Nit
- **Affected scope:**
  - Line 414: the `seed_for_base_roll` helper.
  - Line 501: the traceability row "Integration: run-wide atomicity", test `test_invalid_decision_after_resolved_turn_is_atomic`.
- **Hurdle:** `seed_for_base_roll(target)` only controls the first turn's roll. Because the order is supplied, turn 1 draws the same values in longer runs, so it still works for tests that need turn 1 to fail. The atomicity test is different: an earlier turn must resolve, then a later turn must fail so the failure resolver can return an invalid decision. The plan gives no way to force a Failure on turn 2 or later. The implementer must pick one:
  - search seeds for a two-turn sequence inside the test, or
  - replace `tome.engine.runner.roll_resolution`, which the plan already makes replaceable at line 368, with a scripted sequence.

  Either choice has no effect on production code.
- **Guidance:** Add one sentence to the line-501 row or to line 414. For example: "replace `tome.engine.runner.roll_resolution` with a function returning `(4, 4)` then `(1, 1)`, so turn 1 succeeds and turn 2 fails". Alternatively, extend `seed_for_base_roll` to take a sequence of per-turn targets for a supplied-order run.

**Files read**
- `agents/implementation_readiness.md` (persona) and `resources/document_standards/implementation-readiness-standard.md` (standard), both under `elephant-goldfish-model/`.
- The target plan, lines 1–506, read in full in chunks, with every truncation completed.
- `docs/designs/001_tome_core_architecture.md`, lines 1–1123.
- `pyproject.toml`, `README.md`, `src/tome/__init__.py`, and the start and table names of `src/tome/tables.py`.
- Import lines from all files in `src/tome/*.py` and `tests/*.py`, plus a pattern search over `src/` and `tests/`.
- `git log -3` and `git status`, plus a directory listing of `src/tome` and `tests`.

**Limitations**
- I did not run tests, Ruff or Pydantic. I took the plan's Starting Baseline claims as given:
  - an explicit `null` is rejected;
  - `revalidate_instances` fully re-validates nested instances;
  - JSON dumps write integer keys as strings;
  - the seed-20 and golden-vector draws;
  - Ruff's Markdown handling.
- I did not read spec lines 1124–1141 (the Section 8 review-history footer), the legacy module bodies, `.gitignore` (not in the context list), or `AGENTS.md` beyond the copy loaded with the instructions.
- The worktree currently shows `AGENTS.md` modified and `docs/plans/` untracked. This is not a finding, because the Phase 0 precondition explicitly requires both to be committed first.

## Codebase Details: Complete Report

Status: completed

**Codebase-details review, round 5: No findings.** No Blocker, Major or Nit issues found. Mode: REVIEW. Scope: plan lines 15–506. The plan's SHA-256 matches `713caa27…6115a20b`.

**What I checked against the current repository**

- **Baseline (plan lines 17–32):** Holds.
  - HEAD is `7d3fef1` on `feat/trio-engine-1.1`.
  - The legacy engine has step-dice postures, traits and exhaustion, outcome bands, rumours and urgency sorting (`dice.py`, `models.py`, `runner.py:31-41`, `validator.py:115-165`).
  - `tests/test_tome_core.py` has 8 tests.
  - `tables.py` has no imports and exactly 180 entries (5 tables × 36 keys, 11–66).
  - There is no `uv.lock`, `.python-version`, `scripts/` or `.github/`.
  - The default `python3` is 3.9.6, and `python3.11`, `uv` and `uvx` are installed.
  - `validate_egm.py` exists at the cited path. It only reads top-level `docs/reviews/<NNN>_*.md` files, so the plan and review folders do not affect Phase 1 step 0.
- **`pyproject.toml`:**
  - Dependencies are `pydantic>=2.0.0`, with `pytest` and `ruff` in the `dev` extra (supports D16 and `--extra dev`).
  - The build backend is Hatchling with a `src/tome` layout, so an editable install works.
  - `requires-python >=3.11` agrees with D5.
  - The Ruff section sets only line length and target version, so the default rules apply. No file line exceeds 100 characters except docstrings.
  - The pytest settings are `testpaths=["tests"]` and `python_files=["test_*.py"]`, with no `--import-mode` or `pythonpath`. So `support.py` is not collected as a test file.
  - `tests/` has no `__init__.py` or `conftest.py`, so D7's `from support import ...` works under pytest's default import mode. The test file basenames are unique.
- **Phase 5 grep (plan lines 145–147):** I ran it read-only. It returns exactly 9 lines: `dice.py:6`, `runner.py:5,6,8`, `validator.py:3`, and test lines 1, 2, 3 and 293. It does not match the new `tome.engine.*` or `from tome.engine import` forms.
- **Phase 5 deletion list:** Complete. The five deletions plus the kept `__init__.py` and `tables.py` account for every tracked file under `src/` and `tests/`. The only other references to legacy files are `README.md:96-102`, which Phase 5 updates, and spec line 1032, which names the new unit-test file.
- **README edits (plan lines 183–193):** Every section the plan names exists with the quoted wording: the Setup steps, "Running the Test Suite", "Formatting & Static Analysis", Prerequisites, the Status block, and the project-structure entries and comments.
- **AGENTS.md edit (plan line 196):** Section 3 exists at `AGENTS.md:39`. The `docs/plans/` convention edit is in the working tree but not yet committed, which is what the Phase 0 precondition requires.
- **Other checks:**
  - `.gitignore` already covers `.venv`, `__pycache__` and the pytest and Ruff caches, and does not ignore `uv.lock` or `.python-version`.
  - Non-review Markdown has no `python` or `py` fences.
  - `git diff --check` is clean, and the plan has no trailing whitespace.
  - Every Section 7 bullet appears in the traceability table.
  - The `override_tables` entry format matches the spec's Section 3.4 example.
- **Reuse:** The legacy `sanitize_anchor_string` (`validator.py:6-15`) differs from Spec 3.0 normalization (no two-character minimum, and it returns `None` for empty input) and is being deleted. Writing a new `text.normalize` is correct, and `tables.py` is reused as D8 says.

**Files read:**
- `AGENTS.md`, `README.md`, `pyproject.toml`, `.gitignore`
- all of `src/tome/*.py` and `tests/test_tome_core.py`
- the plan in full
- spec sections 2.1–2.2, 3.0–3.5, Section 4 (to line 917), and the Section 7 headings
- the review-file matching logic in `validate_egm.py` (outside the provided context, read-only)
- git listings and log, `git grep`, and `ls`

**Limitations:**
- I ran no tests and no project code, so I could not confirm these claims:
  - the legacy tests and Ruff checks passing
  - the Pydantic 2.14.3 behaviours
  - the golden-vector and seed-20 draw values
  - the `uv lock` and `uv sync` outcomes
  - that the locked Ruff formats Markdown
- I did not read `docs/reviews/`, so the claim "no `python`-fenced Markdown" is confirmed only for files outside it.

## Style: Complete Report

Status: completed

**Findings**

**style-5-1 — Major — line 179**
- Wording: "With the locked Ruff, the format check also covers Markdown files and reformats the code in fenced `python` blocks".
- Problem 1: The gate runs `ruff format --check`, which reports changes and never writes files. "Reformats" therefore contradicts the command on line 175. An implementer could take it to mean the gate edits Markdown.
- Problem 2: The Markdown-coverage claim is stated as verified fact, but Starting Baseline does not support it. Line 26 ran Ruff through unpinned `uvx`. Line 29 records only the Pydantic version from the temporary lock. Neither shows which Ruff version gets locked or how it treats Markdown.
- Consequence: a reader cannot tell whether README or plan edits that add `python` fences will fail the gate.
- Action: CALIBRATE. Change it to "checks the code in `python`-fenced Markdown blocks and fails if it would reformat it."
  - Then either add the Ruff version and this observation to Starting Baseline, or mark the sentence as an expectation that Phase 0 step 6 confirms.
  - Keep the clause "the repository has no `python`-fenced Markdown at `7d3fef1`". A search of `docs/`, `README.md` and `AGENTS.md` found none.

**style-5-2 — Major — line 53 (D13) against line 305 (Target File 10)**
- D13 says that after request validation, a `RecursionError` or `SystemError` "raised by engine code" is "re-raised unchanged".
- Line 305 says any `Exception` other than `MemoryError` raised while `_validate_output` dumps, converts or validates "becomes `error_cls`". The gate is engine code, so this includes `RecursionError` and `SystemError`.
- For the same event, a `RecursionError` while validating a callback's output, the plan gives two outcomes: propagate unchanged, or wrap as `ProposalGenerationError`, `PeerReviewError` and so on.
- Line 377 makes wrapping happen in practice: the gate wraps first, then the handler re-raises the resulting `RunError`. D13 as written still tells a test author otherwise.
- Action: add a scoping clause to D13, for example: "...raised by engine code and not already converted to a callback error type by `_validate_output` (Target File 10)". Alternatively, if the author intends propagation, extend line 305's exemption list to match D13.

**style-5-3 — Nit — lines 50 (D10), 54 (D14), 304 and 347**
- Wording: "an instance of the corresponding `tome.engine` model class" and "Any other type, including a different model class, is malformed" (line 50). Line 304 says "if `raw` is an instance of `model_cls`".
- A subclass of the model class fits both readings: an `isinstance` check accepts it, while "a different model class" suggests it is rejected. `test_model_instance_returns_accepted` does not settle which.
- Action: state the check explicitly: `isinstance(raw, model_cls)` (subclasses accepted) or `type(raw) is model_cls`. Apply the same wording to `RunRequest` in D14 and on line 347.

**style-5-4 — Nit — line 370**
- Wording: "read from `state` after step 8".
- Top-level step 8 (line 371, "Return `RunResult`") is also "step 8", so the reference can be read two ways. Only sub-step 8 of step 7 (line 366) gives the intended values.
- Action: write "after sub-step 8 of step 7".

**style-5-5 — Nit — line 310**
- Wording: "Then construct `Proposal` from ...".
- The line is indented 8 spaces while item 3's text starts at column 12. Markdown therefore folds it into item 3, so the rendered plan shows construction as part of the "Grounding" check.
- Action: make it item 4, "Construction: build `Proposal` from ...".

**style-5-6 — Nit — line 117 against line 28**
- Line 117 uses `${ARTIFICE_ROOT:-$HOME/.local/share/artifice}`. `ARTIFICE_ROOT` is not defined anywhere in the plan.
- The baseline on line 28 measured the literal `$HOME/.local/share/artifice` path. If the variable is set, a different validator runs than the one measured.
- Action: use the same literal path as line 28, or define `ARTIFICE_ROOT` and state that the baseline used its default.

**Claims checked and kept**
- All counts match:
  - 8 engine files; 15 models; 7 error subclasses; 4 protocols.
  - 5 legacy deletions; D12's 6 passages; 30 tier and table-pair combinations.
- `git grep` on `7d3fef1` returns the 9 legacy-import matches line 147 claims.
- `git grep -E '\b...'` matched nothing on Apple Git 2.54.0, confirming line 146.
- The golden vectors for seeds 42, 4 and 20 match the specification.
- Every Section 7 unit and integration bullet appears in the traceability table.
- The README section names cited on lines 186–193 exist.
- No breaches of the one-sentence-per-line rule were found in prose; the apparent hits were list numbering.

**Files read**
- `elephant-goldfish-model/agents/style.md`
- The target plan, lines 1–506; its SHA-256 matched.
- From the context: targeted sections of `docs/designs/001_tome_core_architecture.md`, `pyproject.toml`, `README.md`, and import lines in `src/` and `tests/` (via `git grep`).

**Limitations**
- I did not run Ruff, so the Markdown-coverage claim in style-5-1 is unverified in either direction.
- No network access, tests or builds.
- I ran read-only `git grep` checks and `git --version`.
- I did not read `docs/reviews/` or session artifacts.
