Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-92-d10b-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: the review of three whole-tree copies limited to `src/` (W2-92, DAEO-n0wb)

You are a fresh, read-only independent reviewer. **Narrow scope: one revision.** READY is computed by `verdict.py`
from your block.

## What happened
- W1-28's rule (DEC-385): a fixture that copies the repository's whole tree must be one its check can run
  (module-level, `root=`, the held-out file left out by its path), or limited to named paths.
- Three helpers broke it: `W2-92/w2_92_support.py::base_src`, `W2-92/test_w2_92_speed.py::base` (`5214e0f01`) and
  `W2-13/w2_13_lexical_policy_support.py::pre_s6_src` (`b6eb2267f`). Each ran `git -C REPO_ROOT archive <commit> src`.
- Red, alone and serial, at integrate: W1-28 1, W1-50 13.
- A test designer revised them under W2-92's ticket.

## What to review
- `git -C /home/usain/gov-os-worktrees/W2-92-d10b-tests diff e74b551bc..bbea1bb16 -- tests/`. A later commit only
  merges `w2/integrate` in.
  - The three now run `git -C REPO_ROOT/src archive --format=tar --prefix=src/ <commit>` (the "named paths" option);
    `base` reuses `base_src`.
  - One README line each.
- **The designer's runs (sandbox):**
  - W1-28 copies + W1-50 freeze settings: 14 failed, 30 passed → 32 passed. W1-50's 12 rows over these functions are
    no longer generated, since they are no longer whole-tree copies.
  - W2-13: 96 passed, unchanged.
  - W2-92: 26 failed, the same before and after (the code-graph tool cannot start in the sandbox).
- **The CTO's helper's run outside the sandbox, with the tool,** is in its record.

## Check
1. **Same content:** does `git -C REPO_ROOT/src archive --prefix=src/ <commit>` produce exactly the old
   `<commit>:src` tree in every case (untracked files, a different working directory, a commit where `src/` differs
   from today's)? Do the callers' premises still hold?
2. **W1-28's and W1-50's checks:** are these now truly named-path copies by W1-28's own reading, or did the change
   only slip past its reader (the designer notes the reader does not read `git archive`'s path argument)? Could
   the held-out file reach either copy?
3. **No expectation lowered** in W2-92, W2-13, W1-28 or W1-50. W1-50's 12 rows disappearing: is that right, or a
   loss of coverage?
4. **Trailers:** Task, Role, Implements, Rewrite-Reason and Co-Authored-By. Only `tests/acceptance/W2-92/**` and
   `W2-13/**` changed.

KPI id for the verdict block: `whole-tree-named-paths`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this revision.

## Write and return
- **You write nothing** in any tree.
- You may run the tests read-only (`-p no:cacheprovider -o tmp_path_retention_policy=failed`) through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=<the branch's worktree>/src`, a TMPDIR folder of your own under the sandbox's TMPDIR, and
  `PYTHONUSERBASE=/home/usain/.local` if you set an empty HOME (so pytest is found).
- No GPU, no installs, never the full suite. Single simple Bash commands (DEC-1080).
- The hidden-half rule holds: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **Your record is your session's final message**, in full:
  - the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
  - your answers to the checks;
  - every finding, with its two lines and its scope;
  - at the end, the fenced `verdict` block:
    `{"kpis": [{"kpi": "<id>", "verdict": "pass|fail", "findings": [...]}]}`, one entry per KPI id named above,
    each finding `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 15 minutes.
