"""PM-1 to PM-3 (plan item 1-11 (c); ``.tickets/DAEO-l2b2.md`` "Fix: the landing proves the path map holds every path a
change adds exactly once"): the landing, ``--dry-run``, ``--full`` and ``--select`` refuse a candidate that adds or renames
a path the merged tree's path map holds in no namespace or in two, naming it and the line to add; a record inside a mapped
folder passes with its notice; the counts are printed as ``path_map``.

The planted projects are W2-115b's, with a narrow path map (the kit's own maps ``**``). Each is built once per session (a
file lock in pytest's shared folder, as ``conftest._shared``). Before ``gov queue`` runs, each build asks the existing
check (``python3 -m gov.check.pathmap``) what it says of the planted trees, so a red is never a broken fixture.
"""

from __future__ import annotations

import fcntl
import json
import os
import shutil
import subprocess
import sys
import traceback

import pytest
import yaml

import w2_206_support as support
from w2_206_support import A, B, C, kit, module_rel

CHANGED = "# CHANGED by the ticket\nVALUE = 2\n"
NOTE = "# A note\n\nText.\n"
DOCS, SHARED = "reference-docs", "shared-notes"     # the two namespaces that overlap on ``docs/mapped/shared-*``
DOCS_PATTERN, SHARED_PATTERN = "docs/mapped/**", "docs/mapped/shared-*"
NEW_X, NEW_Y = "docs/newfolder/x.md", "docs/newfolder/y.md"
NEW_LINE = '- "docs/newfolder/**"'
ROOT_FILE = "STRAY.md"
PLACED, MIXED_NEW = "docs/mixed/placed.md", "docs/mixed/other.md"
TWO_NEW = "docs/mapped/shared-new.md"
MAPPED_NEW = "docs/mapped/new.md"
RENAMED_FROM, RENAMED_TO = "docs/mapped/old.md", "docs/moved/old.md"
OLD_NONE, OLD_TWO, DEBT_NEW = "legacy/old.md", "docs/mapped/shared-old.md", "legacy/new.md"
# invalid to the path map check (a namespace without paths), yet read by the configuration loader every command runs
INVALID_MAP = "namespaces:\n  code: {}\n"
OTHER_INVALID_MAP = "namespaces:\n  other: {}\n"
BASE_DOCS = {"docs/mapped/kept.md": NOTE, RENAMED_FROM: "# The old note\n\nIt is moved.\n", PLACED: NOTE}


def narrow_map(*more_docs):
    """A path map that places the planted project's files and leaves other folders unmapped."""
    entry = kit.PATH_MAP["namespaces"]["all"]
    paths = {"code": ["src/**", "tests/**"], "records": [".tickets/**", "docs/close/**", "docs/checkpoints/**"],
             "governance": ["governance/**"], "root": ["README.md", ".gitignore"],
             DOCS: [DOCS_PATTERN, PLACED, *more_docs], SHARED: [SHARED_PATTERN]}
    return yaml.safe_dump({"namespaces": {name: {**entry, "paths": p} for name, p in paths.items()}}, sort_keys=False)


# --------------------------------------------------------------------------
# Building
# --------------------------------------------------------------------------

def _shared(factory, name, build):
    root = factory.getbasetemp()
    if os.environ.get("PYTEST_XDIST_WORKER"):
        root = root.parent
    folder = root / f"w2-206-pm-{name}"
    with open(root / f"w2-206-pm-{name}.lock", "w") as lock:
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


def _tracked(p, revision):
    return len(kit.git(p.root, "ls-tree", "-r", "--name-only", revision).splitlines())


def _branch(p, ticket, name, files=(), delete=(), rename=()):
    """``name`` from the base, one commit of ``ticket``'s: ``files`` written, ``delete`` removed, ``rename`` moved."""
    p.branch_from(name)
    for old, new in rename:
        (p.root / new).parent.mkdir(parents=True, exist_ok=True)
        kit.git(p.root, "mv", old, new)
    for rel in delete:
        (p.root / rel).unlink()
    tip = p.commit(f"work on {ticket.id}", kit.ENGINEER, [f"Task: {ticket.id}", "Role: engineer"], dict(files))
    p.home()
    return tip


