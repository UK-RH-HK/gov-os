"""Q-1 (the owner's DEC-1050): the merge queue attributes a red once with the batch (its alone re-run) and once on the
head without the batch, with the same failure type; no baseline clone; 3 rounds only for the cases the load-sensitive
list names; the head without the batch is judged even when the integration store is not at that head (the
2026-11-02 20:41 stop). Planted repositories, a planted integration store and stub commands only (as in
test_merge_queue_seed.py, whose helpers this file loads): nothing here touches this repository's branches, its
stores, the real integration store or ~/gov-os-runs."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("merge_queue_seed_helpers", HERE / "test_merge_queue_seed.py")
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)
mq = S.mq
w = S.w  # the planted repository and integration store (its fixture)

# The test command: one line per call (the tree it ran in, its arguments), then pytest.
COUNTING = ("import json, os, subprocess, sys\n"
            "open(os.environ['MQ_T_CALLS'], 'a').write(json.dumps([os.path.basename(os.getcwd()), sys.argv[1:]]) + '\\n')\n"
            "sys.exit(subprocess.run([sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', *sys.argv[1:]])"
            ".returncode)\n")
KNOWN = "tests/test_known.py::test_known"


# ---- the verdict, the list, the rounds -----------------------------------------------------------------------------

@pytest.mark.parametrize("with_rc, without_rc, verdict", [
    (0, 0, "flaky"), (0, 1, "flaky"),  # green with the batch: decides nothing
    (1, 0, "owned"),  # green without the batch: the batch's
    (1, 1, "unowned"),  # red there too (the caller then compares the failure)
    (1, 2, "owned"), (1, 4, "owned"), (2, 5, "owned"),  # cannot run without the batch (a test it added): the batch's
    (2, 1, "unowned"),  # an error with the batch, red without it
])
def test_one_run_each_way_decides(with_rc, without_rc, verdict):
    assert mq.trace_once(with_rc, without_rc) == verdict


def test_the_list_names_a_case_a_function_or_a_file(tmp_path):
    f = tmp_path / "ls.txt"
    f.write_text("# a comment\n\n  tests/a.py::test_x  \ntests/b.py\ntests/c.py::test_p[1]\n")
    entries = mq.read_list(f)
    assert entries == ["tests/a.py::test_x", "tests/b.py", "tests/c.py::test_p[1]"]
    hit = lambda node: any(mq.covers(e, node) for e in entries)  # noqa: E731
    assert hit("tests/a.py::test_x") and hit("tests/a.py::test_x[slow]")
    assert hit("tests/b.py::test_any") and hit("tests/b.py::TestK::test_any[2]") and hit("tests/c.py::test_p[1]")
    assert not hit("tests/a.py::test_xy") and not hit("tests/a.py::test_y") and not hit("tests/c.py::test_p[2]")
    assert not hit("tests/b.pyx::test_any")


def test_only_a_listed_case_gets_three_rounds(tmp_path):
    a = type("A", (), {"repo": str(tmp_path), "integration": "w2/integrate", "rounds": 1})()
    q = mq.Queue(a, tmp_path)
    q.sensitive = ["tests/slow.py"]
    assert q.rounds_for("tests/slow.py::test_s") == mq.LOAD_ROUNDS == 3
    assert q.rounds_for("tests/fast.py::test_f") == 1
    q.rounds = 5
    assert q.rounds_for("tests/slow.py::test_s") == 5 and q.rounds_for("tests/fast.py::test_f") == 5


def test_the_default_is_one_round():
    ap_args = ["run", "--repo", ".", "--queue", "q"]
    seen = {}
    real = mq.run
    try:
        mq.run = lambda a: seen.update(rounds=a.rounds, ls=a.load_sensitive) or 0
        mq.main(ap_args)
    finally:
        mq.run = real
    assert seen == {"rounds": 1, "ls": None}


# ---- the queue on planted repositories -------------------------------------------------------------------------------

def calls(w):
    return S.lines(w.tmp / "calls.jsonl")


def alone_runs(w, node, tree_prefix):
    return [c for c in calls(w) if c[0].startswith(tree_prefix) and node in c[1]]


def run(w, *extra, store=True):
    cmd = w.tmp / "counting.py"
    cmd.write_text(COUNTING)
    return S.tool("run", "--repo", w.repo, "--queue", w.q, "--work", w.tmp / "work", "--test-cmd",
                  f"{sys.executable} {cmd}", "--select-cmd", f"{sys.executable} {w.f['select.py']}",
                  "--prepare-cmd", f"{sys.executable} {w.f['prepare.py']}",
                  *(["--integration-store", w.link] if store else []), *extra)


@pytest.fixture
def counted(w, monkeypatch):
    monkeypatch.setenv("MQ_T_CALLS", str(w.tmp / "calls.jsonl"))
    return w


def test_a_red_on_the_head_too_is_traced_once_each_way_and_lands(counted):
    w = counted
    h = S.on_integrate(w, {"tests/test_known.py": S.ASSERT_RED}, "a known red")
    S.store_at(w, h)
    S.enter(w, "A", S.ticket(w, "A", {"tests/test_a.py": S.OK, "src/a.py": "A = 1\n"}))
    r = run(w)  # no --rounds: the default, one
    assert r.returncode == 0, r.stdout + r.stderr
    assert S.record(w)["unowned"] == [KNOWN] and S.record(w)["trace_base"] == h
    assert len(alone_runs(w, KNOWN, "merged")) == 1  # the alone re-run with the batch, nothing more
    assert len(alone_runs(w, KNOWN, "head-")) == 1  # one run on the head without the batch
    assert "'rounds': 1" in r.stdout and "alt" not in [Path(p[0]).name for p in S.prepares(w)]  # no baseline clone


def test_a_red_without_the_batch_is_the_batchs_after_one_run(counted):
    w = counted
    lib = "import sys, pathlib\nsys.path.insert(0, str(pathlib.Path(__file__).parents[1] / 'src'))\nimport k\n\n\n" \
          "def test_known():\n    assert k.V == 1\n"
    h = S.on_integrate(w, {"src/k.py": "V = 1\n", "tests/test_known.py": lib}, "green on the head")
    S.enter(w, "A", S.ticket(w, "A", {"src/k.py": "V = 0\n"}, start=h))
    S.store_at(w, S.on_integrate(w, {"src/other.py": "Y = 1\n"}, "an unrelated merge"))  # so the run is not skipped
    old = S.head(w)
    r = run(w)
    assert r.returncode == 3 and S.head(w) == old, r.stdout + r.stderr
    assert json.loads((w.q / "ejected/A.json").read_text())["failing"] == [KNOWN]
    assert len(alone_runs(w, KNOWN, "head-")) == 1 and len(alone_runs(w, KNOWN, "merged")) == 1


def test_a_red_on_the_head_that_fails_another_way_is_the_batchs(counted):
    w = counted
    h = S.on_integrate(w, {"tests/test_known.py": S.VALUE_RED}, "red on the head with a ValueError")
    S.enter(w, "A", S.ticket(w, "A", {"tests/test_known.py": S.ASSERT_RED}, start=h))  # red with an AssertionError
    S.store_at(w, S.on_integrate(w, {"src/other.py": "Y = 1\n"}, "an unrelated merge"))
    old = S.head(w)
    r = run(w)
    assert r.returncode == 3 and S.head(w) == old, r.stdout + r.stderr
    assert "not the same failure (['AssertionError'] here, ['ValueError'] there)" in r.stdout
    assert len(alone_runs(w, KNOWN, "head-")) == 1  # the kinds come from the runs made, not from extra ones
    assert len(alone_runs(w, KNOWN, "merged")) == 1


GREEN_KNOWN = ('<testsuite><testcase classname="tests.test_known" name="test_known"/>'
               '<testcase classname="tests.test_ok" name="test_ok"/></testsuite>')
RED_KNOWN = ('<testsuite><testcase classname="tests.test_known" name="test_known">'
             '<failure message="assert False">x</failure></testcase></testsuite>')


def test_the_heads_own_nightly_answers_first_without_a_run(counted):
    """The nightly record lookup stays first (Q-1): green in the nightly of exactly the head without the batch, the red
    is the batch's with no run there, no throwaway tree and no refresh."""
    w = counted
    lib = "import sys, pathlib\nsys.path.insert(0, str(pathlib.Path(__file__).parents[1] / 'src'))\nimport k\n\n\n" \
          "def test_known():\n    assert k.V == 1\n"
    h0 = S.on_integrate(w, {"src/k.py": "V = 1\n", "tests/test_known.py": lib}, "green on the head")
    S.enter(w, "A", S.ticket(w, "A", {"src/k.py": "V = 0\n"}, start=h0))
    h = S.on_integrate(w, {"src/other.py": "Y = 1\n"}, "an unrelated merge")  # the store stays behind
    r = run(w, *S.nightly(w, h, GREEN_KNOWN))
    assert r.returncode == 3, r.stdout + r.stderr
    assert "green on the head without the batch in that head's own nightly (no run): owned" in r.stdout
    assert alone_runs(w, KNOWN, "head-") == [] and S.refreshes(w) == 0 and mq.HEAD_TREE not in r.stdout


