#!/usr/bin/env python3
"""register_check — completeness and mechanical checks of the RoT-1 decision register for the certified profile CP-1 (`29` §4;
FD-1, R-SEL-1…R-SEL-4; review r6 CD6-4, RV6-M2, CR6-B-03 (b)). PROPOSED architecture instrument (AR-0019, revision 7);
decides nothing.

Checks (each reported with its failures; exit 0 iff every check passes):
  C1  schema: unique decision ids; every decision has selectors or a stated shortfall, restrictors, carriers, rules, tests.
  C2  completeness over rule ids: every rule id defined in a rule table of the scoped pack files (`rule_scope`) is named by a
      decision's `rules`; every named id is defined.
  C3  selectors: every selector names a CS7 strategy (function) with goals, or an `outside_calculator` bound; every shortfall
      names a residual and a test.
  C4  restrictors: every restrictor names a CS7 rule or a scenario found in a referenced instrument output (see `instruments`);
      a restrictor with neither is marked defence in depth and names its load-bearing rule.
  C5  calculator coverage: every CS7 rule is referenced; a rule that CS7's mutation analysis reports as not load-bearing in the
      model is referenced together with at least one executed or oracle scenario.
  C6  tests: every RT id named exists in `12-ACCEPTANCE-TEST-PLAN.md`.
  C7  rendering: the table between REGISTER markers in `29` equals the rendering of the YAML (`--write` regenerates it).
  C8  referenced instruments: every `verdicts` object of a referenced instrument output holds only true values.
  C9  (revision 7) completeness over input values: every leaf field of every certified schema in `schemas/` (withdrawn schemas
      excluded) is matched by an `inputs` row of its schema with a role; selector and restrictor rows name the establishing
      party and an existing decision; a wildcard row may only be `carrier` or `informational` and must give a justification;
      every certified schema has an `inputs` entry.
  C10 (revision 7) procedure inputs: every row has an id, a role, a decision that exists, an establishing party (selectors and
      restrictors) or a justification, and at least one test whose input does not come from the register (an instrument
      scenario or an RT marked independent); and the compiled list of procedure inputs review r6 found unregistered (source
      designation, procedure text, the trust-state publication process, the package submitter, the environment-manifest author,
      stored codes, the admission clock, the environment lock, supplier provenance, toolchain provenance, derivation tools) is
      each present.
  C11 (revision 7) exclusions and informational inputs: every exclusion of `profile/CP-1.yaml` has an `excluded_inputs` row
      with its mechanism and tests, every row names an exclusion of the profile, and every `informational` input names no
      decision that reads it.

Usage: register_check.py [--pack DIR] [--write]
Output: JSON on stdout.
"""
import argparse, fnmatch, importlib.util, json, os, re, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--pack", default=os.path.dirname(HERE))
ap.add_argument("--write", action="store_true")
args = ap.parse_args()
PACK = os.path.abspath(args.pack)
REG = yaml.safe_load(open(os.path.join(HERE, "DECISION_REGISTER.yaml")))
PROFILE = yaml.safe_load(open(os.path.join(PACK, "profile", "CP-1.yaml")))
out = {"instrument": "register_check (AR-0019, revision 7)", "profile_id": REG.get("profile_id"), "checks": {}}


def norm(rid):
    return rid.replace("′", "").replace("″", "").replace("'", "").strip()


# ------------------------------------------------------------------------------------------------ inputs
def load_json(rel):
    p = os.path.join(PACK, rel)
    return json.load(open(p)) if os.path.exists(p) else None


INSTR = REG["instruments"]
DATA = {k: load_json(v) for k, v in INSTR.items()}
TEXT = {k: (json.dumps(v, sort_keys=True, ensure_ascii=False) if v is not None else None) for k, v in DATA.items()}
spec = importlib.util.spec_from_file_location("cs7", os.path.join(PACK, "evidence", "r7", "CS7-derivation-calculator.py"))
CS7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CS7)
CS7_RULES = set(CS7.RULES)
CS7_FUNCS = {n for n in dir(CS7) if callable(getattr(CS7, n))}
PLAN = open(os.path.join(PACK, "12-ACCEPTANCE-TEST-PLAN.md")).read()
RT_IDS = set(re.findall(r"^\| \*{0,2}(RT-\d+[a-z]?)\b", PLAN, re.M))
decisions = REG["decisions"]
DEC_IDS = {d.get("id") for d in decisions}

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
defined = {}
for fn in scope["files"]:
    txt = open(os.path.join(PACK, fn)).read()
    allowed = list(scope["prefixes"]) + list(scope.get("file_prefixes", {}).get(fn, []))
    fpat = re.compile(r"^\|\s*\*{0,2}((?:%s)-?\d+(?:′|″|')*r?)\*{0,2}\s*\|" % "|".join(re.escape(p) for p in sorted(allowed, key=len, reverse=True)), re.M)
    for m in fpat.finditer(txt):
        rid = m.group(1)
        if re.fullmatch(r"E\d+", rid) and "E" not in scope.get("file_prefixes", {}).get(fn, []):
            continue
        defined.setdefault(norm(rid), set()).add(fn)
