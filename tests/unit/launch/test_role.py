"""Builder tests for the role a worker is launched as (W2-60a).

Regression evidence only (DEC-136). They cover what the acceptance tests leave
to the builder: the line forms read from the role file, the text appended, the
skill description, and the arguments the launcher sets itself.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.launch import launcher, role  # noqa: E402

VERSION = "- **Version:** 1.2.3"
DEFAULT = "- **Launch default:** model claude-opus-5-5, effort high"


def _tree(tmp_path, *lines, skills=None):
    roles = tmp_path / role.ROLES_REL
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
