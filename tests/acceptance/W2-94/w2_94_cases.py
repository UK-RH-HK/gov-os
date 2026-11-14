"""The planted breaks of the W2-94 acceptance tests, as tables (made-up stand-ins only; see ``w2_94_support``).

Each table maps a case name to ``(build_kwargs, case, exit_code)``. ``build_kwargs`` go to ``w2_94_support.build``;
``case(world)`` plants the break in the good world and returns ``(expected, run_kwargs)``: ``expected`` is a list of
tuples, each the leading words of an output line the program must print (``("q07", "SPAN_OUT_OF_FILE")`` for
``FAIL q07 SPAN_OUT_OF_FILE``; ``("REFUSED", "FIELD_MISSING", "q07")``), and ``run_kwargs`` go to ``run_check``.

The tables are shared by the KPI cases (S1, S4, F3, fail closed) and by the counts-only case, which runs every one of
them and looks at what the program prints.
"""

from __future__ import annotations

import re
import shutil

import w2_94_support as s

# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def _edit(change, code, qid="q07"):
    def case(world):
        world.edit(qid, change)
        return [("REFUSED", code, qid)], {}
    return case


def _drop(field, qid="q07"):
    def case(world):
        world.drop(qid, field)
        return [("REFUSED", "FIELD_MISSING", qid)], {}
    return case


def _source(change, code, qid="q07"):
    def case(world):
        world.edit(qid, lambda d: change(d["sources"][0]))
        return [("REFUSED", code, qid)], {}
    return case


def _pop(key):
    return lambda source: source.pop(key)


def _set(**values):
    return lambda source: source.update(values)


def _line(world, k):
    return next(i for i, line in enumerate(world.draw_lines()) if line.startswith(f"{k} "))


def _rewrite_draw_line(world, k, change):
    lines = world.draw_lines()
    lines[_line(world, k)] = change(lines[_line(world, k)])
    world.set_draw_lines(lines)


# --------------------------------------------------------------------------
# S1: a question that lacks a required field or has a bad one is refused (exit 2); the count is 10 to 20
# --------------------------------------------------------------------------

def _duplicate(world):
    path = world.qpath("q07")
    other = world.hidden_dir if path.parent == world.dev_dir else world.dev_dir
    shutil.copy2(path, other / path.name)
    return [("REFUSED", "ID_DUPLICATE", "q07")], {}


def _scaffold_commit(world):
    head = s.git(world.copy, "rev-parse", "HEAD").strip()
    assert head != world.commit
    world.edit("q07", lambda d: d.update(commit=head))
    return [("REFUSED", "COMMIT_MISMATCH", "q07")], {}


S1_FORM = {f"missing-{field}": ({}, _drop(field), 2) for field in s.REQUIRED}
S1_FORM.update({
    "id-differs-from-the-file-name": ({}, _edit(lambda d: d.update(id="q99"), "ID_MISMATCH"), 2),
    "same-id-in-both-halves": ({}, _duplicate, 2),
    "category-unknown": ({}, _edit(lambda d: d.update(category="poetry"), "CATEGORY_UNKNOWN"), 2),
    "commit-is-another-commit": ({}, _edit(lambda d: d.update(commit="a" * 40), "COMMIT_MISMATCH"), 2),
    "commit-is-the-scaffold-commit": ({}, _scaffold_commit, 2),
    "commit-is-twelve-digits": ({}, _edit(lambda d: d.update(commit=d["commit"][:12]), "COMMIT_MISMATCH"), 2),
    "source-without-a-path": ({}, _source(_pop("path"), "SOURCE_NO_PATH"), 2),
    "source-without-lines": ({}, _source(_pop("lines"), "SOURCE_NO_LINES"), 2),
    "lines-one-integer": ({}, _source(_set(lines=[3]), "LINES_BAD"), 2),
    "lines-three-integers": ({}, _source(_set(lines=[3, 4, 5]), "LINES_BAD"), 2),
    "lines-first-after-last": ({}, _source(_set(lines=[5, 3]), "LINES_BAD"), 2),
    "lines-not-integers": ({}, _source(_set(lines=["a", "b"]), "LINES_BAD"), 2),
    "lines-a-single-integer-not-a-list": ({}, _source(_set(lines=4), "LINES_BAD"), 2),
    "no-sources": ({}, _edit(lambda d: d.update(sources=[]), "FIELD_BAD"), 2),
    "empty-question": ({}, _edit(lambda d: d.update(question=""), "FIELD_BAD"), 2),
    "drawn-neither-sample-nor-none": ({}, _edit(lambda d: d.update(drawn="maybe"), "FIELD_BAD"), 2),
    "keyword-not-a-boolean": ({}, _edit(lambda d: d.update(keyword="yes"), "FIELD_BAD"), 2),
})

