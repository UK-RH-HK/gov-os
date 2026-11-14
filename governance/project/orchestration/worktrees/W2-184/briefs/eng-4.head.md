# Brief: engineer, W2-184 (DAEO-6f0s), batch eng-4 (fix round after review 1)

You are a fresh engineer for DAEO-6f0s (W2-184), launched on Opus because the ticket is promoted (its round-1 review
record, `docs/probes/DAEO-6f0s/PR-DAEO-6f0s-round-1.md`, holds a fail-open finding; DEC-1120 (3)). The head is
bec7757d4; the full verification run at 8830dece0 was green (7,572 tests) and `gov accept W2-184` passes 413/413.
The FULL review's round 1 failed on F1; F2 and F8 ride along (DEC-802). Read the record's F1, F2 and F8, then build:

1. **F1 (blocking):** `governance/project/criticality.yaml`'s C3 rule gains `fixtures/evaluation/*/hidden/*` (hidden
   sets, the path map's hidden halves). A ticket naming `fixtures/evaluation/<set>/hidden/**` resolves to C3, also
   with a `docs/probes/<id>/**  # ...` path beside it.
2. **F8:** the C3 rule gains `.claude/settings.local.json`, `governance/project/secrets.yaml` and
   `governance/project/indep-walls/*` (beside `.claude/settings.json` and `governance/project/held-out.yaml`).
3. **F2:** in `src/gov/launch/launcher.py` `_rubric`: a launch whose `review_round` is 3 or more is refused, naming
   the round and DEC-1010, unless `--owner-named` is given, whatever its setting (interface 6.3 as amended). The
   same-setting rule stays.
Unit cases in `tests/unit/launch/test_w2_184_criticality.py` (the project file: a hidden-set path and each
permission path at C3; the comment-tail case) and `tests/unit/launch/test_w2_184_launch.py` (round 3 after a round 2
at xhigh refused; accepted with `owner_named`). One paragraph in `docs/changes/W2-184-CIT-E.md`: review round 1, F1,
F2, F8, and the rows left for the CTO (F3-F7, F9, F10). The independent test designer writes the acceptance cases in
parallel; never write under `tests/acceptance/`, and never open anything under `fixtures/evaluation/` (path strings
only).

## Where you work
- Your tree: /home/usain/gov-os-worktrees/W2-184, branch w2/W2-184. Write only
  `governance/project/criticality.yaml`, `src/gov/launch/launcher.py`, `tests/unit/launch/test_w2_184_*.py`,
  `docs/changes/W2-184-CIT-E.md`, scratch under `.gov-runtime/scratch/eng/`.

## How to run tests (every pytest through heavy_slot.sh; in the background, never with `&`)
```
env HOME=/home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-184/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
Before your last commit, green: `tests/unit/launch tests/acceptance/W2-184 tests/acceptance/W2-60a
tests/acceptance/W1-46`. Use the session's own `$TMPDIR`. No `gov retrieve`, no `gov context`.

## Commit (your paths only; trailers in ONE final paragraph)
```
git -C /home/usain/gov-os-worktrees/W2-184 commit -m "W2-184 (DAEO-6f0s): review round 1: hidden sets and permissions C3 (F1, F8); no third review round without the owner (F2)" --trailer "Task: DAEO-6f0s" --trailer "Role: engineer" --trailer "Implements: DEC-1120, DEC-1010" -- <your paths>
```
No merge, no push. Refused twice for the same action: stop and say so; never work around it.

## Return (your last message): the twelve fields, each a labelled line
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: /
proposed_decisions: / unresolved: / recommended_next_action:

---
# THE INTERFACE (word for word, with the round-1 amendments)

