"""Support code for the W1-23 acceptance tests (standard library only).

W1-23 builds hierarchical synthesis notes. The tests use only public interfaces:

- ``gov.retrieval.synthesis.synthesize(root, evidence, budget, *, gaps=None)``
- ``gov.retrieval.synthesis.validate_notes(root)``

Both are called in a child process with this worktree's ``src/`` on ``PYTHONPATH``.
Nothing is built in this worktree (DEC-322). Every project is a temporary git
repository with its own ``.gov-runtime/``.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"

# ---- the public interface (DP-1: synthesize, DP-2: validate_notes) ----------

SYNTHESIS_MODULE = "gov.retrieval.synthesis"
SYNTHESIZE_FUNCTION = "synthesize"
VALIDATE_NOTES_FUNCTION = "validate_notes"

CALL_TIMEOUT_S = 60.0
MISSING_EXIT = 3
TOKEN_CHARS = 4


class Missing(AssertionError):
    """Something the ticket builds does not exist yet."""


# --------------------------------------------------------------------------
# The driver: one child process per batch of calls
# --------------------------------------------------------------------------

_DRIVER = r'''
import importlib, json, sys
from pathlib import Path

request = json.loads(sys.stdin.read())


def decode(value):
    if isinstance(value, dict) and set(value) == {"$path"}:
        return Path(value["$path"])
    return value


out = {"calls": []}
for call in request["calls"]:
    try:
        function = getattr(importlib.import_module(call["module"]), call["function"])
    except ModuleNotFoundError as exc:
        if exc.name is None or not (call["module"] == exc.name or call["module"].startswith(exc.name + ".")):
            raise
        print(f"No module named {exc.name!r}", file=sys.stderr)
        sys.exit(3)
    except AttributeError:
        print(f"{call['module']} has no function {call['function']}", file=sys.stderr)
        sys.exit(3)
    record = {"value": None, "error": None}
    try:
        record["value"] = function(*[decode(arg) for arg in call["args"]],
                                   **{key: decode(value) for key, value in call["kwargs"].items()})
    except Exception as exc:
        record["error"] = {"type": type(exc).__name__, "message": str(exc), "code": getattr(exc, "code", None)}
    out["calls"].append(record)
print("\n" + json.dumps(out, default=repr))
'''


def path_arg(path):
    return {"$path": str(path)}


class Outcome:
    def __init__(self, data, stderr):
        self.calls, self.stderr = data["calls"], stderr

    def error(self, index=0):
        return self.calls[index]["error"]

    def value(self, index=0):
        call = self.calls[index]
        assert call["error"] is None, \
            f"call {index} raised {call['error']['type']}: {call['error']['message']}\n{self.stderr[-2000:]}"
        return call["value"]


class Api:
    """Calls this worktree's modules in a new process."""

    def __init__(self, workdir):
        self.workdir = Path(workdir)
        for name in ("home", "tmp", "pycache", "elsewhere", "bin"):
            (self.workdir / name).mkdir(parents=True, exist_ok=True)
        for tool in ("git", "python3"):
            found = sys.executable if tool == "python3" else shutil.which(tool)
            if found:
                wrapper = self.workdir / "bin" / tool
                wrapper.write_text(f'#!/bin/sh\nexec "{found}" "$@"\n', encoding="utf-8")
                wrapper.chmod(0o755)
        self.driver = self.workdir / "driver.py"
        self.driver.write_text(_DRIVER, encoding="utf-8")

    def scratch_env(self):
        return {
            "PATH": str(self.workdir / "bin"),
            "HOME": str(self.workdir / "home"),
            "TMPDIR": str(self.workdir / "tmp"),
            "LC_ALL": "C.UTF-8",
            "GIT_CONFIG_NOSYSTEM": "1",
            "PYTHONPATH": str(SRC),
            "PYTHONPYCACHEPREFIX": str(self.workdir / "pycache"),
        }

    def run(self, calls, *, env=None, timeout=CALL_TIMEOUT_S):
        request = {"calls": [{"module": m, "function": f, "args": list(a), "kwargs": dict(k)}
                             for m, f, a, k in calls]}
        what = ", ".join(dict.fromkeys(f"{m}.{f}" for m, f, *_ in calls))
        try:
            done = subprocess.run([sys.executable, str(self.driver)], input=json.dumps(request),
                                  env=self.scratch_env() if env is None else env,
                                  cwd=str(self.workdir / "elsewhere"), capture_output=True, text=True,
                                  timeout=timeout)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"{what} did not end within {timeout:.0f} s") from None
        if done.returncode == MISSING_EXIT:
            raise Missing(f"the module does not exist: {done.stderr.strip()}")
        assert done.returncode == 0, f"{what} failed (exit {done.returncode}):\n{done.stderr[-4000:]}"
        try:
            data = json.loads(done.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            raise AssertionError(f"{what} gave no JSON:\n{done.stdout}\n{done.stderr}") from None
        return Outcome(data, done.stderr)

    def call(self, module, function, *args, **kwargs):
        return self.run([(module, function, args, kwargs)]).value()

    def exists(self, module, function):
        done = subprocess.run([sys.executable, "-c", f"from {module} import {function}"], capture_output=True,
                              text=True, cwd=str(self.workdir / "elsewhere"), env=self.scratch_env())
        if done.returncode != 0:
            last = done.stderr.strip().splitlines()[-1] if done.stderr.strip() else "import failed"
            raise Missing(f"{module}.{function} does not exist: {last}")

    # ---- DP-1: synthesize

    def synthesize(self, root, evidence, budget, *, gaps=None):
        kwargs = {}
        if gaps is not None:
            kwargs["gaps"] = gaps
        return self.call(SYNTHESIS_MODULE, SYNTHESIZE_FUNCTION, path_arg(root), evidence, budget, **kwargs)

    # ---- DP-2: validate_notes

    def validate_notes(self, root):
        return self.call(SYNTHESIS_MODULE, VALIDATE_NOTES_FUNCTION, path_arg(root))


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def sha256(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def span_bytes(root, rel, start, end):
    lines = (Path(root) / rel).read_bytes().splitlines(keepends=True)
    return b"".join(lines[start - 1:end])


def tokens(text):
    return -(-len(text) // TOKEN_CHARS)


def make_evidence_item(root, rel, start, end, item_id=None):
    body = span_bytes(root, rel, start, end)
    text = body.decode("utf-8", "replace")
    return {
        "id": item_id or f"{rel}:{start}-{end}",
        "sha256": sha256(body),
        "path": rel,
        "start_line": start,
        "end_line": end,
        "text": text,
    }


# --------------------------------------------------------------------------
# Git and fixture helpers
# --------------------------------------------------------------------------

BASE_DATE = "2026-09-01T12:00:00+00:00"


def git(project, *args, date=BASE_DATE):
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(project), "LC_ALL": "C",
           "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "W1-23 tests", "GIT_AUTHOR_EMAIL": "w1-23@example.invalid",
           "GIT_COMMITTER_NAME": "W1-23 tests", "GIT_COMMITTER_EMAIL": "w1-23@example.invalid",
           "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date}
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, env=env)
    assert done.returncode == 0, f"git {' '.join(args)} failed in {project}:\n{done.stderr}"
    return done.stdout


def write(project, rel, text):
    path = Path(project) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return rel


def commit(project, message="a change", date=BASE_DATE):
    git(project, "add", "-A")
    git(project, "commit", "-q", "--allow-empty", "-m", message, date=date)


# --------------------------------------------------------------------------
# The fixture project (files across multiple directories)
# --------------------------------------------------------------------------

ALPHA_TEXT = """\
# Alpha document

This is the alpha document in the docs directory.
It contains important governance information.
Alpha reference line one.
Alpha reference line two.
Alpha reference line three.
Alpha reference line four.
Alpha conclusion paragraph.
End of alpha.
"""

BETA_TEXT = """\
# Beta document

This is the beta document in the docs directory.
Beta contains supplementary details.
Beta reference line one.
Beta reference line two.
Beta reference line three.
Beta conclusion.
End of beta.
"""

GAMMA_TEXT = """\
# Gamma specification

Specification gamma in the specs directory.
Gamma defines the interface contract.
Gamma requirement one.
Gamma requirement two.
Gamma requirement three.
Gamma requirement four.
Gamma requirement five.
End of gamma.
"""

DELTA_TEXT = """\
# Delta record

Delta is a record in the records directory.
Delta captures a design decision.
Delta rationale line one.
Delta rationale line two.
End of delta.
"""


def build_fixture(project):
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    git(project, "init", "-q", "-b", "main")
    write(project, ".gitignore", ".gov-runtime/\n")
    write(project, "docs/alpha.md", ALPHA_TEXT)
    write(project, "docs/beta.md", BETA_TEXT)
    write(project, "specs/gamma.md", GAMMA_TEXT)
    write(project, "records/delta.md", DELTA_TEXT)
    commit(project, "W1-23 fixture")
    return project