# --------------------------------------------------------------------------
# S1: the draw and the halves are reported (exit 1)
# --------------------------------------------------------------------------


def _seed_inconsistent(world):
    _rewrite_draw_line(world, 3, lambda t: re.sub(r"SEED\+3=(\d+)", lambda m: f"SEED+3={int(m.group(1)) + 2}", t))
    return [("draw", "DRAW_SEED_INCONSISTENT")], {}


def _parity_wrong(world):
    _rewrite_draw_line(world, 2, lambda t: t.replace(" even ", " ODD ").replace(" odd ", " even ").replace(" ODD ", " odd "))
    return [("draw", "DRAW_PARITY_MISMATCH")], {}


def _category_in_one_half(world):
    """Pair 2 both in the measured half, pair 3 both in the development half: the halves stay equal in size."""
    world.move_half(world.visible_ids[1])
    world.move_half(world.hidden_ids[2])
    return [("draw", "CATEGORY_IN_ONE_HALF")], {}


def _halves_differ_by_two(world):
    world.move_half(world.visible_ids[0])
    return [("draw", "HALVES_UNBALANCED")], {}


def _rule_violated(world):
    """The pair of category 2 sent the other way round, files and line together: only the brief's rule is broken."""
    visible, hidden = world.visible_ids[1], world.hidden_ids[1]
    world.move_half(visible)
    world.move_half(hidden)
    _rewrite_draw_line(world, 2, lambda t: t.replace(f"visible={visible} hidden={hidden}", f"visible={hidden} hidden={visible}"))
    return [("draw", "DRAW_RULE_VIOLATED")], {}


def _draw_missing(world):
    world.draw.unlink()
    return [("draw", "DRAW_MISSING")], {}


def _draw_line_dropped(world):
    world.set_draw_lines(world.draw_lines()[:-1])
    return [("draw", "DRAW_LINES_MISMATCH")], {}


def _draw_line_garbled(world):
    _rewrite_draw_line(world, 1, lambda t: "1 " + t.split(" ", 2)[1] + " the seed was something")
    return [("draw", "DRAW_LINE_BAD")], {}


def _draw_id_missing(world):
    _rewrite_draw_line(world, 1, lambda t: re.sub(r"visible=q\d\d", "visible=q88", t))
    return [("draw", "DRAW_ID_MISSING")], {}


def _draw_category_wrong(world):
    _rewrite_draw_line(world, 1, lambda t: t.replace("code-location", "callers"))
    return [("draw", "DRAW_CATEGORY_MISMATCH")], {}


def _stray_file(world):
    s.write(world.hidden_dir / "notes.txt", "a stray file\n")
    return [("set", "UNEXPECTED_FILE")], {}


def _digit_k_differs_from_the_first_field(world):
    """Line 3 reads ``3 <category> SEED+4=<seed+4> ...`` (a digit form whose k is not the line's first field), with the
    parity word, the pair and the files all fitting that value: only the k that disagrees is wrong."""
    seed = world.seed
    old = (world.visible_ids[2], world.hidden_ids[2])
    new = s.draw_halves(3, seed + 1)
    if new != old:
        world.move_half(old[0])
        world.move_half(old[1])
    value = seed + 4
    parity = "even" if value % 2 == 0 else "odd"
    _rewrite_draw_line(world, 3, lambda t: f"3 {t.split()[1]} SEED+4={value} {parity} visible={new[0]} hidden={new[1]}")
    return [("draw", "DRAW_CATEGORY_MISMATCH")], {}


S1_DRAW = {
    "digit-form-k-differs-from-the-first-field": ({}, _digit_k_differs_from_the_first_field, 1),
    "seed-inconsistent": ({}, _seed_inconsistent, 1),
    "parity-wrong": ({}, _parity_wrong, 1),
    "category-in-one-half-only": ({}, _category_in_one_half, 1),
    "halves-differ-by-two": ({}, _halves_differ_by_two, 1),
    "rule-violated": ({}, _rule_violated, 1),
    "no-draw-file": ({}, _draw_missing, 1),
    "a-category-without-a-line": ({}, _draw_line_dropped, 1),
    "garbled-line": ({}, _draw_line_garbled, 1),
    "id-in-no-half": ({}, _draw_id_missing, 1),
    "category-wrong-in-a-line": ({}, _draw_category_wrong, 1),
    "a-stray-file-in-the-measured-half": ({}, _stray_file, 1),
}

