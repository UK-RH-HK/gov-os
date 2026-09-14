#!/usr/bin/env python3
"""register_check — completeness and mechanical checks of the RoT-1 decision register (`29` §4; FD-1, R-SEL-1…R-SEL-4;
RV5-M5, CR5-B-05; review r5 CD5-4). PROPOSED architecture instrument (AR-0015, revision 6); decides nothing.

Checks (each reported with its failures; exit 0 iff every check passes):
  C1  schema: unique decision ids; every decision has selectors or a stated shortfall, restrictors, carriers, rules, tests.
  C2  completeness over normative rule ids: every rule id defined in a rule table of the scoped pack files (first table
      column; files and prefixes in DECISION_REGISTER.yaml `rule_scope`) is named by at least one decision's `rules`.
  C3  selectors: every selector names a calculator strategy that exists in CS6 (function name, with goal) or states
      `outside_calculator` with the residual or rule that bounds it.
  C4  restrictors: every restrictor names at least one of: a CS6 rule (key of CS6 RULES); an oracle or executed scenario id
      found in that instrument's committed output (P4r6 scenario ids exactly; DA03r6 mutant ids detected; CSI6 self-test
      case ids passed; others by key presence in the output); a checker case. A restrictor with only an RT must be marked
      `defence_in_depth: true` and name the load-bearing rule.
  C5  calculator coverage: every CS6 rule is referenced by the register; every CS6 rule that the calculator's own mutation
      analysis reports as not load-bearing in the model is referenced together with an oracle or executed scenario.
  C6  tests: every RT id named exists in `12-ACCEPTANCE-TEST-PLAN.md`.
  C7  rendering: the table between `<!-- REGISTER:BEGIN -->` and `<!-- REGISTER:END -->` in `29` equals the rendering of the
      YAML (`--write` regenerates it).
  C8  referenced executed instruments: every `verdicts` object of a referenced instrument output holds only true values.

Usage: register_check.py [--pack DIR] [--evidence DIR] [--write]
Output: JSON on stdout.
"""
import argparse, importlib.util, json, os, re, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--pack", default=os.path.dirname(HERE))
ap.add_argument("--evidence", default=None)
ap.add_argument("--write", action="store_true")
args = ap.parse_args()
PACK = os.path.abspath(args.pack)
EV = os.path.abspath(args.evidence or os.path.join(PACK, "evidence", "r6"))
REG = yaml.safe_load(open(os.path.join(HERE, "DECISION_REGISTER.yaml")))
out = {"instrument": "register_check (AR-0015)", "checks": {}}


def norm(rid):
    return rid.replace("′", "").replace("'", "").strip()


# ------------------------------------------------------------------------------------------------ inputs
def load_json(name):
    p = os.path.join(EV, name)
    return json.load(open(p)) if os.path.exists(p) else None


INSTR = {
    "P4r6": "P4r6-conformance-oracle.json", "FA6": "FA6-first-admission.json", "CON6": "CON6-first-hand-constitutional-content.json",
    "ENV6": "ENV6-build-environment.json", "ADM6": "ADM6-admission-transactions.json", "UW6": "UW6-user-writable-install.json",
    "SRC6": "SRC6-source-identity-v2.json", "DA03r6": "DA03r6-oracle-regression-sensitivity.json", "CSI6": "CSI6-selftest.json",
    "LAY6": "LAY6/LAY6-comparison.json", "CS6": "CS6-derivation-calculator.json", "ATTR6": "ATTR6-gitattributes-condition.json",
}
DATA = {k: load_json(v) for k, v in INSTR.items()}
TEXT = {k: (json.dumps(v, sort_keys=True) if v is not None else None) for k, v in DATA.items()}
spec = importlib.util.spec_from_file_location("cs6", os.path.join(EV, "CS6-derivation-calculator.py"))
CS6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CS6)
CS6_RULES = set(CS6.RULES)
CS6_FUNCS = {n for n in dir(CS6) if callable(getattr(CS6, n))}
PLAN = open(os.path.join(PACK, "12-ACCEPTANCE-TEST-PLAN.md")).read()
RT_IDS = set(re.findall(r"^\| \*{0,2}(RT-\d+[a-z]?)\b", PLAN, re.M))

