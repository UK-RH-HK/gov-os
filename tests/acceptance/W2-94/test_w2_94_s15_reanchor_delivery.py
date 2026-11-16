"""W2-94 (DAEO-g87r), reopened 2026-11-15 (DEC-1186 (4)): the walls launcher's ``--reanchor <week>`` flow, delivery (S15,
the failure line "S14/S15's failure" for delivery, and F1 for leaks).

Written from the KPI lines and the lead's interface text, never from the engineer's work. The stub ``claude`` writes the
delivered files given by each case; the rename-failure cases run ``indep_launch.main(argv)`` in-process with the
module's ``os.replace`` wrapped. Planted words begin with ``zqxw94``.
"""

from __future__ import annotations

import copy
import json
import os

import pytest

from w2_94_reanchor_support import (DROP, NEW_MARKERS, SETN, STAGED_STEMS, UID, WEEK, ReanchorWorld, dump,
                                    good_delivered, indep_launch, m, out_files, result_json, schema)


@pytest.fixture
def rw(tmp_path):
    return ReanchorWorld(tmp_path)


def no_leaks(w):
    hits = w.leaks()
    assert hits == [], f"F1: planted hidden strings outside the sets root: {hits[:4]}"


NOT_STAGED = ("hidden/q03.yaml", "hidden/visible/q04.yaml", "hidden/dropped/q05.yaml", "hidden/DRAW.txt")


def stats(w):
    return {rel: (os.stat(w.setdir / rel).st_ino, os.stat(w.setdir / rel).st_mtime_ns) for rel in NOT_STAGED}


def rel_set(stem):
    return os.path.join("fixtures", "evaluation", SETN, "hidden", f"{stem}.yaml")


# =====================================================================================================================
# S15 -- a good delivery
# =====================================================================================================================
def test_s15_a_good_delivery_replaces_exactly_the_staged_files_and_keeps_the_old_ones_in_the_tar(rw):
    """S15 (interface 5): exit 0; the three staged ids' hidden files hold the delivered mappings; every other file under
    the set's folder is byte-unchanged and a hidden file not requested keeps its inode and mtime; the run's tar holds
    each old file as replaced-hidden/<stem>.yaml and no other; no `.replaced` folder is left; the session saw exactly
    the staged inputs."""
    delivered = good_delivered(rw)
    rw.session(out_files(rw, delivered))
    old = {s: (rw.hidden / f"{s}.yaml").read_bytes() for s in STAGED_STEMS}
    before, st = rw.set_files(), stats(rw)
    rc, counts, p = rw.ra()
    assert rc == 0, (counts, p.stderr)
    assert counts["status"] == "delivered"
    after = rw.set_files()
    changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    assert changed == sorted(rel_set(s) for s in STAGED_STEMS), changed
    import yaml
    for s in STAGED_STEMS:
        assert yaml.safe_load((rw.hidden / f"{s}.yaml").read_text()) == delivered[s], s
    assert stats(rw) == st
    run = counts["run"]
    members = rw.tar_members(run)
    kept = {n: b for n, b in members.items() if n.startswith(f"{run}/replaced-hidden/") and b is not None}
    assert kept == {f"{run}/replaced-hidden/{s}.yaml": old[s] for s in STAGED_STEMS}
    for folder, dirs, files in os.walk(rw.setdir):
        assert ".replaced" not in dirs + files, folder
    assert rw.calls()[-1]["input"] == sorted([f"{s}.yaml" for s in STAGED_STEMS] + ["reanchor.json",
                                                                                    "selection.json"])
    no_leaks(rw)


def test_s15_the_delivered_counts_carry_the_six_reanchor_numbers_and_validate(rw):
    """S15 / interface 6: on delivery the counts' reanchor is {week, entries 5, ids 3, absent 1, corrected 2,
    replaced 1}; stdout and counts.json agree and validate against the counts schema."""
    rw.session(out_files(rw))
    rc, counts, p = rw.ra()
    assert rc == 0, (counts, p.stderr)
    assert counts["reanchor"] == {"week": WEEK, "entries": 5, "ids": 3, "absent": 1, "corrected": 2, "replaced": 1}
    assert json.loads((rw.runs / "writer" / counts["run"] / "counts.json").read_text()) == counts
    assert indep_launch.schema_ok(counts, schema())
    no_leaks(rw)


