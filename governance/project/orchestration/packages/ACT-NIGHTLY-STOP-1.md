# ACT-NIGHTLY-STOP-1 — Stop every scheduled nightly run (DEC-1049, amending DEC-1047)

For the owner's operator, in a plain terminal or a Claude session (it changes only the crontab, not `gov`).
Written 2026-11-02 21:59 by the CTO. Dry-run on a copy of the live crontab: exactly the three nightly lines change, the
dispatcher's every-minute line and the 09:30 runs sweep stay, and the undo restores the crontab byte for byte.

## Why
The owner (DEC-1049): no nightly full-suite run until the investigation's lifting and refactoring are done; the full
suite runs again only on the owner's word. Stop the 04:00 nightly and its 08:00 and @reboot checks, each line kept,
commented out, for an exact undo. The dispatcher's every-minute line stays as it is.

## Commands (run as `usain`)
```bash
# 1. A backup of the crontab as it is now
crontab -l > ~/crontab.pre-nightly-stop-$(date +%Y%m%d-%H%M).txt

# 2. Comment out the three nightly lines, nothing else
crontab -l | sed -e 's|^0 4 \* \* \* bash .*/nightly_cron\.sh$|# DEC-1049 stopped: &|' \
                 -e 's|^0 8 \* \* \* bash .*/nightly_check\.sh$|# DEC-1049 stopped: &|' \
                 -e 's|^@reboot sleep 300 && bash .*/nightly_check\.sh$|# DEC-1049 stopped: &|' | crontab -
```

## The check (all three must hold)
```bash
crontab -l
crontab -l | grep -v '^#' | grep -c 'nightly_cron\|nightly_check'                  # expect 0: no nightly scheduled
crontab -l | grep -c '^# DEC-1049 stopped: '                                        # expect 3: the three lines kept
crontab -l | grep -c '^\* \* \* \* \* /usr/bin/bash .*/dispatch/run_tick\.sh$'     # expect 1: the dispatcher untouched
```

## Undo (exact)
```bash
crontab -l | sed 's|^# DEC-1049 stopped: ||' | crontab -
# or restore the backup: crontab ~/crontab.pre-nightly-stop-<stamp>.txt
```

## What the CTO does alongside (its own tools, no ACT)
- The dispatcher's landing hold before the nightly (03:15 to 05:30, DEC-1018) is switched off in
  `.gov-runtime/scratch/orchestrator/dispatch/config.json` (`nightly_hold_from` and `nightly_hold_until` both `00:00`:
  an empty window), so landings are not held for a nightly that will not run; restored with the nightly.
- No nightly "MISSED" P1 while DEC-1049 holds: the morning package says "nightly stopped by DEC-1049".
