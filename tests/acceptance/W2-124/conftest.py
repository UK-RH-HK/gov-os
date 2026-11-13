"""Fixtures of the W2-124 acceptance tests (README): planted projects, stand-in embedders, and the runs the cases share.

Each distinct run (one planted project, one embedder, one command line) is made once per module and read by every case
that needs it, so the suite stays within a few seconds a case."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = str(Path(__file__).resolve().parent)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import w2_124_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: a case that cannot run in CI")


@pytest.fixture
def box(tmp_path):
    reason = support.lacking()
    if reason:
        pytest.skip(reason)
    return support.make_box(tmp_path / "box")


class Runs:
    """The runs of the module, made on first use. ``rebuild(key, ...)`` and ``adoption(key, ...)`` return what was
    made for ``key`` (a ``Run``, and for a rebuild the embedder's count of embed requests)."""

    def __init__(self, factory):
        self.factory, self.done, self.embedders = factory, {}, []

    def _box(self, key):
        reason = support.lacking()
        if reason:
            pytest.skip(reason)
        return support.make_box(self.factory.mktemp(key.replace(" ", "-")) / "box")

    def embedder(self, mode="healthy", **more):
        stand_in = support.Embedder(mode, **more)
        self.embedders.append(stand_in)
        return stand_in

    def rebuild(self, key, *, embedder, project_options=None, args=("--json",)):
        """``gov rebuild <args>`` in a project planted with ``project_options``; ``embedder``: ``dead``, or the mode
        of a stand-in. Returns ``(run, asked, project)`` where ``asked`` is the stand-in's count of embed requests."""
        if key not in self.done:
            box = self._box(key)
            project = support.plant(box, "project", **(project_options or {}))
            stand_in = None if embedder == "dead" else self.embedder(*embedder if isinstance(embedder, tuple)
                                                                    else (embedder,))
            host = support.dead_host() if stand_in is None else stand_in.host
            run = support.rebuild(project, box, host, *args)
            self.done[key] = (run, None if stand_in is None else stand_in.asked, project)
        return self.done[key]

    def adoption(self, key, *, embedder):
        """A legacy project adopted from A0 to A6: ``(adoption, last run, project)``."""
        if key not in self.done:
            box = self._box(key)
            project = support.plant_legacy(box)
            stand_in = None if embedder == "dead" else self.embedder(embedder)
            adoption = support.Adoption(project, box, support.dead_host() if stand_in is None else stand_in.host)
            last = adoption.through("A6")
            self.done[key] = (adoption, last, project)
        return self.done[key]

    def close(self):
        for stand_in in self.embedders:
            stand_in.close()


@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    shared = Runs(tmp_path_factory)
    yield shared
    shared.close()
