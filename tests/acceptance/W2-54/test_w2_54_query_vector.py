"""KPI success 2 (round 2): the same text always gets the same query vector, whatever was embedded before it; query
vectors are stored, keyed by the model, the model's revision and the exact text, and a stored vector is used
whenever its key matches [owner, 2026-10-18, P-W2-30 (a)].

Seen from outside, through public interfaces only: what a search gives (``gov.retrieval.semantic.search(root, q,
refresh=False)``: its hits, their order and their distances), what the retrieval's public entry gives
(``gov.retrieval.retrieve.retrieve``), what ``gov context --json`` gives, and what the context-reproducibility check
says. No case names where or how a vector is kept.

The embedder is the stand-in of the README ("The stand-in embedder"): like the real one, it gives a text a slightly
different vector when a different text was embedded just before it, and the same vector on a repeat. ``targets``
send a question's vector to the words of one file of the corpus, so the nearest hit shows which vector was used.

Red today: the cases marked *red* fail because each question is embedded afresh, after whatever was embedded
before it, so one question gets several answers in one store. The others pass today and hold what the change must
keep (README, "Round 2").
"""

from __future__ import annotations

import collections
import unicodedata

import pytest

import w2_54_support as S

LACKING = ([] if S.shutil.which("gitleaks") else ["gitleaks is not on PATH: the fixture's index cannot be built"]) + (
    [] if S.importlib.util.find_spec("sqlite_vec") else ["sqlite_vec cannot be imported: no vector can be stored"])
STAND_IN = pytest.mark.skipif(bool(LACKING), reason="; ".join(LACKING) or "none")

QUESTION = "who fires the glazed bowls"
OTHERS = ("who reads the harbour tide tables", "when are the pear trees pruned", "who smokes the hives in July")


def _answers_agree(answers, question):
    first = S.hits_of(answers[0])
    assert answers[0].get("available") is True and first, f"the first answer to {question!r} has no hit: {answers[0]}"
    for number, answer in enumerate(answers[1:], start=2):
        assert answer.get("available") is True, f"answer {number} to {question!r} is unavailable: {answer}"
        assert S.hits_of(answer) == first, (
            f"one question, two answers in one store: answer {number} to {question!r} differs from the first\n"
            f"first: {first[:4]}\nthen:  {S.hits_of(answer)[:4]}")


# ---- 1. one text, one query vector, in one store, whatever was embedded before it ---------------------------------

@STAND_IN
def test_one_question_asked_again_after_others_gives_the_same_answer_across_processes(box, embedder, tmp_path):
    """*Red.* Each search in a process of its own: the question, then other questions, then the question again,
    and again right after itself. The same hits, in the same order, at the same distances, every time."""
    project = S.semantic_project(box, tmp_path / "p", embedder)
    answers = [S.ask(box, project, embedder, QUESTION)]
    for other in OTHERS:
        S.ask(box, project, embedder, other)
        answers.append(S.ask(box, project, embedder, QUESTION))
    answers.append(S.ask(box, project, embedder, QUESTION))
    assert embedder.asked_for(OTHERS[0]) >= 1, "the premise: the other questions were sent to the embedder"
    _answers_agree(answers, QUESTION)


@STAND_IN
def test_one_question_asked_again_after_others_gives_the_same_answer_within_one_process(box, embedder, tmp_path):
    """*Red.* The same, every search in one process."""
    project = S.semantic_project(box, tmp_path / "p", embedder)
    calls = [("search", QUESTION)]
    for other in OTHERS:
        calls += [("search", other), ("search", QUESTION)]
    answers = S.drive(box, project, embedder, *calls)
    _answers_agree(answers[0::2], QUESTION)


@STAND_IN
def test_the_retrieval_s_public_entry_gives_one_bundle_for_one_question_whatever_was_asked_before(
        box, embedder, tmp_path):
    """*Red.* ``gov.retrieval.retrieve.retrieve``: one question, another between, the same question again (in one
    process and in another): the same bundle, the same evidence in the same order."""
    project = S.semantic_project(box, tmp_path / "p", embedder)
    within = S.drive(box, project, embedder, ("retrieve", QUESTION), ("retrieve", OTHERS[0]), ("retrieve", QUESTION))
    S.drive(box, project, embedder, ("retrieve", OTHERS[1]))
    later = S.drive(box, project, embedder, ("retrieve", QUESTION))[0]
    bundles = [within[0], within[2], later]
    evidence = [[(item.get("chunk_id"), item.get("path")) for item in bundle.get("evidence") or []]
                for bundle in bundles]
    assert evidence[0], f"the premise: the retrieval returned no evidence: {S.canonical(within[0])[:800]}"
    assert bundles[0]["facets"].get("semantic", {}).get("available") is True, \
        f"the premise: the semantic route did not answer: {bundles[0]['facets']}"
    for number, items in enumerate(evidence[1:], start=2):
        assert items == evidence[0], (f"one question, two bundles in one store (bundle {number}):\n"
                                      f"first: {evidence[0]}\nthen:  {items}")
    for bundle in bundles[1:]:
        assert S.canonical(bundle) == S.canonical(bundles[0]), "one question, two bundles in one store"


