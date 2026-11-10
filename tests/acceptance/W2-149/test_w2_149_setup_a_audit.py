"""S27: the overlap auditor gets the disputes and returns decisions by rule (DEC-1113 (2); the CTO's delegated split at
40; DEC-1112 (3): the overlap auditor never appends to AUDITS.log).

The tuning half is planted with both labellers' files (``plant_labels``): 45 undecided disputes, one decided by an
earlier audit run, five agreements. The disputes, their x/y order (``random.Random(seed)``), the tickets and the
mapped-back decisions are recomputed here from the planted files and the run's seed.
"""

from __future__ import annotations

import json
import os

import pytest

import w2_149_setup_a as sa
import w2_149_support as support


def plant(world):
    sa.plant_half(world, "tuning", n_actions=48, n_cases=12)
    planted = sa.plant_labels(world, "tuning")
    assert len(planted["undecided"]) == 45, "premise: 45 undecided disputes"
    return planted


def memory_selection(world):
    """A memory writer's selection (S5) at a fixed seed: it rests on AUDITS.log's last line."""
    support.next_second()
    run = world.launch(*world.args("writer", seed=4242, dry=True))
    assert run.code == 0, run.why()
    return json.loads((world.wall(run.line) / "input/selection.json").read_text())


def tar_jsonl(world, line, suffix):
    data = world.tar_member(line, suffix)
    assert data is not None, f"no {suffix} in the packed wall"
    return [json.loads(x) for x in data.decode().splitlines() if x.strip()]


def changes(before, after):
    return {k for k in set(before) | set(after) if before.get(k) != after.get(k)}


def test_s27_the_disputes_their_x_y_order_and_the_tickets_are_staged_by_rule(world):
    planted = plant(world)
    h0 = world.hashes(world.half("tuning"))
    audits = (world.runs / "AUDITS.log").read_bytes()
    run = sa.dry(world, "overlap-auditor", "tuning", seed=5150)
    assert run.code == 0, run.why()
    wall = world.wall(run.line)
    assert sa.input_listing(wall) == ["disputes.jsonl", "half.json", "tickets.jsonl"]
    ids_run = sorted(planted["undecided"])[:40]
    assert planted["earlier"] not in ids_run
    assert json.loads((wall / "input/half.json").read_text()) == {"half": "tuning", "pin": world.sha("B"), "cases": 40}
    assert sa.read_jsonl(wall / "input/disputes.jsonl") == sa.expected_disputes(world, "tuning", planted, 5150, ids_run)
    tickets = sa.read_jsonl(wall / "input/tickets.jsonl")
    assert sorted(tickets, key=lambda t: t["id"]) == sa.expected_tickets(world, "tuning", ids_run)
    assert all(set(t) == {"id", "role", "wbs_id", "allowed_paths"} for t in tickets)
    names = [n for _dp, _dn, fn in os.walk(wall) for n in fn]
    assert not any("map" in n for n in names), f"a map in the wall: {names}"
    inputs = b"".join((wall / "input" / n).read_bytes() for n in sa.input_listing(wall))
    for needle in (support.TICKET_MARK, sa.WHAT_CAME_BACK, sa.PLANTED_EXTRA, "labeller-1", "labeller-2", "labels-2"):
        assert needle.encode() not in inputs, needle
    assert world.hashes(world.half("tuning")) == h0, "a dry build changed the half's folder"
    assert (world.runs / "AUDITS.log").read_bytes() == audits
    assert world.calls() == []


