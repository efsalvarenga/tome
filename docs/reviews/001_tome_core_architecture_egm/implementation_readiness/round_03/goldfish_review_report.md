# Goldfish Annotated Review Report: Stage 9 Round 3

**Status:** resolved
**Date:** 2026-11-18
**Target:** [Implementation plan](../../../../plans/001_tome_core_architecture_plan.md), Detailed Implementation Plan, lines 15-499
**Reviewed SHA-256:** `afd65538a48727343205668a8c3fc6c5d9ce13ab176b508993535c417f5c3a00`
**Post-resolution SHA-256:** `beadbc1e5e7ce6c7b59a8e3107d3ad4714faf49edad5ae9aa87d64e9fac39aad`
**Raw findings:** [Complete round-three reviewer reports](reviewer_report.md)
**Loop state:** [Stage 9 report](../implementation_readiness_report.md)

## Round Decision Before Edits

All three requested reviewers completed.
They reported 17 findings: 0 Blocker, 2 Major, and 15 Nit.
Round 3 is **not clean** because `style-3-1` and `style-3-2` are unsettled Majors.
Consecutive clean rounds: **0 of 2**.

Three of the five rounds have now run.
Convergence within the cap therefore requires rounds 4 and 5 both to be clean.
If round 4 is not clean, the loop reaches its cap at round 5 and you decide whether to accept the residual findings, continue past the cap, or return the plan to drafting.

All 17 findings are classified PROPOSE FIX, and every original severity is unchanged.
No finding is contested, escalated, or declined.
`style-3-2` and `style-3-3` refine wording that round 2 added to the D12 paragraph; neither would be resolved by reverting that wording, so neither is churn, and neither changes D12's behaviour.
The implementation-readiness reviewer again found no Blocker or Major.

The coordinator verified two claims before classifying:

*   **Project build (`implementation_readiness-3-5`, `codebase_details-3-1`).** In a temporary copy of the repository at `7d3fef1`, with `.python-version` set to `3.11`: `uv lock` resolved Pydantic 2.14.3; `uv sync --locked --extra dev` installed `tome` 0.1.0 in editable mode through Hatchling; `import tome` worked under `uv run` without `PYTHONPATH`; and the three gate commands passed, including the 8 legacy tests. The real worktree was not changed.
*   **Validator (`style-3-9`).** `validate_egm.py --spec 001` exits 0 on the default `python3`, which is 3.9.6.

**Coordinator correction (G16).** Applying round-two edit F14, the coordinator appended the upward-shift case to the end of the umpire row, after the `test_umpire_rejection_errors` clause, instead of to `test_umpire_rejection_reverts_and_records` as F14 specified.
G16 moves it to the intended test.

## Findings by Severity

### Major

