"""S11 (DEC-1071 (2), approved for re-pin window 4 by DEC-1074 (5)): the candidate pool, v456.

The line: five query-time settings in ``governance/project/retrieval.yaml``, each absent or 0 meaning today's
behaviour, the loader refusing an invalid value with ``CONFIG_INVALID`` naming the key: ``pool.meaning_uncut`` (the
meaning route's phrasings fused and not cut back to its depth), ``pool.route_depth`` (the keyword and meaning routes'
depth, 30 today), ``pool.rerank_depth`` (the first n fused candidates reranked once, in one pass under the padded
request bound, and the pages cut from that order, in place of each page's 20 reranked apart), ``pool.per_file_first10``
(at most n chunks of one file in the first 10 of the final order, the rest kept after them) and ``pool.drop_nested``
(an item whose lines lie inside an earlier item's of the same file dropped from the bundle). The failure line: a pool
setting absent or 0 that changes what a search returns; a rerank pass that sends a request past the padded bound.

Every case asks ``gov.retrieval.retrieve.retrieve`` of a planted store (``w2_32_pool``) with a stand-in reranker that
keeps each request it receives (``calls``: a hash score, no ties; ``ranks``: the text's ``rankNN``). "Today" is the
same call with the setting absent; each case compares the setting's bundle with today's on the same store.

- **The pool store** (``route_depth``, ``rerank_depth``, the bound): forty long keyword notes (about 2,400 characters,
  one chunk each, not embedded: the keyword route's first 40) and sixty short meaning notes (embedded, two of the
  question's words: the meaning route's first, the keyword route's after the long notes). Today the routes give 30
  each, disjoint, so the fused list holds 60 and today's first two pages each rerank 20 of them apart.
- **The phrased store** (``meaning_uncut``; ``routing.phrasings: true`` on in both runs): seventy notes that every
  phrasing's meaning route finds alike and no keyword finds, and ``docs/rota.md``, which only the phrasing with
  ``CAP-88`` appended finds by meaning (the first of its list); fused, the cut to the route's depth leaves it out.
- **The files store** (``per_file_first10``): a note of six short sections (one chunk each, the reranker's first six)
  and one of three, then sixteen one-chunk notes.
- **The nested store** (``drop_nested``): two notes of the same layout whose one long section is three or more
  chunks; the first of each the rerank puts first is expanded to the section, so its other chunks lie inside it; the
  two sections hold the same lines in two files.
- **Together** (60, 40, 2 and both true, ``V456``): on each store, each effect on top of the other four (today being
  ``V456`` without that one setting), and two runs give the same bundle.

The KPI's "the product's own path gives the research harness's v456 result question for question" and its speed line
are the CTO's measures on the shared servers, verified by the evidence file, not by a case here (README).
"""

from __future__ import annotations

import json

import pytest

import w2_32_driver as driver
import w2_32_pool as p
import w2_32_support as s

PHRASINGS = {"phrasings": True}


@pytest.fixture
def pool_store(tmp_path, needs_vectors, box):
    project = p.plant_pool(tmp_path / "pool")
    box.built(project)
    return project


@pytest.fixture
def phrased_store(tmp_path, needs_vectors, box):
    project = p.plant_phrased(tmp_path / "phrased")
    box.built(project)
    return project


@pytest.fixture
def files_store(tmp_path, needs_vectors, box):
    project = p.plant_files(tmp_path / "files")
    box.built(project)
    return project


@pytest.fixture
def nested_store(tmp_path, needs_vectors, box):
    project = p.plant_nested(tmp_path / "nested")
    box.built(project)
    return project


STORES = {"pool": ("pool_store", p.POOL_QUESTION, None, "calls"),
          "phrased": ("phrased_store", p.PHRASED_QUESTION, PHRASINGS, "calls"),
          "files": ("files_store", p.FILES_QUESTION, None, "ranks"),
          "nested": ("nested_store", p.NESTED_QUESTION, None, "calls")}


def _store(request, name):
    fixture, question, routing, kind = STORES[name]
    return request.getfixturevalue(fixture), question, routing, kind


def _bundle(box, project, question, pool=None, routing=None, kind="calls", **options):
    """The bundle and the rerank requests, the settings written first (``pool`` None: no pool block)."""
    p.settle(project, pool=pool, routing=routing)
    data, requests = p.ask(box, project, question, kind=kind, **options)
    return s.result(data), requests


