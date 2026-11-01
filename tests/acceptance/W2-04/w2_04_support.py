"""Support code for the W2-04 acceptance tests (DAEO-u4oz; standard library and PyYAML only).

W2-04 makes ``gov context`` bounded and reproducible: the packet holds its ceiling with the ticket's own text in it,
refuses by name when the mandatory inputs alone are over it, names each decision by its entry's own hash, gives one
hash across builds, stacks the supplementary evidence from ranked batches and names what it left for a further batch
(DEC-860). The tests use only the public forms the specification fixes (README, "The interfaces"):

- ``gov context <ticket> --json [--budget N] [--brief] [--dry-run]`` (``python3 -m gov.cli.main``), its envelope;
- ``gov.context.context(root, ticket, ...)``, called in a child process;
- ``python3 -m gov.context.context_check``, run in a project root;
- ``gov.store.load``, ``gov.records.records`` (a register entry's ``span`` and ``content_hash``, W2-03) and
  ``gov.retrieval.lexical.refresh``, to build and read what a context reads.

**The code under test (DEC-732):** every child process gets ``Api.env()``, whose ``PYTHONPATH`` ends with the
``src/`` of the tree this file stands in (``SRC``, found from this file's own place), so that the same files, merged
into the ticket's worktree, exercise that worktree's code.

Every project is a temporary git repository built from nothing under pytest's ``tmp_path``; the only files of this
repository that are read are the path map and the template's gitleaks rules (single named files). No vector is built,
the embedder's address is a dead local port, ``HOME`` is empty (no reranker), and the network is not used. The
stand-ins in ``_HOOK`` (README, "The stand-ins") are switched on per process by environment variables.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import site
import socket
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC = REPO_ROOT / "src"
PATH_MAP_REL = "governance/project/path-map.yaml"
GITLEAKS_TEMPLATE = REPO_ROOT / "template" / ".gitleaks.toml"
REGISTER_REL = "docs/DECISION_REGISTER.md"
STORE_REL = ".gov-runtime/store.db"
SCRATCH_REL = ".gov-runtime/scratch"
CALL_TIMEOUT_S = 300.0

# ---- the public forms the specification fixes (S1 to S10)
DEFAULT_CEILING = 6000
TOKEN_CHARS = 4
OVER_CEILING = "CONTEXT_OVER_CEILING"
BLOCKED = "BLOCKED"
K_TICKET_TEXT = "ticket_text"
K_QUERY = "supplementary_query"
K_FURTHER = "further_batch"
K_SUPPLEMENTARY = "supplementary"
K_MANDATORY = "mandatory"
K_DROPPED = "dropped"
K_HASH = "hash"
K_TOKENS = "tokens"
K_BUDGET = "budget"
DETAILS = ("ticket", "limit", "mandatory_tokens")
INDEX_UNAVAILABLE = "index unavailable"
EMPTY_SHA = hashlib.sha256(b"").hexdigest()


def tokens(text):
    """The packet's own count: the text's length in characters divided by 4, rounded up (S1)."""
    return -(-len(text) // TOKEN_CHARS)


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# --------------------------------------------------------------------------
# Files of a planted project
# --------------------------------------------------------------------------

def record(record_id, kind, status, body, **more):
    """A record file with frontmatter (the store's record form, W1-10)."""
    front = {"id": record_id, "type": kind, "status": status, "state_class": "AUTHORITATIVE",
             "title": f"The record {record_id}", **more}
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + f"---\n\n# {record_id}\n\n{body}\n"


def ticket(ticket_id, title, sources, kpis=("The placeholder holds.",), failure=("The placeholder fails.",),
           body="The ticket's body.", **more):
    """A ticket file: its frontmatter (title, KPI lines, sources) and its body."""
    front = {"id": ticket_id, "type": "ticket", "status": "in_progress", "state_class": "AUTHORITATIVE",
             "title": title, "role": "engineer", "allowed_paths": ["src/placeholder/**"],
             "kpis": {"success": list(kpis), "failure": list(failure)}, "sources": list(sources), **more}
    text = yaml.safe_dump(front, sort_keys=False, allow_unicode=True, width=100_000)
    return f"---\n{text}---\n\n# {ticket_id} {title}\n\n{body}\n"


def entry(entry_id, title, body, status="ACCEPTED · **Basis:** OWNER"):
    """One register entry: its heading, its status line first, then its text (the store's entry form, W2-03)."""
    return f"### {entry_id} — {title}\n- **Status:** {status}\n\n{body}\n"


def register(*entries, preamble="# Decision register\n\nThe decisions of the planted harbour, oldest first.\n"):
    return preamble + "\n" + "\n".join(entries)


# ---- the ledger: much matching evidence of two sizes, for the ceiling under pressure (S1) and the batches (S7)
# Every page holds the ticket's title and its KPI line verbatim, each on a line of its own, so a query built from
# the title, from the KPI lines or from their words finds every page (the lexical route matches a line's exact text).

LEDGER_TICKET = "TK-W204-LEDGER"
LEDGER_TITLE = "Beacon ledger"
LEDGER_LINE = "Every beacon ledger line is kept."
LEDGER_PAGES = 48
LEDGER_LARGE_EVERY = 4
CHARTER_ID = "CHARTER-W204"
CHARTER_TEXT = "Every agent starts from a compiled context packet under its ceiling."


def ledger_page(number):
    large = number % LEDGER_LARGE_EVERY == LEDGER_LARGE_EVERY - 1
    filler = " ".join(f"At hour {hour} the keeper wrote the wind, the swell and the state of the lamp."
                      for hour in range(12)) if large else ""
    return f"# {LEDGER_TITLE}, page {number:02d}\n\n{LEDGER_LINE}\n\nPage {number:02d} of the ledger. {filler}\n"


def ledger_files(pages=LEDGER_PAGES):
    files = {f"docs/ledger/page-{number:02d}.md": ledger_page(number) for number in range(pages)}
    files["docs/charter/charter.md"] = record(CHARTER_ID, "charter", "ACTIVE", CHARTER_TEXT)
    files[f".tickets/{LEDGER_TICKET}.md"] = ticket(LEDGER_TICKET, LEDGER_TITLE, [CHARTER_ID], kpis=(LEDGER_LINE,),
                                                   failure=("A page of the ledger is lost.",))
    return files


def ledger_paths(items):
    """The ledger pages among ``items``, in their order."""
    return [item["path"] for item in items if str(item.get("path", "")).startswith("docs/ledger/")]


def filler_entries(first, count, size):
    """``count`` register entries from ``DEC-<first>`` on, each about ``size`` characters, none of them cited."""
    sentence = "The filler decision keeps the register as large as a real one, and no ticket here cites it. "
    body = (sentence * (size // len(sentence) + 1))[:size]
    return [entry(f"DEC-{number:03d}", f"Filler {number}", body) for number in range(first, first + count)]


# --------------------------------------------------------------------------
# git and the project
# --------------------------------------------------------------------------

DATE = "2026-11-01T12:{minute:02d}:00+00:00"


class Project:
    """A temporary git repository: files written, then committed, one commit at a time."""

    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.minute = 0
        self.git("init", "-q", "-b", "main")

    def git(self, *args):
        self.minute += 1
        date = DATE.format(minute=self.minute % 60)
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.root.parent), "LC_ALL": "C",
               "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
               "GIT_AUTHOR_NAME": "W2-04 tests", "GIT_AUTHOR_EMAIL": "w2-04@example.invalid",
               "GIT_COMMITTER_NAME": "W2-04 tests", "GIT_COMMITTER_EMAIL": "w2-04@example.invalid",
               "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date}
        done = subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True, env=env)
        assert done.returncode == 0, f"git {' '.join(args)} failed in {self.root}:\n{done.stderr}"
        return done.stdout

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def write_all(self, files):
        for rel, text in files.items():
            self.write(rel, text)

    def commit(self, subject="a change"):
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "--no-gpg-sign", "-m", subject)
        return self.git("rev-parse", "HEAD").strip()

    def text(self, rel):
        return (self.root / rel).read_text(encoding="utf-8")


