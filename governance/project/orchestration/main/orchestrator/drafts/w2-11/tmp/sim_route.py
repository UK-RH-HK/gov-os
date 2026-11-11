"""Read-only simulation of route (a): a pre-merge commit on w2/W2-11 for the conflicted source files, then
git merge-tree of that synthetic commit with w2/integrate.  Objects only (loose blobs, trees, one commit per
strategy); no ref, no branch, no worktree, no index of the repository is touched (a private GIT_INDEX_FILE).

Strategies for the pre-merge content of each conflicted source file:
  theirs  = integrate's whole file (the form that cannot conflict by construction)
  union   = git merge-file --union of (ours, base, theirs): a mixture of both sides, the form a W1-35-style
            "place W2-11's text clear of integrate's lines" commit would have at best
  ours    = leave W2-11's file as it is (control: the conflicts of today)
Prints the conflict list of each."""
import os
import subprocess
import sys
import tempfile

REPO = "/home/usain/Dynamic-Agentic-Engineering-OS"
TMP = REPO + "/.gov-runtime/scratch/orchestrator/drafts/w2-11/tmp/sim"
os.makedirs(TMP, exist_ok=True)
W, I = sys.argv[1], sys.argv[2]
GENERATED = {".claude/skills/orchestration/SKILL.md", ".claude/skills/test-design/SKILL.md"}


def git(*args, env=None, check=True, inp=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    r = subprocess.run(["git", "-C", REPO, *args], capture_output=True, env=e, input=inp)
    if check and r.returncode not in (0,):
        raise SystemExit("git %s failed: %s" % (args, r.stderr.decode()[:300]))
    return r


base = git("merge-base", W, I).stdout.decode().strip()
mt = git("merge-tree", "--write-tree", "--name-only", W, I, check=False).stdout.decode().splitlines()
conflicted = []
for line in mt:
    if line.startswith("CONFLICT") and "Merge conflict in " in line:
        conflicted.append(line.split("Merge conflict in ", 1)[1].strip())
print("base", base[:12], "conflicted", len(conflicted))
sources = [p for p in conflicted if p not in GENERATED]


def blob(rev, path):
    r = git("rev-parse", "%s:%s" % (rev, path), check=False)
    return r.stdout.decode().strip() if r.returncode == 0 else None


def content(rev, path):
    return git("cat-file", "blob", "%s:%s" % (rev, path)).stdout


def run(strategy):
    idx = tempfile.mktemp(dir=TMP)
    env = {"GIT_INDEX_FILE": idx}
    git("read-tree", W, env=env)
    for path in sources:
        if strategy == "ours":
            continue
        if strategy == "theirs":
            oid = blob(I, path)
        else:
            files = []
            for rev in (W, base, I):
                f = tempfile.mktemp(dir=TMP)
                open(f, "wb").write(content(rev, path))
                files.append(f)
            out = subprocess.run(["git", "merge-file", "-p", "--union", *files], capture_output=True).stdout
            oid = git("hash-object", "-w", "--stdin", inp=out).stdout.decode().strip()
            for f in files:
                os.remove(f)
        git("update-index", "--add", "--cacheinfo", "100644,%s,%s" % (oid, path), env=env)
    tree = git("write-tree", env=env).stdout.decode().strip()
    os.remove(idx)
    commit = git("commit-tree", tree, "-p", W, "-m", "synthetic %s" % strategy,
                 env={"GIT_AUTHOR_NAME": "sim", "GIT_AUTHOR_EMAIL": "sim@example.invalid",
                      "GIT_COMMITTER_NAME": "sim", "GIT_COMMITTER_EMAIL": "sim@example.invalid"}).stdout.decode().strip()
    res = git("merge-tree", "--write-tree", "--name-only", commit, I, check=False).stdout.decode().splitlines()
    left = sorted(l.split("Merge conflict in ", 1)[1] for l in res if "Merge conflict in " in l)
    print("== strategy %-6s synthetic %s: %d conflict(s)" % (strategy, commit[:12], len(left)))
    for p in left:
        print("   ", p)
    return commit


for s in ("ours", "union", "theirs"):
    run(s)
