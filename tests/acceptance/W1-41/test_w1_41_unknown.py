"""An unknown material artefact is never moved or deleted [CAP-06.c]; customer questions are decision packages
[CAP-44.b].

Failure line 4: "An unknown material artefact is moved or deleted". An unknown artefact is a tracked path that no
namespace of the project's path map holds (CAP-06's acceptance line: what ``gov doctor`` reports as unclassified).
It is named, it becomes a question to the customer, and it blocks destructive migration: of itself, and (the
contract item's words, "block destructive migration") of everything else while it is unknown.
"""

from __future__ import annotations

import re

import pytest

import w1_41_support as support

UNKNOWN_BYTES = b"\x00\x01harbour ledger, origin not known\n"


@pytest.fixture()
def unknown_project(tmp_path):
    return support.build_project(tmp_path / "with-unknown", extra={support.UNKNOWN: UNKNOWN_BYTES})


def _still_there(project):
    assert (project / support.UNKNOWN).read_bytes() == UNKNOWN_BYTES, f"{support.UNKNOWN} changed or is gone"
    assert support.at_head(project, support.UNKNOWN) == UNKNOWN_BYTES, f"{support.UNKNOWN} left HEAD or changed there"


def test_a2_names_the_unknown_artefact(unknown_project, adopt_in):
    adoption = adopt_in(unknown_project)
    adoption.through("A2")
    stage = adoption.stages["A2"]
    assert stage.front.get("unknown") == [support.UNKNOWN], \
        f"{stage.record}: 'unknown' is {stage.front.get('unknown')!r}, expected the one path no namespace holds"
    entries = support.entries_by_path(stage.front, stage.record)
    assert not entries[support.UNKNOWN].get("namespace"), \
        f"{stage.record}: the unknown artefact is given a namespace it does not have"


def test_the_unknown_artefact_becomes_a_decision_package_for_the_customer(unknown_project, adopt_in):
    """Success line 1: "customer questions as decision packages". The package is a record of the kernel's form
    (type, an open status, the sections a package is not sent without, DEC-093) and names the artefact."""
    adoption = adopt_in(unknown_project)
    adoption.through("A2")
    stage = adoption.stages["A2"]
    packages = stage.result.get("packages")
    assert isinstance(packages, list) and packages, "the A2 result lists no decision package for the unknown artefact"
    about = []
    for rel in packages:
        data = support.at_head(unknown_project, rel)
        assert data is not None, f"the decision package {rel} is not committed"
        text = data.decode("utf-8")
        front = support.frontmatter(text, rel)
        assert front.get("type") == "decision-package", f"{rel}: type is not 'decision-package'"
        assert front.get("status") == "PROPOSED", f"{rel}: an open package has the status PROPOSED (DEC-308)"
        assert isinstance(front.get("id"), str) and support.RECORD_ID_RE.match(front["id"]), f"{rel}: no record id"
        for heading in ("Question", "Options", "Recommendation", "Confidence"):
            assert re.search(rf"^##\s+{heading}\s*$", text, re.MULTILINE), f"{rel}: no section '{heading}'"
        confidence = re.split(r"^##\s+Confidence\s*$", text, flags=re.MULTILINE)[1].split("\n## ")[0]
        assert re.search(r"\b(low|medium|high)\b", confidence), f"{rel}: the confidence is not low, medium or high"
        if support.UNKNOWN in text:
            about.append(rel)
    assert about, f"no decision package names {support.UNKNOWN}: {packages}"


def test_a_project_without_unknown_artefacts_raises_no_package_about_one(adoption):
    adoption.through("A2")
    assert adoption.stages["A2"].result.get("packages") == [], \
        "the A2 result does not give an empty list of packages where nothing is unknown"


@pytest.mark.parametrize("action,target", [("MOVE", "archive/ledger.bin"), ("RENAME", "archive/ledger.dat"),
                                           ("RETIRE", None), ("DELETE_FROM_ACTIVE_TREE", None)])
def test_a_path_map_that_moves_or_deletes_the_unknown_artefact_is_refused(unknown_project, adopt_in, interface,
                                                                         action, target):
    adoption = adopt_in(unknown_project)
    adoption.through("A2")
    head = support.head(unknown_project)
    entries = [support.entry(support.UNKNOWN, action, target, batch=1 if target else None)]
    run = adoption.run("A3", *adoption.map_argument(entries))
    support.assert_refused(run, interface, support.UNKNOWN)
    assert support.head(unknown_project) == head, f"a path map was recorded\n{run.describe()}"
    _still_there(unknown_project)


def test_an_unknown_artefact_blocks_the_whole_destructive_migration(unknown_project, adopt_in, interface):
    """The path map leaves the unknown artefact where it is and moves other files; the auditor passed it. A6 still
    moves nothing while the artefact is unknown, and names it."""
    adoption = adopt_in(unknown_project)
    adoption.through("A5", support.moves_proposal())
    assert adoption.map_entries()[support.UNKNOWN].get("action") == "KEEP"
    baseline = support.tree(unknown_project)
    run = adoption.run("A6")
    support.assert_refused(run, interface, support.UNKNOWN)
    problems = support.moved_nothing(unknown_project, baseline, [item["path"] for item in support.moves_proposal()])
    assert not problems, f"files moved while an artefact is unknown: {problems}"
    _still_there(unknown_project)


def test_an_unknown_artefact_blocks_retirement_too(unknown_project, adopt_in, interface):
    """Retirement takes files out of the active tree: it is destructive. Nothing legacy is retired while an
    artefact is unknown."""
    adoption = adopt_in(unknown_project)
    adoption.through("A5", support.legacy_proposal())
    baseline = support.tree(unknown_project)
    legacy = [item["path"] for item in support.legacy_proposal()]
    for stage in ("A6", "A8"):
        run = adoption.run(stage)
        support.assert_refused(run, interface)
        problems = support.moved_nothing(unknown_project, baseline, legacy)
        assert not problems, f"stage {stage} retired files while an artefact is unknown: {problems}"
    _still_there(unknown_project)
