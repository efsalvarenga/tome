# Design Specification: TriO Matrix Engine (TOME) Core Architecture

**Document ID:** `docs/designs/001_tome_core_architecture.md`  

| Metadata | Value |
| :--- | :--- |
| Spec Version | 1.1.0 |
| Interface Contract Version | 1.0.0 |
| Status | Under Review |
| Author | Elephant Agent & Developer |
| Target Milestone | v0.1.0 (Core Engine & Pure-Python Mechanics) |

### Changelog

| Spec Version | Summary |
| :--- | :--- |
| 1.1.0 | Revision under human review: standardized TriO naming and actor terminology across prose and contract identifiers; replaced step-dice and persistent actor posture with a per-turn d6 posture; defined built-in default spark tables with optional complete caller overrides and two tables selected randomly each turn, independently of tier; simplified resolution to 2d6 plus peer votes against 7+; removed mechanical trackers, exhaustion, boons, and outcome bands. Deferred actor traits; only `canon_facts` provides grounding references. Added optional human-umpire rejection of illogical vote shifts before resolution, with an audit trail. The interface contract remains a 1.0.0 draft pending approval. |
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

The engine-side integration supplies proposal-generation and peer-review implementations through the adapters in Section 3.5. The caller may also supply an optional umpire-review callback to apply the human user's decisions before resolution. These callables are not serialized into `RunRequest`; collecting user input, provider selection, credentials, and transport remain outside this contract. Mechanics, validation, turn ordering, state transitions, and result records remain governed by this specification.

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
* **Supporting Arguments (Pros):** 1 to 2 arguments explicitly grounded in existing `canon_facts`.

### 2.4 Peer Review & Vote Adjustment

Every non-active actor evaluates the proposal as an independent adjudicator:
1. **Baseline Plausibility:** Rate proposal as $+1$ (Plausible), $0$ (Uncertain), or $-1$ (Implausible).
2. **Strategic Alignment:** Describe whether the outcome is `beneficial`, `neutral`, or `hostile` to the voter. This is narrative metadata, not an additional mechanical constraint on vote direction.
3. **Vote Adjustment:** May shift the final vote by at most $\pm 1$ step from baseline. The resulting `final_vote` is clamped to $[-1, +1]$:
   * $+1 \to +1$ (unaltered beneficial)
   * $+1 \to 0$ (hostile shift down)
   * $0 \to -1$ (hostile shift down)
   * $-1 \to 0$ (beneficial shift up)
   * $0 \to +1$ (beneficial shift up)
   * An individual voter's `final_vote` is strictly bounded within $\{-1, 0, +1\}$.
4. **Grounding & Umpire Review:** If a shift is attempted ($\text{shift} \neq 0$), the voter MUST cite a valid anchor from `canon_facts`. If the anchor is missing or invalid, or the human umpire (the user of the engine) deems the reasoning for the shift illogical, the vote reverts to baseline. Citation validity is checked mechanically; logical rejection is the umpire's decision, not an automatic engine judgement. Facts are reusable references: citing one does not consume or mechanically change it.

The numeric difference between final vote and baseline determines whether a shift was attempted; the adapter's `biased_shift_applied` flag does not authorize or prevent one. After mechanical validation and any umpire review, the engine sets that flag to whether a non-zero shift remains. Invalid or umpire-rejected shifts revert to baseline with the flag false and anchor null; unchanged votes also have the flag false and anchor null. Remaining shifted votes retain the normalized anchor. `goal_alignment` remains descriptive for all three values.

Correctly cited shifts proceed unless the umpire rejects them through the optional callback in Section 3.5. There is no mandatory approval pause when that callback is absent. Rejections are applied before summing votes or rolling resolution dice; they restore `baseline_plausibility`, not a new vote chosen by the umpire. The original evaluation and the umpire's reason are retained in the turn record.

### 2.5 Matrix Adjudication & State Mutation

$$\text{Net Modifier} = \max\left(-3, \min\left(3, \sum \text{final\_vote}\right)\right)$$

Resolution roll: $2d6 + \text{Net Modifier}$ against target number 7:

