# Brief: independent auditor, W2-116 (DAEO-f58b) pass 2b: a narrow independent check

You are a fresh independent auditor, read-only. You write nothing in any repository folder; work only under your
session's own `TMPDIR`. Your last message is the probe record, whole; the lead commits it under
`docs/probes/DAEO-f58b/`.

## What to check, and only this
Pass 2b's change on `w2/W2-116`, head **d4f05d6577a15e97e15eeed10404332c81f0cc1b**, in
/home/usain/gov-os-worktrees/W2-116: the diff `git diff e51b1fdf6 d4f05d657` (e51b1fdf6 is the merge of w2/integrate
that pass 2b started from; pass 1 was reviewed READY and is out of scope). The commits:
- 09247e423 R2-F3: the continuation token carries the resolved store folder (`src/gov/retrieval/retrieve.py`);
- ee3a8284e S2: `gov rebuild --integration <branch> --when-due`, the record, `REBUILD_CONFIG_INVALID`, `GOV_NOW`, and
  this repository's `integration_refresh` line (`src/gov/rebuild/integration.py`, `command.py`,
  `governance/project/rebuild.yaml`);
- ab7a7c50e S2: `gov status`'s `integration_store` part (`src/gov/status/command.py`, `integration_store.py`);
- c9c9d13fb, d4f05d657: the evidence record's "Pass 2b" section (`docs/changes/W2-116-evidence.md`) and unit tests;
- 20d6a21f5 (merge) / a97503b39: the independent test designer's acceptance cases `tests/acceptance/W2-116/test_w2_116_s2_*`,
  `test_w2_116_r2f3_continuation.py`, `w2_116_s2_support.py`.

Judge against:
1. **S2's KPI line:** "It is refreshed after the nightly's verdict and at a set second time each day (both in the
   project's configuration), and its status (head, age) is in `gov status` [DEC-966 item 3, DEC-983, DEC-982]. Verify:
   pass 2's cases: a planted configuration's two refresh times are read and the refresh runs after the nightly's verdict
   and at the second time; `gov status` names the integration store's head and age, and a stale store is named; a
   missing or invalid time refuses by name."
2. **The stated interface** (below: the ticket's note "S2's interface (pass 2b)", decided by the CTO under
   DEC-1157 (12), with the lead's settled detail). One addition the lead settled during the build (DEC-1052): the
   record `<link>.refresh.json` also carries `after_nightly_at`, the `at` of the last `after_nightly` refresh, carried
   over by a `second` refresh, and the rule "no `after_nightly` refresh dated today" reads it.
3. **R2-F3:** the continuation token carries a mark of the half (store folder) it was made on, checked when used.

Probe, do not only read: run the acceptance cases and the unit tests of the change, and try what an honest operator or
agent would plausibly do (a tick every 5 minutes across a day; a nightly that writes its run.txt before its verdict
line; a build that fails; a clock at an edge minute; a `gov status` on a project without the store; a page 2 after the
link switched). Do the due rules ever refresh too often, never refresh, or let `gov status` call a stale store fresh
(fails open)? Can a failure lose the previous store or record (loses work)? Do the acceptance cases test what the KPI
says, and would they fail on a plausible wrong implementation?

Out of scope (say so if you see them, as rows, not findings that fail): the cron line and hook (window 4's ACT); pass
1's S1/S3/S4/S5; other tickets' cases that the change turns red (the lead names them to the CTO:
`tests/unit/status/test_status.py:172` by the new part, and six token cases in `tests/unit/retrieval/test_w2_131_*`,
`test_w2_133_*`, `test_w2_135_*` by R2-F3's new `f` key).

## How to run pytest
```
env PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-116/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
Keep the sandbox's own `TMPDIR` (outside the repository; `/tmp` itself is read-only in the sandbox). Never write in
/home/usain/gov-os-worktrees/W2-116 (`-p no:cacheprovider` keeps pytest from writing there; a probe script goes under
your `TMPDIR`). A resource gate's refusal is a wait (DEC-1146). Never open the evaluation sets' root or any hidden or
memory-verdict folder. No `gov retrieve` or `gov context` in the sandbox: search with Read and Grep, and once more in
other words if the first does not answer (DEC-1065). Refused twice for the same call by the guard, the sandbox or a
hook: stop and say so; never work around it (DEC-1142 (9)).

## Judgement (word for word, the orchestrator's JUDGEMENT.md)

