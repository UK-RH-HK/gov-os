"""KPI 4 and the "not done" line (DEC-969, DEC-968 item 3).

- W2-54's time limits are not raised and its tests are not changed (failure line 4): no commit of this ticket
  touches W2-54's tests or the context check's declaration, nothing there is changed and uncommitted, and the
  declared limit is not above 600 s.
- The measure itself (the context check timed before and after) is the engineer's research record, not an
  acceptance test: this file checks only that the record exists and names the loads, the time in the freshness
  checks and in query embedding, and the batching verdict.
"""

from __future__ import annotations

import re
import subprocess

import pytest
import yaml

import w2_108_support as S

TASK = "DAEO-zoex"
W2_54_TESTS = "tests/acceptance/W2-54"
DECLARATIONS = ("template/governance/kernel/checks/context-reproducibility.yaml",
                "governance/kernel/checks/context-reproducibility.yaml")
LIMIT_FIELD = "timeout-seconds"
W2_54_LIMIT_S = 600       # DEC-969: "the time limit is not raised"; the target is under W2-54's 600 s
RECORD_REL = "docs/research/W2-108-freshness-once.md"
ORDINARY_LOAD_MIN = 40    # KPI 4: two loads, one of them 40 or more


def git_out(*args):
    done = subprocess.run(["git", "-C", str(S.REPO_ROOT), *args], capture_output=True, text=True)
    assert done.returncode == 0, f"git {' '.join(args)}: {done.stderr}"
    return done.stdout


def test_w2_54_is_not_changed_by_this_ticket():
    if not (S.REPO_ROOT / ".git").exists():
        pytest.skip(f"{S.REPO_ROOT} has no .git: this ticket's history cannot be read there")
    paths = [W2_54_TESTS, *DECLARATIONS]
    commits = git_out("log", "--no-merges", "--format=%h %s", f"--grep=^Task: {TASK}$", "--", *paths).strip()
    assert not commits, f"commits of {TASK} change W2-54's tests or the context check's limit:\n{commits}"
    pending = git_out("status", "--porcelain", "--", *paths).strip()
    assert not pending, f"W2-54's tests or the context check's declaration are changed in the working tree:\n{pending}"


def test_the_context_checks_limit_is_not_raised():
    declared = [rel for rel in DECLARATIONS if (S.REPO_ROOT / rel).is_file()]
    assert declared, f"no declaration of the context check at {DECLARATIONS}"
    for rel in declared:
        limit = yaml.safe_load((S.REPO_ROOT / rel).read_text(encoding="utf-8")).get(LIMIT_FIELD)
        assert isinstance(limit, (int, float)) and limit <= W2_54_LIMIT_S, \
            f"{rel}: {LIMIT_FIELD} is {limit!r}, above W2-54's {W2_54_LIMIT_S} s (DEC-969: not raised)"


def test_the_research_record_names_the_measure():
    path = S.REPO_ROOT / RECORD_REL
    assert path.is_file(), f"{RECORD_REL} does not exist: KPI 4's measure is recorded there (DEC-969)"
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    missing = [word for word in ("freshness", "embedding", "batch", "load") if word not in lower]
    assert not missing, f"{RECORD_REL} does not name: {missing}"
    loads = {int(number) for number in re.findall(r"load[^0-9\n]{0,30}(\d+)", lower)}
    assert len(loads) >= 2 and max(loads) >= ORDINARY_LOAD_MIN, (
        f"{RECORD_REL} names the loads {sorted(loads)}: KPI 4 asks for two loads, one of them "
        f"{ORDINARY_LOAD_MIN} or more")
    assert re.search(r"\d+(\.\d+)?\s*s\b", text), f"{RECORD_REL} gives no time in seconds"
