# EGM Stage 9 Round 3: Reviewer Reports

**Date:** 2026-11-18
**Target:** [Implementation plan](../../../../plans/001_tome_core_architecture_plan.md), Detailed Implementation Plan, lines 15-499
**Target SHA-256:** `afd65538a48727343205668a8c3fc6c5d9ce13ab176b508993535c417f5c3a00`
**Specification:** [Spec 001, version 1.1.2](../../../../designs/001_tome_core_architecture.md)
**Additional context:** `src/`, `tests/`, `pyproject.toml`, `AGENTS.md`, `README.md`
**Execution:** Three separate, fresh general-purpose task contexts using the installed official personas; earlier findings were not supplied

| Reviewer | Standard | Status | Findings |
| :--- | :--- | :--- | :--- |
| `implementation_readiness` | `implementation-readiness-standard` | Completed | 0 Blocker, 0 Major, 5 Nit |
| `codebase_details` | `implementation-readiness-standard` | Completed | 0 Blocker, 0 Major, 2 Nit |
| `style` | Official style persona | Completed | 0 Blocker, 2 Major, 8 Nit |

No reviewer failed or required a retry.
The reports below are the reviewers' output, preserved without editing.

## Implementation Readiness: Complete Report

Status: completed

**Verdict:** I could implement every phase on the first attempt without making any design or architectural choice. There are no Blockers and no Majors. The five Nits below are small gaps in instruction wording or test detail.

What I checked:
- **Zero-Decision Rule:** decisions D1–D17 settle every schema, error mapping, callback boundary, draw order, file layout, and gate command I would otherwise have had to choose.
- **Phasing:** each phase ends on the `./scripts/lint.sh` gate. The red-commit failure is declared, and the import order works.
- **File boundary:** it lists exact paths only.
- **Steps per file:** every file has steps that can be acted on directly.
- **Section 7 coverage:** every unit and integration bullet in the spec's Section 7 maps to a named test.
- **Spec conflicts:** I found no plan instruction that contradicts the spec, apart from D12. D12's concrete consequences are carried consistently through runner step 2, the D12/D13 handler order, `_validate_output`, and the D12 tests.

**Findings**

**implementation_readiness-3-1 — Nit**
- **Where:** plan line 368 (runner "Snapshots"); lines 355 and 359 ("evaluation snapshots"); line 467 (`test_callbacks_receive_isolated_snapshots`).
- **Hurdle:** the rule allows "a fresh `list` copy" for any list argument. Read literally, `peer_evaluations` could be passed as `list(evaluations)`, which shares the `PeerEvaluation` objects. A callback that mutated an element would then change engine state, which breaks Spec 3.5's "isolated snapshots". The test only says "mutating arguments does not affect the result", so it may not catch this.
- **Guidance:**
  - State that list arguments made of models are lists of per-element `model_copy(deep=True)` copies.
  - In the test, list the mutations to make, for each of the four callbacks:
    - append to `world_state.canon_facts`;
    - edit an actor;
    - edit `proposal.supporting_pros`;
    - set `peer_evaluations[0].final_vote`;
    - append to `spark_tags` and to `candidate_voter_ids`.

**implementation_readiness-3-2 — Nit**
- **Where:** line 452 (Phase 3, `test_umpire_rejection_reverts_and_records`); lines 460–461 (Phase 4 umpire rows).
- **Hurdle:** the spec's Section 7 "Umpire Audit and Errors" bullet asks to assert that `UmpireReview` *receives* `biased_shift_applied: true` and `cited_anchor: "Fact 1."`. The Phase 3 gate test cannot see what the callback receives, and no Phase 4 test records it.
- **Guidance:** in a Phase 4 test, run the Section 7 vector through `run` with `ScriptedCallbacks`. Assert that `umpire_calls[0][2][0]` has flag `True` and anchor `"Fact 1."`, and that the turn record's `evaluation_before_reversion` equals it.

**implementation_readiness-3-3 — Nit**
- **Where:** line 439 (`test_draws_ignore_table_contents_and_key_order`, "reversed key order").
- **Hurdle:** the phrase could mean the order of the d66 keys or the order of the table names. The spec (Invariant 14 and the Section 7 Seeded Random bullet) is about JSON object key order affecting table selection, so the table-name order matters. The implementer would have to pick one.
- **Guidance:** require both: the five table names in reversed order, and each table's d66 keys in reversed order.

