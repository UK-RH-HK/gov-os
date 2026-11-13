"""The independent review's finding R4-1 (DEC-136): the nightly's ``git bisect run`` gives each step's test exactly
the git environment the run that found the red gave it (DEC-970, W2-05's line: the nightly's bisect pinned as the
close's test runs are), KPI success 1 ("every check, test helper and command that runs git in another folder clears
the inherited GIT_* variables", W2-M161) and the failure KPI, under P-1 (DEC-804 item 3: a program that may start
git elsewhere gets no ``GIT_*`` of its caller).

``git bisect run`` itself puts ``GIT_DIR`` (the night clone's git directory), ``GIT_EXEC_PATH`` and ``GIT_PREFIX``
into the command it starts (measured with git 2.43.0: README, "The review's R4-1"). A test that runs git in a
folder of its own with the environment it inherits, as an honest test does, then acts on the clone and, through it,
on the project.

What a case builds (once for the three, ``night``): a throwaway project from scratch under the case's temporary
folder. Its main tree is on ``work``; ``main`` is checked out nowhere and holds the person's own commit. On ``work``:
the tool's test (green), a green night's record naming that commit, a harmless commit, the culprit (the test's data
turns red), a harmless commit. The tool's test makes a git repository of its own in its temporary folder (``git
init``, two commits, a branch, a checkout, a merge) and requires its two commits there, then reads the project's
data; at each run it adds the names of the ``GIT_*`` variables it sees (never a value) and the commit it runs at
(``stage.txt``) to a file outside every repository. The nightly runs as the product runs it:
``python3 -m gov.close.nightly work --root <project> --json``, this worktree's ``src/`` (DEC-732), with no ``GIT_*``
variable of the caller. A bisect over the four commits after the green night needs at most three steps: a night
whose test has run more than ``MAX_TEST_RUNS`` times is stopped with every process it started (its bisect does not
converge), and so is one that runs past ``NIGHT_TIMEOUT_S``; the project is read after it either way.

What the cases require:

- the project's every ref, the reflog of every branch and of HEAD, its HEAD (branch and commit), its index, the
  commits reachable from its refs and reflogs, and its configuration file are as they were before the night;
- the night ends, red, and its bisect package names the culprit as the first bad commit (a commit of the project's
  history);
- each bisect step's test saw no ``GIT_*`` variable but ``GIT_CONFIG_GLOBAL``, ``GIT_CONFIG_NOSYSTEM`` and
  ``GIT_NO_LAZY_FETCH``, and the same names as the run that found the red (by name, never a value).

Each case first requires that a bisect step ran the tool's test, so that none is green for want of a bisect.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import pytest

import w2_05_support as support
from w2_05_support import skip_without

_W1_30 = str(support.ACCEPTANCE / "W1-30")
if _W1_30 not in sys.path:
    sys.path.insert(0, _W1_30)

import w1_30_support as close_support  # noqa: E402  (W1-30's public support: git, commits, the sandbox's env)

cli_support = close_support.cli_support

NIGHTLY_MODULE = "gov.close.nightly"
NIGHTLY_DIR_REL = "docs/close/nightly"
EXIT_RED, NIGHTLY_RED = 3, "NIGHTLY_RED"
NIGHT_TIMEOUT_S = 240.0
# The night runs the tool's test once in its run, once alone, and once per bisect step: a bisect over the four
# commits after the green night needs at most three. A night whose test has run more often than this is stopped:
# its bisect does not converge (README, "The review's R4-1").
MAX_TEST_RUNS = 20
POLL_S = 0.25

# The three git variables the close's test runs get (DEC-970, W2-05's line), and no other.
PINNED = ("GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM", "GIT_NO_LAZY_FETCH")

WORK, MAIN = "work", "main"
STAGE_REL, DATA_REL, TEST_REL = "stage.txt", "data.txt", "tests/test_tool.py"
TEST_CASE = "test_the_tool_builds_a_repository_of_its_own"
RED_TEST = f"{TEST_REL}::{TEST_CASE}"
BROKEN = "BROKEN"
HEAD_STAGE = "head"

# The tool's test, as the throwaway project holds it. ``@SEEN@`` is the file it adds a line to at each run.
_TOOL_TEST = '''"""The tool's test: a repository of its own in its temporary folder, with the environment it inherits."""
import json
import os
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent


def git(own, *args):
    done = subprocess.run(["git", "-c", "user.name=The tool's test", "-c", "user.email=tool@example.invalid", *args],
                          cwd=str(own), capture_output=True, text=True)
    assert done.returncode == 0, "git " + " ".join(args) + " failed in its own folder: " + done.stderr
    return done.stdout


