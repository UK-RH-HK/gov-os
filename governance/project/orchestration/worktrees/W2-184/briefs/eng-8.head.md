# Brief: engineer, W2-184 (DAEO-6f0s), batch eng-8 (two builder unit cases revised to R3, interface 10.3)

You are a fresh engineer for DAEO-6f0s (W2-184), launched on Opus because the ticket is promoted (DEC-1120 (3)). The
head is f2f76a154. The ticket was reopened on 2026-11-14 under DEC-1180 (4) for KPI lines R1-R3; R3 (interface
**10.3**, at the end of this brief) revises the settled point P-td5-2 ("a path under two roots: only the first copy
counts"). Two earlier engineer-written unit cases still assert P-td5-2 and are red; everything else is green.

## The failing output (all you are given beyond the interface)
- /home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/log/red-8-short.txt (the two cases and their tracebacks);
- /home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/log/red-8.txt (the full `--tb=short -rf` output of
  `tests/unit/launch`; ignore `test_runs.py::test_a_project_under_the_root_gets_no_folder_made_or_added` there: it
  failed only because that run's TMPDIR lay under `~/gov-os-runs`, and passes with another TMPDIR).

## What to deliver
- In `tests/unit/launch/test_w2_184_launch.py` only: revise
  `test_f1_a_path_under_the_launch_root_and_another_is_read_from_the_launch_root` and
  `test_f1_a_path_under_two_other_roots_is_read_from_the_first_in_sorted_order` to 10.3 (every root's copy is read; a
  copy that is not of the form refuses, naming the file; a fail-open finding in any copy promotes; one path is one
  review), and rename each to say what it now checks. Change nothing in `src/` and no other case. If a case cannot be
  made to state 10.3 without changing `src/`, stop and say so (do not change `src/`).

Never write under `tests/acceptance/` or into `tests/unit/launch/test_w2_184_r_fixes.py` (the independent test
designer's), and never open anything under `fixtures/evaluation/` or a `hidden` folder.

## Where you work
- Your tree: /home/usain/gov-os-worktrees/W2-184, branch w2/W2-184. Write only
  `tests/unit/launch/test_w2_184_launch.py` and files under the session's own `$TMPDIR` (no new folder under
  `.gov-runtime/scratch/`).

## How to run tests (every pytest through heavy_slot.sh; long runs in the background, never with `&`)
```
env HOME=/home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-184/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
Before your commit, green: `tests/unit/launch`. No `gov retrieve`, no `gov context`: Read and Grep, and once more in
other words.

## Commit (your path only; trailers in ONE final paragraph, no blank line inside it)
```
git -C /home/usain/gov-os-worktrees/W2-184 commit -m "W2-184 (DAEO-6f0s): two builder unit cases of P-td5-2 revised to R3 (interface 10.3, DEC-1180 (4))" --trailer "Task: DAEO-6f0s" --trailer "Role: engineer" --trailer "Implements: DEC-1180, DEC-1120, DEC-1010" -- tests/unit/launch/test_w2_184_launch.py
```
No merge, no push. Refused twice for the same action: stop and say so; never work around it.

## Return (your last message): the twelve fields, each a labelled line
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: /
proposed_decisions: / unresolved: / recommended_next_action:

---
# THE INTERFACE (word for word, with the round-1 and round-2 amendments and section 10, R1-R3)

