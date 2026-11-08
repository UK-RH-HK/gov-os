"""The bar's arithmetic and rounding (§4.3), the intervals, fresh80_figures.py's verdict line from the judged run only
(the nonexistent-id question apart, the stricter grade, agreement), the data conditions (dry, and E3's run with its own
brake, "data only, not judged"), the E4 copies as built from the reviewed scripts with F1 kept, and no hidden path."""
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

import f80lib as L
import fresh80_data as DA
import fresh80_figures as FG
from helpers import FakeClaude, clean, make_attempt, reader, rows, setup

TOOLS = Path(__file__).resolve().parent.parent


# ---- the bar (§4.3)

@pytest.mark.parametrize("right,wrong,passes", [(68, 3, True), (67, 3, False), (68, 4, False), (79, 0, True),
                                                (76, 3, True), (67, 0, False)])
def test_bar_on_79(right, wrong, passes):
    b = L.bar(right, wrong, 79)
    assert b["passes"] is passes
    assert (b["need_right"], b["max_wrong"], b["target_right"]) == (68, 3, 76)


def test_bar_rounding_edges():
    assert L.bar(75, 0, 79)["target_ok"] is False and L.bar(76, 0, 79)["target_ok"] is True
    assert 100 * 67 / 79 < 85 < 100 * 68 / 79  # 84.8 % misses, 86.1 % passes
    assert 100 * 3 / 79 <= 5 < 100 * 4 / 79  # 3.8 % passes, 5.1 % misses
    b = L.bar(68, 4, 80)  # another denominator: 85 % of 80 is 68 exactly, 5 % is 4
    assert b["need_right"] == 68 and b["max_wrong"] == 4 and b["passes"]


def test_exact_interval_is_clopper_pearson():
    lo, hi = L.exact_interval(70, 79)
    a = 0.025
    assert abs(L._tail_ge(70, 79, lo) - a) < 1e-9 and abs(L._tail_le(70, 79, hi) - a) < 1e-9
    assert (round(100 * lo, 1), round(100 * hi, 1)) == (79.5, 94.7)
    assert L.exact_interval(0, 79)[0] == 0.0 and L.exact_interval(79, 79)[1] == 1.0


def test_wilson_matches_fresh80_1_example():
    lo, hi = L.wilson_interval(70, 79)
    assert (round(100 * lo, 1), round(100 * hi, 1)) == (79.7, 93.9)  # FRESH-80-1 §4.3's "79.7 to 93.9 %"


# ---- the figures

def figures(planted, capsys):
    FG.main(["--sets-root", str(planted["root"])])
    out = capsys.readouterr().out
    clean(out, planted)
    return out


def test_verdict_line_from_the_judged_run(planted, monkeypatch, capsys):
    make_attempt(planted)
    setup(planted, monkeypatch, FakeClaude(check_wrong={"v01", "v02"}, wrong={"v04", "v05", "v06", "v07"}))
    reader(planted)
    capsys.readouterr()
    (planted["root"] / "runs/fresh-80/preflight.json").write_text(json.dumps({"all_ok": True, "item6": {"nowhere": True}}))
    out = figures(planted, capsys)
    # 79 judged; 4 wrong claims (graded wrong): 75 right, MISSES on wrong claims (4 > 3)
    assert "right end to end: 75 of 79 (94.9 %" in out and "wrong claims: 4 of 79" in out
    assert "at least 68 right (met) and at most 3 wrong claims (NOT met): MISSES" in out
    assert "the stricter of the two grades (A2): right 73 of 79" in out
    assert "grader agreement: 78 of 80" in out
    assert "hit@5 69 of 79" in out
    assert "the nonexistent-id question (apart, DEC-1071 (5)): run yes; right yes; the product stopped with UNRESOLVED_IDS naming its id: yes" in out
    assert "DATA ONLY, NOT JUDGED" in out
    f = json.loads((planted["root"] / "runs/fresh-80/figures.json").read_text())
    assert f["n"] == 79 and f["A2"] == 75 and f["A1"] == 65


def test_passing_verdict_and_missing_rows(planted, monkeypatch, capsys):
    make_attempt(planted)
    setup(planted, monkeypatch, FakeClaude())
    reader(planted)
    capsys.readouterr()
    out = figures(planted, capsys)
    assert "right end to end: 79 of 79" in out and "PASSES" in out and "reached" in out
    assert "as at the pre-flight: yes" in out  # readiness-7 F6: the result repeats the digest
    (planted["root"] / "runs/fresh-80/reader/v10.json").unlink()  # a question never run: not right, never dropped
    out = figures(planted, capsys)
    assert "right end to end: 78 of 79" in out and "not run (counted as not right, never dropped): 1: v10" in out


