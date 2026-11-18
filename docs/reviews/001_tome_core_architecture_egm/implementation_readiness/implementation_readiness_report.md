# EGM Stage 9: Implementation Readiness Review Loop

**Status:** Stopped after round 6 (past the cap); plan accepted by the human developer on 2026-11-18
**Started:** 2026-11-17
**Target:** [Implementation plan](../../../plans/001_tome_core_architecture_plan.md), Detailed Implementation Plan section, re-resolved before each round
**Preset:** Implementation plan only (Stage 9)
**Reviewers:** `implementation_readiness`, `codebase_details`, `style`
**Standards:** `implementation-readiness-standard` for readiness and codebase details; the official style persona for wording
**Context:** [Spec 001, version 1.1.2](../../../designs/001_tome_core_architecture.md), auto-included as the plan's only local link; `src/`, `tests/`, `pyproject.toml`, `AGENTS.md`, and `README.md`, selected by the user
**Consecutive clean rounds:** 0 of 2
**Round cap:** 5

## Configuration and Execution

The user selected the implementation-plan-only preset and confirmed the reviewers, standards, context, and loop rules.
The slash-command name was not registered in this harness.
The coordinator follows the installed official `egm-review` and `egm-review-loop` instructions and their general-purpose-subagent fallback with the installed personas.
Each reviewer runs in a fresh native task context without the parent conversation or earlier findings.
Host-level exclusion of project or user instructions has not been independently established.

## Settled Decisions

The plan records these as author decisions; reviewers may report their consequences, but the coordinator does not reopen their direction.

| Decision | Settled by |
| :--- | :--- |
| D1: plan in `docs/plans/` | Author, during drafting |
| D2: build alongside, delete legacy last | Author, during drafting |
| D3: `tome/engine/` subpackage | Author, during drafting |
| D4: `scripts/lint.sh` and committed `uv.lock` | Author, during drafting |
| D12: callback-exception scope, kept over Edge Case 6's wording | Author, 2026-11-17 |

## Rounds

| Round | Detailed range | Reviewers | Raw findings | Clean before edits | Clean streak | Resolution |
| :--- | :--- | :--- | :--- | :--- | ---: | :--- |
| 1 | 15-475 | All three completed | 0 Blocker, 15 Major, 15 Nit | No | 0 | All 20 edit groups accepted and applied |
| 2 | 15-491 | All three completed | 0 Blocker, 4 Major, 15 Nit | No | 0 | All 14 edit groups accepted and applied |
| 3 | 15-499 | All three completed | 0 Blocker, 2 Major, 15 Nit | No | 0 | All 16 edit groups accepted and applied |
| 4 | 15-505 | All three completed | 0 Blocker, 1 Major, 11 Nit | No | 0 | All 12 edit groups accepted and applied |
| 5 | 15-506 | All three completed | 0 Blocker, 2 Major, 5 Nit | No | 0 | All 7 edit groups accepted and applied |
| 6 | 15-508 | All three completed | 0 Blocker, 2 Major, 13 Nit | No | 0 | All 14 edit groups accepted and applied |

### Round 1

- Input SHA-256: `677122edc137a7e1f642f3899a265610b3f0a33614273919ad0b2ef3c4d1a8ef`.
- [Complete reviewer reports](round_01/reviewer_report.md).
- [Annotated resolution proposals](round_01/goldfish_review_report.md).
- All 30 findings are PROPOSE FIX, grouped into 20 edit groups; none reopens a settled decision.
- The coordinator probed five behaviours the findings depend on; one reviewer claim, that a star import fails Ruff F403 under the repository settings, was not confirmed, but the proposed literal-export fix stands.
- No plan edit was made before the human decision.
- The human selected auto accept; all 20 edit groups were applied in one batch.
- The approved E19 pattern used `\b`, which silently matched nothing under macOS `git grep -E`; the plan uses an equivalent portable pattern, tested against the 9 current legacy imports and 13 synthetic cases, as recorded in the round report.
- Post-resolution SHA-256: `6c28bf0617aabdd989d4de1e3ef237e9bf474aa0bdbbf50f9256b7241713631b`; the Detailed Implementation Plan spans lines 15-491.

