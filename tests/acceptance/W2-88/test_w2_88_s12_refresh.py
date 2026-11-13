"""S12 (success-12): the store is current after every merge; adoption installs the refresh (I3's ``refresh`` block and the
ACT package) and the refresh is W2-116's ``gov rebuild --integration <branch>`` (double-buffered).

Two halves. (1) The A9 record's ``refresh {command, hook}`` and the ACT package that installs it (red until A9 exists).
(2) The behaviour on a planted repository, through W2-116's builders and ``--integration`` (its code is on this head, so
these two cases are GREEN on the base: they hold W2-116's behaviour for the adopted repository; they go red for W2-116
if its code is ever missing: ``waits_on`` DAEO-f58b).
"""

from __future__ import annotations

import w2_88_support as W

S116 = None


def _s116():
    global S116
    if S116 is None:
        import w2_116_support as module
        S116 = module
    return S116


def test_s12_the_record_names_the_refresh_command_and_its_hook(worlds):
    refresh = worlds.a9("default").record().get("refresh")
    assert isinstance(refresh, dict), f"refresh: {refresh!r}"
    assert "gov rebuild --integration" in str(refresh.get("command")), f"refresh.command: {refresh.get('command')!r}"
    assert str(refresh.get("hook", "")).strip(), "refresh.hook (the update of the integration branch that runs it) is not named"


def test_s12_the_act_package_installs_the_refresh_and_adoption_installs_nothing_itself(worlds):
    nine = worlds.a9("default")
    nine.record()
    texts = W.all_text(nine.out / "memory-audit")
    assert any(b"gov rebuild --integration" in data for data in texts.values()), \
        "no file of memory-audit/ (the ACT package) names `gov rebuild --integration <branch>`"
    hooks = nine.project / ".git" / "hooks"
    assert not [p for p in hooks.iterdir() if not p.name.endswith(".sample")] if hooks.is_dir() else True, \
        "A9 installed a git hook itself: the refresh goes through the ACT package, never the tool"


def test_s12_a_merge_followed_by_a_query_returns_the_new_commit(tmp_path):
    s = _s116()
    reason = s.lacking()
    if reason:
        import pytest
        pytest.skip(reason)
    box, build, query = s.make_box(tmp_path / "box"), s.Embedder(), s.Embedder()
    try:
        env = s.environment(box, build.host, query.host)
        project = s.make_project(box)
        s.built_integration(project, env)
        s.land_h2(project)
        s.built_integration(project, env)
        run = s.search(project, env, s.MERGED_WORD, root=box.link)
        assert run.ok, run.describe()
        assert s.MERGED in s.evidence_paths(run), f"the search through the link does not return the merged note: {s.evidence_paths(run)}"
    finally:
        build.close()
        query.close()


def test_s12_a_failing_build_keeps_the_old_store_and_reports_the_failure(tmp_path):
    s = _s116()
    reason = s.lacking()
    if reason:
        import pytest
        pytest.skip(reason)
    box, build, query = s.make_box(tmp_path / "box"), s.Embedder(), s.Embedder()
    try:
        env = s.environment(box, build.host, query.host)
        project = s.make_project(box)
        s.built_integration(project, env)
        ready = s.assert_link(box)
        s.land_h2(project)
        failing = s.environment(box, s.closed_host(), query.host)
        run = s.integration_build(project, failing)
        assert not run.ok, f"a build with no embedder succeeded\n{run.describe()}"
        assert (run.stderr + run.stdout).strip(), "the failure was not reported"
        assert s.target(box) == ready, "the failed build moved the link: the old store is not kept in service"
        answered = s.search(project, env, s.KEPT_WORD, root=box.link)
        assert answered.ok and s.evidence_paths(answered), f"the old store no longer answers\n{answered.describe()}"
    finally:
        build.close()
        query.close()
