"""D4B link census (DEC-1072 (1)): every link the repository states, against the edges its record graph holds.

Read-only. Run from anywhere:  PYTHONPATH=<clone>/src python3 census.py <clone> <out.json>
It reads the clone's HEAD files (working tree, clean at the measured commit), its git log and its store
(.gov-runtime/store.db) through gov.records, and writes one JSON of counts and examples. No model, no network.
Every text pattern here is a regular expression and is approximate where the report says so.
"""

from __future__ import annotations

import collections
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2])
sys.path.insert(0, str(ROOT / "src"))
from gov import records as R  # noqa: E402
from gov.store import loader  # noqa: E402

DEC = re.compile(r"\bDEC-(\d{3,})\b")
ANY_ID = re.compile(r"\b(?:DEC-\d{3,}|ADR-\d{4}|CAP-\d{2}(?:\.[a-z])?|MR-\d+|DAEO-[a-z0-9]{4}|W[123]-\d+[a-z]?(?![A-Za-z0-9-])"
                    r"|L-\d{4}|FAIL-\d{4}|EXP-[A-Za-z0-9-]+)\b")
W_TICKET = re.compile(r"\bW[123]-\d+[a-z]?(?![A-Za-z0-9])(?!-)")
DAEO = re.compile(r"\bDAEO-[a-z0-9]{4}\b")
CAP = re.compile(r"\bCAP-\d{2}(?:\.[a-z])?\b")
MR = re.compile(r"\bMR-\d+\b")

out: dict = {}


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, check=True, text=True).stdout


# ---------------------------------------------------------------- the graph as the product sees it
known = R.records(ROOT)
edges = R.edges(ROOT)
ids = {r["id"] for r in known}
rec = {r["id"]: r for r in known}
edge_count = collections.Counter(e["type"] for e in edges)
pairs = collections.defaultdict(set)  # frozenset({a, b}) -> edge types (the closure follows both ways)
for e in edges:
    pairs[frozenset((e["source"], e["target"]))].add(e["type"])
superseded_edges = {e["target"] for e in edges if e["type"] == "SUPERSEDES"}

# ticket aliases: a W1-/W2- id resolves to its ticket (wbs_id / external-ref), as graph_route resolves a W2 id
alias: dict[str, str] = {}
tickets: dict[str, dict] = {}
for path in sorted((ROOT / ".tickets").glob("*.md")):
    text = path.read_text()
    fm = loader._frontmatter(text)
    body = text.split("\n---", 1)[1] if "\n---" in text else ""
    tickets[fm["id"]] = {"fm": fm, "body": body, "path": str(path.relative_to(ROOT))}
    for key in ("wbs_id", "external-ref"):
        if fm.get(key):
            alias.setdefault(str(fm[key]), fm["id"])


def resolve(x: str) -> str | None:
    if x in ids:
        return x
    return alias.get(x)


def in_graph(a: str, b: str) -> bool:
    ra, rb = resolve(a) or a, resolve(b) or b
    return frozenset((ra, rb)) in pairs


con = sqlite3.connect((ROOT / ".gov-runtime/store.db").resolve().as_uri() + "?mode=ro", uri=True)
indexed = {p for p, i in con.execute("SELECT path, indexed FROM lexical_file") if i}
out["store"] = {
    "head": con.execute("SELECT head FROM fingerprints").fetchone()[0],
    "records": len(known), "records_by_type": dict(collections.Counter(r["type"] for r in known)),
    "edges": len(edges), "edges_by_type": dict(edge_count),
    "edge_pairs_by_kind": {f"{t}:{a}->{b}": n for (t, a, b), n in collections.Counter(
        (e["type"], rec.get(e["source"], {}).get("type"), rec.get(e["target"], {}).get("type")) for e in edges).items()},
    "commits": con.execute("SELECT count(*) FROM commits").fetchone()[0],
    "indexed_files": len(indexed),
}

rows: list[dict] = []  # the census table


def row(kind, where, form, instances, pairs_set, resolvable_pairs, in_graph_pairs, follow, note=""):
    rows.append({"kind": kind, "where": where, "form": form, "instances": instances, "pairs": len(pairs_set),
                 "resolvable": resolvable_pairs, "in_graph": in_graph_pairs, "followable": follow, "note": note})


def tally(kind, where, form, links, follow, note="", target_ok=None):
    """links: list of (source, target). Resolvable: the target resolves to a record (or target_ok says so)."""
    ps = set(links)
    ok = (lambda t: resolve(t) is not None) if target_ok is None else target_ok
    res = sum(1 for _, t in ps if ok(t))
    ing = sum(1 for s, t in ps if in_graph(s, t))
    row(kind, where, form, len(links), ps, res, ing, follow, note)
    return ps


# ---------------------------------------------------------------- 1. the register
reg_text = (ROOT / "docs/DECISION_REGISTER.md").read_text()
entries, _refused = loader.register_entries(reg_text)
entry = {e["id"]: e for e in entries}
for e in entries:
    e["end"] = e["line"] + e["span"].count("\n")
