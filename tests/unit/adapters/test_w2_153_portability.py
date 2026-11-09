"""W2-153 builder tests for gov.adapters.portability: the composed subagent sources (S3) and the template copies (S4).

Regression evidence only (DEC-136). Each test builds a small project under ``tmp_path``; no rulesync runs here.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from gov.adapters import portability

REPO = Path(__file__).resolve().parents[3]
ROLE = "- **Purpose:** build one ticket.\n- **Tools:** Read, Grep and\n  Bash. No installs.\n"
TEMPLATE = "---\nname: role-engineer\nversion: 1.0.0\nrole: engineer\nskills: [x, y]\n---\n# You are the engineer\n1. Do.\n"
FRONT = "---\nname: engineer\ntargets: [\"claudecode\"]\nclaudecode:\n  tools: [\"Read\", \"Grep\", \"Bash\"]\n{skills}---\n\n"
COMPOSED = FRONT.format(skills='skills: ["test-driven-development"]\n') + "# You are the engineer\n1. Do.\n"


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "project"
    _write(root / "governance/kernel/roles/engineer.md", ROLE)
    _write(root / "governance/kernel/templates/role-engineer.md", TEMPLATE)
    _write(root / ".rulesync/subagents/engineer.md", COMPOSED)
    return root


def _codes(findings):
    return [(f["code"], f.get("file")) for f in findings]


def test_the_composed_source_is_consistent(project):
    assert portability._kernel_findings(project) == ([], 1)


def test_the_source_holding_the_role_files_body_differs_once_a_template_exists(project):
    _write(project / ".rulesync/subagents/engineer.md", FRONT.format(skills='skills: ["test-driven-development"]\n')
           + ROLE)
    findings, _count = portability._kernel_findings(project)
    assert _codes(findings) == [("SOURCE_DIFFERS", ".rulesync/subagents/engineer.md")]
    assert "governance/kernel/templates/role-engineer.md" in findings[0]["message"]


def test_a_changed_template_body_is_a_finding(project):
    _write(project / "governance/kernel/templates/role-engineer.md", TEMPLATE + "2. More.\n")
    assert _codes(portability._kernel_findings(project)[0]) == [("SOURCE_DIFFERS", ".rulesync/subagents/engineer.md")]


def test_the_templates_own_front_matter_is_not_compared(project):
    _write(project / "governance/kernel/templates/role-engineer.md", TEMPLATE.replace("1.0.0", "2.0.0"))
    assert portability._kernel_findings(project)[0] == []


def test_the_role_files_body_is_no_longer_compared_but_its_tools_are(project):
    _write(project / "governance/kernel/roles/engineer.md", ROLE + "- **Network:** none.\n")
    assert portability._kernel_findings(project)[0] == []
    _write(project / "governance/kernel/roles/engineer.md", ROLE.replace("Bash", "Bash, Write"))
    assert _codes(portability._kernel_findings(project)[0]) == [
        ("SOURCE_TOOLS_DIFFER", ".rulesync/subagents/engineer.md")]


@pytest.mark.parametrize("skills", ['skills: ["audit"]\n', "", 'skills: "test-driven-development"\n',
                                    'skills: ["test-driven-development", "audit"]\n'])
def test_skills_other_than_the_roles_are_a_finding(project, skills):
    _write(project / ".rulesync/subagents/engineer.md", FRONT.format(skills=skills) + "# You are the engineer\n1. Do.\n")
    findings, _count = portability._kernel_findings(project)
    assert _codes(findings) == [("SOURCE_DIFFERS", ".rulesync/subagents/engineer.md")]
    assert "skills" in findings[0]["message"]


def test_the_skills_lists_are_the_tickets():
    assert portability.ROLE_SKILLS == {
        "engineer": ["test-driven-development"], "independent-test-designer": [], "independent-auditor": ["audit"],
        "product-spec": ["change"], "research": ["discovery"], "orchestrator": ["orchestration"]}


def test_the_test_designer_lists_no_test_design_until_w2_128():
    """The ticket's rule: test-design is left out until W2-128 reconciles that skill with DEC-963."""
    assert "test-design" not in portability.ROLE_SKILLS["independent-test-designer"]


