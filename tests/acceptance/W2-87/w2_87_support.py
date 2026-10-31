"""Support code for the W2-87 acceptance tests (standard library and PyYAML only).

W2-87 ranks retrieval by authority (DEC-952 item 1): a register chunk is the entry whose span holds it, and an
order of tiers read from the path map's ``retrieval_authority`` block lifts a governing source above a test or an
assessment report of the same match. The tests use only public interfaces:

- ``gov.retrieval.retrieve.retrieve(root, query, ...)`` and the command ``gov retrieve --json``, each called in a
  child process with this worktree's ``src/`` on ``PYTHONPATH`` (DEC-732);
- ``gov.retrieval.lexical.refresh``, ``gov.store.load`` to build what a retrieval reads (never ``gov rebuild``,
  never this repository's store), and ``gov.retrieval.lexical.search`` with ``gov.retrieval.fusion.rrf`` for the
  plain fused order the bundle is compared with.

Every project is a temporary git repository built from nothing, with its own path map and gitleaks rules. No vector
is built, so the semantic route is unavailable and gives no hit; no reranker is loaded unless a stub is passed.
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
PATH_MAP_REL = "governance/project/path-map.yaml"
GITLEAKS_TEMPLATE = REPO_ROOT / "template/.gitleaks.toml"
REGISTER = "docs/DECISION_REGISTER.md"
CALL_TIMEOUT_S = 300.0
CONFIG_INVALID = "CONFIG_INVALID"
NOT_GATHERED = "NOT_GATHERED"
CLOSURE = "closure"

# --------------------------------------------------------------------------
# The planted corpus: one tracked tree, the same in every project; only the path map's block differs
# --------------------------------------------------------------------------

PHRASE = "vermilion beacon clause"   # every source of the authority cases carries it
FAVOURED = "quartz"                  # the stub reranker scores a text by how often it holds this word
CUT_PHRASE = "cinder gate tally"     # the first-call cut: six reports, then one specification, by path
UNRELATED = "zzyzx plover xyzzy"     # no line of the corpus holds it

# The register: a superseding pair (DEC-102's status line supersedes DEC-101), then three entries without the
# phrase, the last by id (DEC-106) accepted.
OLD, NEW, CLOSED_OVER, NEIGHBOUR, LAST = "DEC-101", "DEC-102", "DEC-104", "DEC-105", "DEC-106"
REGISTER_TEXT = f"""# Decision register

The decisions of the planted harbour, oldest first.

### {OLD}: The first beacon rule
- **Status:** ACCEPTED · **Basis:** OWNER

The {PHRASE} applies to every harbour light.

### {NEW}: The beacon rule, restated
- **Status:** ACCEPTED · **Basis:** OWNER · **Supersedes:** {OLD}

The {PHRASE} applies to every harbour light and every buoy.

### {CLOSED_OVER}: The tide gauge
- **Status:** ACCEPTED · **Basis:** OWNER

The tide gauge is read at dawn by the harbour master.

### {NEIGHBOUR}: The pilot boat
- **Status:** ACCEPTED · **Basis:** OWNER

The pilot boat leaves at the second bell.

### {LAST}: The harbour office
- **Status:** ACCEPTED · **Basis:** OWNER

The harbour office opens at nine.
"""

# A second register, for the drop case: its last entry by id is SUPERSEDED by its own status line.
KEPT_A, KEPT_B, LAST_SUPERSEDED = "DEC-201", "DEC-202", "DEC-203"
SUPERSEDED_LAST_REGISTER_TEXT = f"""# Decision register

### {KEPT_A}: The lamp rule
- **Status:** ACCEPTED · **Basis:** OWNER

The {PHRASE} governs every lamp.

### {KEPT_B}: The mast rule
- **Status:** ACCEPTED · **Basis:** OWNER

The {PHRASE} governs every mast.

### {LAST_SUPERSEDED}: The old flag rule
- **Status:** SUPERSEDED · **Basis:** OWNER

