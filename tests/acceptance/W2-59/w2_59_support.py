"""W2-59 acceptance support: the stand-in pin, the projects under check, the decoys and the runs.

Two installs take part in every case that needs a judge (README, "How the cases run this worktree's code"):

- **the stand-in pin**: a wheel built once per session from this worktree, without writing into it, and installed
  non-editable into a ``--system-site-packages`` virtual environment in a short temporary folder, the way the
  owner's pin is made (DEC-822 item 1). It is reached the way the owner's pin is: a link at
  ``<HOME>/.local/bin/gov`` to its ``bin/gov``, with ``HOME`` a temporary folder;
- **a project under check**: a temporary git repository built from scratch, whose files are data for the judge.

The stand-in is instrumented after its install, and only there: a ``.pth`` file in its site folder leaves a
``pin-python-<pid>`` marker each time its interpreter starts, and its installed ``gov/__init__.py`` leaves a
``pin-gov-<pid>`` marker each time its package is imported. Decoys leave markers of their own: a ``python3`` and a
``gov`` first on ``PATH`` (``path-python3-``, ``path-gov-``), a ``gov`` package in the project's ``src/``
(``tree-gov-``) or at the project's root (``root-gov-``). Every marker is written to a folder whose absolute path
is written into the decoy itself, so no marker depends on an environment variable reaching the process.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path

import yaml

WORKTREE = Path(__file__).resolve().parents[3]
SRC = WORKTREE / "src"
PYPROJECT = WORKTREE / "pyproject.toml"
CHECKS_REL = "template/governance/kernel/checks"
KERNEL_LAYOUTS = {"template": "template/governance/kernel", "installed": "governance/kernel"}  # DEC-579
HOOKS_REL = "template/governance/kernel/hooks"
HOOK_SOURCE_REL = ".rulesync/hooks.jsonc"
BASELINE_IN_PACKAGE = "gov/retrieval/retrieve_baseline.yaml"
REAL_PYTHON = os.path.realpath(sys.executable)
SYSTEM_PATH = "/usr/bin:/bin"
TICKET = "DAEO-w259"

DECOY_CANARY = "w259 decoy canary at the install path"
DECOY_MARK = "w259 decoy at the install path"
TREE_EDIT_CODE = "W259_TREE_EDIT"
PATH_GOV_CODE = "W259_DECOY_GOV_ON_PATH"


# ---------------------------------------------------------------------------------------------------------------
# Runs
# ---------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Run:
    args: tuple
    cwd: str
    returncode: int | None
    stdout: str
    stderr: str

    def describe(self) -> str:
        return (f"$ {' '.join(map(str, self.args))}  (in {self.cwd})\nexit: {self.returncode}\n"
                f"stdout:\n{self.stdout[-3000:]}\nstderr:\n{self.stderr[-3000:]}")


def run(args, cwd, env, stdin: str | None = None, timeout: int = 600) -> Run:
    try:
        done = subprocess.run([str(a) for a in args], cwd=str(cwd), env=env, input=stdin if stdin is not None else "",
                              capture_output=True, text=True, timeout=timeout)
        return Run(tuple(args), str(cwd), done.returncode, done.stdout, done.stderr)
    except subprocess.TimeoutExpired as exc:
        return Run(tuple(args), str(cwd), None, str(exc.stdout or ""), f"timed out after {timeout} s")


def clean_env() -> dict:
    """This process's environment without ``PYTHONPATH``: the test runner's own choice of code is not passed on."""
    return {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}


def base_env(home: Path, path: str) -> dict:
    """A process environment for a judge or a hook: a temporary home, the given ``PATH``, no ``PYTHONPATH``."""
    return {
        "HOME": str(home), "PATH": path, "LANG": "C.UTF-8", "TMPDIR": os.environ.get("TMPDIR", "/tmp"),
        "GIT_AUTHOR_NAME": "w259", "GIT_AUTHOR_EMAIL": "w259@example.invalid",
        "GIT_COMMITTER_NAME": "w259", "GIT_COMMITTER_EMAIL": "w259@example.invalid",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
    }


def worktree_code_env(home: Path) -> dict:
    """The environment that runs this worktree's own ``src/`` (DEC-732), set for the one subprocess."""
    env = base_env(home, SYSTEM_PATH)
    env["PYTHONPATH"] = str(SRC)
    return env


