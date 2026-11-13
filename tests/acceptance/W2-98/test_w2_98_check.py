"""W2-98: the skill's check on planted specs (I1, I3): success-1, success-2, success-3's check half, failure-1, failure-2.

Each case plants a spec in ``tmp_path`` in the nine-heading form of I2 and runs ``python3 <skill>/check_spec.py``.
It judges I3's words and exits only: a ``REFUSED <part>: <reason>`` line and exit 1; ``P1 Test data: <source> cannot
be secured``, the file ``<spec>.P1.md`` and exit 2; ``PASS`` and exit 0 only on a clean spec. A reason's own wording
is never fixed beyond the part's name, the KPI's id or the missing item's name.
"""
from __future__ import annotations

import pytest

import w2_98_support as s


def _assert_refused_only(code, output, part):
    assert code == 1, f"expected exit 1 for a refused spec, got {code}: {output!r}"
    assert s.refused(output, part), f"no 'REFUSED {part}: ...' line in: {output!r}"
    assert not s.passes(output), f"PASS printed beside a REFUSED line: {output!r}"


# success-1: the eight parts ---------------------------------------------------------------------------------------

def test_a_clean_spec_passes(tmp_path):
    code, output, _ = s.check(tmp_path)
    assert code == 0, f"a clean spec exited {code}: {output!r}"
    assert s.passes(output), f"no PASS line for a clean spec: {output!r}"
    assert not s.refused(output) and not s.p1_lines(output), f"a clean spec drew findings: {output!r}"


@pytest.mark.parametrize("part", s.HEADINGS)
def test_a_spec_that_leaves_a_part_out_is_refused_naming_the_part(tmp_path, part):
    code, output, _ = s.check(tmp_path, omit=(part,))
    _assert_refused_only(code, output, part)


def test_leaving_goals_out_is_not_hidden_by_the_non_goals_heading(tmp_path):
    code, output, _ = s.check(tmp_path, omit=("Goals",))
    _assert_refused_only(code, output, "Goals")
    assert not s.refused(output, "Non-goals"), f"Non-goals is present but was refused: {output!r}"


def test_leaving_the_parts_out_names_each_part_missing(tmp_path):
    code, output, _ = s.check(tmp_path, omit=("Problem", "Accepted by"))
    assert code == 1 and not s.passes(output), output
    assert s.refused(output, "Problem") and s.refused(output, "Accepted by"), (
        f"both missing parts are named, each on a REFUSED line: {output!r}")
    assert s.refused_parts(output) == ["Accepted by", "Problem"], f"only the two missing parts: {output!r}"


# failure-1 (and success-1): a KPI that names code, a KPI with no failure line ---------------------------------------

NAMES_CODE = {
    "a code span": "A member opens `settings` and sees the plan the account is on.",
    "a call, name(": "A member presses the button and checkout() returns the receipt page.",
    "a path with an extension": "The weekly summary is saved to data/summary.csv for the support team.",
    "a dotted identifier": "The welcome page shows user.profile with the plan the member chose.",
    "a snake_case identifier": "The welcome page shows plan_name for the member who just registered.",
}


@pytest.mark.parametrize("form", sorted(NAMES_CODE))
def test_a_kpi_that_names_code_is_refused_naming_the_kpi(tmp_path, form):
    kpis = (s.CLEAN_KPIS[0], (NAMES_CODE[form], "the page is blank."), s.CLEAN_KPIS[2])
    code, output, _ = s.check(tmp_path, kpis=kpis)
    _assert_refused_only(code, output, "KPIs")
    lines = s.refused(output, "KPIs")
    assert any("K2" in line for line in lines), f"no REFUSED KPIs line names K2: {lines}"
    assert not any(("K1" in line or "K3" in line) for line in lines), f"a clean KPI was named: {lines}"