# --------------------------------------------------------------------------
# S1, after W2-94 GOLD (owner, 2026-11-13) (iii): a draw line may also be written in the literal letter form
# ``<k> <category> SEED+k=<value> <parity> visible=<id> hidden=<id>`` (the k of ``SEED+<k>`` is the first field); every
# other rule is as for the digit form. Only the literal spelling ``SEED+k=`` is accepted besides ``SEED+<digits>=``.
# --------------------------------------------------------------------------

def _literal(text):
    """One draw line with its ``SEED+<digits>=`` written ``SEED+k=``."""
    return re.sub(r"SEED\+\d+=", "SEED+k=", text)


def _literal_all(world):
    world.set_draw_lines([_literal(line) for line in world.draw_lines()])


def _literal_odd_k_only(world):
    world.set_draw_lines([_literal(line) if int(line.split()[0]) % 2 else line for line in world.draw_lines()])


def _ok(prepare):
    def case(world):
        prepare(world)
        return [], {}
    return case


S1_DRAW_FORMS = {
    "every-line-in-the-literal-form": ({}, _ok(_literal_all), 0),
    "some-lines-digit-form-some-literal": ({}, _ok(_literal_odd_k_only), 0),
}


def _in_literal_form(change, code):
    def case(world):
        _literal_all(world)
        change(world)
        return [("draw", code)], {}
    return case


def _lit_seed_inconsistent(world):
    _rewrite_draw_line(world, 3, lambda t: re.sub(r"SEED\+k=(\d+)", lambda m: f"SEED+k={int(m.group(1)) + 2}", t))


def _lit_parity_wrong(world):
    _rewrite_draw_line(world, 2, lambda t: t.replace(" even ", " ODD ").replace(" odd ", " even ").replace(" ODD ", " odd "))


def _lit_rule_violated(world):
    visible, hidden = world.visible_ids[1], world.hidden_ids[1]
    world.move_half(visible)
    world.move_half(hidden)
    _rewrite_draw_line(world, 2, lambda t: t.replace(f"visible={visible} hidden={hidden}", f"visible={hidden} hidden={visible}"))


def _lit_category_wrong(world):
    _rewrite_draw_line(world, 1, lambda t: t.replace("code-location", "callers"))


def _lit_id_in_no_half(world):
    _rewrite_draw_line(world, 1, lambda t: re.sub(r"visible=q\d\d", "visible=q88", t))


def _spelled(spelling):
    return lambda world: _rewrite_draw_line(world, 1, lambda t: t.replace("SEED+k=", spelling))


S1_DRAW_LITERAL = {
    "literal-seed-inconsistent": ({}, _in_literal_form(_lit_seed_inconsistent, "DRAW_SEED_INCONSISTENT"), 1),
    "literal-parity-wrong": ({}, _in_literal_form(_lit_parity_wrong, "DRAW_PARITY_MISMATCH"), 1),
    "literal-rule-violated": ({}, _in_literal_form(_lit_rule_violated, "DRAW_RULE_VIOLATED"), 1),
    "literal-category-wrong-for-its-k": ({}, _in_literal_form(_lit_category_wrong, "DRAW_CATEGORY_MISMATCH"), 1),
    "literal-id-in-no-half": ({}, _in_literal_form(_lit_id_in_no_half, "DRAW_ID_MISSING"), 1),
    "an-upper-case-K": ({}, _in_literal_form(_spelled("SEED+K="), "DRAW_LINE_BAD"), 1),
    "the-placeholder-in-angle-brackets": ({}, _in_literal_form(_spelled("SEED+<k>="), "DRAW_LINE_BAD"), 1),
    "another-letter": ({}, _in_literal_form(_spelled("SEED+x="), "DRAW_LINE_BAD"), 1),
    "two-letters": ({}, _in_literal_form(_spelled("SEED+kk="), "DRAW_LINE_BAD"), 1),
    "a-space-before-the-plus": ({}, _in_literal_form(_spelled("SEED +k="), "DRAW_LINE_BAD"), 1),
    "a-space-after-the-plus": ({}, _in_literal_form(_spelled("SEED+ k="), "DRAW_LINE_BAD"), 1),
    "a-space-before-the-equals-sign": ({}, _in_literal_form(_spelled("SEED+k ="), "DRAW_LINE_BAD"), 1),
    "no-k-at-all": ({}, _in_literal_form(_spelled("SEED+="), "DRAW_LINE_BAD"), 1),
}

