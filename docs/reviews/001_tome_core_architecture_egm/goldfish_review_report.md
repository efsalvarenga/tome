# Goldfish Annotated Review Report

**Status:** resolved
**Target:** [TOME core architecture](../../designs/001_tome_core_architecture.md), full file, original lines 1-1052
**Date:** 2026-11-14
**Source specification:** 1.1.1
**Resolved specification:** 1.1.2, Under Review
**Interface contract:** 1.1.0
**Source SHA-256:** `f15a4b6c7eb2976a1fe8e73355897e0bad44c92b081452cbaca9ced6081825a9`
**Resolved SHA-256:** `580f4919c88ce2146f2f6b28e4fd25d1aa782d9cff3beeec1bfbe52b96ecf8cb`
**Findings index:** [Consolidated review](consolidated_review_report.md)
**Coupled documentation:** [README](../../../README.md), version/status references only

## Resolution Summary

| Category | Original findings | Resolution |
| :--- | ---: | :--- |
| PROPOSE FIX | 21 | Applied the eleven shared edit groups below. |
| CONTEST | 1 | Preserved explicitly specified request-local scheduling; no automatic fix applied. |
| ESCALATE | 0 | No contest depends on evidence unavailable to its reviewer. |
| DECLINE | 2 | Did not introduce versioned peer-draft or compact-audit schemas. |

Original severities are preserved: 2 Blocker findings, 10 Major findings, and 12 Nit findings.
The earlier consolidated priorities do not replace the severities of the original findings in this report.
Duplicate findings share an edit group; accepting both does not apply the same edit twice.

The human confirmed that canon is append-only history and that adapters and the umpire judge current relevance.
That decision informs E03.
No automatic fact supersession, tracker, or mandatory new umpire pause is proposed.

The human selected "Auto accept: apply all proposed fixes" on 2026-11-14.
All approved groups were applied once to the specification and its coupled README references.

The applied revision keeps Interface Contract 1.1.0.
It retains complete snapshots, request-local rounds, required peer metadata, existing error codes, callback signatures, and random draw order.
It introduces no engine quota or new request field.
E09 records the documentation revision as Spec 1.1.2, Under Review, with fresh review and human sign-off still pending.

Resolution means that the approved dispositions and documentation edits have been applied, not that fresh Goldfish approval has been obtained.
The cost of complete snapshots remains a documented trade-off under the approved caller-owned resource guidance.
This resolution does not claim that output growth has been eliminated.

## Prioritized Findings & AI Suggestions

### egm-design-1-1 [egm-design] - Severity: Blocker

* **Affected Scope:** Sections 1-5, original lines 29-905; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/critic_report.md).
* **Discrepancy Description:** The overview names avoided approaches, and the changelog records replaced mechanics, but neither evaluates viable alternatives with concrete rejection reasons.
* **Rationale:** Consequently, the document does not satisfy the standard's mandatory Alternatives Rule.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** The assigned feature standard explicitly requires substantive alternatives.
  Add a decision comparison for choices already present, without inventing historical maintainer decisions or changing the contract.
* ***Proposed Edit:***
  * Location: Section 1, after Non-Goals.
  * Change: Apply [E01](#e01).

### egm-structural-1-1 [egm-structural] - Severity: Blocker

* **Affected Scope:** Changelog and Section 1, original lines 17-64; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/critic_report.md).
* **Discrepancy Description:** The document records removed mechanics and deferred infrastructure, but does not explain their trade-offs against the selected design.
  Saying an option was removed, excluded, or deferred is not an evaluation.
* **Rationale:** A fresh engineer can implement the chosen contract but cannot assess why consequential design choices are preferable.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** This is the same missing alternatives requirement as `egm-design-1-1`, not a second demand for a different template.
* ***Proposed Edit:***
  * Location: Section 1, after Non-Goals.
  * Change: Apply [E01](#e01) once.

### egm-zoom-out-1-1 [egm-zoom-out] - Severity: Major

* **Affected Scope:** Invariants 1 and 12; Section 5; Edge Case 8; original lines 784-787, 818-822, 890-892, and 927-929; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/zoom_out_report.md).
* **Discrepancy Description:** With two actors and supplied order `[A, B]`, one two-turn request executes A then B and completes a round.
  Two chained one-turn requests execute A twice and never advance `session_index`.
