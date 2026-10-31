"""W2-64 KPI success 2: ``docs/imported/`` is left out of the schema check, as history, and the check says so by
name [DEC-844].

The planted record is the kind lens G's sweep found failing there (run G-4): a decision record whose id is no
decision id (``OWNER-AMENDMENT-P2-0010`` against ``^(ADR|DEC)-[0-9]{3,}$``).
"""

from __future__ import annotations

import pytest

import w2_64_support as S

IMPORTED_REL = "docs/imported/owner-amendments/OWNER-AMENDMENT-P2-0010.md"
VALID_REL = ".tickets/PROJ-aaaa.md"


def _refused_decision():
    return S.markdown(S.shared("OWNER-AMENDMENT-P2-0010", "decision", title="An imported amendment"))


def _project(tmp_path, records):
    project = S.Project(S.Place(tmp_path).real_tool()).kernel_schemas().registry()
    for rel, text in records.items():
        project.write(rel, text)
    return project


def test_a_refused_record_under_docs_imported_does_not_fail_and_is_named_as_history(tmp_path):
    """*Red.* A record its schema refuses, under ``docs/imported/``, beside a valid ticket: core-schema exits 0 with
    no finding, and prints the success form ``{"ok": true, "result": ...}`` whose result names ``docs/imported/``
    as left out and why (history, DEC-844). Today: exit 0 and nothing printed."""
    run = _project(tmp_path, {IMPORTED_REL: _refused_decision(), VALID_REL: S.ticket()}).core_schema()
    assert run.code == 0 and run.findings == [], f"a record under {S.IMPORTED} fails the check\n{run.describe()}"
    assert isinstance(run.output, dict) and run.output.get("ok") is True and "result" in run.output, \
        f"core-schema does not print the success form on a pass\n{run.describe()}"
    assert S.says_imported_left_out(run.output["result"]), \
        f"the result does not name {S.IMPORTED} as left out, as history (DEC-844)\n{run.describe()}"


def test_the_pass_counts_the_records_validated(tmp_path):
    """*Red.* The success form's result gives the count of records validated: two records outside
    ``docs/imported/``, one inside, and the number 2 is in the result. Today: nothing printed."""
    records = {IMPORTED_REL: _refused_decision(), VALID_REL: S.ticket(),
               ".tickets/PROJ-cccc.md": S.ticket(id="PROJ-cccc")}
    run = _project(tmp_path, records).core_schema()
    assert run.code == 0, run.describe()
    result = run.output.get("result") if isinstance(run.output, dict) else None
    assert result is not None and 2 in set(S.integers_in(result)), \
        f"the result gives no count of 2 records validated\n{run.describe()}"


def test_the_refusal_also_names_docs_imported_as_left_out(tmp_path):
    """*Red.* When another record is refused, the output holds the findings and, beside them, the same statement
    that ``docs/imported/`` is left out as history; nothing under ``docs/imported/`` is a finding. Today: a list of
    findings and no statement (and the subset passes the fault)."""
    run = _project(tmp_path, {IMPORTED_REL: _refused_decision(),
                              VALID_REL: S.ticket(state_class="NOT-A-CLASS")}).core_schema()
    assert run.code != 0 and S.about(run.findings, VALID_REL), run.describe()
    assert not [f for f in run.findings if S.IMPORTED in str(f.get("path", ""))], run.describe()
    assert isinstance(run.output, dict) and isinstance(run.output.get("findings"), list), \
        f"the refusal is not printed as {{\"findings\": [...], ...}}\n{run.describe()}"
    beside = {key: value for key, value in run.output.items() if key != "findings"}
    assert S.says_imported_left_out(beside), \
        f"beside the findings, nothing names {S.IMPORTED} as left out, as history\n{run.describe()}"


@pytest.mark.parametrize("rel", (
    "docs/adr/OWNER-AMENDMENT-P2-0010.md",
    "docs/imported-notes/OWNER-AMENDMENT-P2-0010.md",
    "docs/plan/imported/OWNER-AMENDMENT-P2-0010.md",
))
def test_the_same_record_anywhere_else_fails(tmp_path, rel):
    """*Red.* No other folder is left out: the same record outside ``docs/imported/`` (in ``docs/adr/``, in a folder
    whose name only begins with ``imported``, in an ``imported`` folder elsewhere) is refused, naming its path and
    ``id``. Today: no finding (the subset does not check the id's grammar)."""
    run = _project(tmp_path, {rel: _refused_decision()}).core_schema()
    assert run.code != 0, f"a refused record at {rel} passes\n{run.describe()}"
    assert [f for f in S.about(run.findings, rel) if f.get("field") == "id"], \
        f"no finding on {rel} names 'id'\n{run.describe()}"
