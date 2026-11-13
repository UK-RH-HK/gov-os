"""W2-141, round 2: the hook side (DEC-1093 (2), DEC-1102). S1, S2, S3 and the failure lines, through the live G-14
hook module ``role_reads`` (the staged copy ``docs/changes/W2-141-hook/role_reads.py`` when the tree holds it, else
``.claude/hooks/role_reads.py``), called as ``.claude/hooks/pretooluse.py`` calls it (``w2_141_hook_support``).

Round 1 (``test_w2_141_grep_glob.py``, ``test_w2_141_bash.py``, ``test_w2_141_unchanged.py``) drives the guard's
decide function; these cases drive the hook W2-138's search went through. The oracle is the KPI lines; which planted
grep and find commands really reach the folder, and which exclusions really keep it out, was checked by running them
in a copy of the planted project (README, "Round 2").
"""

from __future__ import annotations

import re

import pytest

import w2_141_hook_support as hs
import w2_141_support as s
from w2_141_support import (AUDITOR, DESIGNER, ENGINEER, GREP_DIR_EXCLUSION, GREP_EXCLUSION, ORCHESTRATOR, OTHER,
                            OTHER_TICKET, OTHER_WBS, OWN, PRODUCT_SPEC, RESEARCH, TICKET, TICKET_LEAD, WBS, WORD,
                            bash, glob_call, grep, read, slug)


@pytest.fixture(scope="module")
def hook(tmp_path_factory):
    """The hook over the planted project (a git repository with no commits), with a temporary HOME and GOV_ROLE,
    GOV_TICKET and CLAUDE_PROJECT_DIR cleared; the module is loaded once HOME is set."""
    project = s.make_project(tmp_path_factory.mktemp("w2-141-hook"))
    hs.git_init(project.root)
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("HOME", str(project.home))
        for name in ("GOV_ROLE", "GOV_TICKET", "CLAUDE_PROJECT_DIR"):
            mp.delenv(name, raising=False)
        yield hs.HookGuard(project, hs.load_hook(hs.tree_under_test()))


# The exclusion forms a hook refusal names, as whole words (a hook refusal also names role_paths and the path map, so
# the bare word "path" or "-g" inside another word is not taken as saying how).
def _word(form):
    return re.compile(r"(?<![\w./-])" + re.escape(form) + r"(?![\w-])")


HOOK_HOW = {kind: tuple(_word(f) for f in forms) for kind, forms in s.HOW.items()}


def assert_refused_saying_how(hook, result, call, who=""):
    who = hook.label() + who
    s.assert_refused(result, call, who)
    assert OWN in result.reason, f"{who}{call} was refused, but the reason does not name {OWN}/: {result.describe()}"
    assert any(p.search(result.reason) for p in HOOK_HOW[call.kind]), (
        f"{who}{call} was refused, but the reason does not say how to exclude {OWN}/ "
        f"(one of {s.HOW[call.kind]}): {result.describe()}")


def assert_allowed(hook, result, call, who=""):
    s.assert_allowed(result, call, hook.label() + who)


def assert_refused(hook, result, call, who=""):
    s.assert_refused(result, call, hook.label() + who)


# ---------------------------------------------------------------------------------------------------------------
# S1: the Grep and Glob tools
# ---------------------------------------------------------------------------------------------------------------

GREP_REACHING = [
    grep("Grep with no path"),
    grep("Grep from .", path="."),
    grep("Grep from the absolute root", path="{root}"),
    grep("Grep from tests/", path="tests/"),
    grep("Grep from tests/acceptance", path="tests/acceptance"),
    grep("Grep from the absolute tests/acceptance/", path="{root}/tests/acceptance/"),
    grep("Grep glob **/*.py, no path", glob="**/*.py"),
    grep("Grep type py, no path", type="py"),
    grep("Grep with another ticket's folder excluded", glob=f"!{OTHER}/**"),
]
GLOB_REACHING = [
    glob_call("Glob **/*.py, no path", "**/*.py"),
    glob_call("Glob **/*.py from the absolute root", "**/*.py", "{root}"),
    glob_call("Glob **/* from tests", "**/*", "tests"),
    glob_call("Glob **/test_*.py from tests/acceptance", "**/test_*.py", "tests/acceptance"),
    glob_call("Glob tests/**", "tests/**"),
]


@pytest.mark.parametrize("call", GREP_REACHING, ids=slug)
def test_s1_hook_a_grep_reaching_the_own_acceptance_folder_is_refused_saying_how(hook, call):
    assert_refused_saying_how(hook, hook.ask(call), call)


@pytest.mark.parametrize("call", GLOB_REACHING, ids=slug)
def test_s1_hook_a_glob_reaching_the_own_acceptance_folder_is_refused_saying_how(hook, call):
    assert_refused_saying_how(hook, hook.ask(call), call)


