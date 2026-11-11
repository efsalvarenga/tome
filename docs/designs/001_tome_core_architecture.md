# Design Specification: TriO Matrix Engine (TOME) Core Architecture

**Document ID:** `docs/designs/001_tome_core_architecture.md`  

| Metadata | Value |
| :--- | :--- |
| Spec Version | 1.1.0 |
| Interface Contract Version | 1.1.0 |
| Status | Under Review |
| Author | Elephant Agent & Developer |
| Target Milestone | v0.1.0 (Core Engine & Pure-Python Mechanics) |

### Changelog

| Spec Version | Summary |
| :--- | :--- |
| 1.1.0 | Revision under human review: standardized TriO and actor terminology; replaced persistent posture and step-dice with a per-turn d6; provided default spark tables with complete caller overrides and tier-independent random selection; simplified resolution to 2d6 plus peer votes against 7+; deferred actor traits and retained canon-only grounding; removed mechanical trackers, exhaustion, boons, and outcome bands; added optional pre-roll umpire rejection of illogical shifts and mandatory umpire resolution of failures into new canon consequences based on the lowest final peer votes; required proposals to be new to canon so every resolved turn, Success or Failure, adds exactly one new fact; removed the descriptive `goal_alignment` field from peer evaluations; bumped the interface contract to 1.1.0 for the changed actor schema, binary outcome, umpire callbacks, and `failure_resolution`/`umpire_rejections` records, as a draft pending approval. |
| 1.0.0 | Retained the engine mechanics and defined a transport-neutral multi-turn execution contract. Removed UI, hosting, authentication, deployment, persistence, and provider-selection requirements from the active scope. |

#### Deferred UI / Execution-Bridge Scope

The previous design included a static exploration dashboard/PWA, GitHub Pages hosting, GitHub Actions dispatch, client-side PAT storage, workflow passcodes, execution locks, spend ceilings, and file-based state/history/dossier persistence. These are deferred for a future UI and execution-bridge design. They are intentionally not requirements of this engine contract; the previous document revision remains available through Git history.

---

## 1. Overview & Objectives

The **TriO Matrix Engine (TOME)** is a turn-based simulation engine for exploring emergent realisations in complex multi-agent systems where fundamental behavioral dynamics are incomplete, uncertain, or emergent. It synthesizes the structured argumentation and mechanical probability resolution of **Chris Engle Matrix Games** with the behavioral divergence mechanics of **Cezar Capacle's Triple-O framework**.

**TOME** models multi-actor interactions, institutional friction, and strategic adaptations without relying on conversational consensus, fixed utility equations, or ungrounded claims. The engine accepts a complete world state and a bounded run request, then returns the final state and an auditable per-turn rationale:

$$\mathcal{M}(\text{WorldState}_{t}, \text{RunRequest}) \longrightarrow (\text{WorldState}_{t+n}, \text{TurnRecord}_{1..n})$$

### Goals

* **Deterministic Mechanical Core:** Each turn uses a d6 for posture (1-3 Obvious, 4-5 Option, 6 Odd), d66 lookups on two randomly selected tables independently of posture, and 2d6 plus peer votes against target number 7. Tables come from built-in defaults or a complete caller override. A supplied seed fixes the engine-controlled random sequence for the same engine/runtime version.
* **Narrative-Only Trackers:** Actor conditions and capabilities are narrative facts, not mechanical meters. There are no persistent posture levels, consumable capability pools, recovery mechanics, or automatic bonuses from trackers. Turn and round counters record simulation time only.
* **Strict Epistemic Grounding (The Linter Gate):** Proposal generators and peer reviewers cannot introduce ungrounded setting details or arbitrary voting shifts. Citation checks enforce whitespace-stripped exact matching against existing `canon_facts` only; they do not prove that the argument is logical. The human umpire may reject illogical vote shifts through an optional pre-resolution review callback.
* **Transport-Neutral Execution Contract:** Define versioned input, output, turn-order, validation, and failure semantics without prescribing a UI, transport, hosting provider, or persistence mechanism.
* **Isolated Provider Boundary:** Proposal generation and peer review may be supplied by engine-side adapters; this specification does not select an LLM provider or expose provider credentials through the contract.
* **Narrative Progression Every Turn:** Every resolved turn adds exactly one new fact to canon.
  Success adds the proposal, which must be new to canon.
  Failure adds a new, umpire-resolved consequence instead of merely rejecting the proposal.
  Later actors observe that new fact immediately.

### Non-Goals

* UI implementation, UI hosting, request transport, authentication, authorization, workflow dispatch, and deployment architecture.
* File, database, or repository persistence; the caller owns saving returned state and turn records.
* A specific LLM provider, model tier, retry policy, or provider credential mechanism.
* Open-ended conversational chat simulation between actors (all interactions are strictly structured into Proposal, Grounding, and Adjudication phases).
* Direct in-engine hosting of external narrative vaults (TOME operates as a standalone engine that accepts and returns standardized JSON state and turn records).

---

## 2. Domain Framing & Engine Execution Contract

### 2.0 Execution Boundary

The engine contract describes values and behavior, not a transport. A caller submits a complete `WorldState` and a run request, and receives a completed `RunResult`. The caller is responsible for transport, authorization, persistence, and presenting results. A UI or execution bridge may use synchronous calls, asynchronous jobs, or another mechanism without changing this contract.

The engine-side integration supplies proposal-generation and peer-review implementations through the adapters in Section 3.5.
The caller may also supply an optional umpire-review callback to apply the human user's decisions before the roll.
A separate umpire-controlled failure resolver must provide a consequence after every failed roll.
These callables are not serialized into `RunRequest`; collecting user input, provider selection, credentials, and transport remain outside this contract.
Mechanics, validation, turn ordering, state transitions, and result records remain governed by this specification.

### 2.1 Per-Turn d6 Posture

Every actor uses the same d6 to select a posture for its current turn:

| d6 Roll | Posture | Meaning |
| :---: | :--- | :--- |
| 1-3 | Obvious | A predictable initiative given established canon and the actor's agenda. |
| 4-5 | Option | A lateral but strategically logical initiative. |
| 6 | Odd | An atypical, radical, or unexpected initiative. |

Posture is a turn-local result, not a persistent actor tracker. It is recorded as `trio_tier` in the proposal for compatibility with the draft contract's terminology. Every turn rolls anew; prior successes, failures, and narrative conditions do not change the die or its thresholds.

### 2.2 Dual Spark Table Seeding

The engine comes with five default d66 tables: `Action`, `Focus`, `Method`, `Disposition`, and `Motivation`. The built-in set is identified as `trio-d66-v1`; its contents are the template mappings in [src/tome/tables.py](../../src/tome/tables.py). Changes to the built-in mappings require a new table-set version.

If `RunRequest.spark_tables` is omitted, the engine uses those defaults. A caller may instead supply a complete replacement set containing all five named tables. Partial overrides, null payloads, and malformed tables are rejected rather than silently replaced with defaults.

