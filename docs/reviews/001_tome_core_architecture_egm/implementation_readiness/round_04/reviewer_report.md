# EGM Stage 9 Round 4: Reviewer Reports

**Date:** 2026-11-18
**Target:** [Implementation plan](../../../../plans/001_tome_core_architecture_plan.md), Detailed Implementation Plan, lines 15-505
**Target SHA-256:** `beadbc1e5e7ce6c7b59a8e3107d3ad4714faf49edad5ae9aa87d64e9fac39aad`
**Specification:** [Spec 001, version 1.1.2](../../../../designs/001_tome_core_architecture.md)
**Additional context:** `src/`, `tests/`, `pyproject.toml`, `AGENTS.md`, `README.md`
**Execution:** Three separate, fresh general-purpose task contexts using the installed official personas; earlier findings were not supplied

| Reviewer | Standard | Status | Findings |
| :--- | :--- | :--- | :--- |
| `implementation_readiness` | `implementation-readiness-standard` | Completed | 0 Blocker, 0 Major, 1 Nit |
| `codebase_details` | `implementation-readiness-standard` | Completed | 0 Blocker, 0 Major, 1 Nit |
| `style` | Official style persona | Completed | 0 Blocker, 1 Major, 9 Nit |

No reviewer failed or required a retry.
The reports below are the reviewers' output, preserved without editing.

## Implementation Readiness: Complete Report

Status: completed

**Verdict:** The plan is ready to implement. There are no Blocker or Major findings and one Nit.

**Findings**

**implementation_readiness-4-1: Nit**
- **Where:** Runner steps 7.2, 7.3, 7.4 and 7.7 (lines 357–364), read together with the Snapshots bullet (line 373) and the Error handling bullet (line 376).
- **Hurdle:** The phrase "invoke X(…) under D12 with Error" does not say what the D12 wrapper surrounds.
  - Snapshot arguments are written inline in the call, so the implementer must decide whether the engine's `model_copy(deep=True)` snapshot work sits inside or outside the wrapper.
  - If it sits inside, an engine-side `RecursionError` or other `Exception` raised during snapshot creation is relabelled as that callback's error. D13 says such an error should propagate unchanged or become `MechanicsError`.
  - The word "then" suggests the gate call sits outside the wrapper. If an implementer put it inside, the wrapper would turn `InvalidProposalError` from `build_proposal` into `ProposalGenerationError`. The Phase 4 tests would catch this; they would not catch the snapshot misclassification.
- **Guidance:** Add one sentence:
  - Build all snapshot and list arguments before the guarded call.
  - The D12 `try` wraps only the callable invocation expression.
  - Gate functions (`build_proposal`, `validate_peer_evaluation`, `apply_umpire_rejections`, `validate_failure_resolution`) are called after and outside that `try`.

**Checks that found no problem**
- **File boundary:** Every create, modify, rename and delete is listed with its phase. The "9 legacy imports" count for the Phase 5 search matches the current tree.
- **Phases:** Each phase ends with `./scripts/lint.sh` passing, and the red-then-green commits are explicit.
- **Steps per file:** Signatures, the order of validation checks, the order of random draws, how exceptions are classified, snapshot rules, the export lists and the helper defaults are all fixed in the plan.
- **Coverage:** Every Section 7 bullet in the specification maps to a named test. Rows that list only test names hand their assertions to the named spec bullet, which is clear enough.
- **Disagreements with the spec:** Outside D12, I found no plan instruction that would make the code violate the specification. The consequences of D12 (`MemoryError` and non-`Exception` errors propagate; `concurrent.futures.CancelledError` is wrapped and `asyncio.CancelledError` propagates) are recorded and tested.

**Files actually read**
- The persona `agents/implementation_readiness.md` and the standard `implementation-readiness-standard.md`.
- The target, `docs/plans/001_tome_core_architecture_plan.md`, all 505 lines in chunks with truncations completed. Its SHA-256 matched `beadbc1e…aad`.
- The specification, `docs/designs/001_tome_core_architecture.md`, all 1,140 lines.
- `pyproject.toml`, `README.md`, `AGENTS.md` (plus its uncommitted diff), `.gitignore` and `src/tome/__init__.py`.
- `src/tome/tables.py` (first 30 lines plus the table names), the first 40 lines of `tests/test_tome_core.py`, the import lines of every file under `src/tome/` and `tests/`, a directory listing, and `git log` / `git status` output.

