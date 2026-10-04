"""KPI success 3 and failure 2: files stay byte-identical; the checker never rewrites a decision file.

Each test loads the store, takes a snapshot, runs the check alone and takes a second snapshot: every file of the
tree outside ``.git/`` by the sha256 of its bytes, the commit, the refs, the index and the git status.
"""

from __future__ import annotations

import w1_11_support as support
from w1_11_support import AGENT, adr_path, decision, package, package_path, ticket, ticket_path

# Every finding the checker can raise, in one tree.
EVERY_HAZARD = {
    adr_path("ADR-0010"): decision("ADR-0010", "ACTIVE"),
    adr_path("ADR-0011"): decision("ADR-0011", "ACTIVE", supersedes=["ADR-0010"]),
    "docs/adr/ADR-0020.md": decision("ADR-0020", "PROPOSED"),
    "decisions/ADR-0020.md": decision("ADR-0020", "PROPOSED"),
    "decisions/DEC-0030.md": decision("DEC-0030", "PROPOSED"),
    "docs/adr/ADR-0030.md": decision("ADR-0030", "PROPOSED"),
    adr_path("ADR-0040"): decision("ADR-0040", "SUPERSEDED", supersedes=["ADR-0041"]),
    adr_path("ADR-0041"): decision("ADR-0041", "SUPERSEDED", supersedes=["ADR-0040"]),
    ticket_path("PROJ-aaaa"): ticket("PROJ-aaaa", approval=["DP-0001"], cit="CIT-0007"),
    package_path("DP-0001"): package("DP-0001", "DECLINED", "CIT-0007", constrains=["PROJ-aaaa"]),
}

# Decision files a tool that parses and writes back would not reproduce: CRLF line ends, no final newline, a
# byte-order mark, trailing blanks, a comment and odd spacing in the frontmatter, and frontmatter that is broken.
ODD_FILES = {
    "docs/adr/ADR-0050-crlf.md": decision("ADR-0050", "ACTIVE").replace("\n", "\r\n"),
    "docs/adr/ADR-0051-no-newline.md": decision("ADR-0051", "ACTIVE", supersedes=["ADR-0050"]).rstrip("\n"),
    "docs/adr/ADR-0052-bom.md": "﻿" + decision("ADR-0052", "PROPOSED"),
    "docs/adr/ADR-0053-spacing.md": ("---\nid:    ADR-0053   \ntype: decision\nstatus:   ACTIVE   # set by hand\n"
                                     "state_class: AUTHORITATIVE\nsupersedes:\n    -   ADR-0054\n\n\n---\n"
                                     "# ADR-0053   \n\n\n\nBody with trailing blanks.   \n\t\n"),
    "docs/adr/ADR-0054-superseded.md": decision("ADR-0054", "ACTIVE", superseded_by="ADR-0053"),
    "docs/adr/ADR-0055-broken.md": "---\nid: ADR-0055\nstatus: [ACTIVE\n---\n\nBroken frontmatter.\n",
    "docs/adr/ADR-0056-unclosed.md": "---\nid: ADR-0056\ntype: decision\nstatus: ACTIVE\n\nNever closed.\n",
}


def check_and_compare(api, project):
    api.load(project.root)
    before = support.snapshot(project.root)
    found = api.check_only(project.root)
    return found, support.changed(before, support.snapshot(project.root))


def test_a_check_that_finds_nothing_leaves_every_file_byte_identical(api, project):
    project.put(support.CLEAN)
    _, differences = check_and_compare(api, project)
    assert differences == []


def test_a_check_that_finds_every_hazard_leaves_every_file_byte_identical(api, project):
    project.put({**support.CLEAN, **EVERY_HAZARD}, who=AGENT)
    found, differences = check_and_compare(api, project)
    assert found, "nothing was flagged"
    assert differences == []


def test_decision_files_a_rewrite_would_not_reproduce_stay_byte_identical(api, project):
    project.put({**support.CLEAN, **ODD_FILES}, who=AGENT)
    found, differences = check_and_compare(api, project)
    assert found, "nothing was flagged"
    assert differences == []


def test_uncommitted_work_in_the_tree_is_left_as_it_is(api, project):
    """A modified decision file, a staged one and an untracked one: none is touched, staged or committed."""
    project.put({**support.CLEAN, **EVERY_HAZARD}, who=AGENT)
    project.write(adr_path("ADR-0010"), decision("ADR-0010", "ACTIVE", body="Edited, not committed."))
    project.write(adr_path("ADR-0060"), decision("ADR-0060", "ACTIVE"))
    project.write(adr_path("ADR-0061"), decision("ADR-0061", "ACTIVE", supersedes=["ADR-0060"]))
    support.git(project.root, "add", adr_path("ADR-0061"))
    _, differences = check_and_compare(api, project)
    assert differences == []


def test_a_second_check_leaves_every_file_byte_identical_too(api, project):
    project.put({**support.CLEAN, **EVERY_HAZARD}, who=AGENT)
    api.load(project.root)
    before = support.snapshot(project.root)
    first = api.check_only(project.root)
    second = api.check_only(project.root)
    assert first == second
    assert support.changed(before, support.snapshot(project.root)) == []
