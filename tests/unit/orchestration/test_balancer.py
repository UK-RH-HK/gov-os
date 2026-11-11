"""The Gov Load Balancer's arithmetic (governance/project/orchestration/tools/dispatch/balancer.py; DEC-1039 (1b),
DEC-1037 (4), DEC-1038 (4)): the limits from the machine, the phases' peaks, the forecast, the pairing and the breach
timer. Pure functions: no process, no file. Run: python3 -m pytest -q tests/unit/orchestration/test_balancer.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "governance/project/orchestration/tools/dispatch"))
import balancer as lb  # noqa: E402

GB = 1024 * 1024  # kB
TODAY = {"cpus": 20, "mem_total_kb": 24607384, "gpu_total_mib": 16303}


# ---- the limits from the machine (DEC-1037 (4)) ---------------------------------------------------------------------

def test_todays_numbers_are_unchanged_on_this_machine():
    d = lb.derive_limits(TODAY)
    assert {k: d[k] for k in lb.DERIVED_KEYS} == {
        "cpu_band": [14, 18], "cpu_margin": 2, "heavy_slots": 3, "heavy_workers": 6, "slots_gpu": 3, "slots_cpu": 2,
        "gpu_headroom_mib": 2048, "rerank_gpu_slots": 2, "gpu_shared_floor_mib": 1019}


def test_todays_numbers_hold_with_the_measured_shares_of_today():
    """The embedders at 5.6 GiB with the desktop, one reranker 3.5 GiB: still 2 reranker GPU slots."""
    d = lb.derive_limits(TODAY, {"embedders_gpu_mib": 5734, "reranker_gpu_mib": 3584})
    assert d["rerank_gpu_slots"] == 2 and d["gpu_headroom_mib"] == 2048


def test_a_bigger_machine_gets_bigger_limits():
    d = lb.derive_limits({"cpus": 32, "mem_total_kb": 64 * GB, "gpu_total_mib": 24564})
    assert d["cpu_band"] == [22, 29] and d["cpu_margin"] == 3
    assert (d["heavy_slots"], d["heavy_workers"]) == (5, 5) and (d["slots_gpu"], d["slots_cpu"]) == (5, 3)
    assert d["gpu_headroom_mib"] == 3085 and d["rerank_gpu_slots"] == 4  # (24564 - 5734 - 3085) // 3584


def test_a_small_machine_without_a_gpu():
    d = lb.derive_limits({"cpus": 8, "mem_total_kb": 16 * GB, "gpu_total_mib": None})
    assert d["cpu_band"] == [6, 7] and d["cpu_margin"] == 1
    assert (d["heavy_slots"], d["heavy_workers"]) == (1, 7) and (d["slots_gpu"], d["slots_cpu"]) == (1, 1)
    assert d["gpu_headroom_mib"] == 0 and d["rerank_gpu_slots"] == 0 and d["how"]["rerank_gpu_slots"] == "no GPU"


def test_an_explicit_number_in_the_config_wins_and_is_reported():
    c = {}
    over = lb.apply_limits(c, {"cpu_band": [12, 16], "rerank_gpu_slots": 2}, lb.derive_limits(TODAY))
    assert c["cpu_band"] == [12, 16] and c["rerank_gpu_slots"] == 2 and c["slots_cpu"] == 2
    assert over == {"cpu_band": ([12, 16], [14, 18])}  # the same number set explicitly is no override


def test_a_machine_change_is_found_and_a_gpu_first_read_is_not_one():
    old = {"cpus": 20, "cores": 10, "mem_total_gb": 23.5, "gpu_known": True, "gpu_name": "RTX", "gpu_total_mib": 16303}
    assert lb.machine_changed(old, dict(old)) == []
    assert lb.machine_changed(old, dict(old, mem_total_gb=31.5, cpus=24)) == ["cpus", "mem_total_gb"]
    assert lb.machine_changed(old, dict(old, gpu_total_mib=24564)) == ["gpu_total_mib"]
    assert lb.machine_changed(dict(old, gpu_known=False, gpu_total_mib=None), old) == []
    assert lb.machine_changed({}, old) == []


# ---- the phases and their peaks -------------------------------------------------------------------------------------

def test_few_samples_keep_todays_floors_and_many_give_the_p95():
    few = [{"jobs": [{"k": "slot", "p": "test", "cpu": 3.0, "rss_kb": GB, "rr": 0}]} for _ in range(5)]
    pk = lb.phase_peaks(few, min_samples=30)
    assert pk["slot.test"]["cpu"] == 5.9 and pk["slot.test"]["ram_kb"] == 1910344 and pk["slot.test"]["how"].startswith("floor")
    many = [{"jobs": [{"k": "slot", "p": "test", "cpu": 3.0 + i / 100, "rss_kb": GB, "rr": 0}]} for i in range(100)]
    pk = lb.phase_peaks(many, min_samples=30)
    assert pk["slot.test"]["cpu"] == 3.94 and pk["slot.test"]["ram_kb"] == GB and pk["slot.test"]["how"] == "p95"
    assert pk["lead.retrieval"]["gpu"] == 3584 and pk["lead.build"]["gpu"] == 0  # no samples: the floors


def test_review_f1_one_spike_never_sets_a_phases_peak():
    """Below phase_min_samples one sample alone (a reaped run's CPU landing in one pass) does not set the peak for
    the window; two at that level do."""
    rows = [{"jobs": [{"k": "lead", "p": "build", "cpu": c, "rss_kb": GB, "rr": 0}]} for c in (0.5, 0.4, 0.6, 36.0)]
    assert lb.phase_peaks(rows, 30)["lead.build"]["cpu"] == 1.0  # today's floor
    rows.append({"jobs": [{"k": "lead", "p": "build", "cpu": 30.0, "rss_kb": GB, "rr": 0}]})
    assert lb.phase_peaks(rows, 30)["lead.build"]["cpu"] == 30.0
    assert lb.pick([], 2.0, 30) == 2.0 and lb.pick([9.0], 2.0, 30) == 2.0


def test_review_f2_a_derived_reranker_count_is_never_0_with_a_gpu():
    assert lb.derive_limits(TODAY, {"embedders_gpu_mib": 15000, "reranker_gpu_mib": 3584})["rerank_gpu_slots"] == 1


def test_review_f2_slots_held_by_a_tool_are_no_rerankers_gpu_memory():
    """A slot-holding tool (DEC-1043 item 2) holds no GPU memory: the reranker's share divides by the slots held by
    rerankers (rr_gpu), not all held."""
    rows = [{"gpu_used_mib": 5000, "rr_held": 0, "rr_gpu": 0, "rr_n": 0} for _ in range(40)]
    rows += [{"gpu_used_mib": 8000, "rr_held": 2, "rr_gpu": 1, "rr_n": 1} for _ in range(40)]
    assert lb.shares(rows, 30)["reranker_gpu_mib"] == 3000


def test_the_gpu_shares_are_measured_from_the_rows():
    rows = [{"gpu_used_mib": 5000, "rr_held": 0, "rr_n": 0} for _ in range(40)]
    rows += [{"gpu_used_mib": 5000 + 3000 * h, "rr_held": h, "rr_n": h} for h in (1, 2) for _ in range(20)]
    sh = lb.shares(rows, 30)
    assert sh == {"embedders_gpu_mib": 5000, "reranker_gpu_mib": 3000, "embedders_samples": 40, "reranker_samples": 40}
    assert lb.phase_peaks(rows, 30)["lead.retrieval"]["gpu"] == 3000


# ---- the forecast ---------------------------------------------------------------------------------------------------

def state(**kw):
    s = {"busy_cores": 2.0, "band_hi": 18, "mem_available_kb": 16 * GB, "floor_kb": 3 * GB,
         "gpu": {"used_mib": 5734, "total_mib": 16303}, "headroom_mib": 2048, "rr_held": 0, "rr_slots": 2, "jobs": []}
    s.update(kw)
    return s


def test_the_briefs_gpu_case_adds_up_within_the_budget():
    """The brief's planted figures: the embedders 5.6 GiB, a reranker service 3.5 GiB (holding a GPU slot), a
    newcomer whose retrieval takes 3.5 GiB, on the 16 GB card with 2 GiB headroom: 12.6 of 13.9 GiB, so it is
    admitted, the GPU named as the binding resource (reported to the CTO: the brief expected a refusal)."""
    pk = lb.phase_peaks([])
    f = lb.forecast(state(gpu={"used_mib": 5734 + 3584, "total_mib": 16303}, rr_held=1), pk, "lead")
    assert f["ok"] and f["binding"] == "GPU" and f["resources"]["gpu"]["need"] == 5734 + 3584 + 3584
    assert f["resources"]["gpu"]["cap"] == 16303 - 2048


def test_the_forecast_refuses_a_start_that_would_put_gpu_memory_over_its_budget():
    """The embedders 5.6 GiB, a reranker service 3.5 GiB, and a private embedding server of 2.5 GiB (as the GPU
    agent's on 11-02) on the card: the newcomer's retrieval (3.5 GiB) would reach 15.1 of 13.9 GiB: refused, GPU."""
    pk = lb.phase_peaks([])
    f = lb.forecast(state(gpu={"used_mib": 5734 + 3584 + 2560, "total_mib": 16303}, rr_held=1), pk, "lead")
    assert not f["ok"] and f["binding"] == "GPU" and f["reason"].startswith("forecast refuses (GPU binding): GPU memory")


def test_running_jobs_count_at_their_current_phase_peak():
    pk = lb.phase_peaks([])
    lead = {"kind": "lead", "name": "W2-A", "phase": "retrieval", "cpu": 0.5, "rss_kb": GB, "rr": 0}
    f = lb.forecast(state(jobs=[lead]), pk, "lead")
    assert f["resources"]["gpu"]["need"] == 5734 + 2 * 3584  # its reranker not on the GPU yet, and the newcomer's
    assert f["resources"]["cpu"]["need"] == pytest.approx(2.0 + 1.5 + 2.0)
    held = dict(lead, rr=1)
    f = lb.forecast(state(jobs=[held], gpu={"used_mib": 5734 + 3584, "total_mib": 16303}, rr_held=1), pk, "lead")
    assert f["resources"]["gpu"]["need"] == 5734 + 2 * 3584  # held: in `used` already, not counted twice


def test_the_free_gpu_reranker_slots_bound_the_rerankers_share():
    pk = lb.phase_peaks([])
    jobs = [{"kind": "lead", "name": f"W2-{i}", "phase": "retrieval", "cpu": 0, "rss_kb": 0, "rr": 0} for i in range(4)]
    f = lb.forecast(state(jobs=jobs), pk, "lead")
    assert f["resources"]["gpu"]["need"] == 5734 + 2 * 3584  # 2 slots: at most 2 rerankers on the GPU
    # the text shows what is counted: the running jobs' part capped first, the newcomer's what is left (none)
    assert "running jobs' peaks 7.0 + the newcomer's 0.0; 2 GPU reranker slot(s) free" in f["resources"]["gpu"]["text"]


def test_cpu_and_ram_are_each_named_when_short():
    pk = lb.phase_peaks([])
    tests = [{"kind": "slot", "name": f"pid {i}", "phase": "test", "cpu": 5.0, "rss_kb": GB, "rr": 0} for i in range(3)]
    f = lb.forecast(state(busy_cores=16.0, jobs=tests), pk, "slot")
    assert not f["ok"] and f["binding"] == "CPU"
    f = lb.forecast(state(mem_available_kb=4 * GB), pk, "lead")
    assert not f["ok"] and f["binding"] == "RAM"


def test_an_unread_gpu_or_cpu_is_not_judged():
    f = lb.forecast(state(gpu=None, busy_cores=None), lb.phase_peaks([]), "lead")
    assert f["ok"] and set(f["resources"]) == {"ram"}


# ---- the pairing ----------------------------------------------------------------------------------------------------

def test_pairing_chooses_a_gpu_heavy_start_beside_two_running_test_slots():
    pk = lb.phase_peaks([])
    tests = [{"kind": "slot", "name": f"pid {i}", "phase": "test", "cpu": 5.9, "rss_kb": GB, "rr": 0} for i in range(2)]
    load = lb.loads(state(busy_cores=13.0, jobs=tests), pk)
    assert load["cpu"] > load["gpu"]
    assert lb.pair([("resume-tests", "cpu"), ("new-lead", "gpu")], load) == ["new-lead", "resume-tests"]


def test_pairing_chooses_a_cpu_heavy_start_while_the_gpu_embeds():
    pk = lb.phase_peaks([])
    emb = [{"kind": "rebuild", "name": "pid 7", "phase": "rebuild.embedding", "cpu": 6.0, "rss_kb": GB, "rr": 0},
           {"kind": "lead", "name": "W2-B", "phase": "retrieval", "cpu": 2.0, "rss_kb": GB, "rr": 1}]
    load = lb.loads(state(busy_cores=8.0, jobs=emb, gpu={"used_mib": 9318, "total_mib": 16303}, rr_held=1), pk)
    assert load["gpu"] > load["cpu"]
    assert lb.pair([("new-lead", "gpu"), ("resume-tests", "cpu")], load) == ["resume-tests", "new-lead"]


def test_pairing_keeps_the_order_on_a_tie():
    assert lb.pair([("a", "gpu"), ("b", "gpu"), ("c", None)], {"cpu": 0.5, "gpu": 0.5}) == ["a", "b", "c"]


# ---- the breach timer (DEC-1038 (4)) --------------------------------------------------------------------------------

def run_minutes(st, breached, t0, minutes, event=False):
    acts = []
    for m in range(minutes):
        acts.append(lb.breach_step(st, breached, t0 + 60 * m, event=event))
    return [a for a in acts if a]


def test_the_breach_timer_14_minutes_nothing_16_one_incident_no_second_closed_after_15_held():
    st, t0 = {}, 1_800_000_000.0
    assert run_minutes(st, True, t0, 15) == []  # minutes 0 to 14: nothing
    assert lb.breach_step(st, True, t0 + 16 * 60) == "open" and st["open"] == t0
    assert run_minutes(st, True, t0 + 17 * 60, 20) == ["again"] * 20  # still breached: no second incident
    assert run_minutes(st, False, t0 + 40 * 60, 15) == []  # held 14 minutes: still open
    assert lb.breach_step(st, False, t0 + 55 * 60) == "close" and st["open"] is None


def test_a_breach_back_within_the_quarter_hour_is_the_same_incident():
    st, t0 = {}, 1_800_000_000.0
    run_minutes(st, True, t0, 17)
    assert st["open"]
    run_minutes(st, False, t0 + 17 * 60, 10)
    assert lb.breach_step(st, True, t0 + 27 * 60) == "again" and st["open"] == t0


def test_an_event_target_opens_at_its_first_event_and_once():
    st, t0 = {}, 1_800_000_000.0
    assert lb.breach_step(st, True, t0, event=True) == "open"
    assert lb.breach_step(st, True, t0 + 60, event=True) == "again"
    assert run_minutes(st, False, t0 + 120, 16, event=True) == ["close"]


def test_not_measured_changes_nothing():
    st = {"breach_since": 5.0}
    assert lb.breach_step(st, None, 1e9) is None and st == {"breach_since": 5.0}
