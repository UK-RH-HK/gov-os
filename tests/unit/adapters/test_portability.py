"""Unit tests for gov.adapters.portability.

Each test builds a small project under ``tmp_path``. The rulesync binary is a stand-in script that
prints a fixed answer; no real rulesync runs here.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from gov.adapters import portability

ROLE = "- **Purpose:** build one ticket.\n"
SKILL = "---\nname: planning\nversion: \"1.0.0\"\n---\n\n# Planning\n\nA method.\n"
CLEAN = {"success": True, "data": {"hasDiff": False, "features": {"rules": {"count": 0, "paths": []}}}}


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _registry(root, version="24.0.0", name="rulesync"):
    return _write(root / portability.REGISTRY, f'tools:\n  - name: {name}\n    version: "{version}"\n')


def _binary(tmp_path, *, version="24.0.0", answer=CLEAN, stream=1, code=0):
    """A stand-in rulesync: ``--version`` prints ``version``; any other call prints ``answer``
    (a mapping as JSON, a string as it is) on ``stream`` and ends with ``code``."""
    text = json.dumps(answer) if isinstance(answer, dict) else answer
    _write(tmp_path / "answer.txt", text)
    script = tmp_path / "bin" / "rulesync"
    _write(script, (
        "#!/bin/bash\n"
        f'if [[ "$1" == "--version" ]]; then echo "{version}"; exit 0; fi\n'
        f'cat "{tmp_path / "answer.txt"}" >&{stream}\nexit {code}\n'
    ))
    script.chmod(0o755)
    return str(script)


@pytest.fixture()
def project(tmp_path):
    """A kernel with one role and one skill (with a supporting file), and their sources."""
    root = tmp_path / "project"
    _registry(root)
    _write(root / ".rulesync/rules/governance.md", "---\nroot: true\n---\n\n# Rules\n")
    _write(root / "governance/kernel/roles/engineer.md", ROLE)
    _write(root / ".rulesync/subagents/engineer.md", "---\nname: engineer\n---\n\n" + ROLE)
    _write(root / "governance/kernel/skills/planning/SKILL.md", SKILL)
    _write(root / ".rulesync/skills/planning/SKILL.md", SKILL)
    _write(root / "governance/kernel/skills/superpowers/debugging/SKILL.md", SKILL)
    _write(root / "governance/kernel/skills/superpowers/debugging/notes.md", "notes\n")
    _write(root / ".rulesync/skills/debugging/SKILL.md", SKILL)
    _write(root / ".rulesync/skills/debugging/notes.md", "notes\n")
    return root


def _files(findings):
    return [finding.get("file") for finding in findings]


class TestExpectedVersion:
    def test_reads_the_rulesync_entry(self, tmp_path):
        _registry(tmp_path, "24.0.0")
        assert portability._expected_version(tmp_path) == ("24.0.0", "")

    def test_absent_registry_is_a_reason(self, tmp_path):
        version, reason = portability._expected_version(tmp_path)
        assert version is None and portability.REGISTRY in reason

    def test_registry_without_rulesync_is_a_reason(self, tmp_path):
        _registry(tmp_path, "0.12.21", name="uv")
        version, reason = portability._expected_version(tmp_path)
        assert version is None and "no rulesync entry" in reason

    @pytest.mark.parametrize("text", ["tools: [", "- a\n- b\n", "tools: 3\n", ""])
    def test_unreadable_registry_is_a_reason(self, tmp_path, text):
        _write(tmp_path / portability.REGISTRY, text)
        assert portability._expected_version(tmp_path)[0] is None


class TestVersionFinding:
    def test_none_when_installed_is_expected(self, tmp_path):
        _registry(tmp_path)
        assert portability._version_finding(tmp_path, _binary(tmp_path)) is None

    def test_other_installed_version_names_both(self, tmp_path):
        _registry(tmp_path)
        finding = portability._version_finding(tmp_path, _binary(tmp_path, version="99.0.0"))
        assert finding["code"] == "RULESYNC_VERSION_DIFFERS"
        assert "99.0.0" in finding["message"] and "24.0.0" in finding["message"]

    def test_version_is_compared_whole(self, tmp_path):
        _registry(tmp_path, "4.0.0")
        finding = portability._version_finding(tmp_path, _binary(tmp_path, version="24.0.0"))
        assert finding["code"] == "RULESYNC_VERSION_DIFFERS"

    def test_no_registry_is_a_finding_even_with_rulesync(self, tmp_path):
        finding = portability._version_finding(tmp_path, _binary(tmp_path))
        assert finding["code"] == "RULESYNC_VERSION_UNKNOWN"

    def test_no_binary_is_a_finding(self, tmp_path):
        _registry(tmp_path)
        finding = portability._version_finding(tmp_path, None)
        assert finding["code"] == "RULESYNC_ABSENT" and "not found" in finding["message"]

    def test_rulesync_without_answer_is_a_finding(self, tmp_path, monkeypatch):
        _registry(tmp_path)
        script = _write(tmp_path / "bin" / "rulesync", "#!/bin/bash\nsleep 30\n")
        script.chmod(0o755)
        monkeypatch.setattr(portability, "TIME_LIMIT", 1)
        finding = portability._version_finding(tmp_path, str(script))
        assert finding["code"] == "RULESYNC_FAILED" and "no answer" in finding["message"]


class TestFindRulesync:
    def test_named_binary(self, tmp_path, monkeypatch):
        binary = _binary(tmp_path)
        monkeypatch.setenv("RULESYNC_BIN", binary)
        assert portability._find_rulesync() == binary

    def test_named_binary_that_is_no_file(self, monkeypatch):
        monkeypatch.setenv("RULESYNC_BIN", "/nonexistent/rulesync")
        assert portability._find_rulesync() is None


class TestSplit:
    def test_blank_lines_after_frontmatter_are_dropped(self, tmp_path):
        with_blank = _write(tmp_path / "a.md", "---\nname: a\n---\n\n\n# Body\n")
        without = _write(tmp_path / "b.md", "---\nname: \"a\"\n---\n# Body\n")
        assert portability._split(with_blank) == portability._split(without) == ({"name": "a"}, "# Body\n")

    def test_nothing_else_is_tolerated(self, tmp_path):
        first = _write(tmp_path / "a.md", "---\nname: a\n---\n# Body\n")
        second = _write(tmp_path / "b.md", "---\nname: a\n---\n# Body\n\n")
        assert portability._split(first) != portability._split(second)

    def test_file_without_frontmatter(self, tmp_path):
        assert portability._split(_write(tmp_path / "a.md", "# Body\n")) == (None, "# Body\n")


class TestKernelFindings:
    def test_agreeing_project_has_no_finding_and_counts_what_it_compared(self, project):
        assert portability._kernel_findings(project) == ([], 4)

    def test_kernel_role_changed(self, project):
        _write(project / "governance/kernel/roles/engineer.md", ROLE + "More.\n")
        findings, _count = portability._kernel_findings(project)
        assert _files(findings) == [".rulesync/subagents/engineer.md"]
        assert "governance/kernel/roles/engineer.md" in findings[0]["message"]

    def test_role_source_changed(self, project):
        _write(project / ".rulesync/subagents/engineer.md", "---\nname: engineer\n---\n" + ROLE + "More.\n")
        assert _files(portability._kernel_findings(project)[0]) == [".rulesync/subagents/engineer.md"]

    def test_role_source_frontmatter_is_not_part_of_the_pair(self, project):
        _write(project / ".rulesync/subagents/engineer.md", "---\nname: engineer\ntargets: [x]\n---\n" + ROLE)
        assert portability._kernel_findings(project)[0] == []

    @pytest.mark.parametrize("changed", [
        "governance/kernel/skills/planning/SKILL.md", ".rulesync/skills/planning/SKILL.md",
    ])
    def test_skill_body_changed_on_either_side(self, project, changed):
        _write(project / changed, SKILL + "\nA line.\n")
        assert _files(portability._kernel_findings(project)[0]) == [".rulesync/skills/planning/SKILL.md"]

    def test_skill_frontmatter_changed(self, project):
        _write(project / ".rulesync/skills/planning/SKILL.md", SKILL.replace("1.0.0", "1.1.0"))
        assert _files(portability._kernel_findings(project)[0]) == [".rulesync/skills/planning/SKILL.md"]

    def test_supporting_file_changed(self, project):
        _write(project / ".rulesync/skills/debugging/notes.md", "notes\n\n")
        assert _files(portability._kernel_findings(project)[0]) == [".rulesync/skills/debugging/notes.md"]

    def test_supporting_file_without_source(self, project):
        (project / ".rulesync/skills/debugging/notes.md").unlink()
        findings, _count = portability._kernel_findings(project)
        assert [(f["code"], f["file"]) for f in findings] == [
            ("SOURCE_MISSING", ".rulesync/skills/debugging/notes.md")]

    def test_source_file_the_kernel_does_not_hold(self, project):
        _write(project / ".rulesync/skills/debugging/extra.md", "extra\n")
        _write(project / ".rulesync/subagents/ghost.md", "---\nname: ghost\n---\nGhost.\n")
        findings, _count = portability._kernel_findings(project)
        assert [(f["code"], f["file"]) for f in findings] == [
            ("SOURCE_WITHOUT_KERNEL", ".rulesync/subagents/ghost.md"),
            ("SOURCE_WITHOUT_KERNEL", ".rulesync/skills/debugging/extra.md"),
        ]

    def test_source_skill_that_is_no_kernel_skill_is_left_alone(self, project):
        """OpenSpec's skills are sources without a kernel file (DEC-468)."""
        _write(project / ".rulesync/skills/openspec-propose/SKILL.md", SKILL)
        assert portability._kernel_findings(project)[0] == []

    def test_kernel_of_this_repository(self, project):
        (project / "governance/kernel").rename(project / "template-kernel")
        (project / "template/governance").mkdir(parents=True)
        (project / "template-kernel").rename(project / "template/governance/kernel")
        assert portability._kernel_findings(project) == ([], 4)

    def test_no_kernel_is_a_finding(self, tmp_path):
        findings, count = portability._kernel_findings(tmp_path)
        assert [f["code"] for f in findings] == ["KERNEL_ABSENT"] and count == 0

    def test_empty_kernel_is_a_finding(self, tmp_path):
        (tmp_path / "governance/kernel/roles").mkdir(parents=True)
        findings, count = portability._kernel_findings(tmp_path)
        assert [f["code"] for f in findings] == ["KERNEL_EMPTY"] and count == 0


