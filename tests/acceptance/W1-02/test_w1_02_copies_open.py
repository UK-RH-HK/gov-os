"""W1-02 — what keeps working beside the copies (DEC-548, DP-4): green before and after.

DP-4 widens the rule to "any target whose path ends in either file's
project-relative path" and to the user-level settings file. It names targets,
not folders: another file of a copy's folder named alone, the rest of another
checkout, the files below the folder that holds the user-level settings file,
and a write to a copy are decided as they are today. ``git status`` and
``git diff --stat`` with no other option stay allowed on a copy as on the file
(DP-5).

Everything here is green before the change and stays green: these cases keep
the change from refusing more than DEC-548 says.
"""

from __future__ import annotations

import pytest

import w1_02_copies_support as batch
import w1_02_protected_support as protected
import w1_02_support as support

FILES = batch.FILES
SETTINGS = batch.SETTINGS
WIDEST = "orchestrator"
NOT_A_WRITER = "engineer-who-may-not-write-the-file"


@pytest.fixture(scope="module")
def world(hook, tmp_path_factory):
    return batch.make_world(tmp_path_factory.mktemp("copies-open"))


def _ask(world, site, name, asked, who=WIDEST):
    tool_name, template = asked
    if tool_name == "Bash":
        return batch.ask_bash(world, batch.fill(world, site, name, template), who)
    return batch.ask(world, tool_name, {key: batch.fill(world, site, name, value) for key, value in template.items()},
                     who)


# --------------------------------------------------------------------------
# Another file of the copy's folder, named alone
# --------------------------------------------------------------------------

NEIGHBOURS = [("sibling", name) for name in FILES] + [("nested", name) for name in FILES] + [("home", SETTINGS)]
NEIGHBOUR_FORMS = {
    "Read": ("Read", {"file_path": "{nabs}"}),
    "cat": ("Bash", "cat {nabs}"),
}


@pytest.mark.parametrize("site,name", NEIGHBOURS, ids=[f"{site}-{name}" for site, name in NEIGHBOURS])
@pytest.mark.parametrize("form", sorted(NEIGHBOUR_FORMS))
def test_another_file_of_a_copy_s_folder_named_alone_is_still_read(world, form, site, name):
    result = _ask(world, site, name, NEIGHBOUR_FORMS[form])
    protected.assert_allowed(result, f"{form} of another file in the folder of the copy of the stand-in {name} "
                                     f"at the site '{site}'")


# --------------------------------------------------------------------------
# The rest of another checkout, and the files below the user-level settings folder
# --------------------------------------------------------------------------

ELSEWHERE = {
    "Read-a-file-at-the-root-of-another-checkout": ("sibling", ("Read", {"file_path": "{root}/README.md"})),
    "cat-a-source-file-of-another-checkout": ("sibling", ("Bash", "cat {root}/src/app.py")),
    "Grep-a-source-folder-of-another-checkout": ("sibling", ("Grep", {"pattern": "VALUE", "path": "{root}/src"})),
    "listing-of-a-source-folder-of-another-checkout": ("sibling", ("Bash", "ls {root}/src")),
    "Read-a-file-below-the-user-level-settings-folder": ("home", ("Read",
                                                                  {"file_path": "{root}/" + batch.HOME_BELOW_REL})),
    "cat-a-file-below-the-user-level-settings-folder": ("home", ("Bash", "cat ~/" + batch.HOME_BELOW_REL)),
    "listing-of-a-folder-below-the-user-level-settings-folder": (
        "home", ("Bash", "ls ~/" + batch.HOME_BELOW_REL.rsplit("/", 1)[0])),
}


@pytest.mark.parametrize("case", sorted(ELSEWHERE))
def test_the_rest_of_a_copy_s_site_is_still_read(world, case):
    site, asked = ELSEWHERE[case]
    result = _ask(world, site, SETTINGS, asked)
    protected.assert_allowed(result, case)


# --------------------------------------------------------------------------
# A write to a copy is decided as today
# --------------------------------------------------------------------------

# (site, who) -> allowed today (found by running the hook on these very calls): a copy outside the project is
# outside every role's allow-list; a copy below template/ is the orchestrator's to write and not this engineer's.
WRITES_TODAY = {
    ("sibling", WIDEST): False,
    ("nested", WIDEST): True,
    ("nested", NOT_A_WRITER): False,
}


@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("site,who", sorted(WRITES_TODAY))
def test_a_plain_write_to_a_copy_is_decided_as_today(world, site, who, name):
    tool_input = support.edit_tool_input("Write", world.site(site).path(name))
    result = batch.ask(world, "Write", tool_input, who)
    batch.assert_as_today(result, WRITES_TODAY[(site, who)],
                          f"Write to the copy of the stand-in {name} at the site '{site}' by '{who}'")


def test_a_plain_write_to_the_user_level_settings_file_is_decided_as_today(world):
    result = _ask(world, "home", SETTINGS, ("Bash", "echo '{{}}' > ~/{rel}"))
    batch.assert_as_today(result, False, "an output redirect to the stand-in user-level settings file")


# --------------------------------------------------------------------------
# git status and git diff --stat on a copy
# --------------------------------------------------------------------------

GIT = {
    "status-of-a-copy-in-another-checkout": ("sibling", "git status {abs}"),
    "diff-stat-of-a-copy-in-another-checkout": ("sibling", "git diff --stat {abs}"),
    "diff-stat-of-a-copy-below-the-project-s-root": ("nested", "git diff --stat {here}"),
}


@pytest.mark.parametrize("name", FILES)
@pytest.mark.parametrize("case", sorted(GIT))
def test_git_status_and_diff_stat_stay_allowed_on_a_copy(world, case, name):
    site, command = GIT[case]
    result = _ask(world, site, name, ("Bash", command))
    protected.assert_allowed(result, f"{case} (the stand-in {name})")