named = {norm(r) for d in decisions for r in d["rules"]}
range_ids = {norm(x) for extra in scope.get("ranges", []) for x in extra["expands_to"]}
missing = sorted(r for r in defined if r not in named)
unknown = sorted(r for r in named if r not in defined and r not in range_ids)
out["checks"]["C2_rule_completeness"] = {"rule_ids_defined_in_scope": len(defined), "rule_ids_named_by_register": len(named & set(defined)),
                                         "failures": ["rule %s (%s) is named by no decision" % (r, ", ".join(sorted(defined[r]))) for r in missing]
                                         + ["register names rule %s, which no scoped file defines" % r for r in unknown]}

# ------------------------------------------------------------------------------------------------ C3 selectors
c3 = []
for d in decisions:
    for s in d.get("selectors") or []:
        cs = s.get("calculator")
        if cs:
            if cs.get("strategy") not in CS7_FUNCS:
                c3.append("%s: selector '%s' names unknown CS7 strategy %s" % (d["id"], s["input"], cs.get("strategy")))
            if cs.get("rule") and cs["rule"] not in CS7_RULES:
                c3.append("%s: selector '%s' names unknown CS7 rule %s" % (d["id"], s["input"], cs["rule"]))
        elif not s.get("outside_calculator"):
            c3.append("%s: selector '%s' has neither a calculator strategy nor an outside_calculator bound" % (d["id"], s["input"]))
        if not s.get("established_by"):
            c3.append("%s: selector '%s' names no establishing party" % (d["id"], s["input"]))
    if d.get("shortfall") and not (d["shortfall"].get("residual") and d["shortfall"].get("test")):
        c3.append("%s: shortfall without residual and test" % d["id"])
out["checks"]["C3_selectors"] = {"selectors": sum(len(d.get("selectors") or []) for d in decisions), "failures": c3}


# ------------------------------------------------------------------------------------------------ C4 restrictors
def ref_ok(ref):
    inst, _, key = ref.partition(":")
    if inst not in DATA or DATA[inst] is None:
        return False, "instrument output %s missing" % inst
    if inst == "P4r6":
        sc = DATA[inst]["scenarios"].get(key)
        return (sc is not None and sc["holds"]), "P4r6 scenario %s %s" % (key, "absent" if sc is None else "does not hold")
    if inst == "DA03r6":
        rows = [r for k, v in DATA[inst].items() if k.startswith("section") for r in v]
        r = next((r for r in rows if r.get("mutant") == key), None)
        return (r is not None and r.get("detected") is True), "DA03r6 mutant %s not detected" % key
    if inst == "CSI":
        c = next((c for c in DATA[inst]["cases"] if c["id"] == key), None)
        return (c is not None and c["pass"]), "CSI case %s not passing" % key
    if inst == "PROF7":
        pe = DATA[inst]["per_exclusion"].get(key)
        return (pe is not None and pe["holds"]), "PROF7 exclusion %s %s" % (key, "absent" if pe is None else "does not hold")
    return (key in TEXT[inst]), "%s key %s absent" % (inst, key)


c4, refs_used, cs7_ref = [], set(), {}
for d in decisions:
    for r in d["restrictors"]:
        kinds = 0
        if r.get("calculator_rule"):
            if r["calculator_rule"] not in CS7_RULES:
                c4.append("%s: restrictor '%s' names unknown CS7 rule %s" % (d["id"], r["rule"], r["calculator_rule"]))
            else:
                kinds += 1
                cs7_ref.setdefault(r["calculator_rule"], []).extend(r.get("scenarios", []))
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
            cs7_ref.setdefault(s["calculator"]["rule"], []).extend(s.get("scenarios", []))
out["checks"]["C4_restrictors"] = {"restrictors": sum(len(d["restrictors"]) for d in decisions), "failures": c4}

# ------------------------------------------------------------------------------------------------ C5 calculator coverage
c5 = []
mut = (DATA.get("CS7") or {}).get("mutations", {})
for rule in sorted(CS7_RULES):
    if rule not in cs7_ref:
        c5.append("CS7 rule %s is referenced by no register row" % rule)
        continue
    if (mut.get(rule) or {}).get("load_bearing_in_model") is False and not cs7_ref[rule]:
        c5.append("CS7 rule %s is not load-bearing in the model and its register rows name no executed or oracle scenario" % rule)