def _pages(box, project, question, pool=None, routing=None, kind="calls", **options):
    """The first page and the next (by its continuation): each its bundle and its rerank requests."""
    first, first_requests = _bundle(box, project, question, pool, routing, kind, **options)
    assert first["continuation"], f"premise: the question has a second page ({first['stopping_reason']})"
    second, second_requests = _bundle(box, project, question, pool, routing, kind,
                                      continuation=first["continuation"], **options)
    return (first, first_requests), (second, second_requests)


def _route_counts(bundle):
    counts = {}
    for item in bundle["evidence"]:
        for route in item["routes"]:
            counts[route] = counts.get(route, 0) + 1
    return counts


def _without(setting):
    return {name: value for name, value in p.V456.items() if name != setting}


# ---- absent or 0: today's bundle, item for item (the failure line) --------------------------------------------------

@pytest.mark.parametrize("form", ["zeros", "empty-block", "bare-block"])
@pytest.mark.parametrize("store", sorted(STORES))
def test_with_every_pool_setting_absent_or_0_the_bundle_is_todays(request, box, standin, store, form):
    """No file against a ``pool`` block of five zeros (false for the two flags), an empty block (``pool: {}``) or a
    bare ``pool:``: the same bundle, byte for byte, and the same rerank requests."""
    project, question, routing, kind = _store(request, store)
    today, today_requests = _bundle(box, project, question, routing=routing, kind=kind)
    if form == "bare-block":
        p.settle(project, raw=(p.yaml.safe_dump({"routing": routing}) if routing else "") + f"{p.BLOCK}:\n")
        data, off_requests = p.ask(box, project, question, kind=kind)
        off = s.result(data)
    else:
        off, off_requests = _bundle(box, project, question, pool=p.OFF if form == "zeros" else {}, routing=routing,
                                    kind=kind)
    assert json.dumps(off, sort_keys=True) == json.dumps(today, sort_keys=True), \
        f"pool settings off ({form}) changed what the search returns: {p.items(off)[:4]} against {p.items(today)[:4]}"
    assert off_requests == today_requests, f"pool settings off ({form}) changed what the reranker was sent"


# ---- an invalid value: CONFIG_INVALID naming the key -------------------------------------------------------------

INVALID = {name: ["maybe", [True]] for name in p.FLAGS}
INVALID.update({name: [-1, "many", [2], True] for name in p.COUNTS})


@pytest.mark.parametrize("name", p.KEYS)
def test_an_invalid_pool_value_is_config_invalid_naming_the_key(files_store, box, standin, name):
    """A wrong type or a negative number, for each key: a word and a list for the flags; a negative number, a word,
    a list and true for the counts."""
    for value in INVALID[name]:
        p.settle(files_store, pool={name: value})
        data, _ = p.ask(box, files_store, p.FILES_QUESTION)
        raised = data.get("raised")
        assert raised, f"an invalid {p.key(name)} ({value!r}) was taken: the retrieval answered"
        assert "CONFIG_INVALID" in (str(raised.get("code")) + raised["message"]), \
            f"{p.key(name)} = {value!r}: the refusal is not CONFIG_INVALID: {p.raised_text(data)}"
        assert p.key(name) in raised["message"], \
            f"{p.key(name)} = {value!r}: the refusal does not name the key {p.key(name)}: {raised['message']}"


# ---- route_depth: both routes return up to that depth -------------------------------------------------------------

@pytest.mark.parametrize("depth", [10, 60])
def test_route_depth_has_the_keyword_and_meaning_routes_return_up_to_that_depth(pool_store, box, standin, depth):
    """With a page wide enough for the whole fused list (a batch of 100), the evidence names each route's chunks:
    today 30 each; with the setting, ``depth`` each (the store holds more than 60 chunks either route finds)."""
    today, _ = _bundle(box, pool_store, p.POOL_QUESTION, batch_size=100)
    assert today["continuation"] is None, "premise: the page holds the whole fused list"
    counts = _route_counts(today)
    assert (counts.get("lexical"), counts.get("semantic")) == (p.TODAY_DEPTH, p.TODAY_DEPTH), \
        f"premise: today each route gives {p.TODAY_DEPTH}: {counts}"
    deep, _ = _bundle(box, pool_store, p.POOL_QUESTION, pool={"route_depth": depth}, batch_size=100)
    assert deep["continuation"] is None, "premise: the page holds the whole fused list"
    counts = _route_counts(deep)
    assert counts.get("lexical") == depth, f"pool.route_depth {depth}: the keyword route gave {counts.get('lexical')}"
    assert counts.get("semantic") == depth, \
        f"pool.route_depth {depth}: the meaning route gave {counts.get('semantic')}"


