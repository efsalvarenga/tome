# EGM Stage 9 Round 6: Reviewer Reports

**Date:** 2026-11-18
**Target:** [Implementation plan](../../../../plans/001_tome_core_architecture_plan.md), Detailed Implementation Plan, lines 15-508
**Target SHA-256:** `5ab721dd7e7a20d0c7bebcd22e58c4426bf43f7f3bd4063b650c41fc6b7a5281`
**Specification:** [Spec 001, version 1.1.2](../../../../designs/001_tome_core_architecture.md)
**Additional context:** `src/`, `tests/`, `pyproject.toml`, `AGENTS.md`, `README.md`
**Execution:** Three separate, fresh general-purpose task contexts using the installed official personas; earlier findings were not supplied
**Loop position:** First round past the five-round cap, at the human's request

| Reviewer | Standard | Status | Findings |
| :--- | :--- | :--- | :--- |
| `implementation_readiness` | `implementation-readiness-standard` | Completed | 0 Blocker, 0 Major, 4 Nit |
| `codebase_details` | `implementation-readiness-standard` | Completed | 0 Blocker, 1 Major, 1 Nit |
| `style` | Official style persona | Completed | 0 Blocker, 1 Major, 8 Nit |

No reviewer failed or required a retry.
The reports below are the reviewers' output, preserved without editing.

## Implementation Readiness: Complete Report

Status: completed

**Verdict:** The plan is ready to implement. I found no Blockers and no Majors. I could carry out Phases 0–5 from the plan and the specification without making any design or architectural choice. Each phase ends at a stable state checked by `./scripts/lint.sh`. The file boundary lists exact paths, every file has concrete steps, and every Section 7 bullet maps to named tests. I found no plan instruction that would make an implementation break the specification, apart from the deliberate, human-confirmed narrowing in D12. The four Nits below are test-plan gaps: a wrong implementation could still pass the listed tests.

**implementation_readiness-6-1 — Nit**
- **Where:** Line 475 (the "Callback boundary (D10 to D12)" row), against D12 at line 53 and the runner's error handling at lines 377–381.
- **Hurdle:** D12 requires a callback's `RunError`, `RecursionError` and `SystemError` to be converted to that callback's error type. The runner's outer handler is the opposite: it re-raises exactly those exceptions unchanged.
  - An implementer who reuses the outer handler pattern at the callback site would get this wrong.
  - All listed tests (`ValueError`, `MemoryError`, `KeyboardInterrupt`, cancellation) would still pass.
- **Guidance:** Extend `test_callback_exceptions_wrapped` to cover three more cases:
  - A callback that raises `InvalidProposalError` gives `PeerReviewError` when raised from `peer_reviewer`.
  - A callback's `RecursionError` gives that callback's error type, chained with `__cause__`.
  - A callback's `SystemError` behaves the same way.

**implementation_readiness-6-2 — Nit**
- **Where:** Line 55 (D14) and line 464 (`test_run_accepts_mapping_and_model`).
- **Hurdle:** D14 says any request that is neither a `Mapping` nor a `RunRequest` instance, including a JSON string, raises `InvalidRunRequestError`. No test asserts this. An implementation that falls back to `model_validate_json` for strings would go undetected.
- **Guidance:** Add cases to the run-level request test: a JSON string, a `list`, and `None` as `request` each raise `InvalidRunRequestError` with no callback calls.

**implementation_readiness-6-3 — Nit**
- **Where:** Lines 455, 462 and 471.
- **Hurdle:** Two Section 7 sub-assertions have no stated test. The plan says every bullet is mapped, so the implementer would have to decide the missing assertions.
  - **Historical Canon Grounding:** the spec says a configured umpire review may reject a shift that cites a historical fact, and without that callback the mechanically valid shift remains. Line 455 omits both.
  - **Umpire Failure Resolution:** the spec says a suitable argument may be used directly. Lines 462 and 471 cover only restated and null-source decisions. Line 462's "valid" case does not say it is the direct-use case.
