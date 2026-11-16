"""ACT-WALLS-REANCHOR-1: unit tests for the launch script's weekly re-anchoring flow (`--reanchor <week>` on the writer's
round 2; DEC-1179 (6), DEC-1178 (1)). Planted sets, runs and a stub `claude` only (the World of the W2-149 tests); no
real session, no real sets root. Every planted request holds question ids and entry numbers only, and the marker words
planted in the questions never reach a counts line, a log or a printed line."""
import copy
import json
import os
import re
import tarfile
from pathlib import Path

import pytest
import yaml

from test_w2_149_indep_launch import SET, TEMPLATE, WALLS, World, indep_launch, sha, tree_hash

BRIEF = """---
kind: writer
version: 1
tools: [Read, Grep, Glob, Write, Edit, TodoWrite]
model: claude-sonnet-5-5
effort: high
result_schema: writer-result.schema.json
budget_usd: 4
timeout_s: 2400
---
The re-anchoring brief's text.
"""
WRITER_BRIEF = "governance/project/indep-briefs/writer.md"
WEEK = "2026-W47"
C0, C1 = "a" * 40, "b" * 40


def question(qid, text):
    """A question in the measure's form: three entries, the second a list of two alternatives."""
    return {"id": qid, "question": f"ZZMARKER {text}", "gold_answer": f"ZZGOLD {qid}", "category": "location",
            "area": "code", "commit": C0,
            "sources": [{"path": "src/a.py", "lines": [1, 4]},
                        [{"path": "docs/b.md", "lines": [10, 12], "note": "alt"},
                         {"path": "docs/c.md", "heading": "## C"}],
                        {"path": "src/d.py", "lines": [7, 9], "note": "kept"}]}


def text_of(q):
    return yaml.safe_dump(q, sort_keys=False)


def reanchored(qid, text):
    """The question with its named entries re-anchored the allowed way: entry 1's lines and own commit (h03); entry 2's
    alternatives: one moved (path and lines), one with a new heading and no commit (both ids)."""
    q = copy.deepcopy(question(qid, text))
    if qid == "h03":
        q["sources"][0].update(lines=[2, 5], commit=C1)
    q["sources"][1][0].update(path="docs/b2.md", lines=[20, 22], commit=C1)
    q["sources"][1][1]["heading"] = "## C moved"
    return q


OLD = {"h03": text_of(question("h03", "old h03")), "h20": text_of(question("h20", "old h20")),
       "q01": text_of(question("q01", "untouched"))}
NEW = {"h03": text_of(reanchored("h03", "old h03")),
       "h20": text_of(dict(reanchored("h20", "old h20"), replace_reason="moved-out"))}
ROWS = [{"id": "h03", "entry": 1}, {"id": "h03", "entry": 2}, {"id": "h20", "entry": 2}]
GOOD = {"questions": 2, "corrected": 1, "replaced": 1, "by_kind": {"location": 2}, "by_area": {"code": 1, "docs": 1}}
REA = ["--reanchor", WEEK]


DECLARED = "    input_reanchor: [questions, reanchor]\n"
KINDS_REL = f"governance/project/{WALLS}/kinds.yaml"


def kinds_declared():
    """The repository's template kinds.yaml (which this ticket leaves unchanged) with the writer's re-anchoring input
    declared, as the owner's later ACT will approve it: one line after the writer's `input_round2`."""
    text = (TEMPLATE / "kinds.yaml").read_text()
    assert "input_reanchor" not in text
    out = re.sub(r"(?m)^(    input_round2: \[set, notes\].*\n)", lambda m: m.group(1) + DECLARED, text, count=1)
    assert out != text
    return out


def request(w, rows=ROWS, **over):
    req = {"week": WEEK, "audit_commit": w.commit, "set": SET, "changed": rows, "count": len(rows)}
    req.update(over)
    return req


def plant_request(w, req=None, week=WEEK):
    folder = w.sets / "runs" / SET
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"REANCHOR-{week}.json"
    path.write_text(json.dumps(request(w) if req is None else req))
    return path


@pytest.fixture
def fx(tmp_path):
    w = World(tmp_path)
    w.put(WRITER_BRIEF, BRIEF)
    w.put(KINDS_REL, kinds_declared())
    w.commit = w.commit_all("reanchor brief")
    w.approve()
    w.setdir = w.sets / "fixtures" / "evaluation" / SET
    w.plant_set({f"{k}.yaml": v for k, v in OLD.items()} | {"dropped/d.yaml": "d\n"})
    (w.setdir / "DRAW.txt").write_text("draw\n")
    plant_request(w)
    return w


def rea_run(w, *extra, dry=False, seed=None, **kw):
    return w.run(*w.args(rnd=2, dry=dry, seed=seed, **kw), *(extra or REA))


def snapshot(w):
    return tree_hash(w.sets), tree_hash(w.home)


# -- 17: the argument refusals, nothing built --------------------------------------------------------------------------
@pytest.mark.parametrize("case", ["checker", "round1", "no_round", "week_short", "week_no_w", "week_text", "week_long",
                                  "week_newline", "with_fix_pair", "empty_week", "counts_only"])
def test_reanchor_argument_refusals_17_build_nothing(fx, case):
    before = snapshot(fx)
    extra, kw = list(REA), {"rnd": 2}
    if case == "checker":
        kw["kind"] = "checker"
    elif case == "round1":
        kw["rnd"] = 1
    elif case == "no_round":
        kw["rnd"] = None
    elif case == "week_short":
        extra[1] = "2026-W4"
    elif case == "week_no_w":
        extra[1] = "2026-47"
    elif case == "week_text":
        extra[1] = "latest"
    elif case == "week_long":
        extra[1] = "2026-W470"
    elif case == "week_newline":
        extra[1] = WEEK + "\n"
    elif case == "empty_week":
        extra[1] = ""
    elif case == "with_fix_pair":
        extra += ["--fix", "q02", "--reason", "ANSWER_NOT_IN_SPANS"]
    if case == "counts_only":
        rc, counts, _ = fx.run("--sets-root", str(fx.sets), "--kind", "writer", "--run", "20990101T000000Z-x-r1",
                               "--counts-only", *REA)
    else:
        rc, counts, _ = fx.run(*fx.args(**kw), *extra)
    assert rc == 17 and "reanchor" not in counts
    assert snapshot(fx) == before


