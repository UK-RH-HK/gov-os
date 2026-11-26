"""GB-1 and GB-2 (plan item 1-0 (b); ``.tickets/DAEO-l2b2.md`` "Fix: the selection's graph is the merged tree"): the
selection is read from the merged tree of the run, whatever an earlier run left in the warm clone (GB-1), and the
landing's answer, ``queue.json``, a dry run's answer and ``select.json``, the ``--select`` object and a ticket's first
close record say that tree's commit as ``graph_commit`` (GB-2).

Public interface: ``python3 -m gov.cli.main queue <ticket>=<branch> ... [--select | --dry-run --out <dir> | --full]``,
its answer and exit code, ``queue.json``, ``select.json``, the close record, the warm clone's git objects and the
planted tests' run logs. Each planted project is built once per session (a file lock in pytest's shared folder). The
kit is W2-115b's (``w2_206_support.kit``).
"""

from __future__ import annotations

import fcntl
import json
import os
import re
import shutil
import traceback

import pytest

import w2_206_support as support
from w2_206_support import A, B, BROKEN, C, CHANGED, base, kit, module_rel

KEY = "graph_commit"
LEFTOVER = "tests/unit/test_leftover.py"          # untracked in the stale warm clone, in no commit
BASE_ONLY = "tests/unit/test_base_only.py"        # only the integration head holds it
BRANCH_ONLY = "tests/unit/test_branch_only.py"    # only the branch holds it
MERGED_SUITES = sorted([A.acceptance, kit.USES_WIDGET[0], BASE_ONLY, BRANCH_ONLY])
FIX_LINE = "the module cc returns None for a blank name"


def _shared(factory, name, build):
    root = factory.getbasetemp()
    if os.environ.get("PYTEST_XDIST_WORKER"):
        root = root.parent
    folder = root / f"w2-206-graph-{name}"
    with open(root / f"w2-206-graph-{name}.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        done, broken = folder / "data.json", folder / "broken.txt"
        if broken.is_file():
            raise AssertionError(f"the planted run {name} could not be built:\n{broken.read_text()}")
        if done.is_file():
            return json.loads(done.read_text(encoding="utf-8"))
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True)
        try:
            data = build(folder)
        except BaseException:
            broken.write_text(traceback.format_exc(), encoding="utf-8")
            raise
        done.write_text(json.dumps(data), encoding="utf-8")
        return data


# --------------------------------------------------------------------------
# Reading what a run left, at the moment it ended
# --------------------------------------------------------------------------

def _commit_info(p, value, head, tips):
    """What the warm clone holds of the commit ``value`` names (None where it names none the clone holds)."""
    clone = p.root / kit.CLONE_REL
    if not (isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) and kit.rev(clone, value) == value):
        return None
    return {"parents": kit.parents(clone, value),
            "holds": {name: kit.is_ancestor(clone, commit, value) for name, commit in {"head": head, **tips}.items()}}


def _run(p, *args, plain=False, tickets=()):
    """One ``gov queue``: the step, the integration head before it, ``queue.json``'s result and each ticket's close
    record at ``main`` (None where there is none), and what the warm clone holds of the ``graph_commit`` it said."""
    head = kit.rev(p.root, "main")
    taken = support.step(p, *args, plain=plain)
    said = support.one_object(taken["run"]["stdout"]) or {}
    result = said if plain else said.get("result")
    result = result if isinstance(result, dict) else None
    held = None
    rel = (result or {}).get("record")
    if rel and (p.root / rel).is_file():
        data = json.loads((p.root / rel).read_text(encoding="utf-8"))
        held = data.get("result") if isinstance(data.get("result"), dict) else data
    closes = {}
    for ticket in tickets:
        text = kit.show(p.root, "main", f"docs/close/{ticket.id}/CL-{ticket.id}.md")
        closes[ticket.id] = None if text is None else json.loads(json.dumps(kit.front_matter(text), default=str))
    taken.update(head=head, result=result, held=held, close=closes,
                 commit=_commit_info(p, (result or {}).get(KEY), head, dict(p.tips)))
    return taken


