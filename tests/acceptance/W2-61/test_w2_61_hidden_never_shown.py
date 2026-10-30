"""W2-61, failure 2 and KPI success 3 -- the hidden part prints scores only.

Failure 2: "The script prints, logs or writes a hidden question's gold answer." KPI 3: "... it prints scores, never
the hidden answers [DEC-828 item 4, DEC-820 (d)]".

For a question of the hidden part, stdout, stderr, the record and every file the measure writes hold only ids,
counts, ranks, digests and pass or fail: never its question, its gold answer, its sources' paths or headings, any
retrieved item's path or text, or an unknown field's value. An error on a hidden question names only its id or file
name and the error's kind.

The planted hidden part (``w2_61_support.hidden_questions``): h01 (a hit at rank 2) and h02 (a miss). Every word
of it, and of its governing source's path and heading, the retrieved items' path and text, an unknown field and the
planted gov's error message, holds ``zqxw61hidden``; the scan looks for that in stdout, stderr and every file
created or changed anywhere under the test's folder (the planted repository, HOME, TMPDIR and the ``--out``
folder), compared by a listing before and after the run. The planted gov's own files (its answers and its call log)
are the test's, not the measure's, and are left out. The measure runs as an unmeasured session (orchestrator).

Red now: ``gov.retrieval.measure`` does not exist.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_61_support as s  # noqa: E402

MARK = "zqxw61hidden"


@pytest.fixture
def world(tmp_path):
    w = s.make_world(tmp_path, commit=False)
    s.standard_questions(w)
    s.hidden_questions(w)
    w.commit()
    return w


def _run_and_scan(world, *args):
    before = world.snapshot()
    run = world.measure(*args)
    for stream, text in (("stdout", run.stdout), ("stderr", run.stderr)):
        assert MARK not in text, f"{stream} shows a hidden word ({' '.join(map(str, args))}):\n{text[-3000:]}"
    written = world.written_since(before)
    leaking = [str(path) for path in written if MARK.encode() in path.read_bytes()]
    assert not leaking, f"the measure wrote hidden words into: {leaking}"
    return run, written


CASES = {
    "hidden-text": ("--part", "hidden"),
    "hidden-json": ("--part", "hidden", "--json"),
    "hidden-out": ("--part", "hidden", "--json", "--out", "OUT"),
    "all-text": ("--part", "all"),
    "all-json-out": ("--part", "all", "--json", "--out", "OUT"),
}


@pytest.mark.parametrize("case", sorted(CASES))
def test_a_run_over_the_hidden_part_shows_and_writes_no_hidden_word(world, case):
    args = [str(world.base / "out") if word == "OUT" else word for word in CASES[case]]
    run, written = _run_and_scan(world, s.SET, *args)
    assert run.returncode == 0, f"{case}: the run did not end with 0\n{run.describe()}"
    if "--out" in args:
        assert s.records_in(world.base / "out"), f"{case}: --out wrote no record"
        assert any(path.parent == world.base / "out" for path in written)


def test_the_hidden_part_is_scored(world):
    run, _ = _run_and_scan(world, s.SET, "--part", "hidden", "--json")
    document = run.json()
    assert document.get("part") == "hidden"
    assert [q.get("id") for q in s.questions(document)] == ["h01", "h02"]
    h01, h02 = s.question(document, "h01"), s.question(document, "h02")
    assert (h01.get("hit_at_5"), h01.get("in_bundle"), h01.get("full_evidence"), h01.get("first_gold_rank")) == (
        True, True, True, 2), f"h01: {h01}"
    assert (h02.get("hit_at_5"), h02.get("full_evidence"), h02.get("first_gold_rank")) == (False, False, None), (
        f"h02: {h02}")
    total = document.get("total") or {}
    assert (total.get("hit_at_5") or {}).get("count") == 1 and (total.get("full_evidence") or {}).get("count") == 1
    assert not s.lone_objects(document), s.lone_objects(document)


def test_all_measures_both_parts(world):
    run, _ = _run_and_scan(world, s.SET, "--part", "all", "--json")
    document = run.json()
    assert document.get("part") == "all"
    assert sorted(q.get("id") for q in s.questions(document)) == ["h01", "h02", "v01", "v02", "v03", "v04"]
    assert (document.get("total") or {}).get("questions") == 6


def test_the_text_of_the_hidden_part_still_gives_both_figures_together(world):
    run, _ = _run_and_scan(world, s.SET, "--part", "hidden")
    assert not s.lone_figures(run.stdout), "\n".join(s.lone_figures(run.stdout))
    assert "h01" in run.stdout and "h02" in run.stdout, f"the hidden ids are not given\n{run.describe()}"


# --------------------------------------------------------------------------
# An error on a hidden question names only its id or file name
# --------------------------------------------------------------------------

def _hidden_error_world(tmp_path, kind):
    world = s.make_world(tmp_path, commit=False)
    s.hidden_questions(world)
    question = f"{s.HIDDEN_QUESTION} three?"
    if kind == "malformed":     # no sources
        world.question("h03", {"question": question, "gold_answer": f"{s.HIDDEN_ANSWER} three"}, [[]],
                       part="hidden")
    elif kind == "not-yaml":
        world.write(f"fixtures/evaluation/{s.SET}/hidden/h03.yaml",
                    f"question: [{s.HIDDEN_QUESTION} three\ngold_answer: {s.HIDDEN_ANSWER}: : [\n")
    elif kind == "missing-source":
        world.question("h03", {"question": question, "gold_answer": f"{s.HIDDEN_ANSWER} three",
                               "sources": [{"path": f"{s.HIDDEN_SOURCE_DIR}/absent.md"}]}, [[]], part="hidden")
    elif kind == "no-heading-no-lines":
        world.question("h03", {"question": question, "gold_answer": f"{s.HIDDEN_ANSWER} three",
                               "sources": [{"path": s.HIDDEN_SOURCE, "heading": "## zqxw61hiddenabsentheading"}]},
                       [[]], part="hidden")
    elif kind == "failing-retrieval":
        world.question("h03", {"question": question, "gold_answer": f"{s.HIDDEN_ANSWER} three",
                               "sources": [{"path": s.HIDDEN_SOURCE, "heading": s.HIDDEN_HEADING}]},
                       fail=s.HIDDEN_FAILURE, part="hidden")
    world.commit()
    return world


@pytest.mark.parametrize("kind", ["malformed", "not-yaml", "missing-source", "no-heading-no-lines",
                                  "failing-retrieval"])
@pytest.mark.parametrize("json_flag", [False, True])
def test_an_error_on_a_hidden_question_names_only_its_id(tmp_path, kind, json_flag):
    world = _hidden_error_world(tmp_path, kind)
    args = [s.SET, "--part", "hidden", "--out", str(world.base / "out")] + (["--json"] if json_flag else [])
    run, _ = _run_and_scan(world, *args)
    assert run.returncode != 0, f"{kind}: the hidden error did not end the run with an error\n{run.describe()}"
    assert "h03" in run.output, f"{kind}: the error does not name the question's id or file\n{run.describe()}"
