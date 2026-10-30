"""Part 5, KPI 14 (DEC-912 item 3, P1) and failure line 1: a selected test-map target that cannot be resolved at the
head widens the run to the full regression.

A record-reading or every-close target is selected on every close; a coupling's targets are selected when its
``paths`` match a changed path. A selected target resolves when the tree closed holds it: its file is there and,
for a node id, its file holds the case the id names or begins. One that does not (its file or test function
renamed or gone) would run nothing while the renamed case or file is left out, so a red it would catch passes the
close: the close runs the full regression instead, and ``why_full`` names the target, as the map names it, with
``UNRESOLVED_TARGET`` and why (``FILE_GONE``, ``CASE_GONE``). A coupling the change does not reach is not selected:
its gone target widens nothing. A target that resolves changes nothing (README, "Interface", items 3 and 6). From
the second FULL review (DEC-136). README, "Part 5".
"""

import json

import pytest

import w2_66_support as support

RR_CASE = "test_rr_reads_the_register"
RR_NODE = f"{support.RR_RECORDS}::{RR_CASE}"
# Renamed by W1-rr's test designer: a new name, and a longer one that the old node id begins as text but not at a
# node id's boundary (``::``, ``[``), so it is not the old id's case.
RR_RENAMED = {"renamed": "test_rr_checks_the_register", "renamed-longer": "test_rr_reads_the_register_again"}

EC_RENAMED = "tests/acceptance/W1-ec/test_ec_terms.py"
CP_FILE = support.node_of("W1-cp").split("::")[0]
CP_RENAMED = "tests/acceptance/W1-cp/test_cp_text.py"
CP_CASE = support.case_of("W1-cp")


def _map(**keys):
    return {**support.DEFAULT_TEST_MAP, **keys}


def _coupled_to(target):
    return [{"paths": [support.COUPLED_INPUT], "suites": [target], "why": "W1-cp's test file reads it as text"}]


def _rr_renamed_text(fixture, new_name):
    """W1-rr's record-reading file with its case renamed: the same file, the same body."""
    text = support.project_files(fixture.told)[support.RR_RECORDS]
    assert f"def {RR_CASE}(" in text, f"the fixture is wrong: {support.RR_RECORDS} does not define {RR_CASE}"
    return text.replace(f"def {RR_CASE}(", f"def {new_name}(")


def _rename_rr_case_at_the_base(fixture, new_name):
    """W1-rr's test designer renames the case the map names; a green night after it is the base."""
    return fixture.based({support.RR_RECORDS: _rr_renamed_text(fixture, new_name)},
                         "W1-rr's test designer renames its record-reading case")


def _move_at_the_base(fixture, old, new, body=None):
    """A test file renamed in its folder by its suite's test designer (its text unchanged, or ``body`` after the
    move); a green night after it is the base."""
    fixture.moved(old, new, "the suite's test designer renames a test file")
    if body is not None:
        fixture.merged({new: body}, "the renamed file's case, revised")
    base = fixture.head()
    fixture.plant_green_night(base)
    assert not (fixture.root / old).exists() and (fixture.root / new).is_file(), "the fixture is wrong: the move"
    return base


def _unresolved(evidence, target):
    """The ``why_full`` entries that name ``target`` with ``UNRESOLVED_TARGET``."""
    why = evidence.get("why_full")
    assert isinstance(why, list), \
        f"the evidence gives no why_full: scope {evidence.get('scope')!r}, why_full {evidence.get('why_full')!r}"
    return [w for w in why if isinstance(w, dict) and w.get("reason") == support.UNRESOLVED_TARGET
            and w.get("target") == target]


def _assert_unresolved(evidence, target, detail):
    named = _unresolved(evidence, target)
    assert named, (f"the full run does not name {target} with {support.UNRESOLVED_TARGET}: "
                   f"why_full {evidence.get('why_full')!r}")
    assert any(w.get("detail") == detail for w in named), \
        f"{target} is named without why it does not resolve ({detail}): {named}"


def _assert_widened(run, fixture, target, detail):
    """The close ran the full regression (every suite ran, nothing left out) and named the target and why."""
    evidence = support.assert_full(run, fixture, support.UNRESOLVED_TARGET)
    _assert_unresolved(evidence, target, detail)
    return evidence


# --------------------------------------------------------------------------
# A selected target renamed: the full regression, the target named with why
# --------------------------------------------------------------------------

@pytest.mark.parametrize("renamed", sorted(RR_RENAMED))
def test_a_renamed_record_reading_case_widens_the_run_to_the_full_regression(make_fixture, sandbox, renamed):
    """The map names one case of W1-rr by its node id; W1-rr's test designer renames the function (the file stays).
    The base is green after the rename; then the ticket's ordinary one-module change."""
    fixture = make_fixture(test_map=_map(record_reading=[RR_NODE]))
    _rename_rr_case_at_the_base(fixture, RR_RENAMED[renamed])
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    _assert_widened(run, fixture, RR_NODE, support.CASE_GONE)
    assert fixture.ran(RR_RENAMED[renamed]), f"the renamed case {RR_RENAMED[renamed]} did not run in the full run"


