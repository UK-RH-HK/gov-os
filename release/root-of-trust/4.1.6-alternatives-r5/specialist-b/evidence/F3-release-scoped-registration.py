#!/usr/bin/env python3
"""F3 - single-valued, release-scoped registration of non-orderable constitutional content (AR-0010, specialist B).

Executed. Instruments, loaded by path and UNMODIFIED:
  * the revision-4 coverage checker `constitutional-surface/csi_check.py` (`run_check`, `run_reductions`, `lint`) and
    library `csi_lib.py`;
  * the draft Trust Policy v1 surface `CONSTITUTIONAL_SURFACE_INVENTORY.yaml`;
  * the real legacy 4.1.5 binary as stand-in consumer (as review r3 B, P1r4 and review r4 B part P use it).

What this adds (01-ALTERNATIVE.md M3, form E2): a registration is a FUNCTION from release sequence to exactly one digest
(or one member-id set). `project(inv_seq, n)` turns a sequence-scoped surface into the revision-4 list form holding only
the digest registered for sequence n (or none), and E7 at sequence n is the unmodified revision-4 check against that
projection. Two rules are new and implemented here: `lint_single_valued` (no key has two digests for one sequence;
revision-4 multi-digest lists are malformed) and `content_reductions` (re-registering a superseded digest for a later
sequence, or rewriting an already-registered sequence, is a computed reduction).

Scenario shapes are review r4 B part P (RV4-B-A08: `aws-access-key` regex fixed in 4.1.7, TPS keeps the old digest) and
synthesis D-A02 (T1 tool descriptor member, T2 hard-invariant member, T3 schema file, T4 skill file); the consumer
function is copied from review r4 B `RV4-B-surface-probes.py` (`consume`, `rel_copy`, `db_paths`, `gov`, `git`), with
attribution. Environment: AR10_WORKTREE (default: derived), GOV (legacy 4.1.5), AR10_SCRATCH. GOV_* stripped from
children; HOME and GOV_KERNEL_CACHE point into scratch. Output: JSON on stdout with scratch paths replaced.
"""
import copy, glob, json, os, re, shutil, sqlite3, subprocess, sys, tempfile

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.environ.get("AR10_WORKTREE") or os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
CS = os.path.join(WT, "release", "root-of-trust", "4.1.6", "constitutional-surface")
sys.path.insert(0, CS)
import csi_lib as L  # noqa: E402
import csi_check as C  # noqa: E402

GOV = os.environ.get("GOV", "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/legacy-bin/gov-4.1.5")
FW = os.path.join(WT, "framework")
REL = os.path.join(WT, "release", "releases", "4.1.5")
REL_TOOLS = os.path.join(REL, "kernel", "tools")
INV = yaml.safe_load(open(os.path.join(CS, "CONSTITUTIONAL_SURFACE_INVENTORY.yaml")))
base = os.environ.get("AR10_SCRATCH") or tempfile.gettempdir()
os.makedirs(base, exist_ok=True)
S = tempfile.mkdtemp(prefix="f3-", dir=base)
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
ENV["GOV_KERNEL_CACHE"] = S + "/cache"
ENV["HOME"] = S + "/home"
os.makedirs(ENV["HOME"], exist_ok=True)
OPEN = None


# ------------------------------------------------------------------------------------------------ sequence-scoped registration
def slots(inv):
    """Yield (container, key) for every registered digest list and member-id list of non-orderable content."""
    for f in inv["files"]:
        if isinstance(f.get("digests"), dict):
            for p in f["digests"]:
                yield ("file", f, p)
        for lr in f.get("leaves") or []:
            if isinstance(lr.get("digests"), dict):
                for k in lr["digests"]:
                    yield ("leaf", lr, k)
            if lr.get("class") == "members":
                yield ("members", lr, lr["key"])


def to_sequence_scoped(inv, ranges):
    """Revision-4 list form -> sequence-scoped form: every single registered digest (or member set) holds for `ranges`
    (a list of (from, to) with to=None meaning open-ended)."""
    out = copy.deepcopy(inv)
    for kind, holder, key in slots(out):
        if kind == "members":
            holder["registered_by_sequence"] = [{"from": a, "to": b, "ids": list(holder["registered"])} for a, b in ranges]
        else:
            vals = holder["digests"][key]
            holder.setdefault("digests_by_sequence", {})[key] = [{"from": a, "to": b, "digest": d} for a, b in ranges for d in vals]
    return out


