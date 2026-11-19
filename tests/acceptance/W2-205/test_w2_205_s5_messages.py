"""W2-205, success line 5 (RT-6): no message passes through the owner.

``gov msg send`` and ``read`` serve the addresses ``cto``, ``examin-cto``, ``lead:<ticket>``, ``worker:<ticket>:<role>``
and ``operator``, with the kinds ``wake``, ``notice`` and ``relay``; ``gov msg digest [<address>] [--day <YYYY-MM-DD>]``
prints ``<day> <n> notices``, one line a day; a notice or a relay never wakes; ``gov msg audit --days <n>`` scans every
inbox file and prints one line (id, from, to) for each relay (kind ``relay``, or ``from`` or ``to`` ``owner``), exit 3
when any, else 0.
"""

from __future__ import annotations

import time

import pytest

import w2_205_support as s

ADDRESSES = ("cto", "examin-cto", "lead:DAEO-m605", "worker:DAEO-m605:engineer", "operator")
LEAD = "lead:DAEO-m605"


def _text(done) -> str:
    assert done.returncode == 0, f"exit {done.returncode}, not 0\n{s.said(done)}"
    return done.stdout


def _audit(box, days="7"):
    return box.gov("msg", "audit", "--days", days)


def test_s5_messages_among_the_five_address_kinds_are_each_read_once_in_the_order_sent(box):
    sent = {address: [] for address in ADDRESSES}
    for n, kind in enumerate(("wake", "notice", "relay")):
        for i, address in enumerate(ADDRESSES):
            sender = ADDRESSES[(i + 1 + n) % len(ADDRESSES)]
            result = box.send(address, kind, f"{kind} {n} for {address}", "--from", sender)
            sent[address].append((result["id"], kind, sender))
    for address in ADDRESSES:
        read = box.ok("msg", "read", address)["messages"]
        assert [(m.get("id"), m.get("kind"), m.get("from")) for m in read] == sent[address], (
            f"{address} did not read its three messages in the order sent: {read}")
        assert box.ok("msg", "read", address)["messages"] == [], f"{address} read a message twice"
        assert box.mark_bytes(address), f"{address}'s inbox keeps no read mark"


def test_s5_five_notices_give_one_digest_line_and_no_wake(box):
    for n, what in enumerate(("structural", "idle", "GPU info", "structural", "idle")):
        box.send(LEAD, "notice", f"{what} notice {n}", "--from", "cto")
    days = sorted({m["at"][:10] for m in box.messages(LEAD)})
    assert len(days) == 1, "harness: the five notices were sent across midnight; run the case again"
    line = f"{days[0]} 5 notices"
    by_env = _text(box.gov("msg", "digest", extra_env={"GOV_MSG_ADDRESS": LEAD}))
    assert by_env.splitlines() == [line], f"the digest of five notices is not the one line {line!r}:\n{by_env}"
    assert _text(box.gov("msg", "digest", LEAD)).splitlines() == [line], "the digest by argument differs"
    assert box.stop_check(LEAD) is None, "a notice blocked the turn's end"
    waited = box.gov("msg", "wait", LEAD, "--timeout", "1")
    assert waited.returncode == 124, f"a notice woke the session: gov msg wait exit {waited.returncode}"


def test_s5_the_digest_is_one_line_a_day_for_notices_read_or_unread(box):
    for n, (day, kind) in enumerate([("2026-11-16", "notice")] * 3 + [("2026-11-17", "notice")] * 2
                                    + [("2026-11-17", "wake"), ("2026-11-17", "relay")]):
        box.plant_message(LEAD, f"planted-{n}", f"{day}T0{n}:15:00Z", kind=kind, text=f"{kind} {n}", sender="cto")
    want = ["2026-11-16 3 notices", "2026-11-17 2 notices"]
    assert _text(box.gov("msg", "digest", LEAD)).splitlines() == want, "the digest is not one line a day of notices"
    assert len(box.ok("msg", "read", LEAD)["messages"]) == 7
    assert _text(box.gov("msg", "digest", LEAD)).splitlines() == want, "reading the inbox changed the digest"
    one = _text(box.gov("msg", "digest", LEAD, "--day", "2026-11-17"))
    assert one.splitlines() == ["2026-11-17 2 notices"], f"--day 2026-11-17 gave:\n{one}"


def test_s5_a_relay_never_wakes(box):
    box.send(LEAD, "relay", "the owner asked me to pass this on", "--from", "cto")
    assert box.stop_check(LEAD) is None, "a relay blocked the turn's end"
    waited = box.gov("msg", "wait", LEAD, "--timeout", "1")
    assert waited.returncode == 124, f"a relay woke the session: gov msg wait exit {waited.returncode}"


def test_s5_the_audit_exits_0_when_no_message_names_the_owner(box):
    for i, address in enumerate(ADDRESSES):
        box.send(address, "wake" if i % 2 else "notice", "among the roles", "--from", ADDRESSES[i - 1])
    done = _audit(box)
    assert done.returncode == 0, f"gov msg audit with no relay: exit {done.returncode}, not 0\n{s.said(done)}"


@pytest.mark.parametrize("kind, sender, inbox", [("relay", "cto", LEAD), ("notice", "owner", LEAD),
                                                 ("wake", "cto", "owner")])
def test_s5_the_audit_exits_3_naming_each_relay(box, kind, sender, inbox):
    clean = box.send("operator", "notice", "among the roles", "--from", "cto")
    now = s.iso(time.time())
    box.plant_message(inbox, "zq205-relay-1", now, kind=kind, text="passed through the owner", sender=sender)
    done = _audit(box)
    assert done.returncode == 3, f"a {kind} from {sender} to {inbox}: audit exit {done.returncode}, not 3\n{s.said(done)}"
    lines = [line for line in done.stdout.splitlines() if "zq205-relay-1" in line]
    assert len(lines) == 1 and sender in lines[0] and inbox in lines[0], (
        f"no one line names the relay's id, from and to:\n{done.stdout}")
    assert clean["id"] not in done.stdout, f"a message among the roles is listed as a relay:\n{done.stdout}"


def test_s5_the_audit_counts_the_last_n_days_only(box):
    box.plant_message(LEAD, "zq205-old-relay", s.iso(time.time() - 30 * 86400), kind="relay", sender="owner")
    recent = _audit(box, "7")
    assert recent.returncode == 0, f"a relay 30 days old: --days 7 exit {recent.returncode}, not 0\n{s.said(recent)}"
    wide = _audit(box, "60")
    assert wide.returncode == 3 and "zq205-old-relay" in wide.stdout, f"--days 60 does not name it\n{s.said(wide)}"
