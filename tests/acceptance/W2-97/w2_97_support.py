"""Support code for the W2-97 acceptance tests (DAEO-wq2b; standard library only, pytest in the stubs).

W2-97 (DEC-959 item 1, DEC-979 item 3, DEC-968, DEC-953): the local merge queue. Each approved ticket's commit is
merged (``--no-ff``) onto the integration branch's head in a clean clone, the merged result is tested once (or the
run is skipped, with its reason, when the code is what the lead tested), and the branch moves, by fast-forward, to
the very merge commit tested, only on green. A red ejects the ticket that caused it.

How the tests run (README, "How the suite runs the tool"):

- **The tool under test** is ``governance/project/orchestration/tools/merge_queue.py`` of the repository these tests
  sit in, run with ``sys.executable`` as a subprocess (DEC-732): from the ticket's worktree, that worktree's copy.
- **Public interface only:** the exit code; the planted integration branch's head and its parents; the queue
  folder's files (``requested/``, ``approved/``, ``ejected/``, ``landed/``, ``records/``) and their stated fields;
  the stubs' own logs of how often, where and on which commit they ran.
- **Stand-ins only:** every repository is planted from scratch under pytest's ``tmp_path``: ``main`` and
  ``w2/integrate`` (checked out in the planted repository's own worktree, as in production), ticket branches whose
  commits carry ``Task:`` trailers. The test command is a stub that logs each call, then runs
  ``python3 -m pytest -q -p no:cacheprovider`` over the planted test files; the selection is a stub that prints the
  selection's JSON; the prepare command is ``true`` (or ``false``). ``--work`` and ``--queue`` are always under
  ``tmp_path``; ``HOME`` and ``TMPDIR`` are folders of ``tmp_path``. No test touches this repository's branches, its
  stores, ``~/gov-os-runs/`` or the network.
"""

from __future__ import annotations

import json
import os
import shlex
import site
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
TOOL = REPO_ROOT / "governance/project/orchestration/tools/merge_queue.py"

INTEGRATION = "w2/integrate"
NAME, EMAIL = "W2-97 tests", "w2-97@example.invalid"
RUN_TIMEOUT_S = 600

# What would leak the outer pytest run (or this worktree's code) into the queue and its stubs.
LEAKY = ("PYTEST_ADDOPTS", "PYTEST_PLUGINS", "PYTEST_CURRENT_TEST", "PYTHONPATH")


def clean_env(tmp):
    env = {k: v for k, v in os.environ.items()
           if k not in LEAKY and not k.startswith("PYTEST_XDIST") and not k.startswith("GIT_")}
    home, tmpdir = tmp / "home", tmp / "tmp"
    home.mkdir(exist_ok=True)
    tmpdir.mkdir(exist_ok=True)
    # HOME is empty (no global git identity, nothing of ~/gov-os-runs/); pytest stays importable from the user site.
    env.update(HOME=str(home), TMPDIR=str(tmpdir), PYTHONUSERBASE=site.getuserbase(), GIT_CONFIG_NOSYSTEM="1",
               LC_ALL="C")
    return env


# --------------------------------------------------------------------------
# The planted files
# --------------------------------------------------------------------------

def reads_ok(name):
    """A planted test that is green while ``app/<name>.txt`` holds ``ok``."""
    return ("from pathlib import Path\n\nROOT = Path(__file__).resolve().parents[1]\n\n\n"
            f"def test_{name}():\n    assert (ROOT / 'app/{name}.txt').read_text() == 'ok\\n'\n")


def always_red(name):
    return f"def test_{name}():\n    assert False, 'red on every head'\n"


def red_once(name, marker):
    """Red on its first run anywhere, green after: a flaky case (the marker lives outside every checkout)."""
    return ("from pathlib import Path\n\n"
            f"MARKER = Path({str(marker)!r})\n\n\n"
            f"def test_{name}():\n"
            "    if not MARKER.exists():\n"
            "        MARKER.write_text('ran')\n"
            "        assert False, 'red on its first run only'\n")


def red_if_any(name, rels):
    """Red while any of ``rels`` exists in the checkout."""
    listed = ", ".join(repr(r) for r in rels)
    return ("from pathlib import Path\n\nROOT = Path(__file__).resolve().parents[1]\n\n\n"
            f"def test_{name}():\n    present = [r for r in ({listed},) if (ROOT / r).exists()]\n"
            "    assert not present, present\n")


BASE = {
    "pytest.ini": "[pytest]\n",
    "app/a.txt": "ok\n",
    "app/b.txt": "ok\n",
    "app/notes.txt": "base\n",
    "tests/test_a.py": reads_ok("a"),
    "tests/test_b.py": reads_ok("b"),
}


