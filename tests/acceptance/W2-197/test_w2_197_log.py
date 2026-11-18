"""W2-197 S8, S9, F2: the memory-use log, its reader, and a log that cannot be written (README, "The log").

``gov retrieve`` and ``gov brief`` run in this process against the planted store; ``GOV_MEMORY_LOG`` names a file in
the case's folder (conftest), except where a case tests the default place.
"""

from __future__ import annotations

import json
import os
import re

import pytest

import w2_197_support as s

QUESTION = "how is the widget built from its parts list"


def _retrieve(capsys, *argv):
    return s.gov(capsys, "retrieve", *argv)


def _one(log, run) -> dict:
    lines = s.log_lines(log)
    assert len(lines) == 1, f"the log holds {len(lines)} lines after one call, not 1: {lines}\n{run.describe(600)}"
    wrong = s.check_types(lines[0])
    assert not wrong, f"the log line's fields are wrong: {wrong}\n{lines[0]}"
    return lines[0]


# --- S8: one line per call -------------------------------------------------------------------------------------------

def test_s8_retrieve_appends_one_line_with_every_field(store, log, capsys):
    run = _retrieve(capsys, "--root", store.folder, "--json", "--role", "research", "--ticket", s.TICKET_ID,
                    "--session", "sess-1", QUESTION)
    assert run.code == 0, run.describe()
    record = _one(log, run)
    result = run.result
    assert record["command"] == "retrieve" and record["role"] == "research" and record["ticket"] == s.TICKET_ID
    assert record["session"] == "sess-1" and record["search_number"] == 1, record
    assert record["query_sha256"] == s.query_hash(QUESTION), record["query_sha256"]
    assert QUESTION not in log.read_text(encoding="utf-8"), "the query itself is in the log"
    assert record["stop_reason"] == result["stopping_reason"], record
    assert record["items"] == len(result["evidence"]) and record["items"] > 0, record
    assert record["characters"] == sum(len(item["text"]) for item in result["evidence"]), record
    assert record["refusal"] is None and record["reranked"] is result["merge"]["reranked"], record
    assert s.names_commit(record["store_commit"], store.commit), record["store_commit"]


def test_s8_role_ticket_and_session_come_from_the_environment(store, log, capsys, monkeypatch):
    monkeypatch.setenv("GOV_ROLE", "research")
    monkeypatch.setenv("GOV_TICKET", s.TICKET_ID)
    monkeypatch.setenv("GOV_SESSION", "sess-env")
    run = _retrieve(capsys, "--root", store.folder, "--json", QUESTION)
    assert run.code == 0, run.describe()
    record = _one(log, run)
    assert (record["role"], record["ticket"], record["session"]) == ("research", s.TICKET_ID, "sess-env"), record


def test_s8_search_number_counts_the_session_and_is_null_without_one(store, log, capsys):
    for _ in range(2):
        assert _retrieve(capsys, "--root", store.folder, "--json", "--session", "sess-2", QUESTION).code == 0
    assert _retrieve(capsys, "--root", store.folder, "--json", "--session", "sess-3", QUESTION).code == 0
    assert _retrieve(capsys, "--root", store.folder, "--json", QUESTION).code == 0
    lines = s.log_lines(log)
    assert [(line.get("session"), line.get("search_number")) for line in lines] == \
        [("sess-2", 1), ("sess-2", 2), ("sess-3", 1), (None, None)], lines


@pytest.mark.parametrize("code", ["STORE_MISSING", "CONTINUATION_INVALID", "UNRESOLVED_IDS"])
def test_s8_a_refused_call_is_logged_with_its_code(code, store, log, tmp_path, capsys):
    if code == "STORE_MISSING":
        run = _retrieve(capsys, "--root", tmp_path / "no-store", "--json", QUESTION)
    elif code == "CONTINUATION_INVALID":
        run = _retrieve(capsys, "--root", store.folder, "--json", "--continue", "not-a-token", QUESTION)
    else:
        run = _retrieve(capsys, "--root", store.folder, "--json", "DEC-9999")
    seen = run.envelope().get("error", {}).get("code") or run.result.get("stopping_reason")
    assert seen == code, f"the call did not come back {code}: {run.describe(600)}"
    record = _one(log, run)
    assert record["command"] == "retrieve" and record["refusal"] == code, record