# ---------------------------------------------------------------------------------------------------------------
# Git
# ---------------------------------------------------------------------------------------------------------------

def git(root: Path, *args: str) -> str:
    env = base_env(Path(root), SYSTEM_PATH)
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=env)
    assert done.returncode == 0, f"git {' '.join(args)} failed in {root}: {done.stderr}"
    return done.stdout.strip()


def worktree_head() -> str:
    return git(WORKTREE, "rev-parse", "HEAD")


def make_repository(root: Path, files: dict | None = None, copies: dict | None = None) -> Path:
    """A git repository built from scratch at ``root``: ``files`` (path -> text) written, ``copies`` (path in the
    repository -> one named file of this worktree) copied, all committed once."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    git(root, "init", "-q")
    for rel, text in (files or {}).items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for rel, source in (copies or {}).items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, path)
    if not (files or copies):
        (root / "README.md").write_text("w259\n", encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "w259 project under check")
    return root


# ---------------------------------------------------------------------------------------------------------------
# The stand-in pin
# ---------------------------------------------------------------------------------------------------------------

_PIN_GOV_INSTRUMENT = """

# --- W2-59 acceptance instrumentation of the stand-in pin (added after its install; never in the wheel) ---
try:
    import os as _w259_os
    if _w259_os.path.isdir({markers!r}):
        with open(_w259_os.path.join({markers!r}, "pin-gov-%d" % _w259_os.getpid()), "w") as _w259_f:
            _w259_f.write(__file__)
except OSError:
    pass
