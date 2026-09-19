#!/usr/bin/env python3
"""P2-AR-0014 builder regression evidence for BC-P2-01 (not independent verification).

Copies the contract binding chain (owner source, canonical import, compiled form, lock, schema, evidence map,
generated view) into disposable directories, applies one mutation per case, and runs
`target/release/gov --json --root <copy> contract verify`. Every mutation of a derived view must fail with a typed
error; the unmutated copy must report CONTRACT_SOURCE_BOUND.

usage (worktree root, after `cargo build --release`): python3 <this file> [PROBE_TMP]
"""
import json, os, re, shutil, subprocess, sys, tempfile
import yaml

WT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 6))
GOV = os.path.join(WT, "target/release/gov")
BASE = sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp(prefix="p2ar0014-bc01-")
os.makedirs(BASE, exist_ok=True)
FILES = [
    "Governance_OS_Capability_Acceptance_Contract_v3.md",
    "framework/contracts/source/GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3.md",
    "framework/contracts/governance-capability-acceptance.yaml",
    "framework/contracts/contract-source.lock",
    "framework/schemas/governance-capability-acceptance.schema.json",
    "tests/governance/capability-evidence-map.yaml",
    "docs/generated/GOVERNANCE_CAPABILITY_ACCEPTANCE.md",
]
COMPILED, LOCK, SCHEMA, MAP, VIEW, IMPORT = FILES[2], FILES[3], FILES[4], FILES[5], FILES[6], FILES[1]


def copy(tag):
    d = tempfile.mkdtemp(prefix=f"{tag}-", dir=BASE)
    for f in FILES:
        os.makedirs(os.path.dirname(os.path.join(d, f)) or d, exist_ok=True)
        shutil.copy(os.path.join(WT, f), os.path.join(d, f))
    return d


def yedit(d, rel, fn):
    p = os.path.join(d, rel)
    v = yaml.safe_load(open(p, encoding="utf-8"))
    fn(v)
    # the verifier compares parsed values, so the YAML emitter used here is irrelevant
    open(p, "w", encoding="utf-8").write(yaml.safe_dump(v, sort_keys=False, allow_unicode=True, width=10**9))


def tedit(d, rel, fn):
    p = os.path.join(d, rel)
    text = open(p, encoding="utf-8").read()
    edited = fn(text)
    assert edited != text, f"mutation of {rel} changed nothing"
    open(p, "w", encoding="utf-8").write(edited)


def idx(v, cid, key):
    return next(i for i, c in enumerate(v["capabilities"]) if c[key] == cid)


def verify(d):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
    r = subprocess.run([GOV, "--json", "--root", d, "contract", "verify"], capture_output=True, text=True, env=env)
    out = json.loads(r.stdout)
    if out.get("ok"):
        return r.returncode, out["result"]["verdict"], None
    e = out["error"]
    first = (e.get("details") or {}).get("differences", [{}])[0] if isinstance(e.get("details"), dict) else {}
    return r.returncode, e["code"], first


def rm_item(v, key):
    v["capabilities"][idx(v, "A1", key)]["checklist"].pop(0)


def rm_u(v, key):
    v["capabilities"].pop(idx(v, "U", key))


