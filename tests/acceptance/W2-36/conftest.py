"""Fixtures for the W2-36 acceptance tests (``gov discover``).

P and P with a change are built once per session; a run whose outcome several cases only read (the first discovery,
the generation of S4, the research run of S5, the feature ticket of S6) runs once per session in its own copy. A case
that writes works in its own copy (a temporary folder, never this repository).
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import w2_36_support as support  # noqa: E402


def _built(make):
    """``make()``, or the case fails with the fixture's own message (a fixture error, never the feature's)."""
    try:
        return make()
    except (AssertionError, OSError, subprocess.SubprocessError, ValueError) as exc:
        message = f"{support.FIXTURE_FAILED}: {type(exc).__name__}: {exc}"
    pytest.fail(message, pytrace=False)


@pytest.fixture(scope="session")
def home(tmp_path_factory):
    """A fake HOME shared by the session's runs (it holds no memory store)."""
    return tmp_path_factory.mktemp("w2-36-home")


@pytest.fixture(scope="session")
def project_p(tmp_path_factory):
    """P, committed. Never changed."""
    return _built(lambda: support.build_project(tmp_path_factory.mktemp("w2-36-p")))


@pytest.fixture(scope="session")
def project_c(project_p, tmp_path_factory, home):
    """P with the change and a passing spec, committed. Never changed."""
    return _built(lambda: support.build_with_change(project_p, tmp_path_factory.mktemp("w2-36-c"), home))


@pytest.fixture()
def own_p(project_p, tmp_path):
    return _built(lambda: support.copy_project(project_p, tmp_path))


@pytest.fixture()
def own_c(project_c, tmp_path):
    return _built(lambda: support.copy_project(project_c, tmp_path))


@dataclass
class Outcome:
    project: Path
    run: object
    tickets_before: list
    new_tickets: list
    porcelain_before: list
    porcelain_after: list
    extra: dict = field(default_factory=dict)


def _discovered(project_p, base, home, args):
    project = _built(lambda: support.copy_project(project_p, base))
    tickets_before, porcelain_before = support.tickets(project), support.porcelain(project)
    run = support.discover(project, *args, home=home)
    new = sorted(set(support.tickets(project)) - set(tickets_before))
    return Outcome(project, run, tickets_before, new, porcelain_before, support.porcelain(project))


@pytest.fixture(scope="session")
def discovered(project_p, tmp_path_factory, home):
    """S1: ``gov discover "add CSV export to the report page" --json`` in a copy of P."""
    return _discovered(project_p, tmp_path_factory.mktemp("w2-36-discovered"), home, (support.WORDS, "--json"))


@pytest.fixture(scope="session")
def discovered_plain(project_p, tmp_path_factory, home):
    """S7: ``gov discover how could we add CSV export to the report page? --json`` in a fresh copy of P."""
    return _discovered(project_p, tmp_path_factory.mktemp("w2-36-plain"), home, (*support.PLAIN_WORDS, "--json"))


@pytest.fixture(scope="session")
def researched(project_p, tmp_path_factory, home):
    """S5 (and S2's STANDARD run): ``gov discover "<words>" --profile STANDARD --type performance-capacity``, then
    ``gov discover --generate <change>``, each with no API key and the proxies on a closed port, in a copy of P."""
    project = _built(lambda: support.copy_project(project_p, tmp_path_factory.mktemp("w2-36-researched")))
    before = support.tickets(project)
    run = support.discover(project, support.WORDS, "--profile", "STANDARD", "--type", "performance-capacity",
                           home=home, no_network=True)
    after_discovery = support.tickets(project)
    extra = {"discovery_new": sorted(set(after_discovery) - set(before))}
    for name in ("spec.md", "proposal.md"):
        path = project / support.CHANGE_REL / name
        extra[name] = path.read_text(encoding="utf-8") if path.is_file() else None
    extra["generate"] = support.discover(project, "--generate", support.CHANGE, home=home, no_network=True)
    extra["generate_new"] = sorted(set(support.tickets(project)) - set(after_discovery))
    return Outcome(project, run, before, extra["discovery_new"], [], support.porcelain(project), extra)


@pytest.fixture(scope="session")
def generated(project_p, tmp_path_factory, home):
    """S4: the planted change with gaps, ``gov discover --generate <change> --json``, ``gov readiness
    --specification <id> --json``, then ``--generate`` again, in a copy of P."""
    project = _built(lambda: support.copy_project(project_p, tmp_path_factory.mktemp("w2-36-generated")))
    _built(lambda: support.plant_gaps(project))
    record = project / support.GAPS_CHANGE_REL / "readiness.yaml"
    before, record_before = support.tickets(project), record.read_text(encoding="utf-8")
    porcelain_before = support.porcelain(project)
    run = support.discover(project, "--generate", support.GAPS_CHANGE, "--json", home=home)
    new = sorted(set(support.tickets(project)) - set(before))
    extra = {"record_before": record_before, "record_after": record.read_text(encoding="utf-8"),
             "readiness": support.gov(project, "readiness", "--specification", support.GAPS_SPEC_ID, "--json",
                                      home=home),
             "snapshot_first": support.snapshot(project)}
    extra["second"] = support.discover(project, "--generate", support.GAPS_CHANGE, "--json", home=home)
    extra["snapshot_second"] = support.snapshot(project)
    return Outcome(project, run, before, new, porcelain_before, support.porcelain(project), extra)


@pytest.fixture(scope="session")
def ticketed(project_c, tmp_path_factory, home):
    """S6: ``gov discover --ticket <change> --paths 'src/report/**' --paths 'tests/unit/report/**' --json`` in a copy
    of P with the passing spec."""
    project = _built(lambda: support.copy_project(project_c, tmp_path_factory.mktemp("w2-36-ticketed")))
    before, porcelain_before = support.tickets(project), support.porcelain(project)
    run = support.discover(project, "--ticket", support.CHANGE, "--paths", "src/report/**", "--paths",
                           "tests/unit/report/**", "--json", home=home)
    new = sorted(set(support.tickets(project)) - set(before))
    return Outcome(project, run, before, new, porcelain_before, support.porcelain(project))