- **Guidance:**
  - Line 455: add that a shift citing "Actor A has capability X" is kept by `validate_peer_evaluation` and can still be rejected by `apply_umpire_rejections`.
  - Line 462: define the "valid" case as a statement equal to the source peer's `public_argument`, which is accepted and stored verbatim.

**implementation_readiness-6-4 — Nit**
- **Where:** Line 463, and line 464's "no `random.Random` constructed" check, against lines 353 and 375.
- **Hurdle:** The plan does not say what the `monkeypatch` spy targets, and the runner's import of `random` is only implied by `random.Random(...)`.
  - If the runner uses `from random import Random`, a spy on `random.Random` never fires.
  - The "not constructed" assertions would then pass vacuously.
- **Guidance:**
  - At line 375, state that `runner.py` uses `import random` and calls `random.Random`.
  - At line 463, state the spy target: `monkeypatch.setattr(tome.engine.runner.random, "Random", spy)`.
  - Add a positive control: a valid run calls the spy exactly once.

**Files read:**
- The persona (`implementation_readiness.md`) and the assigned standard (`implementation-readiness-standard.md`).
- The target plan, all 508 lines; its SHA-256 matched `5ab721dd…5281`.
- The specification, all 1,140 lines.
- `pyproject.toml`, `README.md`, and `src/tome/__init__.py`.
- Import lines from the other legacy `src/tome/*.py` files and the first lines of `tests/test_tome_core.py`.
- `AGENTS.md`, as supplied in the instructions.
- I did not read docs/reviews/, session artifacts, or other reviewers' results.

**Limitations:**
- I did not run or test anything, so the Starting Baseline claims are taken as stated. These include the Pydantic 2.14.3 behaviours, the golden-vector and seed-20 draw values, the Hatchling editable install, and Ruff 0.17.5 checking Markdown.
- I checked the Phase 5 `git grep` count of 9 legacy imports against the import lines only, not by running it.
- I could not confirm that the line 494 file-boundary check passes. It depends on what has been committed since `7d3fef1` under `docs/reviews/`, which I may not read, outside the `implementation_readiness/` exception.

## Codebase Details: Complete Report

Status: completed

**Codebase Details Goldfish, round 6, Mode: REVIEW**

- **Target:** `docs/plans/001_tome_core_architecture_plan.md`, lines 15–508. Lines 1–14 were read for context only.
- **SHA-256:** `5ab721dd7e7a20d0c7bebcd22e58c4426bf43f7f3bd4063b650c41fc6b7a5281`. The file on disk matches it.
- **Standard:** Implementation Readiness Standard.

### Findings

**codebase_details-6-1. Severity: Major.**

- **Plan lines:** 29, 70, 107, 113, 176, 180.
- **Other files:** `pyproject.toml` lines 22–24.
- **Problem:** The Ruff format gate may fail on Markdown that Phase 0 adds, and the plan gives no instruction for that case.
  - Line 180 says the repository has no `python`-fenced Markdown "at `7d3fef1`". That claim covers only the files that existed at that commit.
  - Phase 0 step 0 (line 107) requires committing new Markdown files before the gate runs. These are the plan itself and the review records under `docs/reviews/001_tome_core_architecture_egm/implementation_readiness/`.
  - The gate at step 6 (line 113) then runs `ruff format --check .` across the whole repository (line 176).
  - Line 29 and line 180 say the locked Ruff also checks `python`-fenced code in Markdown.
  - `pyproject.toml` has no Ruff `exclude` or `extend-exclude` (lines 22–24). `scripts/lint.sh` does not restrict paths either.
- **Why it matters:** If any review record contains a `python` block that Ruff would reformat, Phase 0 fails. The implementer cannot fix it inside the File Boundary, because line 70 allows those records to change only through the EGM workflow.
  - The plan gives a "stop and raise" rule only for a build failure (line 179).
  - This leaves a decision to the implementer: either restrict the paths passed to `ruff format`, or stop.
