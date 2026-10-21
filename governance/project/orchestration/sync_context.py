"""Copy the orchestration context from scratch into the tree, for the owner's or the orchestrator's commit (Policy 1, DEC-819).

Run from the main tree's root, at every orchestrator checkpoint and before a worktree is removed:

    python3 governance/project/orchestration/sync_context.py [--check]

It copies, file by file and only when the content differs:

- the main tree's ``.gov-runtime/scratch/`` (the orchestrator's checkpoint, archive, briefs, logs, packages, scripts,
  and the automatic checkpoint series) to ``main/``;
- each worktree's ``.gov-runtime/scratch/`` (the lead's records, its checkpoints) to ``worktrees/<worktree name>/``.

It never deletes: a removed worktree's copy stays. It never copies what Policy 1 keeps out: derived context packets
and stores, wheels, archives, compiled files, model files, binary files, files over 2 MB, and anything git ignores.
Then it runs gitleaks over every file it would add, with the repository's ``.gitleaks.toml``, redacted; a file gitleaks
flags is removed again and named, never committed. ``--check`` copies nothing and only lists what it would copy.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path.cwd()
DEST = ROOT / "governance/project/orchestration"
SKIP_DIRS = {"context", "__pycache__", ".git", "xdist-wheels", "vendor-src", "assessment", ".secrets"}
SKIP_SUFFIXES = {".tgz", ".gz", ".zip", ".whl", ".pyc", ".sqlite", ".sqlite3", ".db", ".npy", ".npz", ".bin",
                 ".gguf", ".safetensors", ".pt", ".onnx", ".lance", ".parquet", ".env"}
MAX_BYTES = 2 * 1024 * 1024


def sources():
    yield ROOT / ".gov-runtime/scratch", DEST / "main"
    out = subprocess.run(["git", "worktree", "list", "--porcelain"], capture_output=True, text=True, check=True).stdout
    for line in out.splitlines():
        if line.startswith("worktree "):
            tree = Path(line[len("worktree "):])
            if tree.resolve() != ROOT.resolve():
                yield tree / ".gov-runtime/scratch", DEST / "worktrees" / tree.name


def wanted(path: Path) -> bool:
    if path.suffix.lower() in SKIP_SUFFIXES or path.is_symlink():
        return False
    size = path.stat().st_size
    if size > MAX_BYTES:
        return False
    with open(path, "rb") as f:
        return b"\0" not in f.read(8192)


def plan():
    for src, dst in sources():
        if not src.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(src):
            # A folder with its own .gitignore is a tool's store that ignores itself (W2-48's test-cache stores):
            # copied, it is ignored only by that uncommitted file, which refuses a close (TREE_NOT_COMMITTED).
            if ".gitignore" in filenames:
                dirnames[:] = []
                continue
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for name in sorted(filenames):
                path = Path(dirpath) / name
                if wanted(path):
                    yield path, dst / path.relative_to(src)


def ignored(paths):
    if not paths:
        return set()
    done = subprocess.run(["git", "check-ignore", "--stdin"], input="\n".join(map(str, paths)), capture_output=True,
                          text=True)
    return {Path(p) for p in done.stdout.splitlines()}


def main():
    check = "--check" in sys.argv[1:]
    pairs = [(s, d) for s, d in plan() if not d.exists() or d.read_bytes() != s.read_bytes()]
    skip = ignored([d.relative_to(ROOT) for _, d in pairs])
    pairs = [(s, d) for s, d in pairs if d.relative_to(ROOT) not in skip]
    print(f"{len(pairs)} file(s) new or changed; {len(skip)} left out because git ignores them")
    if check:
        for s, d in pairs:
            print("  ", d.relative_to(ROOT))
        return 0
    for s, d in pairs:
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(s, d)
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "report.json"
        done = subprocess.run(["gitleaks", "dir", str(DEST), "--config", str(ROOT / ".gitleaks.toml"), "--redact",
                               "--no-banner", "--log-level", "error", "--exit-code", "3", "--report-format", "json",
                               "--report-path", str(report)], capture_output=True)
        if done.returncode not in (0, 3):
            print("gitleaks could not scan", done.returncode, done.stderr.decode()[-500:], file=sys.stderr)
            return 2
        findings = json.loads(report.read_text() or "[]") if report.exists() else []
    flagged = sorted({Path(f["File"]).resolve() for f in findings})
    rules = {}
    for f in findings:
        rules.setdefault(Path(f["File"]).resolve(), set()).add(f["RuleID"])
    for path in flagged:
        path.unlink(missing_ok=True)
    print(f"{len(pairs)} copied; {len(flagged)} flagged by gitleaks and removed again (never committed):")
    for path in flagged:
        print("  ", path.relative_to(ROOT.resolve()), sorted(rules[path]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
