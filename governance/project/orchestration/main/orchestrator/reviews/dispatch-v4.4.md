# Review of dispatcher v4.4 (commit 7f81f91a, DEC-1030) - independent, read-only

Method: read the diff; ran tests/unit/orchestration/test_dispatcher.py (136 passed, 92.8 s); probed watch_gpu / gpu_log_new on temp folders with planted nvidia-smi scripts and logs (probe in the session scratchpad); timed the baseline read of the real 287 MB log read-only (0.14 s, 431k lines, 2 error lines in the last 32 MB); ran the real nvidia-smi once (0.06 s; compute-apps lists pid 47866 as [Not Found]/[N/A], handled).

Confirmed good: an nvidia-smi that hangs costs at most 2 x gpu_smi_timeout_s and the log pass still runs (probe: alert written while smi hung); an exception in watch_gpu is caught in tick() and becomes one "failures" entry, other duties (returns, start, land, embed, slots, status) are unaffected; offsets are saved only after the item is written, so a failed write retries rather than loses; partial last line waits; truncation/new inode restarts at 0; 64 MB per-pass cap bounds cost; the real log's lines ("CUDA error: unknown error", the ggml-cuda.cu CUDA error line, "offloaded 0/29") match the patterns. The skip guard tests TOOLS/"land.py"; in the main tree it exists (untracked, git-ignored), so the 6 tests run, not skip (all 136 passed, none skipped).

## Findings

### F1 - empty nvidia-smi output (rc 0) aborts the whole pass before the logs are read
Scenario: nvidia-smi exits 0 with no stdout (driver half-loaded, wrapper printing to stderr). gpu_read does `lines[0]` -> IndexError; it escapes gpu_read and watch_gpu (probe: "IndexError('list index out of range')", inbox 0 although a CUDA error line was waiting). tick() catches it as "gpu watch: IndexError". Offsets are not advanced, so the lines are read once nvidia-smi answers again (probe 2 then alerted); while it keeps answering empty, no log is read and no alert is ever written, at the moment the GPU is most likely broken.
Ordinary work: yes, because a crashed CUDA context is exactly when nvidia-smi misbehaves, and this pass's job is to run then; but empty-with-rc-0 specifically is uncommon (a dead GPU normally gives a non-zero exit, which is handled as "unreadable").
Consequence: fails open (missed alert while the condition lasts; self-heals when smi answers).
Scope: in. Severity: low-medium. Fix: `if not lines:` -> {"ok": False, ...}; and wrap gpu_read so the log pass never depends on it.

### F2 - a damaged or deleted gpu-health.json silently swallows the crash that is waiting
Scenario: the dispatcher is killed (or the disk fills) mid `write_text` of gpu-health.json; the next pass load_json returns {}, every log is "first", `errors = [] if first`, and the baseline reads only the last 32 MB. Probe: a CUDA error line appended with a corrupt state file produced 0 new items. Same if the file is removed during a clean-up. The write is not atomic (write_text), unlike a temp-file-and-rename.
Ordinary work: yes (a restart under the loop, a kill of the dispatcher during an update, a clean-up of the folder), but it needs the kill to land inside the write or someone to delete the file, and the crash to fall between two passes; rare.
Consequence: fails open (one missed alert; also a 0-layer incident in progress is re-derived only from the latest load in the last 32 MB).
Scope: in. Severity: low. Fix: write to a temp file and rename; on a corrupt (not absent) state treat errors as new, or at least log it.

### F3 - a second crash within gpu_alert_gap_s (30 min) of the last CUDA error line is logged, not alerted
Scenario: crash at 10:00 (alert), owner or restart fixes it, a second crash at 10:20: `err_last` is refreshed on every error line, the pass logs "(same incident)", no inbox item, no gpu: line. The real log shows three crashes (lines 1724865, 3232500, 3421608); a restart loop of crash, reload, crash is the typical pattern for this fault, and the per-incident rule makes the second-onward invisible except in dispatcher.log.
Ordinary work: yes (repeated crashes while the cause is being chased).
Consequence: other - by DEC-1030 "once per incident" this is the stated design; it fails open only if an incident is meant to end at recovery. A load with layers after an error is the natural end of an incident and is not used for it.
Scope: in, as a design question for the owner. Severity: low. Option: end the incident at the next successful `offloaded X/Y` with X>0 after the error.