out["checks"]["C5_calculator_coverage"] = {"cs7_rules": len(CS7_RULES), "not_load_bearing_in_model": sorted(r for r, v in mut.items() if v.get("load_bearing_in_model") is False),
                                          "failures": c5}

# ------------------------------------------------------------------------------------------------ C6 tests
all_tests = [t for d in decisions for t in d["tests"]] + [t for p in REG.get("procedure_inputs", []) for t in p.get("tests", []) if t.startswith("RT-")] \
    + [t for e in REG.get("excluded_inputs", []) for t in e.get("tests", []) if t.startswith("RT-")]
c6 = sorted({t for t in all_tests if t.startswith("RT-") and t not in RT_IDS})
out["checks"]["C6_tests_exist"] = {"rt_rows_in_plan": len(RT_IDS), "failures": ["test %s is not a row of 12" % t for t in c6]}


# ------------------------------------------------------------------------------------------------ C7 rendering
def cell(x):
    return str(x).replace("|", "\\|").replace("\n", " ")


def render():
    rows = ["| ID | Decision (confers) | Selectors (authority; currency; established by) | Restrictors | Carriers | Calculator (CS7) | Tests | Specified in |",
            "|---|---|---|---|---|---|---|---|"]
    for d in decisions:
        sel = ["**%s**: %s; %s; established by %s" % (s["input"], s["authority"], s["currency"], s["established_by"]) for s in d.get("selectors") or []]
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
        calc = [("`%s` %s" % (s["calculator"]["strategy"], "/".join(s["calculator"].get("goals", [])))) if s.get("calculator") else "outside: %s" % s["outside_calculator"]
                for s in d.get("selectors") or []]
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

# ------------------------------------------------------------------------------------------------ C9 schema-field completeness
SKIP = {"schema", "_type", "$schema", "x-schema-version"}


def leaves(node, pre=""):
    """Leaf field paths of a JSON schema (same enumeration as review r6 D-A09, extended over allOf/oneOf/anyOf)."""
    if not isinstance(node, dict):
        return
    props = node.get("properties")
    if isinstance(props, dict):
        for k, v in props.items():
            p = pre + "." + k if pre else k
            sub = False
            if isinstance(v, dict) and (v.get("properties") or (isinstance(v.get("items"), dict) and v["items"].get("properties"))
                                        or (isinstance(v.get("additionalProperties"), dict) and v["additionalProperties"].get("properties"))):
                sub = True
                yield from leaves(v, p)
                if isinstance(v.get("items"), dict):
                    yield from leaves(v["items"], p + "[]")
                if isinstance(v.get("additionalProperties"), dict):
                    yield from leaves(v["additionalProperties"], p + "{}")
            if not sub and k not in SKIP:
                yield p
    if isinstance(node.get("items"), dict) and not pre:
        yield from leaves(node["items"], pre)
    for kw in ("allOf", "oneOf", "anyOf"):
        if isinstance(node.get(kw), list):
            for s in node[kw]:
                yield from leaves(s, pre)


SD = os.path.join(PACK, "schemas")
schema_files = sorted(f for f in os.listdir(SD) if f.endswith(".schema.json"))
inputs_by_schema = {e["schema"]: e for e in REG.get("inputs", [])}
ROLES = {"selector", "restrictor", "carrier", "informational", "binding", "excluded"}
c9, c9_counts = [], {"schemas": 0, "fields": 0, "selector": 0, "restrictor": 0, "carrier": 0, "informational": 0, "binding": 0, "excluded": 0}
for sf in schema_files:
    c9_counts["schemas"] += 1
    fields = sorted(set(leaves(json.load(open(os.path.join(SD, sf))))))
    entry = inputs_by_schema.get(sf)
    if entry is None:
        c9.append("%s: no inputs entry (%d fields unregistered)" % (sf, len(fields)))
        continue
    rows = entry.get("fields", [])
    for row in rows:
        if row.get("role") not in ROLES:
            c9.append("%s: row %s has no valid role" % (sf, row.get("match")))
        if row.get("role") in ("selector", "restrictor", "binding"):
            if not row.get("established_by"):
                c9.append("%s: %s row %s names no establishing party" % (sf, row["role"], row.get("match")))
            if row.get("decision") not in DEC_IDS:
                c9.append("%s: %s row %s names decision %s, which does not exist" % (sf, row["role"], row.get("match"), row.get("decision")))
        if str(row.get("match")) == "*" and row.get("role") not in ("carrier", "informational", "excluded"):
            c9.append("%s: whole-schema row has role %s (only carrier, informational or excluded may cover a whole schema)" % (sf, row.get("role")))
        if "*" in str(row.get("match")) and not row.get("justification"):
            c9.append("%s: wildcard row %s gives no justification" % (sf, row.get("match")))
    for f in fields:
        c9_counts["fields"] += 1
        hit = next((r for r in rows if fnmatch.fnmatchcase(f, str(r.get("match")))), None)
        if hit is None:
            c9.append("%s: field %s has no role" % (sf, f))
        else:
            c9_counts[hit["role"]] = c9_counts.get(hit["role"], 0) + 1
    for extra in sorted(set(inputs_by_schema) - set(schema_files)):
        c9.append("inputs entry for %s, which is not a certified schema" % extra)
        inputs_by_schema.pop(extra)
