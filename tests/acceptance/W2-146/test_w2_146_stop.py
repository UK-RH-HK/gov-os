"""KPI S3, S4 and failures 1, 2 (the stop, end to end): ``gov retrieve`` on a planted store whose path map declares id
forms, asked a question that names an id of a declared form that exists nowhere, stops with ``UNRESOLVED_IDS``, that id
a gap ``UNRESOLVED``, no evidence and no continuation; the same id present as a whole token on one line of an indexed
file is retrieved as before (DEC-1071 (5), DEC-1099 (2), DEC-900).

Interfaces 4 and 5: ``_nowhere`` reads the root's forms once and uses them for the question and for ``--id``; the refusal's
shape is the existing one (exit 0); a malformed form makes ``gov retrieve`` exit 1 with ``CONFIG_INVALID``. Nothing
about ranking or indexing moves, and a repository with no form declared stops exactly as today (S4).

Planted stores (``w2_146_support``): the lexical index and the record store are built by a child process, no embedding;
the semantic route is down (a dead endpoint, an empty HOME), which the stop and the lexical route do not need.
"""

from __future__ import annotations

import pytest

import w2_146_support as support

pytestmark = pytest.mark.skipif(not (support.HAS_GIT and support.HAS_GITLEAKS), reason="git and gitleaks are needed")

NAMES = support.FORM_NAMES
HARBOUR = "What does the harbour decide?"
BUILT_IN_MISSING = "DEC-9999"


@pytest.fixture(scope="module")
def absent(tmp_path_factory):
    """Forms declared; no line holds any of the planted ids (a line holds the built-in QX-4471 and SPEC-4)."""
    return support.plant(tmp_path_factory.mktemp("w2-146-absent"), support.ABSENT_FILES, id_forms=support.declared())


@pytest.fixture(scope="module")
def present(tmp_path_factory):
    """Forms declared; each planted id is a whole token on one line of ``notes/declared.md``."""
    return support.plant(tmp_path_factory.mktemp("w2-146-present"), support.PRESENT_FILES,
                         id_forms=support.declared())


@pytest.fixture(scope="module")
def undeclared(tmp_path_factory):
    """No form declared (no ``id_forms`` key); the same files as ``absent``."""
    return support.plant(tmp_path_factory.mktemp("w2-146-undeclared"), support.ABSENT_FILES)


@pytest.fixture(scope="module")
def undeclared_present(tmp_path_factory):
    """No form declared; the same files as ``present``."""
    return support.plant(tmp_path_factory.mktemp("w2-146-undeclared-present"), support.PRESENT_FILES)


def stated_gap(bundle, ids, where):
    assert bundle["stopping_reason"] == support.UNRESOLVED_IDS, \
        f"{where}: stops with {bundle['stopping_reason']}, not UNRESOLVED_IDS; evidence: {len(bundle['evidence'])} items"
    assert bundle["evidence"] == [], f"{where}: unrelated evidence is offered: " \
                                     f"{[item.get('path') for item in bundle['evidence']][:10]}"
    assert bundle["gaps"] == [{"id": name, "reason": support.UNRESOLVED} for name in ids], \
        f"{where}: the gaps are {bundle['gaps']!r}, not {ids!r}"
    assert bundle["continuation"] is None, f"{where}: a continuation is carried"


def retrieved(run, name, where, given=False):
    """The id exists: nothing stops and UNRESOLVED_IDS is never printed; a question's id is no gap (an id given with
    ``--id`` is named by the closure as before, whatever the reader reads, so ``given`` skips that check)."""
    bundle = run.result()
    assert bundle["stopping_reason"] != support.UNRESOLVED_IDS, f"{where}: an existing id stopped the request"
    assert support.UNRESOLVED_IDS not in run.stdout, f"{where}: UNRESOLVED_IDS is printed\n{run.describe()}"
    if not given:
        assert name not in support.gap_ids(bundle), f"{where}: the existing id {name!r} is a gap: {bundle['gaps']!r}"
    return bundle


