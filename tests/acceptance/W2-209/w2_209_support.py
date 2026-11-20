"""Support code for W2-209's acceptance tests: releasing on the owner's behalf, slice (a), the patch release.

Public interfaces only (README, "Interface"): the ``gov`` command line (``gov release <X> --patch [--check] [--suite]
[--kept] [--push] --json``), ``python3 -m gov.close.nightly``, the functions the ticket names
(``gov.release._patch_test``, ``gov.release.proving.rehearse``, ``gov.release.repin.repin``, ``gov.release.repin.burned``,
``gov.update.pending.pending``, ``gov.close.nightly.night``, ``gov.release.verify_at``) and the files they write.
Each function is called in a child process (``w2_209_driver.py``) whose ``HOME`` is the case's scratch home, so no
call of the code under test can reach the machine's own ``~/.local/bin/gov``, pins or burned list.

**The planted source** (``build_base``): a git repository of its own, built at test time, that looks to the release
code like the Gov OS repository: ``pyproject.toml`` (project ``gov``), a small stand-in ``gov`` package under
``src/gov`` (a command line that answers ``--version``, ``--help``, ``launch --help``, ``retrieve --json`` and
``doctor --json`` as the real one does, two command modules, a hook probe), ``template/`` (two kit schemas, the five
hook programs), ``docs/contract``, ``docs/charter``, ``docs/emergency-2/EMERGENCY-2.md``, ``.tickets/``, the
authority file and the tool registry. Its releases ``0.1.0`` and ``0.1.1`` are built with ``gov.release.build`` (the
code on the base, unchanged by this ticket), committed and tagged ``v<X>`` (annotated) on the record commit; a decoy
tag ``v0.1.9`` with no record sits on the first commit. From ``v0.1.1`` (N) one branch per planted change
(``case/<name>``, ``CASES``) and the clean range (``case/clean``) each end in the version commit.

Nothing here writes in this worktree; every repository is under pytest's ``tmp_path``.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import site
import stat
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
DRIVER = HERE / "w2_209_driver.py"

# --------------------------------------------------------------------------
# The interface (README, "Interface")
# --------------------------------------------------------------------------

INTEGRATION = "w2/integrate"
RELEASES_REL = "docs/releases"
AUTHORITY_REL = "governance/project/release-authority.yaml"
REGISTRY_REL = "governance/project/tool-registry.yaml"
FREEZE_REL = ".gov-runtime/freeze"
NIGHTLY_REL = "docs/close/nightly"
HOOKS_REL = "template/governance/kernel/hooks"
SCHEMAS_REL = "template/governance/kernel/schemas"
HOOKS = ("context_watch", "precompact", "sessionstart", "stop", "subagentstop")

REFUSED = "RELEASE_REFUSED"
RULES = ("P1", "P2", "P3", "P4", "P5")
RECORD_FILES = ("manifest.json", "manifest.sha256", "kind.json", "gates.json", "suite.json")
NOTE = "NOTE.md"
ROLLBACK_LINE = "bash ~/.local/share/gov-os/rollback.sh"
DECISION = "DEC-1223"
DECIDED_BY = f"owner (standing, {DECISION})"
PUSH_LIMIT = 190
REPOSITORIES = ("python-app", "rust-workspace", "typescript-monorepo", "legacy-docs", "secret-history",
                "python-app-clean")

A, N_VERSION, X = "0.1.0", "0.1.1", "0.1.2"
DECOY = "v0.1.9"
TIMEOUT_S = 900.0

# --------------------------------------------------------------------------
# git
# --------------------------------------------------------------------------

IDENTITY = {"GIT_AUTHOR_NAME": "W2-209 tests", "GIT_AUTHOR_EMAIL": "w2-209@example.invalid",
            "GIT_COMMITTER_NAME": "W2-209 tests", "GIT_COMMITTER_EMAIL": "w2-209@example.invalid"}


def git(repo, *args, check=True, input=None):
    env = {**os.environ, **IDENTITY, "GIT_CONFIG_NOSYSTEM": "1"}
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=env, input=input)
    if check and done.returncode:
        raise AssertionError(f"W2-209 fixture could not be built (not the feature under test): git {' '.join(args)}"
                             f" in {repo}: {done.stderr.strip()}")
    return done.stdout


def rev(repo, what="HEAD"):
    return git(repo, "rev-parse", "--verify", "--quiet", what).strip()


def tree_of(repo, what="HEAD"):
    return rev(repo, f"{what}^{{tree}}")


def message(subject, trailers=()):
    body = subject
    if trailers:
        body += "\n\n" + "\n".join(f"{key}: {value}" for key, value in trailers)
    return body + "\n"


def write(repo, files):
    for rel, text in files.items():
        path = Path(repo) / rel
        if text is None:
            if path.exists():
                path.unlink()
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def commit(repo, files, subject, trailers=()):
    """Write ``files`` (``None`` removes one), commit everything with ``subject`` and ``trailers``; the new HEAD."""
    write(repo, files)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "--allow-empty", "-F", "-", input=message(subject, trailers))
    return rev(repo)


def trailer(repo, what, key):
    """The values of trailer ``key`` in commit ``what``'s message."""
    out = git(repo, "log", "-1", f"--format=%(trailers:key={key},valueonly,separator=%x00)", what)
    return [value.strip() for value in out.strip().split("\0") if value.strip()]


