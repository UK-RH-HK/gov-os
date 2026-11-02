"""The merge queue without cold rebuilds (owner, DEC-1032 step (iv)): a clone with no store is seeded from the
integration store before its first rebuild; the landed result's stores become the integration store's (heads equal),
else its normal refresh; the head without the batch is read from that head's nightly or re-run on the integration
store's tree, never rebuilt. Planted repositories, a planted integration store (two worktrees behind a link) and stub
seeder, prepare and refresh commands only: nothing here touches this repository's branches, its stores, the real
integration store or ~/gov-os-runs."""
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

TOOL = Path(os.environ.get("MQ_TOOL") or Path(__file__).resolve().parents[3]
            / "governance/project/orchestration/tools/merge_queue.py")
_spec = importlib.util.spec_from_file_location("merge_queue_seed", TOOL)
mq = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mq)

SELECT = ("import json, sys\n"
          "print(json.dumps({'scope': 'scoped', 'selected': [{'target': 'tests'}], 'pytest_options': [],\n"
          "                  'core_changed': [], 'unplaced': []}))\n")
# The prepare stand-in: one line per call (the tree, its head, its arguments); it leaves a store naming that head.
PREPARE = ("import json, os, pathlib, subprocess, sys\n"
           "head = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()\n"
           "open(os.environ['MQ_T_PREPARES'], 'a').write(json.dumps([os.getcwd(), head, sys.argv[1:]]) + '\\n')\n"
           "p = pathlib.Path('.gov-runtime/store.db')\n"
           "p.parent.mkdir(exist_ok=True)\n"
           "p.write_text('built at ' + head)\n")
# The seeder stand-in: seed_store.py's answer; copies the base's store (the link followed) unless the tree has one.
SEEDER = ("import json, os, pathlib, shutil, sys\n"
          "open(os.environ['MQ_T_SEEDS'], 'a').write(json.dumps(sys.argv[1:]) + '\\n')\n"
          "if os.environ.get('MQ_T_SEED_FAIL'):\n"
          "    sys.exit('the seeder broke')\n"
          "tree, base = pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[sys.argv.index('--base') + 1]).resolve()\n"
          "if os.environ.get('MQ_T_PRODUCT'):\n"
          "    print(json.dumps({'mode': 'product', 'status': 'deferred', 'rebuild_args': ['--seed', str(base)]}))\n"
          "    sys.exit(0)\n"
          "dst = tree / '.gov-runtime/store.db'\n"
          "if dst.exists() and '--replace' not in sys.argv:\n"
          "    print(json.dumps({'mode': 'copy', 'status': 'none', 'reason': 'own store', 'rebuild_args': []}))\n"
          "    sys.exit(0)\n"
          "dst.parent.mkdir(exist_ok=True)\n"
          "shutil.copy(base / '.gov-runtime/store.db', dst)\n"
          "print(json.dumps({'mode': 'copy', 'status': 'seeded', 'kept': 'whole store', 'vectors': 1,\n"
          "                  'rebuild_args': []}))\n")
