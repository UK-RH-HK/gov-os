"""The planted project and the readers of DEC-1068's index-time methods M2, M5 and M4 (``test_w2_32_dec1068_*``).

The settings are in ``governance/project/rebuild.yaml``, absent = off: ``chunk_code_by_definition`` (M2),
``chunk_register_by_entry`` (M5), ``lexical_split_identifiers`` (M4). The file is tracked, as this repository's is
(since ``dc8a2829``): each setting is written and committed, so the store sees the file's blob change (P-W2-32-11).
The governance files are kept out of the keyword index, so the keyword answers hold the planted files alone and do not
move with this repository's path map.

Rewrite-Reason: P-W2-32-11 (M5 re-scoped): each entry one chunk up to ``EMBED_LIMIT_CHARS``, a longer one split at its
own bullet or section boundaries; the settings file committed, not kept out of git.

``TODAY`` (``w2_32_dec1068_today.json``) is today's index of the planted files and today's keyword answers, recorded
on integrate's head ``bd87a8b2`` (``python3 w2_32_index_methods.py --record``): what "off" must give exactly.
"""

from __future__ import annotations

import ast
import json
import re
import sqlite3
from pathlib import Path

import yaml

import w2_32_support as s

SETTINGS_REL = "governance/project/rebuild.yaml"
M2, M5, M4 = "chunk_code_by_definition", "chunk_register_by_entry", "lexical_split_identifiers"
KEYS = (M2, M5, M4)
CONTROL = "slow_after_s: 1800\n"  # a key of the file that is none of the three (W2-76's watch)
TODAY_FILE = Path(__file__).resolve().parent / "w2_32_dec1068_today.json"

# ---- M2: a Python file whose class lines lie inside module runs today ------------------------------------------

CODE_REL = "app/quay.py"
_REPORT = "".join(f"        lines.append(\"berth {i:02d}: \" + str(self.rows[{i} % len(self.rows)]))\n"
                  for i in range(24))
CODE_TEXT = (
    '"""The quay\'s berth ledger."""\n'
    "\n"
    "import json\n"
    "\n"
    "LIMIT = 4\n"
    "\n"
    "\n"
    "def open_berth(number):\n"
    '    """Open berth ``number``."""\n'
    '    return {"berth": number, "open": True}\n'
    "\n"
    "\n"
    "class BerthLedger:\n"
    '    """Keeps the berths in a ledger."""\n'
    "\n"
    '    kind = "ledger"\n'
    "\n"
    "    def __init__(self):\n"
    "        self.rows = []\n"
    "\n"
    "    def add(self, row):\n"
    "        self.rows.append(row)\n"
    "        return len(self.rows)\n"
    "\n"
    "    # the long one: more than one chunk\n"
    "    def report(self):\n"
    "        lines = []\n"
    + _REPORT +
    '        return "\\n".join(lines)\n'
    "\n"
    "    def dump(self):\n"
    "        return json.dumps(self.rows)\n"
    "\n"
    "\n"
    "WATCH = \"night\"\n"
    "\n"
    "\n"
    "class TideTable:\n"
    '    """The tide table."""\n'
    "\n"
    "    def high(self, day):\n"
    "        def hour(n):\n"
    "            return n * 2\n"
    "        return hour(day)\n"
    "\n"
    "\n"
    "def close_berth(number):\n"
    '    return {"berth": number, "open": False}\n')

# ---- M4: identifiers whose parts no other planted text holds as a word ---------------------------------------

SNAKE_REL, CAMEL_REL, DOTTED_REL, PATH_REL = ("docs/quay-orders.md", "app/berths.py", "docs/lamp-room.md",
                                              "docs/night-crossing.md")
