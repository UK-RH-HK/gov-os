# ACT-DISPATCHER-1 — the dispatcher survives a reboot or a WSL restart (DEC-1007 item 1)

**What it is:** the dispatcher (`.gov-runtime/scratch/orchestrator/dispatch/`, reviewed PASS on the second round, 33
tests) runs one pass a minute: the gate and the leads from the processes, finished returns into its inbox, the next
ready ticket started when there is room (only from the CTO's `ready.txt`, after its readiness checks), the CTO's
approved landings as one batch, the true status in `status.txt`. It is on now (switched on 19:49, 2026-11-01) as a
detached loop the CTO started (`loop.sh`), which does not come back after a reboot. Cron does: cron already starts with
WSL here (the nightly runs from it), so one line every minute is enough, no `@reboot` needed.

## The change (your WSL terminal; a Claude session is fine)
```
( crontab -l 2>/dev/null; echo '* * * * * bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/dispatch/run_tick.sh' ) | crontab -
crontab -l | grep run_tick.sh
```
Then tell me, and I stop the detached loop (cron takes over; two passes can never overlap: `tick.lock`).

## Stop it at any time
`touch /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/dispatch/OFF` (every pass stops;
delete the file to resume). Undo the cron line: `crontab -l | grep -v run_tick.sh | crontab -`.

## Risk
It starts leads and lands batches on its own, only from the CTO's two lists (`ready.txt`, `land.txt`) and only after
its checks; a wrong line in those lists is the CTO's mistake to catch. Its review's remaining notes are low (a pass
killed in the microseconds between two writes can orphan one approval; it never lands twice).
