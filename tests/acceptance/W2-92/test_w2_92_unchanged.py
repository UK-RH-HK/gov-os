"""KPI success 4 and failure 1: a question that names no record and no symbol gets today's bundle, item for item;
the budget, the batches, the continuation and DEC-424's records ahead are as today; two runs give one bundle.

"Today's bundle" is pinned here as the integrated code gives it for the same planted project, through the same
public call, and checked live against the plain fused order of the lexical route (the one route of today that
answers in these projects): see the README. It was recorded at the base (``7ca16b19df3f``); W2-112 (the shared
reranker, merged into ``w2/integrate`` in D-1) then added one field, ``rerank``, to every bundle, recorded here as
``w2/integrate`` ``23625eb2aebe`` gives it (every other field is the same there as at the base). ``rerank`` is part
of the baseline, not a W2-92 change; any other new or changed field, ordering or content still fails.

Revised under DEC-1055 (D-4b) for W2-13's S2 (the fusion receives the lexical route's ranked list, BM25, beside the
semantic one): the pins are W2-13's head ``d6cba69e`` (the code that lands on ``w2/integrate`` with it). The plain
question's bundle gains the three chunks BM25 finds for its words without the whole phrase (README, the register's
head, the lantern note) after the six pages that hold the phrase; the "unknown id" question's bundle is the plain
question's (the id adds nothing: it is in no planted line and names no record); the ticket's lesson and ticket
chunks come in BM25 order, the lesson still first (DEC-424). Every other field is as before."""

from __future__ import annotations

import json

import pytest

import w2_92_support as support

_FACETS = {"lexical": {"available": True, "reason": None}, "semantic": {"available": False, "reason": "missing"}}
_PAGES = [("f5431210fb79ceedf8270e11", "docs/notes/almanac-01.md", 1, 3),
          ("6b369914a2ac01d256af1f92", "docs/notes/almanac-02.md", 1, 3),
          ("e16af13d42dcf1d94e748141", "docs/notes/almanac-03.md", 1, 3),
          ("df0c0dd84be760c3242087b9", "docs/notes/almanac-04.md", 1, 3),
          ("8cea80a3d80d8f32e9816bb2", "docs/notes/almanac-05.md", 1, 3),
          ("54357424c79d75175ff68807", "docs/notes/almanac-06.md", 1, 3)]
# W2-13's S2: the chunks BM25 finds for the plain question's words (not the whole phrase), after the six exact pages
_WORDS = [("7047140dfe53921fe3bb59d0", "README.md", 1, 3),
          ("277c09087eff4367a1818695", "docs/DECISION_REGISTER.md", 1, 4),
          ("f9a08303a4c56b10ee758a41", "docs/notes/lantern-note.md", 1, 3)]
_ALL = _PAGES + _WORDS
# W2-112's field (``rerank``), as w2/integrate 23625eb2aebe gives it with no reranker: candidates to score and none
# loaded, or nothing to score
_NOT_LOADED = {"by": "unavailable", "device": None, "reason": "the reranker given could not be loaded"}
_NOTHING = {"by": "unavailable", "device": None, "reason": "nothing to rerank"}
_EMPTY = {"batches": [{"size": 0}], "budget": {"bundle": {"limit": 6000, "used": 0}, "rounds": {"limit": 1, "used": 0}},
          "continued": False, "evidence": [], "expansions": [], "facets": _FACETS, "gaps": [],
          "merge": {"candidates": 0, "dropped": [], "duplicates": 0, "reranked": False},
          "rerank": _NOTHING, "stopping_reason": "FACET_UNAVAILABLE"}

# The integrated code's bundles (support.projection): recorded at the base 7ca16b19df3f, with W2-112's ``rerank``
# recorded at w2/integrate 23625eb2aebe, then re-pinned at W2-13's head d6cba69e for its S2 (DEC-1055)
_PLAIN = {"batches": [{"size": 9}], "budget": {"bundle": {"limit": 6000, "used": 157},
                                               "rounds": {"limit": 1, "used": 0}},
          "continued": False, "evidence": _ALL, "expansions": [], "facets": _FACETS, "gaps": [],
          "merge": {"candidates": 9, "dropped": [], "duplicates": 0, "reranked": False},
          "rerank": _NOT_LOADED, "stopping_reason": "FACET_UNAVAILABLE"}
TODAY = {
    "plain": _PLAIN,
    "batched": {"batches": [{"size": 2}, {"size": 2}], "budget": {"bundle": {"limit": 6000, "used": 72},
                                                                  "rounds": {"limit": 1, "used": 1}},
                "continued": True, "evidence": _ALL[:4], "expansions": [], "facets": _FACETS,
                "gaps": [{"chunk_id": chunk, "path": path, "reason": "NOT_GATHERED"} for chunk, path, _, _ in _ALL[4:]],
                "merge": {"candidates": 4, "dropped": [], "duplicates": 0, "reranked": False},
                "rerank": _NOT_LOADED, "stopping_reason": "FACET_UNAVAILABLE"},
    "batched, continued": {"batches": [{"size": 2}, {"size": 2}], "budget": {"bundle": {"limit": 6000, "used": 69},
                                                                             "rounds": {"limit": 1, "used": 1}},
                           "continued": True, "evidence": _ALL[4:8], "expansions": [], "facets": _FACETS,
                           "gaps": [{"chunk_id": chunk, "path": path, "reason": "NOT_GATHERED"}
                                    for chunk, path, _, _ in _ALL[8:]],
                           "merge": {"candidates": 4, "dropped": [], "duplicates": 0, "reranked": False},
                           "rerank": _NOT_LOADED, "stopping_reason": "FACET_UNAVAILABLE"},
    "unknown id": _PLAIN,
    "unknown symbol": _EMPTY,
    "ticket": {"batches": [{"size": 4}], "budget": {"bundle": {"limit": 6000, "used": 92},
                                                    "rounds": {"limit": 1, "used": 0}},
               "continued": False,
               "evidence": [("1c73338107f27cca669bc5d8", support.LESSON_REL, 11, 13),
                            ("e199fe38e2e12cd2f446245f", support.LESSON_REL, 1, 10),
                            ("42397a5310ce4fa38331bdec", support.TICKET_REL, 9, 11),
                            ("5a7ba3b5a82464c9fa94703f", support.TICKET_REL, 1, 8)],
               "expansions": [], "facets": _FACETS, "gaps": [],
               "merge": {"candidates": 4, "dropped": [], "duplicates": 3, "reranked": False},
               "rerank": _NOT_LOADED, "stopping_reason": "FACET_UNAVAILABLE"},
}

