"""W1-46 -- a key written twice in ``held-out.yaml`` or in the research allowlist (batch 3, after implementation).

Described behaviours E and F of the review after implementation (DEC-136).

A YAML mapping has each key once. A reader that keeps the last value of a key
written twice drops the first without a word.

**E, ``governance/project/held-out.yaml``.** KPI success 9 [CAP-49.b]: "The
settings it builds carry the Read deny rule for the held-out directory, whose
path the launcher takes from governance/project/held-out.yaml". DEC-218: "one
Read deny rule per path"; "a missing key, or a broken file, makes the guard
fail closed", and the launcher refuses on a missing key, an empty list or a
broken file. Tested as what every reading shares:

- two lists under the key: no session is started in which a path the file
  names has no ``Read`` rule (the launch is refused, or both paths are denied),
  and the guard does not let a Read of the directory named first through;
- a first value that DEC-218 refuses (an empty list, no value, one string, a
  relative path), followed by a valid list: the launch is refused, and the
  guard fails closed.

The guard's side is W1-47's line [CAP-49.c]; W1-47 is closed, the guard's files
are in this ticket's ``allowed_paths``, and the launcher and the guard read the
file the same way. Every path here is a stand-in directory the test made.

**F, ``governance/project/research-allowlist.yaml``** (DEC-241). A malformed
file refuses the launch (``test_w1_46_research_allowlist.py``). With the list's
key written twice: a first list with an entry the launcher refuses elsewhere,
followed by a valid list, refuses; two valid lists refuse, or the built
allowlist carries the hosts of both ("extends").

No session is started.
"""

from __future__ import annotations

import pytest
import yaml

import w1_46_support as support

w47 = support.w47
KEY = w47.CONFIG_KEY
ENGINEER, RESEARCH = support.ENGINEER, support.RESEARCH


def _twice(key, first, second):
    """A YAML text with ``key`` written twice: ``first`` is the YAML of the first value, ``second`` a list."""
    return f"{key}: {first}\n" + yaml.safe_dump({key: [str(item) for item in second]}, default_flow_style=False)


def _flow(items):
    return "[" + ", ".join(f'"{item}"' for item in items) + "]"


# --------------------------------------------------------------------------
# E: held-out.yaml
# --------------------------------------------------------------------------

@pytest.fixture()
def first(sandbox):
    """A second stand-in directory, the one the file names first."""
    return w47.make_stand_in(sandbox.elsewhere / "named-first-stand-in")


@pytest.mark.parametrize("role", (ENGINEER, RESEARCH))
def test_no_session_is_started_without_a_read_rule_for_a_path_named_under_a_repeated_key(launch, project, stand_in,
                                                                                         first, role):
    launch(role).session()
    w47.write_config(project, _twice(KEY, _flow([first]), [stand_in]))
    result = launch(role)
    if result.run.returncode != 0:
        support.assert_refused(result, "held-out", KEY)
        return
    built = result.settings()
    missing = [name for name, path in (("first", first), ("last", stand_in))
               if not w47.held_out_read_rules(built, str(path))]
    assert missing == [], (
        f"a session was started with no Read deny rule for the path the file names {missing} under the key written "
        "twice"
    )


def test_the_guard_does_not_let_a_read_of_the_directory_named_first_through(guard, project, stand_in, first):
    w47.write_config(project, _twice(KEY, _flow([first]), [stand_in]))
    for tool, tool_input in (("Read", {"file_path": f"{first}/answers.md"}),
                             ("Bash", w47.bash_input(f"ls {first}/cases"))):
        result = guard(tool, tool_input, ENGINEER)
        w47.assert_stopped(result, f"{tool} of the stand-in the file names first, with the key written twice")


BROKEN_FIRST = {
    "an-empty-list": "[]",
    "no-value": "",
    "one-string": "/srv/somewhere/stand-in",
    "a-relative-path": "[somewhere/stand-in]",
}


@pytest.mark.parametrize("name", sorted(BROKEN_FIRST))
def test_a_broken_first_value_is_not_hidden_from_the_launcher_by_a_valid_second_one(launch, project, stand_in, name):
    """DEC-218: an empty list, a key without a value or a value of another shape refuses the launch."""
    launch(ENGINEER).session()
    w47.write_config(project, _twice(KEY, BROKEN_FIRST[name], [stand_in]))
    support.assert_refused(launch(ENGINEER), "held-out", KEY)


@pytest.mark.parametrize("name", sorted(BROKEN_FIRST))
def test_a_broken_first_value_is_not_hidden_from_the_guard_by_a_valid_second_one(guard, project, stand_in, name):
    """DEC-218: the guard fails closed; an ordinary Read is stopped, as with the broken value alone."""
    w47.write_config(project, _twice(KEY, BROKEN_FIRST[name], [stand_in]))
    result = guard("Read", {"file_path": f"{project}/README.md"}, ENGINEER)
    w47.assert_stopped(result, f"Read with a {w47.CONFIG_REL} whose first {KEY} is broken ({name})")


# --------------------------------------------------------------------------
# F: research-allowlist.yaml
# --------------------------------------------------------------------------

@pytest.fixture()
def allowlist(project):
    """``(key, hosts)`` of the project's research allowlist; the test is skipped for a file with no key."""
    key = support.allowlist_key(project)
    if key is None:
        pytest.skip(f"{support.ALLOWLIST_REL} holds its list without a key: a key cannot be written twice")
    data = yaml.safe_load((project / support.ALLOWLIST_REL).read_text(encoding="utf-8"))
    return key, list(data[key])


MALFORMED_FIRST = {
    "an-entry-that-accepts-every-host": '["*"]',
    "an-entry-that-is-a-url": f'["https://{support.ADDED_HOST}/simple/"]',
    "an-entry-that-is-a-number": "[42]",
    "a-word-where-the-list-is": "github.com",
}


@pytest.mark.parametrize("name", sorted(MALFORMED_FIRST))
def test_a_malformed_first_list_is_not_hidden_by_a_valid_second_one(launch, project, allowlist, name):
    """Each first value refuses the launch when it stands alone (``test_w1_46_research_allowlist.py``)."""
    key, hosts = allowlist
    launch(RESEARCH).session()
    support.write(project, support.ALLOWLIST_REL, _twice(key, MALFORMED_FIRST[name], hosts))
    support.assert_refused(launch(RESEARCH), "allowlist")


def test_a_first_list_of_hosts_is_not_dropped_silently(launch, project, allowlist):
    """Refused, or both lists extend the kernel default: the owner's first list never disappears unseen."""
    key, hosts = allowlist
    launch(RESEARCH).session()
    support.write(project, support.ALLOWLIST_REL, _twice(key, _flow([support.ADDED_HOST]), hosts))
    result = launch(RESEARCH)
    if result.run.returncode != 0:
        support.assert_refused(result, "allowlist")
        return
    domains = support.allowed_domains(result.settings())
    assert support.ADDED_HOST in domains, (
        f"a session was started without the host of the first of two lists under '{key}': {domains}"
    )
