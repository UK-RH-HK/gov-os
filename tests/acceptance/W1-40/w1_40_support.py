"""Support code for the W1-40 acceptance tests (lefthook hooks and the CI workflow).

How the tests run:

- **The hook configuration as lefthook runs it.** The repository's ``lefthook.yml`` (one named file) is put
  into a temporary repository built with ``git init``; ``lefthook install`` runs there and nowhere else; the
  tests then commit and push with plain ``git``. The push goes to a bare repository in the same temporary folder.
- **The workflow as text, and as the commands its steps name.** ``Runner`` does what the hosted runner does with
  a push, as far as it can be done offline: a fresh shallow fetch of the pushed commit from the bare repository,
  then every ``run:`` step in order under ``bash -e``. A ``uses:`` step is not run; a step that downloads a tool
  is not run either and is judged as text.
- **A project that is green or red by construction.** The temporary project declares three checks of its own,
  one per tier G1, G2 and G3 (the tier is a field of every check declaration, DEC-186). Each leaves a mark in a
  folder outside the project when it runs and fails when a file there tells it to. No model is involved.
- **The evidence record, through git.** DEC-489 makes it a git note on the head commit under a ref of its own.
  No case names the ref: ``Project.records`` asks the bare repository for every notes ref it holds other than
  git's default one and reads the note of a commit there with ``git notes``.
- **Nothing is written in this repository**, and no hook is installed in it. No network.
"""

from __future__ import annotations

import os
import pwd
import re
import shutil
import subprocess
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"

# The files the ticket fixes (its allowed_paths).
LEFTHOOK_YML = REPO_ROOT / "lefthook.yml"
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
TEMPLATE_LEFTHOOK = REPO_ROOT / "template" / "lefthook.yml.jinja"
TEMPLATE_WORKFLOWS = REPO_ROOT / "template" / ".github" / "workflows"

# Sources the cases read.
GITLEAKS_RULES = REPO_ROOT / "template" / ".gitleaks.toml"   # DEC-288: the template's rules, no allowlist
TOOL_REGISTRY = REPO_ROOT / "governance" / "project" / "tool-registry.yaml"
CHECKS_REL = "template/governance/kernel/checks"             # DEC-186, gov.cli.checks.CHECKS_DIR

SYSTEM_PATH = "/usr/bin:/bin"
CALL_TIMEOUT_S = 300.0
BRANCH = "main"
NOTES = "refs/notes/"                    # git keeps notes under this prefix and refuses any other
DEFAULT_NOTES = "refs/notes/commits"     # git's default notes ref: the record is not there (DEC-489)
NO_G3 = "no G3 check declared"           # DEC-489: the record's words where the project declares no G3 check

# The three checks of the temporary project: tier -> (id, family).
TIER_CHECKS = {
    "G1": ("w1-40-g1", "schema/invariants"),
    "G2": ("w1-40-g2", "graph integrity"),
    "G3": ("w1-40-g3", "retrieval regression"),
}

# Planted values (never written whole in this file). ``PLAIN`` is a token by the project's rules that nothing
# shelters. The two sheltered ones are tokens by the project's rules that gitleaks' built-in global allowlist
# shelters when the project's file extends the defaults (DEC-347; observed with gitleaks 8.30.1 by W1-16).
_RUN = "abcdefghijklm" + "nopqrstuvwxyz"
PLAIN = "sk_" + "7Qd2" + "Xk9Lm4Wp8Zr3Tb6V"
SHELTERED = {
    "alphabet": "sk_" + "7Qd2" + _RUN + "X9",
    "false": "tok-" + "9fK2mQ7x" + "fal" + "se" + "Lp0Zr4Tb",
}


class Absent(Exception):
    """A file the ticket delivers is not there."""


class Unsupported(Exception):
    """The workflow uses something this offline runner cannot evaluate."""


# --------------------------------------------------------------------------
# tools
# --------------------------------------------------------------------------

