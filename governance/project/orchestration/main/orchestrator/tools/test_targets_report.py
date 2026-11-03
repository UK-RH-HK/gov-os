"""targets_report.py's tests (DEC-1038 (4)): the shares over a planted day, the working hours across midnight, the
events, the incidents with their causes, the worst hour. Run: python3 -m pytest -q test_targets_report.py."""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import targets_report as tr  # noqa: E402

DAY = datetime(2026, 11, 2, 0, 0)


def plant_day(tmp, breach):
    """One row a minute for 24 hours from 00:00; `breach(target, t)` gives each target's value."""
    rows = []
    for m in range(24 * 60):
        t = DAY + timedelta(minutes=m)
        rows.append(json.dumps({"t": t.strftime("%Y-%m-%dT%H:%M:%S"),
                                "targets": {k: breach(k, t) for k in tr.TARGETS}}))
    (tmp / "capacity").mkdir()
    (tmp / "capacity" / "balance.jsonl").write_text("\n".join(rows) + "\n")
    (tmp / "incidents").mkdir()
    return tmp / "capacity" / "balance.jsonl"


def run(tmp, bal, *extra):
    return tr.main(["--since", "2026-11-02", "--balance", str(bal), "--incidents", str(tmp / "incidents"), "--json",
                    *extra], now=DAY + timedelta(hours=24))


def test_the_shares_over_a_planted_day(tmp_path, capsys):
    def breach(k, t):
        if k == "T1":  # 16:00 to 18:59 breached: 3 of the 18.5 working hours
            return 16 <= t.hour < 19
        if k == "T3":
            return None if t.hour < 12 else False  # the GPU unread in the morning: not counted
        if k == "T4":
            return t.hour == 9 and t.minute < 2  # two passes with events
        return False
    bal = plant_day(tmp_path, breach)
    assert run(tmp_path, bal) == 0
    rep = json.loads(capsys.readouterr().out)
    t = rep["targets"]
    # working hours 07:30-02:00: 00:00-01:59 (120) + 07:30-23:59 (990) = 1,110 passes
    assert rep["passes"] == 1110 and t["T1"]["passes"] == 1110
    assert t["T1"]["breached"] == 180 and t["T1"]["share"] == round(100 * 930 / 1110, 1) and t["T1"]["ok"] is True
    assert t["T2"]["share"] == 100.0 and t["T2"]["ok"] is True
    assert t["T3"]["passes"] == 720 and t["T3"]["ok"] is True  # 12:00-23:59 only
    assert t["T4"]["breached"] == 2 and t["T4"]["ok"] is False and t["T4"]["share"] is not None
    assert t["T5"]["ok"] is True
    assert t["T1"]["worst_hour"] == {"hour": "2026-11-02 16:00", "share": 0.0}  # the earliest of three
    assert rep["worst_hour"] == {"hour": "2026-11-02 16:00", "breached_passes": 60}


def test_t1_under_80_percent_is_missed_and_the_text_says_so(tmp_path, capsys):
    # the first quarter of every hour breached: 18 whole working hours x 15 of 1,110 passes (07:30-07:59 met)
    bal = plant_day(tmp_path, lambda k, t: k == "T1" and t.minute < 15)
    assert tr.main(["--since", "2026-11-02", "--balance", str(bal), "--incidents", str(tmp_path / "incidents")],
                   now=DAY + timedelta(hours=24)) == 0
    out = capsys.readouterr().out
    assert "T1 busy cores within the band: met 75.7 % of 1110 passes (target at least 80 %): MISSED" in out
    assert "T2 memory available above the floor: met 100.0 % of 1110 passes (target 100 %): MET" in out
    assert "T4 no timed-out embedding: 0 passes with events (target 0): MET" in out


def test_the_working_hours_cross_midnight_and_another_span_counts_otherwise(tmp_path, capsys):
    bal = plant_day(tmp_path, lambda k, t: False)
    run(tmp_path, bal, "--hours", "09:00-17:00")
    assert json.loads(capsys.readouterr().out)["passes"] == 8 * 60
    assert tr.in_hours(datetime(2026, 11, 2, 1, 59), tr.hours_span("07:30-02:00"))
    assert not tr.in_hours(datetime(2026, 11, 2, 2, 0), tr.hours_span("07:30-02:00"))


def test_the_incidents_with_their_causes(tmp_path, capsys):
    bal = plant_day(tmp_path, lambda k, t: False)
    inc = tmp_path / "incidents"
    (inc / "2026-11-02-1620-T1-cpu.md").write_text("# Incident\n\n- **Cause:** gitleaks pools of 20 in each worker\n"
                                                   "- **Fix:** \n- **Closed:** 2026-11-02 17:10:00: held\n")
    (inc / "2026-11-02-2105-T2.md").write_text("# Incident\n\n- **Cause:** \n- **Fix:** \n")
    (inc / "2026-11-02-2200-outside-slot.md").write_text("- **Cause:** \n")
    (inc / "2026-11-01-0900-T3.md").write_text("- **Cause:** old\n")  # before --since: not listed
    run(tmp_path, bal)
    rep = json.loads(capsys.readouterr().out)
    got = [(i["at"], i["target"], i["cause"], i["closed"]) for i in rep["incidents"]]
    assert got == [("2026-11-02 16:20", "T1", "gitleaks pools of 20 in each worker", "2026-11-02 17:10:00: held"),
                   ("2026-11-02 21:05", "T2", "(not filled)", None),
                   ("2026-11-02 22:00", "outside-slot", "(not filled)", None)]


def test_no_rows_is_exit_2(tmp_path):
    assert tr.main(["--balance", str(tmp_path / "none.jsonl")]) == 2


def test_rotated_rows_are_read_too(tmp_path, capsys):
    bal = plant_day(tmp_path, lambda k, t: False)
    lines = bal.read_text().splitlines()
    (bal.parent / "balance-20261102-120000.jsonl").write_text("\n".join(lines[:720]) + "\n")
    bal.write_text("\n".join(lines[720:]) + "\n")
    run(tmp_path, bal)
    assert json.loads(capsys.readouterr().out)["passes"] == 1110
