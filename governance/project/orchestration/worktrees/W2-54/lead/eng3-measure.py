"""W2-54 round 3: is the query vector a read uses the same bytes whatever was embedded before it, and whatever the
cache's state? Against this machine's Ollama at its default address, through gov.retrieval.semantic.query_vector
(the entry semantic.search calls). Never committed; run by the lead outside the sandbox:

    PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 /home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/eng3/measure.py

Two temporary projects are made in a temporary folder (each only a `.gov-runtime/` folder: query_vector needs no
store): one whose cache is writable, one whose `.gov-runtime/` is read-only. Nothing else is written.
"""
import os
import shutil
import struct
import sys
import tempfile
import time
from pathlib import Path

from gov.retrieval import ollama, semantic

os.environ.pop("OLLAMA_HOST", None)  # the default address
os.environ.pop(semantic.CACHE_BOUND_SETTING, None)  # the default bound
I = semantic.INSTRUCTION
TEXTS = ["context", "The context packet's dropped list in a stable order", "who reads the harbour tide tables",
         "the audit-report type exactly as W2-02 defines it", "how is a query vector cached", "café au lait"]
QUESTIONS = ["when are the pear trees pruned", "which check declares a time limit", "what does the guard refuse"]
CHUNK = "# Governance\n\nThis project uses the Gov OS governance framework. All changes follow the Contract."
KINDS = ["question0", "question1", "question2", "chunk", "text alone", "read repeated"]


def floats(blob):
    return struct.unpack(f"{len(blob) // 4}f", blob)


def largest(one, two):
    return max(abs(a - b) for a, b in zip(floats(one), floats(two)))


def before(kind, text):
    """Send what comes before the read: another question, a chunk, the text alone, or nothing (the read repeated)."""
    sent = {"chunk": CHUNK, "text alone": I + text}.get(kind) or (I + QUESTIONS[int(kind[-1])]
                                                                 if kind.startswith("question") else None)
    if sent is not None and semantic._embed([sent]) is None:
        sys.exit("Ollama did not embed")


def main():
    version = semantic._ask("/api/version")
    if version is None:
        sys.exit(f"Ollama does not answer at {ollama.DEFAULT_HOST}")
    print(f"ollama {version.get('version')} at {ollama.DEFAULT_HOST}; {semantic.MODEL} digest {semantic._revision()}")
    print(f"bound {semantic._bound()} bytes; cache {semantic.QUERY_VECTORS_REL}")
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
        totals = {"runs": 0, "differed": 0, "largest": 0.0}
        raw = {"runs": 0, "differed": 0, "largest": 0.0}
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
            # The embedder alone, for comparison: the text right after another question, against its repeat.
            for n in range(3):
                before(f"question{n}", text)
                first, repeat = semantic._embed([I + text])[0], semantic._embed([I + text])[0]
                raw["runs"] += 1
                raw["differed"] += first != repeat
                raw["largest"] = max(raw["largest"], largest(first, repeat))
        if (unwritable / semantic.QUERY_VECTORS_REL).exists():
            sys.exit("a cache was made in the read-only folder")
        print(f"ALL the read's vector: runs {totals['runs']}  differed from the text's first {totals['differed']}  "
              f"largest component difference {totals['largest']:.6f}")
        print(f"RAW the embedder alone, first after another question vs repeat: runs {raw['runs']}  "
              f"differed {raw['differed']}  largest {raw['largest']:.6f}")
        print(f"seconds {time.monotonic() - started:.1f}; the writable cache holds "
              f"{(writable / semantic.QUERY_VECTORS_REL).stat().st_size} bytes")
    finally:
        (unwritable / ".gov-runtime").chmod(0o755)
        shutil.rmtree(box)


if __name__ == "__main__":
    main()
