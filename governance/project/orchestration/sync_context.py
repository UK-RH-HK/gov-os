"""Copy the orchestration context from scratch into the record branch, and commit it there (Policy 1, DEC-819, DEC-887).

Run from the main tree's root, at every orchestrator checkpoint and before a worktree is removed:

    python3 governance/project/orchestration/sync_context.py [--check] [--main] [--commit "<subject>"]

Since DEC-887 (owner, 2026-10-21, P-REC-1 (a)) the raw record lives on its own branch, ``record/w2``, checked out
once as the worktree ``/home/usain/gov-os-worktrees/W2-00-record/``, under the same paths it had in the main tree
(``governance/project/orchestration/…``). The branch never merges into ``w2/integrate`` or ``main``; the owner's daily
push carries it. So the orchestrator's working-memory commits no longer move ``w2/integrate``'s head.

It copies, file by file and only when the content differs, into the record worktree:

- the main tree's ``.gov-runtime/scratch/`` (the orchestrator's checkpoint, archive, briefs, logs, packages, scripts,
  and the automatic checkpoint series) to ``main/``;
- each ticket worktree's ``.gov-runtime/scratch/`` (the lead's records, its checkpoints) to ``worktrees/<name>/``.

``--main`` also refreshes the searchable copy the main tree keeps, ``main/orchestrator/CHECKPOINT.md`` (with the
README, ``packages/`` and ``sessions/``, which are written there directly), for a commit on ``w2/integrate`` that moves
its head anyway (a decision record). ``--commit "<subject>"`` commits the record worktree's changes on ``record/w2``,
after gitleaks over the staged set, with ``Task: DAEO-sdxk`` and ``Role: orchestrator``.

It never deletes: a removed worktree's copy stays. It never copies what Policy 1 keeps out: derived context packets
and stores, wheels, archives, compiled files, model files, binary files, files over 2 MB, folders that ignore
themselves (a ``.gitignore`` of their own), a suite's raw output under a log folder, and anything git ignores. A main
tree copy that no namespace of the path map holds is left out and named. Then it runs gitleaks over the record, with
the repository's ``.gitleaks.toml``, redacted; a file gitleaks flags is removed again and named, never committed.
``--check`` copies nothing and only lists what it would copy.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path.cwd()
RECORD = Path("/home/usain/gov-os-worktrees/W2-00-record")
DEST = RECORD / "governance/project/orchestration"
MAIN_DEST = ROOT / "governance/project/orchestration"
MAIN_COPIES = ("main/orchestrator/CHECKPOINT.md",)  # the searchable copy the main tree keeps (DEC-887 item 1)
SKIP_DIRS = {"context", "__pycache__", ".git", "xdist-wheels", "vendor-src", "assessment", ".secrets"}
SKIP_SUFFIXES = {".tgz", ".gz", ".zip", ".whl", ".pyc", ".sqlite", ".sqlite3", ".db", ".npy", ".npz", ".bin",
                 ".gguf", ".safetensors", ".pt", ".onnx", ".lance", ".parquet", ".env"}
MAX_BYTES = 2 * 1024 * 1024
SUITE_LOG = re.compile(r"W[12]-\d{2}[a-z]?([._-][^/]*)?\.(txt|log|out|err)")
TRAILERS = ["--trailer", "Task: DAEO-sdxk", "--trailer", "Role: orchestrator",
            "--trailer", "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"]


def sources():
    yield ROOT / ".gov-runtime/scratch", DEST / "main"
    out = subprocess.run(["git", "worktree", "list", "--porcelain"], capture_output=True, text=True, check=True).stdout
    for line in out.splitlines():
        if line.startswith("worktree "):
            tree = Path(line[len("worktree "):])
            if tree.resolve() not in (ROOT.resolve(), RECORD.resolve()):
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
            # A folder with its own .gitignore is a tool's store that ignores itself (W2-48's test-cache stores).
            if ".gitignore" in filenames:
                dirnames[:] = []
                continue
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for name in sorted(filenames):
                path = Path(dirpath) / name
                # A suite's raw output under a log folder (W1-27.txt and the like) can name a test's own fixture
                # paths (W1-27's moved-path case, DEC-882); the leads' JSON results carry the suites' outcomes.
                if SUITE_LOG.fullmatch(name) and "log" in path.relative_to(src).parts:
                    continue
                if wanted(path):
                    yield path, dst / path.relative_to(src)


def ignored(paths, root: Path):
    if not paths:
        return set()
    done = subprocess.run(["git", "-C", str(root), "check-ignore", "--stdin"],
                          input="\n".join(map(str, paths)), capture_output=True, text=True)
    return {Path(p) for p in done.stdout.splitlines()}


def namespaced():
    """Whether a main-tree path lies in a namespace of the path map: a copy in none fails W1-08's case, and so every
    close (W2-02's refused close of 2026-10-21)."""
    import yaml
    namespaces = yaml.safe_load((ROOT / "governance/project/path-map.yaml").read_text())["namespaces"]
    patterns = [p for entry in namespaces.values() for p in entry.get("paths", [])]

    def matches(rel: str, pattern: str) -> bool:  # `*` inside one folder, `**` across folders (the path map's language)
        parts = [re.escape(part).replace(r"\*", "[^/]*") for part in pattern.split("**")]
        return re.fullmatch(".*".join(parts), rel) is not None

    return lambda rel: any(matches(rel, p) for p in patterns)


def scan(folder: Path) -> list[Path]:
    """Run gitleaks over ``folder``; remove and name every file it flags. Raises when gitleaks cannot scan."""
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "report.json"
        done = subprocess.run(["gitleaks", "dir", str(folder), "--config", str(ROOT / ".gitleaks.toml"), "--redact",
                               "--no-banner", "--log-level", "error", "--exit-code", "3", "--report-format", "json",
                               "--report-path", str(report)], capture_output=True)
        if done.returncode not in (0, 3):
            raise RuntimeError(f"gitleaks could not scan {folder}: {done.returncode} {done.stderr.decode()[-500:]}")
        findings = json.loads(report.read_text() or "[]") if report.exists() else []
    flagged = sorted({Path(f["File"]).resolve() for f in findings})
    for path in flagged:
        path.unlink(missing_ok=True)
        print("   flagged by gitleaks and removed (never committed):", path, file=sys.stderr)
    return flagged


def commit(subject: str) -> int:
    """Commit the record worktree's changes on record/w2, after gitleaks over the staged set."""
    git = ["git", "-C", str(RECORD)]
    subprocess.run(git + ["add", "-A", "--", "governance/project/orchestration"], check=True)
    if subprocess.run(git + ["diff", "--cached", "--quiet"]).returncode == 0:
        print("record/w2: nothing to commit")
        return 0
    leaks = subprocess.run(["gitleaks", "git", "--staged", "--redact", "--no-banner", "--log-level", "error",
                            "--config", str(ROOT / ".gitleaks.toml"), str(RECORD)])
    if leaks.returncode != 0:
        print("record/w2: gitleaks flagged the staged set; nothing committed", file=sys.stderr)
        return 3
    subprocess.run(git + ["commit", "-q", "-m", subject, *TRAILERS], check=True)
    head = subprocess.run(git + ["log", "--oneline", "-1"], capture_output=True, text=True).stdout.strip()
    print("record/w2:", head)
    return 0


def main():
    args = sys.argv[1:]
    check, to_main = "--check" in args, "--main" in args
    subject = args[args.index("--commit") + 1] if "--commit" in args else None
    if not (RECORD / ".git").exists():
        print(f"the record worktree {RECORD} is missing: nothing copied", file=sys.stderr)
        return 2
    pairs = [(s, d) for s, d in plan() if not d.exists() or d.read_bytes() != s.read_bytes()]
    skip = ignored([d.relative_to(RECORD) for _, d in pairs], RECORD)
    pairs = [(s, d) for s, d in pairs if d.relative_to(RECORD) not in skip]
    main_pairs = []
    if to_main:
        in_namespace = namespaced()
        for rel in MAIN_COPIES:
            src, dst = ROOT / ".gov-runtime/scratch" / rel.removeprefix("main/"), MAIN_DEST / rel
            if src.is_file() and (not dst.exists() or dst.read_bytes() != src.read_bytes()):
                if in_namespace(dst.relative_to(ROOT).as_posix()):
                    main_pairs.append((src, dst))
                else:
                    print("left out, in no namespace of the path map:", dst.relative_to(ROOT), file=sys.stderr)
    print(f"record: {len(pairs)} file(s) new or changed; {len(skip)} left out because git ignores them; "
          f"main tree: {len(main_pairs)} searchable copy(ies)")
    if check:
        for _, d in pairs + main_pairs:
            print("  ", d)
        return 0
    for s, d in pairs + main_pairs:
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(s, d)
    flagged = scan(DEST) + (scan(MAIN_DEST / "main") if main_pairs else [])
    print(f"{len(pairs) + len(main_pairs)} copied; {len(flagged)} flagged by gitleaks and removed again")
    return commit(subject) if subject else 0


if __name__ == "__main__":
    sys.exit(main())
