"""The nightly full regression (W2-66; DEC-880 item 2 (c), DEC-852 item 3, DEC-889 items 2 b, 4 and 12).

``python3 -m gov.close.nightly <branch> --root <project> [--coverage] --json`` runs the full uncached regression
on the branch's head (a detached worktree of that commit, never the working tree) in the close's form: one
parallel run, then the serial-only cases alone, with the per-test limit, the distribution mode, the temp-folder
retention (``-o tmp_path_retention_policy=failed``, DEC-905) and JUnit XML.

Every failing test is run again alone. A red that fails alone is a P1 package, bisected with ``git bisect run``
over the commits since the last green night; a red that passes alone is a flaky candidate, never bisected. A red
that a scoped close since the last green night left out, or ran and passed, is a P1 selection miss carrying the
test map's correction. With ``--coverage`` (the weekly run) coverage.py measures which tests executed each source
file, child processes included (lens H's shim), and the record names the measured map.

The record is ``docs/close/nightly/NR-<UTC stamp>-<head12>.json`` of the project's working tree; the output is
the API-0002 envelope: ``ok: true``, exit 0, ``result.record`` on a green night; ``ok: false``, exit 3,
``error.details.record`` on a red one.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from gov.cli.errors import GovError
from gov.close import command as _close, evidence as _evidence, select as _select
from gov.close.repo import git as _git

COMMAND = "nightly"
EXIT_RED = 3
RUNTIME_DIR = ".gov-runtime/nightly"
DEFAULT_RUN_LIMIT = 7200
PRIORITY = "P1"
GREEN, RED = "green", "red"
FAILED, PASSED = "failed", "passed"


def _last_green(root: Path, head: str) -> str | None:
    """The head of the newest green night of the working tree that is an ancestor of ``head``, other than it."""
    heads = []
    for path in sorted((root / _select.NIGHTLY_REL).glob("*.json")):
        try:
            night = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(night, dict) and night.get("verdict") == GREEN and isinstance(night.get("head"), str):
            heads.append(night["head"])
    found = [h for h in (_select.full_id(root, h) for h in dict.fromkeys(heads))
             if h and h != head and _select.is_ancestor(root, h, head)]
    return _select.newest(root, found)


def _run_limit(root: Path) -> float:
    """The time limit of one test run: the path map's ``close_timeout``, as the close reads it."""
    import yaml
    try:
        settings = yaml.safe_load((root / "governance" / "project" / "path-map.yaml").read_text(encoding="utf-8"))
    except (OSError, ValueError, yaml.YAMLError):
        settings = None
    limit = (settings or {}).get(_close.TIMEOUT_KEY, DEFAULT_RUN_LIMIT) if isinstance(settings, dict) else None
    return limit if isinstance(limit, (int, float)) and not isinstance(limit, bool) and limit > 0 \
        else DEFAULT_RUN_LIMIT


def _pytest_env(tree: Path) -> dict:
    """The environment of a run on ``tree``, as the close gives its runs (DEC-500)."""
    env = {key: value for key, value in os.environ.items()
           if key not in _close._TEST_RUNNER_VARIABLES
           and (not key.startswith(_close._INTERPRETER_VARIABLES) or key in _close._INTERPRETER_PLACES)}
    env["PYTHONPATH"] = str(tree / "src")
    return env


def _alone(tree: Path, test: str, limit: list[str], run_limit: float, env: dict) -> str:
    """``passed`` when ``test`` passes run alone in a process of its own; ``failed`` otherwise."""
    path, sep, rest = test.partition("::")
    cmd = [sys.executable, "-m", "pytest", str(tree / path) + sep + rest, "--rootdir", str(tree), "-q",
           "-p", "no:cacheprovider", "--tb=line", "--no-header"] + limit
    try:
        done = _close._started(tree, cmd, env, run_limit)
    except subprocess.TimeoutExpired:
        return FAILED
    return PASSED if done.returncode == 0 else FAILED


_BISECT_STEP = """
import subprocess, sys
code = subprocess.run([sys.executable, "-m", "pytest", *sys.argv[1:]]).returncode
sys.exit(0 if code == 0 else 125 if code == 5 else 1)
"""


