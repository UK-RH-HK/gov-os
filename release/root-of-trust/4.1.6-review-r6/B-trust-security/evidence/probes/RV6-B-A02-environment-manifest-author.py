#!/usr/bin/env python3
"""RV6-B-A02 / A07 / A08 / A09 — who selects the environment manifest? (review r6 reviewer B, AR-0016). Executed + computed.
Scratch only; the repository is never written.

Pack text relied on (design, 4106885): `33` §3 (environment manifest fields: `components[] {…, upstream_checksum_reference,
supplier_class}`, `assembly {recipe_digest, tool}`, `environment_tree_digest`, `supplier_class`), R-BENV-1 (component digests
match "a checksum signed by that component's upstream release"), R-BENV-2 (environment reproducers "assemble the environment
from the pinned components with the registered recipe"; the ceremony registers when two reproductions agree), R-BENV-4
(binary reproducers re-assemble), R-BENV-5 (diversity counted over distinct `supplier_class` values), §5 (what each party
checks), §6 (OP-16 residuals), `29` DR-13 (selector: "environment manifests (components, recipe, tree digest, supplier
class): the release registration, established by at least two first-hand environment reproductions"), `schemas/
environment-manifest.schema.json` (`upstream_checksum_reference` and `tool` are free strings; `supplier_class` a letter). No
rule names who authors the manifest, what a recipe may contain, which upstream keys are trusted, or how a supplier class is
established.

Executed harness. Built after the architect's ENV6 (`evidence/r6/ENV6-build-environment.py`, AR-0015, helper session), which
follows reviewer B r5 `RV5-B-A08-build-image-selects-bytes.py`: same Rust flags, same `inject.o` constructor, Ed25519-signed
upstream SHA256SUMS, environment reproduction by fetch-by-digest and assembly, binary reproduction by re-assembly and a real
`rustc` build with the environment's `bin/cc` as linker. Code re-typed; the recipe is modelled explicitly as a list of
operations (`place` a component by digest; `write` inline content), because ENV6's recipe is only a digest of the component
path list.

Scenarios (ceremony per R-BENV-1/2; acceptance per ENV6's OP-16 (a)/(b) functions):
  E0   control: recipe places the clean upstream components.
  A07a recipe with inline content (a wrapper `bin/cc` and `lib/inject.o`); every component is upstream-signed and unchanged.
  A07b recipe restricted to placement of upstream-signed components: the author selects the upstream's genuinely signed
       instrumented wrapper and runtime object in place of the plain wrapper.
  A07c OP-16 (b): the class-A and class-B manifests carry the same author's injecting recipe.
  A08  supplier class by label: two environments built only from distA components, labelled A and B; distA compromised.
       Control: classes bound to pinned upstream keys.
  A09  upstream key named by the manifest: the author's own "upstream" key signs SHA256SUMS for the injecting components.
       Control: the ceremony uses a pinned upstream key set.
Computed (CS6, loaded unmodified; `releases` and `build` wrapped, originals called): strategy "pipeline-authored manifest"
(E_man: components genuine, recipe common to every class) and "supplier class by label"; G_ENV minimal sets and CS6's own
invariants INV-ENV, INV-ENV-B, INV-ENV-PIPELINE.

Environment: REVIEW_REPO (export of 4106885), SCRATCH, A02_TOOLCHAIN (default ~/.rustup stable toolchain, read-only),
A02_ACCOUNT_HOME (for rustc only if it does not run with a scratch HOME). Output: JSON on stdout.
"""
import base64, hashlib, importlib.util, json, os, stat, subprocess, sys, tempfile

sys.dont_write_bytecode = True
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

