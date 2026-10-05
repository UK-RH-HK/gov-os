"""Builder tests for the PreToolUse default-deny guard (W1-02).

Tests exercise behaviour through decide() and the hook run as a process.
Covers every probe defect, DEC-107 through DEC-114, and the deny output format.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
HOOK = REPO / "template" / "governance" / "kernel" / "hooks" / "pretooluse.py"

sys.path.insert(0, str(REPO / "src"))
from gov.guard.decide import (  # noqa: E402
    _extract_bash_write_targets,
    _is_in_scratch,
    _match_pattern,
    _parse_frontmatter,
    decide,
    freeze_state,
    KNOWN_ROLES,
)

TID = "DAEO-test"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_project(tmp_path, tickets=None):
    project = tmp_path / "project"
    project.mkdir()
    if tickets:
        ticket_dir = project / ".tickets"
        ticket_dir.mkdir()
        for name, text in tickets.items():
            (ticket_dir / name).write_text(text, encoding="utf-8")
    return str(project)


def _ticket(ticket_id=TID, wbs_id="W1-99", role="engineer",
            status="in_progress", allowed_paths=("src/**",)):
    paths = "".join(f"- {p}\n" for p in allowed_paths)
    return (
        "---\n"
        f"id: {ticket_id}\n"
        f"status: {status}\n"
        f"wbs_id: {wbs_id}\n"
        f"role: {role}\n"
        "allowed_paths:\n"
        f"{paths}"
        "---\n"
    )


def _std_tickets(**overrides):
    """Standard ticket dict keyed by filename matching ticket id."""
    t = _ticket(**overrides)
    tid = overrides.get("ticket_id", TID)
    return {f"{tid}.md": t}


def _run_hook(project, tool_name, tool_input, role=None, ticket=None,
              cwd=None, agent_type=None, tmpdir=None):
    """Run the hook as a process and return (decision, stdout, rc)."""
    env = {
        "PATH": os.environ["PATH"],
        "PYTHONPATH": str(REPO / "src"),
        "CLAUDE_PROJECT_DIR": str(project),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    if tmpdir:
        env["TMPDIR"] = str(tmpdir)
    if role:
        env["GOV_ROLE"] = role
    if ticket:
        env["GOV_TICKET"] = ticket
    data = {
        "session_id": "s",
        "cwd": str(cwd or project),
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input,
    }
    if agent_type:
        data["agent_type"] = agent_type
        data["agent_id"] = "a"
    p = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(data),
        capture_output=True,
        text=True,
        env=env,
        cwd=str(cwd or project),
    )
    denied = p.returncode == 2 or '"deny"' in p.stdout
    return "deny" if denied else "allow", p.stdout.strip(), p.returncode


# ---------------------------------------------------------------------------
# Defect 1, 2: Test designer with no ticket is read-only (DEC-114)
# ---------------------------------------------------------------------------

class TestDesignerNoTicketReadOnly:

    def test_designer_no_ticket_acceptance_write_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "tests/acceptance/t.py"), "content": "x"},
            project_root=project, role="independent-test-designer", ticket_id=None,
        )
        assert d == "deny"

    def test_designer_no_ticket_scratch_write_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, ".gov-runtime/scratch/n.txt"), "content": "x"},
            project_root=project, role="independent-test-designer", ticket_id=None,
        )
        assert d == "deny"

    def test_designer_no_ticket_bash_write_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "echo x > tests/acceptance/W1-90/t.py"},
            project_root=project, role="independent-test-designer", ticket_id=None,
        )
        assert d == "deny"

    def test_designer_with_ticket_acceptance_allowed(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        (Path(project) / "tests/acceptance").mkdir(parents=True, exist_ok=True)
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "tests/acceptance/t.py"), "content": "x"},
            project_root=project, role="independent-test-designer", ticket_id=TID,
        )
        assert d == "allow"


# ---------------------------------------------------------------------------
# Defect 3, 4: Redirect hides the command's own write
# ---------------------------------------------------------------------------

class TestRedirectWithWriteCommand:

    def test_rm_with_redirect_to_devnull_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "rm README.md > /dev/null"},
            project_root=project, role="engineer", ticket_id=TID,
        )
        assert d == "deny"

    def test_touch_with_stderr_redirect_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "touch README.md 2>/dev/null"},
            project_root=project, role="engineer", ticket_id=TID,
        )
        assert d == "deny"


# ---------------------------------------------------------------------------
# Defect 5: | tee hides the pre-pipe write
# ---------------------------------------------------------------------------

class TestPipeTeeHidesWrite:

    def test_rm_piped_to_tee_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "rm -v README.md | tee .gov-runtime/scratch/log"},
            project_root=project, role="engineer", ticket_id=TID,
        )
        assert d == "deny"


# ---------------------------------------------------------------------------
# Defect 6: Relative paths resolved against cwd, not project root
# ---------------------------------------------------------------------------

class TestCwdResolution:

    def test_relative_path_in_subdirectory_cwd(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        other = Path(project) / "other"
        other.mkdir()
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "echo x > src/gov/guard/a.py"},
            project_root=project, role="engineer", ticket_id=TID,
            cwd=str(other),
        )
        assert d == "deny"

    def test_relative_path_at_project_root_allowed(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "echo x > src/foo.py"},
            project_root=project, role="engineer", ticket_id=TID,
            cwd=project,
        )
        assert d == "allow"


# ---------------------------------------------------------------------------
# Defect 7: fd duplication (2>&1, >&2) is not a file write
# ---------------------------------------------------------------------------

class TestFdDuplication:

    def test_2_redirect_1_allowed(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "ls -la 2>&1"},
            project_root=project, role="engineer", ticket_id=TID,
        )
        assert d == "allow"

    def test_redirect_fd2_allowed(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "echo foo >&2"},
            project_root=project, role="engineer", ticket_id=TID,
        )
        assert d == "allow"

    def test_1_redirect_2_allowed(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "echo foo 1>&2"},
            project_root=project, role="engineer", ticket_id=TID,
        )
        assert d == "allow"


# ---------------------------------------------------------------------------
# Defect 8: > inside quotes is not a redirect
# ---------------------------------------------------------------------------

class TestQuotedRedirect:

    def test_grep_with_arrow_in_quotes_allowed(self, tmp_path):
        project = _make_project(tmp_path)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": 'grep -n "->" README.md'},
            project_root=project, role=None, ticket_id=None,
        )
        assert d == "allow"


# ---------------------------------------------------------------------------
# Defect 9: /dev/ too wide -- only /dev/null is allowed
# ---------------------------------------------------------------------------

class TestDevPaths:

    def test_dev_shm_write_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "echo x > /dev/shm/x"},
            project_root=project, role="engineer", ticket_id=TID,
        )
        assert d == "deny"

    def test_dev_null_redirect_allowed(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "echo x > /dev/null"},
            project_root=project, role="engineer", ticket_id=TID,
        )
        assert d == "allow"

    def test_dev_null_write_tool_allowed_no_role(self, tmp_path):
        project = _make_project(tmp_path)
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": "/dev/null", "content": "x"},
            project_root=project, role=None, ticket_id=None,
        )
        assert d == "allow"

    def test_dev_null_write_tool_allowed_when_frozen(self, tmp_path):
        project = _make_project(tmp_path)
        freeze = Path(project) / ".gov-runtime" / "freeze"
        freeze.parent.mkdir(parents=True, exist_ok=True)
        freeze.write_text("FROZEN owner 2026-10-05T00:00:00Z\n")
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": "/dev/null", "content": "x"},
            project_root=project, role="engineer", ticket_id=None,
        )
        assert d == "allow"


# ---------------------------------------------------------------------------
# Defect 10: sed -i.bak / --in-place not seen as sed -i
# ---------------------------------------------------------------------------

class TestSedInPlace:

    def test_sed_ibak_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "sed -i.bak s/x/y/ README.md"},
            project_root=project, role="engineer", ticket_id=TID,
        )
        assert d == "deny"

    def test_sed_in_place_flag_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "sed --in-place s/x/y/ README.md"},
            project_root=project, role="engineer", ticket_id=TID,
        )
        assert d == "deny"

    def test_sed_i_inside_ticket_allowed(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "sed -i s/x/y/ src/foo.py"},
            project_root=project, role="engineer", ticket_id=TID,
        )
        assert d == "allow"


# ---------------------------------------------------------------------------
# Defect 15: || is a separator
# ---------------------------------------------------------------------------

class TestDoubleOrSeparator:

    def test_or_list_second_command_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "echo x > src/foo.py || rm -r docs"},
            project_root=project, role="engineer", ticket_id=TID,
        )
        assert d == "deny"


# ---------------------------------------------------------------------------
# DEC-114: GOV_TICKET as ticket id and as W1 id
# ---------------------------------------------------------------------------

class TestTicketIdLookup:

    def test_ticket_id_direct(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "src/foo.py"), "content": "x"},
            project_root=project, role="engineer", ticket_id=TID,
        )
        assert d == "allow"

    def test_wbs_id_lookup(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "src/foo.py"), "content": "x"},
            project_root=project, role="engineer", ticket_id="W1-99",
        )
        assert d == "allow"


# ---------------------------------------------------------------------------
# DEC-114: Open and closed tickets give no paths
# ---------------------------------------------------------------------------

class TestTicketStatus:

    def test_open_ticket_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets(status="open"))
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "src/foo.py"), "content": "x"},
            project_root=project, role="engineer", ticket_id=TID,
        )
        assert d == "deny"

    def test_closed_ticket_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets(status="closed"))
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "src/foo.py"), "content": "x"},
            project_root=project, role="engineer", ticket_id=TID,
        )
        assert d == "deny"


# ---------------------------------------------------------------------------
# DEC-114: Repository inside temp dir gets no temp-dir allowance
# ---------------------------------------------------------------------------

class TestRepoInTempDir:

    def test_repo_in_temp_dir_no_temp_scratch(self):
        real_tmp = os.path.realpath(tempfile.gettempdir())
        project = os.path.join(real_tmp, "test_project_w102_builder")
        os.makedirs(project, exist_ok=True)
        try:
            target = os.path.join(real_tmp, "some_file.txt")
            assert not _is_in_scratch(target, project)
            scratch = os.path.join(project, ".gov-runtime", "scratch", "note.txt")
            assert _is_in_scratch(scratch, project)
        finally:
            import shutil
            shutil.rmtree(project, ignore_errors=True)


# ---------------------------------------------------------------------------
# DEC-112: Auditor on own claimed ticket
# ---------------------------------------------------------------------------

class TestAuditor:

    def test_auditor_own_ticket_write_allowed(self, tmp_path):
        project = _make_project(tmp_path, {
            "DAEO-aud.md": _ticket(
                ticket_id="DAEO-aud", role="independent-auditor",
                allowed_paths=("docs/audit/wave-1/**",),
            ),
        })
        (Path(project) / "docs/audit/wave-1").mkdir(parents=True, exist_ok=True)
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "docs/audit/wave-1/report.md"), "content": "x"},
            project_root=project, role="independent-auditor", ticket_id="DAEO-aud",
        )
        assert d == "allow"

    def test_auditor_denied_outside_own_ticket(self, tmp_path):
        project = _make_project(tmp_path, {
            "DAEO-aud.md": _ticket(
                ticket_id="DAEO-aud", role="independent-auditor",
                allowed_paths=("docs/audit/wave-1/**",),
            ),
        })
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "src/main.py"), "content": "x"},
            project_root=project, role="independent-auditor", ticket_id="DAEO-aud",
        )
        assert d == "deny"

    def test_auditor_cannot_use_engineer_ticket(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "src/foo.py"), "content": "x"},
            project_root=project, role="independent-auditor", ticket_id=TID,
        )
        assert d == "deny"

    def test_auditor_acceptance_paths_filtered(self, tmp_path):
        project = _make_project(tmp_path, {
            "DAEO-aud.md": _ticket(
                ticket_id="DAEO-aud", role="independent-auditor",
                allowed_paths=("docs/audit/**", "tests/acceptance/**"),
            ),
        })
        (Path(project) / "tests/acceptance/W1-99").mkdir(parents=True, exist_ok=True)
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "tests/acceptance/W1-99/t.py"), "content": "x"},
            project_root=project, role="independent-auditor", ticket_id="DAEO-aud",
        )
        assert d == "deny"

    def test_auditor_has_scratch(self, tmp_path):
        project = _make_project(tmp_path, {
            "DAEO-aud.md": _ticket(
                ticket_id="DAEO-aud", role="independent-auditor",
                allowed_paths=("docs/audit/**",),
            ),
        })
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, ".gov-runtime/scratch/note.txt"), "content": "x"},
            project_root=project, role="independent-auditor", ticket_id="DAEO-aud",
        )
        assert d == "allow"


# ---------------------------------------------------------------------------
# DEC-113: general-purpose / Explore subagent is read-only
# ---------------------------------------------------------------------------

class TestNonRoleSubagent:

    def test_general_purpose_subagent_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "src/foo.py"), "content": "x"},
            project_root=project, role="engineer", ticket_id=TID,
            subagent_type="general-purpose",
        )
        assert d == "deny"

    def test_explore_subagent_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "src/foo.py"), "content": "x"},
            project_root=project, role="engineer", ticket_id=TID,
            subagent_type="Explore",
        )
        assert d == "deny"

    def test_non_role_subagent_can_read(self, tmp_path):
        project = _make_project(tmp_path)
        d, _ = decide(
            tool_name="Read",
            tool_input={"file_path": os.path.join(project, "README.md")},
            project_root=project, role="engineer", ticket_id=None,
            subagent_type="general-purpose",
        )
        assert d == "allow"

    def test_non_role_subagent_bash_write_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "echo x > src/main.py"},
            project_root=project, role="engineer", ticket_id=TID,
            subagent_type="general-purpose",
        )
        assert d == "deny"


# ---------------------------------------------------------------------------
# Deny output: three keys (hookEventName, permissionDecision, permissionDecisionReason)
# ---------------------------------------------------------------------------

class TestDenyOutputFormat:

    def test_deny_output_has_three_keys(self, tmp_path):
        project = _make_project(tmp_path)
        tmpdir = tmp_path / "systmp"
        tmpdir.mkdir()
        _, stdout, rc = _run_hook(
            project, "Write",
            {"file_path": os.path.join(project, "README.md"), "content": "x"},
            tmpdir=str(tmpdir),
        )
        assert rc == 0
        data = json.loads(stdout)
        hso = data["hookSpecificOutput"]
        assert hso["hookEventName"] == "PreToolUse"
        assert hso["permissionDecision"] == "deny"
        assert "permissionDecisionReason" in hso
        assert set(hso.keys()) == {"hookEventName", "permissionDecision", "permissionDecisionReason"}


# ---------------------------------------------------------------------------
# DEC-114 point 5: /dev/null redirect allowed, also role-less and frozen
# ---------------------------------------------------------------------------

class TestDevNullAcrossStates:

    def test_devnull_redirect_roleless(self, tmp_path):
        project = _make_project(tmp_path)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "echo x > /dev/null"},
            project_root=project, role=None, ticket_id=None,
        )
        assert d == "allow"

    def test_devnull_redirect_frozen(self, tmp_path):
        project = _make_project(tmp_path)
        freeze = Path(project) / ".gov-runtime" / "freeze"
        freeze.parent.mkdir(parents=True, exist_ok=True)
        freeze.write_text("FROZEN owner 2026-10-05T00:00:00Z\n")
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "echo x > /dev/null"},
            project_root=project, role="engineer", ticket_id=None,
        )
        assert d == "allow"


# ---------------------------------------------------------------------------
# GOV_TICKET with path separator names no ticket
# ---------------------------------------------------------------------------

class TestTicketIdValidation:

    def test_ticket_id_with_slash_gives_no_paths(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "src/foo.py"), "content": "x"},
            project_root=project, role="engineer", ticket_id="../etc/passwd",
        )
        assert d == "deny"


# ---------------------------------------------------------------------------
# Frontmatter: YAML-quoted allowed_paths entries
# ---------------------------------------------------------------------------

class TestFrontmatterQuoteStripping:

    def test_single_quoted_path(self):
        text = "---\nid: t\nrole: engineer\nstatus: in_progress\nallowed_paths:\n- '*.md'\n---\n"
        fm = _parse_frontmatter(text)
        assert fm is not None
        assert "*.md" in fm["allowed_paths"]

    def test_double_quoted_path(self):
        text = '---\nid: t\nrole: engineer\nstatus: in_progress\nallowed_paths:\n- "src/**"\n---\n'
        fm = _parse_frontmatter(text)
        assert fm is not None
        assert "src/**" in fm["allowed_paths"]


# ---------------------------------------------------------------------------
# Pattern matching (regression)
# ---------------------------------------------------------------------------

class TestPatternMatching:

    def test_double_star_crosses_dirs(self):
        assert _match_pattern("src/gov/guard/deep/file.py", "src/gov/guard/**")

    def test_single_star_stays_in_one_name(self):
        assert _match_pattern("hooks/pretooluse.py", "hooks/pretooluse*")
        assert not _match_pattern("hooks/sub/pretooluse.py", "hooks/pretooluse*")

    def test_exact_match(self):
        assert _match_pattern("pyproject.toml", "pyproject.toml")
        assert not _match_pattern("docs/pyproject.toml", "pyproject.toml")


# ---------------------------------------------------------------------------
# Unparseable bash command (unbalanced quote)
# ---------------------------------------------------------------------------

class TestUnparseableBash:

    def test_unbalanced_quote_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": 'echo "hello'},
            project_root=project, role="engineer", ticket_id=TID,
        )
        assert d == "deny"


# ---------------------------------------------------------------------------
# End-to-end via process: hook denies and allows correctly
# ---------------------------------------------------------------------------

class TestHookProcess:

    def test_hook_allows_read(self, tmp_path):
        project = _make_project(tmp_path)
        tmpdir = tmp_path / "systmp"
        tmpdir.mkdir()
        decision, _, rc = _run_hook(
            project, "Read",
            {"file_path": os.path.join(project, "README.md")},
            tmpdir=str(tmpdir),
        )
        assert decision == "allow"
        assert rc == 0

    def test_hook_denies_write_no_role(self, tmp_path):
        project = _make_project(tmp_path)
        tmpdir = tmp_path / "systmp"
        tmpdir.mkdir()
        decision, _, rc = _run_hook(
            project, "Write",
            {"file_path": os.path.join(project, "README.md"), "content": "x"},
            tmpdir=str(tmpdir),
        )
        assert decision == "deny"
        assert rc == 0

    def test_hook_allows_inside_ticket(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        tmpdir = tmp_path / "systmp"
        tmpdir.mkdir()
        decision, _, rc = _run_hook(
            project, "Write",
            {"file_path": os.path.join(project, "src/foo.py"), "content": "x"},
            role="engineer", ticket=TID,
            tmpdir=str(tmpdir),
        )
        assert decision == "allow"
        assert rc == 0

    def test_hook_denies_outside_ticket(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        tmpdir = tmp_path / "systmp"
        tmpdir.mkdir()
        decision, _, rc = _run_hook(
            project, "Write",
            {"file_path": os.path.join(project, "README.md"), "content": "x"},
            role="engineer", ticket=TID,
            tmpdir=str(tmpdir),
        )
        assert decision == "deny"
        assert rc == 0

    def test_hook_cwd_resolution(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        other = Path(project) / "other"
        other.mkdir()
        tmpdir = tmp_path / "systmp"
        tmpdir.mkdir()
        decision, _, rc = _run_hook(
            project, "Bash",
            {"command": "echo x > src/foo.py"},
            role="engineer", ticket=TID,
            cwd=str(other), tmpdir=str(tmpdir),
        )
        # src/foo.py relative to other/ lands in other/src/foo.py which is outside ticket paths
        assert decision == "deny"


# ---------------------------------------------------------------------------
# Probe-2 comprehensive Bash cases through decide()
# ---------------------------------------------------------------------------

def _probe_project(tmp_path):
    """Set up a project matching probe_guard2.py's fixture."""
    tickets = {
        f"{TID}.md": _ticket(allowed_paths=("src/gov/guard/**",)),
    }
    project = _make_project(tmp_path, tickets)
    for d in ("src/gov/guard", "tests/acceptance/W1-90", "docs", "other"):
        os.makedirs(os.path.join(project, d), exist_ok=True)
    Path(os.path.join(project, "README.md")).write_text("x")
    return project


