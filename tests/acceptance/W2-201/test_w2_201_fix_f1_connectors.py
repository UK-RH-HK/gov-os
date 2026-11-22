"""W2-201 fix F1: no session loads the owner's claude.ai connectors; each gets only its role's MCP tools.

Launch side (the kit's settings key is a W2-17 case, ``tests/acceptance/W2-17/test_w2_17_fix_connectors_key.py``, the
doctor's drift line a W2-22 case). On W2-184's fixture project and the stand-in CLI, which here also copies what each
``--mcp-config`` value holds when the session starts (the value is inline JSON or the path of a file).

* Every session (each worker role, a lead as a feature, ``--fix`` or ``--chore``) is started with ``--strict-mcp-config``
  once, ``--mcp-config`` built from the role's MCP list (``{"mcpServers": {<name>: ...}}``, no server when the list is
  empty, as it is for every role today) and ``ENABLE_CLAUDEAI_MCP_SERVERS=false`` in the CLI process environment.
* The role's list is one line of the role file, ``- **MCP tools:** <name>, <name>`` (the form of its ``Skills`` line); the
  servers of ``--mcp-config`` are exactly those names.
* ``--mcp-config`` after ``--`` is no longer refused outright: a value whose servers are all in the role's list is
  accepted (the session's servers stay within the list); any other value (a server outside the list, any value for a role
  with no list, a path) is refused with ``LAUNCH_REFUSED`` naming ``--mcp-config``.
"""

from __future__ import annotations

import json

import pytest

import w2_201_support as k
import w2_201_x_support as x

s, b = x.s, x.b
FIX_TK, READY_TK = "DAEO-ldfx", "DAEO-lrdy"
CALLER = {"GOV_TICKET": x.CALLER_TICKET}
WORKERS = [k.ENGINEER, k.TEST_DESIGNER, k.AUDITOR, k.PRODUCT_SPEC, k.RESEARCH]
LISTED = ("notes-server", "search-server")
MCP_LINE = "- **MCP tools:** " + ", ".join(LISTED)
ENV_NAME = "ENABLE_CLAUDEAI_MCP_SERVERS"

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
def mcp_cli(sandbox, cli):
    """The stand-in CLI, patched to record what each ``--mcp-config`` file holds (key ``mcp`` of its call record)."""
    text = cli.path.read_text(encoding="utf-8")
    head = 'record = {"argv0"'
    assert head in text, "fixture: the stand-in CLI changed its record line"
    cli.path.write_text(text.replace(head, _SNIPPET + 'record = {"mcp": mcp_seen, "argv0"', 1), encoding="utf-8")
    return cli


def _servers(result):
    """One set of server names per ``--mcp-config`` value the session received."""
    found = []
    for entry in result.session()["mcp"]:
        data = json.loads(entry.get("text") or entry["value"])
        assert isinstance(data, dict) and isinstance(data.get("mcpServers"), dict), (
            f"--mcp-config {entry['value'][:200]!r} is not {{'mcpServers': {{...}}}}")
        found.append(set(data["mcpServers"]))
    return found


def _assert_session_connectors(result, want):
    """strict once, the servers of every --mcp-config together are ``want``, the environment says false."""
    assert result.args.count("--strict-mcp-config") == 1, f"--strict-mcp-config is not once: {result.args}"
    configs = _servers(result)
    assert configs, f"the session got no --mcp-config: {result.args}"
    assert set().union(*configs) == set(want), f"the session's MCP servers are {configs}, not {sorted(want)}"
    env = result.session()["env"]
    assert env.get(ENV_NAME) == "false", f"the CLI process environment has {ENV_NAME}={env.get(ENV_NAME)!r}"


def _plan(project):
    x.ticket(project, x.ENGINEER, "C2", "closed", tk=FIX_TK)
    s.ticket(project, x.ENGINEER, "C2", tk=READY_TK)
    b.write(project / x.READY_REL, f"# batch 1\nW2-201-ready {READY_TK} brief.md log.json\n")
    x.commit(project, "the leads' tickets and the ready list")


@pytest.mark.parametrize("role", WORKERS)
def test_a_worker_has_strict_mcp_an_empty_config_and_the_connectors_off(project, launch, mcp_cli, role):
    """Red on the base: no ``--mcp-config`` and no ``ENABLE_CLAUDEAI_MCP_SERVERS``."""
    tk = s.ticket(project, role, "C2")
    result = launch(role, tk)
    b.assert_launched(result)
    _assert_session_connectors(result, ())


@pytest.mark.parametrize("kind", ["feature", "fix", "chore"])
@pytest.mark.parametrize("role", x.LEAD_ROLES)
def test_a_lead_has_strict_mcp_an_empty_config_and_the_connectors_off(sandbox, project, mcp_cli, role, kind):
    _plan(project)
    head = {"feature": (READY_TK,), "fix": (FIX_TK, "--fix", x.FIX_LINE), "chore": ("--chore", x.CHORE_LINE)}[kind]
    result = x.launched(x.launch(sandbox, mcp_cli, role, *head, extra_env=CALLER))
    _assert_session_connectors(result, ())


def test_a_role_with_mcp_tools_listed_gets_exactly_them(project, launch, mcp_cli):
    s.write_role(project, k.ENGINEER, lines=[MCP_LINE])
    tk = s.ticket(project, k.ENGINEER, "C2")
    result = launch(k.ENGINEER, tk)
    b.assert_launched(result)
    _assert_session_connectors(result, LISTED)


def test_the_list_of_one_role_does_not_reach_another(project, launch, mcp_cli):
    s.write_role(project, k.ENGINEER, lines=[MCP_LINE])
    tk = s.ticket(project, k.TEST_DESIGNER, "C2")
    result = launch(k.TEST_DESIGNER, tk)
    b.assert_launched(result)
    _assert_session_connectors(result, ())


def _inline(*names):
    return json.dumps({"mcpServers": {name: {"command": "true"} for name in names}})


def test_a_caller_config_inside_the_roles_list_is_accepted(project, launch, mcp_cli):
    """Red on the base: ``--mcp-config`` after ``--`` is refused whatever it holds."""
    s.write_role(project, k.ENGINEER, lines=[MCP_LINE])
    tk = s.ticket(project, k.ENGINEER, "C2")
    result = launch(k.ENGINEER, tk, "--mcp-config", _inline(LISTED[0]))
    b.assert_launched(result)
    union = set().union(*_servers(result))
    assert LISTED[0] in union and union <= set(LISTED), f"the session's servers are {union}"
    assert result.args.count("--strict-mcp-config") == 1
    assert result.session()["env"].get(ENV_NAME) == "false"


def test_a_caller_config_outside_the_roles_list_is_refused(project, launch, mcp_cli):
    s.write_role(project, k.ENGINEER, lines=[MCP_LINE])
    tk = s.ticket(project, k.ENGINEER, "C2")
    s.refused(launch(k.ENGINEER, tk, "--mcp-config", _inline(LISTED[0], "other-server")), "--mcp-config", "other-server")


def test_a_caller_config_for_a_role_with_no_list_is_refused(project, launch, mcp_cli):
    """Guard (green on the base, the refusal stays): an empty list allows nothing."""
    tk = s.ticket(project, k.ENGINEER, "C2")
    s.refused(launch(k.ENGINEER, tk, "--mcp-config", _inline("any-server")), "--mcp-config")
    s.refused(launch(k.ENGINEER, tk, "--mcp-config", "servers.json"), "--mcp-config")