def real_tool(name):
    """The path of a registered tool on this machine, or None. Looks on PATH, then in ``~/.local/bin``."""
    found = shutil.which(name)
    if found:
        return found
    local = Path(pwd.getpwuid(os.getuid()).pw_dir) / ".local" / "bin" / name
    return str(local) if local.is_file() and os.access(local, os.X_OK) else None


def registry():
    """``name -> entry`` of the tool registry."""
    data = yaml.safe_load(TOOL_REGISTRY.read_text(encoding="utf-8"))
    return {entry["name"]: entry for entry in data["tools"]}


def _gov_launcher(path):
    """The console script an install of this worktree's package would generate."""
    target = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["scripts"]["gov"]
    module, _, attribute = target.partition(":")
    path.write_text(
        f"#!{sys.executable}\n"
        "import sys\n"
        f"sys.path.insert(0, {str(SRC)!r})\n"
        f"from {module} import {attribute} as _main\n"
        "sys.argv[0] = 'gov'\n"
        "sys.exit(_main())\n", encoding="utf-8")
    path.chmod(0o755)


def _script(path, text):
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


@dataclass
class Machine:
    """A machine as a hook or a CI step sees it: a home, a PATH, and the folder the checks leave their marks in.

    ``lefthook``, ``gitleaks`` and ``gov`` are there or not. A tool that is not there is on no folder of PATH;
    without ``gov`` the package cannot be imported either. ``leak`` puts a stand-in ``gitleaks`` first that
    reports a finding whatever it is given (exit 1, as gitleaks does).
    """

    base: Path
    marks: Path
    lefthook: bool = True
    gitleaks: bool = True
    gov: bool = True
    leak: bool = False
    own_lefthook: bool = False   # a copy of the binary in this machine's folder, which a test can take away
    extra: dict = field(default_factory=dict)

    def __post_init__(self):
        self.base = Path(self.base)
        self.bin = self.base / "bin"
        self.home = self.base / "home"
        for folder in (self.bin, self.home, self.marks):
            folder.mkdir(parents=True, exist_ok=True)
        for name, wanted in (("lefthook", self.lefthook), ("gitleaks", self.gitleaks and not self.leak)):
            if shutil.which(name, path=SYSTEM_PATH):
                raise Unsupported(f"{name} is in a system folder of this machine: it cannot be withheld")
            if wanted and name == "lefthook" and self.own_lefthook:
                shutil.copy2(real_tool(name), self.bin / name)
            elif wanted:
                (self.bin / name).symlink_to(real_tool(name))
        if self.leak:
            _script(self.bin / "gitleaks", "#!/bin/sh\necho 'leaks found: 1' >&2\nexit 1\n")
        if self.gov:
            _gov_launcher(self.bin / "gov")
        # Tools that fetch or run a model, or ask for a GPU: a call leaves a mark and fails.
        for name in ("ollama", "hf", "huggingface-cli", "nvidia-smi"):
            _script(self.bin / name, f"#!/bin/sh\necho \"{name} $*\" >> \"$W1_40_MARKS/model-tool\"\nexit 97\n")

    def env(self, **more):
        import pytest
        paths = [str(Path(pytest.__file__).resolve().parents[1])]
        if self.gov:
            paths.insert(0, str(SRC))
        env = {
            "PATH": f"{self.bin}:{SYSTEM_PATH}",
            "HOME": str(self.home),
            "LC_ALL": "C",
            "TMPDIR": os.environ.get("TMPDIR", "/tmp"),
            "PYTHONPATH": os.pathsep.join(paths),
            "PYTHONDONTWRITEBYTECODE": "1",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_AUTHOR_NAME": "W1-40 fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_NAME": "W1-40 fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
            "W1_40_MARKS": str(self.marks),
        }
        env.update(self.extra)
        env.update(more)
        return env


def sh(args, cwd, env, check=False):
    done = subprocess.run([str(arg) for arg in args], cwd=str(cwd), env=env, capture_output=True, text=True,
                          timeout=CALL_TIMEOUT_S)
    if check and done.returncode != 0:
        raise AssertionError(f"{' '.join(str(arg) for arg in args)} failed in {cwd}:\n{done.stdout}\n{done.stderr}")
    return done


