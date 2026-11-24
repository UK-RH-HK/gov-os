"""UR-3: `gov usage show` in one screen."""

from __future__ import annotations

import re

import w2_207_support as s

DAY = "2026-11-24"


def plant(env):
    """alpha: engineer $60, reviewer $20, qa $10, scout $5 (95 in all); beta: engineer $5. Rate: $20 per 1M output."""
    a, b = env.repo("alpha"), env.repo("beta")
    m = env.msg
    for sess, role, out in (("s-alpha-eng", "engineer", 3_000_000), ("s-alpha-rev", "reviewer", 1_000_000),
                            ("s-alpha-qa", "qa", 500_000), ("s-alpha-scout", "scout", 250_000)):
        env.launch(a, sess, role)
        env.transcript(a, sess, [m(a, sess, "x1", s.ts(DAY), "m-a", 0, out, 0, 0)])
    env.launch(b, "s-beta-eng", "engineer")
    env.transcript(b, "s-beta-eng", [m(b, "s-beta-eng", "y1", s.ts(DAY), "m-a", 0, 250_000, 0, 0)])
    env.usage_txt([f"{DAY} 18:28:37 week (all models)=19% (resets Nov 29, 9am (Europe/London))"])
    return a, b


def repo_line(out, name):
    lines = [l for l in out.splitlines() if name in l and "$" in l and "%" in l]
    assert lines, out
    return lines[0]


def test_ur3_show_a_day_prints_cost_share_top_three_roles_largest_session_and_plan_reading(env):
    plant(env)
    assert env.daily(DAY).returncode == 0
    r = env.run("show", "--date", DAY)
    assert r.returncode == 0, r.stdout + r.stderr
    out = r.stdout
    assert "week (all models)=19%" in out
    la, lb = repo_line(out, "alpha"), repo_line(out, "beta")
    assert "$95.00" in la and "95%" in la
    assert "$5.00" in lb and "5%" in lb
    shares = [int(re.search(r"(\d+)%", l).group(1)) for l in (la, lb)]
    assert abs(sum(shares) - 100) <= 1
    assert "top roles:" in out
    assert "engineer $60.00" in out and "reviewer $20.00" in out and "qa $10.00" in out
    assert "scout" not in out  # the fourth role is trimmed
    assert "largest session:" in out
    assert "s-alpha-eng" in out


def test_ur3_show_n_days_prints_one_line_per_day_per_repository_and_writes_nothing(env):
    a, b = plant(env)
    a_old = "2026-11-22"
    env.launch(a, "s-old", "engineer")
    env.transcript(a, "s-old", [env.msg(a, "s-old", "z1", s.ts(a_old), "m-a", 0, 1_000_000, 0, 0)])
    assert env.daily(DAY).returncode == 0
    r = env.run("show", "--date", DAY, "--days", "3")
    assert r.returncode == 0, r.stdout + r.stderr
    out = r.stdout
    assert re.search(r"2026-11-22\s+\S*alpha\S*\s+\$20\.00\s+100%", out), out
    assert re.search(r"2026-11-24\s+\S*alpha\S*\s+\$95\.00\s+95%", out), out
    assert re.search(r"2026-11-24\s+\S*beta\S*\s+\$5\.00\s+5%", out), out
    assert not re.search(r"2026-11-23\s+\S+\s+\$", out)  # a day with no sessions has no line
    assert not (env.usage_dir / "2026-11-22.json").exists()  # computed in memory, never written
