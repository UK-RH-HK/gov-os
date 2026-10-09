"""The follow-up after W1-41, piece 11: finding 10 of W1-41's probe and the two readings beside it (DEC-552,
DEC-568, DEC-569).

- **Finding 10.** A mandatory source whose record is RETIRED or REJECTED does not satisfy it: the context is
  refused and names the record and its status, as a SUPERSEDED one is treated today. Only a record that
  stands satisfies a mandatory source. "Stands" is DEC-552's finding 6 with DEC-568: a record stands unless
  its status says it no longer does, and the statuses that say so are SUPERSEDED, RETIRED and REJECTED;
  ACTIVE, ACCEPTED, PROPOSED, DRAFT, DEPRECATED and a status the kernel does not know still stand.
- **A mandatory record whose file cannot be read** is a refusal that names the file, not a source presented
  as read with the hash of empty bytes and 0 tokens.
- **A failure of the supplementary lookup** is reported in its own words; "index unavailable" is said only
  where the index is unavailable.

Every case changes its own clone of the suite's fixture. The cases with a lexical index need ``gitleaks``
on PATH, as the suite's other cases of the supplementary context do.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3

import pytest

import w1_24_support as S

RECORD_ID, RECORD_REL = "ADR-W24-STAND", "docs/adr/adr-stand.md"
TICKET = "TK-W24-STAND"
EMPTY_SHA = hashlib.sha256(b"").hexdigest()
INDEX_UNAVAILABLE = "index unavailable"
NO_LONGER_STANDS = ("RETIRED", "REJECTED")
STANDS = ("ACTIVE", "ACCEPTED", "PROPOSED", "DRAFT", "DEPRECATED", "SOMETHING_ELSE")


def _with_a_source(api, repo, status):
    """The fixture with one more decision of ``status`` and a ticket that declares it beside the charter."""
    S.write(repo, RECORD_REL, S.record(RECORD_ID, "decision", status, "Soundings are taken at low water."))
    S.write(repo, f".tickets/{TICKET}.md", S.ticket_file(TICKET, sources=[S.CHARTER_ID, RECORD_ID]))
    S.commit(repo, "a source and its ticket")
    api.build_store(repo)
    return repo


def _refused(api, repo, ticket=TICKET):
    error = api.context_outcome(repo, ticket).error()
    assert error is not None, f"the context of {ticket} was built"
    assert error["code"] == S.BLOCKED, f"expected {S.BLOCKED!r}, got {error['code']!r}: {error['message']}"
    return error


# ---- finding 10

@pytest.mark.parametrize("status", NO_LONGER_STANDS)
def test_a_source_that_no_longer_stands_does_not_satisfy_and_is_named_with_its_status(status, api, repo):
    _with_a_source(api, repo, status)

    outcome = api.context_outcome(repo, TICKET)

    assert outcome.error() is not None, f"a {status} record satisfied a mandatory source: the context was built"
    error = _refused(api, repo)
    assert RECORD_ID in error["message"], f"the refusal does not name the record: {error['message']}"
    assert status in error["message"], f"the refusal does not name the record's status: {error['message']}"


def test_a_superseded_source_is_refused_and_named_with_its_status_as_today(api, repo):
    """Green today in its refusal and its record; the status word is held in the form the two above take."""
    _with_a_source(api, repo, "SUPERSEDED")

    error = _refused(api, repo)

    assert RECORD_ID in error["message"] and "superseded" in error["message"].lower(), error["message"]


@pytest.mark.parametrize("status", STANDS)
def test_a_source_that_stands_satisfies(status, api, repo):
    """Green today, and it stays: only the three statuses of DEC-568 say that a record no longer stands."""
    _with_a_source(api, repo, status)

    packet = api.context(repo, TICKET)

    S.check_packet(packet)
    (item,) = [item for item in packet[S.K_MANDATORY] if item[S.M_ID] == RECORD_ID]
    assert item[S.M_LIFECYCLE] == status


# ---- a mandatory record whose file cannot be read

def _deleted(path):
    path.unlink()
    return lambda: None


def _a_folder(path):
    path.unlink()
    path.mkdir()
    return lambda: None


def _no_permission(path):
    path.chmod(0)
    if os.access(path, os.R_OK):
        path.chmod(0o644)
        pytest.skip("file permissions do not hold this user")
    return lambda: path.chmod(0o644)


@pytest.mark.parametrize("change", [_deleted, _a_folder, _no_permission],
                         ids=["deleted", "a folder in its place", "no permission to read"])
def test_a_mandatory_record_whose_file_cannot_be_read_is_refused_and_the_file_is_named(change, api, repo):
    """The store holds the record; its file in the working tree, which the context reads, cannot be read."""
    _with_a_source(api, repo, "ACTIVE")
    restore = change(repo / RECORD_REL)
    try:
        outcome = api.context_outcome(repo, TICKET)
    finally:
        restore()

    if outcome.error() is None:
        (item,) = [item for item in outcome.value()[S.K_MANDATORY] if item[S.M_ID] == RECORD_ID]
        pytest.fail(f"the packet presents {RECORD_ID} as read, with the hash "
                    f"{'of empty bytes' if item[S.M_SHA] == EMPTY_SHA else item[S.M_SHA]}", pytrace=False)
    error = outcome.error()
    assert error["code"] == S.BLOCKED, f"expected {S.BLOCKED!r}, got {error['code']!r}: {error['message']}"
    assert RECORD_REL in error["message"], f"the refusal does not name the file: {error['message']}"
    assert RECORD_ID in json.dumps(error), f"the refusal does not name the record: {error}"


def test_a_mandatory_record_that_is_read_has_the_hash_of_its_file(api, repo):
    """Green today, and it stays."""
    _with_a_source(api, repo, "ACTIVE")

    (item,) = [item for item in api.context(repo, TICKET)[S.K_MANDATORY] if item[S.M_ID] == RECORD_ID]

    assert item[S.M_SHA] == hashlib.sha256((repo / RECORD_REL).read_bytes()).hexdigest() != EMPTY_SHA


# ---- a failure of the supplementary lookup

@pytest.fixture()
def indexed(api, repo):
    """This case's own clone with its store and its lexical index, and the paths the lookup read from."""
    if not api.has_gitleaks():
        pytest.skip("gitleaks is not on PATH")
    api.build_all(repo)
    packet = api.context(repo, S.TK_SUPP)
    read = sorted({item["path"] for item in packet[S.K_SUPPLEMENTARY]})
    assert read and packet[S.K_DROPPED] == [], f"the fixture is wrong: the lookup found nothing: {packet}"
    return repo, read


