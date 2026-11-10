# D-10's red-fix list: the review of W2-92's planted path map (W2-92, DAEO-n0wb)

You are a fresh, read-only independent reviewer. **Narrow scope: one revision.** READY is computed by `verdict.py`
from your block.

## What happened
- `tests/acceptance/W2-92/test_w2_92_unchanged.py::test_u1_…[unknown symbol]` asks "who calls w92_nowhere" and
  expects an empty bundle. It got `governance/project/path-map.yaml` lines 1-363.
- The cause: `w2_92_support.path_map()` copied this repository's live path map into the planted project, and
  ACT-OPERATOR-1 (`2a6462653`) added `write_refused` with `root: "~/.gov-os/guard-calls"`, so "calls" matched.
- The CTO reproduced it with the code-graph tool on `PATH` (`CODEINTEL_OFF_PATH=`): 1 failed, 8 passed in the file.

## What to review
- **The branch:** `w2/W2-92-d10-tests` in `/home/usain/gov-os-worktrees/W2-92-d10-tests`. Read
  `git -C /home/usain/gov-os-worktrees/W2-92-d10-tests diff adec4718a..cc128cf3b -- tests/`.
  (A later commit only merges `w2/integrate` in.)
- **The revision:**
  - `path_map()` writes only the kernel schema's required keys (`state_class`, `capabilities`, `policies`,
    `systems`), plus `decision_register` and the suite's namespace;
  - it takes only closed values from the live map, sets each system's `where` to `["**"]` and its `reason` to
    "absent", and drops every optional block;
  - one README paragraph.
- **The designer's runs:** without the tool, 114 passed and 30 skipped, before and after. With the tool, the
  sandbox cannot start the code-graph tool (26 reds, the same before and after).
- **The CTO's run outside the sandbox, with the tool on `PATH` (`CODEINTEL_OFF_PATH=`), at `3e983d544` (`cc128cf3b`
  plus a merge of `w2/integrate`):** `tests/acceptance/W2-92`, 144 passed.

## Check
1. **No expectation lowered:** does any W2-92 case (`links_corpus()`, the hop, stated links, status, drift,
   verbless labels, speed) depend on a block or value the new map drops, so that a case now passes for the wrong
   reason or tests less than it did?
2. **The premise kept:** a question naming no record or symbol still gets today's bundle, item for item.
3. **Validity:** is the planted map still a valid path map for what `gov` reads in these cases (schema, the
   `everything` namespace, the register)?
4. **Trailers:** Task, Role, Implements, Rewrite-Reason and Co-Authored-By. Only `tests/acceptance/W2-92/**` changed.

KPI id for the verdict block: `w2-92-planted-map`.

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
