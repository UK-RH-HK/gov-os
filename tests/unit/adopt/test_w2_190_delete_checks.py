"""W2-190: A3 refuses DELETE_FROM_ACTIVE_TREE of a file another tracked file names (DELETE_REFERENCED) or one classed
superseded (DELETE_SUPERSEDED). Builder tests, regression evidence only (DEC-136): a git repository built in
``tmp_path``; only the code graph and the index refresh are replaced, by the ``root`` fixture, as in W1-41's tests."""
from __future__ import annotations

import pytest

from gov.adopt import project, stages

from .test_adopt import PATHS, commit, config, proposal, refused, sh, stage, write  # noqa: F401
from .test_adopt import root  # noqa: F401  (a fixture)

OLD, NEW = "docs/plans/0003-storage-migration.md", "docs/plans/0007-storage-migration.md"
DELETE = {"action": "DELETE_FROM_ACTIVE_TREE"}


def delete(*paths, **more):
    return [{"path": path, **DELETE, **more} for path in paths]


def adopt(root, *entries, conf=None):
    """A0 to A2 on what the repository holds, then A3 with a proposal of ``entries``: the result, or the refusal."""
    for name in ("A0", "A1", "A2"):
        stage(root, name, conf=conf)
    return stage(root, "A3", conf=conf, map=proposal(root, *entries))


def refusal(root, *entries, conf=None):
    """The problems of the refusal of a proposal (and the proof that nothing was recorded)."""
    for name in ("A0", "A1", "A2"):
        stage(root, name, conf=conf)
    head = sh(root, "rev-parse", "HEAD")
    error = refused("PROPOSAL_REFUSED", root, "A3", conf=conf, map=proposal(root, *entries))
    assert sh(root, "rev-parse", "HEAD") == head and not (root / project.record_path("A3")).exists()
    return error.details["problems"]


def codes(problems, path=None):
    return sorted(item["code"] for item in problems if "code" in item and path in (None, item["path"]))


def add(root, files):
    for rel, text in files.items():
        write(root, rel, text)
    commit(root, "fixture: " + ", ".join(files))


# ------------------------------------------------------------------ DELETE_REFERENCED


def test_a_delete_of_a_file_another_names_is_refused_naming_it_and_records_nothing(root):  # noqa: F811
    add(root, {OLD: "# plan 0003\n", NEW: f"# plan 0007\n\nThis plan supersedes plan 0003 (`{OLD}`).\n"})
    problems = refusal(root, *delete(OLD))
    [problem] = problems
    assert problem["path"] == OLD and problem["code"] == "DELETE_REFERENCED"
    assert problem["referenced_by"] == [NEW] and "DELETE_REFERENCED" in problem["reason"] and NEW in problem["reason"]


def test_every_referencing_file_is_named(root):  # noqa: F811
    add(root, {OLD: "x\n", NEW: f"see {OLD}\n", "README.md": f"- [old]({OLD})\n", "lib/note.py": f"# {OLD}\n"})
    [problem] = refusal(root, *delete(OLD))
    assert problem["referenced_by"] == sorted([NEW, "README.md", "lib/note.py"])


def test_retire_and_keep_of_a_referenced_file_are_accepted_and_so_is_an_unreferenced_delete(root):  # noqa: F811
    add(root, {OLD: "x\n", NEW: f"see {OLD}\n", "docs/loose.md": "nothing names me\n"})
    result = adopt(root, {"path": OLD, "action": "RETIRE", "kind": "rule-file"}, *delete("docs/loose.md", batch=2))
    assert result["stage"] == "A3"
    assert [item["batch"] for item in project.frontmatter(
        (root / result["record"]).read_text())["artefacts"] if item["path"] == "docs/loose.md"] == [2]


def test_a_problem_of_the_entry_and_a_delete_problem_are_both_listed(root):  # noqa: F811
    add(root, {OLD: "x\n", NEW: f"see {OLD}\n"})
    problems = refusal(root, *delete(OLD, batch="soon"))
    assert codes(problems) == ["DELETE_REFERENCED"] and len(problems) == 2
    assert {item["path"] for item in problems} == {OLD} and any("batch" in item["reason"] for item in problems)