IDENT_FILES = {
    SNAKE_REL: "# Quay orders\n\nBefore the tide turns the warden calls rebuild_slot_seed once.\n",
    CAMEL_REL: '"""The berths kept between tides."""\n\n\nclass SeededRebuild:\n    """Holds the berth plan."""\n\n'
               "    def plan(self):\n        return \"north quay\"\n",
    DOTTED_REL: "# Lamp room\n\nThe keeper imports gov.lantern.wick_trimmer before dusk.\n",
    PATH_REL: "# Night crossing\n\nRun tools/heavy_ballast.sh before the crossing.\n",
}
# (query, the file, the line that holds it): a part of an identifier, or of a path's segment, today found nowhere
# ('/', '.' and '-' already separate tokens today; '_' and a capital inside a word do not).
PARTS = (
    ("seed", SNAKE_REL, 3),  # rebuild_slot_seed
    ("Seeded", CAMEL_REL, 4),  # SeededRebuild
    ("Rebuild", CAMEL_REL, 4),  # SeededRebuild
    ("trimmer", DOTTED_REL, 3),  # gov.lantern.wick_trimmer
    ("ballast", PATH_REL, 3),  # tools/heavy_ballast.sh
)
WHOLES = (
    ("rebuild_slot_seed", SNAKE_REL, 3),
    ("SeededRebuild", CAMEL_REL, 4),
    ("gov.lantern.wick_trimmer", DOTTED_REL, 3),
    ("tools/heavy_ballast.sh", PATH_REL, 3),
)
WORDS = ("lantern", "ledger rules", "copper tokens")  # plain words: the same answer with every setting

# ---- M5: a register (the path map's ``decision_register``) ---------------------------------------------------

REGISTER_REL = "docs/DECISION_REGISTER.md"
_RULES = "".join(f"- Ledger rule {i:03d}: the clerk enters the berth, the hull and the hour of mooring in ink,\n"
                 f"  and the warden countersigns the page before the bell of rule {i:03d} is rung.\n"
                 f"  A copy goes to the harbour office.\n" for i in range(170))
_BOOK = "".join(f"- Berth {i:03d}: the mooring book names the vessel, her master and the tide she came in on.\n"
                for i in range(96))
