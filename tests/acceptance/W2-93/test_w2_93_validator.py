"""W2-93's acceptance tests for ``validate_hidden.py``: form only (counts, fields, sources exist), on planted stand-ins.

Success lines S1, S2, S4 and S5 and failure line F2 of ``DAEO-6y0x``. Every case plants a stand-in sets root in its own
temporary folder (never the real hidden half), runs the validator as a subprocess and reads its stdout and stderr
together. No case prints, and none may find in an output, a stand-in question or answer (``WORD``) or a stand-in
variant's name, path or text (``VWORD``): counts and ids only.

Red today for one reason: ``fixtures/evaluation/adoption-proving-ground/validate_hidden.py`` is absent at the base.
"""

from __future__ import annotations

import os
import re

import pytest
import w2_93_standin as s

RUST, QID = "rust-workspace", "rust-workspace-h03"  # the repository and the question the field cases break
NO_HIDDEN = "refused: no hidden half under the sets root: fixtures/evaluation/adoption-proving-ground/hidden"


def assert_refused(run):
    """A refusal as the interface fixes it: exit 2, refusal lines only for the faults, no traceback, no valid line, and
    no stand-in question, answer, variant name, path or text in the output."""
    head = run.out[:300]
    assert run.code == 2, f"exit {run.code}: {head}"
    assert "Traceback" not in run.out, "a traceback was printed"
    assert run.refusals, f"no `refused:` line: {head}"
    assert not any(line.startswith("valid:") for line in run.lines), "a valid line beside a refusal"
    assert s.WORD not in run.out, "a stand-in question or answer reached the output"
    assert s.VWORD not in run.out, "a stand-in variant's name, path or text reached the output"


def broken(valid, tmp_path, change, *extra):
    """The valid stand-in copied, broken by ``change(root)``, and validated."""
    root = s.copy_root(valid.root, tmp_path)
    change(root)
    return s.validate(root, tmp_path, *extra)


# --------------------------------------------------------------------------
# S1: at least 10 questions per repository, each with the README's fields
# --------------------------------------------------------------------------

def test_s1_the_valid_stand_in_exits_0_with_a_count_of_10_or_more_for_each_repository(valid):
    """S1: a valid stand-in: exit 0, each of the six repositories' count line shows 10 or more, and the total says so."""
    run = valid.run
    assert run.code == 0, run.out[:400]
    assert "Traceback" not in run.out and not run.refusals
    counts = {}
    for repository in s.REPOS:
        found = [m for m in (re.match(rf"{re.escape(repository)}: (\d+) hidden questions", line) for line in run.lines)
                 if m]
        assert len(found) == 1, f"{repository}: {len(found)} count lines"
        counts[repository] = int(found[0].group(1))
        assert counts[repository] >= 10, f"{repository}: {counts[repository]}"
    total = re.search(r"^valid: (\d+) hidden questions in 6 repositories, (\d+) hidden variants \(seed (\d+)\)$",
                      run.out, re.M)
    assert total, "no `valid:` line of the interface's form"
    assert int(total.group(1)) == sum(counts.values())
    assert int(total.group(2)) == s.VARIANT_COUNT
    assert int(total.group(3)) == s.SEED, "the default seed is W2-81's DEFAULT_SEED"


def test_s1_a_seed_given_is_the_seed_the_valid_line_shows(tmp_path, valid):
    """S1 (the `--seed` option): the stand-in is valid at another seed, and the line names it."""
    run = s.validate(valid.root, tmp_path, "--seed", "4242")
    assert run.code == 0, run.out[:400]
    assert re.search(r"^valid: \d+ hidden questions in 6 repositories, \d+ hidden variants \(seed 4242\)$", run.out,
                     re.M)