def is_ancestor(repo, older, newer):
    return subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", older, newer],
                          capture_output=True).returncode == 0


def tag_type(repo, tag):
    return git(repo, "cat-file", "-t", f"refs/tags/{tag}", check=False).strip()


def show(repo, what):
    done = subprocess.run(["git", "-C", str(repo), "show", what], capture_output=True)
    return done.stdout if done.returncode == 0 else None


def changed_paths(repo, older, newer):
    return sorted(p for p in git(repo, "diff", "--name-only", older, newer).splitlines() if p.strip())


def copy_repo(origin, destination):
    """A copy of a repository the tests built (never of this worktree), ``.git`` with it."""
    origin, destination = Path(origin), Path(destination)
    assert REPO_ROOT.resolve() not in (origin.resolve(), *origin.resolve().parents), "never copy this worktree"
    shutil.copytree(origin, destination, symlinks=True)
    return destination


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


# --------------------------------------------------------------------------
# Snapshots: a refused or read-only call changes nothing
# --------------------------------------------------------------------------

def _entries(root, skip_git=True):
    root = Path(root)
    found = {}
    if not os.path.lexists(root):
        return None
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if skip_git and (rel == ".git" or rel.startswith(".git/")):
            continue
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode):
            found[rel] = ("link", os.readlink(path))
        elif stat.S_ISDIR(info.st_mode):
            found[rel + "/"] = ("folder", stat.S_IMODE(info.st_mode))
        else:
            found[rel] = (sha256_bytes(path.read_bytes()), stat.S_IMODE(info.st_mode))
    return found


def snapshot(repo):
    """Every file and folder outside ``.git`` (bytes and mode), every ref, HEAD, the index and the stashes."""
    return {"files": _entries(repo), "refs": git(repo, "for-each-ref", "--format=%(refname) %(objectname)"),
            "head": rev(repo), "symbolic": git(repo, "symbolic-ref", "-q", "HEAD", check=False),
            "index": git(repo, "ls-files", "-s"), "stash": git(repo, "stash", "list", check=False)}


def folder_snapshot(folder):
    """Every entry under ``folder``, ``.git`` included (a kept run is read, never written)."""
    return _entries(folder, skip_git=False)


def difference(before, after):
    if before is None or after is None:
        return [] if before == after else ["<the folder itself>"]
    if "files" not in before:
        return sorted(rel for rel in set(before) | set(after) if before.get(rel) != after.get(rel))
    changed = [key for key in ("refs", "head", "symbolic", "index", "stash") if before[key] != after[key]]
    files_before, files_after = before["files"], after["files"]
    changed += sorted(rel for rel in set(files_before) | set(files_after) if files_before.get(rel) != files_after.get(rel))
    return changed


# --------------------------------------------------------------------------
# The planted source
# --------------------------------------------------------------------------

PYPROJECT = """[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "gov"
version = "{version}"
description = "The planted Gov OS of the W2-209 tests"
requires-python = ">=3.10"

[project.scripts]
gov = "gov.cli.main:main"

[tool.setuptools.packages.find]
where = ["src"]
"""

# The stand-in command line: what the re-pin's checks ask of a gov, in the real envelopes' forms (``gov doctor
# --json`` exits 3 with DOCTOR_UNHEALTHY and its parts in ``error.details`` when a part fails or drifts; ``gov retrieve
# --json`` gives ``result.facets.<facet>.available``). ``canaries`` is unhealthy in every gov here, before and after.
CLI_BODY = r'''
import json
import sys

_WITH_VALUE = ("--root", "--session", "--role")


def _command(argv):
    skip = False
    for word in argv:
        if skip:
            skip = False
            continue
        if word in _WITH_VALUE:
            skip = True
            continue
        if not word.startswith("-"):
            return word
    return None


def _print(data):
    print(json.dumps(data))


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    command = _command(argv)
    if "--version" in argv and command is None:
        print(f"gov {_version()}")
        return 0
    if command is None:
        print("usage: gov <command> ... (the planted gov of the W2-209 tests)")
        return 0
    if command == "launch" and ("--help" in argv or "-h" in argv):
        print("usage: gov launch <role> <ticket> (the planted gov)")
        return 0
    if command == "retrieve":
        facets = {"lexical": {"available": True}, "semantic": {"available": _fail() != "facet"}}
        _print({"ok": True, "command": "retrieve", "result": {"facets": facets, "evidence": []}, "session": ""})
        return 0
    if command == "doctor":
        parts = {"tools": {"status": "pass"}, "hooks": {"status": "fail" if _fail() == "doctor" else "pass"},
                 "canaries": {"status": "fail", "reason": "planted: unhealthy before and after"}}
        _print({"ok": False, "command": "doctor", "result": {}, "session": "",
                "error": {"code": "DOCTOR_UNHEALTHY", "message": "one or more health checks failed",
                          "details": {"healthy": False, **parts}}})
        return 3
    if "--help" in argv or "-h" in argv:
        print(f"usage: gov {command} ... (the planted gov)")
        return 0
    _print({"ok": False, "command": command, "result": {}, "session": "",
            "error": {"code": "NOT_IMPLEMENTED", "message": "the planted gov answers only the re-pin's checks"}})
    return 1
'''

