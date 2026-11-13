"""The list rows W2-M150, W2-M320 and W2-L319, where ``gov impact`` holds them.

- **W2-M150** (governance paths are derived from the path map, not fixed path prefixes). Reading R10: each entry of
  ``result.change`` carries ``governance``: true when its path lies in a namespace whose ``memory_class`` is
  ``governance`` (path-map.schema.json), false otherwise. The close command's own prefixes are outside this
  ticket's paths (package P-4).
- **W2-M320** (a change that edits a closed specification in place is flagged; DEC-105's three costed options).
  Reading R9 (package P-5): a closed specification is a ``specification`` record with ``status: CLOSED``. A change
  to one gives ``result.options``: DEC-105's three options (apply now, defer, re-baseline), each with a ``cost``.
  An edit of its file that keeps its id, in the working tree or in a commit after it was closed, gives an entry of
  ``result.findings`` whose ``code`` holds ``IN_PLACE`` and that names the specification.
- **W2-L319** (the closure depth per radius comes from a measurement or an owner decision). Reading R11 (package
  P-2): ``result.depth_source`` names where the depth of the radius comes from: an owner decision of this
  repository's register (ACCEPTED by the owner), or a measurement file in this repository. DEC-035 (PROPOSED,
  "numbers are placeholders") and DEC-391 (delegated, "DEC-035's placeholders") are not such a source.
"""

from __future__ import annotations

import re

import pytest

import w2_37_support as support


# --------------------------------------------------------------------------
# W2-M150
# --------------------------------------------------------------------------

def governance_flag(found, wanted):
    entries = [entry for entry in found["change"] if entry["id"] == wanted]
    assert len(entries) == 1, f"`change` does not name {wanted} once: {found['change']}"
    value = entries[0].get("governance")
    assert isinstance(value, bool), f"the change {wanted} does not say whether it is governance: {entries[0]}"
    return value


@pytest.mark.parametrize("swapped", [False, True], ids=["policy-is-governance", "notes-are-governance"])
def test_governance_paths_are_the_path_maps_not_fixed_prefixes(built, box, tmp_path, swapped):
    """``policy/DEC-010.md`` and ``governance/notes/DEC-011.md``: which is governance follows the path map alone."""
    root = support.governance_project(tmp_path / "repo", swapped=swapped)
    support.load_store(root, box)
    unusual = governance_flag(support.ask(root, support.UNUSUAL, box), support.UNUSUAL)
    usual = governance_flag(support.ask(root, support.USUAL, box), support.USUAL)
    assert (unusual, usual) == ((False, True) if swapped else (True, False)), \
        f"the path map puts policy/** in {'product' if swapped else 'governance'} memory and governance/notes/** in " \
        f"{'governance' if swapped else 'product'} memory; gov impact says policy: {unusual}, notes: {usual}"


# --------------------------------------------------------------------------
# W2-M320 and CAP-33.e
# --------------------------------------------------------------------------

def in_place_findings(found, wanted):
    findings = found.get("findings")
    assert isinstance(findings, list), f"the result carries no `findings` list: {sorted(found)}"
    return [f for f in findings if isinstance(f, dict) and "IN_PLACE" in str(f.get("code", "")).upper()
            and wanted in support.text_of(f)]


def test_a_change_to_a_closed_specification_gives_the_three_costed_options(asked):
    """DEC-105, CAP-33.e: apply now, defer, re-baseline, each with its cost."""
    found = asked(support.CLOSED_SPEC)
    options = found.get("options")
    assert isinstance(options, list) and len(options) == 3, f"`options` is not a list of three: {options!r}"
    names = sorted(str(entry.get("option", "")).lower() for entry in options if isinstance(entry, dict))
    assert names == sorted(support.OPTIONS), f"the options are {names}, not DEC-105's {sorted(support.OPTIONS)}"
    for entry in options:
        assert isinstance(entry.get("cost"), str) and entry["cost"].strip(), f"an option without a cost: {entry!r}"


def test_an_unedited_closed_specification_is_not_flagged_as_edited_in_place(asked):
    assert in_place_findings(asked(support.CLOSED_SPEC), support.CLOSED_SPEC) == []


def test_an_edit_in_place_of_a_closed_specification_in_the_working_tree_is_flagged(project, box):
    path = project.root / "docs" / "specs" / f"{support.CLOSED_SPEC}.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nA new requirement, written over the closed text.\n",
                    encoding="utf-8")
    found = support.ask(project.root, support.CLOSED_SPEC, box)
    assert in_place_findings(found, support.CLOSED_SPEC), \
        f"an uncommitted edit of the closed {support.CLOSED_SPEC} is not flagged: {found.get('findings')!r}"


def test_an_edit_in_place_of_a_closed_specification_in_a_commit_is_flagged(project, box):
    """As in a-dev ``f59aa0e`` (DEC-674): the edit is committed after the specification was closed."""
    path = project.root / "docs" / "specs" / f"{support.CLOSED_SPEC}.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nA new requirement, written over the closed text.\n",
                    encoding="utf-8")
    project.commit("edit the closed specification")
    support.load_store(project.root, box)
    found = support.ask(project.root, support.CLOSED_SPEC, box)
    assert in_place_findings(found, support.CLOSED_SPEC), \
        f"a committed edit of the closed {support.CLOSED_SPEC} is not flagged: {found.get('findings')!r}"


def test_an_edit_of_an_open_specification_is_not_flagged(project, box):
    path = project.root / "docs" / "specs" / f"{support.OPEN_SPEC}.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nA draft may change.\n", encoding="utf-8")
    project.commit("edit the draft")
    support.load_store(project.root, box)
    assert in_place_findings(support.ask(project.root, support.OPEN_SPEC, box), support.OPEN_SPEC) == []


# --------------------------------------------------------------------------
# W2-L319
# --------------------------------------------------------------------------

PLACEHOLDERS = ("DEC-035", "DEC-391")


def register_entry(decision_id):
    text = support.OWN_REGISTER.read_text(encoding="utf-8")
    match = re.search(rf"^### {re.escape(decision_id)}\b.*?(?=^### |\Z)", text, re.MULTILINE | re.DOTALL)
    return match.group(0) if match else None


def test_the_depth_of_a_radius_comes_from_an_owner_decision_or_a_measurement(asked):
    found = asked(support.CHANGED)
    source = found.get("depth_source")
    assert isinstance(source, str) and source.strip(), f"the result does not say where its depth comes from: {source!r}"
    if support.DECISION_ID.match(source):
        assert source not in PLACEHOLDERS, f"the depth comes from {source}, whose numbers are placeholders"
        entry = register_entry(source)
        assert entry, f"{source} is not an entry of this repository's register"
        assert re.search(r"\*\*Status:\*\* ACCEPTED \(owner", entry), f"{source} is not an owner decision"
    else:
        measured = support.REPO_ROOT / source
        assert measured.is_file() and measured.resolve().is_relative_to(support.REPO_ROOT / "docs"), \
            f"the depth's source {source!r} is neither an owner decision nor a measurement file under docs/"
