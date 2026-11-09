Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-145/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-145 — the engineer's brief, round 2 (DAEO-2tfd)

You are a fresh engineer for **W2-145** (`.tickets/DAEO-2tfd.md`). Round 1 (`86f1af6e`, `20cd694d` on `w2/W2-145`) built
S1 to S5. The CTO ran the socket cases **outside the sandbox**: `tests/acceptance/W2-145`, the W2-145 unit file and
`test_w2_112_shared_reranker.py` give 145 passed, 3 failed. The three failures share one cause, in S1's failure kind
"no connection within CONNECT_S":

- `gov accept`'s messages (results only): *"the reason does not name the service's failure (no-connection-within-connect-s,
  /timed out|timeout|time out|within|connect/): 'the shared reranker did not answer (BlockingIOError: [Errno 11]
  Resource temporarily unavailable)'"*: the same text in `last_outcome()`'s reason, the bundle's rerank entry and the
  `FALLBACK` line.
- What happens: when the service's listen queue is full, a non-blocking connect on a Unix socket fails with EAGAIN
  (`BlockingIOError`), not with a timeout. S1 says the outcome names the service's failure; a raw `Errno 11` does not
  say that no connection was made within `CONNECT_S`.

**Your job:** make a failure of the connect phase (EAGAIN, a refused or absent socket after the start, a connect that
does not complete within `CONNECT_S`) name itself as such, e.g. "no connection to the shared reranker within
CONNECT_S s (BlockingIOError: …)", in `last_outcome()`, the bundle's rerank entry and the `FALLBACK` line alike, without
changing any other failure kind's reason, without retrying past S4's bound, and without starting anything. Add a unit
case for EAGAIN on connect (a stand-in socket whose connect raises `BlockingIOError`, so it runs in the sandbox).

## Where you work
- `/home/usain/gov-os-worktrees/W2-145`, branch `w2/W2-145`; your paths are the ticket's `allowed_paths`.
- **You never read `tests/acceptance/`** (W2-145's, and the revised W2-112 and W2-32 cases): only `gov accept`'s
  results. Every Grep or Glob call that could reach it carries `!tests/acceptance/**`; recursive grep
  `--exclude-dir=acceptance`.
- Unix sockets are refused in the sandbox: run what it allows; the CTO re-runs the socket cases outside.

## Rules
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. No GPU; never the live service or the Ollama servers.
- DEC-1080: Read and Grep tools; one simple command per Bash call. Search again once (DEC-1092 (1)) if a search does
  not answer.
- Do not merge `w2/integrate`. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-145` with
  `--trailer "Task: DAEO-2tfd" --trailer "Implements: DEC-1048, DEC-1097" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Every run through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-145/src`. A small round; before you end, every run has finished.

## Return
Your whole return is your session's **final message** (the launcher keeps it; it is the record): the twelve labelled
fields of `EMG-common.md` (sandbox and `ps` checks first), the change, the new unit case, the unit and `gov accept`
counts you could run.
