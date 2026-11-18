# Goldfish Annotated Review Report: Stage 9 Round 5

**Status:** resolved
**Date:** 2026-11-18
**Target:** [Implementation plan](../../../../plans/001_tome_core_architecture_plan.md), Detailed Implementation Plan, lines 15-506
**Reviewed SHA-256:** `713caa27483e578bfa27cbd559627e72fd01d5efe72f488ba672176f6115a20b`
**Post-resolution SHA-256:** `5ab721dd7e7a20d0c7bebcd22e58c4426bf43f7f3bd4063b650c41fc6b7a5281`
**Raw findings:** [Complete round-five reviewer reports](reviewer_report.md)
**Loop state:** [Stage 9 report](../implementation_readiness_report.md)

## Round Decision Before Edits

All three requested reviewers completed.
They reported 7 findings: 0 Blocker, 2 Major, and 5 Nit.
Round 5 is **not clean** because `style-5-1` and `style-5-2` are unsettled Majors.
Consecutive clean rounds: **0 of 2**.

**The loop has reached its five-round cap without converging.**
After this round's resolution, the loop rules require a human decision: accept the residual findings and proceed, continue past the cap, or return the plan to drafting.

The codebase-details reviewer reported no findings.
The implementation-readiness reviewer judged that every phase could be implemented without a design choice, and reported one Nit.

All 7 findings are classified PROPOSE FIX, and every original severity is unchanged.
No finding is contested, escalated, or declined.
No finding is churn: `style-5-1` and `style-5-2` concern wording added in rounds 3 and 4, and reverting it would reopen the earlier findings rather than resolve these.

The coordinator verified `style-5-1` before classifying.
In a temporary copy of the repository at `7d3fef1`, `uv lock` pinned Ruff 0.17.5.
Its `ruff format --check` covers Markdown files, fails on a badly formatted `python`-fenced block, and leaves the file unchanged.
The plan's word "reformats" is therefore wrong for a check-only command, and the observation belongs in the Starting Baseline.

## Findings by Severity

### Major