def lookup(ranges, n):
    hit = [r for r in ranges if r["from"] <= n and (r["to"] is OPEN or n <= r["to"])]
    return hit


def lint_single_valued(inv_seq):
    problems = []
    for kind, holder, key in slots(inv_seq):
        if kind == "members":
            rs = holder.get("registered_by_sequence")
            if rs is None:
                continue
        else:
            if len(holder["digests"].get(key, [])) > 1 and "digests_by_sequence" not in holder:
                problems.append({"key": key, "problem": "REGISTRATION_NOT_SINGLE_VALUED: a list of permitted digests lets a lower threshold select"})
                continue
            rs = (holder.get("digests_by_sequence") or {}).get(key)
            if rs is None:
                continue
        edges = sorted({r["from"] for r in rs} | {r["to"] for r in rs if r["to"] is not OPEN})
        for n in edges:
            if len(lookup(rs, n)) > 1:
                problems.append({"key": key, "sequence": n, "problem": "REGISTRATION_NOT_SINGLE_VALUED: overlapping ranges"})
                break
    return {"exit": 5 if problems else 0, "problems": problems[:10], "count": len(problems)}


def project(inv_seq, n):
    """Revision-4 list form holding exactly the registration for sequence n (empty list when none)."""
    out = copy.deepcopy(inv_seq)
    for kind, holder, key in slots(out):
        if kind == "members":
            rs = holder.pop("registered_by_sequence", None)
            if rs is not None:
                hit = lookup(rs, n)
                holder["registered"] = list(hit[0]["ids"]) if hit else []
        else:
            rs = (holder.get("digests_by_sequence") or {}).get(key)
            if rs is not None:
                hit = lookup(rs, n)
                holder["digests"][key] = [hit[0]["digest"]] if hit else []
    for f in out["files"]:
        # a leaf rule whose every registration starts after n does not exist at sequence n (introduced later)
        keep = []
        for lr in f.get("leaves") or []:
            rs_all = [r for rs in (lr.get("digests_by_sequence") or {}).values() for r in rs]
            if rs_all and all(r["from"] > n for r in rs_all):
                continue
            keep.append(lr)
        if f.get("leaves") is not None:
            f["leaves"] = keep
    for kind, holder, key in slots(out):
        holder.pop("digests_by_sequence", None)
    return out


def content_reductions(old_seq, new_seq, history_subjects=()):
    """Computed reductions of non-orderable content between two sequence-scoped registrations (01 M3):
    content_reversion   - a digest registered for a later sequence was superseded at an earlier sequence;
    registration_rewritten - an already-registered sequence now maps to a different digest."""
    reds = []
    old_map = {key: (holder.get("digests_by_sequence") or {}).get(key) for kind, holder, key in slots(old_seq) if kind != "members"}
    for kind, holder, key in slots(new_seq):
        if kind == "members":
            continue
        new_rs = (holder.get("digests_by_sequence") or {}).get(key) or []
        old_rs = old_map.get(key) or []
        for r in new_rs:
            for o in old_rs:
                ov_from = max(r["from"], o["from"])
                ov_to = min(x for x in (r["to"], o["to"]) if x is not OPEN) if (r["to"] is not OPEN or o["to"] is not OPEN) else OPEN
                if (ov_to is OPEN or ov_from <= ov_to) and o["digest"] != r["digest"]:
                    reds.append({"subject": key, "kind": "registration_rewritten", "sequence_from": ov_from})
        history = sorted(old_rs + new_rs, key=lambda x: x["from"])
        for r in new_rs:
            earlier = [h for h in history if h["to"] is not OPEN and h["to"] < r["from"]]
            superseded = [h for h in earlier if h["digest"] == r["digest"] and any(x["digest"] != r["digest"] and x["from"] > h["to"] and x["from"] <= r["from"] for x in history)]
            if superseded:
                reds.append({"subject": key, "kind": "content_reversion", "reverted_to_digest": r["digest"], "from_sequence": r["from"]})
    undeclared = [x for x in reds if x["subject"] not in set(history_subjects)]
    return {"exit": 6 if undeclared else 0, "reductions": reds[:20], "count": len(reds), "undeclared": len(undeclared)}


