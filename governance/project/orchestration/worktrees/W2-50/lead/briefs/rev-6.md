# Brief: reviewer (FULL, read-only) — DAEO-kl5e (W2-50), the review of the last round (DEC-774, DEC-778)

You are a fresh reviewer. Ticket DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL, is implemented and repaired in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`, at the head `fc9e6a2ad67df3e9536e5236e957bc95930c3def` (check it with `git rev-parse HEAD`), and its acceptance tests pass. You probe that head for behaviour the tests miss, **on this round's change only**. You write nothing.

The previous review (probed `2d60cdd3`) failed on finding D. The owner allowed one more short round and widened it (2026-10-18; staged for the owner's commit, not in this worktree's register):

- **DEC-774, finding D:** `cp -b` (`--backup`), `install`, `mv` and `cp --remove-destination` onto a symbolic link replace the link with a new file at the link's own path, while the guard judged the link's target. So where such a link already sits at a protected name (an acceptance test, another ticket's file or folder), a session put a file there. **The guard refuses as doubt a write that replaces a link rather than following it** — the four forms and any other form of `cp`, `install` or `mv` whose write replaces the link at its own path. Ordinary writes through a link to an allowed target, and every copy, install and move the previous round allows into allowed folders, still pass. The change record gets a new section correcting §10's overclaim.
- **DEC-778, one option reader:** the guard's refusal to read protected material (the project's settings file and its held-out file; a second name given by `mv` or `cp -l` to one, or to a folder that holds one, is a read, DEC-548, DEC-553) read `mv` and `cp -l` with an older option reader (a `t` inside an option's value read as `-t`; `--` ignored). Now it uses the reader the write rule uses for `cp` and `install`, so the guard reads every copy-like command one way, for writes and for reads. Ordinary `mv` and `cp -l` of unprotected files still pass.
- **Out of scope:** `ln -f`/`ln -sf` onto the own folder's marker (row W2-L354); a FIFO in the marker's place (row W2-L350).
- **DEC-779 (owner): this is W2-50's last round.** For each finding you report, say **whether a launched, sandboxed worker could reach it** (a session started by `gov launch` runs with the operating system's sandbox, whose write list holds only its worktree, the temp folder and its own folder under `~/gov-os-runs`), or **only an unsandboxed session** (the orchestrator, a ticket lead), or only with a precondition that no session can create through the guard. Give your reasons.

This round's commits: tests `2956f9e7` (`tests/acceptance/W2-50/test_w2_50_link_replaced.py`, D), `397a80de` (`tests/acceptance/W2-50/test_w2_50_one_reader.py`, DEC-778), repair `1c80aa97` (`src/gov/guard/decide.py`, `src/gov/guard/protected.py`, builder tests), record `6f9bc03a` (`docs/changes/W2-50-CIT-E.md` §11), the lead checkpoint at the head.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor` and `DAEO-kl5e`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-50` and `w2/W2-50`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- The guard's hook in your own session runs **this worktree's** `src/` (DEC-751 item 6): the code you probe also confines you. A refusal you meet may be that code speaking; say so, and never work around it.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. A foreground command is killed after 10 minutes: run the acceptance suite's files in a few separate commands. You write nothing, so no commit of yours will exist: return when your findings are complete.
- No `git checkout` of another commit, no `git reset`, no `git clean` in this worktree. Write no file of the repository and make no commit; `git status --short` must be the same before and after your probe (show both). No subagents that write. Install nothing. No push, merge, rebase or tag.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nothing under `~/.claude/` is read.
- **Never read, print, search, diff, copy, move or link the held-out file under `governance/project/`, and never type its path (DEC-525).** Probes of the read rule use a temporary project of your own with its own settings file as the stand-in protected file (the acceptance tests do so), or another public means; never a real repository's settings file or held-out file. Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **The real scratch roots are never touched.** You never create, write, list or remove anything in the real `~/gov-os-runs/` (it does not exist; nobody creates it in this run), the real `~/gov-os-worktrees/` or the real `~/gov-os-workbench/`. Every probe that runs the code under test gives it a temporary `HOME` in your session's temporary folder, and a `TMPDIR` that is a sibling of that home, never a parent of it (the guard allows the temp folder, so a home inside it proves nothing). Run no `local_only` live-launch case and start no real `claude` session. Before you return, run `test -e ~/gov-os-runs && echo PRESENT || echo ABSENT` and quote the output: it must print ABSENT.
- Never copy the repository or a folder of it (a recursive copy, a sync, an archive, a second worktree or a clone of this repository) anywhere. A probe that needs a repository builds a temporary one in your temporary folder from scratch (`git init`, a `.tickets/` folder with the ticket files the probe needs, as `tests/acceptance/W2-50/w2_50_support.py` builds its fixture project). Copy single named files only (the guard hook, for example), never `governance/project/`. Every link and hard link a probe needs is made in your temporary folder, never in the repository. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673). An allowed command you run for real to confirm its effect runs only against files in your temporary folder.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2). Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree. Never write under `src/gov/close/**` or `tests/unit/close/**`.
- Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.
- If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return. Refused twice for the same call: stop and say so; no third try (AR-6). On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.

## What you read

- The ticket file `.tickets/DAEO-kl5e.md`: its KPI lines, its `allowed_paths` and its last note.
- `docs/changes/W2-50-CIT-E.md` §11 (this round) and §10 (the previous round, which §11 corrects).
- The tests `tests/acceptance/W2-50/test_w2_50_link_replaced.py` and `test_w2_50_one_reader.py`, with the README's sections on them, and the change: `git show 1c80aa97`.

## What you probe for — this round's change only

Behaviour the acceptance tests miss, above all a case that could lose work, let a role write outside its scope, let an implementer change the acceptance tests, make the guard fail open, or let a session read the protected pair:

- **D:** every form of `cp`, `install` and `mv` (with `-b`, `--backup[=CONTROL]`, `-S`/`--suffix`, `-f`, `--remove-destination`, `-T`, `-t`, `--target-directory`, `-u`/`--update`, `-n`, `-i`, `-l`, `-s`, `-P`/`-d`/`-a`/`--no-dereference`, `-D`, `--`, joined and separate options, abbreviations the tool accepts) onto a link **at a protected name** (the fixture's acceptance folder; another ticket's folder under the temporary root, its link pointing into the session's own folder) and onto a link **in an allowed folder**; a link at a middle level and a link to a folder as the destination; a dangling link; a link to a file without write permission; several sources; a link moved away. Each form that replaces the link at its own path must be refused (as doubt); each that writes through it is judged at its target. Learn what each form does by running it for real only in your temporary folder.
- **The one reader (DEC-778):** `mv` and `cp -l` (`--link`) of a stand-in protected file (your temporary project's own settings file) and of the folder that holds it, with every value-taking option the tool's `--help` lists, joined and separate, after `=` and as the next word, with a `t` in its value (and a value that is itself `-t` or `--`), in clusters, after the operands; `--` before, between and after the source and the destination; `-t`, `--target-directory` and `-T`; **reads of the stand-in through a link or a hard link** to it (a link made in your temporary project, then given a second name, moved, or copied with `-l`); for the orchestrator (who may write the file) and for an engineer. Each must be refused as a read with the guard's read reason.
- **The CIT-E's new section (§11) says only what holds:** each claim it makes, against the code and the tests; whether its correction of §10 is accurate; whether "What stays open" is complete for this round's change.
- **Nothing earlier now refuses that should pass:** ordinary copies, installs and moves into allowed folders inside the repository and the own folder; plain `cp X <link>` and `cp -t <folder> X` through a link to an allowed file; `cp X <link to folder>/`, `install -m 644 X <folder>/`, `mv X <folder>/`; `cp -S.bak`, `cp -b` onto a plain file, `install -D`, `install -d`, `mv -f`, `mv -n`, `cp -a`, `cp -rp`, `cp --reflink=auto` onto allowed files; ordinary `mv` and `cp -l` of unprotected files; the commands the acceptance suites and the builders use in ordinary work. Name any refusal of an ordinary call and judge whether it blocks work.
- The guard's speed on these forms (the hook's deadline must not make a form fail open).

Run the code; do not judge it by reading alone. Drive the guard as the acceptance suite does (the kernel's PreToolUse hook with the call on stdin). A finding you could not reproduce is marked as such. Out of scope (report only if they fail open in a way the owner's answers did not accept): everything outside this round's change, which the earlier reviews probed; rows W2-L354 and W2-L350; `git clone` destinations (W2-H055); Bash forms the guard never judged anywhere (`find -delete`, `env rm`, `git clean`, `rsync`, `dd of=`, `truncate`, `tar -C`, an interpreter's `-c`); Write and Edit in a launched session through Claude Code (W2-M359); the sandbox itself (W2-21).

Run `tests/acceptance/W2-50` once to its end (in separate runs of its files) and report its count.

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

After the fields, the payload: the full id of the head you probed; your judgement, `pass` (no finding in this round's change that loses work, lets a role write outside its scope, lets an implementer change acceptance tests, makes the guard fail open, or lets a session read the protected pair) or `fail`; and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, whether it loses work, lets a role write outside its scope, fails open or reads the protected pair, whether you reproduced it, and **whether a launched, sandboxed worker could reach it or only an unsandboxed session, or only with a precondition no session can create through the guard, with your reasons**. Say also what you probed and found sound, and any ordinary call now refused. Then the body of the probe record in Markdown, as you would have it committed (a "What was probed", "What it found", "Found sound" and "Judgement" list). The lead writes the probe record from your return; you repair nothing (MR-4). Refused twice for the same call: stop and say so.