**Limitations**
- I did not run any code, so the Pydantic 2.14.3 behaviours, the golden-vector draws and the seed-20 worked-example draws are taken from the plan's Starting Baseline.
- The legacy modules `dice.py`, `models.py`, `runner.py` and `validator.py` were not read in full.
- I did not read anything under `docs/reviews/`, any session artifact, or any other reviewer's output.

## Codebase Details: Complete Report

Status: completed

**Review details**
- Mode: REVIEW, as the codebase-details reviewer, against the implementation-readiness standard.
- Target: `docs/plans/001_tome_core_architecture_plan.md`, lines 15–505. Its SHA-256 matched `beadbc1e…aad`.

### Findings

#### codebase_details-4-1 — Nit

**Where:** plan lines 25, 44, 176 and 488; `pyproject.toml` lines 23–25 (`[tool.ruff]` sets no `include` or `exclude`).

**Problem:** The plan treats the Ruff format check as a check on Python code only. The Ruff version available locally formats Markdown files too, and the plan does not say so.

**Evidence:**
- The locally cached Ruff is 0.17.5. `pyproject.toml` only asks for `ruff>=0.4.0`, so `uv lock` will likely pick a version at least this new.
- `ruff format --no-cache --check -v .` reports 32 files. The extra files are `README.md`, `AGENTS.md`, the specification, this plan, and every Markdown file under `docs/reviews/`, including the untracked `implementation_readiness/` round records. I saw only the paths, not the contents.
- `ruff check --show-files .` covers only the 7 Python files and `pyproject.toml`.
- No Markdown file outside `docs/reviews/` has a Python code block today, and the check passes.

**Why it matters:**
- The gate also covers review records, which the plan says may change "only through the EGM review workflow" (line 101).
- A Python code block in a later review record or README edit could fail `./scripts/lint.sh` for reasons outside the implementer's control. The implementer would then have to choose a fix, which the zero-decision rule forbids.
- The Phase 0 commit body (line 128) records only the Pydantic version, not the Ruff version that `uv.lock` picks, and Ruff's version decides this behaviour.

**Suggested fix:** State that the format check covers Markdown files, or record the locked Ruff version. Changing `pyproject.toml` is out of scope.

### Claims confirmed against the repository
- **Branch and baseline commit:** the branch is `feat/trio-engine-1.1` and HEAD is `7d3fef1`. `AGENTS.md` has the uncommitted `docs/plans/` convention, so the Phase 0 step 0 precondition is not met yet. That is consistent with the plan.
- **Files that do not exist yet:** `uv.lock`, `.python-version`, `scripts/` and `.github/`. `tests/` has no `__init__.py` or `conftest.py`.
- **Legacy engine:** the 4 legacy modules, `tests/test_tome_core.py` and its 8 tests exist as described. The legacy code covers step-dice postures, traits and exhaustion, outcome bands, `active_rumors` and urgency sorting.
- **Phase 5 deletion list:** it is complete. It lists the 4 modules and the renamed test file. `tables.py` and `__init__.py` are kept.
- **Phase 5 `git grep`:** I ran it exactly as written with git 2.54.0 (Apple). It returns exactly 9 matches: 5 in `src/` and 4 in `tests/`. It does not match `tome.engine.*` paths, or the new names the plan lists.
- **`tables.py`:** checked by parsing it, without importing it. It has only a docstring and five `TABLE_*` dictionaries. Each has exactly the 36 d66 keys, all plain integers, with non-blank string values. It imports nothing.
- **`pyproject.toml`:**
  - Pydantic, pytest and Ruff are declared, with pytest and Ruff in the `dev` extra.
  - The build backend is Hatchling, and the package sits at `src/tome`.
  - Ruff uses line length 100 and target `py311`.
  - pytest uses `testpaths=["tests"]`, `python_files=["test_*.py"]`, no `importmode` and no `pythonpath`. So the `prepend` import mode the plan relies on holds, and `support.py` will not be collected as a test file.
