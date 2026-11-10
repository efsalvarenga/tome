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
| 1.1.0 | Revision under human review: standardized TriO naming and actor terminology across prose and contract identifiers; replaced step-dice and persistent actor posture with a per-turn d6 posture; simplified resolution to 2d6 plus peer votes against 7+; removed mechanical trackers, exhaustion, boons, and outcome bands. Narrative traits remain reusable grounding references. The interface contract remains a 1.0.0 draft pending approval. |
| 1.0.0 | Retained the engine mechanics and defined a transport-neutral multi-turn execution contract. Removed UI, hosting, authentication, deployment, persistence, and provider-selection requirements from the active scope. |

#### Deferred UI / Execution-Bridge Scope

The previous design included a static exploration dashboard/PWA, GitHub Pages hosting, GitHub Actions dispatch, client-side PAT storage, workflow passcodes, execution locks, spend ceilings, and file-based state/history/dossier persistence. These are deferred for a future UI and execution-bridge design. They are intentionally not requirements of this engine contract; the previous document revision remains available through Git history.

---

## 1. Overview & Objectives

The **TriO Matrix Engine (TOME)** is a turn-based simulation engine for exploring emergent realisations in complex multi-agent systems where fundamental behavioral dynamics are incomplete, uncertain, or emergent. It synthesizes the structured argumentation and mechanical probability resolution of **Chris Engle Matrix Games** with the behavioral divergence mechanics of **Cezar Capacle's Triple-O framework**.

**TOME** models multi-actor interactions, institutional friction, and strategic adaptations without relying on conversational consensus, fixed utility equations, or ungrounded claims. The engine accepts a complete world state and a bounded run request, then returns the final state and an auditable per-turn rationale:

$$\mathcal{M}(\text{WorldState}_{t}, \text{RunRequest}) \longrightarrow (\text{WorldState}_{t+n}, \text{TurnRecord}_{1..n})$$

### Goals

* **Deterministic Mechanical Core:** Each turn uses a d6 for posture (1-3 Obvious, 4-5 Option, 6 Odd), paired d66 spark-table lookups selected by that posture, and 2d6 plus peer votes against target number 7. A supplied seed fixes the engine-controlled random sequence for the same engine/runtime version.
* **Narrative-Only Trackers:** Actor conditions and capabilities are narrative facts and traits, not mechanical meters. There are no persistent posture levels, trait exhaustion, recovery, or automatic bonuses from trackers. Turn and round counters record simulation time only.
* **Strict Epistemic Grounding (The Linter Gate):** Proposal generators and peer reviewers cannot introduce ungrounded setting details or arbitrary voting shifts. Grounding checks enforce whitespace-stripped exact matching against existing `canon_facts` or intrinsic actor `traits`.
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

The engine-side integration supplies proposal-generation and peer-review implementations through the adapters in Section 3.5. Their provider, model, credentials, and retry policy are not part of the caller-facing contract. Mechanics, validation, turn ordering, state transitions, and result records remain governed by this specification.

### 2.1 Per-Turn d6 Posture

Every actor uses the same d6 to select a posture for its current turn:

| d6 Roll | Posture | Meaning |
| :---: | :--- | :--- |
| 1-3 | Obvious | A predictable initiative given the actor's narrative traits and agenda. |
| 4-5 | Option | A lateral but strategically logical initiative. |
| 6 | Odd | An atypical, radical, or unexpected initiative. |

Posture is a turn-local result, not a persistent actor tracker. It is recorded as `trio_tier` in the proposal for compatibility with the draft contract's terminology. Every turn rolls anew; prior successes, failures, and narrative conditions do not change the die or its thresholds.

### 2.2 Dual Spark Table Seeding

To force semantic divergence, the engine rolls two $d66$ checks against the bundled `trio-d66-v1` spark-table set (Action, Disposition, Motivation, Focus, Method). Its canonical 36-entry mappings are the engine's bundled template data in [src/tome/tables.py](../../src/tome/tables.py); a caller may supply a complete custom set in the run request. A release must not change the bundled data without incrementing the table-set version. The tier dictates the table pairings:

