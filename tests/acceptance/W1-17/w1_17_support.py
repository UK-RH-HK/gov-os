"""Support code for the W1-17 acceptance tests (standard library and PyYAML only).

W1-17 ports the carried FTS5 index and chunking into ``src/gov/retrieval/`` and
registers the index-freshness family check. No ``gov`` command belongs to this
ticket (``src/gov/cli/**`` is outside its paths), so the tests use the Python
interface the README states, all of it in ``gov.retrieval.lexical``:

- ``refresh(root)``, ``search(root, query, refresh=True)``, ``freshness(root)``,
  ``digest(root)``, ``chunks(root, path=None)`` and ``parent(root, parent_id)``;
- ``gov check --list --json`` and the ``command`` of the listed check.

How the tests call it:

- **Every call runs in a new Python process**, through a small driver written to
  a temporary directory, with this worktree's ``src/`` on ``PYTHONPATH``.
- **No index is built in this worktree** (DEC-322). Every project is a temporary
  git repository with its own path map, its own ``.gitleaks.toml`` and its own
  ``.gov-runtime/store.db``.
- **The environment is built from scratch:** ``PATH`` (git and gitleaks are found
  through it), an empty temporary ``HOME``, ``TMPDIR``, locale, ``PYTHONPATH`` and
  ``PYTHONPYCACHEPREFIX``. ``GOV_ROLE`` and ``GOV_TICKET`` are not passed on.
- **No secret is committed.** Every planted string is built at run time from
  parts and written only into a temporary directory.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
MODULE = "gov.retrieval.lexical"
FUNCTIONS = ("refresh", "search", "freshness", "digest", "chunks", "parent")
STORE_MODULE = "gov.store"
STORE_REL = ".gov-runtime/store.db"
RUNTIME_REL = ".gov-runtime"
PATH_MAP_REL = "governance/project/path-map.yaml"
CONFIG_REL = ".gitleaks.toml"
TEMPLATE_CONFIG_REL = "template/.gitleaks.toml"
PYPROJECT_REL = "pyproject.toml"
CHECKS_REL = "template/governance/kernel/checks"
CHECK_GLOB = "index-freshness*.yaml"
CHECK_FIELDS = ("id", "family", "tier", "severity", "command")
FAMILY = "index freshness"

FACET = "lexical"
UNAVAILABLE = "FACET_UNAVAILABLE"
CALL_TIMEOUT_S = 300.0
MISSING_EXIT = 3

DEV_TIERS = Path(os.environ.get("GOV_DEV_TIERS") or "~/gov-os-workbench/synthetic").expanduser()
DEV_TIER = "a-dev"
# "2.8 s scale on a-dev": the bound is generous on purpose (README, package DP-3); only the one call is timed.
REINDEX_LIMIT_S = 10.0

_DRIVER = '''\
import importlib, json, sys, time
from pathlib import Path

out = []
for call in json.loads(sys.stdin.read()):
    try:
        function = getattr(importlib.import_module(call["module"]), call["function"])
    except ModuleNotFoundError as exc:
        if exc.name not in ("gov.retrieval", "gov.retrieval.lexical"):
            raise
        print(f"no module {exc.name}", file=sys.stderr)
        sys.exit(3)
    except AttributeError:
        print(f"{call['module']} has no function {call['function']}", file=sys.stderr)
        sys.exit(3)
    started = time.perf_counter()
    value = function(Path(call["root"]), *call["args"], **call["kwargs"])
    out.append({"value": value, "seconds": time.perf_counter() - started})
print(json.dumps(out))
'''


class Missing(AssertionError):
    """Something the ticket builds does not exist yet."""


# --------------------------------------------------------------------------
# Calling the public interface
# --------------------------------------------------------------------------

class Api:
    """Calls ``gov.retrieval.lexical`` of this worktree, each batch in a new process."""

    def __init__(self, workdir):
        self.workdir = Path(workdir)
        for name in ("home", "tmp", "pycache", "elsewhere"):
            (self.workdir / name).mkdir(parents=True, exist_ok=True)
        self.driver = self.workdir / "driver.py"
        self.driver.write_text(_DRIVER, encoding="utf-8")

    def env(self, **extra):
        return {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(self.workdir / "home"),
            "TMPDIR": str(self.workdir / "tmp"),
            "LC_ALL": "C.UTF-8",
            "GIT_CONFIG_NOSYSTEM": "1",
            "PYTHONPATH": str(SRC),
            "PYTHONPYCACHEPREFIX": str(self.workdir / "pycache"),
            **extra,
        }

    def batch(self, calls, **env):
        """Run ``[(module, function, root, args, kwargs), ...]`` in one process; ``[(value, seconds), ...]``.

        The working directory is not the project: every function is given ``root``.
        """
        request = [{"module": module, "function": function, "root": str(root), "args": list(args), "kwargs": kwargs}
                   for module, function, root, args, kwargs in calls]
        what = ", ".join(f"{module}.{function}" for module, function, *_ in calls)
        try:
            done = subprocess.run([sys.executable, str(self.driver)], input=json.dumps(request), env=self.env(**env),
                                  cwd=str(self.workdir / "elsewhere"), capture_output=True, text=True,
                                  timeout=CALL_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"{what} did not end within {CALL_TIMEOUT_S:.0f} s") from None
        if done.returncode == MISSING_EXIT:
            raise Missing(f"the lexical index does not exist: {done.stderr.strip()} under src/")
        assert done.returncode == 0, f"{what} failed (exit code {done.returncode}):\n{done.stderr}"
        try:
            answers = json.loads(done.stdout)
        except ValueError:
            raise AssertionError(f"{what} did not return JSON values:\n{done.stdout}\n{done.stderr}") from None
        return [(answer["value"], answer["seconds"]) for answer in answers]

    def call(self, function, root, *args, module=MODULE, env=None, **kwargs):
        return self.batch([(module, function, root, args, kwargs)], **(env or {}))[0][0]

    def exists(self):
        """Raise Missing unless every function of the public interface can be imported."""
        source = "import importlib\n" + "".join(
            f"getattr(importlib.import_module({MODULE!r}), {name!r})\n" for name in FUNCTIONS)
        done = subprocess.run([sys.executable, "-c", source], capture_output=True, text=True,
                              cwd=str(self.workdir / "elsewhere"), env=self.env())
        if done.returncode != 0:
            last = done.stderr.strip().splitlines()[-1] if done.stderr.strip() else "import failed"
            raise Missing(f"the lexical index does not exist: {last}")

    # ---- gov.retrieval.lexical

    def refresh(self, root, **env):
        """``refresh(root)``: the report, checked for the two keys the interface fixes."""
        report = self.call("refresh", root, env=env)
        return check_report(report)

    def search(self, root, query, **kwargs):
        return check_answer(self.call("search", root, query, **kwargs), query)

    def timed_search(self, root, query):
        answer, seconds = self.batch([(MODULE, "search", root, (query,), {})])[0]
        return check_answer(answer, query), seconds

    def freshness(self, root):
        state = self.call("freshness", root)
        assert isinstance(state, dict), f"freshness did not return a map: {state!r}"
        assert state.get("status") in ("fresh", "stale", "empty", "missing"), \
            f"freshness' `status` is not fresh, stale, empty or missing: {state!r}"
        assert isinstance(state.get("stale"), list), f"freshness' `stale` is not a list of paths: {state!r}"
        return state

    def digest(self, root, **env):
        value = self.call("digest", root, env=env)
        assert is_digest(value), f"digest is not a sha256 in hex: {value!r}"
        return value

    def chunks(self, root, **kwargs):
        records = self.call("chunks", root, **kwargs)
        assert isinstance(records, list), f"chunks did not return a list: {records!r}"
        for record in records:
            assert isinstance(record, dict), f"a chunk record is not a map: {record!r}"
            for key in ("chunk_id", "path", "parent_id"):
                assert isinstance(record.get(key), str) and record[key], f"a chunk record has no {key}: {record!r}"
            for key in ("start_line", "end_line"):
                assert isinstance(record.get(key), int), f"a chunk record's {key} is not a line number: {record!r}"
            assert 1 <= record["start_line"] <= record["end_line"], f"a chunk's lines are not a span: {record!r}"
        return records

    def parents(self, root, parent_ids):
        """``parent(root, parent_id)`` for each id, in one process: ``parent_id -> parent``."""
        ids = sorted(set(parent_ids))
        values = self.batch([(MODULE, "parent", root, (parent_id,), {}) for parent_id in ids])
        found = {}
        for parent_id, (value, _) in zip(ids, values):
            assert isinstance(value, dict), f"parent({parent_id!r}) did not return a map: {value!r}"
            assert value.get("parent_id") == parent_id, f"parent({parent_id!r}) names another parent: {value!r}"
            assert isinstance(value.get("path"), str) and value["path"], f"a parent has no path: {value!r}"
            assert isinstance(value.get("kind"), str) and value["kind"], f"a parent has no kind: {value!r}"
            assert isinstance(value.get("start_line"), int) and isinstance(value.get("end_line"), int), \
                f"a parent has no span of lines: {value!r}"
            found[parent_id] = value
        return found

    def parent(self, root, parent_id):
        return self.parents(root, [parent_id])[parent_id]

    # ---- gov.store (W1-10), the store the index shares

    def store(self, function, root):
        return self.call(function, root, module=STORE_MODULE)


def is_digest(value):
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def check_report(report):
    assert isinstance(report, dict), f"refresh did not return a map: {report!r}"
    assert is_digest(report.get("digest")), f"refresh's `digest` is not a sha256 in hex: {report.get('digest')!r}"
    indexed = report.get("indexed")
    assert isinstance(indexed, list) and all(isinstance(rel, str) for rel in indexed), \
        f"refresh's `indexed` is not a list of paths: {indexed!r}"
    assert len(set(indexed)) == len(indexed), f"refresh's `indexed` names a path twice: {indexed!r}"
    return report


def check_answer(answer, query):
    """The shape of a ``search`` answer (README): an unavailable facet says so and carries no hit."""
    assert isinstance(answer, dict), f"search did not return a map: {answer!r}"
    assert isinstance(answer.get("available"), bool), f"search's `available` is not true or false: {answer!r}"
    assert answer.get("facet") == FACET, f"search's `facet` is not {FACET!r}: {answer!r}"
    hits = answer.get("hits")
    assert isinstance(hits, list), f"search's `hits` is not a list: {answer!r}"
    if not answer["available"]:
        assert answer.get("state") == UNAVAILABLE, f"an unavailable facet does not say {UNAVAILABLE}: {answer!r}"
        assert isinstance(answer.get("reason"), str) and answer["reason"], f"no reason is given: {answer!r}"
        assert hits == [], f"an unavailable facet returned hits for {query!r}: {answer!r}"
        return answer
    assert answer.get("state") != UNAVAILABLE, f"an available facet says {UNAVAILABLE}: {answer!r}"
    for hit in hits:
        assert isinstance(hit, dict), f"a hit is not a map: {hit!r}"
        assert isinstance(hit.get("path"), str) and hit["path"], f"a hit has no file path: {hit!r}"
        assert isinstance(hit.get("line"), int) and hit["line"] >= 1, f"a hit has no line number: {hit!r}"
        assert isinstance(hit.get("text"), str), f"a hit has no text: {hit!r}"
        for key in ("chunk_id", "parent_id"):
            assert isinstance(hit.get(key), str) and hit[key], f"a hit has no {key}: {hit!r}"
    return answer


def places(answer):
    """``[(path, line), ...]`` of an available answer, sorted; each occurrence is reported once."""
    assert answer["available"], f"the lexical facet is unavailable: {answer!r}"
    found = [(hit["path"], hit["line"]) for hit in answer["hits"]]
    assert len(set(found)) == len(found), f"an occurrence is reported twice: {sorted(found)}"
    return sorted(found)


def unavailable(answer, *reasons):
    """Assert that ``answer`` reports the facet unavailable for one of ``reasons``."""
    assert answer["available"] is False, f"the answer is given as available: {answer!r}"
    assert answer["reason"] in reasons, f"the reason is not one of {reasons}: {answer!r}"


# --------------------------------------------------------------------------
# git
# --------------------------------------------------------------------------

BASE_DATE = "2026-09-01T12:00:00+00:00"
LATER = "2026-09-02T12:00:00+00:00"


def git(project, *args, date=BASE_DATE):
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(project),
        "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_AUTHOR_NAME": "W1-17 tests", "GIT_AUTHOR_EMAIL": "w1-17@example.invalid",
        "GIT_COMMITTER_NAME": "W1-17 tests", "GIT_COMMITTER_EMAIL": "w1-17@example.invalid",
        "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date,
    }
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, env=env)
    assert done.returncode == 0, f"git {' '.join(args)} failed in {project}:\n{done.stderr}"
    return done.stdout


def write(project, rel, text):
    path = Path(project) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return rel


def commit(project, message="a change", date=LATER):
    """Track and commit everything that is not ignored."""
    git(project, "add", "-A")
    git(project, "commit", "-q", "--allow-empty", "-m", message, date=date)


def clone(source, destination):
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(source), str(destination)], check=True,
                   capture_output=True)
    return Path(destination)


def tracked(project):
    return sorted(rel for rel in git(project, "ls-files", "-z").split("\0") if rel)


def porcelain(project):
    return git(project, "status", "--porcelain").splitlines()


def runtime_files(project):
    """Every file under ``.gov-runtime/`` of ``project``, as paths relative to that folder."""
    base = Path(project) / RUNTIME_REL
    return sorted(path.relative_to(base).as_posix() for path in base.rglob("*") if path.is_file())


def files_holding(root, needles):
    """``relative path -> needles found`` for every regular file under ``root`` that holds one of ``needles``."""
    root = Path(root)
    wanted = [needle.encode() for needle in needles]
    found = {}
    if not root.exists():
        return found
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        data = path.read_bytes()
        hits = [needle.decode() for needle in wanted if needle in data]
        if hits:
            found[path.relative_to(root).as_posix()] = hits
    return found


# --------------------------------------------------------------------------
# Planted strings, built at run time: none of them stands whole in this file
# --------------------------------------------------------------------------

def _body(seed, length):
    out, count = "", 0
    while len(out) < length:
        out += base64.b64encode(hashlib.sha256(f"{seed}{count}".encode()).digest()).decode()
        count += 1
    return out.replace("=", "A").replace("+", "b").replace("/", "c")[:length]


_WORD = "CAN" + "ARY"
# The canary as W1-15's first KPI line writes it: found by the canary rule, which DEC-325 leaves unchanged.
CANARY = "_".join(["ARGUS", "TOKEN", _WORD, "4WM8"])
_KEY_BODY = _body("w1-17-key", 192)
# A string the gitleaks default rules find (private-key). Not a real credential.
PRIVATE_KEY = ("-----BEGIN RSA PRIVATE " + "KEY-----\n"
               + "\n".join(_KEY_BODY[start:start + 64] for start in range(0, 192, 64))
               + "\n-----END RSA PRIVATE " + "KEY-----")
SECRETS = {"canary": CANARY, "private-key": PRIVATE_KEY}
# What to look for in a store: the canary, and a line of the key's body.
SECRET_NEEDLES = {"canary": CANARY, "private-key": _KEY_BODY[:64]}

# The three planted values of the a-dev tier that carry the canary word (DEC-286).
A_DEV_CANARIES = (
    "-".join(["ORION", _WORD, "SECRET", "001"]),
    "-".join(["ORION", _WORD, "SECRET", "002"]),
    "-".join(["ORION", _WORD, "SECRET", "003"]),
)


# --------------------------------------------------------------------------
# The fixture project
# --------------------------------------------------------------------------

_NAMESPACE_FIELDS = {
    "sensitivity": "internal",
    "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                        "independent-auditor", "research"],
    "retention": "kept in git history",
    "export_policy": "allowed",
    "embedding_policy": "embedded",
    "provenance": "written by the W1-17 tests",
    "deletion_rebuild": "authoritative; restored from git only",
}

# ``name -> (patterns, memory_class)``. The product namespace has a name and a path this repository's own map does
# not use, so a rule written into the code for this repository cannot satisfy the tests.
NAMESPACES = {
    "top": (["*"], "governance"),
    "overlay": (["governance/**"], "governance"),
    "notes": (["notes/**"], "governance"),
    "code": (["app/**"], "governance"),
    "tenant-exports": (["tenant-exports/**"], "product"),
}


def path_map_text(namespaces):
    """A full path map (DEC-225): this repository's own, with ``namespaces`` in place of its namespaces."""
    document = yaml.safe_load((REPO_ROOT / PATH_MAP_REL).read_text(encoding="utf-8"))
    document["namespaces"] = {
        name: {"paths": list(patterns), "memory_class": memory_class, **_NAMESPACE_FIELDS}
        for name, (patterns, memory_class) in namespaces.items()}
    return yaml.safe_dump(document, sort_keys=False)


