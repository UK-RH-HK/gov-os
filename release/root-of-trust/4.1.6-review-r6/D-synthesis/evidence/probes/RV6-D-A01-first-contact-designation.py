#!/usr/bin/env python3
"""RV6-D-A01 — who designates the first-contact sources and the procedure steps? (review r6 synthesis D, AR-0018)
Executed (reference executor, real Ed25519 via OpenSSL, `sha256sum`) + computed (CS6, functions wrapped, originals called) +
design (pack text at 4106885). Scratch only.

Question. `32` §4 and `06` §3 step 0 have the operator run FC-1…FC-3 "over the sources the owner's OP-13 answer names", and
state that `gov trust fc-procedure` prints those steps (also `09` header). On a first-install machine the only `gov` is the
carrier-delivered, not-yet-admitted candidate, which `31` GB-1′ lets run C0. `32` §10 FC-R2's bound is "the procedure prints
each source's name". If the list of sources and steps comes from a carrier or from the unadmitted candidate, the attacker
chooses which "sources" the operator reads. Reviewer B's RV6-B-A01 held the designation fixed (honest sources carry a
publisher-composed code); this attack holds every owner source and the publisher honest and substitutes the designation.

Parts
  P (executed) For each code-path OP-13 answer: every owner source honest; the printed procedure names attacker pages, either
    with the owner's steps ("owner steps") or with weakened steps (one source, no platform-signature step). Strategies:
    S1 substituted evaluator (genuine lineage and state, attacker admitter digest in the manifest);
    S2 stale genuine state: the attacker pages show the code of the genuine T7 manifest (no `valid_until`), the genuine
       admitter runs, candidate B7x (published at T7 by the keys root v2 later rotated out; revoked at T9).
    Controls: designation known independently (owner pages read, genuine code, B8); one owner page read beside one attacker
    page (k = 2); current code with B7x.
  C (computed) CS6 with an atom `desig` (the party that tells the operator which sources to read and which steps to run).
    Variant V1: sources only (steps as the owner's answer); V2: sources and steps. FA minimal first-contact sets per OP-13
    answer, compared with `declared_fc_root`. Also: witness-reliant runners (victim WR) with reviewer B's `fcpub` atom (the
    witness service takes its input "from the owner's signing ceremony or the channel", `24` §3.3), not computed by B.
    Control: wrappers off reproduce the committed FC-ROOT block and the committed OP-9-BYTES WR row.
  D (design) The texts that name the designation and the procedure's printer; any rule on where the operator obtains them.
Environment: REVIEW_REPO, SCRATCH, GOV. Output: JSON on stdout.
"""
import hashlib, importlib.util, json, os, re, sys, tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d6world as W

SCR = tempfile.mkdtemp(prefix="da01-", dir=os.environ["SCRATCH"])
G, D1, ADM_BYTES = W.load(SCR)
GA = G["GA"]
g = lambda n: G[n]
V = GA.Verifier(SCR)
TARGET, LINEAGE, ADM_D = g("TARGET"), g("LINEAGE"), g("ADMITTER_DIGEST")
to_stmts, key = g("to_stmts"), g("key")
WORK = os.path.join(SCR, "plat")
NOW = "2026-09-14T00:00:00Z"
FC_OPTS = {"a": (1, None), "b": (2, None), "c_all_1": (1, "all"), "c_all_2": (2, "all"), "c_either_1": (1, "either"), "c_either_2": (2, "either"), "d": (1, "media")}
PLAT = "platform:code-signing-service"
PLAT_PUB = key(PLAT)[1]
SUB_ADM = b"#!/bin/sh\n# substituted admitter selected through the designation: admits every candidate\n"
SUB_ADM_D = GA.sha256d(SUB_ADM)
ATK_BIN = b"#!/bin/sh\n# ATTACKER-TCB (designation)\n"


def platform_sig(data):
    return key(PLAT)[0].sign(GA.pae(GA.PLATFORM_SIGNATURE_TYPE, data))


def run_accept(binary, typed, stmts, compiled, fcm=None):
    return GA.accept(binary, typed, to_stmts(stmts), TARGET, ADM_D, verifier=V, workdir=SCR, first_contact_manifest=fcm, compiled=compiled, now=NOW)


def genuine_fcm(k):
    tps = g("TPS1") if k == 2 else g("TPS1_Q1")
    t10 = g("T10") if k == 2 else g("T10_Q1")
    m = GA.make_fcm(LINEAGE, 2, g("ROOT2")["digest"], 1, tps["digest"], 10, t10["digest"], {TARGET: ADM_D}, "2026-09-13T00:00:00Z")
    return m, GA.fcm_bytes(m), GA.first_contact_code(m)


