"""W2-98, review round 1 (DEC-136): cases for findings F1, F2, F4 and the part of F3 that fails closed (B1-B6).

Every case plants an otherwise clean spec (or imports folder) in ``tmp_path``, changes one thing and runs
``python3 <skill>/check_spec.py`` (I3's and I4's words and exits). A reason's own wording is fixed only where the
behaviour fixes it: the part's name, a KPI id or the quoted line's id text, the missing column or item word, the exit
code, and the absence of ``PASS`` beside a refusal.

- B1  a list item under ``## KPIs`` that is no KPI line in form and no ``Fails if:`` line is refused, naming the line.
- B2  a line after a KPI line (or after its ``Fails if:`` line) is part of that text, indented or not, judged for code.
- B3  an empty ``privacy`` or ``secrets`` cell is refused, naming the source and the column.
- B4  a cell holding only a placeholder (owner, source, licence or recipe) is refused as if empty.
- B5  ``--imports``: records come only from the ``imports:`` list; a part with several records needs all allowed.
- B6  Markdown emphasis on the ``Fails if:`` label, a label with its text on the next line, and ``_word_`` emphasis
      are not refused; ``send_welcome`` and ``__all__`` are still code.

Clean controls (green at the head as well as after the fix) are marked in each group.
"""
from __future__ import annotations

import pytest

import w2_98_support as s

PART = "reference-notes.md"
OTHER = "checklist-ideas.md"


def _kpis(middle):
    """K1 and K3 clean, ``middle`` (the text planted for the second KPI, as written) between them."""
    return "\n".join([s.clean_kpi(1), middle, s.clean_kpi(3)])


def _check_kpis(tmp_path, kpi_text):
    code, output, _ = s.check(tmp_path, text=s.spec_with_kpi_text(kpi_text))
    return code, output


def _assert_refused(code, output, part):
    assert code == 1, f"expected exit 1 for a refused spec, got {code}: {output!r}"
    assert s.refused(output, part), f"no 'REFUSED {part}: ...' line in: {output!r}"
    assert not s.passes(output), f"PASS printed beside a REFUSED line: {output!r}"


def _assert_clean(code, output):
    assert code == 0, f"a clean spec exited {code}: {output!r}"
    assert s.passes(output), f"no PASS line for a clean spec: {output!r}"
    assert not s.refused(output) and not s.p1_lines(output), f"a clean spec drew findings: {output!r}"


def _assert_names_only(output, kpi="K2"):
    lines = s.refused(output, "KPIs")
    assert any(kpi in line for line in lines), f"no REFUSED KPIs line names {kpi}: {lines}"
    others = [k for k in ("K1", "K2", "K3") if k != kpi]
    assert not any(k in line for line in lines for k in others), f"a KPI other than {kpi} was named: {lines}"


# ==================================================================================================================
# B1: a list item under ## KPIs that is neither a KPI line in form nor a Fails if: line
# ==================================================================================================================

# (the planted line, the id-like text its quotation must carry in the reason, or None when the line carries none)
NOT_IN_FORM = {
    "a space before the colon": ("- K2 : The member sees it.", "K2"),
    "a numbered item": ("2. K2: The member sees it.", "K2"),
    "a numbered item with a parenthesis": ("2) K2: The member sees it.", "K2"),
    "a plus bullet": ("+ K2: The member sees it.", "K2"),
    "an id with a letter": ("- K2a: The member sees it.", "K2"),
    "an id with a note": ("- K2 (new): The member sees it.", "K2"),
    "a bold id with a dash": ("- **K2** — the member sees it.", "K2"),
    "an asterisk bullet with a space before the colon": ("* K2 : The member sees it.", "K2"),
    "a bullet with no id": ("- The member sees it.", None),
}


