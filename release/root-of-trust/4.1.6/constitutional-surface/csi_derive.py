#!/usr/bin/env python3
"""Derive the Constitutional Surface Inventory (draft surface section of Trust Policy v1) from a kernel tree.

PROPOSED architecture artefact (RoT-1 revision 3). The classification RULES below are the reviewed architectural content:
they say which floor semantics every constitutional file and leaf has. The derivation only fills in the current values
(floor values, registered digests, registered member ids) from the kernel the first Trust Policy is issued for. In
production the result is reviewed in the root ceremony and signed as part of the Trust Policy (`19` §3, `23` §2); the
binary never derives classification from a kernel at run time.

Classification principle for POLICY files (`23` §3): the class is never weaker than what POLICY_PRECEDENCE already
grants the project layer for that key:
  overridable -> project_tunable (a project may set it freely, so the kernel lineage cannot hold a stronger floor)
  immutable -> pinned            floor/ceiling -> *_at_least/*_at_most      additive -> set_superset
  shrink_only -> set_subset      strengthen_only_bool -> bool_toward(strict_value)
with explicit exceptions listed in EXPLICIT. Non-policy files are classified explicitly.

Usage: csi_derive.py <kernel-dir> > CONSTITUTIONAL_SURFACE_INVENTORY.yaml
"""
import datetime, hashlib, json, os, sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import csi_lib as L  # noqa: E402

POLICIES = ["ARCHIVE_POLICY", "AUTHORITY_POLICY", "BUDGET_POLICY", "CHANGE_POLICY", "CHECKPOINT_POLICY", "CONTEXT_POLICY", "HUMAN_GATE_POLICY",
            "LEARNING_POLICY", "MEMORY_POLICY", "MODEL_ROUTING_POLICY", "POLICY_PRECEDENCE", "SECURITY_POLICY", "TEST_POLICY", "TOOL_POLICY"]

EXPLICIT = {
    # POLICY_PRECEDENCE: the rule list is floored per concrete key through the precedence lattice (19 §4.4)
    "POLICY_PRECEDENCE.default_mode": {"class": "floor", "op": "equals"},
    "POLICY_PRECEDENCE.layers": {"class": "pinned"},
}
COLLECTIONS = {
    "SECURITY_POLICY": [{"path": "secret_content_patterns", "id_field": "id", "members_op": "ids_superset",
                         "rationale": "a new content pattern only classifies more material as secret; registered patterns cannot be removed or edited"}],
    "POLICY_PRECEDENCE": [{"path": "rules", "id_field": "key", "members_class": "precedence",
                           "rationale": "rules are compared per concrete key of the policy universe through the precedence lattice, so a new, reordered or re-scoped rule cannot weaken any key"}],
}
RATIONALE = {
    "project_tunable": "POLICY_PRECEDENCE marks the key overridable: the project layer may set it freely, so no kernel-lineage floor can be stronger",
    "pinned": "no order in which a change is provably a strengthening; any change needs a Trust Policy registration signed at root threshold",
}


def rule_class_for_policy_leaf(key, value, prec_rules, default_mode):
    if key in EXPLICIT:
        return dict(EXPLICIT[key])
    parts = key.split(".")
    if len(parts) == 2 and parts[1] in ("policy", "version"):
        return {"class": "pinned", "note": "document header"}
    r = L.effective_rule(prec_rules, default_mode, key)
    m = r["mode"]
    if m == "overridable":
        return {"class": "project_tunable", "precedence_rule": r["key"]}
    if m == "immutable":
        return {"class": "pinned", "precedence_rule": r["key"]}
    if m in ("floor", "ceiling"):
        kind = r["kind"]
        up = m == "floor"
        if kind == "level":
            return {"class": "floor", "op": "level_at_least" if up else "level_at_most", "kind": "level", "precedence_rule": r["key"]}
        if kind in ("radius", "tier"):
            return {"class": "floor", "op": "ordered_at_least" if up else "ordered_at_most", "order": L.ORDERS[kind], "precedence_rule": r["key"]}
        if kind == "ordered":
            return {"class": "floor", "op": "ordered_at_least" if up else "ordered_at_most", "order": r["order"], "precedence_rule": r["key"]}
        if kind == "number":
            return {"class": "floor", "op": "decimal_at_least" if up else "decimal_at_most", "precedence_rule": r["key"]}
    if m == "additive" and isinstance(value, list):
        return {"class": "floor", "op": "set_superset", "precedence_rule": r["key"]}
    if m == "shrink_only" and isinstance(value, list):
        return {"class": "floor", "op": "set_subset", "precedence_rule": r["key"]}
    if m == "strengthen_only_bool":
        return {"class": "floor", "op": "bool_toward", "strict": r["strict_value"], "precedence_rule": r["key"]}
    return {"class": "pinned", "precedence_rule": r["key"], "note": f"mode {m} not applicable to value type; pinned"}