# ---- 2. two computations of every ticket's context in one store give one hash -------------------------------------

@STAND_IN
def test_gov_context_twice_for_each_ticket_with_others_between_gives_one_packet(box, embedder, tmp_path):
    """*Red.* Three tickets, each asking the retrieval its own question. ``gov context --json`` for each, then for
    each again after the others, then in the opposite order: one packet and one hash per ticket."""
    project = S.semantic_project(box, tmp_path / "p", embedder, S.ticket_files())
    tickets = list(S.QUESTION_TICKETS)
    packets = collections.defaultdict(list)
    for ticket_id in tickets + tickets + tickets[::-1]:
        done = S.gov(box, "context", "--json", "--root", project, ticket_id, env=S.embed_env(box, embedder))
        assert done.returncode == 0, done.describe()
        packets[ticket_id].append(done.envelope()["result"])
    assert len(embedder.embedded()) > 0, "the premise: no context asked the embedder anything"
    for ticket_id, computed in packets.items():
        assert computed[0][S.K_SUPPLEMENTARY], f"the premise: {ticket_id}'s context holds no retrieval item"
        hashes = [packet[S.K_HASH] for packet in computed]
        assert len(set(hashes)) == 1, (
            f"{ticket_id}: {len(set(hashes))} hashes in {len(hashes)} computations in one store: {hashes}\n"
            f"supplementary ids: {[[item.get('id') for item in p[S.K_SUPPLEMENTARY]] for p in computed]}")
        assert len({S.canonical(packet) for packet in computed}) == 1, f"{ticket_id}: two packets in one store"


@STAND_IN
def test_the_context_check_is_green_over_several_tickets_with_an_embedder_whose_vectors_vary(
        box, embedder, tmp_path):
    """*Red.* The context-reproducibility check, run as its declaration says, over a project with three tickets,
    the stand-in behind every context: green. Today it prints ``FAIL: <ticket>: <hash> != <hash>``."""
    project = S.semantic_project(box, tmp_path / "p", embedder, S.ticket_files())
    before = len(embedder.embedded())
    done = S.run(["sh", "-c", S.yaml.safe_load(
        (S.REPO_ROOT / S.CONTEXT_DECLARATION_REL).read_text(encoding="utf-8"))["command"]],
        cwd=project, env=S.embed_env(box, embedder), timeout=S.CHECK_TIMEOUT_S)
    assert len(embedder.embedded()) > before, "the premise: the check's contexts never reached the embedder"
    assert done.returncode == 0 and "FAIL" not in done.stdout, \
        f"two computations of a ticket's context in one store give two hashes\n{done.describe()}"


# ---- 3. a stored vector is never taken for another key ------------------------------------------------------------

SPELLINGS = {
    "case": "Who fires the glazed bowls at the café",
    "spacing": "who fires the glazed  bowls at the café",
    "unicode-normal-form": unicodedata.normalize("NFD", "who fires the glazed bowls at the café"),
    "trailing-newline": "who fires the glazed bowls at the café\n",
}
SPELLED = unicodedata.normalize("NFC", "who fires the glazed bowls at the café")


@STAND_IN
@pytest.mark.parametrize("spelling", sorted(SPELLINGS))
def test_a_text_that_differs_in_any_character_gets_its_own_answer(box, embedder, tmp_path, spelling):
    """A question and another spelling of it (``spelling``): the embedder sends the first to the kiln and the
    other to the forge. Asked in one store, first the one and then the other, each gets the answer its own text gets
    from the embedder, never the other's; the first, asked again, still gets its own. Passes today."""
    other = SPELLINGS[spelling]
    assert other != SPELLED
    embedder.targets = {SPELLED: S.SUBJECTS[S.KILN], other: S.SUBJECTS[S.FORGE]}
    project = S.semantic_project(box, tmp_path / "p", embedder)
    first = S.ask(box, project, embedder, SPELLED)
    second = S.ask(box, project, embedder, other)
    again = S.ask(box, project, embedder, SPELLED)
    assert [hit[1] for hit in S.hits_of(first)][:1] == [S.KILN], f"the premise: {S.hits_of(first)[:3]}"
    assert [hit[1] for hit in S.hits_of(second)][:1] == [S.FORGE], (
        f"{spelling}: {other!r} got the answer of {SPELLED!r} (nearest {S.hits_of(second)[:2]}), "
        f"not the one its own text gets from the embedder")
    assert [hit[1] for hit in S.hits_of(again)][:1] == [S.KILN], \
        f"{spelling}: after {other!r}, {SPELLED!r} got another text's answer: {S.hits_of(again)[:2]}"


