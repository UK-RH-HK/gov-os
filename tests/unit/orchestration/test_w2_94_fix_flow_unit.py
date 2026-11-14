"""W2-94: the engineer's unit tests for the launch script's one-question fix flow (`--fix <id> --reason <code>` on the
writer's round 2; DEC-1180 (2)). Planted sets, runs and a stub `claude` only (the World of the W2-149 tests); no real
session, no real sets root."""
import io
import json
import os
import tarfile

import pytest

from test_w2_149_indep_launch import SET, WALLS, World, indep_launch, sha, tree_hash

VARIANT = """---
kind: writer
version: 1
variant_of: governance/project/indep-briefs/examin-sets/EXAMIN-writer.md (version 1)
rounds: 1
tools: [Read, Grep, Glob, Write, Edit, TodoWrite]
model: claude-sonnet-5-5
effort: high
result_schema: writer-result.schema.json
budget_usd: 4
timeout_s: 2400
---
The variant's text.
"""
WRITER_BRIEF = "governance/project/indep-briefs/writer.md"
OLD_Q = "id: q02\nquestion: ZZQUESTIONTEXT old\n"
NEW_Q = "id: q02\nquestion: ZZQUESTIONTEXT new\n"
GOOD = {"questions": 1, "action": "corrected", "by_kind": {"location": 1}, "by_area": {"code": 1}}
FIX = ["--fix", "q02", "--reason", "ANSWER_NOT_IN_SPANS"]


@pytest.fixture
def fx(tmp_path):
    w = World(tmp_path)
    w.put(WRITER_BRIEF, VARIANT)  # the approved variant: a front matter with no `sample:`
    w.commit = w.commit_all("variant")
    w.approve()
    setdir = w.sets / "fixtures" / "evaluation" / SET
    w.plant_set({"q01.yaml": "id: q01\n", "q02.yaml": OLD_Q, "visible/v.yaml": "v\n", "dropped/d.yaml": "d\n"})
    (setdir / "DRAW.txt").write_text("draw\n")
    (setdir / "XCHECK-r1.md").write_text("notes\n")
    w.setdir = setdir
    return w


def plant_run(w, stamp, sample, status="delivered", rnd=1, member="input/selection.json", body=None):
    rid = f"{stamp}-{SET}-r{rnd}"
    d = w.runs / "writer" / rid
    d.mkdir(parents=True)
    (d / "counts.json").write_text(json.dumps({"status": status, "round": rnd, "set": SET}))
    data = (body if body is not None else json.dumps({"sample": sample})).encode()
    (w.sets / WALLS / "writer").mkdir(parents=True, exist_ok=True)
    with tarfile.open(w.sets / WALLS / "writer" / (rid + ".tar"), "w") as t:
        info = tarfile.TarInfo(f"{rid}/{member}")
        info.size = len(data)
        t.addfile(info, io.BytesIO(data))
    return rid


def fix_run(w, *extra, dry=False, seed=None):
    return w.run(*w.args(rnd=2, dry=dry, seed=seed), *(extra or FIX))


def snapshot(w):
    return tree_hash(w.sets), tree_hash(w.home)


# -- 17: the argument refusals, nothing built ------------------------------------------------------------------------
@pytest.mark.parametrize("case", ["fix_alone", "reason_alone", "checker", "round1", "no_round", "q2", "Q02", "q002",
                                  "q0a", "unknown_code", "lower_code", "counts_only"])
def test_fix_argument_refusals_17_build_nothing(fx, case):
    plant_run(fx, "20260101T000000Z", ["a"])
    before = snapshot(fx)
    extra = list(FIX)
    kw = {"rnd": 2}
    if case == "fix_alone":
        extra = FIX[:2]
    elif case == "reason_alone":
        extra = FIX[2:]
    elif case == "checker":
        kw["kind"] = "checker"
    elif case == "round1":
        kw["rnd"] = 1
    elif case == "no_round":
        kw["rnd"] = None
    elif case in ("q2", "Q02", "q002", "q0a"):
        extra[1] = case
    elif case == "unknown_code":
        extra[3] = "NOT_A_CODE"
    elif case == "lower_code":
        extra[3] = "answer_not_in_spans"
    if case == "counts_only":
        rc, counts, _ = fx.run("--sets-root", str(fx.sets), "--kind", "writer", "--run", "20990101T000000Z-x-r1",
                               "--counts-only", *FIX)
    else:
        rc, counts, _ = fx.run(*fx.args(**kw), *extra)
    assert rc == 17 and "fix" not in counts
    assert snapshot(fx) == before


