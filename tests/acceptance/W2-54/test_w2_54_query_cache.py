"""KPI success 3 (round 3): the query-vector cache is the one file a read command writes: a derived file under
.gov-runtime/, keyed by model, model revision and a hash of the exact text, written atomically and safely by several
sessions at once, bounded in size, and rebuildable from nothing [owner, 2026-10-18, P-W2-32 (a)].

And the determinism of success 4 seen outside the sandbox: where the cache cannot be written, the same text still
gets the same vector. A cold, a warm, a full, a deleted and an unwritable cache all give one text one answer.

Seen from outside, through public interfaces only: ``gov retrieve --json``, ``gov context --json``,
``gov.retrieval.semantic.search(root, q, refresh=False)``, the project's file tree before and after, and the public
setting that lowers the bound (README, "The bound"). No case names the cache file, its form or the code that writes
it: the cache is "the one file under .gov-runtime/ a read wrote that is not the store".

The embedder is round 2's stand-in (README, "The stand-in embedder"): a text embedded right after a different text
gets another vector, a repeat gets its own. A read whose answer depends on what was embedded before it, or on
whether the cache could be written, gives one text two answers here.
"""

from __future__ import annotations

import random

import pytest

import w2_54_support as S

LACKING = ([] if S.shutil.which("gitleaks") else ["gitleaks is not on PATH: the fixture's index cannot be built"]) + (
    [] if S.importlib.util.find_spec("sqlite_vec") else ["sqlite_vec cannot be imported: no vector can be stored"])
STAND_IN = pytest.mark.skipif(bool(LACKING), reason="; ".join(LACKING) or "none")

QUESTION = "who fires the glazed bowls"
TICKET = "TK-W254-TIDES"


def _available(answer, what):
    assert answer.get("available") is True and S.hits_of(answer), f"{what}: the semantic facet gave no answer: {answer}"


def _same(answer, reference, what):
    _available(answer, what)
    assert S.hits_of(answer) == S.hits_of(reference), (
        f"{what}: one text, two answers\nfirst in a new store: {S.hits_of(reference)[:3]}\n"
        f"here:                 {S.hits_of(answer)[:3]}")


def _ask(box, project, env, question, what):
    """One search in a process of its own; it must end cleanly."""
    answers, done = S.drive_run(box, project, env, ("search", question))
    assert not S.clean(done), f"{what}: the read was not clean ({', '.join(S.clean(done))})\n{done.describe()}"
    return answers[0]


def _first_answer(box, tmp_path, question, files=None, name="reference"):
    """The answer ``question`` gets as the very first text a fresh embedder sees, in a new store built alike."""
    fresh = S.EmbedderStandIn()
    try:
        project = S.semantic_project(box, tmp_path / name, fresh, files)
        return _ask(box, project, S.embed_env(box, fresh), question, "the reference")
    finally:
        fresh.close()


# ---- 1. the one file a read writes ---------------------------------------------------------------------------------

@STAND_IN
def test_gov_retrieve_and_gov_context_write_at_most_one_derived_file_under_the_runtime_folder(
        box, embedder, tmp_path):
    """After ``gov retrieve`` (two questions) and ``gov context`` (two tickets), the project's tree differs from
    before in at most one file, always the same one: under ``.gov-runtime/``, not a file of the store, not tracked
    by git. No record, no store file, no index, nothing outside ``.gov-runtime/`` changes. Passes today."""
    project = S.semantic_project(box, tmp_path / "p", embedder, S.ticket_files())
    env = S.embed_env(box, embedder)
    before, tracked = S.project_tree(project), S.tracked(project)
    steps = [("retrieve", "--json", "--root", project, QUESTION),
             ("retrieve", "--json", "--root", project, "who reads the harbour tide tables"),
             ("context", "--json", "--root", project, TICKET),
             ("context", "--json", "--root", project, "TK-W254-BAKERY")]
    written = set()
    for step in steps:
        done = S.gov(box, *step, env=env)
        assert not S.clean(done) and done.envelope().get("ok") is True, done.describe()
        changed = S.tree_change(before, S.project_tree(project))
        written |= set(changed)
        assert len(written) <= 1, (f"reads wrote {len(written)} files, not at most one: {sorted(written)} "
                                   f"(after `gov {step[0]}`)")
    assert embedder.embedded(), "the premise: the reads never reached the embedder"
    for rel in written:
        assert rel.startswith(f"{S.RUNTIME_REL}/"), f"a read wrote {rel}, outside .gov-runtime/"
        assert not S.is_store(rel), f"a read wrote {rel}, a file of the store (authoritative for reads)"
        assert rel not in tracked, f"a read wrote {rel}, a file git tracks"


