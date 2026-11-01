"""One table row per measure: wall, load (mean, min, max of the 1-minute load), the freshness and status checks'
time (semantic._status plus lexical.freshness when not called from _status), query embedding (semantic.query_vector),
the embedder's calls, and the verdict. usage: proftable.py <tag> [<tag> ...]"""
import pstats
import sys

PROF = "/tmp/gov-os-lead-W2-108/prof/"


def find(stats, file, func):
    for key, value in stats.stats.items():
        if key[0].endswith("/" + file) and key[2] == func:
            return key, value
    return None, None


print("| run | code | wall s | load mean (min-max) | freshness+status s | query embedding s | embedder calls | verdict |")
print("|---|---|---|---|---|---|---|---|")
for tag in sys.argv[1:]:
    wall = open(PROF + tag + ".wall").read().strip()
    loads = [float(line.split()[1]) for line in open(PROF + tag + ".load") if len(line.split()) == 4]
    stats = pstats.Stats(PROF + tag + ".prof")
    _, status = find(stats, "semantic.py", "_status")
    fkey, fresh = find(stats, "lexical.py", "freshness")
    outside = 0.0
    if fresh:
        for caller, cvalue in fresh[4].items():
            if caller[2] != "_status":
                outside += cvalue[3]
    total = (status[3] if status else 0.0) + outside
    _, qv = find(stats, "semantic.py", "query_vector")
    _, emb = find(stats, "semantic.py", "_embed")
    verdict = open(PROF + tag + ".out").read().strip().splitlines()[-1]
    code = "base f6af39c1665b" if tag.startswith("before") else "W2-108 ee5056be590a"
    print("| %s | %s | %s | %.1f (%.1f-%.1f) | %.1f | %.1f | %d | %s |" % (
        tag, code, wall, sum(loads) / len(loads), min(loads), max(loads), total, qv[3] if qv else 0.0,
        emb[1] if emb else 0, verdict))
