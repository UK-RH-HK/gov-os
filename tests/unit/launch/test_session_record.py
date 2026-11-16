"""W2-60b: the session record (``gov.launch.session_record``): one JSON file per launched session, written whole,
read back by ticket and session id, each measured value with its source or "not measured" with the reason, never 0
for not measured and never text of the log (S1-S6, S11, F2); and the one-writer reading of the records (S10, S12)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tests" / "unit" / "telemetry"))

from gov.cli.errors import GovError  # noqa: E402
from gov.launch import session_record as sr  # noqa: E402
from test_sessionlog_w2_60b import SECRET, Log, _sub  # noqa: E402

SID = "11111111-1111-4111-8111-111111111111"
MEASURED = ("role", "ticket", "task_class", "model", "effort", "window", "tokens_input", "tokens_output",
            "tokens_cache_creation", "tokens_cache_read", "cost_usd", "minutes", "turns", "subagents",
            "rate_limit_events", "compactions", "claude_code_version", "tier", "criticality", "promotion")
HOUSEKEEPING = ("record", "format", "session_id", "worktree", "pid", "started_at", "ended_at", "exit_code")


def _launch_record(promotion=None, criticality="C3", ticket_class="implementation"):
    return {"record": "gov-launch", "session_id": SID, "role": "engineer", "ticket": "DAEO-ecac",
            "ticket_class": ticket_class, "criticality": criticality, "promotion": promotion,
            "model": "claude-opus-5-5"}


def _begun(tmp_path, **kw):
    path = tmp_path / "launches" / f"{SID}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_launch_record(**kw)), encoding="utf-8")
    return sr.begin(path, worktree=str(tmp_path), pid=os.getpid())


def _finished(tmp_path, log=None, result=None, subagents=(), **kw):
    config = tmp_path / "config"
    if log is not None:
        log.write(config, subagents=subagents)
    return sr.finish(_begun(tmp_path, **kw), 0, config, result=result)


def _form_ok(entry):
    if "source" in entry:
        return set(entry) == {"value", "source"} and isinstance(entry["source"], str) and entry["source"]
    return set(entry) == {"value", "not_measured"} and entry["value"] is None and entry["not_measured"]


def test_the_start_record_holds_the_housekeeping_keys_and_the_launch_record_s_keys(tmp_path):
    record = _begun(tmp_path)
    assert record["record"] == "gov-session" and record["format"] == 1 and record["session_id"] == SID
    assert record["ended_at"] is None and record["exit_code"] is None and record["pid"] == os.getpid()
    assert record["worktree"] == str(tmp_path)
    for key, value in (("role", "engineer"), ("ticket", "DAEO-ecac"), ("task_class", "implementation"),
                       ("criticality", "C3"), ("promotion", None)):
        assert record[key]["value"] == value and "launch record" in record[key]["source"], key


def test_the_finished_record_holds_every_key_each_named_by_source_or_not_measured(tmp_path):
    log = Log().user().assistant().compaction().assistant().api_error(429).cost(2.5)
    record = _finished(tmp_path, log, subagents=(_sub("claude-haiku-5-5"),))
    assert set(HOUSEKEEPING) | set(MEASURED) <= set(record)
    for key in MEASURED:
        assert _form_ok(record[key]), (key, record[key])
    assert record["ended_at"] is not None and record["exit_code"] == 0
    assert record["model"]["value"] == "claude-opus-5-5" and record["tier"]["value"] == "opus"
    assert record["effort"]["value"] == "high" and record["compactions"]["value"] == 1
    assert record["cost_usd"]["value"] == 2.5 and record["turns"]["value"] == 2
    assert record["subagents"]["value"] == {"count": 1, "models": ["claude-haiku-5-5"]}
    assert record["rate_limit_events"]["value"] == [{"at": log.lines[4]["timestamp"]}]
    assert record["claude_code_version"]["value"] == "2.1.320"
    assert record["tokens_input"]["value"] == 30  # two main messages and one sub-agent message of 10


def test_no_log_text_reaches_the_record_the_version_excepted(tmp_path):
    log = Log().user().assistant().api_error(429).rate_limit_message().compaction()
    text = json.dumps(_finished(tmp_path, log))
    assert SECRET not in text and "2.1.320" in text


def test_a_log_with_no_cost_says_not_measured_never_zero(tmp_path):
    record = _finished(tmp_path, Log().user().assistant())
    assert record["cost_usd"]["value"] is None and record["cost_usd"]["not_measured"]


def test_with_no_session_log_every_log_value_is_not_measured_with_its_reason(tmp_path):
    record = _finished(tmp_path)
    for key in MEASURED:
        if key not in ("role", "ticket", "task_class", "criticality", "promotion"):
            assert record[key]["value"] is None and record[key]["not_measured"], key


def test_the_window_is_not_measured_from_the_log_alone(tmp_path):
    record = _finished(tmp_path, Log().user().assistant())
    assert record["window"]["value"] is None and "window" in record["window"]["not_measured"]


def test_the_result_line_gives_the_window_cost_turns_and_minutes_with_its_source(tmp_path):
    result = {"type": "result", "num_turns": 7, "total_cost_usd": 3.5, "duration_ms": 120000,
              "modelUsage": {"claude-opus-5-5": {"contextWindow": 1000000, "costUSD": 3.5}}}
    record = _finished(tmp_path, Log().user().assistant(), result=result)
    assert record["window"]["value"] == 1000000 and "result line" in record["window"]["source"]
    assert record["turns"]["value"] == 7 and record["cost_usd"]["value"] == 3.5 and record["minutes"]["value"] == 2.0


def test_a_promotion_s_reason_and_the_criticality_come_from_the_launch_record(tmp_path):
    record = _finished(tmp_path, Log().user().assistant(),
                       promotion={"reason": "a fail-open finding", "record": "docs/probes/x.md"})
    assert record["promotion"]["value"] == "a fail-open finding" and record["criticality"]["value"] == "C3"
    assert record["tier"]["value"] == "opus"


def test_without_a_promotion_or_criticality_the_keys_are_present_and_null(tmp_path):
    record = _finished(tmp_path, criticality=None)
    for key in ("tier", "criticality", "promotion"):
        assert key in record and record[key]["value"] is None, key


@pytest.mark.parametrize("model, tier", (("claude-opus-5-5", "opus"), ("claude-sonnet-5-5", "sonnet"),
                                         ("claude-haiku-5-5", "haiku"), ("claude-fable-5-2", "other")))
def test_the_tier_is_derived_from_the_model_s_name(tmp_path, model, tier):
    assert _finished(tmp_path, Log().user().assistant(model=model))["tier"]["value"] == tier


def test_a_record_is_written_and_read_back_by_ticket_and_session_id(tmp_path):
    record = _finished(tmp_path, Log().user().assistant())
    path = sr.write(tmp_path, record)
    assert path == tmp_path / ".gov-runtime" / "sessions" / f"{SID}.json"
    assert sr.read_record(tmp_path, "DAEO-ecac", SID) == record
    assert [p.name for p in path.parent.iterdir()] == [f"{SID}.json"]


def test_a_record_of_another_ticket_is_not_read_back(tmp_path):
    sr.write(tmp_path, _begun(tmp_path))
    with pytest.raises(GovError):
        sr.read_record(tmp_path, "DAEO-zzzz", SID)


def test_a_missing_record_is_refused(tmp_path):
    with pytest.raises(GovError):
        sr.read_record(tmp_path, "DAEO-ecac", SID)


def test_a_record_in_a_linked_worktree_is_written_in_the_main_checkout(tmp_path):
    main = tmp_path / "main"
    subprocess.run(["git", "init", "-q", str(main)], check=True)
    subprocess.run(["git", "-C", str(main), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                    "--allow-empty", "-m", "x"], check=True)
    subprocess.run(["git", "-C", str(main), "worktree", "add", "-q", "-b", "w", str(tmp_path / "wt")], check=True)
    path = sr.write(Path(os.path.realpath(tmp_path / "wt")), _begun(tmp_path))
    assert path.parent == Path(os.path.realpath(main)) / ".gov-runtime" / "sessions"


def test_an_unwritable_folder_raises_and_leaves_nothing(tmp_path):
    (tmp_path / ".gov-runtime").mkdir()
    (tmp_path / ".gov-runtime" / "sessions").write_text("a file, not a folder", encoding="utf-8")
    with pytest.raises((OSError, GovError)):
        sr.write(tmp_path, _begun(tmp_path))
    assert (tmp_path / ".gov-runtime" / "sessions").read_text() == "a file, not a folder"


@pytest.mark.skipif(os.geteuid() == 0, reason="root writes a read-only folder")
def test_a_read_only_folder_raises_and_leaves_no_temporary_file(tmp_path):
    folder = tmp_path / ".gov-runtime" / "sessions"
    folder.mkdir(parents=True)
    folder.chmod(0o500)
    try:
        with pytest.raises(OSError):
            sr.write(tmp_path, _begun(tmp_path))
        assert list(folder.iterdir()) == []
    finally:
        folder.chmod(0o700)


def test_the_end_write_replaces_the_start_record_whole(tmp_path):
    sr.write(tmp_path, _begun(tmp_path))
    finished = _finished(tmp_path, Log().user().assistant())
    sr.write(tmp_path, finished)
    assert sr.read_record(tmp_path, "DAEO-ecac", SID)["ended_at"] == finished["ended_at"]
    assert len(list((tmp_path / ".gov-runtime" / "sessions").iterdir())) == 1


# -- the keeper: one stderr line for the session, never a changed exit code (S5) ------------------------------------

def _keeper(tmp_path, said):
    launches = tmp_path / ".gov-runtime" / "launches"
    launches.mkdir(parents=True, exist_ok=True)
    path = launches / f"{SID}.json"
    path.write_text(json.dumps(_launch_record()), encoding="utf-8")
    return sr.Keeper(tmp_path, path, worktree=str(tmp_path), pid=os.getpid(), say=said.append,
                     config=tmp_path / "config")


def test_the_keeper_writes_at_the_start_and_replaces_at_the_end(tmp_path):
    said = []
    keeper = _keeper(tmp_path, said)
    keeper.begin()
    assert sr.read_record(tmp_path, "DAEO-ecac", SID)["ended_at"] is None
    keeper.end(3)
    record = sr.read_record(tmp_path, "DAEO-ecac", SID)
    assert record["exit_code"] == 3 and record["ended_at"] is not None and said == []


def test_an_unwritable_record_gives_one_stderr_line_naming_it_for_the_whole_session(tmp_path):
    said = []
    keeper = _keeper(tmp_path, said)
    (tmp_path / ".gov-runtime" / "sessions").write_text("x", encoding="utf-8")
    keeper.begin()
    keeper.end(0)
    assert len(said) == 1 and said[0].count("\n") == 1 and f"{SID}.json" in said[0]


def test_an_end_that_fails_after_a_written_start_says_one_line(tmp_path, monkeypatch):
    said = []
    keeper = _keeper(tmp_path, said)
    keeper.begin()
    monkeypatch.setattr(sr, "finish", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    keeper.end(0)
    assert len(said) == 1 and f"{SID}.json" in said[0]


# -- one writer per worktree (S10, S12) --------------------------------------------------------------------------

def _plant(tmp_path, role="engineer", worktree=None, pid=None, ended=None, name=None, started=None):
    folder = tmp_path / ".gov-runtime" / "sessions"
    folder.mkdir(parents=True, exist_ok=True)
    sid = name or f"2222222{len(list(folder.iterdir()))}-2222-4222-8222-222222222222"
    record = {"record": "gov-session", "format": 1, "session_id": sid, "worktree": str(worktree or tmp_path),
              "pid": os.getpid() if pid is None else pid,
              "started_at": started or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "ended_at": ended, "exit_code": None,
              "role": {"value": role, "source": "launch record"}}
    (folder / f"{sid}.json").write_text(json.dumps(record), encoding="utf-8")
    return sid


def test_a_live_writing_session_refuses_a_second_writer_naming_it_and_the_worktree(tmp_path):
    sid = _plant(tmp_path)
    with pytest.raises(GovError) as raised:
        sr.check_one_writer(tmp_path, str(tmp_path), "engineer")
    assert raised.value.code == "LAUNCH_REFUSED"
    assert sid in raised.value.message and str(tmp_path) in raised.value.message


@pytest.mark.parametrize("role", sorted(sr.REVIEWERS))
def test_a_live_reviewer_is_not_counted(tmp_path, role):
    _plant(tmp_path, role=role)
    sr.check_one_writer(tmp_path, str(tmp_path), "engineer")


def test_the_reviewer_set_holds_the_auditor_and_the_qa_engineer():
    assert sr.REVIEWERS == frozenset({"independent-auditor", "qa-engineer"})


@pytest.mark.parametrize("role", sorted(sr.REVIEWERS))
def test_a_reviewer_is_never_refused_by_a_live_writer(tmp_path, role):
    _plant(tmp_path)
    sr.check_one_writer(tmp_path, str(tmp_path), role)


def test_an_ended_session_is_not_live(tmp_path):
    _plant(tmp_path, ended="2026-11-16T10:00:00Z")
    sr.check_one_writer(tmp_path, str(tmp_path), "engineer")


def test_a_dead_pid_is_not_live(tmp_path):
    process = subprocess.Popen(["true"])
    process.wait()
    _plant(tmp_path, pid=process.pid)
    sr.check_one_writer(tmp_path, str(tmp_path), "engineer")


def test_a_reused_pid_is_not_live(tmp_path):
    """The pid names a process that started after the record's session started: another process than the launcher."""
    _plant(tmp_path, started="2020-01-01T00:00:00Z")
    sr.check_one_writer(tmp_path, str(tmp_path), "engineer")


