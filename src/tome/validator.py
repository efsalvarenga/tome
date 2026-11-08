"""Linter Gate, Epistemic Grounding, and Matrix Adjudication for TOME."""

from tome.models import PeerEvaluation, Proposal, WorldState


def sanitize_anchor_string(anchor: str | None) -> str | None:
    """Strip leading/trailing whitespace and enclosing quotes from an anchor."""
    if not anchor:
        return None
    cleaned = anchor.strip()
    if (cleaned.startswith('"') and cleaned.endswith('"')) or (
        cleaned.startswith("'") and cleaned.endswith("'")
    ):
        cleaned = cleaned[1:-1].strip()
    return cleaned


def validate_and_sanitize_evaluation(
    eval_payload: PeerEvaluation,
    canon_facts: list[str],
    voter_traits: list[str],
    exhausted_traits: set[str],
) -> tuple[PeerEvaluation, str | None]:
    """
    Validates evaluation against Motivated Reasoning contracts.
    Reverts invalid shifts to baseline. Returns (sanitized_eval, trait_to_exhaust).
    """
    shift = eval_payload.final_vote - eval_payload.baseline_plausibility
    trait_consumed = None

    # Invariant 3: Shift must not exceed 1 step (+/- 1)
    if abs(shift) > 1:
        eval_payload.final_vote = eval_payload.baseline_plausibility
        eval_payload.biased_shift_applied = False
        eval_payload.cited_anchor = None
        return eval_payload, None

    # Invariant 4: Grounding Gate for shifted votes
    if shift != 0:
        cleaned_anchor = sanitize_anchor_string(eval_payload.cited_anchor)
        if not cleaned_anchor:
            eval_payload.final_vote = eval_payload.baseline_plausibility
            eval_payload.biased_shift_applied = False
            eval_payload.cited_anchor = None
            return eval_payload, None

        canon_cleaned = {sanitize_anchor_string(f) for f in canon_facts}
        traits_cleaned = {sanitize_anchor_string(t) for t in voter_traits}
        exhausted_cleaned = {sanitize_anchor_string(e) for e in exhausted_traits}

        is_fact = cleaned_anchor in canon_cleaned
        is_trait = cleaned_anchor in traits_cleaned and cleaned_anchor not in exhausted_cleaned

        if not (is_fact or is_trait):
            # Grounding failed: anchor is hallucinated, invalid, or exhausted
            eval_payload.final_vote = eval_payload.baseline_plausibility
            eval_payload.biased_shift_applied = False
            eval_payload.cited_anchor = None
            return eval_payload, None

        eval_payload.cited_anchor = cleaned_anchor
        if is_trait:
            trait_consumed = cleaned_anchor

    return eval_payload, trait_consumed


def validate_and_prune_proposal(
    proposal: Proposal, canon_facts: list[str], active_faction_traits: list[str]
) -> Proposal:
    """Validate supporting_pros against declared facts and traits, pruning ungrounded claims."""
    canon_cleaned = {sanitize_anchor_string(f) for f in canon_facts}
    traits_cleaned = {sanitize_anchor_string(t) for t in active_faction_traits}

    valid_pros = []
    for pro in proposal.supporting_pros:
        ref = sanitize_anchor_string(pro.source_ref)
        if (
            pro.source_type == "canon_fact"
            and ref in canon_cleaned
            or pro.source_type == "faction_trait"
            and ref in traits_cleaned
        ):
            valid_pros.append(pro)

    proposal.supporting_pros = valid_pros
    return proposal


def select_sharpest_con(peer_evaluations: list[PeerEvaluation]) -> PeerEvaluation | None:
    """
    Select sharpest Con from negative votes (final_vote < 0).
    Ordering: lowest final_vote -> lowest baseline_plausibility -> ascending voter_faction_id.
    """
    cons = [e for e in peer_evaluations if e.final_vote < 0]
    if not cons:
        return None
    cons.sort(key=lambda e: (e.final_vote, e.baseline_plausibility, e.voter_faction_id))
    return cons[0]


def select_highest_boon_voter(peer_evaluations: list[PeerEvaluation]) -> PeerEvaluation | None:
    """
    Select highest boon voter from positive votes (final_vote > 0).
    Ordering: highest final_vote -> highest baseline_plausibility -> ascending voter_faction_id.
    """
    pros = [e for e in peer_evaluations if e.final_vote > 0]
    if not pros:
        return None
    # For descending sort on votes and baselines, negate values; faction_id ascends
    pros.sort(key=lambda e: (-e.final_vote, -e.baseline_plausibility, e.voter_faction_id))
    return pros[0]


def apply_adjudication_outcome(
    state: WorldState, proposal: Proposal, peer_evaluations: list[PeerEvaluation], total_roll: int
) -> None:
    """
    Apply state mutations based on total resolution roll (2d6 + Net Modifier).
    Bands:
      10+: Ratified Reality (Proposal in canon_facts; active faction improves; highest +1 voter boon)
      7-9: Fractured Reality (Proposal in canon_facts; sharpest con hook in active_rumors)
      4-6: Contested Friction (Proposal + all cons in active_rumors)
      <=3: Counter-Reality (Sharpest con in canon_facts; active faction degrades)
    """
    active_faction = state.get_faction(proposal.active_faction_id)

    if total_roll >= 10:
        # Ratified Reality
        if proposal.world_change_statement not in state.canon_facts:
            state.canon_facts.append(proposal.world_change_statement)
        if active_faction:
            active_faction.improve_posture()
        # Secondary Boon
        boon_voter = select_highest_boon_voter(peer_evaluations)
        if boon_voter:
            voter_fac = state.get_faction(boon_voter.voter_faction_id)
            if voter_fac:
                if voter_fac.exhausted_traits:
                    voter_fac.exhausted_traits.pop(0)
                else:
                    voter_fac.improve_posture()

    elif 7 <= total_roll <= 9:
        # Fractured Reality
        if proposal.world_change_statement not in state.canon_facts:
            state.canon_facts.append(proposal.world_change_statement)
        sharpest_con = select_sharpest_con(peer_evaluations)
        if sharpest_con:
            complication = f"[COMPLICATION] {sharpest_con.public_argument}"
            state.active_rumors.append(complication)

    elif 4 <= total_roll <= 6:
        # Contested Friction
        state.active_rumors.append(proposal.world_change_statement)
        for con in [e for e in peer_evaluations if e.final_vote < 0]:
            state.active_rumors.append(con.public_argument)

    else:
        # <= 3: Counter-Reality
        sharpest_con = select_sharpest_con(peer_evaluations)
        if sharpest_con:
            state.canon_facts.append(sharpest_con.public_argument)
        if active_faction:
            active_faction.degrade_posture()
