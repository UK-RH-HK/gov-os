"""The sweep (owner, standing, DEC-902): remove throwaway areas under /tmp and run folders, only under the owner's
conditions, and list what was removed and what was skipped, and why.

    python3 sweep.py [--apply] [--only pytest-runs,code-graph,...]

Without --apply it removes nothing and prints what it would do. With --apply it first checks the moment is quiet
(no `claude -p` session, no CLOSE-RUNNING or NIGHTLY-RUNNING lock, no tooltrials.sh) and stops if it is not.

A folder is removed only if all of these hold:
  - it lies in one of the categories below, under /tmp;
  - nothing inside it was modified in the last 24 hours (the newest mtime of the folder and everything in it);
  - no running process holds it open: no cwd, open file or mapping inside it, by /proc and by lsof;
  - it is not the live session's own folder (CLAUDE_SESSION_TMP or this orchestrator session's folder), nor the live
    code-graph daemon's folder (any folder a running codebase-memory process names, holds, or runs in).
Evidence folders (/tmp/gov-os-assessment-*, /tmp/gov-os-tooltrial, /tmp/w216probe.*) are never in any category.
Prints the disk's figures before and after.
"""
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ORCH = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
OWN = {"/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/ced0eb43-d826-42fa-8eab-3ba5655f1a1f"}
if os.environ.get("CLAUDE_SESSION_TMP"):
    OWN.add(os.path.realpath(os.environ["CLAUDE_SESSION_TMP"]))
DAY = 24 * 3600


def categories():
    pt = Path("/tmp/pytest-of-usain")
    runs = sorted((p for p in pt.iterdir() if p.name.startswith("pytest-") and p.name[7:].isdigit()),
                  key=lambda p: int(p.name[7:])) if pt.is_dir() else []
    cl = Path("/tmp/claude-1000")
    return {
        "pytest-garbage": [p for p in pt.iterdir() if p.name.startswith("garbage-")] if pt.is_dir() else [],
        "pytest-runs": runs[:-3],
        "claude-sessions": [s for slug in cl.iterdir() if slug.is_dir() for s in slug.iterdir() if s.is_dir()] if cl.is_dir() else [],
        "launcher-temp": [p for p in Path("/tmp").iterdir() if p.name.startswith("gov-launch-")],
        "code-graph": [p for p in Path("/tmp/gov-cbm-1000").iterdir() if p.is_dir()] if Path("/tmp/gov-cbm-1000").is_dir() else [],
        "testcache-and-check": [p for p in Path("/tmp").iterdir() if p.name.startswith(("gov-testcache-", "gov-check-"))],
    }


def held_paths():
    """Every path a running process holds: its cwd, its root, its open files and its mapped files (/proc), plus
    what lsof lists for the swept roots."""
    held, daemons = set(), set()
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        base = f"/proc/{pid}"
        try:
            cmd = open(f"{base}/cmdline", "rb").read().replace(b"\0", b" ").decode("utf-8", "replace")
            for link in ("cwd", "root"):
                held.add(os.path.realpath(f"{base}/{link}"))
            for fd in os.listdir(f"{base}/fd"):
                held.add(os.path.realpath(f"{base}/fd/{fd}"))
            for line in open(f"{base}/maps"):
                parts = line.split()
                if len(parts) >= 6 and parts[5].startswith("/"):
                    held.add(parts[5])
        except OSError:
            continue
        if "codebase-memory" in cmd or "/gov-cbm-" in cmd:
            daemons.update(w for w in cmd.split() if w.startswith("/tmp/gov-cbm-"))
    # The code-graph tool keeps one folder per project root (gov.codeintel.daemon_dir: the first 16 hex digits of
    # the sha256 of the resolved root). Every live root's folder is the live daemon's: the main tree, every git
    # worktree (the record's and every ticket's), and every run clone under ~/gov-os-runs.
    import hashlib
    roots = [line.split()[0] for line in subprocess.run(
        ["git", "-C", "/home/usain/Dynamic-Agentic-Engineering-OS", "worktree", "list"],
        capture_output=True, text=True).stdout.splitlines() if line.strip()]
    runs = Path.home() / "gov-os-runs"
    if runs.is_dir():
        roots += [str(c) for t in runs.iterdir() if t.is_dir() for c in [t, *t.iterdir()] if c.is_dir()]
    for r in roots:
        daemons.add(f"/tmp/gov-cbm-{os.getuid()}/" + hashlib.sha256(os.fsencode(Path(r).resolve())).hexdigest()[:16])
    for root in ("/tmp/pytest-of-usain", "/tmp/claude-1000", "/tmp/gov-cbm-1000"):
        if os.path.isdir(root):
            done = subprocess.run(["lsof", "-w", "-Fn", "+D", root], capture_output=True, text=True, timeout=600)
            held.update(line[1:] for line in done.stdout.splitlines() if line.startswith("n/"))
    return held, daemons


