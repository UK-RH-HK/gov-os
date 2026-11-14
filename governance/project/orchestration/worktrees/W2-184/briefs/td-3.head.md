# Brief: independent test designer, W2-184 (DAEO-6f0s), batch td-3 (interface 1.4 amended)

You are the independent test designer for DAEO-6f0s (W2-184). Your batches td-1 (875039257) and td-2 (54afbf9a8) are
merged. The lead has **replaced interface 1.4** (below, in the whole interface; also read the intro paragraph, 1.3
and section 9, which changed with it): with no `governance/project/criticality.yaml`, a launch is as before W2-184
(the role's `Launch default` line for every role, no promotion, no review count, no probe, no same-setting refusal;
`criticality`, `promotion`, `review_round` null), but the model-after-`--` rule, the floor, max/`--reason` and the
option forms still apply, and `--trial` with no file is refused naming the file. A present file is read on every
worker launch, and an unreadable or malformed one refuses. The reason: the full verification run found 76 cases of
W1-28's, W1-32's, W1-46's and W1-50's suites refused (their fixtures copy the kernel role files, whose engineer and
test designer files carry a `Launch by criticality` line, and have no `criticality.yaml`), against DEC-1167 (2).
Do not read the engineer's work on this ticket.

## Where you write
- Your tree: /home/usain/gov-os-worktrees/W2-184-tests, branch w2/W2-184-tests (at 54afbf9a8). Write only
  `tests/acceptance/W2-184/`.

## What to write
1. Revise every td-1/td-2 case that asserts the earlier 1.4 (a missing `criticality.yaml` refusing a launch whose
   role file has a `Launch by criticality` line, or a FULL ticket's probe or a promotion with no file refusing, or
   anything else the amendment reverses) to the amended 1.4, and add the trailer
   `Rewrite-Reason: W2-184 interface 1.4 amended (lead, 2026-11-14)` in the commit's one final trailer paragraph.
   List each revised case in your return.
2. New cases, no `criticality.yaml` in the fixture: (a) a role with a well-formed `Launch by criticality` line
   launches on its `Launch default` line, `model_source: role default`, `criticality: null`; (b) the same with a
   malformed `Launch by criticality` line still refuses; (c) a FULL ticket's two `independent-auditor` launches both
   start on the default line, `review_round` null, no same-setting refusal; (d) two failed probe records (or a
   fail-open one) planted: no promotion, `promotion: null`; (e) `--trial` refused naming
   `governance/project/criticality.yaml`; (f) a model after `--` other than the default refused naming both; an
   effort below the floor of a high default refused; a max after `--` on a high default with no `--reason` refused.
3. A present but malformed `criticality.yaml` refuses even a role with only a `Launch default` line (keep or add).
Name, per new or revised case, what it would fail on in a launcher that applies the earlier 1.4.

## How to run tests (every pytest)
```
env HOME=/home/usain/gov-os-worktrees/W2-184-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-184-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-184 -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
(If heavy_slot.sh cannot take a slot inside the sandbox, run pytest directly and say so.) Use the session's own
`$TMPDIR`. No `gov retrieve`, no `gov context`: search with Read and Grep, and once more in other words.

## Commit (your paths only; trailers in ONE final paragraph)
```
git -C /home/usain/gov-os-worktrees/W2-184-tests commit -m "W2-184 (DAEO-6f0s): acceptance cases for interface 1.4 as amended (no criticality.yaml: the launch as before W2-184)" --trailer "Task: DAEO-6f0s" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1167, DEC-1120" --trailer "Rewrite-Reason: W2-184 interface 1.4 amended (lead, 2026-11-14)" -- tests/acceptance/W2-184
```
No merge, no push. Refused twice for the same action: stop and say so; never work around it.

## Return (your last message): the twelve fields, each a labelled line
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: /
proposed_decisions: / unresolved: / recommended_next_action:

---
# THE INTERFACE (word for word, 1.4 amended)

