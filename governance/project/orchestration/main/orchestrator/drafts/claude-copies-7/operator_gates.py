"""Runs the operator's read-only gate functions over the ACT-CLAUDE-COPIES-7 bundle (validate_manifest, check_act,
path_rule, the files' hashes, act_class.classify), as in drafts/claude-copies-6/evidence/operator_gates.txt.
    python3 -I operator_gates.py <install dir> <bundle dir> <evidence dir> [ACT id]
"""
import hashlib, json, os, sys
from pathlib import Path

INSTALL, BUNDLE, EVID = (Path(a).resolve() for a in sys.argv[1:4])
ACT = sys.argv[4] if len(sys.argv) > 4 else "ACT-CLAUDE-COPIES-7"
sys.path.insert(0, str(INSTALL))
import opcommon as oc          # noqa: E402
import operator_run as orun    # noqa: E402
import act_class               # noqa: E402

raw = (BUNDLE / "manifest.json").read_bytes()
m = json.loads(raw)
out = [f"manifest sha256: {hashlib.sha256(raw).hexdigest()}"]
try:
    orun.validate_manifest(m)
    out.append("validate_manifest: pass")
except ValueError as e:
    out.append(f"validate_manifest: FAIL {e}")
try:
    orun.check_act(m, ACT)
    out.append("check_act: pass")
except oc.Refused as e:
    out.append(f"check_act: FAIL {e}")
try:
    orun.path_rule(str(BUNDLE), m, oc.load_settings())
    out.append("path_rule: pass")
except oc.Refused as e:
    out.append(f"path_rule: FAIL {e}")
bad = [p for p, h in m["files"].items() if hashlib.sha256((BUNDLE / p).read_bytes()).hexdigest() != h]
named = set(m["files"]) | {"manifest.json", "review.md"}
unnamed = sorted(str(p.relative_to(BUNDLE)) for p in BUNDLE.rglob("*") if p.is_file() and str(p.relative_to(BUNDLE)) not in named)
out.append(f"hash mismatches: {bad} ; unnamed on disk: {unnamed}")
cls = act_class.classify(str(BUNDLE))
out.append(f"act_class: class {cls['class']}; rows {sorted({f['row'] for f in cls['files']})}; hits {cls['hits']}")
EVID.mkdir(parents=True, exist_ok=True)
(EVID / "operator_gates.txt").write_text("\n".join(out) + "\n")
(EVID / "act_class.json").write_text(json.dumps(cls))
print("\n".join(out))
