"""W2-173: the engineer's unit tests for the launch script's follow-ups for the memory audit (indep_launch.py).

S1 a brief's `effort` reaches the session as `--effort`, recorded in WALL.json and the counts; S2 a writer's or
checker's `stopped` word ends 21 with nothing delivered; S3 the checker's notes and S4 the auditor's classes are checked
against the audit briefs' fixed form before they are delivered (20 otherwise). Planted roots only, as W2-149's World
(HOME, the sets root, the repository, a stub `claude` on PATH); no real claude, ~/gov-os-eval, ~/gov-os-runs or ~/.claude.
"""
import json
import os

import pytest

from test_w2_149_indep_launch import (SCHEMAS, WALLS, World, indep_launch, sha, tree_hash, schema, assert_counts,
                                      nothing_built, writer_out, SET)
from test_w2_149_setup_a import Sgx, plant_labels

STOP_WORDS = ("input-missing", "input-malformed", "decisions-conflict", "forbidden-read-needed", "form-not-writable",
              "not-sealed")


@pytest.fixture
def w(tmp_path):
    return World(tmp_path)


def with_brief(w, kind, **extra):
    """The kind's planted brief rewritten with *extra* front matter, committed and approved: the new commit."""
    w.put(f"governance/project/indep-briefs/{kind}.md", World.brief_text(kind, **extra))
    c = w.commit_all(f"{kind} brief")
    w.approve(c)
    return c


def flag_values(call, name):
    a = call["argv"]
    return [a[i + 1] for i, x in enumerate(a[:-1]) if x == name]


# -- S1: effort ------------------------------------------------------------------------------------------------------
def test_s1_effort_high_reaches_the_canary_and_the_session_and_the_counts(w):
    c = with_brief(w, "writer", effort="high")
    w.stub({"session": "write", "out": writer_out()})
    rc, counts, p = w.launch(commit=c)
    assert rc == 0, (counts, p.stderr)
    assert_counts(counts, 0, "delivered")
    canary, session = w.calls()
    for call in (canary, session):  # the canary runs with the session's flags (W2-149 S11)
        assert flag_values(call, "--effort") == ["high"]
    assert session["argv"][-1] == indep_launch.PROMPT
    assert counts["effort"] == "high"
    on_disk = json.loads((w.runs / "writer" / counts["run"] / "counts.json").read_text())
    assert on_disk["effort"] == "high"


@pytest.mark.parametrize("value", indep_launch.EFFORTS)
def test_s1_each_of_the_five_is_recorded_in_the_wall_manifest(w, value):
    c = with_brief(w, "writer", effort=value)
    rc, counts, p = w.launch(commit=c, seed=1, dry=True)
    assert rc == 0, (counts, p.stderr)
    assert_counts(counts, 0, "dry")
    m = json.loads((w.wall(counts) / "WALL.json").read_text())
    assert m["effort"] == value and counts["effort"] == value


def test_s1_no_effort_line_no_flag_and_null(w):
    w.stub({"session": "write", "out": writer_out()})
    rc, counts, _ = w.launch()
    assert rc == 0, counts
    assert all("--effort" not in call["argv"] for call in w.calls())
    assert counts["effort"] is None
    assert_counts(counts, 0, "delivered")
    rc, dry, _ = w.launch(seed=1, dry=True)
    assert rc == 0
    assert json.loads((w.wall(dry) / "WALL.json").read_text())["effort"] is None and dry["effort"] is None


@pytest.mark.parametrize("value", ["loud", "High", "3", "", "true", "[high]", "{a: b}", "'high '"])
def test_s1_an_effort_outside_the_five_refuses_10_and_builds_nothing(w, value):
    c = with_brief(w, "writer", effort=value)
    w.stub({"session": "write", "out": writer_out()})
    before = tree_hash(w.sets)
    rc, counts, _ = w.launch(commit=c)
    assert rc == 10, counts
    assert_counts(counts, 10, "refused")
    assert counts["reason"] == "brief" and counts["effort"] is None
    assert tree_hash(w.sets) == before  # the walls folder (and the whole sets root) untouched
    nothing_built(w)
    assert w.calls() == []


