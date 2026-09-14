#!/usr/bin/env python3
"""RV7-D-A02 (AR-0022, synthesis reviewer D, held-out) — OP-10 (b) x OP-16 (b) combination: one toolchain lineage and the OTHER
supplier class compromised together ("cross pair").

Normative text at d07d200: `25` AP-6 and `30` R-REP-4′ require >= 2 matching reproductions whose environments span two independent
supplier classes and whose toolchains span two independent lineages, and no conflicting valid reproduction; `30` R-REG-3 (f)
requires each custodian's own reproduction of every target. No rule requires a reproduction in every (supplier class x toolchain
lineage) combination. CS7 (`claims`: every honest reproducer builds in every combination; `custodian_digest`: the custodian builds
in every combination) and ENV7 (`acceptance`: "Every reproducer builds in every (registered environment, registered toolchain)
pair") both assume full-matrix reproduction. The stated invariants INV7-TC and INV7-ENV-B and the blocks CP-TOOLCHAIN / CP-ENV
(`33` §6, `21` §4 "each residual needs both lineages, both classes, hidden common provenance or the compiler source") rest on it.

Part E (executed, reference executor UNMODIFIED): a release RX whose two reproductions are (sup-A, tc-up) and (sup-B, tc-boot), both
naming the injected digest the registration names, published by two trust-state keys: gov-admit result. Controls: an honest third
reproduction in (sup-A, tc-boot) naming the clean digest -> REPRODUCTION_CONFLICT; both reproductions in one class ->
ENVIRONMENT_DIVERSITY_NOT_MET.
Part R (executed, real rustc 1.98.1 + system cc): a compromised upstream lineage is emulated as ENV7 does (an injected link
argument for that lineage's builds); a compromised supplier class B is emulated by that class's `cc` adding the same object
(idempotently). Builds in all four combinations; which digests are equal.
Part C (computed, CS7 loaded UNMODIFIED, functions wrapped, originals called): (i) control: unwrapped G_TOOLCHAIN and G_ENV for P1
equal the committed blocks; (ii) coordinated attacker (an injection on either axis yields the same malicious bytes, as Part R
shows) with full-matrix reproduction (the calculator's assumption); (iii) the same with each honest reproducer and the custodian
building in ONE combination (what the text permits), for every assignment of combinations, and whether a cross pair is absent
exactly when the reproducers' and custodian's combinations together cover every combination; (iv) a fix example: the custodian's
reproduction covers the one combination the reproducers left uncovered.
Environment: A02_SCRATCH, PACK, RUSTC. Output: JSON on stdout.
"""
import hashlib, importlib.util, itertools, json, os, re, subprocess, sys, tempfile
sys.dont_write_bytecode = True
PACK = os.environ["PACK"]
R7DIR = os.path.join(PACK, "evidence", "r7")
sys.path.insert(0, R7DIR)
import w7world as W  # noqa: E402
GA = W.GA
SCR = tempfile.mkdtemp(prefix="d-a02-", dir=os.environ["A02_SCRATCH"])
V = GA.Verifier(SCR)
out = {"probe": "RV7-D-A02 cross-axis reproduction (AR-0022)"}

# ------------------------------------------------------------------------------------------------ Part E
RX = W.Release("RX", 10, 2, 1, 12, ("g3", "g4"), ("p3", "p4"), marker="MALICIOUS-cross-axis",
               rep_plan=[("p3", W.ENV_A, "tc-up"), ("p4", W.ENV_B, "tc-boot")])
CLEAN_D = "sha256:" + hashlib.sha256(b"clean build of RX in (sup-A, tc-boot)").hexdigest()
honest_third = RX.reproduction("p2", W.ENV_A, "tc-boot", digest=CLEAN_D)
RX_ONE_CLASS = W.Release("RX1", 10, 2, 1, 12, ("g3", "g4"), ("p3", "p4"), marker="MALICIOUS-one-class",
                         rep_plan=[("p3", W.ENV_A, "tc-up"), ("p4", W.ENV_A, "tc-boot")])
B11 = W.T11["payload"]


def t12(rel):
    return W.tss(12, "2026-09-14T02:00:00Z", W.ROOT2, 2, W.TPS2, W.FCA2, W.PRIOR11 + [{"sequence": 11, "digest": W.T11["digest"]}],
                 B11["registrations"] + [rel.reg["digest"]], B11["published_binaries"] + [rel.D], B11["revocations"], revocation_statements=B11["revocation_statements"])


