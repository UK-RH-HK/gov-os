# Brief: independent test designer — DAEO-cy5o (W2-57), run 2

You are a fresh independent test designer (MR-3). Ticket: `DAEO-cy5o` (`W2-57`, "Load out of the close: the rulesync probe, the serial-only list, and a route out for every list entry"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-57` on branch `w2/W2-57`.

Run 1 of this ticket is done: a test designer wrote `tests/acceptance/W2-57/` and revised the earlier files the ticket named, an engineer built part of the ticket, and a review passed. Run 2 (owner, DEC-925 item 3) adds three test changes, which are yours. You write them from behaviour and sources, and you show each red where it asks for what the code does not do yet.

## Step 0, before any work: the sandbox check (report it first in your return)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cy5o','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop there and return (twelve fields), naming what happened.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-cy5o`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-57` and `w2/W2-57`), and `git rev-parse --short=12 HEAD` (expect `101285866733`). If anything differs, stop and say so.

## Standing rules (read first)

- **DEC-732, the code under test (word for word):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commits exist. Commit before any long run.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no stash in this worktree. No push, merge or tag.
- **Memory first (DEC-836):** for what you need to know, use `gov retrieve` before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src python3 -m gov.cli.main retrieve "<question>" --json`. **Never one giant query or context (DEC-860):** take a large question in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve`, and for what. (The store may read "stale" because the head moved after the last rebuild; if so, say so and read the named files.)
- **Read refusals (DEC-849):** until W2-58 lands, the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count the refusals you met and give the count in your return.
- **Policy 2, DEC-820 (c) and (d):** (c) you never read this ticket's implementation: the files `git diff --name-only w2/integrate...HEAD` names, other than the tests (`tests/acceptance/**`), are not yours to read on this branch: today they are `src/gov/adapters/portability.py`, `src/gov/doctor/command.py`, `tests/unit/adapters/test_portability.py` and `docs/changes/W2-57-CIT-E.md`. Check that command again before each read of a file under `src/`. The code as it stands on `w2/integrate` (`git show w2/integrate:<path>`) is yours to read, only to learn the public interfaces and the behaviour before this ticket, never to shape a test to an implementation. (d) never read the hidden half of any evaluation set by which you are measured. Never read or print a secret or key.
- **Protected material (DEC-820):** never read the contents of the held-out qualification material (its file names may be seen), never read or name the qualification oracle, never type the held-out file's path, never read `.claude/settings.json`. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **No tree copies:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it. A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. Tests that need a repository build a temporary one from scratch or from the dev tiers. Nothing of a programme is ever put under a `.gov-runtime/` folder. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** anything you write under `.gov-runtime/` (and your return) writes commit hashes as 12 digits, never the full 40, and never writes the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- **Disk budget (DEC-898):** the lead and all its workers share 20 GB and 1,000,000 files and folders outside the tracked tree. **Your share: 6 GB and 300,000 files and folders.** Use the temp folder the launcher gives you (`$TMPDIR` as set; do not set or change `TMPDIR` yourself). Keep pytest's own retention (never `--basetemp`), and pass `-o tmp_path_retention_policy=failed` on every pytest run. Remove every temp tree you make as soon as you no longer need it. Before you return, measure what you leave (`du -sh` and `du -s --inodes` of your temp folder) and give the figures. If you would pass your share, stop the heavy work, clean what you can, and return.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. Never `--no-verify`, never `core.hooksPath`. Node 22 commands (rulesync) carry the prefix `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH`.
- **Never run `gov close`, `gov adopt` or `gov pause`** against this worktree or the main tree (a test's own temporary project is yours to use). Never run the plan validator `docs/plan/tools/validate_s1.py`.
- **Never ask or notify the owner** (no question box, no `owner-ping`). Anything that needs a decision comes back in your return as a package.
- If the guard or the sandbox refuses something you need, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-cy5o.md` (read-only): its KPI lines (success and failure), its sources, and in its body the list of the test designer's files (run 2's two are named at its end).
- The card: `docs/plan/WAVE_2_WBS.md`, section 2, "W2-57", and section 0.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-925 (item 3), DEC-892 (item 2), DEC-889 (item 5), DEC-762, DEC-766, DEC-866, DEC-221, DEC-462, DEC-491. Where an entry carries "Changed by" or "SUPERSEDED by", the newer entry holds (DEC-866).
- The list rows: `docs/plan/WAVE_2_LIST.md` and `docs/plan/WAVE_2_TRIAGE.md`, row W2-M332; `docs/assessment/2026-10/I3-retrieval-context-resume.md`, O3.
- `tests/acceptance/W2-57/` as run 1 left it (its README above all), `tests/acceptance/W1-19/` (the real-model file, its support and README), `tests/acceptance/W1-30/test_w1_30_r15_policy_pairs.py` and its helpers, and W1-38's revised cases (`tests/acceptance/W1-38/`), which show how run 1 held a "not green" assertion to its reason.
- The public interfaces: `gov doctor --json` (its `claude_code` part), `gov check --json` (the adapter-portability family).

## The behaviour to test (owner, DEC-925 item 3)

**1. B3 (a), row W2-M332: W1-19's warm-query times are taken without the memory sampler.** File: `tests/acceptance/W1-19/test_w1_19_real_models.py`.
- Today the module fixture times every query in the same call that also watches the processes' peak memory, so the sampler's own work sits inside the timed queries (I3 O3 (b)); the warm p95 case then reads time the sampler took.
- Revise it so the query times come from a pass without the memory sampler, and the memory peaks come from a second pass that is watched. The p95 case reads the first pass's times; the memory case reads the second pass's peaks; the hit@5 case and the fused-list case keep reading answers as they do (from either pass, said in a comment).
- **No expectation is lowered:** the same p95 limit, the same number of queries timed (at least 50), the same memory limit, the same pass line. Only where the measurement is taken changes.
- This file asks the real embedder and reranker. Inside your sandbox `gov` runs a private Ollama on the CPU, so a run of it there proves nothing about times. Do not run the whole file. Show that it collects (`--collect-only`), and run whatever of it ends in a few minutes in your sandbox, if anything; the lead runs it in full on the shared GPU. Say which you ran.

**2. R2: W1-30's r15 rulesync policy-pair case must not accept a timeout as its red after the fault.** File: `tests/acceptance/W1-30/test_w1_30_r15_policy_pairs.py`, the case `test_a_registry_that_pins_another_rulesync_than_the_installed_one_turns_the_portability_check_red`.
- The reviewer of run 1 put a stand-in rulesync first on the PATH: the installed one for its first two calls, then a `--version` that never answers. The case passed. The run before the fault was green; the run after it was red only with "rulesync --version: no answer within 25 seconds; the generated files were not compared". The version was never compared, yet the case's "red or yellow after" assertion accepted it.
- Hold the after-run's red to its reason, as run 1 did for W1-38's 9 cases: the finding must be the version finding that names the pinned 23.0.0 (and the installed version, if the check's output gives it). A red for any other reason (a timeout above all) fails the case, with a message that names what was found.
- No other expectation of the file changes.
- Show it green against the installed rulesync, and red against the reviewer's construction (a stand-in first on the PATH that hands the first two calls to the installed rulesync and then never answers `--version`, or any equivalent built through the PATH or `RULESYNC_BIN` in the case's temporary folder only, never by patching code). Quote the red message.

**3. R1: an unread Claude Code version is never a pass.** File: `tests/acceptance/W2-57/` (a new case in `test_w2_57_doctor_probes.py` or a file of its own, and the README).
- `gov doctor --json` has a `claude_code` part. When a `claude` CLI is found (first on the PATH) but its version is not read, the part must not read "pass". It reads "unmeasured" or "fail", and says that the CLI's version was not read; `gov doctor` still ends with its envelope.
- The reviewer of run 1 found it this way (F1): a committed repository whose tool registry pins three tools by the sha256 of their binaries, each of whose `--version` never answers, and a `claude` first on the PATH that answers "2.0.0" at once (below doctor's minimum Claude Code version). The three tool probes used up doctor's shared time budget for its probes, the Claude Code probe got no time, and the part read "pass" with no CLI version; doctor exited 0 with ok true and healthy true, after about 90 s. With tools that answer at once, the same repository gave exit 3, DOCTOR_UNHEALTHY, `claude_code` "fail" ("CLI version 2.0.0 below minimum …").
- Cover two routes, each once (a case that must wait out a limit does so once, not per parameter; say in the README how long each takes):
  - (a) a `claude` whose `--version` never answers: the part is not "pass", and it says the version was not read;
  - (b) the reviewer's construction: other probes spend the budget, and a `claude` that would answer a version below the minimum at once: the part is not "pass" (either its version is read and the part fails on the minimum, or it is not read and the part says so); in neither case does `gov doctor` report ok true with `claude_code` "pass".
- Isolate the case from the machine: `HOME` and every place doctor looks for an editor extension point into the case's temporary folder, and the stand-ins are reached through the PATH, as run 1's doctor cases do. Build the registry the way run 1's doctor cases build theirs; use run 1's helpers where they fit.
- Not in scope: a machine with no `claude` CLI at all (today's reading of that is left as it is).
- Also in the README, as a ride-along (reviewer O2 of run 1): where it states the interim savings of the route ("about 303 s less", "no paid session in a close"), say that they hold once the nightly route is built in the close's serial phase.

## What you write

- **Only these files:** `tests/acceptance/W2-57/**`, `tests/acceptance/W1-19/test_w1_19_real_models.py`, `tests/acceptance/W1-30/test_w1_30_r15_policy_pairs.py`. Not the W1-19 or W1-30 README or support files: if one of them needs a change, do not make it; name it in your return.
- **No expectation is lowered.** A revision may hold a case to its reason or move where a measurement is taken, nothing else. A revision a KPI needs that you would have to make outside the files above is not made: return it as a package naming the exact file and change.
- FULL: thorough, in proportion (DEC-221): each behaviour above with its success and failure, no combinatorial expansion. Behaviour through public interfaces, never internals. Deterministic, no network. A test that needs a repository builds a temporary one. Stand-in tools live in the case's temporary folder and are reached through the PATH or `RULESYNC_BIN` as a user's would be, never by patching code.
- Write no implementation and no throwaway implementation into the tree.

## Show it red (and green)

All runs with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src` per command, `-p no:cacheprovider -o tmp_path_retention_policy=failed`, in the foreground, each to its end (never `-x`):
- the R1 cases: red today for the reason the README states (quote it);
- W1-30's r15 rulesync case: green against the installed rulesync; red against the timeout construction (quote it); the rest of the r15 file once, with its counts;
- W1-19's real-model file: collected, and what you could run of it;
- `tests/acceptance/W2-57/` once, `-n auto`, with its counts (the nightly-route case is expected red until the engineer of run 2 builds the route).

## Commit

Commit before any long run, each change in a commit of its own, with the trailers in the final block (DEC-182, DEC-476, DEC-491; an implementer has already committed on this branch, so every commit of yours carries a `Rewrite-Reason:`):

    git commit -m "<subject>" --trailer "Task: DAEO-cy5o" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-925" --trailer "Rewrite-Reason: <reason>" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <paths>

Reasons: W1-19 — `Rewrite-Reason: W2-M332: the query times are taken without the memory sampler (DEC-925 item 3, B3 (a))`; W1-30 r15 — `Rewrite-Reason: DEC-892 item 2: a probe timeout is not the fault under test (DEC-925 item 3, R2)`; W2-57 — `Rewrite-Reason: DEC-925 item 3, R1: an unread Claude Code version is never a pass`. Then show `git log --oneline -5`, `git show --stat HEAD` and `git status --short` (clean).

## Return

Your commits (12 digits each) and what each holds; the test count; each behaviour with its tests; the red reasons as you saw them; every earlier test you revised, with its reason and what changed in its expectation (stricter, or where measured); the `gov.__file__` line; the sandbox check; your temp folder's figures; whether you used `gov retrieve`, and for what; the read refusals you met; any package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

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
