"""W2-199, success line 9 (RT-4, zero GPU spill).

A run of kind ``embedder`` or ``reranker`` needs ``--gpu-need-mib <n>`` (else ``RESOURCE_ARGUMENTS_INVALID``, exit 2,
nothing runs) and starts only when the GPU's used MiB plus the need is within ``gpu_budget_mib`` (0.875 x the GPU's total:
21,504 of the stand-in's 24,576 MiB); otherwise it waits (a ``wait`` event of reason ``gpu``, room false); with no GPU it
is refused (exit 3, the command never starts, stderr says embedding and reranking jobs are refused here and memory is
unavailable); nothing offers or selects the CPU (the run's environment names its need in ``GOV_GPU_NEED_MIB`` and sets no
CPU-device variable); each watch pass appends one ``gpu`` event (``used_mib``, ``total_mib``, ``budget_mib``, ``spill``)
and state.json carries the last reading.

The test designer's readings. The ticket's Verify sentence gives used 20,000 with a need of 4,000 and of 2,000 as
admitted, which is not within the budget 21,504 (24,000 and 22,000); the cases here are: used 10,000 + need 4,000
(admitted), used 19,504 + need 2,000 (exactly the budget, admitted), used 19,505 + need 2,000 and used 20,500 + need 2,000
(held). "No CPU-naming variable" is read as: no variable whose name has CPU in it other than ``GOV_HEAVY_CPUS`` (the slot's
own CPU set, success lines 3 and 10), no value equal to ``cpu`` and no ``CUDA_VISIBLE_DEVICES`` of ``""`` or ``-1``.
state.json's last GPU reading is looked for as an object with ``used_mib`` and ``spill`` anywhere in it.
"""

from __future__ import annotations

import re

import pytest

import w2_199_support as s

TOTAL, BUDGET = 24_576, 21_504


@pytest.mark.parametrize("kind", ["embedder", "reranker"])
def test_s9_a_gpu_kind_without_gpu_need_mib_is_refused_with_exit_2_and_nothing_runs(box, kind):
    box.gpu(TOTAL, 1000)
    job = box.start("a", kind=kind, hold=False)
    code, out, err = job.finish(timeout=10)
    assert code == 2, f"--slot {kind} with no --gpu-need-mib: exit {code}, not 2\n{err[-1500:]}"
    assert "RESOURCE_ARGUMENTS_INVALID" in out + err, f"the refusal does not name RESOURCE_ARGUMENTS_INVALID:\n{out}{err}"
    assert not job.mark.exists(), "the command ran"


@pytest.mark.parametrize("kind,used,need", [("embedder", 10_000, 4_000), ("reranker", 19_504, 2_000)],
                         ids=["well-within", "exactly-the-budget"])
def test_s9_a_need_within_the_budget_is_admitted_at_once_with_its_need_in_the_environment(box, kind, used, need):
    assert used + need <= BUDGET
    box.gpu(TOTAL, used)
    job = box.start("a", kind=kind, opts=("--gpu-need-mib", str(need)), hold=False)
    job.must_start(3.0)
    assert job.env().get("GOV_GPU_NEED_MIB") == str(need), f"GOV_GPU_NEED_MIB: {job.env().get('GOV_GPU_NEED_MIB')!r}"
    assert job.finish()[0] == 0


@pytest.mark.parametrize("used,need", [(19_505, 2_000), (20_500, 2_000)], ids=["one-mib-over", "well-over"])
def test_s9_a_need_over_the_budget_waits_with_a_gpu_event_then_starts_when_the_gpu_frees(box, used, need):
    assert used + need > BUDGET
    box.gpu(TOTAL, used)
    job = box.start("a", kind="embedder", opts=("--gpu-need-mib", str(need)), hold=False)
    assert job.held_for(2.5), "the run started over the GPU budget"
    waits = box.events("wait", pid=job.pid)
    assert waits and all(w.get("reason") == "gpu" and w.get("room") is False for w in waits), (
        f"the wait events of a run held by the GPU: {waits}")
    assert len(waits) == 1, f"one `wait` per reason change: {waits}"
    box.gpu(TOTAL, 10_000)
    job.must_start(3.0)
    assert job.finish()[0] == 0


def test_s9_with_no_nvidia_smi_the_run_is_refused_with_exit_3_the_refusal_text_and_no_command(box):
    box.no_gpu()
    job = box.start("a", kind="embedder", opts=("--gpu-need-mib", "1000"), hold=False)
    code, out, err = job.finish(timeout=10)
    text = out + err
    assert code == 3, f"no GPU: exit {code}, not 3\n{text[-1500:]}"
    assert not job.mark.exists(), "the command started with no GPU"
    assert re.search(r"embed", text, re.I) and re.search(r"rerank", text, re.I) and re.search(r"refus", text, re.I), (
        f"the refusal does not say embedding and reranking jobs are refused here:\n{text}")
    assert re.search(r"memory[^.\n]{0,40}unavailable|unavailable[^.\n]{0,40}memory", text, re.I), (
        f"the refusal does not say memory is unavailable:\n{text}")


def test_s9_nothing_offers_or_selects_the_cpu_in_the_runs_environment(box):
    box.gpu(TOTAL, 1000)
    job = box.start("a", kind="embedder", opts=("--gpu-need-mib", "1000"), hold=False)
    job.must_start(3.0)
    env = job.env()
    assert env.get("GOV_GPU_NEED_MIB") == "1000"
    cpu_named = sorted(name for name in env if "CPU" in name.upper() and name != "GOV_HEAVY_CPUS")
    assert not cpu_named, f"the environment names the CPU: {cpu_named}"
    assert not [name for name, value in env.items() if value.strip().lower() == "cpu"], "a variable selects the CPU"
    assert env.get("CUDA_VISIBLE_DEVICES") not in ("", "-1"), f"CUDA_VISIBLE_DEVICES={env.get('CUDA_VISIBLE_DEVICES')!r}"
    assert job.finish()[0] == 0


def test_s9_three_watch_passes_below_the_budget_log_three_gpu_events_with_spill_false(box):
    box.gpu(TOTAL, 10_000)
    box.passes(3)
    events = box.events("gpu")
    assert len(events) == 3, f"{len(events)} `gpu` events after three passes: {box.log()}"
    for event in events:
        assert (event.get("used_mib"), event.get("total_mib"), event.get("budget_mib")) == (10_000, TOTAL, BUDGET), event
        assert event.get("spill") is False, f"spill below the budget: {event}"
    reading = s.find_dict_with(box.state(), ("used_mib", "spill"))
    assert reading is not None and reading["used_mib"] == 10_000 and reading["spill"] is False, (
        f"state.json carries no last GPU reading (an object with used_mib and spill): {box.state()}")


def test_s9_a_gpu_over_its_budget_is_a_spill_in_the_gpu_event(box):
    box.gpu(TOTAL, 22_000)
    box.run_pass()
    events = box.events("gpu")
    assert len(events) == 1 and events[0].get("used_mib") == 22_000 and events[0].get("spill") is True, (
        f"the `gpu` event of a GPU at 22,000 of the budget 21,504 MiB: {events}")
