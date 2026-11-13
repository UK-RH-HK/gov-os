"""W2-129 S10 (incremental: the range, the mark, the standing count, --all, the refusal) and F5 (no finding older
than the mark is lost). Each case works on its own copy of repository A."""

from __future__ import annotations

import pytest
import w2_129_support as support
from w2_129_support import MARK

T005 = ".tickets/DAEO-t005.md"


def keyed(out: support.Output) -> set:
    return {(f.code, f.path, f.line, f.head) for f in out.findings}


def add_unknown_source(shas: dict, day: int) -> str:
    """A commit that adds the unknown DEC-996 to DAEO-t005's sources; its sha."""
    repo = shas["repo"]
    path = repo / T005
    path.write_text(path.read_text().replace("- DEC-100\n", "- DEC-100\n- DEC-996\n", 1))
    return support.commit(repo, "a source for DAEO-t005", {"Task": "DAEO-t005", "Implements": "DEC-100",
                                                           "Role": "orchestrator"}, day, [T005])


def test_s10_since_the_root_lists_every_finding_as_new_and_all_lists_the_same(since_root, every):
    new, listed = support.Output(since_root[1]), support.Output(every[1])
    assert new.findings and new.standing == 0, new.text()
    assert keyed(listed) == keyed(new)
    assert listed.new + listed.standing == len(listed.findings), listed.text()


def test_s10_with_no_mark_and_no_since_it_refuses_naming_since(fresh):
    repo = fresh["repo"]
    files = support.tree_digest(repo)
    done = support.run_links(repo)
    assert done.returncode == 2 and "--since" in done.stdout + done.stderr, done
    assert not (repo / MARK).exists() and support.tree_digest(repo) == files


def test_s10_the_mark_gives_the_range_and_standing_findings_are_counted_by_code_and_role(fresh):
    repo = fresh["repo"]
    first = support.links(repo, "--since", fresh["root"])
    judged = support.git(repo, "rev-parse", "HEAD")
    assert judged.startswith((repo / MARK).read_text().strip())
    add_unknown_source(fresh, 10)
    out = support.links(repo)
    assert out.code == 1 and out.new == 1 and len(out.findings) == 1, out.text()
    assert len(out.since) >= 7 and judged.startswith(out.since), out.first
    finding = out.findings[0]
    assert finding.code == "UNKNOWN_ID" and finding.names("DEC-996") and finding.path == T005, finding
    assert out.standing == len(first.findings), (out.first, len(first.findings))
    said = out.done.stdout
    standing_codes = {f.code for f in first.findings} - {"UNKNOWN_ID"}
    assert standing_codes and all(code in said for code in standing_codes), said
    assert all(role in said for role in ("product-spec", "engineer", "independent-test-designer")), said


def test_s10_a_finding_older_than_the_mark_is_counted_on_the_next_run_and_listed_with_all(fresh):
    """F5: the new finding of one run is standing on the next, counted, and listed by --all."""
    repo = fresh["repo"]
    first = support.links(repo, "--since", fresh["root"])
    add_unknown_source(fresh, 10)
    support.links(repo)  # the run that lists DEC-996 as new and moves the mark
    again = support.links(repo)
    assert again.code == 0 and again.new == 0 and again.findings == [], again.text()
    assert again.standing == len(first.findings) + 1, again.first
    listed = support.links(repo, "--all")
    assert len(listed.findings) == len(first.findings) + 1, listed.text()
    assert listed.of("UNKNOWN_ID", "DEC-996", path=T005)


def test_s10_a_changed_register_entry_lists_its_own_findings_and_those_of_the_entries_it_names(fresh):
    repo = fresh["repo"]
    support.run_links(repo, "--since", fresh["root"])
    register = repo / support.REGISTER
    register.write_text(register.read_text().replace("The second item is new.\n",
                                                     "The second item is new.\nIt holds from today.\n", 1))
    support.commit(repo, "DEC-104's text", {"Task": "decision-record", "Implements": "DEC-104",
                                           "Role": "orchestrator"}, 10, [support.REGISTER])
    out = support.links(repo)
    assert out.of("UNMARKED_CHANGE", "DEC-103", "DEC-104"), out.text()
    for changed, changer in (("DEC-101", "DEC-102"), ("DEC-109", "DEC-110"), ("DEC-111", "DEC-112")):
        assert not out.of("UNMARKED_CHANGE", changed, changer), out.text()
    assert not out.of("NOT_IN_FORCE_AS_RULE", "DEC-120", path=support.REGISTER), out.text()
    assert out.standing and out.standing > 0, out.first


def test_s10_a_commit_in_the_range_is_judged(fresh):
    repo = fresh["repo"]
    support.run_links(repo, "--since", fresh["root"])
    support.write(repo, "src/app/other.py", "def other():\n    return 2\n")
    sha = support.commit(repo, "another feature", {"Task": "DAEO-t005", "Implements": "DEC-121", "Role": "engineer"},
                         10, ["src/app/other.py"])
    out = support.links(repo)
    found = [f for f in out.of("NOT_IN_FORCE_AS_RULE", "DEC-121") if sha[:7] in f.raw or "Implements" in f.raw]
    assert found and all("engineer" in f.role for f in found), out.text()
    assert out.of("UNLINKED_ID", "DEC-121"), out.text()
    assert not out.of("UNMARKED_CHANGE"), out.text()


@pytest.mark.parametrize("args", [["--since", "HEAD~1"], ["--all"]], ids=["since", "all"])
def test_s10_since_and_all_each_move_the_mark_to_the_head_judged(fresh, args):
    repo = fresh["repo"]
    support.run_links(repo, *args)
    assert support.git(repo, "rev-parse", "HEAD").startswith((repo / MARK).read_text().strip())
