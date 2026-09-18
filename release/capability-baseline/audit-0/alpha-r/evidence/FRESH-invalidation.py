#!/usr/bin/env python3
"""Freshness (Contract v3 lines 95-111; frozen contract AC-10): after a GREEN governance-suite record exists, change one
evidence input at a time and observe whether the product marks the prior green evidence stale (doctor D021
"governance suite green and current"), then restore and re-green before the next input.
Input classes exercised, mapped to the alpha capabilities they feed:
  overlay policy override (A1, A3, A4) · kernel policy file (A1, A2) · kernel schema (S2) · kernel migration (S5) ·
  path map / repository contract (B1, B2) · data-sensitivity policy (A3) · plugin/tool descriptor (A3) ·
  model/retrieval profile pin (S3) · authoritative decision (A1) · other authoritative spec record (B3) ·
  relevant product source (B1) · index manifest (B3) · trust anchor rotation / machine floors (A2) ·
  adoption evidence (S4, T2, T3)
Run: PROBE_TMP=<scratch> python3 FRESH-invalidation.py
"""
import os, sys, json, shutil
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from srr_mint import *
import yaml

sb = Sandbox("fresh")
p = sb.new_repo("f", {"README.md": "# f\n", "product/app.py": "def run():\n    return 1\n"})
sb.gov("init", "--name", "f", "--alias", "fa", cwd=p, quiet=True)
def green():
    sb.gov("rebuild-memory", cwd=p, quiet=True)
    a = sb.gov("audit", cwd=p, quiet=True)
    r_ = a.get("result") or (a.get("error") or {}).get("details") or {}
    return r_.get("verdict"), r_.get("green")
def d021():
    d = sb.gov("doctor", cwd=p, quiet=True); r_ = d.get("result") or (d.get("error") or {}).get("details") or {}
    c = [c for c in r_.get("checks", []) if c["id"] == "D021"][0]
    return c["ok"], c["message"]
def edit_file(rel, fn):
    f = os.path.join(p, rel); os.makedirs(os.path.dirname(f), exist_ok=True)
    old = open(f).read() if os.path.exists(f) else None
    open(f, "w").write(fn(old))
    return lambda: (open(f, "w").write(old) if old is not None else os.remove(f))
def yaml_edit(rel, mut):
    def fn(old):
        y = yaml.safe_load(old) if old else {}
        mut(y); return yaml.safe_dump(y, sort_keys=False)
    return edit_file(rel, fn)
cases = [
    ("overlay policy override (A1/A3/A4)", lambda: yaml_edit("governance/project/PROJECT_POLICY.yaml", lambda y: y.__setitem__("policy_overrides", {"CHANGE_POLICY.auto_approve_max_radius": "R0"}))),
    ("kernel policy file (A1/A2) [tamper]", lambda: edit_file("governance/kernel/policies/BUDGET_POLICY.yaml", lambda o: o + "# edit\n")),
    ("kernel schema (S2)", lambda: edit_file("governance/kernel/schemas/task.schema.json", lambda o: o + "\n")),
    ("kernel migration (S5)", lambda: edit_file("governance/kernel/migrations/M-4.1.4-4.1.5.yaml", lambda o: o + "# edit\n")),
    ("path map / repository contract (B1/B2)", lambda: yaml_edit("governance/project/REPOSITORY_CONTRACT.yaml", lambda y: y["paths"].append({"pattern": "extra/**", "class": "source"}))),
    ("data-sensitivity policy (A3)", lambda: yaml_edit("governance/project/DATA_SENSITIVITY.yaml", lambda y: y.__setitem__("classifications", [{"pattern": "product/**", "class": "confidential"}]))),
    ("plugin descriptor (A3)", lambda: edit_file("governance/project/plugins/x.yaml", lambda o: "plugin_id: x\ncapability: embed\ncommand: [\"true\"]\nversion: \"1\"\n")),
    ("retrieval profile pin via MEMORY_POLICY (S3)", lambda: yaml_edit("governance/project/PROJECT_POLICY.yaml", lambda y: y.__setitem__("policy_overrides", {"MEMORY_POLICY.retrieval.default_k": 3}))),
    ("authoritative decision spec/decisions (A1)", lambda: edit_file("spec/decisions/D-0009.yaml", lambda o: "id: D-0009\ntype: decision\ntitle: new decision\nstatus: ACTIVE\n")),
    ("other authoritative spec record spec/requirements (B3)", lambda: edit_file("spec/requirements/REQ-0001.yaml", lambda o: "id: REQ-0001\ntype: requirement\ntitle: new req\nstatus: ACTIVE\n")),
    ("relevant product source (B1)", lambda: edit_file("product/app.py", lambda o: o + "\ndef new():\n    return 2\n")),
    ("index manifest governance/generated (B3)", lambda: edit_file("governance/generated/index-manifest.json", lambda o: o.replace('"index_version"', '"index_version_x"'))),
    ("adoption evidence spec/audits/GOVERNANCE-ADOPTION (S4/T2/T3)", lambda: edit_file("spec/audits/GOVERNANCE-ADOPTION/06-migration-tests.yaml", lambda o: "tests: []\n")),
]
v = green(); print("## [F0] baseline green audit:", v, "| D021:", d021())
for label, mk in cases:
    restore = mk()
    ok, msg = d021()
    print(f"[F] {label:58s} -> D021 ok={ok!s:5s} ({msg})")
    restore(); green()
print("\n## [F-A2] trust-anchor provisioning / rotation on this machine after a green record")
A_, B_, C_ = K("root-a"), K("root-b"), K("root-c"); REL, SN, TS_ = K("release-1"), K("snapshot-1"), K("timestamp-1")
roles = {"root": (2, [A_, B_, C_]), "release": (1, [REL]), "snapshot": (1, [SN]), "timestamp": (1, [TS_])}
an = os.path.join(sb.admin, "root-1.json"); open(an, "w").write(envelope(root_doc(1, roles), [A_, B_]))
print("[F-A2] green:", green(), "| D021 before:", d021())
sb.gov("trust", "provision", "--anchor", an, cwd=sb.home, quiet=True)
print("[F-A2] after provisioning a trust anchor (machine posture UNPROVISIONED -> PROVISIONED): D021 =", d021())
an2 = os.path.join(sb.admin, "root-2.json"); open(an2, "w").write(envelope(root_doc(2, {"root": (2, [A_, B_, C_]), "release": (1, [K("release-2")]), "snapshot": (1, [SN]), "timestamp": (1, [TS_])}), [A_, B_]))
sb.gov("trust", "root-update", "--anchor", an2, cwd=sb.home, quiet=True)
print("[F-A2] after rotating the release key (root v2): D021 =", d021())
print("\nDONE")
