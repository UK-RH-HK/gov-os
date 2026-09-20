#!/usr/bin/env python3
"""P2-AR-0042 (BC-P2-02) — MUTATION CONTROLS for the evidence owners, through the product surface.

Each case copies the contract chain (framework/, tests/governance/, docs/generated/, the owner source) into a disposable
tree, links the owners' sources (runtime/, release/, tests/certification/) read-only from the worktree — or copies the
certification crate when a test in it must change — applies one mutation, and runs
`gov --json --root <copy> contract verify` (or `contract compile`). Every mutation must fail with its typed error; the
unmutated copy must bind. Builder regression evidence (Contract v3 O3), not independent verification.

Env: GOV (the binary), WT (the worktree), SCRATCH (private directory). Prints one line per case:
  CONTROL <n> <expected code> <observed code> PASS|FAIL  <case>  <first difference>
"""
import json
import os
import shutil
import subprocess
import sys

import yaml

GOV, WT, SCR = os.environ["GOV"], os.environ["WT"], os.environ["SCRATCH"]
if os.path.exists(SCR):
    os.rename(SCR, f"{SCR}.old-{os.getpid()}")
os.makedirs(SCR)
MAP = "tests/governance/capability-evidence-map.yaml"
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
n = 0
fails = 0


def tree(tag, sources=True, copied_tests=False):
    c = os.path.join(SCR, tag)
    for d in ["framework", "tests/governance", "docs/generated"]:
        shutil.copytree(os.path.join(WT, d), os.path.join(c, d))
    shutil.copy(os.path.join(WT, "Governance_OS_Capability_Acceptance_Contract_v3.md"), c)
    if sources:
        for d in ["runtime", "release"]:
            os.symlink(os.path.join(WT, d), os.path.join(c, d))
        if copied_tests:
            shutil.copytree(os.path.join(WT, "tests/certification"), os.path.join(c, "tests/certification"))
        else:
            os.symlink(os.path.join(WT, "tests/certification"), os.path.join(c, "tests/certification"))
    return c


def gov(c, *a):
    r = subprocess.run([GOV, "--json", "--root", c, "contract", *a], capture_output=True, text=True, env=ENV)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"ok": False, "error": {"code": "NOT_JSON", "message": (r.stdout + r.stderr)[-300:]}}


def edit(c, fn):
    p = os.path.join(c, MAP)
    v = yaml.safe_load(open(p))
    fn(v)
    open(p, "w").write(yaml.safe_dump(v, sort_keys=False, allow_unicode=True, width=10**9))


def row(v, cap):
    return next(r for r in v["capabilities"] if r["capability"] == cap)


def first(r, prefix, field="automated_checks"):
    return next(o for o in r[field] if o["id"].startswith(prefix))


def report(expected, d, name):
    global n, fails
    n += 1
    code = "CONTRACT_SOURCE_BOUND" if d.get("ok") and (d.get("result") or {}).get("verdict") == "CONTRACT_SOURCE_BOUND" \
        else (d.get("error") or {}).get("code") or ("OK" if d.get("ok") else "?")
    ok = code == expected
    fails += 0 if ok else 1
    det = (d.get("error") or {}).get("details") or {}
    diff = (det.get("differences") or [{}])[0]
    why = f"{diff.get('at', '')} {diff.get('problem', '')}".strip() or (d.get("error") or {}).get("message", "")[:160]
    print(f"CONTROL {n:02d} {expected} {code} {'PASS' if ok else 'FAIL'}  {name}  {why[:260]}", flush=True)


def case(name, expected, mutate, verb="verify", **kw):
    c = tree(f"c{n + 1:02d}", **kw)
    if mutate:
        mutate(c)
    report(expected, gov(c, verb), name)


def m(fn):
    return lambda c: edit(c, fn)


