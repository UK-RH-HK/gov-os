import json, sys
d = json.load(sys.stdin)
if d.get("ok"):
    s = d["result"].get("separation", {})
    print("ACCEPTED | scanned=%d findings=%s" % (len(s.get("scanned", [])), s.get("findings")))
else:
    e = d["error"]
    fs = (e.get("details") or {}).get("findings") or (e.get("details") or {}).get("violations") or []
    txt = "; ".join("%s :: %s" % (x.get("at", ""), x.get("problem", "")) for x in fs[:3])
    print("%s | %d finding(s): %s" % (e["code"], len(fs), txt))
