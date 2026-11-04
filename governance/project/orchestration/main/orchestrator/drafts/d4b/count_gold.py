#!/usr/bin/env python3
"""D-4b step 0 (DEC-1055): where the memory measure's gold sources sit, as COUNTS only.

Prints no question, answer or path of the hidden half: only how many gold sources fall in each bucket, so D-4's cut
and D-7's embedding scope can be checked against them. Usage: count_gold.py <questions dir> <repo root>
With --check <file of paths> it prints only how many listed paths are gold sources (for D-4's deletion list).
"""
import sys
from pathlib import Path

import yaml

BUCKETS = [
    ("tests/", "under tests/ (D-4 may delete; D-7 un-embeds)"),
    ("docs/close/", "docs/close (D-7 un-embeds)"),
    ("docs/checkpoints/", "docs/checkpoints (D-7 un-embeds)"),
    ("docs/probes/", "docs/probes (D-7 un-embeds)"),
    ("governance/project/orchestration/", "the orchestration record (D-7 un-embeds closes, reviews, sessions, nightly)"),
    ("docs/DECISION_REGISTER.md", "the register (M-5 held)"),
    ("src/", "src/ (D-6 may move)"),
    ("docs/assessment/2026-10/B-memory-retrieval.md", "lens B's report (G4: out of both indexes)"),
    ("docs/research/EXP-003/w2-15a/raw/", "W2-15a's raw output (G4/F5: out of both indexes)"),
    ("fixtures/", "fixtures (not embedded; evaluation fixtures out of both)"),
]


def sources(qdir):
    for f in sorted(Path(qdir).glob("*.yaml")):
        doc = yaml.safe_load(f.read_text()) or {}
        for s in doc.get("sources") or []:
            if isinstance(s, dict) and s.get("path"):
                yield s["path"]


def main(argv):
    qdir, root = Path(argv[1]), Path(argv[2])
    paths = list(sources(qdir))
    if "--check" in argv:
        listed = {l.strip() for l in Path(argv[argv.index("--check") + 1]).read_text().splitlines() if l.strip()}
        print(f"gold sources among the listed paths: {sum(p in listed for p in paths)} of {len(paths)}")
        return 0
    print(f"questions: {len(list(qdir.glob('*.yaml')))}; gold sources: {len(paths)}; distinct files: {len(set(paths))}")
    for prefix, label in BUCKETS:
        print(f"  {label}: {sum(p.startswith(prefix) for p in paths)}")
    print(f"  missing at {root}: {sum(not (root / p).exists() for p in paths)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
