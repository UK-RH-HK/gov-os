"""Tests for measure_week.py on planted files under tmp_path (paths passed as arguments)."""
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import measure_week as mw  # noqa: E402

UTC = dt.timezone.utc


def T(s):
    return mw.p_ts(s)


def write(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return p


def usage_line(ts, pct):
    return f"{ts} week (all models)={pct}% (resets Nov 15, 8:59am (Europe/London));week (Fable)=0% (resets Nov 15, 9am (Europe/London)); last 24h: 1 requests"


@pytest.fixture
def log(tmp_path):
    d = tmp_path / "log"
    d.mkdir()
    return d


# ---------------------------------------------------------------- usage

def test_both_line_forms_and_the_lines_log_are_read(log):
    write(log / "usage.txt",
          "2026-11-01 12:05:16 session unread week 0|Nov 8, 9am (Europe/London)\n"
          "2026-10-29 17:12:01 session 5|Oct 29, 8:49pm (Europe/London) week 15|Nov 1, 8:59am (Europe/London)\n"
          "\n" + usage_line("2026-11-07 14:47:08", 82) + "\n"
          "not a reading at all\n")
    write(log / "usage-lines.log", "2026-11-11 23:15:56 81\n")
    readings, skipped, last_reset = mw.read_usage(log)
    assert [(t.strftime("%m-%d %H:%M"), v) for t, v in readings] == [
        ("10-29 17:12", 15), ("11-01 12:05", 0), ("11-07 14:47", 82), ("11-11 23:15", 81)]
    assert skipped == 1
    assert mw.reset_time_from(last_reset) == T("2026-11-15 09:00:00")


def test_a_drop_is_a_reset_and_gains_the_new_value(log):
    pts = [("2026-11-08 07:00:00", 90), ("2026-11-08 07:30:00", 95), ("2026-11-08 08:00:00", 100),
           ("2026-11-08 09:30:00", 3), ("2026-11-08 10:00:00", 8), ("2026-11-08 10:30:00", 8)]
    readings = [(T(t), v) for t, v in pts]
    kinds = [s["kind"] for s in mw.usage_segments(readings)]
    assert kinds == ["rise", "rise", "reset", "rise", "flat"]
    day = mw.usage_by_day(readings)[dt.date(2026, 11, 8)]
    # 5 + 5 + (reset: the new value 3) + 5 + 0
    assert day["gain"] == pytest.approx(18.0)
    assert day["resets"] == 1
    assert day["hours"] == pytest.approx(3.5)


def test_a_gap_day_is_marked_and_never_zero(tmp_path, log):
    write(log / "usage.txt", usage_line("2026-11-02 10:00:00", 10) + "\n"
          + usage_line("2026-11-02 10:30:00", 12) + "\n"
          + usage_line("2026-11-05 10:00:00", 40) + "\n"
          + usage_line("2026-11-05 11:00:00", 43) + "\n")
    paths = mw.Paths(root=tmp_path, log=log)
    rows, meta = mw.build_daily(paths, "2026-11-02", now=T("2026-11-05 12:00:00"))
    by = {r["day"]: r for r in rows}
    assert by["2026-11-02"]["pts"] == pytest.approx(2.0)
    for d in ("2026-11-03", "2026-11-04"):
        assert by[d]["pts"] is None and by[d]["pts_h"] is None and by[d]["usage_h"] == 0.0
    assert by["2026-11-05"]["pts"] == pytest.approx(3.0)
    assert meta["usage_spans"][0]["pct_from"] == 12 and meta["usage_spans"][0]["pct_to"] == 40
    text = mw.table(rows, False)
    assert "gap" in text.splitlines()[2]


# ---------------------------------------------------------------- spend and leads

def test_spend_is_summed_per_day_with_tier_role_and_unpriced(tmp_path, log):
    rows = [
        {"at": "2026-11-09 10:00", "kind": "launched", "role": "engineer", "model": "claude-opus-5-5", "tier": "opus",
         "cost_usd": 1.5, "what": "a"},
        {"at": "2026-11-09 23:59", "kind": "worker", "role": None, "cost_usd": 2.0, "what": "review (sonnet, high)"},
        {"at": "2026-11-09 12:00", "kind": "agent", "cost_usd": None, "what": "unpriced"},
        {"at": "2026-11-09 13:00", "kind": "brake", "cost_usd": None, "what": "brake"},
        {"at": "2026-11-10 00:00", "kind": "launched", "role": "engineer", "tier": "opus", "cost_usd": 4.0, "what": "b"},
    ]
    write(log / "spend.jsonl", "\n".join(json.dumps(r) for r in rows) + "\nnot json\n")
    paths = mw.Paths(root=tmp_path, log=log)
    out, meta = mw.build_daily(paths, "2026-11-08", now=T("2026-11-10 12:00:00"))
    by = {r["day"]: r for r in out}
    assert by["2026-11-08"]["usd"] is None                      # before the first spend row: a gap
    assert by["2026-11-09"]["usd"] == pytest.approx(3.5)
    assert by["2026-11-09"]["spend_rows"] == 2 and by["2026-11-09"]["unpriced"] == 1
    assert by["2026-11-09"]["tiers"] == {"sonnet": 2.0, "opus": 1.5}
    assert by["2026-11-09"]["roles"]["engineer"] == 1.5
    assert by["2026-11-10"]["usd"] == pytest.approx(4.0)
    assert meta["spend_bad_lines"] == 1


def test_lead_hours_count_in_status_leads_over_real_intervals(tmp_path, log):
    lines = []
    t = T("2026-11-11 10:00:00")
    for i in range(121):                       # 120 minutes at one sample a minute
        at = (t + dt.timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M:%S")
        lines.append(json.dumps({"at": at, "avail_mb": 1, "leads": {
            "W2-1": {"in_status": True}, "W2-2": {"in_status": True}, "W2-3": {"in_status": False}}}))
    write(log / "lead-mem-watch.jsonl", "\n".join(lines) + "\n")
    write(log / "lead-ledger.jsonl",
          json.dumps({"W2": "W2-1", "start": "2026-11-11 10:00:00", "status": "DONE", "wall_minutes": 30}) + "\n"
          + json.dumps({"W2": "W2-2", "start": "2026-11-11 10:05:00", "status": "REFUSED", "wall_minutes": 0}) + "\n")
    paths = mw.Paths(root=tmp_path, log=log)
    rows, _ = mw.build_daily(paths, "2026-11-10", now=T("2026-11-11 12:00:00"))
    by = {r["day"]: r for r in rows}
    assert by["2026-11-11"]["lead_h"] == pytest.approx(2 * 2.0)   # two leads, two hours
    assert by["2026-11-11"]["lead_runs"] == 1 and by["2026-11-11"]["lead_refused"] == 1
    assert by["2026-11-10"]["lead_h"] is None and by["2026-11-10"]["lead_runs"] is None   # gaps, not zeros


# ---------------------------------------------------------------- the fit and the forecast

def test_ols_recovers_a_planted_line():
    buckets = [dict(t=None, x=x, y=1.0 + 0.5 * x) for x in (0, 1, 2, 3, 4, 0, 2, 4, 1, 3)]
    fit = mw.ols(buckets)
    assert fit["identified"]
    assert fit["a"] == pytest.approx(1.0) and fit["b"] == pytest.approx(0.5)
    assert fit["s"] == pytest.approx(0.0, abs=1e-9)
    assert fit["r2"] == pytest.approx(1.0)


def test_ols_without_lead_variation_reports_no_per_lead_rate():
    fit = mw.ols([dict(t=None, x=0.0, y=y) for y in (1, 2, 3, 2)])
    assert not fit["identified"] and fit["b"] is None and fit["a"] == pytest.approx(2.0)


def test_forecast_on_a_planted_series(tmp_path, log):
    # 26 h of hourly readings: rate per hour = 1 + 1 x leads, leads cycling 0,1,2 by the hour
    start = T("2026-11-10 00:00:00")
    pct, ulines, llines = 0, [], []
    for h in range(27):
        t = start + dt.timedelta(hours=h)
        ulines.append(usage_line(t.strftime("%Y-%m-%d %H:%M:%S"), pct))
        pct += 1 + (h % 3)
        for m in range(60):
            at = (t + dt.timedelta(minutes=m)).strftime("%Y-%m-%d %H:%M:%S")
            leads = {f"W2-{k}": {"in_status": True} for k in range(h % 3)}
            llines.append(json.dumps({"at": at, "avail_mb": 1, "leads": leads}))
    write(log / "usage.txt", "\n".join(ulines) + "\n")
    write(log / "lead-mem-watch.jsonl", "\n".join(llines) + "\n")
    readings, _, _ = mw.read_usage(log)
    samples, _ = mw.read_leads(log)
    end = start + dt.timedelta(hours=26)
    fc = mw.forecast(50.0, end, end + dt.timedelta(hours=20), [0, 3, 5], readings, samples, window_h=24)
    fit = fc["fit"]
    assert fit["n"] >= 20
    assert fit["a"] == pytest.approx(1.0, abs=0.05) and fit["b"] == pytest.approx(1.0, abs=0.05)
    r3 = fc["rows"][1]
    assert r3["rate"] == pytest.approx(4.0, abs=0.15)
    assert r3["h100"] == pytest.approx(12.5, abs=0.6)
    assert r3["runs_out_before_reset"] is True            # 12.5 h < 20 h to the reset
    assert fc["rows"][0]["runs_out_before_reset"] is False  # 0 leads: 50 pts at 1/h = 50 h > 20 h
    # largest steady count: (50/20 - 1) / 1 = 1.5 leads
    assert fc["steady"][100] == pytest.approx(1.5, abs=0.1)
    text = "\n".join(mw.fmt_forecast(fc))
    assert "pts/h = " in text and "RUNS OUT" in text and "Largest steady lead count" in text


def test_a_post_reset_forecast_fits_the_newest_window(tmp_path, log):
    write(log / "usage.txt", "\n".join(usage_line(f"2026-11-10 {h:02d}:00:00", h) for h in range(24)) + "\n")
    llines = [json.dumps({"at": f"2026-11-10 {h:02d}:{m:02d}:00", "avail_mb": 1, "leads": {}})
              for h in range(24) for m in range(60)]
    write(log / "lead-mem-watch.jsonl", "\n".join(llines) + "\n")
    readings, _, _ = mw.read_usage(log)
    samples, _ = mw.read_leads(log)
    fc = mw.forecast(0.0, T("2026-11-20 09:00:00"), T("2026-11-27 09:00:00"), [1], readings, samples, 24)
    assert fc["window_end"] == T("2026-11-10 23:00:00") and fc["fit"]["n"] > 10


# ---------------------------------------------------------------- git sources, record, cli

def git_repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()

    def g(*args, date=None):
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                   GIT_COMMITTER_EMAIL="t@t", GIT_CONFIG_GLOBAL="/dev/null")
        if date:
            env["GIT_COMMITTER_DATE"] = env["GIT_AUTHOR_DATE"] = date
        subprocess.run(["git", "-C", str(r), *args], check=True, capture_output=True, env=env)
    g("init", "-b", "main")
    return r, g


def test_closes_and_merges_come_from_git(tmp_path, log):
    r, g = git_repo(tmp_path)
    write(r / ".tickets/A.md", "---\nid: A\nstatus: open\ntags: [x]\n---\nbody\n")
    write(r / ".tickets/B.md", "---\nid: B\nstatus: open\ntags: [withdrawn]\n---\n")
    g("add", "."); g("commit", "-m", "tickets", date="2026-11-09T10:00:00+00:00")
    write(r / ".tickets/A.md", "---\nid: A\nstatus: closed\ntags: [x]\n---\nbody\n")
    write(r / ".tickets/B.md", "---\nid: B\nstatus: closed\ntags: [withdrawn]\n---\n")
    write(r / "governance/project/orchestration/closes/W2-1-A.md", "# closed\n- Closed: 2026-11-10 08:30:00 GMT, by x\n")
    g("add", "."); g("commit", "-m", "close A", date="2026-11-10T09:00:00+00:00")
    g("checkout", "-b", "feat")
    write(r / "f.txt", "x")
    g("add", "."); g("commit", "-m", "work", date="2026-11-10T11:00:00+00:00")
    g("checkout", "main")
    g("merge", "--no-ff", "-m", "Merge feat", "feat", date="2026-11-10T12:00:00+00:00")
    paths = mw.Paths(root=r, log=log, branch="main")
    rows, meta = mw.build_daily(paths, "2026-11-09", now=T("2026-11-10 20:00:00"))
    by = {x["day"]: x for x in rows}
    assert by["2026-11-10"]["closes"] == 1          # A closed on the 10th; B is withdrawn
    assert by["2026-11-09"]["closes"] == 0
    assert by["2026-11-10"]["close_records"] == 1
    assert by["2026-11-10"]["merges"] == 1 and by["2026-11-09"]["merges"] == 0
    assert meta["tickets"]["withdrawn"] == 1


def test_record_appends_one_line_with_rows_and_forecast_inputs(tmp_path, log):
    write(log / "usage.txt", "\n".join(usage_line(f"2026-11-10 {h:02d}:00:00", h) for h in range(24)) + "\n")
    out = tmp_path / "out"
    argv = ["--root", str(tmp_path), "--log", str(log), "--out", str(out)]
    assert mw.main(argv + ["record", "--since", "2026-11-10"]) == 0
    assert mw.main(argv + ["record", "--since", "2026-11-10", "--pct", "50", "--at", "2026-11-11 00:00",
                           "--reset", "2026-11-15 09:00", "--leads", "1,5"]) == 0
    lines = (out / "week.jsonl").read_text().splitlines()
    assert len(lines) == 2
    rec = json.loads(lines[1])
    assert "at" in rec and rec["daily"][0]["day"] == "2026-11-10"
    assert rec["forecast_inputs"]["pct"] == 50 and rec["forecast_inputs"]["leads"] == [1, 5]
    first = json.loads(lines[0])
    assert first["forecast_inputs"]["reset"] == "2026-11-15 09:00"     # read from the newest reading's text


def test_cli_daily_md_prints_a_markdown_table(tmp_path, log, capsys):
    write(log / "usage.txt", usage_line("2026-11-10 10:00:00", 5) + "\n" + usage_line("2026-11-10 11:00:00", 7) + "\n")
    rc = mw.main(["--root", str(tmp_path), "--log", str(log), "--out", str(tmp_path / "o"), "daily",
                  "--since", "2026-11-10", "--md"])
    out = capsys.readouterr().out
    assert rc == 0
    assert out.startswith("| day | pts |") and "|---|" in out and "2026-11-10" in out
