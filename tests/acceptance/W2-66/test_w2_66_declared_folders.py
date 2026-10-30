"""Part 1, KPI 1 and KPI 6: a ticket's suite is its declared acceptance folder.

A ticket file may declare its acceptance folder in ``acceptance_tests.path`` (DEC-892; W2-67, W2-63 and W2-70
declare ``tests/acceptance/W1-27/``, ``W1-49/`` and ``W1-05/``), as W2-07's gate reads it; without one it is
``tests/acceptance/<wbs_id>/``. The overlap rule selects that folder, and the closing ticket's own suite is that
folder (README, "Interface", item 3). From the FULL review of 9174e358. README, "Part 1".
"""

import w2_66_support as support

# W1-dd's folder (gizmo; not reached by a widget change) is the folder the ticket of each case declares.
DECLARED_WBS = "W1-dd"
DECLARED = support.suite_of(DECLARED_WBS)
# A Wave 2 ticket whose paths hold the widget and whose declared folder is a Wave 1 folder: it has no folder of
# its own WBS id.
QQ_TICKET, QQ_WBS = "PROJ-qqqq", "W2-qq"


def _all_selected_exist(fixture, evidence):
    missing = [entry.get("target") for entry in evidence.get("selected") or []
               if not (fixture.root / str(entry.get("target", "")).split("::")[0]).exists()]
    assert not missing, f"the evidence names selected targets that do not exist: {missing}"


def _the_closed_ticket_declaring(fixture, folder):
    """The closed ticket's file, its ``acceptance_tests.path`` changed from its WBS id's folder to ``folder``."""
    rel = support.close_support.ticket_path(support.TICKET)
    text = (fixture.root / rel).read_text(encoding="utf-8")
    old = f"  path: {support.suite_of(support.WBS)}/"
    assert old in text, f"the fixture is wrong: {rel} does not declare {old.strip()}"
    return {rel: text.replace(old, f"  path: {folder}/")}


def test_the_overlap_rule_selects_a_ticket_s_declared_folder(fixture, sandbox):
    """W2-qq's paths hold the changed widget; it declares W1-dd's folder (another wave's), and
    ``tests/acceptance/W2-qq/`` does not exist. W1-dd's folder runs, named with ``OVERLAP`` and W2-qq's ticket."""
    fixture.record_commit({support.close_support.ticket_path(QQ_TICKET): support.close_support.ticket_text(
        QQ_TICKET, QQ_WBS, allowed_paths=[support.WIDGET], status="closed", acceptance=f"{DECLARED}/")},
        "a closed ticket that declares another wave's acceptance folder")
    assert not (fixture.root / support.suite_of(QQ_WBS)).exists(), "the fixture is wrong: W2-qq has a folder"
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    evidence = support.evidence_of(run)
    assert evidence.get("scope") == support.SCOPED, f"a one-module change is not a scoped run: {evidence}"
    why = [w for w in support.selected_for(evidence, DECLARED) if w["reason"] == support.OVERLAP]
    assert any(w.get("ticket") == QQ_TICKET and support.WIDGET in (w.get("paths") or []) for w in why), \
        (f"{DECLARED}, the folder {QQ_TICKET} declares, is not selected with {support.OVERLAP} naming the ticket "
         f"and {support.WIDGET}: selected {evidence.get('selected')}")
    assert fixture.ran(support.case_of(DECLARED_WBS)), f"{DECLARED}, the declared folder, did not run"
    assert not support.suite_named_left_out(fixture, evidence, DECLARED_WBS), \
        f"{DECLARED} is named left out though it is selected: {evidence.get('left_out')}"
    _all_selected_exist(fixture, evidence)


def test_the_own_suite_is_the_closing_ticket_s_declared_folder(fixture, sandbox):
    """The closed ticket declares W1-dd's folder (as W2-67 declares W1-27's): ``selected`` names that folder with
    ``OWN``, it runs, and none of its files is in ``left_out``."""
    fixture.record_commit(_the_closed_ticket_declaring(fixture, DECLARED),
                          "the closed ticket declares another wave's acceptance folder")
    assert support.close_support.read_ticket_frontmatter(fixture.root, support.TICKET)["acceptance_tests"]["path"] \
        == f"{DECLARED}/", "the fixture is wrong: the ticket does not declare the folder"
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    evidence = support.evidence_of(run)
    why = {w["reason"] for w in support.selected_for(evidence, DECLARED)}
    assert support.OWN in why, \
        f"the declared folder {DECLARED} is not named with {support.OWN}: selected {evidence.get('selected')}"
    assert fixture.ran(support.case_of(DECLARED_WBS)), f"the declared folder {DECLARED} did not run"
    files = sorted(p.relative_to(fixture.root).as_posix() for p in (fixture.root / DECLARED).rglob("test_*.py"))
    assert files, "the fixture is wrong: the declared folder holds no test file"
    named = [entry.get("target") for entry in evidence.get("left_out") or []
             if support.within(str(entry.get("target", "")), DECLARED)
             or any(support.covers(str(entry.get("target", "")), rel) for rel in files)]
    assert not named, f"the own suite's files are named left out, though the acceptance run runs it whole: {named}"
    _all_selected_exist(fixture, evidence)
