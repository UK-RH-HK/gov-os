"""Builder tests of ``gov.close.nightly`` (W2-66): the last green night and what a scoped close missed."""
from __future__ import annotations

import json

from gov.close import nightly

from .conftest import Repo


def test_the_last_green_night_is_an_earlier_green_ancestor(repo: Repo):
    first = repo.commit("one")
    second = repo.commit("two")
    folder = repo.root / "docs" / "close" / "nightly"
    folder.mkdir(parents=True)
    (folder / "NR-1.json").write_text(json.dumps({"head": first, "verdict": "green"}), encoding="utf-8")
    (folder / "NR-2.json").write_text(json.dumps({"head": second, "verdict": "red"}), encoding="utf-8")
    assert nightly._last_green(repo.root, second) == first
    assert nightly._last_green(repo.root, first) is None


def test_a_scoped_close_missed_a_test_it_left_out_or_saw_pass():
    close = {"evidence": {"failures": [{"test": "tests/acceptance/W1-a/test_a.py::test_f", "text": "x"}]}}
    assert nightly._missed_by(close, "tests/acceptance/W1-b/test_b.py::test_g")
    assert not nightly._missed_by(close, "tests/acceptance/W1-a/test_a.py::test_f")
    assert nightly._suite_of_test("tests/acceptance/W1-b/test_b.py::test_g") == "tests/acceptance/W1-b/"
