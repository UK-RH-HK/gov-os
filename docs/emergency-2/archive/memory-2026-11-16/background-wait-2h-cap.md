---
name: background-wait-2h-cap
description: CORRECTED 11-15 — background Bash waits were NOT killed at 2 h (wake_at 05:25 and the watchers lived 5.5 h+; proc.sh wait ran its full 6 h); still arm a one-shot CronCreate for a far wake as a second trigger
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-15T05:03:49.838Z
---

On 2026-11-14 at 23:15 I assumed a Bash background call dies at its 7,200,000 ms timeout and added a CronCreate as the "real" trigger. Measured at 05:03 on 11-15: `wake_at.sh 05:25`, started 23:15, was still alive at 5 h 31 min. All watchers armed at 22:56 (helper_watch, sentinel_check, bare_watch, store_refresh_daily, usage_log, refused_starts) were alive at 5 h 49 min. A `proc.sh wait --max 21600` ran its own full 6 h. The 2 h cap did not apply to background runs here.

**Why it matters:** wrong beliefs about what keeps running lead to needless re-arming, or to trusting the wrong trigger.

**How to apply:** a far wake can use `wake_at.sh` in the background. A one-shot CronCreate is a cheap second trigger, but not because the background dies. Check watchers with `ps` rather than assume. A `proc.sh wait` ends at its own `--max`, so re-arm it when its timeout line prints and the pid is still alive. Related: [[long-runs-background-timeout]].

**cwd (11-15 05:37):** arm watchers with `cd /home/usain/Dynamic-Agentic-Engineering-OS &&` first. A waiter started while the shell sat in a worktree died (getcwd) when that worktree was removed.
