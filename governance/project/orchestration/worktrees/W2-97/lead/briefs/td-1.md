# Brief: independent test designer, DAEO-wq2b (W2-97), STANDARD

You are a fresh independent test designer (MR-3). Ticket: `DAEO-wq2b` (`W2-97`, "the local merge queue"), profile STANDARD. You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-97-tests` on branch `w2/W2-97-tests` (DEC-963); you never read or write the ticket's own worktree `/home/usain/gov-os-worktrees/W2-97`. Expect `GOV_ROLE=independent-test-designer` and `GOV_TICKET=DAEO-wq2b`. You write the ticket's acceptance tests from its KPI lines and the specification below, in parallel with an engineer who builds the tool from the same specification; you never read its work, and it never reads yours. You show your tests red.

## Your retrieval (DEC-963)

- Use the integration branch's store only, never the ticket worktree's: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json`. For what changed on `w2/integrate` since that store's last refresh, read it with `git show w2/integrate:<path>`.
- **P-R1:** drop unread any `gov retrieve` result under the ticket's implementation paths (`governance/project/orchestration/tools/`, `tests/unit/orchestration/`), and name in your return any such result you were served.

## What you read

- The ticket file `.tickets/DAEO-wq2b.md` (read-only): its six success and four failure KPI lines, its `allowed_paths`, its sources.
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-959 (item 1), DEC-968, DEC-979 (item 3), DEC-962 (the test lock ended), DEC-848, DEC-953 (item 4).
- `governance/project/orchestration/packages/ROLES-RESEARCH-1.md` §4 option (c) and §5.3 item 5.
- Existing code the queue follows, as it stands (read, never edit; it is the CTO's, untracked, not this ticket's implementation): `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/close_build.py` (how a close clones, selects, runs, re-runs a red alone, traces a red with and without the change, and finds a batch's culprit) and `select_tests.py` (the selection's JSON output).
- An existing acceptance suite as a pattern for layout (README, conftest, a ticket-prefixed support module): `tests/acceptance/W2-108/`.

## What you write

