"""KPI 5, addendum 3's S5 (F1; row W2-H034; DEC-136, DEC-1025 item 1): an emptied mandatory file is never shown read.

The store is built from ``HEAD``, then a truncating write leaves a mandatory file in the working tree empty or
holding only whitespace. The file no longer holds the record the store lists for it. This covers two inputs: a file
of its own (a capability) the ticket cites, and a dependency ticket named in its ``deps``. Either the context is
``BLOCKED`` (``ok: false``, a non-zero exit, the message or ``details`` naming the id and the file), or the input is
listed with ``"read": false``. It is never shown as read: never with the sha256 of empty content or of its
whitespace, never with 0 tokens or the whitespace's own count as if read, never in an ``ok: true`` packet that lists
it as read. The same holds with ``--brief`` (the summary never lists it as present and read) and with ``--dry-run``.

Each case accepts either allowed outcome, as the S5 cases beside it do, and asserts the forbidden ones hard. The
premise (a fixture assertion): before the write, the store lists both inputs at their files, and the context shows
each one read with its file's sha256.

Red reason, today (every case): the emptied or whitespace-only file is read as it stands. The context is ``ok: true``
and lists the input with the sha256 of what is left in the file. With ``--brief`` the summary lists it as it lists a
read input (``CAP-15 (capability, ACCEPTED)``).
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import pytest

import w2_04_support as s

TICKET = "TK-W204-EMPTY"
DEP_TICKET = "TK-W204-EMPTYDEP"
CAP_ID, CAP_REL = "CAP-15", "docs/contract/capabilities/CAP-15.md"
CHARTER_REL = "docs/charter/charter.md"
DEP_REL = f".tickets/{DEP_TICKET}.md"
# The kinds of input a truncating write can leave empty (S5, addendum 3): a file of its own, a dependency ticket.
KINDS = {"capability": (CAP_ID, CAP_REL), "dependency ticket": (DEP_TICKET, DEP_REL)}
# What the write leaves in the file: nothing, one newline, mixed whitespace (spaces, tabs, newlines).
FORMS = {"empty": "", "one newline": "\n", "mixed whitespace": "   \n\t\n"}
MODES = {"json": (), "dry run": ("--dry-run",), "brief": ("--brief",), "brief dry run": ("--brief", "--dry-run")}
# How a brief summary says an input was not read (R9): the summary's own word for an external reference is
# "not read" (``CAP-9 (external, not read)``); the field's own form is taken as well.
NOT_READ = re.compile(r"not read|unread|read\W{0,3}false", re.IGNORECASE)


@pytest.fixture(scope="module")
def emptied(api, tmp_path_factory):
    """The ticket cites the charter and the capability and names the dependency in ``deps``; the store is built from
    ``HEAD``. Each case writes one file in the working tree, then puts it back. The charter stays readable, so a
    refusal can only be for the emptied input."""
    files = {CHARTER_REL: s.record(s.CHARTER_ID, "charter", "ACTIVE", s.CHARTER_TEXT),
             CAP_REL: s.record(CAP_ID, "capability", "ACCEPTED", "The context packet is compiled and bounded."),
             DEP_REL: s.ticket(DEP_TICKET, "The dependency of the emptied ticket", [s.CHARTER_ID],
                               kpis=("The dependency's work is done.",)),
             f".tickets/{TICKET}.md": s.ticket(TICKET, "The emptied ticket", [s.CHARTER_ID, CAP_ID],
                                               deps=[DEP_TICKET])}
    project = s.build_project(tmp_path_factory.mktemp("w2-04-emptied") / "repo", files)
    api.build(project.root, index=False)
    held = api.records(project.root)
    for record_id, rel in KINDS.values():
        assert held.get(record_id, {}).get("path") == rel, \
            f"the fixture is wrong: the store does not list {record_id} at {rel}: {held.get(record_id)}"
    healthy = api.gov(project.root, TICKET).packet
    for record_id, rel in KINDS.values():
        assert s.item_of(healthy, record_id)["sha256"] == s.sha256_file(project.root / rel), \
            f"the fixture is wrong: before any write, {record_id} is not read with its file's sha256"
    return project


def _summary_lists_it_read(summary, record_id):
    """The lines of a brief summary that name ``record_id`` and do not say it was not read."""
    return [line for line in str(summary).splitlines() if record_id in line and not NOT_READ.search(line)]


def _naming(value, record_id):
    """Every map anywhere in ``value`` whose ``id`` is ``record_id``."""
    if isinstance(value, dict):
        if value.get("id") == record_id:
            yield value
        for inner in value.values():
            yield from _naming(inner, record_id)
    elif isinstance(value, list):
        for inner in value:
            yield from _naming(inner, record_id)


def _never_with_what_is_left(value, record_id, left, where):
    """No map naming ``record_id`` and not marked ``"read": false`` carries the sha256 of empty content or of what
    is left in the file, or 0 tokens or the token count of what is left (R10)."""
    hashes = {s.sha256_text(left): f"what is left in its file ({left!r})", s.EMPTY_SHA: "empty content"}
    for found in _naming(value, record_id):
        if found.get("read") is False:
            continue
        for key in ("sha256", "constraint"):
            assert found.get(key) not in hashes, (f"{record_id}'s file holds only {left!r}, and {where} shows it "
                                                  f"with the sha256 of {hashes.get(found.get(key))}: {found}")
        if "tokens" in found:
            assert found["tokens"] not in (0, s.tokens(left)), \
                f"{record_id}'s file holds only {left!r}, and {where} shows it with {found['tokens']} tokens: {found}"


def _listed_not_read(packet, record_id, left, where):
    """An ``ok: true`` packet lists ``record_id`` as not read, and its ``mandatory`` list never shows it as read."""
    _never_with_what_is_left(packet, record_id, left, where)
    shown = [item for item in packet.get(s.K_MANDATORY) or [] if isinstance(item, dict)
             and item.get("id") == record_id and item.get("read") is not False]
    assert not shown, (f"{record_id}'s file holds only {left!r}, yet {where} shows it as read "
                       f"(sha256, tokens): {shown}")
    assert s.marked_not_read(packet, record_id), (
        f"{record_id}'s file holds only {left!r}; {where} neither blocks nor lists it with \"read\": false: "
        f"{packet.get(s.K_MANDATORY)}")


def _never_shown_read(project, answer, record_id, rel, left, brief):
    envelope = answer.envelope
    if envelope["ok"] is False:
        error = envelope.get("error") or {}
        assert error.get("code") == s.BLOCKED, f"expected {s.BLOCKED}, got {error.get('code')!r}\n{answer.describe()}"
        assert answer.returncode != 0, f"the refusal exits 0\n{answer.describe()}"
        said = json.dumps(error)
        assert record_id in said and rel in said, \
            f"the refusal does not name {record_id} and its file {rel} (message or details): {error}"
        return
    assert answer.returncode == 0, f"ok: true with a non-zero exit\n{answer.describe()}"
    result = envelope.get("result")
    if not brief:
        _listed_not_read(answer.packet, record_id, left, "the packet")
        return
    assert isinstance(result, dict), f"the brief's result is not a map\n{answer.describe()}"
    _never_with_what_is_left(result, record_id, left, "the brief's result")
    listed = _summary_lists_it_read(result.get("summary", ""), record_id)
    assert not listed, (f"{record_id}'s file holds only {left!r}, yet the brief summary lists it as present and "
                        f"read: {listed}")
    written = result.get("path")
    if written:
        path = Path(written) if Path(written).is_absolute() else project.root / written
        if path.is_file():
            _listed_not_read(json.loads(path.read_text(encoding="utf-8")), record_id, left,
                             f"the brief's packet file {written}")


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("form", FORMS)
@pytest.mark.parametrize("kind", KINDS)
def test_an_emptied_mandatory_file_blocks_or_is_marked_not_read_never_read(api, emptied, kind, form, mode):
    """Addendum 3's S5 (DEC-1025 item 1). The store holds the record, built from ``HEAD``. In the working tree only,
    the file of the capability, or of the dependency ticket, is truncated to ``form``. ``gov context <ticket>
    --json`` (with ``mode``'s flags) either blocks by name or lists the input as not read; never as read."""
    record_id, rel = KINDS[kind]
    path, left = emptied.root / rel, FORMS[form]
    original = path.read_bytes()
    shutil.rmtree(emptied.root / s.SCRATCH_REL, ignore_errors=True)  # no brief file of an earlier case is read
    path.write_bytes(left.encode("utf-8"))
    try:
        answer = api.gov(emptied.root, TICKET, *MODES[mode])
        _never_shown_read(emptied, answer, record_id, rel, left, brief="--brief" in MODES[mode])
    finally:
        path.write_bytes(original)
