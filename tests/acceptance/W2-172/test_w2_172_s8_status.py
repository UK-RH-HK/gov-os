"""S8: a retrieval change waits for the next audit and is never measured by a separate run (Interface item 11).

``python3 -m gov.memaudit status --sets-root <root> --since <commit>``: the last retrieval change ``L`` is ``git log -1
--format=%H <since>..<main line> -- <the six globs>`` in ``--repo``. No ``L``: ``audited`` (exit 0). ``audited`` (exit 0)
when some ``HISTORY.jsonl`` line with ``measured: true`` has a commit ``A`` with ``L`` an ancestor of ``A`` (or ``A``
itself); otherwise ``not audited, next due <yyyy-mm-dd>`` (exit 1). The repository planted (``w2_172_git.status_repo``):
``B`` (base), ``x1`` (a retrieval path), ``x2`` (docs), ``x3`` (the path map: a retrieval path), ``x4`` (docs), all on
``main``. A release cut reads ``status``; nothing here starts an audit.
"""

from __future__ import annotations

import re

import pytest

import w2_172_git as G

NOT_AUDITED = re.compile(r"not audited, next due \d{4}-\d{2}-\d{2}")


@pytest.fixture
def w(tmp_path):
    return G.status_repo(tmp_path / "w")


def audited(run):
    assert run.code == 0 and run.lines == ["audited"], run


def not_audited(run):
    assert run.code == 1 and len(run.lines) == 1 and NOT_AUDITED.fullmatch(run.lines[0]), run


def test_s8_a_measured_audit_after_the_last_retrieval_change_is_audited(w):
    w.plant_history(G.measured_line(w.x4))  # before: the change x3 is behind the audit's commit x4
    audited(w.status(w.b))


def test_s8_a_measured_audit_at_the_last_retrieval_change_is_audited(w):
    w.plant_history(G.measured_line(w.x3))
    audited(w.status(w.b))


def test_s8_a_measured_audit_before_the_last_retrieval_change_is_not_audited(w):
    w.plant_history(G.measured_line(w.x2))  # after: x3 came later
    not_audited(w.status(w.b))


def test_s8_an_audit_that_was_not_measured_does_not_count(w):
    w.plant_history(G.measured_line(w.x4, measured=False))
    not_audited(w.status(w.b))


def test_s8_no_audit_at_all_is_not_audited(w):
    not_audited(w.status(w.b))


def test_s8_some_line_is_enough(w):
    w.plant_history(G.measured_line(w.x2), G.measured_line(w.x4))
    audited(w.status(w.b))


def test_s8_the_last_change_is_the_latest_of_the_six_globs_since_the_commit(w):
    w.plant_history(G.measured_line(w.x2))
    audited(w.status(w.x3))  # since x3: nothing changed after it that a retrieval path holds (x4 is docs)
    not_audited(w.status(w.x1))  # since x1: x3 is the last, and x2 is before it


def test_s8_no_retrieval_change_since_the_commit_is_audited_whatever_the_history(w):
    audited(w.status(w.x3))  # no audit planted: nothing to wait for
    audited(w.status(w.x4))


@pytest.mark.parametrize("path", G.RETR)
def test_s8_each_of_the_six_globs_is_a_retrieval_path(tmp_path, path):
    w = G.due_repo(tmp_path / "w")
    after = w.commit({path: "changed after the audit\n"}, "2026-11-11T00:00:00+00:00", "retrieval change")
    w.plant_history(G.measured_line(w.l0))
    not_audited(w.status(w.l0))
    w.plant_history(G.measured_line(after))
    audited(w.status(w.l0))


def test_s8_a_change_to_a_path_outside_the_six_globs_is_not_a_retrieval_change(tmp_path):
    w = G.due_repo(tmp_path / "w")
    w.commit({"docs/p000.md": "changed\n", "src/gov/other/x.py": "# x\n", "fixtures/evaluation/e0.md": "e\n"},
             "2026-11-11T00:00:00+00:00", "docs only")
    audited(w.status(w.l0))


def test_s8_status_writes_nothing_and_starts_no_audit(w):
    before = {p: p.read_bytes() for p in w.repo.rglob("*") if p.is_file() and ".git" not in p.parts}
    w.plant_history(G.measured_line(w.x2))
    not_audited(w.status(w.b))
    assert not (w.mem / "STARTS.log").exists(), "a release cut's reading starts nothing"
    assert before == {p: p.read_bytes() for p in w.repo.rglob("*") if p.is_file() and ".git" not in p.parts}


def test_s8_since_is_required(w):
    assert w.drive("status", "--help").code == 0, "the subcommand exists"
    assert w.drive("status", "--sets-root", str(w.sets), "--repo", str(w.repo)).code == 4
