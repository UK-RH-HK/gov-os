"""Round 4 (DEC-798, owner, 2026-10-19, P-W2-40 (b)): query embeddings come from the CPU-only embedder on its own
port, the shared runner is never moved to the CPU, and the cache key names the device.

KPI success 5: "On the shared GPU Ollama, the same text read many times, after different texts and by two sessions at
once, gets one vector: query embeddings come from the CPU-only embedder on its own port, the shared runner is never
moved to the CPU, and the cache key names the device." KPI success 6: "W1-21's hit@5 on the real models, with CPU
query vectors against the GPU-built index, is at or above its pass line of 80; the figure is recorded in the change
record."

The cases here use stand-ins only (README, "Round 4"): the shared runner at ``OLLAMA_HOST`` (its model on the GPU) and
the CPU embedder at the address the setting ``GOV_QUERY_OLLAMA_HOST`` names (an interface this KPI needs), both round
2's stand-in with its variation, and a stand-in ``ollama`` executable for the on-demand start. What the GPU itself
does is held by ``test_w2_54_shared_gpu.py``, which the lead runs.

Seen from outside, through public interfaces only: which stand-in a command asks, with what (its texts and its
``options``), what ``/api/ps`` reports there; what a read answers (``gov retrieve --json``, ``gov context --json``,
``gov.retrieval.semantic.search``); what is left on disk; what the stand-in executable was told when a read started it.
No case names the code that does it.

Rewrite-Reason: DEC-1033 (owner, 2026-11-02; item 2 (b) replaces DEC-798's CPU-only rule; item 3, a test designer
revises the acceptance tests the patches turn red): a question's vector is accepted from any device the query embedder
reports the model loaded on, and the query embedder is started with the GPU left visible. Six cases enforced DEC-798
(README, "DEC-1033: six cases revised"). What still holds is kept: the questions go to the query embedder at its own
address and only there, the chunks to the shared runner, never a runner option to it; a read starts the query
embedder at its address as ``serve`` and never stops it; two reads at once leave one serving and both answered; an
embedder that does not report the model loaded gives no vector, named, nothing cached, no fallback. "The CPU
embedder" in the names and texts that remain is the query embedder at ``GOV_QUERY_OLLAMA_HOST`` (the fixture ``cpu``,
its stand-in on the CPU).
"""

from __future__ import annotations

import re

import pytest

import w2_54_support as S

LACKING = ([] if S.shutil.which("gitleaks") else ["gitleaks is not on PATH: the fixture's index cannot be built"]) + (
    [] if S.importlib.util.find_spec("sqlite_vec") else ["sqlite_vec cannot be imported: no vector can be stored"])
STAND_IN = pytest.mark.skipif(bool(LACKING), reason="; ".join(LACKING) or "none")

QUESTION = "who fires the glazed bowls"
OTHER = "who reads the harbour tide tables"
# Rewrite-Reason: DEC-811 (orchestrator, delegated, 2026-10-19), PKG-W2-54-4-1 (a): a phrase the kiln note holds, for
# the reads that expect lexical evidence once the semantic facet is unavailable. QUESTION ends with it, so a text sent
# for either ends with PHRASE (``S.sent_for(..., PHRASE)`` sees both).
PHRASE = "fires the glazed bowls"
# Rewrite-Reason: DEC-811, PKG-W2-54-4-2 (a): steps 5 and 6 of the first case ask texts no earlier step asked; the
# step-5 text is aimed at the kiln (CPU) and the forge (shared runner), as QUESTION is.
AGAIN_KILN = "where are the glazed bowls fired"
AGAIN_OTHER = "who lifts the honey frames"
CHUNK_PHRASES = {rel: text.split("\n\n", 1)[1].split(";")[0].split(" in ")[0].strip() for rel, text in S.SUBJECTS.items()}


@pytest.fixture()
def shared():
    """The shared runner: round 2's stand-in at OLLAMA_HOST, its model on the GPU; it sends the questions to the
    forge, so an answer from it shows."""
    stand_in = S.EmbedderStandIn(device="gpu", targets=dict.fromkeys((QUESTION, PHRASE, AGAIN_KILN), S.SUBJECTS[S.FORGE]))
    try:
        yield stand_in
    finally:
        stand_in.close()


