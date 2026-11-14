"""W2-94 (DAEO-g87r), reopened 2026-11-14: the launch script's one-question fix flow (S6-S12, F4-F6; DEC-1180 (2)).

Written from the KPI lines and the lead's interface text, never from the engineer's work. Every case runs the script
(``indep_launch.py``) as a process on a planted world (``w2_94_fix_support.FixWorld``) with the stub ``claude``. Planted
words begin with ``zqxw94``. Nothing under ``~/gov-os-eval`` or ``~/gov-os-runs`` is opened.
"""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import tarfile

import pytest
import yaml

from w2_94_fix_support import (CODE, DROP, FIX_CODES, FIXTURE, LATEST, NEW_Q02, OLD_Q02_MARK, ROOT, SAMPLE_OF, SCRIPT,
                               SETN, VARIANT_REL, VARIANT_SHA, WALLS, FixWorld, good_out, indep_launch, result_json,
                               schema, sha, tree_hash, writer_out)


@pytest.fixture
def fw(tmp_path):
    return FixWorld(tmp_path)


def ran(w, *a, **kw):
    """One fix run: (rc, counts, process)."""
    return w.fix(*a, **kw)


def unchanged(w, before, what):
    after = w.state()
    changed = sorted({k for part in before for k in set(before[part]) | set(after[part])
                      if before[part].get(k) != after[part].get(k)})
    assert not changed, f"{what}: something was built or changed: {changed[:6]}"


# =====================================================================================================================
# the approved variant is the one the cases run
# =====================================================================================================================
def test_the_variant_fixture_is_the_approved_variant_byte_for_byte():
    assert sha(FIXTURE.read_bytes()) == VARIANT_SHA


# =====================================================================================================================
# S6 -- the flags
# =====================================================================================================================
BAD_IDS = ["q2", "Q02", "q002", "q0a", "q", "", "q02\n", " q02", "q02 ", "q-2", "q02x", "xq02", "q٠٢", "02"]
BAD_CODES = ["UNKNOWN", "answer_not_in_spans", "Answer_Not_In_Spans", "ANSWER_NOT_IN_SPANS\n", " ANSWER_NOT_IN_SPANS",
             "", "ANSWER", "ANSWER_NOT_IN_SPANS_X", "SPAN_OUT_OF_FILE,HEADING_NOT_FOUND"]


def test_s6_each_wrong_form_is_17_with_nothing_built_and_the_good_form_is_not(fw):
    before = fw.state()
    forms = {"fix alone": dict(reason=None), "reason alone": dict(fix=None),
             "kind checker": dict(kind="checker"), "kind auditor": dict(kind="auditor", audit="e0"),
             "round 1": dict(rnd=1), "no --round": dict(rnd=None), "round 3": dict(rnd=3)}
    forms.update({f"bad id {i!r}": dict(fix=i) for i in BAD_IDS})
    forms.update({f"bad code {c!r}": dict(reason=c) for c in BAD_CODES})
    wrong = {}
    for name, kw in forms.items():
        rc, counts, _ = fw.fix(**kw)
        if rc != 17 or counts.get("code") != 17:
            wrong[name] = rc
    # the counts-only flow takes no fix flag
    rc, counts, _ = fw.run("--sets-root", str(fw.sets), "--kind", "writer", "--run", LATEST, "--counts-only",
                           "--fix", "q02", "--reason", CODE)
    if rc != 17:
        wrong["--counts-only with the flags"] = rc
    assert not wrong, f"not refused 17: {wrong}"
    unchanged(fw, before, "a refused argument form")
    # the corrected form passes the argument stage (a dry run builds its wall)
    rc, counts, p = fw.dry_fix()
    assert rc == 0, p.stderr
    assert counts["status"] == "dry"


@pytest.mark.parametrize("code", FIX_CODES)
def test_s6_each_of_the_eight_codes_and_the_edge_ids_pass_the_argument_stage(fw, code):
    # a question that is not in the set is refused 10 at staging: a refusal later than the argument stage
    before = fw.state()
    for qid in ("q99", "q00"):
        rc, counts, p = fw.fix(fix=qid, reason=code)
        assert rc == 10, (qid, code, rc, p.stderr)
    unchanged(fw, before, "a staging refusal")


