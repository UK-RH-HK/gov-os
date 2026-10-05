"""KPI failure 1 [CAP-51.a], batch 3: a file the checker cannot read does not hide a hazard. Added after
implementation, from a behaviour a review described (DEC-136).

The checker reads frontmatter (DEC-329). A Markdown file that opens with ``---`` and whose frontmatter is not
closed, or is not valid YAML, cannot be read: its id, its status and its supersessions are unknown, so no hazard
can be ruled out for it and the check does not pass. The finding is ``FRONTMATTER_UNREADABLE`` and names the file.
The checker cannot tell which unreadable file is a decision file, so every such Markdown file is reported.

A file whose ``---`` is not its first line (a byte-order mark or a blank line stands before it) is not tested: what
it is waits on a decision package (README, "Open package").
"""

from __future__ import annotations

import pytest

import w1_11_support as support
from w1_11_support import AGENT, adr_path, decision

ADR = "ADR-0010"
SECOND = "decisions/ADR-0010.md"

# A second file with the id of docs/adr/ADR-0010.md, ACTIVE, committed by an agent: a duplicate id and an unapproved
# ACTIVE decision, if it could be read.
UNREADABLE = {
    "broken YAML": f"---\nid: {ADR}\ntype: decision\nstatus: ACTIVE\ntitle: [A decision\n---\n\n# {ADR}\n\nBody.\n",
    "not closed": f"---\nid: {ADR}\ntype: decision\nstatus: ACTIVE\n\n# {ADR}\n\nNever closed.\n",
}


@pytest.mark.parametrize("how", sorted(UNREADABLE))
def test_a_decision_file_that_cannot_be_read_does_not_pass_in_silence(api, project, how):
    project.put({**support.CLEAN, adr_path(ADR): decision(ADR, "PROPOSED")})
    project.put({SECOND: UNREADABLE[how]}, who=AGENT)
    found = api.check(project.root)
    support.assert_fails_naming(found, SECOND, {support.FRONTMATTER_UNREADABLE})


def test_a_markdown_file_without_frontmatter_is_not_unreadable(api, project):
    """The control: a rule `---` in the body of a file that opens with a heading is no frontmatter."""
    project.put({**support.CLEAN, "docs/notes.md": "# Notes\n\nOne part.\n\n---\n\nstatus: [another part\n"})
    found = api.check(project.root)
    assert found == [], f"a clean register does not pass:\n{support.show(found)}"
