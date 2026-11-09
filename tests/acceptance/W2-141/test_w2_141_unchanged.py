"""S3 and the failure lines: nothing else is newly refused. An engineer's search that cannot reach its own acceptance
folder is allowed; other tickets' acceptance tests stay readable (DEC-963); the test designer, a reviewer (an
independent auditor), the orchestrator and the other roles are unaffected; a grep for the tests' names by pattern
only stays allowed; and what is refused today stays refused (G-14's cases, through the decide function).

Every case here is a green guard on w2/integrate.
"""

from __future__ import annotations

import pytest

import w2_141_support as s

W = s.WORD

# An engineer on DAEO-zz41 (W2-941): calls that cannot reach tests/acceptance/W2-941/.
ENGINEER_ALLOWED = [
    s.grep("Grep from src/", path="src"),
    s.grep("Grep from the root, glob src/**/*.py", glob="src/**/*.py"),
    s.grep("Grep from another ticket's folder", path=s.OTHER),
    s.grep("Grep for the folder's name by pattern, from src/", pattern=s.OWN, path="src"),
    s.glob_call("Glob **/*.py from src/", "**/*.py", "src"),
    s.glob_call("Glob src/**/*.py with no path", "src/**/*.py"),
    s.glob_call("Glob **/* from another ticket's folder", "**/*", s.OTHER),
    s.bash(f"grep -rn {s.OWN} src/app/"),
    s.bash(f"grep -rn {W} src/"),
    s.bash(f"rg {W} src"),
    s.bash(f"grep -rn {W} {s.OTHER}"),
    s.bash("find src -name '*.py' -exec cat {} +"),
    s.bash("find src -type f | xargs cat"),
    s.bash("find . -name '*.py'"),
    s.bash("ls tests/acceptance"),
    s.bash(f"grep -n {W} README.md"),
    s.bash(f"python3 -m pytest {s.OWN} -q"),
    s.read(f"{s.OTHER}/test_other.py"),
    s.read("README.md"),
]

# What is refused today stays refused (the first failure line): reads aimed at the folder.
ENGINEER_REFUSED = [
    s.read(f"{s.OWN}/README.md"),
    s.grep("Grep from tests/acceptance/W2-941/", path=s.OWN),
    s.bash(f"cat {s.OWN}/test_feature.py"),
    s.bash(f"grep -rn {W} {s.OWN}"),
]

# The broad searches S1 and S2 refuse an engineer: every other role makes them freely.
BROAD = [
    s.grep("Grep with no path (the session's root)"),
    s.grep("Grep from the root, glob **/*.py", glob="**/*.py"),
    s.glob_call("Glob **/*.py with no path", "**/*.py"),
    s.bash(f"grep -rn {W} ."),
    s.bash(f"rg -n {W}"),
    s.bash(f"ag {W} ."),
    s.bash(f"find . -type f -exec grep -n {W} {{}} +"),
    s.bash(f"find . -type f | xargs grep -n {W}"),
    s.read(f"{s.OWN}/README.md"),
]

OTHER_ROLES = [s.ORCHESTRATOR, s.AUDITOR, s.DESIGNER, s.PRODUCT_SPEC, s.TICKET_LEAD, s.RESEARCH]

# guard4_check.py's G-14 cases (DEC-1052), with this project's paths, as the decide function answers them:
# (label, role, call, decision). Its second case (a case revised for the ticket in another ticket's folder, linked by
# a Task: trailer) is the role_reads hook's, not the decide function's: it is not reproduced here (README, N-3).
G14 = [
    ("G-14 the engineer reads its own acceptance tests", s.ENGINEER, s.read(f"{s.OWN}/README.md"), "deny"),
    ("G-14 the engineer reads another ticket's tests", s.ENGINEER, s.read(f"{s.OTHER}/test_other.py"), "allow"),
    ("G-14 the engineer greps for the tests' name, a pattern not a read", s.ENGINEER,
     s.bash(f"grep -rn {s.OWN} {{root}}/src/app/"), "allow"),
    ("G-14 the orchestrator reads the acceptance tests", s.ORCHESTRATOR, s.read(f"{s.OWN}/README.md"), "allow"),
]


@pytest.mark.parametrize("call", ENGINEER_ALLOWED, ids=s.slug)
def test_s3_guard_an_engineer_search_that_cannot_reach_its_folder_is_allowed(guard, call):
    s.assert_allowed(guard.ask(call), call)


@pytest.mark.parametrize("call", ENGINEER_REFUSED, ids=s.slug)
def test_s3_guard_a_read_aimed_at_the_own_folder_stays_refused(guard, call):
    s.assert_refused(guard.ask(call), call)


@pytest.mark.parametrize("role", OTHER_ROLES)
def test_s3_guard_other_roles_are_unaffected(guard, role):
    refused = [f"{call}: {r.describe()}" for call in BROAD for r in [guard.ask(call, role=role)]
               if r.decision != "allow"]
    assert not refused, f"{role} on {s.TICKET} was refused: " + "; ".join(refused)


def test_s3_guard_another_ticket_s_engineer_reads_this_ticket_s_tests(guard):
    call = s.bash(f"grep -rn {W} {s.OWN}")
    s.assert_allowed(guard.ask(call, ticket=s.OTHER_TICKET), call, f"(engineer on {s.OTHER_TICKET}) ")


@pytest.mark.parametrize("case", G14, ids=lambda c: s.slug(s.Call("", {}, c[0])))
def test_s3_guard_g14_cases_answer_as_before(guard, case):
    label, role, call, want = case
    got = guard.ask(call, role=role)
    assert got.decision == want, f"{label}: want {want}, got {got.describe()}"
