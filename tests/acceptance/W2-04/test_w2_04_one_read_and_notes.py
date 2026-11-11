"""Rows W2-L183 and W2-M134 (S9, S10; CAP-15.f): one read of the ticket; synthesis notes validated and acted on.

S9: a context reads the ticket file once; its sources, dependencies, KPI lines, title and text all come from that one
read. Observed from outside the code: the ``watch`` stand-in (README, "The stand-ins") counts, in the process that
runs ``gov context``, every open of the ticket file and every child process that names it. In a project without a
lexical index nothing else reads the ticket file.

S10: when the project holds synthesis notes (``.gov-runtime/synthesis/notes.json``), ``gov context`` runs their
validator; notes that fail it are never presented as valid, and the packet says whether they passed and names the
failure codes. A project with no notes is unchanged (nothing about notes, no ``NOTES_NOT_FOUND``).

Red reasons, today: the ticket file is read three times (its ids, its sources, its title); ``gov context`` does not
call the notes' validator, so the packet says nothing of failing notes. The case without notes passes today.
"""

from __future__ import annotations

import hashlib
import json

import pytest

import w2_04_support as s

TICKET = "TK-W204-ONCE"
NOTES_REL = ".gov-runtime/synthesis/notes.json"
CHARTER_REL = "docs/charter/charter.md"


@pytest.fixture()
def once(api, tmp_path):
    files = {CHARTER_REL: s.record(s.CHARTER_ID, "charter", "ACTIVE", s.CHARTER_TEXT),
             f".tickets/{TICKET}.md": s.ticket(TICKET, "The ticket read once", [s.CHARTER_ID],
                                               kpis=("The ticket file is read once.",))}
    project = s.build_project(tmp_path / "repo", files)
    api.build(project.root, index=False)
    return project


def test_a_context_reads_the_ticket_file_once(api, once):
    answer = api.gov(once.root, TICKET, env=api.env(watch=(once.root, f".tickets/{TICKET}.md")))
    packet = answer.packet
    reads = answer.reads()
    assert len(reads) <= 1, f"the context read the ticket file {len(reads)} times ({reads}); one read gives its " \
                            f"sources, dependencies, KPI lines, title and text"
    assert packet.get(s.K_TICKET_TEXT) == once.text(f".tickets/{TICKET}.md"), \
        "the packet's ticket text is not the ticket file's text"


def _notes(once, *, broken):
    """Notes as W1-23's synthesis writes them, citing the charter's lines 1 to 3; ``broken`` cites a wrong hash."""
    text = (once.root / CHARTER_REL).read_bytes()
    lines = text.splitlines(keepends=True)
    span = b"".join(lines[0:3])
    citation = {"source_id": s.CHARTER_ID, "path": CHARTER_REL, "start_line": 1, "end_line": 3,
                "source_sha256": "0" * 64 if broken else hashlib.sha256(span).hexdigest(),
                "file_sha256": hashlib.sha256(text).hexdigest()}
    notes = {"notes": [{"group": "docs/charter", "citations": [citation]}], "unresolved": []}
    path = once.root / NOTES_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(notes, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _says_valid(value):
    if isinstance(value, dict):
        return value.get("valid") is True or any(_says_valid(inner) for inner in value.values())
    if isinstance(value, list):
        return any(_says_valid(inner) for inner in value)
    return False


def test_notes_that_fail_their_validator_are_reported_as_failing_never_as_valid(api, once):
    _notes(once, broken=True)
    (check,) = api.batch([("gov.retrieval.synthesis", "validate_notes", once.root, (), {})])
    assert check.get("value", {}).get("valid") is False and \
        "HASH_MISMATCH" in json.dumps(check["value"]), f"the fixture is wrong: the notes pass: {check}"

    packet = api.gov(once.root, TICKET).packet

    said = json.dumps(packet)
    assert "HASH_MISMATCH" in said, "the packet does not name the notes' failure code (HASH_MISMATCH)"
    assert not _says_valid(packet), "the packet presents notes that fail their validator as valid"


def test_a_project_with_no_notes_is_unchanged(api, once):
    """Passes today: nothing about notes, no failure code for notes that do not exist."""
    packet = api.gov(once.root, TICKET).packet
    assert "NOTES_NOT_FOUND" not in json.dumps(packet), "a project with no notes is reported as missing them"
