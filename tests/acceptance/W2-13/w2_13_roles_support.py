"""Support code for W2-13's S5 cases: search respects role separation (DEC-1065 (2); not a test module).

S5: ``gov retrieve``'s results (every route) and ``gov context``'s supplementary block are filtered by the caller's
``role_paths`` (``GOV_ROLE`` or ``--role``, and ``GOV_TICKET``), with the same path checks as the guard's: an engineer
never receives its own ticket's acceptance tests, a test designer never the ticket's new code; what is filtered is
named in the bundle (how many, by which rule), never dropped silently; no ``role_paths`` section means no filter.

The guard's checks, as the tests take them (``.claude/hooks/role_reads.py``, DEC-1052 G-14, DEC-1056, DEC-1063):

- ``role_paths.<role>.reads_denied`` in the path map ``governance/project/path-map.yaml``; this project's own block
  is ``engineer: ["{ticket_tests}"]`` and ``independent-test-designer: ["{ticket_impl}"]``, planted as it is;
- the session's ticket is ``GOV_TICKET``, found in ``.tickets/`` by its file name (or its ``wbs_id``);
- ``{ticket_tests}``: the ticket's own folder ``tests/acceptance/<WBS>/**``, and each file in another ticket's
  acceptance folder that a test designer's commit made for the ticket touched (``Task:`` names the ticket, ``Role:
  independent-test-designer``); for a ``class: coordination`` ticket its own folder only;
- ``{ticket_impl}``: the ticket's ``allowed_paths`` but ``tests/acceptance/``, less the shared test files (any
  ``conftest.py``, ``__init__.py``, ``*support*.py``, ``*helper*.py``), in the engineer's tree
  ``~/gov-os-worktrees/<WBS>``; in that tree only the files its branch changes against ``w2/integrate`` (the rest
  there is integrated code). ``~`` is the folder ``HOME`` names, so each case plants its own home.

Every project is planted from nothing and indexed by ``gov rebuild --no-embeddings``: the record store and the
lexical index only. No embedder, reranker or model is started: the child's environment is the W2-13 scratch one
(an empty ``HOME`` but for the planted tree, a ``PATH`` of git, gitleaks and python3, the Ollama hosts at a dead
port), so the semantic route reports itself unavailable, as DEC-1065 (1) wants, and the keyword route answers.

Each case first makes the same call with no role (no ``GOV_ROLE``, no ``--role``) and checks that the file the
filter must hold back does come back then: the premise, so a red is never a project that does not hold the file.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

import w2_13_support as support

ENGINEER, DESIGNER = "engineer", "independent-test-designer"
ROLE_PATHS = {ENGINEER: {"reads_denied": ["{ticket_tests}"]}, DESIGNER: {"reads_denied": ["{ticket_impl}"]}}
RULE_WORDS = ("role_paths", "reads_denied")

# ---- the tickets
OWN_ID, OWN_WBS = "DAEO-s5own", "W9-01"  # the session's ticket (an implementation ticket)
OTHER_ID, OTHER_WBS = "DAEO-s5other", "W9-02"  # another ticket
COORD_ID, COORD_WBS = "DAEO-s5coord", "W9-00"  # a coordination ticket
RECORD_ID, RECORD_REL = "DEC-0101", "docs/decisions/dec-0101.md"  # the tickets' source (gov context needs one)
ALLOWED = ["src/harbour/**", "tests/unit/harbour/**", "docs/changes/W9-01-evidence.md"]

# ---- the words: every planted file below holds all of them, so each one answers every question
WORDS = ("barnacle", "lighthouse", "gauge")
QUESTION = "barnacle lighthouse gauge"
EXACT = "QZ-7731"  # an id-shaped string every planted file holds: the exact route's question
QUESTIONS = {"plain words": QUESTION, "an exact identifier": EXACT}
TITLE = "Barnacle gauge calibration"
KPI = "The lighthouse barnacle gauge reads true at every tide"


def _body(marker, kind="py"):
    """A file that answers every question, with its own marker word (held by no other file) in its body."""
    if kind == "md":
        return (f"# Barnacle lighthouse gauge\n\nThe barnacle gauge at the lighthouse reads {EXACT}.\n"
                f"Marker: {marker}.\n")
    return (f'"""Barnacle lighthouse gauge: {marker}."""\n\nGAUGE = "{EXACT}"\n\n\n'
            f"def test_barnacle_lighthouse_gauge():\n    # the barnacle gauge at the lighthouse: {marker}\n"
            f"    assert GAUGE == \"{EXACT}\"\n")


def _code(marker):
    return (f'"""The barnacle lighthouse gauge ({marker})."""\n\nGAUGE = "{EXACT}"\n\n\n'
            f"def barnacle_lighthouse_gauge():\n    # the barnacle gauge at the lighthouse: {marker}\n"
            f"    return GAUGE\n")


# ---- project A: the engineer's cases (a plain project, outside any engineer's tree)
OWN_TESTS = {f"tests/acceptance/{OWN_WBS}/test_w9_01_gauge.py": "zanzibarite",
             f"tests/acceptance/{OWN_WBS}/README.md": "quillwort"}
OTHER_TESTS = {f"tests/acceptance/{OTHER_WBS}/test_w9_02_gauge.py": "marmoset"}
LINKED_OWN = {f"tests/acceptance/{OTHER_WBS}/test_w9_02_revised_for_w9_01.py": "pangolin"}  # revised for W9-01
COORD_TESTS = {f"tests/acceptance/{COORD_WBS}/test_w9_00_gauge.py": "ocelot"}
LINKED_COORD = {f"tests/acceptance/{OTHER_WBS}/test_w9_02_revised_for_w9_00.py": "tamarind"}  # revised for W9-00
INTEGRATED = {"src/harbour/gauge.py": "cormorant", "tests/unit/harbour/test_gauge.py": "kestrel",
              "src/quay/berth.py": "heron"}

# ---- project B: the test designer's case, in the engineer's tree ~/gov-os-worktrees/W9-01
NEW_CODE = {"src/harbour/calibrate.py": "wolverine", "tests/unit/harbour/test_calibrate.py": "narwhal",
            "docs/changes/W9-01-evidence.md": "axolotl"}  # the engineer's new work (code, unit test, document)
NEW_SHARED = {"tests/unit/harbour/harbour_support.py": "capybara"}  # a shared test file: stays readable (c3)
OTHER_NEW = {"src/quay/mooring.py": "flamingo"}  # changed on the branch, outside the ticket's paths: not its work


def ticket(ticket_id, wbs, title, kpi, allowed, klass="implementation"):
    front = {"id": ticket_id, "status": "in_progress", "type": "task", "wbs_id": wbs, "external-ref": wbs,
             "title": title, "class": klass, "state_class": "AUTHORITATIVE", "role": "engineer",
             "allowed_paths": allowed, "kpis": {"success": [kpi], "failure": []}, "sources": [RECORD_ID],
             "acceptance_tests": {"path": f"tests/acceptance/{wbs}/"}}
    return f"---\n{yaml.safe_dump(front, sort_keys=False)}---\n# {wbs} {title}\n\nPlanted by W2-13's S5 cases.\n"


def adopt(project, role_paths=True):
    """The W2-13 path map and gitleaks rules, with this project's ``role_paths`` block planted as it stands (or
    none: no section, no filter)."""
    support.adopt(project, embedded=False)
    path = Path(project) / support.PATH_MAP_REL
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    document.pop("role_paths", None)
    if role_paths:
        document["role_paths"] = ROLE_PATHS
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")


def _common(project, role_paths=True):
    adopt(project, role_paths)
    support.write(project, RECORD_REL, support.record(RECORD_ID, "Harbour instruments are calibrated in spring.",
                                                       f"{RECORD_ID} Harbour instruments"))
    support.write(project, f".tickets/{OWN_ID}.md", ticket(OWN_ID, OWN_WBS, TITLE, KPI, ALLOWED))
    support.write(project, f".tickets/{OTHER_ID}.md",
                  ticket(OTHER_ID, OTHER_WBS, "Quay berths", "The quay berths are numbered", ["src/quay/**"]))
    support.write(project, f".tickets/{COORD_ID}.md",
                  ticket(COORD_ID, COORD_WBS, TITLE, KPI, ["docs/plan/**"], klass="coordination"))
    for rel, marker in INTEGRATED.items():
        support.write(project, rel, _code(marker) if rel.startswith("src/") else _body(marker))


def _designer_commit(project, files, task):
    """One non-merge commit by a test designer for ``task`` (the trailers the guard's linked_tests reads)."""
    for rel, marker in files.items():
        support.write(project, rel, _body(marker))
    support.git(project, "add", "-A")
    support.git(project, "commit", "-q", "-m", f"tests revised for {task}\n\nTask: {task}\n"
                                               f"Role: independent-test-designer\n")


def build_engineer_project(project, role_paths=True):
    """Project A: the tickets, their acceptance tests (own, another's, a coordination ticket's), the files revised in
    another ticket's folder for W9-01 and for the coordination ticket, and integrated code. Not indexed."""
    project = Path(project)
    project.mkdir(parents=True, exist_ok=True)
    support.git(project, "init", "-q", "-b", "main")
    _common(project, role_paths)
    for files in (OWN_TESTS, OTHER_TESTS, COORD_TESTS):
        for rel, marker in files.items():
            support.write(project, rel, _body(marker, "md" if rel.endswith(".md") else "py"))
    support.commit(project, "the S5 project")
    _designer_commit(project, LINKED_OWN, OWN_ID)
    _designer_commit(project, LINKED_COORD, COORD_ID)
    return project


def engineer_tree(home):
    """Where the guard places the engineer's tree of W9-01 for a process whose ``HOME`` is ``home``."""
    return Path(home) / "gov-os-worktrees" / OWN_WBS


def build_designer_project(home):
    """Project B, at ``~/gov-os-worktrees/W9-01``: ``w2/integrate`` holds the integrated code (the ticket's paths
    included); the branch ``w2/W9-01``, checked out, adds the engineer's new work. Not indexed."""
    project = engineer_tree(home)
    project.mkdir(parents=True, exist_ok=True)
    support.git(project, "init", "-q", "-b", "w2/integrate")
    _common(project)
    support.write(project, f"tests/acceptance/{OTHER_WBS}/test_w9_02_gauge.py", _body("marmoset"))
    support.commit(project, "the integrated code")
    support.git(project, "checkout", "-q", "-b", f"w2/{OWN_WBS}")
    for files in (NEW_CODE, NEW_SHARED, OTHER_NEW):
        for rel, marker in files.items():
            support.write(project, rel, _code(marker) if rel.startswith("src/") else
                          _body(marker, "md" if rel.endswith(".md") else "py"))
    support.commit(project, "W9-01: the engineer's new work")
    return project


# --------------------------------------------------------------------------
# The calls
# --------------------------------------------------------------------------

def env(box, home=None, role=None, ticket_id=None):
    """The scratch environment (a dead embedder host), with ``GOV_ROLE`` and ``GOV_TICKET`` when given."""
    extra = {}
    if home is not None:
        extra["HOME"] = str(home)
    if role is not None:
        extra["GOV_ROLE"] = role
    if ticket_id is not None:
        extra["GOV_TICKET"] = ticket_id
    return box.scratch_env(**extra)


def rebuild(box, root, home=None):
    """``gov rebuild --no-embeddings --json``: the record store and the lexical index, no embedder asked."""
    run = box.gov("rebuild", "--json", "--no-embeddings", "--root", str(root), env=env(box, home),
                  timeout=support.MEASURE_TIMEOUT_S)
    result = run.result()
    assert result.get("stores", {}).get("lexical", {}).get("status") == "recreated", \
        f"premise: gov rebuild did not recreate the lexical index: {result!r}"
    return root


def call(box, how, root, command, *args, role=None, ticket_id=None, home=None):
    """``gov <command> --json --root <root> <args>`` as ``role``: ``how`` is ``env`` (``GOV_ROLE``) or ``flag``
    (``--role``); ``GOV_TICKET`` is always the environment's. No role: neither. The envelope's result."""
    flag = ["--role", role] if role is not None and how == "flag" else []
    run = box.gov(command, "--json", "--root", str(root), *flag, *args,
                  env=env(box, home, role if how == "env" else None, ticket_id))
    return run.result()


def retrieve(box, how, root, question, **kwargs):
    """A batch that holds every chunk of the small project: what is kept or held back is the filter's, never the
    gather's cut."""
    return call(box, how, root, "retrieve", "--batch-size", str(support.BATCH_LARGE), question, **kwargs)


def context(box, how, root, target, **kwargs):
    """``gov context <target>``: the packet, its supplementary block within the default budget."""
    return call(box, how, root, "context", target, **kwargs)


# --------------------------------------------------------------------------
# What came back
# --------------------------------------------------------------------------

def bundle_paths(bundle):
    """The paths a bundle returns or offers: its evidence, its expansions and the chunks it leaves for a further
    batch (its ``NOT_GATHERED`` gaps)."""
    found = [item.get("path") for item in bundle.get("evidence") or []]
    found += [item.get("path") for item in bundle.get("expansions") or []]
    found += [gap.get("path") for gap in bundle.get("gaps") or [] if gap.get("path")]
    return set(filter(None, found))


def evidence_paths(bundle):
    return {item.get("path") for item in bundle.get("evidence") or []}


def supplementary_paths(packet):
    """The paths ``gov context``'s supplementary block returns or offers: its items, its further batch and the items
    its batches read."""
    found = [item.get("path") for item in packet.get("supplementary") or []]
    found += [item.get("path") for item in packet.get("further_batch") or []]
    found += [item.get("path") for batch in packet.get("supplementary_batches") or []
              for item in batch.get("items") or []]
    return set(filter(None, found))


def stacked_paths(packet):
    return {item.get("path") for item in packet.get("supplementary") or []}


def markers_in(result, files):
    """The marker words of ``files`` (``path -> marker``) that the result holds anywhere, its text included."""
    text = json.dumps(result)
    return sorted(marker for marker in files.values() if re.search(rf"\b{re.escape(marker)}\b", text))


def _cited(node):
    """A returned item (a path with its text): never a filter's record, whatever its text holds."""
    return isinstance(node, dict) and "text" in node and "path" in node


CONTENT_KEYS = frozenset({"text", "ticket_text", "supplementary_query", "body", "query"})  # the project's words


def _mentions(value, rules):
    """A one-line string that names a rule; a text of several lines is a document's, not a filter's naming."""
    return isinstance(value, str) and "\n" not in value and any(rule in value for rule in rules)


def _count(value):
    return type(value) is int and value > 0


def filter_records(result, rules):
    """The places a result names a filter by one of ``rules`` (strings, such as ``role_paths`` or the denied
    glob) with how many it held back: a mapping that names a rule (a key or a value) beside a positive count; a
    mapping from a rule to a positive count; or a non-empty list of entries that each name a rule (one per item
    held back). Cited items (a path and its text), the fields that carry the project's own words (``CONTENT_KEYS``)
    and texts of several lines are passed over: they are the project's, not the filter's."""
    found = []

    def walk(node, where):
        if _cited(node):
            return
        if isinstance(node, dict):
            node = {k: v for k, v in node.items() if k not in CONTENT_KEYS}
            names = any(_mentions(k, rules) or _mentions(v, rules) or
                        (isinstance(v, list) and any(_mentions(x, rules) for x in v)) for k, v in node.items())
            counted = any(_count(v) for k, v in node.items() if "line" not in str(k))
            if names and counted:
                found.append((where, node))
            for k, v in node.items():
                if _mentions(k, rules) and _count(v):
                    found.append((f"{where}.{k}", {k: v}))
                walk(v, f"{where}.{k}")
        elif isinstance(node, list):
            if node and all(isinstance(x, dict) and not _cited(x) and any(_mentions(v, rules) for v in x.values())
                            for x in node):
                found.append((where, node))
            for i, x in enumerate(node):
                walk(x, f"{where}[{i}]")

    walk(result, "result")
    return found


def rules_for(role, *globs):
    """What naming the rule may say: the path map's section and key, the role's entry, or the glob it expands to."""
    return (*RULE_WORDS, *ROLE_PATHS[role]["reads_denied"], *globs)


def shown(result):
    return json.dumps(result, indent=1)[-6000:]
