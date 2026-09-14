#!/usr/bin/env python3
"""RV7-B-CS7 (AR-0020, reviewer B) — computed parts of RV7-B-A01, RV7-B-A02 and RV7-B-A03 with the architect's CS7 calculator
(`evidence/r7/CS7-derivation-calculator.py`, AR-0019) loaded UNMODIFIED; its functions are wrapped and the originals still called.

Control: with no extension, the wrapper reproduces the committed CP-REVOKED block of `32` §8 (FA, RA_held, RA_unheld) and the
CP-FC-ROOT block (FA, G_BYTES).
Extensions (each one strategy; nothing else changed):
  A01-VA  omission, pack as written: no rule has any party establish which revocations the revocation authority has issued a
          Trust State lists (R-FCS-2 (d) refuses only drops of what the custodian itself published; `accept` counts only listed
          revocation statements); the trust-state publication process composes the state the honest key holders sign.
          Strategy: `fcpub` selects a state omitting a revocation never published (victims FA, RA_unheld; P2 also needs `transport`,
          because a running machine applies every verified revocation statement it holds, `17` S5).
  A01-VB  omission, stricter reading: the trust-state key holders establish completeness first-hand; the omission then needs the
          trust-state threshold with the publication process.
  A02     C3 currency with stored codes: R-CUR-1/R-CUR-2 bound the event age, not the named state's age; victim P2 with `stored_old`
          and `transport` (the machine never receives the newer state). Control A02-FIX: a compiled 24-hour state age at C3 (as FC-9).
  A03     one onboarding record designates both sources: atom `onboard` implies `desig1` and `desig2` (R-FCD-2 delivers both
          identities in "the organisation's copy of the root ceremony record"); goal G_BYTES and G_REVOKED at FA.
Environment: PACK. Output: JSON on stdout.
"""
import importlib.util, json, os, re, sys
sys.dont_write_bytecode = True
PACK = os.environ["PACK"]
p = os.path.join(PACK, "evidence", "r7", "CS7-derivation-calculator.py")
spec = importlib.util.spec_from_file_location("cs7", p)
CS7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CS7)
R = CS7.R7
ORIG_REV, ORIG_ATOMS = CS7.revoked_admitted, CS7.atoms_for
MODE = {"omission": None, "stored_c3": False, "c3_state_age": False, "onboard": False}


def revoked_w(C, cfg, R_):
    v = cfg["victim"]
    if ORIG_REV(C, cfg, R_):
        return True
    if v == "RA_held":
        return False
    om = MODE["omission"]
    omitted = (om == "VA" and "fcpub" in C) or (om == "VB" and "fcpub" in C and CS7.ts_quorum(C, R_))
    if v in ("FA", "RA_unheld") and omitted:
        return True
    if v == "P2":
        if omitted and "transport" in C:
            return True
        if MODE["stored_c3"] and "stored_old" in C and "transport" in C and (not MODE["c3_state_age"] or "clockback" in C):
            return True
    return False


def atoms_w(goal, cfg, R_=None):
    a = list(ORIG_ATOMS(goal, cfg, R_))
    if goal == "G_REVOKED" and cfg["victim"] == "P2":
        for x in ("stored_old", "win", "clockback"):
            if x not in a:
                a.append(x)
    if MODE["onboard"] and cfg["victim"] in ("FA", "RA_held", "RA_unheld", "P2", "P1A"):
        a.append("onboard")
    return a


CS7.revoked_admitted = revoked_w
CS7.IMPLIES["onboard"] = ("desig1", "desig2")   # A03: one onboarding record carries both source identities (R-FCD-2)
CS7.atoms_for = atoms_w


def ms(goal, victim):
    r = CS7.minimal_sets(goal, {"victim": victim}, R)["minimal_sets"]
    return {"sets": r, "rendered": [CS7.compact(s) for s in r]}


def block(name):
    t = open(os.path.join(PACK, "32-FIRST-CONTACT-ROOT.md")).read()
    m = re.search(r"<!-- CS7:BEGIN %s -->(.*?)<!-- CS7:END %s -->" % (name, name), t, re.S)
    rows = {}
    for line in m.group(1).strip().split("\n")[2:]:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows[cells[0].split(" ")[0]] = sorted(x.strip() for x in re.findall(r"\{[^}]*\}", cells[1]))
    return rows


