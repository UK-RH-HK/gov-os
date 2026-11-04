#!/usr/bin/env python3
"""Re-pin the memory measure's line-cited gold sources at the measured head, by exact block move (D-4b, P-W2-61h-2 (a)).

Version 2, after the W2-61h review (R2 to R5): each re-pinned source records the commit it was re-pinned at, so a
second run reads its block from there and reports it unchanged; alternatives are walked; writes are mapped by every
`lines:` in document order and refused when the layout cannot be mapped; YAML errors name the file only; the folder
is backed up (mode 700) before any write, and every written file is re-read and checked, the backup restored on a
mismatch.

For each source cited by `lines: [a, b]` (a heading found at the root governs instead, as in measure.py, so it is left):
the block is the file's lines a..b at the source's own `commit`, else the question's `commit`; at the measured root it
is found again, unchanged. Found at the same lines: left. Found exactly once elsewhere: re-pinned (with --write) to
its new lines, and the source gains `commit: <the root's HEAD>`. Otherwise UNRESOLVED, named by question file name and
source entry number only. Prints counts and file names, never a question, an answer, a path or a line of text.
    repin_gold.py <questions dir> <measured root> [--write]
"""
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml

LINES = re.compile(r"^(?P<lead>[ \t]*(?:- )?)lines:[ \t]*\[[ \t]*\d+[ \t]*,[ \t]*\d+[ \t]*\][ \t]*$", re.M)
OWN_COMMIT = re.compile(r"^[ \t]+commit:[ \t]*[0-9a-f]{7,40}[ \t]*$")


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)


def block_at(root, commit, path, a, b):
    out = git(root, "show", f"{commit}:{path}")
    if out.returncode:
        return None
    lines = out.stdout.splitlines()
    return lines[a - 1:b] if 0 < a <= b <= len(lines) else None


def find(hay, needle):
    n = len(needle)
    return [i + 1 for i in range(len(hay) - n + 1) if hay[i:i + n] == needle]


def line_cited(doc):
    """Every source map that carries `lines`, in document order, with its entry number (alternatives as k.j)."""
    out = []
    for k, s in enumerate(doc.get("sources") or [], 1):
        alts = s if isinstance(s, list) else [s]
        for j, m in enumerate(alts, 1):
            if isinstance(m, dict) and "lines" in m:
                out.append((f"{k}" if not isinstance(s, list) else f"{k}.{j}", m))
    return out


def judge(f, root):
    """(moves, counts, unresolved) for one question file; moves are (index in line_cited order, new a, new b)."""
    doc = yaml.safe_load(f.read_text()) or {}
    base = str(doc.get("commit") or "")
    counts = {"line-cited": 0, "unchanged": 0, "re-pinned": 0, "unresolved": 0, "heading-anchored": 0}
    moves, unresolved = [], []
    for i, (entry, s) in enumerate(line_cited(doc)):
        counts["line-cited"] += 1
        span = s.get("lines")
        if not (isinstance(span, list) and len(span) == 2):
            counts["unresolved"] += 1
            unresolved.append(f"{f.name} entry {entry} (malformed lines)")
            continue
        a, b = int(span[0]), int(span[1])
        target = root / str(s.get("path", ""))
        now = target.read_text(errors="ignore").splitlines() if target.is_file() else []
        heading = s.get("heading")
        if heading is not None and any(l.rstrip() == str(heading).rstrip() for l in now):
            counts["heading-anchored"] += 1
            continue
        old = block_at(root, str(s.get("commit") or base), s.get("path", ""), a, b)
        if old is not None and now[a - 1:b] == old:
            counts["unchanged"] += 1
            continue
        hits = find(now, old) if old else []
        if len(hits) == 1:
            counts["re-pinned"] += 1
            moves.append((i, hits[0], hits[0] + (b - a)))
        else:
            counts["unresolved"] += 1
            unresolved.append(f"{f.name} entry {entry}")
    return doc, moves, counts, unresolved