# =====================================================================================================================
# S7 / F4 -- the staging
# =====================================================================================================================
@pytest.fixture(scope="module")
def dry(tmp_path_factory):
    w = FixWorld(tmp_path_factory.mktemp("fixdry"))
    rc, counts, p = w.dry_fix()
    assert rc == 0, p.stderr
    return w, counts, p, w.wall(counts)


EXPECTED_WALL = sorted(["seed.txt", "brief.md", "CLAUDE.md", "WALL.json", "input/selection.json",
                        ".claude/settings.json", ".claude/wall_hook.py", "input/q02.yaml", "input/verdict.txt",
                        "input/sample.json"])


def test_s7_the_wall_holds_the_seven_fixed_files_the_three_inputs_and_an_empty_out(dry):
    w, counts, p, wall = dry
    files, dirs, links = w.wall_listing(wall)
    assert links == []
    assert files == EXPECTED_WALL
    assert dirs == [".claude", "input", "out"]
    assert os.listdir(wall / "out") == []


def test_s7_the_question_is_a_byte_copy_and_the_verdict_is_one_line(dry):
    w, counts, p, wall = dry
    assert (wall / "input" / "q02.yaml").read_bytes() == (w.setdir / "hidden" / "q02.yaml").read_bytes()
    assert (wall / "input" / "verdict.txt").read_bytes() == f"q02 {CODE}\n".encode()


def test_s7_the_sample_is_the_latest_delivered_round_one_run_of_the_set_in_order(dry):
    w, counts, p, wall = dry
    got = json.loads((wall / "input" / "sample.json").read_text())
    assert got == {"sample": SAMPLE_OF[LATEST]}
    for other in (set(SAMPLE_OF) - {LATEST}):
        assert got["sample"] != SAMPLE_OF[other]


def test_f4_no_other_file_of_the_set_reaches_the_wall(dry):
    w, counts, p, wall = dry
    texts = {}
    for rel in w.wall_listing(wall)[0]:
        texts[rel] = (wall / rel).read_bytes()
    found = {(rel, m) for rel, data in texts.items() for m in w.other_markers if m.encode() in data}
    assert not found, sorted(found)
    holders = [rel for rel, data in texts.items() if OLD_Q02_MARK.encode() in data]
    assert holders == ["input/q02.yaml"]
    # the other runs' samples are not staged either
    sample_text = (wall / "input" / "sample.json").read_text()
    for rid, sample in SAMPLE_OF.items():
        if rid != LATEST:
            assert not any(s in sample_text for s in sample)


def test_s7_a_dry_runs_counts_carry_the_fix_and_no_content(dry):
    w, counts, p, wall = dry
    want = {"id": "q02", "code": CODE, "action": None}
    assert counts["fix"] == want
    assert json.loads((w.runs / "writer" / counts["run"] / "counts.json").read_text())["fix"] == want
    assert w.leaks((counts, p)) == []


def _break_q02_absent(w):
    (w.setdir / "hidden" / "q02.yaml").unlink()


def _break_q02_link(w):
    p = w.setdir / "hidden" / "q02.yaml"
    (w.setdir / "hidden" / "elsewhere.yaml").write_text("id: q02\n")
    p.unlink()
    os.symlink("elsewhere.yaml", p)


def _break_q02_folder(w):
    p = w.setdir / "hidden" / "q02.yaml"
    p.unlink()
    p.mkdir()
    (p / "x").write_text("x\n")


def _break_hidden_link(w):
    hidden = w.setdir / "hidden"
    hidden.rename(w.setdir / "hidden-real")
    os.symlink("hidden-real", hidden)


def _break_no_run_records(w):
    import shutil
    shutil.rmtree(w.runs / "writer")


def _break_no_delivered_round1_of_the_set(w):
    from w2_94_fix_support import OLDER
    w.plant_run(OLDER, status="rejected")
    w.plant_run(LATEST, status="rejected")  # the round 2 of the set and a round 1 of another set stay delivered


def _break_archive_missing(w):
    w.tar_path(LATEST).unlink()