print(f"# gov {GOV}; worktree {WT}", flush=True)
case("unmutated chain, owners' sources present", "CONTRACT_SOURCE_BOUND", None)
case("zero owners: Gate U", "CONTRACT_EVIDENCE_OWNER_MISSING", m(lambda v: (row(v, "U").update(
    automated_checks=[], independent_verification=[]), [it.update(automated_checks=[]) for it in row(v, "U")["checklist"]])))
case("only an obligation of a future verifier: A1", "CONTRACT_EVIDENCE_OWNER_MISSING", m(lambda v: (row(v, "A1").update(
    automated_checks=[], independent_verification=[{"id": "obligation:AC-12", "class": "independent audit evidence"}]),
    [it.update(automated_checks=[]) for it in row(v, "A1")["checklist"]])))
case("a test owner renamed away (W3)", "CONTRACT_EVIDENCE_OWNER_UNRESOLVED",
     m(lambda v: first(row(v, "W3"), "test:").update(id=first(row(v, "W3"), "test:")["id"] + "_renamed")))


def ignore_owner(c):
    v = yaml.safe_load(open(os.path.join(c, MAP)))
    oid = first(row(v, "L3"), "test:certification:")["id"]
    mod, fn = oid[len("test:certification:"):].split("::", 1)
    p = os.path.join(c, "tests/certification", mod + ".rs")
    s = open(p).read()
    anchor = f"#[test]\nfn {fn}("
    assert s.count(anchor) == 1, (p, fn)
    open(p, "w").write(s.replace(anchor, f"#[test]\n#[ignore]\nfn {fn}("))


case("an owner test #[ignore]d (L3, copied certification crate)", "CONTRACT_EVIDENCE_OWNER_UNRESOLVED", ignore_owner,
     copied_tests=True)
case("a check the scheduler catalogue does not declare (B2)", "CONTRACT_EVIDENCE_OWNER_UNRESOLVED",
     m(lambda v: first(row(v, "B2"), "check:").update(id="check:path_map_vibes")))
case("a check at a tier the catalogue does not declare (A3)", "CONTRACT_EVIDENCE_OWNER_UNRESOLVED",
     m(lambda v: first(row(v, "A3"), "check:").update(tiers=["G2"])))
case("a G0 owner on a command G0 does not guard (E1: release build)", "CONTRACT_EVIDENCE_OWNER_UNRESOLVED",
     m(lambda v: first(row(v, "E1"), "g0:").update(id="g0:release build")))
case("a held-out test the suite does not have (A2)", "CONTRACT_EVIDENCE_OWNER_UNRESOLVED",
     m(lambda v: first(row(v, "A2"), "heldout:", "independent_verification").update(tests=["heldout_srr::no_such_test"])))
case("a held-out suite that does not exist (O3)", "CONTRACT_EVIDENCE_OWNER_UNRESOLVED",
     m(lambda v: first(row(v, "O3"), "heldout:", "independent_verification").update(
         id="heldout:release/verification/4.1.9-nowhere/evidence/heldout-tests")))
case("an obligation the gate contract does not assign to an independent verifier (AC-10)",
     "CONTRACT_EVIDENCE_OWNER_UNRESOLVED",
     m(lambda v: first(row(v, "D2"), "obligation:", "independent_verification").update(id="obligation:AC-10")))
case("a human-gate owner naming no kernel record type (L2)", "CONTRACT_EVIDENCE_OWNER_UNRESOLVED",
     m(lambda v: first(row(v, "L2"), "human-gate:").update(record="no-such-record")))
# an unknown kind is refused first by the evidence-map schema's owner-id pattern (then, if it got that far, by the
# resolver): CONTRACT_EVIDENCE_MAP_DIVERGED (first run expected _UNRESOLVED and recorded the schema refusal; kept below)
case("an owner kind the contract does not know", "CONTRACT_EVIDENCE_MAP_DIVERGED",
     m(lambda v: row(v, "C1")["automated_checks"].append({"id": "vibes:trust-me", "class": "unit/integration/system test"})))