inside = set()
for e in entries:
    inside.update(range(e["line"], e["end"] + 1))
preamble = "\n".join(l for n, l in enumerate(reg_text.split("\n"), 1) if n not in inside)  # outside every entry

LABEL = re.compile(r"\*\*([A-Z][A-Za-z ]{1,40}?):\*\*")
OUT_LABELS = {  # this entry -> the ids its value names
    "Supersedes": "supersede", "Replaces": "supersede", "Withdraws": "supersede", "Reverses": "supersede",
    "Narrows": "amend", "Restores": "amend", "Clarifies": "refine",
    "Amends": "amend", "Changes": "amend", "Corrects": "amend",
    "Refines": "refine", "Extends": "extend", "Settles": "settle", "Ratifies": "ratify", "Confirms": "confirm",
    "Implements": "implement", "Under": "under", "Source": "source",
}
IN_LABELS = {"Changed by", "Amended by", "Lifted by", "Superseded by", "Amended"}  # the ids named -> this entry
VERB_CLASS = {"supersed": "supersede", "replac": "supersede", "withdr": "supersede", "revers": "supersede",
              "overturn": "supersede", "end": "supersede", "amend": "amend", "correct": "amend", "chang": "amend",
              "lift": "amend", "refin": "refine", "extend": "extend", "settl": "settle", "mark": "mark",
              "shown": "mark", "show": "mark", "carri": "carry", "kept": "mark", "confirm": "confirm"}
BY = re.compile(r"\b(superseded|replaced|withdrawn|reversed|overturned|ended|amended|corrected|changed|lifted|refined|"
                r"extended|settled|marked|shown|carried|kept|confirmed)\b[^.;·]{0,60}?\bby\s+(?:the\s+)?((?:DEC-\d{3,}"
                r"(?:\s*\([^)]{0,40}\))?(?:\s*(?:item|items|Q)\s*[\w.]+(?:\s*(?:and|,)\s*[\w.]+)*)?(?:\s*,\s*|\s+and\s+)?)+)")
OUTVERB = re.compile(r"\b(supersedes|replaces|withdraws|amends|overturns|reverses|corrects|refines|extends)\s+"
                     r"(?:the\s+[^.;·]{0,40}?of\s+)?(DEC-\d{3,})")
HERE = re.compile(r"(DEC-\d{3,})((?:\s*\([^)]*\))*?)\s*\((?:[^)]*?\b)?(amended|superseded|replaced|changed|withdrawn)"
                  r" here")


def vclass(verb: str) -> str:
    v = verb.lower()
    return next((c for k, c in VERB_CLASS.items() if v.startswith(k)), "amend")


def alone(value: str) -> bool:
    """The value names decisions alone (whole): ids, commas, 'and', dates in parentheses; nothing else."""
    s = re.sub(r"\(\d{4}-\d{2}-\d{2}[^)]*\)", "", value)
    s = re.sub(r"\(owner[^)]*\)", "", s)
    s = DEC.sub("", s)
    s = re.sub(r"\b(and|by)\b|[,.;\s]", "", s)
    return s == ""


