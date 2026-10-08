"""Fixtures for the W1-31 acceptance tests (the governance share counter, ``gov telemetry``)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_31_support as support  # noqa: E402

cli_support = support.cli_support


@pytest.fixture()
def sandbox(tmp_path):
    return cli_support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def logs(tmp_path):
    """An empty folder of session logs: what ``CLAUDE_CONFIG_DIR`` names, with its ``projects/``."""
    folder = tmp_path / "claude-config"
    (folder / "projects").mkdir(parents=True)
    return folder


@pytest.fixture(scope="session")
def built(tmp_path_factory):
    """``gov telemetry`` is built. Until then every case of its behaviour fails here, with this reason."""
    base = tmp_path_factory.mktemp("w1-31-built")
    run = support.run_telemetry(base, cli_support.make_sandbox(base / "sandbox"), None, ticket="NO-SUCH-TICKET")
    if run.returncode == support.EXIT_USAGE or "invalid choice" in run.stderr:
        pytest.fail("gov telemetry is not built: there is no command module src/gov/telemetry/command.py "
                    "(the command line answers with a usage error)", pytrace=False)
    return True


@pytest.fixture(scope="session")
def ccusage():
    """The registered ccusage is on this machine; a case that joins its figures is skipped where it is not."""
    if support.ccusage_dir() is None:
        pytest.skip("ccusage is not installed on this machine (tool registry: 20.0.26 under Node v22.23.3)")
    return support.ccusage_dir()


@pytest.fixture()
def project(built, tmp_path):
    return support.Project(tmp_path / "project")


@pytest.fixture()
def make_project(built, tmp_path):
    def make(profile):
        return support.Project(tmp_path / f"project-{profile}", profile=profile)
    return make
