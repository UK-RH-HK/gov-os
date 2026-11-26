"""Support for the W2-213 slice 1 acceptance tests (SL-1 to SL-14): the planted owned repository, its plans, the
``gov layout check`` runner and the readers of its output.

Public interfaces only: the ``gov`` command line, ``git``, ``gitleaks`` (behind the command), the committed standard
and its schema as files. No module of the layout code is imported.

Every repository is built here, file by file, in a temporary folder, with fixed dates; every name and text is
invented. The hidden-set paths and the secret files are stand-ins of the planted repository; the fake secrets are
assembled from parts at run time and are never written whole in a tracked file of this repository.
"""

from __future__ import annotations

import contextlib
import copy
import ctypes
import hashlib
import json
import os
import re
import shutil
import site
import struct
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

import gov

SRC = Path(gov.__file__).resolve().parents[1]  # the tree under test: <tree>/src, as gov accept's PYTHONPATH names it
TREE = SRC.parent
STANDARD_REL = "template/governance/kernel/standard.yaml"
STANDARD = TREE / STANDARD_REL
SCHEMA = TREE / "template/governance/kernel/schemas/standard.schema.json"
SHIPPED_COPY = SRC / "gov" / "_shipped" / STANDARD_REL
KIT_COPY = "governance/kernel/standard.yaml"
PLAN_USUAL = "governance/adoption/layout-plan.jsonl"
MAP_REL = "governance/project/path-map.yaml"
IMPORTS_REL = "governance/project/imports.yaml"

CLASSES = ("code", "tests", "spec", "research", "docs", "record", "governance", "kit", "config", "data", "generated",
           "archive", "import-use", "import-absorb", "import-study", "evaluation", "hidden-set", "secret")
IMPORT_CLASSES = ("import-use", "import-absorb", "import-study")
FIELDS = ("path", "class", "destination", "reason", "kind", "stale_class", "import", "sign", "ask")
KINDS = ("file", "folder", "untracked", "ignored-root", "submodule", "declared")
GIT_DATE = "2026-11-01T00:00:00+00:00"
OLD_MTIME = 1_600_000_000  # planted files are older than the index, so git never re-reads them to see a change
GITLINK_SHA = "1234567890abcdef1234567890abcdef12345678"
RUN_TIMEOUT_S = 300

# memory policy of each class (rubric section 1; the interface's table)
MEMORY = {"code": "embedded", "tests": "keyword", "spec": "embedded", "research": "embedded", "docs": "embedded",
          "record": "keyword", "governance": "embedded", "kit": "keyword", "config": "keyword", "data": "out",
          "generated": "keyword", "archive": "out", "import-use": "keyword", "import-absorb": "keyword",
          "import-study": "embedded", "evaluation": "out", "hidden-set": "out", "secret": "out"}
POLICIES = {"embedded": ("indexed", "embedded"), "keyword": ("indexed", "not embedded"),
            "out": ("not indexed", "not embedded")}


# --------------------------------------------------------------------------
# Plan lines
# --------------------------------------------------------------------------

def line(path, cls, destination=None, kind="file", *, stale=None, imp=None, sign="path", ask=None, reason=None):
    """One plan line with exactly the nine fields; ``destination`` defaults to the item's own path."""
    return {"path": path, "class": cls, "destination": path if destination is None else destination,
            "reason": reason or f"planted reading of {path}", "kind": kind, "stale_class": stale, "import": imp,
            "sign": sign, "ask": ask}


QUESTION = "Is this note about the oddity still current?"