- **`src/tome/__init__.py`:** it holds the docstring and `__version__ = "0.1.0"`. None of the planned exports reuse a submodule name.
- **README sections the plan edits:** Status, Prerequisites, Setup (`uv venv` / `source` / `uv pip install -e ".[dev]"`), "Running the Test Suite", "Formatting & Static Analysis", and the project-structure comments all exist as quoted. The `docs/reviews/001_tome_core_architecture_review.md` entry is tracked.
- **AGENTS.md:** Section 3 exists.
- **Environment:** the default `python3` is 3.9.6, `python3.11` (3.11.18) and `uv` are installed, and the `validate_egm.py` path exists.
- **Random-draw values:** `random.Random` on Python 3.11 reproduces the seed 42 and seed 4 golden vectors and the seed 20 values (posture 6, Focus then Method, keys 66 and 13, dice 5 and 2). The spec's worked example uses seed 20, order `["actor_a","actor_b"]`, and override entries in the `"<Table> <key>"` pattern.
- **Cancellation errors:** on Python 3.11, `concurrent.futures.CancelledError` is an `Exception` subclass and `asyncio.CancelledError` is not.
- **Ruff baseline:** with `--offline --no-cache`, both the lint and format checks pass.
- **Reuse:** I found no missed reuse. Legacy `validator.sanitize_anchor_string` has different rules from spec Section 3.0 and is deleted in Phase 5, so not reusing it is correct.

### Files read
- The plan, lines 1–505.
- The persona file and the standard.
- Spec lines 520–600 and 840–1110, plus searches through the rest.
- Everything in `src/tome/` (`tables.py` partly read, partly parsed).
- `tests/test_tome_core.py`: lines 1–60 and every import and test name.
- `pyproject.toml`, `README.md`, `.gitignore`, and the `AGENTS.md` diff (the injected AGENTS.md also served as context).

### Limitations
- I did not run pytest or Pydantic. The claims that the 8 legacy tests pass with Pydantic 2.14.3, the Pydantic behaviours, and the `uv lock`/`uv sync` results are unverified.
- I did not read inside `docs/reviews/`. I only listed file paths through Ruff's verbose output.

## Style: Complete Report

Status: completed

**Findings (style-4-1 to style-4-10)**

**style-4-1 — Major — line 370 (with lines 368–369)**
- **Wording:** "Append a `TurnRecord` built from the values above."
- **Problem:** `TurnRecord.session_index` can be read two ways. It could hold the value before the step-8 increment, or the value after it. Spec line 520 requires the value after the turn and any round boundary. The plan does not say which. No row in the traceability table asserts a record's `session_index` on a round-ending turn. `test_end_to_end_cycling_and_counters` checks only "one completed round" and the counters. A wrong value at round boundaries could therefore pass the gate.
- **Action:** Add a sentence to step 10: "`turn_index` and `session_index` are taken from `state` after step 8." Also add a record-level `session_index` assertion to the cycling test row.

**style-4-2 — Nit — lines 360–361, 364, 366**
- **Wording:** "…once under D12 with `UmpireReviewError`, then `apply_umpire_rejections`."
- **Problem:** The plan never says to rebind the returned tuple. Step 5 says "final votes" and step 7 says `lowest_vote_candidates(evaluations)`. An implementer could compute both from the evaluations before rejection.
- **Action:** Write "then `evaluations, umpire_rejections = apply_umpire_rejections(...)`".

**style-4-3 — Nit — line 351, line 461**
- **Wording:** "**Generator:** `rng = random.Random(…)`" and "no generator constructed".
- **Problem:** "Generator" also names `proposal_generator`. Line 461 can be read as "no proposal generator". Line 459 says "no `random.Random` constructed" for the same check.
- **Action:** Rename the step 4 label to "**Random generator:**". At line 461, write "no `random.Random` constructed".

**style-4-4 — Nit — line 437**
- **Wording:** "this re-checks on the locked Pydantic version that a `bool` for an integer, an explicit `null` for an optional field, and a tuple for a list are rejected."
- **Problem:** Starting Baseline line 25 records only the explicit-`null` check. "Re-checks" claims earlier verification of the `bool` and tuple cases, and nothing records it.
- **Action:** CALIBRATE: "this checks on the locked Pydantic version that … are rejected, re-checking the explicit-`null` behaviour recorded in Starting Baseline."

**style-4-5 — Nit — line 404**
- **Wording:** "each mutator edits a fresh `make_request()` dict to produce one Edge Case 5 violation."
- **Problem:** Several listed cases are not in Edge Case 5. These are `seed`, `spark_tables`, or `first_round_order` set to `None`, and `first_round_order` supplied as a tuple. They come from the Section 3.4 rule that optional fields reject `null`, or from strict typing.
- **Action:** CALIBRATE to "one Edge Case 5 or Section 3.4 request violation".

