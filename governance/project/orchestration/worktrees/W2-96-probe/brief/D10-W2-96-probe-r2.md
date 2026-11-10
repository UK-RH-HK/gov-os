Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-96-probe/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# A fresh FULL probe of W2-96 (DAEO-ouet), round 2, after D-10's command-list merge (DEC-895)

You are a fresh, read-only independent reviewer: the **FULL probe** of W2-96 that `probe_impact.py` scheduled again.
W2-96's probe of this morning (`docs/probes/DAEO-ouet/PR-DAEO-ouet-d10.md`, pass at `9ca161a6fe38`) went stale when
the merge `c3bf5a547` changed four of its judged files. W2-96's own earlier commits recorded `accept` in those
lists (DEC-970).

## What changed since that probe, in W2-96's judged files
- `tests/acceptance/W1-07/README.md`, `test_w1_07_recorded_commands.py`, `w1_07_support.py` and
  `tests/acceptance/W1-32/test_w1_32_command_set.py`: a test designer recorded `brief`, `links` and `plan` in
  the command lists, beside `accept` (DEC-753). The code list `src/gov/check/commands.py` was changed in `fb4b7a05d`.
  The review is READY (`governance/project/orchestration/reviews/D10-commands-review.md`).
- Also since: W1-46's and W1-27's README maps were made readable by `gov accept` (`8b31965ed`).
- Read `git log 9ca161a6fe38..8b31965edae8 -- tests/acceptance/W1-07 tests/acceptance/W1-32 tests/unit/accept src/gov/accept`
  to confirm nothing else.

## What to judge, against W2-96's KPIs (its ticket file at `8b31965edae8`)
1. `accept` stays recorded and offered; W2-96's command-list KPI holds.
2. **Run read-only:**
   - W1-07's recorded-commands file and W1-32's command set (both opt-ins);
   - `tests/unit/accept` (both opt-ins);
   - `gov accept W2-96` the declared way:
     `PYTHONPATH=src /home/usain/.local/share/gov-os/pin-bcea09060ebc/bin/python -m gov.cli.main accept W2-96`.
   - Report the counts. This morning's probe found the declared run failing four lines whose named cases D-4's cut
     leaves out of the default run, with every case passing. Say whether that still holds.
3. **Your judgement:** pass or fail for W2-96 at `8b31965edae8`.

KPI id for the verdict block: `w2-96-full-probe`. Put the probed commit and your session id in `evidence`.

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