def _clean_lines():
    own = [
        ("README.md", "docs"), ("CLAUDE.md", "governance"), ("AGENTS.md", "governance"), (".gitignore", "config"),
        (".gitleaks.toml", "config"), ("pyproject.toml", "config"), (".github/workflows/ci.yml", "config"),
        (".claude/settings.json", "config"), (".rulesync/rules/main.md", "governance"),
        (".tickets/PLT-1.md", "governance"), ("openspec/specs/billing/spec.md", "spec"),
        ("src/meadow/__init__.py", "code"), ("src/meadow/core.py", "code"), ("src/meadow/schema.json", "data"),
        ("src/meadow/NOTES.md", "docs"), ("tests/test_core.py", "tests"), ("web/package.json", "config"),
        ("web/app/main.js", "code"), ("web/GUIDE.md", "docs"), ("tools/gen.py", "code"),
        ("config/.env.example", "config"), (KIT_COPY, "kit"), ("governance/kernel/skills/retrieval.md", "kit"),
        ("governance/framework.lock", "kit"), (".copier-answers.yml", "kit"), (MAP_REL, "governance"),
        (IMPORTS_REL, "governance"), ("governance/adoption/A1-inventory.md", "record"),
        ("docs/close/PLT-1.md", "record"), ("docs/guide/setup.md", "docs"), ("docs/guide/ops.md", "docs"),
        ("docs/specs/search.md", "spec"), ("docs/research/old-study/notes.md", "research"),
        ("docs/records/measures/2025-01-05.md", "record"), ("data/prices.csv", "data"),
        ("views/index.generated.md", "generated"), ("eval/visible/cases.jsonl", "evaluation"),
    ]
    lines = [line(path, cls) for path, cls in own]
    lines += [
        line("notes/handbook.md", "docs", "docs/handbook.md"),
        line("design/checkout-spec.md", "spec", "docs/specs/checkout-spec.md", sign="content"),
        line("experiments/cache-study.md", "research", "docs/research/cache-study/cache-study.md"),
        line("reports/audit-2025-03-02.md", "record", "docs/records/audits/audit-2025-03-02.md"),
        line("fixtures/sample-orders.csv", "data", "data/sample-orders.csv"),
        line("seedpack", "data", "data/seedpack", "folder"),
        line("plans/roadmap-2024.md", "archive", "archive/superseded/plans/roadmap-2024.md", stale="superseded",
             sign="front-matter"),
        line("legacy-queue", "archive", "archive/legacy/legacy-queue", "folder", stale="legacy", sign="history"),
        line("journal/2023-retro.md", "archive", "archive/historical/journal/2023-retro.md", stale="historical",
             sign="history"),
        line("archive/old/ancient.md", "archive", "archive/historical/old/ancient.md", stale="historical"),
        line("archive/superseded/docs/prior.md", "archive", stale="superseded"),
        line("misc/oddity.txt", "ask", ask={"question": QUESTION, "recommended": "docs"}),
        line("vendor/jsonlib", "import-use", "imports/jsonlib", "folder", imp="jsonlib", sign="licence"),
        line("borrowed/ratelimit/README.md", "import-absorb", "imports/ratelimit/README.md", imp="ratelimit"),
        line("borrowed/ratelimit/limit.py", "import-absorb", "imports/ratelimit/limit.py", imp="ratelimit"),
        line("borrowed/ratelimit/sub/x.py", "import-absorb", "imports/ratelimit/sub/x.py", imp="ratelimit"),
        line("study/notebook", "import-study", "imports/notebook", "folder", imp="notebook", sign="content"),
        line("study/bigbook", "import-study", "imports/bigbook", "folder", imp="bigbook", sign="content"),
        line("external/widgets", "import-use", "imports/widgets", "submodule", imp="widgets", sign="manifest"),
        line("todo.md", "docs", "docs/todo.md", "untracked"),
        line("scratch-notes", "data", "data/scratch-notes", "untracked"),
        line(".env", "secret", kind="ignored-root"),
        line("node_modules", "generated", kind="ignored-root"),
        line("build", "generated", kind="ignored-root"),
        line("src/meadow/__pycache__", "generated", kind="ignored-root"),
        line("../solar-sketch", "import-use", kind="declared", imp="solar", sign="registry"),
    ]
    return lines


_CLEAN = _clean_lines()


def clean_lines():
    return copy.deepcopy(_CLEAN)


def by_path(lines, path):
    found = [item for item in lines if item.get("path") == path]
    assert len(found) == 1, f"fixture: {len(found)} plan lines name {path}"
    return found[0]


def without(lines, *paths):
    for path in paths:
        by_path(lines, path)
    return [item for item in lines if item["path"] not in paths]