def _bisect(tree: Path, good: str, bad: str, test: str, limit: list[str], env: dict) -> str | None:
    """The first bad commit ``git bisect run`` finds for ``test`` between ``good`` and ``bad``; None if none."""
    path, sep, rest = test.partition("::")
    step = [sys.executable, "-c", _BISECT_STEP, path + sep + rest, "-q", "-p", "no:cacheprovider", "--no-header",
            "--rootdir", str(tree)] + limit
    git_env = {key: value for key, value in env.items() if not key.startswith("GIT_")}
    try:
        subprocess.run(["git", "-C", str(tree), "bisect", "start", bad, good], capture_output=True, text=True,
                       env=git_env, check=True)
        done = subprocess.run(["git", "-C", str(tree), "bisect", "run", *step], capture_output=True, text=True,
                              env=git_env, cwd=str(tree))
        for line in done.stdout.splitlines():
            word = line.split(" ", 1)[0]
            if line.endswith("is the first bad commit") and len(word) == 40:
                return word
        found = _git(tree, "rev-parse", "--verify", "--quiet", "refs/bisect/bad", ok=(0, 1)).strip()
        return found or None
    except (OSError, subprocess.CalledProcessError, GovError):
        return None
    finally:
        subprocess.run(["git", "-C", str(tree), "bisect", "reset"], capture_output=True, env=git_env)


def _scoped_closes(root: Path, tree: Path, since: str | None, head: str) -> list[dict]:
    """The scoped closes since the last green night: records whose evidence is scoped and whose head is after
    ``since`` and an ancestor of ``head`` (the head's records and the working tree's)."""
    from gov.tasks.tickets import frontmatter

    found = {}
    for folder in (tree, root):
        for path in sorted((folder / "docs" / "close").glob("*/CL-*.md")):
            front = frontmatter(path) or {}
            evidence = front.get(_evidence.KEY)
            if not isinstance(evidence, dict) or evidence.get("scope") != "scoped":
                continue
            at = _select.full_id(root, str(evidence.get("head") or ""))
            if not at or not _select.is_ancestor(root, at, head):
                continue
            if since and (at == since or _select.is_ancestor(root, at, since)):
                continue
            rel = path.relative_to(folder).as_posix()
            found[rel] = {"record": rel, "ticket": front.get("task"), "evidence": evidence}
    return list(found.values())


def _covers(target: str, test: str) -> bool:
    target = target.rstrip("/")
    return test == target or test.startswith((target + "/", target + "::", target + "["))


def _missed_by(close: dict, test: str) -> bool:
    """Whether a scoped close left ``test`` out or ran it and saw it pass."""
    evidence = close["evidence"]
    return not any(f.get("test") == test for f in evidence.get("failures") or [] if isinstance(f, dict))


def _suite_of_test(test: str) -> str:
    file = test.partition("::")[0]
    return _select.suite_of(file) or file


# ---------------------------------------------------------------------------
# --coverage: lens H's shim, written for the run
# ---------------------------------------------------------------------------

_SHIM = r'''
# Started in every Python process of the nightly's coverage run: measures the tree, with the running test as
# the context. A child finds its test in the environment pytest sets, or by its parents' pid files.
import atexit, os
def _gov_nightly_start():
    data = os.environ.get("GOV_NIGHTLY_COVERAGE_DATA")
    tree = os.environ.get("GOV_NIGHTLY_COVERAGE_TREE")
    if not data or not tree:
        return
    try:
        import coverage
    except ImportError:
        return
    test = None
    current = os.environ.get("PYTEST_CURRENT_TEST")
    if current:
        test = current.rsplit(" (", 1)[0]
    pids = os.path.join(data, "pids")
    pid = os.getppid()
    while test is None and pid > 1:
        try:
            with open(os.path.join(pids, str(pid)), encoding="utf-8") as handle:
                test = handle.read().strip() or None
        except OSError:
            pass
        try:
            with open(f"/proc/{pid}/stat", encoding="utf-8") as handle:
                pid = int(handle.read().rsplit(")", 1)[1].split()[1])
        except (OSError, ValueError, IndexError):
            break
    cov = coverage.Coverage(data_file=os.path.join(data, ".coverage"), data_suffix=True, config_file=False,
                            source=[tree], context=test)
    cov.start()
    def _save():
        try:
            cov.stop()
            cov.save()
        except Exception:
            pass
    atexit.register(_save)
_gov_nightly_start()
'''