E = "engineer"

_BASH_ALLOW = [
    ("rm own file, stderr to /dev/null",
     "rm src/gov/guard/a.py 2>/dev/null", E, TID, None),
    ("touch own file, both streams away",
     "touch src/gov/guard/a.py > /dev/null 2>&1", E, TID, None),
    ("redirect without a space",
     "echo x >src/gov/guard/a.py", E, TID, None),
    ("stderr to own file",
     "echo x 2> src/gov/guard/err.log", E, TID, None),
    ("mkdir then touch, own paths",
     "mkdir -p src/gov/guard/sub && touch src/gov/guard/sub/b.py", E, TID, None),
    ("cd own dir then redirect",
     "cd src/gov/guard && echo x > a.py", E, TID, None),
    ("cp into own dir",
     "cp README.md src/gov/guard/README.copy", E, TID, None),
    ("tee into own file",
     "cat README.md | tee src/gov/guard/a.py", E, TID, None),
    ("absolute-path rm of own file",
     "/bin/rm src/gov/guard/a.py", E, TID, None),
    ("relative write from own subdir (cwd)",
     "echo x > a.py", E, TID, "src/gov/guard"),
    ("two own writes on two lines",
     "touch src/gov/guard/a.py\ntouch src/gov/guard/b.py", E, TID, None),
    ("sed -i on own file",
     "sed -i s/x/y/ src/gov/guard/a.py", E, TID, None),
    ("reads in a list",
     "ls -la; cat README.md", E, TID, None),
    ("pytest piped to tail",
     "python3 -m pytest tests/unit -q 2>&1 | tail -3", E, TID, None),
    ("role-less: cat with stderr away",
     "cat README.md 2>/dev/null", None, None, None),
    ("role-less: ; and rm inside quotes",
     'echo "a; rm b"', None, None, None),
    ("role-less: > inside single quotes",
     "git log --format='%h > %s' -3", None, None, None),
    ("role-less: both streams to /dev/null",
     "ls > /dev/null 2>&1", None, None, None),
    ("role-less: find piped to head",
     'find . -name "*.py" 2>/dev/null | head -5', None, None, None),
    ("role-less: two reads on two lines",
     "ls -la\ngit status --porcelain", None, None, None),
    ("env-prefixed rm of own file",
     "X=1 rm src/gov/guard/a.py", E, TID, None),
    ("role-less: quoted text over two lines with >",
     'echo "line1\nline2 > x"', None, None, None),
]

