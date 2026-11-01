"""The merge queue's speed-ups (owner, DEC-1001): (a) a head that moved only by records re-runs only the
record-reading tests; (b) warm clones kept between runs; (c) the baseline nightly's own record clears a known red
without a baseline build. Planted repositories and stub commands only (nothing here touches this repository's
branches, its stores or ~/gov-os-runs)."""
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
_spec = importlib.util.spec_from_file_location("merge_queue_speed", TOOL)
mq = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mq)

SELECT = ("import json, sys\n"
          "print(json.dumps({'scope': 'scoped', 'selected': [{'target': 'tests'}], 'pytest_options': [],\n"
          "                  'core_changed': [], 'unplaced': []}))\n")
TEST_MAP = ('record_only:\n  - ".tickets/**.md"\n  - "docs/DECISION_REGISTER.md"\n'
            'record_reading:\n  - "tests/test_rr.py"\nevery_close: []\n')
MOVER = ("import os, pathlib, subprocess, sys, tempfile\n"
         "marker, repo, rel = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3]\n"
         "if not marker.exists():\n"
         "    marker.write_text('x')\n"
         "    env = dict(os.environ, GIT_INDEX_FILE=tempfile.mktemp())\n"
         "    g = lambda *a, i=None: subprocess.run(['git', '-C', repo, '-c', 'user.name=t', '-c', 'user.email=t@t', *a],\n"
         "                                          capture_output=True, text=True, check=True, env=env, input=i).stdout.strip()\n"
         "    g('read-tree', 'w2/integrate')\n"
         "    blob = g('hash-object', '-w', '--stdin', i='moved meanwhile\\n')\n"
         "    g('update-index', '--add', '--cacheinfo', '100644,' + blob + ',' + rel)\n"
         "    new = g('commit-tree', g('write-tree'), '-p', 'w2/integrate', '-m', 'moved meanwhile')\n"
         "    g('update-ref', 'refs/heads/w2/integrate', new)\n"
         "sys.exit(subprocess.run([sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', *sys.argv[4:]])"
         ".returncode)\n")


def counter(name, count_dir):
    return (f"import pathlib\nP = pathlib.Path(r'{count_dir}') / '{name}'\n\n\n"
            f"def test_{name}():\n    P.write_text(P.read_text() + 'x' if P.exists() else 'x')\n")


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
    repo, counts = tmp_path / "repo", tmp_path / "counts"
    repo.mkdir()
    counts.mkdir()
    git(repo, "init", "-q", "-b", "main")
    root = commit(repo, {"governance/project/test-map.yaml": TEST_MAP, "tests/test_rr.py": counter("rr", counts),
                         "tests/test_other.py": counter("other", counts)}, "root")
    git(repo, "checkout", "-q", "-b", "w2/integrate")
    git(repo, "checkout", "-q", "main")
    sel = tmp_path / "select.py"
    sel.write_text(SELECT)
    mover = tmp_path / "mover.py"
    mover.write_text(MOVER)
    return SimpleNamespace(tmp=tmp_path, repo=repo, root=root, q=tmp_path / "q", sel=sel, counts=counts, mover=mover)


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


def run(w, *extra, test_cmd=None):
    return tool("run", "--repo", w.repo, "--queue", w.q, "--work", w.tmp / "work", "--test-cmd",
                test_cmd or f"{sys.executable} -m pytest -q -p no:cacheprovider",
                "--select-cmd", f"{sys.executable} {w.sel}", "--prepare-cmd", "true", "--rounds", "1", *extra)


def moving(w, rel):
    return f"{sys.executable} {w.mover} {w.tmp / 'moved'} {w.repo} {rel}"


def head(w):
    return git(w.repo, "rev-parse", "w2/integrate")


def record(w):
    return json.loads((w.q / "records" / f"{head(w)[:12]}.json").read_text())


def runs(w, name):
    p = w.counts / name
    return len(p.read_text()) if p.exists() else 0


def test_record_only_change_is_records_and_never_code():
    places = [".tickets/**.md", "docs/DECISION_REGISTER.md"]
    assert mq.record_only_change([".tickets/T-1.md", "docs/DECISION_REGISTER.md"], places)
    assert mq.record_only_change(["governance/project/orchestration/packages/P.md"], places)
    assert not mq.record_only_change(["governance/project/orchestration/tools/merge_queue.py"], places)
    assert not mq.record_only_change([".tickets/T-1.md", "src/x.py"], places)
    assert not mq.record_only_change([], places)
    for code in ("governance/project/orchestration/tools/heavy_slots.conf", "governance/project/orchestration/tools/Makefile",
                 "governance/project/orchestration/tools/win_toast.ps1", "governance/project/orchestration/x.mjs",
                 "governance/project/orchestration/nightly/nightly.yaml"):
        assert not mq.record_only_change([code], places), code


