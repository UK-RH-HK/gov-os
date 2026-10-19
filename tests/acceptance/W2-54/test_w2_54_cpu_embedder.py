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
CHUNK_PHRASES = {rel: text.split("\n\n", 1)[1].split(";")[0].split(" in ")[0].strip() for rel, text in S.SUBJECTS.items()}


@pytest.fixture()
def shared():
    """The shared runner: round 2's stand-in at OLLAMA_HOST, its model on the GPU; it sends the question to the
    forge, so an answer from it shows."""
    stand_in = S.EmbedderStandIn(device="gpu", targets={QUESTION: S.SUBJECTS[S.FORGE]})
    try:
        yield stand_in
    finally:
        stand_in.close()


@pytest.fixture()
def cpu():
    """The CPU embedder: round 2's stand-in at the CPU embedder's address, its model on the CPU; it sends the question
    to the kiln."""
    stand_in = S.EmbedderStandIn(device="cpu", targets={QUESTION: S.SUBJECTS[S.KILN]})
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

@STAND_IN
def test_every_read_sends_its_question_to_the_cpu_embedder_and_nothing_to_the_shared_runner(
        box, shared, cpu, tmp_path):
    """*Red.* With the shared runner at OLLAMA_HOST and the CPU embedder at its address: two ``gov retrieve``, two
    ``gov context``, a semantic search and a retrieval through the public entry each send the CPU embedder at least
    one text to embed (the question) and send the shared runner none; the search's answer is the CPU embedder's
    vector (the kiln, where the shared runner's would be the forge). No request to the shared runner names a runner
    option, and its model stays on the GPU. Today every question goes to OLLAMA_HOST, with ``num_gpu: 0``."""
    project = S.semantic_project(box, tmp_path / "p", shared, S.ticket_files(), cpu=cpu)
    assert shared.embed_requests() and not cpu.embedded(), \
        f"the premise: the index was built through the shared runner only (CPU embedder sent {cpu.embedded()[:2]})"
    env = S.embed_env(box, shared, cpu)
    steps = [("gov", "retrieve", "--json", "--root", project, QUESTION),
             ("gov", "retrieve", "--json", "--root", project, OTHER),
             ("gov", "context", "--json", "--root", project, "TK-W254-TIDES"),
             ("gov", "context", "--json", "--root", project, "TK-W254-BAKERY"),
             ("search", QUESTION), ("retrieve", OTHER)]
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
    assert cpu.asked_for(QUESTION) >= 1 and cpu.asked_for(OTHER) >= 1, "the questions never reached the CPU embedder"
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
@pytest.mark.parametrize("reported", ("gpu", "partial", "nothing", "other-model"))
def test_an_embedder_at_the_cpu_address_that_does_not_report_the_model_on_the_cpu_gives_no_query_vector(
        box, shared, cpu, tmp_path, reported):
    """*Red.* The embedder at the CPU address reports, at ``/api/ps``, the model in GPU memory (``gpu``), half of it
    there (``partial``), nothing (``nothing``), or only another model on the CPU (``other-model``). A new question then
    gets no query vector: the semantic search is unavailable with a reason and no hit, ``gov retrieve`` ends with exit
    code 0 and no traceback, its semantic facet is unavailable with a reason and the lexical route answers; nothing is
    cached (no file beside the store changes); the question is never sent to the shared runner instead. Once the
    embedder reports the model on the CPU, the question is embedded there and answered with its vector (the kiln).
    Today the question is answered by the shared runner at OLLAMA_HOST."""
    project = S.semantic_project(box, tmp_path / "p", shared, cpu=cpu)
    env = S.embed_env(box, shared, cpu)
    warm, done = S.drive_run(box, project, env, ("search", OTHER))
    assert not S.clean(done), done.describe()
    beside = {rel: S.sha256(project / rel) for rel in S.runtime_others(project)}
    cpu.ps, contacted = reported, len(cpu.requests)
    answers, done = S.drive_run(box, project, env, ("search", QUESTION))
    assert not S.clean(done), f"the read was not clean ({', '.join(S.clean(done))})\n{done.describe()}"
    faults = S.unavailable_with_reason(answers[0])
    assert not faults, (f"the CPU address reports {reported!r}, yet the search answered ({', '.join(faults)}); "
                        f"nearest {S.hits_of(answers[0])[:2]}")
    run = S.gov(box, "retrieve", "--json", "--root", project, QUESTION, env=env)
    assert not S.clean(run), f"gov retrieve was not clean ({', '.join(S.clean(run))})\n{run.describe()}"
    facets = S.facets_of(run)
    assert not S.unavailable_with_reason(facets.get("semantic") or {}), \
        f"gov retrieve's semantic facet is not unavailable with a reason: {facets.get('semantic')}"
    assert (facets.get("lexical") or {}).get("available") is True and run.envelope()["result"].get("evidence"), \
        f"the lexical route did not answer: {facets.get('lexical')}"
    assert len(cpu.requests) > contacted, "the premise: the reads never asked the embedder at the CPU address"
    assert not S.sent_for([shared], QUESTION), \
        f"the question was sent to the shared runner instead: {S.sent_for([shared], QUESTION)}"
    after = {rel: S.sha256(project / rel) for rel in S.runtime_others(project)}
    assert after == beside, f"a read that got no CPU vector changed the files beside the store: {S.tree_change(beside, after)}"
    cpu.ps, sent = None, cpu.asked_for(QUESTION)
    answers, done = S.drive_run(box, project, env, ("search", QUESTION))
    assert not S.clean(done), done.describe()
    assert cpu.asked_for(QUESTION) > sent, "once the model is on the CPU, the question was not embedded there"
    assert answers[0].get("available") is True and _nearest(answers[0]) == [S.KILN], \
        f"once the model is on the CPU, the answer is not the CPU embedder's vector: {S.hits_of(answers[0])[:2]}"
    assert not S.sent_for([shared], QUESTION), "the question was sent to the shared runner"


