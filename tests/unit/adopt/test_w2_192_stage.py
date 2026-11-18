"""W2-192 S1: stage AS stands after A2 and before A3 in the command and in the chain; A3 refuses to run before AS is
recorded; AS commits its record and nothing else. Builder tests, regression evidence only (DEC-136)."""
from __future__ import annotations

from gov.adopt import command, project, spec_audit

from .test_adopt import commit, sh
from .test_w2_192_support import (audited, build, config, keep_all, record, refusal, repo, rewrite,  # noqa: F401
                                  stage, through_a2)


def test_the_command_lists_as_between_a2_and_a3_and_the_chain_does_not():
    assert command.STAGES.index("A2") < command.STAGES.index("AS") < command.STAGES.index("A3")
    assert "AS" not in project.STAGES and "AS" not in project.TITLES
    assert spec_audit.TITLE == "spec audit" and spec_audit.RECORD == "governance/adoption/AS-spec-audit.md"
    assert "AS" in command.__doc__.split("W2-192")[0]  # the usage line names it


def test_as_commits_its_record_and_only_that(repo):  # noqa: F811
    through_a2(repo)
    result = stage(repo, "AS", session="auditor-1")
    assert result["stage"] == "AS" and result["record"] == spec_audit.RECORD
    assert sh(repo, "show", "--name-only", "--format=", "HEAD").split() == [spec_audit.RECORD]
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


def test_a3_after_as_stands_on_a2_and_cites_the_as_record(repo):  # noqa: F811
    audited(repo)
    result = stage(repo, "A3", map=keep_all(repo))
    assert result["stage"] == "A3"
    a3 = record(repo, "A3")
    assert a3["stands_on"] == project.sha256((repo / project.record_path("A2")).read_bytes())
    assert a3["spec_audit"] == project.sha256((repo / spec_audit.RECORD).read_bytes())


def test_a3_with_an_as_record_not_standing_on_a2_as_it_is_now_is_refused_naming_as(repo):  # noqa: F811
    audited(repo)
    stage(repo, "A2", session="another")  # A2 run again after AS: AS stands on the A2 record that was
    head = sh(repo, "rev-parse", "HEAD")
    error = refusal(repo, "A3", "CHAIN_BROKEN", map=keep_all(repo))
    assert error.details["stage"] == "AS" and "AS" in error.message and "run AS again" in error.message
    assert sh(repo, "rev-parse", "HEAD") == head and not (repo / project.record_path("A3")).exists()


def test_a3_with_an_as_record_whose_stands_on_is_edited_is_refused_naming_as(repo):  # noqa: F811
    audited(repo)
    rewrite(repo, lambda head: head.update(stands_on="0" * 64))
    assert refusal(repo, "A3", "CHAIN_BROKEN", map=keep_all(repo)).details["stage"] == "AS"
    assert not (repo / project.record_path("A3")).exists()


def test_a3_with_an_as_record_of_another_stage_is_refused_naming_as(repo):  # noqa: F811
    audited(repo)
    path = repo / spec_audit.RECORD
    path.write_text(path.read_text(encoding="utf-8").replace("stage: AS", "stage: A2", 1), encoding="utf-8")
    commit(repo, "the AS record names another stage")
    assert refusal(repo, "A3", "CHAIN_BROKEN", map=keep_all(repo)).details["stage"] == "AS"


def test_as_before_a2_is_refused_naming_a2_in_a_message_about_as(repo):  # noqa: F811
    stage(repo, "A0")
    stage(repo, "A1")
    error = refusal(repo, "AS", "STAGE_MISSING")
    assert error.details["stage"] == "A2" and error.message.startswith("stage AS stands on stage A2")


def test_a_project_with_no_spec_no_module_and_no_ticket_gets_a_record_with_empty_lists(tmp_path):
    root = build(tmp_path, {"README.md": "# p\n", ".gitignore": ".gov-runtime/\n"})
    audited(root)
    head = record(root)
    for key in ("specs", "modules", "tickets", "specs_without_code", "code_without_spec", "gaps"):
        assert head[key] == [], key
    assert stage(root, "A3", map=keep_all(root))["stage"] == "A3"


def test_the_later_stages_run_after_as_and_stand_on_the_chain_without_it(repo):  # noqa: F811
    audited(repo)
    stage(repo, "A3", map=keep_all(repo))
    stage(repo, "A4")
    for name in ("A0", "A1", "A2", "A3", "A4"):
        assert (repo / project.record_path(name)).is_file()
    assert (repo / spec_audit.RECORD).is_file()
    assert record(repo, "A4")["stands_on"] == project.sha256((repo / project.record_path("A3")).read_bytes())


def test_a_repository_adopted_before_as_goes_on_after_a3_without_the_as_record(repo):  # noqa: F811
    audited(repo)
    stage(repo, "A3", map=keep_all(repo))
    sh(repo, "rm", "-q", "--", spec_audit.RECORD)
    commit(repo, "the repository as it was adopted before AS")
    assert stage(repo, "A4")["stage"] == "A4"
    records, hashes = project.chain(repo, project.tree(repo), "A5")  # what a later stage walks
    assert list(records) == ["A0", "A1", "A2", "A3", "A4"] and set(hashes) == set(records)
    assert stage(repo, "AS")["stage"] == "AS"  # AS can be run there at any later time: its chain is A0-A2
    assert record(repo)["stands_on"] == hashes["A2"]
