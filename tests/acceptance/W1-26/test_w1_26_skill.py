"""KPI S6 (CAP-24.c): skill version check.

Fails a skill file whose content changed without a version change and a linked
decision.

Revised (W2-67, I2 §2.7 R1): the two RED cases change their skill on the green
base (``green_project``) and assert ``skill-version``'s own entry RED with a
finding that names the skill file, not that ``gov check`` failed (the base was
red before any defect).
"""

from __future__ import annotations

import w1_26_support as support


# --------------------------------------------------------------------------
# Content changed, version unchanged -> RED
# --------------------------------------------------------------------------

def test_skill_content_changed_version_unchanged_is_red(green_project, sandbox, interface):
    """A skill file with content changed but version unchanged fails: ``skill-version`` is RED with a finding that
    names the skill file."""
    project = green_project
    rel = project.add_skill("my-skill", version=1, content_marker="original content")
    project.commit("add skill v1")
    project.add_skill("my-skill", version=1, content_marker="changed content")
    project.commit("change skill without version bump")
    run = support.run_check(project, sandbox)
    support.assert_check_red_naming(run, interface, "skill-version", rel)


def test_skill_content_changed_version_unchanged_no_decision_is_red(green_project, sandbox, interface):
    """A skill file with content and version changed but no linked decision fails: ``skill-version`` is RED with a
    finding that names the skill file."""
    project = green_project
    rel = project.add_skill("my-skill", version=1, content_marker="original content")
    project.commit("add skill v1")
    project.add_skill("my-skill", version=2, content_marker="changed content")
    project.commit("bump version without decision")
    run = support.run_check(project, sandbox)
    support.assert_check_red_naming(run, interface, "skill-version", rel)


# --------------------------------------------------------------------------
# Content and version changed with linked decision -> passes
# --------------------------------------------------------------------------

def test_skill_content_version_changed_with_decision_passes(project, sandbox, interface):
    """A skill file with content and version changed, with a linked decision, passes."""
    project.add_skill("my-skill", version=1, content_marker="original content")
    project.commit("add skill v1")
    project.add_skill("my-skill", version=2, content_marker="changed content")
    project.add_decision("DEC-SKILL-001", "ACTIVE",
                          title="Skill change decision", supersedes=[])
    project.commit("bump version with decision")
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)
    for family_name, entry in families.items():
        if "skill" in str(entry).lower():
            status = entry.get("status") if isinstance(entry, dict) else entry
            assert status != support.RED, \
                f"skill with version bump and decision still fails {family_name}\n{run.describe()}"


# --------------------------------------------------------------------------
# No skill change -> no finding
# --------------------------------------------------------------------------

def test_unchanged_skill_no_finding(project, sandbox, interface):
    """An unchanged skill file does not trigger a skill version finding."""
    project.add_skill("my-skill", version=1, content_marker="stable content")
    project.commit("add skill v1")
    project.write("unrelated.txt", "no skill change\n")
    project.commit("unrelated change")
    run = support.run_check(project, sandbox)
    envelope = support.envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    families = support.families_of(result)
    for family_name, entry in families.items():
        if "skill" in str(entry).lower():
            status = entry.get("status") if isinstance(entry, dict) else entry
            assert status != support.RED, \
                f"unchanged skill triggers a finding in {family_name}\n{run.describe()}"