_PLUGIN = r'''
# The worker's own context, switched per test; its pid file names the running test to its children.
import os
def _node(item):
    root = os.environ.get("GOV_NIGHTLY_COVERAGE_TREE", "")
    path = os.path.relpath(str(item.path), root).replace(os.sep, "/")
    return path + "".join(item.nodeid.partition("::")[1:])
def pytest_runtest_setup(item):
    try:
        import coverage
        cov = coverage.Coverage.current()
    except Exception:
        cov = None
    node = _node(item)
    if cov is not None:
        cov.switch_context(node)
    pids = os.path.join(os.environ.get("GOV_NIGHTLY_COVERAGE_DATA", ""), "pids")
    try:
        with open(os.path.join(pids, str(os.getpid())), "w", encoding="utf-8") as handle:
            handle.write(node)
    except OSError:
        pass
'''
_PLUGIN_NAME = "gov_nightly_covmap"


def _coverage_env(shim: Path, data: Path, tree: Path) -> dict:
    (shim / "sitecustomize.py").write_text(_SHIM, encoding="utf-8")
    (shim / f"{_PLUGIN_NAME}.py").write_text(_PLUGIN, encoding="utf-8")
    (data / "pids").mkdir(parents=True, exist_ok=True)
    return {"PYTHONPATH": str(shim), "GOV_NIGHTLY_COVERAGE_DATA": str(data), "GOV_NIGHTLY_COVERAGE_TREE": str(tree),
            "COVERAGE_CORE": "ctrace", "PYTEST_PLUGINS": _PLUGIN_NAME}


def _measured_map(data: Path, tree: Path) -> dict:
    """``{source path: [node ids that executed it]}`` from every process's data file."""
    from coverage import CoverageData

    measured: dict[str, set] = {}
    for path in sorted(data.glob(".coverage.*")):
        found = CoverageData(basename=str(path))
        try:
            found.read()
        except Exception:  # noqa: BLE001 - a data file a process left unfinished measures nothing
            continue
        for file in found.measured_files():
            try:
                rel = Path(file).resolve().relative_to(tree.resolve()).as_posix()
            except ValueError:
                continue
            tests = {context for contexts in (found.contexts_by_lineno(file) or {}).values()
                     for context in contexts if context}
            measured.setdefault(rel, set()).update(tests)
    return {rel: sorted(tests) for rel, tests in sorted(measured.items())}


# ---------------------------------------------------------------------------
# The night
# ---------------------------------------------------------------------------