For each turn, the engine selects two distinct tables uniformly at random from those five, independently of the TriO tier. It rolls one d66 entry from each selected table. Table selection is fresh on every turn, so a table may be used again on later turns.

The two entry values and the independently rolled Obvious/Option/Odd tier form the actor's narrative starting cues for proposing a contribution to the changed state. They are not established facts, supporting evidence, or numeric modifiers. The proposal must still ground its supporting arguments in existing `canon_facts`.

The engine records the two cues in selection order as `spark_tags`, each formatted `<TableName>:<entry>`, and passes them together with the tier to the proposal generator. No table is assigned to a particular tier.

$d66$ uses one-based senary (base-six) notation: two digits, each from 1 to 6, identify one of 36 table entries.

### 2.3 Engle Matrix Game Formulation

A proposal is a structured argument:
* **World-Change Statement:** A single declarative assertion specifying an altered fact in the world benefiting the active actor.
  It must be new: it may not match an existing canon fact after anchor-style normalization.
* **Supporting Arguments (Pros):** 1 to 2 arguments explicitly grounded in existing `canon_facts`.

### 2.4 Peer Review & Vote Adjustment

Every non-active actor evaluates the proposal as an independent adjudicator:

1. **Baseline Plausibility:** Rate the proposal as $+1$ (Plausible), $0$ (Uncertain), or $-1$ (Implausible).
   The voter gives arguments for its submitted vote, including any shift made in the next step.
2. **Vote Adjustment:** A voter may shift its final vote by at most one step up or down from its baseline.
   The shift lets an actor tilt how plausible it claims the proposal is according to its own goals, rather than its honest assessment alone.
   Shifts in either direction are allowed.
   The permitted shifts are $+1 \to 0$, $0 \to -1$, $0 \to +1$, and $-1 \to 0$.
   Every vote is always $-1$, $0$, or $+1$, before and after any shift.
   A shift of more than one step is invalid and the vote reverts to its baseline (Invariant 3).
3. **Grounding & Umpire Review:** A shifted vote must cite a valid anchor from `canon_facts`.
   If the anchor is missing or invalid, the vote reverts to its baseline.
   If the shift is cited correctly but its reasoning is illogical, the human umpire (the user of the engine) may reject it, and the vote reverts to its baseline.
   Citation validity is checked mechanically; rejecting illogical reasoning is the umpire's decision, not an automatic engine judgement.
   Facts are reusable references: citing one does not consume or mechanically change it.

The numeric difference between final vote and baseline determines whether a shift was attempted; the adapter's `biased_shift_applied` flag does not authorize or prevent one.
After mechanical validation and any umpire review, the engine sets that flag to whether a non-zero shift remains.
Invalid or umpire-rejected shifts revert to baseline with the flag false and anchor null; unchanged votes also have the flag false and anchor null.
Remaining shifted votes retain the normalized anchor.

Correctly cited shifts proceed unless the umpire rejects them through the optional pre-roll callback in Section 3.5.
There is no mandatory vote-approval pause when that callback is absent.
Rejections are applied before summing votes or rolling resolution dice; they restore `baseline_plausibility`, not a new vote chosen by the umpire.
The original evaluation and the umpire's reason are retained in the turn record.
This optional pre-roll review is separate from the umpire resolution required after a failed roll.

### 2.5 Matrix Adjudication & State Mutation

$$\text{Net Modifier} = \max\left(-3, \min\left(3, \sum \text{final\_vote}\right)\right)$$

Resolution roll: $2d6 + \text{Net Modifier}$ against target number 7:

| $2d6 + \text{Mod}$ | Outcome | Narrative State Mutation |
| :---: | :--- | :--- |
| **7+** | **Success** | Append the proposal's world-change statement, already validated as new, to `canon_facts`. |
| **Below 7** | **Failure** | Do not enact the proposal; instead add a new, umpire-resolved failure consequence based on the lowest final peer votes to `canon_facts`. |

There are no critical success/failure bands or secondary boons.
Both outcomes change the world: every resolved turn appends exactly one new fact to `canon_facts`.
On success, the proposal itself is the new fact.
On failure, the selected or umpire-restated reason becomes a new canon consequence explaining why the proposal did not occur.
`active_rumors` and actor records remain unchanged by resolution.
Every resolved turn advances time regardless of success or failure.

### 2.6 Failure Consequences

After a failed roll, identify the lowest `final_vote` among all non-active actors after citation validation and any umpire rejections.
Every peer evaluation at that value is a failure candidate, even if the minimum is 0 or +1.
Use the final votes, not the original attempted shifts or baseline scores.

The human umpire resolves every failure through `FailureResolver` before the turn is committed.
If several candidates have the same lowest vote, the umpire selects the reason rather than the engine breaking the tie randomly or alphabetically.
The selected peer's existing `public_argument` is used directly when it is a suitable, concrete failure explanation.
Peer arguments retain ordinary pro/con wording; no separate failure-statement field is required from peers.
The umpire may restate an unsuitable argument or supply a consequence when none of the lowest-scored arguments is usable.
If there are no peers, the umpire supplies the consequence.

The result must describe a concrete new event or condition explaining the failed proposal, such as "The buyer fails to pay because it went bankrupt."
It is a new canonical outcome, not merely an audit note or a repeated fact.
The engine checks that the statement is non-blank and not already present in canon after the same whitespace/outer-quote normalization used for anchors.
It must not match the rejected proposal's world-change statement either.
The umpire judges its narrative suitability and novelty beyond those mechanical checks.
The consequence enters the run's working `canon_facts` immediately, so the next actor sees the changed world even if the requested turns end before a round completes.
The completed run result is still published atomically.
The turn record preserves the source actor when applicable, the original argument through its peer evaluation, the final consequence, and the umpire's rationale.

---

## 3. State Schema & Data Models

### 3.1 World State (`world_state.json`)

All listed fields are required except fields explicitly marked optional elsewhere. Object fields reject undeclared properties. Integer fields are JSON integers, not booleans; string fields have no maximum length unless a non-empty constraint is stated.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "WorldState",
  "type": "object",
  "additionalProperties": false,
  "required": ["session_index", "turn_index", "canon_facts", "active_rumors", "actors"],
  "properties": {
    "session_index": { "type": "integer", "minimum": 0 },
    "turn_index": { "type": "integer", "minimum": 0 },
    "canon_facts": {
      "type": "array",
      "items": { "type": "string" }
    },
    "active_rumors": {
      "type": "array",
      "items": { "type": "string" }
    },
    "actors": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "name", "agenda"],
        "properties": {
          "id": { "type": "string", "minLength": 1 },
          "name": { "type": "string" },
          "agenda": { "type": "string" }
        }
      }
    }
  }
}
```

For every actor, `id` must be non-empty and unique in the world state. Actor traits are deferred from this revision; actors contain only `id`, `name`, and `agenda`. Name and agenda supply narrative context, not grounding evidence. Actor capabilities or conditions may be cited only if stated in `canon_facts`. Legacy payloads containing deferred or removed fields must be adapted by the caller; undeclared fields reject the run as `InvalidRunRequestError`.

### 3.2 Proposal Contract (Stage 3)

```text
SupportingPro = {
  source_type: "canon_fact",
  source_ref: string,
  argument: string
}

