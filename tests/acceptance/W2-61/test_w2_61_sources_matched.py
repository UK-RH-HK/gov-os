"""W2-61, KPI success 3 and 4 -- how a source is matched, what is passed through, and what is an error.

The rules, as the ticket's brief states them:

- an evidence item matches a source when its ``path`` equals the source's path and its span (``start_line`` to
  ``end_line``, inclusive) overlaps the source's span; a source with only a ``path`` is the whole file;
- a ``heading`` is the full text of one line of the file, matched as the first line whose text, trailing whitespace
  removed, equals it. Found, it governs over the stated ``lines``: a heading starting with ``#`` spans to the line
  before the next Markdown heading of the same or a higher level (or the end of the file); any other heading spans
  from its line for as many lines as the stated ``lines`` span (its own line when none are stated). Not found, the
  stated ``lines`` are used; neither found nor stated, the source is malformed;
- a ``sources`` entry that is a list holds alternatives, any one of which counts; full evidence needs every entry;
- ``ticket``, ``ids`` and ``radius`` are passed as ``--ticket``, ``--id`` (each) and ``--radius``; the question
  text is passed as it is, as one argument; ``id`` defaults to the file name without ``.yaml``; questions are taken
  in file-name order; unknown fields are ignored and never printed;
- the run ends non-zero on a malformed question, a gold source naming a path that does not exist in the measured
  root, or a failing retrieval, naming the question.

Red now: ``gov.retrieval.measure`` does not exist.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_61_support as s  # noqa: E402

DEC = s.DECISIONS
DEC1, DEC2, DEC21, DEC3, DEC5 = ("## DEC-1 The packet ceiling", "## DEC-2 The archive",
                                 "### DEC-2.1 The archive's copy", "## DEC-3 The gate", "## DEC-5 The audit lines")


def _ask(world, qid, sources, items, **extra):
    world.question(qid, {"question": f"Question {qid}?", "gold_answer": "planted", "sources": sources, **extra},
                   [items])


# --------------------------------------------------------------------------
# Matching, on the documents as planted
# --------------------------------------------------------------------------

def _matching_cases(world):
    """``{id: (hit_at_5, full_evidence)}``, each a question with one call."""
    d1 = world.span(DEC, DEC1)
    sub = world.span(DEC, DEC21)
    d3 = world.span(DEC, DEC3)
    d4 = world.span(DEC, "## DEC-4 The resume")
    item, section = world.item, world.section
    alternatives = [[{"path": s.ARCHIVE_CODE}, {"path": DEC, "heading": DEC2}]]
    two = [{"path": DEC, "heading": DEC1}, [{"path": DEC, "heading": DEC5}, {"path": s.ARCHIVE_CODE}]]
    cases = {
        "m-alt-first": (alternatives, [section(DEC, DEC2)], (True, True)),
        "m-alt-second": (alternatives, [item(s.ARCHIVE_CODE, 1, 2)], (True, True)),
        "m-two-entries-one-found": (two, [section(DEC, DEC1)], (True, False)),
        "m-two-entries-both-found": (two, [section(DEC, DEC1), section(DEC, DEC5)], (True, True)),
        "m-subheading-inside": ([{"path": DEC, "heading": DEC2}], [item(DEC, *sub)], (True, True)),
        "m-next-heading-outside": ([{"path": DEC, "heading": DEC2}], [item(DEC, *d3)], (False, False)),
        "m-overlap-at-start": ([{"path": DEC, "heading": DEC1}], [item(DEC, d1[0] - 2, d1[0])], (True, True)),
        "m-before-the-span": ([{"path": DEC, "heading": DEC1}], [item(DEC, 1, d1[0] - 1)], (False, False)),
        "m-overlap-at-end": ([{"path": DEC, "heading": DEC1}], [item(DEC, d1[1], d1[1] + 1)], (True, True)),
        "m-path-only": ([{"path": s.ARCHIVE_CODE}], [item(s.ARCHIVE_CODE, 2, 2)], (True, True)),
        "m-other-path": ([{"path": DEC, "heading": DEC1}], [item(s.ARCHIVE_CODE, *d1)], (False, False)),
        "m-heading-absent-lines-used": ([{"path": DEC, "heading": "## DEC-9 Gone", "lines": list(d4)}],
                                        [item(DEC, d4[1], d4[1])], (True, True)),
        "m-heading-absent-lines-missed": ([{"path": DEC, "heading": "## DEC-9 Gone", "lines": list(d4)}],
                                          [item(DEC, 1, 3)], (False, False)),
        "m-lines-only": ([{"path": DEC, "lines": list(d3)}], [item(DEC, d3[1], d3[1])], (True, True)),
        "m-trailing-space-in-file": ([{"path": "docs/trailing.md", "heading": "## Trailing"}],
                                     [item("docs/trailing.md", 3, 4)], (True, True)),
    }
    for qid, (sources, items, _) in cases.items():
        _ask(world, qid, sources, items)
    return {qid: want for qid, (_, _, want) in cases.items()}


def test_items_match_sources_by_path_and_overlapping_span(tmp_path):
    world = s.make_world(tmp_path, files={"docs/trailing.md": "# Trailing file\n\n## Trailing   \nbody\n"},
                         commit=False)
    expected = _matching_cases(world)
    world.commit()
    document = world.measure(s.SET, "--json").json()
    wrong = {}
    for qid, (hit, full) in expected.items():
        got = s.question(document, qid)
        if (got.get("hit_at_5"), got.get("full_evidence")) != (hit, full):
            wrong[qid] = {"want": (hit, full), "got": (got.get("hit_at_5"), got.get("full_evidence"))}
    assert not wrong, f"sources matched wrongly: {wrong}"
    two = s.question(document, "m-two-entries-one-found")
    assert (two.get("pieces_found"), two.get("pieces_needed")) == (1, 2), f"pieces: {two}"


# --------------------------------------------------------------------------
# A heading that has moved: the stated lines are stale
# --------------------------------------------------------------------------

def test_a_heading_that_moved_governs_over_its_stale_lines(tmp_path):
    world = s.make_world(tmp_path, commit=False)
    first_commit = world.commit()
    old_dec1 = list(world.span(DEC, DEC1))
    lines = world.lines(DEC)
    world.write(DEC, "\n".join(lines[:4] + [f"Inserted line {n}." for n in range(1, 11)] + lines[4:]) + "\n")
    code = world.lines(s.ARCHIVE_CODE)
    world.write(s.ARCHIVE_CODE, "\n".join(["import os", "import sys", "", "", ""] + code) + "\n")
    world.commit(message="W2-61 fixture: the headings move down")
    new_dec1 = world.span(DEC, DEC1)
    assert new_dec1[0] > old_dec1[1], (old_dec1, new_dec1)
    md = [{"path": DEC, "heading": DEC1, "lines": old_dec1, "commit": first_commit}]
    code_lines = [{"path": s.ARCHIVE_CODE, "heading": "def archive(path):", "lines": [1, 2]}]
    code_bare = [{"path": s.ARCHIVE_CODE, "heading": "def archive(path):"}]
    item = world.item
    expected = {
        "mv-markdown-new-span": (md, [item(DEC, *new_dec1)], True),
        "mv-markdown-stale-span": (md, [item(DEC, *old_dec1)], False),
        "mv-code-second-line-of-span": (code_lines, [item(s.ARCHIVE_CODE, 7, 7)], True),
        "mv-code-stale-lines": (code_lines, [item(s.ARCHIVE_CODE, 1, 2)], False),
        "mv-code-own-line": (code_bare, [item(s.ARCHIVE_CODE, 6, 6)], True),
        "mv-code-past-its-own-line": (code_bare, [item(s.ARCHIVE_CODE, 7, 7)], False),
    }
    assert world.lines(s.ARCHIVE_CODE)[5] == "def archive(path):"
    for qid, (sources, items, _) in expected.items():
        _ask(world, qid, sources, items, commit=first_commit)
    world.commit(message="W2-61 fixture: the questions")
    document = world.measure(s.SET, "--json").json()
    wrong = {qid: s.question(document, qid).get("hit_at_5") for qid, (*_, hit) in expected.items()
             if s.question(document, qid).get("hit_at_5") is not hit}
    assert not wrong, f"moved headings matched wrongly (want: {({q: e[2] for q, e in expected.items()})}): {wrong}"


# --------------------------------------------------------------------------
# What is passed to gov retrieve
# --------------------------------------------------------------------------

ODD_QUESTION = "What's \"the\" $HOME `gate`; --radius 9 && echo *?"


def test_ticket_ids_radius_and_the_question_are_passed_through(tmp_path):
    world = s.make_world(tmp_path, commit=False)
    sources = [{"path": DEC, "heading": DEC1}]
    world.question("p01", {"question": "Which tickets depend on it?", "gold_answer": "planted", "sources": sources,
                           "ticket": s.MEASURED_TICKET, "ids": ["indexable", "rrf"], "radius": 1}, [[]])
    world.question("p02", {"question": "Nothing else passed?", "gold_answer": "planted", "sources": sources}, [[]])
    world.question("p03", {"question": ODD_QUESTION, "gold_answer": "planted", "sources": sources}, [[]])
    world.commit()
    world.measure(s.SET, "--json").json()
    by_query = {}
    for call in world.calls():
        opts = s.options(call["argv"])
        by_query.setdefault(tuple(opts["query"]), []).append(opts)
    assert set(by_query) == {("Which tickets depend on it?",), ("Nothing else passed?",), (ODD_QUESTION,)}, (
        f"the questions were not passed as one argument each: {sorted(by_query)}")
    p01, = by_query[("Which tickets depend on it?",)]
    assert p01.get("--ticket") == [s.MEASURED_TICKET], f"--ticket: {p01.get('--ticket')}"
    assert p01.get("--id") == ["indexable", "rrf"], f"--id: {p01.get('--id')}"
    assert p01.get("--radius") == ["1"], f"--radius: {p01.get('--radius')}"
    p02, = by_query[("Nothing else passed?",)]
    assert "--ticket" not in p02 and "--id" not in p02, f"options passed that the question does not give: {p02}"


def test_ids_default_to_the_file_name_in_file_name_order_and_unknown_fields_stay_unprinted(tmp_path):
    world = s.make_world(tmp_path, commit=False)
    sources = [{"path": DEC, "heading": DEC1}]
    world.question("b", {"question": "Second file?", "gold_answer": "planted", "sources": sources, "id": "zeta",
                         "remarks": s.UNKNOWN_WORD}, [[]])
    world.question("a", {"question": "First file?", "gold_answer": "planted", "sources": sources,
                         "remarks": s.UNKNOWN_WORD, "category": "decision"}, [[]])
    world.question("c", {"question": "Third file?", "gold_answer": "planted", "sources": sources, "id": "alpha"},
                   [[]])
    world.commit()
    run = world.measure(s.SET, "--json")
    assert [q.get("id") for q in s.questions(run.json())] == ["a", "zeta", "alpha"]
    text = world.measure(s.SET)
    for done in (run, text):
        assert done.returncode == 0, done.describe()
        assert s.UNKNOWN_WORD not in done.output, f"an unknown field was printed\n{done.describe()}"


# --------------------------------------------------------------------------
# Errors: named, non-zero
# --------------------------------------------------------------------------

ERRORS = {
    "failing-retrieval": None,
    "missing-source-path": {"question": "Q?", "gold_answer": "g", "sources": [{"path": "docs/absent.md"}]},
    "heading-absent-no-lines": {"question": "Q?", "gold_answer": "g",
                                "sources": [{"path": DEC, "heading": "## DEC-9 Gone"}]},
    "no-question": {"gold_answer": "g", "sources": [{"path": DEC}]},
    "no-gold-answer": {"question": "Q?", "sources": [{"path": DEC}]},
    "no-sources": {"question": "Q?", "gold_answer": "g"},
    "sources-not-a-list": {"question": "Q?", "gold_answer": "g", "sources": DEC},
    "source-without-path": {"question": "Q?", "gold_answer": "g", "sources": [{"heading": DEC1}]},
}


@pytest.mark.parametrize("kind", sorted(ERRORS))
def test_an_error_in_a_visible_question_ends_the_run_non_zero_and_names_it(tmp_path, kind):
    world = s.make_world(tmp_path, commit=False)
    s.standard_questions(world)
    if kind == "failing-retrieval":
        world.question("e01", {"question": "Q?", "gold_answer": "g", "sources": [{"path": DEC}]},
                       fail="the planted store is missing")
    else:
        world.question("e01", ERRORS[kind], [[]])
    world.commit()
    run = world.measure(s.SET, "--json")
    assert run.returncode != 0, f"{kind}: the run did not end with an error\n{run.describe()}"
    assert "e01" in run.output, f"{kind}: the error does not name the question\n{run.describe()}"