@pytest.mark.parametrize("call", [GREP_REACHING[0], GLOB_REACHING[0]], ids=slug)
def test_s1_hook_the_same_when_the_ticket_is_named_by_its_wbs_id(hook, call):
    assert_refused_saying_how(hook, hook.ask(call, ticket=WBS), call, f"(GOV_TICKET {WBS}) ")


@pytest.mark.parametrize("call", [GREP_REACHING[0], GLOB_REACHING[0]], ids=slug)
def test_s1_hook_the_same_for_an_engineer_subagent_of_an_orchestrator_session(hook, call):
    assert_refused_saying_how(hook, hook.ask(call, role=ORCHESTRATOR, agent=ENGINEER), call,
                              "(an engineer subagent) ")


GREP_EXCLUDED = [
    grep("Grep with the exclusion glob, no path", glob=GREP_EXCLUSION),
    grep("Grep with the exclusion glob from .", path=".", glob=GREP_EXCLUSION),
    grep("Grep with the exclusion glob from the absolute root", path="{root}", glob=GREP_EXCLUSION),
    grep("Grep with the exclusion glob, names only", glob=GREP_EXCLUSION, output_mode="files_with_matches"),
]


@pytest.mark.parametrize("call", GREP_EXCLUDED, ids=slug)
def test_s1_hook_guard_the_grep_with_the_exclusion_is_allowed(hook, call):
    assert_allowed(hook, hook.ask(call), call)
    assert_allowed(hook, hook.ask(call, ticket=WBS), call, f"(GOV_TICKET {WBS}) ")


def test_s1_hook_guard_the_exclusion_does_not_open_a_call_aimed_inside_the_folder(hook):
    call = grep("Grep from the own folder with the exclusion glob", path=f"{OWN}/", glob=GREP_EXCLUSION)
    assert_refused(hook, hook.ask(call), call)


# ---------------------------------------------------------------------------------------------------------------
# S2: recursive Bash searches
# ---------------------------------------------------------------------------------------------------------------

BASH_REACHING = [
    bash(f"grep -rn {WORD} .", "grep"),
    bash(f"grep -rn {WORD}", "grep"),
    bash(f"grep -R {WORD} tests/", "grep"),
    bash(f"grep -rn {WORD} tests/acceptance", "grep"),
    bash(f"grep -rn {WORD} {{root}}", "grep"),
    bash(f"grep -rn --include=*.py {WORD} .", "grep"),
    bash(f"grep -rn --exclude-dir={OTHER_WBS} {WORD} .", "grep"),
    bash(f"grep -rn --exclude-dir={OWN} {WORD} .", "grep"),  # the path form excludes nothing (D-1)
    bash(f"grep -rn {WORD} . | head -n 50", "grep"),
    bash(f"cd tests && grep -rn {WORD} .", "grep"),
    bash(f"rg -n {WORD}", "rg"),
    bash(f"rg {WORD} tests", "rg"),
    bash(f"rg -g '*.py' {WORD}", "rg"),
    bash(f"rg -g '!{OTHER}/**' {WORD}", "rg"),
    bash(f"ag {WORD}", "ag"),
    bash(f"ag {WORD} .", "ag"),
    bash(f"ack {WORD}", "ack"),
    bash(f"ack {WORD} .", "ack"),
    bash("find . -type f -exec cat {} +", "find"),
    bash(f"find . -name '*.py' -exec grep -n {WORD} {{}} +", "find"),
    bash(f"find tests -type f -exec grep -Hn {WORD} {{}} \\;", "find"),
    bash(f"find . -type f | xargs grep -n {WORD}", "find"),
    bash("find . -type f -print0 | xargs -0 cat", "find"),
]


@pytest.mark.parametrize("call", BASH_REACHING, ids=slug)
def test_s2_hook_a_recursive_search_reaching_the_own_acceptance_folder_is_refused_saying_how(hook, call):
    assert_refused_saying_how(hook, hook.ask(call), call)


def test_s2_hook_the_same_when_the_ticket_is_named_by_its_wbs_id(hook):
    call = BASH_REACHING[0]
    assert_refused_saying_how(hook, hook.ask(call, ticket=WBS), call, f"(GOV_TICKET {WBS}) ")


BASH_EXCLUDED = [
    bash(f"grep -rn {WORD} {GREP_DIR_EXCLUSION} ."),
    bash(f"grep -rn {GREP_DIR_EXCLUSION} {WORD} tests/"),
    bash(f"grep -rn --exclude-dir {WBS} {WORD} ."),
    bash(f"grep -rn {GREP_DIR_EXCLUSION} {WORD} {{root}}"),
    bash(f"rg -n {WORD} -g '!{OWN}/**'"),
    bash(f"find . -path ./{OWN} -prune -o -type f -exec grep -n {WORD} {{}} +"),
    bash(f"find . -type f -not -path './{OWN}/*' -exec grep -n {WORD} {{}} +"),
    bash(f"find . -type f ! -path './{OWN}/*' -exec cat {{}} +"),
    bash(f"find . -path ./{OWN} -prune -o -type f -print | xargs grep -n {WORD}"),
]