PACKAGE_MAIN = '"""The planted Gov OS\'s stand-in command line (W2-209 tests)."""\n' + CLI_BODY + r'''

def _fail():
    from gov import w2209_behaviour
    return w2209_behaviour.FAIL


def _version():
    if _fail() == "version":
        return "7.7.7"
    from importlib import metadata
    return metadata.version("gov")


if __name__ == "__main__":
    sys.exit(main())
'''

OLD_PIN_SCRIPT = "#!{python}\n" + '"""The live pin\'s gov in a scratch home (W2-209 tests): release {version}."""\n' + CLI_BODY + r'''

def _fail():
    return None


def _version():
    return "{version}"


if __name__ == "__main__":
    sys.exit(main())
'''

HOOKPROBE = '''"""What the planted hooks ask of the pinned gov (W2-209 tests)."""
import sys

from gov import w2209_behaviour


def run(name):
    sys.stdin.read()
    if w2209_behaviour.FAIL == f"hook_exit:{name}":
        print(f"the planted {name} hook fails", file=sys.stderr)
        return 1
    if w2209_behaviour.FAIL == f"hook_crash:{name}":
        raise RuntimeError(f"the planted {name} hook crashes")
    return 0
'''

HOOK = '''"""A planted hook program (W2-209 tests): run through the pinned gov's interpreter."""
import sys

from gov import hookprobe

sys.exit(hookprobe.run("{name}"))
'''


def behaviour(fail=None):
    return f'"""What the planted gov does wrong, if anything (W2-209 tests)."""\nFAIL = {fail!r}\n'


def ticket(ident, status, wbs):
    return f"---\nid: {ident}\nstatus: {status}\nwbs_id: {wbs}\ntype: task\n---\n# {ident}: a planted ticket\n"


def authority(state="off", decision=DECISION, bake=4):
    lines = [f"patch_releases: {state}"]
    if decision is not None:
        lines.append(f"decision: {decision}")
    lines.append(f"bake_hours: {bake}")
    return "\n".join(lines) + "\n"


REGISTRY = """# The machine's tools (planted, W2-209 tests)
tools:
  - name: other
    version: "1.0"
    sha256: "0000000000000000000000000000000000000000000000000000000000000000"
  - name: gov
    version: "0.1.1"
    sha256: "1111111111111111111111111111111111111111111111111111111111111111"
    install: "a planted install line"
    uninstall: "a planted uninstall line"
    note: "the live pin of the planted machine"
  - name: tail
    version: "2.0"
    sha256: "2222222222222222222222222222222222222222222222222222222222222222"
"""

SCHEMA = '{"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "%s", "type": "object"}\n'

BASE_FILES = {
    ".gitignore": ".gov-runtime/\n__pycache__/\n*.egg-info/\nbuild/\n",
    "pyproject.toml": PYPROJECT.format(version=A),
    "src/gov/__init__.py": '"""The planted Gov OS (W2-209 tests)."""\n',
    "src/gov/cli/__init__.py": "",
    "src/gov/cli/main.py": PACKAGE_MAIN,
    "src/gov/w2209_behaviour.py": behaviour(None),
    "src/gov/hookprobe.py": HOOKPROBE,
    "src/gov/alpha/__init__.py": "",
    "src/gov/alpha/command.py": '"""gov alpha (planted)."""\nHELP = "alpha"\nCLASS = "read"\n',
    "src/gov/alpha/core.py": "COUNT = 1\n",
    "src/gov/beta/__init__.py": "",
    "src/gov/beta/command.py": '"""gov beta (planted)."""\nHELP = "beta"\nCLASS = "read"\n',
    "template/README.md": "The planted kit.\n",
    f"{SCHEMAS_REL}/a.schema.json": SCHEMA % "a",
    f"{SCHEMAS_REL}/b.schema.json": SCHEMA % "b",
    **{f"{HOOKS_REL}/{name}.py": HOOK.format(name=name) for name in HOOKS},
    "docs/contract/CONTRACT.md": "# The planted Contract\n",
    "docs/charter/CHARTER.md": "# The planted Charter\n",
    "docs/emergency-2/EMERGENCY-2.md": "# The planted strategy\n",
    "docs/emergency-2/proposals/NOTE.md": "# A proposal (not the owner's text)\n",
    ".tickets/PLNT-aaaa.md": ticket("PLNT-aaaa", "open", "W9-01"),
    ".tickets/PLNT-bbbb.md": ticket("PLNT-bbbb", "open", "W9-02"),
    AUTHORITY_REL: authority("off"),
    REGISTRY_REL: REGISTRY,
}

