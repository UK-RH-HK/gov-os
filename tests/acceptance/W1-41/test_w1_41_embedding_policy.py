"""The embedding policies of an adopted project's path map (DEC-694, DEC-700; DEC-686, DEC-693).

A namespace of the path map carries ``embedding_policy``. Only a file whose every namespace says exactly
``embedded`` reaches the semantic vectors; anything else is read as "not embedded" (DEC-380, DEC-381, DEC-388).
An adoption could end with no namespace embedded, and nothing said why the semantic index stayed empty. This round:

1. the kernel's adopt skill names the two values, ``embedded`` and ``not embedded``, what each means, and that
   every namespace states one;
2. stage A3 refuses a path map with a namespace whose value is another one, or that has no value (DEC-700), or in
   which no namespace says ``embedded``; a path map whose namespaces each state one of the two, one or more of them
   ``embedded``, goes on, and so does a project that commits a corrected path map after the refusal;
3. ``gov rebuild`` and ``gov doctor`` say ``no namespace is embedded`` where no namespace says exactly ``embedded``,
   and add no failure for it.

Outside adoption nothing is refused for it (DEC-380, DEC-388 stay): W1-19's cases hold that, named in the README.

Every project is the harbour project of ``w1_41_support``, written file by file in the case's temporary folder.
No model is loaded: the embedding endpoint is a loopback address where nothing listens, and its program a path
where none is (``support.environment``). The interface the cases hold is the README's ("The embedding policies").
"""

from __future__ import annotations

import json
import re

import pytest
import yaml

import w1_41_support as support

EMBEDDED, NOT_EMBEDDED, ABSENT = support.EMBEDDED, support.NOT_EMBEDDED, support.ABSENT
WORDS = support.NO_NAMESPACE_EMBEDDED
FREE_TEXT = "not stated by the programme"         # what a-dev's adoption wrote (DEC-693)
ADOPT_FAMILY = "ADOPT_"                            # the code of every refusal of gov adopt --lite today
SKILL_REL = "template/governance/kernel/skills/adopt/SKILL.md"

# The harbour project split in namespaces: the papers (documents, notes, records), the old memory, the rest.
PAPERS = ("docs/**", "notes/**", "spec/**")
ATTIC = ("legacy/**",)
REST = tuple(pattern for pattern in support.NAMESPACE_PATHS if pattern not in PAPERS + ATTIC)


def spaces(papers, harbour=EMBEDDED, attic=None):
    """name -> (patterns, embedding_policy). Without ``attic`` the old memory is in ``harbour``."""
    made = {"papers": (PAPERS, papers)}
    if attic is None:
        made["harbour"] = (REST + ATTIC, harbour)
    else:
        made["harbour"] = (REST, harbour)
        made["attic"] = (ATTIC, attic)
    return made


def keep_everything():
    """A proposal that moves and retires nothing, so no case needs the code graph."""
    return [support.entry("README.md", "KEEP")]


def quoted(value, text):
    """Whether ``text`` names ``value`` as a value: between quotes or backticks."""
    marks = "`'\"‘’“”"
    return re.search(f"[{marks}]{re.escape(value)}[{marks}]", text) is not None


def state_of(project):
    return (support.snapshot(project, skip=(".git", ".gov-runtime")), support.git_state(project),
            support.tree(project))


def assert_wrote_nothing(project, before, run, what="the refusal"):
    snapshot, git_state, tree = before
    changed = support.snapshot_difference(snapshot, support.snapshot(project, skip=(".git", ".gov-runtime")))
    assert not changed, f"{what} wrote in the project: {changed}\n{run.describe()}"
    assert support.git_state(project) == git_state, f"{what} committed or wrote a ref\n{run.describe()}"
    assert support.tree(project) == tree, f"{what} changed the tracked files\n{run.describe()}"
    assert support.porcelain(project) == "", f"{what} left the tree dirty\n{run.describe()}"