@pytest.fixture()
def cpu():
    """The query embedder ("the CPU embedder" in the names that remain): round 2's stand-in at its address, which
    sends the questions to the kiln.

    Rewrite-Reason: DEC-1065 (1): no CPU fallback anywhere; a question's vector reported on the CPU is refused
    (``EMBEDDER_ON_CPU``). The stand-in reports its model on the GPU (it was on the CPU), so what the cases guard
    (the questions go to the query embedder only, the chunks to the shared runner, round 3's key never served, a
    model not reported loaded gives no vector) still has its meaning."""
    stand_in = S.EmbedderStandIn(device="gpu", targets=dict.fromkeys((QUESTION, PHRASE, AGAIN_KILN), S.SUBJECTS[S.KILN]))
    try:
        yield stand_in
    finally:
        stand_in.close()


@pytest.fixture()
def daemons(tmp_path):
    daemons = S.Daemons(tmp_path / "daemons")
    try:
        yield daemons
    finally:
        daemons.close()


def _nearest(answer):
    return [hit[1] for hit in S.hits_of(answer)][:1]


def _chunks_in(texts):
    """The corpus files whose chunk text is among ``texts``."""
    return sorted(rel for rel, phrase in CHUNK_PHRASES.items() if any(phrase in text for text in texts))


def _no_option_and_on_gpu(shared):
    assert not shared.optioned(), (
        f"a request to the shared runner named a runner option: "
        f"{[(request['route'], request['options']) for request in shared.optioned()][:4]}")
    assert shared.on_gpu(), (f"the shared runner was moved off the GPU: its /api/ps reports {shared.ps_models()} "
                             f"(the requests that moved it: {[r['options'] for r in shared.requests if r.get('options')]})")


# ---- 1. query embeddings go to the CPU embedder, and only those ---------------------------------------------------

# Rewrite-Reason: W2-04's KPIs 2 and 4 (CAP-15.d, DEC-860), DEC-1005: ``gov context`` sends nothing to an embedder
# (P-W2-04-2 (A)), so the two questions its steps asked are asked through ``gov retrieve``: the tickets' titles.
TITLE_TIDES, TITLE_BAKERY = S.QUESTION_TICKETS["TK-W254-TIDES"], S.QUESTION_TICKETS["TK-W254-BAKERY"]


@STAND_IN
def test_every_read_sends_its_question_to_the_cpu_embedder_and_nothing_to_the_shared_runner(
        box, shared, cpu, tmp_path):
    """*Red.* With the shared runner at OLLAMA_HOST and the CPU embedder at its address: four ``gov retrieve``, a
    semantic search and a retrieval through the public entry each send the CPU embedder at least one text to embed
    (the question) and send the shared runner none; the search's answer is the CPU embedder's vector (the kiln,
    where the shared runner's would be the forge). Two ``gov context`` send neither embedder anything. No request to
    the shared runner names a runner option, and its model stays on the GPU. Today every question goes to
    OLLAMA_HOST, with ``num_gpu: 0``.

    Rewrite-Reason: DEC-811 (orchestrator, delegated, 2026-10-19), PKG-W2-54-4-2 (a): the search and the retrieval
    (steps 5 and 6) ask texts no earlier step asked (they asked QUESTION and OTHER again, whose vectors the cache
    rightly serves with no request), so each step has a text the CPU embedder has not embedded yet.

    Rewrite-Reason: W2-04's KPIs 2 and 4 (CAP-15.d, DEC-860), DEC-1005: steps 3 and 4 were two ``gov context``, whose
    question went to the embedder; ``gov context`` now sends none (W2-04's addendum, S4 and S7), so they are two
    ``gov retrieve`` of the two tickets' titles (the read that reaches the semantic route), held as every read is.
    The two ``gov context`` stay, and add a guarantee: they send neither embedder a text."""
    project = S.semantic_project(box, tmp_path / "p", shared, S.ticket_files(), cpu=cpu)
    assert shared.embed_requests() and not cpu.embedded(), \
        f"the premise: the index was built through the shared runner only (CPU embedder sent {cpu.embedded()[:2]})"
    env = S.embed_env(box, shared, cpu)
    steps = [("gov", "retrieve", "--json", "--root", project, QUESTION),
             ("gov", "retrieve", "--json", "--root", project, OTHER),
             ("gov", "retrieve", "--json", "--root", project, TITLE_TIDES),
             ("gov", "retrieve", "--json", "--root", project, TITLE_BAKERY),
             ("search", AGAIN_KILN), ("retrieve", AGAIN_OTHER)]
    answer = None
    for step in steps:
        to_shared, to_cpu = len(shared.embed_requests()), len(cpu.embed_requests())
        if step[0] == "gov":
            done = S.gov(box, *step[1:], env=env)
            assert not S.clean(done) and done.envelope().get("ok") is True, done.describe()
        else:
            answers, done = S.drive_run(box, project, env, step)
            assert not S.clean(done), done.describe()
            answer = answers[0] if step[0] == "search" else answer
        what = " ".join(str(part) for part in step if part != project)
        sent = [text[-60:] for request in shared.embed_requests()[to_shared:] for text in request["texts"]]
        assert not sent, f"`{what}` sent the shared runner texts to embed: {sent}"
        assert len(cpu.embed_requests()) > to_cpu, f"`{what}` sent the CPU embedder nothing to embed"
    assert all(cpu.asked_for(text) >= 1 for text in (QUESTION, OTHER, TITLE_TIDES, TITLE_BAKERY, AGAIN_KILN,
                                                     AGAIN_OTHER)), "the questions never reached the CPU embedder"
    for ticket_id in ("TK-W254-TIDES", "TK-W254-BAKERY"):
        to_shared, to_cpu = len(shared.embed_requests()), len(cpu.embed_requests())
        done = S.gov(box, "context", "--json", "--root", project, ticket_id, env=env)
        assert not S.clean(done) and done.envelope().get("ok") is True, done.describe()
        sent = [text[-60:] for stand_in, before in ((shared, to_shared), (cpu, to_cpu))
                for request in stand_in.embed_requests()[before:] for text in request["texts"]]
        assert not sent, f"`gov context {ticket_id}` sent an embedder texts to embed: {sent}"
    assert answer.get("available") is True and _nearest(answer) == [S.KILN], (
        f"the search's answer is not the CPU embedder's vector (the kiln): {S.hits_of(answer)[:2]}")
    assert not _chunks_in(cpu.embedded()), f"the CPU embedder was sent chunks: {_chunks_in(cpu.embedded())}"
    _no_option_and_on_gpu(shared)


