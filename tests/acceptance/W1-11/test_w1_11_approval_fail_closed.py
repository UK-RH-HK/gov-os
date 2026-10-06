"""KPI success 2 [CAP-01.b, CAP-21.a], batch 5: a merge the checker cannot judge against one merge base does not
pass on trust (DEC-398, with DEC-403 and DEC-410). Added after implementation, from the owner's decision.

The approval rule judges a merge against the merge base. Where the parents have several merge bases (two lines that
crossed) or none (unrelated histories), nothing counts as brought by a parent: a decision the merge commit holds
``ACTIVE`` in a file that differs from any parent's, or that a parent does not hold, is set ``ACTIVE`` by the merge
commit itself, and the merge commit's own ``Role`` trailer is the fact. An agent's such merge fails, also where one
merge base would have let it pass: these are false alarms the decision accepts. The owner's passes.

A merge that holds the same file of the decision as every parent sets nothing, whatever the merge bases.

The last case: a merge commit with more parents than the shared merge helper reads (24, DEC-410) is not passed in
silence either.
"""

from __future__ import annotations

import pytest

import w1_11_support as support
from w1_11_support import AGENT, OWNER, adr_path, decision

ADR = "ADR-0010"
PATH = adr_path(ADR)
IMPORTED = "imported/" + PATH

APPROVED = decision(ADR, "ACTIVE")
DEMOTED = decision(ADR, "PROPOSED")
ON_THE_LEFT = decision(ADR, "ACTIVE", body="Body text, as the owner accepted it on the main line.")
ON_THE_RIGHT = decision(ADR, "ACTIVE", body="Body text, as the owner accepted it on the other line.")
NOTES = "# Notes\n\nNo frontmatter here.\n"


def unapproved(found, record_id=ADR):
    return support.matching(found, support.ACTIVE_UNAPPROVED, [record_id])


def the_owner_approves_on_one_of_two_crossed_lines(project, merger):
    """Two lines cross (two merge bases); the decision is PROPOSED on both. The owner then sets it ACTIVE on the
    other line, and the merge brings that to the main line: git makes it by itself."""
    project.put({**support.CLEAN, PATH: DEMOTED}, who=OWNER)
    project.criss_cross("right")
    project.switch("right")
    project.put({PATH: APPROVED}, who=OWNER, message="accept ADR-0010")
    project.switch("main")
    project.put({"README.md": "# A project\n\nReworded.\n"}, who=AGENT)
    return project.merge_with("right", who=merger), PATH, APPROVED


def the_owner_approved_on_both_crossed_lines(project, merger):
    """Two long-lived lines cross. The owner sets the decision ACTIVE on each, with two texts; the merge keeps the
    main line's."""
    project.put({**support.CLEAN, PATH: DEMOTED}, who=OWNER)
    project.criss_cross("right")
    project.switch("right")
    project.put({PATH: ON_THE_RIGHT}, who=OWNER, message="accept ADR-0010")
    project.switch("main")
    project.put({PATH: ON_THE_LEFT}, who=OWNER, message="accept ADR-0010")
    return project.merge_with("right", who=merger, take={PATH: "main"}), PATH, ON_THE_LEFT


def an_unrelated_history_without_the_decision_is_merged(project, merger):
    """The main line holds the decision ACTIVE by the owner. A history that shares no commit with it, and never
    held the decision, is merged in."""
    project.put({**support.CLEAN, PATH: APPROVED}, who=OWNER)
    project.orphan("other", {"vendor/library.py": "VALUE = 1\n", "vendor/NOTES.md": NOTES}, who=AGENT)
    project.switch("main")
    return project.merge_with("other", who=merger, unrelated=True), PATH, APPROVED


def an_unrelated_history_with_the_decision_is_imported(project, merger):
    """A history of its own holds the decision, ACTIVE by its owner commit. It is merged into the main line, which
    never held it, below the folder `imported/`: how a register is imported."""
    project.put(support.CLEAN, who=OWNER)
    project.orphan("other", {PATH: APPROVED, "NOTES.md": NOTES}, who=OWNER)
    project.switch("main")
    return project.merge_with("other", who=merger, under="imported"), IMPORTED, APPROVED