def refused_at_a3(adoption, interface, at_fault=(), none_embedded=False):
    """A0 to A2 go on; A3 is refused by a refusal of its own family, writes nothing, and its message names each
    namespace at fault and both valid values (and, where no namespace is embedded, says so)."""
    adoption.through("A2")
    before = state_of(adoption.project)
    run = adoption.run("A3", *adoption.map_argument(keep_everything()))
    error = support.assert_refused(run, interface)
    code = str(error.get("code") or "")
    assert code.startswith(ADOPT_FAMILY), \
        f"the refusal's code {code!r} is not of stage A3's own family ({ADOPT_FAMILY}…)\n{run.describe()}"
    message = error.get("message")
    assert isinstance(message, str) and message, f"the refusal has no message\n{run.describe()}"
    for name in at_fault:
        assert name in message, f"the message does not name the namespace at fault {name!r}\n{run.describe()}"
    for value in (EMBEDDED, NOT_EMBEDDED):
        assert quoted(value, message), \
            f"the message does not name the valid value {value!r} (between quotes or backticks)\n{run.describe()}"
    if none_embedded:
        assert WORDS in message.lower(), f"the message does not say {WORDS!r}\n{run.describe()}"
    assert_wrote_nothing(adoption.project, before, run, "the refused A3")
    return run


# --------------------------------------------------------------------------
# 1. The kernel's adopt skill names the two values
# --------------------------------------------------------------------------

def _skill():
    return (support.REPO_ROOT / SKILL_REL).read_text(encoding="utf-8")


def test_the_adopt_skill_names_the_two_valid_embedding_policies():
    text = _skill()
    assert "embedding_policy" in text, f"{SKILL_REL} does not name the field embedding_policy"
    for value in (EMBEDDED, NOT_EMBEDDED):
        assert quoted(value, text), f"{SKILL_REL} does not name the value {value!r} (between quotes or backticks)"


def test_the_adopt_skill_says_what_embedded_means():
    """``embedded``: the namespace's files reach the semantic vectors; ``not embedded``: they do not."""
    text = _skill().lower()
    assert "embedding_policy" in text and ("semantic" in text or "vector" in text), \
        f"{SKILL_REL} does not say what the policy decides: whether a namespace reaches the semantic vectors"


def test_the_adopt_skill_says_every_namespace_states_one():
    text = _skill().lower()
    assert "embedding_policy" in text and ("every namespace" in text or "each namespace" in text), \
        f"{SKILL_REL} does not say that every namespace states its embedding policy"


# --------------------------------------------------------------------------
# 2. Stage A3 refuses another value, no value, or no namespace embedded
# --------------------------------------------------------------------------

@pytest.mark.parametrize("value", [FREE_TEXT, "Embedded", "embedded ", "not_embedded"],
                         ids=["free-text", "capital-E", "trailing-space", "underscore"])
def test_a_namespace_with_another_value_is_refused_at_a3(tmp_path, adopt_in, interface, value):
    """The other namespace says ``embedded``: the refusal is for the value alone."""
    adoption = adopt_in(support.build_project(tmp_path / "harbour", namespaces=spaces(value)))
    refused_at_a3(adoption, interface, at_fault=("papers",))


def test_a_namespace_without_the_field_is_refused_at_a3(tmp_path, adopt_in, interface):
    """DEC-700: at adoption a namespace without ``embedding_policy`` counts as another value."""
    adoption = adopt_in(support.build_project(tmp_path / "harbour", namespaces=spaces(ABSENT)))
    refused_at_a3(adoption, interface, at_fault=("papers",))


def test_two_namespaces_at_fault_are_both_named(tmp_path, adopt_in, interface):
    adoption = adopt_in(support.build_project(tmp_path / "harbour",
                                              namespaces=spaces(FREE_TEXT, EMBEDDED, attic=ABSENT)))
    refused_at_a3(adoption, interface, at_fault=("papers", "attic"))


@pytest.mark.parametrize("namespaces", [
    spaces(NOT_EMBEDDED, NOT_EMBEDDED),
    None,                                        # the harbour project's one namespace, as it was before DEC-694
], ids=["two-namespaces", "one-namespace"])
def test_a_path_map_where_every_namespace_says_not_embedded_is_refused_at_a3(tmp_path, adopt_in, interface,
                                                                           namespaces):
    if namespaces is None:
        namespaces = {"harbour": (support.NAMESPACE_PATHS, NOT_EMBEDDED)}
    adoption = adopt_in(support.build_project(tmp_path / "harbour", namespaces=namespaces))
    refused_at_a3(adoption, interface, none_embedded=True)


