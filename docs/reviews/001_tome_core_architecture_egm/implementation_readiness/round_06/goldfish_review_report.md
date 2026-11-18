# Goldfish Annotated Review Report: Stage 9 Round 6

**Status:** resolved
**Date:** 2026-11-18
**Target:** [Implementation plan](../../../../plans/001_tome_core_architecture_plan.md), Detailed Implementation Plan, lines 15-508
**Reviewed SHA-256:** `5ab721dd7e7a20d0c7bebcd22e58c4426bf43f7f3bd4063b650c41fc6b7a5281`
**Post-resolution SHA-256:** `dbdb08a0e1e5986f8b6a7e65d9c08cb4f1e117aeb4e11cfd622ea76e0fc555bb`
**Raw findings:** [Complete round-six reviewer reports](reviewer_report.md)
**Loop state:** [Stage 9 report](../implementation_readiness_report.md)

## Round Decision Before Edits

All three requested reviewers completed.
They reported 15 findings: 0 Blocker, 2 Major, and 13 Nit.
Round 6 is **not clean** because `codebase_details-6-1` and `style-6-1` are unsettled Majors.
Consecutive clean rounds: **0 of 2**.
This is the first round past the five-round cap; the human chose to continue.

The implementation-readiness reviewer again judged the plan ready to implement, with no Blocker or Major; its four Nits are test gaps where a wrong implementation could still pass.

All 15 findings are classified PROPOSE FIX, and every original severity is unchanged.
No finding is contested, escalated, or declined.

**Recurring scope.** The D12 list of narrowed specification passages has been corrected in rounds 2, 3, and now 6 (`style-6-1`).
Reverting any earlier edit would not resolve this finding, so it is not churn by the loop's definition.
To stop the recurrence, J03 replaces the closed count with "every specification passage that says … including …", so a future missed passage does not make the sentence false.
The `MemoryError` sentence (`style-6-2`) is likewise refined in place, not reverted.

The coordinator verified `codebase_details-6-1` before classifying.
All 29 Markdown files in the worktree, tracked and untracked, including this plan and every review record, contain no `python` or `py` fence, and the Ruff format check passes on all 36 checked files.
The gate passes today; the plan lacks an instruction for a future failure and a correct evidence reference.

## Findings by Severity

### Major