CANNOT_BE_JUDGED = {
    "two crossed lines, the owner approved on one": the_owner_approves_on_one_of_two_crossed_lines,
    "two crossed lines, the owner approved on both": the_owner_approved_on_both_crossed_lines,
    "an unrelated history without the decision": an_unrelated_history_without_the_decision_is_merged,
    "an unrelated history imported with the decision": an_unrelated_history_with_the_decision_is_imported,
}
BASES = {name: 0 if name.startswith("an unrelated") else 2 for name in CANNOT_BE_JUDGED}


def build(project, shape, merger):
    """Build the history; check that it is what the case says. Returns the path of the decision in `HEAD`."""
    merge, path, text = CANNOT_BE_JUDGED[shape](project, merger)
    parents = support.parents_of(project.root, merge)
    assert support.git(project.root, "rev-parse", "HEAD").strip() == merge and len(parents) == 2, "HEAD is no merge"
    assert len(support.merge_bases(project.root, *parents)) == BASES[shape], "the parents have other merge bases"
    assert support.git(project.root, "show", f"HEAD:{path}") == text, "the fixture's HEAD holds another file"
    return path


# ---- several merge bases or none: an agent's merge fails, the owner's passes (DEC-398, DEC-403)

@pytest.mark.parametrize("shape", sorted(CANNOT_BE_JUDGED))
def test_an_agent_merge_that_cannot_be_judged_against_one_merge_base_fails(api, project, shape):
    path = build(project, shape, AGENT)
    found = api.check(project.root)
    support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [ADR], [path])


@pytest.mark.parametrize("shape", sorted(CANNOT_BE_JUDGED))
def test_an_owner_merge_that_cannot_be_judged_against_one_merge_base_passes(api, project, shape):
    """The control: the merge commit that sets the decision ACTIVE carries `Role: owner`."""
    build(project, shape, OWNER)
    found = api.check(project.root)
    assert not unapproved(found), support.show(found)


def test_an_agent_merge_of_two_crossed_lines_that_both_hold_the_approved_file_passes(api, project):
    """The control: the owner set the decision ACTIVE before the lines parted, and neither touched it. The merge
    holds the file both parents hold: it has nothing to be trusted for."""
    project.put({**support.CLEAN, PATH: APPROVED}, who=OWNER)
    project.criss_cross("right")
    project.switch("right")
    project.put({"notes/right-2.md": NOTES}, who=AGENT)
    project.switch("main")
    project.put({"README.md": "# A project\n\nReworded.\n"}, who=AGENT)
    merge = project.merge_with("right", who=AGENT)
    assert len(support.merge_bases(project.root, *support.parents_of(project.root, merge))) == 2
    found = api.check(project.root)
    assert found == [], f"a register the owner approved does not pass after two lines crossed:\n{support.show(found)}"


# ---- a merge the shared helper refuses to read (DEC-410: more than 24 parents)

def test_an_agent_merge_with_too_many_parents_that_sets_active_again_does_not_pass(api, project):
    """The owner set the decision ACTIVE and later demoted it. An agent's merge commit with 25 distinct parents
    (the demotion first, then a branch that still holds the old ACTIVE file, then 23 more) holds the decision
    ACTIVE. The helper the checker reads merges with refuses such a commit. The check gives `ACTIVE_UNAPPROVED`
    for the decision or raises `GovError`; it is never a pass."""
    activation = project.put({**support.CLEAN, PATH: APPROVED}, who=OWNER)
    project.switch("work", new=True)
    work = project.put({"notes/work.md": NOTES}, who=AGENT)
    others = project.bare_commits(activation, 23)
    project.switch("main")
    demotion = project.put({PATH: DEMOTED}, who=OWNER)
    support.git(project.root, "checkout", "work", "--", PATH, "notes/work.md")
    merge = project.commit_by_hand([demotion, work, *others], "Merge 24 branches", who=AGENT)
    assert len(set(support.parents_of(project.root, merge))) == 25, "the fixture's merge has not 25 parents"
    assert support.git(project.root, "show", f"HEAD:{PATH}") == APPROVED, "the fixture's HEAD holds another file"
    kind, result = support.outcome(api, project.root)
    if kind == "findings":
        support.assert_flagged(result, support.ACTIVE_UNAPPROVED, [ADR], [PATH])
