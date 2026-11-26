"""SL-5 and SL-6: the command, its plan file, its three outcomes, and what it never opens, prints or writes."""

from __future__ import annotations

import json
import os
import re
import shutil

import pytest

import w2_213_support as support


# --- SL-5: clean, findings, cannot run; writes nothing -------------------------------------------------------------

def test_sl5_the_clean_plan_is_clean_and_changes_nothing(clean_run):
    run, before, after = clean_run
    result = support.assert_clean(run)
    assert re.fullmatch(r"[0-9a-f]{40}", str(result["commit"])), f"no full commit\n{run.describe()}"
    support.assert_unchanged(before, after)


def test_sl5_the_plan_at_its_usual_place_is_not_one_of_its_own_items(own_repo, work):
    plan, _ = support.write_plan(own_repo / support.PLAN_USUAL, support.clean_lines())
    before = support.snapshot(own_repo)
    run = support.run_check(work, own_repo, plan)
    support.assert_clean(run)
    support.assert_unchanged(before, support.snapshot(own_repo))


def test_sl5_chunk_agent_and_blank_lines_change_no_result(clean_repo, clean_run, work):
    plain = support.assert_clean(clean_run[0])
    lines = [{**item, "chunk": f"c{n % 7:02d}", "agent": f"session-{n}"} for n, item in
             enumerate(support.clean_lines())]
    run, _ = support.check_lines(work, clean_repo, lines, blank_before=(0, 5, 9))
    assert support.assert_clean(run) == plain, f"chunk, agent or a blank line changed the result\n{run.describe()}"


def test_sl5_an_untracked_change_is_no_reason_not_to_run(own_repo, work):
    support.write(own_repo, "scratch-notes/c.txt", "gamma\n")
    run, _ = support.check_lines(work, own_repo, support.clean_lines())
    support.assert_clean(run)


@pytest.fixture(scope="module")
def faulty(clean_repo, tmp_path_factory):
    """One run on a plan with a fault of several kinds, blank lines among its lines."""
    lines = support.clean_lines()
    index = {item["path"]: n for n, item in enumerate(lines)}
    lines[index["notes/handbook.md"]]["destination"] = "guides/handbook.md"
    lines[index["tools/gen.py"]]["kind"] = "directory"
    lines[index["design/checkout-spec.md"]]["reason"] = ""
    lines.append(support.line("nowhere/ghost.md", "docs"))
    index["nowhere/ghost.md"] = len(lines) - 1
    lines = support.without(lines, "web/GUIDE.md")
    index = {item["path"]: n for n, item in enumerate(lines)}
    before = support.snapshot(clean_repo)
    work = tmp_path_factory.mktemp("w2-213-faulty")
    run, numbers = support.check_lines(work, clean_repo, lines, blank_before=(0, 3, 20))
    plan = sorted(work.glob("plan-*"))[0]
    text = support.run_check(work, clean_repo, plan, json_form=False)
    return run, text, {path: numbers[n] for path, n in index.items()}, before, support.snapshot(clean_repo)


EXPECTED_FAULTS = (("LAYOUT_DESTINATION", "notes/handbook.md"), ("LAYOUT_INVALID", "tools/gen.py"),
                   ("LAYOUT_INVALID", "design/checkout-spec.md"), ("LAYOUT_NO_ITEM", "nowhere/ghost.md"))


def test_sl5_each_finding_holds_its_code_plan_line_number_and_path(faulty):
    run, _text, numbers, _before, _after = faulty
    result = support.result_of(run, 1)
    for code, path in EXPECTED_FAULTS:
        support.one_finding(result, code, line=numbers[path], path=path)
    gap = support.one_finding(result, "LAYOUT_GAP", path="web/GUIDE.md")
    assert gap.get("line") is None, f"a gap has no plan line: {gap}"
    bad = [f for f in result["findings"] if not (str(f.get("code", "")).startswith("LAYOUT_") and "line" in f
                                                 and f.get("path") and f.get("message"))]
    assert not bad, f"findings without code, line, path or message: {bad}"