* **Rationale:** A caller's batching choice becomes a domain rule controlling actor participation and simulated time.
* ***AI Suggestion:*** CONTEST
* ***Justification:*** The example follows the contract, but the claim that continuation state is missing assumes cross-request continuation that the contract explicitly excludes.
  Invariant 1 says every new request starts at the beginning of its own order.
  Invariant 12, Section 5 step 4, and Edge Case 8 repeat that incomplete rounds do not resume.
  These decisions were in the target the reviewer could read.
  Requiring complete rounds or adding a persisted cursor would change accepted requests or the closed state schema.
* ***Proposed Edit:***
  * Location: None for the contested behavior.
  * Change: Do not add a cursor or full-round restriction.
  * Related valid fix: E01 explains the existing scheduling trade-off under the separately accepted alternatives findings.

### egm-zoom-out-1-2 [egm-zoom-out] - Severity: Major

* **Affected Scope:** Sections 2.5 and 3.4, original lines 170-175, 411-416, and 634-637; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/zoom_out_report.md).
* **Discrepancy Description:** Each turn records the complete canon before and after appending one fact.
  For n turns starting with C facts, those snapshots alone contain `2nC + n^2` fact occurrences, although the run introduces only n facts.
* **Rationale:** This is contract-mandated duplication, not a speculative performance concern requiring caching or benchmarks.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** The growth is real.
  Document its cost, admission ownership, and failure limits rather than silently replacing mandatory 1.1.0 fields.
  E01 evaluates compact records as an alternative.
  E02 mitigates the current-contract risk through caller-owned budgeting; it does not remove quadratic serialization.
* ***Proposed Edit:***
  * Location: New Section 2.8 and resource/atomicity cross-references.
  * Change: Apply [E02](#e02), with E01's independent audit-representation comparison.

### egm-comprehension-1-1 [egm-comprehension] - Severity: Major

* **Affected Scope:** Sections 2.3-2.5 and 3.1; Invariant 6; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/comprehension_report.md).
* **Discrepancy Description:** Canon's interpretation when narrative conditions change is unclear.
* **Rationale:** The document does not explain whether canon represents historical assertions or currently applicable truths, how superseded conditions should be interpreted, or who makes that determination.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** This comprehension gap is valid.
  The human has now explicitly chosen append-only history with relevance judged by adapters and the umpire.
  Explain that choice and test the existing mechanical boundary without adding automatic semantic validation.
* ***Proposed Edit:***
  * Location: New Section 2.7 and the Section 7 unit-test strategy.
  * Change: Apply [E03](#e03).

### egm-design-1-2 [egm-design] - Severity: Major

* **Affected Scope:** Sections 3.1 and 3.4; Invariant 11; Section 8; original lines 234, 371, 635-636, 815-818, and 1047; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/critic_report.md).
* **Discrepancy Description:** Every turn appends one canon fact, and every turn record contains complete before/after canon arrays.
  With C initial facts and T turns, those snapshots contain `2CT + T^2` fact occurrences in serialized output.
* **Rationale:** Line 1047 acknowledges this as deferred, but supplies no workload assumptions, admission-control expectations, or mitigation.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** A finite turn count is not a capacity guarantee.
  E02 names the intended use, analytical growth, caller controls, and limits of typed error delivery.
  It does not invent a benchmarked capacity or a new engine rejection rule.
* ***Proposed Edit:***
  * Location: New Section 2.8; Sections 3.1, 4, 5, and 8.
  * Change: Apply [E02](#e02) and the historical/current-review separation in E09.

### egm-structural-1-2 [egm-structural] - Severity: Major

* **Affected Scope:** Sections 3.1, 3.4, and 8, original lines 234, 367-399, 633-636, and 1047; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/critic_report.md).
* **Discrepancy Description:** Strings have no maximum length; actor, canon, and turn counts have no documented operating envelope; every turn records complete before/after field values.
* **Rationale:** Callers receive no guidance for avoiding excessive output, memory demand, or provider work.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** The risk section must cover scale without importing hosting into the engine.
  Caller policies can bound their own requests and adapters while the schema remains unchanged.
* ***Proposed Edit:***
  * Location: New Section 2.8 and Section 3.1's length statement.
  * Change: Apply [E02](#e02).

### egm-structural-1-3 [egm-structural] - Severity: Major

* **Affected Scope:** Sections 2.0 and 3.5, original lines 69-80 and 658-715; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/critic_report.md).
* **Discrepancy Description:** The architecture passes complete world state to caller-owned, potentially LLM-backed executable callables without identifying disclosure risks, adapter trust assumptions, or corresponding caller-owned controls.
* **Rationale:** Isolated snapshots address mutation, not executable-code sandboxing or external disclosure.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** Preserve the original Major severity.
  Clarify the trusted-executable boundary and the caller's concrete data-handling decisions; do not add an engine sandbox or claim a demonstrated exploit.
