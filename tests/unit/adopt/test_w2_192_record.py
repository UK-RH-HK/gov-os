"""W2-192 S2, S3: what the AS record holds (specs with their class and evidence, modules, tickets, gaps with one question
each) and the lite checks A3 applies to it. Builder tests, regression evidence only (DEC-136)."""
from __future__ import annotations

import pytest

from gov.adopt import project, spec_audit

from .test_adopt import commit, sh, write
from .test_w2_192_support import (audited, build, by_path, config, head_commits, keep_all, record, refusal,  # noqa: F401
                                  repo, rewrite, spec, stage, through_a2)

BUILT, PARTLY, UNBUILT = "specs/built.md", "specs/partly.md", "docs/unbuilt.md"


def test_each_spec_is_in_its_class_with_its_evidence(repo):  # noqa: F811
    audited(repo)
    specs = by_path(record(repo)["specs"])
    assert sorted(specs) == sorted([BUILT, PARTLY, UNBUILT])
    built, partly, unbuilt = specs[BUILT], specs[PARTLY], specs[UNBUILT]
    assert (built["title"], built["wave"], built["status"], built["built"]) == ("Built spec", 1, "established", "built")
    assert built["evidence"] == {"code": ["src/alpha.py"], "tests": ["tests/test_alpha.py"],
                                 "commits": head_commits(repo, "src/alpha.py")}
    assert (partly["title"], partly["wave"], partly["status"], partly["built"]) == ("Partly built spec", None, None,
                                                                                      "partly built")
    assert partly["evidence"] == {"code": ["src/beta.py"], "tests": [], "commits": head_commits(repo, "src/beta.py")}
    assert (unbuilt["title"], unbuilt["wave"], unbuilt["built"]) == ("An unbuilt spec", 2, "not built")
    assert unbuilt["evidence"] == {"code": [], "tests": [], "commits": []}


def test_modules_tickets_and_the_lists_of_gaps(repo):  # noqa: F811
    audited(repo)
    head = record(repo)
    assert head["modules"] == ["src/alpha.py", "src/beta.py", "src/orphan.py"]
    assert head["tickets"] == [{"id": "T-1", "wave": 1, "done": True}, {"id": "T-2", "wave": 2, "done": False}]
    assert head["specs_without_code"] == [UNBUILT]
    assert head["code_without_spec"] == ["src/orphan.py"]


def test_each_gap_is_one_question_with_an_empty_answer(repo):  # noqa: F811
    audited(repo)
    gaps = record(repo)["gaps"]
    assert sorted(gap["subject"] for gap in gaps) == sorted([PARTLY, UNBUILT, "src/orphan.py"])  # once each
    for gap in gaps:
        assert isinstance(gap["question"], str) and gap["question"].strip() and gap["subject"] in gap["question"]
        assert gap["answer"] is None


def test_a_test_that_names_the_path_builds_a_spec_and_a_spec_with_no_test_is_partly_built(tmp_path):
    files = {".gitignore": ".gov-runtime/\n", "src/one.py": "x = 1\n", "src/two.py": "y = 2\n",
             "tests/test_named.py": "def test():\n    assert 'src/one.py'\n",
             "specs/a.md": spec("`src/one.py`\n", type="spec"), "specs/b.md": spec("`src/two.py`\n", type="spec")}
    root = build(tmp_path, files)
    audited(root)
    specs = by_path(record(root)["specs"])
    assert specs["specs/a.md"]["built"] == "built" and specs["specs/a.md"]["evidence"]["tests"] == ["tests/test_named.py"]
    assert specs["specs/b.md"]["built"] == "partly built" and specs["specs/b.md"]["evidence"]["tests"] == []


def test_a_spec_is_found_by_its_type_its_folder_or_its_namespace_and_never_by_its_name(tmp_path):
    files = {".gitignore": ".gov-runtime/\n", "README.md": "# not a spec\n", "notes/typed.md": spec("t\n", type="spec"),
             "specs/deep/in.md": "# In a specs folder\n", "design/spaced.md": "# By namespace\n",
             "docs/other.md": spec("o\n", type="note"), "docs/spec.md": "# named spec, not one\n"}
    root = build(tmp_path, files)
    conf = config({"specs": {"paths": ["design/**"], "embedding_policy": "not embedded"}})
    audited(root, conf)
    specs = by_path(record(root)["specs"])
    assert sorted(specs) == ["design/spaced.md", "notes/typed.md", "specs/deep/in.md"]
    assert specs["specs/deep/in.md"]["title"] == "In a specs folder"


