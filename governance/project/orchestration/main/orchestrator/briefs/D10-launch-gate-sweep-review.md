# D-10's red-fix list: the review of the launcher suites planting an open gate (W2-20, DAEO-r30l)

You are a fresh, read-only independent reviewer. **Narrow scope: one sweep, nine commits.** READY is computed by
`verdict.py` from your block.

## What happened
- Since W2-20's S19 (`d4ceacc1e`, DEC-1088 (5)(b)) every `gov launch` passes the machine's resource gate.
- Acceptance cases that start a real launch read either a HOME with no gate configuration (refused, deterministic)
  or the live machine's gate (refused whenever the machine is loaded, as D-10's own run will load it).
- Tonight W1-46 and W2-54's sandboxed-worker case were refused by `memory: reading 13873688576, limit 14179233792`.
- W2-136's cases (`_plant_open_gate`) and W1-33's (merged tonight, `cfe4ed605`) plant an open gate instead. A test
  designer swept the other launcher suites.

## What to review
- `git -C /home/usain/gov-os-worktrees/W2-20-d10b-tests log --oneline df7c67292..440304dd9` (nine commits:
  W1-46, W1-28, W1-32, W1-38, W1-50, W2-50, W2-54, W2-58, W2-116).
- Read each with `git show`.
  - The shared helper is `w1_46_support.plant_open_gate`. W2-50, W2-58 and W2-116 each have their own.
  - Live-session cases keep the real HOME's `gate.json` (for the CLI's login) and take only planted readings.
  - W1-07 and W2-55 were found not to launch. W2-56 has the pattern and was left alone (another helper's).
- **The designer's runs (sandbox, scratch HOME, `--optin=lifted,breadth`), before → after:**
  - W1-28: 61 failed → 1;
  - W1-32: 17 → 8;
  - W1-38: 42 failed and 16 errors → 37 and 16;
  - W1-46: 286 → 71;
  - W1-50: 23 → 13;
  - W2-50: 116 failed and 212 errors → 0;
  - W2-58: 16 → 0;
  - W2-54: 83 passed, unchanged;
  - W2-116: 6 failed, unchanged (another cause).
  - No case that passed before fails after. The designer names the remaining reds' other causes (W2-56 S5/S15, the
    whole-tree copy check, openspec absent, W1-46's guard cases).

## Check
1. **No expectation lowered:**
   - Does any case whose point is a refusal, the gate, a resource condition or the launch log now pass only because
     the gate is open?
   - Is the gate planted only where a launch must start?
   - Do the planted readings leak into a case that reads the real machine on purpose?
2. **Nothing written to the real HOME;** the live sessions' handling is safe.
3. **No cross-suite coupling** beyond what the suites already had (the W1-46 helper used by W1-28, W1-32, W1-38,
   W1-50, W2-54: did they import W1-46's support before?).
4. **Trailers** on all nine commits, including the Rewrite-Reason. Only `tests/acceptance/**` in the named suites
   changed.

KPI id for the verdict block: `launcher-open-gate`.

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