"""


@dataclass(frozen=True)
class StandIn:
    root: Path      # the short temporary folder that holds everything of the stand-in
    wheel: Path
    venv: Path
    site: Path      # the site folder of its environment
    markers: Path   # where its instrumentation leaves markers

    @property
    def gov(self) -> Path:
        return self.venv / "bin" / "gov"

    @property
    def python(self) -> Path:
        return self.venv / "bin" / "python"

    @property
    def install_path_root(self) -> Path:
        """Where a lookup from the installed package's own location lands: three folders above the installed
        ``gov/retrieval/`` module, which is the repository root for a source checkout (``src/gov/retrieval``) and
        ``<environment>/lib/python3.X`` for this install."""
        return (self.site / "gov" / "retrieval" / "canary.py").resolve().parents[3]

    def clear_markers(self) -> None:
        for path in self.markers.iterdir():
            path.unlink()

    def marks(self, prefix: str) -> list[Path]:
        return sorted(path for path in self.markers.iterdir() if path.name.startswith(prefix))


def _leftovers() -> set[str]:
    """What a plain build leaves in the source tree."""
    found = set()
    for rel in ("build", "dist"):
        if (WORKTREE / rel).exists():
            found.add(rel)
    found.update(str(path.relative_to(WORKTREE)) for path in SRC.glob("*.egg-info"))
    return found


def build_wheel(base: Path) -> Path:
    """One wheel of this worktree, built without writing into it (the lead's form: build and egg-info folders
    moved into ``base`` by ``DIST_EXTRA_CONFIG``)."""
    (base / "eb").mkdir(parents=True)
    config = base / "dist-extra.cfg"
    config.write_text(f"[build]\nbuild_base={base / 'bb'}\n[egg_info]\negg_base={base / 'eb'}\n", encoding="utf-8")
    env = clean_env()
    env.update({"DIST_EXTRA_CONFIG": str(config), "PIP_NO_CACHE_DIR": "1", "PIP_DISABLE_PIP_VERSION_CHECK": "1"})
    before = _leftovers()
    done = run([REAL_PYTHON, "-m", "pip", "wheel", "--no-deps", "--no-build-isolation", "--no-index", "-q",
                "-w", base / "dist", WORKTREE], cwd=base, env=env)
    added = _leftovers() - before
    assert not added, f"building the stand-in's wheel wrote into the worktree: {sorted(added)}"
    assert done.returncode == 0, f"the wheel of this worktree could not be built\n{done.describe()}"
    wheels = sorted((base / "dist").glob("*.whl"))
    assert len(wheels) == 1, f"one wheel expected in {base / 'dist'}, found {wheels}"
    return wheels[0]


def make_stand_in(base: Path) -> StandIn:
    wheel = build_wheel(base)
    venv = base / "venv"
    env = clean_env()
    env.update({"PIP_NO_CACHE_DIR": "1", "PIP_DISABLE_PIP_VERSION_CHECK": "1"})
    done = run([REAL_PYTHON, "-m", "venv", "--system-site-packages", venv], cwd=base, env=env)
    assert done.returncode == 0, done.describe()
    done = run([venv / "bin" / "python", "-m", "pip", "install", "--no-deps", "--no-index", "-q", wheel],
               cwd=base, env=env)
    assert done.returncode == 0, f"the stand-in's wheel could not be installed\n{done.describe()}"
    done = run([venv / "bin" / "python", "-c", "import sysconfig; print(sysconfig.get_paths()['purelib'])"],
               cwd=base, env=env)
    site = Path(done.stdout.strip())
    first = (venv / "bin" / "gov").read_text(encoding="utf-8").splitlines()[0]
    assert first.startswith("#!/") and not first.startswith("#!/bin/sh"), (
        f"the stand-in's bin/gov does not name its interpreter in its first line ({first!r}): the temporary folder "
        f"{base} is too long for a direct '#!' line, unlike the owner's pin; run with a shorter TMPDIR")
    markers = base / "pin-markers"
    markers.mkdir()
    (site / "w259_instrument.pth").write_text(
        f"import os; os.path.isdir({str(markers)!r}) and "
        f"open(os.path.join({str(markers)!r}, 'pin-python-%d' % os.getpid()), 'w').close()\n", encoding="utf-8")
    init = site / "gov" / "__init__.py"
    init.write_text(init.read_text(encoding="utf-8") + _PIN_GOV_INSTRUMENT.format(markers=str(markers)),
                    encoding="utf-8")
    stand_in = StandIn(base, wheel, venv, site, markers)
    plant_install_path_decoys(stand_in)
    return stand_in


def plant_install_path_decoys(stand_in: StandIn) -> None:
    """Files at the place a lookup from the installed package's location leads to, each with content that would
    change the result: a canary declaration with a query of its own (both kernel layouts), a path map and a
    gitleaks configuration that cannot be read."""
    root = stand_in.install_path_root
    for layout in KERNEL_LAYOUTS.values():
        for index in ("lexical", "semantic"):
            path = root / layout / "canaries" / f"{index}.yaml"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f'canaries:\n  - query: "{DECOY_CANARY}"\n', encoding="utf-8")
    path_map = root / "governance" / "project" / "path-map.yaml"
    path_map.parent.mkdir(parents=True, exist_ok=True)
    path_map.write_text(f"namespaces: [{DECOY_MARK}\n  : : not yaml\n", encoding="utf-8")
    for rel in ("template/.gitleaks.toml", ".gitleaks.toml"):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"title = [ \"{DECOY_MARK}\" not toml\n", encoding="utf-8")


# ---------------------------------------------------------------------------------------------------------------
# The box: a temporary home, the decoys on PATH, a marker folder
# ---------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Box:
    home: Path
    local_bin: Path   # <HOME>/.local/bin
    decoy_bin: Path
    markers: Path

    def marks(self, prefix: str) -> list[Path]:
        return sorted(path for path in self.markers.iterdir() if path.name.startswith(prefix))


def make_box(base: Path, stand_in: StandIn | None, *, decoy_gov: bool = False) -> Box:
    """A temporary home with ``.local/bin/gov`` linked to the stand-in's ``bin/gov`` (no link when ``stand_in`` is
    None), a folder with a decoy ``python3`` (and a decoy ``gov`` when asked) that leave markers, and the marker
    folder. The decoy ``python3`` goes on to the real interpreter, so a run that uses it still runs."""
    base = Path(base)
    home, decoy_bin, markers = base / "home", base / "decoy-bin", base / "markers"
    local_bin = home / ".local" / "bin"
    for folder in (local_bin, decoy_bin, markers):
        folder.mkdir(parents=True)
    if stand_in is not None:
        os.symlink(stand_in.gov, local_bin / "gov")
    _script(decoy_bin / "python3", f'#!/bin/sh\n: > "{markers}/path-python3-$$"\nexec "{REAL_PYTHON}" "$@"\n')
    if decoy_gov:
        finding = json.dumps({"findings": [{"code": PATH_GOV_CODE, "message": "the gov first on PATH ran"}]})
        _script(decoy_bin / "gov", f"#!/bin/sh\n: > \"{markers}/path-gov-$$\"\necho '{finding}'\nexit 1\n")
    return Box(home, local_bin, decoy_bin, markers)


def _script(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


def tree_gov_files(markers: Path, prefix: str = "src/") -> dict:
    """A ``gov`` package of the project's own (under ``src/`` by default): importing it leaves a marker, and its
    schema check is edited to give the opposite verdict (a finding, exit 1)."""
    marker = "tree-gov" if prefix == "src/" else "root-gov"
    return {
        f"{prefix}gov/__init__.py": (
            "import os\n"
            f"with open(os.path.join({str(markers)!r}, '{marker}-%d' % os.getpid()), 'w') as f:\n"
            "    f.write(__file__)\n"),
        f"{prefix}gov/check/__init__.py": "",
        f"{prefix}gov/check/schema.py": (
            "import json, sys\n"
            f"print(json.dumps([{{'code': '{TREE_EDIT_CODE}', 'message': 'the check as edited in the tree'}}]))\n"
            "sys.exit(1)\n"),
    }


def declared_check_copies(layout: str = "template") -> dict:
    """Every check declaration of this worktree's kernel, each copied as a single named file into ``layout``."""
    target = f"{KERNEL_LAYOUTS[layout]}/checks"
    return {f"{target}/{path.name}": path for path in sorted((WORKTREE / CHECKS_REL).glob("*.yaml"))}