def test_a_head_moved_by_records_reruns_only_the_record_reading_tests_and_lands(w):
    enter(w, "A", ticket(w, "A", {"tests/test_a.py": "def test_a():\n    pass\n"}))
    on_integrate(w, {"src/later.py": "X = 1\n"}, "an unrelated merge")
    r = run(w, test_cmd=moving(w, ".tickets/T-1.md"))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "moved by records only" in r.stdout and r.stdout.count("merged A onto") == 1
    assert runs(w, "rr") == 2 and runs(w, "other") == 1  # the record reader again, nothing else
    rec = record(w)
    assert rec["record_rerun"]["targets"] == ["tests/test_rr.py"] and rec["record_rerun"]["paths"] == [".tickets/T-1.md"]
    assert git(w.repo, "show", "w2/integrate:.tickets/T-1.md") == "moved meanwhile"


def test_a_head_moved_by_code_reruns_everything(w):
    enter(w, "A", ticket(w, "A", {"tests/test_a.py": "def test_a():\n    pass\n"}))
    on_integrate(w, {"src/later.py": "X = 1\n"}, "an unrelated merge")
    r = run(w, test_cmd=moving(w, "src/x.py"))
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.count("merged A onto") == 2 and runs(w, "other") == 2
    assert record(w)["record_rerun"] is None


@pytest.mark.parametrize("rel", ["governance/project/orchestration/tools/heavy_slots.conf",
                                 "governance/project/orchestration/tools/Makefile"])
def test_a_head_moved_by_a_conf_or_an_extensionless_file_reruns_everything(w, rel):
    enter(w, "A", ticket(w, "A", {"tests/test_a.py": "def test_a():\n    pass\n"}))
    on_integrate(w, {"src/later.py": "X = 1\n"}, "an unrelated merge")
    r = run(w, test_cmd=moving(w, rel))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "moved by records only" not in r.stdout and r.stdout.count("merged A onto") == 2 and runs(w, "other") == 2


def test_a_record_reading_red_after_the_move_falls_back_to_the_full_run(w):
    reader = ("import pathlib\n\n\ndef test_rr():\n"
              "    assert not (pathlib.Path(__file__).parents[1] / '.tickets/T-1.md').exists()\n")
    on_integrate(w, {"tests/test_rr.py": reader}, "a reader of the tickets")
    enter(w, "A", ticket(w, "A", {"tests/test_a.py": "def test_a():\n    pass\n"}))
    r = run(w, test_cmd=moving(w, ".tickets/T-1.md"))
    assert "the record-reading re-run is red" in r.stdout and r.stdout.count("merged A onto") == 2


def test_warm_clones_are_reused_and_a_broken_one_is_replaced(w):
    warm = w.tmp / "warm"
    enter(w, "A", ticket(w, "A", {"tests/test_a.py": "def test_a():\n    pass\n"}))
    assert run(w, "--warm", warm).returncode == 0 and (warm / "merged" / ".git").exists()
    (warm / "merged" / ".gov-runtime").mkdir()
    for kept in ("store.db", "store.db-wal", "query-vector-cache.db", "secrets-clean.json"):
        (warm / "merged" / ".gov-runtime" / kept).write_text("kept")
    (warm / "merged" / ".gov-runtime" / "codeintel").mkdir()
    (warm / "merged" / ".gov-runtime" / "records.jsonl").write_text("stale")
    (warm / "merged" / ".gov-runtime" / "escalations").mkdir()
    enter(w, "B", ticket(w, "B", {"tests/test_b.py": "def test_b():\n    pass\n"}))
    r = run(w, "--warm", warm)
    assert r.returncode == 0 and "warm clone merged reused" in r.stdout
    rt = warm / "merged" / ".gov-runtime"
    assert sorted(p.name for p in rt.iterdir()) == ["codeintel", "query-vector-cache.db", "secrets-clean.json",
                                                     "store.db", "store.db-wal"]  # the stores alone survive the reset
    assert not (warm / "merged" / ".gov-runtime" / "records.jsonl").exists()
    git(warm / "merged", "remote", "set-url", "origin", str(w.tmp / "elsewhere"))
    enter(w, "C", ticket(w, "C", {"tests/test_c.py": "def test_c():\n    pass\n"}))
    r = run(w, "--warm", warm)
    assert r.returncode == 0 and "could not be reset; set aside" in r.stdout
    assert Path(git(warm / "merged", "remote", "get-url", "origin")).resolve() == w.repo.resolve()


