"""W2-111 success-9's count case and failure-4's decisions (DEC-1187 (1); the CTO's interface, DEC-1157 (3)).

The product guard's PreToolUse hook, run as W1-02 runs it, in W1-02's fixture project with the two governance YAML
files the guard reads (``governance/project/held-out.yaml``, ``governance/project/path-map.yaml``). A probe on the
child's path (``w2_111_yaml_count.SITECUSTOMIZE``; it never imports or patches the guard's modules) reports the YAML
files the hook's processes open under ``governance/`` and every parse through yaml's public load API, put to its file.

Three behaviours (the ticket's paragraph "Interface for S9's count case"):

1. a call refused before the held-out check parses no YAML file;
2. a write or an edit, of any role, parses no ``path-map.yaml``;
3. every call parses each YAML file it opens at most once.

DEC-218 is kept: ``held-out.yaml`` is read on every call past the guard's early refusals (a broken ``held-out.yaml``
stops every call), so its one parse is needed, never waste: behaviour 3 asserts it is opened on each such call, and
one case asserts a broken file still refuses every call. Each case also asserts the call's decision, as today, so a
fast refusal cannot pass it.
"""

from __future__ import annotations

import pytest

import w2_111_yaml_count as counting

guard = counting.guard
E, T, A = guard.ENGINEER, guard.TEST_DESIGNER, guard.AUDITOR
TICKET = guard.TICKET_ID
HELD_OUT = counting.HELD_OUT_REL
PATH_MAP = counting.PATH_MAP_REL


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    w = counting.CountWorld(tmp_path_factory.mktemp("w2-111-count"))
    seen = counting.probe_works(w)
    assert seen.opened == [HELD_OUT] and seen.parses == {HELD_OUT: 1}, (
        "the count probe is not live in a child with the hook's environment (a direct yaml.safe_load of "
        f"held-out.yaml should be one open and one parse): {seen.describe()}")
    return w


def _p(world, rel):
    return str(world.project / rel)


def _who(role):
    return role or "no-role"


# --------------------------------------------------------------------------------------------------------------------
# 1. A call refused before the held-out check parses no YAML file
# --------------------------------------------------------------------------------------------------------------------

EARLY = [("Bash-sandbox-off", role) for role in (None, E, T, A)] + [("Read-NUL-path", role) for role in (None, E)]


def _early_input(kind):
    if kind == "Bash-sandbox-off":
        return "Bash", {"command": "ls", "description": "W2-111 S9", "dangerouslyDisableSandbox": True}
    return "Read", {"file_path": "README.md\x00x"}


@pytest.mark.parametrize("kind,role", EARLY, ids=[f"{k}-{_who(r)}" for k, r in EARLY])
def test_a_call_refused_before_the_held_out_check_parses_no_yaml_file(world, kind, role):
    tool, tool_input = _early_input(kind)
    result, count = world.call(tool, tool_input, role=role, ticket=TICKET if role else None)
    assert result.decision == "deny", f"{kind} ({_who(role)}) was not refused, as it is today: {result.describe()}"
    if kind == "Bash-sandbox-off":
        assert "dangerouslyDisableSandbox" in result.stdout, (
            f"the refusal's reason is not today's (dangerouslyDisableSandbox): {result.describe()}")
    assert count.total == 0 and not count.opened, (
        f"{kind} ({_who(role)}), refused before the held-out check, parsed or opened YAML: {count.describe()}")


# --------------------------------------------------------------------------------------------------------------------
# 2. A write or an edit, of any role, parses no path-map.yaml
# --------------------------------------------------------------------------------------------------------------------

WRITES = [  # (role, target, decision today)
    (None, "docs/notes.md", "deny"),
    (E, "src/gov/guard/decide.py", "allow"),
    (E, f"tests/acceptance/{guard.TICKET_WBS_ID}/test_fixture.py", "deny"),
    (T, f"tests/acceptance/{guard.TICKET_WBS_ID}/test_fixture.py", "allow"),
    (A, "src/gov/guard/decide.py", "deny"),
]
WRITE_CASES = [(tool, *w) for tool in ("Write", "Edit") for w in WRITES]
WRITE_IDS = [f"{tool}-{_who(r)}-{'acceptance' if 'acceptance' in t else t.split('/')[0]}"
             for tool, r, t, _ in WRITE_CASES]


