#!/usr/bin/env python3
"""E4 (AR-0009, specialist A) — BC4-3: registration of non-orderable constitutional content as a FUNCTION of the release.

Executed with the pack's own checker and library (release/root-of-trust/4.1.6/constitutional-surface/csi_check.py,
csi_lib.py, draft TPS v1 inventory; loaded by path, unmodified) and the real legacy 4.1.5 binary as a stand-in consumer.

Mechanism under test (01-ALTERNATIVE.md §4). For every non-join unit u (a `pinned` leaf or whole member content, a
`pinned_file` path; the same rule covers migration files and owner-domain binding groups, evaluated in parts M and G):
  - the registration authority records entries (u, release_sequence, digest);
  - E7 judges a kernel carried by a release of sequence s against the digest the registration function gives for s;
  - variant CLOSED (proposal): only an entry whose release_sequence == s counts (every release is registered exactly);
  - variant OPEN (the "sequence range" reading CD4-3 also allows): the entry with the greatest release_sequence <= s.
The projection "registration function at s" is written into a copy of the inventory as a singleton digest list, and the
UNMODIFIED `run_check` judges the kernel. So the only thing this script adds is the projection; the checker is the pack's.

Parts
  P   reviewer B's RV4-B-A08 fixture (aws-access-key regex fix + new gcp member): fixed, mixed at a higher sequence, mixed at
      the fix's sequence, installed 4.1.6 retention, gap sequence, sequence inflation, stale Trust Policy machine.
  T   synthesis D's RV4-D-A02 targets T1-T4 (tool descriptor, hard invariant, schema file, skill file): mixed at 4.1.8-x.
  R   registration history rules: reversion (a later entry re-using a superseded digest) is a computed reduction; a rewrite
      of an existing entry makes the Trust Policy invalid.
  M   migration files as registered units (the root of RV4-M5's selector: release-final choosing migration content).
  G   owner-domain binding group for a hash-bound contract set (RV4-L10): Markdown v2 + compiled YAML v1.
  A   additive collection: an unregistered extra secret pattern with an invalid regex (can an addition weaken?).
  C   consumption on real 4.1.5: which content becomes effective under revision 4 (mixed) and under this proposal (the
      mixed release is ineligible; the effective kernel is the registered one), plus part A's kernel.

Environment: REVIEW_REPO (worktree), GOV (legacy 4.1.5), GOV_REVIEW_SCRATCH (scratch dir). GOV_* stripped from children;
HOME and GOV_KERNEL_CACHE in scratch. Output: JSON on stdout with scratch paths replaced.
"""
import copy, glob, hashlib, json, os, re, shutil, sqlite3, subprocess, sys, tempfile

import yaml

sys.dont_write_bytecode = True
REPO = os.environ["REVIEW_REPO"]
PACK = os.path.join(REPO, "release", "root-of-trust", "4.1.6")
CS = os.path.join(PACK, "constitutional-surface")
sys.path.insert(0, CS)
import csi_lib as L  # noqa: E402
import csi_check as C  # noqa: E402

GOV = os.environ["GOV"]
FW = os.path.join(REPO, "framework")
REL = os.path.join(REPO, "release", "releases", "4.1.5")
REL_TOOLS = os.path.join(REL, "kernel", "tools")
INV = yaml.safe_load(open(os.path.join(CS, "CONSTITUTIONAL_SURFACE_INVENTORY.yaml")))
S = tempfile.mkdtemp(prefix="e4-", dir=os.environ["GOV_REVIEW_SCRATCH"])
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GOV_")}
ENV.update(GOV_KERNEL_CACHE=S + "/cache", HOME=S + "/home")
os.makedirs(ENV["HOME"], exist_ok=True)
SEQ_416, SEQ_417, SEQ_GAP, SEQ_418X, SEQ_419, SEQ_INFLATED = 1600, 1700, 1650, 1800, 1900, 10 ** 9
out = {"probe": "E4 release-scoped registration (AR-0009)", "checker": "csi_check.run_check (revision 4, unmodified)",
       "binary": subprocess.run([GOV, "--version"], capture_output=True, text=True).stdout.strip()}


# ------------------------------------------------------------------------------------------------ kernel fixtures
def kcopy(name, with_tools=True):
    d = os.path.join(S, "k", name)
    shutil.copytree(FW, d)
    if with_tools and not os.path.exists(os.path.join(d, "tools")):
        shutil.copytree(REL_TOOLS, os.path.join(d, "tools"))
    return d


