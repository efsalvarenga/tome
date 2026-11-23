import re
from typing import Annotated, Final, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, field_validator, model_validator

from tome.engine import text

CONTRACT_VERSION: Final = "1.1.0"
D66_KEYS: Final = frozenset(10 * tens + units for tens in range(1, 7) for units in range(1, 7))


def _non_whitespace(value: str) -> str:
    if not text.is_non_whitespace(value):
        raise ValueError("Text must not be blank after normalisation.")
    return value


NonWhitespaceStr = Annotated[str, AfterValidator(_non_whitespace)]
Vote = Annotated[int, Field(ge=-1, le=1)]
TrioTier = Literal["Obvious", "Option", "Odd"]
Outcome = Literal["Success", "Failure"]
ReasonCode = Literal["proposal-succeeded", "failure-consequence", "turn-tick", "round-complete"]
ErrorCode = Literal[
    "INVALID_RUN_REQUEST",
    "PROPOSAL_GENERATION_FAILED",
    "INVALID_PROPOSAL",
    "PEER_REVIEW_FAILED",
    "UMPIRE_REVIEW_FAILED",
    "UMPIRE_RESOLUTION_FAILED",
    "MECHANICS_FAILED",
]
SparkTable = dict[int, NonWhitespaceStr]


class ContractModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", revalidate_instances="always")


class Actor(ContractModel):
    id: NonWhitespaceStr
    name: str
    agenda: str


class WorldState(ContractModel):
    session_index: int = Field(ge=0)
    turn_index: int = Field(ge=0)
    canon_facts: list[NonWhitespaceStr]
    actors: list[Actor]

    @model_validator(mode="after")
    def unique_text(self):
        if text.has_matching_pair(self.canon_facts):
            raise ValueError("Canon facts must not match.")
        if text.has_matching_pair([actor.id for actor in self.actors]):
            raise ValueError("Actor IDs must not match.")
        return self


class SupportingPro(ContractModel):
    source_type: Literal["canon_fact"]
    source_ref: str
    argument: str


class ProposalDraft(ContractModel):
    world_change_statement: NonWhitespaceStr
    supporting_pros: list[SupportingPro] = Field(min_length=1, max_length=2)


class Proposal(ContractModel):
    active_actor_id: str
    posture_roll: int = Field(ge=1, le=6)
    trio_tier: TrioTier
    spark_tags: list[str] = Field(min_length=2, max_length=2)
    world_change_statement: NonWhitespaceStr
    supporting_pros: list[SupportingPro] = Field(min_length=1, max_length=2)


class PeerEvaluation(ContractModel):
    """A peer's vote on a proposal.

    The engine recomputes ``biased_shift_applied`` and ``cited_anchor``, and reverts
    ``final_vote`` to ``baseline_plausibility`` unless a one-step shift cites a canon fact.
    """

    voter_actor_id: str
    baseline_plausibility: Vote
    biased_shift_applied: bool
    cited_anchor: str | None
    final_vote: Vote
    public_argument: str


class UmpireRejection(ContractModel):
    voter_actor_id: str
    reason: NonWhitespaceStr


class UmpireRejectionRecord(ContractModel):
    voter_actor_id: str
    reason: NonWhitespaceStr
    evaluation_before_reversion: PeerEvaluation


class FailureResolution(ContractModel):
    source_voter_actor_id: str | None
    world_change_statement: NonWhitespaceStr
    rationale: NonWhitespaceStr


class StateChange(ContractModel):
    path: Literal["/canon_facts", "/session_index", "/turn_index"]
    before: list[str] | int
    after: list[str] | int
    reason: ReasonCode


class TurnRecord(ContractModel):
    turn_index: int = Field(ge=1)
    session_index: int = Field(ge=0)
    active_actor_id: str
    proposal: Proposal
    peer_evaluations: list[PeerEvaluation]
    umpire_rejections: list[UmpireRejectionRecord]
    net_vote_modifier: int = Field(ge=-3, le=3)
    resolution_roll: int = Field(ge=2, le=12)
    adjusted_total: int = Field(ge=-1, le=15)
    outcome: Outcome
    failure_resolution: FailureResolution | None
    state_changes: list[StateChange]


class SparkTables(ContractModel):
    Action: SparkTable
    Focus: SparkTable
    Method: SparkTable
    Disposition: SparkTable
    Motivation: SparkTable

    @field_validator("Action", "Focus", "Method", "Disposition", "Motivation", mode="before")
    @classmethod
    def d66_keys(cls, value):
        if not isinstance(value, dict):
            return value
        if all(type(key) is str for key in value):
            if not all(re.fullmatch(r"[1-6][1-6]", key) for key in value):
                raise ValueError("Table keys must be decimal d66 keys.")
            value = {int(key): entry for key, entry in value.items()}
        elif not all(type(key) is int for key in value):
            raise ValueError("Table keys must be uniformly strings or integers.")
        if set(value) != D66_KEYS:
            raise ValueError("A table must contain exactly the 36 d66 keys.")
        return value


class RunRequest(ContractModel):
    contract_version: Literal["1.1.0"]
    world_state: WorldState
    turn_count: int = Field(ge=1)
    # Unvalidated defaults allow omission, while explicit null remains invalid.
    spark_tables: SparkTables = None
    first_round_order: list[str] = None
    seed: int = Field(default=None, ge=0)

    @model_validator(mode="after")
    def valid_order(self):
        actor_ids = [actor.id for actor in self.world_state.actors]
        if not actor_ids:
            raise ValueError("A run requires at least one actor.")
        if self.first_round_order is not None and sorted(self.first_round_order) != sorted(
            actor_ids
        ):
            raise ValueError("The order must be an exact permutation of actor IDs.")
        return self


class RunResult(ContractModel):
    contract_version: Literal["1.1.0"]
    final_world_state: WorldState
    spark_table_source: Literal["trio-d66-v1", "request"]
    turn_records: list[TurnRecord]


class RunFailure(ContractModel):
    contract_version: Literal["1.1.0"]
    code: ErrorCode
    message: str
