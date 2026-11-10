# D-10's red-fix list: the review of W2-13's latency cases routed by serial-only.txt (W2-13, DAEO-zqvn)

You are a fresh, read-only independent reviewer. **Narrow scope: one revision.** READY is computed by `verdict.py`
from your block.

## What happened
- `tests/acceptance/W2-13/test_w2_13_latency.py::test_a_warm_retrieval_with_the_real_models_answers_within_the_budget`
  asks the real embedder and reranker with W1-19's warm budget (p95 at most 0.5 s). It was red in the full run's
  form and red alone on 11-10 (0.543-0.578 s).
- The CTO's instruction: use the existing mechanism, do not loosen the 0.5 s limit.
- `tests/acceptance/serial-only.txt` routes `real-model` cases to the nightly (DEC-889 item 5), as W1-19's real-model
  file is.

## What to review
- `git -C /home/usain/gov-os-worktrees/W2-13-d10-tests diff 9ca161a6f..1d3cdeb1f`. A later commit only merges
  `w2/integrate` in.
  - The real-model case is added to the real-model block (`nightly: real-model: …`).
  - The no-model lexical latency case is added to the latency block (`serial: latency: …`).
  - A README bullet.
  - The test file and its budget are untouched.
- **The designer's runs:** the readers (W2-57's serial-list and nightly-route cases, W1-30's r11-r13 files, the
  close's serial unit tests): 110 passed and 2 failed. The 2 are in `W1-30/test_w1_30_r11_declared_here.py`: W1-16's
  counts, and an entry naming `W1-16/test_w1_16_ui_off.py` that names nothing. Judge whether they are this
  revision's or older.

## Check
1. **The routes are the file's rules** (its header): is "real-model → nightly" right for the first case and
   "latency → serial" for the second? Is either route a loosening the CTO's instruction forbids? The budget itself
   is unchanged.
2. **The latency red stays visible:** it runs in the nightly and is filed against W2-13, not excused. Say where a
   reader will see it.
3. **The two W1-30 reds:** are they this change's, or red at integrate without it (check by reading the cases and,
   if you can, by running them at `9ca161a6f`)?
4. **Trailers.** Only `tests/acceptance/serial-only.txt` and W2-13's README changed.

KPI id for the verdict block: `w2-13-latency-route`.

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