# ---------------------------------------------------------------------------------------------------------------
# The judge's answers
# ---------------------------------------------------------------------------------------------------------------

def envelope(done: Run) -> dict:
    try:
        parsed = json.loads(done.stdout)
    except json.JSONDecodeError:
        raise AssertionError(f"the judge printed no JSON envelope\n{done.describe()}") from None
    assert isinstance(parsed, dict), done.describe()
    return parsed


def check_results(done: Run) -> dict:
    """The per-check results of ``gov check --json``, by check id, from the success or the error form."""
    parsed = envelope(done)
    body = parsed.get("result") or {}
    if "checks" not in body:
        body = (parsed.get("error") or {}).get("details") or {}
    checks = body.get("checks")
    assert isinstance(checks, list), f"no per-check results in the envelope\n{done.describe()}"
    return {entry.get("id"): entry for entry in checks if isinstance(entry, dict)}


def finding_codes(entry: dict) -> list:
    return [finding.get("code") for finding in entry.get("findings", []) if isinstance(finding, dict)]


def judge_check(box: Box, project: Path, *, decoys_first: bool) -> Run:
    """The stand-in pin's ``gov check --json`` in ``project``, started through ``<HOME>/.local/bin/gov``."""
    first, second = (box.decoy_bin, box.local_bin) if decoys_first else (box.local_bin, box.decoy_bin)
    env = base_env(box.home, f"{first}:{second}:{SYSTEM_PATH}")
    return run([box.local_bin / "gov", "check", "--json"], cwd=project, env=env)


# ---------------------------------------------------------------------------------------------------------------
# The hook lines
# ---------------------------------------------------------------------------------------------------------------

def load_jsonc(path: Path):
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        kept = [line for line in text.splitlines() if not line.lstrip().startswith("//")]
        return json.loads("\n".join(kept))


def hook_entries() -> list:
    """(event, index, entry) for every command entry of this repository's rulesync hooks source."""
    source = load_jsonc(WORKTREE / HOOK_SOURCE_REL)
    found = []
    for event, entries in (source.get("hooks") or {}).items():
        for index, entry in enumerate(entries or []):
            if isinstance(entry, dict) and entry.get("type") == "command":
                found.append((event, index, entry))
    return found