statements = []  # {source, target, cls, form, whole, where}
under_other = []  # an entry's Under/Implements value naming a capability, MR, ADR or ticket
cites = []  # (entry, cited id) every DEC mention but itself
field_cites = collections.Counter()
for e in entries:
    me, span = e["id"], e["span"]
    for m in DEC.finditer(span):
        t = m.group(0)
        if t != me:
            cites.append((me, t))
    labels = list(LABEL.finditer(span))
    consumed = []
    for i, m in enumerate(labels):
        name = m.group(1).strip()
        end = labels[i + 1].start() if i + 1 < len(labels) else len(span)
        value = span[m.end():end]
        value_line = value.split("\n- ")[0] if name not in ("Changes",) else value.split("\n- **")[0]
        value_line = value_line.split(" · ")[0]
        field_cites[name] += len([x for x in DEC.findall(value_line)])
        if name in OUT_LABELS:
            cls = OUT_LABELS[name]
            consumed.append((m.start(), m.end() + len(value_line)))
            for t in DEC.finditer(value_line):
                if t.group(0) != me:
                    statements.append({"source": me, "target": t.group(0), "cls": cls, "form": f"**{name}:**",
                                       "whole": alone(value_line), "where": "label"})
            if name in ("Under", "Implements"):
                under_other += [(me, x) for x in ANY_ID.findall(value_line) if not x.startswith("DEC-")]
            if name == "Under":  # "DEC-x (amended here)" inside an Under value
                for h in HERE.finditer(value_line):
                    statements.append({"source": me, "target": h.group(1), "cls": vclass(h.group(3)),
                                       "form": "(amended here)", "whole": False, "where": "label"})
        elif name in IN_LABELS:
            consumed.append((m.start(), m.end() + len(value_line)))
            found = False
            for b in BY.finditer(value_line):
                for t in DEC.findall(b.group(2)):
                    found = True
                    statements.append({"source": "DEC-" + t, "target": me, "cls": vclass(b.group(1)),
                                       "form": f"**{name}:** {b.group(1)} by", "where": "label",
                                       "whole": bool(re.match(r"\s*(superseded|replaced|withdrawn)\s+by", value_line))
                                       and alone(re.sub(r"\b(superseded|replaced|withdrawn)\b", "", value_line))})
            if not found:  # "**Changed by:** DEC-953 (item 3)": a change with no verb
                cls = "amend" if name != "Superseded by" else "supersede"
                for t in DEC.findall(value_line):
                    statements.append({"source": "DEC-" + t, "target": me, "cls": cls, "form": f"**{name}:**",
                                       "whole": False, "where": "label"})
        elif name == "Superseded":  # "**Superseded:** DEC-002 (by DEC-058, DEC-064); ..."
            consumed.append((m.start(), m.end() + len(value_line)))
            for x, ys in re.findall(r"(DEC-\d{3,})\s*\(by ([^)]*)\)", value_line):
                for y in DEC.findall(ys):
                    statements.append({"source": "DEC-" + y, "target": x, "cls": "supersede",
                                       "form": "**Superseded:** X (by Y)", "whole": True, "where": "label"})

    def free(pos):
        return not any(a <= pos < b for a, b in consumed)

    for b in BY.finditer(span):  # free text: "... superseded by DEC-x": the subject is the nearest id before
        if not free(b.start()):
            continue
        before = span[max(0, b.start() - 160):b.start()]
        clause = re.split(r"(?<=\.)\s|·|\n", before)[-1]
        if clause.count('"') % 2 or clause.count("\u201c") > clause.count("\u201d"):
            continue  # inside a quotation: an example, not a statement
        subj = DEC.findall(re.split(r";", clause)[-1]) or re.findall(r"DEC-(\d{3,})['\u2019]s\b", clause)
        target = "DEC-" + subj[-1] if subj else me
        for t in DEC.findall(b.group(2)):
            if "DEC-" + t != target:
                statements.append({"source": "DEC-" + t, "target": target, "cls": vclass(b.group(1)),
                                   "form": f"text: {b.group(1)} by", "whole": False, "where": "text"})
    for o in OUTVERB.finditer(span):
        if not free(o.start()):
            continue
        before = span[max(0, o.start() - 120):o.start()]
        clause = re.split(r"(?<=\.)\s|·|\n", before)[-1]
        if clause.count('"') % 2:
            continue
        subj = DEC.findall(clause)
        source = "DEC-" + subj[-1] if subj else me
        if o.group(2) != source:
            statements.append({"source": source, "target": o.group(2), "cls": vclass(o.group(1)),
                               "form": f"text: {o.group(1)}", "whole": False, "where": "text"})
    for h in HERE.finditer(span):
        if free(h.start()) and h.group(1) != me:
            statements.append({"source": me, "target": h.group(1), "cls": vclass(h.group(3)),
                               "form": "text: (… here)", "whole": False, "where": "text"})

# the register's preamble (its change-log table): "DEC-051 (...; supersedes DEC-048)"
pre_statements = []
for o in OUTVERB.finditer(preamble):
    subj = DEC.findall(preamble[max(0, o.start() - 120):o.start()])
    if subj:
        pre_statements.append({"source": "DEC-" + subj[-1], "target": o.group(2), "cls": vclass(o.group(1)),
                               "form": f"change log: {o.group(1)}", "whole": False, "where": "preamble"})

# de-duplicate: one statement per (source, target, cls, form)
seen, uniq = set(), []
for s in statements:
    k = (s["source"], s["target"], s["cls"], s["form"])
    if k not in seen:
        seen.add(k)
        uniq.append(s)
statements = uniq
own_status = {e["id"]: e["first"] for e in entries}

by_cls = collections.defaultdict(list)
for s in statements:
    by_cls[s["cls"]].append(s)
reg_follow = "graph (SUPERSEDES only)"
for cls in ("supersede", "amend", "refine", "extend", "settle", "ratify", "confirm", "implement", "under", "source",
            "mark", "carry"):
    ss = by_cls.get(cls, [])
    if not ss:
        continue
    forms = collections.Counter(s["form"].split(" by")[0] if s["form"].startswith("text") else s["form"] for s in ss)
    links = [(s["source"], s["target"]) for s in ss]
    tally(f"decision {cls} decision", "register entries", "; ".join(f"{f} {n}" for f, n in forms.most_common(6)),
          links, "graph" if cls == "supersede" and False else "keyword only",
          note=f"whole (ids alone) {sum(s['whole'] for s in ss)}; labelled {sum(s['where'] == 'label' for s in ss)},"
               f" free text {sum(s['where'] == 'text' for s in ss)}")
tally("decision cites decision (any DEC id in an entry but its own)", "register entries", "DEC-n anywhere in the span",
      cites, "keyword only")
tally("decision under / implements capability, MR, ADR, ticket", "register entries", "**Under:** CAP-n, MR-n",
      under_other, "keyword only")
out["register_dec_mentions_total"] = len(DEC.findall(reg_text))
out["register_dec_mentions_in_spans_incl_self"] = sum(len(DEC.findall(e["span"])) for e in entries)
tally("register change log: X supersedes/amends Y", "register preamble table", "'(...; amends DEC-n)'",
      [(s["source"], s["target"]) for s in pre_statements], "keyword only")

