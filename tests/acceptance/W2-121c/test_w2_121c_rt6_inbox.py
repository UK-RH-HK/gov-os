"""W2-121c, RT-6: per-session inbox files with a read mark, machine-wide (success lines 1 and 2).

Line 1 (RT-6a): ``gov msg send`` appends one JSON line to ``~/.gov-os/inbox/<to>/messages.jsonl``; ``gov msg read``
prints the messages past ``mark`` and moves it, so each is read once; ``--peek`` leaves the mark; the address defaults
to ``$GOV_MSG_ADDRESS``; the inbox does not depend on the project root; an address with ``/`` or ``..`` is refused
(``MSG_ADDRESS_INVALID``, exit 1) and nothing is written.

Line 2 (RT-6b): ``--id`` already in that inbox is not appended again; the second send answers it is a duplicate, exit 0.
"""

from __future__ import annotations

import json
import subprocess

import pytest

import w2_121c_support as s

LEAD = "lead:DAEO-r6"


def read_json(box, *args, extra_env=None, cwd=None) -> dict:
    return box.ok("msg", "read", *args, extra_env=extra_env, cwd=cwd)


def texts(result) -> list[str]:
    messages = result.get("messages")
    assert isinstance(messages, list), f"gov msg read --json gave no messages list: {result}"
    return [item.get("text") for item in messages]


# --------------------------------------------------------------------------
# Line 1 (RT-6a)
# --------------------------------------------------------------------------

def test_rt6a_a_send_appends_one_json_line_and_two_reads_print_it_once(box):
    sent = box.send(LEAD, "notice", "the build is green")
    lines = box.inbox_file(LEAD).read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1, f"one send did not append exactly one line: {lines}"
    message = json.loads(lines[0])
    assert {"id", "at", "from", "to", "kind", "text"} <= set(message), f"the message lacks a field: {message}"
    assert (message["to"], message["kind"], message["text"]) == (LEAD, "notice", "the build is green"), message
    assert sent.get("id") == message["id"] and sent.get("sent") is True, f"the send's result: {sent}"

    first = box.gov("msg", "read", LEAD)
    assert first.returncode == 0, s.said(first)
    assert "the build is green" in first.stdout, f"the first read did not print the message\n{s.said(first)}"
    second = box.gov("msg", "read", LEAD)
    assert second.returncode == 0, s.said(second)
    assert "the build is green" not in second.stdout, f"the second read printed it again\n{s.said(second)}"


def test_rt6a_read_json_moves_the_mark_to_the_end_of_what_it_read(box):
    box.send(LEAD, "wake", "one")
    box.send(LEAD, "notice", "two")
    result = read_json(box, LEAD)
    assert texts(result) == ["one", "two"], result
    size = box.inbox_file(LEAD).stat().st_size
    assert box.mark_bytes(LEAD) is not None and int(box.mark_bytes(LEAD).decode().strip()) == size, (
        f"the mark is not the byte offset past the messages read ({size}): {box.mark_bytes(LEAD)!r}")
    box.send(LEAD, "notice", "three")
    assert texts(read_json(box, LEAD)) == ["three"], "a read after a new send gives only the new message"
    assert texts(read_json(box, LEAD)) == [], "a read with nothing new gives nothing"


def test_rt6a_peek_prints_without_moving_the_mark(box):
    box.send(LEAD, "notice", "peeked")
    mark = box.mark_bytes(LEAD)
    assert texts(read_json(box, LEAD, "--peek")) == ["peeked"]
    assert box.mark_bytes(LEAD) == mark, "--peek moved the mark"
    assert texts(read_json(box, LEAD, "--peek")) == ["peeked"], "a second peek no longer sees the message"
    assert texts(read_json(box, LEAD)) == ["peeked"], "a read after peeks does not see the message"
    assert texts(read_json(box, LEAD)) == []


def test_rt6a_the_address_defaults_to_gov_msg_address(box):
    box.send(LEAD, "notice", "for the default address")
    env = {"GOV_MSG_ADDRESS": LEAD}
    assert texts(read_json(box, extra_env=env)) == ["for the default address"]
    assert texts(read_json(box, LEAD)) == [], "the read through $GOV_MSG_ADDRESS did not move that address's mark"


def test_rt6a_no_address_and_no_gov_msg_address_is_refused(box):
    done = box.gov("msg", "read", "--json")
    assert done.returncode == 1, f"a read with no address was not refused with exit 1\n{s.said(done)}"
    assert "MSG_ADDRESS_MISSING" in done.stdout + done.stderr, s.said(done)


