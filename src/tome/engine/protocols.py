from collections.abc import Mapping
from typing import Any, Protocol

from tome.engine.models import (
    Actor,
    FailureResolution,
    PeerEvaluation,
    Proposal,
    ProposalDraft,
    TrioTier,
    UmpireRejection,
    WorldState,
)


class ProposalGenerator(Protocol):
    def __call__(
        self,
        active_actor: Actor,
        trio_tier: TrioTier,
        spark_tags: list[str],
        world_state: WorldState,
        /,
    ) -> ProposalDraft | Mapping[str, Any]: ...


class PeerReviewer(Protocol):
    def __call__(
        self,
        voter_actor: Actor,
        proposal: Proposal,
        world_state: WorldState,
        /,
    ) -> PeerEvaluation | Mapping[str, Any]: ...


class UmpireReview(Protocol):
    def __call__(
        self,
        turn_index: int,
        proposal: Proposal,
        peer_evaluations: list[PeerEvaluation],
        world_state: WorldState,
        /,
    ) -> list[UmpireRejection | Mapping[str, Any]]: ...


class FailureResolver(Protocol):
    def __call__(
        self,
        turn_index: int,
        proposal: Proposal,
        peer_evaluations: list[PeerEvaluation],
        candidate_voter_ids: list[str],
        adjusted_total: int,
        world_state: WorldState,
        /,
    ) -> FailureResolution | Mapping[str, Any]: ...
