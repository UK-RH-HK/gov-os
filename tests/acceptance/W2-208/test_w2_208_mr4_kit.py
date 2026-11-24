"""Fix MR-4 (DEC-1246 (3)(b); INTEGRATION-PLAN row 4-2): the kit holds the model hook, the table and ``defaultMode``;
the root permission source matches the kit's two deny lines.

Read: the kit's files, a project adopted at the current kit (``adopted_at_b``: ``copier copy`` and ``gov adapters
generate``), ``gov update`` on a copy holding an older hook, and the hook run as a subprocess on an event.
"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

import w2_208_support as support

HOOK_REL = ".claude/hooks/agent_model.py"
TABLE_REL = "governance/project/role-table.yaml"
HOOKS_JSONC_REL = ".rulesync/hooks.jsonc"
MATCHER = "Agent|Task"
DENY = {"Bash(git push *)", "Bash(sudo *)"}
DENY_ALL = DENY | {"Bash(git push:*)", "Bash(sudo:*)"}
STAND_IN = b"#!/usr/bin/env python3\n" + b"# an older copy of the model hook\n" * 63   # padded below to 2,124 bytes
STAND_IN = (STAND_IN + b"#" * 2124)[:2124]


def _settings_hook_entries(settings):
    entries = (settings.get("hooks") or {}).get("PreToolUse") or []
    return [e for e in entries if "agent_model.py" in json.dumps(e)]


def _hook_run(project, model, tasks=("DAEO-aaaa",)):
    """The project's own hook, as the settings run it, on one spawn of a helper."""
    tool_input = {"description": "helper", "prompt": "Do the work.\n\n" + "\n".join(f"Task: {t}" for t in tasks),
                  "subagent_type": "engineer"}
    if model is not None:
        tool_input["model"] = model
    event = {"session_id": "00000000-0000-4000-8000-000000000208", "hook_event_name": "PreToolUse",
             "tool_name": "Agent", "tool_input": tool_input}
    env = {"PATH": "/usr/bin:/bin", "HOME": str(project), "LANG": "C.UTF-8", "CLAUDE_PROJECT_DIR": str(project)}
    return subprocess.run([sys.executable, "-I", str(project / HOOK_REL)], input=json.dumps(event), env=env,
                          capture_output=True, text=True, cwd=str(project.parent), timeout=60)


# --------------------------------------------------------------------------------------------------------------------
# The kit's own files
# --------------------------------------------------------------------------------------------------------------------

def test_mr4_the_kit_holds_the_hook_file_byte_equal_to_gov_os_s_own():
    """Red on the base: the kit holds no ``.claude/hooks/agent_model.py``."""
    kit = support.TEMPLATE / HOOK_REL
    assert kit.is_file(), f"template/{HOOK_REL} is absent"
    assert kit.read_bytes() == (support.REPO_ROOT / HOOK_REL).read_bytes()


def test_mr4_the_kit_holds_the_table_byte_equal_to_gov_os_s_own():
    kit = support.TEMPLATE / TABLE_REL
    assert kit.is_file(), f"template/{TABLE_REL} is absent"
    assert kit.read_bytes() == (support.REPO_ROOT / TABLE_REL).read_bytes()


def test_mr4_the_kit_s_hook_source_has_one_pretooluse_entry_for_the_model_hook():
    """Red on the base: ``template/.rulesync/hooks.jsonc`` has no preToolUse entry."""
    data = support.jsonc((support.TEMPLATE / HOOKS_JSONC_REL).read_text(encoding="utf-8"))
    entries = [e for e in data["hooks"].get("preToolUse", []) if "agent_model.py" in e.get("command", "")]
    assert len(entries) == 1, f"preToolUse entries naming the hook: {entries}"
    assert entries[0].get("matcher") == MATCHER
    assert '$CLAUDE_PROJECT_DIR/.claude/hooks/agent_model.py' in entries[0]["command"]
    assert entries[0]["command"].startswith("python3 -I ")


def test_mr4_the_root_permission_source_holds_the_kit_s_two_denies_and_nothing_else():
    """Red on the base: the root file also spells the ``:*`` forms."""
    root = support.jsonc((support.REPO_ROOT / support.PERMS_REL).read_text(encoding="utf-8"))
    kit = support.jsonc((support.TEMPLATE / support.PERMS_REL).read_text(encoding="utf-8"))
    rules = {key: value for key, value in root.items() if key != "$schema"}
    assert rules == {"permission": {"bash": {"git push *": "deny", "sudo *": "deny"}}}, json.dumps(root)
    assert root == kit


def test_mr4_gov_os_s_own_settings_are_not_changed_by_this_change():
    """Guard (green on the base): ``.claude/settings.json`` equals the integration branch's."""
    base = subprocess.run(["git", "rev-parse", "--verify", "-q", "w2/integrate"], cwd=str(support.REPO_ROOT),
                          capture_output=True, text=True)
    if base.returncode != 0:
        pytest.skip("no w2/integrate ref here")
    done = subprocess.run(["git", "diff", "--quiet", "w2/integrate", "--", ".claude/settings.json"],
                          cwd=str(support.REPO_ROOT))
    assert done.returncode == 0, ".claude/settings.json differs from w2/integrate"


# --------------------------------------------------------------------------------------------------------------------
# A project adopted from the kit
# --------------------------------------------------------------------------------------------------------------------

