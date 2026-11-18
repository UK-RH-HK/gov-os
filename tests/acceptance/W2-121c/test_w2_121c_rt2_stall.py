"""W2-121c, RT-2 the stall check replaces the dead-man and the sentinel (success line 7, amended c82d31a56: the owner's
working assumptions T1 (c), T2 (b)).

``gov msg watch --to <address> --name <label> --transcript <file or folder> [--stall-after <s>] [--night-stall-after
<s>] [--night <HH:MM-HH:MM>] [--push <command>]`` makes each pass read the transcript's last change (the file's, or the
newest file's in the folder); past the limit (3600 s by day, 7200 s while the local time is in the night window,
02:00-07:30 by default) it sends one wake message naming the label and the silent minutes and, with ``--push``, runs
that command once, detached, with the message text as its last argument; once per incident, never a reminder; a later
change clears the incident, and a new silence sends a new message and push.

Every pass here reads its clock from ``GOV_RUNTIME_NOW`` (ISO-8601, with TZ=UTC so local time is UTC): DAY is 12:00,
NIGHT 03:30, both on 2026-11-16; transcript mtimes are set relative to them with ``os.utime``.
"""

from __future__ import annotations

import os
import re
import time

import w2_121c_support as s

DAY_ISO, NIGHT_ISO = "2026-11-16T12:00:00+00:00", "2026-11-16T03:30:00+00:00"
DAY, NIGHT = int(s.epoch(DAY_ISO)), int(s.epoch(NIGHT_ISO))
AT_DAY, AT_NIGHT = {"GOV_RUNTIME_NOW": DAY_ISO}, {"GOV_RUNTIME_NOW": NIGHT_ISO}
CTO = "cto"


def _set(path, when) -> int:
    os.utime(path, (when, when))
    return int(when)


def test_rt2c_a_silent_transcript_gives_one_message_and_one_push_per_incident(box):
    stub, log = s.push_stub(box.base)
    transcript = s.write(box.base / "session" / "cto.jsonl", '{"type": "assistant"}\n')
    first_mtime = _set(transcript, DAY - 2 * 3600)
    request = box.watch(CTO, "the cto session", "--transcript", str(transcript), "--stall-after", "600",
                        "--push", str(stub))
    box.run_pass(extra_env=AT_DAY)
    wakes = box.wakes(CTO)
    assert len(wakes) == 1, f"a transcript silent past the limit gave {len(wakes)} messages, not one: {wakes}"
    words = s.message_words(wakes[0])
    assert "the cto session" in words, f"the stall message does not name the label: {wakes[0]}"
    assert re.search(r"\b120\b", words), f"the stall message does not name 120 silent minutes: {wakes[0]}"
    assert wakes[0].get("id") == f"stall:{request}:{first_mtime}", wakes[0]
    runs = s.wait_for_runs(log, 1, 5.0)
    assert len(runs) == 1, f"the push stub ran {len(runs)} times for one incident, not once: {runs}"
    assert runs[0] and runs[0][-1] == wakes[0].get("text"), (
        f"the push's last argument is not the message text: {runs[0]!r} / {wakes[0].get('text')!r}")

    box.passes(3, extra_env=AT_DAY)
    assert len(box.wakes(CTO)) == 1, "the same incident was messaged again"
    assert len(s.push_runs(log, settle=1.0)) == 1, "the same incident was pushed again (a reminder)"

    _set(transcript, DAY - 60)  # touched: the incident clears
    box.run_pass(extra_env=AT_DAY)
    assert len(box.wakes(CTO)) == 1, "a transcript just changed gave a message"
    second_mtime = _set(transcript, DAY - 3 * 3600)  # a new silence, at another mtime (P-W2-121c-td-1 (a))
    box.run_pass(extra_env=AT_DAY)
    wakes = box.wakes(CTO)
    assert len(wakes) == 2, f"a new silence after a change gave {len(wakes) - 1} more messages, not one"
    assert wakes[1].get("id") == f"stall:{request}:{second_mtime}", wakes[1]
    runs = s.wait_for_runs(log, 2, 5.0)
    assert len(runs) == 2, f"a new silence after a change gave {len(runs) - 1} more pushes, not one: {runs}"
    assert runs[1][-1] == wakes[1].get("text"), f"the second push's last argument: {runs[1]!r}"


