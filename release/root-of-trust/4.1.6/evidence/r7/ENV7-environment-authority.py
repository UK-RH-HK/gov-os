#!/usr/bin/env python3
"""ENV7 — the environment manifest authority of CP-1 against reviewer B's environment attacks (BC6-3: RV6-H3) (AR-0019).
Executed (real Rust toolchain, system C compiler, Ed25519) + computed (CS7). Scratch only.

The revision-7 ceremony (`33` R-BENV-1″…R-BENV-9″), implemented here as the reference the implementation must match:
  * The environment LOCK is registered source content (`release/build/ENVIRONMENT_LOCK.json`): per target and supplier: components
    {name, version, sha256, placement_path, mode}. There is no recipe, no inline content and no key reference (schema: additional
    properties refused).
  * The environment MANIFEST is derived by gov-envmanifest/1 from the lock, the root-signed supplier registry and the measured bytes.
    Every field is a function of those inputs; `checksum_key_id` is the pinned registry key that verified the component's checksum
    file. A proposal that differs from the derivation is refused (ENVIRONMENT_MANIFEST_NOT_DERIVED).
  * Assembly (gov-envassemble/1) places component bytes only; any other operation is ENVIRONMENT_ASSEMBLY_NONCONFORMANT.
  * Two environment reproductions (of three) must derive and assemble identically; the registration names the exact environment_id.
  * Supplier-class independence is computed from provenance (base image lineage, package source, build system, signing infrastructure),
    pinned key sets and component digests; toolchain-lineage independence from provenance. Labels are never compared.
  * Acceptance counts matching binary reproductions across two independent supplier classes and two independent toolchain lineages;
    any conflicting reproduction refuses.

Attacks re-run (reviewer B RV6-B-A02, AR-0016; environment and build construction after B's probe and the architect's ENV6, re-typed):
  A07a recipe with inline content; A07b pipeline-proposed placement of genuinely signed instrumented artefacts; A07c both classes carrying
  the same author's injection; A08 two labels over one compromised supplier; A09 a checksum key named by the manifest; plus T1 upstream
  binary toolchain lineage compromised, T2 a relabelled toolchain lineage, T3 both lineages compromised (stated residual).
  Honesty note: only one real rustc is available, so toolchain lineages are registry entries and a compromised lineage is emulated by
  a linker argument injected for that lineage's builds; diverse double-compilation over two real bootstrap chains is not executed here
  (certification criterion CC-3 requires it on the implementation).
Environment: SCRATCH, ENV7_TOOLCHAIN (default ~/.rustup stable), ENV7_ACCOUNT_HOME (read-only toolchain). Output: JSON on stdout.
"""
import base64, hashlib, importlib.util, json, os, stat, subprocess, sys, tempfile

sys.dont_write_bytecode = True
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = tempfile.mkdtemp(prefix="env7-", dir=os.environ["SCRATCH"])
ACCOUNT_HOME = os.environ["ENV7_ACCOUNT_HOME"]  # the account home that holds the Rust toolchain (required)
TOOLCHAIN = os.environ.get("ENV7_TOOLCHAIN", ACCOUNT_HOME + "/.rustup/toolchains/stable-x86_64-unknown-linux-gnu")
RUSTC = TOOLCHAIN + "/bin/rustc"
W = BASE + "/work"
for d in (W, W + "/home", W + "/tmp"):
    os.makedirs(d, exist_ok=True)
_r = subprocess.run([RUSTC, "--version"], env={"PATH": "/usr/bin:/bin", "HOME": W + "/home", "TMPDIR": W + "/tmp"}, capture_output=True, text=True)
RUSTC_HOME = W + "/home" if _r.returncode == 0 else ACCOUNT_HOME


def cenv(**kw):
    e = {"PATH": "/usr/bin:/bin", "HOME": RUSTC_HOME, "TMPDIR": W + "/tmp", "PYTHONDONTWRITEBYTECODE": "1"}
    e.update(kw)
    return {k: v for k, v in e.items() if not k.startswith("GOV_")}


