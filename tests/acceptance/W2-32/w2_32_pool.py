"""S11's planted projects and helpers (W2-32; DEC-1071 (2), DEC-1074 (5)): the candidate pool, v456.

- **The settings** (S11's text): five query-time keys in ``governance/project/retrieval.yaml``, under a ``pool`` block:
  ``pool.meaning_uncut`` and ``pool.drop_nested`` (true or false), ``pool.route_depth``, ``pool.rerank_depth`` and
  ``pool.per_file_first10`` (whole numbers). Absent or 0 (false for the two flags): today's behaviour, the bundle item
  for item. An invalid value (a wrong type, a negative number): ``CONFIG_INVALID`` naming the key (``pool.<key>``).
  The measured form (the KPI's "60, 40, 2 and both true"): ``V456``.
- **The settings file is kept out of the index** (a namespace of its own, ``lexical_policy: not indexed``, not
  embedded) and written uncommitted, as ``w2_32_methods`` does, so a setting changes no indexed file.
- **No authority order** (W2-87's ``retrieval_authority`` is removed from the planted path map): the order judged is
  the routes', the fusion's and the reranker's alone.
- **Four planted stores**, each built so that one setting's effect shows (``plant_*``; the cases' module docstring says
  what each holds).
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

import w2_32_methods as m
import w2_32_routing as r
import w2_32_support as s

SETTINGS_REL = m.RETRIEVAL_REL
BLOCK = "pool"
FLAGS = ("meaning_uncut", "drop_nested")
COUNTS = ("route_depth", "rerank_depth", "per_file_first10")
KEYS = FLAGS + COUNTS
V456 = {"meaning_uncut": True, "route_depth": 60, "rerank_depth": 40, "per_file_first10": 2, "drop_nested": True}
OFF = {"meaning_uncut": False, "route_depth": 0, "rerank_depth": 0, "per_file_first10": 0, "drop_nested": False}
TODAY_DEPTH = 30  # the keyword and meaning routes' depth today (S11's text)
PAGE = 20  # today's page at radius 0 with the default batch: (1 round + 1) x 10 (DEC-422)
CAP_TEXTS, CAP_CHARS = 16, 24_000  # the padded request bound (DEC-1067 (f), the engineer's b7085897)


def key(name):
    return f"{BLOCK}.{name}"


def settle(project, pool=None, routing=None, raw=None):
    """Write the settings file: a ``pool`` block of ``pool`` (a dict, may be empty) and a ``routing`` block of
    ``routing``; ``raw`` writes that text; nothing at all (both None) removes the file."""
    if raw is not None:
        m.settle(project, SETTINGS_REL, raw)
        return
    document = {}
    if routing is not None:
        document["routing"] = routing
    if pool is not None:
        document[BLOCK] = pool
    m.settle(project, SETTINGS_REL, yaml.safe_dump(document, sort_keys=False) if document else None)


def _no_authority(project):
    document = yaml.safe_load((Path(project) / s.PATH_MAP_REL).read_text(encoding="utf-8"))
    document.pop("retrieval_authority", None)
    s.write(project, s.PATH_MAP_REL, yaml.safe_dump(document, sort_keys=False))
    s.commit(project, "no authority order")


# ---- the pool store: route_depth, rerank_depth and the padded bound ------------------------------------------------

POOL_QUESTION = "Which harbour ledgers record the quorum tide?"
# Forty long keyword notes (one line each, so one chunk each), not embedded: the keyword route's first 40, the
# question's words many times over; each about 2,400 characters, so the padded bound groups them (9 to a request).
KEYWORD_NOTES = {f"ledgers/keyword-{n:02d}.md": ("harbour ledgers record the quorum tide %02d; " % n * 60).strip()
                 + "\n" for n in range(40)}  # one line, no heading: one chunk, its own parent (nothing expands)
# Sixty short meaning notes, embedded: two of the question's words each, so the keyword route ranks them after the
# long notes and the meaning route ranks them first (the keyword notes have no vector).
MEANING_NOTES = {f"docs/meaning-{n:02d}.md": f"# Meaning note {n:02d}\n\nThe harbour tide almanac page {n:02d} for "
                                             f"the pilots.\n" for n in range(60)}


def plant_pool(project):
    project = m.plant(project, {**s.NOTES, **KEYWORD_NOTES, **MEANING_NOTES},
                      {"ledgers": s.namespace(["ledgers/**"], "not embedded")})
    _no_authority(project)
    return project


# ---- the phrased store: meaning_uncut ----------------------------------------------------------------------------

PHRASED_QUESTION = "What are the quayside lamp hours?"  # names CAP-88 by its title (w2_32_routing): three phrasings
ONLY_ID = "docs/rota.md"  # near the phrasing with CAP-88 appended, and only that one
ONLY_ID_TEXT = "CAP-88 CAP-88 CAP-88 CAP-88\n"
# Seventy notes near every phrasing alike and found by no keyword: each holds three words of the query embedder's
# instruction, which every phrasing is sent with, and none of the question's words. So every phrasing's meaning list
# (30 deep, or 60) is these notes, but for the phrasing with CAP-88 appended, whose first is ``ONLY_ID``; fused, these
# notes are in two lists or three and ``ONLY_ID`` in one, so the cut to the route's depth leaves it out.
CORE_NOTES = {f"docs/core-{n:02d}.md": f"web search passages: ferry bell anchor sail mast gull pier dock net {n:02d}\n"
              for n in range(70)}


def plant_phrased(project):
    files = {**s.NOTES, **CORE_NOTES, ONLY_ID: ONLY_ID_TEXT, r.RECORD_REL: r._record_text()}
    project = m.plant(project, files, {"records": s.namespace(["records/**"], "not embedded")})
    _no_authority(project)
    return project


# ---- the files store: per_file_first10 ---------------------------------------------------------------------------

FILES_QUESTION = "What does the harbour almanac say about the tide?"
ALMANAC, TIDE_BOOK = "docs/almanac.md", "docs/tide-book.md"


def _sections(title, ranks):
    """A note of short sections, one chunk each (each its own parent: nothing expands), ``rankNN`` in each."""
    return f"# {title}\n" + "".join(f"\n## Part {i}\n\nThe harbour almanac on the tide, part {i}: rank{rank:02d}.\n"
                                    for i, rank in enumerate(ranks, 1))


FILES_NOTES = {ALMANAC: _sections("Almanac", (95, 94, 93, 92, 91, 90)),
               TIDE_BOOK: _sections("Tide book", (85, 84, 83)),
               **{f"docs/harbour-{n:02d}.md": f"# Harbour note {n:02d}\n\nThe harbour almanac on the tide, note "
                                              f"rank{40 + n:02d}.\n" for n in range(1, 17)}}


def plant_files(project):
    project = m.plant(project, {**s.NOTES, **FILES_NOTES})
    _no_authority(project)
    return project


# ---- the nested store: drop_nested -------------------------------------------------------------------------------

NESTED_QUESTION = "What does the quay log say about the mooring ropes?"
QUAY_LOG, ROPE_LOG = "docs/quay-log.md", "docs/rope-log.md"


def _log(title, word):
    """A note whose one long section is chunked in three or more children (each up to 1,200 characters), all in one
    parent: the first child the rerank puts first is expanded to the section, the others then lie inside it. Two such
    notes hold the same lines (the same layout, other words)."""
    lines = [f"Entry {n:02d}: the quay log notes the mooring ropes of the {word} berth, checked at dawn and dusk.\n"
             for n in range(36)]
    return f"# {title}\n\n## Entries\n\n" + "".join(lines)


NESTED_NOTES = {QUAY_LOG: _log("Quay log", "north"), ROPE_LOG: _log("Rope log", "south"),
                **{f"docs/mooring-{n:02d}.md": f"# Mooring note {n:02d}\n\nThe quay log on mooring ropes, note "
                                               f"{n:02d}.\n" for n in range(10)}}


def plant_nested(project):
    project = m.plant(project, {**s.NOTES, **NESTED_NOTES})
    _no_authority(project)
    return project


# ---- asking and reading -------------------------------------------------------------------------------------------

def ask(box, project, question, **options):
    """``retrieve`` with the stand-in reranker ``kind`` (``calls``: a hash score, or ``ranks``: the ``rankNN``),
    keeping each request it receives. Returns the driver's data and the requests (each a list of texts)."""
    kind = options.pop("kind", "calls")
    log = Path(box.workdir) / f"rerank-{kind}.jsonl"
    if log.exists():
        log.unlink()
    data = box.call("retrieve", root=str(project), query=question, reranker=f"{kind}:{log}", **options)
    requests = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []
    return data, requests