def said(done):
    return f"exit {done.returncode}\n--- stdout\n{done.stdout[-3000:]}\n--- stderr\n{done.stderr[-3000:]}"


# --------------------------------------------------------------------------
# the temporary project
# --------------------------------------------------------------------------

class Project:
    """A temporary repository with the hooks of ``lefthook.yml`` installed and a bare repository as ``origin``.

    Green by construction: its three checks pass, it holds no secret, its one test passes. Its first commit is
    made and pushed before the hooks are installed, so every later commit and push of a test meets the hooks.

    ``tiers`` names the tiers the project declares a check for (all three unless told otherwise). With
    ``hooks=False`` the project has no hook file and no hook: it is for the cases that call ``gov`` directly,
    and needs neither lefthook nor gitleaks.
    """

    def __init__(self, base, marks, tiers=tuple(TIER_CHECKS), hooks=True):
        if hooks and not LEFTHOOK_YML.is_file():
            raise Absent("lefthook.yml is absent from the repository root")
        self.base = Path(base)
        self.root = self.base / "project"
        self.remote = self.base / "origin.git"
        self.marks = Path(marks)
        self.tiers = tuple(tiers)
        self.setup = Machine(self.base / "setup-machine", self.marks, lefthook=hooks, gitleaks=hooks,
                             own_lefthook=hooks)
        self.root.mkdir(parents=True)
        env = self.setup.env()
        sh(["git", "init", "-q", "--bare", "-b", BRANCH, self.remote], self.base, env, check=True)
        sh(["git", "init", "-q", "-b", BRANCH], self.root, env, check=True)
        self.write("README.md", "# A project\n")
        self.write(".gitignore", ".gov-runtime/\n__pycache__/\n.pytest_cache/\n")
        self.write(".gitleaks.toml", GITLEAKS_RULES.read_text(encoding="utf-8"))
        if hooks:
            self.write("lefthook.yml", LEFTHOOK_YML.read_text(encoding="utf-8"))
        self.write("tests/test_ok.py", "def test_ok():\n    assert True\n")
        for tier in self.tiers:
            self.declare(*TIER_CHECKS[tier], tier)
        sh(["git", "add", "-A"], self.root, env, check=True)
        sh(["git", "commit", "-q", "-m", "initial project"], self.root, env, check=True)
        sh(["git", "remote", "add", "origin", self.remote], self.root, env, check=True)
        sh(["git", "push", "-q", "origin", BRANCH], self.root, env, check=True)
        if not hooks:
            return
        installed = sh(["lefthook", "install"], self.root, env)
        if installed.returncode != 0:
            raise AssertionError(f"lefthook install refused the repository's lefthook.yml:\n{said(installed)}")

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def declare(self, check_id, family, tier, severity="hard-block"):
        """A check of ``tier``: it leaves a line in ``$W1_40_MARKS/<tier>`` and fails while ``fail-<tier>`` is there."""
        command = (f'echo run >> "$W1_40_MARKS/{tier}" && test ! -e "$W1_40_MARKS/fail-{tier}"')
        self.write(f"{CHECKS_REL}/{check_id}.yaml", yaml.safe_dump(
            {"id": check_id, "family": family, "tier": tier, "severity": severity, "command": command},
            sort_keys=False))

    def lose_lefthook(self):
        """Take lefthook away from where it was at install too: the installed hook remembers that place.

        ``lefthook install`` writes the binary's own path into the hook as a second place to look. The project
        is set up with a copy of the binary in its own folder, so that taking the copy away takes lefthook away.
        """
        (self.setup.bin / "lefthook").unlink()

    # -- marks ---------------------------------------------------------

    def fail(self, tier, failing=True):
        flag = self.marks / f"fail-{tier}"
        flag.write_text("fail\n") if failing else flag.unlink(missing_ok=True)

    def ran(self, tier):
        """How many times the check of ``tier`` has run."""
        mark = self.marks / tier
        return len(mark.read_text().splitlines()) if mark.is_file() else 0

    def forget_runs(self):
        for tier in TIER_CHECKS:
            (self.marks / tier).unlink(missing_ok=True)
        (self.marks / "model-tool").unlink(missing_ok=True)

    def model_tool_calls(self):
        mark = self.marks / "model-tool"
        return mark.read_text().splitlines() if mark.is_file() else []

    # -- git -----------------------------------------------------------

    def head(self):
        return sh(["git", "rev-parse", "HEAD"], self.root, self.setup.env(), check=True).stdout.strip()

    def remote_head(self, remote=None):
        done = sh(["git", "rev-parse", "--verify", "-q", f"refs/heads/{BRANCH}"], remote or self.remote,
                  self.setup.env())
        return done.stdout.strip() or None

    def add_remote(self, name):
        """A second bare repository in the temporary folder, known to the project as ``name``. Returns its path."""
        path = self.base / f"{name}.git"
        env = self.setup.env()
        sh(["git", "init", "-q", "--bare", "-b", BRANCH, path], self.base, env, check=True)
        sh(["git", "remote", "add", name, path], self.root, env, check=True)
        return path

    def gov(self, machine, *args):
        """``gov <args>`` in the project, as a hook would call it on ``machine``."""
        return sh(["gov", *args], self.root, machine.env())

    # -- the evidence record: a git note (DEC-489) ---------------------

    def notes_refs(self, repo=None):
        """Every notes ref ``repo`` holds (the bare ``origin`` unless told otherwise), git's default one included."""
        done = sh(["git", "for-each-ref", "--format=%(refname)", NOTES], repo or self.remote, self.setup.env(),
                  check=True)
        return sorted(done.stdout.split())

    def records(self, sha, repo=None):
        """``ref -> text`` of the note of ``sha`` under every notes ref of ``repo`` other than git's default."""
        repo = repo or self.remote
        found = {}
        for ref in self.notes_refs(repo):
            if ref == DEFAULT_NOTES:
                continue
            done = sh(["git", "notes", "--ref", ref, "show", sha], repo, self.setup.env())
            if done.returncode == 0:
                found[ref] = done.stdout
        return found

    def commit(self, machine, rel="notes.txt", text=None, verify=True):
        """Stage one file and commit it on ``machine``. Returns the finished process and whether HEAD moved."""
        before = self.head()
        self.write(rel, text if text is not None else f"a line after {before}\n")
        env = machine.env()
        sh(["git", "add", "--", rel], self.root, env, check=True)
        args = ["git", "commit", "-m", f"change {rel}"] + ([] if verify else ["--no-verify"])
        done = sh(args, self.root, env)
        return done, self.head() != before

    def unhooked_commit(self, rel="notes.txt", text=None):
        done, moved = self.commit(self.setup, rel, text, verify=False)
        assert moved, f"the fixture commit failed:\n{said(done)}"
        return self.head()

    def push(self, machine, verify=True, remote="origin"):
        """``git push <remote> main`` on ``machine``. Returns the finished process and whether the remote now holds HEAD."""
        args = ["git", "push", remote, BRANCH] + ([] if verify else ["--no-verify"])
        done = sh(args, self.root, machine.env())
        held = self.remote_head(None if remote == "origin" else self.base / f"{remote}.git")
        return done, held == self.head()

    def through_the_hooks(self, machine):
        """A new commit, made and pushed through the hooks on ``machine``. Returns its id."""
        done, moved = self.commit(machine)
        assert moved, f"a clean commit was refused:\n{said(done)}"
        done, arrived = self.push(machine)
        assert arrived, f"a push with every declared check passing was refused:\n{said(done)}"
        return self.head()