def H(b):
    return hashlib.sha256(b).hexdigest()


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":")).encode()


def keypair(label):
    sk = Ed25519PrivateKey.from_private_bytes(hashlib.sha256(label.encode()).digest())
    return sk, sk.public_key()


def kid(pk):
    from cryptography.hazmat.primitives import serialization
    return "ed25519:" + H(pk.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw))


SRC = 'fn main() {\n    println!("gov: genuine behaviour");\n}\n'
open(W + "/inject.c", "w").write('#include <unistd.h>\n__attribute__((constructor)) static void env7_inject(void) { write(1, "INJECTED\\n", 9); }\n')
subprocess.run(["/usr/bin/cc", "-c", "-O2", "-fno-ident", "-o", W + "/inject.o", W + "/inject.c"], env=cenv(), check=True, capture_output=True)
INJECT_O = open(W + "/inject.o", "rb").read()
open(W + "/prof.c", "w").write('#include <unistd.h>\n__attribute__((constructor)) static void env7_prof(void) { write(1, "INSTRUMENTED\\n", 13); }\n')
subprocess.run(["/usr/bin/cc", "-c", "-O2", "-fno-ident", "-o", W + "/prof.o", W + "/prof.c"], env=cenv(), check=True, capture_output=True)
PROF_O = open(W + "/prof.o", "rb").read()


def cc_wrapper(extra=""):
    return ("#!/bin/sh\nexec /usr/bin/cc \"$@\" %s\n" % extra).encode()


def upstream(sid, compromised=False, key_label=None):
    arts = {"cc-plain": cc_wrapper(), "cc-instrumented": cc_wrapper("\"${0%/*}/../lib/instrument.o\""), "instrument.o": PROF_O, "SUPPLIER": ("%s\n" % sid).encode()}
    if compromised:
        arts["cc-plain"] = cc_wrapper("\"${0%/*}/../lib/inject.o\"")
        arts["inject.o"] = INJECT_O
    sums = "".join("%s  %s\n" % (H(b), n) for n, b in sorted(arts.items())).encode()
    sk, pk = keypair(key_label or ("upstream:" + sid))
    return {"sid": sid, "arts": arts, "sums": sums, "sig": sk.sign(sums), "pk": pk}


def mirror(*ups):
    m = {}
    for u in ups:
        for b in u["arts"].values():
            m[H(b)] = b
        m[H(u["sums"])] = u["sums"]
    return m


# ---- root-signed supplier and toolchain registries (Trust Policy, root threshold) -----------------------------------------------
UP_A, UP_B = upstream("distA"), upstream("distB")
UP_A_BAD = upstream("distA", compromised=True)
REGISTRY = {
    "sup-A": {"provenance": {"base_image_lineage": "debian-bookworm-images", "package_source": "deb.debian.org", "build_system": "debian-buildd", "signing_infrastructure": "debian-archive-keyring"}, "keys": {kid(UP_A["pk"]): UP_A["pk"]}},
    "sup-B": {"provenance": {"base_image_lineage": "alpine-3.20-images", "package_source": "dl-cdn.alpinelinux.org", "build_system": "alpine-builders", "signing_infrastructure": "alpine-keys"}, "keys": {kid(UP_B["pk"]): UP_B["pk"]}},
    "sup-A-mirror": {"provenance": {"base_image_lineage": "debian-bookworm-images", "package_source": "mirror.example.invalid/debian", "build_system": "debian-buildd", "signing_infrastructure": "debian-archive-keyring"}, "keys": {kid(UP_A["pk"]): UP_A["pk"]}},
}
TOOLCHAINS = {"tc-up": {"bootstrap_root": "upstream-binary-stage0", "package_source": "static.rust-lang.org", "build_system": "rust-ci", "signing_infrastructure": "rust-release-key"},
              "tc-boot": {"bootstrap_root": "mrustc-source-bootstrap", "package_source": "owner-source-mirror", "build_system": "owner-bootstrap-builders", "signing_infrastructure": "owner-registration-quorum"},
              "tc-up-relabelled": {"bootstrap_root": "upstream-binary-stage0", "package_source": "static.rust-lang.org", "build_system": "rust-ci", "signing_infrastructure": "rust-release-key"}}