OWNER_TRAILERS = (("Class", "C"), ("Role", "orchestrator"), ("Decided-by", DECIDED_BY))


@dataclass
class Case:
    """A planted range N..C: its branch, the release version it asks for, the rule it fails (None: clean) and
    what the rule's detail must name (a path, a ticket id, a commit's first 12 characters, a command name or a file
    name), filled in when the branch is built."""
    name: str
    version: str
    rule: str | None
    named: str = ""


def _version_commit(repo, version):
    return commit(repo, {"pyproject.toml": PYPROJECT.format(version=version)}, f"Version {version}",
                  (("Class", "C"),))


def _build_cases(repo, n_commit):
    cases = {}

    def start(name):
        git(repo, "checkout", "-q", "-B", f"case/{name}", n_commit)

    for name, rel in (("contract", "docs/contract/CONTRACT.md"), ("charter", "docs/charter/CHARTER.md"),
                      ("emergency", "docs/emergency-2/EMERGENCY-2.md")):
        start(name)
        commit(repo, {rel: f"# planted text\n\nchanged in the range ({name})\n"}, f"Change {rel}", (("Class", "C"),))
        _version_commit(repo, X)
        cases[name] = Case(name, X, "P2", rel)

    start("ticket")
    commit(repo, {".tickets/PLNT-bbbb.md": ticket("PLNT-bbbb", "closed", "W9-02")}, "Close PLNT-bbbb",
           (("Class", "C"), ("Task", "PLNT-bbbb")))
    _version_commit(repo, X)
    cases["ticket"] = Case("ticket", X, "P3", "PLNT-bbbb")

    start("feature")
    sha = commit(repo, {"src/gov/alpha/core.py": "COUNT = 2\nFEATURE = True\n"}, "Add a feature to alpha",
                 (("Class", "F"), ("Task", "PLNT-bbbb")))
    _version_commit(repo, X)
    cases["feature"] = Case("feature", X, "P3", sha[:12])

    start("fix_open_ticket")
    sha = commit(repo, {"src/gov/alpha/core.py": "COUNT = 3\n"}, "Fix alpha's count under an open ticket",
                 (("Class", "F"), ("Fix", "alpha counted wrong"), ("Task", "PLNT-bbbb")))
    _version_commit(repo, X)
    cases["fix_open_ticket"] = Case("fix_open_ticket", X, "P3", sha[:12])

    start("command")
    commit(repo, {"src/gov/w2209probe/__init__.py": "",
                  "src/gov/w2209probe/command.py": '"""gov w2209probe (planted)."""\nHELP = "probe"\nCLASS = "read"\n'},
           "Add the w2209probe command module", (("Class", "C"),))
    _version_commit(repo, X)
    cases["command"] = Case("command", X, "P4", "w2209probe")

    start("schema_added")
    commit(repo, {f"{SCHEMAS_REL}/new.schema.json": SCHEMA % "new"}, "Add a kit schema", (("Class", "C"),))
    _version_commit(repo, X)
    cases["schema_added"] = Case("schema_added", X, "P5", "new.schema.json")

    start("schema_removed")
    commit(repo, {f"{SCHEMAS_REL}/b.schema.json": None}, "Remove a kit schema", (("Class", "C"),))
    _version_commit(repo, X)
    cases["schema_removed"] = Case("schema_removed", X, "P5", "b.schema.json")

    start("minor")
    _version_commit(repo, "0.2.0")
    cases["minor"] = Case("minor", "0.2.0", "P1", "0.2.0")

    start("prerelease")
    _version_commit(repo, "0.1.2-rc.1")
    cases["prerelease"] = Case("prerelease", "0.1.2-rc.1", "P1", "0.1.2-rc.1")

    start("clean")
    fixes(repo)
    cases["clean"] = Case("clean", X, None)

    # G4's "the previous release's record cannot be read": a commit after N whose record of N no longer matches its
    # hash; the case's copy moves the tag v0.1.1 onto it (``previous_unreadable``).
    start("previous")
    rel = f"{RELEASES_REL}/{N_VERSION}/manifest.sha256"
    commit(repo, {rel: f"{'0' * 64}  manifest.json\n"}, "Break the record of 0.1.1", (("Class", "C"),))
    _version_commit(repo, X)
    cases["previous"] = Case("previous", X, None)
    return cases


