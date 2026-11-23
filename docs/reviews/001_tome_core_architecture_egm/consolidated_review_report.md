# Consolidated EGM Review: TOME Core Architecture

**Target:** [TOME core architecture](../../designs/001_tome_core_architecture.md)
**Date:** 2026-11-13
**Specification:** 1.1.1
**Interface contract:** 1.1.0
**Reviewed revision:** `6882fab977ee25a61b8cd52664399315feaeb499`
**Specification SHA-256:** `f15a4b6c7eb2976a1fe8e73355897e0bad44c92b081452cbaca9ced6081825a9`
**Verdict:** Revisions Required
**Review scope:** Feature specification, stages 5-8
**Implementation readiness:** Not assessed; Stage 9 is not applicable by explicit user choice

## 1. Decision

The specification does not yet pass the official feature-specification standard.
It lacks the standard's mandatory evaluation of alternatives.
It also needs workload and resource-limit guidance, and an explanation of how historical canon facts remain relevant when narrative conditions change.

These findings do not require discarding the design or immediately changing Interface Contract 1.1.0.
The first response should be focused documentation and human decisions about the existing trade-offs.
The raw proposals to change scheduling, replace snapshots, or remove required peer metadata are not permission to alter the contract.

The consolidated result is **1 Blocker, 2 Major actions, and 8 Nit actions**, after deduplication and severity reassessment.
One additional peer-schema suggestion is recorded for a future interface decision.
The initial scheduling complaint is contested as a current-contract defect.

No specification or implementation changes were made.
The existing approval metadata and [historical review](../001_tome_core_architecture_review.md) were preserved.
Their recorded approval and the previously passing mechanical validator do not establish compliance with the additional official review criteria.

## 2. Execution and Scope

The user selected the consolidated all-rubrics preset, with no additional reviewer context.
The document has no separate implementation-plan section.
After that was reported, the user approved running stages 5-8 and recording Stage 9 as not applicable.
The feature range was the complete specification, lines 1-1052.

| Stage | Reviewer | Status | Report |
| :--- | :--- | :--- | :--- |
| 5: Initial Zoom Out | `egm-zoom-out` | Completed | [Initial report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/zoom_out_report.md) |
| 5: Initial Zoom Out | `egm-inventive-catalyst` | Completed | [Initial report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/zoom_out_report.md) |
| 6: Comprehension | `egm-comprehension` | Completed | [Complete paraphrases and findings](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/comprehension_report.md) |
| 7: Critic | `egm-design` | Completed | [Critic report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/critic_report.md) |
| 7: Critic | `egm-structural` | Completed | [Critic report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/critic_report.md) |
| 7: Critic | `egm-style` | Completed | [Critic report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/critic_report.md) |
| 8: Intermediate Zoom Out | `egm-zoom-out` | Completed | [Intermediate report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/intermediate_zoom_out_report.md) |
| 9: Implementation Readiness | No reviewer dispatched | Not applicable | No separate implementation plan; user-approved exclusion |

All seven requested reviewers completed.
No reviewer failure or retry occurred.
The four stage reports retain all 24 raw finding IDs, including six independently reassessed, carried-forward findings from Stage 8.
Stage 8 found no additional issue beyond the preceding reports.

This was an uninterrupted, single-pass review without remediation.
It was not the iterative resolve/review loop, and no two-clean-round convergence or new approval is claimed.

## 3. Prioritized Actions

All current actions below remain open.
The priorities reflect consolidation, not the unchanged raw reviewer severities.

| ID | Priority | Required action | Scope |
| :--- | :--- | :--- | :--- |
| A01 | 🔴 Blocker | Document viable alternatives and concrete reasons for the selected trade-offs. | Overview and architecture, Sections 1-5 |
| A02 | 🟡 Major | Explain result growth, intended workload assumptions, and caller-owned resource budgets and limits. | Sections 3.1 and 3.4; Invariant 11; Section 8 |
| A03 | 🟡 Major | Define canon's temporal meaning and responsibility for judging superseded conditions. | Sections 2.3-2.6 and 3.1; Invariant 6 |
| A04 | 🟢 Nit | State the trusted-executable-adapter assumption and confidentiality limits of snapshots. | Sections 2.0 and 3.5 |
| A05 | 🟢 Nit | Calibrate the reason-code reproducibility sentence to its actual conditions. | Section 3.4, line 648 |
| A06 | 🟢 Nit | Distinguish mechanical vote reversions from human rejections in the audit description. | Section 3.3, line 343 |
| A07 | 🟢 Nit | Correct the blanket mapping/model return rule for the list-returning `UmpireReview`. | Section 3.5, line 676 and callback signature |
| A08 | 🟢 Nit | Narrow the overview's grounding claim to supporting arguments and shifted votes. | Section 1, line 34 |
| A09 | 🟢 Nit | Separate historical pending-approval wording from current approval metadata. | Changelog, line 18; Section 8, line 1050 |
| A10 | 🟢 Nit | Repair the front-matter heading hierarchy and Markdown execution substeps. | Lines 13 and 21; Section 5, lines 873-889 |
| A11 | 🟢 Nit | Describe d66 as two ordered d6 faces forming a lookup key. | Section 2.2, line 119 |

