"""Specimen hooks, third specimen (DEC-495): one script, the case named by its argument. No real project text."""
import json
import os
import sys

case = sys.argv[1]
data = json.load(sys.stdin)
command = str((data.get("tool_input") or {}).get("command", ""))
here = os.path.dirname(os.path.abspath(__file__))


def once(name):
    """True the first time only: a blocking Stop hook must let the session end the second time."""
    flag = os.path.join(here, f".{name}.done")
    if os.path.exists(flag):
        return False
    open(flag, "w").close()
    return True


if case == "SessionStartPlain":
    print("SPECIMEN-SESSIONSTART-PLAIN alpha beta gamma delta")
elif case == "SessionStartFail":
    print("SPECIMEN-SESSIONSTART-FAILED epsilon zeta eta", file=sys.stderr)
    sys.exit(1)
elif case == "PreToolUse":
    if "SPECIMEN-HOOK-DENY" in command:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse", "permissionDecision": "deny",
            "permissionDecisionReason": "SPECIMEN-PRETOOLUSE-DENY-REASON theta iota kappa"}}))
elif case == "PostToolUseFailure":
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PostToolUseFailure",
        "additionalContext": "SPECIMEN-POSTTOOLUSEFAILURE-CONTEXT lambda mu nu"}}))
elif case in ("Stop", "SubagentStop"):
    if once(case):
        print(f"SPECIMEN-{case.upper()}-BLOCKED xi omicron pi: answer with the single word done", file=sys.stderr)
        sys.exit(2)
    print(f"SPECIMEN-{case.upper()}-STDOUT rho sigma tau")
