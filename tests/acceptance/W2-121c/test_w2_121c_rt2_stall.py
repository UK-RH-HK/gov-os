"""W2-121c, RT-2 the stall check replaces the dead-man and the sentinel (success line 7).

``gov msg watch --to <address> --name <label> --transcript <file or folder> [--stall-after <s>]`` (default 3600 s) makes
each pass read the transcript's last change (the file's, or the newest file's in the folder); past ``--stall-after`` it
sends one wake message naming the label and the silent minutes, once per incident; a later change clears the incident
and a new silence sends a new message. Mtimes are set back with ``os.utime``.
"""

from __future__ import annotations

import os
import re
import time

import w2_121c_support as s

CTO_WATCHER = "cto"


def _set_back(path, seconds) -> int:
    when = int(time.time()) - seconds
    os.utime(path, (when, when))
    return when


def test_rt2c_a_silent_transcript_gives_one_message_per_incident(box):
    transcript = s.write(box.base / "session" / "cto.jsonl", '{"type": "assistant"}\n')
    first_mtime = _set_back(transcript, 2 * 3600)
    request = box.watch(CTO_WATCHER, "the cto session", "--transcript", str(transcript), "--stall-after", "600")
    box.run_pass()
    wakes = box.wakes(CTO_WATCHER)
    assert len(wakes) == 1, f"a transcript silent past the limit gave {len(wakes)} messages, not one: {wakes}"
    words = s.message_words(wakes[0])
    assert "the cto session" in words, f"the stall message does not name the label: {wakes[0]}"
    assert re.search(r"\b12[01]\b", words), f"the stall message does not name 120 silent minutes: {wakes[0]}"
    assert wakes[0].get("id") == f"stall:{request}:{first_mtime}", wakes[0]

    box.passes(3)
    assert len(box.wakes(CTO_WATCHER)) == 1, "the same incident was messaged again"

    os.utime(transcript, None)  # touched: the incident clears
    box.run_pass()
    assert len(box.wakes(CTO_WATCHER)) == 1, "a transcript just changed gave a message"
    second_mtime = _set_back(transcript, 3 * 3600)  # a new silence (a later change, then quiet again)
    box.run_pass()
    wakes = box.wakes(CTO_WATCHER)
    assert len(wakes) == 2, f"a new silence after a change gave {len(wakes) - 1} more messages, not one"
    assert wakes[1].get("id") == f"stall:{request}:{second_mtime}", wakes[1]


def test_rt2c_a_transcript_within_the_limit_gives_none(box):
    transcript = s.write(box.base / "session" / "lead.jsonl", "{}\n")
    _set_back(transcript, 300)
    box.watch("lead:DAEO-st", "the lead", "--transcript", str(transcript), "--stall-after", "600")
    box.passes(3)
    assert box.wakes("lead:DAEO-st") == [], "a transcript within its limit gave a message"


def test_rt2c_the_default_limit_is_3600_s(box):
    transcript = s.write(box.base / "session" / "default.jsonl", "{}\n")
    _set_back(transcript, 30 * 60)
    box.watch("lead:DAEO-df", "default limit", "--transcript", str(transcript))
    box.run_pass()
    assert box.wakes("lead:DAEO-df") == [], "30 silent minutes gave a message under the default 3600 s"
    _set_back(transcript, 2 * 3600)
    box.run_pass()
    assert len(box.wakes("lead:DAEO-df")) == 1, "2 silent hours gave no single message under the default 3600 s"


def test_rt2c_a_folder_is_read_by_its_newest_file(box):
    folder = box.base / "session" / "transcripts"
    old = s.write(folder / "old.jsonl", "{}\n")
    new = s.write(folder / "new.jsonl", "{}\n")
    _set_back(old, 5 * 3600)
    _set_back(new, 60)
    box.watch("lead:DAEO-fd", "a folder", "--transcript", str(folder), "--stall-after", "600")
    box.run_pass()
    assert box.wakes("lead:DAEO-fd") == [], "a folder whose newest file changed a minute ago gave a message"
    _set_back(new, 2 * 3600)
    box.run_pass()
    assert len(box.wakes("lead:DAEO-fd")) == 1, "a folder whose newest file is 2 h silent gave no single message"
