Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-11 (DAEO-k7hz): retire or re-point the brief cases (DEC-1137 re-baseline), one designer commit after the merge of integrate

You are a fresh **independent test designer** (Opus, high), launched under W2-11's ticket (`.tickets/DAEO-k7hz.md`), in W2-11's worktree, **after** the merge of `w2/integrate` into `w2/W2-11` has landed there. `EMG-common.md`, `NIGHT-common.md` and `LIFT-common.md` (beside this file in `.gov-runtime/scratch/orchestrator/briefs/`) hold where this file does not change them (the lift's closes are done, the main tree stays clean, the next free decision id is DEC-1139: you never write a decision). Commit hashes in anything you write under `.gov-runtime/` are 12 digits.

## Why you
W2-128 turned the five `template/governance/kernel/templates/brief-*.md` files into one-line pointers, and the owner decided (DEC-1137 (1), 2026-11-11, option (c) of DEC-105) that W2-11's brief KPI lines follow what W2-128 left: the skills, `skill.md`, the orchestration, test-design and QA-review skills and the audit's DEC-430 wording. The CTO has rewritten those ticket lines (the ticket's `sources` now holds DEC-1137). Cases that test the removed lines now fail or test files that carry no text. Only a test designer writes `tests/acceptance/**` (MR-3). Your job is only to retire or re-point those cases.

## What you read (open; nothing else is needed)
- The ticket, `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-k7hz.md`: its KPI lines are now the spec.
- The list of cases, line by line, with the action for each: `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-11/REBASELINE.md`, **section 3**. Follow it; the section 1 table shows each line before and after.
- DEC-1137 in `docs/DECISION_REGISTER.md` (read it by id).
- You do **not** read this ticket's implementation beyond what a case must check by running it (DEC-820 (c)): the merged skills are the files the remaining cases judge, so run the cases and read their results, never re-read the skill to shape a case.

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-11`, branch `w2/W2-11`. First calls: `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-k7hz`); `git -C /home/usain/gov-os-worktrees/W2-11 rev-parse --show-toplevel --abbrev-ref HEAD`; `git -C /home/usain/gov-os-worktrees/W2-11 status --short` must be empty.
- **Precondition, the merge has landed:** `git -C /home/usain/gov-os-worktrees/W2-11 log --merges -1 --format=%h%x20%s` names the merge of `w2/integrate`, and `git -C /home/usain/gov-os-worktrees/W2-11 merge-base --is-ancestor w2/integrate HEAD` exits 0 or the CTO's launch line says integrate moved since (then say which). Also `grep -c DEC-1137 /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-k7hz.md` is at least 2 (the sources line and the body paragraph). Anything else: stop and return PACKAGES. The merge is `4e265aabed5c` (the CTO's, 2026-11-11); **one product-spec commit may sit above it** (the restore of W2-11's own skill text, `W2-11-A4-skills-restore.md`): `git -C /home/usain/gov-os-worktrees/W2-11 log --format=%h%x20%an%x20%s 4e265aabed5c..HEAD` shows that commit alone (its `Role: product-spec`), or nothing. Any other commit above the merge: say which and go on only if it touches no file under `tests/acceptance/`.
- **The CTO's launch note (2026-11-11 21:55 UTC, session b2f0511f): integrate moved since the merge.** `w2/integrate` is now `37066e82a654`; the commits since W2-11's merge base are W2-105's land and close (its install-block cases, `tests/acceptance/W2-105/`, `tests/acceptance/W1-38/`, `template/.rulesync/permissions.jsonc`), W2-149's probe record and the CTO's handover records. None touches `tests/acceptance/W2-11/`, the kernel skills or templates, or `.claude/skills`/`.rulesync/skills` (checked with `git diff --name-only w2/W2-11...w2/integrate`). So the ancestor check exiting 1 is expected: name it in your return and go on; do not merge integrate yourself. The restore commit above the merge is `c174e2c7f799` (product-spec).
- You write only these four files under `tests/acceptance/W2-11/` (absolute paths under the worktree): `test_w2_11_briefs.py`, `test_w2_11_supersession.py`, `w2_11_support.py`, `README.md`. Nothing else, in any tree. Do not touch `tests/acceptance/W1-35/`, `test_w2_11_brief_gaps.py` or `test_w2_11_skills.py`.

## The work
1. Apply REBASELINE.md section 3, row by row: retire the cases and parameters it says retire; re-point the ones it says re-point (the same check on the files that remain). A retired parameter leaves the list it came from; a case whose last parameter goes leaves the file. Retire or re-point only those cases: any other case stays byte for byte.
2. Remove from `w2_11_support.py` the constants and uses that nothing needs afterwards (`BRIEFS`, `BRIEF_RELS`, the `*BRIEF_RELS` in `supersession_files`); keep every helper a remaining case imports.
3. **README.md:** rewrite the KPI map rows success-2, 3, 5, 6, 7, 13 (and the DEC-866 failure row) to name the cases that remain, in the code-span form `gov accept` reads (full node ids; a case without brackets covers every parametrised case of that test); success-5 and success-13 lose their rows' cases, so write for each: "no case: the line's subject is retired (DEC-1137 (1))" or, for the part kept, the remaining cases; drop the two Notes about success-5 and W2-L258; update the case count if the README states one. **Renumber the whole map to the ticket's lines (the ticket's numbering wins; `gov accept` reads the n-th success and n-th failure line of the ticket by number).** The README (and REBASELINE.md's section 3, whose "KPI line" column is still the README's old numbers) were written before DEC-1137 removed the launcher line and before DEC-983 and DEC-1112 added lines; checked against the ticket file today (16 success lines, 2 failure lines), the numbers shift from the sixth line on:

   | README today | the ticket's line now (what it says) | README after your edit |
   |---|---|---|
   | success-1 to success-4 | S1 to S4 (proportion; twelve fields; Policy 2 and the record rule; DEC-430) | success-1 to success-4, unchanged numbers, rows rewritten as above |
   | success-5 (launcher command) | removed by DEC-1137 | no row |
   | success-6 (record frontmatter, loose citations) | S5 (loose citations) | **success-5** |
   | success-7 (supersession) | S6 | **success-6** |
   | success-8 (test kinds) | S7 | **success-7** |
   | success-9 (fixed gaps stay fixed) | S8 | **success-8** |
   | success-10 (one skill template) | S9 | **success-9** |
   | success-11 (test-design's work order) | S10 | **success-10** |
   | success-12 (orchestration's reference files, qa-review) | S11 | **success-11** |
   | success-13 (`brief_gaps`, to Wave 3) | S12 | **success-12** (the row's case goes: write "no case: the first half's subject is retired (DEC-1137 (1)); the second half is Wave 3's (DEC-1083)") |
   | success-14, 15, 16 (round 2's lines: no case yet) | S13 (anti-drift kit), S14 (scope control), S15 (timing test) | success-13, 14, 15: only the paragraph "Round 2's lines" is renumbered; no row, no case (the lead's next test-design batch writes them) |
   | (none) | S16 (the approvals section; DEC-991, round 2) | success-16: named in the same paragraph, no row |
   | failure-1 (the DEC-866 line) | F2 | **failure-2** (row and the paragraph "The failure line that moved" reworded to say so) |
   | (none) | F1 (a permission field in a skill's front matter; round 2) | failure-1: named in the "Round 2's lines" paragraph, no row |

   Renumber every `success-N` and `failure-N` in the README the same way (rows, notes and paragraphs); the case names, node ids and red reasons do not change. The comments inside the test files that say "KPI 12" and the like stay as they are (they are not read).
4. Where a re-pointed case would be red against the merged tree (for example a `test_the_kernel_states_the_distilled_decisions` group that only `brief-lead.md` ever cited), **do not drop it and do not edit the skill**: leave the case, and name the group in your return as a finding for the CTO (the card's DEC-791 (ii) wants those decisions in the kernel).

## Check before you commit
- Run W2-11's own folder once, through the gate: `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env TMPDIR=<your scratch>/tmp PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src python3 -m pytest tests/acceptance/W2-11 -q -p no:cacheprovider -o tmp_path_retention_policy=failed` (about 3 seconds). Give the passed, failed and skipped counts and name every failure with its cause: a failure in a case you did not touch is the skills' state (the product-spec's merge, round 2's lines), not yours to fix; one in a case you re-pointed is yours. **Expected reds you do not touch (the CTO's measure, 2026-11-11, with the restored skill text):** the cases that compare a generated `.claude` copy with its source, red until the copies ACT: `test_w2_11_skills.py::test_every_copy_carries_the_kernel_skills_body[test-design]` and `[orchestration]`, `test_w2_11_skills.py::test_the_skill_carries_one_version_in_all_four_places[discovery]`, `[orchestration]`, `[retrieval]` and `[test-design]`, and `test_w2_11_supersession.py::test_the_file_teaches_no_superseded_rule[.claude/skills/orchestration/SKILL.md]`. Name them and add no others to your return unless the run shows another.
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