def set_namespaces(project, namespaces):
    write(project, PATH_MAP_REL, path_map_text(namespaces))


def adopt(project, namespaces):
    """Give ``project`` a path map and the kernel's gitleaks configuration (the two files the secret filter reads)."""
    set_namespaces(project, namespaces)
    source = REPO_ROOT / TEMPLATE_CONFIG_REL
    if not source.is_file():
        raise Missing(f"{TEMPLATE_CONFIG_REL} does not exist")
    shutil.copy2(source, Path(project) / CONFIG_REL)


ERROR = "connection refused: upstream pool exhausted (code E4417)"
SNAKE = "partition_floor_rules"
CAMEL = "RetryBudgetExceeded"
CALL = "pool.full()"
MARKER = "zebra_quartz_marker"
TWIN = "heliotrope ledger entry"
ABSENT = "no line of the fixture holds this sentence"
PRODUCT_WORD = "Scarborough"

RUNBOOK = "notes/runbook.md"
RUNBOOK_TEXT = f"""\
# Runbook

Intro text for the operators.

## Starting

Start the pool with {SNAKE} enabled.

## Failures

The log shows `{ERROR}` twice.
Retry after the pool drains.

## Recovery

The same words in another order: exhausted pool upstream, refused connection, code (E4417).
"""