def test_s1_a_refusal_before_the_brief_is_read_carries_effort_null(w):
    rc, counts, _ = w.run("--sets-root", str(w.sets), "--kind", "poet")
    assert rc == 17
    assert "effort" in counts and counts["effort"] is None
    assert indep_launch.schema_ok(counts, schema())


def test_s1_the_counts_schema_takes_the_five_or_null_and_nothing_else():
    s = schema()
    e = s["properties"]["effort"]
    assert e["type"] == ["string", "null"] and e["enum"] == ["low", "medium", "high", "xhigh", "max", None]
    base = dict(indep_launch.State().counts, code=17, reason="argument")  # a refusal's line, as finish() writes it
    assert indep_launch.schema_ok(base, s)
    for v in indep_launch.EFFORTS + (None,):
        assert indep_launch.schema_ok(dict(base, effort=v), s)
    for v in ("loud", "", 3, True, ["high"]):
        assert not indep_launch.schema_ok(dict(base, effort=v), s)


def test_s1_the_five_set_up_a_briefs_still_pass_stage_ten_without_effort(tmp_path):
    s = Sgx(tmp_path)
    s.plant_half("tuning")
    plant_labels(s, n=3)
    for bid, half in (("sgx1-writer-tuning", "tuning"), ("sgx1-writer-heldout", "held-out"),
                      ("sgx1-labeller", "tuning"), ("sgx1-labeller-2", "tuning"), ("sgx1-overlap-auditor", "tuning")):
        rc, counts, p = s.go(bid, half=half, seed=5, dry=True)
        assert rc == 0, (bid, counts, p.stderr)
        assert_counts(counts, 0, "dry")
        assert counts["effort"] is None
        assert json.loads((s.wall(counts) / "WALL.json").read_text())["effort"] is None


def test_s1_session_flags_add_effort_only_when_given():
    plain = indep_launch.session_flags("/w", "/t", ["Read"], "m", 1, "sid")
    assert "--effort" not in plain
    high = indep_launch.session_flags("/w", "/t", ["Read"], "m", 1, "sid", effort="high")
    assert high[high.index("--effort") + 1] == "high" and high.count("--effort") == 1
    assert [x for x in high if x not in ("--effort", "high")] == plain


# -- S2: the stop word -------------------------------------------------------------------------------------------------
def checker_ids(n=3):
    return [f"q{i:02d}" for i in range(1, n + 1)]


def plant_checker_set(w, n=3):
    return w.plant_set({f"{i}.yaml": f"id: {i}\nquestion: planted\n" for i in checker_ids(n)})


SET_LINES = ["domains: code 1, decisions 1, tickets 0, plan 0, contract 1, none 0",
             "categories: decision 1, contract 1, plan 0, ticket 0, exact-string 1, callers 0, code-paraphrase 0, "
             "kernel-template 0, multi-file 0, failure-memory 0, history 0, nonexistent-id 0",
             "keyword: any 0, all 0",
             "supersession 0, kernel roles or skills 0, failure or lesson 0, drawn changed 2, drawn sample or none 1",
             "set codes: none"]


def notes_text(rows=None, set_lines=None, head="# Cross-check notes", trailer="\n"):
    rows = rows if rows is not None else [
        "q01 | accept | - | also: docs/a.md#One; docs/b.md#Two | the anchor holds the deciding line",
        "q02 | revise | R6-SPAN-MISSES | also: none | the anchor ends before the deciding line",
        "q03 | reject | R1-WRONG | also: none | the gold names a replaced record"]
    lines = [head, "## Questions", *rows, "## The set", *(set_lines if set_lines is not None else SET_LINES)]
    return "\n".join(lines) + trailer


def checker_result(checked=3, accepted=1, revise=1, rejected=1, **extra):
    return dict({"checked": checked, "accepted": accepted, "revise": revise, "rejected": rejected}, **extra)


def checker_out(notes=None, result=None):
    return {"out/result.json": json.dumps(result if result is not None else checker_result()),
            "out/notes.md": notes if notes is not None else notes_text()}


def writer_stop_out(word):
    out = writer_out()
    res = json.loads(out["out/result.json"])
    res["stopped"] = word
    out["out/result.json"] = json.dumps(res)
    return out


