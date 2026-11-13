# Goldfish Review: TOME Core Architecture

## Spec Version 1.1.0 Approval Check (2026-11-11)

**Review Target:** [`docs/designs/001_tome_core_architecture.md`](../designs/001_tome_core_architecture.md) (Spec Version 1.1.0, Interface Contract 1.1.0)
**Reviewer:** Goldfish Reviewer Agent (Zero Context)
**Date:** 2026-11-11
**Verdict:** Approved

---

### 1. Executive Summary

NEW-09 is fully resolved.
The spec now says in one place when the flag is set and the anchor replaced: during mechanical validation (L147–148).
It also says that both `UmpireReview` and `evaluation_before_reversion` see the evaluation in exactly that form (L150).
Sections 3.0 (L223), 3.4 (L625) and 3.5 (L733, L739) all say the same thing.
The §7 test pins it with fixed values (L988).
The scenario in the review's NEW-09 probe now has only one correct result: `{biased_shift_applied: true, cited_anchor: "The conduit is open."}`.

NEW-10 is resolved: §8 now records all three 1.1.0 passes and what each one found.

I found no new contradiction that could make two careful implementations differ.
One wording nitpick remains, and it does not block approval.

---

### 2. Invariant & Edge-Case Probing

| ID | Area / Component | Potential Failure Mode / Ambiguity | Risk Severity |
| :--- | :--- | :--- | :--- |
| PROBE-01 (NEW-09) | Evaluation passed to the umpire and kept as `evaluation_before_reversion` | **Resolved.** L147–148 define the *mechanically validated evaluation*: the engine sets the flag from whether a valid non-zero shift remains and replaces the anchor with the canon text. L150 says `UmpireReview` receives it and `evaluation_before_reversion` stores it "in exactly that form". L151 says reversion happens only after that. | — |
| PROBE-02 (NEW-09) | Do the other sections agree? | **Consistent.** L223, L625, L733 and L739 all describe the same mechanically validated evaluation. L732 and L737 match L148. | — |
| PROBE-03 (NEW-09) | Fixed-value test | **Present.** L988 sets up baseline 1, final 0, adapter flag `false` and a padded anchor. It asserts that the callback input and the stored record both have flag `true` and anchor `"The conduit is open."`, and that the final evaluation is `1`/false/null. | — |
| PROBE-04 | "Original evaluation" wording | L157 and Edge Case 10 (L933) still said "the original evaluation". L150, L625, L739 and the L988 test already settle the meaning, so this is not a contract ambiguity. | Low |
| PROBE-05 (NEW-10) | §8 gate text | **Resolved.** §8 records the three passes, names NEW-01, NEW-02 and NEW-09, and correctly leaves this confirmation pending. | — |

---

### 3. Detailed Critiques & Blind Spots

#### 3.1 Data Schema Completeness

* **[praise] L147–152:** The new paragraph is the minimal, correct fix.
  It names the intermediate state, says exactly what it contains, says who receives it, and then states the reversion.
  The closing invariant ("A retained `cited_anchor` therefore always appears verbatim in `canon_facts`") still holds.
* **[praise] L223 against L148:** The single exception to "store the original text" now names the stage that applies it, so the two sections cannot drift apart.
* The §3.3 example (baseline 1, final 0, flag `true`, canon-text anchor) is a valid mechanically validated evaluation.
  The worked turn record (unchanged vote, flag false, anchor null) is consistent with L149.

#### 3.2 State Mutation & Deterministic Consistency

* **[praise] L732–739:** The order of operations is clear: mechanical validation; the callback, only if a shift remains; a copy of the evaluation; then the reversion.
  Because only a vote that still differs from baseline can be rejected, every `evaluation_before_reversion` has `biased_shift_applied: true` and a non-null canon-text anchor.
* Canon facts are unique under normalisation (§3.1; Edge Case 5), so "the canon fact it matched" always means exactly one fact.
* **[nitpick] (non-blocking) L157 and L933:** Consider changing "original evaluation" to "mechanically validated evaluation" so all places use the same term.

#### 3.3 Testability & Verification Strategy

* **[praise] L988:** This one assertion covers the whole NEW-09 edge, using an inconsistent adapter flag and a padded, quoted anchor.
* L987 and the Voting Metadata test agree with L988.

---

### 4. Required Revisions

None.

Optional:

1. Change "original evaluation" to "mechanically validated evaluation" at L157 and L933.
2. When recording this approval, update §8 (four passes) and tick the Goldfish confirmation box.

---

### 5. Recommendation & Sign-Off

* **Verdict:** Approved
* **Notes for Elephant Agent:**
  - **NEW-09 and NEW-10:** Closed, with no new contradictions.
  - **Still deferred (non-blocking):** returning the effective seed in `RunResult`, a `trio-d66-v1` content digest, and `before`/`after` snapshot growth.
  - **Next step:** record this Goldfish approval in §8 and the review report, then pass the spec to the human developer for sign-off.

**Elephant follow-up:** Both optional items above were applied after this check.

---

## Spec Version 1.1.0 Sign-Off Check (2026-11-11)

**Review Target:** [`docs/designs/001_tome_core_architecture.md`](../designs/001_tome_core_architecture.md) (Spec Version 1.1.0, Interface Contract 1.1.0)
**Reviewer:** Goldfish Reviewer Agent (Zero Context)
**Date:** 2026-11-11
**Verdict:** Revisions Required

---

### 1. Executive Summary