def _break_member(members):
    return lambda w: w.plant_run(LATEST, members=members)


def _sel(text):
    return [("input/selection.json", text if isinstance(text, bytes) else text.encode())]


STAGING_BREAKS = {
    "hidden file absent": _break_q02_absent,
    "hidden file a link": _break_q02_link,
    "hidden file a folder": _break_q02_folder,
    "hidden folder a link": _break_hidden_link,
    "no run records at all": _break_no_run_records,
    "no delivered round-1 run of the set": _break_no_delivered_round1_of_the_set,
    "the latest run's archive missing": _break_archive_missing,
    "member missing": _break_member([("brief.md", b"x\n")]),
    "member not JSON": _break_member(_sel("not json at all")),
    "member a list": _break_member(_sel("[]")),
    "member without sample": _break_member(_sel('{"changed": []}')),
    "sample a string": _break_member(_sel('{"sample": "docs/a.md"}')),
    "sample not strings": _break_member(_sel('{"sample": [1, 2]}')),
    "sample with one non-string": _break_member(_sel('{"sample": ["docs/a.md", 2]}')),
    "sample null": _break_member(_sel('{"sample": null}')),
    "member a link": _break_member([("input/selection.json", ("link", "../brief.md")), ("brief.md", b"x\n")]),
}


@pytest.mark.parametrize("name", list(STAGING_BREAKS))
def test_s7_a_missing_or_bad_input_is_10_with_nothing_built(fw, name):
    STAGING_BREAKS[name](fw)
    before = fw.state()
    rc, counts, p = fw.dry_fix()
    assert rc == 10, (rc, p.stderr)
    assert counts["status"] == "refused"
    unchanged(fw, before, name)


# =====================================================================================================================
# S8 / F5 -- the delivery
# =====================================================================================================================
def _good_run(w, action="corrected", **changes):
    w.session(good_out(action, **changes))
    before_files = w.set_files()
    old = (w.setdir / "hidden" / "q02.yaml").read_bytes()
    rc, counts, p = w.fix()
    return rc, counts, p, before_files, old


@pytest.mark.parametrize("action,extra", [("corrected", {}), ("replaced", {}), ("replaced", {"stopped": "none"})])
def test_s8_a_good_fix_run_replaces_only_hidden_q02_and_packs_the_old_file(fw, action, extra):
    rc, counts, p, before, old = _good_run(fw, action, **extra)
    assert rc == 0, (counts, p.stderr)
    assert counts["status"] == "delivered"
    after = fw.set_files()
    changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    assert changed == ["fixtures/evaluation/examin/hidden/q02.yaml"], changed
    assert (fw.setdir / "hidden" / "q02.yaml").read_bytes() == NEW_Q02.encode()
    run = counts["run"]
    names = fw.tar_names(run)
    assert [n for n in names if f"{run}/replaced-hidden/" in n and not n.endswith("replaced-hidden")] == [
        f"{run}/replaced-hidden/q02.yaml"]
    assert fw.tar_bytes(run, "replaced-hidden/q02.yaml") == old
    # the replaced file is nowhere under the set, and no temporary name is left
    for folder, _d, files in os.walk(fw.setdir):
        for f in files:
            assert OLD_Q02_MARK.encode() not in (open(os.path.join(folder, f), "rb").read())
    assert not [n for n in after if n.endswith(".tmp") or ".r2-" in n or ".old" in n]


@pytest.mark.parametrize("action,extra", [("corrected", {}), ("replaced", {"stopped": "none"})])
def test_s9_on_delivery_the_counts_carry_the_fix_and_no_content(fw, action, extra):
    rc, counts, p, _, _ = _good_run(fw, action, **extra)
    assert rc == 0, (counts, p.stderr)
    assert counts["fix"] == {"id": "q02", "code": CODE, "action": action}
    on_disk = json.loads((fw.runs / "writer" / counts["run"] / "counts.json").read_text())
    assert on_disk["fix"] == counts["fix"]
    assert fw.leaks((counts, p)) == []


