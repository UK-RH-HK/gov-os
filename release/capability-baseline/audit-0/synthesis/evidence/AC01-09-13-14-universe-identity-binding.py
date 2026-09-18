#!/usr/bin/env python3
"""P2-AR-0007 synthesis probe: AC-1 (universe), AC-9 (frozen candidate identity), AC-13 (contract-binding chain and
semantic fidelity of the derived views), AC-14 (R1-preservation precondition: digest equality).

Independent of every family: the universe is parsed from the owner source text itself, then reconciled against
(a) the union of the six family audits of record, (b) the compiled YAML, (c) the evidence map, (d) the generated view.

usage (from the worktree root, after `~/.cargo/bin/cargo build --release`):
  python3 release/capability-baseline/audit-0/synthesis/evidence/AC01-09-13-14-universe-identity-binding.py
Every output line is tagged [AC-n] or [UNIV]; the synthesis report cites the tags.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))
OWNER = "Governance_OS_Capability_Acceptance_Contract_v3.md"
CANON = "framework/contracts/source/GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3.md"
COMPILED = "framework/contracts/governance-capability-acceptance.yaml"
LOCK = "framework/contracts/contract-source.lock"
EMAP = "tests/governance/capability-evidence-map.yaml"
GVIEW = "docs/generated/GOVERNANCE_CAPABILITY_ACCEPTANCE.md"
SCHEMA = "framework/schemas/governance-capability-acceptance.schema.json"
FAMILIES = ["alpha-r", "beta-r", "gamma-r", "delta-r", "epsilon-r", "zeta-r"]
GOV = os.path.join(ROOT, "target/release/gov")


def sh(*a, cwd=ROOT, env=None):
    r = subprocess.run(a, cwd=cwd, capture_output=True, text=True, env=env)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def sha(path):
    return hashlib.sha256(open(os.path.join(ROOT, path), "rb").read()).hexdigest()


def main():
    # ------------------------------------------------------------------ AC-9 / AC-14 identity
    print("=== AC-9 / AC-14: candidate identity")
    for ref in ["HEAD", "cap2-candidate-0^{commit}", "57177a37ea296ece16b185874831462b6a76db18", "srr1-r1-accepted^{commit}"]:
        rc, out, err = sh("git", "rev-parse", ref)
        commit = out
        rc, out, err = sh("python3", "release/orchestration/phase-2/tools/product_identity.py", commit)
        d = dict(l.split(": ", 1) for l in out.splitlines() if ": " in l)
        print(f"[AC-9] {ref:42s} commit={commit} product_code_digest={d.get('product_code_digest')} governed_state_digest={d.get('governed_state_digest')}")
    rc, out, _ = sh("git", "cat-file", "-p", "cap2-candidate-0")
    print("[AC-9] tag cap2-candidate-0 object:", out.splitlines()[0], "| type:", out.splitlines()[1])
    rc, out, _ = sh("git", "diff", "--name-only", "57177a37ea296ece16b185874831462b6a76db18", "HEAD")
    tops = sorted({"/".join(p.split("/")[:3]) for p in out.splitlines()})
    print(f"[AC-9] paths changed candidate..HEAD: {len(out.splitlines())} files under {tops}")
    prod = ["runtime", "cli", "tests", "framework", "capabilities", "migrations", "tools", "fixtures", "bin", "scripts", "Cargo.toml", "Cargo.lock"]
    touched = [p for p in out.splitlines() if p.split("/")[0] in prod]
    print(f"[AC-9] product-code paths changed candidate..HEAD: {touched}")
    rc, out, _ = sh("sha256sum", "target/release/gov")
    print(f"[AC-9] binary under test: {out}")
    rc, out, _ = sh("git", "rev-parse", "srr1-r1-accepted^{commit}")
    r1 = out
    rc, a, _ = sh("python3", "release/orchestration/phase-2/tools/product_identity.py", "HEAD")
    rc, b, _ = sh("python3", "release/orchestration/phase-2/tools/product_identity.py", r1)
    da = dict(l.split(": ", 1) for l in a.splitlines() if ": " in l)
    db = dict(l.split(": ", 1) for l in b.splitlines() if ": " in l)
    eq = da["product_code_digest"] == db["product_code_digest"]
    print(f"[AC-14] product_code_digest(HEAD)==product_code_digest(srr1-r1-accepted={r1[:7]}): {eq} -> AC-14 re-verification {'NOT REQUIRED' if eq else 'REQUIRED'}")
    # tool quirk: an annotated tag name passed as-is prints the tag-object id as 'commit'
    rc, out, _ = sh("python3", "release/orchestration/phase-2/tools/product_identity.py", "cap2-candidate-0")
    print(f"[AC-9] quirk: product_identity.py cap2-candidate-0 prints '{out.splitlines()[0]}' (the annotated tag object, not the commit); digests are unaffected because tree lookups dereference the tag")

    # ------------------------------------------------------------------ universe from the owner source
    print("\n=== AC-1: universe established from the owner source text")
    src = open(os.path.join(ROOT, OWNER), encoding="utf-8").read().splitlines()
    caps = []  # (id, title, line, label)
    for i, l in enumerate(src, 1):
        m = re.match(r"^## ([A-Z][0-9]+)\. (.*)$", l)
        if m:
            caps.append([m.group(1), m.group(2).strip(), i])
        if l.startswith("# GATE U"):
            caps.append(["U", "Framework Health SLOs", i])
    end_line = next(i for i, l in enumerate(src, 1) if l.startswith("# PRE-ADVANCED-QUALIFICATION ACCEPTANCE GATE"))
    caps.sort(key=lambda c: c[2])
    bullets = {}
    for idx, c in enumerate(caps):
        start = c[2]
        stop = caps[idx + 1][2] if idx + 1 < len(caps) else end_line
        bl = []
        for j in range(start + 1, stop):
            l = src[j - 1]
            if re.match(r"^\s*(-|\d+\.) \[ \] ", l) and not src[j - 1].startswith("#"):
                bl.append(j)
        # stop at the next gate heading as well
        bullets[c[0]] = bl
    labels = {}
    for c in caps:
        t = c[1]
        lab = re.findall(r"\*\*\[([A-Z -]+)\]\*\*", t)
        labels[c[0]] = lab[0] if lab else None
    # Gate-level labels (Gate V heading carries the label for V1..V4)
    gate_v = next(l for l in src if l.startswith("# GATE V"))
    gv_lab = re.findall(r"\*\*\[([A-Z -]+)\]\*\*", gate_v)
    for c in caps:
        if c[0].startswith("V"):
            labels[c[0]] = gv_lab[0] if gv_lab else labels[c[0]]
    universe = [c[0] for c in caps]
    nb = sum(len(v) for v in bullets.values())
    print(f"[UNIV] capabilities in owner source: {len(universe)}; checklist bullets (lines 130-{end_line - 1}): {nb}")
    gates = {}
    for c in universe:
        g = re.match(r"[A-Z]+", c).group(0)
        gates.setdefault(g, []).append(c)
    print("[UNIV] per gate: " + ", ".join(f"{g}:{len(v)}" for g, v in gates.items()))
    print("[UNIV] labelled capabilities: " + ", ".join(f"{k}={v}" for k, v in labels.items() if v))
    print("[UNIV] bullets per capability: " + " ".join(f"{c}={len(bullets[c])}" for c in universe))

    # ------------------------------------------------------------------ reconcile with the six family audits
    print("\n=== AC-1: reconciliation with the union of the six family audits of record")
    fam_caps = {}
    fam_lines = {}
    for fam in FAMILIES:
        d = yaml.safe_load(open(os.path.join(ROOT, "release/capability-baseline/audit-0", fam, "capability-audit.yaml")))
        for c in d["capabilities"]:
            cid = str(c["capability"])
            if cid in fam_caps:
                print(f"[AC-1] DUPLICATE capability {cid} in {fam} and {fam_caps[cid][0]}")
            fam_caps[cid] = (fam, c["status"], len(c.get("bullets") or []))
            fam_lines[cid] = {int(b["source_line"]) for b in (c.get("bullets") or []) if str(b.get("source_line", "")).isdigit()}
    missing = [c for c in universe if c not in fam_caps]
    extra = [c for c in fam_caps if c not in universe]
    print(f"[AC-1] family union: {len(fam_caps)} capabilities; missing from union: {missing}; not in owner source: {extra}")
    uncovered = {c: sorted(set(bullets[c]) - fam_lines.get(c, set())) for c in universe}
    uncovered = {c: v for c, v in uncovered.items() if v}
    print(f"[AC-1] owner-source bullet lines with no bullet record in the owning family audit: {uncovered or 'none'}")
    nostatus = [c for c, v in fam_caps.items() if not v[1]]
    print(f"[AC-1] capabilities without a status: {nostatus or 'none'}")
    for c in universe:
        f = fam_caps.get(c)
        print(f"[AC-1] {c:4s} family={f[0] if f else None:10s} status={f[1] if f else None:24s} family_bullets={f[2] if f else 0:3d} owner_bullets={len(bullets[c])}")

    # ------------------------------------------------------------------ AC-13 binding chain
    print("\n=== AC-13: contract-binding chain")
    s_owner, s_canon = sha(OWNER), sha(CANON)
    print(f"[AC-13] sha256 owner source   {s_owner}")
    print(f"[AC-13] sha256 canonical copy {s_canon}  byte-identical={open(os.path.join(ROOT, OWNER), 'rb').read() == open(os.path.join(ROOT, CANON), 'rb').read()}")
    lock = yaml.safe_load(open(os.path.join(ROOT, LOCK)))
    print(f"[AC-13] lock owner_source_sha256 matches: {lock['owner_source_sha256'] == s_owner}; canonical_import_sha256 matches: {lock['canonical_import_sha256'] == s_canon}; compiled_sha256 (canonical-JSON hash of the compiled value, util::hash_value) matches: {lock['compiled_sha256'] == hashlib.sha256(json.dumps(yaml.safe_load(open(os.path.join(ROOT, COMPILED))), sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()}")
    env = dict(os.environ)
    for k in list(env):
        if k.startswith("GOV_"):
            env.pop(k)
    rc, out, err = sh(GOV, "--json", "contract", "verify", env=env)
    v = json.loads(out)
    print(f"[AC-13] gov contract verify: exit={rc} verdict={v['result'].get('verdict')} capability_count={v['result'].get('capability_count')}")

    comp = yaml.safe_load(open(os.path.join(ROOT, COMPILED)))
    cc = {c["id"]: c for c in comp["capabilities"]}
    print(f"[AC-13] compiled capability_count={comp['capability_count']} ids={len(cc)}; owner universe={len(universe)}; missing from compiled: {[c for c in universe if c not in cc]}")
    fields = sorted({k for c in comp["capabilities"] for k in c})
    print(f"[AC-13] compiled per-capability fields: {fields}")
    req_fields = ["severity", "applicability", "evidence_class", "automated_checks", "independent_verification", "freshness_triggers", "health_scheduler_tiers", "qualification_challenges", "adoption_obligation", "operational_audit_obligation", "allowed_status", "na_requirements", "remediation_rule", "bullets", "checklist"]
    print(f"[AC-13] Contract v3:53-73 field classes present in compiled form: {[f for f in req_fields if f in fields] or 'none'}")
    blob = open(os.path.join(ROOT, COMPILED), encoding="utf-8").read()
    btxt = [re.sub(r"^\s*(-|\d+\.) \[ \] ", "", src[j - 1]).strip() for c in universe for j in bullets[c]]
    long_b = [t for t in btxt if len(t) >= 25]
    carried = sum(1 for t in long_b if t in blob)
    print(f"[AC-13] owner-source checklist bullets of >=25 chars whose full text appears in the compiled form: {carried}/{len(long_b)} (short one-word bullets such as 'tasks' are excluded because they match titles incidentally)")
    cls_map = {"POST-VERIFICATION HARDENING": "POST_VERIFICATION_HARDENING", "NEW EXECUTION REFINEMENT": "EXECUTION_REFINEMENT", "NEW TESTING REFINEMENT": "(no enumerated class; Contract v3:60 lists ORIGINAL/POST_VERIFICATION_HARDENING/EXECUTION_REFINEMENT)"}
    for c in universe:
        lab = labels.get(c)
        comp_cls = cc.get(c, {}).get("requirement_class")
        exp = cls_map.get(lab, "ORIGINAL") if lab else "ORIGINAL"
        mark = "OK" if (comp_cls == exp) else "DIVERGES"
        if lab or mark != "OK":
            print(f"[AC-13] class {c:4s} owner_label={lab!r:32s} compiled={comp_cls!r:32s} expected={exp!r} -> {mark}")
    for c in universe:
        if c in cc:
            t = cc[c]["title"]
            if "**" in t:
                print(f"[AC-13] title {c}: compiled title retains source markup: {t!r}")
    schema = json.load(open(os.path.join(ROOT, SCHEMA)))
    pat = schema["properties"]["capabilities"]["items"]["properties"]["id"]["pattern"]
    print(f"[AC-13] compiled-form schema id pattern {pat!r} admits 'U': {bool(re.match(pat, 'U'))}")

    em = yaml.safe_load(open(os.path.join(ROOT, EMAP)))
    rows = {r["capability"]: r for r in em["capabilities"]}
    classes = sorted({r.get("evidence_class") for r in rows.values()})
    nchk = sum(len(r.get("automated_checks") or []) for r in rows.values())
    print(f"[AC-13] evidence map rows={len(rows)} missing={[c for c in universe if c not in rows]} evidence_classes={classes} automated_checks_total={nchk}")
    zero = [c for c in universe if not (rows.get(c, {}).get("automated_checks"))]
    print(f"[AC-10] capabilities with zero evidence owners in the product's own evidence map: {len(zero)}/{len(universe)}")

    gv = open(os.path.join(ROOT, GVIEW), encoding="utf-8").read()
    gv_ids = re.findall(r"^\| `([A-Z]+[0-9]*)` \|", gv, re.M)
    print(f"[AC-13] generated view rows={len(gv_ids)} missing={[c for c in universe if c not in gv_ids]}; checklist bullets (>=25 chars) carried: {sum(1 for t in long_b if t in gv)}/{len(long_b)}")
    rc, out, _ = sh("grep", "-c", "EVIDENCE_MAP\\|GENERATED_VIEW", "runtime/src/contracts.rs")
    vsrc = open(os.path.join(ROOT, "runtime/src/contracts.rs")).read()
    vbody = vsrc[vsrc.index("pub fn verify("):vsrc.index("Ok(json!({", vsrc.index("pub fn verify("))]
    print(f"[AC-13] contracts::verify reads the evidence map: {'EVIDENCE_MAP' in vbody}; reads the generated view: {'GENERATED_VIEW' in vbody}; compares the compiled form only with a fresh run of the same headings-only compiler: {'compile(&import)' in vbody}")
    rc, out, _ = sh("grep", "-n", "SEMANTIC\\|bullet\\|checklist", "runtime/src/contracts.rs")
    print(f"[AC-13] runtime/src/contracts.rs mentions of bullets/checklist: {len(out.splitlines())} lines")


if __name__ == "__main__":
    main()
