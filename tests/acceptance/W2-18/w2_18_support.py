"""Support code for the W2-18 acceptance tests: the pinned install (ticket DAEO-057v).

Public interfaces only: the ``gov`` command line (``gov install``, ``gov doctor --json``, ``gov --version``), the
pin's files on disk (``<common>/gov/pin.json``, ``<common>/gov/bin/gov``, the environment's site-packages), and the
kernel hook command lines as the template's ``.rulesync/hooks.jsonc`` writes them, run with ``bash -c``. No module of
this worktree's ``src/gov`` is imported here.

Everything runs in temporary folders: a stand-in Gov OS repository holding two fixture releases (W2-16's builders,
``build_gov_os_repository`` and ``build_release`` through the owner's seam), projects adopted from it with Copier,
and a fake ``HOME`` per run. The live pins under ``~/.local`` are never read or run: every environment built here
names its own ``HOME`` and a ``PATH`` without ``~/.local/bin``.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import re
import shutil
import site
import stat
import subprocess
import sys
import tarfile
from dataclasses import dataclass
from pathlib import Path

_HERE = Path(__file__).resolve().parent
for _folder in (_HERE.parent / "W2-16", _HERE.parent / "W1-39", _HERE.parent / "W1-07"):
    if str(_folder) not in sys.path:
        sys.path.insert(0, str(_folder))

import w2_16_support as w216  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
HOOKS_JSONC = REPO_ROOT / "template" / ".rulesync" / "hooks.jsonc"

# Two fixture releases; each release's CLI version (pyproject.toml at its commit) is the release version itself, so
# "A's version" means one string whichever the reader takes.
VERSION_A, VERSION_B = "0.9.0", "0.9.1"
TAG_A, TAG_B = f"v{VERSION_A}", f"v{VERSION_B}"
TICKET = "DEMO-w218"            # a ticket id of the kernel's grammar, for the checkpoint hooks (GOV_TICKET)

SYSTEM_PATH = "/usr/bin:/bin"   # no gov there (checked by ``no_gov_on``)
USER_BASE = os.environ.get("PYTHONUSERBASE") or site.getuserbase()
TIMEOUT_S = 600.0               # a wheel build and an environment: a wait, not a time the ticket promises
HOOK_TIMEOUT_S = 120.0

git = w216.git
make_sandbox = w216.make_sandbox
clone_folder = w216.clone_folder
commit_all = w216.commit_all


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256(path):
    return sha256_bytes(Path(path).read_bytes())


# --------------------------------------------------------------------------
# Running things
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Run:
    argv: tuple
    returncode: int
    stdout: str
    stderr: str

    @property
    def output(self):
        return self.stdout + "\n" + self.stderr

    def describe(self):
        return (f"{' '.join(map(str, self.argv))}\nexit code: {self.returncode}\nstdout:\n{self.stdout[-4000:]}\n"
                f"stderr:\n{self.stderr[-4000:]}")

    def envelope(self):
        try:
            data = json.loads(self.stdout)
        except ValueError:
            raise AssertionError(f"standard output is not one JSON document\n{self.describe()}") from None
        assert isinstance(data, dict), f"standard output is not a JSON object\n{self.describe()}"
        return data


def base_env(sandbox, path=SYSTEM_PATH, **extra):
    """A fresh environment: the sandbox's HOME (no ``.local/bin/gov`` there), a PATH without ``~/.local/bin``, the
    real user base for the user packages Python needs, no ``PYTHONPATH``, no ``GOV_*``."""
    env = {
        "PATH": path,
        "HOME": str(sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "LC_ALL": "C.UTF-8",
        "PYTHONUSERBASE": USER_BASE,
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "W2-18 tests", "GIT_AUTHOR_EMAIL": "w2-18@example.invalid",
        "GIT_COMMITTER_NAME": "W2-18 tests", "GIT_COMMITTER_EMAIL": "w2-18@example.invalid",
        "PIP_NO_INPUT": "1", "PIP_DISABLE_PIP_VERSION_CHECK": "1", "PIP_NO_CACHE_DIR": "1",
    }
    env.update({key: str(value) for key, value in extra.items()})
    return env


def run(argv, cwd, env, stdin=None, timeout=TIMEOUT_S):
    assert Path(cwd).resolve() != REPO_ROOT.resolve(), "no command of these tests runs in this worktree"
    try:
        done = subprocess.run([str(item) for item in argv], cwd=str(cwd), env=env, capture_output=True, text=True,
                              timeout=timeout, input=stdin if stdin is not None else "",)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{' '.join(map(str, argv))} did not end within {timeout:.0f} s") from None
    return Run(tuple(argv), done.returncode, done.stdout, done.stderr)


def checked(done, what):
    assert done.returncode == 0, f"{what} failed (a fixture step, not the feature)\n{done.describe()}"
    return done


def worktree_gov(cwd, sandbox, *args, **extra):
    """``gov <args>`` with this worktree's code, as ``python3 -m gov.cli.main`` with ``PYTHONPATH=<src>``."""
    env = base_env(sandbox, PYTHONPATH=SRC, **extra)
    return run((sys.executable, "-m", "gov.cli.main", *args), cwd, env)