def test_mr4_an_adopted_project_has_the_hook_byte_equal_and_the_table(adopted_at_b):
    """Red on the base: neither file is in the kit."""
    assert (adopted_at_b / HOOK_REL).read_bytes() == (support.REPO_ROOT / HOOK_REL).read_bytes()
    assert (adopted_at_b / TABLE_REL).read_bytes() == (support.REPO_ROOT / TABLE_REL).read_bytes()


def test_mr4_an_adopted_project_s_settings_hold_the_hook_line_once_and_default_mode(adopted_at_b):
    """Red on the base: no PreToolUse entry and no ``defaultMode``."""
    settings = support.read_settings(adopted_at_b)
    entries = _settings_hook_entries(settings)
    assert len(entries) == 1, f"PreToolUse entries naming the hook: {entries}"
    assert entries[0].get("matcher") == MATCHER
    assert json.dumps(settings).count("agent_model.py") == 1
    assert settings.get("permissions", {}).get("defaultMode") == "bypassPermissions"


def test_mr4_an_adopted_project_has_the_two_denies_and_no_edit_deny(adopted_at_b):
    """Red on the base only through the other MR-4 lines; the denies are the K1 lines, kept."""
    settings = support.read_settings(adopted_at_b)
    deny, _ = support.permission_lines(settings)
    assert DENY <= set(deny) and set(deny) <= DENY_ALL, deny
    assert not [line for line in deny if str(line).startswith("Edit(")], deny
    assert (adopted_at_b / HOOK_REL).is_file(), "the hook the settings run is not there"


def test_mr4_the_adopted_hook_refuses_a_non_sonnet_helper_with_exit_2(adopted_at_b):
    """Red on the base: the adopted project holds no hook file."""
    assert (adopted_at_b / HOOK_REL).is_file(), f"{HOOK_REL} is absent from the adopted project"
    for model in ("opus", "claude-opus-5-5", "haiku"):
        done = _hook_run(adopted_at_b, model)
        assert done.returncode == 2, f"{model}: exit {done.returncode}\n{done.stdout}\n{done.stderr}"
        assert done.stderr.strip() and "can't open file" not in done.stderr, f"no reason from the hook: {done.stderr}"


@pytest.mark.parametrize("model", ["sonnet", "claude-sonnet-5-5"])
def test_mr4_the_adopted_hook_lets_a_sonnet_helper_through_with_exit_0(adopted_at_b, model):
    done = _hook_run(adopted_at_b, model)
    assert done.returncode == 0, f"exit {done.returncode}\n{done.stdout}\n{done.stderr}"


def test_mr4_the_adopted_hook_writes_sonnet_into_a_spawn_with_no_model(adopted_at_b):
    done = _hook_run(adopted_at_b, None)
    assert done.returncode == 0, f"exit {done.returncode}\n{done.stderr}"
    out = json.loads(done.stdout)["hookSpecificOutput"]
    assert out["updatedInput"]["model"] == "sonnet"


def test_mr4_a_generation_in_a_scratch_repository_holds_the_hook_line_exactly_once_and_no_edit_deny(tmp_path, sandbox):
    """Failure line. Red on the base: no hook line at all."""
    project = support.template_project(tmp_path / "product")
    for _ in range(2):
        done = support.generate(project, sandbox)
        assert done.returncode == 0, done.describe()
    settings = support.read_settings(project)
    assert json.dumps(settings).count("agent_model.py") == 1, "the hook line is not there exactly once"
    deny, _ = support.permission_lines(settings)
    assert not [line for line in deny if str(line).startswith("Edit(")]
    assert settings.get("permissions", {}).get("defaultMode") == "bypassPermissions"


# --------------------------------------------------------------------------------------------------------------------
# gov update
# --------------------------------------------------------------------------------------------------------------------

def test_mr4_gov_update_replaces_a_2124_byte_stand_in_byte_for_byte_and_the_hook_line_stays_once(
        examin_013, tmp_path):
    """Red on the base: the update leaves the stand-in and adds no hook line."""
    assert len(STAND_IN) == 2124
    sandbox = support.sandbox_at(tmp_path / "sandbox")
    project = support.w216.clone_folder(examin_013, tmp_path / "product")
    support.write(project, HOOK_REL, "")
    (project / HOOK_REL).write_bytes(STAND_IN)
    support.w216.commit_all(project, "an older copy of the hook")
    first = support.update(project, sandbox)
    assert first.returncode == 0, first.describe()
    assert (project / HOOK_REL).read_bytes() == (support.REPO_ROOT / HOOK_REL).read_bytes()
    settings = support.read_settings(project)
    assert len(_settings_hook_entries(settings)) == 1 and json.dumps(settings).count("agent_model.py") == 1
    assert settings["permissions"].get("defaultMode") == "bypassPermissions"
    assert (project / TABLE_REL).read_bytes() == (support.REPO_ROOT / TABLE_REL).read_bytes()
    # Rewrite-Reason: DEC-1246 (3)(b): MR-4: a second `gov update` of the same release refuses by design; the hook line
    # being added once is shown by a regeneration after the update instead.
    done = support.generate(project, sandbox)
    assert done.returncode == 0, done.describe()
    assert json.dumps(support.read_settings(project)).count("agent_model.py") == 1
    assert (project / HOOK_REL).read_bytes() == (support.REPO_ROOT / HOOK_REL).read_bytes()
