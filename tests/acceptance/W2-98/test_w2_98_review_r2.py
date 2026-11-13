"""W2-98, review round 2 (DEC-136; the owner's P-W2-98-R2 (a), DEC-1154): cases for findings F1, F2 and F3 (C1-C3).

Every case plants an otherwise clean spec in ``tmp_path``, changes one thing and runs ``python3 <skill>/check_spec.py``
(I3's words and exits). A reason's own wording is fixed only where the behaviour fixes it: the part's name, the KPI id
or the quoted line's id text, the missing item's word (``behaviour``, ``Fails if``, ``owner``, ``source``, ``licence``,
``recipe``), the exit code, and the absence of ``PASS`` beside a refusal.

The placeholder class (C1 and C3): after removing surrounding spaces, Markdown emphasis (``*``, ``_``), code-span
backticks, surrounding brackets or parentheses and trailing punctuation, a text that is empty or has no letter or digit,
a lone angle-bracket slot, a deferral (TBD, TBC, TBA, TODO, pending, unknown, ``to be <word>``) or an absence word alone
(none, nobody, no one, n/a, na, nil, null), matched case-insensitively against the whole text, never a word in a sentence.

- C1  a KPI behaviour or a ``Fails if:`` text that is empty or a placeholder is refused (``K<n> has no behaviour``,
      ``K<n> has no Fails if: line``).
- C2  a line under ``## KPIs`` that is no list item but starts with a KPI id is refused, quoting the line, and is never
      read as part of the KPI before it.
- C3  an owner, source or ``licence or recipe`` cell that is a placeholder (or, for the licence or recipe cell, says no
      licence was found) is refused as if empty; ``privacy`` and ``secrets`` are unchanged.

Clean controls (green at the head as well as after the fix) are marked in each group.
"""
from __future__ import annotations

import pytest

import w2_98_support as s


def _assert_refused(code, output, part):
    assert code == 1, f"expected exit 1 for a refused spec, got {code}: {output!r}"
    assert s.refused(output, part), f"no 'REFUSED {part}: ...' line in: {output!r}"
    assert not s.passes(output), f"PASS printed beside a REFUSED line: {output!r}"


def _assert_clean(code, output):
    assert code == 0, f"a clean spec exited {code}: {output!r}"
    assert s.passes(output), f"no PASS line for a clean spec: {output!r}"
    assert not s.refused(output) and not s.p1_lines(output), f"a clean spec drew findings: {output!r}"


def _check_kpis(tmp_path, kpi_text):
    code, output, _ = s.check(tmp_path, text=s.spec_with_kpi_text(kpi_text))
    return code, output


def _kpi(n, behaviour, fails):
    """The KPI ``K<n>`` as planted: ``- K<n>: <behaviour>`` (bare ``- K<n>:`` when the behaviour is empty) and its
    indented ``Fails if:`` line (the bare label when the text is empty)."""
    head = f"- K{n}: {behaviour}" if behaviour else f"- K{n}:"
    tail = f"  Fails if: {fails}" if fails else "  Fails if:"
    return f"{head}\n{tail}"


def _kpis_with(n, block):
    """The three KPIs, the clean ``K<n>`` replaced by ``block`` (the text planted, as written)."""
    return "\n".join(block if i == n else s.clean_kpi(i) for i in (1, 2, 3))


def _kpis(middle):
    """K1 and K3 clean, ``middle`` between them (it may be no KPI at all)."""
    return _kpis_with(2, middle)


def _kpi_lines(output):
    return s.refused(output, "KPIs")


def _names(output, kpi, word):
    """The REFUSED KPIs lines that name ``kpi`` and say it has *no* ``word`` (``K2 has no behaviour``, ``K2 has no
    Fails if: line``; lower-cased comparison), so a refusal for another reason (``names code``) does not count."""
    return [line for line in _kpi_lines(output) if kpi in line and f"no {word}".lower() in line.lower()]


def _assert_names_only(output, kpi, word):
    assert _names(output, kpi, word), f"no REFUSED KPIs line names {kpi} and {word!r}: {_kpi_lines(output)}"
    others = [k for k in ("K1", "K2", "K3") if k != kpi]
    assert not any(k in line for line in _kpi_lines(output) for k in others), (
        f"a KPI other than {kpi} was named: {_kpi_lines(output)}")