def e7(kdir, inv_seq, n):
    lint = lint_single_valued(inv_seq)
    if lint["exit"]:
        return {"exit": lint["exit"], "lint": lint}
    r = C.run_check(kdir, project(inv_seq, n), quiet=True)
    keep = {"exit": r["exit"]}
    for k in ("violations", "required_missing", "unclassified_leaves", "malformed", "consistency"):
        if r.get(k):
            keep[k + "_first"] = [str(x)[:200] for x in r[k][:3]]
            keep[k + "_count"] = len(r[k])
    return keep


# ------------------------------------------------------------------------------------------------ kernels (shapes of review r4 B part P)
def ydump(p, d):
    C.ydump(p, d)


def mut(kdir, rel, fn):
    p = os.path.join(kdir, rel)
    d = yaml.safe_load(open(p))
    fn(d)
    ydump(p, d)


def kcopy(name, src=FW, with_tools=False):
    d = os.path.join(S, "k", name)
    shutil.copytree(src, d)
    if with_tools and not os.path.exists(os.path.join(d, "tools")):
        shutil.copytree(REL_TOOLS, os.path.join(d, "tools"))
    return d


KEY = "SECURITY_POLICY.secret_content_patterns[id=aws-access-key].regex"
OLD_RE = "AKIA[0-9A-Z]{16}"
NEW_RE = "(AKIA|ASIA)[0-9A-Z]{16}"
NEW_MEMBER = {"id": "gcp-api-key", "regex": "AIza[0-9A-Za-z_\\-]{35}"}
MEMBERS_KEY = "SECURITY_POLICY.secret_content_patterns[id]#members"
NEW_MEMBER_KEY = f"SECURITY_POLICY.secret_content_patterns[id={NEW_MEMBER['id']}].regex"


def set_patterns(kdir, aws_re, with_member):
    def f(d):
        for p in d["secret_content_patterns"]:
            if p["id"] == "aws-access-key":
                p["regex"] = aws_re
        if with_member and not any(p["id"] == NEW_MEMBER["id"] for p in d["secret_content_patterns"]):
            d["secret_content_patterns"].append(dict(NEW_MEMBER))
    mut(kdir, "policies/SECURITY_POLICY.yaml", f)


def sec_rule(inv):
    fr = next(f for f in inv["files"] if f.get("path") == "policies/SECURITY_POLICY.yaml")
    return fr, next(l for l in fr["leaves"] if l["key"] == KEY), next(l for l in fr["leaves"] if l["key"] == MEMBERS_KEY)


d_old, d_new, d_member = L.vdigest(OLD_RE), L.vdigest(NEW_RE), L.vdigest(NEW_MEMBER["regex"])
assert sec_rule(INV)[1]["digests"][KEY] == [d_old], "draft TPS v1 registers the 4.1.6 regex digest"


def tps_v2(form):
    """TPS v2 after the 4.1.7 fix. form: 'open' (last range open-ended) or 'closed' (every release sequence registered)."""
    last = (7, OPEN) if form == "open" else (7, 7)
    inv = to_sequence_scoped(INV, [(6, OPEN)] if form == "open" else [(6, 6), (7, 7)])
    fr, lr, mr = sec_rule(inv)
    lr["digests_by_sequence"][KEY] = [{"from": 6, "to": 6, "digest": d_old}, {"from": last[0], "to": last[1], "digest": d_new}]
    base_ids = list(mr["registered"])
    mr["registered"] = sorted(set(base_ids) | {NEW_MEMBER["id"]})
    mr["registered_by_sequence"] = [{"from": 6, "to": 6, "ids": base_ids}, {"from": last[0], "to": last[1], "ids": sorted(set(base_ids) | {NEW_MEMBER["id"]})}]
    fr["leaves"].append({"key": NEW_MEMBER_KEY, "class": "pinned", "note": "registered member content (probe TPS v2)",
                         "digests": {NEW_MEMBER_KEY: [d_member]}, "digests_by_sequence": {NEW_MEMBER_KEY: [{"from": last[0], "to": last[1], "digest": d_member}]}})
    return inv


