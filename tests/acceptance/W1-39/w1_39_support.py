"""Support code for the W1-39 acceptance tests (standard library, PyYAML, and W1-07's support).

W1-39 makes this repository a Copier template (DEC-023): ``copier.yml`` at the
root, ``template/`` as what a project receives (ADR-0002 section 5), and a
``framework.lock`` written at install that ``gov doctor`` verifies (CAP-02.a).
The tests use three public interfaces and nothing else: the tool ``copier``
(the registered version, DEC-083), the ``gov doctor`` command, and the files a
created project holds.

**The one permitted copy.** Copier, given a git repository as its source,
clones all of it. This repository is therefore never Copier's source or its
destination. ``assemble_source`` builds the template source in a temporary
folder from the single file ``copier.yml`` and the files under ``template/``
alone, file by file, and makes that folder a git repository of its own, with a
commit and a tag. Nothing under ``governance/project/`` of this repository is
ever copied, listed or read here, except the one named file
``governance/project/tool-registry.yaml`` (the registered Copier version).
No tag is created in this repository.

**What a Copier task finds.** Copier is run with ``--defaults --trust``: no
question is asked, and the tasks ``copier.yml`` declares may run. They run with
``gov`` on ``PATH`` (this worktree's command line) and with the ``gov`` package
importable by ``python3`` (``PYTHONPATH``), which stands in for the installed
package; ``HOME`` is an empty temporary folder; there is no network.
"""

from __future__ import annotations

import hashlib
import json
import os
import pwd
import re
import shutil
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

_W1_07_DIR = str(Path(__file__).resolve().parents[1] / "W1-07")
if _W1_07_DIR not in sys.path:
    sys.path.insert(0, _W1_07_DIR)

import w1_07_support as base  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]

# --- what the sources fix -------------------------------------------------
COPIER_YML_REL = "copier.yml"                      # ADR-0002 section 5; the ticket's allowed_paths
TEMPLATE_REL = "template"                          # ADR-0002 section 5 (_subdirectory: template)
KERNEL_REL = "governance/kernel"                   # ADR-0002 section 5: Copier-owned
OVERLAY_REL = "governance/project"                 # ADR-0002 section 5: the overlay
LOCK_REL = "governance/framework.lock"             # ADR-0002 section 5; allowed path template/governance/framework.lock*
HOOKS_REL = "governance/kernel/hooks"              # W1-04: where Copier puts the hooks in a product
RULESYNC_REL = ".rulesync"                         # W1-38
DEFAULT_ANSWERS_REL = ".copier-answers.yml"        # DEC-023; Copier's own default
TOOL_REGISTRY_REL = "governance/project/tool-registry.yaml"   # DEC-083, DEC-127: one named file
MANIFEST_KEY = "manifest"                          # CAP-02.a "file-hash manifest"; the key gov doctor reads (W1-27)
DOCTOR_LOCK_SECTION = "framework_lock"             # the name of gov doctor's section today (W1-27)

# The top-level entries ADR-0002 section 5 gives a product repository, and Copier's answers file.
PRODUCT_TOP_LEVEL = frozenset({
    "AGENTS.md", "CLAUDE.md", ".claude", ".rulesync", "governance", "openspec", "spec", ".tickets", "tests",
    "lefthook.yml", ".github", ".gitleaks.toml", ".gov-runtime", ".gitignore",
})
# The trees that are the Gov OS repository's own (ADR-0002 section 5) and never a product's.
GOV_OS_ONLY = ("copier.yml", "template", "src", "cli", "fixtures", "docs", "pyproject.toml")
# The separate trees success line 3 names, as ADR-0002 section 5 places them in this repository.
GOV_OS_TREES = {
    "kernel template": "template/governance/kernel",
    "CLI": "src/gov",
    "tests": "tests/acceptance",
    "fixtures": "fixtures",
    "lessons": "docs/lessons",
    "plan": "docs/plan",
    "docs": "docs",
}

FIRST_TAG = "v0.1.0"
SECOND_TAG = "v0.2.0"
COPIER_TIMEOUT_S = 180.0
SHA256_RE = re.compile(r"[0-9a-f]{64}")

git = base.git
commit_all = base.commit_all
make_sandbox = base.make_sandbox