def test_this_repositorys_sources_are_the_composition():
    findings, _count = portability._kernel_findings(REPO)
    assert [f for f in findings if f.get("file", "").startswith(".rulesync/subagents/")] == []


@pytest.mark.parametrize("base", [".rulesync/subagents", "template/.rulesync/subagents"])
def test_the_template_sources_equal_the_repositorys(base):
    for role in portability.ROLE_SKILLS:
        assert (REPO / base / f"{role}.md").read_bytes() == (REPO / ".rulesync/subagents" / f"{role}.md").read_bytes()


# -- S4: the template copies -------------------------------------------------------------------------------------------

@pytest.fixture
def kept(tmp_path):
    root = tmp_path / "kept"
    for stem in portability.TEMPLATE_COPIES:
        _write(root / "template/governance/kernel/templates" / f"{stem}.md", f"---\nname: {stem}\n---\n# {stem}\n")
        _write(root / ".claude/templates" / f"{stem}.md", f"---\nname: {stem}\n---\n# {stem}\n")
    return root


def test_byte_copies_have_no_finding(kept):
    assert portability._template_findings(kept) == []


def test_one_changed_and_one_missing_copy_are_two_findings(kept):
    _write(kept / ".claude/templates/role-lead.md", "---\nname: role-lead\n---\n# role-lead\n\n")
    (kept / ".claude/templates/brief.md").unlink()
    assert _codes(portability._template_findings(kept)) == [
        ("TEMPLATE_COPY_MISSING", ".claude/templates/brief.md"),
        ("TEMPLATE_COPY_DIFFERS", ".claude/templates/role-lead.md")]


def test_a_kernel_without_templates_has_no_copies_to_check(tmp_path):
    (tmp_path / "governance/kernel/roles").mkdir(parents=True)
    assert portability._template_findings(tmp_path) == []


def test_main_reports_the_copies(kept, monkeypatch, capsys):
    (kept / ".claude/templates/role-cto.md").unlink()
    monkeypatch.chdir(kept)
    monkeypatch.setenv("RULESYNC_BIN", "/nonexistent/rulesync")
    assert portability.main() == 1
    codes = [f["code"] for f in json.loads(capsys.readouterr().out)["findings"]]
    assert "TEMPLATE_COPY_MISSING" in codes


def test_the_writer_writes_exactly_the_eight_copies(kept, tmp_path):
    """D-3: <dir> is the copies' folder itself."""
    out = tmp_path / "out" / "templates"
    done = subprocess.run([sys.executable, "-m", "gov.adapters.portability", "--write-templates", str(out)],
                          cwd=kept, capture_output=True, text=True, timeout=60,
                          env={"PYTHONPATH": str(REPO / "src"), "PATH": "/usr/bin:/bin"})
    assert done.returncode == 0, done.stderr
    assert sorted(path.name for path in out.iterdir()) == sorted(f"{stem}.md" for stem in portability.TEMPLATE_COPIES)
    for stem in portability.TEMPLATE_COPIES:
        assert (out / f"{stem}.md").read_bytes() == (
            kept / "template/governance/kernel/templates" / f"{stem}.md").read_bytes()
    assert len(json.loads(done.stdout)["written"]) == 8


def test_the_writer_writes_nothing_when_a_kernel_template_is_missing(kept, tmp_path, monkeypatch, capsys):
    (kept / "template/governance/kernel/templates/role-cto.md").unlink()
    monkeypatch.chdir(kept)
    out = tmp_path / "out"
    assert portability.main(["--write-templates", str(out)]) == 1
    assert not out.exists() and "role-cto" in capsys.readouterr().out


def test_the_written_copies_pass_the_check(kept, monkeypatch, capsys):
    for path in (kept / ".claude/templates").iterdir():
        path.unlink()
    monkeypatch.chdir(kept)
    assert portability.main(["--write-templates", str(kept / ".claude/templates")]) == 0
    assert portability._template_findings(kept) == []


def test_an_unknown_argument_is_a_usage_error(kept, monkeypatch):
    monkeypatch.chdir(kept)
    assert portability.main(["--other"]) == 2