def test_s8_brief_appends_one_line_for_its_retrieval(store, repo, log, capsys):
    run = s.brief(capsys, repo, "engineer", "--store", store.folder)
    text = s.ok_brief(run)
    record = _one(log, run)
    assert record["command"] == "brief" and record["role"] == "engineer" and record["ticket"] == s.TICKET_ID, record
    assert record["query_sha256"] == s.query_hash(s.TITLE), record["query_sha256"]
    assert record["items"] == len(s.index_rows(text)) and record["refusal"] is None, record
    assert s.names_commit(record["store_commit"], store.commit), record["store_commit"]


def test_s8_without_the_variable_the_line_lands_in_the_main_worktree(tmp_path, capsys, monkeypatch):
    with pytest.MonkeyPatch.context() as patch:
        from gov.retrieval import lexical

        patch.setattr(lexical, "indexable", lambda root, paths: list(paths))
        own = s.plant_store(tmp_path / "own")
    monkeypatch.delenv("GOV_MEMORY_LOG")
    monkeypatch.chdir(own.folder)
    run = _retrieve(capsys, "--root", own.folder, "--json", QUESTION)
    assert run.code == 0, run.describe()
    main_log = own.repo / ".gov-runtime/memory-use.jsonl"
    assert len(s.log_lines(main_log)) == 1, f"no line in the main worktree's {main_log}"
    assert not (own.folder / ".gov-runtime/memory-use.jsonl").exists(), "the line landed in the linked worktree"


# --- S9: the reader --------------------------------------------------------------------------------------------------

def _record(day: str, command: str, role: str, refusal: str | None = None) -> dict:
    return {"ts": f"{day}T10:00:00+00:00", "command": command, "role": role, "ticket": s.TICKET_ID, "session": None,
            "query_sha256": "0" * 16, "stop_reason": None if refusal else "SATURATED", "items": 0 if refusal else 3,
            "characters": 0 if refusal else 120, "latency_ms": 5, "refusal": refusal, "store_commit": "a" * 40,
            "reranked": False, "search_number": None}


PLANTED = [
    _record("2026-11-15", "retrieve", "engineer"),
    _record("2026-11-15", "retrieve", "engineer"),
    _record("2026-11-15", "retrieve", "engineer", "STORE_MISSING"),
    _record("2026-11-15", "brief", "lead"),
    _record("2026-11-16", "retrieve", "engineer"),
    _record("2026-11-16", "retrieve", "research"),
    _record("2026-11-16", "brief", "lead"),
    _record("2026-11-16", "brief", "lead"),
]
# (day, role) -> (successful retrieves, refused retrieves, briefs)
EXPECTED = {("2026-11-15", "engineer"): (2, 1, 0), ("2026-11-15", "lead"): (0, 0, 1),
            ("2026-11-16", "engineer"): (1, 0, 0), ("2026-11-16", "research"): (1, 0, 0),
            ("2026-11-16", "lead"): (0, 0, 2)}


@pytest.fixture
def planted_log(tmp_path, monkeypatch):
    path = tmp_path / "planted.jsonl"
    lines = [json.dumps(record) for record in PLANTED]
    lines.insert(5, '{"ts": "2026-11-16T10:00:00+00:00", "command": "retr')  # a line cut short
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    monkeypatch.setenv("GOV_MEMORY_LOG", str(path))
    return path


def _count(value, *names):
    for name in names:
        if isinstance(value, dict) and name in value:
            return value[name]
    raise AssertionError(f"no count {names[0]!r} in {value!r}")


def test_s9_read_returns_the_records_and_skips_the_malformed_line(planted_log):
    from gov import memory_use

    records = memory_use.read(path=planted_log)
    assert [dict(record) for record in records] == PLANTED, f"read gave {records!r}"
    if hasattr(records, "skipped"):
        assert records.skipped == 1, f"read counts {records.skipped} skipped lines, not 1"


def test_s9_read_by_root_finds_the_default_log(tmp_path, monkeypatch):
    from gov import memory_use

    monkeypatch.delenv("GOV_MEMORY_LOG")
    root = tmp_path / "plain"
    (root / ".gov-runtime").mkdir(parents=True)
    (root / ".gov-runtime/memory-use.jsonl").write_text(json.dumps(PLANTED[0]) + "\n", encoding="utf-8")
    assert [dict(record) for record in memory_use.read(root=root)] == [PLANTED[0]]


