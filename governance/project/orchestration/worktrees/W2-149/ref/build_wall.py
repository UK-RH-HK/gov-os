#!/usr/bin/env python3
"""ACT-INDEP-WALLS-1: the reference wall builder. A draft for the rehearsal and for step 2's launch script
(LAUNCH-SPEC.md), not the launch script: it builds one wall from the template and launches nothing.

  python3 build_wall.py --sets-root R --kind K --run ID --repo REPO --commit C --brief B [--seed N|new]
                        [--template DIR] [--runs DIR] [--worktrees DIR] [--model M] [--since C0] [--sample N]

Order (each step refuses on failure, and leaves the wall as far as it got):
  1. the wall <R>/indep-walls/<K>/<ID> must not exist, or be an empty folder;
  2. seed.txt is written and hashed FIRST, and its line appended to <runs>/indep/SEEDS.log, before any content is
     chosen;
  3. the plain tree: `git archive <C>` less tree-exclude.txt, unpacked into <trees>/<K>-<ID> (outside the sets root, so
     the guard's walk of the hidden part never counts it); a link in it refuses; made read-only;
  4. input/selection.json: the paths changed between --since and C, plus a sample of N other tracked paths drawn by
     random.Random(seed) (DEC-1101 (2)): content by rule, not by the CTO;
  5. brief.md, CLAUDE.md, .claude/settings.json and .claude/wall_hook.py from the template; out/ empty;
  6. WALL.json: kind, run, commit, the brief's, seed's, settings', hook's and template's sha256, the selection's count.
It prints only counts and hashes, never a path's content.
"""
import argparse
import hashlib
import io
import json
import os
import random
import re
import secrets
import stat
import subprocess
import sys
import tarfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
KINDS = ("writer", "checker", "auditor", "labeller")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def stop(why):
    print(f"build_wall: refused: {why}", file=sys.stderr)
    sys.exit(3)


def excludes(template):
    lines = open(os.path.join(template, "tree-exclude.txt"), encoding="utf-8").read().splitlines()
    return [l.strip() for l in lines if l.strip() and not l.lstrip().startswith("#")]


def glob_rx(g):
    """A path-map glob as a regex: ** crosses folders, * and ? stay in one; a match at or under the glob."""
    out, i = "", 0
    while i < len(g):
        if g.startswith("**", i):
            out, i = out + ".*", i + 2
        elif g[i] == "*":
            out, i = out + "[^/]*", i + 1
        elif g[i] == "?":
            out, i = out + "[^/]", i + 1
        else:
            out, i = out + re.escape(g[i]), i + 1
    return "^" + out + "(/.*)?$"


