"""Support code for the W1-30 acceptance tests (``gov close``).

W1-30 builds the ``gov close`` command: it runs a ticket's acceptance tests,
requires Implements: and Task: trailers, runs checks and containment, writes a
checkpoint and a close record (a consumption receipt), tracks iteration counts,
and enforces the probe-record gate for FULL-profile tickets.

How the tests run:

- **Through public interfaces only**: the ``gov close`` command line (W1-07's
  console-script stand-in), its API-0002 envelope and exit code; ``gov check``
  for the product-traceability family check.
- **Nothing is written in this worktree** (DEC-322). Every project is a
  temporary git repository: its own ``.tickets/``, its own commits, its own
  acceptance tests. The code under test is this worktree's ``src/``.
- **Before ``gov close`` runs, the project is committed**, so the command may
  read the ticket, its commits, and their trailers.
- **Deterministic, no network.**
"""

from __future__ import annotations

import json
import os
import re
import shutil
import site
import subprocess
import sys
import time
import venv
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
for _name in ("W1-07", "W1-09", "W1-11", "W1-26"):
    _folder = str(_HERE.parent / _name)
    if _folder not in sys.path:
        sys.path.insert(0, _folder)

import w1_07_support as cli_support  # noqa: E402
import w1_09_support as tasks_support  # noqa: E402
import w1_11_support as decisions_support  # noqa: E402
import w1_26_support as check_support  # noqa: E402

# Planned revision (DEC-190): ``close`` is built by W1-30.
BUILT_LATER = cli_support.BUILT_LATER
NOT_BUILT = cli_support.NOT_BUILT
assert "close" in BUILT_LATER, "w1_07_support must list close in BUILT_LATER"
assert "close" not in NOT_BUILT, "w1_07_support must remove close from NOT_BUILT"

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
COMMAND = "close"
NOT_IMPLEMENTED = cli_support.NOT_IMPLEMENTED
CHECKS_REL = cli_support.CHECKS_REL

# Exit codes (API-0002).
EXIT_OK = 0
EXIT_GOV_ERROR = 1
EXIT_CHECK_FAILED = 3
EXIT_BLOCKED = 4

# Identities.
OWNER = decisions_support.OWNER
AGENT = decisions_support.AGENT
FIRST_DATE = decisions_support.FIRST_DATE

IMPLEMENTER = {
    "name": "The Implementer",
    "email": "impl@example.invalid",
    "trailers": ("Task: PROJ-aaaa", "Role: engineer"),
}
REVIEWER = {
    "name": "The Reviewer",
    "email": "reviewer@example.invalid",
    "trailers": ("Role: independent-auditor",),
}
ORCHESTRATOR = {
    "name": "The Orchestrator",
    "email": "orch@example.invalid",
    "trailers": ("Role: orchestrator",),
}
TEST_DESIGNER = {
    "name": "The Test Designer",
    "email": "designer@example.invalid",
    "trailers": ("Task: PROJ-aaaa", "Role: independent-test-designer"),
}
DESIGNER_ROLE = "Role: independent-test-designer"
ENGINEER_ROLE = "Role: engineer"

# Where the roles may write, from ``tests/acceptance/W1-50/README.md`` ("Allowed paths of a commit's trailers",
# "Ticket files"): a ticket file is the orchestrator's, an acceptance test is the test designer's.
TICKETS_PREFIX = ".tickets/"
ACCEPTANCE_PREFIX = "tests/acceptance/"

# The record every fixture ticket names as its source (``tasks_support.ticket_text``: ``sources: [DEC-000]``).
BASE_SOURCE = "DEC-000"

# The six finding dispositions (L-0077, DEC-435, A3 settlement: short names).
DISPOSITIONS = ("repair", "reuse", "delete", "narrow", "defer", "owner")

# Governance file prefixes whose change forces a check re-run at close (A7, CAP-38.d). The installed kernel
# (``governance/kernel/``) is among them since round 8 (DEC-487).
GOVERNANCE_PREFIXES = (
    "governance/kernel/",
    "template/governance/kernel/checks/",
    "template/governance/kernel/schemas/",
    "governance/project/",
    "template/governance/kernel/hooks/",
    "template/governance/kernel/skills/",
    "template/governance/kernel/policies/",
    "template/governance/kernel/roles/",
)

# Iteration count storage (A6): under .gov-runtime/, inaccessible to workers.
ITERATION_DIR = ".gov-runtime/iterations"

# The 17 families (from W1-26).
FAMILIES = check_support.FAMILIES
PRODUCT_TRACEABILITY = "product traceability"

TEMPLATE_OPENSPEC = REPO_ROOT / "template" / "openspec"

# Where a project writes its settings for ``gov close`` (README, round 12, settlement 21): top-level keys of
# its path map, the one project file every command is handed (DEC-185, DEC-479).
PATH_MAP_REL = "governance/project/path-map.yaml"
WORKERS_KEY = "close_workers"
TIME_LIMIT_KEY = "close_timeout"
# The projects of this suite set the number of parallel workers of a close small (DEC-549, P-2): a close
# under test does not start as many workers as the machine gives inside a parallel run of the suite.
SUITE_WORKERS = 2
SUITE_SETTINGS = {WORKERS_KEY: SUITE_WORKERS}


# The keys of a path map whose value is a commit id, full or abbreviated (DEC-479, DEC-482). An id is text
# whatever its characters: one of digits only (``65534367``) written bare is a number to YAML, and the check
# that reads it is handed no commit id. These values are therefore written quoted.
COMMIT_ID_KEYS = ("trailers_base", "decision_citations_base")


def path_map_text(settings):
    """The text of a path map that holds ``settings`` as top-level keys, one on a line, and no namespace (the
    one key the loader requires of a path map). A value is written as given, but for a key that holds a commit
    id (``COMMIT_ID_KEYS``), whose value is written as quoted text."""
    def written(key, value):
        return json.dumps(str(value)) if key in COMMIT_ID_KEYS else value
    return "namespaces: {}\n" + "".join(f"{key}: {written(key, value)}\n" for key, value in settings.items())


# --------------------------------------------------------------------------
# The sandbox: its own home, the installed packages of the interpreter running the suite
# --------------------------------------------------------------------------

def installed_packages_env():
    """What keeps the installed packages in sight when ``HOME`` is the sandbox's.

    Of everything an interpreter imports, only its per-user folder is found through ``HOME``. The interpreter
    running the suite says where its own is (``site.getuserbase()``), and ``PYTHONUSERBASE`` gives the same
    folder to the interpreter a case starts and to every interpreter that one starts in turn. Where the running
    interpreter uses no per-user folder (a virtual environment), nothing is needed and nothing is set.
    """
    return {"PYTHONUSERBASE": site.getuserbase()} if site.ENABLE_USER_SITE else {}


