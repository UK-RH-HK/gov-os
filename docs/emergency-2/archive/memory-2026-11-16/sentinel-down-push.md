---
name: sentinel-down-push
description: "On a sentinel-down inbox item, ping the owner by PushNotification at once, any hour"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 33b3628c-7145-4e49-bfd8-2cfd894e92c4
  modified: 2026-11-04T15:23:13.246Z
---

`tools/sentinel_check.sh` (armed by the CTO; the owner's order of 2026-11-04) drops `dispatch/inbox/*-sentinel-down.txt`
when the sentinel's watch log is stale, its pane shows a login or Remote Control failure, or its tmux session is gone.
On that item, ping the owner by PushNotification at once (any hour: it counts as an emergency, since nothing else can
reach the owner), naming the reason; on `*-sentinel-up.txt`, a short line in the next reply is enough.

**Why:** on 2026-11-04 the sentinel's login expired silently at 11:43 and its alert never reached the owner.

**How to apply:** re-arm `sentinel_check.sh` at each session start while `dispatch/sentinel-expected` exists. Related:
[[standby-file-when-waiting]].
