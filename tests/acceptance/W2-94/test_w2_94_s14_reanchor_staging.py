"""W2-94 (DAEO-g87r), reopened 2026-11-15 (DEC-1186 (4)): the walls launcher's ``--reanchor <week>`` flow, staging (S14,
and the failure line "S14/S15's failure" for staging; F1 for leaks).

Written from the KPI lines and the lead's interface text, never from the engineer's work. Every case runs
``indep_launch.py`` on a planted world (``w2_94_reanchor_support.ReanchorWorld``) with the stub ``claude``. Planted words
begin with ``zqxw94``. Nothing under ``~/gov-os-eval``, ``~/gov-os-runs`` or ``~/gov-os-wall-trees`` is opened.
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys

import pytest

from w2_94_reanchor_support import (CODE, COUNTS_KEYS, DROP, EXPECTED_CHANGED, ROWS, SCRIPT, SETN, STAGED_STEMS, UID,
                                    WALLS, WEEK, ReanchorWorld, indep_launch, schema)


@pytest.fixture
def rw(tmp_path):
    return ReanchorWorld(tmp_path)


def unchanged(w, before, what):
    after = w.state()
    changed = sorted({k for part in before for k in set(before[part]) | set(after[part])
                      if before[part].get(k) != after[part].get(k)})
    assert not changed, f"{what}: something was built or changed: {changed[:6]}"


def no_leaks(w):
    hits = w.leaks()
    assert hits == [], f"F1: planted hidden strings outside the sets root: {hits[:4]}"


# =====================================================================================================================
# S14 -- the flag: --kind writer --round 2 only, never with --fix/--reason or --counts-only, the week's form; else 17
# =====================================================================================================================
BAD_WEEKS = ["2026-W4", "2026-W460", "2026W46", "2026-w46", "26-W46", "2026-W46\n", " 2026-W46", "2026-W46 ", "",
             "２０２６-W46", "2026-W4٦", "2026-46", "2026-WW46", "2026-W46,2026-W47"]


def test_s14_each_wrong_flag_form_is_17_with_nothing_built_and_the_good_form_is_not(rw):
    """S14 (interface 1): another kind, round 1, no round, with --fix/--reason, a bad week: 17, no wall, tree or run
    folder; then the control: the good form's dry run exits 0 (the unchanged script refuses every form with 17)."""
    before = rw.state()
    forms = {"kind checker": dict(kind="checker"), "kind auditor": dict(kind="auditor"),
             "kind labeller": dict(kind="labeller"), "round 1": dict(rnd=1), "no --round": dict(rnd=None),
             "with --fix and --reason": dict(more=["--fix", "q02", "--reason", CODE]),
             "with --fix": dict(more=["--fix", "q02"]), "with --reason": dict(more=["--reason", CODE])}
    forms.update({f"week {wk!r}": dict(week=wk) for wk in BAD_WEEKS})
    wrong = {}
    for name, kw in forms.items():
        rc, counts, _ = rw.ra(**kw)
        if rc != 17 or counts.get("code") != 17:
            wrong[name] = rc
    assert not wrong, f"not refused 17: {wrong}"
    unchanged(rw, before, "a refused flag form")
    rc, counts, p = rw.dry()
    assert rc == 0, (counts, p.stderr)
    assert counts["status"] == "dry"
    no_leaks(rw)


def test_s14_counts_only_with_the_flag_is_17_and_without_it_prints_the_counts(rw):
    """S14 (interface 1): --counts-only takes no --reanchor (17); the same counts-only call without it exits 0."""
    rc, counts, p = rw.dry()
    assert rc == 0, (counts, p.stderr)
    run = counts["run"]
    before = rw.state()
    rc17, c17, _ = rw.run("--sets-root", str(rw.sets), "--kind", "writer", "--run", run, "--counts-only",
                          "--reanchor", WEEK)
    assert rc17 == 17 and c17.get("code") == 17
    unchanged(rw, before, "counts-only with --reanchor")
    rc0, again, _ = rw.run("--sets-root", str(rw.sets), "--kind", "writer", "--run", run, "--counts-only")
    assert rc0 == 0 and again == counts
    no_leaks(rw)


def _doc():
    return ast.get_docstring(ast.parse(SCRIPT.read_text()), clean=False)