NEW-01 is fully resolved.
NEW-02 is resolved for the final `peer_evaluations`.
It is not settled for the pre-reversion evaluation, which the umpire callback receives and `umpire_rejections` stores.
The 1.1.0 confirmation pass named that location as affected (review L76).
All six non-blocking items, NEW-03 to NEW-08, have been dealt with.
All five JSON blocks still parse and satisfy every rule I checked.
The only non-null `cited_anchor` (§3.3 example) appears verbatim in the canon of §3.4.
The worked turn record still adds up: net −1, a roll of 7 adjusted to 6, which is a Failure, and the record has exactly 12 fields.
One narrow ambiguity remains (NEW-09 below), and a one-sentence edit fixes it.

---

### 2. Invariant & Edge-Case Probing

#### 2.1 Required Revisions from the Confirmation Pass

| Item | Status | Evidence |
| :--- | :--- | :--- |
| NEW-01: actor-ID references | **Resolved** | §3.0 L214–216 says actor IDs are identifiers, normalisation applies only to the uniqueness check, and every reference must match exactly. This is restated for `first_round_order` (§3.4 L358), the peer `voter_actor_id` (L650, §3.5 L726), and umpire and failure-resolver IDs (L216, with L741 and L762 relying on it). Invariant 13 (L819) and Invariant 1 (L780) agree. The §7 tests at L989–990 fix the padded `first_round_order` case, the quoted `voter_actor_id` case, and `"a"`/`" a "` being rejected as a match. |
| NEW-02: stored `cited_anchor` | **Partly resolved** | L149 and L219–220 now agree that a retained anchor is replaced by the matched canon fact's original text. The L988 test pins `'  "The conduit is open."  '` → `"The conduit is open."`. It is still open what the *pre-reversion* evaluation contains. See NEW-09. |

#### 2.2 Non-Blocking Items NEW-03 to NEW-08

| Item | Status | Evidence |
| :--- | :--- | :--- |
| NEW-03: out-of-range integers | Addressed | L223 (malformed, "never clamped"), L719, L726 and Edge Case 17 (L953) |
| NEW-04: `ReasonCode` joining rule | Addressed | L411 ("exactly one code per changed field") and L642; the `"; "` joining rule is gone from the spec |
| NEW-05: "engine-side" wording | Addressed | The phrase no longer appears; Edge Case 6 (L918) now says "caller-supplied" |
| NEW-06: Invariant 13 "non-empty" | Addressed | L819 now says "non-whitespace … (Section 3.0)" |
| NEW-07: "stable message" | Addressed | L715: "only `code` is part of the stable contract" |
| NEW-08: Python d66 key type | Addressed | L390: decimal-string or `int` keys, but not both in one table |
| Carried over: effective seed, table digest, `before`/`after` growth | Still open (non-blocking) | `RunResult` has no seed (L366–371); `trio-d66-v1` is still defined only by reference (L99–101); snapshot growth is not mentioned |

#### 2.3 New Probes

| ID | Area / Component | Potential Failure Mode / Ambiguity | Risk Severity |
| :--- | :--- | :--- | :--- |
| NEW-09 | Contents of the pre-reversion evaluation | Take a peer that returns baseline 1, final 0, `biased_shift_applied: false` and anchor `'  "The conduit is open."  '`, and an umpire who then rejects the shift. Implementation A normalises during mechanical validation, reading L730 and L622 ("mechanically validated evaluation"). Its `evaluation_before_reversion` and the `UmpireReview` input carry `{flag: true, cited_anchor: "The conduit is open."}`. Implementation B substitutes only for "remaining"/"retained" votes and sets the flag "after … any umpire review", reading L147, L149, L219–220, and L984 ("original anchors"). It carries `{flag: false, cited_anchor: '  "The conduit is open."  '}`. Both readings are defensible, and they produce different `TurnRecord.umpire_rejections` output. | Med |
| NEW-10 | §8 gate text is out of date | L1037–1040 still describes only the first 1.1.0 review. It does not record that the confirmation pass returned NEW-01 and NEW-02. | Low |

---

### 3. Detailed Critiques & Blind Spots

#### 3.1 Data Schema Completeness

* **[praise]** The actor-ID fix (L214–216) is the minimal, correct split.
  IDs are normalised for uniqueness and compared exactly when referenced.
  Because duplicates are rejected under normalisation, each exact reference identifies exactly one actor.
* **[praise]** The storage rule (L219) and its single exception (L220) are stated in one place.
  Proposal and failure statements (L758, L774), `source_ref` and IDs all keep their original text, and none of them contradicts the exception.
  `source_ref` keeping the adapter's text while `cited_anchor` is replaced is a deliberate asymmetry, not a contradiction (L299).
* **[issue] (blocking) NEW-09, L147, L149 and L220 against L622, L730 and L984:** Say what state the evaluation is in when it is passed to `UmpireReview` and copied into `evaluation_before_reversion`.
  It may already have the engine-set flag and the canon-text anchor, or it may still hold the adapter's raw flag and anchor.

#### 3.2 State Mutation & Deterministic Consistency

* **[praise]** The worked example still follows every rule.
  - **Draws:** I re-checked seed 20 with the supplied order. It gives posture 6, tables `Focus` then `Method`, d66 rolls 66 and 13, and dice 5 and 2.
  - **Pros:** The pro's `source_ref` is exactly the canon fact.
  - **Peer evaluation:** The only one is unchanged, with the flag false and the anchor null (L580–586), which matches L148.
  - **Record:** The net modifier and adjusted total are consistent, and the state changes use valid `ReasonCode` values.
* No other new contradictions were found.
  Edge Case 5 (L916), §5 step 1, Invariant 13 and §3.0 agree on blank or matching IDs and canon facts.
  The "exactly equal" wording at L726 matches L216.

#### 3.3 Testability & Verification Strategy