class TemplateMissing(AssertionError):
    """This repository is not a Copier template yet."""


# --------------------------------------------------------------------------
# Copier itself (DEC-083: registered, never installed by a test)
# --------------------------------------------------------------------------

def _real_home():
    return Path(pwd.getpwuid(os.getuid()).pw_dir)


def registered_copier_version():
    """The Copier version this repository's tool registry records."""
    data = yaml.safe_load((REPO_ROOT / TOOL_REGISTRY_REL).read_text(encoding="utf-8"))
    for entry in data.get("tools", []):
        if isinstance(entry, dict) and entry.get("name") == "copier":
            return str(entry["version"])
    raise AssertionError(f"{TOOL_REGISTRY_REL} has no entry for copier")


def copier_binary():
    """The ``copier`` command at its registered place, then on ``PATH``; ``None`` where there is none."""
    candidate = _real_home() / ".local" / "bin" / "copier"
    if candidate.is_file():
        return candidate
    found = shutil.which("copier")
    return Path(found) if found else None


def require_copier():
    """The path of the registered Copier, or an ``AssertionError`` that says what is needed. Never a skip."""
    binary = copier_binary()
    wanted = registered_copier_version()
    assert binary is not None, (
        f"this suite needs the tool copier {wanted} ({TOOL_REGISTRY_REL}); it is neither at ~/.local/bin/copier "
        f"nor on PATH. Nothing is installed by a test (DEC-083)."
    )
    try:
        done = subprocess.run([str(binary), "--version"], capture_output=True, text=True, timeout=60,
                              stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AssertionError(f"this suite needs copier {wanted}; {binary} --version did not run: {exc}") from None
    found = re.search(r"\d+\.\d+\.\d+", done.stdout + done.stderr)
    assert done.returncode == 0 and found and found.group(0) == wanted, (
        f"this suite needs copier {wanted} ({TOOL_REGISTRY_REL}); {binary} --version answered "
        f"{(done.stdout + done.stderr).strip()!r} with exit code {done.returncode}"
    )
    return binary


# --------------------------------------------------------------------------
# The template source: a temporary git repository of copier.yml and template/ alone
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Release:
    tag: str | None
    commit: str      # the full commit id


@dataclass(frozen=True)
class Source:
    path: Path
    first: Release

    @property
    def template(self):
        return self.path / TEMPLATE_REL

    def configuration(self):
        """``copier.yml`` of the source, parsed."""
        data = yaml.safe_load((self.path / COPIER_YML_REL).read_text(encoding="utf-8"))
        assert isinstance(data, dict), f"{COPIER_YML_REL} is not a YAML map"
        return data

    def answers_rel(self):
        """Where Copier writes its answers in a project: ``_answers_file`` of ``copier.yml``, else Copier's default."""
        value = self.configuration().get("_answers_file")
        return value if isinstance(value, str) and value else DEFAULT_ANSWERS_REL

    def suffix(self):
        """The suffix of a file Copier renders (``_templates_suffix``, by default ``.jinja``)."""
        value = self.configuration().get("_templates_suffix")
        return value if isinstance(value, str) else ".jinja"

    def plain_files(self, below):
        """``{relative path: absolute path}`` of the template's files under ``below`` that Copier copies as they are.

        A rendered file (templates suffix) or a file whose name is itself an expression is left out.
        """
        suffix = self.suffix()
        found = {}
        for path in sorted((self.template / below).rglob("*")):
            rel = path.relative_to(self.template).as_posix()
            if not path.is_file() or "{{" in rel or "{%" in rel or (suffix and rel.endswith(suffix)):
                continue
            found[rel] = path
        return found


def template_listing():
    """The files of this repository that make the template source: ``copier.yml`` and those under ``template/``.

    Tracked files and untracked, unignored ones; the listing is limited to those two paths.
    """
    listing = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--",
         "copier.yml", "template"],
        capture_output=True, text=True, check=True,
    ).stdout
    return sorted(set(item for item in listing.split("\0") if item))


