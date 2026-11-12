---
type: probe
task: DAEO-ifgf
round: 3
reviewer_session: b6b54bcf-73ca-499c-88e8-ae8004a44b76
implementer_session: bc2586bf-4089-4ab5-b83c-826f8b6fd3c7
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: pass
probed_commit: b24361b5159e378aa1092a5f4d61aaa4ace8a937
decisions_applied: DEC-1154, DEC-1149, DEC-802, DEC-1010
---

# Probe record: W2-121b (DAEO-ifgf), the narrow check of the template default (DEC-1154): PASS

A fresh Independent Auditor session (`b6b54bcf-73ca-499c-88e8-ae8004a44b76`, claude-opus-5-5, effort high, read-only) checked only the change the owner decided
after the review (DEC-1149 (2): the template default `working_size_bytes` 805,306,368 B and its unit case), as DEC-1154 asks;
round 2's record is `PR-DAEO-ifgf-round-2.md`. The reviewer's blocks are copied unchanged; the CTO commits this record.

# W2-121b (DAEO-ifgf): narrow check of the template default (DEC-1149 (2))

task: DAEO-ifgf
decisions: [DEC-1149, DEC-802, DEC-801, DEC-808, DEC-1010]
probed_commit: b24361b5159e378aa1092a5f4d61aaa4ace8a937
base: dae1c10e0392 (FULL review, round 2 pass)
KPI: w2-121b-default-check

## What I probed and found sound
1. **Scope of the diff** (`git diff dae1c10e0392 b24361b51 -- src/ tests/`):
   - Apart from two files, the diff is the merge of w2/integrate. Every merged file is byte-identical to integrate's copy at `48ef8cf66`, and none overlaps the branch's own changes.
   - The reviewed W2-121b files did not change across the merge (`git diff dae1c10e0392 fa608e568` over them is empty).
   - After the merge, only `src/gov/resources/config.py` changed: one hunk, the `working_size_bytes` value, date and source in `template()`.
   - The only other change is one new unit case, `tests/unit/dispatch/test_w2_121b_config_default.py`, plus the probe record (outside `src/` and `tests/`).
2. **Value, date and source:**
   - `config.template()` gives `working_size_bytes` = 805306368, dated 2026-11-12, with the source "DEC-1149 (1), (2): 0.75 GiB per live session, from the lead-memory ledger (ACT-P95-1)".
   - The unit case asserts all three. A standalone copy fails on the reviewed `config.py` (`2191601664 != 805306368`) and passes on the head.
3. **No regression** (all runs through `heavy_slot.sh`, scratch HOME and TMPDIR):
   - `tests/unit/dispatch`: 113 passed, nothing deselected.
   - `gov accept W2-121b`: pass on success-1 to success-4 (10, 12, 13, 14) plus 3 unmapped cases, 52 passed, 0 failed, 0 skipped.
   - Extra: `tests/unit/resources` and `tests/unit/launch` (gate fixtures built from `template()`): 539 passed, 86 real-model or timing cases deselected.

## Notes, not findings
- `tests/unit/dispatch/conftest.py` puts the worktree's own `src` first, so a revert probe must run the case outside that folder.
- What would reverse this pass:
  - a byte difference between a merged file and integrate's copy at `48ef8cf66`;
  - a second change inside `config.py`;
  - a failure of the dispatch unit tests or of `gov accept W2-121b` on `b24361b5`.

## Findings
None.

The tree was clean when I finished (`git status --porcelain` empty). I wrote nothing outside my TMPDIR.

```verdict
{"kpis": [{"kpi": "w2-121b-default-check", "verdict": "pass", "findings": []}]}
```
