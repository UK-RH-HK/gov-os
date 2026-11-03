"""KPI 3 (S3; W2-03, AR-1): each decision in the packet is named by its own hash.

A mandatory input that is an entry of the decision register is read as its own span: its ``sha256`` and its
``constraint`` are the entry's own ``content_hash`` (the value ``gov.records.records`` gives for that id), its token
cost is its span's, and editing another entry leaves it unchanged. A mandatory input that is a file of its own keeps
its file's sha256.

Red reason, today: a decision's ``sha256`` is the sha256 of the whole register file and its cost is the register's,
so a ticket citing one short decision of a large register is far over the ceiling (and still ``ok: true``).
"""

from __future__ import annotations

import pytest

import w2_04_support as s

TICKET = "TK-W204-DEC"
CITED, OTHER = "DEC-102", "DEC-104"
CAP_ID, CAP_REL = "CAP-15", "docs/contract/capabilities/CAP-15.md"


def _register(cited_body="The tide gauge is read at dawn.", other_body="The beacon is lit at dusk."):
    entries = [s.entry("DEC-101", "The harbour light", "The harbour light burns all night."),
               s.entry(CITED, "The tide gauge", cited_body),
               s.entry("DEC-103", "The buoy colours", "Buoys are red to port and green to starboard."),
               s.entry(OTHER, "The beacon", other_body),
               s.entry("DEC-105", "The keeper", "A keeper is on watch at every hour.")]
    return s.register(*entries, *s.filler_entries(200, 150, 2000))   # about 300,000 characters


def _files():
    return {CAP_REL: s.record(CAP_ID, "capability", "ACCEPTED", "The context packet is compiled and bounded."),
            f".tickets/{TICKET}.md": s.ticket(TICKET, "The gauge ticket", [CITED, CAP_ID])}


@pytest.fixture(scope="module")
def harbour(api, tmp_path_factory):
    project = s.build_project(tmp_path_factory.mktemp("w2-04-dec") / "repo", _files(), _register())
    api.build(project.root, index=False)
    return project


@pytest.fixture()
def own(api, tmp_path):
    """This case's own project, to change and reload."""
    project = s.build_project(tmp_path / "repo", _files(), _register())
    api.build(project.root, index=False)
    return project


def _entry_hash(api, project, entry_id):
    found = api.records(project.root)[entry_id]
    assert found.get("path") == s.REGISTER_REL and s.sha256_text(found["span"]) == found["content_hash"], \
        f"the fixture is wrong: {entry_id} is no register entry with its own hash: {found}"
    return found


def test_a_decision_is_named_by_its_entrys_own_hash_not_the_registers(api, harbour):
    entry = _entry_hash(api, harbour, CITED)
    item = s.item_of(api.gov(harbour.root, TICKET).packet, CITED)
    register_sha = s.sha256_file(harbour.root / s.REGISTER_REL)
    assert item["sha256"] != register_sha, f"{CITED} is named by the whole register's hash, not its own"
    assert item["sha256"] == entry["content_hash"], \
        f"{CITED}'s sha256 is {item['sha256']}, not its entry's content_hash {entry['content_hash']}"
    assert item.get("constraint") == entry["content_hash"], f"{CITED}'s constraint is {item.get('constraint')!r}"


def test_a_decisions_token_cost_is_its_span_so_one_short_decision_of_a_large_register_fits(api, harbour):
    span = _entry_hash(api, harbour, CITED)["span"]
    texts = [harbour.text(f".tickets/{TICKET}.md"), span, harbour.text(CAP_REL)]
    assert s.tokens(harbour.text(s.REGISTER_REL)) > 10 * s.DEFAULT_CEILING, "the fixture is wrong: a small register"
    answer = api.gov(harbour.root, TICKET)
    assert answer.envelope["ok"] is True, f"one short decision of a large register does not fit\n{answer.describe()}"
    packet = answer.packet
    s.assert_holds_its_ceiling(packet, texts[0])
    low, high = s.tokens("".join(texts)), sum(s.tokens(text) for text in texts)
    assert low <= packet[s.K_TOKENS] <= high, \
        f"tokens is {packet[s.K_TOKENS]}; the ticket, {CITED}'s span and {CAP_ID}'s file are {low} to {high}"


def test_editing_another_entry_leaves_the_decisions_hash_unchanged(api, own):
    before = s.item_of(api.gov(own.root, TICKET).packet, CITED)["sha256"]
    own.write(s.REGISTER_REL, _register(other_body="The beacon is lit at dusk and put out at dawn."))
    own.commit("another entry changes")
    api.load(own.root)

    after = s.item_of(api.gov(own.root, TICKET).packet, CITED)["sha256"]

    assert after == before, f"editing {OTHER} changed {CITED}'s sha256 ({before} -> {after})"
    assert after == _entry_hash(api, own, CITED)["content_hash"]


def test_editing_the_decisions_own_text_changes_its_hash_to_its_new_entry_hash(api, own):
    before = s.item_of(api.gov(own.root, TICKET).packet, CITED)["sha256"]
    own.write(s.REGISTER_REL, _register(cited_body="The tide gauge is read at dawn and at dusk."))
    own.commit("the cited entry changes")
    api.load(own.root)

    after = s.item_of(api.gov(own.root, TICKET).packet, CITED)["sha256"]

    assert after != before, f"editing {CITED}'s own text left its sha256 unchanged"
    assert after == _entry_hash(api, own, CITED)["content_hash"], \
        f"{CITED}'s new sha256 is not its entry's new content_hash"


def test_a_mandatory_input_that_is_a_file_of_its_own_keeps_its_files_sha256(api, harbour):
    """Passes today, and stays."""
    item = s.item_of(api.gov(harbour.root, TICKET).packet, CAP_ID)
    assert item["sha256"] == s.sha256_file(harbour.root / CAP_REL) != s.EMPTY_SHA
