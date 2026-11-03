"""KPI S6: the keyword index honours the path map (DEC-1066 (3), G4; DEC-1052 M-4).

A namespace whose ``lexical_policy`` is ``not indexed`` keeps its files out of the keyword index (absent: indexed, as
today); the path map's validator accepts the field with its two values; a file kept out is named in the rebuild's
report; the evaluation set's own documents (lens B's report, ``fixtures/evaluation/**``) are what D-7 marks so.

The projects are planted (``w2_13_lexical_policy_support``) and indexed by ``gov rebuild --no-embeddings``: the
keyword route only, no embedder. The semantic endpoint is a dead port, so ``gov retrieve`` answers from the keyword
route. Only the vectors' case builds vectors, through W1-21's stand-in endpoint (no model runs). Every "kept out" case
first shows, on the control project (the same files, no ``lexical_policy`` anywhere), that the same question finds the
file: a red is never a question that could not find it.
"""

from __future__ import annotations

import pytest

import w2_13_lexical_policy_support as s6
import w2_13_roles_support as roles
import w2_13_support as support

pytestmark = pytest.mark.needs("git", "gitleaks")

QUESTION_FORMS = ("its words", "its id")


def ask(planted, form):
    return planted.question if form == "its words" else planted.ident


@pytest.fixture(scope="module")
def planted(box, tmp_path_factory):
    """The planted project, rebuilt: ``(root, report)``."""
    root = s6.build_project(tmp_path_factory.mktemp("w2-13-s6-planted") / "repo")
    return root, s6.rebuild(box, root)


@pytest.fixture(scope="module")
def control(box, tmp_path_factory):
    """The same files with no ``lexical_policy`` anywhere, rebuilt: ``(root, report)``."""
    root = s6.build_project(tmp_path_factory.mktemp("w2-13-s6-control") / "repo", with_policy=False)
    return root, s6.rebuild(box, root)


# --------------------------------------------------------------------------
# not indexed: kept out of the keyword index
# --------------------------------------------------------------------------

@pytest.mark.parametrize("form", QUESTION_FORMS)
@pytest.mark.parametrize("kept_out", s6.KEPT_OUT, ids=lambda planted: planted.path)
def test_a_namespace_not_indexed_keeps_its_files_out_of_the_keyword_index(box, planted, control, kept_out, form):
    question = ask(kept_out, form)
    assert kept_out.path in s6.search_paths(box, control[0], question), \
        f"premise: on the control project the keyword route does not find {kept_out.path} for {question!r}"
    found = s6.search_paths(box, planted[0], question)
    assert kept_out.path not in found, \
        f"{kept_out.path} lies in namespace {kept_out.namespace!r} (lexical_policy: not indexed) and the keyword " \
        f"route found it for {question!r}: {sorted(found)}"


def test_no_term_of_the_keyword_index_spells_a_word_of_a_file_kept_out(box, planted, control, tmp_path):
    (tmp_path / "control").mkdir()
    (tmp_path / "planted").mkdir()
    before = support.vocabulary(control[0], tmp_path / "control")
    after = support.vocabulary(planted[0], tmp_path / "planted")
    assert after, f"premise: the planted project's store holds no FTS5 table ({support.STORE_REL})"
    for planted_file in s6.FILES:
        for word in planted_file.words:
            assert s6.in_vocabulary(word, before), \
                f"premise: no FTS5 term of the control project spells {word!r} ({planted_file.path})"
    for kept_in in s6.KEPT_IN:
        for word in kept_in.words:
            assert s6.in_vocabulary(word, after), \
                f"{kept_in.path} is indexed and no FTS5 term of the planted project spells its word {word!r}"
    spelt = sorted(f"{kept_out.path}: {word}" for kept_out in s6.KEPT_OUT for word in kept_out.words
                   if s6.in_vocabulary(word, after))
    assert not spelt, f"the keyword index holds the words of files whose namespace is not indexed: {spelt}"


