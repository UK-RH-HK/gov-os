You are a fresh independent test designer (MR-3). Ticket: DAEO-9nys (W2-67, "Test hygiene: per-test copies, nested runs, temp folders, and the weak tests' revisions"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-67` on branch `w2/W2-67`. This is the ticket's run 3 (rounds 2 and 3 together, DEC-914), batch 6 of its test design: you revise W1-30's 13 first-round cases, each shown red against a planted fault and green on the head; you bring one W1-30 case and two module docstrings up to the decisions that replaced theirs (row W2-L420); you widen one of this ticket's own round-1 guards; and you remove one inert file a past session left.

## Step 0: the sandbox check (before any work; report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-9nys','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return with the twelve fields, saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-9nys`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-67` and `w2/W2-67`) and `git log --oneline -1` (expect `6d44fc80`). If anything differs, stop and say so.

## Standing rules (read first)

- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commits exist. Your budget is about 90 minutes of wall time: note `date` when you start, keep working until every piece of this batch is done or 80 minutes have passed, commit each finished group as you go (see "Commit"), so nothing is lost if time runs out, and say in your return what is left.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- **Memory first (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -m gov.cli.main retrieve "<question>" --json`. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve`, and for what. (The store may answer `FACET_UNAVAILABLE` or stale: then say so and read the files named below.)
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return. Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one. Never read `.claude/settings.json`.
- **Policy 2 (DEC-820):** you read freely, except:
  - (a) secrets and keys, never printed;
  - (b) the contents of the held-out qualification material (never read, print, search, diff or copy the held-out file under `governance/project/`, never type its path; its name may be seen);
  - (c) **this ticket's implementation:** you never read, by any tool (Read, cat, grep, git show, git log -p, git diff), `tests/conftest.py`, `tests/unit/guard/test_decide.py`, anything under `tests/unit/close/` (an engineer changes these in this run), or `tests/acceptance/W1-07/w1_07_support.py`. You may **run** them (any pytest run under `tests/` loads the root conftest) and read their results and messages. The ticket's own acceptance tests and READMEs under `tests/acceptance/W1-27/` (`test_w2_67_*.py`, `w2_67_*.py`, `README-W2-67*.md`) are tests, not implementation: you read them;
  - (d) the hidden half of any evaluation set, by whoever is measured by it. Never read or name the qualification oracle.
- **Protected places:** never write in `~/gov-os-workbench` (never list, glob, search or write there); dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. No clone, copy or file of a programme under any `.gov-runtime/` folder (DEC-673).
- **No tree copying:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it, anywhere. A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. A test that needs a repository builds a temporary one from scratch. Inside this session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never edit `.tickets/`, the decision register, the path map (`governance/project/path-map.yaml`, owner-only, DEC-757) or anything under `src/`, `template/`, `schemas/`, `docs/`, `tests/unit/` or `tests/conftest.py`. **Never leave an untracked file in the worktree:** `rm` may be refused in your session, so put throwaway plants in your own folder under `.gov-runtime/scratch/td-6/` or your temporary folder, never under `tests/`.
- **Row W2-L423's rule (owner, standing, DEC-911):** under `.gov-runtime/` (your plants, evidence, notes), write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule". The same holds for your return.
- **Disk and inodes (DEC-898), your share:** the ticket's budget is 20 GB and 1,000,000 files and folders for the lead and all workers together; **your share is at most 8 GB and 300,000 files and folders at any moment**, in your temporary folder and this worktree's untracked files together. Keep `TMPDIR` as the sandbox sets it (count it). Keep pytest's own retention (three base folders); **never pass a per-run `--basetemp`** (the root conftest refuses it). **Pass `-o tmp_path_retention_policy=failed` on every pytest run you make** (DEC-905). Measure your temporary folder (`du -s --inodes`, `du -sh`) before and after each heavy run and give the figures in your return's `evidence` line. Remove every temporary tree you made as soon as it is no longer needed. If you pass your share, stop the heavy work at once, clean what you can and return.
- **The machine:** W1-30's cases each run `gov close` on a project of their own, with nested test runs. Before any run of more than a few cases, wait while the 1-minute load is above 20 (`until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done`). Run only the cases you need, by node id; never the whole of `tests/acceptance/W1-30/` at once. Never run with `-x`.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try.**
- You never ask or notify the owner (no question box, no `owner-ping`); a package comes back in your return. A behaviour below you find ambiguous, or in conflict with a KPI line or a decision, is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## What you read

- The ticket file `.tickets/DAEO-9nys.md` (read-only): its KPI lines (the fifth: "Each weak case revised is first shown red against a planted fault, then green on the head, each with a Rewrite-Reason; in this order: … W1-30's 13 first-round cases …") and its failure line. Its card: `docs/plan/WAVE_2_WBS.md` §2, the W2-67 card (from line 1152).
- The decisions in `docs/DECISION_REGISTER.md`: DEC-914 (this run), DEC-907, DEC-889 item 7, DEC-898, DEC-905, DEC-491 (Rewrite-Reason), DEC-718 (a row's state is re-checked against the code), DEC-866 (supersession: a test that enforces a superseded decision is revised with `Rewrite-Reason: <the new decision>` and lowers no other expectation), DEC-868 (items 1 (b) and 3: the pre-close gate and the gate order), DEC-908, and the entries it marks: DEC-455, DEC-480, DEC-454; DEC-281 and DEC-321 (the checkpoint watchdog).
- Lens I: `docs/assessment/2026-10/I2-close-checks-ratchet.md` §2.7 (the planted faults PF1, PF2, PF4, PF5, PF5b, PF9, PF10, PF11, PF12, PF13, PF15, PF16 and the weak-test table's W1-30 rows, lines 365 to 378), Finding 2 (from line 590) and package P-I2-5 (line 893); `docs/assessment/2026-10/I-SYNTHESIS.md` §5.2's W1-30 row.
- The row W2-L420 in `docs/plan/WAVE_2_LIST.md` (line 1073).
- `tests/acceptance/W1-30/` as it stands on this branch: its README, `w1_30_support.py`, and the files the 13 cases and W2-L420 live in. W2-07 (`DAEO-r9ss`, merged) revised several W1-30 cases and the fixture after lens I2 wrote; read its commits' messages on these files (`git log --format='%h %s%n%b' -- tests/acceptance/W1-30/`).
- The public interfaces the tests work with: `gov close` and its JSON envelope (`docs/interfaces/`), the ticket and checkpoint records, git. You read no private part of an implementation to learn what a test should expect; reading `src/gov/close/` to find where to plant a fault is allowed.
- For piece 3: `tests/acceptance/W1-27/test_w2_67_temp_folders.py`, `test_w2_67_basetemp_refusal.py` and `README-W2-67.md` (batches 1, 3 and 4 of this ticket).

## The behaviour to test

### Piece 1: W1-30's 13 first-round cases (KPI 5; I2 F2 and §2.7; P-IS-7 (a))

The 13, by I2's weak-test table:
- `test_w1_30_disposition.py::test_all_six_dispositions_recognized` (it asserts the support's own tuple, not the close's; PF1);
- `test_w1_30_disposition.py::test_disposition_with_context_failure` (it asserts only the absence of a literal the close never writes; PF2);
- `test_w1_30_close.py::test_close_requires_implements_trailer`, `::test_close_requires_task_trailer` (PF13);
- `test_w1_30_close.py::test_close_refuses_when_acceptance_tests_fail`, `::test_close_runs_acceptance_tests` (PF5, PF5b);
- `test_w1_30_close.py::test_containment_blocks_close_for_out_of_scope_commit` (PF4);
- `test_w1_30_close.py::test_task_trailer_exact_match_not_substring` (PF15);
- `test_w1_30_close.py::test_regression_runs_to_end_all_failures_collected`, `::test_regression_failure_blocks_close`, `::test_close_runs_regression_tests_when_present` (PF11, PF12, PF16);
- `test_w1_30_receipt.py::test_close_record_packet_hash_matches_context` (PF9);
- `test_w1_30_iteration.py::test_owner_decision_checker_failing_refuses` (PF10).

For each, first **re-check it on this branch's head (DEC-718)**: W2-07 changed some of them (for example, it gave some their checkpoint). Plant the case's fault (I2's PF-n) and run the case:
- if it already fails under its fault for the reason its name claims, and asserts that gate's own finding, it is not rewritten: record it as already sound, with the commit that made it so and the planted-fault evidence;
- otherwise revise it: its project gets what every ticket has before its close (its checkpoint, and whatever else the pre-close gate requires, so that it is refused or closed by the gate it names and not by an earlier one), and its assertion names its gate's own finding or result (for a success case, evidence that the gate actually ran and judged, not `ok` alone). Each revised case is first shown **red against its planted fault**, then **green on the head**; lowers no expectation; keeps its name unless the name states a removed rule; and is committed with a `Rewrite-Reason:` naming why it was weak (I2's own wording, e.g. "refused for the missing checkpoint, not for the gate it names"; "it read the support's constant"; "refused before the checker was asked"; "accepted any string when the context could not be read").
- `test_w1_30_close.py::test_close_runs_containment_check` is not yours: its retirement (P-I2-5) is undecided. Leave it unchanged and name it.
- A case whose honest revision is red **on the head** because the code itself is wrong is not committed red: name it with the evidence, as a finding for the ticket that owns that code.

### Piece 2: row W2-L420 (DEC-866)

`tests/acceptance/W1-30/test_w1_30_context_failures.py::test_a_decision_checker_that_cannot_run_refuses_the_close` still asserts a counted refusal (DEC-455's rule, changed by DEC-868 item 3 and DEC-908); the module docstrings of `test_w1_30_governance_checks.py` and `test_w1_30_context_failures.py` still describe DEC-480's and DEC-455's old rules. Bring the case and the two docstrings to DEC-868 and DEC-908, as W2-07 did for the other cases of these files (read its commits there). `Rewrite-Reason: DEC-868 item 3 and DEC-908 (DEC-455 and DEC-480 changed)`; no other expectation lowered. Show the case red against a planted fault of the behaviour it now asserts, and green on the head. If what DEC-868 requires of this case is unclear (for example, which refusal and exit a checker that cannot run gets), return a package, never a guess.

### Piece 3: P-W2-67-TD4-A (round 1's review F3; DEC-914 item 2)

KPI 4's static guard in `tests/acceptance/W1-27/test_w2_67_temp_folders.py` (batch 4's revision) finds an argument list that passes `--basetemp` as a separate option or as a plain `--basetemp=` string, but not an f-string whose literal start is `--basetemp=` (`f"--basetemp={folder}"`). Widen it to catch that form too, and widen the refusal cases' exemption to the f-string forms of the FORMS table's own parameter only, so that `test_w2_67_basetemp_refusal.py` stays green. Red against a plant (an f-string `--basetemp=` in a source the guard reads, planted through a scratch root or a monkeypatched source list as batch 4 did, never an untracked file under `tests/`), green on the head. It raises the expectation only. `Rewrite-Reason: P-W2-67-TD4-A (DEC-914 item 2): the guard missed an f-string --basetemp=`. If the widened guard is red on the head because a file outside this ticket's folders passes an f-string `--basetemp`, do not exempt it: name it and return a package. Add a short section "Batch 6" to `tests/acceptance/W1-27/README-W2-67.md`.

### Piece 4: the inert plant

Remove `tests/acceptance/W1-27/w2_67_td4_plant.py`, an untracked file a round-1 session left (a docstring only): `rm /home/usain/gov-os-worktrees/W2-67/tests/acceptance/W1-27/w2_67_td4_plant.py`, once. If it is refused, do not try again or by another route: say so.

## Planting a fault

You may not write `src/`, and you may not copy the tree. Plant each fault in a throwaway that the run picks up and that leaves the tracked tree untouched (for example a small module in `/home/usain/gov-os-worktrees/W2-67/.gov-runtime/scratch/td-6/` placed first on the child processes' import path, that imports the real package and replaces one behaviour), and record each plant (the fault in words, how it was planted, the command, the result, a JUnit XML) under `/home/usain/gov-os-worktrees/W2-67/.gov-runtime/scratch/td-6/plant/`. If the Write tool is refused there, write the plant module in your session scratchpad and copy that one named file into that folder with `cp <file> <folder>/` (a single named file, not a tree). Make sure the plant reaches the `gov close` the case starts (its child process and that child's own nested test runs, if the fault lives there): show, for each plant, that the planted behaviour was the one that ran (for example a marker file the plant writes). A case you cannot show red against any plant without writing `src/` is named in your return, with what you tried; it is not committed as revised.

## What you write

- Only inside `tests/acceptance/W1-30/` (pieces 1 and 2) and, for piece 3, `tests/acceptance/W1-27/test_w2_67_temp_folders.py` and `tests/acceptance/W1-27/README-W2-67.md`. A shared file (the W1-30 support module, its README) is touched only on lines of your own; changing the support module must keep every other W1-30 case's result: run the cases of each file you change.
- A `tests/acceptance/W1-30/README-W2-67.md`, pointed to from the W1-30 README: for each of the 13 cases and W2-L420's, its planted fault, its red and green evidence (or "already sound", with the commit), its Rewrite-Reason; every case left, and why.
- FULL proportion: thorough on every case of this batch; no combinatorial expansion beyond what a KPI demands. Deterministic, no network. Tests that need a repository build a temporary one.
- Run every revised case on the head (green) and under its plant (red), by node id, to the end. Then run each W1-30 file you changed, whole, on the head (`-n 4` at most, after the load check), and `test_w2_67_temp_folders.py` and `test_w2_67_basetemp_refusal.py`: no other result may change.
- Before your last commit, run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` once: it must end with no collection error; quote its last line.

## Commit

Commit only your test paths, a group at a time (the trailer and task cases with their one reason, the acceptance and regression cases, …, W2-L420's, piece 3), with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "DAEO-9nys (W2-67): <subject>" --trailer "Task: DAEO-9nys" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-914, DEC-889" --trailer "Rewrite-Reason: <reason>" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

(the `--trailer` options come before `--`; after it git reads them as paths). A README-only commit carries no `Rewrite-Reason`. Before each commit check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. After each commit, check `git log --oneline -2` and `git status --short`.

## Return

Your last message, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), with nothing before them, and any machine-readable payload after them. Put in it: the sandbox check (step 0) first in `work_completed`; every commit's 12-digit hash with its trailers; for each of the 13 cases and W2-L420's, its plant, red and green (or "already sound", with the commit); piece 3's red and green; piece 4's result; every case you could not revise and why; each changed file's lines added and removed; the `gov.__file__` line; the collection line; your scratch figures; the read refusals met; whether you used `gov retrieve`; any package.

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
