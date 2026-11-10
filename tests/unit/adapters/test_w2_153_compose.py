"""W2-153 S3 amended (DEC-1112 (3)) builder tests: ``portability.compose`` and the comparison that uses it.

The composed source is its own rulesync front matter, the role template's body, one blank line and the kernel role
file's body (its front matter, if any, stripped). Regression evidence only (DEC-136); no rulesync runs here.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from gov.adapters import portability

REPO = Path(__file__).resolve().parents[3]
ROLE = "- **Purpose:** build one ticket.\n- **Tools:** Read, Grep and\n  Bash. No installs.\n"
TEMPLATE_BODY = "# You are the engineer\n1. Do.\n"
TEMPLATE = "---\nname: role-engineer\nversion: 1.0.0\nrole: engineer\nskills: [x, y]\n---\n" + TEMPLATE_BODY
FRONT = ('---\nname: engineer\ntargets: ["claudecode"]\nclaudecode:\n  tools: ["Read", "Grep", "Bash"]\n'
         '  skills: ["test-driven-development"]\n---\n')
EXPECTED = FRONT + "\n" + TEMPLATE_BODY + "\n" + ROLE
SOURCE = ".rulesync/subagents/engineer.md"


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "project"
    _write(root / "governance/kernel/roles/engineer.md", ROLE)
    _write(root / "governance/kernel/templates/role-engineer.md", TEMPLATE)
    _write(root / SOURCE, FRONT + "\n# stale body\n")
    return root


def _codes(findings):
    return [(f["code"], f.get("file")) for f in findings]


def test_compose_is_front_matter_template_body_blank_line_role_body(project):
    assert portability.compose(project, "engineer") == EXPECTED


def test_compose_keeps_the_sources_own_front_matter_verbatim(project):
    front = FRONT.replace("claudecode:\n", 'description: "Engineer: one ticket."\nclaudecode:\n')
    _write(project / SOURCE, front + "\nanything\n")
    assert portability.compose(project, "engineer") == front + "\n" + TEMPLATE_BODY + "\n" + ROLE


def test_compose_strips_the_role_files_front_matter(project):
    _write(project / "governance/kernel/roles/engineer.md", "---\nversion: 2\n---\n\n" + ROLE)
    assert portability.compose(project, "engineer") == EXPECTED


def test_compose_puts_exactly_one_blank_line_between_the_bodies(project):
    _write(project / "governance/kernel/templates/role-engineer.md", TEMPLATE.rstrip("\n"))
    assert portability.compose(project, "engineer") == EXPECTED
    _write(project / "governance/kernel/templates/role-engineer.md", TEMPLATE + "\n\n")
    assert portability.compose(project, "engineer") == EXPECTED


def test_compose_reads_the_template_kernel_of_this_repository(tmp_path):
    root = tmp_path / "repo"
    _write(root / "template/governance/kernel/roles/engineer.md", ROLE)
    _write(root / "template/governance/kernel/templates/role-engineer.md", TEMPLATE)
    _write(root / SOURCE, FRONT)
    assert portability.compose(root, "engineer") == EXPECTED


def test_compose_without_a_template_is_the_role_body(project):
    (project / "governance/kernel/templates/role-engineer.md").unlink()
    assert portability.compose(project, "engineer") == FRONT + "\n" + ROLE


def test_compose_without_a_source_or_role_file_refuses(project):
    (project / SOURCE).unlink()
    with pytest.raises(FileNotFoundError):
        portability.compose(project, "engineer")
    _write(project / SOURCE, FRONT)
    (project / "governance/kernel/roles/engineer.md").unlink()
    with pytest.raises(FileNotFoundError):
        portability.compose(project, "engineer")


def test_a_source_without_front_matter_composes_without_one(project):
    _write(project / SOURCE, "# no front matter\n")
    assert portability.compose(project, "engineer") == TEMPLATE_BODY + "\n" + ROLE


# -- the comparison --------------------------------------------------------------------------------------------------

def test_the_composed_source_is_consistent(project):
    _write(project / SOURCE, portability.compose(project, "engineer"))
    assert portability._kernel_findings(project) == ([], 1)


def test_the_source_with_the_template_body_only_differs_naming_both_origins(project):
    _write(project / SOURCE, FRONT + "\n" + TEMPLATE_BODY)
    findings, _count = portability._kernel_findings(project)
    assert _codes(findings) == [("SOURCE_DIFFERS", SOURCE)]
    assert "governance/kernel/templates/role-engineer.md" in findings[0]["message"]
    assert "governance/kernel/roles/engineer.md" in findings[0]["message"]


def test_a_changed_role_file_body_is_a_finding(project):
    _write(project / SOURCE, portability.compose(project, "engineer"))
    _write(project / "governance/kernel/roles/engineer.md", ROLE + "- **Network:** none.\n")
    assert _codes(portability._kernel_findings(project)[0]) == [("SOURCE_DIFFERS", SOURCE)]


def test_blank_lines_after_the_front_matter_stay_tolerated(project):
    _write(project / SOURCE, portability.compose(project, "engineer").replace("---\n\n#", "---\n\n\n#", 1))
    assert portability._kernel_findings(project)[0] == []


def test_skills_and_tools_are_still_checked_beside_the_composition(project):
    _write(project / SOURCE, portability.compose(project, "engineer").replace("test-driven-development", "audit"))
    findings = portability._kernel_findings(project)[0]
    assert _codes(findings) == [("SOURCE_DIFFERS", SOURCE)] and "skills" in findings[0]["message"]
    _write(project / SOURCE, FRONT)  # compose keeps the source's own front matter: restore the role's skills
    _write(project / "governance/kernel/roles/engineer.md", ROLE.replace("Bash", "Bash, Write"))
    _write(project / SOURCE, portability.compose(project, "engineer"))
    assert _codes(portability._kernel_findings(project)[0]) == [("SOURCE_TOOLS_DIFFER", SOURCE)]


@pytest.mark.parametrize("base", ["", "template"])
def test_the_twelve_sources_are_the_composition(base):
    root = REPO / base if base else REPO
    for role in portability.ROLE_SKILLS:
        assert (root / ".rulesync/subagents" / f"{role}.md").read_text(encoding="utf-8") == \
            portability.compose(root, role), role