@pytest.mark.parametrize("kept_out", s6.KEPT_OUT, ids=lambda planted: planted.path)
def test_gov_retrieve_cites_nothing_of_a_file_kept_out(box, planted, control, kept_out):
    """The semantic endpoint is dead: what ``gov retrieve`` returns comes from the keyword route (and the records)."""
    before = roles.retrieve(box, "env", control[0], kept_out.question)
    assert kept_out.path in roles.evidence_paths(before), \
        f"premise: on the control project gov retrieve does not cite {kept_out.path} for {kept_out.question!r}: " \
        f"{sorted(roles.bundle_paths(before))}"
    bundle = roles.retrieve(box, "env", planted[0], kept_out.question)
    returned = roles.bundle_paths(bundle)
    assert kept_out.path not in returned, \
        f"gov retrieve returned {kept_out.path} (lexical_policy: not indexed) for {kept_out.question!r}: " \
        f"{sorted(returned)}"


# --------------------------------------------------------------------------
# the rebuild's report
# --------------------------------------------------------------------------

def test_the_rebuild_names_each_file_it_kept_out(planted):
    root, report = planted
    text = s6.report_text(root, report)
    missing = [kept_out.path for kept_out in s6.KEPT_OUT if not s6.named(text, kept_out.path)]
    assert not missing, f"the rebuild's report does not name the files it kept out of the keyword index: " \
                        f"{missing}\nreport: {text[-3000:]}"
    listed = [kept_in.path for kept_in in s6.KEPT_IN if s6.named(text, kept_in.path)]
    assert not listed, f"the rebuild's report names files that were indexed, beside those kept out: {listed}"


# --------------------------------------------------------------------------
# absent (or indexed): indexed, as today
# --------------------------------------------------------------------------

@pytest.mark.parametrize("form", QUESTION_FORMS)
@pytest.mark.parametrize("kept_in", [s6.ABSENT_FILE, s6.INDEXED_FILE],
                         ids=["lexical_policy absent", "lexical_policy indexed"])
def test_a_namespace_with_no_lexical_policy_or_indexed_is_indexed_as_today(box, planted, kept_in, form):
    question = ask(kept_in, form)
    found = s6.search_paths(box, planted[0], question)
    assert kept_in.path in found, \
        f"{kept_in.path} lies in namespace {kept_in.namespace!r} " \
        f"(lexical_policy: {s6.NAMESPACES[kept_in.namespace][1] or 'absent'}) and the keyword route does not find " \
        f"it for {question!r}: {sorted(found)}"


def test_with_no_lexical_policy_anywhere_every_file_is_indexed_and_none_named(box, control):
    root, report = control
    unfound = [planted.path for planted in s6.FILES
               for question in (planted.question, planted.ident)
               if planted.path not in s6.search_paths(box, root, question)]
    assert not unfound, f"with no lexical_policy in the path map, the keyword route misses: {unfound}"
    text = s6.report_text(root, report)
    listed = [planted.path for planted in s6.FILES if s6.named(text, planted.path)]
    assert not listed, f"with nothing kept out, the rebuild's report names files as if kept out: {listed}"


# --------------------------------------------------------------------------
# the validator
# --------------------------------------------------------------------------

@pytest.mark.parametrize("value", [s6.INDEXED, s6.NOT_INDEXED])
def test_the_path_map_validator_accepts_both_values(box, tmp_path, value):
    root = s6.build_one_namespace(tmp_path / "repo", value)
    outcome = s6.load_config(box, root)
    error = outcome.error()
    assert error is None, f"the path map's validator refused lexical_policy: {value!r}: {error}"
    entry = outcome.value()["path-map.yaml"]["namespaces"]["everything"]
    assert entry.get(s6.FIELD) == value, f"the loaded path map does not keep lexical_policy: {value!r}: {entry!r}"
    assert s6.pathmap_findings(box, root) == [], "premise: a tracked path is in no namespace, or in two"
    s6.rebuild(box, root)


INVALID = {
    "a word": "skip",
    "hyphenated": "not-indexed",
    "capitals": "Not Indexed",
    "embedding_policy's value": "not embedded",
    "empty": "",
    "a boolean": True,
    "a list": ["not indexed"],
}