* **[praise]** L988–990 turn both NEW-01 and NEW-02 into fixed-value assertions.
* **[issue] (blocking, part of NEW-09):** L984 ("original anchors") cannot be written as a fixed expectation until NEW-09 is decided.
  It needs one assertion on `evaluation_before_reversion.cited_anchor` and `biased_shift_applied`, using a padded anchor and an inconsistent adapter flag.
* **[nitpick] (non-blocking) NEW-10, L1037–1040:** Record the confirmation pass and its outcome.

---

### 4. Required Revisions

1. **NEW-09: state of the pre-reversion evaluation.** Add one sentence to §2.4 (near L147–149) or §3.0 (L220).
   It should say whether the evaluation passed to `UmpireReview` and copied into `evaluation_before_reversion` already has the engine-set `biased_shift_applied` and the canon-text `cited_anchor`, or still holds the adapter's values.
   Then align L622, L730 and L984, and add one fixed-value test next to L988.
   Either answer is acceptable.
   Substituting during mechanical validation probably fits "mechanically validated" best, and it lets the umpire see canon text.

---

### 5. Recommendation & Sign-Off

* **Verdict:** Revisions Required
* **Notes for Elephant Agent:**
  - **Resolved:** NEW-01 is fully closed, NEW-02 is closed for the final `peer_evaluations`, and NEW-03 to NEW-08 are all addressed.
    I found no new contradictions, and the JSON examples still pass every rule.
  - **Blocking:** Only NEW-09 remains.
    It is the last edge of NEW-02, about *when* the anchor is replaced and the flag is set, and it fails the "two careful implementations" test only for umpire-rejected votes.
  - **Optional:** NEW-10 (refresh the §8 gate text).
    The three carried-over suggestions can still be deferred.
  - **Next step:** Once the NEW-09 sentence and its test are added, I expect to approve without another full review.

**Provenance:** This review ran with the orchestrator model and no local workers.
I read the four named files, plus the code-reviewer agent definition the harness requires.
I also ran two local checks: parsing the spec's JSON blocks, and a `random.Random(20)` draw to confirm the worked example.
No files were edited.

---

## Spec Version 1.1.0 Confirmation Pass (2026-11-11)

**Review Target:** [`docs/designs/001_tome_core_architecture.md`](../designs/001_tome_core_architecture.md) (Spec Version 1.1.0, Interface Contract 1.1.0)
**Reviewer:** Goldfish Reviewer Agent (Zero Context)
**Date:** 2026-11-11
**Verdict:** Revisions Required

---

### 1. Executive Summary

All six earlier Required Revisions are now resolved in substance.
§3.0 adds one normalisation rule and strict value rules (L201–219).
Canon facts must be non-blank and unique (L239, L270–271).
§3.5 now fixes the order of proposal checks (L711–715), and Edge Case 17 maps each defect to exactly one error (L946–950).
`StateChange.reason` now uses a closed `ReasonCode` vocabulary (L627–638).
The shuffle input is now pinned, and an unsorted golden vector backs it (L815, L824–825).
The `run` entry point and the rule for a missing callable are now defined (L651–666).
The cheap non-blocking items PROBE-09 to PROBE-14 have also been handled.

I re-checked the mechanics on **Python 3.11.18**, the version the golden vectors name:

* **Golden vector 1 (Invariant 14, L822–823):** Seed `42` with `["actor_a","actor_b"]` gives the order `["actor_b","actor_a"]`, posture roll 1, tables `Method` then `Focus`, d66 rolls 22 and 61, and dice (6, 6). Confirmed.
* **Golden vector 2 (L824–826):** Seed `4` with `["actor_c","actor_a","actor_b"]` gives the order `["actor_b","actor_a","actor_c"]`, posture roll 1, tables `Disposition` then `Motivation`, d66 rolls 21 and 11, and dice (4, 5). Confirmed.
  The counterfactual also holds: shuffling the sorted input gives `["actor_c","actor_b","actor_a"]`.
  The draws after the shuffle are the same either way, so this vector only detects a sort through the shuffled order, which is all it needs to do.
* **Worked example (§3.4):** All five JSON blocks parse.
  Every override table has exactly the 36 d66 keys, and none of its values are blank.
  - **Draws:** Seed `20` with the supplied order gives posture roll 6 (Odd), tables `Focus` then `Method`, d66 rolls 66 and 13, and dice 5 + 2 = 7.
    Those rolls map to `Focus:Resource access` and `Method:Public declaration`, as the example shows.
  - **Resolution:** The net modifier is −1, so the adjusted total is 6, which is a Failure.
    The only candidate is `actor_dock_syndicate`, which matches the resolution's source.
  - **Records:** The state changes use the codes `failure-consequence` (L601) and `turn-tick` (L607), in ascending pointer order.
    `session_index` stays 0, and the TurnRecord has exactly the 12 declared fields.
* **Normalisation vectors (L1006):** I worked each one through the rule at L205–211, and all of them follow from it.

Two new gaps remain.
Both come from the revision itself: the new rule at L213 does not say which comparisons it covers, or which text the engine stores.
Each lets two careful implementations return different contract-visible results, which is the same standard the earlier review applied.
Each needs about one sentence to fix.

---

### 2. Invariant & Edge-Case Probing

#### 2.1 Earlier Required Revisions: Status

