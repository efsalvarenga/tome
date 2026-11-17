# Goldfish Annotated Review Report: Loop Round 1

**Status:** resolved
**Date:** 2026-11-14
**Target:** [TOME core architecture](../../../../designs/001_tome_core_architecture.md), full file, lines 1-1144
**Specification:** 1.1.2, Under Review
**Interface contract:** 1.1.0
**Reviewed SHA-256:** `580f4919c88ce2146f2f6b28e4fd25d1aa782d9cff3beeec1bfbe52b96ecf8cb`
**Post-resolution SHA-256:** `5098c3f703c8802b1b14b5914121a228e85cc450e05547123b6ff247cb70a7ee`
**Raw findings:** [Complete round-one reviewer reports](reviewer_report.md)
**Prior decision history:** [Resolved 1.1.1-to-1.1.2 report](../../goldfish_review_report.md)
**Loop state:** [Review-loop report](../review_loop_report.md)

## Round Decision Before Edits

- All three requested reviewers completed.
- The design and structural reviewers reported no findings.
- The style reviewer reported 1 Major and 2 Nits.
- All three findings are classified PROPOSE FIX, with original severities unchanged.
- No finding matches a previously settled issue.
- No finding is at an applied-fix location where reverting that fix would resolve it; no churn was detected.
- Round 1 is **not clean** because `style-1-1` is an unsettled Major.
- Consecutive clean rounds: **0 of 2**.

Applying the proposed edits cannot retroactively make this round clean.
A fresh later round must assess the resulting text.
The five-round cap has not been reached.

## Prioritized Findings & AI Suggestions

### style-1-1 [style] - Severity: Major

* **Affected Scope:** Section 4, Invariant 6, source line 872.
* **Discrepancy Description:** "Grounded peer votes are the only adjustment to the resolution roll."
* **Rationale:** Section 2.4 requires citation grounding for shifts, not every baseline vote.
  Calling the contributing votes "grounded" could lead a reader implementing this invariant to exclude unchanged votes without citations, changing the modifier and potentially the outcome.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** The wording is broader than the existing grounding gate.
  Section 2.4 explicitly clears the anchor for unchanged votes, and Invariant 8 sums all resulting final votes.
  Align Invariant 6 with those rules without adding a citation requirement or changing adjudication.
  For example, an unchanged baseline vote of -1 with a null anchor still contributes -1.
* ***Proposed Edit:***
  * Location: Invariant 6, its final sentence.
  * Replace: `Grounded peer votes are the only adjustment to the resolution roll.`
  * With: `The clamped sum of final peer votes, after mechanical validation and any umpire rejections, is the only numeric modifier to the resolution roll.`

### style-1-2 [style] - Severity: Nit

* **Affected Scope:** Section 3.5, source line 740.
* **Discrepancy Description:** "The caller owns all four callables, including the LLM-backed proposal generator and peer reviewer."
* **Rationale:** Section 2.0 says these integrations typically wrap an LLM provider; their interfaces do not require one.
  "LLM-backed" instead characterizes that implementation as mandatory, leaving a caller uncertain whether deterministic or rule-based adapters conform.
  "All four" also includes the optional callback.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** The local edit removes an accidental provider constraint and leaves the immediately following required/optional distinction intact.
  The contract remains provider-neutral.
* ***Proposed Edit:***
  * Location: Section 3.5, before the required/optional callable paragraph.
  * Replace: `The caller owns all four callables, including the LLM-backed proposal generator and peer reviewer.`
  * With: `The caller owns the supplied callables.`

### style-1-3 [style] - Severity: Nit

* **Affected Scope:** End of Section 3.5, source lines 845-848.
* **Discrepancy Description:**

  > An empty or whitespace-only world-change statement is malformed proposal output and raises `ProposalGenerationError` before adjudication; it must never enter canon.
  > A statement that matches an existing canon fact raises `InvalidProposalError` before peer review.
  > The engine does not request regeneration.
  > Statements retain their original text.

* **Rationale:** The ordered validation rules at source lines 791-797 already specify these checks and regeneration policy.
  Section 3.0, source lines 288-289, specifies original-text preservation.
  This second statement of the rules, placed after failure-resolution behavior, adds no requirement and creates another location to reconcile when editing the contract.
* ***AI Suggestion:*** PROPOSE FIX
* ***Justification:*** Remove only this duplicate four-sentence paragraph.
  The authoritative shape/novelty/grounding order, no-regeneration rule, and original-text rule remain unchanged.
  The removal does not change validation order or error classification.
* ***Proposed Edit:***
  * Location: The quoted four-sentence paragraph at the end of Section 3.5.
  * Change: Delete the paragraph and its redundant blank separator, retaining one blank line before the section divider.

## Approval Boundary

The human selected "Auto accept all three proposed fixes" on 2026-11-14.
All three local repairs were applied in one batch.
This does not approve the specification, change its interface, or authorize engine implementation.
The specification remains an in-progress 1.1.2 draft; no new contract version is proposed.

The next review round requires explicit human confirmation after resolution.

## Applied Resolution and Verification

- Accepted and applied findings: 3.
- Contested: 0.
- Escalated: 0.
- Declined: 0.
- Unaddressed approved fixes: 0.
- Post-resolution target range: Lines 1-1139.
- Round-one clean status remains **No**; clean streak remains **0**.

Reversing exactly the three approved text edits reproduces the reviewed source SHA-256.
All eleven original schema/interface/example fences are byte-identical.
All five JSON blocks parse.
The authoritative shape/novelty/grounding order, no-regeneration policy, and original-text rules remain.
`git diff --check` passed.

Source line references above identify the frozen round-one input, not the shorter post-resolution draft.
Applied findings remain eligible for independent checking; they are not added to the settled-findings list merely because their repairs were approved.
Fresh Goldfish convergence and final human sign-off remain pending.