- Only under `tests/acceptance/W2-97/`, with a `README.md` that maps each KPI line (all six success lines and all four failure lines) to its tests and gives each test's expected red reason today (the tool does not exist on the ticket's base, so every test should fail because the tool file is missing, or say what else).
- **In proportion (STANDARD; DEC-951 item 5: the minimum that shows each line):** every KPI line's success and failure, plus the key edge cases the specification names (a flaky red that passes alone; a red that is not the batch's; a fail-closed batch). No combinatorial expansion. Aim for roughly 10 to 16 tests that run in well under two minutes together.
- **Stand-ins only (the ticket's acceptance line):** each test builds a planted git repository under pytest's `tmp_path` with a fake integration branch (`w2/integrate`, plus a `main` the tests check is never moved), planted ticket branches whose commits carry `Task:` trailers, and stub test, selection and prepare commands (for example small scripts the test writes, or `python3 -m pytest -q -p no:cacheprovider` over planted test files). A stub can record how many times it ran (to show "one run" and "skipped") and can move the planted integration branch during its first run (to show "the head moved while under test"). Strip the environment variables that would leak the outer pytest run into a stub (`PYTEST_ADDOPTS`, `PYTEST_XDIST_*`, `PYTEST_CURRENT_TEST`). Set a git identity for the planted repository's own commits. Always pass `--work` and `--queue` under `tmp_path`. **No test touches this repository's branches, its stores, `~/gov-os-runs/` or the network.**
- The tests run the tool as a subprocess, located relative to the repository root the tests sit in (`governance/project/orchestration/tools/merge_queue.py`), with `sys.executable`, so a run from the ticket worktree exercises that worktree's copy (DEC-732); the README says so.
- Tests check behaviour through the public interface only: the exit code, the integration branch's head (and that it is a merge commit whose parents are the old head and the approved commit, the very commit tested), the files in the queue folder (`approved/`, `ejected/`, `landed/`, `records/`) and their stated fields, and the stubs' own run counts. Never an internal name.
- **Red first:** run your suite to its end from your worktree (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-97-tests/src TMPDIR=/tmp/gov-os-lead-W2-97 python3 -m pytest tests/acceptance/W2-97 -q -p no:cacheprovider -o tmp_path_retention_policy=failed`); every test must fail for the reason your README states. Then run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-97-tests/src python3 -m pytest tests/acceptance/W2-97 --collect-only -q -p no:cacheprovider` and make sure nothing clashes on import with other suites (ticket-prefixed module names).
- An ambiguous KPI line or a point the specification leaves open is never a guess: if it blocks a test, return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence); otherwise test only what the specification fixes and name the gap.
- No KPI here asks for an earlier ticket's test to be revised; if you find one does, name it, do not edit it.
- **Your share of the scratch budget:** 3 GB and 150,000 files and folders.

## Commit

Commit only `tests/acceptance/W2-97/`, in one commit, in your worktree:

    git commit -m "W2-97 acceptance tests: the local merge queue (DAEO-wq2b)" --trailer "Task: DAEO-wq2b" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-959, DEC-979, DEC-953, DEC-968" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

In your return, also give: your commit (12 digits), the test count, the KPI lines with their tests, the red reason as you saw it per test, and every point of the specification you found unclear.

## Standing rules for every worker of this ticket (read first)

- **Step 0, before any work: the sandbox check,** reported first in your return: (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-wq2b','w').write('x')"` must fail; (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.
- Then run `printenv GOV_ROLE GOV_TICKET` and `git rev-parse --show-toplevel --abbrev-ref HEAD`; if they differ from what your brief says, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. Every suite you run, you run to its end, never with `-x`.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-97-tests/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-97-tests/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Memory first (DEC-836):** use `gov retrieve` for what you need to know before reading files at random (the command your brief names). Never one giant query (DEC-860): a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph (DEC-859). Say in your return whether you used it and for what.
- **Reads are open, writes closed (DEC-820, Policy 2).** You read freely, except four things: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen; never read or name the qualification oracle); (c) the counterpart's work on this ticket: the engineer never reads `tests/acceptance/W2-97/` (it may run those tests and see their names, results and failure messages), and the test designer never reads this ticket's implementation (the files `git diff --name-only w2/integrate...w2/W2-97` names, and anything under the ticket's implementation paths `governance/project/orchestration/tools/` and `tests/unit/orchestration/`); (d) the hidden half of any evaluation set, by whoever is measured by it.
- **DEC-849, read refusals until W2-58 lands:** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count the refusals you met in your return. Never read `.claude/settings.json`.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target (use literal paths); no here-document (`<<EOF`), no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; put anything longer in a script file written with the Write tool and run that file. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you need, do not work around it: return it as a package.
- **Protected material:** never read the held-out material's contents and never print a secret. Never write in `~/gov-os-workbench`.
- **No copy of the tree:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it. A test that needs a repository builds a temporary one from scratch (a planted repository under pytest's `tmp_path`). Nothing is cloned or copied under a `.gov-runtime/` folder (DEC-673). Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag** in your worktree. Install nothing (an install you need is a P1 package in your return). Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. No subagents that write. Never run `gov close`, `gov adopt` or `gov pause`. Never run `docs/plan/tools/validate_s1.py`.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/`, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule").
- **Disk and scratch (DEC-898):** the ticket's budget is 20 GB and 1,000,000 files and folders outside the tracked tree; your share is stated in your brief. Keep pytest's own retention (never a per-run `--basetemp`); add `-o tmp_path_retention_policy=failed` to your runs; remove every temporary repository or clone you make as soon as it is done with. Measure your scratch at the end (`du -s --inodes` and `du -sh`) and give the figures in your return.
- **No full suite** (DEC-968): you run only your own tests (and the acceptance tests your brief names), never `pytest tests` as a whole.
- **On an authentication or access error** (401, 403, "Failed to authenticate"): stop and return with status AUTH_REQUIRED.
- **Commits** carry the trailers in the final block with `git commit --trailer`: `Task: DAEO-wq2b`, `Role: <your role>`, `Implements: DEC-959, DEC-979, DEC-953, DEC-968` (ids only) and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. After the commit, show `git log --oneline -2` and `git status --short` in your return.
## The specification (the ticket's KPIs, made concrete by the lead; both the test designer and the engineer build from this same text)

The ticket's KPI lines (in `.tickets/DAEO-wq2b.md`) are the requirement. This section fixes the tool's **public interface** (its command line, the files it reads and writes, its exit codes) so that the tests and the code meet, and states how the lead reads each KPI line. It names no internal function or module: how the tool is built inside is the engineer's.

### Where it lives and how it is run

- The tool is one tracked Python file, `governance/project/orchestration/tools/merge_queue.py`, run as `python3 <that file> <subcommand> …` with the standard library only (plus `git` on PATH). A README in the same folder describes it. Tests locate the file relative to the repository they run in (so a run from a ticket worktree exercises that worktree's copy, DEC-732).
- **One writer:** the queue is the CTO's tool. It is the only thing that moves the integration branch, and only by a fast-forward to a merge commit it made and tested. It never pushes, never touches any other branch of the repository (`main` included), and never amends, rebases or resets a branch.

### The queue folder and the approval (KPI 1: a ticket enters only with approval)

Every subcommand takes `--queue <dir>`, a plain folder (created if missing). Inside it:

- `requested/<ticket>.json` — written by `enqueue`. A request alone never enters the queue.
- `approved/<ticket>.json` — written by `approve`. **The approval file is the entry:** `run` reads only this folder. Until the three layers start, only the CTO approves (it runs `approve`, or writes the file itself in the same form).
- `ejected/<ticket>.json` — written by `run` when it sends a ticket back (below). The approval file is removed when a ticket is ejected or lands.
- `landed/<ticket>.json` — written by `run` when a ticket's merge is on the integration branch.
- `records/<new head, 12 hex>.json` — the record of each advance (KPI 5, below).
- `log/<stamp>/` — the run's own logs (test output, JUnit files); every ejection and record names its run's log folder by absolute path.

Subcommands:

- `enqueue --queue <dir> --ticket <name> --task <task id> --branch <branch> --commit <commit>`: writes `requested/<ticket>.json`. `<ticket>` is the WBS id (e.g. `W2-97`), `<task>` the tracker id its commits carry as `Task:` (e.g. `DAEO-wq2b`), `<branch>` the ticket branch, `<commit>` the exact commit the lead tested (resolved to its full id).
- `approve --queue <dir> --ticket <name> --by <who>`: moves the request to `approved/<ticket>.json`, adding `approved_by` and `approved_at`. A ticket with no request is refused (non-zero exit, nothing written).
- `run --repo <repo> --queue <dir> [--integration <branch>] [--work <dir>] [--test-cmd <cmd>] [--select-cmd <cmd>] [--prepare-cmd <cmd>] [--rounds <n>]`: processes every approved entry (below). `--integration` defaults to `w2/integrate`; `--work` is where the clean clones go (default under `~/gov-os-runs/W2-00/merge-queue/`; removed when the run ends); `--rounds` defaults to 3.
- The JSON files hold at least: `ticket`, `task`, `branch`, `commit`; approvals add `approved_by`, `approved_at`; ejections add `reason`, `failing` (test ids), `log` (the run's log folder), `tested_on` (the head the merge was tested on); landed files add `merge` (the merge commit) and `record` (the record's path).

### Stand-ins (how the tool is driven; production defaults when the options are not given)

- `--test-cmd "<cmd>"`: the command that runs tests (split like a shell would, no shell). The queue runs it with the current directory set to the merged checkout and appends `--junitxml=<file>` and then the targets: the selected targets for a run, or one test id for an "alone" re-run. Exit 0 is green, exit 1 is red with failures named in the JUnit file; any other exit, or a missing or unreadable JUnit file after a run, is "the run did not complete". So `python3 -m pytest -q -p no:cacheprovider` is a valid stand-in, with planted test files in a planted repository. **Default (production):** the close's form as `close_build.py` runs it: one parallel run (`-n auto`, the serial-only plugin, `-o tmp_path_retention_policy=failed`), then the selected serial-only cases, with the merged checkout's own `src` on `PYTHONPATH`.
- `--select-cmd "<cmd>"`: the selection. Run in the merged checkout with these arguments appended: `<checkout> <ticket> <task> --merge <merge commit>`; it prints one JSON object with `scope`, `selected` (a list of objects with a `target`), `pytest_options`, `core_changed` and `unplaced`, exactly as `select_tests.py` prints them. Exit 2 (scope `refused`) or any other failure: the selection cannot be made. A run tests the union of the batch's selected targets (a single ticket's `pytest_options` are added). **Default:** `select_tests.py` (`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/select_tests.py`, DEC-953 item 4), the one selection tool, with the checkout's own `src` first on `PYTHONPATH`.
- `--prepare-cmd "<cmd>"`: run in the merged checkout after merging and before the selection (production: the store rebuild, `flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json` with the checkout's `src`). A failure stops the run. A stand-in such as `true` is allowed.
- **There is no full run** (DEC-968): the full suite runs only in the nightly. A change to the core gets the selection's own scope, never more.
- **No shared test lock** (DEC-962 ended the one-run lock; the KPI's "under the test lock" is read as DEC-962 left it). Instead, the queue holds its own lock for the whole of a `run`, so two queue runs never interleave (one writer): a second `run` while one holds it exits 4 at once and changes nothing.

### What `run` does (the KPI lines, in order)

1. **One head, one batch, one merged result (KPIs 1 and 4).** It reads the integration branch's current head, makes a clean clone of the repository at that head under `--work`, and merges each approved ticket's approved commit into it in turn, `--no-ff`, in the order they were approved, one merge commit per ticket (subject `Merge <branch> (<task>): merge queue`, with `Task: <task>` and `Role: orchestrator` in the final trailer block; made with the repository's configured git identity, or `orchestrator <orchestrator@localhost>` when none is set). A ticket whose commit does not merge cleanly is ejected (reason: conflict) and the rest go on.
2. **Skip only when the code is what the lead tested (KPI 3).** If the merged result's tree equals the tree of the commit a lead tested (one entry's approved commit), with the governance paths left out of the comparison, the run is skipped, the batch advances, and the record states why (`skipped`: the reason, naming the commit the lead tested and the governance paths left out). The governance paths are those `select_tests.py` leaves out: `governance/project/briefs/**`, `governance/project/prompts/**`, `governance/project/orchestration/**`, `.gov-runtime/**`, and the record places of the tree's test map `record_only` list where the tree has one. Any other difference in code paths means one run. A skip never happens without its recorded reason.
3. **Otherwise, one run (KPI 3):** the prepare command, the selection (each ticket's, on its own merge), then the test command once on the union. The run is never repeated on the same merged result.
4. **Green: advance to exactly the commit tested (KPIs 1 and 6).** Before moving the branch, the queue reads its head again. **If the head moved while the candidates were under test,** nothing advances: the same approved commits are merged again onto the new head and that new result is tested (or skipped by rule 2) — never advanced onto a head it was not tested on (a bounded number of attempts, then exit 4 with the entries kept). If the head did not move, the branch is moved to the tested merge commit by fast-forward only: if the branch is checked out in a worktree of the repository, that worktree is fast-forwarded (`merge --ff-only`), otherwise the ref is moved only if it still holds the old head. Any failure leaves the branch where it was (exit 4, entries kept). The new head is the very commit the run tested.
5. **Red: the head does not move (KPI 2).** Every failing test is re-run alone once. One that passes alone is a **flaky candidate**: named in the record and the run's output, it decides nothing on its own (if every red is flaky, the batch advances as green). A test red alone is then checked **without the batch** (on the integration head before the merges), interleaved with and without, `--rounds` rounds (and as many again unless the first are decisive), as `close_build.py`'s red trace does: red without the batch too means **not the batch's** (DEC-968): named in the record, it does not stop the advance. A test that cannot even be collected or run without the batch (it was added by it) is the batch's.
6. **A red the batch caused, one ticket:** that ticket is ejected (`ejected/<ticket>.json` with the failing tests' ids and the run's log folder), the branch does not move, and the run goes on with the next head's entries if any.
7. **A red the batch caused, several tickets (KPI 4, DEC-979 item 3):** each candidate is tried: the merged result is built without that one ticket's merge, and each red is re-run alone `--rounds` times; green in every round means that ticket explains it. A red a ticket's own commit added (it cannot be collected without it) is blamed on that ticket only if it is red, every round, with that ticket alone merged. **Only the culprits are ejected,** each with the tests it caused and the log folder. The rest are merged again without the culprits and that new result gets its own run (a new merged result, so not a second run on the same code), and it advances only on green, by the same rules (so the landed commit is always a tested one). **Fail closed:** a red no single ticket explains, a ticket whose approved commit brings commits that do not carry its own `Task:` trailer (another ticket's work), or a candidate that cannot be isolated (a merge or a rebuild fails without it) ejects the whole batch, each with the reason.
8. **A step that cannot be done** (the clone, the prepare command, the selection refused, a test run that did not complete, the branch that cannot be moved): nothing advances, nothing is ejected for it, the entries stay approved, and `run` exits 4 with the reason on stderr.

### The record (KPI 5)

Each advance writes one JSON record, `records/<new head, 12 hex>.json`, which the close cites instead of running its own tests on the same code. It holds at least: `head` (the new integration head, full id), `base` (the head before), `tickets` (per ticket: `ticket`, `task`, `commit`, `merge`), `skipped` (null, or the recorded reason), `selection` (the targets run, `core_changed`, `unplaced`), `counts` (`tests`, `failures`, `errors`, `skipped` from the run's JUnit files; null when the run was skipped), `flaky` (flaky candidates), `unowned` (reds not the batch's), `ejected` (tickets sent back in this run, with their tests), `log` (the run's log folder), `started`, `finished` (local time). The landed files point at the record.

### Exit codes of `run`

0: every approved entry landed (or there were none); 3: at least one ticket was ejected (others may have landed); 4: the run stopped on a step it could not do, or another run holds the lock (entries kept, the branch unmoved by that step).

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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

After the twelve fields: your sandbox check's result (step 0); whether you used `gov retrieve` and for what; the guard's refusals you met (time, the command's form, the reason given), or "none"; and anything your brief did not tell you that you had to find out (a path, a command form, a tool's behaviour), with the minutes it cost.