T7, TPS1 = g("T7"), g("TPS1")
FCM7 = GA.make_fcm(LINEAGE, 1, LINEAGE, 1, TPS1["digest"], 7, T7["digest"], {TARGET: ADM_D}, "2026-05-01T00:00:00Z")
OLD = [g("ROOT1"), TPS1, g("T1"), g("T5"), g("T6"), T7, g("VA7"), g("FINAL7"), g("REG7")]


def procedure(pages, fcm_b, adm, k, mode):
    if mode == "all":
        sig = platform_sig(adm) if adm == ADM_BYTES else b"\x00" * 64
        return GA.fc_procedure(pages, fcm_b, adm, TARGET, k, WORK, verifier=V, platform_pub=PLAT_PUB, platform_signature=sig, require_platform_signature=True)["result"]
    return GA.fc_procedure(pages, fcm_b, adm, TARGET, k, WORK, verifier=V)["result"]


def attempt(opt, strategy, steps):
    k, mode = FC_OPTS[opt]
    compiled = {"channel_quorum": k, "lineage": LINEAGE if mode else None}      # the genuine admitter's compiled OP-13 answer
    pk, pmode = (k, mode) if steps == "owner" else (1, None)                    # what the printed procedure tells the operator
    if pmode == "either":
        pmode = None                                                             # the printed procedure chooses the channel path
    if strategy == "S1_substituted_evaluator":
        gm, _, _ = genuine_fcm(k)
        m = GA.make_fcm(LINEAGE, 2, g("ROOT2")["digest"], 1, gm["state_epoch"]["policy_digest"], 10, gm["state_epoch"]["state_digest"], {TARGET: SUB_ADM_D}, gm["issued_at"])
        adm, binary, stmts = SUB_ADM, ATK_BIN, g("FULL") if k == 2 else g("FULL_Q1")
    elif strategy == "S2_stale_genuine_state_genuine_admitter":
        m, adm, binary, stmts = FCM7, ADM_BYTES, g("B7x_BYTES"), OLD + g("RP7x")
        pk = max(pk, 2)                                                          # the printed procedure asks for two pages; T7's Trust Policy has quorum 2
    else:
        raise ValueError(strategy)
    fcm_b, fcc = GA.fcm_bytes(m), GA.first_contact_code(m)
    pages = [fcc] * pk                                                           # attacker pages named by the printed procedure
    proc = procedure(pages, fcm_b, adm, pk, pmode)
    if proc != "OK":
        return {"procedure": proc, "admission": None}
    if adm != ADM_BYTES:
        return {"procedure": proc, "admission": "ACCEPTED_BY_SUBSTITUTED_EVALUATOR"}
    r = run_accept(binary, pages, stmts, compiled, fcm=fcm_b)
    return {"procedure": proc, "admission": r["result"], "selected_state": (r.get("selected_state") or {}).get("sequence")}


out = {"probe": "RV6-D-A01 first-contact designation and procedure printer (AR-0018)", "executor_sha256": hashlib.sha256(open(W.R6_PATH, "rb").read()).hexdigest()}
P = {}
for opt in ("a", "b", "c_all_1", "c_all_2", "c_either_1", "c_either_2"):
    k, mode = FC_OPTS[opt]
    gm, gmb, gfcc = genuine_fcm(k)
    comp = {"channel_quorum": k, "lineage": LINEAGE if mode else None}
    ctrl_proc = procedure([gfcc] * k, gmb, ADM_BYTES, k, mode if mode != "either" else None)
    row = {"control_designation_known_independently_genuine_B8": {"procedure": ctrl_proc, "admission": run_accept(g("B8_BYTES"), [gfcc] * k, g("FULL") if k == 2 else g("FULL_Q1"), comp, fcm=gmb)["result"]},
           "control_current_code_B7x": run_accept(g("B7x_BYTES"), [gfcc] * k, g("FULL") if k == 2 else g("FULL_Q1"), comp, fcm=gmb)["result"]}
    for strat in ("S1_substituted_evaluator", "S2_stale_genuine_state_genuine_admitter"):
        for steps in ("owner", "weakened"):
            row["%s|printed_steps=%s" % (strat, steps)] = attempt(opt, strat, steps)
    if k == 2:
        atk = GA.make_fcm(LINEAGE, 2, g("ROOT2")["digest"], 1, gm["state_epoch"]["policy_digest"], 10, gm["state_epoch"]["state_digest"], {TARGET: SUB_ADM_D}, gm["issued_at"])
        row["control_one_owner_page_beside_one_attacker_page"] = GA.fc_procedure([GA.first_contact_code(atk), gfcc], GA.fcm_bytes(atk), SUB_ADM, TARGET, 2, WORK, verifier=V)["result"]
    P[opt] = row
out["P_executed"] = P


