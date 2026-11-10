from tome.dice import PostureTier, resolve_posture_tier, roll_d66
from tome.models import Faction, PeerEvaluation, Posture, Proposal, SupportingPro, WorldState
from tome.validator import (
    apply_adjudication_outcome,
    select_highest_boon_voter,
    select_sharpest_con,
    validate_and_sanitize_evaluation,
)


def test_posture_step_die_bounds():
    """Verify posture step-dice never exceed their physical bounds and map to TriO tiers."""
    for _ in range(500):
        roll, tier = resolve_posture_tier(Posture.STABLE, seed=None)
        assert 1 <= roll <= 4
        assert tier in (PostureTier.OBVIOUS, PostureTier.OPTION)
        assert tier != PostureTier.ODD

    for _ in range(500):
        roll, tier = resolve_posture_tier(Posture.PRESSURED, seed=None)
        assert 1 <= roll <= 6

    for _ in range(500):
        roll, tier = resolve_posture_tier(Posture.CORNERED, seed=None)
        assert 1 <= roll <= 8


def test_spark_table_d66_bounds():
    """Verify d66 rolls map to 11-66 discrete digits with no 0 or 7-9."""
    for _ in range(200):
        d66 = roll_d66()
        d1 = d66 // 10
        d2 = d66 % 10
        assert 1 <= d1 <= 6
        assert 1 <= d2 <= 6


def test_peer_evaluation_linter_shift_limits():
    """Verify shifts > 1 or < -1 are reverted to baseline."""
    eval_invalid = PeerEvaluation(
        voter_faction_id="fac_1",
        baseline_plausibility=1,
        goal_alignment="hostile",
        biased_shift_applied=True,
        cited_anchor="Valid Fact",
        final_vote=-1,  # shift of -2!
        public_argument="Invalid jump",
    )
    sanitized, trait_consumed = validate_and_sanitize_evaluation(
        eval_invalid, canon_facts=["Valid Fact"], voter_traits=["Trait A"], exhausted_traits=set()
    )
    assert sanitized.final_vote == 1
    assert sanitized.biased_shift_applied is False
    assert sanitized.cited_anchor is None
    assert trait_consumed is None


def test_peer_evaluation_grounding_gate():
    """Verify non-zero shifts require exact fact or unexhausted trait, else revert to baseline."""
    # Case 1: Ungrounded / Hallucinated fact
    eval_hallucinated = PeerEvaluation(
        voter_faction_id="fac_1",
        baseline_plausibility=0,
        goal_alignment="hostile",
        biased_shift_applied=True,
        cited_anchor="Hallucinated Fact",
        final_vote=-1,
        public_argument="Some con argument",
    )
    sanitized, trait_consumed = validate_and_sanitize_evaluation(
        eval_hallucinated,
        canon_facts=["Real Fact A"],
        voter_traits=["Trait 1"],
        exhausted_traits=set(),
    )
    assert sanitized.final_vote == 0
    assert sanitized.biased_shift_applied is False
    assert trait_consumed is None

    # Case 2: Valid fact anchor
    eval_valid_fact = PeerEvaluation(
        voter_faction_id="fac_1",
        baseline_plausibility=0,
        goal_alignment="hostile",
        biased_shift_applied=True,
        cited_anchor='"Real Fact A" ',  # with whitespace & quotes
        final_vote=-1,
        public_argument="Some con argument",
    )
    sanitized, trait_consumed = validate_and_sanitize_evaluation(
        eval_valid_fact,
        canon_facts=["Real Fact A"],
        voter_traits=["Trait 1"],
        exhausted_traits=set(),
    )
    assert sanitized.final_vote == -1
    assert sanitized.biased_shift_applied is True
    assert sanitized.cited_anchor == "Real Fact A"
    assert trait_consumed is None

    # Case 3: Valid trait anchor (consumes trait)
    eval_valid_trait = PeerEvaluation(
        voter_faction_id="fac_1",
        baseline_plausibility=0,
        goal_alignment="beneficial",
        biased_shift_applied=True,
        cited_anchor="Trait 1",
        final_vote=1,
        public_argument="Supported by trait",
    )
    sanitized, trait_consumed = validate_and_sanitize_evaluation(
        eval_valid_trait,
        canon_facts=["Real Fact A"],
        voter_traits=["Trait 1"],
        exhausted_traits=set(),
    )
    assert sanitized.final_vote == 1
    assert trait_consumed == "Trait 1"

    # Case 4: Already exhausted trait
    sanitized_exhausted, trait_consumed2 = validate_and_sanitize_evaluation(
        eval_valid_trait,
        canon_facts=["Real Fact A"],
        voter_traits=["Trait 1"],
        exhausted_traits={"Trait 1"},
    )
    assert sanitized_exhausted.final_vote == 0
    assert sanitized_exhausted.biased_shift_applied is False
    assert trait_consumed2 is None