class TestGeneratedFindings:
    @pytest.fixture(autouse=True)
    def root_rule(self, tmp_path):
        _write(tmp_path / ".rulesync/rules/governance.md", "---\nroot: true\n---\n\n# Rules\n")

    def test_clean_answer(self, tmp_path):
        assert portability._generated_findings(tmp_path, _binary(tmp_path)) == []

    @pytest.mark.parametrize("rule", [None, "# Rules\n", "---\nroot: false\n---\n# Rules\n"])
    def test_no_root_rule_is_a_finding_although_rulesync_answers_clean(self, tmp_path, rule):
        (tmp_path / ".rulesync/rules/governance.md").unlink()
        if rule is not None:
            _write(tmp_path / ".rulesync/rules/other.md", rule)
        findings = portability._generated_findings(tmp_path, _binary(tmp_path))
        assert [f["code"] for f in findings] == ["ROOT_RULE_ABSENT"]

    def test_long_answer_is_read_whole(self, tmp_path):
        paths = [f".claude/skills/s{n}/SKILL.md" for n in range(3)]
        answer = {"success": True, "data": {"hasDiff": True, "skills": ["x" * 2_000_000],
                                            "features": {"skills": {"count": 3, "paths": paths}}}}
        findings = portability._generated_findings(tmp_path, _binary(tmp_path, answer=answer))
        assert _files(findings) == paths

    def test_long_text_that_is_no_json_is_reported_by_its_end(self, tmp_path):
        binary = _binary(tmp_path, answer="x" * 5000 + " the end", stream=2, code=1)
        message = portability._generated_findings(tmp_path, binary)[0]["message"]
        assert message.endswith("the end") and len(message) < 600

    def test_one_finding_per_path_of_the_answer(self, tmp_path):
        answer = {"success": True, "data": {"hasDiff": True, "features": {
            "rules": {"count": 2, "paths": ["CLAUDE.md", "AGENTS.md"]},
            "skills": {"count": 1, "paths": [".claude/skills/planning/SKILL.md"]},
        }}}
        findings = portability._generated_findings(tmp_path, _binary(tmp_path, answer=answer))
        assert _files(findings) == [".claude/skills/planning/SKILL.md", "AGENTS.md", "CLAUDE.md"]
        assert {f["code"] for f in findings} == {"GENERATED_DIFFERS"}

    def test_difference_without_a_path(self, tmp_path):
        answer = {"success": True, "data": {"hasDiff": True, "features": {}}}
        findings = portability._generated_findings(tmp_path, _binary(tmp_path, answer=answer))
        assert [f["code"] for f in findings] == ["GENERATED_DIFFERS"] and "file" not in findings[0]

    def test_rulesync_error_is_reported_with_its_message(self, tmp_path):
        answer = {"success": False, "error": {"code": "GENERATION_FAILED", "message": "the reason"}}
        binary = _binary(tmp_path, answer=answer, stream=2, code=1)
        findings = portability._generated_findings(tmp_path, binary)
        assert findings == [{"code": "RULESYNC_FAILED", "message": "rulesync generate --dry-run: the reason"}]

    def test_text_that_is_no_json_is_reported_as_it_is(self, tmp_path):
        binary = _binary(tmp_path, answer="plain reason mentioning CLAUDE.md", stream=2, code=1)
        findings = portability._generated_findings(tmp_path, binary)
        assert [f["code"] for f in findings] == ["RULESYNC_FAILED"] and "file" not in findings[0]
        assert "plain reason mentioning CLAUDE.md" in findings[0]["message"]

    @pytest.mark.parametrize("answer", [
        {"success": True}, {"success": True, "data": {"features": {}}},
        {"success": True, "data": {"hasDiff": False}}, {"data": CLEAN["data"]}, "",
    ])
    def test_answer_without_the_expected_fields_is_not_clean(self, tmp_path, answer):
        findings = portability._generated_findings(tmp_path, _binary(tmp_path, answer=answer))
        assert [f["code"] for f in findings] == ["RULESYNC_FAILED"]

    def test_clean_answer_with_a_failing_exit_is_not_clean(self, tmp_path):
        findings = portability._generated_findings(tmp_path, _binary(tmp_path, code=1))
        assert [f["code"] for f in findings] == ["RULESYNC_FAILED"]


