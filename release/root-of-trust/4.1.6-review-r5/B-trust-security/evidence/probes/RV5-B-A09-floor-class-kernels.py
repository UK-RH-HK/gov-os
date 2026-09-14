#!/usr/bin/env python3
"""RV5-B-A09 / A10 / A11 — constitutional floors as a class under release-scoped registration (review r5 reviewer B, AR-0012).

Scratch only; the repository is never written. Instruments (loaded by path, NOT modified): the revision-5 checker
`constitutional-surface/csi_check.py` and `csi_lib.py` (E7 with `--registrations/--release-id`, `registration-reductions`,
`derive-registration`) and the draft inventory; the real legacy 4.1.5 binary as stand-in consumer, set up as review r4
reviewer B part P and the architect's REG5 do (attribution: `consume`, `rel_copy`, `set_patterns`, the secret marker and the
TPS v2 member classification follow `evidence/r5/REG5-release-scoped-registration.py`, which follows review r4 B).

  A09  Non-identical weakening of registered non-orderable content. 4.1.6 registers the old `aws-access-key` regex; 4.1.7
       registers the fix; 4.1.8 registers a regex that matches exactly what the old one matched but is not byte-identical.
       Also a tool descriptor whose health command changes in 4.1.8 (not a reversion). Is any computed reduction reported?
       Is 4.1.8 eligible under E7? On 4.1.5, is the `ASIA…` key file indexed and served under 4.1.8's content?
  A10  Where reductions are enforced. (i) E7 (`check --registrations`) on a registration that reverts the regex exactly
       without `lowering_history`; (ii) `registration-reductions` over the set with 4.1.7's registration withheld.
  A11  Unknown constitutional key and new constitutional file in registration mode (the registration is derived from the
       kernel that carries them).
  CLS  Non-security classes: a kernel changing only `project_tunable` leaves (review r4 B part T set) plus a key under the
       wildcard `informational` rule, registered as a new release: reductions and E7. (Consumption for that tunable set was
       executed by review r4 B part T and re-run unmodified in this review: every harm outcome equal to the genuine kernel.)

Environment: REVIEW_REPO (export of cdb4e14), GOV (legacy 4.1.5), SCRATCH. GOV_* stripped; HOME and GOV_KERNEL_CACHE in
scratch. Output: JSON on stdout.
"""
import copy, glob, json, os, re, shutil, sqlite3, subprocess, sys, tempfile

import yaml

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
CS = os.path.join(REPO, "release", "root-of-trust", "4.1.6", "constitutional-surface")
sys.path.insert(0, CS)
import csi_lib as L  # noqa: E402
import csi_check as C  # noqa: E402

GOV = os.environ["GOV"]
FW = os.path.join(REPO, "framework")
REL = os.path.join(REPO, "release", "releases", "4.1.5")
REL_TOOLS = os.path.join(REL, "kernel", "tools")
INV = yaml.safe_load(open(os.path.join(CS, "CONSTITUTIONAL_SURFACE_INVENTORY.yaml")))
S = tempfile.mkdtemp(prefix="rv5b-a09-", dir=os.environ["SCRATCH"])
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
ENV["GOV_KERNEL_CACHE"] = os.path.join(S, "cache")
ENV["HOME"] = os.path.join(S, "home")
os.makedirs(ENV["HOME"], exist_ok=True)

KEY = "SECURITY_POLICY.secret_content_patterns[id=aws-access-key].regex"
OLD_RE = "AKIA[0-9A-Z]{16}"
NEW_RE = "(AKIA|ASIA)[0-9A-Z]{16}"
VARIANT_RE = "(?:AKIA)[0-9A-Z]{16}"        # matches exactly the strings OLD_RE matches; not byte-identical
NEW_MEMBER = {"id": "gcp-api-key", "regex": "AIza[0-9A-Za-z_\\-]{35}"}
NEW_MEMBER_KEY = f"SECURITY_POLICY.secret_content_patterns[id={NEW_MEMBER['id']}].regex"
TOOL_ID = "TOOL-GIT-001"


