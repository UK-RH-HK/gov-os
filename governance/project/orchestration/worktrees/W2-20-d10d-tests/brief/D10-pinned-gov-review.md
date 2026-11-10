Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-20-d10d-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: the review of the planted pinned gov for the kernel-hook suites (W2-20, DAEO-r30l)

You are a fresh, read-only independent reviewer. **Narrow scope: three small commits.** READY is computed by
`verdict.py` from your block.

## What happened
- The kernel's hook line (W2-106, `template/governance/kernel/settings.json:13`) runs `$HOME/.local/bin/gov`, or
  else `gov` from PATH, or refuses with "gov hook: no pinned gov".
- W1-46's planted projects (and W2-90's kernel wiring) give the hook a scratch HOME with no pinned gov. The cases
  passed only when the runner's own PATH held the installed `gov`.
- The CTO's landing check (a clean PATH) found 20 W1-46 reds. The CTO's helper reproduced it: 4 passed with
  `~/.local/bin` on PATH, 4 failed with `PATH=/usr/bin:/bin`.
- A test designer revised it under W2-20's ticket.

## What to review
- `git -C /home/usain/gov-os-worktrees/W2-20-d10d-tests log --oneline 09e1ff6e1..5b6873b3a`, then `git show` each:
  - `3a1be7726` W1-47: `plant_pinned_gov` gives a stand-in HOME this tree's pinned gov (`<HOME>/.local/bin/gov`);
  - `24a71cafb` W1-46: `ask_guard` plants it;
  - `5b6873b3a` W2-90: `install_gov_for` plants it too.
- **The CTO's helper's run outside the sandbox** (W1-46, W1-47, W2-90, both opt-ins, `-n auto`, `-m "not local_only"`):
  - integrate under a clean PATH: 117 failed, 222 "no pinned gov" messages;
  - the merge under a clean PATH: 71 failed, 0 such messages;
  - the merge under the normal PATH: 71 failed.
  - All 71 are on `optin-lifted-guard.txt` (report-only), none gated.

## Check
1. **No fail-open:**
   - Does the planted pinned gov run this tree's own guard (the code under test), and never a looser one?
   - Could a case now pass because the hook finds the planted gov where the real product would refuse?
   - Is any case's point "no pinned gov refuses", and is it kept?
2. **No writes outside the case's own folders,** and no change to the real HOME.
3. **Cross-suite coupling:** W1-46 and W2-90 now use W1-47's helper. Was that coupling already there? Is it sound?
4. **Trailers** on all three commits, including the Rewrite-Reason; only `tests/acceptance/**` changed.

KPI id for the verdict block: `pinned-gov-fixture`.

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