def path_map(register_rel=None):
    """This repository's path map, its namespaces replaced by one that classes everything as governance memory without
    vectors, its authority block left out, and ``register_rel`` named as the register (none when None)."""
    document = yaml.safe_load((REPO_ROOT / PATH_MAP_REL).read_text(encoding="utf-8"))
    document.pop("retrieval_authority", None)
    document.pop("decision_register", None)
    if register_rel is not None:
        document["decision_register"] = register_rel
    document["namespaces"] = {"everything": {
        "paths": ["**"], "memory_class": "governance", "sensitivity": "internal",
        "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                            "independent-auditor", "research"],
        "retention": "kept in git history", "export_policy": "allowed", "provenance": "written by the W2-04 tests",
        "deletion_rebuild": "authoritative; restored from git only", "embedding_policy": "not embedded"}}
    return yaml.safe_dump(document, sort_keys=False, allow_unicode=True)


def build_project(root, files, register_text=None):
    """A committed project: README, gitleaks rules, the path map (naming the register when there is one), the register
    and ``files``."""
    project = Project(root)
    project.write("README.md", "# The planted harbour\n\nOrdinary text about the harbour.\n")
    project.write(".gitignore", ".gov-runtime/\n")
    if GITLEAKS_TEMPLATE.is_file():
        shutil.copy2(GITLEAKS_TEMPLATE, project.root / ".gitleaks.toml")
    project.write(PATH_MAP_REL, path_map(REGISTER_REL if register_text is not None else None))
    if register_text is not None:
        project.write(REGISTER_REL, register_text)
    project.write_all(files)
    project.commit("the planted harbour")
    return project