def finish_leaf(rule, key, value):
    out = {"key": key, **rule}
    if rule["class"] == "floor":
        out["value"] = str(value) if isinstance(value, float) else value
    elif rule["class"] == "pinned":
        out["digests"] = {key: [L.vdigest(value)]}
    return out


def policy_file_rule(kdir, name, prec_rules, default_mode):
    rel = f"policies/{name}.yaml"
    doc = L.load_doc(os.path.join(kdir, rel))
    fr = {"path": rel, "mode": "structured", "name": name, "policy_file": True, "collections": [], "leaves": []}
    for c in COLLECTIONS.get(name, []):
        fr["collections"].append({"path": c["path"], "id_field": c["id_field"], "rationale": c["rationale"]})
        base = f"{name}.{c['path']}[{c['id_field']}=*]"
        if c.get("members_class") == "precedence":
            fr["leaves"].append({"key": f"{name}.{c['path']}[{c['id_field']}]#members", "class": "precedence", "rationale": c["rationale"]})
            fr["leaves"].append({"key": base, "class": "covered_by_collection", "subtree": True})
        else:
            items = doc[c["path"]]
            fr["leaves"].append({"key": f"{name}.{c['path']}[{c['id_field']}]#members", "class": "members", "op": c["members_op"],
                                 "registered": sorted(x[c["id_field"]] for x in items), "rationale": c["rationale"]})
            fr["leaves"].append({"key": f"{base}.{c['id_field']}", "class": "collection_id"})
            if c["members_op"] == "ids_superset":
                for fld in sorted({k for x in items for k in x if k != c["id_field"]}):
                    fr["leaves"].append({"key": f"{base}.{fld}", "class": "covered_by_collection",
                                         "rationale": "field of an additional (unregistered) member of an additive collection: " + c["rationale"]})
            for x in items:
                for k, v in x.items():
                    if k == c["id_field"]:
                        continue
                    fr["leaves"].append(finish_leaf({"class": "pinned", "note": "registered member content"}, f"{name}.{c['path']}[{c['id_field']}={x[c['id_field']]}].{k}", v))
    leaves, structure = L.enumerate_leaves(doc, fr)
    assert not structure, structure
    covered = {l["key"] for l in fr["leaves"]}
    for key, v in leaves:
        if any(L.key_match(p, key) for p in covered):
            continue
        fr["leaves"].append(finish_leaf(rule_class_for_policy_leaf(key, v, prec_rules, default_mode), key, v))
    return fr


def roles_rule(kdir):
    rel = "roles/ROLES.yaml"
    doc = L.load_doc(os.path.join(kdir, rel))
    fr = {"path": rel, "mode": "structured", "name": "ROLES", "collections": [{"path": "roles", "id_field": "id",
          "rationale": "removing a role id reclassifies `--by <id>` gate answers as human (gates.rs answer); adding a role grants a new authority level"}], "leaves": []}
    fr["leaves"].append(finish_leaf({"class": "pinned", "note": "document header"}, "ROLES.version", doc["version"]))
    fr["leaves"].append({"key": "ROLES.authority_levels.*.*", "class": "informational",
                         "rationale": "display vocabulary for levels; no runtime reader (grep runtime/src 4.1.5: only authority_levels_required is read); levels are parsed from roles[].level"})
    for g, members in doc["groups"].items():
        fr["leaves"].append({"key": f"ROLES.groups.{g}", "class": "floor", "op": "set_subset", "value": members,
                             "rationale": "group membership grants memory-namespace access (authority.rs role_in); adding a member widens access"})
    fr["leaves"].append({"key": "ROLES.roles[id]#members", "class": "members", "op": "ids_equal", "registered": sorted(r["id"] for r in doc["roles"]),
                         "rationale": "role ids are the authority map's domain"})
    fr["leaves"].append({"key": "ROLES.roles[id=*].id", "class": "collection_id"})
    for r in doc["roles"]:
        b = f"ROLES.roles[id={r['id']}]"
        fr["leaves"].append({"key": b + ".level", "class": "floor", "op": "level_at_most", "kind": "level", "value": r["level"],
                             "rationale": "the actor's authority level for every authority check (authority.rs level_of); raising it is a weakening"})
        fr["leaves"].append({"key": b + ".minimum_tier", "class": "floor", "op": "ordered_at_least", "order": L.ORDERS["tier"], "value": r["minimum_tier"]})
        fr["leaves"].append({"key": b + ".default_reasoning", "class": "floor", "op": "ordered_at_least", "order": L.ORDERS["reasoning"], "value": r["default_reasoning"]})
        fr["leaves"].append(finish_leaf({"class": "pinned", "note": "rendered into agent adapters"}, b + ".name", r["name"]))
    return fr