def night(root: Path, branch: str, coverage: bool = False) -> dict:
    """Run the night on ``branch``'s head; its record, written to the working tree."""
    root = Path(root)
    head = _git(root, "rev-parse", "--verify", "--quiet", f"{branch}^{{commit}}", ok=(0, 1)).strip()
    if not head:
        raise GovError("BRANCH_UNKNOWN", f"{branch} names no commit of {root}", {"branch": branch})
    tree_id = _git(root, "rev-parse", f"{head}^{{tree}}").strip()
    since = _last_green(root, head)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    folder = root / RUNTIME_DIR / f"{stamp}-{head[:12]}"
    folder.mkdir(parents=True, exist_ok=True)
    run_limit = _run_limit(root)

    work = Path(tempfile.mkdtemp(prefix="gov-nightly-"))
    tree = work / "tree"
    _git(root, "worktree", "add", "--detach", "--force", str(tree), head)
    try:
        test_map, _ = _select.load_map(tree)
        per_test, distribution = _select.settings(test_map)
        scope = {"ignore": [], "deselect": [], "per_test_timeout": per_test, "distribution": distribution,
                 "tmp_path_retention_policy": _select.RETENTION_POLICY, "check_result": None, "runs": [], "junit_xml": [], "limit": None, "folder": str(folder)}
        if coverage:  # the shim's folder goes after the tree's own src/ in every run
            (work / "shim").mkdir()
            scope["env"] = _coverage_env(work / "shim", work / "coverage", tree)
        findings, counts = _close._run_tests(tree, tree / "tests", run_limit, scope=scope)
        env = _pytest_env(tree)
        limit = list(scope["limit"] or [])
        failures = [f for run in scope["runs"] for f in run["failures"]]
        tests = list(dict.fromkeys(f["test"] for f in failures))
        per_test, distribution = scope["per_test_timeout"], scope["distribution"]
        closes = _scoped_closes(root, tree, since, head)
        listed, packages = [], []
        for test in tests:
            alone = _alone(tree, test, limit, run_limit, env)
            kind = RED if alone == FAILED else "flaky_candidate"
            text = "\n".join(f["text"] for f in failures if f["test"] == test)
            listed.append({"test": test, "text": text, "alone": alone, "class": kind})
            if kind != RED:
                continue
            packages.append({"priority": PRIORITY, "kind": "bisect", "test": test,
                             "range": f"{since}..{head}" if since else None,
                             "first_bad": _bisect(tree, since, head, test, limit, env) if since else None})
            for close in closes:
                if _missed_by(close, test):
                    packages.append({"priority": PRIORITY, "kind": "selection_miss", "test": test,
                                     "close": close["record"], "ticket": close["ticket"],
                                     "test_map_correction": {"couplings": [{
                                         "paths": list(close["evidence"].get("changed") or []),
                                         "suites": [_suite_of_test(test)],
                                         "why": f"the nightly of {head[:12]} found {test} red after the scoped "
                                                f"close {close['record']} selected it not or saw it pass"}]}})
        measured = None
        if coverage:
            measured_rel = f"{folder.relative_to(root).as_posix()}/measured-map.json"
            (root / measured_rel).write_text(json.dumps(_measured_map(work / "coverage", tree), indent=1),
                                             encoding="utf-8")
            measured = measured_rel
    finally:
        subprocess.run(["git", "-C", str(root), "worktree", "remove", "--force", str(tree)], capture_output=True)
        shutil.rmtree(work, ignore_errors=True)
        subprocess.run(["git", "-C", str(root), "worktree", "prune"], capture_output=True)

    junit = []
    for path in scope["junit_xml"]:
        full = Path(path)
        if not full.exists():
            full.write_text("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<testsuites/>\n", encoding="utf-8")
        junit.append(full.relative_to(root).as_posix())
    verdict = GREEN if not findings and not listed else RED
    record = {"branch": branch, "head": head, "tree": tree_id, "base": since, "scope": "full", "verdict": verdict,
              "junit_xml": junit, "failures": listed, "packages": packages, "tests_run": counts,
              "findings": findings, "per_test_timeout": per_test, "distribution": distribution,
              "tmp_path_retention_policy": scope["tmp_path_retention_policy"], "created": _close._now()}
    if coverage:
        record["measured_map"] = measured
    rel = f"{_select.NIGHTLY_REL}/NR-{stamp}-{head[:12]}.json"
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return {"record": rel, **record}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m gov.close.nightly", description=__doc__.split("\n")[0])
    parser.add_argument("branch")
    parser.add_argument("--root", default=".")
    parser.add_argument("--coverage", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--session", default="")
    args = parser.parse_args(argv)
    try:
        result = night(Path(args.root), args.branch, args.coverage)
    except GovError as error:
        envelope = {"ok": False, "command": COMMAND, "result": {}, "session": args.session,
                    "error": {"code": error.code, "message": error.message, "details": error.details}}
        print(json.dumps(envelope) if args.json else f"{COMMAND}: {error.code}: {error.message}")
        return error.exit_code
    if result["verdict"] == GREEN:
        envelope = {"ok": True, "command": COMMAND, "result": result, "session": args.session}
        code = 0
    else:
        envelope = {"ok": False, "command": COMMAND, "result": {}, "session": args.session,
                    "error": {"code": "NIGHTLY_RED", "message": f"the night of {result['head'][:12]} is red: "
                              f"{len(result['failures'])} failing tests", "details": result}}
        code = EXIT_RED
    print(json.dumps(envelope) if args.json else json.dumps(envelope, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