def _branch(p, ticket, name, files, start=None, more=()):
    """``name`` from ``start`` (the base), one engineer's commit of ``ticket``'s."""
    p.branch_from(name, start)
    p.commit(f"work on {ticket.id}", kit.ENGINEER, [f"Task: {ticket.id}", "Role: engineer", *more], files)
    p.home()
    p.record_branch(ticket, name)
    return p.tips[ticket.id]


def _stale(p):
    """The warm clone an earlier run left, put back at the older commit (the planted base), with an untracked test
    file that imports the module A changes."""
    clone = p.root / kit.CLONE_REL
    assert (clone / ".git").exists(), "fixture: no warm clone was left by the earlier run"
    kit.git(clone, "checkout", "-q", "-f", "--detach", p.base)
    path = clone / LEFTOVER
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(kit.telling(LEFTOVER, p.told, ["widget"]), encoding="utf-8")
    assert kit.rev(clone, "HEAD") == p.base != kit.rev(p.root, "main"), "fixture: the warm clone is not behind"
    assert f"?? {LEFTOVER}" in kit.git(clone, "status", "--porcelain", "--untracked-files=all"), \
        "fixture: the left-over test file is not untracked in the warm clone"


def _leftover_would_be_selected(p, tip):
    """Fixture: on a merged tree that does hold the left-over file, ``gov close --select`` selects it."""
    scratch = base.scratch_at(p, "main", "leftover")
    kit.git(scratch, "merge", "-q", "--no-ff", "--no-edit", tip)
    (scratch / LEFTOVER).write_text(kit.telling(LEFTOVER, p.told, ["widget"]), encoding="utf-8")
    kit.git(scratch, "add", "-A")
    kit.git(scratch, "commit", "-q", "--no-gpg-sign", "-m", "hold the left-over file")
    done = support.gov(scratch, "close", "--select", A.id, "--root", str(scratch),
                       env=kit.base_env(scratch.parent / f"{scratch.name}-env"))
    chosen = support.one_object(done["stdout"]) or {}
    assert done["code"] == 0 and LEFTOVER in chosen.get("suites", []), \
        f"fixture: a tree holding the left-over file does not select it\n{support.said(done)}"
    shutil.rmtree(scratch, ignore_errors=True)


# --------------------------------------------------------------------------
# The planted projects
# --------------------------------------------------------------------------

