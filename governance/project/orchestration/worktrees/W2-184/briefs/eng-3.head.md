# Brief: engineer, W2-184 (DAEO-6f0s), batch eng-3 (interface 1.4 amended; 77 reds)

You are a fresh engineer for DAEO-6f0s (W2-184). The branch head is d858e409b: batches eng-1 and eng-2 and the
acceptance cases merged; `gov accept W2-184` passes 352/352. The full verification run at d858e409b is red:
**77 failed of 7,494**, all from this branch. The list is in
/home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/briefs/verify-1-fails.txt (50 W1-46, 12 W1-32, 8 W1-28,
6 W1-50, 1 W2-60a). Their stderr: `gov launch: LAUNCH_REFUSED: governance/project/criticality.yaml: cannot be read, is
not YAML, or writes a key twice`. Those fixtures copy the kernel role files (the engineer's and test designer's carry a
`Launch by criticality` line) and have no `criticality.yaml`; the W2-60a one launches the auditor twice on a FULL
fixture ticket with no file.

The lead has **replaced interface 1.4** (in the whole interface below; also the intro paragraph, 1.3 and section 9):
with no `criticality.yaml`, a launch is as before W2-184 (the role's `Launch default` line for every role, no
promotion, no review count, no probe, no same-setting refusal; `criticality`, `promotion`, `review_round` null); the
model-after-`--` rule, the floor, max/`--reason` and the option forms still apply; `--trial` with no file is refused
naming the file. A present file is read on every worker launch; unreadable or malformed refuses. Build that.

## The change
`src/gov/launch/launcher.py` (`_rubric`), and `src/gov/launch/criticality.py` if needed. Unit cases in
`tests/unit/launch/test_w2_184_launch.py` (and `test_w2_184_criticality.py` if needed): rewrite any eng-1/eng-2 unit
case that encodes the earlier 1.4, and add cases for each point of the amended 1.4. One paragraph in
`docs/changes/W2-184-CIT-E.md`: 1.4 amended, why (the 77 reds), and replace its section 5 (the W2-60a red is gone).
The independent test designer revises the acceptance cases in parallel; you never write under `tests/acceptance/`.

## Where you work
- Your tree: /home/usain/gov-os-worktrees/W2-184, branch w2/W2-184. Write only `src/gov/launch/launcher.py`,
  `src/gov/launch/criticality.py`, `tests/unit/launch/test_w2_184_*.py`, `docs/changes/W2-184-CIT-E.md`, scratch under
  `.gov-runtime/scratch/eng/`.

## How to run tests (every pytest goes through heavy_slot.sh; run it in the background, never with `&`)
```
env HOME=/home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-184/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
Before your last commit, all green: `tests/acceptance/W1-28 tests/acceptance/W1-32 tests/acceptance/W1-46
tests/acceptance/W1-50 tests/acceptance/W2-60a tests/unit/launch`, and `tests/acceptance/W2-184` except the cases
the test designer is revising (name each W2-184 red you see with its test id and why: an earlier-1.4 assertion).
Also run `tests/acceptance/W2-153 tests/acceptance/W2-58 tests/acceptance/W2-56 tests/acceptance/W2-116
tests/acceptance/W2-50 tests/unit/resources/test_w2_20_unit_launch.py tests/unit/resources/test_w2_20_round3.py`.
Use the session's own `$TMPDIR`. No `gov retrieve`, no `gov context`: Read and Grep, and once more in other words.

## Commit (your paths only; trailers in ONE final paragraph)
```
git -C /home/usain/gov-os-worktrees/W2-184 commit -m "W2-184 (DAEO-6f0s): interface 1.4 amended: no criticality.yaml, the launch as before W2-184" --trailer "Task: DAEO-6f0s" --trailer "Role: engineer" --trailer "Implements: DEC-1167, DEC-1120" -- <your paths>
```
No merge, no push. Refused twice for the same action: stop and say so; never work around it.

## Return (your last message): the twelve fields, each a labelled line
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: /
proposed_decisions: / unresolved: / recommended_next_action:
In `evidence:` the commit and each run's summary line; in `tests:` which W2-184 acceptance cases are red on your head
and why.

---
# THE INTERFACE (word for word, 1.4 amended)

