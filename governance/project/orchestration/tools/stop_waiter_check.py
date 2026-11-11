"""The CTO's Stop hook (owner, DEC-1027 E): a turn of the CTO's session does not end while its inbox waiter is unarmed.

Claude Code runs it when the session is about to end a turn. If this is the CTO's registered session
(`log/cto-session.txt`), the CTO is not on a stand-by it declared (`log/cto-standby.txt`), and no inbox waiter runs
(`tools/inbox_wait.sh` or `tools/inbox_wait_quiet.sh`), it answers "block" with a reason that names the waiter and the
command, so the turn continues and the CTO arms it. Otherwise, and on any error, it says nothing (a reminder, not a
guard: it must never trap a session). It never blocks twice in a row (`stop_hook_active`). Standard library only.
Overrides for tests: GOV_STOPCHECK_ORCH (the orchestrator's scratch folder), GOV_STOPCHECK_PS (a file listing process
command lines, one per line, instead of /proc).
"""
import json
import os
import sys
from pathlib import Path

ORCH = Path(os.environ.get("GOV_STOPCHECK_ORCH")
            or "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
WAITERS = ("tools/inbox_wait.sh", "tools/inbox_wait_quiet.sh")
ARM = f"bash {ORCH}/tools/inbox_wait_quiet.sh"
REASON = ("The inbox waiter is not armed (DEC-1027 E): returns, landings and the nightly would sit unread. Arm it now "
          f"with the Bash tool's own background run: `{ARM}`; then end the turn.")


def command_lines():
    listing = os.environ.get("GOV_STOPCHECK_PS")
    if listing:
        return Path(listing).read_text().splitlines()
    lines = []
    for entry in Path("/proc").iterdir():
        if entry.name.isdigit():
            try:
                lines.append((entry / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace"))
            except OSError:
                continue
    return lines


def should_block(data):
    if data.get("stop_hook_active"):
        return False
    try:
        cto = (ORCH / "log/cto-session.txt").read_text().strip()
    except OSError:
        return False
    if not cto or data.get("session_id") != cto:
        return False
    if (ORCH / "log/cto-standby.txt").exists():
        return False
    return not any(w in line for line in command_lines() for w in WAITERS)


def main():
    try:
        data = json.load(sys.stdin)
        if should_block(data):
            print(json.dumps({"decision": "block", "reason": REASON}))
    except Exception:  # noqa: BLE001 - a reminder never traps the session
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