**style-4-6 — Nit — line 401**
- **Wording:** "naming each actor `Actor A`, `Actor B`, and so on, with agenda `Agenda A`, `Agenda B`, and so on."
- **Problem:** The name could come from list position or from the ID suffix. For IDs `("actor_c", "actor_a", "actor_b")`, the readings differ. The names appear in default proposal statements ("{active_actor.name} achieves outcome …"), so tests that assert those strings depend on the choice.
- **Action:** State the rule, for example "the n-th actor (by position) is named `Actor <n-th capital letter>`".

**style-4-7 — Nit — line 53 (D13)**
- **Wording:** "Those four are re-raised unchanged, because Section 2.8 forbids relabelling resource exhaustion or interpreter failure as `MechanicsError`."
- **Problem:** `RunError` is one of "those four", but it is neither resource exhaustion nor interpreter failure. The stated reason covers only three of the four.
- **Action:** Write "A `RunError` is re-raised because it is already typed; the other three are re-raised because Section 2.8 forbids …".

**style-4-8 — Nit — line 220**
- **Wording:** "Spec Section 3.0 normalization, with no other dependencies."
- **Problem:** The phrase can be read as "no imports". But `find_match` and `has_matching_pair` need `Sequence` imported from `collections.abc`.
- **Action:** Write "imports no other `tome` module".

**style-4-9 — Nit — lines 30, 63–64**
- **Line 30:** "…has no imports, and is reused unchanged." The section reports measured facts, but "is reused unchanged" is a plan decision, already stated in D8 and in the File Boundary. Action: RELOCATE by dropping the clause, since D8 already covers it.
- **Lines 63–64:** "The human developer confirmed this trade-off on 2026-11-17." and "…until then, D12 governs the implementation." These repeat line 37, the D12 Source cell ("Author, 2026-11-17"), and header line 11. Action: DROP both sentences.

**style-4-10 — Nit — lines 487 and 491 (compare 489, 490, 492)**
- **Problem:** "Build and environment" and "File boundary" give no time for the check. Their sibling checks say "exits 0 after every phase" or "at the end of every phase".
- **Action:** Add "after every phase" to both, or name the phase when each check runs.

**Checked with no finding**
- **One sentence per line:** none found in prose lines 15–505 (headings, tables and code exempt).
- **Decision numbering:** D1–D17 run in sequence. The Source attributions in lines 37–38 and 59 match the table.
- **D12's "six specification passages":** matches spec lines 815, 836, Edge Cases 6 and 14, and the two Section 7 bullets.
- **Counts:**
  - 15 models.
  - Seven error subclasses.
  - Eight `engine/` files.
  - Five legacy files, which matches "four legacy modules and `tests/test_legacy_engine.py`".
  - 8 legacy tests.
  - 30 tier and table-pair combinations.
- **Legacy-import search:** a read-only `git grep` confirmed both claims. The pattern returns 9 matching lines today, and `git grep -E` with `\b` matches nothing on this machine (Apple Git 2.54.0).
- **Section 7 coverage:** all 29 unit bullets and 6 integration bullets appear in the traceability table.
- **Worked example and golden vectors:** seed 20 and the override entries match spec lines 371–379, 568–571, 596 and 662. The Invariant 14 vectors match spec lines 898–901.

**Files read**
- Persona: `/Users/Estevao.alvarenga/.vscode/agent-plugins/github.com/google/elephant-goldfish-model/agents/style.md`
- Target: `docs/plans/001_tome_core_architecture_plan.md` (SHA-256 matches `beadbc1e…aad`)
- `docs/designs/001_tome_core_architecture.md` (selected sections)
- `README.md`, `pyproject.toml`
- `src/tome/` file list and import lines; `tests/test_tome_core.py` test names and imports
- `AGENTS.md`, via the injected repository instructions

**Limitations**
- I did not open `AGENTS.md` from disk; I used the copy injected as repository instructions.
- I ran read-only commands: `git grep`, `git status` and `git log`. I did not run tests, Pydantic or Ruff.
- I did not verify the Pydantic, Ruff and pytest behaviour claims beyond what the plan and spec record.
- I did not read `docs/reviews/`.
