# A fresh FULL probe of W2-96 (DAEO-ouet) after D-10's merge into its judged files (DEC-895)

You are a fresh, read-only independent reviewer: the **FULL probe** of W2-96 that `probe_impact.py` scheduled.
W2-96's last probe (`docs/probes/DAEO-ouet/PR-DAEO-ouet.md`, pass at `90122df096e7`) is stale because a later merge
(`f7e63ae4e`, D-10's red-fix list) changed four of its judged files.

## What changed since the last probe
- `tests/unit/accept/test_w2_96_run2.py`, `test_w2_96_accept.py`, `test_w2_96_review3.py`, `test_w2_96_review4.py`,
  and the new `tests/unit/accept/w2_96_reap.py` (`6bcbbcdd5`, `65fa76dc3`, a test designer).
  - Every planted `gov accept` now runs in its own session.
  - A reaper on a pipe kills its process groups on every ending.
  - Three proof cases.
  - Cause: the incident `.gov-runtime/scratch/orchestrator/log/incidents/2026-11-10-0043-outside-slot.md`.
  - Its own review is READY (`governance/project/orchestration/reviews/D10-W2-96-review.md`).
- Nothing in `src/gov/accept/**` changed since the last probe. Confirm with `git log 90122df096e7..9ca161a6fe38 -- src/gov/accept`.

## What to judge, against W2-96's KPIs (read its ticket file at integrate `9ca161a6fe38`)
1. Do the revised builder tests still test what W2-96's KPIs need? The signal handling (128+N, held during the
   clean-up), the clean-up, and no test content reaching the caller.
2. Is any case weaker than before, or now passing for the reaper's reason instead of gov's?
3. **Run read-only:**
   - `tests/unit/accept` (both opt-ins, serial and `-n 4`);
   - W2-96's acceptance suite through `gov accept W2-96`, the declared way:
     `PYTHONPATH=src /home/usain/.local/share/gov-os/pin-bcea09060ebc/bin/python -m gov.cli.main accept W2-96`;
   - report the counts.
4. **Your judgement:** pass or fail for W2-96 as it stands at `9ca161a6fe38`.

KPI id for the verdict block: `w2-96-full-probe`. In your record's twelve fields, put the probed commit
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
