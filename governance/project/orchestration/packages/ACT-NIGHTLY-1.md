# ACT-NIGHTLY-1 (revised) — The nightly every night: three crontab lines, and the Windows side that keeps the machine up at 02:00 (DEC-933 item 2, DEC-934)

From: the W2 orchestrator, 2026-10-28; revised at the owner's four points (DEC-934). Part A is run by your operator; Part B is on Windows, by you.

## 1. Committed, reviewed code (your point 1)

- cron runs the committed scripts in `governance/project/orchestration/nightly/` (README there), not a copy in scratch.
- **The entry refuses to run** unless that folder in the main tree is exactly its commit at HEAD (no change, nothing staged, no untracked file). A refusal is a P1 ping and a line in the log.
- **Reviewed by me with its tests** (`test_nightly.sh`, 20 of 20). A mutation check shows the tests catch a removed code check. The findings I fixed before the commit are in the README.
- Changing the folder later is a reviewed commit with its tests passing (prompt §15).

## 2. Logged, never discarded; a miss is a P1 (your point 2)

- **The log:** everything the entry and the run print goes to `.gov-runtime/scratch/orchestrator/log/nightly/cron/<date>.log`.
- **Rotation, before each night** (`rotate.sh`):
  - cron logs: the newest 30, at most 20 MB together;
  - run folders: the newest 30, at most 200 MB together;
  - JUnit folders: the newest 3.
  - A green or flaky night's clone is removed by the run itself; a red night's is kept for the diagnosis.
- **The morning check** (`nightly_check.sh`, at 05:30 and five minutes after WSL starts) writes one line per night to `log/nightly/status.txt`:
  - `ran`, with the verdict and the estimate against the actual;
  - `FAILED`: started, but no verdict;
  - `MISSED`: nothing started.
  
  `FAILED` and `MISSED` ping P1.
- **The backstop:** my morning digest reports every night since the last digest from `status.txt`. A night with no line is `MISSED`, a P1. So a silent miss can't happen, even when neither cron line could run.

## 3. Does cron run in this WSL, and after a restart? (your point 3)

**Measured today:**
- **Distro and services:** `Ubuntu-24.04`, with `systemd=true` in `/etc/wsl.conf`. `cron` is enabled and active, running since 2026-10-16 02:29.
- **Uptime:** this WSL has been up since 2026-10-16 (one boot), with 24 GB of memory (`.wslconfig`).
- **cron at night:** its own hourly job ran 4 of 4 times between 01:30 and 05:30 on every night from 2026-10-20 to 2026-10-28. So cron runs here, and the PC was awake at night all week. (The journal's "Clock change detected" lines are WSL's time sync, every 34 s; cron ran through them.)
- **Under cron's bare environment** (`env -i`), the entry's PATH finds the same `python3` (with pytest 9.0.3, xdist, pytest-timeout, sqlite-vec), git, flock, rulesync, gitleaks, claude and node as a session.

**After a restart:**
- **A WSL restart:** systemd starts cron with the distro, because cron is enabled. The `@reboot` line then checks the night it may have missed.
- **What doesn't survive:** the distro starts only when something on Windows starts it (a terminal, VS Code, `wsl.exe`). After a Windows restart, or if WSL stops when no Windows program holds it open, nothing runs at 02:00 until someone opens WSL. The miss would be reported, but the night would be lost.
- **The fix (Part B):** a Windows scheduled task at 01:50 that wakes the PC and starts WSL, holding it open through the window with `wsl.exe … sleep`. cron inside then fires at 02:00 as usual. The task does nothing else: the run itself stays in the committed scripts.

## 4. What the machine needs at 02:00 (your point 4)

- **The PC on and awake from 01:50 to about 05:15.** Either sleep set to "Never" when plugged in, or wake timers allowed (Part B's task wakes it). Hibernation must not take it down in the window. If it's a laptop, on mains power.
- **You logged in to Windows** (a locked screen is fine). WSL runs per user, so it doesn't start before a login.
- **WSL running:** Part B's task does that.
- **The network up:** the live-session cases reach their allowlisted hosts.
- **No Windows Update restart between 01:30 and 05:30:** set Windows Update's active hours to cover it.

## Part A — your operator, in this repository (a plain terminal is not needed: it doesn't reinstall gov)

```
crontab -l 2>/dev/null > /tmp/crontab-before-ACT-NIGHTLY-1.txt; cat /tmp/crontab-before-ACT-NIGHTLY-1.txt
( cat /tmp/crontab-before-ACT-NIGHTLY-1.txt
  echo "0 2 * * * bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/nightly_cron.sh"
  echo "30 5 * * * bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/nightly_check.sh"
  echo "@reboot sleep 300 && bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/nightly_check.sh" ) | crontab -
crontab -l
systemctl is-active cron
```

**What to see:**
- the first `cat` prints your crontab as it was (nothing, if none);
- `crontab -l` prints it plus the three lines;
- `systemctl is-active cron` prints `active`.

**Rollback:** `crontab /tmp/crontab-before-ACT-NIGHTLY-1.txt`.

## Part B — you, on Windows (PowerShell, as yourself)

```
$a = New-ScheduledTaskAction -Execute "wsl.exe" -Argument "-d Ubuntu-24.04 -u usain -- sleep 12600"
$t = New-ScheduledTaskTrigger -Daily -At 01:50
$s = New-ScheduledTaskSettingsSet -WakeToRun -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 4)
Register-ScheduledTask -TaskName "GovOS nightly wake" -Action $a -Trigger $t -Settings $s
powercfg /SETACVALUEINDEX SCHEME_CURRENT SUB_SLEEP RTCWAKE 1
powercfg /SETACTIVE SCHEME_CURRENT
```

- The task wakes the PC at 01:50, starts WSL if it is down, and holds it open for 3.5 hours (to about 05:20).
- The two `powercfg` lines allow wake timers on mains power. Check it in Control Panel: Power Options → Change plan settings → Change advanced power settings → Sleep → Allow wake timers: Enable.
- Then set Windows Update's active hours to cover 01:30 to 05:30.

**Rollback:** `Unregister-ScheduledTask -TaskName "GovOS nightly wake"`.

## Then

Tell me both parts are in. I check `crontab -l` and the scheduled task's state. The first night's line in `status.txt` and its log are in the next morning's digest, with the estimate against the actual.