# ---- 3. the cache key names the device -------------------------------------------------------------------------------

@STAND_IN
def test_a_vector_cached_under_round_3_s_key_is_never_served(box, shared, cpu, tmp_path):
    """*Red.* The project's cache file holds the question's vector as round 3 wrote it: computed by the shared runner
    (the forge's), under round 3's key (model, revision, sha256 of the exact text sent; both the text round 3 sent and
    the text sent now), in round 3's layout. The read asks the CPU embedder and answers with its vector, the kiln:
    the answer a new store built alike gives, hit for hit and distance for distance; asked again after another text,
    the same. The shared runner is asked nothing. Today round 3's entry is served (the forge)."""
    twin_shared = S.EmbedderStandIn(device="gpu", targets={QUESTION: S.SUBJECTS[S.FORGE]})
    twin_cpu = S.EmbedderStandIn(device="cpu", targets={QUESTION: S.SUBJECTS[S.KILN]})
    try:
        twin = S.semantic_project(box, tmp_path / "twin", twin_shared, cpu=twin_cpu)
        answers, done = S.drive_run(box, twin, S.embed_env(box, twin_shared, twin_cpu), ("search", QUESTION))
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


# ---- 4. started on demand, on its own port, never stopped -----------------------------------------------------------

def _started_alone_at(daemons, address):
    """The runs of ``serve``: each told to serve at ``address`` and to use no GPU."""
    serves = daemons.serves()
    assert serves, "the read started no Ollama executable"
    for entry in serves:
        told = S.host_of(entry["env"].get("OLLAMA_HOST") or S.SHARED_HOST_DEFAULT)
        assert told == S.host_of(address), \
            f"the executable was told to serve at {told}, not at the CPU embedder's address {address}: {entry}"
        assert S.gpu_hidden(entry["env"]), (
            f"the executable was started without being told to use no GPU (CUDA_VISIBLE_DEVICES=-1, or "
            f"OLLAMA_LLM_LIBRARY=cpu): {entry['env']}")
        assert entry["argv"] == ["serve"], f"the executable was run as {entry['argv']}"
    return serves


def _never_stopped(daemons, address):
    serving = daemons.serving()
    assert len([entry for entry in serving if daemons.alive(entry["pid"])]) == 1, (
        f"after the reads, not exactly one started embedder serves: {serving} "
        f"(alive: {[daemons.alive(entry['pid']) for entry in serving]})")
    assert not daemons.records("signal"), f"gov stopped the embedder it started: {daemons.records('signal')}"
    reply = S.answers(address)
    assert reply and reply[0] == 200, f"after the reads nothing answers at the CPU embedder's address: {reply}"


