"""W1-33 -- the kernel role files of the five Wave 1 roles.

KPI success 1 [CAP-22.a]: "Five roles (orchestrator, product/spec, independent
test designer, engineer, independent auditor) each with purpose, allowed-path
pattern, tools, model tier, authority level and handoff format".

KPI success 2: "Only the test designer pattern includes tests/acceptance/**; the
auditor is read-only; only the orchestrator may install, and only after owner
approval in chat (DEC-083), except the research role inside its experiment
folder (DEC-163)".

KPI success 3 [CAP-58.b]: "Each role maps the Framework §32 permission classes
... a launched worker session's network grant comes from the launcher's network
profile, which the role definition names (empty for engineer, test designer and
auditor; the research allowlist for research, DEC-158, DEC-163)".

KPI success 4, the scope half: "the orchestrator definition states its write
scope, anywhere in the repository except tests/acceptance/** (DEC-156)".

KPI success 5: "W1-33 does not redefine it (DEC-163)": the research role file.

KPI failure 1: "A role lacks any required field". KPI failure 2: "An implementer
role pattern covers tests/acceptance/**".

A kernel role file is ``template/governance/kernel/roles/<role>.md``, in the form
of ``research.md`` (W1-46). The tests of ``.claude/agents/`` are in
``test_w1_33_agent_definitions.py``.
"""

from __future__ import annotations

import pytest

import w1_33_support as support


def _role_file(role):
    return support.read_committed(support.role_file_rel(role))


# --------------------------------------------------------------------------
# Success 1 [CAP-22.a]: the six fields
# --------------------------------------------------------------------------

def test_the_research_role_file_is_read_in_this_form():
    """The form these tests read is the one in use: W1-46's role file has the six fields under it."""
    assert support.missing_fields(_role_file(support.RESEARCH)) == []


@pytest.mark.parametrize("role", support.ROLES)
def test_the_role_has_a_kernel_role_file_with_the_six_fields(role):
    missing = support.missing_fields(_role_file(role))
    assert not missing, f"{support.role_file_rel(role)} lacks {missing}"


# --------------------------------------------------------------------------
# Success 2: tests/acceptance/**, the read-only auditor, installs
# --------------------------------------------------------------------------

def test_the_test_designer_pattern_includes_the_acceptance_tests():
    faults = support.acceptance_faults(support.TEST_DESIGNER, _role_file(support.TEST_DESIGNER))
    assert not faults, f"{support.role_file_rel(support.TEST_DESIGNER)}: {faults}"


@pytest.mark.parametrize("role", support.NOT_TEST_DESIGNER)
def test_no_other_pattern_includes_the_acceptance_tests(role):
    faults = support.acceptance_faults(role, _role_file(role))
    assert not faults, f"{support.role_file_rel(role)}: {faults}"


def test_the_auditor_is_read_only_except_its_ticket_s_report_path():
    """DEC-112: "read-only everywhere except the report path its own ticket allows"."""
    faults = support.auditor_scope_faults(_role_file(support.AUDITOR))
    assert not faults, f"{support.role_file_rel(support.AUDITOR)}: {faults}"


def test_the_orchestrator_may_install_only_after_owner_approval():
    """DEC-083: install commands are an ``ask`` permission for the orchestrator; the owner approves in chat."""
    found = support.statements(_role_file(support.ORCHESTRATOR), "PACKAGE_INSTALL")
    assert found, "the orchestrator's role file does not map PACKAGE_INSTALL"
    for written, statement in found.items():
        assert support.disposition(statement) == "ask", f"{written} is not `ask` for the orchestrator: {statement!r}"
        assert "owner" in statement.lower() and "DEC-083" in statement, (
            f"{written} does not name the owner's approval and DEC-083: {statement!r}"
        )


@pytest.mark.parametrize("role", support.NOT_ORCHESTRATOR)
@pytest.mark.parametrize("name", ("PACKAGE_INSTALL", "SYSTEM_INSTALL"))
def test_no_other_role_may_install(role, name):
    found = support.statements(_role_file(role), name)
    assert found, f"{support.role_file_rel(role)} does not map {name}"
    for written, statement in found.items():
        assert support.disposition(statement) == "denied", f"{written} is not denied to {role}: {statement!r}"


