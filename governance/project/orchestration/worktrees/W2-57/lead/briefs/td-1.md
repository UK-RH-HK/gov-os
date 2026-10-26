# Brief: independent test designer — DAEO-cy5o (W2-57), run 1, batch A

You are a fresh independent test designer (MR-3). Ticket: `DAEO-cy5o` (`W2-57`, "Load out of the close: the rulesync probe, the serial-only list, and a route out for every list entry"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-57` on branch `w2/W2-57`. You write the ticket's acceptance tests from its KPI lines and sources, and revise the earlier tickets' tests its ticket body names for you, before any implementation exists, and you show them red.

The work comes in two batches, in this one session. **This launch is batch A: the rulesync probe (KPI line 1) and the doctor probes (KPI line 2).** Commit batch A and return. The lead will then resume this same session with batch B (the serial-only list and the other KPI lines, 3 to 7); everything you learn now carries over. Read the whole of "The behaviour to test" now so that batch A's README and helpers fit batch B, but write only batch A's tests in this launch.

## Step 0, before any work: the sandbox check (report it first in your return)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cy5o','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop there and return (twelve fields), naming what happened.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-cy5o`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-57` and `w2/W2-57`), and `git rev-parse --short=12 HEAD` (expect `d54546f00b21`). If anything differs, stop and say so.

## Standing rules (read first)

- **DEC-732, the code under test (word for word):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test. Your README says how a run of your tests from this worktree exercises this worktree's code.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. Commit before any long run.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no stash in this worktree. No push, merge or tag.
- **Memory first (DEC-836):** for what you need to know, use `gov retrieve` before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src python3 -m gov.cli.main retrieve "<question>" --json`. **Never one giant query or context (DEC-860):** take a large question in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve`, and for what.
- **Read refusals (DEC-849):** until W2-58 lands, the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count the refusals you met and give the count in your return.
- **Policy 2, DEC-820 (c) and (d):** (c) you never read this ticket's implementation: the files `git diff --name-only w2/integrate...HEAD` names, other than your own tests (today there are none; the existing code as it stands on `w2/integrate`, `git show w2/integrate:<path>`, is yours to read, and you read it only to learn the public interfaces and today's behaviour, never to shape a test to an implementation). Check that command before each read of a file under `src/` in batch B, when an implementation may exist. (d) never read the hidden half of any evaluation set by which you are measured. Never read or print a secret or key.
- **Protected material (DEC-820):** never read the contents of the held-out qualification material (its file names may be seen), never read or name the qualification oracle, never type the held-out file's path, never read `.claude/settings.json`. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **No tree copies:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it. A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. Tests that need a repository build a temporary one from scratch or from the dev tiers. Nothing of a programme is ever put under a `.gov-runtime/` folder. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** anything you write under `.gov-runtime/` (and your return) writes commit hashes as 12 digits, never the full 40, and never writes the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- **Disk budget (DEC-898):** the lead and all its workers share 20 GB and 1,000,000 files and folders outside the tracked tree. **Your share: 6 GB and 300,000 files and folders.** Use the temp folder the launcher gives you (`$TMPDIR` as set; do not set or change `TMPDIR` yourself). Keep pytest's own retention (never `--basetemp`), and pass `-o tmp_path_retention_policy=failed` on every pytest run. Remove every temp tree you make as soon as you no longer need it. Before you return, measure what you leave (`du -sh` and `du -s --inodes` of your temp folder) and give the figures. If you would pass your share, stop the heavy work, clean what you can, and return.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. Never `--no-verify`, never `core.hooksPath`. Node 22 commands (rulesync) carry the prefix `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH`.
- **Never run `gov close`, `gov adopt` or `gov pause`** against this worktree or the main tree (a test's own temporary project is yours to use). Never run the plan validator `docs/plan/tools/validate_s1.py`.
- **Never ask or notify the owner** (no question box, no `owner-ping`). Anything that needs a decision comes back in your return as a package.
- If the guard or the sandbox refuses something you need, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-cy5o.md` (read-only): its KPI lines (success and failure), its `allowed_paths`, its sources, and in its body the list of the test designer's files.
- The card: `docs/plan/WAVE_2_WBS.md`, section 2, "W2-57", and section 0 (the rules for every ticket).
- Lens I: `docs/assessment/2026-10/I-SYNTHESIS.md`, section 3.1 C, the W2-57 block of section 4, and P-IS-6 with both its tables; `docs/assessment/2026-10/I4-records-plan-rest.md`, finding 2 (the probe), finding 5 (W1-07's `[doctor]`), section 4.2 and P-I4-5; `docs/assessment/2026-10/I1-guard-launcher-sandbox.md`, section 4.2, F-1, F-2, F-7, F-10, F-14, P-I1-8; `docs/assessment/2026-10/I2-close-checks-ratchet.md` (F9, F10, F12, F14, section 2.2); `docs/assessment/2026-10/I3-retrieval-context-resume.md` (F6, F7, F8, O3).
- The decisions in `docs/DECISION_REGISTER.md`: DEC-892 (item 2), DEC-889 (item 5), DEC-899 (items 3 and 7), DEC-813, DEC-823, DEC-871, DEC-883 (item 5), DEC-890, DEC-784, DEC-915, DEC-922, DEC-500, DEC-527, DEC-549, DEC-757, DEC-762, DEC-766, DEC-862, DEC-866, DEC-906, DEC-221, DEC-462, DEC-491. Where an entry carries "Changed by" or "SUPERSEDED by", the newer entry holds (DEC-866).
- The list rows: `docs/plan/WAVE_2_LIST.md` and `docs/plan/WAVE_2_TRIAGE.md`, rows W2-M364, W2-M384, W2-M332, W2-L352, W2-L409, W2-L415.
- The earlier suites you revise (below), their READMEs and helpers, as they stand.
- The public interfaces: `gov check` (the adapter-portability family, `--json`) and the portability check's own module entry if it has one; `gov doctor --json`; the `RULESYNC_BIN` variable the portability check already honours; for batch B, `gov close`'s test run as earlier suites drive it (W1-30's helpers), and the serial-only list's documented form (its header).

## The behaviour to test (all KPI lines; batch A is lines 1 and 2)

**1. The rulesync probe, with its four effects (DEC-892 item 2, P-I4-5 (a), I4 finding 2). Batch A.**
- (a) **The portability check's two rulesync calls** (`rulesync --version` and `rulesync generate`) get a time limit a loaded machine meets. Today each has 10 seconds, and under the close's parallel load a call has gone past it (W2-53's close of 2026-10-20, W2-63's of 2026-10-22: `RULESYNC_FAILED`, "no answer within 10 seconds"); measured beside such load, `--version` took 0.33 to 2.81 s at loads up to 47. So: a rulesync that answers either call after a delay well past the old 10 seconds (I4 planted 11 s; take a delay of at least 15 s) is answered within the limit and the check compares as it would with a prompt answer (a clean project stays green; a real fault is still found by its own code). A rulesync that never answers still ends the check within a bounded time, never green, with a finding whose text says that the call gave no answer in time — a timeout is told apart from every other finding, and never read as "not installed". The exact limit is set by the implementer from a measurement under the close's parallel load; do not hard-code a figure the KPI does not give, beyond "well past 10 s" and "bounded". A rulesync that is truly absent (not on the PATH, `RULESYNC_BIN` naming no file) keeps its own finding as today.
- (b) **W1-38's session fixture fails, never skips, when rulesync times out** (a timeout is not "not installed"). Only a rulesync that is truly absent may skip as "not installed". The fixture's own probe and W1-38's other own calls to rulesync (for example its `generate` helper, which timed out at 30 s under load in W2-50's run 9, row W2-L415) get limits a loaded machine meets, and a timeout in any of them is a failure that names the timeout.
- (c) **The 9 W1-38 cases (3 functions) whose "not green" assertion a timeout satisfies assert the reason**: each asserts the finding it expects (its code, or what makes it that fault), so a check that went red on a timeout no longer passes them. I4 names one function (`TestBrokenHeldOutFile::test_broken_file_is_not_green_and_no_path_is_printed`, 7 cases); find the other two by running the cause, as I4 did: a stand-in rulesync first on the path (or named by `RULESYNC_BIN`) whose `--version` or `generate` answers past the old limit. Show each of the 9 green against a prompt rulesync and red against a check that fails on a timeout.
- (d) **W1-33's research case** (`test_the_research_definition_is_the_generated_one`) fails, not skips, the same way: its probe helper (`tests/acceptance/W1-33/w1_33_support.py`) tells a timeout from an absent tool, and a timeout fails the case naming the timeout.
- (e) **Three closes' worth of parallel runs show 0 rulesync skips and 0 timeouts:** this is the lead's own verification (W1-38's suite three times in the close's parallel form). Your README names it as the lead's evidence and says what to count (skips whose reason names rulesync; failures naming a timeout).

**2. The doctor probes (I4 finding 5, I2 F12). Batch A.**
- `gov doctor`'s probes (the tools' version and hash probes, and every other probe it runs that has a time limit) get limits a loaded machine meets: a probed tool that answers well past today's limit is still read as answering.
- A probe exception that `gov doctor` does not catch today (I4 finding 5 names the routes: a decode error from a git call that reads text, an error from an unguarded read, the lock comparison) ends `gov doctor` with its failure text kept: an API-0002 envelope (`ok: false`, an error code and a message that names the exception and where it came from), never a bare traceback with no envelope. Build the cause in a temporary repository through ordinary means (for example a file name or content git returns that is not UTF-8), never by patching the code.
- **W1-07's `test_every_command_returns_the_envelope[doctor]`** keeps its failure text: when it fails, its assertion message carries what `gov doctor` printed (stdout and stderr, trimmed), so the cause shows if it recurs (row W2-L409). No expectation of the case is lowered.

**3. The serial-only list, reworked as P-IS-6's two tables. Batch B.**
- Every entry kept serial names its reason in the list (its kind and a reason in words), and the list's header documents the form, including the way an entry is routed to the nightly.
- W1-16's 94 cases that start no daemon run in the parallel phase (I3 F7); its daemon cases stay serial. W1-50's read-merge latency case runs in parallel (I1 §4.2). **W1-09's two race cases stay serial in this run** (they move only after one green nightly in parallel; the lead returns that as a condition).
- The live and real-model files leave the close for the nightly, as DEC-889 item 5 orders: W1-46's live file; W1-50's two live freeze cases; W1-19's real-model file; W1-21's dev-tier file and its family check (`test_the_check_is_green_when_the_dev_tiers_meet_the_baselines`); W1-49's and W1-25's live files; W2-58's five launched sessions; W2-62's live resume; W2-54's sandboxed worker and real embedder. The close's selection still collects them (they are collected and left out, never ignored and never skipped); they run in neither the close's parallel phase nor its serial phase; the nightly's form (the parallel run less the list, then the list's entries alone) still runs them. The route goes through the list (the test designer's file), not through a marker alone.
- True latency cases stay alone, each with its reason (W1-02's and W1-05's p95, W1-15's bound, W1-07's help, W1-10, W1-17, W1-18's latency cases).
- Failure: a serial entry without its reason; a live or real-model file left in the close; a case weakened, skipped or serialised by marker alone to pass.

**4. W1-30's r11 test** (`tests/acceptance/W1-30/test_w1_30_r11_declared_here.py`), which holds today's serial entries one by one, reads the reworked list and its reasons (`Rewrite-Reason: DEC-889 item 5`). Batch B.

**5. Batch B:** W1-30's r13 case (`test_w1_30_r13_probe_findings.py::test_after_a_run_cut_at_the_time_limit_no_process_of_it_lives_or_writes_into_the_project`) gets a limit a loaded start meets (`Rewrite-Reason: W2-M384`); W1-50's two live freeze cases remove every `CLAUDE*` variable before they launch, as DEC-784 requires (`Rewrite-Reason: DEC-784`); one p95 case covers a test designer's read on a branch with changes (I1 F-10); W2-M332 times W1-19's warm queries without its memory sampler in the same process (I3 O3 (b)).

**6. Batch B:** the close's resource gate covers the wall-clock limits that went red under load: W1-02's 5-second bound (168 cases) and the guard's 20-second deadline, either by a limit a loaded machine meets or by running them alone (I1 F-14).

**7. Batch B:** the network check probes the live tests' hosts through the route the session uses, close to when it runs (I1 F-1).

**8. Not yours:** the removal of `load_sensitive` entries is the orchestrator's commit; never touch `governance/project/path-map.yaml` or `governance/project/test-map.yaml`.

## What you write

- **Your folder:** `tests/acceptance/W2-57/` (new), with a README that maps each KPI line (success and failure) to its tests and gives each test's expected red reason today, and says how a run from this worktree exercises this worktree's code.
- **The earlier tests the ticket body names for you, and only these:** `tests/acceptance/serial-only.txt`; `tests/acceptance/W1-30/test_w1_30_r11_declared_here.py`; `tests/acceptance/W1-30/test_w1_30_r13_probe_findings.py`; `tests/acceptance/W1-38/**`; `tests/acceptance/W1-33/w1_33_support.py`; `tests/acceptance/W1-07/**`; `tests/acceptance/W1-46/**`; `tests/acceptance/W1-50/**`; `tests/acceptance/W1-02/**`. Also `tests/acceptance/W1-30/README.md`, **only where it describes r11 or r13** (the same README is changed on another unmerged branch; a conflict is resolved at merge). Batch A touches only `tests/acceptance/W2-57/`, `W1-38/**`, `W1-33/w1_33_support.py` and `W1-07/**`.
- **No expectation is lowered.** Each revision of an earlier ticket's file says why in its commit (`Rewrite-Reason:`); a revision may make a case stricter (assert a reason) or give a time limit a loaded machine meets, nothing else. A revision that a KPI needs but that you would have to make outside the files above is not made: return it as a package naming the exact file and change.
- FULL: thorough, in proportion (DEC-221): every KPI line's success and failure, and the key edge cases. No combinatorial expansion. Behaviour through public interfaces, never internals. Deterministic, no network. A test that needs a repository builds a temporary one. Stand-in tools (a slow or silent rulesync, a slow tool for the doctor) live in your test's temporary folder and are reached through the PATH or `RULESYNC_BIN` the way a user would, never by patching code.
- Keep the run time sane: a case that must wait out a limit does so once, not per parameter; say in the README how long each slow case takes.
- Write no implementation and no throwaway implementation into the tree.

## Show it red

All runs with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src` per command, `-p no:cacheprovider -o tmp_path_retention_policy=failed`, in the foreground, each to its end (never `-x`):
- your batch-A tests in `tests/acceptance/W2-57/`: each red today for the reason the README states (quote the reasons);
- the revised W1-38 and W1-33 cases: green against the installed rulesync where today's behaviour is right, and red where they now ask for what today's code lacks (state which); the whole of `tests/acceptance/W1-38/` once with `-n auto` (counts, skips and their reasons);
- the revised W1-07 `[doctor]` case: green today (its expectation is unchanged), and shown to carry `gov doctor`'s output in its message when made to fail by a cause you plant in its temporary project only (quote the message head).

## Commit (batch A)

Commit only your batch-A paths, with the trailers in the final block (DEC-182, DEC-476). Your own folder in one commit; each revised earlier suite in a commit of its own with its reason:

    git commit -m "<subject>" --trailer "Task: DAEO-cy5o" --trailer "Role: independent-test-designer" --trailer "Implements: <the KPI or capability ids the store resolves, or DEC-892>" --trailer "Rewrite-Reason: <reason, for an earlier suite's file>" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <paths>

Use the reasons: W1-38 and W1-33 — `Rewrite-Reason: DEC-892 item 2: a probe timeout is not an absent tool and not the fault under test`; W1-07 — `Rewrite-Reason: W2-L409: the failure text is kept`. Then show `git log --oneline -5`, `git show --stat HEAD` and `git status --short` (clean).

## Return

Your commits (12 digits each) and what each holds; the test count; each KPI line (1 and 2) with its tests; the red reasons as you saw them; the 9 masked cases by id, with how you found the other two functions; every earlier test you revised, with its reason and what changed in its expectation (stricter, or a limit); the `gov.__file__` line; the sandbox check; your temp folder's figures; whether you used `gov retrieve`, and for what; the read refusals you met; any package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

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

Your last message is your return: the twelve fields above come first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so; no third try.
