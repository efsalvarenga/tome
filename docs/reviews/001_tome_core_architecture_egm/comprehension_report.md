## What this proposes

TOME is a transport-neutral simulation engine that combines narrative proposals with randomized cues and peer voting.
Each turn samples a TriO tier and two sparks, checks grounding and vote shifts, optionally accepts umpire rejections, and resolves 2d6 plus a clamped modifier against 7.
Success adds the proposal to canon; Failure requires an umpire-resolved consequence instead.
Completed runs return final state and ordered audit records atomically, while callers own narrative adapters, human interaction, and persistence.

## How the existing system works, per this document

The described engine maintains canon facts, actor identities/names/agendas, and turn/round counters; actors follow a fixed run-local order and immediately observe preceding turns' additions.
Earlier designs included persistent posture/step-dice and UI, hosting, access-control, and persistence features that are now removed or deferred.
The document does not establish which historical features were implemented, so this paraphrase describes its stated design rather than verified implementation behavior.

**Status:** Completed
**Stage:** 6, Comprehension Test
**Date:** 2026-11-13
**Target:** [TOME core architecture](../../designs/001_tome_core_architecture.md), lines 1-1052
**Specification:** 1.1.1
**Interface contract:** 1.1.0
**Execution:** Fresh general-purpose subagent reading the official comprehension persona
**Additional context:** None
**Document standard:** None

## Complete Reviewer Findings

### egm-comprehension-1-1: Meaning of superseded narrative conditions

**Severity:** Major
**Affected scope:** Sections 2.3-2.5 and 3.1; Section 4, Invariant 6

Canon's interpretation when narrative conditions change is unclear.
A world-change statement may alter an actor's condition or capability, but resolution only appends facts, and existing facts remain reusable grounding references.
For example, "Actor A has capability X" and a later "Actor A loses capability X" would both remain mechanically valid anchors.
The document does not explain whether canon represents historical assertions or currently applicable truths, how superseded conditions should be interpreted, or who makes that determination.
Clarifying that meaning would connect the narrative-only condition model to subsequent proposal generation and peer reasoning without requiring additional mechanical trackers.

### egm-comprehension-1-2: Blanket mapping-return rule conflicts with a list-returning callback

**Severity:** Nit
**Affected scope:** Section 3.5, introductory callable-return rule and `UmpireReview` signature

The statement that "each callable returns a plain mapping or an equivalent model" conflicts with `UmpireReview`, which returns `UmpireRejection[]`, including `[]`.
The signature and subsequent explanation make the intended list return understandable, but the blanket rule gives contradictory integration guidance.
Limit the mapping/model rule to returned objects, or explicitly distinguish list-returning callbacks.

No section was wholly un-paraphrasable.
There were no Blocker findings.

## Reviewer Provenance

Files actually read:

- Official plugin `agents/comprehension.md` under `/Users/Estevao.alvarenga/.vscode/agent-plugins/github.com/google/elephant-goldfish-model/`.
- [Specification](../../designs/001_tome_core_architecture.md): Complete assigned lines 1-1052, with truncated reads completed.

**Limitations:** Document-only review.
No linked files, historical reviews, implementation, project documentation, or session artifacts were read.
No files were modified, and no tests, compilation, network access, or delegation occurred.