def kcopy(name, src=FW):
    d = os.path.join(S, "k", name)
    shutil.copytree(src, d)
    if not os.path.exists(os.path.join(d, "tools")):
        shutil.copytree(REL_TOOLS, os.path.join(d, "tools"))
    return d


def ymut(kdir, rel, fn):
    p = os.path.join(kdir, rel)
    d = yaml.safe_load(open(p))
    fn(d)
    C.ydump(p, d)


def set_patterns(kdir, aws_re, with_member=True):
    def f(d):
        for p in d["secret_content_patterns"]:
            if p["id"] == "aws-access-key":
                p["regex"] = aws_re
        if with_member and not any(p["id"] == NEW_MEMBER["id"] for p in d["secret_content_patterns"]):
            d["secret_content_patterns"].append(dict(NEW_MEMBER))
    ymut(kdir, "policies/SECURITY_POLICY.yaml", f)


def tool_field(kdir):
    doc = yaml.safe_load(open(os.path.join(kdir, "tools/registry/TOOLS.yaml")))
    t = next(t for t in doc["tools"] if t["tool_id"] == TOOL_ID)
    return {k: t.get(k) for k in t if any(w in k for w in ("command", "install", "health", "check"))}


def set_tool_command(kdir, value):
    def f(d):
        for t in d["tools"]:
            if t["tool_id"] == TOOL_ID:
                for k in list(t.keys()):
                    if "health" in k or "check" in k:
                        if isinstance(t[k], dict):
                            for kk in t[k]:
                                if "command" in kk:
                                    t[k][kk] = value
                        elif isinstance(t[k], str):
                            t[k] = value
                        elif isinstance(t[k], list):
                            t[k] = value.split(" ")
    ymut(kdir, "tools/registry/TOOLS.yaml", f)


INV2 = copy.deepcopy(INV)
fr_sec = next(f for f in INV2["files"] if f.get("path") == "policies/SECURITY_POLICY.yaml")
if not any(l["key"] == NEW_MEMBER_KEY for l in fr_sec["leaves"]):
    fr_sec["leaves"].append({"key": NEW_MEMBER_KEY, "class": "pinned", "note": "member introduced in 4.1.7 (TPS v2 classification)", "digests": {NEW_MEMBER_KEY: [L.vdigest(NEW_MEMBER["regex"])]}})


def check(kdir, regs, release_id, inv=INV2):
    r = C.run_check(kdir, inv, quiet=True, registrations=regs, release_id=release_id)
    return {"exit": r["exit"], "violations": [str(v)[:200] for v in (r.get("violations") or [])[:3]], "malformed": [str(m)[:200] for m in (r.get("malformed") or [])[:2]],
            "unclassified": [str(x)[:160] for x in (r.get("unclassified_leaves") or [])[:3]] + [str(x)[:160] for x in (r.get("unclassified_files") or [])[:3]]}


def reductions(regs, inv=INV2):
    r = C.run_registration_reductions(regs, quiet=True, inv=inv)
    return {"exit": r["exit"], "reductions": [{k: v for k, v in x.items() if k in ("subject", "kind")} for x in r.get("reductions", [])], "undeclared": len(r.get("undeclared", []))}


out = {"probe": "RV5-B-A09/A10/A11/CLS floor class under release-scoped registration (AR-0012)",
       "binary": subprocess.run([GOV, "--version"], capture_output=True, text=True, env=ENV).stdout.strip()}

