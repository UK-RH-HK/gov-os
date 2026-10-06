"""Support code for the W1-36 acceptance tests.

W1-36 delivers four Gov OS method skills (markdown SKILL.md files) and two
check declarations (YAML).  Every test reads and parses the text; none runs
code or needs a network.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]

# ── Skill file paths (relative to REPO_ROOT) ────────────────────────
RETRIEVAL_SKILL_REL = "template/governance/kernel/skills/retrieval/SKILL.md"
AUDIT_SKILL_REL = "template/governance/kernel/skills/audit/SKILL.md"
CHECKPOINT_SKILL_REL = "template/governance/kernel/skills/checkpoint/SKILL.md"
ADOPT_SKILL_REL = "template/governance/kernel/skills/adopt/SKILL.md"

ALL_SKILL_RELS = (
    RETRIEVAL_SKILL_REL,
    AUDIT_SKILL_REL,
    CHECKPOINT_SKILL_REL,
    ADOPT_SKILL_REL,
)
SKILL_NAMES = ("retrieval", "audit", "checkpoint", "adopt")

# ── Check declaration globs (relative to REPO_ROOT) ─────────────────
CHECKS_DIR_REL = "template/governance/kernel/checks"
SKILL_REGRESSION_GLOB = "skill-regression-b*"
AUDIT_REPRO_GLOB = "audit-reproducibility*"

# ── Audit report classes (S2, DEC-088) ───────────────────────────────
AUDIT_CLASSES = (
    "OK",
    "MISSING",
    "WEAKENED",
    "CONTRADICTS",
    "UNJUSTIFIED_DROP",
    "SCOPE_CREEP",
)

# ── Token limit (S3) ────────────────────────────────────────────────
TOKEN_LIMIT = 2500

# ── Keys that belong in role files, not skill files (CAP-24.b) ──────
ROLE_ONLY_KEYS = frozenset({
    "tools", "permissions", "allowed_paths", "model_tier",
    "authority_level", "network", "permission_classes",
})

# ── Source citation pattern ──────────────────────────────────────────
SOURCE_PATTERN = re.compile(r"(DEC-\d+|CAP-\d+|MR-\d+)")

# ── Family normalisation (DEC-436, src/gov/check/runner.py) ──────────
FAMILIES_RAW = (
    "schema/invariants", "graph integrity", "index freshness",
    "retrieval regression", "authority/role limits", "mutation scope",
    "path-map compliance", "context reproducibility",
    "concurrency/claims", "adapter/model portability",
    "skill regression", "command-contract consistency",
    "secrets indexing", "recovery/rebuild",
    "fresh-agent reconstruction", "product traceability",
    "audit reproducibility",
)


def normalise_family(name: str) -> str:
    """DEC-436, src/gov/check/runner.py::_normalise_family."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


NORMALISED_FAMILIES = {normalise_family(f) for f in FAMILIES_RAW}


# ── Parsers ──────────────────────────────────────────────────────────
def parse_skill(path: Path) -> dict:
    """Parse a SKILL.md into {frontmatter, body, path}."""
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{path}: no YAML frontmatter delimiters found")
    frontmatter = yaml.safe_load(parts[1]) or {}
    body = parts[2]
    return {"frontmatter": frontmatter, "body": body, "path": path}


def parse_check(path: Path) -> dict:
    """Parse a check declaration YAML file."""
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}
    data["_path"] = path
    return data


def token_count(text: str) -> int:
    """ceil(len(text) / 4) — the project's token counter."""
    return -(-len(text) // 4)
