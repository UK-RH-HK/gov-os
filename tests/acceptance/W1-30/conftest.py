"""Fixtures for the W1-30 acceptance tests (``gov close``)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_30_support as support  # noqa: E402

cli_support = support.cli_support


@pytest.fixture(scope="session")
def interface():
    """The envelope fields and exit codes of ``docs/interfaces/API-0002.yaml``."""
    return cli_support.load_interface(support.REPO_ROOT)


@pytest.fixture(scope="session")
def built(tmp_path_factory):
    """``gov close`` is built. Until then every test of its behaviour fails here."""
    base = tmp_path_factory.mktemp("w1-30-built")
    project = support.Project(base / "project")
    sandbox = cli_support.make_sandbox(base / "sandbox")
    # The sandbox has its own home; the interpreter a case starts must still find the test runner and the YAML
    # reader that the interpreter running the suite finds (README, "The sandbox"). Asked of that interpreter.
    for module in ("pytest", "yaml"):
        if not support.can_import(module, sandbox):
            pytest.fail(f"the interpreter the cases start does not find {module} in the sandbox's environment, "
                        f"although the interpreter running the suite does", pytrace=False)
    run = project.gov(sandbox, support.COMMAND, "NO-SUCH-TICKET", "--json")
    if support.NOT_IMPLEMENTED in run.stdout:
        pytest.fail("gov close is not built yet: it returns NOT_IMPLEMENTED", pytrace=False)
    return True


@pytest.fixture()
def sandbox(tmp_path):
    return cli_support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def raw_project(tmp_path):
    """A minimal temporary project, whether or not ``gov close`` is built."""
    return support.Project(tmp_path / "project")


@pytest.fixture()
def project(built, tmp_path):
    """A minimal temporary project, with ``gov close`` built."""
    return support.Project(tmp_path / "project")


@pytest.fixture()
def project_with_checks(built, tmp_path):
    """Builds a minimal temporary project that declares its own checks: ``project_with_checks(check, ...)``,
    each check a ``support.declared_check``. The kernel's declarations are not copied into it."""
    def make(*checks):
        return support.Project(tmp_path / "project", checks=list(checks))
    return make

