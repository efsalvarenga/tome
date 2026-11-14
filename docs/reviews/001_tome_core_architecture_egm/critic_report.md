# EGM Stage 7: Critic Review

**Target:** [TOME core architecture](../../designs/001_tome_core_architecture.md)
**Date:** 2026-11-13
**Specification:** 1.1.1
**Interface contract:** 1.1.0
**Target range:** Lines 1-1052, full feature specification
**Status:** Completed
**Execution:** Three independent, fresh general-purpose subagents reading the official plugin personas

This is the single-pass critic stage of the user-selected consolidated review.
No remediation or repeated review rounds were authorized.
No convergence is claimed.
The complete reports below preserve reviewer findings and severities before cross-stage consolidation.
The specification has not been edited.

## Reviewer Completion

| Reviewer | Assigned standard | Status | Reported findings |
| :--- | :--- | :--- | :--- |
| `egm-design` | `feature-spec-standard` | Completed | 1 Blocker, 1 Major |
| `egm-structural` | `feature-spec-standard` | Completed | 1 Blocker, 2 Major, 2 Nit |
| `egm-style` | Official style persona only | Completed | 2 Major, 3 Nit |

## Automatically Included Context

- [Default spark tables](../../../src/tome/tables.py)
- [Historical Goldfish review](../001_tome_core_architecture_review.md)

No new Stage 5 or Stage 6 reports were supplied to these reviewers.
Historical approvals were not treated as evidence of current compliance.

## Design Critic: Complete Reviewer Report

**Status:** Completed

Reviewed the complete target, lines 1-1052, including all truncated portions, in read-only Mode: REVIEW against the assigned feature-specification standard.

### egm-design-1-1: Mandatory alternatives evaluation is missing

**Severity:** Blocker
**Affected scope:** Overview, lines 29-65; architecture and execution choices, Sections 2-5, lines 67-905

The overview names avoided approaches, and the changelog records replaced mechanics, but neither evaluates viable alternatives with concrete rejection reasons.
Consequently, the document does not satisfy the standard's mandatory Alternatives Rule.

For example, complete-field snapshots and compact append-delta records can both support an auditable narrative history.
The specification selects complete snapshots without explaining why their duplication cost is preferable to a compact representation.
Likewise, run-wide atomicity is prescribed without evaluating the trade-off against turn-level completion.

**Recommendation:** Document meaningful engine-level alternatives and their concrete atomicity, auditability, complexity, and resource trade-offs.
This requires substantive reasoning, not a particular heading, and does not require restoring deferred UI or infrastructure scope.

### egm-design-1-2: Quadratic result growth lacks a mitigation

**Severity:** Major
**Affected scope:** Section 3.1, line 234; Section 3.4, lines 371 and 635-636; Invariant 11, lines 815-818; Section 8, line 1047

Every turn appends one canon fact, and every turn record contains complete before/after canon arrays.
With C initial facts and T turns, those snapshots contain `2CT + T^2` fact occurrences in serialized output.

For a valid 10,000-turn request with approximately 200-byte facts, the snapshot text alone approaches 20 GB.
A finite turn count therefore does not establish a practical resource bound.
Snapshot isolation and retaining the entire run until completion add further pressure.

Line 1047 acknowledges this as deferred, but supplies no workload assumptions, admission-control expectations, or mitigation.
This is an engine result-size risk regardless of hosting or persistence choices.

**Recommendation:** Explicitly document the growth, supported workload assumptions, caller preflight expectations, and rejection/failure behavior for infeasible requests.
Alternatively, evaluate a versioned compact audit representation.
No particular numeric quota is implied.

### Reviewer Provenance

Files actually read:

- Official plugin `agents/design_critic.md`.
- Official plugin `resources/document_standards/feature-spec-standard.md`.
- [Specification](../../designs/001_tome_core_architecture.md).
- [Tables](../../../src/tome/tables.py).
- [Historical review](../001_tome_core_architecture_review.md).

The official files were read under the supplied Elephant-Goldfish plugin directory.
Repository files were read under the supplied TOME root.