def test_s1_nine_questions_in_one_repository_is_refused_naming_it(tmp_path, valid):
    """S1: 9 questions in one repository: exit 2, naming the repository and the count."""
    run = broken(valid, tmp_path, lambda root: s.edit_questions(
        root, RUST, lambda data: data["questions"].pop()))
    assert_refused(run)
    assert f"refused: {RUST}: 9 hidden questions, at least 10 needed" in run.refusals
    assert not [line for line in run.refusals if not line.startswith(f"refused: {RUST}:")], "another repository named"


FIELD_FAULTS = {
    "category": lambda q: q.pop("category"),
    "question": lambda q: q.pop("question"),
    "gold_answer": lambda q: q.pop("gold_answer"),
    "sources": lambda q: q.pop("sources"),
    "source-path": lambda q: q["sources"][0].pop("path"),
    "source-holds": lambda q: q["sources"][0].pop("holds"),
    "sources-empty": lambda q: q.__setitem__("sources", []),
    "forbidden-not-a-list": lambda q: q.__setitem__("forbidden", "a-single-string"),
    "forbidden-holds-a-non-string": lambda q: q.__setitem__("forbidden", list(q.get("forbidden") or []) + [7]),
    "forbidden-holds-an-empty-string": lambda q: q.__setitem__("forbidden", list(q.get("forbidden") or []) + [""]),
    "gold_answer-blank": lambda q: q.__setitem__("gold_answer", ""),
    "category-not-a-string": lambda q: q.__setitem__("category", 7),
}


@pytest.mark.parametrize("fault", list(FIELD_FAULTS))
def test_s1_a_question_missing_a_field_or_of_a_wrong_type_is_refused_naming_its_id(tmp_path, valid, fault):
    """S1: a question missing a README field (category, question, gold_answer, sources; a source without path or
    holds), or a field of the wrong type (`forbidden`, when present, a list of non-empty strings): exit 2, naming the
    question's id and not its text. `forbidden` itself is optional: see the next case."""
    run = broken(valid, tmp_path, lambda root: s.edit_questions(
        root, RUST, lambda data: FIELD_FAULTS[fault](data["questions"][2])))
    assert_refused(run)
    assert run.names(QID), f"no refusal names {QID}: {run.refusals}"
    assert not [line for line in run.refusals if QID not in line], "a refusal that does not concern the question"


def test_s1_questions_without_a_forbidden_key_are_valid(tmp_path, valid):
    """S1 (the lead's decision of batch 2): `forbidden` is optional, absent meaning no forbidden citation, as in W2-81's
    own visible half. A stand-in whose questions in one repository carry no `forbidden` key at all exits 0, with the
    count line and the total unchanged."""
    def drop(data):
        for question in data["questions"]:
            question.pop("forbidden", None)

    run = broken(valid, tmp_path, lambda root: s.edit_questions(root, RUST, drop))
    assert run.code == 0, run.out[:400]
    assert "Traceback" not in run.out and not run.refusals, run.refusals
    assert s.WORD not in run.out and s.VWORD not in run.out, "a stand-in question, answer or variant reached the output"
    assert f"{RUST}: 10 hidden questions" in run.lines
    assert re.search(r"^valid: 60 hidden questions in 6 repositories, \d+ hidden variants \(seed \d+\)$", run.out, re.M)


def test_s1_a_question_missing_its_id_is_refused(tmp_path, valid):
    """S1: a question with no `id` has none to name: exit 2 and a refusal, no traceback, nothing quoted."""
    run = broken(valid, tmp_path, lambda root: s.edit_questions(
        root, RUST, lambda data: data["questions"][2].pop("id")))
    assert_refused(run)


@pytest.mark.parametrize("how", ["duplicate", "wrong-form"])
def test_s1_an_id_that_is_given_twice_or_is_not_of_the_form_is_refused_naming_it(tmp_path, valid, how):
    """S1: ids are `<repository>-h<nn>` and unique in the half: a duplicate and a wrong form are each refused naming
    the id."""
    def change(data):
        data["questions"][3]["id"] = QID if how == "duplicate" else "rust-workspace-x04"

    run = broken(valid, tmp_path, lambda root: s.edit_questions(root, RUST, change))
    assert_refused(run)
    named = QID if how == "duplicate" else "rust-workspace-x04"
    assert run.names(named), f"no refusal names {named}: {run.refusals}"