@STAND_IN
def test_in_a_project_without_an_index_a_read_creates_nothing(box, embedder, tmp_path):
    """A committed project never indexed: ``gov retrieve`` and ``gov context`` create no ``.gov-runtime/`` and change
    no file (as W1-21 holds for the retrieval). Passes today."""
    project = S.new_repo(tmp_path / "bare")
    S.adopt_embedded(project)
    for rel, text in S.ticket_files().items():
        S.write(project, rel, text)
    S.commit_all(project)
    before = S.project_tree(project)
    env = S.embed_env(box, embedder)
    for step in (("retrieve", "--json", "--root", project, QUESTION), ("context", "--json", "--root", project, TICKET)):
        done = S.gov(box, *step, env=env)
        assert "Traceback" not in done.stderr, done.describe()
    assert not (project / S.RUNTIME_REL).exists(), "a read in a project without an index made .gov-runtime/"
    assert S.project_tree(project) == before, f"a read changed {S.tree_change(before, S.project_tree(project))}"


# ---- 2. the key: model, revision and a hash of the exact text ------------------------------------------------------

DISTINCT = "Zyxquokkamarmalade"


@STAND_IN
def test_no_file_of_the_project_holds_a_question_in_clear_after_it_was_asked(box, embedder, tmp_path):
    """*Red.* A question with a word no file holds, asked through ``gov retrieve`` and through the semantic search:
    afterwards no file of the project (the store, the cache, anything) holds that word, in UTF-8 or UTF-16. The key
    is a hash of the text, not the text. Today the cache holds the question in clear."""
    project = S.semantic_project(box, tmp_path / "p", embedder)
    question = f"who fires the glazed bowls for {DISTINCT}"
    env = S.embed_env(box, embedder)
    done = S.gov(box, "retrieve", "--json", "--root", project, question, env=env)
    assert not S.clean(done), done.describe()
    _ask(box, project, env, question, "the search")
    assert embedder.asked_for(question) >= 1, "the premise: the question was never sent to the embedder"
    assert S.runtime_others(project), "the premise: the reads left no cache to look in"
    forms = {"UTF-8": DISTINCT.encode("utf-8"), "UTF-16-LE": DISTINCT.encode("utf-16-le"),
             "UTF-16-BE": DISTINCT.encode("utf-16-be")}
    holding = sorted(f"{rel} ({name})" for rel in S.project_tree(project)
                     for name, form in forms.items() if form in (project / rel).read_bytes())
    assert not holding, f"the question is kept in clear: {holding}"


@STAND_IN
def test_two_long_texts_that_differ_only_in_their_last_character_get_their_own_answers(box, embedder, tmp_path):
    """Two questions of about 8,000 characters that differ only in their last character: the embedder sends the
    first to the kiln and the second to the forge. Each gets its own answer, and the first, asked again, its own. A
    key made of part of the text (its first characters) would give the second the first's vector. Passes today."""
    stem = "who fires the glazed bowls and keeps the kiln " * 170
    first, second = stem + "A", stem + "B"
    embedder.targets = {first: S.SUBJECTS[S.KILN], second: S.SUBJECTS[S.FORGE]}
    project = S.semantic_project(box, tmp_path / "p", embedder)
    env = S.embed_env(box, embedder)
    one = _ask(box, project, env, first, "the first text")
    two = _ask(box, project, env, second, "the second text")
    again = _ask(box, project, env, first, "the first text again")
    assert max(len(text) for text in embedder.embedded()) >= len(first), \
        "the premise: the whole text was not sent to the embedder"
    assert [hit[1] for hit in S.hits_of(one)][:1] == [S.KILN], f"the premise: {S.hits_of(one)[:2]}"
    assert [hit[1] for hit in S.hits_of(two)][:1] == [S.FORGE], \
        f"a text differing only in its last character got another text's vector: {S.hits_of(two)[:2]}"
    assert [hit[1] for hit in S.hits_of(again)][:1] == [S.KILN], \
        f"after the second text, the first got another text's vector: {S.hits_of(again)[:2]}"