LOCK_FIELDS = {"name", "version", "sha256", "placement_path", "mode"}


def lock_entry(u, supplier_id, mapping):
    return {"supplier_id": supplier_id, "target": "x86_64-unknown-linux-musl",
            "components": [{"name": n, "version": "1", "sha256": H(u["arts"][n]), "placement_path": p, "mode": 0o755 if p.startswith("bin/") else 0o644} for p, n in sorted(mapping.items())]}


PLAIN = {"bin/cc": "cc-plain", "share/SUPPLIER": "SUPPLIER"}
PLAIN_BAD = {"bin/cc": "cc-plain", "share/SUPPLIER": "SUPPLIER", "lib/inject.o": "inject.o"}
INSTR = {"bin/cc": "cc-instrumented", "share/SUPPLIER": "SUPPLIER", "lib/instrument.o": "instrument.o"}
_seq = [0]


def tdir(prefix):
    _seq[0] += 1
    d = "%s/%s-%d" % (W, prefix, _seq[0])
    os.makedirs(d)
    return d


def tree_digest(d):
    lines = []
    for root, _, files in os.walk(d):
        for f in files:
            p = os.path.join(root, f)
            lines.append("%s\t%o\t%s\n" % (os.path.relpath(p, d), stat.S_IMODE(os.stat(p).st_mode), H(open(p, "rb").read())))
    return H("".join(sorted(lines)).encode())


def verify_component(entry, comp, mir, sums_published, key_source):
    """R-BENV-1″: the component's digest is listed in a checksum file whose signature verifies under a key PINNED for the lock entry's
    supplier in the registry (key_source 'pinned'); revision-6 shape: under the key a manifest names (key_source 'named')."""
    for sums, sig, pk in sums_published:
        listed = {l.split("  ")[0] for l in sums.decode().strip().split("\n")}
        if comp["sha256"] not in listed:
            continue
        candidates = REGISTRY[entry["supplier_id"]]["keys"].items() if key_source == "pinned" else [(kid(pk), pk)]
        for k, pub in candidates:
            try:
                pub.verify(sig, sums)
                return k, H(sums)
            except Exception:
                continue
    return None, None


def derive_manifest(entry, mir, sums_published, key_source="pinned"):
    """gov-envmanifest/1: every field a function of the lock entry, the registry and the measured bytes."""
    if set(entry) - {"supplier_id", "target", "components"} or any(set(c) != LOCK_FIELDS for c in entry["components"]):
        return None, "ENVIRONMENT_ASSEMBLY_NONCONFORMANT"
    comps = []
    for c in entry["components"]:
        b = mir.get(c["sha256"])
        if b is None or H(b) != c["sha256"]:
            return None, "INPUT_DIGEST_MISMATCH"
        k, sd = verify_component(entry, c, mir, sums_published, key_source)
        if k is None:
            return None, "ENVIRONMENT_COMPONENT_UNVERIFIED"
        comps.append(dict(c, checksum_key_id=k, checksum_file_digest=sd))
    d = tdir("env")
    for c in comps:
        fp = os.path.join(d, c["placement_path"])
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        open(fp, "wb").write(mir[c["sha256"]])
        os.chmod(fp, c["mode"])
    m = {"schema": "governance-os.environment-manifest/2", "target": entry["target"], "supplier_id": entry["supplier_id"], "lock_digest": H(canon(entry)), "components": comps,
         "assembly_function": "gov-envassemble/1", "environment_tree_digest": tree_digest(d)}
    return {"manifest": m, "environment_id": H(canon(m)), "tree": d}, None


