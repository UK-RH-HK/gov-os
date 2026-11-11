# ACT-SCHEDULE-STOP-2 — Nothing scheduled runs until the refactoring is finished (DEC-1050 item 5)

For the owner's operator (it changes only the crontab). Written 2026-11-02 22:48 by the CTO. Dry-run on a copy of the
live crontab: only the 09:30 runs-sweep line changes; the undo restores the crontab byte for byte.

## Why, and the CTO's reading
DEC-1050 (5): "nothing scheduled runs until the refactoring is finished". ACT-NIGHTLY-STOP-1 already stopped the nightly
and its two checks. Left in the crontab: the 09:30 runs sweep (`runs_sweep.sh`, clean-up of old run clones) and the
dispatcher's every-minute pass. **This ACT stops the sweep.** The dispatcher's pass stays: it is the Load Balancer and
the landings, which DEC-1047 keeps on (its scheduled side jobs are already off: the guard harvest, DEC-1050 (6); the
pre-nightly landing hold, DEC-1049). Say if the dispatcher should stop too.

## Commands (run as `usain`)
```bash
crontab -l > ~/crontab.pre-schedule-stop-$(date +%Y%m%d-%H%M).txt
crontab -l | sed -e 's|^30 9 \* \* \* bash .*/runs_sweep\.sh$|# DEC-1050 stopped: &|' | crontab -
```

## The check
```bash
crontab -l
crontab -l | grep -v '^#' | grep -vc 'dispatch/run_tick\.sh'                      # expect 0: nothing scheduled but the dispatcher
crontab -l | grep -c '^\* \* \* \* \* /usr/bin/bash .*/dispatch/run_tick\.sh$'     # expect 1: the dispatcher untouched
```

## Undo (exact)
```bash
crontab -l | sed 's|^# DEC-1050 stopped: ||' | crontab -
```
