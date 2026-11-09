# ACT-GUARD-CALLLOG-1: the rehearsal, 2026-11-09

`rehearsal.log` beside this file is the clean run's record: every step in order, from a fresh `env -i` shell,
16:59–17:09 GMT, **0 failures**. Nothing live was changed.

## The clean run
The run used a `--no-hardlinks` clone of `w2/integrate` at the main tree's head, with a worktree. The clone's
`sets_root_hidden` root pointed at a planted sets root (dummy files only) for every hook run with the real HOME. Each
step had its own log folder under `/tmp/gov-os-calllog-rehearsal/`, set through `GOV_GUARD_CALLS_DIR`. The live
folder `~/.gov-os/guard-calls` was checked absent at every step.

| Step | Result |
|---|---|
| Suites before / after | `test_guard_fix_4` 467 passed; `test_g14` 151 passed, 1 skipped; W2-58 sets, launcher, live hook, reads: 109 passed, 2 failed. **The same before and after.** The two W2-58 launch cases fail at this head without the ACT too. The hook before wrote 0 lines; after, 923 valid lines |
| `guard4_check.py --settings <clone>` (the registered line) before / after | 501 run, 0 failed (527 sets cases, 96 `~` cases skipped with the root planted), both; after: 501 valid lines, one per case |
| `apply.sh` in the clone | check ready; applied (folder 0700, salt 0400, hook `a7981319f877`); a second apply refused; a log folder inside the tree refused |
| Replay, 48 hours to the start (8,142 unique calls) | before → after: 8,103 allow→allow, 39 deny→deny, **0 changed**. After: **8,142 lines, one per call**; the multiset of (sha256 recomputed from the call, decision) equals the log's exactly (0 judged not logged, 0 logged not judged) |
| Planted session (22 calls through the registered line: 8 allowed; 13 refused, one per rule id: 12 rules and the fail-closed `error` for input that is not JSON; 1 asked) | every decision as the hook before (22/22). **22 lines, nothing else**: each with its rule id, role, ticket, agent, tool and tree, its sha256 and keyed hash equal to those recomputed. The folder holds the day file and the salt only. No marker text from any input in the log. The same action in another session carries the same two hashes |
| Faults (each of the 22 calls): a read-only folder and day file; a read-only folder; a full disk (EFBIG); the day's cap; the folder a file; the day file a link; the folder a link; a write that hangs (FIFO); no salt; a relative `GOV_GUARD_CALLS_DIR`; an unwritable default folder | **0 decisions changed** in 242 calls. One stderr note per call where nothing was written. Nothing written through links; the full and capped files did not grow; the cap marker made. The hang costs 2.0 s (the log's own deadline). No salt: lines written, keyed null. A relative setting is ignored (the default under the planted HOME) |
| Prune | files past 92 days removed by name; 91-day and recent files and every other name kept; a second call removes nothing |
| Concurrent | 8 sessions at once, 200 calls: 200 whole lines |
| **Latency** (120 calls each, before and after alternated) | median 71.0 → 73.0 ms (**+2.0 ms**); p95 128.4 → 123.3 ms (noise). The log's own cost in the process: **43 µs** per call |
| Live session (haiku, `--no-session-persistence`, as an engineer: Read, `echo` with a marker, `sudo`, a `.env` read, a Write into `tests/acceptance/`, Glob) | 6 tool calls in Claude Code's stream; **6 lines, matched 6 of 6** by the sha256 of `{tool, input}` recomputed from the stream. The decisions match the stream's results (3 allow; deny `4-sudo`, `3-secret`, `1`). Role and ticket as launched. 0 lines with no call; 0 marker lines; $0.006 |
| `apply.sh undo` | the hook byte for byte, `git status` clean; a folder holding only this apply's salt removed. A fresh apply then undo: the same |
| Live files (the hook, `role_reads.py`, `bash_writes.py`, the map, `held-out.yaml`, `settings.json`, `settings.local.json`, `~/.claude/settings.json`; `~/.gov-os/guard-calls` absent) | **unchanged** |

## What the earlier runs found (kept in the record)
1. **Run 1 (16:47):** its last check failed on its own test. It counted the main tree's HEAD and untracked files.
   Other sessions committed during the run (W2-148's merge, DEC-1107), and this ACT's package was written meanwhile.
   Every hashed file was unchanged and every other step passed with the same counts. **Fix:** the check compares the
   files' hashes and tracked edits; HEAD is shown as information.
2. **A partial run (16:19)** of the cheap steps: 0 failures. Its log is not kept here.

## Limits
- The live session matched the hook's input to Claude Code's **stream** (`stream-json`), the same message content a
  transcript records. A persisted transcript was not used, to leave no trace under `~/.claude`.
- The 20-second deadline path (`deadline`) is not driven in the rehearsal. It goes through the same `answer()` →
  `record()` as every refusal.
- The replay's lines run in a clone, so they carry tree `run` and the session `seal-replay`. Live lines carry the
  session's UUID and `main` or `worktree`.