**implementation_readiness-3-4 — Nit**
- **Where:** Target Files 13–14 (lines 375–390) and the traceability table.
- **Hurdle:** no test checks the public API that D3, File 13, and File 14 define. A missing or extra export, or a broken `tome` re-export, would still pass the Phase 4 and Phase 5 gates.
- **Guidance:** add a Phase 4 row, `test_public_api_exports`, asserting:
  - `tome.engine.__all__` is exactly the set listed at line 380;
  - `set(tome.__all__) == set(tome.engine.__all__) | {"__version__"}`;
  - `tome.run is tome.engine.runner.run`.

**implementation_readiness-3-5 — Nit**
- **Where:** Starting Baseline, line 23; Phase 0 exit gate, line 111.
- **Hurdle:** the baseline was measured with `--no-project` and `PYTHONPATH=src`, so nobody has checked that `tome` builds and installs through the existing Hatchling `pyproject.toml` under `uv run --locked`. The Phase 0 gate depends on that build, and `pyproject.toml` is outside the file boundary. If the build fails, the implementer has no allowed fix and must stop.
- **Guidance:** confirm and record that `uv sync --locked --extra dev` builds the project and makes `import tome` work, or state that a build failure at Phase 0 is a stop-and-raise condition.

**Files read**
- The persona file `implementation_readiness.md` and the standard `implementation-readiness-standard.md`.
- The plan, `docs/plans/001_tome_core_architecture_plan.md`: all 499 lines. Its SHA-256 matches `afd65538…3c00`.
- The spec, `docs/designs/001_tome_core_architecture.md`: all of Sections 1–7, plus the start of Section 8.
- `pyproject.toml`, `README.md`, and Sections 2–4 of `AGENTS.md`.
- `src/tome/__init__.py`, plus `src/tome/tables.py` (header and table names).
- The import lines of the legacy `src/tome/*.py` modules and of `tests/test_tome_core.py`; the `src/tome/` and `tests/` directory listings.
- `.gitignore`: read as part of a command, though it is not in the listed context.

**Limitations**
- I did not run any tests, builds, or code, and did not access the network. The Pydantic behaviour, the golden vectors, and whether Hatchling builds the project are taken from the plan's baseline claims, not checked.
- I did not read git history, so I could not confirm that the File Boundary `git diff` check will only show the allowed files.
- I did not read the body of the legacy modules or the legacy test functions; I only checked their imports.
- I did not read the rest of the spec's Section 8 (its review history).

## Codebase Details: Complete Report

Status: completed

**Review:** Codebase Details Goldfish, round 3, Mode: REVIEW.
**Standard:** implementation-readiness-standard.md.
**Target:** `docs/plans/001_tome_core_architecture_plan.md`, lines 15–499. The SHA-256 matches `afd65538…3c00`.

### Verified with no discrepancy

- **Branch and commit:** the branch is `feat/trio-engine-1.1` and HEAD is `7d3fef1` ("Approve Spec 1.1.2 after review").
- **Legacy description (L21):** the legacy code does use step dice, traits and exhaustion, outcome bands, `active_rumors`, and urgency ordering. Evidence: `dice.py` `get_posture_die_sides`, `models.py` `Faction`, `validator.py` `apply_adjudication_outcome`, and `runner.py` `sort_factions_by_urgency`.
- **Legacy tests (L22–23):** `tests/test_tome_core.py` has exactly 8 top-level `test_` functions.
  - There is no `.venv`, so no project environment exists yet.
  - `tome` lives only under `src/`, so it is not importable without `PYTHONPATH=src` in `--no-project` mode.
