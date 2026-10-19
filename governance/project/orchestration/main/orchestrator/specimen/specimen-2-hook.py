"""Specimen hooks (DEC-495): one script, the event named by its argument. No real project text."""
import json
import sys

event = sys.argv[1]
data = json.load(sys.stdin)
command = str((data.get("tool_input") or {}).get("command", ""))

if event == "PreToolUse":
    if "SPECIMEN-BLOCK" in command:
        print("SPECIMEN-PRETOOLUSE-BLOCKED iota kappa lambda", file=sys.stderr)
        sys.exit(2)
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": "SPECIMEN-PRETOOLUSE-CONTEXT mu nu xi omicron"}}))
elif event == "PostToolUseFail":
    print("SPECIMEN-POSTTOOLUSE-FAILED pi rho sigma", file=sys.stderr)
    sys.exit(1)
elif event in ("SessionStart", "PostToolUse"):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": event,
        "additionalContext": f"SPECIMEN-{event.upper()}-CONTEXT alpha beta gamma delta"}}))
else:  # Stop, SubagentStop, PreCompact: plain output, no context
    print(f"SPECIMEN-{event.upper()}-STDOUT tau upsilon phi")
