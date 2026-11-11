"""The planted repository of the W2-133 acceptance tests, today's code and the label oracle.

- ``build(root)``: a temporary git repository whose path map names a register in plain text
  (``docs/DECISION_REGISTER.txt``): a preface, a superseded DEC-100, DEC-101, a section between two entries, DEC-476;
  and a note. A register that is not Markdown is one parent, the whole file, cut by size alone (``chunking.parents``:
  "anything else: the module"), so an expanded parent spans DEC-100 and then DEC-101 (S1), and a chunk can start in
  the section between two entries and run into DEC-476 (S2). A Markdown register is cut at every heading, so neither
  can happen there today (W2-131's README, N-3). Every planted text uses words no other text holds, so a one-word
  question names one chunk.
- ``today()``: ``retrieve.py`` and ``register.py`` as ``w2/integrate`` held them when these tests were written
  (``TODAY_BLOBS``, read from git), each loaded as a module of its own beside the running tree's. They are the
  ticket's only source paths, so the two pipelines differ by the fix alone.
- ``entry_spans()`` and ``label(item)``: an entry's lines and the id S1 and S2 say an item carries, worked out from
  the planted register's text alone (an entry's lines are its heading to the line before the next heading, without
  the blank lines that end it), never from the code under test.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "src"
if importlib.util.find_spec("gov") is None:  # a PYTHONPATH given names the tree under test; else this one
    sys.path.insert(0, str(SRC))

TODAY_COMMIT = "a4e713517cac"  # w2/integrate when these tests were written (DEC-1083, re-pin window 4)
TODAY_BLOBS = {  # the ticket's source paths at TODAY_COMMIT
    "retrieve": ("src/gov/retrieval/retrieve.py", "ecfec265dfaf4d1fb3ee9e17d6990dc495a41a3e"),
    "register": ("src/gov/decisions/register.py", "9b61ada364cc1ca313ec9d979ae33104777ddf1c"),
}

REGISTER = "docs/DECISION_REGISTER.txt"
NOTE = "notes/orchard.md"
SUPERSEDED = "DEC-100"


def _clauses(name: str, count: int, marked: dict[int, str]) -> str:
    """``count`` filler clauses of the entry ``name``, each a line of about 90 characters; clause ``n`` of
    ``marked`` says ``marked[n]`` instead."""
    return "".join(f"- **Clause {n}:** {marked[n]}\n" if n in marked else
                   f"- **Clause {n}:** the {name} keeps the orchard's rows in order, tree by tree, row {n}.\n"
                   for n in range(1, count + 1))


def _gap(count: int) -> str:
    return "".join(f"The interlude's line {n} stands between the entries, in no entry.\n" for n in range(1, count + 1))


REGISTER_TEXT = (
    "Decision register\n"
    "\n"
    "The register's preface keeps the almanac of the orchard.\n"
    "\n"
    "### DEC-100 — The old orchard rule\n"
    "- **Status:** SUPERSEDED by DEC-101\n"
    "- **Decision:** The orchard keeps quince hedges at the gate.\n"
    "\n"
    "### DEC-101 — The new orchard rule\n"
    "- **Status:** ACCEPTED\n"
    "- **Decision:** The orchard keeps open gates.\n"
    + _clauses("new rule", 24, {15: "the new rule rings the persimmon bell at noon, row by row."})
    + "\n"
    "## Interlude\n"
    "\n"
    "Between the entries stands the tamarind clock.\n"
    + _gap(10)
    + "\n"
    "### DEC-476 — The orchard lights\n"
    "- **Status:** ACCEPTED\n"
    "- **Decision:** The orchard keeps lanterns at the gate.\n"
    + _clauses("lights rule", 24, {24: "the lights rule ends with the cardamom lamp."})
)

NOTE_TEXT = "# The orchard\n\nThe orchard's note keeps the orchard's gate.\n"

FILES = {
    ".gitignore": ".gov-runtime/\n",
    "governance/project/path-map.yaml": f"decision_register: {REGISTER}\n",
    REGISTER: REGISTER_TEXT,
    NOTE: NOTE_TEXT,
}

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


def _module(name: str):
    rel, blob = TODAY_BLOBS[name]
    source = subprocess.run(["git", "-C", str(REPO), "cat-file", "blob", blob], check=True,
                            capture_output=True).stdout.decode("utf-8")
    spec = importlib.util.spec_from_loader(f"w2_133_today_{name}", loader=None)
    module = importlib.util.module_from_spec(spec)
    exec(compile(source, f"{rel}@{TODAY_COMMIT}", "exec"), module.__dict__)  # noqa: S102 - our own blob
    return module


def today():
    """``(retrieve, register)``: the two modules as ``TODAY_COMMIT`` held them, beside the running tree's."""
    return _module("retrieve"), _module("register")


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


def holder(line: int) -> str | None:
    """The entry whose lines hold ``line``, or None (the preface, a gap)."""
    return next((rid for rid, (a, b) in entry_spans().items() if a <= line <= b), None)


def touched(first: int, last: int) -> list[str]:
    """The entries the lines ``first`` to ``last`` touch, in order."""
    return [rid for rid, (a, b) in entry_spans().items() if a <= last and first <= b]


def status_of(rid: str) -> str:
    """The status word of the entry ``rid``'s status line, read from the planted text."""
    first, _ = entry_spans()[rid]
    return re.search(r"\*\*Status:\*\*\s*([A-Z]+)", REGISTER_TEXT.split("\n")[first]).group(1)


def label(item: dict) -> str:
    """S1 and S2: the id a register item carries: the entry whose lines hold its first line, else its chunk id."""
    return holder(item["start_line"]) or item["chunk_id"]


def register_items(bundle: dict) -> list[dict]:
    return [item for item in bundle["evidence"] if item["path"] == REGISTER]


# The fields S1 and S2 name on a register item: its id and the entry's marks beside it (W2-92 S9)
LABEL_FIELDS = ("id", "entry", "status", "changed_by", "in_force", "not_in_force", "also")


def without_labels(bundle: dict) -> dict:
    """The bundle with each register item's id and status fields taken off: what S3 says the fix leaves unchanged."""
    return {**bundle, "evidence": [{key: value for key, value in item.items()
                                    if not (item["path"] == REGISTER and key in LABEL_FIELDS)}
                                   for item in bundle["evidence"]]}


def pages(ask, query: str, kwargs: dict, most: int = 10) -> list[dict]:
    """The bundles of ``query``, the first and each its continuation gives, to the end (at most ``most``)."""
    found = [ask(query, **kwargs)]
    while found[-1]["continuation"] and len(found) < most:
        found.append(ask(query, continuation=found[-1]["continuation"], **kwargs))
    return found
