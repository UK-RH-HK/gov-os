"""The planted repository of the W2-131 acceptance tests, today's ``retrieve`` and the label oracle.

- ``build(root)``: a temporary git repository whose path map names a register of three entries (DEC-476, DEC-999,
  DEC-1082) with a preface and a section between two entries, a ticket whose closure holds a failure and a lesson
  record and DEC-476, and plain notes; its lexical index and record store built there. Every planted text uses words
  no other text holds, so a one-word question names one span.
- ``today()``: ``gov.retrieval.retrieve`` as ``w2/integrate`` held it when these tests were written (``TODAY_BLOB``,
  the blob of ``src/gov/retrieval/retrieve.py`` at ``TODAY_COMMIT``), loaded from git as a module of its own. The
  ticket's only source path is that file, so this module and the running tree's differ by the fix alone; both run
  on one store, in one process, with the same stand-ins.
- ``label(item)``: what S1 says a register item's id is, worked out from the planted register's text alone (an
  entry's lines are its heading to the line before the next heading, without the blank lines that end it), never
  from the code under test.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

TODAY_COMMIT = "262c488d2baf"  # w2/integrate when these tests were written (DEC-1082 (2), re-pin window 4)
TODAY_BLOB = "62b12493b443c28f82168d9909c8b5ddb2294b14"  # src/gov/retrieval/retrieve.py at TODAY_COMMIT

REGISTER = "docs/DECISION_REGISTER.md"
TICKET = "DAEO-t131"
TICKET_PATH = ".tickets/DAEO-t131.md"
FAILURE, FAILURE_PATH = "FAIL-131", "docs/failures/FAIL-131.md"
LESSON, LESSON_PATH = "LES-131", "docs/lessons/LES-131.md"
ENTRY_IDS = frozenset({"DEC-476", "DEC-999", "DEC-1082"})

# DEC-1082 is long: more than one chunk of the default chunker (1,200 characters), so a hit on its last chunk is a
# child whose parent (the whole entry) is expanded within the bundle budget. Only its last line holds "cardamom".
_LONG = "".join(f"- **Clause {n}:** the long rule keeps the pier's boards in order, plank by plank, row {n}.\n"
                for n in range(1, 31))
REGISTER_TEXT = (
    "# Decision register\n"
    "\n"
    "The register's preface keeps the almanac of the bay.\n"
    "\n"
    "### DEC-476 — The harbour lights\n"
    "- **Status:** ACCEPTED\n"
    "- **Decision:** The harbour keeps marigold lanterns at the breakwater.\n"
    "\n"
    "## Interlude\n"
    "\n"
    "Between the entries stands the tamarind clock.\n"
    "\n"
    "### DEC-999 — The quay ropes\n"
    "- **Status:** ACCEPTED\n"
    "- **Decision:** The quay holds juniper ropes.\n"
    "\n"
    "### DEC-1082 — The long rule\n"
    "- **Status:** ACCEPTED\n"
    f"{_LONG}"
    "- **Clause 31:** the long rule ends with the cardamom bell.\n"
)

FILES = {
    ".gitignore": ".gov-runtime/\n",
    "governance/project/path-map.yaml": f"decision_register: {REGISTER}\n",
    REGISTER: REGISTER_TEXT,
    TICKET_PATH: (f"---\nid: {TICKET}\ntype: task\nstatus: open\ndepends_on: [{FAILURE}, {LESSON}]\n"
                  "constrains: [DEC-476]\n---\n# The ticket\n\nThe ticket mends the beacon.\n"),
    FAILURE_PATH: (f"---\nid: {FAILURE}\ntype: failure\nstatus: ACTIVE\n---\n# A failure\n\n"
                   "The lantern went dark in the squall.\n"),
    LESSON_PATH: (f"---\nid: {LESSON}\ntype: lesson\nstatus: ACTIVE\n---\n# A lesson\n\n"
                  "Trim the lantern wick before a squall.\n"),
    "notes/lanterns.md": "".join(f"## Lantern note {n}\n\nLantern, lantern, lantern: the lantern row {n}.\n\n"
                                 for n in range(1, 7)),
    "notes/quay.md": "# The quay\n\nThe breakwater shelters the quay.\n",
}

# The questions asked of the planted repository: (case name, question, keyword arguments of ``retrieve``)
SCENARIOS = [
    ("dec-476-alone", "marigold", {}),
    ("dec-999-alone", "juniper", {}),
    ("the-preface", "almanac", {}),
    ("between-entries", "tamarind", {}),
    ("a-parent-expansion", "cardamom", {}),
    ("a-later-chunk-alone", "cardamom", {"bundle_budget": 300}),
    ("a-ticket-dec-424", "lantern", {"ticket": TICKET}),
    ("a-ticket-batched", "lantern", {"ticket": TICKET, "batch_size": 2}),
    ("an-id-at-radius-1", "breakwater", {"ids": ["DEC-476"], "radius": 1}),
]

_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid",
        "GIT_AUTHOR_DATE": "2026-11-06T12:00:00Z", "GIT_COMMITTER_DATE": "2026-11-06T12:00:00Z"}


def build(root: Path) -> Path:
    """The planted repository at ``root``, committed, its lexical index and record store built (the caller replaces
    the secret filter, as the unit tests do)."""
    from gov import store
    from gov.retrieval import lexical

    root.mkdir(parents=True, exist_ok=True)
    for rel, text in FILES.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    for args in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-q", "-m", "the planted repository"]):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True,
                       env={**_ENV, "HOME": str(root)})
    lexical.refresh(root)
    store.load(root)
    return root


def today():
    """``retrieve.py`` as ``TODAY_COMMIT`` held it, as a module of its own beside the running tree's."""
    source = subprocess.run(["git", "-C", str(REPO), "cat-file", "blob", TODAY_BLOB], check=True,
                            capture_output=True).stdout.decode("utf-8")
    spec = importlib.util.spec_from_loader("w2_131_today_retrieve", loader=None)
    module = importlib.util.module_from_spec(spec)
    exec(compile(source, f"retrieve.py@{TODAY_COMMIT}", "exec"), module.__dict__)  # noqa: S102 - our own blob
    return module