def ymut(kdir, rel, fn):
    p = os.path.join(kdir, rel)
    d = yaml.safe_load(open(p))
    fn(d)
    C.ydump(p, d)


KEY = "SECURITY_POLICY.secret_content_patterns[id=aws-access-key].regex"
OLD_RE, NEW_RE = "AKIA[0-9A-Z]{16}", "(AKIA|ASIA)[0-9A-Z]{16}"
GCP = {"id": "gcp-api-key", "regex": "AIza[0-9A-Za-z_\\-]{35}"}
GCP_KEY = f"SECURITY_POLICY.secret_content_patterns[id={GCP['id']}].regex"


def set_patterns(kdir, aws_re, with_member=True, extra=None):
    def f(d):
        for p in d["secret_content_patterns"]:
            if p["id"] == "aws-access-key":
                p["regex"] = aws_re
        if with_member and not any(p["id"] == GCP["id"] for p in d["secret_content_patterns"]):
            d["secret_content_patterns"].append(dict(GCP))
        if extra:
            d["secret_content_patterns"].append(dict(extra))
    ymut(kdir, "policies/SECURITY_POLICY.yaml", f)


SCHEMA = sorted(os.path.relpath(p, FW) for p in glob.glob(os.path.join(FW, "schemas/*.schema.json")))[0]
SKILL = sorted(os.path.relpath(p, FW) for p in glob.glob(os.path.join(FW, "skills/SKL-*.yaml")))[0]


# the four D-A02 fixes (copied from review-r4 D `RV4-D-A02-pinned-retention-breadth.py`, AR-0008, with attribution)
def fix_tool(k):
    ymut(k, "tools/registry/TOOLS.yaml", lambda d: [t.__setitem__("probe_fixed_note", "4.1.7 fix: health command hardened") for t in d["tools"] if t["tool_id"] == "TOOL-GIT-001"])


def fix_invariant(k):
    ymut(k, "constitution/HARD_INVARIANTS.yaml", lambda d: [i.__setitem__("statement", str(i.get("statement", "")) + " (4.1.7 clarification)") for i in d["invariants"] if i["id"] == "INV-001"])


def fix_schema(k):
    p = os.path.join(k, SCHEMA)
    j = json.load(open(p))
    j["$comment"] = "4.1.7 fix: additionalProperties tightened"
    json.dump(j, open(p, "w"), indent=2)


def fix_skill(k):
    ymut(k, SKILL, lambda d: d.__setitem__("probe_fixed_note", "4.1.7 fix: instruction corrected") if isinstance(d, dict) else None)


def fix_pattern(k):
    set_patterns(k, NEW_RE, with_member=True)


FIXES = {"P_aws_regex_and_gcp_member": fix_pattern, "T1_tool_descriptor_member": fix_tool, "T2_hard_invariant_member": fix_invariant,
         "T3_schema_pinned_file": fix_schema, "T4_skill_pinned_file": fix_skill}


# ------------------------------------------------------------------------------------------------ registration function
def units(inv):
    """Every non-join unit with a digest registration in the inventory: pinned leaves / member content, pinned files."""
    u = {}
    for fr in inv["files"]:
        if isinstance(fr.get("digests"), dict):
            for path, ds in fr["digests"].items():
                u[("file", path)] = list(ds)
        for lr in fr.get("leaves") or []:
            if isinstance(lr.get("digests"), dict):
                for key, ds in lr["digests"].items():
                    u[("leaf", key)] = list(ds)
    return u


def history_from_v1(inv):
    h, multi = {}, []
    for unit, ds in units(inv).items():
        if len(ds) != 1:
            multi.append([unit, ds])
        h[unit] = [{"sequence": SEQ_416, "digest": d} for d in ds]
    return h, multi


