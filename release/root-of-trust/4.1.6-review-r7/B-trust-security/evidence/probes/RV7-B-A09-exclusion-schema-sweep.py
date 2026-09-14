#!/usr/bin/env python3
"""RV7-B-A09 (AR-0020): exclusion reachability sweep over the certified schema set (`schemas/*.json`, withdrawn schemas excluded).
For every schema: excluded-mode identifiers appearing anywhere (descriptions included), objects with properties that do not set
additionalProperties false (an excluded field could validate), and external $refs (a certified schema referring to a withdrawn one).
Environment: PACK. Output: JSON on stdout."""
import json, os, re, sys
PACK = os.environ["PACK"]
SD = os.path.join(PACK, "schemas")
WORDS = ("witness", "channel_quorum", "platform_sig", "code_signature", "eligible_until", "op7_mode", "op6_mode", "mode_b", "fresh_certified", "submitter",
         "first-contact-manifest", "freshness", "revoked_self_scope", "max_anchor_age")


def walk(o, path=""):
    out = []
    if isinstance(o, dict):
        if o.get("type") == "object" and "properties" in o and o.get("additionalProperties") is not False:
            out.append({"path": path or "/", "additionalProperties": o.get("additionalProperties", "<absent>")})
        for k, v in o.items():
            out += walk(v, path + "/" + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            out += walk(v, path + "/%d" % i)
    return out


def desc_only(txt_obj, word):
    """True when every occurrence of `word` is inside a description or title string."""
    hits = []
    def rec(o, key=None):
        if isinstance(o, dict):
            for k, v in o.items():
                rec(v, k)
        elif isinstance(o, list):
            for v in o:
                rec(v, key)
        elif isinstance(o, str) and word in o:
            hits.append(key)
        if isinstance(o, dict):
            for k in o:
                if word in k:
                    hits.append("<property-name>")
    rec(txt_obj)
    return all(h in ("description", "title") for h in hits), hits


rows = {}
for f in sorted(os.listdir(SD)):
    if not f.endswith(".json"):
        continue
    s = json.load(open(os.path.join(SD, f)))
    txt = json.dumps(s)
    words = {}
    for w in WORDS:
        if w in txt:
            only, where = desc_only(s, w)
            words[w] = {"only_in_description_or_title": only, "keys": sorted(set(map(str, where)))}
    rows[f] = {"excluded_identifiers": words, "open_objects": walk(s), "external_refs": sorted(set(r for r in re.findall(r'"\$ref": "([^"]+)"', txt) if not r.startswith("#")))}
out = {"probe": "RV7-B-A09 exclusion schema sweep (AR-0020)", "schemas": len(rows), "rows": rows,
       "withdrawn": sorted(os.listdir(os.path.join(SD, "withdrawn-non-production")))}
out["verdicts"] = {"no_excluded_identifier_outside_descriptions": all(v["only_in_description_or_title"] for r in rows.values() for v in r["excluded_identifiers"].values()),
                   "no_external_refs": all(not r["external_refs"] for r in rows.values()),
                   "open_objects": {f: r["open_objects"] for f, r in rows.items() if r["open_objects"]}}
print(json.dumps(out, indent=1, sort_keys=True))