@pytest.mark.parametrize("call", BASH_EXCLUDED, ids=slug)
def test_s2_hook_guard_the_search_with_the_exclusion_is_allowed(hook, call):
    assert_allowed(hook, hook.ask(call), call)


# ---------------------------------------------------------------------------------------------------------------
# S3: nothing else changes
# ---------------------------------------------------------------------------------------------------------------

CANNOT_REACH = [
    grep("Grep from src", path="src"),
    grep("Grep glob src/**/*.py, no path", glob="src/**/*.py"),
    grep("Grep from another ticket's folder", path=OTHER),
    grep("Grep for the folder's name, from src", path="src", **{"pattern": OWN}),
    glob_call("Glob **/*.py from src", "**/*.py", "src"),
    glob_call("Glob src/**/*.py", "src/**/*.py"),
    glob_call("Glob **/* from another ticket's folder", "**/*", OTHER),
    bash(f"grep -rn {OWN} src/"),  # a grep for the tests' names by pattern (G-14)
    bash("grep -rn test_feature src/"),
    bash(f"grep -rn {WORD} src"),
    bash(f"grep -rn {WORD} {OTHER}"),
    bash(f"rg -n {WORD} src"),
    bash(f"find src -type f -exec grep -n {WORD} {{}} +"),
    bash("find . -name '*.py'"),  # names only, no reader
    bash("find tests -type f"),
    bash("ls -R tests"),
    bash(f"ls {OWN} && pytest -q {OWN}"),
    bash("git log --stat -n 3"),
    bash(f"grep -n {WORD} README.md"),
    read(f"{{root}}/{OTHER}/test_other.py"),
    bash(f"cat {OTHER}/test_other.py"),
    read("{root}/README.md"),
]


@pytest.mark.parametrize("call", CANNOT_REACH, ids=slug)
def test_s3_hook_guard_an_engineer_search_that_cannot_reach_its_folder_is_allowed(hook, call):
    assert_allowed(hook, hook.ask(call), call)


OTHER_ROLES = [ORCHESTRATOR, AUDITOR, DESIGNER, PRODUCT_SPEC, TICKET_LEAD, RESEARCH]
BROAD = [GREP_REACHING[0], GLOB_REACHING[0], BASH_REACHING[0], BASH_REACHING[10], BASH_REACHING[14],
         BASH_REACHING[18], read(f"{{root}}/{OWN}/test_feature.py"), bash(f"cat {OWN}/README.md")]


@pytest.mark.parametrize("role", OTHER_ROLES)
def test_s3_hook_guard_other_roles_are_unaffected(hook, role):
    for call in BROAD:
        assert_allowed(hook, hook.ask(call, role=role), call, f"({role}) ")


def test_s3_hook_guard_another_ticket_s_engineer_reads_this_ticket_s_tests(hook):
    for call in (bash(f"grep -rn {WORD} {OWN}"), grep("Grep from W2-941's folder", path=OWN),
                 read(f"{{root}}/{OWN}/test_feature.py")):
        assert_allowed(hook, hook.ask(call, ticket=OTHER_TICKET), call, f"({OTHER_TICKET}'s engineer) ")


# G-14's existing cases (tests/unit/hooks/test_live_hook.py's G14_REFUSED and G14_PASSED for the engineer, on this
# planted project): a true read refused with the G-14 reason, the near misses let through.
G14_REFUSED = [
    read(f"{{root}}/{OWN}/test_feature.py"),
    bash(f"cat {OWN}/test_feature.py"),
    grep("Grep the own folder", path=f"{{root}}/{OWN}"),
    bash(f"cd tests/acceptance && sed -n 1,9p {WBS}/test_feature.py"),
    bash(f"grep -rn {WORD} {OWN}"),
]
G14_PASSED = [
    read(f"{{root}}/{OTHER}/test_other.py"),
    bash(f"ls {OWN} && pytest -q {OWN}"),
    bash(f"grep -rn {OWN} src/"),
    bash(f"python3 -c \"print(open('{OWN}/test_feature.py').read())\""),
]


@pytest.mark.parametrize("call", G14_REFUSED, ids=slug)
def test_s3_hook_guard_g14_true_reads_stay_refused_as_before(hook, call):
    result = hook.ask(call)
    assert_refused(hook, result, call)
    assert "role_paths.engineer.reads_denied" in result.reason and "DEC-1052 G-14" in result.reason, (
        f"{hook.label()}{call}: the G-14 reason changed: {result.describe()}")
    result = hook.ask(call, role=ORCHESTRATOR, agent=ENGINEER)
    assert_refused(hook, result, call, "(an engineer subagent) ")


@pytest.mark.parametrize("call", G14_PASSED, ids=slug)
def test_s3_hook_guard_g14_near_misses_still_pass(hook, call):
    assert_allowed(hook, hook.ask(call), call)
