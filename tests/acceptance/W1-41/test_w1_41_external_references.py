"""Success line 9: the context and the sources that live outside the repository [CAP-15.c; DEC-511, DEC-520].

A ticket declares the ids of its sources. Some of them live outside the repository and will never be records of
the store. The project lists those in ``governance/project/external-references.yaml``; the context accepts a
listed id and reports it as external, never as content. Everything else stays as W1-24 built it: an id that is
neither a record nor listed blocks the context, the list never hides a record, and a file that cannot be read as
what the README states blocks instead of being taken for an empty list (DEC-449, DEC-454).

Reached through the public interface only: the command ``gov context --json --root <project> <ticket>`` for the
main rows, the function ``gov.context.context(root, ticket, ...)`` for a few. Every case builds its own project,
with its own record store, in its own temporary folder. The file's shape and the packet's addition are in
``README.md`` ("Success 9"). No case runs ``gov close``.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

import w1_41_support as support

C = support.context_base

EXT, EXT_LOCATION = "S0a-G-12", "the owner's archive of source documents: sources/S0a/G-12.md"
EXT_REASON = "a planning source the owner keeps outside this repository"
EXT_2, EXT_2_LOCATION = "G-10", "https://example.invalid/library/G-10"
UNUSED = "S0a-G-99"                      # listed, declared by no ticket
GONE = "GONE-H9-404"                     # neither a record nor listed
REGISTER_DECISION = "DEC-086"            # the register's form (DEC-473): DEC-<digits>
REGISTER_TEXT = ("# Decision register\n\n"
                 f"### {REGISTER_DECISION} — Tide tables are published on Mondays\n"
                 "- **Status:** ACCEPTED\n- **Decision:** Mondays.\n")

TK_RECORDS, TK_EXTERNAL, TK_TWO, TK_GONE, TK_BOTH, TK_OLD, TK_REGISTER = (
    "TK-H9-REC", "TK-H9-EXT", "TK-H9-TWO", "TK-H9-GONE", "TK-H9-BOTH", "TK-H9-OLD", "TK-H9-REG")
TICKETS = {
    TK_RECORDS: [support.CHARTER_ID, support.ADR_ID],
    TK_EXTERNAL: [support.CHARTER_ID, EXT, support.ADR_ID],
    TK_TWO: [support.CHARTER_ID, EXT, support.ADR_ID, EXT_2],
    TK_GONE: [support.CHARTER_ID, GONE],
    TK_BOTH: [support.CHARTER_ID, EXT, GONE],
    TK_OLD: [support.CHARTER_ID, support.OLD_ADR_ID],
    TK_REGISTER: [support.CHARTER_ID, REGISTER_DECISION],
}


def _listed():
    """The file of the ordinary project. The order is not the order any ticket declares the ids in."""
    return [support.reference(UNUSED),
            support.reference(EXT_2, EXT_2_LOCATION),
            support.reference(EXT, EXT_LOCATION, EXT_REASON)]


@pytest.fixture(scope="module")
def api(tmp_path_factory):
    """The context's function and command, each call in a new process with this worktree's code."""
    made = C.Api(tmp_path_factory.mktemp("w1-41-context"))
    made.exists()
    made.command_exists()
    return made


@pytest.fixture()
def quay(api, tmp_path):
    """Builds this case's project: ``quay()`` lists the ordinary entries, ``quay(references=None)`` has no file."""
    def build(references=_listed, text=None, register=None, name="quay"):
        entries = references() if callable(references) else references
        return support.context_project(api, tmp_path / name, TICKETS, entries, text, register)
    return build


def _packet(api, project, ticket, *args):
    """The packet the command prints for ``ticket``; an assertion error where the context is refused."""
    run = api.command(project, *args, ticket)
    envelope = run.envelope()
    assert run.returncode == 0 and envelope.get("ok") is True, \
        f"the context of {ticket} is not built\n{run.describe()}"
    return C.check_packet(envelope["result"])


def _blocked(api, project, ticket, *names):
    """The command refuses the context of ``ticket`` with BLOCKED, and its error names every one of ``names``."""
    run = api.command(project, ticket)
    envelope = run.envelope()
    assert envelope.get("ok") is False and run.returncode != 0, \
        f"the context of {ticket} was built; expected {C.BLOCKED}\n{run.describe()}"
    error = envelope.get("error") or {}
    assert error.get("code") == C.BLOCKED, f"expected {C.BLOCKED!r}, got {error.get('code')!r}\n{run.describe()}"
    said = json.dumps(error)
    for name in names:
        assert name in said, f"the error does not name {name!r}\n{run.describe()}"
    return error