def write_plan(destination, lines, blank_before=()):
    """The plan written as JSON Lines; ``blank_before``: indexes before which a blank line stands. Returns the plan's
    path and ``{index in lines: line number in the file}``."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    text, numbers = [], {}
    for index, item in enumerate(lines):
        if index in blank_before:
            text.append("")
        text.append(item if isinstance(item, str) else json.dumps(item))
        numbers[index] = len(text)
    destination.write_text("".join(f"{row}\n" for row in text), encoding="utf-8")
    return destination, numbers


# --------------------------------------------------------------------------
# The planted repository
# --------------------------------------------------------------------------

def sections(count, label):
    """A Markdown text of ``count`` short sections: the indexer's chunker makes one chunk of each."""
    return "".join(f"## {label} section {n:05d}\nentry {n}\n" for n in range(1, count + 1))


PATH_MAP = """\
state_class: AUTHORITATIVE
# history: plans/roadmap-2024.md was last year's plan
namespaces:
  kernel:
    paths: ["governance/kernel/**"]
  project:
    paths: ["governance/project/**"]
evaluation_sets:
  orders-eval:
    visible: ["eval/visible/**"]
    hidden: ["eval/hidden/**"]
    measures:
      roles: [engineer]
sets_root_hidden:
  root: "~/planted-sets-root"
  hidden: ["vault-sets/**"]
  refused_roles: [engineer]
"""

IMPORTS = """\
imports:
  - name: solar
    path: ../solar-sketch
    class: use
"""


def tracked_files():
    standard = STANDARD.read_text(encoding="utf-8") if STANDARD.is_file() else "# the standard is not built yet\n"
    gitleaks = (TREE / "template/.gitleaks.toml").read_text(encoding="utf-8")
    return {
        "README.md": "# Meadow\n\nAn invented product for the layout tests.\n",
        "CLAUDE.md": "# Rules\n\nWork carefully.\n",
        "AGENTS.md": "# Agents\n\nWork carefully.\n",
        ".gitignore": ".env\nid_rsa\nnode_modules/\n__pycache__/\nbuild/\n",
        ".gitleaks.toml": gitleaks,
        "pyproject.toml": '[project]\nname = "meadow"\nversion = "1.0.0"\n',
        ".github/workflows/ci.yml": ("# open items: reports/audit-2025-03-02.md\nname: ci\non: push\njobs:\n"
                                     "  gen:\n    runs-on: ubuntu-latest\n    steps:\n"
                                     "      - run: python tools/gen.py seedpack/regions.csv\n"),
        ".claude/settings.json": "{}\n",
        ".rulesync/rules/main.md": "# Rule\n\nKeep tests green.\n",
        ".tickets/PLT-1.md": "---\nid: PLT-1\nstatus: closed\n---\n# Planted ticket\n",
        "openspec/specs/billing/spec.md": "# Billing\n\nGoals and KPIs of billing.\n",
        "src/meadow/__init__.py": '"""Meadow."""\n',
        "src/meadow/core.py": ('"""Meadow core."""\n# method: experiments/cache-study.md\n'
                               "# open items: reports/audit-2025-03-02.md\n\n\n"
                               "def total(rows):\n    return sum(rows)\n"),
        "src/meadow/schema.json": '{"type": "object"}\n',
        "src/meadow/NOTES.md": "# Module notes\n",
        "tests/test_core.py": ('ORDERS = "fixtures/sample-orders.csv"\n\n\ndef test_orders():\n'
                               "    assert ORDERS\n"),
        "web/package.json": '{"name": "meadow-web", "version": "1.0.0"}\n',
        "web/app/main.js": "export const main = () => 1;\n",
        "web/GUIDE.md": "# Web guide\n",
        "tools/gen.py": '"""Writes the generated index."""\n',
        "config/.env.example": "MEADOW_PORT=8000\n",
        KIT_COPY: standard,
        "governance/kernel/skills/retrieval.md": "# Retrieval\n\nExample question: design/checkout-spec.md\n",
        "governance/framework.lock": "manifest: {}\n",
        ".copier-answers.yml": "_commit: v0.0.0\n",
        MAP_REL: PATH_MAP,
        IMPORTS_REL: IMPORTS,
        "governance/adoption/A1-inventory.md": "# Inventory record 2025-02-01\n",
        "docs/close/PLT-1.md": "# Close of PLT-1\n\nTouched notes/handbook.md.\n",
        "docs/guide/setup.md": ("---\nrelated: design/checkout-spec.md\n---\n# Setup\n\n"
                                "Read the [handbook](../../notes/handbook.md) first.\n\n"
                                "The old plan is in plans/roadmap-2024.md.\n\n"
                                "The [last audit](../../reports/audit-2025-03-02.md) is kept.\n"),
        "docs/guide/ops.md": "---\nsource: reports/audit-2025-03-02.md\n---\n# Operations\n\nDaily steps.\n",
        "docs/specs/search.md": "# Search spec\n",
        "docs/research/old-study/notes.md": "# Old study notes\n",
        "docs/records/measures/2025-01-05.md": "# Measure of 2025-01-05\n",
        "data/prices.csv": "item,price\nrake,3\n",
        "notes/handbook.md": "# Handbook\n\nStart with the [setup guide](../docs/guide/setup.md).\n",
        "design/checkout-spec.md": "# Checkout spec\n\nProblem, goals, KPIs.\n",
        "experiments/cache-study.md": "# Cache study\n\nWe measured twice.\n",
        "reports/audit-2025-03-02.md": ("# Audit of 2025-03-02\n\n"
                                        "Follow-up: [operations](../docs/guide/ops.md).\n"),
        "fixtures/sample-orders.csv": "order,qty\n1,2\n",
        "seedpack/regions.csv": "region\nnorth\n",
        "seedpack/units.csv": "unit\nbox\n",
        "views/index.generated.md": ("<!-- Generated by tools/gen.py -->\n# Index\n\n"
                                     "design/checkout-spec.md\n"),
        "plans/roadmap-2024.md": "---\nstatus: SUPERSEDED\n---\n# Roadmap 2024\n",
        "legacy-queue/worker.py": '"""The retired queue."""\n',
        "legacy-queue/README.md": "# The retired queue\n",
        "journal/2023-retro.md": "# Retrospective 2023\n",
        "archive/old/ancient.md": "# Ancient notes\n",
        "archive/superseded/docs/prior.md": "# Prior text\n",
        "misc/oddity.txt": "an odd note\n",
        "eval/visible/cases.jsonl": '{"case": 1}\n',
        "vendor/jsonlib/LICENSE": "Copyright the invented jsonlib authors. MIT.\n",
        "vendor/jsonlib/README.md": "# jsonlib\n\nOnce compared with notes/handbook.md.\n",
        "vendor/jsonlib/jsonlib.py": '"""jsonlib, vendored."""\n',
        "borrowed/ratelimit/README.md": "# ratelimit\n\nBrought in to assess.\n",
        "borrowed/ratelimit/limit.py": '"""ratelimit."""\n',
        "borrowed/ratelimit/sub/x.py": '"""ratelimit helper."""\n',
        "study/notebook/p1.md": "## first\nentry\n## second\nentry\n",
        "study/notebook/p2.md": "## third\nentry\n",
        "study/notebook/figure.bin": b"\x00\x01\x02\x00figure\x00",
        "study/bigbook/volume.md": sections(2001, "volume"),
    }