| Prior Item | Status | Evidence |
| :--- | :--- | :--- |
| RR-1 Normalisation definition (PROBE-01) | **Resolved** | §3.0 L205–216 defines the stripping steps, the quote set, both-sides matching and "non-whitespace". Goal L47, Invariant 4 (L783), Invariant 5 (L787–788), Edge Case 2 (L900–902) and the L1006 test vectors all refer back to it. Two new scope gaps are raised as NEW-01 and NEW-02. |
| RR-2 `canon_facts` constraints (PROBE-02) | **Resolved** | Schema `pattern: "\\S"` (L239). L270–271 rejects blank or matching entries with `InvalidRunRequestError` and closes the blank-anchor loophole. Also covered by §5 step 1 (L858), Edge Case 5 (L910) and the L1008 test. |
| RR-3 One error per adapter defect (PROBE-03/04/05) | **Resolved** | The novelty clause is gone from `ProposalDraft` (L671). The check order is shape, then novelty, then grounding (L711–715). Peer defects raise `PeerReviewError` (L720, L644). Invariant 5 now names `ProposalGenerationError` (L787), Edge Case 17 lists the mapping (L946–950), and the tests cover it (L1007, L1013). |
| RR-4 `StateChange.reason` vocabulary (PROBE-06) | **Resolved** | The `ReasonCode` table (L627–634), the type (L405) and the example (L601, L607) agree. Reason text is deterministic (L638). See NB-03 for a non-blocking point about the joining rule. |
| RR-5 Shuffle input and unsorted vector (PROBE-07) | **Resolved** | L815 and §5 step 2 (L862) state the input order. The second golden vector (L824–826) is verified above. |
| RR-6 Runner entry point and callable binding (PROBE-08) | **Resolved in substance** | The `run` signature is at L651–660, ownership at L662, the definition of "missing" at L664–665, the return representation and strict values at L666, and the matching tests at Edge Case 16 (L943) and L1004. Stale "engine-side" wording remains at L50, L866 and L912 (NB-01). |

#### 2.2 Earlier Non-Blocking Items: Status

| Prior Item | Status | Evidence |
| :--- | :--- | :--- |
| PROBE-09 Pruned proposal audit | Addressed | L718: reviewers, the record and the callbacks all receive the pruned proposal, and pruned pros are not kept. |
| PROBE-10 `session_index` comment | Addressed | L388: "world session_index after this turn". |
| PROBE-11 `contract_version` mismatch | Addressed | Covered by Edge Case 5 (L910), §5 step 1 (L858) and the L1008 test. |
| PROBE-12 Example rationale | Addressed | The L591 rationale now says "restates its blocking argument as a concrete event". |
| PROBE-13 Goal wording, and whitespace-only `id` | Addressed | L46–47 now limits grounding to pros and anchors. `id` uses `pattern: "\\S"` (L248), and L269 adds the full rule. |
| PROBE-14 Rules that cannot be enforced | Addressed | L124 says the rule is "narrative guidance … the engine does not enforce it". |
| Return the effective seed (2025 suggestion) | Still open (non-blocking) | `RunResult` (L368–373) has no seed. |
| Digest for the built-in table set | Still open (non-blocking) | §2.2 still defines `trio-d66-v1` only by reference to `src/tome/tables.py`. |
| Quadratic `before`/`after` size | Still open (non-blocking) | Not acknowledged. |

#### 2.3 New Probes

| ID | Area / Component | Potential Failure Mode / Ambiguity | Risk Severity |
| :--- | :--- | :--- | :--- |
| NEW-01 | Normalisation scope: actor-ID references | L213 says "Every comparison … normalizes both sides" and then lists only anchors, `source_ref`, novelty and canon duplicates. Actor-ID uniqueness uses "match" (L267, L645), so it is normalised. The other places that refer to actor IDs do not say which rule they use: `first_round_order` "contain every actor ID exactly once" (L353, Invariant 1 L774), `voter_actor_id` "must equal" (L644, L720), `UmpireRejection.voter_actor_id` (L728) and `source_voter_actor_id` (L745). For example, `first_round_order: ["actor_iron_choir ", …]` or `voter_actor_id: "\"actor_dock_syndicate\""` could raise `InvalidRunRequestError` or `PeerReviewError` in one implementation and be accepted in another. Nothing says which ID text the record would then use. | Med |
| NEW-02 | Stored `cited_anchor` text | L149 says "Remaining shifted votes retain the **normalized** anchor". L216 says "The engine stores and returns the **original** text, not its normalized form". The test at L981 ("normalized shift flags/anchors") does not settle it. `cited_anchor` appears in `TurnRecord.peer_evaluations` and in `UmpireRejectionRecord.evaluation_before_reversion`, so this contradiction is visible in the contract output. Take an adapter anchor `'  "The conduit is open."  '`. It could be stored as the adapter's original text, as its normalised form, or as the text of the matching canon fact. | Med |
| NEW-03 | Out-of-range adapter integers | A peer result such as `final_vote: 2` (with baseline 1, a one-step delta) breaks the declared type `integer in [-1, 1]` (L333). Edge Case 17 (L947) and L713/L720 list "wrong type" but not "out of range", while Invariant 3 (L780–782) speaks only of reverting two-step shifts. One reading gives `PeerReviewError`; another clamps or reverts. | Low |
| NEW-04 | `ReasonCode` joining rule cannot be tested | In 1.1.0 each field gets exactly one code per turn (L631–634). The `"; "` joining rule (L405, L636) therefore never applies, so the matching part of the L1011 test cannot be exercised. | Low |
| NEW-05 | Leftover "engine-side" wording | L50 ("may be supplied by engine-side adapters"), L866 ("engine-side proposal-generation integration") and L912 still use the wording that RR-6 asked to reconcile with L72 and L662 ("caller owns all four callables"). | Low |
| NEW-06 | Invariant 13 wording | L813 says IDs must be "unique and non-empty". Elsewhere the rule is non-whitespace after normalisation (L215, L267). | Low |
| NEW-07 | "Stable … message" | L709 calls the `RunFailure` message stable, but no message text is defined anywhere. | Low |
| NEW-08 | D66 key type for Python callers | L383–384 defines the key format only for JSON. With the strict value rules in §3.0, it is unclear whether a Python mapping with `int` keys (`11`) is accepted or rejected as malformed. | Low |