**Limitations:** Static feature-specification audit only.
No tests, compilation, network access, modifications, agents, unrelated files, parent history, or session artifacts were used.
Previous approvals and deferrals were not treated as evidence of compliance.
The size calculation is analytical, not a measured benchmark.

## Structural Reviewer: Complete Reviewer Report

**Status:** Completed

Reviewed the complete target through EOF, including every truncated portion, in read-only Mode: REVIEW.
The assigned standard requires substantive coverage, not a fixed template or exact section names.
Historical approvals were not treated as current structural proof.

**Overall assessment:** The document lacks the mandatory alternatives evaluation and has incomplete risk coverage.

### Structure Map

Under the H1 title at line 1, the actual hierarchy is:

- Metadata: Document identifier and metadata table, lines 3-11.
- H3 Changelog, line 13.
  - H4 Deferred UI / Execution-Bridge Scope, line 21.
- H2 1. Overview & Objectives, line 29.
  - H3 Goals, line 39.
  - H3 Non-Goals, line 57.
- H2 2. Domain Framing & Engine Execution Contract, line 67.
  - H3 2.0 Execution Boundary, line 69.
  - H3 2.1 Per-Turn Posture Die & TriO Tier, line 83.
  - H3 2.2 Dual Spark Table Seeding, line 98.
  - H3 2.3 Engle Matrix Game Formulation, line 121.
  - H3 2.4 Peer Review & Vote Adjustment, line 129.
  - H3 2.5 Matrix Adjudication & State Mutation, line 161.
  - H3 2.6 Failure Consequences, line 179.
- H2 3. State Schema & Data Models, line 203.
  - H3 3.0 Value Rules & Text Normalization, line 205.
  - H3 3.1 World State, line 230.
  - H3 3.2 Proposal Contract (Stage 3), line 286.
  - H3 3.3 Peer Evaluation Contract (Stage 4), line 328.
  - H3 3.4 Run Request, Result, and Turn Record, line 358.
  - H3 3.5 Runner Entry Point, Adapters & Umpire Callbacks, line 658.
- H2 4. Invariants & Rules, line 782.
- H2 5. Execution & State Mutation Logic, line 855.
  - H3 Inputs & Triggers, line 857.
  - H3 Turn Execution, line 863.
  - H3 Outputs & Events, line 898.
- H2 6. Edge Cases & Failure Modes, line 906.
- H2 7. Verification & Automated Test Strategy, line 963.
  - H3 Unit Tests, line 965.
  - H3 Integration Tests, line 1029.
- H2 8. Goldfish Review Gates, line 1040.

There are five Markdown tables and eleven fenced blocks: five JSON examples/schemas and six text contracts.
Their table delimiters and code fences are intact.
Both explicit Markdown links resolve to the supplied local files.
The standard imposes no additional URL or link-text convention.

### Coverage Against the Standard

- Problem and motivation: Present in Section 1; a separately named "Problem Statement" header is unnecessary.
- Goals and non-goals: Explicitly present.
- Architecture, data flow, and integration: Extensively covered in Sections 2-5.
- Alternatives: Changes and exclusions are recorded, but viable alternatives are not evaluated with rejection trade-offs.
- Failure modes and mitigations: Substantial coverage in Sections 3.5, 4, and 6.
- Security and scalability: Boundary decisions exist, but relevant risk and mitigation coverage remains incomplete.

### egm-structural-1-1: Mandatory alternatives evaluation is absent

**Severity:** Blocker
**Affected scope:** Full document, particularly the changelog at lines 17-24 and Section 1 at lines 29-64

**Requirement:** The standard's Alternatives Rule, lines 15-21, explicitly fails specifications that present one path without documented consideration and rejection of viable designs for concrete technical or scope reasons.

**Discrepancy:** The document records removed mechanics and deferred infrastructure, but does not explain their trade-offs against the selected design.
Saying an option was removed, excluded, or deferred is not an evaluation.