def test_s14_one_usage_line_names_reanchor_with_only_the_sets_root_and_help_does_not_list_it():
    """S14 (interface 1): exactly one docstring line holds --reanchor; it names only --sets-root <root> as a path, the
    writer's round 2, a week of the right form and no --fix; --help's option list does not offer --reanchor."""
    lines = [ln.strip() for ln in _doc().splitlines() if "--reanchor" in ln]
    assert len(lines) == 1, lines
    words = lines[0].split()
    assert words[0] == "python3"
    assert words.count("--sets-root") == 1
    root = words[words.index("--sets-root") + 1]
    assert WALLS + "/" not in lines[0] and "fixtures/evaluation" not in lines[0] and "/runs/" not in lines[0]
    assert not any(c in lines[0] for c in "$*?[{<>|;&`"), lines[0]
    assert not [x for x in words if x != root and x.startswith(root.rstrip("/") + "/")]
    assert "--kind writer" in lines[0] and "--round 2" in lines[0]
    assert "--fix" not in words and "--reason" not in words and "--counts-only" not in words
    import re
    assert re.fullmatch(r"[0-9]{4}-W[0-9]{2}", words[words.index("--reanchor") + 1])
    p = subprocess.run([sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True, timeout=60)
    assert p.returncode == 0
    assert "--reanchor" not in p.stdout.split("The documented lines")[0]


# =====================================================================================================================
# S14 -- the template: the writer kind must declare input_reanchor (else 11, nothing built)
# =====================================================================================================================
KINDS_FORMS = {"undeclared": None, "an empty list": "[]", "without reanchor": "[questions]",
               "an unknown word": "[questions, reanchor, notes]", "a string": "reanchor", "null": "null",
               "a list of numbers": "[1, 2]", "a mapping": "{reanchor: true}"}


@pytest.mark.parametrize("name", list(KINDS_FORMS))
def test_s14_an_undeclared_or_malformed_input_reanchor_is_11_with_nothing_built(tmp_path, name):
    """S14 (interface 2): the template's kinds.yaml without input_reanchor under the writer, or with a malformed value,
    refuses 11 before the request is read (a well-formed request is planted)."""
    w = ReanchorWorld(tmp_path, declare=KINDS_FORMS[name])
    before = w.state()
    rc, counts, p = w.dry()
    assert rc == 11, (rc, counts, p.stderr)
    assert counts["status"] == "refused" and counts["code"] == 11
    unchanged(w, before, name)
    no_leaks(w)


def test_s14_input_reanchor_holding_reanchor_alone_is_accepted(tmp_path):
    """S14 (interface 2): a non-empty list holding `reanchor` is a declaration; the dry run builds its wall."""
    w = ReanchorWorld(tmp_path, declare="[reanchor]")
    rc, counts, p = w.dry()
    assert rc == 0, (counts, p.stderr)
    no_leaks(w)


def test_s14_the_checks_run_in_order_arguments_template_request_commit(tmp_path):
    """S14 (interface 3, order): a bad week beats an undeclared template (17); an undeclared template beats a malformed
    request (11); a malformed request beats a foreign audit commit (10)."""
    u = ReanchorWorld(tmp_path / "u", declare=None)
    u.write_request(u.request(extra_key=1))
    assert u.dry(week="2026-W4")[0] == 17
    assert u.dry()[0] == 11
    d = ReanchorWorld(tmp_path / "d")
    d.write_request(d.request(extra_key=1, audit_commit="0" * 40))
    assert d.dry()[0] == 10
    no_leaks(u)
    no_leaks(d)


# =====================================================================================================================
# S14 -- the request's form (else 10, nothing built) and its commit (else 14, nothing staged)
# =====================================================================================================================
def _rows(n, extra=()):
    return [{"id": "Q01", "entry": 1}] + [{"id": f"a{i:03d}", "entry": 1} for i in range(n - 1)] + list(extra)


def _req(**changes):
    return lambda w: w.write_request(w.request(**changes))


def _req_rows(rows, **changes):
    return lambda w: w.write_request(w.request(rows=rows, **changes))


def _bytes(data):
    return lambda w: w.write_request(data)


def _link(w):
    good = w.sets / "runs" / SETN / "good.json"
    good.write_text(json.dumps(w.request()))
    w.request_path.unlink()
    os.symlink("good.json", w.request_path)


def _folder(w):
    w.request_path.unlink()
    w.request_path.mkdir()
    (w.request_path / "x.json").write_text(json.dumps(w.request()))


def _absent(w):
    w.request_path.unlink()


def _oversize(w):
    body = json.dumps(w.request())
    w.write_request((body[:-1] + " " * (8 << 20) + "}\n").encode())


def _one_row_count_true(w):
    w.write_request(w.request(rows=[{"id": "q01", "entry": 1}], count=True))


REQUEST_BREAKS = {
    "week missing": _req(week=DROP), "audit_commit missing": _req(audit_commit=DROP), "set missing": _req(set=DROP),
    "changed missing": _req(changed=DROP), "count missing": _req(count=DROP), "an extra key": _req(note="x"),
    "another week": _req(week="2026-W45"), "week null": _req(week=None), "another set": _req(set="other"),
    "audit_commit short": lambda w: w.write_request(w.request(audit_commit=w.commit[:39])),
    "audit_commit long": lambda w: w.write_request(w.request(audit_commit=w.commit + "0")),
    "audit_commit upper case": lambda w: w.write_request(w.request(audit_commit=w.commit.upper())),
    "audit_commit abbreviated": lambda w: w.write_request(w.request(audit_commit=w.commit[:12])),
    "audit_commit not hex": _req(audit_commit="g" * 40), "audit_commit a number": _req(audit_commit=1),
    "changed empty": _req_rows([], count=0), "changed over 400": _req_rows(_rows(401)),
    "changed a mapping": _req(changed={"id": "q01", "entry": 1}, count=1),
    "a row not a mapping": _req_rows([["q01", 1]]),
    "a row with an extra key": _req_rows([{"id": "q01", "entry": 1, "note": "x"}]),
    "a row without entry": _req_rows([{"id": "q01"}]), "a row without id": _req_rows([{"entry": 1}]),
    "id empty": _req_rows([{"id": "", "entry": 1}]), "id with a slash": _req_rows([{"id": "q01/x", "entry": 1}]),
    "id a parent path": _req_rows([{"id": "../q01", "entry": 1}]),
    "id leading hyphen": _req_rows([{"id": "-q01", "entry": 1}]),
    "id with a space": _req_rows([{"id": "q 01", "entry": 1}]),
    "id with a dot": _req_rows([{"id": "q01.yaml", "entry": 1}]),
    "id of 33 characters": _req_rows([{"id": "q" * 33, "entry": 1}]),
    "id a number": _req_rows([{"id": 1, "entry": 1}]),
    "entry 0": _req_rows([{"id": "q01", "entry": 0}]), "entry -1": _req_rows([{"id": "q01", "entry": -1}]),
    "entry true": _req_rows([{"id": "q01", "entry": True}]), "entry a string": _req_rows([{"id": "q01", "entry": "1"}]),
    "entry a float": _req_rows([{"id": "q01", "entry": 1.0}]),
    "count one too many": _req(count=len(ROWS) + 1), "count one too few": _req(count=len(ROWS) - 1),
    "count a string": _req(count=str(len(ROWS))), "count true for one row": _one_row_count_true,
    "a duplicate row": _req_rows([{"id": "q01", "entry": 1}, {"id": "q01", "entry": 1}]),
    "a duplicate row by case": _req_rows([{"id": "q01", "entry": 1}, {"id": "Q01", "entry": 1}]),
    "not JSON": _bytes(b"{not json\n"), "not UTF-8": _bytes(b'{"week": "\xff\xfe"}\n'),
    "a JSON list": _bytes(b"[]\n"), "JSON null": _bytes(b"null\n"), "empty": _bytes(b""),
    "a link": _link, "a folder": _folder, "absent": _absent, "over the size limit": _oversize,
}


@pytest.mark.parametrize("name", list(REQUEST_BREAKS))
def test_s14_a_request_of_a_wrong_form_is_10_with_nothing_built(rw, name):
    """S14 (interface 3): every request form but the one maintain writes refuses 10, with no wall, tree or run
    folder, and the sets root unchanged."""
    REQUEST_BREAKS[name](rw)
    before = rw.state()
    rc, counts, p = rw.dry()
    assert rc == 10, (rc, counts, p.stderr)
    assert counts["status"] == "refused" and counts["code"] == 10
    unchanged(rw, before, name)
    no_leaks(rw)


def test_s14_a_request_of_400_rows_and_an_id_of_32_characters_pass_the_form_check(tmp_path):
    """S14 (interface 3, the edges): 400 rows, and an id of 32 characters with `_` and `-`, are well formed."""
    w = ReanchorWorld(tmp_path / "a", rows=_rows(399, [{"id": "q02", "entry": 3}]))
    rc, counts, p = w.dry()
    assert rc == 0, (counts, p.stderr)
    assert counts["reanchor"]["entries"] == 400 and counts["reanchor"]["ids"] == 2
    assert counts["reanchor"]["absent"] == 398
    v = ReanchorWorld(tmp_path / "b", rows=[{"id": "Q01", "entry": 1}, {"id": "a" + "_-" * 15 + "z", "entry": 7}])
    rc, counts, p = v.dry()
    assert rc == 0, (counts, p.stderr)
    no_leaks(w)
    no_leaks(v)


@pytest.mark.parametrize("which", ["an earlier commit", "zeros", "another hex string"])
def test_s14_failure_a_request_for_another_commit_is_14_nothing_staged_nothing_built(rw, which):
    """S14 / S14-S15's failure ("a request served for another commit"): a well-formed request whose audit_commit is
    not the launch's --commit refuses 14; the sets root (the hidden half among it), the runs and trees folders are
    unchanged."""
    if which == "an earlier commit":
        other = rw.commit
        rw.put("docs/later.md", "later\n")
        rw.commit = rw.commit_all("later")
        rw.approve(rw.commit)
        assert other != rw.commit
    else:
        other = "0" * 40 if which == "zeros" else ("a" if rw.commit[0] != "a" else "b") + rw.commit[1:]
    rw.write_request(rw.request(audit_commit=other))
    before = rw.state()
    rc, counts, p = rw.dry()
    assert rc == 14, (rc, counts, p.stderr)
    assert counts["status"] == "refused" and counts["code"] == 14
    unchanged(rw, before, which)
    no_leaks(rw)


# =====================================================================================================================
# S14 -- matching (case-insensitive, in the set's own spelling) and staging
# =====================================================================================================================
@pytest.fixture(scope="module")
def dry(tmp_path_factory):
    w = ReanchorWorld(tmp_path_factory.mktemp("reanchor-dry"))
    rc, counts, p = w.dry()
    assert rc == 0, (counts, p.stderr)
    return w, counts, w.wall(counts)


FIXED = ["seed.txt", "brief.md", "CLAUDE.md", "WALL.json", "input/selection.json", ".claude/settings.json",
         ".claude/wall_hook.py"]


def test_s14_the_wall_holds_only_the_fixed_files_the_staged_ids_and_reanchor_json(dry):
    """S14 (interface 4): after a --dry launch the wall's whole file list is the fixed files, input/<stem>.yaml for
    each staged id and input/reanchor.json: no other hidden file, no hidden/visible/, no hidden/dropped/, no DRAW.txt,
    no input/set/, no notes; out/ empty."""
    w, counts, wall = dry
    files, dirs, links = w.wall_listing(wall)
    want = sorted(FIXED + [f"input/{s}.yaml" for s in STAGED_STEMS] + ["input/reanchor.json"])
    assert links == []
    assert files == want
    assert dirs == [".claude", "input", "out"]
    assert os.listdir(wall / "out") == []


def test_s14_upper_and_lower_case_ids_are_staged_in_the_sets_spelling_byte_for_byte(dry):
    """S14 (interface 4, F3 fixed): `q01` is served by hidden/Q01.yaml as input/Q01.yaml, `Q02` by hidden/q02.yaml as
    input/q02.yaml, the unique id by its file; each a byte copy."""
    w, counts, wall = dry
    for stem in STAGED_STEMS:
        assert (wall / "input" / f"{stem}.yaml").read_bytes() == (w.hidden / f"{stem}.yaml").read_bytes(), stem
    assert not (wall / "input" / "q01.yaml").exists() and not (wall / "input" / "Q02.yaml").exists()


def test_s14_reanchor_json_names_the_staged_ids_in_the_sets_spelling_sorted_and_nothing_else(dry):
    """S14 (interface 4): input/reanchor.json is {"week", "changed"} with the staged ids only (the absent id left
    out), in the set's spelling, sorted by id then entry."""
    w, counts, wall = dry
    got = json.loads((wall / "input" / "reanchor.json").read_text())
    assert got == {"week": WEEK, "changed": EXPECTED_CHANGED}


def test_s14_failure_no_other_file_of_the_set_reaches_the_wall(dry):
    """S14-S15's failure ("hidden content outside the walls"): no planted string of a file not staged (q03, the
    development half, the dropped file, DRAW.txt, the cross-check notes, visible/) is in any wall file."""
    w, counts, wall = dry
    found = set()
    for rel in w.wall_listing(wall)[0]:
        data = (wall / rel).read_bytes()
        found |= {(rel, mk) for mk in w.other_markers if mk.encode() in data}
    assert not found, sorted(found)


def test_s14_a_dry_runs_counts_carry_reanchor_numbers_and_validate(dry):
    """S14 / interface 6: the counts' reanchor holds the week, 5 entries, 3 staged ids, 1 absent, and null for the
    result's two numbers; the counts (stdout and counts.json) validate against the counts schema."""
    w, counts, wall = dry
    want = {"week": WEEK, "entries": 5, "ids": 3, "absent": 1, "corrected": None, "replaced": None}
    assert counts["reanchor"] == want
    assert json.loads((w.runs / "writer" / counts["run"] / "counts.json").read_text()) == counts
    assert indep_launch.schema_ok(counts, schema())


def test_f1_a_dry_run_shows_no_planted_string_outside_the_sets_root(dry):
    """F1 (S14-S15's failure, leaks): after the dry run, stdout, stderr, the counts and every file under the planted
    HOME and repository hold none of the planted strings (the unique id and its file name among them)."""
    w, counts, wall = dry
    no_leaks(w)


def test_s14_an_id_with_no_top_level_hidden_file_is_counted_absent_and_not_staged(tmp_path):
    """S14 (interface 4): ids held only in hidden/visible/, only in hidden/dropped/, or nowhere are absent; only the
    top-level file of the one present id is staged."""
    rows = [{"id": "q04", "entry": 1}, {"id": "q05", "entry": 1}, {"id": "q77", "entry": 2},
            {"id": "q03", "entry": 1}]
    w = ReanchorWorld(tmp_path, rows=rows)
    rc, counts, p = w.dry()
    assert rc == 0, (counts, p.stderr)
    assert {k: counts["reanchor"][k] for k in ("entries", "ids", "absent")} == {"entries": 4, "ids": 1, "absent": 3}
    wall = w.wall(counts)
    files = w.wall_listing(wall)[0]
    assert sorted(f for f in files if f.startswith("input/")) == ["input/q03.yaml", "input/reanchor.json",
                                                                 "input/selection.json"]
    assert json.loads((wall / "input" / "reanchor.json").read_text()) == {
        "week": WEEK, "changed": [{"id": "q03", "entry": 1}]}
    no_leaks(w)


def test_s14_ids_differing_only_in_case_are_one_id(tmp_path):
    """S14 (interface 4): `q01` entry 2 and `Q01` entry 1 are one id: one staged file, two entries."""
    w = ReanchorWorld(tmp_path, rows=[{"id": "q01", "entry": 2}, {"id": "Q01", "entry": 1}])
    rc, counts, p = w.dry()
    assert rc == 0, (counts, p.stderr)
    assert {k: counts["reanchor"][k] for k in ("entries", "ids", "absent")} == {"entries": 2, "ids": 1, "absent": 0}
    wall = w.wall(counts)
    assert json.loads((wall / "input" / "reanchor.json").read_text())["changed"] == [
        {"id": "Q01", "entry": 1}, {"id": "Q01", "entry": 2}]
    no_leaks(w)


def _two_matches(w):
    (w.hidden / "q01.yaml").write_bytes((w.hidden / "Q01.yaml").read_bytes())


def _match_link(w):
    (w.hidden / "q02.yaml").rename(w.hidden / "elsewhere.yaml")
    os.symlink("elsewhere.yaml", w.hidden / "q02.yaml")


def _match_folder(w):
    (w.hidden / "q02.yaml").unlink()
    (w.hidden / "q02.yaml").mkdir()
    (w.hidden / "q02.yaml" / "x.yaml").write_text("id: q02\n")


def _none_present(w):
    w.write_request(w.request(rows=[{"id": "q77", "entry": 1}, {"id": "q04", "entry": 1}]))


STAGING_BREAKS = {"two files match one id by case": _two_matches, "the matching file a link": _match_link,
                  "the matching file a folder": _match_folder, "no id present": _none_present}


@pytest.mark.parametrize("name", list(STAGING_BREAKS))
def test_s14_an_ambiguous_linked_or_empty_match_is_10_with_nothing_built(rw, name):
    """S14 (interface 4): two top-level files matching one id case-insensitively, a matching link or folder, or no id
    staged at all: 10, nothing built."""
    STAGING_BREAKS[name](rw)
    before = rw.state()
    rc, counts, p = rw.dry()
    assert rc == 10, (rc, counts, p.stderr)
    assert counts["status"] == "refused"
    unchanged(rw, before, name)
    no_leaks(rw)


def test_s14_plan_reanchor_returns_the_plan_the_staged_request_and_the_numbers(rw):
    """S14 (interface 7): plan_reanchor(root, set, week, commit) returns the (source, input/<stem>.yaml) pairs, the
    staged input/reanchor.json and {entries, ids, absent, present}; it writes nothing."""
    before = rw.state()
    plan, staged, info = indep_launch.plan_reanchor(str(rw.sets), SETN, WEEK, rw.commit)
    got = sorted((os.path.realpath(str(src)), dst) for src, dst in plan)
    assert got == sorted((os.path.realpath(rw.hidden / f"{s}.yaml"), f"input/{s}.yaml") for s in STAGED_STEMS)
    assert set(staged) == {"input/reanchor.json"}
    assert json.loads(staged["input/reanchor.json"]) == {"week": WEEK, "changed": EXPECTED_CHANGED}
    assert info == {"entries": 5, "ids": 3, "absent": 1, "present": sorted(STAGED_STEMS)}
    unchanged(rw, before, "plan_reanchor")


def test_s14_the_counts_schema_takes_an_optional_closed_reanchor_object():
    """S14 / interface 6: the counts schema's root gains `reanchor`, not required, closed, its six keys required."""
    s = schema()
    ra = s["properties"].get("reanchor")
    assert ra is not None, "no reanchor property"
    assert "reanchor" not in s["required"]
    assert ra.get("type") == "object" and ra.get("additionalProperties") is False
    assert sorted(ra.get("required", [])) == sorted(COUNTS_KEYS) == sorted(ra.get("properties", {}))


def test_s14_counts_with_a_reanchor_of_another_form_do_not_validate(dry):
    """S14 / interface 6: the dry run's counts validate; with reanchor given an extra key, a key missing, a string or a
    bool for a number, they do not."""
    w, counts, wall = dry
    assert indep_launch.schema_ok(counts, schema())
    bad = {"an extra key": dict(counts["reanchor"], extra=1),
           "a key missing": {k: v for k, v in counts["reanchor"].items() if k != "absent"},
           "entries a string": dict(counts["reanchor"], entries="5"),
           "ids true": dict(counts["reanchor"], ids=True)}
    passed = [name for name, ra in bad.items() if indep_launch.schema_ok(dict(counts, reanchor=ra), schema())]
    assert passed == []


def test_s12_a_writer_run_without_reanchor_carries_no_reanchor_and_validates(tmp_path):
    """S12 / interface 6 and 8 (a guard): a writer round 1 dry run on the planted declared template, without the flag,
    has counts without `reanchor` that validate as before; the request beside the set is not staged."""
    w = ReanchorWorld(tmp_path)
    rc, counts, p = w.run(*w.args("writer", set_name="brand-new-set", seed=3, dry=True))
    assert rc == 0, (counts, p.stderr)
    assert "reanchor" not in counts
    assert indep_launch.schema_ok(counts, schema())
    assert not (w.wall(counts) / "input" / "reanchor.json").exists()
    no_leaks(w)