@STAND_IN
def test_a_rebuild_and_a_search_that_builds_vectors_send_every_chunk_to_the_shared_runner_and_none_to_the_cpu_one(
        box, shared, cpu, tmp_path):
    """*Red.* The index of a project is built (the semantic refresh), then a new file is committed and ``gov rebuild``
    runs, then another file and a search that builds missing vectors (``refresh=True``): every chunk goes to the shared
    runner, none to the CPU embedder; the search's question goes to the CPU embedder and not to the shared runner. No
    request to the shared runner names a runner option, and its model stays on the GPU. The build and the rebuild pass
    today; the search sends its question to OLLAMA_HOST with ``num_gpu: 0``."""
    project = S.semantic_project(box, tmp_path / "p", shared, cpu=cpu)
    assert _chunks_in(shared.embedded()) == sorted(S.SUBJECTS), \
        f"the build did not send every chunk to the shared runner: {_chunks_in(shared.embedded())}"
    env = S.embed_env(box, shared, cpu)
    cooper, weaver = "The cooper hoops the oak barrels", "The weaver threads the linen warp"
    S.write(project, "notes/cooper.md", f"# Cooper\n\n{cooper} by the river.\n")
    S.commit_all(project, "the cooper")
    done = S.gov(box, "rebuild", "--json", "--root", project, env=env, timeout=300)
    assert done.returncode == 0 and done.envelope().get("ok") is True, done.describe()
    assert done.envelope()["result"]["stores"]["semantic"]["status"] == "recreated", done.describe()
    assert any(cooper in text for text in shared.embedded()), "gov rebuild did not send the new chunk to the shared runner"
    S.write(project, "notes/weaver.md", f"# Weaver\n\n{weaver} at the loom.\n")
    S.commit_all(project, "the weaver")
    asked = len(shared.embedded())
    answers, done = S.drive_run(box, project, env, ("search-refresh", QUESTION))
    assert not S.clean(done) and answers[0].get("available") is True, done.describe()
    assert any(weaver in text for text in shared.embedded()[asked:]), \
        "the search that builds missing vectors did not send the new chunk to the shared runner"
    to_cpu = [text for text in cpu.embedded() if cooper in text or weaver in text or _chunks_in([text])]
    assert not to_cpu, f"chunks were sent to the CPU embedder: {[text[:50] for text in to_cpu]}"
    assert not S.sent_for([shared], QUESTION), \
        f"the search sent its question to the shared runner: {S.sent_for([shared], QUESTION)}"
    assert cpu.asked_for(QUESTION) >= 1, "the search's question never reached the CPU embedder"
    _no_option_and_on_gpu(shared)


# ---- 2. the device ---------------------------------------------------------------------------------------------------

