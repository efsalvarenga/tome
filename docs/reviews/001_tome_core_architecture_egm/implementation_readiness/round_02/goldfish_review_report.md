# Goldfish Annotated Review Report: Stage 9 Round 2

**Status:** resolved
**Date:** 2026-11-18
**Target:** [Implementation plan](../../../../plans/001_tome_core_architecture_plan.md), Detailed Implementation Plan, lines 15-491
**Reviewed SHA-256:** `6c28bf0617aabdd989d4de1e3ef237e9bf474aa0bdbbf50f9256b7241713631b`
**Post-resolution SHA-256:** `afd65538a48727343205668a8c3fc6c5d9ce13ab176b508993535c417f5c3a00`
**Raw findings:** [Complete round-two reviewer reports](reviewer_report.md)
**Loop state:** [Stage 9 report](../implementation_readiness_report.md)

## Round Decision Before Edits

All three requested reviewers completed.
They reported 19 findings: 0 Blocker, 4 Major, and 15 Nit.
Round 2 is **not clean** because it contains unsettled Major findings.
Consecutive clean rounds: **0 of 2**.

All 19 findings are classified PROPOSE FIX, and every original severity is unchanged.
No finding is contested, escalated, or declined.
`style-2-3` touches D12, but it asks for a complete list of the specification passages D12 already narrows and a reason for each, not a change to D12's behaviour.
None of the findings is churn: none would be resolved by reverting a round-one edit.
`style-2-2` and `style-2-4` concern wording that round 1 added, but they ask for that wording to be completed, not removed.

The implementation-readiness reviewer found no Blocker or Major and reported that it could implement every phase without making a design choice.

The coordinator verified three runtime claims before classifying:

*   **`codebase_details-2-1` is confirmed.** The recorded baseline command, without `PYTHONPATH=src`, fails at test collection; with `PYTHONPATH=src`, all 8 legacy tests pass. The reviewer said a confirmed failure would be a Blocker, but graded it Major; the grade is unchanged here.
*   **`style-2-10` is partly wrong.** Under the repository's Ruff configuration, a star import in `__init__.py` or in a module passes; only a computed `__all__` fails, under F401. The proposed edit records that, rather than the reviewer's F403 wording, and keeps the ban on star imports for a stated reason.
*   **Seed-20 worked example.** `random.Random(20)` gives posture 6, tables Focus then Method, keys 66 and 13, and dice 5 and 2, matching the specification; this closes a limitation the readiness reviewer recorded.

## Findings by Severity

### Major