# ---- rerank_depth: the first n fused, reranked once; the pages cut from that one order ------------------------------

def _first_fused(box, project, settings=None):
    """The first 40 fused candidates, as today's first two pages send them to the reranker (20 each, apart)."""
    (one, one_requests), (two, two_requests) = _pages(box, project, p.POOL_QUESTION, settings)
    first = [text for request in one_requests for text in request]
    second = [text for request in two_requests for text in request]
    assert len(first) == len(set(first)) == p.PAGE and len(second) == len(set(second)) == p.PAGE, \
        f"premise: today each page reranks {p.PAGE} apart ({len(first)}, {len(second)})"
    assert not set(first) & set(second), "premise: the two pages rerank different candidates"
    return set(first) | set(second)


def _cut_from_one_order(pool, one, two):
    """The first page is the first 20 of the reranker's order of the pool, the second page the next 20."""
    order = sorted(pool, key=driver.hashed_score, reverse=True)
    pages = [[p.text_of(item) for item in page["evidence"]] for page in (one, two)]
    assert pages[0] == order[:p.PAGE], \
        f"the first page is not the first {p.PAGE} of the one rerank's order: {[p.path_of(t) for t in pages[0][:5]]} " \
        f"against {[p.path_of(t) for t in order[:5]]}"
    assert pages[1] == order[p.PAGE:2 * p.PAGE], \
        f"the second page is not the next {p.PAGE} of that order (a page reranked apart): " \
        f"{[p.path_of(t) for t in pages[1][:5]]} against {[p.path_of(t) for t in order[p.PAGE:p.PAGE + 5]]}"


def _reranked_once(requests, pool):
    sent = [text for request in requests for text in request]
    assert len(sent) == len(set(sent)), "a candidate was sent to the reranker twice: not one pass"
    assert set(sent) == pool, f"the reranker was not sent the first {len(pool)} fused candidates: {len(set(sent))} " \
                              f"sent, {len(set(sent) - pool)} not among them, {len(pool - set(sent))} left out"
    p.within_bound(requests)
    assert len(requests) == p.fewest(sent), \
        f"{len(requests)} rerank requests where {p.fewest(sent)} meet the padded bound: not one pass"


def test_rerank_depth_reranks_the_first_n_fused_once_and_cuts_the_pages_from_that_order(pool_store, box, standin):
    pool = _first_fused(box, pool_store)
    (one, one_requests), (two, two_requests) = _pages(box, pool_store, p.POOL_QUESTION, {"rerank_depth": 40})
    _reranked_once(one_requests, pool)
    _cut_from_one_order(pool, one, two)
    p.within_bound(two_requests)


@pytest.mark.parametrize("settings", ["rerank_depth", "v456"])
def test_every_rerank_request_keeps_the_padded_bound(pool_store, box, standin, settings):
    """The second failure line: with 40 reranked in one pass, about half of them 2,400 characters long, no request
    goes past 16 texts or 24,000 characters padded, on either page."""
    chosen = {"rerank_depth": 40} if settings == "rerank_depth" else p.V456
    (_, one_requests), (_, two_requests) = _pages(box, pool_store, p.POOL_QUESTION, chosen)
    sent = [text for request in one_requests for text in request]
    assert len(sent) >= 40, f"premise: 40 candidates were reranked in the pass ({len(sent)})"
    assert sum(1 for text in sent if len(text) > 2_000) * 2_000 > p.CAP_CHARS, \
        "premise: the pass holds more long candidates than one request can carry"
    p.within_bound(one_requests)
    p.within_bound(two_requests)


# ---- meaning_uncut: a chunk only one phrasing finds stays in the meaning route's list ------------------------------

def _meaning_premise(box, project, bundle):
    """The phrasings the bundle names; ``ONLY_ID`` the meaning route's for the one with CAP-88 appended only."""
    asked = (bundle.get("routing") or {}).get("phrasings") or []
    assert len(asked) == 3, f"premise: the question is searched in three phrasings: {asked}"
    found = {}
    for phrasing in asked:
        hits = s.result(box.call("semantic_search", root=str(project), query=phrasing))["hits"]
        found[phrasing] = p.ONLY_ID in {hit["path"] for hit in hits}
    assert [found[phrasing] for phrasing in asked] == [False, False, True], \
        f"premise: {p.ONLY_ID} is in the meaning route's list of the phrasing with CAP-88 appended alone: {found}"