POOL = "app/pool.py"
POOL_TEXT = f'''\
"""Connection pool."""

LIMIT_OF_THE_POOL = 8


class {CAMEL}(Exception):
    pass


def {SNAKE}(rules):
    kept = [rule for rule in rules if rule]
    return kept


def connect(pool):
    if {CALL}:
        raise {CAMEL}("{ERROR}")
    return {SNAKE}(pool.rules)
'''

CLIENT = "app/client.ts"
CLIENT_TEXT = f"""\
export function connect(pool: Pool): Rules {{
  if ({CALL}) {{
    throw new Error("{ERROR}");
  }}
  return pool.rules;
}}
"""

LONG = "notes/deep/long.md"
LONG_LINES = 3000
MARKED_LINES = (1, 1777, 1778, LONG_LINES)
LONG_TEXT = "".join(
    f"line {number}: {MARKER} stands here\n" if number in MARKED_LINES
    else f"line {number}: nothing of interest here\n"
    for number in range(1, LONG_LINES + 1))

# Strings an FTS5 MATCH would read as syntax. Each stands on one line of the file and is queried as it is.
SYNTAX = "notes/syntax.md"
SYNTAX_QUERIES = {
    "operators": "status AND NOT ready OR (pending)",
    "quotes": 'say "hello world" twice',
    "wildcards": "prefix* wildcard^2 col:value",
    "code": "C++ -> a[i] += 1;",
}
SYNTAX_TEXT = "# Odd strings\n\n" + "".join(f"{text}\n\n" for text in SYNTAX_QUERIES.values())