REPO = os.environ["REVIEW_REPO"]
PK = os.path.join(REPO, "release", "root-of-trust", "4.1.6")
BASE = tempfile.mkdtemp(prefix="a02-", dir=os.environ["SCRATCH"])
ACCOUNT_HOME = os.environ.get("A02_ACCOUNT_HOME", "/home/usain")
TOOLCHAIN = os.environ.get("A02_TOOLCHAIN", ACCOUNT_HOME + "/.rustup/toolchains/stable-x86_64-unknown-linux-gnu")
RUSTC = TOOLCHAIN + "/bin/rustc"
W = BASE + "/work"
for d_ in (W, W + "/home", W + "/tmp"):
    os.makedirs(d_, exist_ok=True)
_r = subprocess.run([RUSTC, "--version"], env={"PATH": "/usr/bin:/bin", "HOME": W + "/home", "TMPDIR": W + "/tmp"}, capture_output=True, text=True)
RUSTC_HOME = W + "/home" if _r.returncode == 0 else ACCOUNT_HOME


def cenv(**kw):
    e = {"PATH": "/usr/bin:/bin", "HOME": RUSTC_HOME, "TMPDIR": W + "/tmp", "PYTHONDONTWRITEBYTECODE": "1"}
    e.update(kw)
    return {k: v for k, v in e.items() if not k.startswith("GOV_")}


def H(b):
    return hashlib.sha256(b).hexdigest()


def keypair(label):
    sk = Ed25519PrivateKey.from_private_bytes(hashlib.sha256(label.encode()).digest())
    return sk, sk.public_key()


def verify(pk, sig, data):
    try:
        pk.verify(sig, data)
        return True
    except Exception:
        return False


SRC = 'fn main() {\n    println!("gov: genuine behaviour");\n}\n'
open(W + "/inject.c", "w").write('#include <unistd.h>\n__attribute__((constructor)) static void rv6b_inject(void) { write(1, "INJECTED-BY-ENVIRONMENT-RECIPE\\n", 31); }\n')
subprocess.run(["/usr/bin/cc", "-c", "-O2", "-fno-ident", "-o", W + "/inject.o", W + "/inject.c"], env=cenv(), check=True, capture_output=True)
INJECT_O = open(W + "/inject.o", "rb").read()
open(W + "/prof.c", "w").write('#include <unistd.h>\n__attribute__((constructor)) static void upstream_prof(void) { write(1, "UPSTREAM-INSTRUMENTATION-RUNTIME\\n", 33); }\n')
subprocess.run(["/usr/bin/cc", "-c", "-O2", "-fno-ident", "-o", W + "/prof.o", W + "/prof.c"], env=cenv(), check=True, capture_output=True)
PROF_O = open(W + "/prof.o", "rb").read()


def cc_wrapper(sid, extra=""):
    return ("#!/bin/sh\n# supplier %s\nexec /usr/bin/cc \"$@\" %s\n" % (sid, extra)).encode()


# Upstream releases: each supplier signs a SHA256SUMS over the artefacts it publishes (genuine ones only, unless compromised).
def upstream(sid, compromised=False):
    arts = {"cc-plain": cc_wrapper(sid), "SUPPLIER": ("%s\n" % sid).encode(),
            "cc-instrumented": cc_wrapper(sid, "\"${0%/*}/../lib/instrument.o\""), "instrument.o": PROF_O}
    if compromised:
        arts["cc-plain"] = cc_wrapper(sid, "\"${0%/*}/../lib/inject.o\"")
        arts["inject.o"] = INJECT_O
    sums = "".join("%s  %s\n" % (H(b), n) for n, b in sorted(arts.items())).encode()
    sk, pk = keypair("upstream:" + sid)
    return {"sid": sid, "arts": arts, "sums": sums, "sig": sk.sign(sums), "pk": pk}


def mirror(*ups):
    m = {}
    for u in ups:
        for b in u["arts"].values():
            m[H(b)] = b
    return m


def recipe_place(u, mapping):
    """mapping: environment path -> upstream artefact name (placement of upstream-signed bytes only)."""
    return [{"op": "place", "path": p, "sha256": H(u["arts"][n]), "mode": 0o755 if p.startswith("bin/") else 0o644} for p, n in sorted(mapping.items())]