def tps_v1(form):
    return to_sequence_scoped(INV, [(6, OPEN)] if form == "open" else [(6, 6)])


def register_sequence(inv_seq, n, like):
    """A later TPS that registers release sequence n with the content registered for sequence `like` (closed form)."""
    out = copy.deepcopy(inv_seq)
    for kind, holder, key in slots(out):
        if kind == "members":
            rs = holder.get("registered_by_sequence") or []
            hit = lookup(rs, like)
            if hit:
                rs.append({"from": n, "to": n, "ids": list(hit[0]["ids"])})
        else:
            rs = (holder.get("digests_by_sequence") or {}).get(key) or []
            hit = lookup(rs, like)
            if hit:
                rs.append({"from": n, "to": n, "digest": hit[0]["digest"]})
    return out


out = {"probe": "F3 release-scoped registration (AR-0010)", "checker": "revision-4 csi_check.py / csi_lib.py, unmodified, run on projections",
       "binary": subprocess.run([GOV, "--version"], capture_output=True, text=True).stdout.strip(), "scratch": "<scratch>"}

k6 = FW                                                   # installed 4.1.6 content (draft TPS v1 registers it)
k7 = kcopy("P-4.1.7-fixed"); set_patterns(k7, NEW_RE, True)
k8_mixed = kcopy("P-4.1.8-forged-mixed"); set_patterns(k8_mixed, OLD_RE, True)      # every 4.1.7 change except the fixed regex
k8_stale = kcopy("P-4.1.8-forged-4.1.6-content")                                    # a later-sequence final carrying only 4.1.6 content
k8_genuine_same = kcopy("P-4.1.8-genuine-same-as-4.1.7"); set_patterns(k8_genuine_same, NEW_RE, True)

# revision-4 baseline (list form, B part P): TPS v2 RETAIN keeps [old, new]
inv_retain = copy.deepcopy(INV)
fr, lr, mr = sec_rule(inv_retain)
lr["digests"][KEY] = [d_old, d_new]
mr["registered"] = sorted(set(mr["registered"]) | {NEW_MEMBER["id"]})
fr["leaves"].append({"key": NEW_MEMBER_KEY, "class": "pinned", "digests": {NEW_MEMBER_KEY: [d_member]}})
partP = {
    "revision_4_list_form_RETAIN (reproduces review r4 B part P)": {
        "forged_4.1.8_mixed": C.run_check(k8_mixed, inv_retain, quiet=True)["exit"],
        "reductions_v1_to_RETAIN": C.run_reductions(INV, inv_retain, [], quiet=True)["exit"]},
    "single_valued_lint_on_revision_4_RETAIN": lint_single_valued(inv_retain),
}
for form in ("open", "closed"):
    v2 = tps_v2(form)
    v1 = tps_v1(form)
    partP[f"E2_{form}"] = {
        "lint_v2": lint_single_valued(v2)["exit"],
        "installed_4.1.6_at_seq_6_under_v2 (legitimate retention)": e7(k6, v2, 6),
        "fixed_4.1.7_at_seq_7_under_v2": e7(k7, v2, 7),
        "forged_4.1.8_mixed_old_regex_at_seq_8_under_v2": e7(k8_mixed, v2, 8),
        "forged_4.1.8_mixed_presented_as_seq_7_under_v2": e7(k8_mixed, v2, 7),
        "genuine_4.1.8_same_content_as_4.1.7_at_seq_8_under_v2 (availability)": e7(k8_genuine_same, v2, 8),
        "stale_machine_holding_only_v1: forged_4.1.8_with_4.1.6_content_at_seq_8": e7(k8_stale, v1, 8),
        "stale_machine_holding_only_v1: forged_4.1.8_mixed_at_seq_8 (differs from 4.1.6 only by the additive member)": e7(k8_mixed, v1, 8),
    }
    if form == "closed":
        v3 = register_sequence(v2, 8, like=7)
        partP["E2_closed"]["after_TPS_v3_registers_seq_8_like_7: genuine_4.1.8_same_content"] = e7(k8_genuine_same, v3, 8)
        partP["E2_closed"]["after_TPS_v3_registers_seq_8_like_7: forged_mixed"] = e7(k8_mixed, v3, 8)
    # an honest or compromised root re-registers the superseded regex for a later sequence
    v3r = copy.deepcopy(v2)
    _, lr3, _ = sec_rule(v3r)
    rs = lr3["digests_by_sequence"][KEY]
    if form == "open":
        rs[-1]["to"] = 7
    rs.append({"from": 8, "to": OPEN if form == "open" else 8, "digest": d_old})
    v3w = copy.deepcopy(v2)
    _, lr3w, _ = sec_rule(v3w)
    lr3w["digests_by_sequence"][KEY][0]["digest"] = d_new                        # rewrite what sequence 6 means
    partP[f"E2_{form}"]["reductions"] = {
        "v2_to_v3_re-registering_superseded_regex_for_seq_8": content_reductions(v2, v3r),
        "same_with_lowering_history": content_reductions(v2, v3r, history_subjects=[KEY]),
        "v2_to_v3_rewriting_sequence_6": content_reductions(v2, v3w),
        "pack_reductions_tool_on_projections_v2@7_vs_v3@8 (unmodified: blind to reversion)": C.run_reductions(project(v2, 7), project(v3r, 8), [], quiet=True)["exit"],
        "forged_mixed_at_seq_8_after_v3_reversion_declared": e7(k8_mixed, v3r, 8)["exit"],
    }