@STAND_IN
@pytest.mark.parametrize("reported", ("gpu", "partial"))
def test_a_question_s_vector_from_the_query_embedder_is_used_whatever_device_it_reports_the_model_on(
        box, shared, cpu, tmp_path, reported):
    """The embedder at the query address reports, at ``/api/ps``, the model in GPU memory (``gpu``) or half of it
    there (``partial``). A new question is embedded there and answered with its vector (the kiln, where the shared
    runner's would be the forge): the semantic search is available, and ``gov retrieve`` ends with exit code 0, no
    traceback and its semantic facet available. The vector is cached (the file beside the store changes), and asked
    again once the embedder reports the model on the CPU, the same answer is served without asking the embedder the
    question again. The question is never sent to the shared runner.

    Rewrite-Reason: DEC-1033 (owner, 2026-11-02, item 2 (b) replacing DEC-798; item 3). Before: the ``gpu`` and
    ``partial`` cases of ``test_an_embedder_at_the_cpu_address_that_does_not_report_the_model_on_the_cpu_gives_no_query_vector``
    required no vector from a query embedder that reported the GPU; DEC-1033 accepts a question's vector from any
    device, so these two expect the answer instead. What they kept: the question goes to the query embedder only,
    never to the shared runner; ``gov retrieve`` stays clean."""
    project = S.semantic_project(box, tmp_path / "p", shared, cpu=cpu)
    env = S.embed_env(box, shared, cpu)
    warm, done = S.drive_run(box, project, env, ("search", OTHER))
    assert not S.clean(done), done.describe()
    beside = {rel: S.sha256(project / rel) for rel in S.runtime_others(project)}
    cpu.ps, sent = reported, cpu.asked_for(QUESTION)
    answers, done = S.drive_run(box, project, env, ("search", QUESTION))
    assert not S.clean(done), f"the read was not clean ({', '.join(S.clean(done))})\n{done.describe()}"
    assert cpu.asked_for(QUESTION) > sent, f"the query embedder reports {reported!r} and was not asked the question"
    assert answers[0].get("available") is True and _nearest(answers[0]) == [S.KILN], (
        f"the query address reports {reported!r}, and the search did not answer with that embedder's vector (the "
        f"kiln): available {answers[0].get('available')!r}, reason {answers[0].get('reason')!r}, nearest "
        f"{S.hits_of(answers[0])[:2]}")
    after = {rel: S.sha256(project / rel) for rel in S.runtime_others(project)}
    assert after != beside, f"the vector computed on {reported!r} was not cached: no file beside the store changed"
    run = S.gov(box, "retrieve", "--json", "--root", project, PHRASE, env=env)
    assert not S.clean(run), f"gov retrieve was not clean ({', '.join(S.clean(run))})\n{run.describe()}"
    assert (S.facets_of(run).get("semantic") or {}).get("available") is True, \
        f"the query address reports {reported!r}, and gov retrieve's semantic facet is not available: {S.facets_of(run)}"
    cpu.ps, asked = None, cpu.asked_for(QUESTION)
    again, done = S.drive_run(box, project, env, ("search", QUESTION))
    assert not S.clean(done), done.describe()
    assert S.hits_of(again[0]) == S.hits_of(answers[0]), \
        f"asked again, the answer changed: {S.hits_of(again[0])[:3]} (first: {S.hits_of(answers[0])[:3]})"
    assert cpu.asked_for(QUESTION) == asked, "the vector cached from the first read was not served: the question was asked again"
    assert not S.sent_for([shared], PHRASE), \
        f"the question was sent to the shared runner: {S.sent_for([shared], PHRASE)}"
    _no_option_and_on_gpu(shared)