# --------------------------------------------------------------------------
# S1: the release (visible/ is byte for byte hidden/visible/; the record names each file) is reported (exit 1)
# --------------------------------------------------------------------------


def _released(world, index=2):
    return world.visible_ids[index]


def _byte_differs(world):
    qid = _released(world)
    with open(world.released_dir / f"{qid}.yaml", "ab") as handle:
        handle.write(b" ")
    return [("release", "VISIBLE_BYTES_DIFFER", qid)], {}


def _file_missing(world):
    qid = _released(world)
    (world.released_dir / f"{qid}.yaml").unlink()
    return [("release", "VISIBLE_FILE_MISSING", qid)], {}


def _extra_question_file(world):
    s.write(world.released_dir / "q99.yaml", "id: q99\n")
    return [("release", "VISIBLE_FILE_EXTRA", "q99")], {}


def _extra_other_file(world):
    s.write(world.released_dir / "notes.txt", "a stray file\n")
    return [("release", "VISIBLE_FILE_EXTRA")], {}


def _record_missing(world):
    world.record.unlink()
    return [("release", "RECORD_MISSING")], {}


def _record_rows(world, change):
    rows = world.record.read_text(encoding="utf-8").splitlines()
    world.record.write_text("\n".join(change(rows)) + "\n", encoding="utf-8")


def _record_sha_wrong(world):
    qid = _released(world)
    _record_rows(world, lambda rows: [f"{r.split()[0]} {'0' * 64}" if r.startswith(qid) else r for r in rows])
    return [("release", "RECORD_SHA_MISMATCH", qid)], {}


def _record_entry_dropped(world):
    qid = _released(world)
    _record_rows(world, lambda rows: [r for r in rows if not r.startswith(qid)])
    return [("release", "RECORD_ENTRY_MISSING", qid)], {}


def _record_entry_extra(world):
    _record_rows(world, lambda rows: rows + [f"q99.yaml {'1' * 64}"])
    return [("release", "RECORD_ENTRY_EXTRA")], {}


def _record_line_bad(world):
    _record_rows(world, lambda rows: rows + ["not a record line"])
    return [("release", "RECORD_LINE_BAD")], {}


def _record_without_folder(world):
    shutil.rmtree(world.released_dir)
    return [("release", "RECORD_WITHOUT_VISIBLE")], {}


def _folder_is_a_file(world):
    shutil.rmtree(world.released_dir)
    s.write(world.released_dir, "not a folder\n")
    return [("release", "VISIBLE_NOT_DIR")], {}


S1_RELEASE = {
    "one-byte-differs": ({}, _byte_differs, 1),
    "a-file-missing": ({}, _file_missing, 1),
    "an-extra-question-file": ({}, _extra_question_file, 1),
    "an-extra-other-file": ({}, _extra_other_file, 1),
    "no-record": ({}, _record_missing, 1),
    "record-sha-wrong": ({}, _record_sha_wrong, 1),
    "record-misses-a-file": ({}, _record_entry_dropped, 1),
    "record-names-a-file-that-is-not-there": ({}, _record_entry_extra, 1),
    "record-line-garbled": ({}, _record_line_bad, 1),
    "record-without-visible": ({}, _record_without_folder, 1),
    "visible-is-a-file": ({}, _folder_is_a_file, 1),
}

# --------------------------------------------------------------------------
# S4, F3: a source that is absent, outside the file, without its heading, or that does not hold the answer is reported
# by that question's id (exit 1), the other nineteen still holding
# --------------------------------------------------------------------------


def _s4(change, code, qid="q07"):
    def case(world):
        world.edit(qid, change)
        return [(qid, code)], {}
    return case


def _first(change):
    return lambda d: change(d["sources"][0])


def _gold_adds(token):
    return lambda d: d.update(gold_answer=d["gold_answer"] + f" It also reads `{token}`.")


