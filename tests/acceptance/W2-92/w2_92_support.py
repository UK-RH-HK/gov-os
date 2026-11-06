"""Support code for the W2-92 acceptance tests (standard library and PyYAML only).

W2-92 adds two routes to plain-question retrieval (DEC-957, MEMORY-SPEC-MAP gaps 2 and 3): an id or a record title
found in the question becomes a start id of the record closure (the record route), and a symbol name found in it is
asked of the code index through the code-graph tool's own traversal (the code route, DEC-859). The tests use only
public interfaces:

- ``gov.retrieval.retrieve.retrieve(root, query, ...)`` and the command ``gov retrieve --json``, each called in a
  child process with this worktree's ``src/`` on ``PYTHONPATH`` (DEC-732);
- ``gov.retrieval.lexical.refresh``, ``gov.store.load`` and ``gov.codeintel.index`` to build what a retrieval reads
  (never ``gov rebuild`` of this repository, never this repository's store), and ``gov.retrieval.lexical.search``
  with ``gov.retrieval.fusion.rrf`` for the plain fused order of the routes that exist today (the lexical route's
  ``ranked`` list since W2-13's S2).

Every project is a temporary git repository built from nothing. No vector is built, so the semantic route is
unavailable and gives no hit; no reranker is loaded. The code-graph tool is reached through a stand-in on ``PATH``
that records every request it is sent and passes it on to the real binary (or, for the fail-closed cases, fails).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import socket
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
SRC = REPO_ROOT / "src"
PATH_MAP_REL = "governance/project/path-map.yaml"
GITLEAKS_TEMPLATE = REPO_ROOT / "template/.gitleaks.toml"
REGISTER = "docs/DECISION_REGISTER.md"
TOOL = "codebase-memory-mcp"
ROW_CAP = 100_000          # the code-graph tool's row cap (codebase-memory-mcp 0.11.0; DEC-859, lens G F1)
CAP_REFUSAL = "exceeded"   # the tool's answer to a query over its cap: "result exceeded 100k rows ..."
CALL_TIMEOUT_S = 300.0
STORE_MISSING = "STORE_MISSING"
NOT_GATHERED = "NOT_GATHERED"

# --------------------------------------------------------------------------
# The planted corpus
# --------------------------------------------------------------------------

UNRELATED = "zzyzx plover"   # no line of the corpus holds these words

# The register: DEC-301 is the named record. Its text shares no word with the questions that name it.
NAMED_DEC, OTHER_DEC = "DEC-301", "DEC-302"
NAMED_DEC_TITLE = "The lantern rule"
NAMED_DEC_TEXT = "Every quayside lamp burns from dusk until the morning bell."
REGISTER_TEXT = f"""# Decision register

The decisions of the planted harbour, oldest first.

### {NAMED_DEC}: {NAMED_DEC_TITLE}
- **Status:** ACCEPTED · **Basis:** OWNER

{NAMED_DEC_TEXT}

### {OTHER_DEC}: The ferry timetable
- **Status:** ACCEPTED · **Basis:** OWNER