UNTRACKED = {"todo.md": "# Things to do\n", "scratch-notes/a.txt": "alpha\n", "scratch-notes/b.txt": "beta\n"}


def ignored_files():
    return {".env": "MEADOW_TOKEN=" + fake_token() + "\n" + SENTINELS[".env"] + "\n",
            "node_modules/lib/index.js": "module.exports = 1;\n", "build/out.txt": "built\n",
            "src/meadow/__pycache__/core.cpython.pyc": b"\x00pyc\x00"}


IGNORED_ROOTS = [".env", "build", "node_modules", "src/meadow/__pycache__"]


# fake secrets and sentinels, assembled at run time -----------------------------------------------

def fake_token():
    return "sk" + "-" + "4" + "Qa7Zr2Lm9" * 3


def fake_canary():
    return "ORDERS_" + "CAN" + "ARY_" + "9f3kq"


SENTINELS = {rel: f"zz-sentinel-{number}-" + hashlib.sha256(rel.encode()).hexdigest()[:20]
             for number, rel in enumerate((".env", "eval/hidden/answers.txt", "vault-sets/q1.txt",
                                           "eval/hidden/more.txt", "deploy/server.pem", "id_rsa",
                                           "notes/ops-handover.txt", "notes/vault-login.txt"))}


# git and files -----------------------------------------------------------------------------------

