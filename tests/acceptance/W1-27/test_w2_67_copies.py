"""W2-67, KPI 1 (I3 F9, I4 F5, I4 §2.1): per-test copies do not race git's garbage collection.

The KPI line: every per-test copy either commits with git's automatic gc switched off (``gc.auto=0``) or copies
the working files without ``.git``; a planted tree of 7,000 objects or more runs every copying case green in
parallel.

How the race happens. W1-07's ``copy_working_tree`` (the one copier that W1-07, W1-25, W1-26 and W1-27 all call)
copies the working files and commits them. Past about 6,700 loose objects that commit starts ``git gc --auto``,
which detaches and packs the loose objects away. A per-test fixture that then copies the session copy with
``shutil.copytree`` reads ``.git/objects/NN`` while gc removes it: ``shutil.Error: ... .git/objects/NN: No such
file or directory`` (the refused closes of W1-25 and W1-07).

What each case does, without editing any fixture:

- It plants a source repository of 7,200 working files (7,200 blobs). git estimates the loose objects from
  ``.git/objects/17`` alone (one 256th of them); 64 of the planted blobs are chosen to land there, so the
  estimate passes the default threshold on every run and the trigger is not left to the hash spread.
- It points the suite's own copying code at that tree: the conftest's fixture bodies are called as functions,
  and ``copy_working_tree``'s default root (the repository) is replaced by the planted one for the case's
  duration. No fixture file is changed, and nothing is copied from this repository.
- It makes two per-test copies at once (two workers, as two pytest-xdist workers would), then judges the KPI's
  either/or: a per-test copy that carries the session copy's ``.git`` is allowed only if no automatic gc started
  in the session copy. A copy that raised, or one whose objects are not all there (``git fsck``), is red too.

Each case removes its trees before it ends (DEC-898): a planted tree and its copies come to about 50,000 files.
The README (README-W2-67.md) gives each case's red reason on the head.
"""

from __future__ import annotations

import concurrent.futures
import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ACCEPTANCE = HERE.parent
for _suite in ("W1-07", "W1-25", "W1-26", "W1-27"):
    if str(ACCEPTANCE / _suite) not in sys.path:
        sys.path.insert(0, str(ACCEPTANCE / _suite))

import w1_07_support  # noqa: E402  the shared copier, copy_working_tree

PLANTED_FILES = 7200        # the KPI's "7,000 objects or more"
SAMPLE_DIR = "17"           # the one object folder ``git gc --auto`` counts to estimate the loose objects
SAMPLE_OBJECTS = 64         # > ceil(6700 / 256) = 27: over the default gc.auto threshold on every run
WORKERS = 2                 # per-test copies made at once (the brief's bound: one or two workers)
WATCH_S = 5.0               # how long a case watches a copy for an automatic gc after its copier returned
SETTLE_S = 120.0            # how long it waits for a started gc to end before it removes the trees
SOURCE_MARK = "w2-67-source-mark"     # left in the planted tree's .git: a .git copied from it carries it
SESSION_MARK = "w2-67-session-mark"   # left in a session copy's .git: a per-test copy of that .git carries it


# --------------------------------------------------------------------------
# The planted tree
# --------------------------------------------------------------------------

def _blob_id(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def plant_tree(directory):
    """A git repository of ``PLANTED_FILES`` untracked, unignored working files; ``SAMPLE_OBJECTS`` of their blobs
    land in ``.git/objects/17``. ``copy_working_tree`` lists untracked files too, so nothing is committed here."""
    directory = Path(directory)
    directory.mkdir(parents=True)
    w1_07_support.git(directory, "init", "-q", "-b", "main")
    (directory / ".gitignore").write_text(".gov-runtime/\n__pycache__/\n", encoding="utf-8")
    (directory / "README.md").write_text("# W2-67 planted source tree\n", encoding="utf-8")
    (directory / "docs").mkdir()
    (directory / "docs" / "README.md").write_text("# docs\n", encoding="utf-8")   # W1-25 writes its input here
    sampled = written = number = 0
    while written < PLANTED_FILES:
        text = f"W2-67 planted object {number}\n"
        number += 1
        if sampled < SAMPLE_OBJECTS:
            if not _blob_id(text.encode()).startswith(SAMPLE_DIR):
                continue
            sampled += 1
        folder = directory / "planted" / f"d{written // 100:03d}"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"f{written:05d}.txt").write_text(text, encoding="utf-8")
        written += 1
    (directory / ".git" / SOURCE_MARK).write_text("planted source\n", encoding="utf-8")
    return directory


