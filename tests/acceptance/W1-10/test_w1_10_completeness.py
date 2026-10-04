"""KPI failure 1: a record present in git is missing from the graph.

Which files are records, and what a record without valid frontmatter does to a load, is package DP-1. The tests
marked "DP-1" follow its recommended option: a record is a tracked Markdown file whose YAML frontmatter carries an
``id``; one that cannot be loaded is listed in ``invalid`` by its path and stops nothing else from loading.
"""

from __future__ import annotations

import re
import shutil
import subprocess

import w1_10_support as support


def test_every_record_of_the_fixture_is_in_the_graph(api, graph):
    assert api.ids(graph.root) == support.RECORD_IDS


def test_a_record_committed_later_is_in_the_graph_after_a_load(api, repo):
    api.load(repo.root)
    support.write(repo.root, "docs/adr/ADR-0008-new.md",
                  support.record("ADR-0008", "decision", "ACTIVE", "New", depends_on=["ADR-0001"]))
    support.commit(repo.root, "a new decision", support.LATER)
    api.load(repo.root)
    assert "ADR-0008" in api.ids(repo.root)
    assert ("DEPENDS_ON", "ADR-0008", "ADR-0001") in support.triples(api.edges(repo.root, source="ADR-0008"))
    assert "ADR-0008" in api.active(repo.root, type="decision")


def test_a_changed_status_is_in_the_graph_after_a_load(api, repo):
    api.load(repo.root)
    support.write(repo.root, "docs/adr/ADR-0006-sixth.md", support.record("ADR-0006", "decision", "ACTIVE", "Sixth"))
    support.commit(repo.root, "the sixth decision is accepted", support.LATER)
    api.load(repo.root)
    assert "ADR-0006" in api.active(repo.root, type="decision")


def test_a_record_removed_from_git_leaves_the_graph(api, repo):
    """The graph is what git holds now: a load leaves no row of an earlier load behind."""
    api.load(repo.root)
    support.git(repo.root, "rm", "-q", "docs/adr/ADR-0002-second.md")
    support.commit(repo.root, "the second decision is withdrawn", support.LATER)
    api.load(repo.root)
    assert "ADR-0002" not in api.ids(repo.root)
    assert api.edges(repo.root, source="ADR-0002") == []
    assert "ADR-0003" in api.active(repo.root, type="decision"), "ADR-0003 is still superseded by a removed record"


def test_a_record_in_any_folder_is_in_the_graph(api, repo):
    """DP-1: a record is known by its frontmatter, not by its folder."""
    support.write(repo.root, "work/deep/er/NOTE-1.md", support.record("NOTE-1", "note", "ACTIVE", "A note"))
    support.commit(repo.root, "a record in an unusual folder", support.LATER)
    api.load(repo.root)
    found = {record["id"]: record["path"] for record in api.records(repo.root, type="note")}
    assert found == {"NOTE-1": "work/deep/er/NOTE-1.md"}


def test_a_file_without_record_frontmatter_is_not_a_record(api, graph):
    """DP-1: no frontmatter, or frontmatter without an ``id`` (a role file), is neither a record nor an error."""
    paths = {record["path"] for record in api.records(graph.root)}
    assert not paths & set(support.OTHER_FILES)
    assert not set(support.invalid_paths(graph.summary)) & set(support.OTHER_FILES)


def test_a_record_with_broken_frontmatter_is_reported_and_stops_no_other_record(api, repo):
    """DP-1: the load ends, every other record is in the graph, and the broken file is named by its path."""
    support.write(repo.root, "docs/adr/ADR-0010-broken.md", "---\nid: ADR-0010\ntype: [decision\nstatus: ACTIVE\n---\n")
    support.write(repo.root, "docs/adr/ADR-0011-open.md", "---\nid: ADR-0011\ntype: decision\nstatus: ACTIVE\n\nBody.\n")
    support.commit(repo.root, "two broken records", support.LATER)
    summary = api.load(repo.root)
    assert api.ids(repo.root) == support.RECORD_IDS
    assert support.invalid_paths(summary) == ["docs/adr/ADR-0010-broken.md", "docs/adr/ADR-0011-open.md"]


def test_a_record_without_a_required_key_is_reported_by_its_path(api, repo):
    """DP-1: ``id``, ``type`` and ``status`` are required (DEC-239); a record lacking one is not silently dropped."""
    support.write(repo.root, "docs/adr/ADR-0012-no-status.md", "---\nid: ADR-0012\ntype: decision\n---\n\nBody.\n")
    support.commit(repo.root, "a record without a status", support.LATER)
    summary = api.load(repo.root)
    assert support.invalid_paths(summary) == ["docs/adr/ADR-0012-no-status.md"]
    assert "ADR-0012" not in api.ids(repo.root)
    assert api.ids(repo.root) == support.RECORD_IDS


def test_a_record_without_state_class_is_loaded(api, repo):
    """The two committed ADRs lack ``state_class`` (W1-08 residual); the graph does not lose them for it."""
    support.write(repo.root, "docs/adr/ADR-0013-plain.md", "---\nid: ADR-0013\ntype: decision\nstatus: ACTIVE\n---\n")
    support.commit(repo.root, "a record without a state class", support.LATER)
    summary = api.load(repo.root)
    assert "ADR-0013" in api.ids(repo.root)
    assert support.invalid_paths(summary) == []


def test_a_file_git_does_not_track_is_not_in_the_graph(api, repo):
    """DP-1: the graph is derived from git; an untracked file is not a record."""
    support.write(repo.root, "docs/adr/ADR-0014-draft.md", support.record("ADR-0014", "decision", "ACTIVE", "Draft"))
    summary = api.load(repo.root)
    assert "ADR-0014" not in api.ids(repo.root)
    assert support.invalid_paths(summary) == []


def test_every_committed_ticket_and_adr_of_this_repository_is_in_the_graph(api, tmp_path):
    """The records this repository holds today, copied to a temporary repository (tickets and ADRs only)."""
    listing = subprocess.run(["git", "-C", str(support.REPO_ROOT), "ls-files", "-z", ".tickets/*.md", "docs/adr/*.md"],
                             capture_output=True, text=True, check=True).stdout
    names = sorted(name for name in listing.split("\0") if name)
    assert names, "this repository has no committed ticket or ADR"
    project = tmp_path / "live"
    project.mkdir()
    support.git(project, "init", "-q", "-b", "main")
    expected = {}
    for name in names:
        target = project / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(support.REPO_ROOT / name, target)
        found = re.search(r"^id:\s*(\S+)\s*$", target.read_text(encoding="utf-8").split("\n---", 1)[0], re.MULTILINE)
        assert found, f"{name} has no id in its frontmatter"
        expected[found.group(1)] = name
    support.commit(project, "the committed tickets and ADRs", support.LATER)
    api.load(project)
    loaded = {record["id"]: record["path"] for record in api.records(project)}
    missing = sorted(set(expected) - set(loaded))
    assert not missing, f"records present in git are missing from the graph: {missing}"
    assert loaded == expected
