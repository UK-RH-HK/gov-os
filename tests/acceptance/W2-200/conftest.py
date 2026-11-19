"""Fixtures for the W2-200 acceptance tests.

A fixture HOME per test under its ``tmp_path``; the close worlds of S3 to S7 and F1 are built and closed once per
session (each close takes a few seconds) and read by every case of their KPI line and by F1. A world is a repository
of its own under ``tmp_path_factory``; nothing is shared between two worlds.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_200_support as s  # noqa: E402


@pytest.fixture
def home(tmp_path):
    return s.make_home(tmp_path)


@pytest.fixture
def env(home):
    return s.make_env(home)


def _project(factory, name, register_text, register_rel=s.REGISTER_REL, extra_files=None, **ticket):
    base = factory.mktemp(name)
    env = s.make_env(s.make_home(base))
    failing = ticket.pop("failing", False)
    project = s.CloseProject(base, env, register_text, register_rel, extra_files)
    project.add_ticket(s.ticket_text(**ticket), failing=failing)
    return base, project


@pytest.fixture(scope="session")
def s3_world(tmp_path_factory):
    """S3: the ticket cites decisions in its sources, its decisions list and its KPI lines; closed, and its clone at
    the same commit closed too."""
    base, project = _project(tmp_path_factory, "s3", s.S3_REGISTER, sources=s.S3_SOURCES, decisions=s.S3_DECISIONS,
                             success=s.S3_SUCCESS, failure=s.S3_FAILURE)
    twin = project.clone(base)
    measured = project.head()   # the commit the close measures: HEAD before the close
    return SimpleNamespace(project=project, measured=measured, run=project.close(), twin=twin, twin_run=twin.close())


@pytest.fixture(scope="session")
def s4_world(tmp_path_factory):
    """S4: a cited decision over 1,200,000 characters and a long ticket, with no setting; the same with
    ``budgets.close_context_tokens: "abc"`` in the facts file."""
    _, big = _project(tmp_path_factory, "s4", s.S4_REGISTER, sources=s.S4_SOURCES, body=s.S4_TICKET_BODY)
    _, invalid = _project(tmp_path_factory, "s4-invalid", s.S4_REGISTER, extra_files={s.FACTS_REL: s.S4_INVALID_FACTS},
                          sources=s.S4_SOURCES, body=s.S4_TICKET_BODY)
    return SimpleNamespace(big=big, big_run=big.close(), invalid=invalid, invalid_run=invalid.close())


@pytest.fixture(scope="session")
def s5_world(tmp_path_factory):
    """S5: one cited decision in each state (standing, superseded three ways, retired, rejected, done)."""
    _, project = _project(tmp_path_factory, "s5", s.S5_REGISTER, sources=s.S5_SOURCES)
    return SimpleNamespace(project=project, run=project.close())


@pytest.fixture(scope="session")
def s6_refused(tmp_path_factory):
    """S6, first fixture: DEC-199 in the sources and DEC-198 in the decisions list, neither in the register. The
    state before the close is taken after the store is rebuilt (the store is not the close's to judge here)."""
    _, project = _project(tmp_path_factory, "s6-refused", s.PLAIN_REGISTER, sources=["DEC-110", "DEC-199"],
                          decisions=["DEC-198"])
    project.rebuild()
    before = SimpleNamespace(status=project.status(), files=s.tree_files(project.root), head=project.head(),
                             checkpoints=project.checkpoints(), iteration=project.iteration_file().exists())
    run = project.close(rebuild=False)
    unknown = project.gov("close", "NO-SUCH-TICKET", "--json")  # a refusal of the same kind, before any gate
    return SimpleNamespace(project=project, run=run, before=before, unknown=unknown)


@pytest.fixture(scope="session")
def s6_kpi_only(tmp_path_factory):
    """S6, second fixture: DEC-199 only inside a KPI line, not in the register."""
    _, project = _project(tmp_path_factory, "s6-kpi", s.PLAIN_REGISTER, sources=["DEC-110"],
                          success=[f"S1 The widget names {s.S6_KPI_ONLY} [{s.S6_KPI_ONLY}]."])
    return SimpleNamespace(project=project, run=project.close())


@pytest.fixture(scope="session")
def s6_no_register(tmp_path_factory):
    """S6, third fixture: the path map names no register (a register file stands at the usual path, unnamed)."""
    _, project = _project(tmp_path_factory, "s6-noreg", None, register_rel=None,
                          extra_files={s.REGISTER_REL: s.S6_UNNAMED_REGISTER}, sources=["DEC-110"],
                          decisions=["DEC-111"], success=["S1 The widget keeps its rule [DEC-112]."])
    return SimpleNamespace(project=project, run=project.close())


@pytest.fixture(scope="session")
def s6_no_citation(tmp_path_factory):
    """S6, fourth fixture: a ticket that cites no decision at all."""
    _, project = _project(tmp_path_factory, "s6-none", s.PLAIN_REGISTER, sources=[])
    measured = project.head()   # the commit the close measures: HEAD before the close
    return SimpleNamespace(project=project, measured=measured, run=project.close())


@pytest.fixture(scope="session")
def s7_world(tmp_path_factory):
    """S7: a close refused on a red acceptance test with ``--disposition repair``."""
    _, project = _project(tmp_path_factory, "s7", s.PLAIN_REGISTER, sources=["DEC-110"], failing=True)
    return SimpleNamespace(project=project, run=project.close("--disposition", "repair"))