S4_BREAKS = {
    "absent-at-the-recorded-commit": ({}, _s4(_first(_set(path=f"docs/{s.WORD}nowhere.md")), "SOURCE_PATH_ABSENT"), 1),
    "only-in-the-scaffold-commit": ({}, _s4(_first(_set(path=s.SCAFFOLD_ONLY)), "SOURCE_PATH_ABSENT"), 1),
    "only-in-the-working-tree": ({}, _s4(_first(_set(path=s.WORKTREE_ONLY)), "SOURCE_PATH_ABSENT"), 1),
    "a-folder-not-a-file": ({}, _s4(_first(_set(path="docs")), "SOURCE_PATH_ABSENT"), 1),
    "a-scaffold-path-the-copy-also-holds": ({}, _s4(_first(_set(path=s.SCAFFOLD_MAP, lines=[1, 2])),
                                                   "SOURCE_IS_SCAFFOLD"), 1),
    "a-scaffold-folder-path": ({}, _s4(_first(_set(path=s.SCAFFOLD_NOTE, lines=[1, 2])), "SOURCE_IS_SCAFFOLD"), 1),
    "not-text": ({}, _s4(_first(_set(path=s.BINARY, lines=[1, 1])), "SOURCE_NOT_TEXT"), 1),
    "span-past-the-end": ({}, _s4(_first(_set(lines=[3, 99])), "SPAN_OUT_OF_FILE"), 1),
    "span-before-the-start": ({}, _s4(_first(_set(lines=[0, 5])), "SPAN_OUT_OF_FILE"), 1),
    "span-as-long-as-the-scaffold-commit-file": ({}, _s4(_first(_set(path=s.CHANGED, lines=[1, 8])),
                                                         "SPAN_OUT_OF_FILE"), 1),
    "heading-not-in-the-file": ({}, _s4(_first(_set(heading="## a heading nobody wrote")), "HEADING_NOT_FOUND"), 1),
    "heading-is-only-part-of-a-line": ({}, _s4(_first(_set(heading="## " + s.WORD)), "HEADING_NOT_FOUND"), 1),
    "span-in-another-file": ({}, _s4(_first(_set(path=s.OTHER, lines=[1, 4], heading=None)), "ANSWER_NOT_IN_SPANS"), 1),
    "span-in-another-part-of-the-file": ({}, _s4(_first(_set(lines=[7, 8])), "ANSWER_NOT_IN_SPANS"), 1),
    "answer-only-in-the-scaffold-commit-version": (
        {}, _s4(lambda d: (d["sources"][0].update(path=s.CHANGED, lines=[1, 3], heading=None),
                           d.update(gold_answer=f"It is the `{s.CHANGED_LATE_TOKEN}`.")), "ANSWER_NOT_IN_SPANS"), 1),
    "an-identifier-of-the-answer-the-span-lacks": ({}, _s4(_gold_adds(f"{s.WORD}missing_name"), "ANSWER_NOT_IN_SPANS"), 1),
    "a-path-in-the-answer-that-is-no-source": ({}, _s4(_gold_adds(f"docs/{s.WORD}elsewhere.md"),
                                                       "ANSWER_NOT_IN_SPANS"), 1),
    "a-prose-answer-the-span-does-not-state": (
        {}, _s4(lambda d: (d["sources"][0].update(path=s.OTHER, lines=[1, 4], heading=None),
                           d.update(gold_answer="The routine reads the configuration value and returns the result to "
                                                "its caller.")), "ANSWER_NOT_IN_SPANS"), 1),
    "every-alternative-bad": (
        {}, _s4(lambda d: d["sources"].__setitem__(0, [{"path": f"docs/{s.WORD}nowhere.md", "lines": [1, 2]},
                                                       {"path": s.SCAFFOLD_ONLY, "lines": [1, 2]}]),
                "SOURCE_PATH_ABSENT"), 1),
    "one-of-two-entries-bad": (
        {}, _s4(lambda d: d["sources"].append({"path": f"docs/{s.WORD}nowhere.md", "lines": [1, 2]}),
                "SOURCE_PATH_ABSENT"), 1),
    "an-entry-the-answer-needs-dropped": (
        {}, _s4(lambda d: d.update(sources=[{"path": s.source_path(7), "lines": [4, 4]}]), "ANSWER_NOT_IN_SPANS"), 1),
}

# --------------------------------------------------------------------------
# S4, rule 2a after W2-94 GOLD (owner, 2026-11-13): (i) a hyphen-digit word is an identifier token only when it is
# id-shaped (the part before the first hyphen starts with an upper-case letter and holds only upper-case letters and
# digits: ``DEC-051``, ``W2-94``); (ii) a path token is also held when its segments occur in order in the spans
# ``q07``'s answer is the good one with a word added; the held ones expect "20 of 20 hold"
# --------------------------------------------------------------------------