def test_a_renamed_every_close_file_widens_the_run_to_the_full_regression(fixture, sandbox):
    """The map's every-close list names W1-ec's contract file; it is renamed in its folder. The base is green
    after the rename; then the ticket's ordinary one-module change."""
    _move_at_the_base(fixture, support.EC_CONTRACT, EC_RENAMED)
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    _assert_widened(run, fixture, support.EC_CONTRACT, support.FILE_GONE)
    assert fixture.ran("test_ec_contract"), f"the renamed every-close file {EC_RENAMED} did not run"


def test_a_renamed_coupling_target_widens_the_run_to_the_full_regression(make_fixture, sandbox):
    """The map couples ``src/gov/textread/data.txt`` to W1-cp's test file; the file is renamed. The base is green
    after the rename; then the change touches the coupled path, and the ticket's ordinary one-module change."""
    fixture = make_fixture(test_map=_map(couplings=_coupled_to(CP_FILE)))
    _move_at_the_base(fixture, CP_FILE, CP_RENAMED)
    fixture.merged({support.COUPLED_INPUT: "data, changed\n"})
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    _assert_widened(run, fixture, CP_FILE, support.FILE_GONE)
    assert fixture.ran(CP_CASE), f"the renamed coupled file {CP_RENAMED} did not run"


# --------------------------------------------------------------------------
# The effect on the outcome: the red the renamed case or file catches refuses the close
# --------------------------------------------------------------------------

def _failing(evidence, node):
    return [f for f in evidence.get("failures") or [] if isinstance(f, dict)
            and support.covers(node, str(f.get("test")))]


def test_a_red_the_renamed_record_reading_case_catches_refuses_the_close(make_fixture, sandbox):
    """Failure line 3 through a renamed target: a record-only commit breaks the register; the renamed record-reading
    case catches it. Only a run that reaches the renamed case (the full regression) refuses the close; a run that
    selects the old node id runs nothing of W1-rr and passes."""
    renamed = RR_RENAMED["renamed"]
    fixture = make_fixture(test_map=_map(record_reading=[RR_NODE]))
    _rename_rr_case_at_the_base(fixture, renamed)
    fixture.record_commit({support.REGISTER_REL: f"# The decision register\n\n{support.BROKEN}\n"})
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    evidence = support.evidence_of(run)
    assert fixture.ran(renamed), (f"the renamed record-reading case {renamed} did not run: the close passed a red "
                                  f"it would catch (scope {evidence.get('scope')!r})")
    error = support.refused(run)
    assert evidence.get("scope") == support.FULL, f"the refused close is not stated full: {evidence.get('scope')!r}"
    _assert_unresolved(evidence, RR_NODE, support.CASE_GONE)
    failing = _failing(evidence, f"{support.RR_RECORDS}::{renamed}")
    assert failing, f"the renamed case is not among the failures: {evidence.get('failures')}\n{error}"
    assert support.BROKEN in str(failing[0].get("text")), f"the failure text is not kept: {failing[0]}"


def test_a_red_the_renamed_coupled_file_catches_refuses_the_close(make_fixture, sandbox):
    """W1-cp's coupled file reads ``src/gov/textread/data.txt``; it is renamed at the base, and the change breaks
    the data. Only a run that reaches the renamed file (the full regression) refuses the close."""
    body = (f"text = open({support.COUPLED_INPUT!r}, encoding='utf-8').read()\n"
            f"    assert {support.BROKEN!r} not in text, 'the coupled data is broken: ' + text")
    fixture = make_fixture(test_map=_map(couplings=_coupled_to(CP_FILE)))
    _move_at_the_base(fixture, CP_FILE, CP_RENAMED, body=support._telling(CP_CASE, fixture.told, body=body))
    fixture.merged({support.COUPLED_INPUT: f"data, {support.BROKEN}\n"})
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    evidence = support.evidence_of(run)
    assert fixture.ran(CP_CASE), (f"the renamed coupled file {CP_RENAMED} did not run: the close passed a red it "
                                  f"would catch (scope {evidence.get('scope')!r})")
    error = support.refused(run)
    assert evidence.get("scope") == support.FULL, f"the refused close is not stated full: {evidence.get('scope')!r}"
    _assert_unresolved(evidence, CP_FILE, support.FILE_GONE)
    failing = _failing(evidence, f"{CP_RENAMED}::{CP_CASE}")
    assert failing, f"the renamed coupled file's case is not among the failures: {evidence.get('failures')}\n{error}"
    assert support.BROKEN in str(failing[0].get("text")), f"the failure text is not kept: {failing[0]}"