@pytest.mark.parametrize("form", sorted(NOT_IN_FORM))
def test_a_list_item_that_is_no_kpi_line_in_form_is_refused_naming_the_line(tmp_path, form):
    line, needle = NOT_IN_FORM[form]
    code, output = _check_kpis(tmp_path, _kpis(line))
    _assert_refused(code, output, "KPIs")
    if needle:
        lines = s.refused(output, "KPIs")
        assert any(needle in found for found in lines), f"no REFUSED KPIs line carries {needle!r} (the line's id): {lines}"


@pytest.mark.parametrize("form", ["a space before the colon", "a numbered item", "an id with a letter"])
def test_a_list_item_that_is_no_kpi_line_is_refused_when_it_is_the_last_item_of_the_part(tmp_path, form):
    line, needle = NOT_IN_FORM[form]
    code, output = _check_kpis(tmp_path, "\n".join([s.clean_kpi(1), s.clean_kpi(2), s.clean_kpi(3), line]))
    _assert_refused(code, output, "KPIs")
    assert any(needle in found for found in s.refused(output, "KPIs")), output


# controls (green at the head)
@pytest.mark.parametrize("lead", ["These are the checks support staff run after each release.",
                                  "These are the checks support staff run after each release.\n"],
                         ids=["prose line directly above", "prose line and a blank line"])
def test_a_plain_prose_line_before_the_first_kpi_is_allowed(tmp_path, lead):
    code, output = _check_kpis(tmp_path, lead + "\n" + _kpis(s.clean_kpi(2)))
    _assert_clean(code, output)


@pytest.mark.parametrize("form", ["asterisk bullet", "bold id, colon outside", "bold id, colon inside"])
def test_a_kpi_line_in_form_passes(tmp_path, form):
    behaviour, fails = s.CLEAN_KPIS[1]
    lead = {"asterisk bullet": "* K2:", "bold id, colon outside": "- **K2**:",
            "bold id, colon inside": "- **K2:**"}[form]
    code, output = _check_kpis(tmp_path, _kpis(f"{lead} {behaviour}\n  Fails if: {fails}"))
    _assert_clean(code, output)


# ==================================================================================================================
# B2: continuation lines belong to the KPI and are judged for code
# ==================================================================================================================

CONTINUATION = {
    "a call, at column 0": "send_welcome() runs.",
    "a code span, at column 0": "`settings` is shown.",
    "a path, at column 0": "data/summary.csv is written.",
    "a dotted identifier, at column 0": "user.profile is shown.",
    "a snake_case identifier, at column 0": "plan_name is shown.",
    "a call, indented": "  checkout() returns.",
    "a call, indented deeper": "    checkout() returns.",
}


@pytest.mark.parametrize("form", sorted(CONTINUATION))
def test_a_continuation_line_of_a_kpi_that_names_code_is_refused_naming_the_kpi(tmp_path, form):
    middle = ("- K2: A returning member sees the page after\n" + CONTINUATION[form] + "\n"
              "  Fails if: no page.")
    code, output = _check_kpis(tmp_path, _kpis(middle))
    _assert_refused(code, output, "KPIs")
    _assert_names_only(output)


def test_a_continuation_line_of_the_last_kpi_is_judged_up_to_the_next_section(tmp_path):
    last = ("- K3: A member who mistypes the email address is asked to correct it before\n"
            "send_welcome() runs.\n  Fails if: an account is created with the mistyped address.")
    code, output = _check_kpis(tmp_path, "\n".join([s.clean_kpi(1), s.clean_kpi(2), last]))
    _assert_refused(code, output, "KPIs")
    _assert_names_only(output, "K3")


def test_a_second_continuation_line_is_judged_too(tmp_path):
    middle = ("- K2: A returning member sees the page after\nthe sign-up form closes and\n"
              "send_welcome() runs.\n  Fails if: no page.")
    code, output = _check_kpis(tmp_path, _kpis(middle))
    _assert_refused(code, output, "KPIs")
    _assert_names_only(output)