### F4 - first read and a retired state ignore errors; layers older than the baseline are unknown
Scenario: first pass after the v4.4 deploy (or a path change in gpu_logs): CUDA errors in the last 32 MB are deliberately not alerted (only 2 are there now, from earlier crashes), and a 0/29 load older than 32 MB shows "shared ?". Intended and documented ("learn the current layers").
Ordinary work: yes, once at deploy. Consequence: other (no alert for events before the watch started). Scope: in. Severity: informational.

### F5 - gaps in the cap and the shrink-and-regrow case
(a) A burst over 64 MB between two passes is read from the tail only; earlier error lines are skipped (only logged as capped? no - not logged at all). (b) A log truncated in place (same inode, `>` redirect) that regrows past the saved offset between two passes is read from the old offset, mid-line; at ~1 pass per tick and 290 MB of offset this needs a very fast regrow.
Ordinary work: no, because an honest agent would need 64 MB of log in one tick, or a truncate plus 290 MB regrowth in one tick; the real log grows ~MB per day. Consequence: fails open in theory. Scope: in. Severity: negligible. (Suggest logging when `capped`.)

### F6 - splitlines on the decoded log
`str.splitlines` also breaks on \x0b, \x0c, \x1c-\x1e, \x85 and U+2028/9; a model-name or prompt fragment containing one would split a line, which cannot hide a match but can shift the "began mid-line" drop. Ordinary work: no (Ollama logs are ASCII). Consequence: other. Scope: in. Severity: negligible.

### F7 - the 6 skipped-by-name tests
No problem found. The guard is a single `land.py` check for tests that also read close_build.py; in a tree with land.py but no close_build.py those parametrised cases would fail rather than skip. Ordinary work: no (both are the CTO's pair, copied together). Consequence: other. Scope: in. Severity: negligible.

## Dispatcher duties
No stall found: worst added time per pass is 2 x 10 s (hung smi) plus a log read bounded at 64 MB (baseline 32 MB measured at 0.14 s, steady state a few KB); failure of the pass is isolated by its own try/except and shown as a TICK FAILED line; status and stale-line writers read the state defensively (load_json). The `gpu:` key is added to the stale-line parser without disturbing the other keys.

```verdict
{"kpis": [
 {"kpi": "no-missed-alert", "verdict": "fail", "findings": [
  {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"},
  {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"},
  {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}
 ]},
 {"kpi": "dispatcher-duties-unharmed", "verdict": "pass", "findings": []}
]}
```

## Round 2 (commit 30d1f6bf, dispatcher v4.5) - F1, F2, F3 only

Method: read the diff; 138 tests pass (93 s); probed on temp folders (empty-answer smi, repeated crashes, corrupt state, deleted state).

- F1 fixed. `gpu_read` treats an empty answer as ok False, and `watch_gpu` wraps `gpu_read` in try/except, so the logs are read whatever the GPU read did. Probe: smi exit 0 with no output, a CUDA error line appended: 1 alert written.
- F2 fixed for the case reported. `gpu_save` writes a temp file then `os.replace` (no leftover .tmp in the probe). A present-but-unreadable file sets `recovering`, so the first re-read counts error lines. Probe: corrupt file, then a crash line: 1 new alert. The re-read covers the last 32 MB, so error lines already alerted in that window may alert once more (a duplicate, not a miss; accepted). Remaining, not claimed fixed: a gpu-health.json that is deleted (absent, not unreadable) still counts as a first read, and a crash between the deletion and the next pass is not alerted (probe: 0 new items). Ordinary work: no, because nothing in the dispatcher deletes the file and an honest agent has no reason to; Consequence: fails open; Scope: in; severity: negligible.
- F3 fixed per DEC-1030. Default gap 0 and `>=`: every pass with new error lines alerts; a pass with no new lines does not re-alert (offsets advance; probe: 2 alerts for 2 crashes, none for an idle pass). A storm gives one combined item per pass, not one per line. The live dispatch/config.json has no gpu keys, so the default applies.
- Nothing new fails open. gpu_save failure (disk full) raises into tick()'s try/except, offsets stay unsaved, and the pass retries (a possible duplicate alert, never a miss). Two minor notes: README.md line 101 still says `gpu_alert_gap_s` 1800 (stale text; not a safety issue), and the `recovering` path logs once per pass while the file stays unreadable (it is rewritten whole on that same pass, so once).

```verdict
{"kpis": [
 {"kpi": "no-missed-alert", "verdict": "pass", "findings": [
  {"id": "F8", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}
 ]},
 {"kpi": "dispatcher-duties-unharmed", "verdict": "pass", "findings": []}
]}
```
