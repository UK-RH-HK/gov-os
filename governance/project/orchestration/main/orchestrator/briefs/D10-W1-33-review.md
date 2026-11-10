# D-10's red-fix list: the review of W1-33's launcher cases under the gate and the lead check (W2-20, DAEO-r30l)

You are a fresh, read-only independent reviewer. **Narrow scope: one revision.** READY is computed by `verdict.py`
from your block.

## What happened
- Four W1-33 cases were red at integrate (the CTO's landing selection; the helper reproduced them):
  - `test_the_launcher_gives_the_role_an_empty_network_profile[engineer|independent-auditor|independent-test-designer]`:
    the gate was shut because the case's HOME had no `gate.json`. Since W2-20's S19 (`d4ceacc1e`, DEC-1088 (5)(b))
    every `gov launch` passes the gate.
  - `test_the_launcher_starts_no_session_for_a_role_that_is_not_a_worker[orchestrator]`: the refusal no longer names
    "worker role". Since W2-136's S9 (`69aa361ab`, DEC-1088 (5)(a)) an orchestrator launch on a ticket is a lead
    launch, checked against the approved ready list.
- A test designer revised them under W2-20's ticket.

## What to review
- `git -C /home/usain/gov-os-worktrees/W2-20-d10-tests diff 16f4958c5..e66c69c45 -- tests/`.
  - The `launch` fixture plants an open gate (`plant_open_gate`, after W2-136's `_plant_open_gate`).
  - Row 2 becomes `[orchestrator-no ready list]` and `[orchestrator-a ready list without the ticket]`: a non-zero
    exit, no session, the refusal naming "ready list" or "batch" and the ticket.
  - The README's count and one line.
- **The designer's runs:**
  - default: 4 failed, 106 passed → 111 passed (1 skipped);
  - with `--optin=lifted,breadth`: 6 failed → 2 failed, the two DEC-1111 cases.

## Check
1. **No expectation lowered:** does the open gate hide anything W1-33 tests (the network profile, one session)? Is
   the gate planted only where a launch must start? Does any refusal case now pass for the gate's reason instead of
   its own?
2. **Row 2 against DEC-1088 (5) and W2-136's S9** (read both in the repository): is "an orchestrator on a ticket
   outside the approved batches starts no session, named" the right reading? Is W1-33's KPI (the launcher starts no
   session for a role that is not a worker) still tested where it still holds, or properly superseded?
3. **The DEC-1111 cases** are untouched.
4. **Trailers:** Task, Role, Implements, Rewrite-Reason and Co-Authored-By. Only `tests/acceptance/W1-33/**`
   changed.

KPI id for the verdict block: `w1-33-launcher-gate`.

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
