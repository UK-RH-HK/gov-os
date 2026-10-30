# ACT-RUNS-SWEEP-1 — Old run clones removed daily by your cron, outside the guard (DEC-941 item 5)

From: the W2 orchestrator, 2026-10-29. Your operator runs it (it does not replace or reinstall gov, DEC-928 item 3).

## What it does

It adds one line to your crontab. Every day at 06:15 it runs the committed `governance/project/orchestration/nightly/runs_sweep.sh`, which removes old run clones under `~/gov-os-runs/W2-00/`. The guard rightly refuses the orchestrator's own `rm` there (annex C, slip E4: about 3 GB kept).

It removes only a folder that:
- sits directly in `nightly/` (named `YYYYMMDD-HHMM`) or `act-runs/` (named `<name>-YYYYMMDD-HHMM`);
- is older than 24 hours;
- no process holds open;
- for a nightly clone, belongs to a night whose verdict was not red, or is older than 7 days. A red night's clone is kept a week for the diagnosis.

Nothing else is touched. Every removal and every kept folder is logged to `.gov-runtime/scratch/orchestrator/log/nightly/cron/runs-sweep-<date>.log`.

**Tested:** `test_nightly.sh` cases S1 to S7 (a temporary folder; nothing outside the stamps touched). The guard's rules stay as they are.

## The commands

```
crontab -l > /tmp/crontab-before-ACT-RUNS-SWEEP-1.txt; cat /tmp/crontab-before-ACT-RUNS-SWEEP-1.txt
( cat /tmp/crontab-before-ACT-RUNS-SWEEP-1.txt
  echo "15 6 * * * bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/runs_sweep.sh" ) | crontab -
crontab -l
```

## What to see

- The first `cat` prints the three nightly lines.
- `crontab -l` prints them, plus the one `15 6 * * * bash …/runs_sweep.sh` line.

## Rollback

`crontab /tmp/crontab-before-ACT-RUNS-SWEEP-1.txt`.

## Then

Tell me it is in. The next morning's package reports the first sweep's log.