def _by_meaning(bundle):
    return {item["path"] for item in bundle["evidence"] if "semantic" in item["routes"]}


def test_meaning_uncut_keeps_a_chunk_only_one_phrasing_finds_in_the_meaning_routes_list(phrased_store, box, standin):
    today, _ = _bundle(box, phrased_store, p.PHRASED_QUESTION, routing=PHRASINGS, batch_size=100)
    _meaning_premise(box, phrased_store, today)
    assert today["continuation"] is None, "premise: the page holds the whole fused list"
    assert p.ONLY_ID not in _by_meaning(today), \
        f"premise: today the phrasings' fused meaning list, cut to its depth, leaves {p.ONLY_ID} out"
    uncut, _ = _bundle(box, phrased_store, p.PHRASED_QUESTION, pool={"meaning_uncut": True}, routing=PHRASINGS,
                       batch_size=100)
    assert p.ONLY_ID in _by_meaning(uncut), \
        f"pool.meaning_uncut: {p.ONLY_ID}, which one phrasing finds, was cut from the meaning route's list"
    assert _by_meaning(today) <= _by_meaning(uncut), "pool.meaning_uncut lost a chunk of the meaning route's list"


# ---- per_file_first10: at most n of a file in the first 10, the rest after them, none lost -------------------------

@pytest.mark.parametrize("n", [1, 2])
def test_per_file_first10_holds_at_most_n_of_a_file_in_the_first_10_and_loses_none(files_store, box, standin, n):
    today, _ = _bundle(box, files_store, p.FILES_QUESTION, kind="ranks")
    counts = {}
    for item in today["evidence"][:10]:
        counts[item["path"]] = counts.get(item["path"], 0) + 1
    assert counts.get(p.ALMANAC, 0) > n and counts.get(p.TIDE_BOOK, 0) >= n, \
        f"premise: today the almanac holds more than {n} of the first 10, the tide book {n} or more: {counts}"
    capped, _ = _bundle(box, files_store, p.FILES_QUESTION, pool={"per_file_first10": n}, kind="ranks")
    first = {}
    for item in capped["evidence"][:10]:
        first[item["path"]] = first.get(item["path"], 0) + 1
    assert max(first.values()) <= n, f"pool.per_file_first10 {n}: a file holds more in the first 10: {first}"
    assert sorted(p.items(capped)) == sorted(p.items(today)), "pool.per_file_first10 lost or added an item"
    assert p.items(capped) == p.items({"evidence": p.capped(today["evidence"], n)}), \
        f"pool.per_file_first10 {n}: the first 10 are not today's order with the file's extra chunks passed over, " \
        f"or the rest do not follow in their order"


# ---- drop_nested: an item inside an earlier item's lines of the same file is dropped --------------------------------

def _nested_premise(evidence):
    inside = p.nested(evidence)
    paths = {evidence[at]["path"] for at in inside}
    assert {p.QUAY_LOG, p.ROPE_LOG} <= paths, f"premise: both logs have an item inside an earlier one: {sorted(paths)}"
    outer = {(item["path"], item["start_line"], item["end_line"]) for at, item in enumerate(evidence)
             if at not in inside}
    lines = {(a, b) for path, a, b in outer if path == p.QUAY_LOG} & {(a, b) for path, a, b in outer
                                                                      if path == p.ROPE_LOG}
    assert lines, "premise: the two logs each hold an outer item of the same lines"
    return inside, lines


def test_drop_nested_drops_an_item_inside_an_earlier_items_lines_of_the_same_file(nested_store, box, standin):
    today, _ = _bundle(box, nested_store, p.NESTED_QUESTION)
    inside, lines = _nested_premise(today["evidence"])
    dropped, _ = _bundle(box, nested_store, p.NESTED_QUESTION, pool={"drop_nested": True})
    assert not p.nested(dropped["evidence"]), \
        f"pool.drop_nested: items inside an earlier item's lines remain: {p.nested(dropped['evidence'])}"
    expected = [item for at, item in enumerate(p.items(today)) if at not in inside]
    assert p.items(dropped) == expected, \
        "pool.drop_nested dropped other than the items inside an earlier item's lines of the same file"
    kept = {(item["path"], item["start_line"], item["end_line"]) for item in dropped["evidence"]}
    for a, b in lines:
        assert {(p.QUAY_LOG, a, b), (p.ROPE_LOG, a, b)} <= kept, \
            f"pool.drop_nested dropped an item of another file with the same lines ({a}-{b})"


