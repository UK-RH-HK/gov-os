"""Support code for the W2-183 acceptance tests (DAEO-href; standard library and PyYAML only).

W2-183 gives ``gov close`` a context packet built at the project's setting ``budgets.close_context_tokens`` (in
``governance/project/facts.yaml``) and caps ``gov context``'s supplementary block at 6,000 tokens whatever ``--budget``
is passed (DEC-1165, DEC-1027, DEC-860, CAP-15.d). The tests use only the public forms the ticket's interface fixes:

- ``gov context <ticket> --json [--budget N]`` (``python3 -m gov.cli.main``), its envelope;
- ``gov.close.command._build_context(root, ticket)`` (the close's context step), called in a child process on a real
  stand-in: it returns the packet or raises a ``_Finding`` (code, message, details);
- ``gov.context.close_budget(root)`` and ``gov.context.SUPPLEMENTARY_CAP`` (imported inside the case that uses
  them, so that a tree without them reds that case and no other);
- ``gov.store.load`` and ``gov.retrieval.lexical.refresh``, to build what a context reads.

Every project is a temporary git repository built from nothing under pytest's ``tmp_path``/``tmp_path_factory``
(never this repository's store or ``.gov-runtime/``). No vector is built, the embedder's address is a dead local port,
``HOME`` is empty (no reranker), the network is not used, and no model runs. The only files of this repository that are
read are the path map and the template's gitleaks rules (single named files).
"""

from __future__ import annotations

import contextlib
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
FACTS_REL = "governance/project/facts.yaml"
CALL_TIMEOUT_S = 300.0

# ---- the public forms the ticket fixes
DEFAULT_CEILING = 6000
SUPPLEMENTARY_CAP = 6000
CLOSE_SETTING = "close_context_tokens"
CLOSE_KEY = f"budgets.{CLOSE_SETTING}"
CLOSE_VALUE = 65536
OVER_CEILING = "CONTEXT_OVER_CEILING"
SETTING_INVALID = "CONTEXT_SETTING_INVALID"
CONTEXT_FAILED = "CONTEXT_FAILED"
TOKEN_CHARS = 4
K_TICKET_TEXT = "ticket_text"
K_SUPPLEMENTARY = "supplementary"
K_MANDATORY = "mandatory"
K_HASH = "hash"
K_TOKENS = "tokens"
K_BUDGET = "budget"
DETAILS = ("ticket", "limit", "mandatory_tokens")