def test_s15_only_cited_keys_and_a_replace_reason_may_change_and_are_accepted(rw):
    """S15 (interface 5, delivered against staged): changing only the named entries' path, lines, heading and commit
    (added, changed, removed), and adding a non-empty replace_reason, is accepted; an alternative left as it is too."""
    q1 = rw.staged("Q01")
    q1["sources"][0].update(path="docs/x-moved.md", commit=rw.commit)
    del q1["sources"][0]["heading"]
    q1["sources"][1][0].update(lines=[9, 9], commit=rw.commit)
    q1["replace_reason"] = "moved-out"
    delivered = dict(good_delivered(rw), Q01=q1)
    rw.session(out_files(rw, delivered, result=result_json(corrected=1, replaced=2)))
    rc, counts, p = rw.ra()
    assert rc == 0, (counts, p.stderr)
    assert counts["reanchor"]["corrected"] == 1 and counts["reanchor"]["replaced"] == 2
    no_leaks(rw)


# a question marked in an earlier week: the staged hidden file already carries a top-level replace_reason
# (the ticket's S15: "plus an optional top-level `replace_reason`"; the lead's point 2: ignored on both sides)
OLD_REASON = m("q02", "replace-reason-old")
NEW_REASON = m("q02", "replace-reason-new")


def _plant_staged_reason(w):
    d = w.staged("q02")
    d["replace_reason"] = OLD_REASON
    (w.hidden / "q02.yaml").write_text(dump(d), encoding="utf-8")
    w.markers += [OLD_REASON, NEW_REASON]


STAGED_REASON_KEPT = {"kept": lambda d: None, "changed": lambda d: d.update(replace_reason=NEW_REASON),
                      "removed": lambda d: d.pop("replace_reason")}


@pytest.mark.parametrize("form", list(STAGED_REASON_KEPT))
def test_s15_a_staged_replace_reason_kept_changed_or_removed_is_accepted(rw, form):
    """S15 (the lead's point 2, amending interface 5): a staged hidden file that already carries a top-level
    replace_reason is delivered re-anchored with that replace_reason kept, changed to another non-empty string, or
    removed: each is accepted (exit 0) and the delivered mapping lands as delivered."""
    _plant_staged_reason(rw)
    delivered = good_delivered(rw)
    assert delivered["q02"]["replace_reason"] == OLD_REASON
    STAGED_REASON_KEPT[form](delivered["q02"])
    rw.session(out_files(rw, delivered))
    rc, counts, p = rw.ra()
    assert rc == 0, (rc, counts, p.stderr)
    assert counts["status"] == "delivered"
    import yaml
    assert yaml.safe_load((rw.hidden / "q02.yaml").read_text()) == delivered["q02"]
    no_leaks(rw)


STAGED_REASON_BAD = {"emptied": "", "a number": 3, "null": None, "a list": [NEW_REASON]}


@pytest.mark.parametrize("form", list(STAGED_REASON_BAD))
def test_s15_failure_a_staged_replace_reason_delivered_not_a_non_empty_string_is_20(rw, form):
    """S15 (interface 5 with the lead's point 2): when the staged file carries a replace_reason, a delivered
    replace_reason that is not a non-empty string (empty, a number, null, a list) is still refused 20, nothing
    replaced."""
    _plant_staged_reason(rw)
    delivered = good_delivered(rw)
    delivered["q02"]["replace_reason"] = STAGED_REASON_BAD[form]
    rw.session(out_files(rw, delivered))
    before = rw.set_files()
    rc, counts, p = rw.ra()
    assert rc == 20, (rc, counts, p.stderr)
    assert counts["status"] == "rejected"
    assert rw.set_files() == before
    no_leaks(rw)


# =====================================================================================================================
# S15 / failure -- all or nothing: a failure at a rename leaves the hidden half byte-identical
# =====================================================================================================================
@pytest.mark.parametrize("at", ["first", "second", "last"])
def test_s15_failure_a_delivery_failing_at_a_rename_is_20_and_leaves_the_hidden_half_byte_identical(
        tmp_path, monkeypatch, capsys, at):
    """S15 / S14-S15's failure ("a partial delivery"): in-process, the module's os.replace raising at the 1st, 2nd or
    last call whose target lies directly in the set's hidden folder gives 20; the hidden half is byte-identical with no
    temporary file left in it, and nothing else of the set changed."""
    counting = ReanchorWorld(tmp_path / "count")
    counting.session(out_files(counting))
    rc, counts, calls = counting.inproc(monkeypatch, capsys, counting.ra_argv())
    assert rc == 0, counts
    n = len(calls)
    assert n >= len(STAGED_STEMS), f"the delivery made {n} os.replace calls into the hidden folder"
    k = {"first": 1, "second": 2, "last": n}[at]
    w = ReanchorWorld(tmp_path / "fail")
    w.session(out_files(w))
    before_hidden, before_set = w.state()["sets"], w.set_files()
    rc, counts, calls = w.inproc(monkeypatch, capsys, w.ra_argv(), fail_at=k)
    assert len(calls) >= k
    assert rc == 20, counts
    assert counts.get("status") == "rejected"
    assert w.set_files() == before_set
    hidden_prefix = os.path.join("fixtures", "evaluation", SETN, "hidden")
    after = w.state()["sets"]
    assert {x: v for x, v in after.items() if x.startswith(hidden_prefix)} == {
        x: v for x, v in before_hidden.items() if x.startswith(hidden_prefix)}
    no_leaks(w)
    no_leaks(counting)


