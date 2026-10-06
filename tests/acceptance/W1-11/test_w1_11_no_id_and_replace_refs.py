"""KPI success 2 [CAP-01.b, CAP-21.a] and failure 1 [CAP-51.a], batch 5: two points DEC-387 decided (packages DP-5
and DP-7). Added after implementation.

- **A file with ``type: decision`` and no ``id`` is a decision that fails.** The checker follows a decision by its
  id; a decision without one cannot be followed, so it does not pass in silence. The finding names the file; its
  code is the engineer's.
- **The checker runs git with replace refs off.** A replace ref makes git show another commit in the place of one
  the history names. The approval fact is the trailer of the commit that set the decision ``ACTIVE`` (DEC-360), not
  of a commit a ref under ``refs/replace/`` puts in its place.

Both run the check without loading the store: what ``gov.store.load`` reads through a replace ref is not this
ticket's.
"""

from __future__ import annotations

import w1_11_support as support
from w1_11_support import AGENT, OWNER, adr_path, decision

ADR = "ADR-0010"
PATH = adr_path(ADR)
WITHOUT_AN_ID = "docs/adr/ADR-0011.md"


def test_an_active_decision_without_an_id_set_by_an_agent_fails(api, project):
    """The file says `type: decision` and `status: ACTIVE` and has no `id`; an agent's commit added it."""
    project.put(support.CLEAN, who=OWNER)
    text = ("---\ntype: decision\nstatus: ACTIVE\nstate_class: AUTHORITATIVE\ntitle: A decision without an id\n---\n\n"
            "# A decision without an id\n\nBody text.\n")
    project.put({WITHOUT_AN_ID: text}, who=AGENT)
    found = api.check_only(project.root)
    support.assert_some_finding_names(found, WITHOUT_AN_ID)


def test_a_replace_ref_that_gives_an_agent_commit_the_owner_role_is_no_approval(api, project):
    """An agent's commit sets the decision ACTIVE. A copy of that commit with the trailer `Role: owner` is made,
    and a replace ref puts the copy in the commit's place: `git log` now shows the owner's role there."""
    project.put(support.CLEAN, who=OWNER)
    commit = project.put({PATH: decision(ADR, "ACTIVE")}, who=AGENT)
    copy = project.copy_of_commit(commit, OWNER)
    support.git(project.root, "replace", commit, copy)
    assert "Role: owner" in support.git(project.root, "log", "-1", "--format=%B", commit), \
        "the fixture's replace ref is not in effect"
    assert "Role: engineer" in support.git(project.root, "--no-replace-objects", "log", "-1", "--format=%B", commit), \
        "the fixture's commit is not the agent's"
    found = api.check_only(project.root)
    support.assert_flagged(found, support.ACTIVE_UNAPPROVED, [ADR], [PATH])
