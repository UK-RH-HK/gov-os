"""Builder tests for the role a worker is launched as (W2-60a).

Regression evidence only (DEC-136). They cover what the acceptance tests leave
to the builder: the line forms read from the role file, the text appended, the
skill description, and the arguments the launcher sets itself.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.launch import launcher, role  # noqa: E402

VERSION = "- **Version:** 1.2.3"
DEFAULT = "- **Launch default:** model claude-opus-5-5, effort high"


def _tree(tmp_path, *lines, skills=None, roles_rel=role.ROLES_REL):
    roles = tmp_path / roles_rel
    roles.mkdir(parents=True)
    (roles / "engineer.md").write_text("# Engineer\n\n" + "\n".join(lines) + "\n", encoding="utf-8")
    for name, text in (skills or {}).items():
        folder = tmp_path / role.SKILLS_REL / name
        folder.mkdir(parents=True)
        (folder / "SKILL.md").write_text(text, encoding="utf-8")
    return tmp_path


def test_the_lines_give_the_version_model_and_effort(tmp_path):
    loaded = role.read_role(_tree(tmp_path, VERSION, DEFAULT), "engineer")
    assert (loaded["role_text"]["version"], loaded["model"], loaded["effort"]) == ("1.2.3", "claude-opus-5-5", "high")
    assert loaded["role_text"]["path"] == f"{role.ROLES_REL}/engineer.md"
    assert loaded["appended"] == (tmp_path / role.ROLES_REL / "engineer.md").read_bytes()


def test_an_adopted_tree_with_no_template_reads_its_kernel_s_role_file(tmp_path):
    loaded = role.read_role(_tree(tmp_path, VERSION, DEFAULT, roles_rel=role.ADOPTED_ROLES_REL), "engineer")
    data = (tmp_path / role.ADOPTED_ROLES_REL / "engineer.md").read_bytes()
    assert loaded["role_text"] == {"path": f"{role.ADOPTED_ROLES_REL}/engineer.md", "version": "1.2.3",
                                   "sha256": role.sha256(data)}
    assert loaded["appended"] == data


def test_where_template_exists_its_role_file_is_read_and_no_other(tmp_path):
    tree = _tree(tmp_path, VERSION, DEFAULT)
    _tree(tmp_path, "- **Version:** 9.9.9", DEFAULT, roles_rel=role.ADOPTED_ROLES_REL)
    assert role.read_role(tree, "engineer")["role_text"]["path"] == f"{role.ROLES_REL}/engineer.md"
    (tree / role.ROLES_REL / "engineer.md").unlink()
    with pytest.raises(GovError, match=role.ROLES_REL):
        role.read_role(tree, "engineer")


def test_a_tree_with_neither_role_file_refuses(tmp_path):
    with pytest.raises(GovError, match=role.ADOPTED_ROLES_REL):
        role.read_role(tmp_path, "engineer")


@pytest.mark.parametrize("lines", (
    (DEFAULT,),
    (VERSION,),
    (VERSION, DEFAULT, DEFAULT),
    (VERSION, "- **Launch default:** model claude-opus-5-5, effort high, threshold none"),
    (VERSION, "- **Launch default:** model claude-, effort high"),
    ("- **Version:** 1.2", DEFAULT),
    (VERSION, DEFAULT, "- **Skills:** change,audit"),
    (VERSION, DEFAULT, "- **Skills:** change, change"),
))
def test_a_line_missing_twice_or_of_another_form_refuses(tmp_path, lines):
    with pytest.raises(GovError):
        role.read_role(_tree(tmp_path, *lines), "engineer")


def test_named_skills_follow_the_role_text_in_the_order_named(tmp_path):
    skills = {"b": "---\nname: b\nversion: 1.0.0\n---\nB\n", "a": "---\nname: a\nversion: 2.0.0\n---\nA",
              "c": "no front matter\n"}
    loaded = role.read_role(_tree(tmp_path, VERSION, DEFAULT, "- **Skills:** b, a", skills=skills), "engineer")
    assert loaded["appended"].endswith(b"B\n---\nname: a\nversion: 2.0.0\n---\nA\n")
    described = {skill["name"]: skill for skill in loaded["skills"]}
    assert (described["a"]["named"], described["b"]["named"], described["c"]["named"]) == (True, True, False)
    assert described["c"]["version"] == role.NO_VERSION


@pytest.mark.parametrize("front, expected", (
    ("version: 1.0.0\n", "1.0.0"),
    ("metadata:\n  version: 1.4.0\n", "1.4.0"),
    ("version: 2.0.0\nmetadata:\n  version: 1.4.0\n", "2.0.0"),
    ("metadata: 1.4.0\n", role.NO_VERSION),
    ("metadata:\n  - version: 1.4.0\n", role.NO_VERSION),
    ("metadata:\n  author: x\n", role.NO_VERSION),
    ("description: x\n", role.NO_VERSION),
))
def test_a_skill_s_version_is_its_own_else_its_metadata_s(tmp_path, front, expected):
    text = f"---\nname: a\n{front}---\nA\n"
    command = f"---\n{front}---\nC\n"
    tree = _tree(tmp_path, VERSION, DEFAULT, skills={"a": text})
    (tree / role.COMMANDS_REL).mkdir(parents=True)
    (tree / role.COMMANDS_REL / "c.md").write_text(command, encoding="utf-8")
    described = {skill["name"]: skill for skill in role.read_role(tree, "engineer")["skills"]}
    assert (described["a"]["version"], described["c"]["version"]) == (expected, expected)
    assert described["a"]["sha256"] == role.sha256(text.encode())


def test_a_named_skill_versioned_under_metadata_loads(tmp_path):
    text = "---\nname: a\nmetadata:\n  version: 1.4.0\n---\nA\n"
    loaded = role.read_role(_tree(tmp_path, VERSION, DEFAULT, "- **Skills:** a", skills={"a": text}), "engineer")
    assert [(s["name"], s["version"], s["named"]) for s in loaded["skills"]] == [("a", "1.4.0", True)]
    assert loaded["appended"].endswith(text.encode())


@pytest.mark.parametrize("front", ("", "metadata: 1.4.0\n", "metadata:\n  author: x\n"))
def test_a_named_skill_with_no_version_in_either_place_refuses(tmp_path, front):
    tree = _tree(tmp_path, VERSION, DEFAULT, "- **Skills:** a", skills={"a": f"---\nname: a\n{front}---\n"})
    with pytest.raises(GovError, match="carries no version"):
        role.read_role(tree, "engineer")


def test_the_folder_hash_follows_a_file_beside_skill_md(tmp_path):
    tree = _tree(tmp_path, VERSION, DEFAULT, skills={"a": "---\nname: a\n---\n"})
    before = role.read_role(tree, "engineer")["skills"][0]["folder_sha256"]
    (tree / role.SKILLS_REL / "a" / "notes.md").write_text("x", encoding="utf-8")
    after = role.read_role(tree, "engineer")["skills"][0]
    assert after["folder_sha256"] != before and after["sha256"] == role.sha256(b"---\nname: a\n---\n")


def test_a_named_skill_in_a_folder_of_another_name_refuses(tmp_path):
    tree = _tree(tmp_path, VERSION, DEFAULT, "- **Skills:** a", skills={"z": "---\nname: a\nversion: 1.0.0\n---\n"})
    with pytest.raises(GovError):
        role.read_role(tree, "engineer")


def test_command_files_are_skills_named_by_their_path(tmp_path):
    tree = _tree(tmp_path, VERSION, DEFAULT, skills={"a": "---\nname: a\n---\n"})
    commands = tree / role.COMMANDS_REL
    (commands / "ns").mkdir(parents=True)
    (commands / "top.md").write_text("---\nversion: 1.0.0\n---\nTop\n", encoding="utf-8")
    (commands / "ns" / "inner.md").write_text("Inner\n", encoding="utf-8")
    (commands / "notes.txt").write_text("not a command\n", encoding="utf-8")
    described = {skill["name"]: skill for skill in role.read_role(tree, "engineer")["skills"]}
    assert sorted(described) == ["a", "ns:inner", "top"]
    assert (described["top"]["path"], described["top"]["version"]) == (f"{role.COMMANDS_REL}/top.md", "1.0.0")
    assert (described["ns:inner"]["version"], described["ns:inner"]["named"]) == (role.NO_VERSION, False)
    assert described["ns:inner"]["sha256"] == role.sha256(b"Inner\n")


@pytest.mark.parametrize("make", (
    lambda c: (c / "x.md").symlink_to(c / "y.md"),
    lambda c: (c / "ns").symlink_to(c),
    lambda c: (c / "bad.md").write_text("---\n: [\n---\n", encoding="utf-8"),
))
def test_a_command_the_record_could_not_describe_refuses(tmp_path, make):
    tree = _tree(tmp_path, VERSION, DEFAULT)
    commands = tree / role.COMMANDS_REL
    commands.mkdir(parents=True)
    (commands / "y.md").write_text("Y\n", encoding="utf-8")
    make(commands)
    with pytest.raises(GovError):
        role.read_role(tree, "engineer")


def test_a_named_skill_is_never_a_command(tmp_path):
    tree = _tree(tmp_path, VERSION, DEFAULT, "- **Skills:** top")
    (tree / role.COMMANDS_REL).mkdir(parents=True)
    (tree / role.COMMANDS_REL / "top.md").write_text("---\nversion: 1.0.0\n---\n", encoding="utf-8")
    with pytest.raises(GovError):
        role.read_role(tree, "engineer")


def test_the_user_rules_are_ask_and_deny_only(tmp_path):
    assert role.user_rules(tmp_path) == {"ask": [], "deny": []}
    (tmp_path / ".claude").mkdir()
    settings = tmp_path / role.USER_SETTINGS_REL
    settings.write_text('{"model": "x", "permissions": {"allow": ["Bash"], "defaultMode": "acceptEdits", '
                        '"ask": ["Bash(rm:*)"]}}', encoding="utf-8")
    assert role.user_rules(tmp_path) == {"ask": ["Bash(rm:*)"], "deny": []}


@pytest.mark.parametrize("text", ("{", "[]", '{"permissions": []}', '{"permissions": {"ask": "Bash"}}',
                                  '{"permissions": {"deny": [1]}}', '{"permissions": {"ask": null}}'))
def test_a_user_settings_file_of_another_shape_refuses(tmp_path, text):
    (tmp_path / ".claude").mkdir()
    (tmp_path / role.USER_SETTINGS_REL).write_text(text, encoding="utf-8")
    with pytest.raises(GovError):
        role.user_rules(tmp_path)


@pytest.mark.parametrize("args", (["--fallback-model", "claude-x"], ["--fallback-model=claude-x"], ["--chrome"],
                                  ["--ide"], ["--system-prompt-snapshot", "s"], ["--system-prompt-snapshot=s"]))
def test_a_model_connector_or_prompt_argument_refuses(args):
    with pytest.raises(GovError):
        launcher._check_own_args(args)


def test_no_chrome_passes():
    assert launcher._check_own_args(["--no-chrome"]) == {"model": None, "effort": None, "resume": None}


@pytest.mark.parametrize("settings", (
    {"env": {"CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50"}},
    {"env": {"CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS": "1"}},
    {"modelSettings": {"claude-opus-5-5": {"autoCompactWindow": 1}}},
    {"modelSettings": []},
    {"modelSettings": {"claude-opus-5-5": 1}},
))
def test_a_compaction_threshold_in_the_repository_settings_refuses(tmp_path, settings):
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude/settings.local.json").write_text(json.dumps(settings), encoding="utf-8")
    with pytest.raises(GovError, match="compaction threshold"):
        launcher._check_repository_settings(tmp_path)


@pytest.mark.parametrize("args, expected", (
    ([], {"model": None, "effort": None, "resume": None}),
    (["--model=claude-x", "--effort", "max"], {"model": "claude-x", "effort": "max", "resume": None}),
    (["-p", "say --agent", "-r", "1ecc24ab-3710-4228-8258-619022e4b679"],
     {"model": None, "effort": None, "resume": "1ecc24ab-3710-4228-8258-619022e4b679"}),
))
def test_the_arguments_given_are_read(args, expected):
    assert launcher._check_own_args(args) == expected


@pytest.mark.parametrize("args", (
    ["--model", "--effort", "high"], ["--effort", "high", "--effort=high"], ["--resume", "x"], ["-rabc"], ["-pc"],
    ["--resume=1ecc24ab-3710-4228-8258-619022e4b679", "--resume", "1ecc24ab-3710-4228-8258-619022e4b679"],
))
def test_a_form_the_launcher_cannot_name_refuses(args):
    with pytest.raises(GovError):
        launcher._check_own_args(args)
