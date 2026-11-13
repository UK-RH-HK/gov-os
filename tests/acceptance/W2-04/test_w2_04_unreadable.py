"""KPI 5 and the failure line's second half (S5; W2-H034, W2-L088, W2-M215): never a record shown read that was not.

A mandatory input whose file, or whose register span, cannot be read or is missing blocks the context (``BLOCKED``,
naming the id and the file) or is listed as not read (``"read": false``); it is never shown as read with the sha256
of empty content or with 0 tokens. A source whose record is SUPERSEDED, RETIRED or REJECTED blocks, naming the id
and its status.

Red reason, today: a register emptied in the working tree is read as empty bytes, so the decision is shown as read
with the empty hash and 0 tokens. The other cases pass today (rows fixed earlier: W1-24's follow-up, DEC-552,
DEC-568); they hold what the change must keep, now that decisions are read as entries.
"""

from __future__ import annotations

import json
import os

import pytest

import w2_04_support as s

TICKET = "TK-W204-READ"
CITED = "DEC-102"
CAP_ID, CAP_REL = "CAP-15", "docs/contract/capabilities/CAP-15.md"
REGISTER_TEXT = s.register(
    s.entry("DEC-101", "The harbour light", "The harbour light burns all night."),
    s.entry(CITED, "The tide gauge", "The tide gauge is read at dawn."),
    s.entry("DEC-103", "The buoy colours", "Buoys are red to port and green to starboard."),
)


@pytest.fixture()
def harbour(api, tmp_path):
    files = {CAP_REL: s.record(CAP_ID, "capability", "ACCEPTED", "The context packet is compiled and bounded."),
             f".tickets/{TICKET}.md": s.ticket(TICKET, "The reading ticket", [CITED, CAP_ID])}
    project = s.build_project(tmp_path / "repo", files, REGISTER_TEXT)
    api.build(project.root, index=False)
    return project


def _deleted(path):
    path.unlink()
    return lambda: None


def _emptied(path):
    path.write_bytes(b"")
    return lambda: None


def _no_permission(path):
    path.chmod(0)
    if os.access(path, os.R_OK):
        path.chmod(0o644)
        pytest.skip("file permissions do not hold this user")
    return lambda: path.chmod(0o644)


def _never_shown_read_unread(api, project, record_id, rel, own_hash=None):
    """The context of ``TICKET`` blocks naming ``record_id`` and ``rel``, or lists ``record_id`` as not read, or (a
    register entry the store still holds) shows it read with its own ``content_hash``; never the empty hash, never 0
    tokens."""
    answer = api.gov(project.root, TICKET)
    envelope = answer.envelope
    if envelope["ok"] is False:
        error = envelope.get("error") or {}
        assert error.get("code") == s.BLOCKED, f"expected {s.BLOCKED}, got {error.get('code')!r}\n{answer.describe()}"
        assert answer.returncode != 0
        said = json.dumps(error)
        assert record_id in said and rel in said, f"the refusal does not name {record_id} and {rel}: {error}"
        return
    packet = answer.packet
    if s.marked_not_read(packet, record_id):
        shown = [item for item in packet[s.K_MANDATORY] if item.get("id") == record_id and item.get("read") is not False]
        assert not shown, f"{record_id} is marked not read and also shown as read: {shown}"
        return
    item = s.item_of(packet, record_id)
    assert item["sha256"] != s.EMPTY_SHA, f"{record_id} is shown as read with the hash of empty content: {item}"
    assert item.get("tokens", 1) != 0, f"{record_id} is shown as read with 0 tokens: {item}"
    assert own_hash is not None and item["sha256"] == own_hash, \
        f"{record_id}'s {rel} cannot be read, yet it is shown as read with the hash {item['sha256']}"


@pytest.mark.parametrize("change", [_deleted, _no_permission], ids=["deleted", "no permission to read"])
def test_a_mandatory_file_that_cannot_be_read_blocks_or_is_marked_not_read(api, harbour, change):
    restore = change(harbour.root / CAP_REL)
    try:
        _never_shown_read_unread(api, harbour, CAP_ID, CAP_REL)
    finally:
        restore()


@pytest.mark.parametrize("change", [_deleted, _emptied, _no_permission],
                         ids=["deleted", "emptied", "no permission to read"])
def test_a_register_entry_whose_span_cannot_be_read_blocks_or_is_marked_not_read(api, harbour, change):
    """The store holds the entry (loaded from the commit); the register in the working tree is gone, empty or
    unreadable. A context that reads the span from the store shows the entry's own hash; one that reads it from
    the working tree blocks or marks it not read. Red today for "emptied": shown read with the empty hash."""
    own_hash = api.records(harbour.root)[CITED]["content_hash"]
    restore = change(harbour.root / s.REGISTER_REL)
    try:
        _never_shown_read_unread(api, harbour, CITED, s.REGISTER_REL, own_hash)
    finally:
        restore()


NO_LONGER_STANDS = ("SUPERSEDED", "RETIRED", "REJECTED")


@pytest.mark.parametrize("status", NO_LONGER_STANDS)
@pytest.mark.parametrize("form", ("register entry", "decision file"))
def test_a_source_that_no_longer_stands_blocks_naming_its_status(api, tmp_path, status, form):
    """Passes today for each status and form (W1-24's follow-up, DEC-568); held for entries read as their spans."""
    source = "DEC-110"
    if form == "register entry":
        line = f"{status} by DEC-111 · **Basis:** OWNER" if status == "SUPERSEDED" else f"{status} · **Basis:** OWNER"
        register_text = s.register(s.entry(source, "The old gauge rule", "The gauge was read at noon.", line),
                                   s.entry("DEC-111", "The gauge rule", "The gauge is read at dawn.",
                                           f"ACCEPTED · **Basis:** OWNER · **Supersedes:** {source}"))
        files = {}
    else:
        register_text = None
        files = {"docs/adr/dec-110.md": s.record(source, "decision", status, "The gauge was read at noon.")}
    files[f".tickets/{TICKET}.md"] = s.ticket(TICKET, "The reading ticket", [source])
    project = s.build_project(tmp_path / "repo", files, register_text)
    api.build(project.root, index=False)
    assert api.records(project.root)[source]["status"] == status, "the fixture is wrong: the store reads another status"

    answer = api.gov(project.root, TICKET)

    error = answer.error
    assert error is not None, f"a {status} {form} satisfied a mandatory source\n{answer.describe()[:1500]}"
    assert error["code"] == s.BLOCKED and answer.returncode != 0, answer.describe()
    assert source in error["message"] and status.lower() in error["message"].lower(), error["message"]