PLAIN = {"bin/cc": "cc-plain", "share/SUPPLIER": "SUPPLIER"}
PLAIN_COMPROMISED = {"bin/cc": "cc-plain", "share/SUPPLIER": "SUPPLIER", "lib/inject.o": "inject.o"}
INSTRUMENTED = {"bin/cc": "cc-instrumented", "share/SUPPLIER": "SUPPLIER", "lib/instrument.o": "instrument.o"}


def inline_injection():
    return [{"op": "write", "path": "bin/cc", "content_b64": base64.b64encode(cc_wrapper("recipe", "\"${0%/*}/../lib/inject.o\"")).decode(), "mode": 0o755},
            {"op": "write", "path": "lib/inject.o", "content_b64": base64.b64encode(INJECT_O).decode(), "mode": 0o644}]


def manifest(env_id, supplier_class, recipe, upstream_ref):
    comps = [{"sha256": r["sha256"], "upstream_checksum_reference": upstream_ref} for r in recipe if r["op"] == "place"]
    m = {"environment_id": env_id, "supplier_class": supplier_class, "components": comps, "recipe": recipe,
         "recipe_digest": H(json.dumps(recipe, sort_keys=True).encode()), "tool": "assemble-ops 1"}
    return m


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
            lines.append("%s\t%s\t%s\n" % (os.path.relpath(p, d), oct(stat.S_IMODE(os.stat(p).st_mode)), H(open(p, "rb").read())))
    return H("".join(sorted(lines)).encode())


def assemble(m, mir):
    """Honest environment reproducer / binary reproducer: fetch every placed component by digest, apply the recipe as registered."""
    d = tdir("env")
    for r in m["recipe"]:
        fp = os.path.join(d, r["path"])
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        if r["op"] == "place":
            b = mir.get(r["sha256"])
            if b is None or H(b) != r["sha256"]:
                return "INPUT_DIGEST_MISMATCH", None
        else:
            b = base64.b64decode(r["content_b64"])
        open(fp, "wb").write(b)
        os.chmod(fp, r["mode"])
    return "OK", d


def ceremony(m, mir, key_source, pinned):
    """R-BENV-1 as written: each component digest listed in a SHA256SUMS whose signature verifies under the key its reference
    names (`key_source='reference'`) or under the pinned upstream key of the supplier class (`key_source='pinned'`).
    R-BENV-2: two honest environment reproductions agree on the tree digest."""
    ref = m["components"][0]["upstream_checksum_reference"] if m["components"] else None
    if key_source == "reference":
        u = ref
    else:
        u = pinned.get(m["supplier_class"])
        if u is None:
            return "ENVIRONMENT_COMPONENT_UNVERIFIED", None
    if not verify(u["pk"], u["sig"], u["sums"]):
        return "ENVIRONMENT_COMPONENT_UNVERIFIED", None
    listed = {l.split("  ")[0] for l in u["sums"].decode().strip().split("\n")}
    for c in m["components"]:
        if c["sha256"] not in listed:
            return "ENVIRONMENT_COMPONENT_UNVERIFIED", None
    reps = [assemble(m, mir) for _ in range(2)]
    if any(s != "OK" for s, _ in reps):
        return "ENVIRONMENT_NOT_REPRODUCED", None
    ds = {tree_digest(d) for _, d in reps}
    if len(ds) != 1:
        return "ENVIRONMENT_REPRODUCTION_CONFLICT", None
    return "REGISTERED", ds.pop()


