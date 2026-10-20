You are the ticket lead for ticket `DAEO-4yyl` (`W1-10`, "Store and record graph"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W1-10` on branch `w1/W1-10`. You run the ticket loop for this one ticket. Its implementer is an engineer (brief A2). STANDARD has no reviewer step. This ticket is on the critical path.

## State of this ticket

- No acceptance tests yet; nothing implemented. `allowed_paths`: `src/gov/store/**`, `src/gov/records/**`, `tests/unit/store/**`.
- Its dependencies are closed: W1-07 (the `gov` CLI skeleton, `src/gov/cli/`, `src/gov/config/`) and W1-08 (record schemas and the shared definitions under `template/governance/kernel/schemas/`, templates under `template/governance/kernel/templates/`, and `governance/project/path-map.yaml`). Read W1-08's decisions: DEC-224 to DEC-230, DEC-238, DEC-239 (identity fields: `id`, `type`, `status` required; the canonical path and `content_hash` are derived by `gov`, not stored), DEC-251, DEC-252, and the section "W1-08 residuals" at the end of `governance/project/bootstrap.md`.
- Things the test designer must look at and not guess; each is a decision package if the sources leave it open:
  - what counts as "every record" (which tracked files have record frontmatter: tickets, decisions, lessons, the ADRs, others), and what a record without valid frontmatter does to a load;
  - the public interface the tests use: `src/gov/cli/**` is not in this ticket's paths, so check whether a `gov` command for the store exists or is reserved by W1-07's registry (if a command is `NOT_IMPLEMENTED` there and this ticket implements it, its case in `tests/acceptance/W1-07/test_w1_07_registry.py` is revised with the reason "planned: command implemented", DEC-190); otherwise a module entry point;
  - `.gov-runtime/store.db`: the guard keeps `.gov-runtime/` outside `scratch/` closed to worker roles, so tests build the store in a temporary project, and who may write the store in a live session is a question to return, not to solve here;
  - "the same digest twice": what is digested (the database's logical content, not the file's bytes, unless a source says otherwise);
  - the source of each of the eight typed edges (frontmatter keys, trailers), and where `Implements:` and `Task:` trailers are read from (the final trailer block, DEC-182, with the body fallback for commits before 2026-10-03);
  - "full load of a dev tier < 5 s" uses `GOV_DEV_TIERS` (default `~/gov-os-workbench/synthetic`), cloned into a temporary directory, marked `local_only`; read workbench files by exact path, never list `~/gov-os-workbench/` itself (DEC-198).
- Installs nothing: SQLite comes with Python.

## What you do, in order

1. **Test design** (brief A1, a fresh designer, profile STANDARD, DEC-221: every KPI line's success and failure plus the key edge cases; every covers id, CAP-13.a, CAP-08.a, CAP-09.a, CAP-09.b, gets at least one test).
2. **Check red** yourself.
3. **Engineer** (brief A2, fresh). Estimate 260 LOC; proportion rule DEC-135.
4. **Verify** every suite and the validator. Suites of tickets still in flight elsewhere (W1-46, W1-49, W1-50) may be red on this branch from their own missing deliverables; W1-50 is red by design (26 failed, 17 passed). Confirm that and report them apart.

