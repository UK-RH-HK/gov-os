You are a fresh independent test designer (MR-3). Ticket: DAEO-uzme (W2-70), profile LITE, class test-revision. You work only in the worktree `/home/usain/gov-os-worktrees/W2-70` on branch `w2/W2-70`. This ticket has no implementer: your two commits are the whole change. Every change under `tests/acceptance/` is yours (owner, standing, DEC-906 item 1).

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-uzme','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return, saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-uzme`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-70` and `w2/W2-70`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, every test run and every `gov` command used for verification runs this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-70/src` set per command (never in a session's `--settings` env). Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **Memory used (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-70/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in your return whether you used `gov retrieve` and for what.
- **Read refusals (DEC-849):** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count every refusal you met and give the count in your return.
- **Policy 2 (DEC-820):** reads are open, writes are closed to your paths. Refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, search, diff or copy it; never read or name the qualification oracle); (c) the counterpart's work on this ticket: the test designer never reads this ticket's implementation (the files `git diff --name-only w2/integrate...HEAD` names, other than its own tests) — here there is no implementation, so this only means you build on the files as they stand; (d) the hidden half of any evaluation set, by whoever is measured by it. Never write in `~/gov-os-workbench`.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Run everything in the foreground, one command after another; return only after your commits exist. No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag. Never `--no-verify`, never `core.hooksPath`.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of it). A test that needs a repository builds a temporary one from scratch with `git init` in pytest's `tmp_path`. No clone, copy or programme file under any `.gov-runtime/` folder. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- Write files with the Write and Edit tools and literal absolute paths (the guard refuses here-documents and unresolved variables in Bash write targets). No subagents that write. Install nothing. Never write `.gov-runtime/**`. Never write `governance/project/path-map.yaml` (owner-only).
- **Disk budget (DEC-898):** the lead and all workers share 20 GB and 1,000,000 files and folders outside the tracked tree; **your share is 10 GB and 500,000.** Your temp folder is the one the sandbox sets (or `/tmp/gov-os-lead-W2-70`); keep pytest's own retention (never a per-run `--basetemp`); pass `-o tmp_path_retention_policy=failed` to every pytest run; clean up anything you made as soon as it is not needed. Measure `du -s --inodes` and `du -sh` of your temp folder at the end and give the figures in your return.
- No full-suite run is needed from you: run only the files you changed, plus the collection checks named below. Never `-x`.

## What you read

- `.tickets/DAEO-uzme.md` (read-only): its KPI lines and `allowed_paths`.
- The card: `docs/plan/WAVE_2_WBS.md`, section "W2-70" (around line 1089), and section 0's rules.
- In `docs/DECISION_REGISTER.md`: DEC-899 (item 1 and its P-IS-3 (a)), DEC-900, DEC-906 (all of it), DEC-491 (rewrite trailers), DEC-892, DEC-889.
- The files you revise, as they stand: `tests/acceptance/W1-05/` (its `test_w1_05_switch_over_record.py`, README, support), `tests/acceptance/W1-47/` (its `test_w1_47_session_role.py`, README), `tests/acceptance/serial-only.txt`, `tests/acceptance/W1-30/test_w1_30_r11_declared_here.py`, `tests/acceptance/W1-01/test_w1_01_history.py`, `tests/acceptance/W1-01/w1_01_support.py`, `tests/acceptance/W1-01/README.md`.
- The path map's `accepted_history` list, which the new list sits beside: read `governance/project/path-map.yaml` by that exact name (no search over `governance/project/`).

## The behaviour to change

Write only inside the ticket's `allowed_paths`: `tests/acceptance/W1-05/**`, `tests/acceptance/W1-47/**`, `tests/acceptance/serial-only.txt`, `tests/acceptance/W1-30/test_w1_30_r11_declared_here.py`, `tests/acceptance/W1-01/test_w1_01_history.py`, `tests/acceptance/W1-01/w1_01_support.py`. Nothing else (DEC-906 failure KPI: "any other test changed"). Proportion LITE: one case per KPI line, plus the three named fixture cases below.

### Commit 1 — the two retirements (DEC-899, P-IS-3 (a))

1. Retire W1-05's switch-over case, `tests/acceptance/W1-05/test_w1_05_switch_over_record.py::test_the_dependencies_pass_their_acceptance_tests_at_the_switch_over`, which re-runs W1-02's, W1-03's and W1-04's acceptance suites in a child pytest process. Its KPI was a one-time order at W1-05's close. The other case in that file (the operator diff check recorded as retired) stays unchanged. Remove whatever in W1-05's support or README then serves nothing, and say in W1-05's README that the case is retired, by DEC-899, and why (one short paragraph).
2. Retire W1-47's builder case, `tests/acceptance/W1-47/test_w1_47_session_role.py::test_the_builder_tests_of_the_guard_pass`, which re-runs `tests/unit/guard` in a child process. Update W1-47's README row for success 7 to say the builder suite runs as itself in every close and the nested rerun is retired by DEC-899. Leave every other W1-47 case alone (`w1_47_support.py`'s `tests/unit/guard/**/*` glob is a different matter: leave it unless it only served the retired case).
3. The switch-over line leaves `tests/acceptance/serial-only.txt`. No other line of that file changes.
4. W1-30's r11 test (`test_w1_30_r11_declared_here.py`), which holds the declared entries one by one, drops the switch-over node from its table, and nothing else.
5. **Nothing else changes:** the suites the two cases re-ran (`tests/acceptance/W1-02`, `W1-03`, `W1-04`, and `tests/unit/guard`) are not touched and still run as themselves in every close. Show it: they still collect (`--collect-only -q`) with this worktree's `src/`.
6. Run the files you changed (W1-05, W1-47, W1-30's r11 file), to the end; they must be green, except anything already red before your change (say which, with the message). Then commit only those paths:

       git commit -m "W2-70 (DAEO-uzme): retire W1-05's switch-over rerun and W1-47's builder rerun (DEC-899)" --trailer "Task: DAEO-uzme" --trailer "Role: independent-test-designer" --trailer "Implements: independent-test-designer" --trailer "Retire-Reason: DEC-899 (P-IS-3 (a)): both cases re-run whole suites the same close already runs as themselves; they cost about 15 minutes of every close and block worksteal" --trailer "Rewrite-Reason: DEC-899: W1-30's r11 table drops the retired switch-over entry" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

### Commit 2 — W1-01's history case reads an exact-commit exemption list (DEC-906 item 2)

The case is `tests/acceptance/W1-01/test_w1_01_history.py::test_only_the_test_designer_commits_to_acceptance_tests`. It has been red on `w2/integrate` since the owner's commit `c9a08678644485a7528bc875164e110881b63d93` (DEC-900's retirement), which touched `tests/acceptance/` with `Role: owner`.

The behaviour, in the decision's words:
- The case reads the path map's `acceptance_exemptions` (in `governance/project/path-map.yaml`, beside `accepted_history`): a list of exact commits, each `{commit: <full sha>, decision: <DEC id>}`.
- A **non-merge** commit that touches `tests/acceptance/` without the test designer's role passes **only when its full sha is listed there.** A prefix or abbreviated sha in the list exempts nothing.
- Any other commit stays red, an owner's included. A `Role: owner` trailer alone exempts nothing (it is only text until W2-44).
- The merge rule (DEC-253) and the test designer's rule stay as they are.
- A path map with no `acceptance_exemptions` key, or an empty list, exempts nothing (it is not an error that turns the case green or skips it).
- The list's only entry will be `c9a08678644485a7528bc875164e110881b63d93`, citing DEC-900. It is the owner's own commit, not yours, and it may not be on this branch yet: you never write the path map. Until it is in, the real-repository case stays red with a message naming `c9a08678` — that red is expected; say so in W1-01's README (`tests/acceptance/W1-01/README.md` is NOT in your paths; put the note as a docstring in the test file instead, and name the README update as a residual in your return).

Test the case's logic against fixtures: temporary git repositories built from scratch in `tmp_path` (with `git init`, a stand-in path map at `governance/project/path-map.yaml` inside the fixture, and commits under `tests/acceptance/`), through the same helper the real case uses. Three fixture cases, at least:
1. **A listed commit passes:** a non-merge `Role: owner` commit touching `tests/acceptance/`, whose full sha is listed, is not an offender.
2. **An unlisted owner commit stays red:** a second `Role: owner` commit touching `tests/acceptance/`, not listed, is an offender.
3. **A listed sha with a different commit's content is not accepted:** a commit that looks like the listed one (same message, same trailers, same author) but whose content differs, so its full sha differs from the listed one, stays red; and a list entry giving only an abbreviated sha of a real offender exempts nothing.

Run W1-01's history file to the end. Expected: the three fixture cases green; the real-repository case red only because `c9a08678` is not yet listed (quote the message). Then commit only your W1-01 paths:

    git commit -m "W2-70 (DAEO-uzme): W1-01's history case reads the exact-commit exemption list (DEC-906)" --trailer "Task: DAEO-uzme" --trailer "Role: independent-test-designer" --trailer "Implements: independent-test-designer" --trailer "Rewrite-Reason: DEC-906: an owner commit touching tests/acceptance/ passes only when its full sha is listed in the path map's acceptance_exemptions" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After each commit, run `git log --oneline -2`, `git log -1 --format=%B` and `git status --short`, and quote them.

## Last checks

- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-70/src python3 -m pytest tests/acceptance/W1-02 tests/acceptance/W1-03 tests/acceptance/W1-04 tests/unit/guard --collect-only -q -p no:cacheprovider | tail -3`: the covered suites still collect.
- `git diff --name-only 23518192 HEAD`: only allowed paths.
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Return

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

Your last message is your return: the twelve fields above first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Put in it: the sandbox check's result first, both commit hashes with their trailers, the test counts, the red reason of the real-repository case as you saw it, every earlier test you rewrote with its reason, whether you used `gov retrieve`, the count of read refusals, your scratch measure. Refused twice for the same call: stop and say so; no third try.
