"""KPI success 4, as DEC-186 states it: check declarations and ``gov check --list --json``.

A declaration is a YAML file under ``template/governance/kernel/checks/`` with
``id``, ``family``, ``tier``, ``severity`` and ``command``. The tests add
declarations to a project copy the way a ticket registers a check: by adding a
file. Running checks stays ``NOT_IMPLEMENTED`` until W1-26.
"""

from __future__ import annotations

import re

import pytest

import w1_07_support as support

FIELDS = ("id", "family", "tier", "severity", "command")

HARD_BLOCK = {
    "id": "w1-07-fixture-mutation-scope",
    "family": "mutation scope",
    "tier": "G1",
    "severity": "hard-block",
    "command": "python3 -m w1_07_fixture.mutation_scope",
}
WARNING = {
    "id": "w1-07-fixture-command-contract",
    "family": "command-contract consistency",
    "tier": "G2",
    "severity": "warning",
    "command": "python3 -m w1_07_fixture.command_contract --strict",
}


def _declare(project, declaration, commit=True):
    folder = project / support.CHECKS_REL
    folder.mkdir(parents=True, exist_ok=True)
    text = "".join(f'{field}: "{declaration[field]}"\n' for field in FIELDS)
    (folder / f"{declaration['id']}.yaml").write_text(text, encoding="utf-8")
    if commit:
        support.commit_all(project, f"declare {declaration['id']}")


def _listed(gov, interface):
    """``id -> record`` for every check ``gov check --list --json`` lists."""
    run = gov("check", "--list", "--json")
    envelope = support.assert_envelope(run, interface, command="check")
    assert envelope["ok"] is True and run.returncode == 0, f"gov check --list does not succeed\n{run.describe()}"
    return {record["id"]: record for record in support.find_records(envelope["result"])}, run


def test_check_list_succeeds(gov, interface):
    _listed(gov, interface)


@pytest.mark.parametrize("declaration", [HARD_BLOCK, WARNING], ids=["hard-block", "warning"])
def test_a_declared_check_is_listed_with_its_five_fields(gov, project, interface, declaration):
    _declare(project, declaration)
    listed, run = _listed(gov, interface)
    assert declaration["id"] in listed, f"the declared check {declaration['id']} is not listed\n{run.describe()}"
    record = listed[declaration["id"]]
    for field in FIELDS:
        assert record.get(field) == declaration[field], \
            f"the listed check has {field}={record.get(field)!r}, declared {declaration[field]!r}\n{run.describe()}"


def test_the_list_follows_the_declaration_files(gov, project, interface):
    """Any ticket registers a check by adding a file: no list in the code decides what is declared."""
    listed, run = _listed(gov, interface)
    assert HARD_BLOCK["id"] not in listed and WARNING["id"] not in listed, run.describe()
    _declare(project, HARD_BLOCK)
    _declare(project, WARNING)
    listed, run = _listed(gov, interface)
    assert HARD_BLOCK["id"] in listed and WARNING["id"] in listed, \
        f"two declarations were added, and the list does not show both\n{run.describe()}"
    (project / support.CHECKS_REL / f"{HARD_BLOCK['id']}.yaml").unlink()
    support.commit_all(project, "one declaration removed")
    listed, run = _listed(gov, interface)
    assert HARD_BLOCK["id"] not in listed and WARNING["id"] in listed, \
        f"a removed declaration is still listed, or the other one is gone\n{run.describe()}"


def test_every_declaration_in_the_kernel_template_is_listed(gov, project, interface):
    """Whatever declarations the repository ships are all listed, next to a new one."""
    _declare(project, WARNING)
    declared = []
    for path in sorted((project / support.CHECKS_REL).glob("*.yaml")):
        found = re.search(r"^id:\s*[\"']?([^\"'\n#]+?)[\"']?\s*(?:#.*)?$", path.read_text(encoding="utf-8"),
                          re.MULTILINE)
        assert found, f"{path.name} has no top-level id"
        declared.append(found.group(1))
    listed, run = _listed(gov, interface)
    missing = [check_id for check_id in declared if check_id not in listed]
    assert not missing, f"declared and not listed: {missing}\n{run.describe()}"
    for check_id in declared:
        absent = [field for field in FIELDS if field not in listed[check_id]]
        assert not absent, f"the listed check {check_id} lacks {absent}\n{run.describe()}"


def test_listing_does_not_run_a_check(gov, project, interface, sandbox):
    """``--list`` only reads the declarations; the declared command is not started."""
    marker = sandbox.elsewhere / "the-check-ran"
    declaration = dict(HARD_BLOCK, command=f"touch {marker}")
    _declare(project, declaration)
    listed, run = _listed(gov, interface)
    assert declaration["id"] in listed, run.describe()
    assert not marker.exists(), f"gov check --list ran the declared command\n{run.describe()}"


def test_running_checks_stays_not_implemented_with_declarations_present(gov, project, interface, sandbox):
    marker = sandbox.elsewhere / "the-check-ran"
    _declare(project, dict(WARNING, command=f"touch {marker}"))
    run = gov("check", "--json")
    support.assert_error(run, interface, support.NOT_IMPLEMENTED, exit_code=1, command="check")
    assert not marker.exists(), f"gov check ran a declared command\n{run.describe()}"


def test_an_uncommitted_declaration_is_listed_and_left_alone(gov, project, interface):
    """Listing reads the working tree, and changes nothing in it."""
    _declare(project, HARD_BLOCK, commit=False)
    before = support.porcelain(project)
    listed, run = _listed(gov, interface)
    assert HARD_BLOCK["id"] in listed, run.describe()
    assert support.porcelain(project) == before, run.describe()
