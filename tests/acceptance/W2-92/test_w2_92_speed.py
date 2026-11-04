"""KPI success 6 (DEC-1065 (4)): a plain question costs about one second, because the record route no longer parses
every record's front matter in each process (the titles kept in the store at rebuild); nothing else in the bundle
changes (success 4).

The time itself (a cold ``gov retrieve`` within about 1.2 s at the median of ten on this repository's store) is the
CTO's measure on the shared servers, not a test here. These tests check what a test can, in a planted project with
many records (``MASS`` of them besides the harbour's), its lexical index and record graph built in a temporary
folder, and no code index (the record route needs none; the code-graph tool is left off ``PATH``):

- ``test_s6a``: one ``retrieve`` of a plain question, in a new process, opens none of the many records' files and
  parses none of their front matters (at most ``ALLOWED`` of them). The integrated code opens and parses every one
  (``graph_route.start_ids`` reads each record's title from its file, ``_parsed``).
- ``test_s6b``: the titles come from the store after a rebuild. A record's file edited in the working tree after
  the load (its title changed, not committed; the lexical index refreshed, so it is fresh and holds the old title
  nowhere) is still found by the title the store was built with; and after the change is committed and the store
  rebuilt, by its new title and no longer by its old one.
- ``test_s6c``: nothing else changes. In the many-records project, the record route answers each question as the
  integrated code ``BASE`` does (its ``src/`` taken from git into the session's folder), item for item: the plain
  question, a record named by id, ticket id, W2 id and title, and radius 1.

Counting is done in the child process: an audit hook (``sys.addaudithook``, event ``open``) records every file
opened under ``records/mass/`` while ``retrieve`` runs, and the YAML module's load functions are wrapped to count
every parse of a text that holds a planted record's id. Both are switched on only around the one call.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import w2_92_support as support

# The integrated code the bundles are compared with: w2/integrate eb28c40866af (DEC-1065 placed), where the record
# route reads every record's front matter per process.
BASE = "eb28c40866afdc315bfa9cf5de37e06888410cd5"

MASS = 240                       # planted records besides the harbour's (this repository holds about 840)
ALLOWED = MASS // 20             # "not every record": at most 5 % of them opened or parsed for a plain question
MASS_DIR = "records/mass"
MASS_PREFIX = "MASS"             # every planted record's id begins with it; no other planted line holds it
MASS_KINDS = ("task", "requirement", "specification", "lesson")
PLAIN = support.PLAIN_PHRASE     # names no record and no symbol


def _mass_id(number):
    return f"{MASS_PREFIX}-{number:04d}"


def _mass_title(number):
    return f"Quay crane {number:04d}"


def _mass_text(number):
    # no word of any question here: the many records are never evidence of the plain question
    return f"Crane {number:04d} inspected; grease applied, cable checked."


def mass_files():
    return {f"{MASS_DIR}/{_mass_id(number).lower()}.md":
            support._record(_mass_id(number), MASS_KINDS[number % len(MASS_KINDS)], "ACTIVE", _mass_title(number),
                            _mass_text(number))
            for number in range(1, MASS + 1)}


def build_many(project):
    """The harbour of the other W2-92 tests with ``MASS`` more records, committed."""
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    support.git(project, "init", "-q", "-b", "main")
    for rel, text in {**support.corpus(), **mass_files(), support.PATH_MAP_REL: support.path_map()}.items():
        (project / rel).parent.mkdir(parents=True, exist_ok=True)
        (project / rel).write_text(text, encoding="utf-8")
    shutil.copy2(support.GITLEAKS_TEMPLATE, project / ".gitleaks.toml")
    support.git(project, "add", "-A")
    support.git(project, "commit", "-q", "-m", "the planted harbour with many records")
    return project


# Runs one ``retrieve`` and counts what it reads of the many records.
_COUNTING = r'''
import importlib, json, os, sys, time
from pathlib import Path

request = json.loads(sys.stdin.read())
MARK, PREFIX = request["mark"], request["prefix"]
seen = {"on": False, "opens": [], "parses": 0, "depth": 0}


def hook(event, args):
    if seen["on"] and event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
        path = os.fsdecode(args[0])
        if MARK in path.replace(os.sep, "/"):
            seen["opens"].append(path)


sys.addaudithook(hook)
import yaml


def counted(original):
    def wrapper(stream, *args, **kwargs):  # one parse is counted once: safe_load calls load inside
        if seen["on"] and not seen["depth"]:
            text = stream.decode("utf-8", "replace") if isinstance(stream, bytes) else stream
            if isinstance(text, str) and PREFIX + "-" in text:
                seen["parses"] += 1
        seen["depth"] += 1
        try:
            return original(stream, *args, **kwargs)
        finally:
            seen["depth"] -= 1
    return wrapper


for name in ("safe_load", "load", "full_load", "unsafe_load", "safe_load_all", "load_all", "full_load_all",
             "unsafe_load_all", "compose", "compose_all", "parse", "scan"):
    if hasattr(yaml, name):
        setattr(yaml, name, counted(getattr(yaml, name)))

def probe(path):
    """What the record route of the integrated code does for one record: read its file, parse its front matter."""
    text = Path(path).read_text(encoding="utf-8")
    return yaml.safe_load(text[4:text.find("\n---", 4)])


retrieve = importlib.import_module("gov.retrieval.retrieve").retrieve
kwargs = dict(request["kwargs"], reranker=lambda: None)
out = {"value": None, "error": None}
seen["on"], start = True, time.perf_counter()
try:
    if request.get("probe"):
        out["value"] = probe(request["probe"])
    else:
        out["value"] = retrieve(Path(request["root"]), request["query"], **kwargs)
except Exception as exc:
    out["error"] = {"type": type(exc).__name__, "message": str(exc), "code": getattr(exc, "code", None)}
finally:
    seen["on"] = False
out.update(seconds=time.perf_counter() - start, opens=sorted(set(seen["opens"])), parses=seen["parses"])
print("\n" + json.dumps(out, default=repr))
'''


class Counting(support.Api):
    """``support.Api`` with the ``src/`` it runs chosen (this worktree's, or ``BASE``'s) and a counting call."""

    def __init__(self, workdir, src=support.SRC):
        super().__init__(workdir)
        self.src = Path(src)
        self.counting = self.workdir / "counting.py"
        self.counting.write_text(_COUNTING, encoding="utf-8")

    def env(self, path):
        return {**super().env(path), "PYTHONPATH": str(self.src)}

    def counted(self, root, query, probe=None, **kwargs):
        """``{"value", "error", "seconds", "opens", "parses"}`` of one ``retrieve`` in a new process (or, with
        ``probe``, of reading that one file and parsing its front matter instead)."""
        path, _ = self.tool_path(support.ABSENT)
        request = {"root": str(root), "query": query, "kwargs": kwargs, "mark": f"/{MASS_DIR}/",
                   "prefix": MASS_PREFIX, "probe": str(probe) if probe else None}
        done = subprocess.run([sys.executable, str(self.counting)], input=json.dumps(request), env=self.env(path),
                              cwd=str(self.workdir / "elsewhere"), capture_output=True, text=True,
                              timeout=support.CALL_TIMEOUT_S)
        assert done.returncode == 0, f"the counting call failed (exit code {done.returncode}):\n{done.stderr[-4000:]}"
        return json.loads(done.stdout.strip().splitlines()[-1])

    def bundle(self, root, query, **kwargs):
        record = self.counted(root, query, **kwargs)
        assert record["error"] is None, f"retrieve raised {record['error']} for {query!r}"
        return record["value"]


@pytest.fixture(scope="module")
def head(tmp_path_factory):
    if shutil.which("gitleaks") is None:
        pytest.skip("gitleaks is not on PATH on this machine: the lexical index's secret filter cannot run (DEC-287)")
    return Counting(tmp_path_factory.mktemp("w2-92-s6-head"))


@pytest.fixture(scope="module")
def base(head, tmp_path_factory):
    """``BASE``'s ``src/``, taken from git into the session's folder (``git archive``), and an Api that runs it."""
    place = tmp_path_factory.mktemp("w2-92-s6-base")
    archive = subprocess.run(["git", "-C", str(support.REPO_ROOT), "archive", "--format=tar", BASE, "src"],
                             capture_output=True)
    if archive.returncode != 0:
        pytest.fail(f"the integrated code {BASE[:12]} is not in this repository's git: {archive.stderr[-500:]!r}")
    subprocess.run(["tar", "-x", "-C", str(place)], input=archive.stdout, check=True)
    return Counting(place / "api", src=place / "src")


@pytest.fixture(scope="module")
def many(head, tmp_path_factory):
    """The many-records project, its lexical index and record graph built by this worktree's code; no code index."""
    root = build_many(tmp_path_factory.mktemp("w2-92-s6-many") / "repo")
    head.build(root, store=True, code=False)
    return root