REGISTER_TEXT = (
    "# Planted decision register\n"
    "\n"
    "Entries are the planted harbour decisions.\n"
    "\n"
    "## 1. Harbour decisions\n"
    "\n"
    "### DEC-901 — The lamp hours\n"
    "- **Status:** ACCEPTED\n"
    "- **Decision:** the quay lamps burn from dusk to the second bell.\n"
    "\n"
    "### DEC-902 — The berth tokens\n"
    "- **Status:** ACCEPTED\n"
    "- **Decision:** berth fees are paid in copper tokens; the gatehouse settings read:\n"
    "\n"
    "```yaml\n"
    "# the gatehouse settings\n"
    "tokens: copper\n"
    "# kept by the warden\n"
    "warden: night\n"
    "```\n"
    "\n"
    "- **Basis:** silver marks were refused by the board.\n"
    "\n"
    "### DEC-903 — The mooring book\n"
    "- **Status:** ACCEPTED\n"
    "- **Decision:** the mooring book, one berth per line:\n"
    + _BOOK +
    "\n"
    "### DEC-904 — The ledger rules\n"
    "- **Status:** ACCEPTED\n"
    "- **Decision:** the ledger rules of the first book:\n"
    + _RULES[:len(_RULES) // 2] +
    "\n"
    "The ledger rules of the second book:\n"
    + _RULES[len(_RULES) // 2:] +
    "\n"
    "## 2. Later decisions\n"
    "\n"
    "### DEC-905 — The night watch\n"
    "- **Status:** PROPOSED\n"
    "- **Decision:** two wardens walk the quay at night, as the lamp hours of DEC-901 allow.\n"
    "\n"
    "## 3. Change log\n"
    "\n"
    "| Version | Date | Change |\n"
    "|---|---|---|\n"
    "| 0.1 | 2026-11-04 | planted |\n")
LIMIT_CHARS = 10_000  # the embedder's limit, ``semantic.EMBED_LIMIT_CHARS`` (P-W2-32-11)
# One chunk each: a short entry, one holding a fenced block with '#' lines, one of about 9,000 characters (under the
# limit, nine chunks today). Split within it: one of about 34,000 characters, its bullets three lines each.
WHOLE_ENTRIES, LONG_ENTRY = ("DEC-901", "DEC-902", "DEC-903", "DEC-905"), "DEC-904"

FILES = {**s.NOTES, CODE_REL: CODE_TEXT, REGISTER_REL: REGISTER_TEXT, **IDENT_FILES}
PYTHON = (CODE_REL, CAMEL_REL)
PLANTED = tuple(sorted(FILES))


# ---- the project and its settings -----------------------------------------------------------------------------

def plant(project):
    """The planted project: ``FILES``; the code in a namespace of its own; the register named; the governance files
    out of the keyword index; the settings file out of git."""
    project = s.plant(project, FILES)
    document = yaml.safe_load((Path(project) / s.PATH_MAP_REL).read_text(encoding="utf-8"))
    document["namespaces"]["code"] = s.namespace(["app/**"], "embedded")
    document["namespaces"]["project"]["lexical_policy"] = "not indexed"
    document["decision_register"] = REGISTER_REL
    s.write(project, s.PATH_MAP_REL, yaml.safe_dump(document, sort_keys=False))
    s.commit(project, "the code, the register named, the governance files out of the keyword index")
    return project


def settle(project, text):
    """Write ``rebuild.yaml`` as ``text`` (``None``: no file) and commit it: the file is tracked (P-W2-32-11)."""
    path = Path(project) / SETTINGS_REL
    if text is None:
        if path.exists():
            path.unlink()
    else:
        s.write(project, SETTINGS_REL, text)
    s.commit(project, "the rebuild settings")


def setting(key, value, control=True):
    """The text of ``rebuild.yaml`` with ``key: value`` (written as is), after the control key."""
    return (CONTROL if control else "") + f"{key}: {value}\n"


# ---- reading the index -----------------------------------------------------------------------------------------

def index(project):
    """The keyword index of the planted files: ``chunks`` as ``[path, start, end, parent kind, parent start, parent
    end, chunk id, parent id]`` by path and line, and ``parents`` as ``[path, kind, start, end, parent id]``."""
    connection = sqlite3.connect(f"file:{Path(project) / s.STORE_REL}?mode=ro", uri=True)
    try:
        parents = {row[0]: row[1:] for row in connection.execute(
            "SELECT parent_id, path, kind, start_line, end_line FROM lexical_parent")}
        rows = connection.execute("SELECT chunk_id, path, start_line, end_line, parent_id FROM lexical_chunk").fetchall()
    finally:
        connection.close()
    chunks = sorted([path, start, end, parents.get(parent_id, (None,) * 4)[1], parents.get(parent_id, (None,) * 4)[2],
                     parents.get(parent_id, (None,) * 4)[3], chunk_id, parent_id]
                    for chunk_id, path, start, end, parent_id in rows if path in PLANTED)
    kept = sorted([path, kind, start, end, parent_id] for parent_id, (path, kind, start, end) in parents.items()
                  if path in PLANTED)
    return {"chunks": chunks, "parents": kept}


def spans(chunks, paths=None):
    """The chunks without their ids: ``(path, start, end, parent kind, parent start, parent end)``."""
    return [tuple(chunk[:6]) for chunk in chunks if paths is None or chunk[0] in paths]


def search(box, project, query, refresh=False):
    """The keyword route's answer to ``query``, the planted files' part: ``available``, ``reason``, ``hits`` as
    ``[path, line, text]`` and ``ranked`` as ``[path, start, end, exact]`` in order."""
    answer = s.result(box.call("lexical_search", root=str(project), query=query, refresh=refresh))
    return {"available": answer.get("available"), "reason": answer.get("reason"),
            "hits": [[hit["path"], hit["line"], hit["text"]] for hit in answer.get("hits") or []
                     if hit["path"] in PLANTED],
            "ranked": [[item["path"], item["start_line"], item["end_line"], item.get("exact")]
                       for item in answer.get("ranked") or [] if item["path"] in PLANTED]}


QUERIES = tuple(dict.fromkeys([query for query, _, _ in PARTS + WHOLES] + list(WORDS)))


def answers(box, project):
    return {query: {key: value for key, value in search(box, project, query).items() if key in ("hits", "ranked")}
            for query in QUERIES}


def today():
    return json.loads(TODAY_FILE.read_text(encoding="utf-8"))


# ---- what each method asks ---------------------------------------------------------------------------------------

def _lines(rel):
    return FILES[rel].splitlines()


def definitions(rel):
    """``line -> name`` of each top-level ``def``/``class`` and each method of the Python file ``rel``."""
    tree = ast.parse(FILES[rel])
    found = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            found[node.lineno] = node.name
            if isinstance(node, ast.ClassDef):
                found.update({item.lineno: f"{node.name}.{item.name}" for item in node.body
                              if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))})
    return found


