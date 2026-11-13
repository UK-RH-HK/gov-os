"""S1: an engineer's Grep or Glob tool call that can reach its own ticket's acceptance folder is refused unless the
call excludes it, and the refusal names the folder and says how; the same calls with the exclusion are allowed.

The planted engineer is on DAEO-zz41 (WBS id ``WBS``); its folder is ``OWN`` (w2_141_support).
"""

from __future__ import annotations

import pytest

import w2_141_support as s

# Calls whose path and pattern can reach the planted ``s.OWN``.
REACHING = [
    s.grep("Grep with no path (the session's root)"),
    s.grep("Grep from '.'", path="."),
    s.grep("Grep from the root by its absolute path", path="{root}"),
    s.grep("Grep from tests/", path="tests"),
    s.grep("Grep from tests/acceptance/", path="tests/acceptance"),
    s.grep("Grep from the root, glob **/*.py", glob="**/*.py"),
    s.grep("Grep from the root, type py", type="py"),
    s.grep("Grep from the root, excluding another ticket's folder", glob=f"!{s.OTHER}/**"),
    s.glob_call("Glob **/*.py with no path", "**/*.py"),
    s.glob_call("Glob **/*.py from the root by its absolute path", "**/*.py", "{root}"),
    s.glob_call("Glob **/* from tests/", "**/*", "tests"),
    s.glob_call("Glob **/test_*.py from tests/acceptance/", "**/test_*.py", "tests/acceptance"),
    s.glob_call("Glob tests/** with no path", "tests/**"),
]

# The Grep calls above with the exclusion the refusal names.
EXCLUDED = [
    s.grep("Grep with no path, glob !tests/acceptance/W2-941/**", glob=s.GREP_EXCLUSION),
    s.grep("Grep from '.', glob !tests/acceptance/W2-941/**", path=".", glob=s.GREP_EXCLUSION),
    s.grep("Grep from the absolute root, glob !tests/acceptance/W2-941/**", path="{root}",
           glob=s.GREP_EXCLUSION),
    s.grep("Grep with no path, files_with_matches, glob !tests/acceptance/W2-941/**", glob=s.GREP_EXCLUSION,
           output_mode="files_with_matches"),
]

# The Glob tool takes no exclusion: a Glob call keeps the folder out by a path or pattern that cannot reach it.
GLOB_KEPT_OUT = [
    s.glob_call("Glob **/*.py from src/", "**/*.py", "src"),
    s.glob_call("Glob src/**/*.py with no path", "src/**/*.py"),
    s.glob_call("Glob **/* from another ticket's folder", "**/*", s.OTHER),
]


# One Grep and one Glob call from the root, for the edge cases.
FROM_ROOT = [REACHING[0], REACHING[8]]


@pytest.mark.parametrize("call", REACHING, ids=s.slug)
def test_s1_a_call_reaching_the_own_acceptance_folder_is_refused_saying_how(guard, call):
    s.assert_refused_saying_how(guard.ask(call), call)


@pytest.mark.parametrize("call", FROM_ROOT, ids=s.slug)
def test_s1_the_same_when_the_ticket_is_named_by_its_wbs_id(guard, call):
    s.assert_refused_saying_how(guard.ask(call, ticket=s.WBS), call, "(GOV_TICKET W2-941) ")


@pytest.mark.parametrize("call", FROM_ROOT, ids=s.slug)
def test_s1_the_same_for_an_engineer_subagent_of_an_orchestrator_session(guard, call):
    s.assert_refused_saying_how(guard.ask(call, role=s.ORCHESTRATOR, agent=s.ENGINEER), call,
                                "(engineer subagent) ")


@pytest.mark.parametrize("call", EXCLUDED, ids=s.slug)
def test_s1_the_grep_call_with_the_exclusion_is_allowed(guard, call):
    s.assert_allowed(guard.ask(call), call)


def test_s1_the_exclusion_is_taken_when_the_ticket_is_named_by_its_wbs_id(guard):
    call = EXCLUDED[0]
    s.assert_allowed(guard.ask(call, ticket=s.WBS), call, "(GOV_TICKET W2-941) ")


@pytest.mark.parametrize("call", GLOB_KEPT_OUT, ids=s.slug)
def test_s1_guard_a_glob_call_that_cannot_reach_the_folder_is_allowed(guard, call):
    s.assert_allowed(guard.ask(call), call)


def test_s1_guard_the_exclusion_does_not_open_a_call_aimed_inside_the_folder(guard):
    call = s.grep("Grep from tests/acceptance/W2-941/, glob !tests/acceptance/W2-941/**", path=s.OWN,
                  glob=s.GREP_EXCLUSION)
    s.assert_refused(guard.ask(call), call)
