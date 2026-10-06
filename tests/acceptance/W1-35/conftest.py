"""Fixtures for the W1-35 acceptance tests (method skills and check declaration)."""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import pytest
import yaml

_HERE = Path(__file__).resolve().parent
REPO_ROOT = _HERE.parents[2]

for _name in ("W1-07",):
    _folder = str(_HERE.parent / _name)
    if _folder not in sys.path:
        sys.path.insert(0, _folder)

import w1_07_support as cli_support  # noqa: E402

RESERVED_COMMANDS = cli_support.RESERVED_COMMANDS

SKILLS_BASE = REPO_ROOT / "template" / "governance" / "kernel" / "skills"
CHECKS_DIR = REPO_ROOT / "template" / "governance" / "kernel" / "checks"

SKILL_NAMES = ("discovery", "planning", "test-design", "change")
SKILL_PATHS = {name: SKILLS_BASE / name / "SKILL.md" for name in SKILL_NAMES}

FRONTMATTER_REQUIRED = ("name", "version", "description")

PERMISSION_PATTERNS = [
    re.compile(r"\b(?:is\s+)?(?:allowed|permitted|granted)\s+to\b", re.IGNORECASE),
    re.compile(r"\b(?:may|can|shall)\s+(?:write|access|read|modify|delete|create|install)\b", re.IGNORECASE),
    re.compile(r"\bgrants?\s+(?:permission|access|authority)\b", re.IGNORECASE),
    re.compile(r"\bhas\s+(?:permission|authority)\s+to\b", re.IGNORECASE),
]

CITATION_PATTERN = re.compile(r"(?:CAP-\d+|DEC-\d+|MR-\d+)")

MAX_DESC_TOKENS = 60
MAX_BODY_TOKENS = 2500


def token_count(text: str) -> int:
    return math.ceil(len(text) / 4)


def parse_skill(path: Path) -> tuple[dict | None, str]:
    if not path.is_file():
        return None, ""
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text
    try:
        end = lines.index("---", 1)
    except ValueError:
        return None, text
    try:
        front = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError:
        return None, text
    body = "\n".join(lines[end + 1:])
    return (front if isinstance(front, dict) else None), body


def all_skill_texts() -> dict[str, tuple[dict | None, str, str]]:
    result = {}
    for name, path in SKILL_PATHS.items():
        front, body = parse_skill(path)
        full_text = path.read_text(encoding="utf-8") if path.is_file() else ""
        result[name] = (front, body, full_text)
    return result


def find_check_declaration() -> Path | None:
    for p in sorted(CHECKS_DIR.glob("skill-regression-a*.yaml")):
        return p
    return None


@pytest.fixture(scope="session")
def skills_exist():
    missing = [name for name, path in SKILL_PATHS.items() if not path.is_file()]
    if missing:
        pytest.fail(
            f"Skill files not yet created: {', '.join(missing)}. "
            "W1-35 implementation must create them first.",
            pytrace=False,
        )


@pytest.fixture(scope="session")
def skill_texts(skills_exist):
    return all_skill_texts()


@pytest.fixture(scope="session")
def check_decl_path():
    return find_check_declaration()
