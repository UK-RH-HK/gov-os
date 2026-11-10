Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-149-sgx/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-149 — the engineer's brief: F36 and F38 closed (DAEO-52ku)

You are a fresh engineer for **W2-149** (`.tickets/DAEO-52ku.md`). Read the changed lines **S23** and **S27** and the
last note. The interface, with the designer's update, is `.gov-runtime/scratch/lead/INTERFACE.md`. Build to it. A small
pass:
- **F36 (S27):** in the overlap auditor's `input/disputes.jsonl`, every side's `reason` is `""`. The x/y order and the
  other label fields do not change.
- **F38 (S23):** in the template's `kinds.yaml`, the `sgx1-overlap-auditor` entry's `tree_exclude` gains
  `.tickets/**`, `governance/project/orchestration/packages/**`, `governance/project/orchestration/tools/indep_launch.py`,
  `tests/acceptance/W2-149/**`, `tests/unit/orchestration/test_w2_149*` and `docs/changes/W2-149-evidence.md`. Edit the
  file with the Edit tool. Never name its folder in a Bash line, and stage with `git add -u`. No other entry changes.
- Update your unit tests, and add a short "F36, F38 (DEC-1112 (3))" section to the evidence.

## Where you work, and the rules
- `/home/usain/gov-os-worktrees/W2-149-sgx`, branch `w2/W2-149-sgx`, head `be77be65a` (the designer's F36/F38 cases). Your paths are the ticket's
  `allowed_paths`.
- **Never read `tests/acceptance/W2-149/`.** You see only `gov accept`'s results. Recursive grep carries
  `--exclude-dir=W2-149`; Grep and Glob carry `!tests/acceptance/W2-149/**`.
- Verify through the heavy slot `EMG-common.md` names, with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-149-sgx/src`,
  your sandbox's TMPDIR, a scratch HOME with `.local` linked in, and `PYTHONUSERBASE=/home/usain/.local`. Run
  `python3 -m gov.cli.main accept W2-149 --root /home/usain/gov-os-worktrees/W2-149-sgx`: every line green but the live
  and `bwrap` cases, which skip and which the lead runs outside. Then run `tests/unit/orchestration/test_w2_149*`.
- The hidden-half rule of `EMG-common.md`. No real `claude` session, GPU, network or installs. Never touch
  `tests/acceptance/**`, `.tickets/` or `.claude/`. DEC-1080. Waits by pid only. Do not merge `w2/integrate`.
- Commit with `--trailer "Task: DAEO-52ku" --trailer "Implements: DEC-1112, DEC-1113" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
- The twelve labelled fields of `EMG-common.md` first, each a single-line labelled field.
- The commits.
- `gov accept` per line, and the unit counts.
- The script's and `kinds.yaml`'s sha256s.

Refused twice for the same call: stop and say so.
