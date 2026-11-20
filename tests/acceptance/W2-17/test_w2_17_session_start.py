"""S6 (fix, DEC-1223 (6)): session start prints one line when an update is pending (CAP-45.b).

The kernel's SessionStart hook of this worktree (`template/governance/kernel/hooks/sessionstart.py`) is run as a
program: the event `{}` on standard input, `CLAUDE_PROJECT_DIR` the clone, `PYTHONPATH` this worktree's `src/` so
gov imports, a `tk` first on PATH whose `tk ready` prints what the case says (nothing by default). The clone holds A
and names the patch source (B pending, kind patch) through a link.

Each case where the hook must print nothing first runs the hook on its clone with B pending and asserts the line is
there (its control): a hook that prints nothing at all does not pass it.
"""

from __future__ import annotations

import w2_17_support as support


def _line_printed(clone, what="B pending", **options):
    """The hook run on the clone with B pending: exit 0, one JSON document whose additionalContext holds the line.
    The additionalContext."""
    run = support.session_start(clone.project, clone.sandbox, options.pop("tk", clone.quiet), **options)
    assert run.returncode == 0, f"{what}: the hook does not exit 0\n{run.describe()}"
    context = support.hook_context(run)
    assert context is not None and support.PENDING_LINE in context.splitlines(), (
        f"{what}: the hook's additionalContext does not hold the line {support.PENDING_LINE!r}\n{run.describe()}")
    return context


def _nothing(run, what):
    assert run.returncode == 0, f"{what}: the hook does not exit 0\n{run.describe()}"
    assert run.stdout.strip() == "", f"{what}: the hook printed something\n{run.describe()}"


def test_session_start_prints_the_pending_line(hook_clone):
    _line_printed(hook_clone)


def test_session_start_prints_nothing_when_up_to_date(hook_clone, project_at_b, tmp_path):
    _line_printed(hook_clone)
    project = support.copy_project(project_at_b, tmp_path / "at-b")
    run = support.session_start(project, hook_clone.sandbox, hook_clone.quiet)
    _nothing(run, f"the clone at {support.B}, the newest release")


def test_session_start_prints_nothing_when_the_source_cannot_be_read(hook_clone, tmp_path):
    _line_printed(hook_clone)
    support.point(hook_clone.link, tmp_path / "nowhere")
    run = support.session_start(hook_clone.project, hook_clone.sandbox, hook_clone.quiet)
    _nothing(run, "_src_path pointing nowhere")


def test_session_start_prints_nothing_while_the_update_is_held_after_a_rollback(hook_clone):
    _line_printed(hook_clone)
    support.plant_rolled_back_record(hook_clone.project)
    run = support.session_start(hook_clone.project, hook_clone.sandbox, hook_clone.quiet)
    _nothing(run, f"{support.ROLLED_BACK_REL} in the clone")


def test_session_start_prints_nothing_when_gov_is_not_importable(hook_clone):
    _line_printed(hook_clone)
    assert not support.gov_importable(hook_clone.sandbox, with_src=False), (
        "W2-17 fixture could not be built (not the feature under test): gov imports without PYTHONPATH")
    run = support.session_start(hook_clone.project, hook_clone.sandbox, hook_clone.quiet, with_src=False)
    _nothing(run, "gov not importable")


def test_orchestrator_session_has_the_line_beside_its_existing_parts(hook_clone, tmp_path):
    tk = support.fake_tk(tmp_path / "tk-ready", "W2-17 fake tk: one ready ticket\n")
    support.point(hook_clone.link, tmp_path / "nowhere")
    without = support.session_start(hook_clone.project, hook_clone.sandbox, tk, role="orchestrator")
    parts = [part for part in (support.hook_context(without) or "").split("\n\n") if part.strip()]
    assert without.returncode == 0 and parts and any("W2-17 fake tk" in part for part in parts), (
        f"W2-17 fixture could not be built (not the feature under test): the orchestrator's hook without a pending "
        f"update printed none of its parts\n{without.describe()}")
    support.point(hook_clone.link, hook_clone.source)
    context = _line_printed(hook_clone, "GOV_ROLE=orchestrator, B pending", tk=tk, role="orchestrator")
    lost = [part for part in parts if part not in context]
    assert not lost, f"with the line added, the orchestrator's existing parts are not all there: {lost}\n{context}"


def test_the_line_survives_a_long_tk_ready_output(hook_clone, tmp_path):
    long_list = "".join(f"W2-17 fake tk: ready ticket {number:04d}, a line to fill the cap\n" for number in range(300))
    assert len(long_list) > 12_000, "fixture: the fake tk ready output is not longer than the hook's cap"
    tk = support.fake_tk(tmp_path / "tk-long", long_list)
    _line_printed(hook_clone, "tk ready printing more than the cap", tk=tk)
