"""Support code for the W1-36 acceptance tests.

W1-36 delivers four Gov OS method skills (markdown SKILL.md files) and two
check declarations (YAML).  Every test reads and parses the text; none runs
code or needs a network.  Integration tests (second start) also build
temporary git projects and call ``run_checks``.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
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


# ── Integration test helpers (second start) ────────────────────────────

def _tmp_git(root, *args, check=True):
    """Run git in a temporary project with deterministic, minimal config."""
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(Path(root).parent),
        "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_AUTHOR_NAME": "Fixture",
        "GIT_AUTHOR_EMAIL": "fixture@test",
        "GIT_COMMITTER_NAME": "Fixture",
        "GIT_COMMITTER_EMAIL": "fixture@test",
    }
    r = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True, text=True, env=env,
    )
    if check and r.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {root}:\n{r.stderr}")
    return r


def build_check_project(root, *, check_decls=None, skill_files=True,
                         extra_files=None):
    """Build a minimal temporary git project for ``run_checks`` integration tests.

    Copies individual named files only (never a folder).
    """
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    _tmp_git(root, "init", "-q", "-b", "main")

    if check_decls is None:
        check_decls = ["skill-regression-b1.yaml", "audit-reproducibility.yaml"]
    decl_dst = root / CHECKS_DIR_REL
    decl_dst.mkdir(parents=True, exist_ok=True)
    for name in check_decls:
        shutil.copy2(REPO_ROOT / CHECKS_DIR_REL / name, decl_dst / name)

    if skill_files:
        for rel in ALL_SKILL_RELS:
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO_ROOT / rel, dst)

    if extra_files:
        for rel_path, content in extra_files.items():
            p = root / rel_path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")

    (root / "README.md").write_text("# Test project\n", encoding="utf-8")
    _tmp_git(root, "add", "-A")
    _tmp_git(root, "commit", "-q", "-m", "initial commit")
    return root


def head_sha(root):
    """Return HEAD's full SHA in a temporary project."""
    r = _tmp_git(Path(root), "rev-parse", "HEAD")
    return r.stdout.strip()


def add_and_commit(root, message="update"):
    """Stage all changes and commit in a temporary project."""
    _tmp_git(Path(root), "add", "-A")
    _tmp_git(Path(root), "commit", "-q", "-m", message)
