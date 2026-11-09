"""S10, S13 and S14: the GPU. A stand-in ``nvidia-smi`` on PATH answers from a planted state; never the real GPU.

S10: a start that declares a GPU need opens only when a GPU's free memory, read with nvidia-smi, is at least the need
plus 10%; no nvidia-smi or no GPU shuts such a start, named; a start with no declared need never reads the GPU
[DEC-950 item 2, DEC-941 item 6].
S13: the gate measures the GPU as it measures CPU and memory: its memory used and total, its utilisation, and which
processes hold it (an embedder, a reranker, other), read once per check; a machine with no GPU or an unreadable one is
named in the answer, never an error [DEC-1030 item 4, DEC-1031 item 4].
S14: each kind of GPU work has a configured share (default: the embedding model first, then one shared reranker, then
the rest), and a job that would push the embedder off the GPU waits (or runs its model on the CPU) instead of
starting; the answer states the GPU room it saw [DEC-1030 items 2 and 4, DEC-1031 item 4].

Interface (README, "The GPU"): ``gov resources --check --gpu-need-mib N [--gpu-kind embedder|reranker|other]``
(kind ``other`` when not given); the margin is the file's ``gpu_margin``; the shares its ``gpu_shares``
(``embedder_mib``, ``reranker_mib``). The room for a job is a GPU's free memory less the unused part of the shares
of the kinds before it; the answer carries ``gpu_room_mib``. The reading's ``gpu`` is ``{"available": true,
"memory_used_mib", "memory_total_mib", "utilisation_pct", "processes": [{"pid", "kind", "used_mib"}]}`` or
``{"available": false, "reason": "..."}``. A process's kind is read from its command line: a word whose file name
begins with ``ollama`` is an embedder, ``rerank`` anywhere a reranker, anything else other.
"""

from __future__ import annotations

import pytest

import w2_20_support as support


def _gpu(total, free, util=3):
    return {"memory.total": total, "memory.used": total - free, "memory.free": free, "utilization.gpu": util}


@pytest.mark.parametrize("gpus, opens", [
    ([_gpu(8192, 1101)], True),
    ([_gpu(8192, 1099)], False),
    ([_gpu(8192, 200), _gpu(8192, 1200)], True),
    ([_gpu(8192, 600), _gpu(8192, 600)], False),
], ids=["free 1101 for a need of 1000 opens", "free 1099 shuts", "the second GPU has room",
        "room only across two GPUs shuts"])
def test_s10_a_declared_gpu_need_opens_only_with_the_need_plus_the_margin_free_on_one_gpu(machine, repo, gpus, opens):
    machine.plant_gpu(gpus=gpus)
    code, envelope, out, err = machine.check(repo, gpu_need_mib=1000)
    if opens:
        support.opened_of(code, envelope, out, err)
    else:
        refused = support.refusal_of(code, envelope, out, err)
        reasons = support.reasons_by_condition(refused)
        assert set(reasons) == {"gpu"}, reasons
        assert support.close_to(reasons["gpu"]["threshold"], 1100, tol=0.5), reasons["gpu"]
    assert machine.gpu_call_list(), "the GPU was not read with nvidia-smi"


@pytest.mark.parametrize("state", ["no nvidia-smi", "no GPU", "an unreadable GPU"])
def test_s10_no_nvidia_smi_or_no_gpu_shuts_a_start_that_declares_a_need_named(machine, repo, state):
    if state == "no GPU":
        machine.plant_gpu(fail="no-gpu")
    elif state == "an unreadable GPU":
        machine.plant_gpu(fail="error")
    refused = support.refusal_of(*machine.check(repo, gpu_need_mib=100))
    reasons = support.reasons_by_condition(refused)
    assert set(reasons) == {"gpu"}, reasons
    assert reasons["gpu"]["reading"] is None, reasons["gpu"]


@pytest.mark.parametrize("planted", [True, False], ids=["a GPU planted", "no nvidia-smi"])
def test_s10_a_start_with_no_declared_need_never_reads_the_gpu(machine, repo, planted):
    if planted:
        machine.plant_gpu(gpus=[_gpu(8192, 0)])  # a full GPU: a read of it would matter
    support.opened_of(*machine.check(repo))
    assert machine.gpu_call_list() == [], f"a start with no GPU need read the GPU: {machine.gpu_call_list()}"


