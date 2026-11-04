"""S7 (G1) with its note under DEC-1067 (owner, 2026-11-04): the reranker's requests capped at 16 texts (f), parent
expansion sending no span twice in either direction, and the embedder's limit named.

- **The cap (DEC-1067 (f)):** a search whose rerank pool exceeds 16 sends the reranker no request of more than 16
  texts, and the final order is the order the same scores give unbatched. The stand-in reranker keeps each request
  (one per call) and scores each text by a hash of it, so no two texts tie.
- **No span twice, the converse (S7; the review's F-5):** a paged retrieval whose first call sends two chunks of a
  section alone (their parent does not fit the bundle budget there) and whose later call expands that section: the
  later call sends no span that contains a span an earlier call sent, and names what it left out. (The direction
  "a span inside a parent expanded earlier is left out and named" is ``test_w2_32_s7_whole_chunk.py``'s.)
- **The embedder's limit, named (S7; the CTO's measure of the shared embedder: it cuts an input above its 4,096-token
  context, about 15,000 characters, silently):** a planted chunk of 40,000 characters (one line) is embedded from its
  first part, at most ``LIMIT_CHARS`` characters, and the rebuild's report names it (its path); never silently.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import w2_32_driver as driver
import w2_32_support as s

CAP = 16
LIMIT_CHARS = 16_384  # 4,096 tokens at four characters each: no limit of the embedder's context lies above it


# ---- the cap: at most 16 texts a request, the order unchanged ----------------------------------------------------

WORDS = ("amber", "basalt", "cobalt", "dune", "ember", "fjord", "garnet", "heron", "indigo", "juniper")
QUESTION = "Which notes mention the quorum of the harbour council?"


def _council():
    return {f"docs/council-{i:02d}.md": (f"# Council note {i}\n\nThe harbour council reached its quorum on the "
                                         f"{WORDS[i % 10]} {WORDS[i // 10]} question, item {i}.\n") for i in range(50)}


@pytest.fixture
def council(tmp_path, needs_vectors, box):
    project = s.plant(tmp_path / "council", {**_council(), "README.md": "# Council notes\n"})
    box.built(project)
    return project


def _requests(box):
    path = Path(box.workdir) / "rerank-calls.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []


def _path_of(text):
    """The path the reranker's text names (``[path: …]`` on its first line)."""
    first = text.split("\n", 1)[0]
    return first[len("[path: "):-1] if first.startswith("[path: ") and first.endswith("]") else None


@pytest.mark.parametrize("op", ["fusion_search", "retrieve"])
def test_no_reranker_request_carries_more_than_16_texts_and_the_order_is_the_unbatched_one(council, box, standin, op):
    spec = f"calls:{Path(box.workdir) / 'rerank-calls.jsonl'}"
    extra = {"limit": 30} if op == "fusion_search" else {"radius": 0}
    answer = s.result(box.call(op, root=str(council), query=QUESTION, reranker=spec, **extra))
    requests = _requests(box)
    pool = [text for request in requests for text in request]
    assert len(pool) > CAP, f"premise: the rerank pool holds more than {CAP} texts ({len(pool)})"
    sizes = [len(request) for request in requests]
    assert max(sizes) <= CAP, f"a reranker request carried more than {CAP} texts (DEC-1067 (f)): {sizes}"
    unbatched = [_path_of(text) for text in sorted(pool, key=driver.hashed_score, reverse=True)]
    assert None not in unbatched, "premise: every text the reranker read names its path"
    hits = answer["hits"] if op == "fusion_search" else answer["evidence"]
    order = s.first_paths(hits, len(hits))
    assert order == unbatched[:len(order)], \
        f"the order is not the one the same scores give unbatched ({op}):\n{order[:8]}\n{unbatched[:8]}"


# ---- no span twice: a child sent alone earlier, its parent expanded later ------------------------------------------

PIERS = ("north", "south", "east", "west", "cedar", "maple", "birch", "alder", "rowan", "hazel")
ALMANAC = "docs/almanac.md"
ALMANAC_TEXT = "# Almanac\n\n" + "".join(
    f"Almanac entry {i:02d}: the tide almanac lists the {PIERS[i % 10]} tide at the {PIERS[(i // 10) % 10]} pier.\n"
    for i in range(44))