def tokens(text):
    """The packet's own count: the text's length in characters divided by 4, rounded up (DEC-083)."""
    return -(-len(text) // TOKEN_CHARS)


def sha256_file(path):
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# --------------------------------------------------------------------------
# Files of a stand-in project
# --------------------------------------------------------------------------

def record(record_id, kind, status, body, **more):
    """A record file with frontmatter (the store's record form)."""
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


def paragraphs(prefix, count):
    """``count`` fixed lines of about 22 tokens each (no time, no randomness: what is hashed is the same each run)."""
    return "\n".join(f"{prefix} {n}: the harbour master reads every line of this text before the tide turns."
                     for n in range(count))


# ---- the stand-ins' ids and sizes
CHARTER_ID = "CHARTER-W183"
CHARTER_REL = "docs/charter/charter.md"
CHARTER_TEXT = "Every agent starts from a compiled context packet under its ceiling."

SMALL_TICKET = "TK-W183-SMALL"
BIG_TICKET = "TK-W183-BIG"
BIG_SOURCE_ID = "ADR-W183-LOGBOOK"
BIG_SOURCE_REL = "docs/adr/logbook.md"
# The big ticket: its own text about 6,300 tokens and its one mandatory source about 4,000, about 10,000 in all.
BIG_TICKET_LINES = 285
BIG_SOURCE_LINES = 180

LEDGER_TICKET = "TK-W183-LEDGER"
LEDGER_TITLE = "Beacon ledger"
LEDGER_LINE = "Every beacon ledger line is kept."
# 80 matching pages of about 300 tokens each: about 24,000 tokens of supplementary evidence, four times the cap.
LEDGER_PAGES = 80


def ledger_page(number):
    filler = " ".join(f"At hour {hour} the keeper wrote the wind, the swell and the state of the lamp."
                      for hour in range(14))
    return f"# {LEDGER_TITLE}, page {number:02d}\n\n{LEDGER_LINE}\n\nPage {number:02d} of the ledger. {filler}\n"


def small_files():
    return {
        CHARTER_REL: record(CHARTER_ID, "charter", "ACTIVE", CHARTER_TEXT),
        f".tickets/{SMALL_TICKET}.md": ticket(SMALL_TICKET, "The small ticket", [CHARTER_ID]),
    }


def big_files():
    return {
        CHARTER_REL: record(CHARTER_ID, "charter", "ACTIVE", CHARTER_TEXT),
        BIG_SOURCE_REL: record(BIG_SOURCE_ID, "decision", "ACTIVE", paragraphs("Logbook entry", BIG_SOURCE_LINES)),
        f".tickets/{BIG_TICKET}.md": ticket(BIG_TICKET, "The big ticket", [CHARTER_ID, BIG_SOURCE_ID],
                                            body=paragraphs("Paragraph", BIG_TICKET_LINES)),
    }


def ledger_files(pages=LEDGER_PAGES):
    files = {f"docs/ledger/page-{number:02d}.md": ledger_page(number) for number in range(pages)}
    files[CHARTER_REL] = record(CHARTER_ID, "charter", "ACTIVE", CHARTER_TEXT)
    files[f".tickets/{LEDGER_TICKET}.md"] = ticket(LEDGER_TICKET, LEDGER_TITLE, [CHARTER_ID], kpis=(LEDGER_LINE,),
                                                   failure=("A page of the ledger is lost.",))
    return files


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
               "GIT_AUTHOR_NAME": "W2-183 tests", "GIT_AUTHOR_EMAIL": "w2-183@example.invalid",
               "GIT_COMMITTER_NAME": "W2-183 tests", "GIT_COMMITTER_EMAIL": "w2-183@example.invalid",
               "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date}
        done = subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True, env=env)
        assert done.returncode == 0, f"git {' '.join(args)} failed in {self.root}:\n{done.stderr}"
        return done.stdout

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def commit(self, subject="a change"):
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "--no-gpg-sign", "-m", subject)
        return self.git("rev-parse", "HEAD").strip()

    def text(self, rel):
        return (self.root / rel).read_text(encoding="utf-8")

    # ---- the project's setting: ``budgets.close_context_tokens`` in governance/project/facts.yaml

    def set_facts(self, document):
        """Write facts.yaml from ``document`` (a map), or remove the file when ``document`` is None."""
        path = self.root / FACTS_REL
        if document is None:
            path.unlink(missing_ok=True)
        else:
            self.write(FACTS_REL, yaml.safe_dump(document, sort_keys=False))

    def set_close_budget(self, value):
        self.set_facts({"project": {"name": "the planted harbour"}, "budgets": {CLOSE_SETTING: value}})

    @contextlib.contextmanager
    def setting(self, value=None, *, facts="setting"):
        """facts.yaml with the close's setting at ``value`` (``facts="setting"``), with a ``budgets:`` that does not
        hold the key (``"no key"``), with no ``budgets:`` at all (``"no budgets"``), or no facts.yaml (``"no file"``);
        the project's own state restored afterwards."""
        path = self.root / FACTS_REL
        before = path.read_bytes() if path.is_file() else None
        try:
            if facts == "setting":
                self.set_close_budget(value)
            elif facts == "no key":
                self.set_facts({"project": {"name": "the planted harbour"}, "budgets": {"other_budget": 2500}})
            elif facts == "no budgets":
                self.set_facts({"project": {"name": "the planted harbour"}})
            elif facts == "no file":
                self.set_facts(None)
            else:
                raise AssertionError(f"unknown facts form {facts!r}")
            yield self
        finally:
            if before is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(before)


def path_map():
    """This repository's path map, its namespaces replaced by one that classes everything as governance memory without
    vectors, its authority block and register left out."""
    document = yaml.safe_load((REPO_ROOT / PATH_MAP_REL).read_text(encoding="utf-8"))
    document.pop("retrieval_authority", None)
    document.pop("decision_register", None)
    document["namespaces"] = {"everything": {
        "paths": ["**"], "memory_class": "governance", "sensitivity": "internal",
        "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                            "independent-auditor", "research"],
        "retention": "kept in git history", "export_policy": "allowed", "provenance": "written by the W2-183 tests",
        "deletion_rebuild": "authoritative; restored from git only", "embedding_policy": "not embedded"}}
    return yaml.safe_dump(document, sort_keys=False, allow_unicode=True)


def build_project(root, files):
    """A committed project: README, gitleaks rules, the path map and ``files``."""
    project = Project(root)
    project.write("README.md", "# The planted harbour\n\nOrdinary text about the harbour.\n")
    project.write(".gitignore", ".gov-runtime/\n")
    if GITLEAKS_TEMPLATE.is_file():
        shutil.copy2(GITLEAKS_TEMPLATE, project.root / ".gitleaks.toml")
    project.write(PATH_MAP_REL, path_map())
    for rel, text in files.items():
        project.write(rel, text)
    project.commit("the planted harbour")
    return project


# --------------------------------------------------------------------------
# Child processes
# --------------------------------------------------------------------------

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

