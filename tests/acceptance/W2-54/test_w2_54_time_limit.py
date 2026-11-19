"""KPI failure 2: a check past its declared limit still fails; no hard-block check is weakened [DEC-768, DEC-595,
DEC-600].

Success 2 (the context check's declared time limit and its change record) is retired with that check
(DEC-1214 M1, W2-200): its five cases are deleted. The failure-line cases stay; they hold what the fix must keep.
"""

from __future__ import annotations

import pytest
import yaml

import w2_54_support as S


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


# Rewrite-Reason: DEC-1045. The owner's decision to switch the secrets scan off by configuration on this repository
# (the feature stays built, on by default elsewhere) added, in ddcec657c278, exactly these three lines at the end of
# the secrets-indexing declaration, so that with ``scan: off`` the check answers not applicable (YELLOW, naming the
# switch). That change is accepted as DEC-1045's, and nothing else: the declaration must be its bytes at the base, or
# those bytes followed by these lines and no other; every other declaration stays byte for byte as at the base.
DECIDED_CHANGES = {
    f"{S.CHECKS_REL}/secrets-indexing.yaml": ("DEC-1045", (
        b"# With `scan: off` in governance/project/secrets.yaml (DEC-1045) the check answers not applicable, naming "
        b"the switch:\n"
        b"# YELLOW with that reason. Absent, the scan is on and the check is as above.\n"
        b'allows-not-applicable: "true"\n')),
}


# The owner's decided removals: a declaration retired by a decision, gone with what it checked (not weakened).
DECIDED_REMOVALS = {f"{S.CHECKS_REL}/context-reproducibility.yaml": "DEC-1214 M1"}   # retired by DEC-1214 M1


def test_no_hard_block_check_is_weakened():
    """DEC-768 item 4: every check declaration is as it was before this ticket, byte for byte; none is removed,
    added, downgraded or excluded. Passes today.

    Rewrite-Reason: DEC-1045: one declaration may also carry an owner's decided change, named in
    ``DECIDED_CHANGES`` with its exact lines appended to the base's bytes (the secrets-indexing check's
    ``allows-not-applicable``, DEC-1045). Any other change to it, or to any other declaration, still fails.

    Rewrite-Reason: DEC-1214 M1 (W2-200): the context check is retired with the context command, so its declaration
    is removed by decision (``DECIDED_REMOVALS``): the folder holds the base's declarations less that one, and no
    other is removed, added or changed. The exception that let the context check's one added line through is gone
    with it."""
    for folder in (S.CHECKS_REL, S.INSTALLED_CHECKS_REL):
        before = S.listed(S.BASE_COMMIT, folder)
        here = S.REPO_ROOT / folder
        after = sorted(path.name for path in here.glob("*.yaml")) if here.is_dir() else []
        kept = [name for name in before if name.endswith(".yaml") and f"{folder}/{name}" not in DECIDED_REMOVALS]
        assert after == kept, f"{folder}: declarations added or removed beyond the decided removals: " \
                              f"expected {kept}, found {after}"
        for name in after:
            rel = f"{folder}/{name}"
            base, now = S.show(S.BASE_COMMIT, rel), (S.REPO_ROOT / rel).read_bytes()
            if rel in DECIDED_CHANGES and now != base:
                decision, lines = DECIDED_CHANGES[rel]
                assert now == base + lines, \
                    f"{rel} is changed beyond {decision}'s lines (only those, appended to the base, are accepted)"
                continue
            assert now == base, f"{rel} is changed"


@pytest.mark.parametrize("rel", (f"{S.CHECKS_REL}/core-schema.yaml",))
def test_the_two_checks_of_this_ticket_stay_hard_block(rel):
    """Core-schema keeps ``severity: hard-block``. Passes today.

    Rewrite-Reason: DEC-1214 M1 (W2-200): the other of the two, the context check, is retired with the context
    command; its row is deleted and core-schema's stays."""
    assert yaml.safe_load((S.REPO_ROOT / rel).read_text(encoding="utf-8"))["severity"] == "hard-block"
