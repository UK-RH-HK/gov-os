"""W2-208 F1 (DAEO-kt8e): ``KIT_TEXT_GUARD_IN_FORCE``, a kit file that names the guard, the sandbox or a permission
prompt as in force. Builder evidence.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gov.adapters import portability

HEAD = ".rulesync/rules/governance.md"
FRONT = "---\nroot: true\n---\n\n# Governance\n\n"


def _write(root: Path, rel: str, text: str) -> None:
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(text, encoding="utf-8")


@pytest.mark.parametrize("line", [
    "Six roles operate under the guard:",
    "## Guard",
    "Each session runs inside the sandbox.",
    "When a permission prompt appears, answer it.",
    "The Sandbox decides.",
    "Permission prompts are answered by the owner.",
])
def test_a_line_naming_one_as_in_force_is_a_finding_with_its_file_and_line(tmp_path, line):
    _write(tmp_path, HEAD, FRONT + line + "\n")
    assert portability.kit_text_findings(tmp_path) == [
        {"code": "KIT_TEXT_GUARD_IN_FORCE", "file": HEAD, "line": 7,
         "message": f"names the guard, the sandbox or a permission prompt as in force: {line}"}]


@pytest.mark.parametrize("line", [
    "- **Trust, then catch and correct; do not prevent.** No guard, no sandbox, no permission prompts.",
    "The guard was retired (EMERGENCY-2 6.1); the sandbox is retired too.",
    "Gov OS guards against honest agent mistakes.",
    "A guarded path, a safeguard and a guardrail are other words.",
])
def test_a_line_saying_they_are_retired_or_using_another_word_is_no_finding(tmp_path, line):
    _write(tmp_path, HEAD, FRONT + line + "\n")
    assert portability.kit_text_findings(tmp_path) == []


def test_every_file_of_the_fixed_list_is_read_and_others_are_not(tmp_path):
    files = (HEAD, ".rulesync/skills/judging-work/SKILL.md", "governance/kernel/skills/judging-work/SKILL.md",
             ".rulesync/permissions.jsonc", "governance/kernel/settings.json")
    for rel in files:
        _write(tmp_path, rel, "under the guard\n")
    _write(tmp_path, ".rulesync/skills/other/SKILL.md", "under the guard\n")
    assert [(f["file"], f["line"]) for f in portability.kit_text_findings(tmp_path)] == [(rel, 1) for rel in files]


def test_main_exits_non_zero_on_a_finding_for_a_project_with_the_head(tmp_path, monkeypatch, capsys):
    _write(tmp_path, HEAD, FRONT + "Six roles operate under the guard:\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("RULESYNC_BIN", str(tmp_path / "no-rulesync"))
    assert portability.main() == 1
    found = json.loads(capsys.readouterr().out)["findings"]
    assert {"code": "KIT_TEXT_GUARD_IN_FORCE", "file": HEAD, "line": 7} in [
        {key: f.get(key) for key in ("code", "file", "line")} for f in found]


def test_the_kit_s_own_head_skill_and_permission_files_give_no_finding():
    template = Path(__file__).resolve().parents[3] / "template"
    assert portability.kit_text_findings(template) == []