@STAND_IN
@pytest.mark.parametrize("place", S.EXECUTABLE_PLACES)
def test_a_read_starts_the_cpu_embedder_at_its_address_with_no_gpu_and_never_stops_it(
        box, shared, daemons, tmp_path, place):
    """*Red.* Nothing answers at the CPU embedder's address; the stand-in ``ollama`` is where DEC-260 looks
    (``place``: ``GOV_OLLAMA_BIN``, ``PATH``, ``~/.local/ollama/bin/ollama``). ``gov retrieve`` starts it as ``serve``,
    told to serve at that address (its OLLAMA_HOST) and to use no GPU, asks it the question and gets the semantic
    answer, with exit code 0; the shared runner is asked nothing. After the read the started embedder still serves and
    was sent no stop; a second read uses it and starts nothing. Today no read starts anything at that address."""
    address = f"127.0.0.1:{S._dead_port()}"
    project = S.semantic_project(box, tmp_path / "p", shared, cpu=address)
    env = daemons.env(S.embed_env(box, shared, address), place)
    run = daemons.run(S.gov_argv("retrieve", "--json", "--root", project, QUESTION), cwd=box.workdir / "elsewhere",
                      env=env)
    assert not S.clean(run), f"the read was not clean ({', '.join(S.clean(run))})\n{run.describe()}"
    semantic = S.facets_of(run).get("semantic") or {}
    assert semantic.get("available") is True, \
        f"the read did not get its semantic answer: {semantic}; the executable's runs: {daemons.records('exec')}"
    _started_alone_at(daemons, address)
    assert daemons.asked(QUESTION) >= 1, "the started embedder was never asked the question"
    assert not S.sent_for([shared], QUESTION), "the question was sent to the shared runner"
    _never_stopped(daemons, address)
    serves = len(daemons.serves())
    again = daemons.run(S.gov_argv("retrieve", "--json", "--root", project, OTHER), cwd=box.workdir / "elsewhere",
                        env=env)
    assert not S.clean(again) and (S.facets_of(again).get("semantic") or {}).get("available") is True, \
        again.describe()
    assert len(daemons.serves()) == serves, "a read started another embedder while one served at the address"
    _never_stopped(daemons, address)
    _no_option_and_on_gpu(shared)


@STAND_IN
def test_two_reads_at_once_leave_one_cpu_embedder_serving_and_both_get_their_answer(
        box, shared, daemons, tmp_path):
    """*Red.* Two ``gov retrieve`` started together, nothing at the CPU embedder's address, the stand-in executable
    at ``GOV_OLLAMA_BIN`` (it takes a second to listen, so both reads find nothing): both end with exit code 0 and
    their semantic answer; every start was told that address and no GPU; afterwards one embedder serves there, and
    nothing stopped it. Today neither read starts anything at that address."""
    address = f"127.0.0.1:{S._dead_port()}"
    project = S.semantic_project(box, tmp_path / "p", shared, cpu=address)
    env = daemons.env(S.embed_env(box, shared, address), "GOV_OLLAMA_BIN")
    waits = [daemons.start(S.gov_argv("retrieve", "--json", "--root", project, text), cwd=box.workdir / "elsewhere",
                           env=env) for text in (QUESTION, OTHER)]
    runs = [wait(S.CALL_TIMEOUT_S) for wait in waits]
    for text, run in zip((QUESTION, OTHER), runs):
        assert not S.clean(run), f"the read of {text!r} was not clean ({', '.join(S.clean(run))})\n{run.describe()}"
        assert (S.facets_of(run).get("semantic") or {}).get("available") is True, \
            f"the read of {text!r} did not get its semantic answer: {S.facets_of(run)}; runs {daemons.records()}"
    _started_alone_at(daemons, address)
    assert daemons.asked(QUESTION) >= 1 and daemons.asked(OTHER) >= 1, "a question never reached the started embedder"
    _never_stopped(daemons, address)
    assert not S.sent_for([shared], QUESTION) and not S.sent_for([shared], OTHER), "a question went to the shared runner"


def _no_semantic_answer_and_no_fallback(box, shared, daemons, project, env, address):
    run = daemons.run(S.gov_argv("retrieve", "--json", "--root", project, QUESTION), cwd=box.workdir / "elsewhere",
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
    assert not S.sent_for([shared], QUESTION), \
        f"the question was sent to the shared runner instead: {S.sent_for([shared], QUESTION)}"
    elsewhere = [entry for entry in daemons.serves()
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

def test_the_change_record_states_w1_21_s_hit_at_5_with_cpu_query_vectors_at_or_above_80():
    """*Red.* The change record has a line that names W1-21, ``hit@5`` and CPU query vectors and states the measured
    figure (a mean, written with its decimals, for example ``81.67``) at or above the pass line of 80 (DEC-414); a line
    naming round 3's GPU measurement (``5f038b47``) does not count. The figure itself is W1-21's own case, run by the
    lead (README, "Round 4"). Today no such line exists."""
    path = S.REPO_ROOT / S.CHANGE_RECORD_REL
    assert path.is_file(), f"there is no {S.CHANGE_RECORD_REL}"
    lines = [line for line in path.read_text(encoding="utf-8").splitlines()
             if "W1-21" in line and "hit@5" in line and "CPU" in line and re.search(r"query[- ]vector", line, re.I)
             and "5f038b47" not in line]
    assert lines, (f"{S.CHANGE_RECORD_REL} has no line naming W1-21, hit@5 and CPU query vectors (the figure of "
                   "KPI success 6)")
    figures = [float(number) for line in lines for number in re.findall(r"(?<![\w.])(\d{2,3}\.\d+)(?![\w.])", line)]
    assert any(80.0 <= figure <= 100.0 for figure in figures), \
        f"no line naming W1-21's hit@5 with CPU query vectors states a figure at or above 80: {lines}"
