"""W2-192 S1: stage AS stands after A2 and before A3 in the command and in the chain; A3 refuses to run before AS is
recorded; AS commits its record and nothing else. Builder tests, regression evidence only (DEC-136)."""
from __future__ import annotations

from gov.adopt import command, project

from .test_adopt import sh
from .test_w2_192_support import (audited, build, config, keep_all, record, refusal, repo, stage,  # noqa: F401
                                  through_a2)


def test_the_command_and_the_chain_list_as_between_a2_and_a3():
    assert command.STAGES.index("A2") < command.STAGES.index("AS") < command.STAGES.index("A3")
    assert project.STAGES.index("A2") + 1 == project.STAGES.index("AS") == project.STAGES.index("A3") - 1
    assert project.TITLES["AS"] == "spec audit" and project.record_path("AS") == "governance/adoption/AS-spec-audit.md"
    assert "AS" in command.__doc__.split("W2-192")[0]  # the usage line names it


def test_as_commits_its_record_and_only_that(repo):  # noqa: F811
    through_a2(repo)
    result = stage(repo, "AS", session="auditor-1")
    assert result["stage"] == "AS" and result["record"] == project.record_path("AS")
    assert sh(repo, "show", "--name-only", "--format=", "HEAD").split() == [project.record_path("AS")]
    head = record(repo)
    assert head["stage"] == "AS" and head["session"] == "auditor-1"
    a2 = project.sha256((repo / project.record_path("A2")).read_bytes())
    assert head["stands_on"] == a2
    assert sh(repo, "status", "--porcelain") == ""


def test_a3_before_as_is_refused_naming_as_and_writes_no_record(repo):  # noqa: F811
    through_a2(repo)
    head = sh(repo, "rev-parse", "HEAD")
    error = refusal(repo, "A3", "STAGE_MISSING", map=keep_all(repo))
    assert error.details["stage"] == "AS" and "AS" in error.message
    assert sh(repo, "rev-parse", "HEAD") == head and not (repo / project.record_path("A3")).exists()


def test_as_before_a2_is_refused_naming_a2_and_a3_with_a0_and_a1_names_a2(repo):  # noqa: F811
    stage(repo, "A0")
    stage(repo, "A1")
    assert refusal(repo, "AS", "STAGE_MISSING").details["stage"] == "A2"
    assert refusal(repo, "A3", "STAGE_MISSING", map=keep_all(repo)).details["stage"] == "A2"


def test_a3_after_as_with_an_all_keep_proposal_stands_on_the_as_record(repo):  # noqa: F811
    audited(repo)
    result = stage(repo, "A3", map=keep_all(repo))
    assert result["stage"] == "A3"
    assert record(repo, "A3")["stands_on"] == project.sha256((repo / project.record_path("AS")).read_bytes())


def test_a_project_with_no_spec_no_module_and_no_ticket_gets_a_record_with_empty_lists(tmp_path):
    root = build(tmp_path, {"README.md": "# p\n", ".gitignore": ".gov-runtime/\n"})
    audited(root)
    head = record(root)
    for key in ("specs", "modules", "tickets", "specs_without_code", "code_without_spec", "gaps"):
        assert head[key] == [], key
    assert stage(root, "A3", map=keep_all(root))["stage"] == "A3"


def test_the_later_stages_run_with_as_in_the_chain(repo):  # noqa: F811
    audited(repo)
    stage(repo, "A3", map=keep_all(repo))
    stage(repo, "A4")
    for name in ("A0", "A1", "A2", "AS", "A3", "A4"):
        assert (repo / project.record_path(name)).is_file()
    assert record(repo, "A4")["stands_on"] == project.sha256((repo / project.record_path("A3")).read_bytes())