The bundled table content is derived from Cezar Capacle's TriO, licensed under CC BY-SA 4.0; see the repository license and README attribution.

* **The Obvious:** `Action` + `Focus`
* **The Option:** `Method` + `Focus`
* **The Odd:** `Disposition` + `Motivation`

An umpire may provide a complete custom `SparkTables` object in `RunRequest`; if omitted, the engine uses the bundled template set. Partial custom table overrides are invalid.

$d66$ notation is standard tabletop die-rolling: two six-sided dice are rolled where the first represents the tens digit and the second represents the units digit ($10 \times \text{die}_1 + \text{die}_2$), producing 36 discrete values from 11 through 66.

### 2.3 Engle Matrix Game Formulation

A proposal is a structured argument:
* **World-Change Statement:** A single declarative assertion specifying an altered fact in the world benefiting the active actor.
* **Supporting Arguments (Pros):** 1 to 2 arguments explicitly grounded in existing `canon_facts` or the actor's own `traits`.

### 2.4 Peer Review & The Cheeky Pivot

Every non-active actor evaluates the proposal as an independent adjudicator:
1. **Baseline Plausibility:** Rate proposal as $+1$ (Plausible), $0$ (Uncertain), or $-1$ (Implausible).
2. **Strategic Alignment:** Describe whether the outcome is `beneficial`, `neutral`, or `hostile` to the voter. This is narrative metadata, not an additional mechanical constraint on vote direction.
3. **The Cheeky Pivot (Biased Shift):** May shift the final vote by at most $\pm 1$ step from baseline. The resulting `final_vote` is clamped to $[-1, +1]$:
   * $+1 \to +1$ (unaltered beneficial)
   * $+1 \to 0$ (hostile shift down)
   * $0 \to -1$ (hostile shift down)
   * $-1 \to 0$ (beneficial shift up)
   * $0 \to +1$ (beneficial shift up)
   * An individual voter's `final_vote` is strictly bounded within $\{-1, 0, +1\}$.
4. **The Grounding Gate:** If a shift is attempted ($\text{shift} \neq 0$), the voter MUST cite a valid anchor from `canon_facts` or its own narrative `traits`. If the anchor is missing or invalid, the vote reverts to baseline. Facts and traits are reusable references: citing one does not consume, exhaust, or mechanically change it.

The numeric difference between final vote and baseline determines whether a shift was attempted; the adapter's `biased_shift_applied` flag does not authorize or prevent one. After validation, the engine sets that flag to whether a valid non-zero shift remains. Invalid shifts revert to baseline with the flag false and anchor null; unchanged votes also have the flag false and anchor null. Valid shifted votes retain the normalized anchor. `goal_alignment` remains descriptive for all three values.

### 2.5 Matrix Adjudication & State Mutation

$$\text{Net Modifier} = \max\left(-3, \min\left(3, \sum \text{final\_vote}\right)\right)$$

Resolution roll: $2d6 + \text{Net Modifier}$ against target number 7:

| $2d6 + \text{Mod}$ | Outcome | Narrative State Mutation |
| :---: | :--- | :--- |
| **7+** | **Success** | Append the proposal's world-change statement to `canon_facts` if not already present. |
| **Below 7** | **Failure** | The proposed change does not enter canon. Record the attempt and rationale without adding facts, rumors, complications, or counter-facts. |