class TestMain:
    def _run(self, root, binary, monkeypatch, capsys):
        monkeypatch.chdir(root)
        monkeypatch.setenv("RULESYNC_BIN", binary)
        code = portability.main()
        return code, json.loads(capsys.readouterr().out)

    def test_green_says_what_was_compared(self, project, tmp_path, monkeypatch, capsys):
        code, printed = self._run(project, _binary(tmp_path), monkeypatch, capsys)
        assert code == 0
        assert printed == {"findings": [], "compared": {
            "rulesync_version": True, "kernel_files": 4, "generated_files": True}}

    def test_other_version_stops_before_the_generated_files(self, project, tmp_path, monkeypatch, capsys):
        code, printed = self._run(project, _binary(tmp_path, version="99.0.0"), monkeypatch, capsys)
        assert code == 1
        assert [f["code"] for f in printed["findings"]] == ["RULESYNC_VERSION_DIFFERS"]
        assert "not compared" in printed["findings"][0]["message"]
        assert printed["compared"] == {"rulesync_version": False, "kernel_files": 4, "generated_files": False}

    def test_kernel_is_compared_also_without_rulesync(self, project, monkeypatch, capsys):
        _write(project / "governance/kernel/roles/engineer.md", ROLE + "More.\n")
        code, printed = self._run(project, "/nonexistent/rulesync", monkeypatch, capsys)
        assert code == 1
        assert [f["code"] for f in printed["findings"]] == ["RULESYNC_ABSENT", "SOURCE_DIFFERS"]

    def test_rulesync_failure_is_not_counted_as_compared(self, project, tmp_path, monkeypatch, capsys):
        binary = _binary(tmp_path, answer="stopped", stream=2, code=1)
        code, printed = self._run(project, binary, monkeypatch, capsys)
        assert code == 1 and printed["compared"]["generated_files"] is False