@pytest.mark.parametrize("form", sorted(CONTINUATION))
def test_a_line_after_the_fails_if_line_that_names_code_is_refused_naming_the_kpi(tmp_path, form):
    middle = "- K2: A returning member sees the welcome page.\n  Fails if: the page is blank\n" + CONTINUATION[form]
    code, output = _check_kpis(tmp_path, _kpis(middle))
    _assert_refused(code, output, "KPIs")
    _assert_names_only(output)


def test_a_line_after_the_fails_if_line_of_the_last_kpi_is_judged_up_to_the_next_section(tmp_path):
    last = ("- K3: A member who mistypes the email address is asked to correct it.\n"
            "  Fails if: an account is created with the mistyped address\nsend_welcome() runs.")
    code, output = _check_kpis(tmp_path, "\n".join([s.clean_kpi(1), s.clean_kpi(2), last]))
    _assert_refused(code, output, "KPIs")
    _assert_names_only(output, "K3")


# controls (a continuation of plain prose is no finding)
def test_a_continuation_line_of_plain_prose_at_column_0_passes(tmp_path):
    middle = ("- K2: A returning member sees the page after\nthe sign-up form closes.\n"
              "  Fails if: no page.")
    code, output = _check_kpis(tmp_path, _kpis(middle))
    _assert_clean(code, output)


def test_a_continuation_line_of_plain_prose_after_the_fails_if_line_passes(tmp_path):
    middle = "- K2: A returning member sees the welcome page.\n  Fails if: the page is blank\nor the form shows again."
    code, output = _check_kpis(tmp_path, _kpis(middle))
    _assert_clean(code, output)


def test_an_indented_continuation_line_of_plain_prose_passes(tmp_path):
    middle = ("- K2: A returning member sees the page after\n  the sign-up form closes.\n"
              "  Fails if: no page\n  or the form shows again.")
    code, output = _check_kpis(tmp_path, _kpis(middle))
    _assert_clean(code, output)


# ==================================================================================================================
# B3: an empty privacy or secrets cell
# ==================================================================================================================

def _test_data(tmp_path, rows):
    code, output, _ = s.check(tmp_path, rows=rows)
    return code, output


def _data_lines(output):
    return [line.lower() for line in s.refused(output, "Test data")]


def _one_row(index, **changes):
    """The two clean rows with ``changes`` applied to row ``index``."""
    rows = [dict(r) for r in s.CLEAN_ROWS]
    rows[index].update(changes)
    return tuple(rows)


@pytest.mark.parametrize("column", ["privacy", "secrets"])
@pytest.mark.parametrize("index", [0, 1], ids=["imported row", "synthetic row"])
def test_an_empty_privacy_or_secrets_cell_is_refused_naming_the_source_and_the_column(tmp_path, index, column):
    code, output = _test_data(tmp_path, _one_row(index, **{column: ""}))
    _assert_refused(code, output, "Test data")
    source = s.CLEAN_ROWS[index]["source"].lower()
    assert any(source in line and column in line for line in _data_lines(output)), (
        f"no REFUSED Test data line names the source {source!r} and the column {column}: {output!r}")
    other = s.CLEAN_ROWS[1 - index]["source"].lower()
    assert not any(other in line for line in _data_lines(output)), f"the clean row {other!r} was named: {output!r}"


def test_an_empty_privacy_cell_and_an_empty_secrets_cell_are_each_named(tmp_path):
    code, output = _test_data(tmp_path, _one_row(0, privacy="", secrets=""))
    _assert_refused(code, output, "Test data")
    source = s.CLEAN_ROWS[0]["source"].lower()
    lines = _data_lines(output)
    assert any(source in line and "privacy" in line for line in lines), f"privacy is not named: {output!r}"
    assert any(source in line and "secrets" in line for line in lines), f"secrets is not named: {output!r}"


def test_a_spaces_only_privacy_cell_is_refused_as_empty(tmp_path):
    code, output = _test_data(tmp_path, _one_row(0, privacy="   "))
    _assert_refused(code, output, "Test data")
    assert any("privacy" in line for line in _data_lines(output)), output


