"""Fixtures for W2-206's acceptance tests: the planted runs, each built once per test session (as W2-202's are).

A planted run is built by the first process that asks for it, under a lock in the session's shared temp folder, and
read by every other case from there; a build that fails is kept as failed, and every case that reads it fails with
the build's error. Before ``gov queue`` runs, each build checks its own planted project (plain pytest at the commits
the case depends on; ``gov accept``, ``gov close --select``, ``gov rebuild --integration`` and ``gov check
--structural`` where the case stands on them), so a red case is never a broken fixture: a broken fixture fails as
``fixture: ...``.
"""

from __future__ import annotations

import fcntl
import json
import os
import shutil
import sys
import traceback
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_206_support as support  # noqa: E402
from w2_206_support import A, B, BROKEN, C, CHANGED, P, Q, base, kit, module_rel, stores  # noqa: E402


def _shared(factory, name, build):
    root = factory.getbasetemp()
    if os.environ.get("PYTEST_XDIST_WORKER"):
        root = root.parent
    folder = root / f"w2-206-{name}"
    with open(root / f"w2-206-{name}.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        done, broken = folder / "landing.json", folder / "broken.txt"
        if broken.is_file():
            raise AssertionError(f"the planted run {name} could not be built:\n{broken.read_text()}")
        if done.is_file():
            return kit.Landing(json.loads(done.read_text(encoding="utf-8")))
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True)
        try:
            data = build(folder)
        except BaseException:
            broken.write_text(traceback.format_exc(), encoding="utf-8")
            raise
        done.write_text(json.dumps(data), encoding="utf-8")
        return kit.Landing(data)


def _data(project, taken, **extra):
    """A planted run's data, as W2-115b's ``Landing`` reads it, from one step (``support.step``)."""
    return kit.landing_data(project, taken["run"], "main", _main_of(taken["before"]), taken["before"], taken=taken,
                            **extra)


def _main_of(snapshot):
    return kit.heads(snapshot).get("refs/heads/main")


def _widget(project):
    return project.plant_branch(A, "topic/aa", [({module_rel("widget"): CHANGED}, "engineer", True)])


def _helper(project):
    return project.plant_branch(A, "topic/aa", [({module_rel("helper"): CHANGED}, "engineer", True)])


def _arg(project, ticket):
    return f"{ticket.id}={project.branches[ticket.id]}"


def _records_at_tested(project, run, tickets):
    """The close records the commit a dry run tested holds (it must hold none), where the answer names that commit:
    looked for at the root and in the warm clone."""
    answer = support.one_object(run["stdout"]) or {}
    tested = (answer.get("result") or {}).get("tested") if isinstance(answer.get("result"), dict) else None
    found = []
    for where in (project.root, project.root / kit.CLONE_REL):
        if tested and (where / ".git").exists() and kit.rev(where, tested):
            found += [f"{where.name}: docs/close/{t.id}/" for t in tickets
                      if kit.git(where, "ls-tree", "-r", "--name-only", tested, "--", f"docs/close/{t.id}/").strip()]
    return {"tested": tested, "records": found}


# --------------------------------------------------------------------------
# A6: --select and --dry-run (one project: neither moves anything)
# --------------------------------------------------------------------------

