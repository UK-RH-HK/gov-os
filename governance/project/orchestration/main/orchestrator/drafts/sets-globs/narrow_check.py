"""ACT-SETS-GLOBS-1: the candidate hook's Narrow walk finds exactly the files the judge's own walk finds, faster.

  python3 narrow_check.py <hook> <tree> <planted sets root> <map>

For each tree of <tree> (the hook's tree_roots: every worktree and run clone) and the planted sets root, and for a
synthetic tree built here (sets with and without hidden/, XCHECK files at several depths, a .git folder, links to a
folder and to a file, a folder named like a file glob, a deeper miss-classes.json), it builds the judge's _Part and the
hook's Narrow over the same globs (the map's sets_root_hidden globs, live and new) and compares their file lists. It
prints the counts and the times; names never (the planted root and the trees hold dummy or repository files only).
Last line PASS or FAIL.
"""
import importlib.util
import os
import sys
import tempfile
import time

hook_path, tree, planted, map_path = sys.argv[1:5]
spec = importlib.util.spec_from_file_location("hook", hook_path)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)
from gov.guard import reads  # noqa: E402

SetsRoot, Judge, Narrow = hook.classes()
import yaml  # noqa: E402

globs = yaml.safe_load(open(map_path))["sets_root_hidden"]["hidden"]
ok = True


def synthetic(d):
    files = ["fixtures/evaluation/a/hidden/q1.yaml", "fixtures/evaluation/a/hidden/sub/q2.yaml",
             "fixtures/evaluation/a/visible/q1.yaml", "fixtures/evaluation/a/XCHECK-r1.md",
             "fixtures/evaluation/a/XCHECK.md", "fixtures/evaluation/a/sub/XCHECK-r2.md",
             "fixtures/evaluation/b/hidden-notes.md", "fixtures/evaluation/b/hidden/.git/x",
             "fixtures/evaluation/.git/hidden/x", "fixtures/evaluation/memory-verdict/x.yaml",
             "runs/r1/miss-classes.json", "runs/r1/misses.jsonl", "runs/r1/deep/miss-classes.json",
             "runs/miss-classes.json/inner.txt", "runs/r2/miss-classes.json/inner.txt", "runs/fresh-80/rows/q.json",
             "transcripts/t.md", "indep-walls/w/x"]
    for rel in files:
        p = os.path.join(d, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write("x\n")
    os.symlink(os.path.join(d, "fixtures/evaluation/a"), os.path.join(d, "fixtures/evaluation/link-set"))
    os.symlink(os.path.join(d, "runs/r1/miss-classes.json"), os.path.join(d, "runs/r3-link"))
    os.makedirs(os.path.join(d, "runs/r4"))
    os.symlink(os.path.join(d, "runs/r1/miss-classes.json"), os.path.join(d, "runs/r4/miss-classes.json"))
    for rel in ("runs/r5", "runs/r6", "fixtures/evaluation/c", "elsewhere/h", "runs/r7/misses.jsonl"):
        os.makedirs(os.path.join(d, rel), exist_ok=True)
    open(os.path.join(d, "elsewhere/h/q.yaml"), "w").write("x\n")
    open(os.path.join(d, "runs/r7/misses.jsonl/inner.txt"), "w").write("x\n")  # a folder named like the file
    os.symlink(os.path.join(d, "nowhere"), os.path.join(d, "runs/r5/misses.jsonl"))  # a broken link
    os.symlink(os.path.join(d, "elsewhere/h"), os.path.join(d, "runs/r6/miss-classes.json"))  # a link to a folder
    os.symlink(os.path.join(d, "elsewhere/h"), os.path.join(d, "fixtures/evaluation/c/hidden"))  # hidden/ a link
    os.symlink(os.path.join(d, "runs/r1"), os.path.join(d, "runs/r8"))  # a run folder that is a link


def compare(label, root, gl):
    global ok
    t0 = time.monotonic()
    a = reads._Part(root, gl, reads.HIDDEN_REFUSAL).files
    t1 = time.monotonic()
    b = Narrow(root, gl, reads.HIDDEN_REFUSAL).files
    t2 = time.monotonic()
    same = a == b
    ok &= same
    return same, len(a), (t1 - t0) * 1000, (t2 - t1) * 1000


with tempfile.TemporaryDirectory() as d:
    synthetic(d)
    for gl_label, gl in (("live globs", [g for g in globs if g.count("*") <= 2 and "/*/" not in g]), ("map globs", globs)):
        same, n, ta, tb = compare("synthetic", d, gl)
        print(f"{'ok  ' if same else 'FAIL'} synthetic tree, {gl_label}: {n} files, judge {ta:.1f} ms, Narrow {tb:.1f} ms")
roots = hook._tree_roots(tree)
for gl_label, gl in (("live globs", [g for g in globs if "/*/" not in g]), ("map globs", globs)):
    tot_a = tot_b = 0.0
    nfiles = 0
    bad = 0
    for r in roots + [planted]:
        same, n, ta, tb = compare(r, r, gl)
        tot_a += ta
        tot_b += tb
        nfiles += n
        bad += not same
    print(f"{'ok  ' if not bad else 'FAIL'} {len(roots)} trees and the planted root, {gl_label} ({len(gl)}): {nfiles} files; "
          f"lists differ: {bad}; judge {tot_a:.0f} ms, Narrow {tot_b:.0f} ms")
# match: Narrow's (kept per path, a prefix filter first) against the judge's, on every path of the tree's HEAD and a
# set of edge paths, for the live and the map globs, over every tree's part (as a revision's listing asks it)
import subprocess  # noqa: E402

names = [n for n in subprocess.run(["git", "-C", tree, "ls-tree", "-r", "--full-tree", "--name-only", "-z", "HEAD"],
                                   capture_output=True, text=True).stdout.split("\0") if n]
names += ["fixtures/evaluation/zz/hidden", "fixtures/evaluation/zz/hidden/q.yaml", "fixtures/evaluation/zz/hiddenx/q",
          "fixtures/evaluation/zz/XCHECK-r1.md", "fixtures/evaluation/zz/XCHECK.md", "fixtures/evaluation/a/b/hidden/q",
          "fixtures/evaluation", "fixtures", "runs", "runs/a/miss-classes.json", "runs/a/miss-classes.json/x",
          "runs/a/b/miss-classes.json", "runs/a/misses.jsonl", "runs/a/b/misses.jsonl", "runs/fresh-80", "runs/fresh-80/x", "runs/fresh-80b/x", "transcripts",
          "transcripts/x", "indep-walls/w/x", "fixtures/evaluation/memory-verdict-2/p.yaml", "", None]
for gl_label, gl in (("live globs", [g for g in globs if "/*/" not in g]), ("map globs", globs)):
    t0 = time.monotonic()
    base = [reads._Part(r, gl, reads.HIDDEN_REFUSAL) for r in roots]
    a = [[p.match(n) for n in names] for p in base]
    t1 = time.monotonic()
    nar = [Narrow(r, gl, reads.HIDDEN_REFUSAL) for r in roots]
    b = [[p.match(n) for n in names] for p in nar]
    t2 = time.monotonic()
    same = a == b
    ok &= same
    print(f"{'ok  ' if same else 'FAIL'} match, {gl_label}: {len(names)} paths x {len(roots)} parts; matched "
          f"{sum(a[0])}; answers differ: {sum(x != y for ra, rb in zip(a, b) for x, y in zip(ra, rb))}; "
          f"judge {(t1 - t0) * 1000:.0f} ms, Narrow {(t2 - t1) * 1000:.0f} ms")
print("PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
