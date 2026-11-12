"""Support code for the W2-45 acceptance tests (``gov check`` runner semantics and scale, DAEO-neam).

How the tests run (README, "How the tests run"):

- **Through public interfaces only**: ``gov check --json`` run as a process in a temporary project, its API-0002
  envelope (a green run: ``result``; a red run, exit code 3: ``error.details``), the check entries and their
  findings by code, the exit code. No private name of the runner is imported.
- **The code under test is this repository's ``src/``** (DEC-732): the folder beside this file's ``tests/``,
  found from this file's own location, never a fixed path or an installed copy. Every ``gov`` process gets it
  first on its ``PYTHONPATH``.
- **Every project is a temporary git repository built from scratch** under pytest's ``tmp_path``. The only file
  taken from this repository is the real ``core-authority`` declaration (S1).
- **Deterministic, no network.**
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"

RED, YELLOW, GREEN = "RED", "YELLOW", "GREEN"
HARD_BLOCK, WARNING = "hard-block", "warning"
EXIT_CHECK_FAILED = 3
DEFAULT_LIMIT_S = 60  # the limit of a check whose declaration states none (DEC-595)

CHECKS_REL = "template/governance/kernel/checks"
PATH_MAP_REL = "governance/project/path-map.yaml"
CORE_AUTHORITY = "core-authority"
CORE_AUTHORITY_FILE = REPO_ROOT / CHECKS_REL / f"{CORE_AUTHORITY}.yaml"

# a name that is on no folder of any PATH
ABSENT_TOOL = "w2-45-no-such-tool-anywhere"

AUTHOR = {"name": "Fixture", "email": "fixture@example.invalid"}


def _git_env(home: Path) -> dict:
    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(home),
        "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_AUTHOR_NAME": AUTHOR["name"], "GIT_AUTHOR_EMAIL": AUTHOR["email"],
        "GIT_COMMITTER_NAME": AUTHOR["name"], "GIT_COMMITTER_EMAIL": AUTHOR["email"],
    }


def git(root: Path, *args: str, stdin: str | None = None) -> str:
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                          env=_git_env(Path(root).parent), input=stdin)
    assert done.returncode == 0, f"git {' '.join(args)} failed in {root}:\n{done.stderr}"
    return done.stdout


class Run:
    """One ``gov check --json`` process: its exit code, output and the envelope parsed from standard output."""

    def __init__(self, args, returncode, stdout, stderr, seconds):
        self.args, self.returncode, self.stdout, self.stderr, self.seconds = args, returncode, stdout, stderr, seconds
        self.envelope = self._parse(stdout)

    @staticmethod
    def _parse(text):
        text = text.strip()
        if not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            for line in reversed(text.splitlines()):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue
        return None

    def describe(self):
        return (f"gov {' '.join(self.args)} -> exit {self.returncode} in {self.seconds:.1f} s\n"
                f"stdout:\n{self.stdout[-3000:]}\nstderr:\n{self.stderr[-3000:]}")

    @property
    def body(self):
        """The runner's result: ``result`` of a green run, ``error.details`` of a red one (exit code 3)."""
        envelope = self.envelope
        assert isinstance(envelope, dict), f"no envelope\n{self.describe()}"
        if envelope.get("ok"):
            return envelope.get("result") or {}
        details = (envelope.get("error") or {}).get("details")
        assert isinstance(details, dict), f"a refusal without the runner's result in its details\n{self.describe()}"
        return details

    @property
    def checks(self):
        found = self.body.get("checks")
        assert isinstance(found, list), f"the runner's result has no list of checks\n{self.describe()}"
        return found

    def entry(self, check_id):
        found = [each for each in self.checks if each.get("id") == check_id]
        assert len(found) == 1, f"{check_id} is not reported exactly once ({len(found)})\n{self.describe()}"
        return found[0]

    def entry_or_none(self, check_id):
        found = [each for each in self.checks if each.get("id") == check_id]
        return found[0] if found else None


def finding_codes(entry) -> list:
    return [finding.get("code") for finding in entry.get("findings", []) if isinstance(finding, dict)]


def findings_with(entry, code) -> list:
    return [finding for finding in entry.get("findings", []) if isinstance(finding, dict) and finding.get("code") == code]


