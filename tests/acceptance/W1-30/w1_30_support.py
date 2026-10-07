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

# The six finding dispositions (L-0077, DEC-435, A3 settlement: short names).
DISPOSITIONS = ("repair", "reuse", "delete", "narrow", "defer", "owner")

# Governance file prefixes whose change forces a check re-run at close (A7, CAP-38.d).
GOVERNANCE_PREFIXES = (
    "template/governance/kernel/checks/",
    "template/governance/kernel/schemas/",
    "governance/project/",
    "template/governance/kernel/hooks/",
    "template/governance/kernel/skills/",
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
    """A ticket file, optionally overriding profile and allowed_paths."""
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
        tk_src = REPO_ROOT / "governance" / "kernel" / "bin" / "tk"
        tk_dst = self.root / "governance" / "kernel" / "bin" / "tk"
        if tk_src.is_file():
            tk_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(tk_src, tk_dst)
            tk_dst.chmod(0o755)

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
        from gov.checkpoint.record import write as cp_write
        cp_write(self.root, ticket_id, trigger, next_action, [])

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

def run_close(project, sandbox, ticket, *extra_args):
    """Run ``gov close <ticket> --json`` and return the Run."""
    return project.gov(sandbox, COMMAND, ticket, "--json", *extra_args)


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
