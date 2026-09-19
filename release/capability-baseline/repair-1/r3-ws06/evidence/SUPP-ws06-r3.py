#!/usr/bin/env python3
"""P2-AR-0037 (WS-6, repair iteration 1 round 3) — supplementary behaviours, run against a given `gov` (before: the base
53897c1 binary; after: this branch's). Builder regression evidence (Contract v3 O3), not acceptance evidence.

Every scenario drives the real binary on a disposable copy of fixtures/greenfield/project; human answers (S9 only) are
relayed by the evidence adapter the runner puts in front of the binary (the round-2 integration's root-channel shim),
never signed here.

  S1  R2-10   files the indexer skips (too large, not UTF-8, a duplicate record id) are not "unindexed" to freshness,
              and a change transaction commits while they exist (its index_freshness verification used to fail)
  S2  R2-10   an exclusion the manifest records never hides a file the path map stops excluding
  S3  R2-10 / BC-P2-29  the occurrence of a duplicated record id the index holds is the record store's, in an
              incremental build as in a full one
  S4  R2-11   a significant mutation observed at `rebuild-memory` writes a checkpoint (delta-r N2.b4's scenario)
  S5  R3-4    Markdown headings (a title directly followed by a sub-heading) are held; no coverage gap is reported
  S6  IP-W7-2 a declared code_intel adapter the product refuses is a recorded degradation (beta-r C5-b8-degrade)
  S7  IP-WS10-05  incomplete research presented as evidence is held reference-only by the index (delta-r J1.b.retrieval)
  S8  IP-WS10-04  `memory benchmark --record --task` writes concluded research naming the commissioning task
  S9  IP-WS10-03  the governed profile decision taken on the benchmark is recorded as its influence
  S10 BC-P2-31    the installed repository contract classifies the OS's stores truthfully under any reading (the check of
              synthesis AC16-X2 X2-B1B3), its specific rules take effect (last-match), framework.json projects the kernel
              store rules

Environment: GOV (the gov under test, or the adapter in front of it), SUPP_SCRATCH (private scratch), WT (tree with
fixtures/). Output: one `CHECK <id> PASS|FAIL <what>` line per check, then a SUMMARY line.
"""
import fnmatch
import json
import os
import shutil
import subprocess
import sys
import uuid

import yaml

GOV = os.environ["GOV"]
SCR = os.environ["SUPP_SCRATCH"]
WT = os.environ["WT"]
RESULTS = []


def check(cid, ok, what, detail=None):
    RESULTS.append((cid, bool(ok)))
    print(f"CHECK {cid} {'PASS' if ok else 'FAIL'} {what}")
    if detail is not None:
        print("      detail: " + json.dumps(detail, default=str)[:1500])


class Proj:
    def __init__(self, tag):
        self.root = os.path.join(SCR, f"{tag}-{uuid.uuid4().hex[:6]}")
        shutil.copytree(os.path.join(WT, "fixtures/greenfield/project"), self.root)
        self.git("init", "-q")
        self.commit("fixture")
        self.machine = self.root + ".machine"
        r = self.run(["init", "--name", tag, "--alias", f"{tag}-alias"])
        assert r.get("ok"), r

    def git(self, *a):
        subprocess.run(["git", "-C", self.root, "-c", "user.email=p@x", "-c", "user.name=p", *a], check=True,
                       capture_output=True)

    def commit(self, msg):
        self.git("add", "-A")
        subprocess.run(["git", "-C", self.root, "-c", "user.email=p@x", "-c", "user.name=p", "commit", "-q",
                        "--allow-empty", "-m", msg], capture_output=True)

    def run(self, args, session="S-supp", role="orchestrator"):
        env = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
        env["XDG_STATE_HOME"] = self.machine
        cmd = [GOV, "--json", "--root", self.root, "--session", session, "--role", role, *args]
        p = subprocess.run(cmd, capture_output=True, text=True, env=env)
        print(f"$ gov {' '.join(args)[:160]} -> exit {p.returncode}")
        try:
            return json.loads(p.stdout)
        except Exception:
            return {"ok": False, "error": {"code": "NO_JSON", "message": (p.stderr or p.stdout)[:400]}}

    def ok(self, args, **kw):
        r = self.run(args, **kw)
        if not r.get("ok"):
            raise RuntimeError(f"gov {' '.join(args)} failed: {r.get('error')}")
        return r["result"]

    def write(self, rel, text):
        p = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(text)

    def put(self, rel, data):
        self.write(rel, yaml.safe_dump(data, sort_keys=False))

    def read_yaml(self, rel):
        return yaml.safe_load(open(os.path.join(self.root, rel)))

    def sql(self, q, *a):
        import sqlite3
        c = sqlite3.connect(os.path.join(self.root, ".governance-runtime/state.db"))
        try:
            return c.execute(q, a).fetchall()
        finally:
            c.close()


