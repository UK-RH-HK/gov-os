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
        freeze.write_text("")
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
        freeze.write_text("")
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
        freeze.write_text("")
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
        freeze.write_text("")
        d, _ = decide(
            tool_name="Bash",
            tool_input={"command": "ls 2>/dev/null"},
            project_root=project, role=None, ticket_id=None,
        )
        assert d == "allow"