def assemble_source(destination):
    """Build the template source in ``destination`` (a temporary folder), commit it and tag it ``FIRST_TAG``."""
    destination = Path(destination)
    if not (REPO_ROOT / COPIER_YML_REL).is_file():
        raise TemplateMissing(
            f"no {COPIER_YML_REL} yet: this repository is not a Copier template, so there is nothing for "
            f"`copier copy` to copy (ADR-0002 section 5, DEC-023)"
        )
    destination.mkdir(parents=True, exist_ok=True)
    for rel in template_listing():
        origin = REPO_ROOT / rel
        target = destination / rel
        if not (origin.is_file() or origin.is_symlink()):
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if origin.is_symlink():
            target.symlink_to(os.readlink(origin))
        else:
            shutil.copy2(origin, target)
    git(destination, "init", "-q", "-b", "main")
    return Source(destination, release(destination, FIRST_TAG, "template source"))


def release(source_path, tag, message="a later release"):
    """Commit the template source as it stands and, when ``tag`` is given, tag the commit. Returns the ``Release``."""
    git(source_path, "add", "-A")
    git(source_path, "commit", "-q", "--allow-empty", "-m", message)
    if tag:
        git(source_path, "tag", tag)
    return Release(tag, git(source_path, "rev-parse", "HEAD").strip())


def write_template_file(source, rel, text):
    """Write ``rel`` (a path as a project sees it) into the temporary template source."""
    path = source.template / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# Running Copier
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Done:
    argv: tuple
    returncode: int
    stdout: str
    stderr: str

    def describe(self):
        return (f"{' '.join(self.argv)}\nexit code: {self.returncode}\nstdout:\n{self.stdout[-4000:]}\n"
                f"stderr:\n{self.stderr[-4000:]}")


