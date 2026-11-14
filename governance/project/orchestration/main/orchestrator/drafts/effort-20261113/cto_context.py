#!/usr/bin/env python3
"""The CTO main sessions' cost by token kind, and what the cache reads above a context cap cost (est. saving of a fresh session at the cap).
Usage numbers and timestamps only. Writes cto_context.json."""
import json, glob, os, collections, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("common", HERE + "/common.py"); C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
CTO = ["8ddb8b14-0dce-4faa-9cb0-7150fcce200d", "b40cba91-6c08-4f82-b30e-591a4b93fb70", "b2f0511f-891b-4874-8930-6d34ca5972ea", "f3886235-4854-4c91-9cf3-1a1dd009cb50"]
CAPS = (200000, 300000)
res = {}
for wn, w in C.WINDOWS.items():
    comp = collections.Counter(); ctxs = []; above = {c: 0.0 for c in CAPS}; n = 0
    for sid in CTO:
        best = {}
        for l in open(f"{C.PROJ}/{sid}.jsonl", errors="replace"):
            if '"usage"' not in l: continue
            try: d = json.loads(l)
            except ValueError: continue
            m = d.get("message")
            if not isinstance(m, dict) or "usage" not in m or C.tier(m.get("model")) is None: continue
            t = C.epoch(d.get("timestamp"))
            if t is None or not (w[0] <= t <= w[1]): continue
            key = m.get("id") or d.get("requestId") or d.get("uuid"); u = m["usage"]
            old = best.get(key)
            if old is None or (u.get("output_tokens") or 0) >= (old[0].get("output_tokens") or 0): best[key] = (u, m.get("model"))
        for u, model in best.values():
            p = C.PRICE["opus"] if C.tier(model) == "opus" else C.PRICE["sonnet"]
            cc = u.get("cache_creation") or {}
            w5 = cc.get("ephemeral_5m_input_tokens"); w1 = cc.get("ephemeral_1h_input_tokens")
            if w5 is None and w1 is None: w5, w1 = (u.get("cache_creation_input_tokens") or 0), 0
            i = u.get("input_tokens") or 0; cr = u.get("cache_read_input_tokens") or 0; o = u.get("output_tokens") or 0
            comp["cache_read"] += cr * p[3] / 1e6; comp["cache_write"] += ((w5 or 0) * p[1] + (w1 or 0) * p[2]) / 1e6
            comp["output"] += o * p[4] / 1e6; comp["input"] += i * p[0] / 1e6
            ctx = i + cr + (w5 or 0) + (w1 or 0); ctxs.append(ctx); n += 1
            for c in CAPS: above[c] += max(0, cr - c) * p[3] / 1e6   # cache reads beyond the cap that a fresh session would not re-read
    ctxs.sort()
    res[wn] = dict(turns=n, cost_by_kind={k: round(v, 2) for k, v in comp.items()}, total=round(sum(comp.values()), 2),
                   ctx_median=ctxs[len(ctxs) // 2] if ctxs else None, ctx_p90=ctxs[int(.9 * len(ctxs))] if ctxs else None,
                   cache_read_above_cap_usd={str(c): round(v, 2) for c, v in above.items()})
json.dump(res, open(HERE + "/cto_context.json", "w"), indent=1)
print(json.dumps(res, indent=1))
