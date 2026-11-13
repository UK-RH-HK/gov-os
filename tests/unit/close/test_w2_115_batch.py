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


def test_s6_a_candidate_built_on_another_cannot_be_isolated_and_the_code_is_printed(tmp_path, capsys):
    """eng-3: c's branch holds b's work, so the build without b still holds it: CANDIDATE_NOT_ISOLATED (not
    BATCH_UNEXPLAINED), in the JSON envelope's error and on stderr, before anything runs; nothing lands."""
    import json

    repo = project(tmp_path)
    base = repo.git("rev-parse", "HEAD").strip()
    _branch(repo, "a", {"src/pkg/other.py": "def other():\n    return 1  # a\n"})
    _branch(repo, "b", {"src/pkg/feature.py": BROKEN_FEATURE})
    _branch(repo, "c", {"docs/c.md": "# c\n"}, base="b")
    code = batch.main(["isolate", "a", "b", "c", "--base", base, "--test", OWN_SUITE, "--onto", "main",
                       "--timeout", "120", "--root", str(repo.root), "--json"])
    out = capsys.readouterr()
    envelope = json.loads(out.out)
    assert code != 0 and envelope["ok"] is False
    assert envelope["error"]["code"] == batch.CANDIDATE_NOT_ISOLATED
    assert envelope["error"]["details"]["candidate"] == "b" and envelope["error"]["details"]["shares_with"] == "c"
    assert batch.CANDIDATE_NOT_ISOLATED in out.err
    assert "runs" not in envelope["error"]["details"]  # refused before anything ran
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


# ---------------------------------------------------------------------------
# ``run`` in a scoped project: W2-68's entry point, each candidate a ticket whose work is on ``w2/<its wbs_id>``
# ---------------------------------------------------------------------------

def _tickets_three(tmp_path, b_files=None):
    from gov.tasks.tickets import frontmatter  # noqa: F401  (the close reads the tickets this way)

    from .test_w2_115_support import ticket_text

    extra = {}
    for tid, wbs in (("T-0002", "W-2"), ("T-0003", "W-3")):
        extra[f".tickets/{tid}.md"] = ticket_text(ticket=tid, wbs=wbs)
        extra[f"tests/acceptance/{wbs}/test_{wbs.lower().replace('-', '_')}.py"] = "def test_ok():\n    assert True\n"
    repo = project(tmp_path, extra=extra)
    base = repo.git("rev-parse", "HEAD").strip()
    for tid, wbs, planted in (("T-0001", "W-1", {"src/pkg/other.py": "def other():\n    return 1  # a\n"}),
                              ("T-0002", "W-2", b_files or {"src/pkg/feature.py": BROKEN_FEATURE}),
                              ("T-0003", "W-3", {"docs/c.md": "# c\n"})):
        repo.git("checkout", "-q", "-b", f"w2/{wbs}", base)
        repo.commit(f"work of {tid}", f"Task: {tid}", "Role: engineer", files=planted)
        repo.git("checkout", "-q", "main")
    return repo, base


def test_s6_run_in_a_scoped_project_sends_back_only_the_culprit_and_closes_the_rest_on_one_commit(tmp_path):
    from gov.tasks.tickets import frontmatter

    repo, base = _tickets_three(tmp_path)
    result, code = batch.run(repo.root, ["T-0001", "T-0002", "T-0003"])
    assert code == batch.EXIT_CULPRITS
    assert result["culprits"] == ["T-0002"] and result["landed"] == ["T-0001", "T-0003"]
    land = result["land_commit"]
    assert repo.git("merge-base", "--is-ancestor", land, "main") == ""
    assert repo.git("show", "main:src/pkg/feature.py") != BROKEN_FEATURE  # the culprit never landed
    commits = set()
    for tid in ("T-0001", "T-0003"):
        record = frontmatter(repo.root / f"docs/close/{tid}/CL-{tid}.md")
        assert record["close"] == "scoped" and record["culprits"] == ["T-0002"]
        assert all(record["runs"]) and all(r["failed"] == 0 for r in record["runs"])
        commits.add(record["commit"])
        assert frontmatter(repo.root / f".tickets/{tid}.md")["status"] == "closed"
    assert commits == {land}  # landed on the same run
    assert not (repo.root / "docs/close/T-0002").exists()
    assert frontmatter(repo.root / ".tickets/T-0002.md")["status"] != "closed"


