"""KPI success 4: decision status and id comparisons follow the schema's grammar, case included [W2-M106, W2-L069].

The rows' expected outcomes: "a non-canonical status is reported as a finding" (W2-M106); "an empty id is
reported as a finding" (W2-L069). Their origin (bootstrap, W1-11's decision checker): "``ACTIVE`` is
case-sensitive; ``status: active`` passes silently"; "``type: decision`` with an empty ``id:`` is followed as
``"None"`` or ``""``, not reported as a decision without id. Only an owner-set ``ACTIVE`` one with a deliberately
empty id passes."

The grammar is the kernel's: ``decision_id`` in ``common.schema.json`` (``^(ADR|DEC)-[0-9]{3,}$``), which the
decision entry's schema (``register-entry.schema.json``, W2-02) and the decision file's (``madr.schema.json``) use.

Readings (README): R6, a canonical status is the status word in capitals as the sources write it (``ACTIVE``,
``ACCEPTED``); a word in lower or mixed case is not canonical. R7, for a register entry whose status word is not
canonical, "reported as a finding" is met by the store's ``invalid`` or by a finding of the decision checker that
names the id; the case holds only that it is reported somewhere public and never passed as the canonical word.
"""

from __future__ import annotations

import pytest

import w2_03_support as support

CONTROL = "docs/adr/ADR-0101.md"


def _register(*entries):
    parts = ["# Decisions\n"]
    for heading, status in entries:
        parts.append(f"{heading}\n- **Status:** {status}\n- **Decision:** A fixture.\n")
    return "\n".join(parts)


# ---- ids outside the grammar: the store

OUT_OF_GRAMMAR = _register(
    ("### DEC-130 — A well-formed id", "ACCEPTED (owner, 2026-10-01)"),
    ("### dec-131 — An id in lower case", "ACCEPTED (owner, 2026-10-01)"),
    ("### Dec-132 — An id in mixed case", "ACCEPTED (owner, 2026-10-01)"),
    ("### DEC-13 — An id of two digits", "ACCEPTED (owner, 2026-10-01)"),
)


def test_a_register_heading_outside_the_id_grammar_is_no_record(api, tmp_path):
    """``dec-131``, ``Dec-132`` and ``DEC-13`` are no decision ids: no record under them, nor under their
    upper-cased or padded forms. ``DEC-130`` beside them is one (the control)."""
    project = support.project_with_register(tmp_path / "project", OUT_OF_GRAMMAR)
    _, records = api.load_and_records(project.root)
    ids = set(support.by_id(records))
    assert "DEC-130" in ids, "the fixture is wrong: the well-formed entry is no record"
    wrong = sorted(ids & {"dec-131", "DEC-131", "Dec-132", "DEC-132", "DEC-13", "DEC-013"})
    assert not wrong, f"headings outside the decision_id grammar made records: {wrong}"


# ---- ids outside the grammar: the citations check

def test_an_id_in_lower_case_does_not_record_the_upper_case_id(tmp_path):
    """A register heading ``### dec-131`` and a decision file whose frontmatter says ``id: dec-133`` (typed a
    decision, otherwise schema-valid) record neither DEC-131 nor DEC-133: a commit citing both is flagged for
    both. DEC-130, a well-formed entry, is not (the control)."""
    files = {"docs/adr/dec-133.md": support.decision_file("dec-133")}
    project = support.project_with_register(tmp_path / "project", OUT_OF_GRAMMAR, files=files)
    commit = project.commit("Change the parser (DEC-130, DEC-131, DEC-133)")
    support.assert_flagged(support.run_citations(project.root), [(commit, "DEC-131"), (commit, "DEC-133")])


# ---- status, case included: the decision checker

def _checked(api, root, files):
    """A project holding ``files`` and the control, all set by the owner; the decision checker's findings."""
    project = support.Project(root)
    project.write("README.md", "# A project\n\nNo frontmatter here.\n")
    project.write(CONTROL, support.decision_file("ADR-0101"))
    for rel, text in files.items():
        project.write(rel, text)
    project.commit("Record the decisions", who=support.OWNER)
    return api.check_decisions(project.root)


