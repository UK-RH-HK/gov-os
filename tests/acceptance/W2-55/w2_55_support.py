"""Support code for the W2-55 acceptance tests (DAEO-arrl; standard library and PyYAML only).

W2-55 tags the register's entries (domain, scope, lands in, done), checks the tags and the status relations, finds
what still enforces a superseded or changed decision, and leaves superseded and done entries out of what agents see.
The tests use only the public forms the lead's interface specification fixes (S1 to S6, in the README):

- ``gov.store.load(root)`` first, as every caller does, then ``gov.decisions.check_tags(root)``,
  ``gov.decisions.check_propagation(root)`` and W2-03's ``gov.decisions.check(root)``, each in a child process;
- the commands ``python3 -m gov.decisions.tags`` and ``python3 -m gov.decisions.propagation``, run in a project root;
- ``gov retrieve <query> --json`` and ``gov context <ticket> --json`` / ``gov context --in-force --json``
  (``python3 -m gov.cli.main ...``), after ``gov.retrieval.lexical.refresh`` and ``gov.store.load`` built what they
  read (never ``gov rebuild``, never this repository's store).

**The code under test (DEC-732):** every child process gets ``Api.env()``, whose ``PYTHONPATH`` is the ``src/`` of
the tree this file stands in (``SRC``, found from this file's own place), so that the same files, merged into the
ticket's worktree, exercise that worktree's code.

Every project is a temporary git repository built from nothing under pytest's ``tmp_path``. No vector is built (the
semantic route is unavailable and gives no hit), no reranker is loaded, the network is not used.
"""

from __future__ import annotations

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
REGISTER = "docs/DECISION_REGISTER.md"
CALL_TIMEOUT_S = 300.0
MISSING_EXIT = 3

DOMAINS = ("guard", "close", "retrieval", "context", "adopt", "launch", "checks", "plan", "roles", "records",
           "release")   # DEC-791 item 1
SCOPES = ("repository", "kernel")
TAG_CODES = ("TAG_MISSING", "TAG_DOMAIN_UNKNOWN", "TAG_SCOPE_UNKNOWN", "TAG_LANDS_IN_UNKNOWN",
             "TAG_LANDS_IN_MISPLACED", "STATUS_SUCCESSOR_UNNAMED", "STATUS_RELATION_UNMARKED")
ENFORCES = "ENFORCES_SUPERSEDED"

# Two places a tag may land in, one per scope (S1): a kernel file and a project brief.
KERNEL_PLACE = "template/governance/kernel/skills/harbour/SKILL.md"
KERNEL_PLACE_2 = "template/governance/kernel/roles/harbour-master.md"
PROJECT_PLACE = "governance/project/briefs/LEAD-harbour.md"
PROMPT_PLACE = "governance/project/prompts/w2-orchestrator.md"
PLACES = {
    KERNEL_PLACE: "# The harbour skill\n\nThe lamp rule is stated here.\n",
    KERNEL_PLACE_2: "# The harbour master\n\nThe mast rule is stated here.\n",
    PROJECT_PLACE: "# The lead's brief\n\nThe flag rule is stated here.\n",
    PROMPT_PLACE: "# The orchestrator's prompt\n\nThe bell rule is stated here.\n",
}


def tags(domain="retrieval", scope="kernel", lands_in=KERNEL_PLACE, done=False):
    """The tags line of S1: ``- **Tags:** domain: <d> · scope: <s> · lands in: <places>[ · done]``."""
    line = f"- **Tags:** domain: {domain} · scope: {scope} · lands in: {lands_in}"
    return line + (" · done" if done else "")


def entry(entry_id, title, status="ACCEPTED · **Basis:** OWNER", tags_line=None, body=None, more=()):
    """One register entry: its heading, its status line first, then its tags line and any further lines."""
    lines = [f"### {entry_id} — {title}", f"- **Status:** {status}"]
    if tags_line is not None:
        lines.append(tags_line)
    lines += list(more)
    lines += ["", body or f"The text of {entry_id}.", ""]
    return "\n".join(lines)


def register(*entries, preamble="# Decision register\n\nThe decisions of the planted harbour, oldest first.\n"):
    return preamble + "\n" + "\n".join(entries)


def heading_ids(text):
    """The ids of the register's entry headings outside fenced code blocks, in order, each once."""
    found, fence = [], None
    for line in text.split("\n"):
        mark = re.match(r" {0,3}(`{3,}|~{3,})", line)
        if fence is not None:
            if mark and mark.group(1).startswith(fence) and not line[mark.end():].strip():
                fence = None
            continue
        if mark:
            fence = mark.group(1)
            continue
        hit = re.match(r"### (DEC-[0-9]{3,})(?=[ :\-–—])", line)
        if hit and hit.group(1) not in found:
            found.append(hit.group(1))
    return found