def gov_console_script(sandbox):
    """One ``gov`` console script for this worktree's code (W2-16's ``write_gov_command``), in the sandbox."""
    return w216.write_gov_command(Path(sandbox.elsewhere) / "commands")


# --------------------------------------------------------------------------
# The stand-in Gov OS repository and its two releases
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Release:
    version: str
    tag: str
    manifest: dict
    manifest_bytes: bytes
    wheel: Path                     # the release's wheel, built here from the manifest's commit as gov release does

    @property
    def manifest_sha256(self):
        return sha256_bytes(self.manifest_bytes)

    @property
    def wheel_name(self):
        return self.manifest["wheel"]["name"]

    @property
    def wheel_sha256(self):
        return self.manifest["wheel"]["sha256"]


@dataclass(frozen=True)
class Releases:
    repo: Path
    a: Release
    b: Release

    def __getitem__(self, version):
        return {VERSION_A: self.a, VERSION_B: self.b}[version]


def set_cli_version(repo, version):
    path = Path(repo) / "pyproject.toml"
    text = path.read_text(encoding="utf-8")
    changed = re.sub(r'(?m)^version\s*=\s*"[^"]*"', f'version = "{version}"', text, count=1)
    path.write_text(changed, encoding="utf-8")
    commit_all(repo, f"the CLI version {version}")


def manifest_at(repo, tag, version):
    rel = f"docs/releases/{version}/manifest.json"
    data = subprocess.run(["git", "-C", str(repo), "show", f"{tag}:{rel}"], capture_output=True, check=True).stdout
    return data, json.loads(data)


def build_wheel(repo, commit, out):
    """The gov wheel of ``commit``, built as ``gov release`` builds it (docs/releases/README.md, the interface's
    "exactly as gov release builds it"): ``pyproject.toml`` and ``src/`` at the commit, setuptools' build backend,
    ``SOURCE_DATE_EPOCH`` the commit's time."""
    out = Path(out)
    archive = subprocess.run(["git", "-C", str(repo), "archive", "--format=tar", commit, "pyproject.toml", "src"],
                             capture_output=True, check=True).stdout
    source = out / "source"
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(source, filter="data")
    # Rewrite-Reason: F3 (fixes-015a): gov release's one build route writes gov/_build_info.py (the commit) into the
    # wheel, so the fixture's rebuild does the same or its sha256 can never equal the manifest's.
    if (source / "src" / "gov").is_dir():
        full = git(repo, "rev-parse", "--verify", f"{commit}^{{commit}}").strip()
        (source / "src" / "gov" / "_build_info.py").write_text(f'COMMIT = "{full}"\n', encoding="utf-8")
    epoch = git(repo, "show", "-s", "--format=%ct", commit).strip()
    env = {key: value for key, value in os.environ.items() if not key.startswith("PYTHON")}
    env.update(SOURCE_DATE_EPOCH=epoch, PYTHONUSERBASE=USER_BASE)
    wheels = out / "wheel"
    done = subprocess.run([sys.executable, "-c", "import sys; from setuptools import build_meta; "
                           "print(build_meta.build_wheel(sys.argv[1]))", str(wheels)], cwd=source, env=env,
                          capture_output=True, text=True, timeout=TIMEOUT_S)
    found = sorted(wheels.glob("*.whl")) if wheels.is_dir() else []
    assert done.returncode == 0 and len(found) == 1, f"the fixture's wheel build failed\n{done.stderr[-3000:]}"
    return found[0]