- **`tables.py` (L28):** it defines exactly `TABLE_ACTION`, `TABLE_FOCUS`, `TABLE_METHOD`, `TABLE_DISPOSITION`, and `TABLE_MOTIVATION`, each a `dict[int, str]` with keys 11–66. It has no imports.
- **Machine (L29):** `python3` is 3.9.6, and `python3.11`, `uv`, and `uvx` are installed.
- **Absent files (L30):** there is no `uv.lock`, `.python-version`, `scripts/`, or `.github/`.
- **`pyproject.toml` (D4, D5, D16, lint.sh):**
  - Pydantic is a dependency, and pytest and Ruff are in the `[project.optional-dependencies] dev` extra, so `--extra dev` is correct.
  - The build backend is hatchling, and `requires-python` is `>=3.11`.
  - Ruff uses `line-length=100` and `target-version="py311"`.
  - pytest uses `testpaths=["tests"]` and `python_files=["test_*.py"]`, with no `--import-mode`.
- **Test helpers (D7):**
  - `tests/` has no `__init__.py` and no `conftest.py`, so the default `prepend` mode lets `from support import ...` work.
  - `support.py` does not match `test_*.py`, so pytest will not collect it.
  - `test_legacy_engine.py` and `test_tome_core.py` have different basenames, as `prepend` mode requires.
- **File Boundary and Phase 5:**
  - Every path is marked Create, Modify, Rename, or Delete.
  - All five Delete targets exist, and the list is complete: `models.py`, `dice.py`, `validator.py`, `runner.py`, and the renamed legacy test file.
  - `__init__.py` and `tables.py` are correctly kept.
  - No proposed export name collides with a legacy submodule name.
- **Phase 5 `git grep` (L143–146):** I ran it at HEAD.
  - It returns exactly 9 lines: `dice.py:6`, `runner.py:5,6,8`, `validator.py:3`, and `test_tome_core.py:1,2,3,293`.
  - I confirmed that `git grep -E` with `\b` silently matches nothing (Apple Git 2.54.0).
  - The planned new imports (`tome.engine.*`, `from .models`) do not match the pattern.
- **README edits:** the `uv venv`, `source .venv/bin/activate`, and `uv pip install -e ".[dev]"` steps exist. So do the "Running the Test Suite" and "Formatting & Static Analysis" subsections, the Prerequisites, the Status block, and the Project Structure entries the plan says it will change or keep.
- **AGENTS.md:** Section 3, "Technology Stack & Standards", exists. The `docs/plans/` convention is present in the working tree but not yet committed, which Phase 0 step 0 makes a precondition.
- **Exception classes (Python 3.11.18):**
  - `concurrent.futures.CancelledError` is an `Exception` subclass.
  - `asyncio.CancelledError` is not an `Exception` subclass and is a different class.
  - `RecursionError` and `SystemError` are both `Exception` subclasses.
- **Legacy field names in tests:** `traits`, `posture`, `exhausted_traits`, `active_rumors`, and `goal_alignment` all exist in legacy `models.py`.
- **Spec cross-checks:**
  - All 29 Spec Section 7 unit bullets and all 6 integration bullets map to traceability rows.
  - The worked example's override labels (`"Focus 66"` → "Resource access", `"Method 13"` → "Public declaration") match the `override_tables` design.
- **Reuse:** no existing code is missed. Legacy `sanitize_anchor_string` normalization differs from Spec 3.0 (it has no two-character minimum and returns `None` for empty input) and is being deleted, so a new `text.py` is justified.

### Findings

**codebase_details-3-1**

- **Severity:** Nit
- **Affected scope:** plan L23 and L175 (also L481); `pyproject.toml` L18–20.
- **Discrepancy:** an assumption is left unstated.
  - L23 records that the legacy tests fail to collect without `PYTHONPATH=src`.
  - The gate at L175 (`uv run --locked --extra dev pytest`) sets no `PYTHONPATH`. It works only because `uv run` installs the project editable, which it does because `[build-system]` uses hatchling and hatchling auto-detects `src/tome/__init__.py`.
  - The plan never states this, and the File Boundary forbids `pyproject.toml` edits such as `pythonpath = ["src"]`.
  - An implementer reconciling L23 with L175 has to infer the mechanism. One sentence in the Starting Baseline or the lint.sh section would remove the guess.

**codebase_details-3-2**

