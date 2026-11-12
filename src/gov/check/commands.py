"""core-commands: every command of the command list has a module (command-contract consistency)."""
from __future__ import annotations

import json
from pathlib import Path

VERSION = "1.0.0"

RESERVED_COMMANDS = (
    "status", "check", "readiness", "doctor", "rebuild", "context",
    "closure", "retrieve", "checkpoint", "close", "adopt", "pause",
)
# Recorded in the command list beside the twelve (DEC-542).
RECORDED_GOV_COMMANDS = ("accept", "ci", "launch", "resources", "telemetry")
# brief (W2-152, DEC-1088 (3)), links (W2-129, LINK-INTEGRITY, DEC-1074 (7)) and plan (W2-136, DEC-1088).
RECORDED_GOV_COMMANDS = RECORDED_GOV_COMMANDS + ("brief", "links", "plan")
# session-watch (W2-159, DEC-1110): a hyphenated command, its module in the underscore folder session_watch (what
# ``gov`` imports); check() accepts that folder or a folder of the command's own name, as it is.
RECORDED_GOV_COMMANDS = RECORDED_GOV_COMMANDS + ("session-watch",)
# Recorded as the module command it is, ``python3 -m gov.<name>``: no ``gov`` command of that name exists.
RECORDED_MODULE_COMMANDS = ("lock",)

GOV_COMMANDS = RESERVED_COMMANDS + RECORDED_GOV_COMMANDS


def check(root: Path) -> list[dict]:
    root = Path(root)
    findings = []
    for command in GOV_COMMANDS:
        module_path = root / "src" / "gov" / command.replace("-", "_") / "command.py"
        own_path = root / "src" / "gov" / command / "command.py"
        alt_path = root / "src" / "gov" / "cli" / "commands" / f"{command}.py"
        if not (module_path.is_file() or own_path.is_file() or alt_path.is_file()):
            findings.append({
                "code": "COMMAND_NO_MODULE",
                "command": command,
                "message": f"reserved command '{command}' has no module file"
            })
    for command in RECORDED_MODULE_COMMANDS:
        if not (root / "src" / "gov" / command / "__main__.py").is_file():
            findings.append({
                "code": "COMMAND_NO_MODULE",
                "command": command,
                "message": f"module command '{command}' has no module file"
            })
    return findings


if __name__ == "__main__":
    import sys
    root = Path.cwd()
    results = check(root)
    if results:
        print(json.dumps(results, indent=2))
        sys.exit(1)
    sys.exit(0)