def test_a_red_in_the_heads_own_nightly_never_clears_without_a_run(counted):
    """A red the nightly of that head had is not taken as clearing by itself: the case runs once there (Q-1)."""
    w = counted
    h = S.on_integrate(w, {"tests/test_known.py": S.ASSERT_RED}, "a known red")
    S.store_at(w, h)
    S.enter(w, "A", S.ticket(w, "A", {"tests/test_a.py": S.OK, "src/a.py": "A = 1\n"}))
    r = run(w, *S.nightly(w, h, RED_KNOWN, f"red-alone {KNOWN}: 1 failed\n"))
    assert r.returncode == 0, r.stdout + r.stderr
    assert S.record(w)["unowned"] == [KNOWN] and len(alone_runs(w, KNOWN, "head-")) == 1


def test_a_load_sensitive_case_gets_three_rounds_each_way(counted):
    w = counted
    h = S.on_integrate(w, {"tests/test_known.py": S.ASSERT_RED}, "a known red")
    S.store_at(w, h)
    S.enter(w, "A", S.ticket(w, "A", {"tests/test_a.py": S.OK, "src/a.py": "A = 1\n"}))
    ls = w.tmp / "load_sensitive.txt"
    ls.write_text("# the CTO's list\ntests/test_known.py\n")
    r = run(w, "--load-sensitive", ls)
    assert r.returncode == 0, r.stdout + r.stderr
    assert S.record(w)["unowned"] == [KNOWN] and "'rounds': 3" in r.stdout
    assert len(alone_runs(w, KNOWN, "head-")) == 3 and len(alone_runs(w, KNOWN, "merged")) == 1 + 3