def _lead_in(lines, start, line):
    """Whether the lines from ``start`` up to before ``line`` are blank or comments alone."""
    return all(not text.strip() or text.lstrip().startswith("#") for text in lines[start - 1:line - 1])


def _covered(rel, chunks, first=1, last=None):
    lines = _lines(rel)
    last = last or len(lines)
    held = {number for chunk in chunks for number in range(chunk[1], chunk[2] + 1)}
    return [number for number in range(first, last + 1) if lines[number - 1].strip() and number not in held]


def m2_problems(chunks, parents):
    """What breaks M2 in the index: a chunk of a Python file must begin at each top-level def/class and method (the
    lines before it in the chunk blank or comments alone), no chunk runs on into a definition, every line is in a
    chunk, today's parents are kept, and each chunk lies inside the parent it names."""
    problems = []
    kept = {(path, kind, start, end) for path, kind, start, end, _ in parents}
    for rel in PYTHON:
        lines, mine = _lines(rel), [chunk for chunk in chunks if chunk[0] == rel]
        for line, name in sorted(definitions(rel).items()):
            if not any(chunk[1] <= line <= chunk[2] and _lead_in(lines, chunk[1], line) for chunk in mine):
                problems.append(f"{rel}: no chunk begins at {name} (line {line}): "
                                f"{[c[1:3] for c in mine if c[1] <= line <= c[2]]}")
            into = [chunk[1:3] for chunk in mine if chunk[1] < line <= chunk[2] and not _lead_in(lines, chunk[1], line)]
            if into:
                problems.append(f"{rel}: chunks {into} run on into {name} (line {line})")
        missing = _covered(rel, mine)
        if missing:
            problems.append(f"{rel}: lines {missing[:8]} are in no chunk")
        for chunk in mine:
            if chunk[3] is None or not (chunk[4] <= chunk[1] and chunk[2] <= chunk[5]):
                problems.append(f"{rel}: chunk {chunk[1:3]} is not inside the parent it names {chunk[3:6]}")
    for path, kind, start, end, _ in today()["parents"]:
        if path in PYTHON and (path, kind, start, end) not in kept:
            problems.append(f"{path}: today's {kind} parent {start}-{end} is not kept")
    return problems


def entries():
    """``id -> (first line, last line that is not blank, the line before the next heading)`` of each register entry:
    from its ``### DEC-`` heading to the next heading outside a fenced block (the store's rule, ``register_entries``)."""
    lines, heads, ends, fence = _lines(REGISTER_REL), [], [], None
    for number, line in enumerate(lines, 1):
        mark = re.match(r" {0,3}(`{3,}|~{3,})", line)
        if fence is not None:
            if mark and mark.group(1).startswith(fence) and not line[mark.end():].strip():
                fence = None
            continue
        if mark:
            fence = mark.group(1)
        elif re.match(r"#{1,6}(\s|$)", line):
            ends.append(number)
            if line.startswith("### DEC-"):
                heads.append(number)
    found = {}
    for head in heads:
        region = next((end for end in ends if end > head), len(lines) + 1) - 1
        last = region
        while last > head and not lines[last - 1].strip():
            last -= 1
        found[lines[head - 1].split()[1]] = (head, last, region)
    return found


_BULLET = re.compile(r" {0,3}(?:[-*+]|\d+[.)])\s")


def chars(rel, start, end):
    """The characters of lines ``start`` to ``end`` of ``rel``, their line ends counted."""
    return len("".join(FILES[rel].splitlines(keepends=True)[start - 1:end]))


def _boundary(lines, head, number):
    """Whether line ``number`` of an entry headed at ``head`` begins one of its own parts: the heading, a bullet of
    its own (not an indented continuation), or a line after a blank line (a section of it)."""
    text = lines[number - 1]
    return number == head or bool(_BULLET.match(text)) or (bool(text.strip()) and not lines[number - 2].strip())


