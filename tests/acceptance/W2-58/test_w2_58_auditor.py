"""W2-58, item 6 -- reviewers and auditors read everything, tests and code alike.

KPI success 5: "Reviewers and auditors read everything, tests and code alike
[DEC-820]". DEC-820 item 3. (a) and (b) still refuse an auditor (see
``test_w2_58_still_refused.py``, every role); (d) refuses it only when a set
lists it as measured.

The auditor runs on T (``GOV_TICKET`` = T's id), in the branch project: it reads
T's acceptance folder and T's changed files by every route.
"""

from __future__ import annotations

import pytest

import w2_58_support as s

TEST_FILE = f"{s.T.acceptance}/test_feature.py"


def _calls(world):
    return [
        s.read(world.path(TEST_FILE)),
        s.grep(path=world.path(s.T.acceptance)),
        s.bash(f"cat {TEST_FILE}"),
        s.bash(f"grep -rn {s.WORD} tests/"),
        s.bash(f"git show HEAD:{TEST_FILE}"),
        s.read(world.path("src/app/main.py")),
        s.grep(path=world.path("src/app")),
        s.bash("cat src/app/added.py"),
        s.bash(f"git show HEAD:src/app/main.py"),
        s.bash(f"git diff {s.INTEGRATE}...HEAD"),
        s.bash("git log -p"),
        s.grep(),
        s.bash(f"grep -r {s.WORD} ."),
    ]


IDS = ("Read-test", "Grep-tests", "cat-test", "grep-r-tests", "git-show-HEAD-test", "Read-changed", "Grep-changed",
       "cat-changed", "git-show-HEAD-changed", "git-diff-base", "git-log-p", "Grep-no-path", "grep-r-dot")


@pytest.mark.parametrize("index", range(len(IDS)), ids=IDS)
def test_the_auditor_on_t_reads_its_tests_and_its_code(branch_world, index):
    call = _calls(branch_world)[index]
    s.assert_allowed(branch_world.ask(call, s.AUDITOR, s.T), call, "auditor on T: ")


def test_secrets_and_held_out_material_still_refuse_the_auditor(branch_world):
    for call in (s.read(branch_world.path(".env")), s.bash("cat config/secrets.yaml"),
                 s.read(branch_world.sandbox.held_out / "answers.md"), s.bash("cat ~/held-out-material/answers.md")):
        s.assert_refused(branch_world.ask(call, s.AUDITOR, s.T), call, "auditor on T: ")


def test_an_auditor_a_set_lists_as_measured_is_refused_its_hidden_part(sandbox):
    project = s.make_eval_project(sandbox, block=s.evaluation_block(roles=(s.AUDITOR,), tickets=()))
    world = s.World(sandbox, project)
    for call in (s.read(project / "eval/memory/hidden/answers.yaml"), s.bash("cat eval/memory/hidden/answers.yaml")):
        s.assert_refused(world.ask(call, s.AUDITOR, s.T), call, "measured auditor: ")
    call = s.read(project / "eval/memory/visible/questions.yaml")
    s.assert_allowed(world.ask(call, s.AUDITOR, s.T), call, "measured auditor: ")
