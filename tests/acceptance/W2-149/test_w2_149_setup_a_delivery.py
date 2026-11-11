"""S16 (set-up A's deliveries land only where the flow delivers), S28 (set-up A's results are counts in their own
schemas). DEC-1112 (3), DEC-1113.

Each delivery hashes the planted sets root and the planted experiment folder (``<runs>/SANDBOX-GUARD-EXP-1``) before
and after: the flow's destination and the packed wall are the only changes. The first labeller's round 2 and the
overlap auditor are in ``test_w2_149_setup_a_rules.py`` and ``test_w2_149_setup_a_audit.py``.
"""

from __future__ import annotations

import json
import os

import pytest

import w2_149_setup_a as sa
import w2_149_support as support

MARK = "MARK-W2149-S28-free-text"


def changes(before, after):
    return {k for k in set(before) | set(after) if before.get(k) != after.get(k)}


def rel_in(world, half, path):
    """A destination's path relative to the root it is hashed under (the experiment folder or the sets root)."""
    return os.path.relpath(path, world.exp if half == "tuning" else world.sr)


def expect_changes(world, half, sr0, exp0, landed, tar):
    if half == "tuning":
        assert changes(sr0, world.hashes(world.sr)) == {tar}
        assert changes(exp0, world.hashes(world.exp)) == landed
    else:
        assert changes(sr0, world.hashes(world.sr)) == {tar} | landed
        assert changes(exp0, world.hashes(world.exp)) == set()


# -- S16 ------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("flow", ["writer-tuning", "writer-heldout"])
def test_s16_set_up_a_writers_deliver_their_cases_to_the_half_s_planted_folder(world, flow):
    half = "tuning" if flow == "writer-tuning" else "held-out"
    sr0, exp0 = world.hashes(world.sr), world.hashes(world.exp)
    out = sa.writer_out(flow)
    run = sa.deliver(world, flow, half, out=out)
    assert run.code == 0, run.why()
    line = run.line
    dest = world.half(half) / "planted/cases.jsonl"
    assert dest.read_text() == out["cases.jsonl"]
    expect_changes(world, half, sr0, exp0, {rel_in(world, half, dest)}, f"indep-walls/writer/{line['run']}.tar")
    assert world.tar_member(line, "out/aims.jsonl") == out["aims.jsonl"].encode(), "aims.jsonl is not in the tar"
    hits = sa.files_holding([world.sr, world.runs_root, world.trees], sa.AIMS_MARK, skip=[world.tar(line)])
    assert hits == [], f"the aims outside the wall's tar: {hits}"
    d = line["delivered"]
    assert d["files"] == 1 and d["to"] == "cases" and d["sha256"] == support.sha256(out["cases.jsonl"].encode()), d
    sa.assert_counts(world, line, sa.RESULT[flow])


@pytest.mark.parametrize("flow,half", [pytest.param("labeller", "held-out", marks=pytest.mark.bwrap),
                                       ("labeller-2", "tuning")])
def test_s16_each_labeller_s_round_1_keeps_its_files_in_the_half_s_round_1_folder(world, flow, half):
    """(labeller 1's param is ``bwrap`` since S25's F18 change: its delivery runs the rule script confined.)"""
    sa.plant_half(world, half)
    sr0, exp0 = world.hashes(world.sr), world.hashes(world.exp)
    out = sa.labeller_r1_out() if flow == "labeller" else sa.labeller2_r1_out()
    run = sa.deliver(world, flow, half, round_=1, out=out)
    assert run.code == 0, run.why()
    line = run.line
    keep = world.half(half) / f"labels/r1-{sa.FLOW[flow][2]}"
    files = {n: t.encode() for n, t in out.items() if n != "result.json"}
    assert sorted(os.listdir(keep)) == sorted(files)
    for name, data in files.items():
        assert (keep / name).read_bytes() == data, name
    expect_changes(world, half, sr0, exp0, {rel_in(world, half, keep / n) for n in files},
                   f"indep-walls/labeller/{line['run']}.tar")
    d = line["delivered"]
    want = sa.manifest_sha(files) if len(files) > 1 else support.sha256(next(iter(files.values())))
    assert d["files"] == len(files) and d["to"] == "round1" and d["sha256"] == want, d
    sa.assert_counts(world, line, json.loads(out["result.json"]))


