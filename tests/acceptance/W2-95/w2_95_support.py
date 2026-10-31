"""Support for the W2-95 acceptance tests (core-pathmap, DAEO-57hm).

Every test plants its own repository in a temporary folder (``git init``, a few
tracked files, ``governance/project/path-map.yaml``) and runs the check through
its public interfaces only:

- the command its declaration states (``template/governance/kernel/checks/
  core-pathmap.yaml``), run from the planted repository's root: findings as JSON
  on stdout, non-zero exit when there are findings, zero when green;
- ``gov check --json`` (``python3 -m gov.cli.main check --json``), whose answer
  carries the family "path-map compliance" and the check ``core-pathmap``: under
  ``result`` when no hard-block check is red, and under ``error.details`` (with
  ``ok`` false and the code ``CHECK_FAILED``) when one is.

The code under test is the ``src/`` folder of the repository that holds this
file: ``REPO_ROOT`` is derived from this file's own location, never from an
absolute path, and every subprocess gets ``PYTHONPATH=<REPO_ROOT>/src``.
This repository's own path map is never used.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
DECLARATION = REPO_ROOT / "template" / "governance" / "kernel" / "checks" / "core-pathmap.yaml"
PATH_MAP = "governance/project/path-map.yaml"
CHECK_ID = "core-pathmap"
FAMILY = "path-map compliance"
TIMEOUT = 300

# The codes and fields core-pathmap already gives on w2/integrate (public interface).
NO_NAMESPACE = "PATH_NO_NAMESPACE"
MULTIPLE_NAMESPACES = "PATH_MULTIPLE_NAMESPACES"

# The fields the path map's schema requires of a namespace besides `paths`, so that
# a planted entry is of the form the schema states and only `paths` is judged.
_NAMESPACE_FIELDS = {
    "memory_class": "governance",
    "sensitivity": "internal",
    "permitted_roles": ["engineer"],
    "retention": "permanent",
    "export_policy": "none",
    "embedding_policy": "embed",
    "provenance": "git",
    "deletion_rebuild": "rebuild from git",
}


def entry(*patterns):
    """A namespace entry of the form the schema states, with these path patterns."""
    return {"paths": list(patterns), **_NAMESPACE_FIELDS}


def mapping_form(namespaces):
    """A path map text in the schema's form: ``namespaces`` maps a name to its entry."""
    return yaml.safe_dump({"namespaces": {n: entry(*p) for n, p in namespaces.items()}}, sort_keys=False)


def list_form(namespaces):
    """A path map text in the older form: ``namespaces`` is a list of entries with ``name``."""
    return yaml.safe_dump(
        {"namespaces": [{"name": n, **entry(*p)} for n, p in namespaces.items()]}, sort_keys=False
    )


def _env(home):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
    env["PYTHONPATH"] = str(SRC)
    env["HOME"] = str(home)
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["LC_ALL"] = "C.UTF-8"
    return env


class Planted:
    """A planted repository: tracked files, a path map, and the two public interfaces."""

    def __init__(self, base, files, path_map=None, path_map_bytes=None, declare_check=True):
        self.root = Path(base) / "repo"
        self.home = Path(base) / "home"
        self.home.mkdir(parents=True)
        self.root.mkdir(parents=True)
        tracked = []
        for rel in files:
            p = self.root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(f"planted {rel}\n", encoding="utf-8")
            tracked.append(rel)
        (self.root / "governance" / "project").mkdir(parents=True, exist_ok=True)
        if path_map is not None or path_map_bytes is not None:
            data = path_map_bytes if path_map_bytes is not None else path_map.encode("utf-8")
            (self.root / PATH_MAP).write_bytes(data)
            tracked.append(PATH_MAP)
        if declare_check:
            # The declaration is present (untracked) so that `gov check` registers core-pathmap.
            target = self.root / "template" / "governance" / "kernel" / "checks"
            target.mkdir(parents=True)
            shutil.copyfile(DECLARATION, target / DECLARATION.name)
        self.git("init", "-q")
        if tracked:
            self.git("add", "-f", "--", *tracked)
        self.tracked = sorted(tracked)

    def git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.root, env=_env(self.home), capture_output=True, text=True, check=True
        )

    def add(self, rel, text="added\n"):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        self.git("add", "-f", "--", rel)

    def declared(self):
        """Run the check's declared command from the repository's root."""
        command = yaml.safe_load(DECLARATION.read_text(encoding="utf-8"))["command"]
        argv = shlex.split(command)
        if argv[0] in ("python3", "python"):
            argv[0] = sys.executable
        run = subprocess.run(
            argv, cwd=self.root, env=_env(self.home), capture_output=True, text=True, timeout=TIMEOUT
        )
        return Declared(run)

    def gov_check(self):
        """Run ``gov check --json`` from the repository's root."""
        run = subprocess.run(
            [sys.executable, "-m", "gov.cli.main", "check", "--json"],
            cwd=self.root,
            env=_env(self.home),
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
        return GovCheck(run)


class Declared:
    """The result of the declared command."""

    def __init__(self, run):
        self.run = run
        self.code = run.returncode
        self.stdout = run.stdout
        self.text = run.stdout + "\n" + run.stderr
        try:
            self.findings = json.loads(run.stdout) if run.stdout.strip() else []
        except ValueError:
            self.findings = None

    def describe(self):
        return f"exit {self.code}\nstdout: {self.stdout[:3000]}\nstderr: {self.run.stderr[-2000:]}"


class GovCheck:
    """The result of ``gov check --json``."""

    def __init__(self, run):
        self.run = run
        self.code = run.returncode
        try:
            self.envelope = json.loads(run.stdout)
        except ValueError:
            self.envelope = None

    def describe(self):
        return f"exit {self.code}\nstdout: {self.run.stdout[:4000]}\nstderr: {self.run.stderr[-1500:]}"

    def failed_form(self):
        """True when gov check answered in its failure form: a hard-block check is red, so
        ``ok`` is false, the error code is ``CHECK_FAILED`` and the checks are under
        ``error.details`` (``result`` is empty)."""
        env = self.envelope or {}
        error = env.get("error") or {}
        return env.get("ok") is False and error.get("code") == "CHECK_FAILED" and isinstance(
            error.get("details"), dict
        )

    def answered(self):
        """True when gov check answered with its checks, in either form; any other answer
        (no JSON, or another error) is a refusal of the planted project."""
        return (self.envelope or {}).get("ok") is True or self.failed_form()

    @property
    def result(self):
        """The checks and families, from ``result`` (success form) or ``error.details``
        (failure form)."""
        env = self.envelope or {}
        if self.failed_form():
            return env["error"]["details"]
        return env.get("result") or {}

    def checks(self):
        return {c.get("id"): c for c in self.result.get("checks") or []}

    def pathmap(self):
        return self.checks().get(CHECK_ID)

    def family(self):
        return (self.result.get("families") or {}).get(FAMILY)


def path_findings(findings):
    """Map each named path to its findings (findings with a ``path`` field)."""
    named = {}
    for f in findings or []:
        if isinstance(f, dict) and isinstance(f.get("path"), str):
            named.setdefault(f["path"], []).append(f)
    return named


def matched(finding):
    """The namespaces a path finding says the path matched (none when the field is absent)."""
    return sorted(finding.get("namespaces") or [])


def mentions_any(text, words):
    low = text.lower()
    return any(w in low for w in words)