_BASH_DENY = [
    ("second line removes README",
     "echo hi\nrm README.md", E, TID, None),
    ("background then rm",
     "echo hi & rm README.md", E, TID, None),
    (">& file",
     "echo x >& README.md", E, TID, None),
    ("&>> file",
     "echo x &>> README.md", E, TID, None),
    ("absolute-path rm outside",
     "/bin/rm README.md", E, TID, None),
    ("cd docs then redirect",
     "cd docs && echo x > a.md", E, TID, None),
    ("cd own dir then rm via ..",
     "cd src/gov/guard && rm ../../../README.md", E, TID, None),
    ("mv own file out",
     "mv src/gov/guard/a.py README.md", E, TID, None),
    ("mv outside file in",
     "mv README.md src/gov/guard/", E, TID, None),
    ("rm -r src",
     "rm -r src", E, TID, None),
    ("own write then outside touch",
     "echo x > src/gov/guard/a.py; touch README.md", E, TID, None),
    ("stderr to outside file",
     "ls 2> README.md", E, TID, None),
    ("relative .. from own subdir (cwd)",
     "echo x > ../../../README.md", E, TID, "src/gov/guard"),
    ("role-less touch",
     "touch x", None, None, None),
    ("role-less scratch write",
     "echo x > .gov-runtime/scratch/a", None, None, None),
    ("role-less rm with stderr away",
     "rm README.md 2>/dev/null", None, None, None),
    ("# inside a word must not hide the rest",
     "echo a#b; rm README.md", E, TID, None),
    ("subshell rm outside",
     "(rm README.md)", E, TID, None),
    ("env-prefixed rm outside",
     "X=1 rm README.md", E, TID, None),
    ("rm outside after ;newline",
     "ls;\nrm README.md", E, TID, None),
]


class TestProbe2BashAllow:

    @pytest.mark.parametrize("desc,cmd,role,ticket,cwd_rel", _BASH_ALLOW)
    def test_allowed(self, tmp_path, desc, cmd, role, ticket, cwd_rel):
        project = _probe_project(tmp_path)
        cwd = os.path.join(project, cwd_rel) if cwd_rel else project
        d, reason = decide(
            tool_name="Bash", tool_input={"command": cmd},
            project_root=project, role=role, ticket_id=ticket, cwd=cwd,
        )
        assert d == "allow", f"{desc}: got deny ({reason})"


class TestProbe2BashDeny:

    @pytest.mark.parametrize("desc,cmd,role,ticket,cwd_rel", _BASH_DENY)
    def test_denied(self, tmp_path, desc, cmd, role, ticket, cwd_rel):
        project = _probe_project(tmp_path)
        cwd = os.path.join(project, cwd_rel) if cwd_rel else project
        d, _ = decide(
            tool_name="Bash", tool_input={"command": cmd},
            project_root=project, role=role, ticket_id=ticket, cwd=cwd,
        )
        assert d == "deny", f"{desc}: got allow"


class TestProbe2WriteTool:

    def test_relative_path_cwd_other_denied(self, tmp_path):
        project = _probe_project(tmp_path)
        other = os.path.join(project, "other")
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": "src/gov/guard/a.py", "content": "x"},
            project_root=project, role=E, ticket_id=TID, cwd=other,
        )
        assert d == "deny"


class TestProbe2ScratchCd:

    def test_cd_to_temp_dir_then_redirect_allowed(self, tmp_path, monkeypatch):
        project = _probe_project(tmp_path)
        tmpdir = tmp_path / "systmp"
        tmpdir.mkdir()
        monkeypatch.setenv("TMPDIR", str(tmpdir))
        tempfile.tempdir = None  # force re-evaluation
        try:
            d, _ = decide(
                tool_name="Bash",
                tool_input={"command": f"cd {tmpdir} && echo x > out.txt"},
                project_root=project, role=E, ticket_id=TID, cwd=project,
            )
            assert d == "allow"
        finally:
            tempfile.tempdir = None