# -- the three staged inputs, the wall's file list, the sample's source ------------------------------------------------
def test_dry_stages_exactly_the_three_inputs_and_the_fixed_files(fx):
    plant_run(fx, "20260101T000000Z", ["old"])
    plant_run(fx, "20260102T000000Z", ["b/x.md", "c/y.md"])
    plant_run(fx, "20260103T000000Z", ["rejected"], status="rejected")
    plant_run(fx, "20260104T000000Z", ["r2"], rnd=2)
    rc, counts, p = fix_run(fx, seed=5, dry=True)
    assert rc == 0 and counts["status"] == "dry", p.stderr
    wall = fx.wall(counts)
    assert sorted(tree_hash(wall)) == [".claude/", ".claude/settings.json", ".claude/wall_hook.py", "CLAUDE.md",
                                       "WALL.json", "brief.md", "input/", "input/q02.yaml", "input/sample.json",
                                       "input/selection.json", "input/verdict.txt", "out/", "seed.txt"]
    assert (wall / "input" / "q02.yaml").read_bytes() == OLD_Q.encode()
    assert (wall / "input" / "verdict.txt").read_bytes() == b"q02 ANSWER_NOT_IN_SPANS\n"
    assert json.loads((wall / "input" / "sample.json").read_text()) == {"sample": ["b/x.md", "c/y.md"]}
    assert json.loads((wall / "input" / "selection.json").read_text())["sample"] == []
    assert counts["fix"] == {"id": "q02", "code": "ANSWER_NOT_IN_SPANS", "action": None}
    assert os.listdir(wall / "out") == []


def test_variant_front_matter_is_refused_without_fix(fx):
    rc, counts, _ = fx.run(*fx.args(rnd=1, seed=1, dry=True))
    assert rc == 10 and "fix" not in counts


@pytest.mark.parametrize("case", ["no_run", "not_delivered", "no_archive", "no_member", "bad_json", "sample_not_list",
                                  "no_question", "question_is_link"])
def test_missing_or_bad_input_refuses_10_with_nothing_built(fx, case):
    if case == "not_delivered":
        plant_run(fx, "20260101T000000Z", ["a"], status="rejected")
    elif case == "no_archive":
        rid = plant_run(fx, "20260101T000000Z", ["a"])
        (fx.sets / WALLS / "writer" / (rid + ".tar")).unlink()
    elif case == "no_member":
        plant_run(fx, "20260101T000000Z", ["a"], member="input/other.json")
    elif case == "bad_json":
        plant_run(fx, "20260101T000000Z", None, body="{not json")
    elif case == "sample_not_list":
        plant_run(fx, "20260101T000000Z", None, body='{"sample": [1, 2]}')
    elif case != "no_run":
        plant_run(fx, "20260101T000000Z", ["a"])
    if case == "no_question":
        (fx.setdir / "hidden" / "q02.yaml").unlink()
    elif case == "question_is_link":
        (fx.setdir / "hidden" / "q02.yaml").unlink()
        (fx.setdir / "hidden" / "q02.yaml").symlink_to(fx.setdir / "hidden" / "q01.yaml")
    before = snapshot(fx)
    rc, counts, _ = fix_run(fx)
    assert rc == 10
    assert snapshot(fx) == before


# -- the delivery -------------------------------------------------------------------------------------------------------
def out_files(result=GOOD, **extra):
    files = {"out/q02.yaml": NEW_Q, "out/result.json": json.dumps(result)}
    files.update(extra)
    return files


def test_good_delivery_replaces_only_the_hidden_question_and_packs_the_old_one(fx):
    plant_run(fx, "20260101T000000Z", ["a"])
    fx.stub({"session": "write", "out": out_files()})
    before = tree_hash(fx.setdir)
    rc, counts, p = fix_run(fx)
    assert rc == 0 and counts["status"] == "delivered", p.stderr
    after = tree_hash(fx.setdir)
    assert set(after) == set(before)
    assert {k for k in after if after[k] != before[k]} == {"hidden/q02.yaml"}
    assert (fx.setdir / "hidden" / "q02.yaml").read_text() == NEW_Q
    assert counts["fix"] == {"id": "q02", "code": "ANSWER_NOT_IN_SPANS", "action": "corrected"}
    assert counts["delivered"] == {"files": 1, "sha256": sha(NEW_Q.encode()), "to": "set"}
    assert json.loads((fx.runs / "writer" / counts["run"] / "counts.json").read_text())["fix"] == counts["fix"]
    with tarfile.open(fx.sets / WALLS / "writer" / (counts["run"] + ".tar")) as t:
        assert t.extractfile(f"{counts['run']}/replaced-hidden/q02.yaml").read() == OLD_Q.encode()
    log = (fx.runs / "writer" / counts["run"] / "launch.log").read_text()
    for text in (p.stdout, p.stderr, log):
        assert "ZZQUESTIONTEXT" not in text and "x.md" not in text
    assert not any(n.endswith(".replaced") for n in os.listdir(fx.sets / WALLS / "writer"))