- **Severity:** Nit
- **Affected scope:** plan L486.
- **Discrepancy:** with no revision argument, `git diff --check` compares only the working tree against the index.
  - The plan requires a commit at the end of each phase, so this check passes trivially after each phase and never inspects the committed changes.
  - It should name the base explicitly, for example `git diff --check 7d3fef1`, matching the neighbouring Contract preservation and File boundary checks.
  - Currently `git diff --check` exits 0, and the plan file has no trailing whitespace.

No Blockers or Majors.

### Files read

- The persona (`codebase_details.md`) and the standard (`implementation-readiness-standard.md`).
- The plan, in full.
- The spec: lines 268–760 and 885–920, plus grep scans and the Section 7 bullets at 1030–1110.
- `src/tome/__init__.py`, `dice.py`, `models.py`, `runner.py`, `tables.py`, and `validator.py`.
- `tests/test_tome_core.py`: imports, test signatures, and lines 133 and 172.
- `pyproject.toml`, `.gitignore`, `README.md`, and `AGENTS.md`, plus the `git diff` of `AGENTS.md`.
- Commands: `git ls-files`, `git status`, `git log`, `git show --stat 7d3fef1`, and the existence and shebang of the external `validate_egm.py`.

### Limitations

- I did not run tests, Ruff, or uv, so these baseline claims are unverified:
  - the legacy tests pass and Ruff passes;
  - the lock resolves Pydantic 2.14.3;
  - the Pydantic strict-mode and serialization behaviours;
  - the seed 20, 42, and 4 golden vectors.
- I did not use the network.
- I did not read `docs/reviews/`.

## Style: Complete Report

Status: completed

**Findings**

**style-3-1: Major. Line 486.**
- Wording: "**Whitespace:** `git diff --check` exits 0."
- Problem: The command has no base revision, so it checks only unstaged working-tree changes. Every phase ends with a commit, so the check passes without examining any work. Lines 484–485 compare against `7d3fef1`; this line does not.
- Action: Change it to "`git diff --check 7d3fef1` exits 0 after every phase."

**style-3-2: Major. Line 59. Action: CALIBRATE.**
- Wording: "`MemoryError` propagates because Section 2.8 states that memory exhaustion can prevent delivery of a typed `RunFailure` and must not be relabelled."
- Problem: Spec Section 2.8 says only that these limits "must not be relabelled as the internal-defect-only MechanicsError". It also groups "interpreter failure" with memory exhaustion. Read broadly, the sentence implies that callback `RecursionError` and `SystemError` must also propagate. D12 (line 50), line 301 and line 345 wrap them instead. An implementer could reasonably add those two exceptions to the D12 exemptions.
- Action: Narrow the sentence to "…and must not be relabelled as `MechanicsError`; D12 extends this to callback error types for `MemoryError` only."

**style-3-3: Nit. Lines 58 and 50.**
- Count problem: Line 58 says "five specification passages", then lists "Section 3.5 for the umpire review and the failure resolver", Edge Cases 6 and 14, and two Section 7 bullets. Section 3.5 has separate umpire-review and failure-resolver sentences (spec lines 815 and 836), so the list reads as six passages.
- Parsing problem: "Umpire Audit and Errors and Failure Resolver Errors bullets" is hard to parse.
- Naming problem: Line 50 shortens the bullet name to "Umpire Audit". The spec, line 58 and line 452 all use "Umpire Audit and Errors".
- Action: State the count to match the list (for example "six passages: the two Section 3.5 sentences…"). Quote the bullet names, as in "the Section 7 'Umpire Audit and Errors' and 'Failure Resolver Errors' bullets". Use the full name at line 50.

**style-3-4: Nit. Line 26. Action: CALIBRATE.**
- Wording: "The same method confirmed the Invariant 14 golden vectors and the Section 3.4 worked example".
- Problem: No new engine exists yet, so only the random draws could have been confirmed, not the worked example's result JSON. That full output is still future work (lines 420–422).
- Action: Change it to "confirmed the draw values of the Invariant 14 golden vectors and of the Section 3.4 worked example: …".

**style-3-5: Nit. Line 27. Action: RELOCATE.**
- Wording: "Those tests check the legacy mechanics, not Spec 1.1.2."
- Problem: The bullet follows two bullets about throwaway Pydantic and golden-vector scripts, so "Those tests" can be read as referring to those scripts.
- Action: Move the bullet to directly after line 23, or begin it with "The 8 legacy tests check…".

