You are a fresh engineer. Ticket: DAEO-9nys (W2-67, "Test hygiene: per-test copies, nested runs, temp folders, and the weak tests' revisions"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-67` on branch `w2/W2-67`. This is the ticket's run 3 (rounds 2 and 3 together, DEC-914). You bound the unit close tests that start a real nested pytest, and give the close's time-limit case a temp folder of its own, inside the ticket's builder files.

## Step 0: the sandbox check (before any work; report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-9nys','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return with the twelve fields, saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-9nys`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-67` and `w2/W2-67`) and `git log --oneline -3` (name the head). If anything differs, stop and say so.

## Standing rules (read first)

- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. Your budget is about 90 minutes: commit your work before you run any long suite.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- **Memory first (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -m gov.cli.main retrieve "<question>" --json`. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve`, and for what. (The store may answer `FACET_UNAVAILABLE` or stale: then say so and read the files named below.)
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return. Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one. Never read `.claude/settings.json`.
- **Policy 2 (DEC-820):** you read freely, except:
  - (a) secrets and keys, never printed;
  - (b) the contents of the held-out qualification material (never read, print, search, diff or copy the held-out file under `governance/project/`, never type its path; its name may be seen);
  - (c) **the counterpart's work on this ticket: its acceptance tests.** You never read, by any tool (Read, cat, grep, git show, git log -p, git diff), any file under `tests/acceptance/` that this ticket's commits changed (`git log --format= --name-only --grep='^DAEO-9nys' -- tests/acceptance` names them: this ticket's KPI tests, probes and READMEs in `tests/acceptance/W1-27/`, and the revised cases, fixtures and READMEs in W1-07, W1-25, W1-26, W1-27, W1-30, W2-02 and W2-50). A search you make never covers those files. You **run** them and read their results: names, pass or fail, failure messages;
  - (d) the hidden half of any evaluation set, by whoever is measured by it. Never read or name the qualification oracle.
- **Protected places:** never write in `~/gov-os-workbench` (never list, glob, search or write there); dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. No clone, copy or file of a programme under any `.gov-runtime/` folder (DEC-673).
- **No tree copying:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it, anywhere. A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. A test that needs a repository builds a temporary one from scratch. Inside this session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **Your writes:** only `tests/unit/close/**`, `tests/unit/guard/**` and `tests/conftest.py` (the ticket's builder files, DEC-907); this run needs `tests/unit/close/**` only. Never `tests/acceptance/**`, never `src/`, `template/`, `schemas/`, `docs/`, `.tickets/`, the decision register, the path map (`governance/project/path-map.yaml`, owner-only, DEC-757), and never `.gov-runtime/**` outside `.gov-runtime/scratch/`. Leave no untracked file in the worktree (`rm` may be refused in your session: put throwaways in your temporary folder). Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write.
- **Row W2-L423's rule (owner, standing, DEC-911):** under `.gov-runtime/` (your notes and evidence), write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule". The same holds for your return.
- **Disk and inodes (DEC-898), your share:** the ticket's budget is 20 GB and 1,000,000 files and folders for the lead and all workers together; **your share is at most 4 GB and 150,000 files and folders at any moment**, in your temporary folder and this worktree's untracked files together. Keep `TMPDIR` as the sandbox sets it (count it). Never pass a per-run `--basetemp` (the root conftest refuses it). **Pass `-o tmp_path_retention_policy=failed` on every pytest run you make** (DEC-905). Measure your temporary folder (`du -s --inodes`, `du -sh`) before and after each run of more than a few cases, and give the figures in your return's `evidence` line. If you pass your share, stop at once, clean what you can and return.
- **The machine:** other sessions share it (20 cores). Before any run of more than a few cases, wait while the 1-minute load is above 20 (`until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done`). **Never make load on purpose** (no CPU burners, no stress loops): other leads' time-sensitive cases run beside you. Never run with `-x`.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try.**
- You never ask or notify the owner (no question box, no `owner-ping`); a package comes back in your return. A KPI line you find ambiguous is never a guess and never bent around: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).
- Proportion rule (DEC-135): no code beyond what the KPIs need. Lower no assertion of the cases you bound: a bounded case asserts what it asserted before.

## What you read

- The ticket file `.tickets/DAEO-9nys.md` (read-only): its second success KPI ("The 15 unit close functions that start a nested pytest get a bound a loaded machine meets (one worker, or a measured limit) …") and its failure line ("an unbounded nested run"). Its card: `docs/plan/WAVE_2_WBS.md` §2, the W2-67 card (from line 1152).
- The decisions in `docs/DECISION_REGISTER.md`: DEC-914 (this run: item 2's "the engineer's P1, option A"), DEC-892 (item a: worksteal waits for these bounds), DEC-889 items 11 and 12, DEC-527 and DEC-549 (the close's parallel runs and their number of workers), DEC-898, DEC-905, DEC-907.
- Lens I: `docs/assessment/2026-10/I2-close-checks-ratchet.md` Finding 5 (from line 650: the 15 functions, in `test_run_and_record.py`, `test_parallel_runs.py`, `test_measured.py`, `test_every_finding.py` and `test_follow_up.py`, start a real nested `pytest` through the close's `_run_tests` or `_check_tests` with a 60-second limit, and the nested run starts its own `-n auto` workers beside the outer run's; five to nine failed under worksteal in the orchestrator's trials with "the test run of tests exceeded the time limit of 60s"); `docs/assessment/2026-10/I-SYNTHESIS.md` line 288 and P-IS-3.
- `tests/unit/close/` as it stands (W2-07 and W2-66 added files and cases since lens I2 counted: count again), and `gov close`'s test runner in `src/gov/close/command.py` (`_run_tests`, `_check_tests`, `_check_acceptance`, `_workers`, `_one_test_run`, `_started`): what a caller can pass (the number of workers, the time limit) and what environment the nested run gets.

## The work

1. **Find the functions** in `tests/unit/close/` that start a real nested pytest (not one whose runner is replaced by a stand-in): list each by node id, with its time limit and number of workers as it stands. If you find more or fewer than 15, say how many and why (new cases since lens I2, cases already bounded).
2. **Bound each** so that a loaded machine meets it: one worker for its nested run where the case is not about the number of workers, and where it is (the parallel-run cases), the fewest workers the case needs; and a time limit with a measured margin. Every bound is a figure the case states, never an unbounded run, and never a change of what the case asserts. A case whose purpose is the time limit itself (the time-limit case) keeps its own short limit.
3. **P1, option A (DEC-914 item 2):** the time-limit case in `tests/unit/close/test_run_and_record.py`, whose nested run the close's time limit kills, sets `TMPDIR` to a folder inside its own `tmp_path` (with `monkeypatch`) for that nested run, so that the killed run's base folder goes away with the case's `tmp_path` and never stays under the session's temp folder. Show it: before your change, the killed nested run's base folder stays under the session's `TMPDIR` after the case; after it, none does.
4. **Measure** (no load made on purpose): run the bounded functions alone ×3 (`-n auto`), and `tests/unit/close/` whole ×3 with `-n auto --dist worksteal` (the condition of lens I2's trials), each after the load check, and record for each run the 1-minute load at its start and end, the slowest nested case's duration, and its bound. State each bound's margin (bound ÷ slowest seen). The lead's full verification run measures them again beside the whole regression.

## What judges you

Run, all from this worktree, to the end:
- `tests/unit/close/` (`-n auto`) and with `--dist worksteal` as in step 4: every case passes;
- the W1-30 acceptance cases that use the close's runner, as a check that nothing else moved: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -m pytest tests/acceptance/W1-30/test_w1_30_close.py tests/acceptance/W1-30/test_w1_30_r11_parallel_runs.py -n 4 -q -p no:cacheprovider -rs -o tmp_path_retention_policy=failed` (you run them and read results only, Policy 2 (c));
- the ticket's temp-folder KPI cases (you run them and read results only): `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -m pytest tests/acceptance/W1-27/test_w2_67_temp_folders.py tests/acceptance/W1-27/test_w2_67_basetemp_refusal.py tests/acceptance/W1-27/test_w2_67_sweep_namespaces.py -n 2 -q -p no:cacheprovider -rs -o tmp_path_retention_policy=failed`: all pass;
- `tests/unit/guard/` (`-n auto`);
- then `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` once: it must end with no collection error; quote its last line.

## Commit

    git commit -m "DAEO-9nys (W2-67): <subject>" --trailer "Task: DAEO-9nys" --trailer "Role: engineer" --trailer "Implements: DEC-914, DEC-892" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

(the `--trailer` options come before `--`). Before each commit check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. After each commit, check `git log --oneline -2` and `git status --short`.

## Return

Your last message, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), with nothing before them, and any machine-readable payload after them. Put in it: the sandbox check (step 0) first in `work_completed`; every commit's 12-digit hash with its trailers; the functions found, each with its bound before and after; P1's before-and-after evidence; step 4's measurements; each other run with its counts; the `gov.__file__` line; the collection line; lines added and removed; your scratch figures; the read refusals met; whether you used `gov retrieve`; any package.

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

Refused twice for the same call: stop and say so; no third try.