def test_s6_run_a_ticket_without_its_work_branch_is_not_isolated(tmp_path):
    repo, base = _tickets_three(tmp_path)
    repo.git("branch", "-q", "-D", "w2/W-3")
    with pytest.raises(GovError) as raised:
        batch.run(repo.root, ["T-0001", "T-0003"])
    assert raised.value.code == batch.CANDIDATE_NOT_ISOLATED
    assert repo.git("rev-parse", "main").strip() == base


def test_f3_run_a_red_no_candidate_explains_lands_nothing_and_closes_nothing(tmp_path, monkeypatch):
    from gov.tasks.tickets import frontmatter

    repo, base = _tickets_three(tmp_path, b_files={"docs/b.md": "# b\n"})
    real = batch._targets
    monkeypatch.setattr(batch, "_targets", lambda clone, c, g: real(clone, c, g) if g else {
        "suites": ["tests/unit/test_red.py"], "pytest_options": real(clone, c, [OWN_SUITE])["pytest_options"]})
    repo.commit("a red on the base", files={"tests/unit/test_red.py": "def test_red():\n    assert 1 == 2\n"})
    base = repo.git("rev-parse", "HEAD").strip()
    with pytest.raises(GovError) as raised:
        batch.run(repo.root, ["T-0001", "T-0002"])
    assert raised.value.code == batch.BATCH_UNEXPLAINED
    assert repo.git("rev-parse", "main").strip() == base
    assert all(frontmatter(repo.root / f".tickets/{t}.md")["status"] != "closed" for t in ("T-0001", "T-0002"))


def test_f4_run_in_a_strict_project_is_todays(tmp_path, monkeypatch):
    repo = project(tmp_path, mode=None)
    called = []
    monkeypatch.setattr(batch, "_measure", lambda root, tickets: called.append(tickets) or (_ for _ in ()).throw(
        GovError("STOP", "today's path")))
    monkeypatch.setattr(batch, "run_scoped", lambda *a, **k: pytest.fail("the scoped batch ran in a strict project"))
    with pytest.raises(GovError) as raised:
        batch.run(repo.root, ["T-0001"])
    assert raised.value.code == "STOP" and called == [["T-0001"]]


# --- F-3 (S6, F3): a culprit whose red is its own new test -----------------------------------------------------

NEW_RED = f"{OWN_SUITE}test_a_new.py"