def test_the_research_exception_is_stated_by_the_research_role_file_alone():
    """DEC-163: the one role that installs without the owner does so inside its experiment folder."""
    tools = support.field(_role_file(support.RESEARCH), "tools") or ""
    assert "experiment folder" in tools and "DEC-163" in tools, "the research role file no longer states its installs"


# --------------------------------------------------------------------------
# Success 3 [CAP-58.b]: the permission classes and the network profile
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", support.ROLES)
def test_the_role_maps_every_permission_class(role):
    text = _role_file(role)
    assert support.field(text, "permission classes") is not None, (
        f"{support.role_file_rel(role)} has no permission-classes field"
    )
    unmapped = [name for name in support.EVERY_CLASS if not support.statements(text, name)]
    assert not unmapped, f"{support.role_file_rel(role)} does not map {unmapped}"


@pytest.mark.parametrize("role", support.ROLES)
def test_the_role_maps_the_classes_as_the_contract_says(role):
    """WRITE_REPO_SCOPED by allowed_paths, installs per DEC-083, SECRET_READ denied, READ_REPO and RUN_TESTS allowed,
    the network, database, cloud, CI-trigger and deploy classes denied unless the definition grants them."""
    faults = support.class_faults(role, _role_file(role))
    assert not faults, f"{support.role_file_rel(role)}: {faults}"


@pytest.mark.parametrize("role", support.EMPTY_PROFILE_ROLES)
def test_a_launched_worker_names_the_launcher_s_empty_network_profile(role):
    faults = support.network_faults(role, _role_file(role))
    assert not faults, f"{support.role_file_rel(role)}: {faults}"


def test_the_research_role_file_names_the_research_allowlist():
    faults = support.network_faults(support.RESEARCH, _role_file(support.RESEARCH))
    assert not faults, f"{support.role_file_rel(support.RESEARCH)}: {faults}"


# --------------------------------------------------------------------------
# Success 4, the scope half: the orchestrator's write scope (DEC-156)
# --------------------------------------------------------------------------

def test_the_orchestrator_role_file_states_its_write_scope():
    faults = support.orchestrator_scope_faults(_role_file(support.ORCHESTRATOR))
    assert not faults, f"{support.role_file_rel(support.ORCHESTRATOR)}: {faults}"


# --------------------------------------------------------------------------
# Success 5: the research role file is left as it is (DEC-163)
# --------------------------------------------------------------------------

def test_the_research_role_file_is_unchanged():
    """Green before implementation; it must stay green."""
    files = sorted(path.name for path in (support.REPO_ROOT / support.ROLES_DIR_REL).glob("research*"))
    assert files == ["research.md"], f"the kernel holds another research role file: {files}"
    assert support.sha256(support.role_file_rel(support.RESEARCH)) == support.RESEARCH_ROLE_FILE_SHA256, (
        "template/governance/kernel/roles/research.md is not the file W1-46 placed"
    )


# --------------------------------------------------------------------------
# Failure 1: a role lacks any required field
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", support.ROLES)
def test_a_role_file_without_one_required_field_is_found(role):
    """Each of the six fields in turn is taken out of the role's own file; the check names exactly that field."""
    text = _role_file(role)
    assert support.missing_fields(text) == [], f"{support.role_file_rel(role)} is not complete to begin with"
    for name in support.REQUIRED_FIELDS:
        assert support.missing_fields(support.without_field(text, name)) == [name], (
            f"{role} without its {name} field was not found to lack exactly that field"
        )


@pytest.mark.parametrize("role", support.ROLES)
def test_a_required_field_with_no_text_is_found(role):
    text = support.with_field(_role_file(role), "model tier", "")
    assert support.missing_fields(text) == ["model tier"], f"an empty model tier of {role} was not found"


# --------------------------------------------------------------------------
# Failure 2: an implementer role pattern covers tests/acceptance/**
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", support.IMPLEMENTERS)
@pytest.mark.parametrize("pattern", (
    "its ticket's `allowed_paths`, and `tests/acceptance/**`.",
    "`src/**` and `tests/acceptance/<ticket-id>/**` on its own ticket.",
))
def test_an_implementer_pattern_that_covers_the_acceptance_tests_is_found(role, pattern):
    text = _role_file(role)
    assert support.acceptance_faults(role, text) == [], f"{support.role_file_rel(role)} is not clean to begin with"
    faults = support.acceptance_faults(role, support.with_field(text, "allowed-path pattern", pattern))
    assert faults, f"a pattern of {role} that covers the acceptance tests was not found: {pattern!r}"
