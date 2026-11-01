"""W2-123 KPI 3: the embedding server at 1, 2, 4 and 8 parallel requests, under the CPU cap and without it, alone and
with three rebuilds' embedding at once, on a private server instance started by the ticket's own code (never the
shared one). Each "rebuild" replays the semantic stage's requests exactly (batches of ``semantic.BATCH`` chunks, each
its first ``EMBED_CHARS`` characters, one request after another) and checks every vector against the stored one.

    measure.py sweep <port> <out.jsonl> <store.db> <home> <capped cpus> [per_client]
    measure.py full  <port> <out.jsonl> <store.db> <home> <capped cpus> <parallel>
"""
import json
import os
import signal
import sqlite3
import subprocess
import sys
import threading
import time
from pathlib import Path

from gov.retrieval import ollama, semantic

MODE, PORT, OUT, STORE, HOME, CAPPED = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), \
    Path(sys.argv[5]), sys.argv[6]
assert PORT not in (11434, 11435), "never the shared servers"
HOST = f"127.0.0.1:{PORT}"
BIN = "/home/usain/.local/ollama/bin/ollama"
MODELS = "/home/usain/.ollama/models"
DET_N = 256
TICK = os.sysconf("SC_CLK_TCK")
ALL = f"0-{os.cpu_count() - 1}"