@pytest.mark.parametrize("fault", ["form", "repository", "questions-not-a-list"])
def test_s1_a_question_file_of_the_wrong_form_is_refused_naming_the_repository(tmp_path, valid, fault):
    """S1: `form: w2-81-questions/1`, `repository` equal to the file's name, `questions` a list: each refused."""
    def change(data):
        if fault == "form":
            data["form"] = "w2-81-questions/2"
        elif fault == "repository":
            data["repository"] = "python-app"
        else:
            data["questions"] = {"not": "a list"}

    run = broken(valid, tmp_path, lambda root: s.edit_questions(root, RUST, change))
    assert_refused(run)
    assert [line for line in run.refusals if RUST in line], f"no refusal names {RUST}: {run.refusals}"


# --------------------------------------------------------------------------
# S2: a hidden variant for each kind the visible builders do not produce
# --------------------------------------------------------------------------

def test_s2_the_variants_line_of_each_planted_repository_names_each_kind_its_visible_build_lacks(valid, visible):
    """S2: a valid stand-in: the variants line of each planted repository names each core kind its visible build lacks,
    with its count (the stand-in plants one of each)."""
    run = valid.run
    assert run.code == 0, run.out[:400]
    for repository in s.PLANTED:
        lines = [line for line in run.lines if line.startswith(f"{repository}: hidden variants")]
        assert len(lines) == 1, f"{repository}: {len(lines)} variants lines"
        lacking = [kind for kind in s.CORE if kind not in visible[repository]]
        assert lacking, f"{repository} lacks no core kind: the stand-in's premise broke"
        for kind in lacking:
            found = re.search(rf"\b{re.escape(kind)}=(\d+)", lines[0])
            assert found, f"{repository}: the line names no count for {kind}"
            assert int(found.group(1)) == s.PLAN[repository].count(kind) == 1, f"{repository}: {kind}"


A_PAIRS = [(repository, kind) for repository, kinds in s.PLAN.items() for kind in kinds if kind in s.CORE]


@pytest.mark.parametrize("repository, kind", A_PAIRS, ids=[f"{r}-{k}" for r, k in A_PAIRS])
def test_s2_a_required_kind_removed_is_refused_naming_the_repository_and_the_kind(tmp_path, valid, repository, kind):
    """S2: the hidden variant of a kind the repository's visible build lacks removed: exit 2, naming both."""
    vid = s.variant_id(repository, kind)
    run = broken(valid, tmp_path, lambda root: s.edit_variants(root, lambda data: data.__setitem__(
        "variants", [v for v in data["variants"] if v["id"] != vid])))
    assert_refused(run)
    assert f"refused: {repository}: no hidden variant of kind {kind}" in run.refusals, run.refusals


@pytest.mark.parametrize("kind", ["legacy-document", "large-file"])
def test_s2_the_legacy_document_or_large_file_variant_removed_is_refused_naming_the_kind(tmp_path, valid, kind):
    """S2: the only `legacy-document` (or `large-file`) variant removed: exit 2, naming the kind."""
    run = broken(valid, tmp_path, lambda root: s.edit_variants(root, lambda data: data.__setitem__(
        "variants", [v for v in data["variants"] if v["kind"] != kind])))
    assert_refused(run)
    assert f"refused: kind {kind}: no hidden variant where the visible builders do not plant it" in run.refusals, \
        run.refusals


def test_s2_a_variant_in_the_clean_twin_is_refused_naming_its_number_and_id(tmp_path, valid):
    """S2 (the clean twin has no variant): one added as the 14th is refused naming its number and id."""
    def change(data):
        extra = s._variant("python-app-clean", "large-file")
        extra["id"] = "cln-large"
        extra["repository"] = "python-app-clean"
        data["variants"].append(extra)

    run = broken(valid, tmp_path, lambda root: s.edit_variants(root, change))
    assert_refused(run)
    assert [line for line in run.refusals if line.startswith("refused: hidden variant #14 (cln-large):")], run.refusals


