"""W1-01: what git history and the ticket records show while the bootstrap holds."""

from __future__ import annotations

import re

import pytest

import w1_01_support as support

ACCEPTANCE_PROBE = ("Edit", "tests/acceptance/W1-02/test_guard.py")
INSTALL_PROBE = ("Bash", "pip install requests")


@pytest.mark.parametrize(
    "probe",
    [
        pytest.param(ACCEPTANCE_PROBE, id="acceptance-tests"),
        pytest.param(INSTALL_PROBE, id="installs"),
    ],
)
def test_interim_rule_stays_in_force_once_introduced(interim, repo_root, probe):
    """KPI success 1 and 3: from the state that introduces a rule to now, no state drops it."""
    tool, target = probe
    states = support.settings_states(repo_root)
    in_force = [bool(support.denying_rules(rules, tool, target, repo_root)) for _, rules in states]
    assert any(in_force), (
        f"no state of {support.SETTINGS_REL} (history or working tree) denies {tool} `{target}`"
    )
    first = in_force.index(True)
    dropped = [label for (label, _), ok in zip(states[first:], in_force[first:]) if not ok]
    assert not dropped, (
        f"{tool} `{target}` was denied from {states[first][0]} but not in: {', '.join(dropped)}"
    )


def test_only_the_test_designer_commits_to_acceptance_tests(repo_root, deny_rules, w1_05_landed):
    """KPI failure 1: no implementer commit touches tests/acceptance/** before W1-05 lands.

    DEC-253 (rewrite after implementation, "owner decision: integration merges"):
    a merge commit passes when every change it brings under tests/acceptance/
    comes from commits on the merged side carrying the test designer's role.
    Every non-merge commit is checked as before.
    """
    if not w1_05_landed:
        tool, target = ACCEPTANCE_PROBE
        assert support.denying_rules(deny_rules, tool, target, repo_root), (
            f"the interim guardrail is not in force: {tool} on {target} is not denied"
        )
    offenders = support.acceptance_test_offenders(repo_root)
    assert not offenders, (
        "commits touch tests/acceptance/** without the trailer "
        f"`Role: {support.TEST_DESIGNER_ROLE}`:\n" + "\n".join(offenders)
    )


def test_implementer_commits_stay_inside_allowed_paths(bootstrap_text, repo_root):
    """KPI success 2 (KD-1): the diff procedure is "used" — git history is the record.

    Until W1-05 lands, a commit that names a ticket in a ``Task:`` trailer, and is
    not a test-designer commit, touches only that ticket's ``allowed_paths`` and
    the ticket's own file in ``.tickets/``.
    """
    offenders = []
    for sha, message in support.interim_commits(repo_root):
        tasks = support.trailer_values(message, "Task")
        if not tasks or support.TEST_DESIGNER_ROLE in support.trailer_values(message, "Role"):
            continue
        allowed, unknown = [], []
        for task in tasks:
            found = support.ticket_file(task, repo_root)
            if found:
                allowed.append(found[0])
                allowed.extend(found[1].get("allowed_paths", []))
            elif re.fullmatch(r"W1-\d+", task):
                unknown.append(task)
        if unknown:
            offenders.append(f"{sha[:12]}: Task {', '.join(unknown)} names no ticket")
        if not allowed:
            continue
        outside = [p for p in support.changed_paths(sha, repo_root)
                   if not support.path_in_globs(p, allowed)]
        if outside:
            offenders.append(f"{sha[:12]} (Task {', '.join(tasks)}): {', '.join(outside)}")
    assert not offenders, "commits touch paths outside their ticket's allowed_paths:\n" + "\n".join(
        offenders
    )


def test_no_install_is_recorded_before_w1_05(interim, repo_root, deny_rules):
    """KPI failure 3: installs stay denied, and W1-06 (the first install) waits for W1-05."""
    tool, target = INSTALL_PROBE
    assert support.denying_rules(deny_rules, tool, target, repo_root), (
        f"the interim install rule is not in force: {tool} `{target}` is not denied"
    )
    w1_06 = support.ticket("W1-06", repo_root)
    assert w1_06 is not None, "no ticket with wbs_id W1-06 in .tickets/"
    assert "W1-05" in w1_06.get("depends_on", []), "W1-06 no longer depends on W1-05"
    assert w1_06.get("status") == "open", (
        f"W1-06 (tool installs) is {w1_06.get('status')} while W1-05 is not closed"
    )
    registry = repo_root / support.TOOL_REGISTRY_REL
    assert not registry.exists(), (
        f"{support.TOOL_REGISTRY_REL} records installs while W1-05 is not closed"
    )
