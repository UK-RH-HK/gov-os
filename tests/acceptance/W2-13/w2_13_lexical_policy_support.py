"""Support code for W2-13's S6 cases: the keyword index honours the path map's ``lexical_policy`` (DEC-1066 (3), G4;
not a test module).

S6: a namespace whose ``lexical_policy`` is ``not indexed`` keeps its files out of the keyword index (absent: indexed,
as today); the path map's validator accepts the field with its two values (``indexed``, ``not indexed``); a file kept
out is named in the rebuild's report; the evaluation set's own documents (lens B's report and
``fixtures/evaluation/**``) are what D-7 marks so.

The planted project has four namespaces, disjoint, every tracked path in exactly one (``gov.check.pathmap``):

- ``evaluation``: ``not indexed``, ``not embedded`` (D-7's shape: kept out of both indexes);
- ``kept-out``: ``not indexed``, ``not embedded`` (a second namespace kept out). ``not indexed`` with ``embedded``
  is refused by the validator (the CTO, P2: the vectors are built from the keyword index's chunks); only a scratch
  copy plants it (``build_project(..., embedded_kept_out=True)``);
- ``indexed``: ``indexed``, ``not embedded`` (the field given, its other value);
- ``governance``: no ``lexical_policy``, ``embedded`` (the rest, the path map itself included).

Each planted file holds two made-up words and an id that no other file of the project holds (made up, so that no
word, stem or trigram of another file's text spells them by chance). The control project is the same files with no
``lexical_policy`` anywhere. Both are indexed by ``gov rebuild --no-embeddings``: the record store and the keyword
index, no embedder asked. Only the vectors' case builds the vectors, through W1-21's stand-in endpoint (vectors made
of words: no model runs, DEC-1064).
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import yaml

import w2_13_support as support

NOT_INDEXED, INDEXED = "not indexed", "indexed"
EMBEDDED, NOT_EMBEDDED = "embedded", "not embedded"
FIELD = "lexical_policy"

# name -> (patterns, lexical_policy or None for absent, embedding_policy)
NAMESPACES = {
    "evaluation": (["evaluation/**"], NOT_INDEXED, NOT_EMBEDDED),
    "kept-out": (["kept-out/**"], NOT_INDEXED, NOT_EMBEDDED),
    "indexed": (["indexed/**"], INDEXED, NOT_EMBEDDED),
    "governance": (["*", "docs/**", "governance/**"], None, EMBEDDED),
}


class Planted:
    """One planted file: its path, its namespace, its two words (the plain-word question) and its id."""

    def __init__(self, path, namespace, words, ident, text):
        self.path, self.namespace, self.words, self.ident, self.text = path, namespace, words, ident, text

    @property
    def question(self):
        return " ".join(self.words)

    def __repr__(self):
        return self.path


def _doc(heading, words, ident):
    return f"# {heading}\n\nThe {words[0]} {words[1]} entry is filed as {ident}.\n"


FILES = [
    Planted("evaluation/lens-report.md", "evaluation", ("zorquix", "vexlumbra"), "EV-5521",
            _doc("Lens report", ("zorquix", "vexlumbra"), "EV-5521")),
    Planted("evaluation/cases/q01.yaml", "evaluation", ("jondrakel", "quivvet"), "EV-5522",
            "question: Where is the jondrakel quivvet rule kept?\nexpected: [EV-5522]\n"),
    Planted("kept-out/notes.md", "kept-out", ("plimzot", "wyxander"), "KO-3301",
            _doc("Kept notes", ("plimzot", "wyxander"), "KO-3301")),
    Planted("indexed/log.md", "indexed", ("draxolum", "fennquist"), "IX-7710",
            _doc("Indexed log", ("draxolum", "fennquist"), "IX-7710")),
    Planted("docs/plain.md", "governance", ("glonkrib", "sartivex"), "PL-1180",
            _doc("Plain page", ("glonkrib", "sartivex"), "PL-1180")),
]
BY_PATH = {planted.path: planted for planted in FILES}
KEPT_OUT = [planted for planted in FILES if NAMESPACES[planted.namespace][1] == NOT_INDEXED]
KEPT_IN = [planted for planted in FILES if NAMESPACES[planted.namespace][1] != NOT_INDEXED]
ABSENT_FILE = BY_PATH["docs/plain.md"]  # its namespace has no lexical_policy
INDEXED_FILE = BY_PATH["indexed/log.md"]  # its namespace says ``indexed``
KEPT_OUT_NAMESPACE = "kept-out"  # the namespace the scratch copy marks ``embedded``, which the validator refuses
EVALUATION_FILE = BY_PATH["evaluation/lens-report.md"]  # not indexed, not embedded

# The repository's own evaluation documents (DEC-1066 (3)): what D-7 marks ``not indexed``.
LENS_B_REPORT = "docs/assessment/2026-10/B-memory-retrieval.md"
EVALUATION_FIXTURES = "fixtures/evaluation/"


# --------------------------------------------------------------------------
# The path map and the projects
# --------------------------------------------------------------------------

def namespace(patterns, lexical_policy, embedding_policy, *, absent=False):
    entry = {"paths": list(patterns), "memory_class": "governance", **support._NAMESPACE_FIELDS,
             "embedding_policy": embedding_policy}
    if not absent:
        entry[FIELD] = lexical_policy
    return entry


def write_path_map(project, namespaces):
    """This repository's path map (as ``w2_13_support.adopt`` takes it), its namespaces replaced by ``namespaces``,
    and the kernel's gitleaks rules."""
    support.adopt(project, embedded=False)
    path = Path(project) / support.PATH_MAP_REL
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    document.pop("role_paths", None)  # no role filter here: S5's own cases hold it
    document["namespaces"] = namespaces
    path.write_text(yaml.safe_dump(document, sort_keys=False, allow_unicode=True), encoding="utf-8")


