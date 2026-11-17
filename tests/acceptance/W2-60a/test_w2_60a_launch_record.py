"""W2-60a, KPI success 8 and failure 2 -- one launch record per launch, written before the session starts.

KPI success 8 [DEC-826 Q1, CAP-36.a lite, lens F R6]: "Every launch writes one
launch record, keyed by the session id the launcher gives with --session-id,
before the session starts: role, ticket, the ticket's class, model, effort,
subagent model, threshold none, the role text's and each skill's version and
hash, the CLI's version and the start time; in one folder every worktree of the
repository shares, stated in the CIT-E; a record that cannot be written refuses
the launch". KPI failure 2: "a launch with no record, or a record naming
another session".

From the design (Behaviour 9): the record is ``<session id>.json`` in
``.gov-runtime/launches/`` of the repository's main checkout, found from the
tree's ``.git`` without running git; written whole before the session starts;
created only if no file of that name exists; a record that cannot be written
refuses the launch, and a CLI that then cannot be started removes it.
(Emergency 2, release 0.1.2: the settings no longer deny the folder to the
session by two literal rules; that half of the cases is retired.) The CLI's version is
read from the name of the file the CLI's link resolves to (``.../versions/<v>``),
never by running it; "not measured: <why>" when it is not such a link.

Resume (Behaviour 8, as the lead's live measurement corrected it): ``--resume
<id>`` (``--resume=<id>``, ``-r <id>``) after ``--`` is passed unchanged, the
launcher adds ``--session-id <a new UUID> --fork-session``, and the new record,
keyed by the new id, has ``resumes`` set to the id given and holds the original
launch's role text and skills, which the forked session keeps; the original's
record is never touched. A resume with no record of the original, or of
another role or ticket, is refused; a resume refuses all a fresh launch does.

Every refusal in this suite also checks that no record was left
(``assert_refused``): no record names a session that never ran.
"""

from __future__ import annotations

import calendar
import json
import os
import shutil
import time
import uuid
from pathlib import Path

import pytest

import w2_60a_support as s

KEYS = ("record", "format", "session_id", "resumes", "started_at", "root", "role", "ticket", "ticket_class",
        "model", "model_source", "effort", "effort_source", "subagent_model", "compaction_threshold", "role_text",
        "appended_sha256", "skills", "kept_out", "cli")


def test_every_launch_writes_one_record_before_the_session_starts(launch):
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    sid = result.session_id()
    assert list(result.new_records) == [f"{sid}.json"], (
        f"the launch did not leave exactly one record, named by its --session-id {sid}: {sorted(result.new_records)}")
    at_start = result.record_at_start()
    assert at_start is not None, "the record was not in its folder when the session started"
    assert json.loads(at_start) == result.record(), "the record the session started with is not the record kept"
    assert result.record().get("session_id") == sid, "the record names another session than its own"


def test_the_record_holds_what_the_launch_was(project, launch):
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    record = result.record()
    missing = [key for key in KEYS if key not in record]
    assert not missing, f"the record lacks {missing}: {sorted(record)}"
    model, effort = s.DEFAULTS[s.ENGINEER]
    expected = {
        "record": "gov-launch", "format": 1, "session_id": result.session_id(), "resumes": None,
        "root": os.path.realpath(project), "role": s.ENGINEER, "ticket": s.T.tk, "ticket_class": "implementation",
        "model": model, "effort": effort, "subagent_model": model, "compaction_threshold": "none",
        "kept_out": s.KEPT_OUT,
    }
    wrong = {key: (record.get(key), value) for key, value in expected.items() if record.get(key) != value}
    assert not wrong, f"the record's values (recorded, expected): {wrong}"
    started = record.get("started_at")
    assert isinstance(started, str) and s.STARTED_AT.fullmatch(started), f"started_at {started!r} is not UTC Z"
    moment = calendar.timegm(time.strptime(started, "%Y-%m-%dT%H:%M:%SZ"))
    assert result.started - 2 <= moment <= result.ended + 2, (
        f"started_at {started} is not the time of the launch")
    assert record["role_text"].get("version") == s.VERSIONS[s.ENGINEER] and s.SHA256.fullmatch(
        str(record["role_text"].get("sha256"))), f"role_text: {record['role_text']}"
    for entry in record["skills"]:
        assert {"version", "sha256"} <= set(entry), f"a skill entry without its version and hash: {entry}"


