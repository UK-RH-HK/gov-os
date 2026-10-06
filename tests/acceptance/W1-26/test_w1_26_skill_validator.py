"""Generic skill-file validator (DEC-439, KPI line 7).

Tests the standalone ``python3 -m gov.check.skill_validator`` command that
validates skill files for frontmatter correctness, token limits, and
gov-command references.
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_26_support as support  # noqa: E402

REPO_ROOT = support.REPO_ROOT
SRC = support.SRC
TIMEOUT_S = 30.0


# --------------------------------------------------------------------------
# Runner helper
# --------------------------------------------------------------------------

def run_skill_validator(*args: str, cwd: str | Path | None = None) -> subprocess.CompletedProcess:
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": os.environ.get("HOME", "/tmp"),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(SRC),
    }
    cmd = [sys.executable, "-m", "gov.check.skill_validator", *args]
    return subprocess.run(
        cmd,
        cwd=str(cwd or REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=TIMEOUT_S,
        stdin=subprocess.DEVNULL,
        env=env,
    )


def parse_output(result: subprocess.CompletedProcess) -> dict:
    """Parse JSON from stdout.  Returns empty dict on non-JSON output."""
    text = result.stdout.strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"_raw": text}


# --------------------------------------------------------------------------
# Skill-file builders
# --------------------------------------------------------------------------

def make_skill(
    tmp_path: Path,
    name: str = "test-skill",
    version: str = "1.0.0",
    description: str = "A test skill",
    body: str = "This skill does things.\n",
    *,
    include_name: bool = True,
    include_version: bool = True,
    include_description: bool = True,
    frontmatter_extra: str = "",
    raw: str | None = None,
) -> Path:
    """Write a skill .md file and return its path."""
    if raw is not None:
        path = tmp_path / name / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(raw, encoding="utf-8")
        return path

    lines = ["---"]
    if include_name:
        lines.append(f"name: {name}")
    if include_version:
        lines.append(f"version: {version}")
    if include_description:
        lines.append(f"description: {description}")
    if frontmatter_extra:
        lines.append(frontmatter_extra)
    lines.append("---")
    lines.append("")
    lines.append(body)
    path = tmp_path / name / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# 1. Valid skill file passes (exit 0)
# --------------------------------------------------------------------------

class TestValidSkillFile:

    def test_valid_skill_file_passes(self, tmp_path):
        """A well-formed skill file with all required fields, body under
        2500 tokens, description under 60 tokens, and only known gov
        commands exits 0."""
        path = make_skill(
            tmp_path,
            name="good-skill",
            version="2.1.0",
            description="A valid skill",
            body="Use `gov check` to verify.\n",
        )
        result = run_skill_validator(str(path))
        assert result.returncode == 0, (
            f"valid skill file should pass (exit 0) but got exit {result.returncode}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_valid_skill_folder_passes(self, tmp_path):
        """Passing a folder containing a valid SKILL.md exits 0."""
        path = make_skill(tmp_path, name="folder-skill")
        folder = path.parent
        result = run_skill_validator(str(folder))
        assert result.returncode == 0, (
            f"valid skill folder should pass (exit 0) but got exit {result.returncode}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


# --------------------------------------------------------------------------
# 2. Missing frontmatter is red
# --------------------------------------------------------------------------

class TestMissingFrontmatter:

    def test_no_frontmatter_delimiters(self, tmp_path):
        """A .md file with no --- delimiters produces a finding."""
        path = make_skill(tmp_path, name="no-front", raw="# No frontmatter\n\nJust text.\n")
        result = run_skill_validator(str(path))
        assert result.returncode != 0, (
            f"file without frontmatter should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )
        output = parse_output(result)
        findings = output.get("findings", [])
        assert len(findings) >= 1, (
            f"expected at least one finding for missing frontmatter\n"
            f"output: {output}"
        )

    def test_unclosed_frontmatter(self, tmp_path):
        """A .md file with an opening --- but no closing --- is invalid."""
        path = make_skill(tmp_path, name="unclosed", raw="---\nname: broken\nversion: 1\nBody text.\n")
        result = run_skill_validator(str(path))
        assert result.returncode != 0, (
            f"file with unclosed frontmatter should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )


# --------------------------------------------------------------------------
# 3. Missing version is red
# --------------------------------------------------------------------------

class TestMissingVersion:

    def test_no_version_field(self, tmp_path):
        """Frontmatter without a ``version`` field produces a finding."""
        path = make_skill(
            tmp_path,
            name="no-ver",
            include_version=False,
        )
        result = run_skill_validator(str(path))
        assert result.returncode != 0, (
            f"skill without version should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )
        output = parse_output(result)
        findings = output.get("findings", [])
        assert any("version" in json.dumps(f).lower() for f in findings), (
            f"expected a finding mentioning 'version'\nfindings: {findings}"
        )

    def test_empty_version_field(self, tmp_path):
        """A ``version:`` with no value is equivalent to missing."""
        path = make_skill(
            tmp_path,
            name="empty-ver",
            raw="---\nname: empty-ver\nversion:\ndescription: Short\n---\n\nBody.\n",
        )
        result = run_skill_validator(str(path))
        assert result.returncode != 0, (
            f"skill with empty version should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )


# --------------------------------------------------------------------------
# 4. Description over 60 tokens is red
# --------------------------------------------------------------------------

class TestDescriptionTooLong:

    def test_description_over_60_tokens(self, tmp_path):
        """A description longer than 60 tokens (ceil(len/4)) fails."""
        # 60 tokens = 240 chars.  Use 250 chars to be safely over.
        long_desc = "A" * 250
        path = make_skill(
            tmp_path,
            name="long-desc",
            description=long_desc,
        )
        result = run_skill_validator(str(path))
        assert result.returncode != 0, (
            f"skill with 250-char description ({250 // 4 + 1} tokens) should fail "
            f"but got exit 0\nstdout: {result.stdout}"
        )
        output = parse_output(result)
        findings = output.get("findings", [])
        assert any("description" in json.dumps(f).lower() for f in findings), (
            f"expected a finding mentioning 'description'\nfindings: {findings}"
        )

    def test_description_at_60_tokens_passes(self, tmp_path):
        """A description at exactly 60 tokens (240 chars) passes."""
        desc_240 = "B" * 240
        path = make_skill(tmp_path, name="ok-desc", description=desc_240)
        result = run_skill_validator(str(path))
        output = parse_output(result)
        findings = output.get("findings", [])
        desc_findings = [f for f in findings if "description" in json.dumps(f).lower()]
        assert not desc_findings, (
            f"description at exactly 60 tokens (240 chars) should not produce "
            f"a description finding\nfindings: {desc_findings}"
        )


# --------------------------------------------------------------------------
# 5. Body over 2500 tokens is red
# --------------------------------------------------------------------------

class TestBodyTooLong:

    def test_body_over_2500_tokens(self, tmp_path):
        """A body longer than 2500 tokens (ceil(len/4) > 2500, i.e. > 10000 chars) fails."""
        # 2500 tokens = 10000 chars.  Use 10004 to be safely over.
        long_body = "X" * 10004
        path = make_skill(
            tmp_path,
            name="long-body",
            body=long_body,
        )
        result = run_skill_validator(str(path))
        assert result.returncode != 0, (
            f"skill with >2500-token body should fail "
            f"but got exit 0\nstdout: {result.stdout[:200]}"
        )
        output = parse_output(result)
        findings = output.get("findings", [])
        assert any("body" in json.dumps(f).lower() or "token" in json.dumps(f).lower()
                    for f in findings), (
            f"expected a finding mentioning 'body' or 'token'\nfindings: {findings}"
        )

    def test_body_at_2500_tokens_passes(self, tmp_path):
        """A body at exactly 2500 tokens (10000 chars) passes."""
        body_10000 = "Y" * 10000
        path = make_skill(tmp_path, name="ok-body", body=body_10000)
        result = run_skill_validator(str(path))
        output = parse_output(result)
        findings = output.get("findings", [])
        body_findings = [f for f in findings
                         if "body" in json.dumps(f).lower() or "token" in json.dumps(f).lower()]
        assert not body_findings, (
            f"body at exactly 2500 tokens (10000 chars) should not produce "
            f"a body/token finding\nfindings: {body_findings}"
        )


# --------------------------------------------------------------------------
# 6. Unknown gov command is red
# --------------------------------------------------------------------------

class TestUnknownGovCommand:

    def test_unknown_gov_command_finding(self, tmp_path):
        """A body referencing ``gov frobnicate`` (not in RESERVED_COMMANDS)
        produces a finding."""
        path = make_skill(
            tmp_path,
            name="bad-cmd",
            body="Run `gov frobnicate` to do the thing.\n",
        )
        result = run_skill_validator(str(path))
        assert result.returncode != 0, (
            f"skill referencing unknown gov command should fail "
            f"but got exit 0\nstdout: {result.stdout}"
        )
        output = parse_output(result)
        findings = output.get("findings", [])
        assert any("frobnicate" in json.dumps(f).lower() for f in findings), (
            f"expected a finding mentioning 'frobnicate'\nfindings: {findings}"
        )

    def test_multiple_unknown_commands(self, tmp_path):
        """Multiple unknown gov commands each produce a finding."""
        path = make_skill(
            tmp_path,
            name="multi-bad",
            body="Use `gov zzzfoo` and `gov zzzbar` together.\n",
        )
        result = run_skill_validator(str(path))
        assert result.returncode != 0, (
            f"skill referencing unknown gov commands should fail "
            f"but got exit 0\nstdout: {result.stdout}"
        )
        output = parse_output(result)
        findings = output.get("findings", [])
        mentioned = json.dumps(findings).lower()
        assert "zzzfoo" in mentioned and "zzzbar" in mentioned, (
            f"expected findings for both 'zzzfoo' and 'zzzbar'\nfindings: {findings}"
        )


# --------------------------------------------------------------------------
# 7. Known gov command passes
# --------------------------------------------------------------------------

class TestKnownGovCommand:

    @pytest.mark.parametrize("command", ["check", "status", "readiness", "rebuild"])
    def test_known_gov_command_no_finding(self, tmp_path, command):
        """A body referencing a known ``gov <command>`` does not produce a
        command-reference finding."""
        path = make_skill(
            tmp_path,
            name=f"ok-{command}",
            body=f"Use `gov {command}` to verify.\n",
        )
        result = run_skill_validator(str(path))
        output = parse_output(result)
        findings = output.get("findings", [])
        cmd_findings = [f for f in findings if command in json.dumps(f).lower()
                        and "command" in json.dumps(f).lower()]
        assert not cmd_findings, (
            f"`gov {command}` is a known command and should not produce a "
            f"command finding\nfindings: {cmd_findings}"
        )


# --------------------------------------------------------------------------
# 8. No arguments -> unmeasured, exit non-zero
# --------------------------------------------------------------------------

class TestNoArguments:

    def test_no_args_unmeasured(self):
        """Called with no file/folder arguments: exit non-zero with
        'unmeasured' in output (DEC-425)."""
        result = run_skill_validator()
        assert result.returncode != 0, (
            f"no arguments should exit non-zero but got exit 0\n"
            f"stdout: {result.stdout}"
        )
        output = parse_output(result)
        combined = (result.stdout + result.stderr).lower()
        assert "unmeasured" in combined or output.get("unmeasured") is True, (
            f"no arguments should report 'unmeasured'\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


# --------------------------------------------------------------------------
# 9. Empty folder -> unmeasured, exit non-zero
# --------------------------------------------------------------------------

class TestEmptyFolder:

    def test_empty_folder_unmeasured(self, tmp_path):
        """A folder with no .md files: exit non-zero, 'unmeasured'."""
        empty = tmp_path / "empty-skills"
        empty.mkdir()
        (empty / "notes.txt").write_text("not a skill\n", encoding="utf-8")
        result = run_skill_validator(str(empty))
        assert result.returncode != 0, (
            f"empty folder should exit non-zero but got exit 0\n"
            f"stdout: {result.stdout}"
        )
        output = parse_output(result)
        combined = (result.stdout + result.stderr).lower()
        assert "unmeasured" in combined or output.get("unmeasured") is True, (
            f"empty folder should report 'unmeasured'\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_folder_with_non_frontmatter_md(self, tmp_path):
        """A folder with .md files but none having YAML frontmatter:
        unmeasured."""
        folder = tmp_path / "no-front-skills"
        folder.mkdir()
        (folder / "README.md").write_text("# Just a readme\n", encoding="utf-8")
        result = run_skill_validator(str(folder))
        assert result.returncode != 0, (
            f"folder with non-skill .md should exit non-zero but got exit 0\n"
            f"stdout: {result.stdout}"
        )
        output = parse_output(result)
        combined = (result.stdout + result.stderr).lower()
        assert "unmeasured" in combined or output.get("unmeasured") is True, (
            f"folder with non-skill .md should report 'unmeasured'\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


# --------------------------------------------------------------------------
# 10. Unreadable file -> unmeasured, exit non-zero
# --------------------------------------------------------------------------

class TestUnreadableFile:

    def test_nonexistent_path_unmeasured(self, tmp_path):
        """A path that does not exist: exit non-zero, 'unmeasured'."""
        bad_path = tmp_path / "does-not-exist" / "SKILL.md"
        result = run_skill_validator(str(bad_path))
        assert result.returncode != 0, (
            f"nonexistent path should exit non-zero but got exit 0\n"
            f"stdout: {result.stdout}"
        )
        output = parse_output(result)
        combined = (result.stdout + result.stderr).lower()
        assert "unmeasured" in combined or output.get("unmeasured") is True, (
            f"nonexistent path should report 'unmeasured'\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_nonexistent_folder_unmeasured(self, tmp_path):
        """A folder path that does not exist: exit non-zero, 'unmeasured'."""
        bad_dir = tmp_path / "ghost-folder"
        result = run_skill_validator(str(bad_dir))
        assert result.returncode != 0, (
            f"nonexistent folder should exit non-zero but got exit 0\n"
            f"stdout: {result.stdout}"
        )
        output = parse_output(result)
        combined = (result.stdout + result.stderr).lower()
        assert "unmeasured" in combined or output.get("unmeasured") is True, (
            f"nonexistent folder should report 'unmeasured'\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


# ==========================================================================
# Fix 1: Folder search at every depth for SKILL.md files
# ==========================================================================

class TestDeepFolderSearch:

    def test_deep_folder_all_valid(self, tmp_path):
        """A skills folder with SKILL.md files at multiple depths: all valid
        -> exit 0."""
        make_skill(tmp_path, name="discovery")
        make_skill(tmp_path, name="planning")
        result = run_skill_validator(str(tmp_path))
        assert result.returncode == 0, (
            f"folder with valid skills at depth should pass (exit 0) "
            f"but got exit {result.returncode}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_deep_folder_one_broken(self, tmp_path):
        """A skills folder where one nested SKILL.md is broken -> exit 1
        with a finding for the broken one."""
        make_skill(tmp_path, name="good-skill")
        make_skill(tmp_path, name="broken-skill", raw="---\nname: broken-skill\n---\n\nNo version.\n")
        result = run_skill_validator(str(tmp_path))
        assert result.returncode != 0, (
            f"folder with one broken nested skill should fail "
            f"but got exit 0\nstdout: {result.stdout}"
        )
        output = parse_output(result)
        findings = output.get("findings", [])
        assert any("broken-skill" in json.dumps(f) for f in findings), (
            f"expected a finding for the broken skill\nfindings: {findings}"
        )


# ==========================================================================
# Fix 2: SKILL.md without valid frontmatter is a finding, not skipped
# ==========================================================================

class TestNoFrontmatterIsFinding:

    def test_skill_with_no_frontmatter_is_finding(self, tmp_path):
        """A SKILL.md file found by folder search that has no frontmatter is
        reported as a finding (SKILL_NO_FRONTMATTER), not silently skipped."""
        make_skill(tmp_path, name="good-skill")
        make_skill(tmp_path, name="bad-skill", raw="# No frontmatter at all\n\nJust text.\n")
        result = run_skill_validator(str(tmp_path))
        assert result.returncode != 0, (
            f"folder with a no-frontmatter SKILL.md should fail "
            f"but got exit 0\nstdout: {result.stdout}"
        )
        output = parse_output(result)
        findings = output.get("findings", [])
        assert any("bad-skill" in json.dumps(f) for f in findings), (
            f"expected a finding for the no-frontmatter skill\nfindings: {findings}"
        )


# ==========================================================================
# Fix 3: Command references with args after the command name are seen
# ==========================================================================

class TestCommandRefsWithArgs:

    def test_misspelt_command_with_args(self, tmp_path):
        """A body containing ``gov retreive --json`` (misspelt with args)
        produces a finding for the misspelt command."""
        path = make_skill(
            tmp_path,
            name="bad-cmd-args",
            body="Run `gov retreive --json` for output.\n",
        )
        result = run_skill_validator(str(path))
        assert result.returncode != 0, (
            f"misspelt gov command with args should fail "
            f"but got exit 0\nstdout: {result.stdout}"
        )
        output = parse_output(result)
        findings = output.get("findings", [])
        assert any("retreive" in json.dumps(f).lower() for f in findings), (
            f"expected a finding for 'retreive'\nfindings: {findings}"
        )

    def test_valid_command_with_args_passes(self, tmp_path):
        """A body containing ``gov check --list`` (valid command with args)
        does not produce a command finding."""
        path = make_skill(
            tmp_path,
            name="ok-cmd-args",
            body="Run `gov check --list` to see checks.\n",
        )
        result = run_skill_validator(str(path))
        output = parse_output(result)
        findings = output.get("findings", [])
        cmd_findings = [f for f in findings if "command" in json.dumps(f).lower()
                        and "check" in json.dumps(f).lower()]
        assert not cmd_findings, (
            f"valid 'gov check --list' should not produce a command finding\n"
            f"findings: {cmd_findings}"
        )

    def test_fenced_code_block_misspelt_command(self, tmp_path):
        """A fenced code block containing ``gov chek --list`` produces a
        finding for the misspelt command."""
        body = "Example:\n\n```bash\ngov chek --list\n```\n"
        path = make_skill(
            tmp_path,
            name="fenced-bad",
            body=body,
        )
        result = run_skill_validator(str(path))
        assert result.returncode != 0, (
            f"misspelt gov command in fenced block should fail "
            f"but got exit 0\nstdout: {result.stdout}"
        )
        output = parse_output(result)
        findings = output.get("findings", [])
        assert any("chek" in json.dumps(f).lower() for f in findings), (
            f"expected a finding for 'chek'\nfindings: {findings}"
        )

    def test_bare_gov_command_still_works(self, tmp_path):
        """The existing test for bare ``gov frobnicate`` still works."""
        path = make_skill(
            tmp_path,
            name="bare-bad",
            body="Run `gov frobnicate` to do the thing.\n",
        )
        result = run_skill_validator(str(path))
        assert result.returncode != 0, (
            f"bare misspelt gov command should fail "
            f"but got exit 0\nstdout: {result.stdout}"
        )
        output = parse_output(result)
        findings = output.get("findings", [])
        assert any("frobnicate" in json.dumps(f).lower() for f in findings), (
            f"expected a finding for 'frobnicate'\nfindings: {findings}"
        )


# ==========================================================================
# Fix 4: name/description/version that is not text is a finding
# ==========================================================================

class TestNonTextFields:

    def test_version_integer_is_finding(self, tmp_path):
        """``version: 1`` (integer, not string) is a finding."""
        path = make_skill(
            tmp_path,
            name="int-ver",
            raw="---\nname: int-ver\nversion: 1\ndescription: A skill\n---\n\nBody.\n",
        )
        result = run_skill_validator(str(path))
        assert result.returncode != 0, (
            f"integer version should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )

    def test_name_integer_is_finding(self, tmp_path):
        """``name: 42`` (integer) is a finding."""
        path = make_skill(
            tmp_path,
            name="int-name",
            raw="---\nname: 42\nversion: 1.0.0\ndescription: A skill\n---\n\nBody.\n",
        )
        result = run_skill_validator(str(path))
        assert result.returncode != 0, (
            f"integer name should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )

    def test_description_list_is_finding(self, tmp_path):
        """``description: [a, b]`` (list) is a finding."""
        path = make_skill(
            tmp_path,
            name="list-desc",
            raw="---\nname: list-desc\nversion: 1.0.0\ndescription: [a, b]\n---\n\nBody.\n",
        )
        result = run_skill_validator(str(path))
        assert result.returncode != 0, (
            f"list description should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )

    def test_name_empty_string_is_finding(self, tmp_path):
        """``name: ""`` (empty string) is a finding."""
        path = make_skill(
            tmp_path,
            name="empty-name",
            raw='---\nname: ""\nversion: 1.0.0\ndescription: A skill\n---\n\nBody.\n',
        )
        result = run_skill_validator(str(path))
        assert result.returncode != 0, (
            f"empty name should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )

    def test_description_empty_string_is_finding(self, tmp_path):
        """``description: ""`` (empty string) is a finding."""
        path = make_skill(
            tmp_path,
            name="empty-desc",
            raw='---\nname: empty-desc\nversion: 1.0.0\ndescription: ""\n---\n\nBody.\n',
        )
        result = run_skill_validator(str(path))
        assert result.returncode != 0, (
            f"empty description should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )


# ==========================================================================
# Fix 5: Token count uses the same formula as gov context
# ==========================================================================

class TestTokenCountFormula:

    def test_body_10001_chars_is_2501_tokens(self, tmp_path):
        """A body of exactly 10001 chars is ceil(10001/4) = 2501 tokens,
        which exceeds the 2500 limit and is a finding. This verifies the
        validator uses the same ceil(len/TOKEN_CHARS) arithmetic as
        ``gov context``."""
        body = "Z" * 10001
        expected_tokens = math.ceil(10001 / 4)
        assert expected_tokens == 2501
        path = make_skill(tmp_path, name="token-math", body=body)
        result = run_skill_validator(str(path))
        assert result.returncode != 0, (
            f"body of 10001 chars ({expected_tokens} tokens) should fail "
            f"but got exit 0\nstdout: {result.stdout[:200]}"
        )
        output = parse_output(result)
        findings = output.get("findings", [])
        assert any("body" in json.dumps(f).lower() or "token" in json.dumps(f).lower()
                    for f in findings), (
            f"expected a finding about body/tokens\nfindings: {findings}"
        )


# ==========================================================================
# Fix 6: Unreadable file is "unmeasured", not a traceback;
#         valid folder plus missing path -> not green
# ==========================================================================

class TestUnmeasuredEdgeCases:

    def test_valid_folder_plus_missing_path(self, tmp_path):
        """A valid skill folder plus a nonexistent path as two arguments
        -> exit non-zero."""
        make_skill(tmp_path / "skills", name="good-skill")
        bad_path = str(tmp_path / "nonexistent" / "SKILL.md")
        result = run_skill_validator(str(tmp_path / "skills"), bad_path)
        assert result.returncode != 0, (
            f"valid folder + nonexistent path should exit non-zero "
            f"but got exit 0\nstdout: {result.stdout}"
        )

    def test_binary_file_unmeasured(self, tmp_path):
        """A file that cannot be decoded (binary content) is unmeasured,
        not a traceback."""
        path = tmp_path / "binary-skill" / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"\x80\x81\x82\x00\xff\xfe" * 100)
        result = run_skill_validator(str(path))
        assert result.returncode != 0, (
            f"binary file should exit non-zero but got exit 0\n"
            f"stdout: {result.stdout}"
        )
        assert "Traceback" not in result.stderr, (
            f"binary file should not produce a traceback\n"
            f"stderr: {result.stderr}"
        )
