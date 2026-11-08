# Design Specification: Triple-O Matrix Engine (TOME) Core Architecture

**Document ID:** `docs/designs/001_tome_core_architecture.md`  
**Status:** Approved  
**Author:** Elephant Agent & Developer  
**Target Milestone:** v0.1.0 (Core Engine & Pure-Python Mechanics)  

---

## 1. Overview & Objectives

The **Triple-O Matrix Engine (TOME)** is a stateless, turn-based faction simulation engine for tabletop roleplaying campaigns. It synthesizes the structured argumentation and mechanical probability resolution of **Chris Engle Matrix Games** with the behavioral divergence mechanics of **Cezar Capacle's Triple-O framework**.

TOME models faction actions during campaign downtime without relying on conversational consensus or unconstrained LLM hallucinations. The engine operates as a pure state transformer:

$$f(\text{WorldState}_{t}, \text{InputParameters}) \longrightarrow \text{WorldState}_{t+1} + \text{DowntimeDossier}_{\text{Tier 2}}$$

### Goals

* **Deterministic Mechanical Core:** Dice mechanics (posture step-dice $1d4, 1d6, 1d8$; resolution $2d6$), spark table lookups ($d66$), posture transitions, immutable order-of-operations sorting, and validation gates execute purely in deterministic Python with zero network calls.
* **Strict Epistemic Grounding (The Linter Gate):** Subagent peer reviewers and proposal authors cannot invent setting details or apply arbitrary voting shifts. Grounding checks enforce whitespace-stripped exact matching against existing `canon_facts` or intrinsic faction `traits`.
* **Zero Recurring Infrastructure Cost:** Standalone repository designed for serverless execution via GitHub Actions with a static PWA client hosted on GitHub Pages.
* **Cost & Security Containment:** Workflow passcode fail-gate, Personal Access Token (PAT) client storage, execution concurrency locks, and hard budget spend ceilings.
* **Frontier LLM Binding:** Google Gemini (`google-genai` / Gemini Flash) constrained by Pydantic JSON schemas for semantic proposal formulation and peer adjudication.

### Non-Goals

* Real-time multiplayer synchronization or persistent backend server daemon (the engine runs purely on-demand via serverless GitHub Actions dispatch).
* Open-ended conversational chat simulation between factions (all interactions are strictly structured into Proposal and Adjudication phases).
* Direct in-engine hosting of the full campaign vault markdown corpus (TOME operates as a standalone engine that ingests and emits standardized JSON state and markdown downtime dossiers).

---

## 2. Domain Framing & User/System Experience

### 2.1 Posture Step-Die & The Triple-O Split

A faction's internal structural integrity is represented by its **Posture** (`Stable`, `Pressured`, or `Cornered`). The posture determines the die type rolled when selecting a course of action. The result maps to fixed target bands across all die types:

| Posture | Die Size | 1–3: The Obvious | 4–5: The Option | 6+: The Odd |
| :--- | :---: | :---: | :---: | :---: |
| **Stable** | $1d4$ | $75.0\%$ | $25.0\%$ | $0.0\%$ |
| **Pressured** | $1d6$ | $50.0\%$ | $33.3\%$ | $16.7\%$ |
| **Cornered** | $1d8$ | $37.5\%$ | $25.0\%$ | $37.5\%$ |

* **The Obvious (1–3):** The most predictable shift given the faction's established traits and agenda.
* **The Option (4–5):** A lateral, less predictable shift that remains strategically logical.
* **The Odd (6+):** An atypical, radical, or volatile initiative. Factions in a `Stable` posture cannot roll an Odd action.

### 2.2 Dual Spark Table Seeding

To force semantic divergence and prevent LLM mode-collapse, the engine deterministically rolls two $d66$ checks against Capacle's Triple-O Spark Tables (Action, Disposition, Motivation, Focus, Method). The tier dictates the table pairings:

* **The Obvious:** `Action` + `Focus`
* **The Option:** `Method` + `Focus`
* **The Odd:** `Disposition` + `Motivation` (or `Method` + `Motivation`)

$d66$ notation is standard tabletop die-rolling: two six-sided dice are rolled where the first represents the tens digit and the second represents the units digit ($10 \times \text{die}_1 + \text{die}_2$), producing 36 discrete values from 11 through 66.

### 2.3 Engle Matrix Game Formulation

A proposal is a structured argument:
* **World-Change Statement:** A single declarative assertion specifying an altered fact in the world benefiting the active faction.
* **Supporting Arguments (Pros):** 1 to 2 arguments explicitly grounded in existing `canon_facts` or the actor's own `traits`.