@pytest.mark.parametrize("ticket, cls", ((s.NO_CLASS, None), (s.SPEC, "specification")), ids=("none", "spec"))
def test_the_record_names_the_ticket_s_class_as_written_or_null(launch, ticket, cls):
    result = launch(ticket.role, ticket)
    s.assert_launched(result)
    assert result.record().get("ticket_class", "absent") == cls, (
        f"ticket_class {result.record().get('ticket_class', 'absent')!r}, not {cls!r}")


def test_two_launches_give_two_sessions_and_two_records(launch):
    first, second = launch(s.ENGINEER), launch(s.ENGINEER)
    s.assert_launched(first)
    s.assert_launched(second)
    assert first.session_id() != second.session_id(), "two launches were given one session id"
    assert set(second.after) == {f"{first.session_id()}.json", f"{second.session_id()}.json"}, (
        f"the folder does not hold the two launches' records: {sorted(second.after)}")
    assert first.record() == json.loads(second.after[f"{first.session_id()}.json"]), (
        "the second launch changed the first launch's record")


def test_the_cli_s_version_is_read_from_the_file_its_link_resolves_to(sandbox, project):
    cli = s.install_stand_in_cli(sandbox, link_version="2.1.292")
    result = s.launch(sandbox, cli, s.ENGINEER, s.T)
    s.assert_launched(result)
    assert len(result.calls) == 1, "the CLI was started more than once (a run to read its version)"
    assert result.record().get("cli") == {"path": "~/.local/bin/claude", "version": "2.1.292"}, (
        f"cli: {result.record().get('cli')!r}")


def test_a_cli_that_is_not_such_a_link_is_recorded_as_not_measured(launch):
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    cli = result.record().get("cli")
    assert "not measured" in json.dumps(cli), f"cli {cli!r} does not say its version is not measured"
    assert "2.1.292" not in json.dumps(cli), "a version was recorded although the CLI is no versions link"


# --------------------------------------------------------------------------
# The folder: shared by every worktree, made at launch
# --------------------------------------------------------------------------

def test_every_worktree_shares_the_main_checkout_s_record_folder(sandbox, project, cli):
    worktree = sandbox.home / "work" / "worktree"
    s.git(project, "worktree", "add", "-q", "-b", "w2/W2-60a-fixture", str(worktree))
    result = s.launch(sandbox, cli, s.ENGINEER, s.T, cwd=worktree)
    s.assert_launched(result)
    assert result.record().get("root") == os.path.realpath(worktree), "the record's root is not the worktree"
    assert not (worktree / s.RECORDS_REL).exists(), "the worktree has a record folder of its own"


@pytest.mark.parametrize("before", ("missing", "there"))
def test_the_record_folder_is_made_before_the_session_starts(sandbox, project, launch, before):
    if before == "there":
        sandbox.records.mkdir(parents=True)
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    assert result.session()["records_at_start"].get(str(sandbox.records)) is not None, (
        "the record folder did not exist when the session started")


def _launches_is_a_file(sandbox):
    s.write(sandbox.records, "not a folder\n")


def _launches_is_a_link(sandbox):
    target = sandbox.elsewhere / "launches-elsewhere"
    target.mkdir()
    sandbox.records.parent.mkdir(parents=True, exist_ok=True)
    os.symlink(target, sandbox.records)


def _runtime_is_a_link(sandbox):
    target = sandbox.elsewhere / "runtime-elsewhere"
    target.mkdir()
    shutil.rmtree(sandbox.project / ".gov-runtime", ignore_errors=True)
    os.symlink(target, sandbox.project / ".gov-runtime")


def _launches_read_only(sandbox):
    if os.geteuid() == 0:
        pytest.skip("a read-only folder does not stop root")
    sandbox.records.mkdir(parents=True)
    sandbox.records.chmod(0o555)


UNWRITABLE = {
    "launches-is-a-file": _launches_is_a_file,
    "launches-is-a-link": _launches_is_a_link,
    "gov-runtime-is-a-link": _runtime_is_a_link,
    "launches-read-only": _launches_read_only,
}


@pytest.mark.parametrize("case", sorted(UNWRITABLE))
def test_a_record_that_cannot_be_written_refuses_the_launch(sandbox, project, launch, case):
    UNWRITABLE[case](sandbox)
    try:
        result = launch(s.ENGINEER)
        s.assert_refused(result, "LAUNCH_REFUSED")
        if case == "launches-is-a-link":
            assert not os.listdir(sandbox.elsewhere / "launches-elsewhere"), "a record was written through the link"
    finally:
        if sandbox.records.is_dir() and not sandbox.records.is_symlink():
            sandbox.records.chmod(0o755)