# --------------------------------------------------------------------------
# The stand-ins (README, "The stand-ins"), a sitecustomize first on PYTHONPATH when a case asks for one
# --------------------------------------------------------------------------

_HOOK = r'''
"""W2-04's stand-ins (acceptance tests only): what a process opens, the retrieval's calls and order, a live semantic
route. Each is on only where its environment variable is set."""
import atexit
import json
import os
import sys

_WATCH = os.environ.get("W204_WATCH")
if _WATCH:
    _target = os.path.realpath(_WATCH)
    _name = os.path.relpath(_target, os.environ.get("W204_WATCH_ROOT", "/"))
    _reads = []

    def _audit(event, args):
        if event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
            try:
                if os.path.realpath(os.fsdecode(args[0])) == _target:
                    _reads.append("open")
            except Exception:
                pass
        elif event == "subprocess.Popen" and len(args) > 1:
            if any(_name in str(part) for part in (args[1] or ())):
                _reads.append("subprocess")

    sys.addaudithook(_audit)
    atexit.register(lambda: sys.stderr.write("\nW204-READS " + json.dumps(_reads) + "\n"))

_MODE, _LOG = os.environ.get("W204_MODE"), os.environ.get("W204_LOG")
if _MODE and _LOG:
    import gov.retrieval.retrieve as _entry

    _real = _entry.retrieve

    def _ties_reversed(items):
        """The items in the same places, except that each group of items with the same text (a tie) is reversed."""
        groups = {}
        for index, item in enumerate(items):
            groups.setdefault(item.get("text"), []).append(index)
        out = list(items)
        for places in groups.values():
            for place, source in zip(places, reversed(places)):
                out[place] = items[source]
        return out

    def retrieve(*args, **kwargs):
        bundle = _real(*args, **kwargs)
        evidence = list(bundle.get("evidence") or [])
        out = dict(bundle)
        if _MODE == "ties-reversed":
            out["evidence"] = _ties_reversed(evidence)
        line = {"pid": os.getpid(), "query": args[1] if len(args) > 1 else kwargs.get("query"),
                "ticket": kwargs.get("ticket"), "batch_size": kwargs.get("batch_size"),
                "continued": kwargs.get("continuation") is not None,
                "in": [[item.get("id"), item.get("path")] for item in evidence],
                "out": [[item.get("id"), item.get("path")] for item in out["evidence"]]}
        with open(os.path.join(_LOG, "calls.jsonl"), "a", encoding="utf-8") as handle:
            handle.write(json.dumps(line) + "\n")
        return out

    _entry.retrieve = retrieve

    if _MODE == "semantic-live":
        import gov.retrieval.lexical as _lexical
        import gov.retrieval.semantic as _semantic

        _only = os.environ.get("W204_SEMANTIC_PATH", "")

        def search(root, query, refresh=True):
            hits = [{"chunk_id": chunk["chunk_id"], "path": chunk["path"], "start_line": chunk["start_line"],
                     "end_line": chunk["end_line"], "parent_id": chunk.get("parent_id"), "distance": 0.125}
                    for chunk in _lexical.chunks(root) if chunk["path"] == _only]
            return {"available": True, "facet": _semantic.FACET, "state": "AVAILABLE", "reason": None, "hits": hits}

        _semantic.search = search
'''