status_words = collections.Counter(rec[e]["status"] for e in entry)
own_marks = {e: f for e, f in own_status.items() if re.search(r"supersed|amended|withdrawn|replaced|changed by|"
                                                              r"corrected|lifted by", f, re.I)}
out["register"] = {
    "entries": len(entries), "status_words": dict(status_words),
    "fields_with_ids": dict(field_cites.most_common()),
    "cites_instances": len(cites), "cites_pairs": len(set(cites)),
    "cites_resolvable_pairs": sum(1 for _, t in set(cites) if t in ids),
    "cites_in_graph_pairs": sum(1 for s, t in set(cites) if in_graph(s, t)),
    "statements_by_class": {c: len(v) for c, v in by_cls.items()},
    "statements_by_class_whole": {c: sum(s["whole"] for s in v) for c, v in by_cls.items()},
    "statements_pairs_by_class": {c: len({(s["source"], s["target"]) for s in v}) for c, v in by_cls.items()},
    "own_status_line_marks": len(own_marks),
    "preamble_statements": len(pre_statements),
    "supersedes_edges_from_register": sorted(f"{e['source']}->{e['target']}" for e in edges if e["type"] == "SUPERSEDES"),
}

# ---------------------------------------------------------------- the drift count
lex = [dict(zip(("chunk_id", "path", "start_line", "end_line"), r)) for r in
       con.execute("SELECT chunk_id, path, start_line, end_line FROM lexical_chunk WHERE path = ?",
                   ("docs/DECISION_REGISTER.md",))]
chunk_text = {}
reg_lines = reg_text.split("\n")
for c in lex:
    chunk_text[c["chunk_id"]] = "\n".join(reg_lines[c["start_line"] - 1:c["end_line"]])
chunks_of = collections.defaultdict(list)
for c in lex:
    for e in entries:
        if e["line"] <= c["start_line"] <= e["end"]:
            chunks_of[e["id"]].append(c["chunk_id"])
            break


def current(t: str) -> bool:
    r = rec.get(t)
    return bool(r) and r["status"] == "ACCEPTED" and r["status"] != "SUPERSEDED" and t not in superseded_edges \
        and r["status"] not in ("DEPRECATED", "REJECTED", "WITHDRAWN")


archive = (ROOT / "governance/project/orchestration/ARCHIVE-SUPERSEDED.md").read_text()
arch_a = archive.split("## B.")[0]
arch_rest = archive.split("## B.", 1)[1]
arch_stmt = []
for line in arch_a.split("\n"):
    if not line.startswith("- DEC-"):
        continue
    head, _, tail = line[2:].partition(":")
    for b in BY.finditer(tail):
        for t in DEC.findall(head):
            for y in DEC.findall(b.group(2)):
                arch_stmt.append({"source": "DEC-" + y, "target": "DEC-" + t, "cls": vclass(b.group(1)),
                                  "whole": bool(re.fullmatch(r"(?:DEC-\d+(?:,\s*|\s+and\s+)?)+", head.strip()))
                                  and bool(re.fullmatch(r"\s*(?:SUPERSEDED|superseded|withdrawn|replaced|reversed)\s*",
                                                        tail[:b.start()] + b.group(1) + " "))
                                  and bool(re.fullmatch(r"[.\s]*(?:\([^)]*\))?[.\s]*", tail[b.end():]))})
arch_spent = set()
for line in arch_rest.split("\n"):
    if line.startswith("- DEC-") and re.search(r"\bSpent\b|\bspent\b", line):
        head = line[2:].split(":")[0]
        arch_spent |= {"DEC-" + x for x in DEC.findall(head)}
    m = re.match(r"- DEC-(\d+) to DEC-(\d+)", line)

drift = {"supersede": collections.defaultdict(list), "amend": collections.defaultdict(list)}
for s in statements + pre_statements + [dict(a, form="ARCHIVE-SUPERSEDED §A", where="archive") for a in arch_stmt]:
    if s["cls"] in drift and s["target"] in entry:
        drift[s["cls"]][s["target"]].append(s)


def hint(target: str, sources: set[str]):
    """Whether the target's own span, and each of its chunks, names any of the sources or marks itself changed."""
    span = entry[target]["span"]
    mark = re.compile(r"supersed|amended by|withdrawn|replaced by|changed by|corrected by|lifted by", re.I)
    in_span = any(x in span for x in sources)
    status_mark = bool(mark.search(entry[target]["first"]))
    ch = chunks_of.get(target, [])
    ch_hint = sum(1 for c in ch if any(x in chunk_text[c] for x in sources))
    return in_span, status_mark, len(ch), ch_hint


