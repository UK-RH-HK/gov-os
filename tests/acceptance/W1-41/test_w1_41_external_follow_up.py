"""The follow-up after W1-41, piece 11: finding 9 of W1-41's probe (DEC-552, DEC-569).

- **9a. The external references are read from the commit.** The file the context reads is the one the head
  commit of the checkout holds, not the one in the working tree: a ticket whose paths include the file cannot
  unblock its own mandatory source without a commit. An entry written, or the file created, and not
  committed (staged or not) leaves the id as missing as before; the same change committed makes it an
  external reference. What the working tree does to a committed file (deleted, made defective, an entry
  taken out) changes nothing either.
- **9b. An id of a form the repository itself holds is not accepted in the list**, as a decision of the
  register is refused by its form today (DEC-551, P-12): the file is defective, every ticket's context is
  refused, and the refusal names the file and the id. Refused here: ``ADR-<digits>``, ``CAP-<digits>`` with
  or without an item suffix, ``MR-<digits>``, ``L-<four or more digits>`` and ``W<digits>-<two or more
  digits>``. Left: the form of a ticket id and the kernel's general record id, which outside ids share
  (README, package P-11.1).

Reached through the command ``gov context --json --root <project> <ticket>``. Every case builds its own
project, with its own record store, in its own temporary folder.
"""

from __future__ import annotations

import json

import pytest

import w1_41_support as support

C = support.context_base

EXT = "S0a-G-12"
OTHER = "S0a-G-99"                    # listed from the start, declared by no ticket
TK_EXTERNAL, TK_RECORDS = "TK-F9-EXT", "TK-F9-REC"
TICKETS = {TK_EXTERNAL: [support.CHARTER_ID, EXT], TK_RECORDS: [support.CHARTER_ID, support.ADR_ID]}
REL = support.EXTERNAL_REFERENCES_REL


@pytest.fixture(scope="module")
def api(tmp_path_factory):
    made = C.Api(tmp_path_factory.mktemp("w1-41-follow-up"))
    made.exists()
    made.command_exists()
    return made


def _project(api, tmp_path, references, tickets=TICKETS):
    return support.context_project(api, tmp_path / "quay", tickets, references)


def _answer(api, project, ticket):
    """``(packet, None)`` where the context is built, ``(None, error)`` where it is refused."""
    run = api.command(project, ticket)
    envelope = run.envelope()
    if envelope.get("ok") is True and run.returncode == 0:
        return C.check_packet(envelope["result"]), None
    assert envelope.get("ok") is False and run.returncode != 0, f"neither a packet nor a refusal\n{run.describe()}"
    return None, envelope.get("error") or {}


def _assert_missing(api, project, ticket, missing, why):
    packet, error = _answer(api, project, ticket)
    assert packet is None, f"{why}: the context of {ticket} is built, with " \
                           f"{[item.get('id') for item in packet.get(support.K_EXTERNAL, [])]} as external"
    assert error.get("code") == C.BLOCKED and missing in json.dumps(error), \
        f"{why}: not refused for the missing id {missing}: {error}"


def _assert_external(api, project, ticket, external):
    packet, error = _answer(api, project, ticket)
    assert packet is not None, f"the context of {ticket} is refused: {error}"
    assert [item.get("id") for item in packet.get(support.K_EXTERNAL, [])] == [external], \
        f"{external} is not reported as external: {packet.get(support.K_EXTERNAL)}"
    return packet


def _both():
    return support.references_text([support.reference(OTHER), support.reference(EXT)])


# --------------------------------------------------------------------------
# 9a. The file is read from the head commit of the checkout
# --------------------------------------------------------------------------

@pytest.mark.parametrize("staged", [False, True], ids=["written", "staged"])
@pytest.mark.parametrize("start", ["an entry added", "the file created"])
def test_an_uncommitted_change_of_the_file_does_not_unblock_a_mandatory_source(start, staged, api, tmp_path):
    """The committed project does not list the id the ticket declares. Listing it in the working tree, or in
    the index, leaves the ticket's context refused for the missing id."""
    project = _project(api, tmp_path, [support.reference(OTHER)] if start == "an entry added" else None)
    _assert_missing(api, project, TK_EXTERNAL, EXT, "the fixture is wrong")
    support.write(project, REL, _both())
    if staged:
        C.git(project, "add", "--", REL)

    _assert_missing(api, project, TK_EXTERNAL, EXT, f"{start}, not committed")


@pytest.mark.parametrize("start", ["an entry added", "the file created"])
def test_the_same_change_committed_makes_the_id_an_external_reference(start, api, tmp_path):
    """Green today, and it stays: the commit is what the edit lacked."""
    project = _project(api, tmp_path, [support.reference(OTHER)] if start == "an entry added" else None)
    _assert_missing(api, project, TK_EXTERNAL, EXT, "the fixture is wrong")

    support.set_references(api, project, text=_both())

    _assert_external(api, project, TK_EXTERNAL, EXT)


def _deleted(project):
    (project / REL).unlink()


def _defective(project):
    support.write(project, REL, "references: [unclosed\n  - }\n")


