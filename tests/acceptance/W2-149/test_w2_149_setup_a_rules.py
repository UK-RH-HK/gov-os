"""S25 (the first labeller's rule script runs confined), S26 (the first labeller's labels are complete before they
land). DEC-1112 (3); the sandbox README item 1; the declaration §5.

Round 1 is a run with the stub's session delivering a planted ``label_rules.py``; round 2 runs it. The cases that need
a working ``bwrap`` carry the marker ``bwrap`` and are kept out of the default run (``GOV_W2_149_BWRAP=1`` runs them):
the launch sandbox cannot start a nested ``bwrap`` (no unprivileged user namespaces), so the CTO runs them outside it.
"""

from __future__ import annotations

import json

import pytest

import w2_149_setup_a as sa
import w2_149_support as support
from w2_149_support import assert_refused

bwrap = pytest.mark.bwrap
LISTING_R2 = ["actions.jsonl", "cases.jsonl", "half.json", "round1/label_rules.py", "round1/rulebook.md", "sample.json",
              "script-labels.jsonl"]


def round1(world, half, rules):
    run = sa.deliver(world, "labeller", half, round_=1, out=sa.labeller_r1_out(rules))
    assert run.code == 0, run.why()
    return run


def round2_dry(world, half, env=None):
    support.next_second()
    return world.launch(*sa.args(world, "labeller", half, round_=2, seed=5150, dry=True), env=sa.rules_env(**(env or {})),
                        timeout=300)


def nothing_staged(world, line):
    """No script output and no sample, in a wall left in place or in its packed tar."""
    if not (line and line.get("run")):
        return
    wall = world.wall(line)
    for name in ("script-labels.jsonl", "sample.json"):
        assert not (wall / "input" / name).exists(), f"input/{name} was staged"
    if world.tar(line).exists():
        names = world.tar_names(line)
        assert not any(n.endswith(("input/script-labels.jsonl", "input/sample.json")) for n in names), names


def tar_jsonl(world, line, suffix):
    data = world.tar_member(line, suffix)
    assert data is not None, f"no {suffix} in the packed wall"
    return [json.loads(x) for x in data.decode().splitlines() if x.strip()]


def changes(before, after):
    return {k for k in set(before) | set(after) if before.get(k) != after.get(k)}


# -- S25 ------------------------------------------------------------------------------------------------------------

def test_s25_no_bwrap_refuses_18(world):
    """The program GOV_INDEP_BWRAP names does not exist: the rule script cannot run confined, so it does not run."""
    sa.plant_half(world, "tuning")
    round1(world, "tuning", sa.RULES_GOOD)
    calls = len(world.calls())
    run = round2_dry(world, "tuning", env={"GOV_INDEP_BWRAP": str(world.tmp / "no-such-bwrap")})
    assert_refused(world, run, 18)
    nothing_staged(world, run.line)
    assert len(world.calls()) == calls, "claude was started"


@bwrap
def test_s25_the_good_rule_script_s_labels_and_the_sample_are_staged(world):
    sa.plant_half(world, "held-out")
    round1(world, "held-out", sa.RULES_GOOD)
    run = round2_dry(world, "held-out")
    assert run.code == 0, run.why()
    wall = world.wall(run.line)
    assert sa.input_listing(wall) == LISTING_R2
    kept = world.half("held-out") / "labels/r1-sgx1-labeller"
    for name in ("rulebook.md", "label_rules.py"):
        assert (wall / "input/round1" / name).read_bytes() == (kept / name).read_bytes()
    assert (kept / "label_rules.py").read_text() == sa.RULES_GOOD
    actions, cases = sa.staged(world, "held-out")
    lines = actions + cases
    assert sa.read_jsonl(wall / "input/actions.jsonl") == actions
    assert sa.read_jsonl(wall / "input/cases.jsonl") == cases
    assert sa.read_jsonl(wall / "input/script-labels.jsonl") == sa.good_rules(lines)
    sample = sa.labeller_sample("5150", [x["id"] for x in lines])
    assert sample, "premise: the planted half's sample at seed 5150 is not empty"
    assert json.loads((wall / "input/sample.json").read_text()) == {"ids": sample}


BAD = ("reads-a-file", "opens-a-socket", "starts-a-process", "loops-past-the-cap", "leaves-out-an-id")