**Consequence:** A fresh engineer can implement the chosen contract but cannot assess why consequential design choices are preferable.

**Recommendation:** Add a substantive comparison of viable alternatives for consequential choices, for example narrative-only versus mechanical trackers, or atomic full-snapshot records versus incremental/delta results, with concrete rejection reasons.
No particular heading name is required.

### egm-structural-1-2: Scalability limits lack mitigation

**Severity:** Major
**Affected scope:** Section 3.1, line 234; Section 3.4, lines 367-399 and 633-636; Section 8, line 1047

**Requirement:** Risks & Limits, standard lines 25-27, requires identification of scalability limits and their mitigation.

**Discrepancy:** Strings have no maximum length; actor, canon, and turn counts have no documented operating envelope; every turn records complete before/after field values.
Line 1047 acknowledges snapshot growth only as a deferred suggestion, without explaining its scale or mitigation.

**Consequence:** Serialized canon history grows quadratically with turns even for bounded-length new facts.
Peer-review work also grows with actor count.
Callers receive no guidance for avoiding excessive output, memory demand, or provider work.

**Recommendation:** Document expected growth and practical limits, then identify scope-compatible mitigation and ownership, such as caller-enforced request budgets.
Merely deferring acknowledgment does not satisfy the requirement.

### egm-structural-1-3: Provider and executable-adapter security risks are not addressed

**Severity:** Major
**Affected scope:** Section 2.0, lines 69-80; Section 3.5, lines 658-715

**Requirement:** Risks & Limits, standard lines 25-27, requires security implications and mitigation.

**Discrepancy:** Excluding credentials and assigning authorization to the caller are useful boundaries.
However, the architecture passes complete world state to caller-owned, potentially LLM-backed executable callables without identifying disclosure risks, adapter trust assumptions, or corresponding caller-owned controls.
Isolated snapshots address mutation, not executable-code sandboxing or external disclosure.

**Consequence:** Readers may mistake mechanical/data isolation for a broader security boundary and overlook what external adapters can access or transmit.

**Recommendation:** Document the trusted-executable-adapter assumption, provider-egress implications, and mitigation responsibilities.
This does not require bringing authentication or deployment into engine scope.

### egm-structural-1-4: Front-matter heading hierarchy skips a level

**Severity:** Nit
**Affected scope:** Lines 1, 13, and 21

**Requirement:** Structural reviewer Mode: REVIEW, item 3, requires logical, sequential heading nesting.

**Discrepancy:** The H1 title is followed by an H3 Changelog without an intervening H2.

**Consequence:** Heading-based navigation presents an incomplete hierarchy.

**Recommendation:** Promote Changelog to H2 and its deferred-scope child to H3, or otherwise establish a sequential hierarchy.
This is not an exact-header requirement from the feature standard.

### egm-structural-1-5: Turn substeps are not encoded as a Markdown list

**Severity:** Nit
**Affected scope:** Section 5, Turn Execution, lines 873-889

**Requirement:** The structural reviewer's formatting audit includes list structure.

**Discrepancy:** Substeps `a.` through `i.` are plain paragraph text, not Markdown ordered-list markers.
Without separating breaks, ordinary Markdown rendering collapses them into a continuous paragraph beneath step 3.

**Consequence:** The central execution sequence loses its intended visual step structure.

**Recommendation:** Use a valid nested ordered list or bullets, retaining letter labels as text if desired.

### Reviewer Provenance

Files actually read:

- Official plugin `agents/structural.md`.
- Official plugin `resources/document_standards/feature-spec-standard.md`.
- [Specification](../../designs/001_tome_core_architecture.md).
- [Tables](../../../src/tome/tables.py).
- [Historical review](../001_tome_core_architecture_review.md).

No tests, compilation, network access, file modifications, or additional agent delegation were performed.

## Style Reviewer: Complete Reviewer Report

**Status:** Completed
**Mode:** REVIEW
**Separate document standard:** None

The full target was reviewed, with truncated passages completed.
There were no Blocker findings.

