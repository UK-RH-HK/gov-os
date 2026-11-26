"""EL-1: the level computed from stated facts, by ``gov decisions level``, cell by cell."""
from __future__ import annotations

import re

import pytest

import w2_211_support as S


@pytest.fixture(scope="module")
def root(tmp_path_factory):
    env = S.make_env(S.make_home(tmp_path_factory.mktemp("h")))
    return S.init_repo(tmp_path_factory.mktemp("lvl"), env, "lvl"), env


def level(root_env, touches, rev, inside, *flags):
    repo, env = root_env
    return S.gov(["decisions", "level", "--touches", touches, "--reversible", rev, "--inside", inside, *flags,
                  "--root", repo], env=env, cwd=repo)


def _level_of(run):
    m = re.search(r"(?m)^level: (P1|P2|P3|emergency)\b(.*)$", run.out)
    assert m, f"no `level: ...` line (exit {run.code}): {run.both[-500:]}"
    return m.group(1), m.group(2)


TOUCH_P1 = ["spec", "kpi", "standing-decision", "contract", "charter", "secret", "paid-service", "model-effort",
            "release"]
TOUCH_P2 = ["shared-code", "cross-stream", "kernel-text"]
TABLE = ([(w, "yes", "worktree", "P1") for w in TOUCH_P1] + [(w, "yes", "worktree", "P2") for w in TOUCH_P2]
         + [("own-ticket", "yes", "worktree", "P3"), ("own-ticket", "yes", "repository", "P2"),
            ("own-ticket", "yes", "outside", "P2"), ("own-ticket", "no", "worktree", "P2"),
            ("own-ticket", "no", "repository", "P1"), ("own-ticket", "no", "outside", "P1"),
            ("shared-code", "no", "repository", "P1"), ("shared-code", "yes", "outside", "P2"),
            ("spec", "yes", "worktree", "P1"), ("spec,own-ticket", "yes", "worktree", "P1"),
            ("own-ticket,shared-code", "yes", "worktree", "P2"), ("own-ticket,kernel-text", "no", "worktree", "P2")])


@pytest.mark.parametrize("touches,rev,inside,expected", TABLE,
                         ids=[f"{t}-{r}-{i}" for t, r, i, _ in TABLE])
def test_level_table_cell(root, touches, rev, inside, expected):
    run = level(root, touches, rev, inside)
    assert run.code == 0, run.both[-400:]
    got, facts = _level_of(run)
    assert got == expected, f"{touches}/{rev}/{inside}: expected {expected}, got {got}"
    for word in touches.split(","):
        assert word in run.out
    assert f"reversible {rev}" in run.out and f"inside {inside}" in run.out


def test_the_printed_line_is_the_levels_and_the_facts_that_set_it(root):
    run = level(root, "spec", "yes", "worktree")
    assert "level: P1 (touches spec; reversible yes; inside worktree)" in run.out, run.out


@pytest.mark.parametrize("flags,expected", [(["--spends"], "P1"), (["--rounds", "3"], "P1"), (["--rounds", "5"], "P1"),
                                            (["--rounds", "2"], "P3"), (["--emergency"], "emergency")])
def test_spends_rounds_and_emergency(root, flags, expected):
    got, _ = _level_of(level(root, "own-ticket", "yes", "worktree", *flags))
    assert got == expected, flags


def test_a_package_path_in_place_of_flags_reads_its_frontmatter(root, tmp_path):
    repo, env = root
    p = S.write(tmp_path / "DP-0001.md", S.package_text("DP-0001", touches=["kernel-text"], reversible="no",
                                                         inside="worktree"))
    run = S.gov(["decisions", "level", str(p), "--root", repo], env=env, cwd=repo)
    got, _ = _level_of(run)
    assert got == "P2" and "kernel-text" in run.out, run.both[-400:]


@pytest.mark.parametrize("args", [["--touches", "nonsense", "--reversible", "yes", "--inside", "worktree"],
                                  ["--touches", "spec", "--reversible", "maybe", "--inside", "worktree"],
                                  ["--touches", "spec", "--reversible", "yes", "--inside", "moon"]])
def test_an_unknown_word_exits_1_level_fact_invalid(root, args):
    repo, env = root
    run = S.gov(["decisions", "level", *args, "--root", repo], env=env, cwd=repo)
    assert run.code == 1 and "LEVEL_FACT_INVALID" in run.both, run.both[-400:]
