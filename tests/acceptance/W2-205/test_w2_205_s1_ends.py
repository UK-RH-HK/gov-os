"""W2-205, success line 1 (RT-2): every end reaches the watching session within 2 minutes.

A lead, a worker or a heavy job that ends gives one wake message to its launcher's address and one ``end`` event in the
runtime log (``ended_at``, ``id``, ``to``, ``kind``); ``gov dispatch waits --ends`` prints each end's gap (the
message's time less ``ended_at``; to now, saying ``unsent``, while there is no message) as ``<id> <kind> <to> gap <n>
s``, with a ``finding:`` line and exit 3 for a gap over 120 s.

The passes read the planted clock ``GOV_RUNTIME_NOW``. Where a pass sends a message itself, its clock is planted at
the real time (a minute ago, then now), so the gap is about 60 s whichever clock stamps the message.
"""

from __future__ import annotations

import re
import time

import w2_205_support as s

LEAD, CTO, TICKET = "lead:DAEO-e205", "cto", "DAEO-e205"
ROW = re.compile(r"^(\S+)\s+(lead|worker|job)\s+(\S+)\s+gap\s+(-?\d+(?:\.\d+)?)\s+s\b(.*)$")
T = 1_795_000_000  # the planted reports' time zero (2026-11-18, whole seconds)


def _report(box, now, *more):
    return box.gov("dispatch", "waits", "--ends", *more, extra_env=s.clock(now))


def _rows(done) -> dict:
    """The report's end lines by id: ``(kind, to, gap, the rest of the line)``."""
    found = {}
    for line in done.stdout.splitlines():
        match = ROW.match(line.strip())
        if match:
            found[match.group(1)] = (match.group(2), match.group(3), float(match.group(4)), match.group(5))
    return found


def _findings(done) -> list[str]:
    return [line for line in done.stdout.splitlines() if line.strip().startswith("finding:")]


def _one_end(box, message_id) -> dict:
    ends = [e for e in box.events("end") if e.get("id") == message_id]
    assert len(ends) == 1, f"{len(ends)} `end` events with the id {message_id} in the runtime log, not one: {box.log()}"
    return ends[0]


def test_s1_a_lead_a_worker_and_a_job_each_give_one_end_event_and_a_gap_within_120_s(box):
    start = int(time.time()) - 60
    lead, worker = box.sleeper(), box.sleeper()
    e_lead = box.register(lead.pid, s.start_ticks(lead.pid), ticket=TICKET, role="orchestrator", notify=CTO,
                          address=f"orchestrator:{TICKET}")
    e_worker = box.register(worker.pid, s.start_ticks(worker.pid), ticket=TICKET, role="engineer", notify=LEAD,
                            address=f"engineer:{TICKET}")
    box.run_pass(extra_env=s.clock(start))
    box.end(lead)
    box.end(worker)
    job = box.gov("resources", "--slot", "test", "--", "true", extra_env={"GOV_MSG_ADDRESS": LEAD})
    assert job.returncode == 0, f"harness: the heavy job did not run\n{s.said(job)}"
    ready = box.events("ready")
    assert len(ready) == 1, f"harness: the job's `ready` event: {ready}"
    job_id = f"job:{ready[0]['job']}"
    box.run_pass(extra_env=s.clock(start + 60))
    box.run_pass(extra_env=s.clock(start + 120))  # a later pass writes no second `end` event

    wanted = {s.end_id(e_lead): ("lead", CTO), s.end_id(e_worker): ("worker", LEAD), job_id: ("job", LEAD)}
    for message_id, (kind, to) in wanted.items():
        event = _one_end(box, message_id)
        assert (event.get("kind"), event.get("to")) == (kind, to), f"the `end` event of the {kind}: {event}"
        sent = [m for m in box.wakes(to) if m.get("id") == message_id]
        assert len(sent) == 1, f"{len(sent)} wake messages {message_id} in {to}'s inbox, not one"
        if kind == "job":
            assert event.get("job") == ready[0]["job"], f"the job's `end` event does not name its job: {event}"
            assert abs(s.epoch(event["ended_at"].replace("Z", "+00:00")) - time.time()) < 30, event
        else:
            assert event.get("ticket") == TICKET, f"the `end` event does not name the ticket: {event}"
            assert s.epoch(event["ended_at"].replace("Z", "+00:00")) == start, (
                f"`ended_at` is {event.get('ended_at')}, not the previous pass's time {s.iso(start)}")
            assert event.get("estimated") is True, f"an end the pass detected is not marked estimated: {event}"

    done = _report(box, start + 120)
    assert done.returncode == 0, f"gov dispatch waits --ends: exit {done.returncode}, not 0\n{s.said(done)}"
    rows = _rows(done)
    assert {key: rows.get(key, ("<no line>",))[:2] for key in wanted} == wanted, (
        f"the report does not list the three ends by id, kind and address:\n{done.stdout}")
    gaps = {key: rows[key][2] for key in wanted}
    assert all(0 <= gap <= 120 for gap in gaps.values()), f"a gap is over 120 s: {gaps}"
    assert _findings(done) == [], f"a finding with every gap within 120 s:\n{done.stdout}"
    as_json = _report(box, start + 120, "--json")
    assert as_json.returncode == 0 and all(s.mentions(s.envelope(as_json)["result"], key) for key in wanted), (
        f"the --json report does not carry the three ends\n{s.said(as_json)}")