# ---- 3. several sessions at once -----------------------------------------------------------------------------------

PROCESSES = 6
SHARED, OWN = 16, 4


@STAND_IN
def test_several_processes_reading_at_once_on_a_cold_cache_get_the_one_answer_and_lose_no_entry(
        box, embedder, tmp_path):
    """*Red.* Six processes on one project with a cold cache, released together, each asking 16 shared questions
    (each in its own order) and 4 of its own: 40 distinct texts. None errors; every answer is the one the text gets
    as the first text in a new store; afterwards, asking every text again in one process gives the same answers and
    sends **none** of them to the embedder (no entry was lost or torn); and ``.gov-runtime/`` holds the store and at
    most one other file (no lock or temporary file left behind). Today the answers depend on the interleaving."""
    shared = S.questions(SHARED)
    own = [S.questions(OWN, start=100 + OWN * n) for n in range(PROCESSES)]
    texts = shared + [text for group in own for text in group]
    fresh = S.EmbedderStandIn()
    try:
        twin = S.semantic_project(box, tmp_path / "reference", fresh)
        references = {text: _ask(box, twin, S.embed_env(box, fresh), text, "the reference") for text in texts}
    finally:
        fresh.close()
    project = S.semantic_project(box, tmp_path / "p", embedder)
    env = S.embed_env(box, embedder)
    lists = []
    for n in range(PROCESSES):
        mine = shared + own[n]
        random.Random(54 + n).shuffle(mine)
        lists.append([("search", text) for text in mine])
    runs = S.at_once(box, project, env, lists)
    for number, (done, calls) in enumerate(zip(runs, lists), start=1):
        assert not S.clean(done), f"concurrent process {number} was not clean ({', '.join(S.clean(done))})\n" \
                                  f"{done.describe()}"
        answers = S.json.loads(done.stdout.strip().splitlines()[-1])[1:]
        for (_, text), answer in zip(calls, answers):
            _same(answer, references[text], f"process {number}, {text!r}")
    asked = {text: embedder.asked_for(text) for text in texts}
    answers, done = S.drive_run(box, project, env, *[("search", text) for text in texts])
    assert not S.clean(done), done.describe()
    for text, answer in zip(texts, answers):
        _same(answer, references[text], f"asked again after the concurrent reads, {text!r}")
    sent_again = sorted(text for text in texts if embedder.asked_for(text) > asked[text])
    assert not sent_again, (f"after the concurrent reads {len(sent_again)} of {len(texts)} texts were sent to the "
                            f"embedder again: their entries were lost or torn: {sent_again[:5]}")
    others = S.runtime_others(project)
    assert len(others) <= 1, f"the concurrent reads left more than one file beside the store: {others}"


# ---- 4. the bound --------------------------------------------------------------------------------------------------

def test_the_change_record_states_the_cache_s_bound_and_the_setting_that_lowers_it():
    """*Red.* The change record names the setting ``GOV_QUERY_VECTOR_CACHE_MAX_BYTES`` and, on that line, the
    default bound as a whole number of bytes (README, "The bound"). Today it names neither."""
    path = S.REPO_ROOT / S.CHANGE_RECORD_REL
    assert path.is_file(), f"there is no {S.CHANGE_RECORD_REL}"
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if S.CACHE_BOUND_SETTING in line]
    assert lines, f"{S.CHANGE_RECORD_REL} does not name the setting {S.CACHE_BOUND_SETTING}"
    numbers = [int(number.replace(",", "").replace("_", "")) for line in lines
               for number in S.re.findall(r"(?<![\w.])\d[\d,_]*(?![\w.])", line.replace(S.CACHE_BOUND_SETTING, ""))]
    assert any(number > 0 for number in numbers), \
        f"no line naming {S.CACHE_BOUND_SETTING} states the default bound in bytes: {lines}"


BOUNDED = 200     # 200 distinct texts of at least 4,096 bytes each: at least 819,200 bytes, past 256 KiB three times