@pytest.fixture(scope="module")
def planted(tmp_path_factory):
    root = tmp_path_factory.mktemp("w2-67-planted") / "source"
    plant_tree(root)
    yield root
    shutil.rmtree(root.parent, ignore_errors=True)


@pytest.fixture()
def point_copier_at(monkeypatch):
    """``point_copier_at(root)``: ``copy_working_tree`` copies ``root`` where its callers name no root."""

    def _point(root):
        monkeypatch.setattr(w1_07_support.copy_working_tree, "__defaults__", (Path(root),))

    return _point


class _Factory:
    """The one method of ``tmp_path_factory`` the session fixtures call."""

    def __init__(self, root):
        self.root = Path(root)

    def mktemp(self, name, numbered=True):
        path = self.root / name
        path.mkdir(parents=True)
        return path


def conftest_of(suite):
    """The suite's ``conftest.py``, loaded under a name of its own (its fixtures are then plain functions)."""
    path = ACCEPTANCE / suite / "conftest.py"
    name = f"w2_67_conftest_{suite.replace('-', '_')}"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        try:
            spec.loader.exec_module(module)
        except BaseException:
            del sys.modules[name]
            raise
    return sys.modules[name]


def body(fixture):
    """The function a ``@pytest.fixture`` wraps."""
    return getattr(fixture, "__wrapped__", fixture)


# --------------------------------------------------------------------------
# What a case observes
# --------------------------------------------------------------------------

def automatic_gc(repo, watch=WATCH_S):
    """What shows that ``git gc --auto`` started in ``repo`` (its pid file, a pack or a pack being written), watched
    for up to ``watch`` seconds; None when nothing did. A copy made by init, add and commit has no pack otherwise."""
    git_dir = Path(repo) / ".git"
    if not git_dir.is_dir():
        return None
    pack_dir = git_dir / "objects" / "pack"
    deadline = time.monotonic() + watch
    while True:
        signs = []
        if (git_dir / "gc.pid").exists():
            signs.append(".git/gc.pid")
        if (git_dir / "gc.log").exists():
            signs.append(".git/gc.log")
        if pack_dir.is_dir():
            packs = [path.name for path in pack_dir.iterdir()]
            if packs:
                signs.append(f"{len([p for p in packs if p.endswith('.pack')])} pack(s) in .git/objects/pack "
                             f"({len(packs)} files)")
        if signs:
            return ", ".join(signs)
        if time.monotonic() >= deadline:
            return None
        time.sleep(0.1)


def fsck(repo):
    """'' when every object HEAD reaches is in ``repo``; else git's complaint."""
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(repo), "LC_ALL": "C",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
    done = subprocess.run(["git", "-C", str(repo), "-c", "gc.auto=0", "fsck", "--connectivity-only",
                           "--no-dangling", "--no-progress"], capture_output=True, text=True, env=env)
    return "" if done.returncode == 0 else (done.stderr or done.stdout).strip()[-400:] or f"exit {done.returncode}"


def settle_and_remove(*trees):
    """Wait for an automatic gc that is still running in a tree, then remove the tree (DEC-898)."""
    for tree in trees:
        tree = Path(tree)
        deadline = time.monotonic() + SETTLE_S
        while (tree / ".git" / "gc.pid").exists() and time.monotonic() < deadline:
            time.sleep(0.2)
        shutil.rmtree(tree, ignore_errors=True)


def copies_at_once(make_copy):
    """Run ``make_copy(i)`` for ``WORKERS`` values of i at once; (the copies, the errors)."""
    copies, errors = [], []
    with concurrent.futures.ThreadPoolExecutor(WORKERS) as pool:
        futures = [pool.submit(make_copy, index) for index in range(WORKERS)]
        for future in futures:
            try:
                copies.append(Path(future.result()))
            except Exception as exc:   # shutil.Error is the race's signature
                errors.append(f"{type(exc).__name__}: {str(exc)[:600]}")
    return copies, errors


def judge_chain(label, session, make_copy, folders):
    """The KPI's either/or for a session copy and the per-test copies made from it."""
    try:
        if (session / ".git").is_dir():
            (session / ".git" / SESSION_MARK).write_text("session copy\n", encoding="utf-8")
        copies, errors = copies_at_once(make_copy)
        gc = automatic_gc(session)
        carried = [copy for copy in copies if (copy / ".git" / SESSION_MARK).exists()]
        broken = {str(copy): problem for copy in copies if (copy / ".git").is_dir() and (problem := fsck(copy))}
        races = bool(gc) and (bool(carried) or bool(errors))
        assert not errors and not broken and not races, (
            f"{label}: per-test copies of a planted tree of {PLANTED_FILES} objects race git's garbage collection.\n"
            f"- automatic gc in the session copy after its commit: {gc or 'none'}\n"
            f"- per-test copies that carry the session copy's .git: {len(carried)} of {WORKERS}\n"
            f"- copies that raised: {errors or 'none'}\n"
            f"- copies with objects missing (git fsck): {broken or 'none'}\n"
            "The KPI: every per-test copy commits with gc.auto=0, or copies the working files without .git "
            "(I3 F9, I4 F5)."
        )
    finally:
        settle_and_remove(*folders)


