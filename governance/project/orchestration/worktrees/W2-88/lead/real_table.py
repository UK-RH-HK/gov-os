import json, os, glob
base = "/home/usain/gov-os-runs/W2-88"
d = json.load(open(base + "/proof-a-real-results.json"))
print("keys:", list(d))
for f in sorted(glob.glob(base + "/proving-ground-real/*-result.json")):
    r = json.load(open(f))
    d.setdefault(r["repository"], r)
    print("file", f, os.path.getmtime(f))
for name, r in d.items():
    if not isinstance(r, dict) or "stores" not in r:
        print(name, "NO STORES", json.dumps(r)[:600])
        continue
    s = r["stores"]; sc = r["scale"]; m = r["measure"]; st = r["standard"]
    print(f"| {name} | {r['built_commit']} / {r['a9_commit']} | {r['size']['files']} files, {r['size']['bytes']:,} B | "
          f"{r['a9_seconds']} s | lexical {s['lexical']['indexed']}/{s['lexical']['judged']}, {s['lexical']['chunks']} chunks; "
          f"vectors {s['vectors']['indexed']}/{s['vectors']['judged']}, {s['vectors']['vectors']} vectors, {s['vectors']['seconds']} s; "
          f"code graph {s['codegraph']['nodes']} nodes, {s['codegraph']['edges']} edges, {s['codegraph']['seconds']} s; "
          f"peak {s['lexical']['peak_rss_bytes']:,} B | lexical {sc['routes'].get('lexical')} ms, vector scan {sc['vector_scan_ms']} ms "
          f"(budget {sc['budget_ms']} ms), retrieve {sc['routes'].get('retrieve')} ms; proposal {r['scale_proposal']} | "
          f"{m['questions']} q: right e2e {m['right_e2e']} %, wrong {m['wrong_claims']}, hit@5 {m['hit_at_5']} % ({len(m['residuals'])} residuals) | "
          f"departures {len(st['departures'])}; pin {st['gov_pin']}; embedder {st['embedder']['model']}; reranker {st['reranker']} ({st['reranker_service']}) |")
    print("   digests", {k: (v[:12] if isinstance(v, str) else v) for k, v in r["digests"].items()},
          "refused", r["refused_reasons"], "residuals", [x["cause"] for x in m["residuals"]])