def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


_DRIVER = r'''
import importlib, json, sys
from pathlib import Path

out = []
for call in json.loads(sys.stdin.read()):
    try:
        function = getattr(importlib.import_module(call["module"]), call["function"])
    except (ImportError, AttributeError) as exc:
        out.append({"missing": f"{call['module']}.{call['function']} cannot be imported: {exc}"})
        continue
    try:
        out.append({"value": function(Path(call["root"]), *call["args"], **call["kwargs"])})
    except Exception as exc:
        out.append({"error": {"type": type(exc).__name__, "code": getattr(exc, "code", None),
                              "message": str(getattr(exc, "message", exc)),
                              "details": getattr(exc, "details", None)}})
print("\n" + json.dumps(out, default=repr))
'''


class Answer:
    def __init__(self, argv, done):
        self.argv, self.returncode, self.stdout, self.stderr = argv, done.returncode, done.stdout, done.stderr

    def describe(self):
        return (f"{' '.join(map(str, self.argv))}\nexit {self.returncode}\nstdout: {self.stdout[-3000:]}\n"
                f"stderr: {self.stderr[-3000:]}")

    @property
    def envelope(self):
        try:
            data = json.loads(self.stdout)
        except ValueError:
            raise AssertionError(f"the output is not one JSON envelope\n{self.describe()}") from None
        assert isinstance(data, dict) and "ok" in data, f"the output is not an envelope\n{self.describe()}"
        return data

    @property
    def packet(self):
        data = self.envelope
        assert self.returncode == 0 and data["ok"] is True, f"gov context refused\n{self.describe()}"
        assert isinstance(data.get("result"), dict), f"the envelope's result is not a map\n{self.describe()}"
        return data["result"]

    @property
    def error(self):
        data = self.envelope
        return data.get("error") if data.get("ok") is False else None

    def reads(self):
        """What the watch stand-in saw: one word per read of the watched file."""
        found = re.findall(r"^W204-READS (\[.*\])$", self.stderr, flags=re.MULTILINE)
        assert found, f"the watch stand-in reported nothing (it did not run)\n{self.describe()}"
        return json.loads(found[-1])