def write_ro(path, text, mode=0o444):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    os.chmod(path, mode)


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--sets-root", required=True)
    a.add_argument("--kind", required=True, choices=KINDS)
    a.add_argument("--run", required=True)
    a.add_argument("--repo", required=True)
    a.add_argument("--commit", required=True)
    a.add_argument("--brief", required=True)
    a.add_argument("--seed", default="new")
    a.add_argument("--template", default=os.path.join(HERE, "template"))
    a.add_argument("--runs", default=os.path.expanduser("~/gov-os-runs"))
    a.add_argument("--worktrees", default=os.path.expanduser("~/gov-os-worktrees"))
    a.add_argument("--trees", default=os.path.expanduser("~/gov-os-wall-trees"))
    a.add_argument("--home", default=os.path.expanduser("~"))
    a.add_argument("--model", default="opus")
    a.add_argument("--since", default="")
    a.add_argument("--sample", type=int, default=0)
    o = a.parse_args()
    if not all(c.isalnum() or c in "-_." for c in o.run) or o.run.startswith("."):
        stop("the run id holds a character outside [A-Za-z0-9._-]")
    sr = os.path.realpath(os.path.expanduser(o.sets_root))
    walls = os.path.join(sr, "indep-walls")
    wall = os.path.join(walls, o.kind, o.run)
    repo = os.path.realpath(o.repo)
    commit = subprocess.run(["git", "-C", repo, "rev-parse", "--verify", o.commit + "^{commit}"],
                            capture_output=True, text=True).stdout.strip()
    if len(commit) != 40:
        stop("the commit does not resolve")
    # 1. an empty wall
    if os.path.lexists(wall):
        if os.path.islink(wall) or not os.path.isdir(wall) or os.listdir(wall):
            stop("the wall exists and is not an empty folder")
    os.makedirs(wall, mode=0o700, exist_ok=True)
    os.chmod(wall, 0o700)
    # 2. the seed, first
    seed = secrets.randbits(63) if o.seed == "new" else int(o.seed)
    write_ro(os.path.join(wall, "seed.txt"), f"{seed}\n")
    seed_sha = sha(os.path.join(wall, "seed.txt"))
    ledger = os.path.join(o.runs, "indep", "SEEDS.log")
    os.makedirs(os.path.dirname(ledger), exist_ok=True)
    with open(ledger, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {o.kind} {o.run} commit {commit} "
                f"seed {seed} sha256 {seed_sha}\n")
    seeded_at = time.time()
    # 3. the plain tree
    tree = os.path.join(os.path.realpath(o.trees), f"{o.kind}-{o.run}")
    if os.path.lexists(tree):
        stop("the wall's tree folder exists already")
    os.makedirs(tree, mode=0o755)
    spec = ["."] + [f":(exclude,glob){g}" for g in excludes(o.template)]
    p = subprocess.run(["git", "-C", repo, "archive", "--format=tar", commit, "--"] + spec, capture_output=True)
    if p.returncode != 0:
        stop("git archive failed: " + p.stderr.decode()[-200:])
    with tarfile.open(fileobj=io.BytesIO(p.stdout)) as t:
        for m in t.getmembers():
            if m.issym() or m.islnk() or m.name.startswith("/") or ".." in m.name.split("/"):
                stop(f"the tree holds a link or a path that climbs out ({m.name})")
        t.extractall(tree, filter="data")
    files = 0
    for folder, dirs, names in os.walk(tree):
        for n in names:
            fp = os.path.join(folder, n)
            if os.path.islink(fp):
                stop("a link in the tree")
            os.chmod(fp, 0o444)
            files += 1
    for folder, dirs, names in os.walk(tree, topdown=False):
        os.chmod(folder, 0o555)
    # 4. the selection by rule
    ex = [re.compile(glob_rx(g)) for g in excludes(o.template)]
    kept = lambda x: x and not any(r.match(x) for r in ex)
    tracked = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "--name-only", "-z", commit],
                             capture_output=True, text=True).stdout.split("\0")
    tracked = [x for x in tracked if kept(x)]
    changed = []
    if o.since:
        changed = subprocess.run(["git", "-C", repo, "diff", "--name-only", "-z", o.since, commit],
                                 capture_output=True, text=True).stdout.split("\0")
        have = set(tracked)
        changed = sorted(x for x in changed if x in have)
    rest = sorted(set(tracked) - set(changed))
    sample = sorted(random.Random(seed).sample(rest, min(o.sample, len(rest)))) if o.sample else []
    os.makedirs(os.path.join(wall, "input"))
    write_ro(os.path.join(wall, "input", "selection.json"),
             json.dumps({"commit": commit, "since": o.since, "seed_sha256": seed_sha, "changed": changed,
                         "sample": sample}, indent=1) + "\n")
    os.chmod(os.path.join(wall, "input"), 0o555)
    # 5. the session's files
    vals = {"@WALL@": wall, "@TREE@": tree, "@KIND@": o.kind, "@RUN@": o.run, "@HOME@": os.path.realpath(o.home),
            "@SETS_ROOT@": sr, "@WALLS@": walls, "@REPO@": repo, "@RUNS@": os.path.realpath(o.runs),
            "@WORKTREES@": os.path.realpath(o.worktrees), "@MODEL@": o.model, "@COMMIT@": commit,
            "@BRIEF_SHA@": sha(o.brief)}

    def fill(text):
        for k, v in vals.items():
            text = text.replace(k, v)
        return text

    write_ro(os.path.join(wall, "brief.md"), open(o.brief, encoding="utf-8").read())
    write_ro(os.path.join(wall, "CLAUDE.md"), fill(open(os.path.join(o.template, "CLAUDE.md.tmpl")).read()))
    cl = os.path.join(wall, ".claude")
    os.makedirs(cl)
    settings = json.loads(fill(open(os.path.join(o.template, "settings.json.tmpl")).read()))
    deny = settings["permissions"]["deny"]
    i = deny.index("@OTHER_WALLS@")
    others = [f"Read(/{os.path.join(walls, k)}/**)" for k in KINDS if k != o.kind]
    kind_dir = os.path.join(walls, o.kind)
    others += [f"Read(/{os.path.join(kind_dir, r)}/**)" for r in sorted(os.listdir(kind_dir)) if r != o.run]
    deny[i:i + 1] = others
    write_ro(os.path.join(cl, "settings.json"), json.dumps(settings, indent=2) + "\n")
    hook = os.path.join(cl, "wall_hook.py")
    write_ro(hook, open(os.path.join(o.template, "wall_hook.py")).read(), 0o555)
    os.chmod(cl, 0o555)
    os.makedirs(os.path.join(wall, "out"), mode=0o700)
    # 6. the manifest
    manifest = {"act": "ACT-INDEP-WALLS-1", "kind": o.kind, "run": o.run, "commit": commit, "repo": repo, "tree": tree,
                "runs": vals["@RUNS@"], "home": vals["@HOME@"],
                "brief_sha256": sha(os.path.join(wall, "brief.md")), "seed_sha256": seed_sha,
                "seeded_before_content": seeded_at <= os.stat(os.path.join(wall, "input", "selection.json")).st_mtime,
                "settings_sha256": sha(os.path.join(cl, "settings.json")), "hook_sha256": sha(hook),
                "template_sha256": {n: sha(os.path.join(o.template, n)) for n in sorted(os.listdir(o.template))
                                    if not n.startswith(".")},
                "tree_files": files, "selection": {"changed": len(changed), "sample": len(sample)}}
    write_ro(os.path.join(wall, "WALL.json"), json.dumps(manifest, indent=1) + "\n")
    os.chmod(wall, 0o555)  # read-only to every process; only out/ is writable
    print(json.dumps({"wall": o.kind + "/" + o.run, "tree_files": files, "changed": len(changed),
                      "sample": len(sample), "seed_sha256": seed_sha[:12],
                      "settings_sha256": manifest["settings_sha256"][:12]}))


if __name__ == "__main__":
    main()
