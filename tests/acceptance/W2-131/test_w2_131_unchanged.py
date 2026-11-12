"""W2-131 S3 (DEC-1082 (2)): nothing else in a bundle changes. On the planted repository the evidence set, its order,
the batches, the budget used, the gaps and the continuation are what today's code gives, but for the ids of register
items: each bundle of the running tree is compared, field by field and then whole, with the bundle of ``retrieve.py``
as ``w2/integrate`` held it before the fix (``w2_131_support.today``), asked on the same store in the same process.

The continuation token is compared decoded (base64 of a JSON object), without its ``s`` key: W2-138 S3 (``dcda27011``,
DEC-1090 (3)) puts the store's commit there, so a token the code before the fix made has none. The new token must carry
``s`` as a full commit (the same on every page of a question, one store), the old token must carry none (the premise
of "today"), and every other key of the two tokens, and whether a token is given at all, is compared as before.
"""

from __future__ import annotations

import base64
import binascii
import json
import re

import pytest

import w2_131_support as support

FIELDS = ("evidence", "batches", "budget", "gaps", "continuation", "expansions", "repeats", "merge", "facets",
          "stopping_reason", "rerank")


STORE_KEY = "s"  # the token's key W2-138 S3 adds: the store's commit (DEC-1090 (3))


def _payload(token):
    """A continuation token decoded: base64 of a JSON object."""
    try:
        payload = json.loads(base64.urlsafe_b64decode(token))
    except (TypeError, ValueError, binascii.Error) as error:
        raise AssertionError(f"the continuation token {token!r} is not base64 of JSON: {error}") from error
    assert isinstance(payload, dict), f"the continuation token decodes to {payload!r}, not an object"
    return payload


def _commit_of(bundle):
    """The store commit the bundle's token names (None: no token). Today's token (before W2-138) names none."""
    return _payload(bundle["continuation"]).get(STORE_KEY) if bundle.get("continuation") else None


def _without_store(bundle):
    """The bundle's token decoded without ``s`` (a bundle without a token stays as it is)."""
    if not bundle.get("continuation"):
        return bundle
    payload = _payload(bundle["continuation"])
    return {**bundle, "continuation": {key: value for key, value in payload.items() if key != STORE_KEY}}


def _account_for_the_store_key(now, before):
    """W2-138 S3 in the comparison: today's token names no store; the running tree's names a full commit."""
    if before.get("continuation"):
        assert STORE_KEY not in _payload(before["continuation"]), "premise: today's token holds no store commit"
    if now.get("continuation"):
        assert re.fullmatch(r"[0-9a-f]{40}", str(_commit_of(now))), \
            f"the token names no full store commit: {_commit_of(now)!r}"


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
    _account_for_the_store_key(now, before)
    now_bare = _without_store(support.without_register_ids(now))
    before_bare = _without_store(support.without_register_ids(before))
    changed = [field for field in FIELDS if now_bare.get(field) != before_bare.get(field)]
    assert not changed, f"fields that changed beside the register items' ids: {changed}"
    assert now_bare == before_bare, "the bundle changed beside the register items' ids"


def test_s3_the_continued_pages_are_todays_but_for_the_ids_of_register_items(today, ask):
    kwargs = {"ticket": support.TICKET, "batch_size": 2}
    now = support.pages(ask, "lantern", kwargs)
    before = support.pages(lambda query, **kw: ask(query, module=today, **kw), "lantern", kwargs)
    assert len(before) > 1, "premise: today's answer continues over more than one page"
    for page, was in zip(now, before):
        _account_for_the_store_key(page, was)
    assert len({_commit_of(page) for page in now if page["continuation"]}) == 1, \
        "the pages of one question name more than one store commit"
    assert [_without_store(support.without_register_ids(page)) for page in now] == \
        [_without_store(support.without_register_ids(page)) for page in before]