Proposal = {
  active_actor_id: string,
  posture_die: "d6",
  posture_roll: integer in [1, 6],
  trio_tier: "Obvious" | "Option" | "Odd",
  spark_tags: string[] with exactly 2 tags from distinct randomly selected tables,
  world_change_statement: non-whitespace string not already in canon_facts,
  supporting_pros: SupportingPro[1..2] with at least 1 grounded entry after pruning
}
```

```json
{
  "active_actor_id": "actor_iron_choir",
  "posture_die": "d6",
  "posture_roll": 6,
  "trio_tier": "Odd",
  "spark_tags": ["Focus:Resource access", "Method:Public declaration"],
  "world_change_statement": "The Iron Choir claims the conduit.",
  "supporting_pros": [
    {
      "source_type": "canon_fact",
      "source_ref": "The conduit is open.",
      "argument": "The open conduit gives the Iron Choir access."
    }
  ]
}
```

### 3.3 Peer Evaluation Contract (Stage 4)

```text
PeerEvaluation = {
  voter_actor_id: string,
  baseline_plausibility: integer in [-1, 1],
  biased_shift_applied: boolean,
  cited_anchor: string | null,
  final_vote: integer in [-1, 1],
  public_argument: string
}
```

`public_argument` retains the peer's ordinary pro/con reasoning.
It is the voter's reasoning for its submitted `final_vote`, including any shift.
It is not rewritten if the shift is reverted; `umpire_rejections` records the reversion, and the umpire judges the argument's fit when resolving a failure.
It is a possible source for a failure consequence, not a fact merely because the peer states it.
The human umpire decides whether it can be used directly, must be restated, or is unsuitable as a failure explanation.

```json
{
  "voter_actor_id": "actor_dock_syndicate",
  "baseline_plausibility": 1,
  "biased_shift_applied": true,
  "cited_anchor": "The conduit is open.",
  "final_vote": 0,
  "public_argument": "The conduit is open, but that does not establish exclusive control."
}
```

### 3.4 Run Request, Result, and Turn Record (Interface Contract v1.1.0)

The caller supplies a full world state and a positive number of turns, with optional spark-table overrides, actor order for the first round, and random seed. If `first_round_order` is omitted, the engine creates a random permutation; when `seed` is supplied, that permutation is reproducible. The supplied order must contain every actor ID exactly once. The engine repeats that order until the requested number of turns has completed.

The interface types are:

```text
RunRequest = {
  contract_version: "1.1.0",
  world_state: WorldState,
  turn_count: integer where turn_count >= 1,
  spark_tables?: SparkTables,
  first_round_order?: string[],
  seed?: integer where seed >= 0
}

RunResult = {
  contract_version: "1.1.0",
  final_world_state: WorldState,
  spark_table_source: "trio-d66-v1" | "request",
  turn_records: TurnRecord[] where length == RunRequest.turn_count
}

SparkTables = {
  Action: Record<D66, non-whitespace string>,
  Focus: Record<D66, non-whitespace string>,
  Method: Record<D66, non-whitespace string>,
  Disposition: Record<D66, non-whitespace string>,
  Motivation: Record<D66, non-whitespace string>
}

D66 = exactly the 36 keys with tens and units digits from 1 through 6;
      JSON serializes each key as its decimal string

TurnRecord = {
  turn_index: integer >= 1,             // value after this turn's tick
  session_index: integer >= 0,          // completed-round count after this turn
  active_actor_id: string,
  proposal: Proposal,
  peer_evaluations: PeerEvaluation[],
  umpire_rejections: UmpireRejectionRecord[],
  net_vote_modifier: integer in [-3, 3],
  resolution_roll: integer in [2, 12],
  adjusted_total: integer in [-1, 15],
  outcome: "Success" | "Failure",
  failure_resolution: FailureResolution | null,
  state_changes: StateChange[]
}

StateChange = {
  path: string,                        // JSON Pointer to a changed top-level field
  before: JSON value,
  after: JSON value,
  reason: string                       // deterministic rule-based explanation
}

UmpireRejection = {
  voter_actor_id: string,
  reason: non-whitespace string
}

UmpireRejectionRecord = {
  voter_actor_id: string,
  reason: non-whitespace string,
  evaluation_before_reversion: PeerEvaluation
}

FailureResolution = {
  source_voter_actor_id: string | null,
  world_change_statement: non-whitespace string,
  rationale: non-whitespace string
}

RunError =
  InvalidRunRequestError |
  ProposalGenerationError |
  InvalidProposalError |
  PeerReviewError |
  UmpireReviewError |
  UmpireResolutionError |
  MechanicsError

