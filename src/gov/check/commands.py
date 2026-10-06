"""core-commands: every reserved command has a module (command-contract consistency)."""
from __future__ import annotations

import json
from pathlib import Path

VERSION = "1.0.0"

RESERVED_COMMANDS = (
    "status", "check", "readiness", "doctor", "rebuild", "context",
    "closure", "retrieve", "checkpoint", "close", "adopt", "pause",
)


def check(root: Path) -> list[dict]:
    root = Path(root)
    findings = []
    for command in RESERVED_COMMANDS:
        module_path = root / "src" / "gov" / command / "command.py"
        alt_path = root / "src" / "gov" / "cli" / "commands" / f"{command}.py"
        if not module_path.is_file() and not alt_path.is_file():
            findings.append({
                "code": "COMMAND_NO_MODULE",
                "command": command,
                "message": f"reserved command '{command}' has no module file"
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