def _blocked_by_the_function(api, project, ticket, *names):
    error = api.context_outcome(project, ticket).error()
    assert error is not None, f"the context of {ticket} was built; expected {C.BLOCKED}"
    assert error["code"] == C.BLOCKED, f"expected {C.BLOCKED!r}, got {error['code']!r}: {error['message']}"
    for name in names:
        assert name in error["message"], f"the error's message does not name {name!r}: {error['message']}"
    return error


def _external(packet):
    listed = packet.get(support.K_EXTERNAL)
    assert isinstance(listed, list) and all(isinstance(item, dict) for item in listed), \
        f"the packet has no list `{support.K_EXTERNAL}` of its external references: {listed!r}"
    return listed


def _ids(items):
    return [item.get(C.M_ID) for item in items]


# --------------------------------------------------------------------------
# A listed id is accepted and reported as external, never as content
# --------------------------------------------------------------------------

def test_the_context_of_a_ticket_that_declares_a_listed_id_is_built(api, quay):
    """The other declared ids are records: they are the packet's mandatory inputs, as for any ticket."""
    packet = _packet(api, quay(), TK_EXTERNAL)
    assert sorted(_ids(packet[C.K_MANDATORY])) == sorted([support.CHARTER_ID, support.ADR_ID])


def test_the_packet_reports_each_listed_id_as_external_with_where_it_lives(api, quay):
    """Under a key of its own: the id, where it lives and why it is not in the store, as the file states them, and
    that it was not read. In the order the ticket declares them; an entry no ticket id names is not reported."""
    external = _external(_packet(api, quay(), TK_TWO))
    assert _ids(external) == [EXT, EXT_2], f"the external references of {TK_TWO}: {external}"
    first, second = external
    assert first.get(support.F_LOCATION) == EXT_LOCATION and second.get(support.F_LOCATION) == EXT_2_LOCATION, \
        f"an external reference does not say where it lives, as the file states it: {external}"
    assert first.get(support.F_REASON) == EXT_REASON, f"{EXT}: the file's reason is not reported: {first}"
    for item in external:
        assert item.get(support.X_READ) is False, \
            f"{item.get(C.M_ID)}: the packet does not say that this source was not read: {item}"


def test_an_external_reference_is_not_among_the_items_read_as_records(api, quay):
    """It has no content hash, no authority tier and no lifecycle, and it stands in none of the blocks whose
    items have them."""
    packet = _packet(api, quay(), TK_EXTERNAL)
    for block in (C.K_MANDATORY, C.K_AUTHORITY, C.K_SUPPLEMENTARY):
        assert EXT not in _ids(packet[block]), f"{EXT} stands in `{block}` as if it had been read"
    (item,) = [item for item in _external(packet) if item.get(C.M_ID) == EXT]
    as_content = sorted(key for key in support.RECORD_ONLY_KEYS if key in item)
    assert not as_content, f"{EXT} is reported with {as_content}, as if a record had been read: {item}"


def test_an_external_reference_adds_nothing_to_the_packets_tokens(api, quay):
    """The ticket's twin declares the same records and no external reference: both packets count the same."""
    project = quay()
    with_it, without = _packet(api, project, TK_EXTERNAL), _packet(api, project, TK_RECORDS)
    assert EXT in _ids(_external(with_it))
    assert with_it[C.K_TOKENS] == without[C.K_TOKENS], \
        f"the external reference counts as read content: {with_it[C.K_TOKENS]} tokens, {without[C.K_TOKENS]} without"
    assert with_it[C.K_BUDGET] == without[C.K_BUDGET], \
        f"the external reference changes the budget: {with_it[C.K_BUDGET]}, {without[C.K_BUDGET]} without it"


def test_the_function_reports_the_same_external_reference(api, quay):
    project = quay()
    packet = C.check_packet(api.context(project, TK_EXTERNAL))
    assert _external(packet) == _external(_packet(api, project, TK_EXTERNAL))
    assert _ids(_external(packet)) == [EXT] and _external(packet)[0].get(support.X_READ) is False


