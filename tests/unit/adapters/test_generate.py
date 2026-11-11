"""Builder tests for ``gov adapters generate`` (W2-23 S2). Regression evidence only.

The planted programme is ``fixtures/adopt/programme`` copied into ``tmp_path`` (its settings placed at
``.claude/settings.json`` there). ``rulesync generate`` is replaced by a stand-in that returns fixed generated files
(``merge.generate_into``); the merge, the writing and the command are the code's own.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from gov.adapters import command, merge
from gov.cli import main as cli
from gov.cli.errors import GovError

FIXTURE = Path(__file__).resolve().parents[3] / "fixtures" / "adopt" / "programme"
GENERATED = {
    "CLAUDE.md": b"# Governance\n\nGenerated line one.\n",
    "AGENTS.md": b"# Governance\n\nGenerated agents line.\n",
    ".claude/settings.json": json.dumps({
        "$schema": "https://json.schemastore.org/claude-code-settings.json",
        "permissions": {"allow": ["Bash(git status)", "Read(./**)"], "deny": ["Read(./.env)"]},
        "hooks": {"PreToolUse": [{"matcher": "Edit", "hooks": [{"type": "command", "command": "gov-guard"}]}],
                  "Stop": [{"hooks": [{"type": "command", "command": "gov-stop"}]}]},
    }).encode(),
    ".claude/agents/engineer.md": b"generated agent\n",
    ".claude/skills/audit/SKILL.md": b"generated skill\n",
}


@pytest.fixture()
def programme(tmp_path, monkeypatch):
    root = tmp_path / "EXAMIN APP"
    shutil.copytree(FIXTURE, root)
    (root / ".claude").mkdir()
    shutil.move(str(root / "claude-settings.json"), str(root / ".claude" / "settings.json"))
    (root / "notes.txt").write_text("an untracked file of the programme\n", encoding="utf-8")
    made = dict(GENERATED)
    monkeypatch.setattr(merge, "generate_into", lambda project, folder: dict(made))
    return root, made


def lines(path):
    return [line for line in path.read_text(encoding="utf-8").split("\n") if line.strip()]


def in_order(sub, full):
    position = 0
    for line in sub:
        position = full.index(line, position) + 1
    return True


def test_s2_each_file_keeps_every_programme_line_in_order_and_gains_the_generated_lines(programme):
    root, _ = programme
    own = {rel: lines(root / rel) for rel in ("CLAUDE.md", "AGENTS.md")}
    own_settings = json.loads((root / ".claude/settings.json").read_text())
    result = merge.generate(root)
    assert result["merged"] == ["CLAUDE.md", "AGENTS.md", ".claude/settings.json"]
    for rel, before in own.items():
        after = lines(root / rel)
        assert after[:len(before)] == before and in_order(before, after)
        assert after[len(before)] == merge.BEGIN and after[-1] == merge.END
        assert lines(root / rel)[len(before) + 1:-1] == [line for line in GENERATED[rel].decode().split("\n") if line]
    settings = json.loads((root / ".claude/settings.json").read_text())
    assert list(settings)[:len(own_settings)] == list(own_settings) and "$schema" in settings
    assert settings["model"] == "programme-model"
    assert settings["permissions"]["allow"] == ["Bash(make check)", "Bash(git status)", "Read(./**)"]
    assert settings["permissions"]["deny"] == ["Read(./secrets/**)", "Read(./.env)"]
    assert settings["hooks"]["PreToolUse"][0] == own_settings["hooks"]["PreToolUse"][0]
    assert settings["hooks"]["PreToolUse"][1]["matcher"] == "Edit" and "Stop" in settings["hooks"]
    assert list(settings["env"]) == ["PROGRAMME_FLAG", *merge.AUTO_COMPACT]
    assert (root / "notes.txt").read_text() == "an untracked file of the programme\n"


def test_s2_the_next_run_replaces_the_block_where_it_stands(programme):
    root, made = programme
    merge.generate(root)
    first = {rel: (root / rel).read_text() for rel in ("CLAUDE.md", "AGENTS.md", ".claude/settings.json")}
    merge.generate(root)
    assert {rel: (root / rel).read_text() for rel in first} == first  # the same sources: the same files
    with (root / "CLAUDE.md").open("a", encoding="utf-8") as handle:
        handle.write("- A programme line added after the block.\n")
    made["CLAUDE.md"] = b"# Governance\n\nGenerated line two.\n"
    merge.generate(root)
    text = (root / "CLAUDE.md").read_text()
    assert text.count(merge.BEGIN) == 1 and "Generated line two." in text and "Generated line one." not in text
    assert text.index(merge.END) < text.index("- A programme line added after the block.")
    assert text.startswith((FIXTURE / "CLAUDE.md").read_text())


def test_s2_other_generated_files_are_written_where_absent_and_a_differing_one_is_kept(programme):
    root, _ = programme
    (root / ".claude/agents").mkdir(parents=True)
    (root / ".claude/agents/engineer.md").write_text("the programme's own agent\n")
    result = merge.generate(root)
    assert result["kept"] == [".claude/agents/engineer.md"] and result["written"] == [".claude/skills/audit/SKILL.md"]
    assert (root / ".claude/agents/engineer.md").read_text() == "the programme's own agent\n"


def test_s2_a_project_without_its_own_files_gets_the_generated_ones_in_the_block(programme):
    root, _ = programme
    for rel in ("CLAUDE.md", "AGENTS.md", ".claude/settings.json"):
        (root / rel).unlink()
    merge.generate(root)
    assert lines(root / "CLAUDE.md")[0] == merge.BEGIN
    assert json.loads((root / ".claude/settings.json").read_text())["env"] == merge.AUTO_COMPACT


def test_s2_a_broken_block_or_unreadable_settings_refuse_and_nothing_is_written(programme):
    root, _ = programme
    (root / "AGENTS.md").write_text("own\n" + merge.BEGIN + "\nhalf\n")
    before = {rel: (root / rel).read_bytes() for rel in ("CLAUDE.md", "AGENTS.md", ".claude/settings.json")}
    with pytest.raises(GovError) as caught:
        merge.generate(root)
    assert caught.value.code == "ADAPTERS_BLOCK_BROKEN"
    (root / "AGENTS.md").write_text("own\n")
    (root / ".claude/settings.json").write_text("{not json")
    with pytest.raises(GovError) as caught:
        merge.generate(root)
    assert caught.value.code == "ADAPTERS_SETTINGS_UNREADABLE"
    assert (root / "CLAUDE.md").read_bytes() == before["CLAUDE.md"] and not (root / ".claude/agents").exists()


def test_s2_merge_value_keeps_the_programmes_scalars_and_order():
    own = {"b": 1, "a": {"x": [1, 2]}, "c": "own"}
    assert merge.merge_value(own, {"c": "gen", "a": {"x": [2, 3], "y": 0}, "d": 4}) == {
        "b": 1, "a": {"x": [1, 2, 3], "y": 0}, "c": "own", "d": 4}
    assert list(merge.merge_value(own, {"d": 4, "b": 9})) == ["b", "a", "c", "d"]


def test_s2_the_command_is_found_by_folder_and_runs(programme, capsys):
    root, _ = programme
    assert command.CLASS == "act" and "CLAUDE.md" in command.ACT_PATHS
    code = cli.main(["adapters", "generate", "--root", str(root), "--json"])
    out = capsys.readouterr().out
    assert code == 0 and json.loads(out)["result"]["merged"][0] == "CLAUDE.md"
