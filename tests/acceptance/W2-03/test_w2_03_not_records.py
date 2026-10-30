"""KPI success 3: a register heading alone, or any Markdown file with a decision id in its frontmatter, is not a
decision record [W2-L221, W2-M267, W2-M145]. With KPI success 2: the citations check resolves a cited id as the
store does [AR-1].

The rows' expected outcomes: "a register entry needs a heading and a status line to count" (W2-L221); "only a
schema-valid decision record satisfies a citation" (W2-M267); "only decision files in the declared folders and
live register entries count" (W2-M145). Their origin (bootstrap, W1-26's residuals): "any Markdown file in the
tree whose frontmatter carries a decision id counts as its record, wherever it lies; a register heading counts
whatever the entry's status or body says (a heading inside an HTML comment too)".

Readings (README): R3, a heading is "alone" when no status line follows it (the status line is the one W1-10's
store reads: ``- **Status:** WORD`` as the entry's first line that is not blank); R4, a heading inside an HTML
comment is no live entry; R5, "schema-valid" is the kernel's schema of the ``decision`` type
(``madr.schema.json``: ``id`` in the ``decision_id`` grammar, ``type: decision``, ``status``, ``state_class``).
Which folders are "declared" is not settled by any source (package P-3) and no case here depends on it: every
decision file lies in ``docs/adr/``.
"""

from __future__ import annotations

import pytest

import w2_03_support as support

ASSORTED = """\
# Decisions

### DEC-101 — A recorded decision
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER
- **Decision:** The parser reads both forms.

### DEC-102 — A heading alone

### DEC-103 — A heading over a body without a status line
- **Decision:** No status line under this heading.

<!--
### DEC-104 — A heading inside an HTML comment
- **Status:** ACCEPTED (owner, 2026-10-01)
-->

### DEC-105 — Another recorded decision
- **Status:** PROPOSED · **Basis:** a report
- **Decision:** The writer keeps its order.
"""

LIVE = ["DEC-101", "DEC-105"]
HEADING_ALONE = ["DEC-102", "DEC-103"]
IN_A_COMMENT = "DEC-104"
CITED = ["DEC-101", "DEC-102", "DEC-103", "DEC-104", "DEC-105"]


@pytest.fixture(scope="module")
def assorted(api, tmp_path_factory):
    project = support.project_with_register(tmp_path_factory.mktemp("w2-03-assorted") / "project", ASSORTED)
    summary, records = api.load_and_records(project.root)
    return project, summary, records


# ---- the store

@pytest.mark.parametrize("record_id", HEADING_ALONE)
def test_a_heading_alone_is_no_record_of_the_store(assorted, record_id):
    """No status line under the heading: no record, and ``invalid`` names the register with the id (as W1-10's
    store already does for an entry without a readable status)."""
    _, summary, records = assorted
    assert record_id not in support.by_id(records), f"the heading of {record_id} alone made a record"
    assert support.invalid_naming(summary, record_id, path=support.REGISTER_REL), \
        f"`invalid` does not name {record_id} in the register: {summary['invalid']}"


def test_a_heading_inside_an_html_comment_is_no_record_of_the_store(assorted):
    """Reading R4: a heading and its status line inside ``<!-- ... -->`` are no live entry."""
    _, _, records = assorted
    assert IN_A_COMMENT not in support.by_id(records), "a heading inside an HTML comment made a record"
    assert sorted(support.register_records(records)) == LIVE, \
        f"the register's records are {sorted(support.register_records(records))}, not {LIVE}"


@pytest.mark.parametrize("form", ["no-type", "another-type"])
def test_a_file_with_a_decision_id_in_its_frontmatter_is_not_loaded_as_that_decision(api, tmp_path, form):
    """A note whose frontmatter carries ``id: DEC-110`` (without a type, or with ``type: note``) beside a register
    that does not record DEC-110: the store holds no decision record of DEC-110."""
    lines = ["id: DEC-110", "status: ACTIVE", "state_class: AUTHORITATIVE", "title: A note"]
    if form == "another-type":
        lines.insert(1, "type: note")
    files = {"docs/notes/a-note.md": support.frontmatter_file(lines)}
    project = support.project_with_register(tmp_path / "project", ASSORTED, files=files)
    _, records = api.load_and_records(project.root)
    as_decision = [r for r in support.by_id(records).get("DEC-110", [])
                   if r.get("type") in ("decision", "register-entry")]
    assert not as_decision, f"a note with a decision id in its frontmatter is loaded as that decision: {as_decision}"


# ---- the decision-citations check

def test_the_check_counts_a_heading_alone_and_a_commented_heading_as_unrecorded(tmp_path):
    """One commit cites the five ids of the register. DEC-101 and DEC-105 are entries with a status line: not
    flagged. DEC-102 and DEC-103 (a heading alone) and DEC-104 (inside an HTML comment) are flagged."""
    project = support.project_with_register(tmp_path / "project", ASSORTED)
    commit = project.commit(f"Change the parser ({', '.join(CITED)})")
    support.assert_flagged(support.run_citations(project.root),
                           [(commit, record_id) for record_id in HEADING_ALONE + [IN_A_COMMENT]])


def test_the_check_and_the_store_count_the_same_entries(api, tmp_path):
    """KPI success 2, "in the same way": the ids the check takes as recorded are the ids the store loads from the
    register, and no others."""
    project = support.project_with_register(tmp_path / "project", ASSORTED)
    project.commit(f"Change the parser ({', '.join(CITED)})")
    flagged = {decision for _, decision in support.run_citations(project.root).flagged}
    _, records = api.load_and_records(project.root)
    recorded_by_the_check = sorted(set(CITED) - flagged)
    loaded_by_the_store = sorted(set(support.register_records(records)) & set(CITED))
    assert recorded_by_the_check == loaded_by_the_store == LIVE, (
        f"the check takes {recorded_by_the_check} as recorded, the store loads {loaded_by_the_store}; "
        f"expected {LIVE} for both")


NOT_A_DECISION_RECORD = {
    # The legacy form W1-26 counts today: an id in the grammar and no type.
    "id-only": ["id: DEC-120", "status: ACTIVE", "state_class: AUTHORITATIVE", "title: A legacy decision"],
    # A record of another type that carries a decision id.
    "another-type": ["id: DEC-120", "type: note", "status: ACTIVE", "state_class: AUTHORITATIVE", "title: A note"],
    # Typed a decision, not valid under the kernel's schema of the type: no state_class.
    "not-schema-valid": ["id: DEC-120", "type: decision", "status: ACTIVE", "title: A decision without a class"],
}


@pytest.mark.parametrize("form", sorted(NOT_A_DECISION_RECORD))
def test_a_file_with_a_decision_id_in_its_frontmatter_does_not_satisfy_a_citation(tmp_path, form):
    """``docs/adr/DEC-120.md`` carries ``id: DEC-120`` in its frontmatter and is no schema-valid decision record:
    a commit citing DEC-120 is flagged. The schema-valid ``docs/adr/DEC-121.md`` in the same tree, cited by the
    same commit, satisfies its citation (the control)."""
    files = {"docs/adr/DEC-120.md": support.frontmatter_file(NOT_A_DECISION_RECORD[form]),
             "docs/adr/DEC-121.md": support.decision_file("DEC-121")}
    project = support.project_with_register(tmp_path / "project", ASSORTED, files=files)
    commit = project.commit("Change the parser (DEC-120, DEC-121)")
    support.assert_flagged(support.run_citations(project.root), [(commit, "DEC-120")])