---

### 3. Detailed Critiques & Blind Spots

#### 3.1 Data Schema Completeness

* **[praise]** §3.0 (L201–219) is a clean single source of truth.
  It covers the `str.strip()` semantics, exactly one ASCII quote pair, preserved case, the original text being stored, and booleans never counting as integers.
  The test vectors at L1006, including the doubled quote pair and typographic quotes, can be written as fixed expectations.
* **[issue] (blocking) NEW-01, L213 against L353, L644, L728 and L745:** Say whether actor-ID references are compared exactly or after normalisation.
  If they are normalised, also say which text appears in `active_actor_id`, `voter_actor_id` and `source_voter_actor_id`.
  The simplest fix keeps exact equality for references and normalisation for uniqueness only, and states that as one sentence in §3.0.
* **[issue] (blocking) NEW-02, L149 against L216:** Pick one stored form for `cited_anchor` and change L149, or L216, and the L981 test to match.
  The options are the adapter's original text, its normalised form, or the text of the matched canon fact.
* **[suggestion] (non-blocking) NEW-03, L713, L720 and L947:** Add "an integer outside its declared range" to the shape errors, so that `final_vote: 2` clearly raises `PeerReviewError` and is never clamped.
* **[suggestion] (non-blocking) NEW-08, L383–384:** Say whether Python-native `SparkTables` callers may use `int` d66 keys or must use decimal strings.
* **[nitpick] (non-blocking) NEW-06, L813:** Change "non-empty" to "non-whitespace (Section 3.0)".

#### 3.2 State Mutation & Deterministic Consistency

* **[praise]** The new check order in §3.5 (L711–715) settles each proposal defect with one error ("the first failing check decides the error").
  It also matches Edge Case 15: the novelty check runs before peer review, so no peer calls or dice are spent.
* **[praise]** The second golden vector and the explicit "never sorts it first" (L815) make the order of the RNG input testable.
  Both vectors reproduce exactly on Python 3.11.18.
* **[praise]** The `run` signature (L651–660) and the definition of "missing" (L664–665) are precise.
  Rejecting the request before any callable is invoked and before any RNG draw is also clearly testable (Edge Case 16, L943–945).
* **[suggestion] (non-blocking) NEW-04, L636 and L1011:** Either say that in 1.1.0 each changed field carries exactly one code, or keep the joining rule only for forward compatibility and remove "joined with `"; "`" from the §7 assertion.
* **[nitpick] (non-blocking) NEW-05, L50, L866 and L912:** Replace "engine-side" with "caller-supplied" so the wording matches L72 and L662.
* **[nitpick] (non-blocking) NEW-07, L709:** Call only the `code` stable, or define the message templates.
* **[suggestion] (non-blocking, carried over):** Consider returning the effective seed in `RunResult`, pinning a content digest for `trio-d66-v1`, and noting that `canon_facts` `before`/`after` snapshots grow over long runs.

#### 3.3 Testability & Verification Strategy

* **[praise]** The §7 tests now have fixed expected values.
  These include the normalisation vectors (L1006), the error classification matrix (L1007), request validation (L1008), required callables (L1004), and round-complete reason codes (L1011).
* **[issue] (blocking, covered by NEW-01 and NEW-02):** The §7 suite cannot set the expected result for whitespace- or quote-padded actor-ID references.
  It also cannot set the expected stored `cited_anchor` text until those two rules are fixed.
  Add one test for each once they are decided.
* Edge Cases 5, 16 and 17 and Invariants 4, 5 and 14 introduce no other contradictions.
  Invariant 5 (L787) and the L713 check order agree.
  Invariant 4 (L783) refers correctly to §3.0.
  Edge Case 5 (L910) matches §3.0 and §5 step 1 (L857–859).

---

### 4. Required Revisions

1. **Normalisation scope for actor-ID references (NEW-01):** In §3.0 (L213), state whether actor-ID references are compared exactly or after normalisation.
   This covers the `first_round_order` entries (L353, Invariant 1), `voter_actor_id` (L644, L720), `UmpireRejection.voter_actor_id` (L728) and `source_voter_actor_id` (L745).
   If they are normalised, say which ID text is recorded.
   Add a §7 test with a padded or quoted ID reference.
2. **Stored form of `cited_anchor` (NEW-02):** Resolve the contradiction between L149 ("normalized anchor") and L216 ("original text").
   State whether a retained shifted vote stores the adapter's original anchor, its normalised form, or the matched canon fact's text.
   Align the L981 test and add a fixed-value assertion.

Everything else in this report is non-blocking.

---

### 5. Recommendation & Sign-Off

* **Verdict:** Revisions Required
* **Notes for Elephant Agent:**
  - **What is resolved:** All six earlier blocking items are resolved, and PROBE-09 to PROBE-14 are addressed.
    The worked example and both golden vectors were re-checked on Python 3.11.18 and found correct.
  - **What blocks:** The two remaining items both concern how far §3.0 reaches.
    One is which comparisons it covers (actor IDs); the other is which text is stored (`cited_anchor`).
    Each is a one-sentence change plus one test, and neither affects the mechanics, the draw order or the error taxonomy.
  - **Optional in the same edit:** NB items NEW-03 to NEW-08 can go in the same edit or be deferred.
    NEW-05 (the leftover "engine-side" wording) is the cheapest and closes the last textual residue of RR-6.
  - **Next step:** Once these are applied, I expect the spec to be ready for Approved status and human sign-off without another full review.

**Provenance:** This review ran with the orchestrator model and no local workers.
I read only the four files named, plus the code-reviewer agent definition the harness requires.
To verify the vectors, I ran `random.Random` checks with the Python 3.11.18 interpreter and parsed the spec's JSON blocks.
No files were edited.

