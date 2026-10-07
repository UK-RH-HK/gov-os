"""Audit-report validator (DEC-439, DEC-441).

Tests the standalone ``python3 -m gov.check.audit_validator`` command that
validates audit report files for frontmatter correctness, table structure,
valid classes, resolvable commits, and evidence paths.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_26_support as support  # noqa: E402

REPO_ROOT = support.REPO_ROOT
SRC = support.SRC
TIMEOUT_S = 30.0

VALID_CLASSES = ("OK", "MISSING", "WEAKENED", "CONTRADICTS", "UNJUSTIFIED_DROP", "SCOPE_CREEP")


# --------------------------------------------------------------------------
# Runner helper
# --------------------------------------------------------------------------

def run_audit_validator(*args: str, cwd: str | Path | None = None) -> subprocess.CompletedProcess:
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": os.environ.get("HOME", "/tmp"),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(SRC),
    }
    cmd = [sys.executable, "-m", "gov.check.audit_validator", *args]
    return subprocess.run(
        cmd,
        cwd=str(cwd or REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=TIMEOUT_S,
        stdin=subprocess.DEVNULL,
        env=env,
    )


# --------------------------------------------------------------------------
# Git repo builder
# --------------------------------------------------------------------------

def make_git_repo(tmp_path, extra_files=None):
    """Create a minimal git repo and return (repo_path, commit_hash).

    ``extra_files`` is an optional dict of {relative_path: content} to add
    before the initial commit.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(tmp_path),
        "LC_ALL": "C.UTF-8",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
    }

    def git(*args):
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, text=True, env=env, check=True,
        )

    git("init", "-q", "-b", "main")
    git("config", "user.email", "test@test")
    git("config", "user.name", "Test")
    (repo / "README.md").write_text("# Test\n")
    if extra_files:
        for rel, content in extra_files.items():
            p = repo / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
    git("add", ".")
    git("commit", "-q", "-m", "init")
    commit = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True, text=True, env=env,
    ).stdout.strip()
    return repo, commit


def make_report(
    *,
    milestone="W1",
    commit="abc123",
    pack_sha256="deadbeef" * 8,
    rows=None,
    include_milestone=True,
    include_commit=True,
    include_pack_sha256=True,
    raw=None,
):
    """Build the text of an audit report."""
    if raw is not None:
        return raw
    front_lines = ["---"]
    if include_milestone:
        front_lines.append(f"milestone: {milestone}")
    if include_commit:
        front_lines.append(f"commit: {commit}")
    if include_pack_sha256:
        front_lines.append(f"pack_sha256: {pack_sha256}")
    front_lines.append("---")
    front_lines.append("")
    front_lines.append("# Audit Report")
    front_lines.append("")
    front_lines.append("| item | class | evidence |")
    front_lines.append("|---|---|---|")
    if rows:
        for item, cls, evidence in rows:
            front_lines.append(f"| {item} | {cls} | {evidence} |")
    front_lines.append("")
    return "\n".join(front_lines)


def write_report(repo, name, text):
    """Write a report file in the repo (not committed)."""
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# 1. Valid report passes (exit 0)
# --------------------------------------------------------------------------