def build_dry(folder):
    """A (the widget, green), B (it breaks the gadget, which its own suite and a unit test guard) and C (it adds a
    file nothing maps to a suite). In turn: ``--select`` of A, of A and B, of C; ``--dry-run --out <folder>`` of
    A; ``--dry-run`` of A and B; ``--dry-run`` of a ticket that does not exist; then the landing of A itself."""
    told = folder / "told"
    p = kit.Planted(folder / "project", told, tickets=(A, B, C), unit=(*kit.UNIT_TESTS, base.USES_GADGET))
    _widget(p)
    p.plant_branch(B, "topic/bb", [({module_rel("gadget"): BROKEN}, "engineer", True)])
    p.plant_branch(C, "topic/cc", [({support.UNMAPPED: "a file no suite is mapped to\n"}, "engineer", True)])
    kit.self_check(p, {p.base: {A.node: "passed", B.node: "passed", base.USES_GADGET_NODE: "passed"},
                       p.tips[A.id]: {A.node: "passed", kit.USES_WIDGET_NODE: "passed"},
                       p.tips[B.id]: {B.node: "failed", base.USES_GADGET_NODE: "failed"}})
    reference = {}
    for ticket in (A, B):
        own = support.close_select(p, p.tips[ticket.id], ticket.id)
        chosen = support.one_object(own["stdout"])
        assert own["code"] == 0 and chosen and chosen.get("suites"), \
            f"fixture: gov close --select does not answer for {ticket.id} at its branch tip\n{support.said(own)}"
        reference[ticket.id] = chosen
    refused = support.close_select(p, p.tips[C.id], C.id)
    assert refused["code"] == 2 and "SELECTION_REFUSED" in refused["stderr"], \
        f"fixture: gov close --select does not refuse C's unmapped path\n{support.said(refused)}"
    out_given, out_default = folder / "out-given", p.root / support.DRY_REL / f"{A.id}+{B.id}"
    out_unknown = folder / "out-unknown"
    steps = {
        "select_one": support.step(p, "--select", _arg(p, A), plain=True),
        "select_two": support.step(p, "--select", _arg(p, A), _arg(p, B), plain=True),
        "select_unmapped": support.step(p, "--select", _arg(p, C), plain=True),
        "dry": support.step(p, _arg(p, A), "--dry-run", "--out", str(out_given)),
    }
    steps["dry"].update(out=str(out_given), files=support.out_listing(out_given),
                        wait=support.wait(p, out_given / "verify.exit"),
                        at_tested=_records_at_tested(p, steps["dry"]["run"], [A]))
    steps["dry_culprit"] = support.step(p, _arg(p, A), _arg(p, B), "--dry-run")
    steps["dry_culprit"].update(out=str(out_default), files=support.out_listing(out_default),
                                wait=support.wait(p, out_default / "verify.exit"),
                                at_tested=_records_at_tested(p, steps["dry_culprit"]["run"], [A, B]))
    steps["dry_unknown"] = support.step(p, "PROJ-zzzz=topic/zz", "--dry-run", "--out", str(out_unknown))
    steps["land"] = support.step(p, _arg(p, A))
    return _data(p, steps["land"], steps=steps, reference=reference)


# --------------------------------------------------------------------------
# A6: --full
# --------------------------------------------------------------------------

def _full_project(folder, change, extra, workers=None):
    told = folder / "told"
    files = {support.CONFTEST: support.recorder(told), kit.PATH_MAP_REL: support.path_map(workers)}
    files.update({rel: make(told) for rel, make in extra.items()})
    p = kit.Planted(folder / "project", told, extra=files)
    change(p)
    return p


def build_full_red(folder):
    """A changes the widget; ``tests/unit/test_far.py`` (outside A's selection: it imports the gizmo and reads the
    widget's file) is green on the base and red with the change. ``gov queue A --full``, then ``gov queue A``."""
    p = _full_project(folder, _widget, {support.FAR: support.far})
    kit.self_check(p, {p.base: {support.FAR_NODE: "passed", A.node: "passed"},
                       p.tips[A.id]: {support.FAR_NODE: "failed", A.node: "passed", kit.USES_WIDGET_NODE: "passed"}})
    full = support.step(p, _arg(p, A), "--full")
    plain = support.step(p, _arg(p, A))
    return _data(p, full, plain=plain)


def build_full_green(folder):
    """A changes the helper; the unrelated test stays green. The path map names 12 workers; the queue's environment
    holds ``GOV_HEAVY_CPUS=0-1`` and ``PYTEST_XDIST_AUTO_NUM_WORKERS=2``. ``gov queue A --full``."""
    p = _full_project(folder, _helper, {support.FAR: support.far}, workers=12)
    kit.self_check(p, {p.tips[A.id]: {support.FAR_NODE: "passed", A.node: "passed",
                                      support.USES_HELPER_NODE: "passed", support.GIZMO_NODE: "passed"}})
    env = support.env_of(p, {"GOV_HEAVY_CPUS": "0-1", "PYTEST_XDIST_AUTO_NUM_WORKERS": "2"})
    return _data(p, support.step(p, _arg(p, A), "--full", env=env))