FIX_LINES = ("alpha counted one too many", "the kit README named the wrong folder")
CHORE_SUBJECT = "Tidy the alpha notes"


def fixes(repo, version=X):
    """The clean range on the current branch: two ``Fix:`` commits (one merged with ``--no-ff``, whose merge commit
    carries no trailer), a ``Class: Q`` chore, a chore under docs/emergency-2 that is not EMERGENCY-2.md, the version."""
    commit(repo, {"src/gov/alpha/core.py": "COUNT = 0\n"}, "Fix alpha's count",
           (("Class", "F"), ("Fix", FIX_LINES[0]), ("Task", "PLNT-aaaa")))
    here = git(repo, "rev-parse", "--abbrev-ref", "HEAD").strip()
    git(repo, "checkout", "-q", "-b", f"{here}-side")
    commit(repo, {"template/README.md": "The planted kit (its folder named right).\n"}, "Fix the kit README",
           (("Class", "F"), ("Fix", FIX_LINES[1]), ("Task", "PLNT-aaaa")))
    git(repo, "checkout", "-q", here)
    git(repo, "merge", "-q", "--no-ff", "-m", f"Merge {here}-side", f"{here}-side")
    git(repo, "branch", "-q", "-D", f"{here}-side")
    commit(repo, {"src/gov/alpha/notes.py": "# notes\n"}, CHORE_SUBJECT, (("Class", "Q"),))
    commit(repo, {"docs/emergency-2/proposals/NOTE.md": "# A proposal, revised\n"}, "Revise a proposal",
           (("Class", "C"),))
    return _version_commit(repo, version)


@dataclass
class Base:
    path: Path
    n_commit: str        # the record commit of 0.1.1, the tag v0.1.1
    n_version_commit: str
    cases: dict


def record(repo, home, version, tag=True, extra=None, subject=None):
    """Build release ``version`` at HEAD with ``gov.release.build`` (the base's code), commit its record (with
    ``extra`` files beside it, in the cut's form) and tag the record commit ``v<version>``, annotated."""
    out = call(home, "gov.release:build", [path_arg(repo), version])
    assert out.kind == "returned", f"W2-209 fixture could not be built (not the feature under test): " \
                                   f"gov.release.build {version}: {out.describe()}"
    files = {f"{RELEASES_REL}/{version}/{name}": text for name, text in (extra or {}).items()}
    sha = commit(repo, files, subject or f"Release {version}: the record",
                 (("Role", "owner"), ("Task", "release")))
    if tag:
        git(repo, "tag", "-a", "-m", f"release {version}", f"v{version}", sha)
    return sha


def build_base(destination, home):
    """The planted source with releases 0.1.0 and 0.1.1 and one branch per case (module docstring)."""
    repo = Path(destination)
    repo.mkdir(parents=True)
    git(repo, "init", "-q", "-b", INTEGRATION)
    git(repo, "config", "user.name", "W2-209 tests")
    git(repo, "config", "user.email", "w2-209@example.invalid")
    git(repo, "config", "commit.gpgsign", "false")
    git(repo, "config", "tag.gpgsign", "false")
    first = commit(repo, BASE_FILES, "The planted Gov OS", OWNER_TRAILERS)
    record(repo, home, A)
    # Between the two releases, changes that every rule would see if N were the older release.
    commit(repo, {".tickets/PLNT-aaaa.md": ticket("PLNT-aaaa", "closed", "W9-01")}, "Close PLNT-aaaa",
           (("Class", "C"), ("Task", "PLNT-aaaa")))
    commit(repo, {"docs/contract/CONTRACT.md": "# The planted Contract, v2\n"}, "Contract v2", (("Class", "C"),))
    commit(repo, {f"{SCHEMAS_REL}/c.schema.json": SCHEMA % "c",
                  "src/gov/gamma/__init__.py": "",
                  "src/gov/gamma/command.py": '"""gov gamma (planted)."""\nHELP = "gamma"\nCLASS = "read"\n'},
           "Add gamma and its schema", (("Class", "F"), ("Task", "PLNT-aaaa")))
    n_version_commit = _version_commit(repo, N_VERSION)
    n_commit = record(repo, home, N_VERSION)
    git(repo, "tag", DECOY, first)
    cases = _build_cases(repo, n_commit)
    git(repo, "checkout", "-q", INTEGRATION)
    assert rev(repo) == n_commit
    return Base(repo, n_commit, n_version_commit, cases)