# ---- premises -------------------------------------------------------------------------------------------------------

def test_s3_premise_no_planted_line_of_the_absent_store_holds_a_planted_id():
    for name in NAMES:
        for token in (support.FORMS[name]["missing"], support.FORMS[name]["other"]):
            assert not any(token in text for text in support.ABSENT_FILES.values()), token
    assert not any(support.FRAGMENT_QUESTION_ID in text for text in support.ABSENT_FILES.values())
    assert any(support.FRAGMENT_HELD in text for text in support.ABSENT_FILES.values())


def test_s3_premise_the_declared_ids_are_the_forms_and_the_built_in_shape_does_not_read_them():
    from gov.retrieval import lexical

    for name in NAMES:
        token = support.FORMS[name]["missing"]
        assert token not in lexical.ids_in(f"What does {token} decide?"), name


# ---- S3 / failure 1: a nonexistent id of a declared form stops ------------------------------------------------------

@pytest.mark.parametrize("name", NAMES)
def test_s3_failure1_a_nonexistent_declared_id_asked_alone_is_the_stated_gap(absent, name):
    token = support.MISSING[name]
    stated_gap(absent.retrieve(token).result(), [token], f"{token!r} alone")


@pytest.mark.parametrize("name", NAMES)
def test_s3_failure1_a_question_naming_a_nonexistent_declared_id_is_the_stated_gap(absent, name):
    token = support.MISSING[name]
    stated_gap(absent.retrieve(f"What does {token} decide?").result(), [token], f"a question naming {token!r}")


@pytest.mark.parametrize("name", NAMES)
def test_s3_failure1_a_nonexistent_declared_id_given_with_id_is_the_stated_gap(absent, name):
    """Interface 4: ``--id <declared-form id>`` passes the id check (``ids_in(name, forms) == [name]``) and stops."""
    token = support.MISSING[name]
    stated_gap(absent.retrieve(HARBOUR, "--id", token).result(), [token], f"--id {token!r}")


def test_s3_failure1_two_nonexistent_declared_ids_of_one_form_are_two_gaps(absent):
    first, second = support.FORMS["lowercase"]["missing"], support.FORMS["lowercase"]["other"]
    stated_gap(absent.retrieve(f"Compare {first} with {second}").result(), [first, second], "two lowercase ids")


def test_s3_failure1_nonexistent_ids_of_every_form_and_the_built_in_shape_are_all_gaps_in_order(absent):
    tokens = [support.MISSING[name] for name in NAMES]
    question = f"Compare {', '.join(tokens)} with {BUILT_IN_MISSING}"
    stated_gap(absent.retrieve(question).result(), [*tokens, BUILT_IN_MISSING], "every form and a built-in id")


def test_s3_failure1_a_declared_id_and_a_nonexistent_built_in_id_are_both_gaps(absent):
    token = support.MISSING["no-hyphen"]
    stated_gap(absent.retrieve(f"What do {BUILT_IN_MISSING} and {token} decide?").result(), [BUILT_IN_MISSING, token],
               "a built-in id and a declared one")


def test_s3_failure1_a_dotted_id_whose_fragment_exists_is_the_stated_gap_for_the_whole_id_alone(absent):
    """Interface 3's overlap: ``SPEC-4`` is held whole by a line, ``SPEC-4.2`` by none; read whole, the request names
    only ``SPEC-4.2`` and stops: a fragment must not stop the refusal."""
    token = support.FRAGMENT_QUESTION_ID
    stated_gap(absent.retrieve(f"What does {token} decide?").result(), [token], f"{token!r}, its fragment held")
    stated_gap(absent.retrieve(HARBOUR, "--id", token).result(), [token], f"--id {token!r}, its fragment held")


# ---- S3 / failure 2: the same id present as a whole token on a line is retrieved -----------------------------------