The ferry crosses twice an hour in summer.
"""

# A capability record and a ticket record, each with a body no question shares a word with; a lesson that
# constrains the ticket (DEC-424: records ahead in a ticket's closure); and a record near the capability (radius 1).
NAMED_CAP = "CAP-77"
NAMED_CAP_TEXT = "Signal flags are hoisted on the eastern mast."
NAMED_TICKET = "DAEO-hb92"
NAMED_TICKET_TEXT = "Repaint the breakwater beacon in red and white bands."
LESSON = "LES-0092"
LESSON_TEXT = "Paint dries slowly in the salt spray; allow two dry days."
NEAR = "REQ-0092"
NEAR_TEXT = "The eastern mast carries three halyards."
TITLED = "SPEC-0092"
TITLED_TITLE = "Cormorant Nesting Protocol"
TITLED_TEXT = "Ledges below the lighthouse stay closed from April to June."

CAP_REL = "records/capabilities/cap-77.md"
TICKET_REL = f".tickets/{NAMED_TICKET}.md"
LESSON_REL = "records/lessons/les-0092.md"
NEAR_REL = "records/requirements/req-0092.md"
TITLED_REL = "docs/spec/spec-0092.md"
NAMED_W2 = "W2-592"
NAMED_W2_TEXT = "Dredge the inner basin before the regatta."
W2_REL = "docs/records/w2-592.md"
# A plain page that cites DEC-301: the one item today's lexical route gives for "lantern note DEC-301"
NOTE_REL = "docs/notes/lantern-note.md"
NOTE_TEXT = f"The lantern note of the harbour cites {NAMED_DEC}."

# Plain-text pages: what today's routes find for the plain questions.
PLAIN_PHRASE = "harbour tide almanac"
PLAIN_PAGES = [f"docs/notes/almanac-{number:02d}.md" for number in range(1, 7)]

# The code: w92_leaf is called by w92_mid (another file) and w92_side; w92_mid is called by w92_top. The callers'
# files hold no word of the question but the symbol's own name.
LEAF, MID, TOP, SIDE = "w92_leaf", "w92_mid", "w92_top", "w92_side"
LEAF_REL, MID_REL, TOP_REL = "app/leaf.py", "app/middle.py", "app/top.py"
LEAF_CODE = f"def {LEAF}(value):\n    return value + 1\n"
MID_CODE = (f"from app.leaf import {LEAF}\n\n\n"
            f"def {MID}(value):\n    return {LEAF}(value) * 2\n\n\n"
            f"def {SIDE}(value):\n    return {LEAF}(value) + 5\n")
TOP_CODE = f"from app.middle import {MID}\n\n\ndef {TOP}(value):\n    return {MID}(value) - 3\n"
# (path, first line, last line) of each function, as the source above says
SPANS = {LEAF: (LEAF_REL, 1, 2), MID: (MID_REL, 4, 5), SIDE: (MID_REL, 8, 9), TOP: (TOP_REL, 4, 5)}
CALLERS = {LEAF: [MID, SIDE], MID: [TOP]}


def _record(record_id, kind, status, title, body, **edges):
    front = {"id": record_id, "type": kind, "status": status, "state_class": "AUTHORITATIVE", "title": title}
    front.update(edges)
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + f"---\n\n# {title}\n\n{body}\n"


def corpus():
    files = {
        "README.md": "# The planted harbour\n\nOrdinary text about the harbour.\n",
        ".gitignore": ".gov-runtime/\n",
        REGISTER: REGISTER_TEXT,
        CAP_REL: _record(NAMED_CAP, "capability", "ACTIVE", "Eastern signals", NAMED_CAP_TEXT),
        NEAR_REL: _record(NEAR, "requirement", "ACTIVE", "Halyards", NEAR_TEXT, implements=[NAMED_CAP]),
        TICKET_REL: _record(NAMED_TICKET, "task", "open", "Breakwater paint", NAMED_TICKET_TEXT),
        LESSON_REL: _record(LESSON, "lesson", "ACTIVE", "Salt spray", LESSON_TEXT, constrains=[NAMED_TICKET]),
        TITLED_REL: _record(TITLED, "specification", "ACTIVE", TITLED_TITLE, TITLED_TEXT),
        W2_REL: _record(NAMED_W2, "task", "open", "Inner basin", NAMED_W2_TEXT),
        NOTE_REL: f"# Lantern note\n\n{NOTE_TEXT}\n",
        LEAF_REL: LEAF_CODE, MID_REL: MID_CODE, TOP_REL: TOP_CODE, "app/__init__.py": "",
    }
    for number, rel in enumerate(PLAIN_PAGES, 1):
        files[rel] = f"# Almanac page {number}\n\nThe {PLAIN_PHRASE} lists the tides of week {number}.\n"
    return files


# --------------------------------------------------------------------------
# git and the project
# --------------------------------------------------------------------------

DATE = "2026-10-31T12:00:00+00:00"


def git(project, *args):
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(project), "LC_ALL": "C",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "W2-92 tests", "GIT_AUTHOR_EMAIL": "w2-92@example.invalid",
           "GIT_COMMITTER_NAME": "W2-92 tests", "GIT_COMMITTER_EMAIL": "w2-92@example.invalid",
           "GIT_AUTHOR_DATE": DATE, "GIT_COMMITTER_DATE": DATE}
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, env=env)
    assert done.returncode == 0, f"git {' '.join(args)} failed in {project}:\n{done.stderr}"
    return done.stdout


def path_map():
    """This repository's path map with one namespace that classes everything as governance memory without vectors
    and the planted register named; no authority block (W2-87's order is not under test here)."""
    document = yaml.safe_load((REPO_ROOT / PATH_MAP_REL).read_text(encoding="utf-8"))
    document.pop("retrieval_authority", None)
    document["decision_register"] = REGISTER
    document["namespaces"] = {"everything": {
        "paths": ["**"], "memory_class": "governance", "sensitivity": "internal",
        "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                            "independent-auditor", "research"],
        "retention": "kept in git history", "export_policy": "allowed", "provenance": "written by the W2-92 tests",
        "deletion_rebuild": "authoritative; restored from git only", "embedding_policy": "not embedded"}}
    return yaml.safe_dump(document, sort_keys=False, allow_unicode=True)


def build_project(project):
    """A committed project; what a retrieval reads is built by ``Api.build``."""
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    git(project, "init", "-q", "-b", "main")
    files = {**corpus(), PATH_MAP_REL: path_map()}
    for rel, text in files.items():
        (project / rel).parent.mkdir(parents=True, exist_ok=True)
        (project / rel).write_text(text, encoding="utf-8")
    shutil.copy2(GITLEAKS_TEMPLATE, project / ".gitleaks.toml")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "the planted harbour")
    return project


# --------------------------------------------------------------------------
# The code-graph tool: the real binary, a recording stand-in, a failing stand-in
# --------------------------------------------------------------------------

# Runs as ``codebase-memory-mcp`` and passes everything on to the real tool, recording each request on the way: a
# one-shot ``cli <tool> <json>`` call by its arguments, and in the server form (MCP over stdin and stdout, one
# message a line) each ``tools/call`` message by its tool name and arguments. An answer that is the tool's refusal
# over its cap is recorded too.
_RECORDER = r'''#!{python}
import json, subprocess, sys, threading
LOG = {log!r}
lock = threading.Lock()


def note(entry):
    with lock, open(LOG, "a", encoding="utf-8") as log:
        log.write(json.dumps(entry) + "\n")


def refused(raw):
    text = raw.decode("utf-8", "replace")
    return {refusal!r} in text and "row" in text


argv = sys.argv[1:]
words = [word for word in argv if not word.startswith("-")]
if words and words[0] == "cli":
    tool = words[1] if len(words) > 1 else ""
    args = {{}}
    if len(words) > 2:
        try:
            args = json.loads(words[2])
        except ValueError:
            args = {{"raw": words[2]}}
    note({{"tool": tool, "args": args}})
    done = subprocess.run([{real!r}, *argv], stdin=sys.stdin, capture_output=True)
    if refused(done.stdout + done.stderr):
        note({{"tool": "(answer)", "args": {{}}, "over_cap": True}})
    sys.stdout.buffer.write(done.stdout)
    sys.stdout.buffer.flush()
    sys.stderr.buffer.write(done.stderr)
    sys.exit(done.returncode)
if words:
    note({{"tool": "(" + " ".join(words) + ")", "args": {{}}}})
    done = subprocess.run([{real!r}, *argv], stdin=sys.stdin)
    sys.exit(done.returncode)

child = subprocess.Popen([{real!r}, *argv], stdin=subprocess.PIPE, stdout=subprocess.PIPE)


def answers():
    for raw in iter(child.stdout.readline, b""):
        if refused(raw):
            note({{"tool": "(answer)", "args": {{}}, "over_cap": True}})
        sys.stdout.buffer.write(raw)
        sys.stdout.buffer.flush()


reader = threading.Thread(target=answers, daemon=True)
reader.start()
for raw in iter(sys.stdin.buffer.readline, b""):
    try:
        message = json.loads(raw)
    except ValueError:
        message = None
    if isinstance(message, dict) and message.get("method") == "tools/call":
        params = message.get("params") or {{}}
        note({{"tool": str(params.get("name", "")), "args": params.get("arguments") or {{}}}})
    child.stdin.write(raw)
    child.stdin.flush()
child.stdin.close()
code = child.wait()
reader.join(timeout=30)
sys.exit(code)
'''