out["P_secret_pattern_retention"] = partP

# ------------------------------------------------------------------------------------------------ D-A02 breadth (T1-T4), shapes copied from synthesis D
SCHEMA = sorted(os.path.relpath(p, FW) for p in glob.glob(os.path.join(FW, "schemas/*.schema.json")))[0]
SKILL = sorted(os.path.relpath(p, FW) for p in glob.glob(os.path.join(FW, "skills/SKL-*.yaml")))[0]


def fix_tool(k):
    mut(k, "tools/registry/TOOLS.yaml", lambda d: [t.__setitem__("probe_fixed_note", "4.1.7 fix: health command hardened") for t in d["tools"] if t["tool_id"] == "TOOL-GIT-001"])


def fix_invariant(k):
    mut(k, "constitution/HARD_INVARIANTS.yaml", lambda d: [i.__setitem__("statement", str(i.get("statement", "")) + " (4.1.7 clarification)") for i in d["invariants"] if i["id"] == "INV-001"])


def fix_schema(k):
    p = os.path.join(k, SCHEMA)
    j = json.load(open(p))
    j["$comment"] = "4.1.7 fix: additionalProperties tightened"
    json.dump(j, open(p, "w"), indent=2)


def fix_skill(k):
    mut(k, SKILL, lambda d: d.__setitem__("probe_fixed_note", "4.1.7 fix: instruction corrected") if isinstance(d, dict) else None)


TARGETS = {
    "T1_tool_descriptor_member": {"fix": fix_tool, "match": lambda v: v.get("class") == "pinned" and "TOOL-GIT-001" in str(v.get("key"))},
    "T2_hard_invariant_member": {"fix": fix_invariant, "match": lambda v: v.get("class") == "pinned" and "INV-001" in str(v.get("key"))},
    "T3_schema_pinned_file": {"fix": fix_schema, "match": lambda v: v.get("class") == "pinned_file" and v.get("file") == SCHEMA},
    "T4_skill_pinned_file": {"fix": fix_skill, "match": lambda v: v.get("class") == "pinned_file" and v.get("file") == SKILL},
}
fixes = {}
for name, t in TARGETS.items():
    k = kcopy("fix-" + name, with_tools=True)
    t["fix"](k)
    v = [x for x in C.run_check(k, INV, quiet=True).get("violations", []) if t["match"](x)]
    fixes[name] = v[0] if v else None
k6t = kcopy("installed-4.1.6-with-tools", with_tools=True)
k7all = kcopy("all-fixed-4.1.7", with_tools=True)
for name in fixes:
    TARGETS[name]["fix"](k7all)
