"""Fixtures for W1-36 acceptance tests.

Every fixture fails with a clear message when the target file does not exist,
so every dependent test shows "X does not exist" as its red reason.
"""
from __future__ import annotations

import pytest

from w1_36_support import (
    ALL_SKILL_RELS,
    AUDIT_REPRO_GLOB,
    CHECKS_DIR_REL,
    REPO_ROOT,
    SKILL_NAMES,
    SKILL_REGRESSION_GLOB,
    parse_check,
    parse_skill,
)


# ── Parametrised fixture: one run per skill ──────────────────────────
@pytest.fixture(
    params=list(zip(SKILL_NAMES, ALL_SKILL_RELS)),
    ids=list(SKILL_NAMES),
)
def skill(request):
    """Each skill file, parametrised over the four skills."""
    name, rel = request.param
    path = REPO_ROOT / rel
    if not path.is_file():
        pytest.fail(f"{name} skill does not exist: {rel}")
    result = parse_skill(path)
    result["skill_name"] = name
    return result


# ── Named fixtures for content tests ─────────────────────────────────
def _load_skill(rel: str, label: str) -> dict:
    path = REPO_ROOT / rel
    if not path.is_file():
        pytest.fail(f"{label} skill does not exist: {rel}")
    return parse_skill(path)


@pytest.fixture
def retrieval_skill():
    return _load_skill(ALL_SKILL_RELS[0], "retrieval")


@pytest.fixture
def audit_skill():
    return _load_skill(ALL_SKILL_RELS[1], "audit")


# ── Check declaration fixtures ───────────────────────────────────────
@pytest.fixture
def skill_regression_checks():
    """Skill-regression check declarations matching the glob."""
    d = REPO_ROOT / CHECKS_DIR_REL
    matches = sorted(p for p in d.glob(SKILL_REGRESSION_GLOB) if p.is_file())
    if not matches:
        pytest.fail(
            f"no skill-regression check declaration matches "
            f"{CHECKS_DIR_REL}/{SKILL_REGRESSION_GLOB}"
        )
    return [parse_check(p) for p in matches]


@pytest.fixture
def audit_repro_checks():
    """Audit-reproducibility check declarations matching the glob."""
    d = REPO_ROOT / CHECKS_DIR_REL
    matches = sorted(p for p in d.glob(AUDIT_REPRO_GLOB) if p.is_file())
    if not matches:
        pytest.fail(
            f"no audit-reproducibility check declaration matches "
            f"{CHECKS_DIR_REL}/{AUDIT_REPRO_GLOB}"
        )
    return [parse_check(p) for p in matches]
