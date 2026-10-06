"""Generic skill-file validator (DEC-439, CAP-24.c / CAP-38.b).

Validates skill files (.md with YAML frontmatter) for required fields,
token limits, and gov-command references.

Usage::

    python3 -m gov.check.skill_validator <skill-folders-or-files...>
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import yaml

from gov.check.commands import RESERVED_COMMANDS

_TOKEN_CHARS = 4
_MAX_DESC_TOKENS = 60
_MAX_BODY_TOKENS = 2500
_REQUIRED_FIELDS = ("name", "version", "description")
_GOV_CMD_RE = re.compile(r"`gov\s+(\w+)`")


def _tokens(text: str) -> int:
    return math.ceil(len(text) / _TOKEN_CHARS)


def _parse_frontmatter(content: str) -> tuple[dict | None, str]:
    if not content.startswith("---"):
        return None, content
    end = content.find("\n---", 3)
    if end < 0:
        return None, content
    fm_text = content[3:end].strip()
    body = content[end + 4:].strip()
    try:
        parsed = yaml.safe_load(fm_text)
    except yaml.YAMLError:
        return None, content
    if not isinstance(parsed, dict):
        return None, content
    return parsed, body


def validate_file(path: Path) -> list[dict]:
    findings: list[dict] = []
    content = path.read_text(encoding="utf-8")

    fm, body = _parse_frontmatter(content)
    if fm is None:
        findings.append({
            "code": "SKILL_NO_FRONTMATTER",
            "message": f"no valid YAML frontmatter in {path.name}",
        })
        return findings

    for field in _REQUIRED_FIELDS:
        val = fm.get(field)
        if field == "version":
            if not val:
                findings.append({
                    "code": "SKILL_MISSING_VERSION",
                    "message": f"version field missing or empty in {path.name}",
                })
        elif val is None:
            findings.append({
                "code": "SKILL_MISSING_FIELD",
                "message": f"required field '{field}' missing in {path.name}",
            })

    desc = fm.get("description")
    if isinstance(desc, str) and _tokens(desc) > _MAX_DESC_TOKENS:
        findings.append({
            "code": "SKILL_DESCRIPTION_TOO_LONG",
            "message": (
                f"description is {_tokens(desc)} tokens "
                f"(max {_MAX_DESC_TOKENS}) in {path.name}"
            ),
        })

    if _tokens(body) > _MAX_BODY_TOKENS:
        findings.append({
            "code": "SKILL_BODY_TOO_LONG",
            "message": (
                f"body is {_tokens(body)} tokens "
                f"(max {_MAX_BODY_TOKENS}) in {path.name}"
            ),
        })

    for match in _GOV_CMD_RE.finditer(body):
        cmd = match.group(1)
        if cmd not in RESERVED_COMMANDS:
            findings.append({
                "code": "SKILL_UNKNOWN_COMMAND",
                "message": f"unknown gov command '{cmd}' in {path.name}",
            })

    return findings


def _find_skill_files(folder: Path) -> list[Path]:
    skill_md = folder / "SKILL.md"
    if skill_md.is_file():
        return [skill_md]
    candidates = []
    for md in folder.glob("*.md"):
        try:
            text = md.read_text(encoding="utf-8")
        except OSError:
            continue
        if text.startswith("---"):
            end = text.find("\n---", 3)
            if end >= 0:
                candidates.append(md)
    return candidates


def _unmeasured(reason: str) -> int:
    print(json.dumps({"unmeasured": True, "reason": reason}))
    return 1


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]

    if not args:
        return _unmeasured("no skill files or folders specified")

    all_findings: list[dict] = []

    for arg in args:
        p = Path(arg)
        if not p.exists():
            return _unmeasured(f"path does not exist: {arg}")

        if p.is_file():
            all_findings.extend(validate_file(p))
        elif p.is_dir():
            files = _find_skill_files(p)
            if not files:
                return _unmeasured(f"no skill files found in {arg}")
            for f in files:
                all_findings.extend(validate_file(f))

    if all_findings:
        print(json.dumps({"findings": all_findings}))
        return 1

    print(json.dumps({"findings": []}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