def make_case(base, destination, case, authority_on=True, integrate=True):
    """A copy of the base with HEAD on ``w2/integrate`` at the case's tip (``integrate=False``: HEAD on a branch
    ``side`` at the tip and ``w2/integrate`` left at N); with ``authority_on``, the authority file is turned on by a
    commit carrying the owner's standing trailer, as the decision-record commit does. Returns the copy's path."""
    repo = copy_repo(base.path, destination)
    name = case if isinstance(case, str) else case.name
    branch = INTEGRATION if integrate else "side"
    git(repo, "checkout", "-q", "-B", branch, f"case/{name}")
    if authority_on:
        turn_authority_on(repo)
    return repo


def turn_authority_on(repo, trailers=OWNER_TRAILERS, text=None):
    return commit(repo, {AUTHORITY_REL: text if text is not None else authority("on")},
                  "Patch releases on (the owner's standing yes)", trailers)


def previous_unreadable(repo):
    """Move the tag v0.1.1 onto the commit that broke its record (the case ``previous``)."""
    broken = rev(repo, "case/previous~1")
    git(repo, "tag", "-f", "-a", "-m", "release 0.1.1 (moved by the W2-209 tests)", f"v{N_VERSION}", broken)


# --------------------------------------------------------------------------
# Suite records (the nightly's form, DEC-1220 (1); README, "Interface")
# --------------------------------------------------------------------------

def suite_record(folder, name, head, tree, **change):
    """A nightly record file outside the tree; ``change`` replaces keys, a value ``DROP`` removes one."""
    data = {"branch": INTEGRATION, "head": head, "tree": tree, "base": None, "scope": "full", "verdict": "green",
            "secrets_full_scan": True, "junit_xml": [], "failures": [], "packages": [],
            "tests_run": {"passed": 412, "failed": 0, "errors": 0, "skipped": 3}, "findings": [],
            "per_test_timeout": 900, "distribution": "load", "tmp_path_retention_policy": "failed",
            "created": "2026-11-20T03:00:00Z", "optin": ["weekly"]}
    for key, value in change.items():
        if value is DROP:
            data.pop(key, None)
        else:
            data[key] = value
    path = Path(folder) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


DROP = object()


def good_suite(repo, folder, name="NR-good.json"):
    return suite_record(folder, name, rev(repo), tree_of(repo))


# --------------------------------------------------------------------------
# The scratch home: a pin folder, the link, a stand-in push command
# --------------------------------------------------------------------------

@dataclass
class Home:
    path: Path
    old_pin: Path

    @property
    def share(self):
        return self.path / ".local" / "share" / "gov-os"

    @property
    def link(self):
        return self.path / ".local" / "bin" / "gov"

    @property
    def burned_file(self):
        return self.share / "burned"

    @property
    def repin_json(self):
        return self.share / "repin.json"

    @property
    def rollback(self):
        return self.share / "rollback.sh"

    def target(self):
        return Path(os.path.realpath(self.link))

    def pins(self):
        return sorted(p.name for p in self.share.glob("pin-*"))

    def state(self):
        """The pin folders' names, the link's target and every entry under ``.local`` (links by target)."""
        return {"link": os.readlink(self.link) if os.path.lexists(self.link) else None,
                "target": str(self.target()), "pins": self.pins(), "entries": _entries(self.path / ".local")}


def make_home(destination, old_commit, version=N_VERSION, repositories=None):
    """A scratch ``$HOME``: the live pin ``pin-<12>`` of the release ``version`` (a stand-in gov script answering
    the re-pin's checks) and ``~/.local/bin/gov`` linked to its ``bin/gov``; ``repositories``, when given, is the
    list of adopted repositories (``~/.gov-os/update/repositories``)."""
    home = Path(destination)
    old = home / ".local" / "share" / "gov-os" / f"pin-{old_commit[:12]}"
    (old / "bin").mkdir(parents=True)
    script = old / "bin" / "gov"
    script.write_text(OLD_PIN_SCRIPT.replace("{python}", sys.executable).replace("{version}", version),
                      encoding="utf-8")
    script.chmod(0o755)
    (home / ".local" / "bin").mkdir(parents=True)
    os.symlink(script, home / ".local" / "bin" / "gov")
    (home / "tmp").mkdir()
    if repositories is not None:
        listed = home / ".gov-os" / "update" / "repositories"
        listed.parent.mkdir(parents=True)
        listed.write_text("".join(f"{line}\n" for line in repositories), encoding="utf-8")
    return Home(home, old)


PUSH_STANDIN = """#!{python}
import json, sys
with open(sys.argv[1], "a", encoding="utf-8") as handle:
    handle.write(json.dumps(sys.argv[2:]) + "\\n")
"""


