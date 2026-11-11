# ACT-STOP-WAITER-1: a Stop hook that names an unarmed inbox waiter (DEC-1027 E)

For the owner's operator, in the main tree (a Claude session may run it; it edits `.claude/settings.local.json`, so
Claude Code's safety check asks you). Approved in principle by DEC-1027 E; this file is the exact change.

## 1. Context
The CTO's session wakes only when a background task ends or you write. The dispatcher's inbox reaches it through a
background waiter (`tools/inbox_wait_quiet.sh`), which must be re-armed after every wake. On 2026-11-02 it was not
armed after the reload (01:26; the sentinel caught it 30 minutes later).

## 2. What it does
`governance/project/orchestration/tools/stop_waiter_check.py` (committed with its six unit tests,
`tests/unit/orchestration/test_stop_waiter_check.py`) runs when the CTO's session is about to end a turn. If the
session is the one in `log/cto-session.txt`, no stand-by is declared (`log/cto-standby.txt`), and no inbox waiter
process runs, it answers `block` with a reason naming the waiter and the command to arm it; the turn continues and
the CTO arms it. It never blocks another session, a declared stand-by, or twice in a row (`stop_hook_active`), and on
any error it says nothing: it is a reminder and must never trap a session. Standard library; about 5 ms.

## 3. The change
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
python3 - <<'EOF'
import json, pathlib
p = pathlib.Path('.claude/settings.local.json')
d = json.loads(p.read_text())
hooks = d.setdefault('hooks', {})
entry = {"matcher": "*", "hooks": [{"type": "command",
         "command": "python3 -E /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/tools/stop_waiter_check.py",
         "timeout": 10}]}
stop = hooks.setdefault('Stop', [])
if not any('stop_waiter_check.py' in json.dumps(e) for e in stop):
    stop.append(entry)
p.write_text(json.dumps(d, indent=2) + '\n')
print('Stop hooks:', len(stop))
EOF
python3 -c "import json; d=json.load(open('.claude/settings.local.json')); print(sorted(d['hooks']))"
```
The second line must list `PermissionRequest` (the quiet-hours hook, kept) and `Stop`. Your `env` and `permissions`
are untouched. It takes effect in sessions started after the change, or at the next settings reload.

## 4. The check
In the CTO's session, with no waiter running, the next turn end shows the reason and the CTO arms the waiter. A
`git diff -- .claude/settings.local.json` shows only the `Stop` block (the file is local, untracked if ignored).

## 5. Risk and undo
A broken hook says nothing (fails quiet, by design: it is a reminder, the sentinel stays the net). Undo: delete the
`Stop` entry. No other session is affected (the session id check).