@pytest.mark.parametrize("value", list(INVALID.values()), ids=list(INVALID))
def test_the_path_map_validator_refuses_an_invalid_value(box, tmp_path, value):
    root = s6.build_one_namespace(tmp_path / "repo", value)
    error = s6.load_config(box, root).error()
    assert error is not None, f"the path map's validator accepted lexical_policy: {value!r}"
    assert error.get("code") == "CONFIG_INVALID" and s6.FIELD in (error.get("message") or ""), \
        f"the refusal of lexical_policy: {value!r} is not CONFIG_INVALID naming the field: {error}"
    run = box.gov("rebuild", "--json", "--no-embeddings", "--root", str(root))
    envelope = run.envelope()
    assert run.returncode != 0 and envelope.get("ok") is False, \
        f"gov rebuild ran on a path map with lexical_policy: {value!r}\n{run.describe()}"
    assert (envelope.get("error") or {}).get("code") == "CONFIG_INVALID", run.describe()
    assert not (root / support.STORE_REL).exists(), "gov rebuild built a store from a path map it should refuse"


# --------------------------------------------------------------------------
# the vectors keep their embedding_policy
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def planted_vectors(box, ollama, tmp_path_factory):
    """The planted project rebuilt with its vectors, through the stand-in endpoint (no model runs)."""
    if support.lacking("sqlite_vec"):
        pytest.skip("; ".join(support.lacking("sqlite_vec")))
    root = s6.build_project(tmp_path_factory.mktemp("w2-13-s6-vectors") / "repo")
    result = box.rebuild(root, host=ollama.host)
    assert result["stores"].get("semantic", {}).get("status") == "recreated", \
        f"premise: the vectors were not built through the stand-in endpoint: {result['stores']!r}"
    return root


VECTOR_CASES = {
    "not indexed, embedded: in the vectors only": (s6.VECTORS_ONLY_FILE, {support.ROUTE_SEMANTIC}),
    "indexed, not embedded: in the keyword index only": (s6.INDEXED_FILE, {support.ROUTE_LEXICAL}),
    "not indexed, not embedded: in neither": (s6.EVALUATION_FILE, set()),
}


@pytest.mark.needs("sqlite_vec")
@pytest.mark.parametrize("case", list(VECTOR_CASES), ids=list(VECTOR_CASES))
def test_the_vectors_keep_their_embedding_policy(box, ollama, planted_vectors, case):
    planted_file, expected = VECTOR_CASES[case]
    answer, routes = s6.fused(box, planted_vectors, planted_file.question, box.scratch_env(ollama.host))
    facets = answer.get("facets", {})
    for route in (support.ROUTE_LEXICAL, support.ROUTE_SEMANTIC):
        assert facets.get(route, {}).get("available") is True, f"premise: the {route} route is not available: {facets!r}"
    got = routes.get(planted_file.path, set()) & {support.ROUTE_LEXICAL, support.ROUTE_SEMANTIC}
    assert got == expected, \
        f"{planted_file.path} ({case}) came back by the routes {sorted(got)}, not {sorted(expected)}, for " \
        f"{planted_file.question!r}"


# --------------------------------------------------------------------------
# the repository: D-7 marks the evaluation set's own documents
# --------------------------------------------------------------------------

@pytest.mark.parametrize("prefix", [s6.LENS_B_REPORT, s6.EVALUATION_FIXTURES],
                         ids=["lens B's report", "the evaluation fixtures"])
def test_the_repository_marks_the_evaluation_sets_own_documents_not_indexed(prefix):
    """This repository's own path map (the run's root): each tracked file lies in exactly one namespace, and that
    namespace says ``lexical_policy: not indexed`` (DEC-1066 (3), D-7)."""
    namespaces = s6.repository_namespaces()
    files = s6.tracked(prefix)
    assert files, f"premise: no tracked file under {prefix}"
    wrong = {}
    for path in files:
        names = s6.holders(namespaces, path)
        if len(names) != 1:
            wrong[path] = f"in {len(names)} namespaces: {names}"
        elif namespaces[names[0]].get(s6.FIELD) != s6.NOT_INDEXED:
            wrong[path] = f"namespace {names[0]!r} says lexical_policy: {namespaces[names[0]].get(s6.FIELD)!r}"
    assert not wrong, f"{len(wrong)} of {len(files)} files under {prefix} are not marked not indexed: " \
                      f"{dict(list(wrong.items())[:5])}"
