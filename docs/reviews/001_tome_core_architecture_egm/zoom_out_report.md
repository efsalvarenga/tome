# EGM Stage 5: Initial Zoom Out Review

**Target:** [TOME core architecture](../../designs/001_tome_core_architecture.md)
**Date:** 2026-11-13
**Specification:** 1.1.1
**Interface contract:** 1.1.0
**Reviewed revision:** `6882fab977ee25a61b8cd52664399315feaeb499`
**Specification SHA-256:** `f15a4b6c7eb2976a1fe8e73355897e0bad44c92b081452cbaca9ced6081825a9`
**Target range:** Lines 1-1052, full file
**Execution:** Fresh general-purpose subagents reading the official plugin personas
**Status:** Completed

The user selected a consolidated review and approved running stages 5-8.
There is no separate implementation-plan section, so Stage 9 is not applicable.
This report preserves the complete findings from both Stage 5 reviewers.
Recommendations have not been applied.
Reviewer severities are recorded as returned, before cross-stage consolidation.

## Reviewer Completion

| Reviewer | Status | Reported findings |
| :--- | :--- | :--- |
| `egm-zoom-out` | Completed | 2 Major, 1 Nit |
| `egm-inventive-catalyst` | Completed | 1 Nit, advisory |

## Automatically Included Context

- [Default spark tables](../../../src/tome/tables.py)
- [Historical Goldfish review](../001_tome_core_architecture_review.md)

These files are existing local links in the specification.
The user requested no additional context.
The zoom-out persona also requires root-document alignment and code searches for reuse.

## Skeptical Architect: Complete Reviewer Report

**Status:** Completed
**Reviewer verdict:** Revisions Required
**Reported severity:** 2 Major findings and 1 Nit; no Blockers

The objective and motivation are clear.
The provider-neutral boundary, narrative-only mechanics, and deferred UI/persistence scope align with the README.
No speculative infrastructure, caching, or queues are proposed.
Approval markers and historical verdicts were evaluated as claims, not accepted as proof.

### egm-zoom-out-1-1: Request boundaries change simulation scheduling

**Severity:** Major
**Affected scope:** Section 4, Invariants 1 and 12, lines 784-787 and 818-822; Section 5, lines 890-892; Section 6, Edge Case 8, lines 927-929

**Consequence:** With two actors and supplied order `[A, B]`, one two-turn request executes A then B and completes a round.
Two chained one-turn requests execute A twice and never advance `session_index`.
Returning the "complete" world state does not preserve the progress needed to continue its partial round.

**Simplicity rationale:** A caller's batching choice becomes a domain rule controlling actor participation and simulated time.
Callers must reconstruct missing scheduling state, undermining the transport-neutral state-transformer boundary.

**Recommendation:** Choose one minimal contract: require complete-round requests, or preserve the current order and next-actor position when exporting partial rounds.
Supporting partial-round continuation needs only that small amount of state, not a generalized scheduler.

### egm-zoom-out-1-2: The audit contract duplicates the growing canon quadratically

**Severity:** Major
**Affected scope:** Section 3.4, `StateChange`, lines 411-416 and 634-637; Section 2.5, lines 170-175

**Consequence:** Each turn records the complete canon before and after appending one fact.
For n turns starting with C facts, those snapshots alone contain `2nC + n^2` fact occurrences, although the run introduces only n facts.
The final world state also repeats the completed canon.

**Simplicity rationale:** The generic full-field change representation is disproportionate to the specified mutations: one canon append and counter increments.
This is contract-mandated duplication, not a speculative performance concern requiring caching or benchmarks.
Historical deferral does not remove it.

**Recommendation:** Represent canon changes as append-only deltas, or reference the canonical outcome already preserved in each turn record.
Retain compact counter changes and a single baseline/final state rather than complete canon prefixes per turn.

### egm-zoom-out-1-3: Peer adapters must supply metadata the engine ignores

**Severity:** Nit
**Affected scope:** Section 2.4, lines 147-151; Section 3.3, lines 330-337; Section 3.5, lines 692-696 and 730

**Consequence:** A peer evaluation that otherwise meets the rules but omits `biased_shift_applied` fails schema validation and can abort the entire run, despite the engine ignoring the submitted flag and recomputing it.

**Simplicity rationale:** This required provider field creates additional malformed-output states without contributing information to adjudication.

**Recommendation:** Make `biased_shift_applied` engine-owned output metadata, following the existing `ProposalDraft` pattern for engine-generated fields.

### Reuse Assessment

The referenced default tables exist and are already reused appropriately.
Existing Pydantic models, dice utilities, and grounding functions provide adaptation points.
Their legacy step-dice, trait-exhaustion, urgency-ordering, and outcome-band behavior is not compatible enough for unchanged wholesale reuse.
No separate duplicate framework is warranted.

### Reviewer Provenance

Official plugin files read:

- `agents/zoom_out.md`
- `resources/document_standards/zoom-out-standard.md`

Both are under `/Users/Estevao.alvarenga/.vscode/agent-plugins/github.com/google/elephant-goldfish-model/`.

Repository files read or searched:

- [Specification](../../designs/001_tome_core_architecture.md): Entire file through EOF, using bounded reads and completing truncated portions.
- [Historical review](../001_tome_core_architecture_review.md): Lines 1-100 read; historical headings, verdicts, and seed/digest/snapshot observations searched.
- [README](../../../README.md), [repository conventions](../../../AGENTS.md), and [project configuration](../../../pyproject.toml): Read completely for root alignment and ecosystem conventions.
- [Tables](../../../src/tome/tables.py), [dice](../../../src/tome/dice.py), [models](../../../src/tome/models.py), [runner](../../../src/tome/runner.py), and [validator](../../../src/tome/validator.py): Read completely for reuse and dependency-boundary evidence.
- [Package entry point](../../../src/tome/__init__.py): Included in source inventory/content searches only.

The `spec-egm` workflow instructions were loaded; no linked skill references were read.
No tests, compilation, network access, modifications, session artifacts, other new review results, or additional agents were used.

## Inventive Catalyst: Complete Reviewer Report

**Status:** Completed

### egm-inventive-catalyst-1-1: Auditability is coupled to repeated canon snapshots

**Severity:** Nit, advisory
**Affected scope:** Section 3.4, lines 635-636; Section 8, line 1047

**False compromise:** Per-turn auditability is coupled to retaining complete before-and-after canon arrays.
The design acknowledges their growth but defers addressing this avoidable duplication.

**Concrete consequence:** For n turns starting with c canon facts, these snapshot fields alone serialize `n^2 + 2nc` fact occurrences.
Internal structural sharing cannot reduce the required full-value JSON output.

**Proposed resolution:** Apply Segmentation through an in-memory append-event record: retain one initial snapshot and each turn's appended fact, reconstructing complete snapshots when needed.
Introduce this through a versioned result contract, not a silent change to 1.1.0.
Input immutability, atomic publication, and exactly one new fact per resolved turn remain unchanged.

**Secondary trade-offs:** Consumers need schema migration and replay logic.
Inspecting an arbitrary turn requires reconstruction; standalone records depend on access to the initial snapshot.
Materializing the legacy output still incurs quadratic serialization.

### Reviewer Provenance

Files actually read:

- Official plugin `agents/inventive_catalyst.md`.
- [Specification](../../designs/001_tome_core_architecture.md): Entire file, bounded ranges; truncated portions reread.
- [Tables](../../../src/tome/tables.py): Entire file.
- [Historical review](../001_tome_core_architecture_review.md): Historical context, lines 1-120 only.