class Api:
    """Calls this tree's modules and its ``gov`` command line, each in a new process."""

    def __init__(self, workdir):
        self.workdir = Path(workdir)
        for name in ("home", "tmp", "pycache", "elsewhere", "bin", "hook", "log"):
            (self.workdir / name).mkdir(parents=True, exist_ok=True)
        for tool, found in (("python3", sys.executable), ("git", shutil.which("git")),
                            ("gitleaks", shutil.which("gitleaks"))):
            if found:
                wrapper = self.workdir / "bin" / tool
                wrapper.write_text(f'#!/bin/sh\nexec "{found}" "$@"\n', encoding="utf-8")
                wrapper.chmod(0o755)
        (self.workdir / "hook" / "sitecustomize.py").write_text(_HOOK, encoding="utf-8")
        self.driver = self.workdir / "driver.py"
        self.driver.write_text(_DRIVER, encoding="utf-8")
        self.dead_host = f"127.0.0.1:{_free_port()}"

    def has_gitleaks(self):
        return (self.workdir / "bin" / "gitleaks").exists()

    def env(self, mode=None, watch=None, **extra):
        """This tree's ``src/`` on ``PYTHONPATH`` (after the stand-ins' folder when one is asked for); an empty HOME,
        a dead embedder address, offline."""
        hooked = mode is not None or watch is not None
        found = {"PATH": f"{self.workdir / 'bin'}:/usr/bin:/bin", "HOME": str(self.workdir / "home"),
                 "TMPDIR": str(self.workdir / "tmp"), "LC_ALL": "C.UTF-8", "GIT_CONFIG_NOSYSTEM": "1",
                 "GIT_CONFIG_GLOBAL": os.devnull,
                 "PYTHONPATH": os.pathsep.join(([str(self.workdir / "hook")] if hooked else []) + [str(SRC)]),
                 "PYTHONPYCACHEPREFIX": str(self.workdir / "pycache"),
                 "OLLAMA_HOST": self.dead_host, "GOV_QUERY_OLLAMA_HOST": self.dead_host,
                 "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}
        if site.ENABLE_USER_SITE:
            found["PYTHONUSERBASE"] = site.getuserbase()
        if mode is not None:
            found.update({"W204_MODE": mode, "W204_LOG": str(self.workdir / "log")})
        if watch is not None:
            found.update({"W204_WATCH": str(watch[0] / watch[1]), "W204_WATCH_ROOT": str(watch[0])})
        found.update(extra)
        return found

    # ---- the retrieval stand-in's log

    def reset_log(self):
        shutil.rmtree(self.workdir / "log", ignore_errors=True)
        (self.workdir / "log").mkdir()

    def calls(self):
        path = self.workdir / "log" / "calls.jsonl"
        if not path.is_file():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    # ---- in-process calls, each batch in one new process

    def batch(self, calls, env=None):
        """``[(module, function, root, args, kwargs), ...]`` in one process."""
        request = [{"module": m, "function": f, "root": str(r), "args": list(a), "kwargs": dict(k)}
                   for m, f, r, a, k in calls]
        what = ", ".join(dict.fromkeys(f"{m}.{f}" for m, f, *_ in calls))
        try:
            done = subprocess.run([sys.executable, str(self.driver)], input=json.dumps(request),
                                  env=env or self.env(), cwd=str(self.workdir / "elsewhere"), capture_output=True,
                                  text=True, timeout=CALL_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"{what} did not end within {CALL_TIMEOUT_S:.0f} s") from None
        assert done.returncode == 0, f"{what} failed (exit code {done.returncode}):\n{done.stderr[-4000:]}"
        out = json.loads(done.stdout.strip().splitlines()[-1])
        for record_ in out:
            assert "missing" not in record_, record_["missing"]
        return out

    def build(self, root, index=True):
        """The lexical index (unless ``index`` is false) and the store of ``root``; no vector."""
        steps = ([("gov.retrieval.lexical", "refresh", root, (), {})] if index else []) + \
                [("gov.store", "load", root, (), {})]
        for record_ in self.batch(steps):
            assert "value" in record_, f"the planted project could not be built: {record_}"

    def load(self, root):
        (loaded,) = self.batch([("gov.store", "load", root, (), {})])
        assert "value" in loaded, f"gov.store.load refused: {loaded}"

    def records(self, root):
        """``id -> record`` of the store's records (``gov.records.records``)."""
        (listed,) = self.batch([("gov.records", "records", root, (), {})])
        assert "value" in listed, f"gov.records.records refused: {listed}"
        found = {}
        for record_ in listed["value"]:
            found.setdefault(record_["id"], record_)
        return found

    def context_calls(self, root, ticket_id, times=1, env=None, **kwargs):
        """``gov.context.context(root, ticket_id, **kwargs)`` ``times`` times in one process: each value or error."""
        return self.batch([("gov.context", "context", root, (ticket_id,), kwargs)] * times, env=env)

    # ---- the command line

    def gov(self, root, *args, env=None):
        """``gov context <args> --json --root <root>``, from a folder outside the project."""
        argv = [sys.executable, "-m", "gov.cli.main", "context", *map(str, args), "--json", "--root", str(root)]
        try:
            done = subprocess.run(argv, cwd=str(self.workdir / "elsewhere"), env=env or self.env(),
                                  capture_output=True, text=True, timeout=CALL_TIMEOUT_S, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"gov context {' '.join(map(str, args))} did not end within {CALL_TIMEOUT_S:.0f} s") \
                from None
        return Answer(["gov", "context", *args], done)

    def context_check(self, root, env=None):
        """The context-reproducibility check: ``python3 -m gov.context.context_check`` in the project root."""
        argv = [sys.executable, "-m", "gov.context.context_check"]
        try:
            done = subprocess.run(argv, cwd=str(root), env=env or self.env(), capture_output=True, text=True,
                                  timeout=CALL_TIMEOUT_S, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"the context check did not end within {CALL_TIMEOUT_S:.0f} s") from None
        return Answer(["python3", "-m", "gov.context.context_check"], done)


# --------------------------------------------------------------------------
# Reading packets
# --------------------------------------------------------------------------

def item_of(packet, record_id):
    found = [item for item in packet[K_MANDATORY] if item.get("id") == record_id]
    assert len(found) == 1, f"{record_id} is not one mandatory input of the packet: {packet[K_MANDATORY]}"
    return found[0]


def marked_not_read(packet, record_id):
    """Whether the packet lists ``record_id`` anywhere as not read (``"read": false``)."""
    def walk(value):
        if isinstance(value, dict):
            if value.get("id") == record_id and value.get("read") is False:
                return True
            return any(walk(inner) for inner in value.values())
        if isinstance(value, list):
            return any(walk(inner) for inner in value)
        return False
    return walk(packet)


def supplementary_tokens(packet):
    return sum(int(item["tokens"]) for item in packet[K_SUPPLEMENTARY])


def assert_holds_its_ceiling(packet, ticket_text):
    """Every packet returned with ``ok: true`` (S1): the ticket's own text whole and verbatim, ``tokens`` equal to
    ``budget.used``, at most ``budget.limit``, and counting at least the ticket's text and the supplementary items."""
    assert packet.get(K_TICKET_TEXT) == ticket_text, (
        f"the packet does not carry the ticket's own text whole and verbatim under `{K_TICKET_TEXT}`: "
        f"{'absent' if K_TICKET_TEXT not in packet else repr(str(packet[K_TICKET_TEXT])[:200])}")
    used, limit = packet[K_BUDGET]["used"], packet[K_BUDGET]["limit"]
    assert packet[K_TOKENS] == used, f"tokens {packet[K_TOKENS]} is not budget.used {used}"
    assert packet[K_TOKENS] <= limit, f"the packet is over its ceiling: tokens {packet[K_TOKENS]} > limit {limit}"
    floor = tokens(ticket_text) + supplementary_tokens(packet)
    assert packet[K_TOKENS] >= floor, (
        f"tokens {packet[K_TOKENS]} does not count the ticket's own text ({tokens(ticket_text)}) and the "
        f"supplementary items ({supplementary_tokens(packet)})")


def assert_refused_over_ceiling(answer, ticket_id, limit):
    """S2: ``ok: false``, ``CONTEXT_OVER_CEILING``, a non-zero exit, a message that names the ticket, the ceiling and
    the mandatory size, and the details."""
    envelope = answer.envelope
    assert envelope["ok"] is False, (
        f"the mandatory inputs are over the ceiling of {limit} and gov context reported ok: true with "
        f"tokens {(envelope.get('result') or {}).get(K_TOKENS)}\n{answer.describe()[:1500]}")
    error = envelope.get("error") or {}
    assert error.get("code") == OVER_CEILING, f"expected {OVER_CEILING}, got {error.get('code')!r}\n{answer.describe()}"
    assert answer.returncode != 0, f"the refusal exits 0\n{answer.describe()}"
    details = error.get("details") or {}
    for key in DETAILS:
        assert key in details, f"the refusal's details have no `{key}`: {details}"
    assert details["ticket"] == ticket_id and details["limit"] == limit, details
    message = error.get("message") or ""
    for named in (ticket_id, str(limit), str(details["mandatory_tokens"])):
        assert named in message, f"the refusal's message does not name {named!r}: {message!r}"
    return details


def ids_paths(items):
    return [(item.get("id"), item.get("path")) for item in items]