dr = {}
examples = {}
for cls in ("supersede", "amend"):
    cur = {t: v for t, v in drift[cls].items() if current(t)}
    whole = {t for t, v in cur.items() if any(s["whole"] for s in v)}
    rows_ = []
    for t, v in sorted(cur.items(), key=lambda kv: int(kv[0][4:])):
        srcs = {s["source"] for s in v}
        in_span, status_mark, nch, ch_hint = hint(t, srcs)
        rows_.append({"id": t, "by": sorted(srcs, key=lambda x: int(x[4:])), "whole": t in whole,
                      "forms": sorted({s.get("form", "") for s in v}), "hint_in_span": in_span,
                      "status_line_marks": status_mark, "chunks": nch, "chunks_with_hint": ch_hint})
    dr[cls] = {
        "targets_stated": len(drift[cls]), "targets_current": len(cur), "current_whole": len(whole),
        "current_no_hint_in_span": sum(1 for r in rows_ if not r["hint_in_span"]),
        "current_no_hint_status_line": sum(1 for r in rows_ if not r["status_line_marks"]),
        "chunks_of_current": sum(r["chunks"] for r in rows_),
        "chunks_without_hint": sum(r["chunks"] - r["chunks_with_hint"] for r in rows_),
        "not_current_already": sorted(t for t in drift[cls] if not current(t)),
    }
    examples[cls] = rows_
both = set(examples["supersede"] and [r["id"] for r in examples["supersede"]]) | {r["id"] for r in examples["amend"]}
dr["either"] = {"current": len(both),
                "no_hint_in_span": len({r["id"] for c in ("supersede", "amend") for r in examples[c]
                                        if not r["hint_in_span"]}
                                       - {r["id"] for c in ("supersede", "amend") for r in examples[c]
                                          if r["hint_in_span"]})}
dr["spent_per_archive"] = {"ids": len(arch_spent), "current": sum(1 for t in arch_spent if current(t))}
dr["archive_A_statements"] = len(arch_stmt)
dr["archive_A_targets_current"] = len({a["target"] for a in arch_stmt if current(a["target"])})
reg_targets = {s["target"] for s in statements if s["cls"] in ("supersede", "amend")}
dr["archive_A_targets_not_found_in_register_text"] = sorted({a["target"] for a in arch_stmt} - reg_targets)
dr["proposed_or_done_current_but_stated"] = sorted(set(
    t for c in drift for t in drift[c] if t in rec and rec[t]["status"] in ("PROPOSED", "DONE", "CONDITIONAL")
    and t not in superseded_edges))
out["drift"] = dr
out["drift_examples"] = examples

# ---------------------------------------------------------------- 2. tickets
tk = collections.defaultdict(list)
kpi_dec, body_dec, body_w, kpi_tests = [], [], [], []
for tid, t in tickets.items():
    fm = t["fm"]
    for key in ("sources", "closes", "deps", "depends_on", "links", "parent", "list_rows"):
        v = fm.get(key) or []
        for x in (v if isinstance(v, list) else [v]):
            tk[key].append((tid, str(x)))
    k = fm.get("kpis") or {}
    ktext = json.dumps(k)
    kpi_dec += [(tid, "DEC-" + x) for x in DEC.findall(ktext)]
    body_dec += [(tid, "DEC-" + x) for x in DEC.findall(t["body"])]
    body_w += [(tid, x) for x in W_TICKET.findall(t["body"] + ktext) if resolve(x) != tid]
    at = fm.get("acceptance_tests")
    if isinstance(at, dict) and at.get("path"):
        kpi_tests.append((tid, at["path"]))
srcs = tk["sources"]
tally("ticket sources -> decision", ".tickets/*.md front matter", "sources: [DEC-n]",
      [p for p in srcs if p[1].startswith("DEC-")], "keyword only")
tally("ticket sources -> capability / MR / ADR", ".tickets/*.md front matter", "sources: [CAP-n, MR-n]",
      [p for p in srcs if not p[1].startswith("DEC-")], "keyword only")
tally("ticket closes -> decision / capability / row", ".tickets/*.md front matter", "closes: [...]", tk["closes"],
      "keyword only", note="W2-H/M/L list rows are rows of docs/plan lists, no records")
tally("ticket depends_on -> ticket", ".tickets/*.md front matter", "depends_on: [DAEO-x]", tk["depends_on"], "graph")
tally("ticket deps -> ticket (tk's copy)", ".tickets/*.md front matter", "deps: [DAEO-x]", tk["deps"], "graph",
      note="duplicates depends_on where both are present")
tally("ticket links -> ticket", ".tickets/*.md front matter", "links: [DAEO-x]", tk["links"], "keyword only")
tally("ticket parent -> ticket", ".tickets/*.md front matter", "parent: DAEO-x", tk["parent"], "keyword only")
tally("ticket list_rows -> list row", ".tickets/*.md front matter", "list_rows: [W2-H001]", tk["list_rows"],
      "keyword only", target_ok=lambda t: False, note="rows of the plan's lists; no record holds them")
tally("ticket KPI names decision", ".tickets/*.md kpis", "[DEC-n] in a KPI line", kpi_dec, "keyword only")
tally("ticket body names decision", ".tickets/*.md body", "DEC-n in the text", body_dec, "keyword only")
tally("ticket names ticket (W-id in KPIs/body)", ".tickets/*.md body and kpis", "W2-n", body_w, "keyword only")