@STAND_IN
def test_the_cache_never_grows_past_its_bound_and_reads_at_the_bound_give_the_same_answers(box, embedder, tmp_path):
    """*Red.* The bound lowered to 256 KiB by its setting; 200 distinct texts asked in four processes of 50 (at
    least 819,200 bytes of vectors, so the bound is reached). After every process the files beside the store hold
    at most 256 KiB; every read ends cleanly with an answer; and the first and last ten texts, asked again at the
    bound, get the answers they got in a new store without a bound. Today the setting changes nothing: the cache
    grows past the bound."""
    assert BOUNDED * S.VECTOR_BYTES > 3 * S.LOW_BOUND
    texts = S.questions(BOUNDED, start=1000)
    fresh = S.EmbedderStandIn()
    try:
        twin = S.semantic_project(box, tmp_path / "reference", fresh)
        answers, done = S.drive_run(box, twin, S.embed_env(box, fresh), *[("search", text) for text in texts])
        assert not S.clean(done), done.describe()
        references = dict(zip(texts, answers))
    finally:
        fresh.close()
    project = S.semantic_project(box, tmp_path / "p", embedder)
    env = {**S.embed_env(box, embedder), S.CACHE_BOUND_SETTING: str(S.LOW_BOUND)}
    sizes = []
    for start in range(0, BOUNDED, 50):
        answers, done = S.drive_run(box, project, env, *[("search", text) for text in texts[start:start + 50]])
        assert not S.clean(done), f"a read at the bound was not clean\n{done.describe()}"
        for answer in answers:
            _available(answer, "a read at the bound")
        sizes.append(S.others_size(project))
        assert sizes[-1] <= S.LOW_BOUND, (f"the cache grew past its bound of {S.LOW_BOUND} bytes: "
                                          f"{sizes} after {start + 50} texts ({S.runtime_others(project)})")
    again = texts[:10] + texts[-10:]
    answers, done = S.drive_run(box, project, env, *[("search", text) for text in again])
    assert not S.clean(done), done.describe()
    for text, answer in zip(again, answers):
        _same(answer, references[text], f"at the bound, {text!r}")
    assert S.others_size(project) <= S.LOW_BOUND, f"the cache grew past its bound: {S.others_size(project)} bytes"


# ---- 5. rebuildable from nothing; one answer whatever the cache's state --------------------------------------------

STATES = ("cold", "warm", "deleted", "full", "unwritable-folder", "unwritable-file")


@STAND_IN
@pytest.mark.parametrize("state", STATES)
def test_one_text_gets_one_answer_whatever_the_cache_s_state(box, embedder, tmp_path, state):
    """*Red.* The question's answer, each read in a process of its own after other texts, with the cache ``cold``
    (never asked), ``warm`` (asked before), ``deleted`` (every file beside the store removed after it was asked),
    ``full`` (the bound lowered and 200 other texts asked first: the question first asked at the bound; a question
    asked before the cache filled is the bound case's), ``unwritable-folder`` (``.gov-runtime/`` read-only,
    no cache file) or ``unwritable-file`` (the cache's files read-only): the answer the question gets as the first
    text in a new store, hit for hit and distance for distance. An unwritable cache gives no error and no traceback.
    Today the answer depends on what was embedded before the question was first asked."""
    reference = _first_answer(box, tmp_path, QUESTION)
    project = S.semantic_project(box, tmp_path / "p", embedder)
    env = S.embed_env(box, embedder)
    others = iter(S.questions(8, start=500 + 10 * STATES.index(state)))
    ask = lambda text, what=state: _ask(box, project, env, text, what)   # noqa: E731
    runtime = project / S.RUNTIME_REL
    if state == "cold":
        ask(next(others)), ask(next(others))
        _same(ask(QUESTION), reference, "cold, after two other texts")
    elif state == "warm":
        ask(next(others))
        first = ask(QUESTION)
        ask(next(others))
        _same(first, reference, "the first read, after another text")
        _same(ask(QUESTION), reference, "warm, after another text")
    elif state == "deleted":
        ask(QUESTION), ask(next(others))
        assert S.delete_cache(project), "the premise: the reads left no cache to delete"
        ask(next(others))
        _same(ask(QUESTION), reference, "the cache deleted, after another text")
    elif state == "full":
        env = {**env, S.CACHE_BOUND_SETTING: str(S.LOW_BOUND)}
        answers, done = S.drive_run(box, project, env, *[("search", text) for text in S.questions(BOUNDED, start=3000)])
        assert not S.clean(done), done.describe()
        ask(next(others))
        _same(ask(QUESTION), reference, "the cache full, first asked after 200 other texts")
        ask(next(others))
        _same(ask(QUESTION), reference, "the cache full, asked again after another text")
    elif state == "unwritable-folder":
        assert S.os.geteuid() != 0, "the premise: running as root, no folder is read-only"
        with S.ReadOnly(runtime):
            assert S.cannot_create_in(runtime), "the premise: .gov-runtime/ still takes a new file"
            ask(next(others)), ask(next(others))
            _same(ask(QUESTION), reference, ".gov-runtime/ read-only, after two other texts")
            ask(next(others))
            _same(ask(QUESTION), reference, ".gov-runtime/ read-only, asked again after another text")
        assert not S.runtime_others(project), f"a file was made in a read-only folder: {S.runtime_others(project)}"
    elif state == "unwritable-file":
        ask(next(others))
        files = S.runtime_others(project)
        assert files, "the premise: the read left no cache file to make read-only"
        with S.ReadOnly(*[project / rel for rel in files]):
            ask(next(others))
            _same(ask(QUESTION), reference, "the cache's files read-only, after another text")
            ask(next(others))
            _same(ask(QUESTION), reference, "the cache's files read-only, asked again after another text")


