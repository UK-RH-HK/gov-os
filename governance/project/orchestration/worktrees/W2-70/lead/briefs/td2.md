You are a fresh independent test designer (MR-3). Ticket: DAEO-uzme (W2-70), profile LITE, class test-revision. You work only in the worktree `/home/usain/gov-os-worktrees/W2-70` on branch `w2/W2-70`. This ticket has no implementer: your commit is part of the whole change. Every change under `tests/acceptance/` is a test designer's (owner, standing, DEC-906 item 1).

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-uzme','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return, saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-uzme`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-70` and `w2/W2-70`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, every test run and every `gov` command used for verification runs this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-70/src` set per command (never in a session's `--settings` env). Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **Memory used (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-70/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in your return whether you used `gov retrieve` and for what.
- **Read refusals (DEC-849):** the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count every refusal you met and give the count in your return.
- **Policy 2 (DEC-820):** reads are open, writes are closed to your paths. Refused: (a) secrets and keys, never printed — **never print environment variables** (`env`, `printenv` with no name, `os.environ` dumps, `GIT_*` dumps): the sandbox's environment holds a credential; (b) the contents of the held-out qualification material (never read, search, diff or copy it; never read or name the qualification oracle); (c) the counterpart's work on this ticket: the test designer never reads this ticket's implementation (the files `git diff --name-only w2/integrate...HEAD` names, other than tests) — here there is no implementation; the W1-01 files are earlier tests you revise; (d) the hidden half of any evaluation set, by whoever is measured by it. Never write in `~/gov-os-workbench`.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Run everything in the foreground, one command after another; return only after your commit exists. No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag. Never `--no-verify`, never `core.hooksPath`.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of it). A test that needs a repository builds a temporary one from scratch with `git init` in pytest's `tmp_path`. No clone, copy or programme file under any `.gov-runtime/` folder. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- Write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing. Never write `.gov-runtime/**`. Never write `governance/project/path-map.yaml` (owner-only). Keep any scratch script inside pytest's or the sandbox's temp folder, not in a place you cannot remove.
- **Disk budget (DEC-898):** the lead and all workers share 20 GB and 1,000,000 files and folders outside the tracked tree; **your share is 5 GB and 250,000.** Your temp folder is the one the sandbox sets; keep pytest's own retention (never a per-run `--basetemp`); pass `-o tmp_path_retention_policy=failed` to every pytest run; clean up anything you made. Measure `du -s --inodes` and `du -sh` of your temp folder at the end and give the figures in your return.
- No full-suite run is needed from you: run only the W1-01 folder. Never `-x`.

## What you read

- `.tickets/DAEO-uzme.md` (read-only): its KPI lines (the last success line is yours) and `allowed_paths`.
- In `docs/DECISION_REGISTER.md`: DEC-906 (all of it), DEC-908 (item 3), DEC-253, DEC-491.
- The files you revise, as they stand on this branch: `tests/acceptance/W1-01/w1_01_support.py` (its `merge_offences`, `acceptance_exemptions` and `acceptance_test_offenders`), `tests/acceptance/W1-01/test_w1_01_integration_merges.py`, `tests/acceptance/W1-01/test_w1_01_history.py` (its fixture cases show how this ticket built temporary repositories with a stand-in path map).
- The path map's `acceptance_exemptions` (now on this branch, the owner's commit `18ad2382`): read `governance/project/path-map.yaml` by that exact name.

## The behaviour to change (DEC-908 item 3, applying DEC-906)

The case is `tests/acceptance/W1-01/test_w1_01_integration_merges.py::test_the_integration_merges_of_this_repository_pass`, which judges every merge on HEAD's history touching `tests/acceptance/` by the DEC-253 rule. Under that rule a merge passes only when every commit it brings from the merged side that touches `tests/acceptance/` carries the test designer's role. A branch made before `c9a08678` that merges `w2/integrate` back brings `c9a08678` (the owner's listed commit), so such a merge is red under the old rule even though the commit itself is listed.

The KPI line, word for word: "W1-01's integration-merge case (test_the_integration_merges_of_this_repository_pass) reads the same list through merge_offences: a merge that brings a listed commit's changes passes; one that brings an unlisted commit without the test designer's role stays red; Rewrite-Reason: DEC-906 [DEC-908 item 3]".

- A commit the merge brings is accepted when it carries the test designer's role, or when its **full sha** is listed in the path map's `acceptance_exemptions` (the same list, read the same way as the history case reads it: an abbreviated sha, a missing key, an empty list exempt nothing; a `Role: owner` trailer alone exempts nothing).
- Everything else in the DEC-253 rule stays exactly as it is: a merge whose own changes go beyond what its parents hold stays red, whatever it brings.
- No other expectation is lowered. The offender line format stays.

Write only inside `tests/acceptance/W1-01/w1_01_support.py`, `tests/acceptance/W1-01/test_w1_01_integration_merges.py` and, if you need it, `tests/acceptance/W1-01/test_w1_01_history.py`. Nothing else.

Proportion LITE: one fixture case per clause of the KPI line, built in temporary git repositories in `tmp_path`:
1. **A merge that brings a listed commit's changes passes:** a branch made before an owner (`Role: owner`) commit touching `tests/acceptance/`, the owner commit listed by its full sha in the fixture's path map, then the branch merges the line holding it back: the merge has no offence.
2. **A merge that brings an unlisted commit without the role stays red:** the same shape with the owner commit not listed (or listed only by an abbreviated sha): the merge is an offence naming that commit.

Run the whole W1-01 folder to the end; every case must be green (the history case is green now that the owner's entry is in). Then commit only your paths:

    git commit -m "W2-70 (DAEO-uzme): W1-01's integration-merge case reads the exact-commit exemption list (DEC-908)" --trailer "Task: DAEO-uzme" --trailer "Role: independent-test-designer" --trailer "Implements: independent-test-designer" --trailer "Rewrite-Reason: DEC-906 (DEC-908 item 3): a merge that brings a commit listed by its full sha in acceptance_exemptions passes; an unlisted commit without the role stays red" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After the commit, run `git log --oneline -2`, `git log -1 --format=%B` and `git status --short`, and quote them. Then `git diff --name-only e04e6ee6 HEAD`: only your paths.

An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

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

Your last message is your return: the twelve fields above first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Put in it: the sandbox check's result first, the commit hash with its trailers, the test counts, every earlier test you rewrote with its reason, whether you used `gov retrieve`, the count of read refusals, your scratch measure. Refused twice for the same call: stop and say so; no third try.
