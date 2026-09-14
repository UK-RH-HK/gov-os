#!/usr/bin/env python3
"""Constitutional Surface Inventory (CSI) — reference library for RoT-1 revision 3 (`19` §2–§5, `23`).

PROPOSED architecture artefact, not the Governance OS implementation. It defines, executably, the floor semantics the
revision-3 pack specifies so the coverage checker (`csi_check.py`), the inventory derivation (`csi_derive.py`) and the
architect evidence (`../evidence/P1r3-*`) share one definition:

* enumeration of every constitutional leaf of a kernel tree, driven by the inventory (never by the tree being judged);
* default deny: a file or leaf that matches no inventory rule is `UNCLASSIFIED`;
* the closed class and operator vocabulary of `floor_schema_version: 2` (`19` §4);
* the strength lattice and join for POLICY_PRECEDENCE rules, evaluated per concrete key (`19` §4.4);
* evaluation of a candidate kernel against the inventory (the E7 surface check) and the effective value of every leaf.

Only the Python standard library and PyYAML are used.
"""
import copy, fnmatch, hashlib, json, os, re
from decimal import Decimal, InvalidOperation

import yaml

FLOOR_SCHEMA_VERSION = 2
ORDERS = {
    "level": ["L0", "L1", "L2", "L3", "L4", "L5"],
    "radius": ["R0", "R1", "R2", "R3", "R4", "R5"],
    "tier": ["none", "T0", "T1", "T2", "T3"],
    "reasoning": ["none", "low", "medium", "high", "extra_high"],
}
FILE_MODES = {"structured", "pinned_file", "transaction_input", "informational_file"}
LEAF_CLASSES = {"floor", "pinned", "members", "precedence", "release_bound", "project_tunable", "informational", "collection_id", "covered_by_collection"}
FLOOR_OPS = {"level_at_least", "level_at_most", "ordered_at_least", "ordered_at_most", "decimal_at_least", "decimal_at_most",
             "set_superset", "set_subset", "bool_toward", "equals"}
MEMBER_OPS = {"ids_equal", "ids_subset", "ids_superset"}
MODES = {"immutable", "floor", "ceiling", "additive", "shrink_only", "strengthen_only_bool", "overridable"}
# Keys a PROJECT_EXCEPTIONS entry may never relax, independent of any kernel or TPS attribute (compiled rule, `19` §5.3).
NEVER_EXCEPTION_RELAXABLE_PREFIXES = ("SECURITY_POLICY.", "AUTHORITY_POLICY.", "HUMAN_GATE_POLICY.", "TOOL_POLICY.", "POLICY_PRECEDENCE.", "ROLES.")


# ------------------------------------------------------------------------------------------------ canonical values
def canon(v):
    """Value canonical form for digests: GOV-JCS-1 plus decimal strings for YAML floats and strings for YAML dates."""
    if v is None or isinstance(v, bool) or isinstance(v, int):
        return v
    if isinstance(v, float):
        return {"$decimal": repr(v)}
    if isinstance(v, str):
        return v
    if isinstance(v, list):
        return [canon(x) for x in v]
    if isinstance(v, dict):
        return {str(k): canon(x) for k, x in v.items()}
    return str(v)