@STAND_IN
def test_a_stored_vector_is_not_used_under_another_revision_and_is_used_again_when_the_revision_matches(
        box, embedder, tmp_path):
    """*Red.* The model list reports one digest (the model's revision): the question goes to the kiln. Then it
    reports another digest, and that build of the model sends the question to the forge: the answer is the forge's,
    or the facet is unavailable with no hit, never the kiln's. Then the first digest again: the first answer, hit
    for hit and distance for distance, whatever was embedded meanwhile. Every request to be embedded names the
    pinned model (the key's model part; no public interface selects another model). Today the last answer differs
    from the first."""
    embedder.targets = {QUESTION: S.SUBJECTS[S.KILN]}
    project = S.semantic_project(box, tmp_path / "p", embedder)
    first = S.ask(box, project, embedder, QUESTION)
    assert [hit[1] for hit in S.hits_of(first)][:1] == [S.KILN], f"the premise: {S.hits_of(first)[:3]}"
    rebuilt = S.EmbedderStandIn(digest=S.OTHER_DIGEST, targets={QUESTION: S.SUBJECTS[S.FORGE]})
    try:
        S.ask(box, project, rebuilt, OTHERS[0])
        other = S.ask(box, project, rebuilt, QUESTION)
        models = {request.get("model") for request in rebuilt.requests if "texts" in request}
    finally:
        rebuilt.close()
    if other.get("available"):
        assert [hit[1] for hit in S.hits_of(other)][:1] == [S.FORGE], (
            f"under another revision of the model the question got the vector stored under the first: "
            f"{S.hits_of(other)[:2]}")
    else:
        assert other.get("hits") == [], f"an unavailable facet gave hits: {other}"
    S.ask(box, project, embedder, OTHERS[1])
    back = S.ask(box, project, embedder, QUESTION)
    models |= {request.get("model") for request in embedder.requests if "texts" in request}
    assert models == {S.EMBED_MODEL}, f"vectors were asked of another model than the pinned one: {models}"
    assert S.hits_of(back) == S.hits_of(first), (
        "with the first revision again, the question did not get the vector stored under it\n"
        f"first: {S.hits_of(first)[:3]}\nback:  {S.hits_of(back)[:3]}")


# ---- 4. the first answer for a text is unchanged --------------------------------------------------------------------

@STAND_IN
def test_a_question_asked_for_the_first_time_gets_the_vector_the_embedder_returns_for_it(box, embedder, tmp_path):
    """In a new store, a question asked for the first time is sent to the embedder and answered with the vector
    it returns: the embedder sends it to the orchard, which its own words do not lead to, and the orchard is
    nearest. Two projects built alike, asked alike, give that first answer hit for hit. Passes today."""
    embedder.targets = {QUESTION: S.SUBJECTS[S.ORCHARD]}
    project = S.semantic_project(box, tmp_path / "p", embedder)
    answer = S.ask(box, project, embedder, QUESTION)
    assert embedder.asked_for(QUESTION) == 1, \
        f"a question asked for the first time was sent to the embedder {embedder.asked_for(QUESTION)} times"
    assert [hit[1] for hit in S.hits_of(answer)][:1] == [S.ORCHARD], \
        f"the first answer is not the embedder's vector for the question: {S.hits_of(answer)[:3]}"
    twin_embedder = S.EmbedderStandIn(targets={QUESTION: S.SUBJECTS[S.ORCHARD]})
    try:
        twin = S.semantic_project(box, tmp_path / "twin", twin_embedder)
        twin_answer = S.ask(box, twin, twin_embedder, QUESTION)
    finally:
        twin_embedder.close()
    assert S.hits_of(twin_answer) == S.hits_of(answer), \
        f"two new stores asked alike give two first answers:\n{S.hits_of(answer)[:3]}\n{S.hits_of(twin_answer)[:3]}"


# ---- 5. nothing is left behind by a failed or partial embedding call -----------------------------------------------