def hook_input(event: str, project: Path) -> dict:
    """What the harness gives each event on standard input, as much of it as the programs read."""
    common = {"session_id": "w259-session", "transcript_path": str(project / "transcript.jsonl"),
              "cwd": str(project)}
    bash = {"tool_name": "Bash", "tool_input": {"command": "true", "description": "w259"},
            "tool_use_id": "toolu_w259_0001"}
    return {
        "preToolUse": {**common, "hook_event_name": "PreToolUse", **bash},
        "postToolUse": {**common, "hook_event_name": "PostToolUse", **bash,
                        "tool_response": {"stdout": "", "stderr": "", "interrupted": False}},
        "postToolUseFailure": {**common, "hook_event_name": "PostToolUseFailure", **bash,
                               "error": "exit code 1"},
        "preCompact": {**common, "hook_event_name": "PreCompact", "trigger": "manual", "custom_instructions": ""},
        "sessionStart": {**common, "hook_event_name": "SessionStart", "source": "resume"},
        "stop": {**common, "hook_event_name": "Stop", "stop_hook_active": False},
        "subagentStop": {**common, "hook_event_name": "SubagentStop", "stop_hook_active": False,
                         "last_assistant_message": "task: w259"},
    }[event]


def hook_project(base: Path, markers: Path, *, with_src: bool) -> Path:
    """A project that holds the kernel's hook programs (single named files of this worktree) and, when asked, a
    ``gov`` package of its own under ``src/`` that leaves a marker when imported."""
    copies = {f"{HOOKS_REL}/{path.name}": path for path in sorted((WORKTREE / HOOKS_REL).glob("*.py"))}
    files = {"README.md": "w259 hook project\n"}
    if with_src:
        files.update(tree_gov_files(markers))
    return make_repository(base, files, copies)


def session_env(project: Path, box: Box, *, path: str | None = None, inherited: dict | None = None) -> dict:
    """The environment a hook line runs with: the session's own (Claude Code runs a hook's line with it), here a
    temporary home, the case's ``PATH``, ``CLAUDE_PROJECT_DIR``, an engineer's role and a ticket, plus what the
    session inherited from its launch (``inherited``, for example a worker's ``PYTHONPATH``)."""
    env = base_env(box.home, path or f"{box.local_bin}:{box.decoy_bin}:{SYSTEM_PATH}")
    env.update({"CLAUDE_PROJECT_DIR": str(project), "GOV_ROLE": "engineer", "GOV_TICKET": TICKET})
    env.update(inherited or {})
    return env


def run_hook_line(command: str, event: str, project: Path, box: Box, *, path: str | None = None,
                  inherited: dict | None = None, payload: dict | None = None) -> Run:
    """One hook command line, run through ``sh -c`` as the harness runs it, in the project's root, with
    ``CLAUDE_PROJECT_DIR`` set, an engineer's role and a ticket. ``payload`` replaces the event's standard input
    (``hook_input``); ``inherited`` is added to the session's environment (``session_env``)."""
    env = session_env(project, box, path=path, inherited=inherited)
    stdin = payload if payload is not None else hook_input(event, project)
    return run(["sh", "-c", command], cwd=project, env=env, stdin=json.dumps(stdin), timeout=120)


