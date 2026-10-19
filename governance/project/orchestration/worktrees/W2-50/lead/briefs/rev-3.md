# Brief: reviewer (FULL, read-only) — DAEO-kl5e (W2-50), the extra independent review (DEC-752 item 2)

You are a fresh reviewer. Ticket DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL, is implemented and repaired in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`, at the head `19a4e9fd20b9562c24b1824076c67403fb323db5` (check it with `git rev-parse HEAD`), and its acceptance tests pass. You probe that head for behaviour the tests miss. You write nothing.

The change loosens the guard (DEC-728), so the owner allowed one more independent review beyond DEC-413 (DEC-752 item 2, owner, 2026-10-17; staged for the owner's commit, not in this worktree's register). Two earlier reviews failed; their findings and what was done with each are in `docs/changes/W2-50-CIT-E.md` §8. This review is of the whole ticket's final code, with its focus on the last repair (`df5f1e50`, DEC-751).

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-kl5e`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-50` and `w2/W2-50`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- The guard's hook in your own session runs **this worktree's** `src/` (DEC-751 item 6): the code you probe also confines you. A refusal you meet may be that code speaking; say so, and never work around it.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. You write nothing, so no commit of yours will exist: return when your findings are complete.
- No `git checkout` of another commit, no `git reset`, no `git clean` in this worktree. Write no file of the repository and make no commit; `git status --short` must be the same before and after your probe (show both). No subagents that write. Install nothing. No push, merge, rebase or tag.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nothing under `~/.claude/` is read.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **The real scratch roots are never touched.** You never create, write, list or remove anything in the real `~/gov-os-runs/` (it does not exist; nobody creates it in this run), the real `~/gov-os-worktrees/` or the real `~/gov-os-workbench/`. Every probe that runs the code under test gives it a temporary `HOME` in your session's temporary folder, and a `TMPDIR` that is a sibling of that home, never a parent of it (the guard allows the temp folder, so a home inside it proves nothing). Run no `local_only` live-launch case and start no real `claude` session. Before you return, run `test -e ~/gov-os-runs && echo PRESENT || echo ABSENT` and quote the output: it must print ABSENT.
- Never copy the repository or a folder of it (a recursive copy, a sync, an archive, a second worktree or a clone of this repository) anywhere. A probe that needs a repository builds a temporary one in your temporary folder from scratch (`git init`, a `.tickets/` folder with the ticket files the probe needs, as `tests/acceptance/W2-50/w2_50_support.py` builds its fixture project); a worktree or a clone of **that temporary repository** is allowed and is how you probe the worktree and clone cases. Copy single named files only (the guard hook, for example), never `governance/project/`. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2). Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree.
- Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.
- If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return. Refused twice for the same call: stop and say so; no third try (AR-6). On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.

## What you read

- The ticket file `.tickets/DAEO-kl5e.md`: its KPI lines and its `allowed_paths`.
- The approved proposal `docs/changes/W2-50-CIT-P.md` with the owner's answers (DEC-743) in its closing section, and the record `docs/changes/W2-50-CIT-E.md` (§6 and §7 describe the two repairs, §8 the two failed reviews; differences 14 and 15 are confirmed by DEC-756 and need nothing: the own folder opens only after a launch made it, and the marker is protected by the guard, while a sandbox `denyWrite` on it is a W2-21 row).
- The decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-728, DEC-723, DEC-159, DEC-108, DEC-313, DEC-334, DEC-386, DEC-434, DEC-685, DEC-136, DEC-137, DEC-413, DEC-498. DEC-751 (delegated by the orchestrator, staged): P-A (a) the launcher writes a marker in the own folder naming this repository's git common directory, and the guard and the launcher refuse a folder whose marker is missing or names another repository; P-B (a) the secrets walk follows links whose target stays inside the repository being scanned, even under the root, while W1-15's B4 stays green.
- The ticket's acceptance tests `tests/acceptance/W2-50/` (with their README) and the code at the head: `git diff 689bd17e HEAD -- src/` (the whole change: `91200c82`, `86aa805c`, `df5f1e50`), and `git show df5f1e50` for the last repair.

## What you probe for

Behaviour the acceptance tests miss, above all a case that could:

- lose work;
- let a role write outside its scope;
- let an implementer change the acceptance tests;
- make the guard or a gate fail open.

**Focus on the repair:**

- **The marker.** It is made only when nothing exists at the folder's path, and never rewritten; its bytes are exact (this repository's common directory and a newline: try a trailing space, no newline, two newlines, a relative path, the path spelled through a link). Put a symbolic link, a FIFO, a directory or a hard link in the marker's place (a hard link to another folder's marker included), and a folder made by hand with a marker copied from a real one. Another repository's marker; a worktree of this repository (same common directory: same repository); a clone (another repository); a `.git` file whose `gitdir:` points elsewhere, a `commondir` that is a link or relative; a project with no `.git` at all. Races between the launcher's checks and its make.
- **The guard's refusals of the marker itself:** Write, Edit and the judged Bash forms on it (`rm`, `mv` over it, `cp` onto it, `ln -f`, `>` and `>>`, `sed -i`, `touch`), by every spelling (`..`, a link to the folder, a case change, a trailing `/.`), and moving or renaming the whole own folder away and making a new one.
- **The launcher's sandbox list:** exactly the temp folder and the one own folder, and only when it carries this repository's marker; never the root, a parent, a link or another ticket's folder; what the launcher makes or leaves on disk when it refuses.
- **The secrets walk's links inside the scanned project:** a link inside the project whose own target leads out under the root (a link to a link, a chain, `..` spellings), a link that stays inside a clone under the root, a link from a project outside the root into a clone under it, and W1-15's B4 (run `tests/acceptance/W1-15` to see it green).

Then the whole ticket's final code: another ticket's folder reached by `..`, a symbolic link, a hard link, a rename or a case change; the root itself in every spelling; a session with no ticket, an empty or forged ticket id, a ticket not `in_progress`, an unknown role and `ticket-lead`; a crafted `external-ref`; two tickets that name the same folder; the guard's other refusals that must still come first (a frozen project, the settings file, the acceptance tests, `.tickets/`); a clone in the own folder reaching this repository's stores or index. Drive the guard as the acceptance suite does (the kernel's PreToolUse hook with the call on stdin, or the public decision function), and `gov launch` with a stand-in CLI as the suite does.

Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such. Known and out of scope (report only if you find they fail open in a way the owner's answers did not accept): `git clone` destinations are not judged (row W2-H055, W2-09); Write and Edit in a launched session through Claude Code (row W2-M359, W2-21); a sandbox `denyWrite` on the marker (W2-21, DEC-756); `rmdir` of another ticket's empty folder, `rmdir -p` ending at the root, and `rmdir` of an argument the guard cannot resolve (R7 scoped to the root, DEC-743; CIT-E difference 5); Bash forms the guard never judged anywhere, inside the repository either (`find -delete`, `env rm`, `git clean`, `rsync --delete`, `dd of=`, `truncate`, an interpreter's `-c`); a subagent acting in its own role in a `ticket-lead` session; a FIFO among the ticket files (fails closed; a residual row); the silent start with no own folder (a W2-21 warning row).

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

After the fields, the payload: the full id of the head you probed; your judgement, `pass` (no finding that loses work, lets a role write outside its scope, lets an implementer change acceptance tests, or makes the guard fail open) or `fail`; and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and whether it loses work, lets a role write outside its scope or fails open, and whether you reproduced it. Say also what you probed and found sound. Then the body of the probe record in Markdown, as you would have it committed (a "What was probed", "What it found", "Found sound" and "Judgement" list, as the two records in `docs/changes/W2-50-CIT-E.md` §8 summarise). The lead writes the probe record from your return; you repair nothing (MR-4). Refused twice for the same call: stop and say so.