def rewrite(text, doc, moves, head):
    """The file's text with each moved `lines:` replaced and its own `commit:` set; None if the layout is unmappable."""
    matches = list(LINES.finditer(text))
    if len(matches) != len(line_cited(doc)):
        return None
    lines = text.splitlines(keepends=True)
    starts = [0]
    for l in lines:
        starts.append(starts[-1] + len(l))
    for i, na, nb in sorted(moves, reverse=True):
        m = matches[i]
        row = next(r for r in range(len(lines)) if starts[r] <= m.start() < starts[r + 1])
        col = len(m.group("lead"))
        lines[row] = f"{m.group('lead')}lines: [{na}, {nb}]\n"
        own = f"{' ' * col}commit: {head}\n"
        if row + 1 < len(lines) and OWN_COMMIT.match(lines[row + 1].rstrip("\n")) and \
                len(lines[row + 1]) - len(lines[row + 1].lstrip()) == col:
            lines[row + 1] = own
        else:
            lines.insert(row + 1, own)
    return "".join(lines)


def main(argv):
    qdir, root, write = Path(argv[1]), Path(argv[2]), "--write" in argv
    head = git(root, "rev-parse", "--short=12", "HEAD").stdout.strip()
    if write and (not head or git(root, "status", "--porcelain", "--untracked-files=no").stdout.strip()):
        print("REFUSED: the measured root is not a clean git tree at a commit")
        return 2
    total = {"line-cited": 0, "unchanged": 0, "re-pinned": 0, "unresolved": 0, "heading-anchored": 0}
    unresolved, plans = [], []
    for f in sorted(qdir.glob("*.yaml")):
        try:
            doc, moves, counts, unres = judge(f, root)
        except yaml.YAMLError:
            print(f"  UNREADABLE {f.name}")
            total["unresolved"] += 1
            continue
        for k, v in counts.items():
            total[k] += v
        unresolved += unres
        if moves:
            plans.append((f, doc, moves))
    if write and plans:
        backup = qdir.parent / f"backup-{qdir.name}-{time.strftime('%Y%m%d-%H%M%S')}"
        shutil.copytree(qdir, backup)
        backup.chmod(0o700)
        for f, doc, moves in plans:
            new = rewrite(f.read_text(), doc, moves, head)
            if new is None:
                print(f"  REFUSED {f.name}: its layout cannot be mapped; left as it was")
                total["unresolved"] += 1
                continue
            f.write_text(new)
            again = line_cited(yaml.safe_load(f.read_text()) or {})
            ok = all(again[i][1].get("lines") == [na, nb] and str(again[i][1].get("commit")) == head
                     for i, na, nb in moves)
            if not ok:
                shutil.copy2(backup / f.name, f)
                print(f"  RESTORED {f.name}: the written file did not check; the backup is back")
                total["unresolved"] += 1
                continue
            # DEC-1069 (6): a reason line for every automatic re-anchor (ids, entries and lines only; no question,
            # answer or source text), beside the folder, in the sets root's own protection
            log = qdir.parent / f"REANCHOR-LOG-{qdir.name}.md"
            old = line_cited(doc)
            with log.open("a") as out:
                for i, na, nb in moves:
                    entry, s = old[i]
                    out.write(f"- {time.strftime('%Y-%m-%d %H:%M')} {f.stem} entry {entry}: lines {s.get('lines')} -> "
                              f"[{na}, {nb}] at {head}: the cited block moved unchanged (automatic re-anchor by "
                              f"repin_gold.py before a measure; backup {backup.name})\n")
            log.chmod(0o600)
        print(f"  backup: {backup.name}")
    print("; ".join(f"{k}: {v}" for k, v in total.items()) + ("; written at " + head if write else "; dry run"))
    for u in unresolved:
        print(f"  UNRESOLVED {u}")
    return 1 if total["unresolved"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