### Round 2

- The user confirmed continuing on 2026-11-18, after a restart; the plan and records were unchanged.
- Input SHA-256: `6c28bf0617aabdd989d4de1e3ef237e9bf474aa0bdbbf50f9256b7241713631b`.
- [Complete reviewer reports](round_02/reviewer_report.md).
- [Annotated resolution proposals](round_02/goldfish_review_report.md).
- The implementation-readiness reviewer found no Blocker or Major.
- All 19 findings are PROPOSE FIX, grouped into 14 edit groups; none reopens a settled decision and none is churn.
- The coordinator confirmed the baseline-command defect, found the Ruff star-import attribution wrong, and verified the seed-20 worked example.
- The human selected auto accept; all 14 edit groups were applied in one batch, exactly as proposed.
- Post-resolution SHA-256: `afd65538a48727343205668a8c3fc6c5d9ce13ab176b508993535c417f5c3a00`; the Detailed Implementation Plan spans lines 15-499.

### Round 3

- The user confirmed round 3 after round-two resolution.
- Input SHA-256: `afd65538a48727343205668a8c3fc6c5d9ce13ab176b508993535c417f5c3a00`.
- [Complete reviewer reports](round_03/reviewer_report.md).
- [Annotated resolution proposals](round_03/goldfish_review_report.md).
- The implementation-readiness and codebase-details reviewers found no Blocker or Major; the style reviewer found 2 Majors.
- All 17 findings are PROPOSE FIX, grouped into 15 edit groups; none reopens a settled decision and none is churn.
- The coordinator verified the Hatchling build and gate in a temporary copy of the repository, and the validator on the default `python3`.
- Edit group G16 corrects a misplacement the coordinator made when applying round-two edit F14.
- Convergence within the cap now requires rounds 4 and 5 both to be clean.
- The human selected auto accept; all 16 edit groups were applied in one batch, with the `|` in the new D3 row escaped for table formatting.
- Post-resolution SHA-256: `beadbc1e5e7ce6c7b59a8e3107d3ad4714faf49edad5ae9aa87d64e9fac39aad`; the Detailed Implementation Plan spans lines 15-505.

### Round 4

- The user confirmed round 4 after round-three resolution.
- Input SHA-256: `beadbc1e5e7ce6c7b59a8e3107d3ad4714faf49edad5ae9aa87d64e9fac39aad`.
- [Complete reviewer reports](round_04/reviewer_report.md).
- [Annotated resolution proposals](round_04/goldfish_review_report.md).
- The implementation-readiness reviewer judged the plan ready to implement; it and the codebase-details reviewer found no Blocker or Major.
- The style reviewer found one Major: the source of `TurnRecord.session_index` on round-ending turns was ambiguous and untested.
- All 12 findings are PROPOSE FIX, grouped into 12 edit groups; none reopens a settled decision and none is churn.
- The coordinator verified that Ruff 0.17.5 format-checks Markdown but reformats only `python`-fenced code.
- Two consecutive clean rounds are no longer possible within the five-round cap; after round 5, the loop stops at the cap for a human decision.
- The human selected auto accept; all 12 edit groups were applied in one batch, with the callback-wrapping rule placed as a runner rule bullet.
- Post-resolution SHA-256: `713caa27483e578bfa27cbd559627e72fd01d5efe72f488ba672176f6115a20b`; the Detailed Implementation Plan spans lines 15-506.

### Round 5

