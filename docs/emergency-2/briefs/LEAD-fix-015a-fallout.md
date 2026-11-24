# Lead brief: fix-015a-fallout, the reds the straight-through full run found after `fixes-015a` (fixes under their owning tickets)

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it (node on PATH; `PYTHONPATH=<worktree>/src:<worktree>/src/gov/close/pytest_plugin`;
`GOV_TESTS_OPTIN=weekly` for the weekly tier; the test designer's reading bounded). Name: `fix-015a-fallout`; worktree
`/home/usain/gov-os-worktrees/E2-fix-015a-fallout`, branch `e2/fix-015a-fallout` from `w2/integrate` (it holds the W2-56
fix). **Do not merge.** Every helper Sonnet; this lead runs medium. It blocks release 0.1.5: as fast as it can be green,
working the groups in parallel helpers where their files do not meet. Decide, never ask (you run as `claude -p`).

**The input:** `docs/emergency-2/integration/REDS-0.1.5-f511bb6c0.txt`: 70 failed and 25 errors of a straight-through
full run (`pytest tests -n 4`, weekly tier, in the main tree at `f511bb6c0`, not the nightly's clean clone). Groups:
W1-46 (30), W2-18 (25 errors), W2-153 (13), W2-56 (7: **already fixed** on `w2/integrate` by `fix-w2-56`, skip), W2-197 (6),
W2-60b (3), W2-208 (2), W1-01 (2: **the owner's decision**, seven `acceptance_exemptions` entries; skip, do not touch the
path map's exemptions), unit/memaudit (1), W2-54 (1), W2-200 (1), W2-184 (1), W2-13 (1), W1-39 (1), W1-19 (1).

**What changed under them** (most are fallout of `fixes-015a`, landed `461c214a5`, whose lead tested only a subset):
F1 (every `gov launch` passes `--strict-mcp-config`, an `--mcp-config` from the role's MCP list and
`ENABLE_CLAUDEAI_MCP_SERVERS=false`; the kit's settings carry `disableClaudeAiConnectors`; doctor reports a missing key),
F11 (generated agent files regenerated with no unfilled slot), F13/F14/F19 (helpers forced to Sonnet; leads Sonnet at
medium; any model the rubric does not give replaced; C3 Opus and C0 Haiku retired, DEC-1225), F15 (the figure's stamp),
F18 (doctor checks the pytest plugins as packages), and W2-209 slice (a) (the record's `optin`).

## The work, per failing case
1. Reproduce it on your branch, through the slot, the way the nightly does (in a scratch clone of the branch's HEAD
   when the case reads the repository's own tree; W2-54's context-reproducibility case needs the store built from HEAD:
   `gov rebuild --root <clone>` first). A case that passes there is **environment** (this run's main tree): list it with
   the reason, change nothing.
2. A case red for a change DEC-1225, DEC-1232 (6), DEC-1236 (2) or F11/F15/F18 made on purpose is a **stale test**: the
   independent test designer revises it to the rule in force, with a `Rewrite-Reason` naming the decision inside the
   final trailer paragraph; no assertion's point is dropped (if the point itself is retired, say which decision retired
   it).
3. A case red because the code does something no decision asked for is a **product bug**: the test stays (it is the
   failing test), the engineer fixes the code.
4. Record each fix in its owning ticket (`## Fix:` section; find with `grep -l "^wbs_id: W.-N" .tickets/*.md`).

## Green and return
Every listed group green on your branch (W1-01 and W2-56 excepted), plus `tests/unit/launch`, `tests/unit/doctor`,
`tests/unit/adapters`, `tests/unit/optin`. Return: branch and head; a table, one row per group: environment / stale test
/ product bug, the decision or cause, the commit; the pytest summary lines; reds not yours.
