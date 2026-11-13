"""S5, the follow-up R5 (DEC-1112 (3); the lead gets the launcher's own GOV_STORE): a lead's cleaned environment.

S5: a launched session gets a cleaned process environment: PATH, HOME, the locale, what the CLI needs to sign in, its
identity and the launcher's own values; none of the parent's CLAUDE* and GOV* variables and no PYTHONPATH reach it
[DEC-826 Q5, lens E F13, DEC-784, DEC-877 item 4, W2-M393]. The review's R5 (round 1): since S5 a lead started by
``gov launch orchestrator|lead <ticket>`` no longer inherits the parent's ``GOV_STORE``, and gets none of its own, so
its plain ``gov retrieve`` in a fresh worktree answers ``STORE_MISSING``. The CTO's decision: the lead gets the
launcher's own ``GOV_STORE``, exactly as a worker does (W2-116 S3: the main repository's ``integration_store``, the
link path as written), never the parent's; ``TERM`` and ``TMPDIR`` are not passed to a lead.

The lead is admitted as W2-136 and W2-20 admit one: an approved ready list naming its ticket in the main tree
(``governance/project/orchestration/ready.txt``), its waits met; the resource gate passed with the recorded override
the other W2-56 cases use (``w2_56_support.GATE_OVERRIDE``). The stand-in CLI records the session's process
environment and its ``--settings`` value; no session starts. Both lead names the launcher takes (``orchestrator``,
``lead``) are launched where the case says.
"""

from __future__ import annotations

import json
import os

import pytest

import w2_56_support as s

LEADS = ("orchestrator", "lead")
LEAD_ROLE = "orchestrator"           # GOV_ROLE of a lead, whichever name launched it
READY_REL = "governance/project/orchestration/ready.txt"
STORE_REL = "governance/project/rebuild.yaml"
PARENT_STORE = f"/tmp/{s.MARK}-store"   # the parent's GOV_STORE: a different, planted value
NO_LINE = "# integration_store is set in the main tree only (planted for W2-56 R5)\n"
UNUSABLE = (("relative", "integration_store: relative/store\n"), ("not-a-map", "- one\n- two\n"))


def _ready(*tickets) -> str:
    lines = ["# the approved ready list (planted for the W2-56 R5 cases)\n", "# batch 1\n"]
    lines += [f"{t.wbs} {t.tk} {t.wbs}-A5-plan.md {t.wbs}-A5-plan.json\n" for t in tickets]
    return "".join(lines)


def _store_link(box: s.Box):
    """The integration store's place: a link (as ``gov rebuild --integration`` keeps it) to one half."""
    half = box.base / "stores" / "half-a"
    half.mkdir(parents=True)
    link = box.base / "stores" / "integration"
    os.symlink(half, link)
    assert os.path.realpath(link) != str(link), "premise: the store's place is not a link"
    return link


def _setting(link) -> str:
    return f"integration_store: {json.dumps(str(link))}\n"


def _project(box: s.Box, store=None) -> s.Box:
    """The W2-56 fixture project, its ready list naming the ticket, and ``rebuild.yaml`` where ``store`` is given."""
    files = {READY_REL: _ready(s.T)}
    if store is not None:
        files[STORE_REL] = store
    s.make_project(box, extra=files)
    s.install_stand_in_cli(box)
    s.set_plan(box)
    return box


def _worktree_lacking_the_line(box: s.Box, link):
    """A worktree of the project made while the project's rebuild.yaml had no integration_store; the main tree's
    then names it (the worktree's own copy still lacks the line)."""
    worktree = s.add_worktree(box.project, "W2-77-lead")
    s.write(box.project / STORE_REL, _setting(link))
    assert "integration_store:" not in (worktree / STORE_REL).read_text(encoding="utf-8"), (
        "premise: the worktree's own rebuild.yaml names integration_store")
    return worktree


def _launch(box, role, *, cwd=None, planted=None) -> s.Launch:
    env = s.base_environment(box)
    env.update({"GOV_STORE": PARENT_STORE} if planted is None else planted)
    return s.run_launch(box, role, s.T.tk, env=env, cwd=cwd)


def _started(launch) -> tuple[dict, dict]:
    assert launch.returncode == 0 and launch.started, f"the launch did not start one session\n{launch.describe()}"
    return launch.call["env"], launch.settings().get("env") or {}


def _assert_the_launchers_store(launch, link, who: str) -> None:
    env, settings_env = _started(launch)
    want = str(link)
    assert env.get("GOV_STORE") == want, (
        f"{who}: the process environment's GOV_STORE is {env.get('GOV_STORE')!r}, not the launcher's own {want!r} "
        f"(the main repository's integration_store, the link as written)")
    assert settings_env.get("GOV_STORE") == want, (
        f"{who}: the --settings env's GOV_STORE is {settings_env.get('GOV_STORE')!r}, not the launcher's own {want!r}")


# --------------------------------------------------------------------------
# Point 1: the launcher's own GOV_STORE, from the main tree or a worktree of it
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", LEADS)
def test_r5_a_lead_gets_the_launchers_own_gov_store_launched_from_the_main_tree(tmp_path, role):
    box = s.make_box(tmp_path)
    link = _store_link(box)
    _project(box, store=_setting(link))
    _assert_the_launchers_store(_launch(box, role), link, f"a lead ({role}) launched from the main tree")