# --------------------------------------------------------------------------
# the workflow files
# --------------------------------------------------------------------------

def workflow_files(folder=None):
    folder = WORKFLOWS if folder is None else folder
    if not folder.is_dir():
        return []
    return sorted(path for path in folder.rglob("*") if path.is_file() and path.suffix in (".yml", ".yaml"))


def load_workflow(path):
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise AssertionError(f"{path}: the workflow is not a map")
    if True in data:  # YAML 1.1 reads the key ``on`` as a boolean
        data["on"] = data.pop(True)
    return data


def triggers(workflow):
    on = workflow.get("on")
    if isinstance(on, str):
        return {on}
    return set(on or ())


def push_workflows():
    """``(path, workflow)`` for every workflow of the repository that a push starts."""
    found = [(path, load_workflow(path)) for path in workflow_files()]
    found = [(path, workflow) for path, workflow in found if "push" in triggers(workflow)]
    if not found:
        raise Absent("no workflow under .github/workflows/ runs on push")
    return found


def steps_of(workflow):
    """``(job id, job, step)`` for every step, in file order."""
    for job_id, job in (workflow.get("jobs") or {}).items():
        for step in job.get("steps") or ():
            yield job_id, job, step


_DOWNLOAD = re.compile(
    r"\b(curl|wget)\b|\bgh\s+release\b|\bpip3?\s+install\b|\buv\s+(tool|pip)\s+install\b|\buv\s+sync\b"
    r"|\bnpm\s+(install|i|ci)\b|\bapt(-get)?\s+install\b|\bgo\s+install\b|\bbrew\s+install\b")


