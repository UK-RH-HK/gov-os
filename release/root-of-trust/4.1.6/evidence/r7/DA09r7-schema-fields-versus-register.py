#!/usr/bin/env python3
"""DA09r7 — does the decision register see every value that enters a trust decision? Review r6 synthesis D's RV6-D-A09 (AR-0018),
re-expressed against the revision-7 register and certified schemas (AR-0019). Computed; scratch only for part 4.

Independence from `register_check.py`: this probe has its own leaf enumeration (copied from RV6-D-A09 with attribution and
extended over allOf/oneOf/anyOf), its own establishment test (lexical, reported with its pattern), and it runs the register check
only as a black box on mutated copies of the register.
  1  Every leaf field of every certified schema (`schemas/*.schema.json`; withdrawn schemas excluded): is it covered by an `inputs`
     row of its schema? For selector, restrictor and binding rows: does the establishing party pass the lexical test?
  2  The focus fields review r6 named (first-contact values, the environment manifest, admission records) in their revision-7 form.
  3  The procedure inputs review r6 found unregistered: source designation, procedure text, the composer / publication process,
     the package submitter, the environment-manifest author.
  4  Held-out mutations of the register, each run through `register_check.py` on a scratch copy of `decision-register/` against
     the pack: removing the designation, publication-process, submitter or manifest-author procedure input; removing a schema-field
     row; blanking a selector's establishing party; removing an exclusion row. Each must fail; the unmodified copy must pass.
Environment: DA09_SCRATCH. Output: JSON on stdout.
"""
import copy, fnmatch, glob, json, os, re, shutil, subprocess, sys, tempfile

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PK = os.path.abspath(os.path.join(HERE, "..", ".."))
REGP = os.path.join(PK, "decision-register", "DECISION_REGISTER.yaml")
REG = yaml.safe_load(open(REGP))
SCR = tempfile.mkdtemp(prefix="da09r7-", dir=os.environ["DA09_SCRATCH"])
SKIP = {"schema", "_type", "$schema", "x-schema-version"}


def leaves(node, pre=""):
    if not isinstance(node, dict):
        return
    props = node.get("properties")
    if isinstance(props, dict):
        for k, v in props.items():
            p = pre + "." + k if pre else k
            sub = False
            if isinstance(v, dict) and (v.get("properties") or (isinstance(v.get("items"), dict) and v["items"].get("properties")) or (isinstance(v.get("additionalProperties"), dict) and v["additionalProperties"].get("properties"))):
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


EST = re.compile(r"first-hand|deriv|verif|reproduc|root|threshold|operator|custodian|registration|compiled|ceremony|gov-admit|signer|keys|install transaction|publisher|verifier|admitted gov|per-project record|root discovery|source|const|lock|clock|trust-state|revocation|profile|chain|digest of", re.I)
by_schema = {e["schema"]: e.get("fields", []) for e in REG.get("inputs", [])}
res = {"schemas": {}}
tot = {"schemas": 0, "fields": 0, "not_covered": 0, "selector_like_without_establishing_party": 0, "by_role": {}}
for path in sorted(glob.glob(os.path.join(PK, "schemas", "*.schema.json"))):
    name = os.path.basename(path)
    fields = sorted(set(leaves(json.load(open(path)))))
    rows = by_schema.get(name, [])
    tot["schemas"] += 1
    per = {}
    for f in fields:
        tot["fields"] += 1
        hit = next((r for r in rows if fnmatch.fnmatchcase(f, str(r.get("match")))), None)
        if hit is None:
            per[f] = "not_covered"
            tot["not_covered"] += 1
            continue
        role = hit.get("role")
        tot["by_role"][role] = tot["by_role"].get(role, 0) + 1
        if role in ("selector", "restrictor", "binding") and not EST.search(str(hit.get("established_by", ""))):
            per[f] = "%s_without_establishing_party" % role
            tot["selector_like_without_establishing_party"] += 1
        else:
            per[f] = role
    res["schemas"][name] = per
res["totals"] = tot
res["establishment_pattern"] = EST.pattern
focus = {"first-contact-authority.schema.json": ["lineage", "admitters", "sources[].locator", "procedure_digest", "certified_targets"],
         "environment-manifest.schema.json": ["components[].sha256", "components[].placement_path", "environment_tree_digest", "assembly_function", "supplier_id"],
         "environment-lock.schema.json": ["environments[].components[].sha256", "environments[].supplier_id"],
         "admission-record.schema.json": ["valid_until", "admitter_digest", "state_code", "admitter_kind"],
         "release-registration.schema.json": ["environments[].environment_id", "toolchains[].toolchain_id", "binary_digests", "security_relevant_change"],
         "trust-policy-statement.schema.json": ["supply_chain.suppliers[].provenance.base_image_lineage", "supply_chain.toolchains[].provenance.bootstrap_root", "gating.mode"]}