def test_the_fix_pair_with_the_reanchor_week_is_refused_in_either_order(fx):
    rc, _, _ = fx.run(*fx.args(rnd=2), "--fix", "q02", "--reason", "ANSWER_NOT_IN_SPANS", *REA)
    assert rc == 17
    rc, _, _ = fx.run(*fx.args(rnd=2), "--reason", "ANSWER_NOT_IN_SPANS", *REA)
    assert rc == 17


# -- 11: the approved template must declare the input ------------------------------------------------------------------
def kinds_without_the_input():
    text = kinds_declared()
    out = re.sub(r"(?m)^    input_reanchor:.*\n", "", text)
    assert out != text and out == (TEMPLATE / "kinds.yaml").read_text()
    return out


@pytest.mark.parametrize("case", ["line_absent", "empty_list", "unknown_word", "not_a_list", "kind_has_no_word"])
def test_a_template_without_the_declaration_refuses_11_and_builds_nothing(fx, case):
    text = kinds_declared()
    if case == "line_absent":
        text = kinds_without_the_input()
    elif case == "empty_list":
        text = text.replace("input_reanchor: [questions, reanchor]", "input_reanchor: []")
    elif case == "unknown_word":
        text = text.replace("input_reanchor: [questions, reanchor]", "input_reanchor: [questions, everything]")
    elif case == "not_a_list":
        text = text.replace("input_reanchor: [questions, reanchor]", "input_reanchor: reanchor")
    else:
        text = text.replace("input_reanchor: [questions, reanchor]", "input_reanchor: [questions]")
    fx.put(f"governance/project/{WALLS}/kinds.yaml", text)
    fx.commit = fx.commit_all("template")
    fx.approve()
    plant_request(fx)
    before = snapshot(fx)
    rc, counts, _ = rea_run(fx)
    assert rc == 11
    assert snapshot(fx) == before


def test_the_old_approved_line_for_kinds_refuses_11_until_the_list_is_re_pinned(fx):
    old = kinds_without_the_input()
    approved = (fx.sets / WALLS / "APPROVED").read_text().splitlines()
    new_sha = sha(kinds_declared().encode())
    stale = [x.replace(new_sha, sha(old.encode())) if f"{WALLS}/kinds.yaml" in x else x for x in approved]
    assert stale != approved
    (fx.sets / WALLS / "APPROVED").write_text("\n".join(stale) + "\n")
    rc, counts, _ = rea_run(fx, dry=True, seed=1)
    assert rc == 11
    (fx.sets / WALLS / "APPROVED").write_text("\n".join(approved) + "\n")
    rc, counts, p = rea_run(fx, dry=True, seed=1)
    assert rc == 0, p.stderr


def test_a_run_without_the_flag_is_unaffected_by_the_declaration(fx):
    fx.put(WRITER_BRIEF, World.brief_text("writer"))
    fx.put(f"governance/project/{WALLS}/kinds.yaml", kinds_without_the_input())
    fx.commit = fx.commit_all("template")
    fx.approve()
    rc, counts, p = fx.run(*fx.args(rnd=1, seed=2, dry=True))
    assert rc == 0 and "reanchor" not in counts, p.stderr


# -- the staged inputs and the wall's file list --------------------------------------------------------------------------
def test_dry_stages_the_listed_questions_the_request_and_the_fixed_files_only(fx):
    rc, counts, p = rea_run(fx, seed=5, dry=True)
    assert rc == 0 and counts["status"] == "dry", p.stderr
    wall = fx.wall(counts)
    assert sorted(tree_hash(wall)) == [".claude/", ".claude/settings.json", ".claude/wall_hook.py", "CLAUDE.md",
                                       "WALL.json", "brief.md", "input/", "input/h03.yaml", "input/h20.yaml",
                                       "input/reanchor.json", "input/selection.json", "out/", "seed.txt"]
    for qid in ("h03", "h20"):
        assert (wall / "input" / f"{qid}.yaml").read_bytes() == OLD[qid].encode()
    assert json.loads((wall / "input" / "reanchor.json").read_text()) == {"week": WEEK, "changed": ROWS}
    assert json.loads((wall / "input" / "selection.json").read_text())["sample"] == []
    assert counts["reanchor"] == {"week": WEEK, "entries": 3, "ids": 2, "absent": 0, "corrected": None,
                                  "replaced": None}
    assert os.listdir(wall / "out") == []
    # the other questions, the dropped folder and the draw record are not staged anywhere
    assert not any("q01" in n or "DRAW" in n or "dropped" in n for n in tree_hash(wall))
    assert "fix" not in counts


def test_an_id_with_no_hidden_file_is_counted_absent_and_not_staged(fx):
    rows = ROWS + [{"id": "v07", "entry": 1}, {"id": "v08", "entry": 3}]
    plant_request(fx, request(fx, rows))
    rc, counts, p = rea_run(fx, seed=5, dry=True)
    assert rc == 0, p.stderr
    wall = fx.wall(counts)
    assert sorted(n for n in tree_hash(wall) if n.startswith("input/")) == [
        "input/", "input/h03.yaml", "input/h20.yaml", "input/reanchor.json", "input/selection.json"]
    assert json.loads((wall / "input" / "reanchor.json").read_text())["changed"] == ROWS
    assert counts["reanchor"]["entries"] == 5 and counts["reanchor"]["ids"] == 2 and counts["reanchor"]["absent"] == 2


