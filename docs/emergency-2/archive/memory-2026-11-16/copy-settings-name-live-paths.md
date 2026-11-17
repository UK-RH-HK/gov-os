---
name: copy-settings-name-live-paths
description: "an operator-folder COPY keeps operator-settings.json naming the LIVE home/held-out paths; any step run without --config on the copy reads live data (job runner round 10, 11-16)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-16T06:06:07.037Z
---

A `cp -a ~/gov-os-operator <scratch>/op` copy keeps install/operator-settings.json. That file names the live operator root, HOME and (through job_run's defaults) the live held-out paths. On 2026-11-16, while rehearsing round 10, install.sh ran its new first index pass (`job_run.py --index`) on the copy without --config. It hashed about 88,000 live protected files (the real ~/.ssh and held-out trees) into the copy's log/jobs/protected/. I deleted the index unread and reported it.

It happened twice. My first fix checked the settings' operator_root against the runner's folder. That did not help, because the copy's settings name no operator_root (it defaults to the copy), while HOME defaults to the real `~` and held_out to the live paths. The fix that worked: install.sh runs no index pass at all; the first cron tick makes the index. Both indexes were deleted unread.

**Why:** a hash index of held-out files is a guess-confirmation oracle in my scratchpad. Reads of held-out material by a process I start are what DEC-820 forbids, even when the guard cannot see them.

**How to apply:** before running anything on an operator copy, check every step for a run without `--config`, including steps inside install scripts. Make the code refuse when the settings' operator_root is not the folder it runs from. Planted paths only. See [[no-rehearsal-against-live]].