class TestProbe2Frozen:

    def test_frozen_rm_own_file_denied(self, tmp_path):
        project = _probe_project(tmp_path)
        freeze = Path(project) / ".gov-runtime" / "freeze"
        freeze.parent.mkdir(parents=True, exist_ok=True)
        freeze.write_text("FROZEN owner 2026-10-05T00:00:00Z\n")
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "rm src/gov/guard/a.py 2>/dev/null"},
            project_root=project, role=E, ticket_id=TID,
        )
        assert d == "deny"

    def test_frozen_roleless_read_allowed(self, tmp_path):
        project = _probe_project(tmp_path)
        freeze = Path(project) / ".gov-runtime" / "freeze"
        freeze.parent.mkdir(parents=True, exist_ok=True)
        freeze.write_text("FROZEN owner 2026-10-05T00:00:00Z\n")
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "ls 2>/dev/null"},
            project_root=project, role=None, ticket_id=None,
        )
        assert d == "allow"


# ---------------------------------------------------------------------------
# DEC-125: a role subagent in a session with no role is read-only
# ---------------------------------------------------------------------------

class TestRoleSubagentNoSessionRole:
    """DEC-125: a role subagent's role applies only when the session has a role."""

    def test_engineer_subagent_no_session_role_write_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "src/foo.py"), "content": "x"},
            project_root=project, role=None, ticket_id=TID,
            subagent_type="engineer",
        )
        assert d == "deny"

    def test_engineer_subagent_blank_session_role_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "src/foo.py"), "content": "x"},
            project_root=project, role="", ticket_id=TID,
            subagent_type="engineer",
        )
        assert d == "deny"

    def test_engineer_subagent_unknown_session_role_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "src/foo.py"), "content": "x"},
            project_root=project, role="developer", ticket_id=TID,
            subagent_type="engineer",
        )
        assert d == "deny"

    def test_designer_subagent_no_session_role_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        (Path(project) / "tests/acceptance").mkdir(parents=True, exist_ok=True)
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "tests/acceptance/t.py"), "content": "x"},
            project_root=project, role=None, ticket_id=TID,
            subagent_type="independent-test-designer",
        )
        assert d == "deny"

    def test_role_subagent_no_session_role_scratch_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, ".gov-runtime/scratch/n.txt"), "content": "x"},
            project_root=project, role=None, ticket_id=TID,
            subagent_type="engineer",
        )
        assert d == "deny"

    def test_role_subagent_no_session_role_reads_allowed(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Read",
            tool_input={"file_path": os.path.join(project, "README.md")},
            project_root=project, role=None, ticket_id=TID,
            subagent_type="engineer",
        )
        assert d == "allow"


# ---------------------------------------------------------------------------
# DEC-117: inside a role subagent, the subagent's role governs
# ---------------------------------------------------------------------------

class TestRoleSubagentGoverns:
    """DEC-117: the subagent's role governs; the session's role plays no part."""

    def test_engineer_subagent_in_orchestrator_session_allowed(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "src/foo.py"), "content": "x"},
            project_root=project, role="orchestrator", ticket_id=TID,
            subagent_type="engineer",
        )
        assert d == "allow"

    def test_engineer_subagent_denied_outside_own_ticket(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "README.md"), "content": "x"},
            project_root=project, role="orchestrator", ticket_id=TID,
            subagent_type="engineer",
        )
        assert d == "deny"

    def test_engineer_subagent_denied_acceptance_tests(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        (Path(project) / "tests/acceptance/W1-99").mkdir(parents=True, exist_ok=True)
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "tests/acceptance/W1-99/t.py"), "content": "x"},
            project_root=project, role="engineer", ticket_id=TID,
            subagent_type="engineer",
        )
        assert d == "deny"

    def test_non_role_subagent_in_engineer_session_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "src/foo.py"), "content": "x"},
            project_root=project, role="engineer", ticket_id=TID,
            subagent_type="claude",
        )
        assert d == "deny"

    def test_frozen_role_subagent_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        freeze = Path(project) / ".gov-runtime" / "freeze"
        freeze.parent.mkdir(parents=True, exist_ok=True)
        freeze.write_text("FROZEN owner 2026-10-05T00:00:00Z\n")
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "src/foo.py"), "content": "x"},
            project_root=project, role="orchestrator", ticket_id=TID,
            subagent_type="engineer",
        )
        assert d == "deny"

    def test_engineer_subagent_bash_write_allowed(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "echo x > src/foo.py"},
            project_root=project, role="orchestrator", ticket_id=TID,
            subagent_type="engineer",
        )
        assert d == "allow"


# ---------------------------------------------------------------------------
# DEC-115: Bash target resolution
# ---------------------------------------------------------------------------

from gov.guard.decide import _expand_token, _has_glob  # noqa: E402


class TestExpandToken:
    """Unit tests for _expand_token: tilde, env vars, unresolvable forms."""

    def test_plain_path(self):
        assert _expand_token("src/gov/guard/decide.py") == "src/gov/guard/decide.py"

    def test_tilde(self, monkeypatch):
        monkeypatch.setenv("HOME", "/test/home")
        assert _expand_token("~/file.py") == "/test/home/file.py"

    def test_tilde_alone(self, monkeypatch):
        monkeypatch.setenv("HOME", "/test/home")
        assert _expand_token("~") == "/test/home"

    def test_env_var(self, monkeypatch):
        monkeypatch.setenv("MY_DIR", "/some/dir")
        assert _expand_token("$MY_DIR/file.py") == "/some/dir/file.py"

    def test_braced_env_var(self, monkeypatch):
        monkeypatch.setenv("MY_DIR", "/some/dir")
        assert _expand_token("${MY_DIR}/file.py") == "/some/dir/file.py"

    def test_command_substitution_dollar_paren(self):
        assert _expand_token("$(echo hi)") is None

    def test_backtick(self):
        assert _expand_token("`echo hi`") is None

    def test_trailing_dollar(self):
        assert _expand_token("src/gov/guard/$") is None

    def test_bare_dollar(self):
        assert _expand_token("$") is None

    def test_unset_variable(self):
        assert _expand_token("$UNSET_VAR_THAT_DOES_NOT_EXIST_W102") is None

    def test_unset_braced(self):
        assert _expand_token("${UNSET_VAR_THAT_DOES_NOT_EXIST_W102}") is None

    def test_complex_brace_form(self, monkeypatch):
        monkeypatch.setenv("X", "val")
        assert _expand_token("${X:-default}") is None

    def test_positional_parameter(self):
        assert _expand_token("${1}") is None

    def test_special_dollar_question(self):
        assert _expand_token("$?") is None

    def test_special_dollar_dollar(self):
        assert _expand_token("$$") is None

    def test_empty_token(self):
        assert _expand_token("") is None

    def test_tilde_unknown_user(self):
        assert _expand_token("~no_such_user_w102/file") is None