- The user confirmed round 5 as the final round.
- Input SHA-256: `713caa27483e578bfa27cbd559627e72fd01d5efe72f488ba672176f6115a20b`.
- [Complete reviewer reports](round_05/reviewer_report.md).
- [Annotated resolution proposals](round_05/goldfish_review_report.md).
- The codebase-details reviewer reported no findings; the implementation-readiness reviewer reported one Nit; the style reviewer reported 2 Majors and 4 Nits.
- All 7 findings are PROPOSE FIX, grouped into 7 edit groups; none reopens a settled decision and none is churn.
- The coordinator verified that the locked Ruff is 0.17.5 and that its format check covers Markdown without editing files.
- The loop has reached its five-round cap without two consecutive clean rounds; a human decision is required after this resolution.
- The human selected auto accept; all 7 edit groups were applied in one batch, exactly as proposed.
- Post-resolution SHA-256: `5ab721dd7e7a20d0c7bebcd22e58c4426bf43f7f3bd4063b650c41fc6b7a5281`; the Detailed Implementation Plan spans lines 15-508.
- No fresh reviewer has assessed the round-five edits.

### Round 6

- The human chose to continue past the cap; round 6 is the first round beyond it.
- Input SHA-256: `5ab721dd7e7a20d0c7bebcd22e58c4426bf43f7f3bd4063b650c41fc6b7a5281`.
- [Complete reviewer reports](round_06/reviewer_report.md).
- [Annotated resolution proposals](round_06/goldfish_review_report.md).
- The implementation-readiness reviewer judged the plan ready to implement, with no Blocker or Major.
- Majors: committed review-record Markdown is format-checked without a failure instruction, and the D12 narrowed-passage list omitted two passages.
- All 15 findings are PROPOSE FIX, grouped into 14 edit groups; none reopens a settled decision and none is churn.
- The coordinator verified that no Markdown file in the worktree contains a `python` fence.
- The human selected auto accept; all 14 edit groups were applied in one batch.
- An application error that dropped part of the validator baseline bullet was corrected; an exact reverse-hash check confirmed no other change.
- Post-resolution SHA-256: `dbdb08a0e1e5986f8b6a7e65d9c08cb4f1e117aeb4e11cfd622ea76e0fc555bb`; the Detailed Implementation Plan spans lines 15-512.

## Cap Status

The loop ran all five rounds without two consecutive clean rounds, so it stopped at its cap.
There are no unaddressed findings: every finding from every round was accepted and applied.
Over the five rounds, 85 findings were raised; Blocker count was 0 in every round, and Major counts fell from 15 to 4, 2, 1, and 2.
In rounds 2 to 5, the implementation-readiness reviewer found no Blocker or Major and judged the plan implementable without design decisions.
Every Major from round 2 onward concerned wording precision, recorded evidence, verification commands, or test coverage; none required changing the specification, the module layout, or the author decisions.

On 2026-11-18 the human chose to continue past the cap.
Rounds continue with the same reviewers and rules; convergence still requires two consecutive clean rounds, and the coordinator asks before each further round.

## Convergence Rules

A clean round has no unsettled Blocker or Major and completion reports from all requested reviewers.
Clean status is decided before applying that round's edits.
Convergence requires two consecutive clean rounds, with a cap of five rounds.
After each resolution, the coordinator asks before starting the next round.

## Final Decision

On 2026-11-18, after round 6, the human developer chose to stop the loop and accept the plan as is.
The plan's status is now Approved.

| Measure | Value |
| :--- | ---: |
| Rounds run | 6 (5 within the cap, 1 past it) |
| Reviewer tasks completed | 18 of 18 |
| Findings raised | 100 |
| Blocker findings | 0 |
| Major findings by round | 15, 4, 2, 1, 2, 2 |
| Findings accepted and applied | 100 |
| Open findings | 0 |
| Consecutive clean rounds reached | 0 |

From round 2 onward, the implementation-readiness reviewer found no Blocker or Major and judged the plan implementable without design decisions.
The loop never produced two consecutive clean rounds, so convergence was not reached; acceptance is a human decision, not a convergence result.
The round-six edits were checked directly by the coordinator, including an exact reverse-hash check, but no fresh reviewer has assessed them.

The final approved plan SHA-256, after the approval-status header was added, is recorded in the plan's commit.

## Next Steps

1.  Commit the plan, these review records, and the `AGENTS.md` `docs/plans/` convention; Phase 0 step 0 requires them committed and a clean worktree.
2.  Hand the approved plan to implementation, starting at Phase 0.