def m5_problems(chunks):
    """What breaks M5 (P-W2-32-11) in the index: each entry's chunks lie inside it (no chunk spans two entries, or an
    entry and what is not it) and inside the parent each names, and cover it; an entry within ``LIMIT_CHARS`` is one
    chunk holding it whole; the longer one is more than one, each at most ``LIMIT_CHARS``, each beginning at one of
    the entry's own bullet or section boundaries and ending just before one (or at the entry's end)."""
    problems = []
    lines = _lines(REGISTER_REL)
    mine = [chunk for chunk in chunks if chunk[0] == REGISTER_REL]
    for entry, (head, last, region) in entries().items():
        touching = sorted((chunk for chunk in mine if chunk[1] <= region and chunk[2] >= head), key=lambda c: c[1])
        spans_of = [c[1:3] for c in touching]
        outside = [chunk[1:3] for chunk in touching if chunk[1] < head or chunk[2] > region]
        if outside:
            problems.append(f"{entry} (lines {head}-{last}): chunks {outside[:4]} reach past the entry")
        for chunk in touching:
            if chunk[3] is None or not (chunk[4] <= chunk[1] and chunk[2] <= chunk[5]):
                problems.append(f"{entry}: chunk {chunk[1:3]} is not inside the parent it names {chunk[3:6]}")
        missing = _covered(REGISTER_REL, touching, head, last)
        if missing:
            problems.append(f"{entry}: lines {missing[:8]} are in no chunk of it")
        if entry in WHOLE_ENTRIES:
            if len(touching) != 1 or touching[0][1] != head or touching[0][2] < last:
                problems.append(f"{entry} (lines {head}-{last}, {chars(REGISTER_REL, head, last)} characters, within "
                                f"{LIMIT_CHARS}) is not one chunk holding it whole: {spans_of[:10]}")
            continue
        if len(touching) < 2:
            problems.append(f"{entry} ({chars(REGISTER_REL, head, last)} characters) is not split within it: "
                            f"{spans_of}")
        for _, start, end, *_ in touching:
            first = next((n for n in range(start, end + 1) if lines[n - 1].strip()), start)
            if not _boundary(lines, head, first):
                problems.append(f"{entry}: the part {start}-{end} begins inside a bullet: {lines[first - 1]!r}")
            after = end + 1
            if after <= last and lines[after - 1].strip() and not _boundary(lines, head, after):
                problems.append(f"{entry}: the part {start}-{end} ends inside a bullet, before {lines[after - 1]!r}")
            if chars(REGISTER_REL, start, end) > LIMIT_CHARS:
                problems.append(f"{entry}: the part {start}-{end} holds {chars(REGISTER_REL, start, end)} characters, "
                                f"above {LIMIT_CHARS}")
    return problems


def m4_problems(box, project, refresh=False):
    """What breaks M4: a keyword search for a part of an identifier or of a path's segment finds the chunk (in the
    ranked list) and the line (a hit, its text the file's line)."""
    problems = []
    for query, rel, line in PARTS:
        answer = search(box, project, query, refresh=refresh)
        if not answer["available"]:
            problems.append(f"{query!r}: the keyword route answered unavailable ({answer['reason']})")
            continue
        if not any(item[0] == rel and item[1] <= line <= item[2] for item in answer["ranked"]):
            problems.append(f"{query!r}: the chunk of {rel} holding line {line} is not in the ranked list "
                            f"{answer['ranked'][:6]}")
        if [rel, line, _lines(rel)[line - 1]] not in answer["hits"]:
            problems.append(f"{query!r}: {rel}:{line} ({_lines(rel)[line - 1]!r}) is not a hit: {answer['hits'][:6]}")
    return problems


def record():
    """Record ``TODAY`` with the code at hand (run on integrate's head only)."""
    import tempfile

    with tempfile.TemporaryDirectory() as place:
        stand_in = s.OllamaStandIn({s.PIN_MODEL: s.PIN_DIGEST})
        try:
            box = s.Box(Path(place) / "box", stand_in.host)
            project = plant(Path(place) / "project")
            box.built(project)
            got = {"made": "today's index and keyword answers of the planted files (w2_32_index_methods.record)",
                   **index(project), "answers": answers(box, project)}
        finally:
            stand_in.close()
    TODAY_FILE.write_text(json.dumps(got, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["--record"]:
        record()
