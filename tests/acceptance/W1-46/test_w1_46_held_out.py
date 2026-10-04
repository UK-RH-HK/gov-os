"""W1-46 -- the held-out directory: one ``Read`` deny rule per configured path, and no launch without them.

KPI success 9 [CAP-49.b]: "The settings it builds carry the Read deny rule for
the held-out directory, whose path the launcher takes from
governance/project/held-out.yaml, the file W1-47 creates; from a launched
worker's Bash that directory looks empty; the test uses a stand-in directory,
never the qualification oracle".
KPI failure 9: "An acceptance test or implementation file of this ticket reads
or names the qualification oracle".

DEC-218: the launcher reads the key ``held_out_paths``, a list of absolute
paths, and builds one ``Read`` deny rule per path; "a missing key, or a broken
file, makes the guard fail closed", and the launcher refuses to launch on a
missing key, an empty list or a broken file.

Every project here has a ``held-out.yaml`` written by the test, with made-up
paths. "Looks empty from a launched worker's Bash" needs a session: see
``test_w1_46_live_sessions.py``.
"""

from __future__ import annotations

import pytest

import w1_46_support as support

w47 = support.w47

BROKEN = {
    "missing-key": "other_key:\n- /somewhere/else\n",
    "empty-list": f"{w47.CONFIG_KEY}: []\n",
    "key-without-a-value": f"{w47.CONFIG_KEY}:\n",
    "not-yaml": f"{w47.CONFIG_KEY}: [unclosed\n  - : :\n",
    "not-a-map": "- /somewhere/else\n",
    "empty-file": "",
}


@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_the_built_settings_carry_the_read_deny_rule_for_the_configured_path(launch, stand_in, role):
    built = launch(role).settings()
    assert w47.held_out_read_rules(built, str(stand_in)), (
        f"no Read deny rule of the built settings is built from the configured stand-in path; Read rules: "
        f"{support.deny_rules(built, 'Read')}"
    )


def test_there_is_one_read_deny_rule_per_configured_path(launch, project, sandbox, stand_in):
    """DEC-218: "one Read deny rule per path"."""
    second = w47.make_stand_in(sandbox.elsewhere / "second-stand-in")
    w47.configure_stand_in(project, stand_in, second)
    built = launch(support.RESEARCH).settings()
    for path in (stand_in, second):
        assert len(w47.held_out_read_rules(built, str(path))) == 1, (
            f"the built settings do not carry exactly one Read deny rule for {path}; Read rules: "
            f"{support.deny_rules(built, 'Read')}"
        )


def test_the_path_is_read_at_each_launch(launch, project, sandbox, stand_in):
    """The rule follows the file: a changed ``held-out.yaml`` changes the next launch's rule."""
    launch(support.ENGINEER).settings()
    moved = w47.make_stand_in(sandbox.elsewhere / "moved-stand-in")
    w47.configure_stand_in(project, moved)
    built = launch(support.ENGINEER).settings()
    assert w47.held_out_read_rules(built, str(moved)), "the second launch has no Read deny rule for the new path"
    assert not w47.held_out_read_rules(built, str(stand_in)), "the second launch still denies the path of the first"


@pytest.mark.parametrize("role", (support.ENGINEER, support.RESEARCH))
@pytest.mark.parametrize("name", sorted(BROKEN))
def test_the_launcher_refuses_to_launch_on_a_broken_held_out_file(launch, project, role, name):
    """DEC-218: a missing key, an empty list or a broken file. Non-zero exit, a named reason, no session."""
    w47.write_config(project, BROKEN[name])
    support.assert_refused(launch(role), "held-out", w47.CONFIG_KEY)


def test_no_file_of_this_ticket_names_a_held_out_path():
    """KPI failure 9. The committed list is read at run time, as in W1-47; no value is ever shown.

    The files: this suite, and what exists under the ticket's ``allowed_paths``.
    Holds before implementation.
    """
    configured = w47.load_configured()
    files = w47.files_matching((
        "tests/acceptance/W1-46/**/*", "src/gov/launch/**/*", "src/gov/cli/**/*", "src/gov/guard/**/*",
        "template/governance/kernel/launch/**/*", "template/governance/kernel/hooks/pretooluse*",
        "template/governance/kernel/roles/research*", ".claude/agents/research.md", support.ROSTER_REL,
        "tests/unit/launch/**/*", "tests/unit/guard/**/*",
    ))
    assert files, "no file of the ticket was found"
    naming = [str(path.relative_to(support.REPO_ROOT)) for path in w47.files_naming(files, configured.values)]
    if naming:
        pytest.fail(f"these files of the ticket name a held-out path (the path is not shown): {naming}", pytrace=False)
