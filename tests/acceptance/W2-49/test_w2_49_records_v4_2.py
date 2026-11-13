"""DEC-750 item 5 (P-W2-16): CAP-45.a's record and every record's status follow the approved Contract v4.2.

The records under ``docs/contract/capabilities/`` are DERIVED from
``contract.yaml`` (DEC-614).

- CAP-45.a's record is regenerated from v4.2: its title, its heading and its
  ``Item:`` line are ``contract.yaml``'s CAP-45.a item text (the Wave 2
  wording of DEC-741 D (ii)), in the form of the unchanged sibling CAP-45.b.
- Every record's ``status:`` is the Contract's: the status both Contract files
  state, ACCEPTED.
"""

from __future__ import annotations

import re

import pytest

from w2_49_support import (
    CONTRACT_YAML,
    capability_record_paths,
    contract_status,
    frontmatter,
    load_yaml_text,
    read_doc,
    read_record,
    record_shape,
    require_v42,
    yaml_model,
)

RECORD, SIBLING, PARENT = "CAP-45.a", "CAP-45.b", "CAP-45"


@pytest.fixture(scope="module")
def contract():
    text = read_doc(CONTRACT_YAML)
    caps = {c["id"]: c for c in load_yaml_text(text)["capabilities"]}
    return yaml_model(text), caps


def test_cap_45a_record_carries_contract_v4_2_item_text(contract):
    """DEC-750 item 5: CAP-45.a.md's title, heading and Item line are v4.2's item, in CAP-45.b.md's form."""
    model, caps = contract
    require_v42(model)
    item = model.by_id().get(RECORD)
    assert item is not None and item.cap == PARENT, f"contract.yaml has no {RECORD} under {PARENT}"
    text = str(item.raw["item"])
    parent_title = caps[PARENT]["title"]

    meta, body = read_record(RECORD)
    sib_meta, sib_body = read_record(SIBLING)
    sib = model.by_id()[SIBLING]

    assert meta.get("id") == RECORD, f"{RECORD}.md: id is {meta.get('id')!r}"
    assert meta.get("title") == text, (
        f"{RECORD}.md: title {meta.get('title')!r} is not contract.yaml's item {text!r} (regenerate from v4.2)"
    )
    assert meta.get("depends_on") == [PARENT], f"{RECORD}.md: depends_on {meta.get('depends_on')!r}"
    assert list(meta) == list(sib_meta), f"{RECORD}.md: frontmatter keys {list(meta)} differ from {SIBLING}.md's"
    for key in ("type", "status", "state_class"):
        assert meta.get(key) == sib_meta.get(key), f"{RECORD}.md: {key} {meta.get(key)!r} differs from {SIBLING}.md's"
    assert re.search(rf"^# {re.escape(RECORD)}: {re.escape(text)}$", body, re.MULTILINE), (
        f"{RECORD}.md: heading is not '# {RECORD}: <contract.yaml's item>'"
    )
    assert re.search(rf"^- \*\*Item:\*\* {re.escape(text)}$", body, re.MULTILINE), (
        f"{RECORD}.md: Item line is not contract.yaml's item"
    )
    assert re.search(rf"^- \*\*Wave:\*\* {item.wave}$", body, re.MULTILINE), f"{RECORD}.md: Wave line is not {item.wave}"
    assert record_shape(body, RECORD, text, PARENT, parent_title) == record_shape(
        sib_body, SIBLING, str(sib.raw["item"]), PARENT, parent_title
    ), f"{RECORD}.md: body does not have the form of {SIBLING}.md"


@pytest.mark.parametrize("cap_id", ["CAP-45", "CAP-45.a"])
def test_cap_45_and_cap_45a_records_state_wave_w3_as_contract_yaml(contract, cap_id):
    """DEC-1093 (1), W2-27-CIT-P §5.3: CAP-45.md and CAP-45.a.md each state `- **Wave:** W3`, once, and that is
    contract.yaml's wave for the id (the records are DERIVED, DEC-614)."""
    # Added-For: DEC-1093 (1) — A (i), the two derived records at W3, matching contract.yaml (the note's §5.3).
    model, caps = contract
    require_v42(model)
    wave = caps["CAP-45"].get("wave") if cap_id == "CAP-45" else model.by_id()[cap_id].wave
    assert str(wave) == "W3", f"contract.yaml has {cap_id} at {wave}, not W3 (DEC-1093 moves it)"
    _, body = read_record(cap_id)
    lines = re.findall(r"^- \*\*Wave:\*\* (\S+)$", body, re.MULTILINE)
    assert lines == ["W3"], f"{cap_id}.md states Wave {lines}, not one W3 as contract.yaml"


def test_every_capability_record_states_the_contracts_status():
    """DEC-750 item 5: every record's frontmatter status is the status both Contract files state (ACCEPTED)."""
    statuses = {source: contract_status(source) for source in ("yaml", "markdown")}
    assert statuses["yaml"] == statuses["markdown"], f"the two Contract files state different statuses: {statuses}"
    expected = statuses["yaml"]
    assert expected == "ACCEPTED", f"the Contract states status {expected!r}, not ACCEPTED (DEC-741)"
    paths = capability_record_paths()
    assert paths, "docs/contract/capabilities/ holds no record"
    wrong = {}
    for path in paths:
        meta, _ = frontmatter(path.read_text(encoding="utf-8"))
        if meta.get("status") != expected:
            wrong[path.stem] = meta.get("status")
    assert not wrong, (
        f"{len(wrong)} of {len(paths)} capability records do not state the Contract's status {expected}: "
        f"e.g. {dict(list(wrong.items())[:5])}"
    )
