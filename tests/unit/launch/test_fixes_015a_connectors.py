"""Builder tests for fixes-015a F1 (connectors off), F14 (lead effort) and F19 (rubric model) in the launcher's pieces.

Regression evidence only (DEC-136): the MCP line of a role file, the launcher's own ``--mcp-config``, a caller's config
inside or outside the role's list, the lead's effort, the merge's connectors key and the doctor's drift line.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.adapters import merge  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402
from gov.doctor import command as doctor  # noqa: E402
from gov.launch import launcher, role  # noqa: E402


def _roles(tmp_path, **files):
    folder = tmp_path / role.ROLES_REL
    folder.mkdir(parents=True)
    for name, text in files.items():
        (folder / f"{name}.md").write_text(f"# {name}\n\n{text}\n", encoding="utf-8")
    return tmp_path


def test_no_mcp_line_is_an_empty_list(tmp_path):
    assert role.mcp_tools(_roles(tmp_path, engineer="- **Version:** 1.0.0"), "engineer") == []


def test_the_mcp_line_lists_its_names(tmp_path):
    root = _roles(tmp_path, engineer="- **MCP tools:** alpha, beta.2")
    assert role.mcp_tools(root, "engineer") == ["alpha", "beta.2"]


@pytest.mark.parametrize("line", ("- **MCP tools:** a, a", "- **MCP tools:** a b, c", "- **MCP tools:** a\n- **MCP tools:** b"))
def test_a_doubled_or_odd_mcp_line_refuses(tmp_path, line):
    with pytest.raises(GovError) as caught:
        role.mcp_tools(_roles(tmp_path, engineer=line), "engineer")
    assert caught.value.code == "LAUNCH_REFUSED"


def test_an_unreadable_lead_role_file_is_an_empty_list_and_a_worker_one_refuses(tmp_path):
    root = _roles(tmp_path)
    assert role.mcp_tools(root, "ticket-lead", required=False) == []
    with pytest.raises(GovError):
        role.mcp_tools(root, "engineer")


def test_the_launcher_config_holds_one_server_per_listed_name(tmp_path):
    root = _roles(tmp_path, engineer="- **MCP tools:** alpha, beta")
    flag, value = launcher._mcp_args(root, "engineer", [])
    assert flag == "--mcp-config" and set(json.loads(value)["mcpServers"]) == {"alpha", "beta"}


def test_a_lead_reads_the_ticket_lead_file(tmp_path):
    root = _roles(tmp_path, **{"ticket-lead": "- **MCP tools:** alpha"})
    for name in launcher.LEAD_ROLES:
        assert set(json.loads(launcher._mcp_args(root, name, [])[1])["mcpServers"]) == {"alpha"}


@pytest.mark.parametrize("spelling", ("spaced", "joined"))
def test_a_caller_config_is_accepted_only_inside_the_list(tmp_path, spelling):
    root = _roles(tmp_path, engineer="- **MCP tools:** alpha")
    def args(servers):
        text = json.dumps({"mcpServers": {name: {} for name in servers}})
        return ["--mcp-config", text] if spelling == "spaced" else [f"--mcp-config={text}"]
    launcher._mcp_args(root, "engineer", args(["alpha"]))
    with pytest.raises(GovError) as caught:
        launcher._mcp_args(root, "engineer", args(["alpha", "intruder"]))
    assert "--mcp-config" in caught.value.message and "intruder" in caught.value.message


@pytest.mark.parametrize("value", ("not json {", "[]", '{"mcpServers": []}', "/nonexistent/file.json"))
def test_a_caller_config_that_cannot_be_read_refuses(tmp_path, value):
    root = _roles(tmp_path, engineer="- **MCP tools:** alpha")
    with pytest.raises(GovError) as caught:
        launcher._mcp_args(root, "engineer", ["--mcp-config", value])
    assert "--mcp-config" in caught.value.message


def test_a_caller_config_file_inside_the_list_is_accepted(tmp_path):
    root = _roles(tmp_path, engineer="- **MCP tools:** alpha")
    path = tmp_path / "mcp.json"
    path.write_text(json.dumps({"mcpServers": {"alpha": {}}}), encoding="utf-8")
    launcher._mcp_args(root, "engineer", ["--mcp-config", str(path)])


def test_a_lead_gets_medium_effort_unless_the_caller_names_one():
    assert launcher._lead_effort_args(["-p", "go"]) == ["--effort", "medium"]
    assert launcher._lead_effort_args(["--effort", "high"]) == []
    assert launcher._lead_effort_args(["--effort=low"]) == []


def test_the_merge_adds_the_connectors_key_and_keeps_a_value_the_project_holds():
    assert merge.merge_settings(None, {"permissions": {}})["disableClaudeAiConnectors"] is True
    own = {"disableClaudeAiConnectors": False, "other": 1}
    merged = merge.merge_settings(own, {"permissions": {}})
    assert merged["disableClaudeAiConnectors"] is False and merged["other"] == 1


def test_the_kit_settings_carry_the_key():
    data = json.loads((REPO / "template/governance/kernel/settings.json").read_text(encoding="utf-8"))
    assert data["disableClaudeAiConnectors"] is True


def test_doctor_reports_settings_without_the_key_as_non_blocking_drift(tmp_path):
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude/settings.json").write_text('{"hooks": {}}', encoding="utf-8")
    section = doctor._check_connectors(tmp_path)
    assert section["status"] == "drift" and section["drift_blocking"] is False
    assert "disableClaudeAiConnectors" in section["reason"] and not doctor._blocks_health(section)
    (tmp_path / ".claude/settings.json").write_text('{"disableClaudeAiConnectors": true}', encoding="utf-8")
    assert doctor._check_connectors(tmp_path)["status"] == "pass"