# ------------------------------------------------------------------------------------------------ C computed
spec = importlib.util.spec_from_file_location("cs6", W.CS6_PATH)
CS6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CS6)
ORIG = {n: getattr(CS6, n) for n in ("fc_eval_sub", "fc_lineage_sub", "atoms_for", "thief_selectable")}
MODE = {"desig": False, "steps": False, "fcpub_wr": False}
committed = json.load(open(os.path.join(W.R6, "CS6-derivation-calculator.json")))


def w_fc_eval_sub(C, opt, R):
    if MODE["desig"] and "desig" in C:
        k, mode = CS6.FC_OPTS[opt]
        if mode in (None, "either"):
            return True
        if mode == "all" and (MODE["steps"] or "alt" in C):
            return True
    return ORIG["fc_eval_sub"](C, opt, R)


def w_fc_lineage_sub(C, opt, R):
    if MODE["desig"] and "desig" in C and CS6.FC_OPTS[opt][1] is None:
        return True
    return ORIG["fc_lineage_sub"](C, opt, R)


def w_atoms_for(goal, cfg):
    a = list(ORIG["atoms_for"](goal, cfg))
    if MODE["desig"] and cfg["victim"] == "FA":
        a.append("desig")
    if MODE["fcpub_wr"] and cfg["victim"] in ("WR", "ING_WR"):
        a.append("fcpub")
    return a


def w_thief(C, cfg, R):
    if MODE["fcpub_wr"] and cfg["victim"] in ("WR", "ING_WR") and "fcpub" in C:
        return True
    return ORIG["thief_selectable"](C, cfg, R)


CS6.fc_eval_sub, CS6.fc_lineage_sub, CS6.atoms_for, CS6.thief_selectable = w_fc_eval_sub, w_fc_lineage_sub, w_atoms_for, w_thief
CS6.IMPLIES["fcpub"] = ("ts",)
base = {"reg": "root", "V": 1, "repro": "n2q2", "victim": "FA", "fc": "a", "op4": "sep", "tc": "accept", "env": "a"}
ctrl = []
for opt in CS6.FC_OPTS:
    fs = CS6.minimal_sets("G_BYTES", dict(base, fc=opt), CS6.R6)["minimal_sets"]
    ctrl.append("| %s | %s | %d |" % (opt, "; ".join(CS6.compact(s) for s in fs if set(s) <= CS6.FC_ATOMS), len([s for s in fs if not set(s) <= CS6.FC_ATOMS])))
Cpart = {"control_wrappers_off_reproduce_committed_FC_ROOT": committed["statements"]["FC-ROOT"].endswith("\n".join(ctrl))}
wr_ctrl = "| n2q2 | WR | %s |" % "; ".join(CS6.uniq_render(CS6.undominated(CS6.minimal_sets("G_BYTES", dict(base, victim="WR", fc="-"), CS6.R6)["minimal_sets"])))
Cpart["control_wrappers_off_reproduce_committed_OP9_WR_row"] = wr_ctrl in committed["statements"]["OP-9-BYTES"]
EXTRA = CS6.FC_ATOMS | {"desig"}
for variant, steps in (("V1_designation_of_sources", False), ("V2_designation_of_sources_and_steps", True)):
    MODE.update(desig=True, steps=steps, fcpub_wr=False)
    rows = {}
    for opt in CS6.FC_OPTS:
        fs = CS6.minimal_sets("G_BYTES", dict(base, fc=opt), CS6.R6)["minimal_sets"]
        fc_sets = sorted(sorted(s) for s in fs if set(s) <= EXTRA)
        declared = sorted(sorted(x) for x in CS6.declared_fc_root(opt))
        fcc = CS6.minimal_sets("G_CONTENT", dict(base, fc=opt), CS6.R6)["minimal_sets"]
        rows[opt] = {"declared_first_contact_root": declared, "computed_no_key_sets": fc_sets, "outside_declared_root": [s for s in fc_sets if s not in declared],
                     "content_no_key_sets_outside_declared_root": sorted(sorted(s) for s in fcc if set(s) <= EXTRA and sorted(s) not in declared)}
    Cpart[variant] = rows
MODE.update(desig=False, steps=False, fcpub_wr=True)
wr = {}
for goal, victim, key_ in (("G_BYTES", "WR", "OP-9-BYTES"), ("G_CONTENT", "ING_WR", None)):
    fs = CS6.minimal_sets(goal, dict(base, victim=victim, fc="-"), CS6.R6)["minimal_sets"]
    wr["%s %s" % (goal, victim)] = {"with_fcpub": CS6.uniq_render(CS6.undominated(fs)),
                                    "committed_row": [l for l in committed["statements"][key_].splitlines() if l.startswith("| n2q2 | WR |")] if key_ else "no generated block for ING_WR"}
Cpart["WR_witness_input_composed_by_publisher"] = wr
MODE.update(desig=False, steps=False, fcpub_wr=False)
out["C_computed"] = Cpart

