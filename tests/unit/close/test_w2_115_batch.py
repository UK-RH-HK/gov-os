"""W2-115 S6 and F3: a batch's culprit found before anything lands, by building the merged result without each
candidate."""
from __future__ import annotations

import pytest

from gov.cli.errors import GovError
from gov.close import attribution, batch

from .test_w2_115_support import OWN_SUITE, project

BROKEN_FEATURE = "from pkg.core import add\n\n\ndef twice(x):\n    return add(x, x) + 1\n"


def _branch(repo, name, planted, base="main"):
    repo.git("checkout", "-q", "-b", name, base)
    repo.commit(f"candidate {name}", f"Task: {name}", files=planted)
    repo.git("checkout", "-q", "main")


def _three(tmp_path, b_files=None):
    repo = project(tmp_path)
    base = repo.git("rev-parse", "HEAD").strip()
    _branch(repo, "a", {"src/pkg/other.py": "def other():\n    return 1  # a\n"})
    _branch(repo, "b", b_files or {"src/pkg/feature.py": BROKEN_FEATURE})
    _branch(repo, "c", {"docs/c.md": "# c\n"})
    return repo, base


def test_s6_only_the_culprit_goes_back_the_rest_land_on_the_same_run(tmp_path, monkeypatch):
    repo, base = _three(tmp_path)
    events = []
    real_alone, real_git = attribution.run_alone, batch._git
    monkeypatch.setattr(attribution, "run_alone", lambda c, t, o, f, to, tag: events.append(("run", tag)) or
                        real_alone(c, t, o, f, to, tag))
    monkeypatch.setattr(batch, "_git", lambda root, *a, **k: events.append(("git", a[0])) or real_git(root, *a, **k))
    result, code = batch.isolate(repo.root, base, ["a", "b", "c"], targets=[OWN_SUITE, "tests/unit/"], onto="main",
                                 timeout=120)
    assert code == batch.EXIT_CULPRITS
    assert result["culprits"] == ["b"] and result["landed"] == ["a", "c"]
    assert result["explains"] == {f"{OWN_SUITE}test_w_1.py::test_twice": ["b"]}
    head = repo.git("rev-parse", "main").strip()
    assert head == result["land_commit"]
    assert "# a" in repo.git("show", "main:src/pkg/other.py")
    assert repo.git("show", "main:docs/c.md") == "# c\n"
    assert repo.git("show", "main:src/pkg/feature.py") != BROKEN_FEATURE  # the culprit did not land
    lands = [n for n, e in enumerate(events) if e in (("git", "merge"), ("git", "update-ref"))]
    withouts = [n for n, e in enumerate(events) if e[0] == "run" and e[1].startswith("without")]
    assert lands and withouts and min(lands) > max(withouts)  # nothing landed before every candidate was judged
    # the build without the culprit was run green: the rest's run
    assert all(r["failed"] == 0 and r["errors"] == 0 for r in result["rest_runs"])


def test_s6_a_green_batch_lands_whole(tmp_path):
    repo, base = _three(tmp_path, b_files={"docs/b.md": "# b\n"})
    result, code = batch.isolate(repo.root, base, ["a", "b", "c"], targets=[OWN_SUITE], onto="main", timeout=120)
    assert code == 0 and result["culprits"] == [] and result["landed"] == ["a", "b", "c"]
    assert repo.git("rev-parse", "main").strip() == result["land_commit"]


def test_f3_a_red_no_single_candidate_explains_refuses_and_nothing_lands(tmp_path):
    repo = project(tmp_path, extra={f"{OWN_SUITE}test_old.py": "def test_old():\n    assert 1 == 2\n"})
    base = repo.git("rev-parse", "HEAD").strip()
    _branch(repo, "a", {"src/pkg/other.py": "def other():\n    return 1  # a\n"})
    _branch(repo, "b", {"docs/b.md": "# b\n"})
    with pytest.raises(GovError) as raised:
        batch.isolate(repo.root, base, ["a", "b"], targets=[OWN_SUITE], onto="main", timeout=120)
    assert raised.value.code == batch.BATCH_UNEXPLAINED
    assert repo.git("rev-parse", "main").strip() == base


def test_s6_a_candidate_that_cannot_be_isolated_refuses(tmp_path, monkeypatch):
    repo, base = _three(tmp_path)
    real = batch._build
    monkeypatch.setattr(batch, "_build", lambda clone, b, merged: None if len(merged) == 2 and "a" not in [
        m["name"] for m in merged] else real(clone, b, merged))
    with pytest.raises(GovError) as raised:
        batch.isolate(repo.root, base, ["a", "b", "c"], targets=[OWN_SUITE], onto="main", timeout=120)
    assert raised.value.code == batch.CANDIDATE_NOT_ISOLATED and raised.value.details["candidate"] == "a"
    assert repo.git("rev-parse", "main").strip() == base


def test_s6_candidates_that_do_not_merge_together_refuse(tmp_path):
    repo = project(tmp_path)
    base = repo.git("rev-parse", "HEAD").strip()
    _branch(repo, "a", {"src/pkg/other.py": "def other():\n    return 'a'\n"})
    _branch(repo, "b", {"src/pkg/other.py": "def other():\n    return 'b'\n"})
    with pytest.raises(GovError) as raised:
        batch.isolate(repo.root, base, ["a", "b"], targets=[OWN_SUITE], onto="main", timeout=120)
    assert raised.value.code == batch.CANDIDATE_NOT_ISOLATED and raised.value.details["candidate"] == "b"
    assert repo.git("rev-parse", "main").strip() == base


def test_s6_the_without_build_is_a_fresh_merge_never_a_revert(tmp_path, monkeypatch):
    repo, base = _three(tmp_path)
    merged = []
    real = batch._build
    monkeypatch.setattr(batch, "_build", lambda clone, b, m: merged.append(sorted(c["name"] for c in m)) or real(
        clone, b, m))
    batch.isolate(repo.root, base, ["a", "b", "c"], targets=[OWN_SUITE], timeout=120)
    assert merged[:4] == [["a", "b", "c"], ["b", "c"], ["a", "c"], ["a", "b"]]
    log = attribution._git(repo.root / attribution.CLONE_REL, "log", "--all", "--format=%s").stdout
    assert "Revert" not in log