def ceremony(entry_in_source, proposal, mir, sums_published, key_source="pinned"):
    """Two environment reproducers and each registration custodian derive the manifest from the lock in the registered source; the
    proposal must equal it; the two derivations must agree."""
    runs = [derive_manifest(entry_in_source, mir, sums_published, key_source) for _ in range(2)]
    for r, err in runs:
        if err:
            return {"result": err}
    ids = {r["environment_id"] for r, _ in runs}
    if len(ids) != 1:
        return {"result": "ENVIRONMENT_REPRODUCTION_CONFLICT"}
    eid = ids.pop()
    if proposal is not None and H(canon(proposal)) != eid:
        return {"result": "ENVIRONMENT_MANIFEST_NOT_DERIVED"}
    return {"result": "REGISTERED", "environment_id": eid, "tree": runs[0][0]["tree"], "supplier_id": entry_in_source["supplier_id"]}


def independent(ids, table, attrs, keys=None):
    ids = sorted(set(ids))
    for a in range(len(ids)):
        for b in range(a + 1, len(ids)):
            pa, pb = table[ids[a]], table[ids[b]]
            if all(pa[k] != pb[k] for k in attrs) and (keys is None or not (set(keys[ids[a]]) & set(keys[ids[b]]))):
                return True
    return False


SUP_ATTRS = ("base_image_lineage", "package_source", "build_system", "signing_infrastructure")
TC_ATTRS = ("bootstrap_root", "package_source", "build_system", "signing_infrastructure")