def test_sl5_the_text_form_prints_each_finding_with_kind_line_and_path(faulty):
    run, text, numbers, _before, _after = faulty
    support.result_of(run, 1)
    assert text.returncode == 1, f"the text form does not exit 1\n{text.describe()}"
    rows = text.stdout.splitlines()
    for code, path in EXPECTED_FAULTS:
        start = f"gov layout check: {code} line {numbers[path]}: {path}: "
        assert any(row.startswith(start) for row in rows), f"no line `{start}...`\n{text.describe()}"
    assert any(row.startswith("gov layout check: LAYOUT_GAP line -: web/GUIDE.md: ") for row in rows), (
        f"the gap's line is missing\n{text.describe()}")


def test_sl5_a_run_with_findings_changes_nothing(faulty):
    run, _text, _numbers, before, after = faulty
    support.result_of(run, 1)
    support.assert_unchanged(before, after)


def test_sl5_a_plan_line_that_is_no_json_never_ends_clean(clean_repo, work):
    lines = support.clean_lines() + ["{ this is no JSON object"]
    run, numbers = support.check_lines(work, clean_repo, lines)
    if run.returncode == 2:
        support.assert_cannot_run(run)
    else:
        result = support.result_of(run, 1)
        assert any(f.get("line") == numbers[len(lines) - 1] for f in result["findings"]), (
            f"no finding names the broken line\n{run.describe()}")


def _refused(work, root, plan, **kwargs):
    before = support.snapshot(root) if root.is_dir() else None
    run = support.run_check(work, root, plan, **kwargs)
    error = support.assert_cannot_run(run)
    assert error.get("message"), f"the refusal has no message\n{run.describe()}"
    if before:
        support.assert_unchanged(before, support.snapshot(root))
    return run


@pytest.mark.parametrize("fault", ["absent", "not-utf-8", "unreadable", "a-folder"])
def test_sl5_an_unreadable_plan_cannot_run(clean_repo, work, fault):
    plan = work / "plan.jsonl"
    if fault == "not-utf-8":
        plan.write_bytes(b'\xff\xfe{"path": "\xc3\x28"}\n')
    elif fault == "unreadable":
        support.write_plan(plan, support.clean_lines())
        plan.chmod(0)
    elif fault == "a-folder":
        plan.mkdir()
    _refused(work, clean_repo, plan)


def test_sl5_the_text_form_of_cannot_run_goes_to_standard_error(clean_repo, work):
    run = support.run_check(work, clean_repo, work / "absent.jsonl", json_form=False)
    assert run.returncode == 2 and "gov layout check: LAYOUT_CANNOT_RUN: " in run.stderr, run.describe()


@pytest.mark.parametrize("fault", ["no-repository", "no-folder"])
def test_sl5_a_non_repository_cannot_run(work, tmp_path, fault):
    root = tmp_path / "bare"
    if fault == "no-repository":
        support.write(root, "notes/handbook.md", "# Handbook\n")
    plan, _ = support.write_plan(work / "plan.jsonl", support.clean_lines())
    _refused(work, root, plan)


@pytest.mark.parametrize("fault", ["modified", "staged", "deleted"])
def test_sl5_an_uncommitted_change_to_a_tracked_file_cannot_run(own_repo, work, fault):
    path = own_repo / "docs/guide/ops.md"
    if fault == "deleted":
        path.unlink()
    else:
        path.write_text("# Operations\n\nChanged, not committed.\n", encoding="utf-8")
        if fault == "staged":
            support.git(own_repo, "add", "docs/guide/ops.md")
    plan, _ = support.write_plan(work / "plan.jsonl", support.clean_lines())
    _refused(work, own_repo, plan)


@pytest.mark.parametrize("fault", ["not-yaml", "no-mapping"])
def test_sl5_an_import_register_that_cannot_be_read_cannot_run(own_repo, work, fault):
    text = "imports: [unclosed\n" if fault == "not-yaml" else "- just\n- a list\n"
    support.add_commit(own_repo, {support.IMPORTS_REL: text})
    plan, _ = support.write_plan(work / "plan.jsonl", support.clean_lines())
    _refused(work, own_repo, plan)


@pytest.mark.parametrize("fault", ["not-yaml", "no-classes"])
def test_sl5_a_broken_standard_cannot_run(clean_repo, work, tmp_path, fault):
    assert support.STANDARD.is_file(), f"the kit holds no standard file: {support.STANDARD_REL}"
    site = tmp_path / "site"
    shutil.copytree(support.SRC / "gov", site / "gov", ignore=shutil.ignore_patterns("__pycache__"))
    shipped = site / "gov/_shipped" / support.STANDARD_REL
    assert shipped.is_file(), f"the package ships no standard: {shipped}"
    shipped.write_text("classes: [unclosed\n" if fault == "not-yaml" else "version: 1\n", encoding="utf-8")
    plan, _ = support.write_plan(work / "plan.jsonl", support.clean_lines())
    _refused(work, clean_repo, plan, src=site)