def test_a_cli_that_cannot_be_started_leaves_no_record(sandbox, project, cli, launch):
    cli.path.chmod(0o644)
    result = launch(s.ENGINEER)
    s.assert_refused(result, "DEC-205")
    assert not result.after, f"a record of a session that never ran is left: {sorted(result.after)}"


def test_a_tree_whose_git_gives_no_common_directory_is_refused(sandbox, cli):
    project = s.make_project(sandbox, commit=False)
    s.write(project / ".git", "gitdir: /w260a/no/such/git/dir\n")
    s.assert_refused(s.launch(sandbox, cli, s.ENGINEER, s.T), "LAUNCH_REFUSED")


def test_a_tree_with_no_git_is_its_own_main_checkout(sandbox, cli):
    project = s.make_project(sandbox, commit=False)
    result = s.launch(sandbox, cli, s.ENGINEER, s.T)
    s.assert_launched(result)
    assert result.record().get("root") == os.path.realpath(project)


def test_a_successful_launch_writes_nothing_new_to_stdout_or_stderr(launch):
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    result.record()
    assert (result.run.stdout, result.run.stderr) == ("", ""), f"the launcher wrote\n{result.describe()}"


# --------------------------------------------------------------------------
# Resume
# --------------------------------------------------------------------------

def _resume_arguments(spelling, sid):
    return {"spaced": ("--resume", sid), "joined": (f"--resume={sid}",), "short": ("-r", sid)}[spelling]


@pytest.mark.parametrize("spelling", ("spaced", "joined", "short"))
def test_a_resumed_launch_forks_under_a_new_id_with_a_record_of_its_own(sandbox, project, launch, spelling):
    first = launch(s.ENGINEER)
    s.assert_launched(first)
    original_id, original = first.session_id(), first.record()
    original_text = (sandbox.records / f"{original_id}.json").read_text(encoding="utf-8")
    s.write_role(project, s.ENGINEER, version=s.version_line("1.4.3"), word="zq60a-role-text-after-the-first")
    passed = ("-p", "Go on.", *_resume_arguments(spelling, original_id))
    resumed = launch(s.ENGINEER, None, *passed)
    s.assert_launched(resumed)
    new_id = resumed.session_id()
    assert new_id != original_id, "the resumed launch was not given an id of its own"
    assert s.occurrences(resumed.args, "--fork-session") == 1, f"the line does not fork once: {resumed.args}"
    s.assert_passed_through(resumed, passed, "the resume arguments did not reach the CLI unchanged")
    record = resumed.record()
    assert record.get("resumes") == original_id, f"resumes is {record.get('resumes')!r}, not {original_id}"
    assert record.get("role_text") == original.get("role_text"), (
        "the resumed session's record does not hold the role text the session has: the original launch's")
    assert record.get("skills") == original.get("skills"), "the resumed record's skills are not the original's"
    assert (sandbox.records / f"{original_id}.json").read_text(encoding="utf-8") == original_text, (
        "the original session's record was changed by the resume")


def test_a_resume_with_no_record_of_the_original_is_refused(launch):
    s.assert_refused(launch(s.ENGINEER, None, "-p", "Go on.", "--resume", str(uuid.uuid4())), "LAUNCH_REFUSED",
                     "resume")


@pytest.mark.parametrize("first_role, first_ticket, role, ticket", (
    (s.AUDITOR, s.T, s.TEST_DESIGNER, s.T),
    (s.ENGINEER, s.T, s.ENGINEER, s.NO_CLASS),
), ids=("another-role", "another-ticket"))
def test_a_resume_of_another_role_s_or_ticket_s_session_is_refused(launch, first_role, first_ticket, role, ticket):
    first = launch(first_role, first_ticket)
    s.assert_launched(first)
    s.assert_refused(launch(role, ticket, "-p", "Go on.", "--resume", first.session_id()), "LAUNCH_REFUSED",
                     "resume")


def test_a_resume_refuses_what_a_fresh_launch_refuses(project, launch):
    first = launch(s.ENGINEER)
    s.assert_launched(first)
    s.write_role(project, s.ENGINEER, default="")
    s.assert_refused(launch(s.ENGINEER, None, "-p", "Go on.", "--resume", first.session_id()), "Launch default")
