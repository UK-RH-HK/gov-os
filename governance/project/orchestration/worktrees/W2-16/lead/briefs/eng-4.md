# Brief: engineer (W2-16 round 3, DEC-772 item 1)

You are a fresh engineer. Ticket: `DAEO-49o5` (`W2-16`, "Immutable, hash-pinned releases (CAP-43.b lite)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-16` on branch `w2/W2-16`. The ticket is implemented. The owner's decision DEC-772 changes who may build a release: you build that, to the specification below and the ticket's KPIs, never to the tests. An independent test designer writes the acceptance cases at the same time, in another worktree, from the same specification; you never read them (below).

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-49o5','w').write('x')"` must fail. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-49o5`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-16` and `w2/W2-16`) and `git log --oneline -1` (expect `2c8cfc7a`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Reads (DEC-820, Policy 2).** You read freely, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen), and never the qualification oracle; **(c) the counterpart's work: never read `tests/acceptance/W2-16/`, here, in `/home/usain/gov-os-worktrees/W2-16-tests` or in git history** (no Read, cat, grep, diff or `git show` of it); you may run those tests and see their names, results and failure messages; (d) the hidden half of any evaluation set.
- **Retrieval (DEC-836, DEC-860, DEC-859):** what you need to know you ask first with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -m gov.cli.main retrieve "<question>" --json`, before reading files at random. Never one giant query: a large question in batches (`--batch-size`, then `--continue <token>`). A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; if that tool is not available to you, search named folders with Grep. Drop unread any result under `tests/acceptance/W2-16/`.
- **Read refusals (DEC-849):** the guard may still refuse a search that starts at the repository root, `governance/project/` or `.claude/`. Take the refusal, never look for another form; search named folders instead; count the refusals in your return.
- **Scratch budget (DEC-898):** your share is 6 GB and 300,000 files and folders, outside the tracked tree. Keep pytest's own temp retention (no `--basetemp`); clean what you make as soon as it is not needed; give `du -sh` and `du -s --inodes` of anything you leave in your return.
- **Commit hashes (row W2-L423's rule, DEC-911):** anything you write under `.gov-runtime/` holds commit hashes as 12 digits, never 40, and never the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- Run everything in the foreground, one command after another: your session ends with your last message. A single tool call is cut off at 10 minutes: run a long suite file by file. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase. A correction is a new commit.
- Never read `.claude/settings.json` or `.claude/settings.local.json`, anywhere, nor anything under `~/.claude/`.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **Never copy the repository or a folder of it** (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of it); a try-out that needs a repository builds a temporary one from scratch. Nothing under `.gov-runtime/` holds a clone or copy of a programme (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Write files with the Write and Edit tools and literal absolute paths. No subagents that write. **Install nothing** (the guard refuses it; a tool you need is a package). No push, rebase or tag; the one merge you make is below.
- **Nobody tags and nobody signs.** You never run `gov release` against this repository's real history and write nothing into `docs/releases/` but its README. Try-outs build releases in temporary repositories. Never set `GOV_ROLE` or `GOV_TICKET` on a command line of yours; builder tests set them inside the test process (pytest's `monkeypatch`).
- Never touch `tests/acceptance/**` (MR-3). Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause`.
- If the guard or the sandbox refuses something you needed, return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6). Record each refusal by the guard (time, the command's form in one line, the reason it gave).
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return status `AUTH_REQUIRED`.

## What you read

- The ticket file `.tickets/DAEO-49o5.md` (read-only): its KPI lines and `allowed_paths`.
- DEC-772, DEC-761, DEC-409, DEC-365, DEC-753 in `docs/DECISION_REGISTER.md` (search the register by id).
- The code: `src/gov/release/`, its builder tests `tests/unit/release/`, `docs/releases/README.md`; and the freeze lift's checks you mirror, `src/gov/pause/command.py` (`read_ancestry`, `_is_session`, `_caller_refusal`, `_lift_test`, `lift`). You may import and reuse that module's functions; you never change it.

## The behaviour this round builds (DEC-772 item 1), as the lead specifies it for both workers

The owner's decision (DEC-772, 2026-10-18), item 1, word for word: "`gov release` is owner-only, from a plain terminal, like `gov approve` and the freeze lift: it refuses with a Claude Code process among its ancestors, with `GOV_ROLE` or `GOV_TICKET` set, or without a terminal, and asks for a typed one-time code. This replaces DEC-761 item 1's line '`gov release` refuses unless the role is orchestrator, or the owner in a plain terminal'. It is W2-16's next round, and that round does only this (tests first, one review of that change); W2-16's allowed paths do not change."

The lead's reading (fixed for this round; a worker who judges it wrong returns a package, never guesses):

1. **Which form.** Item 1 governs the build form: `gov release <version>`, and every `gov release` call that is not `--lock-from`. `gov release --lock-from <template>` (the template's Copier task, run inside `copier copy` and `copier update`) keeps its caller check exactly as it stands (refused for a `GOV_ROLE` set to anything but `orchestrator`; runs with it unset or `orchestrator`). Reason: a terminal-and-code check on the Copier task would refuse every install and update that is not typed by hand, against KPI 4 ("at copy as well as at update") and against W1-39's closed suite, which DEC-771 item 1 says W2-16 does not reopen.
2. **The build form refuses, before it reads or writes anything** (no file, no ref, no tag, no index change; non-zero exit; no traceback; the error code `RELEASE_REFUSED`; its details carry `reason`, one of the words below; its message says the reason in words), in each of these cases:
   - `session`: a Claude Code session is among its ancestor processes. The signs and the reading are the freeze lift's (DEC-409, `gov pause --off`): the same chain from `/proc`, the same signs of a session;
   - `ancestry`: the chain of ancestor processes cannot be read whole up to the system's first process (process 1, `init` or `systemd`);
   - `role`: `GOV_ROLE` is set in its environment, to any value (`orchestrator`, `owner` and the empty value included);
   - `ticket`: `GOV_TICKET` is set, to any value (the empty value included);
   - `terminal`: its standard input and its standard output are not both a terminal;
   - `code`: the code typed back is not the code shown. Only after every check above has passed, the command writes to the terminal a prompt holding a one-time code, the word `RELEASE-` followed by four decimal digits from the system's random source, and reads one line; the line, stripped of surrounding white space, must equal the code. A wrong line, an empty line or end of input refuses. Nothing is shown on a call refused earlier.
   - Where several hold, which reason is given is not fixed; every refusal writes nothing.
   - On success the build is what it is today: the record under `docs/releases/<version>/`, no commit, no tag; the result `{"version": <version>, "record": <the record's folder>}`.
3. **The test seam, in the freeze lift's form** (W1-50 drives `gov.pause.command._lift_test` the same way): the module `gov.release.command` has a function `_release_test(root, version, ancestry=None, terminal=None)`. `root` is the repository to release from (as the command's root); `version` the version string; `ancestry` a planted chain in the form `gov.pause.command.read_ancestry()` returns (a list of maps `pid`, `ppid`, `comm`, `exe`, `cmdline`; this process first, the system's first process last); `terminal` a pair `(input descriptor, output descriptor)`, each asked `os.isatty` whatever is passed. `GOV_ROLE` and `GOV_TICKET` are read from the process environment, never planted. It returns the command's result on success and raises `gov.cli.errors.GovError` with code `RELEASE_REFUSED` and details `reason` on refusal. The command itself always reads the real chain from `/proc` and uses descriptors `(0, 1)`; no option, argument or environment variable plants either.
4. **Nothing else changes:** what a release record holds, immutability, `verify`, `--lock-from`'s rules, doctor, Copier. The command lists (`src/gov/check/commands.py`, W1-07's list) are not touched in this round: W2-20's change is not in this tree (DEC-753 items 2 and 3).

## What you write

- Only `src/gov/release/**`, `tests/unit/release/**` and `docs/releases/README.md` (the owner's procedure: run `gov release <version>` from a plain terminal, outside any Claude Code session, with no `GOV_ROLE` or `GOV_TICKET`, and type back the code). **Not** `src/gov/check/commands.py` (W2-20's change is not in this tree: DEC-753 item 3), not `src/gov/lock/**` or `copier.yml` (nothing there changes), not `src/gov/pause/**`, never a file of another ticket. A change you need outside these paths is a package, not made.
- Update the builder tests that held the old caller rule (the orchestrator and the unset role building a release) to the new one, and add builder tests for each refusal and the success through the seam, as regression evidence.
- Proportion (DEC-135): only what the specification needs. **Never make a guard or gate decision fail open:** a chain that cannot be read, a descriptor that cannot be asked, a read that fails, all refuse; nothing builds a release unless every check has passed.
- Commit your work before you run any long suite. Run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -m pytest tests/unit/release tests/unit/lock -q -p no:cacheprovider` (to its end, never `-x`).

## The acceptance tests (DEC-963)

When you have built and committed: if `/home/usain/gov-os-worktrees/W2-16/.gov-runtime/scratch/lead/TESTS-READY` exists, run `git merge --no-ff w2/W2-16-tests -m "Merge the W2-16 round 3 acceptance cases" --trailer "Task: DAEO-49o5" --trailer "Role: engineer"` in this worktree (the paths are disjoint; a conflict: stop and return it), then run the acceptance suite once, reading results only:

    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -m pytest tests/acceptance/W2-16 -q -p no:cacheprovider -rfs -o tmp_path_retention_policy=failed

(file by file, by name from `--collect-only -q`, if it passes 10 minutes). A failure whose message shows your code is wrong: repair in a new commit and run once more. A failure you judge to be the test's fault: never edit it and never work around it; return it as a package with the failure message. If TESTS-READY does not exist yet when you are done, check once more after about ten minutes of other checks (your builder tests, your own review of the diff); if it is still absent, return, saying so.

## Commit

Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, do not commit: stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only your paths, with the trailers in the final block:

    git commit -m "<subject>" --trailer "Task: DAEO-49o5" --trailer "Role: engineer" --trailer "Implements: DEC-772, CAP-43.b, DEC-722" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After each commit show `git log --oneline -2`, `git log -1 --format=%B` and `git status --short`.

## Return

Your last message, complete in itself: the sandbox check's result; your commits' 12-digit hashes; the files changed; the interface as built (each refusal and its `reason`, the code's prompt, the seam); each suite you ran with its counts and each red case by name with its message; the `gov.__file__` line; `git diff --stat 2c8cfc7a..HEAD -- src tests/unit docs/releases`; whether you used `gov retrieve` and for what; the guard's refusals and read refusals you met; any package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
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

The twelve fields come first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.