@pytest.mark.parametrize("name", NAMES)
def test_s3_failure2_a_declared_id_present_on_a_line_is_retrieved_not_stopped(present, name):
    token = support.MISSING[name]
    retrieved(present.retrieve(f"What does {token} decide?"), token, f"a question naming {token!r}")


@pytest.mark.parametrize("name", NAMES)
def test_s3_failure2_a_declared_id_present_on_a_line_asked_alone_is_retrieved_not_stopped(present, name):
    token = support.MISSING[name]
    retrieved(present.retrieve(token), token, f"{token!r} alone")


@pytest.mark.parametrize("name", NAMES)
def test_s3_failure2_a_declared_id_present_given_with_id_is_retrieved_not_stopped(present, name):
    token = support.MISSING[name]
    retrieved(present.retrieve(HARBOUR, "--id", token), token, f"--id {token!r}", given=True)


@pytest.mark.parametrize("name", NAMES)
def test_s3_failure2_the_present_id_asked_alone_cites_the_file_that_holds_it(present, name):
    token = support.MISSING[name]
    bundle = present.retrieve(token).result()
    assert support.PRESENT_FILE in [item["path"] for item in bundle["evidence"]], \
        f"{token!r}: the file that holds it is not cited: {[item['path'] for item in bundle['evidence']]}"


# ---- S3: the "every" rule stays -------------------------------------------------------------------------------------

def test_s3_every_rule_a_nonexistent_declared_id_beside_an_existing_built_in_id_is_retrieved(absent):
    token = support.MISSING["underscore"]
    bundle = absent.retrieve(f"What do {support.BUILT_IN_EXISTING} and {token} say?").result()
    assert bundle["stopping_reason"] != support.UNRESOLVED_IDS and support.UNRESOLVED_IDS not in str(bundle)


def test_s3_every_rule_a_nonexistent_declared_id_beside_an_existing_declared_id_is_retrieved(present):
    held, missing = support.FORMS["lowercase"]["missing"], support.FORMS["lowercase"]["other"]
    run = present.retrieve(f"What do {held} and {missing} say?")
    bundle = run.result()
    assert bundle["stopping_reason"] != support.UNRESOLVED_IDS, run.describe()
    assert support.UNRESOLVED_IDS not in run.stdout
    assert held not in support.gap_ids(bundle)


def test_s3_every_rule_two_declared_ids_of_two_forms_one_present_and_one_not_is_retrieved(present):
    held, missing = support.FORMS["spaced"]["missing"], support.FORMS["no-hyphen"]["other"]
    bundle = present.retrieve(f"What do {held} and {missing} say?").result()
    assert bundle["stopping_reason"] != support.UNRESOLVED_IDS


def test_s3_every_rule_an_id_of_a_declared_form_the_question_holds_inside_a_longer_word_is_no_id(absent):
    """The whole-token rule at the stop: ``xreq12`` is no declared id, so no id is named and nothing stops."""
    bundle = absent.retrieve("What does xreq12 decide about the harbour?").result()
    assert bundle["stopping_reason"] != support.UNRESOLVED_IDS and bundle["gaps"] == []


# ---- Interface 5: a malformed form is loud, before any search ---------------------------------------------------------

BAD_FORMS = {
    "a pattern that does not compile": {"name": "broken", "pattern": "("},
    "an entry with no pattern": {"name": "request"},
    "an entry with no name": {"pattern": "req[0-9]+"},
}


@pytest.fixture(scope="module")
def spoiled(tmp_path_factory):
    """A planted, indexed store whose path map (rewritten after the build, working tree only) later gets a bad form."""
    return support.plant(tmp_path_factory.mktemp("w2-146-spoiled"), support.ABSENT_FILES, id_forms=support.declared())


@pytest.mark.parametrize("which", list(BAD_FORMS))
@pytest.mark.parametrize("question", [f"What does {support.MISSING['lowercase']} decide?",
                                      f"What does {BUILT_IN_MISSING} decide?"],
                         ids=["a declared-form id", "a built-in id"])
