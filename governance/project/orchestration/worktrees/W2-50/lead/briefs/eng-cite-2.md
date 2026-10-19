# Brief: engineer — DAEO-kl5e (W2-50), FULL: the CIT-E's history of the two failed reviews (DEC-752)

You are a fresh engineer. Ticket: DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`, at head `6d5ad6d0`. The change is implemented, repaired twice and verified green. Your one task: add one section to `docs/changes/W2-50-CIT-E.md` and commit it. You change no code, no test and nothing else in that file.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-kl5e`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-50` and `w2/W2-50`), `git log --oneline -1` (expect `6d5ad6d0`) and `git status --short` (expect empty). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- The guard's hook in your session runs **this worktree's** `src/` (DEC-751 item 6). You change nothing under `src/`, so this only means: if the guard refuses you, the refusal is this worktree's code speaking; do not work around it.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`. Never read `.claude/settings.json` or `.claude/settings.local.json`, here or anywhere. Nothing under `~/.claude/` is read. Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path. Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never create, write, list or remove anything in the real `~/gov-os-runs/` (it does not exist) or the real `~/gov-os-worktrees/`. You run no tests in this task.
- Never copy the repository or a folder of it anywhere. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673). You may copy the content of single named files only.
- The guard refuses here-documents and unresolvable variables in Bash write targets: edit with the Edit tool and literal absolute paths. No subagents that write. Install nothing. No push, merge, rebase or tag. Never write `.gov-runtime/**`: the two draft records you read there stay as they are, uncommitted. Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause`. Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2).
- Refused twice for the same call: stop and say so; no third try (AR-6).
- If the guard refuses something you need, do not work around it: return it as a package. On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.

## The owner's decision behind this task

DEC-752 item 2 (owner, 2026-10-17; staged for the owner's commit, not in this worktree's register — name it as written here): one more independent review of W2-50's repair. Only that review's pass record is committed under `docs/probes/DAEO-kl5e/`. **The two fail records go into the CIT-E as history.** That is your task.

## What you read

- `docs/changes/W2-50-CIT-E.md` in full (its §5, §6 and §7 already describe the two repair rounds).
- The two draft fail records, each a single named file: `/home/usain/gov-os-worktrees/W2-50/.gov-runtime/scratch/lead/probes/PR-DAEO-kl5e-round-1.md` and `/home/usain/gov-os-worktrees/W2-50/.gov-runtime/scratch/lead/probes/PR-DAEO-kl5e-round-2.md`.
- `git log --format='%h %s%n%b' 74403441^..HEAD` for the commits.

## The facts the lead gives you (what was done with each finding)

**Review 1** (probed `b7981b0faf3cad33b596cdd330cd1a339fad5d8c`, reviewer session `9ffac555-e15e-4654-ba56-e68b45435bb3`, judgement fail):
1. A project inside the own folder lost every in-project rule — repaired: tests `72263054`, repair `86aa805c`, CIT-E `0bbada97` (§6 finding 1).
2. Glob characters in `external-ref` widened the sandbox write list — repaired in the same commits (§6 finding 2).
3. Two tickets naming the same folder shared it — repaired in the same commits (§6 finding 3).
4. A `ticket-lead` session's subagent of another role type reaches the folder — residual: the guard's model of the acting role, as inside the repository; not fail-open under DEC-743 item 7 as the second review was briefed.
5. The own folder's path can be written as a file — residual: a later launch then started without an own folder (CIT-E difference 7, to W2-21; DEC-751 W-2 (b) makes the silent start a warning row for W2-21). Since `df5f1e50` a file in the folder's place also gives no folder (§7).
6. `rmdir` of the root with an unresolvable argument — residual: CIT-E difference 5, to W2-09 (§5).
7. Bash forms the guard never judged (`find -delete`, `env rm`, `git clean`, `rsync --delete`, `dd of=`, `truncate`, an interpreter's `-c`) — residual, pre-existing, the guard's Bash forms (W2-09).
8. Two cases stricter than needed (a link in the own folder resolved through for `rm`; a secrets-check loop on a link to a HOME that holds the project, which fails closed and existed before) — residual, not fail-open.

**Review 2, the second and last under DEC-413** (probed `f9277098f60c747df9c52efb134dd684cd064f0c`, reviewer session `1e0c179d-c135-4a63-a5a3-e65980db433f`, judgement fail):
1. Another project's ticket of the same name got this repository's ticket folder — decided by DEC-751 item 1 (P-A (a)); repaired: tests `e58081be`, repair `df5f1e50`, CIT-E `8a3c27e9` (§7 finding 1, the marker).
2. A clone's own secrets check failed open for a linked store inside the clone — decided by DEC-751 item 2 (P-B (a)); repaired in the same commits (§7 finding 2).
3. A FIFO among the ticket files hangs `gov launch` and makes the guard refuse writes outside the project until its deadline — residual row (DEC-751 item 5); fails closed, availability only.

Neither fail record is committed; DEC-752 item 2 keeps them out of `docs/probes/`. A further independent review (DEC-752 item 2) follows this commit; its pass record, if it passes, is the only probe record committed.

## What you write

Append one section at the end of `docs/changes/W2-50-CIT-E.md`, headed `## 8. The two failed reviews (history, DEC-752)`. For each review: its probed commit (full id), the reviewer session, its judgement, each finding (as described behaviour, as in the record — copy or summarise the record's own words) and what was done with it (repaired in which commits, or a residual and where it goes). Add one closing line: the records stay uncommitted drafts by DEC-752 item 2, and the extra review follows. A table per review or a numbered list, as you find clearer. Change nothing else in the file (frontmatter included, unless the schema `template/governance/kernel/schemas/change-execution-record.schema.json` requires it; you may add `DEC-752` to `decisions_carried` only if the schema accepts it — check, and say what you did). Quote no code beyond a name.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only that one file, with the trailers in the final block:

    git add docs/changes/W2-50-CIT-E.md
    git commit -m "W2-50 (DAEO-kl5e): the CIT-E's history of the two failed reviews (DEC-752)" --trailer "Task: DAEO-kl5e" --trailer "Role: engineer" --trailer "Implements: DEC-728" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -2`, `git log -1 --format=%B`, `git show --stat HEAD` and `git status --short`.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | LEAD_CHECKPOINT | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

In those fields give: the commit hash and trailers; the lines added; what you did with the frontmatter; the `gov.__file__` line. Refused twice for the same call: stop and say so.