def log(record):
    record["at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with OUT.open("a") as handle:
        handle.write(json.dumps(record) + "\n")
    print(json.dumps(record), flush=True)


def sample():
    """The stored chunks with vectors, in id order: (text, stored vector)."""
    connection = sqlite3.connect(STORE.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        rows = connection.execute(
            "SELECT f.text, v.embedding FROM semantic_vector v JOIN lexical_chunk c ON c.chunk_id = v.chunk_id "
            "JOIN lexical_fts f ON f.rowid = c.id ORDER BY c.id").fetchall()
    finally:
        connection.close()
    return [(text[:semantic.EMBED_CHARS], bytes(blob)) for text, blob in rows]


def pid_on_port():
    out = subprocess.run(["ss", "-ltnpH", f"sport = :{PORT}"], capture_output=True, text=True).stdout
    for part in out.split("pid=")[1:]:
        return int(part.split(",")[0])
    return None


def children(pid):
    found = []
    for entry in Path("/proc").iterdir():
        if entry.name.isdigit():
            try:
                if int((entry / "stat").read_text().rsplit(")", 1)[1].split()[1]) == pid:
                    found.append(int(entry.name))
            except (OSError, IndexError, ValueError):
                pass
    return found + [g for c in found for g in children(c)]


def cpu_seconds(pids):
    total = 0
    for pid in pids:
        try:
            fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
            total += int(fields[11]) + int(fields[12])
        except (OSError, IndexError, ValueError):
            pass
    return total / TICK


def stop():
    pid = pid_on_port()
    if pid is None:
        return
    cmd = Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")
    environ = Path(f"/proc/{pid}/environ").read_bytes().split(b"\0")
    assert cmd[:2] == [BIN.encode(), b"serve"] and f"OLLAMA_HOST={HOST}".encode() in environ, "not my server"
    for p in [pid] + children(pid):
        try:
            os.kill(p, signal.SIGTERM)
        except ProcessLookupError:
            pass
    for _ in range(100):
        if pid_on_port() is None:
            break
        time.sleep(0.2)
    for p in [pid] + children(pid):
        try:
            os.kill(p, signal.SIGKILL)
        except ProcessLookupError:
            pass
    time.sleep(1)


def cpu_set(text):
    out = set()
    for part in text.split(","):
        lo, _, hi = part.partition("-")
        out |= set(range(int(lo), int(hi or lo) + 1))
    return out


def by_hand(parallel, cpus, nice):
    """The server started as the spec's start does it: `ollama serve`, the cap set in the started process."""
    def cap():
        os.sched_setaffinity(0, cpu_set(cpus))
        os.setpriority(os.PRIO_PROCESS, 0, max(nice, os.getpriority(os.PRIO_PROCESS, 0)))
    env = {**os.environ, "OLLAMA_HOST": HOST, "OLLAMA_NUM_PARALLEL": str(parallel)}
    subprocess.Popen([BIN, "serve"], env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, start_new_session=True, preexec_fn=cap)
    for _ in range(300):
        if semantic._ask("/api/version", host=HOST):
            return {"by": "hand", "parallel": parallel, "cpus": cpus, "nice": nice}
        time.sleep(0.2)
    raise RuntimeError("private server did not answer")


def determinism(refs, parallel):
    """S5's check, by hand: each text in a request of its own, `parallel` in flight, byte for byte."""
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(parallel) as pool:
        got = list(pool.map(lambda r: (semantic._embed([r[0]], HOST) or [None])[0], refs))
    differing = [i for i, (v, (_, e)) in enumerate(zip(got, refs)) if v != e]
    return {"parallel": parallel, "checked": len(refs), "differing": differing,
            "verdict": "refused" if differing else "accepted"}


def start(parallel, cpus, nice):
    stop()
    if os.environ.get("MEASURE_BY_HAND"):
        result = {"settings": by_hand(parallel, cpus, nice)}
    else:
        folder = HOME / ".gov-os" / "machine"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "gate.json").write_text(json.dumps(
            {"embedding_servers": {"shared": {"parallel": parallel, "cpus": cpus, "nice": nice}}}))
        env = {**os.environ, "HOME": str(HOME), "OLLAMA_HOST": HOST, "OLLAMA_MODELS": MODELS, "GOV_OLLAMA_BIN": BIN}
        result = ollama.ensure_available(timeout_s=60, env=env)
        assert result["available"] and result["started"], result
    assert semantic._embed(["warm up"], HOST) is not None
    pid = pid_on_port()
    runners = [c for c in children(pid) if b"llama-server" in Path(f"/proc/{c}/cmdline").read_bytes()]
    seen = {"settings": result["settings"], "server_pid": pid, "runners": []}
    for p in [pid] + runners:
        args = Path(f"/proc/{p}/cmdline").read_bytes().split(b"\0")
        np_ = args[args.index(b"-np") + 1].decode() if b"-np" in args else None
        status = Path(f"/proc/{p}/status").read_text()
        allowed = next(line.split()[1] for line in status.splitlines() if line.startswith("Cpus_allowed_list"))
        entry = {"pid": p, "np": np_, "cpus": allowed, "nice": os.getpriority(os.PRIO_PROCESS, p)}
        if p == pid:
            seen["server"] = entry
        else:
            seen["runners"].append(entry)
    return seen


class Gpu(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.samples, self.done = [], threading.Event()

    def run(self):
        while not self.done.is_set():
            out = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used",
                                  "--format=csv,noheader,nounits"], capture_output=True, text=True).stdout
            try:
                self.samples.append([float(x) for x in out.strip().split(",")])
            except ValueError:
                pass
            self.done.wait(1.0)

    def stop(self):
        self.done.set()
        self.join()
        if not self.samples:
            return None
        return {"util_mean": round(sum(s[0] for s in self.samples) / len(self.samples), 1),
                "mem_max_mib": max(s[1] for s in self.samples)}


def replay(chunks, result):
    """One rebuild's semantic stage over ``chunks``: its requests one after another; vectors compared."""
    began, differ = time.monotonic(), 0
    for at in range(0, len(chunks), semantic.BATCH):
        batch = chunks[at:at + semantic.BATCH]
        vectors = semantic._embed([text for text, _ in batch], HOST)
        if vectors is None:
            result["error"] = f"no vectors at batch {at}"
            return
        differ += sum(v != stored for v, (_, stored) in zip(vectors, batch))
    result["seconds"] = time.monotonic() - began
    result["differ"] = differ