class Project:
    """A temporary git repository with a set of declared checks, built from scratch."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True)
        self.home = self.root.parent / "home"
        self.home.mkdir(exist_ok=True)
        git(self.root, "init", "-q", "-b", "main")
        self.write("README.md", "# A project\n")
        self.write(".gitignore", ".gov-runtime/\n")

    def write(self, rel: str, text: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def declare(self, check_id: str, command: str, severity: str = HARD_BLOCK, family: str = "schema/invariants",
                tier: str = "G1", timeout_seconds: int | None = None, enforces=None) -> Path:
        lines = [f'id: "{check_id}"', f'family: "{family}"', f'tier: "{tier}"', f'severity: "{severity}"',
                 f"command: {json.dumps(command)}"]
        if timeout_seconds is not None:
            lines.append(f"timeout-seconds: {timeout_seconds}")
        if enforces is not None:
            lines.append("enforces: [" + ", ".join(enforces) + "]")
        return self.write(f"{CHECKS_REL}/{check_id}.yaml", "\n".join(lines) + "\n")

    def script(self, name: str, text: str) -> str:
        """A planted check script; returns the command that runs it (``python3 <path>``)."""
        path = self.write(f"checks-bin/{name}.py", text)
        return f"python3 {path}"

    def path_map(self, policies: dict) -> None:
        text = "namespaces: {all: {paths: ['**']}}\npolicies:\n" + "".join(
            f"  {key}: {strength}\n" for key, strength in policies.items())
        self.write(PATH_MAP_REL, text)

    def commit_all(self, message="fixture", trailers=("Task: setup", "Role: owner")) -> None:
        git(self.root, "add", "-A")
        args = ["commit", "-q", "--allow-empty", "--no-gpg-sign", "-m", message]
        for trailer in trailers:
            args += ["--trailer", trailer]
        git(self.root, *args)

    def env(self, path: str | None = None) -> dict:
        env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin") if path is None else path,
            "HOME": str(self.home),
            "TMPDIR": str(self.home),
            "LC_ALL": "C.UTF-8",
            "PYTHONPATH": str(SRC),
            "PYTHONPYCACHEPREFIX": str(self.home / "pycache"),
        }
        if os.environ.get("PYTHONUSERBASE"):
            env["PYTHONUSERBASE"] = os.environ["PYTHONUSERBASE"]
        return env

    def check(self, path: str | None = None, timeout: float = 600) -> Run:
        """``gov check --json`` in this project, run as a process on this repository's ``src/``."""
        args = ("check", "--json", "--root", str(self.root))
        started = time.perf_counter()
        try:
            done = subprocess.run([sys.executable, "-m", "gov.cli.main", *args], cwd=str(self.root),
                                  env=self.env(path), capture_output=True, text=True, timeout=timeout,
                                  stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"gov {' '.join(args)} did not end within {timeout:.0f} s") from None
        return Run(args, done.returncode, done.stdout, done.stderr, time.perf_counter() - started)


def make_path(folder: Path, *, keep=("git", "python3", "sh", "bash")) -> str:
    """A ``PATH`` of one folder ``folder`` holding links to the tools in ``keep`` only (so ``openspec``,
    ``gitleaks`` and any other tool are on no folder of it). Returns the folder as the ``PATH`` text."""
    folder.mkdir(parents=True, exist_ok=True)
    for name in keep:
        found = shutil.which(name)
        if found is None:
            continue
        link = folder / name
        if not link.exists():
            link.symlink_to(found)
    return str(folder)


def repo_with_decisions(project: Project, decisions: int = 200, commits: int = 20000) -> None:
    """Fill ``project`` (an empty git repository) with ``decisions`` decision records and ``commits`` commits,
    built with ``git fast-import``.

    The first ``decisions`` commits each add one decision file ``docs/adr/DEC-<n>.md`` (``type: decision``,
    ``status: ACTIVE``, an owner's trailer on the commit that sets it). Of the remaining commits every second one
    touches a decision file (a line added to its body), the others touch a file under ``src/``, so the decision
    checker's walk over history meets many commits that concern decisions."""
    assert commits >= decisions
    base = 1_792_000_000  # 2026-10-14: after the date from which the trailer is read from the final block
    stream = []

    def commit(index: int, message: str, files: dict) -> None:
        data = message.encode()
        stream.append(f"commit refs/heads/main\ncommitter {AUTHOR['name']} <{AUTHOR['email']}> {base + index} +0000\n"
                      f"data {len(data)}\n{message}\n")
        for rel, text in files.items():
            body = text.encode()
            stream.append(f"M 100644 inline {rel}\ndata {len(body)}\n{text}\n")
        stream.append("\n")

    def decision_text(number: int, revision: int) -> str:
        return (f"---\nid: DEC-{number:03d}\ntype: decision\nstatus: ACTIVE\ntitle: Decision {number}\n---\n"
                f"# DEC-{number:03d}\n\nrevision {revision}\n")

    revisions = {}
    for index in range(commits):
        if index < decisions:
            number = index + 1
            revisions[number] = 0
            commit(index, f"decision {number}\n\nTask: setup\nRole: owner",
                   {f"docs/adr/DEC-{number:03d}.md": decision_text(number, 0)})
        elif index % 2 == 0:
            number = (index % decisions) + 1
            revisions[number] += 1
            commit(index, f"revise decision {number}\n\nTask: setup\nRole: owner",
                   {f"docs/adr/DEC-{number:03d}.md": decision_text(number, revisions[number])})
        else:
            commit(index, f"work {index}\n\nTask: work\nRole: engineer",
                   {f"src/part{index % 50}.txt": f"line {index}\n"})
    done = subprocess.run(["git", "-C", str(project.root), "fast-import", "--quiet"], input="".join(stream).encode(),
                          capture_output=True, env=_git_env(project.root.parent))
    assert done.returncode == 0, f"git fast-import failed: {done.stderr.decode()}"
    git(project.root, "reset", "-q", "--hard", "main")