GOOD_07 = f"The routine `{s.WORD}func07_run` returns {s.WORD}ans07."
ID_TOKEN = "ZQXW-9451"                              # made up; id-shaped (upper-case prefix, then a digit)
JOINER = f"src/{s.WORD}/joiner.py"                  # a span that joins a path the way code does
LITERAL_HOLDER = f"src/{s.WORD}/literal_holder.py"  # a span that holds the same path literally
PATH_TOKEN = f"{s.WORD}spec/2-PLAN/{s.WORD}VIEWS.md"
JOINER_TEXT = ("import os\n"
               "# The view list path is joined here.\n"
               f"def {s.WORD}_views():\n"
               f"    return os.path.join(\"{s.WORD}spec/2-PLAN\", \"{s.WORD}VIEWS.md\")\n")
LITERAL_TEXT = ("import os\n"
                f"# The view list path is {PATH_TOKEN} here.\n"
                f"def {s.WORD}_views():\n"
                "    return None\n")


def _with_id_in_the_span():
    """The planted source of q07 with the id-shaped word on its line 5 (the file keeps its eight lines)."""
    lines = s.source_lines(7)
    lines[4] = f"It returns {s.WORD}ans07 to its caller, see {ID_TOKEN}."
    return {s.source_path(7): "\n".join(lines) + "\n"}


def _answer_adds(text):
    """The good answer of q07 with ``text`` added: the added words are what the case is about."""
    return lambda d: d.update(gold_answer=f"{GOOD_07} {text}")


def _joined(answer, path=JOINER, last=4):
    """q07 cites the joiner file (lines 1 to ``last``) and states ``answer``."""
    return lambda d: (d["sources"][0].update(path=path, lines=[1, last], heading=None), d.update(gold_answer=answer))


def _path_answer(token):
    return f"The view list path is `{token}`."


def _holds(change):
    def case(world):
        world.edit("q07", change)
        return [], {}
    return case


S4_BREAKS.update({
    # (i) an id-shaped hyphen-digit word the spans lack is still a token that is not held
    "an-id-shaped-word-the-span-lacks": ({}, _s4(_answer_adds(f"It is tagged {ID_TOKEN}."), "ANSWER_NOT_IN_SPANS"), 1),
    "an-id-shaped-word-with-digits-in-its-prefix-the-span-lacks": (
        {}, _s4(_answer_adds("It is tagged ZQXW94-7."), "ANSWER_NOT_IN_SPANS"), 1),
    "a-one-letter-id-shaped-word-the-span-lacks": ({}, _s4(_answer_adds("It is tagged X-5."), "ANSWER_NOT_IN_SPANS"), 1),
    "a-back-quoted-lower-case-hyphen-digit-word-the-span-lacks": (
        {}, _s4(_answer_adds("It reads `level-2`."), "ANSWER_NOT_IN_SPANS"), 1),
    # (ii) segments out of order, one absent or one repeated beyond what the spans hold do not hold
    "path-segments-in-reverse-order": (
        {"extra_copy": {JOINER: JOINER_TEXT}},
        _s4(_joined(_path_answer(f"{s.WORD}VIEWS.md/2-PLAN/{s.WORD}spec")), "ANSWER_NOT_IN_SPANS"), 1),
    "path-segments-with-the-middle-one-swapped": (
        {"extra_copy": {JOINER: JOINER_TEXT}},
        _s4(_joined(_path_answer(f"{s.WORD}spec/{s.WORD}VIEWS.md/2-PLAN")), "ANSWER_NOT_IN_SPANS"), 1),
    "a-path-segment-absent-from-the-spans": (
        {"extra_copy": {JOINER: JOINER_TEXT}},
        _s4(_joined(_path_answer(f"{s.WORD}spec/2-PLAN/{s.WORD}NOPE.md")), "ANSWER_NOT_IN_SPANS"), 1),
    "a-path-segment-held-once-but-named-twice": (
        {"extra_copy": {JOINER: JOINER_TEXT}},
        _s4(_joined(_path_answer(f"{s.WORD}spec/{s.WORD}spec/{s.WORD}VIEWS.md")), "ANSWER_NOT_IN_SPANS"), 1),
})