def test_the_request_may_list_its_rows_in_any_order(fx):
    plant_request(fx, request(fx, list(reversed(ROWS))))
    rc, counts, p = rea_run(fx, seed=5, dry=True)
    assert rc == 0, p.stderr
    assert json.loads((fx.wall(counts) / "input" / "reanchor.json").read_text())["changed"] == ROWS


# -- F3: ids matched case-insensitively, staged in the set's own spelling ------------------------------------------------
def test_upper_and_mixed_case_ids_are_staged_in_the_sets_spelling(fx):
    (fx.setdir / "hidden" / "Q07.yaml").write_text(text_of(question("Q07", "upper")))
    (fx.setdir / "hidden" / "Mx9.yaml").write_text(text_of(question("Mx9", "mixed")))
    rows = [{"id": "q07", "entry": 2}, {"id": "Q07", "entry": 1}, {"id": "mX9", "entry": 3}, {"id": "h03", "entry": 1}]
    plant_request(fx, request(fx, rows))
    rc, counts, p = rea_run(fx, seed=5, dry=True)
    assert rc == 0, p.stderr
    wall = fx.wall(counts)
    assert sorted(n for n in tree_hash(wall) if n.startswith("input/") and n.endswith(".yaml")) == [
        "input/Mx9.yaml", "input/Q07.yaml", "input/h03.yaml"]
    assert (wall / "input" / "Q07.yaml").read_bytes() == (fx.setdir / "hidden" / "Q07.yaml").read_bytes()
    assert json.loads((wall / "input" / "reanchor.json").read_text()) == {"week": WEEK, "changed": [
        {"id": "Mx9", "entry": 3}, {"id": "Q07", "entry": 1}, {"id": "Q07", "entry": 2}, {"id": "h03", "entry": 1}]}
    assert counts["reanchor"] == {"week": WEEK, "entries": 4, "ids": 3, "absent": 0, "corrected": None,
                                  "replaced": None}


def test_absent_is_counted_once_per_case_folded_id(fx):
    rows = ROWS + [{"id": "v07", "entry": 1}, {"id": "V07", "entry": 2}, {"id": "Zz1", "entry": 1}]
    plant_request(fx, request(fx, rows))
    rc, counts, p = rea_run(fx, seed=5, dry=True)
    assert rc == 0, p.stderr
    assert counts["reanchor"]["entries"] == 6 and counts["reanchor"]["ids"] == 2 and counts["reanchor"]["absent"] == 2


def test_a_case_collision_among_hidden_files_not_requested_is_not_refused(fx):
    (fx.setdir / "hidden" / "Q01.yaml").write_text(OLD["q01"])  # q01.yaml and Q01.yaml: neither is requested
    rc, counts, p = rea_run(fx, seed=5, dry=True)
    assert rc == 0, p.stderr
    assert not any("01" in n for n in tree_hash(fx.wall(counts)))


def test_plan_reanchor_returns_the_plan_the_staged_request_and_the_numbers(fx):
    (fx.setdir / "hidden" / "Q07.yaml").write_text(text_of(question("Q07", "upper")))
    plant_request(fx, request(fx, [{"id": "q07", "entry": 1}, {"id": "H20", "entry": 2}, {"id": "x1", "entry": 1}]))
    plan, staged, info = indep_launch.plan_reanchor(str(fx.sets), SET, WEEK, fx.commit)
    hidden = str(fx.setdir / "hidden")
    assert plan == [(os.path.join(hidden, "Q07.yaml"), "input/Q07.yaml"),
                    (os.path.join(hidden, "h20.yaml"), "input/h20.yaml")]
    assert list(staged) == ["input/reanchor.json"]
    assert json.loads(staged["input/reanchor.json"]) == {"week": WEEK, "changed": [{"id": "Q07", "entry": 1},
                                                                                     {"id": "h20", "entry": 2}]}
    assert info == {"entries": 3, "ids": 2, "absent": 1, "present": ["Q07", "h20"]}
    # batch 2: the named entries and each staged file's sha256 kept for the delivery, outside the mapping
    assert info.named == {"Q07": [1], "h20": [2]}
    assert info.sha256 == {"Q07": sha((fx.setdir / "hidden" / "Q07.yaml").read_bytes()),
                           "h20": sha(OLD["h20"].encode())}


def test_an_upper_case_id_is_delivered_under_the_sets_spelling(fx):
    (fx.setdir / "hidden" / "Q07.yaml").write_text(text_of(question("Q07", "upper")))
    plant_request(fx, request(fx, [{"id": "q07", "entry": 1}]))
    q = question("Q07", "upper")
    q["sources"][0]["lines"] = [3, 6]
    res = {"questions": 1, "corrected": 1, "replaced": 0, "by_kind": {"fact": 1}, "by_area": {"code": 1}}
    fx.stub({"session": "write", "out": {"out/Q07.yaml": text_of(q), "out/result.json": json.dumps(res)}})
    rc, counts, p = rea_run(fx)
    assert rc == 0, p.stderr
    assert (fx.setdir / "hidden" / "Q07.yaml").read_text() == text_of(q)
    assert not (fx.setdir / "hidden" / "q07.yaml").exists()


def test_an_upper_case_id_delivered_under_another_spelling_is_refused_20(fx):
    (fx.setdir / "hidden" / "Q07.yaml").write_text(text_of(question("Q07", "upper")))
    plant_request(fx, request(fx, [{"id": "Q07", "entry": 1}]))
    res = {"questions": 1, "corrected": 1, "replaced": 0, "by_kind": {"fact": 1}, "by_area": {"code": 1}}
    fx.stub({"session": "write", "out": {"out/q07.yaml": text_of(question("Q07", "upper")),
                                         "out/result.json": json.dumps(res)}})
    before = tree_hash(fx.setdir)
    rc, counts, _ = rea_run(fx)
    assert rc == 20 and tree_hash(fx.setdir) == before