def req(i, title):
    return {"id": i, "type": "requirement", "title": title, "status": "ACTIVE", "kind": "functional"}


def section(name):
    print(f"\n## {name}", flush=True)


def guarded(fn):
    try:
        fn()
    except Exception as e:  # a scenario that cannot proceed on this binary records why; later scenarios still run
        print(f"SCENARIO-STOPPED {fn.__name__}: {e}"[:1200])
        RESULTS.append((fn.__name__ + ".completed", False))


def s1():
    section("S1 R2-10: files the indexer skips; a change transaction commits while they exist")
    p = Proj("s1")
    p.write("product/big.txt", "a line of text the index would hold if it were not too large\n" * 36000)
    with open(os.path.join(p.root, "product/latin1.txt"), "wb") as f:
        f.write(b"caf\xe9 au lait\n")
    p.put("spec/requirements/REQ-0101.yaml", req("REQ-0101", "Totals are exact"))
    p.put("governance/project/extra/REQ-0101.yaml", req("REQ-0101", "Totals are exact (copy)"))
    p.commit("skipped files")
    r = p.ok(["rebuild-memory", "--incremental"])
    f = p.ok(["memory", "freshness"])
    check("S1.fresh-with-skipped-files", f["fresh"] is True and not f["added"],
          "after a build, nothing the indexer skips (too large, not UTF-8, duplicate id) reads as unindexed",
          {"fresh": f["fresh"], "added": f["added"], "excluded": [(e["path"], e["reason"]) for e in r.get("excluded", [])]})
    mf = os.path.join(p.root, ".governance-runtime/supp-m.json")
    json.dump([{"op": "write_file", "path": "spec/now/NOW.md", "content": "# NOW\ngoverned while skipped files exist\n"}],
              open(mf, "w"))
    c = p.ok(["cit", "propose", "--proposal", "editorial update of NOW", "--trigger", "editorial", "--manifest", mf])
    cid = c["id"]
    p.ok(["cit", "simulate", cid])
    p.ok(["cit", "approve", cid, "--by", "agent", "--method", "auto"])
    ex = p.run(["cit", "execute", cid])
    st = p.read_yaml(f"spec/decisions/{cid}.yaml").get("cit_status")
    check("S1.cit-commits", ex.get("ok") and st == "COMMITTED",
          "a change transaction's post-execution index_freshness verification passes while such files exist",
          {"ok": ex.get("ok"), "cit_status": st, "error": ex.get("error")})


def s2():
    section("S2 R2-10: a lifted path-map exclusion is not hidden by the manifest")
    p = Proj("s2")
    p.write("product/data/customers.md", "# Customers\nACME account\n")
    ds = p.read_yaml("governance/project/DATA_SENSITIVITY.yaml")
    ds["classifications"] = [{"pattern": "product/data/**", "class": "restricted"}]
    p.put("governance/project/DATA_SENSITIVITY.yaml", ds)
    p.commit("restricted data")
    p.ok(["rebuild-memory", "--incremental"])
    ds["classifications"] = []
    p.put("governance/project/DATA_SENSITIVITY.yaml", ds)
    f = p.ok(["memory", "freshness"])
    check("S2.lifted-exclusion-reported", "product/data/customers.md" in f["added"],
          "a file the path map no longer excludes is reported as not yet indexed", {"added": f["added"], "fresh": f["fresh"]})


def s3():
    section("S3 R2-10 / BC-P2-29: the held occurrence of a duplicated id; incremental equals full")
    p = Proj("s3")
    p.put("governance/project/extra/REQ-0102.yaml", req("REQ-0102", "Refunds are exact (governance copy)"))
    p.commit("one occurrence")
    p.ok(["rebuild-memory", "--incremental"])
    p.put("spec/requirements/REQ-0102.yaml", req("REQ-0102", "Refunds are exact"))
    inc = p.ok(["rebuild-memory", "--incremental"])
    held = p.sql("SELECT path FROM artifacts WHERE artifact_id='REQ-0102'")
    check("S3.held-occurrence-is-the-record-stores", held == [("spec/requirements/REQ-0102.yaml",)],
          "the index holds the occurrence the record store resolves the id to (spec/ before governance/project/)",
          {"held": held})
    full = p.ok(["rebuild-memory"])
    check("S3.incremental-equals-full", inc["manifest_hash"] == full["manifest_hash"],
          "the incremental build derived the same index as a full build", {"incremental": inc["manifest_hash"], "full": full["manifest_hash"]})