def test_s16_labeller_2_s_round_2_delivers_its_labels_to_labels_2_jsonl(world):
    sa.plant_half(world, "tuning")
    r1 = sa.deliver(world, "labeller-2", "tuning", round_=1, out=sa.labeller2_r1_out())
    assert r1.code == 0, r1.why()
    sr0, exp0 = world.hashes(world.sr), world.hashes(world.exp)
    run = sa.deliver(world, "labeller-2", "tuning", round_=2, program="labels2")
    assert run.code == 0, run.why()
    line = run.line
    dest = world.half("tuning") / "labels/labels-2.jsonl"
    wrote = [json.loads(x) for x in world.tar_member(line, "out/labels-2.jsonl").decode().splitlines() if x.strip()]
    assert sa.read_jsonl(dest) == [dict(x, rule_class=int(x["rule_class"])) for x in wrote], \
        "labels-2.jsonl is not the session's lines with rule_class an integer (S30, S31)"
    actions, cases = sa.staged(world, "tuning")
    want_ids = [x["id"] for x in sa.overlap(str(sa.seed_of(world, line["run"])), actions + cases)]
    assert [x["id"] for x in sa.read_jsonl(dest)] == want_ids, "labels-2.jsonl is not the wall's overlap (S20)"
    expect_changes(world, "tuning", sr0, exp0, {rel_in(world, "tuning", dest)}, f"indep-walls/labeller/{line['run']}.tar")
    d = line["delivered"]
    assert d["files"] == 1 and d["to"] == "labels" and d["sha256"] == support.sha_file(dest), d
    sa.assert_counts(world, line, json.loads(world.tar_member(line, "out/result.json")))


@pytest.mark.parametrize("flow", ["writer-tuning", "labeller-2"])
def test_s16_an_existing_set_up_a_destination_refuses_20(world, flow):
    h = world.half("tuning")
    if flow == "writer-tuning":
        support.write_file(h, "planted/cases.jsonl", "planted earlier\n")
        sr0, exp0 = world.hashes(world.sr), world.hashes(world.exp)
        run = sa.deliver(world, flow, "tuning", out=sa.writer_out(flow))
    else:
        sa.plant_half(world, "tuning")
        r1 = sa.deliver(world, flow, "tuning", round_=1, out=sa.labeller2_r1_out())
        assert r1.code == 0, r1.why()
        support.write_file(h, "labels/labels-2.jsonl", "planted earlier\n")
        sr0, exp0 = world.hashes(world.sr), world.hashes(world.exp)
        run = sa.deliver(world, flow, "tuning", round_=2, program="labels2")
    assert run.code == 20, run.why()
    assert run.line["status"] == "rejected" and run.line["reason"] == "result", run.line
    assert world.hashes(world.exp) == exp0, "the half's folder changed"
    assert changes(sr0, world.hashes(world.sr)) <= {f"indep-walls/{sa.FLOW[flow][0]}/{run.line['run']}.tar"}


def test_s16_a_set_up_a_delivery_is_all_or_nothing(world):
    """Round 1's two files: label_rules.py's destination exists, so rulebook.md must not land either."""
    sa.plant_half(world, "held-out")
    support.write_file(world.half("held-out"), "labels/r1-sgx1-labeller/label_rules.py", "# planted earlier\n")
    sr0, exp0 = world.hashes(world.sr), world.hashes(world.exp)
    run = sa.deliver(world, "labeller", "held-out", round_=1, out=sa.labeller_r1_out())
    assert run.code == 20, run.why()
    assert not (world.half("held-out") / "labels/r1-sgx1-labeller/rulebook.md").exists(), "a partial delivery"
    assert changes(sr0, world.hashes(world.sr)) <= {f"indep-walls/labeller/{run.line['run']}.tar"}
    assert world.hashes(world.exp) == exp0


# -- S28 ------------------------------------------------------------------------------------------------------------

L1_R2 = {"round": 2, "hand_labelled": 3, "allow": 1, "refuse": 1, "ask": 1, "by_class": sa.by14(lambda c: 1 if c in (1, 7, 14) else 0),
         "uncertain_seen": 2, "sample": 1, "instructions_ignored": 0, "stopped": "none"}
L2_R2 = {"round": 2, "sample": 3, "labelled": 3, "allow": 1, "refuse": 1, "ask": 1,
         "by_class": sa.by14(lambda c: 1 if c in (1, 7, 14) else 0), "instructions_ignored": 0, "stopped": "none"}
AUDIT = {"cases": 3, "decided": 3, "allow": 1, "refuse": 1, "ask": 1, "agrees_x": 1, "agrees_y": 1, "neither": 1,
         "cannot_settle": 0, "may_change_verdict": 1, "by_class": sa.by14(lambda c: 1 if c in (1, 7, 14) else 0),
         "instructions_ignored": 0, "stopped": "none"}
