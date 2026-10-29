"""Round 4, KPI success 5 on the real models (DEC-798, owner, 2026-10-19, P-W2-40 (b)): on the shared GPU Ollama,
the same text read many times, after different texts and by two sessions at once, gets one vector; the shared runner
is never moved to the CPU; the CPU-only embedder holds the model on the CPU.

**The lead runs these cases, in the lead's session, outside any sandbox** (README, "Round 4", "The cases on the shared
GPU"). They need this machine's Ollama at its default address (``127.0.0.1:11434``) holding ``qwen3-embedding:0.6b``
on the GPU, the real ``ollama`` executable where DEC-260 looks (``GOV_OLLAMA_BIN``, ``PATH``,
``~/.local/ollama/bin/ollama``), ``sqlite_vec`` and ``gitleaks``. Neither address is set: the CPU embedder is at its
default address, ``GOV_QUERY_OLLAMA_HOST``'s default (README, "The interfaces this KPI needs"). Inside a sandbox the
shared server cannot be reached and the GPU is blocked, so nothing measured there is evidence about the GPU.

Marked ``shared_gpu``: a run selects them only with ``-m shared_gpu`` (``conftest.py`` deselects them otherwise).
Selected, they **fail, they do not skip**, when a prerequisite is missing or the shared server does not hold the model
on the GPU. Each case prints what it saw (run with ``-s`` to see it): the CPU embedder's port and its ``size``.
"""

from __future__ import annotations

import pytest

import w2_54_support as S

pytestmark = pytest.mark.shared_gpu

QUESTION = "who fires the glazed bowls"
OTHERS = ("who reads the harbour tide tables", "when are the pear trees pruned", "who smokes the hives in July")


def _models(address):
    """What ``/api/ps`` at ``address`` reports for the pinned model (a list of entries)."""
    reply = S.answers(address, "/api/ps", timeout=10.0)
    assert reply and reply[0] == 200 and isinstance(reply[1], dict), f"/api/ps at {address} did not answer: {reply}"
    return [model for model in reply[1].get("models") or [] if model.get("name", model.get("model")) == S.EMBED_MODEL
            or model.get("model") == S.EMBED_MODEL]


def _on_the_gpu(when):
    models = _models(S.SHARED_HOST_DEFAULT)
    assert models and all(model.get("size_vram") == model.get("size") and model.get("size", 0) > 0
                          for model in models), (
        f"{when}, the shared server at {S.SHARED_HOST_DEFAULT} does not hold {S.EMBED_MODEL} wholly on the GPU "
        f"(size_vram equal to size): {models}")
    return models[0]


def _env(box):
    """This machine's environment with this worktree's ``src/``, and neither embedder's address set."""
    env = S.real_env(box)
    for key in ("OLLAMA_HOST", S.QUERY_HOST_SETTING):
        env.pop(key, None)
    return env


@pytest.fixture(scope="module")
def gpu_project(box, tmp_path_factory):
    """A project of six notes whose index is built through the shared server (on the GPU)."""
    lacking = S.real_embedder_lacking()
    if lacking:
        pytest.fail(f"the shared-GPU cases need {lacking}", pytrace=False)
    env = _env(box)
    project = S.new_repo(tmp_path_factory.mktemp("w2-54-shared-gpu") / "p")
    S.adopt_embedded(project)
    for rel, text in S.SUBJECTS.items():
        S.write(project, rel, text)
    S.commit_all(project)
    report = S.drive_env(box, project, env, ("refresh",), ("load",))[0]
    assert report.get("available") is True, f"the index was not built through the shared server: {report}"
    return project, env


def _search(box, project, env, text, what):
    answers, done = S.drive_run(box, project, env, ("search", text), timeout=600.0)
    assert not S.clean(done), f"{what}: the read was not clean ({', '.join(S.clean(done))})\n{done.describe()}"
    answer = answers[0]
    assert answer.get("available") is True and S.hits_of(answer), f"{what}: the semantic facet gave no answer: {answer}"
    return answer


def _same(answer, reference, what):
    assert S.hits_of(answer) == S.hits_of(reference), (
        f"{what}: one text, two answers on the shared GPU\nfirst: {S.hits_of(reference)[:3]}\n"
        f"here:  {S.hits_of(answer)[:3]}")