def newest(path: Path) -> float:
    latest = path.lstat().st_mtime
    for dirpath, dirnames, filenames in os.walk(path, onerror=lambda e: None):
        for name in dirnames + filenames:
            try:
                latest = max(latest, os.lstat(os.path.join(dirpath, name)).st_mtime)
            except OSError:
                pass
    return latest


def quiet() -> str | None:
    if (ORCH / "CLOSE-RUNNING").exists():
        return "a close is running (CLOSE-RUNNING)"
    if (ORCH / "NIGHTLY-RUNNING").exists():
        return "the nightly run is running (NIGHTLY-RUNNING)"
    procs = subprocess.run(["pgrep", "-af", "claude -p|tooltrials.sh"], capture_output=True, text=True).stdout
    live = [line for line in procs.splitlines() if "pgrep" not in line]
    return f"{len(live)} lead, worker, auditor or trial process(es) running" if live else None


def disk():
    out = subprocess.run(["df", "--output=used,iused,iavail", "-B1G", "/"], capture_output=True, text=True).stdout
    return out.split("\n")[1].split()


def main():
    apply = "--apply" in sys.argv
    only = None
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    if apply:
        why = quiet()
        if why:
            sys.exit(f"sweep: not a quiet moment ({why}); nothing removed")
    held, daemons = held_paths()
    now = time.time()
    before = disk()
    report = []
    for cat, paths in categories().items():
        if only and cat not in only:
            continue
        removed, skipped = 0, {}
        for p in sorted(paths):
            sp = str(p)
            reason = None
            if not sp.startswith("/tmp/") or p.is_symlink() or not p.is_dir():
                reason = "not a folder under /tmp"
            elif sp in OWN or any(sp == o or o.startswith(sp + "/") for o in OWN):
                reason = "the live session's own folder"
            elif any(d == sp or d.startswith(sp + "/") or sp.startswith(d + "/") for d in daemons):
                reason = "the live code-graph daemon's folder"
            elif any(h == sp or h.startswith(sp + "/") for h in held):
                reason = "held open by a running process"
            elif now - newest(p) < DAY:
                reason = "modified in the last 24 hours"
            if reason:
                skipped.setdefault(reason, []).append(sp)
                continue
            if apply:
                shutil.rmtree(p, ignore_errors=True)
            removed += 1
        report.append((cat, removed, skipped))
    after = disk() if apply else before
    verb = "removed" if apply else "would remove"
    for cat, removed, skipped in report:
        print(f"{cat}: {verb} {removed}; skipped {sum(len(v) for v in skipped.values())}")
        for reason, items in skipped.items():
            print(f"   skipped, {reason}: {len(items)}" + (f" ({', '.join(items[:3])}{' ...' if len(items) > 3 else ''})"))
    print(f"disk used {before[0]} GiB -> {after[0]} GiB; inodes used {before[1]} -> {after[1]}, free {after[2]}")


if __name__ == "__main__":
    main()