def register_release(h, seq, kdir, inv_for_digests):
    """A release registration lists EVERY unit's digest for that release (closed variant). The digest of a unit whose
    content changed is read from the pack checker's own violation report (as review-r4 D-A02 does)."""
    h = copy.deepcopy(h)
    r = C.run_check(kdir, inv_for_digests, quiet=True)
    changed = {}
    for v in r.get("violations", []):
        if v.get("class") == "pinned_file":
            changed[("file", v["file"])] = v["digest"]
        elif v.get("class") == "pinned":
            changed[("leaf", v["key"])] = v["digest"]
    for unit, entries in h.items():
        latest = max((e for e in entries if e["sequence"] <= seq), key=lambda e: e["sequence"])
        h[unit] = entries + [{"sequence": seq, "digest": changed.get(unit, latest["digest"])}]
    for unit, d in changed.items():
        if unit not in h:
            h[unit] = [{"sequence": seq, "digest": d}]
    return h, sorted([list(k) for k in changed])


def lookup(entries, s, mode):
    if mode == "union":  # mutant = revision 4: every digest ever registered for the unit, whatever the sequence
        return sorted({x["digest"] for x in entries})
    if mode == "latest":  # mutant: newest digest regardless of the release's own sequence
        return [max(entries, key=lambda x: x["sequence"])["digest"]] if entries else []
    if mode == "closed":
        e = [x for x in entries if x["sequence"] == s]
    else:
        e = [x for x in entries if x["sequence"] <= s]
        e = [max(e, key=lambda x: x["sequence"])] if e else []
    return [e[0]["digest"]] if e else []


def project(inv, h, s, mode, extra_members=()):
    inv = copy.deepcopy(inv)
    known = set()
    for fr in inv["files"]:
        if isinstance(fr.get("digests"), dict):
            for path in list(fr["digests"]):
                fr["digests"][path] = lookup(h.get(("file", path), []), s, mode)
                known.add(("file", path))
        for lr in fr.get("leaves") or []:
            if isinstance(lr.get("digests"), dict):
                for key in list(lr["digests"]):
                    lr["digests"][key] = lookup(h.get(("leaf", key), []), s, mode)
                    known.add(("leaf", key))
    # units registered by a later release that the v1 draft has no rule for (the new gcp member)
    for unit, entries in h.items():
        if unit in known or unit[0] != "leaf":
            continue
        ds = lookup(entries, s, mode)
        if not ds:
            continue
        fr = next(f for f in inv["files"] if f.get("path") == "policies/SECURITY_POLICY.yaml")
        fr["leaves"].append({"key": unit[1], "class": "pinned", "note": "registered member content (release registration)", "digests": {unit[1]: ds}})
        for lr in fr["leaves"]:
            if lr["key"] == "SECURITY_POLICY.secret_content_patterns[id]#members":
                lr["registered"] = sorted(set(lr["registered"]) | set(extra_members))
    return inv


def judge(kdir, h, s, mode, inv=INV, extra_members=()):
    r = C.run_check(kdir, project(inv, h, s, mode, extra_members), quiet=True)
    return {"exit": r["exit"], "violations": [str(v)[:160] for v in r.get("violations", [])[:4]], "violation_count": len(r.get("violations", []))}


def registration_changes(h_old, h_new):
    """Rules R-REG-4/5: entries are append-only (a changed or removed entry = REGISTRATION_REWRITE, Trust Policy invalid);
    a new entry whose digest equals an earlier digest of the same unit that a later entry superseded = computed reduction."""
    rewrites, reversions = [], []
    for unit, old in h_old.items():
        new = h_new.get(unit, [])
        if any(e not in new for e in old):
            rewrites.append(list(unit))
    for unit, new in h_new.items():
        old = h_old.get(unit, [])
        for e in [x for x in new if x not in old]:
            earlier = sorted([x for x in new if x["sequence"] < e["sequence"]], key=lambda x: x["sequence"])
            if earlier and e["digest"] != earlier[-1]["digest"] and e["digest"] in {x["digest"] for x in earlier[:-1]}:
                reversions.append({"unit": list(unit), "sequence": e["sequence"], "digest": e["digest"]})
    return {"REGISTRATION_REWRITE": rewrites, "computed_reductions_registration_reversion": reversions}


# ================================================================================================ build histories
H1, multi = history_from_v1(INV)
out["draft_v1_units"] = {"count": len(H1), "units_with_more_than_one_registered_digest": multi}
k_fixed_all = kcopy("fixed-all")
for fn in FIXES.values():
    fn(k_fixed_all)
