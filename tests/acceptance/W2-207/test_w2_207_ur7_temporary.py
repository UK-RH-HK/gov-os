"""UR-7: transcripts of temporary folders are left out of the repository rows and counted on one `temporary` line.

Temporary: cwd under /tmp/ or /var/tmp/ and (it does not exist, or it holds no .git).
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import pytest

import w2_207_support as s

DAY = "2026-11-24"


@pytest.fixture
def tmpdirs():
    made = []

    def make(git):
        d = Path(tempfile.mkdtemp(dir="/tmp", prefix="ur7-"))
        made.append(d)
        if git:
            (d / ".git").mkdir()
        return d

    yield make
    for d in made:
        shutil.rmtree(d, ignore_errors=True)


def plant(env, tmpdirs):
    real = env.git_repo("real")
    env.launch(real, "R1", "engineer")
    env.transcript(real, "R1", [env.msg(real, "R1", "r1", s.ts(DAY), "m-a", 1000000, 0, 0, 0)])  # 10.0
    gone = Path("/tmp/ur7-never-existed-xyz")
    assert not gone.exists()
    vgone = Path("/var/tmp/ur7-never-existed-xyz")
    plain = tmpdirs(git=False)
    env.transcript(gone, "T1", [env.msg(gone, "T1", "t1", s.ts(DAY), "m-a", 100000, 0, 0, 0)])  # 1.0
    env.transcript(vgone, "T2", [env.msg(vgone, "T2", "t2", s.ts(DAY), "m-a", 200000, 0, 0, 0)])  # 2.0
    env.transcript(plain, "T3", [env.msg(plain, "T3", "t3", s.ts(DAY), "m-a", 300000, 0, 0, 0)])  # 3.0
    return real, [gone, vgone, plain]


def test_ur7_temporary_transcripts_are_counted_on_one_line_of_the_record(env, tmpdirs):
    real, temps = plant(env, tmpdirs)
    r = env.daily(DAY)
    assert r.returncode == 0, r.stdout + r.stderr
    rec = env.record(DAY)
    assert rec["temporary"]["sessions"] == 3
    assert abs(rec["temporary"]["cost_usd"] - 6.0) < 1e-6
    assert {x["session"] for x in rec["rows"]} == {"R1"}
    assert set(rec["totals"]["by_repository"]) == {str(real)}
    s.assert_totals_match(rec)
    for t in temps:
        assert str(t) not in str(rec["rows"]) + str(rec["totals"])


def test_ur7_a_git_repository_under_tmp_stays_a_repository_row(env, tmpdirs):
    repo = tmpdirs(git=True)
    env.transcript(repo, "G1", [env.msg(repo, "G1", "g1", s.ts(DAY), "m-a", 1000000, 0, 0, 0)])
    assert env.daily(DAY).returncode == 0
    rec = env.record(DAY)
    assert [x["repository"] for x in rec["rows"]] == [str(repo)]
    assert set(rec["totals"]["by_repository"]) == {str(repo)}
    assert rec["temporary"]["sessions"] == 0


def test_ur7_show_prints_one_temporary_line_and_no_temporary_repository(env, tmpdirs):
    real, temps = plant(env, tmpdirs)
    assert env.daily(DAY).returncode == 0
    r = env.run("show", "--date", DAY)
    assert r.returncode == 0, r.stdout + r.stderr
    assert len([ln for ln in r.stdout.splitlines() if "temporary" in ln.lower()]) == 1, r.stdout
    assert "real" in r.stdout
    for t in temps:
        assert str(t) not in r.stdout and t.name not in r.stdout