# ==================================================================================================================
# C1: a KPI behaviour or a Fails if: text that is empty or a placeholder
# ==================================================================================================================

# the ten examples of the behaviour first, then the rest of the class as it is worded
C1_PLACEHOLDERS = ["TBD", "-", "—", "n/a", "?", "TODO", "none", "(none)", "**TBD**", "to be written",
                   "Tbd.", "`TBD`", "...", "…", "TBC", "to be decided", "pending", "unknown", "nobody", "no one",
                   "nil", "null", "NA", "N/A.", "<behaviour>"]
C1_IDS = [f"ph{n}" for n in range(len(C1_PLACEHOLDERS))]


@pytest.mark.parametrize("text", C1_PLACEHOLDERS, ids=C1_IDS)
def test_a_placeholder_failure_text_is_refused_as_a_missing_fails_if_line(tmp_path, text):
    middle = _kpi(2, s.CLEAN_KPIS[1][0], text)
    code, output = _check_kpis(tmp_path, _kpis(middle))
    _assert_refused(code, output, "KPIs")
    _assert_names_only(output, "K2", "Fails if")


@pytest.mark.parametrize("n", [1, 2, 3], ids=["first KPI", "middle KPI", "last KPI"])
def test_a_failure_text_of_tbd_is_refused_naming_each_kpi_it_is_planted_in(tmp_path, n):
    code, output = _check_kpis(tmp_path, _kpis_with(n, _kpi(n, s.CLEAN_KPIS[n - 1][0], "TBD")))
    _assert_refused(code, output, "KPIs")
    _assert_names_only(output, f"K{n}", "Fails if")


@pytest.mark.parametrize("label", ["**Fails if:**", "*Fails if:*", "_Fails if:_"], ids=["bold", "star", "underscore"])
def test_a_placeholder_failure_text_after_an_emphasised_label_is_refused(tmp_path, label):
    middle = f"- K2: {s.CLEAN_KPIS[1][0]}\n  {label} TBD"
    code, output = _check_kpis(tmp_path, _kpis(middle))
    _assert_refused(code, output, "KPIs")
    _assert_names_only(output, "K2", "Fails if")


@pytest.mark.parametrize("text", ["TBD", "n/a", "—", "to be written", "(none)"], ids=[f"ph{n}" for n in range(5)])
def test_a_placeholder_failure_text_on_the_next_indented_line_is_refused(tmp_path, text):
    middle = f"- K2: {s.CLEAN_KPIS[1][0]}\n  Fails if:\n    {text}"
    code, output = _check_kpis(tmp_path, _kpis(middle))
    _assert_refused(code, output, "KPIs")
    _assert_names_only(output, "K2", "Fails if")


@pytest.mark.parametrize("text", C1_PLACEHOLDERS, ids=C1_IDS)
def test_a_placeholder_behaviour_is_refused_naming_the_kpi(tmp_path, text):
    middle = _kpi(2, text, s.CLEAN_KPIS[1][1])
    code, output = _check_kpis(tmp_path, _kpis(middle))
    _assert_refused(code, output, "KPIs")
    _assert_names_only(output, "K2", "behaviour")


@pytest.mark.parametrize("n", [1, 2, 3], ids=["first KPI", "middle KPI", "last KPI"])
def test_a_behaviour_of_tbd_is_refused_naming_each_kpi_it_is_planted_in(tmp_path, n):
    code, output = _check_kpis(tmp_path, _kpis_with(n, _kpi(n, "TBD", s.CLEAN_KPIS[n - 1][1])))
    _assert_refused(code, output, "KPIs")
    _assert_names_only(output, f"K{n}", "behaviour")


@pytest.mark.parametrize("n", [1, 2, 3], ids=["first KPI", "middle KPI", "last KPI"])
def test_an_empty_behaviour_before_the_fails_if_line_is_refused_naming_the_kpi(tmp_path, n):
    code, output = _check_kpis(tmp_path, _kpis_with(n, _kpi(n, "", s.CLEAN_KPIS[n - 1][1])))
    _assert_refused(code, output, "KPIs")
    _assert_names_only(output, f"K{n}", "behaviour")