# ---------------------------------------------------------------- 3. commit trailers
log = git("log", "--format=%x1e%H%x1f%(trailers:key=Task,key=Implements,key=Role,key=Decided-by,unfold)%x1f%B",
          "HEAD")
tr = collections.defaultdict(list)
msg_dec = []
task_impl = []
for item in log.split("\x1e")[1:]:
    h, block, body = item.split("\x1f", 2)
    got = collections.defaultdict(list)
    for line in block.splitlines():
        key, _, val = line.partition(":")
        for v in (re.split(r"[,\s]+", val.strip()) if key.strip() in ("Task", "Implements") else [val.strip()]):
            if v:
                got[key.strip()].append(v)
    for key, vals in got.items():
        tr[key] += [(h, v) for v in vals]
    trailer_free = "\n".join(l for l in body.splitlines() if not re.match(r"^[A-Z][A-Za-z-]+: ", l))
    msg_dec += [(h, "DEC-" + x) for x in DEC.findall(trailer_free)]
    for t in got.get("Task", []):
        for d in got.get("Implements", []):
            task_impl.append((t, d))
store_tr = collections.defaultdict(list)
for c, k, v in con.execute("SELECT commit_id, key, value FROM trailers"):
    store_tr[k].append((c, v))
out["trailers"] = {}
for key in ("Task", "Implements", "Role", "Decided-by"):
    links = tr.get(key, [])
    vals = collections.Counter(v for _, v in links)
    res = sum(1 for v in vals if resolve(v))
    out["trailers"][key] = {"instances": len(links), "commits": len({c for c, _ in links}), "distinct_values": len(vals),
                            "resolvable_values": res,
                            "store_instances": len(store_tr.get(key, []))}
    row(f"commit trailer {key}:", "git log (final trailer block)", f"{key}: <id>", len(links),
        set(links), sum(1 for _, v in set(links) if resolve(v)) if key in ("Task", "Implements") else 0, 0,
        "no (store table, not an edge; git log)" if key in ("Task", "Implements") else "no (git log only)",
        note=f"{len({c for c, _ in links})} commits, {len(vals)} distinct values; the store keeps Task/Implements in"
             f" its trailers table ({len(store_tr.get(key, []))} rows), never as edges")
ti = set(task_impl)
tally("ticket implements decision, via one commit's Task+Implements", "git log trailers", "Task: T + Implements: D",
      task_impl, "no", target_ok=lambda t: resolve(t) is not None)
row("commit message names decision", "git log (subject and body)", "DEC-n in the message", len(msg_dec),
    set(msg_dec), sum(1 for _, t in set(msg_dec) if t in ids), 0, "no (git log only)",
    note="commit messages are not indexed")

# ---------------------------------------------------------------- 4. Contract and capabilities
contract = yaml.safe_load((ROOT / "docs/contract/contract.yaml").read_text())
cap_prov, cap_src, item_prov, mr_prov, mr_src, item_src = [], [], [], [], [], []
for c in contract["capabilities"]:
    cap_prov += [(c["id"], str(p)) for p in c.get("provider", []) or []]
    cap_src += [(c["id"], "DEC-" + x) for s in c.get("sources", []) or [] for x in DEC.findall(str(s))]
    for it in c.get("covers", []) or []:
        item_prov += [(it["id"], str(p)) for p in it.get("provider", []) or []]
        item_src += [(it["id"], "DEC-" + x) for x in DEC.findall(str(it.get("source", "")))]
for m in contract.get("master_rules", []):
    mr_prov += [(m["id"], str(p)) for p in m.get("provider", []) or []]
    mr_src += [(m["id"], "DEC-" + x) for s in m.get("sources", []) or [] for x in DEC.findall(str(s))]
tal = lambda links: [p for p in links if W_TICKET.fullmatch(p[1])]  # noqa: E731
tally("capability -> provider ticket", "docs/contract/contract.yaml capabilities[].provider", "provider: [W1-10]",
      tal(cap_prov), "keyword only", note=f"{len(cap_prov) - len(tal(cap_prov))} more providers are tools, not tickets")
tally("capability item -> provider ticket", "contract.yaml capabilities[].covers[].provider", "provider: [W1-24]",
      tal(item_prov), "keyword only", note=f"{len(item_prov) - len(tal(item_prov))} more are tools")
tally("capability -> decision (sources)", "contract.yaml capabilities[].sources and covers[].source", "DEC-n",
      cap_src + item_src, "keyword only")
tally("master rule -> provider ticket", "contract.yaml master_rules[].provider", "provider: [W1-12]", tal(mr_prov),
      "keyword only")
tally("master rule -> decision", "contract.yaml master_rules[].sources", "DEC-n", mr_src, "keyword only")
cap_dep = [(e["source"], e["target"]) for e in edges if e["type"] == "DEPENDS_ON" and rec.get(e["source"], {}).get("type") == "capability"]
tally("capability item -> its capability; capability -> Contract", "docs/contract/capabilities/*.md front matter",
      "depends_on: [CAP-01]", cap_dep, "graph")