class TestValidReport:

    def test_valid_report_passes(self, tmp_path):
        """A well-formed report with a resolvable commit, valid rows with
        existing paths at the commit, passes."""
        repo, commit = make_git_repo(tmp_path, extra_files={
            "src/main.py": "print('hello')\n",
        })
        text = make_report(
            commit=commit,
            rows=[
                ("CAP-24", "OK", "src/main.py"),
                ("DEC-070", "MISSING", "-"),
            ],
        )
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode == 0, (
            f"valid report should pass (exit 0) but got exit {result.returncode}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


# --------------------------------------------------------------------------
# 2. Missing frontmatter is red
# --------------------------------------------------------------------------

class TestMissingFrontmatter:

    def test_no_frontmatter(self, tmp_path):
        """A .md file with no frontmatter is red."""
        repo, commit = make_git_repo(tmp_path)
        report = write_report(repo, "audit.md", "# No frontmatter\n\nJust text.\n")
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode != 0, (
            f"report without frontmatter should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )


# --------------------------------------------------------------------------
# 3. Missing `commit` field is red
# --------------------------------------------------------------------------

class TestMissingCommit:

    def test_missing_commit_field(self, tmp_path):
        """Frontmatter without a ``commit`` field is red."""
        repo, commit = make_git_repo(tmp_path)
        text = make_report(
            include_commit=False,
            rows=[("CAP-24", "OK", "README.md")],
        )
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode != 0, (
            f"report without commit should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )


# --------------------------------------------------------------------------
# 4. Missing `milestone` field is red
# --------------------------------------------------------------------------

class TestMissingMilestone:

    def test_missing_milestone_field(self, tmp_path):
        """Frontmatter without a ``milestone`` field is red."""
        repo, commit = make_git_repo(tmp_path)
        text = make_report(
            commit=commit,
            include_milestone=False,
            rows=[("CAP-24", "OK", "README.md")],
        )
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode != 0, (
            f"report without milestone should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )


# --------------------------------------------------------------------------
# 5. Missing `pack_sha256` field is red
# --------------------------------------------------------------------------

class TestMissingPackSha256:

    def test_missing_pack_sha256_field(self, tmp_path):
        """Frontmatter without a ``pack_sha256`` field is red."""
        repo, commit = make_git_repo(tmp_path)
        text = make_report(
            commit=commit,
            include_pack_sha256=False,
            rows=[("CAP-24", "OK", "README.md")],
        )
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode != 0, (
            f"report without pack_sha256 should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )


# --------------------------------------------------------------------------
# 6. Unresolvable commit is red
# --------------------------------------------------------------------------

class TestUnresolvableCommit:

    def test_unresolvable_commit(self, tmp_path):
        """A commit hash that does not exist in the repository is red."""
        repo, _ = make_git_repo(tmp_path)
        text = make_report(
            commit="deadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
            rows=[("CAP-24", "OK", "README.md")],
        )
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode != 0, (
            f"unresolvable commit should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )


# --------------------------------------------------------------------------
# 7. No table rows is red
# --------------------------------------------------------------------------

class TestNoTableRows:

    def test_no_table_rows(self, tmp_path):
        """Frontmatter valid but no table body rows is red."""
        repo, commit = make_git_repo(tmp_path)
        text = make_report(commit=commit, rows=[])
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode != 0, (
            f"report with no table rows should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )


# --------------------------------------------------------------------------
# 8. Invalid class is red
# --------------------------------------------------------------------------

class TestInvalidClass:

    def test_invalid_class(self, tmp_path):
        """A row with a class not in the six valid ones is red."""
        repo, commit = make_git_repo(tmp_path)
        text = make_report(
            commit=commit,
            rows=[("CAP-24", "BOGUS", "README.md")],
        )
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode != 0, (
            f"invalid class should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )


# --------------------------------------------------------------------------
# 9. OK row with no evidence path is red
# --------------------------------------------------------------------------

class TestOKRowNoEvidence:

    def test_ok_row_with_dash_evidence(self, tmp_path):
        """An OK row citing ``-`` as evidence is red."""
        repo, commit = make_git_repo(tmp_path)
        text = make_report(
            commit=commit,
            rows=[("CAP-24", "OK", "-")],
        )
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode != 0, (
            f"OK row with '-' evidence should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )


# --------------------------------------------------------------------------
# 10. Non-OK row with `-` passes
# --------------------------------------------------------------------------

class TestNonOKRowDashEvidence:

    @pytest.mark.parametrize("cls", ["MISSING", "WEAKENED", "CONTRADICTS",
                                      "UNJUSTIFIED_DROP", "SCOPE_CREEP"])
    def test_non_ok_row_with_dash_passes(self, tmp_path, cls):
        """A non-OK row with ``-`` as evidence is allowed."""
        repo, commit = make_git_repo(tmp_path)
        text = make_report(
            commit=commit,
            rows=[
                ("CAP-24", "OK", "README.md"),
                ("DEC-070", cls, "-"),
            ],
        )
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode == 0, (
            f"non-OK row ({cls}) with '-' evidence should pass but got exit {result.returncode}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


# --------------------------------------------------------------------------
# 11. Evidence path that does not exist at the commit is red
# --------------------------------------------------------------------------

class TestEvidencePathMissing:

    def test_evidence_path_not_at_commit(self, tmp_path):
        """An evidence path that does not exist at the cited commit is red."""
        repo, commit = make_git_repo(tmp_path)
        text = make_report(
            commit=commit,
            rows=[("CAP-24", "OK", "does/not/exist.py")],
        )
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode != 0, (
            f"evidence path not at commit should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )


# --------------------------------------------------------------------------
# 12. Evidence path that exists at the commit passes
# --------------------------------------------------------------------------

class TestEvidencePathExists:

    def test_evidence_path_at_commit(self, tmp_path):
        """An evidence path that exists at the cited commit passes."""
        repo, commit = make_git_repo(tmp_path, extra_files={
            "src/main.py": "print('hello')\n",
            "docs/arch.md": "# Architecture\n",
        })
        text = make_report(
            commit=commit,
            rows=[
                ("CAP-24", "OK", "src/main.py"),
                ("CAP-38", "OK", "docs/arch.md"),
            ],
        )
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode == 0, (
            f"evidence paths at commit should pass but got exit {result.returncode}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_multiple_evidence_paths_comma_separated(self, tmp_path):
        """Multiple comma-separated evidence paths that all exist pass."""
        repo, commit = make_git_repo(tmp_path, extra_files={
            "src/main.py": "print('hello')\n",
            "docs/arch.md": "# Architecture\n",
        })
        text = make_report(
            commit=commit,
            rows=[("CAP-24", "OK", "src/main.py, docs/arch.md")],
        )
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode == 0, (
            f"comma-separated evidence paths should pass but got exit {result.returncode}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


# --------------------------------------------------------------------------
# 13. Multiple rows, one bad, is red
# --------------------------------------------------------------------------

class TestMultipleRowsOneBad:

    def test_one_bad_row_among_good(self, tmp_path):
        """Multiple rows where one has a non-existent evidence path is red."""
        repo, commit = make_git_repo(tmp_path, extra_files={
            "src/main.py": "print('hello')\n",
        })
        text = make_report(
            commit=commit,
            rows=[
                ("CAP-24", "OK", "src/main.py"),
                ("CAP-38", "OK", "does/not/exist.py"),
            ],
        )
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode != 0, (
            f"one bad row should fail the whole report but got exit 0\n"
            f"stdout: {result.stdout}"
        )


# --------------------------------------------------------------------------
# 14. No arguments -> unmeasured, exit non-zero
# --------------------------------------------------------------------------

class TestNoArguments:

    def test_no_args_unmeasured(self, tmp_path):
        """Called with no file/folder arguments: exit non-zero (DEC-425)."""
        repo, _ = make_git_repo(tmp_path)
        result = run_audit_validator(cwd=repo)
        assert result.returncode != 0, (
            f"no arguments should exit non-zero but got exit 0\n"
            f"stdout: {result.stdout}"
        )
        combined = (result.stdout + result.stderr).lower()
        assert "unmeasured" in combined, (
            f"no arguments should report 'unmeasured'\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


# --------------------------------------------------------------------------
# 15. Empty folder -> not applicable, exit non-zero (revised DEC-447)
# --------------------------------------------------------------------------

class TestEmptyFolder:

    def test_empty_folder_not_applicable(self, tmp_path):
        """A folder with no report files: exit non-zero, "not applicable
        until the first audit" (owner decision DEC-447).

        Previously asserted 'unmeasured'; revised because DEC-447 requires
        the validator to say "not applicable" when a folder holds no report
        at all."""
        repo, _ = make_git_repo(tmp_path)
        empty = repo / "reports"
        empty.mkdir()
        (empty / "notes.txt").write_text("not a report\n", encoding="utf-8")
        result = run_audit_validator(str(empty), cwd=repo)
        assert result.returncode != 0, (
            f"folder with no reports should exit non-zero but got exit 0\n"
            f"stdout: {result.stdout}"
        )
        parsed = json.loads(result.stdout)
        assert parsed.get("not_applicable") is True, (
            f"expected not_applicable=true (owner decision DEC-447)\n"
            f"stdout: {result.stdout}"
        )
        assert "not applicable until the first audit" in parsed.get("reason", ""), (
            f"expected reason 'not applicable until the first audit' (DEC-447)\n"
            f"got: {parsed.get('reason')}"
        )


# --------------------------------------------------------------------------
# 16. Unreadable file -> unmeasured, exit non-zero
# --------------------------------------------------------------------------

class TestUnreadableFile:

    def test_nonexistent_path_unmeasured(self, tmp_path):
        """A path that does not exist: exit non-zero, 'unmeasured'."""
        repo, _ = make_git_repo(tmp_path)
        bad_path = repo / "does-not-exist" / "report.md"
        result = run_audit_validator(str(bad_path), cwd=repo)
        assert result.returncode != 0, (
            f"nonexistent path should exit non-zero but got exit 0\n"
            f"stdout: {result.stdout}"
        )
        combined = (result.stdout + result.stderr).lower()
        assert "unmeasured" in combined, (
            f"nonexistent path should report 'unmeasured'\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


# --------------------------------------------------------------------------
# 17. Outside a git repository -> unmeasured, exit non-zero
# --------------------------------------------------------------------------

class TestOutsideGitRepo:

    def test_outside_git_repo_unmeasured(self, tmp_path):
        """Running the validator outside a git repository is unmeasured."""
        no_git = tmp_path / "no-git"
        no_git.mkdir()
        text = make_report(
            commit="abc123",
            rows=[("CAP-24", "OK", "README.md")],
        )
        report_path = no_git / "audit.md"
        report_path.write_text(text, encoding="utf-8")
        result = run_audit_validator(str(report_path), cwd=no_git)
        assert result.returncode != 0, (
            f"outside git repo should exit non-zero but got exit 0\n"
            f"stdout: {result.stdout}"
        )
        combined = (result.stdout + result.stderr).lower()
        assert "unmeasured" in combined, (
            f"outside git repo should report 'unmeasured'\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


# --------------------------------------------------------------------------
# 18. Folder search finds .md files with frontmatter containing milestone and commit
# --------------------------------------------------------------------------

class TestFolderSearch:

    def test_folder_with_report_files(self, tmp_path):
        """A folder with .md files having frontmatter with milestone and
        commit is searched and validated."""
        repo, commit = make_git_repo(tmp_path, extra_files={
            "src/main.py": "print('hello')\n",
        })
        reports_dir = repo / "reports"
        reports_dir.mkdir()
        text = make_report(
            commit=commit,
            rows=[("CAP-24", "OK", "src/main.py")],
        )
        (reports_dir / "audit-w1.md").write_text(text, encoding="utf-8")
        result = run_audit_validator(str(reports_dir), cwd=repo)
        assert result.returncode == 0, (
            f"folder with valid report should pass but got exit {result.returncode}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


# --------------------------------------------------------------------------
# 19. A valid folder plus a missing path -> not green
# --------------------------------------------------------------------------

class TestMixedArguments:

    def test_valid_folder_plus_missing_path(self, tmp_path):
        """One good argument and one bad argument: not green."""
        repo, commit = make_git_repo(tmp_path, extra_files={
            "src/main.py": "print('hello')\n",
        })
        reports_dir = repo / "reports"
        reports_dir.mkdir()
        text = make_report(
            commit=commit,
            rows=[("CAP-24", "OK", "src/main.py")],
        )
        (reports_dir / "audit-w1.md").write_text(text, encoding="utf-8")
        bad_path = str(repo / "nonexistent-report.md")
        result = run_audit_validator(str(reports_dir), bad_path, cwd=repo)
        assert result.returncode != 0, (
            f"valid folder + missing path should not be green but got exit 0\n"
            f"stdout: {result.stdout}"
        )


# --------------------------------------------------------------------------
# 20. A malformed row (wrong number of columns) is red
# --------------------------------------------------------------------------

class TestMalformedRow:

    def test_row_with_two_columns(self, tmp_path):
        """A row with only two columns (missing evidence) is red."""
        repo, commit = make_git_repo(tmp_path)
        text = textwrap.dedent(f"""\
            ---
            milestone: W1
            commit: {commit}
            pack_sha256: {"ab" * 32}
            ---

            # Audit Report

            | item | class | evidence |
            |---|---|---|
            | CAP-24 | OK |
        """)
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode != 0, (
            f"malformed row (two columns) should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )

    def test_row_with_four_columns(self, tmp_path):
        """A row with four columns (extra column) is red."""
        repo, commit = make_git_repo(tmp_path)
        text = textwrap.dedent(f"""\
            ---
            milestone: W1
            commit: {commit}
            pack_sha256: {"ab" * 32}
            ---

            # Audit Report

            | item | class | evidence |
            |---|---|---|
            | CAP-24 | OK | README.md | extra |
        """)
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode != 0, (
            f"malformed row (four columns) should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )


# --------------------------------------------------------------------------
# 21. OK row with empty evidence cell is red (DEC-441)
# --------------------------------------------------------------------------

class TestOKRowEmptyEvidence:

    def test_ok_row_empty_evidence_cell(self, tmp_path):
        """An OK row whose evidence cell is empty (nothing or only spaces
        between the bars) is red.

        DEC-441: "A row of class OK cites at least one path."
        The empty string is not a path."""
        repo, commit = make_git_repo(tmp_path)
        text = make_report(
            commit=commit,
            rows=[("CAP-24", "OK", "")],
        )
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode != 0, (
            f"OK row with empty evidence should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )

    def test_ok_row_evidence_empty_entry_among_real(self, tmp_path):
        """An evidence cell with an empty entry among real ones is not
        well-formed: ``src/main.py, , README.md`` has a blank between
        two commas."""
        repo, commit = make_git_repo(tmp_path, extra_files={
            "src/main.py": "print('hello')\n",
        })
        text = make_report(
            commit=commit,
            rows=[("CAP-24", "OK", "src/main.py, , README.md")],
        )
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode != 0, (
            f"evidence cell with empty entry among real ones should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )

    def test_ok_row_evidence_trailing_comma(self, tmp_path):
        """A trailing comma in the evidence cell creates an empty entry,
        which is not well-formed."""
        repo, commit = make_git_repo(tmp_path, extra_files={
            "src/main.py": "print('hello')\n",
        })
        text = make_report(
            commit=commit,
            rows=[("CAP-24", "OK", "src/main.py,")],
        )
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode != 0, (
            f"evidence cell with trailing comma should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )

    def test_non_ok_row_empty_evidence_cell(self, tmp_path):
        """A non-OK row with an empty evidence cell is not well-formed.

        DEC-441 writes 'none' as ``-``, so an empty cell is not the same
        as ``-`` and is not well-formed for any class."""
        repo, commit = make_git_repo(tmp_path)
        text = make_report(
            commit=commit,
            rows=[
                ("CAP-24", "OK", "README.md"),
                ("DEC-070", "MISSING", ""),
            ],
        )
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode != 0, (
            f"non-OK row with empty evidence should fail (should be '-') but got exit 0\n"
            f"stdout: {result.stdout}"
        )


# --------------------------------------------------------------------------
# 22. Folder: broken/incomplete frontmatter is not silently skipped
# --------------------------------------------------------------------------

class TestFolderBrokenFrontmatterNotSkipped:

    def test_folder_broken_yaml_frontmatter_not_skipped(self, tmp_path):
        """A Markdown file in a folder whose frontmatter delimiters are present
        but whose YAML is broken must not be silently skipped.  It is a finding
        or unmeasured by name.

        A file with no frontmatter at all (no ``---`` delimiters), such as a
        README, may be ignored."""
        repo, commit = make_git_repo(tmp_path, extra_files={
            "src/main.py": "print('hello')\n",
        })
        reports_dir = repo / "reports"
        reports_dir.mkdir()
        valid_text = make_report(
            commit=commit,
            rows=[("CAP-24", "OK", "src/main.py")],
        )
        (reports_dir / "audit-valid.md").write_text(valid_text, encoding="utf-8")
        broken_text = textwrap.dedent("""\
            ---
            milestone: W1
            commit: [broken yaml
            ---

            # Audit Report

            | item | class | evidence |
            |---|---|---|
            | CAP-24 | OK | src/main.py |
        """)
        (reports_dir / "audit-broken.md").write_text(broken_text, encoding="utf-8")
        result = run_audit_validator(str(reports_dir), cwd=repo)
        assert result.returncode != 0, (
            f"folder with broken-frontmatter report should not be green but got exit 0\n"
            f"stdout: {result.stdout}"
        )

    def test_folder_missing_commit_in_frontmatter_not_skipped(self, tmp_path):
        """A Markdown file with valid frontmatter that lacks ``commit`` must not
        be silently skipped when validating a folder.  DEC-441 requires
        ``commit``; its absence is a finding.

        A file with no frontmatter at all may be ignored."""
        repo, commit = make_git_repo(tmp_path, extra_files={
            "src/main.py": "print('hello')\n",
        })
        reports_dir = repo / "reports"
        reports_dir.mkdir()
        valid_text = make_report(
            commit=commit,
            rows=[("CAP-24", "OK", "src/main.py")],
        )
        (reports_dir / "audit-valid.md").write_text(valid_text, encoding="utf-8")
        no_commit_text = make_report(
            include_commit=False,
            rows=[("CAP-24", "OK", "src/main.py")],
        )
        (reports_dir / "audit-no-commit.md").write_text(no_commit_text, encoding="utf-8")
        result = run_audit_validator(str(reports_dir), cwd=repo)
        assert result.returncode != 0, (
            f"folder with report missing commit should not be green but got exit 0\n"
            f"stdout: {result.stdout}"
        )


# --------------------------------------------------------------------------
# 23. commit must be a hexadecimal commit id (DEC-441)
# --------------------------------------------------------------------------

class TestCommitMustBeHexId:

    def test_commit_is_head(self, tmp_path):
        """``commit: HEAD`` resolves to the current commit but names a moving
        reference, not a hexadecimal commit id.  DEC-441 says 'the audited
        commit', meaning a fixed hex id."""
        repo, _ = make_git_repo(tmp_path)
        text = make_report(
            commit="HEAD",
            rows=[("CAP-24", "OK", "README.md")],
        )
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode != 0, (
            f"commit=HEAD should fail (not a hex commit id) but got exit 0\n"
            f"stdout: {result.stdout}"
        )

    def test_commit_is_branch_name(self, tmp_path):
        """``commit: main`` resolves to a commit but is a branch name, not a
        hexadecimal commit id.  DEC-441 requires a fixed hex id."""
        repo, _ = make_git_repo(tmp_path)
        text = make_report(
            commit="main",
            rows=[("CAP-24", "OK", "README.md")],
        )
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode != 0, (
            f"commit=main should fail (not a hex commit id) but got exit 0\n"
            f"stdout: {result.stdout}"
        )


# --------------------------------------------------------------------------
# 24. pack_sha256 must be a valid SHA-256 hex string (DEC-441)
# --------------------------------------------------------------------------

class TestPackSha256Format:

    def test_pack_sha256_too_short(self, tmp_path):
        """A ``pack_sha256`` value shorter than 64 hex characters is a finding.

        DEC-441: the pack hash is a SHA-256, which is 64 hexadecimal
        characters (with or without a ``sha256:`` prefix)."""
        repo, commit = make_git_repo(tmp_path)
        text = make_report(
            commit=commit,
            pack_sha256="deadbeef",
            rows=[("CAP-24", "OK", "README.md")],
        )
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode != 0, (
            f"short pack_sha256 should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )

    def test_pack_sha256_non_hex(self, tmp_path):
        """A ``pack_sha256`` value with non-hexadecimal characters is a
        finding."""
        repo, commit = make_git_repo(tmp_path)
        text = make_report(
            commit=commit,
            pack_sha256="not-a-sha256-value-at-all!!!",
            rows=[("CAP-24", "OK", "README.md")],
        )
        report = write_report(repo, "audit.md", text)
        result = run_audit_validator(str(report), cwd=repo)
        assert result.returncode != 0, (
            f"non-hex pack_sha256 should fail but got exit 0\n"
            f"stdout: {result.stdout}"
        )