# --------------------------------------------------------------------------
# Only selected targets count; a target that resolves changes nothing
# --------------------------------------------------------------------------

def test_a_gone_coupling_target_the_change_does_not_reach_widens_nothing(make_fixture, sandbox):
    """The coupling's target is renamed at the base, but no changed path matches the coupling's ``paths``: the
    coupling is not selected, and the close stays scoped (the KPI line's *selected* target)."""
    fixture = make_fixture(test_map=_map(couplings=_coupled_to(CP_FILE)))
    _move_at_the_base(fixture, CP_FILE, CP_RENAMED)
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    evidence = support.evidence_of(run)
    assert support.COUPLED_INPUT not in (evidence.get("changed") or []), "the fixture is wrong: the coupled path"
    assert evidence.get("scope") == support.SCOPED, \
        f"a coupling the change does not reach widened the run: scope {evidence.get('scope')!r}, " \
        f"why_full {evidence.get('why_full')!r}"
    assert not _unresolved({"why_full": evidence.get("why_full") or []}, CP_FILE), \
        f"a target no change selects is named unresolved: {evidence.get('why_full')!r}"
    assert not support.selected_for(evidence, CP_FILE), \
        f"the coupling's target is named selected though no changed path reaches it: {evidence.get('selected')}"
    assert not fixture.ran(CP_CASE), "W1-cp ran, though nothing of the change reaches it"


FORMS = "tests/acceptance/W1-ec/test_ec_forms.py"
FORMS_METHOD = f"{FORMS}::TestForms::test_forms_method"         # a class's method
FORMS_PARAM = f"{FORMS}::test_forms_param[two]"                  # one parameter set of a parametrised case
FORMS_GROUPED = f"{FORMS}::test_forms_grouped"                   # a parametrised case, named by its beginning
FORMS_CLASS = f"{FORMS}::TestShapes"                             # a class, named by its beginning


def _forms_text(told):
    """A W1-ec file whose cases are a class's methods and parametrised functions; each tells how it ran, as W1-30's
    telling test does (the told file is named as the case is in its node id)."""
    tell = (
        "def _tell():\n"
        "    case = os.environ['PYTEST_CURRENT_TEST'].split('::')[-1].split(' ')[0]\n"
        f"    with open(os.path.join({str(told)!r}, case), 'a', encoding='utf-8') as told:\n"
        f"        told.write(os.environ.get({support.close_support.WORKER_VARIABLE!r}, "
        f"{support.close_support.NO_WORKER!r}) + ' ' + repr(time.time()) + '\\n')\n"
    )
    return ("import os\nimport time\n\nimport pytest\n\n\n" + tell + "\n\n"
            "class TestForms:\n"
            "    def test_forms_method(self):\n        _tell()\n\n"
            "    def test_forms_other_method(self):\n        _tell()\n\n\n"
            "class TestShapes:\n"
            "    def test_shapes_square(self):\n        _tell()\n\n\n"
            "@pytest.mark.parametrize('form', ['one', 'two'])\n"
            "def test_forms_param(form):\n    _tell()\n\n\n"
            "@pytest.mark.parametrize('group', ['a', 'b'])\n"
            "def test_forms_grouped(group):\n    _tell()\n")


def test_selected_targets_that_resolve_change_nothing(make_fixture, sandbox):
    """Node ids the existing interface reads (a node id or its beginning): a class's method, one parameter set of
    a parametrised case, a parametrised case by its function, a class by its name. Each resolves: the close stays
    scoped, names none unresolved, and runs each."""
    fixture = make_fixture(test_map=_map(every_close=[support.EC_CONTRACT, FORMS_METHOD, FORMS_PARAM],
                                         record_reading=[support.RR_RECORDS, FORMS_GROUPED, FORMS_CLASS]))
    fixture.based({FORMS: _forms_text(fixture.told)}, "W1-ec's file of class and parametrised cases")
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    evidence = support.evidence_of(run)
    unresolved = [w for w in evidence.get("why_full") or []
                  if isinstance(w, dict) and w.get("reason") == support.UNRESOLVED_TARGET]
    assert not unresolved, f"targets that resolve are named unresolved: {json.dumps(unresolved)}"
    assert evidence.get("scope") == support.SCOPED, \
        f"targets that resolve widened the run: scope {evidence.get('scope')!r}, why_full {evidence.get('why_full')!r}"
    for case in ("test_forms_method", "test_forms_param[two]", "test_forms_grouped[a]", "test_forms_grouped[b]",
                 "test_shapes_square"):
        assert fixture.ran(case), f"the selected case {case} did not run"
