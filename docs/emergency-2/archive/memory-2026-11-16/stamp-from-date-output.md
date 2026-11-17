---
name: stamp-from-date-output
description: "Every time stamp written in a record, report or push is copied from a `date` output in the same or the previous command, never guessed or rounded up"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 6ff2ee7c-f234-443c-8484-b5e93fc3d159
  modified: 2026-11-16T16:01:04.873Z
---

Copy every time stamp (CHECKPOINT lines, ready.txt comments, stand-by file, report-state, reports, pushes) from a `date '+%H:%M'` output taken in the same command or the one just before. Never estimate the time and never round up.

**Why:** on 11-14 my stamps ran ahead of the clock again and again: 13:45, 15:25–15:55, 17:30/17:35, 18:45–18:53, 19:50, then 22:04 in ready.txt and 22:21 in the handover stand-by and push, each written one or more minutes before that time. Each one counted as a stale fact in the trial.

**How to apply:** run `date` before you write; if more than a minute may have passed since, run it again. Related: [[lesson-to-memory-at-once]].

**Again 2026-11-14 23:39 (session acd80751):** I stamped the owner's message "~23:40" in DEC-1185 before the clock reached it (it arrived about 23:36). It was corrected by ebedddd60. For an owner message, take the time of the last `date` printed before it arrived, never a rounded-up minute.

**Again 2026-11-16:** CHECKPOINT stamps "17:0x", "17:1x" and "17:2x" were guessed. `date` printed 16:00. They are now corrected to "before 16:00" and "16:00 (date)".