def push_command(folder):
    """A stand-in push command: appends its arguments (the text is the last) as one JSON line to a file. Returns
    ``(command, file)``; the command is one string, as ``--push`` takes it."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    script = folder / "push-standin"
    script.write_text(PUSH_STANDIN.replace("{python}", sys.executable), encoding="utf-8")
    script.chmod(0o755)
    pushes = folder / "pushes.jsonl"
    return f"{script} {pushes}", pushes


def pushes(file, wait_s=20.0, settle_s=1.5):
    """The pushes recorded (each the list of arguments); waits for a first one (the push is detached), then a little
    more, so a second push would be seen too. ``wait_s=0``: read now."""
    file = Path(file)
    deadline = time.monotonic() + wait_s
    while wait_s and not (file.exists() and file.read_text(encoding="utf-8").strip()) and time.monotonic() < deadline:
        time.sleep(0.2)
    if wait_s and file.exists():
        time.sleep(settle_s)
    if not file.exists():
        return []
    return [json.loads(line) for line in file.read_text(encoding="utf-8").splitlines() if line.strip()]


# --------------------------------------------------------------------------
# Running gov and the functions
# --------------------------------------------------------------------------

def user_base():
    return os.environ.get("PYTHONUSERBASE") or site.getuserbase()


def environment(home, role=None, extra=None):
    """A child's environment built from nothing: the scratch home, this worktree's ``src/``, the real user base (so
    the packages gov needs import), no Claude Code variable, no ``GOV_TICKET``; ``GOV_ROLE`` only when given."""
    path = os.pathsep.join([str(Path(sys.executable).parent), "/usr/local/bin", "/usr/bin", "/bin"])
    env = {"PATH": path, "HOME": str(home), "LC_ALL": "C.UTF-8", "PYTHONPATH": str(SRC),
           "PYTHONUSERBASE": user_base(), "PYTHONDONTWRITEBYTECODE": "1", "GIT_CONFIG_NOSYSTEM": "1",
           "TMPDIR": str(Path(home) / "tmp"), **IDENTITY}
    if os.environ.get("GOV_REBUILD_LOCK"):
        env["GOV_REBUILD_LOCK"] = os.environ["GOV_REBUILD_LOCK"]
    if role is not None:
        env["GOV_ROLE"] = role
    env.update(extra or {})
    Path(env["TMPDIR"]).mkdir(parents=True, exist_ok=True)
    return env


@dataclass(frozen=True)
class Run:
    argv: tuple
    returncode: int
    stdout: str
    stderr: str

    def describe(self):
        return (f"{' '.join(map(str, self.argv))}\nexit code: {self.returncode}\nstdout:\n{self.stdout[-4000:]}\n"
                f"stderr:\n{self.stderr[-4000:]}")

    def envelope(self):
        try:
            data = json.loads(self.stdout)
        except ValueError:
            raise AssertionError(f"no API-0002 envelope on standard output (the command or flag is not "
                                 f"there)\n{self.describe()}") from None
        assert isinstance(data, dict), f"standard output is not a JSON object\n{self.describe()}"
        return data


def run(argv, cwd, env, timeout=TIMEOUT_S, stdin=subprocess.DEVNULL):
    assert Path(cwd).resolve() != REPO_ROOT.resolve(), "no command of these tests runs in this worktree"
    try:
        done = subprocess.run([str(a) for a in argv], cwd=str(cwd), env=env, capture_output=True, text=True,
                              timeout=timeout, stdin=stdin)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{' '.join(map(str, argv))} did not end within {timeout:.0f} s") from None
    return Run(tuple(map(str, argv)), done.returncode, done.stdout, done.stderr)


def gov(cwd, home, *args, role="orchestrator", extra=None, timeout=TIMEOUT_S):
    """``gov <args> --json`` in ``cwd`` with this worktree's code, ``HOME`` the scratch home."""
    return run((sys.executable, "-m", "gov.cli.main", *args, "--json"), cwd, environment(home, role, extra),
               timeout=timeout)


def release(cwd, home, version, *args, role="orchestrator", extra=None, timeout=TIMEOUT_S):
    return gov(cwd, home, "release", version, "--patch", *args, role=role, extra=extra, timeout=timeout)


def refusal(run_):
    """The details of a ``RELEASE_REFUSED`` envelope; fails naming what came instead."""
    envelope = run_.envelope()
    error = envelope.get("error") or {}
    assert envelope.get("ok") is False and error.get("code") == REFUSED, \
        f"not refused with {REFUSED}\n{run_.describe()}"
    assert run_.returncode != 0, f"a refusal that exits 0\n{run_.describe()}"
    details = error.get("details")
    assert isinstance(details, dict), f"the refusal carries no details\n{run_.describe()}"
    return details


def assert_gate(details, gate, what="", check=None, rule=None):
    assert details.get("gate") == gate, f"{what}: the refusal names gate {details.get('gate')!r}, not {gate}: {details}"
    assert isinstance(details.get("reason"), str) and details["reason"].strip(), f"{what}: no reason: {details}"
    if check is not None:
        assert details.get("check") == check, \
            f"{what}: the refusal names the check {details.get('check')!r}, not {check!r}: {details}"
    if rule is not None:
        assert details.get("rule") == rule, f"{what}: the refusal names rule {details.get('rule')!r}, not {rule}: {details}"


