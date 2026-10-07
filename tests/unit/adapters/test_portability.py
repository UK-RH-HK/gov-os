"""Unit tests for gov.adapters.portability.

Each test builds a small project under ``tmp_path``. The rulesync binary is a stand-in script that
writes a fixed set of files into the folder it is run in; no real rulesync runs here.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from gov.adapters import portability

ROLE = "- **Purpose:** build one ticket.\n- **Tools:** Read, Grep and\n  Bash. No installs.\n- **Network:** none.\n"
ROLE_SOURCE = "---\nname: engineer\nclaudecode:\n  tools: [{tools}]\n---\n\n" + ROLE
SKILL = "---\nname: planning\nversion: \"1.0.0\"\n---\n\n# Planning\n\nA method.\n"
GENERATED = {"CLAUDE.md": "# Rules\n", ".claude/settings.json": '{\n  "permissions": {"deny": ["Bash(sudo *)"]}\n}\n',
             ".claude/agents/engineer.md": "an engineer\n", ".claude/skills/planning/SKILL.md": "a method\n",
             ".claude/commands/opsx/apply.md": "apply\n"}


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _registry(root, version="24.0.0", name="rulesync"):
    return _write(root / portability.REGISTRY, f'tools:\n  - name: {name}\n    version: "{version}"\n')


def _binary(tmp_path, *, version="24.0.0", files=GENERATED, said="", stream=2, code=0):
    """A stand-in rulesync: ``--version`` prints ``version``; any other call writes ``files`` into the
    folder it runs in, prints ``said`` on ``stream`` and ends with ``code``."""
    (tmp_path / "made").mkdir()
    for rel, text in files.items():
        _write(tmp_path / "made" / rel, text)
    _write(tmp_path / "said.txt", said)
    script = tmp_path / "bin" / "rulesync"
    _write(script, (
        "#!/bin/bash\n"
        f'if [[ "$1" == "--version" ]]; then echo "{version}"; exit 0; fi\n'
        f'echo "$@" > "{tmp_path / "called.txt"}"\ncp -r "{tmp_path / "made"}/." .\n'
        f'cat "{tmp_path / "said.txt"}" >&{stream}\nexit {code}\n'
    ))
    script.chmod(0o755)
    return str(script)


def _generate(root, files=GENERATED):
    for rel, text in files.items():
        _write(root / rel, text)
    return root


@pytest.fixture()
def project(tmp_path):
    """A kernel with one role and one skill (with a supporting file), and their sources."""
    root = tmp_path / "project"
    _registry(root)
    _write(root / ".rulesync/rules/governance.md", "---\nroot: true\n---\n\n# Rules\n")
    _write(root / "governance/kernel/roles/engineer.md", ROLE)
    _write(root / ".rulesync/subagents/engineer.md", ROLE_SOURCE.format(tools="Bash, Read, Grep"))
    _write(root / "governance/kernel/skills/planning/SKILL.md", SKILL)
    _write(root / ".rulesync/skills/planning/SKILL.md", SKILL)
    _write(root / "governance/kernel/skills/superpowers/debugging/SKILL.md", SKILL)
    _write(root / "governance/kernel/skills/superpowers/debugging/notes.md", "notes\n")
    _write(root / ".rulesync/skills/debugging/SKILL.md", SKILL)
    _write(root / ".rulesync/skills/debugging/notes.md", "notes\n")
    return _generate(root)


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
        _write(project / ".rulesync/subagents/engineer.md", ROLE_SOURCE.format(tools="Bash, Read, Grep") + "More.\n")
        findings, _count = portability._kernel_findings(project)
        assert [(f["code"], f["file"]) for f in findings] == [("SOURCE_DIFFERS", ".rulesync/subagents/engineer.md")]

    def test_role_source_frontmatter_is_not_part_of_the_pair(self, project):
        source = ROLE_SOURCE.format(tools="Read, Grep, Bash").replace("name: engineer", "name: other\ntargets: [x]")
        _write(project / ".rulesync/subagents/engineer.md", source)
        assert portability._kernel_findings(project)[0] == []

    @pytest.mark.parametrize("tools, said", [
        ("Read, Grep, Bash, NotebookEdit", "only in the source ['NotebookEdit'], only in the kernel role []"),
        ("Read, Grep", "only in the source [], only in the kernel role ['Bash']"),
        ("Read, Grep, bash", "only in the source ['bash'], only in the kernel role ['Bash']"),
    ])
    def test_role_source_with_other_tools_names_the_source_and_the_difference(self, project, tools, said):
        _write(project / ".rulesync/subagents/engineer.md", ROLE_SOURCE.format(tools=tools))
        findings, _count = portability._kernel_findings(project)
        assert [(f["code"], f["file"]) for f in findings] == [
            ("SOURCE_TOOLS_DIFFER", ".rulesync/subagents/engineer.md")]
        assert said in findings[0]["message"] and "governance/kernel/roles/engineer.md" in findings[0]["message"]

    @pytest.mark.parametrize("source", [
        "---\nname: engineer\n---\n\n" + ROLE, "---\nname: engineer\nclaudecode:\n  tools: Read\n---\n\n" + ROLE, ROLE,
    ])
    def test_role_source_without_a_tools_list_is_a_finding(self, project, source):
        _write(project / ".rulesync/subagents/engineer.md", source)
        findings, _count = portability._kernel_findings(project)
        assert [f["code"] for f in findings] == ["SOURCE_TOOLS_DIFFER"] and "claudecode.tools" in findings[0]["message"]

    def test_kernel_role_without_a_tools_field_is_a_finding(self, project):
        for rel in ("governance/kernel/roles/engineer.md", ".rulesync/subagents/engineer.md"):
            path = project / rel
            _write(path, path.read_text(encoding="utf-8").replace("**Tools:**", "**Means:**"))
        findings, _count = portability._kernel_findings(project)
        assert [f["code"] for f in findings] == ["SOURCE_TOOLS_DIFFER"] and "no Tools field" in findings[0]["message"]


class TestToolsDifference:
    FRONT = {"claudecode": {"tools": ["Read", "Edit"]}}

    @pytest.mark.parametrize("body", [
        "- **Tools:** Read and Edit.\n",
        "- **Tools:** Edit; Read for its report only. No installs.\n",
        "* **Tools**: Read,\n  Edit.\n- **Network:** WebFetch runs outside the sandbox.\n",
        "- **Tools:** Read,\n  Edit.\n\nA paragraph naming Bash.\n",
        "- **Purpose:** uses Bash.\n- **Tools:** Read, Edit, `gov launch`, reading and NotebookEditor.\n# Write\n",
    ])
    def test_field_is_read_to_the_end_of_its_indented_lines_by_whole_words(self, body):
        assert portability._tools_difference(body, self.FRONT) == ""

    def test_tool_named_on_a_continuation_line_counts(self):
        difference = portability._tools_difference("- **Tools:** Read, Edit and\n  WebSearch.\n", self.FRONT)
        assert difference == "only in the source [], only in the kernel role ['WebSearch']"

    def test_order_and_repetition_are_free(self):
        front = {"claudecode": {"tools": ["Edit", "Read", "Edit"]}}
        assert portability._tools_difference("- **Tools:** Read, Edit.\n", front) == ""

    def test_empty_list_is_compared_not_skipped(self):
        difference = portability._tools_difference("- **Tools:** Read.\n", {"claudecode": {"tools": []}})
        assert difference == "only in the source [], only in the kernel role ['Read']"

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
    @pytest.fixture()
    def root(self, tmp_path):
        root = tmp_path / "project"
        _write(root / ".rulesync/rules/governance.md", "---\nroot: true\n---\n\n# Rules\n")
        return _generate(root)

    def _codes(self, findings):
        return [(f["code"], f.get("file")) for f in findings]

    def test_project_holding_what_rulesync_writes(self, root, tmp_path):
        assert portability._generated_findings(root, _binary(tmp_path)) == ([], len(GENERATED))

    def test_rulesync_is_given_the_project_s_sources_and_writes_nothing_in_the_project(self, root, tmp_path):
        before = sorted(path for path in root.rglob("*"))
        portability._generated_findings(root, _binary(tmp_path, files={**GENERATED, "new.md": "new\n"}))
        called = (tmp_path / "called.txt").read_text(encoding="utf-8").split()
        assert called[0] == "generate" and called[-2:] == ["--input-roots", str(root / ".rulesync")]
        assert "--delete" not in called and sorted(path for path in root.rglob("*")) == before

    @pytest.mark.parametrize("rule", [None, "# Rules\n", "---\nroot: false\n---\n# Rules\n"])
    def test_no_root_rule_is_a_finding_and_nothing_is_counted(self, root, tmp_path, rule):
        (root / ".rulesync/rules/governance.md").unlink()
        if rule is not None:
            _write(root / ".rulesync/rules/other.md", rule)
        findings, count = portability._generated_findings(root, _binary(tmp_path))
        assert self._codes(findings) == [("ROOT_RULE_ABSENT", None)] and count == 0

    @pytest.mark.parametrize("rel", sorted(GENERATED))
    def test_changed_file_is_one_finding_naming_it(self, root, tmp_path, rel):
        _write(root / rel, GENERATED[rel] + " ")
        findings, count = portability._generated_findings(root, _binary(tmp_path))
        assert self._codes(findings) == [("GENERATED_DIFFERS", rel)] and count == len(GENERATED)

    def test_missing_file_is_a_finding(self, root, tmp_path):
        (root / "CLAUDE.md").unlink()
        assert self._codes(portability._generated_findings(root, _binary(tmp_path))[0]) == [
            ("GENERATED_DIFFERS", "CLAUDE.md")]

    @pytest.mark.parametrize("settings", [
        '{\n  "permissions": {"deny": ["Bash(sudo *)"], "allow": ["WebFetch(domain:example.com)"]}\n}\n',
        '{\n  "permissions": {"deny": ["Bash(sudo *)"], "defaultMode": "bypassPermissions"}\n}\n',
        '{\n  "permissions": {"deny": ["Bash(sudo *)"]}, "env": {"BY_HAND": "1"}\n}\n',
        '{\n  "permissions": {"deny": ["Bash(sudo *)"]}, "hooks": {"Notification": []}\n}\n',
        '{\n  "permissions": {"deny": []}\n}\n',
    ])
    def test_settings_key_added_or_removed_by_hand(self, root, tmp_path, settings):
        _write(root / ".claude/settings.json", settings)
        assert self._codes(portability._generated_findings(root, _binary(tmp_path))[0]) == [
            ("GENERATED_DIFFERS", ".claude/settings.json")]

    @pytest.mark.parametrize("rel", [
        ".claude/agents/by-hand.md", ".claude/skills/by-hand/SKILL.md", ".claude/skills/planning/by-hand.md",
        ".claude/commands/by-hand.md", ".claude/commands/opsx/deep/by-hand.md",
    ])
    def test_file_without_a_source_is_one_finding_naming_it(self, root, tmp_path, rel):
        _write(root / rel, "by hand\n")
        assert self._codes(portability._generated_findings(root, _binary(tmp_path))[0]) == [
            ("GENERATED_WITHOUT_SOURCE", rel)]

    @pytest.mark.parametrize("rel", [
        ".claude/settings.local.json", ".claude/worktrees/w/.claude/agents/by-hand.md", ".claude/other.json",
        "docs/by-hand.md",
    ])
    def test_file_outside_the_generated_folders_is_not_judged(self, root, tmp_path, rel):
        _write(root / rel, "{}\n")
        assert portability._generated_findings(root, _binary(tmp_path)) == ([], len(GENERATED))

    def test_failure_is_reported_with_rulesync_s_reason_and_no_file(self, root, tmp_path):
        binary = _binary(tmp_path, said="plain reason mentioning CLAUDE.md", code=1)
        findings, count = portability._generated_findings(root, binary)
        assert self._codes(findings) == [("RULESYNC_FAILED", None)] and count == 0
        assert "plain reason mentioning CLAUDE.md" in findings[0]["message"]

    def test_long_reason_is_reported_by_its_end(self, root, tmp_path):
        binary = _binary(tmp_path, said="x" * 5000 + " the end", code=1)
        message = portability._generated_findings(root, binary)[0][0]["message"]
        assert message.endswith("the end") and len(message) < 600

    def test_failing_exit_is_a_failure_although_the_files_were_written(self, root, tmp_path):
        findings, count = portability._generated_findings(root, _binary(tmp_path, code=1))
        assert self._codes(findings) == [("RULESYNC_FAILED", None)] and count == 0

    def test_rulesync_that_writes_nothing_is_a_failure_not_a_match(self, root, tmp_path):
        findings, count = portability._generated_findings(root, _binary(tmp_path, files={}))
        assert self._codes(findings) == [("RULESYNC_FAILED", None)] and count == 0
        assert "0 files written" in findings[0]["message"]


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
            "rulesync_version": True, "kernel_files": 4, "generated_files": len(GENERATED)}}

    def test_other_version_stops_before_the_generated_files(self, project, tmp_path, monkeypatch, capsys):
        code, printed = self._run(project, _binary(tmp_path, version="99.0.0"), monkeypatch, capsys)
        assert code == 1
        assert [f["code"] for f in printed["findings"]] == ["RULESYNC_VERSION_DIFFERS"]
        assert "not compared" in printed["findings"][0]["message"]
        assert printed["compared"] == {"rulesync_version": False, "kernel_files": 4, "generated_files": 0}

    def test_kernel_is_compared_also_without_rulesync(self, project, monkeypatch, capsys):
        _write(project / "governance/kernel/roles/engineer.md", ROLE + "More.\n")
        code, printed = self._run(project, "/nonexistent/rulesync", monkeypatch, capsys)
        assert code == 1
        assert [f["code"] for f in printed["findings"]] == ["RULESYNC_ABSENT", "SOURCE_DIFFERS"]

    def test_rulesync_failure_is_not_counted_as_compared(self, project, tmp_path, monkeypatch, capsys):
        binary = _binary(tmp_path, said="stopped", code=1)
        code, printed = self._run(project, binary, monkeypatch, capsys)
        assert code == 1 and printed["compared"]["generated_files"] == 0