@pytest.mark.parametrize("case", ["no_file", "file_is_link", "not_json", "json_constant", "not_object", "extra_key",
                                  "missing_key", "week_differs", "set_differs", "commit_short", "commit_not_hex",
                                  "count_differs", "count_bool", "duplicate_row", "duplicate_row_other_case",
                                  "entry_zero", "entry_bool", "entry_text", "id_bad", "id_path", "id_long",
                                  "id_not_text", "row_extra_key", "row_not_object", "empty", "none_present",
                                  "hidden_is_link", "hidden_is_folder", "hidden_case_collision", "too_many"])
def test_a_missing_or_malformed_request_refuses_10_with_nothing_built(fx, case):
    req = request(fx)
    path = fx.sets / "runs" / SET / f"REANCHOR-{WEEK}.json"
    if case == "no_file":
        path.unlink()
    elif case == "file_is_link":
        other = fx.sets / "runs" / SET / "other.json"
        other.write_text(json.dumps(req))
        path.unlink()
        path.symlink_to(other)
    elif case == "not_json":
        path.write_text("{not json")
    elif case == "json_constant":
        path.write_text(json.dumps(req).replace('"count": 3', '"count": NaN'))
    elif case == "not_object":
        path.write_text("[1]")
    elif case == "extra_key":
        path.write_text(json.dumps(dict(req, note="x")))
    elif case == "missing_key":
        path.write_text(json.dumps({k: v for k, v in req.items() if k != "audit_commit"}))
    elif case == "week_differs":
        path.write_text(json.dumps(dict(req, week="2026-W46")))
    elif case == "set_differs":
        path.write_text(json.dumps(dict(req, set="other-set")))
    elif case == "commit_short":
        path.write_text(json.dumps(dict(req, audit_commit=fx.commit[:12])))
    elif case == "commit_not_hex":
        path.write_text(json.dumps(dict(req, audit_commit="Z" * 40)))
    elif case == "count_differs":
        path.write_text(json.dumps(dict(req, count=2)))
    elif case == "count_bool":
        path.write_text(json.dumps(dict(req, count=True)))
    elif case == "duplicate_row":
        path.write_text(json.dumps(request(fx, ROWS + [ROWS[0]])))
    elif case == "duplicate_row_other_case":  # Q01 and q01 are one id: the same entry twice
        path.write_text(json.dumps(request(fx, ROWS + [{"id": "H03", "entry": 1}])))
    elif case == "id_long":
        path.write_text(json.dumps(request(fx, [{"id": "h" * 33, "entry": 1}])))
    elif case == "id_not_text":
        path.write_text(json.dumps(request(fx, [{"id": 3, "entry": 1}])))
    elif case == "hidden_case_collision":  # two top-level files whose stems match one requested id
        (fx.setdir / "hidden" / "H20.yaml").write_text(OLD["h20"])
    elif case == "entry_zero":
        path.write_text(json.dumps(request(fx, [{"id": "h03", "entry": 0}])))
    elif case == "entry_bool":
        path.write_text(json.dumps(request(fx, [{"id": "h03", "entry": True}])))
    elif case == "entry_text":
        path.write_text(json.dumps(request(fx, [{"id": "h03", "entry": "1"}])))
    elif case == "id_bad":
        path.write_text(json.dumps(request(fx, [{"id": "h.03", "entry": 1}])))
    elif case == "id_path":
        path.write_text(json.dumps(request(fx, [{"id": "../q01", "entry": 1}])))
    elif case == "row_extra_key":
        path.write_text(json.dumps(request(fx, [{"id": "h03", "entry": 1, "text": "x"}])))
    elif case == "row_not_object":
        path.write_text(json.dumps(request(fx, ["h03 1"])))
    elif case == "empty":
        path.write_text(json.dumps(request(fx, [])))
    elif case == "none_present":
        path.write_text(json.dumps(request(fx, [{"id": "v07", "entry": 1}])))
    elif case == "hidden_is_link":
        (fx.setdir / "hidden" / "h20.yaml").unlink()
        (fx.setdir / "hidden" / "h20.yaml").symlink_to(fx.setdir / "hidden" / "q01.yaml")
    elif case == "hidden_is_folder":
        (fx.setdir / "hidden" / "h20.yaml").unlink()
        (fx.setdir / "hidden" / "h20.yaml").mkdir()
    elif case == "too_many":
        path.write_text(json.dumps(request(fx, [{"id": "h03", "entry": n} for n in range(1, 402)])))
    before = snapshot(fx)
    rc, counts, _ = rea_run(fx)
    assert rc == 10
    assert snapshot(fx) == before


def test_a_request_listed_at_another_commit_than_the_trees_refuses_14(fx):
    plant_request(fx, request(fx, audit_commit="0123456789abcdef0123456789abcdef01234567"))
    before = snapshot(fx)
    rc, counts, _ = rea_run(fx)
    assert rc == 14
    assert snapshot(fx) == before


def test_a_malformed_row_refuses_10_before_the_commit_is_compared(fx):
    plant_request(fx, request(fx, [{"id": "h.03", "entry": 1}], audit_commit="0123456789abcdef0123456789abcdef01234567"))
    rc, _, _ = rea_run(fx)
    assert rc == 10


def test_a_count_that_is_not_an_integer_refuses_10(fx):
    plant_request(fx, request(fx, count=3.0))
    before = snapshot(fx)
    rc, _, _ = rea_run(fx)
    assert rc == 10 and snapshot(fx) == before


def test_the_flow_runs_a_plain_writer_brief_only(fx):
    fx.put(WRITER_BRIEF, BRIEF.replace("budget_usd: 4", "brief: sgx1-writer-tuning\nbudget_usd: 4"))
    fx.commit = fx.commit_all("entry")
    fx.approve()
    plant_request(fx)
    rc, _, _ = rea_run(fx, seed=3, dry=True)
    assert rc == 10


