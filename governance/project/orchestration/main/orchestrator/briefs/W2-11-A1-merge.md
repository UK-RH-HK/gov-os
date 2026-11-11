# W2-11 (DAEO-k7hz): the acceptance part of the merge of `w2/integrate` into `w2/W2-11` (one designer commit before the merge)

You are a fresh **independent test designer**, launched under W2-11's ticket (`.tickets/DAEO-k7hz.md`), in W2-11's worktree. `EMG-common.md`, `NIGHT-common.md` and `LIFT-common.md` (beside `W2-11-A1-merge.md` in `.gov-runtime/scratch/orchestrator/briefs/`) hold where this file does not change them. Commit hashes in anything you write under `.gov-runtime/` are 12 digits.

## Why you
A merge of `w2/integrate` into `w2/W2-11` conflicts, among 19 other files that are not yours (kernel skills and templates, their generated copies; a product-spec session settles those), in **one acceptance file: `tests/acceptance/W1-35/w1_35_orchestration_support.py`**. Only a test designer writes `tests/acceptance/**` (MR-3). The merge itself will be made by another role. So you do the acceptance part **before** the merge, as one ordinary non-merge commit that moves W2-11's one edit in that file out of the lines `w2/integrate` also changed. After your commit git's own merge of the two branches has no conflict in that file and gives both sides' edits; the merge commit then changes nothing in `tests/acceptance/` that git's own merge does not hold (the DEC-253 and DEC-912 rule of `merge_offences`).

## The two sides (for your understanding; you do not need to read more)
- W2-11 replaced, in the row `"parallel tickets"`, the clause "a stated ceiling of tickets in flight" by the clause "no fixed number of tickets in flight" (DEC-847, DEC-866), and made other edits elsewhere in the file that merge cleanly.
- `w2/integrate` (W2-128 and D-4 cut B, DEC-1061, DEC-942) **removed** the stated-ceiling clause and left a `Rewrite-Reason` comment in its place; it also added the retired-brief helpers elsewhere in the file.
- The final file keeps integrate's removal of the old clause **and** W2-11's positive clause, which pins the KPI line "no fixed ceiling of tickets in flight (DEC-847)" that no other case of W2-11 pins.

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-11`, branch `w2/W2-11`. First calls: `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-k7hz`); `git -C /home/usain/gov-os-worktrees/W2-11 rev-parse --show-toplevel --abbrev-ref HEAD`; `git -C /home/usain/gov-os-worktrees/W2-11 status --short` must be empty; `git -C /home/usain/gov-os-worktrees/W2-11 rev-parse --short=12 HEAD` must be `c9f99b28b88b`. Anything else: stop and return PACKAGES.
- You write exactly one file: `tests/acceptance/W1-35/w1_35_orchestration_support.py`. Nothing else, in any tree.

## The change (two Edit calls on that file, absolute path `/home/usain/gov-os-worktrees/W2-11/tests/acceptance/W1-35/w1_35_orchestration_support.py`)
Edit 1. Replace these three lines (inside `ROWS["parallel tickets"]["clauses"]`):

```
            # DEC-847 replaced the stated ceiling (DEC-737, DEC-776, DEC-786) with no fixed number.
            ("no fixed number of tickets in flight",
             [r"no fixed|not (a )?fixed|no set", r"number|ceiling|cap|count", r"ticket|lead"]),
```

with these three lines (the base's clause, as it stood before W2-11):

```
            ("a stated ceiling of tickets in flight",
             [r"ceiling|at most|up to|no more than|maximum|limit", r"ticket",
              r"in flight|at a time|at once|parallel|concurrent|running"]),
```

Edit 2. Directly after the clause whose text is

```
            ("the resource gate before each start",
             [r"resource gate", r"before (each|every|any|a)\b|(each|every) start"]),
```

insert these four lines (same indentation):

```
            # W2-11 (DEC-847, DEC-866): DEC-847 replaced the stated ceiling (DEC-737, DEC-776, DEC-786) with no fixed
            # number; the skill says so, and this clause pins it.
            ("no fixed number of tickets in flight",
             [r"no fixed|not (a )?fixed|no set", r"number|ceiling|cap|count", r"ticket|lead"]),
```

Why this shape: the two clauses must not touch each other's lines, and the old clause must stand in the lines `w2/integrate` rewrote, so git's merge takes integrate's removal there and keeps your inserted clause two lines further down. (This commit is a **pre-merge form**: on its own, at this commit, W1-35's "parallel tickets" cases may be red against W2-11's skill, which says "no fixed number"; that is expected and is not yours to fix. The merge settles it.)

## Check before you commit (no test run; nothing here needs the suite)
1. Compare your file with the reference, which must be byte-identical: `cmp /home/usain/gov-os-worktrees/W2-11/tests/acceptance/W1-35/w1_35_orchestration_support.py /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-11/W1-35-orchestration-support.PRE-MERGE.py` (no output = identical). If it differs, fix your edit; never copy the reference over the file by a shell command.
2. `git -C /home/usain/gov-os-worktrees/W2-11 diff --stat` shows that one file, 7 lines inserted and 3 deleted or fewer.
3. Collect only: `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/acceptance/W1-35 --collect-only -q -p no:cacheprovider` and give the count (it must equal the count before your edit: `git stash` is not allowed, so count once before editing).
4. After the commit (below), the proof that git's own merge no longer conflicts in the file: `git -C /home/usain/gov-os-worktrees/W2-11 merge-tree --write-tree --name-only HEAD w2/integrate` (read-only; it exits 1 because 19 other files still conflict). Its listing of conflicted files must **not** contain `tests/acceptance/W1-35/w1_35_orchestration_support.py` and must show that file as `Auto-merging`. Quote the two relevant lines and the count of `CONFLICT` lines (expect 19, all under `template/`, `.claude/` and `.rulesync/`). If integrate moved since this brief and the file conflicts again, stop and return PACKAGES with the new hunk.

## Commit
```
git commit -m "W2-11 tests: W1-35's no-fixed-number clause moved clear of the lines w2/integrate rewrote (the pre-merge form)" --trailer "Task: DAEO-k7hz" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-847, DEC-866" --trailer "Rewrite-Reason: DEC-1061 with DEC-1040 (1), DEC-847: integrate removed the stated-ceiling clause (DEC-942); W2-11's positive clause stays, placed so git's merge is clean" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W1-35/w1_35_orchestration_support.py
```
Never amend, rebase, reset, push or merge. Do not run `git merge` or `git merge --abort`: the merge is not yours.

## Rules
- The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or any folder named `hidden`, `memory-verdict` or `memory-verdict-2`. No installs, no GPU, never the full suite. One simple command per Bash call; Edit and Write tools for file changes (no here-documents).
- `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<question>"` is optional here (at most twice); say whether you used it.
- Refused twice for the same call: stop and say so.
- Estimate: 10 minutes. Return the twelve fields as labelled lines (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), short; `evidence` holds the commit (12 digits) with its trailers, the `cmp` result, the collect count before and after, and the merge-tree lines of check 4.
