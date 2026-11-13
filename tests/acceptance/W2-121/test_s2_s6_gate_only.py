"""S2 and S6, review round 1 finding F-5: the refusal that only the gate gives.

Reading fixed by the fix round: a gate shut for load or for CPU (not memory), with memory ample for every peak (so the
room check alone would admit the start), refuses every entry with a reason that names the gate ("gate shut"), exit 3,
no start. The reason must not rest on memory or on a room check: the entry's own part of the status names the gate.
The same holds when the gate is shut for memory: the reason names the gate, not only a memory figure.
"""

from __future__ import annotations

import re

import pytest

import w2_121_support as support
from w2_121_support import candidates, explain, named_with


def refused_by_the_gate(p, entries, r) -> None:
    assert r.code == 3, r
    p.settle()
    assert p.launches() == [], "a session started with the gate shut"
    assert p.started() == []
    for entry in entries:
        assert named_with(p, entry.log, r"gate|shut"), f"{entry.log} is not named with the gate" + explain(p, r)
        pieces = candidates(p.status_json(), p.status_text(), entry.log)
        resting = [c for c in pieces if re.search(r"(?i)memory|no room", c) and not re.search(r"(?i)gate|shut", c)]
        assert not resting, f"{entry.log} is refused for a reason that rests on memory or room, not the gate: {resting}"
    assert any(k == "open" and v is False for k, v in support.walk(p.status_json())), "the status does not show a shut gate"


@pytest.mark.parametrize("change, word", [({"load": (30.0, 30.0, 30.0)}, "load"), ({"busy": 20.0}, "cpu")],
                         ids=["load", "cpu"])
def test_s2_a_gate_shut_for_load_or_cpu_with_ample_memory_refuses_every_entry_by_the_gate(project, change, word):
    p = project
    entries = [p.add_ticket(901), p.add_ticket(902)]
    p.set_machine(mem_gib=16, **change)  # memory 16 GiB: the floor and every working size fit many times over
    reading = p.gate_reading()
    assert reading["open"] is False, reading
    assert any(word in reason.lower() for reason in reading["reasons"]), reading
    assert not any("memory" in reason.lower() for reason in reading["reasons"]), reading
    p.ready(*entries)
    r = p.tick()
    refused_by_the_gate(p, entries, r)


def test_s2_the_same_machine_with_the_gate_open_starts_the_entry(project):
    p = project
    entry = p.add_ticket(901)
    p.set_machine(mem_gib=16)
    assert p.gate_reading()["open"] is True
    p.ready(entry)
    assert p.tick().code == 0
    p.wait_launches(1)
    assert p.launched_logs() == [entry.log]


def test_s6_a_gate_shut_for_load_refuses_a_review_launch_and_a_plain_one_alike(project):
    p = project
    entries = [p.add_ticket(901), p.add_ticket(902, brief="# Review brief\n\nrun: review\n\nReview it.\n")]
    p.set_machine(mem_gib=16, load=(30.0, 30.0, 30.0))
    p.ready(*entries)
    r = p.tick()
    refused_by_the_gate(p, entries, r)
