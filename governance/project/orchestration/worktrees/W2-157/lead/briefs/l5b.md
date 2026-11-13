## L5b (the lead's reading, added after review round 1's FR-1 and FR-2): the backstop's own group is paused last

When the process group of the `gov` process itself (`os.getpgrp()`) is among the named groups (for example a job
started with `&` from the same non-interactive shell that runs `gov resources --backstop`, so both share one group):

1. at start, the start log line (L6) carries `; own group <g> named: paused last` at its end;
2. on a trip, every other live named group is paused first (SIGSTOP, in the order named); then the TRIP log line (L6) and
   the one inbox item (L7) are written, the item's `paused:` line listing every paused group the own group included,
   with its `resume:` and `stop:` lines, and one more line `note: the backstop's own group <g> is paused last; resuming
   it resumes the backstop, which then ends`; then, last of all, SIGSTOP to the own group (which stops `gov` too);
3. so while everything is stopped, every named group is stopped and the TRIP line and the item exist; after
   `kill -CONT -- -<g>` the command ends: exit 0, `tripped: true`, `paused` holding every paused group (the own one
   included), as L8.

When the own group is not named, nothing changes. Nothing else is signalled; no group is refused for being the own one.