* ***Proposed Edit:***
  * Location: End of Section 2.0.
  * Change: Apply [E04](#e04).

### egm-style-1-1 [egm-style] - Severity: Major

* **Affected Scope:** Section 3.4, original line 648; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/critic_report.md).
* **Discrepancy Description:** "Given the same inputs and umpire decisions, the engine produces the same `reason` text."
* **Rationale:** This reproducibility promise omits the seed and adapter-output conditions stated elsewhere.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** Preserve the original Major severity.
  Define reason classification from the changed field and outcome, and reference the complete existing reproducibility conditions.
* ***Proposed Edit:***
  * Location: The quoted sentence in Section 3.4.
  * Change: Apply [E05](#e05).

### egm-style-1-2 [egm-style] - Severity: Major

* **Affected Scope:** Section 3.3, original line 343; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/critic_report.md).
* **Discrepancy Description:** "It is not rewritten if the shift is reverted; `umpire_rejections` records the reversion, and the umpire judges the argument's fit when resolving a failure."
* **Rationale:** Invalid shifts can revert without producing such an entry.
  This overstates the audit record's specified coverage.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** Preserve the original Major severity.
  Correct the description of existing records without introducing a raw-provider or mechanical-rejection audit subsystem.
* ***Proposed Edit:***
  * Location: The quoted sentence in Section 3.3.
  * Change: Apply [E06](#e06).

### egm-zoom-out-2-1 [egm-zoom-out] - Severity: Major

* **Affected Scope:** Sections 3.1, 3.4, and 8; Invariant 11; original lines 234, 411-416, 633-650, 815-818, and 1047; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/intermediate_zoom_out_report.md).
* **Discrepancy Description:** Complete before/after canon arrays contain `2nC + n^2` fact occurrences for n turns starting with C facts.
* **Rationale:** Full snapshots can simplify inspection of short runs, but their duplication is structural.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** This independently supports the same resource documentation as the other growth findings.
  E02 keeps resource exhaustion distinct from an internal `MechanicsError`.
* ***Proposed Edit:***
  * Location: New Section 2.8 and atomicity cross-references.
  * Change: Apply [E02](#e02) once.

### egm-zoom-out-2-2 [egm-zoom-out] - Severity: Major

* **Affected Scope:** Sections 2.3-2.6 and 3.1; Invariant 6; original lines 145, 170-199, 278-284, and 800-802; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/intermediate_zoom_out_report.md).
* **Discrepancy Description:** After "Actor A has capability X" and "Actor A loses capability X" enter canon, both remain mechanically valid citation anchors.
* **Rationale:** The missing element is semantic ownership, not necessarily a mechanical capability tracker or fact-status database.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** E03 records the human's selected interpretation while retaining the existing optional human-review behavior.
* ***Proposed Edit:***
  * Location: New Section 2.7 and the Section 7 unit-test strategy.
  * Change: Apply [E03](#e03) once.

### egm-zoom-out-1-3 [egm-zoom-out] - Severity: Nit

* **Affected Scope:** Sections 2.4, 3.3, and 3.5, original lines 147-151, 330-337, 692-696, and 730; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/zoom_out_report.md).
* **Discrepancy Description:** A peer evaluation that otherwise meets the rules but omits `biased_shift_applied` fails schema validation and can abort the entire run, despite the engine ignoring the submitted flag and recomputing it.
* **Rationale:** This required provider field creates additional malformed-output states without contributing information to adjudication.
* ***AI Suggestion:*** DECLINE
* ***Justification:*** The simplification is a future interface choice.
  Section 3.3 explicitly requires the field, and Section 2.4 explicitly defines recomputation.
  Removing it or adding `PeerEvaluationDraft` would change callback validation under 1.1.0.
* ***Proposed Edit:***
  * Location: None.
  * Change: Keep the current schema; record the suggestion without implementing it.

### egm-inventive-catalyst-1-1 [egm-inventive-catalyst] - Severity: Nit

* **Affected Scope:** Sections 3.4 and 8, original lines 635-636 and 1047; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/zoom_out_report.md).
* **Discrepancy Description:** Per-turn auditability is coupled to retaining complete before-and-after canon arrays.
* **Rationale:** Internal structural sharing cannot reduce the required full-value JSON output.
* ***AI Suggestion:*** DECLINE
* ***Justification:*** Do not adopt the advisory append-event/replay schema in this resolution.
  It requires a versioned result contract and consumer reconstruction.
  E01 and E02 address the independently reported alternatives and resource gaps, but do not implement this declined schema change.