# -- the delivery -------------------------------------------------------------------------------------------------------
def out_files(result=GOOD, **extra):
    files = {"out/h03.yaml": NEW["h03"], "out/h20.yaml": NEW["h20"], "out/result.json": json.dumps(result)}
    files.update(extra)
    return files


def test_good_delivery_replaces_only_the_listed_questions_and_packs_the_old_ones(fx):
    fx.stub({"session": "write", "out": out_files()})
    before = tree_hash(fx.setdir)
    q01 = os.lstat(fx.setdir / "hidden" / "q01.yaml")
    rc, counts, p = rea_run(fx)
    assert rc == 0 and counts["status"] == "delivered", p.stderr
    kept = os.lstat(fx.setdir / "hidden" / "q01.yaml")
    assert (kept.st_ino, kept.st_mtime_ns) == (q01.st_ino, q01.st_mtime_ns)
    after = tree_hash(fx.setdir)
    assert set(after) == set(before)
    assert {k for k in after if after[k] != before[k]} == {"hidden/h03.yaml", "hidden/h20.yaml"}
    for qid in ("h03", "h20"):
        assert (fx.setdir / "hidden" / f"{qid}.yaml").read_text() == NEW[qid]
    assert (fx.setdir / "hidden" / "q01.yaml").read_text() == OLD["q01"]
    assert counts["reanchor"] == {"week": WEEK, "entries": 3, "ids": 2, "absent": 0, "corrected": 1, "replaced": 1}
    pairs = sorted((f"{q}.yaml", sha(NEW[q].encode())) for q in ("h03", "h20"))
    assert counts["delivered"] == {"files": 2, "sha256": indep_launch.bundle_sha(pairs), "to": "set"}
    assert json.loads((fx.runs / "writer" / counts["run"] / "counts.json").read_text())["reanchor"] == counts["reanchor"]
    with tarfile.open(fx.sets / WALLS / "writer" / (counts["run"] + ".tar")) as t:
        for qid in ("h03", "h20"):
            assert t.extractfile(f"{counts['run']}/replaced-hidden/{qid}.yaml").read() == OLD[qid].encode()
    log = (fx.runs / "writer" / counts["run"] / "launch.log").read_text()
    for text in (p.stdout, p.stderr, log):
        assert "ZZMARKER" not in text
    assert not any(n.endswith(".replaced") for n in os.listdir(fx.sets / WALLS / "writer"))
    left = [n for n in os.listdir(fx.setdir / "hidden") if n.endswith(".tmp") or n.startswith(".")]
    assert left == []
    # the counts line of the run reads back, and carries the key the schema now allows
    rc2, again, p2 = fx.run("--sets-root", str(fx.sets), "--kind", "writer", "--run", counts["run"], "--counts-only")
    assert rc2 == 0, p2.stderr
    assert again["reanchor"] == counts["reanchor"]


def test_one_staged_id_delivers_one_file(fx):
    plant_request(fx, request(fx, [{"id": "h20", "entry": 2}]))
    fx.stub({"session": "write", "out": {"out/h20.yaml": NEW["h20"], "out/result.json": json.dumps(
        {"questions": 1, "corrected": 1, "replaced": 0, "by_kind": {"fact": 1}, "by_area": {"code": 1}})}})
    before = tree_hash(fx.setdir)
    rc, counts, p = rea_run(fx)
    assert rc == 0, p.stderr
    after = tree_hash(fx.setdir)
    assert {k for k in after if after[k] != before[k]} == {"hidden/h20.yaml"}
    assert counts["delivered"]["files"] == 1 and counts["delivered"]["sha256"] == sha(NEW["h20"].encode())


@pytest.mark.parametrize("case", ["extra_file", "conflicts_file", "folder", "missing_yaml", "unlisted_yaml",
                                  "id_mismatch", "not_mapping", "bad_yaml", "two_questions_one", "questions_off",
                                  "kind_sum", "area_sum", "no_corrected", "no_replaced", "sum_off", "bool_count",
                                  "negative", "schema"])
def test_delivery_refusal_20_leaves_the_set_unchanged(fx, case):
    files = out_files()
    result = dict(GOOD)
    if case == "extra_file":
        files["out/other.txt"] = "x"
    elif case == "conflicts_file":
        files["out/conflicts.md"] = "x"
    elif case == "folder":
        files["out/sub/x.txt"] = "x"
    elif case == "missing_yaml":
        del files["out/h20.yaml"]
    elif case == "unlisted_yaml":
        files["out/q01.yaml"] = "id: q01\n"
    elif case == "id_mismatch":
        files["out/h20.yaml"] = "id: h03\n"
    elif case == "not_mapping":
        files["out/h20.yaml"] = "- h20\n"
    elif case == "bad_yaml":
        files["out/h20.yaml"] = "id: [h20\n"
    elif case == "two_questions_one":
        result["questions"] = 1
    elif case == "questions_off":
        result["questions"] = 3
    elif case == "kind_sum":
        result["by_kind"] = {"location": 3}
    elif case == "area_sum":
        result["by_area"] = {}
    elif case == "no_corrected":
        del result["corrected"]
    elif case == "no_replaced":
        del result["replaced"]
    elif case == "sum_off":
        result["corrected"] = 2
    elif case == "bool_count":
        result["corrected"], result["replaced"] = True, 1
    elif case == "negative":
        result["corrected"], result["replaced"] = 3, -1
    elif case == "schema":
        result["by_area"] = {"code": "2"}
    files["out/result.json"] = json.dumps(result)
    fx.stub({"session": "write", "out": files})
    before = tree_hash(fx.setdir)
    rc, counts, _ = rea_run(fx)
    assert rc == 20 and counts["status"] == "rejected"
    assert tree_hash(fx.setdir) == before
    if case not in ("extra_file", "conflicts_file", "folder", "missing_yaml", "unlisted_yaml", "id_mismatch",
                    "not_mapping", "bad_yaml"):  # the result's own checks refuse before any number is copied
        assert counts["reanchor"]["corrected"] is None and counts["reanchor"]["replaced"] is None
    assert not any(n.endswith(".replaced") for n in os.listdir(fx.sets / WALLS / "writer"))