class TestTargetResolutionDecide:
    """DEC-115 through decide(): each unresolvable form is denied."""

    def _project(self, tmp_path, monkeypatch):
        tickets = {f"{TID}.md": _ticket(allowed_paths=("src/gov/guard/**",))}
        project = _make_project(tmp_path, tickets)
        for d in ("src/gov/guard", "docs"):
            os.makedirs(os.path.join(project, d), exist_ok=True)
        Path(os.path.join(project, "README.md")).write_text("x")
        # Set up env vars the guard process would see.
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", project)
        monkeypatch.setenv("HOME", os.path.join(str(tmp_path), "home"))
        os.makedirs(os.path.join(str(tmp_path), "home"), exist_ok=True)
        return project

    # -- redirect targets that are unresolvable → denied --

    @pytest.mark.parametrize("cmd", [
        "echo changed > $(echo decide.py)",
        "echo changed > `echo decide.py`",
        'echo changed > "$(echo decide.py)"',
        "echo changed > $UNSET_W102_VAR",
        "echo changed > ${UNSET_W102_VAR}",
        "echo changed > $UNSET_W102_VAR/notes.py",
    ])
    def test_unresolvable_redirect_denied(self, tmp_path, monkeypatch, cmd):
        project = self._project(tmp_path, monkeypatch)
        d, _ = decide(
            tool_name="Bash", tool_input={"command": cmd},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "deny", f"expected deny for: {cmd}"

    # -- write command arguments that are unresolvable → denied --

    @pytest.mark.parametrize("cmd", [
        "touch src/gov/guard/$(date +%s).py",
        "rm src/gov/guard/$UNSET_W102_VAR",
        "touch src/gov/guard/$UNSET_W102_VAR/file.py",
    ])
    def test_unresolvable_write_cmd_denied(self, tmp_path, monkeypatch, cmd):
        project = self._project(tmp_path, monkeypatch)
        d, _ = decide(
            tool_name="Bash", tool_input={"command": cmd},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "deny", f"expected deny for: {cmd}"

    # -- reads with ~, $, globs must still be allowed (role-less session) --

    @pytest.mark.parametrize("cmd", [
        "ls ~",
        "cat $HOME/.profile",
        "echo $(date)",
        "ls *.py",
        "grep -r x src/*",
    ])
    def test_reads_with_special_chars_allowed_roleless(self, tmp_path, monkeypatch, cmd):
        project = self._project(tmp_path, monkeypatch)
        d, _ = decide(
            tool_name="Bash", tool_input={"command": cmd},
            project_root=project, role=None, ticket_id=None, cwd=project,
        )
        assert d == "allow", f"expected allow for read: {cmd}"

    # -- cd to unresolvable → relative write denied, reads allowed --

    def test_cd_unresolvable_then_relative_write_denied(self, tmp_path, monkeypatch):
        project = self._project(tmp_path, monkeypatch)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "cd $UNSET_W102_VAR && echo changed > file.py"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "deny"

    def test_cd_unresolvable_then_reads_allowed(self, tmp_path, monkeypatch):
        project = self._project(tmp_path, monkeypatch)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "cd $UNSET_W102_VAR && ls -la"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "allow"

    # -- variable with a relative path --

    def test_variable_relative_path_inside(self, tmp_path, monkeypatch):
        project = self._project(tmp_path, monkeypatch)
        monkeypatch.setenv("GUARD_DIR", "src/gov/guard")
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "touch $GUARD_DIR/new.py"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "allow"

    def test_variable_relative_path_outside(self, tmp_path, monkeypatch):
        project = self._project(tmp_path, monkeypatch)
        monkeypatch.setenv("UP", "../../..")
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "echo changed > src/gov/guard/$UP/README.md"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "deny"

    # -- glob matching --

    def test_glob_inside_allowed(self, tmp_path, monkeypatch):
        project = self._project(tmp_path, monkeypatch)
        (Path(project) / "src/gov/guard/a.py").write_text("x")
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "rm src/gov/guard/*.py"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "allow"

    def test_glob_matching_nothing_denied(self, tmp_path, monkeypatch):
        project = self._project(tmp_path, monkeypatch)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "rm src/gov/guard/*.nomatch"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "deny"

    def test_glob_with_symlink_outside_denied(self, tmp_path, monkeypatch):
        project = self._project(tmp_path, monkeypatch)
        # Create a symlink from inside guard/ to docs/
        link = Path(project) / "src/gov/guard/docs_link"
        link.symlink_to("../../../docs", target_is_directory=True)
        (Path(project) / "docs/notes.md").write_text("x")
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "rm src/gov/guard/*/notes.md"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "deny"

    # -- variable set inside the command → denied --

    def test_variable_set_inside_command_denied(self, tmp_path, monkeypatch):
        project = self._project(tmp_path, monkeypatch)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "cd src/gov/guard && D=../../.. && echo changed > $D/README.md"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "deny"

    def test_variable_exported_inside_command_denied(self, tmp_path, monkeypatch):
        project = self._project(tmp_path, monkeypatch)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "export D=../../..; echo changed > src/gov/guard/$D/README.md"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "deny"

    # -- tilde resolved from HOME --

    def test_tilde_redirect_outside_denied(self, tmp_path, monkeypatch):
        project = self._project(tmp_path, monkeypatch)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "cd src/gov/guard && echo changed > ~/notes.py"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "deny"

    def test_tilde_as_project_home_allowed(self, tmp_path, monkeypatch):
        project = self._project(tmp_path, monkeypatch)
        monkeypatch.setenv("HOME", project)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "echo changed > ~/src/gov/guard/new.py"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "allow"

    # -- env var expanding to allowed path --

    def test_project_var_inside_allowed(self, tmp_path, monkeypatch):
        project = self._project(tmp_path, monkeypatch)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": f"echo changed > $CLAUDE_PROJECT_DIR/src/gov/guard/new.py"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "allow"

    # -- hook-level: target resolution via the hook process --

    def test_hook_tilde_redirect_outside_denied(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        tmpdir = tmp_path / "systmp"
        tmpdir.mkdir()
        home = tmp_path / "home"
        home.mkdir()
        decision, _, rc = _run_hook(
            project, "Bash",
            {"command": "cd src && echo changed > ~/file.py"},
            role=E, ticket=TID, tmpdir=str(tmpdir),
        )
        assert decision == "deny"

    def test_hook_project_var_allowed(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        tmpdir = tmp_path / "systmp"
        tmpdir.mkdir()
        env = {"CLAUDE_PROJECT_DIR": str(project)}
        decision, _, rc = _run_hook(
            project, "Bash",
            {"command": "echo changed > $CLAUDE_PROJECT_DIR/src/foo.py"},
            role=E, ticket=TID, tmpdir=str(tmpdir),
        )
        assert decision == "allow"


# ---------------------------------------------------------------------------
# DEC-115 repair: bracket glob, brace expansion, cd-no-arg, pushd/popd
# ---------------------------------------------------------------------------

def _probe3_project(tmp_path, monkeypatch):
    """Set up a project matching probe_guard3.py's fixture with a symlink."""
    tickets = {
        f"{TID}.md": _ticket(allowed_paths=("src/gov/guard/**",)),
    }
    project = _make_project(tmp_path, tickets)
    for d in ("src/gov/guard", "docs", "tests/acceptance/W1-90"):
        os.makedirs(os.path.join(project, d), exist_ok=True)
    Path(os.path.join(project, "README.md")).write_text("x")
    Path(os.path.join(project, "docs/notes.md")).write_text("x")
    Path(os.path.join(project, "src/gov/guard/a.py")).write_text("x")
    Path(os.path.join(project, "src/gov/guard/b.py")).write_text("x")
    # Symlink: src/gov/guard/docs_link -> ../../../docs (outside ticket paths)
    os.symlink(
        os.path.join(project, "docs"),
        os.path.join(project, "src/gov/guard/docs_link"),
    )
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", project)
    return project


class TestProbe3SymlinkGlobBrace:
    """The four probe-3 mismatches: bracket glob through symlink, brace
    expansion, cd-no-arg and pushd."""

    def test_bracket_glob_through_symlink_denied(self, tmp_path, monkeypatch):
        project = _probe3_project(tmp_path, monkeypatch)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "touch src/gov/guard/docs_lin[k]/x.md"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "deny"

    def test_brace_expansion_through_symlink_denied(self, tmp_path, monkeypatch):
        project = _probe3_project(tmp_path, monkeypatch)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "touch src/gov/guard/docs_lin{k,k}/x.md"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "deny"

    def test_cd_no_arg_then_relative_write_denied(self, tmp_path, monkeypatch):
        project = _probe3_project(tmp_path, monkeypatch)
        monkeypatch.setenv("HOME", os.path.join(str(tmp_path), "home"))
        os.makedirs(os.path.join(str(tmp_path), "home"), exist_ok=True)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "cd && touch src/gov/guard/a.py"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "deny"

    def test_pushd_then_relative_write_denied(self, tmp_path, monkeypatch):
        project = _probe3_project(tmp_path, monkeypatch)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "pushd docs && touch src/gov/guard/a.py"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "deny"


class TestBracketGlob:
    """[`-glob: matches inside ticket paths allowed; no match denied."""

    def test_bracket_glob_matching_inside_allowed(self, tmp_path, monkeypatch):
        tickets = {f"{TID}.md": _ticket(allowed_paths=("src/gov/guard/**",))}
        project = _make_project(tmp_path, tickets)
        os.makedirs(os.path.join(project, "src/gov/guard"), exist_ok=True)
        Path(os.path.join(project, "src/gov/guard/file.py")).write_text("x")
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", project)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "touch src/gov/guard/fil[e].py"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "allow"

    def test_bracket_glob_matching_nothing_denied(self, tmp_path, monkeypatch):
        tickets = {f"{TID}.md": _ticket(allowed_paths=("src/gov/guard/**",))}
        project = _make_project(tmp_path, tickets)
        os.makedirs(os.path.join(project, "src/gov/guard"), exist_ok=True)
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", project)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "touch src/gov/guard/nonexisten[t].py"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "deny"


class TestBraceExpansion:
    """Brace expansion without symlinks: always denied."""

    def test_brace_no_link_denied(self, tmp_path, monkeypatch):
        tickets = {f"{TID}.md": _ticket(allowed_paths=("src/gov/guard/**",))}
        project = _make_project(tmp_path, tickets)
        os.makedirs(os.path.join(project, "src/gov/guard"), exist_ok=True)
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", project)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "touch src/gov/guard/{a,b}.py"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "deny"


class TestCdNoArg:
    """cd with no argument: goes to HOME."""

    def test_cd_no_arg_home_is_guard_dir_allowed(self, tmp_path, monkeypatch):
        tickets = {f"{TID}.md": _ticket(allowed_paths=("src/gov/guard/**",))}
        project = _make_project(tmp_path, tickets)
        guard = os.path.join(project, "src/gov/guard")
        os.makedirs(guard, exist_ok=True)
        monkeypatch.setenv("HOME", guard)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "cd && touch a.py"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "allow"

    def test_cd_no_arg_home_is_elsewhere_denied(self, tmp_path, monkeypatch):
        tickets = {f"{TID}.md": _ticket(allowed_paths=("src/gov/guard/**",))}
        project = _make_project(tmp_path, tickets)
        os.makedirs(os.path.join(project, "src/gov/guard"), exist_ok=True)
        home = tmp_path / "home"
        home.mkdir()
        monkeypatch.setenv("HOME", str(home))
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "cd && touch a.py"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "deny"


class TestCdDashAndDoubleDash:
    """cd -, cd -- x, pushd, popd followed by relative/absolute writes."""

    def test_cd_dash_then_relative_write_denied(self, tmp_path, monkeypatch):
        tickets = {f"{TID}.md": _ticket(allowed_paths=("src/gov/guard/**",))}
        project = _make_project(tmp_path, tickets)
        os.makedirs(os.path.join(project, "src/gov/guard"), exist_ok=True)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "cd - && touch a.py"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "deny"

    def test_cd_doubledash_then_relative_write_denied(self, tmp_path, monkeypatch):
        tickets = {f"{TID}.md": _ticket(allowed_paths=("src/gov/guard/**",))}
        project = _make_project(tmp_path, tickets)
        guard = os.path.join(project, "src/gov/guard")
        os.makedirs(guard, exist_ok=True)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": f"cd -- {guard} && touch a.py"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "deny"

    def test_pushd_then_relative_write_denied(self, tmp_path, monkeypatch):
        tickets = {f"{TID}.md": _ticket(allowed_paths=("src/gov/guard/**",))}
        project = _make_project(tmp_path, tickets)
        os.makedirs(os.path.join(project, "src/gov/guard"), exist_ok=True)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "pushd src && touch a.py"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "deny"

    def test_popd_then_relative_write_denied(self, tmp_path, monkeypatch):
        tickets = {f"{TID}.md": _ticket(allowed_paths=("src/gov/guard/**",))}
        project = _make_project(tmp_path, tickets)
        os.makedirs(os.path.join(project, "src/gov/guard"), exist_ok=True)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "popd && touch a.py"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "deny"

    def test_cd_dash_then_absolute_write_inside_allowed(self, tmp_path, monkeypatch):
        tickets = {f"{TID}.md": _ticket(allowed_paths=("src/gov/guard/**",))}
        project = _make_project(tmp_path, tickets)
        guard = os.path.join(project, "src/gov/guard")
        os.makedirs(guard, exist_ok=True)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": f"cd - && touch {guard}/a.py"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "allow"

    def test_cd_doubledash_then_absolute_write_inside_allowed(self, tmp_path, monkeypatch):
        tickets = {f"{TID}.md": _ticket(allowed_paths=("src/gov/guard/**",))}
        project = _make_project(tmp_path, tickets)
        guard = os.path.join(project, "src/gov/guard")
        os.makedirs(guard, exist_ok=True)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": f"cd -- {guard} && touch {guard}/a.py"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "allow"

    def test_pushd_then_absolute_write_inside_allowed(self, tmp_path, monkeypatch):
        tickets = {f"{TID}.md": _ticket(allowed_paths=("src/gov/guard/**",))}
        project = _make_project(tmp_path, tickets)
        guard = os.path.join(project, "src/gov/guard")
        os.makedirs(guard, exist_ok=True)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": f"pushd src && touch {guard}/a.py"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "allow"

    def test_popd_then_absolute_write_inside_allowed(self, tmp_path, monkeypatch):
        tickets = {f"{TID}.md": _ticket(allowed_paths=("src/gov/guard/**",))}
        project = _make_project(tmp_path, tickets)
        guard = os.path.join(project, "src/gov/guard")
        os.makedirs(guard, exist_ok=True)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": f"popd && touch {guard}/a.py"},
            project_root=project, role=E, ticket_id=TID, cwd=project,
        )
        assert d == "allow"


class TestReadsWithGlobBraceCdPushdRoleless:
    """Reads with glob, brace, cd-no-arg, pushd stay allowed in role-less sessions."""

    @pytest.mark.parametrize("cmd", [
        "ls [a-z]*",
        "echo {a,b}",
        "cd && ls",
        "pushd docs && ls",
    ])
    def test_roleless_reads_allowed(self, tmp_path, cmd):
        project = _make_project(tmp_path)
        os.makedirs(os.path.join(project, "docs"), exist_ok=True)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": cmd},
            project_root=project, role=None, ticket_id=None, cwd=project,
        )
        assert d == "allow", f"expected allow for role-less read: {cmd}"


# ---------------------------------------------------------------------------
# DEC-156: orchestrator writes anywhere except tests/acceptance/**
# ---------------------------------------------------------------------------

class TestOrchestratorScope:
    """DEC-156: the orchestrator may write anywhere in the repository
    except ``tests/acceptance/**``, whatever the ticket or with no ticket."""

    def test_orchestrator_allowed_outside_ticket_paths(self, tmp_path):
        project = _make_project(tmp_path, {
            "DAEO-orch.md": _ticket(
                ticket_id="DAEO-orch", role="orchestrator",
                allowed_paths=(".claude/settings.json",),
            ),
        })
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "README.md"), "content": "x"},
            project_root=project, role="orchestrator", ticket_id="DAEO-orch",
        )
        assert d == "allow"

    def test_orchestrator_allowed_without_ticket(self, tmp_path):
        project = _make_project(tmp_path)
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "src/foo.py"), "content": "x"},
            project_root=project, role="orchestrator", ticket_id=None,
        )
        assert d == "allow"

    def test_orchestrator_denied_under_acceptance(self, tmp_path):
        project = _make_project(tmp_path)
        (Path(project) / "tests/acceptance/W1-99").mkdir(parents=True, exist_ok=True)
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "tests/acceptance/W1-99/t.py"), "content": "x"},
            project_root=project, role="orchestrator", ticket_id=None,
        )
        assert d == "deny"

    def test_orchestrator_bash_write_allowed(self, tmp_path):
        project = _make_project(tmp_path)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "echo changed > README.md"},
            project_root=project, role="orchestrator", ticket_id=None,
        )
        assert d == "allow"

    def test_engineer_still_denied_outside_paths(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "README.md"), "content": "x"},
            project_root=project, role="engineer", ticket_id=TID,
        )
        assert d == "deny"