- **What I verified:**
  - The plan has no code fences at all.
  - `README.md`, `AGENTS.md` and the spec have only `text`, `json` and `bash` fences.
  - Per the persona, I did not read `docs/reviews/`.
- **Secondary point:** Line 180's "(see Starting Baseline)" cross-reference is wrong. Starting Baseline (lines 19–35) never records the absence of `python` fences. Line 29 records only Ruff's Markdown behaviour.

**codebase_details-6-2. Severity: Nit.**

- **Plan lines:** 75, 179, 490.
- **Other files:** `pyproject.toml` lines 18–20.
- **Problem:** The build backend is not version-locked, so the gate is less reproducible than line 75 suggests.
  - `[build-system] requires = ["hatchling"]` has no version pin.
  - `uv.lock` does not pin build-system requirements.
  - So every `uv sync --locked` / `uv run --locked` editable build can resolve a different Hatchling version. Line 75 says `uv.lock` gives "Reproducible dependency versions for the gate".
- **Mitigation:** Line 179's stop-and-raise rule covers a build failure. A sentence saying that Hatchling is deliberately left unpinned would remove the ambiguity.

### Verified with no discrepancy

**Repository state (lines 19–35)**
- Branch is `feat/trio-engine-1.1` and HEAD is `7d3fef1`.
- There is no `uv.lock`, `.python-version`, `scripts/` or `.github/`.
- The legacy code has the features the plan names:
  - step dice: `dice.get_posture_die_sides`
  - traits and exhausted traits
  - outcome bands: `validator.py` lines 120–123
  - `active_rumors`
  - urgency ordering: `runner.sort_factions_by_urgency`
- `tests/test_tome_core.py` contains exactly 8 tests.
- `tables.py` has five `TABLE_*` tables, no imports, and 36 keys (11–66) per table. Every value is a non-blank, unique string.
- Default `python3` is 3.9.6. `python3.11`, `uv` and `uvx` are installed.
- The `validate_egm.py` path exists and is executable.

**Configuration**
- `pyproject.toml` has:
  - `pydantic>=2.0.0`
  - a `dev` extra with pytest and Ruff, so `--extra dev` is correct
  - the Hatchling build backend
  - Ruff with `py311` and line length 100
  - pytest with `testpaths=["tests"]`, `test_*.py`, and no `pythonpath` or `addopts`. So the default `prepend` import mode applies, `tests/support.py` is importable and not collected, and `tests/__init__.py` does not exist.
- `src/tome/__init__.py` has a docstring and `__version__ = "0.1.0"`.

**Documentation sections the plan edits**
- `README.md` contains every section and entry the plan says it will edit: Status block, Prerequisites, Setup steps, "Running the Test Suite", "Formatting & Static Analysis", and the project-structure comments.
- `AGENTS.md` has Section 3. The `docs/plans/` convention exists only as an uncommitted change, which the Phase 0 precondition covers.

**Phase 5**
- I ran the Phase 5 `git grep` at the current state. It returns exactly the 9 legacy imports the plan states, including `tests/test_tome_core.py:293`.
- The deletion list is complete:
  - only the four legacy modules and the test file use the legacy modules
  - `tables.py` is correctly kept
  - stale `__pycache__` files cannot be imported
- New paths such as `tome.engine.runner` do not match the pattern.

**New files and APIs**
- `src/tome/engine/` has no name collisions.
- The re-exported names do not shadow the legacy submodules.
- The import order between modules has no cycles.
- The protocol signatures match Spec Section 3.5.
- The `override_tables` format matches the Spec Section 3.4 example.
- There is no missed reuse. `validator.sanitize_anchor_string` is legacy, is deleted in Phase 5, and differs from Section 3.0 on the one-character quote case.

### Files read

