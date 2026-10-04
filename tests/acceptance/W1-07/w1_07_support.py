"""Support code for the W1-07 acceptance tests (standard library only).

W1-07 builds the skeleton of the ``gov`` command line. The tests use it only
through its public interface: the ``gov`` command, its arguments, its output and
its exit code.

- **Nothing is installed.** An installed package would give a ``gov`` console
  script made from ``[project.scripts] gov = "<module>:<function>"`` in
  ``pyproject.toml``. The tests read that line and write the same small launcher
  into a temporary directory, then run it with ``python3`` and the project's
  ``src/`` on ``PYTHONPATH`` (the way ``.claude/settings.json`` finds the ``gov``
  package for the hooks).
- **The repository itself is never the project.** The working tree is copied to
  a temporary directory and committed there; every command runs in a copy, with
  the copy's own ``src/`` as the code under test. Bytecode goes to a temporary
  ``PYTHONPYCACHEPREFIX``, so nothing is written next to the sources.
- **The environment is built from scratch:** ``PATH``, an empty temporary
  ``HOME``, ``TMPDIR``, locale, ``PYTHONPATH`` and ``PYTHONPYCACHEPREFIX``.
  ``GOV_ROLE`` and ``GOV_TICKET`` of the session that runs the tests are not
  passed on.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PYPROJECT_REL = "pyproject.toml"
API_REL = "docs/interfaces/API-0002.yaml"
PATH_MAP_REL = "governance/project/path-map.yaml"
CHECKS_REL = "template/governance/kernel/checks"

# The twelve Wave 1 governance operations the registry reserves (ticket KPI, CAP-28.b).
RESERVED_COMMANDS = ("status", "check", "readiness", "doctor", "rebuild", "context", "closure", "retrieve",
                     "checkpoint", "close", "adopt", "pause")

# What W1-07 builds: a minimal ``status`` and ``check --list`` (ticket text, DEC-186).
# Every other reserved command, and ``check`` without ``--list``, is not built yet.
# Planned revision (DEC-190, "planned: command implemented"): W1-25 builds ``checkpoint``; its cases are in
# ``tests/acceptance/W1-25/``.
BUILT_LATER = ("checkpoint",)
NOT_BUILT = tuple(name for name in RESERVED_COMMANDS if name != "status" and name not in BUILT_LATER)

# The read commands of CAP-27's acceptance line, as argument lists, plus ``check --list`` (DEC-186).
READ_COMMANDS = (("status",), ("check",), ("check", "--list"), ("readiness",), ("doctor",), ("context", "--dry-run"),
                 ("closure",), ("retrieve",))

# Every invocation these tests know: one per reserved command, and ``check --list``.
EVERY_INVOCATION = tuple((name,) for name in RESERVED_COMMANDS) + (("check", "--list"),)

NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
CONFIG_INVALID = "CONFIG_INVALID"

COMMAND_TIMEOUT_S = 30.0
# Left out of a tree snapshot: git's own files, and derived state, which is ignored by git.
SNAPSHOT_SKIP = (".git", ".gov-runtime")


class CliMissing(AssertionError):
    """The ``gov`` command line does not exist yet."""


def label(args):
    """``("check", "--list")`` -> ``"check --list"`` (test ids and messages)."""
    return " ".join(args)


# --------------------------------------------------------------------------
# git and the project copy
# --------------------------------------------------------------------------

def git(project, *args, check=True):
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(project),
        "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "W1-07 tests", "GIT_AUTHOR_EMAIL": "w1-07@example.invalid",
        "GIT_COMMITTER_NAME": "W1-07 tests", "GIT_COMMITTER_EMAIL": "w1-07@example.invalid",
    }
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, env=env)
    if check and done.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {project}:\n{done.stderr}")
    return done.stdout


def copy_working_tree(destination, root=REPO_ROOT):
    """Copy the repository's working tree (tracked files and untracked, unignored ones) and commit it."""
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    listing = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        capture_output=True, text=True, check=True,
    ).stdout
    for rel in sorted(set(item for item in listing.split("\0") if item)):
        source = Path(root) / rel
        target = destination / rel
        if not (source.is_file() or source.is_symlink()):
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_symlink():
            target.symlink_to(os.readlink(source))
        else:
            shutil.copy2(source, target)
    git(destination, "init", "-q", "-b", "main")
    git(destination, "add", "-A")
    git(destination, "commit", "-q", "-m", "copy of the working tree")
    return destination


def commit_all(project, message="fixture"):
    git(project, "add", "-A")
    git(project, "commit", "-q", "--allow-empty", "-m", message)


def porcelain(project):
    """``git status --porcelain`` of the project, the measure CAP-27 names."""
    return git(project, "status", "--porcelain")


def git_state(project):
    """HEAD, every ref and the stash: what a command that only reads leaves alone."""
    return {
        "head": git(project, "rev-parse", "HEAD").strip(),
        "branch": git(project, "symbolic-ref", "-q", "HEAD", check=False).strip(),
        "refs": git(project, "for-each-ref", "--format=%(refname) %(objectname)"),
    }


