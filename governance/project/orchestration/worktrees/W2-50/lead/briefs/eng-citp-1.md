# Brief: engineer — DAEO-kl5e (W2-50), FULL: commit the approved CIT-P (DEC-738 item 1, DEC-743 item 9)

You are a fresh engineer. Ticket: DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`. Your one task: commit the owner-approved change-impact proposal at `docs/changes/W2-50-CIT-P.md`, the draft's text word for word followed by a closing section with the owner's answers, in a commit of its own. You write no code, no test and nothing else.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-kl5e`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-50` and `w2/W2-50`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`. Never read `.claude/settings.json` or `.claude/settings.local.json`, here or anywhere. Nothing under `~/.claude/` is read. Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path. Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never create, write, list or remove anything in the real `~/gov-os-runs/` (it does not exist; nobody creates it in this run) or the real `~/gov-os-worktrees/`.
- Never copy the repository or a folder of it anywhere; copy single named files only. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- The guard refuses here-documents and unresolvable variables in Bash write targets: use the Write and Edit tools or a plain command with literal absolute paths. No subagents that write. Install nothing. No push, merge, rebase or tag. Never write `.gov-runtime/**`. Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause`. Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2).
- Refused twice for the same call: stop and say so; no third try (AR-6).
- If the guard refuses something you need, do not work around it: return it as a package. On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.

## The owner's decision (DEC-743, 2026-10-17; staged for the owner's commit, not in this worktree's register)

The owner approved W2-50's CIT-P, apply now, within DEC-728, and decided (DEC-738 item 1) that the engineer — the ticket's `role:` — commits it word for word, with the owner's answers, before any code.

## What you do

1. Copy the draft, unchanged, to the target, with one plain command:
   `cp /home/usain/gov-os-worktrees/W2-50/.gov-runtime/scratch/lead/W2-50-CIT-P.draft.md /home/usain/gov-os-worktrees/W2-50/docs/changes/W2-50-CIT-P.md`
   (if this is refused, read the draft in full with the Read tool and write it with the Write tool, character for character).
2. Check it: `head -n 318 /home/usain/gov-os-worktrees/W2-50/docs/changes/W2-50-CIT-P.md | sha256sum` must print `776d1338657cc22e9e5515eb2f58983cf934c6f85288c6b07610d3a7253410a5`. If it does not, stop and say so.
3. Append, with the Edit tool after the file's last line, one blank line and then exactly this section (nothing else changes in the file; the draft's frontmatter and text stay as they are):

```
## The owner's answers (DEC-743, 2026-10-17)

The owner approved this proposal on 2026-10-17 (DEC-743): apply now, within DEC-728.

1. **The CIT-P is approved, with readings R1 to R8 as written.**
   - R7 is scoped to the root: `rmdir` is judged for `~/gov-os-runs` itself, not everywhere.
   - R2's step (the launcher makes the own folder before the session starts) is approved, one step beyond "the
     sandbox write list only".
2. **W2-50 stays within DEC-728.** A session writes only under its own ticket's folder of `~/gov-os-runs`. Nothing
   there is indexed or scanned by this repository. The workbench and other worktrees stay refused.
3. **§6.1 (i).** This ticket's `allowed_paths` now hold `src/gov/secrets/__init__.py`, for the link rule only: a link
   from `.gov-runtime/` into `~/gov-os-runs` is not followed. W1-15's B4 stays green.
4. **§6.2** (the guard does not judge `git clone` destinations) is row W2-H055, triaged to W2-09, which edits
   `decide.py` after this ticket. Not this ticket's work; never widen it here.
5. **§6.3** (whether a launched session's Write and Edit reach the own folder) is row W2-M359, triaged to W2-21. Not
   this ticket's work.
6. **§6.4.** The own folder is open only while the ticket is `in_progress` (stricter).
7. **§6.5.** `ticket-lead` is not among "any role" (stricter; DEC-434 unchanged).
8. **§6.6** (CAP-58's text) is row W2-L342, Wave 3. Not this ticket's work.
9. **The engineer commits the CIT-P word for word, with these answers, before any code** (DEC-738 item 1).
```

4. Check again: step 2's command still prints the same hash, and `git diff --stat` / `git status --short` show only `docs/changes/W2-50-CIT-P.md` (new, untracked).

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only that one file, in a commit of its own, with the trailers in the final block:

    git add docs/changes/W2-50-CIT-P.md
    git commit -m "W2-50 (DAEO-kl5e): the approved CIT-P, word for word, with the owner's answers (DEC-743)" --trailer "Task: DAEO-kl5e" --trailer "Role: engineer" --trailer "Implements: DEC-728" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

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

In those fields give: the commit hash and trailers, both hash checks, and the `gov.__file__` line. Refused twice for the same call: stop and say so.