def build_main(folder):
    """A changes the widget and brings a unit test; after a first ``--select`` (which leaves the warm clone) ``main``
    gains a unit test of its own. C is closed. In turn, the warm clone made stale before each of the first three:
    ``--select`` A; ``--dry-run --out`` A; the landing of A. Then ``B --full``, and a fix landing of C."""
    told = folder / "told"
    p = kit.Planted(folder / "project", told, tickets=(A, B, C),
                    extra={C.ticket_rel: kit.ticket_text(C, "closed")})
    tip = _branch(p, A, "topic/aa", {module_rel("widget"): CHANGED,
                                     BRANCH_ONLY: kit.telling(BRANCH_ONLY, told, ["widget"])})
    _branch(p, B, "topic/bb", {module_rel("gadget"): CHANGED})
    first = support.queue(p, f"{A.id}=topic/aa", "--select", plain=True)
    assert first["code"] == 0, f"fixture: the first --select does not answer\n{support.said(first)}"
    p.commit("a commit of the base: a unit test", kit.ORCHESTRATOR, ["Role: orchestrator"],
             {BASE_ONLY: kit.telling(BASE_ONLY, told, ["widget"])})
    for name in (BASE_ONLY, BRANCH_ONLY):
        where = "main" if name == BASE_ONLY else tip
        other = tip if name == BASE_ONLY else "main"
        assert kit.show(p.root, where, name) and kit.show(p.root, other, name) is None, \
            f"fixture: {name} is not held by one side alone"
    kit.self_check(p, {tip: {A.node: "passed", kit.USES_WIDGET_NODE: "passed", kit.node(BRANCH_ONLY): "passed"},
                       "main": {kit.node(BASE_ONLY): "passed"}})
    _leftover_would_be_selected(p, tip)
    arg = f"{A.id}=topic/aa"
    _stale(p)
    select = _run(p, arg, "--select", plain=True)
    _stale(p)
    out = folder / "out"
    dry = _run(p, arg, "--dry-run", "--out", str(out), tickets=(A,))
    chosen = out / "select.json"
    dry["select_json"] = support.one_object(chosen.read_text(encoding="utf-8")) if chosen.is_file() else None
    _stale(p)
    land = _run(p, arg, tickets=(A,))
    assert (land["result"] or {}).get("landed") == [A.id], f"fixture: A did not land\n{kit.describe(land['run'])}"
    land["ran"] = {name: len(p.told_runs(name)) - land["before"]["told"].get(f"{name}.jsonl", 0)
                   for name in ("test_base_only", "test_branch_only")}
    leftover_ran = len(p.told_runs("test_leftover"))
    full = _run(p, f"{B.id}=topic/bb", "--full", tickets=(B,))
    assert (full["result"] or {}).get("landed") == [B.id], f"fixture: B --full did not land\n{kit.describe(full['run'])}"
    _branch(p, C, "fix/cc", {module_rel("mod_cc"): CHANGED}, start="main", more=[f"Fix: {FIX_LINE}"])
    fix = _run(p, f"{C.id}=fix/cc", tickets=(C,))
    assert (fix["result"] or {}).get("landed") == [C.id], f"fixture: the fix did not land\n{kit.describe(fix['run'])}"
    return {"tips": dict(p.tips), "select": select, "dry": dry, "land": land, "leftover_ran": leftover_ran,
            "full": full, "fix": fix}


def build_culprit(folder):
    """A changes the widget, B breaks the gadget, C's branch edits its own acceptance suite as the engineer (refused
    before the run). ``gov queue C``; then ``gov queue A B``."""
    told = folder / "told"
    p = kit.Planted(folder / "project", told, tickets=(A, B, C), unit=(*kit.UNIT_TESTS, base.USES_GADGET))
    _branch(p, A, "topic/aa", {module_rel("widget"): CHANGED})
    _branch(p, B, "topic/bb", {module_rel("gadget"): BROKEN})
    _branch(p, C, "topic/cc", {module_rel("mod_cc"): CHANGED,
                               C.suite_file: kit.telling(C.suite_file, told, C.modules) + "# the engineer's\n"})
    kit.self_check(p, {p.tips[A.id]: {A.node: "passed", kit.USES_WIDGET_NODE: "passed"},
                       p.tips[B.id]: {base.USES_GADGET_NODE: "failed"}})
    early = _run(p, f"{C.id}=topic/cc", tickets=(C,))
    assert "TEST_AUTHOR_REFUSED" in early["run"]["stdout"] + early["run"]["stderr"], \
        f"fixture: C is not refused before the run\n{kit.describe(early['run'])}"
    land = _run(p, f"{A.id}=topic/aa", f"{B.id}=topic/bb", tickets=(A,))
    answer = land["result"] or {}
    assert answer.get("landed") == [A.id] and B.id in json.dumps(answer.get("culprits")), \
        f"fixture: B is not the culprit beside a landed A\n{kit.describe(land['run'])}"
    return {"tips": dict(p.tips), "early": early, "land": land}