def test_a_placeholder_behaviour_and_a_placeholder_failure_text_are_each_named(tmp_path):
    kpis = "\n".join([_kpi(1, s.CLEAN_KPIS[0][0], "TBD"), s.clean_kpi(2), _kpi(3, "n/a", s.CLEAN_KPIS[2][1])])
    code, output = _check_kpis(tmp_path, kpis)
    _assert_refused(code, output, "KPIs")
    assert _names(output, "K1", "Fails if"), f"K1's missing Fails if: is not named: {_kpi_lines(output)}"
    assert _names(output, "K3", "behaviour"), f"K3's missing behaviour is not named: {_kpi_lines(output)}"
    assert not any("K2" in line for line in _kpi_lines(output)), f"the clean K2 was named: {_kpi_lines(output)}"


# controls (green at the head): a behaviour on the next line, a failure text on the next line, a placeholder word in a
# sentence
@pytest.mark.parametrize("n", [1, 2, 3], ids=["first KPI", "middle KPI", "last KPI"])
def test_a_behaviour_on_the_indented_line_after_the_kpi_id_passes(tmp_path, n):
    behaviour, fails = s.CLEAN_KPIS[n - 1]
    block = f"- K{n}:\n  {behaviour}\n  Fails if: {fails}"
    code, output = _check_kpis(tmp_path, _kpis_with(n, block))
    _assert_clean(code, output)


def test_a_failure_text_on_the_next_indented_line_passes(tmp_path):
    middle = f"- K2: {s.CLEAN_KPIS[1][0]}\n  Fails if:\n    the member sees a blank page or the sign-up form again."
    code, output = _check_kpis(tmp_path, _kpis(middle))
    _assert_clean(code, output)


@pytest.mark.parametrize("text", ["the member sees none of the page.", "no page is shown.",
                                  "None of the members sees the page.", "Nadia sees a blank page.",
                                  "TBD or the form shows again.", "n/a is printed instead of the plan."],
                         ids=["none inside", "no page", "None of the", "a name", "TBD first", "n/a first"])
def test_a_sentence_with_a_placeholder_word_is_no_placeholder_failure_text(tmp_path, text):
    code, output = _check_kpis(tmp_path, _kpis(_kpi(2, s.CLEAN_KPIS[1][0], text)))
    _assert_clean(code, output)


@pytest.mark.parametrize("text", ["None of the members sees a blank page after sign-up.",
                                  "No page is shown to a member who is signed out.",
                                  "Nadia sees the welcome page after sign-up.",
                                  "NASA data is not shown to a member."],
                         ids=["None of the", "no page", "a name", "NASA"])
def test_a_sentence_with_a_placeholder_word_is_no_placeholder_behaviour(tmp_path, text):
    code, output = _check_kpis(tmp_path, _kpis(_kpi(2, text, s.CLEAN_KPIS[1][1])))
    _assert_clean(code, output)


# ==================================================================================================================
# C2: a line under ## KPIs that is no list item but starts with a KPI id
# ==================================================================================================================

LOOSE_LINES = {
    "a bare id and colon": "K2: The member sees it.",
    "a bold id and colon": "**K2:** The member sees it.",
    "an indented id and colon": "  K2: The member sees it.",
    "an id and a full stop": "K2. The member sees it.",
    "an id and a space": "K2 The member sees it.",
    "an id alone": "K2",
    "a star-emphasised id": "*K2* The member sees it.",
}


@pytest.mark.parametrize("form", sorted(LOOSE_LINES))
def test_a_line_that_starts_with_a_kpi_id_and_is_no_list_item_is_refused_naming_the_line(tmp_path, form):
    code, output = _check_kpis(tmp_path, _kpis(LOOSE_LINES[form]))
    _assert_refused(code, output, "KPIs")
    assert any("K2" in line for line in _kpi_lines(output)), (
        f"no REFUSED KPIs line carries 'K2' (the line's id): {_kpi_lines(output)}")


@pytest.mark.parametrize("form", ["a bare id and colon", "a bold id and colon", "an indented id and colon",
                                  "an id and a full stop"])
def test_a_line_that_starts_with_a_kpi_id_is_refused_when_it_is_the_last_line_of_the_part(tmp_path, form):
    code, output = _check_kpis(tmp_path, "\n".join([s.clean_kpi(1), s.clean_kpi(2), s.clean_kpi(3), LOOSE_LINES[form]]))
    _assert_refused(code, output, "KPIs")
    assert any("K2" in line for line in _kpi_lines(output)), _kpi_lines(output)