def test_replaced_action_is_the_results_word(fx):
    plant_run(fx, "20260101T000000Z", ["a"])
    fx.stub({"session": "write", "out": out_files(dict(GOOD, action="replaced"))})
    rc, counts, _ = fix_run(fx)
    assert rc == 0 and counts["fix"]["action"] == "replaced"


@pytest.mark.parametrize("case", ["extra_file", "conflicts_on_delivery", "folder", "id_mismatch", "not_mapping",
                                  "bad_yaml", "no_action", "other_action", "two_questions", "kind_sum", "area_sum",
                                  "schema"])
def test_delivery_refusal_20_leaves_the_set_unchanged(fx, case):
    plant_run(fx, "20260101T000000Z", ["a"])
    files = out_files()
    if case == "extra_file":
        files["out/other.txt"] = "x"
    elif case == "conflicts_on_delivery":
        files["out/conflicts.md"] = "x"
    elif case == "folder":
        files["out/sub/x.txt"] = "x"
    elif case == "id_mismatch":
        files["out/q02.yaml"] = "id: q03\n"
    elif case == "not_mapping":
        files["out/q02.yaml"] = "- q02\n"
    elif case == "bad_yaml":
        files["out/q02.yaml"] = "id: [q02\n"
    elif case == "no_action":
        files = out_files({k: v for k, v in GOOD.items() if k != "action"})
    elif case == "other_action":
        files = out_files(dict(GOOD, action="rewritten"))
    elif case == "two_questions":
        files = out_files(dict(GOOD, questions=2))
    elif case == "kind_sum":
        files = out_files(dict(GOOD, by_kind={"location": 2}))
    elif case == "area_sum":
        files = out_files(dict(GOOD, by_area={}))
    elif case == "schema":
        files = out_files(dict(GOOD, by_area={"code": "1"}))
    fx.stub({"session": "write", "out": files})
    before = tree_hash(fx.setdir)
    rc, counts, _ = fix_run(fx)
    assert rc == 20 and counts["status"] == "rejected"
    assert tree_hash(fx.setdir) == before
    if case in ("no_action", "other_action", "two_questions", "kind_sum", "area_sum", "schema"):
        assert counts["fix"]["action"] is None


def test_a_stopped_result_delivers_nothing_21(fx):
    plant_run(fx, "20260101T000000Z", ["a"])
    fx.stub({"session": "write", "out": {"out/result.json": json.dumps(dict(GOOD, stopped="decisions-conflict")),
                                         "out/conflicts.md": "x\n"}})
    before = tree_hash(fx.setdir)
    rc, counts, _ = fix_run(fx)
    assert rc == 21 and counts["status"] == "stopped"
    assert tree_hash(fx.setdir) == before
    assert counts["fix"]["action"] is None


# -- without --fix nothing changes --------------------------------------------------------------------------------------
def test_a_run_without_fix_has_no_fix_key(fx):
    fx.put(WRITER_BRIEF, "---\nkind: writer\nsample: 1\nmodel: claude-haiku-5-5\n"
                         "result_schema: writer-result.schema.json\ntimeout_s: 20\n---\nb\n")
    fx.commit = fx.commit_all("plain")
    fx.approve()
    rc, counts, _ = fx.run(*fx.args(rnd=2, seed=3, dry=True))
    assert rc == 0 and "fix" not in counts
    assert sorted(os.listdir(fx.wall(counts) / "input")) == ["notes.md", "selection.json", "set"]


def test_the_docstring_has_one_fix_usage_line_naming_only_the_sets_root():
    lines = [x.strip() for x in indep_launch.__doc__.splitlines() if x.strip().startswith("python3 ") and "--fix" in x]
    assert len(lines) == 1
    assert "--set examin --round 2 --fix q02 --reason ANSWER_NOT_IN_SPANS" in lines[0]
    assert WALLS + "/" not in lines[0] and "$" not in lines[0]