# ---- together: 60, 40, 2 and both true ---------------------------------------------------------------------------

def test_v456_route_depth_reaches_past_todays_depth_with_the_others_on(pool_store, box, standin):
    """At depth 30 the keyword route's list is the forty long notes' first 30, so no meaning note carries the keyword
    route; at 60 it reaches twenty meaning notes, which both routes then name, so they are fused first and reranked."""
    meaning = lambda bundle: {item["path"] for item in bundle["evidence"]  # noqa: E731
                              if item["path"].startswith("docs/meaning-") and "lexical" in item["routes"]}
    today, _ = _bundle(box, pool_store, p.POOL_QUESTION, pool=_without("route_depth"), batch_size=100)
    assert not meaning(today), f"premise: at depth 30 no meaning note carries the keyword route: {sorted(meaning(today))}"
    together, _ = _bundle(box, pool_store, p.POOL_QUESTION, pool=p.V456, batch_size=100)
    assert len(meaning(together)) >= 10, \
        f"v456: the keyword route did not reach past depth 30 ({len(meaning(together))} meaning notes by keyword)"


def test_v456_rerank_depth_reranks_the_first_40_once_and_cuts_the_pages_with_the_others_on(pool_store, box, standin):
    pool = _first_fused(box, pool_store, _without("rerank_depth"))
    (one, one_requests), (two, _) = _pages(box, pool_store, p.POOL_QUESTION, p.V456)
    _reranked_once(one_requests, pool)
    _cut_from_one_order(pool, one, two)


def test_v456_meaning_uncut_keeps_the_chunk_one_phrasing_finds_with_the_others_on(phrased_store, box, standin):
    today, _ = _bundle(box, phrased_store, p.PHRASED_QUESTION, pool=_without("meaning_uncut"), routing=PHRASINGS,
                       batch_size=100)
    _meaning_premise(box, phrased_store, today)
    assert p.ONLY_ID in {item["path"] for item in today["evidence"]} and p.ONLY_ID not in _by_meaning(today), \
        f"premise: without meaning_uncut {p.ONLY_ID} is in the bundle by keyword, not by meaning"
    together, _ = _bundle(box, phrased_store, p.PHRASED_QUESTION, pool=p.V456, routing=PHRASINGS, batch_size=100)
    assert p.ONLY_ID in _by_meaning(together), f"v456: {p.ONLY_ID} was cut from the meaning route's list"


def test_v456_per_file_first10_holds_with_the_others_on(files_store, box, standin):
    today, _ = _bundle(box, files_store, p.FILES_QUESTION, pool=_without("per_file_first10"), kind="ranks")
    together, _ = _bundle(box, files_store, p.FILES_QUESTION, pool=p.V456, kind="ranks")
    assert p.items(together) == p.items({"evidence": p.capped(today["evidence"], 2)}), \
        "v456: the first 10 are not at most 2 of a file, the rest in their order, none lost"


def test_v456_drop_nested_holds_with_the_others_on(nested_store, box, standin):
    today, _ = _bundle(box, nested_store, p.NESTED_QUESTION, pool=_without("drop_nested"))
    inside, lines = _nested_premise(today["evidence"])
    together, _ = _bundle(box, nested_store, p.NESTED_QUESTION, pool=p.V456)
    assert not p.nested(together["evidence"]), "v456: an item inside an earlier item's lines of the same file remains"
    assert p.items(together) == [item for at, item in enumerate(p.items(today)) if at not in inside], \
        "v456: other than the nested items were dropped, or the rest moved"
    kept = {(item["path"], item["start_line"], item["end_line"]) for item in together["evidence"]}
    assert all({(p.QUAY_LOG, a, b), (p.ROPE_LOG, a, b)} <= kept for a, b in lines), \
        "v456: an item of another file with the same lines was dropped"


@pytest.mark.parametrize("store", sorted(STORES))
def test_v456_two_runs_on_one_store_give_the_same_bundle(request, box, standin, store):
    project, question, routing, kind = _store(request, store)
    first, first_requests = _bundle(box, project, question, pool=p.V456, routing=routing, kind=kind)
    second, second_requests = _bundle(box, project, question, pool=p.V456, routing=routing, kind=kind)
    assert json.dumps(second, sort_keys=True) == json.dumps(first, sort_keys=True), "v456: two runs, two bundles"
    assert second_requests == first_requests, "v456: two runs sent the reranker different requests"
