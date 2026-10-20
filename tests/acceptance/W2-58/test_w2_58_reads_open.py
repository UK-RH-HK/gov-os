"""W2-58, item 1 -- the reads Policy 2 opened are open for every role (KPI success 4).

KPI success 4: "The listing and search refusals over governance/ and .claude/
(DEC-508) are gone: a search that starts at the repository root or
governance/project/ is no longer refused for the protected files' sake; the
held-out list file's names are readable and the held-out material's contents
refused; the settings file's reads follow Policy 2; secrets stay refused
[DEC-820 (a), (b), DEC-857 item 3]". DEC-821 item 3: "The listing refusals
DEC-508 named are removed, with DEC-525's and DEC-557's refusals narrowed to
Policy 2 (b)".

KPI failure: "no write rule widens".

The project here has no ``w2/integrate`` branch, so the test designer has no
base and (c) refuses it nothing (item 4); the engineer's searches that would
take in its own ticket's acceptance folder are item 3's, not here. The project
holds stand-in secrets (``.env`` and others): a search that starts above one is
not refused for its sake (DEC-820 (a), item 2).
"""

from __future__ import annotations

import pytest

import w2_58_support as s

EVERY_ROLE = s.ROLES
# Roles whose root searches no part of (c) concerns in this project (the engineer's take in T's tests: item 3).
ROOT_SEARCHERS = tuple(role for role in s.ROLES if role != s.ENGINEER)


def _file_reads(world):
    held, settings = world.path(s.HELD_OUT_LIST_REL), world.path(s.SETTINGS_REL)
    return [
        s.read(held),
        s.bash(f"cat {s.HELD_OUT_LIST_REL}"),
        s.bash(f"grep -n {s.HELD_OUT_KEY} {s.HELD_OUT_LIST_REL}"),
        s.grep(path=held, pattern=s.HELD_OUT_KEY),
        s.read(settings),
        s.bash(f"cat {s.SETTINGS_REL}"),
        s.bash(f"grep -n PreToolUse {s.SETTINGS_REL}"),
        s.grep(path=settings, pattern="PreToolUse"),
    ]


FILE_READ_IDS = ("Read-held-out-list", "cat-held-out-list", "grep-held-out-list", "Grep-held-out-list",
                 "Read-settings", "cat-settings", "grep-settings", "Grep-settings")


def _named_searches(world):
    """Searches and listings of governance/, governance/project/ and .claude/ (the refusals of 2026-10-19 and 20)."""
    return [
        s.bash("ls governance/project/"),
        s.bash("ls governance/"),
        s.bash("ls -la .claude/"),
        s.glob_call("governance/project/*"),
        s.glob_call("*", path=world.path(".claude")),
        s.grep(path=world.path("governance/project")),
        s.grep(path=world.path("governance")),
        s.grep(path=world.path(".claude"), pattern="hooks"),
        s.bash("grep -rn 'governance/project' src/"),
        s.bash(f"git grep -n {s.HELD_OUT_KEY} -- 'governance/project/*.yaml'"),
        s.bash("grep -rn PreToolUse .claude/"),
        s.bash("find governance -name '*.yaml'"),
    ]


NAMED_IDS = ("ls-governance-project", "ls-governance", "ls-claude", "Glob-governance-project",
             "Glob-in-claude", "Grep-governance-project", "Grep-governance", "Grep-claude",
             "grep-r-pattern-names-the-folder", "git-grep-governance-project-yaml", "grep-r-claude",
             "find-governance")


def _root_searches(world):
    """Searches and listings that start at the repository root."""
    return [
        s.grep(),
        s.grep(path=world.project),
        s.bash(f"grep -r {s.WORD} ."),
        s.bash(f"grep -rn {s.WORD}"),
        s.bash(f"rg {s.WORD}"),
        s.bash(f"git grep -n {s.WORD}"),
        s.bash("find . -name 'notes.md'"),
        s.glob_call("**/*.md"),
    ]