def test_shared_gpu_one_text_gets_one_answer_after_other_texts_at_once_and_whatever_the_cache_s_state(
        box, gpu_project):
    """One text read through the semantic search and ``gov retrieve``, after different texts, with the cache cold
    (deleted before each read), warm, and unwritable (``.gov-runtime/`` read-only, no cache file), and by two
    processes at once: one answer (hits, order and distances; one bundle) every time. The shared server holds the
    model on the GPU before and after."""
    project, env = gpu_project
    _on_the_gpu("before the reads")
    S.delete_cache(project)
    reference = _search(box, project, env, QUESTION, "the first read, cold")
    for other in OTHERS:
        S.delete_cache(project)
        _search(box, project, env, other, f"cold, {other!r}")
        S.delete_cache(project)
        _same(_search(box, project, env, QUESTION, f"cold, after {other!r}"), reference, f"cold, after {other!r}")
    for other in OTHERS:
        _search(box, project, env, other, f"warm, {other!r}")
        _same(_search(box, project, env, QUESTION, f"warm, after {other!r}"), reference, f"warm, after {other!r}")
    S.delete_cache(project)
    runtime = project / S.RUNTIME_REL
    with S.ReadOnly(runtime):
        assert S.cannot_create_in(runtime), "the premise: .gov-runtime/ still takes a new file"
        for other in OTHERS:
            _search(box, project, env, other, f"unwritable, {other!r}")
            _same(_search(box, project, env, QUESTION, f"unwritable, after {other!r}"), reference,
                  f".gov-runtime/ read-only, after {other!r}")
    bundles = []
    for other in OTHERS[:2]:
        S.delete_cache(project)
        S.gov(box, "retrieve", "--json", "--root", project, other, env=env, timeout=600.0)
        done = S.gov(box, "retrieve", "--json", "--root", project, QUESTION, env=env, timeout=600.0)
        assert not S.clean(done) and (S.facets_of(done).get("semantic") or {}).get("available") is True, \
            done.describe()
        bundles.append(done.envelope()["result"])
    assert S.canonical(bundles[0]) == S.canonical(bundles[1]), (
        "gov retrieve gave one text two bundles on the shared GPU:\n"
        f"{[item.get('chunk_id') for item in bundles[0].get('evidence') or []]}\n"
        f"{[item.get('chunk_id') for item in bundles[1].get('evidence') or []]}")
    S.delete_cache(project)
    runs = S.at_once(box, project, env, [[("search", OTHERS[0]), ("search", QUESTION)],
                                         [("search", OTHERS[1]), ("search", QUESTION)]], timeout=600.0)
    for number, run in enumerate(runs, start=1):
        assert not S.clean(run), f"concurrent process {number} was not clean\n{run.describe()}"
        answer = S.json.loads(run.stdout.strip().splitlines()[-1])[2]
        _same(answer, reference, f"process {number} of two at once")
    _on_the_gpu("after the reads")


def test_shared_gpu_the_shared_runner_keeps_the_model_on_the_gpu_and_the_cpu_embedder_holds_it_on_the_cpu(
        box, gpu_project):
    """After the index build and a read: the shared server's ``/api/ps`` reports the model with ``size_vram`` equal to
    ``size``; the CPU embedder at its default address reports it with ``size_vram`` 0, and both list the model at one
    revision (the digest of ``/api/tags``). Prints the CPU embedder's port and its size."""
    project, env = gpu_project
    shared = _on_the_gpu("after the index build")
    _search(box, project, env, QUESTION, "a read")
    cpu = _models(S.QUERY_HOST_DEFAULT)
    assert cpu and all(model.get("size_vram") == 0 and model.get("size", 0) > 0 for model in cpu), (
        f"the CPU embedder at {S.QUERY_HOST_DEFAULT} does not hold {S.EMBED_MODEL} wholly on the CPU "
        f"(size_vram 0): {cpu}")
    shared = _on_the_gpu("after the read")
    digests = {}
    for address in (S.SHARED_HOST_DEFAULT, S.QUERY_HOST_DEFAULT):
        reply = S.answers(address, "/api/tags", timeout=10.0)
        assert reply and reply[0] == 200, f"/api/tags at {address} did not answer: {reply}"
        digests[address] = sorted(model.get("digest") for model in reply[1].get("models") or []
                                  if model.get("name") == S.EMBED_MODEL or model.get("model") == S.EMBED_MODEL)
    assert digests[S.SHARED_HOST_DEFAULT] == digests[S.QUERY_HOST_DEFAULT] != [], \
        f"the two embedders list the model at two revisions: {digests}"
    port = S.QUERY_HOST_DEFAULT.rpartition(":")[2]
    print(f"\nW2-54 shared GPU: the CPU embedder serves at {S.QUERY_HOST_DEFAULT} (port {port}); its {S.EMBED_MODEL} "
          f"size {cpu[0]['size']} bytes ({cpu[0]['size'] / 2 ** 30:.2f} GiB), size_vram {cpu[0]['size_vram']}; the "
          f"shared runner at {S.SHARED_HOST_DEFAULT}: size {shared['size']}, size_vram {shared['size_vram']}; "
          f"digest {digests[S.QUERY_HOST_DEFAULT]}")
