# Brief: engineer, W2-184 (DAEO-6f0s), batch eng-5 (fix after review round 2, F1)

You are a fresh engineer for DAEO-6f0s (W2-184), launched on Opus because the ticket is promoted (DEC-1120 (3)). The
head is 7d275b97f. New acceptance cases are red; make them green within the ticket's paths. The behaviour they test
is interface **5.1a** (below, with its two settled points); the rest of the interface is unchanged and its cases are
green.

## The failing output (all you are given beyond the interface)
`gov accept W2-184 --root /home/usain/gov-os-worktrees/W2-184` exits 3: 453 passed, 19 failed (success-5: 15,
failure-1: 4). The 19 are all in `tests/acceptance/W2-184/test_w2_184_f1_tests_worktree.py`:
- /home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/log/red-5-short.txt (the case names and the two
  assertion lines);
- /home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/log/red-5.txt (the full `--tb=line -rf` output).

Context: /home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/briefs/ctx-eng-5.md (JSON: the ticket and its
sources, from `gov context`).

Never write under `tests/acceptance/` (the independent test designer's), and never open anything under
`fixtures/evaluation/` or a `hidden` folder.

## What to deliver
- The change in `src/gov/launch/launcher.py` (and only the ticket's other paths if needed).
- Unit cases in `tests/unit/launch/test_w2_184_launch.py` (or a new `tests/unit/launch/test_w2_184_*.py`).
- One paragraph in `docs/changes/W2-184-CIT-E.md`: review round 2's F1, the owner's P-W2-184-1 (a) (DEC-1010), what
  changed.

## Where you work
- Your tree: /home/usain/gov-os-worktrees/W2-184, branch w2/W2-184. Write only `src/gov/launch/launcher.py`,
  `src/gov/launch/role.py`, `src/gov/launch/record.py`, `src/gov/launch/criticality.py`, `src/gov/launch/command.py`,
  `governance/project/criticality.yaml`, `tests/unit/launch/test_w2_184_*.py`, `docs/changes/W2-184-CIT-E.md`, and
  scratch under `.gov-runtime/scratch/eng/`.

## How to run tests (every pytest through heavy_slot.sh; in the background, never with `&`)
```
env HOME=/home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-184/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
Before your last commit, green: `tests/unit/launch tests/acceptance/W2-184 tests/acceptance/W2-60a
tests/acceptance/W1-46`. Use the session's own `$TMPDIR`. No `gov retrieve`, no `gov context`: Read and Grep, and once
more in other words.

## Commit (your paths only; trailers in ONE final paragraph, no blank line inside it)
```
git -C /home/usain/gov-os-worktrees/W2-184 commit -m "W2-184 (DAEO-6f0s): review round 2's F1: the probe records are also read under each root the ticket's launch records name (P-W2-184-1 (a))" --trailer "Task: DAEO-6f0s" --trailer "Role: engineer" --trailer "Implements: DEC-1120, DEC-1010" -- <your paths>
```
No merge, no push. Refused twice for the same action: stop and say so; never work around it.

## Return (your last message): the twelve fields, each a labelled line
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: /
proposed_decisions: / unresolved: / recommended_next_action:

---
# THE INTERFACE (word for word, with the round-1 and round-2 amendments)