# --------------------------------------------------------------------------
# S6: the record route reads no record's front matter for a plain question
# --------------------------------------------------------------------------

PLAIN_QUESTIONS = [("plain", PLAIN), ("unknown id", f"{PLAIN} DEC-999")]


@pytest.mark.parametrize("name, question", PLAIN_QUESTIONS, ids=[case[0] for case in PLAIN_QUESTIONS])
def test_s6a_a_plain_question_does_not_read_every_records_front_matter(head, many, name, question):
    """A new process, one plain question: the many records' files are not opened and their front matters not
    parsed (at most ``ALLOWED`` of ``MASS``); the titles the record route needs are the store's (DEC-1065 (4))."""
    record = head.counted(many, question)
    assert record["error"] is None, f"retrieve raised {record['error']} for {question!r}"
    opened, parsed = [Path(path).name for path in record["opens"]], record["parses"]
    assert len(opened) <= ALLOWED, (
        f"one plain question opened {len(opened)} of the {MASS} planted records' files (at most {ALLOWED} allowed): "
        f"the record route still reads every record's front matter in each process; for example {opened[:3]}")
    assert parsed <= ALLOWED, (
        f"one plain question parsed {parsed} front matters of the {MASS} planted records (at most {ALLOWED} "
        f"allowed): the record route still parses every record's front matter in each process")


