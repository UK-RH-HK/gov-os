"""W2-92 S10 (DEC-1072 (1)): the drift count before and after the stated links, by the census's definitions.

Read-only. Run from anywhere, after the clone's rebuild:
    PYTHONPATH=<clone>/src python3 W2-92-proto-drift.py <clone> [<out.json>]
or, with no store (the records and links read from HEAD by the loader's own rule, nothing written):
    PYTHONPATH=<clone>/src python3 W2-92-proto-drift.py <clone> [<out.json>] --from-head

The question: of the decisions current though stated changed (the census's 215 at m6), for how many does a search
that reaches the decision now also reach a decision that changed it? Counted in the graph: a one-hop link from the
decision to the changer (AMENDS or SUPERSEDES, from the changer), and by the retrieval's own rule
(``graph_route.follow`` from the decision and its closure at R0/R1), within the bound.

DEC-1073 (2): the decisions ARCHIVE-SUPERSEDED §B calls spent while the register lists them as current are left out
of the drift and listed apart for a status reconciliation; a decision not ACCEPTED (PROPOSED) is never current, and
the stated-changed ones are counted by status, apart.

The definitions are the census's (``docs/research/D4B-link-census.py``, 3d1c459e): its register statements are read
through ``loader.register_statements``, which gives them one for one (W2-92 S7), and ARCHIVE-SUPERSEDED §A with the
same patterns; a statement is a register label, its free text, the change log or ARCHIVE-SUPERSEDED §A;
current is status ACCEPTED and no SUPERSEDES edge in ``edges`` (the edges table, unchanged by the prototype, so the
set is the same before and after). No model, no network, no GPU; nothing is written but <out.json>.
"""

from __future__ import annotations

import collections
import json
import re
import sqlite3
import sys
from pathlib import Path

import yaml

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
FROM_HEAD = "--from-head" in sys.argv
ROOT = Path(ARGS[0]).resolve()
OUT = Path(ARGS[1]) if len(ARGS) > 1 else None
sys.path.insert(0, str(ROOT / "src"))
from gov.retrieval import graph_route  # noqa: E402
from gov.store import loader  # noqa: E402

DEC = re.compile(r"\bDEC-(\d{3,})\b")
ARCHIVE = "governance/project/orchestration/ARCHIVE-SUPERSEDED.md"

# ---------------------------------------------------------------- the graph: the store's, or HEAD's by the loader
if FROM_HEAD:
    rows, edge_rows, _, _, _, link_rows = loader._read_records(ROOT)
    rec = {rid: {"id": rid, "type": kind, "status": status} for _, rid, kind, status in rows}
    edges = [{"type": t, "source": s, "target": d} for t, s, d in edge_rows]
    links = [{"type": t, "source": s, "target": d, "via": v} for t, s, d, v in link_rows]
else:
    con = sqlite3.connect((ROOT / loader.STORE_REL).resolve().as_uri() + "?mode=ro", uri=True)
    rec = {rid: {"id": rid, "type": kind, "status": status}
           for rid, kind, status in con.execute("SELECT id, type, status FROM records")}
    edges = [dict(zip(("type", "source", "target"), r)) for r in con.execute("SELECT type, source, target FROM edges")]
    try:
        links = [dict(zip(("type", "source", "target", "via"), r))
                 for r in con.execute(f"SELECT type, source, target, via FROM {loader.LINKS_TABLE}")]
    except sqlite3.OperationalError:
        sys.exit(f"{loader.LINKS_TABLE}: the store holds no stated links; rebuild the store with W2-92 S7")
    head = con.execute("SELECT head FROM fingerprints").fetchone()
superseded_edges = {e["target"] for e in edges if e["type"] == "SUPERSEDES"}
decisions = {rid for rid, r in rec.items() if r["type"] == "decision"}

# ---------------------------------------------------------------- the census's statements, by the loader's one function
reg_rel = yaml.safe_load((ROOT / loader.PATH_MAP_REL).read_text())[loader.REGISTER_KEY]
reg_text = (ROOT / reg_rel).read_text()
entries, _refused = loader.register_entries(reg_text)
entry = {e["id"]: e for e in entries}
said = loader.register_statements(reg_text, entries)  # the census's statements one for one (W2-92 S7)
statements = [s for s in said if s["where"] != "preamble"]
pre_statements = [s for s in said if s["where"] == "preamble"]
BY, vclass = loader._BY, loader._verb_class  # the archive's §A is read with the same patterns

arch_stmt, arch_spent = [], set()
if (ROOT / ARCHIVE).is_file():
    for line in (ROOT / ARCHIVE).read_text().split("## B.", 1)[-1].split("\n"):  # §B, "Spent" (census.py §2)
        if line.startswith("- DEC-") and re.search(r"\bSpent\b|\bspent\b", line):
            arch_spent |= {"DEC-" + x for x in DEC.findall(line[2:].split(":")[0])}
    for line in (ROOT / ARCHIVE).read_text().split("## B.")[0].split("\n"):
        if not line.startswith("- DEC-"):
            continue
        head_, _, tail = line[2:].partition(":")
        for b in BY.finditer(tail):
            for t in DEC.findall(head_):
                for y in DEC.findall(b.group(2)):
                    arch_stmt.append({"source": "DEC-" + y, "target": "DEC-" + t, "cls": vclass(b.group(1)),
                                      "form": "ARCHIVE-SUPERSEDED §A", "where": "archive"})


