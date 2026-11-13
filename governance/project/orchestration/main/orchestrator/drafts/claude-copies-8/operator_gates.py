"""Runs the operator's own read-only gate functions on a bundle (no queue, no log, no run): check_act (G1),
validate_manifest, path_rule (G1), the manifest's file hashes and act_class (G6), with the install's settings.

    python3 -I operator_gates.py <bundle dir> <act id>
"""
import hashlib, json, os, sys

INSTALL = os.path.expanduser("~/gov-os-operator/install")
sys.path.insert(0, INSTALL)
import opcommon as oc          # noqa: E402
import operator_run as orun    # noqa: E402
import act_class               # noqa: E402

bundle, act = sys.argv[1], sys.argv[2]
raw = open(os.path.join(bundle, "manifest.json"), "rb").read()
m = json.loads(raw)
s = oc.load_settings()
out = {"manifest_sha256": hashlib.sha256(raw).hexdigest()}
for name, fn in (("check_act", lambda: orun.check_act(m, act)), ("validate_manifest", lambda: orun.validate_manifest(m)),
                 ("path_rule", lambda: orun.path_rule(bundle, m, s))):
    try:
        fn()
        out[name] = "pass"
    except Exception as e:      # Refused or ValueError: the gate's own text
        out[name] = f"refused: {getattr(e, 'reason', e)}"
mism = [p for p, h in m["files"].items()
        if not os.path.isfile(os.path.join(bundle, p)) or hashlib.sha256(open(os.path.join(bundle, p), "rb").read()).hexdigest() != h]
on_disk = sorted(os.path.relpath(os.path.join(d, f), bundle) for d, _, fs in os.walk(bundle) for f in fs)
unnamed = [p for p in on_disk if p not in m["files"] and p not in ("manifest.json", "review.md")]
out["hash_mismatches"], out["unnamed_on_disk"] = mism, unnamed
c = act_class.classify(bundle)
out["act_class"] = c.get("class")
out["rows"] = sorted({(f["path"], f["row"], f["class"]) for f in c.get("files", [])})
out["hits"] = c.get("hits")
print(json.dumps(out, indent=1))