ALMANAC_QUESTION = "What does the tide almanac list for the pier tides?"
BUDGET = 1000  # the first call's two chunks leave no room for their section; the second call's one does


def _named(value, skip=("evidence", "expansions")):
    """Every span record the bundle names outside its evidence and expansions, but for a not-gathered gap."""
    if isinstance(value, dict):
        found = [value] if {"path", "start_line", "end_line"} <= set(value) and value.get("reason") != "NOT_GATHERED" \
            else []
        return found + [record for key, item in value.items() if key not in skip for record in _named(item, ())]
    if isinstance(value, list):
        return [record for item in value for record in _named(item, ())]
    return []


@pytest.fixture
def almanac(tmp_path, needs_vectors, box):
    project = s.plant(tmp_path / "almanac", {**s.NOTES, ALMANAC: ALMANAC_TEXT})
    box.built(project)
    return project


def test_a_parent_expanded_later_leaves_out_the_children_sent_alone_earlier_and_names_them(almanac, box, standin):
    bundles, token = [], None
    for _ in range(12):
        call = {"root": str(almanac), "query": ALMANAC_QUESTION, "batch_size": 1, "radius": 0,
                "bundle_budget": BUDGET}
        if token:
            call["continuation"] = token
        bundle = s.result(box.call("retrieve", **call))
        bundles.append(bundle)
        token = bundle.get("continuation")
        if not token:
            break
    first = [(item["start_line"], item["end_line"]) for item in bundles[0]["evidence"] if item["path"] == ALMANAC]
    assert first and not [e for e in bundles[0]["expansions"] if e["path"] == ALMANAC], \
        f"premise: the first call sends chunks of the section alone, unexpanded: {bundles[0]['evidence']}"
    later_items = [(number, item) for number, bundle in enumerate(bundles[1:], 2) for item in bundle["evidence"]
                   if item["path"] == ALMANAC]
    named = [record for bundle in bundles[1:] for record in _named(bundle) if record["path"] == ALMANAC
             and any(start <= record["start_line"] and record["end_line"] <= end for start, end in first)]
    expanded = [e for bundle in bundles[1:] for e in bundle["expansions"] if e["path"] == ALMANAC]
    assert later_items or named or expanded, \
        "premise: a later call reaches the section again (sends, expands or names a part of it)"
    for number, item in later_items:
        held = [(start, end) for start, end in first if item["start_line"] <= start and end <= item["end_line"]]
        assert not held, f"call {number} sends {ALMANAC}:{item['start_line']}-{item['end_line']}, which holds " \
                         f"{held[0][0]}-{held[0][1]} sent alone in call 1: those lines are sent twice"
    if expanded:
        assert named, f"a later call expanded the section ({expanded}) and names none of the spans it left out"


# ---- the embedder's limit, named ----------------------------------------------------------------------------------

LONG = "docs/ledger-table.md"
LONG_LINE = "".join(f"| ledger cell {i:05d} quill |" for i in range(1700)) + "\n"


@pytest.fixture
def long_chunk(tmp_path, needs_vectors):
    assert len(LONG_LINE) > 40_000, "premise: one line of more than 40,000 characters, so one chunk"
    return s.plant(tmp_path / "long", {**s.NOTES, LONG: "# Ledger table\n\n" + LONG_LINE})


def test_a_chunk_above_the_embedders_limit_is_embedded_from_its_first_part_and_named(long_chunk, box, standin):
    envelope = box.rebuild(long_chunk)
    store = s.semantic_store(envelope)
    assert envelope.get("ok") is True and store.get("status") == "recreated", \
        f"a chunk above the limit fails the rebuild instead of being embedded from its first part: {store}"
    sent = standin.texts_embedded(s.PIN_MODEL)
    longest = max(len(text) for text in sent)
    assert longest <= LIMIT_CHARS, f"the embedder was sent {longest} characters, above any 4,096-token context"
    parts = [text for text in sent if "ledger cell" in text]
    assert parts and all(LONG_LINE.startswith(text.rstrip("\n")) or text.rstrip("\n") in LONG_LINE[:LIMIT_CHARS]
                         for text in parts), "the long chunk was not embedded from its first part"
    assert LONG in s.vector_paths(long_chunk), "the long chunk has no vector"
    report = json.dumps(envelope.get("result") or {})
    assert LONG in report, f"the rebuild's report does not name the chunk embedded from its first part: {store}"
    assert "docs/harbour.md" not in report, "premise: the report names the cut chunk, not every file"


