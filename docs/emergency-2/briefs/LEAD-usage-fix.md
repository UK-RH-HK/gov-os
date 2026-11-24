# Lead brief: `gov usage` prices wrong; fix before it lands (W2-207, on `e2/usage-per-repo`)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-24. **Read `docs/emergency-2/briefs/LEAD-COMMON.md` first: every rule there applies.** Decide, never ask (I-10).

## The fault
`e2/usage-per-repo` (worktree `/home/usain/gov-os-worktrees/E2-usage-per-repo`, head `e5d22d739`, not landed) built `gov usage daily | show` (UR-1 to UR-4 in `.tickets/DAEO-rt4s.md`; brief `docs/emergency-2/briefs/LEAD-usage-per-repo.md`). Its figures for 2026-11-24 are about four times too high (Gov OS $514, EXAMIN $131, ASMO OS $38, against about $112, $46 and $3.5 by the method below). The cause: `governance/project/usage-prices.yaml` holds prices no record supports (Opus 15/75/1.5/18.75), and it prices cache creation at one rate though transcripts split it into 5-minute and 1-hour writes (`usage.cache_creation.ephemeral_5m_input_tokens`, `ephemeral_1h_input_tokens`). UR-2 checks only that totals equal their rows, so nothing caught it.

The evidence-based table (`.gov-runtime/scratch/orchestrator/log/usage-breakdown-2026-11-22.md` line 3): a fit of all 85 model entries of the leads' own records (`log/leads/*.json`, `total_cost_usd` and `modelUsage`) is exact to 1e-14 at, per million tokens, **Opus: input 4, 5-minute write 5, 1-hour write 8, cache read 0.2, output 20; Sonnet: 2, 2.5, 4, 0.1, 10; Haiku: 0.1, 0.125, 0.2, 0.01, 0.5** (Haiku's 1-hour price assumed 1.6x its 5-minute one). Re-derive it yourself from today's lead records before you use it.

## What (KPI lines, added to the same `## Fix:` section of `.tickets/DAEO-rt4s.md`)
- **UR-5 Prices that match the plan's own counting.** The price table has separate 5-minute and 1-hour cache-write prices and holds the figures the lead records reproduce; a test computes, from planted transcripts and a planted lead record, the cost of a lead session and finds it equal to the record's `total_cost_usd` within 1 %; and on this machine, `gov usage daily` for 2026-11-24 gives, for each finished lead of that day, a cost within 1 % of its `log/leads/<name>.json` `total_cost_usd` (report the comparison).
- **UR-6 The price table found from anywhere.** `gov usage` works from any repository root: the table ships with the product (a copy in the package or the kit) and a repository's own table, when present, overrides it.
- **UR-7 Only real repositories.** Transcripts of temporary folders (paths under `/tmp/`, pytest temporaries) are left out of the repository rows and counted on one `temporary` line.
- `usage` added to the recorded command list (`RECORDED_GOV_COMMANDS` in `src/gov/check/commands.py`, with its test); the CTO approves that by this brief.

The test designer writes UR-5 to UR-7's acceptance cases in `tests/acceptance/W2-207/` (its README rows), red on the branch's head; the engineer builds. Never read a real transcript in a test.

## Where
The same worktree and branch; `git merge w2/integrate` first.

## Green
`gov accept W2-207` and exactly the impact-selected suites (`PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-rt4s=e2/usage-per-repo --onto w2/integrate --select`), both through the heavy slot (DEC-1244 X-1). I-21 is fixed on `w2/integrate` (after the merge it should be green); I-22's two W1-35 import errors are not yours. Check the acceptance trailers (LEAD-COMMON).

## Return
Branch and head; UR-5 to UR-7 with tests and result; the table as derived (and how); the per-lead comparison for 2026-11-24 (lead, record cost, computed cost); `gov usage show --date 2026-11-24` run against the main tree (`--root /home/usain/Dynamic-Agentic-Engineering-OS`); the selected suites' summary lines; reds not yours.