def git_env():
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_AUTHOR_DATE=GIT_DATE, GIT_COMMITTER_DATE=GIT_DATE, GIT_CONFIG_NOSYSTEM="1",
               GIT_CONFIG_GLOBAL=os.devnull, LC_ALL="C.UTF-8")
    return env


def git(root, *args):
    done = subprocess.run(["git", "-c", "user.name=planted", "-c", "user.email=planted@example.invalid",
                           "-c", "commit.gpgsign=false", *args], cwd=root, env=git_env(), capture_output=True,
                          text=True, timeout=120)
    assert done.returncode == 0, f"fixture: git {' '.join(args)} failed in {root}\n{done.stdout}\n{done.stderr}"
    return done.stdout


def head(root):
    return git(root, "rev-parse", "HEAD").strip()


def write(root, rel, content):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
    os.utime(path, (OLD_MTIME, OLD_MTIME))
    return path


def commit(root, message="planted"):
    git(root, "commit", "-q", "--allow-empty", "--no-verify", "-m", message)


def add_commit(root, files, message="planted more"):
    """``files`` written, added by name (ignored or not) and committed."""
    for rel, content in files.items():
        write(root, rel, content)
    if files:
        git(root, "add", "-f", "--", *files)
    commit(root, message)


def build_repository(root):
    root = Path(root)
    root.mkdir(parents=True)
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "core.trustctime", "false")
    git(root, "config", "core.checkStat", "minimal")
    for rel, content in tracked_files().items():
        write(root, rel, content)
    git(root, "add", "-A")
    git(root, "update-index", "--add", "--cacheinfo", f"160000,{GITLINK_SHA},external/widgets")
    (root / "external/widgets").mkdir(parents=True)
    commit(root)
    for rel, content in {**UNTRACKED, **ignored_files()}.items():
        write(root, rel, content)
    return root


def copy_repository(origin, destination):
    """A copy of a planted repository (temporary only), its index refreshed."""
    shutil.copytree(origin, destination, symlinks=True)
    git(destination, "update-index", "-q", "--refresh")
    return Path(destination)


def listed(root, *args):
    return sorted(item for item in git(root, "ls-files", "-z", *args).split("\0") if item)


def items_of(root):
    """Every item of the spec's "what is classed", read from the planted repository itself."""
    tracked = listed(root)
    untracked = listed(root, "--others", "--exclude-standard")
    ignored = [item.rstrip("/") for item in
               listed(root, "--others", "--ignored", "--exclude-standard", "--directory")]
    return sorted(tracked + untracked + ignored + ["../solar-sketch"])


def covered(item_line, items):
    """The items a plan line covers: its own path, and for a folder or untracked line everything below it."""
    path = item_line["path"]
    below = [i for i in items if item_line["kind"] in ("folder", "untracked") and i.startswith(path + "/")]
    return ([path] if path in items else []) + below


def snapshot(root):
    """Everything a run must leave alone: every file outside ``.git``, HEAD, the refs, the objects and the status."""
    root = Path(root)
    files = {}
    for folder, names, plain in os.walk(root):
        names[:] = [n for n in names if not (Path(folder) == root and n == ".git")]
        for name in names + plain:
            path = Path(folder) / name
            rel = path.relative_to(root).as_posix()
            info = path.lstat()
            digest = None
            if path.is_file() and not path.is_symlink() and os.access(path, os.R_OK):
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
            files[rel] = (digest, info.st_mode, None if path.is_dir() else info.st_size)
    state = {"files": files}
    if (root / ".git").exists():
        state.update(head=head(root), refs=git(root, "for-each-ref"), objects=git(root, "count-objects", "-v"),
                     staged=git(root, "ls-files", "-s"))
    return state


def assert_unchanged(before, after):
    changed = sorted(rel for rel in set(before["files"]) | set(after["files"])
                     if before["files"].get(rel) != after["files"].get(rel))
    changed += [key for key in before if key != "files" and before[key] != after[key]]
    assert not changed, f"the check changed the repository: {changed[:30]}"