T12 = t12(RX)
T12_1 = t12(RX_ONE_CLASS)
pub = GA.custodian_publish(V, W.to_stmts(W.FULL + RX.all() + [T12]), W.LINEAGE, W.FCA2["digest"], T12["digest"], W.to_stmts([W.T11])[0])
E = {"custodian_publishes_T12": pub.get("published"),
     "diagonal_reproductions_only": W.admit(RX.binary, W.FCA2, T12, W.FULL + RX.all() + [T12], verifier=V, workdir=SCR)["result"],
     "control_honest_reproduction_in_uncovered_combination": W.admit(RX.binary, W.FCA2, T12, W.FULL + RX.all() + [T12, honest_third], verifier=V, workdir=SCR)["result"],
     "control_both_reproductions_in_one_class": W.admit(RX_ONE_CLASS.binary, W.FCA2, T12_1, W.FULL + RX_ONE_CLASS.all() + [T12_1], verifier=V, workdir=SCR)["result"],
     "reproductions_counted": [(r["payload"]["environment_id"] == W.ENV_A and "sup-A" or "sup-B", r["payload"]["toolchain_id"]) for r in RX.reps]}
out["E_executed_reference"] = E

# ------------------------------------------------------------------------------------------------ Part R (real toolchain)
RUSTC = os.environ.get("RUSTC", "rustc")
R = {"rustc": subprocess.run([RUSTC, "--version"], capture_output=True, text=True).stdout.strip(),
     "cc": subprocess.run(["cc", "--version"], capture_output=True, text=True).stdout.splitlines()[0]}
wd = os.path.join(SCR, "rt")
os.makedirs(wd)
open(os.path.join(wd, "inject.c"), "w").write('#include <stdio.h>\nstatic void __attribute__((constructor)) inj(void){ puts("INJECTED"); }\n')
subprocess.run(["cc", "-O2", "-fno-asynchronous-unwind-tables", "-c", os.path.join(wd, "inject.c"), "-o", os.path.join(wd, "inject.o")], check=True)
INJ = os.path.join(wd, "inject.o")
SRC = 'fn main() { println!("gov reproduction probe"); }\n'
for cls in ("A", "B"):
    b = os.path.join(wd, "env-" + cls, "bin")
    os.makedirs(b)
    if cls == "A":
        body = '#!/bin/sh\nexec /usr/bin/cc "$@"\n'
    else:   # compromised class B linker driver: adds the object unless it is already present (idempotent)
        body = '#!/bin/sh\ncase " $* " in *" %s "*) exec /usr/bin/cc "$@";; esac\nexec /usr/bin/cc "$@" %s\n' % (INJ, INJ)
    open(os.path.join(b, "cc"), "w").write(body)
    os.chmod(os.path.join(b, "cc"), 0o755)


def build(cls, lineage):
    d = os.path.join(wd, "build-%s-%s" % (cls, lineage))
    os.makedirs(d)
    open(os.path.join(d, "main.rs"), "w").write(SRC)
    envtree = os.path.join(wd, "env-" + cls)
    cmd = [RUSTC, "--edition", "2021", "-C", "opt-level=2", "-C", "codegen-units=1", "-C", "debuginfo=0", "-C", "strip=symbols", "-C", "linker=" + envtree + "/bin/cc",
           "--remap-path-prefix", d + "=/build", "--remap-path-prefix", envtree + "=/env", "-C", "link-arg=-Wl,--build-id=none", "-o", os.path.join(d, "gov"), os.path.join(d, "main.rs")]
    if lineage == "up":     # compromised upstream binary lineage (ENV7 T1 emulation): the compiler adds the object
        cmd += ["-C", "link-arg=" + INJ]
    r = subprocess.run(cmd, capture_output=True, text=True, env={"PATH": envtree + "/bin:/usr/bin:/bin", "HOME": os.environ.get("HOME", SCR), "TMPDIR": SCR,
                                                                  "RUSTUP_HOME": os.environ.get("RUSTUP_HOME", ""), "CARGO_HOME": os.environ.get("CARGO_HOME", "")})
    if r.returncode != 0:
        return {"status": "BUILD_FAILED", "stderr": r.stderr[-400:]}
    bb = open(os.path.join(d, "gov"), "rb").read()
    run = subprocess.run([os.path.join(d, "gov")], capture_output=True, text=True)
    return {"status": "OK", "digest": "sha256:" + hashlib.sha256(bb).hexdigest(), "stdout": run.stdout.strip().splitlines()}