def test_rt6a_two_sessions_in_two_repositories_exchange_messages_with_no_relay(box):
    one, two = box.base / "repo-one", box.base / "repo-two"
    for repo in (one, two):
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True, env=box.env())
    sent = box.gov("msg", "send", "cto", "wake", "from repository one", "--from", "examin-cto", "--json", cwd=one,
                   extra_env={"GOV_MSG_ADDRESS": "examin-cto"})
    assert sent.returncode == 0, s.said(sent)
    got = read_json(box, "cto", cwd=two)
    assert texts(got) == ["from repository one"], f"the session in repository two did not read it: {got}"
    for repo in (one, two):
        left = [str(p.relative_to(repo)) for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts]
        assert not left, f"the inbox wrote into the repository {repo.name}: {left}"
    assert box.inbox_file("cto").is_file(), "the message is not in HOME's inbox"


def test_rt6a_eight_concurrent_senders_give_400_whole_lines_each_read_exactly_once(box):
    address = "lead:DAEO-many"
    box.send(address, "notice", "seed")  # the inbox exists before the readers start
    stop = box.base / "stop-readers"
    go_r, readers = box.drivers(2, 0, ["msg", "read", address, "--json"], stop=stop)
    go_s, senders = box.drivers(8, 50, ["msg", "send", address, "notice", "s{n}-{i}", "--json"])
    go_r.touch()
    go_s.touch()
    sent = box.driver_results(senders)
    stop.touch()
    read = box.driver_results(readers)
    codes = {call["rc"] for calls in sent for call in calls}
    assert codes == {0}, f"concurrent sends did not all exit 0: {sorted(codes, key=str)}"

    lines = [item for item in box.messages(address) if item.get("text") != "seed"]  # every line whole JSON
    assert len(lines) == 400, f"8 senders of 50 left {len(lines)} lines, not 400"
    assert sorted(item["text"] for item in lines) == sorted(f"s{n}-{i}" for n in range(8) for i in range(50))

    seen = []
    for calls in read:
        for call in calls:
            assert call["rc"] == 0, f"a concurrent read failed: {call['out'][-500:]}"
            seen += texts(json.loads(call["out"])["result"])
    seen += texts(read_json(box, address))
    seen = [text for text in seen if text != "seed"]
    duplicates = sorted({text for text in seen if seen.count(text) > 1})
    assert not duplicates, f"messages read more than once: {duplicates[:10]}"
    assert len(seen) == 400, f"{len(seen)} messages read across the readers, not 400"


@pytest.mark.parametrize("address", ["lead/DAEO-x", "..", "lead..x", "../escape"])
def test_rt6a_an_address_with_a_slash_or_dotdot_is_refused_and_nothing_is_written(box, address):
    before = box.home_files()
    done = box.gov("msg", "send", address, "wake", "never written", "--json")
    assert done.returncode == 1, f"the address {address!r} was not refused with exit 1\n{s.said(done)}"
    assert "MSG_ADDRESS_INVALID" in done.stdout + done.stderr, s.said(done)
    read = box.gov("msg", "read", address, "--json")
    assert read.returncode == 1 and "MSG_ADDRESS_INVALID" in read.stdout + read.stderr, s.said(read)
    assert box.home_files() == before, "a refused address wrote under HOME"
    outside = [p for p in box.base.rglob("*") if p.is_file() and "never written" in p.read_text(errors="replace")]
    assert not outside, f"the refused message was written: {outside}"


# --------------------------------------------------------------------------
# Line 2 (RT-6b)
# --------------------------------------------------------------------------

def test_rt6b_the_same_id_sent_twice_leaves_one_line_the_second_a_duplicate(box):
    first = box.send(LEAD, "wake", "the end of DAEO-x", "--id", "end:fixture:1")
    second = box.send(LEAD, "wake", "the end of DAEO-x", "--id", "end:fixture:1")
    assert len(box.messages(LEAD)) == 1, f"the same id sent twice left {len(box.messages(LEAD))} lines"
    assert (first.get("sent"), first.get("duplicate")) == (True, False), f"the first send: {first}"
    assert (second.get("sent"), second.get("duplicate")) == (False, True), f"the second send: {second}"
    assert second.get("id") == "end:fixture:1" and second.get("to") == LEAD, second


def test_rt6b_the_same_id_sent_concurrently_from_four_processes_leaves_one_line(box):
    go, started = box.drivers(4, 1, ["msg", "send", LEAD, "wake", "raced", "--id", "end:race:4", "--json"])
    go.touch()
    results = [calls[0] for calls in box.driver_results(started)]
    assert [call["rc"] for call in results] == [0, 0, 0, 0], f"a concurrent send did not exit 0: {results}"
    assert len(box.messages(LEAD)) == 1, f"4 concurrent sends of one id left {len(box.messages(LEAD))} lines"
    answers = [json.loads(call["out"])["result"] for call in results]
    assert sorted(bool(a.get("duplicate")) for a in answers) == [False, True, True, True], answers


def test_rt6b_an_id_is_a_duplicate_only_in_its_own_inbox(box):
    box.send(LEAD, "wake", "to the lead", "--id", "shared-id")
    other = box.send("cto", "wake", "to the cto", "--id", "shared-id")
    assert other.get("sent") is True and other.get("duplicate") is False, other
    assert len(box.messages(LEAD)) == 1 and len(box.messages("cto")) == 1