@bwrap
@pytest.mark.parametrize("how", BAD)
def test_s25_a_rule_script_that_breaks_its_confinement_refuses_18(world, how):
    """Each planted script would pass, with its marker inside its labels, if it ran unconfined; confined, its read,
    socket or process fails (or the cap stops it, or an id is missing) and the launch refuses 18, nothing staged."""
    sa.plant_half(world, "tuning")
    listener, marker = None, None
    if how == "reads-a-file":
        outside = world.tmp / "outside" / "note.txt"
        support.write_file(outside.parent, outside.name, sa.MARK_FILE + "\n")
        rules, marker = sa.rules_reading(outside), sa.MARK_FILE
    elif how == "opens-a-socket":
        listener = sa.Listener(sa.MARK_SOCKET)
        rules, marker = sa.rules_socket(listener.port), sa.MARK_SOCKET
    elif how == "starts-a-process":
        rules, marker = sa.rules_process(), sa.MARK_PROCESS
    elif how == "loops-past-the-cap":
        rules = sa.RULES_LOOP
    else:
        rules = sa.RULES_DROPS_AN_ID
    try:
        round1(world, "tuning", rules)
        calls = len(world.calls())
        run = round2_dry(world, "tuning")
    finally:
        if listener:
            listener.close()
    assert_refused(world, run, 18)
    nothing_staged(world, run.line)
    assert len(world.calls()) == calls, "claude was started"
    if listener:
        assert listener.connections == 0, "the rule script reached the listener"
    if marker:
        assert marker not in run.out and marker not in run.err, "the marker reached the printed output"
        hits = sa.files_holding([world.sr, world.runs_root, world.trees], marker)
        assert hits == [], f"the marker reached {hits}"


# -- S26 ------------------------------------------------------------------------------------------------------------

@bwrap
def test_s26_a_hand_file_missing_a_required_id_is_rejected_20(world):
    sa.plant_half(world, "tuning")
    round1(world, "tuning", sa.RULES_GOOD)
    sr0, exp0 = world.hashes(world.sr), world.hashes(world.exp)
    run = sa.deliver(world, "labeller", "tuning", round_=2, program="hand_labels", program_args={"drop": 0})
    assert run.code == 20, run.why()
    assert run.line["status"] == "rejected" and run.line["reason"] == "result", run.line
    assert not (world.half("tuning") / "labels/labels.jsonl").exists()
    assert world.hashes(world.exp) == exp0, "the half's folder changed"
    assert changes(sr0, world.hashes(world.sr)) <= {f"indep-walls/labeller/{run.line['run']}.tar"}


@bwrap
def test_s26_a_complete_hand_file_merges_hand_over_script(world):
    """Every required id (uncertain, classes 1-13, the sample) hand-labelled, and two more: labels.jsonl is one line
    per staged id, in the staged order, the hand label over the script's (S26); it alone lands (S16)."""
    sa.plant_half(world, "held-out")
    round1(world, "held-out", sa.RULES_GOOD)
    sr0, exp0 = world.hashes(world.sr), world.hashes(world.exp)
    run = sa.deliver(world, "labeller", "held-out", round_=2, program="hand_labels", program_args={"extra": 2})
    assert run.code == 0, run.why()
    line = run.line
    actions, cases = sa.staged(world, "held-out")
    lines = actions + cases
    script = sa.good_rules(lines)
    assert tar_jsonl(world, line, "input/script-labels.jsonl") == script
    seed = sa.seed_of(world, line["run"])
    sample = set(sa.labeller_sample(str(seed), [x["id"] for x in lines]))
    need = {x["id"] for x in script if x["uncertain"] or 1 <= x["rule_class"] <= 13 or x["id"] in sample}
    hand = {x["id"]: x for x in tar_jsonl(world, line, "out/hand-labels.jsonl")}
    assert need <= set(hand) and len(hand) == len(need) + 2, "premise: the stub's hand file"
    want = []
    for x in script:
        h = hand.get(x["id"])
        src, how = (h, "hand") if h else (dict(x, reason=""), "script")
        want.append({k: src[k] for k in sa.MERGED[:-1]} | {"how": how})
    dest = world.half("held-out") / "labels/labels.jsonl"
    assert sa.read_jsonl(dest) == want
    assert changes(sr0, world.hashes(world.sr)) == {f"{support.SEALED}/labels/labels.jsonl",
                                                    f"indep-walls/labeller/{line['run']}.tar"}
    assert world.hashes(world.exp) == exp0
    d = line["delivered"]
    assert d["files"] == 1 and d["to"] == "labels" and d["sha256"] == support.sha_file(dest), d
    sa.assert_counts(world, line, json.loads(world.tar_member(line, "out/result.json")))