# controls (green at the head)
@pytest.mark.parametrize("column", ["privacy", "secrets"])
def test_none_is_a_valid_privacy_and_secrets_value(tmp_path, column):
    code, output = _test_data(tmp_path, _one_row(0, **{column: "none"}))
    _assert_clean(code, output)


def test_none_in_both_cells_of_every_row_passes(tmp_path):
    rows = tuple(dict(r, privacy="none", secrets="none") for r in s.CLEAN_ROWS)
    code, output = _test_data(tmp_path, rows)
    _assert_clean(code, output)


# ==================================================================================================================
# B4: a cell holding only a placeholder is refused as if it were empty
# ==================================================================================================================

PLACEHOLDERS = ["-", "—", "–", "TBD", "tbd", "TODO", "Todo", "unknown", "Unknown", "?", "n/a", "N/A", "none", "None"]
EMPHASISED = ["**TBD**", "_unknown_", "*n/a*", " N/A ", "__none__", "*TODO*"]

# the cell, the row it is planted in, the item word the refusal names, and whether the source name is in the line
CELLS = {
    "owner": (0, "owner", "owner", True),
    "source": (0, "source", "source", False),
    "licence": (0, "licence or recipe", "licence", True),
    "recipe": (1, "licence or recipe", "recipe", True),
}


def _placeholder_case(tmp_path, cell, text):
    index, column, word, named_by_source = CELLS[cell]
    code, output = _test_data(tmp_path, _one_row(index, **{column: text}))
    _assert_refused(code, output, "Test data")
    lines = _data_lines(output)
    assert any(word in line for line in lines), f"no REFUSED Test data line names the {word}: {output!r}"
    if named_by_source:
        source = s.CLEAN_ROWS[index]["source"].lower()
        assert any(source in line and word in line for line in lines), (
            f"no REFUSED Test data line names the source {source!r} and the {word}: {output!r}")


@pytest.mark.parametrize("cell", sorted(CELLS))
@pytest.mark.parametrize("text", PLACEHOLDERS, ids=[f"ph{n}" for n in range(len(PLACEHOLDERS))])
def test_a_placeholder_cell_is_refused_as_if_it_were_empty(tmp_path, cell, text):
    _placeholder_case(tmp_path, cell, text)


@pytest.mark.parametrize("cell", sorted(CELLS))
@pytest.mark.parametrize("text", EMPHASISED, ids=[f"em{n}" for n in range(len(EMPHASISED))])
def test_a_placeholder_in_emphasis_or_with_spaces_is_refused_as_if_it_were_empty(tmp_path, cell, text):
    _placeholder_case(tmp_path, cell, text)


# controls (green at the head): a placeholder word inside real text is no placeholder
@pytest.mark.parametrize("column, text", [
    ("owner", "Priya Nair, data steward (TBD backup)"),
    ("licence or recipe", "MIT (unknown version)"),
    ("owner", "Nadia Unknown, data steward"),
], ids=["owner with TBD inside", "licence with unknown inside", "owner whose surname is a placeholder word"])
def test_a_placeholder_word_inside_real_text_is_no_placeholder(tmp_path, column, text):
    code, output = _test_data(tmp_path, _one_row(0, **{column: text}))
    _assert_clean(code, output)


def test_a_recipe_that_begins_with_none_of_is_no_placeholder(tmp_path):
    rows = _one_row(1, **{"licence or recipe": "none of the questions are reused; written by hand"})
    code, output = _test_data(tmp_path, rows)
    _assert_clean(code, output)


# ==================================================================================================================
# B5: --imports reads records only from the imports: list; several records need every licence allowed
# ==================================================================================================================

def _imports(tmp_path, parts, imports_yaml):
    folder = s.planted_imports_folder(tmp_path, parts, imports_yaml)
    return s.run_script("--imports", folder, cwd=tmp_path)


def _naming(output, part):
    return [line for line in s.refused(output) if part in line]