def snapshot(root, skip=SNAPSHOT_SKIP):
    """Every file, link and directory under ``root`` with its content hash; ``skip`` names top-level entries left out."""
    root = Path(root)
    seen = {}
    for folder, dirs, files in os.walk(root):
        rel_folder = Path(folder).relative_to(root)
        if rel_folder == Path("."):
            dirs[:] = [name for name in dirs if name not in skip]
        for name in dirs:
            path = Path(folder) / name
            rel = str(rel_folder / name)
            seen[rel] = "link:" + os.readlink(path) if path.is_symlink() else "dir"
        for name in files:
            path = Path(folder) / name
            rel = str(rel_folder / name)
            if path.is_symlink():
                seen[rel] = "link:" + os.readlink(path)
            else:
                seen[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return seen


def snapshot_difference(before, after):
    """A readable list of what differs between two snapshots; empty when nothing does."""
    lines = []
    for rel in sorted(set(before) | set(after)):
        if rel not in before:
            lines.append(f"created: {rel}")
        elif rel not in after:
            lines.append(f"deleted: {rel}")
        elif before[rel] != after[rel]:
            lines.append(f"changed: {rel}")
    return lines


# --------------------------------------------------------------------------
# The interface file: the envelope and the exit codes the tests hold the CLI to
# --------------------------------------------------------------------------

_JSON_TYPES = {"boolean": bool, "string": str, "object": dict}


@dataclass(frozen=True)
class Interface:
    required: dict       # field name -> Python type
    optional: dict       # field name -> tuple of the keys of that object
    exit_codes: tuple    # the exit codes the interface defines


def load_interface(project):
    """The envelope fields and the exit codes, read from ``docs/interfaces/API-0002.yaml`` of the project.

    The file is read as text (no YAML package is needed for these two entries),
    so a change of the interface file changes what the tests ask of the CLI.
    """
    path = Path(project) / API_REL
    assert path.is_file(), f"{API_REL} does not exist"
    text = path.read_text(encoding="utf-8")
    found = re.search(r'^\s*json_envelope:\s*"\{(.*)\}"\s*$', text, re.MULTILINE)
    assert found, f"{API_REL} has no json_envelope line the tests can read"
    required, optional = {}, {}
    for name, mark, kind in re.findall(r"(\w+)(\??):\s*(\{[^}]*\}|\w+)", found.group(1)):
        if kind.startswith("{"):
            keys = tuple(key.strip() for key in kind.strip("{}").split(",") if key.strip())
            assert mark == "?", f"{API_REL}: the tests expect the object field {name!r} to be optional"
            optional[name] = keys
        else:
            assert mark == "" and kind in _JSON_TYPES, f"{API_REL}: the tests cannot read the field {name}: {kind}"
            required[name] = _JSON_TYPES[kind]
    assert required and optional, f"{API_REL}: no envelope fields read from {found.group(0)!r}"
    block = re.search(r"^\s*exit_codes:\s*\n((?:\s+\"\d+\":.*\n)+)", text, re.MULTILINE)
    assert block, f"{API_REL} has no exit_codes block the tests can read"
    codes = tuple(int(code) for code in re.findall(r'"(\d+)":', block.group(1)))
    assert codes, f"{API_REL}: no exit codes read"
    return Interface(required=required, optional=optional, exit_codes=codes)


# --------------------------------------------------------------------------
# Running the CLI
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Sandbox:
    home: Path
    tmpdir: Path
    bin: Path
    pycache: Path
    elsewhere: Path


def make_sandbox(base):
    base = Path(base)
    names = ("home", "tmp", "bin", "pycache", "elsewhere")
    for name in names:
        (base / name).mkdir(parents=True, exist_ok=True)
    return Sandbox(*(base / name for name in names))


def entry_point(code_root):
    """``(module, attribute)`` of ``[project.scripts] gov`` in ``pyproject.toml`` under ``code_root``."""
    path = Path(code_root) / PYPROJECT_REL
    if not path.is_file():
        raise CliMissing(f"the gov command does not exist: there is no {PYPROJECT_REL}")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise CliMissing(f"{PYPROJECT_REL} is not valid TOML: {exc}") from None
    scripts = data.get("project", {}).get("scripts", {}) if isinstance(data.get("project"), dict) else {}
    target = scripts.get("gov") if isinstance(scripts, dict) else None
    if not isinstance(target, str) or ":" not in target:
        raise CliMissing(f'the gov command does not exist: {PYPROJECT_REL} declares no [project.scripts] gov = '
                         f'"<module>:<function>"')
    module, _, attribute = target.partition(":")
    return module.strip(), attribute.strip()


def write_launcher(code_root, sandbox):
    """Write the console script an install would generate, in the sandbox, and return its path."""
    module, attribute = entry_point(code_root)
    launcher = sandbox.bin / "gov"
    launcher.write_text(
        "import sys\n"
        f"import {module} as _module\n"
        "_target = _module\n"
        f"for _name in {attribute!r}.split('.'):\n"
        "    _target = getattr(_target, _name)\n"
        "if __name__ == '__main__':\n"
        "    sys.argv[0] = 'gov'\n"
        "    sys.exit(_target())\n",
        encoding="utf-8",
    )
    return launcher


@dataclass(frozen=True)
class Run:
    args: tuple
    returncode: int
    stdout: str
    stderr: str
    seconds: float

    def describe(self):
        return (f"gov {' '.join(self.args)}\nexit code: {self.returncode}\nstdout:\n{self.stdout}\n"
                f"stderr:\n{self.stderr}")

    def envelope(self):
        """Standard output as one JSON object."""
        try:
            data = json.loads(self.stdout)
        except ValueError:
            raise AssertionError(f"standard output is not one JSON document\n{self.describe()}") from None
        assert isinstance(data, dict), f"standard output is not a JSON object\n{self.describe()}"
        return data


def run_gov(project, sandbox, *args, cwd=None):
    """Run ``gov <args>`` with the project as the working directory (or ``cwd``), using the project's own code."""
    project = Path(project)
    code_root = project if (project / PYPROJECT_REL).is_file() else None
    assert code_root is not None, f"{project} has no {PYPROJECT_REL}; use run_gov_with_code for a foreign project"
    return run_gov_with_code(code_root, project, sandbox, *args, cwd=cwd)


def run_gov_with_code(code_root, project, sandbox, *args, cwd=None):
    """Run ``gov <args>`` in ``project`` with the ``gov`` package of ``code_root``."""
    launcher = write_launcher(code_root, sandbox)
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(Path(code_root) / "src"),
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
    }
    started = time.perf_counter()
    try:
        done = subprocess.run([sys.executable, str(launcher), *args], cwd=str(cwd or project), env=env,
                              capture_output=True, text=True, timeout=COMMAND_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"gov {' '.join(args)} did not end within {COMMAND_TIMEOUT_S:.0f} s") from None
    return Run(tuple(args), done.returncode, done.stdout, done.stderr, time.perf_counter() - started)