def test_s1_failure3_a_malformed_form_in_the_path_map_makes_retrieve_fail_with_config_invalid(spoiled, which, question):
    import yaml

    good = {"name": "request", "pattern": "req[0-9]+"}
    support.write(spoiled.root, support.PATH_MAP_REL,
                  yaml.safe_dump(support.valid_path_map(id_forms=[good, BAD_FORMS[which]]), sort_keys=False))
    run = spoiled.retrieve(question)
    assert "Traceback (most recent call last)" not in run.stdout + run.stderr, run.describe()
    assert run.returncode == 1, f"a malformed form did not make the command fail\n{run.describe()}"
    envelope = run.envelope()
    assert envelope.get("ok") is False and envelope["error"]["code"] == "CONFIG_INVALID", run.describe()
    assert "id_forms" in envelope["error"]["message"], run.describe()
    assert support.UNRESOLVED_IDS not in run.stdout, "the request was searched and refused before the form was read"


# ---- S4: nothing else moves -------------------------------------------------------------------------------------------

def test_s4_with_no_form_declared_a_nonexistent_built_in_id_stops_as_today(undeclared):
    stated_gap(undeclared.retrieve(BUILT_IN_MISSING).result(), [BUILT_IN_MISSING], "a built-in id, no form declared")
    stated_gap(undeclared.retrieve(f"What does {BUILT_IN_MISSING} decide?").result(), [BUILT_IN_MISSING],
               "a question naming a built-in id, no form declared")
    stated_gap(undeclared.retrieve(HARBOUR, "--id", BUILT_IN_MISSING).result(), [BUILT_IN_MISSING],
               "--id of a built-in id, no form declared")


def test_s4_with_no_form_declared_an_existing_built_in_id_is_retrieved(undeclared):
    retrieved(undeclared.retrieve(f"What does {support.BUILT_IN_EXISTING} decide?"), support.BUILT_IN_EXISTING,
              "an existing built-in id, no form declared")


@pytest.mark.parametrize("name", [name for name in NAMES if name != "dotted"])
def test_s4_with_no_form_declared_a_declared_form_like_token_does_not_stop_the_request(undeclared, name):
    token = support.MISSING[name]
    run = undeclared.retrieve(f"What does {token} decide?")
    bundle = run.result()
    assert bundle["stopping_reason"] != support.UNRESOLVED_IDS and support.UNRESOLVED_IDS not in run.stdout, \
        f"{token!r} stopped the request though no form is declared\n{run.describe()}"
    assert bundle["gaps"] == [] or token not in support.gap_ids(bundle)


def test_s4_with_no_form_declared_a_dotted_token_stops_on_its_built_in_fragment_as_today(undeclared):
    token = support.MISSING["dotted"]
    fragment = token.split(".")[0]
    stated_gap(undeclared.retrieve(f"What does {token} decide?").result(), [fragment], f"{token!r}, no form declared")


@pytest.mark.parametrize("name", NAMES)
def test_s4_a_declared_form_moves_nothing_but_the_reader_for_an_id_that_exists(present, undeclared_present, name):
    """The same files and the same question, with and without the declaration: the same evidence, in the same order,
    the same gaps and reason (ranking, closure and indexing are not the reader's)."""
    token = support.MISSING[name]

    def projection(repo):
        bundle = repo.retrieve(f"What does {token} decide?").result()
        keys = ("path", "start_line", "end_line", "sha256", "routes")
        # the path map itself differs (it holds the declared patterns), so it is no part of the comparison
        return (bundle["stopping_reason"], [{key: item[key] for key in keys} for item in bundle["evidence"]
                                            if item["path"] != support.PATH_MAP_REL],
                bundle["gaps"], [entry for entry in bundle["expansions"] if entry["path"] != support.PATH_MAP_REL],
                bundle["continuation"])

    assert projection(present) == projection(undeclared_present)
