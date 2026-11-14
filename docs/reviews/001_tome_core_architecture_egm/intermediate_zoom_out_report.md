# EGM Stage 8: Intermediate Zoom Out

**Status:** Completed
**Mode:** REVIEW
**Target:** [TOME core architecture](../../designs/001_tome_core_architecture.md), full file, lines 1-1052
**Date:** 2026-11-13
**Specification:** 1.1.1
**Interface contract:** 1.1.0
**Execution:** Fresh general-purpose subagent reading the official zoom-out persona and standard

## Overall Intermediate Assessment

The design addresses the README's root problem: exploring uncertain multi-actor interactions through structured narrative proposals, grounded voting, stochastic mechanics, and human adjudication.
Its provider-neutral boundary and deferred infrastructure avoid unnecessary engine responsibilities.

The preceding reports identify resource and semantic concerns, but not every proposed remedy is a current-contract correction.
Request-local scheduling is explicitly chosen behavior.
Compact audit records, resumable rounds, and provider-draft schemas would change the interface rather than repair an internally inconsistent implementation requirement.

**No new findings beyond the preceding reports were identified.**
The findings below independently reassess those concerns using this checkpoint's stable IDs.
No additional architecture-level contradiction was established.
The specific wording/interface contradictions below remain present in the unchanged target.
Historical approvals and deferrals do not resolve them.

## Carried-Forward Findings, Independently Reassessed

### egm-zoom-out-2-1: Audit growth needs an operating envelope

**Severity:** Major
**Affected scope:** Section 3.1, line 234; Section 3.4, lines 411-416 and 633-650; Invariant 11, lines 815-818; Section 8, line 1047

**Consequence:** Complete before/after canon arrays contain `2nC + n^2` fact occurrences for n turns starting with C facts.
Ten thousand turns with roughly 200-byte facts approach 20 GB of snapshot text alone.
A finite turn count therefore does not establish practical feasibility.
Actor count and unconstrained narrative lengths introduce additional work and size uncertainty.

**Simplicity rationale:** Full snapshots can simplify inspection of short runs, but their duplication is structural.
Caching, queues, persistence, or internal structural sharing would not remove the specified JSON duplication.
Conversely, introducing replay machinery before defining the intended workload could also be unnecessary complexity.

**Recommendation:** Document the growth, intended workload assumptions, and caller-owned budgeting responsibilities for turns, actors, canon, and narrative payloads.
Explain admission ownership and resource-failure limitations without misclassifying resource exhaustion as the internal-defect-only `MechanicsError`.
Evaluate compact records separately as a versioned alternative; do not silently replace the mandatory 1.1.0 snapshots.

### egm-zoom-out-2-2: Canon's temporal meaning remains unspecified

**Severity:** Major
**Affected scope:** Sections 2.3-2.6, particularly lines 145 and 170-199; Section 3.1, lines 278-284; Invariant 6, lines 800-802

**Consequence:** After "Actor A has capability X" and "Actor A loses capability X" enter canon, both remain mechanically valid citation anchors.
The document does not explain whether these are historical assertions or simultaneously applicable truths, or who determines their present relevance.
Different adapters can consequently interpret the same changed world differently.

**Simplicity rationale:** Append-only narrative history is compatible with changing conditions.
The example does not itself prove an architectural contradiction.
The missing element is semantic ownership, not necessarily a mechanical capability tracker or fact-status database.

**Recommendation:** State canon's temporal interpretation and assign applicability judgment explicitly to proposal generators, peers, and the umpire where appropriate.
If canon is historical evidence, clarify that successful citation matching does not establish a capability's current availability.
Do not introduce automatic supersession or "latest statement wins" mechanics merely to supply this explanation.

### egm-zoom-out-2-3: Reason-code wording overstates reproducibility

**Severity:** Nit
**Affected scope:** Section 3.4, line 648; contrasted with line 458 and Invariant 10, lines 810-814

**Consequence:** "Given the same inputs and umpire decisions" promises identical reason text without the seed and adapter-output conditions specified elsewhere.
Otherwise identical unseeded requests can resolve differently and select `proposal-succeeded` versus `failure-consequence`.

**Simplicity rationale:** The existing fixed vocabulary already provides deterministic classification of resolved changes.
No additional reproducibility subsystem is needed.

**Recommendation:** Say that the changed field and resolved outcome determine its `ReasonCode`, or explicitly reference the complete reproducibility conditions in Invariant 10.

### egm-zoom-out-2-4: Reversion wording promises audit coverage not retained

**Severity:** Nit
**Affected scope:** Section 3.3, line 343; Section 2.4, lines 147-152; Section 3.4, lines 624-626; Section 3.5, lines 740-746

**Consequence:** The statement that `umpire_rejections` records "the reversion" includes mechanical reversions in ordinary reading.
Those reversions can occur without an umpire entry.
The result retains the validated evaluation, not a separate record of every invalid attempted shift.

**Simplicity rationale:** Retaining ordinary arguments while normalizing votes is an explicit design choice.
Correcting the description is simpler than adding raw-provider histories or a new mechanical-rejection logging subsystem.

**Recommendation:** State that the public argument remains unchanged after either kind of reversion, while `umpire_rejections` records only human-umpire rejections.
Describe the existing audit coverage accurately rather than expanding it implicitly.

### egm-zoom-out-2-5: Blanket callback return rule contradicts the list callback

**Severity:** Nit
**Affected scope:** Section 3.5, line 676 and lines 707-712; rejection-return explanation, lines 738-739

**Consequence:** "Each callable returns a plain mapping or an equivalent model" conflicts with `UmpireReview` returning a list, including `[]`.
A bridge following the blanket instruction could wrap that list in an undeclared object and produce invalid callback output.

