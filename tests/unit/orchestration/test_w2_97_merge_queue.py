"""W2-97, the local merge queue (DEC-959 item 1, DEC-979 item 3, DEC-968): close_build.py's reviewed red attribution
and culprit search, carried as merge_queue.py holds them (their 26 cases), and the queue's runs on planted
repositories with stub commands (nothing here touches this repository's branches, its stores or ~/gov-os-runs)."""
import fcntl
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

TOOL = Path(__file__).resolve().parents[3] / "governance/project/orchestration/tools/merge_queue.py"
_spec = importlib.util.spec_from_file_location("w2_97_merge_queue", TOOL)
mq = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mq)


# ---- close_build.py's cases (reviewed three times on 2026-10-31) ---------------------------------------------------

def trace(seq):
    """seq: per round (exit with the change, exit without it)."""
    w = iter(a for a, _ in seq)
    wo = iter(b for _, b in seq)
    verdict, c = mq.trace_node(lambda: next(w), lambda: next(wo))
    return verdict, c["rounds"]


def test_a_new_failing_test_is_the_changes():  # absent without the change (exit 4)
    assert trace([(1, 4)] * 6) == ("owned", 0)


def test_a_collection_error_without_the_change_is_the_changes():
    assert trace([(1, 2)] * 6)[0] == "owned"


def test_absent_without_even_if_green_with_is_the_changes():  # fails closed
    assert trace([(0, 5)] * 6)[0] == "owned"


def test_red_with_green_without_is_the_changes_after_3():
    assert trace([(1, 0)] * 6) == ("owned", 3)


def test_a_collection_error_with_the_change_counts_red():
    assert trace([(2, 0)] * 6) == ("owned", 3)


def test_red_both_ways_is_not_the_changes_after_3():
    assert trace([(1, 1)] * 6) == ("unowned", 3)


def test_load_sensitive_mixed_is_not_the_changes():
    assert trace([(1, 0), (0, 0), (0, 1), (1, 1), (0, 0), (0, 1)])[0] == "unowned"


def test_much_worse_with_the_change_is_the_changes():
    assert trace([(1, 0), (1, 1), (1, 0), (1, 0), (1, 0), (1, 0)]) == ("owned", 6)