def _check_says(p, revision):
    """``{(code, path)}`` of the existing path map check at ``revision`` (a scratch clone)."""
    scratch = support.base.scratch_at(p, revision, "pathmap")
    done = subprocess.run([sys.executable, "-m", "gov.check.pathmap"], cwd=str(scratch), env=support.env_of(p),
                          capture_output=True, text=True, timeout=120)
    shutil.rmtree(scratch, ignore_errors=True)
    assert done.returncode in (0, 1), f"fixture: the path map check did not run\n{done.stdout}\n{done.stderr}"
    return {(f["code"], f["path"]) for f in json.loads(done.stdout or "[]")}


def _expect(p, revision, expected):
    got = _check_says(p, revision)
    assert got == set(expected), f"fixture: the path map check at {revision} says {got}, not {set(expected)}"


def _record(p, taken):
    """What ``queue.json`` holds of a step's landing (None where the answer names no record)."""
    answer = support.one_object(taken["run"]["stdout"]) or {}
    rel = (answer.get("result") or {}).get("record")
    path = p.root / rel if rel else None
    return json.loads(path.read_text(encoding="utf-8")) if path and path.is_file() else None


def _close_front(p, ticket):
    text = kit.show(p.root, "main", f"docs/close/{ticket.id}/CL-{ticket.id}.md")
    return None if text is None else kit.front_matter(text)


def _tested(p, taken):
    """``(tested commit, its tracked paths' number)`` of a step's answer."""
    answer = support.one_object(taken["run"]["stdout"]) or {}
    tested = (answer.get("result") or {}).get("tested")
    for where in (p.root, p.root / kit.CLONE_REL):
        if tested and (where / ".git").exists() and kit.rev(where, tested):
            return tested, len(kit.git(where, "ls-tree", "-r", "--name-only", tested).splitlines())
    return tested, None


def build_main(folder):
    """The narrow map. ``--select`` of one branch each (and of two); ``A B --dry-run``; ``C --full``; then the landing
    ``A B`` (A adds two files under an unmapped folder, B adds a document under a mapped one)."""
    extra = {**BASE_DOCS, kit.PATH_MAP_REL: narrow_map()}
    p = kit.Planted(folder / "project", folder / "told", tickets=(A, B, C), extra=extra)
    a = _branch(p, A, "topic/aa", {module_rel("widget"): CHANGED, NEW_X: NOTE, NEW_Y: NOTE})
    b = _branch(p, B, "topic/bb", {module_rel("gadget"): CHANGED, MAPPED_NEW: NOTE})
    c = _branch(p, C, "topic/cc", {module_rel("mod_cc"): CHANGED, "docs/elsewhere/z.md": NOTE})
    tips = {
        "root": _branch(p, A, "pm/root", {ROOT_FILE: NOTE}),
        "mixed": _branch(p, A, "pm/mixed", {MIXED_NEW: NOTE}),
        "two": _branch(p, A, "pm/two", {TWO_NEW: NOTE}),
        "rename": _branch(p, A, "pm/rename", rename=[(RENAMED_FROM, RENAMED_TO)]),
        "followed": _branch(p, A, "pm/followed",
                            {NEW_X: NOTE, kit.PATH_MAP_REL: narrow_map("docs/newfolder/**")}),
        "deleted": _branch(p, A, "pm/deleted", delete=[kit.PATH_MAP_REL]),
        "spoiled": _branch(p, A, "pm/spoiled", {kit.PATH_MAP_REL: INVALID_MAP}),
    }
    none, two = "PATH_NO_NAMESPACE", "PATH_MULTIPLE_NAMESPACES"
    _expect(p, p.base, [])
    _expect(p, a, [(none, NEW_X), (none, NEW_Y)])
    _expect(p, b, [])
    _expect(p, c, [(none, "docs/elsewhere/z.md")])
    for name, found in (("root", [(none, ROOT_FILE)]), ("mixed", [(none, MIXED_NEW)]), ("two", [(two, TWO_NEW)]),
                        ("rename", [(none, RENAMED_TO)]), ("followed", []),
                        ("deleted", [("PATH_MAP_MISSING", kit.PATH_MAP_REL)]),
                        ("spoiled", [("PATH_MAP_INVALID", kit.PATH_MAP_REL)])):
        _expect(p, tips[name], found)
    kit.self_check(p, {a: {A.node: "passed", kit.USES_WIDGET_NODE: "passed"}, b: {B.node: "passed"},
                       c: {C.node: "passed"}})
    steps = {name: support.step(p, f"{A.id}=pm/{name}", "--select", plain=True) for name in tips}
    steps["newfolder"] = support.step(p, f"{A.id}=topic/aa", "--select", plain=True)
    steps["mapped"] = support.step(p, f"{B.id}=topic/bb", "--select", plain=True)
    steps["pair"] = support.step(p, f"{A.id}=topic/aa", f"{B.id}=topic/bb", "--select", plain=True)
    counts = {"followed": _tracked(p, tips["followed"]), "mapped": _tracked(p, b)}
    out = folder / "out"
    dry = support.step(p, f"{A.id}=topic/aa", f"{B.id}=topic/bb", "--dry-run", "--out", str(out))
    chosen = out / "select.json"
    dry["select_json"] = chosen.read_text(encoding="utf-8") if chosen.is_file() else None
    dry["tested"] = _tested(p, dry)
    full = support.step(p, f"{C.id}=topic/cc", "--full")
    land = support.step(p, f"{A.id}=topic/aa", f"{B.id}=topic/bb")
    land.update(record=_record(p, land), tested=_tested(p, land), close_b=_close_front(p, B),
                at_head=kit.git(p.root, "ls-tree", "-r", "--name-only", "main").splitlines(),
                status={t.id: kit.status_at(p.root, "main", t.id) for t in (A, B)})
    return {"steps": steps, "dry": dry, "full": full, "land": land, "counts": counts}


