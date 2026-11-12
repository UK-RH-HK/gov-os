"""The driver's pieces the acceptance suite reaches only end to end (W2-172): the churn of a commit, the mode rule, the USED
boundary by step and exit, the digest's twelve lines and the figures reader. Planted repositories under ``tmp_path``."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from gov.memaudit import digest, driver, schedule

T0 = datetime(2026, 11, 12, 12, 0, tzinfo=timezone.utc)


def _git(repo, *args, when=None):
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           "PATH": "/usr/bin:/bin"}
    if when:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = when
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=env, check=True)
    return done.stdout.strip()


def _commit(repo, files, when, msg="c"):
    for name, text in files.items():
        p = Path(repo) / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", msg, when=when)
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q", "-b", "main")
    base = {f"docs/f{i}.md": "x" for i in range(30)}
    base["governance/project/indep-walls/tree-exclude.txt"] = "# walls\nfixtures/**\n"
    base["fixtures/a.txt"] = "x"
    base["fixtures/b.txt"] = "x"
    _commit(r, base, "2026-09-01T00:00:00+00:00", "base")
    _commit(r, {"docs/f0.md": "y"}, "2026-10-01T00:00:00+00:00", "one change: the head's churn is 1 of 31")
    return r


def test_churn_is_the_share_of_tracked_paths_changed_in_28_days_less_the_excluded(repo):
    # 31 tracked paths after the exclusion (30 docs and the tree-exclude file); two docs change inside the window
    x = _commit(repo, {"docs/f0.md": "z", "docs/f1.md": "y", "fixtures/a.txt": "y"}, "2026-11-01T00:00:00+00:00")
    churn, retrieval = schedule.churn_at(repo, x)
    assert churn == round(2 / 31, 4) and retrieval is False


def test_a_change_older_than_28_days_does_not_count_and_a_retrieval_path_does(repo):
    _commit(repo, {"docs/f2.md": "y"}, "2026-10-02T00:00:00+00:00")
    x = _commit(repo, {"src/gov/store/s.py": "y"}, "2026-11-01T00:00:00+00:00")
    churn, retrieval = schedule.churn_at(repo, x)
    assert churn == round(1 / 32, 4) and retrieval is True
    assert schedule.retrieval_changed(repo, None, x) == []


def _history(runs, rows):
    folder = schedule.folder(runs)
    folder.mkdir(parents=True)
    (folder / "HISTORY.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))


def _line(commit, **kw):
    return {"audit": "a", "commit": commit, "at": "2026-10-01T00:00:00Z", "mode": "weekly", "churn": 0.01,
            "retrieval_28d": False, "passes": True, "pool_regression": False, "measured": True, "used": True} | kw


def test_the_mode_is_weekly_until_three_measured_audits_and_monthly_when_they_were_calm(repo, tmp_path):
    runs = tmp_path / "runs"
    head = _git(repo, "rev-parse", "HEAD")
    _history(runs, [_line(head), _line(head)])
    assert schedule.decide(repo, runs, head, T0)["reason"] == "start"
    _history_more = [_line(head)] * 3
    (schedule.folder(runs) / "HISTORY.jsonl").write_text("".join(json.dumps(r) + "\n" for r in _history_more))
    got = schedule.decide(repo, runs, head, T0)
    assert (got["mode"], got["reason"]) == ("monthly", "stable")


@pytest.mark.parametrize("change,reason", [({"passes": False}, "verdict"), ({"pool_regression": True}, "pool")])
def test_a_last_verdict_below_the_bar_or_a_pool_regression_sends_it_back_to_weekly(repo, tmp_path, change, reason):
    runs, head = tmp_path / "runs", _git(repo, "rev-parse", "HEAD")
    _history(runs, [_line(head), _line(head), _line(head, **change)])
    got = schedule.decide(repo, runs, head, T0)
    assert (got["mode"], got["reason"]) == ("weekly", reason)


def test_a_retrieval_change_since_the_last_audit_sends_it_back_to_weekly(repo, tmp_path):
    runs, audited = tmp_path / "runs", _git(repo, "rev-parse", "HEAD")
    _history(runs, [_line(audited)] * 3)
    head = _commit(repo, {"src/gov/codeintel/z.py": "y"}, "2026-11-10T00:00:00+00:00")
    got = schedule.decide(repo, runs, head, T0)
    assert (got["mode"], got["reason"]) == ("weekly", "retrieval")


def test_due_is_six_days_when_weekly_and_twenty_eight_when_monthly(repo, tmp_path):
    runs, head = tmp_path / "runs", _git(repo, "rev-parse", "HEAD")
    folder = schedule.folder(runs)
    folder.mkdir(parents=True)

    def due_after(days):
        at = (T0 - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        (folder / "STARTS.log").write_text(json.dumps({"audit": "a", "at": at}) + "\n")
        return schedule.decide(repo, runs, head, T0)

    assert [due_after(d)["due"] for d in (5, 6)] == [False, True]
    (folder / "HISTORY.jsonl").write_text("".join(json.dumps(_line(head)) + "\n" for _ in range(3)))
    assert [due_after(d)["due"] for d in (27, 28)] == [False, True]
    assert due_after(27)["mode"] == "monthly" and due_after(27)["next"] == "2026-11-13"
    (folder / "STARTS.log").unlink()
    assert schedule.decide(repo, runs, head, T0)["due"] is True  # no start yet: due


def test_the_used_boundary_is_known_from_the_step_and_its_exit():
    assert [driver._used(s, 2, False) for s in ("writer-1", "preflight", "checker-1", "void")] == [False] * 4
    assert driver._used("measure", 1, False) is False and driver._used("measure", 4, False) is False
    assert [driver._used("measure", c, False) for c in (0, 2, 3)] == [True] * 3
    assert driver._used("measure", 2, True) is False  # the gate is shut before measure starts
    assert all(driver._used(s, 1, False) for s in ("judge", "auditor", "classes", "pool", "figures"))
    assert driver._used("judge", 2, True) is True


FIG = {"n": 20, "n_gold": 18, "verdict": {"right": 15, "wrong": 1, "passes": True, "interval_exact": [0.5, 0.9]},
       "bar": {"need_right": 14, "max_wrong": 2, "target_right": 16}, "hit5": 12, "in_bundle": 14,
       "by_rank": {"rank_1_5": 1, "rank_6_20": 2, "not_in_20": 3}, "by_namespace": {"embedded": 4, "keyword_only": 2},
       "classes": dict.fromkeys(digest.CLASSES, 1),
       "pool": {"n": 400, "hit5": 300, "full": 200, "last_hit5": None, "last_full": None, "regression": False},
       "kept": 20, "dropped": 3, "by_code": {"AMBIG": 2, "DUP": 1}}


def _state(**kw):
    return {"audit": "memory-audit-20261112", "commit": "a" * 40, "mode": "weekly", "reason": "start", "figures": FIG,
            "retrieval": ["src/gov/store/x.py"], "cost": {"writer-1": 0.5, "judge": 1.25}, "next": "2026-11-18",
            "next_mode": "weekly", "stop": None, "refused": None} | kw


SCHEMA = [r"AUDIT memory-audit-\d{8} commit [0-9a-f]{12}", r"MODE (weekly|monthly) reason [a-z]+",
          r"VERDICT right \d+ of \d+; wrong \d+; exact \d+\.\d to \d+\.\d %; bar \d+ right, \d+ wrong: (passes|misses)",
          r"HIT5 \d+ of \d+; first bundle \d+",
          r"MISSES class gold_wrong \d+ question_ambiguous \d+ out_of_scope \d+ retrieval_miss \d+ answer_wrong \d+; "
          r"rank 1-5 \d+ 6-20 \d+ none \d+; namespace embedded \d+ keyword_only \d+",
          r"POOL hit5 \d+ of \d+ last (\d+|none); full \d+ last (\d+|none); regression (yes|no)",
          r"RETRIEVAL changed \d+(: \S+( \S+)*)?", r"QUESTIONS kept \d+ dropped \d+(; \S+ \d+( \S+ \d+)*)?",
          r"COST (\S+ \d+\.\d\d )*total \d+\.\d\d", r"NEXT due \d{4}-\d\d-\d\d (weekly|monthly)",
          r"STOP (none|\S+ exit \d+)|REFUSED RN-[A-Z]+", r"OWNER none|OWNER stopped after USED at \S+ exit \d+: .*"]


def test_the_digest_is_twelve_lines_in_order_each_matching_its_expression():
    block = digest.lines(_state())
    assert len(block) == 12
    for line, rx in zip(block, SCHEMA):
        assert re.fullmatch(rx, line), line
    assert block[7] == "QUESTIONS kept 20 dropped 3; AMBIG 2 DUP 1"
    assert block[6] == "RETRIEVAL changed 1: src/gov/store/x.py"
    assert block[8] == "COST writer-1 0.50 judge 1.25 total 1.75"


def test_a_figure_not_reached_prints_its_word_and_a_stop_after_used_names_the_owner_line():
    block = digest.lines(_state(figures=None, cost={}, retrieval=[],
                                stop={"step": "judge", "exit": 2, "used": True}))
    assert [x for x in block if x.endswith("not reached")] == [
        "VERDICT not reached", "HIT5 not reached", "MISSES not reached", "POOL not reached",
        "QUESTIONS not reached", "COST not reached"]
    assert block[6] == "RETRIEVAL changed 0"
    assert block[10] == "STOP judge exit 2"
    assert block[11] == "OWNER stopped after USED at judge exit 2: the set is not run again"
    assert digest.lines(_state(refused="RN-LOCK"))[10] == "REFUSED RN-LOCK"


def test_figures_gives_null_for_a_missing_file_and_exits_ok(tmp_path):
    (tmp_path / "runs" / "memory-audit-20261112").mkdir(parents=True)
    said = []
    assert digest.figures(str(tmp_path), "memory-audit-20261112", said.append) == "ok"
    line = json.loads(said[0])
    assert line["verdict"] is None and line["kept"] is None and line["pool"] is None