# -- the delivered question against the staged one ---------------------------------------------------------------------
def changed(case):
    """The two delivered questions (h03 named entries 1 and 2, h20 named entry 2) with one difference the check refuses."""
    h03, h20 = reanchored("h03", "old h03"), dict(reanchored("h20", "old h20"), replace_reason="moved-out")
    s3, s20 = h03["sources"], h20["sources"]
    if case == "question":
        h03["question"] = "ZZMARKER old h03 reworded"
    elif case == "gold_answer":
        h20["gold_answer"] = "ZZGOLD other"
    elif case == "category":
        h03["category"] = "fact"
    elif case == "question_commit":
        h03["commit"] = C1
    elif case == "id":
        h03["id"] = "h04"
    elif case == "other_top_key":
        h20["area"] = "docs"
    elif case == "top_key_added":
        h03["note"] = "x"
    elif case == "top_key_removed":
        del h03["category"]
    elif case == "replace_reason_empty":
        h03["replace_reason"] = ""
    elif case == "replace_reason_not_text":
        h03["replace_reason"] = 1
    elif case == "sources_longer":
        s3.append({"path": "src/e.py"})
    elif case == "sources_shorter":
        s20.pop()
    elif case == "sources_not_list":
        h20["sources"] = {"path": "src/a.py"}
    elif case == "unnamed_entry_lines":  # h03's entry 3 is not named
        s3[2]["lines"] = [8, 10]
    elif case == "unnamed_entry_commit":  # h20's entry 1 is not named
        s20[0]["commit"] = C1
    elif case == "unnamed_entry_other_key":
        s3[2]["note"] = "changed"
    elif case == "named_entry_other_key":
        s3[0]["quote"] = "x"
    elif case == "named_alternative_other_key":  # h20's named entry 2: a key beyond the four added
        s20[1][1]["kind"] = "x"
    elif case == "named_alternative_key_removed":  # h03's named entry 2: a key beyond the four removed
        del s3[1][0]["note"]
    elif case == "named_dict_becomes_list":
        s3[0] = [dict(s3[0])]
    elif case == "named_list_becomes_dict":
        s3[1] = dict(s3[1][0])
    elif case == "named_list_longer":
        s3[1].append({"path": "docs/z.md", "lines": [1, 2]})
    elif case == "named_list_shorter":
        s20[1].pop()
    elif case == "named_alternative_not_mapping":
        s3[1][1] = "docs/c.md"
    elif case == "bool_for_int":  # True == 1 in Python; the check compares types too
        s20[2]["lines"] = [True, 9]
    elif case == "float_for_int":
        s3[2]["lines"] = [7.0, 9]
    return h03, h20


CHANGED = ["question", "gold_answer", "category", "question_commit", "id", "other_top_key", "top_key_added",
           "top_key_removed", "replace_reason_empty", "replace_reason_not_text", "sources_longer", "sources_shorter",
           "sources_not_list", "unnamed_entry_lines", "unnamed_entry_commit", "unnamed_entry_other_key",
           "named_entry_other_key", "named_alternative_other_key", "named_alternative_key_removed",
           "named_dict_becomes_list",
           "named_list_becomes_dict", "named_list_longer", "named_list_shorter", "named_alternative_not_mapping",
           "bool_for_int", "float_for_int"]


@pytest.mark.parametrize("case", CHANGED)
def test_a_delivered_question_changed_beyond_the_named_blocks_is_refused_20_with_nothing_replaced(fx, case):
    h03, h20 = changed(case)
    fx.stub({"session": "write", "out": out_files(**{"out/h03.yaml": text_of(h03), "out/h20.yaml": text_of(h20)})})
    before = tree_hash(fx.setdir)
    q01 = os.lstat(fx.setdir / "hidden" / "q01.yaml")
    rc, counts, p = rea_run(fx)
    assert rc == 20 and counts["status"] == "rejected", p.stderr
    assert tree_hash(fx.setdir) == before
    after = os.lstat(fx.setdir / "hidden" / "q01.yaml")
    assert (after.st_ino, after.st_mtime_ns) == (q01.st_ino, q01.st_mtime_ns)
    assert "reanchor_changed" in (fx.runs / "writer" / counts["run"] / "launch.log").read_text()
    assert not any(n.endswith(".replaced") for n in os.listdir(fx.sets / WALLS / "writer"))
    for text in (p.stdout, p.stderr):
        assert "ZZMARKER" not in text and "ZZGOLD" not in text and "h03" not in text


def test_only_path_lines_heading_and_commit_of_a_named_entry_and_replace_reason_may_change(fx):
    h03, h20 = reanchored("h03", "old h03"), reanchored("h20", "old h20")
    del h03["sources"][0]["lines"]  # removed, and a heading added, on named entry 1
    h03["sources"][0]["heading"] = "## A"
    del h03["sources"][1][1]["heading"]  # an alternative's heading removed, its lines added
    h03["sources"][1][1]["lines"] = [1, 3]
    h03["replace_reason"] = "unclear"
    fx.stub({"session": "write", "out": out_files(**{"out/h03.yaml": text_of(h03), "out/h20.yaml": text_of(h20)})})
    rc, counts, p = rea_run(fx)
    assert rc == 0 and counts["status"] == "delivered", p.stderr
    assert yaml.safe_load((fx.setdir / "hidden" / "h03.yaml").read_text()) == h03