def build_releases(base):
    """A stand-in Gov OS repository (W2-16's) holding releases A and B, tagged as the owner tags them; each release's
    wheel built here too and checked against its manifest (the build is reproducible, or no case could pass)."""
    base = Path(base)
    repo = w216.build_gov_os_repository(base / "gov-os")
    sandbox = make_sandbox(base / "sandbox")
    made = {}
    for version, tag in ((VERSION_A, TAG_A), (VERSION_B, TAG_B)):
        set_cli_version(repo, version)
        w216.build_release(repo, sandbox, version, tag=tag)
        data, manifest = manifest_at(repo, tag, version)
        wheel = build_wheel(repo, manifest["commit"], base / f"wheel-{version}")
        assert wheel.name == manifest["wheel"]["name"] and sha256(wheel) == manifest["wheel"]["sha256"], (
            f"release {version}: the wheel built again from {manifest['commit']} is {wheel.name} {sha256(wheel)}, "
            f"the manifest names {manifest['wheel']}: the build is not reproducible on this machine")
        made[version] = Release(version, tag, manifest, data, wheel)
    return Releases(repo, made[VERSION_A], made[VERSION_B])


def adopt(copier_bin, releases, destination, tag=TAG_A):
    """A product adopted from ``tag`` by ``copier copy`` (its task writes the lock), committed."""
    destination = Path(destination)
    sandbox = make_sandbox(destination.parent / f"{destination.name}-sandbox")
    return w216.create_project(copier_bin, sandbox, releases.repo, destination, tag)


def copy_project(project, destination):
    """A copy of a project that holds no pin (a pin's environment holds absolute paths: it is never copied)."""
    assert not (common_dir(project) / "gov").exists(), "a project with a pin is never copied"
    return clone_folder(project, destination)


def tamper_wheel_hash(releases, destination, version=VERSION_A):
    """A copy of the stand-in whose release ``version`` names another wheel sha256, its ``manifest.sha256`` made to
    agree, the tag moved onto that commit: only the wheel check can fail. Returns (repo, the false sha256)."""
    repo = clone_folder(releases.repo, destination)
    release = releases[version]
    false = sha256_bytes(b"W2-18: a wheel hash that belongs to nothing\n")
    folder = repo / "docs" / "releases" / version
    data = release.manifest_bytes.replace(release.wheel_sha256.encode(), false.encode())
    assert data != release.manifest_bytes
    git(repo, "checkout", "-q", "-B", w216.INTEGRATION_BRANCH, release.tag)
    (folder / "manifest.json").write_bytes(data)
    (folder / "manifest.sha256").write_text(f"{sha256_bytes(data)}  manifest.json\n", encoding="utf-8")
    commit_all(repo, f"release {version}'s record, its wheel hash changed")
    git(repo, "tag", "-f", release.tag)
    return repo, false


# --------------------------------------------------------------------------
# The pin
# --------------------------------------------------------------------------

def common_dir(project):
    return Path(git(project, "rev-parse", "--path-format=absolute", "--git-common-dir").strip())


def pin_folder(project):
    return common_dir(project) / "gov"


def read_pin(project):
    path = pin_folder(project) / "pin.json"
    assert path.is_file(), f"there is no {path}"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{path} is not a JSON object"
    return data


