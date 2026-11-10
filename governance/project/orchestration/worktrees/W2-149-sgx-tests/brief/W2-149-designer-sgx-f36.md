Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-149-sgx-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-149 — the independent test designer's brief: F36 and F38 closed (DAEO-52ku)

You are a fresh independent test designer for **W2-149** (`.tickets/DAEO-52ku.md`). Read the changed lines **S23** and
**S27** and the ticket's last note. The CTO decided (DEC-1112 (3); DEC-1113 (2): the overlap auditor decides "from the
decisions alone", blind) to close two rows of the last review:
- **F36:** in the auditor's `input/disputes.jsonl`, **every** side's `reason` is `""`, whatever the labellers wrote.
  `x`/`y` stay in the seeded order, and the other label fields stay. Today only a dispute with an empty side is blanked.
- **F38:** the overlap auditor entry's `tree_exclude` also leaves out `.tickets/**`,
  `governance/project/orchestration/packages/**`, `governance/project/orchestration/tools/indep_launch.py`,
  `tests/acceptance/W2-149/**`, `tests/unit/orchestration/test_w2_149*` and `docs/changes/W2-149-evidence.md`. The other
  four set-up A entries keep their exclusions, and a brief with no entry keeps all of these.

Your earlier cases are in `tests/acceptance/W2-149/`: the README's set-up A interface, `w2_149_setup_a.py`,
`test_w2_149_setup_a_audit.py`, `test_w2_149_setup_a_fixes.py` and S23's tree case.

## What the cases must show
Each case must be red today for the reason your README states.
- **S27:** disputes where both sides carry reasons are staged with both reasons `""`. The case where one side is empty
  stays green.
- **S23:**
  - the overlap auditor's dry-built tree, from a planted commit holding a file under each new glob, holds none of them;
  - a labeller's or writer's tree under a set-up A entry still holds them;
  - a memory writer's tree holds them all;
  - the template static check reads the real `kinds.yaml` entry.
- **Revise** only the cases that assert the old forms (two reasons kept; the auditor's tree holding those files), with
  `--trailer "Rewrite-Reason: DEC-1112 (3) (F36, F38 closed: S23, S27 changed)"`. Update the README's interface and map.

## Where you work, and the rules
- `/home/usain/gov-os-worktrees/W2-149-sgx-tests`, branch `w2/W2-149-sgx-tests`, head `9699bbbc9`. Write only
  `tests/acceptance/W2-149/`. Your record is your final message, in full.
- Never read the implementation: not `indep_launch.py`, not `tests/unit/orchestration/test_w2_149*`, not the evidence,
  never the `W2-149-sgx` worktree. You may read the template with the Read tool, never naming its folder in a Bash
  line.
- No GPU, model, network or installs; no real `claude` session; planted roots only; the hidden-half rule of
  `EMG-common.md`. A nested `bwrap` cannot start in your sandbox: mark the cases that need it `bwrap`.
- Run through the heavy slot `EMG-common.md` names, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-149-sgx-tests/src`, your sandbox's TMPDIR, a scratch HOME with `.local`
  linked in, and `PYTHONUSERBASE=/home/usain/.local`. Then run
  `python3 -m gov.cli.main accept W2-149 --root /home/usain/gov-os-worktrees/W2-149-sgx-tests`.
- DEC-1080: one simple command per Bash call. Waits by pid only.
- Commit with `--trailer "Task: DAEO-52ku" --trailer "Implements: DEC-1112, DEC-1113" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
- The twelve labelled fields of `EMG-common.md` first, each a single-line labelled field.
- The cases (node ids, red today and why, which carry `bwrap`).
- The commits.
- `gov accept`'s counts.
- `TESTS-READY`.

Refused twice for the same call: stop and say so.