def test_an_unchanged_copy_is_delivered(fx):
    fx.stub({"session": "write", "out": out_files(**{"out/h03.yaml": OLD["h03"], "out/h20.yaml": OLD["h20"]})})
    rc, counts, p = rea_run(fx)
    assert rc == 0, p.stderr


def test_reanchor_same_compares_by_type_and_names_entries_by_their_1_based_index():
    same = indep_launch.reanchor_same
    a = question("h03", "x")
    b = copy.deepcopy(a)
    b["sources"][2]["lines"] = [1, 2]
    assert not same(a, b, {1, 2}) and same(a, b, {3})
    assert same(a, copy.deepcopy(a), set())
    assert not same(a, dict(copy.deepcopy(a), category=None), set())
    assert not same([1], [1], set()) and not same(a, [a], set())
    assert same({"id": 1, "x": float("nan")}, {"id": 1, "x": float("nan")}, set())


def test_a_destination_that_goes_missing_before_delivery_refuses_20_and_changes_nothing(fx):
    hook = fx.hook("if point == 'after_session':\n"
                   f"    os.unlink({str(fx.setdir / 'hidden' / 'h20.yaml')!r})\n")
    fx.stub({"session": "write", "out": out_files()})
    rc, counts, _ = fx.run(*fx.args(rnd=2), *REA, extra={"GOV_INDEP_TEST_HOOK": hook})
    assert rc == 20 and counts["status"] == "rejected"
    assert (fx.setdir / "hidden" / "h03.yaml").read_text() == OLD["h03"]  # the first id is not replaced
    assert not (fx.setdir / "hidden" / "h20.yaml").exists()
    assert not any(n.endswith(".replaced") for n in os.listdir(fx.sets / WALLS / "writer"))
    assert [n for n in os.listdir(fx.setdir / "hidden") if n.startswith(".")] == []


# -- batch 2: the comparison from the launcher's own reading, never from the wall --------------------------------------
WALL_PUT = ("def put(rel, text):\n"
            "    p = os.path.join(wall, rel)\n"
            "    os.chmod(os.path.dirname(p), 0o700)\n"
            "    if os.path.lexists(p):\n"
            "        os.chmod(p, 0o600)\n"
            "        os.unlink(p)\n"
            "    if text is not None:\n"
            "        with open(p, 'w') as f:\n"
            "            f.write(text)\n")


def session_alters_wall(fx, files):
    """A hook that, after the session, rewrites (or, for None, removes) the named files in the wall's input/."""
    body = WALL_PUT + "if point == 'after_session':\n"
    body += "".join(f"    put({rel!r}, {text!r})\n" for rel, text in files.items())
    return {"GOV_INDEP_TEST_HOOK": fx.hook(body)}


@pytest.mark.parametrize("alter", ["staged_yaml", "staged_request", "both_removed"])
def test_a_wall_input_the_session_altered_does_not_open_a_refused_change(fx, alter):
    h03, h20 = changed("unnamed_entry_lines")  # h03's entry 3 changed: refused against the hidden file
    if alter == "staged_yaml":  # the wall's staged copy made to match the delivered question
        files = {"input/h03.yaml": text_of(h03)}
    elif alter == "staged_request":  # the wall's request made to name h03's entry 3
        files = {"input/reanchor.json": json.dumps({"week": WEEK, "changed": ROWS + [{"id": "h03", "entry": 3}]})}
    else:
        files = {"input/h03.yaml": None, "input/reanchor.json": None}
    fx.stub({"session": "write", "out": out_files(**{"out/h03.yaml": text_of(h03), "out/h20.yaml": text_of(h20)})})
    before = tree_hash(fx.setdir)
    rc, counts, p = fx.run(*fx.args(rnd=2), *REA, extra=session_alters_wall(fx, files))
    assert rc == 20 and counts["status"] == "rejected", p.stderr
    assert "reanchor_changed" in (fx.runs / "writer" / counts["run"] / "launch.log").read_text()
    assert tree_hash(fx.setdir) == before
    assert not any(n.endswith(".replaced") for n in os.listdir(fx.sets / WALLS / "writer"))


@pytest.mark.parametrize("alter", ["staged_yaml", "staged_request", "both_removed"])
def test_a_wall_input_the_session_altered_does_not_refuse_a_good_delivery(fx, alter):
    if alter == "staged_yaml":
        files = {"input/h03.yaml": "id: other\n"}
    elif alter == "staged_request":
        files = {"input/reanchor.json": json.dumps({"week": WEEK, "changed": []})}
    else:
        files = {"input/h03.yaml": None, "input/h20.yaml": None, "input/reanchor.json": None}
    fx.stub({"session": "write", "out": out_files()})
    rc, counts, p = fx.run(*fx.args(rnd=2), *REA, extra=session_alters_wall(fx, files))
    assert rc == 0 and counts["status"] == "delivered", p.stderr
    for qid in ("h03", "h20"):
        assert (fx.setdir / "hidden" / f"{qid}.yaml").read_text() == NEW[qid]


def test_a_hidden_file_changed_between_staging_and_delivery_refuses_20_with_the_hidden_half_as_it_was(fx):
    edited = OLD["h20"].replace("old h20", "edited h20")
    target = fx.setdir / "hidden" / "h20.yaml"
    hook = fx.hook("if point == 'after_session':\n"
                   f"    with open({str(target)!r}, 'w') as f:\n"
                   f"        f.write({edited!r})\n")
    fx.stub({"session": "write", "out": out_files()})
    rc, counts, p = fx.run(*fx.args(rnd=2), *REA, extra={"GOV_INDEP_TEST_HOOK": hook})
    assert rc == 20 and counts["status"] == "rejected", p.stderr
    assert "destination" in (fx.runs / "writer" / counts["run"] / "launch.log").read_text()
    assert (fx.setdir / "hidden" / "h03.yaml").read_text() == OLD["h03"]  # nothing replaced, the first id included
    assert target.read_text() == edited and (fx.setdir / "hidden" / "q01.yaml").read_text() == OLD["q01"]
    assert not any(n.endswith(".replaced") for n in os.listdir(fx.sets / WALLS / "writer"))
    assert [n for n in os.listdir(fx.setdir / "hidden") if n.startswith(".") or n.endswith(".tmp")] == []
    for text in (p.stdout, p.stderr):
        assert "ZZMARKER" not in text and "edited" not in text


