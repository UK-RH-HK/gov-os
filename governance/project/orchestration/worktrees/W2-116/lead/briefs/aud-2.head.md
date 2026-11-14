# Brief: independent auditor, W2-116 (DAEO-f58b) pass 2c: a narrow independent check of a test revision

You are a fresh independent auditor, read-only. You write nothing in any repository folder; work only under your
session's own `TMPDIR`. Your last message is the probe record, whole; the lead commits it under
`docs/probes/DAEO-f58b/`.

## What to check, and only this
The independent test designer's change of pass 2c on `w2/W2-116`, in /home/usain/gov-os-worktrees/W2-116, head
**037cf8a4fff0cada2b64fb8b7751b7c6d5dcd4ed** (the merge of w2/W2-116-tests). The change is
`git diff 9e9428942df546bb9d19f2b271b63b4fd0644bf4 6666cec2cbc9` (9e9428942 is the merge of w2/integrate pass 2c
started from), seven commits, one per file:
- 8893ad5b0 `tests/acceptance/W2-131/test_w2_131_unchanged.py`
- d92b61bf5 `tests/acceptance/W2-133/test_w2_133_unchanged.py`
- 67aa2d12b `tests/acceptance/W2-135/test_w2_135_unchanged.py`
- 3ad7ce713 `tests/unit/retrieval/test_w2_131_register_ids.py`
- 56930ce1a `tests/unit/retrieval/test_w2_133_gap_label.py`
- cd2324e06 `tests/unit/retrieval/test_w2_135_item_cap.py`
- 6666cec2c `tests/unit/status/test_status.py`

**Why the change exists (the order the lead was given, DEC-1156 (7)):** two decided behaviours of W2-116 turn 17
cases of other tickets red; the CTO routes them as revisions of decided behaviour, to a test designer, with
`Rewrite-Reason: DEC-1156 (7), R2-F3's token key / S2's status part (W2-116 pass 2c)`, one commit per file, no case
losing its point:
1. **R2-F3's `f` token key** (the CTO's Q3 (a) under DEC-1157 (12)): a continuation token now carries `f`, the store
   folder (half) it was made on, beside W2-138's `s` (the store's commit) (`src/gov/retrieval/retrieve.py` ~195-225).
   In the six token files, "the helper that drops the `s` key before comparing continuation tokens from two folders
   drops `f` as well. Nothing else changes."
2. **S2's `integration_store` status part** (in the ticket): `gov status` gains a part `integration_store` after
   `reranker` (`src/gov/status/command.py` 195-209); unconfigured, it is `{"read": false, ...}` and `not_read` names
   it. In `tests/unit/status/test_status.py`: "the exact `PARTS` tuple gains `integration_store` in the position the
   code gives it, and `not_read` stays asserted as the code's behaviour now is. The case still pins the whole tuple."

**Judge, for each of the seven files:**
- Does each case keep its point (what it guards for its own ticket: W2-131 register ids, W2-133 gap labels, W2-135
  item cap / cut lines, W2-138's `s` premise where it is read, the status case's "every not-read place named")?
  Would it still fail on the plausible wrong change it was written against? Is any assertion loosened (a subset, an
  `in`, a filter, a dropped key beyond `f`)?
- Did nothing but `f` and `integration_store` change (comments and docstrings naming them aside)?
- Is dropping `f` limited to comparisons of tokens from two folders (before/after stores), so that no case that should
  see `f` loses it?

**Probe, do not only read:** run the seven files, before (at 9e9428942, from a `git worktree add --detach` under your
`TMPDIR`, or `git show <rev>:<path>` into your `TMPDIR`) and after (at the head), and say which cases were red before
and green after. If you can, try a plausible wrong change against a revised case (e.g. in a copy under your `TMPDIR`,
drop a register id's fix or a not-read place) and see that the case still fails.

How to run pytest (every run):
```
env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-116/.gov-runtime/scratch/empty-home PYTHONPATH=<the checkout's>/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
`/tmp` is read-only in the sandbox: keep the sandbox's own `TMPDIR` (outside the repository). A resource gate's
refusal is a wait (DEC-1146); the `heavy-slot-waits.jsonl: Read-only file system` line is harmless. Never open the
evaluation sets' root or any hidden or memory-verdict folder. No `gov retrieve` or `gov context` in the sandbox: search
with Read and Grep, and once more in other words if the first does not answer (DEC-1065). Refused twice for the same
call by the guard, the sandbox or a hook: stop and say so; never work around it (DEC-1142 (9)).

Out of scope (rows if you see them, never failing findings): W2-116's own implementation and its acceptance suite
(reviewed in pass 2b, PASS); F-1 (a store named stale after an unchanged scheduled refresh, already a row); other
tickets' cases not in the seven files.

