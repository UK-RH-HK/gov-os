"""S6: the baseline (Interface item 10).

``python3 -m gov.memaudit baseline --sets-root <root> --commit <rev>`` appends ``{"time","commit","run":"baseline",
"audit":"baseline"}`` to ``<runs>/indep/AUDITS.log`` (the launch script's line form: its ``last_audit`` reads the last
line's ``commit``), prints ``BASELINE <12 hex>`` and exits 0. It refuses with exit 1 and writes nothing: ``BL-COMMIT`` when
the commit does not resolve (``git rev-parse --verify <rev>^{commit}``) in ``--repo``, ``BL-EXISTS`` when the log holds any
line. The runs folder is ``$GOV_INDEP_RUNS_DIR`` (planted).
"""

from __future__ import annotations

import importlib.util
import json
from datetime import datetime

import pytest

import w2_172_checks as C
import w2_172_git as G
import w2_172_world as W

LAUNCH = W.TREE / "governance" / "project" / "orchestration" / "tools" / "indep_launch.py"


@pytest.fixture
def repo(tmp_path):
    w = G.status_repo(tmp_path / "w")
    w.audits_log.unlink(missing_ok=True)
    return w


def log_lines(w):
    return [x for x in w.audits_log.read_text().splitlines() if x.strip()] if w.audits_log.exists() else []


def test_s6_an_empty_log_takes_one_line_in_the_launch_scripts_form(repo):
    sha = repo.x2
    run = repo.baseline(sha[:12])
    assert run.code == 0 and run.lines == [f"BASELINE {sha[:12]}"], run
    lines = log_lines(repo)
    assert len(lines) == 1
    line = json.loads(lines[0])
    assert set(line) == {"time", "commit", "run", "audit"}, line
    assert line["commit"] == sha, "the full 40 hex digits of the resolved commit"
    assert line["run"] == "baseline" and line["audit"] == "baseline"
    assert datetime.fromisoformat(line["time"].replace("Z", "+00:00"))


def test_s6_a_log_present_but_empty_is_empty(repo):
    repo.audits_log.write_text("")
    run = repo.baseline("main~1")
    assert run.code == 0 and run.lines == [f"BASELINE {repo.x3[:12]}"], run
    assert json.loads(log_lines(repo)[0])["commit"] == repo.x3, "a revision is resolved in --repo"


def test_s6_the_first_audits_changed_list_starts_at_the_baseline_commit(repo):
    """The launch script's ``last_audit`` reads the last line's commit: the first audit starts there."""
    spec = importlib.util.spec_from_file_location("indep_launch_under_test", LAUNCH)
    launch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(launch)
    assert launch.last_audit(str(repo.runs / "indep")) is None
    assert repo.baseline(repo.x1).code == 0
    assert launch.last_audit(str(repo.runs / "indep")) == repo.x1


def test_s6_a_second_baseline_while_an_audit_line_exists_is_refused_and_writes_nothing(repo):
    assert repo.baseline(repo.x1).code == 0
    before = repo.audits_log.read_bytes()
    run = repo.baseline(repo.x3)
    assert run.code == 1 and run.lines == ["BL-EXISTS"], run
    assert repo.audits_log.read_bytes() == before


def test_s6_a_line_written_by_an_audit_is_a_line_too(repo):
    repo.plant_audits({"time": "2026-11-02T00:00:00Z", "commit": repo.x1, "run": "20261102T000000Z-auditor-r1",
                       "audit": "memory-audit-20261102"})
    before = repo.audits_log.read_bytes()
    run = repo.baseline(repo.x3)
    assert run.code == 1 and run.lines == ["BL-EXISTS"], run
    assert repo.audits_log.read_bytes() == before


@pytest.mark.parametrize("rev", ["0123456789abcdef0123456789abcdef01234567", "no-such-revision", "HEAD^{tree}"])
def test_s6_a_commit_not_in_the_repository_is_refused_and_nothing_is_written(repo, rev):
    run = repo.baseline(rev)
    assert run.code == 1 and run.lines == ["BL-COMMIT"], run
    assert not repo.audits_log.exists(), "nothing written: not even an empty log"


def test_s6_the_commit_flag_is_required(repo):
    assert repo.drive("baseline", "--help").code == 0, "the subcommand exists"
    run = repo.drive("baseline", "--sets-root", str(repo.sets), "--repo", str(repo.repo))
    assert run.code == 4, run
    assert not repo.audits_log.exists()


def test_s6_run_refuses_rn_nobase_until_a_baseline_is_written(make_world):
    world = make_world()
    world.audits_log.unlink()
    world.plan_launch({"writer-1": [{"exit": 10}]})
    C.refused_without_a_start(world, world.go(), "RN-NOBASE")
    import shutil
    shutil.rmtree(world.audit_dir, ignore_errors=True)
    assert world.baseline(world.base_commit).code == 0
    run = world.go()
    assert run.code == 2 and "STOPPED writer-1 10" in run.lines, "RN-NOBASE no longer refuses"
    assert world.audits()[-1]["commit"] == world.base_commit
