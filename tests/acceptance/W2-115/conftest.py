"""Fixtures for W2-115's acceptance tests (the smart close)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_115_support as support  # noqa: E402


@pytest.fixture()
def sandbox(tmp_path):
    return support.cli_support.make_sandbox(tmp_path / "sandbox")


class Unowned:
    """A scoped close with two reds its change did not cause (both red on the base, the same failure type):
    a known red, and a load-sensitive one (an entry of the serial-only list with the kind ``latency``). The path
    map's bytes and time are taken before the close.

    The green base is the initial commit G (both reds already red there): one green nightly record names it, so
    the head without the change is G, an ancestor of HEAD. The nightly's newest record, red with both failures,
    names the commit after G (the green record's own, the same code), so it does not stand in for the run on G.

    Rewrite-Reason: DEC-1150 (2): the planted project needs a green base on HEAD's line under the owner's P1-K (a).
    Before, the only record was red, so no green base existed and the reds were judged against the parent of the
    ticket's oldest own commit, the fallback the owner dropped (R2-1)."""

    def __init__(self, base):
        self.sandbox = support.cli_support.make_sandbox(base / "sandbox")
        self.known = support.node_of("W2-bb", "bb_known", "test_bb_known")
        self.load_sensitive = support.node_of("W2-bb", "bb_timing", "test_bb_timing")
        told = base / "told"
        reds = {self.known.split("::")[0]: support.telling("test_bb_known", told, support.KNOWN_RED),
                self.load_sensitive.split("::")[0]: support.telling("test_bb_timing", told, support.KNOWN_RED)}
        failures = [{"test": node, "failure_type": "AssertionError", "text": "AssertionError: a known red"}
                    for node in (self.known, self.load_sensitive)]
        self.project = project = support.Smart(base / "project", told, reds=reds, nightly="green",
                                               serial=[self.load_sensitive])
        self.green_base = project.initial
        project.nightly_record = project.plant_night(project.head(), failures)
        self.known_tickets = {p.stem for p in (project.root / ".tickets").glob("*.md")}
        project.work({support.WIDGET: "# the widget, CHANGED\n"})
        project.ready(self.sandbox)
        path_map = project.root / support.PATH_MAP_REL
        self.path_map_before = (path_map.read_bytes(), path_map.stat().st_mtime_ns)
        self.files_before = {p.relative_to(project.root).as_posix() for p in project.root.rglob("*")
                             if ".git" not in p.parts}
        self.closed_head = project.head()
        self.run = project.close(self.sandbox)


@pytest.fixture(scope="session")
def unowned(tmp_path_factory):
    return Unowned(tmp_path_factory.mktemp("w2_115_unowned"))


@pytest.fixture()
def make_project(tmp_path):
    """Builds a planted project: ``make_project(close=..., reds=..., nightly=..., ...)``."""
    def make(name="project", **keys):
        return support.Smart(tmp_path / name, tmp_path / f"{name}-told", **keys)
    return make