def build_debt(folder):
    """A project whose base already holds one path in no namespace and one in two. ``--select`` of a branch that adds
    another unmapped path; then the landing of a branch that only changes the two old ones (and the widget)."""
    extra = {**BASE_DOCS, kit.PATH_MAP_REL: narrow_map(), OLD_NONE: NOTE, OLD_TWO: NOTE}
    p = kit.Planted(folder / "project", folder / "told", extra=extra)
    more = _branch(p, B, "pm/more", {DEBT_NEW: NOTE, OLD_NONE: NOTE + "More.\n"})
    work = _branch(p, A, "topic/aa",
                   {module_rel("widget"): CHANGED, OLD_NONE: NOTE + "Changed.\n", OLD_TWO: NOTE + "Changed.\n"})
    old = [("PATH_NO_NAMESPACE", OLD_NONE), ("PATH_MULTIPLE_NAMESPACES", OLD_TWO)]
    _expect(p, p.base, old)
    _expect(p, work, old)
    _expect(p, more, [*old, ("PATH_NO_NAMESPACE", DEBT_NEW)])
    kit.self_check(p, {work: {A.node: "passed", kit.USES_WIDGET_NODE: "passed"}})
    select = support.step(p, f"{B.id}=pm/more", "--select", plain=True)
    land = support.step(p, f"{A.id}=topic/aa")
    land.update(record=_record(p, land), tested=_tested(p, land), close=_close_front(p, A))
    return {"select": select, "land": land}


def build_unusable(folder):
    """A project whose path map is invalid already on the base: ``--select`` of a branch that adds a path, of one that
    changes the map, and of one that only changes code."""
    p = kit.Planted(folder / "project", folder / "told", extra={kit.PATH_MAP_REL: INVALID_MAP})
    tips = {"adds": _branch(p, A, "pm/adds", {MAPPED_NEW: NOTE}),
            "changes_map": _branch(p, A, "pm/changes_map", {kit.PATH_MAP_REL: OTHER_INVALID_MAP}),
            "code_only": _branch(p, A, "pm/code_only", {module_rel("widget"): CHANGED})}
    for tip in (p.base, *tips.values()):
        _expect(p, tip, [("PATH_MAP_INVALID", kit.PATH_MAP_REL)])
    return {name: support.step(p, f"{A.id}=pm/{name}", "--select", plain=True) for name in tips}


def build_no_project(folder):
    """A project with no ``governance/project/`` (so no test map either): ``A --dry-run --full``."""
    p = kit.Planted(folder / "project", folder / "told")
    shutil.rmtree(p.root / "governance" / "project")
    p.base = p.commit("no project folder", kit.OWNER, ["Role: owner"])
    tip = _branch(p, A, "topic/aa", {module_rel("widget"): CHANGED})
    assert not kit.git(p.root, "ls-tree", "-r", "--name-only", tip, "--", "governance/project").strip(), \
        "fixture: the branch holds governance/project/"
    _expect(p, tip, [])
    out = folder / "out"
    dry = support.step(p, f"{A.id}=topic/aa", "--dry-run", "--full", "--out", str(out))
    chosen = out / "select.json"
    dry.update(record=_record(p, dry), select_json=chosen.read_text(encoding="utf-8") if chosen.is_file() else None)
    return {"dry": dry}


