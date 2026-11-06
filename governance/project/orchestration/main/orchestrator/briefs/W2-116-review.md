# W2-116's review: the integration store in the product, pass 1 (DEC-1087 (3))

You are an independent reviewer for the CTO. You read everything and change nothing: your one write is your record,
`.gov-runtime/scratch/orchestrator/reviews/w2-116.md` in the main tree. Read
`.gov-runtime/scratch/orchestrator/briefs/EMG-common.md` for the common rules.

**What to review:** branch `w2/W2-116` at `ca757c6107d5` (worktree `/home/usain/gov-os-worktrees/W2-116`) against
`w2/integrate` (which now holds `rebuild.yaml`'s `integration_store` line).
- **The ticket:** `.tickets/DAEO-f58b.md`. Judge against its pass-1 lines (S1, S3 widened to every worker, S4, S5)
  and the three failure lines, as its DEC-1087 (3) note and TESTS-READY note scope them. S2 is not this pass.
- **The engineer's evidence:** `docs/changes/W2-116-evidence.md`, with the hook it proposes for window 4 (a
  `reference-transaction` hook that runs `gov rebuild --integration w2/integrate` after every update of
  `w2/integrate`).
- **The CTO's tools it replaces:** `.gov-runtime/scratch/orchestrator/tools/refresh_integration_store.sh`,
  `seed_store.py`, `rebuild_pinned.sh`.

Check in particular:
- the link switches only after a build that succeeded, the semantic store recreated included;
- a search through the link during a build answers from the ready half, never `stale`;
- a killed build leaves the ready half and the link as they were;
- at an unchanged head the refresh does nothing;
- the refresh seeds from the ready half, so only what changed is re-embedded;
- `gov launch` sets `GOV_STORE` for every worker, and `gov retrieve` reads it only when no `--root` is given; a
  designer never reads a ticket worktree's store;
- the lock serialises two refreshes;
- the hook's line: does it run in the background without blocking the merge, does it log, and is it safe when two
  merges land close together;
- **the rebuild uses the code it runs under**, so after window 4 the store matches the pinned code;
- the engineer's stated risks: after a re-pin the first refresh rebuilds without the seed; a search started before a
  switch finishes on the old half.

**Facts the CTO has:** `gov accept W2-116` 20/20; the engineer's regression run of `tests/unit/rebuild`, `launch` and
`retrieve` with every row, 249 passed. Re-run what you need through the heavy slot. No GPU, no real model, never
`~/gov-os-worktrees/W2-00-store`.

**The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
`memory-verdict` or `memory-verdict-2` folder.

**DEC-1080:**
- read with the Read and Grep tools;
- one simple command per Bash call;
- no `cd … &&` chains and no `git -C`;
- one line before any command that will ask for permission.

**The judgement rules:** `governance/project/briefs/JUDGEMENT.md`, word for word. Each finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.

**Your record:** per KPI line of this pass (`success-1`, `success-3`, `success-4`, `success-5`, `failure-1` to
`failure-3`), what you checked and the findings. End with the fenced `verdict` block:
`{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`.
Then return the record's path and the verdict block. Est.: 1.5 hours.