H2, changed_417 = register_release(H1, SEQ_417, k_fixed_all, INV)
# a new member of the additive collection is not a violation under v1 (covered_by_collection), so the release
# registration records its content explicitly, as reviewer B's TPS v2 did
H2[("leaf", GCP_KEY)] = [{"sequence": SEQ_417, "digest": L.vdigest(GCP["regex"])}]
changed_417.append(["leaf", GCP_KEY])
out["release_4.1.7_registration"] = {"sequence": SEQ_417, "changed_units": changed_417}

# ================================================================================================ part P
k_mixed = kcopy("P-mixed")  # 4.1.8-x: every other fix, old aws regex, new gcp member
for name, fn in FIXES.items():
    if name != "P_aws_regex_and_gcp_member":
        fn(k_mixed)
set_patterns(k_mixed, OLD_RE, with_member=True)
k_416 = kcopy("installed-4.1.6")
EM = (GCP["id"],)
partP = {
    "fixed_4.1.7_at_1700": {m: judge(k_fixed_all, H2, SEQ_417, m, extra_members=EM) for m in ("closed", "open")},
    "mixed_4.1.8x_at_1800": {m: judge(k_mixed, H2, SEQ_418X, m, extra_members=EM) for m in ("closed", "open")},
    "mixed_at_fix_sequence_1700": {m: judge(k_mixed, H2, SEQ_417, m, extra_members=EM) for m in ("closed", "open")},
    "installed_4.1.6_at_1600_under_registration_v2 (legitimate retention)": {m: judge(k_416, H2, SEQ_416, m, extra_members=EM) for m in ("closed", "open")},
    "mixed_at_gap_1650": {m: judge(k_mixed, H2, SEQ_GAP, m, extra_members=EM) for m in ("closed", "open")},
    "4.1.6_content_at_gap_1650 (forged unregistered sequence below the fix)": {m: judge(k_416, H2, SEQ_GAP, m, extra_members=EM) for m in ("closed", "open")},
    "4.1.6_content_at_1800 (superseded content at a higher sequence)": {m: judge(k_416, H2, SEQ_418X, m, extra_members=EM) for m in ("closed", "open")},
    "stale_machine_holding_only_v1: 4.1.6_content_at_1800": {m: judge(k_416, H1, SEQ_418X, m) for m in ("closed", "open")},
    "fixed_at_inflated_sequence_1e9": {m: judge(k_fixed_all, H2, SEQ_INFLATED, m, extra_members=EM) for m in ("closed", "open")},
    "stale_machine_holding_only_v1: mixed_at_1800": {m: judge(k_mixed, H1, SEQ_418X, m) for m in ("closed", "open")},
    "stale_machine_holding_only_v1: 4.1.6_at_1600": {m: judge(k_416, H1, SEQ_416, m) for m in ("closed", "open")},
}
# revision-4 baseline on the same fixtures (retaining TPS: both digests listed)
inv_retain = copy.deepcopy(INV)
for fr in inv_retain["files"]:
    if isinstance(fr.get("digests"), dict):
        for path in fr["digests"]:
            fr["digests"][path] = sorted({e["digest"] for e in H2.get(("file", path), [])})
    for lr in fr.get("leaves") or []:
        if isinstance(lr.get("digests"), dict):
            for key in lr["digests"]:
                lr["digests"][key] = sorted({e["digest"] for e in H2.get(("leaf", key), [])})
fr_sec = next(f for f in inv_retain["files"] if f.get("path") == "policies/SECURITY_POLICY.yaml")
fr_sec["leaves"].append({"key": GCP_KEY, "class": "pinned", "digests": {GCP_KEY: sorted({e["digest"] for e in H2[("leaf", GCP_KEY)]})}})
for lr in fr_sec["leaves"]:
    if lr["key"] == "SECURITY_POLICY.secret_content_patterns[id]#members":
        lr["registered"] = sorted(set(lr["registered"]) | {GCP["id"]})
partP["revision4_baseline_retaining_TPS: mixed kernel"] = {"exit": C.run_check(k_mixed, inv_retain, quiet=True)["exit"]}
partP["revision4_baseline_retaining_TPS: fixed kernel"] = {"exit": C.run_check(k_fixed_all, inv_retain, quiet=True)["exit"]}
out["P_pattern_fixture"] = partP

