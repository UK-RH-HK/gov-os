"""KPI success 2 and failure 2: the context-reproducibility declaration states a time limit that fits its
measured run and does not hide a hang; a check past its declared limit still fails; no hard-block check is
weakened [DEC-768, DEC-595, DEC-600].

Red reasons, today: the declaration states no ``timeout-seconds`` (so the check gets the runner's 60 seconds,
DEC-595), and ``docs/changes/W2-54-CIT-E.md`` does not exist. The failure-line cases pass today; they hold what
the fix must keep.
"""

from __future__ import annotations

import re

import pytest
import yaml

import w2_54_support as S

KEPT_KEYS = ("id", "family", "tier", "severity", "command", "enforces")


def _declared():
    return (S.REPO_ROOT / S.CONTEXT_DECLARATION_REL).read_text(encoding="utf-8")


def test_only_the_timeout_line_is_added_to_the_declaration():
    """*Red.* Against the declaration before this ticket (``b644d28a``), exactly one line is added, a
    ``timeout-seconds: <whole number>`` line, and no line is changed or removed."""
    before = S.show(S.BASE_COMMIT, S.CONTEXT_DECLARATION_REL).decode("utf-8").splitlines()
    after = _declared().splitlines()
    added = list(after)
    for line in before:
        assert line in added, f"the line {line!r} of the declaration is changed or removed"
        added.remove(line)
    assert [line for line in after if line not in added] == before, "the declaration's lines are reordered"
    assert len(added) == 1 and re.fullmatch(r"timeout-seconds: [1-9][0-9]*", added[0]), \
        f"the declaration should add one `timeout-seconds: <seconds>` line and nothing else; it adds {added}"


def test_the_declaration_s_other_keys_are_unchanged():
    """``id``, ``family``, ``tier``, ``severity: hard-block``, ``command`` and ``enforces`` are as they were
    (DEC-768 item 4). Passes today."""
    before = yaml.safe_load(S.show(S.BASE_COMMIT, S.CONTEXT_DECLARATION_REL))
    after = yaml.safe_load(_declared())
    assert after.get("severity") == "hard-block"
    assert {key: after.get(key) for key in KEPT_KEYS} == {key: before.get(key) for key in KEPT_KEYS}
    assert set(after) - set(before) <= {S.TIMEOUT_FIELD}, f"keys added beyond the time limit: {set(after) - set(before)}"


def test_the_declared_limit_is_above_the_runner_s_and_bounded():
    """*Red.* The declaration states a positive whole number of seconds (DEC-600), above the runner's 60
    (DEC-595: the measured run at ``c9537e39`` was 122 s) and at most 600 s, so that a hang is still caught
    (README, "The bound on the time limit")."""
    limit = S.limit_of(_declared())
    assert limit is not None, f"{S.CONTEXT_DECLARATION_REL} states no {S.TIMEOUT_FIELD}: the check gets the " \
                              f"runner's {S.RUNNER_DEFAULT_S} seconds"
    assert type(limit) is int and limit > S.RUNNER_DEFAULT_S, f"the declared limit {limit!r} does not exceed 60 s"
    assert limit <= S.LIMIT_BOUND_S, f"the declared limit {limit} s is above {S.LIMIT_BOUND_S} s: it would hide a hang"


def test_the_change_record_states_the_limit_and_its_measurement():
    """*Red.* ``docs/changes/W2-54-CIT-E.md`` records the change and the measurement: the declared limit, the
    run's seconds, the tickets measured and the machine's load."""
    path = S.REPO_ROOT / S.CHANGE_RECORD_REL
    assert path.is_file(), f"there is no change record {S.CHANGE_RECORD_REL}"
    text = path.read_text(encoding="utf-8")
    limit = S.limit_of(_declared())
    assert S.TIMEOUT_FIELD in text, f"the change record does not name {S.TIMEOUT_FIELD}"
    assert limit is not None and re.search(rf"\b{limit}\b", text), \
        f"the change record does not state the declared limit ({limit})"
    for word in ("seconds", "load", "ticket"):
        assert word in text.lower(), f"the change record does not state the measurement's {word!r}"


