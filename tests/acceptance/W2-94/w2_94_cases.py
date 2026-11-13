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


S1_DRAW = {
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