| Finding | Scope | Summary | Suggestion | Edit |
| :--- | :--- | :--- | :--- | :--- |
| `codebase_details-6-1` | Phase 0 gate, `scripts/lint.sh`, Starting Baseline | Committed review-record Markdown is format-checked, but the plan has no instruction if it fails and cites missing evidence. | PROPOSE FIX | [J01](#j01) |
| `style-6-1` | D12 paragraph and Source | The narrowed-passage list omits Edge Case 11 and Invariant 15. | PROPOSE FIX | [J03](#j03) |

### Nit

| Finding | Scope | Summary | Suggestion | Edit |
| :--- | :--- | :--- | :--- | :--- |
| `implementation_readiness-6-1` | Callback-boundary test | A callback's `RunError`, `RecursionError`, and `SystemError` wrapping is untested. | PROPOSE FIX | [J11](#j11) |
| `implementation_readiness-6-2` | Request-validation run test | Non-mapping request types are untested. | PROPOSE FIX | [J12](#j12) |
| `implementation_readiness-6-3` | Historical canon and failure-resolution tests | Two Section 7 sub-assertions are unassigned. | PROPOSE FIX | [J13](#j13) |
| `implementation_readiness-6-4` | Runner imports, required-callables test | The `random.Random` spy target is unstated, so the check could pass vacuously. | PROPOSE FIX | [J14](#j14) |
| `codebase_details-6-2` | `uv.lock` rationale | Hatchling is not pinned by `uv.lock`. | PROPOSE FIX | [J02](#j02) |
| `style-6-2` | D12 `MemoryError` sentence | The relabelling clause does not support D12; the callback-versus-engine difference is unexplained. | PROPOSE FIX | [J04](#j04) |
| `style-6-3` | Baseline | "Three gate commands" is a forward reference. | PROPOSE FIX | [J05](#j05) |
| `style-6-4` | `scripts/lint.sh` | Same evidence gap as `codebase_details-6-1`; an unevidenced fence-language claim. | PROPOSE FIX | [J01](#j01) |
| `style-6-5` | Phase 5 step 3 | "Before Phase 5" and "imports" are imprecise. | PROPOSE FIX | [J06](#j06) |
| `style-6-6` | `uv.lock` details | The refresh sentence cannot apply within this plan. | PROPOSE FIX | [J07](#j07) |
| `style-6-7` | `ErrorCode` | "From `errors.py`" reads as an import, which would be circular. | PROPOSE FIX | [J08](#j08) |
| `style-6-8` | `apply_umpire_rejections` | Positional arguments would fail on a Pydantic model. | PROPOSE FIX | [J09](#j09) |
| `style-6-9` | `ScriptedCallbacks` peer default | `voter_actor_id` is missing. | PROPOSE FIX | [J10](#j10) |

## Proposed Edit Groups

Line numbers refer to the reviewed plan revision.
No edit changes the specification, `src/`, `tests/`, or `pyproject.toml`.

### J01

**Findings:** `codebase_details-6-1`, `style-6-4`.

*   Add a Starting Baseline bullet after the Ruff 0.17.5 bullet: "On 2026-11-18, none of the 29 Markdown files in the worktree, tracked and untracked, including this plan and its review records, contained a `python` or `py` fence, and the format check passed on all checked files."
*   `scripts/lint.sh`: replace the Markdown bullet with "With the locked Ruff, the format check also covers Markdown files and fails if the code in a `python`-fenced block would be reformatted; it does not edit files. No Markdown file contained such a block when this plan was written (see Starting Baseline). If the format check fails on a Markdown file, stop and raise it with the human developer, because documents outside the file boundary may not be edited."

### J02

**Finding:** `codebase_details-6-2`.

*   File Boundary, `uv.lock` row rationale: replace "Reproducible dependency versions for the gate (D4)." with "Reproducible runtime and development dependency versions for the gate (D4); the Hatchling build backend is not pinned by `uv.lock`, and a build failure follows the `scripts/lint.sh` stop-and-raise rule."

### J03

**Finding:** `style-6-1`.

*   Replace "D12 narrows six specification passages that say any callback failure or cancellation raises a typed error: the two Section 3.5 sentences for the umpire review and the failure resolver, Edge Cases 6 and 14, and the Section 7 "Umpire Audit and Errors" and "Failure Resolver Errors" bullets." with "D12 narrows every specification passage that says a callback failure or cancellation raises a typed error, including the two Section 3.5 sentences for the umpire review and the failure resolver, Edge Cases 6, 11, and 14, Invariant 15, and the Section 7 "Umpire Audit and Errors" and "Failure Resolver Errors" bullets."
*   D12 Source cell: replace "kept over the broader wording of Section 3.5, Edge Cases 6 and 14, and the Section 7 "Umpire Audit and Errors" and "Failure Resolver Errors" bullets" with "kept over the broader wording of the specification passages listed after this table".

### J04

**Finding:** `style-6-2`.

*   Replace the `MemoryError` sentence with two sentences:
    "`MemoryError` propagates because Section 2.8 states that memory exhaustion can prevent delivery of a typed `RunFailure`."
    "Among `Exception` subclasses, D12 exempts only `MemoryError`, so a callback's `RecursionError` or `SystemError` becomes that callback's error type; D13 re-raises engine-raised ones unchanged, because Section 2.8 forbids only relabelling them as `MechanicsError`."

### J05

**Finding:** `style-6-3`.

*   Baseline: replace "and the three gate commands passed" with "and the three `scripts/lint.sh` commands (Target File 3) passed".

### J06

**Finding:** `style-6-5`.

*   Phase 5 step 3: replace "Before Phase 5 it reports the 9 legacy imports in `src/tome/` and `tests/`, which confirms that it works." with "At `7d3fef1` it reports 9 matching legacy import lines in `src/tome/` and `tests/`, which confirms that it works."

### J07

**Finding:** `style-6-6`.

*   `uv.lock` details: delete "Refresh it with `uv lock` only when `pyproject.toml` dependencies change."

### J08

**Finding:** `style-6-7`.

*   Replace "`ErrorCode = Literal[...]` with the seven codes from `errors.py`." with "`ErrorCode = Literal[...]` with the seven `code` strings from the Target File 6 table, written as literals."

### J09

**Finding:** `style-6-8`.

*   Replace "`UmpireRejectionRecord(voter_actor_id, reason, evaluation_before_reversion=evaluation.model_copy(deep=True))`" with "`UmpireRejectionRecord(voter_actor_id=…, reason=…, evaluation_before_reversion=evaluation.model_copy(deep=True))`, using the rejection's `voter_actor_id` and `reason`".

### J10

**Finding:** `style-6-9`.

*   `ScriptedCallbacks` peer default: replace "Peer: `baseline_plausibility` 0," with "Peer: `voter_actor_id` `voter_actor.id`, `baseline_plausibility` 0,".

### J11

**Finding:** `implementation_readiness-6-1`.

*   Callback-boundary row: append to `test_callback_exceptions_wrapped`: "an `InvalidProposalError` raised by `peer_reviewer` becomes `PeerReviewError`; a callback's `RecursionError` and `SystemError` each become that callback's error type, with the original as `__cause__`."

### J12

**Finding:** `implementation_readiness-6-2`.

*   Request Validation (through `run`) row: append "`test_run_rejects_non_mapping_request`: a JSON string, a `list`, and `None` as `request` each raise `InvalidRunRequestError` with no callback calls."

### J13

**Finding:** `implementation_readiness-6-3`.

*   Historical Canon Grounding row: append "; a shift citing "Actor A has capability X" is kept by `validate_peer_evaluation` and can still be rejected by `apply_umpire_rejections`".
*   `test_failure_resolution_validation`: replace "valid, restated, and null-source decisions accepted" with "a direct-use decision whose statement equals the source peer's `public_argument`, a restated decision, and a null-source decision are accepted and stored verbatim".

### J14

**Finding:** `implementation_readiness-6-4`.

*   Runner Imports bullet: append "`runner.py` uses `import random` and calls `random.Random`."
*   Required Callables row: replace "no `random.Random` constructed (spied with `monkeypatch`)" with "no `random.Random` constructed, checked by `monkeypatch.setattr(tome.engine.runner.random, "Random", spy)`; as a positive control, a valid run calls the spy exactly once".

## Approval Boundary

The human selected "auto accept" on 2026-11-18.
All 14 edit groups were applied to the plan in one batch.
This does not change the specification, approve the plan, or authorize implementation.

## Applied Resolution and Verification

*   Accepted and applied findings: 15.
*   Contested: 0.
*   Escalated: 0.
*   Declined: 0.
*   Unaddressed approved fixes: 0.
*   Round-six clean status remains **No**; the clean streak remains **0 of 2**.
*   Post-resolution plan: 512 lines; the Detailed Implementation Plan still starts at line 15.

**Application error, corrected before verification.** While inserting the J01 baseline bullet, the coordinator's replacement dropped the opening of the next bullet, which records the `validate_egm.py` run.
The bullet was restored immediately.
Reversing exactly the 14 approved edit groups then reproduced the reviewed SHA-256, which proves that no other text changed.

Checks after applying:

*   Every applied text occurs exactly once.
*   Plan tables keep consistent column counts; links, whitespace, and `git diff --check` pass.
*   The Phase 5 search still reports the 9 current legacy imports, and the Ruff format check passes on all 38 files.
*   The specification, `src/`, `tests/`, and `pyproject.toml` are unchanged from `7d3fef1`; the targeted EGM validator passes.