def test_s1_a_session_gov_launch_started_leaves_an_end_event_with_its_message_id(make_rig):
    rig = make_rig(LEAD)
    rig.session("DAEO-e2l5")
    sent = [m for m in rig.home.wakes(LEAD) if str(m.get("id", "")).startswith("end:")]
    assert len(sent) == 1, f"harness: the launcher's end message: {rig.home.wakes(LEAD)}"
    event = _one_end(rig.home, sent[0]["id"])
    assert (event.get("kind"), event.get("to"), event.get("ticket")) == ("worker", LEAD, "DAEO-e2l5"), event
    assert abs(s.epoch(event["ended_at"].replace("Z", "+00:00")) - time.time()) < 30, event
    done = _report(rig.home, time.time())
    assert done.returncode == 0, f"gov dispatch waits --ends: exit {done.returncode}\n{s.said(done)}"
    row = _rows(done).get(sent[0]["id"])
    assert row and row[:2] == ("worker", LEAD) and 0 <= row[2] <= 120, f"the launched session's line:\n{done.stdout}"


def test_s1_a_planted_end_whose_message_is_200_s_late_exits_3_naming_it(box):
    planted = {"end:boot-a:101:1": ("lead", CTO, 120), "end:boot-a:102:2": ("worker", LEAD, 200),
               "job:planted-3": ("job", LEAD, 30)}
    for message_id, (kind, to, late) in planted.items():
        box.plant_end(message_id, kind, to, T, **({"job": "planted-3"} if kind == "job" else {"ticket": TICKET}))
        box.plant_message(to, message_id, s.iso(T + late), text=f"{kind} ended")
    done = _report(box, T + 3600)
    assert done.returncode == 3, f"a message 200 s after its end: exit {done.returncode}, not 3\n{s.said(done)}"
    rows = _rows(done)
    assert {key: rows.get(key, ("<no line>",))[:3] for key in planted} == planted, (
        f"the report's lines are not the three planted ends with gaps 120, 200 and 30 s:\n{done.stdout}")
    findings = _findings(done)
    assert len(findings) == 1 and "end:boot-a:102:2" in findings[0], (
        f"the findings are not the one end whose gap is over 120 s (a gap of 120 s is none): {findings}")
    as_json = _report(box, T + 3600, "--json")
    assert as_json.returncode == 3 and s.mentions(s.envelope(as_json), "end:boot-a:102:2"), s.said(as_json)


def test_s1_an_end_with_no_message_yet_is_a_gap_to_now_and_says_unsent(box):
    box.plant_end("end:boot-b:201:1", "worker", LEAD, T, ticket=TICKET)
    box.plant_end("end:boot-b:202:2", "lead", CTO, T, ticket=TICKET)
    box.plant_message(CTO, "end:boot-b:202:2", s.iso(T + 10))
    done = _report(box, T + 90)
    assert done.returncode == 0, f"an unsent end 90 s old: exit {done.returncode}, not 0\n{s.said(done)}"
    rows = _rows(done)
    unsent, sent = rows.get("end:boot-b:201:1"), rows.get("end:boot-b:202:2")
    assert unsent and unsent[2] == 90 and "unsent" in unsent[3], f"the unsent end's line (gap 90 s, unsent):\n{done.stdout}"
    assert sent and sent[2] == 10 and "unsent" not in sent[3], f"the messaged end's line (gap 10 s):\n{done.stdout}"
    late = _report(box, T + 121)
    assert late.returncode == 3, f"an unsent end 121 s old: exit {late.returncode}, not 3\n{s.said(late)}"
    findings = _findings(late)
    assert len(findings) == 1 and "end:boot-b:201:1" in findings[0], f"the finding does not name the unsent end: {findings}"
