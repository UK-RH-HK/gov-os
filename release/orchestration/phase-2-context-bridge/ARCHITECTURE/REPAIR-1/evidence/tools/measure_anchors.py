#!/usr/bin/env python3
"""BR-AR-0016 failure analysis: per failed [D] item of the run-1 grade, measure where the required evidence was.

Reads the QUARANTINED grade report and oracle at runtime (``git show bridge/grade-0012:<path>``); this file itself
carries no oracle content. Writes two outputs:
  --private-out  full detail, including anchor locators  (NEVER committed: it is per-query expected items)
  --public-out   keys + measured booleans/ranks + class only (committable)

Read-only against the store: it must be pointed (GOVBRIDGE_STORE) at a COPY of the demonstration store, with
GOV_BRIDGE_HOME at a scratch home (telemetry isolation). It never writes the store.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys

import yaml

DOM = "release/orchestration/phase-2-context-bridge"
QBR = "bridge/grade-0012"
TOL = 3
K_PROBE = 200


def sh(args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def repo_root():
    return sh(["git", "rev-parse", "--show-toplevel"]).stdout.strip()


REPO = None
_blob = {}


def blob(commit, path):
    if not commit or not path:
        return None
    k = (commit, path)
    if k not in _blob:
        r = sh(["git", "rev-parse", "-q", "--verify", f"{commit}:{path}"], cwd=REPO)
        _blob[k] = r.stdout.strip() if r.returncode == 0 else None
    return _blob[k]


def full_commit(c):
    if not c:
        return c
    r = sh(["git", "rev-parse", "-q", "--verify", f"{c}^{{commit}}"], cwd=REPO)
    return r.stdout.strip() or c


def quarantined(path):
    r = sh(["git", "show", f"{QBR}:{DOM}/{path}"], cwd=REPO)
    if r.returncode != 0:
        raise SystemExit(f"cannot read quarantined {path}: {r.stderr}")
    return r.stdout


def same_file(a_commit, a_path, b_commit, b_path):
    if not a_path or a_path != b_path:
        return False
    if a_commit and b_commit and full_commit(a_commit) == full_commit(b_commit):
        return True
    ba, bb = blob(a_commit, a_path), blob(b_commit, b_path)
    return bool(ba and ba == bb)


def overlap(al, bl, tol=TOL):
    if not al or not bl:
        return False
    return bl[0] <= al[1] + tol and bl[1] >= al[0] - tol


def substantive(al, bl):
    """Evidence-possession overlap: no tolerance, and at least min(3, anchor length) shared lines."""
    if not al or not bl or bl[0] is None:
        return False
    shared = min(al[1], bl[1]) - max(al[0], bl[0]) + 1
    return shared >= min(3, al[1] - al[0] + 1)


def anchor_label(a):
    s = f"{a.get('kind')}:{a.get('path')}@{(a.get('commit') or '')[:7]}"
    if a.get("lines"):
        s += f":{a['lines'][0]}-{a['lines'][1]}"
    for k in ("record_id", "symbol", "section"):
        if a.get(k):
            s += f" {k}={a[k]}"
    return s


def parse_label(lbl):
    """Grade-report missed_required strings -> anchor dict (to find the oracle index)."""
    m = re.match(r"^(\w+):(.+?)@([0-9a-f]+):(\d+)-(\d+)(.*)$", lbl)
    if not m:
        m2 = re.match(r"^(\w+):(.+?)@([0-9a-f]+)(.*)$", lbl)
        if not m2:
            return {"raw": lbl}
        kind, path, commit, rest = m2.groups()
        d = {"kind": kind, "path": path, "commit": commit}
    else:
        kind, path, commit, l1, l2, rest = m.groups()
        d = {"kind": kind, "path": path, "commit": commit, "lines": [int(l1), int(l2)]}
    rid = re.search(r"record_id=(\S+)", rest)
    sym = re.search(r"symbol=(\S+)", rest)
    if rid:
        d["record_id"] = rid.group(1)
    if sym:
        d["symbol"] = sym.group(1)
    return d


def same_anchor(a, b):
    return (a.get("path") == b.get("path") and (a.get("commit") or "")[:7] == (b.get("commit") or "")[:7]
            and (a.get("lines") or None) == (b.get("lines") or None)
            and (a.get("record_id") or None) == (b.get("record_id") or None)
            and (a.get("symbol") or None) == (b.get("symbol") or None))


# ------------------------------------------------------------------------------------------------ packet spans

def packet_spans(manifest, capture):
    """Every packet item as a span. level: CONTENT (anchor text delivered), POINTER (location only, no body),
    TRUNCATED (an A item whose rendered excerpt stops before the end of its source)."""
    pre = {}
    for sec, items in capture["pre"].items():
        for it in items:
            pre[it["item_id"]] = it
    spans = []
    for sec, v in manifest["sections"].items():
        groups = [(sec, v.get("items") or [])]
        for sb, sv in (v.get("subblocks") or {}).items():
            groups.append((sb, sv.get("items") or []))
        for s, items in groups:
            for it in items:
                src = it.get("source") or {}
                p = pre.get(it["item_id"], {})
                text = p.get("text") or ""
                ls, le = src.get("line_start"), src.get("line_end")
                level = "CONTENT"
                rendered = None
                if s == "A" and src.get("path") and src.get("commit"):
                    r = sh(["git", "show", f"{src['commit']}:{src['path']}"], cwd=REPO)
                    if r.returncode == 0:
                        full = r.stdout.splitlines(keepends=True)
                        l1 = ls or 1
                        l2 = le or len(full)
                        body = "".join(full[l1 - 1:l2])
                        shown = body[:4000]
                        n = shown.count("\n") + (0 if shown.endswith("\n") else 1)
                        rendered = [l1, l1 + n - 1]
                        if len(body) > 4000:
                            level = "TRUNCATED"
                elif it.get("route") == "semantic" or not text.strip():
                    level = "POINTER"
                elif it["unit"]["kind"] == "symbol":
                    level = "POINTER"
                elif it["unit"]["kind"] == "occurrence":
                    level = "LINE"
                spans.append({"section": s, "item_id": it["item_id"], "unit_id": it["unit"]["id"],
                              "unit_kind": it["unit"]["kind"], "route": it.get("route"),
                              "delivery": it.get("delivery"), "path": src.get("path"), "commit": src.get("commit"),
                              "lines": [ls, le] if ls is not None else None, "rendered": rendered, "level": level,
                              "text": text})
    return spans


def pre_budget_spans(capture):
    out = []
    post = set(i for ids in capture["post"].values() for i in ids)
    for sec, items in capture["pre"].items():
        for it in items:
            out.append({"section": sec, "item_id": it["item_id"], "unit_id": it["unit_id"],
                        "unit_kind": it["unit_kind"], "path": it.get("path"), "commit": it.get("commit"),
                        "lines": [it["line_start"], it["line_end"]] if it.get("line_start") is not None else None,
                        "kept": it["item_id"] in post, "text": it.get("text") or ""})
    return out


def span_matches_anchor(sp, a, want_content=False):
    if a.get("record_id") and sp.get("unit_id") == a["record_id"] and not want_content:
        return True
    if not same_file(a.get("commit"), a.get("path"), sp.get("commit"), sp.get("path")):
        return False
    al = a.get("lines")
    if not al:
        return True
    if a.get("symbol") and sp.get("unit_kind") == "symbol" and sp.get("text", "").split(" [")[0].endswith(
            a["symbol"].split("::")[-1]):
        return True
    rng = sp.get("rendered") if want_content and sp.get("rendered") else sp.get("lines")
    if rng is None:
        # whole-file item: citable only by the lenient whole-document rule (GD-8); content if rendered covers it
        return bool(want_content and sp.get("rendered") and substantive(al, sp["rendered"]))
    return substantive(al, rng) if want_content else overlap(al, rng)


# ------------------------------------------------------------------------------------------------ agent outputs

def output_spans(qdir, conn):
    spans = []
    b2p = {}

    def path_of_blob(b):
        if b not in b2p:
            row = conn.execute("SELECT path, commit_id FROM occurrence WHERE blob_id=? LIMIT 1", (b,)).fetchone()
            b2p[b] = row
        return b2p[b]

    for f in sorted(os.listdir(qdir)):
        if not f.endswith(".json"):
            continue
        try:
            d = json.load(open(os.path.join(qdir, f)))
        except Exception:
            continue
        if "hits" in d and "query" in d and isinstance(d.get("hits"), list) and d["hits"] and "line" in d["hits"][0]:
            for h in d["hits"]:
                spans.append({"file": f, "path": h["path"], "commit": d.get("commit"), "lines": [h["line"], h["line"]],
                              "level": "LINE", "text": h.get("text") or ""})
        elif "text" in d and "path" in d and "line_start" in d:
            spans.append({"file": f, "path": d["path"], "commit": d["commit"],
                          "lines": [d["line_start"], d["line_end"]], "level": "CONTENT", "text": d.get("text") or ""})
        elif "hits_by_route" in d:
            for rn, hits in d["hits_by_route"].items():
                for h in hits:
                    for o in h.get("occurrences") or []:
                        spans.append({"file": f, "path": o["path"], "commit": o["commit"],
                                      "lines": [o.get("line_start"), o.get("line_end")],
                                      "level": "CONTENT" if h.get("text") else "POINTER", "text": h.get("text") or ""})
        elif "value" in d and "path" in d:
            spans.append({"file": f, "path": d["path"], "commit": d["commit"], "lines": [d["line_start"], d["line_end"]],
                          "level": "CONTENT", "text": json.dumps(d["value"])})
        else:
            edges = []
            for st in (d.get("stages") or {}).values():
                edges += st.get("hops") or []
            for e in d.get("entries") or []:
                if e.get("edge"):
                    edges.append(e["edge"])
            edges += d.get("code") or []
            for e in edges:
                occ = e.get("evidence_occurrence") or ""
                line = e.get("evidence_line")
                if "@" in occ:
                    p, _, rest = occ.partition("@")
                    c = rest.split(":", 1)[0]
                elif ":" in occ:
                    b, _, ln = occ.partition(":")
                    row = path_of_blob(b)
                    if not row:
                        continue
                    p, c = row
                    line = int(ln) if ln.isdigit() else line
                else:
                    continue
                if line:
                    spans.append({"file": f, "path": p, "commit": c, "lines": [line, line], "level": "POINTER",
                                  "text": json.dumps(e)})
    return spans


# ------------------------------------------------------------------------------------------------ answers

def answer_citations(ans):
    cits = list(ans.get("citations") or [])
    for st in ans.get("stages") or []:
        cits += st.get("citations") or []
    for blk in ("evidence_for", "evidence_against"):
        for row in ans.get(blk) or []:
            cits += row.get("citations") or []
    for k in ("shared_points", "differing_points"):
        cits += ans.get(k) or []
    return cits


def cit_span(c, items):
    if isinstance(c, str):
        row = items.get(c)
        if row is None:
            return None
        src = row.get("source") or {}
        return {"path": src.get("path"), "commit": src.get("commit"),
                "lines": [src["line_start"], src["line_end"]] if src.get("line_start") is not None else None,
                "unit_id": row["unit"]["id"], "unit_kind": row["unit"]["kind"], "text": ""}
    if isinstance(c, dict) and "exact" in c:
        e = c["exact"] or {}
        return {"path": e.get("path"), "commit": e.get("commit"), "lines": e.get("lines")}
    return None


# ------------------------------------------------------------------------------------------------ store probes

def store_facts(conn, a):
    b = blob(a.get("commit"), a.get("path"))
    out = {"blob_known": False, "corpus_effect": None, "lexical_indexed": False, "chunk_covers": False,
           "vector_covers": False, "code_parsed": False, "code_symbol": False, "record_def": False,
           "in_view_blob": False}
    if b:
        row = conn.execute("SELECT corpus_effect FROM blob WHERE blob_id=?", (b,)).fetchone()
        out["blob_known"] = row is not None
        out["corpus_effect"] = row[0] if row else None
        out["lexical_indexed"] = conn.execute("SELECT 1 FROM lexical_indexed_blob WHERE blob_id=?", (b,)).fetchone() is not None
        out["in_view_blob"] = conn.execute("SELECT 1 FROM occurrence WHERE blob_id=? LIMIT 1", (b,)).fetchone() is not None
        al = a.get("lines")
        if al:
            ch = conn.execute("SELECT chunk_id FROM chunk WHERE blob_id=? AND start_line<=? AND end_line>=?",
                              (b, al[1] + TOL, al[0] - TOL)).fetchall()
            out["chunk_covers"] = bool(ch)
            if ch:
                q = ",".join("?" * len(ch))
                out["vector_covers"] = conn.execute(f"SELECT 1 FROM vector WHERE chunk_id IN ({q}) LIMIT 1",
                                                    [c[0] for c in ch]).fetchone() is not None
        out["code_parsed"] = conn.execute("SELECT 1 FROM code_blob WHERE blob_id=?", (b,)).fetchone() is not None
        if a.get("symbol"):
            nm = a["symbol"].split("::")[-1]
            out["code_symbol"] = conn.execute("SELECT 1 FROM code_symbol WHERE blob_id=? AND name=?",
                                              (b, nm)).fetchone() is not None
    if a.get("record_id"):
        out["record_def"] = conn.execute("SELECT 1 FROM record_def WHERE id=?", (a["record_id"],)).fetchone() is not None
    return out


def chunk_hit_matches(conn, chunk_id, a):
    row = conn.execute("SELECT blob_id, start_line, end_line FROM chunk WHERE chunk_id=?", (chunk_id,)).fetchone()
    if not row:
        return False
    b = blob(a.get("commit"), a.get("path"))
    if not b or row[0] != b:
        return False
    al = a.get("lines")
    return (not al) or overlap(al, [row[1], row[2]])


_lex_cache, _sem_cache = {}, {}


def lexical_rank(conn, text, a, exclude):
    from govbridge.lexical import query as lq
    from govbridge.route.real_routes import _safe_fts_query
    if text not in _lex_cache:
        res = lq.query(_safe_fts_query(text), k=K_PROBE, exclude=exclude, record_telemetry=False)
        _lex_cache[text] = [(h["item_id"]) for h in res["hits"]]
    for i, cid in enumerate(_lex_cache[text], start=1):
        if chunk_hit_matches(conn, cid, a):
            return i
    return None


def semantic_rank(conn, text, a, exclude):
    from govbridge.semantic import search as ss
    from govbridge.core import pathrules
    if text not in _sem_cache:
        res = ss.search(text, k=K_PROBE)
        ids = []
        for r in res["results"]:
            occ = r.get("occurrence")
            if occ and exclude and pathrules.any_glob_match(occ["path"], exclude) is not None:
                continue
            ids.append(r["id"])
        _sem_cache[text] = ids
    for i, cid in enumerate(_sem_cache[text], start=1):
        if chunk_hit_matches(conn, cid, a):
            return i
    return None


def scoped_rank(conn, text, a):
    """Rank of the anchor's chunk among the chunks of the anchor's OWN document, for the public query text: what a
    section-level retrieval inside an already-known document (e.g. a truncated mandatory input) would return."""
    from govbridge.route.real_routes import _safe_fts_query
    b = blob(a.get("commit"), a.get("path"))
    if not b or not a.get("lines"):
        return None, 0
    rows = conn.execute("SELECT chunk_id, start_line, end_line, bm25(lexical_fts) s FROM lexical_fts "
                        "WHERE lexical_fts MATCH ? AND blob_id=? ORDER BY s ASC", (_safe_fts_query(text), b)).fetchall()
    n = conn.execute("SELECT count(*) FROM chunk WHERE blob_id=?", (b,)).fetchone()[0]
    for i, (cid, s1, s2, _s) in enumerate(rows, start=1):
        if overlap(a["lines"], [s1, s2]):
            return i, n
    return None, n


def code_one_hop(conn, a, packet_symbol_names):
    """Is the anchor symbol one CALLS/TESTS hop from a symbol the compile already surfaced?"""
    if not a.get("symbol"):
        return None
    b = blob(a.get("commit"), a.get("path"))
    if not b:
        return None
    nm = a["symbol"].split("::")[-1]
    rows = conn.execute("SELECT symbol_id FROM code_symbol WHERE blob_id=? AND name=?", (b, nm)).fetchall()
    if not rows:
        return None
    ids = [r[0] for r in rows]
    q = ",".join("?" * len(ids))
    callee_names = {r[0] for r in conn.execute(
        f"SELECT callee_name FROM code_call_site WHERE caller_symbol IN ({q})", ids).fetchall()}
    if callee_names & packet_symbol_names:
        return "anchor_calls_packet_symbol"
    caller_ids = [r[0] for r in conn.execute("SELECT DISTINCT caller_symbol FROM code_call_site WHERE callee_name=?",
                                             (nm,)).fetchall() if r[0]]
    if caller_ids:
        q = ",".join("?" * len(caller_ids))
        names = {r[0] for r in conn.execute(f"SELECT name FROM code_symbol WHERE symbol_id IN ({q})", caller_ids)}
        if names & packet_symbol_names:
            return "packet_symbol_calls_anchor"
    return False


def symbol_span(conn, a):
    """The code store's own (start, end) for the anchor's symbol in the anchor's blob, or None."""
    if not a.get("symbol"):
        return None
    b = blob(a.get("commit"), a.get("path"))
    if not b:
        return None
    nm = a["symbol"].split("::")[-1]
    row = conn.execute("SELECT min(start_line), max(end_line) FROM code_symbol WHERE blob_id=? AND name=?",
                       (b, nm)).fetchone()
    return [row[0], row[1]] if row and row[0] is not None else None


