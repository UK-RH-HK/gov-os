"""The queue's selection and two findings of the first integration (README, "Fix: select I-1 and I-2").

I-1: a test file the branch deletes is no selected target (``deleted``), a target the test map names that is gone
still refuses ``FILE_GONE``. I-2: a record-only document the branch writes that nothing places is placed with a
notice (``records``, ``RECORD_PLACED <path>`` under ``notices``); code or a Markdown file under ``src/`` or
``template/`` that nothing places still refuses.

Each case plants a project (``w2_115b_support.Planted``), a green nightly record naming its first commit, and A's
branch ``topic/aa`` forked after it. ``gov queue PROJ-aaaa=topic/aa --select`` and the landing (``--json``) are run as
programs.
"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest
import yaml

import w2_115b_support as support
from w2_115b_support import A, ORCHESTRATOR, module_rel

EXIT_SELECT_REFUSED = 2
CHANGED = "# CHANGED by the ticket\nVALUE = 2\n"
WIDGET = {module_rel("widget"): CHANGED}        # mapped code: A's suite holds it, a unit test imports it
DOC = "docs/x.md"                                # outside record_only, placed by nothing
STRAY = "tools/stray.sh"
FOLDER = "tests/suite_x/"                        # a suite folder with two test files; the branch deletes the first
ONE, TWO = FOLDER + "test_one.py", FOLDER + "test_two.py"
GONE = "tests/gone/test_gone.py"                 # the only file of its folder, named by a coupling


def _suite_files(told):
    return {ONE: support.telling(ONE, told, ["gizmo"]), TWO: support.telling(TWO, told, ["widget"])}


def _map(coupling=None):
    test_map = dict(support.TEST_MAP)
    if coupling:
        test_map["couplings"] = [coupling]
    return {support.TEST_MAP_REL: yaml.safe_dump(test_map, sort_keys=False)}


def _plant(planted, tmp_path, files=None, delete=(), extra=None):
    """A green night after the planted commit; A's branch ``topic/aa``: one commit of A's writing ``files`` (the
    widget by default) and deleting ``delete``."""
    told = tmp_path / "told"
    p = planted(extra={**_suite_files(told), GONE: support.telling(GONE, told, ["gizmo"]), **(extra or {})})
    green = p.base
    p.commit("a green night", ORCHESTRATOR, ["Role: orchestrator"],
             {f"docs/close/nightly/NR-20261101T010000Z-{green[:12]}.json":
              json.dumps({"verdict": "green", "head": green}) + "\n"})
    p.branch_from("topic/aa")
    for rel in delete:
        (p.root / rel).unlink()
    p.work(A, WIDGET if files is None else files)
    p.record_branch(A, "topic/aa")
    p.home()
    return p


def _program(project, *args):
    env = support.base_env(project.root.parent / f"{project.root.name}-env")
    cmd = [sys.executable, "-m", "gov.cli.main", *args, "--root", str(project.root)]
    done = subprocess.run(cmd, cwd=str(project.root), env=env, capture_output=True, text=True,
                          timeout=support.GOV_TIMEOUT_S, stdin=subprocess.DEVNULL)
    return {"args": list(args), "code": done.returncode, "stdout": done.stdout, "stderr": done.stderr}


def _select(project):
    return _program(project, "queue", f"{A.id}=topic/aa", "--select")


def _object(run):
    assert run["code"] == 0, f"exit {run['code']}, not 0\n{support.describe(run)}"
    try:
        chosen = json.loads(run["stdout"])
    except ValueError:
        raise AssertionError(f"stdout is not one JSON object\n{support.describe(run)}") from None
    assert isinstance(chosen, dict), support.describe(run)
    return chosen


def _refused(run, *named, unnamed=()):
    assert run["code"] == EXIT_SELECT_REFUSED, f"exit {run['code']}, not 2\n{support.describe(run)}"
    assert "SELECTION_REFUSED" in run["stderr"], support.describe(run)
    for rel in named:
        assert rel in run["stderr"], f"the refusal does not name {rel}\n{support.describe(run)}"
    for rel in unnamed:
        assert rel not in run["stderr"], f"the refusal names {rel}\n{support.describe(run)}"


def _assert_lands(p, extra_checks=None):
    old_head = support.rev(p.root, "main")
    result = support.answer(support.run_queue(p, f"{A.id}=topic/aa"), support.EXIT_LANDED)
    assert result.get("landed") == [A.id], f"landed: {result.get('landed')}"
    support.assert_landed_through_close_commits(p, result, "main", old_head)
    head = support.rev(p.root, "main")
    assert support.status_at(p.root, head, A.id) == "closed"
    return result


# -- I-1: a deleted test file is no target ------------------------------------------------------------------------------

def test_a_deleted_test_file_is_listed_under_deleted_not_selected_and_its_folder_still_runs(planted, tmp_path):
    p = _plant(planted, tmp_path, delete=[ONE])
    chosen = _object(_select(p))
    assert chosen.get("deleted") == [ONE], f"deleted: {chosen.get('deleted')!r}"
    suites = chosen.get("suites", [])
    assert not [s for s in suites if s == ONE], f"the deleted file is selected: {suites}"
    assert A.acceptance in suites or any(s.startswith(A.acceptance) for s in suites), f"A's suite: {suites}"
    assert any(s == TWO or s.rstrip("/") == FOLDER.rstrip("/") for s in suites), f"the folder's rest: {suites}"


def test_the_landing_beside_a_deleted_test_file_lands_and_closes(planted, tmp_path):
    p = _plant(planted, tmp_path, delete=[ONE])
    support.self_check(p, {p.tips[A.id]: {A.node: "passed", support.node(TWO): "passed"}})
    _assert_lands(p)


def test_deleted_is_present_and_empty_when_the_change_deletes_nothing(planted, tmp_path):
    p = _plant(planted, tmp_path)
    assert _object(_select(p)).get("deleted") == []


def test_a_map_named_target_the_branch_deletes_still_refuses_file_gone(planted, tmp_path):
    coupling = {"paths": [module_rel("widget")], "suites": [GONE], "why": "the planted coupling"}
    p = _plant(planted, tmp_path, delete=[GONE], extra=_map(coupling))
    support.self_check(p, {p.base: {A.node: "passed"}})
    run = _select(p)
    _refused(run, GONE)
    assert "FILE_GONE" in run["stderr"], support.describe(run)


# -- I-2: a record-only document is placed with a notice -----------------------------------------------------------------

def test_a_document_nothing_places_is_a_record_with_a_notice_and_select_exits_0(planted, tmp_path):
    p = _plant(planted, tmp_path, {**WIDGET, DOC: "# a note\n"})
    chosen = _object(_select(p))
    assert chosen.get("records") == [DOC], f"records: {chosen.get('records')!r}"
    assert f"RECORD_PLACED {DOC}" in (chosen.get("notices") or []), f"notices: {chosen.get('notices')!r}"
    assert A.acceptance in chosen.get("suites", []), f"A's own suite is not selected: {chosen.get('suites')}"


def test_the_landing_places_the_record_and_holds_the_notice_in_its_answer_and_the_queue_record(planted, tmp_path):
    p = _plant(planted, tmp_path, {**WIDGET, DOC: "# a note\n"})
    support.self_check(p, {p.tips[A.id]: {A.node: "passed", support.USES_WIDGET_NODE: "passed"}})
    result = _assert_lands(p)
    notice = f"RECORD_PLACED {DOC}"
    assert notice in (result.get("notices") or []), f"answer notices: {result.get('notices')!r}"
    rel = result.get("record") or ""
    held = json.loads((p.root / rel).read_text(encoding="utf-8"))
    assert notice in (held.get("notices") or []), f"the queue record's notices: {held.get('notices')!r}"


def test_code_beside_a_record_is_refused_naming_the_code_and_not_the_record(planted, tmp_path):
    p = _plant(planted, tmp_path, {**WIDGET, DOC: "# a note\n", STRAY: "#!/bin/sh\necho stray\n"})
    _refused(_select(p), STRAY, unnamed=[DOC])


@pytest.mark.parametrize("path", ["src/app/NOTES.md", "template/guide.md"])
def test_a_markdown_file_under_src_or_template_that_nothing_places_still_refuses(planted, tmp_path, path):
    p = _plant(planted, tmp_path, {**WIDGET, DOC: "# a note\n", path: "# not a record\n"})
    _refused(_select(p), path, unnamed=[DOC])