def test_s9_per_role_day_counts_retrieves_briefs_and_refusals(planted_log):
    from gov import memory_use

    counts = memory_use.per_role_day(memory_use.read(path=planted_log))
    got = {(str(day), role): value for (day, role), value in dict(counts).items()}
    assert sorted(got) == sorted(EXPECTED), f"per_role_day's keys are {sorted(got)}"
    for key, (ok, refused, briefs) in EXPECTED.items():
        value = got[key]
        assert _count(value, "brief", "briefs") == briefs, f"{key}: {value}"
        assert _count(value, "refused") == refused, f"{key}: {value}"
        assert _count(value, "retrieve", "retrieves") in (ok, ok + refused), f"{key}: {value}"


LINE = re.compile(r"^(\d{4}-\d{2}-\d{2}) (\S+) retrieves (\d+) briefs (\d+) refused (\d+)$")


def _lines(run) -> set[tuple]:
    assert run.code == 0, run.describe()
    return {(m[1], m[2], int(m[3]), int(m[4]), int(m[5])) for m in map(LINE.match, run.out.splitlines()) if m}


def _expected(since: str = "") -> set[tuple]:
    from gov import memory_use

    counts = {(str(day), role): value for (day, role), value in dict(memory_use.per_role_day(PLANTED)).items()}
    return {(day, role, _count(counts[(day, role)], "retrieve", "retrieves"), briefs, refused)
            for (day, role), (_ok, refused, briefs) in EXPECTED.items() if day >= since}


def test_s9_command_prints_one_line_per_day_and_role(planted_log, capsys):
    run = s.gov(capsys, "memory-use")
    assert _lines(run) == _expected(), f"gov memory-use printed:\n{run.out}"


def test_s9_command_since_keeps_the_later_days(planted_log, capsys):
    run = s.gov(capsys, "memory-use", "--since", "2026-11-16")
    assert _lines(run) == _expected("2026-11-16"), f"gov memory-use --since 2026-11-16 printed:\n{run.out}"


def test_s9_command_json_is_an_envelope(planted_log, capsys):
    run = s.gov(capsys, "memory-use", "--json")
    assert run.code == 0 and run.envelope().get("ok") is True, run.describe()


# --- F2: a log that cannot be written changes nothing ----------------------------------------------------------------

def _unwritable(kind: str, tmp_path):
    if kind == "folder":
        path = tmp_path / "log-is-a-folder"
        path.mkdir()
    else:
        if os.geteuid() == 0:
            pytest.skip("root writes a read-only file")
        path = tmp_path / "read-only.jsonl"
        path.write_text("", encoding="utf-8")
        path.chmod(0o444)
    return path


@pytest.mark.parametrize("kind", ["folder", "read-only"])
def test_f2_retrieve_output_is_the_same_with_an_unwritable_log(kind, store, log, tmp_path, capsys, monkeypatch):
    first = _retrieve(capsys, "--root", store.folder, "--json", QUESTION)
    assert s.log_lines(log), "the writable log got no line: S8's writer is not there"
    monkeypatch.setenv("GOV_MEMORY_LOG", str(_unwritable(kind, tmp_path)))
    second = _retrieve(capsys, "--root", store.folder, "--json", QUESTION)
    assert (second.code, second.out) == (first.code, first.out), \
        f"an unwritable log changed gov retrieve:\n{first.describe(400)}\n---\n{second.describe(400)}"


@pytest.mark.parametrize("kind", ["folder", "read-only"])
def test_f2_brief_output_is_the_same_with_an_unwritable_log(kind, store, repo, log, tmp_path, capsys, monkeypatch):
    first = s.brief(capsys, repo, "engineer", "--store", store.folder)
    assert first.code == 0 and s.log_lines(log), f"the writable log got no line:\n{first.describe(400)}"
    monkeypatch.setenv("GOV_MEMORY_LOG", str(_unwritable(kind, tmp_path)))
    second = s.brief(capsys, repo, "engineer", "--store", store.folder)
    assert (second.code, second.out) == (first.code, first.out), "an unwritable log changed gov brief"


def test_f2_append_never_raises(tmp_path, monkeypatch):
    from gov import memory_use

    folder = _unwritable("folder", tmp_path)
    monkeypatch.setenv("GOV_MEMORY_LOG", str(folder))
    memory_use.append(_record("2026-11-17", "retrieve", "engineer"), tmp_path)
    assert folder.is_dir() and not any(folder.iterdir()), "append changed the folder in the log's place"
