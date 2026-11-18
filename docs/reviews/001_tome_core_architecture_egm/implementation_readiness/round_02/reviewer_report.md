# EGM Stage 9 Round 2: Reviewer Reports

**Date:** 2026-11-18
**Target:** [Implementation plan](../../../../plans/001_tome_core_architecture_plan.md), Detailed Implementation Plan, lines 15-491
**Target SHA-256:** `6c28bf0617aabdd989d4de1e3ef237e9bf474aa0bdbbf50f9256b7241713631b`
**Specification:** [Spec 001, version 1.1.2](../../../../designs/001_tome_core_architecture.md)
**Additional context:** `src/`, `tests/`, `pyproject.toml`, `AGENTS.md`, `README.md`
**Execution:** Three separate, fresh general-purpose task contexts using the installed official personas; round-one findings were not supplied

| Reviewer | Standard | Status | Findings |
| :--- | :--- | :--- | :--- |
| `implementation_readiness` | `implementation-readiness-standard` | Completed | 0 Blocker, 0 Major, 4 Nit |
| `codebase_details` | `implementation-readiness-standard` | Completed | 0 Blocker, 1 Major, 2 Nit |
| `style` | Official style persona | Completed | 0 Blocker, 3 Major, 9 Nit |

No reviewer failed or required a retry.
The reports below are the reviewers' output, preserved without editing.

## Implementation Readiness: Complete Report

Status: completed

**Verdict:** I found no Blockers and no Majors. I could implement every phase without making a design or architectural choice. The findings below are four Nits.

Target checked: `docs/plans/001_tome_core_architecture_plan.md`, lines 15–491. The SHA-256 matches `6c28bf06…3631b`.

**What I checked**
- **File boundary:** it lists exact paths and phases, and the Phase 5 legacy-file deletions are explicit.
- **Phase checkpoints:** every phase ends with `./scripts/lint.sh` exiting 0, and the module import order works phase by phase (`text` → `models` → `errors` → `mechanics` → `gates` → `runner`).
- **Spec coverage:** I traced every Spec Section 7 bullet, Invariants 1–18, Edge Cases 1–17 and the Section 3.5 check order to a file, a step and a test.
- **Phase 5 legacy-import search:** the `git grep` pattern currently returns exactly the 9 legacy import lines the plan predicts.

**Findings**

**implementation_readiness-2-1: Nit.** Lines 395–404, `tests/support.py`, `ScriptedCallbacks` and `seed_for_base_roll`.
- **Hurdle:** the helper's interface is not defined:
  - the attribute names that hold recorded calls, and the shape of each record;
  - how a test replaces a default (constructor keyword, attribute assignment, or something else);
  - the `argument` text of the default supporting pro;
  - what `seed_for_base_roll` does if no seed from 0 to 9,999 matches.
- **Impact:** this is test-only code, but every Phase 4 test depends on it, so the implementer must design it.
- **Guidance:**
  - Specify the constructor (for example `ScriptedCallbacks(proposal=None, peer=None, umpire=None, failure=None)`, each an optional function with the matching protocol signature).
  - Name the recorded-call lists (for example `.proposal_calls`, each entry a tuple of positional arguments).
  - Fix the default pro `argument` string.
  - State that `seed_for_base_roll` raises `AssertionError` when no seed matches.

**implementation_readiness-2-2: Nit.** Lines 112–115 versus 118, Phase 0 steps 3 and 7.
- **Hurdle:** step 3 says to commit `uv.lock` and put the Pydantic version in "the commit message body". Step 7 gives a separate commit subject. It is unclear whether this is one commit or two, and if two, what the step-3 subject is.
- **Guidance:** say "stage `uv.lock`; the step 7 commit body records the locked Pydantic version", or give the step-3 commit its own subject.

**implementation_readiness-2-3: Nit.** Line 51, D13; lines 314–316, runner error handling.
- **Concrete consequence:** under D13, a `RecursionError` (stack exhaustion) or `SystemError` (internal interpreter error) raised in engine code becomes `MechanicsError`.
- **Spec conflict:** Spec Section 2.8 says memory exhaustion and interpreter failure "must not be relabelled as the internal-defect-only MechanicsError". Only `MemoryError` is carved out.
- **Scope:** D13 is labelled an interpretation and invites challenge, so this is a challenge to D13, not to D12.
- **Guidance:** either add `RecursionError` and `SystemError` to the re-raise tuple in D13 and the runner handler (plus a test), or state that D13 deliberately treats them as engine defects.