# =====================================================================================================================
# S15 / failure -- delivered against staged: any change but the cited keys of named entries is 20, nothing replaced
# =====================================================================================================================
def _q(stem, fn):
    def make(w):
        d = good_delivered(w)
        fn(d[stem], w)
        return d
    return make


def _set(key, value):
    def fn(d, w):
        d[key] = value
    return fn


def _del(key):
    def fn(d, w):
        del d[key]
    return fn


def _src(fn):
    return lambda d, w: fn(d["sources"])


BAD_DELIVERED = {
    "the question text changed": _q("Q01", lambda d, w: d.update(question=d["question"] + "-x")),
    "the gold answer changed": _q("Q01", lambda d, w: d.update(gold_answer=d["gold_answer"] + "-x")),
    "the category changed": _q("Q01", _set("category", "fact")),
    "the id changed": _q("Q01", _set("id", "Q09")),
    "the id in another case": _q("Q01", _set("id", "q01")),
    "the question's own commit changed": _q("Q01", _set("commit", "1" * 40)),
    "a top-level key removed": _q("Q01", _del("keyword")),
    "a top-level key added": _q("Q01", _set("note", "x")),
    "replace_reason empty": _q("Q01", _set("replace_reason", "")),
    "replace_reason a number": _q("Q01", _set("replace_reason", 3)),
    "an unnamed entry's lines changed": _q("Q01", _src(lambda s: s[2].update(lines=[1, 2]))),
    "an unnamed entry given a commit": _q("q02", lambda d, w: d["sources"][0].update(commit=w.commit)),
    "an unnamed alternative entry changed": _q("q02", _src(lambda s: s[2].update(path="docs/other.md"))),
    "an entry appended": _q("Q01", _src(lambda s: s.append({"path": "docs/new.md", "lines": [1, 2]}))),
    "an entry removed": _q("Q01", _src(lambda s: s.pop())),
    "sources a mapping": _q(UID, lambda d, w: d.update(sources={"path": "docs/x.md"})),
    "a named mapping made a list": _q("Q01", _src(lambda s: s.__setitem__(0, [s[0]]))),
    "a named list made a mapping": _q("Q01", _src(lambda s: s.__setitem__(1, s[1][0]))),
    "a named list shortened": _q("Q01", _src(lambda s: s.__setitem__(1, s[1][:1]))),
    "a named list lengthened": _q("Q01", _src(lambda s: s[1].append(copy.deepcopy(s[1][0])))),
    "a named entry's non-cited key changed": _q("Q01", _src(lambda s: s[0].update(note=s[0]["note"] + "-x"))),
    "a named alternative's non-cited key changed": _q("Q01", _src(lambda s: s[1][0].update(role="x"))),
    "a non-cited key added to a named entry": _q("Q01", _src(lambda s: s[0].update(extra="x"))),
    "a non-cited key removed from a named entry": _q("Q01", _src(lambda s: s[0].pop("note"))),
    "a non-cited key removed from a named alternative": _q("Q01", _src(lambda s: s[1][1].pop("role"))),
}


@pytest.mark.parametrize("name", list(BAD_DELIVERED))
def test_s15_failure_a_delivered_file_differing_beyond_the_cited_keys_is_20_with_nothing_replaced(rw, name):
    """S15 / S14-S15's failure ("a delivered file whose question, answer or unnamed entries changed"): the question
    text, the gold answer, the category, the id, any other top-level key, an unnamed entry, a named entry's shape, or a
    non-cited key of a named entry or alternative changed: 20, every file under the set unchanged."""
    rw.session(out_files(rw, BAD_DELIVERED[name](rw)))
    before = rw.set_files()
    rc, counts, p = rw.ra()
    assert rc == 20, (rc, counts, p.stderr)
    assert counts["status"] == "rejected"
    assert rw.set_files() == before
    no_leaks(rw)


