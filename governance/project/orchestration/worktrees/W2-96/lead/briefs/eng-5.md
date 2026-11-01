# Brief: engineer, W2-96 (DAEO-ouet), run 2 (DEC-970)

You are a fresh engineer. Ticket: `DAEO-ouet` (W2-96, the opaque acceptance runner `gov accept`), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-96` on branch `w2/W2-96`. You build the code to the specification and its KPIs, never to the tests (DEC-957); your test-driven development is your own unit tests.

**Where things stand.** `gov accept` is built (`src/gov/accept/__init__.py`, `command.py`, `runner.py`; unit tests `tests/unit/accept/test_w2_96_accept.py`, 41 passing), its 79 acceptance cases pass, and `gov accept DAEO-ouet --json` passes on this repository. Two independent reviews probed it; the owner's delegate decided the open points (DEC-970), and the lead turned them into run 2's addendum below. Your job: build the addendum, test-first in your own unit tests, inside your paths, and commit. A test designer writes run 2's acceptance cases in parallel; the lead merges them after you return, and then resumes this session for one acceptance run.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ouet','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (never delete such a file; name it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-ouet`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-96` and `w2/W2-96`), and `git rev-parse --short=12 HEAD` (expect `549dd29b1c6f`). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src` set **per command** (never in a session's `--settings` env). Show it once with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -c "import gov; print(gov.__file__)"` and quote the line.
- **Policy 2 (DEC-820):** reads are open, writes are closed. Refused to you: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy the held-out file under `governance/project/`, never type its path, never read or name the qualification oracle); **(c) this ticket's acceptance tests: you never read `tests/acceptance/W2-96/`** (here, in `/home/usain/gov-os-worktrees/W2-96-tests`, or on branch `w2/W2-96-tests`), by any tool — no `cat`, `Read`, `Grep`, `git show`, `git diff` of it; you may run them and see their names, results and failure messages; (d) the hidden half of any evaluation set.
- **DEC-849:** until W2-58 lands the guard still refuses some reads (searches starting at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form; search named folders instead, and count the refusals you met in your return. Never read `.claude/settings.json`.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src timeout 90 python3 -m gov.cli.main retrieve "<question>" --json` (this worktree's store, rebuilt in run 1). Known: inside the sandbox that call can hang on the embedder's network call; try it once, and if it times out, say so and search named folders under `src/gov/` instead. Do not run `gov rebuild` yourself. Never one giant query or context (DEC-860): a large question in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph (DEC-859). Drop unread any result under `tests/acceptance/W2-96/`.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository); a test that needs a repository builds a temporary one from scratch. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only. No clone, copy or programme file under any `.gov-runtime/` folder. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Write files with the Write and Edit tools at literal absolute paths; put anything longer in a script file in your session's own temporary folder (the one the launcher set; `.gov-runtime/scratch/eng/` is refused to this role) and run it by its literal path; a command with `$TMPDIR` in it is refused, so write the path out. Never `cd` into a subfolder of the repository. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. No subagents that write. Install nothing (an install you need is a P1 escalation in your return).
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Budget (DEC-898):** your share is 5 GB and 250,000 files and folders outside the tracked tree. Keep pytest's own temp retention (never a per-run `--basetemp` for your suite runs); run with `-o tmp_path_retention_policy=failed`. Your temp folder is the one the launcher set; clean up what you make as you go; measure at the end (`du -sh`, `du -s --inodes`) and give the figures.
- If the guard or the sandbox refuses something you need, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try (AR-6).**

## What you read

- The ticket file `.tickets/DAEO-ouet.md` (read-only): its KPI lines, its `allowed_paths` and its body (DEC-970's decisions).
- DEC-970 (its W2-96 item), DEC-959 (items 6 and 7), DEC-957, DEC-820 (c), DEC-317, DEC-747 in `docs/DECISION_REGISTER.md`.
- The code as it stands: `src/gov/accept/`, `tests/unit/accept/test_w2_96_accept.py`, `src/gov/check/commands.py`, `src/gov/cli/main.py`'s docstring.
- The lead's design note and review 1's addendum (`/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/design.md`, `design-r1.md`), which still hold except where run 2's addendum below differs.

## Run 2's addendum (DEC-970; behaviour only; it overrides the design note and review 1's addendum where they differ)

- **R8 (any failed case fails the run; PKG-1 (a); stricter only).** The run's `outcome` is `fail` and `gov accept` exits 3 when any collected case failed or errored, whether a README line maps it or not. A case the README never names is still only counted under `unmapped` (passed, failed and skipped counts), never named. `outcome: pass` and exit 0 need both: every mapped line passes, and no case anywhere failed or errored. Skipped cases never fail the run. A mapped line still fails as before (no case, or an item matching nothing, R5); a run error is still `error` with its kind only and exit 4; a refusal is still exit 1. This replaces "unmapped cases never change the exit code".
- **R9 (Ctrl-C during the clean-up is held back too; review 2's N2).** A SIGINT that arrives while the clean-up runs (stopping the child, restoring permissions, removing the private folder) is held back exactly as SIGTERM and SIGHUP already are: the clean-up finishes, nothing of the run stays in the `TMPDIR` the caller gave, and only then does `gov` end. More signals of the three kinds during the clean-up change nothing. A Ctrl-C while the child runs still ends the run as an interrupt: the child and everything it started are stopped and the private folder is removed before `gov` exits. Nothing of the tests' content is printed in any path (no traceback with a frame or value from the acceptance folder).
- **R10 (the clean-up without recursion; review 2's N5).** The private folder is removed whatever its depth: a test that leaves a chain of more than 1,100 nested folders (some of them without permissions) does not turn a finished run into a `crash`; the run is reported as its results say, and nothing stays in the caller's `TMPDIR`.
- **R11 (an inherited "ignore" is kept; review 2's N7).** A signal among SIGHUP, SIGTERM and SIGINT that `gov accept` was started with set to "ignore" (as `nohup` does for SIGHUP, and a shell does for SIGINT in a background job) stays ignored for the whole run: that signal neither stops the run nor its child, and the run completes and reports as usual.
- **R12 (the exit after a signal; review 2's N8).** Whenever a SIGINT, SIGTERM or SIGHUP ends the run (during the run, or held back during the clean-up and acted on after it), `gov` ends by an ordinary exit with code 128 plus the signal's number (130, 143, 129): a parent process sees that code, never a death by the signal (`-2`, `-15`, `-1` in Python's `subprocess`).
- **R13 (the command is recorded; P-W2-96-CMDLIST (a), DEC-747).** Add `accept` to `RECORDED_GOV_COMMANDS` in `src/gov/check/commands.py` — **that one line only**: W2-16, W2-20 and W2-37 hold the rest of that file (DEC-970). The test designer revises W1-07's and W1-32's lists; you do not touch them.

Points that keep this failing closed, never open: any unexpected exception inside the runner is caught and reported as `crash` with no message; nothing is ever printed from the child; a line with no test fails; a refusal still refuses.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/accept/**`, `tests/unit/accept/test_w2_96*.py` (no `__init__.py` there; every new file's basename starts `test_w2_96_`), and the one line in `src/gov/check/commands.py`.
- Never `src/gov/cli/main.py`, never `tests/acceptance/**` (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Proportion (DEC-135): no code for edge cases beyond the addendum; review 2 judged the narrow windows N3 (microsecond signal windows), N4 (SIGKILL of `gov` alone) and N6 (inherited test classes) rows for Wave 3: do not build them.
- Unit tests first (TDD), one or more per point R8 to R12 (R9 and R12: send the signals to a `gov accept` process you start on a planted project; check processes inside the same command, since each Bash call is its own PID namespace), run with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -m pytest tests/unit/accept -q -p no:cacheprovider -o tmp_path_retention_policy=failed`, to the end, never `-x`. They plant tiny projects in temporary folders; never run anything against this worktree's own acceptance folders except as step 2 below says.
- **Commit each fix before the next run.** Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Trailers in the final block:

      git commit -m "W2-96 (DAEO-ouet): run 2, any failed case fails the run; signals held and ended as 128+N; clean-up without recursion; accept recorded (DEC-970)" --trailer "Task: DAEO-ouet" --trailer "Role: engineer" --trailer "Implements: DEC-970, DEC-959, DEC-317" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

  `Implements:` holds only ids the register holds (DEC-927). After every commit: `git log --oneline -2` and `git status --short`.

## Steps

1. Build R8 to R13 with unit tests for each point, run your unit tests to the end, commit.
2. Run run 1's acceptance tests once, through pytest, reading results only, as a regression check: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -m pytest tests/acceptance/W2-96 -q -p no:cacheprovider -o tmp_path_retention_policy=failed --tb=line`. A case R8 or R12 changes may now fail by design (an unmapped failing test that used to pass the run, a negative return code after a signal): name it with its one-line message and do not bend the code back; the test designer is revising those. Any other failure: fix the code to the specification, commit, run again; at most three runs in all.
3. Run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -m gov.cli.main accept DAEO-ouet --json` once and quote its JSON, and `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -m gov.cli.main --help` once (it must offer `accept`).
4. Return. The lead resumes this session after merging run 2's acceptance cases, for one acceptance run.

## Return

Your last message, complete in itself. Refused twice for the same call: stop and say so. The twelve fields come first, each as a labelled line, any payload after them:

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

In `evidence` also: the sandbox check, your commits' 12-digit hashes, the `gov.__file__` line, the lines added and removed, whether you used `gov retrieve`, the guard read refusals you met (count), and your scratch measure. After the twelve fields, a `brief_gaps:` section (one line per thing you had to discover that this brief did not tell you, with minutes it cost, or `brief_gaps: none`).