# Runs as ``codebase-memory-mcp`` and can read no index: it records that it was started and fails.
_BROKEN = r'''#!{python}
import json, sys
with open({log!r}, "a", encoding="utf-8") as log:
    log.write(json.dumps({{"tool": "(started)", "args": {{"argv": sys.argv[1:]}}}}) + "\n")
sys.stderr.write("error: the index cannot be read (W2-92 stand-in)\n")
sys.exit(1)
'''


def real_tool():
    return shutil.which(TOOL)


def requests(log):
    """What a stand-in recorded: ``[{"tool", "args", "over_cap"}]``, in order. A request to the tool is named by
    the tool's own question (``trace_path``, ``query_graph``, ...); ``(answer)`` is the tool's refusal over its cap;
    a name in brackets is another start of the binary (``(config set ui_enabled false)``, the server form)."""
    log = Path(log)
    if not log.is_file():
        return []
    out = []
    for line in log.read_text(encoding="utf-8").splitlines():
        entry = json.loads(line)
        out.append({"tool": entry["tool"], "args": entry.get("args") or {}, "over_cap": entry.get("over_cap", False)})
    return out


def _numbers(value, key=""):
    """Every ``(key, number)`` in an argument tree."""
    if isinstance(value, bool):
        return []
    if isinstance(value, (int, float)):
        return [(key, value)]
    if isinstance(value, dict):
        return [pair for k, v in value.items() for pair in _numbers(v, k)]
    if isinstance(value, list):
        return [pair for v in value for pair in _numbers(v, key)]
    return []


GRAPH_QUESTIONS = ("query_graph", "search_graph", "trace_path")


def _strings(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for inner in value.values() for text in _strings(inner)]
    if isinstance(value, list):
        return [text for inner in value for text in _strings(inner)]
    return []


def over_the_cap(entry):
    """A request that asks for more rows than the tool's cap (a row or limit argument, or a ``LIMIT`` in its query),
    or an answer the tool refused for being over it."""
    asked = [number for key, number in _numbers(entry["args"])
             if ("row" in key.lower() or "limit" in key.lower() or key.lower() in ("page_size", "max_results"))
             and number > ROW_CAP]
    in_query = [int(number) for text in _strings(entry["args"])
                for number in re.findall(r"\bLIMIT\s+(\d+)", text, flags=re.IGNORECASE) if int(number) > ROW_CAP]
    return bool(asked) or bool(in_query) or entry["over_cap"]


def whole_graph(entry, symbols):
    """A graph question that names none of the question's symbols: it asks the whole graph (DEC-859 item 1)."""
    if entry["tool"] not in GRAPH_QUESTIONS:
        return False
    text = json.dumps(entry["args"])
    return not any(symbol in text for symbol in symbols)


def names_a_symbol(entry, symbol):
    return entry["tool"] in GRAPH_QUESTIONS and symbol in json.dumps(entry["args"])


# --------------------------------------------------------------------------
# The driver: one child process per batch of calls
# --------------------------------------------------------------------------