@pytest.mark.parametrize("value", [True, None, ""], ids=["yaml-boolean", "empty-value", "empty-text"])
def test_a_value_that_is_no_text_is_refused_before_a3_goes_on(tmp_path, adopt_in, interface, value):
    """A value that is no text is another value too. The project's configuration refuses it for every command
    today (README, "The embedding policies"): held is that adoption is refused at A3 or a stage before it, writes
    nothing, and names the namespace; whichever stage refuses, A3 never records such a path map."""
    project = support.build_project(tmp_path / "harbour", namespaces=spaces(value))
    adoption = adopt_in(project)
    for stage in ("A0", "A1", "A2", "A3"):
        before = state_of(project)
        extra = adoption.map_argument(keep_everything()) if stage == "A3" else ()
        run = adoption.run(stage, *extra)
        envelope = json.loads(run.stdout) if run.stdout.strip().startswith("{") else {}
        if envelope.get("ok") is True and stage != "A3":
            assert support.porcelain(project) == "", f"stage {stage} left the tree dirty\n{run.describe()}"
            continue
        support.assert_refused(run, interface, "papers")
        assert_wrote_nothing(project, before, run, f"the refused stage {stage}")
        return
    raise AssertionError("stage A3 recorded a path map whose namespace 'papers' has no text as its embedding policy")


# --------------------------------------------------------------------------
# 2. ... and goes on where every namespace states one of the two, one or more of them embedded
# --------------------------------------------------------------------------

@pytest.mark.parametrize("namespaces", [
    spaces(EMBEDDED, NOT_EMBEDDED),
    spaces(NOT_EMBEDDED, EMBEDDED, attic=NOT_EMBEDDED),
    spaces(EMBEDDED, EMBEDDED),
], ids=["papers-embedded", "harbour-embedded-two-not", "all-embedded"])
def test_a_path_map_whose_namespaces_each_state_a_valid_value_goes_on(tmp_path, adopt_in, namespaces):
    adoption = adopt_in(support.build_project(tmp_path / "harbour", namespaces=namespaces))
    adoption.through("A4", keep_everything())


def test_a_corrected_path_map_committed_after_the_refusal_goes_on(tmp_path, adopt_in, interface):
    project = support.build_project(tmp_path / "harbour", namespaces=spaces(FREE_TEXT))
    adoption = adopt_in(project)
    refused_at_a3(adoption, interface, at_fault=("papers",))
    support.write(project, support.PATH_MAP_REL,
                  yaml.safe_dump(support.path_map(namespaces=spaces(EMBEDDED, NOT_EMBEDDED)), sort_keys=False))
    support.commit(project, "the path map states every namespace's embedding policy")
    adoption.ok("A3", *adoption.map_argument(keep_everything()))
    adoption.ok("A4")


# --------------------------------------------------------------------------
# 3. gov rebuild and gov doctor say "no namespace is embedded"
# --------------------------------------------------------------------------

NONE_EMBEDDED = {
    "every-namespace-not-embedded": spaces(NOT_EMBEDDED, NOT_EMBEDDED),
    "another-value": spaces(FREE_TEXT, NOT_EMBEDDED),
    "no-field": spaces(ABSENT, ABSENT),
    "near-spelling": spaces("Embedded", NOT_EMBEDDED),
}
ONE_EMBEDDED = {
    "beside-not-embedded": spaces(EMBEDDED, NOT_EMBEDDED),
    "beside-another-value": spaces(EMBEDDED, FREE_TEXT),
}
FULL, WITHOUT_EMBEDDINGS = (), ("--no-embeddings",)
MODES = {"full": FULL, "no-embeddings": WITHOUT_EMBEDDINGS}


def semantic_parts(value):
    """Every value under a key ``semantic``, at any depth: the semantic part of an answer."""
    found = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "semantic":
                found.append(item)
            found += semantic_parts(item)
    elif isinstance(value, list):
        for item in value:
            found += semantic_parts(item)
    return found


def says_it(value):
    return WORDS in json.dumps(semantic_parts(value)).lower()


def envelope_of(run, interface, command):
    return support.base.assert_envelope(run, interface, command=command)


def rebuild(project, sandbox, interface, mode):
    run = support.run_gov(project, sandbox, "rebuild", *mode, "--json")
    return run, envelope_of(run, interface, "rebuild")


def doctor(project, sandbox, interface):
    """``gov doctor --json`` after a rebuild without embeddings; its sections from the result or the error."""
    rebuild(project, sandbox, interface, WITHOUT_EMBEDDINGS)
    run = support.run_gov(project, sandbox, "doctor", "--json")
    envelope = envelope_of(run, interface, "doctor")
    answer = envelope.get("result") if envelope.get("ok") else (envelope.get("error") or {}).get("details")
    assert isinstance(answer, dict), f"gov doctor gives no sections\n{run.describe()}"
    return run, envelope, answer


def statuses(answer):
    return {name: section.get("status") for name, section in answer.items()
            if isinstance(section, dict) and "status" in section}


