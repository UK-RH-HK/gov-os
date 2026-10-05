"""Support code for the W1-11 acceptance tests (standard library only).

W1-11 builds the decision checker. No ``gov`` command belongs to this ticket
(``src/gov/cli/**`` is outside its paths; W1-26 runs the checker from
``gov check``), so the tests use the Python interface of ``gov.decisions``,
stated in the README:

- ``gov.decisions.check(root)``: the list of findings; an empty list passes.

How the tests call it:

- **Every call runs in a new Python process**, through a small driver written to
  a temporary directory, with this worktree's ``src/`` on ``PYTHONPATH``.
- **Nothing is written in this worktree.** Every project is a temporary git
  repository, or a clone of the b-dev tier in a temporary directory. The store
  is built there (DEC-322), never in this repository.
- **The environment is built from scratch:** ``PATH``, an empty temporary
  ``HOME``, ``TMPDIR``, locale, ``PYTHONPATH`` and ``PYTHONPYCACHEPREFIX``.
  ``GOV_ROLE`` and ``GOV_TICKET`` of the session that runs the tests are not
  passed on.
- **Before a check, the project is committed and the store is loaded**
  (``gov.store.load``), so the checker may read the record graph, git or the
  working tree: the three agree.
- **Fixture commits have fixed dates, authors and trailers.** A commit is dated 2026-10-04, or 2026-09-20 where
  a test needs one made before the trailer rule of DEC-182.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
DECISIONS_MODULE = "gov.decisions"
STORE_MODULE = "gov.store"
STORE_REL = ".gov-runtime/store.db"
CALL_TIMEOUT_S = 120.0
MISSING_EXIT = 3

DEV_TIERS = Path(os.environ.get("GOV_DEV_TIERS") or Path.home() / "gov-os-workbench" / "synthetic")
B_DEV = "b-dev"

# The codes of a finding (README, "The public interface").
ACTIVE_SUPERSEDED = "ACTIVE_SUPERSEDED"
DUPLICATE_ID = "DUPLICATE_ID"
OVERLAPPING_ID = "OVERLAPPING_ID"
SUPERSESSION_CYCLE = "SUPERSESSION_CYCLE"
ACTIVE_UNAPPROVED = "ACTIVE_UNAPPROVED"
GATE_NOT_AUTHORISING = "GATE_NOT_AUTHORISING"
TICKET_WAITS_ON_DEAD_GATE = "TICKET_WAITS_ON_DEAD_GATE"
HAZARD_CODES = (ACTIVE_SUPERSEDED, DUPLICATE_ID, OVERLAPPING_ID, SUPERSESSION_CYCLE)

# DEC-328: the five values of a gate record's `status`; only ACCEPTED is an answered gate.
GATE_OPEN = "PROPOSED"
GATE_ANSWERED = "ACCEPTED"
GATE_DEAD = ("DECLINED", "REVOKED", "STALE")

_DRIVER = '''\
import importlib, json, sys
from pathlib import Path

out = []
for call in json.loads(sys.stdin.read()):
    try:
        function = getattr(importlib.import_module(call["module"]), call["function"])
    except ModuleNotFoundError as exc:
        if exc.name != "gov.decisions":
            raise
        print(f"No module named {exc.name!r}", file=sys.stderr)
        sys.exit(3)
    except AttributeError:
        print(f"{call['module']} has no function {call['function']}", file=sys.stderr)
        sys.exit(3)
    try:
        out.append({"value": function(Path(call["root"]))})
    except Exception as exc:
        if type(exc).__name__ != "GovError":
            raise
        out.append({"error": {"code": exc.code, "message": exc.message, "details": exc.details}})
print(json.dumps(out))
'''


class CheckerMissing(AssertionError):
    """The decision checker does not exist yet."""


class Raised(Exception):
    """A call raised ``GovError``."""

    def __init__(self, error):
        super().__init__(f"GovError {error.get('code')}: {error.get('message')}")
        self.code = error.get("code")
        self.message = error.get("message")
        self.details = error.get("details")


# --------------------------------------------------------------------------
# Calling the public interface
# --------------------------------------------------------------------------

class Api:
    """Calls ``gov.decisions`` (and ``gov.store.load``) of this worktree, each batch in a new process."""

    def __init__(self, workdir):
        self.workdir = Path(workdir)
        for name in ("home", "tmp", "pycache"):
            (self.workdir / name).mkdir(parents=True, exist_ok=True)
        self.driver = self.workdir / "driver.py"
        self.driver.write_text(_DRIVER, encoding="utf-8")

    def _batch(self, calls):
        request = [{"module": module, "function": function, "root": str(root)} for module, function, root in calls]
        environment = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(self.workdir / "home"),
            "TMPDIR": str(self.workdir / "tmp"),
            "LC_ALL": "C.UTF-8",
            "GIT_CONFIG_NOSYSTEM": "1",
            "PYTHONPATH": str(SRC),
            "PYTHONPYCACHEPREFIX": str(self.workdir / "pycache"),
        }
        what = ", ".join(f"{module}.{function}" for module, function, _ in calls)
        try:
            done = subprocess.run([sys.executable, str(self.driver)], input=json.dumps(request), env=environment,
                                  cwd=str(self.workdir), capture_output=True, text=True, timeout=CALL_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"{what} did not end within {CALL_TIMEOUT_S:.0f} s") from None
        if done.returncode == MISSING_EXIT:
            raise CheckerMissing(f"the decision checker does not exist: {done.stderr.strip()} under src/")
        assert done.returncode == 0, f"{what} failed (exit code {done.returncode}):\n{done.stderr}"
        try:
            return json.loads(done.stdout)
        except ValueError:
            raise AssertionError(f"{what} did not return JSON values:\n{done.stdout}\n{done.stderr}") from None

    def load(self, root):
        """``gov.store.load(root)``: build the store of the temporary project."""
        answer = self._batch([(STORE_MODULE, "load", root)])[0]
        assert "value" in answer, f"gov.store.load failed: {answer.get('error')}"
        return answer["value"]

    def check_only(self, root):
        """``gov.decisions.check(root)`` alone: the findings, each checked for the shape the interface fixes."""
        answer = self._batch([(DECISIONS_MODULE, "check", root)])[0]
        if "error" in answer:
            raise Raised(answer["error"])
        return findings(answer["value"])

    def check(self, root):
        """Load the store of ``root``, then check it."""
        self.load(root)
        return self.check_only(root)


def findings(value):
    """``value`` when it is a list of findings in the shape the interface fixes."""
    assert isinstance(value, list), f"check did not return a list of findings: {value!r}"
    for finding in value:
        assert isinstance(finding, dict), f"a finding is not a map: {finding!r}"
        assert isinstance(finding.get("code"), str) and finding["code"], f"a finding has no `code`: {finding!r}"
        for key in ("ids", "paths"):
            assert isinstance(finding.get(key), list) and all(isinstance(item, str) for item in finding[key]), \
                f"a finding's `{key}` is not a list of strings: {finding!r}"
        assert isinstance(finding.get("message"), str) and finding["message"].strip(), \
            f"a finding has no `message`: {finding!r}"
    return value


def with_code(found, code):
    return [finding for finding in found if finding["code"] == code]


def matching(found, code, ids=(), paths=()):
    """The findings with ``code`` that name every one of ``ids`` and every one of ``paths``."""
    return [finding for finding in with_code(found, code)
            if set(ids) <= set(finding["ids"]) and set(paths) <= set(finding["paths"])]


def assert_flagged(found, code, ids=(), paths=()):
    assert matching(found, code, ids, paths), (
        f"no {code} finding names ids {sorted(ids)} and paths {sorted(paths)}; the findings were:\n{show(found)}")


def assert_not_flagged(found, code, ids=()):
    hits = matching(found, code, ids)
    assert not hits, f"{code} was raised for {sorted(ids) or 'this tree'}, which is no such case:\n{show(hits)}"


def show(found):
    return "\n".join(f"  {finding['code']} ids={finding['ids']} paths={finding['paths']}: {finding['message']}"
                     for finding in found) or "  (none)"


# --------------------------------------------------------------------------
# git and the temporary project
# --------------------------------------------------------------------------

# Who commits. The owner's approval fact is the `Role: owner` trailer on the commit that sets a decision ACTIVE
# (DEC-360), in the final trailer block (DEC-182). An agent's commit differs in name, email and role;
# AGENT_AS_OWNER differs in the role alone, as in a repository where agents commit under the owner's account.
OWNER = {"name": "The Owner", "email": "owner@example.invalid", "trailers": ("Role: owner",)}
AGENT = {"name": "An Agent", "email": "agent@example.invalid",
         "trailers": ("Task: PROJ-aaaa", "Role: engineer")}
ANONYMOUS = {"name": "An Agent", "email": "agent@example.invalid", "trailers": ()}
AGENT_AS_OWNER = {"name": OWNER["name"], "email": OWNER["email"], "trailers": AGENT["trailers"]}

# From 2026-10-03, trailers are read from the final trailer block alone (DEC-182). Both dates are the author's
# and the committer's, and fall on the same side of 2026-10-03 in every time zone.
FIRST_DATE = "2026-10-04T12:{minute:02d}:00+00:00"
BEFORE_THE_TRAILER_RULE = "2026-09-20T12:00:00+00:00"


def git(project, *args, who=AGENT, date=FIRST_DATE.format(minute=0), check=True):
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(Path(project).parent),
        "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_AUTHOR_NAME": who["name"], "GIT_AUTHOR_EMAIL": who["email"],
        "GIT_COMMITTER_NAME": who["name"], "GIT_COMMITTER_EMAIL": who["email"],
        "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date,
    }
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, env=env)
    if check and done.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {project}:\n{done.stderr}")
    return done.stdout


class Project:
    """A temporary git repository: files are written, then committed by the owner or by an agent."""

    def __init__(self, root, init=True):
        self.root = Path(root)
        self.minute = 0
        if init:
            self.root.mkdir(parents=True, exist_ok=True)
            git(self.root, "init", "-q", "-b", "main")

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
        return path

    def commit(self, message="records", who=OWNER, trailers=None, date=None):
        """Commit everything; trailers go in the final trailer block with ``git commit --trailer`` (DEC-182).
        ``date`` replaces the next fixture date, as the author's and the committer's."""
        self.minute += 1
        date = date or FIRST_DATE.format(minute=self.minute)
        git(self.root, "add", "-A", who=who, date=date)
        arguments = ["commit", "-q", "--allow-empty", "--no-gpg-sign", "-m", message]
        for trailer in (who["trailers"] if trailers is None else trailers):
            arguments += ["--trailer", trailer]
        git(self.root, *arguments, who=who, date=date)
        return git(self.root, "rev-parse", "HEAD").strip()

    def put(self, files, who=OWNER, message="records"):
        """Write ``path -> text`` and commit it."""
        for rel, text in files.items():
            self.write(rel, text)
        return self.commit(message, who=who)


def clone(source, destination):
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(source), str(destination)], check=True,
                   capture_output=True)
    return Project(destination, init=False)


def snapshot(root):
    """Everything a checker that only reads leaves as it was: every file of the tree outside ``.git/`` with the
    sha256 of its bytes (a link with its target), the commit, the refs, the index and the git status."""
    root = Path(root)
    files = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if rel == ".git" or rel.startswith(".git/"):
            continue
        if path.is_symlink():
            files[rel] = "link:" + os.readlink(path)
        elif path.is_file():
            files[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            files[rel] = "dir"
    return {
        "files": files,
        "head": git(root, "rev-parse", "HEAD"),
        "refs": git(root, "for-each-ref"),
        "index": git(root, "ls-files", "--stage"),
        "status": git(root, "status", "--porcelain", "--untracked-files=all", "--ignored"),
    }


def changed(before, after):
    """What differs between two snapshots, in words."""
    out = []
    for rel in sorted(set(before["files"]) | set(after["files"])):
        if before["files"].get(rel) != after["files"].get(rel):
            state = "added" if rel not in before["files"] else "removed" if rel not in after["files"] else "rewritten"
            out.append(f"{rel}: {state}")
    out += [f"git {key} changed" for key in ("head", "refs", "index", "status") if before[key] != after[key]]
    return out


# --------------------------------------------------------------------------
# Records
# --------------------------------------------------------------------------

def record(record_id, record_type, status, title="A record", body="Body text.", **keys):
    """A record file: frontmatter (``id``, ``type``, ``status``, ``state_class``, the given keys) and a body."""
    lines = [f"id: {record_id}", f"type: {record_type}", f"status: {status}", "state_class: AUTHORITATIVE",
             f"title: {title}"]
    for key, value in keys.items():
        lines.append(f"{key}: {json.dumps(value)}")  # a JSON list or string is a YAML flow value
    return "---\n" + "\n".join(lines) + f"\n---\n\n# {record_id} — {title}\n\n{body}\n"


def decision(record_id, status, **keys):
    """A MADR decision record, as the decision-record template of W1-08 and W1-34 writes it."""
    return record(record_id, "decision", status, **keys)


def package(record_id, status, cit, constrains=()):
    """A decision package, as the template of W1-34 writes it: state in `status` alone, the CIT in `cit`.
    ``cit=None`` leaves the key out."""
    keys = {"rank": "P2", "cit": cit, "constrains": list(constrains)}
    if cit is None:
        del keys["cit"]
    return record(record_id, "decision-package", status, **keys)


def ticket(ticket_id, status="open", **keys):
    """A ticket as tk and the task contract write it."""
    return record(ticket_id, "task", status, deps=[], role="engineer", allowed_paths=["src/**"],
                  kpis={"success": ["works"], "failure": []}, **keys)


def adr_path(record_id):
    return f"docs/adr/{record_id}.md"


def ticket_path(ticket_id):
    return f".tickets/{ticket_id}.md"


def package_path(record_id):
    return f"docs/decisions/packages/{record_id}.md"


# A decision register with no hazard: one directory, distinct ids, a supersession recorded on both sides and a
# chain of three that ends.
CLEAN = {
    adr_path("ADR-0001"): decision("ADR-0001", "ACTIVE"),
    adr_path("ADR-0002"): decision("ADR-0002", "SUPERSEDED", superseded_by="ADR-0003"),
    adr_path("ADR-0003"): decision("ADR-0003", "SUPERSEDED", supersedes=["ADR-0002"], superseded_by="ADR-0004"),
    adr_path("ADR-0004"): decision("ADR-0004", "ACTIVE", supersedes=["ADR-0003"], depends_on=["ADR-0001"]),
    adr_path("ADR-0005"): decision("ADR-0005", "PROPOSED"),
    "README.md": "# A project\n\nNo frontmatter here.\n",
}