@pytest.mark.parametrize("kind", ["writer", "checker"])
@pytest.mark.parametrize("word", STOP_WORDS)
def test_s2_a_result_that_says_it_stopped_delivers_nothing_and_ends_21(w, kind, word):
    if kind == "checker":
        plant_checker_set(w)
        w.stub({"session": "write", "out": checker_out(result=checker_result(stopped=word))})
    else:
        w.stub({"session": "write", "out": writer_stop_out(word)})
    before = tree_hash(w.sets / "fixtures")
    rc, counts, _ = w.launch(kind)
    assert rc == 21, counts
    assert_counts(counts, 21, "stopped")
    assert counts["reason"] == "stopped" and counts["out"]["stopped"] == word
    assert counts["delivered"] == {"files": 0, "sha256": None, "to": None}
    assert tree_hash(w.sets / "fixtures") == before
    assert (w.sets / WALLS / kind / (counts["run"] + ".tar")).exists() and not w.wall(counts).exists()
    on_disk = json.loads((w.runs / kind / counts["run"] / "counts.json").read_text())
    assert on_disk["out"]["stopped"] == word and on_disk["code"] == 21


def test_s2_a_stopped_result_ends_21_even_with_no_set_or_notes_beside_it(w):
    # the stop is read before the out/ files are looked for: no 20 for the missing set
    w.stub({"session": "write", "out": {"out/result.json": json.dumps(
        {"questions": 0, "by_kind": {}, "by_area": {}, "stopped": "input-missing"})}})
    rc, counts, _ = w.launch()
    assert rc == 21 and counts["out"]["stopped"] == "input-missing", counts
    plant_checker_set(w)
    w.stub({"session": "write", "out": {"out/result.json": json.dumps(
        {"checked": 0, "accepted": 0, "revise": 0, "rejected": 0, "stopped": "input-malformed"})}})
    rc, counts, _ = w.launch("checker")
    assert rc == 21 and counts["out"]["stopped"] == "input-malformed", counts


def test_s2_none_or_absent_delivers_as_before(w):
    w.stub({"session": "write", "out": writer_stop_out("none")})
    rc, counts, _ = w.launch()
    assert rc == 0 and counts["status"] == "delivered", counts
    assert counts["out"].get("stopped") is None


def test_s2_none_or_absent_delivers_as_before_for_the_checker(w):
    plant_checker_set(w)
    for result in (checker_result(stopped="none"), checker_result()):
        w.stub({"session": "write", "out": checker_out(result=result)})
        rc, counts, _ = w.launch("checker")
        assert rc == 0 and counts["delivered"]["to"] == "notes", counts
        assert counts["out"].get("stopped") is None


@pytest.mark.parametrize("word", ["tired", "None", "", 3, None, ["input-missing"]])
def test_s2_a_word_outside_the_seven_is_a_schema_refusal_20(w, word):
    w.stub({"session": "write", "out": writer_stop_out(word)})
    before = tree_hash(w.sets / "fixtures")
    rc, counts, _ = w.launch()
    assert rc == 20, counts
    assert_counts(counts, 20, "rejected")
    assert counts["out"]["schema_ok"] is False and counts["out"].get("stopped") is None
    assert tree_hash(w.sets / "fixtures") == before


def test_s2_the_result_schemas_take_stopped_as_optional():
    for name, good in (("writer-result.schema.json", {"questions": 1, "by_kind": {}, "by_area": {}}),
                       ("checker-result.schema.json", checker_result())):
        s = json.loads((SCHEMAS / name).read_text())
        assert "stopped" not in s.get("required", [])
        assert s["properties"]["stopped"]["enum"] == list(indep_launch.STOPPED)
        assert indep_launch.schema_ok(good, s)  # the first version's result, without stopped
        for word in indep_launch.STOPPED:
            assert indep_launch.schema_ok(dict(good, stopped=word), s)
        for word in ("tired", 1, None):
            assert not indep_launch.schema_ok(dict(good, stopped=word), s)


def test_s2_a_stopped_result_with_a_trace_still_ends_22(w):
    w.stub({"session": "write", "out": writer_stop_out("not-sealed"), "trace_drawn": True})
    rc, counts, _ = w.launch()
    assert rc == 22, counts
    assert counts["status"] == "stopped" and counts["traces"] == 1 and counts["out"]["stopped"] == "not-sealed"