partD = {"fixed_digests_found": {n: bool(v) for n, v in fixes.items()}}
for form in ("open", "closed"):
    v2 = to_sequence_scoped(INV, [(6, OPEN)] if form == "open" else [(6, 6), (7, 7)])
    for name, viol in fixes.items():
        key = viol.get("key") or viol.get("file")
        for kind, holder, k in slots(v2):
            if k == key and kind != "members":
                old = holder["digests"][k][0]
                holder["digests_by_sequence"][k] = [{"from": 6, "to": 6, "digest": old}, {"from": 7, "to": OPEN if form == "open" else 7, "digest": viol["digest"]}]
    row = {"lint": lint_single_valued(v2)["exit"], "installed_4.1.6_at_6": e7(k6t, v2, 6)["exit"], "all_fixed_4.1.7_at_7": e7(k7all, v2, 7)["exit"], "mixed_releases_at_seq_8": {}}
    for name in fixes:
        km = kcopy(f"mix-{form}-" + name, with_tools=True)
        for other in fixes:
            if other != name:
                TARGETS[other]["fix"](km)
        row["mixed_releases_at_seq_8"][name] = e7(km, v2, 8)["exit"]
    partD[f"E2_{form}"] = row
out["D_A02_breadth"] = partD


# ------------------------------------------------------------------------------------------------ consumption on real 4.1.5 (copied from review r4 B, attribution above)
def gov(root, role, *a):
    r = subprocess.run([GOV, "--json", "--root", root, "--session", "S-ar10-f3", "--role", role, *a], env=ENV, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout[-400:], "stderr": r.stderr[-400:]}


def git(root, *a):
    subprocess.run(["git", "-c", "user.name=p", "-c", "user.email=p@x", *a], cwd=root, check=True, capture_output=True, env=ENV)


def rel_copy(name, kernel_mutator):
    d = os.path.join(S, "src", name)
    shutil.copytree(REL, d)
    kernel_mutator(os.path.join(d, "kernel"))
    return d


def db_paths(root, suffix):
    try:
        con = sqlite3.connect(root + "/.governance-runtime/state.db")
        ind = [x[0] for x in con.execute("select path from artifacts") if x[0].endswith(suffix)]
        return ind
    except sqlite3.Error as e:
        return f"db error {e}"


def consume(label, src, extra_files, marker_rel, marker):
    root = f"{S}/consumer-{label}"
    os.makedirs(root)
    git(root, "init", "-q")
    git(root, "commit", "-q", "--allow-empty", "-m", "i")
    init = gov(root, "orchestrator", "init", "--source", src, "--name", "ar10f3", "--skip-index")
    for rel, text in extra_files.items():
        os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
        open(os.path.join(root, rel), "w").write(text)
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "project material")
    trust = gov(root, "orchestrator", "kernel", "trust")
    rb = gov(root, "orchestrator", "rebuild-memory")
    q = gov(root, "orchestrator", "memory", "query", marker)
    hits = [h.get("path") for h in ((q.get("result") or {}).get("hits") or []) if (h.get("path") or "").endswith(marker_rel)]
    return {"init_ok": init.get("ok"), "kernel_trust_verified": (trust.get("result") or {}).get("verified"), "rebuild_ok": rb.get("ok"),
            "indexed": bool(db_paths(root, marker_rel)), "retrievable_by_default_query": bool(hits)}


SECRET = "ASIAQ3EGUH7X4MPLE2Z9"
FILES = {"product/notes/deploy.md": f"# Deploy notes AR10F3MARK\n\naws key used by the job: {SECRET}\n"}
selected = {
    "revision_4_RETAIN_selects_forged_4.1.8_mixed (E7 exit 0 above)": rel_copy("mixed", lambda k: set_patterns(k, OLD_RE, True)),
    "E2_refuses_forged_4.1.8; effective root stays the eligible 4.1.7 content": rel_copy("fixed", lambda k: set_patterns(k, NEW_RE, True)),
}
out["consumption_4_1_5"] = {label: consume(f"c{i}", src, FILES, "notes/deploy.md", "AR10F3MARK") for i, (label, src) in enumerate(selected.items())}

txt = json.dumps(out, indent=1, default=str)
txt = txt.replace(S, "<scratch>").replace(WT, "<worktree>").replace(os.path.dirname(GOV), "<legacy-bin>")
txt = re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad-path>", txt)
print(txt)
