"""KPI failure 1 [CAP-51.a], batch 3: a file the checker cannot read does not hide a hazard. Added after
implementation, from a behaviour a review described (DEC-136).

The checker reads frontmatter (DEC-329). A Markdown file that opens with ``---`` and whose frontmatter is not
closed, or is not valid YAML, cannot be read: its id, its status and its supersessions are unknown, so no hazard
can be ruled out for it and the check does not pass. The finding is ``FRONTMATTER_UNREADABLE`` and names the file.
The checker cannot tell which unreadable file is a decision file, so every such Markdown file is reported.

Batch 5 (DEC-387, package DP-5 option (a)): a file whose head looks like frontmatter and cannot be read as the
store reads it is unreadable too. The store takes frontmatter only from a file whose first line is exactly ``---``
in UTF-8 with LF or CRLF line ends, so each of the five heads below is, for the store, a file with no frontmatter;
for the checker it is a finding. A decision file with CRLF line ends, and prose that opens with a byte-order mark or
a blank line, are ordinary files: the control.
"""

from __future__ import annotations

import pytest

import w1_11_support as support
from w1_11_support import AGENT, OWNER, adr_path, decision

ADR = "ADR-0010"
SECOND = "decisions/ADR-0010.md"

# A second file with the id of docs/adr/ADR-0010.md, ACTIVE, committed by an agent: a duplicate id and an unapproved
# ACTIVE decision, if it could be read.
READABLE = f"---\nid: {ADR}\ntype: decision\nstatus: ACTIVE\ntitle: A decision\n---\n\n# {ADR}\n\nBody.\n"
UNREADABLE = {
    "broken YAML": f"---\nid: {ADR}\ntype: decision\nstatus: ACTIVE\ntitle: [A decision\n---\n\n# {ADR}\n\nBody.\n",
    "not closed": f"---\nid: {ADR}\ntype: decision\nstatus: ACTIVE\n\n# {ADR}\n\nNever closed.\n",
    # batch 5 (DEC-387): the head looks like frontmatter and the store does not read it as frontmatter
    "a byte-order mark before the first line": "﻿" + READABLE,
    "a blank line before the first line": "\n" + READABLE,
    "a comment on the first line": READABLE.replace("---\n", "--- # c\n", 1),
    "CR-only line ends": READABLE.replace("\n", "\r"),
    "UTF-16": READABLE.encode("utf-16"),
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


def test_an_ordinary_file_is_not_unreadable(api, project):
    """The control of batch 5 (DEC-387): a decision file with CRLF line ends is read as the store reads it, and
    prose that opens with a byte-order mark, a blank line or a longer rule has no head that looks like
    frontmatter."""
    project.put({
        **support.CLEAN,
        adr_path(ADR): decision(ADR, "ACTIVE").replace("\n", "\r\n"),
        "docs/with-a-mark.md": "﻿# Notes\n\nOne part.\n\n---\n\nstatus: [another part\n",
        "docs/with-a-blank-line.md": "\n# Notes\n\nOne part.\n\n---\n\nAnother part.\n",
        "docs/with-a-long-rule.md": "-----\n\n# Notes\n\nstatus: [a part\n",
    }, who=OWNER)
    found = api.check(project.root)
    assert found == [], f"a clean register does not pass:\n{support.show(found)}"
