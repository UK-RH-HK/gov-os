# Brief: engineer, W2-184 (DAEO-6f0s), batch eng-2 (one amended point)

You are the engineer for DAEO-6f0s (W2-184). Batch eng-1 (21e78812e, 3b4523b04, 643a90b0e) is merged with the
acceptance cases (merge e4f59abc0) and `gov accept W2-184` passes 327/327. The lead has amended one settled point of
the interface, **3.2a** (in the whole interface below; read 3.2, 3.2a and section 8's `effort_source` line). Build it.

## The change
In `src/gov/launch/launcher.py` `_rubric`: a max given after `--` that equals the effort already resolved for this
launch (the table's max, or the probe's max on a FULL ticket's round 2+) needs no `--reason`; only a max after `--`
that differs from the resolved effort, or a trial's max, does. When the given max equals the probe's, `effort_source`
is `probe`; when it equals the table's, `after --`. Add unit cases in `tests/unit/launch/test_w2_184_launch.py`
(both accepted cases, and a max after `--` on a high table still refused without `--reason`). Add one line to
`docs/changes/W2-184-CIT-E.md` naming 3.2a.

**Not changed (the lead's decisions on your eng-1 return):** your option A for the W2-60a user-permissions case is
not taken: the interface stays fail-closed (a FULL ticket's second auditor launch with no `criticality.yaml` refuses;
the same setting twice refuses). That case
(`tests/acceptance/W2-60a/test_w2_60a_user_permissions.py`, `[independent-auditor]`) is another ticket's; the lead
names it to the CTO (DEC-1156 (7)). Do not edit it. Your other readings (eng-1 discoveries 2-8) stand.

## Where you work
- Your tree: /home/usain/gov-os-worktrees/W2-184, branch w2/W2-184. Write only `src/gov/launch/launcher.py`,
  `tests/unit/launch/test_w2_184_launch.py`, `docs/changes/W2-184-CIT-E.md`, scratch under `.gov-runtime/scratch/eng/`.
- Never write under `tests/acceptance/`.

## How to run tests (every pytest goes through heavy_slot.sh; run in the background, not with `&`)
```
env HOME=/home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-184/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/launch tests/acceptance/W2-184 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
Both must stay green (but for the reds you named at base in eng-1). Use the session's own `$TMPDIR`.
No `gov retrieve`, no `gov context`.

## Commit (your paths only; trailers in ONE final paragraph)
```
git -C /home/usain/gov-os-worktrees/W2-184 commit -m "W2-184 (DAEO-6f0s): interface 3.2a: a max after -- equal to the resolved effort needs no --reason" --trailer "Task: DAEO-6f0s" --trailer "Role: engineer" --trailer "Implements: DEC-1120, DEC-1010" -- src/gov/launch/launcher.py tests/unit/launch/test_w2_184_launch.py docs/changes/W2-184-CIT-E.md
```
No merge, no push. Refused twice for the same action: stop and say so; never work around it.

## Return (your last message): the twelve fields, each a labelled line
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: /
proposed_decisions: / unresolved: / recommended_next_action:

---
# THE INTERFACE (word for word, with 3.2a)

