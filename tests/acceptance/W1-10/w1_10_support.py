"""Support code for the W1-10 acceptance tests (standard library only).

W1-10 builds the store and the record graph. No ``gov`` command belongs to this
ticket (``src/gov/cli/**`` is outside its paths), so the tests use the two
packages' Python interface, stated in the README:

- ``gov.store.load(root)`` and ``gov.store.digest(root)``;
- ``gov.records.records``, ``active``, ``edges``, ``dangling`` and ``commits``.

How the tests call it:

- **Every call runs in a new Python process**, through a small driver written to
  a temporary directory, with this worktree's ``src/`` on ``PYTHONPATH``. A new
  process gives each load its own hash seed and time zone, which a load in the
  test's own process could not.
- **The store is never built in this worktree.** Every project is a temporary
  git repository; ``load`` writes ``.gov-runtime/store.db`` there.
- **The environment is built from scratch:** ``PATH``, an empty temporary
  ``HOME``, ``TMPDIR``, locale, ``PYTHONPATH`` and ``PYTHONPYCACHEPREFIX``.
  ``GOV_ROLE`` and ``GOV_TICKET`` of the session that runs the tests are not
  passed on.
- **Fixture commits have fixed dates and authors**, so the same fixture built
  twice has the same commit ids.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
STORE_REL = ".gov-runtime/store.db"
STORE_MODULE = "gov.store"
RECORDS_MODULE = "gov.records"
CALL_TIMEOUT_S = 120.0
MISSING_EXIT = 3

# The eight typed edges of CAP-09.a.
EDGE_TYPES = ("EVIDENCE_FOR", "CONSTRAINS", "IMPLEMENTS", "TESTS", "GENERATES", "VALIDATES", "SUPERSEDES",
              "DEPENDS_ON")

DEV_TIERS = Path(os.environ.get("GOV_DEV_TIERS") or Path.home() / "gov-os-workbench" / "synthetic")
DEV_TIER_NAMES = ("a-dev", "b-dev")
FULL_LOAD_LIMIT_S = 5.0

_DRIVER = '''\
import importlib, json, sys, time
from pathlib import Path

out = []
for call in json.loads(sys.stdin.read()):
    try:
        function = getattr(importlib.import_module(call["module"]), call["function"])
    except ModuleNotFoundError as exc:
        if exc.name not in ("gov.store", "gov.records"):
            raise
        print(f"no module {exc.name}", file=sys.stderr)
        sys.exit(3)
    except AttributeError:
        print(f"{call['module']} has no function {call['function']}", file=sys.stderr)
        sys.exit(3)
    started = time.perf_counter()
    value = function(Path(call["root"]), **call["kwargs"])
    out.append({"value": value, "seconds": time.perf_counter() - started})
print(json.dumps(out))
'''


class StoreMissing(AssertionError):
    """The store or the record graph does not exist yet."""


# --------------------------------------------------------------------------
# Calling the public interface
# --------------------------------------------------------------------------

class Api:
    """Calls ``gov.store`` and ``gov.records`` of this worktree, each batch in a new process."""

    def __init__(self, workdir):
        self.workdir = Path(workdir)
        for name in ("home", "tmp", "pycache"):
            (self.workdir / name).mkdir(parents=True, exist_ok=True)
        self.driver = self.workdir / "driver.py"
        self.driver.write_text(_DRIVER, encoding="utf-8")

    def batch(self, calls, **env):
        """Run ``[(module, function, root, kwargs), ...]`` in one process; ``[(value, seconds), ...]``."""
        request = [{"module": module, "function": function, "root": str(root), "kwargs": kwargs}
                   for module, function, root, kwargs in calls]
        environment = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(self.workdir / "home"),
            "TMPDIR": str(self.workdir / "tmp"),
            "LC_ALL": "C.UTF-8",
            "GIT_CONFIG_NOSYSTEM": "1",
            "PYTHONPATH": str(SRC),
            "PYTHONPYCACHEPREFIX": str(self.workdir / "pycache"),
            **env,
        }
        what = ", ".join(f"{module}.{function}" for module, function, _, _ in calls)
        try:
            done = subprocess.run([sys.executable, str(self.driver)], input=json.dumps(request), env=environment,
                                  cwd=str(self.workdir), capture_output=True, text=True, timeout=CALL_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"{what} did not end within {CALL_TIMEOUT_S:.0f} s") from None
        if done.returncode == MISSING_EXIT:
            raise StoreMissing(f"the store and record graph do not exist: {done.stderr.strip()} under src/")
        assert done.returncode == 0, f"{what} failed (exit code {done.returncode}):\n{done.stderr}"
        try:
            answers = json.loads(done.stdout)
        except ValueError:
            raise AssertionError(f"{what} did not return JSON values:\n{done.stdout}\n{done.stderr}") from None
        return [(answer["value"], answer["seconds"]) for answer in answers]

    def call(self, module, function, root, env=None, **kwargs):
        return self.batch([(module, function, root, kwargs)], **(env or {}))[0][0]

    def exists(self):
        """Raise StoreMissing unless every function of the public interface can be imported."""
        names = [(STORE_MODULE, "load"), (STORE_MODULE, "digest")]
        names += [(RECORDS_MODULE, name) for name in ("records", "active", "edges", "dangling", "commits")]
        source = "import importlib,sys\n" + "".join(
            f"getattr(importlib.import_module({module!r}), {name!r})\n" for module, name in names)
        done = subprocess.run([sys.executable, "-c", source], capture_output=True, text=True, cwd=str(self.workdir),
                              env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONPATH": str(SRC),
                                   "PYTHONPYCACHEPREFIX": str(self.workdir / "pycache")})
        if done.returncode != 0:
            last = done.stderr.strip().splitlines()[-1] if done.stderr.strip() else "import failed"
            raise StoreMissing(f"the store and record graph do not exist: {last}")

    # ---- gov.store

    def load(self, root, **env):
        """``gov.store.load(root)``: the summary, checked for the two keys the interface fixes."""
        summary = self.call(STORE_MODULE, "load", root, env=env)
        assert isinstance(summary, dict), f"load did not return a map: {summary!r}"
        assert is_digest(summary.get("digest")), f"load's `digest` is not a sha256 in hex: {summary.get('digest')!r}"
        assert isinstance(summary.get("invalid"), list), f"load's `invalid` is not a list: {summary.get('invalid')!r}"
        return summary

    def timed_load(self, root):
        return self.batch([(STORE_MODULE, "load", root, {})])[0]

    def digest(self, root, **env):
        return self.call(STORE_MODULE, "digest", root, env=env)

    # ---- gov.records

    def records(self, root, **filters):
        return self.call(RECORDS_MODULE, "records", root, **filters)

    def ids(self, root, **filters):
        return sorted(record["id"] for record in self.records(root, **filters))

    def active(self, root, **filters):
        return self.call(RECORDS_MODULE, "active", root, **filters)

    def edges(self, root, **filters):
        return self.call(RECORDS_MODULE, "edges", root, **filters)

    def dangling(self, root):
        return self.call(RECORDS_MODULE, "dangling", root)

    def commits(self, root, **filters):
        return self.call(RECORDS_MODULE, "commits", root, **filters)

    def dump(self, root, **env):
        """The logical content of the store, through the queries alone, in a form two loads can be compared by."""
        calls = [(RECORDS_MODULE, name, root, {}) for name in ("records", "edges", "dangling", "commits")]
        records, edges, dangling, commits = (value for value, _ in self.batch(calls, **env))
        return {
            "records": sorted(json.dumps(record, sort_keys=True) for record in records),
            "edges": sorted(triples(edges)),
            "dangling": sorted(triples(dangling)),
            "commits": by_commit(commits),
        }


def is_digest(value):
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def triples(edges):
    """``[(type, source, target), ...]`` of a list of edges, in the order given."""
    assert isinstance(edges, list), f"not a list of edges: {edges!r}"
    for edge in edges:
        assert isinstance(edge, dict) and {"type", "source", "target"} <= set(edge), \
            f"an edge is not a map with type, source and target: {edge!r}"
    return [(edge["type"], edge["source"], edge["target"]) for edge in edges]


def record_edges(edges, commit_ids=()):
    """The edges between records, as a sorted list of triples: an edge whose source is a commit is left out.

    Whether an ``Implements:`` trailer is also an edge of the graph is open (package DP-5); the tests of the
    frontmatter edges hold either way.
    """
    return sorted(triple for triple in triples(edges) if triple[1] not in set(commit_ids))


def by_commit(commits):
    """``commit id -> (sorted Task ids, sorted Implements ids)`` of a ``commits`` answer."""
    assert isinstance(commits, list), f"not a list of commits: {commits!r}"
    found = {}
    for entry in commits:
        assert isinstance(entry, dict) and {"commit", "task", "implements"} <= set(entry), \
            f"a commit is not a map with commit, task and implements: {entry!r}"
        assert entry["commit"] not in found, f"the commit {entry['commit']} is listed twice"
        found[entry["commit"]] = (sorted(entry["task"]), sorted(entry["implements"]))
    return found


def invalid_paths(summary):
    for entry in summary["invalid"]:
        assert isinstance(entry, dict) and isinstance(entry.get("path"), str) and entry.get("reason"), \
            f"an `invalid` entry is not a map with a path and a reason: {entry!r}"
    return sorted(entry["path"] for entry in summary["invalid"])


# --------------------------------------------------------------------------
# git
# --------------------------------------------------------------------------

BASE_DATE = "2026-09-01T12:00:00+00:00"


def git(project, *args, date=BASE_DATE, check=True):
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(project),
        "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "W1-10 tests", "GIT_AUTHOR_EMAIL": "w1-10@example.invalid",
        "GIT_COMMITTER_NAME": "W1-10 tests", "GIT_COMMITTER_EMAIL": "w1-10@example.invalid",
        "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date,
    }
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, env=env)
    if check and done.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {project}:\n{done.stderr}")
    return done.stdout


def write(project, rel, text):
    path = Path(project) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def commit(project, message, date, trailers=()):
    """Commit everything; ``trailers`` go in the final trailer block with ``git commit --trailer`` (DEC-182)."""
    git(project, "add", "-A")
    arguments = ["commit", "-q", "--allow-empty", "-m", message]
    for trailer in trailers:
        arguments += ["--trailer", trailer]
    git(project, *arguments, date=date)
    return head(project)


def head(project):
    return git(project, "rev-parse", "HEAD").strip()


def all_commits(project):
    return sorted(git(project, "rev-list", "HEAD").split())


def clone(source, destination):
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(source), str(destination)], check=True,
                   capture_output=True)
    return Path(destination)


def porcelain(project):
    return git(project, "status", "--porcelain").splitlines()


# --------------------------------------------------------------------------
# The fixture record set
# --------------------------------------------------------------------------

def record(record_id, record_type, status, title, **keys):
    """A record file: frontmatter (``id``, ``type``, ``status``, ``state_class``, the given keys) and a body."""
    lines = [f"id: {record_id}", f"type: {record_type}", f"status: {status}", "state_class: AUTHORITATIVE",
             f"title: {title}"]
    for key, value in keys.items():
        lines.append(f"{key}: {json.dumps(value)}")  # a JSON list or string is a YAML flow value
    return "---\n" + "\n".join(lines) + f"\n---\n\n# {record_id} — {title}\n\nBody text.\n"


TICKET = "DAEO-aaaa"

# path -> text. The record files of the fixture; each record's edges are in its own frontmatter.
RECORD_FILES = {
    "docs/adr/ADR-0001-first.md": record(
        "ADR-0001", "decision", "ACTIVE", "First", depends_on=[], supersedes=[], consumers=["W1-11"],
        decisions=["DEC-012"]),
    "docs/adr/ADR-0002-second.md": record(
        "ADR-0002", "decision", "ACTIVE", "Second", supersedes=["ADR-0003"], depends_on=["ADR-0001"],
        implements=["REQ-0001"], constrains=["ADR-0001", "REQ-0001"]),
    # Its own frontmatter still says ACTIVE; ADR-0002 supersedes it.
    "docs/adr/ADR-0003-third.md": record("ADR-0003", "decision", "ACTIVE", "Third"),
    # Named from both sides: one SUPERSEDES edge, not two.
    "docs/adr/ADR-0004-fourth.md": record("ADR-0004", "decision", "SUPERSEDED", "Fourth", superseded_by="ADR-0005"),
    "docs/adr/ADR-0005-fifth.md": record(
        "ADR-0005", "decision", "ACTIVE", "Fifth", supersedes=["ADR-0004"], depends_on=["ADR-0001", "ADR-0099"]),
    "docs/adr/ADR-0006-sixth.md": record("ADR-0006", "decision", "PROPOSED", "Sixth"),
    # Says ACTIVE and names its own successor; the successor does not name it.
    "docs/adr/ADR-0007-seventh.md": record("ADR-0007", "decision", "ACTIVE", "Seventh", superseded_by=["ADR-0005"]),
    "docs/spec/REQ-0001.md": record("REQ-0001", "requirement", "ACTIVE", "A requirement"),
    f".tickets/{TICKET}.md": record(
        TICKET, "task", "closed", "A ticket", role="engineer", allowed_paths=["src/**"],
        kpis={"success": ["works"], "failure": []}, deps=[], implements=["REQ-0001"]),
    "docs/evidence/TR-0001.md": record(
        "TR-0001", "evidence", "FINAL", "A test result", validates=["REQ-0001"], tests=["REQ-0001"],
        evidence_for=["ADR-0001"]),
    "docs/research/RR-0001.md": record(
        "RR-0001", "research", "FINAL", "A research record", generates=["ADR-0006"], evidence_for=["ADR-0001"],
        validates=["REQ-0404"]),
    "docs/lessons/L-0001.md": record("L-0001", "lesson", "ACTIVE", "A lesson", lifecycle="candidate"),
}

# Files that are not records: no frontmatter, or frontmatter without an `id`.
OTHER_FILES = {
    "README.md": "# A project\n\nNo frontmatter here.\n",
    ".claude/agents/engineer.md": "---\nname: engineer\ndescription: a role file, not a record\n---\n\nRole text.\n",
    "docs/notes.md": "Plain notes.\n\n---\n\nA rule in the middle is not frontmatter.\n",
}

RECORD_PATHS = {text.split("\n")[1][len("id: "):]: path for path, text in RECORD_FILES.items()}
RECORD_IDS = sorted(RECORD_PATHS)

# What the frontmatter above says, edge by edge: (type, source, target).
EXPECTED_EDGES = sorted([
    ("SUPERSEDES", "ADR-0002", "ADR-0003"), ("SUPERSEDES", "ADR-0005", "ADR-0004"),
    ("SUPERSEDES", "ADR-0005", "ADR-0007"),
    ("DEPENDS_ON", "ADR-0002", "ADR-0001"), ("DEPENDS_ON", "ADR-0005", "ADR-0001"),
    ("DEPENDS_ON", "ADR-0005", "ADR-0099"),
    ("IMPLEMENTS", "ADR-0002", "REQ-0001"), ("IMPLEMENTS", TICKET, "REQ-0001"),
    ("CONSTRAINS", "ADR-0002", "ADR-0001"), ("CONSTRAINS", "ADR-0002", "REQ-0001"),
    ("VALIDATES", "TR-0001", "REQ-0001"), ("VALIDATES", "RR-0001", "REQ-0404"),
    ("TESTS", "TR-0001", "REQ-0001"),
    ("EVIDENCE_FOR", "TR-0001", "ADR-0001"), ("EVIDENCE_FOR", "RR-0001", "ADR-0001"),
    ("GENERATES", "RR-0001", "ADR-0006"),
])
EXPECTED_DANGLING = sorted([("DEPENDS_ON", "ADR-0005", "ADR-0099"), ("VALIDATES", "RR-0001", "REQ-0404")])
ACTIVE_DECISIONS = ["ADR-0001", "ADR-0002", "ADR-0005"]
ACTIVE_ALL = sorted(ACTIVE_DECISIONS + ["REQ-0001", "L-0001"])
STATUS_ACTIVE_DECISIONS = ["ADR-0001", "ADR-0002", "ADR-0003", "ADR-0005", "ADR-0007"]

BEFORE_RULE = "2026-09-20T12:00:00+00:00"   # before 2026-10-03: the body fallback of DEC-182 applies
AFTER_RULE = "2026-10-04T12:00:00+00:00"    # from 2026-10-03: the final trailer block only
LATER = "2026-10-05T12:00:00+00:00"


def build_fixture(project, reverse=False):
    """Build the fixture repository; ``commit name -> commit id``.

    ``reverse`` writes the files in the opposite order. The commits are the same either way.
    """
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    git(project, "init", "-q", "-b", "main")
    files = sorted({**RECORD_FILES, **OTHER_FILES}.items(), reverse=reverse)
    for rel, text in files:
        write(project, rel, text)
    commits = {"base": commit(project, "records", BASE_DATE)}

    # Before 2026-10-03, trailers in the body and not in the last paragraph: read by the fallback.
    write(project, "src/app.py", "print('one')\n")
    commits["old_body"] = commit(
        project,
        f"old work\n\nTask: {TICKET}\nImplements: ADR-0001\n\nA closing paragraph, which is not a trailer block.",
        BEFORE_RULE)

    write(project, "src/app.py", "print('two')\n")
    commits["final_block"] = commit(project, "new work", AFTER_RULE,
                                    trailers=[f"Task: {TICKET}", "Implements: ADR-0002", "Role: engineer"])

    write(project, "src/other.py", "print('other')\n")
    commits["two_ids"] = commit(project, "work under two decisions", AFTER_RULE,
                                trailers=[f"Task: {TICKET}", "Implements: ADR-0001, ADR-0002", "Role: engineer"])

    # From 2026-10-03, trailers in the body and not in the last paragraph: not trailers.
    write(project, "src/late.py", "print('late')\n")
    commits["new_body"] = commit(
        project,
        f"late work\n\nTask: {TICKET}\nImplements: ADR-0001\n\nA closing paragraph, which is not a trailer block.",
        LATER)
    return commits


EXPECTED_TRAILERS = {
    "base": ([], []),
    "old_body": ([TICKET], ["ADR-0001"]),
    "final_block": ([TICKET], ["ADR-0002"]),
    "two_ids": ([TICKET], ["ADR-0001", "ADR-0002"]),
    "new_body": ([], []),
}