def test_the_message_names_the_code_and_the_path(root):  # noqa: F811
    add(root, {OLD: "x\n", NEW: f"see {OLD}\n"})
    for name in ("A0", "A1", "A2"):
        stage(root, name)
    error = refused("PROPOSAL_REFUSED", root, "A3", map=proposal(root, *delete(OLD)))
    assert OLD in error.message and "DELETE_REFERENCED" in error.message


# ------------------------------------------------------------------ what is no reference (F2)


def test_a_mention_in_the_file_itself_the_adoptions_records_or_a_file_also_deleted_is_no_reference(root):  # noqa: F811
    add(root, {"docs/self.md": "I am docs/self.md\n", "docs/a.md": "see docs/b.md\n", "docs/b.md": "see docs/a.md\n"})
    result = adopt(root, *delete("docs/self.md", "docs/a.md", "docs/b.md"))  # A1's record lists every path
    assert result["stage"] == "A3"


def test_a_path_that_only_shares_a_suffix_is_no_reference(root):  # noqa: F811
    add(root, {"x.md": "x\n", "docs/a/x.md": "y\n", "docs/b.md": "see docs/a/x.md and my-x.md and x.mdx and x.md/y\n"})
    assert adopt(root, *delete("x.md"), conf=config(paths=(*PATHS, "x.md")))["stage"] == "A3"


@pytest.mark.parametrize("text", [f"`{OLD}`", f"({OLD})", f"{OLD} is old", f"see {OLD}.", f"see {OLD}.\n", f"{OLD}:",
                                  f"{OLD}#top", f'"{OLD}"', f"see {OLD}", f"- {OLD}\n", f"{OLD}, {OLD}"])
def test_the_path_counts_where_its_boundaries_are_not_path_characters(text):
    assert stages._mentions(text, OLD)


@pytest.mark.parametrize("text", [f"docs/a/{OLD}", f"x{OLD}", f"_{OLD}", f"-{OLD}", f".{OLD}", f"{OLD}x", f"{OLD}x.md",
                                  f"{OLD}/y", f"{OLD}.gz", f"{OLD}-old", f"{OLD}_2", "docs/plans/0003", "other.md"])
def test_the_path_does_not_count_inside_a_longer_path(text):
    assert not stages._mentions(text, OLD)


def test_the_boundaries_with_a_short_root_path():
    assert stages._mentions("x.md is here", "x.md") and stages._mentions("(x.md).", "x.md")
    assert not stages._mentions("docs/a/x.md", "x.md") and not stages._mentions("x.mdx", "x.md")
    assert not stages._mentions("x.md/y", "x.md")


def test_a_file_that_is_no_text_is_skipped(root):  # noqa: F811
    for rel, data in {"lib/nul.bin": b"docs/old.md\0\1", "lib/latin.bin": b"\xff\xfe docs/old.md\n"}.items():
        (root / rel).write_bytes(data)
    commit(root, "binaries")
    assert adopt(root, *delete("docs/old.md"))["stage"] == "A3"


def test_a_glob_of_the_path_map_is_no_mention_and_an_exact_path_in_it_is(root):  # noqa: F811
    holds = (*PATHS, "governance/project/*")
    add(root, {"governance/project/path-map.yaml": "namespaces:\n  all:\n    paths: ['docs/**', '*.md']\n"})
    assert adopt(root, *delete("docs/old.md"), conf=config(paths=holds))["stage"] == "A3"


def test_an_exact_path_in_the_path_map_is_a_mention(root):  # noqa: F811
    holds = (*PATHS, "governance/project/*")
    add(root, {"governance/project/path-map.yaml": "namespaces:\n  all:\n    paths: ['docs/old.md']\n"})
    [problem] = refusal(root, *delete("docs/old.md"), conf=config(paths=holds))
    assert problem["referenced_by"] == ["governance/project/path-map.yaml"]


# ------------------------------------------------------------------ DELETE_SUPERSEDED


def head(**front):
    lines = [f"{key}: {value}" for key, value in front.items()]
    return "---\n" + "\n".join(lines) + "\n---\n\n# a record\n"