def test_an_unreadable_load_sensitive_list_stops_before_anything(counted):
    w = counted
    S.enter(w, "A", S.ticket(w, "A", {"tests/test_a.py": S.OK}))
    old = S.head(w)
    r = run(w, "--load-sensitive", w.tmp / "missing.txt")
    assert r.returncode == 4 and S.head(w) == old and (w.q / "approved/A.json").exists()
    assert "the load-sensitive list" in r.stderr and calls(w) == []


# ---- the head without the batch when the integration store is not at that head (2026-11-02 20:41) -------------------

MOVING_REFRESH = ('#!/usr/bin/env bash\n'  # the branch moves on by a record first, then the normal refresh builds it
                  'echo refresh >> "$MQ_T_REFRESHES"\n'
                  'tip=$(git -C "$GOV_STORE_REPO" rev-parse "$GOV_STORE_REF")\n'
                  'new=$(git -C "$GOV_STORE_REPO" -c user.name=t -c user.email=t@t commit-tree "$tip^{tree}" -p "$tip"'
                  ' -m "a record")\n'
                  'git -C "$GOV_STORE_REPO" update-ref "refs/heads/$GOV_STORE_REF" "$new" "$tip"\n'
                  'cur=$(readlink -f "$GOV_STORE_LINK")\n'
                  'case "$cur" in *-a) next=$GOV_STORE_LINK-b ;; *) next=$GOV_STORE_LINK-a ;; esac\n'
                  'git -C "$next" checkout -q --force --detach "$new" || exit 2\n'
                  'mkdir -p "$next/.gov-runtime" && echo "refreshed at $new" > "$next/.gov-runtime/store.db"\n'
                  'ln -sfn "$next" "$GOV_STORE_LINK.tmp" && mv -T "$GOV_STORE_LINK.tmp" "$GOV_STORE_LINK"\n')