# ================================================================================================ part T
partT = {}
for name in ("T1_tool_descriptor_member", "T2_hard_invariant_member", "T3_schema_pinned_file", "T4_skill_pinned_file"):
    k = kcopy("T-mix-" + name)
    for other, fn in FIXES.items():
        if other != name:
            fn(k)
    partT[name] = {"revision4_retaining_TPS": C.run_check(k, inv_retain, quiet=True)["exit"],
                   "proposal_closed_at_1800": judge(k, H2, SEQ_418X, "closed", extra_members=EM)["exit"],
                   "proposal_open_at_1800": judge(k, H2, SEQ_418X, "open", extra_members=EM)["exit"],
                   "proposal_closed_at_1700": judge(k, H2, SEQ_417, "closed", extra_members=EM)["exit"]}
out["T_D_A02_targets"] = partT

# ================================================================================================ part R
H3_rev = copy.deepcopy(H2)
H3_rev[("leaf", KEY)].append({"sequence": SEQ_419, "digest": L.vdigest(OLD_RE)})
H3_rw = copy.deepcopy(H2)
for e in H3_rw[("leaf", KEY)]:
    if e["sequence"] == SEQ_417:
        e["digest"] = L.vdigest(OLD_RE)
out["R_history_rules"] = {"v2_to_v3_reversion_of_aws_regex": registration_changes(H2, H3_rev),
                          "v2_to_v3_rewrite_of_1700_entry": registration_changes(H2, H3_rw),
                          "v1_to_v2_ordinary_release": registration_changes(H1, H2)}

# ================================================================================================ part M (migrations)
def migration_digest(text):
    return "sha256:" + hashlib.sha256(text.encode()).hexdigest()


M_OK = "id: M-017\nfrom_version: 4.1.6\nto_version: 4.1.7\noperations:\n  - {op: note, text: tighten template}\n"
M_WEAK = "id: M-017\nfrom_version: 4.1.6\nto_version: 4.1.7\noperations:\n  - {op: set_overlay_key, file: REPOSITORY_CONTRACT.yaml, key: paths, value: [{pattern: '**/.env*', index: true}]}\n"
HM = {("file", "migrations/M-017.yaml"): [{"sequence": SEQ_417, "digest": migration_digest(M_OK)}]}
out["M_migration_units"] = {
    "release_4.1.8x_carries_weaker_M-017_closed": "refused (unregistered)" if migration_digest(M_WEAK) not in [e["digest"] for e in HM[("file", "migrations/M-017.yaml")] if e["sequence"] == SEQ_418X] else "accepted",
    "release_4.1.8x_carries_weaker_M-017_open": "refused (digest differs from registered)" if lookup(HM[("file", "migrations/M-017.yaml")], SEQ_418X, "open") != [migration_digest(M_WEAK)] else "accepted",
    "release_4.1.7_carries_registered_M-017": "accepted" if lookup(HM[("file", "migrations/M-017.yaml")], SEQ_417, "closed") == [migration_digest(M_OK)] else "refused",
    "note": "the pack checker does not pin transaction_input digests (it checks operations only); this part applies the same registration function to migration files",
}

# ================================================================================================ part G (owner-domain binding group)
md_v1, md_v2, y_v1, y_v2 = (migration_digest(x) for x in ("contract v1", "contract v2", "compiled v1", "compiled v2"))
def group_digest(members):
    return "sha256:" + hashlib.sha256(json.dumps(sorted(members.items()), separators=(",", ":")).encode()).hexdigest()
confirmed_groups = {group_digest({"CONTRACT.md": md_v1, "CONTRACT.yaml": y_v1}), group_digest({"CONTRACT.md": md_v2, "CONTRACT.yaml": y_v2})}
per_path_pins = {"CONTRACT.md": {md_v1, md_v2}, "CONTRACT.yaml": {y_v1, y_v2}}
present = {"CONTRACT.md": md_v2, "CONTRACT.yaml": y_v1}
out["G_owner_domain_contract_set"] = {
    "present_set": "Markdown v2 + compiled YAML v1",
    "revision4_per_path_slots_with_two_valid_pins": "accepted" if all(present[p] in per_path_pins[p] for p in present) else "refused",
    "proposal_binding_group": "accepted" if group_digest(present) in confirmed_groups else "refused (OWNER_CONSTITUTIONAL_GROUP_UNCONFIRMED)",
}

# ================================================================================================ part A (additive member)
k_add = kcopy("A-invalid-extra-pattern")
for fn in FIXES.values():
    fn(k_add)