def keyed_pinned_rule(kdir, rel, name, coll, idf, members_op, rationale):
    doc = L.load_doc(os.path.join(kdir, rel))
    fr = {"path": rel, "mode": "structured", "name": name, "collections": [{"path": coll, "id_field": idf, "rationale": rationale}], "leaves": []}
    for k, v in doc.items():
        if k != coll:
            fr["leaves"].append(finish_leaf({"class": "pinned", "note": "document header"}, f"{name}.{k}", v))
    fr["leaves"].append({"key": f"{name}.{coll}[{idf}]#members", "class": "members", "op": members_op, "registered": sorted(x[idf] for x in doc[coll]), "rationale": rationale})
    sub = {"key": f"{name}.{coll}[{idf}=*]", "class": "pinned", "subtree": True, "note": "each registered member is content-registered as a whole", "digests": {}}
    for x in doc[coll]:
        sub["digests"][f"{name}.{coll}[{idf}={x[idf]}]"] = [L.vdigest(x)]
    fr["leaves"].append(sub)
    return fr


def kernel_yaml_rule(kdir):
    doc = L.load_doc(os.path.join(kdir, "KERNEL.yaml"))
    fr = {"path": "KERNEL.yaml", "mode": "structured", "name": "KERNEL", "collections": [], "leaves": []}
    fr["leaves"].append({"key": "KERNEL.framework", "class": "floor", "op": "equals", "value": doc["framework"]})
    bound = {"version": "release.version", "kernel_contract_version": "compatibility.kernel_contract_version", "cli_version": "compatibility.cli",
             "runtime_version": "compatibility.runtime", "supported_from_versions": "compatibility.supported_from_versions"}
    for k, f in bound.items():
        fr["leaves"].append({"key": f"KERNEL.{k}", "class": "release_bound", "statement_field": f,
                             "rationale": "must equal the signed release statement (04 V8/V11); decides compatibility only, never eligibility, floors or gates"})
    for k in doc["schema_versions"]:
        fr["leaves"].append({"key": f"KERNEL.schema_versions.{k}", "class": "release_bound", "statement_field": "compatibility.schema_versions",
                             "rationale": "must equal the signed release statement; selects record-schema versions, validated against the pinned schemas"})
    for k in ("framework_revision", "payload_dirs"):
        fr["leaves"].append(finish_leaf({"class": "pinned"}, f"KERNEL.{k}", doc[k]))
    for k, v in doc["adapter_versions"].items():
        fr["leaves"].append(finish_leaf({"class": "pinned"}, f"KERNEL.adapter_versions.{k}", v))
    return fr


def file_digests(kdir, rels):
    return {r: [L.fdigest(os.path.join(kdir, r))] for r in rels}


