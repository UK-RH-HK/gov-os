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
from gov.context import TOKEN_CHARS

_MAX_DESC_TOKENS = 60
_MAX_BODY_TOKENS = 2500
_REQUIRED_FIELDS = ("name", "version", "description")
_GOV_CMD_RE = re.compile(r"gov\s+(\w+)")


def _tokens(text: str) -> int:
    return math.ceil(len(text) / TOKEN_CHARS)


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


def _extract_code_text(body: str) -> list[str]:
    """Extract text from inline code spans and fenced code blocks."""
    parts: list[str] = []
    lines = body.split("\n")
    in_fence = False
    fence_content: list[str] = []
    for line in lines:
        if not in_fence and re.match(r"^```", line):
            in_fence = True
            fence_content = []
            continue
        if in_fence:
            if re.match(r"^```", line):
                in_fence = False
                parts.append("\n".join(fence_content))
            else:
                fence_content.append(line)
            continue
        for span in re.findall(r"`([^`]+)`", line):
            parts.append(span)
    return parts


def validate_file(path: Path) -> list[dict]:
    findings: list[dict] = []
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    label = str(path)
    fm, body = _parse_frontmatter(content)
    if fm is None:
        findings.append({
            "code": "SKILL_NO_FRONTMATTER",
            "message": f"no valid YAML frontmatter in {label}",
        })
        return findings

    for field in _REQUIRED_FIELDS:
        val = fm.get(field)
        if field == "version":
            if val is None or (isinstance(val, str) and not val):
                findings.append({
                    "code": "SKILL_MISSING_VERSION",
                    "message": f"version field missing or empty in {label}",
                })
            elif not isinstance(val, str):
                findings.append({
                    "code": "SKILL_INVALID_FIELD",
                    "message": f"version must be a string in {label}",
                })
        elif val is None:
            findings.append({
                "code": "SKILL_MISSING_FIELD",
                "message": f"required field '{field}' missing in {label}",
            })
        elif not isinstance(val, str) or not val:
            findings.append({
                "code": "SKILL_INVALID_FIELD",
                "message": f"field '{field}' must be a non-empty string in {label}",
            })

    desc = fm.get("description")
    if isinstance(desc, str) and _tokens(desc) > _MAX_DESC_TOKENS:
        findings.append({
            "code": "SKILL_DESCRIPTION_TOO_LONG",
            "message": (
                f"description is {_tokens(desc)} tokens "
                f"(max {_MAX_DESC_TOKENS}) in {label}"
            ),
        })

    if _tokens(body) > _MAX_BODY_TOKENS:
        findings.append({
            "code": "SKILL_BODY_TOO_LONG",
            "message": (
                f"body is {_tokens(body)} tokens "
                f"(max {_MAX_BODY_TOKENS}) in {label}"
            ),
        })

    for code_text in _extract_code_text(body):
        for match in _GOV_CMD_RE.finditer(code_text):
            cmd = match.group(1)
            if cmd not in RESERVED_COMMANDS:
                findings.append({
                    "code": "SKILL_UNKNOWN_COMMAND",
                    "message": f"unknown gov command '{cmd}' in {label}",
                })

    return findings


def _find_skill_files(folder: Path) -> list[Path]:
    return sorted(folder.rglob("SKILL.md"))


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
            result = validate_file(p)
            if result is None:
                return _unmeasured(f"cannot read file: {arg}")
            all_findings.extend(result)
        elif p.is_dir():
            files = _find_skill_files(p)
            if not files:
                return _unmeasured(f"no skill files found in {arg}")
            for f in files:
                result = validate_file(f)
                if result is None:
                    return _unmeasured(f"cannot read file: {f}")
                all_findings.extend(result)

    if all_findings:
        print(json.dumps({"findings": all_findings}))
        return 1

    print(json.dumps({"findings": []}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
