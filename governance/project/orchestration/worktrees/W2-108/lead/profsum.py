"""Summarise one measure: wall time, the load during it, and cProfile's cumulative time in the freshness checks,
the status, the query embedding and the retrieval calls. usage: profsum.py <tag> [<tag> ...]"""
import pstats
import sys

PROF = "/tmp/gov-os-lead-W2-108/prof/"
WANTED = [
    ("semantic.py", "_status"), ("semantic.py", "_wanted"), ("semantic.py", "embedded"),
    ("lexical.py", "freshness"), ("lexical.py", "_tracked"),
    ("semantic.py", "query_vector"), ("semantic.py", "_embed"),
    ("semantic.py", "search"), ("lexical.py", "search"), ("retrieve.py", "retrieve"),
]


def load(tag):
    rows = []
    with open(PROF + tag + ".load") as f:
        for line in f:
            parts = line.split()
            if len(parts) == 4:
                rows.append(float(parts[1]))
    return rows


for tag in sys.argv[1:]:
    wall = open(PROF + tag + ".wall").read().strip()
    code = open(PROF + tag + ".exit").read().strip()
    loads = load(tag)
    print("== %s: wall %s s, exit %s, 1-min load mean %.1f min %.1f max %.1f over %d samples" % (
        tag, wall, code, sum(loads) / len(loads), min(loads), max(loads), len(loads)))
    stats = pstats.Stats(PROF + tag + ".prof")
    total = stats.total_tt
    print("   profiled total %.1f s" % total)
    for (fname, line, func), (cc, nc, tt, ct, callers) in sorted(stats.stats.items()):
        for want_file, want_func in WANTED:
            if fname.endswith("/" + want_file) and func == want_func:
                print("   %-14s %-14s calls %9d  cumulative %8.1f s" % (want_file, func, nc, ct))
    extra = [(ct, nc, fname, func) for (fname, line, func), (cc, nc, tt, ct, callers) in stats.stats.items()
             if fname.endswith(("/semantic.py", "/lexical.py")) and (fname.rsplit("/", 1)[1], func) not in WANTED]
    for ct, nc, fname, func in sorted(extra, reverse=True)[:8]:
        print("   (other) %-14s %-24s calls %9d  cumulative %8.1f s" % (fname.rsplit("/", 1)[1], func, nc, ct))
    out = open(PROF + tag + ".out").read().strip().splitlines()
    print("   last line: %s" % (out[-1] if out else "(none)"))
