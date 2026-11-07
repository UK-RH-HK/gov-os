# PAT: the parallel-agents and memory test, one agent's brief (DEC-1087 (10), DEC-1089 (1)), 2026-11-07

Read `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/EMG-common.md` first: its rules hold.

You are one of two research agents working at the same time, each in its own git worktree, both searching the one
shared integration store. You are being observed as a worker would be: do the task as you normally would, and
report exactly what you saw. The CTO may land commits on `w2/integrate` while you work; that is part of the test.

- **Your worktree and branch:** given in the CTO's message (`WT`, `BRANCH`). Read and write only there.
- **Search:** `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<question>" --json` (the common brief's
  form). Save each search's output to a file under your `TMPDIR` with the Write-free form
  `--json > $TMPDIR/s<k>.json` is fine as one command; read what you need with the Read tool.
- **The task:** answer these three questions for a colleague, from the store plus your own worktree's files:
  1. What are the steps after re-pin window 4 is done, in order?
  2. What did the owner decide about keystone 7 and about usage pings?
  3. Which candidate-pool settings does `governance/project/retrieval.yaml` switch on?

  For each answer, cite file and line numbers **as they are in your own worktree** and quote the lines you rely on.
- **Also report, per search (a table):** the time (`date +%T`), the question, `ok`, `result.rerank.by`, whether both
  facets were available, the top 3 evidence items (path, start_line-end_line), and anything in the result that tells
  you which commit the store holds.
- **Then check every evidence item you cited:** open that file at that line range **in your own worktree** and say
  whether the lines there say what the search's evidence said (`same`, `shifted to <lines>`, `absent in my tree`).
- **Edit your own worktree:** write your findings to `docs/research/pat/<A or B>-findings.md` (create the folder),
  and commit it on your branch only:
  `git -C <WT> add docs/research/pat/<A or B>-findings.md` then
  `git -C <WT> commit -m "PAT <A or B>: findings" --trailer "Task: DAEO-sdxk" --trailer "Role: research" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- docs/research/pat/<A or B>-findings.md`.
- **Budget:** at most 10 searches; about 15 minutes. No test runs, no GPU work of your own, no other agents.
- **Return:** the twelve fields; in `discoveries`, say plainly whether anything misled you or could mislead a worker
  whose branch is behind integrate, and whether you could tell which commit the store answered from.
