"""S2: a check that exits 0 with findings, or with "unmeasured" in its result, is not green [W2-M129, W2-M212].

Planted checks run by ``gov check --json`` in a temporary project (Interface item 4): a check is GREEN only when
it exits 0 with no finding; the findings of an exit 0 come from a non-empty ``findings`` of the success form, from
a JSON mapping with ``"unmeasured": true`` (code ``CHECK_UNMEASURED``, with its ``reason``) and from non-JSON
output holding the word "unmeasured" (``CHECK_UNMEASURED``). Status from findings: RED if hard-block, YELLOW if
warning.
"""

from __future__ import annotations

import w2_45_support as support
from w2_45_support import GREEN, HARD_BLOCK, RED, WARNING, YELLOW

FINDING_LIST = (
    "import json, sys\n"
    "print(json.dumps([{'code': 'PLANTED_FINDING', 'message': 'a finding of the planted check'}]))\n"
    "sys.exit(0)\n"
)
FINDING_IN_SUCCESS_FORM = (
    "import json, sys\n"
    "print(json.dumps({'ok': True, 'result': {'findings': [{'code': 'PLANTED_FINDING', 'message': 'in the result'}]}}))\n"
    "sys.exit(0)\n"
)
UNMEASURED_TOP_LEVEL = (
    "import json, sys\n"
    "print(json.dumps({'unmeasured': True, 'reason': 'planted reason: no data was read'}))\n"
    "sys.exit(0)\n"
)
UNMEASURED_IN_RESULT = (
    "import json, sys\n"
    "print(json.dumps({'ok': True, 'result': {'unmeasured': True, 'reason': 'planted reason in the result'}}))\n"
    "sys.exit(0)\n"
)
UNMEASURED_PLAIN_TEXT = (
    "import sys\n"
    "print('coverage of the store: unmeasured')\n"
    "sys.exit(0)\n"
)
CLEAN_SUCCESS_FORM = (
    "import json, sys\n"
    "print(json.dumps({'ok': True, 'result': {'findings': []}}))\n"
    "sys.exit(0)\n"
)
CLEAN_NO_OUTPUT = "import sys\nsys.exit(0)\n"
CLEAN_PLAIN_TEXT = (
    "import sys\n"
    "print('measured 12 of 12 items')\n"
    "sys.exit(0)\n"
)


def planted(project, name, script, severity=HARD_BLOCK):
    project.declare(name, project.script(name, script), severity=severity)
    project.commit_all(f"plant {name}")
    return project.check()


def test_s2_exit_zero_with_a_finding_is_red_not_green(project):
    run = planted(project, "planted-finding", FINDING_LIST)
    entry = run.entry("planted-finding")
    assert entry["status"] != GREEN, run.describe()
    assert entry["status"] == RED, run.describe()
    assert "PLANTED_FINDING" in support.finding_codes(entry), run.describe()
    assert run.returncode == support.EXIT_CHECK_FAILED, run.describe()


def test_s2_exit_zero_with_a_finding_in_the_success_form_is_not_green(project):
    run = planted(project, "planted-result-finding", FINDING_IN_SUCCESS_FORM)
    entry = run.entry("planted-result-finding")
    assert entry["status"] == RED, run.describe()
    assert "PLANTED_FINDING" in support.finding_codes(entry), run.describe()


def test_s2_exit_zero_with_a_finding_of_a_warning_check_is_yellow(project):
    run = planted(project, "planted-warning-finding", FINDING_LIST, severity=WARNING)
    entry = run.entry("planted-warning-finding")
    assert entry["status"] == YELLOW, run.describe()
    assert entry["status"] != GREEN, run.describe()


def test_s2_exit_zero_with_unmeasured_in_a_json_mapping_is_red_with_its_reason(project):
    run = planted(project, "planted-unmeasured", UNMEASURED_TOP_LEVEL)
    entry = run.entry("planted-unmeasured")
    assert entry["status"] != GREEN, run.describe()
    assert entry["status"] == RED, run.describe()
    found = support.findings_with(entry, "CHECK_UNMEASURED")
    assert found, f"no CHECK_UNMEASURED finding\n{run.describe()}"
    assert "planted reason: no data was read" in str(found), f"the finding does not carry the reason\n{run.describe()}"
    assert run.returncode == support.EXIT_CHECK_FAILED, run.describe()


def test_s2_exit_zero_with_unmeasured_in_the_result_of_the_success_form_is_red(project):
    run = planted(project, "planted-result-unmeasured", UNMEASURED_IN_RESULT)
    entry = run.entry("planted-result-unmeasured")
    assert entry["status"] == RED, run.describe()
    found = support.findings_with(entry, "CHECK_UNMEASURED")
    assert found, f"no CHECK_UNMEASURED finding\n{run.describe()}"
    assert "planted reason in the result" in str(found), run.describe()


def test_s2_exit_zero_with_the_word_unmeasured_in_plain_output_is_red(project):
    run = planted(project, "planted-text-unmeasured", UNMEASURED_PLAIN_TEXT)
    entry = run.entry("planted-text-unmeasured")
    assert entry["status"] == RED, run.describe()
    assert "CHECK_UNMEASURED" in support.finding_codes(entry), run.describe()


def test_s2_exit_zero_with_unmeasured_of_a_warning_check_is_yellow_not_green(project):
    run = planted(project, "planted-warning-unmeasured", UNMEASURED_TOP_LEVEL, severity=WARNING)
    entry = run.entry("planted-warning-unmeasured")
    assert entry["status"] == YELLOW, run.describe()
    assert "CHECK_UNMEASURED" in support.finding_codes(entry), run.describe()


def test_s2_clean_check_exiting_zero_is_green_in_every_form(project):
    for name, script in (("clean-success-form", CLEAN_SUCCESS_FORM), ("clean-no-output", CLEAN_NO_OUTPUT),
                         ("clean-plain-text", CLEAN_PLAIN_TEXT)):
        project.declare(name, project.script(name, script))
    project.commit_all("plant three clean checks")
    run = project.check()
    for name in ("clean-success-form", "clean-no-output", "clean-plain-text"):
        entry = run.entry(name)
        assert entry["status"] == GREEN, f"{name}\n{run.describe()}"
        assert entry.get("findings") == [], f"{name}\n{run.describe()}"


def test_s2_a_clean_check_is_green_beside_a_check_that_is_not(project):
    """Both kinds in one run: the not-green one does not turn the clean one red, nor the reverse."""
    project.declare("clean-beside", project.script("clean-beside", CLEAN_SUCCESS_FORM))
    project.declare("unmeasured-beside", project.script("unmeasured-beside", UNMEASURED_TOP_LEVEL))
    project.commit_all("plant a clean check and an unmeasured one")
    run = project.check()
    assert run.entry("clean-beside")["status"] == GREEN, run.describe()
    assert run.entry("unmeasured-beside")["status"] == RED, run.describe()