# ---------------------------------------------------------------------------------------------- releases
K416 = kcopy("4.1.6")                         # framework/ (4.1.5 kernel content) = old regex
set_patterns(K416, OLD_RE, with_member=False)
K417 = kcopy("4.1.7")
set_patterns(K417, NEW_RE)
K418v = kcopy("4.1.8-variant")
set_patterns(K418v, VARIANT_RE)
K418r = kcopy("4.1.8-exact-reversion")
set_patterns(K418r, OLD_RE)
tool_before = tool_field(K417)
K418t = kcopy("4.1.8-tool")
set_patterns(K418t, NEW_RE)
set_tool_command(K418t, "sh -c 'touch $HOME/rv5b-tool-command-ran'")
tool_after = tool_field(K418t)

REG416 = L.registration_record(INV2, K416, "4.1.6", 1600, "sha256:final-4.1.6")
REG417 = L.registration_record(INV2, K417, "4.1.7", 1700, "sha256:final-4.1.7")
REG418v = L.registration_record(INV2, K418v, "4.1.8", 1800, "sha256:final-4.1.8")
REG418r = L.registration_record(INV2, K418r, "4.1.8", 1800, "sha256:final-4.1.8")
REG418t = L.registration_record(INV2, K418t, "4.1.8", 1800, "sha256:final-4.1.8")

A09 = {
    "units_changed_4.1.7_to_4.1.8_variant": sorted(u for u in set(REG417["units"]) | set(REG418v["units"]) if REG417["units"].get(u) != REG418v["units"].get(u)),
    "E7_4.1.8_variant_under_its_registration": check(K418v, [REG416, REG417, REG418v], "4.1.8"),
    "registration_reductions_416_417_418variant": reductions([REG416, REG417, REG418v]),
    "control_exact_reversion_registration_reductions": reductions([REG416, REG417, REG418r]),
    "tool_descriptor_fields_before": tool_before, "tool_descriptor_fields_after": tool_after,
    "E7_4.1.8_tool_under_its_registration": check(K418t, [REG416, REG417, REG418t], "4.1.8"),
    "registration_reductions_416_417_418tool": reductions([REG416, REG417, REG418t]),
    "strength_direction_of_pinned_leaf": L.leaf_direction(next(l for l in fr_sec["leaves"] if l["key"] == KEY)),
}
A10 = {
    "E7_on_exact_reversion_without_lowering_history (verifier side)": check(K418r, [REG416, REG417, REG418r], "4.1.8"),
    "registration_reductions_same_set (ceremony tool)": reductions([REG416, REG417, REG418r]),
    "registration_reductions_with_4.1.7_withheld": reductions([REG416, REG418r]),
}

# ---------------------------------------------------------------------------------------------- A11
Ku = kcopy("4.1.7-unknown-key")
set_patterns(Ku, NEW_RE)
ymut(Ku, "KERNEL.yaml", lambda d: d.__setitem__("trust_bypass", True))
Kf = kcopy("4.1.7-new-file")
set_patterns(Kf, NEW_RE)
os.makedirs(os.path.join(Kf, "contracts"), exist_ok=True)
open(os.path.join(Kf, "contracts", "CAPABILITY_ACCEPTANCE_CONTRACT.md"), "w").write("# contract\n")
REGu = L.registration_record(INV2, Ku, "4.1.7u", 1701)
REGf = L.registration_record(INV2, Kf, "4.1.7f", 1702)
A11 = {"unknown_key_registration_mode": check(Ku, [REG416, REGu], "4.1.7u"), "unknown_key_plain_mode": check(Ku, None, None),
       "new_file_registration_mode": check(Kf, [REG416, REGf], "4.1.7f"), "new_file_plain_mode": check(Kf, None, None),
       "derived_registration_mentions_unknown_key": any("trust_bypass" in u for u in REGu["units"]),
       "derived_registration_mentions_new_file": any("CAPABILITY_ACCEPTANCE_CONTRACT" in u for u in REGf["units"])}