def is_download(step):
    """Whether a ``run:`` step fetches something from the network: it is judged as text and not run offline."""
    return bool(_DOWNLOAD.search(str(step.get("run", ""))))


_EXPRESSION = re.compile(r"\$\{\{\s*(.*?)\s*\}\}")


@dataclass
class StepRun:
    name: str
    kind: str          # "run", "uses", "download", "skipped"
    returncode: int | None = None
    output: str = ""


@dataclass
class CiResult:
    steps: list

    @property
    def ran(self):
        return [step for step in self.steps if step.kind == "run"]

    @property
    def green(self):
        return bool(self.ran) and all(step.returncode == 0 for step in self.ran)

    @property
    def output(self):
        """What the steps that ran printed, in order: the job's log as far as this runner has one."""
        return "\n".join(step.output for step in self.ran)

    def __str__(self):
        lines = []
        for step in self.steps:
            lines.append(f"[{step.kind}] {step.name}: exit {step.returncode}")
            if step.kind == "run" and step.returncode != 0:
                lines.append(step.output[-2500:])
        return "\n".join(lines)


class Runner:
    """What the hosted runner does with a push of ``sha`` on ``main``, offline.

    The tree comes as ``actions/checkout`` brings it: a new repository, ``origin`` set, one fetch of the pushed
    branch at the depth the checkout step asks for (1 where it asks for none), nothing else fetched: no note, no
    other ref. Then every ``run:`` step of every job of every push workflow runs in order under ``bash -e``
    (``-o pipefail`` where the step names ``shell: bash``), with the ``env`` of the workflow, job and step. A
    step after a failed one runs only with ``if: always()``. A job is green when every step that ran exits 0.
    """

    def __init__(self, project, machine, base):
        self.project, self.machine, self.base = project, machine, Path(base)

    def _checkout(self, workspace, depth):
        env = self.machine.env()
        workspace.mkdir(parents=True)
        url = f"file://{self.project.remote}"
        sh(["git", "init", "-q", "-b", BRANCH], workspace, env, check=True)
        sh(["git", "remote", "add", "origin", url], workspace, env, check=True)
        fetch = ["git", "fetch", "-q", "--no-tags", "origin", f"+refs/heads/{BRANCH}:refs/remotes/origin/{BRANCH}"]
        if depth:
            fetch.insert(3, f"--depth={depth}")
        sh(fetch, workspace, env, check=True)
        sh(["git", "checkout", "-q", "-B", BRANCH, f"refs/remotes/origin/{BRANCH}"], workspace, env, check=True)
        return sh(["git", "rev-parse", "HEAD"], workspace, env, check=True).stdout.strip()

    @staticmethod
    def _value(text, context):
        def replace(match):
            name = match.group(1)
            if name not in context:
                raise Unsupported(f"the expression ${{{{ {name} }}}} cannot be evaluated offline")
            return context[name]
        return _EXPRESSION.sub(replace, str(text))

    def run(self):
        steps = []
        for number, (path, workflow) in enumerate(push_workflows()):
            for job_id, job in (workflow.get("jobs") or {}).items():
                if "strategy" in job or "if" in job or "container" in job or "services" in job:
                    raise Unsupported(f"{path.name}: job {job_id} uses strategy, if, container or services")
                checkouts = [step for step in job.get("steps") or () if str(step.get("uses", "")).startswith("actions/checkout")]
                if not checkouts:
                    raise AssertionError(f"{path.name}: job {job_id} has no actions/checkout step: it has no tree to check")
                depth = int((checkouts[0].get("with") or {}).get("fetch-depth", 1))
                workspace = self.base / f"runner-{number}-{job_id}" / "workspace"
                sha = self._checkout(workspace, depth)
                context = {"github.sha": sha, "github.ref": f"refs/heads/{BRANCH}", "github.ref_name": BRANCH,
                           "github.workspace": str(workspace), "github.event_name": "push"}
                base_env = self.machine.env(
                    CI="true", GITHUB_ACTIONS="true", GITHUB_SHA=sha, GITHUB_REF=f"refs/heads/{BRANCH}",
                    GITHUB_REF_NAME=BRANCH, GITHUB_WORKSPACE=str(workspace), GITHUB_EVENT_NAME="push")
                for scope in (workflow, job):
                    for key, value in (scope.get("env") or {}).items():
                        base_env[key] = self._value(value, context)
                failed = False
                for index, step in enumerate(job.get("steps") or ()):
                    name = f"{path.name}:{job_id}:{step.get('name') or step.get('id') or index}"
                    condition = str(step.get("if", "")).strip()
                    if condition not in ("", "always()", "${{ always() }}"):
                        raise Unsupported(f"{name}: the condition {condition!r} cannot be evaluated offline")
                    if "uses" in step:
                        steps.append(StepRun(name, "uses"))
                        continue
                    if "run" not in step:
                        continue
                    if is_download(step):
                        steps.append(StepRun(name, "download"))
                        continue
                    if failed and not condition:
                        steps.append(StepRun(name, "skipped"))
                        continue
                    env = dict(base_env)
                    for key, value in (step.get("env") or {}).items():
                        env[key] = self._value(value, context)
                    shell = str(step.get("shell", (job.get("defaults") or {}).get("run", {}).get("shell", "")))
                    if shell not in ("", "bash", "sh"):
                        raise Unsupported(f"{name}: shell {shell!r}")
                    args = {"": ["bash", "-e", "-c"], "bash": ["bash", "--noprofile", "--norc", "-e", "-o", "pipefail", "-c"],
                            "sh": ["sh", "-e", "-c"]}[shell]
                    cwd = workspace / str(step.get("working-directory", "."))
                    done = sh(args + [self._value(step["run"], context)], cwd, env)
                    steps.append(StepRun(name, "run", done.returncode, done.stdout + done.stderr))
                    failed = failed or done.returncode != 0
        return CiResult(steps)


# --------------------------------------------------------------------------
# gitleaks, called directly: what one scan with the project's file finds
# --------------------------------------------------------------------------

def single_scan_finds(content, machine, config=GITLEAKS_RULES):
    """Whether one gitleaks scan with the project's file as it stands (defaults extended) flags ``content``."""
    done = subprocess.run(
        ["gitleaks", "stdin", "--no-banner", "--redact", "--config", str(config), "--log-level", "error",
         "--exit-code", "3"],
        input="\n" + content, capture_output=True, text=True, env=machine.env(), timeout=CALL_TIMEOUT_S)
    if done.returncode not in (0, 3):
        raise AssertionError(f"gitleaks did not decide:\n{said(done)}")
    return done.returncode == 3
