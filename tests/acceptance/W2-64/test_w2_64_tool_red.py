"""W2-64 KPI failure 2: check-jsonschema missing or failing to run is RED, never anything else; and KPI success 1's
"pinned in the tool registry": a validator of another version than the pin is RED.

Each project holds a record that is valid, so that a green answer would be the fail-open the KPI line names. The
validator on ``PATH`` is the case's: none, the installed one, or a stand-in script in a temporary folder.
"""

from __future__ import annotations

import pytest

import w2_64_support as S

TICKET_REL = ".tickets/PROJ-aaaa.md"


def _project(place, registry=True, record=None):
    project = S.Project(place).kernel_schemas()
    if registry:
        project.registry()
    project.write(TICKET_REL, record or S.ticket())
    return project


def _assert_red(run, what):
    assert run.code != 0, f"core-schema is not RED when {what}\n{run.describe()}"
    assert run.findings or run.output is None, f"core-schema exits {run.code} with no finding when {what}"


def test_check_jsonschema_absent_from_path_is_red_naming_the_tool(tmp_path):
    """*Red.* No check-jsonschema on ``PATH``: core-schema exits non-zero with a finding that names the tool; it is
    never green and never a skip. Today: exit 0, no finding (the subset needs no validator)."""
    run = _project(S.Place(tmp_path).no_tool()).core_schema()
    assert run.code != 0, f"core-schema is green with no {S.TOOL} on PATH\n{run.describe()}"
    assert any(S.TOOL in S.text_of(finding) for finding in run.findings), \
        f"no finding names {S.TOOL}\n{run.describe()}"


def test_gov_check_shows_core_schema_red_without_the_tool(tmp_path):
    """*Red.* ``gov check --json`` in that project gives the ``core-schema`` entry RED with a finding that names the
    tool. Today: GREEN."""
    project = _project(S.Place(tmp_path).no_tool()).declaration()
    run, entry = project.gov_check()
    assert entry.get("status") == "RED", f"gov check gives core-schema {entry.get('status')} with no {S.TOOL}: " \
                                         f"{entry}\n{run.describe()}"
    assert any(S.TOOL in S.text_of(finding) for finding in entry.get("findings") or []), entry


@pytest.mark.parametrize("kind", sorted(S.STAND_INS))
def test_a_validator_that_fails_to_run_or_answers_no_json_is_red(tmp_path, kind):
    """*Red.* A check-jsonschema stand-in on ``PATH`` that prints text that is not its JSON answer and exits 1
    (``prints-text``), exits 0 printing nothing (``silent-exit-0``), answers ``ok`` naming none of the instances it
    was given (``names-no-instance``), is killed (``killed``), or fails every call, ``--version`` included
    (``fails-every-call``): core-schema is RED. Today: exit 0, no finding (the validator is never called)."""
    run = _project(S.Place(tmp_path).stand_in(kind)).core_schema()
    _assert_red(run, f"the validator stand-in '{kind}' is on PATH")


def test_a_validator_that_cannot_be_executed_is_red(tmp_path):
    """*Red.* A check-jsonschema on ``PATH`` without the execute bit: RED. Today: exit 0."""
    run = _project(S.Place(tmp_path).not_executable()).core_schema()
    _assert_red(run, f"the {S.TOOL} on PATH cannot be executed")


def test_errors_answered_with_exit_0_are_still_refused(tmp_path):
    """*Red.* A stand-in that prints the real validator's answer and always exits 0: a record the schema refuses is
    still refused on its path, not passed on the exit code. Today: no finding."""
    place = S.Place(tmp_path).answers_exit_0()
    run = _project(place, record=S.ticket(state_class="NOT-A-CLASS")).core_schema()
    assert run.code != 0, f"errors answered with exit 0 pass\n{run.describe()}"
    assert S.about(run.findings, TICKET_REL), f"no finding names {TICKET_REL}\n{run.describe()}"


def test_a_validator_of_another_version_than_the_pin_is_red_naming_both(tmp_path):
    """*Red.* A stand-in that answers ``--version`` with another version than the registry's pin (and validates with
    the real tool): RED, with a finding that names both versions (DEC-074: the pinned validator is the judge).
    Today: exit 0, no finding."""
    run = _project(S.Place(tmp_path).other_version()).core_schema()
    assert run.code != 0, f"a validator of version {S.OTHER_VERSION} against the pin {S.pinned_version()} passes\n" \
                          f"{run.describe()}"
    assert any(S.OTHER_VERSION in S.text_of(f) and S.pinned_version() in S.text_of(f) for f in run.findings), \
        f"no finding names both {S.OTHER_VERSION} and {S.pinned_version()}\n{run.describe()}"


def test_the_pinned_version_is_green(tmp_path):
    """The control: the installed validator, of the pinned version, and a valid record: exit 0, no finding. Passes
    today."""
    run = _project(S.Place(tmp_path).real_tool()).core_schema()
    assert run.code == 0 and run.findings == [], run.describe()


def test_a_registry_that_cannot_be_read_is_red(tmp_path):
    """*Red.* A tool registry that exists but is not YAML: RED. Today: exit 0 (the registry is not read)."""
    project = _project(S.Place(tmp_path).real_tool(), registry=False)
    project.write(S.REGISTRY_REL, "tools: [ {name: check-jsonschema, version: \n  : : :\n")
    run = project.core_schema()
    _assert_red(run, "the tool registry cannot be read")


def _no_pin(project, registry):
    if registry == "no-entry":
        project.write(S.REGISTRY_REL, "tools:\n  - name: lefthook\n    version: \"2.1.15\"\n")
    return project


@pytest.mark.parametrize("registry", ("absent", "no-entry"))
def test_no_pin_stated_still_validates(tmp_path, registry):
    """*Red.* A project with no registry, or a registry with no check-jsonschema entry, states no pin: the check
    still validates (a record its schema refuses is refused), and the absent pin is no finding of its own. Today:
    the fault passes."""
    project = _no_pin(_project(S.Place(tmp_path).real_tool(), registry=False,
                               record=S.ticket(state_class="NOT-A-CLASS")), registry)
    run = project.core_schema()
    assert run.code != 0 and S.about(run.findings, TICKET_REL), \
        f"with no pin stated ({registry}), a refused record passes\n{run.describe()}"
    assert not [f for f in run.findings if f.get("path") != TICKET_REL], \
        f"no pin stated ({registry}) gives a finding of its own: {run.findings}"


@pytest.mark.parametrize("registry", ("absent", "no-entry"))
def test_no_pin_stated_is_green_and_says_so(tmp_path, registry):
    """*Red.* With no pin stated and a valid record: exit 0, no finding, and the output says that no pin was stated
    (it mentions a pin). Today: nothing is printed."""
    run = _no_pin(_project(S.Place(tmp_path).real_tool(), registry=False), registry).core_schema()
    assert run.code == 0 and run.findings == [], f"no pin stated ({registry}) is not green\n{run.describe()}"
    assert "pin" in run.stdout.lower(), f"the output does not say that no pin was stated\n{run.describe()}"