# ---- no span twice with nested parents: a Python module and its functions (the round-2 review, R2-F1) -------------

# A module whose parent (the whole file) holds its function parents. Each function and each run of module lines is
# one chunk of its own (under the chunker's 1,200 characters), so no two chunks overlap: a line sent twice is sent
# twice by expansion. Every line of it answers the question.
TIDE_PIERS = ("north", "south", "east", "west", "cedar")
CODE = "docs/tides.py"


def _function(pier):
    body = "".join(f"    # the tide almanac lists the {pier} pier tide at hour {hour:02d}\n" for hour in range(6))
    return f"def {pier}_pier_tides():\n    \"\"\"The tide almanac for the {pier} pier.\"\"\"\n{body}    return \"{pier}\"\n"


CODE_TEXT = ('"""The tide almanac: each pier\'s tides, as the almanac lists them."""\n\n'
             'ALMANAC_PIERS = ("north", "south", "east", "west", "cedar")  # the tide almanac\'s piers\n'
             'TIDE_UNIT = "metres"  # the almanac lists each pier tide in metres\n\n\n'
             + "\n\n".join(_function(pier) for pier in TIDE_PIERS))
CODE_QUESTION = "What does the tide almanac list for each pier tide?"


@pytest.fixture
def module(tmp_path, needs_vectors, box):
    project = s.plant(tmp_path / "module", {**s.NOTES, CODE: CODE_TEXT})
    box.built(project)
    return project


def test_nested_parents_send_no_line_twice_and_name_every_span_left_out(module, box, standin):
    """The round-2 review's R2-F1 (DEC-1067; the owner's order: parent expansion sends no span twice, and every span
    left out is named as a span record). A paged retrieval (one item a batch, followed through its continuations):
    across all calls, and within one call, no line of the module is sent twice in the evidence; in each call every
    gathered chunk is either sent or named as a span record outside the evidence and the expansions; and a named
    span lies within lines already sent."""
    bundles, token = [], None
    for _ in range(14):
        call = {"root": str(module), "query": CODE_QUESTION, "batch_size": 1, "radius": 0}
        if token:
            call["continuation"] = token
        bundle = s.result(box.call("retrieve", **call))
        bundles.append(bundle)
        token = bundle.get("continuation")
        if not token:
            break
    reached = sum(1 for bundle in bundles for item in bundle["evidence"] + _named(bundle) if item["path"] == CODE)
    assert reached >= 3, f"premise: the retrieval reaches the module's functions more than once ({reached})"
    assert any(e["path"] == CODE for bundle in bundles for e in bundle["expansions"]) or any(
        item["path"] == CODE and item["end_line"] - item["start_line"] > 12 for bundle in bundles
        for item in bundle["evidence"]), "premise: a parent of the module (the module or a function) is expanded"
    sent: dict[str, set[int]] = {}
    for number, bundle in enumerate(bundles, 1):
        named = _named(bundle)
        for record in named:
            lines = set(range(record["start_line"], record["end_line"] + 1))
            assert lines <= sent.get(record["path"], set()) | {
                line for item in bundle["evidence"] if item["path"] == record["path"]
                for line in range(item["start_line"], item["end_line"] + 1)}, \
                f"call {number} names {record['path']}:{record['start_line']}-{record['end_line']} as left out, " \
                "but those lines were never sent"
        for item in bundle["evidence"]:
            lines = set(range(item["start_line"], item["end_line"] + 1))
            twice = sorted(lines & sent.get(item["path"], set()))
            assert not twice, f"call {number} sends {item['path']}:{item['start_line']}-{item['end_line']}: lines " \
                              f"{twice[0]}-{twice[-1]} were already sent (unnamed, sent twice)"
            sent.setdefault(item["path"], set()).update(lines)
        gathered = bundle["merge"]["candidates"]
        assert gathered == len(bundle["evidence"]) + len(named), \
            f"call {number} gathered {gathered} chunks, sent {len(bundle['evidence'])} and named {len(named)} as " \
            "left out: a chunk left out is not named"