def test_s2_a_variant_that_cannot_be_built_is_refused_naming_its_number_and_id_only(tmp_path, valid):
    """S2 (every variant builds): a step that removes a file no commit holds: refused as `cannot be built`, by number
    and id, never its message, path or texts."""
    def change(data):
        data["variants"][0]["steps"].append({"message": f"{s.VWORD} gone", "remove": [f"no/{s.VWORD}/such-file"]})

    run = broken(valid, tmp_path, lambda root: s.edit_variants(root, change))
    assert_refused(run)
    assert "refused: hidden variant #1 (pyt-secret): cannot be built" in run.refusals, run.refusals


@pytest.mark.parametrize("fault", ["unknown-kind", "duplicate-id", "variants-not-a-list"])
def test_s2_a_variants_file_with_an_unknown_kind_a_duplicate_id_or_no_list_is_refused(tmp_path, valid, fault):
    """S2: `variants:` a list of mappings with unique ids, each of a planted kind."""
    def change(data):
        if fault == "unknown-kind":
            data["variants"][0]["kind"] = "not-a-planted-kind"
        elif fault == "duplicate-id":
            data["variants"][1]["id"] = data["variants"][0]["id"]
        else:
            data["variants"] = {"not": "a list"}

    run = broken(valid, tmp_path, lambda root: s.edit_variants(root, change))
    assert_refused(run)
    if fault == "unknown-kind":
        assert [line for line in run.refusals if line.startswith("refused: hidden variant #1 (pyt-secret):")], \
            run.refusals
    if fault == "variants-not-a-list":
        assert [line for line in run.refusals if "variants.yaml" in line], run.refusals


# --------------------------------------------------------------------------
# S4 and F2: every gold answer is held by the built repository
# --------------------------------------------------------------------------

GOLD_FAULTS = {
    "line-not-at-head": lambda q: q["sources"][0].__setitem__("holds", f"{s.WORD} a line no file of the build holds"),
    "path-not-at-head": lambda q: q["sources"][0].__setitem__("path", f"docs/{s.WORD}-no-such-file.md"),
    "fact-of-the-answer-missing": lambda q: q.__setitem__("gold_answer", f"{s.WORD} {{a_fact_no_builder_records}}"),
}


@pytest.mark.parametrize("fault", list(GOLD_FAULTS))
def test_s4_f2_a_gold_answer_the_built_copy_does_not_hold_is_refused_naming_the_question_id_only(tmp_path, valid,
                                                                                                 fault):
    """S4 and F2: a question whose gold source line is not at the built HEAD (or whose path is not, or whose answer's
    template names a fact the builder lacks): exit 2, naming the question's id, never its text."""
    run = broken(valid, tmp_path, lambda root: s.edit_questions(
        root, RUST, lambda data: GOLD_FAULTS[fault](data["questions"][4])))
    assert_refused(run)
    assert run.names("rust-workspace-h05"), f"no refusal names rust-workspace-h05: {run.refusals}"
    assert not [line for line in run.refusals if "rust-workspace-h05" not in line], "another question named"


# --------------------------------------------------------------------------
# S5: every forbidden citation names a file of the built copy; what cannot be read refuses
# --------------------------------------------------------------------------

@pytest.mark.parametrize("citation", [f"docs/{s.WORD}-no-such-file.md", "{stale}.bak"],
                         ids=["a-literal-path", "a-fact-with-a-suffix"])