# The refresh stand-in (refresh_integration_store.sh's contract): the standby half built at the ref, the link moved.
REFRESH = ('#!/usr/bin/env bash\n'
           'echo refresh >> "$MQ_T_REFRESHES"\n'
           'want=$(git -C "$GOV_STORE_REPO" rev-parse "$GOV_STORE_REF")\n'
           'cur=$(readlink -f "$GOV_STORE_LINK")\n'
           'case "$cur" in *-a) next=$GOV_STORE_LINK-b ;; *) next=$GOV_STORE_LINK-a ;; esac\n'
           'git -C "$next" checkout -q --force --detach "$want" || exit 2\n'
           'mkdir -p "$next/.gov-runtime" && echo "refreshed at $want" > "$next/.gov-runtime/store.db"\n'
           'ln -sfn "$next" "$GOV_STORE_LINK.tmp" && mv -T "$GOV_STORE_LINK.tmp" "$GOV_STORE_LINK"\n')
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
def w(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    root = commit(repo, {"tests/test_ok.py": OK, ".gitignore": ".gov-runtime/\n__pycache__/\n"}, "root")
    git(repo, "checkout", "-q", "-b", "w2/integrate")
    git(repo, "checkout", "-q", "main")
    files = {}
    for name, text in (("select.py", SELECT), ("prepare.py", PREPARE), ("seeder.py", SEEDER), ("refresh.sh", REFRESH)):
        files[name] = tmp_path / name
        files[name].write_text(text)
    link = tmp_path / "wt" / "store"
    link.parent.mkdir()
    for half in ("a", "b"):
        git(repo, "worktree", "add", "-q", "--detach", str(link) + "-" + half, root)
        (Path(str(link) + "-" + half) / ".gov-runtime").mkdir()
        (Path(str(link) + "-" + half) / ".gov-runtime/store.db").write_text(f"built at {root}")
    link.symlink_to(str(link) + "-a")
    env = {"MQ_T_PREPARES": tmp_path / "prepares.jsonl", "MQ_T_SEEDS": tmp_path / "seeds.jsonl",
           "MQ_T_REFRESHES": tmp_path / "refreshes.txt", "MERGE_QUEUE_SEEDER": files["seeder.py"],
           "MERGE_QUEUE_REFRESH": files["refresh.sh"]}
    for k, v in env.items():
        monkeypatch.setenv(k, str(v))
    return SimpleNamespace(tmp=tmp_path, repo=repo, root=root, q=tmp_path / "q", link=link, f=files)


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


def run(w, *extra, store=True):
    return tool("run", "--repo", w.repo, "--queue", w.q, "--work", w.tmp / "work", "--test-cmd", PYTEST,
                "--select-cmd", f"{sys.executable} {w.f['select.py']}",
                "--prepare-cmd", f"{sys.executable} {w.f['prepare.py']}", "--rounds", "1",
                *(["--integration-store", w.link] if store else []), *extra)


def store_at(w, commit_id):
    """The integration store's ready half moved to `commit_id`, built there (as a refresh leaves it)."""
    tree = w.link.resolve()
    git(tree, "checkout", "-q", "--force", "--detach", commit_id)
    (tree / ".gov-runtime/store.db").write_text(f"built at {commit_id}")


def head(w):
    return git(w.repo, "rev-parse", "w2/integrate")


def record(w):
    return json.loads((w.q / "records" / f"{head(w)[:12]}.json").read_text())


def lines(path):
    return [json.loads(x) for x in Path(path).read_text().splitlines()] if Path(path).exists() else []


def prepares(w):
    return lines(w.tmp / "prepares.jsonl")


def refreshes(w, wait=0.0):
    p = w.tmp / "refreshes.txt"
    end = time.time() + wait
    while wait and not p.exists() and time.time() < end:
        time.sleep(0.1)
    return len(p.read_text().split()) if p.exists() else 0


def landed_ticket(w):
    """A ticket whose merge is not its approved commit's code (integrate moved since it started), so the run is
    not skipped and the merged clone is rebuilt at the landed commit."""
    later = on_integrate(w, {"src/later.py": "X = 1\n"}, "an unrelated merge")
    store_at(w, later)
    enter(w, "A", ticket(w, "A", {"tests/test_a.py": OK}))
    return later


# ---- the seed ----------------------------------------------------------------------------------------------------

def test_a_clone_without_a_store_is_seeded_before_its_first_rebuild(w):
    landed_ticket(w)
    r = run(w)
    assert r.returncode == 0, r.stdout + r.stderr
    seeds = lines(w.tmp / "seeds.jsonl")
    assert seeds[0][0] == "seed" and seeds[0][1].endswith("/merged") and \
        seeds[0][seeds[0].index("--base") + 1] == str(w.link)
    assert "seed of merged from" in r.stdout and ": seeded (copy)" in r.stdout
    first = prepares(w)[0]
    assert first[0].endswith("/merged") and first[2] == []  # a copy seed: the rebuild itself takes no argument


def test_in_product_mode_the_rebuild_gets_the_products_seed(w, monkeypatch):
    monkeypatch.setenv("MQ_T_PRODUCT", "1")
    landed_ticket(w)
    r = run(w)
    assert r.returncode == 0, r.stdout + r.stderr
    first = prepares(w)[0]
    assert first[0].endswith("/merged") and first[2] == ["--seed", str(w.link) + "-a"]  # the ready half then


def test_a_seeder_that_fails_leaves_the_normal_rebuild_named(w, monkeypatch):
    monkeypatch.setenv("MQ_T_SEED_FAIL", "1")
    landed_ticket(w)
    r = run(w)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "seed of merged not applied" in r.stdout and "a normal rebuild" in r.stdout
    assert prepares(w)[0][2] == []


def test_without_the_integration_store_nothing_is_seeded(w):
    landed_ticket(w)
    assert run(w, store=False).returncode == 0
    assert not lines(w.tmp / "seeds.jsonl") and refreshes(w) == 0


# ---- the promotion -----------------------------------------------------------------------------------------------

def test_the_landed_result_is_promoted_into_the_standby_half_and_the_link_moves(w):
    landed_ticket(w)
    r = run(w)
    assert r.returncode == 0, r.stdout + r.stderr
    new = head(w)
    standby = Path(str(w.link) + "-b")
    assert w.link.resolve() == standby.resolve() and git(standby, "rev-parse", "HEAD") == new
    assert "integration store promoted" in r.stdout
    seed = lines(w.tmp / "seeds.jsonl")[-1]
    assert seed[1] == str(standby) and "--replace" in seed and seed[seed.index("--base") + 1].endswith("/merged")
    assert prepares(w)[-1][:2] == [str(standby), new]  # the rebuild that finds nothing to embed, at the landed head
    assert refreshes(w, wait=1.0) == 0  # the integration store's own refresh not needed


def test_a_skipped_run_is_not_promoted_and_the_normal_refresh_runs(w):
    enter(w, "A", ticket(w, "A", {"tests/test_a.py": OK}))  # its merge is its own code: the run is skipped
    r = run(w)
    assert r.returncode == 0 and "run skipped" in r.stdout, r.stdout + r.stderr
    assert "integration store not promoted: the merged clone's stores were not rebuilt" in r.stdout
    assert refreshes(w, wait=20.0) == 1


def test_a_held_store_lock_is_not_waited_for_and_the_refresh_runs(w):
    import fcntl
    landed_ticket(w)
    with open(str(w.link) + ".lock", "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        r = run(w)
    assert r.returncode == 0 and "a refresh holds the integration store's lock" in r.stdout, r.stdout
    assert w.link.resolve().name == "store-a" and refreshes(w, wait=20.0) == 1


# ---- the head without the batch: never rebuilt ---------------------------------------------------------------------

def no_rebuild_but_the_merged_and_the_promotion(w, base=None):
    """No prepare ran in an alt clone, nor in the tree the head without the batch was re-run in."""
    trees = [Path(p[0]).name for p in prepares(w)]
    assert "alt" not in trees or base, trees
    return trees


def test_a_red_the_baseline_had_is_judged_on_the_integration_stores_tree_without_a_rebuild(w):
    base = on_integrate(w, {"tests/test_known.py": ASSERT_RED}, "a known red at the nightly")
    later = on_integrate(w, {"src/later.py": "X = 1\n"}, "a later merge")
    store_at(w, later)
    enter(w, "A", ticket(w, "A", {"tests/test_a.py": OK}))
    r = run(w, "--base", base)
    assert r.returncode == 0, r.stdout + r.stderr
    assert record(w)["unowned"] == ["tests/test_known.py::test_known"]
    assert "the head without the batch: the integration store's tree" in r.stdout
    trees = [Path(p[0]).name for p in prepares(w)]
    assert trees.count("alt") == 1 and set(trees) <= {"merged", "alt", "store-b"}  # alt only at the baseline
    assert [p[1] for p in prepares(w) if Path(p[0]).name == "alt"] == [base]


def test_a_red_since_the_baseline_seen_on_the_stores_tree_stops_and_blames_nobody(w):
    base = on_integrate(w, {"src/later.py": "X = 1\n"}, "the nightly's head")
    since = on_integrate(w, {"tests/test_since.py": ASSERT_RED.replace("known", "since")}, "a merge after it")
    store_at(w, since)
    old = head(w)
    enter(w, "A", ticket(w, "A", {"tests/test_a.py": OK}))
    r = run(w, "--base", base)
    assert r.returncode == 4 and head(w) == old, r.stdout + r.stderr
    assert "red since the baseline" in r.stderr and (w.q / "approved/A.json").exists()
    assert [Path(p[0]).name for p in prepares(w)].count("alt") == 1


def test_a_baseline_red_the_batch_breaks_again_is_the_batchs_on_the_stores_tree(w):
    known = "import sys, pathlib\nsys.path.insert(0, str(pathlib.Path(__file__).parents[1] / 'src'))\nimport k\n\n\n" \
            "def test_known():\n    assert k.V == 1\n"
    base = on_integrate(w, {"src/k.py": "V = 0\n", "tests/test_known.py": known}, "a known red at the nightly")
    fixed = on_integrate(w, {"src/k.py": "V = 1\n"}, "a later merge fixes it")
    c = ticket(w, "A", {"src/k.py": "V = 0\n"}, start=fixed)
    store_at(w, on_integrate(w, {"src/other.py": "Y = 1\n"}, "an unrelated merge"))
    old = head(w)
    enter(w, "A", c)
    r = run(w, "--base", base)
    assert r.returncode == 3 and head(w) == old, r.stdout + r.stderr
    assert json.loads((w.q / "ejected/A.json").read_text())["failing"] == ["tests/test_known.py::test_known"]
    assert "the head without the batch: the integration store's tree" in r.stdout


def nightly(w, h, junit, run_extra=""):
    log, junits = w.tmp / "nightly", w.tmp / "junit"
    (log / "20990101-0400").mkdir(parents=True)
    (junits / "20990101-0400").mkdir(parents=True)
    (log / "20990101-0400/run.txt").write_text(f"x nightly\nhead {h[:12]}\n{run_extra}verdict: green\n")
    (junits / "20990101-0400/parallel.xml").write_text(junit)
    return ["--nightly-log", log, "--nightly-junit", junits]


def test_the_nightly_of_the_head_answers_green_without_any_run_there(w):
    known = "import sys, pathlib\nsys.path.insert(0, str(pathlib.Path(__file__).parents[1] / 'src'))\nimport k\n\n\n" \
            "def test_known():\n    assert k.V == 1\n"
    base = on_integrate(w, {"src/k.py": "V = 0\n", "tests/test_known.py": known}, "a known red at the nightly")
    fixed = on_integrate(w, {"src/k.py": "V = 1\n"}, "a later merge fixes it")
    c = ticket(w, "A", {"src/k.py": "V = 0\n"}, start=fixed)
    h = on_integrate(w, {"src/other.py": "Y = 1\n"}, "an unrelated merge")
    enter(w, "A", c)  # the store is left at the root: a run there would have to refresh it first
    junit = ('<testsuite><testcase classname="tests.test_known" name="test_known"/>'
             '<testcase classname="tests.test_ok" name="test_ok"/></testsuite>')
    r = run(w, "--base", base, *nightly(w, h, junit))
    assert r.returncode == 3, r.stdout + r.stderr
    assert "green on the head without the batch in that head's own nightly (no run)" in r.stdout
    assert "the integration store's tree" not in r.stdout and refreshes(w) == 0


def test_the_nightly_of_the_head_red_alone_stops_without_a_run_but_never_clears_by_itself(w):
    base = on_integrate(w, {"src/later.py": "X = 1\n"}, "the nightly's head")
    h = on_integrate(w, {"tests/test_since.py": ASSERT_RED.replace("known", "since")}, "a merge after it")
    enter(w, "A", ticket(w, "A", {"tests/test_a.py": OK}))
    junit = ('<testsuite><testcase classname="tests.test_since" name="test_since">'
             '<failure message="assert False">x</failure></testcase></testsuite>')
    r = run(w, "--base", base, *nightly(w, h, junit, "red-alone tests/test_since.py::test_since: 1 failed\n"))
    assert r.returncode == 4 and "red since the baseline" in r.stderr, r.stdout + r.stderr
    assert "red alone on the head without the batch in that head's own nightly" in r.stdout
    assert "the integration store's tree" not in r.stdout


def test_a_store_behind_the_head_is_refreshed_first_never_a_clone_rebuilt(w):
    base = on_integrate(w, {"tests/test_known.py": ASSERT_RED}, "a known red at the nightly")
    on_integrate(w, {"src/later.py": "X = 1\n"}, "a later merge")  # the store stays at the root
    enter(w, "A", ticket(w, "A", {"tests/test_a.py": OK}))
    r = run(w, "--base", base)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "its normal refresh first" in r.stdout and refreshes(w) >= 1
    assert record(w)["unowned"] == ["tests/test_known.py::test_known"]
    assert [Path(p[0]).name for p in prepares(w)].count("alt") == 1  # the baseline's, nothing at the head


def test_without_base_the_trace_runs_on_the_stores_tree_and_a_test_that_changes_it_is_undone(w):
    since = ("import pathlib\n\n\ndef test_since():\n"
             "    (pathlib.Path(__file__).parent / 'test_ok.py').write_text('changed by a test')\n"
             "    assert False\n")
    h = on_integrate(w, {"tests/test_since.py": since}, "a red merge")
    store_at(w, h)
    enter(w, "A", ticket(w, "A", {"tests/test_a.py": OK}))
    r = run(w)
    assert r.returncode == 0, r.stdout + r.stderr
    assert record(w)["unowned"] == ["tests/test_since.py::test_since"]
    assert "alt" not in [Path(p[0]).name for p in prepares(w)]
    assert "a re-run changed the integration store's tree" in r.stdout
    tree = Path(str(w.link) + "-a")
    assert git(tree, "status", "--porcelain") == "" and git(tree, "rev-parse", "HEAD") == h


def test_junit_cases_names_the_passed_and_leaves_out_the_skipped(tmp_path):
    x = tmp_path / "r.xml"
    x.write_text('<testsuite><testcase classname="t" name="a"/><testcase classname="t" name="b">'
                 '<skipped/></testcase><testcase classname="t" name="c"><failure message="assert 0"/></testcase>'
                 '</testsuite>')
    assert mq.passing_cases([x], tmp_path, ["t.py"]) == ["t.py::a"]
    assert mq.failing_cases([x], tmp_path, ["t.py"]) == [("t.py::c", {"AssertionError"})]
