# Goldfish Annotated Review Report: Stage 9 Round 4

**Status:** resolved
**Date:** 2026-11-18
**Target:** [Implementation plan](../../../../plans/001_tome_core_architecture_plan.md), Detailed Implementation Plan, lines 15-505
**Reviewed SHA-256:** `beadbc1e5e7ce6c7b59a8e3107d3ad4714faf49edad5ae9aa87d64e9fac39aad`
**Post-resolution SHA-256:** `713caa27483e578bfa27cbd559627e72fd01d5efe72f488ba672176f6115a20b`
**Raw findings:** [Complete round-four reviewer reports](reviewer_report.md)
**Loop state:** [Stage 9 report](../implementation_readiness_report.md)

## Round Decision Before Edits

All three requested reviewers completed.
They reported 12 findings: 0 Blocker, 1 Major, and 11 Nit.
Round 4 is **not clean** because `style-4-1` is an unsettled Major.
Consecutive clean rounds: **0 of 2**.

**Cap consequence.** Four of the five rounds have run.
Two consecutive clean rounds are no longer possible within the cap, because only round 5 remains.
Under the loop rules, after round 5 is resolved the loop stops at its cap, and you choose whether to accept the residual findings and proceed, continue past the cap, or return the plan to drafting.

The implementation-readiness reviewer judged the plan ready to implement, with one Nit and no Blocker or Major.
The codebase-details reviewer also found no Blocker or Major.

All 12 findings are classified PROPOSE FIX, and every original severity is unchanged.
No finding is contested, escalated, or declined.
`style-4-9` asks to drop two D12 sentences; the proposal keeps the forward-looking spec-alignment note, which is stated nowhere else, and drops only the repeated parts.
No finding is churn: `style-4-7` and `style-4-9` touch round-three wording, and reverting it would not resolve them.

The coordinator verified `codebase_details-4-1` before classifying.
With Ruff 0.17.5, the format check includes Markdown files but reformats only the code inside fenced `python` blocks; it leaves prose and other fence languages unchanged.
The repository currently has no Python-fenced Markdown, and the format check passes on all 32 files.

## Findings by Severity

### Major