**style-3-6: Nit. Line 231.**
- Wording: "makes nested model instances, including ones built with `model_construct`, pass full validation".
- Problem: "Pass" can be read as "be accepted by". The intent, shown by line 25 ("fully validated") and the test at line 438 ("is rejected"), is that the instances are re-validated and can fail.
- Action: Change it to "subjects nested model instances, including ones built with `model_construct`, to full validation".

**style-3-7: Nit. Line 346.**
- Wording: "No callable has been invoked and no `random.Random` exists before step 3."
- Problem 1: The engine creates the generator in step 4, not step 3.
- Problem 2: The `random` module always holds a global `Random` instance, so "no `random.Random` exists" is literally false. Tests at lines 455–456 check construction, not existence.
- Action: Change it to "Steps 1 and 2 invoke no callable and construct no `random.Random`."

**style-3-8: Nit. Lines 34–35 and the Source column of D1–D4 and D12.**
- Wording: Line 35 lists the Source values `Spec`, `Interpretation`, `AGENTS.md` and `Plan`.
- Problem: The legend omits `Author`, which the table uses for five rows. The prose then alternates between "the human developer" (lines 11, 34) and "the author" (lines 10, 61) for the same role.
- Action: On line 34, write "The human developer (Source `Author`) made decisions D1 to D4 and confirmed D12." Then use one term throughout.

**style-3-9: Nit. Line 117. Action: CALIBRATE.**
- Wording: "The validator runs on the system Python 3.9."
- Problem: This reads as a measured fact. The Starting Baseline (lines 19–30) records that `python3` is 3.9.6, but it does not record any run of `validate_egm.py` or the existence of the `ARTIFICE_ROOT` default path.
- Action: Either add a baseline bullet recording a successful validator run at `7d3fef1`, or rewrite the line as an instruction: "Use the default `python3` (3.9.6); the validator does not need the project environment."

**style-3-10: Nit. Lines 309–317, 322, 347, 351, 359 and 366.**
- Problem 1: Several names are used before they are defined:
  - `tables`, `source`, `records` and `evaluations` in the runner
  - unqualified `turn_count` (line 351)
  - `evaluation` and "the flag" / "the anchor" in the gates
- Problem 2: The gates text never ties "the flag" to `biased_shift_applied` or "the anchor" to `cited_anchor`.
- Action:
  - Step 3: "set `tables` and `source` to…".
  - Before step 7: add "start with `records = []`".
  - Line 351: use `request.turn_count`.
  - Line 309: "`evaluation = _validate_output(…)`".
  - First use in the gates: "`biased_shift_applied` (the flag)" and "`cited_anchor` (the anchor)".

**One sentence per line:** I found no prose line in lines 15–499 with more than one sentence. Tables, code and headings are exempt.

**Claims checked and found accurate (not findings):**
- 8 legacy tests (line 22).
- `tables.py` has no imports (line 28).
- No `uv.lock`, `.python-version`, `scripts/` directory or CI workflow (line 29).
- 9 legacy import matches (line 146), and `\b` matching nothing under Apple Git 2.54 (line 145).
- 15 models in the Target File 8 table; eight `src/tome/engine/` files; five legacy files.
- 30 tier and table-pair combinations; the Invariant 14 golden-vector values.
- The README section names and setup steps; Section 7 bullet coverage in the traceability table.
- Spec's "base roll" wording matches `seed_for_base_roll`.

**Files read:**
- The persona `style.md`.
- The target plan, all lines; SHA-256 verified as `afd65538…3c00`.
- From the context list: parts of the spec (Sections 2.8, 3.4–3.5, 4, 6, 7), `README.md`, `pyproject.toml`, `src/tome/tables.py`, `tests/test_tome_core.py` (test count), and read-only `git grep` / `git status` over `src/` and `tests/`.

**Limitations:**
- I did not read `validate_egm.py` or the `ARTIFICE_ROOT` path, because both are outside the permitted context.
- I ran no tests or Python code, so the Pydantic behaviour claims and the `concurrent.futures.CancelledError` subclass claim were not re-run.
- I did not inspect git history for `AGENTS.md`.