decisions = REG["decisions"]

# ------------------------------------------------------------------------------------------------ C1 schema
c1 = []
ids = [d.get("id") for d in decisions]
if len(ids) != len(set(ids)):
    c1.append("duplicate decision ids")
for d in decisions:
    for f in ("id", "decision", "restrictors", "carriers", "rules", "tests", "specified_in"):
        if f not in d:
            c1.append("%s: missing %s" % (d.get("id"), f))
    if not d.get("selectors") and not d.get("shortfall"):
        c1.append("%s: neither selectors nor a stated shortfall" % d.get("id"))
out["checks"]["C1_schema"] = {"decisions": len(decisions), "failures": c1}

# ------------------------------------------------------------------------------------------------ C2 completeness over rule ids
scope = REG["rule_scope"]
prefixes = scope["prefixes"]
pat = re.compile(r"^\|\s*\*{0,2}((?:%s)-?\d+(?:′|')?r?)\*{0,2}\s*\|" % "|".join(re.escape(p) for p in sorted(prefixes, key=len, reverse=True)), re.M)
defined = {}
for fn in scope["files"]:
    txt = open(os.path.join(PACK, fn)).read()
    allowed = set(prefixes) | set(scope.get("file_prefixes", {}).get(fn, []))
    fpat = re.compile(r"^\|\s*\*{0,2}((?:%s)-?\d+(?:′|')?r?)\*{0,2}\s*\|" % "|".join(re.escape(p) for p in sorted(allowed, key=len, reverse=True)), re.M)
    for m in fpat.finditer(txt):
        rid = m.group(1)
        if re.fullmatch(r"E\d+", rid) and "E" not in scope.get("file_prefixes", {}).get(fn, []):
            continue
        defined.setdefault(norm(rid), set()).add(fn)
named = {norm(r) for d in decisions for r in d["rules"]}
range_ids = {norm(x) for extra in scope.get("ranges", []) for x in extra["expands_to"]}
missing = sorted(r for r in defined if r not in named)
unknown = sorted(r for r in named if r not in defined and r not in range_ids and not any(r.startswith(x) for x in scope.get("named_elsewhere_prefixes", [])))
c2_unknown_fail = ["register names rule %s, which no scoped file defines" % r for r in unknown]
out["checks"]["C2_rule_completeness"] = {"rule_ids_defined_in_scope": len(defined), "rule_ids_named_by_register": len(named & set(defined)),
                                         "failures": ["rule %s (%s) is named by no decision" % (r, ", ".join(sorted(defined[r]))) for r in missing] + c2_unknown_fail}

# ------------------------------------------------------------------------------------------------ C3 selectors
c3 = []
for d in decisions:
    for s in d.get("selectors") or []:
        cs = s.get("calculator")
        if cs:
            if cs.get("strategy") not in CS6_FUNCS:
                c3.append("%s: selector '%s' names unknown CS6 strategy %s" % (d["id"], s["input"], cs.get("strategy")))
            if cs.get("rule") and cs["rule"] not in CS6_RULES:
                c3.append("%s: selector '%s' names unknown CS6 rule %s" % (d["id"], s["input"], cs["rule"]))
        elif not s.get("outside_calculator"):
            c3.append("%s: selector '%s' has neither a calculator strategy nor an outside_calculator bound" % (d["id"], s["input"]))
    if d.get("shortfall") and not (d["shortfall"].get("residual") and d["shortfall"].get("test")):
        c3.append("%s: shortfall without residual and test" % d["id"])
out["checks"]["C3_selectors"] = {"selectors": sum(len(d.get("selectors") or []) for d in decisions), "failures": c3}