# ---------------------------------------------------------------------------
# DEC-156 + DEC-136 batch 3: the wide orchestrator scope does not reach
# an orchestrator subagent in a non-orchestrator session
# ---------------------------------------------------------------------------

class TestOrchestratorSubagentScope:
    """The wide DEC-156 scope applies only in an orchestrator session.
    An orchestrator subagent in a non-orchestrator session falls through
    to the ticket-path rule."""

    def test_orchestrator_subagent_denied_in_engineer_session(self, tmp_path):
        """The orchestrator subagent in an engineer session cannot write
        outside the ticket's paths, even though a main-thread orchestrator
        could."""
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "README.md"), "content": "x"},
            project_root=project, role="engineer", ticket_id=TID,
            subagent_type="orchestrator",
        )
        assert d == "deny"

    def test_orchestrator_subagent_denied_in_engineer_session_on_source(self, tmp_path):
        """The subagent gets nothing from the engineer's own ticket paths:
        the ticket's role is engineer, not orchestrator."""
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "src/foo.py"), "content": "x"},
            project_root=project, role="engineer", ticket_id=TID,
            subagent_type="orchestrator",
        )
        assert d == "deny"

    def test_orchestrator_subagent_allowed_on_orchestrator_ticket(self, tmp_path):
        """On a ticket whose role IS orchestrator, the subagent gets that
        ticket's allowed_paths."""
        project = _make_project(tmp_path, {
            "DAEO-orch.md": _ticket(
                ticket_id="DAEO-orch", role="orchestrator",
                allowed_paths=(".claude/settings.json",),
            ),
        })
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, ".claude/settings.json"), "content": "x"},
            project_root=project, role="engineer", ticket_id="DAEO-orch",
            subagent_type="orchestrator",
        )
        assert d == "allow"

    def test_orchestrator_subagent_denied_outside_orchestrator_ticket_paths(self, tmp_path):
        """Even on the orchestrator ticket, paths outside the ticket's
        allowed_paths are denied in a non-orchestrator session."""
        project = _make_project(tmp_path, {
            "DAEO-orch.md": _ticket(
                ticket_id="DAEO-orch", role="orchestrator",
                allowed_paths=(".claude/settings.json",),
            ),
        })
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "README.md"), "content": "x"},
            project_root=project, role="engineer", ticket_id="DAEO-orch",
            subagent_type="orchestrator",
        )
        assert d == "deny"

    def test_orchestrator_subagent_wide_in_orchestrator_session(self, tmp_path):
        """In an orchestrator session, the orchestrator subagent keeps the
        wide DEC-156 scope."""
        project = _make_project(tmp_path, {
            "DAEO-orch.md": _ticket(
                ticket_id="DAEO-orch", role="orchestrator",
                allowed_paths=(".claude/settings.json",),
            ),
        })
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "README.md"), "content": "x"},
            project_root=project, role="orchestrator", ticket_id="DAEO-orch",
            subagent_type="orchestrator",
        )
        assert d == "allow"

    def test_orchestrator_subagent_without_ticket_denied(self, tmp_path):
        """Without a ticket the orchestrator subagent in a non-orchestrator
        session has no paths."""
        project = _make_project(tmp_path)
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "README.md"), "content": "x"},
            project_root=project, role="engineer", ticket_id=None,
            subagent_type="orchestrator",
        )
        assert d == "deny"

    def test_orchestrator_subagent_scratch_in_non_orchestrator_session(self, tmp_path):
        """Scratch is still available to a known-role subagent."""
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, ".gov-runtime/scratch/note.txt"), "content": "x"},
            project_root=project, role="engineer", ticket_id=TID,
            subagent_type="orchestrator",
        )
        assert d == "allow"

    def test_orchestrator_main_thread_still_wide(self, tmp_path):
        """The main thread of an orchestrator session still has the wide scope
        (no regression from the subagent fix)."""
        project = _make_project(tmp_path)
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, "README.md"), "content": "x"},
            project_root=project, role="orchestrator", ticket_id=None,
        )
        assert d == "allow"