---

## Spec Version 1.1.0 Review (2026-11-11)

**Review Target:** [`docs/designs/001_tome_core_architecture.md`](../designs/001_tome_core_architecture.md) (Spec Version 1.1.0, Interface Contract 1.1.0)
**Reviewer:** Goldfish Reviewer Agent (Zero Context)
**Date:** 2026-11-11
**Verdict:** Revisions Required

---

### 1. Executive Summary

The specification is mostly ready to build from.
The mechanics fit together, error handling is atomic, the draw order is pinned to exact `random.Random` calls, and the umpire callbacks are kept apart from the random number generator (RNG).
I checked the worked examples against the rules, and they hold up:

* **Golden vector (§4, Invariant 14):** Seed `42` gives the order `["actor_b", "actor_a"]`, a posture roll of 1, tables `Method` then `Focus`, d66 rolls 22 and 61, and dice 6 and 6.
* **Worked example (§3.4):** Seed `20` gives a posture roll of 6 (Odd), tables `Focus` then `Method`, d66 rolls 66 and 13, and resolution dice 5 + 2 = 7.
  The override tables map these to `Focus:Resource access` and `Method:Public declaration`, which matches the example.
* **Example arithmetic:** One unshifted vote of −1 gives a net modifier of −1, so 7 − 1 = 6, which is a Failure.
  The candidate set `{actor_dock_syndicate}` matches the resolution source.
  The `state_changes` entries are in ascending pointer order (`/canon_facts` before `/turn_index`).
  `session_index` correctly stays 0 for an incomplete pass, and `turn_index` goes from 0 to 1.

These checks were run locally on Python 3.9.6, not the 3.11 the golden vector names.
`randint`, `sample` and `shuffle` work the same way on lists in both versions.

However, a few gaps would let two careful implementations of the contract behave differently.
Those gaps are:

* the grounding normalisation rule;
* how canon facts are validated;
* which error class covers adapter output that breaks the stated type constraints;
* the content of the "engine-generated" `reason` text;
* the input order for the seeded shuffle;
* how the required callables are passed to the runner.

Each of these is cheap to fix, but each affects determinism or whether the spec can be tested.

---

### 2. Invariant & Edge-Case Probing

| ID | Area / Component | Potential Failure Mode / Ambiguity | Risk Severity |
| :--- | :--- | :--- | :--- |
| PROBE-01 | Grounding normalisation | Three different definitions: whitespace-only (L47), whitespace plus enclosing quotation marks matched "exactly" against the raw canon string (Invariant 4, L725–726), and "one matching enclosing quote pair" (Edge Case 2, L838). Novelty checks normalise both sides (L124, L693, L708), but the anchor check appears to normalise only the citation. The quote characters, the stripping order and the definition of whitespace are not stated. | High |
| PROBE-02 | `canon_facts` schema | Items are a plain `string` (L218), with no non-blank or uniqueness rule. If a caller sends a blank canon fact, a blank or `""` anchor normalises to empty and passes the Linter Gate. Duplicates that only become equal after normalisation are not covered either. | High |
| PROBE-03 | Error classification | `ProposalDraft.world_change_statement` is typed "not already in canon_facts" (L622), so a duplicate draft is malformed output and becomes `ProposalGenerationError` (L659). L708 and Edge Case 15 say `InvalidProposalError` instead. | Med |
| PROBE-04 | Error classification | `SupportingPro.source_type` is the literal `"canon_fact"` (L259), so other values are malformed (`ProposalGenerationError`). Invariant 5 (L729–730) says such pros are pruned. §7 (L942) says `actor_trait` is "rejected" but names no error. Draft output with 0 or 3 pros is equally ambiguous. | Med |
| PROBE-05 | Peer identity | §3.4 (L609) requires each voter ID to be a distinct non-active actor. No error is named for a `PeerReviewer` result whose `voter_actor_id` differs from the `voter_actor` it was called with. | Med |
| PROBE-06 | `StateChange.reason` | Declared "engine-generated" (L379, L601–603), with no template or vocabulary. The example reason (L575, "The umpire-resolved blocking event explains why the claim fails.") paraphrases the story, which an engine cannot derive from its inputs. The example contradicts the rule, and conformance cannot be tested. | Med |
| PROBE-07 | Seeded order | Invariant 14 and §5 step 2 (L756, L799) shuffle "the actor IDs" without saying their starting order. The golden vector's IDs (`actor_a`, `actor_b`) are already sorted, so it cannot tell `WorldState.actors` order from sorted order. | Med |
| PROBE-08 | Callable ownership | L50 and L75 say the "engine-side integration supplies" the proposal and peer adapters. L76, L680 and L789 say the caller supplies them. There is no runner signature, no definition of "missing" (`None` versus not callable), and no defined return representation for adapters. Yet Edge Case 16 and §7 require a deterministic `InvalidRunRequestError`. | Med |
| PROBE-09 | Pruning audit | The record keeps only grounded pros (L589, L270). Pruned pros disappear from the audit. It is not stated whether `PeerReviewer` (L633) receives the pruned or the unpruned proposal. | Low |
| PROBE-10 | Counter semantics | The TurnRecord comment says `session_index` is the "completed-round count after this turn" (L362). It is really the cumulative world counter, which may start above 0. | Low |
| PROBE-11 | Request validation | A `contract_version` mismatch is implied invalid (literal type, L334) but is missing from Edge Case 5 (L847) and from the §7 tests. | Low |
| PROBE-12 | Example narrative | The rationale says the umpire "confirms its blocking argument" (L565), but the stored statement restates the argument ("could block" becomes "blocks"). | Low |
| PROBE-13 | Goal wording | L46 says generators "cannot introduce ungrounded setting details". World-change statements and umpire consequences add new details by design; only pros and anchors are grounded. | Low |
| PROBE-14 | Untestable rules | "Single declarative assertion … benefiting the active actor" (L123) cannot be checked mechanically, and the spec does not say it is advisory. | Low |