def build_full_plain(folder):
    """A changes the helper. Outside its selection: a test red on the base (a bare assert) and a test red the first
    time it runs. The path map names no workers and the environment neither variable. ``gov queue A --full``."""
    p = _full_project(folder, _helper, {support.KNOWN_FAR: support.known_far, support.ONCE: support.once})
    kit.self_check(p, {p.base: {support.KNOWN_FAR_NODE: "failed", support.ONCE_NODE: "passed"},
                       p.tips[A.id]: {support.KNOWN_FAR_NODE: "failed", A.node: "passed",
                                      support.USES_HELPER_NODE: "passed"}})
    env = support.env_of(p)
    for name in ("GOV_HEAVY_CPUS", "PYTEST_XDIST_AUTO_NUM_WORKERS", "GOV_HEAVY_WORKERS", "GOV_HEAVY_SLOTS"):
        assert name not in env, f"fixture: the queue's environment holds {name}"
    sizes = support.one_slot(p, env)
    return _data(p, support.step(p, _arg(p, A), "--full", env=env), sizes=sizes)


FULL_TIME_LIMIT = "30"


def build_full_timeout(folder):
    """A changes the helper; ``tests/unit/test_slow.py`` (outside its selection) never ends inside the run's limit.
    ``gov queue A --full --timeout 30`` (the test map's per-test limit is 120 s, so the run's limit comes first)."""
    p = _full_project(folder, _helper, {support.SLOW: support.slow})
    assert kit.TEST_MAP["per_test_timeout"] > int(FULL_TIME_LIMIT), "fixture: the per-test limit comes first"
    kit.self_check(p, {p.tips[A.id]: {support.SLOW_NODE: "passed", A.node: "passed"}})
    return _data(p, support.step(p, _arg(p, A), "--full", "--timeout", FULL_TIME_LIMIT))


# --------------------------------------------------------------------------
# A8: the after-step
# --------------------------------------------------------------------------

def _store_line(root, env, link):
    """The store line ``gov retrieve --root <link>`` prints, and the run."""
    done = support.gov(root, "retrieve", "--root", str(link), "the quillwort ledger", env=stores.run_environment(env))
    lines = [line for line in (done["stdout"] + "\n" + done["stderr"]).splitlines() if line.startswith("store: ")]
    return (lines[0] if lines else None), done


def build_after_store(folder):
    """A project whose ``rebuild.yaml`` names an integration store (a link outside the project), built at the base
    by ``gov rebuild --integration main`` with stand-in embedding endpoints; A changes the widget. ``gov queue A``,
    then the store line ``gov retrieve --root <link>`` prints."""
    lacking = stores.lacking()
    assert not lacking, f"fixture: {lacking}"
    box = stores.make_box(folder / "box")
    extra = {".gitleaks.toml": stores.GITLEAKS_TEMPLATE.read_text(encoding="utf-8"),
             kit.PATH_MAP_REL: stores.path_map_text(), support.REBUILD_REL: stores.settings_text(box),
             "docs/notes/kept.md": stores.note("quillwort")}
    p = kit.Planted(folder / "project", folder / "told", extra=extra)
    _widget(p)
    kit.self_check(p, {p.tips[A.id]: {A.node: "passed", kit.USES_WIDGET_NODE: "passed"}})
    build, questions = stores.Embedder(), stores.Embedder()
    try:
        env = {**support.env_of(p), **stores.environment(box, build.host, questions.host)}
        first = support.gov(p.root, "rebuild", "--json", "--integration", "main", env=stores.run_environment(env))
        assert first["code"] == 0, f"fixture: the integration store cannot be built at the base\n{support.said(first)}"
        line, asked = _store_line(p.root, env, box.link)
        assert line and p.base[:12] in line and "stale" not in line, \
            f"fixture: the store line before the landing is {line!r}\n{support.said(asked)}"
        taken = support.step(p, _arg(p, A), env=env)
        line_after, asked_after = _store_line(p.root, env, box.link)
    finally:
        build.close()
        questions.close()
    return _data(p, taken, link=str(box.link), line_before=line, line_after=line_after,
                 asked_after=support.said(asked_after))


