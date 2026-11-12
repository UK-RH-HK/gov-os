"""W2-115 S4 (a red judged against the head without the change) and S10 (the warm clone)."""
from __future__ import annotations

import json

from gov.close import attribution

from .test_w2_115_support import TICKET, change, project

FAILS = "def test_x():\n    assert 1 == 2\n"
RAISES = "def test_x():\n    raise ValueError('no')\n"


# --- the judgement, by itself -----------------------------------------------------

def test_s4_judge_same_type_without_is_not_caused():
    assert attribution.judge(["AssertionError"], ["AssertionError"])[0] is False


def test_s4_judge_green_without_is_caused():
    assert attribution.judge(["AssertionError"], [None])[0] is True


def test_s4_judge_other_type_without_is_caused():
    assert attribution.judge(["AssertionError"], ["ValueError"])[0] is True


def test_s4_judge_timeout_unknown_absent_never_match():
    for kind in (attribution.TIMEOUT, attribution.UNKNOWN, attribution.ABSENT):
        assert attribution.judge([kind], [kind])[0] is True, kind
    assert attribution.judge(["AssertionError"], [attribution.ABSENT])[0] is True
    assert attribution.judge(["AssertionError"], [])[0] is True  # no record never matches


def test_s4_judge_green_alone_is_a_flaky_candidate_not_the_changes():
    caused, _, reason = attribution.judge([None], [])
    assert caused is False and "flaky" in reason


def test_s4_judge_load_sensitive_rounds():
    assert attribution.judge(["E"] * 3, ["E"] * 3)[0] is False
    assert attribution.judge(["E"] * 3, ["E", None, None])[0] is True
    assert attribution.judge(["E", None, "E"], ["E", "E", None])[0] is False


def test_s4_failure_types():
    assert attribution.failure_type("assert 1 == 2", "") == "AssertionError"
    assert attribution.failure_type("ValueError: no", "") == "ValueError"
    assert attribution.failure_type("Failed: Timeout >1.0s", "") == attribution.TIMEOUT
    assert attribution.failure_type('failed on setup with "KeyError: 1"', "") == "KeyError"
    assert attribution.failure_type("", "x\nE       RuntimeError: boom\n") == "RuntimeError"
    assert attribution.failure_type("", "something odd") == attribution.UNKNOWN


def test_s4_load_sensitive_is_declared_in_the_tests_code(tmp_path):
    (tmp_path / "t.py").write_text("import pytest\n\n@pytest.mark.load_sensitive\ndef test_a():\n    pass\n\n"
                                   "def test_b():\n    pass\n", encoding="utf-8")
    (tmp_path / "m.py").write_text("import pytest\npytestmark = [pytest.mark.load_sensitive]\n\n"
                                   "def test_c():\n    pass\n", encoding="utf-8")
    assert attribution.load_sensitive(tmp_path, "t.py::test_a")
    assert not attribution.load_sensitive(tmp_path, "t.py::test_b")
    assert attribution.load_sensitive(tmp_path, "m.py::test_c")


# --- the attribution on a planted project ------------------------------------------

def _attribute(repo, failing_test="tests/unit/test_x.py::test_x", kind="AssertionError"):
    from gov.close.select import ticket_change
    head = repo.git("rev-parse", "HEAD").strip()
    _, base = ticket_change(repo.root, TICKET)
    clone = attribution.prepare(repo.root, head)
    tree = repo.root / clone["path"]
    failing = [{"test": failing_test, "failure_type": kind, "text": ""}]
    return attribution.attribute(repo.root, tree, head, base, failing, ["-p", "no:cacheprovider"],
                                 repo.root / ".gov-runtime/close/scoped/t/alone", 60)


def test_s4_a_red_the_head_without_the_change_has_is_not_the_changes(tmp_path):
    repo = project(tmp_path, extra={"tests/unit/test_x.py": FAILS})
    change(repo, {"src/pkg/feature.py": "from pkg.core import add\n\n\ndef twice(x):\n    return add(x, x)\n#\n"})
    reds, night = _attribute(repo)
    assert reds[0]["caused"] is False and reds[0]["failure_type"] == "AssertionError"
    assert night == {"read": False, "record": None}


def test_s4_a_red_the_head_without_the_change_has_not_is_the_changes(tmp_path):
    repo = project(tmp_path, extra={"tests/unit/test_x.py": "def test_x():\n    assert True\n"})
    change(repo, {"tests/unit/test_x.py": FAILS})
    reds, _ = _attribute(repo)
    assert reds[0]["caused"] is True


def test_s4_another_failure_type_without_is_the_changes(tmp_path):
    repo = project(tmp_path, extra={"tests/unit/test_x.py": RAISES})
    change(repo, {"tests/unit/test_x.py": FAILS})
    reds, _ = _attribute(repo)
    assert reds[0]["caused"] is True


def test_s4_a_test_the_change_added_is_the_changes(tmp_path):
    repo = project(tmp_path)
    change(repo, {"tests/unit/test_x.py": FAILS})
    reds, _ = _attribute(repo)
    assert reds[0]["caused"] is True and "absent" in reds[0]["reason"]