ct = (ROOT / "docs/contract/CONTRACT_v4.md").read_text()
tally("Contract text cites decision", "docs/contract/CONTRACT_v4.md", "DEC-n",
      [("CONTRACT-v4", "DEC-" + x) for x in DEC.findall(ct)], "keyword only")

# ---------------------------------------------------------------- 5. KPI -> tests
tdirs = {p.name for p in (ROOT / "tests/acceptance").iterdir() if p.is_dir()}
tally("ticket -> its acceptance tests", ".tickets/*.md acceptance_tests.path", "path: tests/acceptance/W2-21/",
      kpi_tests, "keyword only (the path, not the files)", target_ok=lambda t: (ROOT / t).exists(),
      note=f"resolvable = the path exists; {len(tdirs)} folders under tests/acceptance")
fold = [(d, alias.get(d, d)) for d in tdirs]
row("test folder -> ticket (by folder name)", "tests/acceptance/<W-id>/", "folder named by the WBS id", len(fold),
    set(fold), sum(1 for d, t in fold if t in ids), 0, "no edge; keyword on the path")
test_dec, test_tk = [], []
for f in (ROOT / "tests").rglob("*.py"):
    s = f.read_text(errors="replace")
    rel = str(f.relative_to(ROOT))
    test_dec += [(rel, "DEC-" + x) for x in DEC.findall(s)]
    test_tk += [(rel, x) for x in W_TICKET.findall(s)]
tally("test file names decision", "tests/**/*.py", "DEC-n in docstrings/comments", test_dec, "keyword only",
      note="tests/** are indexed today; DEC-1052 M-4 plans to stop embedding them")
tally("test file names ticket", "tests/**/*.py", "W2-n", test_tk, "keyword only")
tm = yaml.safe_load((ROOT / "governance/project/test-map.yaml").read_text())
coup = [(p, s) for c in tm.get("couplings", []) or [] for p in c["paths"] for s in c["suites"]]
row("test map coupling: path -> suite", "governance/project/test-map.yaml couplings", "paths: [...] suites: [...]",
    len(coup), set(coup), sum(1 for _, s in set(coup) if (ROOT / s).exists()), 0, "keyword only",
    note="resolvable = the suite path exists")
tmt = (ROOT / "governance/project/test-map.yaml").read_text()
tally("test map cites decision", "test-map.yaml comments", "# DEC-n", [("test-map", "DEC-" + x) for x in DEC.findall(tmt)],
      "keyword only")

# ---------------------------------------------------------------- 6. roles and skills
skills = sorted(p.parent.name for p in (ROOT / "template/governance/kernel/skills").rglob("SKILL.md"))
role_sk, role_dec, sk_dec, sk_role = [], [], [], []
roles = sorted(p.stem for p in (ROOT / "template/governance/kernel/roles").glob("*.md"))
for p in (ROOT / "template/governance/kernel/roles").glob("*.md"):
    s = p.read_text()
    role_sk += [(p.stem, k) for k in skills if re.search(rf"(skills/{k}\b|\b{k}\b skill|`{k}`)", s)]
    role_dec += [(p.stem, x) for x in ANY_ID.findall(s) if x.startswith(("DEC", "CAP", "MR"))]
for p in (ROOT / "template/governance/kernel/skills").rglob("SKILL.md"):
    s = p.read_text()
    k = p.parent.name
    sk_dec += [(k, x) for x in ANY_ID.findall(s) if x.startswith(("DEC", "CAP", "MR"))]
    sk_role += [(k, r) for r in roles if re.search(rf"\b{r.replace('-', '[- ]')}\b", s)]
row("role -> skill", "template/governance/kernel/roles/*.md", "a skill named in the role file", len(role_sk),
    set(role_sk), len(set(role_sk)), 0, "no", note=f"{len(roles)} roles, {len(skills)} skills; no role file names a skill")
row("skill -> role", "kernel skills SKILL.md", "the role named in the text", len(sk_role), set(sk_role),
    len(set(sk_role)), 0, "keyword only")
tally("role file cites decision / capability / MR", "kernel roles", "DEC-n, CAP-n, MR-n", role_dec, "keyword only")
tally("skill cites decision / capability / MR", "kernel skills", "DEC-n, CAP-n", sk_dec, "keyword only")

# ---------------------------------------------------------------- 7. lessons and failures
les_c, les_src = [], []
for p in (ROOT / "docs/lessons").glob("*.md"):
    s = p.read_text()
    fm = loader._frontmatter(s)
    les_c += [(fm["id"], x) for x in fm.get("constrains", []) or []]
    les_src += [(fm["id"], "DEC-" + x) for x in DEC.findall(s.split("\n---", 1)[1])]
tally("lesson constrains ticket", "docs/lessons/*.md front matter", "constrains: [DAEO-x]", les_c, "graph")
tally("lesson -> the decision it came from", "docs/lessons/*.md body", "**Source:** DEC-n", les_src, "keyword only")
fails = [r for r in known if r["type"] == "failure" and "templates" not in r["path"]]
row("failure record -> its source", "failure records", "(none exist beyond the template)", 0, set(), 0, 0, "-",
    note=f"{len(fails)} failure records outside the template")