@pytest.mark.parametrize("tool,role,target,decision", WRITE_CASES, ids=WRITE_IDS)
def test_a_write_or_edit_of_any_role_parses_no_path_map(world, tool, role, target, decision):
    result, count = world.call(tool, guard.edit_tool_input(tool, _p(world, target)), role=role,
                               ticket=TICKET if role else None)
    assert result.decision == decision, (
        f"{tool} of {target} ({_who(role)}) was not decided {decision}, as today: {result.describe()}")
    assert PATH_MAP not in count.parses, (
        f"{tool} of {target} ({_who(role)}) parsed path-map.yaml: {count.describe()}")
    if PATH_MAP in count.opened:
        assert "<other>" not in count.parses, (
            f"{tool} of {target} ({_who(role)}) opened path-map.yaml and parsed text the probe cannot place: "
            f"{count.describe()}")


# --------------------------------------------------------------------------------------------------------------------
# 3. Every call parses each YAML file it opens at most once; held-out.yaml is read on each (DEC-218)
# --------------------------------------------------------------------------------------------------------------------

def _call_input(world, tool):
    if tool == "Read":
        return {"file_path": _p(world, "README.md")}
    if tool in ("Write", "Edit"):
        return guard.edit_tool_input(tool, _p(world, "src/gov/guard/decide.py"))
    if tool == "Glob":
        return {"pattern": "**/*.py", "path": _p(world, "src")}
    if tool == "Grep":
        return {"pattern": "VALUE", "path": _p(world, "src")}
    return guard.bash_tool_input("ls src/gov/guard")


EVERY = [  # (tool, role, decision today)
    ("Read", E, "allow"), ("Write", E, "allow"), ("Edit", E, "allow"),
    ("Glob", E, "allow"), ("Grep", E, "allow"), ("Bash", E, "allow"),
    ("Read", T, "allow"), ("Bash", T, "allow"),
    ("Read", None, "allow"), ("Write", None, "deny"), ("Edit", None, "deny"),
    ("Glob", None, "allow"), ("Grep", None, "allow"), ("Bash", None, "allow"),
]


@pytest.mark.parametrize("tool,role,decision", EVERY, ids=[f"{t}-{_who(r)}" for t, r, _ in EVERY])
def test_each_yaml_file_a_call_opens_is_parsed_at_most_once(world, tool, role, decision):
    result, count = world.call(tool, _call_input(world, tool), role=role, ticket=TICKET if role else None)
    assert result.decision == decision, f"{tool} ({_who(role)}) was not decided {decision}, as today: {result.describe()}"
    twice = {f: n for f, n in count.parses.items() if f.startswith("governance/") and n > 1}
    assert not twice, f"{tool} ({_who(role)}) parsed a governance YAML file more than once: {count.describe()}"
    assert HELD_OUT in count.opened, (
        f"{tool} ({_who(role)}) did not read held-out.yaml: DEC-218 has it read on every call past the early "
        f"refusals (its one parse is needed): {count.describe()}")


@pytest.mark.parametrize("tool,role", [("Read", None), ("Read", E), ("Write", E), ("Glob", E), ("Bash", E)],
                         ids=["Read-no-role", "Read-engineer", "Write-engineer", "Glob-engineer", "Bash-engineer"])
def test_a_broken_held_out_yaml_still_stops_every_call(hook, tmp_path_factory, tool, role):
    w = counting.CountWorld(tmp_path_factory.mktemp("w2-111-count-broken"))
    (w.project / HELD_OUT).write_text("held_out_paths: [unclosed\n", encoding="utf-8")
    result, count = w.call(tool, _call_input(w, tool), role=role, ticket=TICKET if role else None)
    assert result.decision == "deny", (
        f"{tool} ({_who(role)}) was let through with a broken held-out.yaml (DEC-218: it stops every call): "
        f"{result.describe()}; {count.describe()}")
