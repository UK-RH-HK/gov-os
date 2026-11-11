"""ACT-OPERATOR-ROUNDS-1 (DEC-1131 (3)): READY needs no KPI line marked fail; the two-round cap counts per ACT id."""
import json
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_w2_148_kit import OPDIR, Kit  # noqa: E402

sys.path.insert(0, str(OPDIR))
import verdict  # noqa: E402


@pytest.fixture
def kit(tmp_path):
    return Kit(tmp_path)


def rec(kpis):
    return "x\n```verdict\n" + json.dumps({"kpis": kpis}) + "\n```\n"


# ---------------------------------------------------------------------------------------------------- the verdict
def test_a_fail_with_no_blocking_finding_is_not_ready():
    ok, why = verdict.ready(rec([{"kpi": "K7", "verdict": "fail", "findings": []}]))
    assert ok is False and why == ["K7: the KPI line is marked fail"]
    ok, why = verdict.ready(rec([{"kpi": "K7", "verdict": "fail", "findings": [
        {"id": "F1", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}]))
    assert ok is False and "marked fail" in why[0]


def test_all_pass_with_non_blocking_findings_is_still_ready():
    ok, why = verdict.ready(rec([{"kpi": "K1", "verdict": "pass", "findings": [
        {"id": "F1", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}]}]))
    assert (ok, why) == (True, [])


@pytest.mark.parametrize("v", [{"kpi": "K1"}, {"kpi": "K1", "verdict": "partial"}, {"kpi": "K1", "verdict": "Pass"}])
def test_no_or_an_unknown_verdict_is_not_ready(v):
    ok, why = verdict.ready(rec([v]))
    assert ok is False and "neither pass nor fail" in why[0]


# ---------------------------------------------------------------------------------------------------- the operator
def test_g4_a_fail_with_no_blocking_finding_is_refused_by_the_verdict(kit):
    msha = kit.bundle("ACT-R1", {("repo", "tests/optin-x.txt"): b"one\nthree\n"})
    p = kit.scratch / "acts/ACT-R1/review.md"
    p.write_text(p.read_text().replace('"verdict": "pass"', '"verdict": "fail"'))
    rc, res, _ = kit.run("run", "ACT-R1", msha)
    assert rc != 0 and res["gate"] == "G4" and "marked fail" in res["reason"] and "READY by verdict.py" in res["reason"]


def build(kit, act, content, rounds):
    return kit.bundle(act, {("repo", "tests/optin-x.txt"): content}, rounds=rounds)


def test_g4_a_second_build_of_the_same_act_after_two_reviews_is_refused_naming_the_count(kit):
    m1 = build(kit, "ACT-R2", b"one\nthree\n", rounds=2)
    rc, res, _ = kit.run("run", "ACT-R2", m1)
    assert res["result"] == "applied", res
    assert [e["act_rounds"] for e in kit.log() if e["gate"] == "G4"] == [2]
    m2 = build(kit, "ACT-R2", b"one\n", rounds=1)
    assert m2 != m1
    rc, res, _ = kit.run("run", "ACT-R2", m2)
    assert rc != 0 and res["gate"] == "G4", res
    assert "third review round" in res["reason"] and "to the owner" in res["reason"]
    assert "3 verdict blocks across this ACT's builds, 1 in this one" in res["reason"]
    assert (kit.repo / "tests/optin-x.txt").read_bytes() == b"one\nthree\n"      # the second build applied nothing
    assert any(n["kind"] == "to-owner" for n in kit.notices())


def test_g4_one_review_each_on_two_builds_is_two_rounds_and_passes(kit):
    m1 = build(kit, "ACT-R3", b"one\nthree\n", rounds=1)
    assert kit.run("run", "ACT-R3", m1)[1]["result"] == "applied"
    m2 = build(kit, "ACT-R3", b"one\n", rounds=1)
    rc, res, _ = kit.run("run", "ACT-R3", m2)
    assert res["result"] == "applied", res
    assert [e["act_rounds"] for e in kit.log() if e["gate"] == "G4"] == [1, 2]
    assert [e["rounds"] for e in kit.log() if e["gate"] == "G4"] == [1, 1]


def test_g4_a_different_act_id_is_unaffected(kit):
    m1 = build(kit, "ACT-R4", b"one\nthree\n", rounds=2)
    assert kit.run("run", "ACT-R4", m1)[1]["result"] == "applied"
    m2 = build(kit, "ACT-R5", b"one\n", rounds=2)
    rc, res, _ = kit.run("run", "ACT-R5", m2)
    assert res["result"] == "applied", res
    assert [e["act_rounds"] for e in kit.log() if e["gate"] == "G4"] == [2, 2]


def test_g4_a_review_record_that_carries_the_earlier_block_forward_counts_it_once(kit):
    m1 = build(kit, "ACT-R6", b"one\nthree\n", rounds=1)
    assert kit.run("run", "ACT-R6", m1)[1]["result"] == "applied"
    first = (kit.scratch / "acts/ACT-R6/review.md").read_text()
    m2 = build(kit, "ACT-R6", b"one\n", rounds=1)
    p = kit.scratch / "acts/ACT-R6/review.md"
    p.write_text(first + p.read_text())                      # round 1 of build 1, then round 2 of build 2
    rc, res, _ = kit.run("run", "ACT-R6", m2)
    assert res["result"] == "applied", res
    assert [e["act_rounds"] for e in kit.log() if e["gate"] == "G4"] == [1, 2]


def test_g4_the_same_build_asked_twice_is_not_counted_twice(kit):
    msha = kit.bundle("ACT-R7", {("repo", "tests/optin-x.txt"): b"one\nthree\n"}, rounds=2, reviewer="cto")
    for _ in range(2):
        rc, res, _ = kit.run("run", "ACT-R7", msha)
        assert res["gate"] == "G4" and "author" in res["reason"]      # refused for the author, never for a count


def test_g4_a_lookalike_folder_of_another_act_id_does_not_count(kit):
    m1 = build(kit, "ACT-R8-1", b"one\nthree\n", rounds=2)
    assert kit.run("run", "ACT-R8-1", m1)[1]["result"] == "applied"
    m2 = build(kit, "ACT-R8", b"one\n", rounds=2)
    rc, res, _ = kit.run("run", "ACT-R8", m2)
    assert res["result"] == "applied", res


def test_g4_a_folder_whose_manifest_names_another_act_does_not_count(kit):
    m1 = build(kit, "ACT-R9", b"one\nthree\n", rounds=1)
    assert kit.run("run", "ACT-R9", m1)[1]["result"] == "applied"
    real = next((kit.root / "acts").glob("ACT-R9-*"))
    fake = kit.root / "acts" / ("ACT-R9-" + "0" * 12)
    shutil.copytree(real, fake)                              # named for ACT-R9, its manifest naming another ACT
    fake.chmod(0o755)
    (fake / "manifest.json").chmod(0o644)
    m = json.loads((fake / "manifest.json").read_text())
    m["act"] = "ACT-SOMETHING-ELSE"
    (fake / "manifest.json").write_text(json.dumps(m))
    (fake / "review.md").chmod(0o644)
    text = (fake / "review.md").read_text()
    (fake / "review.md").write_text(text + text.replace('"reviewer": "rev"', '"reviewer": "other"'))   # two more blocks
    m2 = build(kit, "ACT-R9", b"one\n", rounds=1)
    rc, res, _ = kit.run("run", "ACT-R9", m2)
    assert res["result"] == "applied", res                  # 1 + 1 counted; the fake's blocks are not
    assert [e["act_rounds"] for e in kit.log() if e["gate"] == "G4"] == [1, 2]