def bin_repro(label, m, mir, registered_tree):
    st, img = assemble(m, mir)
    if st != "OK":
        return {"status": st}
    if tree_digest(img) != registered_tree:
        return {"status": "INPUT_DIGEST_MISMATCH"}
    wd = tdir("build-" + label)
    os.makedirs(wd + "/src")
    open(wd + "/src/main.rs", "w").write(SRC)
    outp = wd + "/gov"
    cmd = [RUSTC, "--edition", "2021", "-C", "opt-level=2", "-C", "codegen-units=1", "-C", "debuginfo=0", "-C", "strip=symbols",
           "-C", "linker=" + img + "/bin/cc", "--remap-path-prefix", wd + "=/build", "--remap-path-prefix", img + "=/image",
           "-C", "link-arg=-Wl,--build-id=none", "-o", outp, wd + "/src/main.rs"]
    r = subprocess.run(cmd, env=cenv(PATH=img + "/bin:/usr/bin:/bin", TMPDIR=W + "/tmp"), capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        return {"status": "BUILD_FAILED", "stderr": r.stderr[-300:]}
    b = open(outp, "rb").read()
    run = subprocess.run([outp], capture_output=True, text=True, env={"PATH": "/usr/bin:/bin"}, timeout=10)
    return {"status": "OK", "binary_digest": H(b), "stdout": run.stdout.strip().splitlines(),
            "contains_path": (wd.encode() in b) or (img.encode() in b)}


def op16a(reps):
    ok = [r for r in reps if r["status"] == "OK"]
    if len(ok) < 2:
        return "REPRODUCTION_QUORUM_NOT_MET"
    return "REPRODUCTION_CONFLICT" if len({r["binary_digest"] for r in ok}) > 1 else "ACCEPTED"


def op16b(items):
    """ENV6 `op16b` semantics: diversity counted over the registered `supplier_class` values."""
    classes = {c for c, _ in items}
    if len(classes) < 2:
        return "ENVIRONMENT_DIVERSITY_NOT_MET"
    ds = {r["binary_digest"] for _, r in items if r["status"] == "OK"}
    return "REPRODUCTION_CONFLICT" if len(ds) > 1 else "ACCEPTED"


def summarise(reps):
    return [{"digest": r.get("binary_digest", "")[:16], "stdout": r.get("stdout"), "status": r["status"]} for r in reps]


A_ok, B_ok = upstream("distA"), upstream("distB")
A_bad = upstream("distA", compromised=True)
PINNED = {"A": A_ok, "B": B_ok}
out = {"probe": "RV6-B-A02/A07/A08/A09 environment manifest author (AR-0016)", "rustc": subprocess.run([RUSTC, "--version"], capture_output=True, text=True, env=cenv()).stdout.strip()}
S = {}

# E0 control
m0 = manifest("envA", "A", recipe_place(A_ok, PLAIN), A_ok)
c0, t0 = ceremony(m0, mirror(A_ok), "pinned", PINNED)
r0 = [bin_repro("E0-%d" % i, m0, mirror(A_ok), t0) for i in (1, 2)]
S["E0_control_plain_recipe"] = {"ceremony": c0, "reproductions": summarise(r0), "acceptance": op16a(r0)}

# A07a inline recipe content, every component upstream-verified (pinned keys)
m1 = manifest("envA", "A", recipe_place(A_ok, PLAIN) + inline_injection(), A_ok)
c1, t1 = ceremony(m1, mirror(A_ok), "pinned", PINNED)
r1 = [bin_repro("A07a-%d" % i, m1, mirror(A_ok), t1) for i in (1, 2)]
S["A07a_recipe_inline_content"] = {"ceremony": c1, "components_all_upstream_signed": True, "reproductions": summarise(r1), "acceptance": op16a(r1),
                                    "bit_identical": len({r.get("binary_digest") for r in r1}) == 1, "injected": all("INJECTED-BY-ENVIRONMENT-RECIPE" in (r.get("stdout") or []) for r in r1)}

# A07b placement only: selection among genuinely signed upstream artefacts
m2 = manifest("envA", "A", recipe_place(A_ok, INSTRUMENTED), A_ok)
c2, t2 = ceremony(m2, mirror(A_ok), "pinned", PINNED)
r2 = [bin_repro("A07b-%d" % i, m2, mirror(A_ok), t2) for i in (1, 2)]
S["A07b_placement_selects_genuine_instrumented_artefacts"] = {"ceremony": c2, "reproductions": summarise(r2), "acceptance": op16a(r2),
                                                              "bytes_differ_from_E0": r2[0].get("binary_digest") != r0[0].get("binary_digest"),
                                                              "instrumentation_runs": all("UPSTREAM-INSTRUMENTATION-RUNTIME" in (r.get("stdout") or []) for r in r2)}

# A07c OP-16 (b): both classes carry the same author's injecting recipe
m3a = manifest("envA", "A", recipe_place(A_ok, PLAIN) + inline_injection(), A_ok)
m3b = manifest("envB", "B", recipe_place(B_ok, PLAIN) + inline_injection(), B_ok)
c3a, t3a = ceremony(m3a, mirror(A_ok), "pinned", PINNED)
c3b, t3b = ceremony(m3b, mirror(B_ok), "pinned", PINNED)
r3a, r3b = bin_repro("A07c-A", m3a, mirror(A_ok), t3a), bin_repro("A07c-B", m3b, mirror(B_ok), t3b)
S["A07c_op16b_both_classes_same_author_recipe"] = {"ceremony_A": c3a, "ceremony_B": c3b, "reproductions": summarise([r3a, r3b]), "acceptance": op16b([("A", r3a), ("B", r3b)]),
                                                   "injected_both_classes": all("INJECTED-BY-ENVIRONMENT-RECIPE" in (r.get("stdout") or []) for r in (r3a, r3b))}
# control for (b): same author, plain recipes, class A upstream compromised -> conflict (the stated mechanism works when recipes are honest)
m3ca = manifest("envA", "A", recipe_place(A_bad, PLAIN_COMPROMISED), A_bad)
c3ca, t3ca = ceremony(m3ca, mirror(A_bad), "reference", PINNED)
m3cb = manifest("envB", "B", recipe_place(B_ok, PLAIN), B_ok)
c3cb, t3cb = ceremony(m3cb, mirror(B_ok), "pinned", PINNED)
r3ca, r3cb = bin_repro("C-A", m3ca, mirror(A_bad), t3ca), bin_repro("C-B", m3cb, mirror(B_ok), t3cb)
S["control_op16b_class_A_upstream_compromised_honest_recipes"] = {"acceptance": op16b([("A", r3ca), ("B", r3cb)])}

# A08 supplier class by label: both environments from distA (compromised), labelled A and B
m4a = manifest("envA", "A", recipe_place(A_bad, PLAIN_COMPROMISED), A_bad)
m4b = manifest("envB", "B", recipe_place(A_bad, PLAIN_COMPROMISED), A_bad)
c4a, t4a = ceremony(m4a, mirror(A_bad), "reference", PINNED)
c4b, t4b = ceremony(m4b, mirror(A_bad), "reference", PINNED)
r4a, r4b = bin_repro("A08-A", m4a, mirror(A_bad), t4a), bin_repro("A08-B", m4b, mirror(A_bad), t4b)
c4b_pinned, _ = ceremony(m4b, mirror(A_bad), "pinned", PINNED)
S["A08_supplier_class_by_label_one_upstream_compromised"] = {"ceremony_A": c4a, "ceremony_B_label_only": c4b, "reproductions": summarise([r4a, r4b]),
                                                             "acceptance_op16b_label_counting": op16b([("A", r4a), ("B", r4b)]),
                                                             "injected": all("INJECTED-BY-ENVIRONMENT-RECIPE" in (r.get("stdout") or []) for r in (r4a, r4b)),
                                                             "control_class_B_bound_to_pinned_distB_key": c4b_pinned}

# A09 upstream key named by the manifest
EV = {"sid": "dist-evil", "arts": dict(A_bad["arts"]), "sums": None}
EV["sums"] = "".join("%s  %s\n" % (H(b), n) for n, b in sorted(EV["arts"].items())).encode()
sk_ev, pk_ev = keypair("author-generated-upstream")
EV["sig"], EV["pk"] = sk_ev.sign(EV["sums"]), pk_ev
m5 = manifest("envA", "A", recipe_place(EV, PLAIN_COMPROMISED), EV)
c5_ref, t5 = ceremony(m5, mirror(EV), "reference", PINNED)
c5_pin, _ = ceremony(m5, mirror(EV), "pinned", PINNED)
r5 = [bin_repro("A09-%d" % i, m5, mirror(EV), t5) for i in (1, 2)] if c5_ref == "REGISTERED" else []
S["A09_upstream_key_named_by_manifest"] = {"ceremony_key_from_reference": c5_ref, "ceremony_pinned_keys_control": c5_pin, "reproductions": summarise(r5), "acceptance": op16a(r5) if r5 else None}
out["scenarios"] = S

schema = json.load(open(os.path.join(PK, "schemas", "environment-manifest.schema.json")))
t33 = open(os.path.join(PK, "33-BUILD-ENVIRONMENT.md")).read().lower()
out["design"] = {
    "schema_upstream_checksum_reference_type": schema["properties"]["components"]["items"]["properties"]["upstream_checksum_reference"]["type"],
    "schema_assembly_tool_type": schema["properties"]["assembly"]["properties"]["tool"]["type"],
    "schema_supplier_class_pattern": schema["properties"]["supplier_class"]["pattern"],
    "33_names_manifest_author": any(w in t33 for w in ("authored by", "author of the manifest", "produces the environment manifest", "proposes the environment manifest")),
    "33_constrains_recipe_content": any(w in t33 for w in ("recipe may", "recipe contains only", "recipe is part of the registered source", "recipe is reviewed")),
    "33_pins_upstream_keys": any(w in t33 for w in ("pinned upstream key", "upstream keys pinned", "upstream signing keys", "trust policy lists the upstream")),
    "33_establishes_supplier_class": any(w in t33 for w in ("supplier class is established", "share no component", "disjoint", "distinct upstream keys")),
}

# computed part
spec = importlib.util.spec_from_file_location("cs6", os.path.join(PK, "evidence", "r6", "CS6-derivation-calculator.py"))
CS6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CS6)
O_rel, O_build = CS6.releases, CS6.build
MODE = {"manifest": False, "label": False}