def test_f3_a_culprits_own_new_red_test_is_blamed_once_confirmed_alone(tmp_path, monkeypatch):
    """a adds a test that is red; b and c are clean. Without a the test is absent, so no build without a candidate
    turns it green; it is red again on the base with a alone, so a goes back and b and c land on the same run."""
    repo = project(tmp_path)
    base = repo.git("rev-parse", "HEAD").strip()
    _branch(repo, "a", {NEW_RED: "def test_new():\n    assert 1 == 2\n"})
    _branch(repo, "b", {"src/pkg/other.py": "def other():\n    return 1  # b\n"})
    _branch(repo, "c", {"docs/c.md": "# c\n"})
    events = []
    real_alone, real_git = attribution.run_alone, batch._git
    monkeypatch.setattr(attribution, "run_alone", lambda c, t, o, f, to, tag: events.append(("run", tag)) or
                        real_alone(c, t, o, f, to, tag))
    monkeypatch.setattr(batch, "_git", lambda root, *a, **k: events.append(("git", a[0])) or real_git(root, *a, **k))
    result, code = batch.isolate(repo.root, base, ["a", "b", "c"], targets=[OWN_SUITE, "tests/unit/"], onto="main",
                                 timeout=120)
    assert code == batch.EXIT_CULPRITS
    assert result["culprits"] == ["a"] and result["landed"] == ["b", "c"]
    assert result["explains"] == {f"{NEW_RED}::test_new": ["a"]}
    assert repo.git("rev-parse", "main").strip() == result["land_commit"]
    assert "# b" in repo.git("show", "main:src/pkg/other.py") and repo.git("show", "main:docs/c.md") == "# c\n"
    assert "test_a_new.py" not in repo.git("ls-tree", "-r", "--name-only", "main")  # the culprit did not land
    confirms = [n for n, e in enumerate(events) if e == ("run", "alone-a")]
    lands = [n for n, e in enumerate(events) if e in (("git", "merge"), ("git", "update-ref"))]
    assert confirms and lands and min(lands) > max(confirms)  # nothing landed before the culprit was confirmed


def test_f3_an_absent_red_not_red_with_its_candidate_alone_refuses_and_nothing_lands(tmp_path):
    """a adds a test that is red only beside b or c: absent without a, red without b, red without c, green with a
    alone: no single candidate explains it, so the batch refuses as before and nothing lands."""
    repo = project(tmp_path)
    base = repo.git("rev-parse", "HEAD").strip()
    _branch(repo, "a", {NEW_RED: "import importlib.util\n\n\ndef test_new():\n"
                                 "    assert importlib.util.find_spec('pkg.bmod') is None\n"
                                 "    assert importlib.util.find_spec('pkg.cmod') is None\n"})
    _branch(repo, "b", {"src/pkg/bmod.py": "B = 1\n"})
    _branch(repo, "c", {"src/pkg/cmod.py": "C = 1\n"})
    with pytest.raises(GovError) as raised:
        batch.isolate(repo.root, base, ["a", "b", "c"], targets=[OWN_SUITE], onto="main", timeout=120)
    assert raised.value.code == batch.BATCH_UNEXPLAINED
    assert raised.value.details["unexplained"] == [f"{NEW_RED}::test_new"]
    assert raised.value.details["explains"] == {f"{NEW_RED}::test_new": []}
    assert repo.git("rev-parse", "main").strip() == base


ADDED_RED = "tests/unit/test_a_added.py"


def test_f3_the_run_on_the_rest_leaves_out_a_culprits_own_new_test_file(tmp_path):
    """reds-6 (S6, F3): the selection names a's own new red test file by itself (not inside a suite folder). The
    rest (b and c) does not hold that file, so its run must not name it (pytest exits 4 on a missing path, and the
    batch refused RUN_INCOMPLETE): a goes back, b and c land on the same run, and the rest's run is green."""
    repo = project(tmp_path)
    base = repo.git("rev-parse", "HEAD").strip()
    _branch(repo, "a", {ADDED_RED: "def test_added():\n    assert 1 == 2\n"})
    _branch(repo, "b", {"src/pkg/other.py": "def other():\n    return 1  # b\n"})
    _branch(repo, "c", {"docs/c.md": "# c\n"})
    result, code = batch.isolate(repo.root, base, ["a", "b", "c"], targets=[OWN_SUITE, ADDED_RED], onto="main",
                                 timeout=120)
    assert code == batch.EXIT_CULPRITS
    assert result["culprits"] == ["a"] and result["landed"] == ["b", "c"]
    assert repo.git("rev-parse", "main").strip() == result["land_commit"] != base
    rest = {r["name"]: r for r in result["rest_runs"]}
    assert rest["parallel"]["passed"] >= 1 and rest["parallel"]["failed"] == 0
    assert result["selection"]["suites"] == sorted([OWN_SUITE, ADDED_RED])  # the batch's selection is unchanged
