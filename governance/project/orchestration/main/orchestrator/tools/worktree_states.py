#!/usr/bin/env python3
"""DEC-1087 (7): every worktree of the repository with its state, as a Markdown table on stdout.
  merged-clean   its branch's head is in w2/integrate and `git status --porcelain` is empty: removable
  unmerged       its head is not in w2/integrate (work that is only there)
  uncommitted    it has changes not committed (listed by count, never removed)
  in-use         a store half, the record branch, the main tree, or a worktree named in --keep: kept whatever it is
Read-only; with --remove it runs `git worktree remove` (no --force) on the merged-clean ones only, keeping branches.
    worktree_states.py [--keep <path> ...] [--remove]
"""
import subprocess
import sys

REPO = "/home/usain/Dynamic-Agentic-Engineering-OS"
INUSE = {REPO, "/home/usain/gov-os-worktrees/W2-00-record", "/home/usain/gov-os-worktrees/W2-00-store-a",
         "/home/usain/gov-os-worktrees/W2-00-store-b"}


def git(*args, cwd=REPO):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


keep = set()
args = sys.argv[1:]
while "--keep" in args:
    i = args.index("--keep")
    keep.add(args[i + 1].rstrip("/"))
    del args[i:i + 2]
remove = "--remove" in args

trees, cur = [], {}
for line in git("worktree", "list", "--porcelain").stdout.splitlines() + [""]:
    if not line:
        if cur:
            trees.append(cur)
        cur = {}
    elif line.startswith("worktree "):
        cur["path"] = line[9:]
    elif line.startswith("HEAD "):
        cur["head"] = line[5:]
    elif line.startswith("branch "):
        cur["branch"] = line[7:].replace("refs/heads/", "")
    elif line == "detached":
        cur["branch"] = "(detached)"

rows, removable = [], []
for t in trees:
    path, head, branch = t["path"], t.get("head", ""), t.get("branch", "?")
    dirty = [l for l in git("status", "--porcelain", "--untracked-files=no", cwd=path).stdout.splitlines() if l]
    merged = git("merge-base", "--is-ancestor", head, "w2/integrate").returncode == 0
    if path in INUSE or path in keep:
        state = "in-use"
    elif dirty:
        state = "uncommitted (%d)" % len(dirty)
    elif not merged:
        ahead = git("rev-list", "--count", "w2/integrate.." + head).stdout.strip()
        state = "unmerged (%s commits not in integrate)" % ahead
    else:
        state = "merged-clean"
        removable.append(path)
    rows.append((path.replace("/home/usain/gov-os-worktrees/", ""), branch, head[:9], state))

print("| worktree | branch | head | state |")
print("|---|---|---|---|")
for r in rows:
    print("| %s | %s | %s | %s |" % r)
counts = {}
for r in rows:
    counts[r[3].split(" (")[0]] = counts.get(r[3].split(" (")[0], 0) + 1
print("\n" + "; ".join("%s %d" % kv for kv in sorted(counts.items())) + "; of %d" % len(rows))
if remove:
    import os
    archive = "/home/usain/gov-os-runs/worktree-archive"
    os.makedirs(archive, exist_ok=True)
    for path in removable:
        scratch = os.path.join(path, ".gov-runtime/scratch")
        if os.path.isdir(scratch):  # its logs, briefs and returns (ignored by git) are kept; its stores can be rebuilt
            tgz = os.path.join(archive, os.path.basename(path) + "-scratch.tgz")
            t = subprocess.run(["tar", "-czf", tgz, "-C", path, ".gov-runtime/scratch"], capture_output=True, text=True)
            if t.returncode != 0:
                print("NOT removed (scratch not archived: %s) %s" % (t.stderr.strip()[:120], path))
                continue
        r = git("worktree", "remove", path)
        print(("removed " if r.returncode == 0 else "NOT removed (%s) " % r.stderr.strip()) + path)
