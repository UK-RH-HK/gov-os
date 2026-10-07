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
import subprocess
import sys
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

# Governance file prefixes whose change forces a check re-run at close (A7, CAP-38.d).
GOVERNANCE_PREFIXES = (
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

    def __init__(self, root, copy_tree=False):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._minute = 0
        if copy_tree:
            cli_support.copy_working_tree(self.root)
        else:
            self._init_minimal()

    def _init_minimal(self):
        git(self.root, "init", "-q", "-b", "main")
        write(self.root, "README.md", "# A project\n")
        write(self.root, ".gitignore", ".gov-runtime/\n")
        write(self.root, "pyproject.toml",
              (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        shutil.copytree(REPO_ROOT / "src", self.root / "src")
        self._copy_kernel_templates()
        # The source every fixture ticket names (``sources: [DEC-000]``): without it the ticket's context
        # cannot be built (W1-24: a missing mandatory input is BLOCKED), and no ticket could close (DEC-454).
        write(self.root, f"docs/adr/{BASE_SOURCE}.md", decision(BASE_SOURCE, "ACTIVE", title="The base decision"))
        commit_all(self.root, "initial project")

    def _copy_kernel_templates(self):
        checks_src = REPO_ROOT / CHECKS_REL
        checks_dst = self.root / CHECKS_REL
        if checks_src.is_dir():
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

    def gov(self, sandbox, *args):
        return cli_support.run_gov_with_code(REPO_ROOT, self.root, sandbox, *args)


class FullProject:
    """A copy of the working tree, committed, with its own store."""

    def __init__(self, root):
        self.root = Path(root)
        cli_support.copy_working_tree(self.root)
        self._minute = 0

    def write(self, rel, text):
        return write(self.root, rel, text)

    def commit(self, message="fixture", who=OWNER, trailers=None):
        self._minute += 1
        date = FIRST_DATE.format(minute=self._minute)
        git(self.root, "add", "-A", who=who, date=date)
        args = ["commit", "-q", "--allow-empty", "--no-gpg-sign", "-m", message]
        for t in (who["trailers"] if trailers is None else trailers):
            args += ["--trailer", t]
        git(self.root, *args, who=who, date=date)
        return git(self.root, "rev-parse", "HEAD", who=who).strip()

    def gov(self, sandbox, *args):
        return cli_support.run_gov_with_code(REPO_ROOT, self.root, sandbox, *args)


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
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(SRC),
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
    }
    done = subprocess.run([sys.executable, "-c", _JUDGE, str(project.root), *commits], cwd=str(project.root),
                          env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if done.returncode != 0 and not check:
        return None   # the function raised (a case broke the history on purpose): nothing is known
    assert done.returncode == 0, f"W1-50's judge_commits did not answer:\n{done.stdout}\n{done.stderr}"
    return json.loads(done.stdout)


def sandbox_env(sandbox):
    """The environment W1-07's stand-in gives ``gov``, for a call of a public function of ``src/``."""
    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(sandbox.home),
        "TMPDIR": str(sandbox.tmpdir),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(SRC),
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
    }


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


def tk(project, *args):
    """Run the project's own ticket tool (``governance/kernel/bin/tk``) and return its output."""
    script = Path(project.root) / "governance" / "kernel" / "bin" / "tk"
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


def run_close(project, sandbox, ticket, *extra_args, store=True):
    """Run ``gov close <ticket> --json`` and return the Run.

    The record store is loaded first (``store=False`` leaves it as it is), so that the ticket's context can be
    built wherever the case did not break it on purpose.

    DEC-453: ``gov close`` adds no exemption to W1-50's judgement of the ticket's commits. So in every case of
    this suite a close that succeeds had commits that judgement passes; where it finds something and the close
    succeeds all the same, the case fails here, whatever it went on to assert.
    """
    if store:
        load_store(project, sandbox, check=False)
    commits = ticket_commits(project.root, ticket)
    findings = (judged_by_w1_50(project, sandbox, commits, check=False) or []) if commits else []
    run = project.gov(sandbox, COMMAND, ticket, "--json", *extra_args)
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