def current(t: str) -> bool:  # the census's: ACCEPTED, and no SUPERSEDES edge in ``edges``
    r = rec.get(t)
    return bool(r) and r["status"] == "ACCEPTED" and t not in superseded_edges


# DEC-1073 (2): the register is the authority. A decision the archive calls spent while the register lists it as
# current is no drift: it goes to a list for a status reconciliation. A decision not ACCEPTED (PROPOSED above all) is
# not in force and never current: the stated-changed ones are counted by their status, apart.
spent_current = sorted((t for t in arch_spent if current(t)), key=lambda x: int(x[4:]))
changers = collections.defaultdict(set)  # drifted decision -> the decisions stated to change it
kinds = collections.defaultdict(set)
stated_changed = set()
for s in statements + pre_statements + arch_stmt:
    if s["cls"] in ("supersede", "amend") and s["target"] in entry:
        stated_changed.add(s["target"])
        if current(s["target"]):
            changers[s["target"]].add(s["source"])
            kinds[s["target"]].add(s["cls"])
census_215 = len(changers)  # the census's count, spent included
spent_drifted = sorted((t for t in changers if t in arch_spent), key=lambda x: int(x[4:]))
for t in spent_drifted:
    del changers[t]
not_accepted = collections.defaultdict(list)  # status -> the stated-changed decisions with it, never current
for t in sorted(stated_changed, key=lambda x: int(x[4:])):
    if t in rec and rec[t]["status"] != "ACCEPTED":
        not_accepted[rec[t]["status"]].append(t)
drifted = sorted(changers, key=lambda x: int(x[4:]))


def hint(t: str) -> bool:  # the census's "hint in its own entry": its span names one of its changers
    return any(x in entry[t]["span"] for x in changers[t])


# ---------------------------------------------------------------- one hop, before and after
before = {(e["source"], e["target"]) for e in edges if e["type"] == "SUPERSEDES"}  # all the graph had: edges
after = before | {(lk["source"], lk["target"]) for lk in links if lk["type"] in graph_route.CHANGE_LINKS}
near = collections.defaultdict(set)  # the closure at R0/R1 over ``edges``: its neighbours, both ways
for e in edges:
    near[e["source"]].add(e["target"])
    near[e["target"]].add(e["source"])


def joined(pairs, t):
    return sorted((s for s in changers[t] if (s, t) in pairs), key=lambda x: int(x[4:]))


rows = []
for t in drifted:
    hop = graph_route.follow(links, [t], {t} | (near[t] & set(rec)), decisions)
    reach = set(hop["records"]) | near[t]
    rows.append({"id": t, "classes": sorted(kinds[t]), "changers": sorted(changers[t], key=lambda x: int(x[4:])),
                 "hint_in_own_entry": hint(t), "edge_before": joined(before, t), "edge_after": joined(after, t),
                 "reached_by_follow": sorted((changers[t] & reach), key=lambda x: int(x[4:])),
                 "named_in_changed_by": sorted(set(hop["changed_by"].get(t, ())) & changers[t]),
                 "only_in_archive": sorted(changers[t] - {s["source"] for s in statements + pre_statements
                                                          if s["target"] == t})})


def count(pred, subset=None):
    return sum(1 for r in rows if (subset is None or subset(r)) and pred(r))


no_hint = lambda r: not r["hint_in_own_entry"]  # noqa: E731
summary = {
    "store": "HEAD by the loader (--from-head)" if FROM_HEAD else {"head": head and head[0]},
    "links_by_type": dict(collections.Counter(lk["type"] for lk in links)),
    "census_drifted_current_with_spent": census_215,
    "drifted_current": len(rows), "drifted_no_hint": count(no_hint),
    "spent_for_status_reconciliation": {"count": len(spent_current), "ids": spent_current,
                                        "of_them_stated_changed": len(spent_drifted)},
    "stated_changed_not_accepted": {status: {"count": len(ids), "ids": ids}
                                    for status, ids in sorted(not_accepted.items())},
    "proposed_decisions_in_all": sum(1 for r in rec.values() if r["type"] == "decision"
                                     and r["status"] == "PROPOSED"),
    "superseded_in_part_current": count(lambda r: "supersede" in r["classes"]),
    "before": {"one_hop_edge_to_a_changer": count(lambda r: r["edge_before"])},
    "after": {
        "one_hop_edge_to_a_changer": count(lambda r: r["edge_after"]),
        "one_hop_edge_to_every_changer": count(lambda r: set(r["edge_after"]) == set(r["changers"])),
        "of_the_no_hint": count(lambda r: r["edge_after"], no_hint),
        "reached_by_follow_a_changer": count(lambda r: r["reached_by_follow"]),
        "reached_by_follow_every_changer": count(lambda r: set(r["reached_by_follow"]) == set(r["changers"])),
        "named_in_changed_by": count(lambda r: r["named_in_changed_by"]),
    },
    "not_joined": [{"id": r["id"], "changers": r["changers"], "only_in_archive": r["only_in_archive"]}
                   for r in rows if not r["edge_after"]],
    "changer_pairs": sum(len(r["changers"]) for r in rows),
    "changer_pairs_joined_after": sum(len(r["edge_after"]) for r in rows),
}
print(json.dumps(summary, indent=1))
if OUT is not None:
    OUT.write_text(json.dumps({"summary": summary, "rows": rows}, indent=1))