# --------------------------------------------------------------------------
# Assertions
# --------------------------------------------------------------------------

def assert_envelope(run, interface, command=None):
    """The run printed the API-0002 envelope, and its exit code agrees with it. Returns the envelope."""
    envelope = run.envelope()
    allowed = set(interface.required) | set(interface.optional)
    extra = sorted(set(envelope) - allowed)
    assert not extra, f"the envelope has fields {API_REL} does not define: {extra}\n{run.describe()}"
    for name, kind in interface.required.items():
        assert name in envelope, f"the envelope lacks the field {name!r}\n{run.describe()}"
        assert isinstance(envelope[name], kind), \
            f"the envelope field {name!r} is not a {kind.__name__}\n{run.describe()}"
    assert run.returncode in interface.exit_codes, \
        f"the exit code is not one of {interface.exit_codes}\n{run.describe()}"
    error = envelope.get("error")
    if envelope["ok"]:
        assert run.returncode == 0, f"ok is true but the exit code is not 0\n{run.describe()}"
        assert error is None, f"ok is true but the envelope carries an error\n{run.describe()}"
    else:
        assert run.returncode != 0, f"ok is false but the exit code is 0\n{run.describe()}"
        assert isinstance(error, dict), f"ok is false but the envelope has no error object\n{run.describe()}"
        keys = interface.optional["error"]
        assert sorted(error) == sorted(keys), \
            f"the error object does not have exactly the keys {list(keys)}\n{run.describe()}"
        assert isinstance(error["code"], str) and re.fullmatch(r"[A-Z][A-Z0-9_]*", error["code"]), \
            f"error.code is not an upper-case code\n{run.describe()}"
        assert isinstance(error["message"], str) and error["message"].strip(), \
            f"error.message is not a non-empty string\n{run.describe()}"
    if command is not None:
        assert command in envelope["command"].split(), \
            f"the envelope's command field does not name {command!r}\n{run.describe()}"
    return envelope


def assert_error(run, interface, code, exit_code=1, command=None):
    """The run failed with the GovError ``code`` and the exit code for a governance error. Returns the error object."""
    envelope = assert_envelope(run, interface, command=command)
    assert envelope["ok"] is False, f"expected the error {code}, but ok is true\n{run.describe()}"
    assert envelope["error"]["code"] == code, f"expected the error code {code}\n{run.describe()}"
    assert run.returncode == exit_code, f"expected exit code {exit_code} for {code}\n{run.describe()}"
    return envelope["error"]


def find_records(value, key="id"):
    """Every JSON object, at any depth of ``value``, that has ``key``."""
    found = []
    if isinstance(value, dict):
        if key in value:
            found.append(value)
        for item in value.values():
            found.extend(find_records(item, key))
    elif isinstance(value, list):
        for item in value:
            found.extend(find_records(item, key))
    return found