RunFailure = {
  contract_version: "1.1.0",
  code: "INVALID_RUN_REQUEST" | "PROPOSAL_GENERATION_FAILED" |
        "INVALID_PROPOSAL" | "PEER_REVIEW_FAILED" | "UMPIRE_REVIEW_FAILED" |
        "UMPIRE_RESOLUTION_FAILED" | "MECHANICS_FAILED",
  message: string
}
```

`turn_index` and `session_index` in a record are their values after the turn has resolved and the round boundary (if any) has been processed. `adjusted_total` is `resolution_roll + net_vote_modifier`.

`first_round_order`, `seed`, and `spark_tables` are optional. None of these fields accepts `null`. Omitting `spark_tables` selects the built-in defaults; omitting `seed` initializes the run-local random generator from system entropy and makes the run non-reproducible.

The complete example below demonstrates an override using illustrative caller-supplied cue labels. These entries are not the built-in defaults. To use defaults instead, omit the entire `spark_tables` field.

```json
{
  "contract_version": "1.1.0",
  "world_state": {
    "session_index": 0,
    "turn_index": 0,
    "canon_facts": ["The conduit is open."],
    "active_rumors": [],
    "actors": [
      {
        "id": "actor_iron_choir",
        "name": "Iron Choir",
        "agenda": "Control the conduit"
      },
      {
        "id": "actor_dock_syndicate",
        "name": "Dock Syndicate",
        "agenda": "Protect trade"
      }
    ]
  },
  "turn_count": 1,
  "spark_tables": {
    "Action": {
      "11": "Action 11", "12": "Action 12", "13": "Action 13", "14": "Action 14", "15": "Action 15", "16": "Action 16",
      "21": "Action 21", "22": "Action 22", "23": "Action 23", "24": "Action 24", "25": "Action 25", "26": "Action 26",
      "31": "Action 31", "32": "Action 32", "33": "Action 33", "34": "Action 34", "35": "Action 35", "36": "Action 36",
      "41": "Action 41", "42": "Action 42", "43": "Action 43", "44": "Action 44", "45": "Action 45", "46": "Action 46",
      "51": "Action 51", "52": "Action 52", "53": "Action 53", "54": "Action 54", "55": "Action 55", "56": "Action 56",
      "61": "Action 61", "62": "Action 62", "63": "Action 63", "64": "Action 64", "65": "Action 65", "66": "Action 66"
    },
    "Focus": {
      "11": "Focus 11", "12": "Focus 12", "13": "Focus 13", "14": "Focus 14", "15": "Focus 15", "16": "Focus 16",
      "21": "Focus 21", "22": "Focus 22", "23": "Focus 23", "24": "Focus 24", "25": "Focus 25", "26": "Focus 26",
      "31": "Focus 31", "32": "Focus 32", "33": "Focus 33", "34": "Focus 34", "35": "Focus 35", "36": "Focus 36",
      "41": "Focus 41", "42": "Focus 42", "43": "Focus 43", "44": "Focus 44", "45": "Focus 45", "46": "Focus 46",
      "51": "Focus 51", "52": "Focus 52", "53": "Focus 53", "54": "Focus 54", "55": "Focus 55", "56": "Focus 56",
      "61": "Focus 61", "62": "Focus 62", "63": "Focus 63", "64": "Focus 64", "65": "Focus 65", "66": "Resource access"
    },
    "Method": {
      "11": "Method 11", "12": "Method 12", "13": "Public declaration", "14": "Method 14", "15": "Method 15", "16": "Method 16",
      "21": "Method 21", "22": "Method 22", "23": "Method 23", "24": "Method 24", "25": "Method 25", "26": "Method 26",
      "31": "Method 31", "32": "Method 32", "33": "Method 33", "34": "Method 34", "35": "Method 35", "36": "Method 36",
      "41": "Method 41", "42": "Method 42", "43": "Method 43", "44": "Method 44", "45": "Method 45", "46": "Method 46",
      "51": "Method 51", "52": "Method 52", "53": "Method 53", "54": "Method 54", "55": "Method 55", "56": "Method 56",
      "61": "Method 61", "62": "Method 62", "63": "Method 63", "64": "Method 64", "65": "Method 65", "66": "Method 66"
    },
    "Disposition": {
      "11": "Disposition 11", "12": "Disposition 12", "13": "Disposition 13", "14": "Disposition 14", "15": "Disposition 15", "16": "Disposition 16",
      "21": "Disposition 21", "22": "Disposition 22", "23": "Disposition 23", "24": "Disposition 24", "25": "Disposition 25", "26": "Disposition 26",
      "31": "Disposition 31", "32": "Disposition 32", "33": "Disposition 33", "34": "Disposition 34", "35": "Disposition 35", "36": "Disposition 36",
      "41": "Disposition 41", "42": "Disposition 42", "43": "Disposition 43", "44": "Disposition 44", "45": "Disposition 45", "46": "Disposition 46",
      "51": "Disposition 51", "52": "Disposition 52", "53": "Disposition 53", "54": "Disposition 54", "55": "Disposition 55", "56": "Disposition 56",
      "61": "Disposition 61", "62": "Disposition 62", "63": "Disposition 63", "64": "Disposition 64", "65": "Disposition 65", "66": "Disposition 66"
    },
    "Motivation": {
      "11": "Motivation 11", "12": "Motivation 12", "13": "Motivation 13", "14": "Motivation 14", "15": "Motivation 15", "16": "Motivation 16",
      "21": "Motivation 21", "22": "Motivation 22", "23": "Motivation 23", "24": "Motivation 24", "25": "Motivation 25", "26": "Motivation 26",
      "31": "Motivation 31", "32": "Motivation 32", "33": "Motivation 33", "34": "Motivation 34", "35": "Motivation 35", "36": "Motivation 36",
      "41": "Motivation 41", "42": "Motivation 42", "43": "Motivation 43", "44": "Motivation 44", "45": "Motivation 45", "46": "Motivation 46",
      "51": "Motivation 51", "52": "Motivation 52", "53": "Motivation 53", "54": "Motivation 54", "55": "Motivation 55", "56": "Motivation 56",
      "61": "Motivation 61", "62": "Motivation 62", "63": "Motivation 63", "64": "Motivation 64", "65": "Motivation 65", "66": "Motivation 66"
    }
  },
  "first_round_order": ["actor_iron_choir", "actor_dock_syndicate"],
  "seed": 20
}
```

`first_round_order` and `seed` are optional. `turn_count` must be a positive integer and `seed`, when supplied, must be a non-negative integer. The run request does not include credentials, storage paths, transport metadata, or provider-specific configuration.
When supplied, `spark_tables` must contain exactly the five named tables, each with exactly the 36 valid d66 keys and a non-whitespace string value for every key. Missing tables, extra table names, and incomplete tables are invalid. `spark_table_source` in the result is `request` for a valid override, or `trio-d66-v1` when the request omits overrides.

A completed run returns the complete final world state and exactly one ordered record for each completed turn, including turns whose proposal failed.
In this example, the base roll of 7 receives a -1 peer modifier, so the proposal fails at 6 and the umpire resolves the peer's blocking argument into a new consequence:

```json
{
  "contract_version": "1.1.0",
  "spark_table_source": "request",
  "final_world_state": {
    "session_index": 0,
    "turn_index": 1,
    "canon_facts": [
      "The conduit is open.",
      "The Dock Syndicate blocks the approach, preventing the Iron Choir from claiming the conduit."
    ],
    "active_rumors": [],
    "actors": [
      {
        "id": "actor_iron_choir",
        "name": "Iron Choir",
        "agenda": "Control the conduit"
      },
      {
        "id": "actor_dock_syndicate",
        "name": "Dock Syndicate",
        "agenda": "Protect trade"
      }
    ]
  },
  "turn_records": [
    {
      "turn_index": 1,
      "session_index": 0,
      "active_actor_id": "actor_iron_choir",
      "proposal": {
        "active_actor_id": "actor_iron_choir",
        "posture_die": "d6",
        "posture_roll": 6,
        "trio_tier": "Odd",
        "spark_tags": ["Focus:Resource access", "Method:Public declaration"],
        "world_change_statement": "The Iron Choir claims the conduit.",
        "supporting_pros": [
          {
            "source_type": "canon_fact",
            "source_ref": "The conduit is open.",
            "argument": "The open conduit gives the Iron Choir access."
          }
        ]
      },
      "peer_evaluations": [
        {
          "voter_actor_id": "actor_dock_syndicate",
          "baseline_plausibility": -1,
          "biased_shift_applied": false,
          "cited_anchor": null,
          "final_vote": -1,
          "public_argument": "The Dock Syndicate could block the approach to prevent this claim."
        }
      ],
      "umpire_rejections": [],
      "net_vote_modifier": -1,
      "resolution_roll": 7,
      "adjusted_total": 6,
      "outcome": "Failure",
      "failure_resolution": {
        "source_voter_actor_id": "actor_dock_syndicate",
        "world_change_statement": "The Dock Syndicate blocks the approach, preventing the Iron Choir from claiming the conduit.",
        "rationale": "The only peer has the lowest final vote; the umpire confirms its blocking argument as the cause of failure."
      },
      "state_changes": [
        {
          "path": "/canon_facts",
          "before": ["The conduit is open."],
          "after": [
            "The conduit is open.",
            "The Dock Syndicate blocks the approach, preventing the Iron Choir from claiming the conduit."
          ],
          "reason": "The umpire-resolved blocking event explains why the claim fails."
        },
        {
          "path": "/turn_index",
          "before": 0,
          "after": 1,
          "reason": "One simulation turn completed."
        }
      ]
    }
  ]
}
```

Each `turn_record` preserves the proposal and its grounded pros, its `trio_tier`, its two selected table names/entry values in `spark_tags`, all peer evaluations after mechanical validation and any umpire rejections, the clamped net vote modifier, resolution roll and adjusted total, success or failure, and the state changes applied by that turn.
`umpire_rejections` preserves the original mechanically validated evaluation and the user's reason for each rejected shift, in peer-evaluation order.
An empty list means no umpire rejections were applied, not that a human approved every vote.
`failure_resolution` is null for Success and contains the validated umpire decision for Failure.
For a peer-sourced consequence, `source_voter_actor_id` identifies a lowest-voted peer whose original `public_argument` remains available in `peer_evaluations`.
If no lowest-vote candidate provides a usable source, or there are no peers, the umpire sets the source to null and explains why a supplied consequence is needed in `rationale`.
The engine does not infer that judgement from the argument text.
The record explains why the final state changed; it is not a UI-formatted dossier.

`peer_evaluations` contains exactly one evaluation for each non-active actor, in the order those actors appear in the input `WorldState`. `state_changes` contains each changed top-level `WorldState` field exactly once, ordered by ascending JSON Pointer. Each entry's `before` and `after` are the complete JSON values of that field; `reason` describes every deterministic engine rule that affected it, in execution order. These values represent the net change at the end of the turn, including counter updates. A completed run contains exactly `turn_count` records, including failed attempts; errors use one of the `RunError` types and never include a partial result.

The proposal's `active_actor_id` must equal the actor taking the turn; its die is always `d6`, its roll is the engine's turn-local posture roll, and its tier must match that roll. Its two spark tags must match the d66 entries from the independently selected distinct tables in selection order, not a tier-specific pairing. Each peer evaluation's voter ID must identify a distinct non-active actor. A caller-supplied state must contain every field in Section 3.1; actor IDs are non-empty and unique. All contract objects reject undeclared fields.

### 3.5 Engine-Side Adapters & Umpire Callbacks

The runner invokes two engine-side adapters, may invoke the optional pre-roll `UmpireReview`, and invokes `FailureResolver` after every failed roll.
None is part of the serialized `RunRequest`; how a UI or bridge gathers the human user's decisions is outside this specification:

```text
ProposalDraft = {
  world_change_statement: non-whitespace string not already in canon_facts,
  supporting_pros: SupportingPro[1..2]
}