def test_s13_the_reading_measures_gpu_memory_utilisation_and_which_processes_hold_it(machine, repo):
    embedder = machine.live_process(tag="ollama")
    reranker = machine.live_process(tag="gov-rerank-worker")
    other = machine.live_process(tag="w2-20-other-job")
    machine.plant_gpu(gpus=[{"memory.total": 8192, "memory.used": 5000, "utilization.gpu": 37}], apps=[
        {"pid": embedder.pid, "process_name": "/usr/local/bin/ollama", "used_memory": 3000},
        {"pid": reranker.pid, "process_name": "python3", "used_memory": 1500},
        {"pid": other.pid, "process_name": "python3", "used_memory": 500},
    ])

    gpu = machine.read(repo).get("gpu")
    assert isinstance(gpu, dict) and gpu.get("available") is True, f"the reading has no GPU measure: {gpu}"
    assert gpu.get("memory_used_mib") == 5000 and gpu.get("memory_total_mib") == 8192, gpu
    assert gpu.get("utilisation_pct") == 37, gpu
    kinds = {int(p["pid"]): (p.get("kind"), p.get("used_mib")) for p in gpu.get("processes", [])}
    assert kinds == {embedder.pid: ("embedder", 3000), reranker.pid: ("reranker", 1500),
                     other.pid: ("other", 500)}, kinds

    calls = machine.gpu_call_list()
    for query in ("--query-gpu", "--query-compute-apps"):
        assert sum(any(a.startswith(query) for a in call) for call in calls) <= 1, (
            f"the GPU was read more than once in one check ({query}): {calls}")


@pytest.mark.parametrize("state", ["no nvidia-smi", "no GPU", "an unreadable GPU"])
def test_s13_no_gpu_or_an_unreadable_one_is_named_in_the_answer_never_an_error(machine, repo, state):
    if state == "no GPU":
        machine.plant_gpu(fail="no-gpu")
    elif state == "an unreadable GPU":
        machine.plant_gpu(fail="error")
    reading = machine.read(repo)  # exit 0, ok: true (reading_of checks)
    gpu = reading.get("gpu")
    assert isinstance(gpu, dict) and gpu.get("available") is False, gpu
    assert isinstance(gpu.get("reason"), str) and gpu["reason"].strip(), f"the GPU's absence is not named: {gpu}"
    assert support.gate_of(reading)["open"] is True, "a machine without a GPU shut the gate for sessions"


@pytest.mark.parametrize("kind, need, embedder_loaded, room, opens", [
    ("reranker", 4000, False, 5192, True),
    ("reranker", 5000, False, 5192, False),
    ("other", 3000, False, 3192, False),
    ("reranker", 4000, True, 5192, True),
], ids=["a reranker within its room", "a reranker that would push the embedder off",
        "other work behind the embedder and the reranker", "the embedder already loaded"])
def test_s14_a_job_that_would_push_the_embedder_off_the_gpu_waits_and_the_answer_states_the_room(
        machine, repo, kind, need, embedder_loaded, room, opens):
    """Shares: the embedder 3000 MiB, the reranker 2000 MiB, on a GPU of 8192 MiB. Nothing loaded: a reranker's
    room is 8192 - 3000 = 5192, other work's 8192 - 3000 - 2000 = 3192. The embedder loaded (3000 used, its share
    taken): a reranker's room is the 5192 free."""
    machine.open_config(gpu_shares={"embedder_mib": 3000, "reranker_mib": 2000})
    apps = []
    used = 0
    if embedder_loaded:
        embedder = machine.live_process(tag="ollama")
        apps = [{"pid": embedder.pid, "process_name": "/usr/local/bin/ollama", "used_memory": 3000}]
        used = 3000
    machine.plant_gpu(gpus=[{"memory.total": 8192, "memory.used": used, "utilization.gpu": 10}], apps=apps)

    code, envelope, out, err = machine.check(repo, gpu_need_mib=need, gpu_kind=kind)
    if opens:
        answer = support.opened_of(code, envelope, out, err)
    else:
        answer = support.refusal_of(code, envelope, out, err)
        assert set(support.reasons_by_condition(answer)) == {"gpu"}, answer
    assert answer.get("gpu_room_mib") == room, f"the answer does not state the GPU room it saw ({room}): {answer}"