# ---------------------------------------------------------------------------
# DEC-176: .gov-runtime/ other than scratch/** denied to the orchestrator
# ---------------------------------------------------------------------------

class TestGovRuntimeProtected:
    """DEC-176: the freeze flag, snapshots, findings and records under
    .gov-runtime/ are denied to the orchestrator. scratch/** stays writable."""

    @pytest.mark.parametrize("rel", [
        ".gov-runtime/freeze",
        ".gov-runtime/findings.jsonl",
        ".gov-runtime/records.jsonl",
        ".gov-runtime/snapshots/snap.json",
    ])
    def test_orchestrator_denied_gov_runtime_file_tool(self, tmp_path, rel):
        project = _make_project(tmp_path)
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, rel), "content": "x"},
            project_root=project, role="orchestrator", ticket_id=None,
        )
        assert d == "deny", f"orchestrator was not denied {rel}"

    @pytest.mark.parametrize("rel", [
        ".gov-runtime/freeze",
        ".gov-runtime/findings.jsonl",
    ])
    def test_orchestrator_denied_gov_runtime_bash(self, tmp_path, rel):
        project = _make_project(tmp_path)
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": f"echo x >> {rel}"},
            project_root=project, role="orchestrator", ticket_id=None,
        )
        assert d == "deny", f"orchestrator Bash was not denied {rel}"

    def test_orchestrator_scratch_still_allowed(self, tmp_path):
        project = _make_project(tmp_path)
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, ".gov-runtime/scratch/note.txt"), "content": "x"},
            project_root=project, role="orchestrator", ticket_id=None,
        )
        assert d == "allow"

    def test_orchestrator_scratch_orchestrator_still_allowed(self, tmp_path):
        project = _make_project(tmp_path)
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, ".gov-runtime/scratch/orchestrator/cp.json"),
                         "content": "x"},
            project_root=project, role="orchestrator", ticket_id=None,
        )
        assert d == "allow"

    def test_engineer_gov_runtime_still_denied(self, tmp_path):
        """Other roles were already denied .gov-runtime/ paths (no regression)."""
        project = _make_project(tmp_path, _std_tickets())
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, ".gov-runtime/freeze"), "content": "x"},
            project_root=project, role="engineer", ticket_id=TID,
        )
        assert d == "deny"

    def test_orchestrator_denied_gov_runtime_with_ticket(self, tmp_path):
        """DEC-176 holds regardless of the ticket."""
        project = _make_project(tmp_path, {
            "DAEO-orch.md": _ticket(ticket_id="DAEO-orch", role="orchestrator"),
        })
        d, _ = decide(
            tool_name="Write",
            tool_input={"file_path": os.path.join(project, ".gov-runtime/freeze"), "content": "x"},
            project_root=project, role="orchestrator", ticket_id="DAEO-orch",
        )
        assert d == "deny"


# ---------------------------------------------------------------------------
# W1-46 batch 5: a write through a link made in the same command, and cp
# with its directory in an option (DEC-311, DEC-135)
# ---------------------------------------------------------------------------

def _bash(project, command):
    d, _ = decide(
        tool_name="Bash", tool_input={"command": command},
        project_root=project, role="engineer", ticket_id=TID,
    )
    return d