def _write_gov_command(folder):
    """An executable ``gov`` in ``folder``: this worktree's command line, as an install would provide it."""
    module, attribute = base.entry_point(REPO_ROOT)
    folder.mkdir(parents=True, exist_ok=True)
    command = folder / "gov"
    command.write_text(
        f"#!{sys.executable}\n"
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
    command.chmod(command.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return command


def copier_environment(sandbox):
    commands = Path(sandbox.elsewhere) / "commands"
    _write_gov_command(commands)
    return {
        "PATH": f"{commands}{os.pathsep}{Path(sys.executable).parent}{os.pathsep}"
                f"{os.environ.get('PATH', '/usr/bin:/bin')}",
        "HOME": str(sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(REPO_ROOT / "src"),
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "W1-39 tests", "GIT_AUTHOR_EMAIL": "w1-39@example.invalid",
        "GIT_COMMITTER_NAME": "W1-39 tests", "GIT_COMMITTER_EMAIL": "w1-39@example.invalid",
    }


def run_copier(binary, sandbox, cwd, *args):
    for forbidden in (REPO_ROOT,):
        assert Path(cwd).resolve() != forbidden.resolve() and str(forbidden) not in args, \
            "Copier is never given this repository as its source or its destination"
    argv = (str(binary), *args)
    try:
        done = subprocess.run(argv, cwd=str(cwd), env=copier_environment(sandbox), capture_output=True, text=True,
                              timeout=COPIER_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{' '.join(argv)} did not end within {COPIER_TIMEOUT_S:.0f} s") from None
    return Done(("copier", *args), done.returncode, done.stdout, done.stderr)


def copy(binary, sandbox, source, destination, ref=FIRST_TAG):
    """``copier copy --defaults --trust --vcs-ref <ref> <source> <destination>``; the run, whatever its exit code."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    return run_copier(binary, sandbox, destination.parent, "copy", "--defaults", "--trust", "--vcs-ref", ref,
                      str(source.path), str(destination))


def create_project(binary, sandbox, source, destination, ref=FIRST_TAG):
    """A project created by ``copier copy`` and committed as a git repository of its own."""
    done = copy(binary, sandbox, source, destination, ref=ref)
    assert done.returncode == 0, f"`copier copy` failed\n{done.describe()}"
    destination = Path(destination)
    if not (destination / ".git").exists():
        git(destination, "init", "-q", "-b", "main")
    commit_all(destination, "created by copier copy")
    return destination


def update(binary, sandbox, source, project, ref=SECOND_TAG):
    """``copier update --defaults --trust --vcs-ref <ref>`` in the project; the run, whatever its exit code."""
    args = ["update", "--defaults", "--trust", "--vcs-ref", ref]
    answers = source.answers_rel()
    if answers != DEFAULT_ANSWERS_REL:
        args += ["--answers-file", answers]
    return run_copier(binary, sandbox, project, *args)


# --------------------------------------------------------------------------
# Files of a project
# --------------------------------------------------------------------------

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def files_under(project, below=""):
    """Relative POSIX paths of every file under ``below`` in the project, git's own folder left out."""
    root = Path(project)
    start = root / below if below else root
    found = []
    for path in sorted(start.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if rel == ".git" or rel.startswith(".git/"):
            continue
        if path.is_file() or path.is_symlink():
            found.append(rel)
    return found


def kernel_files(project):
    files = files_under(project, KERNEL_REL)
    assert files, f"the project has no file under {KERNEL_REL}/"
    return files


def is_executable(path):
    return bool(Path(path).stat().st_mode & stat.S_IXUSR)


# --------------------------------------------------------------------------
# The lock
# --------------------------------------------------------------------------

def lock_path(project):
    return Path(project) / LOCK_REL


def lock_text(project):
    path = lock_path(project)
    assert path.is_file(), f"the project has no {LOCK_REL} (ADR-0002 section 5)"
    return path.read_text(encoding="utf-8")


def read_lock(project):
    """The lock as ``gov doctor`` reads it: one YAML map."""
    try:
        data = yaml.safe_load(lock_text(project))
    except yaml.YAMLError as exc:
        raise AssertionError(f"{LOCK_REL} is not YAML: {exc}") from None
    assert isinstance(data, dict), f"{LOCK_REL} is not a YAML map"
    return data


def manifest_of(project):
    """``{path relative to the project root: sha256}`` of the lock's file-hash manifest (CAP-02.a)."""
    manifest = read_lock(project).get(MANIFEST_KEY)
    assert isinstance(manifest, dict) and manifest, \
        f"{LOCK_REL} has no file-hash manifest under the key {MANIFEST_KEY!r} (a non-empty map of path to hash)"
    return manifest


def rewrite_lock(project, change):
    """Apply ``change`` to the parsed lock and write it back as YAML."""
    data = read_lock(project)
    change(data)
    lock_path(project).write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


# --------------------------------------------------------------------------
# gov doctor
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Doctor:
    run: object          # W1-07's Run
    report: dict         # the doctor's sections
    section: dict        # its framework-lock section

    @property
    def text(self):
        return json.dumps(self.section, sort_keys=True)

    @property
    def claims_match(self):
        """The section says the installed kernel matches its lock (CAP-02: MATCH), or counts as passed."""
        return bool(re.search(r"\bMATCH\b", self.text)) or self.section.get("status") == "pass"

    @property
    def reports_drift(self):
        return bool(re.search(r"\bDRIFT\b", self.text))

    def names(self, rel):
        return rel in self.text

    def describe(self):
        return f"framework-lock section: {self.text}\n{self.run.describe()}"


def doctor(project, sandbox):
    """Run ``gov doctor --json`` in the project with this worktree's code; the report and its framework-lock section."""
    run = base.run_gov_with_code(REPO_ROOT, project, sandbox, "doctor", "--json")
    envelope = run.envelope()
    report = envelope.get("result") or (envelope.get("error") or {}).get("details") or {}
    assert isinstance(report, dict) and report, f"gov doctor gave no report\n{run.describe()}"
    section = report.get(DOCTOR_LOCK_SECTION)
    assert isinstance(section, dict), f"gov doctor's report has no {DOCTOR_LOCK_SECTION} section\n{run.describe()}"
    return Doctor(run, report, section)


def assert_not_a_match(result, why):
    """Measured or refused (DEC-449, DEC-454): the lock part neither says MATCH nor counts as passed."""
    assert not result.claims_match, f"gov doctor reports the lock as matching although {why}\n{result.describe()}"


def assert_drift_naming(result, rel, why):
    assert_not_a_match(result, why)
    assert result.reports_drift and result.names(rel), \
        f"gov doctor does not report DRIFT naming {rel} although {why}\n{result.describe()}"
    assert result.run.returncode != 0 and result.run.envelope().get("ok") is False, \
        f"gov doctor exits 0 although {why}\n{result.describe()}"