def test_dropped_nonexistent_id(planted, monkeypatch, capsys):
    make_attempt(planted)
    setup(planted, monkeypatch, FakeClaude())
    reader(planted)
    capsys.readouterr()
    (planted["root"] / "runs/fresh-80/preflight.json").write_text(json.dumps({"item6": {"nowhere": False}}))
    out = figures(planted, capsys)
    assert "DROPPED from every figure" in out and "of 79" in out


# ---- the data conditions

def test_data_dry_all_conditions(planted, monkeypatch, capsys):
    make_attempt(planted)
    fake = FakeClaude()
    setup(planted, monkeypatch, fake)
    for c in DA.PROJECTIONS:
        if c == "e2g" and not DA.GLOSSARY.is_dir():
            continue
        assert DA.main([c, "--sets-root", str(planted["root"]), "--clone", str(planted["clone"]), "--dry"]) == 0
    out = capsys.readouterr().out
    assert fake.calls == 0 and out.count("data only, not judged") >= 4
    assert "projection 36.00, brake 72.00" in out and "projection 17.00, brake 34.00" in out
    clean(out, planted)


def test_data_refused_during_hold_or_before_judged(planted, monkeypatch):
    make_attempt(planted)
    setup(planted, monkeypatch, FakeClaude())
    with pytest.raises(SystemExit):  # the hold is on (setup)
        DA.main(["e3", "--sets-root", str(planted["root"]), "--clone", str(planted["clone"])])
    monkeypatch.setattr(L, "hold_on", lambda: False)
    with pytest.raises(SystemExit):  # the judged run has not run
        DA.main(["e3", "--sets-root", str(planted["root"]), "--clone", str(planted["clone"])])


def test_data_e3_runs_with_its_own_brake(planted, monkeypatch, capsys):
    make_attempt(planted)
    setup(planted, monkeypatch, FakeClaude())
    reader(planted)
    monkeypatch.setattr(L, "hold_on", lambda: False)
    fake = FakeClaude(cost=0.01)
    monkeypatch.setattr(L, "_run_claude", fake)
    DA.main(["e3", "--sets-root", str(planted["root"]), "--clone", str(planted["clone"])])
    out = capsys.readouterr().out
    clean(out, planted)
    d = planted["root"] / "runs/fresh-80/data/e3"
    assert len([f for f in d.glob("v*.json")]) == 320
    s = json.loads((d / "summary.json").read_text())
    assert s["label"] == "data only, not judged" and s["brake_usd"] == 72.0
    assert s["top5"]["right"] == 69  # the 10 planted misses lack the gold in every one-call bundle
    out = figures(planted, capsys)
    assert "e3: top5: right 69 of 79" in out
    # a one-call question's second call is never the next question's first (e3_run.py's slip, fixed)
    store = DA.Store(planted["clone"])
    att = L.counting_attempt(planted["root"])
    q = {"id": "v01"}
    b = DA.e3_bundles(q, att / "kept", (1, 1), store)
    assert not any(it[0] == "docs/q/v02.md" for it in b["unranked40"])


def test_data_brake(planted, monkeypatch, capsys):
    make_attempt(planted)
    setup(planted, monkeypatch, FakeClaude())
    reader(planted)
    monkeypatch.setattr(L, "hold_on", lambda: False)
    monkeypatch.setattr(L, "_run_claude", FakeClaude(cost=1.0))
    DA.main(["e3", "--sets-root", str(planted["root"]), "--clone", str(planted["clone"]), "--projection", "2"])
    s = json.loads((planted["root"] / "runs/fresh-80/data/e3/summary.json").read_text())
    assert s["stopped"] and "brake" in s["stopped"]
    assert len(list((planted["root"] / "runs/fresh-80/data/e3").glob("v*.json"))) <= 2 + DA.WORKERS


# ---- the E4 copies

