"""core-mutation: check implementer write scope (mutation scope)."""
from __future__ import annotations

import fnmatch
import json
from pathlib import Path

import yaml

VERSION = "1.0.0"

TICKETS_REL = ".tickets"
IMPLEMENTER_ROLES = ("engineer", "product-spec", "research")
ACCEPTANCE_PATTERNS = ("tests/acceptance/**", "tests/acceptance/*")


def _frontmatter(text: str) -> dict | None:
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = lines.index("---", 1)
    except ValueError:
        return None
    try:
        front = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError:
        return None
    return front if isinstance(front, dict) else None


def _is_under_acceptance(pattern: str) -> bool:
    if pattern == "tests/acceptance/**" or pattern == "tests/acceptance/*":
        return True
    if pattern.startswith("tests/acceptance/"):
        return True
    if fnmatch.fnmatch("tests/acceptance/W1-99/test.py", pattern):
        return True
    return False


def check(root: Path) -> list[dict]:
    root = Path(root)
    findings = []
    tickets_dir = root / TICKETS_REL
    if not tickets_dir.is_dir():
        return findings
    for md_file in sorted(tickets_dir.glob("*.md")):
        rel = str(md_file.relative_to(root))
        try:
            text = md_file.read_text(encoding="utf-8")
        except OSError:
            continue
        front = _frontmatter(text)
        if front is None:
            continue
        role = front.get("role", "")
        if role not in IMPLEMENTER_ROLES:
            continue
        allowed_paths = front.get("allowed_paths", [])
        if not isinstance(allowed_paths, list):
            continue
        for pattern in allowed_paths:
            if isinstance(pattern, str) and _is_under_acceptance(pattern):
                findings.append({
                    "code": "IMPLEMENTER_COVERS_ACCEPTANCE",
                    "path": rel,
                    "id": str(front.get("id", "")),
                    "pattern": pattern,
                    "message": f"{rel}: implementer allowed_paths pattern '{pattern}' covers tests/acceptance/"
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