CASES = {
    "plain": (support.PLAIN_PHRASE, {}),
    "batched": (support.PLAIN_PHRASE, {"batch_size": 2}),
    "unknown id": (f"{support.PLAIN_PHRASE} DEC-999", {}),
    "unknown symbol": ("who calls w92_nowhere", {}),
    "ticket": ("paint", {"ticket": support.NAMED_TICKET}),
}


def _same(found, expected):
    """Compare through JSON, so a tuple and a list of the same items are one."""
    return json.loads(json.dumps(found, sort_keys=True)) == json.loads(json.dumps(expected, sort_keys=True))


def _diff(found, expected):
    keys = sorted(set(found) | set(expected))
    return {key: {"now": found.get(key), "today": expected.get(key)} for key in keys
            if not _same(found.get(key), expected.get(key))}


@pytest.mark.parametrize("case", list(CASES), ids=list(CASES))
def test_u1_a_question_naming_no_record_or_symbol_gets_todays_bundle(asked, case):
    """Failure 1: the plain question, the same in batches, an id the store does not hold, a symbol the index does
    not hold, and DEC-424's records ahead (a ticket's lesson first) give the integrated code's bundle, item for
    item (W2-112's ``rerank`` included)."""
    question, kwargs = CASES[case]
    bundle, _ = asked("full", question, **kwargs)
    found = support.projection(bundle)
    assert _same(found, TODAY[case]), f"{case}: the bundle differs from today's: {_diff(found, TODAY[case])}"
    if case == "batched":
        following, _ = asked("full", question, continuation=bundle["continuation"], **kwargs)
        found = support.projection(following)
        expected = TODAY["batched, continued"]
        assert _same(found, expected), f"the continued page differs from today's: {_diff(found, expected)}"


def test_u2_todays_bundle_is_the_plain_fused_order_of_todays_routes(api, planted, asked):
    """The live check of the pinned answer: the plain question's evidence is the lexical route's fused order (its
    ranked list, W2-13's S2)."""
    bundle, _ = asked("full", support.PLAIN_PHRASE)
    plain = api.plain_order(planted("full"), support.PLAIN_PHRASE)
    assert [(item[0], item[1]) for item in support.items(bundle)] == plain, (support.items(bundle), plain)
    assert [(chunk, path) for chunk, path, _, _ in _ALL] == plain, "the pinned answer is not today's fused order"


@pytest.mark.parametrize("question", [f"who calls {support.LEAF} under {support.NAMED_DEC}", support.PLAIN_PHRASE],
                         ids=["new routes", "plain"])
def test_u3_two_runs_on_one_store_give_the_same_bundle(api, planted, question):
    first, _ = api.retrieve(planted("full"), question)
    second, _ = api.retrieve(planted("full"), question)
    assert _same(first, second), f"two runs of {question!r} differ: {_diff(first, second)}"


def test_u4_a_batched_answer_with_a_new_route_continues_to_its_end_within_the_budget(api, planted):
    """``batch_size=1``: the pages, followed by their continuation to the last, together hold the new routes'
    evidence (the named decision and the callers), no item twice, each page's parent expansions within its budget.

    The budget is DEC-419 DP-3's (W1-21's approved spec): it bounds parent expansion only, and a child hit is never
    dropped for it. So a page whose gathered chunks alone pass the budget is not cut, and expands nothing; a page
    that names an expansion is within its budget (revised under DEC-1055 for P-W2-13-R3 (a); whether the budget
    should bound the whole bundle is W2-32's S5, with its own tests)."""
    question = f"who calls {support.LEAF} under {support.NAMED_DEC}"
    root, token, pages = planted("full"), None, []
    while len(pages) < 12:
        bundle, _ = api.retrieve(root, question, batch_size=1, bundle_budget=400, continuation=token)
        pages.append(bundle)
        budget = bundle["budget"]["bundle"]
        assert budget["limit"] == 400, f"page {len(pages)} does not carry the budget asked for: {budget}"
        assert not bundle["expansions"] or budget["used"] <= budget["limit"], \
            f"page {len(pages)} expanded a parent past its budget: {budget}; expansions {bundle['expansions']}"
        token = bundle.get("continuation")
        if token is None:
            break
    assert token is None, "the continuation did not end within 12 pages"
    every = [item for page in pages for item in support.items(page)]
    assert len(every) == len(set(every)), f"an item is on two pages: {every}"
    together = {"evidence": [item for page in pages for item in page["evidence"]]}
    assert support.holds_text(together, support.NAMED_DEC_TEXT), \
        f"no page holds {support.NAMED_DEC}'s evidence: {every}"
    missing = [name for name in support.CALLERS[support.LEAF] if not support.covers(together, *support.SPANS[name])]
    assert not missing, f"no page holds the callers {missing}: {every}"