builds = {"%s,%s" % (c, l): build(c, l) for c in ("A", "B") for l in ("up", "boot")}
R["builds"] = builds
dg = {k: v.get("digest") for k, v in builds.items()}
R["diagonal_A_up_equals_B_boot"] = dg["A,up"] == dg["B,boot"] and dg["A,up"] is not None
R["B_up_equals_diagonal"] = dg["B,up"] == dg["A,up"]
R["A_boot_is_clean_and_differs"] = dg["A,boot"] != dg["A,up"] and builds["A,boot"].get("stdout") == ["gov reproduction probe"]
R["diagonal_output_injected"] = "INJECTED" in (builds["A,up"].get("stdout") or [])
out["R_executed_real_toolchain"] = R

# ------------------------------------------------------------------------------------------------ Part C (computed)
spec = importlib.util.spec_from_file_location("cs7", os.path.join(R7DIR, "CS7-derivation-calculator.py"))
CS7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CS7)
ORIG = {n: getattr(CS7, n) for n in ("build", "claims", "custodian_digest", "atoms_for", "coverage_ok")}
MODE = {"coordinated": False, "plan": None, "cust": None, "cover_all": False, "joint_atoms": False}
COMBOS = [(c, t) for c in CS7.CLASSES for t in CS7.LINEAGES]


def build_w(rel, j, c, t, C, R_):
    b = ORIG["build"](rel, j, c, t, C, R_)
    if MODE["coordinated"] and (b[3] or b[4]):
        return (b[0], b[1], b[2], True, False, b[5])       # either injection yields the same malicious bytes (Part R)
    return b


def claims_w(rel, X, C, R_, first_hand):
    if MODE["plan"] is None:
        return ORIG["claims"](rel, X, C, R_, first_hand)
    outl = []
    for j in range(1, CS7.N_REP + 1):
        c, t = MODE["plan"][j - 1]
        if f"rp{j}" in C:
            outl.append((j, c, t, X, False))
        else:
            if first_hand and CS7.can_build(rel, R_):
                outl.append((j, c, t, CS7.build(rel, j, c, t, C, R_), True))
            if f"repk{j}" in C:
                outl.append((j, c, t, X, False))
    return outl


def custodian_w(rel, X, C, R_):
    if MODE["cust"] is None:
        return ORIG["custodian_digest"](rel, X, C, R_)
    if not R_["H_REG_OWN_REPRODUCTION"] and "pipeline" in C:
        return X
    if not CS7.can_build(rel, R_):
        return None
    c, t = MODE["cust"]
    return CS7.build(rel, 0, c, t, C, R_)


def atoms_w(goal, cfg, R_=None):
    a = list(ORIG["atoms_for"](goal, cfg, R_))
    if MODE["joint_atoms"] and goal == "G_TOOLCHAIN":
        a += [x for x in ("env_up_a", "env_up_b", "env_common") if x not in a]
    return a


def coverage_w(matching, R_):
    if not ORIG["coverage_ok"](matching, R_):
        return False
    if MODE["cover_all"]:
        return set(COMBOS) <= {(c, t) for _, c, t, _, _ in matching}
    return True


CS7.build, CS7.claims, CS7.custodian_digest, CS7.atoms_for, CS7.coverage_ok = build_w, claims_w, custodian_w, atoms_w, coverage_w
RR = CS7.R7


def ms(goal, victim="P1"):
    return sorted(sorted(s) for s in CS7.minimal_sets(goal, {"victim": victim}, RR)["minimal_sets"])


def block(fname, name, victim="P1"):
    t = open(os.path.join(PACK, fname)).read()
    m = re.search(r"<!-- CS7:BEGIN %s -->(.*?)<!-- CS7:END %s -->" % (name, name), t, re.S)
    for line in m.group(1).strip().split("\n"):
        if line.startswith("| %s |" % victim):
            return sorted(x.strip() for x in re.findall(r"\{[^}]*\}", line))
    return None


def render(sets):
    return sorted(CS7.compact(s) for s in CS7.undominated(sets))


