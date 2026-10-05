"""Fixtures for the W1-14 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_14_support as support  # noqa: E402


@pytest.fixture(scope="session")
def driver(tmp_path_factory):
    return support.Driver(tmp_path_factory.mktemp("w1-14-driver"))


@pytest.fixture(scope="session")
def built(tmp_path_factory, driver):
    """The bridge exists. Until then every test fails here, with the reason the README states."""
    probe = tmp_path_factory.mktemp("w1-14-built")
    outcome = driver.attempt(support.BRIDGE_MODULE, support.DERIVE_FUNCTION, probe, support.CHANGE)
    if outcome.missing is not None:
        pytest.fail(f"the bridge is not built yet: {outcome.missing} "
                    f"({support.BRIDGE_MODULE}.{support.DERIVE_FUNCTION})", pytrace=False)
    return True


@pytest.fixture()
def project(built, driver, tmp_path):
    """This test's own temporary project. The folder is named ``project``: the ticket script takes the id prefix
    from the folder name, and ``pro-xxxx`` is a ticket id of ``common.schema.json``."""
    return support.Project(tmp_path / "project", driver)
