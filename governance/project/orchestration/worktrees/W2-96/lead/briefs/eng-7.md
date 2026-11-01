# Brief: engineer, W2-96 (DAEO-ouet), run 3: review 4's W1 fix, the run's processes stopped and reaped before the clean-up (DEC-987)

You are a fresh engineer. Ticket: `DAEO-ouet` (W2-96, the opaque acceptance runner `gov accept`), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-96` on branch `w2/W2-96`. You build the code to the specification and its KPIs, never to the tests (DEC-957); your test-driven development is your own unit tests.

**Where things stand.** Runs 1 and 2 are built (R1 to R15), and `gov accept DAEO-ouet` passed 106 of 106 on them. Review 4 probed the head and found W1 (below). The owner decided (DEC-987, in `docs/DECISION_REGISTER.md`): fix it now, about 30 to 40 lines; a test designer has already written two acceptance cases for it (merged here at `9d2d27e2b5bd`, red on the code as it stands); after you, a third review judges your change alone.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ouet','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (never delete such a file; name it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-ouet`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-96` and `w2/W2-96`), and `git rev-parse --short=12 HEAD` (expect `9d2d27e2b5bd`). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src` set **per command** (never in a session's `--settings` env). Show it once with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -c "import gov; print(gov.__file__)"` and quote the line.
- **Policy 2 (DEC-820):** reads are open, writes are closed. Refused to you: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy the held-out file under `governance/project/`, never type its path, never read or name the qualification oracle); **(c) this ticket's acceptance tests: you never read `tests/acceptance/W2-96/`** (here, in `/home/usain/gov-os-worktrees/W2-96-tests`, or on branch `w2/W2-96-tests`), by any tool — no `cat`, `Read`, `Grep`, `git show`, `git diff`, `git log -p` of it; you may run them through `gov accept` and see its results; (d) the hidden half of any evaluation set, by whoever is measured by it.
- **DEC-849:** until W2-58 lands the guard still refuses some reads (searches starting at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form; search named folders instead, and count the refusals you met in your return. Never read `.claude/settings.json`.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src timeout 90 python3 -m gov.cli.main retrieve "<question>" --json` (this worktree's store). Known: inside the sandbox that call can hang on the embedder's network call; try it once, and if it times out, say so and search named folders under `src/gov/` instead. Do not run `gov rebuild` yourself. Never one giant query or context (DEC-860): a large question in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph (DEC-859). Drop unread any result under `tests/acceptance/W2-96/`.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository); a test that needs a repository builds a temporary one from scratch. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only. No clone, copy or programme file under any `.gov-runtime/` folder. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Write files with the Write and Edit tools at literal absolute paths; put anything longer in a script file in your session's own temporary folder (the one the launcher set; `.gov-runtime/scratch/eng/` is refused to this role) and run it by its literal path; a command with `$TMPDIR` in it is refused, so write the path out. Never `cd` into a subfolder of the repository. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. No subagents that write. Install nothing (an install you need is a P1 escalation in your return).
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Budget (DEC-898):** your share is 5 GB and 250,000 files and folders outside the tracked tree. Keep pytest's own temp retention (never a per-run `--basetemp` for your suite runs); run with `-o tmp_path_retention_policy=failed`. Your temp folder is the one the launcher set; clean up what you make as you go; measure at the end (`du -sh`, `du -s --inodes`) and give the figures.
- If the guard or the sandbox refuses something you need, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try (AR-6).**

## What you read

- The ticket file `.tickets/DAEO-ouet.md` (read-only): its KPI lines (KPI 2 above all), its `allowed_paths` and its body.
- DEC-987 in `docs/DECISION_REGISTER.md`.
- The code as it stands: `src/gov/accept/` (the child's start, the signal handling and the clean-up in `runner.py` above all), `tests/unit/accept/`.
- The lead's addenda: `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/design.md`, `design-r1.md`, `design-r2.md`, `design-r3.md` (R1 to R15), which still hold except where R16 below differs.

## R16, review 4's W1 (behaviour; it overrides the earlier notes where they differ)

- **What review 4 found (W1).** A planted test runs a nested `gov accept` in a session of its own (the acceptance harness starts nested runs this way; W2-69, W2-71, W2-50, W2-76, W1-28 and W1-32 also start own-session processes), with its `TMPDIR` inside the test's temporary folder; the nested test sleeps 1 to 3 s. A stop (SIGTERM, Ctrl-C, coreutils `timeout`) reaches the outer `gov` alone while the nested pytest still runs. The outer `gov` ends with 143 or 130 and the caller's `TMPDIR` empty; 2.4 to 3.4 s later, the orphaned nested pytest's report writer recreates its report's missing folders, so `gov-accept-XXXX/tmp/pytest-of-<user>/pytest-0/<the outer test's name>/given-1` appears in the caller's `TMPDIR` (23 of 24 runs). A test that starts such a run and does not wait for it does the same after a pass with exit 0 (3 of 3). A stop sent to the whole process tree at once leaves nothing.
- **R16 (what must hold).** Before its clean-up, in every path (a pass, a failure, an error, a stop by SIGINT, SIGTERM or SIGHUP), `gov accept` stops every process the run started, **whatever its session or process group**, and waits until none is left; only then does it remove its private folder. Once `gov` has ended, no process of the run is alive, and nothing of the run appears in the caller's `TMPDIR` later. Exit codes, the envelope, R9's held signals, R12's 128 plus the signal, R14's tolerant removal and R15's linear time are unchanged; nothing from the child is printed.
- **The mechanism the owner named (DEC-987):** on Linux, `gov` makes itself the reaper of its descendants' orphans (`prctl(PR_SET_CHILD_SUBREAPER, 1)`, through `ctypes` on libc; no new dependency), so a process that leaves its session or whose parent dies is re-parented to `gov`, not to init; before the clean-up it stops every descendant still alive (its children and theirs, found from the kernel, for example `/proc/<pid>/task/<tid>/children` walked from `gov`'s own pid) and reaps them (`waitpid`), repeating until `gov` has no child left (a descendant may fork while being stopped). About 30 to 40 lines.
- **Points of care, so it fails closed and harms nothing:**
  - Stop only `gov`'s own descendants: never a process found by name, user or command line.
  - Reaping must not steal the main child's exit status from the code that waits for it (wait for the main child first, or reap by pid), and the result it reports must stay the child's.
  - Bounded: the loop ends (a total time limit you state, while R9's signals stay held); if a descendant survives it, `gov` still cleans up and exits as before; a stopped run never exits 0.
  - Where `PR_SET_CHILD_SUBREAPER` is not available (not Linux, or the call fails), `gov` keeps today's behaviour and fails no run for it; say in your return what it does there.
  - The subreaper setting stays inside `gov accept`'s own process; nothing else in the product changes.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/accept/**` and `tests/unit/accept/test_w2_96*.py` (every new file's basename starts `test_w2_96_`). Not `src/gov/check/commands.py`.