FORMS = {"writer-tuning": [sa.RESULT["writer-tuning"]],
         "writer-heldout": [sa.RESULT["writer-heldout"], dict(sa.RESULT["writer-heldout"], stopped="not-sealed")],
         "labeller": [sa.RESULT["labeller-r1"], L1_R2],
         "labeller-2": [sa.RESULT["labeller-2-r1"], L2_R2],
         "overlap-auditor": [AUDIT]}


@pytest.mark.parametrize("flow", sorted(sa.FLOW))
def test_s28_each_flow_s_result_schema_is_closed_and_takes_the_brief_s_forms(flow):
    path = support.SCHEMAS / sa.SCHEMA[flow]
    assert path.is_file(), f"indep-schemas/{sa.SCHEMA[flow]} does not exist yet"
    schema = json.loads(path.read_text())
    assert support.schema_holes(schema) == [], support.schema_holes(schema)
    for form in FORMS[flow]:
        assert support.validate(schema, form) == [], (form, support.validate(schema, form))
        assert support.validate(schema, dict(form, note=MARK)) != [], "an extra free-text field passed"
        assert support.validate(schema, dict(form, stopped="some-other-word")) != [], "a stopped word off the list passed"
        for key, value in form.items():
            if isinstance(value, dict):
                assert support.validate(schema, dict(form, **{key: dict(value, **{"15": 1})})) != [], key
            elif isinstance(value, int) and not isinstance(value, bool) and key != "round":
                assert support.validate(schema, dict(form, **{key: MARK})) != [], f"text accepted for {key}"
    if flow == "writer-tuning":
        assert support.validate(schema, dict(FORMS[flow][0], stopped="not-sealed")) != [], "writer 1 cannot be not-sealed"


EXTRA = ["writer-tuning", "writer-heldout", "labeller-r1", "labeller-2-r1", "labeller-2-r2", "overlap-auditor",
         pytest.param("labeller-r2", marks=pytest.mark.bwrap)]


@pytest.mark.parametrize("case", EXTRA)
def test_s28_an_extra_free_text_field_is_refused_20_without_a_trace(world, case):
    note = {"note": MARK}
    if case.startswith("writer"):
        half = "tuning" if case == "writer-tuning" else "held-out"
        sr0, exp0 = world.hashes(world.sr), world.hashes(world.exp)
        run = sa.deliver(world, case, half, out=sa.writer_out(case, **note))
    else:
        half = "held-out" if case in ("labeller-r1", "labeller-r2") else "tuning"
        sa.plant_half(world, half, n_actions=48, n_cases=12)
        if case == "labeller-r2":
            assert sa.deliver(world, "labeller", half, round_=1, out=sa.labeller_r1_out()).code == 0
        if case == "labeller-2-r2":
            assert sa.deliver(world, "labeller-2", half, round_=1, out=sa.labeller2_r1_out()).code == 0
        if case == "overlap-auditor":
            sa.plant_labels(world, half)
        sr0, exp0 = world.hashes(world.sr), world.hashes(world.exp)
        if case == "labeller-r1":
            run = sa.deliver(world, "labeller", half, round_=1, out=sa.labeller_r1_out(**note))
        elif case == "labeller-2-r1":
            run = sa.deliver(world, "labeller-2", half, round_=1, out=sa.labeller2_r1_out(**note))
        elif case == "labeller-r2":
            run = sa.deliver(world, "labeller", half, round_=2, program="hand_labels",
                             program_args={"extra_result": note})
        elif case == "labeller-2-r2":
            run = sa.deliver(world, "labeller-2", half, round_=2, program="labels2", program_args={"extra_result": note})
        else:
            run = sa.deliver(world, "overlap-auditor", half, program="decide", program_args={"extra_result": note})
    assert run.code == 20, run.why()
    line = run.line
    assert line["status"] == "rejected" and line["reason"] == "result" and line["out"]["schema_ok"] is False, line
    folder = world.counts_dir(line)
    for name, text in (("counts.json", (folder / "counts.json").read_text()), ("stdout", run.out), ("stderr", run.err),
                       ("launch.log", (folder / "launch.log").read_text())):
        assert MARK not in text, f"the marker reached {name}"
    assert world.hashes(world.exp) == exp0, "the experiment folder changed"
    assert changes(sr0, world.hashes(world.sr)) <= {f"indep-walls/{sa.FLOW[case.rsplit('-r', 1)[0]][0]}/{line['run']}.tar"}