def site_packages(environment):
    found = sorted(Path(environment).glob("lib/python*/site-packages"))
    assert len(found) == 1, f"{environment} has {len(found)} site-packages folders"
    return found[0]


def flat_editable_source(releases, version, destination):
    """The gov package of release ``version`` in a flat layout (``gov/`` beside ``pyproject.toml``, no ``src/``), for
    an editable install that is not a source tree's ``src/gov``: only the case ``editable`` applies to it."""
    destination = Path(destination)
    commit = releases[version].manifest["commit"]
    archive = subprocess.run(["git", "-C", str(releases.repo), "archive", "--format=tar", commit, "src/gov"],
                             capture_output=True, check=True).stdout
    unpacked = destination.parent / f"{destination.name}-unpacked"
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(unpacked, filter="data")
    destination.mkdir(parents=True)
    shutil.move(str(unpacked / "src" / "gov"), str(destination / "gov"))
    (destination / "pyproject.toml").write_text(
        '[build-system]\nrequires = ["setuptools>=68"]\nbuild-backend = "setuptools.build_meta"\n\n'
        f'[project]\nname = "gov"\nversion = "{version}"\nrequires-python = ">=3.11"\n\n'
        '[project.scripts]\ngov = "gov.cli.main:main"\n\n'
        '[tool.setuptools.packages.find]\nwhere = ["."]\ninclude = ["gov", "gov.*"]\n', encoding="utf-8")
    return destination


def plant_pin(project, releases, version, sandbox, editable=None):
    """A pin made by hand as the interface states it: ``<common>/gov/envs/<version>/`` (a ``--system-site-packages``
    virtual environment) with the release's wheel installed by ``pip install --no-deps --no-index`` (or, with
    ``editable``, ``pip install -e`` of that folder), ``bin/gov`` a link to the environment's gov, and ``pin.json``
    naming the release. Returns the environment."""
    release = releases[version]
    pin = pin_folder(project)
    environment = pin / "envs" / version
    env = base_env(sandbox)
    checked(run((sys.executable, "-m", "venv", "--system-site-packages", "--without-pip", environment),
                sandbox.tmpdir, env), "creating the planted pin's environment")
    python = environment / "bin" / "python"
    what = ("-e", editable) if editable else (release.wheel,)
    extra = ("--no-build-isolation",) if editable else ()
    checked(run((python, "-m", "pip", "install", "--no-deps", "--no-index", *extra, *what), sandbox.tmpdir, env),
            "installing gov into the planted pin's environment")
    (pin / "bin").mkdir(parents=True, exist_ok=True)
    (pin / "bin" / "gov").symlink_to(environment / "bin" / "gov")
    (pin / "pin.json").write_text(json.dumps({
        "version": version,
        "wheel": {"name": release.wheel_name, "sha256": release.wheel_sha256},
        "manifest_sha256": release.manifest_sha256,
        "source": str(releases.repo),
        "commit": release.manifest["commit"],
        "environment": str(environment),
        "hash_check": "passed",
    }, indent=2) + "\n", encoding="utf-8")
    return environment


def tree_state(folder):
    """Every entry under ``folder`` (no link followed): a link's target, a file's sha256 and mode, a folder."""
    folder = Path(folder)
    if not folder.exists() and not folder.is_symlink():
        return None
    state = {}
    for top, names, files in os.walk(folder):
        for name in names + files:
            path = Path(top) / name
            rel = path.relative_to(folder).as_posix()
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                state[rel] = ("link", os.readlink(path))
            elif stat.S_ISDIR(mode):
                state[rel] = ("dir",)
            else:
                state[rel] = ("file", sha256(path), stat.S_IMODE(mode))
    return state


def state_difference(before, after):
    if before is None or after is None:
        return f"before: {'absent' if before is None else 'present'}, after: {'absent' if after is None else 'present'}"
    changed = sorted(rel for rel in set(before) | set(after) if before.get(rel) != after.get(rel))
    return f"{len(changed)} entries differ: {changed[:15]}"