@pytest.mark.parametrize("form", ["a bare id and colon", "an indented id and colon"])
def test_a_line_that_starts_with_a_kpi_id_is_refused_between_a_kpi_line_and_its_fails_if_line(tmp_path, form):
    behaviour, fails = s.CLEAN_KPIS[0]
    first = f"- K1: {behaviour}\n{LOOSE_LINES[form]}\n  Fails if: {fails}"
    code, output = _check_kpis(tmp_path, "\n".join([first, s.clean_kpi(3)]))
    _assert_refused(code, output, "KPIs")
    assert any("K2" in line for line in _kpi_lines(output)), _kpi_lines(output)


@pytest.mark.parametrize("line", ["K2: The member sees send_welcome() after sign-up.",
                                  "**K2:** The member sees plan_name after sign-up.",
                                  "  K2: The member sees `settings` after sign-up."],
                         ids=["a call", "a snake_case identifier", "a code span"])
def test_a_kpi_id_line_is_not_read_as_part_of_the_kpi_before_it(tmp_path, line):
    code, output = _check_kpis(tmp_path, _kpis(line))
    _assert_refused(code, output, "KPIs")
    assert any("K2" in found for found in _kpi_lines(output)), f"the line is not quoted: {_kpi_lines(output)}"
    assert not any("K1" in found and "code" in found.lower() for found in _kpi_lines(output)), (
        f"the code in the K2 line was named under K1: {_kpi_lines(output)}")


# controls (green at the head)
@pytest.mark.parametrize("lead", ["Key results follow.", "Key results follow.\n"],
                         ids=["prose line directly above", "prose line and a blank line"])
def test_a_prose_line_that_starts_with_a_k_before_the_first_kpi_is_allowed(tmp_path, lead):
    code, output = _check_kpis(tmp_path, lead + "\n" + _kpis(s.clean_kpi(2)))
    _assert_clean(code, output)


@pytest.mark.parametrize("line", ["Kiosk members see it too.", "K2nd place is shown too."], ids=["Kiosk", "K2nd"])
@pytest.mark.parametrize("where", ["after the behaviour", "after the Fails if line"])
def test_a_continuation_line_that_starts_with_a_k_but_no_id_passes(tmp_path, line, where):
    behaviour, fails = s.CLEAN_KPIS[1]
    if where == "after the behaviour":
        middle = f"- K2: {behaviour}\n{line}\n  Fails if: {fails}"
    else:
        middle = f"- K2: {behaviour}\n  Fails if: {fails}\n{line}"
    code, output = _check_kpis(tmp_path, _kpis(middle))
    _assert_clean(code, output)


# ==================================================================================================================
# C3: an owner, source or licence-or-recipe cell that is a placeholder, or says no licence was found
# ==================================================================================================================

def _test_data(tmp_path, rows):
    code, output, _ = s.check(tmp_path, rows=rows)
    return code, output


def _data_lines(output):
    return [line.lower() for line in s.refused(output, "Test data")]


def _one_row(index, **changes):
    rows = [dict(r) for r in s.CLEAN_ROWS]
    rows[index].update(changes)
    return tuple(rows)


# the cell, the row it is planted in, the item word the refusal names, and whether the source name is in the line
CELLS = {
    "owner": (0, "owner", "owner", True),
    "source": (0, "source", "source", False),
    "licence": (0, "licence or recipe", "licence", True),
    "recipe": (1, "licence or recipe", "recipe", True),
}


def _assert_cell_refused(tmp_path, cell, text):
    index, column, word, named_by_source = CELLS[cell]
    code, output = _test_data(tmp_path, _one_row(index, **{column: text}))
    _assert_refused(code, output, "Test data")
    lines = _data_lines(output)
    assert any(word in line for line in lines), f"no REFUSED Test data line names the {word}: {output!r}"
    if named_by_source:
        source = s.CLEAN_ROWS[index]["source"].lower()
        assert any(source in line and word in line for line in lines), (
            f"no REFUSED Test data line names the source {source!r} and the {word}: {output!r}")
    other = s.CLEAN_ROWS[1 - index]["source"].lower()
    assert not any(other in line for line in lines), f"the clean row {other!r} was named: {output!r}"


