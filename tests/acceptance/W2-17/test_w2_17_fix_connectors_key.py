"""Fix F1 (a) (owner W2-17 for the update merge): the kit's settings carry ``"disableClaudeAiConnectors": true`` and the
adopted repository's ``.claude/settings.json`` gets that key, by ``gov adapters generate`` at adoption and by ``gov
update``; an existing settings file keeps all its other keys.

* The kit's own file ``template/governance/kernel/settings.json`` holds the key as ``true`` (and its permission denies).
* A project adopted at A (``adopted``: copier copy, ``gov adapters generate``) has the key in its settings.
* A project whose settings lack the key (an older kit's) and hold its own keys (``model``, a ``permissions.allow`` entry,
  an ``env`` variable, a hook of its own) is committed, ``gov update B`` runs: the settings then hold the key as ``true``
  and every planted key, entry and hook as planted.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import w2_17_support as support

KEY = "disableClaudeAiConnectors"
OWN = {
    "model": "claude-sonnet-5-5",
    "permissions": {"allow": ["Bash(make test:*)"]},
    "env": {"W2_17_OWN": "1"},
}
OWN_HOOK = {"matcher": "Bash", "hooks": [{"type": "command", "command": 'python3 -I "$CLAUDE_PROJECT_DIR/tools/own.py"'}]}


def _load(project):
    return json.loads((Path(project) / ".claude" / "settings.json").read_text(encoding="utf-8"))


def test_the_kits_settings_carry_the_key():
    """Red on the base: the key is not in the kit's settings."""
    data = json.loads((support.REPO_ROOT / "template/governance/kernel/settings.json").read_text(encoding="utf-8"))
    assert data.get(KEY) is True, f"the kit's settings hold {KEY} = {data.get(KEY)!r}, not true"
    assert data["permissions"]["deny"], "the kit's permission denies are kept"


def test_a_freshly_adopted_repository_has_the_key(adopted):
    """Red on the base: adoption (copier copy, ``gov adapters generate``) writes settings without it."""
    assert _load(adopted).get(KEY) is True


@pytest.fixture(scope="module")
def updated_with_own_keys(adopted, tmp_path_factory):
    base = tmp_path_factory.mktemp("w2-17-connectors")
    project = support.copy_project(adopted, base / "product")
    sandbox = support.make_sandbox(base / "sandbox")
    planted = _load(project)
    planted.pop(KEY, None)
    planted["model"] = OWN["model"]
    planted["env"] = {**planted.get("env", {}), **OWN["env"]}
    permissions = planted.setdefault("permissions", {})
    permissions["allow"] = [*OWN["permissions"]["allow"], *permissions.get("allow", [])]
    planted.setdefault("hooks", {}).setdefault("PostToolUse", []).insert(0, OWN_HOOK)
    (project / ".claude" / "settings.json").write_text(json.dumps(planted, indent=2) + "\n", encoding="utf-8")
    support.commit_all(project, "W2-17 F1: settings without the connectors key, with the project's own keys")
    assert not support.porcelain_paths(project), "the planted project is not clean (fixture, not the fix)"
    assert KEY not in _load(project)
    return project, planted, support.update(project, sandbox)


def test_gov_update_adds_the_key_to_settings_that_lack_it(updated_with_own_keys):
    """Red on the base."""
    project, _, run = updated_with_own_keys
    assert run.returncode == 0, f"`gov update --json` did not exit 0\n{run.describe()}"
    assert _load(project).get(KEY) is True


def test_gov_update_keeps_every_other_key_of_the_settings(updated_with_own_keys):
    """Guard (green on the base): the project's own keys, entries and hook stay as planted."""
    project, planted, run = updated_with_own_keys
    assert run.returncode == 0, f"`gov update --json` did not exit 0\n{run.describe()}"
    after = _load(project)
    assert after["model"] == planted["model"]
    assert after["env"].get("W2_17_OWN") == "1"
    assert "Bash(make test:*)" in after["permissions"]["allow"]
    assert OWN_HOOK in after["hooks"]["PostToolUse"]
    assert set(planted["permissions"].get("deny", [])) <= set(after["permissions"].get("deny", []))