### 2.4 Subagent Peer Review & The Cheeky Pivot

Every non-active faction evaluates the proposal as an independent adjudicator:
1. **Baseline Plausibility:** Rate proposal as $+1$ (Plausible), $0$ (Uncertain), or $-1$ (Implausible).
2. **Strategic Alignment:** Determine if the outcome is `beneficial`, `neutral`, or `hostile` to the voter.
3. **The Cheeky Pivot (Biased Shift):** May shift the final vote by at most $\pm 1$ step from baseline. The resulting `final_vote` is clamped to $[-1, +1]$:
   * $+1 \to +1$ (unaltered beneficial)
   * $+1 \to 0$ (hostile shift down)
   * $0 \to -1$ (hostile shift down)
   * $-1 \to 0$ (beneficial shift up)
   * $0 \to +1$ (beneficial shift up)
   * An individual voter's `final_vote` is strictly bounded within $\{-1, 0, +1\}$.
4. **The Grounding Gate:** If a shift is attempted ($\text{shift} \neq 0$), the voter MUST cite a valid anchor from `canon_facts` or an unexhausted voter `trait`. If the anchor is missing, invalid, or exhausted, the vote reverts to baseline. Citing a trait flags it as exhausted for the remainder of the cycle.

### 2.5 Matrix Adjudication & State Mutation

$$\text{Net Modifier} = \max\left(-3, \min\left(3, \sum \text{final\_vote}\right)\right)$$

Resolution roll: $2d6 + \text{Net Modifier}$ against target number 7:

| $2d6 + \text{Mod}$ | Outcome Band | World State Mutation | Posture Mutation |
| :---: | :--- | :--- | :--- |
| **$10+$** | **Ratified Reality** | Proposal locks into `canon_facts`. Highest $+1$ voter gains a secondary boon (recovers 1 exhausted trait, or improves posture by 1 step if no traits were exhausted). | Active faction improves 1 step ($d8 \to d6 \to d4$). |
| **$7\text{–}9$** | **Fractured Reality** | Proposal locks into `canon_facts`; the sharpest Con argument manifests as an active complication hook (`[COMPLICATION] <arg>`) appended to `active_rumors`. | No posture change. |
| **$4\text{–}6$** | **Contested Friction** | Proposal fails to manifest. Both the proposal and opposing Cons convert to active session rumors in `active_rumors`. | No posture change. |
| **$\le 3$** | **Counter-Reality** | Proposal fails completely. The most severe $-1$ Con argument crystallizes into a new `canon_fact`. | Active faction degrades 1 step ($d4 \to d6 \to d8$). |

---

## 3. State Schema & Data Models