# =====================================================================================================================
# S15 -- out/ holds exactly the staged ids' files and the result; each a plain UTF-8 YAML mapping
# =====================================================================================================================
def _hook_link(w):
    target = w.tmp / "elsewhere.yaml"
    target.write_text((w.hidden / "q02.yaml").read_text())
    return ["p = os.path.join(wall, 'out', 'q02.yaml')", "os.unlink(p)", f"os.symlink({str(target)!r}, p)"]


OUT_BREAKS = {
    "a staged id's file missing": dict(out=lambda w: out_files(w, drop=("q02",))),
    "the result missing": dict(out=lambda w: out_files(w, result=DROP)),
    "an extra question file": dict(out=lambda w: out_files(w, add={"out/q03.yaml": "id: q03\n"})),
    "a file in the absent id's name": dict(out=lambda w: out_files(w, add={"out/q77.yaml": "id: q77\n"})),
    "an extra text file": dict(out=lambda w: out_files(w, add={"out/notes.txt": "x\n"})),
    "conflicts.md on a delivered result": dict(out=lambda w: out_files(w, add={"out/conflicts.md": "classes\n"})),
    "a file in another spelling": dict(out=lambda w: {**{k.replace("Q01", "q01"): v for k, v in out_files(w).items()}}),
    "an extra file in a folder": dict(out=lambda w: out_files(w, add={"out/sub/x.yaml": "x: 1\n"})),
    "an empty extra folder": dict(hook=lambda w: ["os.mkdir(os.path.join(wall, 'out', 'empty'))"]),
    "a question file a link": dict(hook=_hook_link),
    "a question file a folder": dict(hook=lambda w: ["p = os.path.join(wall, 'out', 'q02.yaml')", "os.unlink(p)",
                                                     "os.mkdir(p)"]),
    "a question file not UTF-8": dict(hook=lambda w: [
        "open(os.path.join(wall, 'out', 'q02.yaml'), 'wb').write(b'id: q02\\nquestion: \\xff\\xfe\\n')"]),
    "a question file not YAML": dict(q02="id: [unclosed\n"),
    "a question file a YAML list": dict(q02="- id: q02\n"),
    "a question file a YAML scalar": dict(q02="just text\n"),
    "a question file empty": dict(q02=""),
}


@pytest.mark.parametrize("name", list(OUT_BREAKS))
def test_s15_out_files_other_than_exactly_the_staged_ids_and_the_result_are_20_with_nothing_replaced(rw, name):
    """S15 (interface 5): a missing or extra file, conflicts.md beside a delivered result, a file not a plain UTF-8
    YAML mapping: 20, nothing replaced."""
    spec = OUT_BREAKS[name]
    if "q02" in spec:
        d = good_delivered(rw)
        d["q02"] = spec["q02"]
        out = out_files(rw, d)
    elif "out" in spec:
        out = spec["out"](rw)
    else:
        out = out_files(rw)
    env = rw.session(out, hook_lines=spec["hook"](rw) if "hook" in spec else None)
    before = rw.set_files()
    rc, counts, p = rw.ra(extra=env)
    assert rc == 20, (rc, counts, p.stderr)
    assert counts["status"] == "rejected"
    assert rw.set_files() == before
    no_leaks(rw)


# =====================================================================================================================
# S15 -- the result: the writer schema plus corrected and replaced, summing to the staged ids; stopped delivers nothing
# =====================================================================================================================
BAD_RESULTS = {
    "questions 2": dict(questions=2), "questions 4": dict(questions=4), "questions absent": dict(questions=DROP),
    "questions a string": dict(questions="3"),
    "by_kind sums to 2": dict(by_kind={"location": 2}), "by_kind sums to 4": dict(by_kind={"location": 2, "fact": 2}),
    "by_kind absent": dict(by_kind=DROP), "by_kind an unknown word": dict(by_kind={"location": 2, "poem": 1}),
    "by_area sums to 2": dict(by_area={"code": 2}), "by_area sums to 4": dict(by_area={"code": 2, "docs": 2}),
    "by_area absent": dict(by_area=DROP),
    "corrected plus replaced 2": dict(corrected=1, replaced=1),
    "corrected plus replaced 4": dict(corrected=3, replaced=1),
    "corrected absent": dict(corrected=DROP), "replaced absent": dict(replaced=DROP),
    "corrected true": dict(corrected=True, replaced=2), "replaced a string": dict(replaced="1"),
    "corrected negative": dict(corrected=-1, replaced=4), "replaced null": dict(replaced=None),
    "not JSON": "raw:{not json", "a JSON list": "raw:[]",
}


