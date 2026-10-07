"""Adapter/model-portability check: generated adapters match their rulesync source."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys


def _find_rulesync() -> str | None:
    explicit = os.environ.get("RULESYNC_BIN")
    if explicit:
        return explicit if os.path.isfile(explicit) else None
    return shutil.which("rulesync")


def _check_version(bin_path: str) -> str | None:
    expected = os.environ.get("RULESYNC_EXPECTED_VERSION")
    if not expected:
        return None
    result = subprocess.run(
        [bin_path, "--version"], capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        return f"rulesync version check failed (exit {result.returncode})"
    actual = result.stdout.strip()
    if expected not in actual:
        return f"rulesync version mismatch: expected {expected}, got {actual}"
    return None


def _source_empty() -> bool:
    rs = os.path.join(os.getcwd(), ".rulesync")
    if not os.path.isdir(rs):
        return True
    return not any(os.scandir(rs))


def main() -> int:
    if _source_empty():
        print("source folder .rulesync/ is empty or missing", file=sys.stderr)
        return 1

    bin_path = _find_rulesync()
    if not bin_path:
        print("rulesync not found", file=sys.stderr)
        return 1

    version_err = _check_version(bin_path)
    if version_err:
        print(version_err, file=sys.stderr)
        return 1

    targets = "claudecode"
    if os.path.isfile(os.path.join(os.getcwd(), "AGENTS.md")):
        targets = "claudecode,agentsmd"

    result = subprocess.run(
        [bin_path, "generate", "--check",
         "--targets", targets,
         "--features", "rules,hooks,permissions,subagents,commands,skills"],
        capture_output=True, text=True, timeout=30,
    )

    if result.returncode == 0:
        print("[]")
        return 0

    output = result.stdout.strip() + "\n" + result.stderr.strip()
    findings = []
    for token in output.split():
        if any(token.endswith(ext) for ext in (".md", ".json", ".yaml", ".jsonc")):
            clean = token.strip(",'\"[]")
            if clean:
                findings.append({"file": clean, "status": "differs"})

    if not findings:
        for name in ("CLAUDE.md", "AGENTS.md", ".claude/settings.json"):
            findings.append({"file": name, "status": "differs"})

    print(json.dumps(findings))
    return 1


if __name__ == "__main__":
    sys.exit(main())