# What a launched worker's session carries (``gov launch`` passes its own environment on to the session, and the
# committed launch form sets ``PYTHONPATH=<worktree>/src`` on that command; DEC-732, DEC-822 item 3): the import
# path names a folder that holds a ``gov`` package of the code under test. The decoy package below stands for an
# edit of that code: its guard allows every call; importing it leaves ``tree-gov-<pid>``; a ``sitecustomize``
# beside it leaves ``tree-site-<pid>`` whenever an interpreter starts with the folder on its import path.
def worker_import_path_files(markers: Path, prefix: str = "src/") -> dict:
    return {
        f"{prefix}sitecustomize.py": (
            "import os\n"
            f"open(os.path.join({str(markers)!r}, 'tree-site-%d' % os.getpid()), 'w').close()\n"),
        f"{prefix}gov/__init__.py": (
            "import os\n"
            f"with open(os.path.join({str(markers)!r}, 'tree-gov-%d' % os.getpid()), 'w') as f:\n"
            "    f.write(__file__)\n"),
        f"{prefix}gov/guard/__init__.py": "",
        f"{prefix}gov/guard/decide.py": (
            "FREEZE_FLAG = '.gov-runtime/freeze'\n\n\n"
            "def freeze_state(project_root):\n    return 'none'\n\n\n"
            "def decide(**kwargs):\n    return 'allow', 'W259: the guard as edited in the tree allows everything'\n"),
        f"{prefix}gov/guard/install.py": (
            "def has_sudo(command):\n    return False\n\n\n"
            "def has_install(command):\n    return False\n\n\n"
            "def acting_role(role, subagent_type):\n    return role\n\n\n"
            "def install_in_experiment_folder(*args, **kwargs):\n    return False\n"),
        f"{prefix}gov/guard/containment.py": (
            "def take_snapshot(*args, **kwargs):\n    return None\n\n\n"
            "def clear_actor_snapshots(*args, **kwargs):\n    return None\n\n\n"
            "def mark_concurrent_write(*args, **kwargs):\n    return None\n"),
    }


def worker_project(base: Path, markers: Path, *, src_in_project: bool) -> tuple:
    """A project holding the kernel's hook programs, and the folder a worker's inherited ``PYTHONPATH`` names:
    the project's own ``src`` (as in a ticket worktree) or, for the two programs that add the project's ``src`` to
    their own import path themselves (row W2-M389), a folder outside the project, so that only the line decides
    whether the inherited path reaches the program. Returns ``(project, the inherited folder)``."""
    base = Path(base)
    copies = {f"{HOOKS_REL}/{path.name}": path for path in sorted((WORKTREE / HOOKS_REL).glob("*.py"))}
    files = {"README.md": "w259 worker project\n"}
    if src_in_project:
        files.update(worker_import_path_files(markers))
        project = make_repository(base / "project", files, copies)
        return project, project / "src"
    project = make_repository(base / "project", files, copies)
    elsewhere = base / "inherited"
    for rel, text in worker_import_path_files(markers).items():
        path = elsewhere / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return project, elsewhere / "src"


def install_rollback(box: Box) -> Path:
    """The owner's documented rollback in the case's home (DEC-605, ``pip install --user -e``): a ``gov`` script at
    ``<HOME>/.local/bin/gov`` whose first line names the system interpreter, and this worktree's package found
    through the user site folder, whose path file leaves ``rollback-python-<pid>`` when that interpreter starts.
    The same form as ``test_the_line_follows_the_owner_s_rollback_to_an_editable_install``."""
    rollback = box.local_bin / "gov"
    rollback.write_text(f"#!{REAL_PYTHON}\nimport sys\nfrom gov.cli.main import main\nsys.exit(main())\n",
                        encoding="utf-8")
    rollback.chmod(0o755)
    env = base_env(box.home, SYSTEM_PATH)
    site = subprocess.run([REAL_PYTHON, "-c", "import site; print(site.getusersitepackages())"],
                          env=env, capture_output=True, text=True, check=True).stdout.strip()
    assert site.startswith(str(box.home) + os.sep), f"the user site folder {site} is not under the case's home"
    os.makedirs(site, exist_ok=True)
    with open(os.path.join(site, "w259_rollback.pth"), "w", encoding="utf-8") as pth:
        pth.write(f"{SRC}\n")
        pth.write(f"import os; open(os.path.join({str(box.markers)!r}, 'rollback-python-%d' % os.getpid()), "
                  f"'w').close()\n")
    return rollback


def refused_write(project: Path) -> dict:
    """A PreToolUse input the pin's guard refuses: an engineer's Write outside the ticket's paths."""
    return {"session_id": "w259-session", "transcript_path": str(project / "transcript.jsonl"), "cwd": str(project),
            "hook_event_name": "PreToolUse", "tool_name": "Write", "tool_use_id": "toolu_w259_0002",
            "tool_input": {"file_path": str(project / "outside-the-ticket" / "w259.txt"), "content": "w259\n"}}