def build(label, env_tree, tc_id, compromised_tcs=()):
    wd = tdir("build-" + label)
    os.makedirs(wd + "/src")
    open(wd + "/src/main.rs", "w").write(SRC)
    outp = wd + "/gov"
    cmd = [RUSTC, "--edition", "2021", "-C", "opt-level=2", "-C", "codegen-units=1", "-C", "debuginfo=0", "-C", "strip=symbols", "-C", "linker=" + env_tree + "/bin/cc",
           "--remap-path-prefix", wd + "=/build", "--remap-path-prefix", env_tree + "=/env", "-C", "link-arg=-Wl,--build-id=none", "-o", outp, wd + "/src/main.rs"]
    if tc_id in compromised_tcs:
        cmd[1:1] = ["-C", "link-arg=" + W + "/inject.o"]
    r = subprocess.run(cmd, env=cenv(PATH=env_tree + "/bin:/usr/bin:/bin"), capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        return {"status": "BUILD_FAILED", "stderr": r.stderr[-300:]}
    b = open(outp, "rb").read()
    run = subprocess.run([outp], capture_output=True, text=True, env={"PATH": "/usr/bin:/bin"}, timeout=10)
    return {"status": "OK", "digest": H(b), "stdout": run.stdout.strip().splitlines()}


def acceptance(envs, toolchains, compromised_tcs=(), by_label=False, reproducers=("rep1", "rep2")):
    """Every reproducer builds in every (registered environment, registered toolchain) pair; acceptance needs one digest from >= 2
    reproducers, the pairs spanning two independent supplier classes and two independent toolchain lineages, and no conflict."""
    rows = []
    for rp in reproducers:
        for e in envs:
            for tc in toolchains:
                b = build("%s-%s-%s" % (rp, e["supplier_id"], tc), e["tree"], tc, compromised_tcs)
                rows.append(dict(b, reproducer=rp, supplier=e["supplier_id"], toolchain=tc))
    ok = [r for r in rows if r["status"] == "OK"]
    digests = {r["digest"] for r in ok}
    summary = {"builds": len(rows), "distinct_digests": len(digests), "stdout": sorted({" | ".join(r["stdout"]) for r in ok})}
    if len(digests) != 1:
        return dict(summary, result="REPRODUCTION_CONFLICT")
    sups = {e["supplier_id"] for e in envs}
    if not (len(sups) >= 2 if by_label else independent(sups, {k: v["provenance"] for k, v in REGISTRY.items()}, SUP_ATTRS, {k: list(v["keys"]) for k, v in REGISTRY.items()})):
        return dict(summary, result="ENVIRONMENT_DIVERSITY_NOT_MET")
    if not (len(set(toolchains)) >= 2 if by_label else independent(toolchains, TOOLCHAINS, TC_ATTRS)):
        return dict(summary, result="TOOLCHAIN_DIVERSITY_NOT_MET")
    return dict(summary, result="ACCEPTED", injected=any("INJECTED" in r["stdout"] for r in ok), instrumented=any("INSTRUMENTED" in r["stdout"] for r in ok))


PUB_A = [(UP_A["sums"], UP_A["sig"], UP_A["pk"])]
PUB_B = [(UP_B["sums"], UP_B["sig"], UP_B["pk"])]
PUB_A_BAD = [(UP_A_BAD["sums"], UP_A_BAD["sig"], UP_A_BAD["pk"])]
LOCK_A, LOCK_B = lock_entry(UP_A, "sup-A", PLAIN), lock_entry(UP_B, "sup-B", PLAIN)
out = {"probe": "ENV7 environment manifest authority under CP-1 (AR-0019)", "rustc": subprocess.run([RUSTC, "--version"], capture_output=True, text=True, env=cenv()).stdout.strip()}
S = {}

cA = ceremony(LOCK_A, None, mirror(UP_A), PUB_A)
cB = ceremony(LOCK_B, None, mirror(UP_B), PUB_B)
S["E0_control"] = {"ceremony_A": cA["result"], "ceremony_B": cB["result"], "acceptance": acceptance([cA, cB], ["tc-up", "tc-boot"])}

# A07a: inline content in the lock or in a pipeline-proposed manifest
lock_inline = dict(LOCK_A, components=LOCK_A["components"] + [{"name": "inline", "version": "1", "sha256": H(INJECT_O), "placement_path": "lib/inject.o", "mode": 0o644, "content_b64": base64.b64encode(INJECT_O).decode()}])
S["A07a_lock_with_inline_content"] = ceremony(lock_inline, None, dict(mirror(UP_A), **{H(INJECT_O): INJECT_O}), PUB_A)["result"]
prop = derive_manifest(LOCK_A, mirror(UP_A), PUB_A)[0]["manifest"]
prop_inj = json.loads(json.dumps(prop))
prop_inj["components"].append({"name": "inline", "version": "1", "sha256": H(INJECT_O), "placement_path": "lib/inject.o", "mode": 0o644, "checksum_key_id": "none", "checksum_file_digest": "none"})
S["A07a_pipeline_manifest_with_injection"] = ceremony(LOCK_A, prop_inj, mirror(UP_A), PUB_A)["result"]
# A07b: pipeline proposes placement of genuinely signed instrumented artefacts; the registered lock names the plain ones
prop_instr = derive_manifest(lock_entry(UP_A, "sup-A", INSTR), mirror(UP_A), PUB_A)[0]["manifest"]
S["A07b_pipeline_manifest_selects_instrumented_artefacts"] = ceremony(LOCK_A, prop_instr, mirror(UP_A), PUB_A)["result"]
cI = ceremony(lock_entry(UP_A, "sup-A", INSTR), None, mirror(UP_A), PUB_A)
cIB = ceremony(lock_entry(UP_B, "sup-B", INSTR), None, mirror(UP_B), PUB_B)
S["A07b_source_authority_control_lock_changed_in_reviewed_source (TB-4/TB-4′ route, not pipeline)"] = {"ceremony": [cI["result"], cIB["result"]], "acceptance": acceptance([cI, cIB], ["tc-up", "tc-boot"])}
# A07c: both classes' pipeline manifests carry the same injection
propB_inj = json.loads(json.dumps(derive_manifest(LOCK_B, mirror(UP_B), PUB_B)[0]["manifest"]))
propB_inj["components"].append(prop_inj["components"][-1])
S["A07c_both_classes_same_injection"] = [ceremony(LOCK_A, prop_inj, mirror(UP_A), PUB_A)["result"], ceremony(LOCK_B, propB_inj, mirror(UP_B), PUB_B)["result"]]
# A08: one compromised supplier under two labels
lock_bad_A = lock_entry(UP_A_BAD, "sup-A", PLAIN_BAD)
lock_bad_M = lock_entry(UP_A_BAD, "sup-A-mirror", PLAIN_BAD)
UP_A_BAD_SIGNED_BY_A = dict(UP_A_BAD, sig=keypair("upstream:distA")[0].sign(UP_A_BAD["sums"]), pk=UP_A["pk"])
PUB_BAD = [(UP_A_BAD_SIGNED_BY_A["sums"], UP_A_BAD_SIGNED_BY_A["sig"], UP_A_BAD_SIGNED_BY_A["pk"])]
c8a = ceremony(lock_bad_A, None, mirror(UP_A_BAD), PUB_BAD)
c8m = ceremony(lock_bad_M, None, mirror(UP_A_BAD), PUB_BAD)
S["A08_two_labels_over_one_compromised_supplier"] = {"ceremonies": [c8a["result"], c8m["result"]], "acceptance": acceptance([c8a, c8m], ["tc-up", "tc-boot"]),
                                                     "control_label_counting_mutant": acceptance([c8a, c8m], ["tc-up", "tc-boot"], by_label=True)}
S["control_one_compromised_class_with_independent_honest_class"] = acceptance([c8a, cB], ["tc-up", "tc-boot"])
# A09: a manifest naming the author's own checksum key
EVIL = upstream("dist-evil", compromised=True, key_label="author-generated-key")
lock_evil = lock_entry(EVIL, "sup-A", PLAIN_BAD)
PUB_EVIL = [(EVIL["sums"], EVIL["sig"], EVIL["pk"])]
S["A09_checksum_key_named_by_manifest"] = {"pinned_keys_r7": ceremony(lock_evil, None, mirror(EVIL), PUB_EVIL)["result"],
                                           "control_named_key_revision6_shape": ceremony(lock_evil, None, mirror(EVIL), PUB_EVIL, key_source="named")["result"]}
# toolchain lineages
S["T1_upstream_binary_lineage_compromised"] = acceptance([cA, cB], ["tc-up", "tc-boot"], compromised_tcs=("tc-up",))
S["T2_relabelled_toolchain_lineage"] = acceptance([cA, cB], ["tc-up", "tc-up-relabelled"])
S["T2_control_label_counting_mutant"] = acceptance([cA, cB], ["tc-up", "tc-up-relabelled"], compromised_tcs=("tc-up", "tc-up-relabelled"), by_label=True)
S["T3_both_lineages_compromised (stated residual)"] = acceptance([cA, cB], ["tc-up", "tc-boot"], compromised_tcs=("tc-up", "tc-boot"))
out["scenarios"] = {k: ({kk: vv for kk, vv in v.items() if kk != "tree"} if isinstance(v, dict) else v) for k, v in S.items()}

# computed (CS7): pipeline-authored manifest and label diversity with the revision-7 rules and with them switched off (RV6-D-A05 E1)
spec = importlib.util.spec_from_file_location("cs7", os.path.join(HERE, "CS7-derivation-calculator.py"))
CS7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CS7)
comp = {}
for victim in ("P1", "CIR", "FA"):
    for label, R in (("CP-1", CS7.R7), ("rules_off_H_ENV_LOCK_IN_SOURCE", dict(CS7.R7, H_ENV_LOCK_IN_SOURCE=False)), ("rules_off_V_SUPPLIER_PROVENANCE", dict(CS7.R7, V_SUPPLIER_PROVENANCE=False)),
                     ("rules_off_V_SUPPLIER_PINNED_KEYS", dict(CS7.R7, V_SUPPLIER_PINNED_KEYS=False))):
        sets = CS7.minimal_sets("G_ENV", {"victim": victim}, R)["minimal_sets"]
        comp["%s|%s" % (victim, label)] = {"pipeline_alone_minimal": ["pipeline"] in sets, "single_supplier_alone_minimal": ["env_up_a"] in sets or ["env_up_b"] in sets,
                                          "invariant_failures": sorted(k.split(" ")[0] for k, v in CS7.invariants("G_ENV", {"victim": victim}, sets).items() if not v["holds"])}
