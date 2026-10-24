"""W2-58, item 7 -- a guard error still fails closed.

KPI failure: "a guard error still fails closed". When the guard cannot work
out a refusal it owes, the call is refused, never allowed:

- a malformed ``evaluation_sets`` block (a set whose ``hidden`` is not a list)
  refuses the calls of the sessions it could concern, and ``gov launch``
  refuses to launch such a session;
- an engineer's or a test designer's ticket file that cannot be parsed refuses
  its reads under (c);
- a git failure while finding a test designer's changed files (with
  ``w2/integrate`` present: here T's branch shares no commit with it, so git
  finds no merge base) refuses its reads under (c).
"""

from __future__ import annotations

import pytest

import w2_58_support as s

TEST_FILE = f"{s.T.acceptance}/test_feature.py"
HIDDEN_FILE = "eval/memory/hidden/answers.yaml"


def _malformed_block():
    block = s.evaluation_block(roles=(s.RESEARCH,), tickets=(s.MEASURED.tk,))
    block[s.EVAL_SET]["hidden"] = "eval/memory/hidden/**"
    return block


@pytest.mark.parametrize("session", ("by-role", "by-ticket"))
def test_a_malformed_evaluation_block_refuses_the_calls_of_the_sessions_it_could_concern(sandbox, session):
    role, ticket = {"by-role": (s.RESEARCH, s.EXPERIMENT), "by-ticket": (s.ENGINEER, s.MEASURED)}[session]
    project = s.make_eval_project(sandbox, block=_malformed_block())
    world = s.World(sandbox, project)
    for call in (s.read(project / HIDDEN_FILE), s.bash(f"cat {HIDDEN_FILE}"), s.read(project / "README.md")):
        s.assert_refused(world.ask(call, role, ticket), call, f"{session}, malformed evaluation_sets: ")


def test_a_malformed_evaluation_block_refuses_the_launch(sandbox, cli):
    s.make_eval_project(sandbox, block=_malformed_block())
    result = s.launch(sandbox, cli, s.ENGINEER, s.MEASURED)
    assert result.run.returncode != 0 and not result.calls, (
        f"gov launch started a session under a malformed evaluation_sets block\n{result.describe()}")


BROKEN_TICKET = "---\nid: DAEO-zz58\nwbs_id: [unclosed\nrole: engineer\n---\n# broken\n"


def test_an_engineer_s_unparseable_ticket_file_refuses_its_reads_under_c(sandbox):
    project = s.make_project(sandbox, base=True)
    s.write(project / f".tickets/{s.T.tk}.md", BROKEN_TICKET)
    world = s.World(sandbox, project)
    for call in (s.read(project / TEST_FILE), s.bash(f"cat {TEST_FILE}")):
        s.assert_refused(world.ask(call, s.ENGINEER, s.T), call, "engineer, unparseable ticket file: ")


def test_a_test_designer_s_unparseable_ticket_file_refuses_its_reads_under_c(sandbox):
    project = s.make_project(sandbox, base=True)
    s.write(project / f".tickets/{s.T.tk}.md", BROKEN_TICKET)
    world = s.World(sandbox, project)
    for call in (s.read(project / "src/app/main.py"), s.bash("cat src/app/main.py")):
        s.assert_refused(world.ask(call, s.TEST_DESIGNER, s.T), call, "test designer, unparseable ticket file: ")


def test_a_git_failure_finding_the_changed_files_refuses_the_test_designer_s_reads(sandbox):
    project = s.make_project(sandbox, base=True, orphan=True)
    done = s.run_in_project(sandbox, project, ["git", "merge-base", s.INTEGRATE, "HEAD"])
    assert done.returncode != 0, f"the fixture meant to have no merge base has one\n{done.describe()}"
    world = s.World(sandbox, project)
    for call in (s.read(project / "src/app/main.py"), s.bash("cat src/app/added.py")):
        s.assert_refused(world.ask(call, s.TEST_DESIGNER, s.T), call, "test designer, git finds no base: ")