@STAND_IN
@pytest.mark.parametrize("reported", ("nothing", "other-model"))
def test_an_embedder_at_the_query_address_that_does_not_report_the_model_loaded_gives_no_query_vector(
        box, shared, cpu, tmp_path, reported):
    """*Red.* The embedder at the query address reports, at ``/api/ps``, nothing (``nothing``), or only another model
    (``other-model``, on the CPU). A new question then gets no query vector: the semantic search is unavailable with a
    reason and no hit, ``gov retrieve`` ends with exit code 0 and no traceback, its semantic facet is unavailable with
    a reason and the lexical route answers; nothing is cached (no file beside the store changes); the question is
    never sent to the shared runner instead. Once the embedder reports the model loaded (here on the CPU), the
    question is embedded there and answered with its vector (the kiln). Today the question is answered by the shared
    runner at OLLAMA_HOST.

    Rewrite-Reason: DEC-811 (orchestrator, delegated, 2026-10-19), PKG-W2-54-4-1 (a): ``gov retrieve`` asks PHRASE, a
    phrase the kiln note holds, where it asked QUESTION, which no note holds as a phrase (so the lexical route had no
    evidence to give whatever the semantic facet did); the no-fallback check looks for PHRASE, which every text sent
    for either read ends with. The lexical route and every other assertion are unchanged.

    Rewrite-Reason: DEC-1033 (owner, 2026-11-02, item 2 (b) replacing DEC-798; item 3): renamed from
    ``test_an_embedder_at_the_cpu_address_that_does_not_report_the_model_on_the_cpu_gives_no_query_vector``, which
    stated DEC-798's rule; its ``gpu`` and ``partial`` cases moved to
    ``test_a_question_s_vector_from_the_query_embedder_is_used_whatever_device_it_reports_the_model_on``. These two
    cases and every assertion of theirs are unchanged."""
    project = S.semantic_project(box, tmp_path / "p", shared, cpu=cpu)
    env = S.embed_env(box, shared, cpu)
    warm, done = S.drive_run(box, project, env, ("search", OTHER))
    assert not S.clean(done), done.describe()
    beside = {rel: S.sha256(project / rel) for rel in S.runtime_others(project)}
    cpu.ps, contacted = reported, len(cpu.requests)
    answers, done = S.drive_run(box, project, env, ("search", QUESTION))
    assert not S.clean(done), f"the read was not clean ({', '.join(S.clean(done))})\n{done.describe()}"
    faults = S.unavailable_with_reason(answers[0])
    assert not faults, (f"the query address reports {reported!r}, yet the search answered ({', '.join(faults)}); "
                        f"nearest {S.hits_of(answers[0])[:2]}")
    run = S.gov(box, "retrieve", "--json", "--root", project, PHRASE, env=env)
    assert not S.clean(run), f"gov retrieve was not clean ({', '.join(S.clean(run))})\n{run.describe()}"
    facets = S.facets_of(run)
    assert not S.unavailable_with_reason(facets.get("semantic") or {}), \
        f"gov retrieve's semantic facet is not unavailable with a reason: {facets.get('semantic')}"
    assert (facets.get("lexical") or {}).get("available") is True and run.envelope()["result"].get("evidence"), \
        f"the lexical route did not answer: {facets.get('lexical')}"
    assert len(cpu.requests) > contacted, "the premise: the reads never asked the embedder at the query address"
    assert not S.sent_for([shared], PHRASE), \
        f"the question was sent to the shared runner instead: {S.sent_for([shared], PHRASE)}"
    after = {rel: S.sha256(project / rel) for rel in S.runtime_others(project)}
    assert after == beside, f"a read that got no query vector changed the files beside the store: {S.tree_change(beside, after)}"
    cpu.ps, sent = None, cpu.asked_for(QUESTION)
    answers, done = S.drive_run(box, project, env, ("search", QUESTION))
    assert not S.clean(done), done.describe()
    assert cpu.asked_for(QUESTION) > sent, "once the model is reported loaded, the question was not embedded there"
    assert answers[0].get("available") is True and _nearest(answers[0]) == [S.KILN], \
        f"once the model is reported loaded, the answer is not the query embedder's vector: {S.hits_of(answers[0])[:2]}"
    assert not S.sent_for([shared], QUESTION), "the question was sent to the shared runner"


# ---- 3. the cache key names the device -------------------------------------------------------------------------------

