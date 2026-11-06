#!/usr/bin/env python3
"""Count files under a folder that hold any hidden question's text or gold answer (counts only, nothing printed).
    scan_copies.py --sets-root <root> --set <name> --part hidden <folder>
    scan_copies.py <hidden dir> <folder>      (the old form)
The first form builds the hidden folder here (sets_form.py; DEC-1084, ACT-GUARD-SETS-1), never named on the line."""
import os
import sys
from pathlib import Path
import yaml
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))  # sets_form.py beside this file (also under -I)
from sets_form import sets_argv  # noqa: E402
argv = sets_argv(sys.argv)
hidden, folder = Path(argv[1]), Path(argv[2])
needles = []
for f in sorted(hidden.glob("*.yaml")):
    d = yaml.safe_load(f.read_text()) or {}
    for k in ("question", "gold_answer"):
        v = " ".join(str(d.get(k) or "").split())
        if len(v) >= 24:
            needles.append(v[:60])
hits = 0
files = 0
for p in folder.rglob("*"):
    if p.is_file() and p.stat().st_size < 50_000_000:
        files += 1
        try:
            t = " ".join(p.read_text(errors="ignore").split())
        except OSError:
            continue
        if any(n in t for n in needles):
            hits += 1
print(f"needles: {len(needles)}; files scanned: {files}; files holding hidden text: {hits}")