@pytest.mark.parametrize("delivered", ["kept", "changed", "dropped"])
def test_a_replace_reason_on_the_staged_side_kept_changed_or_dropped_is_accepted(fx, delivered):
    marked = dict(question("h20", "old h20"), replace_reason="marked-earlier")
    (fx.setdir / "hidden" / "h20.yaml").write_text(text_of(marked))
    h20 = reanchored("h20", "old h20")
    if delivered == "kept":
        h20["replace_reason"] = "marked-earlier"
    elif delivered == "changed":
        h20["replace_reason"] = "moved-again"
    fx.stub({"session": "write", "out": out_files(**{"out/h20.yaml": text_of(h20)})})
    rc, counts, p = rea_run(fx)
    assert rc == 0 and counts["status"] == "delivered", p.stderr
    assert yaml.safe_load((fx.setdir / "hidden" / "h20.yaml").read_text()) == h20


@pytest.mark.parametrize("bad", ["", 1, None])
def test_a_delivered_replace_reason_that_is_not_a_non_empty_string_is_refused_even_when_staged(fx, bad):
    marked = dict(question("h20", "old h20"), replace_reason="marked-earlier")
    (fx.setdir / "hidden" / "h20.yaml").write_text(text_of(marked))
    h20 = dict(reanchored("h20", "old h20"), replace_reason=bad)
    fx.stub({"session": "write", "out": out_files(**{"out/h20.yaml": text_of(h20)})})
    before = tree_hash(fx.setdir)
    rc, counts, p = rea_run(fx)
    assert rc == 20 and counts["status"] == "rejected", p.stderr
    assert "reanchor_changed" in (fx.runs / "writer" / counts["run"] / "launch.log").read_text()
    assert tree_hash(fx.setdir) == before


def test_reanchor_same_ignores_a_staged_replace_reason_but_checks_a_delivered_one():
    same = indep_launch.reanchor_same
    a = dict(question("h03", "x"), replace_reason="old")
    b = question("h03", "x")
    assert same(a, b, set()) and same(b, a, set()) and same(a, dict(b, replace_reason="new"), set())
    for bad in ("", 0, None, ["x"]):
        assert not same(a, dict(b, replace_reason=bad), set()) and not same(b, dict(b, replace_reason=bad), set())


def test_a_stopped_result_delivers_nothing_21(fx):
    fx.stub({"session": "write", "out": {"out/result.json": json.dumps(dict(GOOD, stopped="decisions-conflict")),
                                         "out/conflicts.md": "x\n"}})
    before = tree_hash(fx.setdir)
    rc, counts, _ = rea_run(fx)
    assert rc == 21 and counts["status"] == "stopped"
    assert tree_hash(fx.setdir) == before
    assert counts["reanchor"]["corrected"] is None


# -- the counts schema and the documented form ---------------------------------------------------------------------------
def test_the_counts_schema_closes_the_reanchor_object():
    s = json.loads((Path(indep_launch.SCHEMAS) / "indep-counts.schema.json").read_text())
    r = s["properties"]["reanchor"]
    assert r["additionalProperties"] is False
    assert set(r["required"]) == set(r["properties"]) == {"week", "entries", "ids", "absent", "corrected", "replaced"}
    assert "reanchor" not in s["required"]
    good = {"week": WEEK, "entries": 3, "ids": 2, "absent": 0, "corrected": None, "replaced": None}
    sub = dict(s, required=[], properties={"reanchor": r})
    assert indep_launch.schema_ok({"reanchor": good}, sub)
    for bad in (dict(good, note="x"), dict(good, week="2026-W4"), dict(good, ids=-1), dict(good, ids=True),
                dict(good, entries="3"), {k: v for k, v in good.items() if k != "absent"}):
        assert not indep_launch.schema_ok({"reanchor": bad}, sub), bad


def test_the_docstring_has_one_reanchor_usage_line_naming_only_the_sets_root_and_help_omits_it():
    lines = [x.strip() for x in indep_launch.__doc__.splitlines() if x.strip().startswith("python3 ")
             and "--reanchor" in x]
    assert len(lines) == 1
    assert "--set examin --round 2 --reanchor 2026-W47" in lines[0]
    assert WALLS + "/" not in lines[0] and "$" not in lines[0]
    import subprocess
    import sys
    p = subprocess.run([sys.executable, str(indep_launch.__file__), "--help"], capture_output=True, text=True,
                       timeout=60)
    assert p.returncode == 0 and "reanchor" not in p.stdout.lower()


def test_the_planted_declaration_loads_and_a_malformed_one_makes_the_kinds_file_invalid():
    # the repository's own kinds.yaml is not changed by this ticket (the owner's class O; a later ACT adds the line)
    k =yaml.safe_load(kinds_declared())["kinds"]
    assert k["writer"]["input_reanchor"] == ["questions", "reanchor"]
    assert all("input_reanchor" not in k[n] for n in k if n != "writer")
    assert indep_launch.load_kinds(kinds_declared().encode()) is not None
    assert indep_launch.load_kinds((TEMPLATE / "kinds.yaml").read_bytes()) is not None
    for bad in ("[]", "[questions, everything]", "reanchor", "[1]", "{reanchor: 1}"):
        text = kinds_declared().replace("[questions, reanchor]", bad, 1)
        assert indep_launch.load_kinds(text.encode()) is None, bad