def test_deterministic_con_selection():
    """Verify sharpest con selects lowest final_vote -> lowest baseline -> alphabetical faction id."""
    v1 = PeerEvaluation(
        voter_faction_id="fac_b",
        baseline_plausibility=0,
        goal_alignment="hostile",
        biased_shift_applied=True,
        cited_anchor="F",
        final_vote=-1,
        public_argument="Arg B",
    )
    v2 = PeerEvaluation(
        voter_faction_id="fac_a",
        baseline_plausibility=0,
        goal_alignment="hostile",
        biased_shift_applied=True,
        cited_anchor="F",
        final_vote=-1,
        public_argument="Arg A",
    )
    v3 = PeerEvaluation(
        voter_faction_id="fac_c",
        baseline_plausibility=-1,
        goal_alignment="hostile",
        biased_shift_applied=False,
        cited_anchor=None,
        final_vote=-1,
        public_argument="Arg C",
    )

    # v3 has baseline -1, lower than 0
    sharpest = select_sharpest_con([v1, v2, v3])
    assert sharpest.voter_faction_id == "fac_c"

    # Between v1 and v2 with equal votes and baselines, fac_a wins alphabetically
    sharpest_tie = select_sharpest_con([v1, v2])
    assert sharpest_tie.voter_faction_id == "fac_a"


def test_deterministic_boon_selection():
    """Verify highest boon selects highest final_vote -> highest baseline -> alphabetical faction id."""
    v1 = PeerEvaluation(
        voter_faction_id="fac_b",
        baseline_plausibility=0,
        goal_alignment="beneficial",
        biased_shift_applied=True,
        cited_anchor="F",
        final_vote=1,
        public_argument="Arg B",
    )
    v2 = PeerEvaluation(
        voter_faction_id="fac_a",
        baseline_plausibility=0,
        goal_alignment="beneficial",
        biased_shift_applied=True,
        cited_anchor="F",
        final_vote=1,
        public_argument="Arg A",
    )
    v3 = PeerEvaluation(
        voter_faction_id="fac_c",
        baseline_plausibility=1,
        goal_alignment="beneficial",
        biased_shift_applied=False,
        cited_anchor=None,
        final_vote=1,
        public_argument="Arg C",
    )

    # v3 has baseline 1, higher than 0
    boon_voter = select_highest_boon_voter([v1, v2, v3])
    assert boon_voter.voter_faction_id == "fac_c"

    # Between v1 and v2, fac_a wins alphabetically
    boon_tie = select_highest_boon_voter([v1, v2])
    assert boon_tie.voter_faction_id == "fac_a"


