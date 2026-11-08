"""Data models and Pydantic schemas for TOME."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Posture(str, Enum):
    STABLE = "Stable"
    PRESSURED = "Pressured"
    CORNERED = "Cornered"


class Faction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    name: str
    agenda: str
    posture: Posture
    traits: list[str] = Field(default_factory=list)
    exhausted_traits: list[str] = Field(default_factory=list)

    def improve_posture(self) -> None:
        """Improve posture by 1 step (clamped at Stable)."""
        if self.posture == Posture.CORNERED:
            self.posture = Posture.PRESSURED
        elif self.posture == Posture.PRESSURED:
            self.posture = Posture.STABLE

    def degrade_posture(self) -> None:
        """Degrade posture by 1 step (clamped at Cornered)."""
        if self.posture == Posture.STABLE:
            self.posture = Posture.PRESSURED
        elif self.posture == Posture.PRESSURED:
            self.posture = Posture.CORNERED


class WorldState(BaseModel):
    model_config = ConfigDict(extra="forbid")
    session_index: int = Field(ge=0)
    canon_facts: list[str] = Field(default_factory=list)
    active_rumors: list[str] = Field(default_factory=list)
    factions: list[Faction] = Field(default_factory=list)

    def get_faction(self, faction_id: str) -> Faction | None:
        for f in self.factions:
            if f.id == faction_id:
                return f
        return None


class SupportingPro(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_type: str = Field(..., pattern="^(faction_trait|canon_fact)$")
    source_ref: str
    argument: str


class Proposal(BaseModel):
    model_config = ConfigDict(extra="forbid")
    active_faction_id: str
    posture_die: str
    posture_roll: int
    triple_o_tier: str
    spark_tags: list[str] = Field(default_factory=list)
    world_change_statement: str
    supporting_pros: list[SupportingPro] = Field(default_factory=list)


class PeerEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    voter_faction_id: str
    baseline_plausibility: int = Field(..., ge=-1, le=1)
    goal_alignment: str = Field(..., pattern="^(beneficial|neutral|hostile)$")
    biased_shift_applied: bool = False
    cited_anchor: str | None = None
    final_vote: int = Field(..., ge=-1, le=1)
    public_argument: str
