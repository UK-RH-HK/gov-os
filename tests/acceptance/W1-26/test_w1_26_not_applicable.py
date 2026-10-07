"""DEC-447: the audit check is "not applicable until the first audit".

While a project has no audit report, the audit-reproducibility check reports
"not applicable until the first audit" as a warning (YELLOW), not RED.  Once
an audit report exists, the check is a hard block.  No other check gains this
answer, and the answer is never GREEN.

Validator exit codes: 0 clean, 1 findings or unmeasured, 2 not applicable.
Declaration field: ``allows-not-applicable: "true"`` (optional; absent = no
change to existing behaviour).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_26_support as support  # noqa: E402

REPO_ROOT = support.REPO_ROOT
SRC = support.SRC
CHECKS_REL = support.CHECKS_REL
TIMEOUT_S = 30.0

EXIT_NOT_APPLICABLE = 2
NOT_APPLICABLE_REASON = "not applicable until the first audit"
NA_FIELD = "allows-not-applicable"
NA_VALUE = "true"


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _run_validator(*args: str, cwd: str | Path | None = None) -> subprocess.CompletedProcess:
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": os.environ.get("HOME", "/tmp"),
        "LC_ALL": "C.UTF-8",
        "PYTHONPATH": str(SRC),
    }
    return subprocess.run(
        [sys.executable, "-m", "gov.check.audit_validator", *args],
        cwd=str(cwd or REPO_ROOT),
        capture_output=True, text=True, timeout=TIMEOUT_S,
        stdin=subprocess.DEVNULL, env=env,
    )


def _git_repo(tmp_path, extra_files=None):
    repo = tmp_path / "repo"
    repo.mkdir()
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(tmp_path), "LC_ALL": "C.UTF-8",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
    }
    def git(*a):
        subprocess.run(["git", "-C", str(repo), *a],
                       capture_output=True, text=True, env=env, check=True)
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


def _report(*, commit="abc123", pack_sha256="deadbeef" * 8, rows=None):
    lines = [
        "---", f"milestone: W1", f"commit: {commit}",
        f"pack_sha256: {pack_sha256}", "---", "",
        "# Audit Report", "",
        "| item | class | evidence |", "|---|---|---|",
    ]
    for item, cls, evidence in (rows or []):
        lines.append(f"| {item} | {cls} | {evidence} |")
    lines.append("")
    return "\n".join(lines)


def _write_na_declaration(project, check_id, family, command,
                          severity="hard-block", allows_na=True):
    lines = [
        f'id: "{check_id}"', f'family: "{family}"',
        f'tier: "G2"', f'severity: "{severity}"',
        f'command: "{command}"',
    ]
    if allows_na:
        lines.append(f'{NA_FIELD}: "{NA_VALUE}"')
    support.write(project.root, f"{CHECKS_REL}/{check_id}.yaml",
                  "\n".join(lines) + "\n")


def _script(tmp_path, name, body):
    s = tmp_path / name
    s.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
    s.chmod(0o755)
    return str(s)


def _na_cmd(tmp_path, name="na.sh"):
    return _script(tmp_path, name,
        f"printf '{{\"not_applicable\": true, \"reason\": \"{NOT_APPLICABLE_REASON}\"}}\\n'\n"
        f"exit {EXIT_NOT_APPLICABLE}")


def _na_exit0_cmd(tmp_path, name="na0.sh"):
    return _script(tmp_path, name,
        f"printf '{{\"not_applicable\": true, \"reason\": \"{NOT_APPLICABLE_REASON}\"}}\\n'\n"
        "exit 0")


def _findings_cmd(tmp_path, name="findings.sh"):
    return _script(tmp_path, name,
        "printf '{\"findings\": [{\"code\": \"TEST\", \"message\": \"planted\"}]}\\n'\n"
        "exit 1")


def _unmeasured_cmd(tmp_path, name="unmeasured.sh"):
    return _script(tmp_path, name,
        "printf '{\"unmeasured\": true, \"reason\": \"nothing\"}\\n'\nexit 1")


# ==========================================================================
# GROUP 1 — The validator
# ==========================================================================

class TestValidatorNotApplicable:
    """Folder with no reports → ``not_applicable`` JSON, exit 2."""

    def test_folder_exists_no_reports_says_not_applicable(self, tmp_path):
        """A folder that exists but holds no Markdown file with frontmatter
        says ``not_applicable`` with the reason text."""
        repo, _ = _git_repo(tmp_path)
        folder = repo / "audit-reports"
        folder.mkdir()
        (folder / "notes.txt").write_text("not a report\n")
        r = _run_validator(str(folder), cwd=repo)
        assert r.returncode != 0
        parsed = json.loads(r.stdout)
        assert parsed.get("not_applicable") is True, (
            f"expected not_applicable=true\nstdout: {r.stdout}")
        assert NOT_APPLICABLE_REASON in parsed.get("reason", ""), (
            f"expected reason '{NOT_APPLICABLE_REASON}'\ngot: {parsed.get('reason')}")

    def test_folder_does_not_exist_says_not_applicable(self, tmp_path):
        """A folder argument that does not exist: not applicable, not
        unmeasured.  A missing reports folder means no audit yet."""
        repo, _ = _git_repo(tmp_path)
        missing = repo / "audit-reports"
        assert not missing.exists()
        r = _run_validator(str(missing), cwd=repo)
        assert r.returncode != 0
        parsed = json.loads(r.stdout)
        assert parsed.get("not_applicable") is True, (
            f"expected not_applicable=true\nstdout: {r.stdout}")
        assert NOT_APPLICABLE_REASON in parsed.get("reason", ""), (
            f"expected reason '{NOT_APPLICABLE_REASON}'\ngot: {parsed.get('reason')}")

    def test_not_applicable_exit_code_is_2(self, tmp_path):
        """The exit code for not-applicable is 2 (not 0 and not 1)."""
        repo, _ = _git_repo(tmp_path)
        (repo / "audit-reports").mkdir()
        r = _run_validator(str(repo / "audit-reports"), cwd=repo)
        assert r.returncode == EXIT_NOT_APPLICABLE, (
            f"expected exit {EXIT_NOT_APPLICABLE}, got {r.returncode}\n"
            f"stdout: {r.stdout}")

    def test_not_applicable_exit_code_distinct_from_findings_and_unmeasured(
            self, tmp_path):
        """Exit 2 differs from the exit code for findings and for unmeasured
        (both currently 1)."""
        repo, commit = _git_repo(tmp_path)
        (repo / "audit-reports").mkdir()
        na = _run_validator(str(repo / "audit-reports"), cwd=repo)
        report = repo / "bad.md"
        report.write_text(_report(commit=commit, rows=[]))
        findings = _run_validator(str(report), cwd=repo)
        unmeasured = _run_validator(cwd=repo)
        assert na.returncode != findings.returncode, (
            f"na ({na.returncode}) must differ from findings ({findings.returncode})")
        assert na.returncode != unmeasured.returncode, (
            f"na ({na.returncode}) must differ from unmeasured ({unmeasured.returncode})")


class TestValidatorUnmeasuredUnchanged:
    """Cases that stay unmeasured, never not-applicable."""

    def test_no_args_is_unmeasured(self, tmp_path):
        repo, _ = _git_repo(tmp_path)
        r = _run_validator(cwd=repo)
        assert r.returncode != 0
        out = r.stdout.lower()
        assert "unmeasured" in out, f"expected unmeasured\nstdout: {r.stdout}"
        assert "not_applicable" not in out and "not applicable" not in out

    def test_file_does_not_exist_is_unmeasured(self, tmp_path):
        repo, _ = _git_repo(tmp_path)
        r = _run_validator(str(repo / "missing" / "report.md"), cwd=repo)
        assert r.returncode != 0
        assert "unmeasured" in r.stdout.lower()

    def test_outside_git_repo_is_unmeasured(self, tmp_path):
        no_git = tmp_path / "no-git"
        no_git.mkdir()
        (no_git / "reports").mkdir()
        r = _run_validator(str(no_git / "reports"), cwd=no_git)
        assert r.returncode != 0
        assert "unmeasured" in r.stdout.lower()


class TestValidatorFolderWithReports:
    """A folder with at least one report is validated, never not-applicable."""

    def test_folder_valid_report(self, tmp_path):
        repo, commit = _git_repo(tmp_path, {"src/m.py": "x\n"})
        d = repo / "reports"
        d.mkdir()
        (d / "r.md").write_text(_report(commit=commit,
                                        rows=[("CAP-24", "OK", "src/m.py")]))
        r = _run_validator(str(d), cwd=repo)
        assert r.returncode == 0, f"valid report should pass\nstdout: {r.stdout}"
        assert "not_applicable" not in r.stdout.lower()

    def test_folder_broken_report(self, tmp_path):
        repo, commit = _git_repo(tmp_path)
        d = repo / "reports"
        d.mkdir()
        (d / "r.md").write_text(_report(commit=commit, rows=[]))
        r = _run_validator(str(d), cwd=repo)
        assert r.returncode != 0
        parsed = json.loads(r.stdout)
        assert parsed.get("not_applicable") is not True, (
            "broken report must not be not-applicable")


# ==========================================================================
# GROUP 2 — The runner
# ==========================================================================

class TestRunnerOptedIn:
    """``allows-not-applicable: "true"`` + not-applicable answer → YELLOW."""

    def test_opted_in_check_is_yellow(self, project, sandbox, interface, tmp_path):
        cmd = _na_cmd(tmp_path)
        _write_na_declaration(project, "audit-na-y", "audit reproducibility",
                              cmd, allows_na=True)
        project.commit()
        run = support.run_check(project, sandbox)
        envelope = support.envelope_of(run, interface)
        result = envelope.get("result") or envelope.get("error", {}).get("details", {})
        entry = next((c for c in support.checks_of(result)
                       if c.get("id") == "audit-na-y"), None)
        assert entry is not None, "check not found in results"
        assert entry.get("status") == support.YELLOW, (
            f"expected YELLOW, got {entry.get('status')!r}\n"
            f"entry: {json.dumps(entry, indent=2)}")

    def test_opted_in_family_is_yellow(self, project, sandbox, interface, tmp_path):
        # revised after implementation: W1-36's kernel declaration of the
        # audit-reproducibility check is now in every project built from the
        # template (DEC-447)
        project.remove_check_declaration("audit-reproducibility")
        cmd = _na_cmd(tmp_path)
        _write_na_declaration(project, "audit-na-f", "audit reproducibility",
                              cmd, allows_na=True)
        project.commit()
        run = support.run_check(project, sandbox)
        envelope = support.envelope_of(run, interface)
        result = envelope.get("result") or envelope.get("error", {}).get("details", {})
        status = support.family_status(result, "audit reproducibility")
        assert status == support.YELLOW, (
            f"family expected YELLOW, got {status!r}")

    def test_opted_in_reason_in_json(self, project, sandbox, interface, tmp_path):
        cmd = _na_cmd(tmp_path)
        _write_na_declaration(project, "audit-na-r", "audit reproducibility",
                              cmd, allows_na=True)
        project.commit()
        run = support.run_check(project, sandbox)
        envelope = support.envelope_of(run, interface)
        blob = json.dumps(envelope)
        assert NOT_APPLICABLE_REASON in blob, (
            f"reason text not in gov check JSON\nenvelope: {blob[:800]}")


class TestRunnerNotOptedIn:
    """Without ``allows-not-applicable``, the same answer is RED."""

    def test_not_opted_in_is_red(self, project, sandbox, interface, tmp_path):
        cmd = _na_cmd(tmp_path)
        _write_na_declaration(project, "audit-no-opt", "audit reproducibility",
                              cmd, allows_na=False)
        project.commit()
        run = support.run_check(project, sandbox)
        envelope = support.envelope_of(run, interface)
        result = envelope.get("result") or envelope.get("error", {}).get("details", {})
        entry = next((c for c in support.checks_of(result)
                       if c.get("id") == "audit-no-opt"), None)
        assert entry is not None
        assert entry.get("status") == support.RED, (
            f"not-opted-in must be RED, got {entry.get('status')!r}")


class TestRunnerOptedInOtherFailures:
    """Opted in but the command fails another way: RED (or not GREEN)."""

    def test_findings_is_red(self, project, sandbox, interface, tmp_path):
        cmd = _findings_cmd(tmp_path)
        _write_na_declaration(project, "audit-fi", "audit reproducibility",
                              cmd, allows_na=True)
        project.commit()
        run = support.run_check(project, sandbox)
        envelope = support.envelope_of(run, interface)
        result = envelope.get("result") or envelope.get("error", {}).get("details", {})
        entry = next((c for c in support.checks_of(result)
                       if c.get("id") == "audit-fi"), None)
        assert entry is not None
        assert entry.get("status") == support.RED

    def test_unmeasured_is_red(self, project, sandbox, interface, tmp_path):
        cmd = _unmeasured_cmd(tmp_path)
        _write_na_declaration(project, "audit-um", "audit reproducibility",
                              cmd, allows_na=True)
        project.commit()
        run = support.run_check(project, sandbox)
        envelope = support.envelope_of(run, interface)
        result = envelope.get("result") or envelope.get("error", {}).get("details", {})
        entry = next((c for c in support.checks_of(result)
                       if c.get("id") == "audit-um"), None)
        assert entry is not None
        assert entry.get("status") == support.RED

    def test_crash_is_red(self, project, sandbox, interface, tmp_path):
        _write_na_declaration(project, "audit-cr", "audit reproducibility",
                              "exit 1", allows_na=True)
        project.commit()
        run = support.run_check(project, sandbox)
        envelope = support.envelope_of(run, interface)
        result = envelope.get("result") or envelope.get("error", {}).get("details", {})
        entry = next((c for c in support.checks_of(result)
                       if c.get("id") == "audit-cr"), None)
        assert entry is not None
        assert entry.get("status") == support.RED

    def test_other_exit_code_is_red(self, project, sandbox, interface, tmp_path):
        _write_na_declaration(project, "audit-e42", "audit reproducibility",
                              "exit 42", allows_na=True)
        project.commit()
        run = support.run_check(project, sandbox)
        envelope = support.envelope_of(run, interface)
        result = envelope.get("result") or envelope.get("error", {}).get("details", {})
        entry = next((c for c in support.checks_of(result)
                       if c.get("id") == "audit-e42"), None)
        assert entry is not None
        assert entry.get("status") == support.RED

    def test_marker_with_exit_0_not_green(self, project, sandbox, interface,
                                          tmp_path):
        """Not-applicable marker with exit 0 is not GREEN.
        DEC-425: not measured is never green."""
        cmd = _na_exit0_cmd(tmp_path)
        _write_na_declaration(project, "audit-na0", "audit reproducibility",
                              cmd, allows_na=True)
        project.commit()
        run = support.run_check(project, sandbox)
        envelope = support.envelope_of(run, interface)
        result = envelope.get("result") or envelope.get("error", {}).get("details", {})
        entry = next((c for c in support.checks_of(result)
                       if c.get("id") == "audit-na0"), None)
        assert entry is not None
        assert entry.get("status") != support.GREEN, (
            f"marker + exit 0 must not be GREEN (DEC-425)\n"
            f"entry: {json.dumps(entry, indent=2)}")


# ==========================================================================
# GROUP 3 — Lifecycle through ``gov check``
# ==========================================================================

class TestLifecycle:
    """No report → YELLOW → valid → GREEN → broken → RED → removed → YELLOW."""

    def test_lifecycle(self, project, sandbox, interface):
        # revised after implementation: W1-36's kernel declaration of the
        # audit-reproducibility check is now in every project built from the
        # template (DEC-447)
        project.remove_check_declaration("audit-reproducibility")
        report_dir = "audit-reports"
        (project.root / report_dir).mkdir(parents=True, exist_ok=True)
        cmd = f"python3 -m gov.check.audit_validator {report_dir}"
        _write_na_declaration(project, "audit-lc", "audit reproducibility",
                              cmd, allows_na=True)

        # Phase 1: no report → YELLOW
        project.commit()
        r1 = support.run_check(project, sandbox)
        e1 = support.envelope_of(r1, interface)
        res1 = e1.get("result") or e1.get("error", {}).get("details", {})
        s1 = support.family_status(res1, "audit reproducibility")
        assert s1 == support.YELLOW, f"Phase 1 (no report): {s1!r}, want YELLOW"
        assert NOT_APPLICABLE_REASON in json.dumps(e1), "Phase 1: reason missing"

        # Phase 2: valid report committed → GREEN
        head = support.git(project.root, "rev-parse", "HEAD").strip()
        project.write(f"{report_dir}/audit-w1.md",
                      _report(commit=head,
                              rows=[("CAP-24", "OK", "README.md")]))
        project.commit()
        r2 = support.run_check(project, sandbox)
        e2 = support.envelope_of(r2, interface)
        res2 = e2.get("result") or e2.get("error", {}).get("details", {})
        s2 = support.family_status(res2, "audit reproducibility")
        assert s2 == support.GREEN, f"Phase 2 (valid): {s2!r}, want GREEN"

        # Phase 3: broken report → RED
        project.write(f"{report_dir}/audit-w1.md",
                      _report(commit=head, rows=[]))
        project.commit()
        r3 = support.run_check(project, sandbox)
        e3 = support.envelope_of(r3, interface)
        res3 = e3.get("result") or e3.get("error", {}).get("details", {})
        s3 = support.family_status(res3, "audit reproducibility")
        assert s3 == support.RED, f"Phase 3 (broken): {s3!r}, want RED"

        # Phase 4: all reports removed → YELLOW again
        (project.root / report_dir / "audit-w1.md").unlink()
        project.commit()
        r4 = support.run_check(project, sandbox)
        e4 = support.envelope_of(r4, interface)
        res4 = e4.get("result") or e4.get("error", {}).get("details", {})
        s4 = support.family_status(res4, "audit reproducibility")
        assert s4 == support.YELLOW, f"Phase 4 (removed): {s4!r}, want YELLOW"


# ==========================================================================
# GROUP 4 — Never GREEN on the not-applicable answer
# ==========================================================================

class TestNeverGreen:

    def test_not_applicable_never_green_json(self, project, sandbox, interface,
                                             tmp_path):
        # revised after implementation: W1-36's kernel declaration of the
        # audit-reproducibility check is now in every project built from the
        # template (DEC-447)
        project.remove_check_declaration("audit-reproducibility")
        cmd = _na_cmd(tmp_path)
        _write_na_declaration(project, "audit-ng", "audit reproducibility",
                              cmd, allows_na=True)
        project.commit()
        run = support.run_check(project, sandbox)
        envelope = support.envelope_of(run, interface)
        result = envelope.get("result") or envelope.get("error", {}).get("details", {})
        status = support.family_status(result, "audit reproducibility")
        assert status != support.GREEN, (
            f"not-applicable must never be GREEN in JSON, got {status!r}")

    def test_not_applicable_never_green_text(self, project, sandbox, interface,
                                             tmp_path):
        # revised after implementation: W1-36's kernel declaration of the
        # audit-reproducibility check is now in every project built from the
        # template (DEC-447)
        project.remove_check_declaration("audit-reproducibility")
        cmd = _na_cmd(tmp_path)
        _write_na_declaration(project, "audit-ngt", "audit reproducibility",
                              cmd, allows_na=True)
        project.commit()
        run = project.gov(sandbox, "check")
        combined = (run.stdout + run.stderr).lower()
        assert "audit" in combined and "reproducibility" in combined, (
            f"family not named in text output\nstdout: {run.stdout[:500]}")
        for line in combined.split("\n"):
            if "audit" in line and "reproducib" in line:
                assert "green" not in line, (
                    f"not-applicable must not show GREEN\nline: {line}")