---

### 3. Detailed Critiques & Blind Spots

#### 3.1 Data Schema Completeness

* **[issue] (blocking) PROBE-02, §3.1 L218:** `canon_facts.items` needs `minLength` plus a non-whitespace rule.
  The spec also needs to say whether canon entries that are equal after normalisation are rejected or tolerated.
  Without this, the "Strict Epistemic Grounding" goal (L46) can be bypassed by a caller-supplied blank fact.
* **[issue] (blocking) PROBE-01:** "Non-whitespace string" (L269, L383–387, L622) and "anchor-style normalisation" need a single definition, written once and referenced everywhere else. It should cover:
  * which whitespace characters count (for example Python `str.strip()` semantics);
  * which quote characters count (ASCII `"` and `'` only, or also curly quotes);
  * the stripping order (whitespace, then one quote pair, then whitespace again?);
  * whether the canon side is normalised for anchor and `source_ref` matching, as it is for novelty checks.

  Invariant 4's "match exactly an existing string" (L725–726) currently disagrees with L124, L693 and L708.
* **[issue] (blocking) PROBE-08, §2.0, §3.5 and §5:** Adapter outputs are given as abstract types.
  The spec does not say whether they arrive as mappings or models, or whether the strict integer rule at L204 (integers, not booleans) also applies to adapter output.
  For example, a `PeerEvaluation` with `baseline_plausibility: True` is not covered.
* **[suggestion] (non-blocking) PROBE-13, L227:** `id` has `minLength: 1` but can be whitespace-only. Consider the same non-whitespace rule.
* **[suggestion] (non-blocking) L204:** "No maximum length unless a non-empty constraint is stated" mixes two separate constraints. Consider rewording it.
* **[suggestion] (non-blocking) L100:** The `trio-d66-v1` contents are defined only by reference to source code. Consider pinning a content digest in the spec so the version identity can be checked without reading code.

#### 3.2 State Mutation & Deterministic Consistency

* **[issue] (blocking) PROBE-03, PROBE-04 and PROBE-05:** `RunFailure.code` is part of the versioned contract, so every adapter-output defect needs exactly one error code.
  At present, these cases each map to two plausible codes or to none:
  * a duplicate-canon draft;
  * a non-`canon_fact` source type;
  * a pro count outside `[1, 2]`;
  * a mismatched `voter_actor_id`.

  The spec should state a precedence order, for example "schema shape → `ProposalGenerationError`, then the semantic gates → `InvalidProposalError`".
  It should then remove the canon-novelty clause from the `ProposalDraft` type (L622) or say explicitly that the clause is enforced as `InvalidProposalError`.
* **[issue] (blocking) PROBE-07, Invariant 14 and §5 step 2:** The shuffle input should be the actor IDs in `WorldState.actors` order.
  The spec should also add a golden vector whose input is unsorted, so the tests can catch an implementation that sorts first.
* **[issue] (blocking) PROBE-06, L379 and L601–603 versus L575:** The spec should either define a closed set of reason strings or templates, such as `success:proposal-appended`, `failure:umpire-consequence`, `turn-tick` and `round-complete`, joined in execution order, or drop the claim that the text is engine-generated and deterministic.
  The current example cannot have come from the engine.
* **[praise]** The atomic publication rule (Invariant 11), the rule that umpire callbacks never touch the RNG (Invariant 10), and the exact draw sequence (Invariant 14) are clear and make reproducible runs straightforward.
  The worked example matches seed `20` exactly.
* **[question] (non-blocking) PROBE-09:** Is the `Proposal` passed to `PeerReviewer` the pruned version?
  If so, the spec should say so, and it should consider recording the pruned pros for audit.
* **[nitpick] (non-blocking) PROBE-10, L362:** Reword the comment to "world `session_index` after this turn".
* **[suggestion] (non-blocking):** When `seed` is omitted, the run cannot be reproduced afterwards.
  Consider returning the effective seed in `RunResult` to support the auditability goal.
  Separately, recording the full `canon_facts` array in each `before`/`after` grows quadratically over long runs; consider acknowledging this.

#### 3.3 Testability & Verification Strategy

* **[issue] (blocking, covered by PROBE-01 and PROBE-06):** The §7 tests for normalisation (L914, "New Proposals", "New Failure State") and for state-change records (L941) need fixed expected values.
  Until the normalisation and reason vocabulary are defined, these tests can only check that one implementation agrees with itself, not that it meets the contract.
* **[issue] (blocking, covered by PROBE-08):** The "Required Callables" test (§7) and Edge Case 16 need a defined runner signature.
  They also need a definition of a "missing" callable, so tests can be written without guessing the API.
* **[suggestion] (non-blocking):** Add §7 cases for each of the following:
  * a blank or duplicate canon fact in the input;
  * a mismatched `voter_actor_id`;
  * a `contract_version` mismatch (PROBE-11);
  * an adapter returning a boolean where an integer is expected.
* **[suggestion] (non-blocking) PROBE-14:** Mark "single declarative assertion … benefiting the active actor" (L123) as narrative guidance that the engine does not enforce.
  Similarly, narrow the goal at L46 to say that pros and anchors are the grounded parts.
* **[nitpick] (non-blocking) PROBE-12, L565:** Align the rationale with the restated statement, for example "the umpire restates its blocking argument as a concrete event".

---

### 4. Required Revisions