def test_s5_a_forbidden_citation_naming_no_file_of_the_built_copy_is_refused_naming_the_id(tmp_path, valid, citation):
    """S5: a must-not-cite file that is not a file of the built copy: exit 2, naming the question's id."""
    run = broken(valid, tmp_path, lambda root: s.edit_questions(
        root, RUST, lambda data: data["questions"][1].__setitem__("forbidden", [citation])))
    assert_refused(run)
    assert run.names("rust-workspace-h02"), f"no refusal names rust-workspace-h02: {run.refusals}"
    assert not [line for line in run.refusals if "rust-workspace-h02" not in line], "another question named"


def _no_permission(path):
    path.chmod(0)
    assert not os.access(path, os.R_OK), "the stand-in file is still readable: the case cannot show the refusal"


def _break_file(root, name, how, base):
    """Break the hidden folder's file ``name`` as ``how`` says; returns the file name the refusal must name."""
    path = s.hidden_of(root) / name
    if how == "no-read-permission":
        _no_permission(path)
    elif how == "not-utf8":
        path.write_bytes(path.read_bytes() + f"\n# {s.WORD} ".encode() + b"\xff\xfe\xfa\n")
    elif how == "bad-yaml":
        path.write_text(f"form: [{s.WORD} unclosed\nquestions: {{ {s.WORD}: [\n  - : :\n", encoding="utf-8")
    elif how == "wrong-top-level-type":
        path.write_text(f"- {s.WORD}\n- two\n", encoding="utf-8")
    elif how == "symbolic-link-in-place":
        elsewhere = base / "elsewhere.yaml"
        elsewhere.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(elsewhere)
    else:
        raise AssertionError(how)
    return name


UNREADABLE = ["no-read-permission", "not-utf8", "bad-yaml", "wrong-top-level-type", "symbolic-link-in-place"]


@pytest.mark.parametrize("how", UNREADABLE)
@pytest.mark.parametrize("name", ["rust-workspace.yaml", "variants.yaml"])
def test_s5_a_file_the_validator_cannot_read_is_refused_naming_the_file_only(tmp_path, valid, how, name):
    """S5 (fail closed): a question file or `variants.yaml` with no read permission, not UTF-8, of bad YAML, of a wrong
    top-level type, or a symbolic link: exit 2, naming the file and nothing of its content (the bad ones carry a
    planted word on the very lines that fail)."""
    root = s.copy_root(valid.root, tmp_path)
    try:
        _break_file(root, name, how, tmp_path)
        run = s.validate(root, tmp_path)
    finally:
        for path in s.hidden_of(root).iterdir():
            if not path.is_symlink():
                path.chmod(0o644)
    assert_refused(run)
    assert [line for line in run.refusals if name in line], f"no refusal names {name}: {run.refusals}"


@pytest.mark.parametrize("how", ["extra-file", "extra-folder", "extra-symbolic-link"])
def test_s5_an_entry_of_the_hidden_folder_that_is_not_the_half_is_refused_naming_its_file_name(tmp_path, valid, how):
    """S5: the folder holds the six question files and `variants.yaml` and nothing else: another file, a subfolder or
    a symbolic link is refused naming its file name only."""
    name = {"extra-file": "notes.txt", "extra-folder": "spare", "extra-symbolic-link": "alias.yaml"}[how]

    def change(root):
        extra = s.hidden_of(root) / name
        if how == "extra-file":
            extra.write_text(f"{s.WORD}\n", encoding="utf-8")
        elif how == "extra-folder":
            extra.mkdir()
            (extra / "inner.yaml").write_text(f"{s.WORD}\n", encoding="utf-8")
        else:
            extra.symlink_to(s.hidden_of(root) / "python-app.yaml")

    run = broken(valid, tmp_path, change)
    assert_refused(run)
    assert [line for line in run.refusals if name in line], f"no refusal names {name}: {run.refusals}"