def test_a_session_in_another_worktree_is_not_counted(tmp_path):
    other = tmp_path / "other"
    other.mkdir()
    _plant(tmp_path, worktree=other)
    sr.check_one_writer(tmp_path, str(tmp_path), "engineer")


def test_a_live_session_with_no_role_counts_as_a_writer(tmp_path):
    _plant(tmp_path, role=None)
    with pytest.raises(GovError):
        sr.check_one_writer(tmp_path, str(tmp_path), "engineer")


@pytest.mark.parametrize("text", ("not json", "[]", json.dumps({"record": "gov-session", "pid": "x"})))
def test_a_session_record_that_cannot_be_read_refuses_naming_it(tmp_path, text):
    folder = tmp_path / ".gov-runtime" / "sessions"
    folder.mkdir(parents=True)
    (folder / "broken.json").write_text(text, encoding="utf-8")
    with pytest.raises(GovError) as raised:
        sr.check_one_writer(tmp_path, str(tmp_path), "engineer")
    assert "broken.json" in raised.value.message


def test_no_session_folder_means_no_live_writer(tmp_path):
    sr.check_one_writer(tmp_path, str(tmp_path), "engineer")


def test_a_file_in_the_folder_s_place_holds_no_record_and_refuses_nothing(tmp_path):
    (tmp_path / ".gov-runtime").mkdir()
    (tmp_path / ".gov-runtime" / "sessions").write_text("x", encoding="utf-8")
    sr.check_one_writer(tmp_path, str(tmp_path), "engineer")


@pytest.mark.skipif(os.geteuid() == 0, reason="root lists any folder")
def test_a_folder_that_cannot_be_listed_refuses(tmp_path):
    _plant(tmp_path)
    folder = tmp_path / ".gov-runtime" / "sessions"
    folder.chmod(0o000)
    try:
        with pytest.raises(GovError) as raised:
            sr.check_one_writer(tmp_path, str(tmp_path), "engineer")
        assert "cannot be listed" in raised.value.message
    finally:
        folder.chmod(0o700)


def test_a_hidden_temporary_file_is_not_read_as_a_record(tmp_path):
    folder = tmp_path / ".gov-runtime" / "sessions"
    folder.mkdir(parents=True)
    (folder / f".{SID}.0123456789abcdef.tmp").write_text("partial", encoding="utf-8")
    sr.check_one_writer(tmp_path, str(tmp_path), "engineer")