@pytest.mark.parametrize("role", LEADS)
def test_r5_a_lead_launched_from_a_worktree_gets_the_main_repositorys_gov_store(tmp_path, role):
    box = s.make_box(tmp_path)
    link = _store_link(box)
    _project(box, store=NO_LINE)
    worktree = _worktree_lacking_the_line(box, link)
    _assert_the_launchers_store(_launch(box, role, cwd=worktree), link,
                                f"a lead ({role}) launched from a worktree whose rebuild.yaml lacks the line")


# --------------------------------------------------------------------------
# Point 2: never the parent's GOV_STORE
# --------------------------------------------------------------------------

@pytest.mark.parametrize("configured", (True, False), ids=("with-the-setting", "without-the-setting"))
def test_r5_a_parents_gov_store_never_reaches_a_lead(tmp_path, configured):
    box = s.make_box(tmp_path)
    link = _store_link(box)
    _project(box, store=_setting(link) if configured else None)
    env, settings_env = _started(_launch(box, LEAD_ROLE))
    for where, values in (("process environment", env), ("--settings env", settings_env)):
        held = [name for name, value in values.items() if PARENT_STORE in str(value)]
        assert not held, f"the parent's GOV_STORE reached the lead's {where}: {held}"
        if not configured:
            assert "GOV_STORE" not in values, (
                f"with no integration_store set, the lead's {where} has GOV_STORE {values['GOV_STORE']!r}")


# --------------------------------------------------------------------------
# Point 3: a setting that cannot be used refuses the lead as it refuses a worker
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", LEADS)
@pytest.mark.parametrize("text", [case[1] for case in UNUSABLE], ids=[case[0] for case in UNUSABLE])
def test_r5_an_unusable_store_setting_refuses_a_lead_as_it_refuses_a_worker(tmp_path, text, role):
    box = _project(s.make_box(tmp_path))
    s.write(box.project / STORE_REL, text)   # after the commit: the launcher reads the main tree's working tree
    worker = s.run_launch(box, s.ENGINEER, s.T.tk)
    assert worker.returncode != 0 and not worker.calls and "LAUNCH_REFUSED" in worker.output, (
        f"premise: the worker's launch is not refused on the setting\n{worker.describe()}")
    lead = _launch(box, role)
    assert lead.returncode != 0, f"the lead's launch ({role}) was not refused on {text!r}\n{lead.describe()}"
    assert not lead.calls, f"the refused lead's launch started a session\n{lead.describe()}"
    assert "LAUNCH_REFUSED" in lead.output and ("rebuild.yaml" in lead.output or "integration_store" in lead.output), (
        f"the lead's refusal does not say LAUNCH_REFUSED naming the setting\n{lead.describe()}")
    left = [entry for entry in s.temp_folders(box) if entry.startswith(s.TEMP_PREFIX)]
    assert not left, f"the refused lead's launch left temp folders {left}"


# --------------------------------------------------------------------------
# Point 4: no parent TERM or TMPDIR; --settings env: role, ticket and (where set) GOV_STORE
# --------------------------------------------------------------------------

@pytest.mark.parametrize("configured", (False, True), ids=("without-the-setting", "with-the-setting"))
def test_r5_a_leads_environment_holds_no_parent_term_or_tmpdir_and_its_settings_env_role_ticket_and_store(
        tmp_path, configured):
    box = s.make_box(tmp_path)
    link = _store_link(box)
    _project(box, store=_setting(link) if configured else None)
    parent_tmp = box.base / f"{s.MARK}-tmp"
    parent_tmp.mkdir()
    planted = {name: s.parent_value(name) for name in s.PARENT_VARIABLES}
    planted.update(TERM=f"xterm-{s.MARK}", TMPDIR=str(parent_tmp))
    env, settings_env = _started(_launch(box, LEAD_ROLE, planted=planted))
    checked = {name: value for name, value in planted.items() if name != "GOV_STORE"}   # GOV_STORE: points 1, 2
    for where, values in (("process environment", env), ("--settings env", settings_env)):
        leaked = s.leaks(values, checked)
        assert not leaked, f"the parent's values reached the lead's {where}: {leaked}"
    for name in ("TERM", "TMPDIR"):
        assert env.get(name) != planted[name], f"the parent's {name} reached the lead: {env.get(name)!r}"
    expected = {"GOV_ROLE": LEAD_ROLE, "GOV_TICKET": s.T.tk}
    if configured:
        expected["GOV_STORE"] = str(link)
    assert settings_env == expected, (
        f"the lead's --settings env is {settings_env}, not GOV_ROLE, GOV_TICKET and (where set) GOV_STORE: {expected}")


# --------------------------------------------------------------------------
# Point 5 (guard): a worker's GOV_STORE stays the launcher's own
# --------------------------------------------------------------------------

@pytest.mark.parametrize("tree", ("main", "worktree"))
def test_r5_guard_a_workers_gov_store_is_still_the_launchers_own(tmp_path, tree):
    box = s.make_box(tmp_path)
    link = _store_link(box)
    cwd = None
    if tree == "main":
        _project(box, store=_setting(link))
    else:
        _project(box, store=NO_LINE)
        cwd = _worktree_lacking_the_line(box, link)
    _assert_the_launchers_store(_launch(box, s.ENGINEER, cwd=cwd), link, f"a worker launched from the {tree} tree")
