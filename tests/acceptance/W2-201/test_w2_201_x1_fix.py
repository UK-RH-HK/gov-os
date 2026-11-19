"""W2-201 fix X1 (DEC-1219 (5)): a fix launches under its owning ticket, closed or not; and the Interface paragraph's
usage errors and record keys.

``gov launch <role> <ticket> --fix "<line>"`` on W2-184's fixture project and the stand-in CLI: the ticket file exists,
whatever its status, and the role starts with the model and effort the rubric gives that ticket's class (``by
criticality``); the record holds ``kind`` ``fix``, ``ticket`` and ``kind_line``. ``--plan --fix`` prints the role's
default line; ``--tests-worktree --fix`` makes the closed ticket's tests worktree. Without ``--fix`` the same launches
are refused as today (``is not in_progress``). The usage errors (exit 2, nothing started or recorded), the refusals that
stay (an unknown ticket, another role's ticket, another model, the pause) and the ordinary launch's ``kind`` ``feature``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import w2_201_support as k
import w2_201_x_support as x

s, b = x.s, x.b


@pytest.mark.parametrize("status, cls, model", [("closed", "C3", x.OPUS), ("closed", "C2", x.SONNET),
                                                ("open", "C2", x.SONNET), ("in_progress", "C2", x.SONNET)])
def test_x1_an_engineer_launches_with_fix_on_its_ticket_whatever_its_status(sandbox, project, cli, status, cls, model):
    tk = x.ticket(project, x.ENGINEER, cls, status, tk=f"DAEO-fx{cls.lower()}{status[0]}")
    result = x.launch(sandbox, cli, x.ENGINEER, tk, "--fix", x.FIX_LINE)
    x.launched(result)
    effort = x.ENGINEER_TABLE[cls][1]
    x.assert_line(result, model, effort)
    got = x.record_of(result, "kind", "ticket", "kind_line", "model", "model_source", "effort", "effort_source",
                      "criticality")
    want = {"kind": "fix", "ticket": tk, "kind_line": x.FIX_LINE, "model": model, "model_source": "by criticality",
            "effort": effort, "effort_source": "by criticality", "criticality": cls}
    assert got == want, f"the fix's launch record states {got}, not {want}"
    k.quiet(result)


@pytest.mark.parametrize("cls", ["C3", "C2"])
def test_x1_the_same_launch_without_fix_is_refused_as_today(sandbox, project, cli, cls):
    """Guard on the base: a closed ticket refuses an ordinary launch."""
    tk = x.ticket(project, x.ENGINEER, cls, "closed", tk=f"DAEO-nf{cls.lower()}")
    s.refused(x.launch(sandbox, cli, x.ENGINEER, tk), "is not in_progress", tk)


def test_x1_plan_with_fix_prints_the_role_s_default_line(sandbox, project, cli):
    tk = x.ticket(project, x.ENGINEER, "C3", "closed", tk="DAEO-fxpl")
    result = x.launch(sandbox, cli, x.ENGINEER, tk, "--plan", "--fix", x.FIX_LINE)
    model, effort = x.ROLE_DEFAULT
    assert result.run.returncode == 0, f"--plan --fix did not end 0\n{result.describe()}"
    assert result.run.stdout.strip() == f"model {model}, effort {effort}", (
        f"--plan --fix did not print the role's default line\n{result.describe()}")
    assert not result.calls and not result.new_records, f"--plan started or recorded something\n{result.describe()}"


def test_x1_plan_without_fix_on_a_closed_ticket_is_refused_as_today(sandbox, project, cli):
    """Guard on the base."""
    tk = x.ticket(project, x.ENGINEER, "C3", "closed", tk="DAEO-nfpl")
    result = x.launch(sandbox, cli, x.ENGINEER, tk, "--plan")
    s.refused(result, "is not in_progress")
    assert result.run.stdout.strip() == "", f"a refused --plan printed a line\n{result.describe()}"


def _tests_tree(sandbox):
    return Path(f"{Path(sandbox.project).resolve()}-tests")


def test_x1_tests_worktree_with_fix_makes_the_closed_ticket_s_tests_worktree(sandbox, project, cli):
    tk = x.ticket(project, x.ENGINEER, "C2", "closed", tk="DAEO-fxtw")
    tree = _tests_tree(sandbox)
    result = x.launch(sandbox, cli, x.TEST_DESIGNER, tk, "--tests-worktree", "--fix", x.FIX_LINE)
    assert result.run.returncode == 0, f"--tests-worktree --fix did not end 0\n{result.describe()}"
    assert result.run.stdout.strip() == str(tree), f"it did not print the tests worktree's path {tree}\n" \
                                                   f"{result.describe()}"
    assert tree.is_dir(), f"no tests worktree at {tree}"
    listed = b.git(project, "worktree", "list", "--porcelain")
    assert f"worktree {tree}" in listed and "branch refs/heads/main-tests" in listed, (
        f"git does not list the tests worktree on main-tests:\n{listed}")
    assert not result.calls and not result.new_records, "--tests-worktree started or recorded something"


def test_x1_tests_worktree_without_fix_on_a_closed_ticket_is_refused_as_today(sandbox, project, cli):
    """Guard on the base."""
    tk = x.ticket(project, x.ENGINEER, "C2", "closed", tk="DAEO-nftw")
    result = x.launch(sandbox, cli, x.TEST_DESIGNER, tk, "--tests-worktree")
    s.refused(result, "is not in_progress")
    assert not _tests_tree(sandbox).exists(), "a refused --tests-worktree made the tests worktree"


def test_x1_a_fix_on_an_unknown_ticket_is_refused(sandbox, project, cli):
    s.refused(x.launch(sandbox, cli, x.ENGINEER, "DAEO-nope", "--fix", x.FIX_LINE), "unknown ticket", "DAEO-nope")


def test_x1_a_fix_keeps_the_role_to_its_own_ticket(sandbox, project, cli):
    """The engineer keeps to its own ticket (``_check_ticket``'s role rule): a closed product-spec ticket refuses."""
    tk = x.ticket(project, x.PRODUCT_SPEC, "C2", "closed", tk="DAEO-fxps")
    s.refused(x.launch(sandbox, cli, x.ENGINEER, tk, "--fix", x.FIX_LINE), "another role")


def test_x1_a_fix_still_refuses_a_caller_s_other_model(sandbox, project, cli):
    """S4 as for any launch: Opus asked on a C2 ticket, no exceptions file."""
    tk = x.ticket(project, x.ENGINEER, "C2", "closed", tk="DAEO-fxmd")
    result = x.launch(sandbox, cli, x.ENGINEER, tk, "--fix", x.FIX_LINE, "--", "--model", x.OPUS)
    s.refused(result, x.OPUS, k.EXCEPTIONS_REL)


def test_x1_a_fix_is_stopped_by_gov_pause(sandbox, project, cli):
    tk = x.ticket(project, x.ENGINEER, "C2", "closed", tk="DAEO-fxpa")
    env, words = x.stop(sandbox, "pause")
    x.stopped(x.launch(sandbox, cli, x.ENGINEER, tk, "--fix", x.FIX_LINE, extra_env=env), words)


@pytest.mark.parametrize("role", [x.ENGINEER, x.TEST_DESIGNER])
def test_x1_an_ordinary_launch_records_kind_feature_and_kind_line_null(sandbox, project, cli, role):
    tk = s.ticket(project, role, "C2")
    result = x.launch(sandbox, cli, role, tk)
    x.launched(result)
    got = x.record_of(result, *x.KIND_KEYS)
    assert got == {"kind": "feature", "kind_line": None}, f"an ordinary launch's record states {got}"


TK = "DAEO-usag"
USAGE = {
    "fix-and-chore": ("{role}", TK, "--fix", x.FIX_LINE, "--chore", x.CHORE_LINE),
    "fix-with-no-ticket": ("{role}", "--fix", x.FIX_LINE),
    "chore-with-a-ticket": ("{role}", TK, "--chore", x.CHORE_LINE),
    "neither-and-no-ticket": ("{role}",),
    "fix-blank": ("{role}", TK, "--fix", ""),
    "fix-spaces": ("{role}", TK, "--fix", "   "),
    "chore-blank": ("{role}", "--chore", ""),
    "chore-spaces": ("{role}", "--chore", " \t "),
}


@pytest.mark.parametrize("role", [x.ENGINEER, "orchestrator"])
@pytest.mark.parametrize("case", list(USAGE))
def test_x1_a_usage_error_ends_2_before_the_launcher(sandbox, project, cli, case, role):
    """The ticket exists (closed), so nothing but the usage rule can refuse. ``neither-and-no-ticket`` is a guard on
    the base (argparse already requires the ticket)."""
    x.ticket(project, x.ENGINEER, "C2", "closed", tk=TK)
    words = tuple(role if word == "{role}" else word for word in USAGE[case])
    x.usage_error(x.launch(sandbox, cli, *words))
