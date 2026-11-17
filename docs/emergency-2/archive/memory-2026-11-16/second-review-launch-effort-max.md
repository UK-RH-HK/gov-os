---
name: second-review-launch-effort-max
description: "a ticket's second reviewer launch (a narrow check after a FULL review counts) must be at effort max, the launcher's probe; high repeats round 1 and gov launch refuses (DEC-1010)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: d5ede711-b29b-4e67-8855-a7ef6103c9eb
  modified: 2026-11-16T10:13:16.450Z
---

A narrow independent check launched after a ticket's FULL review is counted by `gov launch` as review round 2, the "probe" (src/gov/launch/launcher.py `_rubric`, ~line 702-761). Round 2 resolves effort to **max** (and Opus). Launching the auditor at `high`, the same model and effort as round 1, is refused: "LAUNCH_REFUSED: the review of session <id> ran on model claude-opus-5-5, effort high, the setting this launch would repeat: it needs --owner-named <DEC-id> (DEC-1010)". `gov launch --plan` prints only the role default (high) and does not count rounds, so it does not warn. W2-189 au-2, 2026-11-16 10:1x: relaunched at `max`, which needs no --reason because it is the launcher's own resolved value.

**Why:** DEC-1010 allows the same review setting twice only when the owner names it; the probe exists to vary the setting.
**How to apply:** for a ticket's second reviewer launch, pass effort `max` to launch_worker.sh. A third round needs `--owner-named` (at most two rounds), so a narrow check spends the last round: write its brief tight. Related: [[narrow-check-after-review]], [[worker-effort-floor-high]].