@STAND_IN
def test_a_vector_cached_under_round_3_s_key_is_never_served(box, shared, cpu, tmp_path):
    """*Red.* The project's cache file holds the question's vector as round 3 wrote it: computed by the shared runner
    (the forge's), under round 3's key (model, revision, sha256 of the exact text sent; both the text round 3 sent and
    the text sent now), in round 3's layout. The read asks the CPU embedder and answers with its vector, the kiln:
    the answer a new store built alike gives, hit for hit and distance for distance; asked again after another text,
    the same. The shared runner is asked nothing. Today round 3's entry is served (the forge).

    Rewrite-Reason: DEC-1033 (item 3; DEC-1042 item 2): the new store built alike (the twin) is built and asked with
    a machine-wide vector cache of its own (as on another machine). Sharing the case's cache, W2-126 would serve the
    project the twin's vector, so the CPU embedder would rightly not be asked and the case would read the outcome
    the cache is for as a failure. The assertions are unchanged."""
    twin_shared = S.EmbedderStandIn(device="gpu", targets={QUESTION: S.SUBJECTS[S.FORGE]})
    # Rewrite-Reason: DEC-1065 (1): the twin's query embedder reports the GPU too (a CPU vector is refused, so the
    # reference answer would be empty); the round-3 entry is still the shared runner's, never served.
    twin_cpu = S.EmbedderStandIn(device="gpu", targets={QUESTION: S.SUBJECTS[S.KILN]})
    twin_cache = tmp_path / "twin-vector-cache"
    try:
        twin = S.semantic_project(box, tmp_path / "twin", twin_shared, cpu=twin_cpu, cache=twin_cache)
        answers, done = S.drive_run(box, twin, S.embed_env(box, twin_shared, twin_cpu, cache=twin_cache),
                                    ("search", QUESTION))
        assert not S.clean(done), done.describe()
        reference, sent = answers[0], S.sent_for([twin_shared, twin_cpu], QUESTION)
    finally:
        twin_shared.close()
        twin_cpu.close()
    assert sent, "the premise: the question was never sent to be embedded"
    project = S.semantic_project(box, tmp_path / "p", shared, cpu=cpu)
    planted = S.plant_round_3_entry(project, [S.ROUND_3_PREFIX + QUESTION, *sent], S.word_vector(S.SUBJECTS[S.FORGE]))
    assert S.runtime_others(project) == [planted.relative_to(project).as_posix()], S.runtime_others(project)
    env = S.embed_env(box, shared, cpu)
    first, done = S.drive_run(box, project, env, ("search", QUESTION))
    assert not S.clean(done), f"the read was not clean ({', '.join(S.clean(done))})\n{done.describe()}"
    assert first[0].get("available") is True and _nearest(first[0]) == [S.KILN], (
        f"the read served the vector cached by the shared runner under round 3's key (nearest "
        f"{S.hits_of(first[0])[:2]}), not the CPU embedder's (the kiln)")
    assert cpu.asked_for(QUESTION) >= 1, "the CPU embedder was never asked the question"
    assert S.hits_of(first[0]) == S.hits_of(reference), (
        f"the answer is not the one a new store gives\nnew store: {S.hits_of(reference)[:3]}\n"
        f"here:      {S.hits_of(first[0])[:3]}")
    S.drive_run(box, project, env, ("search", OTHER))
    again, done = S.drive_run(box, project, env, ("search", QUESTION))
    assert not S.clean(done) and S.hits_of(again[0]) == S.hits_of(reference), \
        f"asked again after another text: {S.hits_of(again[0])[:3]}"
    run = S.gov(box, "retrieve", "--json", "--root", project, QUESTION, env=env)
    assert not S.clean(run) and (S.facets_of(run).get("semantic") or {}).get("available") is True, run.describe()
    assert not S.sent_for([shared], QUESTION), "the question was sent to the shared runner"


# ---- 4. a read never starts an embedder (DEC-1065 (1)) -------------------------------------------------------------

# Rewrite-Reason: DEC-1065 (1) replaces the start on demand (DEC-260, DEC-261, DEC-1033's query embedder started by a
# read): ``ensure_*`` is a health check only, and only an explicit restart starts a server. The two cases whose whole
# premise was a read starting the query embedder become the refusal: with nothing at the query embedder's address and
# the stand-in ``ollama`` where DEC-260 looks, a read runs no executable, its semantic part is unavailable, named
# ``EMBEDDER_UNAVAILABLE``, it answers by keywords, and the question goes to no other embedder. What they also guarded
# (one read, then another, and two reads at once, all answered; the question never sent to the shared runner) is kept.
UNAVAILABLE = "EMBEDDER_UNAVAILABLE"


def _started_nothing(daemons):
    assert not daemons.records("exec"), f"a read ran the Ollama executable (DEC-1065 (1)): {daemons.records('exec')}"
    assert not daemons.serves(), f"a read started an embedder: {daemons.serves()}"


def _named_unavailable_with_keywords(run, text):
    assert not S.clean(run), f"the read of {text!r} was not clean ({', '.join(S.clean(run))})\n{run.describe()}"
    facets = S.facets_of(run)
    semantic = facets.get("semantic") or {}
    assert not S.unavailable_with_reason(semantic) and UNAVAILABLE in semantic["reason"], \
        f"the read of {text!r}: its semantic part is not unavailable, named {UNAVAILABLE}: {semantic}"
    assert (facets.get("lexical") or {}).get("available") is True and run.envelope()["result"].get("evidence"), \
        f"the read of {text!r} did not answer by keywords: {facets}"


