"""W1-47 -- the guard and a ``held-out.yaml`` that is missing, incomplete or broken (DEC-218).

KPI success 4: "the guard takes the path from governance/project/held-out.yaml".
DEC-218: the guard reads the key ``held_out_paths``, a list of absolute paths.
"A missing key, or a broken file, makes the guard fail closed. The owner repairs
it through the operator."

- **A file that exists and has no such key, or is broken** (not readable as
  YAML, or not the stated shape): the guard fails closed. Tested as: no call
  goes through. The hook answers with a deny decision, or with exit code 2,
  its report of its own failure (DEC-110); either stops the call.
- **A file that is missing altogether** is a reading, not an answer of the
  owner: there is no held-out rule and calls are decided as before. The fixture
  projects of W1-02...W1-45 have no such file and expect their calls to be
  allowed; those suites hold the guard to it.

Every file here is written by the test into a temporary project. No call is
ever made.
"""

from __future__ import annotations

import pytest

import w1_47_support as support

SOURCE_FILE = support.check_support.SOURCE_FILE

# name: the text of a held-out.yaml that exists and is not a list of absolute paths under ``held_out_paths``.
BROKEN = {
    "empty-file": "",
    "comment-only": "# the held-out paths\n",
    "another-key": "paths:\n- /srv/somewhere/held-out\n",
    "key-misspelt": "held_out_path:\n- /srv/somewhere/held-out\n",
    "not-yaml": "held_out_paths: [\n  - /srv/somewhere: {\n",
    "not-a-mapping": "- /srv/somewhere/held-out\n",
    "key-without-a-value": "held_out_paths:\n",
    "key-holds-one-string": "held_out_paths: /srv/somewhere/held-out\n",
    "key-holds-a-mapping": "held_out_paths:\n  first: /srv/somewhere/held-out\n",
    "list-holds-a-number": "held_out_paths:\n- 42\n",
    "list-holds-a-relative-path": "held_out_paths:\n- somewhere/held-out\n",
}
# Calls the guard lets through for these actors when there is no held-out.yaml at all.
CALLS = {
    "Read": ("Read", lambda project: {"file_path": f"{project}/README.md"}),
    "Grep": ("Grep", lambda project: {"pattern": "guard", "path": f"{project}/src"}),
    "Bash": ("Bash", lambda project: support.bash_input("ls -la")),
    "Write-inside-the-ticket-paths": ("Write", lambda project: support.write_input("Write",
                                                                                   f"{project}/{SOURCE_FILE}")),
}
ACTORS = (support.ORCHESTRATOR, support.ENGINEER)


@pytest.mark.parametrize("who", ACTORS)
@pytest.mark.parametrize("call", sorted(CALLS))
def test_without_the_configuration_file_there_is_no_held_out_rule(project, guard, call, who):
    """Reading: a missing ``held-out.yaml`` means no held-out rule; the earlier suites' fixtures have none."""
    assert not (project / support.CONFIG_REL).exists(), "the fixture project has a held-out.yaml of its own"
    tool_name, build = CALLS[call]
    result = guard(project, tool_name, build(project), support.EVERY_SESSION[who])
    support.assert_allowed(result, f"{call} by {who} in a project with no {support.CONFIG_REL}")


@pytest.mark.parametrize("who", ACTORS)
@pytest.mark.parametrize("call", sorted(CALLS))
@pytest.mark.parametrize("name", sorted(BROKEN))
def test_a_broken_configuration_makes_the_guard_fail_closed(project, guard, name, call, who):
    """DEC-218: a file with no ``held_out_paths`` key, or one that is not the stated shape, stops every call."""
    support.write_config(project, BROKEN[name])
    tool_name, build = CALLS[call]
    result = guard(project, tool_name, build(project), support.EVERY_SESSION[who])
    support.assert_stopped(result, f"{call} by {who} with a {support.CONFIG_REL} that is broken ({name})")


def test_a_broken_configuration_fails_closed_with_no_role(project, guard):
    """DEC-218: also for a session that declares no role, whose reads are otherwise open."""
    support.write_config(project, BROKEN["another-key"])
    result = guard(project, "Read", {"file_path": f"{project}/README.md"})
    support.assert_stopped(result, f"Read by a session with no role with a {support.CONFIG_REL} that has no key")


def test_a_broken_configuration_fails_closed_through_the_committed_settings(wired, live):
    """DEC-218: in this repository's wiring, through the commands its settings register."""
    support.write_config(wired, BROKEN["not-yaml"])
    result = live(wired, "Read", {"file_path": f"{wired}/README.md"}, support.ORCHESTRATOR)
    assert result.ran, f"the Read call reached no registered PreToolUse command: {result.describe()}"
    assert result.decision == "deny", (
        f"Read with a {support.CONFIG_REL} that is not YAML was let through by the registered commands: "
        f"{result.describe()}"
    )


def test_a_repaired_configuration_opens_the_guard_again(project, sandbox, guard):
    """DEC-218: "the owner repairs it": with a file of the stated shape the calls go through as before."""
    orchestrator = support.EVERY_SESSION[support.ORCHESTRATOR]
    support.write_config(project, BROKEN["key-holds-one-string"])
    result = guard(project, "Read", {"file_path": f"{project}/README.md"}, orchestrator)
    support.assert_stopped(result, f"Read with a {support.CONFIG_REL} whose key holds one string")
    support.configure_stand_in(project, support.make_stand_in(sandbox.tmpdir / "held-out-stand-in"))
    result = guard(project, "Read", {"file_path": f"{project}/README.md"}, orchestrator)
    support.assert_allowed(result, f"Read of another file once {support.CONFIG_REL} has the stated shape")