# --------------------------------------------------------------------------
# The stubs (written into tmp_path/stubs; each reads the JSON file beside it)
# --------------------------------------------------------------------------

STUB_TEST = r'''"""W2-97 stand-in test command: logs each call, then runs pytest over the planted tests in the current folder."""
import json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve()
CFG = json.loads(HERE.with_suffix(".json").read_text())
ARGS = sys.argv[1:]
CWD = os.getcwd()
CLEAN = {k: v for k, v in os.environ.items()
         if not k.startswith("PYTEST_") and not k.startswith("GIT_") and k != "PYTHONPATH"}


def git(*a, cwd):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, env=CLEAN)
    return r.stdout.strip() if r.returncode == 0 else None


positional = [a for a in ARGS if not a.startswith("-")]
alone = len(positional) == 1 and "::" in positional[0]
log = Path(CFG["log"])
earlier = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
entry = {"argv": ARGS, "targets": positional, "cwd": CWD, "head": git("rev-parse", "HEAD", cwd=CWD),
         "tree": git("rev-parse", "HEAD^{tree}", cwd=CWD), "alone": alone, "time": time.time()}
with log.open("a") as f:
    f.write(json.dumps(entry) + "\n")

if CFG.get("incomplete"):
    sys.exit(2)  # no JUnit file written: the run did not complete

block = CFG.get("block")
if block and not alone:
    Path(block["started"]).write_text("started")
    deadline = time.time() + 120
    while not Path(block["release"]).exists() and time.time() < deadline:
        time.sleep(0.1)

move = CFG.get("move")
if move and not alone and not any(not e["alone"] for e in earlier):
    # The integration branch moves while the candidate is under test: a commit lands on it in the planted repository.
    repo = move["repo"]
    (Path(repo) / move["path"]).write_text(move["text"])
    subprocess.run(["git", "-C", repo, "add", "-A"], check=True, env=CLEAN)
    subprocess.run(["git", "-C", repo, "commit", "-q", "-m", move["subject"], "-m", "Task: W2-00"],
                   check=True, env=CLEAN)

done = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *ARGS], cwd=CWD, env=CLEAN)
sys.exit(done.returncode)
'''

STUB_SELECT = r'''"""W2-97 stand-in selection: prints the selection's JSON object (select_tests.py's form) and logs each call."""
import json, os, sys
from pathlib import Path

HERE = Path(__file__).resolve()
CFG = json.loads(HERE.with_suffix(".json").read_text())
ARGS = sys.argv[1:]
with Path(CFG["log"]).open("a") as f:
    f.write(json.dumps({"argv": ARGS, "cwd": os.getcwd()}) + "\n")
if CFG.get("refuse"):
    print(json.dumps({"scope": "refused", "why": [{"reason": "stand-in refusal"}], "note": "W2-97 tests"}))
    sys.exit(2)
ticket = ARGS[1] if len(ARGS) > 1 else ""
targets = CFG.get("targets", {}).get(ticket, CFG.get("default", ["tests"]))
print(json.dumps({"scope": "scoped", "why_full": [], "core_changed": CFG.get("core_changed", []),
                  "unplaced": CFG.get("unplaced", []), "base": None, "head": None, "governance_left_out": [],
                  "changed": [], "selected": [{"target": t, "why": [{"reason": "OWN"}]} for t in targets],
                  "pytest_options": [], "ignore": [], "deselect": [], "per_test_timeout": None}, indent=1))
'''


# --------------------------------------------------------------------------
# The planted repository and its queue
# --------------------------------------------------------------------------