@STAND_IN
@pytest.mark.parametrize("place", S.EXECUTABLE_PLACES)
def test_a_read_with_nothing_at_the_query_address_starts_nothing_and_answers_by_keywords(
        box, shared, daemons, tmp_path, place):
    """Nothing answers at the query embedder's address; the stand-in ``ollama`` is where DEC-260 looks (``place``).
    ``gov retrieve`` runs no executable; its semantic part is unavailable, named ``EMBEDDER_UNAVAILABLE``; it answers
    by keywords; the question is not sent to the shared runner; a second read starts nothing either. The semantic
    search is unavailable with a reason, and no embedder is started anywhere.

    Rewrite-Reason: DEC-1065 (1) replaces the start on demand: renamed from
    ``test_a_read_starts_the_query_embedder_at_its_address_and_never_stops_it``."""
    address = f"127.0.0.1:{S._dead_port()}"
    project = S.semantic_project(box, tmp_path / "p", shared, cpu=address)
    env = daemons.env(S.embed_env(box, shared, address), place)
    for text in (PHRASE, OTHER):
        run = daemons.run(S.gov_argv("retrieve", "--json", "--root", project, text), cwd=box.workdir / "elsewhere",
                          env=env)
        _named_unavailable_with_keywords(run, text)
        _started_nothing(daemons)
    _no_semantic_answer_and_no_fallback(box, shared, daemons, project, env, address)
    _started_nothing(daemons)
    assert not S.sent_for([shared], QUESTION) and not S.sent_for([shared], OTHER), "a question went to the shared runner"
    _no_option_and_on_gpu(shared)


@STAND_IN
def test_two_reads_at_once_with_nothing_at_the_query_address_start_nothing_and_both_answer_by_keywords(
        box, shared, daemons, tmp_path):
    """Two ``gov retrieve`` started together, nothing at the query embedder's address, the stand-in executable at
    ``GOV_OLLAMA_BIN``: both end with exit code 0, each names its semantic part unavailable
    (``EMBEDDER_UNAVAILABLE``) and answers by keywords; no executable ran; no question reached the shared runner.

    Rewrite-Reason: DEC-1065 (1) replaces the start on demand: renamed from
    ``test_two_reads_at_once_leave_one_query_embedder_serving_and_both_get_their_answer``."""
    address = f"127.0.0.1:{S._dead_port()}"
    project = S.semantic_project(box, tmp_path / "p", shared, cpu=address)
    env = daemons.env(S.embed_env(box, shared, address), "GOV_OLLAMA_BIN")
    waits = [daemons.start(S.gov_argv("retrieve", "--json", "--root", project, text), cwd=box.workdir / "elsewhere",
                           env=env) for text in (PHRASE, OTHER)]
    runs = [wait(S.CALL_TIMEOUT_S) for wait in waits]
    for text, run in zip((PHRASE, OTHER), runs):
        _named_unavailable_with_keywords(run, text)
    _started_nothing(daemons)
    assert not S.sent_for([shared], PHRASE) and not S.sent_for([shared], OTHER), "a question went to the shared runner"


def _no_semantic_answer_and_no_fallback(box, shared, daemons, project, env, address):
    # Rewrite-Reason: DEC-811 (orchestrator, delegated, 2026-10-19), PKG-W2-54-4-1 (a): ``gov retrieve`` asks PHRASE,
    # a phrase the kiln note holds, where it asked QUESTION, which no note holds as a phrase; the no-fallback check
    # looks for PHRASE, which the texts sent for both reads end with. Every other assertion is unchanged.
    run = daemons.run(S.gov_argv("retrieve", "--json", "--root", project, PHRASE), cwd=box.workdir / "elsewhere",
                      env=env)
    assert not S.clean(run), f"the read was not clean ({', '.join(S.clean(run))})\n{run.describe()}"
    facets = S.facets_of(run)
    faults = S.unavailable_with_reason(facets.get("semantic") or {})
    assert not faults, f"the semantic facet is not unavailable with a reason ({', '.join(faults)}): {facets}"
    assert (facets.get("lexical") or {}).get("available") is True and run.envelope()["result"].get("evidence"), \
        f"the other routes did not answer: {facets}"
    answers, done = S.drive_run(box, project, env, ("search", QUESTION), timeout=S.CALL_TIMEOUT_S)
    assert not S.clean(done) and not S.unavailable_with_reason(answers[0]), \
        f"the semantic search is not unavailable with a reason: {answers and answers[0]}\n{done.describe()}"
    assert not S.sent_for([shared], PHRASE), \
        f"the question was sent to the shared runner instead: {S.sent_for([shared], PHRASE)}"
    elsewhere =[entry for entry in daemons.serves()
                 if S.host_of(entry["env"].get("OLLAMA_HOST") or S.SHARED_HOST_DEFAULT) != S.host_of(address)]
    assert not elsewhere, f"an embedder was started at another address: {elsewhere}"


