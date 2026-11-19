"""KPI S2: the kept register, built from the archive (EMERGENCY-2 11.3, DEC-1214 G4 (a)).

Repository-state cases on this tree's register and archive; the doctor case runs ``gov doctor --json`` as a child on
two temporary clones (the base and HEAD), offline, with an empty ``HOME``.
"""

from __future__ import annotations

import re

import w2_203_support as s


def _read(rel: str) -> str:
    path = s.REPO / rel
    assert path.is_file(), f"{rel} is not a file of this tree"
    return path.read_text(encoding="utf-8")


def _expected() -> list[tuple[str, str]]:
    """The archive's entries the kept register must hold, in the archive's order."""
    wanted = [(record_id, text) for record_id, text in s.entries(_read(s.ARCHIVE_REL)) if s.kept(record_id, text)]
    assert len(wanted) > 100, f"premise: the archive holds {len(wanted)} kept or late entries"
    return wanted


def test_s2_the_register_holds_the_kept_entries_and_every_late_one_in_the_archives_order_and_no_other():
    wanted = [record_id for record_id, _ in _expected()]
    held = [record_id for record_id, _ in s.entries(_read(s.REGISTER_REL))]
    assert held == wanted, (f"the register holds {len(held)} entries, the archive has {len(wanted)} kept or late: "
                            f"missing {[i for i in wanted if i not in held][:8]}, "
                            f"not kept {[i for i in held if i not in wanted][:8]}"
                            + ("" if sorted(held) != sorted(wanted) else ", in another order"))
    late = [record_id for record_id in held if s.number_of(record_id) >= s.FIRST_LATE]
    assert late[:1] == ["DEC-1211"] and len(late) >= 6, f"the entries from DEC-1211 on: {late}"


def test_s2_each_entry_is_the_archives_verbatim():
    held = dict(s.entries(_read(s.REGISTER_REL)))
    wanted = _expected()
    differing = [record_id for record_id, text in wanted if held.get(record_id) != text]
    assert not differing, f"{len(differing)} entries are not the archive's text: {differing[:10]}"
    for record_id, text in wanted[:1] + wanted[-1:]:  # the heading, the status line and its class are in that text
        lines = text.split("\n")
        assert lines[0].startswith(f"### {record_id}") and "**Status:**" in lines[1]


def test_s2_the_store_loader_reads_the_register_with_no_refusal():
    from gov.store.loader import register_entries

    _read(s.ARCHIVE_REL)  # the register is the kept one only once the archive exists
    live, refused = register_entries(_read(s.REGISTER_REL))
    assert refused == [], f"the store's loader refuses headings of the kept register: {refused[:5]}"
    assert [entry["id"] for entry in live] == [record_id for record_id, _ in _expected()]


def test_s2_the_head_says_what_the_file_is_and_names_the_archive_and_audit_8():
    text = _read(s.REGISTER_REL)
    head = text[:text.index("### DEC-")]
    assert head.startswith("# "), "the register opens with its title"
    assert s.ARCHIVE_REL in head, f"the head does not name the archive {s.ARCHIVE_REL}"
    assert re.search(r"audit 8|08-register", head, re.IGNORECASE), "the head does not name audit 8"
    assert len(head.split("\n")) <= 40, f"the head is {len(head.splitlines())} lines: it is short"


def test_s2_doctor_lists_the_archive_among_its_historical_paths():
    from gov.doctor import command

    assert s.ARCHIVE_REL in command.HISTORICAL_PATHS, f"HISTORICAL_PATHS: {command.HISTORICAL_PATHS}"
    assert s.REGISTER_REL in command.HISTORICAL_PATHS


def test_s2_doctor_reports_no_more_problems_than_on_the_base(base_clone, head_clone, home, moved):
    """Each part's outcome is the base's; no path is unclassified; no moved reference appears that the base lacked."""
    base, head = s.both(base_clone, head_clone, home, "-m", "gov.cli.main", "doctor", "--json", "--root", "{root}")

    def parts(answer):
        result = answer.get("result") or answer.get("error", {}).get("details") or {}
        assert "path_map" in result and "path_compliance" in result, f"gov doctor gave no parts: {str(answer)[:600]}"
        return result

    base, head = parts(base), parts(head)
    statuses = {name: (base[name].get("status"), head.get(name, {}).get("status")) for name in base
                if isinstance(base[name], dict)}
    changed = {name: pair for name, pair in statuses.items() if pair[0] != pair[1]}
    assert not changed, f"doctor's outcome per part, (base, this tree): {changed}"
    assert head["path_map"].get("unclassified_count") == 0, head["path_map"]

    def moved_references(result):
        return {(ref["old_path"], ref["new_path"], ref["referenced_in"])
                for ref in result["path_compliance"].get("moved_references") or []}

    new = sorted(moved_references(head) - moved_references(base))
    assert not new, f"{len(new)} moved references the base did not report: {new[:5]}"
