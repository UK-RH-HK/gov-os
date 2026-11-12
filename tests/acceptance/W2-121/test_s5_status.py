"""S5: a status file every pass; a pass that fails says so at the top, never a stale file that looks current.

Readings fixed by the brief: ``status.json`` and ``status.txt`` are written whole (temp file + rename) every pass; they
hold the pass's time and outcome, the running sessions (counted from the processes that carry the lead's identity
marker, never from ``started.txt`` or the logs), load, memory, the gate, the slots held, each kind's peak, the peaks
ahead, the queue (``land.txt``'s pending lines; part a only shows them) and the inbox (the unread items). The key names
are the engineer's: the tests find a section by a part of its key (``running``, ``load``, ``mem``, ``gate``, ``slot``,
``ahead``, ``queue``, ``inbox``) and read its figures, not the names. Times are ISO-8601 strings. A failing pass writes
``PASS FAILED <time>: <reason>`` as the first line of ``status.txt`` and ``"ok": false`` with the reason in
``status.json``.
"""

from __future__ import annotations

import json
import os

import w2_121_support as support
from w2_121_support import GIB, MEM_FORMS, explain, has_figure, numbers


def section(status: dict, *parts: str):
    for part in parts:
        found = support.values_under(status, part)
        if found:
            return found
    return []


def test_s5_the_status_holds_the_running_sessions_counted_from_the_processes(project):
    p = project
    p.plant_lead("DAEO-r001")
    p.plant_lead("DAEO-r002")
    p.plant_process(["tail", "-f", "DAEO-r003.log"])  # a mention is no session
    p.plant_lead("DAEO-r004", role="engineer")  # nor is a worker
    r = p.tick()
    assert r.code == 0, r
    status = p.status_json()
    found = section(status, "running", "leads", "sessions")
    assert found, "no running-sessions section in status.json" + explain(p, r)
    counted = [len(v) if isinstance(v, (list, dict)) else v for v in found]
    assert 2 in counted, f"running sessions counted as {counted}, planted 2 leads"
    text = json.dumps(status)
    assert "DAEO-r001" in text and "DAEO-r002" in text, "the running sessions' tickets are not named"
    assert "DAEO-r003" not in text and "DAEO-r004" not in text


def test_s5_the_status_holds_load_memory_gate_slots_peaks_ahead_queue_and_inbox(project):
    p = project
    entry = p.add_ticket(901)
    p.set_machine(mem_gib=12, load=(3.5, 2.0, 1.0))
    p.land("W2-950=0123456789ab\nW2-951=ba9876543210\n")
    land_before = ((p.state / "land.txt").read_text(), (p.state / "land.txt").stat().st_mtime_ns)
    p.plant_item("0001.txt", "W2-960-A5-x.json", "W2-960")
    p.plant_item("0002.txt", "W2-962-A5-x.json", "W2-962")
    p.plant_item("0003.txt", "W2-961-A5-x.json", "W2-961", read=True)
    p.ready(entry)
    r = p.tick()
    assert r.code == 0, r
    status, text = p.status_json(), p.status_text()
    assert status.get("ok") is True, status
    assert support.near_now(support.iso_leaves(status)), "no time of this pass in status.json"
    assert not text.startswith("PASS FAILED"), text
    where = lambda *parts: section(status, *parts)  # noqa: E731
    assert any(has_figure(v, 3.5) for v in where("load")), "the load 3.5 is not in the status" + explain(p, r)
    assert any(has_figure(v, 12 * GIB, MEM_FORMS) for v in where("mem")), "MemAvailable 12 GiB is not in the status" + explain(p, r)
    gate = where("gate")
    assert gate, "no gate in status.json"
    assert any(k == "open" and v is True for k, v in support.walk(gate)) or "open" in json.dumps(gate).lower(), gate
    assert where("slot"), "no slots held in status.json"
    assert where("ahead"), "no peaks ahead in status.json"
    queue = json.dumps(where("queue"))
    assert "W2-950" in queue and "W2-951" in queue and "0123456789ab" in queue, f"the queue: {queue}"
    inbox = json.dumps(where("inbox"))
    assert "W2-960" in inbox and "W2-962" in inbox and "W2-961" not in inbox, f"the inbox section: {inbox}"
    assert entry.log in json.dumps(status), "the entry this pass started is not in the status"
    for word in ("W2-950", "W2-960"):
        assert word in text, f"status.txt does not show {word}" + explain(p, r)
    assert ((p.state / "land.txt").read_text(), (p.state / "land.txt").stat().st_mtime_ns) == land_before, \
        "part a changed land.txt (landing is part b)"


def test_s5_session_counts_do_not_come_from_started_txt_or_the_logs(project):
    p = project
    first, second = p.add_ticket(901), p.add_ticket(902)
    p.set_sleep(10)
    p.ready(first, second)
    assert p.tick().code == 0
    p.wait_launches(1)  # started.txt and logs/ now hold a start that no planted process carries
    assert p.tick().code == 0
    status = p.status_json()
    found = section(status, "running", "leads", "sessions")
    counted = [len(v) if isinstance(v, (list, dict)) else v for v in found]
    assert counted and all(c == 0 for c in counted if isinstance(c, (int, float))), \
        f"sessions counted from started.txt or the logs: {counted}"


def test_s5_the_status_files_are_replaced_by_rename_every_pass(project):
    p = project
    assert p.tick().code == 0
    inodes = {n: os.stat(p.state / n).st_ino for n in ("status.json", "status.txt")}
    assert p.tick().code == 0
    again = {n: os.stat(p.state / n).st_ino for n in ("status.json", "status.txt")}
    assert all(again[n] != inodes[n] for n in inodes), f"a status file was written in place: {inodes} {again}"
    json.loads((p.state / "status.json").read_text(encoding="utf-8"))
    leftovers = [f.name for f in p.state.iterdir() if f.name.endswith((".tmp", ".part")) or f.name.startswith("status.json.")]
    assert leftovers == [], f"temporary files left in the state folder: {leftovers}"


def test_s5_a_failing_pass_says_so_at_the_top_and_leaves_no_stale_status(project):
    p = project
    entry = p.add_ticket(901)
    assert p.tick().code == 0  # a good pass first: a status that says it succeeded
    assert json.loads((p.state / "status.json").read_text(encoding="utf-8")).get("ok") is True
    good_text = p.status_text()
    (p.state / "started.txt").mkdir()  # the record of what was started cannot be read: no pass can pass over that
    p.ready(entry)
    r = p.tick()
    assert r.code != 0, r
    p.settle()
    assert p.launches() == [], "a pass that could not read started.txt started a session"
    text = p.status_text()
    first = text.splitlines()[0] if text else ""
    assert first.startswith("PASS FAILED"), f"first line of status.txt: {first!r}\n{r}"
    assert text != good_text
    status = p.status_json()
    assert status.get("ok") is False, status
    reasons = [v for v in support.values_under(status, "reason") + support.values_under(status, "error")
               if isinstance(v, str) and v.strip()]
    assert reasons, f"status.json names no reason: {status}"
    assert support.near_now(support.iso_leaves(first)), f"the first line carries no time of the failed pass: {first!r}"
