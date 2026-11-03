"""land.py under DEC-1050: G-1 (before a ticket is queued, every commit of its range that changes tests/acceptance/
carries Role: independent-test-designer or Role: owner, else the landing refuses, naming the commits) and Q-1 (no
nightly baseline: the queue traces each red once each way against the head without the batch, 3 rounds only for the
load-sensitive list). The file under test: LAND_UNDER_TEST, default land.candidate.py beside this file (land.py once
promoted). Planted repositories under tmp_path only.

    PYTHONPATH= python3 -m pytest -q -p no:cacheprovider test_land_dec1050.py
"""
import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
UNDER_TEST = Path(os.environ.get("LAND_UNDER_TEST") or HERE / "land.candidate.py")


@pytest.fixture
def land():
    spec = importlib.util.spec_from_file_location("land_under_test", UNDER_TEST)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(d, *a):
    return subprocess.run(["git", "-C", str(d), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                          capture_output=True, text=True, check=True).stdout.strip()


def commit(d, files, msg, *roles, rm=()):
    for rel, text in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    for rel in rm:
        git(d, "rm", "-q", rel)
    git(d, "add", "-A")
    git(d, "commit", "-q", "--allow-empty", "-m", msg, "--trailer", "Task: T-1",
        *[x for r in roles for x in ("--trailer", f"Role: {r}")])
    return git(d, "rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    git(r, "init", "-q", "-b", "main")
    commit(r, {"src/a.py": "A = 1\n", "tests/acceptance/W2-1/test_old.py": "def test_old():\n    pass\n"}, "root")
    git(r, "branch", "w2/integrate")
    git(r, "checkout", "-q", "-b", "w2/W2-1")
    return r


def authors(land, repo, ref="HEAD"):
    return land.acceptance_authors(git(repo, "rev-parse", ref), root=repo)


# ---- G-1: who wrote the acceptance tests --------------------------------------------------------------------------

def test_the_test_designers_and_the_owners_commits_pass_and_are_counted(land, repo):
    commit(repo, {"tests/acceptance/W2-1/test_a.py": "def test_a():\n    pass\n"}, "the tests", "independent-test-designer")
    commit(repo, {"tests/acceptance/W2-1/test_a.py": "def test_a():\n    assert 1\n"}, "an owner fix", "owner")
    commit(repo, {"src/a.py": "A = 2\n"}, "the code", "engineer")  # no test changed: not counted
    assert authors(land, repo) == ([], 2)


def test_a_ticket_without_acceptance_test_changes_has_nothing_to_check(land, repo):
    commit(repo, {"src/a.py": "A = 2\n", "tests/unit/test_u.py": "def test_u():\n    pass\n"}, "code", "engineer")
    assert authors(land, repo) == ([], 0)


@pytest.mark.parametrize("roles, shown", [(("engineer",), "engineer"), ((), "none"), (("orchestrator",), "orchestrator"),
                                          (("independent-test-designer", "engineer"), "independent-test-designer, engineer"),
                                          (("Independent-Test-Designer",), "Independent-Test-Designer")])
def test_any_other_role_is_refused_and_named(land, repo, roles, shown):
    commit(repo, {"tests/acceptance/W2-1/test_a.py": "def test_a():\n    pass\n"}, "the tests", "independent-test-designer")
    bad_c = commit(repo, {"tests/acceptance/W2-1/test_a.py": "def test_a():\n    assert True\n"}, "a builder edit", *roles)
    bad, n = authors(land, repo)
    assert n == 2 and bad == [f"{bad_c[:12]} (Role: {shown}) a builder edit"]


def test_a_deletion_or_a_rename_out_of_the_folder_counts(land, repo):
    gone = commit(repo, {}, "a deleted test", "engineer", rm=["tests/acceptance/W2-1/test_old.py"])
    bad, n = authors(land, repo)
    assert n == 1 and bad[0].startswith(gone[:12])


def test_commits_already_on_the_integration_branch_are_not_this_tickets(land, repo):
    git(repo, "checkout", "-q", "w2/integrate")
    commit(repo, {"tests/acceptance/W2-9/test_z.py": "def test_z():\n    pass\n"}, "an older landing", "engineer")
    git(repo, "checkout", "-q", "w2/W2-1")
    git(repo, "merge", "-q", "--no-edit", "w2/integrate")  # the lead brings the branch up to date
    commit(repo, {"src/a.py": "A = 3\n"}, "the code", "engineer")
    assert authors(land, repo) == ([], 0)


def test_a_clean_merge_of_the_designers_branch_passes(land, repo):
    git(repo, "checkout", "-q", "-b", "tests")
    commit(repo, {"tests/acceptance/W2-1/test_a.py": "def test_a():\n    pass\n"}, "the tests", "independent-test-designer")
    git(repo, "checkout", "-q", "w2/W2-1")
    commit(repo, {"src/a.py": "A = 2\n"}, "the code", "engineer")
    git(repo, "merge", "-q", "--no-ff", "-m", "Merge the tests branch", "-m", "Role: orchestrator", "tests")
    assert authors(land, repo) == ([], 1)


def test_an_edit_made_in_a_merge_is_refused(land, repo):
    git(repo, "checkout", "-q", "-b", "tests")
    commit(repo, {"tests/acceptance/W2-1/test_a.py": "def test_a():\n    pass\n"}, "the tests", "independent-test-designer")
    git(repo, "checkout", "-q", "w2/W2-1")
    commit(repo, {"src/a.py": "A = 2\n"}, "the code", "engineer")
    git(repo, "merge", "-q", "--no-ff", "--no-commit", "tests")
    (repo / "tests/acceptance/W2-1/test_a.py").write_text("def test_a():\n    assert 'weakened'\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "Merge the tests branch", "--trailer", "Role: orchestrator")
    merge = git(repo, "rev-parse", "HEAD")
    bad, n = authors(land, repo)
    assert n == 2 and bad == [f"{merge[:12]} (Role: orchestrator) Merge the tests branch"]


def test_a_range_git_cannot_read_fails_closed(land, repo):
    bad, n = land.acceptance_authors("0" * 40, root=repo)
    assert n == 0 and len(bad) == 1 and bad[0].startswith("the commits could not be read")


def test_the_precheck_refuses_naming_the_commits(land, repo, monkeypatch):
    bad_c = commit(repo, {"tests/acceptance/W2-1/test_a.py": "x = 1\n"}, "a builder writes a test", "engineer")
    monkeypatch.setattr(land, "ROOT", repo)
    land.SCAN = False
    bad, _ = land.precheck("W2-1", "DAEO-x", "STANDARD", bad_c)
    assert len(bad) == 1 and "W2-1: commits that change tests/acceptance/ without Role: independent-test-designer" in bad[0]
    assert f"{bad_c[:12]} (Role: engineer) a builder writes a test" in bad[0] and "G-1, DEC-1050" in bad[0]


# ---- main: refused before anything is queued; Q-1's queue run ------------------------------------------------------

@pytest.fixture
def main_env(land, tmp_path, monkeypatch):
    root = tmp_path / "root"
    (root / "governance/project").mkdir(parents=True)
    (root / "governance/project/secrets.yaml").write_text("scan: off\n")
    ls = tmp_path / "load_sensitive.txt"
    ls.write_text("# none\n")
    calls = []

    def fake(cmd, **kw):
        calls.append([str(c) for c in cmd])
        return SimpleNamespace(returncode=0, stdout="", stderr="")
    monkeypatch.setattr(land, "ROOT", root)
    monkeypatch.setattr(land, "QUEUE", tmp_path / "q")
    monkeypatch.setattr(land, "LOAD_SENSITIVE", ls)
    monkeypatch.setattr(land, "sh", fake)
    monkeypatch.setattr(land, "subprocess", SimpleNamespace(run=fake))
    monkeypatch.setattr(land, "git", lambda *a: "c" * 40)
    monkeypatch.setattr(land, "ticket_of", lambda w2: ("DAEO-x", "STANDARD"))
    return SimpleNamespace(calls=calls, ls=ls)


def test_a_g1_refusal_queues_nothing(land, main_env, monkeypatch, capsys):
    monkeypatch.setattr(land, "precheck", lambda *a: (["W2-1: commits that change tests/acceptance/ ... (G-1)"], "r"))
    monkeypatch.setattr(sys, "argv", ["land.py", "W2-1"])
    with pytest.raises(SystemExit) as e:
        land.main()
    assert e.value.code == 2 and "REFUSED before anything was queued" in capsys.readouterr().out
    assert not [c for c in main_env.calls if "enqueue" in c or "run" in c]


def test_the_queue_runs_without_a_baseline_once_each_way_with_the_list(land, main_env, monkeypatch, capsys):
    monkeypatch.setattr(land, "precheck", lambda *a: ([], "r"))
    monkeypatch.setattr(sys, "argv", ["land.py", "W2-1", "--base", "9d605eba20a2"])
    with pytest.raises(SystemExit) as e:
        land.main()
    out = capsys.readouterr().out
    assert e.value.code == 0, out
    assert "--base 9d605eba20a2 not used" in out and "the head without the batch, once each way" in out
    runs = [c for c in main_env.calls if "run" in c[2:4]]
    assert len(runs) == 1
    r = runs[0]
    assert "--base" not in r and "--base-results" not in r and "--base-run" not in r
    assert r[r.index("--rounds") + 1] == "1" and r[r.index("--load-sensitive") + 1] == str(main_env.ls)
    assert "--integration-store" in r


def test_a_missing_load_sensitive_list_refuses(land, main_env, monkeypatch, capsys):
    main_env.ls.unlink()
    monkeypatch.setattr(land, "precheck", lambda *a: ([], "r"))
    monkeypatch.setattr(sys, "argv", ["land.py", "W2-1"])
    with pytest.raises(SystemExit) as e:
        land.main()
    assert e.value.code == 2 and "no load-sensitive list" in capsys.readouterr().out


def test_the_close_record_names_the_trace_and_the_test_authors(land):
    rec = {"base": "c" * 40, "head": "d" * 40, "trace_base": "c" * 40, "unowned": ["tests/x.py::t"]}
    landed = {"commit": "a" * 40, "merge": "b" * 40, "record": "r"}
    text = land.close_record("W2-1", "DAEO-x", "STANDARD", landed, rec, "r", land.BASE_WHY, 3)
    assert "the head without the batch, once each way" in text and "Red on the head without the batch too" in text
    assert "- Acceptance tests' authors (G-1, DEC-1050): 3 commit(s) changing tests/acceptance/" in text
    assert "no commit changes tests/acceptance/" in land.close_record("W2-1", "DAEO-x", "LITE", landed, rec, "r")


def test_the_cto_load_sensitive_list_reads_as_the_queue_reads_it():
    lines = (HERE / "load_sensitive.txt").read_text(encoding="utf-8").splitlines()
    ids = [x.strip() for x in lines if x.strip() and not x.strip().startswith("#")]
    assert ids and all(i.startswith("tests/") and ".py" in i for i in ids)