def test_the_tool_builds_a_repository_of_its_own(tmp_path):
    stage = (HERE.parent / "stage.txt").read_text(encoding="utf-8").strip()
    seen = sorted(name for name in os.environ if name.startswith("GIT_"))
    with open(@SEEN@, "a", encoding="utf-8") as out:
        out.write(json.dumps({"stage": stage, "git": seen}) + "\\n")
    own = tmp_path / "own"
    own.mkdir()
    git(own, "init", "-q", "-b", "main")
    (own / "one.txt").write_text("one\\n", encoding="utf-8")
    git(own, "add", "one.txt")
    git(own, "commit", "-q", "-m", "one")
    git(own, "checkout", "-q", "-b", "side")
    (own / "two.txt").write_text("two\\n", encoding="utf-8")
    git(own, "add", "two.txt")
    git(own, "commit", "-q", "-m", "two")
    git(own, "checkout", "-q", "main")
    git(own, "merge", "-q", "--no-edit", "side")
    assert git(own, "rev-list", "--count", "main").strip() == "2", "its own repository does not hold its two commits"
    data = (HERE.parent / "data.txt").read_text(encoding="utf-8")
    assert "BROKEN" not in data, "the data is broken: " + data
'''


def short(text):
    """``text`` with every full commit id cut to its first 12 digits (row W2-L423)."""
    return re.sub(r"\b([0-9a-f]{12})[0-9a-f]{28}\b", r"\1", str(text))


# --------------------------------------------------------------------------
# the throwaway project
# --------------------------------------------------------------------------

class Project:
    """The throwaway project (module docstring): its root, the file its test tells, and its named commits."""

    def __init__(self, base):
        self.base = Path(base)
        self.root = self.base / "project"
        self.seen = self.base / "seen-by-the-tool-s-test.jsonl"
        self.sandbox = cli_support.make_sandbox(self.base / "sandbox")
        self._minute = 0
        self.root.mkdir(parents=True)
        close_support.git(self.root, "init", "-q", "-b", WORK)
        self.green = self._commit({
            "README.md": "# A tool\n", ".gitignore": ".gov-runtime/\n__pycache__/\n", DATA_REL: "fine\n",
            STAGE_REL: "green\n", TEST_REL: _TOOL_TEST.replace("@SEEN@", repr(str(self.seen))),
        }, "the tool's test")
        tree = close_support.git(self.root, "rev-parse", f"{self.green}^{{tree}}").strip()
        record = {"branch": WORK, "head": self.green, "tree": tree, "scope": "full", "verdict": "green",
                  "base": None, "junit_xml": [], "failures": [], "packages": []}
        self.night_record = self._commit({
            f"{NIGHTLY_DIR_REL}/NR-20261001T000000Z-{self.green[:12]}.json": json.dumps(record, indent=2) + "\n",
            STAGE_REL: "night\n"}, "a green night's record")
        # ``main``: the person's other branch, with a commit of their own, checked out nowhere during the night.
        close_support.git(self.root, "checkout", "-q", "-b", MAIN)
        self.person = self._commit({"person.md": "the person's own work on main\n"}, "the person's own work")
        close_support.git(self.root, "checkout", "-q", WORK)
        self.harmless = self._commit({STAGE_REL: "harmless one\n", "notes.md": "a note\n"}, "harmless one")
        self.culprit = self._commit({STAGE_REL: "culprit\n", DATA_REL: f"{BROKEN}\n"}, "the culprit")
        self.head = self._commit({STAGE_REL: f"{HEAD_STAGE}\n", "notes.md": "another note\n"}, "harmless two")

    def _commit(self, files, message):
        for rel, text in files.items():
            close_support.write(self.root, rel, text)
        self._minute += 1
        return close_support.commit_all(self.root, message, minute=self._minute)

    def night(self):
        """``python3 -m gov.close.nightly work --root <project> --json`` as W2-66 and W2-77 run it: this worktree's
        ``src/``, the sandbox's environment (no ``GIT_*`` variable), in a process group of its own. It is stopped,
        with every process it started, when the tool's test has run more than ``MAX_TEST_RUNS`` times or at
        ``NIGHT_TIMEOUT_S``; ``stopped`` then says why."""
        cmd = [sys.executable, "-m", NIGHTLY_MODULE, WORK, "--root", str(self.root), "--json"]
        out, err = self.base / "night.out", self.base / "night.err"
        started = time.monotonic()
        stopped = None
        with open(out, "w", encoding="utf-8") as stdout, open(err, "w", encoding="utf-8") as stderr:
            process = subprocess.Popen(cmd, cwd=str(self.root), env=close_support.sandbox_env(self.sandbox),
                                       stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, text=True,
                                       start_new_session=True)
            while process.poll() is None:
                runs = len(self.told())
                if runs > MAX_TEST_RUNS:
                    stopped = (f"stopped after the tool's test had run {runs} times: the bisect did not converge "
                               f"(a bisect over the four commits after the green night needs at most three steps)")
                elif time.monotonic() - started > NIGHT_TIMEOUT_S:
                    stopped = f"stopped: it did not end within {NIGHT_TIMEOUT_S:.0f} s"
                if stopped:
                    support.stop_group(process.pid)
                    support.reap(self.base)
                    process.wait(timeout=30)
                    break
                time.sleep(POLL_S)
        return NightRun(tuple(cmd[2:]), process.returncode, out.read_text(encoding="utf-8", errors="replace"),
                        err.read_text(encoding="utf-8", errors="replace"), stopped, time.monotonic() - started)

    def told(self):
        """Each run of the tool's test, in order: ``{"stage": <commit's stage>, "git": [GIT_* names]}``. A line
        still being written (read while the night runs) is left out."""
        if not self.seen.is_file():
            return []
        told = []
        for line in self.seen.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                told.append(json.loads(line))
            except ValueError:
                continue
        return told


@dataclass
class NightRun:
    args: tuple
    returncode: int | None
    stdout: str
    stderr: str
    stopped: str | None
    seconds: float

    def describe(self):
        return short(f"{' '.join(self.args)}\nexit code: {self.returncode}"
                     + (f" ({self.stopped})" if self.stopped else "")
                     + f", {self.seconds:.0f} s\nstdout:\n{self.stdout[-2500:]}\nstderr:\n{self.stderr[-2500:]}")


def _read(root, *args):
    """``git -C <root> <args>`` with the suite's clean git: its output, or ``error: <what git said>`` (a project
    git no longer reads as it did is a change too, never a crash of the case)."""
    done = subprocess.run([support.GIT, "-C", str(root), *args], capture_output=True, text=True,
                          env=support.clean_env(), timeout=support.CALL_TIMEOUT_S, stdin=subprocess.DEVNULL)
    if done.returncode != 0:
        return "error: " + " ".join(done.stderr.split())[:300]
    return done.stdout


def project_state(root):
    """What the night may not change in the project, read with the suite's clean git: every ref, the reflog of
    every branch and of HEAD, HEAD (the branch it names and its commit), the main tree's index, the commits
    reachable from refs and reflogs, and the configuration file of its git directory."""
    root = Path(root)
    listed = _read(root, "for-each-ref", "--format=%(refname) %(objectname)")
    refs = dict(line.partition(" ")[::2] for line in listed.splitlines()) if not listed.startswith("error:") \
        else {"(for-each-ref)": listed}
    reflogs = {name: _read(root, "reflog", "show", "--format=%H", name, "--").split()
               for name in [*sorted(n for n in refs if n.startswith("refs/heads/")), "HEAD"]}
    return {
        "refs": refs,
        "reflogs": reflogs,
        "head_names": _read(root, "symbolic-ref", "-q", "HEAD").strip(),
        "head": _read(root, "rev-parse", "HEAD").strip(),
        "index": _read(root, "ls-files", "--stage"),
        "reachable": set(_read(root, "rev-list", "--all", "--reflog").split()),
        "config": (root / ".git" / "config").read_text(encoding="utf-8", errors="replace"),
    }


def state_changes(before, after):
    """The differences between two ``project_state`` readings, each in one line (commits in 12 digits)."""
    changes = []
    for name in sorted(set(before["refs"]) | set(after["refs"])):
        old, new = before["refs"].get(name), after["refs"].get(name)
        if old != new:
            changes.append(f"ref {name}: {(old or 'absent')[:12]} -> {(new or 'absent')[:12]}")
    for name in sorted(set(before["reflogs"]) | set(after["reflogs"])):
        old, new = before["reflogs"].get(name, []), after["reflogs"].get(name, [])
        if old != new:
            changes.append(f"reflog of {name}: {len(old)} entries -> {len(new)} (newest now "
                           f"{(new[0] if new else 'none')[:12]})")
    if before["head_names"] != after["head_names"]:
        changes.append(f"HEAD names {before['head_names']!r} -> {after['head_names']!r}")
    if before["head"] != after["head"]:
        changes.append(f"HEAD {before['head'][:12]} -> {short(after['head'])[:80]}")
    if before["index"] != after["index"]:
        changes.append("the main tree's index changed" + (f" ({after['index'][:200]})"
                                                          if after["index"].startswith("error:") else ""))
    new = sorted(after["reachable"] - before["reachable"])
    if new:
        changes.append(f"{len(new)} commit(s) not of the project's history now reachable: "
                       f"{[c[:12] for c in new[:6]]}")
    if before["config"] != after["config"]:
        old_lines = [line.strip() for line in before["config"].splitlines()]
        new_lines = [line.strip() for line in after["config"].splitlines()]
        changes.append(f"its git configuration changed: lines now {[n for n in new_lines if n not in old_lines]}, "
                       f"lines gone {[o for o in old_lines if o not in new_lines]}")
    return changes


@dataclass
class Night:
    project: Project
    run: NightRun
    before: dict
    after: dict


@pytest.fixture(scope="module")
def night(tmp_path_factory):
    """One night over the throwaway project, and the project's state before and after it."""
    skip_without("git")
    base = tmp_path_factory.mktemp("w2-05-bisect-step")
    try:
        project = Project(base)
        before = project_state(project.root)
        run = project.night()
        after = project_state(project.root)
    finally:
        support.reap(base)
    return Night(project, run, before, after)


# --------------------------------------------------------------------------
# what the cases require first: a bisect step that ran the test; for the commit named, a red night that ended
# --------------------------------------------------------------------------

def red_record(night):
    """The night's record: the night ended, red (exit 3, ``NIGHTLY_RED``), and its record is there."""
    run, root = night.run, night.project.root
    assert run.stopped is None, f"the night did not end: {run.stopped}\n{run.describe()}"
    try:
        data = json.loads(run.stdout)
    except ValueError:
        data = None
    assert isinstance(data, dict), f"the nightly printed no JSON envelope\n{run.describe()}"
    error = data.get("error") or {}
    assert data.get("ok") is False and run.returncode == EXIT_RED and error.get("code") == NIGHTLY_RED, \
        f"the night is not red (exit 3, {NIGHTLY_RED})\n{run.describe()}"
    rel = (error.get("details") or {}).get("record")
    assert isinstance(rel, str) and (root / rel).is_file(), f"the red night names no record\n{run.describe()}"
    return json.loads((root / rel).read_text(encoding="utf-8"))


def bisect_steps(night):
    """The runs of the tool's test at a commit other than the head: the bisect's steps. At least one."""
    told = night.project.told()
    steps = [entry for entry in told if entry.get("stage") != HEAD_STAGE]
    assert steps, (f"no bisect step ran the tool's test (its runs, by commit: {[e.get('stage') for e in told]}); "
                   f"the case shows nothing without one\n{night.run.describe()}")
    return steps


# --------------------------------------------------------------------------
# the cases
# --------------------------------------------------------------------------

def test_the_night_s_bisect_leaves_every_branch_head_and_reflog_of_the_project_as_it_was(night):
    bisect_steps(night)
    changes = state_changes(night.before, night.after)
    assert not changes, (
        "the night's bisect changed the project (a test's git in a folder of its own acted on it"
        + (f"; the night {night.run.stopped}" if night.run.stopped else "") + "): " + "; ".join(changes))


def test_the_night_s_bisect_names_the_commit_that_made_the_test_red(night):
    bisect_steps(night)
    record = red_record(night)
    project = night.project
    packages = [p for p in record.get("packages") or [] if p.get("kind") == "bisect" and p.get("test") == RED_TEST]
    assert packages, f"the red night has no bisect package for {RED_TEST}: {short(record.get('packages'))}"
    named = packages[0].get("first_bad")
    history = set(night.before.get("reachable", ()))
    where = ("not named" if not named else "a commit of the project's history" if named in history
             else "a commit outside the project's history")
    assert named == project.culprit, (
        f"the bisect named {str(named)[:12]} ({where}) as the first bad commit, not the culprit "
        f"{project.culprit[:12]} that made {RED_TEST} red (range {short(packages[0].get('range'))})")


def test_each_bisect_step_s_test_sees_only_the_git_variables_of_the_run_that_found_the_red(night):
    steps = bisect_steps(night)
    finding = next((entry for entry in night.project.told() if entry.get("stage") == HEAD_STAGE), None)
    assert finding is not None, "the night's run did not run the tool's test at the head"
    found_with = set(finding.get("git") or [])
    assert found_with <= set(PINNED), \
        f"the run that found the red saw GIT_* variables beyond {list(PINNED)}: {sorted(found_with - set(PINNED))}"
    wrong = {}
    for step in steps:
        names = set(step.get("git") or [])
        if not names <= set(PINNED) or names != found_with:
            key = (step.get("stage"), tuple(sorted(names)))
            wrong[key] = wrong.get(key, 0) + 1
    assert not wrong, (
        f"a bisect step's test saw other GIT_* variables (by name) than the run that found the red "
        f"({sorted(found_with)}; only {list(PINNED)} may be given), in {sum(wrong.values())} of {len(steps)} "
        f"steps: " + "; ".join(f"{count} at {stage!r}: {list(names)}" for (stage, names), count in wrong.items()))
