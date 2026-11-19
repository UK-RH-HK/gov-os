"""W2-205: what the launcher records for a death to resume (``session_id``, ``launcher_pid``) and the end event of its
end message (RT-2, RT-5)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.launch import launcher  # noqa: E402

ID = "11111111-2222-3333-4444-555555555555"


def test_a_workers_session_id_is_the_one_its_plan_gave():
    assert launcher._session_key({"session_id": ID}, ["-p"]) == {"session_id": ID}
    assert launcher._session_key({}, ["-p"]) == {}


def test_a_leads_session_id_is_the_one_it_is_given_or_resumes():
    assert launcher._session_key(None, ["--session-id", ID, "-p"]) == {"session_id": ID}
    assert launcher._session_key(None, [f"--session-id={ID}"]) == {"session_id": ID}
    assert launcher._session_key(None, ["--resume", ID]) == {"session_id": ID}


def test_a_lead_with_no_id_or_a_bare_resume_records_none():
    assert launcher._session_key(None, ["-p", "go"]) == {}
    assert launcher._session_key(None, ["--resume", "write the report"]) == {}
    assert launcher._session_key(None, ["--resume"]) == {}


def test_the_end_message_writes_one_end_event_of_the_right_kind_with_its_message_id(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    from gov.dispatch import inbox, runtime
    for pid, (role, kind) in enumerate((("engineer", "worker"), ("orchestrator", "lead")), start=5):
        entry = {"pid": pid, "role": role, "ticket": f"T-{role}", "started": "s", "notify": "cto",
                 "address": f"{role}:T-{role}", "boot": "b", "start_ticks": 9}
        launcher._end_message(entry, 0)
        launcher._end_message(entry, 0)
        events = [json.loads(line) for line in (tmp_path / ".gov-os" / "runtime" / "log.jsonl").read_text().splitlines()]
        found = [e for e in events if e["id"] == runtime.end_id(entry)]
        assert len(found) == 1 and found[0]["event"] == "end" and found[0]["kind"] == kind and found[0]["to"] == "cto"
        assert found[0]["ticket"] == f"T-{role}" and found[0]["ended_at"].endswith("Z")
    assert len(inbox.read("cto", peek=True)["messages"]) == 2