def phase(groups):
    """Run one replay per group at once; wall seconds, per-rebuild results, cores busy, GPU."""
    pids = [pid_on_port()] + children(pid_on_port())
    gpu, cpu0, began = Gpu(), cpu_seconds(pids), time.monotonic()
    gpu.start()
    results = [{} for _ in groups]
    threads = [threading.Thread(target=replay, args=(g, r)) for g, r in zip(groups, results)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    wall = time.monotonic() - began
    pids = [pid_on_port()] + children(pid_on_port())
    chunks = sum(len(g) for g in groups)
    return {"wall_s": round(wall, 2), "chunks": chunks, "chunks_per_s": round(chunks / wall, 1),
            "per_rebuild": [{"chunks": len(g), "seconds": round(r.get("seconds", -1), 2),
                             "chunks_per_s": round(len(g) / r["seconds"], 1) if "seconds" in r else None,
                             "differ": r.get("differ"), "error": r.get("error")} for g, r in zip(groups, results)],
            "cores_busy": round((cpu_seconds(pids) - cpu0) / wall, 2), "gpu": gpu.stop(),
            "load1": os.getloadavg()[0]}


def main():
    rows = sample()
    corpus = len(rows)
    det = rows[::max(1, corpus // DET_N)][:DET_N]
    log({"kind": "sample", "corpus_chunks": corpus, "det_chunks": len(det), "store": str(STORE)})
    try:
        if MODE == "sweep":
            per = int(sys.argv[7]) if len(sys.argv) > 7 else 1024
            stride = corpus // 3
            groups = [rows[i * stride:i * stride + per] for i in range(3)]
            start(1, CAPPED, 10)  # the references: each text alone, one request at a time, at -np 1
            det = [(text, semantic._embed([text], HOST)[0]) for text, _ in det]
            check_of = determinism if os.environ.get("MEASURE_BY_HAND") else (
                lambda refs, p: ollama.check_determinism(HOST, refs, p))
            for parallel in (1, 2, 4, 8):
                for cap, (cpus, nice) in (("capped", (CAPPED, 10)), ("uncapped", (ALL, 0))):
                    seen = start(parallel, cpus, nice)
                    check = check_of(det, parallel)
                    check = {k: check[k] for k in ("parallel", "checked", "verdict")} | {
                        "differing": len(check["differing"])}
                    alone = phase(groups[:1])
                    three = phase(groups)
                    log({"kind": "case", "parallel": parallel, "cap": cap, "started": seen,
                         "determinism": check, "alone": alone, "three": three,
                         "stage_s_alone": round(corpus / alone["chunks_per_s"], 1),
                         "stage_s_three": round(corpus / min(r["chunks_per_s"] or 1e-9
                                                             for r in three["per_rebuild"]), 1)})
        elif MODE == "cases":  # cases <port> <out> <store> <home> <unused> <p:cpus:nice,...> [per_client]
            per = int(sys.argv[8]) if len(sys.argv) > 8 else 1024
            stride = corpus // 3
            groups = [rows[i * stride:i * stride + per] for i in range(3)]
            start(1, CAPPED, 10)
            det = [(text, semantic._embed([text], HOST)[0]) for text, _ in det]
            check_of = determinism if os.environ.get("MEASURE_BY_HAND") else (
                lambda refs, p: ollama.check_determinism(HOST, refs, p))
            for case in sys.argv[7].split(","):
                parallel, cpus, nice = case.split(":")
                parallel, nice = int(parallel), int(nice)
                seen = start(parallel, cpus, nice)
                check = check_of(det, max(parallel, 1))
                check = {k: check[k] for k in ("parallel", "checked", "verdict")} | {
                    "differing": len(check["differing"])}
                alone = phase(groups[:1])
                three = phase(groups)
                log({"kind": "case", "parallel": parallel, "cap": f"cpus {cpus} nice {nice}", "started": seen,
                     "determinism": check, "alone": alone, "three": three,
                     "stage_s_alone": round(corpus / alone["chunks_per_s"], 1),
                     "stage_s_three": round(corpus / min(r["chunks_per_s"] or 1e-9
                                                         for r in three["per_rebuild"]), 1)})
        else:
            parallel = int(sys.argv[7])
            seen = start(parallel, CAPPED, 10)
            full = phase([rows])
            log({"kind": "full", "parallel": parallel, "cap": "capped", "started": seen, "stage": full})
    finally:
        stop()


if __name__ == "__main__":
    main()