@STAND_IN
@pytest.mark.parametrize("failure", ("fail", "short"))
def test_a_failed_embedding_gives_no_hit_and_leaves_nothing_a_later_search_uses(box, embedder, tmp_path, failure):
    """The embedder fails (``fail``: HTTP 500) or returns one vector fewer than asked (``short``): the facet is
    unavailable with no hit, as today. The next search, the embedder healthy, asks the embedder again and gets its
    vector (the apiary). Passes today."""
    embedder.targets = {QUESTION: S.SUBJECTS[S.APIARY]}
    project = S.semantic_project(box, tmp_path / "p", embedder)
    embedder.mode = failure
    failed = S.ask(box, project, embedder, QUESTION)
    assert embedder.asked_for(QUESTION) >= 1, "the premise: the question was sent to the failing embedder"
    assert failed.get("available") is False and failed.get("hits") == [], \
        f"a failed embedding ({failure}) gave an answer: {failed}"
    embedder.mode = "healthy"
    sent = embedder.asked_for(QUESTION)
    healthy = S.ask(box, project, embedder, QUESTION)
    assert embedder.asked_for(QUESTION) > sent, \
        f"after a failed embedding ({failure}) the next search did not ask the embedder: something was left behind"
    assert healthy.get("available") is True and [hit[1] for hit in S.hits_of(healthy)][:1] == [S.APIARY], \
        f"after a failed embedding ({failure}) the answer is not the healthy embedder's: {healthy}"


# ---- 6. one project's stored vectors are never another's -----------------------------------------------------------

@STAND_IN
def test_two_projects_do_not_share_query_vectors(box, tmp_path):
    """Two projects, each with its own store, the same model and revision. In the first the embedder sends the
    question to the kiln; in the second it sends it to the forge. Each gets its own embedder's answer; the second's
    search changes no file of the first project's runtime folder and none under HOME. Passes today."""
    one = S.EmbedderStandIn(targets={QUESTION: S.SUBJECTS[S.KILN]})
    two = S.EmbedderStandIn(targets={QUESTION: S.SUBJECTS[S.FORGE]})
    try:
        first = S.semantic_project(box, tmp_path / "one", one)
        second = S.semantic_project(box, tmp_path / "two", two)
        in_first = S.ask(box, first, one, QUESTION)
        runtime, home = S.runtime_digest(first), S.home_files(box)
        in_second = S.ask(box, second, two, QUESTION)
        assert S.runtime_digest(first) == runtime, \
            "a search in the second project changed the first project's runtime folder"
        assert S.home_files(box) == home, f"a search wrote under HOME: {sorted(set(S.home_files(box)) - set(home))}"
        assert two.asked_for(QUESTION) >= 1, "the second project never asked its embedder: it used another's vector"
    finally:
        one.close()
        two.close()
    assert [hit[1] for hit in S.hits_of(in_first)][:1] == [S.KILN], f"the premise: {S.hits_of(in_first)[:3]}"
    assert [hit[1] for hit in S.hits_of(in_second)][:1] == [S.FORGE], \
        f"the second project got the first project's vector: {S.hits_of(in_second)[:3]}"


# ---- the real embedder (this machine's Ollama) ----------------------------------------------------------------------

@pytest.mark.skipif(bool(S.real_embedder_lacking()), reason="; ".join(S.real_embedder_lacking()) or "none")
def test_with_the_real_embedder_one_question_gives_one_answer_whatever_was_asked_before(box, tmp_path):
    """*Red* where the variation reproduces. **Needs the real embedder** (``ollama`` with ``qwen3-embedding:0.6b``),
    ``sqlite_vec`` and ``gitleaks``; skips with the reason otherwise. In this machine's own environment: the
    question, other questions, the question again, in separate processes and in one: one answer."""
    env = S.real_env(box)
    project = S.new_repo(tmp_path / "real")
    S.adopt_embedded(project)
    for rel, text in S.SUBJECTS.items():
        S.write(project, rel, text)
    S.commit_all(project)
    report = S.drive_env(box, project, env, ("refresh",), ("load",))[0]
    assert report.get("available") is True, f"the vectors were not built with the real embedder: {report}"
    answers = [S.drive_env(box, project, env, ("search", QUESTION))[0]]
    for other in OTHERS:
        S.drive_env(box, project, env, ("search", other))
        answers.append(S.drive_env(box, project, env, ("search", QUESTION))[0])
    calls = [("search", QUESTION)]
    for other in reversed(OTHERS):
        calls += [("search", other), ("search", QUESTION)]
    answers += S.drive_env(box, project, env, *calls)[0::2]
    _answers_agree(answers, QUESTION)
