"""Main orchestration loop and state transformer for TOME."""

from collections.abc import Callable

from tome.dice import PostureTier, resolve_posture_tier, roll_d66, roll_dice
from tome.models import Faction, PeerEvaluation, Posture, Proposal, WorldState
from tome.tables import TABLE_ACTION, TABLE_DISPOSITION, TABLE_FOCUS, TABLE_METHOD, TABLE_MOTIVATION
from tome.validator import (
    apply_adjudication_outcome,
    validate_and_prune_proposal,
    validate_and_sanitize_evaluation,
)

ProposalGenerator = Callable[[Faction, PostureTier, list[str], WorldState], Proposal]
PeerReviewer = Callable[[Faction, Proposal, WorldState], PeerEvaluation]


def get_paired_spark_tags(tier: PostureTier, seed: int | None = None) -> list[str]:
    """Roll 2x d66 on paired tables corresponding to Triple-O tier."""
    r1 = roll_d66(seed)
    r2 = roll_d66(seed + 1 if seed is not None else None)

    if tier == PostureTier.OBVIOUS:
        return [f"Action:{TABLE_ACTION[r1]}", f"Focus:{TABLE_FOCUS[r2]}"]
    elif tier == PostureTier.OPTION:
        return [f"Method:{TABLE_METHOD[r1]}", f"Focus:{TABLE_FOCUS[r2]}"]
    else:  # ODD
        return [f"Disposition:{TABLE_DISPOSITION[r1]}", f"Motivation:{TABLE_MOTIVATION[r2]}"]


def sort_factions_by_urgency(factions: list[Faction]) -> list[Faction]:
    """
    Sort factions once at cycle start: Cornered (d8) -> Pressured (d6) -> Stable (d4).
    Ties broken alphabetically by faction id.
    """
    posture_weight = {
        Posture.CORNERED: 0,
        Posture.PRESSURED: 1,
        Posture.STABLE: 2,
    }
    return sorted(factions, key=lambda f: (posture_weight.get(f.posture, 3), f.id))


def run_simulation_cycle(
    state: WorldState,
    proposal_fn: ProposalGenerator,
    peer_review_fn: PeerReviewer,
    seed: int | None = None,
) -> tuple[WorldState, list[Proposal], list[list[PeerEvaluation]]]:
    """
    Execute a single simulation cycle across all system actors/factions.
    Pure state transformer: M(WorldState_t, Interventions) -> WorldState_{t+1}
    """
    # 1. Immutable Turn Order Snapshot
    turn_order = sort_factions_by_urgency(state.factions)

    all_proposals: list[Proposal] = []
    all_evaluations: list[list[PeerEvaluation]] = []

    # 2. Sequential Loop
    for active_fac in turn_order:
        current_fac = state.get_faction(active_fac.id)
        if not current_fac:
            continue

        # a. Roll posture die & tier
        roll, tier = resolve_posture_tier(current_fac.posture, seed=seed)
        spark_tags = get_paired_spark_tags(tier, seed=seed)

        # b. Generate proposal
        raw_proposal = proposal_fn(current_fac, tier, spark_tags, state)
        raw_proposal.posture_roll = roll
        raw_proposal.triple_o_tier = tier.value
        raw_proposal.spark_tags = spark_tags

        # c. Validate & prune proposal
        proposal = validate_and_prune_proposal(raw_proposal, state.canon_facts, current_fac.traits)
        all_proposals.append(proposal)

        # d. Peer Review from all non-active factions
        evaluations: list[PeerEvaluation] = []
        for voter_fac in state.factions:
            if voter_fac.id == current_fac.id:
                continue

            raw_eval = peer_review_fn(voter_fac, proposal, state)
            sanitized_eval, trait_consumed = validate_and_sanitize_evaluation(
                raw_eval,
                canon_facts=state.canon_facts,
                voter_traits=voter_fac.traits,
                exhausted_traits=set(voter_fac.exhausted_traits),
            )
            if trait_consumed:
                voter_fac.exhausted_traits.append(trait_consumed)
            evaluations.append(sanitized_eval)

        all_evaluations.append(evaluations)

        # e. Adjudication & Roll (2d6 + Net Modifier)
        raw_modifier = sum(e.final_vote for e in evaluations)
        net_modifier = max(-3, min(3, raw_modifier))
        resolution_roll = roll_dice(6, count=2, seed=seed)
        total_roll = resolution_roll + net_modifier

        apply_adjudication_outcome(state, proposal, evaluations, total_roll=total_roll)

    # 3. End of Cycle State Commitments
    for f in state.factions:
        f.exhausted_traits.clear()
    state.session_index += 1

    return state, all_proposals, all_evaluations