* ***Proposed Edit:***
  * Location: None for the proposed replay architecture.
  * Change: Retain the complete 1.1.0 snapshots.

### egm-comprehension-1-2 [egm-comprehension] - Severity: Nit

* **Affected Scope:** Section 3.5, introductory callable-return rule and `UmpireReview` signature; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/comprehension_report.md).
* **Discrepancy Description:** The statement that "each callable returns a plain mapping or an equivalent model" conflicts with `UmpireReview`, which returns `UmpireRejection[]`, including `[]`.
* **Rationale:** The signature and subsequent explanation make the intended list return understandable, but the blanket rule gives contradictory integration guidance.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** A local wording repair prevents an adapter from inventing an undeclared result wrapper.
* ***Proposed Edit:***
  * Location: Section 3.5's blanket return-shape sentence.
  * Change: Apply [E07](#e07).

### egm-structural-1-4 [egm-structural] - Severity: Nit

* **Affected Scope:** Original lines 1, 13, and 21; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/critic_report.md).
* **Discrepancy Description:** The H1 title is followed by an H3 Changelog without an intervening H2.
* **Rationale:** Heading-based navigation presents an incomplete hierarchy.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** Promote the two front-matter headings without renumbering the eight main specification sections.
* ***Proposed Edit:***
  * Location: Changelog and Deferred UI / Execution-Bridge Scope headings.
  * Change: Apply [E10](#e10).

### egm-structural-1-5 [egm-structural] - Severity: Nit

* **Affected Scope:** Section 5, original lines 873-889; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/critic_report.md).
* **Discrepancy Description:** Substeps `a.` through `i.` are plain paragraph text, not Markdown ordered-list markers.
* **Rationale:** The central execution sequence loses its intended visual step structure.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** Change list markers, not execution order or content.
* ***Proposed Edit:***
  * Location: The nine substeps under Turn Execution step 3.
  * Change: Apply [E10](#e10).

### egm-style-1-3 [egm-style] - Severity: Nit

* **Affected Scope:** Section 1, original line 34; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/critic_report.md).
* **Discrepancy Description:** "without relying on conversational consensus, fixed utility equations, or ungrounded claims."
* **Rationale:** The unqualified grounding phrase is broader than the stated gate: supporting pros and shifted votes require canon references, while proposals and failure consequences introduce new facts.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** Remove the overbroad phrase.
  The following Goals already define the narrower grounding guarantee.
* ***Proposed Edit:***
  * Location: The introductory TOME sentence in Section 1.
  * Change: Apply [E08](#e08).

### egm-style-1-4 [egm-style] - Severity: Nit

* **Affected Scope:** Changelog, original line 18; Section 8, original line 1050; metadata, original lines 7-9; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/critic_report.md).
* **Discrepancy Description:** Historical drafting and completed approval are insufficiently time-labelled.
* **Rationale:** The current metadata identifies approved Spec Version 1.1.1.
  The long changelog cell also repeats review chronology already presented in Section 8, making the status transition harder to follow.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** Separate the historical 1.1.0 approval from the new resolution draft.
  The broader review has not approved the revised document.
  Synchronize the README's two version/status references to avoid continuing to advertise the current draft as approved.
* ***Proposed Edit:***
  * Location: Metadata, changelog, Section 8, and the README's status/tree references.
  * Change: Apply [E09](#e09).

### egm-style-1-5 [egm-style] - Severity: Nit

* **Affected Scope:** Section 2.2, original line 119; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/critic_report.md).
* **Discrepancy Description:** "`d66` uses one-based senary (base-six) notation: two digits, each from 1 to 6, identify one of 36 table entries."
* **Rationale:** Numeral-base terminology introduces an unnecessary encoding question where the contract specifies decimal-string or integer lookup keys.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** Describe the existing dice-to-key operation directly.
  Do not change key types or random draws.
