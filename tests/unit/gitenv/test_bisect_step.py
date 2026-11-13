"""Builder test for W2-05's review finding R4-1 (DEC-970, P-1): a real ``git bisect run`` through the nightly's
``_bisect``. ``git bisect run`` exports ``GIT_DIR``, ``GIT_EXEC_PATH`` and ``GIT_PREFIX`` to its command; the
tests the step starts must not inherit them, or their git in a folder of their own acts on the night's clone and,
through it, on the project (regression evidence only; the acceptance tests are W2-05's own)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from gov.close import nightly

RUN_KEYS = ["GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM", "GIT_NO_LAZY_FETCH"]
IDENTITY = ["-c", "user.name=Night", "-c", "user.email=night@example.invalid"]

# The project's red test: it records the environment it got, then runs git in a folder of its own with that
# environment (init, commits, a branch, a checkout), and is red once ``flag.txt`` says so.
RED_TEST = '''
import json, os, shutil, subprocess, tempfile
from pathlib import Path

ID = {identity!r}


def test_red():
    with open({record!r}, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(os.environ)) + "\\n")
    own = tempfile.mkdtemp(prefix="own-repo-")
    try:
        for args in (["init", "-q"], [*ID, "commit", "-q", "--allow-empty", "-m", "own"], ["branch", "own-branch"],
                     ["checkout", "-q", "-b", "own-other"], [*ID, "commit", "-q", "--allow-empty", "-m", "own 2"]):
            subprocess.run(["git", *args], cwd=own, capture_output=True)
    finally:
        shutil.rmtree(own, ignore_errors=True)
    assert (Path(__file__).parent.parent / "flag.txt").read_text().strip() == "green"
'''


def _git(root: Path, *args: str) -> str:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    return subprocess.run(["git", "-C", str(root), *IDENTITY, *args], check=True, capture_output=True, text=True,
                          env=env).stdout


def _commit(root: Path, name: str, text: str) -> str:
    (root / name).write_text(text, encoding="utf-8")
    _git(root, "add", name)
    _git(root, "commit", "-q", "-m", f"{name}: {text.strip()}")
    return _git(root, "rev-parse", "HEAD").strip()


def _state(root: Path) -> dict:
    """The project's branches and other refs, its HEAD, its reflogs and its working tree."""
    logs = root / ".git" / "logs"
    return {"refs": _git(root, "for-each-ref", "--format=%(refname) %(objectname)"),
            "head": _git(root, "symbolic-ref", "HEAD") + _git(root, "rev-parse", "HEAD"),
            "status": _git(root, "status", "--porcelain"),
            "reflogs": {path.relative_to(logs).as_posix(): path.read_text(encoding="utf-8")
                        for path in sorted(logs.rglob("*")) if path.is_file()}}


def test_a_real_bisect_s_tests_get_only_the_run_s_environment(tmp_path, monkeypatch):
    # With the clone's ``GIT_DIR`` leaked, each step's commits move the clone's HEAD and the bisect never ends: a
    # time limit on ``bisect run`` turns that into a failure.
    real = subprocess.run
    monkeypatch.setattr(nightly.subprocess, "run", lambda args, *rest, **kwargs: real(
        args, *rest, **({"timeout": 60, **kwargs} if args[3:5] == ["bisect", "run"] else kwargs)))
    root, tree, record = tmp_path / "project", tmp_path / "night" / "tree", tmp_path / "record.jsonl"
    root.mkdir()
    _git(root, "init", "-q", "-b", "work")
    (root / "tests").mkdir()
    (root / "tests" / "test_red.py").write_text(RED_TEST.format(identity=IDENTITY, record=str(record)),
                                                encoding="utf-8")
    _git(root, "add", "tests")
    good = _commit(root, "flag.txt", "green\n")
    _git(root, "branch", "main")  # checked out nowhere
    _commit(root, "a.txt", "one\n")
    red = _commit(root, "flag.txt", "red\n")
    head = _commit(root, "b.txt", "two\n")
    _git(root, "worktree", "add", "--detach", "--force", str(tree), head)  # the night's clone, as ``night`` makes it
    before = _state(root)
    env = nightly._pytest_env(tree)
    test = "tests/test_red.py::test_red"

    # The run alone, through ``_started``: the environment every bisect step's test must get.
    assert nightly._alone(tree, test, [], 120, env) == nightly.FAILED
    alone = [json.loads(line) for line in record.read_text(encoding="utf-8").splitlines()]
    record.unlink()
    assert len(alone) == 1 and sorted(n for n in alone[0] if n.startswith("GIT_")) == RUN_KEYS

    assert nightly._bisect(tree, good, head, test, [], env) == red
    steps = [json.loads(line) for line in record.read_text(encoding="utf-8").splitlines()]
    assert steps
    for seen in steps:
        assert sorted(name for name in seen if name.startswith("GIT_")) == RUN_KEYS
        assert {k: v for k, v in seen.items() if k != "GIT_CONFIG_GLOBAL"} == \
            {k: v for k, v in alone[0].items() if k != "GIT_CONFIG_GLOBAL"}
        assert not os.path.exists(seen["GIT_CONFIG_GLOBAL"])  # the run's file, removed once the bisect ended
    assert _state(root) == before
    assert _git(root, "rev-parse", "main").strip() == good
    _git(root, "worktree", "remove", "--force", str(tree))


def test_a_step_without_the_run_s_environment_judges_no_commit_good(tmp_path):
    (tmp_path / "test_green.py").write_text("def test_green():\n    pass\n", encoding="utf-8")
    step = [sys.executable, "-c", nightly._BISECT_STEP, "test_green.py", "-q", "-p", "no:cacheprovider"]
    base = {key: value for key, value in os.environ.items() if key != nightly._STEP_ENV}
    for handed in (None, "not json", "[]", '{"PATH": 1}'):
        env = base if handed is None else {**base, nightly._STEP_ENV: handed}
        assert subprocess.run(step, cwd=tmp_path, env=env, capture_output=True).returncode == 125
    assert subprocess.run(step, cwd=tmp_path, env={**base, nightly._STEP_ENV: json.dumps(base)},
                          capture_output=True).returncode == 0