case("row evidence class outside Contract v3:81-91 (K2)", "CONTRACT_EVIDENCE_MAP_DIVERGED",
     m(lambda v: row(v, "K2").update(evidence_class=["builder says so"])))
case("row tier outside O5 (K2: G7)", "CONTRACT_EVIDENCE_MAP_DIVERGED",
     m(lambda v: row(v, "K2").update(health_scheduler_tiers=["G7"])))
case("freshness trigger outside Contract v3:97-109 (D1)", "CONTRACT_EVIDENCE_MAP_DIVERGED",
     m(lambda v: row(v, "D1").update(freshness_triggers=["the weather"])))
case("allowed status outside the frozen gate contract §4 (D2)", "CONTRACT_EVIDENCE_MAP_DIVERGED",
     m(lambda v: row(v, "D2").update(allowed_status=["GREEN_ENOUGH"])))
case("an owner's class outside Contract v3:81-91 (E4)", "CONTRACT_EVIDENCE_OWNER_INVALID",
     m(lambda v: first(row(v, "E4"), "test:").update({"class": "vibes"})))
case("an independent owner filed as builder evidence (A2)", "CONTRACT_EVIDENCE_OWNER_INVALID",
     m(lambda v: row(v, "A2")["automated_checks"].append(dict(row(v, "A2")["independent_verification"][0]))))
case("an evidence class claimed without an owner that carries it (C4)", "CONTRACT_EVIDENCE_OWNER_INVALID",
     m(lambda v: row(v, "C4")["evidence_class"].append("synthetic-repository evidence")))
case("a tier claimed without an owner that runs there (Q2)", "CONTRACT_EVIDENCE_OWNER_INVALID",
     m(lambda v: row(v, "Q2").update(health_scheduler_tiers=["G6"])))
case("an in-vocabulary freshness trigger no owner's inputs include (A4)", "CONTRACT_EVIDENCE_OWNER_INVALID",
     m(lambda v: row(v, "A4")["freshness_triggers"].append("model/retrieval profile")))
case("a freshness trigger in use with no owner proving its invalidation", "CONTRACT_EVIDENCE_OWNER_INVALID",
     m(lambda v: v.update(freshness_invalidation=[e for e in v["freshness_invalidation"] if e["trigger"] != "project path map"])))
case("a checklist item naming an owner its capability does not have (A1.1)", "CONTRACT_EVIDENCE_OWNER_INVALID",
     m(lambda v: row(v, "A1")["checklist"][0].update(automated_checks=["check:graph_integrity"])))
case("a governed field changed without a recompile (O5 severity)", "CONTRACT_EVIDENCE_MAP_NOT_RECOMPILED",
     m(lambda v: row(v, "O5").update(severity="critical")))
case("an owner's statement edited without a recompile (W8)", "CONTRACT_EVIDENCE_MAP_NOT_RECOMPILED",
     m(lambda v: first(row(v, "W8"), "test:").update(exercises="edited by hand after the last compile")))
case("a release-tooling tree without the owners' sources: verify discloses deferred owners", "CONTRACT_SOURCE_BOUND", None,
     sources=False)
case("a release-tooling tree without the owners' sources: compile refuses", "CONTRACT_EVIDENCE_OWNER_UNRESOLVED", None,
     verb="compile", sources=False)
# AC-13: compile preserves every governed field (idempotent over the committed map)
c = tree("c-compile")
before = open(os.path.join(c, MAP), "rb").read()
d = gov(c, "compile")
after = open(os.path.join(c, MAP), "rb").read()
n += 1
ok = d.get("ok") and before == after
fails += 0 if ok else 1
print(f"CONTROL {n:02d} compile-preserves-governed-fields {'OK' if d.get('ok') else (d.get('error') or {}).get('code')} "
      f"{'PASS' if ok else 'FAIL'}  `gov contract compile` over the committed chain rewrites the evidence map byte-identically",
      flush=True)
print(f"# SUMMARY {n - fails}/{n} controls as expected", flush=True)
sys.exit(1 if fails else 0)