def test_the_brief_says_that_the_external_source_was_not_read(api, quay):
    """The summary a reader of ``--brief`` sees names the id and says it was not read; the file it points to is
    the packet, with the same key."""
    result = api.context(quay(), TK_EXTERNAL, brief=True)
    lines = [line for line in result["summary"].splitlines() if EXT in line]
    assert lines, f"the summary does not name {EXT}:\n{result['summary']}"
    assert any("not read" in line.lower() for line in lines), \
        f"the summary names {EXT} without saying that it was not read:\n{result['summary']}"
    written = json.loads(Path(result["path"]).read_text(encoding="utf-8"))
    assert _ids(_external(written)) == [EXT], f"the brief file does not report {EXT} as external"


def test_the_same_project_gives_the_same_hash_twice(api, quay):
    project = quay()
    first, second = _packet(api, project, TK_EXTERNAL), _packet(api, project, TK_EXTERNAL)
    assert first[C.K_HASH] == second[C.K_HASH]
    assert first == second, "two runs on the same project gave two packets"


@pytest.mark.parametrize("key,value", [
    (support.F_LOCATION, "the owner's archive, moved: vault/S0a/G-12.md"),
    (support.F_REASON, "superseded outside this repository; kept for history"),
])
def test_a_change_of_the_listed_entry_changes_the_packets_hash(api, quay, key, value):
    """The hash proves what the worker received (CAP-15.e): where the source lives and why it was not read are
    part of that."""
    project = quay()
    before = _packet(api, project, TK_EXTERNAL)
    entries = [dict(item, **{key: value}) if item[support.F_ID] == EXT else item for item in _listed()]
    support.set_references(api, project, entries)
    after = _packet(api, project, TK_EXTERNAL)
    assert after[C.K_MANDATORY] == before[C.K_MANDATORY], "the case changed more than the listed entry"
    assert after[C.K_HASH] != before[C.K_HASH], f"the packet's hash does not cover the entry's `{key}`"


# --------------------------------------------------------------------------
# An id that is neither a record nor listed blocks as before
# --------------------------------------------------------------------------

def test_an_id_that_is_neither_a_record_nor_listed_stays_blocked(api, quay):
    """Green before the file is read at all, and it stays green."""
    _blocked_by_the_function(api, quay(), TK_GONE, GONE)


def test_an_unlisted_id_blocks_a_ticket_that_also_declares_a_listed_one(api, quay):
    """Accepting the listed id does not accept the one after it: the error names the id that is not listed."""
    _blocked(api, quay(), TK_BOTH, GONE)


# --------------------------------------------------------------------------
# The list never hides a record
# --------------------------------------------------------------------------

def test_a_listed_id_that_is_a_record_is_the_stores_record(api, quay):
    """It stands among the mandatory inputs with its content hash, and it is not reported as external; the id
    beside it, which is no record, is."""
    project = quay(references=_listed() + [support.reference(support.CHARTER_ID)])
    packet = _packet(api, project, TK_EXTERNAL)
    (charter,) = [item for item in packet[C.K_MANDATORY] if item[C.M_ID] == support.CHARTER_ID]
    assert charter[C.M_SHA] == hashlib.sha256((project / support.CHARTER_REL).read_bytes()).hexdigest()
    assert _ids(_external(packet)) == [EXT], \
        f"a record of the store is reported as external, or the external one is not: {_external(packet)}"


def test_a_listed_id_that_is_a_superseded_record_still_blocks(api, quay):
    """Listing a superseded record does not make it satisfy a requirement. Green before the file is read."""
    project = quay(references=_listed() + [support.reference(support.OLD_ADR_ID)])
    _blocked(api, project, TK_OLD, support.OLD_ADR_ID)


# --------------------------------------------------------------------------
# Nothing fails open: a file that is there and is not what the README states
# --------------------------------------------------------------------------

def _entries(*entries):
    return support.references_text(entries)


NOT_OF_THE_SHAPE = {
    "not valid YAML": "references: [unclosed\n  - }\n",
    "an empty file": "",
    "a list, not a mapping": f"- id: {EXT}\n  location: elsewhere\n  reason: kept\n",
    "a mapping without `references`": "sources: []\n",
    "`references` is a mapping, not a list": f"references:\n  {EXT}:\n    location: elsewhere\n    reason: kept\n",
    "an entry that is not a mapping": f"references:\n  - {EXT}\n",
    "an entry without an id": _entries({support.F_LOCATION: "elsewhere", support.F_REASON: "kept"}),
    "an entry without where it lives": _entries(support.reference(EXT, location=None)),
    "an entry without its reason": _entries(support.reference(EXT, reason=None)),
    "an empty location": _entries(support.reference(EXT, location="  ")),
    "a reason that is not text": _entries(support.reference(EXT, reason=["kept"])),
    "an id listed twice": _entries(support.reference(EXT), support.reference(EXT)),
    "another entry is broken": _entries(support.reference(EXT), support.reference(UNUSED, location=None)),
}


