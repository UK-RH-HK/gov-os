Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-145-d10-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: the review of W1-19's default-reranker case under the shared service (W2-145, DAEO-2tfd)

You are a fresh, read-only independent reviewer. **Narrow scope: one revision.** READY is computed by `verdict.py`
from your block.

## What happened
- `tests/acceptance/W1-19/test_w1_19_real_models.py::test_the_default_reranker_is_a_process_of_its_own_started_from_the_reranker_environment`
  (`local_only`, the real reranker) required a process started from the reranker environment's interpreter
  **under the calling process** (DEC-397, ADR-0002 §2).
- Since DEC-982 (W2-112) one shared reranker service serves every session, and W2-145 removes the private reranker
  beside it. So a call made while the service already runs starts nothing under the caller.
- The CTO measured it at integrate `b0bbd373f`: alone, with the service up, 1 failed
  (`no process started with …/reranker-venv/bin/python was seen under the calling process`). Every scoring check
  before that passed.
- A test designer revised the case under W2-145's ticket. Rewrite-Reason: DEC-982.

## What to review
- **The branch:** `w2/W2-145-d10-tests` in `/home/usain/gov-os-worktrees/W2-145-d10-tests`. Read
  `git -C /home/usain/gov-os-worktrees/W2-145-d10-tests diff 9f9809e09..6f693ee53`.
  - `c2dc4a563` is the CTO's ticket commit.
  - `6f693ee53` is the revision:
    - a helper `_service_processes` finds the processes holding the service's listening socket
      (`/proc/net/unix`, then `/proc/<pid>/fd`), from W2-112's README line 75;
    - the case requires that some process listen at the socket after the call, started with
      `support.reranker_python()` and never from the workbench;
    - every Python process under the caller must come from that interpreter and must be the service;
    - the scoring checks and the no-heavy-libraries check are unchanged;
    - one README line.
- **The runs:**
  - The designer could not run the case: the sandbox refuses `socket(AF_UNIX)` and hides the service's processes.
  - The CTO ran it outside the sandbox with the service up: 1 passed.
  - The service-down run (the call starts it) is the CTO's, when the shared service has idled out.

## Check
1. **No fail-open:** can the revised case pass when the reranker does not run in a process of its own from the
   reranker environment? Consider:
   - the caller scoring in-process with a stand-in;
   - a service started by another interpreter;
   - a process that listens at a stale socket path;
   - a socket held by an unrelated process;
   - the private fallback answering when the service did not answer.
   Is "every Python process under the caller is the service" too strict or too loose (matching by the first four
   arguments)?
2. **Robust on this machine:** `/proc/net/unix` parsing (listening entries only, path column, inode); a socket
   path with spaces; the service ending between the call and the lookup; another user's processes whose fds cannot
   be read.
3. **The decisions:** read DEC-397, DEC-982 and ADR-0002 §2 in the repository. Does the case still test what
   DEC-397 and ADR-0002 §2 ask that DEC-982 left standing? Is the unchanged name honest?
4. **Trailers:** Task, Role, Implements, Rewrite-Reason and Co-Authored-By on `6f693ee53`. Only the two files
   changed, plus the CTO's ticket line.

KPI id for the verdict block: `w1-19-default-reranker`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this revision.

## Write and return
- **You write nothing** in any tree.
- You may run tests read-only through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`. This case
  cannot run in your sandbox; collect it only (`--collect-only -q`).
- No GPU, no installs, never the full suite. Single simple Bash commands (DEC-1080).
- The hidden-half rule holds: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **Your record is your session's final message**, in full:
  - the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
  - your answers to the checks;
  - every finding, with its two lines and its scope;
  - at the end, the fenced `verdict` block:
    `{"kpis": [{"kpi": "w1-19-default-reranker", "verdict": "pass|fail", "findings": [...]}]}`, each finding
    `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 15 minutes.
