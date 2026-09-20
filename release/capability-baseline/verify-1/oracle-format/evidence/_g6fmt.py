import json, sys
t = sys.stdin.read()
try:
    d = json.loads(t)
except Exception:
    print("UNPARSEABLE:", t[:200].replace("\n", " ")); raise SystemExit
if d.get("ok"):
    q = d["result"]["qualification"]
    h = d["result"]["health"]
    print("RECORDED | counts_as_qualification=%s purpose=%s posture=%s health=%s" % (
        q["counts_as_qualification"], q["oracle"]["purpose"], q["machine_posture"],
        h.get("state") or h.get("verdict") or h.get("status")))
else:
    print("%s | %s" % (d["error"]["code"], d["error"]["message"][:130].replace("\n", " ")))