def w_releases(goal, C):
    r = O_rel(goal, C)
    return r


def w_releases_ctx(goal, C, cfg_env):
    r = list(O_rel(goal, C))
    if MODE["manifest"] and goal == "G_ENV" and "pipeline" in C and cfg_env in ("a", "b"):
        r.append({"S": "S_good", "I": "I_good", "E": "E_man", "K": "K_good", "genuine": False})
    return r


def w_build(rel, j, C, cfg, R):
    b = O_build(rel, j, C, cfg, R)
    if rel["E"] == "E_man":
        return (b[0], b[1], b[2], b[3], True, b[5])
    if MODE["label"] and cfg.get("env") == "b" and CS6.env_class(cfg, j) == "B" and "env_up_a" in C:
        return (b[0], b[1], b[2], b[3], True, b[5])
    return b


O_bin = CS6.binary_accepted


def w_binary_accepted(goal, C, cfg, R):
    CS6.releases = lambda g_, C_: w_releases_ctx(g_, C_, cfg.get("env", "a"))
    try:
        return O_bin(goal, C, cfg, R)
    finally:
        CS6.releases = O_rel


CS6.build, CS6.binary_accepted = w_build, w_binary_accepted
comp = {}
for mode_name, flags in (("control_unmodified", {"manifest": False, "label": False}), ("pipeline_authored_manifest", {"manifest": True, "label": False}),
                         ("supplier_class_by_label", {"manifest": False, "label": True})):
    MODE.update(flags)
    rows = {}
    for env in ("a", "b", "c"):
        for repro in ("n2q2", "n3q2"):
            cfg = {"reg": "root", "V": 1, "repro": repro, "victim": "P1", "fc": "-", "op4": "sep", "tc": "accept", "env": env}
            sets = CS6.minimal_sets("G_ENV", cfg, CS6.R6)["minimal_sets"]
            inv = CS6.invariants("G_ENV", cfg, sets)
            rows["OP-16=%s|OP-9=%s" % (env, repro)] = {"minimal_sets": [CS6.compact(s) for s in sets], "invariant_failures": sorted(k.split(" ")[0] for k, v in inv.items() if not v["holds"])}
    comp[mode_name] = rows