# ------------------------------------------------------------------------------------------------ C4 restrictors
def ref_ok(ref):
    inst, _, key = ref.partition(":")
    if inst == "P4r5u":
        inst_data = DATA.get("P4r6")
        if inst_data is None:
            return False, "instrument output P4r6 missing"
    elif inst not in DATA or DATA[inst] is None:
        return False, "instrument output %s missing" % inst
    if inst == "P4r6":
        sc = DATA[inst]["scenarios"].get(key)
        return (sc is not None and sc["holds"]), "P4r6 scenario %s %s" % (key, "absent" if sc is None else "does not hold")
    if inst == "P4r5u":
        row = (DATA["P4r6"] or {}).get("p4r5_under_r6", {}).get("rows", {}).get(key)
        return (row is not None and row["refusal_or_control_preserved"] and row["r6_holds_with_r5_expectation"]), "P4r5 row %s under revision-6 rules %s" % (key, "absent" if row is None else "does not hold")
    if inst == "DA03r6":
        rows = [r for k, v in DATA[inst].items() if k.startswith("section") for r in v]
        r = next((r for r in rows if r.get("mutant") == key), None)
        return (r is not None and r.get("detected") is True), "DA03r6 mutant %s not detected" % key
    if inst == "CSI6":
        c = next((c for c in DATA[inst]["cases"] if c["id"] == key), None)
        return (c is not None and c["pass"]), "CSI6 case %s not passing" % key
    return (key in TEXT[inst]), "%s key %s absent" % (inst, key)


c4, refs_used = [], set()
cs6_rules_referenced = {}
for d in decisions:
    for r in d["restrictors"]:
        kinds = 0
        if r.get("calculator_rule"):
            if r["calculator_rule"] not in CS6_RULES:
                c4.append("%s: restrictor '%s' names unknown CS6 rule %s" % (d["id"], r["rule"], r["calculator_rule"]))
            else:
                kinds += 1
                cs6_rules_referenced.setdefault(r["calculator_rule"], []).extend(r.get("scenarios", []))
        for ref in r.get("scenarios", []):
            ok, why = ref_ok(ref)
            refs_used.add(ref.split(":")[0])
            if not ok:
                c4.append("%s: restrictor '%s': %s" % (d["id"], r["rule"], why))
            else:
                kinds += 1
        if kinds == 0 and not r.get("defence_in_depth"):
            c4.append("%s: restrictor '%s' has no calculator rule and no scenario" % (d["id"], r["rule"]))
        if r.get("defence_in_depth") and not r.get("load_bearing"):
            c4.append("%s: defence-in-depth restrictor '%s' names no load-bearing rule" % (d["id"], r["rule"]))
    for s in d.get("selectors") or []:
        if (s.get("calculator") or {}).get("rule"):
            cs6_rules_referenced.setdefault(s["calculator"]["rule"], []).extend(s.get("scenarios", []))
out["checks"]["C4_restrictors"] = {"restrictors": sum(len(d["restrictors"]) for d in decisions), "failures": c4}

# ------------------------------------------------------------------------------------------------ C5 calculator coverage
c5 = []
mut = (DATA["CS6"] or {}).get("mutations", {})
for rule in sorted(CS6_RULES):
    if rule not in cs6_rules_referenced:
        c5.append("CS6 rule %s is referenced by no register row" % rule)
        continue
    lb = (mut.get(rule) or {}).get("load_bearing_in_model")
    if lb is False and not cs6_rules_referenced[rule]:
        c5.append("CS6 rule %s is not load-bearing in the model and its register rows name no oracle or executed scenario" % rule)
out["checks"]["C5_calculator_coverage"] = {"cs6_rules": len(CS6_RULES), "not_load_bearing_in_model": sorted(r for r, v in mut.items() if v.get("load_bearing_in_model") is False),
                                          "failures": c5}

# ------------------------------------------------------------------------------------------------ C6 tests
c6 = sorted({"%s: %s" % (d["id"], t) for d in decisions for t in d["tests"] if t not in RT_IDS})
out["checks"]["C6_tests_exist"] = {"rt_rows_in_plan": len(RT_IDS), "failures": c6}


