# ACT-DEADMAN-1 — the dead-man's switch on the CTO's session (DEC-988 item 4, DEC-991 item 6)

**Owner act:** one crontab line, with the channel you choose. In your WSL terminal (a Claude session is fine; nothing
here replaces gov).

## 1. Context
On 2026-11-01 the CTO's session waited 8 h 52 min (01:46 to 10:37) on one permission prompt, and on 2026-10-31 7 h
45 min on another. Nothing noticed: the session itself was the thing that pings, and `owner-ping` only writes
`~/.config/gov-os-notify/pings.log`, which reaches no phone (the nightly's 08:00 P1s never reached you either).
DEC-991 stops the cause (no prompting call in the quiet hours; ping first by day; ACT-QUIET-DENY-1 as the net).
This switch is the last net, for whatever else stalls the session.

## 2. What it does (tested)
`governance/project/orchestration/tools/deadman.py`, every 15 minutes from cron:
- reads the newest transcript in `~/.claude/projects/-home-usain-Dynamic-Agentic-Engineering-OS/` and its last
  `assistant` entry (entry types and times only, never their text; not the file's mtime, which queued notifications
  kept moving during the freeze);
- alerts when that is over 60 minutes old (inside 02:00 to 07:30 only past 2 hours): "the CTO session is waiting on a
  tool (Bash; likely a permission prompt) since 01:46, 133 min | approve or restart it", or "idle since HH:MM (its turn
  ended and nothing woke it)";
- one alert per stall, then a reminder every 2 hours; every check logged in `log/deadman.log`.
- **Tests:** replaying last night's transcript cut at 04:00 gives the alert above (waiting on Bash since 01:46, 133 min);
  at 02:30 and 03:00 (quiet hours, under 2 hours) no alert; this live session: alive. Unit tests in
  `tests/unit/orchestration/test_cto_safety_nets.py`.

## 3. Why it matters
A frozen CTO stops every merge, close and lead start, and last night it also kept the nightly from running. The
Gov OS's promise is unattended progress with the owner told of anything that needs them.

## 4. The channel: the open question (your choice)
| Option | Reaches | Cost and install | Tested today | Risk |
|---|---|---|---|---|
| (a) **Windows toast** (PowerShell, from WSL) | the PC's screen only | none | 12:13: the call returned ok (please confirm you saw "Gov OS TEST") | useless when you are away or asleep |
| (b) **Headless `claude -p` calling PushNotification** | your phone through Remote Control, when the PC is not in use | none; about $0.11 per alert (Haiku) | 12:14: the tool exists headless; it answered "not sent: this terminal is active" (you were at the PC, the designed skip) | not yet seen reaching the phone from cron: needs one away test (below); depends on Remote Control and your account's push setting |
| (c) **A phone push service** (ntfy, free app; Pushover, paid) | the phone, always | an app on your phone (DEC-945: your call) | not tested | a third-party service; a topic name is the only secret |
| (d) **Email** (the Gmail connector) | the phone's mail | none, but the Gmail connector needs your authorisation in claude.ai first | unavailable now | slower; needs the connector |
| (e) the log only (`pings.log`) | nobody | none | yes | what failed last night |

## 5. Recommendation (confidence: medium-high)
**(a) + (b) + (e) now** (no install, no paid service); the away test of (b) right after: lock the PC for 20 minutes
and tell me, and I run `deadman.py --channel push` with a forced test line; if it does not reach your phone, (c) ntfy
as a yes-or-no question. Threat model: an honest failure (a prompt, a hang), not an adversary.

## 6. What it blocks, and what waiting costs
Nothing waits on it; DEC-991's rule and ACT-QUIET-DENY-1 cover the known cause. Without it, any other stall goes
unnoticed until you look.

## The commands (choose the channel; the recommended line first)
```
# 1. add the line (recommended channels: toast,push,log)
( crontab -l 2>/dev/null; echo '*/15 * * * * /usr/bin/python3 /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/deadman.py --channel toast,push,log >> /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/deadman-cron.log 2>&1' ) | crontab -
# 2. check it
crontab -l | grep deadman
python3 /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/deadman.py --dry
# undo: crontab -l | grep -v deadman.py | crontab -
```
For the log only, use `--channel log`; for the PC only, `--channel toast,log`.