BUILDS = {"main": build_main, "debt": build_debt, "unusable": build_unusable, "no_project": build_no_project}


@pytest.fixture(scope="session")
def built(tmp_path_factory):
    return lambda name: _shared(tmp_path_factory, name, BUILDS[name])


# --------------------------------------------------------------------------
# Reading
# --------------------------------------------------------------------------

def _refused_select(taken, code, ticket):
    """The reason of a ``--select`` refused ``code`` for ``ticket``: exit 2, the line on stderr, no object."""
    run = taken["run"]
    assert run["code"] == 2, f"exit {run['code']}, not 2\n{kit.describe(run)}"
    prefix = f"{code}: {ticket}: "
    assert prefix in run["stderr"], f"stderr does not say '{prefix}<reason>'\n{kit.describe(run)}"
    assert support.one_object(run["stdout"]) is None, f"an object is printed on stdout\n{kit.describe(run)}"
    return run["stderr"][run["stderr"].index(prefix) + len(prefix):]


def _selected(taken):
    run = taken["run"]
    assert run["code"] == 0, f"gov queue --select exited {run['code']}, not 0\n{kit.describe(run)}"
    chosen = support.one_object(run["stdout"])
    assert chosen is not None, f"stdout is not one JSON object\n{kit.describe(run)}"
    return chosen


def _the_refusal(result, ticket):
    entries = [r for r in result.get("refused") or [] if r.get("ticket") == ticket]
    assert len(entries) == 1, f"refused holds no one entry for {ticket}: {result.get('refused')}"
    return entries[0]


def _line(tracked, none=0, two=0):
    assert isinstance(tracked, int), "the answer names no tested commit whose paths can be counted"
    return f"path map: {tracked} tracked, {none} in none, {two} in two"


# --------------------------------------------------------------------------
# PM-1: refused
# --------------------------------------------------------------------------

def test_pm1_select_refuses_an_added_path_under_no_namespace_naming_it_and_the_folder_s_line(built):
    reason = _refused_select(built("main")["steps"]["newfolder"], "PATH_NO_NAMESPACE", A.id)
    assert NEW_X in reason and NEW_Y in reason, f"the reason does not name each path:\n{reason}"
    assert NEW_LINE in reason, f"the reason does not give the line {NEW_LINE}:\n{reason}"


def test_pm1_a_root_file_s_line_to_add_is_the_path_itself(built):
    reason = _refused_select(built("main")["steps"]["root"], "PATH_NO_NAMESPACE", A.id)
    assert f'- "{ROOT_FILE}"' in reason, f"the reason does not give the path itself as the line:\n{reason}"


def test_pm1_in_a_folder_holding_placed_files_the_line_to_add_is_the_path_itself(built):
    reason = _refused_select(built("main")["steps"]["mixed"], "PATH_NO_NAMESPACE", A.id)
    assert f'- "{MIXED_NEW}"' in reason, f"the reason does not give the path itself as the line:\n{reason}"
    assert '- "docs/mixed/**"' not in reason, f"the reason offers the whole folder, which holds a placed file:\n{reason}"


def test_pm1_an_added_path_two_namespaces_hold_is_refused_naming_both_and_their_patterns(built):
    reason = _refused_select(built("main")["steps"]["two"], "PATH_MULTIPLE_NAMESPACES", A.id)
    for word in (TWO_NEW, DOCS, SHARED, DOCS_PATTERN, SHARED_PATTERN):
        assert word in reason, f"the reason does not name {word}:\n{reason}"


def test_pm1_a_rename_into_an_unmapped_folder_is_refused(built):
    reason = _refused_select(built("main")["steps"]["rename"], "PATH_NO_NAMESPACE", A.id)
    assert RENAMED_TO in reason and '- "docs/moved/**"' in reason, reason