def _naming(found, path):
    return [finding for finding in found if path in finding["paths"]]


@pytest.mark.parametrize("status", ["active", "Active"])
def test_a_decision_with_a_non_canonical_status_is_reported(api, tmp_path, status):
    """An owner-set decision file whose status is ``active`` or ``Active``: a finding names it. The owner-set
    ``ACTIVE`` control beside it has none."""
    path = "docs/adr/ADR-0102.md"
    found = _checked(api, tmp_path / "project", {path: support.decision_file("ADR-0102", status=status)})
    assert not _naming(found, CONTROL), \
        f"the fixture is wrong: the owner-set ACTIVE control is flagged:\n{support.show_findings(found)}"
    assert _naming(found, path), \
        f"status {status!r} passes silently: no finding names {path}\n{support.show_findings(found)}"


EMPTY_IDS = {"no-value": "id:", "empty-string": 'id: ""'}


@pytest.mark.parametrize("form", sorted(EMPTY_IDS))
def test_a_decision_with_an_empty_id_is_reported_never_followed_as_none_or_empty(api, tmp_path, form):
    """An owner-set ``ACTIVE`` decision file whose ``id`` is empty: a finding names its path, and no finding, nor
    any record of the store, carries the id ``None`` or ``""``. The control beside it has no finding."""
    path = "docs/adr/no-id.md"
    text = support.frontmatter_file([EMPTY_IDS[form], "type: decision", "status: ACTIVE",
                                     "state_class: AUTHORITATIVE", "title: A decision without an id"])
    found = _checked(api, tmp_path / "project", {path: text})
    assert not _naming(found, CONTROL), \
        f"the fixture is wrong: the owner-set ACTIVE control is flagged:\n{support.show_findings(found)}"
    assert _naming(found, path), \
        f"a decision with an empty id passes silently: no finding names {path}\n{support.show_findings(found)}"
    followed = [finding for finding in found if {"None", ""} & set(finding["ids"])]
    assert not followed, f"the empty id is followed as an id:\n{support.show_findings(followed)}"
    _, records = api.load_and_records(tmp_path / "project")
    assert not [r for r in records if r.get("id") in ("None", "")], "the store holds a record whose id is None or ''"


# ---- status, case included: a register entry

def test_a_register_entry_with_a_non_canonical_status_is_reported_not_passed_as_canonical(api, tmp_path):
    """``- **Status:** accepted (owner, 2026-10-01)``: the store does not hold DEC-140 as ACCEPTED, and the entry
    is reported, by the store's ``invalid`` or by a finding of the decision checker that names DEC-140. DEC-130,
    beside it, is ACCEPTED (the control)."""
    register = _register(("### DEC-130 — A well-formed entry", "ACCEPTED (owner, 2026-10-01)"),
                         ("### DEC-140 — A status in lower case", "accepted (owner, 2026-10-01)"))
    project = support.project_with_register(tmp_path / "project", register)
    summary, records = api.load_and_records(project.root)
    entries = support.register_records(records)
    assert entries.get("DEC-130", {}).get("status") == "ACCEPTED", f"the fixture is wrong: {entries.get('DEC-130')}"
    as_canonical = [r for r in support.by_id(records).get("DEC-140", []) if r.get("status") == "ACCEPTED"]
    assert not as_canonical, f"a lower-case status is passed as the canonical word: {as_canonical}"
    found = api.check_decisions(project.root)
    reported = support.invalid_naming(summary, "DEC-140") + [
        f for f in found if "DEC-140" in f["ids"] or "DEC-140" in str(f.get("message"))]
    assert reported, ("a register entry with the status `accepted` passes silently: neither the store's `invalid` "
                      f"nor a finding names DEC-140\ninvalid: {summary['invalid']}\n{support.show_findings(found)}")