TWINS = ("notes/copy-a.txt", "app/copy-b.txt")
TWIN_TEXT = f"First line.\nThe {TWIN} is on line two.\n"

PRODUCT_FILE = "tenant-exports/2026/customers.csv"
PRODUCT_TEXT = f"id,name,city\n1,Ada,Leeds\n2,Grace,{PRODUCT_WORD}\n"

# The tracked files an index must hold: no folder, name or extension is special.
CORPUS = {
    "README.md": "# A project\n\nOrdinary text about the project.\n",
    "Makefile": "check:\n\tpython3 -m pytest\n",
    RUNBOOK: RUNBOOK_TEXT,
    "notes/README": "A file without an extension.\n",
    LONG: LONG_TEXT,
    SYNTAX: SYNTAX_TEXT,
    POOL: POOL_TEXT,
    CLIENT: CLIENT_TEXT,
    "app/data/values.json": '{"limit": 8, "name": "pool"}\n',
    TWINS[0]: TWIN_TEXT,
    TWINS[1]: TWIN_TEXT,
}
GITIGNORE = ".gov-runtime/\nscratch-local/\n"


def build_fixture(project):
    """The fixture repository: one commit holding the corpus, a product-data file, the path map and the rules."""
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    git(project, "init", "-q", "-b", "main")
    adopt(project, NAMESPACES)
    write(project, ".gitignore", GITIGNORE)
    write(project, PRODUCT_FILE, PRODUCT_TEXT)
    for rel, text in CORPUS.items():
        write(project, rel, text)
    commit(project, "the fixture", BASE_DATE)
    return project