def vdigest(v):
    return "sha256:" + hashlib.sha256(json.dumps(canon(v), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def fdigest(path):
    return "sha256:" + hashlib.sha256(open(path, "rb").read()).hexdigest()


# ------------------------------------------------------------------------------------------------ keys
def split_key(key):
    """Split a dotted key on dots outside brackets: `rules[key=A.b.*].mode` -> ['rules[key=A.b.*]', 'mode']."""
    out, cur, depth = [], "", 0
    for ch in key:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        if ch == "." and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return out


def seg_match(pat, seg):
    if pat == "*":
        return "[" not in seg
    m = re.fullmatch(r"(.+)\[([A-Za-z_]+)=\*\]", pat)
    if m:
        m2 = re.fullmatch(r"(.+)\[([A-Za-z_]+)=(.*)\]", seg)
        return bool(m2) and m2.group(1) == m.group(1) and m2.group(2) == m.group(2)
    return pat == seg


def key_match(pattern, key):
    ps, ks = split_key(pattern), split_key(key)
    return len(ps) == len(ks) and all(seg_match(p, k) for p, k in zip(ps, ks))


def precedence_key_matches(pattern, key):
    """runtime/src/policy_precedence.rs key_matches: `*` one segment; trailing `*` one or more segments."""
    ps, ks = pattern.split("."), key.split(".")
    if ps and ps[-1] == "*" and len(ps) <= len(ks):
        head = ps[:-1]
        if all(p == "*" or p == k for p, k in zip(head, ks)) and len(ks) > len(head):
            return True
    return len(ps) == len(ks) and all(p == "*" or p == k for p, k in zip(ps, ks))


# ------------------------------------------------------------------------------------------------ tree and files
def kernel_files(kdir):
    out = []
    for dp, dns, fns in os.walk(kdir):
        dns.sort()
        for fn in sorted(fns):
            rel = os.path.relpath(os.path.join(dp, fn), kdir).replace(os.sep, "/")
            if rel == "KERNEL_MANIFEST.json":
                continue  # excluded by the tree rules (07 §5.1 rule 4); never part of the RoT-1 kernel
            out.append(rel)
    return out


def match_file_rule(inv, rel):
    exact = [f for f in inv["files"] if f.get("path") == rel]
    if exact:
        return exact if len(exact) > 1 else exact[0]
    globs = [f for f in inv["files"] if f.get("glob") and fnmatch.fnmatchcase(rel, f["glob"])]
    if len(globs) == 1:
        return globs[0]
    return globs if globs else None


def load_doc(path):
    if path.endswith((".yaml", ".yml")):
        return yaml.safe_load(open(path, encoding="utf-8"))
    if path.endswith(".json"):
        return json.load(open(path, encoding="utf-8"))
    raise ValueError("structured file must be YAML or JSON: " + path)


# ------------------------------------------------------------------------------------------------ leaf enumeration
def enumerate_leaves(doc, fr):
    """Enumerate constitutional leaves of one structured document, using only the inventory's declarations."""
    name = fr["name"]
    colls = {c["path"]: c for c in fr.get("collections", [])}
    subtree_pats = [l["key"] for l in fr.get("leaves", []) if l.get("subtree")]
    out, structure = [], []

    def is_subtree(key):
        return any(key_match(p, key) for p in subtree_pats)

    def walk(node, key):
        rel = key[len(name) + 1:] if key.startswith(name + ".") else ""
        if key != name and is_subtree(key):
            out.append((key, node))
            return
        if rel in colls:
            c = colls[rel]
            idf = c["id_field"]
            ok = isinstance(node, list) and all(isinstance(x, dict) and isinstance(x.get(idf), str) for x in node)
            ids = [x[idf] for x in node] if ok else []
            if not ok or len(set(ids)) != len(ids):
                structure.append({"key": key, "problem": f"declared collection is not a list of objects with unique string '{idf}'"})
                out.append((key + "#structure", node))
                return
            out.append((f"{key}[{idf}]#members", sorted(ids)))
            for x in node:
                walk(x, f"{key}[{idf}={x[idf]}]")
            return
        if isinstance(node, dict) and node:
            for k, v in node.items():
                walk(v, f"{key}.{k}")
            return
        if key == name:
            structure.append({"key": key, "problem": "document root is not a non-empty mapping"})
        out.append((key, node))

    walk(doc, name)
    return out, structure


def match_leaf_rule(fr, key):
    hits = [l for l in fr.get("leaves", []) if key_match(l["key"], key)]
    exact = [l for l in hits if "*" not in l["key"]]
    if len(exact) == 1:
        return exact[0]
    if len(hits) == 1:
        return hits[0]
    return hits if hits else None


# ------------------------------------------------------------------------------------------------ operators
def _rank(order, v):
    try:
        return order.index(v)
    except ValueError:
        return None


def _dec(v):
    try:
        return Decimal(str(v))
    except (InvalidOperation, ValueError):
        return None


def op_holds(rule, v):
    op, fv = rule["op"], rule["value"]
    order = rule.get("order") or ORDERS.get(rule.get("kind", "level"))
    if op in ("level_at_least", "ordered_at_least"):
        a, b = _rank(order, v), _rank(order, fv)
        return v is None or (a is not None and a >= b)
    if op in ("level_at_most", "ordered_at_most"):
        a, b = _rank(order, v), _rank(order, fv)
        return v is None or (a is not None and a <= b)
    if op == "decimal_at_least":
        return v is None or (_dec(v) is not None and _dec(v) >= _dec(fv))
    if op == "decimal_at_most":
        return v is None or (_dec(v) is not None and _dec(v) <= _dec(fv))
    if op == "set_superset":
        return v is None or (isinstance(v, list) and all(canon(x) in [canon(y) for y in v] for x in fv))
    if op == "set_subset":
        return v is None or (isinstance(v, list) and all(canon(x) in [canon(y) for y in fv] for x in v))
    if op == "bool_toward":
        return v is None or v == rule["strict"] or fv != rule["strict"]
    if op == "equals":
        return canon(v) == canon(fv)
    raise ValueError("unknown operator " + op)


def op_stronger_than_floor(rule, v):
    """True when the kernel value is strictly stronger than the registered floor (FLOOR_NOT_REGISTERED at the producer)."""
    op, fv = rule["op"], rule["value"]
    order = rule.get("order") or ORDERS.get(rule.get("kind", "level"))
    if v is None:
        return False
    if op in ("level_at_least", "ordered_at_least"):
        return _rank(order, v) is not None and _rank(order, v) > _rank(order, fv)
    if op in ("level_at_most", "ordered_at_most"):
        return _rank(order, v) is not None and _rank(order, v) < _rank(order, fv)
    if op == "decimal_at_least":
        return _dec(v) is not None and _dec(v) > _dec(fv)
    if op == "decimal_at_most":
        return _dec(v) is not None and _dec(v) < _dec(fv)
    if op == "set_superset":
        return isinstance(v, list) and len({json.dumps(canon(x)) for x in v} - {json.dumps(canon(x)) for x in fv}) > 0
    if op == "set_subset":
        return isinstance(v, list) and len({json.dumps(canon(x)) for x in fv} - {json.dumps(canon(x)) for x in v}) > 0
    if op == "bool_toward":
        return v == rule["strict"] and fv != rule["strict"]
    return False


def op_join(rule, v):
    """Effective value = registered floor joined with the kernel value (never weaker than the floor)."""
    op, fv = rule["op"], rule["value"]
    order = rule.get("order") or ORDERS.get(rule.get("kind", "level"))
    if v is None:
        return copy.deepcopy(fv)
    if op in ("level_at_least", "ordered_at_least"):
        a, b = _rank(order, v), _rank(order, fv)
        return v if a is not None and a >= b else fv
    if op in ("level_at_most", "ordered_at_most"):
        a, b = _rank(order, v), _rank(order, fv)
        return v if a is not None and a <= b else fv
    if op == "decimal_at_least":
        return v if _dec(v) is not None and _dec(v) >= _dec(fv) else fv
    if op == "decimal_at_most":
        return v if _dec(v) is not None and _dec(v) <= _dec(fv) else fv
    if op == "set_superset":
        base = list(v) if isinstance(v, list) else []
        seen = [canon(x) for x in base]
        return base + [x for x in fv if canon(x) not in seen]
    if op == "set_subset":
        allowed = [canon(x) for x in fv]
        return [x for x in (v if isinstance(v, list) else []) if canon(x) in allowed]
    if op == "bool_toward":
        return rule["strict"] if (v == rule["strict"] or fv == rule["strict"]) else v
    if op == "equals":
        return copy.deepcopy(fv)
    raise ValueError(op)


# ------------------------------------------------------------------------------------------------ precedence lattice (19 §4.4)
def rule_tuple(r):
    return {"key": r["key"], "mode": r.get("mode"), "kind": r.get("kind"), "order": r.get("order"),
            "strict_value": r.get("strict_value"), "exception_relaxable": bool(r.get("exception_relaxable", False))}


def rule_for(rules, key):
    for r in rules:
        if precedence_key_matches(r["key"], key):
            return r
    return None


def effective_rule(rules, default_mode, key):
    r = rule_for(rules, key)
    return rule_tuple(r) if r else {"key": "<default>", "mode": default_mode, "kind": None, "order": None, "strict_value": None, "exception_relaxable": False}


def rule_ge(a, b):
    """a is at least as strong as b for the project layer."""
    if a["mode"] not in MODES or b["mode"] not in MODES:
        return False
    if a["exception_relaxable"] and not b["exception_relaxable"]:
        return False
    if a["mode"] == "immutable" or b["mode"] == "overridable":
        return True
    if a["mode"] != b["mode"]:
        return False
    if a["mode"] in ("floor", "ceiling"):
        return a["kind"] == b["kind"] and (a["order"] or None) == (b["order"] or None)
    if a["mode"] == "strengthen_only_bool":
        return a["strict_value"] == b["strict_value"]
    return True


def rule_join(a, b):
    if rule_ge(a, b):
        return a
    if rule_ge(b, a):
        return b
    return {"key": "<join>", "mode": "immutable", "kind": None, "order": None, "strict_value": None, "exception_relaxable": False}


def precedence_universe(policy_leaf_keys, rules_a, rules_b):
    u = set(policy_leaf_keys)
    for r in list(rules_a) + list(rules_b):
        u.add(r["key"].replace("*", "p3probe"))
    return sorted(u)


# ------------------------------------------------------------------------------------------------ evaluation of a kernel against the inventory
def evaluate(inv, kdir, embedded_dir=None, named_policy_inv=None):
    """Evaluate a kernel tree against an inventory (the effective TPS surface section).

    Returns coverage, violations and per-leaf effective values. `named_policy_inv` is the surface of the TPS named by the
    release's own `trust_references.trust_policy_version` (floor violations are judged against it; joins use `inv`).
    """
    named = named_policy_inv or inv
    res = {"unclassified_files": [], "ambiguous_files": [], "unclassified_leaves": [], "ambiguous_leaves": [], "structure": [],
           "violations": [], "stronger_than_registered": [], "consistency": [], "counts": {}, "effective": {}, "files": {}}
    policy_leaf_keys, kernel_rules, default_mode = [], None, None
    docs = {}
    for rel in kernel_files(kdir):
        fr = match_file_rule(inv, rel)
        if fr is None:
            res["unclassified_files"].append(rel)
            continue
        if isinstance(fr, list):
            res["ambiguous_files"].append({"file": rel, "rules": [f.get("path") or f.get("glob") for f in fr]})
            continue
        mode = fr["mode"]
        res["counts"][mode] = res["counts"].get(mode, 0) + 1
        path = os.path.join(kdir, rel)
        if mode == "pinned_file":
            d = fdigest(path)
            ok = d in fr.get("digests", {}).get(rel, [])
            res["files"][rel] = {"mode": mode, "digest": d, "registered": ok}
            if not ok:
                res["violations"].append({"file": rel, "class": "pinned_file", "reason": "file digest not registered", "digest": d})
            continue
        if mode in ("transaction_input", "informational_file"):
            res["files"][rel] = {"mode": mode, "digest": fdigest(path)}
            continue
        try:
            doc = load_doc(path)
        except Exception as e:
            res["structure"].append({"file": rel, "problem": f"unparseable: {e}"})
            continue
        docs[rel] = (fr, doc)
        leaves, structure = enumerate_leaves(doc, fr)
        for s in structure:
            s["file"] = rel
        res["structure"] += structure
        res["files"][rel] = {"mode": mode, "leaves": len(leaves)}
        for key, v in leaves:
            if key.endswith("#structure"):
                continue
            lr = match_leaf_rule(fr, key)
            if lr is None:
                res["unclassified_leaves"].append({"file": rel, "key": key})
                continue
            if isinstance(lr, list):
                res["ambiguous_leaves"].append({"file": rel, "key": key, "rules": [x["key"] for x in lr]})
                continue
            cls = lr["class"]
            res["counts"][cls] = res["counts"].get(cls, 0) + 1
            if fr.get("policy_file") and cls not in ("collection_id", "covered_by_collection"):
                if key.endswith("#members"):
                    policy_leaf_keys.append(key.split("[")[0])
                elif "[" not in key:
                    policy_leaf_keys.append(key)
            eff = v
            if cls == "floor":
                nlr = match_leaf_rule(named_file_rule(named, rel) or fr, key)
                nlr = nlr if isinstance(nlr, dict) and nlr.get("class") == "floor" else lr
                if not op_holds(nlr, v):
                    res["violations"].append({"file": rel, "key": key, "class": "floor", "op": nlr["op"], "floor": nlr["value"], "kernel": v})
                if op_stronger_than_floor(nlr, v):
                    res["stronger_than_registered"].append({"file": rel, "key": key, "op": nlr["op"], "floor": nlr["value"], "kernel": v})
                eff = op_join(lr, v)
            elif cls == "pinned":
                d = vdigest(v)
                if d not in lr.get("digests", {}).get(key, []):
                    res["violations"].append({"file": rel, "key": key, "class": "pinned", "reason": "value digest not registered", "digest": d})
                    eff = {"$unavailable": "pinned value not registered"}
            elif cls == "members":
                reg = lr["registered"]
                got = v if isinstance(v, list) else []
                missing, added = sorted(set(reg) - set(got)), sorted(set(got) - set(reg))
                bad = (lr["op"] in ("ids_equal", "ids_superset") and missing) or (lr["op"] in ("ids_equal", "ids_subset") and added)
                if bad:
                    res["violations"].append({"file": rel, "key": key, "class": "members", "op": lr["op"], "missing": missing, "unregistered": added})
                eff = sorted(set(got) & set(reg)) if lr["op"] != "ids_superset" else got
            elif cls == "precedence":
                pass  # rules are read from the document below and compared per concrete key
            res["effective"][key] = eff
        if fr.get("name") == "POLICY_PRECEDENCE":
            default_mode = doc.get("default_mode") if isinstance(doc, dict) else None
            kernel_rules = [rule_tuple(r) for r in (doc.get("rules") or [])] if isinstance(doc, dict) else []
    # precedence floor, per concrete key of the policy universe
    reg = inv.get("precedence") or {}
    if reg:
        reg_rules = reg["rules"]
        kr = kernel_rules if kernel_rules is not None else []
        dm = default_mode or "immutable"
        weaker = []
        for key in precedence_universe(policy_leaf_keys, reg_rules, kr):
            a = effective_rule(kr, dm, key)
            b = effective_rule(reg_rules, reg["default_mode"], key)
            if not rule_ge(a, b):
                weaker.append({"key": key, "kernel": a, "registered": b, "effective": rule_join(a, b)})
        res["precedence_weaker_keys"] = weaker
        if weaker:
            res["violations"].append({"class": "precedence", "reason": "effective POLICY_PRECEDENCE rule weaker than registered for some keys", "keys": [w["key"] for w in weaker][:40], "count": len(weaker)})
        res["effective_precedence"] = {w["key"]: w["effective"] for w in weaker}
    res["surface_ok"] = not (res["unclassified_files"] or res["ambiguous_files"] or res["unclassified_leaves"] or res["ambiguous_leaves"] or res["structure"])
    res["eligible_surface"] = res["surface_ok"] and not res["violations"] and not res["stronger_than_registered"]
    return res


def named_file_rule(inv, rel):
    fr = match_file_rule(inv, rel)
    return fr if isinstance(fr, dict) else None


def exception_may_relax(key, registered_rule, kernel_rule):
    """Effective exception_relaxable (19 §5.3): TPS-registered AND kernel, and never for the compiled prefixes."""
    if key.startswith(NEVER_EXCEPTION_RELAXABLE_PREFIXES):
        return False
    return bool(registered_rule.get("exception_relaxable")) and bool(kernel_rule.get("exception_relaxable"))