ProposalGenerator(
  active_actor: Actor,
  tier: PostureTier,
  spark_tags: string[],
  world_state: WorldState
) -> ProposalDraft

PeerReviewer(
  voter_actor: Actor,
  proposal: Proposal,
  world_state: WorldState
) -> PeerEvaluation

UmpireReview(
  turn_index: integer >= 1,
  proposal: Proposal,
  peer_evaluations: PeerEvaluation[],
  world_state: WorldState
) -> UmpireRejection[]

FailureResolver(
  turn_index: integer >= 1,
  proposal: Proposal,
  peer_evaluations: PeerEvaluation[],
  candidate_voter_ids: string[],
  adjusted_total: integer in [-1, 6],
  world_state: WorldState
) -> FailureResolution
```

The proposal generator returns only a `ProposalDraft`; the engine creates the complete `Proposal` by attaching the active actor ID, posture die and roll, tier, and spark tags already resolved for that turn. Each adapter must return the declared schema and must not mutate its arguments. The runner supplies isolated snapshots of the current state and proposal. Provider/network errors or malformed output become `ProposalGenerationError` or `PeerReviewError`. The engine applies grounding and voting validation to returned values. It prunes ungrounded proposal pros; if no grounded pro remains, it raises `InvalidProposalError` without automatically retrying. Any adapter retry policy is outside the engine contract. Engine errors expose the stable code and message represented by `RunFailure`; an execution bridge maps those values into its chosen transport response without returning partial state.

If configured and at least one valid shifted vote remains after mechanical checks, the runner invokes `UmpireReview` once before computing the turn's modifier. It receives isolated snapshots of the proposal, all mechanically validated evaluations, and the pre-resolution world state. `turn_index` identifies the turn being resolved (`world_state.turn_index + 1`). The callback conveys the human umpire's decisions, not additional peer-agent votes; it must not mutate its arguments or consume the engine's RNG.

The callback returns zero or more rejections, each naming a distinct voter whose vote still differs from baseline and giving the user's reason. Returning `[]` leaves votes unchanged. For each rejection, the engine records an independent copy of the pre-reversion evaluation, restores `final_vote` to `baseline_plausibility`, sets `biased_shift_applied` to false, and clears `cited_anchor`. The baseline and public argument are unchanged. The engine builds `UmpireRejectionRecord` entries itself and includes them in peer-evaluation order; peer-review providers cannot supply these records.

If the callback is absent or no shifted votes remain, it is not invoked and `umpire_rejections` is empty. Duplicate/unknown voter IDs, rejection of a vote already at baseline, blank reasons, malformed output, or a callback failure/cancellation raise `UmpireReviewError` with code `UMPIRE_REVIEW_FAILED`. The engine must not silently proceed, retry, or publish a partial result on callback failure.

After every failed roll, the runner invokes the caller-supplied, human-umpire-controlled `FailureResolver` before updating canon or time counters.
Its `turn_index` identifies the turn being resolved (`world_state.turn_index + 1`).
The callback receives isolated snapshots of the proposal, all post-review peer evaluations, the lowest-vote candidate IDs in peer-evaluation order, the adjusted total, and the current world state.
With no peer evaluations, `candidate_voter_ids` is empty.
The callback must not mutate those inputs or consume engine RNG draws.

The callback returns the human umpire's `FailureResolution`.
A non-null `source_voter_actor_id` must identify one of the lowest-vote candidates, even when the umpire restates the selected argument.
Tied candidates require the umpire's choice, not an engine-generated tie-break.
When the chosen `public_argument` is suitable, its text is the consequence; otherwise the umpire may restate it as a concrete failure event.
If none of the candidates provides a usable source, or no peers exist, the umpire may supply the consequence with a null source and a rationale explaining that decision.
The engine validates the source ID and non-blank fields but does not independently decide whether ordinary pro/con reasoning is narratively suitable.

The returned statement must remain non-blank after anchor-style normalization and must not equal any normalized canon fact or the rejected proposal's normalized statement.
The original returned text is stored in canon and the audit record after those checks.
The engine records the validated decision in `failure_resolution` and applies it before the next actor's turn.
On Success, `FailureResolver` is not invoked and `failure_resolution` is null.

A missing required resolver or decision, a non-lowest/unknown source actor, a non-null source when no peers exist, blank fields, an already-canonical or rejected-proposal statement, malformed output, or callback failure/cancellation raises `UmpireResolutionError` with code `UMPIRE_RESOLUTION_FAILED`.
The engine does not replace an invalid decision with a random argument, generated story, or no-change outcome.
It does not retry or publish partial state on this error.

The generator receives the TriO tier and both selected spark tags together as the narrative starting cues. It must not replace the sampled tables with a tier-specific pair or treat their entries as grounding evidence. The active actor and current world state provide narrative context; only `canon_facts` provides grounding references.

An empty or whitespace-only world-change statement is malformed proposal output and raises `ProposalGenerationError` before adjudication; it must never enter canon.
A statement that matches an existing canon fact after anchor-style normalization raises `InvalidProposalError` before peer review.
The engine does not request regeneration.
Non-blank statements retain their original text.

---

## 4. Invariants & Rules

* **Invariant 1 (Run Turn Order):** The caller may supply `first_round_order`, which must be a permutation of all actor IDs. If omitted, the engine creates a random permutation; a supplied seed makes that order reproducible. This order remains fixed and repeats until the requested turns are complete. Every new `RunRequest` starts at the beginning of its own order; partial rounds are not resumed across requests.
* **Invariant 2 (Per-Turn Posture):** Every turn rolls one d6: 1-3 means Obvious, 4-5 means Option, and 6 means Odd. The selected posture is turn-local; no actor condition changes this mapping.
* **Invariant 3 (Vote Adjustment Limits & Bounds):** Both `baseline_plausibility` and `final_vote` are always $-1$, $0$, or $+1$.
  A shift $(\text{final\_vote} - \text{baseline\_plausibility})$ may be at most one step.
  A two-step shift (from $+1$ to $-1$, or from $-1$ to $+1$) is invalid, and the vote reverts to its baseline.
* **Invariant 4 (Grounding & Umpire Rejection):** Any non-zero vote shift $(\text{shift} \neq 0)$ requires `cited_anchor` (after stripping whitespace and enclosing quotation marks) to match exactly an existing string in `canon_facts`. A missing/invalid anchor or human-umpire rejection of the reasoning discards the shift: `final_vote` reverts to `baseline_plausibility`, the shift flag becomes false, and the anchor is cleared. Correctly cited shifts remain unless explicitly rejected by the optional callback. Valid anchors remain reusable across turns.
* **Invariant 5 (Proposal Pro Grounding Gate):** Each entry in `supporting_pros` must use `source_type: "canon_fact"` and its normalized `source_ref` must match a known canon fact. Ungrounded pros are pruned. The proposal proceeds only if at least 1 grounded pro remains; otherwise, the run fails with `InvalidProposalError` and the engine does not regenerate the proposal.
* **Invariant 6 (Narrative-Only Trackers):** Rumors and actor conditions carry narrative information only. They are not consumed, recovered, stepped, or used as automatic numeric modifiers. Grounded peer votes are the only adjustment to the resolution roll.
* **Invariant 7 (Binary Resolution):** An adjusted total of 7 or more is Success; a lower total is Failure.
  Success appends the proposal's world-change statement to canon.
  Because proposals are validated as new before peer review, Success always adds a new fact.
  Failure does not enact the proposal; it adds an umpire-resolved failure consequence instead.
  Neither outcome adds rumors automatically.
* **Invariant 8 (Net Modifier Clamping):** After mechanical checks and any umpire rejections, sum the resulting final peer votes and clamp to $[-3, +3]$ inclusive before rolling $2d6$.
* **Invariant 9 (Time Always Advances):** Success and resolved Failure both advance the turn's time counter and remain in `turn_records`.
  A failed roll is not itself an engine error.
  Failure requires a valid new consequence before its turn can complete.
* **Invariant 10 (Deterministic Core Isolation):** No network socket, external process, or non-deterministic clock affects mechanical calculations.
  One Python `random.Random` instance is created per run, seeded from `seed` or system entropy.
  With a seed, identical proposal/peer outputs, and identical umpire rejections and failure resolutions, mechanics are reproducible for the same engine/runtime version.
  Adapters and umpire callbacks do not consume the engine's random stream.
* **Invariant 11 (State and Result Atomicity):** The submitted `WorldState` is never mutated.
  The engine returns a final state and exactly `turn_count` records only after all requested turns complete.
  An engine error, including an unavailable or invalid failure resolution, returns no partial state.
* **Invariant 12 (Time and Round Counters):** `turn_index` increments once after each resolved turn. Within a request, `session_index` increments once after every complete pass through that request's order; it does not increment for an incomplete final pass. A new request starts a new order rather than resuming an incomplete pass. There are no round-end tracker resets.
* **Invariant 13 (Unique Actor Identity):** Actor IDs must be unique and non-empty so that each run order identifies exactly one actor per turn.
* **Invariant 14 (Seeded Draw Order):** If `first_round_order` is omitted, `rng.shuffle` consumes the run's first random draws.
  Each turn draws one posture d6 with `rng.randint(1, 6)`, then selects two distinct tables with `rng.sample(["Action", "Focus", "Method", "Disposition", "Motivation"], 2)`.
  Preserve sample order.
  In that order, roll one d66 per table using two `rng.randint(1, 6)` calls (tens, then units), and convert to tens-times-ten plus units.
  After proposal/peer validation and any pre-roll umpire review, roll the two resolution d6.
  Failure resolution happens after the roll and draws no additional randomness.
  Neither tier, table contents, nor umpire decisions changes this draw sequence; JSON object key order must not affect table selection.
  * **Golden Vector (Python 3.11):** With seed `42`, actor IDs `["actor_a", "actor_b"]`, and no supplied order, shuffle produces `["actor_b", "actor_a"]`. The first posture roll is `1` (Obvious), selected tables are `Method` then `Focus`, their d66 rolls are `22` and `61`, and resolution dice are `6` and `6` (base total `12`).
* **Invariant 15 (Explicit Failure Types):** Invalid requests raise `InvalidRunRequestError`; proposal generation, invalid proposals, peer review, umpire review, umpire failure resolution, and mechanics failures raise their corresponding `RunError` type.
  No engine-level retry or partial result is permitted.
* **Invariant 16 (Narrative Sparks):** Use the built-in default set when the request omits `spark_tables`, or the complete valid caller override when supplied. Every turn uniformly selects two distinct tables from the effective set without using the tier as a selection criterion; all table pairs are available to every tier, and selection resets each turn. The two entries and tier are narrative starting cues only. Drawing a spark never automatically changes world state.
* **Invariant 17 (Lowest-Vote Failure Candidates):** For Failure, candidates are all non-active actors at the minimum post-review `final_vote`, including neutral or positive minima.
  Multiple lowest-vote candidates require an umpire selection rather than a deterministic or random engine tie-break.
  A selected peer source must belong to this set; the umpire may supply a null-source consequence when no candidate is usable or no peers exist.
* **Invariant 18 (New Failure Consequence):** Every resolved Failure appends exactly one new, umpire-resolved statement to canon before the next actor acts.
  The statement must not normalize to an existing canon fact or to the rejected proposal.
  When an argument is restated, only the returned consequence enters canon; the original argument remains in the audit record.
  A failed turn that only updates counters is not a valid resolved outcome.

---

## 5. Execution & State Mutation Logic

### Inputs & Triggers

The engine accepts a `RunRequest` as defined in Section 3.4: a complete `WorldState`, positive `turn_count`, and optional `spark_tables`, `first_round_order`, and `seed`. No passcode, transport token, file path, storage location, or deployment trigger is an engine input.

### Turn Execution

1. Validate the complete world state, unique actor IDs, positive `turn_count`, optional order permutation, and any supplied complete `spark_tables` override before executing any turn. A run requires at least one actor. Invalid supplied tables fail validation; they do not trigger a fallback.
2. Select the built-in `trio-d66-v1` tables if `spark_tables` is omitted; otherwise use the valid caller-supplied set unchanged. Create one `random.Random` instance from the non-negative `seed`, or system entropy when omitted. Select the first-round order from the supplied permutation, or shuffle the actor IDs with that instance.
3. Execute exactly `turn_count` turns, advancing through the order and restarting at its first actor after each complete pass:
   a. Roll one posture d6 and map it to Obvious/Option/Odd. Independently sample two distinct tables, roll one d66 entry from each, and construct their spark tags in selection order.
   b. Generate a `ProposalDraft` through the engine-side proposal-generation integration; the engine attaches the already-resolved active actor ID, posture die/roll, tier, and spark tags to form the `Proposal`.
   c. Reject a proposal statement that already matches a normalized canon fact with `InvalidProposalError`.
      Validate and prune proposal pros against `canon_facts` only; if none remain, fail with `InvalidProposalError`.
   d. Obtain one peer evaluation from every non-active actor, then apply shift and canon-fact grounding validation without consuming any fact.
   e. If an umpire callback is configured and any shifted votes remain, obtain its rejections and validate them. Preserve each rejected evaluation and the user's reason, then revert only those shifts to baseline. Without a callback or without rejections, mechanically valid votes proceed.
   f. Sum the post-review final votes, clamp to $[-3, +3]$, roll 2d6, and add the modifier.
   g. If the adjusted total is at least 7, record Success and append the proposal statement to canon.
   h. Otherwise record Failure, derive the lowest-final-vote candidate set, and obtain a validated `FailureResolution` from the human-umpire-controlled callback.
      Append exactly that new consequence to canon, not the rejected proposal or any additional automatic rumors or boons.
   i. Increment `turn_index`.
      If every actor in the fixed run order has acted, increment `session_index`.
      Record the proposal, final evaluations, umpire rejections, roll, modifier, outcome, nullable failure resolution, and end-of-turn state delta in a `TurnRecord`.
4. Return `RunResult` with the final state and ordered records. If the requested count ends partway through a round, return that partial round's state and records without incrementing `session_index`. A later request starts a fresh order and does not resume that round.

The engine works on an isolated copy of the input state.
If validation, proposal generation, peer review, umpire review, failure resolution, or mechanics fail, it raises an explicit error.
It publishes no partial result, and the caller retains its original state unchanged.

### Outputs & Events

The successful output is the versioned `RunResult` in Section 3.4. The engine does not write files, append history, create a dossier, or emit transport-specific progress events. A caller may persist the returned state and turn records as it chooses.

---

## 6. Edge Cases & Failure Modes

* **Edge Case 1: Repeated Fact Citations:** The same canon fact may ground multiple turns. Citations neither consume references nor create tracker state.
* **Edge Case 2: Hallucinated Anchor Strings:** Peer reviews might include leading/trailing whitespace or enclosing quotes. The linter gate strips outer whitespace and one matching enclosing quote pair before checking exact membership. If not found in `canon_facts`, the shift is reverted.
* **Edge Case 3: One Actor:** A one-actor run is valid; it has no peer evaluations, so the net modifier is $0$.
  On Failure, the umpire supplies a new consequence with `source_voter_actor_id: null`.
  The one-actor order completes a round on every resolved turn.
* **Edge Case 4: Resolution Boundaries:** Total 6 fails; total 7 succeeds.
  Higher and lower totals do not create additional outcome bands.
  Success adds the new proposal statement, a turn record, and a time tick.
  Failure produces a new consequence, a turn record, and a time tick after umpire resolution.
* **Edge Case 5: Invalid Run Request:** A non-positive `turn_count`, negative seed, empty actor set, duplicate/empty actor ID, undeclared tracker field, or `first_round_order` that is not an exact permutation is rejected with `InvalidRunRequestError` before execution. The caller's input state remains untouched.
* **Edge Case 6: Proposal or Peer-Review Failure:** Any engine-side proposal or peer-review integration failure, including malformed output, aborts with `ProposalGenerationError` or `PeerReviewError`. The engine does not retry. No partial state or turn records are returned.
* **Edge Case 7: Proposal Without Grounded Pros:** Ungrounded pros are pruned. If none remain, the run aborts with `InvalidProposalError`; the engine does not request regeneration.
* **Edge Case 8: Run Ends Mid-Round:** The engine returns all resolved turn records and the corresponding partial-round state. `turn_index` reflects every resolved turn; `session_index` advances only for complete passes within this request. A subsequent request starts a new order rather than continuing the previous one.
* **Edge Case 9: Default or Invalid Spark Tables:** An omitted `spark_tables` field selects built-in defaults. A supplied null payload, missing or extra table name, extra or missing d66 key, or non-string/blank entry is rejected with `InvalidRunRequestError` before execution. Invalid overrides are never silently replaced with defaults.
* **Edge Case 10: Umpire Rejects a Cited Shift:** Even an exact canon citation does not prevent rejection of illogical reasoning. Revert the vote to its original baseline before aggregation, clear its shift flag and anchor, and preserve the original evaluation and reason in `umpire_rejections`. A valid rejection is normal adjudication, not an engine failure.
* **Edge Case 11: Optional Pre-Roll Intervention:** An absent `UmpireReview`, no remaining shifted votes, or an empty rejection list adds no vote-approval requirement.
  Mechanically valid shifts proceed.
  A configured review callback that fails or returns invalid decisions raises `UmpireReviewError`; it must not be treated as no intervention.
  This optional review does not remove the need for `FailureResolver` after a failed roll.
* **Edge Case 12: Neutral or Positive Failure Candidates:** A failed roll can occur even when every peer voted 0 or +1.
  Select candidates at the lowest final value anyway.
  If their pro/con arguments do not explain failure, the umpire restates or supplies a new consequence instead of treating supportive wording as an established failure event.
* **Edge Case 13: Unsuitable or Repeated Failure Statement:** The umpire may restate a selected argument or supply a consequence if no candidate is usable.
  Returning a blank statement, an existing normalized canon fact, or the rejected proposal raises `UmpireResolutionError`.
  The engine must not silently complete the turn with no narrative change.
* **Edge Case 14: Missing or Invalid Failure Decision:** A failed roll without a resolver or valid decision raises `UmpireResolutionError`.
  Choosing a non-lowest or unknown peer source, or a non-null source when no peers exist, is invalid.
  Callback failure/cancellation also aborts the run with no partial result.
* **Edge Case 15: Proposal Already in Canon:** A proposal whose normalized statement matches an existing canon fact would add nothing on Success.
  It is rejected with `InvalidProposalError` before peer review, so no peer calls or resolution dice are spent on it.
  The engine does not request regeneration.

---

## 7. Verification & Automated Test Strategy

### Unit Tests (`tests/test_tome_core.py`)

* **Posture d6 Mapping:** Exhaustively assert faces 1-3 map to Obvious, 4-5 to Option, and 6 to Odd; every actor uses the same mapping. Assert no tier filters or replaces the random table selection.
* **Seeded Random Sequence:** Assert golden vectors for seeded actor-order shuffling, posture d6, two-table sampling, both d66 lookups, and resolution dice. Verify the canonical sampling list, sample order, and `randint(1, 6)` sequence, including independence from JSON key order.
* **Spark Table Defaults and Overrides:** Assert omitted `spark_tables` selects `trio-d66-v1`; valid complete overrides produce exact supplied `<TableName>:<entry>` tags and source `request`. Reject null payloads, missing/extra table names or d66 keys, and non-string/blank entries without falling back to defaults. Table-source selection must not consume RNG draws or alter the table-sampling procedure.
* **Narrative Spark Selection:** Assert each turn selects two distinct tables, all ten unordered pairs are eligible under all three tiers, and later turns may reuse tables. Verify the generator receives both entries and the tier together; sparks alone cannot ground supporting arguments or vote shifts.
* **Linter Gate Shift Bounds:** Assert shifts of $\pm 2$ are rejected and reverted to baseline. Assert `final_vote` values strictly stay within $\{-1, 0, +1\}$.
* **Grounding Gate Verification:** Assert only canon facts ground supporting arguments and shifted votes. Nonexistent strings, actor metadata, and spark entries do not qualify unless independently present in `canon_facts`. Assert the same canon fact can be reused on later turns without mutation.
* **Umpire Rejection:** Assert a human rejection reverts a correctly cited upward or downward shift to its exact baseline, sets the flag false and anchor null, and leaves baseline/public argument unchanged. Verify rejected votes are reverted before summation and clamping, while other votes are unchanged.
* **Optional Pre-Roll Callback:** Assert absence of `UmpireReview` adds no vote-approval requirement; no remaining shifts skips that callback.
  A configured callback receives all validated evaluations once per eligible turn.
  Empty decisions leave valid shifts unchanged.
  The separate failure-resolution requirement still applies after a failed roll.
  Callback decisions consume no RNG draws.
* **Umpire Audit and Errors:** Assert rejected evaluations, original anchors, and user reasons are retained independently in peer order. Reject duplicate/unknown voters, votes already at baseline, blank reasons, malformed returns, and callback failures/cancellation with `UmpireReviewError`; preserve the submitted state and return no partial result.
* **Proposal and Evaluation Schemas:** Assert adapter output validation, engine attachment of turn mechanics to `ProposalDraft`, and one ordered peer evaluation per non-active actor.
* **Voting Metadata:** Assert normalized shift flags/anchors follow the numeric shift, grounding checks, and any umpire rejections, including inconsistent adapter flags.
  Reject a peer evaluation containing the removed `goal_alignment` field as an undeclared field.
* **Closed State Schema:** Assert unknown fields are rejected at both world-state and actor-object levels.
* **Non-Blank Proposals:** Reject empty and whitespace-only statements before any resolution roll or canon insertion.
* **New Proposals:** Reject a proposal statement matching an existing canon fact after whitespace/outer-quote normalization with `InvalidProposalError`.
  Assert this happens before any peer review or resolution dice.
* **Net Modifier Clamping:** Assert extreme positive and negative vote sums clamp strictly at $[-3, +3]$.
* **Binary Resolution:** Assert adjusted totals 6 and 7 resolve to Failure and Success respectively; all totals below 7 use the failure-consequence path and all totals at least 7 use the success path.
  Success appends the new proposal statement to canon and records `failure_resolution: null`.
  Assert every resolved turn, Success or Failure, increases `canon_facts` by exactly one entry.
  Failure does not enact the proposal; it appends exactly one new umpire-resolved consequence, advances time, and emits a record.
* **Lowest-Vote Failure Candidates:** Assert candidates are exactly the peers with the lowest post-review final vote, including tied, all-neutral, and all-positive evaluations.
  Verify that pre-roll rejections can change the candidate set.
  Reject sources outside that set.
* **Umpire Failure Resolution:** Assert every failed roll invokes `FailureResolver`, even with one unique lowest candidate.
  Ties must use the umpire's chosen source rather than a random or alphabetical fallback.
  Suitable arguments may be used directly, while restatements preserve the original argument and source in the audit record.
  If no candidate is usable or there are no peers, accept an umpire-supplied null-source consequence with a rationale.
* **New Failure State:** Reject blank consequences, canon duplicates after whitespace/outer-quote normalization, and statements matching the rejected proposal.
  Assert each resolved Failure changes `canon_facts`, not just the time counters.
* **Failure Resolver Errors:** Reject a missing callback/decision, unknown or non-lowest sources, invalid fields, and callback failure/cancellation with `UmpireResolutionError`.
  A one-actor failure requires a null source.
  No invalid decision may become a no-op, automatic tie-break, generated fallback, or partial run result.
* **Narrative State Preservation:** Assert resolution does not automatically change rumors or actor records or create mechanical trackers and boons.
  On Failure, only the validated consequence enters canon; unselected arguments and the rejected proposal do not.
* **State-Change Records:** Assert each changed top-level field appears once, sorted by ascending JSON Pointer, with before/after values and deterministic reason text.
* **Deferred and Removed Actor Fields:** Reject actor traits and legacy persistent posture/exhaustion fields as undeclared fields; reject `actor_trait` as a supporting argument's source type.

### Integration Tests

* End-to-end run tests for exact turn counts, order cycling, seeded initial order, per-turn records, time counters, partial-round behavior, and final state.
* Compare identical seeded runs with and without a human vote rejection: dice draws stay the same, but the modifier, outcome, and resulting canon reflect the post-review votes.
* Verify the next actor's proposal/review inputs include the preceding failed turn's new consequence.
* Verify a run ending partway through a round still exports its last failure consequence.
* Include a missing or invalid failure decision after an earlier resolved turn to verify run-wide atomicity.
* Assert the input `WorldState` remains unchanged after both successful and failed runs, and that failures expose no partial result.

---

## 8. Goldfish Review Gates

The [Goldfish review report](../reviews/001_tome_core_architecture_review.md) records the historical 1.0.0 approval and findings on an earlier 1.1.0 draft.
Human review subsequently changed actor terminology, the spark-table contract, grounding scope, umpire interfaces, and failure-state progression.
Independent review of the current draft and human approval remain pending.

- [ ] Zero-context Goldfish review completed for the current Spec Version 1.1.0 draft
- [ ] Goldfish confirmation of corrected contract gaps for Spec Version 1.1.0
- [ ] Human developer approval signed off
