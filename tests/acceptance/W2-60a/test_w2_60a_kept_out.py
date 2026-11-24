"""W2-60a, KPI success 6 -- no connectors, no user-level agents or skills, no model-side memory (stand-in cases).

KPI success 6 [DEC-826 Q5, lens E R6]: "A launched session loads no
connectors, no user-level agents or skills and no model-side memory: a test
home planted with one of each shows none in the session's start; what the CLI
gives no switch for is a package naming it, never passed silently". KPI
failure 1: "a user-level agent, skill or connector, or model-side memory".

Every test's home is planted (``w2_60a_support.plant_home``) with a connector in
``~/.claude.json``, a user-level agent and skill, a model-side memory file, a
user-level ``CLAUDE.md`` and rule, and a user settings file that sets a model,
an effort, a subagent model, a compaction threshold, an ``env`` variable, a
hook and permission rules; the project carries a connector in ``.mcp.json``.
Of the user settings, only the ``permissions.ask`` and ``permissions.deny``
strings may reach the session (round 2, review 1's F2:
``test_w2_60a_user_permissions.py``). A session needs the caller's own sign-in, which
lives in the real home, so a planted home can only be used with the stand-in:
these cases show the switches the design measured (Behaviour 4) on the line, in
the settings and in the record. That a real session's start then shows none of
them is the live file's (``test_w2_60a_live_sessions.py``), in the caller's
real home. The packages that name what the CLI gives no switch for are
checked in ``test_w2_60a_documents.py``.
"""

from __future__ import annotations

import json

import pytest

# Rewrite-Reason: F1 / DEC-1232 (6): no session loads the owner's claude.ai connectors; each gets only its role's MCP tools.
# The line keeps --strict-mcp-config and now also carries one --mcp-config whose config holds no server (the list is empty
# for every role): the connector assertion below asserts exactly that instead of "no --mcp-config".
# Rewrite-Reason: DEC-1225 / DEC-1236 (2): F19, no launch takes a model the rubric does not give; the fixture roles' default
# models were Opus and are Sonnet now, so the model a case expects the launch to carry is Sonnet.
import w2_60a_support as s


_SNIPPET = '''mcp_seen = []
for value in values("--mcp-config"):
    entry = {"value": value}
    try:
        with open(value, encoding="utf-8") as handle:
            entry["text"] = handle.read()
    except OSError:
        pass
    mcp_seen.append(entry)
'''


@pytest.fixture()
def cli(sandbox):
    """The stand-in CLI, patched to copy what each ``--mcp-config`` file holds when the session starts."""
    stand_in = s.install_stand_in_cli(sandbox)
    text = stand_in.path.read_text(encoding="utf-8")
    head = 'record = {"argv0"'
    assert head in text, "fixture: the stand-in CLI changed its record line"
    stand_in.path.write_text(text.replace(head, _SNIPPET + 'record = {"mcp": mcp_seen, "argv0"', 1), encoding="utf-8")
    return stand_in


def test_the_line_keeps_connectors_and_user_level_settings_out(launch):
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    assert s.occurrences(result.args, "--strict-mcp-config") == 1, (
        f"the line does not carry --strict-mcp-config once: {result.args}")
    assert s.occurrences(result.args, "--mcp-config") == 1, f"the line does not carry --mcp-config once: {result.args}"
    entry = result.session()["mcp"][0]
    config = json.loads(entry.get("text") or entry["value"])
    assert config.get("mcpServers") == {}, f"the line hands the session a connector: {config}"
    assert result.values("--setting-sources") == ["project,local"], (
        f"the line does not keep the user's settings out with --setting-sources project,local: {result.args}")


def test_the_settings_turn_model_side_memory_off(launch):
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    assert result.settings().get("autoMemoryEnabled") is False, (
        f"the settings do not set autoMemoryEnabled false: {sorted(result.settings())}")


def test_the_record_names_what_is_kept_out(launch):
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    assert result.record().get("kept_out") == s.KEPT_OUT, f"kept_out: {result.record().get('kept_out')!r}"


def test_nothing_of_the_test_home_but_the_user_s_ask_and_deny_rules_reaches_the_session_s_start(launch):
    """Round 2 (review 1, F2): the user settings' ``permissions.ask`` and ``permissions.deny`` strings are the only
    part of the test home the settings may carry (``test_w2_60a_user_permissions.py``)."""
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    assert s.USER_WORD not in result.appended()["text"], "text planted in the test home was appended to the start"
    settings = result.settings()
    permissions = dict(settings.get("permissions") or {})
    for key, planted in (("ask", s.USER_ASK), ("deny", s.USER_DENY)):
        if key in permissions:
            permissions[key] = [rule for rule in permissions[key] if rule not in planted]
    rest = json.dumps({**settings, "permissions": permissions})
    assert s.USER_WORD not in rest, (
        "the test home's text reached the settings in more than the user settings' ask and deny rules")
    names = [entry.get("name") for entry in result.record().get("skills") or [] if isinstance(entry, dict)]
    assert s.USER_SKILL not in names, "the test home's user-level skill is recorded as one the session can load"


def test_the_session_s_values_come_from_the_repository_not_the_user_s_settings(launch):
    """Lens F recommendation 1: the planted user settings say Haiku, effort low, subagent Haiku."""
    result = launch(s.ENGINEER)
    s.assert_launched(result)
    assert (result.one("--model"), result.one("--effort")) == s.DEFAULTS[s.ENGINEER], (
        f"the line's model and effort are not the role's: {result.args}")
    assert result.env_block().get("CLAUDE_CODE_SUBAGENT_MODEL") == s.SONNET, (
        "the subagent model is not the role's model")