def test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit(code_under_test):
    """*Red.* Needs this worktree's store (about three minutes). The check's command, by ``sh -c`` in this
    worktree, ends with exit 0 within the declared limit. Today no limit is declared (and the run, 164 s at a
    load of 15 to 29 on 20 processors, fails on 13 tickets)."""
    limit = S.limit_of(_declared())
    assert limit is not None, f"{S.CONTEXT_DECLARATION_REL} states no {S.TIMEOUT_FIELD}"
    command = yaml.safe_load(_declared())["command"]
    done = S.run(["sh", "-c", command], cwd=S.REPO_ROOT, env=S.worktree_env(), timeout=max(limit, 1) + 30)
    assert done.seconds < limit, f"the check ran {done.seconds:.0f} s, past its declared limit of {limit} s"
    assert done.returncode == 0, f"the check is not green on this repository\n{done.describe()}"


# ---- failure line 2: a check past its declared limit still fails; nothing is weakened

def _project_with(box, path, command, limit):
    project = S.new_repo(path)
    S.write(project, f"{S.CHECKS_REL}/w254-timed.yaml", yaml.safe_dump(
        {"id": "w254-timed", "family": "w254-timed", "tier": "G1", "severity": "hard-block",
         "command": command, S.TIMEOUT_FIELD: limit}, sort_keys=False))
    S.commit_all(project)
    done = S.gov(box, "check", "--json", "--root", project)
    return done, S.checks_of(done.envelope())


def test_a_check_past_its_declared_limit_is_red(box, tmp_path):
    """Failure line 2. A hard-block check that runs past its declared two seconds is red, its finding says it
    did not end within its limit, and ``gov check`` does not pass. Passes today."""
    done, checks = _project_with(box, tmp_path / "slow", "python3 -c 'import time; time.sleep(30)'", 2)
    entry = checks.get("w254-timed")
    assert entry is not None, done.describe()
    assert entry["status"] == S.RED, f"a check past its declared limit is {entry['status']}\n{done.describe()}"
    assert "limit" in S.canonical(entry.get("findings")).lower(), entry
    assert done.returncode != 0 and done.envelope().get("ok") is False, done.describe()
    assert done.seconds < 25, f"gov check waited {done.seconds:.0f} s for a check whose limit is 2 s"


def test_the_same_check_within_its_limit_is_green(box, tmp_path):
    """The control of the case above: the same declaration, a command that ends at once, is green."""
    done, checks = _project_with(box, tmp_path / "quick", "python3 -c 'pass'", 2)
    assert checks["w254-timed"]["status"] == S.GREEN, done.describe()


def test_no_hard_block_check_is_weakened():
    """DEC-768 item 4: every check declaration is as it was before this ticket, byte for byte, but the context
    check's one added line; none is removed, added, downgraded or excluded. Passes today."""
    for folder in (S.CHECKS_REL, S.INSTALLED_CHECKS_REL):
        before = S.listed(S.BASE_COMMIT, folder)
        here = S.REPO_ROOT / folder
        after = sorted(path.name for path in here.glob("*.yaml")) if here.is_dir() else []
        assert after == [name for name in before if name.endswith(".yaml")], \
            f"{folder}: declarations added or removed: before {before}, after {after}"
        for name in after:
            rel = f"{folder}/{name}"
            if rel == S.CONTEXT_DECLARATION_REL:
                continue
            assert (S.REPO_ROOT / rel).read_bytes() == S.show(S.BASE_COMMIT, rel), f"{rel} is changed"


@pytest.mark.parametrize("rel", (S.CONTEXT_DECLARATION_REL, f"{S.CHECKS_REL}/core-schema.yaml"))
def test_the_two_checks_of_this_ticket_stay_hard_block(rel):
    """The context check and core-schema keep ``severity: hard-block``. Passes today."""
    assert yaml.safe_load((S.REPO_ROOT / rel).read_text(encoding="utf-8"))["severity"] == "hard-block"