- The plan (full)
- The persona and the standard
- `pyproject.toml`, `.gitignore`, `README.md`, `AGENTS.md` (plus its working-tree diff)
- `src/tome/__init__.py`, `models.py`, `dice.py`
- `runner.py` lines 1–60, `validator.py` lines 1–20 and grep results
- `tables.py` (headers and grep, and a parse of its literals)
- Import and def lines of `tests/test_tome_core.py`
- Spec sections 2.0–2.4, 3.4 (example) and 3.5, plus targeted greps of the spec

### Limitations

- As instructed, I did not run tests, Ruff or uv.
- I could not verify these claims: Pydantic 2.14.3 behaviour, Ruff 0.17.5 Markdown formatting, the golden-vector draw values, the legacy tests passing, the Hatchling editable build, and `validate_egm.py` exiting 0.
- I did not read `docs/reviews/`, so I could not confirm whether those records contain `python` fences (finding codebase_details-6-1).

## Style: Complete Report

Status: completed

### Style Goldfish review, round 6

**Scope:** `docs/plans/001_tome_core_architecture_plan.md`, lines 15–508. The file's SHA-256 matched `5ab721dd…7a5281`.

**One sentence per line:** I checked every prose line in the range, leaving out tables, code and headings. No line holds more than one sentence.

**Checks that passed:** These counts and cross-references are consistent:
- 15 models.
- Eight engine files.
- Five legacy files and four legacy modules.
- Seven error codes.
- 30 combinations of tier and table pair.
- References to Target Files 8, 10 and 13.
- Every Section 7 bullet appears in the traceability table.
- The 9 lines that the legacy-import search matches at `7d3fef1`.
- The claim that `\b` fails silently in Apple's `git grep -E`.
- The 8 legacy tests.
- The spec's worked-example table entries.

### Findings

**style-6-1 — Major — lines 53 and 61–64 (CALIBRATE)**
- **Wording:** "D12 narrows six specification passages that say any callback failure or cancellation raises a typed error: …"
- **Problem:** At least two more spec passages say callback failures raise typed errors, and D12 also narrows them:
  - Edge Case 11: "A configured review callback that fails or returns invalid decisions raises `UmpireReviewError`".
  - Invariant 15: "proposal generation, … peer review, umpire review, umpire failure resolution … raise their corresponding `RunError` type".
- **Consequence:** The record of an author-confirmed deviation from the approved spec understates how far it reaches. Line 64's "future specification revision" would leave those passages out of line with D12.
- **Action:** Add Edge Case 11 and Invariant 15 to both lists and change "six" to "eight". Alternatively, replace "six specification passages … :" with "specification passages, including …".

**style-6-2 — Nit — line 62 (CALIBRATE)**
- **Wording:** "`MemoryError` propagates because Section 2.8 states that memory exhaustion … must not be relabelled as `MechanicsError`".
- **Problem 1:** D12 wraps callback exceptions into callback error types, never into `MechanicsError`, so the relabelling clause does not support D12.
- **Problem 2:** The same Section 2.8 sentence also names "interpreter failure". D13 (line 54) cites that phrase to exempt `RecursionError` and `SystemError`, yet line 62 wraps them when a callback raises them. The stated reason does not account for this difference.
- **Action:** Delete "and must not be relabelled as `MechanicsError`". Add one sentence saying that the different handling of callback and engine-raised `RecursionError`/`SystemError` is an intentional author decision.

**style-6-3 — Nit — line 28 (forward reference)**
- **Wording:** "the three gate commands passed".
- **Problem:** The gate commands are first listed at Target File 3, about 150 lines later. A reader of the Starting Baseline cannot yet tell which three commands are meant.
- **Action:** Replace with "the three `scripts/lint.sh` commands (Target File 3) passed".