def _assert_import_refused(code, output, part):
    assert code == 1, f"exit {code}: {output!r}"
    assert _naming(output, part), f"no REFUSED line names {part}: {output!r}"
    assert all(line.startswith("REFUSED import") for line in s.refused(output)), f"{output!r}"
    assert not s.passes(output), f"PASS printed beside a refusal: {output!r}"


OTHER_KEYS = ["notes", "vendored", "previous_imports", "import"]


@pytest.mark.parametrize("key", OTHER_KEYS)
def test_a_record_under_another_top_level_key_is_no_record(tmp_path, key):
    code, output = _imports(tmp_path, [PART], {"imports": [], key: [s.record(PART, "MIT")]})
    _assert_import_refused(code, output, PART)


@pytest.mark.parametrize("key", OTHER_KEYS)
def test_a_record_under_another_key_with_no_imports_key_at_all_is_no_record(tmp_path, key):
    code, output = _imports(tmp_path, [PART], {key: [s.record(PART, "MIT")]})
    _assert_import_refused(code, output, PART)


def test_only_the_part_recorded_nowhere_but_under_another_key_is_named(tmp_path):
    data = {"imports": [s.record(OTHER, "MIT")], "notes": [s.record(PART, "MIT")]}
    code, output = _imports(tmp_path, [PART, OTHER], data)
    _assert_import_refused(code, output, PART)
    assert not _naming(output, OTHER), f"the recorded, allowed part {OTHER} was named: {output!r}"


def test_a_forbidding_record_under_another_key_does_not_count_against_a_part_recorded_as_allowed(tmp_path):
    data = {"imports": [s.record(PART, "MIT")], "notes": [s.record(PART, "GPL-3.0")]}
    code, output = _imports(tmp_path, [PART], data)
    assert code == 0 and s.passes(output) and not s.refused(output), f"exit {code}: {output!r}"


MIXED = {
    "GPL-3.0 then MIT": ("GPL-3.0", "MIT"),
    "MIT then GPL-3.0": ("MIT", "GPL-3.0"),
    "Proprietary then MIT": ("Proprietary", "MIT"),
    "MIT then CC-BY-NC-4.0": ("MIT", "CC-BY-NC-4.0"),
    "Apache-2.0 then Proprietary": ("Apache-2.0", "Proprietary"),
}


@pytest.mark.parametrize("form", sorted(MIXED))
def test_a_part_with_one_forbidding_and_one_allowed_record_is_refused_naming_the_part(tmp_path, form):
    data = {"imports": [s.record(PART, lic) for lic in MIXED[form]]}
    code, output = _imports(tmp_path, [PART], data)
    _assert_import_refused(code, output, PART)


def test_a_part_with_an_allowed_record_between_two_forbidding_ones_is_refused(tmp_path):
    data = {"imports": [s.record(PART, "GPL-3.0"), s.record(PART, "MIT"), s.record(PART, "Proprietary")]}
    code, output = _imports(tmp_path, [PART], data)
    _assert_import_refused(code, output, PART)


def test_a_part_with_two_records_is_refused_but_a_single_record_part_beside_it_is_not_named(tmp_path):
    data = {"imports": [s.record(PART, "MIT"), s.record(PART, "GPL-3.0"), s.record(OTHER, "MIT")]}
    code, output = _imports(tmp_path, [PART, OTHER], data)
    _assert_import_refused(code, output, PART)
    assert not _naming(output, OTHER), f"the single-record allowed part {OTHER} was named: {output!r}"


# controls (green at the head)
def test_a_single_mit_record_passes(tmp_path):
    code, output = _imports(tmp_path, [PART], {"imports": [s.record(PART, "MIT")]})
    assert code == 0 and s.passes(output) and not s.refused(output), f"exit {code}: {output!r}"


@pytest.mark.parametrize("licences", [("MIT", "Apache-2.0"), ("MIT", "MIT"), ("BSD-3-Clause", "Apache-2.0", "MIT")],
                         ids=["MIT and Apache-2.0", "MIT twice", "three allowed"])