def test_package_folders_under_src_are_modules_and_tests_never_are(tmp_path):
    files = {".gitignore": ".gov-runtime/\n", "src/pkg/__init__.py": "", "src/pkg/sub/deep.py": "z = 1\n",
             "src/top.py": "t = 1\n", "src/data/readme.txt": "no code\n", "tests/helper.py": "h = 1\n",
             "specs/s.md": spec("`src/pkg/deep_missing.py`\n", type="spec")}
    root = build(tmp_path, files)
    audited(root)
    head = record(root)
    assert head["modules"] == ["src/pkg", "src/top.py"]
    assert head["code_without_spec"] == ["src/pkg", "src/top.py"] or head["code_without_spec"] == ["src/top.py"]


def test_a_spec_that_names_a_file_of_a_module_names_that_module(tmp_path):
    files = {".gitignore": ".gov-runtime/\n", "src/pkg/__init__.py": "", "src/pkg/core.py": "z = 1\n",
             "specs/s.md": spec("`src/pkg/core.py`\n", type="spec")}
    root = build(tmp_path, files)
    audited(root)
    assert record(root)["code_without_spec"] == []


def test_a_named_path_that_is_not_tracked_is_not_evidence(tmp_path):
    files = {".gitignore": ".gov-runtime/\n", "specs/s.md": spec("`src/real.py` and `src/ghost.py`\n", type="spec"),
             "src/real.py": "r = 1\n"}
    root = build(tmp_path, files)
    audited(root)
    row = record(root)["specs"][0]
    assert row["evidence"]["code"] == ["src/real.py"] and row["built"] == "partly built"


# ------------------------------------------------------------------ the lite checks


def test_a_record_missing_a_module_is_refused_by_a3_naming_it(repo):  # noqa: F811
    audited(repo)
    rewrite(repo, lambda head: head["modules"].remove("src/beta.py"))
    head = sh(repo, "rev-parse", "HEAD")
    error = refusal(repo, "A3", "SPEC_AUDIT_INCOMPLETE", map=keep_all(repo))
    assert error.details["modules"] == ["src/beta.py"] and "src/beta.py" in error.message
    assert sh(repo, "rev-parse", "HEAD") == head and not (repo / project.record_path("A3")).exists()


def test_a_record_missing_a_spec_is_refused_by_a3_naming_it(repo):  # noqa: F811
    audited(repo)
    rewrite(repo, lambda head: head.update(specs=[row for row in head["specs"] if row["path"] != PARTLY]))
    error = refusal(repo, "A3", "SPEC_AUDIT_INCOMPLETE", map=keep_all(repo))
    assert error.details["specs"] == [PARTLY] and PARTLY in error.message


@pytest.mark.parametrize("change", [
    pytest.param(lambda gap: gap.update(question=""), id="empty"),
    pytest.param(lambda gap: gap.update(question="  "), id="blank"),
    pytest.param(lambda gap: gap.pop("question"), id="absent"),
    pytest.param(lambda gap: gap.update(question=None), id="null")])
def test_a_gap_without_a_question_is_refused_by_a3_naming_its_subject(repo, change):  # noqa: F811
    audited(repo)
    rewrite(repo, lambda head: change(next(gap for gap in head["gaps"] if gap["subject"] == "src/orphan.py")))
    error = refusal(repo, "A3", "GAP_WITHOUT_QUESTION", map=keep_all(repo))
    assert error.details["gaps"] == ["src/orphan.py"] and "src/orphan.py" in error.message
    assert not (repo / project.record_path("A3")).exists()


def test_the_check_runs_before_a3_reads_its_proposal(repo):  # noqa: F811
    audited(repo)
    rewrite(repo, lambda head: head["modules"].clear())
    refusal(repo, "A3", "SPEC_AUDIT_INCOMPLETE")  # no --map: the proposal's own refusal does not come first


def test_the_check_holds_the_inventory_not_the_working_tree(repo):  # noqa: F811
    audited(repo)
    write(repo, "src/late.py", "late = 1\n")
    write(repo, "specs/late.md", spec("`src/late.py`\n", type="spec"))
    commit(repo, "after the inventory")
    assert stage(repo, "A3", map=keep_all(repo))["stage"] == "A3"


def test_an_incomplete_record_is_never_committed_by_as(repo, monkeypatch):  # noqa: F811
    through_a2(repo)
    head = sh(repo, "rev-parse", "HEAD")
    original = spec_audit.audit  # an audit whose record leaves out the module the finder reports

    def fewer(*args):
        data = original(*args)
        data["modules"] = []
        return data

    monkeypatch.setattr(spec_audit, "find_modules", lambda paths: ["src/alpha.py"])
    monkeypatch.setattr(spec_audit, "audit", fewer)
    refusal(repo, "AS", "SPEC_AUDIT_INCOMPLETE")
    assert sh(repo, "rev-parse", "HEAD") == head and not (repo / spec_audit.RECORD).exists()