def build_merged(folder):
    """A's branch is merged into ``main`` by hand, the ticket still open. ``--select`` A; then the landing."""
    p = kit.Planted(folder / "project", folder / "told")
    tip = _branch(p, A, "topic/aa", {module_rel("widget"): CHANGED})
    kit.git(p.root, "merge", "--no-ff", "-q", "-m", "merge topic/aa by hand", "topic/aa", who=kit.ORCHESTRATOR,
            date="2026-11-01T13:00:00+00:00")
    assert kit.is_ancestor(p.root, tip, "main") and kit.status_at(p.root, "main", A.id) == "open", \
        "fixture: the branch is not merged by hand with its ticket open"
    kit.self_check(p, {"main": {A.node: "passed", kit.USES_WIDGET_NODE: "passed"}})
    arg = f"{A.id}=topic/aa"
    select = _run(p, arg, "--select", plain=True)
    land = _run(p, arg, tickets=(A,))
    assert (land["result"] or {}).get("landed") == [A.id], f"fixture: A did not land\n{kit.describe(land['run'])}"
    return {"select": select, "land": land}


BUILDS = {"main": build_main, "culprit": build_culprit, "merged": build_merged}


@pytest.fixture(scope="session")
def built(tmp_path_factory):
    return lambda name: _shared(tmp_path_factory, name, BUILDS[name])


def _result(taken):
    assert taken["result"] is not None, f"no answer\n{kit.describe(taken['run'])}"
    return taken["result"]


def _said(holder, where):
    """``holder``'s ``graph_commit``, which must be there as a full commit id."""
    assert isinstance(holder, dict), f"{where} is not there: {holder!r}"
    value = holder.get(KEY)
    assert isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value), \
        f"{where} holds no graph_commit: {value!r}; keys {sorted(holder)}"
    return value


def _merge_of_head_and_tip(taken, tip, where):
    info = taken["commit"]
    assert info is not None, f"{where}: the warm clone holds no commit {taken['result'].get(KEY)!r}"
    assert taken["head"] in info["parents"] and tip in info["parents"], \
        f"{where}: the parents {info['parents']} do not hold the head {taken['head']} and the tip {tip}"


# --------------------------------------------------------------------------
# GB-1: never behind
# --------------------------------------------------------------------------

def test_gb1_select_over_a_stale_warm_clone_selects_the_merged_tree_s_suites(built):
    taken = built("main")["select"]
    assert taken["run"]["code"] == 0, kit.describe(taken["run"])
    suites = _result(taken).get("suites")
    assert isinstance(suites, list), kit.describe(taken["run"])
    assert LEFTOVER not in suites, f"the left-over file of the stale clone is selected: {suites}"
    assert sorted(suites) == MERGED_SUITES, f"suites {sorted(suites)} are not the merged tree's {MERGED_SUITES}"


def test_gb1_the_landing_over_a_stale_warm_clone_runs_the_merged_tree_s_suites(built):
    data = built("main")
    ran = data["land"]["ran"]
    assert all(count >= 1 for count in ran.values()), f"a test one side alone holds did not run: {ran}"
    assert data["leftover_ran"] == 0, f"the left-over file ran {data['leftover_ran']} time(s)"


# --------------------------------------------------------------------------
# GB-2: the graph's commit is said
# --------------------------------------------------------------------------

def test_gb2_select_names_the_warm_clone_s_merge_of_the_head_and_the_tip(built):
    data = built("main")
    taken = data["select"]
    _said(_result(taken), "--select's object")
    _merge_of_head_and_tip(taken, data["tips"][A.id], "--select")


def test_gb2_a_dry_run_s_answer_and_select_json_name_the_commit_the_selection_was_read_from(built):
    data = built("main")
    dry = data["dry"]
    answer = _result(dry)
    said = _said(answer, "the dry run's answer")
    assert _said(dry["select_json"], "select.json") == said, \
        f"select.json says {dry['select_json'].get(KEY)}, the answer {said}"
    _merge_of_head_and_tip(dry, data["tips"][A.id], "the dry run")
    assert said == answer.get("tested"), f"no culprit: graph_commit {said} is not tested {answer.get('tested')}"


def test_gb2_a_landing_with_no_culprit_says_the_tested_commit_in_the_answer_and_queue_json(built):
    land = built("main")["land"]
    answer = _result(land)
    said = _said(answer, "the answer")
    assert said == answer.get("tested"), f"graph_commit {said} is not tested {answer.get('tested')}"
    assert _said(land["held"], "queue.json") == said, f"queue.json says {land['held'].get(KEY)}, the answer {said}"