def known_red(w, junit_text, run_text):
    base = on_integrate(w, {"tests/test_known.py": "def test_known():\n    assert False\n"}, "a known red")
    on_integrate(w, {"src/later.py": "X = 1\n"}, "a later merge")
    res = w.tmp / "nightly"
    res.mkdir()
    (res / "parallel.xml").write_text(junit_text)
    (w.tmp / "run.txt").write_text(run_text or f"head {base[:12]}\nred-alone tests/test_known.py::test_known: 1 failed\n")
    enter(w, "A", ticket(w, "A", {"tests/test_a.py": "def test_a():\n    pass\n"}))
    return run(w, "--base", base, "--base-results", res, "--base-run", w.tmp / "run.txt")


JUNIT = ('<testsuites><testsuite tests="1" failures="1"><testcase classname="tests.test_known" name="test_known">'
         '<failure message="assert False">x</failure></testcase></testsuite></testsuites>')


def test_the_nightlys_record_clears_a_known_red_without_a_baseline_build(w):
    r = known_red(w, JUNIT, None)
    assert r.returncode == 0, r.stdout + r.stderr
    rec = record(w)
    assert rec["cleared_by_results"] == ["tests/test_known.py::test_known"]
    assert rec["unowned"] == ["tests/test_known.py::test_known"]
    assert "no baseline build" in r.stdout and "traced against the baseline" not in r.stdout


def test_a_case_not_red_alone_in_the_nightly_or_an_unreadable_record_falls_back_to_the_trace(w):
    r = known_red(w, "<testsuites><not-closed", None)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "cannot be read" in r.stdout and "traced against the baseline" in r.stdout
    assert record(w)["cleared_by_results"] == [] and record(w)["unowned"] == ["tests/test_known.py::test_known"]


def test_rebuild_slot_takes_a_lock_of_the_trees_own(tmp_path):
    slot = next((p for p in (TOOL.parent / "rebuild_slot.sh", mq.REBUILD_SLOT) if p.is_file()), None)
    if slot is None:
        pytest.skip("rebuild_slot.sh is not installed")
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir()
    b.mkdir()
    out = [subprocess.run(["bash", str(slot), str(t)], capture_output=True, text=True,
                          env=dict(os.environ, GOV_REBUILD_SLOT_DRY="1")).stdout for t in (a, b, a)]
    locks = [o.split()[0] for o in out]
    assert locks[0] == locks[2] != locks[1] and all(l.startswith("lock=/tmp/gov-os-rebuild-") for l in locks)
    assert "rebuild --json" in out[0] and f"tree={a.resolve()}" in out[0]
    py = subprocess.run(["bash", str(slot), str(a)], capture_output=True, text=True,
                        env=dict(os.environ, GOV_REBUILD_SLOT_DRY="1", GOV_REBUILD_PYTHON="/opt/py/bin/python3")).stdout
    assert "cmd=/opt/py/bin/python3 -m gov.cli.main rebuild --json" in py


def test_a_nightly_record_for_another_head_is_not_read(w):
    r = known_red(w, JUNIT, "head 000000000000\nred-alone tests/test_known.py::test_known: 1 failed\n")
    assert r.returncode == 0 and "is not for the baseline" in r.stdout and record(w)["cleared_by_results"] == []


def test_a_warm_clone_with_a_hook_installed_loses_it_and_one_whose_config_changed_is_replaced(w):
    warm = w.tmp / "warm"
    enter(w, "A", ticket(w, "A", {"tests/test_a.py": "def test_a():\n    pass\n"}))
    assert run(w, "--warm", warm).returncode == 0
    hook = warm / "merged" / ".git" / "hooks" / "pre-commit"
    hook.write_text("#!/bin/sh\nexit 1\n")
    enter(w, "B", ticket(w, "B", {"tests/test_b.py": "def test_b():\n    pass\n"}))
    r = run(w, "--warm", warm)
    assert r.returncode == 0 and "warm clone merged reused" in r.stdout and not hook.exists()
    git(warm / "merged", "config", "core.hooksPath", "/elsewhere")
    enter(w, "C", ticket(w, "C", {"tests/test_c.py": "def test_c():\n    pass\n"}))
    r = run(w, "--warm", warm)
    assert r.returncode == 0 and "could not be reset; set aside" in r.stdout
    assert subprocess.run(["git", "-C", str(warm / "merged"), "config", "core.hooksPath"]).returncode == 1


def test_a_cleared_red_that_fails_differently_after_the_move_forces_the_full_run(w):
    reader = ("import pathlib\n\n\ndef test_rr():\n"
              "    if (pathlib.Path(__file__).parents[1] / '.tickets/T-1.md').exists():\n"
              "        raise ValueError('another failure')\n"
              "    assert False\n")
    on_integrate(w, {"tests/test_rr.py": reader}, "a known red that reads the tickets")
    enter(w, "A", ticket(w, "A", {"tests/test_a.py": "def test_a():\n    pass\n"}))
    r = run(w, test_cmd=moving(w, ".tickets/T-1.md"))
    assert "the record-reading re-run is red" in r.stdout and r.stdout.count("merged A onto") == 2
