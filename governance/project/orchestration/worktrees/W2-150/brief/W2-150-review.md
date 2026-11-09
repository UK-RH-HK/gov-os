Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-150/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-150 — the independent review: memory's import closure free of the gates (DAEO-ijf5)

You are a fresh, read-only independent reviewer of **W2-150** (`.tickets/DAEO-ijf5.md`). Read it whole, with S1-S5,
the failure lines and both notes. It is D-6 part 2's code item (P1-PLAN §A P1-6 item 1; DEC-1039 (2), DEC-1040 (1),
DEC-1109 (2)). READY is computed by `verdict.py` from your block.

## What to review
- **The branch:** `w2/W2-150` in `/home/usain/gov-os-worktrees/W2-150`, head `b85efb879`, made from `w2/integrate` at
  `40a146e66`. Read `git diff 40a146e66..b85efb879`.
  - The designer's cases: `tests/acceptance/W2-150/` (`321d2bf4`, merged at `82faa2c89`).
  - The engineer's change: `28c586930`, `14135b50c` and `b85efb879`, with the evidence record
    `docs/changes/W2-150-evidence.md`.
- **What the engineer did (its return):**
  - Moved names into `gov.util` (`parts`, `patterns`, `register`, `role_paths`, `runs_root`, `tickets`) and into
    `gov.store.loader` (the fingerprint).
  - **Aliased** `gov.guard.role_paths` and `gov.decisions.register` to their new homes through `sys.modules`. The aim
    is that existing tests patching module attributes still reach the moved code.
  - Left **copies** of `guard.protected._Glob`, `guard.heldout.load_yaml_unique` and `close.repo.git`. Their home
    files are outside the paths.
  - The walk went from 101 modules and 25,596 lines to 53 modules and 11,095 lines, with 0 gate modules.
- **The runs:**
  - The engineer's, in the sandbox: `gov accept W2-150` 26/0; `tests/unit/util` 73; gate suites with opt-ins
    2,046 passed and 1 failed (`test_w2_141_search.py::test_the_staged_pretooluse_adds_only_glob_to_g14s_tools`,
    red at the base too).
  - The CTO's, outside the sandbox at `b85efb879`: `tests/unit/hooks`, acceptance W2-141, W2-129, W2-150 and W2-55
    gave 505 passed and 3 failed. The 3 are `test_w2_55_backfill.py` cases, red at the base too.
  - The CTO's import timing: `import gov.guard.decide` 15.0 ms at the base, 14.5 ms on the branch (median of five).
    It loads only `gov.guard.{decide,runs}` and `gov.util.{gitenv,patterns,runs_root,tickets}`.

## Check
1. **Behaviour unchanged, especially the guard's:**
   - Read the moved code against the originals (`git show 40a146e66:<path>`). Is any decision of the guard, the
     role filter, the held-out and evaluation-set reading, the close fingerprint or the selection different?
     Compare byte for byte where it was moved.
   - The role filter (`role_paths`) and the evaluation-set reading guard the hidden half and role separation. A
     changed rule there fails open.
2. **The `sys.modules` aliasing:**
   - Is the same object really under both names in every import order (old first, new first, `from … import`,
     `importlib.reload`)?
   - Can a test or the hook end up with two copies whose state diverges, for example a patched `WORKTREES` seen by one
     name only?
   - Does the live hook (`.claude/hooks/`, the pinned copy at the next re-pin) import either module?
3. **The copies:**
   - Are they identical to their originals today?
   - What is the drift risk until the follow-up (the originals import from the new homes) lands?
   - Is that follow-up ordinary work, a row, not a blocker?
4. **S1/S2 honestly met:** no `importlib` or `__import__` in place of an import statement, and no import hidden from
   the walk. `gov.decisions/__init__` is unchanged.
5. **S3 and S5:** every old name importable with the same behaviour; unit cases moved or added for each helper.
6. **Cycles and import order:** `close/select.py` now imports `gov.store.loader` at module level. Check that no
   circular import appears in any entry point, such as `gov.cli.main` and the hook.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding is `scope: in` only if it
concerns W2-150's KPI lines.

## Write and return
- **You write nothing** in any tree. Scratch files go only in your TMPDIR.
- You may run tests read-only (`-p no:cacheprovider`) through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-150/src` and an empty scratch HOME (`PYTHONUSERBASE=/home/usain/.local`).
- No GPU. Single simple Bash commands (DEC-1080).
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them. Read the code that guards them, never their data.
- **Search again once (DEC-1092 (1)).**
- **Your record is your session's final message**, in full. It holds:
  - the twelve labelled fields of `EMG-common.md` (the sandbox and `ps` checks first);
  - your answers to checks 1-6;
  - every finding, with its two lines and its scope;
  - at the end, the fenced `verdict` block over S1-S5 and F1-F3:
    `{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [...]}, ..., {"kpi": "F3", ...}]}`,
    each finding `{"id", "scope", "ordinary_work", "consequence"}`.