# the nine examples of the behaviour first, then the rest of the class as it is worded
C3_PLACEHOLDERS = ["TBC", "Tbd.", "N/A.", "NA", "nobody", "to be decided", "`TBD`", "...", "<owner>",
                   "…", "TBA", "pending", "no one", "nil", "null", "(none)", "to be confirmed", "to be written",
                   "[TBD]", "TBD;", "<licence>", "<behaviour>"]


@pytest.mark.parametrize("cell", sorted(CELLS))
@pytest.mark.parametrize("text", C3_PLACEHOLDERS, ids=[f"ph{n}" for n in range(len(C3_PLACEHOLDERS))])
def test_a_placeholder_cell_of_the_class_is_refused_as_if_it_were_empty(tmp_path, cell, text):
    _assert_cell_refused(tmp_path, cell, text)


# the words that say no licence was found, in the licence or recipe cell of an imported row and of a synthetic row
NO_LICENCE = ["unlicensed", "unlicenced", "none found", "not found", "no licence", "no license"]


@pytest.mark.parametrize("cell", ["licence", "recipe"])
@pytest.mark.parametrize("text", NO_LICENCE, ids=[f"nl{n}" for n in range(len(NO_LICENCE))])
def test_a_licence_or_recipe_cell_that_says_no_licence_was_found_is_refused_as_if_it_were_empty(tmp_path, cell, text):
    _assert_cell_refused(tmp_path, cell, text)


def test_an_owner_and_a_licence_that_are_placeholders_are_each_named(tmp_path):
    code, output = _test_data(tmp_path, _one_row(0, owner="TBC", **{"licence or recipe": "unlicensed"}))
    _assert_refused(code, output, "Test data")
    source = s.CLEAN_ROWS[0]["source"].lower()
    lines = _data_lines(output)
    assert any(source in line and "owner" in line for line in lines), f"the owner is not named: {output!r}"
    assert any(source in line and "licence" in line for line in lines), f"the licence is not named: {output!r}"


def test_a_placeholder_owner_in_one_row_does_not_name_the_other_row(tmp_path):
    code, output = _test_data(tmp_path, _one_row(1, owner="N/A."))
    _assert_refused(code, output, "Test data")
    other = s.CLEAN_ROWS[0]["source"].lower()
    assert not any(other in line for line in _data_lines(output)), f"the clean row {other!r} was named: {output!r}"


# controls (green at the head): real owners, licences and recipes; privacy and secrets are unchanged
@pytest.mark.parametrize("owner", ["Data team", "NASA data office", "Nadia (QA)", "Nadia"],
                         ids=["a team", "NASA", "a name with a note", "a name"])
def test_a_real_owner_that_starts_like_a_placeholder_passes(tmp_path, owner):
    code, output = _test_data(tmp_path, _one_row(0, owner=owner))
    _assert_clean(code, output)


@pytest.mark.parametrize("licence", ["MIT", "CC-BY-4.0", "Apache-2.0"])
def test_a_named_licence_passes(tmp_path, licence):
    code, output = _test_data(tmp_path, _one_row(0, **{"licence or recipe": licence}))
    _assert_clean(code, output)


def test_a_recipe_in_words_passes(tmp_path):
    rows = _one_row(1, **{"licence or recipe": "two questions per topic, written by hand and reviewed by a second person"})
    code, output = _test_data(tmp_path, rows)
    _assert_clean(code, output)


@pytest.mark.parametrize("column", ["privacy", "secrets"])
@pytest.mark.parametrize("text", ["none", "N/A", "TBC", "unknown", "nobody"], ids=["none", "n/a", "tbc", "unknown", "nobody"])
@pytest.mark.parametrize("index", [0, 1], ids=["imported row", "synthetic row"])
def test_any_stated_text_passes_in_the_privacy_and_secrets_cells(tmp_path, index, column, text):
    code, output = _test_data(tmp_path, _one_row(index, **{column: text}))
    _assert_clean(code, output)


@pytest.mark.parametrize("column", ["privacy", "secrets"])
def test_an_empty_privacy_or_secrets_cell_is_still_refused(tmp_path, column):
    code, output = _test_data(tmp_path, _one_row(0, **{column: ""}))
    _assert_refused(code, output, "Test data")
    assert any(column in line for line in _data_lines(output)), f"the {column} cell is not named: {output!r}"