The {PHRASE} once governed every flag.
"""

ADR = "docs/adr/adr-0001-beacons.md"
DEPRECATED_ADR = "docs/adr/adr-0002-lamps.md"
REPORT = "docs/assessment/beacon-report.md"
SPEC = "docs/spec/beacon-spec.md"
NOTES = "notes/beacon-notes.md"
CAPABILITY = "records/capabilities/cap-0010.md"
TEST = "tests/test_beacon.py"
CUT_REPORTS = [f"docs/assessment/cut-r{number:02d}.md" for number in range(1, 7)]
CUT_SPEC = "docs/spec/cut-gate.md"


def _record(record_id, kind, status, body):
    front = {"id": record_id, "type": kind, "status": status, "state_class": "AUTHORITATIVE"}
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + f"---\n\n# {record_id}\n\n{body}\n"


def corpus(register_text=REGISTER_TEXT):
    files = {
        "README.md": "# The planted harbour\n\nOrdinary text about the harbour.\n",
        ".gitignore": ".gov-runtime/\n",
        REGISTER: register_text,
        ADR: f"# ADR-0001: Beacons\n\nThe {PHRASE} is set by this architecture record.\n",
        DEPRECATED_ADR: _record("ADR-0002", "decision", "DEPRECATED", f"The {PHRASE} once named the lamps."),
        REPORT: f"# Beacon assessment\n\nThe {PHRASE} was found in three places. "
                f"{FAVOURED} {FAVOURED} {FAVOURED}\n",
        SPEC: f"# Beacon specification\n\nThe {PHRASE} is specified here.\n",
        NOTES: f"# Notes\n\nA note on the {PHRASE}.\n",
        CAPABILITY: _record("CAP-0010", "capability", "ACTIVE", f"The {PHRASE} is a capability of the harbour."),
        TEST: f'"""The {PHRASE} is tested here ({FAVOURED})."""\n\n\ndef test_beacon():\n    assert True\n',
        CUT_SPEC: f"# Gate specification\n\nThe {CUT_PHRASE} is specified here.\n",
    }
    for number, rel in enumerate(CUT_REPORTS, 1):
        files[rel] = f"# Cut report {number}\n\nThe {CUT_PHRASE} was counted at gate {number}.\n"
    return files


GOVERNING = [ADR, SPEC, CAPABILITY]   # with NEW's register chunk
REPORTS = [REPORT, TEST]

# --------------------------------------------------------------------------
# The blocks of the path map (the form is the interface; the values are this suite's own)
# --------------------------------------------------------------------------

GOVERNING_TIER = {"name": "governing",
                  "records": [{"type": "decision", "status": ["ACCEPTED"]}, {"type": "capability"}],
                  "paths": ["docs/contract/**", "docs/charter/**", "docs/spec/**", "docs/adr/**"]}
MIDDLE_TIER = {"name": "middle"}
REPORTS_TIER = {"name": "reports", "paths": ["tests/**", "docs/assessment/**", "docs/audit/**", "docs/probes/**"]}


def block(fused=0.004, rerank=1.0, tiers=(GOVERNING_TIER, MIDDLE_TIER, REPORTS_TIER), default="middle"):
    return {"lift": {"fused": fused, "rerank": rerank}, "default": default, "tiers": [dict(t) for t in tiers]}


ABSENT = object()
CONFIGS = {
    "absent": ABSENT,
    "main": block(),
    # tests and reports above decisions: the configuration, not the code, decides
    "flipped": block(tiers=(dict(REPORTS_TIER, name="reports-first"), MIDDLE_TIER,
                            dict(GOVERNING_TIER, name="governing-last"))),
    # a lift of 0.00054 per step: 0.00108 between a governing chunk and a report, which passes a report one to
    # four places ahead of it in the plain fused order (at most 0.00095 better) and not one five places ahead
    # (0.00120 better); see test_w2_87_authority.py
    "small": block(fused=0.00054),
    # fail closed (CONFIG_INVALID)
    "not-a-mapping": "governing first, then the rest",
    "unknown-default": block(default="nowhere"),
    "unknown-key": {**block(), "weight": 2},
    "status-not-a-word": block(tiers=({**GOVERNING_TIER, "records": [{"type": "decision",
                                                                         "status": ["ACCEPTED, SUPERSEDED"]}]},
                                      MIDDLE_TIER, REPORTS_TIER)),
}

# --------------------------------------------------------------------------
# git and the project
# --------------------------------------------------------------------------

DATE = "2026-10-30T12:00:00+00:00"


def git(project, *args):
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(project), "LC_ALL": "C",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "W2-87 tests", "GIT_AUTHOR_EMAIL": "w2-87@example.invalid",
           "GIT_COMMITTER_NAME": "W2-87 tests", "GIT_COMMITTER_EMAIL": "w2-87@example.invalid",
           "GIT_AUTHOR_DATE": DATE, "GIT_COMMITTER_DATE": DATE}
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, env=env)
    assert done.returncode == 0, f"git {' '.join(args)} failed in {project}:\n{done.stderr}"
    return done.stdout


def path_map(authority):
    """This repository's path map as W1-21 adopts it: its namespaces replaced by one that classes everything as
    governance memory without vectors, the planted register named, and the authority block set or left out."""
    document = yaml.safe_load((REPO_ROOT / PATH_MAP_REL).read_text(encoding="utf-8"))
    document.pop("retrieval_authority", None)
    document["decision_register"] = REGISTER
    document["namespaces"] = {"everything": {
        "paths": ["**"], "memory_class": "governance", "sensitivity": "internal",
        "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                            "independent-auditor", "research"],
        "retention": "kept in git history", "export_policy": "allowed", "provenance": "written by the W2-87 tests",
        "deletion_rebuild": "authoritative; restored from git only", "embedding_policy": "not embedded"}}
    if authority is not ABSENT:
        document["retrieval_authority"] = authority
    return yaml.safe_dump(document, sort_keys=False, allow_unicode=True)


def build_project(project, authority, register_text=REGISTER_TEXT):
    """A committed project; its lexical index and record graph are built by ``Api.build``."""
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    git(project, "init", "-q", "-b", "main")
    files = {**corpus(register_text), PATH_MAP_REL: path_map(authority)}
    for rel, text in files.items():
        (project / rel).parent.mkdir(parents=True, exist_ok=True)
        (project / rel).write_text(text, encoding="utf-8")
    shutil.copy2(GITLEAKS_TEMPLATE, project / ".gitleaks.toml")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "the planted harbour")
    return project


# --------------------------------------------------------------------------
# The driver: one child process per batch of calls
# --------------------------------------------------------------------------

_DRIVER = r'''
import importlib, json, sys
from pathlib import Path

request = json.loads(sys.stdin.read())


def stub():
    """The stub reranker's loader: a text scores how often it holds the favoured words."""
    favour = request["favour"]

    def score(query, texts):
        return [float(sum(str(text).count(word) for word in favour)) for text in texts]

    return score