| Finding | Scope | Summary | Suggestion | Edit |
| :--- | :--- | :--- | :--- | :--- |
| `style-5-1` | `scripts/lint.sh`, Starting Baseline | "Reformats" contradicts the check-only command; the Ruff Markdown behaviour is not in the recorded evidence. | PROPOSE FIX | [I01](#i01) |
| `style-5-2` | D13 against `_validate_output` | The two give different outcomes for a `RecursionError` or `SystemError` raised while validating callback output. | PROPOSE FIX | [I02](#i02) |

### Nit

| Finding | Scope | Summary | Suggestion | Edit |
| :--- | :--- | :--- | :--- | :--- |
| `implementation_readiness-5-1` | Atomicity test | No stated way to force Failure on a later turn. | PROPOSE FIX | [I07](#i07) |
| `style-5-3` | D10, D14, `_validate_output`, runner step 2 | Whether subclasses of a model class are accepted is ambiguous. | PROPOSE FIX | [I03](#i03) |
| `style-5-4` | Runner step 7.10 | "After step 8" can mean top-level step 8. | PROPOSE FIX | [I04](#i04) |
| `style-5-5` | `build_proposal` | The construction sentence renders as part of the grounding item. | PROPOSE FIX | [I05](#i05) |
| `style-5-6` | Phase 1 step 0 | `ARTIFICE_ROOT` is undefined; the baseline used the literal path. | PROPOSE FIX | [I06](#i06) |

## Proposed Edit Groups

Line numbers refer to the reviewed plan revision.
No edit changes the specification, `src/`, `tests/`, or `pyproject.toml`.

### I01

**Finding:** `style-5-1`.

*   Add a Starting Baseline bullet after the temporary-copy bullet: "In the same temporary copy, `uv lock` pinned Ruff 0.17.5, whose `ruff format --check` also covers Markdown files: it fails if the code in a `python`-fenced block would be reformatted, and it does not edit files."
*   `scripts/lint.sh`: replace "With the locked Ruff, the format check also covers Markdown files and reformats the code in fenced `python` blocks; prose and other fence languages are unchanged, and the repository has no `python`-fenced Markdown at `7d3fef1`." with "With the locked Ruff, the format check also covers Markdown files and fails if the code in a `python`-fenced block would be reformatted; it does not edit files or check prose and other fence languages, and the repository has no `python`-fenced Markdown at `7d3fef1` (see Starting Baseline)."

### I02

**Finding:** `style-5-2`.

*   D13: replace "any `Exception` raised by engine code," with "any `Exception` raised by engine code and not already converted to a callback error type by `_validate_output` (Target File 10),".
*   `_validate_output`: append "This conversion includes `RecursionError` and `SystemError`, because they are raised while validating callback output; D13 applies only outside `_validate_output`."

### I03

**Finding:** `style-5-3`.

*   D10: replace "or an instance of the corresponding `tome.engine` model class; an instance is re-validated from `model_dump()`. Any other type, including a different model class, is malformed." with "or an object for which `isinstance(raw, model_cls)` holds, so subclasses are accepted; such an instance is re-validated from `model_dump()`. Any other type, including an unrelated model class, is malformed."
*   D14: replace "a `Mapping` or a `RunRequest` instance;" with "a `Mapping` or an object for which `isinstance(request, RunRequest)` holds;".
*   `_validate_output`: replace "if `raw` is an instance of `model_cls`" with "if `isinstance(raw, model_cls)`".
*   Runner step 2: replace "or a `RunRequest` with" with "or an object for which `isinstance(request, RunRequest)` holds with".

### I04

**Finding:** `style-5-4`.

*   Runner step 7.10: replace "read from `state` after step 8" with "read from `state` after sub-step 8 of step 7".

### I05

**Finding:** `style-5-5`.

*   `build_proposal`: replace the unnumbered "Then construct `Proposal` from …" line with numbered item "4.  Construction: build `Proposal` from …" (rest unchanged), indented as items 1 to 3.

### I06

**Finding:** `style-5-6`.

*   Phase 1 step 0: replace `${ARTIFICE_ROOT:-$HOME/.local/share/artifice}` with `$HOME/.local/share/artifice`, the path recorded in the Starting Baseline.

### I07

**Finding:** `implementation_readiness-5-1`.

*   Integration atomicity row: replace "`test_invalid_decision_after_resolved_turn_is_atomic`." with "`test_invalid_decision_after_resolved_turn_is_atomic`: with a two-actor supplied order, `tome.engine.runner.roll_resolution` is replaced with a function returning `(4, 4)` then `(1, 1)`, so turn 1 succeeds and turn 2 fails; the failure resolver returns an invalid decision on turn 2, and `run` raises `UmpireResolutionError` with no result and an unchanged input."

## Approval Boundary

The human selected "auto accept" on 2026-11-18.
All 7 edit groups were applied to the plan in one batch, exactly as proposed.
This does not change the specification, approve the plan, or authorize implementation.

## Applied Resolution and Verification

*   Accepted and applied findings: 7.
*   Contested: 0.
*   Escalated: 0.
*   Declined: 0.
*   Unaddressed approved fixes: 0.
*   Round-five clean status remains **No**; the clean streak remains **0 of 2**.
*   Post-resolution plan: 508 lines; the Detailed Implementation Plan still starts at line 15.

Checks after applying:

*   Every applied text is present, and none of the replaced text remains.
*   Plan tables keep consistent column counts; links, whitespace, and `git diff --check` pass.
*   The Phase 5 search still reports the 9 current legacy imports, and the Ruff format check passes on all 36 files.
*   The specification, `src/`, `tests/`, and `pyproject.toml` are unchanged from `7d3fef1`; the targeted EGM validator passes.

These round-five edits were checked directly; no fresh reviewer has assessed them, because the loop has reached its cap.
