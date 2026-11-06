#!/usr/bin/env python3
"""The live window's copy of ACT-RERANK-TRIAL-1's probe (drafts/rerank-trial/rerank_trial_probe.py, the same file as
the trial service's svc/ copy), with two additions: ``--bound`` and ``--max-texts`` give a model's own request
bound, so the 4B is probed at the 8 texts and 12,000 padded characters it is sent (DEC-1079 (a)), never at a shape
the harness cannot send it (unset: the original's 24,000 and 16, the same five shapes); and ``peak`` exits 5 when a
shape was not answered (the original exited 0). Speaks the shared reranker's
protocol ([query, [text, ...]] in, one JSON line out) to a TRIAL service's socket only. Never starts a service.

  live_probe.py SOCKET peak  [--limit MIB] [--bound N] [--max-texts N]   the bound's worst shapes, one at a time, GPU
                                                     read before and after each; stops at --limit (default 14255)
  live_probe.py SOCKET load N [--limit MIB] [--bound N] [--max-texts N]  N clients at once, each a search's requests
  live_probe.py SOCKET warm                          one request of one short text (the window's warm-up); exit 5
                                                     when it is not answered

Texts are cut from this repository's own visible files (code first, the densest in tokens), never from evaluation
fixtures. The client's answer timeout is the product's (GOV_RERANK_TIMEOUT_S, 30 s)."""
import json, os, socket, statistics, subprocess, sys, threading, time

REPO = "/home/usain/Dynamic-Agentic-Engineering-OS"
SOURCES = [f"{REPO}/src/gov/retrieval/{n}" for n in ("retrieve.py", "semantic.py", "lexical.py", "fusion.py")]
BOUND, MAX_TEXTS = 24_000, 16  # the product's padded bound since b7085897 (count x longest pair) and its count cap
QUERY = "where does the reranker's request bound get applied and what does it count"
TIMEOUT = float(os.environ.get("GOV_RERANK_TIMEOUT_S", "30"))
WARM_TEXT = "def warm(): return 'a short text to score once'"


def corpus() -> str:
    return "\n".join(open(p, encoding="utf-8").read() for p in SOURCES)


def shapes(text: str, bound: int = BOUND, max_texts: int = MAX_TEXTS):
    """(name, texts): each at the bound, count x (len(query) + len(text)) <= bound, for counts 1, 2, 4, 8, 16 up to
    max_texts."""
    out = []
    for count in (c for c in (1, 2, 4, 8, 16) if c <= max_texts):
        size = bound // count - len(QUERY)
        out.append((f"{count}x{size}", [text[i * 997 % (len(text) - size):][:size] for i in range(count)]))
    return out


def gpu_used():
    try:
        return int(subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                                  capture_output=True, text=True, timeout=10).stdout.split()[0])
    except Exception:
        return None


def ask(path: str, texts: list) -> tuple[float, str]:
    started = time.monotonic()
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.settimeout(2.0)
        try:
            s.connect(path)
        except OSError as error:
            return time.monotonic() - started, f"error: {error}"
        s.settimeout(TIMEOUT)
        s.sendall((json.dumps([QUERY, texts]) + "\n").encode())
        try:
            line = s.makefile("rb").readline()
        except socket.timeout:
            return time.monotonic() - started, "timeout"
        except OSError as error:
            return time.monotonic() - started, f"error: {error}"
    answer = json.loads(line) if line else {"error": "closed"}
    ok = "scores" in answer and len(answer["scores"]) == len(texts)
    return time.monotonic() - started, "ok" if ok else f"error: {answer.get('error')}"


def _opt(argv, name, default):
    return int(argv[argv.index(name) + 1]) if name in argv else default


def main(argv):
    path, mode = argv[1], argv[2]
    limit = _opt(argv, "--limit", 14255)
    bound, max_texts = _opt(argv, "--bound", BOUND), _opt(argv, "--max-texts", MAX_TEXTS)
    if mode == "warm":  # the live window's warm-up: one short text, so the next GPU reading is the steady state
        seconds, how = ask(path, [WARM_TEXT])
        print(f"warm-up: {how} in {seconds:.2f} s")
        return 0 if how == "ok" else 5
    text = corpus()
    cases = shapes(text, bound, max_texts)
    print(f"probe: bound {bound} padded characters, at most {max_texts} texts; limit {limit} MiB")
    if mode == "peak":
        failed = 0
        for name, texts in cases:
            before = gpu_used()
            if before is not None and before >= limit:
                print(f"STOP before {name}: GPU {before} MiB >= {limit}"); return 3
            seconds, how = ask(path, texts)
            after = gpu_used()
            print(f"{name}: {how} in {seconds:.2f} s; GPU {before} -> {after} MiB")
            failed += how != "ok"
            if after is not None and after >= limit:
                print(f"STOP after {name}: GPU {after} MiB >= {limit}"); return 3
        return 5 if failed else 0  # a shape not answered (refused, timed out, closed) is not a pass either
    n = int(argv[3])
    search = [cases[0][1], cases[min(2, len(cases) - 1)][1], cases[-1][1]]  # one search: three of the bound's shapes
    times, outcomes, peak = [], [], [gpu_used() or 0]
    stop = threading.Event()

    def sample():
        while not stop.is_set():
            peak[0] = max(peak[0], gpu_used() or 0)
            time.sleep(1)

    def client():
        for texts in search:
            seconds, how = ask(path, texts)
            times.append(seconds); outcomes.append(how)

    sampler = threading.Thread(target=sample, daemon=True); sampler.start()
    started = time.monotonic()
    threads = [threading.Thread(target=client) for _ in range(n)]
    for t in threads: t.start()
    for t in threads: t.join()
    stop.set()
    wall = time.monotonic() - started
    bad = sum(1 for o in outcomes if o != "ok")
    if not times:
        print(f"load {n}: no request answered"); return 4
    q = statistics.quantiles(times, n=20) if len(times) > 1 else times * 19
    print(f"load {n}: {len(times)} requests in {wall:.1f} s; per request p50 {statistics.median(times):.2f} s, "
          f"p95 {q[18]:.2f} s, max {max(times):.2f} s; not ok {bad} (timeouts {outcomes.count('timeout')}); "
          f"GPU peak {peak[0]} MiB")
    return 0 if bad == 0 and peak[0] < limit else 4


if __name__ == "__main__":
    sys.exit(main(sys.argv))
