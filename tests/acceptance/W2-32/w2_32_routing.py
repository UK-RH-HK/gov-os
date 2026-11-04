"""S8's planted project and helpers (W2-32; DEC-1067 (a): routing by question type).

- **The settings** (the CTO's ruling: each half behind its own setting, both off by default; off gives today's order
  exactly; an invalid value is ``CONFIG_INVALID`` naming the key). As the engineer stated them: in
  ``governance/project/retrieval.yaml`` a ``routing`` block with ``code_first`` (the symbol half: how many of the code
  route's first hits go ahead) and ``named_first`` (the record half: how many of the named record's best chunks go
  ahead); absent or 0 is off, the measured form is 2; invalid values are ``CONFIG_INVALID`` naming the key
  (``routing.code_first``). With either half on, the bundle carries a ``routing`` record of what it moved.
  Rewrite-Reason: the engineer's stated setting names (they were ``route_by_symbol`` and ``route_by_record``,
  true or false).
- **The corpus:** three code files, one function each (``CODE``: the code route's hits, in its order); a record
  (``CAP-88``) of three sections, one chunk each; notes enough for a rerank pool above 16. Every chunk that a case
  orders holds a token ``rankNN``: the stand-in reranker's score is that number (no token: 0), so the reranker's
  order is set by the corpus, and the routed chunks score below the notes (routing is what puts them ahead).
- **The code route** is a stand-in (the driver's ``code_route`` option): the real code-graph tool needs a local
  coordination endpoint the launch sandbox refuses. It answers a question naming ``SYMBOL`` with the chunks of
  ``CODE`` in that order, and a question naming none with nothing (no route), as the real route does.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

import w2_32_support as s

SETTINGS_REL = "governance/project/retrieval.yaml"
BLOCK = "routing"
KEYS = {"symbol": "routing.code_first", "record": "routing.named_first"}  # as the loader names them
ON, OFF = 2, 0  # the measured form; 0 (or absent) is off

SYMBOL = "w32_alpha"
CODE = ["app/alpha.py", "app/beta.py", "app/gamma.py"]  # the code route's hits, first to last
# One function a file and nothing else, so each file is one chunk (no module lines to chunk or expand apart).
CODE_TEXT = {
    "app/alpha.py": f"def {SYMBOL}(tide):\n    \"\"\"The harbour signal of a tide: rank03.\"\"\"\n    return tide + 1\n",
    "app/beta.py": f"def w32_beta(tide):\n    \"\"\"Twice the harbour signal: rank02.\"\"\"\n    return {SYMBOL}(tide) * 2\n",
    "app/gamma.py": f"def w32_gamma(tide):\n    \"\"\"The harbour signal less three: rank04.\"\"\"\n    return {SYMBOL}(tide) - 3\n",
}
RECORD, RECORD_REL = "CAP-88", "records/capabilities/cap-88.md"
RECORD_RANKS = (7, 9, 8)  # its three sections; its two best are 9 and 8
FILLERS = {f"docs/harbour-{n:02d}.md": f"# Harbour note {n}\n\nThe harbour almanac signals note rank{40 + n}: tide "
                                        f"and quay.\n" for n in range(1, 17)}

SYMBOL_QUESTION = f"Who calls `{SYMBOL}` for the harbour signals?"
RECORD_QUESTION = f"What does {RECORD} say about the harbour signals?"
BOTH_QUESTION = f"Who calls `{SYMBOL}`, and what does {RECORD} say about the harbour signals?"
PLAIN_QUESTION = "What does the harbour almanac say about the tide and quay?"


def _record_text():
    front = {"id": RECORD, "type": "capability", "status": "ACTIVE", "state_class": "AUTHORITATIVE",
             "title": "Quayside lamp hours"}
    sections = "".join(f"\n## Part {i}\n\nThe lamps are lit at the quay in part {i}: rank{rank:02d}.\n"
                       for i, rank in enumerate(RECORD_RANKS, 1))
    return "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n# Quayside lamp hours\n" + sections


def plant(project):
    files = {**s.NOTES, **FILLERS, **CODE_TEXT, "app/__init__.py": "", RECORD_REL: _record_text()}
    project = s.plant(project, files)
    document = yaml.safe_load((Path(project) / s.PATH_MAP_REL).read_text(encoding="utf-8"))
    document.pop("retrieval_authority", None)  # W2-87's authority order is not under test here
    document["namespaces"]["code"] = s.namespace(["app/**"], "embedded")
    document["namespaces"]["records"] = s.namespace(["records/**"], "embedded")
    document["namespaces"]["project"]["paths"] = [p for p in document["namespaces"]["project"]["paths"]
                                                  if p != "records/**"]
    s.write(project, s.PATH_MAP_REL, yaml.safe_dump(document, sort_keys=False))
    s.commit(project, "the code and the record in namespaces of their own")
    return project


def set_routing(project, symbol=None, record=None, raw=None):
    """Write the routing settings: each half a count (``ON``, ``OFF``, or any value to plant) or left out (``None``);
    ``raw`` writes that text as the file."""
    if raw is not None:
        s.write(project, SETTINGS_REL, raw)
        return
    block = {KEYS[half].split(".", 1)[1]: value for half, value in (("symbol", symbol), ("record", record))
             if value is not None}
    s.write(project, SETTINGS_REL, yaml.safe_dump({BLOCK: block}, sort_keys=False))


def unset_routing(project):
    path = Path(project) / SETTINGS_REL
    if path.exists():
        path.unlink()


RANK = re.compile(r"\brank(\d{2})\b")


def rank_of(text):
    """The stand-in reranker's score of a text: its ``rankNN``, else 0."""
    found = [int(number) for number in RANK.findall(text or "")]
    return max(found) if found else 0


def key_of(path, text):
    """A chunk as the cases name it: its path and its rank (a record's sections differ by rank only)."""
    return path, rank_of(text)


CODE_ROUTE = {"symbol": SYMBOL, "paths": CODE}