@pytest.mark.parametrize("status", ["SUPERSEDED", "superseded", "Superseded"])
def test_a_file_whose_status_is_superseded_in_any_case_is_refused(root, status):  # noqa: F811
    add(root, {"docs/old-spec.md": head(id="SPEC-1", type="spec", status=status)})
    [problem] = refusal(root, *delete("docs/old-spec.md"))
    assert problem["code"] == "DELETE_SUPERSEDED" and problem["status"] == status and problem["superseded_by"] == []
    assert "DELETE_SUPERSEDED" in problem["reason"] and status in problem["reason"]


def test_the_target_of_a_supersedes_edge_is_refused_naming_the_source_record(root):  # noqa: F811
    add(root, {"docs/spec-1.md": head(id="SPEC-1", type="spec", status="ACTIVE"),
               "docs/spec-2.md": head(id="SPEC-2", type="spec", status="ACTIVE", supersedes="[SPEC-1]")})
    [problem] = refusal(root, *delete("docs/spec-1.md"))
    assert problem["code"] == "DELETE_SUPERSEDED" and problem["superseded_by"] == ["SPEC-2"] and problem["status"] is None
    assert "SPEC-2" in problem["reason"]


def test_a_record_that_says_superseded_by_is_refused(root):  # noqa: F811
    add(root, {"docs/spec-1.md": head(id="SPEC-1", type="spec", status="ACTIVE", superseded_by="[SPEC-2]"),
               "docs/spec-2.md": head(id="SPEC-2", type="spec", status="ACTIVE")})
    [problem] = refusal(root, *delete("docs/spec-1.md"))
    assert problem["code"] == "DELETE_SUPERSEDED" and problem["superseded_by"] == ["SPEC-2"]


def test_the_successor_is_not_refused_for_superseding(root):  # noqa: F811
    add(root, {"docs/spec-1.md": head(id="SPEC-1", type="spec", status="ACTIVE"),
               "docs/spec-2.md": head(id="SPEC-2", type="spec", status="ACTIVE", supersedes="[SPEC-1]")})
    assert adopt(root, *delete("docs/spec-2.md"))["stage"] == "A3"


def test_a_file_both_referenced_and_superseded_gets_both_problems_with_their_evidence(root):  # noqa: F811
    add(root, {OLD: head(id="PLAN-3", type="plan", status="superseded"), NEW: f"This plan replaces `{OLD}`.\n"})
    problems = refusal(root, *delete(OLD))
    assert codes(problems, OLD) == ["DELETE_REFERENCED", "DELETE_SUPERSEDED"]
    referenced, superseded = sorted(problems, key=lambda item: item["code"])
    assert referenced["referenced_by"] == [NEW] and superseded["status"] == "superseded"


def test_a_successor_naming_the_old_file_in_prose_without_front_matter_is_only_referenced(root):  # noqa: F811
    add(root, {OLD: "# plan\n", NEW: f"# plan 7\n\nReplaces {OLD}.\n"})
    assert codes(refusal(root, *delete(OLD))) == ["DELETE_REFERENCED"]


# ------------------------------------------------------------------ an unreadable record


def test_one_unreadable_record_does_not_refuse_a_delete_that_has_nothing_to_do_with_it(root):  # noqa: F811
    add(root, {"docs/bad.md": "---\nid: [unclosed\n---\n\n# bad\n"})
    assert adopt(root, *delete("docs/old.md"))["stage"] == "A3"


def test_the_deleted_files_own_unreadable_front_matter_is_read_as_no_status(root):  # noqa: F811
    add(root, {"docs/bad.md": "---\nstatus: [superseded\n---\n\n# bad\n"})
    assert adopt(root, *delete("docs/bad.md"))["stage"] == "A3"


def test_a_delete_of_a_file_that_is_no_markdown_is_not_read_for_status(root):  # noqa: F811
    (root / "lib/latin.bin").write_bytes(b"\xff\xfe")
    commit(root, "binary")
    assert adopt(root, *delete("lib/latin.bin"))["stage"] == "A3"


def test_the_record_graph_is_not_read_for_a_proposal_without_a_delete(root, monkeypatch):  # noqa: F811
    def graph(*args, **more):
        raise AssertionError("the record graph is read")

    monkeypatch.setattr(project, "record_graph", graph)
    assert adopt(root, {"path": "docs/old.md", "action": "KEEP"})["stage"] == "A3"
