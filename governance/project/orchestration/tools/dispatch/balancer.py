"""The Gov Load Balancer's arithmetic (owner, DEC-1039 (1b); DEC-1037 (4); DEC-1038 (4)). Pure functions, no I/O: the
dispatcher (dispatcher.py beside this file) reads the machine, the processes and the samples, and calls these.

  - derive_limits: every limit from the detected machine by ratios that give today's numbers on this machine
    (20 CPUs, 24 GB, the RTX 5070 Ti's 16,303 MiB); apply_limits: an explicit number in config.json still wins;
  - PHASES and phase_peaks: the phases of each kind of work and each phase's peak on every resource (CPU cores busy,
    RAM, GPU memory, GPU use), a p95 over a rolling window of the dispatcher's own samples, with a floor from today's
    figures while the samples are few;
  - forecast: a start is admitted only if, for every resource, the running jobs' current-phase peaks plus the
    newcomer's worst-phase peak stay within capacity; the binding resource is named;
  - pair: when several starts are possible, the one whose heavy resource is the idler goes first;
  - Breach: the standing targets' 15-minute breach rule, one incident per breach.
"""
import math

# ---- the machine and its limits (DEC-1037 (4): no number fixed for this machine) ------------------------------------

REFERENCE = {"cpus": 20, "mem_total_kb": 24607384, "gpu_total_mib": 16303}  # this machine on 2026-11-02
RATIOS = {
    "cpu_band": (0.70, 0.90),        # 14-18 busy cores of 20
    "cpu_margin": 0.10,              # 2 of 20
    "heavy_slots": 0.15,             # 3 slots on 20 CPUs
    "heavy_cpu_share": 0.90,         # the slots' workers together: 18 of 20 -> 6 workers a slot
    "slots_cpu_of_gpu": 2 / 3,       # 2 slots while the embedder is on the CPU, of 3
    "gpu_headroom": 0.1256,          # 2048 MiB of 16,303
    "gpu_shared_floor": 1 / 16,      # a spill reading: shared GPU memory above 1,019 MiB of 16,303 (the desktop: ~580)
}
FLOOR_EMBEDDERS_GPU_MIB = 5734      # the two embedders on the GPU with the desktop, 2026-11-02 19:30 (5.6 GiB)
FLOOR_RERANKER_GPU_MIB = 3584       # one reranker process on the GPU (LB-PLAN-gpu section 5: about 3.5 GiB)
DERIVED_KEYS = ("cpu_band", "cpu_margin", "heavy_slots", "heavy_workers", "slots_gpu", "slots_cpu", "gpu_headroom_mib",
                "rerank_gpu_slots", "gpu_shared_floor_mib")


def half_up(x):
    """Rounding half up (Python's round() rounds half to even)."""
    return int(math.floor(x + 0.5))


