# ACT-NIGHTLY-0400: the nightly at 04:00, its check at 08:00, the Windows wake at 03:50 (DEC-973)

For the owner. **The nightly folder's change is committed: `e8c36347`** (its window 04:00 to 08:00, the check at 08:00 with re-checks at 08:30 and 09:00, the quiet hours 02:00 to 07:30; independently reviewed, PASS; `test_nightly.sh` PASS). **Run it today, before 02:00.** Until it is in, the old crontab still starts the nightly at 02:00 (which works under the new window) but runs the check at 05:30, and the new check does nothing before 08:00: tonight would go unchecked, and the morning package would show it as MISSED.

## Part A: you, in WSL (a plain terminal or your operator)
```
crontab -l > /tmp/crontab-before-ACT-NIGHTLY-0400.txt
( echo "0 4 * * * bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/nightly_cron.sh"
  echo "0 8 * * * bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/nightly_check.sh"
  echo "@reboot sleep 300 && bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/nightly_check.sh"
  echo "30 9 * * * bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/runs_sweep.sh" ) | crontab -
crontab -l
systemctl is-active cron
```
**What changes:**

| Job | Was | Now | Why |
|---|---|---|---|
| The nightly | 02:00 | 04:00 | your new time |
| Its check | 05:30 | 08:00 | after the nightly; it re-checks at 08:30 and 09:00 by itself |
| @reboot check | unchanged | unchanged | |
| `runs_sweep.sh` | 06:15 | 09:30 | it cleans old run folders; after the check and the 09:00 package |

**What to see:**
- `crontab -l` prints the four lines;
- `systemctl is-active cron` prints `active`.

**Rollback:** `crontab /tmp/crontab-before-ACT-NIGHTLY-0400.txt`.

## Part B: you, on Windows (PowerShell, as yourself)
```
$a = New-ScheduledTaskAction -Execute "wsl.exe" -Argument "-d Ubuntu-24.04 -u usain -- sleep 20400"
$t = New-ScheduledTaskTrigger -Daily -At 03:50
$s = New-ScheduledTaskSettingsSet -WakeToRun -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 6)
Set-ScheduledTask -TaskName "GovOS nightly wake" -Action $a -Trigger $t -Settings $s
Get-ScheduledTask -TaskName "GovOS nightly wake" | Get-ScheduledTaskInfo
```
**What it does:**
- The task "GovOS nightly wake" (ACT-NIGHTLY-1) now wakes the PC at **03:50**.
- It holds WSL open for 5 h 40 min, to about 09:30. That covers the nightly (04:00 to about 07:00), its check and re-checks (08:00 to 09:00) and the 09:00 morning package.
- The wake-timer setting from ACT-NIGHTLY-1 stays as it is.
- Then set Windows Update's active hours to cover **03:30 to 09:30**.

**Rollback:** the same three lines with `sleep 12600`, `-At 01:50` and `-Hours 4`.

## Then
Tell me both parts are in. I check `crontab -l`, and the first 04:00 night's line in `status.txt` goes in the 09:00 package, with the estimate against the actual.