def callsite_hop(conn, a, discovered):
    """For a code anchor WITHOUT a symbol: a call site inside the anchor window whose callee is a function defined in
    the same file and whose name was already discovered (packet text or agent outputs) -- i.e. `callers <name>` of an
    identifier in hand would surface the window."""
    if a.get("symbol") or a.get("kind") not in ("code", "test") or not a.get("lines"):
        return None
    b = blob(a.get("commit"), a.get("path"))
    if not b:
        return None
    local = {r[0] for r in conn.execute("SELECT name FROM code_symbol WHERE blob_id=?", (b,)).fetchall()}
    rows = conn.execute("SELECT callee_name FROM code_call_site WHERE blob_id=? AND line BETWEEN ? AND ?",
                        (b, a["lines"][0], a["lines"][1])).fetchall()
    for (callee,) in rows:
        if callee in local and len(callee) >= 6 and callee in discovered:
            return "callers_of_discovered_local_fn"
    return False


PRIMARY_ORDER = ["B-BUDGET-DROP", "B-TRUNCATED-MANDATORY", "B-BYREF-DIR-UNEXPANDED", "B-QUERY-NOT-RUN",
                 "B-FOLLOWUP-ID", "B-FOLLOWUP-CALLERS", "B-TOPK", "B-SCOPED-SECTION"]