out["computed"] = comp
g = lambda k: S[k]
out["verdicts"] = {
    "E0_honest_registered_and_accepted_bit_identical_across_classes_and_lineages": S["E0_control"]["ceremony_A"] == "REGISTERED" and S["E0_control"]["ceremony_B"] == "REGISTERED"
                                                                                   and S["E0_control"]["acceptance"]["result"] == "ACCEPTED" and not S["E0_control"]["acceptance"]["injected"],
    "A07a_refused_before_registration": S["A07a_lock_with_inline_content"] == "ENVIRONMENT_ASSEMBLY_NONCONFORMANT" and S["A07a_pipeline_manifest_with_injection"] == "ENVIRONMENT_MANIFEST_NOT_DERIVED",
    "A07b_pipeline_selection_refused": S["A07b_pipeline_manifest_selects_instrumented_artefacts"] == "ENVIRONMENT_MANIFEST_NOT_DERIVED",
    "A07b_selection_needs_source_authority": g("A07b_source_authority_control_lock_changed_in_reviewed_source (TB-4/TB-4′ route, not pipeline)")["acceptance"]["result"] == "ACCEPTED",
    "A07c_refused": S["A07c_both_classes_same_injection"] == ["ENVIRONMENT_MANIFEST_NOT_DERIVED", "ENVIRONMENT_MANIFEST_NOT_DERIVED"],
    "A08_label_diversity_refused": S["A08_two_labels_over_one_compromised_supplier"]["acceptance"]["result"] == "ENVIRONMENT_DIVERSITY_NOT_MET",
    "A08_control_label_counting_accepts_injection": S["A08_two_labels_over_one_compromised_supplier"]["control_label_counting_mutant"]["result"] == "ACCEPTED"
                                                    and S["A08_two_labels_over_one_compromised_supplier"]["control_label_counting_mutant"]["injected"],
    "independent_class_detects_compromised_supplier": S["control_one_compromised_class_with_independent_honest_class"]["result"] == "REPRODUCTION_CONFLICT",
    "A09_pinned_keys_refuse": S["A09_checksum_key_named_by_manifest"]["pinned_keys_r7"] == "ENVIRONMENT_COMPONENT_UNVERIFIED" and S["A09_checksum_key_named_by_manifest"]["control_named_key_revision6_shape"] == "REGISTERED",
    "T1_conflict": S["T1_upstream_binary_lineage_compromised"]["result"] == "REPRODUCTION_CONFLICT",
    "T2_relabelled_lineage_refused": S["T2_relabelled_toolchain_lineage"]["result"] == "TOOLCHAIN_DIVERSITY_NOT_MET" and S["T2_control_label_counting_mutant"]["result"] == "ACCEPTED",
    "T3_residual_as_stated": S["T3_both_lineages_compromised (stated residual)"]["result"] == "ACCEPTED" and S["T3_both_lineages_compromised (stated residual)"]["injected"],
    "computed_CP1_pipeline_never_minimal_and_invariants_hold": all(not v["pipeline_alone_minimal"] and not v["single_supplier_alone_minimal"] and not v["invariant_failures"] for k, v in comp.items() if k.endswith("|CP-1")),
    "computed_controls_show_rules_load_bearing": comp["P1|rules_off_H_ENV_LOCK_IN_SOURCE"]["pipeline_alone_minimal"] and comp["P1|rules_off_V_SUPPLIER_PROVENANCE"]["single_supplier_alone_minimal"]
                                                and comp["P1|rules_off_V_SUPPLIER_PINNED_KEYS"]["pipeline_alone_minimal"],
}
txt = json.dumps(out, indent=1, sort_keys=True, default=str)
print(txt.replace(BASE, "<scratch>").replace(ACCOUNT_HOME, "<home>"))
