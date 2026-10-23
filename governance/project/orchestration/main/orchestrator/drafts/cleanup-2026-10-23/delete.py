"""The approved cleanup (run only on the owner's approval, DEC-899 item 10): for each list named, re-check every path
just before removing it. A path is removed only if it still exists, is a folder, is still idle (no process has its
cwd or an open file there), lies under /tmp, and its list's sha256 matches the approved one. Prints what it removed
and the disk's figures before and after. Usage: delete.py <list file>=<sha256 prefix> ..."""
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path


def held():
    out = set()
    for pid in os.listdir("/proc"):
        if pid.isdigit():
            try:
                out.add(os.path.realpath(f"/proc/{pid}/cwd"))
                out.update(os.path.realpath(f"/proc/{pid}/fd/{fd}") for fd in os.listdir(f"/proc/{pid}/fd"))
            except OSError:
                pass
    return out


def disk():
    return subprocess.run(["df", "--output=used,iused", "-B1G", "/"], capture_output=True, text=True).stdout.split("\n")[1].split()


before = disk()
for arg in sys.argv[1:]:
    name, _, approved = arg.partition("=")
    text = Path(name).read_text()
    if not hashlib.sha256(text.encode()).hexdigest().startswith(approved):
        sys.exit(f"{name}: its sha256 is not the approved one; nothing removed from it")
    busy, removed, skipped = held(), 0, 0
    for line in text.splitlines():
        p = Path(line)
        if (not line.startswith("/tmp/") or not p.is_dir() or p.is_symlink()
                or any(h == line or h.startswith(line + "/") for h in busy)):
            skipped += 1
            continue
        shutil.rmtree(p, ignore_errors=True)
        removed += 1
    print(f"{Path(name).name}: removed {removed}, skipped {skipped} (gone, not a folder, outside /tmp, or in use)")
after = disk()
print(f"disk used: {before[0]} GiB -> {after[0]} GiB; inodes used: {before[1]} -> {after[1]}")
