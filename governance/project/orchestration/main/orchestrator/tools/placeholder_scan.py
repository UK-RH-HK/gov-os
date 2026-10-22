"""Refuse placeholders in what is about to reach the owner or a commit (owner, standing, DEC-893).

    python3 placeholder_scan.py                 # added lines of uncommitted changes, untracked files, drafts/*.patch
    python3 placeholder_scan.py --commit <sha>  # the added lines of one commit (a check of what already went in)
    python3 placeholder_scan.py <file> ...      # named files (a package or entry before it is sent)

Placeholders: an unfilled time or date (`00:2x`, `16:xx`, `2026-10-xx`), `TBD`, `TODO`, `XXX`, a whole-word `xx`,
`???`; and, in path-map lines and patches only, an angle-bracket slot (`<n>`, `<time>`) other than the few template
words commands use (`<path>`, `<subject>`). Prints each hit (file, line, the match); exits 1 if any.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
DRAFTS = ROOT / ".gov-runtime/scratch/orchestrator/drafts"
GENERAL = re.compile(r"\b\d{1,2}:(?:\dx|xx)\b|\b20\d\d-\d\d-(?:xx|\dx)\b|\bTBD\b|\bTODO\b|\bXXX\b|\bxx\b|\?\?\?", re.I)
ANGLE = re.compile(r"<(?!path>|subject>)[A-Za-z][^<>\n]{0,30}>")


def angle_scope(name: str) -> bool:
    return name.endswith(".patch") or name.endswith("path-map.yaml")


def scan_lines(name: str, numbered):
    hits = []
    for no, line in numbered:
        for m in GENERAL.finditer(line):
            hits.append((name, no, m.group(0)))
        if angle_scope(name):
            for m in ANGLE.finditer(line):
                hits.append((name, no, m.group(0)))
    return hits


def added_lines(diff: str):
    """(file, new line number, text) of each added line of a unified diff."""
    name, no = None, 0
    for line in diff.splitlines():
        if line.startswith("+++ "):
            name = line[6:] if line.startswith("+++ b/") else line[4:]
        elif line.startswith("@@"):
            no = int(re.search(r"\+(\d+)", line).group(1)) - 1
        elif line.startswith("+") and not line.startswith("+++"):
            no += 1
            yield name, no, line[1:]
        elif not line.startswith("-"):
            no += 1


def main(argv):
    hits = []
    if argv[:1] == ["--commit"]:
        diff = subprocess.run(["git", "-C", str(ROOT), "show", "--format=", "-U0", argv[1]], capture_output=True, text=True).stdout
        for name, no, text in added_lines(diff):
            hits += scan_lines(name, [(no, text)])
    elif argv:
        for f in argv:
            p = Path(f)
            hits += scan_lines(str(p), enumerate(p.read_text(errors="replace").splitlines(), 1))
    else:
        diff = subprocess.run(["git", "-C", str(ROOT), "diff", "HEAD", "-U0"], capture_output=True, text=True).stdout
        for name, no, text in added_lines(diff):
            hits += scan_lines(name, [(no, text)])
        untracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--others", "--exclude-standard"],
                                   capture_output=True, text=True).stdout.split()
        for rel in untracked:
            p = ROOT / rel
            if p.is_file() and p.stat().st_size < 2_000_000:
                hits += scan_lines(rel, enumerate(p.read_text(errors="replace").splitlines(), 1))
        for p in sorted(DRAFTS.glob("*.patch")):
            added = [(no, text) for _, no, text in added_lines(p.read_text(errors="replace"))]
            hits += scan_lines(str(p.relative_to(ROOT)), added)
    for name, no, match in hits:
        print(f"placeholder: {name}:{no}: {match!r}")
    print(f"placeholder scan: {len(hits)} hit(s)")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
