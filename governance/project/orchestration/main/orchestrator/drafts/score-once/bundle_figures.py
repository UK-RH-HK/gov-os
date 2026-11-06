#!/usr/bin/env python3
"""DEC-1084's question, figures only, from kept runs (no GPU): per model and set, hit@5, hit@10 and "in the bundle";
the first call's bundle size in tokens (median, p90) and items; and, where the first call holds fewer than 10 items,
what the first 10 would cost (the next calls' items, by the first call's own tokens-per-character). Counts only; the
kept outputs are read for sizes and counts, never for text that is printed.

    bundle_figures.py <name> <run folder (r80/, r60/)> <kept r80 folder> <kept r60 folder> [...]
"""
import json
import re
import statistics
import sys
from pathlib import Path

APART = {"h24", "m60"}


def lines(measure):
    out, start = [], 1
    for line in open(measure):
        m = re.match(r"(\S+) \((\w+)\): hit@5 (yes|no)(?: \(first gold rank (\d+|-)\))?, in the bundle (yes|no).*?(\d+) calls?",
                     line)
        if m:
            n = int(m[6])
            rank = int(m[4]) if m[4] and m[4] != "-" else None
            out.append((m[1], m[2], m[3] == "yes", rank, m[5] == "yes", start, n))
            start += n
    return out


def call(folder, n):
    r = json.loads((Path(folder) / f"{n:05d}.json").read_text()).get("result") or {}
    ev = r.get("evidence", [])
    used = ((r.get("budget") or {}).get("bundle") or {}).get("used")
    chars = sum(len(str(e.get("text", ""))) for e in ev)
    return ev, used, chars


def pct(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(p * len(v)))] if v else None


args = sys.argv[1:]
while args:
    name, run, k80, k60, args = args[0], Path(args[1]), args[2], args[3], args[4:]
    sets = {"visible": [], "hidden": [], "spent": []}
    sizes, items, extra, need = [], [], [], 0
    for part, kept in (("r80", k80), ("r60", k60)):
        for qid, kind, h5, rank, inb, start, n in lines(run / part / "measure.txt"):
            if qid in APART:
                continue
            ev, used, chars = call(kept, start)
            sets["spent" if part == "r60" else kind].append((h5, rank is not None and rank <= 10, inb,
                                                             rank is not None and rank <= len(ev)))
            sizes.append(used or 0)
            items.append(len(ev))
            if len(ev) < 10:  # the cost of the rest of a top 10, from the next calls' items
                need += 1
                rate = (used / chars) if used and chars else 0.25
                more, got = 0, len(ev)
                for c in range(start + 1, start + n):
                    ev2, _, _ = call(kept, c)
                    for e in ev2:
                        if got >= 10:
                            break
                        more += len(str(e.get("text", ""))) * rate
                        got += 1
                    if got >= 10:
                        break
                extra.append(round(more))
    print(f"== {name}")
    allq = [x for v in sets.values() for x in v]
    for k, v in list(sets.items()) + [("the 138", allq)]:
        print(f"  {k}: hit@5 {sum(x[0] for x in v)}/{len(v)}; hit@10 {sum(x[1] for x in v)}/{len(v)}; "
              f"in the first call's bundle {sum(x[3] for x in v)}/{len(v)}; in the bundle (all calls) "
              f"{sum(x[2] for x in v)}/{len(v)}")
    print(f"  first call's bundle: tokens median {statistics.median(sizes):.0f}, p90 {pct(sizes, 0.9)}, max {max(sizes)}; "
          f"items median {statistics.median(items):.0f}, min {min(items)}, p90 {pct(items, 0.9)}")
    print(f"  first calls with fewer than 10 items: {need} of {len(sizes)}"
          + (f"; the rest of a top 10 would cost tokens median {statistics.median(extra):.0f}, p90 {pct(extra, 0.9)}"
             if extra else ""))