def path_arg(path):
    return {"path": str(path)}


@dataclass
class Outcome:
    kind: str                 # returned | raised | missing | crashed
    result: object = None
    error: dict = field(default_factory=dict)
    run: Run | None = None

    def describe(self):
        return f"{self.kind}: result={json.dumps(self.result, default=str)[:3000]} error={self.error}\n" + \
            (self.run.describe() if self.run else "")

    def returned(self, what=""):
        assert self.kind == "returned", f"{what}: the call did not return a result\n{self.describe()}"
        return self.result

    def refused(self, what=""):
        """The details of a ``GovError("RELEASE_REFUSED", ...)`` the call raised."""
        assert self.kind == "raised" and self.error.get("code") == REFUSED, \
            f"{what}: the call was not refused with {REFUSED}\n{self.describe()}"
        details = self.error.get("details")
        assert isinstance(details, dict), f"{what}: the refusal carries no details\n{self.describe()}"
        return details


_MARK = "W2-209-OUTCOME: "


def call(home, target, args=(), kwargs=None, role=None, extra=None, timeout=TIMEOUT_S, cwd=None):
    """Call ``module:function`` in a child process (``w2_209_driver.py``) with the scratch ``home`` as ``HOME``.
    ``args``/``kwargs`` are JSON; ``{"path": p}`` is a ``Path``; ``{"standin": name, ...}`` is a stand-in of
    ``w2_209_standins``. A function that does not exist is ``missing`` (the feature is not built)."""
    spec = json.dumps({"call": target, "args": list(args), "kwargs": kwargs or {}})
    env = environment(home, role, extra)
    try:
        proc = subprocess.run([sys.executable, str(DRIVER)], cwd=str(cwd or home), env=env, input=spec,
                              capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{target} did not return within {timeout:.0f} s") from None
    done = Run((target,), proc.returncode, proc.stdout, proc.stderr)
    lines = [line for line in proc.stdout.splitlines() if line.startswith(_MARK)]
    if not lines:
        return Outcome("crashed", run=done)
    data = json.loads(lines[-1][len(_MARK):])
    return Outcome(data["kind"], data.get("result"), data.get("error") or {}, done)


def missing_message(outcome, what):
    return f"{what} does not exist (the feature is not built): {outcome.error.get('message')}"


def standin(name, **options):
    return {"standin": name, **options}


def read_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def ready_report(verdict="READY"):
    return {"verdict": verdict, "reasons": [] if verdict == "READY" else ["planted: not ready"],
            "repositories": {name: {"failed": None} for name in REPOSITORIES}}


# --------------------------------------------------------------------------
# A kept W2-81 run (G3's input), planted
# --------------------------------------------------------------------------

def make_kept(folder, root, tickets=False, leave_out=None):
    folder.mkdir(parents=True)
    heads = {}
    for index, name in enumerate(REPOSITORIES):
        if name == leave_out:
            continue
        repo = folder / "repos" / name
        repo.mkdir(parents=True)
        git(repo, "init", "-q", "-b", "main")
        git(repo, "config", "user.name", "W2-209 tests")
        git(repo, "config", "user.email", "w2-209@example.invalid")
        heads[name] = commit(repo, {
            ".copier-answers.yml": f"_commit: v{N_VERSION}\n_src_path: {root}\n",
            "governance/framework.lock": f'release:\n  version: "{N_VERSION}"\n',
            "README.md": f"# {name}: a kept proving repository (planted)\n",
            f".tickets/K-{index}.md": ticket(f"K-{index}", "in_progress", f"W9-{index}"),
        }, f"{name} adopted at {N_VERSION}")
        out = folder / "outputs" / name
        out.mkdir(parents=True)
        (out / "adopt.log").write_text(f"{name}: the adoption's log (planted)\n", encoding="utf-8")
        manifests = folder / "manifests"
        manifests.mkdir(exist_ok=True)
        (manifests / f"{name}.json").write_text(json.dumps({"seed": 4242, "head": heads[name]}) + "\n",
                                                encoding="utf-8")
    (folder / "run.json").write_text(json.dumps({"form": "w2-81-run/1", "seed": 4242, "large_size": 4096,
                                                 "manifests": str(folder / "manifests"), "hidden_variants": 0,
                                                 "heads": heads}, indent=2) + "\n", encoding="utf-8")
    if tickets:
        repositories = {name: {"queue": {"run": True, "ticket": f"K-{i}", "exit": 0}}
                        for i, name in enumerate(REPOSITORIES) if name != leave_out}
        (folder / "report.json").write_text(json.dumps({"form": "w2-81-report/1", "verdict": "READY",
                                                        "repositories": repositories}, indent=2) + "\n",
                                            encoding="utf-8")
    return folder