def sandbox_env(sandbox):
    """The environment of every process this suite starts: W1-07's stand-in environment (the sandbox's own
    ``HOME``, ``TMPDIR`` and bytecode folder, ``src/`` on ``PYTHONPATH``) and the installed packages of the
    interpreter running the suite."""
    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(SRC),
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
        **installed_packages_env(),
    }


def run_gov(project_root, sandbox, *args, python=None, env=None):
    """Run ``gov <args>`` in the project through W1-07's console-script stand-in, as
    ``cli_support.run_gov_with_code`` does, in ``sandbox_env``. ``python`` is another interpreter than the one
    running the suite and ``env`` replaces the environment; only the case without a test runner gives them."""
    launcher = cli_support.write_launcher(REPO_ROOT, sandbox)
    limit = cli_support.COMMAND_TIMEOUT_S
    started = time.perf_counter()
    try:
        done = subprocess.run([str(python or sys.executable), str(launcher), *args], cwd=str(project_root),
                              env=sandbox_env(sandbox) if env is None else env, capture_output=True, text=True,
                              timeout=limit, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"gov {' '.join(args)} did not end within {limit:.0f} s") from None
    return cli_support.Run(tuple(args), done.returncode, done.stdout, done.stderr, time.perf_counter() - started)


def can_import(module, sandbox, python=None, env=None):
    """Whether the interpreter a case starts finds ``module``, asked of that interpreter in that environment."""
    done = subprocess.run([str(python or sys.executable), "-c",
                           "import importlib.util, sys\n"
                           "sys.exit(0 if importlib.util.find_spec(sys.argv[1]) else 1)\n", module],
                          env=sandbox_env(sandbox) if env is None else env, cwd=str(sandbox.elsewhere),
                          capture_output=True, text=True, stdin=subprocess.DEVNULL)
    assert done.returncode in (0, 1), f"the interpreter did not answer:\n{done.stdout}\n{done.stderr}"
    return done.returncode == 0


# What makes up the test runner in a folder of installed packages.
_TEST_RUNNER_NAMES = ("pytest", "_pytest", "pytest.py", "py.test")


def interpreter_without_test_runner(base, sandbox):
    """An interpreter that has every installed package of the one running the suite except pytest, and the
    environment to start it in: ``(python, env)``.

    The interpreter is a virtual environment without packages of its own, so it sees none of the machine's
    folders of installed packages, wherever pytest lies on this machine. Each of those folders is given back on
    ``PYTHONPATH`` as a folder of links to everything in it but the test runner. ``PATH`` names the virtual
    environment first, so that ``python3`` is that interpreter too.
    """
    base = Path(base)
    venv.EnvBuilder(with_pip=False, symlinks=True, system_site_packages=False).create(base / "venv")
    python = base / "venv" / "bin" / "python3"
    assert python.exists(), f"the virtual environment has no interpreter at {python}"
    folders = list(site.getsitepackages())
    if site.ENABLE_USER_SITE:
        folders.append(site.getusersitepackages())
    mirrors = []
    for number, folder in enumerate(dict.fromkeys(folders)):
        if not Path(folder).is_dir():
            continue
        mirror = base / "packages" / str(number)
        mirror.mkdir(parents=True)
        for entry in Path(folder).iterdir():
            name = entry.name.lower()
            if name in _TEST_RUNNER_NAMES or name.startswith("pytest-") or name.endswith(".pth"):
                continue
            (mirror / entry.name).symlink_to(entry)
        mirrors.append(str(mirror))
    env = {
        "PATH": str(python.parent) + os.pathsep + os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": os.pathsep.join([str(SRC), *mirrors]),
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
    }
    return python, env


# --------------------------------------------------------------------------
# git and the temporary project
# --------------------------------------------------------------------------

def git(project, *args, who=AGENT, date=None, check=True):
    d = date or FIRST_DATE.format(minute=0)
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(Path(project).parent),
        "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_AUTHOR_NAME": who["name"], "GIT_AUTHOR_EMAIL": who["email"],
        "GIT_COMMITTER_NAME": who["name"], "GIT_COMMITTER_EMAIL": who["email"],
        "GIT_AUTHOR_DATE": d, "GIT_COMMITTER_DATE": d,
    }
    done = subprocess.run(["git", "-C", str(project), *args],
                          capture_output=True, text=True, env=env)
    if check and done.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {project}:\n{done.stderr}")
    return done.stdout


def write(root, rel, text):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def commit_all(project, message="fixture", who=OWNER, trailers=(), minute=0):
    date = FIRST_DATE.format(minute=minute)
    git(project, "add", "-A", who=who, date=date)
    args = ["commit", "-q", "--allow-empty", "--no-gpg-sign", "-m", message]
    effective = trailers if trailers else who.get("trailers", ())
    for t in effective:
        args += ["--trailer", t]
    git(project, *args, who=who, date=date)
    return git(project, "rev-parse", "HEAD", who=who).strip()


# --------------------------------------------------------------------------
# Ticket helpers
# --------------------------------------------------------------------------

def ticket_text(ticket_id, wbs, profile="STANDARD", allowed_paths=None, **keys):
    """A ticket file, optionally overriding profile and allowed_paths.

    The ticket is in progress unless ``status`` says otherwise: W1-50's judgement gives a ticket's paths to a
    worker's commit only while the ticket is in progress (DEC-318).
    """
    keys.setdefault("status", "in_progress")
    text = tasks_support.ticket_text(ticket_id, wbs, **keys)
    if profile != "STANDARD":
        text = text.replace("profile: STANDARD", f"profile: {profile}")
    if allowed_paths is not None:
        old_block = "allowed_paths:\n- src/example/**"
        new_block = "allowed_paths:\n" + "\n".join(f"- {p}" for p in allowed_paths)
        text = text.replace(old_block, new_block)
    return text


def ticket_path(ticket_id):
    return f".tickets/{ticket_id}.md"


def read_ticket_frontmatter(root, ticket_id):
    path = Path(root) / ticket_path(ticket_id)
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    return yaml.safe_load(parts[1]) or {}


# --------------------------------------------------------------------------
# Record helpers
# --------------------------------------------------------------------------

def record(record_id, record_type, status, title=None, **keys):
    if title is None:
        title = f"Record {record_id}"
    return decisions_support.record(record_id, record_type, status, title=title, **keys)


def decision(record_id, status, **keys):
    return decisions_support.decision(record_id, status, **keys)


def skill_file(name, version, content_marker="default content"):
    return check_support.skill_file(name, version, content_marker)


