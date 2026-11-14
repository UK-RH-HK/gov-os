# Brief: engineer, W2-184 (DAEO-6f0s), batch eng-7 (R1-R3, the narrow check's F1-F3)

You are a fresh engineer for DAEO-6f0s (W2-184), launched on Opus because the ticket is promoted (DEC-1120 (3)). The
ticket was reopened on 2026-11-14 under DEC-1180 (4) (a defect spotted is fixed in the same flow) for KPI lines R1-R3.
The head is bf7b93bcf, the merge of the test designer's new cases (td-7, tests 19324ca4b). New cases are red; make them
green within the ticket's paths. The behaviour they test is interface **section 10** (at the end of this brief); the
rest of the interface is unchanged and its cases are green.

## The failing output (all you are given beyond the interface)
- /home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/log/red-7-short.txt (the failing case names and their
  assertion lines);
- /home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/log/red-7.txt (the full `--tb=short -rf` output).

Context: /home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/briefs/ctx-eng-5.md (JSON: the ticket and its
sources, from `gov context`; today's `gov context` is BLOCKED because DEC-1180 is not yet in the store).

Never write under `tests/acceptance/` or into `tests/unit/launch/test_w2_184_r_fixes.py` (both the independent test
designer's), and never open anything under `fixtures/evaluation/` or a `hidden` folder.

## What to deliver
- The change in `src/gov/launch/command.py` (R1), `src/gov/launch/launcher.py` (R1's second fence, R3; and the reader
  if R2 needs it) and `src/gov/launch/record.py` (R2). Nothing else changes in `src/`.
- One paragraph in `docs/changes/W2-184-CIT-E.md`: R1-R3 (DEC-1180 (4), the narrow check's F1-F3), what changed.
- You may add unit cases in a new file `tests/unit/launch/test_w2_184_r_engineer.py` if useful.

## Where you work
- Your tree: /home/usain/gov-os-worktrees/W2-184, branch w2/W2-184. Write only `src/gov/launch/command.py`,
  `src/gov/launch/launcher.py`, `src/gov/launch/record.py`, `docs/changes/W2-184-CIT-E.md`,
  `tests/unit/launch/test_w2_184_r_engineer.py`, and files under the session's own `$TMPDIR` (no new folder under
  `.gov-runtime/scratch/`).

## How to run tests (every pytest through heavy_slot.sh; long runs in the background, never with `&`)
```
env HOME=/home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-184/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
Before your last commit, green: `tests/unit/launch tests/unit/cli tests/acceptance/W2-184 tests/acceptance/W2-60a
tests/acceptance/W1-46 tests/acceptance/W2-20` (leave out any of these folders that does not exist). No `gov
retrieve`, no `gov context`: Read and Grep, and once more in other words.

## Commit (your paths only; trailers in ONE final paragraph, no blank line inside it)
```
git -C /home/usain/gov-os-worktrees/W2-184 commit -m "W2-184 (DAEO-6f0s): R1-R3 (DEC-1180 (4)): a lead refuses --reason, --trial and --owner-named; the launch record written atomically; every root's copy of a probe record read" --trailer "Task: DAEO-6f0s" --trailer "Role: engineer" --trailer "Implements: DEC-1180, DEC-1120, DEC-1010" -- <your paths>
```
No merge, no push. Refused twice for the same action: stop and say so; never work around it.

## Return (your last message): the twelve fields, each a labelled line
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: /
proposed_decisions: / unresolved: / recommended_next_action:

---
# THE INTERFACE (word for word, with the round-1 and round-2 amendments and section 10, R1-R3)