def items(bundle):
    """The bundle's evidence, item for item, as the cases compare it."""
    return [(item["path"], item["start_line"], item["end_line"], item["sha256"]) for item in bundle["evidence"]]


def text_of(item):
    """The text the reranker is given for an evidence item (its path line and its text; ``retrieve``'s form)."""
    return f"[path: {item['path']}]\n{item['text']}"


def path_of(text):
    first = text.split("\n", 1)[0]
    return first[len("[path: "):-1] if first.startswith("[path: ") and first.endswith("]") else None


def nested(evidence):
    """The positions of the items whose lines lie inside an earlier item's of the same file."""
    out = []
    for at, item in enumerate(evidence):
        if any(other["path"] == item["path"] and other["start_line"] <= item["start_line"]
               and item["end_line"] <= other["end_line"] for other in evidence[:at]):
            out.append(at)
    return out


def capped(order, n, head=10):
    """``order`` (a list of evidence items) with at most ``n`` of one file in its first ``head``: the first ``head``
    taken in order, an item skipped while its file holds ``n`` of them, the rest after them in their order."""
    first, count = [], {}
    for at, item in enumerate(order):
        if len(first) == head:
            break
        if count.get(item["path"], 0) < n:
            count[item["path"]] = count.get(item["path"], 0) + 1
            first.append(at)
    return [order[at] for at in first] + [item for at, item in enumerate(order) if at not in set(first)]


def within_bound(requests):
    """Fails unless every request keeps the padded bound: at most 16 texts, its texts times its longest at most
    24,000 characters (S11's second failure line)."""
    for number, request in enumerate(requests, 1):
        padded = len(request) * max((len(text) for text in request), default=0)
        assert len(request) <= CAP_TEXTS, f"rerank request {number} carries {len(request)} texts (at most 16)"
        assert padded <= CAP_CHARS, f"rerank request {number}'s padded size is {padded} characters " \
                                    f"({len(request)} texts): above {CAP_CHARS} (the padded bound)"


def fewest(pool):
    """How many requests the pool takes under the padded bound, grouped longest first (``test_w2_32_s7_size_bound``)."""
    count, texts, longest = 0, 0, 0
    for size in sorted((len(text) for text in pool), reverse=True):
        if texts and (texts + 1 > CAP_TEXTS or (texts + 1) * longest > CAP_CHARS):
            count, texts, longest = count + 1, 0, 0
        texts, longest = texts + 1, max(longest, size)
    return count + (1 if texts else 0)


def raised_text(data):
    raised = data.get("raised") or {}
    return f"{raised.get('type')}: {raised.get('code')} {raised.get('message')}"