def test_intermittent_only_with_the_change_is_the_changes():
    assert trace([(1, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]) == ("owned", 6)


def test_green_with_the_change_every_round_is_flaky():
    assert trace([(0, 0)] * 6) == ("flaky", 6)


def test_slightly_worse_with_is_not_the_changes():
    assert trace([(1, 1), (1, 0), (0, 0), (1, 1), (0, 0), (0, 0)])[0] == "unowned"


def rcs(*codes):
    it = iter(codes)
    return lambda: next(it)


def test_green_without_in_three_rounds_explains():
    assert mq.explained_without(rcs(0, 0, 0)) == "yes"


def test_one_red_round_without_does_not_explain():
    assert mq.explained_without(rcs(0, 1, 0)) == "no"


def test_a_collection_error_or_crash_without_does_not_explain():
    assert mq.explained_without(rcs(2)) == "no"
    assert mq.explained_without(rcs(-9)) == "no"


def test_red_alone_needs_a_real_failure_every_round():
    assert mq.red_alone(rcs(1, 1, 1)) is True
    assert mq.red_alone(rcs(1, 0, 1)) is False
    assert mq.red_alone(rcs(4, 4, 4)) is False


def culprits(reds, candidates, verdicts, skip=(), confirmed=()):
    state = {}

    def prepare(c):
        state["c"] = c
        return c not in skip

    return mq.assign_culprits(reds, candidates, prepare, lambda r: verdicts.get((r, state["c"]), "no"),
                              lambda r, c: (r, c) in confirmed)


def test_one_culprit_explains_its_reds_and_the_rest_close():
    got, left, skipped = culprits(["r1", "r2"], ["A", "B", "C"], {("r1", "B"): "yes", ("r2", "B"): "yes"})
    assert got == {"r1": ["B"], "r2": ["B"]} and left == [] and skipped == []


def test_two_culprits_each_own_their_red():
    got, left, _ = culprits(["r1", "r2"], ["A", "B"], {("r1", "A"): "yes", ("r2", "B"): "yes"})
    assert got == {"r1": ["A"], "r2": ["B"]} and left == []


def test_a_red_either_ticket_alone_explains_sends_both_back():
    got, left, _ = culprits(["r1"], ["A", "B", "C"], {("r1", "A"): "yes", ("r1", "B"): "yes"})
    assert got == {"r1": ["A", "B"]} and left == []


def test_a_red_no_single_ticket_explains_is_unexplained():
    got, left, _ = culprits(["r1"], ["A", "B"], {})
    assert got == {} and left == ["r1"]


def test_a_skipped_candidate_is_reported_so_the_batch_is_refused():
    _, _, skipped = culprits(["r1"], ["A", "B"], {("r1", "A"): "yes"}, skip={"B"})
    assert skipped == ["B"]


def test_a_test_a_ticket_added_is_its_own_only_if_red_with_it_alone():
    got, left, _ = culprits(["r1"], ["A", "B"], {("r1", "A"): "absent"}, confirmed={("r1", "A")})
    assert got == {"r1": ["A"]} and left == []


def test_a_test_a_ticket_added_that_another_breaks_is_not_blamed_on_it():
    got, left, _ = culprits(["r1"], ["A", "B"], {("r1", "A"): "absent", ("r1", "B"): "yes"}, confirmed=set())
    assert got == {"r1": ["B"]} and left == []


def test_an_unproven_absent_test_with_no_other_cause_refuses():
    got, left, _ = culprits(["r1"], ["A", "B"], {("r1", "A"): "absent"}, confirmed=set())
    assert got == {} and left == ["r1"]


def test_every_candidate_is_tried():
    seen = []

    def prepare(c):
        seen.append(c)
        return True

    mq.assign_culprits(["r1"], ["A", "B", "C"], prepare, lambda r: "yes" if seen[-1] == "A" else "no",
                       lambda r, c: False)
    assert seen == ["A", "B", "C"]


def git(d, *a):
    return subprocess.run(["git", "-C", str(d), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                          capture_output=True, text=True, check=True).stdout.strip()


def _repo(tmp_path):
    d = tmp_path / "r"
    d.mkdir()
    g = lambda *a: git(d, *a)  # noqa: E731
    g("init", "-q", "-b", "main")
    g("commit", "-q", "--allow-empty", "-m", "base")
    return g


def test_a_tickets_own_commits_are_isolable(tmp_path):
    g = _repo(tmp_path)
    g("checkout", "-q", "-b", "a")
    g("commit", "-q", "--allow-empty", "-m", "a1", "--trailer", "Task: T-A")
    assert mq.own_commits(g, "main", "a", "T-A") is True


def test_a_commit_that_brings_another_tickets_commits_is_not(tmp_path):  # a stacked branch
    g = _repo(tmp_path)
    g("checkout", "-q", "-b", "b")
    g("commit", "-q", "--allow-empty", "-m", "b1", "--trailer", "Task: T-B")
    g("checkout", "-q", "-b", "a")
    g("commit", "-q", "--allow-empty", "-m", "a1", "--trailer", "Task: T-A")
    assert mq.own_commits(g, "main", "a", "T-A") is False


# ---- the queue's own helpers ---------------------------------------------------------------------------------------

def test_the_governance_grammar_and_the_test_maps_record_places(tmp_path):
    assert mq.match("governance/project/briefs/a/b.md", "governance/project/briefs/**")
    assert mq.match("docs/close/nightly/x.json", "docs/close/nightly/*.json")
    assert not mq.match("src/gov/x.py", "governance/project/orchestration/**")
    (tmp_path / "governance/project").mkdir(parents=True)
    (tmp_path / mq.MAP_REL).write_text('shared_core:\n  - "src/**"\nrecord_only:\n  - ".tickets/**.md"\n'
                                       '  - docs/plan/**.md\nevery_close:\n  - tests/x\n')
    assert mq.record_places(tmp_path) == [".tickets/**.md", "docs/plan/**.md"]
    assert mq.record_places(tmp_path / "none") == []


def test_failing_ids_follow_pytests_rootdir(tmp_path):
    (tmp_path / "tests/sub").mkdir(parents=True)
    (tmp_path / "tests/sub/test_k.py").write_text("")
    xml = tmp_path / "r.xml"
    xml.write_text('<testsuites><testsuite tests="3" failures="1" errors="1">'
                   '<testcase classname="sub.test_k.TestK" name="test_x"><failure/></testcase>'
                   '<testcase classname="" name="sub.test_k"><error/></testcase>'
                   '<testcase classname="sub.test_k" name="test_ok"/></testsuite></testsuites>')
    assert mq.failing([xml], tmp_path, ["tests"]) == ["tests/sub/test_k.py::TestK::test_x", "tests/sub/test_k.py"]
    up = tmp_path / "up.xml"  # a rootdir above the checkout (an ini file further up)
    up.write_text('<testsuite><testcase classname="work.merged.tests.sub.test_k" name="test_y"><failure/></testcase>'
                  '</testsuite>')
    assert mq.failing([up], tmp_path, ["tests"]) == ["tests/sub/test_k.py::test_y"]
    assert mq.totals([xml]) == {"tests": 3, "failures": 1, "errors": 1, "skipped": 0}


# ---- the queue on planted repositories ----------------------------------------------------------------------------

BASE_TEST = "from lib import value\n\n\ndef test_value():\n    assert value() == 1\n"
SELECT = ("import json, pathlib, sys\n"
          "with open(pathlib.Path(sys.argv[0]).with_suffix('.args'), 'a') as f:\n"
          "    f.write(json.dumps(sys.argv[1:]) + '\\n')\n"
          "if pathlib.Path(sys.argv[0]).with_suffix('.refuse').exists():\n"
          "    print(json.dumps({'scope': 'refused'})); sys.exit(2)\n"
          "full = pathlib.Path(sys.argv[0]).with_suffix('.full').exists()\n"
          "print(json.dumps({'scope': 'full' if full else 'scoped', 'selected': [{'target': 'tests'}], 'pytest_options': [],\n"
          "                  'core_changed': [], 'unplaced': []}))\n")
PYTEST = f"{sys.executable} -m pytest -q -p no:cacheprovider"


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
    """A planted repository: main and w2/integrate; the integration head one code commit past the base."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.name", "Queue Tester")
    git(repo, "config", "user.email", "qt@example.invalid")
    base = commit(repo, {"src/lib.py": "def value():\n    return 1\n", "tests/test_base.py": BASE_TEST}, "base")
    git(repo, "checkout", "-q", "-b", "w2/integrate")
    commit(repo, {"src/extra.py": "X = 1\n"}, "an earlier merge")
    git(repo, "checkout", "-q", "main")
    sel = tmp_path / "select.py"
    sel.write_text(SELECT)
    return SimpleNamespace(tmp=tmp_path, repo=repo, base=base, q=tmp_path / "q", sel=sel)


def ticket(w, name, files, start=None):
    git(w.repo, "checkout", "-q", "-b", f"w2/{name}", start or w.base)
    c = commit(w.repo, files, f"{name} work", f"T-{name}")
    git(w.repo, "checkout", "-q", "main")
    return c


def tool(*args):
    return subprocess.run([sys.executable, str(TOOL), *map(str, args)], capture_output=True, text=True)


def enter(w, name, commit):
    assert tool("enqueue", "--queue", w.q, "--ticket", name, "--task", f"T-{name}", "--branch", f"w2/{name}",
                "--commit", commit, "--repo", w.repo).returncode == 0
    assert tool("approve", "--queue", w.q, "--ticket", name, "--by", "CTO").returncode == 0


def run(w, test_cmd=PYTEST):
    return tool("run", "--repo", w.repo, "--queue", w.q, "--work", w.tmp / "work", "--test-cmd", test_cmd,
                "--select-cmd", f"{sys.executable} {w.sel}", "--prepare-cmd", "true", "--rounds", "1")


def head(w):
    return git(w.repo, "rev-parse", "w2/integrate")


def entry(w, kind, name):
    return json.loads((w.q / kind / f"{name}.json").read_text())


def test_approve_needs_a_request_and_a_request_alone_never_runs(w):
    c = ticket(w, "A", {"tests/test_a.py": "def test_a():\n    pass\n"})
    r = tool("approve", "--queue", w.q, "--ticket", "A", "--by", "CTO")
    assert r.returncode != 0 and not (w.q / "approved").exists()
    assert tool("enqueue", "--queue", w.q, "--ticket", "A", "--task", "T-A", "--branch", "w2/A", "--commit", "w2/A",
                "--repo", w.repo).returncode == 0
    assert entry(w, "requested", "A")["commit"] == c
    before = head(w)
    assert run(w).returncode == 0 and head(w) == before and not (w.q / "landed").exists()


def test_a_request_holds_the_full_id_and_run_resolves_a_hand_written_short_one(w):
    c = ticket(w, "A", {"tests/test_a.py": "def test_a():\n    pass\n"})
    r = subprocess.run([sys.executable, str(TOOL), "enqueue", "--queue", str(w.q), "--ticket", "A", "--task", "T-A",
                        "--branch", "w2/A", "--commit", c[:12]], capture_output=True, text=True, cwd=w.tmp)
    assert r.returncode != 0 and not (w.q / "requested").exists()  # nowhere to resolve it: refused, nothing written
    r = subprocess.run([sys.executable, str(TOOL), "enqueue", "--queue", str(w.q), "--ticket", "A", "--task", "T-A",
                        "--branch", "w2/A", "--commit", c[:12]], capture_output=True, text=True, cwd=w.repo)
    assert r.returncode == 0 and entry(w, "requested", "A")["commit"] == c  # the lead's worktree: resolved there
    (w.q / "approved").mkdir()
    (w.q / "approved/A.json").write_text(json.dumps(dict(entry(w, "requested", "A"), commit=c[:12],
                                                         approved_by="CTO", approved_at="2026-10-31T00:00:00")))
    assert run(w).returncode == 0
    assert entry(w, "landed", "A")["commit"] == c and git(w.repo, "rev-parse", "w2/integrate^2") == c


def test_green_advances_by_fast_forward_to_the_tested_merge_and_records_it(w):
    c = ticket(w, "A", {"tests/test_a.py": "def test_a():\n    pass\n"})
    enter(w, "A", c)
    old, refs = head(w), git(w.repo, "for-each-ref", "--format=%(refname) %(objectname)", "--exclude=refs/heads/w2/integrate")
    r = run(w)
    assert r.returncode == 0, r.stderr
    new = head(w)
    assert git(w.repo, "rev-list", "--parents", "-1", new).split()[1:] == [old, c]
    assert git(w.repo, "log", "-1", "--format=%s", new) == "Merge w2/A (T-A): merge queue"
    assert git(w.repo, "log", "-1", "--format=%(trailers:key=Task,valueonly)%(trailers:key=Role,valueonly)",
               new).split() == ["T-A", "orchestrator"]
    assert git(w.repo, "log", "-1", "--format=%an", new) == "Queue Tester"
    assert git(w.repo, "for-each-ref", "--format=%(refname) %(objectname)", "--exclude=refs/heads/w2/integrate") == refs
    rec = json.loads((w.q / "records" / f"{new[:12]}.json").read_text())
    assert rec["head"] == new and rec["base"] == old and rec["skipped"] is None
    assert rec["tickets"] == [{"ticket": "A", "task": "T-A", "commit": c, "merge": new}]
    assert rec["counts"]["tests"] == 2 and rec["counts"]["failures"] == 0 and rec["selection"]["targets"] == ["tests"]
    assert Path(rec["log"]).is_dir() and rec["started"] and rec["finished"]
    assert entry(w, "landed", "A")["merge"] == new and not (w.q / "approved/A.json").exists()
    args = json.loads(w.sel.with_suffix(".args").read_text().splitlines()[0])
    assert args[1:] == ["A", "T-A", "--merge", new] and Path(args[0]).name == "merged"
    assert not any((w.tmp / "work").iterdir())


def test_a_checked_out_integration_branch_is_fast_forwarded_in_its_worktree(w):
    c = ticket(w, "A", {"tests/test_a.py": "def test_a():\n    pass\n"})
    enter(w, "A", c)
    git(w.repo, "checkout", "-q", "w2/integrate")
    assert run(w).returncode == 0
    assert git(w.repo, "rev-parse", "HEAD") == head(w) and (w.repo / "tests/test_a.py").is_file()


def test_red_ejects_with_the_failing_tests_and_the_log_and_the_head_stays(w):
    c = ticket(w, "A", {"src/lib.py": "def value():\n    return 2\n"})
    enter(w, "A", c)
    old = head(w)
    assert run(w).returncode == 3 and head(w) == old
    e = entry(w, "ejected", "A")
    assert e["reason"] == "red" and e["failing"] == ["tests/test_base.py::test_value"] and e["tested_on"] == old
    assert Path(e["log"]).is_dir() and not (w.q / "approved/A.json").exists()


def test_a_red_that_passes_alone_is_a_flaky_candidate_and_decides_nothing(w):
    marker = w.tmp / "flaky-seen"
    c = ticket(w, "A", {"tests/test_flaky.py": f"import pathlib\nM = pathlib.Path(r'{marker}')\n\n\n"
                        "def test_flaky():\n    if not M.exists():\n        M.write_text('x')\n        assert False\n"})
    enter(w, "A", c)
    r = run(w)
    assert r.returncode == 0 and "tests/test_flaky.py::test_flaky" in r.stdout
    assert json.loads((w.q / "records" / f"{head(w)[:12]}.json").read_text())["flaky"] == ["tests/test_flaky.py::test_flaky"]


def test_a_red_without_the_batch_too_is_not_the_batchs_and_does_not_stop_it(w):
    git(w.repo, "checkout", "-q", "w2/integrate")
    commit(w.repo, {"tests/test_known.py": "def test_known():\n    assert False\n"}, "a known red")
    git(w.repo, "checkout", "-q", "main")
    enter(w, "A", ticket(w, "A", {"tests/test_a.py": "def test_a():\n    pass\n"}))
    assert run(w).returncode == 0
    rec = json.loads((w.q / "records" / f"{head(w)[:12]}.json").read_text())
    assert rec["unowned"] == ["tests/test_known.py::test_known"] and rec["counts"]["failures"] == 1


def test_identical_code_skips_the_run_and_records_why(w):
    c = ticket(w, "A", {"tests/test_a.py": "def test_a():\n    pass\n"}, start="w2/integrate")
    git(w.repo, "checkout", "-q", "w2/integrate")
    commit(w.repo, {"governance/project/briefs/x.md": "a brief\n"}, "a brief")
    git(w.repo, "checkout", "-q", "main")
    enter(w, "A", c)
    r = run(w, test_cmd="false")  # any run would stop the queue: it did not complete
    assert r.returncode == 0, r.stderr
    rec = json.loads((w.q / "records" / f"{head(w)[:12]}.json").read_text())
    assert c in rec["skipped"] and "governance/project/briefs/x.md" in rec["skipped"] and rec["counts"] is None


def test_a_batch_gives_one_result_ejects_only_its_culprit_and_lands_the_rest_tested(w):
    a = ticket(w, "A", {"tests/test_a.py": "def test_a():\n    pass\n"})
    b = ticket(w, "B", {"src/lib.py": "def value():\n    return 2\n"})
    enter(w, "A", a)
    enter(w, "B", b)
    old = head(w)
    assert run(w).returncode == 3
    assert entry(w, "ejected", "B")["failing"] == ["tests/test_base.py::test_value"]
    new = head(w)
    assert git(w.repo, "rev-list", "--parents", "-1", new).split()[1:] == [old, a]
    rec = json.loads((w.q / "records" / f"{new[:12]}.json").read_text())
    assert [t["ticket"] for t in rec["tickets"]] == ["A"] and rec["ejected"][0]["ticket"] == "B"
    assert rec["counts"]["failures"] == 0


def test_a_test_a_ticket_added_and_broke_is_blamed_on_it_alone(w):
    enter(w, "A", ticket(w, "A", {"tests/test_new.py": "def test_new():\n    assert False\n"}))
    enter(w, "B", ticket(w, "B", {"src/b.py": "B = 1\n"}))
    assert run(w).returncode == 3
    assert entry(w, "ejected", "A")["failing"] == ["tests/test_new.py::test_new"]
    assert entry(w, "landed", "B")["merge"] == head(w)


def test_a_red_no_single_ticket_explains_ejects_the_whole_batch(w):
    git(w.repo, "checkout", "-q", "w2/integrate")
    commit(w.repo, {"tests/test_none.py": "import pathlib\nS = pathlib.Path(__file__).parents[1] / 'src'\n\n\n"
                    "def test_none():\n    assert not ((S / 'a.py').exists() or (S / 'b.py').exists())\n"}, "a guard")
    git(w.repo, "checkout", "-q", "main")
    enter(w, "A", ticket(w, "A", {"src/a.py": "A = 1\n"}))
    enter(w, "B", ticket(w, "B", {"src/b.py": "B = 1\n"}))
    old = head(w)
    assert run(w).returncode == 3 and head(w) == old
    assert all("fail closed" in entry(w, "ejected", t)["reason"] for t in ("A", "B"))


def test_a_ticket_carrying_anothers_commits_fails_the_batch_closed(w):
    a = ticket(w, "A", {"tests/test_a.py": "def test_a():\n    pass\n"})
    b = ticket(w, "B", {"src/lib.py": "def value():\n    return 2\n"}, start="w2/A")
    enter(w, "A", a)
    enter(w, "B", b)
    old = head(w)
    assert run(w).returncode == 3 and head(w) == old
    assert "another ticket's work" in entry(w, "ejected", "B")["reason"] and (w.q / "ejected/A.json").is_file()


def test_a_conflict_is_ejected_and_the_rest_go_on(w):
    enter(w, "A", ticket(w, "A", {"src/lib.py": "def value():\n    return 1  # A\n"}))
    enter(w, "B", ticket(w, "B", {"src/lib.py": "def value():\n    return 1  # B\n"}))
    assert run(w).returncode == 3
    assert entry(w, "ejected", "B")["reason"] == "conflict" and entry(w, "landed", "A")["merge"] == head(w)


MOVER = ("import pathlib, subprocess, sys\n"
         "marker, repo = pathlib.Path(sys.argv[1]), sys.argv[2]\n"
         "if not marker.exists():\n"
         "    marker.write_text('x')\n"
         "    g = lambda *a: subprocess.run(['git', '-C', repo, '-c', 'user.name=t', '-c', 'user.email=t@t', *a],\n"
         "                                  capture_output=True, text=True, check=True).stdout.strip()\n"
         "    new = g('commit-tree', 'w2/integrate^{tree}', '-p', 'w2/integrate', '-m', 'moved meanwhile')\n"
         "    g('update-ref', 'refs/heads/w2/integrate', new)\n"
         "sys.exit(subprocess.run([sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', *sys.argv[3:]])"
         ".returncode)\n")


def test_a_head_that_moves_under_test_gets_a_new_merge_and_a_new_run(w):
    mover = w.tmp / "mover.py"
    mover.write_text(MOVER)
    c = ticket(w, "A", {"tests/test_a.py": "def test_a():\n    pass\n"})
    enter(w, "A", c)
    old = head(w)
    r = run(w, test_cmd=f"{sys.executable} {mover} {w.tmp / 'moved'} {w.repo}")
    assert r.returncode == 0, r.stderr
    new = head(w)
    moved = git(w.repo, "rev-parse", f"{new}^1")
    assert moved != old and git(w.repo, "rev-parse", f"{moved}^1") == old and git(w.repo, "rev-parse", f"{new}^2") == c
    assert json.loads((w.q / "records" / f"{new[:12]}.json").read_text())["base"] == moved
    assert r.stdout.count("merged A onto") == 2


def test_another_run_holding_the_lock_exits_4_at_once(w):
    enter(w, "A", ticket(w, "A", {"tests/test_a.py": "def test_a():\n    pass\n"}))
    with open(w.q / "run.lock", "a") as held:
        fcntl.flock(held, fcntl.LOCK_EX)
        r = run(w)
    assert r.returncode == 4 and "lock" in r.stderr and (w.q / "approved/A.json").is_file()


@pytest.mark.parametrize("why", ["selection refused", "selection full", "run did not complete",
                                 "red without a JUnit file"])
def test_a_step_that_cannot_be_done_keeps_everything(w, why):
    enter(w, "A", ticket(w, "A", {"tests/test_a.py": "def test_a():\n    pass\n"}))
    if why == "selection refused":
        w.sel.with_suffix(".refuse").write_text("")
    if why == "selection full":  # DEC-968, DEC-983: never run here, whatever it names
        w.sel.with_suffix(".full").write_text("")
    ran = w.tmp / "ran"
    cmd = {"selection refused": PYTEST, "run did not complete": f"{sys.executable} -c 'raise SystemExit(3)'",
           "selection full": f"{sys.executable} -c 'import pathlib; pathlib.Path(r\"{ran}\").write_text(\"x\")'",
           "red without a JUnit file": "false"}[why]
    old = head(w)
    r = run(w, test_cmd=cmd)
    assert r.returncode == 4 and "stopped" in r.stderr and head(w) == old
    assert (w.q / "approved/A.json").is_file() and not (w.q / "ejected").exists()
    if why == "selection full":
        assert "nightly" in r.stderr and not ran.exists()


def test_the_default_run_takes_a_heavy_slot_and_the_alone_reruns_do_not(tmp_path, monkeypatch):
    """DEC-979 D1, DEC-983: the parallel run and the serial-only cases go through verify_lock.sh; an alone re-run
    runs freely. A recording sh: no slot is taken and no suite runs."""
    calls = []

    def recorded(cmd, **kw):
        calls.append(cmd)
        out = json.dumps(["tests/test_s.py::test_serial"]) if cmd[1:2] == ["-c"] else ""
        return subprocess.CompletedProcess(cmd, 0, out, "")

    a = SimpleNamespace(repo=str(tmp_path), integration="w2/integrate", rounds=3, test_cmd=None)
    q = mq.Queue(a, tmp_path)
    q.log = q.work = tmp_path
    monkeypatch.setattr(mq, "sh", recorded)
    assert q.tests(tmp_path, "run", ["tests"])[0] == 0
    assert q.tests(tmp_path, "alone", ["tests/test_s.py::test_serial"])[0] == 0
    slot = ["bash", "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh",
            sys.executable, "-m", "pytest"]
    parallel, listing, serial, alone = calls
    assert parallel[:5] == slot and parallel[parallel.index("-n") + 1] == "auto" and "tests" in parallel
    assert listing[:2] == [sys.executable, "-c"]
    assert serial[:5] == slot and "tests/test_s.py::test_serial" in serial and "-n" not in serial
    assert alone[:3] == [sys.executable, "-m", "pytest"] and "bash" not in alone
