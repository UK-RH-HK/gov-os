"""For each ticket branch given, every merge commit on it (since its fork from w2/integrate's history) and the number
of merge bases between its two parents; more than one is the shape containment's DEC-918 rule reads as all-own."""
import subprocess
import sys

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS"


def git(*a):
    return subprocess.run(["git", "-C", ROOT, *a], capture_output=True, text=True).stdout.split()


for br in sys.argv[1:]:
    merges = git("rev-list", "--merges", "--max-count=6", br)
    out = []
    for m in merges:
        p = git("rev-list", "--parents", "-n", "1", m)[1:]
        if len(p) < 2:
            continue
        bases = git("merge-base", "--all", p[0], p[1])
        out.append("%s:%d" % (m[:10], len(bases)))
    print(br, " ".join(out))
