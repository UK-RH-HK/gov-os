"""S4: a hard-block key is covered only by a check of hard-block tier [W2-M211, W2-M259].

Interface items 1 and 6: the tier is the declaration's ``severity``. A path-map policy key of strength hard-block
whose covering declarations (``enforces``) are all warnings gives a result ``policy-<key>``, severity hard-block,
RED, with the finding ``POLICY_TIER_TOO_LOW`` (``policy``, ``checks`` the covering ids, a message naming the key);
"refused" is that RED result and ``gov check``'s non-zero exit. One hard-block declaration covering the key gives
no policy result. An uncovered key keeps ``POLICY_NOT_COVERED``.
"""

from __future__ import annotations

import w2_45_support as support
from w2_45_support import HARD_BLOCK, RED, WARNING

CLEAN = "import sys\nsys.exit(0)\n"
KEY = "security"


def planted(project, policies, declarations):
    """A project whose path map states ``policies`` and whose clean checks are ``declarations``:
    ``(id, severity, enforces)``."""
    project.path_map(policies)
    for check_id, severity, enforces in declarations:
        project.declare(check_id, project.script(check_id, CLEAN), severity=severity, enforces=enforces)
    project.commit_all("plant a check map")
    return project.check()


def policy_entry(run, key=KEY):
    return run.entry_or_none(f"policy-{key}")


def test_s4_hard_block_key_covered_only_by_a_warning_check_is_refused_naming_the_key(project):
    run = planted(project, {KEY: "hard-block"}, [("cover-warning", WARNING, [KEY])])
    entry = policy_entry(run)
    assert entry is not None, f"no policy-{KEY} result\n{run.describe()}"
    assert entry["severity"] == HARD_BLOCK, run.describe()
    assert entry["status"] == RED, run.describe()
    found = support.findings_with(entry, "POLICY_TIER_TOO_LOW")
    assert found, f"no POLICY_TIER_TOO_LOW finding\n{run.describe()}"
    assert found[0].get("policy") == KEY, run.describe()
    assert KEY in str(found[0].get("message", "")), f"the message does not name the key\n{run.describe()}"
    assert run.returncode == support.EXIT_CHECK_FAILED, run.describe()


def test_s4_the_finding_lists_the_covering_checks(project):
    run = planted(project, {KEY: "hard-block"},
                  [("cover-warning-a", WARNING, [KEY]), ("cover-warning-b", WARNING, [KEY, "memory"])])
    entry = policy_entry(run)
    assert entry is not None, f"no policy-{KEY} result\n{run.describe()}"
    found = support.findings_with(entry, "POLICY_TIER_TOO_LOW")
    assert found, f"no POLICY_TIER_TOO_LOW finding\n{run.describe()}"
    assert sorted(found[0].get("checks", [])) == ["cover-warning-a", "cover-warning-b"], run.describe()
    assert "POLICY_NOT_COVERED" not in support.finding_codes(entry), run.describe()


def test_s4_the_same_key_covered_by_a_hard_block_check_is_accepted(project):
    run = planted(project, {KEY: "hard-block"}, [("cover-hard", HARD_BLOCK, [KEY])])
    assert policy_entry(run) is None, f"policy-{KEY} is reported although a hard-block check covers it\n{run.describe()}"
    assert not any("POLICY_" in str(code) for entry in run.checks for code in support.finding_codes(entry)), \
        run.describe()


def test_s4_one_hard_block_check_among_warning_checks_covers_the_key(project):
    run = planted(project, {KEY: "hard-block"},
                  [("cover-warning", WARNING, [KEY]), ("cover-hard", HARD_BLOCK, [KEY])])
    assert policy_entry(run) is None, run.describe()


def test_s4_a_hard_block_key_nothing_covers_keeps_policy_not_covered(project):
    run = planted(project, {KEY: "hard-block"}, [("other-check", HARD_BLOCK, ["memory"])])
    entry = policy_entry(run)
    assert entry is not None, run.describe()
    assert entry["status"] == RED, run.describe()
    assert "POLICY_NOT_COVERED" in support.finding_codes(entry), run.describe()
    assert "POLICY_TIER_TOO_LOW" not in support.finding_codes(entry), run.describe()


def test_s4_a_warning_key_may_be_covered_by_a_warning_check(project):
    """The rule is for hard-block keys: a key of strength warning covered by a warning check is accepted."""
    run = planted(project, {"memory": "warning"}, [("cover-memory", WARNING, ["memory"])])
    assert policy_entry(run, "memory") is None, run.describe()