def _reasons(packet):
    return [str(entry.get(S.M_REASON, "")) for entry in packet[S.K_DROPPED]]


def test_a_lookup_that_fails_on_a_file_it_cannot_read_says_so_and_not_that_the_index_is_unavailable(api, indexed):
    """The index is there and answers. A file it names, which is no mandatory input of the ticket, cannot be
    read: the packet is built, and what it says of the supplementary context names that file."""
    repo, read = indexed
    victim = repo / [rel for rel in read if rel.startswith("docs/adr/")][0]
    victim.chmod(0)
    try:
        if os.access(victim, os.R_OK):
            pytest.skip("file permissions do not hold this user")
        packet = api.context(repo, S.TK_SUPP)
    finally:
        victim.chmod(0o644)

    reasons = _reasons(packet)
    assert packet[S.K_SUPPLEMENTARY] == [] and reasons, \
        f"the fixture is wrong: the lookup did not fail: {packet[S.K_SUPPLEMENTARY]}, {packet[S.K_DROPPED]}"
    assert not any(INDEX_UNAVAILABLE in reason.lower() for reason in reasons), \
        f"a file that cannot be read is reported as an index that is unavailable: {reasons}"
    assert any(str(victim.relative_to(repo)) in reason for reason in reasons), \
        f"the packet does not say which file the lookup could not read: {reasons}"


def test_a_lookup_that_fails_on_a_damaged_index_says_that_the_index_is_unavailable(api, indexed):
    """Green today, and it stays: the index's own table is gone, so the index is what is unavailable."""
    repo, _ = indexed
    connection = sqlite3.connect(repo / ".gov-runtime" / "store.db")
    try:
        connection.execute("DROP TABLE lexical_chunk")
        connection.commit()
    finally:
        connection.close()

    packet = api.context(repo, S.TK_SUPP)

    assert packet[S.K_SUPPLEMENTARY] == []
    assert any(INDEX_UNAVAILABLE in reason.lower() for reason in _reasons(packet)), \
        f"a damaged index is not reported as unavailable: {packet[S.K_DROPPED]}"


def test_the_two_failures_give_two_packets(api, indexed):
    """What the packet says of a failure is part of what is hashed: two causes are not one packet."""
    repo, read = indexed
    victim = repo / [rel for rel in read if rel.startswith("docs/adr/")][0]
    victim.chmod(0)
    try:
        if os.access(victim, os.R_OK):
            pytest.skip("file permissions do not hold this user")
        unread = api.context(repo, S.TK_SUPP)
    finally:
        victim.chmod(0o644)
    connection = sqlite3.connect(repo / ".gov-runtime" / "store.db")
    try:
        connection.execute("DROP TABLE lexical_chunk")
        connection.commit()
    finally:
        connection.close()
    damaged = api.context(repo, S.TK_SUPP)

    assert unread[S.K_DROPPED] != damaged[S.K_DROPPED] and unread[S.K_HASH] != damaged[S.K_HASH], \
        f"a file that cannot be read and a damaged index give the same statement: {unread[S.K_DROPPED]}"
