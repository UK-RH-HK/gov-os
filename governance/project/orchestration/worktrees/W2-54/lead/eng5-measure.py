"""W2-54 round 4, after the change (DEC-798): is the query vector a read uses the same bytes whatever was embedded
before it, by this process or another, and whatever the cache's state, now that a question is embedded by the CPU-only
embedder at GOV_QUERY_OLLAMA_HOST (default 127.0.0.1:11435) and the shared runner at OLLAMA_HOST (default
127.0.0.1:11434) only builds the index? Through gov.retrieval.semantic.query_vector (the entry semantic.search calls).
Never committed. Run by the lead outside the sandbox, with neither address set:

    env -u OLLAMA_HOST -u GOV_QUERY_OLLAMA_HOST PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 <this file>

It starts the CPU-only embedder if nothing answers at its address (DEC-261 as DEC-798 amends it: never stopped; the
lead decides whether to stop it afterwards). No request it sends to the shared runner names an option. It prints where
the model sits on the shared runner (``size_vram`` against ``size``) before and after, and the CPU embedder's port and
placement. The predecessors of a read are sent where other clients would send them: other questions to the CPU
embedder (another session's reads), chunks to the shared runner (an index build) and to the CPU embedder.

Everything it writes is in a temporary folder of its own (made with tempfile.mkdtemp, removed at the end): two
projects (each only a `.gov-runtime/` folder: query_vector needs no store), one whose cache is writable, one whose
`.gov-runtime/` is read-only. It never reads or deletes the worktree's cache file. Exit code 0 only when every read
gave its text's one vector and the shared runner held the model wholly on the GPU before and after.
"""
import hashlib
import multiprocessing as mp
import os
import shutil
import struct
import sys
import tempfile
import time
from pathlib import Path

from gov.retrieval import ollama, semantic

os.environ.pop(semantic.CACHE_BOUND_SETTING, None)  # the default bound
SHARED = os.environ.get("OLLAMA_HOST") or ollama.DEFAULT_HOST
CPU = ollama.query_host()
I = semantic.INSTRUCTION
TEXTS = ["context", "The context packet's dropped list in a stable order", "who reads the harbour tide tables",
         "the audit-report type exactly as W2-02 defines it", "how is a query vector cached", "café au lait"]
QUESTIONS = ["when are the pear trees pruned", "which check declares a time limit", "what does the guard refuse"]
CHUNK = "# Governance\n\nThis project uses the Gov OS governance framework. All changes follow the Contract."
KINDS = ["question0", "question1", "question2", "chunk on the shared runner", "chunk on the CPU embedder",
         "text alone", "longer prefix", "longer prefix, other end", "read repeated", "nothing"]


def floats(blob):
    return struct.unpack(f"{len(blob) // 4}f", blob)


def largest(one, two):
    return max(abs(a - b) for a, b in zip(floats(one), floats(two)))


def short(blob):
    return hashlib.sha256(blob).hexdigest()[:10]


def placement(host):
    models = (semantic._ask("/api/ps", host=host) or {}).get("models") or []
    return [f"{m.get('name')} size {m.get('size')} size_vram {m.get('size_vram')}" for m in models] or ["none loaded"]


def shared_on_gpu():
    models = (semantic._ask("/api/ps", host=SHARED) or {}).get("models") or []
    return any(m.get("name") == semantic.MODEL and (m.get("size") or 0) > 0 and m.get("size_vram") == m.get("size")
               for m in models)


def embed(texts, host):
    if semantic._embed(texts, host) is None:
        sys.exit(f"Ollama did not embed at {host}")


def before(kind, text):
    """What comes before the read: another question, a chunk, the text itself, a text sharing all but the text's last
    word with it, or nothing; each a request with no option, at the address another client would use."""
    words = text.split()
    head = I + " ".join(words[:-1]) if len(words) > 1 else I + text[:-1]
    if kind.startswith("question"):
        embed([I + QUESTIONS[int(kind[-1])]], CPU)
    elif kind == "chunk on the shared runner":
        embed([CHUNK], SHARED)
    elif kind == "chunk on the CPU embedder":
        embed([CHUNK], CPU)
    elif kind in ("text alone", "longer prefix", "longer prefix, other end"):
        embed([{"text alone": I + text, "longer prefix": head,
                "longer prefix, other end": head + " and something else entirely"}[kind]], CPU)


def read(root, text):
    vector, reason = semantic.query_vector(Path(root), text)
    if vector is None:
        sys.exit(f"the read got no vector: {reason}")
    return vector


def reader(args):
    """One process's reads at once with others: the text after a noise request, through query_vector."""
    root, text, n, seed = args
    out = []
    for k in range(n):
        before(KINDS[(seed + k) % 5], text)
        out.append(read(root, text))
    return out


def noise(seconds):
    """Another client meanwhile: requests of several shapes to both addresses, the instruction and texts' prefixes."""
    end, k = time.monotonic() + seconds, 0
    while time.monotonic() < end:
        semantic._embed([CHUNK, I + QUESTIONS[k % 3], I + TEXTS[k % len(TEXTS)][:9]], CPU if k % 2 else SHARED)
        k += 1
    return k