def canary_semantic(answer):
    section = ((answer.get("canaries") or {}).get("indices") or {}).get("semantic") or {}
    return {key: section.get(key) for key in ("passed", "status", "misses")}


def stores(envelope):
    return {name: (store or {}).get("status")
            for name, store in ((envelope.get("result") or {}).get("stores") or {}).items()}


def built(tmp_path, name, namespaces):
    return support.build_project(tmp_path / name / "harbour", namespaces=namespaces)


@pytest.fixture(scope="module")
def reference(tmp_path_factory, interface):
    """The same project with one namespace that says ``embedded`` (no vectors either way): its rebuilds and its
    doctor, to compare with."""
    base = tmp_path_factory.mktemp("w1-41-embedded-reference")
    project = built(base, "reference", ONE_EMBEDDED["beside-not-embedded"])
    sandbox = support.make_sandbox(base / "sandbox")
    answers = {mode: rebuild(project, sandbox, interface, args) for mode, args in MODES.items()}
    answers["doctor"] = doctor(project, sandbox, interface)
    return answers


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("map_name", NONE_EMBEDDED)
def test_the_rebuild_says_no_namespace_is_embedded(tmp_path, sandbox, interface, reference, map_name, mode):
    """The stores are recreated as for the project with one embedded namespace, with the same exit code and the
    same outcome for every store; the answer for the semantic store carries the words."""
    project = built(tmp_path, map_name, NONE_EMBEDDED[map_name])
    run, envelope = rebuild(project, sandbox, interface, MODES[mode])
    ref_run, ref_envelope = reference[mode]
    assert envelope["ok"] is True and run.returncode == 0, f"the rebuild did not succeed\n{run.describe()}"
    assert (run.returncode, envelope["ok"]) == (ref_run.returncode, ref_envelope["ok"]), \
        f"the exit code differs from the project with one embedded namespace\n{run.describe()}"
    assert stores(envelope).get("lexical") == "recreated", f"the lexical index is not recreated\n{run.describe()}"
    assert stores(envelope) == stores(ref_envelope), \
        f"the stores' outcomes differ from the project with one embedded namespace " \
        f"({stores(ref_envelope)})\n{run.describe()}"
    assert says_it(envelope.get("result")), \
        f"the rebuild's answer for the semantic store does not say {WORDS!r}\n{run.describe()}"


@pytest.mark.parametrize("map_name", NONE_EMBEDDED)
def test_the_doctor_says_no_namespace_is_embedded_and_adds_no_failure(tmp_path, sandbox, interface, reference,
                                                                     map_name):
    """Held against the same project with one embedded namespace: the same exit code, the same verdict and the same
    status in every section; the canary's answer for the semantic index as the canary gives it; only the words
    differ."""
    project = built(tmp_path, map_name, NONE_EMBEDDED[map_name])
    run, envelope, answer = doctor(project, sandbox, interface)
    ref_run, ref_envelope, ref_answer = reference["doctor"]
    assert says_it(answer), f"the doctor's semantic part does not say {WORDS!r}\n{run.describe()}"
    assert (run.returncode, envelope["ok"], answer.get("healthy")) == \
        (ref_run.returncode, ref_envelope["ok"], ref_answer.get("healthy")), \
        f"the doctor's verdict differs from the project with one embedded namespace\n{run.describe()}\n" \
        f"with one embedded namespace:\n{ref_run.describe()}"
    assert statuses(answer) == statuses(ref_answer), \
        f"the sections' statuses differ: {statuses(answer)} against {statuses(ref_answer)}\n{run.describe()}"
    assert canary_semantic(answer) == canary_semantic(ref_answer), \
        f"the canary's answer for the semantic index changed: {canary_semantic(answer)} against " \
        f"{canary_semantic(ref_answer)}\n{run.describe()}"


@pytest.mark.parametrize("command", ["rebuild-full", "rebuild-no-embeddings", "doctor"])
@pytest.mark.parametrize("map_name", ONE_EMBEDDED)
def test_neither_says_it_where_a_namespace_is_embedded(tmp_path, sandbox, interface, map_name, command):
    project = built(tmp_path, map_name, ONE_EMBEDDED[map_name])
    if command == "doctor":
        run = doctor(project, sandbox, interface)[0]
    else:
        run = rebuild(project, sandbox, interface, FULL if command == "rebuild-full" else WITHOUT_EMBEDDINGS)[0]
    assert WORDS not in (run.stdout + run.stderr).lower(), \
        f"gov {command} says {WORDS!r} where a namespace is embedded\n{run.describe()}"
