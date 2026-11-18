"""Fixtures for the W1-04 acceptance tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_04_support as support  # noqa: E402


@pytest.fixture(scope="session")
def schema():
    """The tool-registry schema of the kernel template, parsed."""
    directory = support.REPO_ROOT / support.SCHEMA_DIR_REL
    path = directory / support.SCHEMA_NAME
    if not path.is_file():
        found = sorted(p.name for p in directory.glob(support.SCHEMA_GLOB)) if directory.is_dir() else []
        pytest.fail(
            f"{support.SCHEMA_DIR_REL}/{support.SCHEMA_NAME} does not exist: the tool-registry schema is missing"
            + (f" (found instead: {', '.join(found)})" if found else ""),
            pytrace=False,
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        pytest.fail(f"{support.SCHEMA_DIR_REL}/{support.SCHEMA_NAME} is not JSON: {exc}", pytrace=False)
    return data