@STAND_IN
def test_one_ticket_gets_one_packet_hash_whatever_the_cache_s_state(box, embedder, tmp_path):
    """*Red.* ``gov context --json`` for one ticket, in a process of its own, after other tickets' contexts and
    other questions: cold, warm, the cache deleted, ``.gov-runtime/`` read-only, the cache's files read-only, and the
    cache full (bound lowered, 200 other texts): one packet and one hash, the one the ticket gets as the first
    context in a new store built alike. Every run ends with exit code 0 and no traceback. Today the hash depends on
    what was embedded before the ticket's question was first asked."""
    files = S.ticket_files()
    fresh = S.EmbedderStandIn()
    try:
        twin = S.semantic_project(box, tmp_path / "reference", fresh, files)
        reference = S.gov(box, "context", "--json", "--root", twin, TICKET, env=S.embed_env(box, fresh))
        assert not S.clean(reference), reference.describe()
        reference = reference.envelope()["result"]
    finally:
        fresh.close()
    assert reference[S.K_SUPPLEMENTARY], "the premise: the ticket's context holds no retrieval item"
    project = S.semantic_project(box, tmp_path / "p", embedder, files)
    env = S.embed_env(box, embedder)
    runtime = project / S.RUNTIME_REL

    def context(what, ticket=TICKET, env=env):
        done = S.gov(box, "context", "--json", "--root", project, ticket, env=env)
        assert not S.clean(done) and done.envelope().get("ok") is True, f"{what}\n{done.describe()}"
        return done.envelope()["result"]

    def same(what, **kwargs):
        packet = context(what, **kwargs)
        assert packet[S.K_HASH] == reference[S.K_HASH] and S.canonical(packet) == S.canonical(reference), (
            f"{what}: one ticket, two packets: {packet[S.K_HASH]} != {reference[S.K_HASH]} (the first in a new store)"
            f"\nsupplementary ids: {[item.get('id') for item in packet[S.K_SUPPLEMENTARY]]} / "
            f"{[item.get('id') for item in reference[S.K_SUPPLEMENTARY]]}")

    context("another ticket first", ticket="TK-W254-BAKERY")
    same("cold, after another ticket")
    context("another ticket", ticket="TK-W254-ORCHARD")
    same("warm, after another ticket")
    assert S.delete_cache(project), "the premise: the contexts left no cache to delete"
    context("another ticket", ticket="TK-W254-BAKERY")
    same("the cache deleted, after another ticket")
    S.delete_cache(project)
    with S.ReadOnly(runtime):
        assert S.cannot_create_in(runtime), "the premise: .gov-runtime/ still takes a new file"
        context("another ticket", ticket="TK-W254-ORCHARD")
        same(".gov-runtime/ read-only, after another ticket")
    context("another ticket", ticket="TK-W254-BAKERY")
    assert S.runtime_others(project), "the premise: the context left no cache file to make read-only"
    with S.ReadOnly(*[project / rel for rel in S.runtime_others(project)]):
        same("the cache's files read-only, after another ticket")
    bounded = {**env, S.CACHE_BOUND_SETTING: str(S.LOW_BOUND)}
    answers, done = S.drive_run(box, project, bounded, *[("search", text) for text in S.questions(BOUNDED, start=5000)])
    assert not S.clean(done), done.describe()
    same("the cache full, after 200 other texts", env=bounded)
