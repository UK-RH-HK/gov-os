# The orchestration record (Policy 1, DEC-819; its place since DEC-887)

Everything that is context goes into git, so every worktree and session sees the same truth. The orchestration
context lives, while work runs, in git-ignored scratch folders, and its committed copy is the orchestration record.

**Since 2026-10-21 (DEC-887, owner, P-REC-1 (a)) the raw record lives on its own branch, `record/w2`.** Before that,
it filled 73 % of this repository's checked-out tree, and the test suites that copy the tree paid for it on every run.
The branch is checked out once as the worktree `/home/usain/gov-os-worktrees/W2-00-record/`, under the same paths as
here (`governance/project/orchestration/…`). It never merges into `w2/integrate` or `main`; the owner's daily push
carries it beside `w2/integrate`. Its first commit (`0412d69e`) imported the record from `w2/integrate` at `206974e1`,
tree for tree: the folder's tree object `46610514` is the same on both branches. The record's earlier history stays in
`w2/integrate`'s history, unchanged.

**What stays here, in the main tree, for agents to search:**

| Path | What it holds |
|---|---|
| `README.md` | this file |
| `sync_context.py` | the copy script |
| `packages/` | the decision packages brought to the owner |
| `sessions/` | session summaries, one per compaction or session end |
| `main/orchestrator/CHECKPOINT.md` | a copy of the orchestrator's checkpoint, its RESUME HERE section first, refreshed with decision-record commits (`sync_context.py --main`) |

**What lives on `record/w2`:**

| Path on the branch | What it holds | Copied from |
|---|---|---|
| `main/orchestrator/` | the orchestrator's checkpoint and its archive; the briefs given (`briefs/`); run logs and returns (`log/`); drafts; notes and the orchestrator's scripts and tools | `.gov-runtime/scratch/orchestrator/` in the main tree |
| `main/checkpoints/` | the scratch checkpoint series (automatic checkpoints at stop and compaction, by ticket) | `.gov-runtime/scratch/checkpoints/` in the main tree |
| `worktrees/<W2 id>/` | a ticket lead's records: its briefs, its workers' logs and returns, its lead checkpoint, probe drafts | `.gov-runtime/scratch/` in that ticket's worktree |
| `packages/`, `sessions/`, `README.md` | copies of what this folder holds | this folder |

**How to read it:**
- `git show record/w2:governance/project/orchestration/<path>` for one file;
- `git ls-tree -r --name-only record/w2` for the list;
- or open the files in the record worktree, read only.

**How it is kept.**
- `sync_context.py` copies new and changed files into the record worktree, and `--commit "<subject>"` commits them on `record/w2` after gitleaks over the staged set. So these commits never move `w2/integrate`'s head, and no close meets a stale store, a forced rebuild or a dirty tree because of them.
- It never deletes a copy: a removed worktree's records stay.
- It never copies what Policy 1 keeps out:
  - secrets and keys (gitleaks scans every copy; a flagged file is removed again and named);
  - the held-out material;
  - derived context packets, indexes and stores;
  - model files, wheels, archives, compiled files, binary files and files over 2 MB;
  - folders that ignore themselves, and a suite's raw output under a log folder;
  - anything git ignores.

**Read it as a record.** The live files are the scratch ones, where the hooks read them; a copy is never edited by
hand.

The other kinds of context live where they did:
- the standing rules in `governance/project/prompts/w2-orchestrator.md` and `docs/plan/WAVE_2_WBS.md` §0;
- the brief templates in force in `governance/project/briefs/`;
- plans in `docs/plan/`;
- assessment reports in `docs/assessment/<yyyy-mm>/`;
- audit reports in `docs/audit/`;
- committed ticket checkpoints in `docs/checkpoints/<ticket>/`;
- decisions in `docs/DECISION_REGISTER.md`.

**First copy:** 2026-10-19, 5,673 files, 28.4 MB, gitleaks clean. **Moved to `record/w2`:** 2026-10-21, 8,249 files, 49.3 MB.