# --------------------------------------------------------------------------
# Running the check
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Run:
    argv: tuple
    returncode: int
    stdout: str
    stderr: str
    sandbox: Path

    def describe(self):
        return (f"{' '.join(self.argv)}\nexit code: {self.returncode}\nstdout:\n{self.stdout[:6000]}\n"
                f"stderr:\n{self.stderr[-3000:]}")

    def envelope(self):
        try:
            data = json.loads(self.stdout)
        except ValueError:
            raise AssertionError(f"standard output is not one JSON document\n{self.describe()}") from None
        assert isinstance(data, dict), f"standard output is not a JSON object\n{self.describe()}"
        return data


def environment(sandbox, src):
    gitleaks = shutil.which("gitleaks") or str(Path.home() / ".local/bin/gitleaks")
    assert Path(gitleaks).exists(), "gitleaks is not on PATH: the secrets filter these tests need is not there"
    return {"PATH": os.pathsep.join([str(Path(gitleaks).parent), os.environ.get("PATH", "/usr/bin:/bin")]),
            "HOME": str(sandbox / "home"), "TMPDIR": str(sandbox / "tmp"), "LC_ALL": "C.UTF-8",
            "PYTHONPATH": str(src), "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONUSERBASE": os.environ.get("PYTHONUSERBASE") or site.getuserbase(),
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}


def run_check(work, root, plan, *extra, src=SRC, json_form=True):
    """``gov layout check <plan> --root <root> [extra] [--json]`` as a child process from an empty folder, with a fresh
    HOME and TMPDIR under ``work``."""
    sandbox = Path(work) / f"run-{len(list(Path(work).glob('run-*')))}"
    for name in ("home", "tmp", "elsewhere"):
        (sandbox / name).mkdir(parents=True)
    argv = [sys.executable, "-B", "-m", "gov.cli.main", "layout", "check", str(plan), "--root", str(root), *extra]
    if json_form:
        argv.append("--json")
    env = environment(sandbox, src)
    env["GIT_CEILING_DIRECTORIES"] = str(Path(root).parent)
    try:
        done = subprocess.run(argv, cwd=sandbox / "elsewhere", env=env, capture_output=True, text=True,
                              timeout=RUN_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"the check did not end within {RUN_TIMEOUT_S} s: {argv}") from None
    return Run(tuple(argv), done.returncode, done.stdout, done.stderr, sandbox)


def check_lines(work, root, lines, *extra, **kwargs):
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    plan, numbers = write_plan(work / f"plan-{len(list(work.glob('plan-*')))}.jsonl", lines,
                               kwargs.pop("blank_before", ()))
    return run_check(work, root, plan, *extra, **kwargs), numbers


def result_of(run, code):
    """The ``result`` of a check that ran: exit ``code`` (0 clean, 1 findings or stoppers)."""
    assert run.returncode == code, f"expected exit {code}\n{run.describe()}"
    data = run.envelope()
    assert data.get("ok") is True and data.get("command") == "layout" and "session" in data, (
        f"not the envelope of a layout check that ran\n{run.describe()}")
    result = data.get("result")
    assert isinstance(result, dict), f"the envelope has no result\n{run.describe()}"
    for key in ("findings", "stoppers", "rewrites", "held", "kept", "asks", "counts", "commit", "standard", "hash",
                "namespaces", "imports"):
        assert key in result, f"the result has no `{key}`\n{run.describe()}"
    return result


def assert_clean(run):
    result = result_of(run, 0)
    assert result["findings"] == [] and result["stoppers"] == [], f"a clean plan has findings\n{run.describe()}"
    return result


def assert_cannot_run(run):
    assert run.returncode == 2, f"expected exit 2 (cannot run)\n{run.describe()}"
    data = run.envelope()
    error = data.get("error")
    assert data.get("ok") is False and data.get("command") == "layout" and isinstance(error, dict), (
        f"not an error envelope of the layout check\n{run.describe()}")
    assert error.get("code") == "LAYOUT_CANNOT_RUN", f"the error code is not LAYOUT_CANNOT_RUN\n{run.describe()}"
    return error


def findings(result, code=None):
    return [f for f in result["findings"] if code is None or f.get("code") == code]


def text_of(finding):
    return " ".join(str(finding.get(key) or "") for key in ("path", "other", "message"))