class Planted:
    """A planted repository with ``main`` and ``w2/integrate``, its queue folder, its work folder and its stubs."""

    def __init__(self, tmp):
        self.tmp = Path(tmp)
        self.repo = self.tmp / "repo"
        self.queue = self.tmp / "queue"
        self.work = self.tmp / "work"
        self.stubs = self.tmp / "stubs"
        self.stubs.mkdir()
        self.env = clean_env(self.tmp)
        self.test_stub = self.stubs / "stub_test.py"
        self.select_stub = self.stubs / "stub_select.py"
        self.test_stub.write_text(STUB_TEST)
        self.select_stub.write_text(STUB_SELECT)
        self.test_log = self.stubs / "test-calls.jsonl"
        self.select_log = self.stubs / "select-calls.jsonl"
        self.configure_tests()
        self.configure_select()
        self.h0 = self.main0 = None

    # ---- git

    def git(self, *args, cwd=None, extra_env=None, input=None):
        env = dict(self.env, **(extra_env or {}))
        done = subprocess.run(["git", "-C", str(cwd or self.repo), *args], capture_output=True, text=True,
                              env=env, input=input)
        assert done.returncode == 0, f"git {' '.join(args)} failed:\n{done.stderr}"
        return done.stdout.strip()

    def rev(self, ref):
        return self.git("rev-parse", "--verify", ref)

    def head(self):
        return self.rev(f"refs/heads/{INTEGRATION}")

    def parents(self, commit):
        return self.git("rev-list", "--parents", "-n", "1", commit).split()[1:]

    def is_ancestor(self, older, newer):
        env = dict(self.env)
        return subprocess.run(["git", "-C", str(self.repo), "merge-base", "--is-ancestor", older, newer],
                              env=env).returncode == 0

    def files_at(self, commit):
        return set(self.git("ls-tree", "-r", "--name-only", commit).splitlines())

    # ---- planting

    def plant(self, extra=None):
        """``main`` and ``w2/integrate`` at one base commit H0; ``w2/integrate`` checked out in the worktree."""
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", NAME)
        self.git("config", "user.email", EMAIL)
        self.git("config", "commit.gpgsign", "false")
        for rel, text in {**BASE, **(extra or {})}.items():
            path = self.repo / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "base", "-m", "Task: W2-00")
        self.h0 = self.main0 = self.rev("HEAD")
        self.git("checkout", "-q", "-b", INTEGRATION)
        return self.h0

    def integrate_commit(self, files, subject="a commit on the integration branch"):
        """A commit on ``w2/integrate`` in its own worktree (the planted repository's)."""
        for rel, text in files.items():
            path = self.repo / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", subject, "-m", "Task: W2-00")
        return self.head()

    def code_moves_on(self):
        """H1: a code change on the integration branch after the tickets were cut (so no merge equals a lead's tree)."""
        return self.integrate_commit({"app/notes.txt": "integrate\n"}, "a code change on the integration head")

    def commit_on(self, branch, parent, files, subject, task):
        """One commit on ``branch`` (no checkout): ``files`` maps a path to its text, or to None to remove it."""
        index = self.tmp / "plumbing.index"
        env = {"GIT_INDEX_FILE": str(index)}
        self.git("read-tree", parent, extra_env=env)
        for rel, text in files.items():
            if text is None:
                self.git("update-index", "--force-remove", rel, extra_env=env)
            else:
                blob = self.git("hash-object", "-w", "--stdin", input=text)
                self.git("update-index", "--add", "--cacheinfo", f"100644,{blob},{rel}", extra_env=env)
        tree = self.git("write-tree", extra_env=env)
        index.unlink()
        commit = self.git("commit-tree", tree, "-p", parent, "-m", f"{subject}\n\nTask: {task}\n")
        self.git("update-ref", f"refs/heads/{branch}", commit)
        return commit

    def ticket(self, number, files, parent=None, before=None):
        """A ticket branch ``w2/W2-<number>`` cut from ``parent`` (default H0), task ``DAEO-t<number>``. ``before``:
        commits (files, task) made on the branch first, e.g. another ticket's work."""
        name, task, branch = f"W2-{number}", f"DAEO-t{number}", f"w2/W2-{number}"
        tip = parent or self.h0
        for other_files, other_task in before or ():
            tip = self.commit_on(branch, tip, other_files, f"work of {other_task}", other_task)
        commit = self.commit_on(branch, tip, files, f"{name}: its change", task)
        return Ticket(name, task, branch, commit)

    # ---- stubs

    def configure_tests(self, **cfg):
        self.test_stub.with_suffix(".json").write_text(json.dumps({"log": str(self.test_log), **cfg}))

    def configure_select(self, **cfg):
        self.select_stub.with_suffix(".json").write_text(json.dumps({"log": str(self.select_log), **cfg}))

    def test_calls(self):
        if not self.test_log.exists():
            return []
        return [json.loads(line) for line in self.test_log.read_text().splitlines()]

    def runs(self):
        """The test command's calls on a batch (not a single case re-run alone)."""
        return [c for c in self.test_calls() if not c["alone"]]

    # ---- the tool

    def tool(self, *args, timeout=RUN_TIMEOUT_S):
        assert TOOL.is_file(), f"the merge queue does not exist on this tree: {TOOL} (W2-97 not built)"
        return subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True, env=self.env,
                              cwd=str(self.tmp), timeout=timeout)

    def enqueue(self, t, commit=None):
        return self.tool("enqueue", "--queue", str(self.queue), "--ticket", t.name, "--task", t.task,
                         "--branch", t.branch, "--commit", commit or t.commit)

    def approve(self, name, by="CTO"):
        return self.tool("approve", "--queue", str(self.queue), "--ticket", name, "--by", by)

    def submit(self, *tickets):
        for t in tickets:
            done = self.enqueue(t)
            assert done.returncode == 0, f"enqueue {t.name}: exit {done.returncode}\n{done.stderr}"
            done = self.approve(t.name)
            assert done.returncode == 0, f"approve {t.name}: exit {done.returncode}\n{done.stderr}"

    def run_args(self, prepare="true", rounds=None):
        args = ["run", "--repo", str(self.repo), "--queue", str(self.queue), "--integration", INTEGRATION,
                "--work", str(self.work),
                "--test-cmd", f"{shlex.quote(sys.executable)} {shlex.quote(str(self.test_stub))}",
                "--select-cmd", f"{shlex.quote(sys.executable)} {shlex.quote(str(self.select_stub))}",
                "--prepare-cmd", prepare]
        if rounds is not None:
            args += ["--rounds", str(rounds)]
        return args

    def run(self, prepare="true", rounds=None):
        return self.tool(*self.run_args(prepare, rounds))

    def start_run(self):
        assert TOOL.is_file(), f"the merge queue does not exist on this tree: {TOOL} (W2-97 not built)"
        return subprocess.Popen([sys.executable, str(TOOL), *self.run_args()], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, env=self.env, cwd=str(self.tmp))

    # ---- the queue folder

    def entry(self, folder, name):
        path = self.queue / folder / f"{name}.json"
        return json.loads(path.read_text()) if path.is_file() else None

    def names(self, folder):
        return sorted(p.stem for p in (self.queue / folder).glob("*.json"))

    def record(self, head):
        path = self.queue / "records" / f"{head[:12]}.json"
        assert path.is_file(), f"no record {path.name} for the new head; records: {self.names('records')}"
        return json.loads(path.read_text())

    def record_path(self, landed):
        """The record a landed file points at, absolute or relative to the queue folder."""
        p = Path(landed["record"])
        return p if p.is_absolute() else self.queue / p


