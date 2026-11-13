"""W2-133 S3 (DEC-1083): nothing else in a bundle changes: the evidence set, its order, the batches, the budget used,
the gaps, ``left_out`` and the continuation, but for the ids and status fields S1 and S2 name.

"Before the fix" is ``retrieve.py`` and ``register.py`` as ``w2/integrate`` held them (``w2_133_support.TODAY_BLOBS``),
loaded from git beside the running tree's; both are asked on the same store, in the same process, with the same
stand-ins, through the same pipeline (``retrieve``, then ``leave_out``, as ``gov retrieve`` runs them), and through
``retrieve`` alone. The comparison takes off each register item's ``LABEL_FIELDS`` only, and compares the
continuation token decoded, without its ``s`` key: W2-138 S3 puts the store's commit there (DEC-1090 (3)), so a token
the code before the fix made has none. Every other key of the token is compared, and so is whether a token is given.
"""

from __future__ import annotations

import base64
import binascii
import json

import pytest

import w2_133_support as support

# (case name, question, keyword arguments of ``retrieve``)
SCENARIOS = [
    ("narrowed-inside-DEC-101", "persimmon", {}),
    ("alone-inside-DEC-101", "persimmon", {"bundle_budget": 300}),
    ("narrowed-from-the-gap", "lanterns", {}),
    ("alone-from-the-gap", "lanterns", {"bundle_budget": 300}),
    ("narrowed-into-DEC-476", "tamarind", {}),
    ("alone-into-DEC-476", "tamarind", {"bundle_budget": 300}),
    ("narrowed-inside-DEC-476", "cardamom", {}),
    ("alone-inside-DEC-476", "cardamom", {"bundle_budget": 300}),
    ("dec-100-left-out", "quince", {}),
    ("dec-100-left-out-alone", "quince", {"bundle_budget": 300}),
    ("the-preface", "almanac", {}),
    ("every-chunk", "orchard", {}),
    ("every-chunk-batched", "orchard", {"batch_size": 1}),
]
CASES = [pytest.param(*case, id=case[0]) for case in SCENARIOS]
FIELDS = ("evidence", "batches", "budget", "gaps", "left_out", "continuation", "expansions", "repeats", "merge",
          "facets", "stopping_reason", "rerank")


def _evidence(bundle):
    return [(item["path"], item["start_line"], item["end_line"], item["chunk_id"], item["sha256"])
            for item in bundle["evidence"]]


STORE_COMMIT_KEY = "s"  # the token's key W2-138 S3 adds: the store's commit (DEC-1090 (3))


def _token(token):
    """A continuation token decoded (base64 of a JSON object), without the store's commit key; no token stays as it
    is (None, or an empty string)."""
    if not token:
        return token
    try:
        payload = json.loads(base64.urlsafe_b64decode(token))
    except (TypeError, ValueError, binascii.Error) as error:
        raise AssertionError(f"the continuation token {token!r} is not base64 of JSON: {error}") from error
    assert isinstance(payload, dict), f"the continuation token decodes to {payload!r}, not an object"
    return {key: value for key, value in payload.items() if key != STORE_COMMIT_KEY}


def _comparable(bundle):
    """What S3 says the fix leaves unchanged: the bundle without the label fields, its token decoded without ``s``."""
    bare = support.without_labels(bundle)
    if "continuation" in bare:
        bare["continuation"] = _token(bare["continuation"])
    return bare


def _same(before, after):
    assert _evidence(after) == _evidence(before), "the evidence set or its order changed"
    old, new = _comparable(before), _comparable(after)
    for field in FIELDS:
        assert new.get(field) == old.get(field), f"the bundle's {field!r} changed"
    assert new == old, "the bundle changed beside the register items' ids and status fields"


def test_s3_premise_today_s_modules_are_the_code_before_the_fix(ask, today):
    items = support.register_items(ask("persimmon", modules=today))
    assert [item["id"] for item in items] == ["DEC-100"], \
        f"premise: today's pipeline keeps the parent's DEC-100 on the narrowed item; it gives {items}"


@pytest.mark.parametrize("pipeline", ["gov-retrieve", "retrieve-alone"])
@pytest.mark.parametrize("name, query, kwargs", CASES)
def test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status(ask, raw, today, pipeline, name, query,
                                                                             kwargs):
    asked = ask if pipeline == "gov-retrieve" else raw
    _same(asked(query, modules=today, **kwargs), asked(query, **kwargs))


@pytest.mark.parametrize("pipeline", ["gov-retrieve", "retrieve-alone"])
def test_s3_the_continued_pages_are_today_s_but_for_the_register_items_ids_and_status(ask, raw, today, pipeline):
    asked = ask if pipeline == "gov-retrieve" else raw
    kwargs = {"batch_size": 1}
    before = support.pages(lambda query, **more: asked(query, modules=today, **more), "orchard", kwargs)
    after = support.pages(asked, "orchard", kwargs)
    assert len(before) > 1, "premise: the batched question has more than one page"
    assert len(after) == len(before), f"{len(after)} pages, where today gives {len(before)}"
    for old, new in zip(before, after):
        _same(old, new)