def one_finding(result, code, *, line=None, path=None, names=()):
    """At least one finding of ``code`` (on plan line ``line``, with ``path``, naming each of ``names``)."""
    found = [f for f in findings(result, code)
             if (line is None or f.get("line") == line) and (path is None or f.get("path") == path)
             and all(name in text_of(f) for name in names)]
    assert found, (f"no {code} (line {line}, path {path}, naming {list(names)}) among:\n"
                   f"{json.dumps(result['findings'][:60], indent=1)}")
    return found[0]


# --------------------------------------------------------------------------
# Opened files (inotify)
# --------------------------------------------------------------------------

@contextlib.contextmanager
def watched(paths):
    """Yields a function giving which of ``paths`` any process opened since the watch began."""
    libc = ctypes.CDLL(None, use_errno=True)
    handle = libc.inotify_init1(os.O_NONBLOCK)
    assert handle >= 0, "fixture: inotify is not available"
    names = {}
    try:
        for path in paths:
            watch = libc.inotify_add_watch(handle, os.fsencode(str(path)), 0x00000020 | 0x00000001)  # open, access
            assert watch >= 0, f"fixture: cannot watch {path}"
            names[watch] = str(path)
        seen = set()

        def opened():
            while True:
                try:
                    data = os.read(handle, 65536)
                except BlockingIOError:
                    return sorted(seen)
                offset = 0
                while offset < len(data):
                    watch, _mask, _cookie, length = struct.unpack_from("iIII", data, offset)
                    seen.add(names.get(watch, str(watch)))
                    offset += 16 + length

        yield opened
    finally:
        os.close(handle)


# --------------------------------------------------------------------------
# Globs of the path map's language
# --------------------------------------------------------------------------

def matches(path, pattern):
    """``*`` stays inside one folder, ``**`` crosses folders."""
    regex = "".join(".*" if part == "**" else "[^/]*" if part == "*" else re.escape(part)
                    for part in re.split(r"(\*\*|\*)", pattern))
    return re.fullmatch(regex, path) is not None