committed = json.load(open(os.path.join(PK, "evidence", "r6", "CS6-derivation-calculator.json")))
comp["committed_OP16_ENV_block"] = committed["statements"]["OP-16-ENV"].splitlines()[-6:]
out["computed"] = comp

out["verdicts"] = {
    "E0_control_registered_and_accepted_genuine": c0 == "REGISTERED" and op16a(r0) == "ACCEPTED" and all(r.get("stdout") == ["gov: genuine behaviour"] for r in r0),
    "A07a_recipe_injection_registered_accepted_bit_identical_injected": c1 == "REGISTERED" and S["A07a_recipe_inline_content"]["acceptance"] == "ACCEPTED" and S["A07a_recipe_inline_content"]["bit_identical"] and S["A07a_recipe_inline_content"]["injected"],
    "A07b_component_selection_changes_bytes_and_is_accepted": c2 == "REGISTERED" and S["A07b_placement_selects_genuine_instrumented_artefacts"]["acceptance"] == "ACCEPTED" and S["A07b_placement_selects_genuine_instrumented_artefacts"]["bytes_differ_from_E0"] and S["A07b_placement_selects_genuine_instrumented_artefacts"]["instrumentation_runs"],
    "A07c_op16b_does_not_detect_a_common_recipe": S["A07c_op16b_both_classes_same_author_recipe"]["acceptance"] == "ACCEPTED" and S["A07c_op16b_both_classes_same_author_recipe"]["injected_both_classes"],
    "control_op16b_detects_one_compromised_upstream_with_honest_recipes": S["control_op16b_class_A_upstream_compromised_honest_recipes"]["acceptance"] == "REPRODUCTION_CONFLICT",
    "A08_label_diversity_accepts_one_compromised_upstream": S["A08_supplier_class_by_label_one_upstream_compromised"]["acceptance_op16b_label_counting"] == "ACCEPTED",
    "A08_control_pinned_class_key_refuses": c4b_pinned == "ENVIRONMENT_COMPONENT_UNVERIFIED",
    "A09_reference_named_key_registers": c5_ref == "REGISTERED" and S["A09_upstream_key_named_by_manifest"]["acceptance"] == "ACCEPTED",
    "A09_control_pinned_keys_refuse": c5_pin == "ENVIRONMENT_COMPONENT_UNVERIFIED",
    "computed_pipeline_manifest_violates_INV_ENV_PIPELINE_under_a_and_b": all("INV-ENV-PIPELINE" in comp["pipeline_authored_manifest"]["OP-16=%s|OP-9=%s" % (e, r)]["invariant_failures"] for e in ("a", "b") for r in ("n2q2", "n3q2")),
    "computed_pipeline_manifest_no_effect_under_c": not any(comp["pipeline_authored_manifest"]["OP-16=c|OP-9=%s" % r]["invariant_failures"] for r in ("n2q2", "n3q2")),
    "computed_label_violates_INV_ENV_B": all("INV-ENV-B" in comp["supplier_class_by_label"]["OP-16=b|OP-9=%s" % r]["invariant_failures"] for r in ("n2q2", "n3q2")),
    "computed_control_no_invariant_failure": not any(v["invariant_failures"] for v in comp["control_unmodified"].values()),
}
txt = json.dumps(out, indent=1, sort_keys=True)
txt = txt.replace(BASE, "<scratch>").replace(W, "<scratch>/work").replace(ACCOUNT_HOME, "<home>").replace(REPO, "<export>")
print(txt)
