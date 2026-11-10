# D-10's red-fix list: the review of W2-58's live-session probe (W2-141, DAEO-xwro)

You are a fresh, read-only independent reviewer. **Narrow scope: one revision.** READY is computed by `verdict.py`
from your block.

## What happened
- W2-58's 5 live-session cases were red: the launched session's hook blocked `bash …/probe.sh`.
- The designer traced it without a live session.
  - The hook allows the probe for both roles.
  - The real cause is that `gov launch` passes no `PYTHONPATH` (W2-56 S5, on purpose). The fixture's hook command,
    a bare `python3 …/pretooluse.py`, then cannot import `gov` and refuses every call.

## What to review
- `git -C /home/usain/gov-os-worktrees/W2-58-d10-tests diff 9ca161a6f..9d99dbaca`. A later commit only merges
  `w2/integrate` in.
  - The probe is one plain Bash line in a single call (no `probe.sh`), each step writing to the scratch folder.
  - The one-try prompt is kept.
  - The live fixture's hook names its interpreter and this tree's code (`PYTHONPATH=<src> … <sys.executable> …/pretooluse.py`),
    as the real project's hook names the pinned interpreter.
- **The designer's runs:** the non-live cases 99 passed before and after. Under the recorded launch environment, the
  fixture's hook allows the line; running it gives the expected results for both roles.
- The live run is the CTO's helper's, after this review.

## Check
1. **What each case measures is unchanged:** the engineer collects and runs its own acceptance tests and sees
   results, the test designer imports the branch's code, no phantom deletion.
2. **The hook fix is right:**
   - Is naming the interpreter and `PYTHONPATH` in the fixture's settings what the real kernel's settings do?
   - Could it make the fixture's guard weaker than the real one (another interpreter, another `gov`)?
   - Does a fixture hook that fails to import `gov` still fail closed?
3. **Discovery (2):** the hook refuses `bash -c '<pytest of the acceptance tests>'` for the engineer while it allows
   the plain call. Is that a false refusal (fails closed, other) or by design? Give it a finding with scope.
4. **Trailers:** Task, Role, Implements, Rewrite-Reason and Co-Authored-By. Only `tests/acceptance/W2-58/**` changed.

KPI id for the verdict block: `w2-58-live-probe`.

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