def test_s27_a_delivered_audit_maps_x_y_back_and_writes_the_labels_by_rule(world):
    """45 disputes give runs of 40 and 5; the map from the seed, outside the wall; decisions mapped back; settled
    cases take the auditor's label, rule_class, clauses (its basis) and reason with `audit`, flagged ones keep
    labeller 1's line with `owner` and are appended to owner.jsonl; the old labels.jsonl in history/; nothing else
    changes (S16); no AUDITS.log line and a memory writer's selection unchanged. The disputes' reasons are blinded
    (either empty, both empty)."""
    planted = plant(world)
    h = world.half("tuning")
    old_labels = (h / "labels/labels.jsonl").read_bytes()
    audits = (world.runs / "AUDITS.log").read_bytes()
    memory_before = memory_selection(world)
    sr0, exp0 = world.hashes(world.sr), world.hashes(world.exp)
    run = sa.deliver(world, "overlap-auditor", "tuning", program="decide")
    assert run.code == 0, run.why()
    line = run.line
    rid = line["run"]
    seed = sa.seed_of(world, rid)
    ids_run = sorted(planted["undecided"])[:40]
    order = sa.xy(seed, ids_run)
    assert {a for a, _b in order.values()} == {1, 2}, "premise: both orders drawn"
    assert tar_jsonl(world, line, "input/disputes.jsonl") == sa.expected_disputes(world, "tuning", planted, seed, ids_run)
    assert not any("map" in n.rsplit("/", 1)[-1] for n in world.tar_names(line)), "a map in the packed wall"
    the_map = json.loads((h / f"labels/audit/{rid}.map.json").read_text())
    assert the_map == {i: {"x": a, "y": b} for i, (a, b) in order.items()}
    decisions = tar_jsonl(world, line, "out/decisions.jsonl")
    assert [d["id"] for d in decisions] == ids_run
    assert sa.read_jsonl(h / f"labels/audit/{rid}.decisions.jsonl") == sa.mapped_back(decisions, order)
    got = sa.read_jsonl(h / "labels/labels.jsonl")
    assert [x["id"] for x in got] == planted["ids"]
    dec = {d["id"]: d for d in decisions}
    old = {x["id"]: x for x in planted["lines1"]}
    for x in got:
        d = dec.get(x["id"])
        if d is None:
            assert x == old[x["id"]], x
        elif d["flag"] == "none":
            assert x == sa.settled_line(d), ("a settled line is not the auditor's decision (S27, F22)", x, d)
        else:
            assert x == dict(old[x["id"]], how="owner"), ("a flagged line is not labeller 1's with how owner", x, d)
    history = sorted((h / "labels/history").iterdir())
    assert len(history) == 1 and history[0].read_bytes() == old_labels
    owner = sa.read_jsonl(h / "labels/owner.jsonl")
    assert owner[0] == {"id": "an-earlier-owner-case", "run": "planted"}
    assert [x["id"] for x in owner[1:]] == [d["id"] for d in decisions if d["flag"] != "none"]
    assert changes(exp0, world.hashes(world.exp)) == {
        "tuning/labels/labels.jsonl", "tuning/labels/owner.jsonl", f"tuning/labels/audit/{rid}.decisions.jsonl",
        f"tuning/labels/audit/{rid}.map.json", os.path.relpath(history[0], world.exp)}
    assert changes(sr0, world.hashes(world.sr)) == {f"indep-walls/auditor/{rid}.tar"}
    d = line["delivered"]
    assert d["to"] == "decisions" and d["sha256"] == support.sha_file(h / f"labels/audit/{rid}.decisions.jsonl"), d
    sa.assert_counts(world, line, json.loads(world.tar_member(line, "out/result.json")))
    assert (world.runs / "AUDITS.log").read_bytes() == audits, "the overlap auditor appended to AUDITS.log"
    assert memory_selection(world) == memory_before, "a memory writer's selection changed"
    rest = sorted(planted["undecided"])[40:]
    run2 = sa.dry(world, "overlap-auditor", "tuning", seed=5150)
    assert run2.code == 0, run2.why()
    wall2 = world.wall(run2.line)
    assert json.loads((wall2 / "input/half.json").read_text())["cases"] == 5
    assert sa.read_jsonl(wall2 / "input/disputes.jsonl") == sa.expected_disputes(world, "tuning", planted, 5150, rest)


@pytest.mark.parametrize("bad", ["drop_last", "swap", "reason_on_none", "flag_word"])
def test_s27_a_decisions_file_out_of_rule_is_rejected_20(world, bad):
    plant(world)
    h0 = world.hashes(world.half("tuning"))
    audits = (world.runs / "AUDITS.log").read_bytes()
    run = sa.deliver(world, "overlap-auditor", "tuning", program="decide", program_args={"bad": bad})
    assert run.code == 20, run.why()
    assert run.line["status"] == "rejected" and run.line["reason"] == "result", run.line
    assert world.hashes(world.half("tuning")) == h0, "the half's folder changed"
    assert (world.runs / "AUDITS.log").read_bytes() == audits
