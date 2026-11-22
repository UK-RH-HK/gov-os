"""Shared fixtures of W2-209's acceptance tests (README, "How the suite runs").

- ``base``: the planted source (``w2_209_support.build_base``), built once per process and copied by each case.
- ``machine_untouched`` (every test): the machine's own ``~/.local/bin/gov`` link, ``repin.json`` and ``rollback.sh``
  are read before and after each test; a change that names this run's temporary folder (a planted pin, home or
  release reached the real home) fails the test. Every call of the code under test runs with a scratch ``HOME``, so
  this is a backstop, never the way a case is kept apart; a real re-pin made by the CTO meanwhile names no planted
  folder and fails nothing.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

import w2_209_support as support


@pytest.fixture(scope="session")
def base(tmp_path_factory):
    folder = tmp_path_factory.mktemp("w2-209-base")
    home = folder / "builder-home"
    (home / "tmp").mkdir(parents=True)
    return support.build_base(folder / "source", home)


def _machine():
    home = Path(os.path.expanduser("~"))
    link = home / ".local" / "bin" / "gov"
    share = home / ".local" / "share" / "gov-os"

    def read(path):
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""
    return {"link": os.path.realpath(link) if os.path.lexists(link) else "",
            "repin": read(share / "repin.json"), "rollback": read(share / "rollback.sh")}


@pytest.fixture(autouse=True)
def machine_untouched(tmp_path_factory):
    planted = str(tmp_path_factory.getbasetemp().resolve().parent)
    before = _machine()
    yield
    after = _machine()
    reached = [key for key in after if after[key] != before[key] and planted in after[key]]
    assert not reached, f"a planted pin or home reached the machine's own {reached}: {before} -> {after}"


@pytest.fixture
def home(tmp_path, base):
    """A scratch ``$HOME`` with the live pin of 0.1.1 and its link."""
    return support.make_home(tmp_path / "home", base.n_version_commit)