_DRIVER = r'''
import importlib, json, sys
from pathlib import Path

request = json.loads(sys.stdin.read())


def decode(value):
    if isinstance(value, dict) and set(value) == {"$path"}:
        return Path(value["$path"])
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

NO_RERANKER = "$absent"
# The forms of the code-graph tool on a child's PATH
ABSENT, REAL, RECORDING, BROKEN = "absent", "real", "recording", "broken"


def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _script(path, text):
    path = Path(path)
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)
    return path


class Api:
    """Calls this worktree's modules and its ``gov`` command line, each in a new process."""

    def __init__(self, workdir):
        self.workdir = Path(workdir)
        for name in ("home", "tmp", "pycache", "elsewhere", "bin", "logs"):
            (self.workdir / name).mkdir(parents=True, exist_ok=True)
        for tool in ("git", "gitleaks", "python3"):   # the base PATH holds these three only
            found = sys.executable if tool == "python3" else shutil.which(tool)
            if found:
                _script(self.workdir / "bin" / tool, f'#!/bin/sh\nexec "{found}" "$@"\n')
        self.driver = self.workdir / "driver.py"
        self.driver.write_text(_DRIVER, encoding="utf-8")
        self.dead_host = f"127.0.0.1:{_free_port()}"
        self.calls = 0
        self.roots = set()   # every root whose code index a call may have reached (its daemon folder, DEC-338)

    def tool_path(self, tool):
        """``(PATH, log)``: the base PATH, with the code-graph tool in the given form; ``log`` records requests."""
        self.calls += 1
        if tool == ABSENT:
            return str(self.workdir / "bin"), None
        place = self.workdir / "logs" / f"call-{self.calls:03d}"
        place.mkdir(parents=True, exist_ok=True)
        log = place / "requests.jsonl"
        if tool == REAL:
            _script(place / TOOL, f'#!/bin/sh\nexec "{real_tool()}" "$@"\n')
        elif tool == RECORDING:
            _script(place / TOOL, _RECORDER.format(python=sys.executable, real=real_tool(), log=str(log),
                                                   refusal=CAP_REFUSAL))
        elif tool == BROKEN:
            _script(place / TOOL, _BROKEN.format(python=sys.executable, log=str(log)))
        else:
            raise ValueError(tool)
        return f"{place}{os.pathsep}{self.workdir / 'bin'}", log

    def env(self, path):
        """Built from nothing: an empty HOME (no reranker), a dead embedder endpoint, offline model hubs."""
        return {"PATH": path, "HOME": str(self.workdir / "home"),
                "TMPDIR": str(self.workdir / "tmp"), "LC_ALL": "C.UTF-8", "GIT_CONFIG_NOSYSTEM": "1",
                "PYTHONPATH": str(SRC), "PYTHONPYCACHEPREFIX": str(self.workdir / "pycache"),
                "OLLAMA_HOST": self.dead_host, "GOV_QUERY_OLLAMA_HOST": self.dead_host,
                "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}

    def run(self, calls, tool=ABSENT):
        """``(records, log)`` of the calls, made one after the other in one new process."""
        path, log = self.tool_path(tool)
        request = {"calls": [{"module": m, "function": f, "args": list(a), "kwargs": dict(k)}
                             for m, f, a, k in calls]}
        done = subprocess.run([sys.executable, str(self.driver)], input=json.dumps(request), env=self.env(path),
                              cwd=str(self.workdir / "elsewhere"), capture_output=True, text=True,
                              timeout=CALL_TIMEOUT_S)
        assert done.returncode == 0, f"the driver failed (exit code {done.returncode}):\n{done.stderr[-4000:]}"
        return json.loads(done.stdout.strip().splitlines()[-1]), log

    def build(self, root, store=True, code=True):
        """The lexical index, the record graph (``store``) and the code index (``code``) of ``root``; no vector."""
        root_arg = {"$path": str(root)}
        calls = [("gov.retrieval.lexical", "refresh", [root_arg], {})]
        if store:
            calls.append(("gov.store", "load", [root_arg], {}))
        out, _ = self.run(calls)
        for record in out:
            assert record["error"] is None, f"the planted project could not be built: {record['error']}"
        if code:
            self.roots.add(str(root))
            out, _ = self.run([("gov.codeintel", "index", [root_arg], {})], tool=REAL)
            assert out[0]["error"] is None, f"the planted code index could not be built: {out[0]['error']}"

    def outcome(self, root, query, tool=RECORDING, **kwargs):
        """``(record, log)``: ``record`` is ``{"value": bundle, "error": None}`` or ``{"value": None, "error": ...}``."""
        kwargs.setdefault("reranker", NO_RERANKER)
        self.roots.add(str(root))
        out, log = self.run([("gov.retrieval.retrieve", "retrieve", [{"$path": str(root)}, query], kwargs)],
                            tool=tool)
        return out[0], log

    def retrieve(self, root, query, tool=RECORDING, **kwargs):
        """``(bundle, requests)``: the bundle of a call that must not raise, and what the code tool was sent."""
        record, log = self.outcome(root, query, tool=tool, **kwargs)
        assert record["error"] is None, f"retrieve raised {record['error']} for {query!r}"
        return record["value"], requests(log) if log else []

    def plain_order(self, root, query):
        """``(chunk_id, path)`` of the plain fused order of the lexical route, the one route of today that answers
        in these projects (no vector is built). The route's list for the fusion is its ``ranked`` list where it gives
        one (W2-13's S2: the exact string's chunks first, then BM25's), else its ``hits``, as ``retrieve`` takes it."""
        root_arg = {"$path": str(root)}
        out, _ = self.run([("gov.retrieval.lexical", "search", [root_arg, query], {"refresh": False})])
        assert out[0]["error"] is None, out[0]["error"]
        hits = out[0]["value"].get("ranked", out[0]["value"]["hits"])
        fused = self.run([("gov.retrieval.fusion", "rrf", [{"lexical": hits}], {})])[0][0]["value"]
        return [(hit["chunk_id"], hit["path"]) for hit in fused]

    def command(self, root, *args, tool=RECORDING):
        """``(completed process, requests)`` of ``gov retrieve --json --root <root> <args>``."""
        path, log = self.tool_path(tool)
        self.roots.add(str(root))
        done = subprocess.run([sys.executable, "-m", "gov.cli.main", "retrieve", "--json", "--root", str(root),
                               *args], capture_output=True, text=True, cwd=str(self.workdir / "elsewhere"),
                              env=self.env(path), timeout=CALL_TIMEOUT_S, stdin=subprocess.DEVNULL)
        return done, requests(log) if log else []

    def daemon_dir(self, root):
        out, _ = self.run([("gov.codeintel", "daemon_dir", [{"$path": str(root)}], {})])
        return out[0]["value"]


def remove_daemon_dirs(api):
    """At the end of the session: each planted root's daemon folder (``gov.codeintel.daemon_dir``, DEC-338), only
    when it holds nothing but the tool's own folder of plain files. The folder above them is left alone."""
    folder = f"cbm-daemon-{os.getuid()}"
    for root in sorted(api.roots):
        try:
            path = Path(api.daemon_dir(root))
            if path.is_symlink() or not path.is_dir() or os.listdir(path) not in ([], [folder]):
                continue
            inside = list(os.scandir(path / folder)) if (path / folder).is_dir() else []
            if (path / folder).is_symlink() or any(not entry.is_file(follow_symlinks=False) for entry in inside):
                continue
            for entry in inside:
                os.unlink(entry.path)
            if (path / folder).is_dir():
                (path / folder).rmdir()
            path.rmdir()
        except (AssertionError, OSError, TypeError, subprocess.TimeoutExpired):
            continue


# --------------------------------------------------------------------------
# Reading a bundle
# --------------------------------------------------------------------------

def items(bundle):
    """The evidence, item for item: ``(chunk_id, path, start_line, end_line)`` in the bundle's order."""
    return [(item.get("chunk_id"), item["path"], item.get("start_line"), item.get("end_line"))
            for item in bundle["evidence"]]


def paths(bundle):
    return [item["path"] for item in bundle["evidence"]]


def holds_text(bundle, text):
    """Whether an evidence item's text, or the file span it cites, holds ``text``."""
    return any(text in str(item.get("text", "")) for item in bundle["evidence"])


def covers(bundle, rel, first, last):
    """Whether an evidence item cites ``rel`` with a span that overlaps lines ``first`` to ``last``."""
    for item in bundle["evidence"]:
        if item["path"] != rel:
            continue
        start, end = item.get("start_line"), item.get("end_line")
        if start is None or end is None or (start <= last and end >= first):
            return True
    return False


def outside_evidence(bundle):
    """The bundle without its evidence: where a route's state and stopping reason are stated."""
    return {key: value for key, value in bundle.items() if key != "evidence"}


CODE_ROUTE_WORDS = ("code", "symbol")
RECORD_ROUTE_WORDS = ("record", "closure", "graph", "store")
TODAYS_FACETS = ("lexical", "semantic")


def route_entries(bundle, route_words):
    """What the bundle states about a route, outside its evidence: each entry of ``facets`` (today's form of a
    route's state, ``{"available", "reason"}``) and of any other mapping or list of per-route stopping reasons whose
    key or text names one of ``route_words``. Today's two routes' own entries are left out."""
    found = []
    for key, value in (bundle.get("facets") or {}).items():
        if key in TODAYS_FACETS:
            continue
        if any(word in f"{key} {json.dumps(value)}".lower() for word in route_words):
            found.append((f"facets.{key}", value))
    for key, value in bundle.items():
        if key in ("evidence", "facets", "stopping_reason") or "stopping" not in key and "route" not in key:
            continue
        inner = value.items() if isinstance(value, dict) else enumerate(value if isinstance(value, list) else [])
        for name, entry in inner:
            if any(word in f"{name} {json.dumps(entry)}".lower() for word in route_words):
                found.append((f"{key}.{name}", entry))
    return found


UNAVAILABLE_WORDS = ("UNAVAILABLE", "MISSING", "UNREADABLE", "NOT_BUILT", "NO INDEX", "NO_INDEX", "NOT FOUND",
                     "NOT_FOUND", "FAILED", "ERROR", "CANNOT", "COULD NOT", "DID NOT", "NO RECORD GRAPH", "NO STORE")


def unavailable(entry):
    """An entry that says its route could not answer, and why: ``available`` false with a reason, or a stopping
    reason in words."""
    if isinstance(entry, dict) and "available" in entry:
        return entry["available"] is False and bool(entry.get("reason"))
    return any(word in json.dumps(entry).upper().replace("-", " ") for word in UNAVAILABLE_WORDS)


def reported_ok(entry):
    """An entry that calls the route fine."""
    if isinstance(entry, dict) and "available" in entry:
        return entry["available"] is True
    return str(entry).strip().upper() in ("OK", "AVAILABLE", "ANSWERED", "COMPLETE", "CLOSURE_COMPLETE")


def projection(bundle):
    """The bundle as today's code shapes it, without its continuation token (its bytes are the implementation's;
    what it continues to is compared instead) and with only today's two facets."""
    out = {key: value for key, value in bundle.items() if key not in ("continuation", "facets")}
    out["facets"] = {key: value for key, value in (bundle.get("facets") or {}).items() if key in TODAYS_FACETS}
    out["evidence"] = items(bundle)
    out["continued"] = bundle.get("continuation") is not None
    return out


# ==========================================================================
# S7 to S10 (DEC-1074 (5), LINK-INTEGRITY §6.1): the stated links
# ==========================================================================
#
# A second planted project, the marina, whose records state each link kind S7 names, in the census's forms
# (docs/research/D4B-link-census.md §1 and its patterns). It is a project of its own, so the harbour's pinned bundles
# (test_w2_92_unchanged.TODAY) do not move. Every record's text uses words no other record and no question holds, so
# a hop's record can reach a bundle only through the hop: the questions name records by their titles (no id in the
# question, so the lexical route's id boost brings nothing), and each case checks that the integrated code's bundle
# does not already hold what the hop must bring.

# The integrated code the S7 to S10 cases are compared with: w2/integrate 8c28aa70fb3f, the tree merged into this
# branch at 436a7520 (DEC-1074 (5), re-pin window 4).
LINKS_BASE = "8c28aa70fb3f88187984f3f9b39479696a41a38a"

# Link types (S7's words)
CITES, OF_TASK, UNDER, SUPERSEDES, AMENDS = "CITES", "OF_TASK", "UNDER", "SUPERSEDES", "AMENDS"
NOT_IN_FORCE = ("PROPOSED", "REJECTED", "WITHDRAWN", "SUPERSEDED")   # S9: marked not in force

# The front-matter records: (id, type, status, title, text, front-matter links)
LK_TICKET, LK_DEPENDENT, LK_MANY, LK_TASK = "DAEO-lk01", "DAEO-lk02", "DAEO-lk03", "DAEO-lk04"
LK_CHECKPOINT, LK_CLOSE, LK_REQ, LK_SPEC, LK_CHANGE = "CKP-0401", "CLS-0401", "REQ-0401", "SPEC-0401", "CHG-0401"
MANY_NOUNS = ("herring", "mackerel", "pilchard", "sprat", "whiting", "haddock", "plaice", "sole", "turbot", "brill",
              "skate", "conger", "pollack", "ling", "hake", "gurnard", "dab", "flounder", "mullet", "bass")
MANY_IDS = tuple(f"DEC-{461 + index}" for index in range(len(MANY_NOUNS)))   # DAEO-lk03's twenty sources
HOP_LIMIT = 12   # S8: one hop brings at most 12 records

FRONT_RECORDS = [
    (LK_TICKET, "task", "open", "Quayside winch overhaul", "Grease the capstan gears and fit new pawl springs.",
     {"sources": ["DEC-411"], "closes": ["DEC-412"]}),
    (LK_DEPENDENT, "task", "open", "Lobster pot tally", "Count the creels stacked behind the fish market.",
     {"depends_on": [LK_TICKET]}),
    (LK_MANY, "task", "open", "Dredger hopper refit", "Reline the spoil chute with hardened plates.",
     {"sources": list(MANY_IDS)}),
    (LK_TASK, "task", "open", "Boathouse gutter repair", "Gutters on the boathouse get new copper troughs.", {}),
    (LK_CHECKPOINT, "checkpoint", "ACTIVE", "Midday progress snapshot", "Half the troughs are fitted; the clamps wait.",
     {"task": LK_TASK}),
    (LK_CLOSE, "close", "ACTIVE", "Final handover memo", "Closed after the last inspection walk.",
     {"task": LK_TASK, "decisions_applied": ["DEC-413"], "requirements_implemented": [LK_REQ]}),
    (LK_REQ, "requirement", "ACTIVE", "Downpipe sizing", "Each downpipe carries a hundred millimetre bore.", {}),
    (LK_SPEC, "specification", "ACTIVE", "Varnish curing method", "Three thin coats, each left a full day.",
     {"decisions": ["DEC-414"]}),
    (LK_CHANGE, "change", "ACTIVE", "Halyard swap diary", "The old halyards come down after the regatta.",
     {"decisions_carried": ["DEC-415"], "decisions_recorded": ["DEC-416"], "decisions_read": ["DEC-417"]}),
]
FRONT_RELS = {
    LK_TICKET: f".tickets/{LK_TICKET}.md", LK_DEPENDENT: f".tickets/{LK_DEPENDENT}.md",
    LK_MANY: f".tickets/{LK_MANY}.md", LK_TASK: f".tickets/{LK_TASK}.md",
    LK_CHECKPOINT: "records/checkpoints/ckp-0401.md", LK_CLOSE: "records/close/cls-0401.md",
    LK_REQ: "records/requirements/req-0401.md", LK_SPEC: "docs/spec/spec-0401.md",
    LK_CHANGE: "records/changes/chg-0401.md",
}

# The register's entries: (id, title, status, the rest of its status line, its decision line, more lines). Each
# entry is "### <id>: <title>", its status line, "- **Decision:** <text>" and its more lines; the decision line
# starts with "- ", so a label's value on the status line ends there, as the census reads it.
_RACKS = [f"- Rack {n:02d}: the dinghies of row {n:02d} stow keel-up on trestles, oars lashed beside them."
          for n in range(1, 46)]   # DEC-432 runs to about 4,000 characters: several chunks of the register
REGISTER_ENTRIES = [
    ("DEC-411", "The kelp harvest limit", "ACCEPTED", "", "Kelp is cut only below the third marker.", []),
    ("DEC-412", "The anchor chain gauge", "ACCEPTED", "", "Chains are measured in fathoms of galvanised links.", []),
    ("DEC-413", "The tern colony fence", "ACCEPTED", "", "A low fence guards the nesting shingle from April.", []),
    ("DEC-414", "The ballast water log", "ACCEPTED", "", "Every tanker records its pumped tonnage on arrival.", []),
    ("DEC-415", "The rope locker inventory", "ACCEPTED", "", "Coils are counted each Monday and tagged by length.", []),
    ("DEC-416", "The barnacle scraping rota", "ACCEPTED", "", "Hulls are scraped in turn during the spring lows.", []),
    ("DEC-417", "The tidepole calibration day", "ACCEPTED", "", "Tidepoles are checked against the benchmark bolt.",
     []),
    # UNDER: DEC-421 is under DEC-422 and DEC-423
    ("DEC-421", "The mooring fee schedule", "ACCEPTED", " · **Under:** DEC-422, DEC-423",
     "Fees rise with the length of the vessel.", []),
    ("DEC-422", "The harbourmaster charter", "ACCEPTED", " · **Under:** DEC-424",
     "The harbourmaster answers to the town council.", []),
    ("DEC-423", "The quay levy principle", "ACCEPTED", "", "A levy funds the upkeep of the stone quay.", []),
    ("DEC-424", "The wharf statute", "ACCEPTED", "", "The borough has owned the wharf since an old statute.", []),
    # AMENDS: DEC-431 changes DEC-432 (stated on the changer); DEC-433 changes DEC-432 (stated on the changed entry)
    ("DEC-431", "The slipway booking rule", "ACCEPTED", " · **Changes:** DEC-432 (item 2)",
     "Launch times are booked a week ahead.", []),
    ("DEC-432", "The dinghy rack allocation", "ACCEPTED", " · **Changed by:** DEC-433 (item 3's wording)",
     "Racks are allotted each season by lot.", _RACKS),
    ("DEC-433", "The fender colour code", "ACCEPTED", "", "Fenders are coloured orange for visitors.", []),
    # AMENDS: **Amends:**
    ("DEC-434", "The bilge pump inspection", "ACCEPTED", " · **Amends:** DEC-435",
     "Pumps are run dry for one minute each quarter.", []),
    ("DEC-435", "The crane lift permit", "ACCEPTED", "", "Lifts above two tonnes need a signed permit.", []),
    # AMENDS: a supersession naming a part (**Supersedes:** with an item) and one in free text; both targets current
    ("DEC-436", "The buoy lantern spacing", "ACCEPTED", " · **Supersedes:** DEC-437 (2)",
     "Lanterns hang every forty metres along the channel.", []),
    ("DEC-437", "The pontoon width standard", "ACCEPTED", "", "Walkways are two metres wide with a kerb.", []),
    ("DEC-438", "The ferry ramp curfew", "ACCEPTED", "",
     "The ramp closes at ten each night. Its weekend clause is superseded by DEC-439.", []),
    ("DEC-439", "The jetty bell signal", "ACCEPTED", "", "The bell rings twice before each departure.", []),
    # SUPERSEDES: ids alone, as **Replaces:** on the status line and as **Supersedes:** on a later line (no edge
    # holds either: the loader reads only a **Supersedes:** on the status line)
    ("DEC-441", "The net drying yard", "ACCEPTED", " · **Replaces:** DEC-442", "Nets dry along the north wall.", []),
    ("DEC-442", "The cellar storage custom", "ACCEPTED", "", "Gear was kept in the cellar under the inn.", []),
    ("DEC-443", "The pier lighting plan", "ACCEPTED", "", "Lights line the pier from end to end.",
     ["- **Supersedes:** DEC-444", "- **Basis of the plan:** the council's survey."]),
    ("DEC-444", "The torch bracket order", "ACCEPTED", "", "Torches were fixed on iron brackets.", []),
    # SUPERSEDES ids alone on the status line: an edge today (loader), kept as it is
    ("DEC-445", "The sail loft lease", "ACCEPTED", " · **Supersedes:** DEC-446", "The loft is let to the rowing crews.",
     []),
    ("DEC-446", "The rigging shed tenancy", "ACCEPTED", "", "Riggers once rented the shed by the gatehouse.", []),
    # S9: statuses not in force, and a whole supersession stated on the changed entry ("Changed by: superseded by")
    ("DEC-451", "The oyster bed survey", "PROPOSED", "", "Divers would map the beds each autumn.", []),
    ("DEC-452", "The gull deterrent trial", "REJECTED", "", "Kites shaped like hawks were to fly over the stalls.", []),
    ("DEC-453", "The cockle licence draw", "WITHDRAWN", "", "Licences were to be drawn from a hat.", []),
    ("DEC-454", "The seawall paint scheme", "SUPERSEDED", " · **Changed by:** superseded by DEC-455",
     "The seawall was to be coated grey.", []),
    ("DEC-455", "The breakwater lamp rota", "ACCEPTED", "", "Keepers take the lamp in weekly turns.", []),
] + [(MANY_IDS[index], f"The {noun} ledger", "ACCEPTED", "", f"Entry for the {noun} trade, kept in ink.", [])
     for index, noun in enumerate(MANY_NOUNS)]

# What S7 must find: (type, source, target), the census's direction (a changer to the changed decision)
STATED = [
    (CITES, LK_TICKET, "DEC-411", "a ticket's sources:"),
    (CITES, LK_TICKET, "DEC-412", "a ticket's closes:"),
    (OF_TASK, LK_CHECKPOINT, LK_TASK, "a checkpoint's task:"),
    (OF_TASK, LK_CLOSE, LK_TASK, "a close record's task:"),
    (CITES, LK_CLOSE, "DEC-413", "a close record's decisions_applied:"),
    (CITES, LK_CLOSE, LK_REQ, "a close record's requirements_implemented:"),
    (CITES, LK_SPEC, "DEC-414", "a spec's decisions:"),
    (CITES, LK_CHANGE, "DEC-415", "a change record's decisions_carried:"),
    (CITES, LK_CHANGE, "DEC-416", "a change record's decisions_recorded:"),
    (CITES, LK_CHANGE, "DEC-417", "a change record's decisions_read:"),
    (UNDER, "DEC-421", "DEC-422", "the register's **Under:** (first id)"),
    (UNDER, "DEC-421", "DEC-423", "the register's **Under:** (second id)"),
    (UNDER, "DEC-422", "DEC-424", "the register's **Under:** (one id)"),
    (AMENDS, "DEC-431", "DEC-432", "the register's **Changes:**"),
    (AMENDS, "DEC-433", "DEC-432", "the register's **Changed by:**"),
    (AMENDS, "DEC-434", "DEC-435", "the register's **Amends:**"),
    (AMENDS, "DEC-436", "DEC-437", "a **Supersedes:** naming a part"),
    (AMENDS, "DEC-439", "DEC-438", "a free-text 'superseded by'"),
    (SUPERSEDES, "DEC-441", "DEC-442", "a **Replaces:** naming ids alone"),
    (SUPERSEDES, "DEC-443", "DEC-444", "a **Supersedes:** naming ids alone, on a later line"),
    (SUPERSEDES, "DEC-455", "DEC-454", "a **Changed by:** superseded by, ids alone"),
] + [(CITES, LK_MANY, target, "a ticket's sources: (one of twenty)") for target in MANY_IDS]
EDGE_ONLY = (SUPERSEDES, "DEC-445", "DEC-446")   # a **Supersedes:** ids alone on the status line: today's edge


def changers():
    """``decision -> the decisions that change it`` (AMENDS and SUPERSEDES toward it, the edge's too)."""
    found = {}
    for kind, source, target, _ in [*STATED, (*EDGE_ONLY, "")]:
        if kind in (AMENDS, SUPERSEDES):
            found.setdefault(target, set()).add(source)
    return found


TEXT_OF = {**{rid: text for rid, _, _, _, text, _ in FRONT_RECORDS},
           **{rid: text for rid, _, _, _, text, _ in REGISTER_ENTRIES}}
TITLE_OF = {**{rid: title for rid, _, _, title, _, _ in FRONT_RECORDS},
            **{rid: title for rid, title, _, _, _, _ in REGISTER_ENTRIES}}
STATUS_OF = {rid: status for rid, _, status, _, _, _ in REGISTER_ENTRIES}
WEATHER = "weather almanac gales"   # the plain pages' words: no record holds them
WEATHER_PAGES = [f"docs/notes/weather-{number:02d}.md" for number in range(1, 4)]


def links_register():
    """The marina's register text, and ``id -> (first line, last line)`` of each entry (1-based, inclusive: its
    heading to the line before the next heading)."""
    lines = ["# Decision register", "", "The decisions of the planted marina, oldest first.", ""]
    spans = {}
    for rid, title, status, rest, decision, more in REGISTER_ENTRIES:
        first = len(lines) + 1
        lines += [f"### {rid}: {title}", f"- **Status:** {status} · **Basis:** OWNER{rest}",
                  f"- **Decision:** {decision}", *more, ""]
        spans[rid] = (first, len(lines))
    return "\n".join(lines), spans


def links_corpus():
    register, _ = links_register()
    files = {"README.md": "# The planted marina\n\nOrdinary words about the moorings' owners.\n",
             ".gitignore": ".gov-runtime/\n", REGISTER: register + "\n"}
    for rid, kind, status, title, text, links in FRONT_RECORDS:
        files[FRONT_RELS[rid]] = _record(rid, kind, status, title, text, **links)
    for number, rel in enumerate(WEATHER_PAGES, 1):
        files[rel] = f"# Weather page {number}\n\nThe {WEATHER} of week {number} are listed here.\n"
    return files


def build_links_project(project):
    """The marina, committed (fixed dates and author: the same commit wherever it is built)."""
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    git(project, "init", "-q", "-b", "main")
    for rel, text in {**links_corpus(), PATH_MAP_REL: path_map()}.items():
        (project / rel).parent.mkdir(parents=True, exist_ok=True)
        (project / rel).write_text(text, encoding="utf-8")
    shutil.copy2(GITLEAKS_TEMPLATE, project / ".gitleaks.toml")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "the planted marina")
    return project


class AtSrc(Api):
    """``Api`` running the ``src/`` given: this worktree's (``SRC``) or the integrated code's (``LINKS_BASE``)."""

    def __init__(self, workdir, src=SRC):
        super().__init__(workdir)
        self.src = Path(src)

    def env(self, path):
        return {**super().env(path), "PYTHONPATH": str(self.src)}

    def value(self, module, function, *args, **kwargs):
        """The value of one call of ``module.function`` in a new process (a ``Path`` argument passed as one)."""
        encode = lambda item: {"$path": str(item)} if isinstance(item, Path) else item  # noqa: E731
        out, _ = self.run([(module, function, [encode(arg) for arg in args], kwargs)])
        assert out[0]["error"] is None, f"{module}.{function} raised {out[0]['error']} ({self.src})"
        return out[0]["value"]

    def bundle(self, root, query, **kwargs):
        """The bundle of one plain question; the code-graph tool off ``PATH`` (the marina has no code)."""
        return self.retrieve(root, query, tool=ABSENT, **kwargs)[0]


def base_src(place):
    """``LINKS_BASE``'s ``src/``, taken from this repository's git into ``place``; its path."""
    archive = subprocess.run(["git", "-C", str(REPO_ROOT), "archive", "--format=tar", LINKS_BASE, "src"],
                             capture_output=True)
    if archive.returncode != 0:
        raise AssertionError(f"the integrated code {LINKS_BASE[:12]} is not in this repository's git: "
                             f"{archive.stderr[-500:]!r}")
    subprocess.run(["tar", "-x", "-C", str(place)], input=archive.stdout, check=True)
    return Path(place) / "src"


# --------------------------------------------------------------------------
# Reading the store's tables (S7): the stated links in a table of their own
# --------------------------------------------------------------------------

def store_tables(root):
    """``table -> rows`` of every table of ``root``'s store, read-only (sqlite's own tables left out)."""
    import sqlite3

    path = Path(root) / ".gov-runtime/store.db"
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        names = [name for (name,) in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        return {name: [tuple(row) for row in connection.execute(f'SELECT * FROM "{name}"')] for name in names}
    finally:
        connection.close()


def _kind(cell):
    return str(cell).strip().upper().replace("-", "_").replace(" ", "_")


def typed(rows, kind, source, target):
    """Whether a row states ``source`` -> ``target`` as ``kind``: a cell that is the type (in any case), a cell that
    is the source and, after it, a cell that is the target (the edges table's order: type, source, target)."""
    for row in rows:
        cells = [str(cell) for cell in row]
        if not any(_kind(cell) == kind for cell in cells) or source not in cells:
            continue
        if target in cells[cells.index(source) + 1:]:
            return True
    return False


def kinds_of(rows, source, target):
    """Every link type a row states for ``source`` -> ``target`` (of S7's five)."""
    return sorted(kind for kind in (CITES, OF_TASK, UNDER, SUPERSEDES, AMENDS) if typed(rows, kind, source, target))


# --------------------------------------------------------------------------
# Reading a bundle's register chunks (S9)
# --------------------------------------------------------------------------

_PLACE_KEYS = ("text", "sha256", "chunk_id", "path", "start_line", "end_line", "batch", "routes", "id")


def entry_of_line(spans, line):
    """The register entry whose lines hold ``line``; None for the register's head."""
    return next((rid for rid, (first, last) in spans.items() if first <= line <= last), None)


def register_items(bundle, spans):
    """``(item, entry id)`` of every evidence item of the register that lies in an entry."""
    return [(item, entry_of_line(spans, item["start_line"])) for item in bundle["evidence"]
            if item["path"] == REGISTER and entry_of_line(spans, item.get("start_line") or 0)]


def _mentions(value, names):
    text = json.dumps(value, default=str)
    return any(name and name in text for name in names)


def what_the_item_says(bundle, item, entry):
    """Everything the bundle tells an agent about this register chunk, as text: its own text and every field it
    carries beyond its place (path, lines, ids, hash, routes, batch), and any entry outside the evidence that names
    the chunk or its entry (a mapping keyed by either, or a listed entry holding either)."""
    told = [str(item.get("text", ""))]
    told += [json.dumps({key: value}, default=str) for key, value in item.items() if key not in _PLACE_KEYS]
    names = (item.get("chunk_id"), entry)

    def walk(value):
        if isinstance(value, dict):
            for key, inner in value.items():
                if key in names:
                    told.append(json.dumps({key: inner}, default=str))
                elif isinstance(inner, (dict, list)):
                    walk(inner)
        elif isinstance(value, list):
            for inner in value:
                if isinstance(inner, dict) and any(inner.get(key) in names for key in inner):
                    told.append(json.dumps(inner, default=str))
                elif isinstance(inner, (dict, list)):
                    walk(inner)

    walk({key: value for key, value in bundle.items() if key != "evidence"})
    return "\n".join(told)


def _says_not_in_force(text):
    """A field ``not_in_force: true`` or ``in_force: false`` (any of ``_ - space`` between the words), else the
    words "not in force" in the text."""
    lower = text.lower()
    field = re.search(r'"not[ _-]?in[ _-]?force"\s*:\s*(true|false)', lower)
    if field:
        return field.group(1) == "true"
    field = re.search(r'"in[ _-]?force"\s*:\s*(true|false)', lower)
    if field:
        return field.group(1) == "false"
    return bool(re.search(r"\bnot in force\b", re.sub(r"[_\-]+", " ", lower)))


def status_faults(bundle, spans):
    """S9's faults in a bundle: each register chunk that does not name its entry's status word, does not name an
    entry that changes it, is not marked not in force while its status is one of ``NOT_IN_FORCE``, or is marked not
    in force while its status is not."""
    faults, changed = [], changers()
    for item, entry in register_items(bundle, spans):
        told, status = what_the_item_says(bundle, item, entry), STATUS_OF[entry]
        where = f"{entry}'s chunk at lines {item['start_line']}-{item['end_line']}"
        if not re.search(rf"(?<![A-Z_]){status}(?![A-Z_])", told):
            faults.append(f"{where} does not name its status {status}")
        missing = sorted(rid for rid in changed.get(entry, ()) if not re.search(rf"{rid}(?!\d)", told))
        if missing:
            faults.append(f"{where} does not name the entries that change it: {missing}")
        marked = _says_not_in_force(told)
        if status in NOT_IN_FORCE and not marked:
            faults.append(f"{where} is {status} and not marked not in force")
        if status not in NOT_IN_FORCE and marked:
            faults.append(f"{where} is {status} and marked not in force")
    return faults