**implementation_readiness-2-4: Nit.** Lines 430–466, traceability table. Four Spec Section 7 assertions are not assigned to any test:
- **Run-level RNG check:** the spec says table-source selection must not consume RNG draws. `test_spark_table_source_and_tags` (line 450) does not compare a seeded default-table run with a seeded override run. The runner's order (tables chosen before the generator exists) satisfies this by construction, but nothing tests it end to end.
- **No dice on a canon-duplicate proposal:** the spec says rejection happens "before any peer review or resolution dice". `test_new_proposal_rejected_before_peers_and_dice` (line 452) only asserts there are no peer calls.
- **Upward-shift rejection:** the spec requires rejecting a correctly cited upward or downward shift. `test_umpire_rejection_reverts_and_records` (line 444) names only the downward vector (baseline 1, final 0).
- **Restated consequence in the audit record:** the spec says restatements preserve the original argument and source in the record. No run-level test checks that `peer_evaluations[*].public_argument` keeps the original text while canon gets the restated text.
- **Guidance:** add these assertions to the named tests. Examples: compare `posture_roll`, table-name prefixes and `resolution_roll` across default and override runs with the same seed; spy on `mechanics.roll_resolution`; add a baseline −1 to final 0 rejection case; check the record after a restated failure.

**Files read**
- The persona and the implementation-readiness standard.
- The plan: lines 1–491 in full.
- The specification `docs/designs/001_tome_core_architecture.md`: lines 1–1124. I did not read the tail of Section 8 (Goldfish review history).
- `pyproject.toml` and `README.md` in full.
- `src/tome/`: the file list, `__init__.py`, the head and table names of `tables.py`, and the import lines of all modules.
- `tests/test_tome_core.py`: its import lines and the start of the file.
- `AGENTS.md`: from the repository conventions supplied with this session; I did not open the file on disk.

**Limitations**
- I ran no tests or code, as instructed. The Pydantic behaviours the plan says it probe-verified, and the worked-example draws for seed 20 (posture 6, tables Focus then Method, keys 66 and 13, base roll 7), are therefore unverified. The plan relies on the spec for the seed-20 draws and does not say they were verified the way the seed-42 and seed-4 golden vectors are.
- I ran a few read-only git queries outside the listed files: `git log`, `git status`, `git ls-files`, `git check-ignore .venv`, and the Phase 5 `git grep` pattern. I did not open `.gitignore`. I did not read `docs/reviews/`, session artifacts, or other reviewers' output.

## Codebase Details: Complete Report

Status: completed

**Target:** `docs/plans/001_tome_core_architecture_plan.md`, lines 15–491. The SHA-256 matches `6c28bf06…1631b`. Mode was REVIEW, against the Implementation Readiness Standard.

### Findings

**codebase_details-2-1 — Major**
- **Where:** plan line 23, the Starting Baseline reproduction command. Related files: `pyproject.toml:26-28`, `tests/test_tome_core.py:1-3,293`, and the `src/` layout.
- **Problem:** the configuration does not support the stated command `uv run --isolated --no-project … python -m pytest`.
  - `--no-project` does not install `tome`.
  - `[tool.pytest.ini_options]` sets only `testpaths` and `python_files`. It has no `pythonpath = ["src"]` and no import-mode setting.
  - `tests/` has no `__init__.py` or `conftest.py`.
  - So `sys.path` gets only the repository root (from `-m`) and `tests/` (from prepend mode). Neither contains `tome`, which lives in `src/tome/`.
  - `from tome.dice import …` at `tests/test_tome_core.py:1` would therefore fail at collection with `ModuleNotFoundError`, unless something unrecorded, such as `PYTHONPATH=src`, was set.
- **Fix:** record the full environment actually used, or reword the line.
- **Scope:** the Phase 0+ gate is not affected. `uv run --locked --extra dev` installs the project editable through hatchling.
- **Severity note:** I graded this Major because I could not run the command to confirm it. If confirmed, it is a contradiction with the code and should be a Blocker.

**codebase_details-2-2 — Nit**
- **Where:** plan line 184, the Phase 5 README project-structure edit. Related file: `README.md:95`.
- **Problem:** the edit lists what to add, remove and keep, but does not say what happens to the existing `src/tome/__init__.py` entry. That entry's comment is "Package entry point and version", but after Phase 4 the file also re-exports the public API.
- **Related wording mismatch:** lines 178–179 say "Testing and formatting". In `README.md` these are two separate headings, "Running the Test Suite" (line 131) and "Formatting & Static Analysis" (line 137). The plan does not say whether to merge them.
- These are small choices left to the implementer, which the zero-decision rule does not allow.

**codebase_details-2-3 — Nit**
- **Where:** plan lines 141–145, the Phase 5 `git grep`.
- **Problem:** the pattern checks one line at a time. It does not catch:
  - `from . import models` (or `dice`, `validator`, `runner`) in `src/tome/__init__.py`;
  - module names on later lines of a multi-line `from tome import (` block.