def planted_namespaces(with_policy=True):
    return {name: namespace(patterns, lexical, embedding, absent=(lexical is None or not with_policy))
            for name, (patterns, lexical, embedding) in NAMESPACES.items()}


def build_project(project, with_policy=True, embedded_kept_out=False):
    """The planted project (``with_policy``) or its control (no ``lexical_policy`` anywhere): one commit. Not
    indexed. ``embedded_kept_out``: the scratch copy whose ``kept-out`` namespace says ``not indexed`` and
    ``embedded``, the combination the validator refuses."""
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    support.git(project, "init", "-q", "-b", "main")
    namespaces = planted_namespaces(with_policy)
    if embedded_kept_out:
        namespaces[KEPT_OUT_NAMESPACE]["embedding_policy"] = EMBEDDED
    write_path_map(project, namespaces)
    support.write(project, ".gitignore", ".gov-runtime/\n")
    support.write(project, "README.md", "# A project\n\nOrdinary text about the project.\n")
    for planted in FILES:
        support.write(project, planted.path, planted.text)
    support.commit(project, "the S6 project")
    return project


def build_one_namespace(project, value):
    """A project whose one namespace holds every path and says ``lexical_policy: <value>``. One commit."""
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    support.git(project, "init", "-q", "-b", "main")
    write_path_map(project, {"everything": {**namespace(["**"], None, EMBEDDED, absent=True), FIELD: value}})
    support.write(project, ".gitignore", ".gov-runtime/\n")
    support.write(project, "docs/page.md", ABSENT_FILE.text)
    support.commit(project, "one namespace")
    return project


# --------------------------------------------------------------------------
# The calls
# --------------------------------------------------------------------------

def rebuild(box, root, env=None):
    """``gov rebuild --json --no-embeddings``: the record store and the keyword index, no embedder asked. The
    report: the envelope's result."""
    run = box.gov("rebuild", "--json", "--no-embeddings", "--root", str(root), env=env or box.scratch_env(),
                  timeout=support.MEASURE_TIMEOUT_S)
    result = run.result()
    assert result.get("stores", {}).get("lexical", {}).get("status") == "recreated", \
        f"premise: gov rebuild did not recreate the keyword index: {result!r}"
    return result