| $2d6 + \text{Mod}$ | Outcome | Narrative State Mutation |
| :---: | :--- | :--- |
| **7+** | **Success** | Append the proposal's world-change statement to `canon_facts` if not already present. |
| **Below 7** | **Failure** | The proposed change does not enter canon. Record the attempt and rationale without adding facts, rumors, complications, or counter-facts. |

There are no critical success/failure bands or secondary boons. Peer arguments inform the modifier and remain in the audit record; they do not automatically become facts. `active_rumors`, actor records, and all other narrative state remain unchanged by resolution. Every resolved turn advances time regardless of success or failure.

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
  world_change_statement: non-whitespace string,
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
  goal_alignment: "beneficial" | "neutral" | "hostile",
  biased_shift_applied: boolean,
  cited_anchor: string | null,
  final_vote: integer in [-1, 1],
  public_argument: string
}
```

```json
{
  "voter_actor_id": "actor_dock_syndicate",
  "baseline_plausibility": 1,
  "goal_alignment": "hostile",
  "biased_shift_applied": true,
  "cited_anchor": "The conduit is open.",
  "final_vote": 0,
  "public_argument": "The conduit is open, but that does not establish exclusive control."
}
```

### 3.4 Run Request, Result, and Turn Record (Interface Contract v1.0.0)

The caller supplies a full world state and a positive number of turns, with optional spark-table overrides, actor order for the first round, and random seed. If `first_round_order` is omitted, the engine creates a random permutation; when `seed` is supplied, that permutation is reproducible. The supplied order must contain every actor ID exactly once. The engine repeats that order until the requested number of turns has completed.

The interface types are:

```text
RunRequest = {
  contract_version: "1.0.0",
  world_state: WorldState,
  turn_count: integer where turn_count >= 1,
  spark_tables?: SparkTables,
  first_round_order?: string[],
  seed?: integer where seed >= 0
}