### 3.1 World State (`world_state.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "WorldState",
  "type": "object",
  "required": ["session_index", "canon_facts", "active_rumors", "factions"],
  "properties": {
    "session_index": { "type": "integer", "minimum": 0 },
    "canon_facts": {
      "type": "array",
      "items": { "type": "string" }
    },
    "active_rumors": {
      "type": "array",
      "items": { "type": "string" }
    },
    "factions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "agenda", "posture", "traits", "exhausted_traits"],
        "properties": {
          "id": { "type": "string" },
          "name": { "type": "string" },
          "agenda": { "type": "string" },
          "posture": { "type": "string", "enum": ["Stable", "Pressured", "Cornered"] },
          "traits": {
            "type": "array",
            "items": { "type": "string" }
          },
          "exhausted_traits": {
            "type": "array",
            "items": { "type": "string" }
          }
        }
      }
    }
  }
}
```

### 3.2 Proposal Contract (Stage 3)

```json
{
  "active_faction_id": "fac_iron_choir",
  "posture_die": "d8",
  "posture_roll": 7,
  "triple_o_tier": "Odd",
  "spark_tags": ["Disposition:Distrustful", "Motivation:Obsession"],
  "world_change_statement": "The Iron Choir establishes a fortified scrap blockade across Conduit 4, redirecting geothermal power exclusively to their foundries.",
  "supporting_pros": [
    {
      "source_type": "faction_trait",
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

```json
{
  "voter_faction_id": "fac_dock_syndicate",
  "baseline_plausibility": 1,
  "goal_alignment": "hostile",
  "biased_shift_applied": true,
  "cited_anchor": "Harbor quarantine is active until winter.",
  "final_vote": 0,
  "public_argument": "While their conduit access is uncontested, the harbor quarantine restricts industrial distribution, meaning diverted geothermal power will quickly overheat local distribution coils."
}
```

---

## 4. Invariants & Rules

* **Invariant 1 (Immutable Turn Sequence):** At cycle start (Step 1), faction turn order is computed once as an immutable sequence sorted by initial urgency: `Cornered` ($1d8$) $\to$ `Pressured` ($1d6$) $\to$ `Stable` ($1d4$), with ties broken alphabetically by `id`. Mid-cycle posture changes take effect for subsequent cycles, not the active sequence.
* **Invariant 2 (Posture Tier Bounds):** Factions in a `Stable` posture ($1d4$) can never roll a $6+$ and therefore can never execute an `Odd` action.
* **Invariant 3 (Cheeky Pivot Shift Limit & Bounds):** A peer evaluation shift $(\text{final\_vote} - \text{baseline\_plausibility})$ cannot exceed $\pm 1$. Any deviation $> 1$ or $< -1$ is invalid and reverts to baseline. Both `baseline_plausibility` and `final_vote` are strictly constrained to $\{-1, 0, +1\}$.
* **Invariant 4 (Grounding Gate Validity):** Any non-zero vote shift $(\text{shift} \neq 0)$ requires `cited_anchor` (after stripping whitespace and enclosing quotation marks) to match exactly an existing string in `canon_facts` OR an unexhausted string in the voter faction's `traits`. If ungrounded or exhausted, the shift is discarded and `final_vote` reverts to `baseline_plausibility`.
* **Invariant 5 (Proposal Pro Grounding Gate):** Each entry in `supporting_pros` must validate its `source_ref` against the declared `source_type`: if `canon_fact`, it must match a known canon fact; if `faction_trait`, it must match one of the active faction's own traits. If any pro is ungrounded, the pro is pruned. The proposal proceeds as long as at least 1 grounded pro remains; otherwise, the proposal prompt is regenerated or execution fails safely.
* **Invariant 6 (Tag Exhaustion Scope):** When a voter cites its own trait to validate a shifted vote, that trait is added to `exhausted_traits` for that voter and cannot be cited again during the same simulation cycle. At the end of the full simulation cycle, all `exhausted_traits` are cleared.
* **Invariant 7 (Deterministic Con & Boon Selection):**
  * **Sharpest Con Selection ($7\text{–}9$ and $\le 3$):** Among peer evaluations with $\text{final\_vote} < 0$, select the evaluation with lowest `final_vote`, then lowest `baseline_plausibility`, breaking ties by `voter_faction_id` ascending alphabetical order.
  * **Highest Boon Voter Selection ($10+$):** Among peer evaluations with $\text{final\_vote} > 0$, select the evaluation with highest `final_vote`, then highest `baseline_plausibility`, breaking ties by `voter_faction_id` ascending alphabetical order.
  * **Secondary Boon Mutation:** The selected boon voter immediately recovers 1 trait from `exhausted_traits` (if any are exhausted); if none are exhausted, the voter's posture improves by 1 step (clamped at `Stable`).
* **Invariant 8 (Net Modifier Clamping):** The sum of final peer votes is clamped strictly between $[-3, +3]$ inclusive before rolling $2d6$.
* **Invariant 9 (Posture Step Transitions):**
  * Improvement step: `Cornered` $\to$ `Pressured` $\to$ `Stable` (clamped at `Stable`).
  * Degradation step: `Stable` $\to$ `Pressured` $\to$ `Cornered` (clamped at `Cornered`).
* **Invariant 10 (Deterministic Core Isolation):** No network socket, external process, or non-deterministic clock affects core mechanical roll calculations. Random seeds can be injected for reproducible testing.

---

## 5. Execution & State Mutation Logic

### Inputs & Triggers

* `world_state.json`: Current simulation ledger.
* `seed`: Optional random seed for reproducible dice rolls and table selections.
* `passcode`: Security validation parameter matching `TOME_EXECUTION_PASSPHRASE`.

### State Mutation Logic

1. **Sort Factions (Immutable Order):** Order factions once at cycle start by initial `posture` urgency (`Cornered` $\to$ `Pressured` $\to$ `Stable`), breaking ties by `id` ascending.
2. **For each faction in turn:**
   a. Look up posture die ($1d4, 1d6, 1d8$) and roll posture die.
   b. Determine Triple-O tier:
      * $1\le \text{roll} \le 3 \implies$ `Obvious`
      * $4\le \text{roll} \le 5 \implies$ `Option`
      * $\text{roll} \ge 6 \implies$ `Odd`
   c. Roll $2\times d66$ on corresponding paired spark tables.
   d. Dispatch proposal generation prompt to LLM (or mock generator in unit tests).
   e. Run Proposal Grounding Gate: verify `supporting_pros` against `canon_facts` and active faction `traits`.
   f. Dispatch peer review prompts to all non-active factions.
   g. Run Linter Gate on each peer evaluation: verify single-step shift and cited anchor presence. Revert ungrounded shifts; record exhausted traits.
   h. Compute $\text{Net Modifier} = \text{clamp}(\sum \text{final\_vote}, -3, 3)$.
   i. Roll $2d6 + \text{Net Modifier}$:
      * $\ge 10$ (Ratified Reality): Proposal added to `canon_facts`; active faction improves posture. Highest $+1$ voter gains secondary boon (recovers 1 exhausted trait, or improves posture 1 step).
      * $7\text{–}9$ (Fractured Reality): Proposal added to `canon_facts`; sharpest Con argument is formatted as `[COMPLICATION] <argument>` and added to `active_rumors`.
      * $4\text{–}6$ (Contested Friction): Proposal and all opposing Con arguments are added to `active_rumors`.
      * $\le 3$ (Counter-Reality): Proposal fails; sharpest Con argument added to `canon_facts`; active faction degrades posture.
3. **End of Cycle:**
   a. Clear all `exhausted_traits` for all factions.
   b. Increment `session_index`.
   c. Atomically serialize updated `world_state.json`, append resolved turn ledger to `history.jsonl`, and compile markdown dossier to `_sessions/_downtime/cycle_XX.md`.

---

## 6. Edge Cases & Failure Modes

* **Edge Case 1: Active Faction Trait Exhaustion:** An active faction cannot exhaust its traits during its own proposal, as pro arguments are claims of capability, not biased review shifts. Only non-active voters exhaust traits when biasing votes.
* **Edge Case 2: Hallucinated Anchor Strings:** LLM peer reviews might include leading/trailing whitespace or enclosing quotes. The linter gate normalizes strings (`anchor.strip().strip('"\'')`) before checking exact membership. If not found in `canon_facts` or unexhausted `traits`, the shift is reverted.
* **Edge Case 3: Zero or One Peer Faction:** If the simulation has fewer than 2 factions total, peer adjudication defaults to Net Modifier $0$.
* **Edge Case 4: No Positive Voters on 10+ or No Negative Voters on 7–9 / $\le 3$:**
  * If outcome is $10+$ but no voter cast $\text{final\_vote} > 0$, no secondary boon is granted.
  * If outcome is $7\text{–}9$ or $\le 3$ but no voter cast $\text{final\_vote} < 0$, no complication or counter-reality fact is generated; the outcome resolves purely on the proposal.
* **Edge Case 5: Provider Failure / Atomic Abort:** If the LLM provider call fails, times out, or emits malformed JSON after 2 retry attempts, the engine raises `EngineExecutionError` and halts with non-zero exit code. `world_state.json` is untouched, guaranteeing atomic failure semantics and zero partial state corruption.

---

## 7. Verification & Automated Test Strategy

### Unit Tests (`tests/test_tome_core.py`)

* **Posture Step-Die Distribution:** Verify $1d4$ never produces $\ge 5$, $1d6$ never produces $\ge 7$, and outcome distributions match Capacle target bands over 10,000 seeded rolls.
* **Linter Gate Shift Bounds:** Assert shifts of $\pm 2$ are rejected and reverted to baseline. Assert `final_vote` values strictly stay within $\{-1, 0, +1\}$.
* **Grounding Gate Verification:** Assert valid canon facts and valid voter traits allow shifts; assert nonexistent strings or already exhausted traits cause immediate reversion to baseline.
* **Tag Exhaustion Tracking:** Assert consumed traits are added to `exhausted_traits` and reset at cycle conclusion.
* **Deterministic Con/Boon Tie-Breaking:** Assert multiple voters with equal $-1$ or $+1$ votes are selected deterministically by vote, baseline plausibility, and faction ID.
* **Net Modifier Clamping:** Assert extreme positive and negative vote sums clamp strictly at $[-3, +3]$.
* **Outcome Band State Mutations:** Assert all 4 resolution bands ($10+, 7\text{–}9, 4\text{–}6, \le 3$) execute exact state mutations, complications in rumors, and posture transitions.

### Integration Tests

* End-to-end full simulation cycle test with deterministic mock provider verifying complete $f(\text{WorldState}_{t}) \to \text{WorldState}_{t+1}$ transitions and markdown dossier compilation.

---

## 8. Goldfish Review Gates

- [x] Zero-context Goldfish review completed
- [x] Logic contradictions and edge-case holes addressed
- [x] Human developer approval signed off