### A01: Alternatives, not a replacement design

The official feature-specification standard explicitly requires evaluation and rejection of viable alternatives for concrete reasons.
A list of removed features or non-goals does not supply those reasons.
Both the design and structural reviewers independently reported this as a Blocker.

Compare consequential choices already present in the engine contract.
At minimum, address full snapshots versus compact audit records, and run-wide atomic publication versus turn-level completion.
Treat audit representation and publication atomicity as separate decisions.
Compact records do not inherently require partial publication.

Explain the selected request-local ordering semantics when discussing execution trade-offs.
Document the actor/narrative-state rationale where useful.
Do not add an exhaustive history of every rejected feature or revive excluded infrastructure.

**Closure evidence:** A fresh reader can identify a viable competing approach, its concrete costs, and why the chosen approach fits this milestone.
No exact section title is required by the standard.

### A02: Operating envelope and resource ownership

The result schema requires complete before/after canon arrays every turn.
For T turns starting with C facts, those arrays alone contain `2CT + T^2` fact occurrences.
With one initial fact, 10,000 turns, and roughly 200 bytes per fact, this is about 20 GB of snapshot text before JSON overhead.
This is an analytical example, not a measured implementation benchmark.

Peer-review calls also scale as `T * (A - 1)` for A actors.
Unbounded narrative lengths add uncertainty to input, output, and provider work.
A finite positive turn count is not a practical resource limit.

Document intended workloads and the caller's preflight responsibilities.
Explain which guarantees do not cover resource exhaustion or process termination.
Do not silently reject previously valid requests with new engine quotas, or label resource exhaustion as the internal-defect-only `MechanicsError`.
New engine limits or stable resource-error semantics require an explicit contract decision.

**Closure evidence:** The specification states growth, workload assumptions, mitigation ownership, and the limits of atomic failure reporting.
Changing the serialized audit representation is optional and must be considered separately as a versioned alternative.

### A03: Historical facts versus present applicability

The mechanically valid anchor "Actor A has capability X" can remain in canon after "Actor A loses capability X" is appended.
The contract explains citation matching, but not the temporal interpretation of these statements.

Clarify whether canon is historical evidence, currently applicable truth, or another explicitly defined model.
State who judges relevance and supersession when generating proposals, voting, and umpiring.
The existing distinction between citation validity and logical judgment can support this explanation.

**Closure evidence:** A fresh reader can explain how both example statements may remain in canon and who decides whether capability X can justify a later argument.
Do not introduce mechanical trackers, automatic fact invalidation, or a "latest statement wins" rule without a separate human design decision.

### A04-A11: Local documentation repairs

These actions can describe the existing contract without adding engine features.
In particular:

- Snapshots isolate data mutations; they do not sandbox trusted callback code or control provider disclosure.
- A fixed `ReasonCode` vocabulary is determined by the changed field and outcome, not by identical unseeded requests alone.
- `umpire_rejections` records human-umpire rejections, not every mechanically invalid attempted shift.
- `UmpireReview` returns a list; its rejection elements follow the declared object shape.
- A completed historical approval should not be labelled the "current draft."
- Lettered execution substeps should use valid nested Markdown list structure.

The intermediate reviewer reduced the adapter-trust and two wording concerns from Major to Nit.
The detailed contract already establishes the relevant behavior, and the remedies need not change schemas or mechanics.
This severity reassessment does not mark the actions fixed.
No exploitable vulnerability was established by the adapter-trust observation.

## 4. Contested and Versioned Suggestions

### D01: Request-local scheduling is an intentional contract choice

The initial reviewer observed that one two-turn request with order `[A, B]` runs A then B, while two one-turn requests with the same order run A twice.
That observation follows from the specification.
The claim that it is a missing continuation-state defect does not.

Invariants 1 and 12, execution step 4, and Edge Case 8 consistently define a fresh order and request-local rounds.
The contract does not promise equivalent results when a run is split across requests.
Keep the behavior under 1.1.0 unless the human explicitly chooses a different model.
A01 should explain this trade-off and make its consequence visible.

### F01: Engine-owned peer metadata

`biased_shift_applied` is required in peer output although the engine recomputes it.
A `PeerEvaluationDraft` or removing that provider requirement could reduce malformed-output states.
This is a future interface suggestion, not a current error.
The field remains required under 1.1.0.

