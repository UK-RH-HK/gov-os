"""S15, S17 and F1: a heavy job's thread budget and CPU set.

S15: a heavy job's slot carries a thread budget: every program the job starts (children, grandchildren, xdist
workers, programs started by its tests) receives the common runtimes' thread limits (Go, OpenMP, MKL, OpenBLAS,
Rayon, numexpr, Accelerate) set to the slot's share of the logical CPUs divided by its workers, at least 1, derived
from the machine at start (never a number fixed for one machine); a value inherited from the caller does not raise
it; the configuration file may set it, with its date and source [DEC-1038 (4), P-W2-20-THREAD-BUDGET (a)].
S17: a heavy job's slot is confined to its share of the logical CPUs (its own CPU set, derived from the machine and
the number of slots, outside any CPU set the configuration gives the embedding servers), so a program that ignores
every thread variable or starts many processes is still held to the share [DEC-1038 (4)].
F1 (failure): a heavy job whose child programs together use more CPUs than its slot's share, because they start
their own thread pools or size their pools to the whole machine.

Expected values are derived here from this machine at run time (README, "Heavy jobs"): the slots' CPUs are the CPUs
the process may use less the embedding servers' CPUs; each slot's set has ``max(1, len(those) // heavy_slots)`` CPUs;
the budget is ``max(1, len(set) // workers)``; ``thread_budget`` in the file, when present, is the budget.
"""

from __future__ import annotations

import pytest

import w2_20_support as support

INHERITED = {var: "999" for var in support.THREAD_VARS}  # the caller's own values, far above any share


def _slot_cpus(machine, slots=2):
    shared, query = machine.embedding_cpus()
    servers = support.parse_cpu_list(shared) | support.parse_cpu_list(query)
    pool = [c for c in support.allowed_cpus() if c not in servers] or support.allowed_cpus()
    return set(pool), servers, max(1, len(pool) // slots)


@pytest.mark.parametrize("workers", [1, 4], ids=["one worker", "four workers"])
def test_s15_every_program_a_heavy_job_starts_gets_the_slots_thread_budget(machine, repo, workers):
    machine.open_config(heavy_slots=2)
    _, _, share = _slot_cpus(machine)
    budget = str(max(1, share // workers))
    machine.slot_job(repo, "test", "budget", workers=workers, hold=False, child=True, env_extra=INHERITED)

    for tag in ("budget", "budget.child"):
        record = machine.job_record(tag)
        wrong = {var: value for var, value in record["env"].items() if value != budget}
        assert not wrong, (f"{tag}: the thread limits are not the slot's budget {budget} (share {share}, "
                           f"{workers} workers; the caller's 999 must not raise it): {wrong}")


def test_s15_the_configuration_file_may_set_the_budget(machine, repo):
    machine.open_config(heavy_slots=2, thread_budget=support.dated(1, source="planted: one thread"))
    machine.slot_job(repo, "test", "fixed", hold=False, child=True, env_extra=INHERITED)
    for tag in ("fixed", "fixed.child"):
        record = machine.job_record(tag)
        assert all(value == "1" for value in record["env"].values()), f"{tag}: {record['env']}"


def test_s17_a_heavy_job_and_its_children_are_confined_to_the_slots_share_outside_the_servers_cpus(machine, repo):
    machine.open_config(heavy_slots=2)
    pool, servers, share = _slot_cpus(machine)
    machine.slot_job(repo, "test", "confined", hold=False, child=True)

    job, child = machine.job_record("confined"), machine.job_record("confined.child")
    cpus = set(job["affinity"])
    assert len(cpus) == share, f"the slot's CPU set has {len(cpus)} CPUs, not its share {share}: {sorted(cpus)}"
    assert cpus <= pool, f"the slot's CPU set takes CPUs outside the slots' pool: {sorted(cpus - pool)}"
    assert not cpus & servers or pool == set(support.allowed_cpus()), (
        f"the slot's CPU set takes the embedding servers' CPUs: {sorted(cpus & servers)}")
    assert set(child["affinity"]) <= cpus, f"F1: the job's child runs outside the slot's CPUs: {child['affinity']}"


def test_s17_two_slots_held_at_once_have_disjoint_cpu_sets(machine, repo):
    machine.open_config(heavy_slots=2)
    pool, _, share = _slot_cpus(machine)
    machine.slot_job(repo, "test", "left")
    machine.slot_job(repo, "test", "right")
    machine.wait_started("left")
    machine.wait_started("right")
    left, right = set(machine.job_record("left")["affinity"]), set(machine.job_record("right")["affinity"])
    assert len(left) == len(right) == share, (sorted(left), sorted(right), share)
    if len(pool) >= 2 * share:
        assert not left & right, f"two slots share CPUs: {sorted(left & right)}"
    machine.release("left")
    machine.release("right")