cross = [{"toolchain_up", "env_up_b"}, {"toolchain_up", "env_up_a"}, {"diverse_tc", "env_up_a"}, {"diverse_tc", "env_up_b"}]
is_cross = lambda s: any(set(s) == c for c in cross)
C = {}
MODE.update(coordinated=False, plan=None, cust=None, cover_all=False, joint_atoms=False)
C["control_committed_CP_TOOLCHAIN_P1"] = {"computed": render(ms("G_TOOLCHAIN")), "committed": block("33-BUILD-ENVIRONMENT.md", "CP-TOOLCHAIN")}
canon_sets = lambda xs: sorted("{" + ", ".join(sorted(x.strip("{}").split(", "))) + "}" for x in (xs or []))
C["control_committed_CP_TOOLCHAIN_P1"]["equal"] = canon_sets(C["control_committed_CP_TOOLCHAIN_P1"]["computed"]) == canon_sets(C["control_committed_CP_TOOLCHAIN_P1"]["committed"])
MODE.update(coordinated=True, joint_atoms=True)
fm = ms("G_TOOLCHAIN")
C["coordinated_full_matrix (calculator assumption)"] = {"minimal_sets": render(fm), "cross_pairs_minimal": [s for s in fm if is_cross(s)]}
plans = {}
for plan in itertools.product(COMBOS, repeat=CS7.N_REP):
    for cust in COMBOS:
        MODE.update(plan=list(plan), cust=cust, cover_all=False)
        sets = ms("G_TOOLCHAIN")
        key = "reps=%s cust=%s" % ("/".join("%s%s" % p for p in plan), "%s%s" % cust)
        cov = CS7.coverage_ok([(j + 1, c, t, "x", True) for j, (c, t) in enumerate(plan)], RR)
        union_all = set(COMBOS) <= set(plan) | {cust}
        plans[key] = {"plan_meets_AP6_coverage": cov, "reproducers_and_custodian_cover_every_combination": union_all, "cross_pairs_minimal": [s for s in sets if is_cross(s)]}
C["coordinated_one_combination_per_party (text-permitted), every assignment"] = {
    "assignments": len(plans),
    "assignments_meeting_AP6_coverage": sum(1 for v in plans.values() if v["plan_meets_AP6_coverage"]),
    "of_those_with_a_cross_pair_minimal_set": sum(1 for v in plans.values() if v["plan_meets_AP6_coverage"] and v["cross_pairs_minimal"]),
    "of_those_covering_every_combination": sum(1 for v in plans.values() if v["plan_meets_AP6_coverage"] and v["reproducers_and_custodian_cover_every_combination"]),
    "cross_pair_absent_iff_every_combination_covered": all((not v["cross_pairs_minimal"]) == v["reproducers_and_custodian_cover_every_combination"] for v in plans.values() if v["plan_meets_AP6_coverage"]),
    "example": {k: v for k, v in plans.items() if k == "reps=Aup/Bboot/Bup cust=Aup"}}
MODE.update(plan=[("A", "up"), ("B", "boot"), ("B", "up")], cust=("A", "boot"), cover_all=False)
fx = ms("G_TOOLCHAIN")
C["fix_example_custodian_reproduces_the_uncovered_combination"] = {"minimal_sets": render(fx), "cross_pairs_minimal": [s for s in fx if is_cross(s)]}
out["C_computed_CS7"] = C
ex = C["coordinated_one_combination_per_party (text-permitted), every assignment"]
out["verdicts"] = {
    "E_reference_accepts_diagonal_reproductions": E["diagonal_reproductions_only"] == "ACCEPTED",
    "E_control_honest_uncovered_combination_conflicts": E["control_honest_reproduction_in_uncovered_combination"] == "REPRODUCTION_CONFLICT",
    "R_two_different_injection_points_give_bit_identical_bytes": R["diagonal_A_up_equals_B_boot"] and R["diagonal_output_injected"],
    "C_control_equals_committed_block": C["control_committed_CP_TOOLCHAIN_P1"]["equal"],
    "C_full_matrix_assumption_has_no_cross_pair": not C["coordinated_full_matrix (calculator assumption)"]["cross_pairs_minimal"],
    "C_text_permitted_assignments_meeting_AP6_with_a_cross_pair": "%d of %d" % (ex["of_those_with_a_cross_pair_minimal_set"], ex["assignments_meeting_AP6_coverage"]),
    "C_cross_pair_absent_exactly_when_every_combination_is_covered": ex["cross_pair_absent_iff_every_combination_covered"],
    "C_fix_example_removes_cross_pairs": not C["fix_example_custodian_reproduces_the_uncovered_combination"]["cross_pairs_minimal"],
}
print(re.sub(r"/tmp/[^\"\s]*", "<scratch>", json.dumps(out, indent=1, sort_keys=True, default=str)))