def _an_entry_taken_out(project):
    support.write(project, REL, support.references_text([support.reference(OTHER)]))


@pytest.mark.parametrize("change", [_deleted, _defective, _an_entry_taken_out],
                         ids=["deleted", "made defective", "an entry taken out"])
def test_what_the_working_tree_does_to_the_committed_file_changes_nothing(change, api, tmp_path):
    """The commit lists the id. With the file deleted, broken or shortened in the working tree and not
    committed, the ticket gets the packet it got before, its hash included."""
    project = _project(api, tmp_path, [support.reference(OTHER), support.reference(EXT)])
    before = _assert_external(api, project, TK_EXTERNAL, EXT)
    change(project)

    packet, error = _answer(api, project, TK_EXTERNAL)

    assert packet is not None, f"the working tree's file was read, not the commit's: {error}"
    assert packet == before, "the packet changed with a file that is in no commit"


def test_the_commit_read_is_the_head_of_the_checkout(api, tmp_path):
    """Two commits: the first lists the id, the second takes it out. The head is the second: the id is
    missing, though an earlier commit and the working tree (written again, not committed) both list it."""
    project = _project(api, tmp_path, [support.reference(OTHER), support.reference(EXT)])
    _assert_external(api, project, TK_EXTERNAL, EXT)
    support.set_references(api, project, [support.reference(OTHER)])
    support.write(project, REL, _both())

    _assert_missing(api, project, TK_EXTERNAL, EXT, "listed by an earlier commit and by the working tree")


def test_a_defect_of_the_working_trees_file_alone_blocks_no_ticket(api, tmp_path):
    """The other side of the same reading: a defective file blocks every ticket (DEC-551, P-11) where the
    commit holds it, and not where only the working tree does."""
    project = _project(api, tmp_path, [support.reference(OTHER)])
    before, _ = _answer(api, project, TK_RECORDS)
    _defective(project)

    packet, error = _answer(api, project, TK_RECORDS)

    assert before is not None, "the fixture is wrong: the ticket's context is not built"
    assert packet == before, f"an uncommitted defect of the file changed the context of a ticket: {error}"


# --------------------------------------------------------------------------
# 9b. An id of a form the repository itself holds is not accepted in the list
# --------------------------------------------------------------------------

HELD_BY_THE_REPOSITORY = {
    "a capability": "CAP-13",
    "a capability item": "CAP-13.a",
    "a capability item of two letters": "CAP-38.ab",
    "a must rule": "MR-3",
    "a decision file": "ADR-0002",
    "a lesson": "L-0074",
    "a work-breakdown id": "W1-30",
}
LEFT_TO_THE_LIST = {
    "the form of a ticket id": "ISO-9001",
    "the kernel's general record id": "RFC-2119.b",
    "nearly a capability": "CAPE-13",
    "a capability's prefix inside a longer id": "S0a-CAP-13",
}


@pytest.mark.parametrize("form", list(HELD_BY_THE_REPOSITORY))
def test_a_listed_id_of_a_form_the_repository_holds_is_refused(form, api, tmp_path):
    """The ticket declares the id and the file lists it. The file is defective for it: the refusal names the
    file and the id."""
    listed = HELD_BY_THE_REPOSITORY[form]
    entries = [support.reference(OTHER), support.reference(listed, "docs/contract/contract.yaml",
                                                           "not yet a record of the store")]
    project = _project(api, tmp_path, entries, {**TICKETS, TK_EXTERNAL: [support.CHARTER_ID, listed]})

    packet, error = _answer(api, project, TK_EXTERNAL)

    assert packet is None, f"{listed} ({form}) is accepted as an external reference: " \
                           f"{packet.get(support.K_EXTERNAL)}"
    assert error.get("code") == C.BLOCKED, f"expected {C.BLOCKED!r}: {error}"
    said = json.dumps(error)
    assert REL in said and json.dumps(listed)[1:-1] in said, \
        f"the refusal does not name the file and the id {listed}: {error}"


def test_a_listed_id_of_such_a_form_blocks_a_ticket_that_does_not_declare_it(api, tmp_path):
    """As any defect of the file (DEC-551, P-11): seen at once, by every ticket."""
    entries = [support.reference(OTHER), support.reference("CAP-13")]
    project = _project(api, tmp_path, entries)

    packet, error = _answer(api, project, TK_RECORDS)

    assert packet is None, "a file that lists a capability id as external blocks no other ticket"
    assert error.get("code") == C.BLOCKED and REL in json.dumps(error) and "CAP-13" in json.dumps(error), error


@pytest.mark.parametrize("form", list(LEFT_TO_THE_LIST))
def test_an_id_of_a_form_outside_sources_share_is_still_accepted(form, api, tmp_path):
    """Green today, and it stays: the refusal is by the narrow forms above, not by a prefix and a dash."""
    listed = LEFT_TO_THE_LIST[form]
    entries = [support.reference(OTHER), support.reference(listed)]
    project = _project(api, tmp_path, entries, {**TICKETS, TK_EXTERNAL: [support.CHARTER_ID, listed]})

    _assert_external(api, project, TK_EXTERNAL, listed)