class TestLinkThenWrite:

    def _project(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        os.makedirs(os.path.join(project, "src"))
        os.makedirs(os.path.join(project, "tests/acceptance/W1-99"))
        return project

    @pytest.mark.parametrize("command", [
        "ln -s {p}/tests/acceptance/W1-99 src/l && echo x > src/l/t.py",
        "ln -s {p}/tests/acceptance/W1-99 src/l; touch src/l/t.py",
        "ln tests/acceptance/W1-99/t.py src/l.py && echo x > src/l.py",
        "ln -s {p}/.gov-runtime/freeze src/l && touch src/l",
        "touch src/a && ln -s {p}/tests/acceptance/W1-99 src/l",
        # A relative name of a symbolic link is not resolved: refused.
        "ln -s ../tests/acceptance/W1-99 src/l && touch src/l/t.py",
        "ln -s a.py src/l.py && touch src/b.py",
    ])
    def test_link_and_write_denied(self, tmp_path, command):
        project = self._project(tmp_path)
        assert _bash(project, command.format(p=project)) == "deny"

    @pytest.mark.parametrize("command", [
        "ln -s {p}/src/a.py src/l.py",
        "ln src/a.py src/l.py",
        "ln -s {p}/tests/acceptance/W1-99 src/l",
        "ln -s {p}/src/a.py src/l.py && echo x > src/l.py",
        "ln src/a.py src/l.py && touch src/b.py",
    ])
    def test_link_inside_the_paths_allowed(self, tmp_path, command):
        project = self._project(tmp_path)
        assert _bash(project, command.format(p=project)) == "allow"


class TestCpTargetDirectory:

    @pytest.mark.parametrize("option", [
        "-t {d}", "-t{d}", "-rt {d}", "--target-directory={d}",
        "--target-directory {d}", "--target={d}",
    ])
    @pytest.mark.parametrize("directory", ["tests/acceptance/W1-99", ".tickets"])
    def test_outside_the_paths_denied(self, tmp_path, option, directory):
        project = _make_project(tmp_path, _std_tickets())
        assert _bash(project, f"cp {option.format(d=directory)} src/a.py") == "deny"

    @pytest.mark.parametrize("command", [
        "cp src/a.py -t",                     # no value
        "cp --target-directory= src/a.py",    # an empty value
        "cp --tmpfoo=x src/a.py src/b.py",    # an option the guard cannot read
        "cp -t src ..",                       # no name to land under
    ])
    def test_unreadable_form_denied(self, tmp_path, command):
        project = _make_project(tmp_path, _std_tickets())
        assert _bash(project, command) == "deny"

    @pytest.mark.parametrize("command", [
        "cp -t src docs/a.py",
        "cp --target-directory=src/gov docs/a.py docs/b.py",
        "cp docs/a.py src/b.py",
    ])
    def test_inside_the_paths_allowed(self, tmp_path, command):
        project = _make_project(tmp_path, _std_tickets())
        assert _bash(project, command) == "allow"


# ---------------------------------------------------------------------------
# W1-46 batch 6: a hard link to a file the role may not write, and mv
# --target-directory and install (DEC-334)
# ---------------------------------------------------------------------------

class TestHardLinkMvInstall:

    @pytest.mark.parametrize("command", [
        "ln tests/acceptance/W1-99/t.py src/l.py",
        "ln -f docs/a.py src/l.py",
        "cp -l tests/acceptance/W1-99/t.py src/l.py",
        "cp -al docs/a.py src/l.py",
        "cp --link -t src docs/a.py",
        "link .tickets/DAEO-test.md src/l.md",
        "ln .gov-runtime/freeze src/l",
        "mv --target-directory=tests/acceptance/W1-99 src/a.py",
        "mv --target-directory .tickets src/a.py",
        "mv -t.tickets src/a.py",
        "mv --target-directory= src/a.py",    # an empty value
        "mv --tmpfoo=x src/a.py src/b.py",    # an option the guard cannot read
        "install -t tests/acceptance/W1-99 src/a.py",
        "install src/a.py tests/acceptance/W1-99/t.py",
        "install -m 644 src/a.py .tickets/DAEO-test.md",
        "install -D src/a.py .tickets/w/a.py",
        "install -d src/d tests/acceptance/W1-99/d",
        "install src/a.py -t",                # no value
    ])
    def test_denied(self, tmp_path, command):
        project = _make_project(tmp_path, _std_tickets())
        assert _bash(project, command) == "deny"

    @pytest.mark.parametrize("command", [
        "link src/a.py src/l.py",
        "cp -l src/a.py src/l.py",
        "mv --target-directory=src/gov src/a.py",
        "mv src/a.py src/b.py",
        "install src/a.py src/b.py",
        "install -t src/gov docs/a.py",
        "install -d src/d",
    ])
    def test_inside_the_paths_allowed(self, tmp_path, command):
        project = _make_project(tmp_path, _std_tickets())
        assert _bash(project, command) == "allow"


# ---------------------------------------------------------------------------
# W1-46 batch 7: an option with its value after the destination of install,
# cp and ln (DEC-334, DEC-311)
# ---------------------------------------------------------------------------

class TestOptionAfterTheDestination:

    @pytest.mark.parametrize("command", [
        "cd src && install a.py ../tests/acceptance/W1-99/t.py -m 644",
        "cd src && install a.py ../.tickets/DAEO-test.md --mode 644",
        "cd src && cp a.py ../tests/acceptance/W1-99/t.py -S bak",
        "cd src && cp a.py ../tests/acceptance/W1-99/t.py --suffix bak",
        "cd src && ln -sf a.py ../tests/acceptance/W1-99/t.py -S bak",
        "cd src && ln a.py ../tests/acceptance/W1-99/t.py --suffix bak",
    ])
    def test_denied(self, tmp_path, command):
        project = _make_project(tmp_path, _std_tickets())
        assert _bash(project, command) == "deny"

    @pytest.mark.parametrize("command", [
        "cd src && install -m 644 a.py b.py",
        "cd src && cp a.py b.py",
        "cd src && cp a.py b.py -S bak",
    ])
    def test_inside_the_paths_allowed(self, tmp_path, command):
        project = _make_project(tmp_path, _std_tickets())
        assert _bash(project, command) == "allow"


# ---------------------------------------------------------------------------
# W1-50: the freeze flag carries a marker (DEC-402)
# ---------------------------------------------------------------------------

class TestFreezeState:

    def _flag(self, tmp_path):
        flag = Path(tmp_path) / ".gov-runtime" / "freeze"
        flag.parent.mkdir(parents=True, exist_ok=True)
        return flag

    def test_nothing_at_the_path_is_absent(self, tmp_path):
        assert freeze_state(str(tmp_path)) == "absent"
        self._flag(tmp_path)
        assert freeze_state(str(tmp_path)) == "absent"

    @pytest.mark.parametrize("content", [
        b"", b"off\n", b"FROZE N\n", b"\n\n", b"\xef\xbb\xbf",
        b"\xff\xfeo\x00f\x00f\x00\n\x00",
    ])
    def test_a_file_without_the_marker_is_unmarked(self, tmp_path, content):
        self._flag(tmp_path).write_bytes(content)
        assert freeze_state(str(tmp_path)) == "unmarked"

    def test_a_character_device_is_unmarked(self, tmp_path):
        self._flag(tmp_path).symlink_to("/dev/null")
        assert freeze_state(str(tmp_path)) == "unmarked"

    @pytest.mark.parametrize("content", [
        b"FROZEN\n", b"FROZEN owner 2026-10-05T00:00:00Z\n", b"frozen\n",
        b"a note\n  FROZEN x\n", b"\xef\xbb\xbfFROZEN\r\nmore\r\n",
        b"FROZEN",
    ])
    def test_a_marker_line_is_frozen(self, tmp_path, content):
        self._flag(tmp_path).write_bytes(content)
        assert freeze_state(str(tmp_path)) == "frozen"

    @pytest.mark.parametrize("content", [
        "FROZEN owner\n".encode("utf-16"), "FROZEN owner\n".encode("utf-32-be"),
        b"\x00FROZEN\n", b"FROZEN\x00 owner\n", "​FROZEN\n".encode(),
        b"FROZEN: owner\n", b'"FROZEN"\n', b"# FROZEN owner\n",
        b"state: frozen\n", b"FROZEN_BY: owner\n",
        # The word is not told apart from a longer word or a negation.
        b"not FROZEN\n", b"FROZENX\n",
    ])
    def test_a_file_that_carries_the_word_is_frozen(self, tmp_path, content):
        self._flag(tmp_path).write_bytes(content)
        assert freeze_state(str(tmp_path)) == "frozen"

    def test_a_dangling_link_as_runtime_folder_is_frozen(self, tmp_path):
        target = tmp_path / "no-such-folder"
        (tmp_path / ".gov-runtime").symlink_to(target)
        assert freeze_state(str(tmp_path)) == "frozen"
        assert not os.path.lexists(target)

    def test_a_regular_file_as_runtime_folder_is_absent(self, tmp_path):
        (tmp_path / ".gov-runtime").write_bytes(b"")
        assert freeze_state(str(tmp_path)) == "absent"

    def test_decide_takes_the_state_its_caller_read(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        target = {"file_path": os.path.join(project, "src/a.py"), "content": "x"}
        args = ("Write", target, project, "engineer", TID)
        assert decide(*args)[0] == "allow"
        assert decide(*args, flag="frozen") == ("deny", "frozen: all writes denied")
        self._flag(project).write_text("FROZEN\n")
        assert decide(*args)[0] == "deny"

    def test_a_file_too_large_to_read_whole_is_frozen(self, tmp_path):
        # Stricter: the marker may be past what is read.
        self._flag(tmp_path).write_bytes(b"filler line\n" * 10_000)
        assert freeze_state(str(tmp_path)) == "frozen"

    def test_a_fifo_is_frozen_and_is_not_opened(self, tmp_path):
        os.mkfifo(self._flag(tmp_path))
        assert freeze_state(str(tmp_path)) == "frozen"

    def test_a_directory_and_a_dangling_link_are_frozen(self, tmp_path):
        flag = self._flag(tmp_path)
        flag.mkdir()
        assert freeze_state(str(tmp_path)) == "frozen"
        flag.rmdir()
        flag.symlink_to(tmp_path / "no-such-file")
        assert freeze_state(str(tmp_path)) == "frozen"

    def test_an_empty_flag_does_not_freeze_a_write(self, tmp_path):
        project = _make_project(tmp_path, _std_tickets())
        self._flag(project).write_text("")
        assert _bash(project, "cd src && cp a.py b.py") == "allow"


RECORDS = ".gov-runtime/records.jsonl"


class TestUnmarkedFlagRecord:
    """The hook's record of an unmarked presence (DEC-402, DEC-177)."""

    def _project(self, tmp_path):
        project = Path(_make_project(tmp_path, _std_tickets()))
        (project / ".gov-runtime").mkdir()
        (project / ".gov-runtime" / "freeze").write_bytes(b"")
        return project

    def _write(self, project):
        return _run_hook(
            project, "Write",
            {"file_path": str(project / "src" / "a.py"), "content": "x"},
            role="engineer", ticket=TID)[0]

    def test_an_allowed_write_is_recorded(self, tmp_path):
        project = self._project(tmp_path)
        assert self._write(project) == "allow"
        lines = (project / RECORDS).read_text().splitlines()
        assert len(lines) == 1
        assert json.loads(lines[0])["paths"] == [".gov-runtime/freeze"]

    @pytest.mark.parametrize("command", ["sudo ls", "pip install requests"])
    def test_a_call_a_later_rule_denies_is_not_recorded(self, tmp_path, command):
        project = self._project(tmp_path)
        decision, out, rc = _run_hook(project, "Bash", {"command": command},
                                      role="engineer", ticket=TID)
        assert (decision, rc) == ("deny", 0) and "frozen" not in out
        assert not (project / RECORDS).exists()

    def test_nothing_is_written_through_a_link(self, tmp_path):
        project = self._project(tmp_path)
        target = tmp_path / "elsewhere.txt"
        target.write_text("kept\n")
        (project / RECORDS).symlink_to(target)
        assert self._write(project) == "allow"
        assert target.read_text() == "kept\n"
        (project / RECORDS).unlink()
        (project / RECORDS).symlink_to(tmp_path / "missing.jsonl")
        assert self._write(project) == "allow"
        assert not (tmp_path / "missing.jsonl").exists()

    def test_nothing_is_written_in_a_linked_runtime_folder(self, tmp_path):
        project = Path(_make_project(tmp_path, _std_tickets()))
        elsewhere = tmp_path / "elsewhere"
        elsewhere.mkdir()
        (elsewhere / "freeze").write_bytes(b"")
        (project / ".gov-runtime").symlink_to(elsewhere)
        assert self._write(project) == "allow"
        assert not (elsewhere / "records.jsonl").exists()