# ---------------------------------------------------------------------------------------------- CLS
TUNABLE_CHANGES = {
    ("policies/MEMORY_POLICY.yaml", "namespaces.archive.default_retrieval"): True, ("policies/MEMORY_POLICY.yaml", "retrieval.default_k"): 200,
    ("policies/ARCHIVE_POLICY.yaml", "archive_root"): "product/customers", ("policies/ARCHIVE_POLICY.yaml", "unused_code_action"): "delete",
    ("policies/CONTEXT_POLICY.yaml", "max_retrieved_slices"): 1000, ("policies/HUMAN_GATE_POLICY.yaml", "batch_low_priority"): True,
    ("policies/TOOL_POLICY.yaml", "plugins.timeout_seconds"): 1, ("policies/TEST_POLICY.yaml", "product_families"): [],
}


def set_dotted(d, dotted, v):
    cur = d
    parts = dotted.split(".")
    for p in parts[:-1]:
        cur = cur[p]
    cur[parts[-1]] = v


Kt = kcopy("4.1.7-tunables")
set_patterns(Kt, NEW_RE)
classes = {}
for (rel, dotted), v in TUNABLE_CHANGES.items():
    try:
        ymut(Kt, rel, lambda d, dotted=dotted, v=v: set_dotted(d, dotted, v))
        fr = L.match_file_rule(INV2, rel)
        lr = L.match_leaf_rule(fr, fr["name"] + "." + dotted)
        classes[f"{rel}:{dotted}"] = lr.get("class") if isinstance(lr, dict) else str(lr)
    except Exception as e:
        classes[f"{rel}:{dotted}"] = f"not applied: {e}"
ymut(Kt, "constitution/ROLES.yaml" if os.path.exists(os.path.join(Kt, "constitution/ROLES.yaml")) else glob.glob(os.path.join(Kt, "**/ROLES.yaml"), recursive=True)[0].replace(Kt + "/", ""),
     lambda d: d.get("authority_levels", {}).get("L2", {}).__setitem__("may_answer_trust_gates", True) if isinstance(d.get("authority_levels", {}).get("L2"), dict) else None)
REG417T = L.registration_record(INV2, Kt, "4.1.7", 1700, "sha256:final-4.1.7t")
CLS = {"changed_leaf_classes": classes, "E7_under_its_registration": check(Kt, [REG416, REG417T], "4.1.7"),
       "registration_reductions_416_417tunables": reductions([REG416, REG417T]),
       "units_differing_from_4.1.6": sorted(u for u in set(REG416["units"]) | set(REG417T["units"]) if REG416["units"].get(u) != REG417T["units"].get(u))}


# ---------------------------------------------------------------------------------------------- consumption on 4.1.5 (A09)
def gov(root, role, *a):
    r = subprocess.run([GOV, "--json", "--root", root, "--session", "S-rv5b", "--role", role, *a], env=ENV, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout[-300:], "stderr": r.stderr[-300:]}


def git(root, *a):
    subprocess.run(["git", "-c", "user.name=p", "-c", "user.email=p@x", *a], cwd=root, check=True, capture_output=True, env={"PATH": "/usr/bin:/bin", "HOME": ENV["HOME"], "GIT_CONFIG_NOSYSTEM": "1"})


def rel_copy(name, kernel_mutator):
    d = os.path.join(S, "src", name)
    shutil.copytree(REL, d)
    kernel_mutator(os.path.join(d, "kernel"))
    return d


def db_paths(root, suffix):
    try:
        con = sqlite3.connect(root + "/.governance-runtime/state.db")
        return [x[0] for x in con.execute("select path from artifacts") if x[0].endswith(suffix)]
    except sqlite3.Error as e:
        return f"db error {e}"


SECRET = "ASIAQ3EGUH7X4MPLE2Z9"
SECRET_AKIA = "AKIAQ3EGUH7X4MPLE2Z9"
MARK = "RV5BSECRETMARK"