@pytest.mark.parametrize("name", ["legacy-docs.yaml", "variants.yaml"])
def test_s5_a_missing_repository_file_or_variants_file_is_refused_naming_it(tmp_path, valid, name):
    """S5/S1: a repository's question file (or `variants.yaml`) absent: exit 2, naming the repository (or the file)."""
    run = broken(valid, tmp_path, lambda root: (s.hidden_of(root) / name).unlink())
    assert_refused(run)
    wanted = name.removesuffix(".yaml") if name != "variants.yaml" else name
    assert [line for line in run.refusals if wanted in line], f"no refusal names {wanted}: {run.refusals}"


def test_s5_the_validator_leaves_none_of_its_built_copy_behind_after_a_refusal(tmp_path, valid):
    """S5 (interface item 4): the temporary folder of the built copy is removed when the run ends, refused or valid."""
    run = broken(valid, tmp_path, lambda root: s.edit_questions(
        root, RUST, lambda data: data["questions"].pop()))
    assert_refused(run)
    assert not list(run.tmpdir.iterdir()), f"left in TMPDIR: {sorted(p.name for p in run.tmpdir.iterdir())}"
    assert not list(valid.run.tmpdir.iterdir()), "left in TMPDIR after a valid run"


def test_s5_the_runners_and_w2_81s_files_are_untouched_but_the_two_paths_of_dec_1144_6():
    """S5: `git diff --name-only a7b36bcfd98a -- tests/acceptance/W2-81` lists nothing but `w2_81_run.py` and
    `test_w2_81_runner.py`."""
    import subprocess

    done = subprocess.run(["git", "-C", str(s.REPO_ROOT), "diff", "--name-only", s.BASE_COMMIT, "--",
                           "tests/acceptance/W2-81"], capture_output=True, text=True)
    assert done.returncode == 0, "git diff failed"
    allowed = {"tests/acceptance/W2-81/w2_81_run.py", "tests/acceptance/W2-81/test_w2_81_runner.py"}
    changed = set(done.stdout.split())
    assert changed <= allowed, f"W2-81 files changed beyond DEC-1144 (6)'s two: {sorted(changed - allowed)}"


# --------------------------------------------------------------------------
# The stand-in itself: the red reason is the missing validator, nothing in the stand-in
# --------------------------------------------------------------------------

def test_the_stand_in_plants_each_kind_the_visible_builders_lack(visible):
    """The premise of S2: the stand-in's plan covers each core kind each planted repository's visible build lacks (one
    each), one `legacy-document` and one `large-file` where the visible build has none, and nothing in the clean twin."""
    for repository in s.PLANTED:
        planted = set(s.PLAN[repository])
        assert planted & set(s.CORE) == {k for k in s.CORE if k not in visible[repository]}, repository
        assert len([k for k in s.PLAN[repository] if k in s.CORE]) == len(planted & set(s.CORE)), "one of each kind"
    for kind in s.LEGACY:
        homes = [r for r in s.PLANTED if kind in s.PLAN[r]]
        assert homes and all(kind not in visible[r] for r in homes), kind
    assert s.VARIANT_COUNT == 13 and not visible[s.REPOS[-1]]


def test_the_stand_in_builds_and_each_question_resolves_with_its_forbidden_files_at_head(tmp_path):
    """The stand-in is itself valid: its 13 variants build, each question resolves on the built copy, each forbidden
    citation names a file at HEAD, and every question and answer carries the planted word."""
    import w2_81_build as build
    import w2_81_git as gitlib
    import w2_81_questions as questions

    built = build.build_all(tmp_path / "run", s.SEED, s.LARGE, variants=s.variants())
    assert {name: sorted(kinds) for name, kinds in s.hidden_kinds(built).items() if kinds} == {
        name: sorted(kinds) for name, kinds in s.PLAN.items()}
    for name, data in s.question_sets().items():
        repo = built[name]
        asked = questions.resolve(data, repo.manifest, repo.root, "hidden")
        assert len(asked) == 10 and all(s.WORD in q.question and s.WORD in q.gold_answer for q in asked)
        for q in asked:
            for path in q.forbidden:
                assert gitlib.blob(repo.root, repo.manifest["head"], path) is not None, f"{q.id}: a forbidden file"