def _hook_link_q02(w):
    elsewhere = w.tmp / "elsewhere.yaml"
    elsewhere.write_text("id: q02\nmarker: x\n")
    return [f"p = os.path.join(wall, 'out', 'q02.yaml')", "os.unlink(p)", f"os.symlink({str(elsewhere)!r}, p)"]


DELIVERY_BREAKS = {
    "an extra file": (dict(out=lambda w: {**good_out(), "out/extra.txt": "x\n"})),
    "an extra folder with a file": (dict(out=lambda w: {**good_out(), "out/sub/x.txt": "x\n"})),
    "an empty extra folder": dict(hook=lambda w: ["os.mkdir(os.path.join(wall, 'out', 'empty'))"]),
    "an extra link": dict(hook=lambda w: ["os.symlink('result.json', os.path.join(wall, 'out', 'extra'))"]),
    "conflicts.md without a stop": dict(out=lambda w: {**good_out(), "out/conflicts.md": "classes only\n"}),
    "q02.yaml absent": dict(out=lambda w: {"out/result.json": result_json()}),
    "q02.yaml a link": dict(hook=_hook_link_q02),
    "q02.yaml a folder": dict(hook=lambda w: ["p = os.path.join(wall, 'out', 'q02.yaml')", "os.unlink(p)",
                                              "os.mkdir(p)"]),
    "not YAML": dict(q02="id: [unclosed\n"),
    "a YAML list": dict(q02="- id: q02\n- b\n"),
    "a YAML scalar": dict(q02="just some text\n"),
    "an empty document": dict(q02=""),
    "no id": dict(q02="question: x\n"),
    "another id": dict(q02="id: q03\nquestion: x\n"),
    "the id in another case": dict(q02="id: Q02\nquestion: x\n"),
    "an unsafe tag": dict(q02="id: q02\nboom: !!python/object/apply:os.mkdir [{proof}]\n", proof=True),
    "an unsafe tag as the id": dict(q02="!!python/object/apply:os.mkdir [{proof}]\n", proof=True),
}


@pytest.mark.parametrize("name", list(DELIVERY_BREAKS))
def test_s8_f5_a_delivery_refusal_is_20_and_leaves_every_set_file_unchanged(fw, name):
    spec = DELIVERY_BREAKS[name]
    proof = fw.tmp / "proof-of-unsafe-load"
    if "q02" in spec:
        out = {"out/q02.yaml": spec["q02"].replace("{proof}", json.dumps(str(proof))),
               "out/result.json": result_json()}
    elif "out" in spec:
        out = spec["out"](fw)
    else:
        out = good_out()
    env = fw.session(out, hook_lines=spec["hook"](fw) if "hook" in spec else None)
    before = fw.set_files()
    rc, counts, p = fw.fix(extra=env)
    assert rc == 20, (counts, p.stderr)
    assert counts["status"] == "rejected"
    assert fw.set_files() == before
    assert OLD_Q02_MARK.encode() in (fw.setdir / "hidden" / "q02.yaml").read_bytes()
    if spec.get("proof"):
        assert not proof.exists(), "the YAML was loaded with an unsafe loader"


# =====================================================================================================================
# S9 -- the result
# =====================================================================================================================
BAD_RESULTS = {
    "no action": dict(action=DROP),
    "action null": dict(action=None),
    "action another word": dict(action="fixed"),
    "action in another case": dict(action="Corrected"),
    "action empty": dict(action=""),
    "action a list": dict(action=["corrected"]),
    "questions 0": dict(questions=0),
    "questions 2": dict(questions=2),
    "questions a string": dict(questions="1"),
    "questions true": dict(questions=True),
    "questions absent": dict(questions=DROP),
    "by_kind sums to 2": dict(by_kind={"location": 1, "fact": 1}),
    "by_kind sums to 0": dict(by_kind={"location": 0}),
    "by_kind empty": dict(by_kind={}),
    "by_kind one entry of 2": dict(by_kind={"location": 2}),
    "by_area sums to 2": dict(by_area={"code": 1, "docs": 1}),
    "by_area sums to 0": dict(by_area={"code": 0}),
    "by_area empty": dict(by_area={}),
    "by_area one entry of 2": dict(by_area={"code": 2}),
    "by_kind absent": dict(by_kind=DROP),
    "by_area absent": dict(by_area=DROP),
    "by_kind an unknown key": dict(by_kind={"bogus": 1}),
    "by_area an unknown key": dict(by_area={"bogus": 1}),
    "by_kind a negative number": dict(by_kind={"location": 2, "fact": -1}),
}


