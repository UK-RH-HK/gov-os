"""DEC-741 K (2): the capability records of the split and moved items follow Contract v4.2.

A reading staged for the owner to confirm or overturn: the records of CAP-43.b,
CAP-44.f and CAP-44.h are rewritten from the approved ``contract.yaml``, the
records of the new ids CAP-43.d, CAP-44.k and CAP-44.l are added, and the
"Covers:" lists of CAP-43 and CAP-44 follow.  This file holds only those
tests, so it can be dropped alone if the owner overturns the reading.  The
version line in every record (K (1)) is tested elsewhere and does not depend
on this file.

A record is DERIVED from ``contract.yaml`` (DEC-614): its frontmatter and body
must have the same form as an unchanged sibling record of the same capability
(CAP-43.a, CAP-44.a), with the item's own id, item text, wave and parent.
"""

from __future__ import annotations

import re

import pytest

from w2_49_support import (
    CONTRACT_YAML,
    MOVED_ITEMS,
    NEW_SPLIT_IDS,
    load_yaml_text,
    read_doc,
    read_record,
    require_v42,
    yaml_model,
)

SIBLING = {"CAP-43": "CAP-43.a", "CAP-44": "CAP-44.a"}


@pytest.fixture(scope="module")
def contract():
    text = read_doc(CONTRACT_YAML)
    caps = {c["id"]: c for c in load_yaml_text(text)["capabilities"]}
    return yaml_model(text), caps


def _shape(body: str, cap_id: str, item: str, parent: str, parent_title: str) -> str:
    """The record body with its own values replaced by placeholders."""
    out = body.replace(item, "{ITEM}").replace(cap_id, "{ID}").replace(parent_title, "{PARENT_TITLE}")
    out = re.sub(rf"{re.escape(parent)}(?![\w.])", "{PARENT}", out)
    return re.sub(r"^(- \*\*Wave:\*\*) \S+$", r"\1 {WAVE}", out, flags=re.MULTILINE)


@pytest.mark.parametrize("cap_id", MOVED_ITEMS + NEW_SPLIT_IDS)
def test_record_of_split_item_follows_contract_v4_2(contract, cap_id):
    """K (2): the record's title, item, wave and parent are those of v4.2, in its sibling records' form."""
    model, caps = contract
    require_v42(model)
    item = model.by_id().get(cap_id)
    assert item is not None, f"contract.yaml has no {cap_id}"
    text = str(item.raw["item"])
    parent = item.cap
    parent_title = caps[parent]["title"]

    meta, body = read_record(cap_id)
    sib_id = SIBLING[parent]
    sib_meta, sib_body = read_record(sib_id)
    sib = model.by_id()[sib_id]

    assert meta.get("id") == cap_id, f"{cap_id}.md: id is {meta.get('id')!r}"
    assert meta.get("title") == text, f"{cap_id}.md: title {meta.get('title')!r} is not v4.2's item {text!r}"
    assert meta.get("depends_on") == [parent], f"{cap_id}.md: depends_on {meta.get('depends_on')!r}, not [{parent}]"
    assert list(meta) == list(sib_meta), f"{cap_id}.md: frontmatter keys {list(meta)} differ from {sib_id}.md's"
    for key in ("type", "status", "state_class"):
        assert meta.get(key) == sib_meta.get(key), f"{cap_id}.md: {key} {meta.get(key)!r} differs from {sib_id}.md's"

    assert re.search(rf"^- \*\*Item:\*\* {re.escape(text)}$", body, re.MULTILINE), f"{cap_id}.md: Item line is not v4.2's item"
    assert re.search(rf"^- \*\*Wave:\*\* {item.wave}$", body, re.MULTILINE), f"{cap_id}.md: Wave line is not {item.wave}"
    assert _shape(body, cap_id, text, parent, parent_title) == _shape(
        sib_body, sib_id, str(sib.raw["item"]), parent, parent_title
    ), f"{cap_id}.md: body does not have the form of {sib_id}.md"


@pytest.mark.parametrize("cap", ["CAP-43", "CAP-44"])
def test_capability_record_covers_list_equals_contract_v4_2(contract, cap):
    """K (2): CAP-43's and CAP-44's "Covers:" lists hold exactly their covers ids in v4.2."""
    model, _ = contract
    require_v42(model)
    _, body = read_record(cap)
    m = re.search(r"^- \*\*Covers:\*\* (.+)$", body, re.MULTILINE)
    assert m, f"{cap}.md has no Covers line"
    listed = [s.strip() for s in m.group(1).split(",")]
    expected = [c.id for c in model.covers_of(cap)]
    assert len(listed) == len(set(listed)), f"{cap}.md lists a covers id twice: {listed}"
    assert set(listed) == set(expected), f"{cap}.md Covers {listed}, contract.yaml {expected}"
