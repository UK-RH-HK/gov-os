"""The wiring review's F18-F23, fixed before the owner is asked (DEC-1112 (3), the CTO's decision): S25 changed (the
rule script's confined check also at labeller 1's round-1 delivery, F18), S27 changed (the disputes' reasons blinded,
F21; a settled line takes the auditor's decision, F22), S29 (a result that says it stopped delivers nothing, F19), S30
(labeller 2's labels checked before they land, F20), S31 (``rule_class`` a JSON integer or a decimal string 1-14,
stored as an integer, F23).

Written from the ticket's KPI lines and the five approved briefs' output and result sections; the interface is this
folder's README ("Set-up A's wiring: the interface"). The cases whose launch runs the first labeller's rule script
confined carry the marker ``bwrap`` (run by the CTO outside the launch sandbox with ``GOV_W2_149_BWRAP=1``).
"""

from __future__ import annotations

import json
import os

import pytest

import w2_149_setup_a as sa
import w2_149_support as support
from w2_149_support import assert_refused

bwrap = pytest.mark.bwrap
R1_DIR = "labels/r1-sgx1-labeller"


def changes(before, after):
    return {k for k in set(before) | set(after) if before.get(k) != after.get(k)}


def tar_jsonl(world, line, suffix):
    data = world.tar_member(line, suffix)
    assert data is not None, f"no {suffix} in the packed wall"
    return [json.loads(x) for x in data.decode().splitlines() if x.strip()]


def rejected(run):
    assert run.code == 20, run.why()
    assert run.line["status"] == "rejected" and run.line["reason"] == "result", run.line


def no_files(folder):
    return not folder.exists() or not any(p.is_file() for p in folder.rglob("*"))


def all_int(lines):
    """Every rule_class a JSON integer (never a string, a float or a boolean)."""
    return all(type(x["rule_class"]) is int for x in lines)


def round1(world, half, rules, env=None):
    return sa.deliver(world, "labeller", half, round_=1, out=sa.labeller_r1_out(rules), env=env)


