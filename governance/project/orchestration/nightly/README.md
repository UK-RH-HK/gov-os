# The nightly full run (owner, standing: DEC-852 item 3, DEC-933 item 2, DEC-934)

Every night between 02:00 and 05:00, a full uncached regression of `w2/integrate`'s head in the close's form, on a fresh clone. The owner's crontab runs the committed scripts in this folder, never a copy in scratch.

| File | What it does |
|---|---|
| `nightly_cron.sh` | cron's entry at 02:00. Refuses to run (P1) unless this folder is exactly its commit at HEAD. Sets a session's environment (HOME, UTF-8 locale, the PATH the closes run with). Logs everything to `log/nightly/cron/<date>.log` in the orchestrator's scratch. Rotates, then starts `nightly.sh night`. |
| `nightly.sh` | The run. At night: books its measured estimate inside the window, starts once the state is clean and no later than 05:00 less the estimate, holds the close and verification locks while it runs, releases them the moment it ends, pings P1 on a red or a night without a verdict, P2 when the estimate no longer fits the window. Removes a green or flaky night's own clone; keeps a red night's for the diagnosis. By day (no argument): a manual run after 5 quiet minutes. |
| `nightly_estimate.py` | The estimate, measured from the last full runs' per-test durations: the parallel sum divided by the lowest effective parallelism of the last three runs (about 7.4 to 8.2 on this machine, not the 20 workers), never less than the longest case; plus the serial sum, the measured setup and 10 %. It records each night's sums, estimate and actual in `log/nightly/history.jsonl`. |
| `nightly_alone.py` | Re-runs each failing case alone once and gives the verdict: `green`, `flaky-candidates <n>` or `red <n>`. |
| `nightly_check.sh` | The morning check, run by cron at 05:30 and five minutes after WSL starts. It writes one line per night to `log/nightly/status.txt` (`ran`, `FAILED` or `MISSED`) and pings P1 on `FAILED` or `MISSED`. |
| `rotate.sh` | Keeps the logs under their budget: cron logs the newest 30 and at most 20 MB; run folders the newest 30 and at most 200 MB; JUnit folders the newest 3. |
| `disk_gate.sh` | DEC-898's disk floor (100 GiB and 10,000,000 inodes free), or no run. |
| `test_nightly.sh` | The tests: 20 cases, on copies against a temporary repository, folder and fake ping. |

## The owner's crontab (ACT-NIGHTLY-1)

```
0 2 * * * bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/nightly_cron.sh
30 5 * * * bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/nightly_check.sh
@reboot sleep 300 && bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/nightly_check.sh
```

## Where a miss shows

- **A night that starts and fails:** `nightly.sh` pings P1, and the check writes `FAILED`.
- **A night that never starts** (cron, WSL or the PC not up): the 05:30 check writes `MISSED` and pings P1. If WSL was down at 05:30 too, the check at WSL's next start does it.
- **The backstop:** the orchestrator's morning digest reads `status.txt` and reports every night since the last digest. A night with no line is `MISSED`, a P1, so a miss is never silent.

## Tests and review (2026-10-28)

`bash governance/project/orchestration/nightly/test_nightly.sh` passes 20 of 20:
- `nightly.sh`: a held lock, a start after 05:00, a close running past the latest start, a merge in progress, a dirty tree and a head under 5 minutes old each stop it with a P1. An estimate over the window pings P2 and goes on. By day it waits and never pings.
- `nightly_cron.sh`: committed code runs with a session's PATH after a rotation. A changed or untracked file in this folder refuses the run with a P1.
- `nightly_check.sh`: nothing before 05:00; `MISSED` with a P1; checked once a night; `FAILED`; `ran` with the verdict and the estimate against the actual; a day run is not a night's.
- `rotate.sh`: the newest 30 logs kept; the newest 3 JUnit folders kept; over the budget, the oldest run folder goes first.

A mutation check: with the committed-code check removed from a copy of `nightly_cron.sh`, cases C2 and C3 fail.

The orchestrator's review findings, fixed before the commit:
- the clone's removal is limited to this night's own stamp under `~/gov-os-runs/W2-00/nightly/`;
- cron's bare PATH would have skipped the rulesync cases, so the entry sets the closes' PATH, checked with `env -i`.

**Not yet exercised:** holding the verification lock through real test phases, and a night's record end to end. The first night does both, and the morning check reports it.