def main():
    version = semantic._ask("/api/version", host=SHARED)
    if version is None:
        sys.exit(f"the shared Ollama does not answer at {SHARED}")
    t = time.monotonic()
    started = ollama.ensure_query_available()
    if not started["available"]:
        sys.exit(f"the CPU embedder does not answer at {CPU}")
    print(f"shared: ollama {version.get('version')} at {SHARED}; {semantic.MODEL} digest {semantic._revision(SHARED)}")
    print(f"CPU embedder: at {CPU} (port {CPU.rsplit(':', 1)[-1]}), started by this run: {started['started']} "
          f"({time.monotonic() - t:.2f}s); digest {semantic._revision(CPU)}")
    print(f"bound {semantic._bound()} bytes; cache {semantic.QUERY_VECTORS_REL} (in this run's own folders only)")
    gpu_before = shared_on_gpu()
    print("shared runner loaded before:", placement(SHARED), "wholly on the GPU:", gpu_before)
    print("CPU embedder loaded before:", placement(CPU))
    box = Path(tempfile.mkdtemp(prefix="w2-54-measure-"))
    writable, unwritable = box / "writable", box / "unwritable"
    for root in (writable, unwritable):
        (root / ".gov-runtime").mkdir(parents=True)
    (unwritable / ".gov-runtime").chmod(0o555)
    try:
        try:
            (unwritable / ".gov-runtime" / "probe").touch()
            sys.exit("the premise: a file could be made in the read-only .gov-runtime/ (run as root?)")
        except OSError:
            pass
        t = time.monotonic()
        first = read(unwritable, TEXTS[0])
        print(f"first question request {time.monotonic() - t:.2f}s; CPU embedder after it:", placement(CPU))
        t = time.monotonic()
        embed([CHUNK], SHARED)
        print(f"a chunk to the shared runner after it {time.monotonic() - t:.2f}s; shared:", placement(SHARED))
        totals = {"runs": 0, "differed": 0, "largest": 0.0}
        references = {}
        began = time.monotonic()
        for text in TEXTS:
            reference = None
            for state in ("cold", "written", "unwritable"):
                runs, differed, worst = 0, 0, 0.0
                for kind in KINDS:
                    for _ in range(2):
                        cache = writable / semantic.QUERY_VECTORS_REL
                        if state == "cold" and cache.exists():
                            cache.unlink()
                        root = unwritable if state == "unwritable" else writable
                        if kind == "read repeated":
                            read(root, text)
                        before(kind, text)
                        vector = read(root, text)
                        reference = reference or vector
                        runs += 1
                        differed += vector != reference
                        worst = max(worst, largest(vector, reference))
                print(f"{state:10} {text[:40]!r:44} runs {runs:3}  differed {differed:3}  largest {worst:.6f}")
                totals["runs"] += runs
                totals["differed"] += differed
                totals["largest"] = max(totals["largest"], worst)
            references[text] = reference
        print(f"ALL one process: runs {totals['runs']}  differed from the text's first {totals['differed']}  "
              f"largest component difference {totals['largest']:.6f}")
        # Two processes reading at once (the cache unwritable, so each computes), a third client meanwhile.
        runs = differed = 0
        for text in TEXTS:
            with mp.Pool(3) as pool:
                hammer = pool.apply_async(noise, (8,))
                results = pool.map(reader, [(str(unwritable), text, 8, seed) for seed in range(2)])
                noised = hammer.get()
            for vector in (v for r in results for v in r):
                runs += 1
                differed += vector != references[text]
            print(f"two processes at once {text[:40]!r:44} reads {sum(map(len, results))}  noise requests {noised}  "
                  f"vectors {sorted({short(v) for r in results for v in r})}  reference {short(references[text])}")
        print(f"ALL two processes: runs {runs}  differed from the one-process reference {differed}")
        if (unwritable / semantic.QUERY_VECTORS_REL).exists():
            sys.exit("a cache was made in the read-only folder")
        print(f"seconds {time.monotonic() - began:.1f}; the writable cache holds "
              f"{(writable / semantic.QUERY_VECTORS_REL).stat().st_size} bytes; first == reference: "
              f"{first == references[TEXTS[0]]}")
        gpu_after = shared_on_gpu()
        print("shared runner loaded after:", placement(SHARED), "wholly on the GPU:", gpu_after)
        print(f"CPU embedder at {CPU} loaded after:", placement(CPU))
        ok = totals["differed"] == 0 and differed == 0 and first == references[TEXTS[0]] and gpu_before and gpu_after
        print("VERDICT:", "GREEN" if ok else "RED", f"(differed {totals['differed']} + {differed}; shared on the GPU "
              f"before {gpu_before}, after {gpu_after})")
        return 0 if ok else 1
    finally:
        (unwritable / ".gov-runtime").chmod(0o755)
        shutil.rmtree(box)


if __name__ == "__main__":
    sys.exit(main())