def test_s4_load_sensitive_gets_three_rounds_others_one(tmp_path, monkeypatch):
    marked = "import pytest\n\n@pytest.mark.load_sensitive\ndef test_x():\n    assert 1 == 2\n"
    repo = project(tmp_path, extra={"tests/unit/test_x.py": marked, "tests/unit/test_y.py": FAILS.replace("x", "y")})
    change(repo, {"src/pkg/feature.py": "from pkg.core import add\n\n\ndef twice(x):\n    return add(x, x)\n#\n"})
    calls = []
    real = attribution.run_alone
    monkeypatch.setattr(attribution, "run_alone", lambda c, t, *a, **k: calls.append(t) or real(c, t, *a, **k))
    from gov.close.select import ticket_change
    head = repo.git("rev-parse", "HEAD").strip()
    tree = repo.root / attribution.prepare(repo.root, head)["path"]
    failing = [{"test": "tests/unit/test_x.py::test_x", "failure_type": "AssertionError", "text": ""},
               {"test": "tests/unit/test_y.py::test_y", "failure_type": "AssertionError", "text": ""}]
    reds, _ = attribution.attribute(repo.root, tree, head, ticket_change(repo.root, TICKET)[1], failing, [],
                                    repo.root / ".gov-runtime/a", 60)
    assert calls.count("tests/unit/test_x.py::test_x") == 6  # three rounds each way
    assert calls.count("tests/unit/test_y.py::test_y") == 2  # one run each way
    assert [r["rounds"] for r in reds] == [3, 1]
    assert all(r["caused"] is False for r in reds)


def test_s4_the_nightly_is_read_first_and_no_baseline_clone_is_built(tmp_path, monkeypatch):
    repo = project(tmp_path, extra={"tests/unit/test_x.py": FAILS})
    base = repo.git("rev-parse", "HEAD").strip()
    night = {"head": base, "scope": "full", "verdict": "red",
             "failures": [{"test": "tests/unit/test_x.py::test_x", "class": "red",
                           "text": "E       AssertionError: assert 1 == 2"}]}
    from .test_w2_115_support import write
    write(repo, "docs/close/nightly/NR-20261112T000000Z-aaaa.json", json.dumps(night))
    repo.commit("the night's record")
    change(repo, {"src/pkg/feature.py": "from pkg.core import add\n\n\ndef twice(x):\n    return add(x, x)\n#\n"})
    # the head without the change is the night's head plus its record commit: not the same commit, so it runs
    reds, read = _attribute(repo)
    assert read == {"read": True, "record": "docs/close/nightly/NR-20261112T000000Z-aaaa.json"}
    assert reds[0]["caused"] is False
    folders = sorted(p.name for p in (repo.root / ".gov-runtime/close").iterdir())
    assert folders == ["clone", "scoped"]  # one warm clone; nothing built for the nightly baseline


def test_s4_the_nightly_of_the_head_without_the_change_stands_for_its_run(tmp_path, monkeypatch):
    repo = project(tmp_path, extra={"tests/unit/test_x.py": "def test_x():\n    assert True\n"})
    base = repo.git("rev-parse", "HEAD").strip()
    change(repo, {"tests/unit/test_x.py": FAILS})
    night = {"head": base, "scope": "full", "verdict": "red",
             "failures": [{"test": "tests/unit/test_x.py::test_x", "class": "red",
                           "text": "E       AssertionError: assert 1 == 2"}]}
    from .test_w2_115_support import write
    write(repo, "docs/close/nightly/NR-20261112T000000Z-bbbb.json", json.dumps(night))
    repo.commit("the night's record (a record, no task)")
    tags = []
    real = attribution.run_alone
    monkeypatch.setattr(attribution, "run_alone", lambda c, t, o, f, to, tag: tags.append(tag) or real(
        c, t, o, f, to, tag))
    reds, read = _attribute(repo)
    assert read["read"] is True
    assert not [t for t in tags if t.startswith("without")]  # the night stood for the run without the change
    assert reds[0]["caused"] is False and "nightly record" in reds[0]["reason"]


# --- S10: the warm clone ------------------------------------------------------------

def test_s10_second_use_reuses_the_clone_reset_with_its_stores(tmp_path):
    repo = project(tmp_path)
    first = attribution.prepare(repo.root, repo.git("rev-parse", "HEAD").strip())
    assert first == {"path": attribution.CLONE_REL, "reused": False, "replaced": None}
    clone = repo.root / attribution.CLONE_REL
    (clone / ".gov-runtime").mkdir()
    (clone / ".gov-runtime" / "store.db").write_text("a store", encoding="utf-8")
    (clone / "stray.txt").write_text("left by a run", encoding="utf-8")
    (clone / "src/pkg/core.py").write_text("changed by a run\n", encoding="utf-8")
    head = change(repo, {"src/pkg/other.py": "def other():\n    return 2\n"})
    second = attribution.prepare(repo.root, head)
    assert second == {"path": attribution.CLONE_REL, "reused": True, "replaced": None}
    assert (clone / ".gov-runtime" / "store.db").read_text(encoding="utf-8") == "a store"
    assert not (clone / "stray.txt").exists()
    assert (clone / "src/pkg/core.py").read_text(encoding="utf-8") == "def add(a, b):\n    return a + b\n"
    assert "return 2" in (clone / "src/pkg/other.py").read_text(encoding="utf-8")


def test_s10_a_clone_that_cannot_be_reset_is_replaced_and_said(tmp_path):
    repo = project(tmp_path)
    head = repo.git("rev-parse", "HEAD").strip()
    attribution.prepare(repo.root, head)
    clone = repo.root / attribution.CLONE_REL
    (clone / ".git" / "HEAD").write_text("garbage\n", encoding="utf-8")
    again = attribution.prepare(repo.root, head)
    assert again["reused"] is False and again["replaced"] and "could not be reset" in again["replaced"]
    assert (clone / "src/pkg/core.py").is_file()