def test_s2_the_auditor_is_not_in_s2(w):
    # an auditor's result with a stop word is checked as today: its schema (open) passes, its classes deliver
    plant_audit(w)
    w.stub({"session": "write", "out": auditor_out(result={"misses": {"retrieval_miss": 2, "gold_wrong": 1},
                                                           "stopped": "input-missing"})})
    rc, counts, _ = w.launch("auditor", audit="e0")
    assert rc == 0 and counts["delivered"]["to"] == "classes", counts
    assert counts["out"].get("stopped") is None


# -- S3: the checker's notes --------------------------------------------------------------------------------------------
def test_s3_well_formed_notes_are_delivered(w):
    plant_checker_set(w)
    text = notes_text()
    w.stub({"session": "write", "out": checker_out(notes=text)})
    rc, counts, _ = w.launch("checker")
    assert rc == 0, counts
    assert_counts(counts, 0, "delivered")
    dst = w.sets / "fixtures" / "evaluation" / SET / "XCHECK-r1.md"
    assert dst.read_text() == text
    assert counts["delivered"] == {"files": 1, "sha256": sha(text.encode()), "to": "notes"}


def bad_notes():
    rows = notes_text().split("\n")[2:5]
    return {
        "a missing line": (notes_text(rows=rows[:2]), checker_result(checked=3)),
        "a missing line, counts following it": (notes_text(rows=rows[:2]), checker_result(2, 1, 1, 0)),
        "a fourth verdict word": (notes_text(rows=[rows[0], rows[1], rows[2].replace("reject", "maybe")]),
                                  checker_result()),
        "an id not in the set": (notes_text(rows=[rows[0], rows[1], rows[2].replace("q03", "q09")]), checker_result()),
        "counts that disagree": (notes_text(), checker_result(3, 2, 1, 0)),
        "checked that disagrees": (notes_text(), checker_result(4, 1, 1, 1)),
        "ids out of order": (notes_text(rows=[rows[1], rows[0], rows[2]]), checker_result()),
        "a line twice": (notes_text(rows=[rows[0], rows[0], rows[1], rows[2]]), checker_result()),
        "another heading": (notes_text(head="# Cross-check notes (draft)"), checker_result()),
        "no set section": ("\n".join(["# Cross-check notes", "## Questions", *rows]) + "\n", checker_result()),
        "four set lines": (notes_text(set_lines=SET_LINES[:4]), checker_result()),
        "set lines out of order": (notes_text(set_lines=[SET_LINES[1], SET_LINES[0], *SET_LINES[2:]]),
                                   checker_result()),
        "a line after the set": (notes_text(set_lines=SET_LINES + ["extra"]), checker_result()),
        "four fields": (notes_text(rows=[rows[0], rows[1], "q03 | reject | R1-WRONG | also: none"]), checker_result()),
        "no also": (notes_text(rows=[rows[0], rows[1], rows[2].replace("also: none", "none")]), checker_result()),
        "an empty sentence": (notes_text(rows=[rows[0], rows[1], "q03 | reject | R1-WRONG | also: none | "]),
                              checker_result()),
        "an empty codes field": (notes_text(rows=[rows[0], rows[1], "q03 | reject |  | also: none | gone"]),
                                 checker_result()),
        "a blank line between two questions": (notes_text(rows=[rows[0], "", rows[1], rows[2]]), checker_result()),
        "two trailing newlines": (notes_text(trailer="\n\n"), checker_result()),
        "CRLF lines": (notes_text().replace("\n", "\r\n"), checker_result()),
        "the stop form": ("# Cross-check notes\ninput-missing: q01\n", checker_result(0, 0, 0, 0)),
    }


@pytest.mark.parametrize("case", sorted(bad_notes()))
def test_s3_notes_that_do_not_fit_are_refused_20_nothing_written(w, case):
    plant_checker_set(w)
    text, result = bad_notes()[case]
    w.stub({"session": "write", "out": checker_out(notes=text, result=result)})
    setdir = w.sets / "fixtures" / "evaluation" / SET
    before = tree_hash(setdir)
    rc, counts, _ = w.launch("checker")
    assert rc == 20, (case, counts)
    assert_counts(counts, 20, "rejected")
    assert counts["delivered"] == {"files": 0, "sha256": None, "to": None}
    assert tree_hash(setdir) == before and not (setdir / "XCHECK-r1.md").exists()