def line_of(text: str) -> int:
    """The 1-based line of the planted register that starts with ``text``."""
    return next(n for n, line in enumerate(REGISTER_TEXT.split("\n"), 1) if line.startswith(text))


def entry_spans() -> dict[str, tuple[int, int]]:
    """``id -> (first, last)`` of each entry of the planted register, read from its text alone: the heading to the
    line before the next heading, without the blank lines that end it."""
    lines = REGISTER_TEXT.split("\n")
    heads = [n for n, line in enumerate(lines) if re.match(r"#{1,6}\s", line)] + [len(lines)]
    spans = {}
    for at, end in zip(heads, heads[1:]):
        found = re.match(r"### (DEC-[0-9]{3,})[ :\-–—]", lines[at])
        if not found:
            continue
        last = end - 1
        while not lines[last].strip():
            last -= 1
        spans[found.group(1)] = (at + 1, last + 1)
    return spans


def label(item: dict) -> str:
    """S1: the id a register item carries: the entry whose lines hold its first line, else its chunk id."""
    first = item["start_line"]
    return next((rid for rid, (a, b) in entry_spans().items() if a <= first <= b), item["chunk_id"])


def pages(ask, query: str, kwargs: dict, most: int = 10) -> list[dict]:
    """The bundles of ``query``, the first and each its continuation gives, to the end (at most ``most``)."""
    found = [ask(query, **kwargs)]
    while found[-1]["continuation"] and len(found) < most:
        found.append(ask(query, continuation=found[-1]["continuation"], **kwargs))
    return found


def register_items(bundle: dict) -> list[dict]:
    return [item for item in bundle["evidence"] if item["path"] == REGISTER]


def without_register_ids(bundle: dict) -> dict:
    """The bundle with the ``id`` of each register item taken off: what S3 says the fix leaves unchanged."""
    return {**bundle, "evidence": [{key: value for key, value in item.items()
                                    if not (item["path"] == REGISTER and key == "id")}
                                   for item in bundle["evidence"]]}
