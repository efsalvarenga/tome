from collections.abc import Mapping, Sequence

from tome.engine import text
from tome.engine.errors import (
    InvalidProposalError,
    PeerReviewError,
    ProposalGenerationError,
    UmpireResolutionError,
    UmpireReviewError,
)
from tome.engine.mechanics import TurnCues
from tome.engine.models import (
    FailureResolution,
    PeerEvaluation,
    Proposal,
    ProposalDraft,
    UmpireRejection,
    UmpireRejectionRecord,
)


def _validate_output(raw, model_cls, error_cls):
    if not isinstance(raw, (model_cls, Mapping)):
        raise error_cls("The callback returned an unsupported value.")
    try:
        value = raw.model_dump() if isinstance(raw, model_cls) else dict(raw)
        return model_cls.model_validate(value)
    except MemoryError:
        raise
    except Exception as exc:
        raise error_cls("The callback output is malformed.") from exc


def build_proposal(
    raw,
    *,
    active_actor_id: str,
    cues: TurnCues,
    canon_facts: Sequence[str],
) -> Proposal:
    draft = _validate_output(raw, ProposalDraft, ProposalGenerationError)
    if text.find_match(draft.world_change_statement, canon_facts) is not None:
        raise InvalidProposalError("The proposal already appears in canon.")
    pros = [
        pro
        for pro in draft.supporting_pros
        if text.find_match(pro.source_ref, canon_facts) is not None
    ]
    if not pros:
        raise InvalidProposalError("The proposal has no grounded supporting arguments.")
    return Proposal(
        active_actor_id=active_actor_id,
        posture_roll=cues.posture_roll,
        trio_tier=cues.trio_tier,
        spark_tags=list(cues.spark_tags),
        world_change_statement=draft.world_change_statement,
        supporting_pros=pros,
    )


def validate_peer_evaluation(
    raw,
    *,
    voter_actor_id: str,
    canon_facts: Sequence[str],
) -> PeerEvaluation:
    evaluation = _validate_output(raw, PeerEvaluation, PeerReviewError)
    if evaluation.voter_actor_id != voter_actor_id:
        raise PeerReviewError("The evaluation names a different voter.")
    shift = evaluation.final_vote - evaluation.baseline_plausibility
    anchor = None
    if abs(shift) == 1 and evaluation.cited_anchor is not None:
        anchor = text.find_match(evaluation.cited_anchor, canon_facts)
    if anchor is None:
        evaluation.final_vote = evaluation.baseline_plausibility
    evaluation.biased_shift_applied = anchor is not None
    evaluation.cited_anchor = anchor
    return evaluation


def apply_umpire_rejections(
    raw,
    *,
    evaluations: list[PeerEvaluation],
) -> tuple[list[PeerEvaluation], list[UmpireRejectionRecord]]:
    if not isinstance(raw, list):
        raise UmpireReviewError("Umpire review must return a list.")
    by_id = {evaluation.voter_actor_id: evaluation for evaluation in evaluations}
    rejections = {}
    for element in raw:
        rejection = _validate_output(element, UmpireRejection, UmpireReviewError)
        voter_id = rejection.voter_actor_id
        if voter_id in rejections or voter_id not in by_id:
            raise UmpireReviewError("A rejection names a duplicate or unknown voter.")
        evaluation = by_id[voter_id]
        if evaluation.final_vote == evaluation.baseline_plausibility:
            raise UmpireReviewError("A rejection must name a remaining shifted vote.")
        rejections[voter_id] = rejection
    updated, records = [], []
    for evaluation in evaluations:
        after = evaluation.model_copy(deep=True)
        if evaluation.voter_actor_id in rejections:
            rejection = rejections[evaluation.voter_actor_id]
            records.append(
                UmpireRejectionRecord(
                    voter_actor_id=rejection.voter_actor_id,
                    reason=rejection.reason,
                    evaluation_before_reversion=evaluation.model_copy(deep=True),
                )
            )
            after.final_vote = after.baseline_plausibility
            after.biased_shift_applied = False
            after.cited_anchor = None
        updated.append(after)
    return updated, records


def lowest_vote_candidates(evaluations: list[PeerEvaluation]) -> list[str]:
    if not evaluations:
        return []
    lowest = min(evaluation.final_vote for evaluation in evaluations)
    return [
        evaluation.voter_actor_id for evaluation in evaluations if evaluation.final_vote == lowest
    ]


def validate_failure_resolution(
    raw,
    *,
    candidate_voter_ids: list[str],
    canon_facts: Sequence[str],
    rejected_statement: str,
) -> FailureResolution:
    resolution = _validate_output(raw, FailureResolution, UmpireResolutionError)
    if (
        resolution.source_voter_actor_id is not None
        and resolution.source_voter_actor_id not in candidate_voter_ids
    ):
        raise UmpireResolutionError("The failure source is not a lowest-vote candidate.")
    if text.find_match(resolution.world_change_statement, canon_facts) is not None or text.matches(
        resolution.world_change_statement, rejected_statement
    ):
        raise UmpireResolutionError("The failure consequence must be new.")
    return resolution
