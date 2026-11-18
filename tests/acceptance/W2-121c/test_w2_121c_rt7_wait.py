"""W2-121c, RT-7 one wake rule (success line 3).

A session is woken when its inbox has an unread ``wake`` message past its mark: ``gov msg wait [<address>] [--timeout
<s>]`` exits 0 as soon as one exists (printing it, the mark unmoved), keeps waiting while only ``notice`` messages are
unread, and exits 124 when the timeout passes. Short timeouts only (a few seconds).
"""

from __future__ import annotations

import time

import w2_121c_support as s

LEAD = "lead:DAEO-r7"


def test_rt7a_a_wake_already_unread_returns_0_at_once_printing_it_mark_unmoved(box):
    box.send(LEAD, "notice", "an idle notice")
    box.send(LEAD, "wake", "worker DAEO-r7 returned")
    mark = box.mark_bytes(LEAD)
    started = time.monotonic()
    done = box.gov("msg", "wait", LEAD, "--timeout", "8", timeout=20)
    elapsed = time.monotonic() - started
    assert done.returncode == 0, f"the wait did not exit 0 with a wake message unread\n{s.said(done)}"
    assert elapsed < 4.0, f"the wait took {elapsed:.1f} s with a wake message already unread, not at once"
    assert "worker DAEO-r7 returned" in done.stdout, f"the wait did not print the wake message\n{s.said(done)}"
    assert box.mark_bytes(LEAD) == mark, "the wait moved the mark"


def test_rt7a_a_wake_sent_2_s_after_the_wait_began_returns_0_within_5_s(box):
    box.send(LEAD, "notice", "a notice before the wait")
    mark = box.mark_bytes(LEAD)
    proc = box.popen("msg", "wait", LEAD, "--timeout", "9")
    time.sleep(2.0)
    assert proc.poll() is None, (f"the wait ended (exit {proc.returncode}) before any wake message was sent\n"
                                 f"{proc.communicate()}")
    box.send(LEAD, "wake", "the late wake message")
    sent_at = time.monotonic()
    try:
        out, err = proc.communicate(timeout=6)
    except Exception:
        proc.kill()
        raise AssertionError("the wait did not end after the wake message was sent") from None
    after = time.monotonic() - sent_at
    assert proc.returncode == 0, f"the wait exited {proc.returncode}, not 0\nstdout:\n{out}\nstderr:\n{err}"
    assert after <= 3.0, f"the wait ended {after:.1f} s after the send: past the 5 s from its start"
    assert "the late wake message" in out, f"the wait did not print the wake message\n{out}"
    assert box.mark_bytes(LEAD) == mark, "the wait moved the mark"


def test_rt7a_only_notices_unread_keeps_waiting_and_exits_124_at_the_timeout(box):
    box.send(LEAD, "notice", "notice one")
    box.send(LEAD, "notice", "notice two")
    mark = box.mark_bytes(LEAD)
    started = time.monotonic()
    done = box.gov("msg", "wait", LEAD, "--timeout", "2", timeout=20)
    elapsed = time.monotonic() - started
    assert done.returncode == 124, f"the wait with only notices unread exited {done.returncode}, not 124\n" \
                                   f"{s.said(done)}"
    assert elapsed >= 1.9, f"the wait ended after {elapsed:.1f} s, before its 2 s timeout"
    assert box.mark_bytes(LEAD) == mark, "the wait moved the mark"


def test_rt7a_every_wake_already_read_exits_124_at_the_timeout(box):
    box.send(LEAD, "wake", "an old wake message")
    read = box.gov("msg", "read", LEAD)
    assert read.returncode == 0, s.said(read)
    box.send(LEAD, "notice", "a later notice")
    mark = box.mark_bytes(LEAD)
    assert mark is not None, "the read left no mark"
    started = time.monotonic()
    done = box.gov("msg", "wait", LEAD, "--timeout", "2", timeout=20)
    elapsed = time.monotonic() - started
    assert done.returncode == 124, f"the wait with every wake message read exited {done.returncode}, not 124\n" \
                                   f"{s.said(done)}"
    assert elapsed >= 1.9, f"the wait ended after {elapsed:.1f} s, before its 2 s timeout"
    assert box.mark_bytes(LEAD) == mark, "the wait moved the mark"