**style-6-4 — Nit — line 180 (CALIBRATE)**
- **Wording:** "it does not edit files or check prose and other fence languages, and the repository has no `python`-fenced Markdown at `7d3fef1` (see Starting Baseline)".
- **Problem 1:** The Starting Baseline (line 29) records only that Ruff checks `python` fences and does not edit files. It does not record the absence of `python` fences, so the cross-reference points to nothing.
- **Problem 2:** "does not check … other fence languages" is a claim about tool behaviour with no recorded evidence. The claim that no `python` fences exist is true; I confirmed it by reading the tracked Markdown.
- **Action:** Either add a Starting Baseline bullet stating that tracked Markdown at `7d3fef1` has no `python` fences, or drop "(see Starting Baseline)". Narrow the negative claim to "does not edit files".

**style-6-5 — Nit — line 148 (CALIBRATE)**
- **Wording:** "Before Phase 5 it reports the 9 legacy imports in `src/tome/` and `tests/`, which confirms that it works."
- **Problem:** The count was measured at `7d3fef1`. "Before Phase 5" also covers Phases 1–4, where new files exist that were never measured. The search also counts matching lines, not imports: line 8 of `runner.py` starts a multi-line import.
- **Action:** Replace with "At `7d3fef1` it reports 9 matching legacy import lines in `src/tome/` and `tests/`, which confirms that it works."

**style-6-6 — Nit — line 166 (DROP)**
- **Wording:** "Refresh it with `uv lock` only when `pyproject.toml` dependencies change."
- **Problem:** Under the File Boundary and D16, `pyproject.toml` cannot change during this plan, so the implementer never reaches this decision. The lasting convention is already recorded in the `AGENTS.md` bullet (Target File 5).
- **Action:** Delete the sentence.

**style-6-7 — Nit — line 242 (two readings)**
- **Wording:** "`ErrorCode = Literal[...]` with the seven codes from `errors.py`."
- **Problem:** "from `errors.py`" can be read as importing or deriving the codes from that module. That would create a circular import, which line 216 forbids ("`models.py` never imports `errors.py`").
- **Action:** Replace with "with the seven `code` strings from the Target File 6 table, written as literals".

**style-6-8 — Nit — line 327 (notation that fails if copied)**
- **Wording:** "record `UmpireRejectionRecord(voter_actor_id, reason, evaluation_before_reversion=…)`".
- **Problem:** Pydantic models accept keyword arguments only. If an implementer copies this call as written, it raises `TypeError`.
- **Action:** Write `UmpireRejectionRecord(voter_actor_id=…, reason=…, evaluation_before_reversion=…)`.

**style-6-9 — Nit — line 414 (incomplete list)**
- **Wording:** "Peer: `baseline_plausibility` 0, `final_vote` 0, flag `False`, anchor `None`, argument …".
- **Problem:** This lists five of the six `PeerEvaluation` fields and leaves out `voter_actor_id`. The Proposal and Failure defaults list every field, so this one leaves a choice open.
- **Action:** Add "`voter_actor_id` `voter_actor.id`," at the start of the list.

### Files read

- The style persona: `.../elephant-goldfish-model/agents/style.md`.
- The target plan, lines 1–508.
- `docs/designs/001_tome_core_architecture.md`: Sections 2.8, 3.4 (worked-example tables), 3.5, 4 (Invariants 14 and 15), 6 and 7.
- `README.md`, lines 84–145.
- `AGENTS.md`, both the committed version at `7d3fef1` and the working-tree version, for the `docs/plans` line.
- `pyproject.toml`.
- `src/tome/__init__.py`, the head and `TABLE_*` names of `src/tome/tables.py`, and keyword searches of the legacy `src/tome/*.py` files.
- `tests/test_tome_core.py`, for the test count and legacy imports.

### Limitations

- I did not run Ruff, `uv` or pytest. Claims about Ruff and Pydantic behaviour were checked only against the plan's own Starting Baseline.
- I ran `git grep` (read-only) to confirm the 9 matching lines and the `\b` behaviour.
- I did not read `docs/reviews/`.
- The working-tree `AGENTS.md` has uncommitted changes. The `docs/plans` convention is not present at `7d3fef1`, which is consistent with the Phase 0 precondition.
