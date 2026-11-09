Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-20/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-20 — the engineer's brief, round 4: DEC-1105's exception round, R2-F1 only (DAEO-r30l)

You are a fresh engineer for **W2-20** (`.tickets/DAEO-r30l.md`). Round 3 is on `w2/W2-20` (head `2bb6f70b6`), READY by
review round 2 with `gov accept W2-20` 168/0/1 and W2-136 76/76 outside the sandbox. The owner granted one exception
round (DEC-1105, the register's last entry): **fix R2-F1 only.** The designer's case for it, and S16's revised measure,
are merged into your branch.

> **R2-F1. The first reading after ten quiet minutes shuts the gate on cpu.** At `machine.py:303–312`, `known()` counts
> any kept window sample of the server's process, however old. So a server is not resampled. The window is then
> filtered to `KEEP_S` (600 s) at `:330`, leaving it empty. `_window_rate` returns None, `now` is null, and the gate
> shuts on cpu. A launch reads the gate once (`check_start`), so that launch is refused. The next one passes, because
> the failed reading added a fresh sample. (The reviewer's stand-in confirmed it at 700 s; at 300 s the reading is fine.)

**The fix (DEC-1105):** a server whose kept readings have all expired is resampled before the cpu rule reads it (as a
server with no window is today: a short pending sample at once), so the gate never refuses a launch for stale
readings. An unreadable server still reads null and shuts on cpu (F5): only expiry changes. Add a unit case with a
planted history older than `KEEP_S`; update `docs/changes/W2-20-evidence.md`'s R2-F1 row.

- **Nothing else changes.** **The configuration format stays frozen** from `28fbcfebf`: do not touch
  `src/gov/resources/config.py` or any key's name, nesting, value form or meaning.

## Where you work
- `/home/usain/gov-os-worktrees/W2-20`, branch `w2/W2-20`; your paths are the ticket's `allowed_paths`.
- **You never read `tests/acceptance/`**: only `gov accept`'s results. Every Grep or Glob call that could reach it
  carries `!tests/acceptance/**`; recursive grep `--exclude-dir=acceptance`.

## Verify
- Through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src` and `-m "not local_only" -k "not real and not green_here and not time_limit"`:
  `tests/unit/resources tests/unit/launch`; then `python3 -m gov.cli.main accept W2-20 --root /home/usain/gov-os-worktrees/W2-20`.

## Rules
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. Never touch the Ollama servers, the reranker service, `~/.local/bin`,
  `~/.ollama`, `~/.gov-os/` or any service; no GPU job.
- DEC-1080: Read and Grep tools; one simple command per Bash call.
- Do not merge `w2/integrate`. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-20` with
  `--trailer "Task: DAEO-r30l" --trailer "Implements: DEC-1105, DEC-1097" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A small round. Before you end, every run you started has finished.

## Return
Your whole return is your session's **final message** (the launcher keeps it; it is the record): the twelve labelled
fields of `EMG-common.md` (sandbox and `ps` checks first), the change, the new unit case, the unit and `gov accept`
counts.

---

# The interface the R2-F1 case assumes (the designer's README, round 8, as written)

The samples file below is a cache, not the frozen configuration: build to it (round 3 kept these samples in `server-cpu.json`; move them, and read or drop an old `server-cpu.json` so a history written by round 3 never shuts the gate). Nothing in `gate.json` changes.

### The servers' CPU samples (round 8, review R2-F1, DEC-1105)

When `GOV_RESOURCES_EMBEDDING_CPU` and `GOV_RESOURCES_EMBEDDING_CPU_NOW` are not set, the gate takes the two servers'
p95 and current use itself:

- **The servers** are the processes that listen on their addresses, as `gov.retrieval.ollama` reads them:
  `OLLAMA_HOST` (default `127.0.0.1:11434`) for `shared`, `GOV_QUERY_OLLAMA_HOST` (default `127.0.0.1:11435`) for
  `query`; each server's use is that process and its descendants (its runners).
- **The samples file** *(choice)*: `$HOME/.gov-os/machine/embedding-cpu.jsonl`, one JSON object per line, one line
  per server per sample: `{"time": seconds since the epoch, "server": "shared"|"query", "pid": the listening
  process's pid, "cpu_seconds": the user + system CPU time of that process and its descendants, in seconds}`. The p95
  and the current use are computed from the samples **kept**: those of the server's current pid not older than the
  **keep window, 600 s** (the review's `KEEP_S`). A reading appends the samples it takes; it may drop expired lines.
- **Expired is unknown (DEC-1105):** a server whose kept samples have all expired (or that has none under its current
  pid) is **sampled afresh before the cpu rule reads it**, so a reading never shows `embedding_cpu_now` (or the p95)
  `null` for a server that is listening, and the gate never refuses a start for stale samples. How a fresh figure is
  taken (for example two samples a short interval apart) is the engineer's; the fresh sample is written to the file.

`test_w2_20_stale_samples.py` plants this file under the test's HOME with a history of each server, at the live
stand-in's pid and CPU time, all three hours old; the two stand-in servers (a script named `ollama`, run as
`ollama serve`, listening on a free local port named by the two variables) sit idle.


**If this section and round 7's interface (the p95's span, S12) disagree,** keep what S12 and round 7 state for the p95, apply the expiry rule above to the current use, and name the disagreement in your return; never fail open, never change `gate.json`.