def consume(label, src):
    root = os.path.join(S, "consumer-" + label)
    os.makedirs(root)
    git(root, "init", "-q")
    git(root, "commit", "-q", "--allow-empty", "-m", "i")
    init = gov(root, "orchestrator", "init", "--source", src, "--name", "rv5b", "--skip-index")
    os.makedirs(os.path.join(root, "product", "notes"), exist_ok=True)
    open(os.path.join(root, "product", "notes", "deploy.md"), "w").write(f"# Deploy notes {MARK}\n\naws key used by the job: {SECRET}\n")
    open(os.path.join(root, "product", "notes", "legacy.md"), "w").write(f"# Legacy notes {MARK}L\n\nold key: {SECRET_AKIA}\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "project material")
    trust = gov(root, "orchestrator", "kernel", "trust")
    rb = gov(root, "orchestrator", "rebuild-memory")
    q = gov(root, "orchestrator", "memory", "query", MARK)
    hits = [h.get("path") for h in ((q.get("result") or {}).get("hits") or []) if (h.get("path") or "").endswith("notes/deploy.md")]
    return {"init_ok": init.get("ok"), "kernel_trust_verified": (trust.get("result") or {}).get("verified"), "rebuild_ok": rb.get("ok"),
            "ASIA_file_indexed": db_paths(root, "notes/deploy.md"), "ASIA_file_retrievable": hits, "AKIA_file_indexed": db_paths(root, "notes/legacy.md")}


cons = {"4.1.7_fixed_regex": consume("417-fixed", rel_copy("417", lambda k: set_patterns(k, NEW_RE))),
        "4.1.8_variant_regex": consume("418-variant", rel_copy("418v", lambda k: set_patterns(k, VARIANT_RE)))}
A09["consumption_4_1_5"] = cons

out.update({"A09_non_identical_weakening": A09, "A10_reduction_enforcement_points": A10, "A11_unknown_key_and_file_registration_mode": A11, "CLS_non_security_classes": CLS})
out["verdicts"] = {
    "A09_variant_eligible_under_E7": A09["E7_4.1.8_variant_under_its_registration"]["exit"] == 0,
    "A09_variant_no_reduction_reported": A09["registration_reductions_416_417_418variant"]["exit"] == 0 and not A09["registration_reductions_416_417_418variant"]["reductions"],
    "A09_control_exact_reversion_reported": A09["control_exact_reversion_registration_reductions"]["exit"] == 6,
    "A09_tool_command_change_no_reduction": A09["registration_reductions_416_417_418tool"]["exit"] == 0 and A09["tool_descriptor_fields_before"] != A09["tool_descriptor_fields_after"],
    "A09_fixed_release_excludes_ASIA_file": not cons["4.1.7_fixed_regex"]["ASIA_file_indexed"],
    "A09_variant_release_indexes_ASIA_file": bool(cons["4.1.8_variant_regex"]["ASIA_file_indexed"]),
    "A09_variant_release_serves_ASIA_file": bool(cons["4.1.8_variant_regex"]["ASIA_file_retrievable"]),
    "A10_E7_accepts_undeclared_exact_reversion": A10["E7_on_exact_reversion_without_lowering_history (verifier side)"]["exit"] == 0,
    "A10_reversion_invisible_when_intermediate_registration_withheld": A10["registration_reductions_with_4.1.7_withheld"]["exit"] == 0,
    "A11_unknown_key_refused_in_registration_mode": A11["unknown_key_registration_mode"]["exit"] == 2,
    "A11_new_file_refused_in_registration_mode": A11["new_file_registration_mode"]["exit"] == 2,
    "CLS_tunable_and_informational_changes_eligible_without_reduction": CLS["E7_under_its_registration"]["exit"] == 0 and CLS["registration_reductions_416_417tunables"]["exit"] == 0,
}
txt = json.dumps(out, indent=1, default=str)
txt = txt.replace(S, "<scratch>").replace(REPO, "<repo>").replace(os.path.dirname(GOV), "<legacy-bin>")
print(re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad>", txt))
