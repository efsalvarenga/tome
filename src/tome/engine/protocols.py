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
    """Drafts the active actor's proposal; uncited pros are pruned, and one must cite canon."""

    def __call__(
        self,
        active_actor: Actor,
        trio_tier: TrioTier,
        spark_tags: list[str],
        world_state: WorldState,
        /,
    ) -> ProposalDraft | Mapping[str, Any]: ...


class PeerReviewer(Protocol):
    """Returns one non-active actor's evaluation of the proposal."""

    def __call__(
        self,
        voter_actor: Actor,
        proposal: Proposal,
        world_state: WorldState,
        /,
    ) -> PeerEvaluation | Mapping[str, Any]: ...


class UmpireReview(Protocol):
    """Optional human review that may reject shifted votes before the resolution roll."""

    def __call__(
        self,
        turn_index: int,
        proposal: Proposal,
        peer_evaluations: list[PeerEvaluation],
        world_state: WorldState,
        /,
    ) -> list[UmpireRejection | Mapping[str, Any]]: ...


class FailureResolver(Protocol):
    """Turns a failed proposal into one new canon fact, citing a lowest-vote peer or none."""

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