def derive_limits(machine, measured=None):
    """The limits from the machine {cpus, mem_total_kb, gpu_total_mib (None: no GPU)} and the measured shares
    {embedders_gpu_mib, reranker_gpu_mib}. Returns {key: value} for DERIVED_KEYS and "how": {key: the rule}."""
    measured = measured or {}
    cpus = int(machine.get("cpus") or REFERENCE["cpus"])
    lo, hi = RATIOS["cpu_band"]
    slots = max(1, half_up(cpus * RATIOS["heavy_slots"]))
    workers = max(1, int(cpus * RATIOS["heavy_cpu_share"] // slots))
    out = {"cpu_band": [max(1, half_up(cpus * lo)), max(1, half_up(cpus * hi))],
           "cpu_margin": max(1, half_up(cpus * RATIOS["cpu_margin"])),
           "heavy_slots": slots, "heavy_workers": workers,
           "slots_gpu": slots, "slots_cpu": max(1, half_up(slots * RATIOS["slots_cpu_of_gpu"]))}
    how = {"cpu_band": f"{lo:.2f}-{hi:.2f} of {cpus} CPUs", "cpu_margin": f"{RATIOS['cpu_margin']:.2f} of {cpus} CPUs",
           "heavy_slots": f"{RATIOS['heavy_slots']:.2f} of {cpus} CPUs",
           "heavy_workers": f"{RATIOS['heavy_cpu_share']:.2f} of {cpus} CPUs / {slots} slots",
           "slots_gpu": "the heavy slots", "slots_cpu": f"{RATIOS['slots_cpu_of_gpu']:.2f} of the heavy slots"}
    total = machine.get("gpu_total_mib")
    if total:
        emb = int(measured.get("embedders_gpu_mib") or FLOOR_EMBEDDERS_GPU_MIB)
        rr = int(measured.get("reranker_gpu_mib") or FLOOR_RERANKER_GPU_MIB)
        head = half_up(total * RATIOS["gpu_headroom"])
        out.update(gpu_headroom_mib=head, gpu_shared_floor_mib=half_up(total * RATIOS["gpu_shared_floor"]),
                   rerank_gpu_slots=max(1, int((total - emb - head) // rr)))  # never 0 with a GPU (review F2)
        how.update(gpu_headroom_mib=f"{RATIOS['gpu_headroom']:.4f} of {total} MiB",
                   gpu_shared_floor_mib=f"1/16 of {total} MiB",
                   rerank_gpu_slots=f"({total} - the embedders' {emb} - headroom {head}) MiB / a reranker's {rr} MiB")
    else:  # no GPU: nothing may rely on one
        out.update(gpu_headroom_mib=0, gpu_shared_floor_mib=0, rerank_gpu_slots=0)
        how.update(gpu_headroom_mib="no GPU", gpu_shared_floor_mib="no GPU", rerank_gpu_slots="no GPU")
    out["how"] = how
    return out


def apply_limits(c, explicit, derived):
    """Each derived limit into the configuration `c`, unless config.json set it (`explicit`: its keys): the owner's
    override wins. Returns {key: (the explicit value, the derived one)} for the overrides that differ."""
    over = {}
    for k in DERIVED_KEYS:
        if k not in derived:
            continue
        if k in explicit:
            if explicit[k] != derived[k]:
                over[k] = (explicit[k], derived[k])
            c[k] = explicit[k]
        else:
            c[k] = derived[k]
    return over


def machine_changed(old, new):
    """The fields that differ between two machine records (RAM by the half GB: MemTotal moves by a few kB)."""
    if not old:
        return []
    keys = ("cpus", "cores", "mem_total_gb")
    if old.get("gpu_known") and new.get("gpu_known"):  # a GPU not read yet is no change
        keys += ("gpu_name", "gpu_total_mib")
    return [k for k in keys if old.get(k) != new.get(k)]


# ---- the phases and their peaks (DEC-1039 (1b)) ---------------------------------------------------------------------

GB_KB = 1024 * 1024
R = "reranker"  # a phase whose GPU memory is one reranker's share (measured, at least FLOOR_RERANKER_GPU_MIB)
# Each phase's floor: today's figures (2026-11-02; the sources are in the README's "The Gov Load Balancer"):
# cpu (cores busy), ram_kb, gpu (MiB; R = one reranker's share), util (GPU use %), heavy (the resource it loads most).
PHASES = {
    "start": {"cpu": 2.0, "ram_kb": 2180248, "gpu": R, "util": 10, "heavy": "gpu"},
    "retrieval": {"cpu": 2.0, "ram_kb": 2180248, "gpu": R, "util": 10, "heavy": "gpu"},
    "review": {"cpu": 2.0, "ram_kb": 2180248, "gpu": R, "util": 10, "heavy": "gpu"},
    "build": {"cpu": 1.0, "ram_kb": 2180248, "gpu": 0, "util": 0, "heavy": None},
    "test": {"cpu": 5.9, "ram_kb": 1910344, "gpu": 0, "util": 0, "heavy": "cpu"},
    "rebuild.lexical": {"cpu": 2.5, "ram_kb": 521024, "gpu": 0, "util": 0, "heavy": "cpu"},
    "rebuild.embedding": {"cpu": 6.0, "ram_kb": 521024, "gpu": 0, "util": 65, "heavy": "gpu"},
    "other": {"cpu": 1.0, "ram_kb": 521024, "gpu": 0, "util": 0, "heavy": None},
}
KIND_FLOORS = {("lead", "test"): {"ram_kb": 4090592}}  # a lead's tree in its test run (the leads' p95 inside one)
KINDS = {  # the phases of each kind of work; a lead's own admission covers the phases it enters with no other gate
    "lead": ("start", "retrieval", "build", "test", "review", "rebuild.lexical", "rebuild.embedding"),
    "landing": ("rebuild.lexical", "rebuild.embedding", "test", "other"),
    "close": ("rebuild.lexical", "rebuild.embedding", "test", "other"),
    "nightly": ("rebuild.lexical", "rebuild.embedding", "test", "other"),
    "rebuild": ("rebuild.lexical", "rebuild.embedding"),
    "slot": ("test",),
}
UNGATED = ("start", "retrieval", "build", "review")  # a test run takes a slot, a rebuild its slot: admitted there
NEWCOMERS = {"lead": UNGATED, "slot": ("test",), "rebuild": ("rebuild.lexical", "rebuild.embedding")}


def pct(values, q):
    v = sorted(values)
    return v[min(len(v) - 1, int(q * (len(v) - 1) + 0.5))] if v else None


def pick(vals, floor, min_samples):
    """A phase's peak: the p95 from `min_samples` on; before that the larger of the floor (today's figure) and the
    second-largest sample, so one sample alone never sets it (review F1: one spike would hold the peak for the whole
    window and refuse every newcomer)."""
    if len(vals) >= min_samples:
        return pct(vals, 0.95)
    return max([floor] + sorted(vals)[:-1])


def floor_of(kind, phase):
    f = dict(PHASES.get(phase) or PHASES["other"])
    f.update(KIND_FLOORS.get((kind, phase), {}))
    return f


def shares(rows, min_samples=30):
    """The GPU's measured shares from the balance rows: the embedders' (GPU used while no reranker holds a GPU slot
    and none runs) and one reranker's ((used - the embedders' share) / the GPU slots held). Each a p95 once there are
    `min_samples`, else at least today's figure (the largest sample: a larger share prices the GPU higher, the safe
    side). Only the GPU slots held by reranker processes count (`rr_gpu`): a tool holding slots so that no private
    reranker joins the shared service (DEC-1043 item 2) holds no GPU memory."""
    def on_gpu(r):
        return r.get("rr_gpu", r.get("rr_held"))
    base = [r["gpu_used_mib"] for r in rows if r.get("gpu_used_mib") is not None and on_gpu(r) == 0
            and r.get("rr_n") == 0]
    emb = pct(base, 0.95) if len(base) >= min_samples else max([FLOOR_EMBEDDERS_GPU_MIB] + base)
    each = [(r["gpu_used_mib"] - emb) / on_gpu(r) for r in rows
            if r.get("gpu_used_mib") is not None and (on_gpu(r) or 0) > 0]
    each = [x for x in each if x > 0]
    rr = pct(each, 0.95) if len(each) >= min_samples else max([FLOOR_RERANKER_GPU_MIB] + each)
    return {"embedders_gpu_mib": int(emb), "reranker_gpu_mib": int(rr), "embedders_samples": len(base),
            "reranker_samples": len(each)}


def phase_peaks(rows, min_samples=30):
    """{"kind.phase": {cpu, ram_kb, gpu, util, heavy, samples, how}} from the balance rows (each with its jobs: kind
    "k", phase "p", cores "cpu", tree RSS "rss_kb", GPU reranker slots held in its tree "rr"). A p95 over the rows
    given (the rolling window) once a phase has `min_samples`; before that the larger of the floor and the
    second-largest sample (`pick`: one spike never sets it)."""
    sh = shares(rows, min_samples)
    samples = {}
    for r in rows:
        jobs = r.get("jobs") or []
        gpu_heavy = [j for j in jobs if (PHASES.get(j.get("p")) or {}).get("heavy") == "gpu"]
        for j in jobs:
            s = samples.setdefault(f"{j.get('k')}.{j.get('p')}", {"cpu": [], "ram_kb": [], "rr": [], "util": []})
            if j.get("cpu") is not None:
                s["cpu"].append(j["cpu"])
            s["ram_kb"].append(j.get("rss_kb") or 0)
            s["rr"].append(j.get("rr") or 0)
            if len(gpu_heavy) == 1 and gpu_heavy[0] is j and r.get("gpu_util") is not None:
                s["util"].append(r["gpu_util"])
    out = {}
    for kind, phases in KINDS.items():
        for phase in phases:
            key, f = f"{kind}.{phase}", floor_of(kind, phase)
            s = samples.get(key, {"cpu": [], "ram_kb": [], "rr": [], "util": []})
            n = len(s["ram_kb"])
            gpu_floor = sh["reranker_gpu_mib"] if f["gpu"] == R else f["gpu"]
            rr_n = pick(s["rr"], 1 if f["gpu"] == R else 0, min_samples)
            out[key] = {"cpu": round(pick(s["cpu"], f["cpu"], min_samples), 2),
                        "ram_kb": int(pick(s["ram_kb"], f["ram_kb"], min_samples)),
                        "gpu": int(rr_n * sh["reranker_gpu_mib"]) if f["gpu"] == R or rr_n else int(gpu_floor),
                        "util": pick(s["util"], f["util"], min_samples) if f["heavy"] == "gpu" else f["util"],
                        "heavy": f["heavy"], "samples": n,
                        "how": "p95" if n >= min_samples else f"floor ({n} of {min_samples} samples)"}
    out["_shares"] = sh
    return out


def with_history(peaks, history):
    """The RAM floors from the 7-day history the memory rule uses (peaks.json: a lead's p95 outside verification and
    inside it, a slot run's memory, a rebuild's p95), for the phases with too few samples of their own: one measure
    of a lead's memory for the forecast and the memory rule. `history` values None are left at today's figures."""
    h = history or {}
    out = dict(peaks)
    for key, p in peaks.items():
        if key.startswith("_") or p.get("how") == "p95":
            continue
        kind, phase = key.split(".", 1)
        kb = (h.get("lead_inside_kb") if (kind, phase) == ("lead", "test") else
              h.get("lead_outside_kb") if kind == "lead" and phase in UNGATED else
              h.get("slot_run_kb") if phase == "test" else
              h.get("rebuild_kb") if phase.startswith("rebuild.") else None)
        if kb:
            out[key] = dict(p, ram_kb=int(kb), how=p["how"] + "; RAM from the 7-day history")
    return out


def peak_of(peaks, kind, phase):
    p = peaks.get(f"{kind}.{phase}")
    if p:
        return p
    f = floor_of(kind, phase)
    sh = peaks.get("_shares") or {}
    return dict(f, gpu=(sh.get("reranker_gpu_mib") or FLOOR_RERANKER_GPU_MIB) if f["gpu"] == R else f["gpu"])


def worst(peaks, kind, phases):
    """The newcomer's worst phase on each resource (each resource's own worst)."""
    ps = [peak_of(peaks, kind, p) for p in phases]
    return {"cpu": max(p["cpu"] for p in ps), "ram_kb": max(p["ram_kb"] for p in ps),
            "gpu": max(p["gpu"] for p in ps), "util": max(p["util"] for p in ps)}


GB = lambda kb: f"{kb / GB_KB:.1f}"  # noqa: E731


def forecast(state, peaks, newcomer_kind, newcomer_phases=None):
    """Admit a start only if, for every resource, the running jobs' current-phase peaks plus the newcomer's worst-phase
    peak stay within capacity: CPU within the band (busy + each job's peak above what it uses now + the newcomer <= the
    band's top), RAM above the floor (available - each job's peak above its RSS now - the newcomer >= the floor), GPU
    memory at most total minus headroom (used + each job's GPU peak above what it holds + the newcomer, the rerankers'
    part at most the free GPU reranker slots' share). `state`: busy_cores, band_hi, mem_available_kb, floor_kb,
    gpu {used_mib, total_mib} or None, headroom_mib, rr_held, rr_slots, jobs [{kind, phase, cpu, rss_kb, rr}].
    Returns {ok, binding, resources: {cpu|ram|gpu: {need, cap, ok, frac, text}}, newcomer, reason}."""
    phases = newcomer_phases or NEWCOMERS.get(newcomer_kind, UNGATED)
    new = worst(peaks, newcomer_kind, phases)
    rr_share = (peaks.get("_shares") or {}).get("reranker_gpu_mib") or FLOOR_RERANKER_GPU_MIB
    cpu_up = ram_up = gpu_up = 0.0
    for j in state.get("jobs") or []:
        p = peak_of(peaks, j["kind"], j["phase"])
        cpu_up += max(0.0, p["cpu"] - (j.get("cpu") or 0.0))
        ram_up += max(0, p["ram_kb"] - (j.get("rss_kb") or 0))
        gpu_up += max(0, p["gpu"] - (j.get("rr") or 0) * rr_share)
    res = {}
    busy = state.get("busy_cores")
    hi = state["band_hi"]
    if busy is not None:
        need = busy + cpu_up + new["cpu"]
        res["cpu"] = {"need": round(need, 1), "cap": hi, "ok": need <= hi, "frac": need / hi if hi else 9,
                      "text": f"CPU {need:.1f} of {hi} cores (busy {busy} + running jobs' peaks {cpu_up:.1f} + the "
                              f"newcomer's {new['cpu']})"}
    avail, floor = state.get("mem_available_kb"), state.get("floor_kb")
    if avail is not None and floor is not None:
        need, cap = ram_up + new["ram_kb"], avail - floor
        res["ram"] = {"need": need, "cap": cap, "ok": need <= cap, "frac": need / cap if cap > 0 else 9,
                      "text": f"RAM {GB(avail - need)} GB left of {GB(avail)} available (floor {GB(floor)}; running "
                              f"jobs' peaks {GB(ram_up)} + the newcomer's {GB(new['ram_kb'])})"}
    g = state.get("gpu")
    if g and g.get("used_mib") is not None and g.get("total_mib"):
        slots, held = state.get("rr_slots"), state.get("rr_held")
        free = None if held is None or slots is None else max(0, slots - held)
        new_gpu = new["gpu"] if (free is None or free > 0 or new["gpu"] == 0) else 0
        if free is not None:  # the rerankers' part at most the free slots' share: the running jobs' first
            gpu_up = min(gpu_up, free * rr_share)
            new_gpu = min(new_gpu, max(0, free * rr_share - gpu_up))
        up = gpu_up + new_gpu
        cap = g["total_mib"] - state.get("headroom_mib", 0)
        need = g["used_mib"] + up
        res["gpu"] = {"need": int(need), "cap": int(cap), "ok": need <= cap, "frac": need / cap if cap > 0 else 9,
                      "text": f"GPU memory {need / 1024:.1f} of {cap / 1024:.1f} GB (used {g['used_mib'] / 1024:.1f} + "
                              f"running jobs' peaks {gpu_up / 1024:.1f} + the newcomer's {new_gpu / 1024:.1f}; "
                              f"{'?' if free is None else free} GPU reranker slot(s) free)"}
    names = {"cpu": "CPU", "ram": "RAM", "gpu": "GPU"}
    short = [k for k in ("cpu", "ram", "gpu") if k in res and not res[k]["ok"]]
    binding = short[0] if short else (max(res, key=lambda k: res[k]["frac"]) if res else None)
    ok = not short
    reason = (f"forecast refuses ({names[binding]} binding): {res[binding]['text']}" if not ok else
              (f"forecast admits (binding {names[binding]}: {res[binding]['text']})" if binding else
               "forecast: nothing measured"))
    return {"ok": ok, "binding": names.get(binding), "resources": res, "newcomer": new, "reason": reason}


def loads(state, peaks):
    """How loaded the CPU and the GPU are now, with the running jobs' current-phase peaks (0 to 1 and over): the CPU
    by cores against the band's top, the GPU by the larger of its memory against its budget and its use (the
    running phases' GPU use)."""
    f = forecast(state, peaks, "slot", ("other",))
    other = peak_of(peaks, "slot", "other")
    cpu = f["resources"].get("cpu")
    cpu_load = (cpu["need"] - other["cpu"]) / cpu["cap"] if cpu and cpu["cap"] else 0.0
    gpu = f["resources"].get("gpu")
    mem = (gpu["need"] / gpu["cap"]) if gpu and gpu["cap"] else 0.0
    util = sum(peak_of(peaks, j["kind"], j["phase"])["util"] for j in state.get("jobs") or []) / 100
    return {"cpu": round(cpu_load, 2), "gpu": round(max(mem, util), 2)}


def pair(candidates, load):
    """The starts possible, best first: the one whose heavy resource is the idler (a GPU-heavy start while test runs
    fill the CPU; a CPU-heavy one while the GPU is busy embedding), so neither peaks twice. `candidates`:
    [(item, heavy)] in the list's order; a start with no heavy resource counts as half loaded. Ties keep the order."""
    def score(c):
        return load.get(c[1], 0.5) if c[1] else 0.5
    return [c[0] for c in sorted(candidates, key=score)]


# ---- the standing targets: the breach rule (DEC-1038 (4)) ------------------------------------------------------------

OPEN_AFTER_S = 900   # a breach lasting more than 15 minutes opens an incident
CLOSE_AFTER_S = 900  # it closes when the target has held again for 15 minutes


def breach_step(st, breached, t, event=False, open_after=OPEN_AFTER_S, close_after=CLOSE_AFTER_S):
    """One target's timer, one pass. `st` (changed in place): breach_since, ok_since, open (the incident's start or
    None). A continuous target (T1-T3, the heavy steps outside a slot) opens when breached for more than `open_after`;
    an event target (T4, T5: `event` True and `breached` the pass's events) opens at its first event. One incident per
    breach: none again while it is open; it closes when the target has held for `close_after`. Returns "open",
    "close", "again" (an event or breach while open) or None. `breached` None (not measured) changes nothing."""
    if breached is None:
        return None
    if breached:
        st["ok_since"] = None
        st["breach_since"] = st.get("breach_since") or t
        if st.get("open"):
            return "again"
        if event or t - st["breach_since"] > open_after:
            st["open"] = st["breach_since"]
            return "open"
        return None
    st["breach_since"] = None
    st["ok_since"] = st.get("ok_since") or t
    if st.get("open") and t - st["ok_since"] >= close_after:
        st["open"] = None
        return "close"
    return None