def test_s6a_premise_the_counter_sees_a_record_read(head, many):
    """The counter is live: in the same child, reading one planted record's file and parsing its front matter (what
    the integrated record route does for every record) counts one open and one parse."""
    rel = next(iter(mass_files()))
    record = head.counted(many, PLAIN, probe=many / rel)
    assert record["error"] is None, record["error"]
    assert record["value"]["id"] == _mass_id(1), record["value"]
    assert [Path(path).name for path in record["opens"]] == [Path(rel).name], record["opens"]
    assert record["parses"] == 1, record["parses"]


# --------------------------------------------------------------------------
# S6: the titles come from the store after a rebuild
# --------------------------------------------------------------------------

NEW_TITLE = "Gannet Survey Method"


def _title_question(title):
    return f"what does the {title} require"


def _retitled(project):
    """``TITLED``'s file with its title changed to ``NEW_TITLE`` (front matter and heading); its body unchanged."""
    path = Path(project) / support.TITLED_REL
    text = path.read_text(encoding="utf-8")
    assert text.count(support.TITLED_TITLE) == 2, text
    path.write_text(text.replace(support.TITLED_TITLE, NEW_TITLE), encoding="utf-8")


def _lexical(api, root, *calls):
    """The values of ``gov.retrieval.lexical``'s ``calls`` (``(function, args, kwargs)``) on ``root``, in one process."""
    out, _ = api.run([("gov.retrieval.lexical", name, [{"$path": str(root)}, *args], kwargs)
                      for name, args, kwargs in calls])
    for record in out:
        assert record["error"] is None, record["error"]
    return [record["value"] for record in out]


def test_s6b_a_title_is_the_one_the_store_was_built_with(head, tmp_path):
    """After the load, the record's file is edited in the working tree (its title changed, not committed, the
    store not rebuilt) and the lexical index refreshed, so the index is fresh (DEC-342 is not the cause) and holds
    the old title nowhere. Asked by the title the store was built with, only the record route can bring the record:
    it does, so the title is the store's and the working file's edit is not read for it.

    Revised (Rewrite-Reason: s6b's premise, a stale index cites nothing, DEC-342): before, the index was left stale
    by the edit, and a stale index cites no chunk whatever the title's source (the CTO's decision P2)."""
    root = build_many(tmp_path / "repo")
    head.build(root, store=True, code=False)
    _retitled(root)
    _, fresh, alone = _lexical(head, root, ("refresh", [], {}), ("freshness", [], {}),
                               ("search", [support.TITLED_TITLE], {"refresh": False}))
    assert fresh["status"] == "fresh", f"premise: the lexical index is not fresh after its refresh: {fresh}"
    found = [hit.get("path") for hit in alone.get("ranked", alone["hits"])]
    assert support.TITLED_REL not in found, (
        f"premise: the lexical route alone finds {support.TITLED_REL} for the old title, so the case cannot tell "
        f"where the title came from: {found}")
    bundle = head.bundle(root, support.TITLED_TITLE)
    assert support.holds_text(bundle, support.TITLED_TEXT), (
        f"the question is {support.TITLED}'s title as the store holds it ({support.TITLED_TITLE!r}); the lexical "
        f"index is fresh and holds that title nowhere, and the record is not in the bundle: the record route took "
        f"the title from the working tree's edited file ({NEW_TITLE!r}), not from the store "
        f"(the bundle holds {support.paths(bundle)})")


