---
name: rearm-inbox-waiter-every-time
description: re-arm inbox_wait_quiet.sh in the same response as every waiter completion; on 11-15 two lead returns (W2-174 22:11, W2-88 22:50) sat unread ~50 min because I did not
metadata:
  type: feedback
---

On 2026-11-15 the inbox waiter's completion (21:5x) was handled, and the waiter was not re-armed. W2-174's DONE (22:11) and W2-88's DONE (22:50) sat in the inbox until the helper watch's 24-hour end made me look at 23:00.

**Why:** with no waiter armed, nothing wakes me for a lead's return. The land and the next round wait silently, which costs critical-path time (release 0.1.1).

**How to apply:** every time a waiter completes, read the item, file it in inbox/read/, and re-arm `bash .gov-runtime/scratch/orchestrator/tools/inbox_wait_quiet.sh` (background, 7200000 ms) in the same response, even when the item needs no action. Re-arm the helper watch when it ends (24 h). Related: [[waits-by-pid-only]], [[long-runs-background-timeout]].

**Waiter guard (11-15 23:5x):** `tools/waiter_guard.sh` also runs in the background. It exits, and so wakes me, when an inbox item is unread for more than 10 min, or when the inbox waiter or helper watch has been gone for 2 min. Re-arm it in the same response as each of its exits, like the waiter.