### F02: Compact audit records

Replacing complete snapshots with append events can reduce output duplication.
It also creates replay, reconstruction, and consumer-migration responsibilities.
Consider that option in A01 and A02, but do not silently implement it under the current closed schema.

Other historical suggestions remain separate decisions: returning the effective seed and adding result digest fields would change the result schema.
Pinning an existing table digest in documentation alone need not change the interface.
Changing the default table contents already requires a new table-set version.

## 5. Traceability Matrix

Every raw finding maps to an action or an explicit disposition.
Raw severities remain available in the linked stage reports.

| Raw finding ID | Reported severity | Consolidated action or disposition |
| :--- | :--- | :--- |
| egm-zoom-out-1-1 | Major | D01: Contested as a defect; document the trade-off in A01. |
| egm-zoom-out-1-2 | Major | A02; compare versioned compact records through A01/F02. |
| egm-zoom-out-1-3 | Nit | F01: Future peer-schema decision; no current field removal. |
| egm-inventive-catalyst-1-1 | Nit, advisory | A02/F02: Same snapshot-growth concern and a versioned alternative. |
| egm-comprehension-1-1 | Major | A03: Define temporal meaning and judgment ownership. |
| egm-comprehension-1-2 | Nit | A07: Correct the mapping/list return wording. |
| egm-design-1-1 | Blocker | A01: Mandatory alternatives evaluation. |
| egm-design-1-2 | Major | A02: Resource growth and mitigation. |
| egm-structural-1-1 | Blocker | A01: Duplicate of the same missing alternatives requirement. |
| egm-structural-1-2 | Major | A02: Workload limits and caller mitigation ownership. |
| egm-structural-1-3 | Major | A04: Reassessed as a trust-boundary documentation Nit. |
| egm-structural-1-4 | Nit | A10: Repair heading hierarchy. |
| egm-structural-1-5 | Nit | A10: Repair execution-list rendering. |
| egm-style-1-1 | Major | A05: Reassessed as a reproducibility-wording Nit. |
| egm-style-1-2 | Major | A06: Reassessed as an audit-description Nit. |
| egm-style-1-3 | Nit | A08: Narrow the grounding claim. |
| egm-style-1-4 | Nit | A09: Label approval chronology accurately. |
| egm-style-1-5 | Nit | A11: Use direct lookup-key terminology. |
| egm-zoom-out-2-1 | Major | A02: Independent reassessment of the resource concern. |
| egm-zoom-out-2-2 | Major | A03: Independent reassessment of temporal canon semantics. |
| egm-zoom-out-2-3 | Nit | A05: Independent reassessment of reproducibility wording. |
| egm-zoom-out-2-4 | Nit | A06: Independent reassessment of reversion coverage. |
| egm-zoom-out-2-5 | Nit | A07: Independent reassessment of callback return shape. |
| egm-zoom-out-2-6 | Nit | A04: Independent reassessment of adapter trust limits. |

## 6. Where to Resume EGM

Return to Elephant resolution or drafting for A01-A03, not directly to implementation handoff.
Discuss any material change to canon semantics, resource admission, scheduling, or output shape with the human before revising the contract.
The remaining local documentation repairs can be grouped coherently with the approved revision.

After revisions, run the applicable fresh review or confirmation.
Do not convert the older mechanical-validator pass into approval under this broader standard.
When the specification passes and the human signs off, prepare a separate implementation plan if Stage 9 readiness is desired.
The legacy engine still needs a contract-first implementation migration; this report did not verify that implementation.

## 7. Provenance and Limitations

The slash-command skill name was not registered in this harness.
The orchestrator read the user-supplied installed `skills/egm-review/SKILL.md`, its harness guidance, the applicable personas and standards, and the review-loop guidance.
It used the documented general-purpose-subagent fallback to execute the official review stages.

Each reviewer started in a separate native task context.
No parent conversation was supplied in the review prompts.
Host-level exclusion of project or user instructions was not verified.
The initial zoom-out reviewer reported loading the local `spec-egm` workflow instructions.
This report therefore does not claim that reviewers received no host instructions.

The specification's two local Markdown links were automatically included as context according to the plugin rules:

- [Default spark tables](../../../src/tome/tables.py).
- [Historical Goldfish review](../001_tome_core_architecture_review.md).

The comprehension reviewer received neither file and read the target alone with its persona.
The intermediate reviewer received the preceding three stage reports, as required by the Stage 8 workflow.
Zoom-out reviewers performed the additional root-alignment and reuse reads listed in their reports.

No reviewer ran tests, compiled code, accessed the network, or modified files.
The orchestrator wrote only these review deliverables.
No code, specification, approval history, or implementation plan was changed.
There is no implementation-readiness, performance-benchmark, security-audit, or convergence certification in this report.