RunResult = {
  contract_version: "1.0.0",
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

RunError =
  InvalidRunRequestError |
  ProposalGenerationError |
  InvalidProposalError |
  PeerReviewError |
  UmpireReviewError |
  MechanicsError

RunFailure = {
  contract_version: "1.0.0",
  code: "INVALID_RUN_REQUEST" | "PROPOSAL_GENERATION_FAILED" |
        "INVALID_PROPOSAL" | "PEER_REVIEW_FAILED" | "UMPIRE_REVIEW_FAILED" |
        "MECHANICS_FAILED",
  message: string
}
```

`turn_index` and `session_index` in a record are their values after the turn has resolved and the round boundary (if any) has been processed. `adjusted_total` is `resolution_roll + net_vote_modifier`.

`first_round_order`, `seed`, and `spark_tables` are optional. None of these fields accepts `null`. Omitting `spark_tables` selects the built-in defaults; omitting `seed` initializes the run-local random generator from system entropy and makes the run non-reproducible.

The complete example below demonstrates an override using illustrative caller-supplied cue labels. These entries are not the built-in defaults. To use defaults instead, omit the entire `spark_tables` field.

```json
{
  "contract_version": "1.0.0",
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

The successful result contains the complete final world state and exactly one ordered record for each completed turn:

```json
{
  "contract_version": "1.0.0",
  "spark_table_source": "request",
  "final_world_state": {
    "session_index": 0,
    "turn_index": 1,
    "canon_facts": [
      "The conduit is open.",
      "The Iron Choir claims the conduit."
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
          "baseline_plausibility": 0,
          "goal_alignment": "hostile",
          "biased_shift_applied": false,
          "cited_anchor": null,
          "final_vote": 0,
          "public_argument": "The Dock Syndicate remains uncertain."
        }
      ],
      "umpire_rejections": [],
      "net_vote_modifier": 0,
      "resolution_roll": 7,
      "adjusted_total": 7,
      "outcome": "Success",
      "state_changes": [
        {
          "path": "/canon_facts",
          "before": ["The conduit is open."],
          "after": [
            "The conduit is open.",
            "The Iron Choir claims the conduit."
          ],
          "reason": "The proposal entered canon because the adjusted total met target number 7."
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

Each `turn_record` preserves the proposal and its grounded pros, its `trio_tier`, its two selected table names/entry values in `spark_tags`, all peer evaluations after mechanical validation and any umpire rejections, the clamped net vote modifier, resolution roll and adjusted total, success or failure, and the state changes applied by that turn. `umpire_rejections` preserves the original mechanically validated evaluation and the user's reason for each rejected shift, in peer-evaluation order. An empty list means no umpire rejections were applied, not that a human approved every vote. The record explains why the final state changed; it is not a UI-formatted dossier.

`peer_evaluations` contains exactly one evaluation for each non-active actor, in the order those actors appear in the input `WorldState`. `state_changes` contains each changed top-level `WorldState` field exactly once, ordered by ascending JSON Pointer. Each entry's `before` and `after` are the complete JSON values of that field; `reason` describes every deterministic engine rule that affected it, in execution order. These values represent the net change at the end of the turn, including counter updates. A completed run contains exactly `turn_count` records, including failed attempts; errors use one of the `RunError` types and never include a partial result.

The proposal's `active_actor_id` must equal the actor taking the turn; its die is always `d6`, its roll is the engine's turn-local posture roll, and its tier must match that roll. Its two spark tags must match the d66 entries from the independently selected distinct tables in selection order, not a tier-specific pairing. Each peer evaluation's voter ID must identify a distinct non-active actor. A caller-supplied state must contain every field in Section 3.1; actor IDs are non-empty and unique. All contract objects reject undeclared fields.

### 3.5 Engine-Side Adapters & Optional Umpire Review

The runner invokes two engine-side adapters and may invoke a caller-supplied umpire-review callback. None is part of the serialized `RunRequest`; how a UI or bridge gathers the human user's decisions is outside this specification:

```text
ProposalDraft = {
  world_change_statement: non-whitespace string,
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
```

The proposal generator returns only a `ProposalDraft`; the engine creates the complete `Proposal` by attaching the active actor ID, posture die and roll, tier, and spark tags already resolved for that turn. Each adapter must return the declared schema and must not mutate its arguments. The runner supplies isolated snapshots of the current state and proposal. Provider/network errors or malformed output become `ProposalGenerationError` or `PeerReviewError`. The engine applies grounding and voting validation to returned values. It prunes ungrounded proposal pros; if no grounded pro remains, it raises `InvalidProposalError` without automatically retrying. Any adapter retry policy is outside the engine contract. Engine errors expose the stable code and message represented by `RunFailure`; an execution bridge maps those values into its chosen transport response without returning partial state.

If configured and at least one valid shifted vote remains after mechanical checks, the runner invokes `UmpireReview` once before computing the turn's modifier. It receives isolated snapshots of the proposal, all mechanically validated evaluations, and the pre-resolution world state. `turn_index` identifies the turn being resolved (`world_state.turn_index + 1`). The callback conveys the human umpire's decisions, not additional peer-agent votes; it must not mutate its arguments or consume the engine's RNG.

The callback returns zero or more rejections, each naming a distinct voter whose vote still differs from baseline and giving the user's reason. Returning `[]` leaves votes unchanged. For each rejection, the engine records an independent copy of the pre-reversion evaluation, restores `final_vote` to `baseline_plausibility`, sets `biased_shift_applied` to false, and clears `cited_anchor`. The baseline and public argument are unchanged. The engine builds `UmpireRejectionRecord` entries itself and includes them in peer-evaluation order; peer-review providers cannot supply these records.

If the callback is absent or no shifted votes remain, it is not invoked and `umpire_rejections` is empty. Duplicate/unknown voter IDs, rejection of a vote already at baseline, blank reasons, malformed output, or a callback failure/cancellation raise `UmpireReviewError` with code `UMPIRE_REVIEW_FAILED`. The engine must not silently proceed, retry, or publish a partial result on callback failure.

The generator receives the TriO tier and both selected spark tags together as the narrative starting cues. It must not replace the sampled tables with a tier-specific pair or treat their entries as grounding evidence. The active actor and current world state provide narrative context; only `canon_facts` provides grounding references.

An empty or whitespace-only world-change statement is malformed proposal output and raises `ProposalGenerationError` before adjudication; it must never enter canon. Non-blank statements retain their original text.

---

## 4. Invariants & Rules

* **Invariant 1 (Run Turn Order):** The caller may supply `first_round_order`, which must be a permutation of all actor IDs. If omitted, the engine creates a random permutation; a supplied seed makes that order reproducible. This order remains fixed and repeats until the requested turns are complete. Every new `RunRequest` starts at the beginning of its own order; partial rounds are not resumed across requests.
* **Invariant 2 (Per-Turn Posture):** Every turn rolls one d6: 1-3 means Obvious, 4-5 means Option, and 6 means Odd. The selected posture is turn-local; no actor condition changes this mapping.
* **Invariant 3 (Vote Adjustment Limits & Bounds):** A peer evaluation shift $(\text{final\_vote} - \text{baseline\_plausibility})$ cannot exceed $\pm 1$. Any deviation $> 1$ or $< -1$ is invalid and reverts to baseline. Both `baseline_plausibility` and `final_vote` are strictly constrained to $\{-1, 0, +1\}$.
* **Invariant 4 (Grounding & Umpire Rejection):** Any non-zero vote shift $(\text{shift} \neq 0)$ requires `cited_anchor` (after stripping whitespace and enclosing quotation marks) to match exactly an existing string in `canon_facts`. A missing/invalid anchor or human-umpire rejection of the reasoning discards the shift: `final_vote` reverts to `baseline_plausibility`, the shift flag becomes false, and the anchor is cleared. Correctly cited shifts remain unless explicitly rejected by the optional callback. Valid anchors remain reusable across turns.
* **Invariant 5 (Proposal Pro Grounding Gate):** Each entry in `supporting_pros` must use `source_type: "canon_fact"` and its normalized `source_ref` must match a known canon fact. Ungrounded pros are pruned. The proposal proceeds only if at least 1 grounded pro remains; otherwise, the run fails with `InvalidProposalError` and the engine does not regenerate the proposal.
* **Invariant 6 (Narrative-Only Trackers):** Rumors and actor conditions carry narrative information only. They are not consumed, recovered, stepped, or used as automatic numeric modifiers. Grounded peer votes are the only adjustment to the resolution roll.
* **Invariant 7 (Binary Resolution):** An adjusted total of 7 or more is Success; a lower total is Failure. Success appends the world-change statement to canon only if absent. Failure introduces no narrative changes. Neither outcome adds rumors or peer arguments to canon automatically.
* **Invariant 8 (Net Modifier Clamping):** After mechanical checks and any umpire rejections, sum the resulting final peer votes and clamp to $[-3, +3]$ inclusive before rolling $2d6$.
* **Invariant 9 (Time Always Advances):** Success and Failure both resolve the turn and advance its time counter. A failed attempt is not an engine error and remains in `turn_records`.
* **Invariant 10 (Deterministic Core Isolation):** No network socket, external process, or non-deterministic clock affects mechanical calculations. One Python `random.Random` instance is created per run, seeded from `seed` or system entropy. With a seed, identical proposal/peer outputs, and identical umpire rejections, mechanics are reproducible for the same engine/runtime version. Adapters and the umpire callback do not consume the engine's random stream.
* **Invariant 11 (State and Result Atomicity):** The submitted `WorldState` is never mutated. The engine returns a final state and exactly `turn_count` records only after all requested turns complete; on any failure it raises an explicit error and returns no partial state.
* **Invariant 12 (Time and Round Counters):** `turn_index` increments once after each resolved turn. Within a request, `session_index` increments once after every complete pass through that request's order; it does not increment for an incomplete final pass. A new request starts a new order rather than resuming an incomplete pass. There are no round-end tracker resets.
* **Invariant 13 (Unique Actor Identity):** Actor IDs must be unique and non-empty so that each run order identifies exactly one actor per turn.
* **Invariant 14 (Seeded Draw Order):** If `first_round_order` is omitted, `rng.shuffle` consumes the run's first random draws. Each turn draws one posture d6 with `rng.randint(1, 6)`, then selects two distinct tables with `rng.sample(["Action", "Focus", "Method", "Disposition", "Motivation"], 2)`. Preserve sample order. In that order, roll one d66 per table using two `rng.randint(1, 6)` calls (tens, then units), and convert to tens-times-ten plus units. After proposal/peer validation and any umpire review, roll the two resolution d6. Neither tier, table contents, nor umpire decisions changes this draw sequence; JSON object key order must not affect table selection.
  * **Golden Vector (Python 3.11):** With seed `42`, actor IDs `["actor_a", "actor_b"]`, and no supplied order, shuffle produces `["actor_b", "actor_a"]`. The first posture roll is `1` (Obvious), selected tables are `Method` then `Focus`, their d66 rolls are `22` and `61`, and resolution dice are `6` and `6` (base total `12`).
* **Invariant 15 (Explicit Failure Types):** Invalid requests raise `InvalidRunRequestError`; proposal generation, invalid proposals, peer review, umpire review, and mechanics failures raise their corresponding `RunError` type. No engine-level retry or partial result is permitted.
* **Invariant 16 (Narrative Sparks):** Use the built-in default set when the request omits `spark_tables`, or the complete valid caller override when supplied. Every turn uniformly selects two distinct tables from the effective set without using the tier as a selection criterion; all table pairs are available to every tier, and selection resets each turn. The two entries and tier are narrative starting cues only. Drawing a spark never automatically changes world state.

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
   c. Validate and prune proposal pros against `canon_facts` only; if none remain, fail with `InvalidProposalError`.
   d. Obtain one peer evaluation from every non-active actor, then apply shift and canon-fact grounding validation without consuming any fact.
   e. If an umpire callback is configured and any shifted votes remain, obtain its rejections and validate them. Preserve each rejected evaluation and the user's reason, then revert only those shifts to baseline. Without a callback or without rejections, mechanically valid votes proceed.
   f. Sum the post-review final votes, clamp to $[-3, +3]$, roll 2d6, and add the modifier.
   g. If the adjusted total is at least 7, record Success and append the proposal statement to canon if absent. Otherwise record Failure and leave narrative state unchanged. Do not generate automatic rumors, complications, boons, or counter-facts.
   h. Increment `turn_index`. If every actor in the fixed run order has acted, increment `session_index`. Record the proposal, final evaluations, umpire rejections, roll, modifier, Success/Failure, and end-of-turn state delta in a `TurnRecord`.
4. Return `RunResult` with the final state and ordered records. If the requested count ends partway through a round, return that partial round's state and records without incrementing `session_index`. A later request starts a fresh order and does not resume that round.

The engine works on an isolated copy of the input state. It publishes no partial result: if validation, proposal generation, peer review, umpire review, or mechanics fail, it raises an explicit error and the caller retains its original state unchanged.

### Outputs & Events

The successful output is the versioned `RunResult` in Section 3.4. The engine does not write files, append history, create a dossier, or emit transport-specific progress events. A caller may persist the returned state and turn records as it chooses.

---

## 6. Edge Cases & Failure Modes

* **Edge Case 1: Repeated Fact Citations:** The same canon fact may ground multiple turns. Citations neither consume references nor create tracker state.
* **Edge Case 2: Hallucinated Anchor Strings:** Peer reviews might include leading/trailing whitespace or enclosing quotes. The linter gate strips outer whitespace and one matching enclosing quote pair before checking exact membership. If not found in `canon_facts`, the shift is reverted.
* **Edge Case 3: One Actor:** A one-actor run is valid; it has no peer evaluations, so the net modifier is $0$. The one-actor order completes a round on every turn.
* **Edge Case 4: Resolution Boundaries:** Total 6 fails; total 7 succeeds. Higher and lower totals have no additional effects. An already-present statement is not duplicated on success. A failed roll still produces a turn record and advances time.
* **Edge Case 5: Invalid Run Request:** A non-positive `turn_count`, negative seed, empty actor set, duplicate/empty actor ID, undeclared tracker field, or `first_round_order` that is not an exact permutation is rejected with `InvalidRunRequestError` before execution. The caller's input state remains untouched.
* **Edge Case 6: Proposal or Peer-Review Failure:** Any engine-side proposal or peer-review integration failure, including malformed output, aborts with `ProposalGenerationError` or `PeerReviewError`. The engine does not retry. No partial state or turn records are returned.
* **Edge Case 7: Proposal Without Grounded Pros:** Ungrounded pros are pruned. If none remain, the run aborts with `InvalidProposalError`; the engine does not request regeneration.
* **Edge Case 8: Run Ends Mid-Round:** The engine returns all resolved turn records and the corresponding partial-round state. `turn_index` reflects every resolved turn; `session_index` advances only for complete passes within this request. A subsequent request starts a new order rather than continuing the previous one.
* **Edge Case 9: Default or Invalid Spark Tables:** An omitted `spark_tables` field selects built-in defaults. A supplied null payload, missing or extra table name, extra or missing d66 key, or non-string/blank entry is rejected with `InvalidRunRequestError` before execution. Invalid overrides are never silently replaced with defaults.
* **Edge Case 10: Umpire Rejects a Cited Shift:** Even an exact canon citation does not prevent rejection of illogical reasoning. Revert the vote to its original baseline before aggregation, clear its shift flag and anchor, and preserve the original evaluation and reason in `umpire_rejections`. A valid rejection is normal adjudication, not an engine failure.
* **Edge Case 11: No Umpire Intervention:** An absent callback, no remaining shifted votes, or an empty rejection list adds no rejections or approval requirement. Mechanically valid shifts proceed. A configured callback that fails or returns invalid decisions instead raises `UmpireReviewError`; it must not be treated as no intervention.

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
* **Optional Umpire Callback:** Assert runs without a callback proceed unattended; no remaining shifts skips the callback; a configured callback receives all validated evaluations once per eligible turn. Empty decisions leave valid shifts unchanged. Callback decisions consume no RNG draws.
* **Umpire Audit and Errors:** Assert rejected evaluations, original anchors, and user reasons are retained independently in peer order. Reject duplicate/unknown voters, votes already at baseline, blank reasons, malformed returns, and callback failures/cancellation with `UmpireReviewError`; preserve the submitted state and return no partial result.
* **Proposal and Evaluation Schemas:** Assert adapter output validation, engine attachment of turn mechanics to `ProposalDraft`, and one ordered peer evaluation per non-active actor.
* **Voting Metadata:** Assert alignment is descriptive and normalized shift flags/anchors follow the numeric shift, grounding checks, and any umpire rejections, including inconsistent adapter flags.
* **Closed State Schema:** Assert unknown fields are rejected at both world-state and actor-object levels.
* **Non-Blank Proposals:** Reject empty and whitespace-only statements before any resolution roll or canon insertion.
* **Net Modifier Clamping:** Assert extreme positive and negative vote sums clamp strictly at $[-3, +3]$.
* **Binary Resolution:** Assert adjusted totals 6 and 7 resolve to Failure and Success respectively; all totals below 7 behave alike and all totals at least 7 behave alike. Only successful proposals enter canon, without duplicates. Failures still advance time and emit records.
* **Narrative State Preservation:** Assert resolution never automatically changes rumors or actor records; no posture, exhaustion, recovery, boon, complication, or counter-fact is created.
* **State-Change Records:** Assert each changed top-level field appears once, sorted by ascending JSON Pointer, with before/after values and deterministic reason text.
* **Deferred and Removed Actor Fields:** Reject actor traits and legacy persistent posture/exhaustion fields as undeclared fields; reject `actor_trait` as a supporting argument's source type.

### Integration Tests

* End-to-end run tests for exact turn counts, order cycling, seeded initial order, per-turn records, time counters, partial-round behavior, and final state.
* Compare identical seeded runs with and without a human rejection: dice draws stay the same, but the modifier, outcome, and resulting canon reflect the post-review votes. Include a callback failure after an earlier resolved turn to verify run-wide atomicity.
* Assert the input `WorldState` remains unchanged after both successful and failed runs, and that failures expose no partial result.

---

## 8. Goldfish Review Gates

The [Goldfish review report](../reviews/001_tome_core_architecture_review.md) records the historical 1.0.0 approval and findings on an earlier 1.1.0 draft. Human review subsequently changed actor terminology, the spark-table contract, grounding scope, and the optional umpire-review interface. Independent review of the current draft and human approval remain pending.

- [ ] Zero-context Goldfish review completed for the current Spec Version 1.1.0 draft
- [ ] Goldfish confirmation of corrected contract gaps for Spec Version 1.1.0
- [ ] Human developer approval signed off
