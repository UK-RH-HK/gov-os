#!/usr/bin/env python3
"""DEC-1071 (1), the structural review's evidence: memory's structure across the whole index, and the gold's
structure per half. Counts only; nothing of a hidden question is printed (DEC-820 (d)).

    cd <m6 clone> && PYTHONPATH=src python3 structural.py <sets root> <out.json>
"""
import ast
import collections
import hashlib
import json
import re
import sqlite3
import statistics
import sys
from pathlib import Path

from gov import records
from gov.guard.reads import evaluation_sets
from gov.retrieval import authority
from gov.retrieval.measure import EVALUATION, _load, _Part

root, sets_root, out = Path("."), Path(sys.argv[1]), Path(sys.argv[2])
db = sqlite3.connect(root / ".gov-runtime" / "store.db")
chunks = list(db.execute("select chunk_id, path, start_line, end_line, parent_id from lexical_chunk"))
embedded = {r[0] for r in db.execute("select chunk_id from semantic_vector")}
parents = {pid: (p, s, e, kind) for pid, p, kind, s, e in db.execute("select parent_id, path, kind, start_line, end_line from lexical_parent")}
lines_of = {}


def text(path, s, e):
    if path not in lines_of:
        try:
            lines_of[path] = (root / path).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            lines_of[path] = []
    return lines_of[path][s - 1:e]


R = {}
# ---- the index: size, embedding, parents, duplicates
emb = [c for c in chunks if c[0] in embedded]
size = {c[0]: sum(len(l) + 1 for l in text(c[1], c[2], c[3])) for c in emb}
sz = sorted(size.values())
R["index"] = {"chunks": len(chunks), "embedded": len(emb), "embedded_files": len({c[1] for c in emb}),
              "chars_p50": sz[len(sz) // 2], "chars_p90": sz[int(len(sz) * .9)],
              "over_2000": sum(x > 2000 for x in sz), "over_10000_truncated": sum(x > 10000 for x in sz)}
by_parent = collections.Counter(c[4] for c in emb)
R["index"]["parents_embedded"] = len(by_parent)
R["index"]["parents_split_in_2plus"] = sum(n > 1 for n in by_parent.values())
R["index"]["chunks_in_split_parents"] = sum(n for n in by_parent.values() if n > 1)
digest = {c[0]: hashlib.sha256("\n".join(text(c[1], c[2], c[3])).strip().encode()).hexdigest() for c in emb}
groups = collections.defaultdict(list)
for c in emb:
    if size[c[0]] > 80:
        groups[digest[c[0]]].append(c[1])
dup = {d: ps for d, ps in groups.items() if len(set(ps)) > 1}
R["index"]["dup_groups_across_files"] = len(dup)
R["index"]["chunks_in_dup_groups"] = sum(len(ps) for ps in dup.values())
fam = collections.Counter()
for ps in dup.values():
    tops = tuple(sorted({"/".join(p.split("/")[:2]) for p in ps}))
    fam[tops] += len(ps)
R["index"]["dup_families_top"] = [[list(k), v] for k, v in fam.most_common(8)]
# ---- code: chunks cut away from their definitions
py = [c for c in emb if c[1].endswith(".py")]
starts_at_def = mid = 0
fn_split = fn_total = 0
defs_by_file = {}
for path in {c[1] for c in py}:
    try:
        tree = ast.parse((root / path).read_text(encoding="utf-8", errors="replace"))
    except (SyntaxError, OSError, ValueError):
        continue
    defs = [(n.lineno, n.end_lineno) for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    defs_by_file[path] = defs
for c in py:
    first = (text(c[1], c[2], c[2]) or [""])[0].lstrip()
    if c[2] == 1 or re.match(r"(def |async def |class |@)", first):
        starts_at_def += 1
    else:
        mid += 1
for path, defs in defs_by_file.items():
    spans = [(c[2], c[3]) for c in py if c[1] == path]
    for a, b in defs:
        if not any(s <= a <= e for s, e in spans):
            continue
        fn_total += 1
        holder = [(s, e) for s, e in spans if s <= a <= e]
        if holder and holder[0][1] < b:
            fn_split += 1
R["code"] = {"py_chunks": len(py), "starting_at_a_def_or_file_start": starts_at_def, "starting_mid_body": mid,
             "defs": fn_total, "defs_running_past_their_chunk": fn_split}
# ---- the graph
known = records.records(root)
edges = records.edges(root)
R["graph"] = {"records": len(known), "edges": dict(collections.Counter(e["type"] for e in edges))}
# ---- the gold, per half (counts only)
entry = evaluation_sets(str(sets_root))["memory-retrieval"]
quoting = _Part("/q", [*entry.get("visible", []), *entry["hidden"], f"{EVALUATION}/**"], "")
sup = records.edges(root, type=authority.SUPERSEDES)
order = authority.order(root, known, sup, authority.register_entries_of(known, sup, root))
chunk_by_path = collections.defaultdict(list)
for c in emb:
    chunk_by_path[c[1]].append(c)
dup_digests = set(dup)


def form(lines):
    first = (lines or [""])[0].strip()
    if len(lines) == 1 and first.startswith("|"):
        return "table row"
    if re.match(r"([-*] |\d+\. )", first):
        return "list item"
    if re.match(r"[\w\"'-]+:\s", first) and not first.startswith("#"):
        return "field"
    if len(lines) <= 2:
        return "one or two lines"
    if first.startswith("#"):
        return "section"
    return "block"


for part in ("visible", "hidden"):
    st = collections.Counter()
    for f in sorted((sets_root / EVALUATION / "memory-retrieval" / part).glob("*.yaml")):
        q = _load(f, part, root, quoting)
        named = set(re.findall(r"\b(?:DEC|CAP|MR|W\d)-[\w.]+", q["question"]))
        st["questions"] += 1
        st["questions naming a record id"] += bool(named)
        for alts in q["sources"]:
            p, s, e = alts[0]
            st["pieces"] += 1
            st["form: " + form(text(p, s, e))] += 1
            st["tier: " + {1: "governing", 0: "middle", -1: "reports"}.get(order.steps(p, s), "other")] += 1
            holders = [c for c in chunk_by_path.get(p, []) if c[2] <= e and s <= c[3]]
            if not holders:
                st["gold in no embedded chunk"] += 1
                continue
            h = holders[0]
            clen, glen = h[3] - h[2] + 1, e - s + 1
            st["gold under a quarter of its chunk"] += glen * 4 < clen
            st["gold spread over 2+ chunks"] += len(holders) > 1
            st["gold chunk in a split parent"] += by_parent[h[4]] > 1
            st["gold chunk without its parent's first line"] += h[2] > parents.get(h[4], (p, h[2], 0, ""))[1]
            st["gold chunk duplicated in another file"] += digest[h[0]] in dup_digests
            st["gold chunk over 2000 chars"] += size[h[0]] > 2000
            if p.endswith(".py"):
                st["code gold"] += 1
                first = (text(p, h[2], h[2]) or [""])[0].lstrip()
                st["code gold chunk not starting at a def"] += not (h[2] == 1 or re.match(r"(def |async def |class |@)", first))
            if named and p == "docs/DECISION_REGISTER.md":
                ent = [l for l in text(p, s, e) if l.startswith("### ")]
                if ent and not any(n in ent[0] for n in named):
                    st["named record, gold in another register entry"] += 1
    R["gold_" + part] = dict(st)
out.write_text(json.dumps(R, indent=1))
print(json.dumps(R, indent=1))