- **Impact:** low. Either form would fail at import after the deletions, so the pytest gate would catch it. The grep alone is not a complete check, though.

### Verified as accurate
- **Branch and commit:** branch `feat/trio-engine-1.1`, HEAD `7d3fef1`.
- **Legacy design features exist:**
  - d4/d6/d8 posture dice in `dice.py`;
  - `traits` and `exhausted_traits`;
  - outcome bands in `apply_adjudication_outcome`;
  - `active_rumors`;
  - `sort_factions_by_urgency`.
- **Legacy test file:** has exactly 8 tests.
- **`tables.py`:** five tables of 36 entries each, keys 11–66, no imports. The spec (line 124) names this file as `trio-d66-v1`.
- **`pyproject.toml`:**
  - dependency `pydantic>=2.0.0`;
  - `dev` extra with pytest and ruff;
  - build backend is hatchling, and `src/tome` matches the project name;
  - Ruff `py311`, line length 100, default rule set;
  - pytest settings as quoted above.
- **Environment:** default `python3` is 3.9.6; `python3.11` and `uv` are installed; `validate_egm.py` is at the stated path.
- **Absent files, as the plan says:** no `uv.lock`, `.python-version`, `scripts/`, CI workflow, `.venv`, or `tests/__init__.py`.
- **`.gitignore`:** ignores `.venv/` and does not ignore any planned file.
- **Phase 5 grep:** returns exactly 9 matches today, as claimed.
- **Deletion list:** complete; no other tracked file outside the README references the legacy modules.
- **README and AGENTS.md sections the plan edits:** all exist (README Status, Prerequisites, Setup commands, test and ruff instructions, Project Structure; AGENTS.md Section 3).
- **`src/tome/__init__.py`:** holds a docstring and `__version__ = "0.1.0"`.
- **Planned engine:** the subpackage layout, absolute imports, import order and Python 3.11 features all fit the existing package and tool settings. The engine has no name clashes with the legacy submodules.
- **Reuse:** nothing in the legacy code should be reused that the plan misses. `sanitize_anchor_string` is legacy and is deleted.

### Files read
- The persona and the standard.
- The plan, in full.
- The spec: selected sections (lines 1028–1112) plus targeted greps.
- `src/tome/__init__.py`, `dice.py`, `models.py`, `runner.py`, `tables.py` and `validator.py`.
- `tests/test_tome_core.py`: imports and test signatures, via grep.
- `pyproject.toml`, `README.md`, `.gitignore`, and the uncommitted `AGENTS.md` diff.
- Directory listings.

### Limitations
- I did not run tests, Ruff, `uv` or the validator, so these were not checked:
  - the Pydantic 2.14.3 and pass/fail baseline claims;
  - pytest's default import mode under the version `uv lock` will choose;
  - whether the validator runs on Python 3.9.
- `AGENTS.md` currently has an uncommitted change that adds the `docs/plans/` convention. The plan treats committing it as a Phase 0 precondition.

## Style: Complete Report

Status: completed

Target hash matched `6c28bf06…713631b`. I reviewed lines 15–491 in Mode: REVIEW against the style persona rubric.

**style-2-1 — Major — lines 104–105 and 109**
- Wording: "Run `uv lock` and commit the resulting `uv.lock`." / "Record the locked Pydantic version in the commit message body." / "Commit: `build(tooling): add locked uv verification gate`."
- Consequence: an implementer can read Phase 0 as having one commit or two. "the commit message body" could mean either commit, so the record of the locked Pydantic version could land in the wrong commit.
- Action: In step 3, change "commit" to "stage". In step 7, state that the single Phase 0 commit body records the locked Pydantic version. If two commits are intended, give step 3 its own commit message instead.

**style-2-2 — Major — line 270, CALIBRATE**
- Wording: "`model_dump(mode="json")` serializes `SparkTable` keys as decimal strings (… the Phase 1 tests re-check this behaviour on the locked version)."
- Consequence: no Phase 1 row in the traceability table (lines 423–430) checks JSON serialization of `SparkTable` keys. `RunResult` has no spark tables, so the Phase 4 worked-example test does not check it either. The promised re-check would not happen.
- Action: Name the assertion in a Phase 1 row, for example in `test_spark_tables_validation`. Otherwise, remove the re-check clause.

**style-2-3 — Major — lines 56–57 (and the D12 Source cell), CALIBRATE**
- Wording: "D12 departs from Edge Case 6…" and "…reads a keyboard interrupt as forced termination."
- Consequence: D12 and the row at line 460 let `asyncio.CancelledError` propagate. Spec Section 3.5 says a "callback failure/cancellation" raises `UmpireReviewError` or `UmpireResolutionError`, so D12 also narrows Section 3.5, not only Edge Case 6. The stated reason covers keyboard interrupts but not `asyncio.CancelledError` or other non-`Exception` errors. The header exception at line 13 therefore covers less than the plan actually departs from.
- Action: List every spec passage D12 narrows, including both Section 3.5 cancellation sentences. Give the reason for each case that propagates unchanged.