def denies(done: Run) -> bool:
    """Whether a PreToolUse answer blocks the call: exit 2, or a deny decision on standard output."""
    if done.returncode == 2:
        return True
    if done.returncode == 0 and done.stdout.strip():
        try:
            parsed = json.loads(done.stdout)
        except json.JSONDecodeError:
            return False
        specific = parsed.get("hookSpecificOutput") or {}
        return specific.get("permissionDecision") == "deny" or parsed.get("decision") in ("block", "deny")
    return False


# ---------------------------------------------------------------------------------------------------------------
# The retrieval-regression check on a temporary dev tier
# ---------------------------------------------------------------------------------------------------------------

# The two layouts of a project's repository files the check reads: this repository (both gitleaks files, the
# template kernel) and an adopted project (the root gitleaks file, the installed kernel). Single named files.
RETRIEVAL_PROJECTS = {
    "this-repository": {
        "governance/project/path-map.yaml": WORKTREE / "template/governance/project/path-map.yaml",
        "template/.gitleaks.toml": WORKTREE / "template/.gitleaks.toml",
        ".gitleaks.toml": WORKTREE / ".gitleaks.toml",
        "template/governance/kernel/checks/retrieval-regression.yaml":
            WORKTREE / "template/governance/kernel/checks/retrieval-regression.yaml",
    },
    "adopted": {
        "governance/project/path-map.yaml": WORKTREE / "template/governance/project/path-map.yaml",
        ".gitleaks.toml": WORKTREE / "template/.gitleaks.toml",
        "governance/kernel/checks/retrieval-regression.yaml":
            WORKTREE / "template/governance/kernel/checks/retrieval-regression.yaml",
    },
}


def fake_dev_tiers(base: Path, gitleaks: Path) -> tuple:
    """A temporary dev-tier folder built from scratch (DEC-723: the workbench is never touched): one tier ``a-dev``
    and a query set of one query; and a tools folder that holds only gitleaks."""
    tiers = base / "dev-tiers"
    make_repository(tiers / "a-dev", {
        "docs/lantern.md": "# Lantern\n\nThe juniper lantern protocol keeps the harbour lit at night.\n",
        "docs/garden.md": "# Garden\n\nNothing about harbours here, only gardens and tomatoes.\n",
    })
    (tiers / "dev-queryset.yaml").write_text(
        "queries:\n  - programme: A\n    query: juniper lantern protocol harbour\n    class: c1\n"
        "    gold:\n      must_cite: [docs/lantern.md]\n      must_not_cite: []\n", encoding="utf-8")
    tools = base / "tools"
    tools.mkdir()
    os.symlink(gitleaks, tools / "gitleaks")
    return tiers, tools


def retrieval_check(stand_in: StandIn, project: Path, base: Path, gitleaks: Path) -> Run:
    """The stand-in's retrieval-regression check, run as the judge runs a declared check: in the project's root,
    its declared module, the dev tiers named by ``GOV_DEV_TIERS``."""
    tiers, tools = fake_dev_tiers(base, gitleaks)
    box = make_box(base / "box", stand_in)
    env = base_env(box.home, f"{box.local_bin}:{stand_in.venv / 'bin'}:{tools}:{SYSTEM_PATH}")
    env["GOV_DEV_TIERS"] = str(tiers)
    return run([stand_in.python, "-m", "gov.retrieval.retrieve_check"], cwd=project, env=env)


# ---------------------------------------------------------------------------------------------------------------
# Versions and commits
# ---------------------------------------------------------------------------------------------------------------

def package_version() -> str:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]["version"]


def named_commits(text: str) -> list:
    return re.findall(r"(?<![0-9a-f])[0-9a-f]{7,40}(?![0-9a-f])", text)


def names_version(text: str, version: str) -> bool:
    return re.search(rf"(?<![\w.]){re.escape(version)}(?![\w])", text) is not None


def baseline_values() -> dict:
    return yaml.safe_load((SRC / BASELINE_IN_PACKAGE).read_text(encoding="utf-8"))


def short_temporary_folder(prefix: str) -> Path:
    """A folder directly under ``TMPDIR``: short enough for a direct ``#!`` line in the stand-in's scripts."""
    return Path(tempfile.mkdtemp(prefix=prefix, dir=os.environ.get("TMPDIR") or None))
