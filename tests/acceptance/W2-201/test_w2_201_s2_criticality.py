"""W2-201 S2: the criticality list is Table 3 with the retired machinery gone.

``gov.launch.criticality.ticket_criticality`` on this repository's own ``governance/project/criticality.yaml``, for a
ticket (front-matter map, profile STANDARD unless named) whose ``allowed_paths`` hold one path: one per listed C3 path
(C3); the guard, a hook, the settings and the other old C3 entries (not C3); ``src/gov/health/x.py`` (C2) and
``docs/x.md`` (C1); a FULL ticket on ``docs/x.md`` is C2.
"""

from __future__ import annotations

import pytest

import w2_201_support as k

# One path per C3 entry of S2, a file inside each glob or the file itself.
C3_PATHS = {
    "template/governance/kernel/**": "template/governance/kernel/roles/x.md",
    "governance/kernel/**": "governance/kernel/x.md",
    "docs/contract/**": "docs/contract/x.md",
    "src/gov/close/**": "src/gov/close/x.py",
    "src/gov/accept/**": "src/gov/accept/x.py",
    "src/gov/queue/**": "src/gov/queue/x.py",
    "src/gov/dispatch/landing.py": "src/gov/dispatch/landing.py",
    "src/gov/tasks/queue.py": "src/gov/tasks/queue.py",
    "governance/project/orchestration/tools/merge_queue.py": "governance/project/orchestration/tools/merge_queue.py",
    "governance/project/operator/landing_check.py": "governance/project/operator/landing_check.py",
    "src/gov/memaudit/**": "src/gov/memaudit/x.py",
    "fixtures/evaluation/**": "fixtures/evaluation/examin/cases.json",
    "src/gov/release/**": "src/gov/release/x.py",
    "src/gov/update/**": "src/gov/update/x.py",
    "src/gov/lock/**": "src/gov/lock/x.py",
    "governance/project/path-map.yaml": "governance/project/path-map.yaml",
}

# The old list's guard, hooks, settings, secrets, walls, held-out and operator entries: no longer C3 rules. The first
# three are the Verify's; the others are the same sentence's remaining entries.
NOT_C3 = ("src/gov/guard/x.py", ".claude/hooks/agent_model.py", ".claude/settings.json", ".claude/settings.local.json",
          "governance/project/secrets.yaml", "governance/project/indep-walls/x.yaml",
          "governance/project/held-out.yaml", "governance/project/operator/agent.md")


@pytest.mark.parametrize("entry", sorted(C3_PATHS))
def test_s2_a_ticket_on_a_listed_path_is_c3(entry):
    path = C3_PATHS[entry]
    assert k.real_criticality([path]) == "C3", f"a STANDARD ticket on {path} (S2's entry {entry}) is not C3"


@pytest.mark.parametrize("path", NOT_C3)
def test_s2_a_ticket_on_the_retired_machinery_is_not_c3(path):
    got = k.real_criticality([path])
    assert got != "C3", f"a STANDARD ticket on {path} is {got}: the old list's entry is still a C3 rule"


@pytest.mark.parametrize("path, profile, want", [
    ("src/gov/health/x.py", "STANDARD", "C2"),
    ("governance/project/test-map.yaml", "STANDARD", "C2"),
    ("docs/x.md", "STANDARD", "C1"),
    ("docs/x.md", "FULL", "C2"),
], ids=["other-src-is-c2", "test-map-is-c2", "docs-is-c1", "full-docs-is-c2"])
def test_s2_other_src_is_c2_docs_c1_and_a_full_ticket_at_least_c2(path, profile, want):
    """Guard (green on the base): the C2 and C1 rules and the FULL floor stay."""
    got = k.real_criticality([path], profile)
    assert got == want, f"a {profile} ticket on {path} is {got}, not {want}"