def s4():
    section("S4 R2-11: a significant mutation observed at rebuild writes a checkpoint (delta-r N2.b4's scenario)")
    p = Proj("s4")
    p.ok(["checkpoint", "create", "--next-action", "bulk import", "--step", "planned"])
    cdir = os.path.join(p.root, "spec/reports/checkpoints")
    n0 = len([f for f in os.listdir(cdir) if f.startswith("CKPT-")])
    for i in range(30):
        p.write(f"product/bulk_{i}.txt", f"{i}\n")
    r = p.ok(["rebuild-memory", "--incremental"])
    n1 = len([f for f in os.listdir(cdir) if f.startswith("CKPT-")])
    lt = p.ok(["checkpoint", "latest"])
    check("S4.checkpoint-at-significant-mutation", n1 > n0 and lt.get("trigger") == "significant_mutation",
          "30 new product files indexed by `rebuild-memory --incremental` write a significant_mutation checkpoint",
          {"before": n0, "after": n1, "trigger": lt.get("trigger"), "boundaries": r.get("boundaries")})


def s5():
    section("S5 R3-4: Markdown headings are held; no false coverage gap")
    p = Proj("s5")
    p.write("spec/notes/guide.md", "# Operating guide\n\n## Scope\nwhat the guide covers\n# Appendix\n## Glossary\n")
    p.commit("headings")
    r = p.ok(["rebuild-memory"])
    check("S5.build-coverage-complete", r["coverage"]["complete"] is True,
          "the build's coverage check finds every line of the document held (headings included)", r["coverage"])
    a = p.run(["audit", "--no-persist"])
    body = a.get("result") or (a.get("error") or {}).get("details") or {}
    fam = (body.get("families") or {}).get("index_content_coverage") or {}
    finds = [f for f in body.get("findings", []) if f.get("family") == "index_content_coverage"]
    check("S5.suite-no-coverage-gap", (fam.get("detail") or {}).get("complete") is True and not finds,
          "the governance suite's index_content_coverage family reports no gap for held headings",
          {"detail": fam.get("detail"), "findings": finds})


def s6():
    section("S6 IP-W7-2: a refused code_intel adapter is a recorded degradation")
    p = Proj("s6")
    p.write("product/app.py", "def total(lines):\n    return sum(lines)\n")
    shutil.copytree(os.path.join(WT, "capabilities/python/govos_capabilities"),
                    os.path.join(p.root, "tools/pyplug/govos_capabilities"),
                    ignore=shutil.ignore_patterns("__pycache__"))
    p.put("governance/project/plugins/python-ast.yaml",
          {"plugin_id": "python-ast", "capability": "code_intel", "version": "1.0.0", "languages": ["python"],
           "command": ["python3", "-m", "govos_capabilities.code_intel_python_ast"], "cwd": "tools/pyplug"})
    p.commit("declared python adapter")
    r = p.ok(["rebuild-memory"])
    deg = [d for d in r.get("degradations", []) if "python-ast" in d]
    check("S6.refused-adapter-degradation", bool(deg), "the build records the refused adapter as a degradation (C5-b8-degrade)",
          {"degradations": r.get("degradations")})
    recs = []
    for f in r.get("failures", []):
        if f.get("path") and os.path.exists(os.path.join(p.root, f["path"])):
            t = open(os.path.join(p.root, f["path"])).read()
            if "python-ast" in t:
                recs.append(f["path"])
    check("S6.failure-memory", bool(recs), "failure memory records the refused adapter (tool-failure)", {"failures": r.get("failures")})


def s7():
    section("S7 IP-WS10-05: incomplete research presented as evidence is held reference-only")
    p = Proj("s7")
    p.put("spec/research/RES-0101.yaml", {"id": "RES-0101", "type": "research", "title": "Unsupported claim", "status": "ACTIVE",
                                           "question": "Does caching help?", "conclusion": "Caching halves latency.", "state_class": "EVIDENCE"})
    p.commit("research")
    p.ok(["rebuild-memory", "--incremental"])
    q = p.ok(["memory", "query", "does caching halve latency"])
    hit = [(h["artifact_id"], h.get("state_class")) for h in q["hits"] if h["artifact_id"] == "RES-0101"]
    check("S7.incomplete-research-reference-only", hit and hit[0][1] == "NARRATIVE",
          "the unsupported research conclusion is retrievable only as reference (NARRATIVE), not as evidence", {"hits": hit})