There are no critical success/failure bands or secondary boons. Peer arguments inform the modifier and remain in the audit record; they do not automatically become facts. `active_rumors`, actor traits, and all other narrative state remain unchanged by resolution. Every resolved turn advances time regardless of success or failure.

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
        "required": ["id", "name", "agenda", "traits"],
        "properties": {
          "id": { "type": "string", "minLength": 1 },
          "name": { "type": "string" },
          "agenda": { "type": "string" },
          "traits": {
            "type": "array",
            "items": { "type": "string" }
          }
        }
      }
    }
  }
}
```

For every actor, `id` must be non-empty and unique in the world state. `traits` contains narrative descriptions, not consumable capabilities. Actors have no persistent `posture` or `exhausted_traits` fields. Legacy payloads containing removed fields must be adapted by the caller; undeclared fields reject the run as `InvalidRunRequestError`.

### 3.2 Proposal Contract (Stage 3)

```text
SupportingPro = {
  source_type: "actor_trait" | "canon_fact",
  source_ref: string,
  argument: string
}

Proposal = {
  active_actor_id: string,
  posture_die: "d6",
  posture_roll: integer in [1, 6],
  trio_tier: "Obvious" | "Option" | "Odd",
  spark_tags: string[] with exactly 2 tier-appropriate table tags,
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
  "spark_tags": ["Disposition:Distrustful", "Motivation:Obsession"],
  "world_change_statement": "The Iron Choir establishes a fortified scrap blockade across Conduit 4, redirecting geothermal power exclusively to their foundries.",
  "supporting_pros": [
    {
      "source_type": "actor_trait",
      "source_ref": "Sub-Surface Conduit Maps",
      "argument": "Their navigation charts permit precise bypass and isolation of auxiliary conduits."
    },
    {
      "source_type": "canon_fact",
      "source_ref": "The Iron Foundry in Sector 4 was destroyed.",
      "argument": "The regional power grid is already destabilized, creating an exploitable energy vacuum."
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
  "cited_anchor": "Harbor quarantine is active until winter.",
  "final_vote": 0,
  "public_argument": "While their conduit access is uncontested, the harbor quarantine restricts industrial distribution, meaning diverted geothermal power will quickly overheat local distribution coils."
}
```

### 3.4 Run Request, Result, and Turn Record (Interface Contract v1.0.0)

The caller supplies a full world state, a positive number of turns, and optionally the actor order for the first round and a random seed. If `first_round_order` is omitted, the engine creates a random permutation; when `seed` is supplied, that permutation is reproducible. The supplied order must contain every actor ID exactly once. The engine repeats that order until the requested number of turns has completed.

The interface types are:

```text
RunRequest = {
  contract_version: "1.0.0",
  world_state: WorldState,
  turn_count: integer where turn_count >= 1,
  first_round_order?: string[],
  seed?: integer where seed >= 0,
  spark_tables?: SparkTables
}

RunResult = {
  contract_version: "1.0.0",
  final_world_state: WorldState,
  spark_table_source: "trio-d66-v1" | "request",
  turn_records: TurnRecord[] where length == RunRequest.turn_count
}

SparkTables = {
  Action: Record<D66, non-empty string>,
  Focus: Record<D66, non-empty string>,
  Method: Record<D66, non-empty string>,
  Disposition: Record<D66, non-empty string>,
  Motivation: Record<D66, non-empty string>
}

D66 = exactly the 36 keys with tens and units digits from 1 through 6;
      JSON serializes each key as its decimal string

TurnRecord = {
  turn_index: integer >= 1,             // value after this turn's tick
  session_index: integer >= 0,          // completed-round count after this turn
  active_actor_id: string,
  proposal: Proposal,
  peer_evaluations: PeerEvaluation[],
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

RunError =
  InvalidRunRequestError |
  ProposalGenerationError |
  InvalidProposalError |
  PeerReviewError |
  MechanicsError

RunFailure = {
  contract_version: "1.0.0",
  code: "INVALID_RUN_REQUEST" | "PROPOSAL_GENERATION_FAILED" |
        "INVALID_PROPOSAL" | "PEER_REVIEW_FAILED" | "MECHANICS_FAILED",
  message: string
}
```

`turn_index` and `session_index` in a record are their values after the turn has resolved and the round boundary (if any) has been processed. `adjusted_total` is `resolution_roll + net_vote_modifier`.

The request's `first_round_order`, `seed`, and `spark_tables` are absent-or-value fields; `null` is invalid. If no seed is supplied, the engine initializes its run-local random generator from system entropy and the run is not reproducible.

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
        "agenda": "Control the conduit",
        "traits": ["Scrap mastery"]
      },
      {
        "id": "actor_dock_syndicate",
        "name": "Dock Syndicate",
        "agenda": "Protect trade",
        "traits": ["Harbor control"]
      }
    ]
  },
  "turn_count": 1,
  "first_round_order": ["actor_iron_choir", "actor_dock_syndicate"],
  "seed": 20
}
```

`first_round_order` and `seed` are optional. `turn_count` must be a positive integer and `seed`, when supplied, must be a non-negative integer. The run request does not include credentials, storage paths, transport metadata, or provider-specific configuration.
`spark_tables`, when supplied, must contain all five tables, each with exactly the 36 valid d66 keys and a non-empty string value for every key. Otherwise, `spark_table_source` in the result is `trio-d66-v1`; when supplied, it is `request`.

The successful result contains the complete final world state and exactly one ordered record for each completed turn:

```json
{
  "contract_version": "1.0.0",
  "spark_table_source": "trio-d66-v1",
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
        "agenda": "Control the conduit",
        "traits": ["Scrap mastery"]
      },
      {
        "id": "actor_dock_syndicate",
        "name": "Dock Syndicate",
        "agenda": "Protect trade",
        "traits": ["Harbor control"]
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
        "spark_tags": ["Disposition:Unpredictable", "Motivation:Obsession"],
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

Each `turn_record` preserves the proposal and its grounded pros, all peer evaluations after grounding validation, the clamped net vote modifier, resolution roll and adjusted total, success or failure, and the state changes applied by that turn. It is an audit record of why the final state changed; it is not a UI-formatted dossier.

`peer_evaluations` contains exactly one evaluation for each non-active actor, in the order those actors appear in the input `WorldState`. `state_changes` contains each changed top-level `WorldState` field exactly once, ordered by ascending JSON Pointer. Each entry's `before` and `after` are the complete JSON values of that field; `reason` describes every deterministic engine rule that affected it, in execution order. These values represent the net change at the end of the turn, including counter updates. A completed run contains exactly `turn_count` records, including failed attempts; errors use one of the `RunError` types and never include a partial result.

The proposal's `active_actor_id` must equal the actor taking the turn; its die is always `d6`, its roll is the engine's turn-local posture roll, and its tier and two spark tags must match that roll and selected tables. Each peer evaluation's voter ID must identify a distinct non-active actor. A caller-supplied state must contain every field in Section 3.1; actor IDs are non-empty and unique. All contract objects reject undeclared fields.

### 3.5 Engine-Side Proposal and Peer-Review Adapters

The runner invokes two engine-side adapters; these are not part of `RunRequest` and are not implemented by the UI:

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
```

The proposal generator returns only a `ProposalDraft`; the engine creates the complete `Proposal` by attaching the active actor ID, posture die and roll, tier, and spark tags already resolved for that turn. Each adapter must return the declared schema and must not mutate its arguments. The runner supplies isolated snapshots of the current state and proposal. Provider/network errors or malformed output become `ProposalGenerationError` or `PeerReviewError`. The engine applies grounding and voting validation to returned values. It prunes ungrounded proposal pros; if no grounded pro remains, it raises `InvalidProposalError` without automatically retrying. Any adapter retry policy is outside the engine contract. Engine errors expose the stable code and message represented by `RunFailure`; an execution bridge maps those values into its chosen transport response without returning partial state.

An empty or whitespace-only world-change statement is malformed proposal output and raises `ProposalGenerationError` before adjudication; it must never enter canon. Non-blank statements retain their original text.

---

## 4. Invariants & Rules

* **Invariant 1 (Run Turn Order):** The caller may supply `first_round_order`, which must be a permutation of all actor IDs. If omitted, the engine creates a random permutation; a supplied seed makes that order reproducible. This order remains fixed and repeats until the requested turns are complete. Every new `RunRequest` starts at the beginning of its own order; partial rounds are not resumed across requests.
* **Invariant 2 (Per-Turn Posture):** Every turn rolls one d6: 1-3 means Obvious, 4-5 means Option, and 6 means Odd. The selected posture is turn-local; no actor condition changes this mapping.
* **Invariant 3 (Cheeky Pivot Shift Limit & Bounds):** A peer evaluation shift $(\text{final\_vote} - \text{baseline\_plausibility})$ cannot exceed $\pm 1$. Any deviation $> 1$ or $< -1$ is invalid and reverts to baseline. Both `baseline_plausibility` and `final_vote` are strictly constrained to $\{-1, 0, +1\}$.
* **Invariant 4 (Grounding Gate Validity):** Any non-zero vote shift $(\text{shift} \neq 0)$ requires `cited_anchor` (after stripping whitespace and enclosing quotation marks) to match exactly an existing string in `canon_facts` or the voter actor's `traits`. If ungrounded, the shift is discarded and `final_vote` reverts to `baseline_plausibility`. Valid anchors remain reusable across turns.
* **Invariant 5 (Proposal Pro Grounding Gate):** Each entry in `supporting_pros` must validate its `source_ref` against the declared `source_type`: if `canon_fact`, it must match a known canon fact; if `actor_trait`, it must match one of the active actor's own traits. Ungrounded pros are pruned. The proposal proceeds only if at least 1 grounded pro remains; otherwise, the run fails with `InvalidProposalError` and the engine does not regenerate the proposal.
* **Invariant 6 (Narrative-Only Trackers):** Traits, rumors, and actor conditions carry narrative information only. They are not consumed, recovered, stepped, or used as automatic numeric modifiers. Grounded peer votes are the only adjustment to the resolution roll.
* **Invariant 7 (Binary Resolution):** An adjusted total of 7 or more is Success; a lower total is Failure. Success appends the world-change statement to canon only if absent. Failure introduces no narrative changes. Neither outcome adds rumors or peer arguments to canon automatically.
* **Invariant 8 (Net Modifier Clamping):** The sum of final peer votes is clamped to $[-3, +3]$ inclusive before rolling $2d6$.
* **Invariant 9 (Time Always Advances):** Success and Failure both resolve the turn and advance its time counter. A failed attempt is not an engine error and remains in `turn_records`.
* **Invariant 10 (Deterministic Core Isolation):** No network socket, external process, or non-deterministic clock affects mechanical calculations. One Python `random.Random` instance is created per run, seeded from `seed` or system entropy. With a seed and identical adapter outputs, rolls and randomized initial order are reproducible for the same engine/runtime version. Proposal and peer-review adapters do not consume the engine's random stream.
* **Invariant 11 (State and Result Atomicity):** The submitted `WorldState` is never mutated. The engine returns a final state and exactly `turn_count` records only after all requested turns complete; on any failure it raises an explicit error and returns no partial state.
* **Invariant 12 (Time and Round Counters):** `turn_index` increments once after each resolved turn. Within a request, `session_index` increments once after every complete pass through that request's order; it does not increment for an incomplete final pass. A new request starts a new order rather than resuming an incomplete pass. There are no round-end tracker resets.
* **Invariant 13 (Unique Actor Identity):** Actor IDs must be unique and non-empty so that each run order identifies exactly one actor per turn.
* **Invariant 14 (Seeded Draw Order):** If `first_round_order` is omitted, `random.Random.shuffle` consumes the run's first random draws. Every die face is drawn with `rng.randint(1, 6)`. For each turn, draw one posture d6, two d66 rolls (tens then units for each), and two resolution d6, in that order. Convert each d66 to tens-times-ten plus units. The Odd posture uses `Disposition` + `Motivation`. Custom tables change labels only, not draw order.
  * **Golden Vector (Python 3.11):** With seed `42`, actor IDs `["actor_a", "actor_b"]`, and no supplied order, shuffle produces `["actor_b", "actor_a"]`. The first posture roll is `1`, spark d66 rolls are `63` and `22`, and resolution dice are `2` and `6` (base total `8`).
* **Invariant 15 (Explicit Failure Types):** Invalid requests raise `InvalidRunRequestError`; proposal generation, invalid proposals, peer review, and mechanics failures raise their corresponding `RunError` type. No engine-level retry or partial result is permitted.

---

## 5. Execution & State Mutation Logic

### Inputs & Triggers

The engine accepts a `RunRequest` as defined in Section 3.4: a complete `WorldState`, positive `turn_count`, and optional `first_round_order`, `seed`, and `spark_tables`. No passcode, transport token, file path, storage location, or deployment trigger is an engine input.

### Turn Execution

1. Validate the complete world state, unique actor IDs, positive `turn_count`, optional order permutation, and optional complete `spark_tables` payload before executing any turn. A run requires at least one actor.
2. Select custom `spark_tables` from the request, or the bundled template table set when omitted. Create one `random.Random` instance from the non-negative `seed`, or system entropy when omitted. Select the first-round order from the supplied permutation, or shuffle the actor IDs with that instance.
3. Execute exactly `turn_count` turns, advancing through the order and restarting at its first actor after each complete pass:
   a. Roll one posture d6, map it to Obvious/Option/Odd, and draw the paired d66 spark tags for that posture.
   b. Generate a `ProposalDraft` through the engine-side proposal-generation integration; the engine attaches the already-resolved active actor ID, posture die/roll, tier, and spark tags to form the `Proposal`.
   c. Validate and prune proposal pros against canon facts and active-actor traits; if none remain, fail with `InvalidProposalError`.
   d. Obtain one peer evaluation from every non-active actor, then apply shift and grounding validation without consuming any trait or fact.
   e. Clamp the sum of final votes to $[-3, +3]$, roll 2d6, and add the modifier.
   f. If the adjusted total is at least 7, record Success and append the proposal statement to canon if absent. Otherwise record Failure and leave narrative state unchanged. Do not generate automatic rumors, complications, boons, or counter-facts.
   g. Increment `turn_index`. If every actor in the fixed run order has acted, increment `session_index`. Record the proposal, evaluations, roll, modifier, Success/Failure, and end-of-turn state delta in a `TurnRecord`.
4. Return `RunResult` with the final state and ordered records. If the requested count ends partway through a round, return that partial round's state and records without incrementing `session_index`. A later request starts a fresh order and does not resume that round.

The engine works on an isolated copy of the input state. It publishes no partial result: if validation, proposal generation, peer review, or mechanics fail, it raises an explicit error and the caller retains its original state unchanged.

### Outputs & Events

The successful output is the versioned `RunResult` in Section 3.4. The engine does not write files, append history, create a dossier, or emit transport-specific progress events. A caller may persist the returned state and turn records as it chooses.

---

## 6. Edge Cases & Failure Modes

* **Edge Case 1: Repeated Trait Citations:** The same fact or voter trait may ground multiple turns. Citations neither consume references nor create tracker state.
* **Edge Case 2: Hallucinated Anchor Strings:** Peer reviews might include leading/trailing whitespace or enclosing quotes. The linter gate strips outer whitespace and one matching enclosing quote pair before checking exact membership. If not found in `canon_facts` or voter `traits`, the shift is reverted.
* **Edge Case 3: One Actor:** A one-actor run is valid; it has no peer evaluations, so the net modifier is $0$. The one-actor order completes a round on every turn.
* **Edge Case 4: Resolution Boundaries:** Total 6 fails; total 7 succeeds. Higher and lower totals have no additional effects. An already-present statement is not duplicated on success. A failed roll still produces a turn record and advances time.
* **Edge Case 5: Invalid Run Request:** A non-positive `turn_count`, negative seed, empty actor set, duplicate/empty actor ID, undeclared tracker field, or `first_round_order` that is not an exact permutation is rejected with `InvalidRunRequestError` before execution. The caller's input state remains untouched.
* **Edge Case 6: Proposal or Peer-Review Failure:** Any engine-side proposal or peer-review integration failure, including malformed output, aborts with `ProposalGenerationError` or `PeerReviewError`. The engine does not retry. No partial state or turn records are returned.
* **Edge Case 7: Proposal Without Grounded Pros:** Ungrounded pros are pruned. If none remain, the run aborts with `InvalidProposalError`; the engine does not request regeneration.
* **Edge Case 8: Run Ends Mid-Round:** The engine returns all resolved turn records and the corresponding partial-round state. `turn_index` reflects every resolved turn; `session_index` advances only for complete passes within this request. A subsequent request starts a new order rather than continuing the previous one.
* **Edge Case 9: Invalid Spark Tables:** A custom table payload missing a table, containing an extra or missing d66 key, or containing an empty value is rejected with `InvalidRunRequestError` before execution.

---

## 7. Verification & Automated Test Strategy

### Unit Tests (`tests/test_tome_core.py`)

* **Posture d6 Mapping:** Exhaustively assert faces 1-3 map to Obvious, 4-5 to Option, and 6 to Odd; every actor uses the same mapping. Verify the three postures select the specified table pairs.
* **Seeded Random Sequence:** Assert golden draw vectors for seeded order shuffling, posture d6, both d66 lookups, and resolution dice; verify every face uses `randint(1, 6)` in the specified order.
* **Spark Table Payload:** Assert omitted tables select `trio-d66-v1`; reject partial, extra-key, missing-key, or empty-value custom tables; verify valid custom table values produce matching spark tags.
* **Linter Gate Shift Bounds:** Assert shifts of $\pm 2$ are rejected and reverted to baseline. Assert `final_vote` values strictly stay within $\{-1, 0, +1\}$.
* **Grounding Gate Verification:** Assert valid canon facts and valid voter traits allow shifts; nonexistent strings cause reversion to baseline. Assert the same valid reference can be reused on later turns without mutation.
* **Proposal and Evaluation Schemas:** Assert adapter output validation, engine attachment of turn mechanics to `ProposalDraft`, and one ordered peer evaluation per non-active actor.
* **Voting Metadata:** Assert alignment is descriptive and normalized shift flags/anchors follow the numeric shift and grounding checks, including inconsistent adapter flags.
* **Closed State Schema:** Assert unknown fields are rejected at both world-state and actor-object levels.
* **Non-Blank Proposals:** Reject empty and whitespace-only statements before any resolution roll or canon insertion.
* **Net Modifier Clamping:** Assert extreme positive and negative vote sums clamp strictly at $[-3, +3]$.
* **Binary Resolution:** Assert adjusted totals 6 and 7 resolve to Failure and Success respectively; all totals below 7 behave alike and all totals at least 7 behave alike. Only successful proposals enter canon, without duplicates. Failures still advance time and emit records.
* **Narrative State Preservation:** Assert resolution never automatically changes rumors, actors, or traits; no posture, exhaustion, recovery, boon, complication, or counter-fact is created.
* **State-Change Records:** Assert each changed top-level field appears once, sorted by ascending JSON Pointer, with before/after values and deterministic reason text.
* **Removed Tracker Fields:** Reject legacy persistent posture and exhaustion fields as undeclared fields.

### Integration Tests

* End-to-end run tests for exact turn counts, order cycling, seeded initial order, per-turn records, time counters, partial-round behavior, and final state.
* Assert the input `WorldState` remains unchanged after both successful and failed runs, and that failures expose no partial result.

---

## 8. Goldfish Review Gates

The [Goldfish review report](../reviews/001_tome_core_architecture_review.md) records the historical 1.0.0 approval and the 1.1.0 review findings. The current draft addresses those findings, but independent confirmation and human approval remain pending.

- [x] Zero-context Goldfish review completed for Spec Version 1.1.0
- [ ] Goldfish confirmation of corrected contract gaps for Spec Version 1.1.0
- [ ] Human developer approval signed off
