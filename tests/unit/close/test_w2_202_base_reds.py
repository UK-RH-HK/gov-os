"""W2-202 A1 (DEC-1214 L2, Q-CLOSE): ``batch.isolate`` runs a red no candidate explains once at the base; red there
with the same failure type it is a known base red (named, not blocking), else the batch is refused as before. And
the runs a caller adds to the batch's (``also``: the queue's acceptance runs) are judged by the same search."""
from __future__ import annotations

import pytest

from gov.cli.errors import GovError
from gov.close import attribution, batch

from .test_w2_115_support import OWN_SUITE, OWN_TEST, project

OLD = "tests/unit/test_old.py"
OLD_NODE = f"{OLD}::test_old"
BROKEN_FEATURE = "from pkg.core import add\n\n\ndef twice(x):\n    return add(x, x) + 1\n"


def _branch(repo, name, planted):
    repo.git("checkout", "-q", "-b", name, "main")
    repo.commit(f"candidate {name}", f"Task: {name}", files=planted)
    repo.git("checkout", "-q", "main")


def _tags(monkeypatch):
    """The tags of the alone runs, in order."""
    tags, real = [], attribution.run_alone
    monkeypatch.setattr(attribution, "run_alone", lambda c, t, o, f, to, tag: tags.append(tag) or
                        real(c, t, o, f, to, tag))
    return tags


def test_a_base_red_is_named_with_its_type_and_the_base_and_run_once_there(tmp_path, monkeypatch):
    repo = project(tmp_path, extra={OLD: "def test_old():\n    assert 1 == 2\n"})
    base = repo.git("rev-parse", "HEAD").strip()
    _branch(repo, "a", {"src/pkg/other.py": "def other():\n    return 1  # a\n"})
    tags = _tags(monkeypatch)
    result, code = batch.isolate(repo.root, base, ["a"], targets=[OLD], onto="main", timeout=120)
    assert code == 0 and result["landed"] == ["a"] and result["culprits"] == []
    assert result["base_reds"] == [{"test": OLD_NODE, "failure_type": "AssertionError", "base": base}]
    assert result["reds"] == [OLD_NODE]
    # one candidate: the merged result without it is the base, so that run is the base's
    assert tags == ["batch", "without-a"]
    assert "rest_runs" not in result  # nothing was left out: the batch's run is the landed one's


def test_a_red_green_at_the_base_that_no_single_candidate_explains_is_refused_after_one_run_there(tmp_path,
                                                                                                 monkeypatch):
    both = "from pkg.lonely import VALUE\nfrom pkg.other import other\n\n\ndef test_both():\n" \
           "    assert other() == 1 and VALUE == 1\n"
    repo = project(tmp_path, extra={"tests/unit/test_both.py": both})
    base = repo.git("rev-parse", "HEAD").strip()
    _branch(repo, "a", {"src/pkg/other.py": "def other():\n    return 2\n"})
    _branch(repo, "b", {"src/pkg/lonely.py": "VALUE = 2\n"})
    tags = _tags(monkeypatch)
    with pytest.raises(GovError) as raised:
        batch.isolate(repo.root, base, ["a", "b"], targets=["tests/unit/test_both.py"], onto="main", timeout=120)
    assert raised.value.code == batch.BATCH_UNEXPLAINED and raised.value.exit_code == batch.EXIT_RED
    assert raised.value.details["base_reds"] == []
    assert tags == ["batch", "without-a", "without-b", "base"]
    assert repo.git("rev-parse", "main").strip() == base


def test_a_red_at_the_base_that_fails_another_way_in_the_batch_is_not_a_base_red(tmp_path):
    repo = project(tmp_path, extra={OLD: "from pkg.other import other\n\n\ndef test_old():\n"
                                         "    assert other() == 2\n"})
    base = repo.git("rev-parse", "HEAD").strip()
    _branch(repo, "a", {"src/pkg/other.py": "def other():\n    raise ValueError('changed')\n"})
    with pytest.raises(GovError) as raised:
        batch.isolate(repo.root, base, ["a"], targets=[OLD], onto="main", timeout=120)
    assert raised.value.code == batch.BATCH_UNEXPLAINED
    assert raised.value.details["base_reds"] == []
    assert repo.git("rev-parse", "main").strip() == base


def test_a_culprit_beside_a_base_red_goes_back_and_the_rest_lands_with_the_base_red(tmp_path):
    repo = project(tmp_path, extra={OLD: "def test_old():\n    assert 1 == 2\n"})
    base = repo.git("rev-parse", "HEAD").strip()
    _branch(repo, "a", {"docs/a.md": "# a\n"})
    _branch(repo, "b", {"src/pkg/feature.py": BROKEN_FEATURE})
    result, code = batch.isolate(repo.root, base, ["a", "b"], targets=[OWN_SUITE, OLD], onto="main", timeout=120)
    assert code == batch.EXIT_CULPRITS and result["culprits"] == ["b"] and result["landed"] == ["a"]
    assert [r["test"] for r in result["base_reds"]] == [OLD_NODE]
    assert result["explains"] == {f"{OWN_TEST}::test_twice": ["b"], OLD_NODE: []}
    assert sum(r["failed"] for r in result["rest_runs"]) == 1  # the base red, still red without the culprit
    assert repo.git("rev-parse", "main").strip() == result["land_commit"]
    assert repo.git("show", "main:src/pkg/feature.py") != BROKEN_FEATURE


def test_the_reds_of_the_caller_s_own_runs_are_judged_by_the_same_search(tmp_path):
    repo = project(tmp_path)
    base = repo.git("rev-parse", "HEAD").strip()
    _branch(repo, "a", {"docs/a.md": "# a\n"})
    _branch(repo, "b", {"src/pkg/feature.py": BROKEN_FEATURE})
    calls = []

    def also(commit, names):
        calls.append(list(names))
        red = "b" in names  # the merged result that holds b holds the broken feature
        return {"runs": [{"name": "extra", "passed": int(not red), "failed": int(red), "errors": 0, "skipped": 0}],
                "failing": [{"test": f"{OWN_TEST}::test_twice", "failure_type": "AssertionError"}] if red else []}

    result, code = batch.isolate(repo.root, base, ["a", "b"], targets=[], onto="main", timeout=120, also=also)
    assert code == batch.EXIT_CULPRITS and result["culprits"] == ["b"] and result["landed"] == ["a"]
    assert calls == [["a", "b"], ["a"]]
    assert result["selection"]["suites"] == []  # an empty selection beside the caller's runs is run as it is
    assert [r["name"] for r in result["runs"]][-1] == "extra" and result["runs"][-1]["failed"] == 1
    assert [r["name"] for r in result["rest_runs"]][-1] == "extra" and result["rest_runs"][-1]["passed"] == 1
    assert repo.git("rev-parse", "main").strip() == result["land_commit"]
