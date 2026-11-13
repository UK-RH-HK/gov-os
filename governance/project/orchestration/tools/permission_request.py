"""The quiet-hours safety net (owner, DEC-991): a Claude Code PermissionRequest hook for the CTO's session.

Claude Code runs it at the moment it is about to show a permission prompt. Between 02:00 and 07:30 (local time) it
refuses the call at once, with a message the model reads, and queues it for the 09:00 morning package
(log/approval-queue.jsonl), so a misjudged command can never freeze the session. By day it says nothing and the
normal prompt appears (the owner approves through Remote Control or at the PC; the CTO pinged first). It records
every prompt it sees either way. Standard library only; any error inside the quiet hours still refuses.
`GOV_QUIET_NOW=HH:MM` overrides the clock (tests only).
"""
import json
import os
import sys
import time

QUEUE = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/approval-queue.jsonl"
MESSAGE = ("Quiet hours (02:00 to 07:30): this call needs the owner's approval, so it was refused at once and queued "
           "for the 09:00 morning package (DEC-991). Do not retry it or try another form of it; carry on with other "
           "work and list it in the morning package.")


def quiet(hhmm):
    h, m = (int(x) for x in hhmm.split(":"))
    return 2 * 60 <= h * 60 + m < 7 * 60 + 30


def main():
    hhmm = os.environ.get("GOV_QUIET_NOW") or time.strftime("%H:%M")
    night = quiet(hhmm)
    try:
        data = json.load(sys.stdin)
        tool = data.get("tool_name", "?")
        ti = data.get("tool_input") or {}
        what = ti.get("command") or ti.get("file_path") or json.dumps(ti)[:300]
        with open(os.environ.get("GOV_QUIET_QUEUE") or QUEUE, "a") as f:  # the override: tests only
            f.write(json.dumps({"at": time.strftime("%F %T"), "clock": hhmm, "quiet": night, "tool": tool,
                                "what": str(what)[:1000], "cwd": data.get("cwd"),
                                "session": data.get("session_id"),
                                "outcome": "refused and queued" if night else "asked (by day)"}) + "\n")
    except Exception:  # noqa: BLE001 - the refusal below must happen whatever went wrong
        pass
    if night:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PermissionRequest",
                                                 "decision": {"behavior": "deny", "message": MESSAGE}}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