class Ticket:
    def __init__(self, name, task, branch, commit):
        self.name, self.task, self.branch, self.commit = name, task, branch, commit


# --------------------------------------------------------------------------
# Shared checks
# --------------------------------------------------------------------------

def said(done):
    return f"exit {done.returncode}\nstdout:\n{done.stdout[-3000:]}\nstderr:\n{done.stderr[-3000:]}"


def assert_main_unmoved(q):
    assert q.rev("refs/heads/main") == q.main0, "main was moved: the queue must touch no branch but the integration"


def assert_ejected(q, t, old_head, test_name=None):
    """``t`` is in ``ejected/`` with its fields; with ``test_name``, a failing id names it and the run's log folder
    (absolute, present) and the head tested on are given."""
    e = q.entry("ejected", t.name)
    assert e is not None, f"{t.name} is not ejected; ejected: {q.names('ejected')}, landed: {q.names('landed')}"
    assert (e["ticket"], e["task"], e["branch"], e["commit"]) == (t.name, t.task, t.branch, t.commit), e
    assert e["reason"], e
    assert q.entry("approved", t.name) is None, f"{t.name} was ejected but its approval was kept"
    assert q.entry("landed", t.name) is None, f"{t.name} is both ejected and landed"
    if test_name is not None:
        assert any(test_name in f for f in e["failing"]), f"no failing id names {test_name}: {e['failing']}"
        log = Path(e["log"])
        assert log.is_absolute() and log.is_dir(), f"the ejection's log folder is not an absolute folder: {e['log']}"
        assert e["tested_on"] == old_head, f"tested_on {e['tested_on']} is not the head tested on {old_head}"
    return e


def assert_landed_as(q, t, merge):
    """``t`` landed through ``merge``: a merge commit whose second parent is ``t``'s approved commit."""
    landed = q.entry("landed", t.name)
    assert landed is not None, f"{t.name} did not land; landed: {q.names('landed')}, ejected: {q.names('ejected')}"
    assert landed["merge"] == merge, f"{t.name}'s landed merge {landed['merge']} is not {merge}"
    assert q.parents(merge)[1:] == [t.commit], f"{merge[:12]}'s second parent is not {t.name}'s approved commit"
    assert q.record_path(landed).is_file(), f"{t.name}'s landed file points at no record: {landed['record']}"
    assert q.entry("approved", t.name) is None, f"{t.name} landed but its approval was kept"
    return landed


def wait_for(path, seconds=90):
    deadline = time.time() + seconds
    while not Path(path).exists():
        assert time.time() < deadline, f"{path} did not appear in {seconds} s"
        time.sleep(0.1)
