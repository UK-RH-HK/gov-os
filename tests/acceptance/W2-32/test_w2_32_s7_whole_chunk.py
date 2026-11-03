"""S7 (G1, round 1; DEC-1066): the models read the whole chunk.

The line: the embedder and the reranker read each chunk in full (no 512/500-character cut below the chunk's size; the
manifest's cut changes, so a full re-embed by S1), and parent expansion keeps its expanded parents across
continuations (no span sent twice).

- **The whole chunk:** a planted note is one chunk (under the chunker's 1,200 characters) whose only words of the
  question lie past character 600: the text the stand-in embedder was sent for it, and the text the recording
  reranker was given for it, both hold those words; the semantic route finds the note nearer the question than when
  it is embedded from its first 512 characters (the distance worked out from the question text the stand-in was sent).
- **The cut:** the manifest records its cut (any key besides the two models, W2-L065) and it is neither 512 nor 500.
  A store that records the old cut of 512, with the note's vector made from its first 512 characters, is stale (no
  answer from it) and the next rebuild embeds the note whole.
- **Across continuations:** a section of about 3,500 characters (several chunks, one parent) asked with one item a
  batch: following the continuations, no evidence item repeats a sha256 sent in an earlier bundle, and none lies
  within a span an earlier bundle sent.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import w2_32_support as s

LONG = "docs/ferry-office.md"
FILLER = "The clerk stamps forms, files receipts, counts coins and sorts the post into numbered pigeonholes.\n"
LONG_TEXT = "# Ferry office\n\n" + FILLER * 7 + "The quokka ferry sails to the basalt islet at noon each day.\n"
LONG_QUESTION = "Which quokka ferry sails to the basalt islet at noon?"
LONG_WORDS = ("quokka", "basalt", "islet")
ALMANAC = "docs/almanac.md"
PIERS = ("north", "south", "east", "west", "cedar", "maple", "birch", "alder", "rowan", "hazel")
ALMANAC_TEXT = "# Almanac\n\n" + "".join(
    f"Almanac entry {i:02d}: the tide almanac lists the {PIERS[i % 10]} tide at the {PIERS[(i // 10) % 10]} pier.\n"
    for i in range(50))
ALMANAC_QUESTION = "What does the tide almanac list for the pier tides?"
OLD_CUT = 512


@pytest.fixture
def long_project(tmp_path, needs_vectors):
    assert LONG_TEXT.index("quokka") > 600 and len(LONG_TEXT) < 1200, "premise: one chunk, its words past 600"
    assert not any(word in LONG_TEXT[:OLD_CUT] for word in LONG_WORDS)
    assert len(ALMANAC_TEXT) > 3000, "premise: the almanac section is several chunks"
    return s.plant(tmp_path / "project", {**s.NOTES, LONG: LONG_TEXT, ALMANAC: ALMANAC_TEXT})


def _vector_texts(project, standin, path):
    """The texts the stand-in made the stored vectors of ``path`` from."""
    return [standin.text_of.get(vector) for rel, vector in s.vectors(project).values() if rel == path]


# ---- the embedder reads the whole chunk ----

def test_the_embedder_reads_the_whole_chunk_and_the_semantic_route_finds_words_past_the_old_cut(
        long_project, box, standin):
    box.built(long_project)
    texts = _vector_texts(long_project, standin, LONG)
    assert texts and all(text and all(word in text for word in LONG_WORDS) for text in texts), \
        f"the embedder was not sent the whole chunk of {LONG}: {[text and text[-80:] for text in texts]}"
    # Rewrite-Reason: S7's first-hit premise (the stand-in's bag of words, not the cut). The stand-in's vectors are
    # bags of words, so the note's seven filler lines outweigh its last line and a short note sharing the question's
    # common words can rank first at any cut. What S7 changes is that the words past the old cut reach the vector:
    # the note's distance to the question is smaller than the distance it has when embedded from its first 512
    # characters, worked out here from the very question text the stand-in was sent.
    standin.clear()
    answer = s.result(box.call("semantic_search", root=str(long_project), query=LONG_QUESTION))
    assert answer["available"] is True, answer
    asked = [text for text in standin.texts_embedded(s.PIN_MODEL) if text.endswith(LONG_QUESTION)]
    assert asked, "premise: the question was sent to the stand-in embedder"
    question = s.stand_in_vector(s.PIN_MODEL, asked[-1])
    cut = s.stand_in_vector(s.PIN_MODEL, LONG_TEXT[:OLD_CUT])
    cut_distance = 1.0 - sum(a * b for a, b in zip(question, cut))
    found = [hit["distance"] for hit in answer["hits"] if hit["path"] == LONG]
    assert found, f"the note is not among the semantic route's hits: {s.first_paths(answer['hits'], 30)}"
    assert min(found) < cut_distance - 1e-3, \
        f"the note is no nearer the question than when embedded from its first {OLD_CUT} characters " \
        f"({min(found):.4f}, cut at {OLD_CUT}: {cut_distance:.4f}): its words past the cut did not reach the route"


# ---- the reranker reads the whole chunk ----

def _reranked_texts(box):
    path = Path(box.workdir) / "reranked.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []


@pytest.mark.parametrize("op", ["retrieve", "fusion_search"])
def test_the_reranker_reads_the_whole_chunk(long_project, box, standin, op):
    box.built(long_project)
    spec = f"record:{Path(box.workdir) / 'reranked.jsonl'}:quokka"
    extra = {"limit": 5} if op == "fusion_search" else {}
    answer = s.result(box.call(op, root=str(long_project), query=LONG_QUESTION, reranker=spec, **extra))
    given = [text for text in _reranked_texts(box) if "pigeonholes" in text]  # the ferry office's chunk
    assert given, f"the reranker was never given the ferry office's chunk ({op})"
    assert all(all(word in text for word in LONG_WORDS) for text in given), \
        f"the reranker was given the chunk cut short ({op}): it ends {given[0][-80:]!r}"
    hits = answer["evidence"] if op == "retrieve" else answer["hits"]
    assert s.first_paths(hits)[:1] == [LONG], f"the reranker's choice is first ({op}): {s.first_paths(hits)}"


# ---- the cut in the manifest ----

def test_the_manifest_records_a_cut_that_is_not_the_old_one(long_project, box, standin):
    box.built(long_project)
    cut = s.cut_entries(s.result(box.call("manifest", root=str(long_project))))
    assert cut, "the manifest records no embedding cut (W2-L065)"
    assert not any(s.holds_value(value, old) for value in cut.values() for old in (OLD_CUT, 500)), \
        f"the manifest still records a cut of 512 or 500 characters: {cut}"


def test_a_store_embedded_at_the_old_cut_is_stale_and_the_next_rebuild_embeds_the_chunk_whole(
        long_project, box, standin):
    box.built(long_project)
    manifest = s.result(box.call("manifest", root=str(long_project)))
    assert s.set_store_cut(long_project, manifest, OLD_CUT) > 0, \
        f"premise: the store holds the cut the manifest names, to be set back to {OLD_CUT}: {s.cut_entries(manifest)}"
    old = s.blob(s.stand_in_vector(s.PIN_MODEL, LONG_TEXT[:OLD_CUT]))
    assert s.set_vectors_of(long_project, LONG, old), "premise: the note has a vector"

    stale = s.result(box.call("semantic_search", root=str(long_project), query=LONG_QUESTION))
    assert stale["available"] is False and stale["hits"] == [], \
        f"a store embedded at the old cut of {OLD_CUT} characters was answered from: {stale}"

    box.built(long_project)
    texts = _vector_texts(long_project, standin, LONG)
    assert texts and all(text and "quokka" in text for text in texts), "the rebuild did not embed the chunk whole"
    renewed = s.cut_entries(s.result(box.call("manifest", root=str(long_project))))
    assert not any(s.holds_value(value, OLD_CUT) for value in renewed.values()), renewed


# ---- parent expansion across continuations ----

def test_across_continuations_no_span_is_sent_twice(long_project, box, standin):
    box.built(long_project)
    bundles, token = [], None
    for _ in range(12):
        call = {"root": str(long_project), "query": ALMANAC_QUESTION, "batch_size": 1, "radius": 0}
        if token:
            call["continuation"] = token
        bundle = s.result(box.call("retrieve", **call))
        bundles.append(bundle["evidence"])
        token = bundle.get("continuation")
        if not token:
            break
    assert len(bundles) >= 2, "premise: the question takes more than one bundle"
    assert sum(item["path"] == ALMANAC for items in bundles[1:] for item in items), \
        "premise: a later bundle holds another chunk of the almanac's section"
    sent_hashes, sent_spans = set(), []
    for number, items in enumerate(bundles, 1):
        for item in items:
            assert item["sha256"] not in sent_hashes, \
                f"bundle {number} sends again {item['path']}:{item['start_line']}-{item['end_line']}, sent earlier"
            inside = [span for span in sent_spans if span[0] == item["path"] and span[1] <= item["start_line"]
                      and item["end_line"] <= span[2]]
            assert not inside, f"bundle {number} sends {item['path']}:{item['start_line']}-{item['end_line']}, " \
                               f"within {inside[0][1]}-{inside[0][2]} sent earlier"
        sent_hashes |= {item["sha256"] for item in items}
        sent_spans += [(item["path"], item["start_line"], item["end_line"]) for item in items]