FAILING_REFRESH = '#!/usr/bin/env bash\necho refresh >> "$MQ_T_REFRESHES"\nexit 2\n'


def store_behind(w, refresh, monkeypatch):
    stub = w.tmp / "refresh-q1.sh"
    stub.write_text(refresh)
    monkeypatch.setenv("MERGE_QUEUE_REFRESH", str(stub))
    h = S.on_integrate(w, {"tests/test_known.py": S.ASSERT_RED}, "a known red; the store is left behind")
    S.enter(w, "A", S.ticket(w, "A", {"tests/test_a.py": S.OK, "src/a.py": "A = 1\n"}))
    return h


def head_tree_prepares(w, at):
    return [p for p in S.prepares(w) if Path(p[0]).name.startswith(mq.HEAD_TREE) and p[1] == at]


def test_a_store_its_refresh_cannot_bring_to_the_head_seeds_and_rebuilds_the_throwaway_tree(counted, monkeypatch):
    w = counted
    h = store_behind(w, FAILING_REFRESH, monkeypatch)
    r = run(w)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "its normal refresh first" in r.stdout and S.refreshes(w) >= 1
    assert "rebuilt once, seeded from the integration store" in r.stdout and "cannot be judged" not in r.stderr
    assert S.record(w)["unowned"] == [KNOWN]
    assert len(head_tree_prepares(w, h)) == 1  # one rebuild of the throwaway tree, at the head
    seeds = [s for s in S.lines(w.tmp / "seeds.jsonl") if Path(s[1]).name.startswith(mq.HEAD_TREE)]
    assert len(seeds) == 1 and seeds[0][seeds[0].index("--base") + 1] == str(w.link)  # seeded, never cold
    assert "alt" not in [Path(p[0]).name for p in S.prepares(w)]


def test_the_20_41_case_a_refresh_that_builds_the_branchs_newer_head_no_longer_stops(counted, monkeypatch):
    """The 20:41 run: the store behind the head under test; the branch moved on by a record while the refresh ran, so
    the refresh built the newer head; the run stopped. Now: one seeded rebuild of the throwaway tree, and the run goes
    on (the moved head then gets its new merge and run, judged from the store now at that head)."""
    w = counted
    h = store_behind(w, MOVING_REFRESH, monkeypatch)
    r = run(w)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "cannot be judged" not in r.stderr and "rebuilt once, seeded from the integration store" in r.stdout
    assert len(head_tree_prepares(w, h)) == 1
    assert KNOWN in S.record(w)["unowned"] and S.record(w)["trace_base"] != h  # landed on the moved head


def test_a_branch_already_moved_on_is_not_refreshed_for(w, tmp_path):
    h = S.on_integrate(w, {"src/x.py": "X = 1\n"}, "the head under test; the store stays at the root")
    a = type("A", (), {"repo": str(w.repo), "integration": "w2/integrate", "rounds": 1,
                       "integration_store": str(w.link)})()
    q = mq.Queue(a, tmp_path / "q")
    q.log = tmp_path
    q.head = lambda: "f" * 40  # the branch has moved on past h
    q.refresh = lambda wait: pytest.fail("refreshed for a head the branch has left")
    tree = tmp_path / "head-tree"
    S.git(w.repo, "worktree", "add", "-q", "--detach", str(tree), h)
    assert q.copy_head_stores(h, tree) is None and not (tree / mq.STORE_REL).exists()
    assert "has moved on: no refresh" in (tmp_path / "queue.txt").read_text()
