"""W2-175 success 7: the change's CIT-P record, docs/changes/W2-175-CIT-P.md (DEC-1116's route, CAP-33).

The record is read as the tree holds it at the head; the template bytes it names are the tree's (the head's) and
the base's (git, at each file's base commit). The record is never required to be ACCEPTED: the owner's approval
follows the independent review, after the lead returns (README).
"""

from __future__ import annotations

import pytest

import w2_175_support as t

NEEDED = ("DEC-1137", "DEC-820", "DEC-861")


@pytest.mark.parametrize("key", ("decisions_read", "decisions_carried"))
def test_s7_record_front_matter_cites_dec_1137_dec_820_and_dec_861(key):
    front, _ = t.record()
    assert isinstance(front, dict), "docs/changes/W2-175-CIT-P.md opens with no YAML front matter"
    missing = [dec for dec in NEEDED if dec not in t.ids_in(front.get(key))]
    assert not missing, f"docs/changes/W2-175-CIT-P.md: {key} lacks {missing} (it holds {front.get(key)!r})"


def test_s7_record_has_an_entry_for_each_cap_33_step():
    _, body = t.record()
    found = t.entries(body)
    assignment = t.step_assignment(found)
    assert assignment is not None, (
        "docs/changes/W2-175-CIT-P.md has no section (a heading, or a row of a steps table) of its own for each "
        f"CAP-33 step {list(t.STEPS)}; headings and row titles read: {[title for title, _ in found]}")


def test_s7_record_status_is_accepted_only_with_the_owner_s_approval():
    front, body = t.record()
    assert isinstance(front, dict), "docs/changes/W2-175-CIT-P.md opens with no YAML front matter"
    status = str(front.get("status", "")).strip().upper()
    assert status in t.STATUSES, f"docs/changes/W2-175-CIT-P.md: status {front.get('status')!r} is none of {t.STATUSES}"
    if status in t.APPROVED:
        found = t.entries(body)
        approvals = [text for title, text in found if t.STEPS["owner's approval"].search(title.replace("*", ""))]
        assert any(t.approval_given(text) for text in approvals), (
            f"docs/changes/W2-175-CIT-P.md is {status} but its owner's-approval section records no approval "
            f"(a DEC id or a date): {approvals}")


@pytest.mark.parametrize("stem", t.SEVEN)
def test_s7_record_sha256_of_each_template_is_its_sha256_at_the_head(stem):
    _, body = t.record()
    rows = [row for row in t.table_rows(body) if f"{stem}.md" in row]
    assert rows, f"docs/changes/W2-175-CIT-P.md has no table row naming {stem}.md"
    head = t.sha256(t.path_of(stem).read_bytes())
    assert any(head in t.HEX64.findall(row.lower()) for row in rows), \
        f"docs/changes/W2-175-CIT-P.md: no row naming {stem}.md holds its sha256 at the head ({head}): {rows}"


@pytest.mark.parametrize("stem", t.SEVEN)
def test_s7_record_names_each_template_s_base_sha256(stem):
    _, body = t.record()
    rows = [row for row in t.table_rows(body) if f"{stem}.md" in row]
    assert rows, f"docs/changes/W2-175-CIT-P.md has no table row naming {stem}.md"
    t.base_text(stem)  # premise: the base is the 1.0.0 template
    base = t.sha256(t.base_bytes(stem))
    assert any(base in t.HEX64.findall(row.lower()) for row in rows), \
        f"docs/changes/W2-175-CIT-P.md: no row naming {stem}.md holds its base sha256 ({base}, at {t.BASE[stem]}): {rows}"