ROOT_IDS = ("Grep-no-path", "Grep-root-path", "grep-r-dot", "grep-rn-no-path", "rg", "git-grep", "find-dot-name",
            "Glob-everything-md")


@pytest.mark.parametrize("index", range(len(FILE_READ_IDS)), ids=FILE_READ_IDS)
@pytest.mark.parametrize("role", EVERY_ROLE)
def test_the_held_out_list_and_the_settings_file_are_readable(open_world, role, index):
    """DEC-820 (b): the held-out list holds names, not contents; DEC-857 item 3: the settings file follows Policy 2."""
    call = _file_reads(open_world)[index]
    s.assert_allowed(open_world.ask(call, role), call, f"{role}: ")


@pytest.mark.parametrize("index", range(len(NAMED_IDS)), ids=NAMED_IDS)
@pytest.mark.parametrize("role", EVERY_ROLE)
def test_searches_and_listings_of_governance_and_claude_are_open(open_world, role, index):
    """DEC-508's listing refusals are gone (DEC-820, DEC-821 item 3)."""
    call = _named_searches(open_world)[index]
    s.assert_allowed(open_world.ask(call, role), call, f"{role}: ")


@pytest.mark.parametrize("index", range(len(ROOT_IDS)), ids=ROOT_IDS)
@pytest.mark.parametrize("role", ROOT_SEARCHERS)
def test_searches_from_the_repository_root_are_open(open_world, role, index):
    """DEC-557's root-search refusal is narrowed away (DEC-821 item 3); the stand-in secrets do not refuse it."""
    call = _root_searches(open_world)[index]
    s.assert_allowed(open_world.ask(call, role), call, f"{role}: ")


# --------------------------------------------------------------------------
# No write rule widens
# --------------------------------------------------------------------------

def _writes(world):
    settings, held = world.path(s.SETTINGS_REL), world.path(s.HELD_OUT_LIST_REL)
    return [
        s.write_call(settings),
        s.edit_call(settings),
        s.write_call(held),
        s.edit_call(held),
        s.bash(f"echo '{{}}' > {s.SETTINGS_REL}"),
        s.bash(f"sed -i 's/a/b/' {s.HELD_OUT_LIST_REL}"),
    ]


WRITE_IDS = ("Write-settings", "Edit-settings", "Write-held-out-list", "Edit-held-out-list", "redirect-settings",
             "sed-i-held-out-list")
# The roles whose tickets' allowed_paths name neither file.
NON_WRITERS = (s.ENGINEER, s.TEST_DESIGNER, s.AUDITOR, s.PRODUCT_SPEC, s.RESEARCH)


@pytest.mark.parametrize("index", range(len(WRITE_IDS)), ids=WRITE_IDS)
@pytest.mark.parametrize("role", NON_WRITERS)
def test_a_role_that_may_not_write_either_file_still_may_not(open_world, role, index):
    """KPI failure: no write rule widens."""
    call = _writes(open_world)[index]
    s.assert_refused(open_world.ask(call, role), call, f"{role}: ")
    assert (open_world.path(s.SETTINGS_REL).read_text(encoding="utf-8") == s.settings_text())


@pytest.mark.parametrize("role", EVERY_ROLE)
def test_the_hook_listing_helper_still_lists_the_hook_events(open_world, role):
    """DEC-525's helper stays: ``python3 -m gov.guard.hooks`` is allowed and prints the registered events."""
    call = s.bash("python3 -m gov.guard.hooks")
    s.assert_allowed(open_world.ask(call, role), call, f"{role}: ")
    run = s.run_in_project(open_world.sandbox, open_world.project, ["python3", "-m", "gov.guard.hooks"], role,
                           s.TICKET_OF[role].tk)
    assert run.returncode == 0 and "PreToolUse" in run.stdout, f"the helper did not list the events\n{run.describe()}"
