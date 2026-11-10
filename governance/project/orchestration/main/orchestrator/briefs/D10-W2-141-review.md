# D-10's red-fix list: the review of W2-141's staged hook, rebuilt on the live hook (W2-141, DAEO-xwro; row 78)

You are a fresh, read-only independent reviewer. **Narrow scope: one rebuild.** READY is computed by `verdict.py`
from your block.

## What happened
- W2-141's hook change is staged at `docs/changes/W2-141-hook/` for the lift's re-pin ACT; a launched worker
  cannot edit `.claude/` (DEC-315).
- `tests/unit/guard/test_w2_141_search.py::test_the_staged_pretooluse_adds_only_glob_to_g14s_tools` requires the
  staged `pretooluse.py` to equal the live hook with one line changed (`"Grep", "Bash"` → `"Grep", "Glob", "Bash"`).
- It was red because the live hook gained rules 2b (glob line), 2c and 2d after the copy was made. ACT-SETS-GLOBS-1
  is now live (`9cce7430d`; live sha256 `74f8dbea4761…`). DECIDED-NOT-DONE row 78 asked for the rebuild.

## What to review
- **The branch:** `w2/W2-141-d10` in `/home/usain/gov-os-worktrees/W2-141-d10`. Read
  `git -C /home/usain/gov-os-worktrees/W2-141-d10 show 9536ea954`.
- **The engineer's report:**
  - W2-141's only change to `pretooluse.py` against the hook it was built on (`15952bbfa`, `bd545af8…`) was that one
    line;
  - the new staged file is the live hook plus that line (sha256 `e7e1c4ce…`);
  - `role_reads.py` is unchanged (live `5407aade…` still matches);
  - the README's hash, note and rollback commit are updated.
- **The engineer's runs:**
  - `tests/unit/guard/test_w2_141_search.py` 204 passed;
  - `tests/unit/hooks` 100 passed and 2 failed, the 2 from a scratch HOME (`rm -f ~/.bashrc`), 8 of 8 with the real
    HOME;
  - `gov accept W2-141` 184 passed.

## Check
1. **Exactly one change:** diff the staged file against `.claude/hooks/pretooluse.py` at `9cce7430d`, and the old
   staged file against `15952bbfa:.claude/hooks/pretooluse.py`. Did W2-141 ever change anything else in
   `pretooluse.py` that the rebuild dropped?
2. **The combination is sound:** does W2-141's Glob line interact correctly with rule 2b's new glob handling
   (ACT-SETS-GLOBS-1) and with rules 2c and 2d? Would a Glob call now be judged twice, or not at all, anywhere?
   Could it refuse a call 2b allows, or allow one 2b refuses?
3. **The README:** hashes, rollback commit and steps correct for the ACT preparer.
4. **Trailers:** Task, Role, Implements and Co-Authored-By. Only `docs/changes/W2-141-hook/**` changed.

KPI id for the verdict block: `w2-141-staged-hook`.

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