S4_HOLDS = {
    # (i) lower-case or mixed-case hyphen-digit words are not tokens (they count as prose, if at all)
    "lower-case-hyphen-digit-words": ({}, _holds(_answer_adds("It handles level-2 and top-3.")), 0),
    "a-capitalised-hyphen-digit-word-with-lower-case-letters": ({}, _holds(_answer_adds("It reaches Level-2.")), 0),
    "a-hyphen-digit-word-that-starts-with-a-digit": ({}, _holds(_answer_adds("It uses 2D-3.")), 0),
    "a-lower-case-look-alike-of-an-id": ({}, _holds(_answer_adds("It is tagged zqxw-9451.")), 0),
    # (i) the id-shaped word is held when the span has it
    "an-id-shaped-word-the-span-holds": (
        {"extra_copy": _with_id_in_the_span()}, _holds(_answer_adds(f"It is tagged {ID_TOKEN}.")), 0),
    # (ii) a path joined by code, a literal path, empty segments, a subsequence of the segments
    "a-path-joined-the-way-code-joins-it": (
        {"extra_copy": {JOINER: JOINER_TEXT}}, _holds(_joined(_path_answer(PATH_TOKEN))), 0),
    "a-literal-path-in-the-span": (
        {"extra_copy": {LITERAL_HOLDER: LITERAL_TEXT}},
        _holds(_joined(_path_answer(PATH_TOKEN), path=LITERAL_HOLDER, last=3)), 0),
    "a-path-with-a-leading-and-a-doubled-slash": (
        {"extra_copy": {JOINER: JOINER_TEXT}},
        _holds(_joined(_path_answer(f"/{s.WORD}spec//2-PLAN/{s.WORD}VIEWS.md"))), 0),
    "a-path-whose-segments-are-some-of-the-spans-in-order": (
        {"extra_copy": {JOINER: JOINER_TEXT}},
        _holds(_joined(_path_answer(f"{s.WORD}spec/{s.WORD}VIEWS.md"))), 0),
}

# --------------------------------------------------------------------------
# S4: the nonexistent questions (q19 and q20 of a set of 20; the asked names are s.ghost(19) and s.ghost(20))
# --------------------------------------------------------------------------


def _ghost_in_a_file(world):
    return [("q19", "NONEXISTENT_NAME_FOUND")], {}


def _only_real_names(world):
    world.edit("q19", lambda d: d.update(question="Where is `real_function` defined?"))
    return [("q19", "NONEXISTENT_NAME_FOUND")], {}


def _only_a_real_path(world):
    world.edit("q19", lambda d: d.update(question=f"What is in `{s.LOCATOR}`?"))
    return [("q19", "NONEXISTENT_NAME_FOUND")], {}


def _no_name(world):
    world.edit("q19", lambda d: d.update(question="Where is the thing the team always asks about?"))
    return [("q19", "NONEXISTENT_NO_NAME")], {}


def _nonexistent_source_absent(world):
    world.edit("q19", lambda d: d["sources"][0].update(path=f"docs/{s.WORD}nowhere.md"))
    return [("q19", "SOURCE_PATH_ABSENT")], {}


NONEXISTENT_BREAKS = {
    "the-asked-name-is-in-a-file": ({"extra_copy": {"src/zqxw94/uses_ghost.py": f"NAME = '{s.ghost(19)}'\n"}},
                                    _ghost_in_a_file, 1),
    "the-asked-name-is-in-a-path": ({"extra_copy": {f"src/{s.ghost(19)}.py": "x = 1\n"}}, _ghost_in_a_file, 1),
    "the-question-names-only-existing-things": ({}, _only_real_names, 1),
    "the-question-names-only-an-existing-file": ({}, _only_a_real_path, 1),
    "the-question-names-nothing": ({}, _no_name, 1),
    "the-file-that-would-hold-it-is-absent": ({}, _nonexistent_source_absent, 1),
}

# --------------------------------------------------------------------------
# Fail closed: what the program cannot read or parse is refused (exit 2), never passed
# --------------------------------------------------------------------------


def _no_sets_root(world):
    return [("REFUSED", "SETS_ROOT_UNREADABLE")], {"sets_root": world.base / "no-such-root"}


def _sets_root_is_a_file(world):
    path = s.write(world.base / "a-file", "not a folder\n")
    return [("REFUSED", "SETS_ROOT_UNREADABLE")], {"sets_root": path}


def _sets_root_without_the_set(world):
    (world.base / "empty-root").mkdir()
    return [("REFUSED", "HIDDEN_UNREADABLE")], {"sets_root": world.base / "empty-root"}