**Simplicity rationale:** The explicit callback signature already expresses the intended interface.
A universal result wrapper would add complexity solely to reconcile an inaccurate sentence.

**Recommendation:** Distinguish object-returning callbacks from `UmpireReview`.
Specify that its list elements are mappings or equivalent models with the declared rejection fields.

### egm-zoom-out-2-6: Executable-adapter trust assumptions need explicit limits

**Severity:** Nit
**Affected scope:** Section 2.0, lines 69-80; Section 3.5, lines 658-718, 733-735, and 748-752

**Consequence:** Caller-owned executable callbacks receive complete world-state snapshots.
Snapshot isolation protects mechanical state from mutation.
It does not sandbox executable code or prevent a provider adapter from transmitting that state externally.

**Simplicity rationale:** This warrants boundary documentation, not authentication, deployment controls, or an in-engine sandbox.
Those additions would conflict with the deliberately narrow engine scope.

**Recommendation:** State that callbacks are trusted executable integrations, distinguish state isolation from confidentiality, and assign provider-egress and data-handling controls to the caller.
The preceding security-documentation concern is upheld, but it does not establish a newly demonstrated vulnerability.

## Evaluation of Prior Major Recommendations

### Upheld Concerns

- **Quadratic audit growth:** The calculations in `egm-zoom-out-1-2`, `egm-design-1-2`, `egm-structural-1-2`, and the Inventive Catalyst report follow directly from the contract.
  Prior deferral does not supply workload assumptions or mitigation.
  The current finding is `egm-zoom-out-2-1`.
  However, mandatory immediate replacement with deltas is stronger than the evidence requires.
- **Canon interpretation:** `egm-comprehension-1-1` identifies a semantic gap.
  The appropriate first mitigation is explanatory ownership, as in `egm-zoom-out-2-2`, not restoration of mechanical trackers.
- **Missing alternatives evaluation:** The unchanged target still does not provide the substantive comparisons requested by `egm-design-1-1` and `egm-structural-1-1`.
  Their reported feature-standard Blockers are not erased by this checkpoint.
  A focused discussion should compare full snapshots with compact audit records, and separately compare run-wide atomic publication with turn-level completion.
  Audit representation and publication atomicity are independent choices: compact records need not imply partial publication.
  Requiring exhaustive discussion of every removed historical feature would create unnecessary scope.
- **Adapter trust documentation:** The scope-compatible mitigation in `egm-structural-1-3` is sound.
  This checkpoint treats it as a boundary-documentation Nit, not evidence that the design promises secure execution of untrusted callbacks.
- **Reason-code and reversion claims:** Both style-review Major concerns identify inaccurate sentences.
  This checkpoint grades them as Nits because the detailed behavior is already specified and the remedies need not alter mechanics or schemas.

### Contested Interpretation

**Finding:** `egm-zoom-out-1-1`, request boundaries change scheduling.

Its two-actor example holds: one two-turn request with `[A, B]` executes A then B; two one-turn requests with that same order execute A twice and do not complete a request-local round.

That consequence is nevertheless specified consistently in Invariants 1 and 12, execution step 4, and Edge Case 8.
The contract does not promise request-chunk equivalence or cross-request round continuation.
A complete world state need not contain progress through an order explicitly defined as run-local.

The scheduling consequence deserves prominent explanation, but requiring full rounds or preserving a cursor is not a necessary correction to 1.1.0.
Either would revise explicitly chosen behavior.

## Recommendations Requiring a New Interface Version

- **Compact canon deltas or references:** These replace mandatory complete `StateChange.before` and `after` values.
  They require a versioned result contract and explicit reconstruction assumptions.
  Run-wide atomic publication can remain unchanged.
- **Resumable partial rounds or complete-round-only requests:** A cursor changes the closed state schema.
  A full-round restriction changes accepted requests and specified partial-round behavior.
- **Engine-owned peer metadata:** Removing required `biased_shift_applied` from provider output, or introducing `PeerEvaluationDraft`, is a simplification opportunity from `egm-zoom-out-1-3`, but changes callback validation.
  It is not permission to omit the field under 1.1.0.
- **Effective seed or digest fields in results:** These are future result-schema additions, not repairs to the current conditional reproducibility promise.
  Pinning a table digest in documentation alone need not change the interface.
  Changing table contents already requires a new table-set version.
- **Engine-enforced resource quotas or new stable resource errors:** These change acceptance or failure semantics.
  Caller-owned preflight policies and documented workload assumptions can be clarified without silently changing 1.1.0.

## Reuse, Altitude, and Provenance

The supplied default tables are appropriate reuse.
Searches found existing model, dice, orchestration, and grounding components.
Their legacy step-dice, trait, urgency-ordering, and tier-pairing behavior prevents unchanged wholesale reuse.
Adaptation within those existing modules is preferable to another generic engine framework.

The exact random draw sequence and golden vectors support an observable reproducibility contract.
They are justified detail, not an altitude violation.

The target and all supplied review reports were read completely in bounded ranges, with truncated portions completed.
The linked historical review and tables were also read completely.

**Required prior-stage reports:**

- [Initial zoom out](zoom_out_report.md).
- [Comprehension](comprehension_report.md).
- [Critic review](critic_report.md).

**Additional repository reads:**

- [README](../../../README.md).
- [Dice](../../../src/tome/dice.py).
- [Models](../../../src/tome/models.py).
- [Runner](../../../src/tome/runner.py), lines 1-105.
- [Validator](../../../src/tome/validator.py), lines 1-105.

Symbol searches covered `src/tome/*.py`.
Additional searches located target line references.
Read-only line counts verified coverage.

No tests, compilation, network access, file modifications, parent conversation, session artifacts, or further delegation were used.
