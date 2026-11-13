# ACT-DISPATCH-CRON-2 — the dispatcher's crontab line moves to its committed code (DEC-1010 item 6)

**When:** after the CTO's commit of `governance/project/orchestration/tools/dispatch/` (the code), never before.
**What changes:** only the path of `run_tick.sh`. The state stays where it is (`.gov-runtime/scratch/orchestrator/
dispatch/`), and both the old and the new `run_tick.sh` take the same `tick.lock` there, so even a minute with both
lines in the crontab runs one pass, never two.

In your WSL terminal (your operator):
```
( crontab -l | grep -v 'dispatch/run_tick.sh'; echo '* * * * * /usr/bin/bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/dispatch/run_tick.sh' ) | crontab -
crontab -l | grep run_tick.sh
```
**Check:** the second command prints exactly the new line. Within two minutes,
`tail -3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/dispatch/status.txt` shows a
fresh time and "real busy cores".
**Undo:** the same command with the old path (`.gov-runtime/scratch/orchestrator/dispatch/run_tick.sh`) in the echo.
The `grep -v 'dispatch/run_tick.sh'` removes either line, so running the command twice leaves exactly one.