**style-2-4 — Nit — lines 227, 258, 270, CALIBRATE/RELOCATE**
- Wording: "probe-verified on Pydantic 2.14.3" appears three times.
- Consequence: the Starting Baseline (lines 19–27) lists measured facts but records no probe command, date or commit. A reader cannot trace the evidence, and the repeated caveat adds noise.
- Action: Move the three probe results into the Starting Baseline with their method. At each site, keep only the reference to the test that re-checks the behaviour.

**style-2-5 — Nit — lines 54–55, CALIBRATE + DROP**
- Wording: "do not add behaviour to the contract" / "the implementation-readiness review should challenge them…"
- Consequence: D13 and D14 do define behaviour that the spec leaves open, so the first sentence conflicts with "fix choices". The second clause tells reviewers what to do, gives the implementer no decision, and goes stale once the plan is approved.
- Action: Reword to "…fix choices the specification leaves open and change no behaviour it defines". Drop the reviewer clause.

**style-2-6 — Nit — lines 64, 101, 477**
- Wording: the same records are called "its review records under `…/implementation_readiness/`", "its Stage 9 review records" and "the documents named in the File Boundary exception". Line 64 does not call itself an exception, and it names a directory rather than documents.
- Action: Use one term and one path at all three sites.

**style-2-7 — Nit — line 180**
- Wording: "`pip` users can … run the three gate commands directly."
- Consequence: the gate commands (lines 169–171) start with `uv run --locked`, which `pip` users cannot run.
- Action: Spell out the commands without `uv`: `ruff check .`, `ruff format --check .`, `pytest`.

**style-2-8 — Nit — lines 181 and 183**
- Wording: "removed in Phase 5" and "the Section 7 test suite".
- Consequence: these terms belong to the plan and the spec, and README readers will not know them.
- Action: Use "to be removed" and "the specification's Section 7 tests", linking the spec.

**style-2-9 — Nit — line 235**
- Wording: "`for tens in 1..6 for units in 1..6`"
- Consequence: this is not Python inside a code span. It could be translated to `range(1, 6)`, which would build 25 keys instead of 36.
- Action: Write `range(1, 7)`.

**style-2-10 — Nit — line 377, CALIBRATE**
- Wording: "Do not use star imports or a computed `__all__`, which fails Ruff F401."
- Consequence: Ruff reports star imports as F403/F405, not F401.
- Action: Change to "which Ruff reports as F403 or F401".

**style-2-11 — Nit — lines 347, 351, 355, 401, 456**
- Wording: the runner passes `turn_number` (`state.turn_index + 1`), while the protocols and the default at line 401 use `turn_index` (`f"Consequence {turn_index}."`).
- Consequence: a reader can confuse that parameter with `state.turn_index`, which is one lower.
- Action: At line 401, state that the parameter holds `world_state.turn_index + 1`, or use one name throughout.

**style-2-12 — Nit — lines 429, 436, 461**
- Wording: "Explicit failure types", "Spark table identity", "Explicit failure types (run)".
- Consequence: the column header says rows come from a Section 7 bullet, an invariant or a plan decision. These labels name no source, so a reader cannot check the claim "every Spec Section 7 bullet appears".
- Action: Prefix each with its source, for example "Invariant 15 (Explicit Failure Types)" and "D8 (default table identity)".

**Checked and calibrated (not reported):**
- **Counts:** 8 legacy tests, 9 legacy imports (confirmed by running the line 141 `git grep`), 5 legacy files, 4 legacy modules, 8 engine files, 15 models, 7 error subclasses, 4 protocols, 30 tier/pair combinations.
- **Cross-references:** D1–D17 and every Invariant, Edge Case and Section 7 label cited.
- **Other claims:** the `\b` claim at line 142 (confirmed: `git grep -E '\b…'` matches nothing); `tables.py` has no imports.
- **One sentence per line:** no violations in the prose.

**Files read:**
- The persona file `style.md`
- The target plan, lines 1–491
- `docs/designs/001_tome_core_architecture.md`: headings, Section 2.8, Section 3.5, Invariants, Edge Cases, Section 7
- `README.md`, `pyproject.toml`, `AGENTS.md` (committed version at 7d3fef1)
- Imports and test count in `src/tome/` and `tests/test_tome_core.py`
- Read-only git output (log, status, diff stat, grep)

**Limitations:** I ran no tests. The Pydantic 2.14.3 and Python 3.9 claims were not checked. I did not read docs/reviews/.