| Finding | Scope | Summary | Suggestion | Edit |
| :--- | :--- | :--- | :--- | :--- |
| `codebase_details-2-1` | Starting Baseline | Recorded baseline command omits `PYTHONPATH=src` and fails as written. | PROPOSE FIX | [F04](#f04) |
| `style-2-1` | Phase 0 steps 3 and 7 | One commit or two is ambiguous; the Pydantic-version record could land in the wrong commit. | PROPOSE FIX | [F01](#f01) |
| `style-2-2` | `models.py` JSON keys | The promised re-check of JSON key serialization has no test. | PROPOSE FIX | [F02](#f02) |
| `style-2-3` | D12 rationale and Source | D12 also narrows Section 3.5, Edge Case 14, and two Section 7 bullets, and the rationale omits `asyncio.CancelledError`. | PROPOSE FIX | [F03](#f03) |

### Nit

| Finding | Scope | Summary | Suggestion | Edit |
| :--- | :--- | :--- | :--- | :--- |
| `implementation_readiness-2-1` | `tests/support.py` | `ScriptedCallbacks` interface and `seed_for_base_roll` failure behaviour undefined. | PROPOSE FIX | [F10](#f10) |
| `implementation_readiness-2-2` | Phase 0 | Same as `style-2-1`. | PROPOSE FIX | [F01](#f01) |
| `implementation_readiness-2-3` | D13, runner handler | `RecursionError` and `SystemError` would be relabelled `MechanicsError`, which Section 2.8 forbids. | PROPOSE FIX | [F13](#f13) |
| `implementation_readiness-2-4` | Traceability | Four Section 7 assertions unassigned. | PROPOSE FIX | [F14](#f14) |
| `codebase_details-2-2` | README edits | The `__init__.py` tree comment and the two test and format headings are unaddressed. | PROPOSE FIX | [F07](#f07) |
| `codebase_details-2-3` | Phase 5 search | The line-based search misses `from . import models` and multi-line imports. | PROPOSE FIX | [F12](#f12) |
| `style-2-4` | Probe claims | Probe evidence has no recorded method, and the caveat is repeated three times. | PROPOSE FIX | [F04](#f04) |
| `style-2-5` | Interpretations paragraph | "Do not add behaviour" conflicts with D13 and D14; the reviewer-directed clause goes stale. | PROPOSE FIX | [F05](#f05) |
| `style-2-6` | Review-record exception | The same records are named three ways. | PROPOSE FIX | [F06](#f06) |
| `style-2-7` | README Prerequisites | `pip` users cannot run the `uv`-prefixed gate commands. | PROPOSE FIX | [F07](#f07) |
| `style-2-8` | README wording | "Phase 5" and "Section 7 test suite" are internal terms in user documentation. | PROPOSE FIX | [F07](#f07) |
| `style-2-9` | `D66_KEYS` | `1..6` could be translated to `range(1, 6)`. | PROPOSE FIX | [F08](#f08) |
| `style-2-10` | Export rule | Ruff rule attribution for star imports is wrong. | PROPOSE FIX, with corrected wording | [F09](#f09) |
| `style-2-11` | Callback `turn_index` | Parameter name can be confused with `state.turn_index`. | PROPOSE FIX | [F10](#f10) |
| `style-2-12` | Traceability labels | Three row labels name no source. | PROPOSE FIX | [F11](#f11) |

## Proposed Edit Groups

Line numbers refer to the reviewed plan revision.
No edit changes the specification, `src/`, `tests/`, or `pyproject.toml`.

### F01

**Findings:** `style-2-1`, `implementation_readiness-2-2`.

*   Phase 0 step 3: replace with "Run `uv lock` and stage the resulting `uv.lock`."
*   Phase 0 step 7: replace with "Commit all Phase 0 changes in one commit with subject `build(tooling): add locked uv verification gate`; its body records the Pydantic version that `uv.lock` resolved."

### F02

**Finding:** `style-2-2`.

*   Traceability, `Spark Table Defaults and Overrides (validation)` row: append "; `SparkTables.model_dump(mode="json")` serializes every table's keys as decimal strings `"11"` to `"66"`".

### F03

**Finding:** `style-2-3`.

*   D12 Source cell: replace "kept over the broader wording of Edge Case 6" with "kept over the broader wording of Section 3.5, Edge Cases 6 and 14, and the Section 7 Umpire Audit and Failure Resolver Errors bullets".
*   Replace the two D12 paragraph sentences beginning "D12 departs from Edge Case 6" and "The author kept D12" with:
    "D12 narrows five specification passages that say any callback failure or cancellation raises a typed error: Section 3.5 for the umpire review and the failure resolver, Edge Cases 6 and 14, and the Section 7 Umpire Audit and Errors and Failure Resolver Errors bullets."
    "`MemoryError` propagates because Section 2.8 states that memory exhaustion can prevent delivery of a typed `RunFailure` and must not be relabelled."
    "Exceptions that are not `Exception` subclasses propagate because Python reserves them for stopping or cancelling execution: wrapping `KeyboardInterrupt`, `SystemExit`, or `asyncio.CancelledError` would stop Ctrl+C, `sys.exit()`, and asyncio task cancellation from behaving normally."
    "The author confirmed this trade-off on 2026-11-17."
*   Change "A future specification revision should align Edge Case 6 with D12" to "A future specification revision should align those passages with D12".

### F04

**Findings:** `codebase_details-2-1`, `style-2-4`.

*   Starting Baseline, replace the reproduction bullet with:
    "Those tests were run with `PYTHONPATH=src uv run --isolated --no-project --python 3.11 --with 'pydantic>=2' --with 'pytest>=8' python -m pytest -p no:cacheprovider`, because no project environment exists yet; without `PYTHONPATH=src`, collection fails because `tome` is not importable."
    "Ruff was run as `uvx ruff check --no-cache .` and `uvx ruff format --no-cache --check .`."
*   Add a Starting Baseline bullet:
    "Pydantic behaviours this plan relies on were checked with throwaway scripts outside the repository, run by `uv run --isolated --no-project --python 3.11 --with 'pydantic>=2' python <script>`, which resolved Pydantic 2.14.3: an explicit `null` is rejected for a field annotated without `None`; nested model instances, including ones built with `model_construct`, are fully validated under `revalidate_instances="always"`; and `model_dump(mode="json")` writes integer dictionary keys as decimal strings."
    "The same method confirmed the Invariant 14 golden vectors and the Section 3.4 worked example: seed 20 gives posture 6, tables Focus then Method, keys 66 and 13, and dice 5 and 2."
*   Replace the three in-place qualifiers "(probe-verified on Pydantic 2.14.3; the Phase 1 tests re-check this behaviour on the locked version)" with "(see Starting Baseline; re-checked by a Phase 1 test)".

### F05

**Finding:** `style-2-5`.

*   Replace "Interpretations D10, D11, D13, and D14 do not add behaviour to the contract." and the following sentence with "Interpretations D10, D11, D13, and D14 fix choices the specification leaves open and change no behaviour it defines."

### F06

**Finding:** `style-2-6`.

*   File Boundary sentence: replace with "File Boundary exception: this plan and its review records under `docs/reviews/001_tome_core_architecture_egm/implementation_readiness/` may change only through the EGM review workflow."
*   Phase 0 step 0: replace "its Stage 9 review records" with "its review records under `docs/reviews/001_tome_core_architecture_egm/implementation_readiness/`".
*   Verification file-boundary line: replace "the documents named in the File Boundary exception" with "the plan and review records named in the File Boundary exception".

### F07

**Findings:** `codebase_details-2-2`, `style-2-7`, `style-2-8`.

*   README Phase 0, testing bullet: replace with "Testing and formatting: replace the "Running the Test Suite" and "Formatting & Static Analysis" subsections with one subsection, `### Verification`, that runs `./scripts/lint.sh` and states that it runs Ruff lint, the Ruff format check, and pytest."
*   README Phase 0, Prerequisites bullet: replace "run the three gate commands directly" with "run `ruff check .`, `ruff format --check .`, and `pytest` directly".
*   README Phase 0, project-structure bullet: replace "# Legacy tests, removed in Phase 5" with "# Legacy tests, to be removed".
*   README Phase 5, status bullet: replace "is checked by the Section 7 test suite" with "is checked by tests derived from Section 7 of the specification", linking "specification" to `docs/designs/001_tome_core_architecture.md`.
*   README Phase 5, project-structure bullet: add "change the `src/tome/__init__.py` comment to "Package entry point, version, and public API"".

### F08

**Finding:** `style-2-9`.

*   `D66_KEYS`: replace `for tens in 1..6 for units in 1..6` with `for tens in range(1, 7) for units in range(1, 7)`.

### F09

**Finding:** `style-2-10`.

*   Target File 13: replace "Do not use star imports or a computed `__all__`, which fails Ruff F401." with "Do not use star imports, which hide the export list, or a computed `__all__`, which Ruff reports as F401."
*   Target File 14: replace "Do not use star imports or a computed `__all__`." with the same sentence.

### F10

**Findings:** `implementation_readiness-2-1`, `style-2-11`.

*   Replace the `ScriptedCallbacks` bullet with:
    "(Phase 4) `ScriptedCallbacks(proposal=None, peer=None, umpire=None, failure=None)`: each argument is an optional function with the matching protocol signature that replaces the default."
    "It exposes the bound methods `proposal_generator`, `peer_reviewer`, `umpire_review`, and `failure_resolver`, which tests pass to `run`."
    "Each method appends a tuple of the positional arguments it received to `proposal_calls`, `peer_calls`, `umpire_calls`, or `failure_calls`, then returns the function's result or the default."
    Defaults:
    *   Proposal: statement `f"{active_actor.name} achieves outcome {world_state.turn_index + 1}."`, with one supporting pro citing `world_state.canon_facts[0]` with argument `"Scripted supporting argument."`.
    *   Peer, umpire review: unchanged.
    *   Failure: unchanged, and state that `turn_index` is the callback's first parameter, equal to `world_state.turn_index + 1`.
*   `seed_for_base_roll`: append "If no seed matches, it raises `AssertionError` naming the target."

### F11

**Finding:** `style-2-12`.

*   Rename the row labels "Explicit failure types" to "Invariant 15 (Explicit Failure Types)", "Spark table identity" to "D8 (default table identity)", and "Explicit failure types (run)" to "Invariant 15 (Explicit Failure Types, run)".

### F12

**Finding:** `codebase_details-2-3`.

*   Phase 5 step 3: append "The search checks single lines; a package-relative import such as `from . import models`, or a module name on a later line of a multi-line import, is caught by the exit gate instead, because importing a deleted module fails when `tome` and the test modules load."

### F13

**Finding:** `implementation_readiness-2-3`.

*   D13 Choice: replace "other than a `RunError` or `MemoryError`" with "other than a `RunError`, `MemoryError`, `RecursionError`, or `SystemError`", and "`RunError` and `MemoryError` are re-raised unchanged" with "Those four are re-raised unchanged, because Section 2.8 forbids relabelling resource exhaustion or interpreter failure as `MechanicsError`."
*   Runner error handling: change the first handler to `except (RunError, MemoryError, RecursionError, SystemError): raise`.
*   Runner: add "Import `draw_turn_cues`, `roll_resolution`, and the other mechanics and gate functions by name, so tests can replace them through `tome.engine.runner`."
*   Traceability: add a Phase 4 row "D13 (engine-internal exceptions)": "`test_engine_internal_exceptions`: replacing `tome.engine.runner.draw_turn_cues` with a function raising `ValueError` gives `MechanicsError`; raising `RecursionError` or `SystemError` propagates unchanged."

### F14

**Finding:** `implementation_readiness-2-4`.

*   `test_spark_table_source_and_tags`: append "with the same seed and supplied order, a default-table run and an override run give identical `posture_roll`, table-name prefixes of `spark_tags`, and `resolution_roll`".
*   `test_new_proposal_rejected_before_peers_and_dice`: replace "with no peer calls" with "with no peer calls and no call to `tome.engine.runner.roll_resolution`, replaced with a spy".
*   `test_umpire_rejection_reverts_and_records`: append "; and the upward vector of baseline -1, final 0, and anchor `"Fact 1."`, which reverts to -1".
*   `test_failure_resolver_called_on_every_failure`: append "; after a restated consequence, `peer_evaluations` keeps the source peer's original `public_argument`, `failure_resolution.source_voter_actor_id` names that peer, and canon receives only the restated statement".

## Approval Boundary

The human selected "auto accept" on 2026-11-18.
All 14 edit groups were applied to the plan in one batch, exactly as proposed.
This does not change the specification, approve the plan, or authorize implementation.

## Applied Resolution and Verification

*   Accepted and applied findings: 19.
*   Contested: 0.
*   Escalated: 0.
*   Declined: 0.
*   Unaddressed approved fixes: 0.
*   Round-two clean status remains **No**; the clean streak remains **0 of 2**.
*   Post-resolution plan: 499 lines; the Detailed Implementation Plan still starts at line 15.

Checks after applying:

*   Every applied text is present and none of the replaced text remains; the three in-place probe qualifiers and the two export-rule sentences were each replaced at every site.
*   Plan tables keep consistent column counts; links, whitespace, and `git diff --check` pass.
*   The Phase 5 search still reports the 9 current legacy imports.
*   The specification, `src/`, `tests/`, and `pyproject.toml` are unchanged from `7d3fef1`; the targeted EGM validator passes.