# The close's context step and the reader of its setting, each in a process of its own; nothing is mocked.
_CLOSE_STEP = r'''
import json, sys
from pathlib import Path

root, ticket = Path(sys.argv[1]), sys.argv[2]
out = {}
try:
    from gov.close.command import _build_context
    out["value"] = _build_context(root, ticket)
except Exception as exc:
    out["error"] = {"type": type(exc).__name__, "code": getattr(exc, "code", None),
                    "message": str(getattr(exc, "message", exc)), "details": getattr(exc, "details", None),
                    "module": type(exc).__module__}
print("\n" + json.dumps(out, default=repr))
'''

_CLOSE_BUDGET = r'''
import json, sys
from pathlib import Path

root = Path(sys.argv[1])
out = {}
try:
    from gov.context import close_budget
    out["value"] = close_budget(root)
except Exception as exc:
    out["error"] = {"type": type(exc).__name__, "code": getattr(exc, "code", None),
                    "message": str(getattr(exc, "message", exc)), "details": getattr(exc, "details", None)}
print("\n" + json.dumps(out, default=repr))
'''

_CAP_CONSTANT = r'''
import json
from gov import context
print("\n" + json.dumps({"cap": getattr(context, "SUPPLEMENTARY_CAP", None),
                         "default": getattr(context, "DEFAULT_BUDGET", None)}))
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


class Step:
    """What the close's context step (or ``close_budget``) did in its process: a value or an error."""

    def __init__(self, what, done, out):
        self.what, self.done, self.out = what, done, out

    def describe(self):
        return f"{self.what}\nexit {self.done.returncode}\nresult: {str(self.out)[:1500]}\nstderr: {self.done.stderr[-2500:]}"

    @property
    def error(self):
        return self.out.get("error")

    @property
    def packet(self):
        assert "error" not in self.out, f"{self.what} refused\n{self.describe()}"
        return self.out["value"]


class Api:
    """Calls this tree's modules and its ``gov`` command line, each in a new process."""

    def __init__(self, workdir):
        self.workdir = Path(workdir)
        for name in ("home", "tmp", "pycache", "elsewhere", "bin"):
            (self.workdir / name).mkdir(parents=True, exist_ok=True)
        for tool, found in (("python3", sys.executable), ("git", shutil.which("git")),
                            ("gitleaks", shutil.which("gitleaks"))):
            if found:
                wrapper = self.workdir / "bin" / tool
                wrapper.write_text(f'#!/bin/sh\nexec "{found}" "$@"\n', encoding="utf-8")
                wrapper.chmod(0o755)
        self.driver = self.workdir / "driver.py"
        self.driver.write_text(_DRIVER, encoding="utf-8")
        self.dead_host = f"127.0.0.1:{_free_port()}"

    def has_gitleaks(self):
        return (self.workdir / "bin" / "gitleaks").exists()

    def env(self, **extra):
        """The ``PYTHONPATH`` this process was given (the code under test, as the run names it), then this tree's
        ``src/``; an empty HOME, a dead embedder address, offline."""
        given = [entry for entry in os.environ.get("PYTHONPATH", "").split(os.pathsep) if entry]
        found = {"PATH": f"{self.workdir / 'bin'}:/usr/bin:/bin", "HOME": str(self.workdir / "home"),
                 "TMPDIR": str(self.workdir / "tmp"), "LC_ALL": "C.UTF-8", "GIT_CONFIG_NOSYSTEM": "1",
                 "GIT_CONFIG_GLOBAL": os.devnull,
                 "PYTHONPATH": os.pathsep.join(dict.fromkeys([*given, str(SRC)])),
                 "PYTHONPYCACHEPREFIX": str(self.workdir / "pycache"),
                 "OLLAMA_HOST": self.dead_host, "GOV_QUERY_OLLAMA_HOST": self.dead_host,
                 "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}
        if site.ENABLE_USER_SITE:
            found["PYTHONUSERBASE"] = site.getuserbase()
        found.update(extra)
        return found

    def _run(self, argv, what, stdin=None):
        try:
            return subprocess.run(argv, cwd=str(self.workdir / "elsewhere"), env=self.env(), capture_output=True,
                                  text=True, timeout=CALL_TIMEOUT_S, input=stdin,
                                  stdin=None if stdin is not None else subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"{what} did not end within {CALL_TIMEOUT_S:.0f} s") from None

    def batch(self, calls):
        """``[(module, function, root, args, kwargs), ...]`` in one process."""
        request = [{"module": m, "function": f, "root": str(r), "args": list(a), "kwargs": dict(k)}
                   for m, f, r, a, k in calls]
        what = ", ".join(dict.fromkeys(f"{m}.{f}" for m, f, *_ in calls))
        done = self._run([sys.executable, str(self.driver)], what, stdin=json.dumps(request))
        assert done.returncode == 0, f"{what} failed (exit code {done.returncode}):\n{done.stderr[-4000:]}"
        out = json.loads(done.stdout.strip().splitlines()[-1])
        for record_ in out:
            assert "missing" not in record_, record_["missing"]
        return out

    def build(self, root, index=True):
        """The lexical index (unless ``index`` is false) and the store of ``root``; no vector."""
        if index:
            assert self.has_gitleaks(), "gitleaks is not on PATH: the lexical index's secret filter cannot run (DEC-287)"
        steps = ([("gov.retrieval.lexical", "refresh", root, (), {})] if index else []) + \
                [("gov.store", "load", root, (), {})]
        for record_ in self.batch(steps):
            assert "value" in record_, f"the planted project could not be built: {record_}"

    # ---- the command line

    def gov(self, root, *args):
        """``gov context <args> --json --root <root>``, from a folder outside the project."""
        argv = [sys.executable, "-m", "gov.cli.main", "context", *map(str, args), "--json", "--root", str(root)]
        done = self._run(argv, f"gov context {' '.join(map(str, args))}")
        return Answer(["gov", "context", *args], done)

    # ---- the close's context step and its setting

    def close_step(self, root, ticket_id):
        """``gov.close.command._build_context(root, ticket_id)`` in a process of its own."""
        what = f"gov.close.command._build_context({ticket_id})"
        done = self._run([sys.executable, "-c", _CLOSE_STEP, str(root), ticket_id], what)
        assert done.returncode == 0, f"{what} failed (exit code {done.returncode}):\n{done.stderr[-4000:]}"
        return Step(what, done, json.loads(done.stdout.strip().splitlines()[-1]))

    def close_budget(self, root):
        """``gov.context.close_budget(root)`` in a process of its own."""
        what = "gov.context.close_budget"
        done = self._run([sys.executable, "-c", _CLOSE_BUDGET, str(root)], what)
        assert done.returncode == 0, f"{what} failed (exit code {done.returncode}):\n{done.stderr[-4000:]}"
        return Step(what, done, json.loads(done.stdout.strip().splitlines()[-1]))

    def constants(self):
        done = self._run([sys.executable, "-c", _CAP_CONSTANT], "gov.context constants")
        assert done.returncode == 0, f"reading gov.context failed:\n{done.stderr[-3000:]}"
        return json.loads(done.stdout.strip().splitlines()[-1])


# --------------------------------------------------------------------------
# Reading packets
# --------------------------------------------------------------------------

def supplementary_tokens(packet):
    return sum(int(item["tokens"]) for item in packet[K_SUPPLEMENTARY])


def supplementary_ids(packet):
    return [(item.get("id"), item.get("path")) for item in packet[K_SUPPLEMENTARY]]


def mandatory_tokens(packet):
    """The packet's tokens less its supplementary block: the ticket's own text and the mandatory inputs."""
    return packet[K_TOKENS] - supplementary_tokens(packet)


def mandatory_ids(packet):
    return [item["id"] for item in packet[K_MANDATORY]]


def assert_refused_over_ceiling(answer, ticket_id, limit):
    """``ok: false``, ``CONTEXT_OVER_CEILING``, a non-zero exit, a message naming the ticket, the ceiling and the
    mandatory size, and the details (today's form)."""
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


def assert_close_refused(step, code, context_error=None):
    """The close's context step raised a ``_Finding`` with ``CONTEXT_FAILED`` and the context's own error in its
    details (``context_error``): never a packet, never another exception type."""
    assert step.error is not None, f"the close's context step returned a packet instead of refusing\n{step.describe()}"
    error = step.error
    assert error["type"] == "_Finding", f"the close's step raised {error['type']}, not a _Finding\n{step.describe()}"
    assert error["code"] == code, f"expected finding code {code}, got {error['code']!r}\n{step.describe()}"
    if context_error is not None:
        details = error.get("details") or {}
        assert details.get("context_error") == context_error, (
            f"expected details['context_error'] == {context_error!r}, got {details!r}\n{step.describe()}")
    return error


def assert_mandatory_whole(project, packet, ticket_id, source_rels):
    """Each mandatory input is there by the sha256 of its whole file, and the ticket's own text is whole and
    verbatim (CAP-15.d): nothing of the mandatory part is shortened."""
    ticket_rel = f".tickets/{ticket_id}.md"
    assert packet.get(K_TICKET_TEXT) == project.text(ticket_rel), "the ticket's own text is not whole and verbatim"
    shas = {item["id"]: item["sha256"] for item in packet[K_MANDATORY]}
    for rel in source_rels:
        found = [sha for sha in shas.values() if sha == sha256_file(project.root / rel)]
        assert found, f"{rel} is not a mandatory input of the packet by its file's sha256: {shas}"
    assert re.fullmatch(r"[0-9a-f]{64}", packet[K_HASH]), packet[K_HASH]