def test_s3_notes_not_utf8_are_refused_20(w):
    plant_checker_set(w)
    w.stub({"session": "write", "out": checker_out()})
    ids = checker_ids()
    with pytest.raises(indep_launch.Refuse) as e:
        indep_launch.check_notes(b"# Cross-check notes\n\xff\n", ids, checker_result())
    assert e.value.code == 20


def test_s3_check_notes_accepts_the_form_and_blank_lines_beside_the_headings():
    ids = checker_ids()
    indep_launch.check_notes(notes_text().encode(), ids, checker_result())
    indep_launch.check_notes(notes_text(trailer="").encode(), ids, checker_result())  # no final newline
    spaced = notes_text().replace("## Questions\n", "\n## Questions\n\n").replace("## The set\n", "\n## The set\n\n")
    indep_launch.check_notes(spaced.encode(), ids, checker_result())
    # a sentence holding " | " stays one field (the fifth), as the next step's reader splits it (at most five)
    piped = notes_text().replace("the gold names a replaced record", "two records | one replaced")
    indep_launch.check_notes(piped.encode(), ids, checker_result())


def test_s3_the_ids_are_the_staged_sets_file_stems_in_order(w):
    # a set with a nested file: its stem is an id too, ordered among the others
    w.plant_set({"q01.yaml": "a\n", "q02.yaml": "b\n", "sub/q03.yaml": "c\n"})
    w.stub({"session": "write", "out": checker_out()})
    rc, counts, _ = w.launch("checker")
    assert rc == 0, counts


def test_s3_a_set_with_one_stem_twice_cannot_be_matched_line_for_file_20(w):
    setdir = w.plant_set({"q01.yaml": "a\n", "q02.yaml": "b\n", "sub/q02.yaml": "c\n"}).parent
    rows = ["q01 | accept | - | also: none | fine", "q02 | accept | - | also: none | fine",
            "q02 | accept | - | also: none | fine"]
    w.stub({"session": "write", "out": checker_out(notes=notes_text(rows=rows), result=checker_result(3, 3, 0, 0))})
    rc, counts, _ = w.launch("checker")
    assert rc == 20, counts
    assert not (setdir / "XCHECK-r1.md").exists()


def test_s3_a_round_two_checker_delivers_its_own_round_and_keeps_round_one(w):
    plant_checker_set(w)
    r1 = w.sets / "fixtures" / "evaluation" / SET / "XCHECK-r1.md"
    r1.write_text("round one\n")
    w.stub({"session": "write", "out": checker_out(notes=notes_text(rows=[
        "q01 | accept | - | also: none | fine", "q02 | accept | - | also: none | fine",
        "q03 | accept | - | also: none | fine"]), result=checker_result(3, 3, 0, 0))})
    rc, counts, _ = w.launch("checker", rnd=2)
    assert rc == 0, counts
    assert r1.read_text() == "round one\n"
    assert (r1.parent / "XCHECK-r2.md").read_text().startswith("# Cross-check notes\n")


# -- S4: the auditor's classes --------------------------------------------------------------------------------------------
MISS_IDS = ["q04", "q11", "q27"]


def plant_audit(w, ids=MISS_IDS):
    w.plant_set()
    folder = w.sets / "runs" / "e0"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "misses.jsonl").write_text("".join(json.dumps(
        {"id": i, "question": "planted", "gold_answer": "x", "gold_sources": [], "answer": "y", "outcome": "wrong",
         "evidence_in_bundle": False}) + "\n" for i in ids))
    return folder


def good_classes():
    return {"q04": {"class": "retrieval_miss", "reason": "memory put no gold place in front of the agent"},
            "q11": {"class": "gold_wrong", "reason": "the gold span ends before the deciding line"},
            "q27": {"class": "retrieval_miss", "reason": "no gold place in the bundle"}}


def auditor_out(classes=None, result=None, raw=None):
    return {"out/result.json": json.dumps(result if result is not None else
                                          {"misses": {"retrieval_miss": 2, "gold_wrong": 1}}),
            "out/classes.json": raw if raw is not None else json.dumps(classes if classes is not None
                                                                       else good_classes())}


