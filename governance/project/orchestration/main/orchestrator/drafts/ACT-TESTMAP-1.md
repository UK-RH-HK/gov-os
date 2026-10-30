# ACT-TESTMAP-1 — three record-only lines in the test map, so scoped verification is scoped (DEC-952)

From: the W2 orchestrator, 2026-10-30. Your act: one commit with `Role: owner`. Growing the test map's lists is your commit (P-SCOPE-RECORDS-1; W2-78 makes it durable).

## Why
- **The problem:** DEC-952 has every lead verify exactly what a scoped close selects (W2-66's `gov.close.select.plan`). On W2-61's worktree today, that selection comes out **full**, not scoped (`tools/scoped_plan.py`): `why_full: UNPLACED`.
- **The cause:** the orchestrator's own governance edits since the last green base are in no list of the test map:
  - `governance/project/briefs/LEAD-w2-common.md`;
  - `governance/project/prompts/w2-orchestrator.md`;
  - the nightly's scripts under `governance/project/orchestration/nightly/`.

  Every lead's verification, and every close, would therefore run in full until W2-78 lands.
- **Why these are safe as record-only:** no pytest test runs them. Prompts and briefs are text that sessions read. The nightly's scripts have their own `test_nightly.sh` and are frozen (DEC-946 item 9). `governance/project/orchestration/**.md` is already on the list.

## The change
In `governance/project/test-map.yaml`, under `record_only:`, after the line `  - "governance/project/orchestration/**.md"`, add:

```
  - "governance/project/briefs/**.md"
  - "governance/project/prompts/**.md"
  - "governance/project/orchestration/nightly/**"
```

## Your commands (a plain terminal, in `/home/usain/Dynamic-Agentic-Engineering-OS`, after today's close queue has ended)
1. Edit the file as above.
2. Check it: `PYTHONPATH=src python3 -m pytest -q tests/acceptance/W2-66/test_w2_66_live_test_map.py`.
3. Commit:
   - message: `ACT-TESTMAP-1 (DEC-952): prompts, briefs and the nightly's scripts are record-only`;
   - trailers: `Role: owner`, `Task: decision-record`, `Implements: DEC-952`.

## What to see
`tools/scoped_plan.py` on a lead's worktree no longer names these paths under `UNPLACED`.

## Rollback
Revert the commit.
