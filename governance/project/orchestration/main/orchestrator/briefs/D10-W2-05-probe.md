# A fresh FULL probe of W2-05 (DAEO-0z8c) after D-10's merge into its paths (DEC-895)

You are a fresh, read-only independent reviewer: the **FULL probe** of W2-05 that `probe_impact.py` scheduled.
W2-05's last probe (`docs/probes/DAEO-0z8c/PR-DAEO-0z8c-dec971.md`, judgement pass at `e122beca7ef7`) is stale
because a later merge (`384b2245b`, D-10's red-fix list item 1) changed one of its judged files.

## What changed since the last probe, in W2-05's paths
- `.tickets/DAEO-0z8c.md`: `tests/conftest.py` added to its `allowed_paths` (`b83e73b99`). Later, DEC-1109 joined its
  sources.
- `tests/conftest.py` and `tests/unit/gitenv/test_w2_05_suite_git_env.py` (`5e9cdcc8d`, a test designer): the
  suites drop git's repository-local variables in every process of a run (the core.bare fix's tests' half). Its own
  review is READY (`governance/project/orchestration/reviews/D10-coregit-review.md`).
- Other tickets' changes to `tests/conftest.py` since the last probe (W2-56 `8eb7a39aa`, `7dea70376`, `bf13ef74f`;
  W2-141 `92b38e74e`) are not W2-05's. Look at them only for whether they break W2-05's KPIs.

## What to judge, against W2-05's KPIs (read its ticket file at integrate `9ca161a6fe38`)
1. **The success KPI:** "Every check, test helper and command that runs git in another folder clears the inherited
   GIT_* variables. One helper does it." Does the conftest strip, together with W2-05's own helper
   (`src/gov/util/gitenv.py`), still meet it? Does anything in the D-10 change contradict W2-05's one-helper rule
   for product code?
2. **The DEC-710 case:** a hooked commit in a linked worktree keeps its branch, index and reflog. Is it unaffected?
3. **Run W2-05's acceptance suite and its unit tests read-only:**
   - `tests/acceptance/W2-05` and `tests/unit/gitenv` with both opt-ins;
   - name every red and whether it is W2-05's or another ticket's;
   - at this writing W2-05's adapter-portability cases are red at integrate from other tickets' skill and `.claude/`
     changes, waiting on ACT-CLAUDE-COPIES-2.
4. **Your judgement:** pass or fail for W2-05 as it stands at `9ca161a6fe38`.

KPI id for the verdict block: `w2-05-full-probe`. In your record's twelve fields, put the probed commit
`9ca161a6fe38` and your session id in `evidence`.

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