- Never `src/gov/cli/main.py`, never `tests/acceptance/**` (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Proportion (DEC-135): only R16. Review 4's rows W2 (silent give-up after a lasting error) and W3 (a link put in place of the private folder) are Wave 3 rows: do not build them.
- Unit tests first (TDD): an own-session grandchild that outlives its parent is stopped and reaped before the clean-up (pass and stopped paths); a child that keeps forking is still ended within the bound; the main child's exit status is reported as before; nothing of the run appears in the given `TMPDIR` after `gov` returns, checked again after the orphan would have written. Run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -m pytest tests/unit/accept -q -p no:cacheprovider -o tmp_path_retention_policy=failed` to the end, never `-x`.
- **Commit before the acceptance run.** Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Trailers in the final block:

      git commit -m "W2-96 (DAEO-ouet): review 4's W1, gov accept stops and reaps every process of the run before its clean-up (DEC-987)" --trailer "Task: DAEO-ouet" --trailer "Role: engineer" --trailer "Implements: DEC-987, DEC-959, DEC-317" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

  `Implements:` holds only ids the register holds (DEC-927). After every commit: `git log --oneline -2` and `git status --short`.

## Steps

1. Build R16 with unit tests, run your unit tests to the end, commit. Count the lines you added and removed (`git show --stat HEAD`).
2. Run the acceptance tests **once**, reading results only: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -m gov.cli.main accept DAEO-ouet --json` (quote the JSON and the exit code; it should cover 108 cases). Do not run them through pytest and do not run them again: if the run does not pass, return with its JSON, and the lead decides the next step.
3. Return.

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

In `evidence` also: the sandbox check, your commit's 12-digit hash, the `gov.__file__` line, the lines added and removed, the bound you chose and the behaviour where the subreaper is unavailable, whether you used `gov retrieve`, the guard read refusals you met (count), and your scratch measure. After the twelve fields, a `brief_gaps:` section (one line per thing you had to discover that this brief did not tell you, with minutes it cost, or `brief_gaps: none`).