out["checks"]["C9_schema_field_completeness"] = {"counts": c9_counts, "failures": c9}

# ------------------------------------------------------------------------------------------------ C10 procedure inputs
REQUIRED_PROCEDURE_INPUTS = {
    "source designation": r"designation of the two first-contact sources",
    "procedure text": r"procedure text of the first-contact procedure",
    "trust-state publication process (composer)": r"trust-state publication process",
    "package submitter": r"package submitter",
    "environment-manifest author": r"environment manifest author",
    "stored first-contact codes (media, CI image, cache)": r"stored first-contact codes",
    "admission clock": r"admission clock",
    "environment lock": r"environment lock in the registered source",
    "supplier provenance": r"supplier provenance registry",
    "toolchain provenance": r"toolchain provenance registry",
    "derivation and assembly tools": r"derivation tool and assembly tool",
    "operator reading of both sources": r"operator reading both sources",
    "repository release request": r"repository request",
    "account store files": r"account store files",
}
c10 = []
procs = REG.get("procedure_inputs", [])
pids = [p.get("id") for p in procs]
if len(pids) != len(set(pids)):
    c10.append("duplicate procedure input ids")
for p in procs:
    if p.get("role") not in ROLES:
        c10.append("%s: no valid role" % p.get("id"))
    if p.get("decision") not in DEC_IDS:
        c10.append("%s: decision %s does not exist" % (p.get("id"), p.get("decision")))
    if p.get("role") in ("selector", "restrictor", "binding") and not p.get("established_by"):
        c10.append("%s: %s names no establishing party" % (p.get("id"), p.get("role")))
    if p.get("role") in ("carrier", "informational", "excluded") and not p.get("justification"):
        c10.append("%s: %s gives no justification" % (p.get("id"), p.get("role")))
    indep = [t for t in p.get("tests", []) if ":" in t]
    for t in indep:
        ok, why = ref_ok(t)
        refs_used.add(t.split(":")[0])
        if not ok:
            c10.append("%s: test %s: %s" % (p.get("id"), t, why))
    if not indep:
        c10.append("%s: no test whose input is independent of the register (an instrument scenario)" % p.get("id"))
text_inputs = [p.get("input", "") for p in procs]
for name, pat in REQUIRED_PROCEDURE_INPUTS.items():
    if not any(re.search(pat, t, re.I) for t in text_inputs):
        c10.append("required procedure input '%s' is not registered" % name)
out["checks"]["C10_procedure_inputs"] = {"procedure_inputs": len(procs), "required_kinds": len(REQUIRED_PROCEDURE_INPUTS), "failures": c10}

# ------------------------------------------------------------------------------------------------ C11 exclusions and informational inputs
c11 = []
ex_profile = {e["id"] for e in PROFILE["exclusions"]}
rows = REG.get("excluded_inputs", [])
for r in rows:
    if r.get("exclusion") not in ex_profile:
        c11.append("excluded input '%s' names %s, which is not an exclusion of the profile" % (r.get("input"), r.get("exclusion")))
    if r.get("role") != "excluded" or not r.get("mechanism") or not r.get("tests"):
        c11.append("excluded input '%s' lacks role, mechanism or tests" % r.get("input"))
    for t in r.get("tests", []):
        if ":" in t:
            ok, why = ref_ok(t)
            if not ok:
                c11.append("excluded input '%s': %s" % (r.get("input"), why))
for ex in sorted(ex_profile - {r.get("exclusion") for r in rows}):
    c11.append("exclusion %s has no excluded input row" % ex)
for p in procs:
    if p.get("role") == "informational" and p.get("read_by_decision") not in (None, "none"):
        c11.append("%s: informational input is read by decision %s" % (p.get("id"), p.get("read_by_decision")))
out["checks"]["C11_exclusions_and_informational"] = {"excluded_inputs": len(rows), "profile_exclusions": len(ex_profile), "failures": c11}

fails = sum(len(v["failures"]) for v in out["checks"].values())
out["summary"] = {"decisions": len(decisions), "schemas": c9_counts["schemas"], "schema_fields": c9_counts["fields"], "procedure_inputs": len(procs),
                  "excluded_inputs": len(rows), "failures": fails, "result": "PASS" if fails == 0 else "FAIL"}
print(json.dumps(out, indent=1, ensure_ascii=False))
sys.exit(0 if fails == 0 else 1)