1. **Single normalisation definition (PROBE-01):** Write one normative definition covering:
   * the whitespace set and the quote characters;
   * how many quote pairs are stripped, and the stripping order;
   * whether canon entries are normalised for anchor and `source_ref` matching.

   Reconcile L47, Invariant 4 (L725–726), Invariant 5, Edge Case 2 (L838), L124, L693 and L708 with it.
   Define "non-whitespace string" in terms of the same rule.
2. **Constrain `canon_facts` (PROBE-02):** Require non-whitespace items in the §3.1 schema, and state whether entries that are equal after normalisation are rejected with `InvalidRunRequestError`.
   Add the matching Edge Case 5 entry and §7 test.
3. **One error code per adapter-output defect (PROBE-03, PROBE-04, PROBE-05):** Cover a canon-duplicate draft, a non-`canon_fact` source type, a pro count outside `[1, 2]`, and a `voter_actor_id` that does not match the requested voter.
   Remove or clarify the conflicting clause in the L622 type, reconcile Invariant 5 with the L259 literal, and name the error in the L942 test.
4. **Define `StateChange.reason` (PROBE-06):** Give a fixed vocabulary or template for the engine-generated text, and correct the §3.4 example (L575) so it uses that format.
5. **Pin the shuffle input order (PROBE-07):** State that the shuffle input is the actor IDs in `WorldState.actors` order.
   Add a golden vector with an unsorted actor list.
6. **Define the runner entry point (PROBE-08):** Resolve whether the engine or the caller supplies the proposal and peer adapters (L50 and L75 versus L76 and L789).
   Specify:
   * how the four callables are passed;
   * what counts as "missing";
   * the representation of adapter return values, including whether strict integers (L204) apply to them.

---

### 5. Recommendation & Sign-Off

* **Verdict:** Revisions Required
* **Notes for Elephant Agent:** The mechanics, draw order, binary resolution, failure-consequence flow and atomicity rules are sound, and the worked examples are internally consistent.
  The blocking items are all about determinism and testability: wherever the contract exposes a value (normalised strings, error codes, reason text, shuffle input, callable binding), two independent implementations must produce the same result.
  Each revision is local and should not disturb the rest of the design.
  Fix revisions 1 and 2 together, because the blank-anchor loophole comes from how they interact.
  The non-blocking observations (PROBE-09 to PROBE-14, the effective-seed suggestion and the table-digest suggestion) can be handled in the same edit or deferred.
  After these changes, the spec should be ready for confirmation and human sign-off.

---

## Spec Version 1.0.0: Historical Review

**Review Target:** [`docs/designs/001_tome_core_architecture.md`](../designs/001_tome_core_architecture.md)
**Reviewer:** Goldfish Reviewer Agent (Zero Context)  
**Date:** 2026-11-08  
**Specification Version:** 1.0.0
**Verdict:** Approved

---

## 1. Executive Summary

The specification defines a transport-neutral engine boundary with versioned run inputs and outputs, turn/round behavior, provider adapter contracts, deterministic mechanics, and explicit failure semantics. The reviewed revision resolves findings on proposal metadata ownership, state-change ordering, exhaustion validation, partial runs, seeded draws, custom spark tables, and boon cleanup.

---

## 2. Invariant & Edge-Case Probing

| ID | Area / Component | Finding | Status |
| :--- | :--- | :--- | :--- |
| PROBE-01 | Proposal Adapter | Engine attaches posture and spark mechanics to `ProposalDraft`; adapter output no longer has to invent the roll. | **Resolved** |
| PROBE-02 | State-Change Ordering | Changed top-level fields sort by ascending JSON Pointer; the example follows the rule. | **Resolved** |
| PROBE-03 | Exhausted-Trait Validation | Initial exhausted traits must be unique members of the faction's trait list. | **Resolved** |
| PROBE-04 | Run Ordering & Counters | Each run starts its own order; partial rounds do not resume, and counter/exhaustion behavior is defined. | **Resolved** |
| PROBE-05 | Seeded Mechanics | Per-die `randint` mapping, draw order, golden vector, Odd pairing, and custom table input/fallback are specified. | **Resolved** |
| PROBE-06 | Adapter Failures & Atomicity | Adapter signatures, typed errors, no engine retries, input immutability, and no partial result are specified. | **Resolved** |
| PROBE-07 | Outcomes & Audit Records | Rumor order/content, boon recovery/cleanup, and end-of-turn net state deltas are defined. | **Resolved** |
| PROBE-08 | Engine/Bridge Boundary | UI, transport, authorization, persistence, and provider selection remain outside the engine contract. | **Resolved** |

---

## 3. Detailed Critiques & Blind Spots

### 3.1 Data Schema Completeness

The WorldState constraints relevant to identity and exhaustion, Proposal and PeerEvaluation structures, ProposalDraft adapter return, RunRequest/RunResult/TurnRecord, SparkTables, and failure categories are defined. Undeclared fields, invalid custom tables, and invalid exhausted-trait state are rejected.

### 3.2 State Mutation & Deterministic Consistency

The run order and partial-run behavior are explicit. Seeded mechanics define stream draw order and include a Python 3.11 golden vector. Boon recovery occurs before round-end cleanup; recovered traits may be reused on later turns in that round. State-change records contain net end-of-turn values and use deterministic JSON Pointer ordering.

### 3.3 Testability & Verification Strategy

The verification plan covers seeded draw vectors, table validation, order cycling, exact rumor ordering, boon reuse and cleanup, state immutability, and atomic failure. These tests can validate the engine contract independently from transport or provider choice.

---

## 4. Required Revisions

None.

---

## 5. Recommendation & Sign-Off

* **Verdict:** **Approved**
* **Notes for Elephant Agent:** The reviewed specification resolves the identified contract gaps. No further mandatory changes are required before contract validation and implementation handoff.