def test_e4_copies_as_built_with_f1_kept():
    sys.path.insert(0, str(TOOLS))
    import make_f80_e4 as MK
    outs = MK.outputs()
    for name, text in outs.items():
        assert (TOOLS / name).read_text() == text, name
    w = outs["f80_e4_window.sh"]
    for f1 in ("rc=$?; trap '' INT TERM PIPE; trap - EXIT",  # the cleanup ignores a second signal
               "setsid -w env --default-signal=INT,TERM,PIPE ~/.local/bin/gov retrieve",  # restore in its own session
               "trap '' INT TERM; tee -p -a \"$OUT/window.log\"",  # the output frame ignores INT and TERM, -p
               "trap cleanup EXIT; trap 'exit 130' INT; trap 'exit 143' TERM"):
        assert f1 in w, f1
    for name in ("f80_e4_window.sh", "f80_e4_replays.sh", "f80_e4_prep.sh", "f80_so_measure.sh", "f80_e5_live.sh",
                 "run_measure.sh"):
        assert subprocess.run(["bash", "-n", str(TOOLS / name)]).returncode == 0, name
        src = "\n".join(x for x in (TOOLS / name).read_text().splitlines() if not x.lstrip().startswith("#"))
        assert "gov-os-eval/runs" not in src and "memory-verdict-2/hidden" not in src.replace(
            "fixtures/evaluation/memory-verdict-2/hidden/**", "")


def test_data_e3sa_and_e5_run(planted, monkeypatch, capsys):
    import shutil
    att = make_attempt(planted)
    setup(planted, monkeypatch, FakeClaude())
    reader(planted)
    monkeypatch.setattr(L, "hold_on", lambda: False)
    monkeypatch.setattr(L, "_run_claude", FakeClaude())
    DA.main(["e3sa", "--sets-root", str(planted["root"]), "--clone", str(planted["clone"])])
    live = planted["root"] / "runs/fresh-80/data/e5/live"
    live.mkdir(parents=True)
    shutil.copytree(att / "kept", live / "kept")
    shutil.copy(att / "measure.txt", live / "measure.txt")
    DA.main(["e5", "--sets-root", str(planted["root"]), "--clone", str(planted["clone"])])
    out = capsys.readouterr().out
    clean(out, planted)
    s = json.loads((planted["root"] / "runs/fresh-80/data/e3sa/summary.json").read_text())
    assert s["top20"]["A2"] == 79 and s["top20"]["A1"] == 69 and s["top20"]["search_failures"] == 0
    s5 = json.loads((planted["root"] / "runs/fresh-80/data/e5/summary.json").read_text())
    assert s5["bundle12000"]["right"] == 69 and s5["projection_usd"] == 17.0


@pytest.mark.parametrize("script", ["f80_e4_prep.sh", "f80_e4_replays.sh"])
def test_e4_dry_prints_no_hidden_path(planted, script):
    import os
    e = {k: v for k, v in os.environ.items() if k != "GOV_STORE"}
    e["DRY"] = "1"
    p = subprocess.run(["bash", str(TOOLS / script), "--sets-root", str(planted["root"])], capture_output=True,
                       text=True, env=e, start_new_session=True, timeout=120)
    out = p.stdout + p.stderr
    assert "DRY:" in out
    clean(out, planted)
    assert not (planted["root"] / "runs/fresh-80/data").exists()  # nothing written


# ---- the hold (readiness-7 F5)

def run_hold(cmd, f):
    return subprocess.run(["bash", str(TOOLS / "hold.sh"), cmd, "--file", str(f)], capture_output=True, text=True)


def test_hold_never_overwrites_and_ends_only_its_own(tmp_path):
    f = tmp_path / "act-in-progress.txt"
    f.write_text("ACT-GUARD-SETS-1 hand-over: until the owner's word\n")
    p = run_hold("begin", f)
    assert p.returncode == 1 and "ACT-GUARD-SETS-1 hand-over" in p.stdout
    assert f.read_text() == "ACT-GUARD-SETS-1 hand-over: until the owner's word\n"
    p = run_hold("end", f)
    assert p.returncode == 1 and f.is_file()  # not ours: left in place
    f.unlink()
    assert run_hold("begin", f).returncode == 0 and f.read_text().startswith("FRESH-80 HOLD")
    import f80lib as L
    assert L.HOLD_MARK in f.read_text()
    assert run_hold("end", f).returncode == 0 and not f.exists()
    assert len(list(tmp_path.glob("act-in-progress.ended-*-fresh80.txt"))) == 1


def test_figures_refuse_a_denominator_not_79(planted, monkeypatch, capsys):  # code review R10
    make_attempt(planted)
    setup(planted, monkeypatch, FakeClaude())
    reader(planted)
    plan = planted["root"] / "runs/fresh-80/reader/plan.json"
    d = json.loads(plan.read_text())
    d["main"] = d["main"][:-1]
    plan.write_text(json.dumps(d))
    capsys.readouterr()
    assert L.run_tool("figures", FG.main, ["--sets-root", str(planted["root"])]) == 2
    assert "not the declared 79" in capsys.readouterr().out
