import random
from collections.abc import Mapping
from typing import Any

from tome.engine.errors import (
    InvalidRunRequestError,
    MechanicsError,
    PeerReviewError,
    ProposalGenerationError,
    RunError,
    UmpireResolutionError,
    UmpireReviewError,
)
from tome.engine.gates import (
    apply_umpire_rejections,
    build_proposal,
    lowest_vote_candidates,
    validate_failure_resolution,
    validate_peer_evaluation,
)
from tome.engine.mechanics import (
    DEFAULT_TABLE_SET_ID,
    default_spark_tables,
    draw_turn_cues,
    first_round_order,
    net_vote_modifier,
    resolve_outcome,
    roll_resolution,
)
from tome.engine.models import CONTRACT_VERSION, RunRequest, RunResult, StateChange, TurnRecord
from tome.engine.protocols import FailureResolver, PeerReviewer, ProposalGenerator, UmpireReview


def run(
    request: RunRequest | Mapping[str, Any],
    proposal_generator: ProposalGenerator,
    peer_reviewer: PeerReviewer,
    failure_resolver: FailureResolver,
    umpire_review: UmpireReview | None = None,
) -> RunResult:
    if not all(
        callable(callback) for callback in (proposal_generator, peer_reviewer, failure_resolver)
    ):
        raise InvalidRunRequestError("All three required integrations must be callable.")
    if umpire_review is not None and not callable(umpire_review):
        raise InvalidRunRequestError("Umpire review must be callable or None.")
    if not isinstance(request, (Mapping, RunRequest)):
        raise InvalidRunRequestError("The request must be a mapping or RunRequest.")
    try:
        value = (
            dict(request) if isinstance(request, Mapping) else request.model_dump(exclude_none=True)
        )
        request = RunRequest.model_validate(value)
    except MemoryError:
        raise
    except Exception as exc:
        raise InvalidRunRequestError("The run request is invalid.") from exc

    try:
        if request.spark_tables is None:
            tables, source = default_spark_tables(), DEFAULT_TABLE_SET_ID
        else:
            tables, source = request.spark_tables, "request"
        rng = random.Random(request.seed) if request.seed is not None else random.Random()
        order = first_round_order(
            rng,
            [actor.id for actor in request.world_state.actors],
            request.first_round_order,
        )
        state = request.world_state.model_copy(deep=True)
        actors = {actor.id: actor for actor in state.actors}
        records = []
        for i in range(request.turn_count):
            active_id = order[i % len(order)]
            turn_number = state.turn_index + 1
            cues = draw_turn_cues(rng, tables)
            proposal_args = (
                actors[active_id].model_copy(deep=True),
                cues.trio_tier,
                list(cues.spark_tags),
                state.model_copy(deep=True),
            )
            try:
                raw = proposal_generator(*proposal_args)
            except MemoryError:
                raise
            except Exception as exc:
                raise ProposalGenerationError("Proposal generation failed.") from exc
            proposal = build_proposal(
                raw,
                active_actor_id=active_id,
                cues=cues,
                canon_facts=state.canon_facts,
            )
            evaluations = []
            for actor in state.actors:
                if actor.id == active_id:
                    continue
                peer_args = (
                    actor.model_copy(deep=True),
                    proposal.model_copy(deep=True),
                    state.model_copy(deep=True),
                )
                try:
                    raw = peer_reviewer(*peer_args)
                except MemoryError:
                    raise
                except Exception as exc:
                    raise PeerReviewError("Peer review failed.") from exc
                evaluations.append(
                    validate_peer_evaluation(
                        raw,
                        voter_actor_id=actor.id,
                        canon_facts=state.canon_facts,
                    )
                )
            umpire_rejections = []
            if umpire_review is not None and any(
                evaluation.final_vote != evaluation.baseline_plausibility
                for evaluation in evaluations
            ):
                review_args = (
                    turn_number,
                    proposal.model_copy(deep=True),
                    [evaluation.model_copy(deep=True) for evaluation in evaluations],
                    state.model_copy(deep=True),
                )
                try:
                    raw = umpire_review(*review_args)
                except MemoryError:
                    raise
                except Exception as exc:
                    raise UmpireReviewError("Umpire review failed.") from exc
                evaluations, umpire_rejections = apply_umpire_rejections(
                    raw, evaluations=evaluations
                )
            modifier = net_vote_modifier(evaluation.final_vote for evaluation in evaluations)
            first_die, second_die = roll_resolution(rng)
            roll = first_die + second_die
            total = roll + modifier
            outcome = resolve_outcome(total)
            failure_resolution = None
            if outcome == "Success":
                new_fact, reason = proposal.world_change_statement, "proposal-succeeded"
            else:
                candidates = lowest_vote_candidates(evaluations)
                failure_args = (
                    turn_number,
                    proposal.model_copy(deep=True),
                    [evaluation.model_copy(deep=True) for evaluation in evaluations],
                    list(candidates),
                    total,
                    state.model_copy(deep=True),
                )
                try:
                    raw = failure_resolver(*failure_args)
                except MemoryError:
                    raise
                except Exception as exc:
                    raise UmpireResolutionError("Failure resolution failed.") from exc
                failure_resolution = validate_failure_resolution(
                    raw,
                    candidate_voter_ids=candidates,
                    canon_facts=state.canon_facts,
                    rejected_statement=proposal.world_change_statement,
                )
                new_fact, reason = failure_resolution.world_change_statement, "failure-consequence"
            before_canon = list(state.canon_facts)
            before_turn, before_session = state.turn_index, state.session_index
            state.canon_facts.append(new_fact)
            state.turn_index += 1
            if (i + 1) % len(order) == 0:
                state.session_index += 1
            if (
                len(state.canon_facts) != len(before_canon) + 1
                or state.turn_index != before_turn + 1
            ):
                raise MechanicsError("A turn must add exactly one fact and one time tick.")
            changes = [
                StateChange(
                    path="/canon_facts",
                    before=before_canon,
                    after=list(state.canon_facts),
                    reason=reason,
                )
            ]
            if state.session_index != before_session:
                changes.append(
                    StateChange(
                        path="/session_index",
                        before=before_session,
                        after=state.session_index,
                        reason="round-complete",
                    )
                )
            changes.append(
                StateChange(
                    path="/turn_index",
                    before=before_turn,
                    after=state.turn_index,
                    reason="turn-tick",
                )
            )
            records.append(
                TurnRecord(
                    turn_index=state.turn_index,
                    session_index=state.session_index,
                    active_actor_id=active_id,
                    proposal=proposal,
                    peer_evaluations=evaluations,
                    umpire_rejections=umpire_rejections,
                    net_vote_modifier=modifier,
                    resolution_roll=roll,
                    adjusted_total=total,
                    outcome=outcome,
                    failure_resolution=failure_resolution,
                    state_changes=changes,
                )
            )
        if len(records) != request.turn_count:
            raise MechanicsError("The record count does not equal the requested turn count.")
        return RunResult(
            contract_version=CONTRACT_VERSION,
            final_world_state=state,
            spark_table_source=source,
            turn_records=records,
        )
    except (RunError, MemoryError, RecursionError, SystemError):
        raise
    except Exception as exc:
        raise MechanicsError("An internal engine operation failed.") from exc