def test_s6b_after_a_rebuild_the_new_title_is_the_stores(head, tmp_path):
    """A title changed, committed and the store and lexical index rebuilt: the new title brings the record, the old
    one no longer does (a guard: the store's titles follow its rebuild). The questions are the bare titles, so no
    other word of the question can bring the record through the lexical route."""
    root = build_many(tmp_path / "repo")
    head.build(root, store=True, code=False)
    _retitled(root)
    support.git(root, "commit", "-q", "-am", "the protocol retitled")
    head.build(root, store=True, code=False)
    renamed = head.bundle(root, NEW_TITLE)
    assert support.holds_text(renamed, support.TITLED_TEXT), (
        f"after the rebuild the question naming the new title {NEW_TITLE!r} does not bring {support.TITLED}: "
        f"{support.paths(renamed)}")
    old = head.bundle(root, support.TITLED_TITLE)
    assert not support.holds_text(old, support.TITLED_TEXT), (
        f"after the rebuild the old title {support.TITLED_TITLE!r} still brings {support.TITLED}: the store kept "
        f"the title of before the rebuild ({support.paths(old)})")


# --------------------------------------------------------------------------
# S6 with S4: nothing else changes in the bundle
# --------------------------------------------------------------------------

# (case, question, retrieve's arguments, a text the bundle holds: the named record's evidence, or a plain page's)
SAME = [
    ("plain", PLAIN, {}, PLAIN),
    ("unknown id", f"{PLAIN} DEC-999", {}, PLAIN),
    ("decision id", f"what does {support.NAMED_DEC} say", {}, support.NAMED_DEC_TEXT),
    ("contract id at radius 1", f"what does {support.NAMED_CAP} say", {"radius": 1}, support.NEAR_TEXT),
    ("ticket id", f"what does {support.NAMED_TICKET} say", {}, support.NAMED_TICKET_TEXT),
    ("W2 id", f"what does {support.NAMED_W2} say", {}, support.NAMED_W2_TEXT),
    ("record title", _title_question(support.TITLED_TITLE), {}, support.TITLED_TEXT),
    ("a many-records title", f"what does the {_mass_title(42)} say", {}, _mass_text(42)),
    ("ticket", PLAIN, {"ticket": support.NAMED_TICKET}, support.LESSON_TEXT),
    ("batched", PLAIN, {"batch_size": 2}, PLAIN),
]


@pytest.mark.parametrize("name, question, kwargs, text", SAME, ids=[case[0] for case in SAME])
def test_s6c_the_record_route_answers_as_the_integrated_code_does(head, base, many, name, question, kwargs, text):
    """Item for item, the bundle this worktree's code gives in the many-records project is the one ``BASE`` gives
    (its continuation token's bytes and facets other than today's two aside, as ``support.projection`` reads it);
    each holds the evidence the question names, so two empty bundles never pass."""
    given = base.bundle(many, question, **kwargs)
    assert support.holds_text(given, text), (
        f"premise: the integrated code's bundle for {question!r} does not hold {text!r}: {support.paths(given)}")
    now = head.bundle(many, question, **kwargs)
    assert support.holds_text(now, text), (
        f"the bundle for {question!r} no longer holds {text!r}, as the integrated code's does: {support.paths(now)}")
    before, after = support.projection(given), support.projection(now)
    assert after["evidence"] == before["evidence"], (
        f"the evidence changed for {question!r}:\n  integrated {before['evidence']}\n  now        {after['evidence']}")
    assert after == before, (
        "the bundle changed outside its evidence: "
        + json.dumps({key: [before.get(key), after.get(key)] for key in sorted(set(before) | set(after))
                      if before.get(key) != after.get(key)}, default=repr))
