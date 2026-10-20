"""The worker tripwire (DEC-789, owner, 2026-10-18). Reads only; prints JSON.

  python3 tripwire.py snapshot            > <your scratch>/tripwire-before-<n>.json
  python3 tripwire.py compare <before.json>   (prints what changed; exit 0 = nothing, 1 = a change)

For the main tree and every worktree under ~/gov-os-worktrees: HEAD, `git status --porcelain`, and a
sha256 of each folder of tests/acceptance/ (paths and contents). Other leads run beside you, so a change
in another tree may be theirs: report every change by tree and path, and the orchestrator attributes it."""
import hashlib
import json
import os
import subprocess
import sys

MAIN = "/home/usain/Dynamic-Agentic-Engineering-OS"
WTS = "/home/usain/gov-os-worktrees"
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def git(tree, *args):
    r = subprocess.run(["git", "-C", tree, *args], capture_output=True, text=True, env=ENV)
    return r.stdout if r.returncode == 0 else f"<git failed: {r.stderr.strip()[:120]}>"


def folder_hash(path):
    h = hashlib.sha256()
    for base, dirs, files in os.walk(path):
        dirs[:] = sorted(d for d in dirs if d not in ("__pycache__", ".pytest_cache"))
        for name in sorted(files):
            if name.endswith(".pyc"):
                continue
            p = os.path.join(base, name)
            h.update(os.path.relpath(p, path).encode() + b"\0")
            try:
                with open(p, "rb") as f:
                    h.update(f.read())
            except OSError as e:
                h.update(f"<unreadable {e.errno}>".encode())
    return h.hexdigest()


def snapshot():
    trees = [MAIN] + sorted(os.path.join(WTS, d) for d in os.listdir(WTS)
                            if os.path.exists(os.path.join(WTS, d, ".git")))
    out = {}
    for t in trees:
        acc = os.path.join(t, "tests", "acceptance")
        out[t] = {
            "head": git(t, "rev-parse", "HEAD").strip(),
            "status": sorted(git(t, "status", "--porcelain", "--untracked-files=all").splitlines()),
            "acceptance": {d: folder_hash(os.path.join(acc, d)) for d in sorted(os.listdir(acc))
                           if os.path.isdir(os.path.join(acc, d)) and d != "__pycache__"} if os.path.isdir(acc) else {},
        }
    return out


def compare(before, after):
    changes = []
    for t in sorted(set(before) | set(after)):
        b, a = before.get(t), after.get(t)
        if b is None or a is None:
            changes.append({"tree": t, "change": "tree appeared" if b is None else "tree disappeared"})
            continue
        if b["head"] != a["head"]:
            changes.append({"tree": t, "change": "head", "before": b["head"][:12], "after": a["head"][:12]})
        sb, sa = set(b["status"]), set(a["status"])
        for line in sorted(sa - sb):
            changes.append({"tree": t, "change": "status line added", "line": line})
        for line in sorted(sb - sa):
            changes.append({"tree": t, "change": "status line gone", "line": line})
        for d in sorted(set(b["acceptance"]) | set(a["acceptance"])):
            if b["acceptance"].get(d) != a["acceptance"].get(d):
                changes.append({"tree": t, "change": "acceptance folder", "folder": d})
    return changes


if __name__ == "__main__":
    if sys.argv[1:2] == ["snapshot"]:
        json.dump(snapshot(), sys.stdout)
    elif sys.argv[1:2] == ["compare"] and len(sys.argv) == 3:
        changes = compare(json.load(open(sys.argv[2])), snapshot())
        json.dump({"changes": changes}, sys.stdout, indent=1)
        sys.exit(1 if changes else 0)
    else:
        sys.exit(__doc__)
