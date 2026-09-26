#!/usr/bin/env python3
"""BR-AR-0016: oracle-free measurements of the run-1 packet, the compile, the saved query outputs and the store.

Nothing here reads the oracle or the grade. Inputs: the committed run-1 artefacts, the recompile capture
(recompile_capture.py), the bridge state's mandatory-input declarations and a READ-ONLY copy of the demonstration
store (GOVBRIDGE_STORE). Output: one JSON document on stdout."""
from __future__ import annotations

import collections
import json
import os
import re
import sqlite3
import subprocess
import sys

import yaml

DOM = "release/orchestration/phase-2-context-bridge"


def sh(*a):
    return subprocess.run(list(a), capture_output=True, text=True)


def main():
    capture_path, store_db = sys.argv[1], sys.argv[2]
    root = sh("git", "rev-parse", "--show-toplevel").stdout.strip()
    D = os.path.join(root, DOM)
    run1 = os.path.join(D, "DEMONSTRATION/run-1")
    man = json.load(open(os.path.join(run1, "packet/manifest.json")))
    cap = json.load(open(capture_path))
    state = yaml.safe_load(open(os.path.join(D, "ORCHESTRATOR_STATE.yaml")))
    out = {}

    # 1. mandatory inputs (section A): rendered vs source, declared selectors
    decl = {i["id"]: i for i in (state.get("mandatory_bridge_inputs") or {}).get("items", [])} \
        if isinstance(state.get("mandatory_bridge_inputs"), dict) else {}
    rows, total_src, total_rendered = [], 0, 0
    pre_text = {i["item_id"]: i.get("text") or "" for i in cap["pre"]["A"]}
    for it in man["sections"]["A"]["items"]:
        src = it["source"]
        r = sh("git", "cat-file", "-s", f"{src['commit']}:{src['path']}")
        full = int(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip().isdigit() else None
        body = sh("git", "show", f"{src['commit']}:{src['path']}").stdout if full else ""
        lines_total = body.count("\n")
        if src.get("line_start"):
            sel = "".join(body.splitlines(keepends=True)[src["line_start"] - 1:src["line_end"]])
        else:
            sel = body
        rendered = pre_text.get(it["item_id"], "")
        d = decl.get(it["unit"]["id"], {})
        selectors = [k for k in ("entries", "keys") if k in d] + (["paths(multi)"] if len(d.get("paths") or []) > 1 else [])
        rows.append({"id": it["unit"]["id"], "class": it.get("authority_class"), "lifecycle": it.get("lifecycle"),
                     "declared_range": bool(src.get("line_start")), "declared_selectors": selectors,
                     "source_bytes": len(sel.encode()), "rendered_bytes": len(rendered.encode()),
                     "rendered_fraction": round(len(rendered.encode()) / max(len(sel.encode()), 1), 4),
                     "truncated": len(sel.encode()) > len(rendered.encode()) + 64, "file_lines": lines_total})
        total_src += len(sel.encode())
        total_rendered += len(rendered.encode())
    out["section_a"] = {"items": rows, "n_items": len(rows), "n_truncated": sum(r["truncated"] for r in rows),
                        "sum_source_bytes": total_src, "sum_rendered_bytes": total_rendered,
                        "synthesis_profile_total_bytes": 360 * 1024,
                        "truncation_marker_in_packet": "truncated" in open(os.path.join(run1, "packet/packet.md")).read().lower()}

    # 2. rendered bytes per section; delivered item-content bytes by (section, route, kind)
    p = open(os.path.join(run1, "packet/packet.md"), encoding="utf-8").read()
    idx = [(m.start(), m.group(1)) for m in re.finditer(r"^## ([A-J])\. ", p, re.M)] + [(len(p), "END")]
    out["packet_md"] = {"bytes": len(p.encode()),
                        "rendered_bytes_by_section": {n: len(p[s:e].encode()) for (s, n), (e, _) in zip(idx, idx[1:])}}
    content = collections.Counter()
    count = collections.Counter()
    for sec, v in man["sections"].items():
        groups = [(sec, v.get("items") or [])] + [(sb, sv["items"]) for sb, sv in (v.get("subblocks") or {}).items()]
        for s, items in groups:
            for it in items:
                k = f"{s}|{it['route']}|{it['unit']['kind']}"
                content[k] += it["bytes"]
                count[k] += 1
    out["item_content"] = {k: {"items": count[k], "content_bytes": content[k]} for k in sorted(count)}
    b = open(os.path.join(run1, "bootstrap.md"), encoding="utf-8").read()
    out["bootstrap"] = {"bytes": len(b.encode()), "contains_whole_packet_body": p[200:] in b}

    # 3. which public queries the compiler executed
    qdoc = yaml.safe_load(open(os.path.join(run1, "task-inputs/demonstration-queries.yaml")))
    executed = sorted({r["id"] for rows_ in cap["queries_log"].values() for r in rows_})
    out["compiler_queries"] = {"public_queries": len(qdoc["queries"]),
                               "public_queries_without_text": sum(1 for q in qdoc["queries"] if not q.get("text")),
                               "executed_ids": executed,
                               "k_values": sorted({r.get("k") for rows_ in cap["queries_log"].values() for r in rows_
                                                   if r.get("k")})}

    # 4. candidates before budget, by tier/type/resolution, kept or dropped
    post = set(i for ids in cap["post"].values() for i in ids)
    for sec in ("G", "H"):
        c = collections.Counter()
        for it in cap["pre"][sec]:
            typ = it["unit_id"].split(":")[0] if it["unit_kind"] == "occurrence" else it["unit_kind"]
            is_test = bool(it.get("path") and re.search(r"(^|/)tests?/", it["path"]))
            c[f"{it.get('tier')}|{it['route']}|{typ}|{it.get('resolution')}|{'test' if is_test else 'src'}|"
              f"{'kept' if it['item_id'] in post else 'dropped'}"] += 1
        out[f"candidates_{sec}"] = {"pre_budget": len(cap["pre"][sec]), "kept": len(cap["post"][sec]),
                                    "by_tier_route_type_resolution_surface_fate": dict(sorted(c.items()))}

    # 5. fan-out: T1 seed symbols whose call-site count exceeds the profile's max_callers
    conn = sqlite3.connect(f"file:{store_db}?mode=ro", uri=True)
    budgets = yaml.safe_load(open(os.path.join(D, "config/budgets.yaml")))
    cap_callers = budgets["profiles"]["synthesis"]["g_fanout"]["max_callers"]
    t1 = [it for it in cap["pre"]["G"] if it.get("tier") == "T1" and it["unit_kind"] == "symbol"]
    counts = []
    for it in t1:
        nm = it["text"].split(" [")[0].split(" ")[-1].split("::")[-1]
        counts.append(conn.execute("SELECT count(*) FROM code_call_site WHERE callee_name=?", (nm,)).fetchone()[0])
    out["fanout"] = {"t1_symbols": len(t1), "max_callers_synthesis": cap_callers,
                     "t1_symbols_with_more_call_sites_than_cap": sum(1 for n in counts if n > cap_callers),
                     "call_sites_beyond_cap_total": sum(max(0, n - cap_callers) for n in counts),
                     "continuation_supported": False}

    # 6. saved query outputs: bytes by command, text payload vs metadata vs per-hit occurrence fan-out
    qd = os.path.join(run1, "supplementary/queries")
    by = collections.Counter()
    payload = occ = total = 0
    occ_rows = []
    for f in sorted(os.listdir(qd)):
        raw = open(os.path.join(qd, f), encoding="utf-8").read()
        total += len(raw.encode())
        kind = "index" if f.endswith(".md") else f.split("-", 1)[1][:-5]
        try:
            d = json.loads(raw) if f.endswith(".json") else None
        except Exception:
            d = None
        if isinstance(d, dict) and kind == "exact":
            kind = "exact-grep" if "hits" in d else ("exact-show" if "text" in d else "exact-error")
        by[kind] += len(raw.encode())
        if not isinstance(d, dict):
            continue
        if "text" in d and isinstance(d["text"], str):
            payload += len(d["text"].encode())
        for h in d.get("hits") or []:
            payload += len((h.get("text") or "").encode())
        for hs in (d.get("hits_by_route") or {}).values():
            for h in hs:
                payload += len((h.get("text") or "").encode())
                occ += len(json.dumps(h.get("occurrences")).encode())
                occ_rows.append(len(h.get("occurrences") or []))
    out["saved_query_outputs"] = {"files": len(os.listdir(qd)), "bytes_total": total, "bytes_by_command": dict(by),
                                  "text_payload_bytes": payload, "search_hit_occurrence_metadata_bytes": occ,
                                  "search_hits": len(occ_rows),
                                  "max_occurrences_per_search_hit": max(occ_rows) if occ_rows else 0,
                                  "has_manifest_or_hash": False}

    # 7. record addressability inside YAML state files (generic): top-level keys vs record_def rows
    rec = {}
    for path in ("release/orchestration/phase-2/ORCHESTRATOR_STATE.yaml",
                 "release/orchestration/phase-1/ORCHESTRATOR_STATE.yaml",
                 f"{DOM}/ORCHESTRATOR_STATE.yaml"):
        commit = man["view"][0]["commit"]
        txt = sh("git", "show", f"{commit}:{path}").stdout
        try:
            doc = yaml.safe_load(txt) or {}
        except Exception:
            doc = {}
        top = len(doc) if isinstance(doc, dict) else 0
        ids = sum(1 for v in (doc.values() if isinstance(doc, dict) else []) if isinstance(v, list)
                  for x in v if isinstance(x, dict) and "id" in x)
        n_def = conn.execute("SELECT count(*) FROM record_def WHERE path=?", (path,)).fetchone()[0]
        rec[path] = {"top_level_keys": top, "list_items_with_id": ids, "record_def_rows": n_def}
    out["state_record_addressability"] = rec

    # 8. places where retrieval_exclusions are not passed to a route (static)
    pk = open(os.path.join(D, "govbridge/compile/packet.py")).read().splitlines()
    out["routes_called_without_exclusions"] = [
        {"file": "govbridge/compile/packet.py", "line": i + 1, "code": l.strip()[:120]}
        for i, l in enumerate(pk) if "routes.run(" in l and "exclude" not in l and "retrieval_exclusions" not in
        "".join(pk[i:i + 3])]
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