CASES = [
    ("positive control: unmodified chain", None, "CONTRACT_SOURCE_BOUND"),
    ("compiled: delete one checklist bullet (A1.1)", lambda d: yedit(d, COMPILED, lambda v: rm_item(v, "id")), "CONTRACT_COMPILED_DIVERGED"),
    ("compiled: delete capability U", lambda d: yedit(d, COMPILED, lambda v: rm_u(v, "id")), "CONTRACT_COMPILED_DIVERGED"),
    ("compiled: change one label (O5)", lambda d: yedit(d, COMPILED, lambda v: v["capabilities"][idx(v, "O5", "id")].__setitem__("requirement_class_label", "EXECUTION REFINEMENT")), "CONTRACT_COMPILED_DIVERGED"),
    ("compiled: map Gate V's label to ORIGINAL (V1)", lambda d: yedit(d, COMPILED, lambda v: v["capabilities"][idx(v, "V1", "id")].__setitem__("requirement_class", "ORIGINAL")), "CONTRACT_COMPILED_DIVERGED"),
    ("compiled: drop the W10 hard invariant", lambda d: yedit(d, COMPILED, lambda v: v["capabilities"][idx(v, "W10", "id")].__setitem__("statements", [s for s in v["capabilities"][idx(v, "W10", "id")]["statements"] if s["kind"] != "hard_invariant"])), "CONTRACT_COMPILED_DIVERGED"),
    ("compiled: drop the qualifier at line 515", lambda d: yedit(d, COMPILED, lambda v: v["capabilities"][idx(v, "H2", "id")].__setitem__("statements", [s for s in v["capabilities"][idx(v, "H2", "id")]["statements"] if s["line"] != 515])), "CONTRACT_COMPILED_DIVERGED"),
    ("compiled: drop Gate W's advanced-qualification challenge", lambda d: yedit(d, COMPILED, lambda v: v.__setitem__("advanced_qualification_challenges", [c for c in v["advanced_qualification_challenges"] if c["id"] != "AQC-W12"])), "CONTRACT_COMPILED_DIVERGED"),
    ("compiled: invent a per-capability severity (A1)", lambda d: yedit(d, COMPILED, lambda v: v["capabilities"][idx(v, "A1", "id")].__setitem__("severity", "HIGH")), "CONTRACT_COMPILED_DIVERGED"),
    ("evidence map: delete one checklist bullet (A1.1)", lambda d: yedit(d, MAP, lambda v: rm_item(v, "capability")), "CONTRACT_EVIDENCE_MAP_DIVERGED"),
    ("evidence map: delete capability U", lambda d: yedit(d, MAP, lambda v: rm_u(v, "capability")), "CONTRACT_EVIDENCE_MAP_DIVERGED"),
    ("evidence map: change one label (V4)", lambda d: yedit(d, MAP, lambda v: v["capabilities"][idx(v, "V4", "capability")].__setitem__("requirement_class_label", "NEW EXECUTION REFINEMENT")), "CONTRACT_EVIDENCE_MAP_DIVERGED"),
    ("evidence map: drop a Contract v3:53-73 field (A1.freshness_triggers)", lambda d: yedit(d, MAP, lambda v: v["capabilities"][idx(v, "A1", "capability")].pop("freshness_triggers")), "CONTRACT_EVIDENCE_MAP_DIVERGED"),
    ("evidence map: evidence class outside Contract v3:81-91", lambda d: yedit(d, MAP, lambda v: v["capabilities"][idx(v, "A1", "capability")].__setitem__("evidence_class", "vibes")), "CONTRACT_EVIDENCE_MAP_DIVERGED"),
    ("generated view: delete one checklist bullet line", lambda d: tedit(d, VIEW, lambda t: re.sub(r"^- \[ \] Constitution/hard invariants.*\n", "", t, count=1, flags=re.M)), "CONTRACT_GENERATED_VIEW_DIVERGED"),
    ("generated view: delete capability U's row", lambda d: tedit(d, VIEW, lambda t: re.sub(r"^\| `U` \|.*\n", "", t, count=1, flags=re.M)), "CONTRACT_GENERATED_VIEW_DIVERGED"),
    ("generated view: change one label", lambda d: tedit(d, VIEW, lambda t: t.replace("`NEW TESTING REFINEMENT`", "`TESTING_REFINEMENT`", 1)), "CONTRACT_GENERATED_VIEW_DIVERGED"),
    ("source lock: alter the evidence-map digest", lambda d: yedit(d, LOCK, lambda v: v.__setitem__("evidence_map_source_sha256", "0" * 64)), "CONTRACT_LOCK_DIVERGED"),
    ("schema: an id pattern that cannot express Gate U", lambda d: tedit(d, SCHEMA, lambda t: t.replace("^[A-Z]+[0-9]*$", "^[A-Z]+[0-9]+$")), "CONTRACT_SCHEMA_DIVERGED"),
    ("canonical import: one appended line", lambda d: tedit(d, IMPORT, lambda t: t + "\nan unauthorised addition\n"), "CONTRACT_SOURCE_DIVERGED"),
]

fails = 0
print(f"# gov: {GOV}")
print(f"# gov sha256: {subprocess.run(['sha256sum', GOV], capture_output=True, text=True).stdout.split()[0]}")
print(f"# worktree HEAD: {subprocess.run(['git', '-C', WT, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()}")
for name, mutate, want in CASES:
    d = copy("case")
    if mutate:
        mutate(d)
    rc, got, first = verify(d)
    ok = got == want and ((rc == 0) == (want == "CONTRACT_SOURCE_BOUND"))
    fails += 0 if ok else 1
    detail = f" | first difference: {first.get('at')} {first.get('problem')}" if first else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: exit={rc} {got} (expected {want}){detail}")
print(f"SUMMARY cases={len(CASES)} pass={len(CASES) - fails} fail={fails}")
sys.exit(1 if fails else 0)
