"""KPI success 1: an id or a record title found in a plain question becomes a start id of the record closure."""

from __future__ import annotations

import json

import pytest

import w2_92_support as support

# (what the question names, the question, a text only the named record's evidence holds)
NAMED = [
    ("decision id", f"what does {support.NAMED_DEC} say", support.NAMED_DEC_TEXT),
    ("contract id", f"what does {support.NAMED_CAP} say", support.NAMED_CAP_TEXT),
    ("ticket id", f"what does {support.NAMED_TICKET} say", support.NAMED_TICKET_TEXT),
    ("W2 id", f"what does {support.NAMED_W2} say", support.NAMED_W2_TEXT),
    ("record title", f"what does the {support.TITLED_TITLE} require", support.TITLED_TEXT),
]


@pytest.mark.parametrize("named, question, text", NAMED, ids=[case[0] for case in NAMED])
def test_r1_a_record_named_in_a_plain_question_reaches_the_bundle(asked, named, question, text):
    """No ``--ticket`` and no ``--id``: the named record's evidence is in the bundle (DEC-957, DEC-954 Q9c)."""
    bundle, _ = asked("full", question)
    assert support.holds_text(bundle, text), (
        f"the question names a record by its {named} and the record's evidence ({text!r}) is not in the bundle; "
        f"the bundle holds {support.paths(bundle)}")


def test_r2_at_radius_1_the_named_records_near_records_join(asked):
    """At radius 1 the closure of the named record joins: the requirement that implements CAP-77 is near it."""
    bundle, _ = asked("full", f"what does {support.NAMED_CAP} say", radius=1)
    assert support.holds_text(bundle, support.NAMED_CAP_TEXT), \
        f"the named record is not in the bundle: {support.paths(bundle)}"
    assert support.holds_text(bundle, support.NEAR_TEXT), (
        f"at radius 1 the record near {support.NAMED_CAP} ({support.NEAR}, which implements it) is not in the "
        f"bundle: {support.paths(bundle)}")


def test_r3_an_id_in_the_question_and_with_id_is_one_start_id(asked):
    """The same id given both ways: the record's evidence is there once, never twice."""
    bundle, _ = asked("full", f"what does {support.NAMED_DEC} say", ids=[support.NAMED_DEC])
    assert support.holds_text(bundle, support.NAMED_DEC_TEXT), \
        f"the named record is not in the bundle: {support.paths(bundle)}"
    chunk_ids = [item.get("chunk_id") for item in bundle["evidence"]]
    spans = [(item["path"], item.get("start_line"), item.get("end_line")) for item in bundle["evidence"]]
    assert len(chunk_ids) == len(set(chunk_ids)) and len(spans) == len(set(spans)), \
        f"an item is in the bundle twice: {support.items(bundle)}"


def test_r4_the_command_takes_the_record_route_of_a_plain_question(api, planted):
    """``gov retrieve --json`` with a plain question that names a decision, and no ``--id``."""
    done, _ = api.command(planted("full"), f"what does {support.NAMED_DEC} say")
    assert done.returncode == 0, f"gov retrieve failed (exit code {done.returncode}):\n{done.stderr[-2000:]}"
    envelope = json.loads(done.stdout)
    assert envelope.get("ok") is True, envelope
    assert support.holds_text(envelope["result"], support.NAMED_DEC_TEXT), (
        f"the command's bundle does not hold {support.NAMED_DEC}'s evidence: {support.paths(envelope['result'])}")