set_patterns(k_add, NEW_RE, with_member=True, extra={"id": "zz-invalid", "regex": "(?=lookahead-unsupported"})
out["A_additive_unregistered_member"] = {
    "checker_closed_at_1700": judge(k_add, H2, SEQ_417, "closed", extra_members=EM)["exit"],
    "runtime_pattern_compilation": [l.strip() for l in open(os.path.join(REPO, "runtime/src/security/secrets.rs")) if "Regex::new" in l],
}


# ================================================================================================ part C (consumption on 4.1.5)
def gov(root, role, *a):
    r = subprocess.run([GOV, "--json", "--root", root, "--session", "S-e4", "--role", role, *a], env=ENV, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout[-300:], "stderr": r.stderr[-300:]}


def git(root, *a):
    subprocess.run(["git", "-c", "user.name=p", "-c", "user.email=p@x", *a], cwd=root, check=True, capture_output=True)


SECRET = "ASIAQ3EGUH7X4MPLE2Z9"


def consume(label, mutate):
    src = os.path.join(S, "src", label)
    shutil.copytree(REL, src)
    mutate(os.path.join(src, "kernel"))
    root = os.path.join(S, "consumer-" + label)
    os.makedirs(root)
    git(root, "init", "-q")
    git(root, "commit", "-q", "--allow-empty", "-m", "i")
    init = gov(root, "orchestrator", "init", "--source", src, "--name", "e4", "--skip-index")
    os.makedirs(os.path.join(root, "product/notes"), exist_ok=True)
    open(os.path.join(root, "product/notes/deploy.md"), "w").write(f"# Deploy notes E4SECRETMARK\n\naws key used by the job: {SECRET}\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "material")
    trust = gov(root, "orchestrator", "kernel", "trust")
    rb = gov(root, "orchestrator", "rebuild-memory")
    con = sqlite3.connect(os.path.join(root, ".governance-runtime/state.db"))
    indexed = [x[0] for x in con.execute("select path from artifacts") if x[0].endswith("notes/deploy.md")]
    q = gov(root, "orchestrator", "memory", "query", "E4SECRETMARK")
    hits = [h.get("path") for h in ((q.get("result") or {}).get("hits") or []) if (h.get("path") or "").endswith("notes/deploy.md")]
    return {"init_ok": init.get("ok"), "kernel_trust_verified": (trust.get("result") or {}).get("verified"), "rebuild_ok": rb.get("ok"),
            "secret_file_indexed": bool(indexed), "secret_file_retrievable": bool(hits)}


c_mixed = consume("effective-under-revision4-mixed", lambda k: set_patterns(k, OLD_RE, with_member=True))
c_fixed = consume("effective-under-proposal-registered", lambda k: set_patterns(k, NEW_RE, with_member=True))
c_add = consume("additive-invalid-extra-pattern", lambda k: set_patterns(k, NEW_RE, with_member=True, extra={"id": "zz-invalid", "regex": "(?=lookahead-unsupported"}))
out["C_consumption_4.1.5"] = {
    "revision4: mixed 4.1.8-x is eligible under a retaining TPS, so its content is effective": c_mixed,
    "proposal: mixed 4.1.8-x is ineligible; the effective content is the content registered for the running release (fixed)": c_fixed,
    "additive unregistered member with an invalid regex (does an addition weaken?)": c_add,
}

# ================================================================================================ lookup-rule mutants
VEC = {
    "fixed_4.1.7_at_1700": (k_fixed_all, H2, SEQ_417, True),
    "mixed_4.1.8x_at_1800": (k_mixed, H2, SEQ_418X, False),
    "installed_4.1.6_at_1600": (k_416, H2, SEQ_416, True),
    "4.1.6_content_at_1800": (k_416, H2, SEQ_418X, False),
    "4.1.6_content_at_gap_1650": (k_416, H2, SEQ_GAP, False),
    "fixed_at_inflated_1e9": (k_fixed_all, H2, SEQ_INFLATED, False),
}
vec_mode = {}
for m in ("closed", "open", "union", "latest"):
    vec_mode[m] = {name: judge(k, h, s_, m, extra_members=EM)["exit"] for name, (k, h, s_, _) in VEC.items()}
out["lookup_mutants"] = {
    "expected_eligible": {name: v[3] for name, v in VEC.items()},
    "exits_by_rule": vec_mode,
    "rule_matches_expectation": {m: all((vec_mode[m][n] == 0) == VEC[n][3] for n in VEC) for m in vec_mode},
    "note": "closed = proposal; open = sequence-range reading; union = revision 4 (retaining TPS); latest = ignores the release's own sequence",
}

# ================================================================================================ verdicts
cl = lambda row: row["closed"]["exit"]
op = lambda row: row["open"]["exit"]
out["verdicts"] = {
    "revision4_baseline_mixed_eligible": partP["revision4_baseline_retaining_TPS: mixed kernel"]["exit"] == 0,
    "proposal_closed_refuses_mixed_at_higher_sequence": cl(partP["mixed_4.1.8x_at_1800"]) == 3,
    "proposal_open_refuses_mixed_at_higher_sequence": op(partP["mixed_4.1.8x_at_1800"]) == 3,
    "proposal_refuses_mixed_at_fix_sequence": cl(partP["mixed_at_fix_sequence_1700"]) == 3 and op(partP["mixed_at_fix_sequence_1700"]) == 3,
    "legitimate_retention_4.1.6_at_own_sequence_eligible": cl(partP["installed_4.1.6_at_1600_under_registration_v2 (legitimate retention)"]) == 0 and op(partP["installed_4.1.6_at_1600_under_registration_v2 (legitimate retention)"]) == 0,
    "mixed_kernel_at_gap_1650 [closed, open]": [cl(partP["mixed_at_gap_1650"]), op(partP["mixed_at_gap_1650"])],
    "4.1.6_content_at_gap_1650 [closed, open] (open admits content equal to installed 4.1.6)": [cl(partP["4.1.6_content_at_gap_1650 (forged unregistered sequence below the fix)"]), op(partP["4.1.6_content_at_gap_1650 (forged unregistered sequence below the fix)"])],
    "4.1.6_content_at_1800 [closed, open] (RV4-H3 shape with every unit superseded)": [cl(partP["4.1.6_content_at_1800 (superseded content at a higher sequence)"]), op(partP["4.1.6_content_at_1800 (superseded content at a higher sequence)"])],
    "stale_v1_machine_4.1.6_content_at_1800 [closed, open] (open = RS-1 equivalent)": [cl(partP["stale_machine_holding_only_v1: 4.1.6_content_at_1800"]), op(partP["stale_machine_holding_only_v1: 4.1.6_content_at_1800"])],
    "inflated_sequence_fixed_content [closed, open]": [cl(partP["fixed_at_inflated_sequence_1e9"]), op(partP["fixed_at_inflated_sequence_1e9"])],
    "stale_v1_machine_mixed_kernel_at_1800 [closed, open]": [cl(partP["stale_machine_holding_only_v1: mixed_at_1800"]), op(partP["stale_machine_holding_only_v1: mixed_at_1800"])],
    "D_A02_T1_T4_revision4_retaining_all_exit_0": all(v["revision4_retaining_TPS"] == 0 for v in partT.values()),
    "D_A02_T1_T4_proposal_closed_all_refused": all(v["proposal_closed_at_1800"] == 3 for v in partT.values()),
    "D_A02_T1_T4_proposal_open_all_refused": all(v["proposal_open_at_1800"] == 3 for v in partT.values()),
    "reversion_reported_as_computed_reduction": bool(out["R_history_rules"]["v2_to_v3_reversion_of_aws_regex"]["computed_reductions_registration_reversion"]),
    "rewrite_detected": bool(out["R_history_rules"]["v2_to_v3_rewrite_of_1700_entry"]["REGISTRATION_REWRITE"]),
    "ordinary_release_no_rewrite_no_reversion": not any(out["R_history_rules"]["v1_to_v2_ordinary_release"].values()),
    "consumption_revision4_mixed_indexes_secret": c_mixed["secret_file_indexed"],
    "consumption_proposal_effective_excludes_secret": not c_fixed["secret_file_indexed"],
    "additive_invalid_pattern_does_not_disable_other_patterns": not c_add["secret_file_indexed"],
}
txt = json.dumps(out, indent=1, default=str).replace(S, "<scratch>").replace(REPO, "<worktree>").replace(os.path.dirname(GOV), "<legacy-bin>")
print(re.sub(r"/tmp/claude-1000/[^\"\s]*", "<scratchpad-path>", txt))
