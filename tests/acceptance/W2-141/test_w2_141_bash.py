"""S2: an engineer's recursive Bash search (grep -r / -R, rg, ag, ack, find with a reading action or piped into a
reader) started at a folder that holds its own ticket's acceptance folder is refused unless the command excludes it
(grep --exclude-dir, rg -g '!...', find -prune / -not -path); the refusal names the folder and says how.

The planted engineer is on DAEO-zz41 (WBS id W2-941); its folder is tests/acceptance/W2-941/ (w2_141_support).
"""

from __future__ import annotations

import pytest

import w2_141_support as s

W = s.WORD

REACHING = [
    s.bash(f"grep -rn {W} .", "grep"),
    s.bash(f"grep -rn {W}", "grep"),
    s.bash(f"grep -Rn {W} tests/", "grep"),
    s.bash(f"grep -rn {W} tests/acceptance", "grep"),
    s.bash(f"grep -rln {W} --include=*.py .", "grep"),
    s.bash(f"grep -rn {W} {{root}}", "grep"),
    # Another ticket's folder kept out, not the own one.
    s.bash(f"grep -rn {W} --exclude-dir={s.OTHER_WBS} .", "grep"),
    # GNU grep matches --exclude-dir against a folder's base name when it recurses: a path keeps nothing out (D-1).
    s.bash(f"grep -rn {W} --exclude-dir={s.OWN} .", "grep"),
    s.bash(f"rg -n {W}", "rg"),
    s.bash(f"rg {W} tests", "rg"),
    s.bash(f"rg -n {W} -g '*.py'", "rg"),
    s.bash(f"rg -n {W} -g '!{s.OTHER}/**'", "rg"),
    s.bash(f"ag {W} .", "ag"),
    s.bash(f"ag {W}", "ag"),
    s.bash(f"ack {W} .", "ack"),
    s.bash(f"ack {W}", "ack"),
    s.bash("find . -name '*.py' -exec cat {} +", "find"),
    s.bash(f"find . -type f -exec grep -n {W} {{}} +", "find"),
    s.bash("find tests -type f -exec cat {} \\;", "find"),
    s.bash(f"find . -type f | xargs grep -n {W}", "find"),
    s.bash("find . -name '*.py' -print0 | xargs -0 cat", "find"),
]

EXCLUDED = [
    s.bash(f"grep -rn {W} {s.GREP_DIR_EXCLUSION} ."),
    s.bash(f"grep -rn {s.GREP_DIR_EXCLUSION} {W} tests/"),
    s.bash(f"rg -n {W} -g '!{s.OWN}/**'"),
    s.bash(f"find . -path ./{s.OWN} -prune -o -type f -exec grep -n {W} {{}} +"),
    s.bash(f"find . -type f -not -path './{s.OWN}/*' -exec grep -n {W} {{}} +"),
    s.bash(f"find . -path ./{s.OWN} -prune -o -type f -print | xargs grep -n {W}"),
]


@pytest.mark.parametrize("call", REACHING, ids=s.slug)
def test_s2_a_recursive_search_reaching_the_own_acceptance_folder_is_refused_saying_how(guard, call):
    s.assert_refused_saying_how(guard.ask(call), call)


@pytest.mark.parametrize("call", EXCLUDED, ids=s.slug)
def test_s2_the_search_with_the_exclusion_is_allowed(guard, call):
    s.assert_allowed(guard.ask(call), call)


def test_s2_the_same_when_the_ticket_is_named_by_its_wbs_id(guard):
    refused, allowed = REACHING[0], EXCLUDED[0]
    s.assert_refused_saying_how(guard.ask(refused, ticket=s.WBS), refused, "(GOV_TICKET W2-941) ")
    s.assert_allowed(guard.ask(allowed, ticket=s.WBS), allowed, "(GOV_TICKET W2-941) ")