def entry_spans(text):
    """``id -> (first, last)``: the 1-based lines of each entry, its heading to the line before the next heading."""
    lines = text.split("\n")
    heads = [n for n, line in enumerate(lines, 1) if re.match(r"#{1,6}\s", line)]
    spans = {}
    for at, n in enumerate(heads):
        hit = re.match(r"### (DEC-[0-9]{3,})", lines[n - 1])
        if hit:
            last = heads[at + 1] - 1 if at + 1 < len(heads) else len(lines)
            spans[hit.group(1)] = (n, last)
    return spans


def line_number(text, needle):
    """The 1-based number of the one line of ``text`` that holds ``needle``."""
    numbers = [n for n, line in enumerate(text.split("\n"), 1) if needle in line]
    assert len(numbers) == 1, f"the fixture is wrong: {needle!r} is on lines {numbers}"
    return numbers[0]


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
               "GIT_AUTHOR_NAME": "W2-55 tests", "GIT_AUTHOR_EMAIL": "w2-55@example.invalid",
               "GIT_COMMITTER_NAME": "W2-55 tests", "GIT_COMMITTER_EMAIL": "w2-55@example.invalid",
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


def path_map(register_rel=REGISTER, extra_comment=None):
    """This repository's path map, its namespaces replaced by one that classes everything as governance memory
    without vectors, its authority block left out, and ``register_rel`` named (or no register when None)."""
    document = yaml.safe_load((REPO_ROOT / PATH_MAP_REL).read_text(encoding="utf-8"))
    document.pop("retrieval_authority", None)
    document.pop("decision_register", None)
    if register_rel is not None:
        document["decision_register"] = register_rel
    document["namespaces"] = {"everything": {
        "paths": ["**"], "memory_class": "governance", "sensitivity": "internal",
        "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                            "independent-auditor", "research"],
        "retention": "kept in git history", "export_policy": "allowed", "provenance": "written by the W2-55 tests",
        "deletion_rebuild": "authoritative; restored from git only", "embedding_policy": "not embedded"}}
    text = yaml.safe_dump(document, sort_keys=False, allow_unicode=True)
    if extra_comment:
        text = f"# {extra_comment}\n" + text
    return text


def build_project(root, register_text, files=None, register_rel=REGISTER, places=True, path_map_comment=None):
    """A committed project: README, gitleaks rules, the path map naming ``register_rel``, the register (unless
    None), the two scopes' places (unless ``places`` is False) and ``files``."""
    project = Project(root)
    project.write("README.md", "# The planted harbour\n\nOrdinary text about the harbour.\n")
    project.write(".gitignore", ".gov-runtime/\n")
    if GITLEAKS_TEMPLATE.is_file():
        shutil.copy2(GITLEAKS_TEMPLATE, project.root / ".gitleaks.toml")
    project.write(PATH_MAP_REL, path_map(register_rel, path_map_comment))
    if register_text is not None:
        project.write(register_rel or REGISTER, register_text)
    if places:
        project.write_all(PLACES)
    project.write_all(files or {})
    project.commit("the planted harbour")
    return project


# --------------------------------------------------------------------------
# The driver and the commands, each in a new process on this tree's src/
# --------------------------------------------------------------------------

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
                              "message": str(getattr(exc, "message", exc))}})
