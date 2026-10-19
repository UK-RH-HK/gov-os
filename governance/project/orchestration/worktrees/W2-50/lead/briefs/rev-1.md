# Brief: reviewer (FULL, read-only) — DAEO-kl5e (W2-50)

You are a fresh reviewer. Ticket DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL, is implemented in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`, at the head `b7981b0faf3cad33b596cdd330cd1a339fad5d8c` (check it with `git rev-parse HEAD`), and its acceptance tests pass. You probe that head for behaviour the tests miss. You write nothing.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-kl5e`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-50` and `w2/W2-50`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. You write nothing, so no commit of yours will exist: return when your findings are complete.
- No `git checkout` of another commit, no `git reset`, no `git clean` in this worktree. Write no file of the repository and make no commit; `git status --short` must be the same before and after your probe (show both). No subagents that write. Install nothing. No push, merge, rebase or tag.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nothing under `~/.claude/` is read.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **The real scratch roots are never touched.** You never create, write, list or remove anything in the real `~/gov-os-runs/` (it does not exist; nobody creates it in this run), the real `~/gov-os-worktrees/` or the real `~/gov-os-workbench/`. Every probe that runs the code under test gives it a temporary `HOME` in your session's temporary folder, and a `TMPDIR` that is a sibling of that home, never a parent of it (the guard allows the temp folder, so a home inside it proves nothing). Run no `local_only` live-launch case and start no real `claude` session. Before you return, run `test -e ~/gov-os-runs && echo PRESENT || echo ABSENT` and quote the output: it must print ABSENT.
- Never copy the repository or a folder of it (a recursive copy, a sync, an archive, a second worktree or a clone of this repository) anywhere. A probe that needs a repository builds a temporary one in your temporary folder from scratch (a `.tickets/` folder with the ticket files the probe needs, as `tests/acceptance/W2-50/w2_50_support.py` builds its fixture project); copy single named files only (the guard hook, for example), never `governance/project/`. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2). Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree.
- Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.
- If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return. Refused twice for the same call: stop and say so; no third try (AR-6). On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.

## What you read

- The ticket file `.tickets/DAEO-kl5e.md`: its KPI lines and its `allowed_paths` (`src/gov/guard/runs.py`, `src/gov/guard/decide.py`, `src/gov/launch/launcher.py`, `template/governance/kernel/checks/secrets-indexing.yaml`, `src/gov/secrets/__init__.py` (the link rule only), `tests/unit/guard/test_runs*`, `tests/unit/launch/test_runs*`, `docs/changes/W2-50-CIT-P.md`, `docs/changes/W2-50-CIT-E.md`).
- The sources: the approved proposal `docs/changes/W2-50-CIT-P.md` with the owner's answers (DEC-743) in its closing section, and the record `docs/changes/W2-50-CIT-E.md`.
- The decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-728, DEC-723, DEC-159, DEC-108, DEC-313, DEC-334, DEC-386, DEC-434, DEC-685, DEC-136, DEC-137, DEC-413, DEC-498.
- The ticket's acceptance tests `tests/acceptance/W2-50/` (with their README), and the code at the head: `git show 91200c82`, and the files it touches.

## What you probe for

Behaviour the acceptance tests miss, above all a case that could:

- lose work;
- let a role write outside its scope;
- let an implementer change the acceptance tests;
- make the guard or a gate fail open.

In particular, try: another ticket's folder reached by `..`, a symbolic link, a hard link, a rename or a case change; the root itself (a file in it, removing or moving it, in every spelling); a session with no ticket, an empty or forged ticket id, a ticket id that names a ticket by another key, a ticket not `in_progress`, an unknown role and `ticket-lead`; a ticket whose `external-ref` is crafted (for example one that holds `..`, a slash, or that names another ticket's folder or the root); two tickets that name the same folder; the guard's other refusals that must still come first (a frozen project, held-out paths, the settings file, the acceptance tests, `.tickets/`); the sandbox write list widened beyond the one folder (the root, a parent, a link), and what the launcher makes or leaves on disk; the secrets check with links into and near the root, and a clone there reaching this repository's stores or index; Bash forms that write under the root without being judged. Drive the guard as the acceptance suite does (the kernel's PreToolUse hook with the call on stdin, or the public decision function), and `gov launch` with a stand-in CLI as the suite does.

Run the code; do not judge it by reading alone. A finding you could not reproduce is marked as such. Known and out of scope (report only if you find they fail open in a way the owner's answers did not accept): `git clone` destinations are not judged (row W2-H055, W2-09); Write and Edit in a launched session through Claude Code (row W2-M359, W2-21); `rmdir` of another ticket's empty folder and `rmdir -p` ending at the root (R7 scoped to the root, DEC-743).

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

After the fields, the payload: the full id of the head you probed; your judgement, `pass` (no finding that loses work, lets a role write outside its scope, lets an implementer change acceptance tests, or makes the guard fail open) or `fail`; and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and whether it loses work, lets a role write outside its scope or fails open, and whether you reproduced it. Say also what you probed and found sound. The lead writes the probe record from your return; you repair nothing (MR-4). Refused twice for the same call: stop and say so.
