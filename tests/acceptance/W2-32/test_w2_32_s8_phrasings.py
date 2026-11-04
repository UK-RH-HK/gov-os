"""S8's note under DEC-1067 order (4), measure 3: three deterministic phrasings of each question.

The note: with ``routing.phrasings: true`` in ``governance/project/retrieval.yaml``, each question is searched in three
deterministic phrasings (the question itself; its content words without stopwords or the question mark; the question
with the record ids the record route resolves appended), fused, and reranked once over the merged pool; absent or
false is today's order byte for byte; an invalid value is ``CONFIG_INVALID`` naming ``routing.phrasings``.

- **The content-word phrasing:** ``LEDGER`` holds the question's content words in a row once, in a long chunk kept
  out of the vectors; forty short notes hold the same words more often (never in that row), so the lexical route's
  30 words-ranked chunks of the question as asked leave ``LEDGER`` out, and the semantic route never has it. Only the
  content words searched as their own phrasing (the lexical route's phrase boost) bring it: with the setting on it
  is in the rerank pool; off it is not.
- **The id-appended phrasing:** a question names the record ``CAP-88`` by its title; the record route resolves it,
  and the phrasing with ``CAP-88`` appended reaches ``CITING``, a note that names ``CAP-88`` and shares no word with
  the question (kept out of the vectors): in the pool with the setting on, not off.
- **Reranked once:** with the setting on, the merged pool goes to the reranker once (each text once) in requests
  within 16 texts and 24,000 characters, the fewest that meet both in the order sent.
- **Off:** no setting, and ``phrasings: false``, give the same bundle, byte for byte.
- **Invalid:** a word, a number, a list: ``CONFIG_INVALID`` naming ``routing.phrasings``.

The retrieval is ``retrieve`` at radius 4 with the default batch, so the whole fused list is gathered and the pool
is every fused chunk; the stand-in reranker keeps each request and scores by a hash (``w2_32_driver``).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

import w2_32_routing as r
import w2_32_support as s
from test_w2_32_s7_size_bound import CAP_CHARS, CAP_TEXTS, _fewest

KEY = "routing.phrasings"
CONTENT_QUESTION = "Where is the tide ledger quorum kept?"
CONTENT_WORDS = "tide ledger quorum kept"  # the question less its stopwords and its question mark
LEDGER = "records/ledger-room.md"
LEDGER_TEXT = ("# Ledger room\n\n" + "The archive shelves hold bound volumes of harbour accounts and charts. " * 12
               + f"The {CONTENT_WORDS} in the north archive.\n")
DISTRACTORS = {f"docs/quorum-{n:02d}.md": f"# Quorum note {n}\n\nQuorum and ledger, kept by the tide: the quorum "
                                          f"ledger tide note {n} keeps the tide.\n" for n in range(40)}
RECORD_TITLE_QUESTION = "What are the quayside lamp hours?"  # names CAP-88 by its title (w2_32_routing)
CITING = "records/board-minutes.md"
CITING_TEXT = "# Board minutes\n\nThe harbour board cites CAP-88 for its evening rota.\n"


@pytest.fixture
def phrased(tmp_path, needs_vectors, box):
    project = r.plant(tmp_path / "phrased")
    for rel, text in {LEDGER: LEDGER_TEXT, CITING: CITING_TEXT, **DISTRACTORS}.items():
        s.write(project, rel, text)
    document = yaml.safe_load((Path(project) / s.PATH_MAP_REL).read_text(encoding="utf-8"))
    document["namespaces"]["plain"] = s.namespace([LEDGER, CITING], "not embedded")
    document["namespaces"]["records"]["paths"] = ["records/capabilities/**"]
    s.write(project, s.PATH_MAP_REL, yaml.safe_dump(document, sort_keys=False))
    s.commit(project, "the ledger room, the board minutes and the quorum notes")
    box.built(project)
    return project


def _set(project, value=None, raw=None):
    s.write(project, r.SETTINGS_REL, raw if raw is not None else yaml.safe_dump({r.BLOCK: {"phrasings": value}}))


def _ask(box, project, question):
    log = Path(box.workdir) / "rerank-calls.jsonl"
    if log.exists():
        log.unlink()
    data = box.call("retrieve", root=str(project), query=question, radius=4, reranker=f"calls:{log}",
                    code_route=r.CODE_ROUTE)
    requests = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []
    return data, requests


def _pool_paths(requests):
    return {text.split("\n", 1)[0][len("[path: "):-1] for request in requests for text in request}


def _premise_unreached(project, question, rel):
    """Off, the target is in no route's list: not in the vectors, and not in the lexical route's list for the
    question as asked."""
    assert rel not in s.vector_paths(project), f"premise: {rel} has no vector"


@pytest.mark.parametrize("setting", ["on", "off"])
def test_the_content_word_phrasing_brings_a_chunk_only_it_reaches(phrased, box, standin, setting):
    _premise_unreached(phrased, CONTENT_QUESTION, LEDGER)
    if setting == "on":
        _set(phrased, True)
    data, requests = _ask(box, phrased, CONTENT_QUESTION)
    bundle = s.result(data)
    pool = _pool_paths(requests)
    assert len(pool) > 20, f"premise: the pool is the fused list ({len(pool)} paths)"
    if setting == "off":
        assert LEDGER not in pool, f"premise: the question as asked never reaches {LEDGER} (it is in the pool off)"
    else:
        assert LEDGER in pool, f"with routing.phrasings on, the content-word phrasing ({CONTENT_WORDS!r}) did not " \
                               f"bring {LEDGER} into the rerank pool"
        assert LEDGER in {item["path"] for item in bundle["evidence"]}, f"{LEDGER} is not in the bundle"


@pytest.mark.parametrize("setting", ["on", "off"])
def test_the_id_appended_phrasing_reaches_a_chunk_naming_the_resolved_record(phrased, box, standin, setting):
    _premise_unreached(phrased, RECORD_TITLE_QUESTION, CITING)
    if setting == "on":
        _set(phrased, True)
    data, requests = _ask(box, phrased, RECORD_TITLE_QUESTION)
    bundle = s.result(data)
    assert bundle["facets"].get("closure", {}).get("available") is True, \
        f"premise: the record route resolves {r.RECORD} from its title: {bundle['facets']}"
    pool = _pool_paths(requests)
    assert r.RECORD_REL in pool, f"premise: the resolved record's own chunks are in the pool: {sorted(pool)[:8]}"
    if setting == "off":
        assert CITING not in pool, f"premise: the question as asked never reaches {CITING}"
    else:
        assert CITING in pool, f"with routing.phrasings on, the phrasing with {r.RECORD} appended did not bring " \
                               f"{CITING} (which names {r.RECORD}) into the rerank pool"


@pytest.mark.parametrize("question", [CONTENT_QUESTION, RECORD_TITLE_QUESTION], ids=["content", "record"])
def test_the_merged_pool_is_reranked_once_within_16_texts_and_24000_characters(phrased, box, standin, question):
    _set(phrased, True)
    data, requests = _ask(box, phrased, question)
    s.result(data)
    pool = [text for request in requests for text in request]
    assert len(pool) > CAP_TEXTS, f"premise: the merged pool holds more than {CAP_TEXTS} texts ({len(pool)})"
    assert len(set(pool)) == len(pool), "a text was given to the reranker twice: the merged pool was not reranked once"
    for number, request in enumerate(requests, 1):
        assert len(request) <= CAP_TEXTS and sum(map(len, request)) <= CAP_CHARS, \
            f"request {number}: {len(request)} texts, {sum(map(len, request))} characters (bounds 16, 24,000)"
    assert len(requests) == _fewest(pool), \
        f"{len(requests)} rerank requests where {_fewest(pool)} meet both bounds: not one rerank of the merged pool"


@pytest.mark.parametrize("question", [CONTENT_QUESTION, RECORD_TITLE_QUESTION], ids=["content", "record"])
def test_off_is_todays_bundle_byte_for_byte(phrased, box, standin, question):
    r.unset_routing(phrased)
    absent, absent_requests = _ask(box, phrased, question)
    _set(phrased, False)
    off, off_requests = _ask(box, phrased, question)
    assert json.dumps(s.result(off), sort_keys=True) == json.dumps(s.result(absent), sort_keys=True), \
        "routing.phrasings: false gives another bundle than no setting"
    assert off_requests == absent_requests, "routing.phrasings: false gives the reranker another pool than no setting"


@pytest.mark.parametrize("value", ["maybe", 2, [True]], ids=["word", "number", "list"])
def test_an_invalid_phrasings_value_is_config_invalid_naming_the_key(phrased, box, standin, value):
    _set(phrased, value)
    data, _ = _ask(box, phrased, CONTENT_QUESTION)
    raised = data.get("raised")
    assert raised, f"an invalid {KEY} ({value!r}) was taken: the retrieval answered"
    assert "CONFIG_INVALID" in (str(raised.get("code")) + raised["message"]), \
        f"the refusal is not CONFIG_INVALID: {raised['type']}: {raised['message']}"
    assert KEY in raised["message"], f"the refusal does not name {KEY}: {raised['message']}"