def test_a_kpi_with_no_failure_line_is_refused_naming_the_kpi(tmp_path):
    kpis = (s.CLEAN_KPIS[0], (s.CLEAN_KPIS[1][0], None), s.CLEAN_KPIS[2])
    code, output, _ = s.check(tmp_path, kpis=kpis)
    _assert_refused_only(code, output, "KPIs")
    lines = s.refused(output, "KPIs")
    assert any("K2" in line for line in lines), f"no REFUSED KPIs line names K2: {lines}"
    assert not any(("K1" in line or "K3" in line) for line in lines), f"a clean KPI was named: {lines}"


def test_a_kpi_naming_a_function_and_a_kpi_with_no_failure_line_are_both_refused_and_named(tmp_path):
    kpis = (s.CLEAN_KPIS[0], ("The page is built when checkout() returns.", "the page is blank."),
            (s.CLEAN_KPIS[2][0], None))
    code, output, _ = s.check(tmp_path, kpis=kpis)
    _assert_refused_only(code, output, "KPIs")
    named = " ".join(s.refused(output, "KPIs"))
    assert "K2" in named and "K3" in named, f"K2 (names code) and K3 (no failure line) are both named: {named!r}"
    assert "K1" not in named, f"the clean K1 was named: {named!r}"
    assert not s.passes(output)


# success-2 and failure-2: the test data ----------------------------------------------------------------------------

def test_test_data_with_no_owner_is_refused_naming_the_missing_item(tmp_path):
    code, output, _ = s.check(tmp_path, rows=(s.row(owner=""), s.CLEAN_ROWS[1]))
    _assert_refused_only(code, output, "Test data")
    assert any("owner" in line.lower() for line in s.refused(output, "Test data")), (
        f"no REFUSED Test data line names the owner: {output!r}")


def test_an_imported_row_with_no_licence_is_refused_naming_the_licence(tmp_path):
    code, output, _ = s.check(tmp_path, rows=(s.row(**{"licence or recipe": ""}), s.CLEAN_ROWS[1]))
    _assert_refused_only(code, output, "Test data")
    assert any(("licence" in line.lower() or "recipe" in line.lower()) for line in s.refused(output, "Test data")), (
        f"no REFUSED Test data line names the licence or recipe: {output!r}")


def test_a_synthetic_row_with_no_recipe_is_refused_naming_the_recipe(tmp_path):
    code, output, _ = s.check(tmp_path, rows=(s.CLEAN_ROWS[0], dict(s.CLEAN_ROWS[1], **{"licence or recipe": ""})))
    _assert_refused_only(code, output, "Test data")
    assert any(("recipe" in line.lower() or "licence" in line.lower()) for line in s.refused(output, "Test data")), (
        f"no REFUSED Test data line names the recipe: {output!r}")


def test_a_row_with_no_source_is_refused_naming_the_source(tmp_path):
    code, output, _ = s.check(tmp_path, rows=(s.row(source=""), s.CLEAN_ROWS[1]))
    _assert_refused_only(code, output, "Test data")
    assert any("source" in line.lower() for line in s.refused(output, "Test data")), (
        f"no REFUSED Test data line names the source: {output!r}")


def test_a_clean_test_data_table_with_a_synthetic_row_and_no_hidden_half_passes(tmp_path):
    rows = (s.CLEAN_ROWS[0], dict(s.CLEAN_ROWS[1], **{"hidden half": "n/a"}))
    code, output, _ = s.check(tmp_path, rows=rows)
    assert code == 0 and s.passes(output) and not s.refused(output), (
        f"a row with source, owner, recipe and no hidden half (it does not measure) should pass: {code} {output!r}")


def _unsecured(tmp_path, source="scraped customer chats"):
    rows = (s.CLEAN_ROWS[0], s.row(source=source, secured="no"))
    return s.check(tmp_path, rows=rows)


def test_data_that_cannot_be_secured_gives_a_p1_line_exit_2_and_no_pass(tmp_path):
    code, output, _ = _unsecured(tmp_path)
    assert code == 2, f"expected exit 2 for data that cannot be secured, got {code}: {output!r}"
    assert "P1 Test data: scraped customer chats cannot be secured" in s.lines_of(output), (
        f"the P1 line is not printed in I3's words: {output!r}")
    assert not s.passes(output), f"PASS printed beside a P1 line: {output!r}"
    assert not s.refused(output), f"a spec that is only unsecurable was also refused: {output!r}"


