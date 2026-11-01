"""The merge queue's --base (DEC-988, DEC-989): reds traced against a known state (the last nightly with a verdict),
never against code made by undoing merges; cleared only if red there with the same failure. Planted repositories
and stub commands only (nothing here touches this repository's branches, its stores or ~/gov-os-runs)."""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

TOOL = Path(os.environ.get("MQ_TOOL") or Path(__file__).resolve().parents[3]
            / "governance/project/orchestration/tools/merge_queue.py")
_spec = importlib.util.spec_from_file_location("merge_queue_base", TOOL)
mq = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mq)

SELECT = ("import json, sys\n"
          "print(json.dumps({'scope': 'scoped', 'selected': [{'target': 'tests'}], 'pytest_options': [],\n"
          "                  'core_changed': [], 'unplaced': []}))\n")
PYTEST = f"{sys.executable} -m pytest -q -p no:cacheprovider"
OK = "def test_ok():\n    pass\n"
ASSERT_RED = "def test_known():\n    assert False\n"
VALUE_RED = "def test_known():\n    raise ValueError('x')\n"


def git(d, *a):
    return subprocess.run(["git", "-C", str(d), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                          capture_output=True, text=True, check=True).stdout.strip()


def commit(d, files, msg, task=None):
    for rel, text in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    git(d, "add", "-A")
    git(d, "commit", "-q", "-m", msg, *(["--trailer", f"Task: {task}"] if task else []))
    return git(d, "rev-parse", "HEAD")


@pytest.fixture
def w(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    root = commit(repo, {"tests/test_ok.py": OK}, "root")
    git(repo, "checkout", "-q", "-b", "w2/integrate")
    git(repo, "checkout", "-q", "main")
    sel = tmp_path / "select.py"
    sel.write_text(SELECT)
    return SimpleNamespace(tmp=tmp_path, repo=repo, root=root, q=tmp_path / "q", sel=sel)


def on_integrate(w, files, msg):
    git(w.repo, "checkout", "-q", "w2/integrate")
    c = commit(w.repo, files, msg)
    git(w.repo, "checkout", "-q", "main")
    return c


def ticket(w, name, files, start=None):
    git(w.repo, "checkout", "-q", "-b", f"w2/{name}", start or w.root)
    c = commit(w.repo, files, f"{name} work", f"T-{name}")
    git(w.repo, "checkout", "-q", "main")
    return c


def tool(*args):
    return subprocess.run([sys.executable, str(TOOL), *map(str, args)], capture_output=True, text=True)


def enter(w, name, c):
    assert tool("enqueue", "--queue", w.q, "--ticket", name, "--task", f"T-{name}", "--branch", f"w2/{name}",
                "--commit", c, "--repo", w.repo).returncode == 0
    assert tool("approve", "--queue", w.q, "--ticket", name, "--by", "CTO").returncode == 0


def run(w, base):
    return tool("run", "--repo", w.repo, "--queue", w.q, "--work", w.tmp / "work", "--test-cmd", PYTEST,
                "--select-cmd", f"{sys.executable} {w.sel}", "--prepare-cmd", "true", "--rounds", "1",
                *(["--base", base] if base else []))


def head(w):
    return git(w.repo, "rev-parse", "w2/integrate")


def record(w):
    return json.loads((w.q / "records" / f"{head(w)[:12]}.json").read_text())


def test_failure_kinds_reads_failures_and_setup_errors(tmp_path):
    x = tmp_path / "r.xml"
    x.write_text('<testsuite><testcase classname="t" name="a"><failure message="AssertionError: assert False"/>'
                 '</testcase><testcase classname="t" name="b"><error message="failed on setup with &quot;'
                 'RuntimeError: boom&quot;"/></testcase><testcase classname="t" name="c"/></testsuite>')
    assert mq.failure_kinds([x]) == ["AssertionError", "RuntimeError"]
    assert mq.failure_kinds([tmp_path / "missing.xml"]) == []


def test_a_red_the_baseline_had_with_the_same_failure_is_cleared_and_the_branch_advances(w):
    base = on_integrate(w, {"tests/test_known.py": ASSERT_RED}, "a known red at the nightly")
    on_integrate(w, {"src/later.py": "X = 1\n"}, "a later merge")
    enter(w, "A", ticket(w, "A", {"tests/test_a.py": OK}))
    r = run(w, base)
    assert r.returncode == 0, r.stdout + r.stderr
    rec = record(w)
    assert rec["unowned"] == ["tests/test_known.py::test_known"] and rec["trace_base"] == base


def test_a_red_the_baseline_had_failing_differently_is_the_batchs(w):
    base = on_integrate(w, {"tests/test_known.py": ASSERT_RED}, "a known red at the nightly")
    on_integrate(w, {"src/later.py": "X = 1\n"}, "a later merge")
    old = head(w)
    enter(w, "A", ticket(w, "A", {"tests/test_known.py": VALUE_RED}, start=base))
    r = run(w, base)
    assert r.returncode == 3 and head(w) == old, r.stdout + r.stderr
    e = json.loads((w.q / "ejected/A.json").read_text())
    assert e["reason"] == "red" and e["failing"] == ["tests/test_known.py::test_known"]


def test_a_red_green_at_the_baseline_that_the_candidate_caused_is_ejected(w):
    base = on_integrate(w, {"src/later.py": "X = 1\n"}, "the nightly's head")
    old = head(w)
    enter(w, "A", ticket(w, "A", {"tests/test_new.py": ASSERT_RED.replace("known", "new")}))
    r = run(w, base)
    assert r.returncode == 3 and head(w) == old
    assert json.loads((w.q / "ejected/A.json").read_text())["failing"] == ["tests/test_new.py::test_new"]


def test_a_red_that_came_after_the_baseline_stops_the_queue_and_blames_nobody(w):
    base = on_integrate(w, {"src/later.py": "X = 1\n"}, "the nightly's head")
    on_integrate(w, {"tests/test_since.py": ASSERT_RED.replace("known", "since")}, "a merge after the nightly")
    old = head(w)
    enter(w, "A", ticket(w, "A", {"tests/test_a.py": OK}))
    r = run(w, base)
    assert r.returncode == 4 and head(w) == old
    assert "red since the baseline" in r.stderr and "tests/test_since.py::test_since" in r.stderr
    assert (w.q / "approved/A.json").exists() and not (w.q / "ejected").exists()


def test_without_base_the_head_without_the_batch_still_clears(w):  # the earlier behaviour, unchanged
    on_integrate(w, {"tests/test_since.py": ASSERT_RED.replace("known", "since")}, "a merge after the nightly")
    enter(w, "A", ticket(w, "A", {"tests/test_a.py": OK}))
    r = run(w, None)
    assert r.returncode == 0 and record(w)["unowned"] == ["tests/test_since.py::test_since"]


def test_a_baseline_that_is_not_a_commit_stops_before_anything(w):
    old = head(w)
    enter(w, "A", ticket(w, "A", {"tests/test_a.py": OK}))
    r = run(w, "0" * 40)
    assert r.returncode == 4 and head(w) == old and (w.q / "approved/A.json").exists()


def test_a_bare_assert_and_an_assert_with_a_message_are_the_same_failure(tmp_path):
    x = tmp_path / "r.xml"
    x.write_text('<testsuite><testcase classname="t" name="a"><failure message="assert 1 == 2"/></testcase>'
                 '</testsuite>')
    y = tmp_path / "s.xml"
    y.write_text('<testsuite><testcase classname="t" name="a"><failure message="AssertionError: boom&#10;assert False"/>'
                 '</testcase></testsuite>')
    assert mq.failure_kinds([x]) == mq.failure_kinds([y]) == ["AssertionError"]


def test_an_unknown_failure_never_matches():  # a timeout or a missing JUnit file on either side
    assert not mq.same_failure([], []) and not mq.same_failure(["X"], []) and mq.same_failure(["X"], ["X"])


def test_a_baseline_red_a_later_merge_fixed_and_the_batch_breaks_again_is_the_batchs(w):
    known = "import sys, pathlib\nsys.path.insert(0, str(pathlib.Path(__file__).parents[1] / 'src'))\nimport k\n\n\n" \
            "def test_known():\n    assert k.V == 1\n"
    base = on_integrate(w, {"src/k.py": "V = 0\n", "tests/test_known.py": known}, "a known red at the nightly")
    fixed = on_integrate(w, {"src/k.py": "V = 1\n"}, "a later merge fixes it")
    c = ticket(w, "A", {"src/k.py": "V = 0\n"}, start=fixed)  # breaks it again, the same way
    on_integrate(w, {"src/other.py": "Y = 1\n"}, "an unrelated merge")
    old = head(w)
    enter(w, "A", c)
    r = run(w, base)
    assert r.returncode == 3 and head(w) == old, r.stdout + r.stderr
    assert json.loads((w.q / "ejected/A.json").read_text())["failing"] == ["tests/test_known.py::test_known"]