def test_outcome_band_state_mutations():
    """Verify 10+, 7-9, 4-6, <=3 state mutations on WorldState."""
    f1 = Faction(
        id="f1",
        name="F1",
        agenda="A",
        posture=Posture.PRESSURED,
        traits=["T1"],
        exhausted_traits=["T1"],
    )
    f2 = Faction(
        id="f2", name="F2", agenda="A", posture=Posture.STABLE, traits=["T2"], exhausted_traits=[]
    )
    state = WorldState(session_index=1, canon_facts=["F0"], active_rumors=[], factions=[f1, f2])

    proposal = Proposal(
        active_faction_id="f1",
        posture_die="d6",
        posture_roll=2,
        trio_tier="Obvious",
        spark_tags=["Action:Attack", "Focus:Resource"],
        world_change_statement="F1 takes over mine.",
        supporting_pros=[SupportingPro(source_type="canon_fact", source_ref="F0", argument="Arg")],
    )

    # 1. Band 10+ (Ratified Reality)
    eval_f2 = PeerEvaluation(
        voter_faction_id="f2",
        baseline_plausibility=1,
        goal_alignment="beneficial",
        biased_shift_applied=False,
        final_vote=1,
        public_argument="Great",
    )
    apply_adjudication_outcome(state, proposal, [eval_f2], total_roll=10)
    assert "F1 takes over mine." in state.canon_facts
    assert state.get_faction("f1").posture == Posture.STABLE  # improved from Pressured to Stable

    # 2. Band 7-9 (Fractured Reality)
    eval_con = PeerEvaluation(
        voter_faction_id="f2",
        baseline_plausibility=0,
        goal_alignment="hostile",
        biased_shift_applied=True,
        cited_anchor="T2",
        final_vote=-1,
        public_argument="Mine is toxic.",
    )
    proposal2 = Proposal(
        active_faction_id="f1",
        posture_die="d4",
        posture_roll=1,
        trio_tier="Obvious",
        spark_tags=[],
        world_change_statement="F1 mines ore.",
        supporting_pros=[SupportingPro(source_type="canon_fact", source_ref="F0", argument="Arg")],
    )
    apply_adjudication_outcome(state, proposal2, [eval_con], total_roll=8)
    assert "F1 mines ore." in state.canon_facts
    assert "[COMPLICATION] Mine is toxic." in state.active_rumors

    # 3. Band 4-6 (Contested Friction)
    proposal3 = Proposal(
        active_faction_id="f1",
        posture_die="d4",
        posture_roll=1,
        trio_tier="Obvious",
        spark_tags=[],
        world_change_statement="F1 builds wall.",
        supporting_pros=[SupportingPro(source_type="canon_fact", source_ref="F0", argument="Arg")],
    )
    apply_adjudication_outcome(state, proposal3, [eval_con], total_roll=5)
    assert "F1 builds wall." not in state.canon_facts
    assert "F1 builds wall." in state.active_rumors

    # 4. Band <=3 (Counter-Reality)
    apply_adjudication_outcome(state, proposal3, [eval_con], total_roll=3)
    assert "Mine is toxic." in state.canon_facts
    assert state.get_faction("f1").posture == Posture.PRESSURED  # degraded from Stable to Pressured


def test_full_simulation_cycle_e2e():
    """Verify an end-to-end simulation cycle with deterministic mock generators."""
    from tome.runner import run_simulation_cycle

    f1 = Faction(
        id="fac_iron",
        name="Iron Choir",
        agenda="Power",
        posture=Posture.CORNERED,
        traits=["Scrap Mastery"],
    )
    f2 = Faction(
        id="fac_dock",
        name="Dock Syndicate",
        agenda="Trade",
        posture=Posture.STABLE,
        traits=["Harbor Control"],
    )
    state = WorldState(
        session_index=1, canon_facts=["The Conduit is open."], active_rumors=[], factions=[f1, f2]
    )

    def mock_proposal(fac, tier, tags, s):
        return Proposal(
            active_faction_id=fac.id,
            posture_die="d8" if fac.posture == Posture.CORNERED else "d4",
            posture_roll=1,
            trio_tier=tier.value,
            spark_tags=tags,
            world_change_statement=f"{fac.name} claims the conduit.",
            supporting_pros=[
                SupportingPro(
                    source_type="canon_fact", source_ref="The Conduit is open.", argument="Open."
                )
            ],
        )

    def mock_peer_review(voter, prop, s):
        return PeerEvaluation(
            voter_faction_id=voter.id,
            baseline_plausibility=1,
            goal_alignment="hostile",
            biased_shift_applied=True,
            cited_anchor="The Conduit is open.",
            final_vote=0,
            public_argument=f"{voter.name} opposes this.",
        )

    updated_state, proposals, evals = run_simulation_cycle(
        state, mock_proposal, mock_peer_review, seed=42
    )

    assert updated_state.session_index == 2
    assert len(proposals) == 2
    assert len(evals) == 2
    for proposal in proposals:
        assert proposal.model_dump()["trio_tier"] in {tier.value for tier in PostureTier}
    # Verify exhausted traits are clean at cycle conclusion
    for f in updated_state.factions:
        assert len(f.exhausted_traits) == 0