def test_a_part_whose_every_record_carries_an_allowed_licence_passes(tmp_path, licences):
    data = {"imports": [s.record(PART, lic) for lic in licences]}
    code, output = _imports(tmp_path, [PART], data)
    assert code == 0 and s.passes(output) and not s.refused(output), f"exit {code}: {output!r}"


def test_an_unrelated_top_level_key_beside_the_imports_list_is_harmless(tmp_path):
    data = {"imports": [s.record(PART, "MIT")], "notes": ["reviewed by hand"]}
    code, output = _imports(tmp_path, [PART], data)
    assert code == 0 and s.passes(output) and not s.refused(output), f"exit {code}: {output!r}"


# ==================================================================================================================
# B6: emphasis on the Fails if: label, the label with its text on the next line, _word_ emphasis (these refuse today)
# ==================================================================================================================

LABELS = {
    "bold": "**Fails if:** the welcome page does not appear in the same visit.",
    "star emphasis": "*Fails if:* the welcome page does not appear in the same visit.",
    "underscore emphasis": "_Fails if:_ the welcome page does not appear in the same visit.",
}


@pytest.mark.parametrize("form", sorted(LABELS))
def test_a_fails_if_label_in_markdown_emphasis_counts_as_the_failure_line(tmp_path, form):
    behaviour = s.CLEAN_KPIS[1][0]
    code, output = _check_kpis(tmp_path, _kpis(f"- K2: {behaviour}\n  {LABELS[form]}"))
    _assert_clean(code, output)


@pytest.mark.parametrize("form", sorted(LABELS))
def test_every_kpi_may_carry_an_emphasised_fails_if_label(tmp_path, form):
    kpis = "\n".join(f"- K{n}: {s.CLEAN_KPIS[n - 1][0]}\n  {LABELS[form]}" for n in (1, 2, 3))
    code, output = _check_kpis(tmp_path, kpis)
    _assert_clean(code, output)


def test_a_fails_if_label_with_its_text_on_the_next_indented_line_counts_as_present(tmp_path):
    middle = f"- K2: {s.CLEAN_KPIS[1][0]}\n  Fails if:\n    the member sees a blank page or the sign-up form again."
    code, output = _check_kpis(tmp_path, _kpis(middle))
    _assert_clean(code, output)


@pytest.mark.parametrize("where", ["behaviour", "failure text", "both"])
@pytest.mark.parametrize("word", ["_quickly_", "(_quickly_)", "_quickly_."], ids=["bare", "in brackets", "full stop"])
def test_a_word_in_underscore_emphasis_is_not_a_snake_case_identifier(tmp_path, where, word):
    behaviour = f"A member sees the welcome page {word} after sign-up" if where != "failure text" else \
        s.CLEAN_KPIS[1][0]
    fails = f"the page appears {word} late" if where != "behaviour" else s.CLEAN_KPIS[1][1]
    code, output = _check_kpis(tmp_path, _kpis(f"- K2: {behaviour}\n  Fails if: {fails}"))
    _assert_clean(code, output)


def test_emphasis_on_the_label_and_emphasis_on_a_word_together_pass(tmp_path):
    middle = "- K2: A member sees the welcome page _quickly_ after sign-up.\n  _Fails if:_ the page is _slow_ to appear."
    code, output = _check_kpis(tmp_path, _kpis(middle))
    _assert_clean(code, output)


# controls (green at the head): these are still code
@pytest.mark.parametrize("word", ["send_welcome", "__all__", "plan_name"])
def test_a_snake_case_or_dunder_identifier_is_still_code(tmp_path, word):
    middle = f"- K2: A member sees the page after {word} runs.\n  Fails if: no page."
    code, output = _check_kpis(tmp_path, _kpis(middle))
    _assert_refused(code, output, "KPIs")
    _assert_names_only(output)