| Finding | Scope | Summary | Suggestion | Edit |
| :--- | :--- | :--- | :--- | :--- |
| `style-3-1` | Verification, whitespace line | `git diff --check` has no base and checks nothing after a phase commit. | PROPOSE FIX | [G01](#g01) |
| `style-3-2` | D12 rationale | The `MemoryError` sentence can be read as requiring callback `RecursionError` and `SystemError` to propagate. | PROPOSE FIX | [G02](#g02) |

### Nit

| Finding | Scope | Summary | Suggestion | Edit |
| :--- | :--- | :--- | :--- | :--- |
| `implementation_readiness-3-1` | Runner snapshots, isolation test | List arguments of models may share elements; the isolation test lists no mutations. | PROPOSE FIX | [G12](#g12) |
| `implementation_readiness-3-2` | Phase 4 umpire tests | No test checks what `UmpireReview` receives. | PROPOSE FIX | [G13](#g13) |
| `implementation_readiness-3-3` | Table-independence test | "Reversed key order" is ambiguous. | PROPOSE FIX | [G14](#g14) |
| `implementation_readiness-3-4` | Public API | No test checks the exports. | PROPOSE FIX | [G15](#g15) |
| `implementation_readiness-3-5` | Baseline, Phase 0 | The Hatchling build under `uv run` was unverified. | PROPOSE FIX | [G11](#g11) |
| `codebase_details-3-1` | Baseline, lint script | Why the gate needs no `PYTHONPATH` is unstated. | PROPOSE FIX | [G11](#g11) |
| `codebase_details-3-2` | Verification, whitespace line | Same as `style-3-1`. | PROPOSE FIX | [G01](#g01) |
| `style-3-3` | D12 paragraph and Source | Passage count reads as six; bullet names are hard to parse and inconsistent. | PROPOSE FIX | [G03](#g03) |
| `style-3-4` | Baseline | Only draw values were confirmed, not the worked-example result. | PROPOSE FIX | [G04](#g04) |
| `style-3-5` | Baseline | "Those tests" can refer to the probe scripts. | PROPOSE FIX | [G05](#g05) |
| `style-3-6` | `ContractModel` | "Pass full validation" can read as "be accepted". | PROPOSE FIX | [G06](#g06) |
| `style-3-7` | Runner step 2 | Wrong step number; a global `Random` always exists. | PROPOSE FIX | [G07](#g07) |
| `style-3-8` | Decision legend | `Author` is missing from the legend; two terms for one role. | PROPOSE FIX | [G08](#g08) |
| `style-3-9` | Phase 1 step 0 | Validator on Python 3.9 stated without recorded evidence. | PROPOSE FIX | [G09](#g09) |
| `style-3-10` | Runner, gates | Names used before definition; "flag" and "anchor" not tied to fields. | PROPOSE FIX | [G10](#g10) |

## Proposed Edit Groups

Line numbers refer to the reviewed plan revision.
No edit changes the specification, `src/`, `tests/`, or `pyproject.toml`.

### G01

**Findings:** `style-3-1`, `codebase_details-3-2`.

*   Verification, whitespace line: replace "`git diff --check` exits 0." with "`git diff --check 7d3fef1` exits 0 after every phase."

### G02

**Finding:** `style-3-2`.

*   Replace the `MemoryError` sentence with "`MemoryError` propagates because Section 2.8 states that memory exhaustion can prevent delivery of a typed `RunFailure` and must not be relabelled as `MechanicsError`; among `Exception` subclasses, D12 exempts only `MemoryError`, so a callback's `RecursionError` or `SystemError` is wrapped like any other callback failure."

### G03

**Finding:** `style-3-3`.

*   Replace "D12 narrows five specification passages … Failure Resolver Errors bullets." with "D12 narrows six specification passages that say any callback failure or cancellation raises a typed error: the two Section 3.5 sentences for the umpire review and the failure resolver, Edge Cases 6 and 14, and the Section 7 "Umpire Audit and Errors" and "Failure Resolver Errors" bullets."
*   D12 Source cell: replace "the Section 7 Umpire Audit and Failure Resolver Errors bullets" with "the Section 7 "Umpire Audit and Errors" and "Failure Resolver Errors" bullets".

### G04

**Finding:** `style-3-4`.

*   Replace "The same method confirmed the Invariant 14 golden vectors and the Section 3.4 worked example:" with "The same method confirmed the draw values of the Invariant 14 golden vectors and of the Section 3.4 worked example:".

### G05

**Finding:** `style-3-5`.

*   Replace "Those tests check the legacy mechanics, not Spec 1.1.2." with "The 8 legacy tests check the legacy mechanics, not Spec 1.1.2.", and move the bullet to directly after the bullet stating that the legacy tests pass.

### G06

**Finding:** `style-3-6`.

*   Replace "makes nested model instances, including ones built with `model_construct`, pass full validation" with "subjects nested model instances, including ones built with `model_construct`, to full validation".

### G07

**Finding:** `style-3-7`.

*   Runner step 2: replace "No callable has been invoked and no `random.Random` exists before step 3." with "Steps 1 and 2 invoke no callable and construct no `random.Random`."

### G08

**Finding:** `style-3-8`.

*   Replace "The human developer made decisions D1 to D4 and confirmed D12." with "The human developer (Source `Author`) made decisions D1 to D4 and confirmed D12."
*   Header: replace "which the author confirmed on 2026-11-17" with "which the human developer confirmed on 2026-11-17".
*   D12 paragraph: replace "The author confirmed this trade-off on 2026-11-17." with "The human developer confirmed this trade-off on 2026-11-17."

### G09

**Finding:** `style-3-9`.

*   Add a Starting Baseline bullet: "`python3 "$HOME/.local/share/artifice/scripts/validate_egm.py" . --spec 001` exits 0 at `7d3fef1` on the default `python3`."
*   Phase 1 step 0: replace "The validator runs on the system Python 3.9." with "Use the default `python3`; the validator does not need the project environment."

### G10

**Finding:** `style-3-10`.

*   `validate_peer_evaluation` step 1: "`evaluation = _validate_output(raw, PeerEvaluation, PeerReviewError)`."
*   `validate_peer_evaluation` step 4: "If `shift == 0`: set `biased_shift_applied` (the flag) to `False` and `cited_anchor` (the anchor) to `None`."
*   Runner step 3: "**Tables:** set `tables` and `source` to `request.spark_tables` and `"request"`, or to `default_spark_tables()` and `"trio-d66-v1"`."
*   Runner step 6: append "Start with `records = []`."
*   Runner step 7: replace "from `0` to `turn_count - 1`" with "from `0` to `request.turn_count - 1`".
*   Runner step 7.3: append "Collect the results, in that order, as `evaluations`."

### G11

**Findings:** `implementation_readiness-3-5`, `codebase_details-3-1`.

*   Add a Starting Baseline bullet: "In a temporary copy of the repository at `7d3fef1`, with `.python-version` set to `3.11`, `uv lock` resolved Pydantic 2.14.3, `uv sync --locked --extra dev` installed `tome` in editable mode through the existing Hatchling build backend, and the three gate commands passed on the 8 legacy tests without `PYTHONPATH`."
*   `scripts/lint.sh`: append "`uv run` installs the project in editable mode through the existing Hatchling build backend, so the gate needs no `PYTHONPATH`; if that build fails, stop and raise it with the human developer, because `pyproject.toml` is outside the file boundary."

### G12

**Finding:** `implementation_readiness-3-1`.

*   Runner "Snapshots": replace with "Every model argument is a fresh `model_copy(deep=True)`; every list argument is a new list, and a list of models holds a fresh `model_copy(deep=True)` of each element, made for that call."
*   `test_callbacks_receive_isolated_snapshots`: replace "mutating arguments does not affect the result" with "callbacks that append to `world_state.canon_facts`, rename an actor, append to `proposal.supporting_pros`, set `peer_evaluations[0].final_vote`, and append to `spark_tags` and `candidate_voter_ids` leave the result identical to an unmutated run".

### G13

**Finding:** `implementation_readiness-3-2`.

*   Phase 4 "Umpire Audit and Errors (run)" row: append "`test_umpire_review_receives_validated_evaluation`: the Section 7 vector run through `run` with `ScriptedCallbacks`; `umpire_calls[0][2][0]` has `biased_shift_applied` `True` and `cited_anchor` `"Fact 1."`, and equals the turn record's `evaluation_before_reversion`."

### G14

**Finding:** `implementation_readiness-3-3`.

*   Replace "the same override with reversed key order" with "the same override with the five table names in reverse order and each table's d66 keys in reverse order".

### G15

**Finding:** `implementation_readiness-3-4`.

*   Add a Phase 4 traceability row "D3 (public API)": "`test_public_api_exports`: `tome.engine.__all__` contains exactly the names listed in Target File 13; `set(tome.__all__) == set(tome.engine.__all__) | {"__version__"}`; and `tome.run is tome.engine.runner.run`."

### G16

**Coordinator correction to round-two edit F14.**

*   Umpire row: remove "; and the upward vector of baseline -1, final 0, and anchor `"Fact 1."`, which reverts to -1" from the end, and insert "; and the upward vector of baseline -1, final 0, and anchor `"Fact 1."`, which reverts to -1" directly after the `test_umpire_rejection_reverts_and_records` Section 7 vector clause.

## Approval Boundary

The human selected "auto accept" on 2026-11-18.
All 16 edit groups were applied to the plan in one batch.
This does not change the specification, approve the plan, or authorize implementation.

## Applied Resolution and Verification

*   Accepted and applied findings: 17, plus the G16 correction.
*   Contested: 0.
*   Escalated: 0.
*   Declined: 0.
*   Unaddressed approved fixes: 0.
*   Round-three clean status remains **No**; the clean streak remains **0 of 2**.
*   Post-resolution plan: 505 lines; the Detailed Implementation Plan still starts at line 15.

**G15 formatting adjustment:** the `|` set-union operator in the new D3 row is written as `\|`, because an unescaped `|` inside a table cell splits the cell in Markdown.
The rendered text matches G15.

Checks after applying:

*   Every applied text is present and none of the replaced text remains; the moved legacy-test bullet now follows the bullet stating that the legacy tests pass.
*   Plan tables keep consistent column counts; links, whitespace, and `git diff --check` pass.
*   The Phase 5 search still reports the 9 current legacy imports.
*   The specification, `src/`, `tests/`, and `pyproject.toml` are unchanged from `7d3fef1`; the targeted EGM validator passes.
