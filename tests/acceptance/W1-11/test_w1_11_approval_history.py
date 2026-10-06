"""KPI success 2 [CAP-01.b, CAP-21.a], batch 3: the approval fact in a history that is not a straight line of
plain commits. Added after implementation, from behaviours a review described (DEC-136).

The rule is DEC-360's: the owner's approval fact for a decision is the ``Role: owner`` trailer on the commit that
sets the decision ``ACTIVE``, and a later owner commit approves nothing earlier. Read here as:

- **Only a commit's own ``Role`` trailer is its fact.** Nothing else its message holds makes an approval, whatever
  characters it is written with (CAP-01.b). The first group.
- **"Later" is by ancestry, not by date.** An owner commit that descends from the commit that set the decision
  ``ACTIVE`` is later, whatever its date says and whether it reaches ``HEAD`` directly or through a merge. An owner
  commit on a branch that itself sets the decision ``ACTIVE`` still approves it after the merge. The second group.
- **The decision is its id, not its file's path.** A commit that only moves the file sets nothing. The third group.
"""

from __future__ import annotations

import pytest

import w1_11_support as support
from w1_11_support import AGENT, OWNER, adr_path, decision

ADR = "ADR-0010"
PATH = adr_path(ADR)

UNIT_SEPARATOR, RECORD_SEPARATOR = "\x1f", "\x1e"

# Text laid out like a further entry of a commit log: a commit name, a date and the owner's role, between the
# ASCII separators a log format may use.
IMITATED_ENTRY = (UNIT_SEPARATOR + RECORD_SEPARATOR + "HEAD" + UNIT_SEPARATOR + "2026-10-04" + UNIT_SEPARATOR
                  + "Role: owner" + UNIT_SEPARATOR)

IMITATIONS = {
    "in the subject": "accept ADR-0010" + IMITATED_ENTRY + "as agreed",
    "in the body": "accept ADR-0010\n\n" + IMITATED_ENTRY + "as agreed",
}

LATE, EARLY = "2026-10-04T23:00:00+00:00", "2026-10-04T13:00:00+00:00"
LATER, LATEST = "2026-10-04T23:10:00+00:00", "2026-10-04T23:20:00+00:00"


def unapproved(found, record_id=ADR):
    return support.matching(found, support.ACTIVE_UNAPPROVED, [record_id])


# ---- only a commit's own Role trailer is its fact (DEC-360, CAP-01.b)

@pytest.mark.parametrize("where", sorted(IMITATIONS))
def test_a_commit_message_that_imitates_an_owner_log_entry_is_no_approval(api, project, where):
    """The agent's commit sets the decision ACTIVE; its final trailer block says `Role: engineer`."""
    project.put(support.CLEAN)
    project.write(PATH, decision(ADR, "ACTIVE"))
    project.commit(IMITATIONS[where], who=AGENT)
    found = api.check(project.root)
    support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [ADR], [PATH])


def test_a_control_character_in_a_commit_message_does_not_break_the_check(api, project):
    """A stray unit separator in the message of a commit that touches no decision: the register still passes.
    The store is not loaded first: the checker reads frontmatter and git (DEC-329), and `gov.store.load` of W1-10
    itself fails on such a history, which is not this ticket's to repair."""
    project.put(support.CLEAN, who=OWNER)
    project.write("README.md", "# A project\n\nReworded.\n")
    project.commit("reword the README" + UNIT_SEPARATOR + " and nothing else", who=AGENT)
    found = api.check_only(project.root)
    assert found == [], f"a clean register, committed by the owner, does not pass:\n{support.show(found)}"


# ---- "later" is by ancestry, not by date (DEC-360)

def test_a_later_owner_commit_on_a_merged_branch_approves_nothing_earlier(api, project):
    """The owner's commit descends from the agent's, leaves the decision ACTIVE and has the earlier date. The same
    commits in a straight line are `test_a_later_owner_commit_that_does_not_set_active_approves_nothing_earlier`."""
    project.put({**support.CLEAN, PATH: decision(ADR, "PROPOSED")})
    project.write(PATH, decision(ADR, "ACTIVE"))
    project.commit("accept ADR-0010", who=AGENT, date=LATE)
    project.switch("owner-edit", new=True)
    project.write(PATH, decision(ADR, "ACTIVE", body="Body text, reworded by the owner."))
    project.commit("reword ADR-0010", who=OWNER, date=EARLY)
    project.switch("main")
    project.write("README.md", "# A project\n\nReworded.\n")
    project.commit("reword the README", who=AGENT, date=LATER)
    project.merge("owner-edit", who=AGENT, date=LATEST)
    found = api.check(project.root)
    support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [ADR], [PATH])


def test_an_owner_commit_on_a_branch_that_sets_active_approves_after_the_merge(api, project):
    """The control: the owner's commit is the one that sets the decision ACTIVE; the agent's merge commit brings it
    to the main line and sets nothing."""
    project.put({**support.CLEAN, PATH: decision(ADR, "PROPOSED")})
    project.switch("owner-accepts", new=True)
    project.put({PATH: decision(ADR, "ACTIVE")}, who=OWNER)
    project.switch("main")
    project.put({"README.md": "# A project\n\nReworded.\n"}, who=AGENT)
    project.merge("owner-accepts", who=AGENT)
    found = api.check(project.root)
    assert not unapproved(found), support.show(found)


def test_an_agent_decision_kept_by_a_merge_over_the_owner_file_at_the_same_path_fails(api, project):
    """Two branches add the same path. The owner's file was ACTIVE on its branch; the merge keeps the agent's file,
    which the agent's commit set ACTIVE. Every commit has its fixture date, in the order it was made."""
    project.put(support.CLEAN)
    project.switch("owner-adds", new=True)
    project.put({PATH: decision(ADR, "ACTIVE", title="The owner's decision")}, who=OWNER)
    project.switch("main")
    agents = decision(ADR, "ACTIVE", title="The agent's decision", body="Another decision altogether.")
    project.put({PATH: agents}, who=AGENT)
    project.merge("owner-adds", who=AGENT, keep={PATH: "ours"})
    assert (project.root / PATH).read_text(encoding="utf-8") == agents, "the fixture did not keep the agent's file"
    found = api.check(project.root)
    support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [ADR], [PATH])


# ---- the decision is its id, not its file's path (DEC-360)

def test_an_owner_commit_that_only_renames_the_file_approves_nothing_earlier(api, project):
    """The agent's commit set the decision ACTIVE. The owner's commit moves the file and changes no byte of it."""
    renamed = "docs/adr/ADR-0010-renamed.md"
    project.put(support.CLEAN)
    project.put({PATH: decision(ADR, "ACTIVE")}, who=AGENT)
    support.git(project.root, "mv", PATH, renamed)
    project.commit("rename ADR-0010", who=OWNER)
    found = api.check(project.root)
    support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [ADR], [renamed])
