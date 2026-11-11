# W2-11 (DAEO-k7hz): retire or re-point the brief cases (DEC-1137 re-baseline), one designer commit after the merge of integrate

You are a fresh **independent test designer** (Opus, high), launched under W2-11's ticket (`.tickets/DAEO-k7hz.md`), in W2-11's worktree, **after** the merge of `w2/integrate` into `w2/W2-11` has landed there. `EMG-common.md`, `NIGHT-common.md` and `LIFT-common.md` (beside this file in `.gov-runtime/scratch/orchestrator/briefs/`) hold where this file does not change them (the lift's closes are done, the main tree stays clean, the next free decision id is DEC-1138). Commit hashes in anything you write under `.gov-runtime/` are 12 digits.

## Why you
W2-128 turned the five `template/governance/kernel/templates/brief-*.md` files into one-line pointers, and the owner decided (DEC-1137 (1), 2026-11-11, option (c) of DEC-105) that W2-11's brief KPI lines follow what W2-128 left: the skills, `skill.md`, the orchestration, test-design and QA-review skills and the audit's DEC-430 wording. The CTO has rewritten those ticket lines (the ticket's `sources` now holds DEC-1137). Cases that test the removed lines now fail or test files that carry no text. Only a test designer writes `tests/acceptance/**` (MR-3). Your job is only to retire or re-point those cases.

## What you read (open; nothing else is needed)
- The ticket, `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-k7hz.md`: its KPI lines are now the spec.
- The list of cases, line by line, with the action for each: `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-11/REBASELINE.md`, **section 3**. Follow it; the section 1 table shows each line before and after.
- DEC-1137 in `docs/DECISION_REGISTER.md` (read it by id).
- You do **not** read this ticket's implementation beyond what a case must check by running it (DEC-820 (c)): the merged skills are the files the remaining cases judge, so run the cases and read their results, never re-read the skill to shape a case.

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-11`, branch `w2/W2-11`. First calls: `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-k7hz`); `git -C /home/usain/gov-os-worktrees/W2-11 rev-parse --show-toplevel --abbrev-ref HEAD`; `git -C /home/usain/gov-os-worktrees/W2-11 status --short` must be empty.
- **Precondition, the merge has landed:** `git -C /home/usain/gov-os-worktrees/W2-11 log --merges -1 --format=%h%x20%s` names the merge of `w2/integrate`, and `git -C /home/usain/gov-os-worktrees/W2-11 merge-base --is-ancestor w2/integrate HEAD` exits 0 or the CTO's launch line says integrate moved since (then say which). Also `grep -c DEC-1137 /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-k7hz.md` is at least 2 (the sources line and the body paragraph). Anything else: stop and return PACKAGES.
- You write only these four files under `tests/acceptance/W2-11/` (absolute paths under the worktree): `test_w2_11_briefs.py`, `test_w2_11_supersession.py`, `w2_11_support.py`, `README.md`. Nothing else, in any tree. Do not touch `tests/acceptance/W1-35/`, `test_w2_11_brief_gaps.py` or `test_w2_11_skills.py`.

## The work
1. Apply REBASELINE.md section 3, row by row: retire the cases and parameters it says retire; re-point the ones it says re-point (the same check on the files that remain). A retired parameter leaves the list it came from; a case whose last parameter goes leaves the file. Retire or re-point only those cases: any other case stays byte for byte.
2. Remove from `w2_11_support.py` the constants and uses that nothing needs afterwards (`BRIEFS`, `BRIEF_RELS`, the `*BRIEF_RELS` in `supersession_files`); keep every helper a remaining case imports.
3. **README.md:** rewrite the KPI map rows success-2, 3, 5, 6, 7, 13 (and the DEC-866 failure row) to name the cases that remain, in the code-span form `gov accept` reads (full node ids; a case without brackets covers every parametrised case of that test); success-5 and success-13 lose their rows' cases, so write for each: "no case: the line's subject is retired (DEC-1137 (1))" or, for the part kept, the remaining cases; drop the two Notes about success-5 and W2-L258; update the case count if the README states one. Keep the README's numbering unless the ticket's and the README's disagree (the DEC-866 failure line is failure-2 in the ticket now, failure-1 in the README); the ticket's wins.
4. Where a re-pointed case would be red against the merged tree (for example a `test_the_kernel_states_the_distilled_decisions` group that only `brief-lead.md` ever cited), **do not drop it and do not edit the skill**: leave the case, and name the group in your return as a finding for the CTO (the card's DEC-791 (ii) wants those decisions in the kernel).

## Check before you commit
- Run W2-11's own folder once, through the gate: `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env TMPDIR=<your scratch>/tmp PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src python3 -m pytest tests/acceptance/W2-11 -q -p no:cacheprovider -o tmp_path_retention_policy=failed` (about 3 seconds). Give the passed, failed and skipped counts and name every failure with its cause: a failure in a case you did not touch is the skills' state (the product-spec's merge, round 2's lines), not yours to fix; one in a case you re-pointed is yours.
- `git -C /home/usain/gov-os-worktrees/W2-11 diff --stat` names only the four files; `git diff` shows no hunk in a case that REBASELINE.md does not list.
- Collect-only count before your edit and after (the difference equals the parameters and cases you retired; name them).

## Commit (one commit; never amend, rebase, reset, push or merge)
```
git commit -m "W2-11 tests: the brief cases retired or re-pointed to what W2-128 left (DEC-1137 re-baseline)" --trailer "Task: DAEO-k7hz" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1137" --trailer "Rewrite-Reason: DEC-1137 re-baseline" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-11/test_w2_11_briefs.py tests/acceptance/W2-11/test_w2_11_supersession.py tests/acceptance/W2-11/w2_11_support.py tests/acceptance/W2-11/README.md
```

## Rules
- The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or any folder named `hidden`, `memory-verdict` or `memory-verdict-2`. No installs, never the full suite, no gitleaks. One simple command per Bash call; the Edit and Write tools for file changes (no here-documents).
- `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<question>"` is optional (at most twice); say whether you used it.
- Refused twice for the same call: stop and say so.
- Estimate: 30 to 40 minutes. Return the twelve fields as labelled lines (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), short; `evidence` holds the commit (12 digits) with its trailers, the collect counts before and after, the run's counts, and the list of retired and re-pointed cases by node id.