def found_paths(answer):
    """Every path the keyword route returns for a question: its exact hits and its ranked chunks."""
    paths = {hit.get("path") for hit in answer.get("hits") or []}
    paths |= {chunk.get("path") for chunk in answer.get("ranked") or [] if isinstance(chunk, dict)}
    return set(filter(None, paths))


def search_paths(box, root, question):
    """``lexical.search(root, question, refresh=False)``: the answer must be available; the paths it returns."""
    answer = box.search(root, question, refresh=False)
    assert answer.get("available") is True, f"premise: the keyword index is not available: {answer!r}"
    return found_paths(answer)


def fused(box, root, question, env):
    """``fusion.search(root, question, None, refresh=False, reranker=<absent>)``: ``path -> set of routes``."""
    outcome = box.run([(support.FUSION, "search", [support.path_arg(root), question, None],
                        {"refresh": False, "reranker": support.ABSENT_RERANKER})], env=env)
    answer = outcome.value()
    assert isinstance(answer, dict) and isinstance(answer.get("hits"), list), f"not a fused answer: {answer!r}"
    routes = {}
    for hit in answer["hits"]:
        routes.setdefault(hit.get("path"), set()).update(hit.get("routes") or [])
    return answer, routes


def load_config(box, root):
    """``gov.config.loader.load_config(root)`` in a child: the outcome (its value, or what it raised)."""
    return box.run([("gov.config.loader", "load_config", [support.path_arg(root)], {})])


def pathmap_findings(box, root):
    """``gov.check.pathmap.check(root)``: every tracked path in exactly one namespace."""
    return box.run([("gov.check.pathmap", "check", [support.path_arg(root)], {})]).value()


# --------------------------------------------------------------------------
# What came back
# --------------------------------------------------------------------------

def report_text(root, report):
    """The rebuild's report as text: its ``--json`` result and the record file the result names, if any."""
    text = json.dumps(report)
    record = report.get("record")
    if isinstance(record, str) and record:
        path = Path(record) if Path(record).is_absolute() else Path(root) / record
        if path.is_file():
            text += "\n" + path.read_text(encoding="utf-8", errors="replace")
    return text


def named(text, path):
    return path in text


def in_vocabulary(word, terms_by_table):
    """Whether an FTS5 table's terms spell ``word``, whatever the tokenizer: the word itself, a stem of it (a term at
    least four characters long that begins it, or that it begins), or every trigram of it."""
    word = word.lower()
    grams = {word[start:start + 3] for start in range(len(word) - 2)}
    for terms in terms_by_table.values():
        if word in terms or any(len(term) >= 4 and (word.startswith(term) or term.startswith(word)) for term in terms):
            return True
        if grams and grams <= terms:
            return True
    return False


# --------------------------------------------------------------------------
# The repository's own path map
# --------------------------------------------------------------------------

def matches(path, pattern):
    """``*`` stays inside one folder, ``**`` crosses folders (the language of the path map)."""
    parts = [re.escape(part).replace(r"\*", "[^/]*") for part in pattern.split("**")]
    return re.fullmatch(".*".join(parts), path) is not None


def repository_namespaces():
    document = yaml.safe_load((support.REPO_ROOT / support.PATH_MAP_REL).read_text(encoding="utf-8"))
    namespaces = document.get("namespaces") or {}
    assert isinstance(namespaces, dict) and namespaces, f"premise: {support.PATH_MAP_REL} names no namespaces"
    return namespaces


def tracked(prefix):
    done = subprocess.run(["git", "-C", str(support.REPO_ROOT), "ls-files", "-z", "--", prefix],
                          capture_output=True, text=True, check=True)
    return [path for path in done.stdout.split("\0") if path]


def holders(namespaces, path):
    return [name for name, entry in namespaces.items()
            if isinstance(entry, dict) and any(matches(path, pattern) for pattern in entry.get("paths") or [])]