def working_tree_state(project):
    """The project's files outside ``.git``, its HEAD and its git status."""
    root = Path(project)
    files = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if rel == ".git" or rel.startswith(".git/"):
            continue
        if path.is_symlink():
            files[rel] = ("link", os.readlink(path))
        elif path.is_file():
            files[rel] = ("file", sha256(path))
    return {"files": files, "head": git(root, "rev-parse", "HEAD").strip(),
            "status": git(root, "status", "--porcelain", "--untracked-files=all")}


# --------------------------------------------------------------------------
# gov doctor --json, its section install
# --------------------------------------------------------------------------

INSTALL_SECTION = "install"


@dataclass(frozen=True)
class Doctor:
    run: Run
    report: dict
    section: dict

    def describe(self):
        return f"install section: {json.dumps(self.section, indent=1)[:3000]}\n{self.run.describe()}"


def doctor_of(done):
    envelope = done.envelope()
    report = envelope.get("result") or (envelope.get("error") or {}).get("details") or {}
    assert isinstance(report, dict) and report, f"gov doctor gave no report\n{done.describe()}"
    section = report.get(INSTALL_SECTION)
    assert isinstance(section, dict), (
        f"gov doctor's report has no section {INSTALL_SECTION!r} (sections: {sorted(report)})\n{done.describe()}")
    return Doctor(done, report, section)


def doctor_from_pin(project, sandbox):
    """``<common>/gov/bin/gov doctor --json`` in the project: the doctor the pin runs."""
    return doctor_of(run((pin_folder(project) / "bin" / "gov", "doctor", "--json"), project, base_env(sandbox)))


def doctor_from_source_tree(project, sandbox, src):
    """``gov doctor --json`` in the project by a gov imported from the source tree ``src`` (``PYTHONPATH``), with
    ``GOV_PIN=off``."""
    env = base_env(sandbox, PYTHONPATH=src, GOV_PIN="off")
    return doctor_of(run((sys.executable, "-m", "gov.cli.main", "doctor", "--json"), project, env))


def assert_fails_with_case(result, case, why):
    section = result.section
    assert section.get("status") == "fail" and section.get("case") == case, (
        f"the install section does not fail with case {case!r} although {why}\n{result.describe()}")
    assert result.run.returncode != 0, f"gov doctor exits 0 although {why}\n{result.describe()}"


# --------------------------------------------------------------------------
# The kernel hook command lines
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class HookLine:
    event: str
    index: int
    matcher: str
    command: str

    @property
    def ident(self):
        return f"{self.event}-{self.index}"


def _strip_jsonc(text):
    """JSON with ``//`` and ``/* */`` comments outside strings, and trailing commas, as plain JSON."""
    out, i, quoted = [], 0, False
    while i < len(text):
        c = text[i]
        if quoted:
            out.append(c)
            if c == "\\":
                out.append(text[i + 1])
                i += 1
            elif c == '"':
                quoted = False
        elif c == '"':
            quoted = True
            out.append(c)
        elif text.startswith("//", i):
            while i < len(text) and text[i] != "\n":
                i += 1
            continue
        elif text.startswith("/*", i):
            i = text.index("*/", i) + 2
            continue
        else:
            out.append(c)
        i += 1
    return re.sub(r",(\s*[}\]])", r"\1", "".join(out))


def hook_lines():
    """Every command line of the template's ``.rulesync/hooks.jsonc``, by event."""
    data = json.loads(_strip_jsonc(HOOKS_JSONC.read_text(encoding="utf-8")))
    lines = []
    for event, entries in (data.get("hooks") or {}).items():
        for index, entry in enumerate(entries):
            if entry.get("type", "command") == "command" and entry.get("command"):
                lines.append(HookLine(event, index, entry.get("matcher", ""), entry["command"]))
    return lines


