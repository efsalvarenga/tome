# EGM Review Record: Spec Version 1.1.3 (Editorial, D12 Alignment)

**Target:** [`docs/designs/001_tome_core_architecture.md`](../designs/001_tome_core_architecture.md) on branch `issue/13-spec-1-1-3-align-callback-cancellation`.
**Date:** 2026-11-27.
**Scope:** editorial delta only — the new Section 3.5 callback exception boundary, the aligned passages in Sections 3.5, 4 (Invariant 15), 6 (Edge Cases 6, 11, 14), and 7, the changelog row, the metadata table, the Section 8 subsections, and the README status line.
**Ground truth:** decision D12 and the narrowed-passage list in [`docs/plans/001_tome_core_architecture_plan.md`](../plans/001_tome_core_architecture_plan.md) (lines 56 and 64–68), Amendment A2 item 6 (lines 560–563), and [issue #13](https://github.com/efsalvarenga/tome/issues/13).
**Method:** three rounds of four zero-context Goldfish reviewers (`egm-style`, `egm-comprehension`, `egm-structural`, `egm-design`), each spawned read-only in a fresh context with the diff and the ground-truth documents.

## Round 1

| Reviewer | Verdict | Findings |
| :--- | :--- | :--- |
| egm-structural | Approved | 1 Nit |
| egm-style | Approved | 1 Nit |
| egm-design | Approved | 3 Nits |
| egm-comprehension | Revisions Required | 1 Major, 4 Nits |

Findings and dispositions:

- Double blank line after the new Section 3.5 boundary paragraph (structural-r1-1, style-r1-1, design-r1-1, Nit) — fixed by removing the extra blank line.
- Section 3.5 error sentences lacked the explicit `MemoryError`/non-`Exception` carve-out (design-r1-2, comprehension-r1-3, Nit) — fixed by adding "(wrapped unless it is `MemoryError` or not an `Exception` subclass)" to both sentences.
- The 1.1.2 heading asserted supersession while 1.1.3 is under review (design-r1-3, Nit) — fixed: "(proposed successor: Spec Version 1.1.3, under review)".
- "decision-D12" was an undefined, unlinked project identifier in the changelog and Section 8 (comprehension-r1-1, Major) — fixed by linking `[implementation plan](../plans/001_tome_core_architecture_plan.md)` at both places.
- "the error type" in Invariant 15 had an ambiguous antecedent (comprehension-r1-2, Nit) — fixed by naming `MechanicsError` explicitly.
- "the two Section 3.5 sentences" was ambiguous (comprehension-r1-4, Nit) — fixed: "for the umpire review and the failure resolver".
- README status line lacked an under-review qualifier (comprehension-r1-5, Nit) — fixed.

## Round 2

All round-1 fixes confirmed landed.

| Reviewer | Verdict | Findings |
| :--- | :--- | :--- |
| egm-structural | Approved | none |
| egm-design | Approved | none |
| egm-style | Approved | 1 Nit |
| egm-comprehension | Approved | 1 Nit |

Residual Nits accepted without change: the plan link lands at the file top rather than the D12 row (comprehension-r2-1; Markdown tables carry no row anchors), and a redundant version mention in the README parenthetical (style-r2-1; tightened in the same round).

## Round 3

| Reviewer | Verdict | Findings |
| :--- | :--- | :--- |
| egm-style | Approved | none |
| egm-structural | Approved | none |
| egm-design | Approved | none |
| egm-comprehension | Approved | 1 Nit |

Residual Nit accepted without change: the acronym "EGM" is not expanded inline (comprehension-r3-1); the Section 8 heading and the `docs/reviews/001_tome_core_architecture_egm/` path make the referent unambiguous, and `AGENTS.md` uses the same acronym.

## Verdict

Review verdict: Approved — two consecutive clean rounds (rounds 2 and 3) with no Blocker or Major findings.
The delta states D12 exactly, the Python 3.11 exception-hierarchy claims were verified empirically (`asyncio.CancelledError`, `KeyboardInterrupt`, `SystemExit` are `BaseException`-only; `concurrent.futures.CancelledError` and `MemoryError` are `Exception` subclasses), and the engine's `_invoke` implements the boundary as written.
Interface Contract 1.1.0, mechanics, rules, and tests are unchanged; `./scripts/lint.sh` passes on tracked files (273 tests).
Human developer sign-off on Spec Version 1.1.3 remains pending and is recorded as an unchecked item in the specification's Section 8.
