#!/usr/bin/env python3
"""The hidden-half rule's check on a report written from hidden questions, before the CTO reads it (DEC-820 (d)).

    python3 -I leak_check.py <questions folder> <report.md>

Reads the questions (question, gold_answer, every source's path and heading) and the report, and prints counts only:
how many report lines share a run of 6 or more words with any question or gold answer, and how many name a gold
path or quote a gold heading. Nothing of a question is printed. 0 and 0 is the pass.
"""
import re
import sys
from pathlib import Path

import yaml

qdir, report = Path(sys.argv[1]), Path(sys.argv[2])
words = lambda t: re.findall(r"[a-z0-9_]+", str(t).lower())
shingles, strings = set(), set()
for f in sorted(qdir.glob("*.yaml")):
    q = yaml.safe_load(f.read_text())
    for text in (q.get("question", ""), q.get("gold_answer", "")):
        w = words(text)
        shingles.update(tuple(w[i:i + 6]) for i in range(len(w) - 5))
    for entry in q.get("sources") or []:
        for alt in entry if isinstance(entry, list) else [entry]:
            for key in ("path", "heading"):
                v = str(alt.get(key, "")).strip().lstrip("#").strip()
                if len(v) >= 8:
                    strings.add(v.lower())
shared = named = 0
for line in report.read_text().splitlines():
    w = words(line)
    if any(tuple(w[i:i + 6]) in shingles for i in range(len(w) - 5)):
        shared += 1
    low = line.lower()
    if any(s in low for s in strings):
        named += 1
print(f"leak check: lines sharing 6+ words with a question or answer: {shared}; lines naming a gold path or heading: {named}")
sys.exit(0 if shared == named == 0 else 1)