def occurrences(needle, files=None):
    """``[(path, line), ...]`` of every line of ``files`` (default: the corpus) that holds ``needle``, sorted."""
    files = CORPUS if files is None else files
    return sorted((rel, number) for rel, text in files.items()
                  for number, line in enumerate(text.splitlines(), 1) if needle in line)


def line_of(text, start):
    """The number of the one line of ``text`` that starts with ``start``."""
    found = [number for number, line in enumerate(text.splitlines(), 1) if line.startswith(start)]
    assert len(found) == 1, f"expected one line starting with {start!r}, found {len(found)}"
    return found[0]


def line_count(text):
    return len(text.splitlines())


# --------------------------------------------------------------------------
# The dev tier
# --------------------------------------------------------------------------

def clone_tier(destination):
    """A clone of the a-dev tier in a temporary directory, or None when this machine has no such tier."""
    tier = DEV_TIERS / DEV_TIER
    if not (tier / ".git").exists():
        return None
    return clone(tier, destination)


# --------------------------------------------------------------------------
# gov check --list --json, and the declared command
# --------------------------------------------------------------------------

def family_key(text):
    """``"Index-Freshness"`` -> ``"index freshness"``."""
    return " ".join(re.findall(r"[a-z0-9]+", str(text).lower()))


def family_check(api):
    """The one check of the index-freshness family that ``gov check --list --json`` lists for this repository."""
    if not sorted((REPO_ROOT / CHECKS_REL).glob(CHECK_GLOB)):
        raise Missing(f"the index-freshness check is not registered: nothing matches {CHECKS_REL}/{CHECK_GLOB}")
    scripts = tomllib.loads((REPO_ROOT / PYPROJECT_REL).read_text(encoding="utf-8"))["project"]["scripts"]
    module, _, attribute = scripts["gov"].partition(":")
    launcher = f"import sys\nimport {module} as _m\nsys.argv[0] = 'gov'\nsys.exit(getattr(_m, {attribute!r})())\n"
    done = subprocess.run([sys.executable, "-c", launcher, "check", "--list", "--json", "--root", str(REPO_ROOT)],
                          cwd=str(api.workdir / "elsewhere"), env=api.env(), capture_output=True, text=True,
                          timeout=CALL_TIMEOUT_S, stdin=subprocess.DEVNULL)
    described = f"gov check --list --json\nexit code: {done.returncode}\nstdout:\n{done.stdout}\nstderr:\n{done.stderr}"
    assert done.returncode == 0, f"gov check --list does not succeed\n{described}"
    checks = json.loads(done.stdout)["result"]["checks"]
    found = [check for check in checks if family_key(check.get("family")) == FAMILY]
    assert len(found) == 1, f"expected one listed check of the family {FAMILY!r}, found {len(found)}\n{described}"
    return found[0]


class CheckRun:
    def __init__(self, command, done):
        self.command, self.returncode, self.stdout, self.stderr = command, done.returncode, done.stdout, done.stderr
        self.output = done.stdout + done.stderr

    def describe(self):
        return f"{self.command}\nexit code: {self.returncode}\nstdout:\n{self.stdout}\nstderr:\n{self.stderr}"


def run_check(check, project, api):
    """Run the declared command as DEC-285 states: by ``sh -c``, in the project's root; exit 0 is green."""
    command = check["command"]
    try:
        done = subprocess.run(command, shell=True, cwd=str(project), env=api.env(), capture_output=True, text=True,
                              timeout=CALL_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"the check command did not end within {CALL_TIMEOUT_S:.0f} s: {command}") from None
    return CheckRun(command, done)