def test_s4_well_formed_classes_are_delivered_and_the_audit_logged(w):
    folder = plant_audit(w)
    out = auditor_out()
    w.stub({"session": "write", "out": out})
    rc, counts, _ = w.launch("auditor", audit="e0")
    assert rc == 0, counts
    assert_counts(counts, 0, "delivered")
    assert (folder / "miss-classes.json").read_text() == out["out/classes.json"]
    line = json.loads((w.runs / "AUDITS.log").read_text().splitlines()[-1])
    assert line["run"] == counts["run"] and line["audit"] == "e0"


def bad_classes():
    g = good_classes()
    res = {"misses": {"retrieval_miss": 2, "gold_wrong": 1}}
    two = {k: v for k, v in g.items() if k != "q27"}
    return {
        "a missing id": (json.dumps(two), res),
        "a missing id, counts following it": (json.dumps(two), {"misses": {"retrieval_miss": 1, "gold_wrong": 1}}),
        "an extra id": (json.dumps(dict(g, q99={"class": "gold_wrong", "reason": "x"})),
                        {"misses": {"retrieval_miss": 2, "gold_wrong": 2}}),
        "a sixth class": (json.dumps(dict(g, q27={"class": "unlucky", "reason": "x"})), res),
        "a two-line reason": (json.dumps(dict(g, q27={"class": "retrieval_miss", "reason": "one\ntwo"})), res),
        "a carriage return": (json.dumps(dict(g, q27={"class": "retrieval_miss", "reason": "one\rtwo"})), res),
        "a reason of 201 characters": (json.dumps(dict(g, q27={"class": "retrieval_miss", "reason": "x" * 201})), res),
        "counts that disagree": (json.dumps(g), {"misses": {"retrieval_miss": 3}}),
        "counts that disagree by a zero": (json.dumps(g), {"misses": {"retrieval_miss": 2, "gold_wrong": 0}}),
        "a bare class string": (json.dumps(dict(g, q27="retrieval_miss")), res),
        "no reason": (json.dumps(dict(g, q27={"class": "retrieval_miss"})), res),
        "a reason that is not a string": (json.dumps(dict(g, q27={"class": "retrieval_miss", "reason": 7})), res),
        "a list": (json.dumps(list(g)), res),
        "not JSON": ("{not json", res),
        "an id twice": (json.dumps(g)[:-1] + ', "q27": {"class": "retrieval_miss", "reason": "again"}}', res),
    }


@pytest.mark.parametrize("case", sorted(bad_classes()))
def test_s4_classes_that_do_not_fit_are_refused_20_nothing_written(w, case):
    folder = plant_audit(w)
    raw, result = bad_classes()[case]
    w.stub({"session": "write", "out": auditor_out(raw=raw, result=result)})
    before = tree_hash(folder)
    rc, counts, _ = w.launch("auditor", audit="e0")
    assert rc == 20, (case, counts)
    assert_counts(counts, 20, "rejected")
    assert tree_hash(folder) == before and not (folder / "miss-classes.json").exists()
    assert not (w.runs / "AUDITS.log").exists()


def test_s4_a_reason_of_200_characters_and_an_empty_misses_file_pass():
    ids = ["q01"]
    indep_launch.check_classes(json.dumps({"q01": {"class": "out_of_scope", "reason": "y" * 200}}).encode(), ids,
                               {"misses": {"out_of_scope": 1, "gold_wrong": 0}})
    indep_launch.check_classes(b"{}\n", [], {"misses": {}})
    indep_launch.check_classes(b"{}", [], {"misses": {c: 0 for c in indep_launch.MISS_CLASSES}})


def test_s4_an_unreadable_misses_file_refuses_20(w):
    folder = plant_audit(w)
    (folder / "misses.jsonl").write_text('{"question": "no id"}\n')
    w.stub({"session": "write", "out": auditor_out(classes={})})
    rc, counts, _ = w.launch("auditor", audit="e0")
    assert rc == 20, counts
    assert not (folder / "miss-classes.json").exists()


# -- S5: the codes keep their meaning ----------------------------------------------------------------------------------
def test_s5_the_exit_codes_and_reasons_are_as_at_the_base():
    assert indep_launch.CODES == {10: "brief", 11: "template", 12: "wall_exists", 13: "seed_order", 14: "commit",
                                  15: "file_budget", 16: "canary", 17: "argument", 18: "rules", 20: "result",
                                  21: "stopped", 22: "trace"}
    assert indep_launch.STOPPED == ("none",) + STOP_WORDS
