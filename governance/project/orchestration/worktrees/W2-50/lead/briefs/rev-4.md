# Brief: reviewer (FULL, read-only) — DAEO-kl5e (W2-50), the review of the last round (DEC-758 item 2)

You are a fresh reviewer. Ticket DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL, is implemented and repaired in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`, at the head `8a310cb2d5111ca7c64386b75e9970c2555b189f` (check it with `git rev-parse HEAD`), and its acceptance tests pass. You probe that head for behaviour the tests miss, **on this round's change only**. You write nothing.

The previous review (the extra review, DEC-752 item 2, probed `19a4e9fd`) failed on two findings. The owner allowed one last short round (DEC-758, 2026-10-17; staged for the owner's commit, not in this worktree's register):

- **F1:** every copy or install into a folder (`cp X d/`, `cp X d`, `install X d/`, `cp -r s/. d/`, with or without a trailing slash, with `-t`/`--target-directory` as before) is judged as **each file it writes, `<folder>/<name>`, under the same link and hard-link rule as a direct write**, and refused with the guard's reason. This closes the older hole for every ticket (row W2-H056), and the case where the destination is the own folder's marker (row W2-L349).
- **F2:** a project whose real root is inside `~/gov-os-runs` gets **no own folder**.
- **DEC-758 item 2:** then one independent review of that change only — this one. A fail goes back to the owner with no further round.

This round's commits: tests `ef7c1835` (`tests/acceptance/W2-50/test_w2_50_extra_review.py`), repair `83b0f2f4` (`src/gov/guard/decide.py`, `src/gov/guard/runs.py`, builder tests), record `d5334c0f` (`docs/changes/W2-50-CIT-E.md` §9, with differences 16 to 19), lead checkpoint at the head.

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
- Never copy the repository or a folder of it (a recursive copy, a sync, an archive, a second worktree or a clone of this repository) anywhere. A probe that needs a repository builds a temporary one in your temporary folder from scratch (`git init`, a `.tickets/` folder with the ticket files the probe needs, as `tests/acceptance/W2-50/w2_50_support.py` builds its fixture project); a worktree or a clone of **that temporary repository** is allowed and is how you probe the worktree and clone cases. Copy single named files only (the guard hook, for example), never `governance/project/`. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673). An allowed command you run for real to confirm its effect runs only against files in your temporary folder.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2). Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree. Never write under `src/gov/close/**` or `tests/unit/close/**` (W2-53's).
- Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.
- If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return. Refused twice for the same call: stop and say so; no third try (AR-6). On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.

## What you read

- The ticket file `.tickets/DAEO-kl5e.md`: its KPI lines and its `allowed_paths`.
- `docs/changes/W2-50-CIT-E.md` §9 (this round, differences 16 to 19) and §8 (the earlier reviews), and `docs/changes/W2-50-CIT-P.md` R8 (the link rule).
- The previous review's findings, as behaviour: (1) a copy into a folder was judged as the folder, so a file landed through a symbolic or hard link entry already in it (an acceptance test changed, another ticket's file overwritten, a source repository's objects corrupted through a local clone's hard links); (2) a project made inside the own folder, with a `.git` file naming this repository's common directory and a forged ticket, got another ticket's folder from the guard and from `gov launch`; (3) the marker's refusal was bypassed by a folder destination (`mv`, `cp`, `install`, `ln -sf` into the own folder).
- The tests `tests/acceptance/W2-50/test_w2_50_extra_review.py` with the README's section on them, and the change: `git show 83b0f2f4`.

## What you probe for — this round's change only

Behaviour the acceptance tests miss, above all a case that could lose work, let a role write outside its scope, let an implementer change the acceptance tests, or make the guard fail open:

- **Every copy, install and move form into a folder:** trailing slash or not; `-t DIR` and `--target-directory=DIR`, `-T`; `-r`/`-R`/`-a` with `s/.` and with `s` (a folder copied into a folder); several sources; option clusters and `--` ; a source given by a relative name after `cd`, a glob, a name with spaces; the destination folder spelled through `..`, a link to a folder, `/.`. In each: a symbolic link or a hard link already at `<folder>/<name>` leading outside the session's scope (the project's acceptance tests, another ticket's folder, `.tickets/`, the settings file, outside the repository), a link to a folder at `<folder>/<name>` for a folder copy, a nested folder further down that holds such a link, and the own folder's marker as `<folder>/<name>`. Inside the repository for an ordinary ticket (W2-H056) as well as in the own folder. `ln` and `ln -sf` into a folder (the old finding 3) — say whether they are refused now, and if not, whether it matters.
- **A project inside `~/gov-os-runs`:** a project with a `.git` file, a `git worktree add` of a temporary repository, a clone; reached directly and through a link from outside the root; with forged tickets naming other folders and its own. The guard (Write, Edit, judged Bash) and `gov launch` (its sandbox write list, and what it makes or marks on disk) must give it no folder under the root.
- **Nothing earlier now refuses that should pass:** an ordinary copy, install or move into an allowed folder inside the repository and into the own folder still works; a copy over an ordinary file; a recursive copy of a tree into a new folder; the commands the acceptance suites and the builders use in ordinary work. Name any refusal of an ordinary call (difference 18 names some: an unresolvable source, a glob with no match, more than 10 000 paths) and judge whether it blocks work.
- Speed: a folder copy of a large tree must not make the guard's call exceed its deadline in a way that fails open.

Run the code; do not judge it by reading alone. Drive the guard as the acceptance suite does (the kernel's PreToolUse hook with the call on stdin) and `gov launch` with a stand-in CLI as the suite does. A finding you could not reproduce is marked as such. Out of scope (report only if they fail open in a way the owner's answers did not accept): everything outside this round's change, which the earlier reviews probed; a FIFO in the marker's place (row W2-L350); `git clone` destinations not judged (W2-H055); Bash forms the guard never judged anywhere (`find -delete`, `env rm`, `git clean`, `rsync`, `dd of=`, `truncate`, an interpreter's `-c`); Write and Edit in a launched session through Claude Code (W2-M359); a sandbox `denyWrite` on the marker (W2-21).

Run `tests/acceptance/W2-50` once to its end and report its count.

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

After the fields, the payload: the full id of the head you probed; your judgement, `pass` (no finding in this round's change that loses work, lets a role write outside its scope, lets an implementer change acceptance tests, or makes the guard fail open) or `fail`; and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, and whether it loses work, lets a role write outside its scope or fails open, and whether you reproduced it. Say also what you probed and found sound, and any ordinary call now refused. Then the body of the probe record in Markdown, as you would have it committed (a "What was probed", "What it found", "Found sound" and "Judgement" list). The lead writes the probe record from your return; you repair nothing (MR-4). Refused twice for the same call: stop and say so.