### egm-style-1-1: Reason-code reproducibility promise omits its conditions

**Severity:** Major
**Affected scope:** Section 3.4, line 648; supporting references at lines 458, 641-642, and 814

**Phrasing:** "Given the same inputs and umpire decisions, the engine produces the same `reason` text."

**Rationale:** This reproducibility promise omits the seed and adapter-output conditions stated elsewhere.
Identical requests without a seed can resolve differently, selecting `proposal-succeeded` versus `failure-consequence`.
The specified fixed vocabulary does not guarantee identical outcomes.

**Editorial action - CALIBRATE:** State that the resolved outcome and changed field determine the `ReasonCode`, rather than promising identical text for otherwise identical requests.

### egm-style-1-2: Public-argument description overstates reversion audit coverage

**Severity:** Major
**Affected scope:** Section 3.3, line 343; supporting references in Section 2.4, lines 140-150, and Section 3.5, line 744

**Sentence:** "It is not rewritten if the shift is reverted; `umpire_rejections` records the reversion, and the umpire judges the argument's fit when resolving a failure."

**Rationale:** "The reversion" includes mechanical reversions in the preceding terminology, but `umpire_rejections` records only human-umpire rejections.
Invalid shifts can revert without producing such an entry.
This overstates the audit record's specified coverage.

**Editorial action - CALIBRATE:** Distinguish mechanical from umpire-driven reversions; retain the statement that the argument remains unchanged after either.

### egm-style-1-3: Overview grounding claim is broader than the enforced gate

**Severity:** Nit
**Affected scope:** Section 1, line 34; supporting references at lines 47-49

**Phrasing:** "without relying on conversational consensus, fixed utility equations, or ungrounded claims."

**Rationale:** The unqualified grounding phrase is broader than the stated gate: supporting pros and shifted votes require canon references, while proposals and failure consequences introduce new facts.
Citation matching explicitly does not establish logical validity.

**Editorial action - CALIBRATE:** Name the canon-reference requirements for supporting arguments and shifted votes.
Preserve the adjacent, grounded distinction between mechanical citation checks and umpire judgment.

### egm-style-1-4: Approval history mixes completed and pending status

**Severity:** Nit
**Affected scope:** Changelog, line 18; Section 8, line 1050; metadata, lines 7-9

**Phrasing:** "Approved 2026-11-11 after Goldfish review" ... "as a draft pending approval"; "the current Spec Version 1.1.0 draft."

**Rationale:** Historical drafting and completed approval are insufficiently time-labelled.
The current metadata identifies approved Spec Version 1.1.1.
The long changelog cell also repeats review chronology already presented in Section 8, making the status transition harder to follow.

**Editorial action - CALIBRATE:** Label the pending-approval wording as historical, remove "current" and "draft" from the completed-review checkbox, and shorten the changelog's review chronology by referring to Section 8.

### egm-style-1-5: Numeral-base terminology obscures d66 lookup encoding

**Severity:** Nit
**Affected scope:** Section 2.2, line 119; supporting reference in Section 3.4, lines 392-394

**Sentence:** "`d66` uses one-based senary (base-six) notation: two digits, each from 1 to 6, identify one of 36 table entries."

**Rationale:** Numeral-base terminology introduces an unnecessary encoding question where the contract specifies decimal-string or integer lookup keys.

**Editorial action - CALIBRATE:** Describe the operation directly: two d6 faces, in order, form a two-digit lookup key with 36 valid combinations.

### Reviewer Provenance

Files actually read:

- Official plugin `agents/style.md`.
- [Specification](../../designs/001_tome_core_architecture.md).
- [Tables](../../../src/tome/tables.py).
- [Historical review](../001_tome_core_architecture_review.md).

**Limitations:** Strictly read-only.
No tests, compilation, network access, modifications, or agent delegation occurred.
Findings concern the specification's wording and internal contracts.
Table mappings were inspected, but engine implementation behavior was not verified.
Section 7 was treated as specified verification requirements.
Historical review results and approval markers were not treated as implementation evidence.
