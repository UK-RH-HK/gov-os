"""FR-1 (DAEO-ma4q, fix ``forbidden-reach``): who holds a cited forbidden source, in the cases beyond the K-line's Verify:
the order of the rules, D3's classifier where the tree has it, and the flags' faults. Everything is planted under
``tmp_path``."""

from __future__ import annotations

import json
import subprocess
import sys
import types

import pytest
import yaml

from gov.memaudit import __main__ as cli

from .conftest import AUDIT

OUT = {"lexical_policy": "not indexed", "embedding_policy": "not embedded"}


class Reach:
    def __init__(self, base):
        self.repo, self.sets = base / "repo", base / "sets"
        self.repo.mkdir()
        self.sets.mkdir()
        self.git("init", "-q")

    def git(self, *args):
        subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True)

    @staticmethod
    def write(path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def track(self, *rels):
        for rel in rels:
            self.write(self.repo / rel, "a line\n")
            self.git("add", rel)

    def namespaces(self, **spaces):
        self.write(self.repo / "governance/project/path-map.yaml",
                   yaml.safe_dump({"version": 1, "namespaces": spaces}, sort_keys=False))

    def miss(self, *paths, qid="q01"):
        self.write(self.sets / "fixtures/evaluation" / AUDIT / "hidden" / f"{qid}.yaml",
                   yaml.safe_dump({"id": qid, "forbidden": list(paths)}))
        cites = [{"path": p, "start_line": 1, "end_line": 1} for p in paths]
        self.write(self.sets / "runs" / AUDIT / "reader" / f"{qid}.json", json.dumps(
            {"id": qid, "forbidden_cited": True,
             "attempts": [{"attempt": 1, "verdict": "answer", "citations": cites}]}))

    def run(self, capsys, repo=None):
        code = cli.main(["forbidden-reach", "--sets-root", str(self.sets), "--audit", AUDIT,
                         "--repo", str(repo or self.repo)])
        return code, capsys.readouterr().out.splitlines()


@pytest.fixture
def reach(tmp_path):
    return Reach(tmp_path)


def line(cited, outside, inside, holders):
    return (0, [f"FORBIDDEN-REACH {cited} cited, {outside} outside, {inside} inside; {holders}"])


def test_a_stale_class_without_either_policy_counts_as_outside(reach, capsys):
    reach.namespaces(old={"paths": ["old/**"], "stale_class": "legacy"})
    reach.track("old/a.md")
    reach.miss("old/a.md")
    assert reach.run(capsys) == line(1, 1, 0, "old: 1")


def test_an_untracked_file_is_held_by_untracked_also_under_an_excluding_namespace(reach, capsys):
    reach.namespaces(old={"paths": ["old/**"], "stale_class": "legacy", **OUT})
    reach.write(reach.repo / "old/a.md", "never added\n")
    reach.miss("old/a.md")
    assert reach.run(capsys) == line(1, 1, 0, "untracked: 1")


@pytest.mark.parametrize("first, second", [({"stale_class": "legacy"}, OUT), (OUT, {"stale_class": "legacy"}),
                                           (OUT, OUT), ({"stale_class": "legacy"}, {"stale_class": "historical"})])
def test_of_two_excluding_namespaces_the_first_in_the_map_holds_the_file_once(reach, capsys, first, second):
    reach.namespaces(zed={"paths": ["old/**"], **first}, abc={"paths": ["old/**"], **second})
    reach.track("old/a.md")
    reach.miss("old/a.md")
    assert reach.run(capsys) == line(1, 1, 0, "zed: 1")


def test_a_tracked_link_into_a_not_indexed_namespace_is_outside(reach, capsys):
    reach.namespaces(live={"paths": ["live/**"]}, shut={"paths": ["shut/**"], **OUT})
    reach.track("shut/a.md")
    (reach.repo / "live").mkdir()
    (reach.repo / "live/link.md").symlink_to("../shut/a.md")
    reach.git("add", "live/link.md")
    reach.miss("live/link.md")
    assert reach.run(capsys) == line(1, 1, 0, "shut: 1")


def test_d3s_classifier_is_asked_where_the_tree_has_it(reach, capsys, monkeypatch):
    """A stand-in for ``gov.retrieval.stale`` that calls every file stale: its answer is the one printed."""
    stub = types.ModuleType("gov.retrieval.stale")
    stub.classifier = lambda root: lambda rel: ("other", "legacy")
    monkeypatch.setitem(sys.modules, "gov.retrieval.stale", stub)
    reach.namespaces(live={"paths": ["live/**"]}, other={"paths": ["other/**"]})
    reach.track("live/a.md")
    reach.miss("live/a.md")
    assert reach.run(capsys) == line(1, 1, 0, "other: 1")


def test_a_repo_folder_below_the_top_level_reads_the_whole_repository(reach, capsys):
    reach.namespaces(live={"paths": ["live/**"]})
    reach.track("live/a.md")
    reach.miss("live/a.md")
    assert reach.run(capsys, repo=reach.repo / "live") == line(1, 0, 1, "live: 1")


def test_a_repo_inside_the_sets_root_is_a_usage_fault(reach, capsys):
    reach.miss("live/a.md")
    inner = reach.sets / "repo"
    inner.mkdir()
    subprocess.run(["git", "-C", str(inner), "init", "-q"], check=True)
    assert reach.run(capsys, repo=inner) == (4, ["ERROR: UsageError"])