res["focus_fields"] = {s: {f: res["schemas"].get(s, {}).get(f, "field path not found") for f in fs} for s, fs in focus.items()}
ptext = " || ".join(p.get("input", "") for p in REG.get("procedure_inputs", []))
res["procedure_inputs"] = {"register_names_source_designation": bool(re.search(r"designation of the two first-contact sources", ptext)), "register_names_procedure_text": bool(re.search(r"procedure text", ptext)),
                           "register_names_composer_or_publication_process": bool(re.search(r"compos|publication process", ptext)),
                           "register_names_package_submitter": bool(re.search(r"submitter", ptext)), "register_names_environment_manifest_author": bool(re.search(r"manifest author", ptext))}
rc_src = open(os.path.join(PK, "decision-register", "register_check.py")).read()
res["register_check_reads_schemas"] = "schemas" in rc_src and "leaves(" in rc_src


# ------------------------------------------------------------------------------------------------ part 4
def run_check(mutator, label):
    d = os.path.join(SCR, re.sub(r"\W+", "_", label))
    shutil.copytree(os.path.join(PK, "decision-register"), d)
    reg = yaml.safe_load(open(os.path.join(d, "DECISION_REGISTER.yaml")))
    if mutator:
        mutator(reg)
    yaml.safe_dump(reg, open(os.path.join(d, "DECISION_REGISTER.yaml"), "w"), sort_keys=False, allow_unicode=True, width=10000)
    r = subprocess.run([sys.executable, "-B", os.path.join(d, "register_check.py"), "--pack", PK], capture_output=True, text=True,
                       env={"PATH": "/usr/bin:/bin", "HOME": SCR, "PYTHONDONTWRITEBYTECODE": "1"})
    try:
        j = json.loads(r.stdout)
        failing = {k: v["failures"][:3] for k, v in j["checks"].items() if v["failures"]}
    except Exception:  # noqa: BLE001
        failing = {"unparsed": r.stdout[-300:] + r.stderr[-300:]}
    return {"exit": r.returncode, "failing_checks": failing}


def drop_pi(pid):
    return lambda reg: reg.__setitem__("procedure_inputs", [p for p in reg["procedure_inputs"] if p["id"] != pid])


def drop_field(schema, match):
    def m(reg):
        for e in reg["inputs"]:
            if e["schema"] == schema:
                e["fields"] = [f for f in e["fields"] if f.get("match") != match]
    return m


def blank_establisher(did):
    def m(reg):
        for d in reg["decisions"]:
            if d["id"] == did:
                d["selectors"][0]["established_by"] = ""
    return m


def drop_exclusion(ex):
    return lambda reg: reg.__setitem__("excluded_inputs", [e for e in reg["excluded_inputs"] if e["exclusion"] != ex])


MUTS = {"control_unmodified": None, "M1_designation_removed": drop_pi("PI-01"), "M2_publication_process_removed": drop_pi("PI-05"), "M3_submitter_removed": drop_pi("PI-06"),
        "M4_manifest_author_removed": drop_pi("PI-07"), "M5_fca_sources_field_row_removed": drop_field("first-contact-authority.schema.json", "sources*"),
        "M6_fca_selector_establisher_blank": blank_establisher("DR-36"), "M7_exclusion_EX05_row_removed": drop_exclusion("EX-05")}
res["mutations"] = {k: run_check(v, k) for k, v in MUTS.items()}
res["verdicts"] = {
    "every_certified_schema_field_covered": tot["not_covered"] == 0,
    "no_selector_restrictor_or_binding_without_establishing_party": tot["selector_like_without_establishing_party"] == 0,
    "register_names_designation_procedure_composer_submitter_and_manifest_author": all(res["procedure_inputs"].values()),
    "register_check_reads_schemas": res["register_check_reads_schemas"],
    "control_register_check_passes": res["mutations"]["control_unmodified"]["exit"] == 0 and not res["mutations"]["control_unmodified"]["failing_checks"],
    # a mutation counts as detected only when the check runs to completion and names a failing check (a crash is not a detection)
    "every_held_out_mutation_fails_the_register_check": all(v["exit"] != 0 and v["failing_checks"] and "unparsed" not in v["failing_checks"]
                                                            for k, v in res["mutations"].items() if k != "control_unmodified"),
}
print(json.dumps(res, indent=1, sort_keys=True).replace(SCR, "<scratch>"))