def test_gb2_the_first_close_record_holds_the_graph_commit(built):
    land = built("main")["land"]
    front = land["close"][A.id]
    said = _said(front, "the close record")
    assert said == front.get("commit"), f"graph_commit {said} is not the record's commit {front.get('commit')}"
    assert said == _result(land).get(KEY), f"the record says {said}, the answer {_result(land).get(KEY)}"


def test_gb2_with_a_culprit_it_stays_the_commit_the_selection_was_read_from_not_the_tested_rest(built):
    data = built("culprit")
    land = data["land"]
    answer = _result(land)
    said = _said(answer, "the answer")
    assert said != answer.get("tested"), f"graph_commit is the tested rest {said}"
    info = land["commit"]
    assert info is not None, f"the warm clone holds no commit {said}"
    assert info["holds"] == {"head": True, A.id: True, B.id: True, C.id: False}, \
        f"graph_commit {said} is not the merge of the head, A and B: it holds {info['holds']}"
    assert _said(land["held"], "queue.json") == said, f"queue.json says {land['held'].get(KEY)}, the answer {said}"
    front = land["close"][A.id]
    assert _said(front, "the close record") == said, f"the record says {front.get(KEY)}, the answer {said}"
    assert front.get("commit") == answer.get("tested"), f"the record's commit {front.get('commit')}"


@pytest.mark.parametrize("which", ("select", "land"))
def test_gb2_a_branch_already_merged_says_the_integration_head(built, which):
    taken = built("merged")[which]
    said = _said(_result(taken), f"the {which} answer")
    assert said == taken["head"], f"graph_commit {said} is not the integration head {taken['head']}"
    if which == "land":
        assert _said(taken["held"], "queue.json") == said, f"queue.json says {taken['held'].get(KEY)}"
        assert _said(taken["close"][A.id], "the close record") == said, taken["close"][A.id].get(KEY)


def test_gb2_a_fix_landing_says_it_in_the_answer_and_queue_json_and_not_in_its_close_record(built):
    fix = built("main")["fix"]
    answer = _result(fix)
    said = _said(answer, "the fix landing's answer")
    assert said == answer.get("tested"), f"graph_commit {said} is not tested {answer.get('tested')}"
    assert _said(fix["held"], "queue.json") == said, f"queue.json says {fix['held'].get(KEY)}, the answer {said}"
    front = fix["close"][C.id]
    assert front is not None, "the fix landing wrote no close record"
    assert set(front) == {"id", "type", "status", "state_class", "task", "created", "fixes"}, \
        f"the fix's close record is not X6's own form: {sorted(front)}"
    assert KEY not in json.dumps(front), f"the fix's entry holds graph_commit: {front['fixes']}"


# --------------------------------------------------------------------------
# GB-2: absent where no selection is computed (each case first reads a landing that computed one)
# --------------------------------------------------------------------------

def test_gb2_with_full_there_is_no_graph_commit(built):
    data = built("main")
    _said(_result(data["land"]), "the answer of the landing without --full")
    full = data["full"]
    assert KEY not in _result(full), f"--full's answer holds graph_commit {full['result'][KEY]!r}"
    assert isinstance(full["held"], dict) and KEY not in full["held"], f"--full's queue.json: {full['held']}"
    front = full["close"][B.id]
    assert front is not None and KEY not in front, f"--full's close record: {front}"


def test_gb2_a_landing_that_ends_before_the_selection_has_no_graph_commit(built):
    data = built("culprit")
    _said(_result(data["land"]), "the answer of the landing that ran its selection")
    early = data["early"]
    for where, holder in (("the answer", early["result"]), ("queue.json", early["held"])):
        assert KEY not in (holder or {}), f"{where} of a landing ending before the selection holds {holder.get(KEY)!r}"
    assert early["close"][C.id] is None, f"a refused ticket has a close record: {early['close'][C.id]}"
