# The orchestration record (Policy 1, DEC-819)

Everything that is context goes into git, so every worktree and session sees the same truth. This folder holds the
committed copy of the orchestration context that lives, while work runs, in git-ignored scratch folders.

| Folder | What it holds | Copied from |
|---|---|---|
| `main/orchestrator/` | The orchestrator's checkpoint (`CHECKPOINT.md`, its RESUME HERE section first) and its archive (`CHECKPOINT-ARCHIVE.md`); the briefs given (`briefs/`); run logs and returns (`log/`); decision packages (`PR-*.md`); notes and the orchestrator's scripts and tools | `.gov-runtime/scratch/orchestrator/` in the main tree |
| `main/checkpoints/` | The scratch checkpoint series (automatic checkpoints at stop and compaction, by ticket) | `.gov-runtime/scratch/checkpoints/` in the main tree |
| `worktrees/<W2 id>/` | A ticket lead's records: its briefs, its workers' logs and returns, its lead checkpoint, probe drafts, its checkpoint series | `.gov-runtime/scratch/` in that ticket's worktree |
| `sessions/` | Session summaries, one per compaction or session end | written by the orchestrator |

The other kinds of context live where they did: the standing rules in `governance/project/prompts/w2-orchestrator.md`
and `docs/plan/WAVE_2_WBS.md` §0; the brief templates in force in `governance/project/briefs/`; plans in `docs/plan/`;
assessment reports in `docs/assessment/<yyyy-mm>/`; audit reports in `docs/audit/`; committed ticket checkpoints in
`docs/checkpoints/<ticket>/`; decisions in `docs/DECISION_REGISTER.md`.

**How it is kept.** `sync_context.py` copies new and changed files, never deletes a copy (a removed worktree's records
stay), and never copies what Policy 1 keeps out: secrets and keys (gitleaks scans every copy; a flagged file is removed
again and named), the held-out material, derived context packets, indexes and stores, model files, wheels, archives,
compiled files, binary files and files over 2 MB, and anything git ignores. The orchestrator runs it at every
checkpoint and before a worktree is removed, then runs gitleaks over the staged set and commits (w2 prompt §15).

**Read it as a record.** The live files are the scratch ones, where the hooks read them; a copy here is never edited by
hand. `governance/project/**` is not indexed for retrieval (its namespace has no memory class), so these copies do not
crowd the index; read them by path, or with git.

**First copy:** 2026-10-19, 5,673 files, 28.4 MB, gitleaks clean (the vendored `ccusage` archive, two wheels and one
compiled file left out by rule).