# ---------------------------------------------------------------- 8. plan, path map
plan_dec, card_tk, card_dec = [], [], []
for p in (ROOT / "docs/plan").glob("*.md"):
    s = p.read_text()
    fm = loader._frontmatter(s) or {}
    plan_dec += [(fm.get("id", p.stem), str(x)) for x in fm.get("decisions", []) or []]
    cur = None
    for line in s.split("\n"):
        h = re.match(r"#{2,5} (W[123]-\d+[a-z]?)\b", line)
        if h:
            cur = h.group(1)
            card_tk.append((p.stem, cur))
            continue
        if line.startswith("#"):
            cur = None
        if cur:
            card_dec += [(cur, "DEC-" + x) for x in DEC.findall(line)]
tally("plan -> decisions (front matter)", "docs/plan/*.md front matter", "decisions: [DEC-n]", plan_dec,
      "keyword only", note="'decisions' is no edge type of the loader")
tally("plan card -> ticket", "docs/plan/*.md '#### W2-n' cards", "card heading", card_tk, "keyword only")
tally("plan card (ticket) -> decision", "docs/plan/*.md card text", "DEC-n under a card", card_dec, "keyword only")
pm = (ROOT / "governance/project/path-map.yaml").read_text()
tally("path map entry -> decision", "governance/project/path-map.yaml comments", "# DEC-n",
      [("path-map", "DEC-" + x) for x in DEC.findall(pm)], "keyword only")

# ---------------------------------------------------------------- 9. others: other records' front matter, packages
other = collections.defaultdict(list)
for path, fm, err in loader.frontmatters(ROOT):
    if not isinstance(fm, dict) or "id" not in fm or path.startswith(".tickets/") or path.startswith("docs/plan/"):
        continue
    for key in ("task", "decisions", "decisions_applied", "requirements_implemented", "decisions_carried",
                "decisions_recorded", "decisions_read"):
        v = fm.get(key)
        for x in (v if isinstance(v, list) else [v] if v else []):
            other[(fm.get("type"), key)].append((fm["id"], str(x)))
for (typ, key), links in sorted(other.items(), key=lambda kv: -len(kv[1])):
    tally(f"{typ} {key} -> {'ticket' if key == 'task' else 'decision'}", f"{typ} records front matter", f"{key}:",
          links, "keyword only", note="no edge type of the loader")
pk, pk_dec = [], []
for p in (ROOT / "governance/project/orchestration/packages").rglob("*.md"):
    s = p.read_text(errors="replace")
    rel = str(p.relative_to(ROOT))
    pk += [(rel, x) for x in set(W_TICKET.findall(p.stem + " " + s[:2000]))]
    pk_dec += [(rel, "DEC-" + x) for x in DEC.findall(s)]
tally("review package -> ticket (W-id in name or opening)", "governance/project/orchestration/packages/**",
      "W2-n", pk, "keyword only", note="approximate: any W-id in the file name or first 2,000 characters")
tally("review package cites decision", "packages/**", "DEC-n", pk_dec, "keyword only")
# every other indexed text file citing a decision
oth = []
skip = ("docs/DECISION_REGISTER.md", ".tickets/", "tests/", "docs/plan/", "governance/project/orchestration/packages/",
        "template/governance/kernel/skills/", "template/governance/kernel/roles/", "docs/contract/")
for p in indexed:
    if p.startswith(skip) or not (ROOT / p).is_file():
        continue
    try:
        s = (ROOT / p).read_text()
    except (UnicodeDecodeError, OSError):
        continue
    oth += [(p, "DEC-" + x) for x in DEC.findall(s)]
tally("any other indexed file cites decision", "the rest of the index (checkpoints, research, briefs, src, …)",
      "DEC-n", oth, "keyword only", note=f"{len({s for s, _ in oth})} files")
inforce = (ROOT / "governance/project/orchestration/DECISIONS-IN-FORCE.md").read_text()
tally("in-force list names decision", "orchestration/DECISIONS-IN-FORCE.md", "DEC-n",
      [("DECISIONS-IN-FORCE", "DEC-" + x) for x in DEC.findall(inforce)], "keyword only")
tally("archive: X superseded/changed by Y", "orchestration/ARCHIVE-SUPERSEDED.md §A", "- DEC-x: ... by DEC-y",
      [(a["source"], a["target"]) for a in arch_stmt], "keyword only")
row("archive: decision spent", "ARCHIVE-SUPERSEDED.md §B", "- DEC-x: ... Spent.", len(arch_spent), arch_spent,
    sum(1 for t in arch_spent if t in ids), 0, "keyword only", note="a state, not a pair")

out["rows"] = rows
out["cites_by_field"] = dict(field_cites.most_common(25))
OUT.write_text(json.dumps(out, indent=1, default=list))
print(json.dumps({"rows": len(rows), "drift": {k: v for k, v in dr.items() if k in ("supersede", "amend", "either")}},
                 indent=1, default=list))