def classify(rec, compiled_query_ids):
    """Deterministic class + cause code for one missed [D] item (see CAUSE_ANALYSIS.md section 2 for the rules)."""
    st = rec["store"]
    indexed = st["chunk_covers"] or st["code_symbol"] or st["record_def"]
    if rec["doc_level_citation_this_answer"]:
        return "GRADER_DEFECT", "GD-8", []
    if rec["symbol_body_citation_this_answer"]:
        return "GRADER_DEFECT", "GD-10", []
    if rec["in_packet_citable"] or rec["in_packet_content"]:
        return "AGENT_BEHAVIOUR", "A-PACKET-NOT-CITED", []
    if rec["agent_outputs_content"] or (rec["agent_outputs_line"] and rec["kind"] in ("code", "test")):
        return "AGENT_BEHAVIOUR", "A-OUTPUT-NOT-CITED", []
    if rec["cited_in_other_answers"]:
        return "AGENT_BEHAVIOUR", "A-CITED-ELSEWHERE", []
    signals = []
    if indexed:
        if rec["compiler_candidate_budget_dropped"]:
            signals.append("B-BUDGET-DROP")
        if rec["doc_in_packet_truncated_before_anchor"]:
            signals.append("B-TRUNCATED-MANDATORY")
        if rec["in_byref_mandatory_dir"]:
            signals.append("B-BYREF-DIR-UNEXPANDED")
        best = min([r for r in (rec["probe_lexical_rank_k200"], rec["probe_semantic_rank_k200"]) if r] or [10 ** 9])
        if rec["query_id"] not in compiled_query_ids and best <= 100:
            signals.append("B-QUERY-NOT-RUN")
        if (rec["identifier_in_packet_text"] or rec["identifier_in_agent_outputs"]) and (
                st["record_def"] or st["code_symbol"]):
            signals.append("B-FOLLOWUP-ID")
        if rec["path_parts_in_agent_outputs"] and not rec["path_in_packet_text"] and rec["kind"] in ("code", "contract"):
            signals.append("B-FOLLOWUP-ID")
        if rec["probe_code_one_hop"] or rec["probe_callsite_hop"]:
            signals.append("B-FOLLOWUP-CALLERS")
        if rec["query_id"] in compiled_query_ids and 8 < best <= 100:
            signals.append("B-TOPK")
        if rec["probe_scoped_doc_rank"] and rec["probe_scoped_doc_rank"] <= 5 and rec["path_in_packet_text"]:
            signals.append("B-SCOPED-SECTION")
    signals = sorted(set(signals), key=PRIMARY_ORDER.index)
    if signals:
        primary = signals[0]
        return "BRIDGE_NOT_IN_PACKET_BUT_RETRIEVABLE", primary, signals
    if not st["blob_known"] or not indexed:
        return "BRIDGE_NOT_RETRIEVABLE", "N-NOT-INDEXED", []
    return "BRIDGE_NOT_RETRIEVABLE", "N-NO-ROUTE", []