print("\n" + json.dumps(out, default=repr))
'''


def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


class Answer:
    def __init__(self, done):
        self.returncode, self.stdout, self.stderr = done.returncode, done.stdout, done.stderr

    def describe(self):
        return f"exit {self.returncode}\nstdout: {self.stdout[-3000:]}\nstderr: {self.stderr[-3000:]}"

    @property
    def envelope(self):
        try:
            data = json.loads(self.stdout)
        except ValueError:
            raise AssertionError(f"the output is not one JSON envelope\n{self.describe()}") from None
        assert isinstance(data, dict) and "ok" in data, f"the output is not an envelope\n{self.describe()}"
        return data

    @property
    def result(self):
        data = self.envelope
        assert data["ok"] is True, f"the command refused\n{self.describe()}"
        assert isinstance(data.get("result"), dict), f"the envelope's result is not a map\n{self.describe()}"
        return data["result"]


class Api:
    """Calls this tree's modules and its ``gov`` command line, each in a new process."""

    def __init__(self, workdir):
        self.workdir = Path(workdir)
        for name in ("home", "tmp", "pycache", "elsewhere"):
            (self.workdir / name).mkdir(parents=True, exist_ok=True)
        self.driver = self.workdir / "driver.py"
        self.driver.write_text(_DRIVER, encoding="utf-8")
        self.dead_host = f"127.0.0.1:{_free_port()}"

    def env(self):
        """This tree's ``src/`` on ``PYTHONPATH``; an empty HOME, a dead embedder endpoint, offline."""
        found = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.workdir / "home"),
                 "TMPDIR": str(self.workdir / "tmp"), "LC_ALL": "C.UTF-8", "GIT_CONFIG_NOSYSTEM": "1",
                 "GIT_CONFIG_GLOBAL": os.devnull, "PYTHONPATH": str(SRC),
                 "PYTHONPYCACHEPREFIX": str(self.workdir / "pycache"),
                 "OLLAMA_HOST": self.dead_host, "GOV_QUERY_OLLAMA_HOST": self.dead_host,
                 "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}
        if site.ENABLE_USER_SITE:
            found["PYTHONUSERBASE"] = site.getuserbase()
        return found

    def batch(self, calls):
        """``[(module, function, root, args, kwargs), ...]`` in one process."""
        request = [{"module": m, "function": f, "root": str(r), "args": list(a), "kwargs": dict(k)}
                   for m, f, r, a, k in calls]
        what = ", ".join(f"{m}.{f}" for m, f, *_ in calls)
        try:
            done = subprocess.run([sys.executable, str(self.driver)], input=json.dumps(request), env=self.env(),
                                  cwd=str(self.workdir / "elsewhere"), capture_output=True, text=True,
                                  timeout=CALL_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"{what} did not end within {CALL_TIMEOUT_S:.0f} s") from None
        assert done.returncode == 0, f"{what} failed (exit code {done.returncode}):\n{done.stderr[-4000:]}"
        return json.loads(done.stdout.strip().splitlines()[-1])

    def load(self, root):
        """``gov.store.load(root)``; its refusal, if any (``None`` when it loaded)."""
        out = self.batch([("gov.store", "load", root, (), {})])[0]
        return out.get("error")

    def build(self, root):
        """The lexical index and the store of ``root``; no vector."""
        out = self.batch([("gov.retrieval.lexical", "refresh", root, (), {}), ("gov.store", "load", root, (), {})])
        for record in out:
            assert "value" in record, f"the planted project could not be built: {record}"

    def findings(self, root, function):
        """``gov.store.load(root)`` then ``gov.decisions.<function>(root)``: the list of findings."""
        loaded, checked = self.batch([("gov.store", "load", root, (), {}), ("gov.decisions", function, root, (), {})])
        assert "value" in loaded, f"gov.store.load refused: {loaded}"
        assert "missing" not in checked, checked["missing"]
        assert "value" in checked, f"gov.decisions.{function} refused instead of reporting: {checked}"
        found = checked["value"]
        assert isinstance(found, list), f"{function} did not return a list of findings: {found!r}"
        for finding in found:
            assert isinstance(finding, dict) and isinstance(finding.get("code"), str), f"not a finding: {finding!r}"
            for key in ("ids", "paths"):
                assert isinstance(finding.get(key), list), f"a finding's `{key}` is not a list: {finding!r}"
            assert isinstance(finding.get("message"), str), f"a finding has no message: {finding!r}"
        return found

    def module(self, root, name):
        """``python3 -m <name>`` run in the project's root (the store loaded first)."""
        assert self.load(root) is None, "gov.store.load refused"
        done = subprocess.run([sys.executable, "-m", name], cwd=str(root), env=self.env(), capture_output=True,
                              text=True, timeout=CALL_TIMEOUT_S, stdin=subprocess.DEVNULL)
        return Answer(done)

    def gov(self, root, *args):
        """``gov <args> --json --root <root>``, from a folder outside the project."""
        done = subprocess.run([sys.executable, "-m", "gov.cli.main", *args, "--json", "--root", str(root)],
                              cwd=str(self.workdir / "elsewhere"), env=self.env(), capture_output=True, text=True,
                              timeout=CALL_TIMEOUT_S, stdin=subprocess.DEVNULL)
        return Answer(done)


# --------------------------------------------------------------------------
# Reading findings, bundles and packets
# --------------------------------------------------------------------------

def show(found):
    return "\n".join(f"  {f.get('code')} ids={f.get('ids')} paths={f.get('paths')}: {f.get('message')}"
                     for f in found) or "  (none)"


def naming(found, code=None, entry_id=None):
    """The findings of ``code`` (any code when None) whose ``ids`` hold ``entry_id``."""
    return [f for f in found if (code is None or f["code"] == code) and (entry_id is None or entry_id in f["ids"])]


def names_line(message, rel, number):
    """The message names the place ``rel`` at line ``number``: ``<rel>:<number>`` or ``line <number>``, the number
    not followed by another digit (a lone digit elsewhere, in a path or an id, is no line)."""
    at_place = rf"{re.escape(rel)}:{number}(?!\d)"
    in_words = rf"(?<![\w-])line {number}(?!\d)"
    return re.search(f"{at_place}|{in_words}", message) is not None


def entries_of(item, register_text):
    """The register entries an evidence item or a supplementary item holds: each entry whose heading line is in its
    text, and (for a bundle item) the entry whose span holds its first line."""
    text = item.get("text", "") or ""
    found = set(re.findall(r"^### (DEC-[0-9]{3,})", text, flags=re.MULTILINE))
    start = item.get("start_line")
    if isinstance(start, int):
        for entry_id, (first, last) in entry_spans(register_text).items():
            if first <= start <= last:
                found.add(entry_id)
    return found


def served(items, register_text, register_rel=REGISTER):
    """Every register entry the items hold."""
    found = set()
    for item in items:
        if item.get("path") == register_rel:
            found |= entries_of(item, register_text)
    return found
