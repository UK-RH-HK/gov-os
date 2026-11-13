"""W2-120 (DAEO-i89t): the skill validator's closed front matter (I1 to I4; DEC-995, DEC-996, DEC-1156 (2)).

Each case plants a small project in ``tmp_path``, runs ``skill_validator.main`` with the project as the working
directory and judges the JSON on stdout and the exit. Paths are compared as ``Path`` values, never as text (DEC-1155).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from gov.check import skill_validator

KERNEL = Path("template/governance/kernel/skills")
INSTALLED = Path("governance/kernel/skills")
RULESYNC = Path(".rulesync/skills")
TEMPLATE_RULESYNC = Path("template/.rulesync/skills")
CLAUDE = Path(".claude/skills")

PERMISSION_KEYS = ("allowed-tools", "permissions", "paths", "sandbox", "network", "model", "effort")

FULL = {"name": "x", "version": "1.0.0", "description": "Method for x.", "output": "none",
        "metadata": {"version": "1.0.0"}}
GENERATED = {"name": "x", "description": "Method for x.", "metadata": {"version": "1.0.0"}}


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


def plant(root: Path, folder: Path, name: str, front, body: str = "Body.\n", raw: str | None = None) -> Path:
    path = root / folder / name / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    text = raw if raw is not None else "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n" + body
    path.write_text(text, encoding="utf-8")
    return path


def run(capsys, *argv: str) -> tuple[int, dict]:
    code = skill_validator.main(list(argv))
    return code, json.loads(capsys.readouterr().out)


def kernel_one(capsys, name: str = "x"):
    return run(capsys, "--both-layouts", str(KERNEL / name))


def same_file(finding: dict, expected: Path) -> bool:
    return Path(finding["file"]).resolve() == expected.resolve()


def codes(out: dict) -> list[str]:
    return [f["code"] for f in out["findings"]]


# ---- a clean skill, and a project with no generated folders -------------------------------------------------

def test_clean_kernel_skill_with_no_generated_folders_passes(project, capsys):
    plant(project, KERNEL, "x", FULL)
    code, out = kernel_one(capsys)
    assert (code, out) == (0, {"findings": []})


def test_clean_kernel_skill_and_clean_copies_pass(project, capsys):
    plant(project, KERNEL, "x", FULL)
    plant(project, RULESYNC, "x", FULL)
    plant(project, TEMPLATE_RULESYNC, "x", FULL)
    plant(project, CLAUDE, "x", GENERATED)
    code, out = kernel_one(capsys)
    assert (code, out) == (0, {"findings": []})


def test_missing_output_is_not_refused(project, capsys):
    front = {k: v for k, v in FULL.items() if k != "output"}
    plant(project, KERNEL, "x", front)
    code, out = kernel_one(capsys)
    assert (code, out) == (0, {"findings": []})


# ---- I2: permission keys and keys outside the list, on the kernel copy --------------------------------------

@pytest.mark.parametrize("key", PERMISSION_KEYS)
def test_permission_key_in_kernel_copy_is_refused_with_file_and_key(project, capsys, key):
    path = plant(project, KERNEL, "x", {**FULL, key: "anything"})
    code, out = kernel_one(capsys)
    assert code == 1
    assert len(out["findings"]) == 1
    finding = out["findings"][0]
    assert finding["key"] == key
    assert finding["code"] == "SKILL_PERMISSION_KEY"
    assert same_file(finding, path)
    assert key in finding["message"]


def test_other_key_in_kernel_copy_is_refused_as_unlisted(project, capsys):
    path = plant(project, KERNEL, "x", {**FULL, "license": "MIT"})
    code, out = kernel_one(capsys)
    assert code == 1
    (finding,) = out["findings"]
    assert (finding["code"], finding["key"]) == ("SKILL_UNLISTED_KEY", "license")
    assert same_file(finding, path)


def test_metadata_key_other_than_version_is_refused(project, capsys):
    plant(project, KERNEL, "x", {**FULL, "metadata": {"version": "1.0.0", "author": "me"}})
    code, out = kernel_one(capsys)
    assert code == 1
    (finding,) = out["findings"]
    assert (finding["code"], finding["key"]) == ("SKILL_UNLISTED_KEY", "metadata.author")


def test_each_refused_key_is_one_finding(project, capsys):
    plant(project, KERNEL, "x", {**FULL, "allowed-tools": "Bash", "model": "opus", "color": "red"})
    code, out = kernel_one(capsys)
    assert code == 1
    assert sorted(f["key"] for f in out["findings"]) == ["allowed-tools", "color", "model"]


# ---- I2 and I3: every generated copy is read ----------------------------------------------------------------

@pytest.mark.parametrize("folder", [RULESYNC, TEMPLATE_RULESYNC])
def test_permission_key_in_a_rulesync_copy_is_refused(project, capsys, folder):
    plant(project, KERNEL, "x", FULL)
    path = plant(project, folder, "x", {**FULL, "allowed-tools": "Bash"})
    code, out = kernel_one(capsys)
    assert code == 1
    (finding,) = out["findings"]
    assert (finding["code"], finding["key"]) == ("SKILL_PERMISSION_KEY", "allowed-tools")
    assert same_file(finding, path)


def test_rulesync_copy_keeps_the_template_list_including_output(project, capsys):
    plant(project, KERNEL, "x", FULL)
    plant(project, RULESYNC, "x", FULL)
    code, out = kernel_one(capsys)
    assert code == 0 and out == {"findings": []}


def test_rulesync_copy_still_needs_a_version(project, capsys):
    plant(project, KERNEL, "x", FULL)
    path = plant(project, RULESYNC, "x", {k: v for k, v in FULL.items() if k != "version"})
    code, out = kernel_one(capsys)
    assert code == 1
    (finding,) = out["findings"]
    assert (finding["code"], finding["key"]) == ("SKILL_MISSING_VERSION", "version")
    assert same_file(finding, path)


def test_claude_copy_with_a_permission_key_is_refused(project, capsys):
    plant(project, KERNEL, "x", FULL)
    path = plant(project, CLAUDE, "x", {**GENERATED, "allowed-tools": "Bash"})
    code, out = kernel_one(capsys)
    assert code == 1
    (finding,) = out["findings"]
    assert (finding["code"], finding["key"]) == ("SKILL_PERMISSION_KEY", "allowed-tools")
    assert same_file(finding, path)


@pytest.mark.parametrize("key", ["version", "output"])
def test_claude_copy_list_is_name_description_and_metadata_only(project, capsys, key):
    plant(project, KERNEL, "x", FULL)
    path = plant(project, CLAUDE, "x", {**GENERATED, key: "1.0.0" if key == "version" else "none"})
    code, out = kernel_one(capsys)
    assert code == 1
    (finding,) = out["findings"]
    assert (finding["code"], finding["key"]) == ("SKILL_UNLISTED_KEY", key)
    assert same_file(finding, path)


def test_claude_copy_needs_no_version_and_no_metadata(project, capsys):
    plant(project, KERNEL, "x", FULL)
    plant(project, CLAUDE, "x", {"name": "x", "description": "Method for x."})
    code, out = kernel_one(capsys)
    assert (code, out) == (0, {"findings": []})


def test_single_kernel_folder_reads_only_its_own_copies(project, capsys):
    plant(project, KERNEL, "x", FULL)
    plant(project, KERNEL, "y", FULL)
    plant(project, CLAUDE, "y", {**GENERATED, "name": "y", "model": "opus"})
    code, out = kernel_one(capsys, "x")
    assert (code, out) == (0, {"findings": []})


def test_skills_root_reads_every_generated_folder_that_exists(project, capsys):
    plant(project, KERNEL, "x", FULL)
    plant(project, KERNEL, "y", FULL)
    claude = plant(project, CLAUDE, "y", {**GENERATED, "name": "y", "model": "opus"})
    rulesync = plant(project, RULESYNC, "x", {**FULL, "effort": "high"})
    code, out = run(capsys, "--both-layouts", str(KERNEL))
    assert code == 1
    found = {(Path(f["file"]).resolve(), f["key"]) for f in out["findings"]}
    assert found == {(claude.resolve(), "model"), (rulesync.resolve(), "effort")}


def test_both_layouts_do_not_report_a_generated_copy_twice(project, capsys):
    plant(project, KERNEL, "x", FULL)
    plant(project, INSTALLED, "x", FULL)
    plant(project, CLAUDE, "x", {**GENERATED, "model": "opus"})
    code, out = kernel_one(capsys)
    assert code == 1
    assert [f["key"] for f in out["findings"]] == ["model"]


def test_installed_kernel_layout_is_read_too(project, capsys):
    plant(project, KERNEL, "x", FULL)
    path = plant(project, INSTALLED, "x", {**FULL, "sandbox": "off"})
    code, out = kernel_one(capsys)
    assert code == 1
    (finding,) = out["findings"]
    assert finding["key"] == "sandbox" and same_file(finding, path)


# ---- I4: vendored skills are named, the exit stays ----------------------------------------------------------

def test_single_kernel_folder_reaches_no_vendored_skill(project, capsys):
    plant(project, KERNEL, "x", FULL)
    plant(project, CLAUDE, "openspec-apply", {"name": "openspec-apply", "description": "d", "allowed-tools": "Bash"})
    code, out = kernel_one(capsys)
    assert (code, out) == (0, {"findings": []})


def test_vendored_generated_copy_is_named_and_the_exit_stays_zero(project, capsys):
    plant(project, KERNEL, "x", FULL)
    path = plant(project, CLAUDE, "openspec-apply", {
        "name": "openspec-apply", "description": "d", "allowed-tools": "Bash(openspec:*)", "license": "MIT",
        "metadata": {"author": "openspec", "version": "1.0"}})
    code, out = run(capsys, "--both-layouts", str(KERNEL))
    assert code == 0
    assert codes(out) == ["SKILL_VENDORED_KEY"] * 3
    assert sorted(f["key"] for f in out["findings"]) == ["allowed-tools", "license", "metadata.author"]
    assert all(same_file(f, path) and f["message"] for f in out["findings"])


def test_vendored_kernel_superpowers_skill_is_named_and_needs_no_version(project, capsys):
    plant(project, KERNEL, "x", FULL)
    path = plant(project, KERNEL / "superpowers", "tdd", {"name": "tdd", "description": "d", "model": "opus"})
    code, out = run(capsys, "--both-layouts", str(KERNEL))
    assert code == 0
    (finding,) = out["findings"]
    assert (finding["code"], finding["key"]) == ("SKILL_VENDORED_KEY", "model")
    assert same_file(finding, path)


def test_vendored_finding_does_not_hide_a_refusing_one(project, capsys):
    plant(project, KERNEL, "x", {**FULL, "paths": "src"})
    plant(project, CLAUDE, "openspec-apply", {"name": "openspec-apply", "description": "d", "allowed-tools": "Bash"})
    code, out = run(capsys, "--both-layouts", str(KERNEL))
    assert code == 1
    assert sorted(codes(out)) == ["SKILL_PERMISSION_KEY", "SKILL_VENDORED_KEY"]


def test_clean_vendored_skill_gives_no_finding(project, capsys):
    plant(project, KERNEL, "x", FULL)
    plant(project, CLAUDE, "openspec-apply", {"name": "openspec-apply", "description": "d"})
    code, out = run(capsys, "--both-layouts", str(KERNEL))
    assert (code, out) == (0, {"findings": []})


# ---- I1: every finding carries code, file, key and message --------------------------------------------------

def test_every_old_finding_carries_code_file_key_and_message(project, capsys):
    folder = project / KERNEL
    plant(project, KERNEL, "nofm", None, raw="no front matter\n")
    plant(project, KERNEL, "missing", {"name": "missing", "version": "1.0.0"})
    plant(project, KERNEL, "invalid", {"name": "invalid", "version": 1, "description": ""})
    plant(project, KERNEL, "long", {**FULL, "name": "long", "description": "word " * 400}, body="b " * 6000)
    plant(project, KERNEL, "cmd", {**FULL, "name": "cmd"}, body="Run `gov nosuchcommand` now.\n")
    code, out = run(capsys, str(folder))
    assert code == 1
    for finding in out["findings"]:
        assert set(finding) == {"code", "file", "key", "message"}
        assert finding["file"] and finding["message"]
        assert Path(finding["file"]).resolve().is_relative_to(folder.resolve())
    by_code = {f["code"]: f for f in out["findings"]}
    assert set(by_code) == {"SKILL_NO_FRONTMATTER", "SKILL_MISSING_FIELD", "SKILL_INVALID_FIELD",
                            "SKILL_DESCRIPTION_TOO_LONG", "SKILL_BODY_TOO_LONG", "SKILL_UNKNOWN_COMMAND"}
    assert by_code["SKILL_NO_FRONTMATTER"]["key"] is None
    assert by_code["SKILL_MISSING_FIELD"]["key"] == "description"
    assert by_code["SKILL_DESCRIPTION_TOO_LONG"]["key"] == "description"
    assert by_code["SKILL_BODY_TOO_LONG"]["key"] == "body"
    assert by_code["SKILL_UNKNOWN_COMMAND"]["key"] == "body"


def test_missing_version_finding_names_the_version_key(project, capsys):
    plant(project, KERNEL, "x", {k: v for k, v in FULL.items() if k != "version"})
    code, out = kernel_one(capsys)
    assert code == 1
    (finding,) = out["findings"]
    assert (finding["code"], finding["key"]) == ("SKILL_MISSING_VERSION", "version")


# ---- exit and unmeasured stay ---------------------------------------------------------------------------------

def test_folder_with_no_skill_is_still_unmeasured(project, capsys):
    (project / "empty").mkdir()
    assert skill_validator.main([str(project / "empty")]) == 1
    assert json.loads(capsys.readouterr().out)["unmeasured"] is True


def test_no_arguments_is_still_unmeasured(project, capsys):
    assert skill_validator.main([]) == 1
    assert json.loads(capsys.readouterr().out)["unmeasured"] is True