def load_yaml(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# The dirty repository: stoppers
# --------------------------------------------------------------------------

def dirty_tracked():
    return {
        "eval/hidden/answers.txt": SENTINELS["eval/hidden/answers.txt"] + "\nsee notes/handbook.md\n",
        "vault-sets/q1.txt": SENTINELS["vault-sets/q1.txt"] + "\nsee plans/roadmap-2024.md\n",
        "deploy/server.pem": SENTINELS["deploy/server.pem"] + "\nsee design/checkout-spec.md\n",
        "notes/ops-handover.txt": ("Handover note.\n" + SENTINELS["notes/ops-handover.txt"] + "\nmarker "
                                   + fake_canary() + "\n"),
        "notes/vault-login.txt": SENTINELS["notes/vault-login.txt"] + "\n",
    }


def dirty_other():
    return {"eval/hidden/more.txt": SENTINELS["eval/hidden/more.txt"] + "\nsee notes/handbook.md\n",
            "id_rsa": SENTINELS["id_rsa"] + "\n"}


NEVER_OPENED = ("eval/hidden/answers.txt", "vault-sets/q1.txt", "eval/hidden/more.txt", "deploy/server.pem", ".env",
                "id_rsa")
TRACKED_STOPPERS = ("eval/hidden/answers.txt", "vault-sets/q1.txt", "deploy/server.pem", "notes/ops-handover.txt",
                    "notes/vault-login.txt")


def dirty_lines():
    return clean_lines() + [
        line("eval/hidden/answers.txt", "hidden-set", sign="registry"),
        line("vault-sets/q1.txt", "hidden-set", sign="registry"),
        line("eval/hidden/more.txt", "hidden-set", kind="untracked", sign="registry"),
        line("deploy/server.pem", "secret"),
        line("id_rsa", "secret", kind="ignored-root"),
        line("notes/ops-handover.txt", "docs", "docs/ops-handover.txt"),
        line("notes/vault-login.txt", "secret", sign="content"),
    ]


def build_dirty(clean_root, destination):
    root = copy_repository(clean_root, destination)
    add_commit(root, dirty_tracked(), "planted: hidden-set and secret files in the tree")
    for rel, content in dirty_other().items():
        write(root, rel, content)
    return root


# --------------------------------------------------------------------------
# The correctly moved repository (SL-14)
# --------------------------------------------------------------------------

HELD_ITEMS = ("experiments/cache-study.md", "reports/audit-2025-03-02.md", "fixtures/sample-orders.csv", "seedpack")

REWRITTEN = {
    "docs/guide/setup.md": ("---\nrelated: docs/specs/checkout-spec.md\n---\n# Setup\n\n"
                            "Read the [handbook](../handbook.md) first.\n\n"
                            "The old plan is in archive/superseded/plans/roadmap-2024.md.\n\n"
                            "The [last audit](../../reports/audit-2025-03-02.md) is kept.\n"),
    "docs/handbook.md": "# Handbook\n\nStart with the [setup guide](guide/setup.md).\n",
}


def moved_path(item_line, path):
    """Where ``path``, covered by ``item_line``, lies after the moves (a held item stays)."""
    if item_line["path"] in HELD_ITEMS:
        return path
    return item_line["destination"] + path[len(item_line["path"]):]


def namespace_of(item_line):
    """The moved map's namespace for a plan line."""
    cls = item_line["class"]
    if cls == "ask":
        return "unsure"
    if cls == "archive":
        return f"archive-{item_line['stale_class']}"
    if cls in IMPORT_CLASSES:
        return f"import-{item_line['import']}"
    return cls


def build_moved(clean_root, destination):
    """The hand restructure of the clean plan: every moving item that is not held moved, the listed references
    rewritten, the path map written from the standard, all committed."""
    root = copy_repository(clean_root, destination)
    items = listed(root)
    placed = {}  # each path's namespace, by where it lies after the moves
    for item_line in clean_lines():
        if item_line["kind"] != "declared":
            for item in covered(item_line, items):
                placed[moved_path(item_line, item)] = namespace_of(item_line)
        old, new = item_line["path"], item_line["destination"]
        if old == new or old in HELD_ITEMS or item_line["kind"] == "declared":
            continue
        (root / new).parent.mkdir(parents=True, exist_ok=True)
        if item_line["kind"] == "submodule":
            git(root, "update-index", "--force-remove", old)
            (root / old).rename(root / new)
            (root / old).parent.rmdir()
            git(root, "update-index", "--add", "--cacheinfo", f"160000,{GITLINK_SHA},{new}")
        elif item_line["kind"] == "untracked":
            (root / old).rename(root / new)
        else:
            git(root, "mv", old, new)
    for rel, text in REWRITTEN.items():
        write(root, rel, text)
    write(root, MAP_REL, moved_map(placed, set(listed(root))))
    git(root, "add", "--", MAP_REL, *REWRITTEN)
    commit(root, "planted: the restructure")
    return root


def moved_map(placed, tracked):
    """The repository's own path map after the moves: each tracked path in one namespace, listed by name, with the
    class's policies; ``placed`` is ``{path: namespace name}``."""
    missing = sorted(tracked - set(placed))
    assert not missing, f"fixture: tracked paths of the moved repository with no namespace: {missing}"
    spaces = {}
    for path in sorted(tracked):
        spaces.setdefault(placed[path], []).append(path)
    document = yaml.safe_load(PATH_MAP)
    document["namespaces"] = {name: namespace_entry(name, paths) for name, paths in sorted(spaces.items())}
    return yaml.safe_dump(document, sort_keys=False)


def namespace_entry(name, paths):
    """A namespace of the moved map: ``unsure`` holds the ask item (any policy), ``import-bigbook`` is the study
    import over the ceiling."""
    if name == "unsure":
        policy = "embedded"
    elif name.startswith("archive-"):
        policy = "out"
    elif name == "import-notebook":
        policy = "embedded"
    elif name.startswith("import-"):
        policy = "keyword"
    else:
        policy = MEMORY[name]
    lexical, embedding = POLICIES[policy]
    entry = {"paths": sorted(paths), "memory_class": "governance", "sensitivity": "internal",
             "permitted_roles": ["engineer"], "retention": "kept in git history", "export_policy": "allowed",
             "embedding_policy": embedding, "provenance": "planted", "deletion_rebuild": "restored from git"}
    if lexical == "not indexed":
        entry["lexical_policy"] = lexical  # absent is indexed
    if name.startswith("archive-"):
        entry["stale_class"] = name.removeprefix("archive-")
    return entry