def main():
    kdir = os.path.abspath(sys.argv[1])
    files = L.kernel_files(kdir)
    prec = L.load_doc(os.path.join(kdir, "policies/POLICY_PRECEDENCE.yaml"))
    prec_rules = [L.rule_tuple(r) for r in prec["rules"]]
    inv = {
        "schema": "governance-os.constitutional-surface-inventory", "schema_version": 1, "csi_version": 1,
        "status": "PROPOSED (RoT-1 revision 3) - draft surface section of Trust Policy v1; not signed, not active, not approved",
        "floor_schema_version": L.FLOOR_SCHEMA_VERSION, "default": "deny",
        "derived_from": {"kernel_dir": os.path.relpath(kdir, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))),
                         "kernel_version": L.load_doc(os.path.join(kdir, "KERNEL.yaml"))["version"],
                         "file_count": len(files), "tree_digest_of_classified_files": "sha256:" + hashlib.sha256(json.dumps(file_digests(kdir, files), sort_keys=True).encode()).hexdigest()},
        "vocabulary": {"file_modes": sorted(L.FILE_MODES), "leaf_classes": sorted(L.LEAF_CLASSES), "floor_ops": sorted(L.FLOOR_OPS), "member_ops": sorted(L.MEMBER_OPS),
                       "orders": L.ORDERS, "precedence_modes": sorted(L.MODES)},
        "precedence": {"default_mode": prec["default_mode"], "rules": prec_rules},
        "never_exception_relaxable_prefixes": list(L.NEVER_EXCEPTION_RELAXABLE_PREFIXES),
        "rationale": RATIONALE,
        "files": [],
    }
    for name in POLICIES:
        inv["files"].append(policy_file_rule(kdir, name, prec_rules, prec["default_mode"]))
    inv["files"].append(roles_rule(kdir))
    inv["files"].append(keyed_pinned_rule(kdir, "constitution/HARD_INVARIANTS.yaml", "HARD_INVARIANTS", "invariants", "id", "ids_equal",
                                          "invariant text is copied verbatim into agent adapters; ids and statements are registered"))
    inv["files"].append(kernel_yaml_rule(kdir))
    tools_reg = "tools/registry/TOOLS.yaml"
    if os.path.exists(os.path.join(kdir, tools_reg)) or True:
        src = kdir if os.path.exists(os.path.join(kdir, tools_reg)) else os.path.join(kdir, "..")
        fr = keyed_pinned_rule(src, tools_reg, "TOOLS_REGISTRY", "tools", "tool_id", "ids_subset",
                               "tool descriptors carry executed install and health commands; a new or edited descriptor needs registration, removal is a narrowing")
        inv["files"].append(fr)
    pinned_paths = ["policies/ENFORCEMENT_MAP.yaml", "commands/COMMAND_CONTRACT.yaml", "constitution/CONSTITUTION.md", "tools/mcp/registry.yaml"]
    for p in pinned_paths:
        src = kdir if os.path.exists(os.path.join(kdir, p)) else os.path.join(kdir, "..")
        inv["files"].append({"path": p, "mode": "pinned_file", "digests": file_digests(src, [p]),
                             "rationale": "non-orderable constitutional content (enforcement map, command contract, constitution text, MCP registry)"})
    for g, why in [("adapters/*", "agent-facing adapter descriptors and templates"), ("overlay-templates/*.yaml", "defaults written into every new project overlay"),
                   ("schemas/*.schema.json", "validate records, overlays, exceptions, gates, registries and migrations"), ("skills/SKL-*.yaml", "agent-facing skill instructions"),
                   ("taxonomy/*.yaml", "readiness and capability vocabularies consumed by readiness gating")]:
        inv["files"].append({"glob": g, "mode": "pinned_file", "digests": file_digests(kdir, [f for f in files if __import__("fnmatch").fnmatchcase(f, g)]), "rationale": why})
    mig_src = kdir if any(f.startswith("migrations/") for f in files) else os.path.join(kdir, "..")
    inv["files"].append({"glob": "migrations/M-*.yaml", "mode": "transaction_input",
                         "rationale": "consumed only inside the install transaction from authenticated buffers (04 V10); overlay effects are computed and every weakening needs a trust gate (19 §9); cannot change any floor, pin or registration"})
    inv["files"].append({"path": "migrations/README.md", "mode": "informational_file", "rationale": "documentation; no runtime reader"})
    inv["files"].append({"path": "tools/installers/README.md", "mode": "informational_file", "rationale": "documentation; no runtime reader"})
    yaml.safe_dump(inv, sys.stdout, sort_keys=False, width=200, allow_unicode=False)


if __name__ == "__main__":
    main()