@pytest.mark.parametrize("text", list(NOT_OF_THE_SHAPE.values()), ids=list(NOT_OF_THE_SHAPE))
def test_a_file_that_is_not_of_the_stated_shape_blocks_and_is_named(api, quay, text):
    """The ticket declares an id that is no record. Before the file is read this is blocked as a missing id, and
    the file is not named: a file that is ignored is not a file that was found defective."""
    _blocked(api, quay(text=text), TK_EXTERNAL, support.EXTERNAL_REFERENCES_REL)


def test_a_file_that_cannot_be_read_blocks_and_is_named(api, quay, tmp_path):
    if not support.can_be_made_unreadable(tmp_path):
        pytest.skip("file permissions do not hold this user")
    project = quay()
    restore = support.make_unreadable(project / support.EXTERNAL_REFERENCES_REL)
    try:
        _blocked(api, project, TK_EXTERNAL, support.EXTERNAL_REFERENCES_REL)
    finally:
        restore()


def test_the_function_names_the_defective_file_in_its_message(api, quay):
    project = quay(text=NOT_OF_THE_SHAPE["an entry without where it lives"])
    _blocked_by_the_function(api, project, TK_EXTERNAL, support.EXTERNAL_REFERENCES_REL)


@pytest.mark.parametrize("shape", ["not valid YAML", "an entry without its reason"])
def test_a_defective_file_blocks_a_ticket_whose_ids_are_all_records_too(api, quay, shape):
    """The stricter reading (README, package P-11): a defective governance file is never passed over because
    this ticket happens not to need it. Without the file the same ticket's context is built."""
    project = quay(text=NOT_OF_THE_SHAPE[shape])
    _blocked(api, project, TK_RECORDS, support.EXTERNAL_REFERENCES_REL)


# --------------------------------------------------------------------------
# A project without the file behaves as before
# --------------------------------------------------------------------------

def test_a_project_without_the_file_gives_the_packet_it_gave_before(api, quay):
    """The eight keys of W1-24's packet and no other: the key of the external references is absent where the
    ticket declares none. Green before and after."""
    project = quay(references=None)
    assert not (project / support.EXTERNAL_REFERENCES_REL).exists()
    packet = _packet(api, project, TK_RECORDS)
    assert sorted(packet) == sorted(support.PACKET_KEYS), f"the packet's keys changed: {sorted(packet)}"
    assert sorted(_ids(packet[C.K_MANDATORY])) == sorted([support.CHARTER_ID, support.ADR_ID])


def test_a_missing_id_blocks_in_a_project_without_the_file(api, quay):
    """Green before and after; the id that would be listed elsewhere is as missing here as any other."""
    project = quay(references=None)
    _blocked_by_the_function(api, project, TK_GONE, GONE)
    _blocked(api, project, TK_EXTERNAL, EXT)


@pytest.mark.parametrize("references", [[], _listed()], ids=["lists nothing", "lists other ids"])
def test_a_file_the_ticket_names_nothing_of_leaves_its_packet_as_it_was(api, quay, references):
    """Held against the whole packet, its hash included: what the same ticket got in the same project before the
    file was there. Green before and after."""
    project = quay(references=None)
    before = _packet(api, project, TK_RECORDS)
    support.set_references(api, project, references)
    after = _packet(api, project, TK_RECORDS)
    assert after == before, "a file that lists nothing this ticket declares changed its packet"


# --------------------------------------------------------------------------
# A register decision is not an external reference (DEC-519, DEC-521)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("register", [REGISTER_TEXT, None], ids=["in the named register", "by its form alone"])
def test_a_listed_id_of_the_decision_registers_form_is_refused(api, quay, register):
    """A decision lives in the repository: in a decision file or in the register (DEC-473). Until the store loads
    register decisions as records it stays blocked, and listing it as external is a defect of the file: the error
    names the file and the id. Before the file is read the id is blocked as missing and the file is not named."""
    entries = _listed() + [support.reference(REGISTER_DECISION, "docs/decision-register.md",
                                             "not yet a record of the store")]
    project = quay(references=entries, register=register)
    _blocked(api, project, TK_REGISTER, support.EXTERNAL_REFERENCES_REL, REGISTER_DECISION)