def test_data_that_cannot_be_secured_writes_the_p1_package_beside_the_spec(tmp_path):
    code, output, path = _unsecured(tmp_path)
    candidates = [tmp_path / f"{path.name}.P1.md", tmp_path / f"{path.stem}.P1.md"]
    written = [p for p in candidates if p.is_file()]
    assert written, f"no <spec>.P1.md written beside the spec (looked for {[p.name for p in candidates]}): {output!r}"
    text = written[0].read_text(encoding="utf-8")
    assert "scraped customer chats" in text, "the P1 package does not name the source"
    assert "option" in text.lower() and "recommend" in text.lower(), (
        "the P1 package is not a package (options with their cost, a recommendation)")


def test_a_secured_spec_writes_no_p1_package(tmp_path):
    code, output, path = s.check(tmp_path)
    assert code == 0, f"a clean spec did not pass, so no P1 can be judged: {output!r}"
    assert not list(tmp_path.glob("*.P1.md")), "a P1 package was written for a spec with every source secured"


def test_a_spec_with_no_owner_and_one_unsecurable_source_is_not_passed(tmp_path):
    rows = (s.row(owner=""), s.row(source="scraped customer chats", secured="no"))
    code, output, _ = s.check(tmp_path, rows=rows)
    assert code in (1, 2), f"a spec with a refusal and a P1 exited {code}: {output!r}"
    assert s.refused(output, "Test data") and "P1 Test data: scraped customer chats cannot be secured" in (
        s.lines_of(output)), f"both the refusal and the P1 are printed: {output!r}"
    assert not s.passes(output)


# success-3 (the check half): one KPI naming a function plus one source with no owner fails exactly those two -------

def test_a_kpi_naming_a_function_and_a_source_with_no_owner_fail_exactly_those_two_items(tmp_path):
    kpis = (s.CLEAN_KPIS[0], ("The page is built when checkout() returns.", "the page is blank."), s.CLEAN_KPIS[2])
    rows = (s.CLEAN_ROWS[0], s.row(source="support chat exports", owner=""))
    code, output, _ = s.check(tmp_path, kpis=kpis, rows=rows)
    assert code == 1 and not s.passes(output) and not s.p1_lines(output), f"{code}: {output!r}"
    assert s.refused_parts(output) == ["KPIs", "Test data"], f"exactly the KPI and the data item fail: {output!r}"
    kpi_lines, data_lines = s.refused(output, "KPIs"), s.refused(output, "Test data")
    assert any("K2" in line for line in kpi_lines) and not any(("K1" in l or "K3" in l) for l in kpi_lines), kpi_lines
    assert any("owner" in line.lower() for line in data_lines), f"the data line does not name the owner: {data_lines}"


def test_a_clean_planted_spec_passes_every_item(tmp_path):
    code, output, _ = s.check(tmp_path)
    assert code == 0 and s.passes(output) and not s.refused(output) and not s.p1_lines(output), f"{code}: {output!r}"


# I3: the one rule that ties the lines together --------------------------------------------------------------------

@pytest.mark.parametrize("spec_args", [
    {"omit": ("Out of scope",)},
    {"kpis": (s.CLEAN_KPIS[0], (s.CLEAN_KPIS[1][0], None))},
    {"rows": (s.row(owner=""),)},
    {"rows": (s.row(secured="no"),)},
], ids=["a part left out", "a KPI with no failure line", "no owner", "cannot be secured"])
def test_pass_is_never_printed_beside_a_refusal_or_a_p1(tmp_path, spec_args):
    code, output, _ = s.check(tmp_path, **spec_args)
    assert code in (1, 2), f"a spec with a finding exited {code}: {output!r}"
    assert (s.refused(output) or s.p1_lines(output)), f"no finding line printed: {output!r}"
    assert not s.passes(output), f"PASS printed beside a finding: {output!r}"
