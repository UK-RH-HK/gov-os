"""W1-13, second batch (DEC-136) -- B1: the bare command does not pass over a change it cannot judge.

KPI failure 1: "a spec with a required MISSING row is reported closed" must never happen. ``gov readiness`` with
neither selector judges every specification (DEC-351), and a specification is the record in the frontmatter of
``openspec/changes/<change>/proposal.md`` (DEC-350). Nothing writes that frontmatter yet (DEC-350's residual): the
proposal template has none. So a change folder that cannot be read as a specification record is the usual change of
an adopted project today, and a gate that skips it answers "passes" for a change whose every row is MISSING.

Expected: such a change is an invalid record (DEC-351): ``READINESS_INVALID``, exit code 1, the change named in the
error, nothing written. ``openspec/changes/archive/`` holds archived changes and is not a change.
"""

from __future__ import annotations

import w1_13_support as support

CHANGE = support.CHANGE
BARE = (support.COMMAND, "--json")


def _refused(project, gov, interface, proposal, change=CHANGE):
    """Write the change with every row MISSING, run the bare command: it refuses, names the change, writes nothing."""
    support.write_change(project, change, proposal, support.fresh_rows())
    project.settle()
    before = project.state()
    run = gov(*BARE)
    error = support.unreadable(run, interface, change)
    assert project.state() == before, f"gov readiness changed the project\n{run.describe()}"
    return error


# ---- a change that is no specification record

def test_a_proposal_with_no_frontmatter_does_not_pass(project, gov, interface):
    """The proposal template as it is written today, beside a fresh ``readiness.yaml``."""
    template = support.PROPOSAL_TEMPLATE.read_text(encoding="utf-8")
    assert not template.startswith("---"), "the proposal template now writes a frontmatter: revise this case"
    _refused(project, gov, interface, template)


def test_a_proposal_that_is_not_of_type_specification_does_not_pass(project, gov, interface):
    """No ``type``, then another type: a change's proposal is a specification or the change is not judged."""
    _refused(project, gov, interface, support.proposal_text(support.frontmatter(type=None)))
    _refused(project, gov, interface, support.proposal_text(support.frontmatter(type="note")))


def test_a_proposal_with_no_id_does_not_pass(project, gov, interface):
    """No ``id``, then an empty one: nothing could name this specification, and no ticket could wait on it."""
    _refused(project, gov, interface, support.proposal_text(support.frontmatter(id=None)))
    _refused(project, gov, interface, support.proposal_text(support.frontmatter(id="")))


def test_a_proposal_whose_frontmatter_is_not_yaml_does_not_pass(project, gov, interface):
    broken = f"id: {support.SPEC}\ntype: {support.SPEC_TYPE}\nstatus: [{support.STATUS_OPEN}\nprofile: FULL: {{\n"
    _refused(project, gov, interface, support.proposal_text(broken))


def test_a_change_with_a_readiness_record_and_no_proposal_does_not_pass(project, gov, interface):
    _refused(project, gov, interface, None)


def test_one_unreadable_change_beside_a_complete_specification_does_not_pass(project, gov, interface):
    """The complete specification does not answer for the change beside it."""
    project.specification(support.complete_rows(), spec_id=support.OTHER_SPEC, change=support.OTHER_CHANGE)
    _refused(project, gov, interface, support.proposal_text(None))


# ---- controls: nothing to judge

def test_a_project_with_no_change_passes(project, gov, interface):
    run = gov(*BARE)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is True and run.returncode == 0, f"there is nothing to judge\n{run.describe()}"


def test_the_archive_folder_is_not_a_change(project, gov, interface):
    """An archived change, unreadable and with every row MISSING, under ``openspec/changes/archive/``."""
    support.write_change(project, "2026-01-01-zq11-old-feature", support.proposal_text(None), support.fresh_rows(),
                         parent=f"{support.CHANGES_REL}/{support.ARCHIVE_NAME}")
    run = gov(*BARE)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is True and run.returncode == 0, f"only the archive folder is there\n{run.describe()}"
