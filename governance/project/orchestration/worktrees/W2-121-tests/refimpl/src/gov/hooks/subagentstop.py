#!/usr/bin/env python3
"""SubagentStop hook (W1-29, CAP-37.d).

Enforces the 12-field worker return contract of Framework S61.
Parses last_assistant_message for the fields as JSON keys or text labels.
Exit 0 if all present; exit 2 (block) if any missing, naming them once on stderr.
"""
from __future__ import annotations

import json
import re
import sys

TWELVE_FIELDS = (
    "task", "status", "work_completed", "files_changed",
    "evidence", "tests", "discoveries", "risks",
    "lessons", "proposed_decisions", "unresolved",
    "recommended_next_action",
)


def _find_fields(message: str) -> set[str]:
    found: set[str] = set()
    try:
        obj = json.loads(message)
        if isinstance(obj, dict):
            found.update(k for k in obj if k in TWELVE_FIELDS and obj[k] is not None and obj[k] != "")
    except (json.JSONDecodeError, TypeError, ValueError):
        pass
    for field in TWELVE_FIELDS:
        if field in found:
            continue
        pattern = re.compile(
            rf'(?:^|\n)\s*(?:#+\s*)?[\*_]*{re.escape(field)}[\*_]*\s*[:=][ \t]*\S',
            re.IGNORECASE,
        )
        if pattern.search(message):
            found.add(field)
    return found


def main() -> None:
    data = json.loads(sys.stdin.read())
    message = data.get("last_assistant_message", "")
    found = _find_fields(message)
    missing = [f for f in TWELVE_FIELDS if f not in found]

    if not missing:
        sys.exit(0)

    reason = f"Worker return contract incomplete. Missing fields: {', '.join(missing)}"
    sys.stdout.write(json.dumps({"hookSpecificOutput": {
        "hookEventName": "SubagentStop",
        "blockReason": reason,
        "missingFields": missing,
    }}))
    # Claude Code reads a SubagentStop block's reason from stderr on exit 2 (stdout is not delivered).
    sys.stderr.write(reason + "\n")
    sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write(f"Worker return contract could not be checked: {exc}\n")
        sys.exit(2)