@STAND_IN
def test_an_address_held_by_something_that_is_not_an_embedder_gives_no_semantic_answer_and_no_fallback(
        box, shared, daemons, tmp_path):
    """*Red.* The CPU embedder's address is held by a listener that does not answer as Ollama (HTTP 404 to every
    request); the stand-in executable is at ``GOV_OLLAMA_BIN``. ``gov retrieve`` ends with exit code 0 and no
    traceback; its semantic facet is unavailable with a reason, its lexical route answers; the semantic search is
    unavailable with a reason; the question is not sent to the shared runner, and no embedder is started at another
    address. Today the shared runner answers the question."""
    listener = S.NotAnEmbedder()
    try:
        project = S.semantic_project(box, tmp_path / "p", shared, cpu=listener.host)
        env = daemons.env(S.embed_env(box, shared, listener.host), "GOV_OLLAMA_BIN")
        _no_semantic_answer_and_no_fallback(box, shared, daemons, project, env, listener.host)
    finally:
        listener.close()


@STAND_IN
def test_with_no_executable_and_nothing_at_the_cpu_address_the_semantic_facet_is_unavailable_and_the_rest_answers(
        box, shared, daemons, tmp_path):
    """*Red.* Nothing answers at the CPU embedder's address and no ``ollama`` is where DEC-260 looks (no
    ``GOV_OLLAMA_BIN``, none on PATH, none under HOME): as with a listener that is not an embedder, exit code 0, no
    traceback, the semantic facet unavailable with a reason, the other routes answering, no fallback to the shared
    runner. Today the shared runner answers the question."""
    address = f"127.0.0.1:{S._dead_port()}"
    project = S.semantic_project(box, tmp_path / "p", shared, cpu=address)
    env = daemons.env(S.embed_env(box, shared, address), None)
    _no_semantic_answer_and_no_fallback(box, shared, daemons, project, env, address)
    assert not daemons.records("exec"), "an executable ran though none was where DEC-260 looks"


# ---- 6. W1-21's hit@5 with CPU query vectors, recorded in the change record ----------------------------------------

FIGURE = r"(?<![\w.])(\d{2,3}\.\d+)(?![\w.])"


def _headline(line):
    """The figure ``line`` states as W1-21's hit@5 (the overall mean): the first figure written with decimals after
    ``hit@5``, before any per-class list (``per class``, ``per-class``); None when there is none."""
    before_classes = re.split(r"per[- ]class", line, maxsplit=1, flags=re.I)[0]
    figures = re.findall(FIGURE, before_classes.split("hit@5", 1)[-1]) if "hit@5" in before_classes else []
    return float(figures[0]) if figures else None


def test_the_change_record_states_w1_21_s_hit_at_5_with_cpu_query_vectors_at_or_above_80():
    """*Red.* The change record has a line that names W1-21, ``hit@5`` and CPU query vectors and states the measured
    figure (a mean, written with its decimals, for example ``81.67``) at or above the pass line of 80 (DEC-414); a line
    naming round 3's GPU measurement (``5f038b47``) does not count. The figure itself is W1-21's own case, run by the
    lead (README, "Round 4"). Today no such line exists.

    Rewrite-Reason: DEC-811 (orchestrator, delegated, 2026-10-19), ride-along (DEC-802): the figure read is W1-21's
    headline hit@5, the first figure with decimals after ``hit@5`` and before any per-class list, on every such line,
    where any figure from 80 to 100 on the line counted before (so a per-class figure such as
    ``failed-approaches 100.0`` met it with a headline below 80). The pass line stays 80."""
    path = S.REPO_ROOT / S.CHANGE_RECORD_REL
    assert path.is_file(), f"there is no {S.CHANGE_RECORD_REL}"
    lines = [line for line in path.read_text(encoding="utf-8").splitlines()
             if "W1-21" in line and "hit@5" in line and "CPU" in line and re.search(r"query[- ]vector", line, re.I)
             and "5f038b47" not in line]
    assert lines, (f"{S.CHANGE_RECORD_REL} has no line naming W1-21, hit@5 and CPU query vectors (the figure of "
                   "KPI success 6)")
    headlines = {line: _headline(line) for line in lines}
    stated = [figure for figure in headlines.values() if figure is not None]
    assert stated, (f"no line naming W1-21's hit@5 with CPU query vectors states its headline figure (with decimals, "
                    f"after hit@5 and before any per-class list): {lines}")
    assert all(80.0 <= figure <= 100.0 for figure in stated), \
        f"W1-21's headline hit@5 with CPU query vectors is not at or above 80: {headlines}"
