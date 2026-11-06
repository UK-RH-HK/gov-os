"""W2-131 S3 (DEC-1082 (2)): nothing else in a bundle changes. On the planted repository the evidence set, its order,
the batches, the budget used, the gaps and the continuation are what today's code gives, but for the ids of register
items: each bundle of the running tree is compared, field by field and then whole, with the bundle of ``retrieve.py``
as ``w2/integrate`` held it before the fix (``w2_131_support.today``), asked on the same store in the same process.
"""

from __future__ import annotations

import pytest

import w2_131_support as support

FIELDS = ("evidence", "batches", "budget", "gaps", "continuation", "expansions", "repeats", "merge", "facets",
          "stopping_reason", "rerank")


def _place(bundle):
    """The evidence set in its order: where each item lies and what it holds, its id left out."""
    return [(item["path"], item["start_line"], item["end_line"], item["chunk_id"], item["sha256"])
            for item in bundle["evidence"]]


def test_s3_premise_todays_module_is_the_code_before_the_fix(today, ask):
    (item,) = support.register_items(ask("marigold", module=today))
    assert item["id"] == "DEC-999", "premise: today's retrieve labels DEC-476's chunk DEC-999 (the bug of W2-131)"


@pytest.mark.parametrize("name, query, kwargs", [pytest.param(*case, id=case[0]) for case in support.SCENARIOS])
def test_s3_the_bundle_is_todays_but_for_the_ids_of_register_items(today, ask, name, query, kwargs):
    now, before = ask(query, **kwargs), ask(query, module=today, **kwargs)
    assert _place(now) == _place(before), "the evidence set or its order changed"
    now_bare, before_bare = support.without_register_ids(now), support.without_register_ids(before)
    changed = [field for field in FIELDS if now_bare.get(field) != before_bare.get(field)]
    assert not changed, f"fields that changed beside the register items' ids: {changed}"
    assert now_bare == before_bare, "the bundle changed beside the register items' ids"


def test_s3_the_continued_pages_are_todays_but_for_the_ids_of_register_items(today, ask):
    kwargs = {"ticket": support.TICKET, "batch_size": 2}
    now = support.pages(ask, "lantern", kwargs)
    before = support.pages(lambda query, **kw: ask(query, module=today, **kw), "lantern", kwargs)
    assert len(before) > 1, "premise: today's answer continues over more than one page"
    assert [support.without_register_ids(page) for page in now] == \
        [support.without_register_ids(page) for page in before]