# --------------------------------------------------------------------------
# The chains: a session copy, then the per-test copies of it
# --------------------------------------------------------------------------

def test_w1_07_per_test_copies_of_a_7000_object_tree_do_not_race_gits_gc(planted, point_copier_at, tmp_path):
    """W1-07: ``live`` (copy_working_tree) and ``project`` (a copytree of it), from its conftest."""
    conftest = conftest_of("W1-07")
    point_copier_at(planted)
    session = body(conftest.live)(_Factory(tmp_path / "session"))
    judge_chain("W1-07 (conftest live -> project)", session,
                lambda index: body(conftest.project)(session, tmp_path / f"test-{index}"),
                [tmp_path / "session", *(tmp_path / f"test-{index}" for index in range(WORKERS))])


def test_w1_25_per_test_copies_of_a_7000_object_tree_do_not_race_gits_gc(planted, point_copier_at, tmp_path):
    """W1-25: ``live`` (copy_working_tree and its fixture tickets) and ``_copy`` (the copytree behind
    ``raw_project`` and ``project``; ``built`` and the live-session case copy the same ``live`` the same way)."""
    conftest = conftest_of("W1-25")
    point_copier_at(planted)
    session = body(conftest.live)(_Factory(tmp_path / "session"))
    judge_chain("W1-25 (conftest live -> _copy)", session,
                lambda index: conftest._copy(session, tmp_path / f"test-{index}"),
                [tmp_path / "session", *(tmp_path / f"test-{index}" for index in range(WORKERS))])


def test_w1_27_per_test_copies_of_a_7000_object_tree_do_not_race_gits_gc(planted, point_copier_at, tmp_path):
    """W1-27: ``live`` (copy_working_tree) and ``project`` (a copytree of it), from its conftest."""
    conftest = conftest_of("W1-27")
    point_copier_at(planted)
    session = body(conftest.live)(_Factory(tmp_path / "session"))
    judge_chain("W1-27 (conftest live -> project)", session,
                lambda index: body(conftest.project)(session, tmp_path / f"test-{index}"),
                [tmp_path / "session", *(tmp_path / f"test-{index}" for index in range(WORKERS))])


# --------------------------------------------------------------------------
# Per-test copies made straight from the working files (no session copy between)
# --------------------------------------------------------------------------

def _w1_26_full_project(destination):
    import w1_26_support
    return w1_26_support.FullProject(destination).root


def _w1_26_project_copy_tree(destination):
    import w1_26_support
    return w1_26_support.Project(destination, copy_tree=True).root


def _w1_27_copy_working_tree(destination):
    import w1_27_support
    return w1_27_support.copy_working_tree(destination)


@pytest.mark.parametrize("copier", [_w1_26_full_project, _w1_26_project_copy_tree, _w1_27_copy_working_tree],
                         ids=["W1-26-FullProject", "W1-26-Project-copy_tree", "W1-27-copy_working_tree-per-test"])
def test_a_per_test_copy_from_the_working_files_carries_no_copied_git_while_gc_runs(planted, point_copier_at,
                                                                                      tmp_path, copier):
    """W1-26's per-test copies and the W1-27 cases that call ``copy_working_tree`` themselves (adoption,
    held-out): each copy takes the working files, never a ``.git``. If one ever copied a ``.git`` and its commit
    started gc, it would race like the chains above. Green on the head: a guard."""
    point_copier_at(planted)
    folders = [tmp_path / f"test-{index}" for index in range(WORKERS)]
    try:
        copies, errors = copies_at_once(lambda index: copier(folders[index] / "project"))
        gc = {str(copy): sign for copy in copies if (sign := automatic_gc(copy, watch=0.0))}
        carried = [str(copy) for copy in copies if (copy / ".git" / SOURCE_MARK).exists()]
        broken = {str(copy): problem for copy in copies if (copy / ".git").is_dir() and (problem := fsck(copy))}
        assert not errors and not broken and not (gc and carried), (
            f"{copier.__name__}: copies that raised: {errors or 'none'}; with objects missing: {broken or 'none'}; "
            f"carrying a copied .git: {carried or 'none'}; automatic gc: {gc or 'none'}"
        )
    finally:
        settle_and_remove(*folders)