# --- SL-6: never opens, never prints ---------------------------------------------------------------------------------

def _secret_bytes():
    return [*support.SENTINELS.values(), support.fake_token(), support.fake_canary()]


def test_sl6_no_hidden_set_or_secret_named_file_is_opened(dirty_repo, work):
    """The kernel's own watch on each file: no process of the run opens or reads one, with the full plan, an empty
    plan and in the text form."""
    plan, _ = support.write_plan(work / "full.jsonl", support.dirty_lines())
    empty, _ = support.write_plan(work / "empty.jsonl", [])
    with support.watched([dirty_repo / rel for rel in support.NEVER_OPENED]) as opened:
        runs = [support.run_check(work, dirty_repo, plan), support.run_check(work, dirty_repo, empty),
                support.run_check(work, dirty_repo, plan, json_form=False)]
        seen = opened()
    for run in runs:
        assert run.returncode == 1, f"the check did not run to its findings\n{run.describe()}"
    support.result_of(runs[0], 1)
    assert not seen, f"hidden-set or secret-named files were opened: {seen}"


def test_sl6_unreadable_hidden_and_secret_files_give_the_same_result(dirty_repo, work, tmp_path):
    root = support.copy_repository(dirty_repo, tmp_path / "meadow")
    plan, _ = support.write_plan(work / "plan.jsonl", support.dirty_lines())
    readable = [support.run_check(work, root, plan), support.run_check(work, root, plan, json_form=False)]
    support.result_of(readable[0], 1)
    for rel in support.NEVER_OPENED:
        os.chmod(root / rel, 0)
    try:
        unreadable = [support.run_check(work, root, plan), support.run_check(work, root, plan, json_form=False)]
    finally:
        for rel in support.NEVER_OPENED:
            os.chmod(root / rel, 0o644)
    for before, after in zip(readable, unreadable):
        assert (after.returncode, after.stdout) == (before.returncode, before.stdout), (
            f"the result differs once the files cannot be read\n{before.describe()}\n{after.describe()}")


def test_sl6_no_output_and_no_file_holds_a_byte_of_them_only_the_path_and_the_rule(dirty_repo, work):
    plan, _ = support.write_plan(work / "plan.jsonl", support.dirty_lines())
    before = support.snapshot(dirty_repo)
    runs = [support.run_check(work, dirty_repo, plan), support.run_check(work, dirty_repo, plan, json_form=False)]
    result = support.result_of(runs[0], 1)
    support.assert_unchanged(before, support.snapshot(dirty_repo))
    secrets = _secret_bytes()
    for run in runs:
        shown = [s for s in secrets if s in run.stdout or s in run.stderr]
        assert not shown, f"planted content or a secret value is on the screen: {len(shown)}\n{run.argv}"
        assert "9f3kq" not in run.stdout + run.stderr, f"part of the secret value is on the screen\n{run.argv}"
        for rel in support.TRACKED_STOPPERS:
            assert rel in run.stdout, f"the output does not name {rel}\n{run.describe()}"
        assert "gov-canary" in run.stdout, f"the output does not name the filter's rule\n{run.describe()}"
    written = [str(path) for run in runs for path in run.sandbox.rglob("*") if path.is_file()
               and any(s.encode() in path.read_bytes() for s in secrets)]
    assert not written, f"a file written by the run holds planted content or a secret: {written}"
    stopper = [s for s in result["stoppers"] if s.get("path") == "notes/ops-handover.txt"]
    assert stopper and stopper[0].get("rule") == "gov-canary", f"the content stopper: {stopper}"
    listed = [entry.get("path") for key in ("rewrites", "kept", "held") for entry in result[key]]
    listed += [entry.get("by") for entry in result["held"]]
    read = sorted(set(listed) & set(support.NEVER_OPENED))
    assert not read, f"references were reported from files that must never be read: {read}"
    assert json.dumps(result)  # the envelope is plain JSON