# ------------------------------------------------------------------------------------------------ C7 rendering
def cell(x):
    return str(x).replace("|", "\\|").replace("\n", " ")


def render():
    rows = ["| ID | Decision (confers) | Selectors (authority; currency) | Restrictors | Carriers | Calculator (CS6) | Tests | Specified in |",
            "|---|---|---|---|---|---|---|---|"]
    for d in decisions:
        sel = []
        for s in d.get("selectors") or []:
            sel.append("**%s**: %s; %s" % (s["input"], s["authority"], s["currency"]))
        if d.get("shortfall"):
            sel.append("**shortfall (FD-1 §2 (5))**: %s; residual %s" % (d["shortfall"]["statement"], d["shortfall"]["residual"]))
        res = []
        for r in d["restrictors"]:
            tag = []
            if r.get("calculator_rule"):
                tag.append("`%s`" % r["calculator_rule"])
            if r.get("scenarios"):
                tag.append(", ".join("`%s`" % x for x in r["scenarios"][:3]) + (" …" if len(r["scenarios"]) > 3 else ""))
            if r.get("defence_in_depth"):
                tag.append("defence in depth of %s" % r["load_bearing"])
            res.append("%s (%s)" % (r["rule"], "; ".join(tag)))
        calc = []
        for s in d.get("selectors") or []:
            if s.get("calculator"):
                calc.append("`%s` %s" % (s["calculator"]["strategy"], "/".join(s["calculator"].get("goals", []))))
            else:
                calc.append("outside: %s" % s["outside_calculator"])
        rows.append("| %s | %s (%s) | %s | %s | %s | %s | %s | %s |" % (
            d["id"], cell(d["decision"]), cell(d.get("confers", "—")), cell("<br>".join(sel)), cell("<br>".join(res)), cell(", ".join(d["carriers"]) or "—"),
            cell("<br>".join(calc) or "—"), cell(", ".join(d["tests"])), cell(", ".join(d["specified_in"]))))
    return "\n".join(rows)


p29 = os.path.join(PACK, "29-FACT-DERIVATION-AND-SELECTION-AUTHORITY.md")
t29 = open(p29).read()
m = re.search(r"<!-- REGISTER:BEGIN -->\n(.*?)\n?<!-- REGISTER:END -->", t29, re.S)
table = render()
if args.write and m:
    t29 = t29[:m.start()] + "<!-- REGISTER:BEGIN -->\n" + table + "\n<!-- REGISTER:END -->" + t29[m.end():]
    open(p29, "w").write(t29)
    m = re.search(r"<!-- REGISTER:BEGIN -->\n(.*?)\n?<!-- REGISTER:END -->", t29, re.S)
out["checks"]["C7_rendering"] = {"failures": [] if (m and m.group(1).strip() == table.strip()) else ["the table in 29 differs from the rendering of DECISION_REGISTER.yaml"]}

# ------------------------------------------------------------------------------------------------ C8 executed instruments
c8 = []


def falses(v, path=""):
    if isinstance(v, dict):
        for k, x in v.items():
            yield from falses(x, path + "." + k)
    elif v is False:
        yield path


for inst in sorted(refs_used):
    dct = DATA.get(inst) or {}
    if isinstance(dct, dict) and "verdicts" in dct:
        bad = [p for p in falses(dct["verdicts"]) if not p.endswith("_revision5") and "r5_would" not in p]
        if bad:
            c8.append("%s verdicts false: %s" % (inst, bad[:5]))
out["checks"]["C8_referenced_instruments"] = {"instruments": sorted(refs_used), "failures": c8}

fails = sum(len(v["failures"]) for v in out["checks"].values())
out["summary"] = {"decisions": len(decisions), "failures": fails, "result": "PASS" if fails == 0 else "FAIL"}
print(json.dumps(out, indent=1, ensure_ascii=False))
sys.exit(0 if fails == 0 else 1)
