"""W2-54 round 3, after the change (num_gpu: 0 for a question): is the query vector a read uses the same bytes
whatever was embedded before it, by this process or another, and whatever the cache's state? Against the Ollama at
OLLAMA_HOST (default 127.0.0.1:11434), through gov.retrieval.semantic.query_vector (the entry semantic.search
calls). Never committed. Run by the lead outside the sandbox:

    PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 <this file>

NOTE for the shared server: a question's request names num_gpu: 0, so the first one reloads the model on the CPU if
it is loaded on the GPU (about a second), and Ollama then serves every client's default-option requests from that CPU
runner until the model is unloaded (idle keep-alive). The script prints where the model sits before and after.

Everything it writes is in a temporary folder of its own (made with tempfile.mkdtemp, removed at the end): two
projects (each only a `.gov-runtime/` folder: query_vector needs no store), one whose cache is writable, one whose
`.gov-runtime/` is read-only.
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
HOST = os.environ.get("OLLAMA_HOST") or ollama.DEFAULT_HOST
I = semantic.INSTRUCTION
TEXTS = ["context", "The context packet's dropped list in a stable order", "who reads the harbour tide tables",
         "the audit-report type exactly as W2-02 defines it", "how is a query vector cached", "café au lait"]
QUESTIONS = ["when are the pear trees pruned", "which check declares a time limit", "what does the guard refuse"]
CHUNK = "# Governance\n\nThis project uses the Gov OS governance framework. All changes follow the Contract."
KINDS = ["question0", "question1", "question2", "chunk", "text alone", "longer prefix", "longer prefix, other end",
         "read repeated", "nothing"]


def floats(blob):
    return struct.unpack(f"{len(blob) // 4}f", blob)


def largest(one, two):
    return max(abs(a - b) for a, b in zip(floats(one), floats(two)))


def short(blob):
    return hashlib.sha256(blob).hexdigest()[:10]


def placement():
    models = (semantic._ask("/api/ps") or {}).get("models") or []
    return [f"{m.get('name')} size {m.get('size')} size_vram {m.get('size_vram')}" for m in models] or ["none loaded"]


def before(kind, text):
    """What comes before the read, as a default-option request (as the index build and other clients send): another
    question, a chunk, the text itself, a text sharing all but the text's last word with it, or nothing."""
    words = text.split()
    head = I + " ".join(words[:-1]) if len(words) > 1 else I + text[:-1]
    sent = {"chunk": CHUNK, "text alone": I + text, "longer prefix": head,
            "longer prefix, other end": head + " and something else entirely"}.get(kind)
    if kind.startswith("question"):
        sent = I + QUESTIONS[int(kind[-1])]
    if sent is not None and semantic._embed([sent]) is None:
        sys.exit("Ollama did not embed")


def reader(args):
    """One process's reads at once with others: the text after a noise request, through query_vector."""
    root, text, n, seed = args
    out = []
    for k in range(n):
        before(KINDS[(seed + k) % 4], text)
        out.append(semantic.query_vector(Path(root), text))
    return out


def noise(seconds):
    """Another client meanwhile: default-option requests of several shapes, the instruction and texts' prefixes."""
    end, k = time.monotonic() + seconds, 0
    while time.monotonic() < end:
        semantic._embed([CHUNK, I + QUESTIONS[k % 3], I + TEXTS[k % len(TEXTS)][:9]])
        k += 1
    return k


def main():
    version = semantic._ask("/api/version")
    if version is None:
        sys.exit(f"Ollama does not answer at {HOST}")
    print(f"ollama {version.get('version')} at {HOST}; {semantic.MODEL} digest {semantic._revision()}")
    print(f"query options {semantic.QUERY_OPTIONS}; bound {semantic._bound()} bytes; cache {semantic.QUERY_VECTORS_REL}")
    print("loaded before:", placement())
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
        first = semantic.query_vector(unwritable, TEXTS[0])
        print(f"first question request {time.monotonic() - t:.2f}s; loaded after it:", placement())
        t = time.monotonic()
        semantic._embed([CHUNK])
        print(f"a default-option request after it {time.monotonic() - t:.2f}s; loaded:", placement())
        totals = {"runs": 0, "differed": 0, "largest": 0.0}
        references = {}
        started = time.monotonic()
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
                            semantic.query_vector(root, text)
                        before(kind, text)
                        vector = semantic.query_vector(root, text)
                        if vector is None:
                            sys.exit("the read got no vector")
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
        print(f"seconds {time.monotonic() - started:.1f}; the writable cache holds "
              f"{(writable / semantic.QUERY_VECTORS_REL).stat().st_size} bytes; first == reference: "
              f"{first == references[TEXTS[0]]}")
        print("loaded after:", placement())
    finally:
        (unwritable / ".gov-runtime").chmod(0o755)
        shutil.rmtree(box)


if __name__ == "__main__":
    main()