def round2_dry(world, half):
    support.next_second()
    return world.launch(*sa.args(world, "labeller", half, round_=2, seed=5150, dry=True), env=sa.rules_env(),
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


def labeller2_round1(world):
    """The tuning half (200 actions, so a drawn seed's 10 % overlap is never empty) and labeller 2's round 1."""
    sa.plant_half(world, "tuning", n_actions=200)
    r1 = sa.deliver(world, "labeller-2", "tuning", round_=1, out=sa.labeller2_r1_out())
    assert r1.code == 0, r1.why()


# -- S25 (F18): the rule script's check at round 1's delivery ----------------------------------------------------------

@bwrap
@pytest.mark.parametrize("how", ["leaves-out-an-id", "reads-a-file"])
def test_s25_round_1_s_delivery_runs_the_rule_script_confined_and_a_failing_one_lands_nothing(world, how):
    """Round 1's out/label_rules.py runs under the same confined check over the half's staged lines: a script that
    leaves out an id, or reads a planted marker file outside it, is rejected 20 with nothing in r1-sgx1-labeller/ and
    the marker nowhere; a good script then delivers both files."""
    sa.plant_half(world, "held-out")
    keep = world.half("held-out") / R1_DIR
    marker = None
    if how == "reads-a-file":
        path = world.tmp / "outside" / "note.txt"
        support.write_file(path.parent, path.name, sa.MARK_FILE + "\n")
        rules, marker = sa.rules_reading(path), sa.MARK_FILE
    else:
        rules = sa.RULES_DROPS_AN_ID
    sr0, exp0 = world.hashes(world.sr), world.hashes(world.exp)
    run = round1(world, "held-out", rules)
    rejected(run)
    assert no_files(keep), f"a failing rule script landed: {sorted(os.listdir(keep))}"
    assert changes(sr0, world.hashes(world.sr)) <= {f"indep-walls/labeller/{run.line['run']}.tar"}
    assert world.hashes(world.exp) == exp0
    if marker:
        assert marker not in run.out and marker not in run.err, "the marker reached the printed output"
        hits = sa.files_holding([world.sr, world.runs_root, world.trees], marker)
        assert hits == [], f"the marker reached {hits}"
    good = round1(world, "held-out", sa.RULES_GOOD)
    assert good.code == 0, good.why()
    assert sorted(os.listdir(keep)) == ["label_rules.py", "rulebook.md"]
    assert (keep / "label_rules.py").read_text() == sa.RULES_GOOD


def test_s25_no_bwrap_at_round_1_s_delivery_rejects_20_and_lands_nothing(world):
    """The program GOV_INDEP_BWRAP names does not exist: round 1's check cannot run confined, so the script is neither
    run unconfined nor passed unchecked (failure line 11): rejected 20, nothing lands. Needs no bwrap."""
    sa.plant_half(world, "tuning")
    sr0, exp0 = world.hashes(world.sr), world.hashes(world.exp)
    run = round1(world, "tuning", sa.RULES_GOOD, env={"GOV_INDEP_BWRAP": str(world.tmp / "no-such-bwrap")})
    rejected(run)
    assert no_files(world.half("tuning") / R1_DIR), "round 1 landed without its check"
    assert world.hashes(world.exp) == exp0
    assert changes(sr0, world.hashes(world.sr)) <= {f"indep-walls/labeller/{run.line['run']}.tar"}


# -- S29 (F19): a result that says it stopped delivers nothing -------------------------------------------------------

STOP_CASES = ["writer-tuning", "writer-heldout", pytest.param("labeller-r1", marks=bwrap), "labeller-2-r1",
              "labeller-2-r2", pytest.param("labeller-r2", marks=bwrap), "overlap-auditor"]


@pytest.mark.parametrize("case", STOP_CASES)
def test_s29_a_result_that_says_it_stopped_delivers_nothing(world, case):
    """A valid result.json whose stopped is a word other than none, the flow's out/ products present: rejected 20,
    out.stopped the word, every destination unchanged (the sets root and the experiment folder hashed), the products
    (and conflicts.md) in the wall's tar only."""
    word = sa.STOP_WORD[case]
    flow = case.rsplit("-r", 1)[0]
    audits = (world.runs / "AUDITS.log").read_bytes()
    out = {}
    if case.startswith("writer"):
        half = "tuning" if case == "writer-tuning" else "held-out"
        out = sa.stopped_out(sa.writer_out(case), word)
        products = ["cases.jsonl", "aims.jsonl", "conflicts.md"]
        sr0, exp0 = world.hashes(world.sr), world.hashes(world.exp)
        run = sa.deliver(world, case, half, out=out)
    else:
        half = "held-out" if case in ("labeller-r1", "labeller-r2") else "tuning"
        sa.plant_half(world, half, n_actions=48, n_cases=12)
        if case == "labeller-r2":
            assert round1(world, half, sa.RULES_GOOD).code == 0
        if case == "labeller-2-r2":
            assert sa.deliver(world, "labeller-2", half, round_=1, out=sa.labeller2_r1_out()).code == 0
        if case == "overlap-auditor":
            sa.plant_labels(world, half)
        sr0, exp0 = world.hashes(world.sr), world.hashes(world.exp)
        stop = {"extra_result": {"stopped": word}}
        if case == "labeller-r1":
            out = sa.stopped_out(sa.labeller_r1_out(), word)
            products = ["rulebook.md", "label_rules.py", "conflicts.md"]
            run = sa.deliver(world, "labeller", half, round_=1, out=out)
        elif case == "labeller-2-r1":
            out = sa.stopped_out(sa.labeller2_r1_out(), word)
            products = ["rulebook-2.md", "conflicts.md"]
            run = sa.deliver(world, "labeller-2", half, round_=1, out=out)
        elif case == "labeller-r2":
            products = ["hand-labels.jsonl", "conflicts.md"]
            run = sa.deliver(world, "labeller", half, round_=2, out={"conflicts.md": sa.CONFLICTS},
                             program="hand_labels", program_args=stop)
        elif case == "labeller-2-r2":
            products = ["labels-2.jsonl", "conflicts.md"]
            run = sa.deliver(world, "labeller-2", half, round_=2, out={"conflicts.md": sa.CONFLICTS},
                             program="labels2", program_args=stop)
        else:
            products = ["decisions.jsonl", "conflicts.md"]
            run = sa.deliver(world, "overlap-auditor", half, out={"conflicts.md": sa.CONFLICTS}, program="decide",
                             program_args=stop)
    rejected(run)
    line = run.line
    assert line["out"].get("schema_ok") is True and line["out"].get("stopped") == word, line["out"]
    tar = f"indep-walls/{sa.FLOW[flow][0]}/{line['run']}.tar"
    assert changes(sr0, world.hashes(world.sr)) == {tar}, "a destination under the sets root changed"
    assert changes(exp0, world.hashes(world.exp)) == set(), "a destination under the experiment folder changed"
    for name in products:
        data = world.tar_member(line, f"out/{name}")
        assert data, f"out/{name} is not in the wall's tar"
        if name in out:
            assert data == out[name].encode(), name
        hits = sa.files_holding([world.sr, world.runs_root, world.trees], data.decode(), skip=[world.tar(line)])
        assert hits == [], f"out/{name} outside the wall's tar: {hits}"
    assert (world.runs / "AUDITS.log").read_bytes() == audits


# -- S30 (F20): labeller 2's labels checked before they land ---------------------------------------------------------

@pytest.mark.parametrize("bad", ["missing", "extra", "repeat", "label", "how", "clauses"])
def test_s30_labeller_2_s_labels_out_of_rule_are_rejected_20(world, bad):
    """A sample id left out, an id not in the sample, an id twice, a label off the list, how not hand, clauses not a
    list: rejected 20, labels-2.jsonl not written, nothing else changed."""
    labeller2_round1(world)
    dest = world.half("tuning") / "labels/labels-2.jsonl"
    sr0, exp0 = world.hashes(world.sr), world.hashes(world.exp)
    run = sa.deliver(world, "labeller-2", "tuning", round_=2, program="labels2", program_args={"bad": bad})
    rejected(run)
    assert not dest.exists(), "labels-2.jsonl landed"
    assert world.hashes(world.exp) == exp0, "the half's folder changed"
    assert changes(sr0, world.hashes(world.sr)) <= {f"indep-walls/labeller/{run.line['run']}.tar"}


def test_s30_a_good_labels_2_file_lands_with_rule_class_an_integer(world):
    """One valid line per staged sample id, rule_class written as decimal strings: delivered, its lines as the
    session wrote them with rule_class an integer."""
    labeller2_round1(world)
    dest = world.half("tuning") / "labels/labels-2.jsonl"
    run = sa.deliver(world, "labeller-2", "tuning", round_=2, program="labels2", program_args={"class_form": "str"})
    assert run.code == 0, run.why()
    line = run.line
    wrote = tar_jsonl(world, line, "out/labels-2.jsonl")
    assert wrote and all(isinstance(x["rule_class"], str) for x in wrote), "premise: the session wrote strings"
    got = sa.read_jsonl(dest)
    assert got == [dict(x, rule_class=int(x["rule_class"])) for x in wrote]
    assert all_int(got), "a rule_class landed that is not an integer"
    actions, cases = sa.staged(world, "tuning")
    assert [x["id"] for x in got] == [x["id"] for x in sa.overlap(str(sa.seed_of(world, line["run"])), actions + cases)]
    d = line["delivered"]
    assert d["files"] == 1 and d["to"] == "labels" and d["sha256"] == support.sha_file(dest), d


# -- S27 (F21): the disputes' reasons blinded --------------------------------------------------------------------------

def test_s27_an_empty_reason_on_either_side_blanks_both_and_two_reasons_are_kept(world):
    """Labeller 1's script labels carry reason "" and labeller 2 leaves three reasons empty: in input/disputes.jsonl
    such a case has both reasons "", so no side is told apart by it; a case where both have a reason keeps both."""
    sa.plant_half(world, "tuning", n_actions=48, n_cases=12)
    planted = sa.plant_labels(world, "tuning")
    ids_run = sorted(planted["undecided"])[:40]
    one = {x["id"]: x for x in planted["lines1"]}
    blank2 = set([i for i in ids_run if one[i]["reason"]][:3])
    planted["lines2"] = [dict(x, reason="") if x["id"] in blank2 else x for x in planted["lines2"]]
    support.write_file(world.half("tuning"), "labels/labels-2.jsonl", sa.jsonl(planted["lines2"]))
    two = {x["id"]: x for x in planted["lines2"]}
    script_side = [i for i in ids_run if one[i]["reason"] == ""]
    both = [i for i in ids_run if one[i]["reason"] and two[i]["reason"]]
    assert script_side and len(blank2) == 3 and both, "premise: each kind of case is in the run"
    run = sa.dry(world, "overlap-auditor", "tuning", seed=5150)
    assert run.code == 0, run.why()
    rows = sa.read_jsonl(world.wall(run.line) / "input/disputes.jsonl")
    got = {x["id"]: x for x in rows}
    for i in script_side + sorted(blank2):
        assert got[i]["x"]["reason"] == "" and got[i]["y"]["reason"] == "", ("a reason tells the sides apart", got[i])
    order = sa.xy(5150, ids_run)
    for i in both:
        side = {1: one[i], 2: two[i]}
        a, b = order[i]
        assert (got[i]["x"]["reason"], got[i]["y"]["reason"]) == (side[a]["reason"], side[b]["reason"]), got[i]
    assert rows == sa.expected_disputes(world, "tuning", planted, 5150, ids_run)


# -- S31 (F23): rule_class an integer or a decimal string 1-14, stored as an integer ----------------------------------

FORMS = sorted(sa.BAD_CLASS)


@bwrap
def test_s31_the_rule_script_s_string_rule_class_is_accepted_and_staged_as_an_integer(world):
    """A rule script writing every rule_class as "1".."14" passes round 1's check (delivered) and round 2's;
    input/script-labels.jsonl carries each as an integer."""
    sa.plant_half(world, "held-out")
    r1 = round1(world, "held-out", sa.rules_forms("str"))
    assert r1.code == 0, r1.why()
    run = round2_dry(world, "held-out")
    assert run.code == 0, run.why()
    actions, cases = sa.staged(world, "held-out")
    got = sa.read_jsonl(world.wall(run.line) / "input/script-labels.jsonl")
    assert got == sa.good_rules(actions + cases) and all_int(got), "script-labels.jsonl is not the labels as integers"


@bwrap
@pytest.mark.parametrize("form", FORMS)
def test_s31_a_bad_rule_class_from_the_rule_script_rejects_round_1_20_and_refuses_round_2_18(world, form):
    """One line's rule_class in a refused form: at round 1's delivery rejected 20, nothing lands; a script whose bad
    form appears only on the trigger line is delivered, and at round 2 (the trigger added) refuses 18, nothing
    staged, no session."""
    bad = sa.BAD_CLASS[form]
    sa.plant_half(world, "tuning")
    keep = world.half("tuning") / R1_DIR
    run = round1(world, "tuning", sa.rules_forms("str", bad=bad, bad_on="first"))
    rejected(run)
    assert no_files(keep), "a rule script giving a bad rule_class landed"
    r1 = round1(world, "tuning", sa.rules_forms("str", bad=bad, bad_on="trigger"))
    assert r1.code == 0, r1.why()
    sa.plant_trigger(world, "tuning")
    calls = len(world.calls())
    r2 = round2_dry(world, "tuning")
    assert_refused(world, r2, 18)
    nothing_staged(world, r2.line)
    assert len(world.calls()) == calls, "claude was started"


@bwrap
@pytest.mark.parametrize("form", FORMS)
def test_s31_hand_labels_take_rule_class_as_an_integer_or_a_decimal_string(world, form):
    """Labeller 1's round 2: a hand file with one rule_class in a refused form is rejected 20 (labels.jsonl not
    written); the same file with every rule_class a decimal string is delivered, labels.jsonl carrying integers."""
    sa.plant_half(world, "held-out")
    assert round1(world, "held-out", sa.RULES_GOOD).code == 0
    dest = world.half("held-out") / "labels/labels.jsonl"
    bad = sa.deliver(world, "labeller", "held-out", round_=2, program="hand_labels",
                     program_args={"class_form": "str", "bad_class": sa.BAD_CLASS[form]})
    rejected(bad)
    assert not dest.exists(), "labels.jsonl landed"
    run = sa.deliver(world, "labeller", "held-out", round_=2, program="hand_labels", program_args={"class_form": "str"})
    assert run.code == 0, run.why()
    hand = tar_jsonl(world, run.line, "out/hand-labels.jsonl")
    assert hand and all(isinstance(x["rule_class"], str) for x in hand), "premise: the session wrote strings"
    got = sa.read_jsonl(dest)
    by = {x["id"]: x for x in got}
    for h in hand:
        assert by[h["id"]] == dict(h, rule_class=int(h["rule_class"]), how="hand"), by[h["id"]]
    assert all_int(got), "a rule_class landed that is not an integer"


@pytest.mark.parametrize("form", FORMS)
def test_s31_labeller_2_s_labels_take_rule_class_as_an_integer_or_a_decimal_string(world, form):
    """Labeller 2's round 2: one rule_class in a refused form, rejected 20 (labels-2.jsonl not written); every
    rule_class a decimal string, delivered with integers."""
    labeller2_round1(world)
    dest = world.half("tuning") / "labels/labels-2.jsonl"
    bad = sa.deliver(world, "labeller-2", "tuning", round_=2, program="labels2",
                     program_args={"class_form": "str", "bad_class": sa.BAD_CLASS[form]})
    rejected(bad)
    assert not dest.exists(), "labels-2.jsonl landed"
    run = sa.deliver(world, "labeller-2", "tuning", round_=2, program="labels2", program_args={"class_form": "str"})
    assert run.code == 0, run.why()
    wrote = tar_jsonl(world, run.line, "out/labels-2.jsonl")
    got = sa.read_jsonl(dest)
    assert got == [dict(x, rule_class=int(x["rule_class"])) for x in wrote] and all_int(got)


@pytest.mark.parametrize("form", FORMS)
def test_s31_the_auditor_s_decisions_take_rule_class_as_an_integer_or_a_decimal_string(world, form):
    """The overlap auditor: one decision's rule_class in a refused form, rejected 20 (the half's folder unchanged);
    every rule_class a decimal string, delivered: the decisions file and labels.jsonl carry integers, each settled
    line the auditor's decision (S27, F22)."""
    sa.plant_half(world, "tuning", n_actions=48, n_cases=12)
    planted = sa.plant_labels(world, "tuning")
    h = world.half("tuning")
    h0 = world.hashes(h)
    bad = sa.deliver(world, "overlap-auditor", "tuning", program="decide",
                     program_args={"class_form": "str", "bad_class": sa.BAD_CLASS[form]})
    rejected(bad)
    assert world.hashes(h) == h0, "the half's folder changed"
    run = sa.deliver(world, "overlap-auditor", "tuning", program="decide", program_args={"class_form": "str"})
    assert run.code == 0, run.why()
    rid = run.line["run"]
    ids_run = sorted(planted["undecided"])[:40]
    order = sa.xy(sa.seed_of(world, rid), ids_run)
    decisions = tar_jsonl(world, run.line, "out/decisions.jsonl")
    assert [d["id"] for d in decisions] == ids_run
    assert all(isinstance(d["rule_class"], str) for d in decisions), "premise: the session wrote strings"
    delivered = sa.read_jsonl(h / f"labels/audit/{rid}.decisions.jsonl")
    assert delivered == sa.mapped_back(decisions, order) and all_int(delivered)
    got = sa.read_jsonl(h / "labels/labels.jsonl")
    by = {x["id"]: x for x in got}
    for d in decisions:
        if d["flag"] == "none":
            assert by[d["id"]] == sa.settled_line(d), (by[d["id"]], d)
    assert all_int(got), "a rule_class in labels.jsonl that is not an integer"