def _no_hidden_folder(world):
    shutil.rmtree(world.hidden_dir)
    return [("REFUSED", "HIDDEN_UNREADABLE")], {}


def _no_development_half(world):
    shutil.rmtree(world.dev_dir)
    return [("REFUSED", "HIDDEN_VISIBLE_UNREADABLE")], {}


def _no_copy(world):
    return [("REFUSED", "COPY_UNREADABLE")], {"copy": world.base / "no-such-clone"}


def _copy_is_no_repository(world):
    (world.base / "plain").mkdir()
    return [("REFUSED", "COPY_UNREADABLE")], {"copy": world.base / "plain"}


def _unparsable(text, code="QUESTION_UNPARSABLE"):
    def case(world):
        path = world.qpath("q07")
        if isinstance(text, bytes):
            path.write_bytes(text)
        else:
            path.write_text(text, encoding="utf-8")
        return [("REFUSED", code, "q07")], {}
    return case


def _bad_set_name(world):
    return [("REFUSED", "SET_NAME_BAD")], {"extra": ["--set", "../examin"]}


def _unknown_set(world):
    return [("REFUSED", "HIDDEN_UNREADABLE")], {"extra": ["--set", "no-such-set"]}


def _no_copy_flag(world):
    return [("REFUSED", "USAGE")], {"drop": ("--copy",)}


def _no_sets_root_flag(world):
    return [("REFUSED", "USAGE")], {"drop": ("--sets-root",)}


def _unknown_flag(world):
    return [("REFUSED", "USAGE")], {"extra": ["--write-something"]}


def _head_text(text, code):
    """A COPY-HEAD.txt of the given text: the planted copy is rebuilt with it."""
    return ({"copy_head": text}, lambda world: ([("REFUSED", code)], {}), 2)


def _commit_not_in_the_copy(world):
    return [("REFUSED", "COMMIT_NOT_IN_COPY")], {}


FAIL_CLOSED = {
    "no-sets-root": ({}, _no_sets_root, 2),
    "sets-root-is-a-file": ({}, _sets_root_is_a_file, 2),
    "sets-root-without-the-set": ({}, _sets_root_without_the_set, 2),
    "no-hidden-folder": ({}, _no_hidden_folder, 2),
    "no-development-half": ({}, _no_development_half, 2),
    "no-copy": ({}, _no_copy, 2),
    "copy-is-no-repository": ({}, _copy_is_no_repository, 2),
    "no-copy-head-file": ({"copy_head": None}, lambda w: ([("REFUSED", "COPY_HEAD_UNREADABLE")], {}), 2),
    "copy-head-empty": _head_text("\n", "COPY_HEAD_MALFORMED"),
    "copy-head-twelve-digits": _head_text("0a82082495f5\n", "COPY_HEAD_MALFORMED"),
    "copy-head-forty-one-digits": _head_text("a" * 41 + "\n", "COPY_HEAD_MALFORMED"),
    "copy-head-not-hex": _head_text("g" * 40 + "\n", "COPY_HEAD_MALFORMED"),
    "copy-head-a-word": _head_text("HEAD\n", "COPY_HEAD_MALFORMED"),
    "copy-head-two-commits": _head_text("a" * 40 + " " + "b" * 40 + "\n", "COPY_HEAD_MALFORMED"),
    "copy-head-not-in-the-copy": ({"copy_head": "c" * 40 + "\n"}, lambda w: ([("REFUSED", "COMMIT_NOT_IN_COPY")], {}), 2),
    "a-question-file-that-does-not-parse": ({}, _unparsable(f"sources: [{s.WORD}unclosed\nquestion: '{s.WORD}x\n"), 2),
    "a-question-file-that-is-a-list": ({}, _unparsable(f"- {s.WORD}one\n- two\n"), 2),
    "a-question-file-that-is-empty": ({}, _unparsable(""), 2),
    "a-question-file-that-is-not-text": ({}, _unparsable(b"\xff\xfe\x00\x01\xc3\x28", "QUESTION_UNPARSABLE"), 2),
    "a-set-name-that-is-a-path": ({}, _bad_set_name, 2),
    "a-set-that-is-not-there": ({}, _unknown_set, 2),
    "no-copy-flag": ({}, _no_copy_flag, 2),
    "no-sets-root-flag": ({}, _no_sets_root_flag, 2),
    "an-unknown-flag": ({}, _unknown_flag, 2),
}
