"""S3 on this repository: each ``.rulesync/subagents/<role>.md`` and ``template/.rulesync/subagents/<role>.md`` is the
rulesync front matter it has on integrate plus the role's ``skills:`` list, with the body of its kernel role template
(``template/governance/kernel/templates/<stem>.md`` without its own front matter), read as the portability check
reads a Markdown file (the blank lines after the front matter dropped).

The test designer's list: ``[test-design]`` once W2-128 has reconciled that skill with DEC-963 (the kernel skill then
names DEC-963); until then ``test-design`` is left out, so the list is empty or absent (the ticket's Interface).
"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

import w2_153_support as support
from w2_153_support import KERNEL_ROLE_TEMPLATE, SKILLS

TREES = (".rulesync", "template/.rulesync")


def _expected_skills(role: str):
    if role == "independent-test-designer" and not support.design_skill_reconciled():
        return None  # left out until W2-128 reconciles test-design with DEC-963
    return SKILLS[role]


@pytest.mark.parametrize("tree", TREES)
@pytest.mark.parametrize("role", sorted(SKILLS))
def test_s3_each_role_source_is_its_front_matter_its_skills_and_its_template_s_body(role, tree):
    rel = f"{tree}/subagents/{role}.md"
    front, body = support.split_front((support.REPO / rel).read_text(encoding="utf-8"))
    _template_front, template_body = support.split_front(
        (support.KERNEL_TEMPLATES / f"{KERNEL_ROLE_TEMPLATE[role]}.md").read_text(encoding="utf-8"))
    assert body == template_body, f"{rel}: the body is not that of templates/{KERNEL_ROLE_TEMPLATE[role]}.md"
    assert isinstance(front, dict), f"{rel} has no front matter"
    expected = _expected_skills(role)
    if expected is None:
        assert front.get("skills") in (None, []), f"{rel}: test-design is listed before W2-128 reconciles it"
    else:
        assert front.get("skills") == expected, f"{rel}: skills {front.get('skills')!r}, not {expected!r}"
    integrate_front, _ = support.split_front(support.git("show", f"{support.BASELINE_COMMIT}:{rel}"))
    kept = {key: value for key, value in front.items() if key != "skills"}
    assert kept == integrate_front, f"{rel}: the front matter changed beyond the skills list"


def test_s3_guard_the_check_finds_no_role_source_drift_in_this_repository(tmp_path):
    """``python3 -m gov.adapters.portability`` from this repository's root (no rulesync: the kernel comparison runs
    alone) names no ``subagents`` source. Green on integrate, where it compares the role files' bodies; it must stay
    green once the sources hold the templates' bodies and the check compares the composition."""
    done = subprocess.run([sys.executable, "-m", "gov.adapters.portability"], cwd=str(support.REPO),
                          capture_output=True, text=True, timeout=support.COMMAND_TIMEOUT_S,
                          env=support.portability_env(tmp_path, RULESYNC_BIN="/nonexistent/rulesync"),
                          stdin=subprocess.DEVNULL)
    findings = json.loads(done.stdout)["findings"]
    drift = [f for f in findings if "/subagents/" in str(f.get("file", ""))]
    assert drift == [], f"role source findings: {drift}"
