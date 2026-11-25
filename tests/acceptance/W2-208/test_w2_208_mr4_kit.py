"""Fix MR-4 (DEC-1246 (3)(b); INTEGRATION-PLAN row 4-2): the kit holds the model hook, the table and ``defaultMode``;
the root permission source matches the kit's two deny lines.

Read: the kit's files, a project adopted at the current kit (``adopted_at_b``: ``copier copy`` and ``gov adapters
generate``), ``gov update`` on a copy holding an older hook, and the hook run as a subprocess on an event.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

import w2_208_support as support

HOOK_REL = ".claude/hooks/agent_model.py"
KERNEL_HOOK_REL = "governance/kernel/hooks/agent_model.py"   # Rewrite-Reason: DEC-1246 (3)(b): MR-4: the kit holds the hook with the kernel hooks
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


def _hook_command(project):
    entries = _settings_hook_entries(support.read_settings(project))
    assert len(entries) == 1, f"PreToolUse entries naming the hook: {entries}"
    return entries[0]["hooks"][0]["command"] if "hooks" in entries[0] else entries[0]["command"]


def _hook_run(project, model, tasks=("DAEO-aaaa",), kind="engineer"):
    """The settings' own hook command, through `sh -c` as the harness runs it, with a stand-in `gov` at
    `<HOME>/.local/bin/gov` whose first line names the interpreter (the kit's line is the pin-interpreter wrapper:
    it needs a gov and exits 0 when none is found).

    Rewrite-Reason: DEC-1246 (3)(b): MR-4.
    """
    import tempfile
    tool_input = {"description": "helper", "prompt": "Do the work.\n\n" + "\n".join(f"Task: {t}" for t in tasks),
                  "subagent_type": kind}
    if model is not None:
        tool_input["model"] = model
    event = {"session_id": "00000000-0000-4000-8000-000000000208", "hook_event_name": "PreToolUse",
             "tool_name": "Agent", "tool_input": tool_input}
    command = _hook_command(project)
    with tempfile.TemporaryDirectory(prefix="w208") as home:
        local_bin = Path(home) / ".local" / "bin"
        local_bin.mkdir(parents=True)
        pin = local_bin / "gov"
        pin.write_text(f"#!{sys.executable}\nraise SystemExit(0)\n", encoding="utf-8")
        pin.chmod(0o755)
        env = {"PATH": "/usr/bin:/bin", "HOME": home, "LANG": "C.UTF-8", "CLAUDE_PROJECT_DIR": str(project)}
        return subprocess.run(["sh", "-c", command], input=json.dumps(event), env=env, capture_output=True,
                              text=True, cwd=str(project), timeout=60)


# --------------------------------------------------------------------------------------------------------------------
# The kit's own files
# --------------------------------------------------------------------------------------------------------------------

def test_mr4_the_kit_holds_the_hook_file_byte_equal_to_gov_os_s_own():
    """Red on the base: the kit holds no model hook."""
    # Rewrite-Reason: DEC-1246 (3)(b): MR-4: the kit's copy is a kernel hook, `template/governance/kernel/hooks/agent_model.py`; the adopted
    # project's `.claude/hooks/agent_model.py` is written from it by `gov adapters generate` and `gov update`.
    kit = support.TEMPLATE / KERNEL_HOOK_REL
    assert kit.is_file(), f"template/{KERNEL_HOOK_REL} is absent"
    assert kit.read_bytes() == (support.REPO_ROOT / HOOK_REL).read_bytes()


def test_mr4_the_kit_holds_the_table_byte_equal_to_gov_os_s_own():
    kit = support.TEMPLATE / TABLE_REL
    assert kit.is_file(), f"template/{TABLE_REL} is absent"
    assert kit.read_bytes() == (support.REPO_ROOT / TABLE_REL).read_bytes()


def test_mr4_the_kit_s_hook_source_has_one_pretooluse_entry_for_the_model_hook():
    """Red on the base: ``template/.rulesync/hooks.jsonc`` has no preToolUse entry."""
    # Rewrite-Reason: DEC-1246 (3)(b): MR-4: the line is the pin-interpreter wrapper naming the kernel hook (no `python3 -I` line).
    data = support.jsonc((support.TEMPLATE / HOOKS_JSONC_REL).read_text(encoding="utf-8"))
    entries = [e for e in data["hooks"].get("preToolUse", []) if "agent_model.py" in e.get("command", "")]
    assert len(entries) == 1, f"preToolUse entries naming the hook: {entries}"
    assert entries[0].get("matcher") == MATCHER
    command = entries[0]["command"]
    assert command.count("governance/kernel/hooks/agent_model.py") == 1 and command.count("agent_model.py") == 1
    assert not command.startswith("python3 -I"), "the line is not the wrapper that starts the pin's interpreter"


def test_mr4_the_root_permission_source_holds_the_kit_s_two_denies_and_no_legacy_edit_deny():
    """The root's bash denies include the kit's two (`git push *`, `sudo *`) and nothing else but their `:*` forms and
    the owner's interim eval-root entries; no legacy `Edit(.tickets...)`-style deny.

    Rewrite-Reason: DEC-1246 (3)(b): MR-4, with DEC-1249 (2): the integration branch's root file also carries the
    owner's interim denies (read and edit of two eval roots, `*examin-eval*` for bash), which are allowed here.
    """
    root = support.jsonc((support.REPO_ROOT / support.PERMS_REL).read_text(encoding="utf-8"))
    kit = support.jsonc((support.TEMPLATE / support.PERMS_REL).read_text(encoding="utf-8"))
    rules = {key: value for key, value in root.items() if key != "$schema"}
    assert set(rules) == {"permission"} and set(rules["permission"]) <= {"bash", "read", "edit"}, json.dumps(root)
    bash = rules["permission"]["bash"]
    for line, verdict in kit["permission"]["bash"].items():
        assert bash.get(line) == verdict == "deny", f"the kit's {line!r} is not denied at the root: {bash}"
    allowed_bash = set(kit["permission"]["bash"]) | {"git push:*", "sudo:*", "*examin-eval*"}   # DEC-1249 (2): the last
    assert set(bash) <= allowed_bash and set(bash.values()) == {"deny"}, bash
    for kind in ("read", "edit"):   # DEC-1249 (2): the interim eval-root entries only
        entries = rules["permission"].get(kind, {})
        assert all("eval" in path and verdict == "deny" for path, verdict in entries.items()), entries
    assert ".tickets" not in json.dumps(root), "a legacy `.tickets` edit deny is back at the root"


def test_mr4_gov_os_s_own_settings_are_not_changed_by_this_change():
    """Guard (green on the base): ``.claude/settings.json`` equals the integration branch's at the point this branch
    left it (the merge base: the integration branch moves on without this change).

    Rewrite-Reason: DEC-1246 (3)(b): MR-4: the comparison was against the moving tip of ``w2/integrate``.
    """
    base = subprocess.run(["git", "merge-base", "w2/integrate", "HEAD"], cwd=str(support.REPO_ROOT),
                          capture_output=True, text=True)
    if base.returncode != 0:
        pytest.skip("no w2/integrate ref here")
    done = subprocess.run(["git", "diff", "--quiet", base.stdout.strip(), "--", ".claude/settings.json"],
                          cwd=str(support.REPO_ROOT))
    assert done.returncode == 0, ".claude/settings.json differs from the merge base with w2/integrate"


# --------------------------------------------------------------------------------------------------------------------
# A project adopted from the kit
# --------------------------------------------------------------------------------------------------------------------

def test_mr4_an_adopted_project_has_the_hook_byte_equal_and_the_table(adopted_at_b):
    """Red on the base: neither file is in the kit."""
    assert (adopted_at_b / KERNEL_HOOK_REL).read_bytes() == (support.REPO_ROOT / HOOK_REL).read_bytes()
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


@pytest.mark.parametrize("kind,written", [("engineer", "claude-sonnet-5-5"), ("Explore", "sonnet")],
                         ids=["a-type-with-a-table-row", "a-type-without-a-row"])
def test_mr4_the_adopted_hook_writes_the_rows_model_into_a_spawn_with_no_model(adopted_at_b, kind, written):
    # Rewrite-Reason: DEC-1246 (3)(b): MR-4, ruling: the rule wins. The hook writes the table row's model for a
    # subagent_type that has a row, and `sonnet` only where there is no usable row.
    done = _hook_run(adopted_at_b, None, kind=kind)
    assert done.returncode == 0, f"exit {done.returncode}\n{done.stderr}"
    out = json.loads(done.stdout)["hookSpecificOutput"]
    assert out["updatedInput"]["model"] == written


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
    # Rewrite-Reason: DEC-1246 (3)(b): MR-4: the older copy is the adopted one at `.claude/hooks/` (as EXAMIN holds it);
    # a file already at the kernel path is the project's own and `gov update` keeps it, so none is planted there.
    support.w216.commit_all(project, "an older copy of the hook")
    first = support.update(project, sandbox)
    assert first.returncode == 0, first.describe()
    own = (support.REPO_ROOT / HOOK_REL).read_bytes()
    state = {"kernel copy replaced": (project / KERNEL_HOOK_REL).read_bytes() == own,
             "adopted copy replaced": (project / HOOK_REL).read_bytes() == own}
    assert all(state.values()), f"{state}\n{first.stdout[-1500:]}"
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
