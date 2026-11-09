# D-10's red-fix list, item (6): the review of test_fusion's revision for DEC-1090 (2) (DAEO-5emz)

You are a fresh, read-only independent reviewer. **Narrow scope: one unit case.** READY is computed by `verdict.py`
from your block.

## What happened
W2-137 (`.tickets/DAEO-5emz.md`, KPI S1) raised `gov.retrieval.rerank.MAX_REQUEST_TEXTS` from 16 to 64 (DEC-1090 (2)).
`tests/unit/semantic/test_fusion.py::test_only_the_first_30_fused_chunks_are_scored_and_returned` still expected
requests of `[16, 14]` and went red: it now gets `[30]`. An engineer revised only that expectation to the cap in force.

## What to review
- **The branch:** `w2/W2-137-d10` in `/home/usain/gov-os-worktrees/W2-137-d10`, from integrate at `bc72066fa417`.
  Read `git -C /home/usain/gov-os-worktrees/W2-137-d10 log --format='%h %s' bc72066fa417..HEAD`, then the diff.
  - `14efc5cf3c9e` is the CTO's ticket line, which put the file in W2-137's paths.
  - The engineer's commit or commits after it.

## Check
1. **No expectation lowered.** The request sizes are computed from the cap in force (and from `MAX_REQUEST_CHARS`
   if that bound applies), not from a new literal. Would the case still catch a request over the cap? Would it catch
   a split that was not needed, or more than `RERANK_TOP` texts scored?
2. **Everything else the case protects is unchanged:** exactly the first 30 scored, one rerank of them, the
   reranker's order, `limit=2`, and the unranked fallback.
3. **Only that case changed:** no other case, and no code under `src/`. The trailers are Task, Role, Implements and
   Co-Authored-By.
4. Run `tests/unit/semantic/test_fusion.py` and `tests/unit/retrieval/test_w2_137_request_cap.py` at the branch head:
   all green.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this revision.

## Write and return
- **You write nothing** in any tree.
- You may run the tests read-only (`-p no:cacheprovider`) through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`. Use
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-137-d10/src`, an empty scratch HOME, and
  `PYTHONUSERBASE=/home/usain/.local`.
- No GPU, no model, no shared server, no installs, never the full suite. Single simple Bash commands (DEC-1080).
- The hidden-half rule holds: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **Your record is your session's final message**, in full:
  - the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
  - your answers to checks 1-4;
  - every finding, with its two lines and its scope;
  - at the end, the fenced `verdict` block:
    `{"kpis": [{"kpi": "S1-test_fusion", "verdict": "pass|fail", "findings": [...]}]}`, with each finding
    `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 10 minutes.