def test_rt2c_a_transcript_within_the_limit_gives_none(box):
    stub, log = s.push_stub(box.base)
    transcript = s.write(box.base / "session" / "lead.jsonl", "{}\n")
    _set(transcript, DAY - 300)
    box.watch("lead:DAEO-st", "the lead", "--transcript", str(transcript), "--stall-after", "600", "--push", str(stub))
    box.passes(3, extra_env=AT_DAY)
    assert box.wakes("lead:DAEO-st") == [], "a transcript within its limit gave a message"
    assert s.push_runs(log, settle=1.0) == [], "a transcript within its limit was pushed"


def test_rt2c_the_day_limit_defaults_to_3600_s(box):
    transcript = s.write(box.base / "session" / "default.jsonl", "{}\n")
    _set(transcript, DAY - 30 * 60)
    box.watch("lead:DAEO-df", "default limit", "--transcript", str(transcript))
    box.run_pass(extra_env=AT_DAY)
    assert box.wakes("lead:DAEO-df") == [], "30 silent minutes by day gave a message under the default 3600 s"
    _set(transcript, DAY - 65 * 60)
    box.run_pass(extra_env=AT_DAY)
    assert len(box.wakes("lead:DAEO-df")) == 1, "65 silent minutes by day gave no single message (default 3600 s)"


def test_rt2c_at_night_90_minutes_give_none_and_130_minutes_give_one(box):
    transcript = s.write(box.base / "session" / "night.jsonl", "{}\n")
    _set(transcript, NIGHT - 90 * 60)
    box.watch(CTO, "the cto at night", "--transcript", str(transcript))
    box.run_pass(extra_env=AT_NIGHT)
    assert box.wakes(CTO) == [], "90 silent minutes at 03:30 gave a message (the night limit is 7200 s)"
    _set(transcript, NIGHT - 130 * 60)
    box.run_pass(extra_env=AT_NIGHT)
    wakes = box.wakes(CTO)
    assert len(wakes) == 1, f"130 silent minutes at 03:30 gave {len(wakes)} messages, not one"
    assert re.search(r"\b130\b", s.message_words(wakes[0])), f"the message does not name 130 minutes: {wakes[0]}"


def test_rt2c_without_push_no_command_runs(box):
    transcript = s.write(box.base / "session" / "quiet.jsonl", "{}\n")
    _set(transcript, DAY - 2 * 3600)
    box.watch(CTO, "no push", "--transcript", str(transcript), "--stall-after", "600")
    box.run_pass(extra_env=AT_DAY)
    assert len(box.wakes(CTO)) == 1, "the stall gave no single message"
    time.sleep(1.0)
    assert box.claude_calls() == [], f"a command ran without --push (the claude stand-in): {box.claude_calls()}"


def test_rt2c_the_push_runs_detached_and_the_pass_does_not_wait_for_it(box):
    stub, log = s.push_stub(box.base, name="slow-push", delay=8)
    transcript = s.write(box.base / "session" / "slow.jsonl", "{}\n")
    _set(transcript, DAY - 2 * 3600)
    box.watch(CTO, "a slow push", "--transcript", str(transcript), "--stall-after", "600", "--push", str(stub))
    started = time.monotonic()
    box.run_pass(extra_env=AT_DAY)
    took = time.monotonic() - started
    assert took < 5.0, f"the pass took {took:.1f} s: it waited for a push that takes 8 s"
    assert len(box.wakes(CTO)) == 1, "the stall gave no single message"
    runs = s.wait_for_runs(log, 1, 10.0)
    assert len(runs) == 1, f"the slow push did not run once after the pass returned: {runs}"


def test_rt2c_a_folder_is_read_by_its_newest_file(box):
    folder = box.base / "session" / "transcripts"
    old = s.write(folder / "old.jsonl", "{}\n")
    new = s.write(folder / "new.jsonl", "{}\n")
    _set(old, DAY - 5 * 3600)
    _set(new, DAY - 60)
    box.watch("lead:DAEO-fd", "a folder", "--transcript", str(folder), "--stall-after", "600")
    box.run_pass(extra_env=AT_DAY)
    assert box.wakes("lead:DAEO-fd") == [], "a folder whose newest file changed a minute ago gave a message"
    _set(new, DAY - 2 * 3600)
    box.run_pass(extra_env=AT_DAY)
    assert len(box.wakes("lead:DAEO-fd")) == 1, "a folder whose newest file is 2 h silent gave no single message"