def build_after_plain(folder):
    """A project whose ``rebuild.yaml`` names no store, with a declared schema check that notices a changed widget
    and tells where and when it ran; A changes the widget. ``gov queue A``; then the structural pass itself, in a
    scratch clone at the landed head with the old head as its base (its own lines, to read ``queue.json`` against)."""
    told = folder / "told"
    root = folder / "project"
    extra = {support.REBUILD_REL: "slow_after_s: 600\n", support.CHECK_DECL_REL: support.CHECK_DECL,
             support.CHECK_SCRIPT_REL: support.check_script(root, told)}
    p = kit.Planted(root, told, extra=extra)
    _widget(p)
    kit.self_check(p, {p.tips[A.id]: {A.node: "passed", kit.USES_WIDGET_NODE: "passed"}})
    env = support.env_of(p)
    no_store = support.gov(p.root, "rebuild", "--json", "--integration", "main", env=env)
    assert no_store["code"] != 0 and "integration_store" in no_store["stdout"] + no_store["stderr"], \
        f"fixture: gov rebuild --integration does not say the project names no store\n{support.said(no_store)}"
    at_base = support.structural(p.root, p.base, env)
    assert at_base["code"] == 0 and "schema: ok" in at_base["stdout"], \
        f"fixture: the planted check is not ok at the base\n{support.said(at_base)}"
    at_tip = support.structural(base.scratch_at(p, p.tips[A.id], "structural"), p.base, env)
    assert at_tip["code"] == 0 and f"schema: NOTICE {support.NOTICED}" in at_tip["stdout"], \
        f"fixture: the planted check does not notice the changed widget\n{support.said(at_tip)}"
    assert not support.rows(told, support.STRUCTURAL_TOLD), "fixture: the planted check told a run of the fixture's"
    assert not (p.root / ".gov-runtime" / "store.db").exists(), "fixture: the root holds a store before the landing"
    taken = support.step(p, _arg(p, A), env=env)
    head = _main_of(taken["after"])
    own = support.structural(base.scratch_at(p, head, "structural"), p.base, env)
    return _data(p, taken, own_lines=own["stdout"].splitlines(), own_code=own["code"])


def build_after_failing(folder):
    """A project whose ``rebuild.yaml`` names a store that cannot be built (the place is a plain file, no link) and
    where the structural pass cannot run at all (git does not answer its first question: exit 2). B breaks the gadget
    (a culprit); A changes the widget. ``gov queue B`` (nothing lands), then ``gov queue A``."""
    link = folder / "stores" / "integration"
    link.parent.mkdir(parents=True)
    link.write_text("a plain file where the store's link should be\n", encoding="utf-8")
    extra = {support.REBUILD_REL: f"slow_after_s: 600\nintegration_store: {json.dumps(str(link))}\n"}
    p = kit.Planted(folder / "project", folder / "told", unit=(*kit.UNIT_TESTS, base.USES_GADGET), extra=extra)
    _widget(p)
    p.plant_branch(B, "topic/bb", [({module_rel("gadget"): BROKEN}, "engineer", True)])
    kit.self_check(p, {p.tips[A.id]: {A.node: "passed", kit.USES_WIDGET_NODE: "passed"},
                       p.tips[B.id]: {base.USES_GADGET_NODE: "failed"}})
    plain = support.env_of(p)
    env = {**plain, "PATH": f"{support.failing_git(folder / 'bin')}{os.pathsep}{plain['PATH']}"}
    unbuilt = support.gov(p.root, "rebuild", "--json", "--integration", "main", env=env)
    assert unbuilt["code"] != 0 and "REBUILD_FAILED" in unbuilt["stdout"] + unbuilt["stderr"], \
        f"fixture: the planted store can be built\n{support.said(unbuilt)}"
    assert link.is_file() and not link.is_symlink(), "fixture: the store's place is no plain file any more"
    could, cannot = support.structural(p.root, p.base, plain), support.structural(p.root, p.base, env)
    assert could["code"] == 0 and cannot["code"] == 2, \
        f"fixture: the structural pass exits {could['code']} with git and {cannot['code']} with the planted git\n" \
        f"{support.said(cannot)}"
    assert kit.git(p.root, "status", "--porcelain") == "", "fixture: the fixture's own checks left the root dirty"
    culprit = support.step(p, _arg(p, B), env=env)
    taken = support.step(p, _arg(p, A), env=env)
    return _data(p, taken, culprit=culprit)


