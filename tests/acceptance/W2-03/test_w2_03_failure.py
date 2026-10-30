"""KPI failure: an edited entry changes only its own hash; a duplicate DEC id is refused with both locations.

Readings (README): R1 (``content_hash`` and ``span``, as in ``test_w2_03_entry_records.py``); R2, "refused" is
the store's refusal of a record as DEC-274 and W1-10 fix it: the load goes on, no record is made of the id, and
``invalid`` names it. "Both locations" are the places the id is recorded: a register entry by the register's path
and the line number of its heading, a decision file by its path.
"""

from __future__ import annotations

import pytest

import w2_03_support as support

REGISTER = """\
# Decisions

## 1. The first part

### DEC-201 — The first decision
- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER
- **Decision:** The first text.

### DEC-202 — The second decision
- **Status:** PROPOSED · **Basis:** a report
- **Decision:** The second text.

## 2. The second part

### DEC-203 — The third decision
- **Status:** ACCEPTED (owner, 2026-10-02)
- **Decision:** The third text.

### DEC-204 — The fourth decision
- **Status:** ACCEPTED (owner, 2026-10-03)
- **Decision:** The fourth text.
"""
IDS = ["DEC-201", "DEC-202", "DEC-203", "DEC-204"]

EDITS = {
    "the body of a middle entry": ("DEC-202", "- **Decision:** The second text.",
                                   "- **Decision:** The second text, edited."),
    "the status of a middle entry": ("DEC-203", "- **Status:** ACCEPTED (owner, 2026-10-02)",
                                     "- **Status:** SUPERSEDED (owner, 2026-10-09)"),
    "the title of the first entry": ("DEC-201", "### DEC-201 — The first decision",
                                     "### DEC-201 — The first decision, retitled"),
    "the body of the last entry": ("DEC-204", "- **Decision:** The fourth text.",
                                   "- **Decision:** The fourth text, edited."),
}


def _hashes_and_spans(api, root):
    _, records = api.load_and_records(root)
    entries = support.register_records(records)
    assert sorted(entries) == IDS, f"the register's records are {sorted(entries)}"
    for record_id, record in entries.items():
        assert support.is_sha256(record.get(support.HASH_KEY)), \
            f"{record_id}'s record carries no sha256 as `{support.HASH_KEY}`: keys {sorted(record)}"
    return ({record_id: record[support.HASH_KEY] for record_id, record in entries.items()},
            {record_id: record.get(support.SPAN_KEY) for record_id, record in entries.items()})


@pytest.mark.parametrize("edit", sorted(EDITS))
def test_an_edited_entry_changes_only_its_own_hash(api, tmp_path, edit):
    """Load, load again unchanged, edit one entry and commit, load: the edited entry's hash changes, every other
    entry's hash and span stay as they were."""
    edited_id, old, new = EDITS[edit]
    assert REGISTER.count(old) == 1, "the fixture is wrong"
    project = support.project_with_register(tmp_path / "project", REGISTER)
    before, spans_before = _hashes_and_spans(api, project.root)
    again, _ = _hashes_and_spans(api, project.root)
    project.write(support.REGISTER_REL, REGISTER.replace(old, new))
    project.commit(f"Edit {edited_id}", who=support.OWNER)
    after, spans_after = _hashes_and_spans(api, project.root)

    assert again == before, "the same commit gives the entries other hashes"
    assert after[edited_id] != before[edited_id], f"editing {edit} left {edited_id}'s hash as it was"
    moved = [record_id for record_id in IDS if record_id != edited_id and after[record_id] != before[record_id]]
    assert not moved, f"editing {edited_id} changed the hashes of {moved}"
    moved_spans = [record_id for record_id in IDS
                   if record_id != edited_id and spans_after[record_id] != spans_before[record_id]]
    assert not moved_spans, f"editing {edited_id} changed the spans of {moved_spans}"


def test_a_duplicate_id_in_the_register_is_refused_with_both_locations(api, tmp_path):
    """DEC-202 under two headings: the load goes on (the other entries are records), DEC-202 is no record, and
    ``invalid`` names the register and the line of each of the two headings."""
    second = "### DEC-202 — The second decision, again"
    register = REGISTER + f"\n{second}\n- **Status:** ACCEPTED (owner, 2026-10-04)\n- **Decision:** Again.\n"
    first_line = support.line_of(register, "### DEC-202 — The second decision")
    second_line = support.line_of(register, second)
    project = support.project_with_register(tmp_path / "project", register)
    summary, records = api.load_and_records(project.root)

    entries = support.register_records(records)
    assert {"DEC-201", "DEC-203", "DEC-204"} <= set(entries), f"the duplicate stopped the other entries: {entries}"
    assert "DEC-202" not in support.by_id(records), "a duplicate id is a record: one of the two headings was chosen"
    named = support.invalid_naming(summary, "DEC-202", path=support.REGISTER_REL)
    assert named, f"`invalid` does not name DEC-202 in the register: {summary['invalid']}"
    said = " ".join(str(entry.get("reason")) for entry in named)
    missing = [line for line in (first_line, second_line)
               if not support.invalid_naming({"invalid": [{"reason": said}]}, str(line))]
    assert not missing, (f"the refusal of DEC-202 does not name both locations (lines {first_line} and "
                         f"{second_line} of {support.REGISTER_REL}); it lacks line {missing}: {named}")


def test_an_id_recorded_as_a_file_and_as_an_entry_names_both_locations(api, tmp_path):
    """DEC-203 recorded by ``docs/adr/DEC-203.md`` and by an entry of the register: ``invalid`` names the entry
    with the decision file's path and the line of the entry's heading. Which of the two stands is W1-10's
    (the file); this case holds the locations only."""
    file_rel = "docs/adr/DEC-203.md"
    line = support.line_of(REGISTER, "### DEC-203 — The third decision")
    project = support.project_with_register(tmp_path / "project", REGISTER,
                                            files={file_rel: support.decision_file("DEC-203")})
    summary, _ = api.load_and_records(project.root)

    named = support.invalid_naming(summary, "DEC-203", path=support.REGISTER_REL)
    assert named, f"`invalid` does not name the entry that a decision file also records: {summary['invalid']}"
    said = " ".join(str(entry.get("reason")) for entry in named)
    assert file_rel in said, f"the refusal does not name the decision file {file_rel}: {named}"
    assert support.invalid_naming({"invalid": [{"reason": said}]}, str(line)), \
        f"the refusal does not name the entry's location, line {line} of {support.REGISTER_REL}: {named}"
