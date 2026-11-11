"""S3 on this repository: each ``.rulesync/subagents/<role>.md`` and ``template/.rulesync/subagents/<role>.md`` is the
rulesync front matter it has on integrate plus the role's skills list under ``claudecode: skills:`` (DEC-1112 (3):
rulesync 24.0.0 drops a top-level ``skills``, so none may sit there), with S3 amended's body (DEC-1112 (3),
2026-11-10): the body of its kernel role template (``template/governance/kernel/templates/<stem>.md`` without its own
front matter), then one blank line, then the body of its kernel role file (``template/governance/kernel/roles/
<role>.md``, verbatim, front matter if any stripped), each read as the portability check reads a Markdown file (the
blank lines after the front matter dropped).

So the agent carries the role file's labelled fields (W1-33, MR-5, DEC-066; W1-38), and only those: the role
templates carry none.

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
KERNEL_ROLES = support.KERNEL / "roles"


def _expected_skills(role: str):
    if role == "independent-test-designer" and not support.design_skill_reconciled():
        return None  # left out until W2-128 reconciles test-design with DEC-963
    return SKILLS[role]


def _template_text(role: str) -> str:
    return (support.KERNEL_TEMPLATES / f"{KERNEL_ROLE_TEMPLATE[role]}.md").read_text(encoding="utf-8")


def _role_text(role: str) -> str:
    return (KERNEL_ROLES / f"{role}.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("tree", TREES)
@pytest.mark.parametrize("role", sorted(SKILLS))
def test_s3_each_role_source_is_its_front_matter_its_skills_its_template_s_body_and_its_role_file_s_body(role, tree):
    rel = f"{tree}/subagents/{role}.md"
    front, body = support.split_front((support.REPO / rel).read_text(encoding="utf-8"))
    _template_front, template_body = support.split_front(_template_text(role))
    _role_front, role_body = support.split_front(_role_text(role))
    expected_body = support.composed_body(template_body, role_body)
    assert body == expected_body, (
        f"{rel}: the body is not that of templates/{KERNEL_ROLE_TEMPLATE[role]}.md, one blank line, then that of "
        f"roles/{role}.md (S3 amended, DEC-1112 (3))")
    assert isinstance(front, dict), f"{rel} has no front matter"
    assert "skills" not in front, f"{rel}: a top-level skills list (rulesync 24.0.0 drops it; DEC-1112 (3))"
    claudecode = front.get("claudecode") or {}
    assert isinstance(claudecode, dict), f"{rel}: claudecode is {claudecode!r}, not a mapping"
    listed = claudecode.get("skills")
    expected = _expected_skills(role)
    if expected is None:
        assert listed in (None, []), f"{rel}: test-design is listed before W2-128 reconciles it"
    else:
        assert listed == expected, f"{rel}: claudecode.skills {listed!r}, not {expected!r}"
    integrate_front, _ = support.split_front(support.git("show", f"{support.BASELINE_COMMIT}:{rel}"))
    kept = dict(front)
    kept_claudecode = {key: value for key, value in claudecode.items() if key != "skills"}
    if kept_claudecode or "claudecode" in integrate_front:
        kept["claudecode"] = kept_claudecode
    else:
        kept.pop("claudecode", None)
    assert kept == integrate_front, f"{rel}: the front matter changed beyond claudecode.skills"


@pytest.mark.parametrize("tree", TREES)
@pytest.mark.parametrize("role", sorted(SKILLS))
def test_s3_the_source_s_labelled_fields_are_its_role_file_s_and_the_template_contributes_none(role, tree):
    """W1-33's ``fields()`` rule (MR-5, DEC-066): every labelled list item of the source's text equals the role
    file's, label for label and text for text, and the role template (the source's first part) has none, so no
    field of the agent comes from it."""
    rel = f"{tree}/subagents/{role}.md"
    role_fields = support.fields(_role_text(role))
    assert role_fields, f"roles/{role}.md has no labelled field: the case's premise"
    template_fields = support.fields(_template_text(role))
    assert template_fields == {}, (
        f"templates/{KERNEL_ROLE_TEMPLATE[role]}.md carries labelled fields {sorted(template_fields)}: the template "
        "must contribute none (S3 amended)")
    source_fields = support.fields((support.REPO / rel).read_text(encoding="utf-8"))
    missing = sorted(set(role_fields) - set(source_fields))
    extra = sorted(set(source_fields) - set(role_fields))
    changed = sorted(label for label in set(role_fields) & set(source_fields)
                     if role_fields[label] != source_fields[label])
    assert (missing, extra, changed) == ([], [], []), (
        f"{rel}: its labelled fields are not roles/{role}.md's: missing {missing}, extra {extra}, changed {changed}")


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
