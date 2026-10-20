# Brief: reviewer (FULL, read-only) — DAEO-kl5e (W2-50), the review of one more short round (DEC-764 item 3)

You are a fresh reviewer. Ticket DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL, is implemented and repaired in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`, at the head `2d60cdd3b8773ac6803d004afb16b10e85652a92` (check it with `git rev-parse HEAD`), and its acceptance tests pass. You probe that head for behaviour the tests miss, **on this round's change only**. You write nothing.

The previous review (probed `8a310cb2`) failed on finding A (`cp --parents`) and found B (the option parser). The owner allowed one more short round (2026-10-18; staged for the owner's commit, not in this worktree's register):

- **DEC-764:** **A:** the guard refuses `cp --parents` (and every copy, install or move option that makes the landed path other than `<folder>/<name>`) **as doubt**, the way `ln -t` is refused today. **The change record is corrected:** a new section of `docs/changes/W2-50-CIT-E.md` states what holds after this round and corrects §9's claim (that every copy into a folder is judged file by file and that W2-H056 is closed); §9 is not rewritten in place.
- **DEC-765:** the guard reads option values as values and honours `--`: the short options that take a value (among them `-S`, `-o`, `-g`, `-m`, `-Z`, joined to the letter or separate, and their long forms) never read as `-t`; nothing after `--` is read as an option, and the destination is still judged. `cp -S.t`, `cp -bS.t`, `install -S.t`, `install -oroot`, `install -m+t` onto an acceptance test, and `cp -- -t F`, are judged as the files they write (B). `ln -f`/`ln -sf` onto the own folder's marker is row W2-L354, a FIFO in the marker's place row W2-L350: **out of scope.**
- **The lead's reading of `-Z`:** GNU coreutils 9.4 on this machine gives `-Z` no value for `cp`, `install` and `mv`; so `cp -Zt <folder> X` is a copy into `<folder>` and stays judged (a fail-closed control in the suite). Say whether you agree.
- **DEC-764 item 3:** then one review of that change only — this one. A fail goes back to the owner with no further round.

This round's commits: tests `41aa00c0` (`tests/acceptance/W2-50/test_w2_50_short_round.py`, 53 cases, and the README), repair `83756def` (`src/gov/guard/decide.py`, builder tests in `tests/unit/guard/test_runs.py`), record `3787cc79` (`docs/changes/W2-50-CIT-E.md` §10), lead checkpoint at the head.

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
- Never copy the repository or a folder of it (a recursive copy, a sync, an archive, a second worktree or a clone of this repository) anywhere. A probe that needs a repository builds a temporary one in your temporary folder from scratch (`git init`, a `.tickets/` folder with the ticket files the probe needs, as `tests/acceptance/W2-50/w2_50_support.py` builds its fixture project). Copy single named files only (the guard hook, for example), never `governance/project/`. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673). An allowed command you run for real to confirm its effect runs only against files in your temporary folder.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2). Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree. Never write under `src/gov/close/**` or `tests/unit/close/**`.
- Your temporary folder is removed when your session ends (DEC-386): every finding is in your final message.
- If the guard or the sandbox refuses something you needed for the probe, do not work around it: say so in your return. Refused twice for the same call: stop and say so; no third try (AR-6). On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.

## What you read

- The ticket file `.tickets/DAEO-kl5e.md`: its KPI lines and its `allowed_paths`.
- `docs/changes/W2-50-CIT-E.md` §10 (this round) and §9 (the previous round, which §10 corrects).
- The previous review's findings, as behaviour: (A) `cp --parents <source> <folder>` writes `<folder>/<source path as written>`; with `..` in the source, or through a link at a middle level, it reached the project's acceptance test and another ticket's folder under the root, and the guard allowed it; (B) the guard read a `t` inside an option's value as `-t` (`cp -S.t`, `cp -bS.t`, `install -S.t`, `install -oroot`, `install -m+t`), so it judged the wrong path, and `cp -- -t F` judged nothing; both overwrote an acceptance test when run for real.
- The tests `tests/acceptance/W2-50/test_w2_50_short_round.py` with the README's section on them, and the change: `git show 83756def`.

## What you probe for — this round's change only

Behaviour the acceptance tests miss, above all a case that could lose work, let a role write outside its scope, let an implementer change the acceptance tests, or make the guard fail open:

- **`--parents` and every other option that changes the landed path,** for `cp`, `install` and `mv` (read `cp --help`, `install --help`, `mv --help` on this machine; run a form for real only in your temporary folder to learn where it lands): every spelling and abbreviation the tool accepts, with `-t`, `--target-directory`, a trailing slash or not, `-r`/`-a`; into a folder holding a symbolic link, a hard link or another ticket's file; into the own folder and into an allowed folder of the repository. Each must be refused (as doubt) or judged as the path it actually lands on.
- **Every value-taking short option, joined and separate, with a `t` in its value** (and a value that is itself `-t`, `--`, or starts with `-`), and their long forms with `=` and as the next word, abbreviated: for `cp` (`-S`, `--suffix`, and any long option that takes a value, such as `--sparse`, `--reflink`, `--no-preserve`, `--backup`, `--context`, `--update`), for `install` (`-S`, `-o`, `-g`, `-m`, `--strip-program`, and the rest) and for `mv`. Also clusters (`-bS.t`, `-pvS.t`, `-Zt`, `-vt d`), options after operands, and `-Z`'s reading. Each call must be judged as the files it actually writes, onto an acceptance test and onto another ticket's folder.
- **`--` before and after the destination and `-t`:** `cp -- -t F`, `cp -t D -- X`, `cp -- X D/`, `cp X -- D`, `cp X D --`, `-t` after `--`, several `--`, `mv` and `install` the same; with the destination an acceptance test, a protected folder, or a folder holding a link.
- **The backups** this round adds to what is judged (`-b`, `--backup`, `-S`, `--suffix`): whether they are judged where the tool writes them, and whether that refuses anything that should pass.
- **The CIT-E's new section (§10) says only what holds:** each claim it makes, against the code and the tests; in particular whether W2-H056 is closed in the scope it states, and whether "What stays open" is complete for this round's change.
- **Nothing earlier now refuses that should pass:** ordinary copies, installs and moves into allowed folders inside the repository and the own folder; `cp -t <folder> X` and `install -m 644 X <folder>/` judged as before; `cp -S.bak`, `install -m 0644 -o root`, `cp --`, `cp -a`, `cp -rp`, `cp --preserve=mode`, `install -D`, `install -d`, `mv -f`, `mv -n`, `cp --reflink=auto` onto allowed files; the commands the acceptance suites and the builders use in ordinary work. Name any refusal of an ordinary call and judge whether it blocks work.
- The guard's speed on these forms (the hook's deadline must not make a form fail open).

Run the code; do not judge it by reading alone. Drive the guard as the acceptance suite does (the kernel's PreToolUse hook with the call on stdin). A finding you could not reproduce is marked as such. Out of scope (report only if they fail open in a way the owner's answers did not accept): everything outside this round's change, which the earlier reviews probed; rows W2-L354 and W2-L350; `git clone` destinations (W2-H055); Bash forms the guard never judged anywhere (`find -delete`, `env rm`, `git clean`, `rsync`, `dd of=`, `truncate`, `tar -C`, an interpreter's `-c`); Write and Edit in a launched session through Claude Code (W2-M359); the sandbox (W2-21).

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

After the fields, the payload: the full id of the head you probed; your judgement, `pass` (no finding in this round's change that loses work, lets a role write outside its scope, lets an implementer change acceptance tests, or makes the guard fail open) or `fail`; and each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its severity, whether it loses work, lets a role write outside its scope or fails open, and whether you reproduced it. Say also what you probed and found sound, and any ordinary call now refused. Then the body of the probe record in Markdown, as you would have it committed (a "What was probed", "What it found", "Found sound" and "Judgement" list). The lead writes the probe record from your return; you repair nothing (MR-4). Refused twice for the same call: stop and say so.