@pytest.mark.parametrize("name", list(BAD_RESULTS))
def test_s9_a_result_of_a_wrong_form_is_20_nothing_delivered_and_the_action_null(fw, name):
    fw.session({"out/q02.yaml": NEW_Q02, "out/result.json": result_json(**BAD_RESULTS[name])})
    before = fw.set_files()
    rc, counts, p = fw.fix()
    assert rc == 20, (counts, p.stderr)
    assert counts["status"] == "rejected"
    assert fw.set_files() == before
    assert counts["fix"] == {"id": "q02", "code": CODE, "action": None}
    assert fw.leaks((counts, p)) == []


@pytest.mark.parametrize("result", [dict(), dict(action=DROP, questions=DROP, by_kind=DROP, by_area=DROP),
                                    dict(action="fixed")])
def test_s9_a_stopped_result_is_21_and_delivers_nothing(fw, result):
    body = json.loads(result_json(stopped="decisions-conflict", **result))
    fw.session({"out/q02.yaml": NEW_Q02, "out/result.json": json.dumps(body), "out/conflicts.md": "path classes\n"})
    before = fw.set_files()
    rc, counts, p = fw.fix()
    assert rc == 21, (counts, p.stderr)
    assert counts["status"] == "stopped"
    assert fw.set_files() == before
    assert counts["fix"] == {"id": "q02", "code": CODE, "action": None}
    assert fw.leaks((counts, p)) == []


def test_s9_a_stop_without_a_question_file_is_21_too(fw):
    fw.session({"out/result.json": json.dumps({"stopped": "input-missing"}), "out/conflicts.md": "path classes\n"})
    before = fw.set_files()
    rc, counts, p = fw.fix()
    assert rc == 21 and fw.set_files() == before


# =====================================================================================================================
# S10 / F6 -- the approved variant, end to end
# =====================================================================================================================
def test_s10_the_approved_variant_runs_end_to_end_byte_for_byte(fw):
    assert sha(fw.blob(fw.commit, VARIANT_REL)) == VARIANT_SHA
    fw.session(good_out("corrected"))
    rc, counts, p = fw.fix()
    assert rc == 0, (counts, p.stderr)
    assert counts["brief_sha256"] == VARIANT_SHA
    assert counts["status"] == "delivered"
    assert (fw.setdir / "hidden" / "q02.yaml").read_bytes() == NEW_Q02.encode()
    run = counts["run"]
    assert fw.tar_bytes(run, "brief.md") == FIXTURE.read_bytes()
    # the front matter names no sample: the wall's own selection holds an empty one
    assert json.loads(fw.tar_bytes(run, "input/selection.json"))["sample"] == []
    # the session saw exactly the three inputs and the selection
    assert fw.calls()[-1]["input"] == ["q02.yaml", "sample.json", "selection.json", "verdict.txt"]
    assert yaml.safe_load(NEW_Q02)["id"] == "q02"


def test_s10_a_fix_run_still_checks_the_brief_as_approved(fw):
    before = fw.state()
    flipped = ("0" if VARIANT_SHA[0] != "0" else "1") + VARIANT_SHA[1:]
    wrong = {"bytes differ from the sha": dict(brief_sha=flipped),
             "another brief's bytes": dict(brief="governance/project/indep-briefs/writer.md"),
             "a brief that is not in the commit": dict(brief="governance/project/indep-briefs/none.md")}
    got = {name: fw.dry_fix(**kw)[0] for name, kw in wrong.items()}
    assert got == {name: 10 for name in wrong}
    unchanged(fw, before, "a brief refusal")
    rc, counts, p = fw.dry_fix()
    assert rc == 0, p.stderr