# --------------------------------------------------------------------------
# W2-202 fix 2: an acceptance run that fails without naming a failing test
# --------------------------------------------------------------------------

def _unnamed_project(folder, ticket, uses, readme, suite):
    """B (the gadget, clean) and ``ticket``, whose acceptance folder holds its README alone on the base; its work
    branch brings the folder's test file (the test designer's commit) and its module's change (the engineer's)."""
    told = folder / "told"
    extra = {ticket.ticket_rel: kit.ticket_text(ticket), ticket.acceptance + "README.md": readme}
    p = kit.Planted(folder / "project", told, unit=(*kit.UNIT_TESTS, base.USES_GADGET, uses), extra=extra)
    p.tickets[ticket.id] = ticket
    p.plant_branch(ticket, f"topic/{ticket.slug}",
                   [({ticket.suite_file: suite(told)}, "independent-test-designer", True),
                    ({module_rel(ticket.modules[0]): CHANGED}, "engineer", True)])
    p.plant_branch(B, "topic/bb", [({module_rel("gadget"): CHANGED}, "engineer", True)])
    return p


def _accept_says(project, ticket):
    own = base.accept_at(project, project.tips[ticket.id], ticket.id)
    try:
        return own, json.loads(own["stdout"])["result"]
    except (ValueError, KeyError, TypeError):
        raise AssertionError(f"fixture: gov accept gives no result for {ticket.id}\n{support.said(own)}") from None


def build_unnamed(folder):
    """P's README maps its failure line to a test that does not exist: its one test passes, its acceptance run
    fails, and no failing test is named. ``gov queue P B``; then ``gov queue P`` alone."""
    p = _unnamed_project(folder, P, support.USES_MOD_PP, support.readme_with_a_missing_test(P),
                         lambda told: kit.telling(P.suite_file, told, P.modules))
    kit.self_check(p, {p.tips[P.id]: {P.node: "passed", kit.node(support.USES_MOD_PP[0]): "passed"},
                       p.tips[B.id]: {B.node: "passed", base.USES_GADGET_NODE: "passed"}})
    own, result = _accept_says(p, P)
    assert own["code"] != 0 and result.get("outcome") == "fail" and (result.get("totals") or {}).get("failed") == 0, \
        f"fixture: gov accept does not fail P's run with no failed test\n{support.said(own)}"
    batch = support.step(p, _arg(p, P), _arg(p, B))
    alone = support.step(p, _arg(p, P))
    return _data(p, batch, alone=alone)


def build_unnamed_crash(folder):
    """Q's suite, brought by its branch, crashes at collection: its acceptance run is an error naming no test.
    ``gov queue Q B``."""
    p = _unnamed_project(folder, Q, support.USES_MOD_QQ, kit.readme_text(Q), lambda told: support.CRASHING)
    kit.self_check(p, {p.tips[B.id]: {B.node: "passed", base.USES_GADGET_NODE: "passed"},
                       p.tips[Q.id]: {kit.node(support.USES_MOD_QQ[0]): "passed"}})
    own, result = _accept_says(p, Q)
    assert own["code"] != 0 and result.get("outcome") == "error" and result.get("error_kind") == "collection", \
        f"fixture: gov accept does not say Q's suite crashes at collection\n{support.said(own)}"
    return _data(p, support.step(p, _arg(p, Q), _arg(p, B)))


BUILDS = {name[len("build_"):]: f for name, f in globals().items() if name.startswith("build_")}


@pytest.fixture(scope="session")
def landing(tmp_path_factory):
    """``landing(name)``: the planted run ``name`` (one of ``BUILDS``), built once per session."""
    return lambda name: _shared(tmp_path_factory, name, BUILDS[name])