def probe_record(ticket_id, reviewer_session="reviewer-001",
                 implementer_session="impl-001",
                 reviewer_wrote_nothing=True,
                 commissioned_by="orchestrator",
                 judged_by="orchestrator",
                 judgement="pass",
                 probed_commit=None):
    """A probe record for a FULL-profile ticket (DEC-137, A5)."""
    probe_id = f"PR-{ticket_id}"
    front = {
        "id": probe_id,
        "type": "probe",
        "status": "ACTIVE",
        "state_class": "NARRATIVE",
        "task": ticket_id,
        "reviewer_session": reviewer_session,
        "implementer_session": implementer_session,
        "reviewer_wrote_nothing": reviewer_wrote_nothing,
        "commissioned_by": commissioned_by,
        "judged_by": judged_by,
        "judgement": judgement,
    }
    if probed_commit is not None:
        front["probed_commit"] = probed_commit
    text = "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n"
    text += f"# {probe_id} — Probe record for {ticket_id}\n\nPost-green probe.\n"
    return text


# --------------------------------------------------------------------------
# A temporary project for gov close
# --------------------------------------------------------------------------

class Project:
    """A temporary git repository that gov close can run in."""

    def __init__(self, root, checks=None, settings=SUITE_SETTINGS):
        """``checks`` is the project's own set of check declarations (``declared_check``); without it the
        project holds a copy of the kernel's declarations. ``settings`` are the project's settings for
        ``gov close``, written as a project writes them (``path_map_text``; a value is written as given, so
        a case may give a wrong one); ``None`` is a project without a path map."""
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._minute = 0
        self._checks = checks
        self._settings = settings
        self._init_minimal()

    def _init_minimal(self):
        git(self.root, "init", "-q", "-b", "main")
        write(self.root, "README.md", "# A project\n")
        write(self.root, ".gitignore", ".gov-runtime/\n")
        write(self.root, "pyproject.toml",
              (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        shutil.copytree(REPO_ROOT / "src", self.root / "src")
        self._copy_kernel_templates()
        if self._settings is not None:
            write(self.root, PATH_MAP_REL, path_map_text(self._settings))
        # The source every fixture ticket names (``sources: [DEC-000]``): without it the ticket's context
        # cannot be built (W1-24: a missing mandatory input is BLOCKED), and no ticket could close (DEC-454).
        write(self.root, f"docs/adr/{BASE_SOURCE}.md", decision(BASE_SOURCE, "ACTIVE", title="The base decision"))
        commit_all(self.root, "initial project")

    def _copy_kernel_templates(self):
        checks_src = REPO_ROOT / CHECKS_REL
        checks_dst = self.root / CHECKS_REL
        if self._checks is not None:
            for declaration in self._checks:
                self.add_check_declaration(**declaration)
        elif checks_src.is_dir():
            shutil.copytree(checks_src, checks_dst, dirs_exist_ok=True)
        schemas_src = REPO_ROOT / "template" / "governance" / "kernel" / "schemas"
        schemas_dst = self.root / "template" / "governance" / "kernel" / "schemas"
        if schemas_src.is_dir():
            shutil.copytree(schemas_src, schemas_dst, dirs_exist_ok=True)
        if TEMPLATE_OPENSPEC.is_dir():
            shutil.copytree(TEMPLATE_OPENSPEC, self.root / "openspec", dirs_exist_ok=True)
        tk_src = REPO_ROOT / "template" / "governance" / "kernel" / "bin" / "tk"
        tk_dst = self.root / "governance" / "kernel" / "bin" / "tk"
        if tk_src.is_file():
            tk_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(tk_src, tk_dst)
            tk_dst.chmod(0o755)

    def write(self, rel, text):
        return write(self.root, rel, text)

    def commit(self, message="fixture", who=OWNER, trailers=None, exact=False):
        """Commit what the working tree holds.

        A commit that carries ``Role: engineer`` is made as a project makes it, so that W1-50's judgement finds
        nothing in it by accident (``tests/acceptance/W1-50/README.md``): the ticket files waiting in the working
        tree are committed first by the orchestrator, the acceptance tests by the test designer (with the
        engineer's other trailers), and the engineer's commit holds the rest. ``exact=True`` makes one commit of
        everything with exactly the given trailers; a case that plants a commit W1-50 must flag uses it.
        """
        effective = tuple(who["trailers"] if trailers is None else trailers)
        if not exact and ENGINEER_ROLE in effective:
            waiting = self.waiting_paths()
            tickets = [rel for rel in waiting if rel.startswith(TICKETS_PREFIX)]
            tests = [rel for rel in waiting if rel.startswith(ACCEPTANCE_PREFIX)]
            if tickets:
                self._commit("ticket files", ORCHESTRATOR, ORCHESTRATOR["trailers"], tickets)
            if tests:
                designer = tuple(DESIGNER_ROLE if t == ENGINEER_ROLE else t for t in effective)
                self._commit("acceptance tests", TEST_DESIGNER, designer, tests)
        return self._commit(message, who, effective)

    def waiting_paths(self):
        """The paths changed in the working tree and not yet committed."""
        out = git(self.root, "status", "--porcelain=v1", "-z", "-uall")
        return [entry[3:] for entry in out.split("\0") if entry]

    def _commit(self, message, who, trailers, paths=None):
        self._minute += 1
        date = FIRST_DATE.format(minute=self._minute)
        if paths is None:
            git(self.root, "add", "-A", who=who, date=date)
        else:
            git(self.root, "add", "-A", "--", *paths, who=who, date=date)
        args = ["commit", "-q", "--allow-empty", "--no-gpg-sign", "-m", message]
        for t in trailers:
            args += ["--trailer", t]
        git(self.root, *args, who=who, date=date)
        return git(self.root, "rev-parse", "HEAD", who=who).strip()

    def add_ticket(self, ticket_id, wbs, profile="STANDARD", allowed_paths=None, **keys):
        text = ticket_text(ticket_id, wbs, profile=profile, allowed_paths=allowed_paths, **keys)
        write(self.root, ticket_path(ticket_id), text)
        tests_dir = self.root / "tests" / "acceptance" / wbs
        tests_dir.mkdir(parents=True, exist_ok=True)
        write(self.root, f"tests/acceptance/{wbs}/README.md", f"# {wbs}\n")
        return ticket_id

    def add_passing_test(self, wbs, name="test_pass"):
        write(self.root, f"tests/acceptance/{wbs}/{name}.py",
              f"def {name}():\n    assert True\n")

    def add_failing_test(self, wbs, name="test_fail"):
        write(self.root, f"tests/acceptance/{wbs}/{name}.py",
              f"def {name}():\n    assert False, 'planted failure'\n")

    def add_record(self, rel, record_id, record_type, status, **keys):
        write(self.root, rel, record(record_id, record_type, status, **keys))
        return rel

    def add_decision(self, record_id, status, **keys):
        rel = f"docs/adr/{record_id}.md"
        write(self.root, rel, decision(record_id, status, **keys))
        return rel

    def add_skill(self, name, version, content_marker="default content"):
        rel = f"template/governance/kernel/vendor/{name}.md"
        write(self.root, rel, skill_file(name, version, content_marker))
        return rel

    def add_kernel_skill(self, name, version):
        """A skill with a version under template/governance/kernel/skills/<name>/SKILL.md (B4)."""
        text = f"---\nname: {name}\nversion: \"{version}\"\n---\n# {name}\n\nContent.\n"
        rel = f"template/governance/kernel/skills/{name}/SKILL.md"
        write(self.root, rel, text)
        return rel

    def add_vendor_skill(self, name):
        """A vendored skill without a version under vendor/superpowers/skills/<name>/SKILL.md (B4)."""
        text = f"---\nname: {name}\n---\n# {name}\n\nVendored content.\n"
        rel = f"template/governance/kernel/vendor/superpowers/skills/{name}/SKILL.md"
        write(self.root, rel, text)
        return rel

    def add_probe(self, ticket_id, probed_commit=None, **kwargs):
        if probed_commit is None:
            probed_commit = git(self.root, "rev-parse", "HEAD").strip()
        text = probe_record(ticket_id, probed_commit=probed_commit, **kwargs)
        rel = f"docs/probes/{ticket_id}/PR-{ticket_id}.md"
        write(self.root, rel, text)
        return rel

    def add_checkpoint(self, ticket_id, trigger="stop", next_action="resume"):
        sb = cli_support.make_sandbox(self.root.parent / "_cp_sandbox")
        run = self.gov(sb, "checkpoint", "--ticket", ticket_id,
                       "--trigger", trigger, "--next", next_action, "--json")
        assert run.returncode == 0, f"gov checkpoint failed:\n{run.stdout}\n{run.stderr}"

    def add_check_declaration(self, check_id, family, tier="G1", severity="hard-block",
                              command="true"):
        text = "\n".join(f'{field}: "{value}"' for field, value in [
            ("id", check_id), ("family", family), ("tier", tier),
            ("severity", severity), ("command", command),
        ]) + "\n"
        write(self.root, f"{CHECKS_REL}/{check_id}.yaml", text)
        return check_id

    def gov(self, sandbox, *args, python=None, env=None):
        return run_gov(self.root, sandbox, *args, python=python, env=env)


# --------------------------------------------------------------------------
# Running gov close
# --------------------------------------------------------------------------

def ticket_commits(root, ticket):
    """The commits in ``HEAD``'s history whose final trailer block holds ``Task: <ticket>``, oldest first.

    Empty when git cannot read the history (a case may have broken it on purpose).
    """
    out = git(root, "log", "--reverse", "--format=%H%x1f%(trailers:key=Task,valueonly,separator=%x1e)%x1d",
              "HEAD", check=False)
    commits = []
    for entry in out.split("\x1d"):
        commit, _, tasks = entry.strip().partition("\x1f")
        if commit and ticket in [value.strip() for value in tasks.split("\x1e")]:
            commits.append(commit)
    return commits


_JUDGE = (
    "import json, sys\n"
    "from gov.guard.containment import judge_commits\n"
    "found = judge_commits(sys.argv[1], sys.argv[2:])\n"
    "print(json.dumps([{'commit': f.commit, 'paths': list(f.paths), 'reason': f.reason} for f in found]))\n"
)


def judged_by_w1_50(project, sandbox, commits, check=True):
    """W1-50's public judgement of ``commits`` (DEC-453; ``tests/acceptance/W1-50/README.md``, "The public
    function"): a list of ``{commit, paths, reason}``, empty when every commit passes. It only reads."""
    done = subprocess.run([sys.executable, "-c", _JUDGE, str(project.root), *commits], cwd=str(project.root),
                          env=sandbox_env(sandbox), capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if done.returncode != 0 and not check:
        return None   # the function raised (a case broke the history on purpose): nothing is known
    assert done.returncode == 0, f"W1-50's judge_commits did not answer:\n{done.stdout}\n{done.stderr}"
    return json.loads(done.stdout)


def load_store(project, sandbox, check=True):
    """Load the project's record store, as ``gov.store.load(root)`` does (the W1-24 suite builds what a context
    reads the same way). ``gov context`` only reads: without a loaded store no context can be built."""
    done = subprocess.run([sys.executable, "-c", "import sys\nfrom gov.store import load\nload(sys.argv[1])\n",
                           str(project.root)], cwd=str(project.root), env=sandbox_env(sandbox),
                          capture_output=True, text=True, stdin=subprocess.DEVNULL)
    assert done.returncode == 0 or not check, f"gov.store.load failed in the fixture:\n{done.stdout}\n{done.stderr}"


_DECISION_CHECK = (
    "import json, sys\n"
    "from pathlib import Path\n"
    "from gov.cli.errors import GovError\n"
    "from gov.decisions import check\n"
    "try:\n"
    "    print(json.dumps({'findings': check(Path(sys.argv[1]))}))\n"
    "except GovError as error:\n"
    "    print(json.dumps({'error': error.code}))\n"
)


def decision_check(project, sandbox):
    """W1-11's checker on the project (``gov.decisions.check(root)``, ``tests/acceptance/W1-11/README.md``):
    ``{"findings": [...]}``, or ``{"error": <code>}`` when it raises ``GovError`` and so cannot run."""
    done = subprocess.run([sys.executable, "-c", _DECISION_CHECK, str(project.root)], cwd=str(project.root),
                          env=sandbox_env(sandbox), capture_output=True, text=True, stdin=subprocess.DEVNULL)
    assert done.returncode == 0, f"gov.decisions.check did not answer:\n{done.stdout}\n{done.stderr}"
    return json.loads(done.stdout.strip().splitlines()[-1])


def context_error(project, sandbox, ticket):
    """The error ``gov context <ticket>`` gives in this project; the case fails when it gives none."""
    run = project.gov(sandbox, "context", ticket, "--json")
    envelope = run.envelope()
    assert envelope["ok"] is False, f"the fixture's context can be built, so the case measures nothing\n{run.describe()}"
    return envelope["error"]


def tk(project, *args, script=None):
    """Run the project's own ticket tool (``governance/kernel/bin/tk``) and return its output. ``script`` is
    another ticket tool than the project's (round 9: the one on ``PATH``)."""
    script = Path(script or Path(project.root) / "governance" / "kernel" / "bin" / "tk")
    done = subprocess.run([str(script), *args], cwd=str(project.root), capture_output=True, text=True,
                          stdin=subprocess.DEVNULL)
    assert done.returncode == 0, f"tk {' '.join(args)} failed:\n{done.stdout}\n{done.stderr}"
    return done.stdout


def path_without(tool, links):
    """The caller's ``PATH`` with ``tool`` on none of its folders and every other program still there: a folder
    that holds ``tool`` is replaced by ``links/<n>``, which links to each of its other programs."""
    folders = []
    for number, folder in enumerate(dict.fromkeys(os.environ.get("PATH", "").split(os.pathsep))):
        if not folder:
            continue
        if not (Path(folder) / tool).exists():
            folders.append(folder)
            continue
        stand_in = Path(links) / str(number)
        stand_in.mkdir(parents=True)
        for program in Path(folder).iterdir():
            if program.name != tool:
                (stand_in / program.name).symlink_to(program)
        folders.append(str(stand_in))
    assert shutil.which(tool, path=os.pathsep.join(folders)) is None
    return os.pathsep.join(folders)


def trailers_of(ticket, role="engineer", implements="CAP-01"):
    return (f"Task: {ticket}", f"Role: {role}", f"Implements: {implements}")


def build_ticket(project, ticket, wbs, failing=False, **ticket_keys):
    """A ticket whose work is done, by the roles that may do it: the orchestrator's ticket file, the test
    designer's acceptance test (failing when ``failing``), the engineer's source file inside the ticket's
    paths, and the orchestrator's checkpoint. Returns the engineer's trailers."""
    trailers = trailers_of(ticket)
    project.add_ticket(ticket, wbs, **ticket_keys)
    if failing:
        project.add_failing_test(wbs)
    else:
        project.add_passing_test(wbs)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=IMPLEMENTER, trailers=trailers)
    project.add_checkpoint(ticket)
    project.commit("checkpoint", who=ORCHESTRATOR)
    return trailers


def run_close(project, sandbox, ticket, *extra_args, store=True, env=None):
    """Run ``gov close <ticket> --json`` and return the Run.

    The record store is loaded first (``store=False`` leaves it as it is), so that the ticket's context can be
    built wherever the case did not break it on purpose. ``env`` replaces the environment of the close alone
    (round 13: where the session logs are, another ``PATH``).

    DEC-453: ``gov close`` adds no exemption to W1-50's judgement of the ticket's commits. So in every case of
    this suite a close that succeeds had commits that judgement passes; where it finds something and the close
    succeeds all the same, the case fails here, whatever it went on to assert.
    """
    if store:
        load_store(project, sandbox, check=False)
    commits = ticket_commits(project.root, ticket)
    findings = (judged_by_w1_50(project, sandbox, commits, check=False) or []) if commits else []
    run = project.gov(sandbox, COMMAND, ticket, "--json", *extra_args, env=env)
    try:
        closed = json.loads(run.stdout).get("ok") is True
    except (ValueError, AttributeError):
        closed = False
    assert not (closed and findings), (
        "gov close closed a ticket although W1-50's judgement of its commits has findings (DEC-453):\n"
        + "\n".join(f"  {f['commit'][:10]} {f['paths']}: {f['reason']}" for f in findings))
    return run


def refused(run, interface, exit_code):
    """The close was refused with ``exit_code``; returns the ``error`` object."""
    envelope = envelope_of(run, interface)
    assert envelope["ok"] is False, f"gov close was not refused\n{run.describe()}"
    assert run.returncode == exit_code, f"expected exit code {exit_code}\n{run.describe()}"
    return envelope["error"]


def error_text(error):
    """The whole ``error`` object as one string: code, message and details."""
    return json.dumps(error, ensure_ascii=False)


def close_records(root, ticket):
    """Every close record of ``ticket`` the project holds: ``(path, frontmatter)`` of each markdown file outside
    ``.git`` and ``.gov-runtime`` whose frontmatter has ``type: close`` and names the ticket in ``task``."""
    found = []
    for path in sorted(Path(root).rglob("*.md")):
        rel = path.relative_to(root)
        if rel.parts[0] in (".git", ".gov-runtime") or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        try:
            front = yaml.safe_load(text[3:end]) if end > 0 else None
        except yaml.YAMLError:
            continue
        if isinstance(front, dict) and front.get("type") == "close" and front.get("task") == ticket:
            found.append((str(rel), front))
    return found


def ticket_status(root, ticket_id):
    return read_ticket_frontmatter(root, ticket_id).get("status")


def other_tickets(root, *known):
    """The ticket files of the project other than ``known``: the repair tickets a failing close opened."""
    folder = Path(root) / ".tickets"
    return sorted(path for path in folder.glob("*.md") if path.stem not in known)


def frontmatter_of(path):
    parts = Path(path).read_text(encoding="utf-8").split("---", 2)
    return (yaml.safe_load(parts[1]) or {}) if len(parts) >= 3 else {}


def iteration_count(root, ticket_id):
    """The number of consecutive failed closes the project holds for the ticket (settlement 3); 0 without a file."""
    data = read_iteration_file(root, ticket_id)
    if data is None:
        return 0
    assert isinstance(data, dict) and isinstance(data.get("count"), int), f"unreadable count file: {data!r}"
    return data["count"]


def assert_not_closed(project, ticket, before=None):
    """Nothing of a close happened: the ticket is in progress and the project holds no close record of it."""
    assert ticket_status(project.root, ticket) == "in_progress", \
        f"the ticket's status is {ticket_status(project.root, ticket)!r} after a refused close"
    records = close_records(project.root, ticket)
    assert not records, f"a refused close left a close record: {[rel for rel, _ in records]}"


def envelope_of(run, interface):
    """Parse the API-0002 envelope and assert basic structure."""
    envelope = cli_support.assert_envelope(run, interface, command=COMMAND)
    code = (envelope.get("error") or {}).get("code")
    assert code != NOT_IMPLEMENTED, f"gov close is not built yet\n{run.describe()}"
    return envelope


def result_of(run, interface):
    """The result dict when gov close succeeds."""
    envelope = envelope_of(run, interface)
    assert envelope["ok"] is True, f"gov close did not succeed\n{run.describe()}"
    assert run.returncode == EXIT_OK, f"exit code is not 0\n{run.describe()}"
    return envelope["result"]


def assert_error(run, interface, code, exit_code=EXIT_GOV_ERROR):
    """The run failed with GovError ``code``."""
    envelope = envelope_of(run, interface)
    assert envelope["ok"] is False, f"expected error {code}, but ok is true\n{run.describe()}"
    assert envelope["error"]["code"] == code, f"expected error code {code}\n{run.describe()}"
    assert run.returncode == exit_code, \
        f"expected exit code {exit_code} for {code}\n{run.describe()}"
    return envelope["error"]


# --------------------------------------------------------------------------
# Record discovery: scan for new markdown files written by gov close
# --------------------------------------------------------------------------

def new_files(root, before, after, suffix=".md"):
    """Paths that appeared between two snapshots."""
    return sorted(rel for rel in set(after) - set(before) if rel.endswith(suffix))


def find_record_of_type(root, paths, record_type):
    """Among new files, find one whose frontmatter ``type`` matches."""
    for rel in paths:
        path = Path(root) / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        end = text.find("---", 3)
        if end < 0:
            continue
        try:
            front = yaml.safe_load(text[3:end])
        except Exception:
            continue
        if isinstance(front, dict) and front.get("type") == record_type:
            return rel, front
    return None, None


def find_close_record(root, paths):
    return find_record_of_type(root, paths, "close")


def find_checkpoint_record(root, paths):
    return find_record_of_type(root, paths, "checkpoint")


# --------------------------------------------------------------------------
# Check helpers (delegate to W1-26 support)
# --------------------------------------------------------------------------

def run_check(project, sandbox, *extra_args):
    """Run ``gov check --json``."""
    return project.gov(sandbox, "check", "--json", *extra_args)


def check_envelope_of(run, interface):
    """Parse envelope for a check run."""
    return check_support.envelope_of(run, interface)


def check_result_of(run, interface):
    return check_support.result_of(run, interface)


def family_status(result, family_name):
    return check_support.family_status(result, family_name)


def checks_of(result):
    return check_support.checks_of(result)


def finding_codes(result):
    return check_support.finding_codes(result)


# --------------------------------------------------------------------------
# The governance checks of a close (CAP-38.d, DEC-454, DEC-476)
# --------------------------------------------------------------------------

RED, YELLOW, GREEN = check_support.RED, check_support.YELLOW, check_support.GREEN
HARD_BLOCK, WARNING = check_support.HARD_BLOCK, check_support.WARNING

# Where the close record states the governance checks (settlement 12).
CHECK_COMMIT_KEY = "check_commit"
CHECK_RESULT_KEY = "governance_checks"


def declared_check(check_id, command, severity=HARD_BLOCK, family="schema/invariants", tier="G1"):
    """One check declaration of a project's own set (``Project(root, checks=[...])``)."""
    return {"check_id": check_id, "family": family, "tier": tier, "severity": severity, "command": command}


def checks_at_head(project, sandbox):
    """What W1-26's runner says of every check in the project as it stands: ``{id: entry}`` from
    ``gov check --json``, read from ``result`` (exit code 0) or from ``error.details`` (exit code 3)."""
    run = run_check(project, sandbox)
    envelope = run.envelope()
    body = envelope.get("result") if envelope.get("ok") else (envelope.get("error") or {}).get("details")
    entries = (body or {}).get("checks")
    assert isinstance(entries, list) and entries, f"gov check named no check\n{run.describe()}"
    return {entry["id"]: entry for entry in entries}


def statuses(entries):
    return {check_id: entry["status"] for check_id, entry in entries.items()}


def red_hard_blocks(entries):
    return sorted(check_id for check_id, entry in entries.items()
                  if entry["severity"] == HARD_BLOCK and entry["status"] == RED)


def the_close_record(project, ticket):
    """The frontmatter of the ticket's one close record."""
    records = close_records(project.root, ticket)
    assert len(records) == 1, f"one close record of {ticket} is expected, found {[rel for rel, _ in records]}"
    return records[0][1]


def recorded_check_statuses(front):
    """``{id: status}`` of every check the close record states: each object under ``governance_checks`` that has
    an ``id`` and a ``status``, at any depth."""
    found = [entry for entry in cli_support.find_records(front.get(CHECK_RESULT_KEY), key="id") if "status" in entry]
    return {entry["id"]: entry["status"] for entry in found}


def head_of(project):
    return git(project.root, "rev-parse", "HEAD").strip()


# The paths of a ticket that may change governance files: W1-50's judgement passes an engineer's commit there.
GOVERNANCE_TICKET_PATHS = ("src/example/**", "governance/project/**", "template/governance/kernel/**",
                           "governance/kernel/**")


def start_ticket(project, ticket, wbs, allowed_paths=GOVERNANCE_TICKET_PATHS):
    """The orchestrator's ticket file and the test designer's passing acceptance test, waiting for the
    engineer's first commit (``engineer_commit``)."""
    project.add_ticket(ticket, wbs, allowed_paths=list(allowed_paths))
    project.add_passing_test(wbs)


def engineer_commit(project, ticket, files):
    """One commit of the ticket's engineer that writes ``files`` (``{path: text}``); returns its id."""
    for rel, text in files.items():
        project.write(rel, text)
    return project.commit("work on the ticket", who=IMPLEMENTER, trailers=trailers_of(ticket))


def checkpointed(project, ticket):
    """The orchestrator's checkpoint, committed: the project is ready for its close. Returns ``HEAD``, the
    commit being closed."""
    project.add_checkpoint(ticket)
    return project.commit("checkpoint", who=ORCHESTRATOR)


def assert_dependent_repair_ticket(project, ticket, run, script=None):
    """The refused close opened exactly one other ticket, and by the ticket tool it depends on ``ticket``.
    Returns the repair ticket's file. ``script`` as in ``tk``."""
    repairs = other_tickets(project.root, ticket)
    assert len(repairs) == 1, f"one repair ticket is expected, found {[p.name for p in repairs]}\n{run.describe()}"
    tree = tk(project, "dep", "tree", repairs[0].stem, script=script).splitlines()
    assert any(ticket in line for line in tree[1:]), \
        f"by the ticket tool the repair ticket does not depend on {ticket}: {tree}"
    return repairs[0]


# --------------------------------------------------------------------------
# Iteration file helpers (A6)
# --------------------------------------------------------------------------

def write_iteration_file(root, ticket_id, data):
    """Write an iteration count file under .gov-runtime/iterations/."""
    path = Path(root) / ITERATION_DIR / f"{ticket_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def corrupt_iteration_file(root, ticket_id, content="not json at all {{{"):
    """Write an unparseable iteration count file."""
    path = Path(root) / ITERATION_DIR / f"{ticket_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def read_iteration_file(root, ticket_id):
    """Read an iteration count file, or None if absent."""
    path = Path(root) / ITERATION_DIR / f"{ticket_id}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# Round 8 (DEC-487, made exact by DEC-490): what a close did not measure
# --------------------------------------------------------------------------

ESCALATION_DIR = ".gov-runtime/escalations"

# The test runner's own option variable: what it holds is added to every run of the runner that inherits it.
TEST_RUNNER_OPTIONS = "PYTEST_ADDOPTS"

CLOSED_NEXT_ACTION = "ticket closed"


def no_trailers_commit(project, message, files):
    """One commit that writes ``files`` and carries no trailer at all, by someone who is neither the owner
    nor the orchestrator; returns its id."""
    for rel, text in files.items():
        project.write(rel, text)
    return project.commit(message, who=AGENT, trailers=(), exact=True)


def refused_without_a_finding(run, interface):
    """The close was refused because it could not measure, not for a finding about the ticket's work: exit
    code 1 (DEC-490; DEC-470 gives 3 to a finding). Returns the ``error`` object."""
    envelope = envelope_of(run, interface)
    assert envelope["ok"] is False, f"gov close was not refused\n{run.describe()}"
    assert run.returncode == EXIT_GOV_ERROR, \
        f"a close that could not measure ends with exit code 1, not {run.returncode}\n{run.describe()}"
    return envelope["error"]


def assert_nothing_counted(project, ticket, run, count=0):
    """The refusal is not counted: the ticket's count is still ``count``."""
    assert iteration_count(project.root, ticket) == count, \
        f"the refusal was counted as an iteration: the count is {iteration_count(project.root, ticket)}\n{run.describe()}"


def assert_no_repair_ticket(project, run, *known):
    repairs = other_tickets(project.root, *known)
    assert not repairs, f"the refusal opened a repair ticket: {[p.name for p in repairs]}\n{run.describe()}"


def records_saying_closed(root, ticket):
    """What in the tree says the ticket closed: its close records whose status is ACTIVE, and its checkpoints
    whose next action is "ticket closed". Paths, relative to the project."""
    found = [rel for rel, front in close_records(root, ticket) if str(front.get("status", "")).upper() == "ACTIVE"]
    for path in sorted(Path(root).rglob("*.md")):
        rel = path.relative_to(root)
        if rel.parts[0] in (".git", ".gov-runtime") or not path.is_file():
            continue
        front = frontmatter_of(path) if path.read_text(encoding="utf-8", errors="replace").startswith("---") else {}
        if isinstance(front, dict) and front.get("type") == "checkpoint" and front.get("task") == ticket \
                and str(front.get("next_action", "")).strip().lower() == CLOSED_NEXT_ACTION:
            found.append(str(rel))
    return found


def untracked_paths(project):
    """The files of the working tree that git neither knows nor ignores."""
    out = git(project.root, "ls-files", "--others", "--exclude-standard", "-z")
    return sorted(rel for rel in out.split("\0") if rel)


def commit_what_a_refusal_left(project):
    """A refused close opens a repair ticket, a file git does not know yet. The orchestrator commits it here.
    DEC-490: left untracked it refuses no later close (its parent is the ticket being closed); the cases of
    ``test_w1_30_r8_tree.py`` hold that, the others commit it."""
    if project.waiting_paths():
        project.commit("what the refused close left", who=ORCHESTRATOR)


def escalate(project, sandbox, interface, ticket):
    """Three closes refused for the ticket's failing acceptance test, each a finding, and a fourth that is
    blocked: the escalation is in force. What each refusal left is committed by the orchestrator."""
    for _ in range(3):
        refused(run_close(project, sandbox, ticket), interface, EXIT_CHECK_FAILED)
        commit_what_a_refusal_left(project)
    refused(run_close(project, sandbox, ticket), interface, EXIT_BLOCKED)
    commit_what_a_refusal_left(project)


def assert_escalation_in_force(project, sandbox, interface, ticket, why):
    """A close without an owner's decision is blocked (exit code 4): the escalation was not lifted."""
    run = run_close(project, sandbox, ticket)
    envelope = envelope_of(run, interface)
    assert envelope["ok"] is False and run.returncode == EXIT_BLOCKED, \
        f"{why}: the escalation is no longer in force, the next close ran\n{run.describe()}"


# --------------------------------------------------------------------------
# Round 9 (DEC-492): every finding in one run; the ticket tool on PATH
# --------------------------------------------------------------------------

TOOL_REL = "governance/kernel/bin/tk"
TOOL_NAME = "tk"
KERNEL_TOOL = REPO_ROOT / "template" / "governance" / "kernel" / "bin" / "tk"


def path_with_tool(folder, links, script=None):
    """A ``PATH`` whose only ticket tool is ``folder/tk``: the caller's ``PATH`` without ``tk``
    (``path_without``), and ``folder`` before it. ``script`` is the text of that tool; without it the tool is a
    copy of the kernel's. Returns ``(path, tool)``."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    tool = folder / TOOL_NAME
    if script is None:
        shutil.copy2(KERNEL_TOOL, tool)
    else:
        tool.write_text(script, encoding="utf-8")
    tool.chmod(0o755)
    path = str(folder) + os.pathsep + path_without(TOOL_NAME, links)
    assert shutil.which(TOOL_NAME, path=path) == str(tool), "the fixture is wrong: another ticket tool is on PATH"
    return path, tool


def _plain(text):
    """Lower case, with ``_``, ``-`` and runs of blanks as one blank: ``not_measured`` reads "not measured"."""
    return re.sub(r"[_\-\s]+", " ", str(text)).lower()


def says_not_measured(error, what):
    """Whether the answer says of ``what`` (a word, as "acceptance") that it was not measured, by name
    (DEC-492). No source gives the form, so any of these is taken (README, round 9, settlement 14): one
    sentence of one string holds both "not measured" and ``what``; or one of the two is in a key and the other
    is under that key. ``_`` and ``-`` read as blanks. A string that only names ``what`` elsewhere (the finding
    "no acceptance tests") says nothing of the kind."""
    what = _plain(what)

    def under(node, word):
        return word in _plain(json.dumps(node, ensure_ascii=False))

    def walk(node):
        if isinstance(node, str):
            return any(NOT_MEASURED_WORDS in part and what in part
                       for part in map(_plain, re.split(r"[;\n]|\.\s", node)))
        if isinstance(node, dict):
            for key, value in node.items():
                key = _plain(key)
                if (NOT_MEASURED_WORDS in key and under(value, what)) or \
                        (what in key and under(value, NOT_MEASURED_WORDS)):
                    return True
            return any(walk(value) for value in node.values())
        if isinstance(node, list):
            return any(walk(value) for value in node)
        return False

    return walk(error)


NOT_MEASURED_WORDS = "not measured"


# --------------------------------------------------------------------------
# Round 11 (DEC-527): the test runs in parallel, the declared cases alone afterwards
# --------------------------------------------------------------------------

# The list a project owns of its cases that cannot hold under parallel load (README, round 11, settlement 18).
SERIAL_ONLY_REL = "tests/acceptance/serial-only.txt"
# The kinds an entry of this repository's list names in its comment.
SERIAL_ONLY_KINDS = ("latency", "real-model-or-daemon", "live-session", "race")

# Where the close record and the result state the test runs, and the forms a run has (settlement 19).
TEST_RUNS_KEY = "test_runs"
PARALLEL, SERIAL, SERIAL_AFTERWARDS = "parallel", "serial", "serial-afterwards"
ACCEPTANCE_RUN, REGRESSION_RUN = "acceptance", "regression"
RUN_COUNTS = ("passed", "failed", "errors", "skipped")

# What a worker of the installed parallel runner (pytest-xdist) has in its environment, and no other test process.
WORKER_VARIABLE = "PYTEST_XDIST_WORKER"
NO_WORKER = "none"
_PARALLEL_RUNNER_NAMES = ("xdist",)
_PARALLEL_RUNNER_PREFIXES = ("pytest_xdist", "pytest-xdist")


def telling_test(name, told, body="assert True", decorator="", arguments=""):
    """The text of a test file with one test function, ``name``, that tells how it ran: at every run it adds a
    line to a file of its own under ``told``, outside the project, with the parallel worker it ran in
    (``NO_WORKER`` when it ran in none) and the time. The file is named as the case is in its node id
    (``name``, or ``name[set]`` for a parameter set). ``body`` is what the test does after that; ``decorator``
    stands before the function and ``arguments`` are its own."""
    return (
        "import os\nimport time\n\nimport pytest\n\n\n"
        f"{decorator}"
        f"def {name}({arguments}):\n"
        "    case = os.environ['PYTEST_CURRENT_TEST'].split('::')[-1].split(' ')[0]\n"
        f"    with open(os.path.join({str(told)!r}, case), 'a', encoding='utf-8') as told:\n"
        f"        told.write(os.environ.get({WORKER_VARIABLE!r}, {NO_WORKER!r}) + ' ' + repr(time.time()) + '\\n')\n"
        f"    {body}\n"
    )


def told_by(told):
    """What the telling tests told: ``{name: [(worker, time), ...]}``, one pair for each time the test ran."""
    runs = {}
    for path in sorted(Path(told).iterdir()):
        lines = path.read_text(encoding="utf-8").splitlines()
        runs[path.name] = [(line.split()[0], float(line.split()[1])) for line in lines]
    return runs


def ran_in_a_worker(runs):
    """Whether a telling test ran exactly once, in a worker of the parallel runner."""
    return len(runs) == 1 and re.fullmatch(r"gw\d+", runs[0][0]) is not None


def ran_alone(runs):
    """Whether a telling test ran exactly once, in no worker."""
    return len(runs) == 1 and runs[0][0] == NO_WORKER


def serial_only_entries(path):
    """The entries of a serial-only list, as ``[(entry, comment)]``: one on a line, the beginning of a node id;
    what follows `` #`` (or a ``#`` that begins the line) is the comment; empty lines hold nothing."""
    entries = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        entry, _, comment = (" " + line).partition(" #")
        if entry.strip():
            entries.append((entry.strip(), comment.strip()))
    return entries


def declared_serial_only(node_id, entries):
    """Whether a node id is named by one of the entries: it is the entry, or begins with it at a boundary of
    the id (``::`` after a file, ``[`` after a function)."""
    return any(node_id == entry or (node_id.startswith(entry) and node_id[len(entry):].startswith(("::", "[", "/")))
               for entry in entries)


def runs_stated_by(holder, where):
    """The test runs ``holder`` (the close record's frontmatter, or the result) states under ``test_runs``,
    each checked for its form: ``run``, ``form``, ``seconds`` and the four counts."""
    runs = holder.get(TEST_RUNS_KEY)
    assert isinstance(runs, list) and runs, f"{where} states no test runs under {TEST_RUNS_KEY!r}: {sorted(holder)}"
    for run in runs:
        assert isinstance(run, dict), f"{where}: a test run is not an object: {run!r}"
        assert run.get("run") in (ACCEPTANCE_RUN, REGRESSION_RUN), f"{where}: a test run names no run: {run!r}"
        assert run.get("form") in (PARALLEL, SERIAL, SERIAL_AFTERWARDS), f"{where}: a test run names no form: {run!r}"
        seconds = run.get("seconds")
        assert isinstance(seconds, (int, float)) and not isinstance(seconds, bool) and seconds >= 0, \
            f"{where}: a test run does not say how long it took: {run!r}"
        for key in RUN_COUNTS:
            assert isinstance(run.get(key), int) and not isinstance(run.get(key), bool), \
                f"{where}: a test run does not count {key}: {run!r}"
    return runs


def the_run(runs, run, form):
    """The one test run of ``runs`` that is ``run`` in ``form``; None when there is none."""
    found = [entry for entry in runs if (entry["run"], entry["form"]) == (run, form)]
    assert len(found) <= 1, f"more than one {form} run of the {run} tests: {found}"
    return found[0] if found else None


# --------------------------------------------------------------------------
# Round 12 (DEC-549): the number of parallel workers of a close is a setting of the project
# --------------------------------------------------------------------------

# What the setting holds without a line of the project, and what a project may write beside a whole number.
AUTO = "auto"
# Where a parallel run states the number of workers it was given (settlement 22).
WORKERS_FIELD = "workers"
# The refusals of a setting that is none (settlement 23); the time limit's is DEC-487's.
INVALID_WORKERS = "INVALID_WORKERS"
INVALID_TIMEOUT = "INVALID_TIMEOUT"
# The key of a refusal's details that names the argument or the setting refused, as the time limit's does.
REFUSED_KEY = "argument"


def workers_that_ran(ran, names):
    """The workers of the parallel runner in which the telling tests ``names`` ran, each named once."""
    return sorted({worker for name in names for worker, _ in ran.get(name, [])})


def workers_named(number):
    """The names the parallel runner gives ``number`` workers."""
    return [f"gw{index}" for index in range(number)]


def environment_without_parallel_runner(base, sandbox):
    """The environment of ``sandbox_env`` in which the interpreter running the suite finds every installed
    package but the parallel runner; None where that cannot be arranged.

    ``gov close`` gives its test runs no ``PYTHONPATH`` of the caller, and passes on where the per-user folder
    of installed packages is (``PYTHONUSERBASE``). So the runner is taken away there: a per-user folder of
    links to everything in the real one but the parallel runner. Where the runner is installed elsewhere (or
    there is no per-user folder), this fixture cannot take it away.
    """
    if not site.ENABLE_USER_SITE:
        return None
    real = Path(site.getusersitepackages())
    if not real.is_dir():
        return None
    mirror = Path(base) / "userbase" / real.relative_to(site.getuserbase())
    mirror.mkdir(parents=True)
    for entry in real.iterdir():
        name = entry.name.lower()
        if name in _PARALLEL_RUNNER_NAMES or name.startswith(_PARALLEL_RUNNER_PREFIXES) or name.endswith(".pth"):
            continue
        (mirror / entry.name).symlink_to(entry)
    env = {**sandbox_env(sandbox), "PYTHONUSERBASE": str(Path(base) / "userbase")}
    return None if can_import("xdist", sandbox, env=env) else env