def s8_s9():
    section("S8 IP-WS10-04 / S9 IP-WS10-03: benchmark research names its task; the decision is its influence")
    p = Proj("s8")
    t = p.ok(["task", "create", "--class", "discovery", "--objective", "choose the retrieval profile", "--status", "READY"])["id"]
    b = p.run(["memory", "benchmark", "--candidate", "current", "--candidate", "builtin:64", "--record", "--task", t])
    rec = p.read_yaml(f"spec/research/{b['result']['research_record']}.yaml") if b.get("ok") else {}
    check("S8.benchmark-names-its-task", b.get("ok") and rec.get("influences") == [t] and rec.get("research_state") == "CONCLUDED",
          "the recorded benchmark is concluded research that names the task that commissioned it",
          {"ok": b.get("ok"), "error": b.get("error"), "influences": rec.get("influences"), "research_state": rec.get("research_state")})
    if not b.get("ok"):
        b = {"result": p.ok(["memory", "benchmark", "--candidate", "current", "--candidate", "builtin:64", "--record"])}
    res = b["result"]["research_record"]
    sel = p.ok(["memory", "select", "builtin:64", "--research", res])
    if not sel.get("applied") and sel.get("human_gate"):
        g = sel["human_gate"]
        p.ok(["gate", "present", g])
        p.ok(["decide", g, "--option", "A", "--rationale", "owner relay by the evidence adapter"])
        sel = p.ok(["memory", "select", "builtin:64", "--research", res, "--gate", g])
    infl = p.read_yaml(f"spec/research/{res}.yaml").get("influences") or []
    check("S9.decision-recorded-as-influence", sel.get("decision") in infl,
          "the decision that adopted the benchmarked profile is recorded on the research it relied on",
          {"decision": sel.get("decision"), "influences": infl})


def s10():
    section("S10 BC-P2-31: the installed repository contract states where the OS keeps its state")
    p = Proj("s10")
    rc = p.read_yaml("governance/project/REPOSITORY_CONTRACT.yaml")
    rules = rc.get("paths", [])

    # the reading of synthesis AC16-X2 (every matching rule, fnmatch or prefix), verbatim in substance
    def any_match(path):
        hits = []
        for rule in rules:
            pat = rule.get("pattern")
            if pat and (fnmatch.fnmatch(path, pat) or path.startswith(pat.rstrip("*").rstrip("/") + "/")):
                hits.append((pat, rule.get("class")))
        return hits
    stores = (".governance-runtime/claims.db", ".governance-runtime/control.json", "governance/generated/plugin-registry.json")
    classes = {s: any_match(s) for s in stores}
    derivedish = any(c[1] in ("derived", "generated", "runtime") for v in classes.values() for c in v)
    check("S10.X2-B1B3-reading", not derivedish, "no rule the overlay applies to where claims, control state and the registry are kept is derived/generated",
          classes)

    # the product's documented reading (last match decides)
    def last_match(path):
        cls = None
        for rule in rules:
            if fnmatch.fnmatch(path, rule.get("pattern", "")):
                cls = rule.get("class")
        return cls
    want = {"spec/reports/checkpoints/CKPT-00001.yaml": "evidence", "spec/research/RES-0001.yaml": "evidence",
            "spec/requirements/REQ-0001.yaml": "authoritative", "product/tests/test_a.py": "test"}
    got = {k: last_match(k) for k in want}
    check("S10.specific-rules-take-effect", got == want, "the refining rules (spec evidence areas, product tests) decide their paths", got)
    fj = json.load(open(os.path.join(p.root, "framework.json")))
    kp = fj.get("kernel_paths") or {}
    check("S10.framework-json-kernel-paths", (kp.get(".governance-runtime/claims.db*") or {}).get("class") == "operational",
          "framework.json projects the kernel's classification of the OS stores", {"kernel_paths": list(kp)[:6], "precedence": fj.get("precedence")})


for fn in (s1, s2, s3, s4, s5, s6, s7, s8_s9, s10):
    guarded(fn)
passed = sum(1 for _, ok in RESULTS if ok)
print(f"\nSUMMARY checks={len(RESULTS)} pass={passed} fail={len(RESULTS) - passed} failed={[c for c, ok in RESULTS if not ok]}")