def test_s10_a_variant_not_in_the_approved_list_is_refused_10(tmp_path):
    w = FixWorld(tmp_path, listed=False)
    before = w.state()
    rc, counts, p = w.dry_fix()
    assert rc == 10, p.stderr
    unchanged(w, before, "an unlisted brief")


def test_s10_without_fix_the_variants_front_matter_is_refused_10_as_today(fw):
    # green today and after: nothing about the front matter changes without --fix (no `sample:` there)
    before = fw.state()
    rc, counts, p = fw.fix(fix=None, reason=None, dry=True, seed=3)
    assert rc == 10, p.stderr
    unchanged(fw, before, "a plain round 2 with the variant")


# =====================================================================================================================
# S11 -- the usage line; the walls and the briefs unchanged, of the schemas only the counts schema changed (S13)
# =====================================================================================================================
def _doc():
    return ast.get_docstring(ast.parse(SCRIPT.read_text()), clean=False)


def test_s11_the_docstring_has_one_fix_usage_line_naming_only_the_sets_root():
    lines = [ln.strip() for ln in _doc().splitlines() if "--fix" in ln and "--reason" in ln]
    assert len(lines) == 1, lines
    line = lines[0]
    words = line.split()
    assert words.count("--sets-root") == 1
    root = words[words.index("--sets-root") + 1]
    assert WALLS + "/" not in line and "fixtures/evaluation" not in line
    assert not any(c in line for c in "$*?[{<>|;&`"), line
    assert not [w for w in words if w != root and w.startswith(root.rstrip("/") + "/")]
    assert "--kind writer" in line and "--round 2" in line
    for flag in ("--brief", "--brief-sha256", "--commit", "--set"):
        assert flag in words
    assert re.fullmatch(r"q[0-9]{2}", words[words.index("--fix") + 1])
    assert words[words.index("--reason") + 1] in FIX_CODES


def _git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, timeout=120)


COUNTS_SCHEMA_REL = "governance/project/orchestration/tools/indep-schemas/indep-counts.schema.json"


def test_s11_f6_the_branch_changes_no_wall_or_brief_file_and_of_the_schemas_only_the_counts_schema():
    # S13 (2026-11-14) changes indep-counts.schema.json by this ticket: it alone may differ under indep-schemas/
    ref = _git("rev-parse", "--verify", "--quiet", "w2/integrate")
    if ref.returncode != 0:
        pytest.skip("w2/integrate is not a ref in this repository")
    base = _git("merge-base", "HEAD", "w2/integrate").stdout.strip()
    assert base
    guarded = ["governance/project/indep-walls/", "governance/project/indep-briefs/",
               "governance/project/orchestration/tools/indep-schemas/"]
    changed = _git("diff", "--name-only", base, "--", *guarded).stdout.split()
    untracked = _git("ls-files", "--others", "--exclude-standard", "--", *guarded).stdout.split()
    assert [c for c in changed if c != COUNTS_SCHEMA_REL] == [] and untracked == [], (changed, untracked)


# =====================================================================================================================
# S12 -- without --fix a writer round 2 is as before
# =====================================================================================================================
def test_s12_a_writer_round_two_without_fix_stages_the_whole_set_and_replaces_the_whole_hidden(fw):
    fw.stub({"session": "write", "out": writer_out()})
    rc, counts, p = fw.run(*fw.args("writer", rnd=2, set_name=SETN))
    assert rc == 0, (counts, p.stderr)
    run = counts["run"]
    assert "fix" not in counts
    assert "fix" not in json.loads((fw.runs / "writer" / run / "counts.json").read_text())
    assert indep_launch.schema_ok(counts, schema())
    names = fw.tar_names(run)
    for want in ("input/set/q03.yaml", "input/set/visible/q07.yaml", "input/set/dropped/q09.yaml", "input/notes.md",
                 "replaced-hidden/q03.yaml", "replaced-hidden/DRAW.txt", "replaced-hidden/dropped/q09.yaml"):
        assert f"{run}/{want}" in names, want
    assert sorted(tree_hash(fw.setdir / "hidden")) == ["deep/", "deep/q02.yaml", "q01.yaml"]
    assert (fw.setdir / "XCHECK-r1.md").exists() and (fw.setdir / "visible" / "q07.yaml").exists()