def test_pm1_select_of_two_branches_names_the_ticket_that_adds_the_path_and_moves_and_runs_nothing(built):
    taken = built("main")["steps"]["pair"]
    reason = _refused_select(taken, "PATH_NO_NAMESPACE", A.id)
    assert MAPPED_NEW not in reason, f"the clean candidate's path is named:\n{reason}"
    assert taken["after"]["told"] == taken["before"]["told"], "a planted test ran"
    support.moved_nothing(taken)


def test_pm1_the_landing_lists_the_candidate_under_refused_with_its_code_paths_and_the_line(built):
    land = built("main")["land"]
    result = kit.answer(land["run"], kit.EXIT_NOT_ALL_LANDED)
    entry = _the_refusal(result, A.id)
    assert entry.get("code") == "PATH_NO_NAMESPACE", entry
    assert sorted(entry.get("paths") or []) == [NEW_X, NEW_Y], f"paths: {entry.get('paths')!r}"
    reason = entry.get("reason") or ""
    assert NEW_X in reason and NEW_Y in reason and NEW_LINE in reason, f"reason: {reason}"
    held = (land["record"] or {}).get("result") or {}
    assert held.get("refused") == result["refused"], f"queue.json's refused: {held.get('refused')}"


def test_pm1_the_batch_s_clean_candidate_lands_and_the_refused_one_stays_out(built):
    land = built("main")["land"]
    result = kit.answer(land["run"], kit.EXIT_NOT_ALL_LANDED)
    assert result.get("landed") == [B.id], f"landed: {result.get('landed')}"
    assert MAPPED_NEW in land["at_head"], "the clean candidate's document is not on the integration branch"
    assert not [x for x in land["at_head"] if x.startswith("docs/newfolder/")], "the refused paths were merged"
    assert land["status"] == {A.id: "open", B.id: "closed"}, land["status"]


def test_pm1_a_dry_run_refuses_it_too_and_moves_nothing(built):
    dry = built("main")["dry"]
    result = kit.answer(dry["run"], kit.EXIT_NOT_ALL_LANDED)
    entry = _the_refusal(result, A.id)
    assert entry.get("code") == "PATH_NO_NAMESPACE" and NEW_LINE in (entry.get("reason") or ""), entry
    assert result.get("landed") == [B.id], f"landed: {result.get('landed')}"
    assert kit.heads(dry["after"]) == kit.heads(dry["before"]), "a dry run moved a branch"


def test_pm1_with_full_the_candidate_is_refused_and_nothing_lands(built):
    full = built("main")["full"]
    result = kit.answer(full["run"], kit.EXIT_NOT_ALL_LANDED)
    entry = _the_refusal(result, C.id)
    assert entry.get("code") == "PATH_NO_NAMESPACE" and entry.get("paths") == ["docs/elsewhere/z.md"], entry
    assert result.get("landed") == [], f"landed: {result.get('landed')}"
    assert kit.heads(full["after"]) == kit.heads(full["before"]), "a branch moved"


def test_pm1_a_branch_that_deletes_the_path_map_is_refused_path_map_missing(built):
    _refused_select(built("main")["steps"]["deleted"], "PATH_MAP_MISSING", A.id)


def test_pm1_a_branch_that_makes_the_path_map_invalid_is_refused_path_map_invalid(built):
    _refused_select(built("main")["steps"]["spoiled"], "PATH_MAP_INVALID", A.id)


def test_pm1_under_a_map_already_unusable_a_branch_that_adds_a_path_or_changes_the_map_is_refused(built):
    for name in ("adds", "changes_map"):
        _refused_select(built("unusable")[name], "PATH_MAP_INVALID", A.id)


def test_pm1_an_added_unmapped_path_is_refused_without_naming_the_paths_already_in_none_or_two(built):
    reason = _refused_select(built("debt")["select"], "PATH_NO_NAMESPACE", B.id)
    assert DEBT_NEW in reason, reason
    assert OLD_NONE not in reason and OLD_TWO not in reason, f"a path the change does not add is named:\n{reason}"


# --------------------------------------------------------------------------
# PM-1: refuses nothing else
# --------------------------------------------------------------------------

def test_pm1_a_branch_that_adds_the_line_with_its_path_is_selected(built):
    _selected(built("main")["steps"]["followed"])


def test_pm1_changing_paths_already_in_none_or_two_refuses_nothing_and_lands(built):
    result = kit.answer(built("debt")["land"]["run"], kit.EXIT_LANDED)
    assert result.get("landed") == [A.id] and not result.get("refused"), result.get("refused")