* ***Proposed Edit:***
  * Location: The d66 explanatory sentence in Section 2.2.
  * Change: Apply [E11](#e11).

### egm-zoom-out-2-3 [egm-zoom-out] - Severity: Nit

* **Affected Scope:** Section 3.4, original line 648; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/intermediate_zoom_out_report.md).
* **Discrepancy Description:** "Given the same inputs and umpire decisions" promises identical reason text without the seed and adapter-output conditions specified elsewhere.
* **Rationale:** The existing fixed vocabulary already provides deterministic classification of resolved changes.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** This duplicates the valid wording issue in `egm-style-1-1`; preserve both reported severities and apply one replacement.
* ***Proposed Edit:***
  * Location: Section 3.4's reproducibility sentence.
  * Change: Apply [E05](#e05) once.

### egm-zoom-out-2-4 [egm-zoom-out] - Severity: Nit

* **Affected Scope:** Sections 2.4, 3.3, 3.4, and 3.5, original lines 147-152, 343, 624-626, and 740-746; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/intermediate_zoom_out_report.md).
* **Discrepancy Description:** The statement that `umpire_rejections` records "the reversion" includes mechanical reversions in ordinary reading.
* **Rationale:** Correcting the description is simpler than adding raw-provider histories or a new mechanical-rejection logging subsystem.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** The existing record definition is specific enough; repair the broader sentence without adding fields.
* ***Proposed Edit:***
  * Location: Section 3.3's public-argument explanation.
  * Change: Apply [E06](#e06) once.

### egm-zoom-out-2-5 [egm-zoom-out] - Severity: Nit

* **Affected Scope:** Section 3.5, original lines 676, 707-712, and 738-739; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/intermediate_zoom_out_report.md).
* **Discrepancy Description:** "Each callable returns a plain mapping or an equivalent model" conflicts with `UmpireReview` returning a list, including `[]`.
* **Rationale:** A universal result wrapper would add complexity solely to reconcile an inaccurate sentence.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** State the existing list shape and its element shape explicitly.
* ***Proposed Edit:***
  * Location: Section 3.5's blanket return-shape sentence.
  * Change: Apply [E07](#e07) once.

### egm-zoom-out-2-6 [egm-zoom-out] - Severity: Nit

* **Affected Scope:** Sections 2.0 and 3.5, original lines 69-80, 658-718, 733-735, and 748-752; [source report](https://github.com/efsalvarenga/tome/blob/88df7b6d4ee387d5eefa45cef2479044f64b989b/docs/reviews/001_tome_core_architecture_egm/intermediate_zoom_out_report.md).
* **Discrepancy Description:** Snapshot isolation protects mechanical state from mutation.
  It does not sandbox executable code or prevent a provider adapter from transmitting that state externally.
* **Rationale:** This warrants boundary documentation, not authentication, deployment controls, or an in-engine sandbox.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** Document concrete caller responsibilities while preserving the deliberately narrow engine boundary.
* ***Proposed Edit:***
  * Location: End of Section 2.0.
  * Change: Apply [E04](#e04) once.

## Exact Proposed Edits

The following text records the shared edits approved and applied.
Locations use headings and existing sentences so that applying earlier insertions does not invalidate later edits.
All fenced schema, interface, and JSON-example blocks in the specification remain unchanged.

### E01

**Location:** Insert after Non-Goals, before Section 2.
**Change:** Add this subsection.

```markdown
### Alternatives Considered

The following comparisons explain the choices retained for Interface Contract 1.1.0.
Audit representation and publication atomicity are independent decisions: compact audit records could still be published atomically.

| Selected approach | Alternative | Reason for this milestone | Cost or limitation accepted |
| :--- | :--- | :--- | :--- |
| Canon-only narrative conditions | Persistent posture, traits, or capability meters | Numeric trackers would impose behavioral rules that this contract does not define; canon leaves their interpretation to the adapters and umpire. | No automatic capability-availability check; historical relevance requires judgment (Section 2.7). |
| Complete before/after values per changed field | One baseline plus append-only deltas | Each 1.1.0 record can expose the changed field directly without replay or reconstruction. | Canon snapshots grow quadratically across a run; callers must budget accordingly (Section 2.8). Compact records remain a possible versioned alternative. |
| Run-wide atomic publication | Turn-by-turn result publication | A successful call returns exactly the requested turns, and an ordinary engine error cannot be mistaken for a completed partial run. | Completed callback work is not rolled back; long runs retain all records until completion and return no partial progress (Section 2.8). |
| A fresh, fixed order per request | Persisted order and next-actor cursor | The run is a self-contained bounded experiment; the closed world-state schema does not store scheduler progress. | Splitting a run into several requests is not equivalent to one longer request. Repeating one-turn requests with the same supplied order repeats its first actor; callers wanting a complete pass request enough turns. |

These choices do not require a UI, execution bridge, provider-specific integration, or persistence layer inside the engine.
Changing a mandatory result shape, adding scheduler state, or restricting requests to complete rounds requires an explicit interface revision rather than a silent implementation change.
```

### E02

**Location:** Insert Section 2.8 after the historical-canon subsection in E03.
**Change:** Add this subsection.

```markdown
### 2.8 Workload, Resource Budgets & Failure Limits

This contract targets bounded, human-umpired exploratory runs, not an assurance of arbitrary batch capacity.
No maximum workload has been benchmarked or guaranteed.
Positive turn counts and unbounded string fields describe schema acceptance, not resource admission.

For T turns starting with C canon facts, the required complete before/after canon snapshots contain 2CT + T^2 fact occurrences in serialized output.
With one initial fact, 10,000 turns, and approximately 200 bytes per fact, those occurrences represent about 20 GB of fact text alone, before JSON overhead and the other result fields.
This is an analytical illustration, not a measured memory or performance result.
Sharing objects internally cannot remove the duplication from the specified full-value JSON representation.

A completed run with A actors also makes T proposal-generator calls and T * (A - 1) peer-reviewer calls.
It can require up to T pre-roll umpire reviews and T failure resolutions; the actual counts follow the callback conditions in Section 3.5.
Provider charges, human decisions, callback snapshots, narrative lengths, and the complete retained result all contribute to the caller's resource budget.

Before calling the engine, the caller chooses and enforces a workload budget for turns, actors, initial canon size, and narrative payloads using its own resources and provider limits.
The caller also owns adapter-side output limits and timeouts, whose ordinary callback failures use the existing corresponding adapter errors.
Capacity planning must allow for all result fields and encoding overhead, not only the canon-text calculation above.
If the budget is insufficient, the caller reduces or declines the workload before invoking the engine.
These are caller policies, not new RunRequest fields, engine quotas, or stable error codes.

Run-wide atomicity covers engine-owned state and result publication, not external callback effects.
A failed run does not undo provider calls, spend, or human decisions already made.
The caller retains its submitted state and decides whether to retry; the engine does not retry or publish partial records.
Memory exhaustion, interpreter failure, or forced process termination can prevent delivery of either a result or a typed RunFailure.
No partial result is substituted, and these environmental limits must not be relabelled as the internal-defect-only MechanicsError.
```

**Additional replacements and insertions:**

1. Replace `String fields have no maximum length.` in Section 3.1 with:

   > String fields have no maximum length in the schema; this is not a resource-capacity guarantee (Section 2.8).

2. Append to Invariant 11:

   > This atomicity guarantee does not roll back external callback effects; resource-delivery limits are defined in Section 2.8.

3. After the Section 5 paragraph ending `the caller retains its original state unchanged.`, add:

   > Section 2.8 defines the environmental limits of error delivery; they do not authorize a partial result or an engine-level retry.

4. Update the stale deferred-growth description through E09; do not silently replace complete snapshots.

### E03

**Human decision:** Append-only history; adapters and umpire judge current relevance.
**Location:** Insert after Section 2.6, before Section 3.
**Change:** Add this subsection.

```markdown
### 2.7 Historical Canon & Current Relevance

`canon_facts` is an append-only narrative history, in list order, not a mechanically maintained set of currently active capabilities or conditions.
Later events can change an earlier condition without deleting its original assertion.
For example, "Actor A has capability X" and the later "Actor A loses capability X" can both remain in canon.
Citation matching can therefore succeed for a historical fact without establishing that its condition still applies.

Proposal generators and peer reviewers interpret the full supplied history when judging an earlier fact's current relevance.
The human umpire judges reasoning and narrative suitability when the configured review or required failure-resolution callback is invoked.
The engine performs the declared text, shape, vote, and novelty checks; it does not infer temporal applicability, invalidate older entries, or apply a "latest statement wins" rule.
The optional pre-roll review remains optional, so a mechanically valid shift is not guaranteed to have received human relevance review.

Novelty checks still compare a new proposal or failure consequence against the entire canon history using Section 3.0.
A new occurrence of a condition must be expressed as a distinct event rather than repeating an earlier canon statement.
```

**Location:** In Section 7, after Grounding Gate Verification and before Umpire Rejection.
**Change:** Add this unit-test requirement.

```markdown
* **Historical Canon Grounding:** With both "Actor A has capability X" and the later "Actor A loses capability X" in canon, assert that the earlier text remains mechanically valid as a citation and neither entry is removed or invalidated automatically.
  A configured umpire review may reject the resulting shift through the existing rejection rules; without that callback, a mechanically valid shift remains.
  Assert that proposal and failure-consequence novelty checks still cover the entire history.
  These assertions verify the mechanical boundary, not the quality of adapter or human interpretation.
```

### E04

**Location:** End of Section 2.0.
**Change:** Add this paragraph.

```markdown
The four callables are trusted executable integrations selected by the caller.
Their world-state snapshots include the supplied canon facts and actor context.
Snapshots isolate engine working state from mutation; they do not sandbox callback code or prevent it from transmitting data to an external provider.
Before selecting or invoking an integration, the caller decides which simulation data it may disclose and applies its own provider-access, transmission, retention, and confidentiality controls.
Excluding credentials from RunRequest is not a promise that executable callbacks cannot access their host environment.
Untrusted-code isolation, when needed, is a caller responsibility outside this engine contract.
```

### E05

**Location:** Section 3.4.
**Replace:**

> Given the same inputs and umpire decisions, the engine produces the same `reason` text.

**With:**

```markdown
The changed field and resolved outcome determine its `ReasonCode` according to the table above.
Reproducing the outcome also requires the seed, adapter-output, umpire-decision, and runtime conditions in Invariant 10.
```

### E06

**Location:** Section 3.3.
**Replace:**

> It is not rewritten if the shift is reverted; `umpire_rejections` records the reversion, and the umpire judges the argument's fit when resolving a failure.

**With:**

```markdown
It is not rewritten if a shift is reverted mechanically or by the umpire.
`umpire_rejections` records only human-umpire rejections; mechanically invalid attempted shifts have no separate rejection record.
The umpire judges the argument's fit when resolving a failure.
```

### E07

**Location:** Section 3.5.
**Replace:**

> Each callable returns a plain mapping or an equivalent model with exactly the declared fields, and the strict value rules of Section 3.0 apply to it.

**With:**

```markdown
`ProposalGenerator`, `PeerReviewer`, and `FailureResolver` return a plain mapping or an equivalent model with exactly the declared fields.
`UmpireReview` returns a list, including `[]`, whose elements are plain mappings or equivalent models with exactly the `UmpireRejection` fields.
The strict value rules of Section 3.0 apply to all returned values.
```

### E08

**Location:** Section 1.
**Replace:**

> **TOME** models multi-actor interactions, friction between actors, and adaptation without relying on conversational consensus, fixed utility equations, or ungrounded claims.

**With:**

> **TOME** models multi-actor interactions, friction between actors, and adaptation without relying on conversational consensus or fixed utility equations.

The following Goals retain the precise grounding rules for supporting arguments and shifted votes.

### E09

**Location:** Specification metadata and changelog.
**Changes:**

1. Set Spec Version to `1.1.2`.
2. Retain Interface Contract Version `1.1.0`.
3. Set Status to `Under Review`.
4. Add this changelog row:

   | Spec Version | Summary |
   | :--- | :--- |
   | 1.1.2 | Review-resolution draft, 2026-11-14: documented alternatives, caller-owned workload budgets and runtime limits, append-only historical canon, and trusted-adapter boundaries; corrected callback return guidance, audit/determinism wording, review-history labels, and Markdown layout. Interface Contract 1.1.0 is unchanged; fresh Goldfish confirmation and human sign-off remain pending. |

5. Replace the 1.1.0 changelog summary with:

   > Approved 2026-11-11 after four Goldfish passes: adopted per-turn d6 tiers, tier-independent spark sampling, canon-only grounding, binary 2d6 resolution against 7, optional pre-roll umpire rejections, mandatory failure consequences, strict value/error rules, seeded draw order, and the caller-owned run contract. Removed persistent posture, traits/exhaustion, boons, outcome bands, `goal_alignment`, and `active_rumors`. Interface Contract 1.1.0; detailed review chronology is recorded in Section 8.

**Location:** Section 8.
**Changes:**

1. Insert `### Historical Approvals` before the existing review-history paragraphs.
2. Retain the recorded 1.0.0/1.1.0 review outcomes and 2026-11-11 sign-off.
3. Replace the sentence beginning `Three non-blocking suggestions remain deferred:` with:

   > At that approval, three non-blocking suggestions were deferred: returning the effective seed in `RunResult`, pinning a content digest for `trio-d66-v1`, and documenting snapshot growth over long runs.

4. Replace the three historical checklist items with:

   ```markdown
   - [x] Zero-context Goldfish review completed for Spec Version 1.1.0
   - [x] Goldfish confirmation of corrected contract gaps for Spec Version 1.1.0
   - [x] Human developer approval of Spec Version 1.1.0 signed off on 2026-11-11
   ```

5. Append:

   ```markdown
   ### Current Resolution Draft: Spec Version 1.1.2

   The [official-workflow review of Spec Version 1.1.1](../reviews/001_tome_core_architecture_egm/consolidated_review_report.md) completed on 2026-11-13 with `Verdict: Revisions Required`.
   The [annotated resolution report](../reviews/001_tome_core_architecture_egm/goldfish_review_report.md) records the dispositions and approved documentation changes for this draft.
   Section 2.8 now documents snapshot growth and caller-owned mitigation; a compact result schema remains a separate versioned alternative.
   Effective-seed output and table-digest pinning remain deferred suggestions.
   Interface Contract 1.1.0 is unchanged.
   This revision has not received fresh Goldfish approval or final human sign-off.
   Mechanical contract validation is a separate structural gate and does not replace those approvals.

   - [x] Human-approved resolution edits applied to the specification
   - [ ] Fresh Goldfish confirmation of Spec Version 1.1.2
   - [ ] Human developer sign-off on Spec Version 1.1.2
   ```

The applied-edits checkbox is checked only after the approved batch is actually applied.
If the human chooses no changes, none of E09 is applied.

**Location:** README status block.
**Replace its two status lines with:**

```markdown
> **Status:** The [core architecture specification](docs/designs/001_tome_core_architecture.md) (Spec 1.1.2, Interface Contract 1.1.0) is under review after EGM resolution.
> The code in `src/tome/` still implements an earlier design; implementation handoff awaits fresh specification review and human sign-off.
```

**Location:** README project tree, `tome/` source-package comment.
**Replace:** `Simulation engine (being rewritten to Spec 1.1.1)`
**With:** `Simulation engine (legacy implementation; Spec 1.1.2 under review)`

### E10

**Location:** Front-matter headings.
**Changes:**

- Replace `### Changelog` with `## Changelog`.
- Replace `#### Deferred UI / Execution-Bridge Scope` with `### Deferred UI / Execution-Bridge Scope`.

**Location:** Section 5, Turn Execution step 3.
**Change:** Replace the nine lettered substep markers `a.` through `i.` with a valid nested ordered list numbered `1.` through `9.`.
Retain every substep's text, continuation, order, and nesting beneath parent step 3.
Use three spaces before each nested list marker and six before its continuation lines.
Do not renumber the four outer execution steps or the eight main specification sections.

### E11

**Location:** Section 2.2.
**Replace:**

> $d66$ uses one-based senary (base-six) notation: two digits, each from 1 to 6, identify one of 36 table entries.

**With:**

> A d66 lookup rolls two d6 in order and uses the first face as the tens digit and the second as the units digit of a lookup key, giving 36 valid keys.

## Approval and Verification Boundary

Only the exact shared groups attached to approved PROPOSE FIX findings may be applied.
CONTEST, ESCALATE, and DECLINE items are not changed automatically.
An interactive decision on a shared group must be consistent across its duplicate findings; conflicting decisions require clarification before editing.

Before applying the batch, recheck the original specification digest and account for any intervening human edits.
After applying it, verify local links, heading/list structure, parseable JSON examples, and unchanged original fenced contract/example blocks.
Verify that version/status references agree and that the historical reviews and engine source are untouched.
Do not mark this report resolved before a human has chosen a resolution action.
Do not claim fresh Goldfish approval, implementation readiness, a tested workload limit, or engine implementation from these documentation changes.

## Applied Resolution and Handoff

- **Human decision:** Auto accept all PROPOSE FIX items.
- **Applied:** 11 shared documentation edit groups, covering 21 original findings.
- **Contested and unchanged:** 1 original finding.
- **Escalated:** 0.
- **Declined and unimplemented:** 2 advisory schema changes.
- **Remaining unaddressed approved fixes:** 0.
- **Remaining workflow gates:** Fresh Goldfish confirmation and human developer sign-off for Spec 1.1.2.

The resource-call-count sentence explicitly describes a completed run; an error still aborts execution under the existing rules.
No new callback behavior, quota, schema, error code, or engine implementation was introduced.
The revised specification has 1144 lines.
Original finding scopes above remain references to the frozen 1.1.1 source, not recalculated assertions about current line numbers.

### Verification

- All 11 original fenced schema, interface, and example blocks are unchanged; all five JSON blocks parse.
- Scheduling Invariants 1 and 12 and seeded-draw Invariant 14 are unchanged.
- The execution substeps retain their exact text and order; only their Markdown list markers changed.
- Heading hierarchy, local links, nested list structure, and specification/README version references passed checks.
- The snapshot-growth formula and its approximately 20 GB example were checked analytically.
- `git diff --check` passed.
- The installed targeted EGM validator passed with `--spec 001`.
  That check still recognizes the historical approved review; it does not approve the current resolution draft.
- Tracked changes are limited to the specification and README.
  Engine code, tests, and historical reviews are untouched.

No engine test suite or performance benchmark was run for these documentation-only changes.
Do not begin implementation handoff on the strength of the structural validator alone.