# ------------------------------------------------------------------------------------------------ main

def main():
    global REPO
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", required=True, help="recompile_capture.py output (pre-budget candidates)")
    ap.add_argument("--answers-normalised", required=True, help="the grader's lossless START-END normalised answers")
    ap.add_argument("--private-out", required=True)
    ap.add_argument("--public-out", required=True)
    args = ap.parse_args()
    REPO = repo_root()
    D = os.path.join(REPO, DOM)
    sys.path.insert(0, D)

    oracle = yaml.safe_load(quarantined("DEMONSTRATION/oracle/oracle.yaml"))
    grade = yaml.safe_load(quarantined("DEMONSTRATION/grading/run-1.yaml"))
    queries = yaml.safe_load(open(os.path.join(D, "DEMONSTRATION/run-1/task-inputs/demonstration-queries.yaml")))
    manifest = json.load(open(os.path.join(D, "DEMONSTRATION/run-1/packet/manifest.json")))
    task = yaml.safe_load(open(os.path.join(D, "DEMONSTRATION/run-1/packet/task_spec.yaml")))
    exclude = task.get("retrieval_exclusions") or []
    capture = json.load(open(args.capture))
    answers = json.load(open(args.answers_normalised))
    by_q = {a["query_id"]: a for a in answers["answers"]}
    items = {}
    for sec, v in manifest["sections"].items():
        for it in v.get("items") or []:
            items[it["item_id"]] = it
        for sb, sv in (v.get("subblocks") or {}).items():
            for it in sv.get("items") or []:
                items[it["item_id"]] = it

    from govbridge.core import store as storemod
    conn = storemod.open_db()

    pkt = packet_spans(manifest, capture)
    pre = pre_budget_spans(capture)
    outs = output_spans(os.path.join(D, "DEMONSTRATION/run-1/supplementary/queries"), conn)
    packet_md = open(os.path.join(D, "DEMONSTRATION/run-1/packet/packet.md"), encoding="utf-8").read()
    outputs_text = "\n".join(s["text"] for s in outs)
    packet_symbol_names = {(sp["text"].split(" [")[0].split(" ")[-1]).split("::")[-1]
                           for sp in pkt if sp["unit_kind"] == "symbol"}
    pre_symbol_names = {(sp["text"].split(" [")[0].split(" ")[-1]).split("::")[-1]
                        for sp in pre if sp["unit_kind"] == "symbol"}

    discovered = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]{5,}", packet_md + "\n" + outputs_text))
    byref_dirs = [sp["path"] for sp in pkt if sp["section"] == "A" and sp.get("path") and sp["path"].endswith("/")]
    compiled_query_ids = {r["id"] for rows in capture["queries_log"].values() for r in rows}
    qtext = {}
    for q in queries["queries"]:
        if q.get("text"):
            qtext[q["id"]] = q["text"]
        else:
            qtext[q["id"]] = f"{queries['query_classes'][q['class']]} Subject: {queries['subjects'][q['subject']]}"

    # ---- enumerate failed [D] items -> (key, query_id, anchor list, scope)
    todo = []
    G = grade["gates"]
    ochains = {c["query_id"]: c for c in oracle["chains"]}
    for ch in G["G4_chains"]["chains"]:
        for st in ch["stages"]:
            if st["grade"] != "REACHED" and not st["d_anchor_reached_design"]:
                osd = [s for s in ochains[ch["query_id"]]["stages"] if s["stage"] == st["stage"]][0]
                anc = osd["anchors"].get("any_of") or osd["anchors"].get("all_of") or []
                for i, a in enumerate(anc, start=1):
                    todo.append((f"G4.{ch['query_id']}.{st['stage']}.A{i}", ch["query_id"], a))
    oq = {q["query_id"]: q for q in oracle["queries"]}
    oc = {q["query_id"]: q for q in oracle["controls"]}

    def req_keys(prefix, qid, oentry, missed):
        for lbl in missed:
            pa = parse_label(lbl)
            idx = None
            for i, a in enumerate(oentry.get("required") or [], start=1):
                if isinstance(a, dict) and same_anchor(a, pa):
                    idx, anc = i, a
                    break
            if idx is None:
                raise SystemExit(f"cannot map missed item for {qid}")
            todo.append((f"{prefix}.{qid}.R{idx}", qid, anc))

    for q in G["G5_query_classes"]["per_query"]:
        if q["result"] == "FAIL":
            req_keys("G5", q["query_id"], oq[q["query_id"]], q["missed_required"])
    for q in G["G8_controls"]["per_query"]:
        if q["result"] == "FAIL":
            req_keys("G8", q["query_id"], oc[q["query_id"]], q["missed_required"])
    for q in G["G3_authority_classes"]["auth_queries_informational"]["per_query"]:
        if q["result"] == "FAIL":
            req_keys("G3i", q["query_id"], oq[q["query_id"]], q["missed_required"])
    for lbl in G["G6_f1_both_ways"]["missed_consumer_anchors"]:
        pa = parse_label(lbl)
        for i, a in enumerate(oracle["f1_both_ways"]["consumer_anchors"], start=1):
            if same_anchor(a, pa):
                todo.append((f"G6.R8-F1-BOTHWAYS.C{i}", "R8-F1-BOTHWAYS", a))

    lenient = {}
    for q in G["G5_query_classes"]["per_query"] + G["G8_controls"]["per_query"] + \
            G["G3_authority_classes"]["auth_queries_informational"]["per_query"]:
        lenient[q["query_id"]] = (q.get("recall"), q.get("recall_lenient_whole_doc"))

    private, public = [], []
    for key, qid, a in todo:
        this_cits = [cit_span(c, items) for c in answer_citations(by_q.get(qid, {}))]
        this_cits = [c for c in this_cits if c]
        other_cits = []
        for oqid, ans in by_q.items():
            if oqid == qid:
                continue
            for c in answer_citations(ans):
                s = cit_span(c, items)
                if s:
                    other_cits.append((oqid, s))
        # GD-8 lenient: a whole-document citation of the same (blob-identical) file in THIS answer
        doc_level_this = any(c.get("lines") in (None, []) and same_file(a.get("commit"), a.get("path"),
                                                                         c.get("commit"), c.get("path"))
                             for c in this_cits)
        # same symbol / same path cited in THIS answer at a commit whose blob differs (historical-commit anchors)
        same_path_other_blob_this = any(c.get("path") == a.get("path") and not same_file(
            a.get("commit"), a.get("path"), c.get("commit"), c.get("path")) and overlap(a.get("lines"), c.get("lines"), 400)
            for c in this_cits)
        cited_elsewhere = sorted({oqid for oqid, s in other_cits if span_matches_anchor(
            {**s, "unit_kind": s.get("unit_kind")}, a, True)})
        pk_cit = [sp for sp in pkt if span_matches_anchor(sp, a)]
        pk_con = [sp for sp in pkt if sp["level"] in ("CONTENT", "TRUNCATED") and span_matches_anchor(sp, a, True)]
        pk_trunc_doc = [sp for sp in pkt if sp["level"] == "TRUNCATED" and same_file(
            a.get("commit"), a.get("path"), sp.get("commit"), sp.get("path")) and not span_matches_anchor(sp, a, True)]
        pre_hit = [sp for sp in pre if span_matches_anchor(sp, a)]
        pre_dropped = [sp for sp in pre_hit if not sp["kept"]]
        out_con = [sp for sp in outs if sp["level"] == "CONTENT" and span_matches_anchor(sp, a, True)]
        out_line = [sp for sp in outs if sp["level"] == "LINE" and span_matches_anchor(sp, a)]
        out_ptr = [sp for sp in outs if sp["level"] == "POINTER" and span_matches_anchor(sp, a)]
        ident = a.get("record_id") or (a.get("symbol") or "").split("::")[-1] or None
        ident_in_packet = bool(ident and ident in packet_md)
        ident_in_outputs = bool(ident and ident in outputs_text)
        ident_in_answer = bool(ident and ident in json.dumps(by_q.get(qid, {})))
        path_in_packet = bool(a.get("path") and a["path"] in packet_md)
        parts = (a.get("path") or "").split("/")
        path_parts_in_outputs = len(parts) >= 2 and all(p_ in outputs_text for p_ in parts[-2:])
        sf = store_facts(conn, a)
        text = qtext[qid]
        lr = lexical_rank(conn, text, a, exclude)
        sr = semantic_rank(conn, text, a, exclude)
        scr, scn = scoped_rank(conn, text, a)
        hop = code_one_hop(conn, a, pre_symbol_names | packet_symbol_names)
        cs_hop = callsite_hop(conn, a, discovered)
        span = symbol_span(conn, a)
        sym_body = bool(span) and any(
            same_file(a.get("commit"), a.get("path"), c.get("commit"), c.get("path")) and c.get("lines")
            and overlap(span, c["lines"], 0) for c in this_cits)
        byref = any(a.get("path", "").startswith(d) for d in byref_dirs)
        rec = {
            "key": key, "query_id": qid, "kind": a.get("kind"),
            "ref_role": {"3c880d8": "product", "6e7a2a3": "records", "58219d5": "evidence",
                         "a7b4dbe": "records-bridge"}.get((a.get("commit") or "")[:7], "historical"),
            "in_packet_citable": bool(pk_cit), "in_packet_content": bool(pk_con),
            "in_packet_sections": sorted({sp["section"] for sp in pk_cit + pk_con}),
            "in_packet_levels": sorted({sp["level"] for sp in pk_cit + pk_con}),
            "doc_in_packet_truncated_before_anchor": bool(pk_trunc_doc),
            "compiler_candidate_pre_budget": bool(pre_hit), "compiler_candidate_budget_dropped": bool(pre_dropped)
            and not pk_cit,
            "agent_outputs_content": len({s["file"] for s in out_con}), "agent_outputs_line": len({s["file"] for s in out_line}),
            "agent_outputs_pointer": len({s["file"] for s in out_ptr}),
            "cited_in_other_answers": cited_elsewhere, "doc_level_citation_this_answer": doc_level_this,
            "same_path_other_blob_cited_this_answer": same_path_other_blob_this,
            "identifier_in_packet_text": ident_in_packet, "identifier_in_agent_outputs": ident_in_outputs,
            "identifier_in_this_answer": ident_in_answer, "path_in_packet_text": path_in_packet,
            "store": sf, "probe_lexical_rank_k200": lr, "probe_semantic_rank_k200": sr,
            "probe_scoped_doc_rank": scr, "probe_scoped_doc_chunks": scn, "probe_code_one_hop": hop,
            "query_recall_design_vs_lenient": lenient.get(qid),
            "symbol_body_citation_this_answer": sym_body, "probe_callsite_hop": cs_hop,
            "in_byref_mandatory_dir": byref, "path_parts_in_agent_outputs": path_parts_in_outputs,
        }
        cls, cause, signals = classify(rec, compiled_query_ids)
        rec.update({"class": cls, "cause": cause, "bridge_signals": signals})
        public.append(rec)
        private.append({**rec, "anchor": anchor_label(a),
                        "packet_items": [sp["item_id"] for sp in pk_cit],
                        "output_files": sorted({s["file"] for s in out_con + out_line + out_ptr})})
    json.dump(private, open(args.private_out, "w"), indent=1)
    json.dump(public, open(args.public_out, "w"), indent=1)
    print(json.dumps({"failed_items": len(public)}, indent=1))


if __name__ == "__main__":
    main()