TWELVE_FIELDS = ("task", "status", "work_completed", "files_changed", "evidence", "tests", "discoveries", "risks",
                 "lessons", "proposed_decisions", "unresolved", "recommended_next_action")


def payload(event, project, transcript):
    """A JSON payload of the event, as Claude Code gives it, for a call the hook itself has no reason to refuse."""
    common = {"session_id": "w2-18-session", "transcript_path": str(transcript), "cwd": str(project)}
    name = event[0].upper() + event[1:]
    bash = {"tool_name": "Bash", "tool_input": {"command": "ls"}}
    specific = {
        "preToolUse": bash,
        "postToolUse": {**bash, "tool_response": {"stdout": "", "stderr": "", "interrupted": False}},
        "postToolUseFailure": {**bash, "error": "exit code 1"},
        "sessionStart": {"source": "compact"},
        "stop": {"stop_hook_active": False},
        "subagentStop": {"stop_hook_active": False,
                         "last_assistant_message": json.dumps({field: "done" for field in TWELVE_FIELDS})},
        "preCompact": {"trigger": "auto", "custom_instructions": ""},
    }.get(event, {})
    return json.dumps({**common, "hook_event_name": name, **specific})


def run_hook(line, tree, env):
    """The command line with ``bash -c`` in ``tree``, ``CLAUDE_PROJECT_DIR=<tree>``, its event's payload on stdin."""
    transcript = Path(env["TMPDIR"]) / "transcript.jsonl"
    transcript.touch()
    env = {**env, "CLAUDE_PROJECT_DIR": str(tree)}
    return run(("bash", "-c", line.command), tree, env, stdin=payload(line.event, tree, transcript),
               timeout=HOOK_TIMEOUT_S)


def no_gov_on(env, cwd):
    """The environment finds no gov: none on PATH, and its python3 imports none."""
    found = run(("bash", "-c", "command -v gov"), cwd, env)
    assert found.returncode != 0, f"a gov is on the case's PATH: {found.stdout.strip()}"
    imported = run(("bash", "-c", "python3 -c 'import gov'"), cwd, env)
    assert imported.returncode != 0, "the case's python3 imports a gov"


def add_ticket(project, ticket=TICKET):
    path = Path(project) / ".tickets" / f"{ticket}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\nid: {ticket}\nstatus: in_progress\ntitle: a ticket of the product\n---\n\n# {ticket}\n",
                    encoding="utf-8")


def add_product_gov_package(project, marker):
    """The product's own package named gov, under its ``src/`` beside a ``pyproject.toml``: importing its
    ``gov.checkpoint.record`` writes ``marker``."""
    root = Path(project)
    (root / "pyproject.toml").write_text('[project]\nname = "product"\nversion = "1.0.0"\n', encoding="utf-8")
    package = root / "src" / "gov"
    (package / "checkpoint").mkdir(parents=True)
    (package / "__init__.py").write_text('"""The product\'s own package named gov."""\n', encoding="utf-8")
    (package / "checkpoint" / "__init__.py").write_text("", encoding="utf-8")
    (package / "checkpoint" / "record.py").write_text(
        "from pathlib import Path\n"
        f"Path({str(marker)!r}).write_text('the product\\'s gov.checkpoint.record was imported\\n')\n\n"
        "def write(*args, **kwargs):\n"
        f"    Path({str(marker)!r}).write_text('the product\\'s gov.checkpoint.record.write ran\\n')\n"
        "    return {}\n\n"
        "def brief(*args, **kwargs):\n"
        "    return ''\n", encoding="utf-8")


def records(tree, ticket=TICKET):
    folder = Path(tree) / ".gov-runtime" / "scratch" / "checkpoints" / ticket
    return sorted(path.name for path in folder.glob(f"CP-{ticket}-*.md")) if folder.is_dir() else []


VERSION_TOKEN = r"(?<![\w.]){}(?![\w.])"


def prints_version(output, version):
    return re.search(VERSION_TOKEN.format(re.escape(version)), output) is not None
