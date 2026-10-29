# The nightly full run (owner, standing: DEC-852 item 3, DEC-933 item 2, DEC-934)

Every night between 02:00 and 05:00, a full uncached regression of `w2/integrate`'s head in the close's form, on a fresh clone. The owner's crontab runs the committed scripts in this folder, never a copy in scratch.

| File | What it does |
|---|---|
| `nightly_cron.sh` | cron's entry at 02:00. Refuses to run (P1) unless this folder is exactly its commit at HEAD. Sets a session's environment (HOME, UTF-8 locale, the PATH the closes run with). Logs everything to `log/nightly/cron/<date>.log` in the orchestrator's scratch. Rotates, then starts `nightly.sh night`. |
| `nightly.sh` | The run. At night: books its measured estimate inside the window, starts once the state is clean and no later than 05:00 less the estimate, holds the close and verification locks while it runs, releases them the moment it ends, pings P1 on a red or a night without a verdict, P2 when the estimate no longer fits the window. Removes a green or flaky night's own clone; keeps a red night's for the diagnosis. By day (no argument): a manual run after 5 quiet minutes. |
| `nightly_estimate.py` | The estimate, measured from the last full runs' per-test durations: the parallel sum divided by the lowest effective parallelism of the last three runs (about 7.4 to 8.2 on this machine, not the 20 workers), never less than the longest case; plus the serial sum, the measured setup and 10 %. It records each night's sums, estimate and actual in `log/nightly/history.jsonl`. |
| `nightly_alone.py` | Re-runs each failing case alone once and gives the verdict: `green`, `flaky-candidates <n>` or `red <n>`. |
| `nightly_check.sh` | The morning check, run by cron at 05:30 and five minutes after WSL starts. It writes one line per night to `log/nightly/status.txt` (`ran`, `FAILED` or `MISSED`) at once, and pings P1 on `FAILED` or `MISSED` through the gate: at once if the owner is active, otherwise at 07:30. It stays running until then to send the night's held pings. |
| `ping_gate.sh` | Every ping of the nightly goes through it (DEC-936). From 07:30 to midnight it pings at once. From midnight to 07:30 it pings at once only if the owner used Windows in the last 15 minutes (Windows' last-input time, read through PowerShell); otherwise it holds the ping, and the morning check sends it at 07:30, or as soon as the owner is active, marked "held from". An unreadable idle time counts as inactive: held, never lost. |
| `rotate.sh` | Keeps the logs under their budget: cron logs the newest 30 and at most 20 MB; run folders the newest 30 and at most 200 MB; JUnit folders the newest 3. |
| `disk_gate.sh` | DEC-898's disk floor (100 GiB and 10,000,000 inodes free), or no run. |
| `test_nightly.sh` | The tests: 28 cases, on copies against a temporary repository, folder and fake ping. |

## The owner's crontab (ACT-NIGHTLY-1)

```
0 2 * * * bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/nightly_cron.sh
30 5 * * * bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/nightly_check.sh
@reboot sleep 300 && bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/nightly_check.sh
```

## Where a miss shows

- **A night that starts and fails:** `nightly.sh` pings P1, and the check writes `FAILED`.
- **A night that never starts** (cron, WSL or the PC not up): the 05:30 check writes `MISSED` and pings P1. If WSL was down at 05:30 too, the check at WSL's next start does it.
- **When the P1 arrives:** every night ping goes through `ping_gate.sh`. It reaches the owner at once if they are active; otherwise at 07:30, marked with the time it was held. The status line is written at once either way.
- **The backstop:** the orchestrator's morning digest reads `status.txt` and reports every night since the last digest. A night with no line is `MISSED`, a P1, so a miss is never silent.

## Tests and review (2026-10-28)

`bash governance/project/orchestration/nightly/test_nightly.sh` passes all its cases (2026-10-29, after DEC-945):
- `nightly.sh`: a held lock, a start after 05:00, a close running past the latest start, a merge in progress, a dirty tree and a head under 5 minutes old each stop it with a P1. An estimate over the window pings P2 and goes on; the disk gate shut at night stops it, for the morning package (DEC-945). By day it waits and never pings. It takes the machine's rebuild lock (`/tmp/gov-os-rebuild.lock`) for its clone's rebuild, and records the time spent waiting for the verification lock apart from its setup (DEC-939 items 2 and 6).
- `nightly_estimate.py`: the lock wait recorded apart; the estimate's setup is the smallest recorded.
- `nightly_cron.sh`: committed code runs with a session's PATH after a rotation. A changed or untracked file in this folder refuses the run with a P1.
- `nightly_check.sh`: nothing before 05:00; `MISSED` with a P1; checked once a night; `FAILED`; `ran` with the verdict and the estimate against the actual; a day run is not a night's. With the owner inactive at 05:30, the line is written at once, the P1 is held, and it goes at 08:00 marked held.
- `ping_gate.sh`: by day at once; at night at once when the owner is active; held when inactive or unreadable; `--wait-flush` waits at 04:00 and flushes at 07:30.
- `rotate.sh`: the newest 30 logs kept; the newest 3 JUnit folders kept; over the budget, the oldest run folder goes first.

Two mutation checks:
- with the committed-code check removed from a copy of `nightly_cron.sh`, cases C2 and C3 fail;
- with `ping_gate.sh` made to ping always, cases K7, K8 and G3 to G6 fail;
- with its message filter removed, cases P4 and P5 fail.

The idle read was checked live on 2026-10-28: at a simulated 03:00, with the owner active (37 s idle), the ping went at once.

The orchestrator's review findings, fixed before the commit:
- the clone's removal is limited to this night's own stamp under `~/gov-os-runs/W2-00/nightly/`;
- cron's bare PATH would have skipped the rulesync cases, so the entry sets the closes' PATH, checked with `env -i`.

**Not yet exercised:** holding the verification lock through real test phases, and a night's record end to end. The first night does both, and the morning check reports it.