| Finding | Scope | Summary | Suggestion | Edit |
| :--- | :--- | :--- | :--- | :--- |
| `style-4-1` | Runner step 10, cycling test | `TurnRecord.session_index` before or after the step-8 increment is ambiguous, and no test checks it on a round-ending turn. | PROPOSE FIX | [H01](#h01) |

### Nit

| Finding | Scope | Summary | Suggestion | Edit |
| :--- | :--- | :--- | :--- | :--- |
| `implementation_readiness-4-1` | Runner callback steps | What the D12 wrapper surrounds is unstated. | PROPOSE FIX | [H11](#h11) |
| `codebase_details-4-1` | Gate, Phase 0 commit | The format check covers Python fences in Markdown; the locked Ruff version is not recorded. | PROPOSE FIX | [H12](#h12) |
| `style-4-2` | Runner step 7.4 | The rejection result is not rebound to `evaluations`. | PROPOSE FIX | [H02](#h02) |
| `style-4-3` | Runner step 4, request-validation row | "Generator" also names `proposal_generator`. | PROPOSE FIX | [H03](#h03) |
| `style-4-4` | Request-validation row | "Re-checks" claims earlier verification of the `bool` and tuple cases. | PROPOSE FIX | [H04](#h04) |
| `style-4-5` | `INVALID_REQUEST_CASES` | Some cases come from Section 3.4, not Edge Case 5. | PROPOSE FIX | [H05](#h05) |
| `style-4-6` | `make_world` | Actor naming by position or by ID suffix is ambiguous. | PROPOSE FIX | [H06](#h06) |
| `style-4-7` | D13 | The stated reason covers three of the four re-raised types. | PROPOSE FIX | [H07](#h07) |
| `style-4-8` | `text.py` | "No other dependencies" can be read as "no imports". | PROPOSE FIX | [H08](#h08) |
| `style-4-9` | Baseline, D12 paragraph | A plan decision sits in the baseline; two D12 sentences repeat earlier text. | PROPOSE FIX, modified | [H09](#h09) |
| `style-4-10` | Verification | Two checks give no timing. | PROPOSE FIX | [H10](#h10) |

## Proposed Edit Groups

Line numbers refer to the reviewed plan revision.
No edit changes the specification, `src/`, `tests/`, or `pyproject.toml`.

### H01

**Finding:** `style-4-1`.

*   Runner step 10: replace "Append a `TurnRecord` built from the values above." with "Append a `TurnRecord` built from the values above; its `turn_index` and `session_index` are read from `state` after step 8."
*   Integration cycling row: replace "one completed round, `turn_index` +5, and the order repeated" with "one completed round, `turn_index` +5, and the order repeated; each record's `turn_index` and `session_index` equal the state after that turn, so the third record shows the incremented `session_index` and the fourth and fifth records keep it".

### H02

**Finding:** `style-4-2`.

*   Runner step 7.4: replace "then `apply_umpire_rejections`." with "then `evaluations, umpire_rejections = apply_umpire_rejections(raw, evaluations=evaluations)`."

### H03

**Finding:** `style-4-3`.

*   Runner step 4: replace "**Generator:**" with "**Random generator:**".
*   Request Validation (through `run`) row: replace "no generator constructed" with "no `random.Random` constructed".

### H04

**Finding:** `style-4-4`.

*   Request Validation row: replace "this re-checks on the locked Pydantic version that a `bool` for an integer, an explicit `null` for an optional field, and a tuple for a list are rejected" with "this checks on the locked Pydantic version that a `bool` for an integer, an explicit `null` for an optional field, and a tuple for a list are rejected, re-checking the explicit-`null` behaviour recorded in Starting Baseline".

### H05

**Finding:** `style-4-5`.

*   `INVALID_REQUEST_CASES`: replace "to produce one Edge Case 5 violation" with "to produce one Edge Case 5 or Section 3.4 request violation".

### H06

**Finding:** `style-4-6`.

*   `make_world`: replace "naming each actor `Actor A`, `Actor B`, and so on, with agenda `Agenda A`, `Agenda B`, and so on" with "naming the actors by list position: the first is `Actor A` with agenda `Agenda A`, the second `Actor B` with agenda `Agenda B`, and so on, whatever their IDs".

### H07

**Finding:** `style-4-7`.

*   D13: replace "Those four are re-raised unchanged, because Section 2.8 forbids relabelling resource exhaustion or interpreter failure as `MechanicsError`." with "A `RunError` is re-raised unchanged because it is already typed; the other three are re-raised unchanged because Section 2.8 forbids relabelling resource exhaustion or interpreter failure as `MechanicsError`."

### H08

**Finding:** `style-4-8`.

*   `text.py` scope: replace "Spec Section 3.0 normalization, with no other dependencies." with "Spec Section 3.0 normalization; imports no other `tome` module."

### H09

**Finding:** `style-4-9`.

*   Baseline: replace "has no imports, and is reused unchanged." with "and has no imports."
*   D12 paragraph: delete "The human developer confirmed this trade-off on 2026-11-17."
*   D12 paragraph: replace "A future specification revision should align those passages with D12; until then, D12 governs the implementation." with "A future specification revision should align those passages with D12."
*   **Modification:** the reviewer proposed dropping the whole last sentence; the spec-alignment note is kept because no other line of the plan records that follow-up.

### H10

**Finding:** `style-4-10`.

*   Verification: "**Build and environment:** `uv sync --locked --extra dev` succeeds on Python 3.11 after every phase."
*   Verification: "**File boundary:** after every phase, `git diff --name-status 7d3fef1` lists only …" (rest unchanged).

### H11

**Finding:** `implementation_readiness-4-1`.

*   After runner step 7, add: "For each callback invocation in step 7, build all snapshot and list arguments first; the D12 `try` wraps only the callable invocation expression, and the gate function named after "then" is called after and outside that `try`."

### H12

**Finding:** `codebase_details-4-1`.

*   `scripts/lint.sh`: add "With the locked Ruff, the format check also covers Markdown files and reformats the code in fenced `python` blocks; prose and other fence languages are unchanged, and the repository has no `python`-fenced Markdown at `7d3fef1`."
*   Phase 0 step 7: replace "its body records the Pydantic version that `uv.lock` resolved." with "its body records the Pydantic and Ruff versions that `uv.lock` resolved."

## Approval Boundary

The human selected "auto accept" on 2026-11-18.
All 12 edit groups were applied to the plan in one batch.
This does not change the specification, approve the plan, or authorize implementation.

## Applied Resolution and Verification

*   Accepted and applied findings: 12.
*   Contested: 0.
*   Escalated: 0.
*   Declined: 0.
*   Unaddressed approved fixes: 0.
*   Round-four clean status remains **No**; the clean streak remains **0 of 2**.
*   Post-resolution plan: 506 lines; the Detailed Implementation Plan still starts at line 15.

**H11 placement:** the callback-wrapping rule was added as a "Callback wrapping" bullet in the runner's rule list, next to "Imports" and "Snapshots", rather than as a sentence inside step 7's numbered sub-steps, so the sub-step numbering is unchanged.
The text matches H11.

Checks after applying:

*   Every applied text is present, and none of the replaced text remains.
*   Plan tables keep consistent column counts; links, whitespace, and `git diff --check` pass.
*   The Phase 5 search still reports the 9 current legacy imports, and the Ruff format check passes on all 34 files.
*   The specification, `src/`, `tests/`, and `pyproject.toml` are unchanged from `7d3fef1`; the targeted EGM validator passes.