def decode(value):
    if isinstance(value, dict) and set(value) == {"$path"}:
        return Path(value["$path"])
    if value == "$stub":
        return stub
    if value == "$absent":
        return lambda: None
    return value


out = []
for call in request["calls"]:
    function = getattr(importlib.import_module(call["module"]), call["function"])
    record = {"value": None, "error": None}
    try:
        record["value"] = function(*[decode(arg) for arg in call["args"]],
                                   **{key: decode(value) for key, value in call["kwargs"].items()})
    except Exception as exc:
        record["error"] = {"type": type(exc).__name__, "message": str(exc), "code": getattr(exc, "code", None)}
    out.append(record)
print("\n" + json.dumps(out, default=repr))
'''

STUB, NO_RERANKER = "$stub", "$absent"


def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


class Api:
    """Calls this worktree's modules and its ``gov`` command line, each in a new process."""

    def __init__(self, workdir):
        self.workdir = Path(workdir)
        for name in ("home", "tmp", "pycache", "elsewhere", "bin"):
            (self.workdir / name).mkdir(parents=True, exist_ok=True)
        for tool in ("git", "gitleaks", "python3"):   # the scratch PATH holds these three only
            found = sys.executable if tool == "python3" else shutil.which(tool)
            if found:
                wrapper = self.workdir / "bin" / tool
                wrapper.write_text(f'#!/bin/sh\nexec "{found}" "$@"\n', encoding="utf-8")
                wrapper.chmod(0o755)
        self.driver = self.workdir / "driver.py"
        self.driver.write_text(_DRIVER, encoding="utf-8")
        self.dead_host = f"127.0.0.1:{_free_port()}"

    def env(self):
        """Built from nothing: an empty HOME (no reranker environment), a dead embedder endpoint, offline."""
        return {"PATH": str(self.workdir / "bin"), "HOME": str(self.workdir / "home"),
                "TMPDIR": str(self.workdir / "tmp"), "LC_ALL": "C.UTF-8", "GIT_CONFIG_NOSYSTEM": "1",
                "PYTHONPATH": str(SRC), "PYTHONPYCACHEPREFIX": str(self.workdir / "pycache"),
                "OLLAMA_HOST": self.dead_host, "GOV_QUERY_OLLAMA_HOST": self.dead_host,
                "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}

    def run(self, calls, favour=()):
        request = {"favour": list(favour), "calls": [{"module": m, "function": f, "args": list(a), "kwargs": dict(k)}
                                                     for m, f, a, k in calls]}
        done = subprocess.run([sys.executable, str(self.driver)], input=json.dumps(request), env=self.env(),
                              cwd=str(self.workdir / "elsewhere"), capture_output=True, text=True,
                              timeout=CALL_TIMEOUT_S)
        assert done.returncode == 0, f"the driver failed (exit code {done.returncode}):\n{done.stderr[-4000:]}"
        return json.loads(done.stdout.strip().splitlines()[-1])

    def build(self, root):
        """The lexical index and the record graph of ``root``; no vector."""
        root_arg = {"$path": str(root)}
        out = self.run([("gov.retrieval.lexical", "refresh", [root_arg], {}),
                        ("gov.store", "load", [root_arg], {})])
        for record in out:
            assert record["error"] is None, f"the planted project could not be built: {record['error']}"

    def outcome(self, root, query, favour=(), **kwargs):
        """``{"value": bundle, "error": None}`` or ``{"value": None, "error": {type, message, code}}``."""
        kwargs.setdefault("reranker", NO_RERANKER)
        return self.run([("gov.retrieval.retrieve", "retrieve", [{"$path": str(root)}, query], kwargs)],
                        favour=favour)[0]

    def retrieve(self, root, query, favour=(), **kwargs):
        record = self.outcome(root, query, favour=favour, **kwargs)
        assert record["error"] is None, f"retrieve raised {record['error']}"
        return record["value"]

    def plain_order(self, root, query):
        """The chunk ids of the plain fused order of the lexical route (the only route that answers here)."""
        root_arg = {"$path": str(root)}
        out = self.run([("gov.retrieval.lexical", "search", [root_arg, query], {"refresh": False})])
        assert out[0]["error"] is None, out[0]["error"]
        hits = out[0]["value"]["hits"]
        fused = self.run([("gov.retrieval.fusion", "rrf", [{"lexical": hits}], {})])[0]["value"]
        return [(hit["chunk_id"], hit["path"]) for hit in fused]

    def command(self, root, *args):
        done = subprocess.run([sys.executable, "-m", "gov.cli.main", "retrieve", "--json", "--root", str(root),
                               *args], capture_output=True, text=True, cwd=str(self.workdir / "elsewhere"),
                              env=self.env(), timeout=CALL_TIMEOUT_S, stdin=subprocess.DEVNULL)
        return done


# --------------------------------------------------------------------------
# Reading a bundle
# --------------------------------------------------------------------------

def register_span(text, entry_id):
    """``(first, last)`` lines (1-based) of an entry: its heading to the line before the next heading."""
    lines = text.split("\n")
    first = next(n for n, line in enumerate(lines, 1) if line.startswith(f"### {entry_id}:"))
    last = next((n - 1 for n, line in enumerate(lines, 1) if n > first and line.startswith("#")), len(lines))
    return first, last


def label(item, register_text=REGISTER_TEXT):
    """A register chunk is named by the entry whose span holds its first line; any other chunk by its path."""
    if item["path"] != REGISTER:
        return item["path"]
    for line in register_text.split("\n"):
        if line.startswith("### "):
            entry_id = line[4:].split(":")[0]
            first, last = register_span(register_text, entry_id)
            if first <= item["start_line"] <= last:
                return entry_id
    return f"{REGISTER} (before the first entry)"


def labels(bundle, register_text=REGISTER_TEXT):
    return [label(item, register_text) for item in bundle["evidence"]]


def rank_of(names, name):
    assert name in names, f"{name} is not in the bundle: {names}"
    return names.index(name)


def gathered_set(bundle):
    """What a bundle keeps and what it leaves out: its evidence's chunks, its drops and its not-gathered gaps."""
    return (sorted(item["chunk_id"] for item in bundle["evidence"]),
            sorted(json.dumps(entry, sort_keys=True) for entry in bundle["merge"]["dropped"]),
            sorted(gap["chunk_id"] for gap in bundle["gaps"] if gap.get("reason") == NOT_GATHERED))