# ------------------------------------------------------------------------------------------------ D design
t06, t32, t09, t31, t24, t12, t01, t21 = (W.pack(n) for n in ("06-BOOTSTRAP.md", "32-FIRST-CONTACT-ROOT.md", "09-INTEGRATION-REQUIREMENTS.md", "31-INDEPENDENT-ADMISSION.md",
                                                            "24-FRESHNESS-ANCHORING-AND-MACHINE-BOOTSTRAP.md", "12-ACCEPTANCE-TEST-PLAN.md", "01-THREAT-MODEL.md", "21-OWNER-OPTIONS.md"))
alltext = "\n".join((t06, t32, t09, t31, t24, t01, t21))
out["D_design"] = {
    "06_s3_step0": W.lines(t06, lambda l: l.startswith("| 0 |")),
    "32_s4_fc_procedure": W.lines(t32, lambda l: "fc-procedure" in l),
    "09_header_fc_procedure": W.lines(t09, lambda l: "fc-procedure" in l),
    "32_FC_R2_bound": W.lines(t32, lambda l: l.startswith("| FC-R2")),
    "31_TB_1_prime": W.lines(t31, lambda l: l.startswith("| TB-1′")),
    "31_GB_1_prime_C0_without_record": "the binary runs **C0 only**" in t31,
    "24_C0_row_names_fc_procedure": any("fc-procedure" in l for l in t24.splitlines() if l.startswith("| **C0**")),
    "01_TA_5_prime": W.lines(t01, lambda l: l.startswith("| TA-5′")),
    "any_rule_on_where_the_operator_obtains_the_designation_or_procedure": [p for p in (r"onboarding", r"designation (?:is|of the sources is) (?:obtained|delivered|known)", r"procedure (?:is|text is) (?:published|obtained) (?:in|from) the (?:sources|root ceremony)",
                                                                                        r"never (?:printed|run) (?:by|from) (?:an unadmitted|the candidate)", r"fc-procedure[^\n]*(?:admitted|another machine|root ceremony)")
                                                                              if re.search(p, alltext, re.I)],
    "plan_rows_substituting_the_designation_or_procedure_printer": [m.group(1) for m in re.finditer(r"^\| \*{0,2}(RT-\d+)[^\n]*", t12, re.M) if re.search(r"fc-procedure|designat|printed procedure", m.group(0), re.I)],
}

S = lambda o, s: P[o][s]["admission"]
acc = lambda x: isinstance(x, str) and x.startswith("ACCEPTED")
out["verdicts"] = {
    "controls_genuine_designation_accepted_every_answer": all(P[o]["control_designation_known_independently_genuine_B8"]["admission"] == "ACCEPTED" for o in P),
    "controls_current_code_refuses_B7x": all(not acc(P[o]["control_current_code_B7x"]) for o in P),
    "control_owner_page_beside_attacker_page_disagreement": all(P[o]["control_one_owner_page_beside_one_attacker_page"] == "FIRST_CONTACT_DISAGREEMENT" for o in P if "control_one_owner_page_beside_one_attacker_page" in P[o]),
    "S1_substituted_evaluator_owner_steps_admitted_a_b_c_either": all(acc(S(o, "S1_substituted_evaluator|printed_steps=owner")) for o in ("a", "b", "c_either_1", "c_either_2")),
    "S1_substituted_evaluator_owner_steps_refused_c_all": all(not acc(S(o, "S1_substituted_evaluator|printed_steps=owner")) for o in ("c_all_1", "c_all_2")),
    "S1_substituted_evaluator_weakened_steps_admitted_every_code_path_answer": all(acc(S(o, "S1_substituted_evaluator|printed_steps=weakened")) for o in P),
    "S2_stale_state_B7x_admitted_by_genuine_admitter_every_code_path_answer_owner_steps": all(acc(S(o, "S2_stale_genuine_state_genuine_admitter|printed_steps=owner")) for o in P),
    "C_controls_reproduce_committed_blocks": Cpart["control_wrappers_off_reproduce_committed_FC_ROOT"] and Cpart["control_wrappers_off_reproduce_committed_OP9_WR_row"],
    "C_V1_sets_outside_declared_root": {o: v["outside_declared_root"] for o, v in Cpart["V1_designation_of_sources"].items()},
    "C_V2_sets_outside_declared_root": {o: v["outside_declared_root"] for o, v in Cpart["V2_designation_of_sources_and_steps"].items()},
    "D_no_rule_on_designation_source": not out["D_design"]["any_rule_on_where_the_operator_obtains_the_designation_or_procedure"],
    "D_no_plan_row": not out["D_design"]["plan_rows_substituting_the_designation_or_procedure_printer"],
}
print(json.dumps(out, indent=1, sort_keys=True, default=str).replace(SCR, "<scratch>").replace(W.REPO, "<export>"))