def test_pm1_under_a_map_already_unusable_a_branch_that_only_changes_code_is_not_refused(built):
    _selected(built("unusable")["code_only"])


# --------------------------------------------------------------------------
# PM-2: a record inside a mapped folder
# --------------------------------------------------------------------------

def test_pm2_select_of_a_record_inside_a_mapped_folder_exits_0_with_the_notice(built):
    chosen = _selected(built("main")["steps"]["mapped"])
    assert f"RECORD_PLACED {MAPPED_NEW}" in (chosen.get("notices") or []), chosen.get("notices")


def test_pm2_the_landing_lands_the_record_inside_a_mapped_folder_with_the_notice(built):
    land = built("main")["land"]
    result = (support.one_object(land["run"]["stdout"]) or {}).get("result") or {}
    assert B.id in (result.get("landed") or []), kit.describe(land["run"])
    assert not [r for r in result.get("refused") or [] if r.get("ticket") == B.id], result.get("refused")
    notice = f"RECORD_PLACED {MAPPED_NEW}"
    assert notice in (result.get("notices") or []), result.get("notices")
    assert notice in ((land["record"] or {}).get("notices") or []), "queue.json holds no notice"


# --------------------------------------------------------------------------
# PM-3: the counts
# --------------------------------------------------------------------------

def test_pm3_the_select_object_holds_the_counts_of_the_merged_tree(built):
    data = built("main")
    for name in ("mapped", "followed"):
        chosen = _selected(data["steps"][name])
        assert chosen.get("path_map") == _line(data["counts"][name]), f"{name}: path_map {chosen.get('path_map')!r}"


def test_pm3_the_landing_s_answer_and_queue_json_hold_the_counts_of_the_tested_merge(built):
    land = built("main")["land"]
    result = kit.answer(land["run"], kit.EXIT_NOT_ALL_LANDED)
    want = _line(land["tested"][1])
    assert result.get("path_map") == want, f"the answer's path_map {result.get('path_map')!r} is not {want!r}"
    held = (land["record"] or {}).get("result") or {}
    assert held.get("path_map") == want, f"queue.json's path_map: {held.get('path_map')!r}"


def test_pm3_the_close_record_holds_the_counts(built):
    land = built("main")["land"]
    assert land["close_b"] is not None, f"no close record for {B.id}\n{kit.describe(land['run'])}"
    want = _line(land["tested"][1])
    assert land["close_b"].get("path_map") == want, f"path_map {land['close_b'].get('path_map')!r} is not {want!r}"


def test_pm3_a_dry_run_s_answer_and_select_json_hold_the_counts(built):
    dry = built("main")["dry"]
    result = kit.answer(dry["run"], kit.EXIT_NOT_ALL_LANDED)
    want = _line(dry["tested"][1])
    assert result.get("path_map") == want, f"the answer's path_map {result.get('path_map')!r} is not {want!r}"
    chosen = support.one_object(dry["select_json"] or "") or {}
    assert chosen.get("path_map") == want, f"select.json's path_map: {chosen.get('path_map')!r}"


def test_pm3_a_project_with_a_path_already_in_none_and_one_in_two_lands_and_counts_them(built):
    land = built("debt")["land"]
    result = kit.answer(land["run"], kit.EXIT_LANDED)
    want = _line(land["tested"][1], none=1, two=1)
    assert result.get("path_map") == want, f"the answer's path_map {result.get('path_map')!r} is not {want!r}"
    assert ((land["record"] or {}).get("result") or {}).get("path_map") == want, "queue.json's path_map"
    assert (land["close"] or {}).get("path_map") == want, f"the close record: {land['close']}"


def test_pm3_a_project_with_no_project_folder_has_no_path_map(built):
    dry = built("no_project")["dry"]
    result = kit.answer(dry["run"], kit.EXIT_LANDED)
    assert result.get("landed") == [A.id], result
    chosen = support.one_object(dry["select_json"] or "")
    assert chosen is not None, "no select.json"
    held = (dry["record"] or {}).get("result")
    assert held is not None, "no queue.json"
    for where, value in (("the answer", result), ("queue.json", held), ("select.json", chosen)):
        assert "path_map" not in value, f"{where} holds path_map: {value.get('path_map')!r}"