out = {"probe": "RV7-B-CS7 extensions (AR-0020)", "calculator_sha256": __import__("hashlib").sha256(open(p, "rb").read()).hexdigest()}
# control
base = {v: ms("G_REVOKED", v) for v in ("FA", "RA_held", "RA_unheld", "P2")}
committed = block("CP-REVOKED")
out["control_reproduces_committed_CP_REVOKED"] = {v: sorted(base[v]["rendered"]) == committed[v] for v in ("FA", "RA_held", "RA_unheld")}
fc_root = ms("G_BYTES", "FA")
nokey = lambda xs: [x for x in xs if not re.search(r"\d [a-z]", x)]
out["control_FA_G_BYTES_first_contact_sets"] = nokey(fc_root["rendered"])
out["control_equals_committed_CP_FC_ROOT"] = sorted(out["control_FA_G_BYTES_first_contact_sets"]) == sorted(block("CP-FC-ROOT")["FA"])
out["base_P2_G_REVOKED (not computed by the pack)"] = base["P2"]["rendered"]
res = {}
for label, mode in (("A01-VA", {"omission": "VA"}), ("A01-VB", {"omission": "VB"}), ("A02", {"stored_c3": True}), ("A02-FIX", {"stored_c3": True, "c3_state_age": True})):
    MODE.update({"omission": None, "stored_c3": False, "c3_state_age": False, "onboard": False})
    MODE.update(mode)
    res[label] = {v: ms("G_REVOKED", v)["rendered"] for v in ("FA", "RA_held", "RA_unheld", "P2")}
MODE.update({"omission": None, "stored_c3": False, "c3_state_age": False, "onboard": True})
res["A03"] = {"FA_G_BYTES": nokey(ms("G_BYTES", "FA")["rendered"]), "FA_G_REVOKED": ms("G_REVOKED", "FA")["rendered"]}
MODE["onboard"] = False
out["extensions"] = res
new = lambda lab, v: sorted(set(res[lab][v]) - set(base[v]["rendered"]))
out["new_minimal_sets"] = {"A01-VA": {v: new("A01-VA", v) for v in ("FA", "RA_held", "RA_unheld", "P2")},
                           "A01-VB": {v: new("A01-VB", v) for v in ("FA", "RA_held", "RA_unheld", "P2")},
                           "A02": {"P2": new("A02", "P2")}, "A02-FIX": {"P2": new("A02-FIX", "P2")},
                           "A03": {"FA_G_BYTES": sorted(set(res["A03"]["FA_G_BYTES"]) - set(out["control_FA_G_BYTES_first_contact_sets"])),
                                   "FA_G_REVOKED": sorted(set(res["A03"]["FA_G_REVOKED"]) - set(base["FA"]["rendered"]))}}
out["verdicts"] = {
    "control_equals_committed_block": all(out["control_reproduces_committed_CP_REVOKED"].values()) and out["control_equals_committed_CP_FC_ROOT"],
    "A01_VA_publication_process_alone_admits_a_revoked_binary_at_FA": "{fcpub}" in res["A01-VA"]["FA"],
    "A01_VB_trust_state_threshold_with_publication_admits_at_FA": any("2 trust-state keys" in x and "fcpub" in x for x in res["A01-VB"]["FA"]),
    "A01_INV7_AGE_would_fail": any(("win" not in x and "stored_old" not in x) and not x.startswith("{src") and "desig" not in x and "op1src" not in x for x in res["A01-VA"]["FA"]),
    "A02_stored_codes_with_transport_admit_at_P2": "{transport, stored_old}" in res["A02"]["P2"] or "{stored_old, transport}" in res["A02"]["P2"],
    "A02_FIX_removes_it": not any(x in res["A02-FIX"]["P2"] for x in ("{transport, stored_old}", "{stored_old, transport}")),
    "A03_single_onboarding_record_is_a_minimal_first_contact_root_set": "{onboard}" in res["A03"]["FA_G_BYTES"],
}
print(json.dumps(out, indent=1, sort_keys=True))
