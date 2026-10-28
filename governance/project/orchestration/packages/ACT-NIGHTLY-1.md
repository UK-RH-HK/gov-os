# ACT-NIGHTLY-1 — The nightly every night at 02:00: one line in your crontab (DEC-933 item 2)

From: the W2 orchestrator, 2026-10-28. Your operator runs it (DEC-928 item 3: it does not replace or reinstall gov).

## What it does

It adds one line to your user crontab, so that cron starts `tools/nightly.sh night` at 02:00 every night, whether or not a Claude session is open. The script then does what DEC-933 item 2 says:
- it estimates the run from the last full runs (tonight: 84 minutes);
- it starts once the state is clean, no later than 05:00 less the estimate;
- it holds the close and verification locks while it runs, and lets them go at its end;
- it writes the result and the estimate against the actual for the morning digest;
- it pings P1 on a red or a night without a verdict, and P2 when the estimate no longer fits the window.

The machine must be awake at 02:00 (cron runs here; systemd is on).

## When

Any time. The first run is the next 02:00 after the line is in. The nightly waits for any close or merge in progress, so nothing has to be stopped first.

## The commands

```
crontab -l 2>/dev/null > /tmp/crontab-before-ACT-NIGHTLY-1.txt; cat /tmp/crontab-before-ACT-NIGHTLY-1.txt
( cat /tmp/crontab-before-ACT-NIGHTLY-1.txt; echo "0 2 * * * bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/nightly.sh night > /dev/null 2>&1" ) | crontab -
crontab -l
```

## What to see

- The first `cat` prints your crontab as it was (nothing, if you had none).
- The last `crontab -l` prints the same lines, plus the one `0 2 * * * bash …/nightly.sh night …` line.

## Rollback

`crontab /tmp/crontab-before-ACT-NIGHTLY-1.txt` puts back the crontab as it was.

## Then

Tell me it is in. I check `crontab -l`, and the morning digest after the first night gives the run's result and its estimate against the actual.