@pytest.mark.parametrize("name", list(BAD_RESULTS))
def test_s15_a_result_of_a_wrong_form_is_20_with_nothing_replaced(rw, name):
    """S15 (interface 5): questions not the staged count, by_kind or by_area not summing to it, corrected + replaced
    not equal to it, either missing or not a non-negative integer, not a JSON object: 20, nothing replaced."""
    spec = BAD_RESULTS[name]
    result = spec[4:] if isinstance(spec, str) else result_json(**spec)
    rw.session(out_files(rw, result=result))
    before = rw.set_files()
    rc, counts, p = rw.ra()
    assert rc == 20, (rc, counts, p.stderr)
    assert counts["status"] == "rejected"
    assert rw.set_files() == before
    no_leaks(rw)


@pytest.mark.parametrize("form", ["no question files", "with the question files"])
def test_s15_a_stopped_result_is_21_with_nothing_replaced_and_null_result_numbers(rw, form):
    """S15 (interface 5, 6): a result whose `stopped` is not `none` delivers nothing (21); the counts' reanchor holds
    null for corrected and replaced and the counts validate."""
    stop = json.dumps({"questions": 0, "by_kind": {}, "by_area": {}, "stopped": "input-missing"})
    if form == "no question files":
        out = {"out/result.json": stop, "out/conflicts.md": "path classes\n"}
    else:
        out = out_files(rw, result=result_json(stopped="decisions-conflict"), add={"out/conflicts.md": "classes\n"})
    rw.session(out)
    before = rw.set_files()
    rc, counts, p = rw.ra()
    assert rc == 21, (rc, counts, p.stderr)
    assert counts["status"] == "stopped"
    assert rw.set_files() == before
    assert counts["reanchor"]["corrected"] is None and counts["reanchor"]["replaced"] is None
    assert counts["reanchor"]["week"] == WEEK
    assert indep_launch.schema_ok(counts, schema())
    no_leaks(rw)


# =====================================================================================================================
# F1 -- no planted string outside the sets root, across every outcome
# =====================================================================================================================
def test_f1_the_scan_finds_a_planted_string_placed_outside_the_sets_root(rw):
    """F1 (the scan itself): every planted string is in the planted set, and one written under the planted HOME is
    found, so a 0-hit result means something."""
    blob = b"".join(p.read_bytes() for p in rw.setdir.rglob("*") if p.is_file())
    assert all(mk.encode() in blob for mk in rw.markers)
    assert any(UID in p.name for p in rw.hidden.iterdir())
    probe = rw.home / "probe.txt"
    probe.write_text(rw.markers[0])
    assert rw.leaks() != []
    probe.unlink()
    (rw.home / f"{UID}.log").write_text("x")
    assert rw.leaks() != []


def test_f1_no_planted_string_leaves_the_sets_root_across_every_outcome(rw):
    """F1 (S14-S15's failure, "hidden content outside the walls"): one world launched to 17, 11-free 10, 14, a dry
    wall, 20, 21 and a delivery; after each, stdout, stderr, the counts and every file under the planted HOME (runs and
    trees folders) and repository hold no planted question, answer, heading, path, the unique id or its file name."""
    seen = []
    rc, _, _ = rw.ra(week="2026-W4")
    seen.append(rc)
    good = rw.request()
    rw.write_request(rw.request(note="x"))
    seen.append(rw.dry()[0])
    rw.write_request(rw.request(audit_commit="0" * 40))
    seen.append(rw.dry()[0])
    rw.write_request(good)
    seen.append(rw.dry()[0])
    no_leaks(rw)
    bad = good_delivered(rw)
    bad["Q01"]["question"] += "-x"
    rw.session(out_files(rw, bad))
    seen.append(rw.ra()[0])
    rw.session({"out/result.json": json.dumps({"questions": 0, "by_kind": {}, "by_area": {}, "stopped": "input-missing"}),
                "out/conflicts.md": "path classes\n"})
    seen.append(rw.ra()[0])
    rw.session(out_files(rw))
    seen.append(rw.ra()[0])
    assert seen == [17, 10, 14, 0, 20, 21, 0]
    no_leaks(rw)
    assert all(mk in (rw.hidden / "Q01.yaml").read_text() for mk in NEW_MARKERS[:3])
