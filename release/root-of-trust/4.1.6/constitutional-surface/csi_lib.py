#!/usr/bin/env python3
"""Constitutional Surface Inventory (CSI) — reference library for RoT-1 revision 4 (`19` §2–§5, `23`, `26` §6).

PROPOSED architecture artefact, not the Governance OS implementation. It defines, executably, the floor semantics the
revision-4 pack specifies, so the coverage checker (`csi_check.py`), the inventory derivation (`csi_derive.py`) and the
architect evidence (`../evidence/P1r4-*`) share one definition.

Kept from revision 3 (confirmed sound by review r3):
* enumeration of every constitutional leaf of a kernel tree, driven by the inventory (never by the tree being judged);
* default deny: a file or leaf that matches no inventory rule is `UNCLASSIFIED`;
* the closed class and operator vocabulary, and value joins for floor leaves.

Changed in revision 4 (blocking class BC-1: RV3-H1, with the roots of RV3-M5 and RV3-M7; carried CR-02, CR-07, CR-08):
* precedence is registered exactly and read only from the Trust Policy: a kernel's POLICY_PRECEDENCE must equal the named
  registration, and the project-layer rule of every key is taken from registrations, never from the kernel (`23` §4);
* the strength order over precedence rules is sound in both directions: `a >= b` only if `a` refuses every weakening `b`
  refuses AND admits every strengthening `b` admits (`23` §4.2);
* the project layer is a directed join: admitted strengthening is applied, unadmitted weakening is refused, and no
  refusal discards an admitted strengthening (`19` §5.3);
* absence is not neutral: every registered file and leaf is required unless the inventory declares it optional under the
  presence lint (`23` §3.5);
* one YAML profile for producer, CI and binary: YAML 1.2 core booleans; no anchors, aliases, merge keys, explicit tags,
  duplicate keys or non-string keys (`23` §3.6);
* migration operations are default-deny over the Overlay Surface (`23` §11);
* project-owned strength is a set of requirements evaluated over the effective policy and the overlay inputs, whatever
  changed them (`26` §6).

Only the Python standard library and PyYAML are used.
"""
import copy, fnmatch, hashlib, json, os, re
from decimal import Decimal, InvalidOperation

import yaml

FLOOR_SCHEMA_VERSION = 3
OPERATOR_VOCABULARY = "floor-ops/3"
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
PRESENCE = {"required", "optional"}
# Leaf classes that may be declared optional (their absence can never weaken a security decision point, `23` §3.5).
OPTIONAL_LEAF_CLASSES = {"informational", "covered_by_collection", "collection_id"}
# File modes that may be declared optional; a structured file may be optional only when every leaf rule is pinned,
# informational, collection plumbing or an ids_subset membership (absence then removes capability, never a control).
OPTIONAL_FILE_MODES = {"pinned_file", "informational_file", "transaction_input"}
# Keys a PROJECT_EXCEPTIONS entry may never relax, independent of any kernel or TPS attribute (compiled rule, `19` §5.3).
NEVER_EXCEPTION_RELAXABLE_PREFIXES = ("SECURITY_POLICY.", "AUTHORITY_POLICY.", "HUMAN_GATE_POLICY.", "TOOL_POLICY.", "POLICY_PRECEDENCE.", "ROLES.")
# Directions of the Overlay Surface (`23` §11): which change of an overlay input is a strengthening.
OVERLAY_DIRECTIONS = {"none", "equal", "up", "down", "add", "remove", "strict_true", "strict_false", "classification_superset",
                      "contract_at_least", "map_subset", "entries_subset", "applicable_superset", "effective_policy", "file_set_subset"}
MIGRATION_OPS_NO_TARGET = {"note", "require_index_rebuild", "regenerate_adapters"}
MIGRATION_OPS_OVERLAY = {"add_overlay_file_from_template", "rename_overlay_file", "set_overlay_key", "rename_overlay_key", "delete_overlay_key", "set_overlay_rule"}


# ------------------------------------------------------------------------------------------------ YAML profile (23 §3.6, CR-08)
YAML11_ONLY_BOOL = re.compile(r"^(?:y|Y|yes|Yes|YES|n|N|no|No|NO|on|On|ON|off|Off|OFF)$")
CORE_BOOL = re.compile(r"^(?:true|True|TRUE|false|False|FALSE)$")


class ProfileError(ValueError):
    """A constitutional document violates the single YAML/JSON profile (`SURFACE_STRUCTURE(yaml_profile)`)."""


class StrictLoader(yaml.SafeLoader):
    """YAML 1.2 core booleans; duplicate and non-string mapping keys refused."""

    def construct_mapping(self, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=True)
            if not isinstance(key, str):
                raise ProfileError(f"non-string mapping key {key!r} at line {key_node.start_mark.line + 1}")
            if key in seen:
                raise ProfileError(f"duplicate mapping key {key!r} at line {key_node.start_mark.line + 1}")
            seen.add(key)
        return super().construct_mapping(node, deep=deep)


StrictLoader.yaml_implicit_resolvers = {k: [(t, r) for (t, r) in v if t != "tag:yaml.org,2002:bool"]
                                        for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()}
StrictLoader.add_implicit_resolver("tag:yaml.org,2002:bool", CORE_BOOL, list("tTfF"))


def yaml_profile_problems(text):
    """Anchors, aliases, explicit tags, merge keys and YAML-1.1-only boolean tokens (read differently by producer and binary)."""
    probs = []
    try:
        for ev in yaml.parse(text, Loader=yaml.SafeLoader):
            line = ev.start_mark.line + 1
            if isinstance(ev, yaml.AliasEvent):
                probs.append(f"alias *{ev.anchor} at line {line}")
                continue
            if getattr(ev, "anchor", None):
                probs.append(f"anchor &{ev.anchor} at line {line}")
            if isinstance(ev, (yaml.ScalarEvent, yaml.MappingStartEvent, yaml.SequenceStartEvent)) and getattr(ev, "tag", None) is not None:
                if not (isinstance(ev, (yaml.MappingStartEvent, yaml.SequenceStartEvent)) and ev.implicit):
                    probs.append(f"explicit tag {ev.tag} at line {line}")
            if isinstance(ev, yaml.ScalarEvent) and ev.style is None:
                if YAML11_ONLY_BOOL.match(ev.value):
                    probs.append(f"YAML 1.1 boolean token {ev.value!r} at line {line} (a string under the single profile)")
                if ev.value == "<<":
                    probs.append(f"merge key at line {line}")
    except yaml.YAMLError as e:
        probs.append(f"unparseable: {e}")
    return probs


def load_doc(path, strict=True):
    raw = open(path, "rb").read()
    if path.endswith((".yaml", ".yml")):
        text = raw.decode("utf-8")
        if not strict:
            return yaml.safe_load(text)
        probs = yaml_profile_problems(text)
        if probs:
            raise ProfileError("; ".join(probs[:5]))
        return yaml.load(text, Loader=StrictLoader)
    if path.endswith(".json"):
        def hook(pairs):
            d = {}
            for k, v in pairs:
                if k in d:
                    raise ProfileError(f"duplicate JSON member {k!r}")
                d[k] = v
            return d
        return json.loads(raw.decode("utf-8"), object_pairs_hook=hook)
    raise ValueError("structured file must be YAML or JSON: " + path)


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


def deep_get(doc, dotted):
    cur = doc
    for part in dotted.split(".") if dotted else []:
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


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


def registered_paths(fr):
    """Paths a file rule registers: its path, or every path its registered digests name (`23` §3.5)."""
    if fr.get("path"):
        return [fr["path"]]
    return sorted((fr.get("digests") or {}).keys())


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


def required_leaf_keys(fr):
    """Registered leaves that must be present (`23` §3.5): every concrete leaf rule, including collection memberships."""
    out = []
    for l in fr.get("leaves", []):
        if "*" in l["key"] or l.get("presence", "required") != "required" or l.get("class") in OPTIONAL_LEAF_CLASSES:
            continue
        out.append(l["key"])
    return out


# ------------------------------------------------------------------------------------------------ operators
def _rank(order, v):
    try:
        return order.index(v)
    except (ValueError, AttributeError):
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


# ------------------------------------------------------------------------------------------------ strength direction (23 §4.2)
_MODE_DIRECTION = {"floor": "up", "ceiling": "down", "additive": "add", "shrink_only": "remove"}
_DIRECTION_MODE = {"up": "floor", "down": "ceiling", "add": "additive", "remove": "shrink_only", "strict_true": "strengthen_only_bool", "strict_false": "strengthen_only_bool"}
_OPPOSITE = {"up": "down", "down": "up", "add": "remove", "remove": "add", "strict_true": "strict_false", "strict_false": "strict_true"}


def leaf_direction(lr):
    """The registered strength direction of a constitutional leaf, from its root-signed classification (never from a rule)."""
    if not isinstance(lr, dict):
        return "none"
    cls, op = lr.get("class"), lr.get("op")
    if cls == "floor":
        if op in ("level_at_least", "ordered_at_least", "decimal_at_least"):
            return "up"
        if op in ("level_at_most", "ordered_at_most", "decimal_at_most"):
            return "down"
        if op == "set_superset":
            return "add"
        if op == "set_subset":
            return "remove"
        if op == "bool_toward":
            return "strict_true" if lr.get("strict") is True else "strict_false"
        return "none"
    if cls == "members":
        return {"ids_superset": "add", "ids_subset": "remove"}.get(op, "none")
    return "none"


def mode_direction(rule):
    m = rule.get("mode")
    if m in _MODE_DIRECTION:
        return _MODE_DIRECTION[m]
    if m == "strengthen_only_bool":
        return "strict_false" if rule.get("strict_value") is False else "strict_true"
    return None


def admitted(rule, direction):
    """Which project changes a precedence rule admits on a key whose strength direction is `direction`:
    's' = a strengthening, 'w' = a weakening. Unknown modes are treated as admitting weakening and no strengthening."""
    m = rule.get("mode")
    if m not in MODES:
        return {"w"}
    if m == "overridable":
        return {"w"} if direction == "none" else {"s", "w"}
    if m == "immutable":
        return set()
    if direction == "none":
        return {"w"}
    return {"s"} if mode_direction(rule) == direction else {"w"}


def _direction(a, b, direction):
    if direction:
        return direction
    for r in (b, a):
        d = mode_direction(r)
        if d:
            return d
    return "none"


def _same_comparison(a, b):
    if a.get("mode") in ("floor", "ceiling") and b.get("mode") == a.get("mode"):
        return (a.get("kind") or None) == (b.get("kind") or None) and (a.get("order") or None) == (b.get("order") or None)
    return True


# ------------------------------------------------------------------------------------------------ precedence (23 §4)
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


def rule_ge(a, b, direction=None):
    """a is at least as strong as b for the project layer, in BOTH directions (`23` §4.2 revision 4):
    a admits no weakening b refuses, a admits every strengthening b admits, and exception relaxation does not widen.
    The direction is the key's registered classification; when omitted it is inferred from b's, then a's, mode."""
    if a.get("mode") not in MODES or b.get("mode") not in MODES:
        return False
    d = _direction(a, b, direction)
    A, B = admitted(a, d), admitted(b, d)
    if "w" in A and "w" not in B:
        return False
    if "s" in B and "s" not in A:
        return False
    if bool(a.get("exception_relaxable")) and not bool(b.get("exception_relaxable")):
        return False
    return _same_comparison(a, b)


def rule_from_admitted(J, direction, exc, candidates=()):
    out = {"key": "<join>", "mode": None, "kind": None, "order": None, "strict_value": None, "exception_relaxable": exc}
    if not J:
        out["mode"] = "immutable"
    elif J == {"s", "w"} or (direction == "none" and J == {"w"}):
        out["mode"] = "overridable"
    else:
        want = direction if J == {"s"} else _OPPOSITE.get(direction, direction)
        mode = _DIRECTION_MODE.get(want, "immutable")
        out["mode"] = mode
        if mode == "strengthen_only_bool":
            out["strict_value"] = want == "strict_true"
        for c in candidates:
            if c.get("mode") == mode:
                out["kind"], out["order"] = c.get("kind"), c.get("order")
                break
    return out


def rule_join(a, b, direction=None):
    """The strongest combination of two rules for the project layer: a weakening is admitted only if both admit it, a
    strengthening is admitted if either admits it; exception relaxation only if both. Never discards admitted strengthening."""
    d = _direction(a, b, direction)
    A, B = admitted(a, d), admitted(b, d)
    J = ((A & B) & {"w"}) | ((A | B) & {"s"})
    exc = bool(a.get("exception_relaxable")) and bool(b.get("exception_relaxable"))
    for r, R in ((b, B), (a, A)):
        if R == J and bool(r.get("exception_relaxable")) == exc and r.get("mode") in MODES:
            return dict(r)
    return rule_from_admitted(J, d, exc, (b, a))


def precedence_doc_rules(doc):
    return [rule_tuple(r) for r in (doc.get("rules") or []) if isinstance(r, dict) and "key" in r] if isinstance(doc, dict) else []


def precedence_mismatches(doc, registered):
    """Exact precedence registration (`23` §4.1): the kernel's ordered rule list and default_mode equal the registration."""
    if not isinstance(doc, dict):
        return [{"problem": "POLICY_PRECEDENCE is not a mapping"}]
    probs = []
    if doc.get("default_mode") != registered.get("default_mode"):
        probs.append({"field": "default_mode", "kernel": doc.get("default_mode"), "registered": registered.get("default_mode")})
    kr, rr = precedence_doc_rules(doc), [rule_tuple(r) for r in registered.get("rules", [])]
    for i in range(max(len(kr), len(rr))):
        a = kr[i] if i < len(kr) else None
        b = rr[i] if i < len(rr) else None
        if a != b:
            probs.append({"index": i, "kernel": a, "registered": b})
    return probs


def structured_rule_for_key(inv, key):
    name = key.split(".", 1)[0]
    for f in inv.get("files", []):
        if f.get("mode") == "structured" and f.get("name") == name:
            return f
    return None


def key_leaf_rule(inv, key):
    fr = structured_rule_for_key(inv, key)
    if not fr:
        return None
    lr = match_leaf_rule(fr, key)
    return lr if isinstance(lr, dict) else None


def key_direction(inv, key):
    return leaf_direction(key_leaf_rule(inv, key))


def effective_project_rule(inv, key, held_inv=None):
    """`19` §5.3 revision 4: the project-layer precedence rule of a concrete key comes from Trust Policy registrations only.
    `held_inv` is the registration this project's strength was recorded under; while a reduction against it has not been
    accepted by the per-project `policy_lowering` trust gate, the effective rule is the sound join of both."""
    reg = inv["precedence"]
    r = effective_rule(reg["rules"], reg["default_mode"], key)
    if held_inv is None:
        return r
    h = effective_rule(held_inv["precedence"]["rules"], held_inv["precedence"]["default_mode"], key)
    d = key_direction(held_inv, key)
    if d == "none":
        d = key_direction(inv, key)
    # a key without a concrete leaf rule (a rule pattern) takes its direction from the registered modes (lint-consistent)
    return rule_join(r, h, None if d == "none" else d)


def precedence_reductions(inv_old, inv_new, keys):
    """Computed reductions of precedence between two registrations (`19` §10.6 revision 4): the new rule is not at least as
    strong as the old one in both directions (a newly admitted weakening, or a removed admitted strengthening)."""
    out = []
    for k in keys:
        a = effective_rule(inv_new["precedence"]["rules"], inv_new["precedence"]["default_mode"], k)
        b = effective_rule(inv_old["precedence"]["rules"], inv_old["precedence"]["default_mode"], k)
        d = key_direction(inv_old, k)
        d = None if d == "none" else d
        if not rule_ge(a, b, d):
            d = _direction(a, b, d)
            A, B = admitted(a, d), admitted(b, d)
            out.append({"key": k, "direction": d, "old_mode": b["mode"], "new_mode": a["mode"],
                        "admits_new_weakening": "w" in A and "w" not in B, "removes_admitted_strengthening": "s" in B and "s" not in A,
                        "exception_relaxation_added": bool(a.get("exception_relaxable")) and not bool(b.get("exception_relaxable"))})
    return out


def precedence_universe(policy_leaf_keys, rules_a, rules_b):
    u = set(policy_leaf_keys)
    for r in list(rules_a) + list(rules_b):
        u.add(r["key"].replace("*", "p3probe"))
    return sorted(u)


# ------------------------------------------------------------------------------------------------ directed project join (19 §5.3)
def _rank_for(lr, v):
    op = lr.get("op", "") or ""
    if op.startswith("decimal"):
        return _dec(v)
    order = lr.get("order") or ORDERS.get(lr.get("kind") or "level")
    return _rank(order, v)


def project_apply(lr, rule, base, override):
    """Apply one project override leaf as a directed join. Returns (effective, applied, refused) where applied/refused list
    's' (strengthening component) and 'w' (weakening component). A refusal never discards an admitted component."""
    d = leaf_direction(lr)
    A = admitted(rule, d)
    if canon(override) == canon(base):
        return copy.deepcopy(base), [], []
    if d in ("up", "down"):
        rb, ro = _rank_for(lr, base), _rank_for(lr, override)
        if rb is None or ro is None:
            return (copy.deepcopy(override), ["s", "w"], []) if A == {"s", "w"} else (copy.deepcopy(base), [], ["incomparable"])
        kind = "s" if ((ro > rb) if d == "up" else (ro < rb)) else "w"
        return (copy.deepcopy(override), [kind], []) if kind in A else (copy.deepcopy(base), [], [kind])
    if d in ("add", "remove"):
        if not isinstance(override, list):
            return (copy.deepcopy(override), ["w"], []) if "w" in A else (copy.deepcopy(base), [], ["type"])
        bl = list(base) if isinstance(base, list) else []
        bc, oc = [canon(x) for x in bl], [canon(x) for x in override]
        adds = [x for x in override if canon(x) not in bc]
        rems = [x for x in bl if canon(x) not in oc]
        add_kind, rem_kind = ("s", "w") if d == "add" else ("w", "s")
        eff, applied, refused = list(bl), [], []
        if adds:
            if add_kind in A:
                eff += adds
                applied.append(add_kind)
            else:
                refused.append(add_kind)
        if rems:
            if rem_kind in A:
                rc = [canon(r) for r in rems]
                eff = [x for x in eff if canon(x) not in rc]
                applied.append(rem_kind)
            else:
                refused.append(rem_kind)
        return eff, applied, refused
    if d in ("strict_true", "strict_false"):
        kind = "s" if override is (d == "strict_true") else "w"
        return (copy.deepcopy(override), [kind], []) if kind in A else (copy.deepcopy(base), [], [kind])
    return (copy.deepcopy(override), ["w"], []) if "w" in A else (copy.deepcopy(base), [], ["w"])


def flatten_overrides(overrides):
    """PROJECT_POLICY.policy_overrides as concrete leaves, flattening mapping values as the runtime does."""
    out = []

    def walk(k, v):
        if isinstance(v, dict) and v:
            for kk, vv in v.items():
                walk(f"{k}.{kk}", vv)
        else:
            out.append((k, v))
    for k, v in (overrides or {}).items():
        walk(k, v)
    return out


def project_effective(inv, base_values, overrides, held_inv=None):
    """Effective policy values after the project layer (`19` §5.3 revision 4). base_values: the root kernel's effective values."""
    eff, applied, refused = dict(base_values), [], []
    for key, value in flatten_overrides(overrides):
        lr = key_leaf_rule(inv, key)
        if held_inv is not None and leaf_direction(lr) == "none":
            hlr = key_leaf_rule(held_inv, key)
            if leaf_direction(hlr) != "none":
                lr = hlr  # the held registration's strength direction governs until the reduction is accepted per project
        rule = effective_project_rule(inv, key, held_inv)
        if lr is None:
            refused.append({"key": key, "reason": "not a registered constitutional leaf", "rule": rule["mode"]})
            continue
        e, ap, rf = project_apply(lr, rule, base_values.get(key), value)
        eff[key] = e
        if ap:
            applied.append({"key": key, "components": ap, "rule": rule["mode"]})
        if rf:
            refused.append({"key": key, "components": rf, "rule": rule["mode"]})
    return eff, applied, refused


# ------------------------------------------------------------------------------------------------ project-owned strength (26 §6)
def requirement_holds(req, current, sensitivity_order=None):
    op = req["op"]
    if op in ("level_at_least", "ordered_at_least", "level_at_most", "ordered_at_most", "decimal_at_least", "decimal_at_most", "set_superset", "set_subset", "bool_toward"):
        if current is None:
            return False
        rule = {"op": op, "value": req["value"], "order": req.get("order") if req.get("order") != "<sensitivity>" else sensitivity_order,
                "kind": req.get("kind") or "level", "strict": req.get("strict")}
        return op_holds(rule, current)
    if op == "equal":
        return canon(current) == canon(req["value"])
    if op == "classification_superset":
        cur = {x.get("pattern"): x.get("class") for x in (current or []) if isinstance(x, dict)}
        return all(p in cur and _rank(sensitivity_order, cur[p]) is not None and _rank(sensitivity_order, cur[p]) >= _rank(sensitivity_order, c)
                   for p, c in ((x.get("pattern"), x.get("class")) for x in req["value"] if isinstance(x, dict)))
    if op == "contract_at_least":
        return not contract_losses(req["value"], current or [])
    if op == "map_subset":
        cur = current or {}
        rec = req["value"] or {}
        return isinstance(cur, dict) and all(k in rec and {json.dumps(canon(x)) for x in (v or [])} <= {json.dumps(canon(x)) for x in (rec[k] or [])} for k, v in cur.items())
    if op == "entries_subset":
        rec = {x.get("id"): canon(x) for x in (req["value"] or []) if isinstance(x, dict)}
        return all(isinstance(x, dict) and x.get("id") in rec and canon(x) == rec[x.get("id")] for x in (current or []))
    if op == "applicable_superset":
        cur = current or {}
        return all(not (isinstance(v, dict) and v.get("applicable") is True) or (isinstance(cur.get(k), dict) and cur[k].get("applicable") is True)
                   for k, v in (req["value"] or {}).items())
    if op == "file_set_subset":
        return all(req["value"].get(k) == v for k, v in (current or {}).items())
    if op == "file_unchanged":
        return current is None or current == req["value"]
    raise ValueError("unknown requirement op " + op)


_CONTRACT_STRICT_FALSE = ("semantic_index", "lexical_index", "graph_index", "code_index", "default_retrieval")
_CONTRACT_ORDERED = {"agent_read": ["allowed", "restricted", "prohibited"], "export": ["allowed", "restricted", "denied"],
                     "mutation": ["generated", "restricted", "prohibited"]}


def contract_effective(paths, probe):
    """REPOSITORY_CONTRACT semantics for one path: later rules override earlier ones; the `secret` class always wins."""
    eff, secret = {}, False
    for r in paths or []:
        if isinstance(r, dict) and fnmatch.fnmatchcase(probe, r.get("pattern", "")):
            eff.update({k: v for k, v in r.items() if k != "pattern"})
            secret = secret or r.get("class") == "secret"
    if secret:
        eff["class"] = "secret"
    return eff


def contract_losses(recorded_paths, current_paths):
    losses = []
    for r in recorded_paths or []:
        if not isinstance(r, dict):
            continue
        probe = r.get("pattern", "").replace("**", "p4dir").replace("*", "p4x")
        a, b = contract_effective(recorded_paths, probe), contract_effective(current_paths, probe)
        for f in _CONTRACT_STRICT_FALSE:
            if a.get(f) is False and b.get(f) is not False:
                losses.append({"pattern": r.get("pattern"), "field": f, "recorded": False, "current": b.get(f)})
        for f, order in _CONTRACT_ORDERED.items():
            ra, rb = _rank(order, a.get(f)), _rank(order, b.get(f))
            if ra is not None and ra > 0 and (rb is None or rb < ra):
                losses.append({"pattern": r.get("pattern"), "field": f, "recorded": a.get(f), "current": b.get(f)})
        if a.get("class") == "secret" and b.get("class") != "secret":
            losses.append({"pattern": r.get("pattern"), "field": "class", "recorded": "secret", "current": b.get("class")})
    return losses


def overlay_file_rule(inv, rel):
    for f in (inv.get("overlay_surface") or {}).get("files", []):
        if f.get("path") == rel or (f.get("glob") and fnmatch.fnmatchcase(rel, f["glob"])):
            return f
    return None


def overlay_key_rule(ofr, full_key):
    hits = [k for k in ofr.get("keys", []) if key_match(k["key"], full_key)]
    exact = [k for k in hits if "*" not in k["key"]]
    return exact[0] if exact else (hits[0] if hits else None)


def _req_op(direction):
    return {"up": "ordered_at_least", "down": "ordered_at_most", "add": "set_superset", "remove": "set_subset",
            "strict_true": "bool_toward", "strict_false": "bool_toward"}.get(direction, direction)


def requirement_from_component(key, lr, base, effective):
    """The strength a project contributes on one constitutional key, as a requirement on its effective value."""
    d = leaf_direction(lr)
    if d == "none" or canon(effective) == canon(base):
        return None
    if d in ("up", "down"):
        rb, re_ = _rank_for(lr, base), _rank_for(lr, effective)
        if rb is None or re_ is None or not ((re_ > rb) if d == "up" else (re_ < rb)):
            return None
        return {"subject": key, "source": "effective_policy", "op": lr["op"], "value": effective, "order": lr.get("order"), "kind": lr.get("kind")}
    if d == "add":
        added = [x for x in (effective or []) if canon(x) not in [canon(y) for y in (base or [])]]
        return {"subject": key, "source": "effective_policy", "op": "set_superset", "value": added} if added else None
    if d == "remove":
        removed = [x for x in (base or []) if canon(x) not in [canon(y) for y in (effective or [])]]
        return {"subject": key, "source": "effective_policy", "op": "set_subset", "value": effective} if removed else None
    strict = d == "strict_true"
    return {"subject": key, "source": "effective_policy", "op": "bool_toward", "strict": strict, "value": strict} if effective is strict and base is not strict else None


def strength_requirements(inv, overlay_docs, effective_values, base_values):
    """Record the project-owned strength vector (`26` §6 revision 4). overlay_docs: {relpath under governance/overlay: doc or
    digest string for non-YAML}; effective_values / base_values: effective policy with and without the project layer."""
    reqs = []
    for key in sorted(effective_values):
        req = requirement_from_component(key, key_leaf_rule(inv, key), base_values.get(key), effective_values[key])
        if req:
            reqs.append(req)
    plugin_files = {}
    for rel in sorted(overlay_docs):
        doc = overlay_docs[rel]
        ofr = overlay_file_rule(inv, rel)
        if ofr is None:
            reqs.append({"subject": f"overlay:{rel}", "source": "overlay", "op": "file_unchanged", "value": vdigest(doc)})
            continue
        if ofr.get("file_direction") == "file_set_subset":
            plugin_files[rel] = vdigest(doc)
            continue
        name = ofr["name"]
        for kr in ofr.get("keys", []):
            if kr["direction"] in ("none", "effective_policy") or "*" in kr["key"]:
                continue
            v = deep_get(doc, kr["key"][len(name) + 1:])
            if v is None:
                continue
            reqs.append({"subject": f"{rel}:{kr['key']}", "source": "overlay", "op": _req_op(kr["direction"]), "value": copy.deepcopy(v),
                         "order": kr.get("order"), "strict": {"strict_true": True, "strict_false": False}.get(kr["direction"])})
    if plugin_files or any(f.get("file_direction") == "file_set_subset" for f in (inv.get("overlay_surface") or {}).get("files", [])):
        reqs.append({"subject": "overlay-files:plugins/*.yaml", "source": "overlay", "op": "file_set_subset", "value": plugin_files})
    return reqs


def strength_failures(inv, reqs, overlay_docs, effective_values):
    """Evaluate a recorded vector against current inputs from ANY source (kernel, TPS, precedence, migration, recovery, overlay)."""
    sens = (inv.get("overlay_surface") or {}).get("sensitivity_order")
    failures, recorded_unclassified = [], set()
    for r in reqs:
        if r["source"] == "effective_policy":
            cur = effective_values.get(r["subject"])
        elif r["op"] == "file_set_subset":
            cur = {rel: vdigest(doc) for rel, doc in overlay_docs.items() if (overlay_file_rule(inv, rel) or {}).get("file_direction") == "file_set_subset"}
        elif r["op"] == "file_unchanged":
            rel = r["subject"].split(":", 1)[1]
            recorded_unclassified.add(rel)
            cur = vdigest(overlay_docs[rel]) if rel in overlay_docs else None
        else:
            rel, key = r["subject"].split(":", 1)
            ofr = overlay_file_rule(inv, rel)
            cur = deep_get(overlay_docs.get(rel), key[len(ofr["name"]) + 1:]) if ofr and rel in overlay_docs else None
        if not requirement_holds(r, cur, sens):
            failures.append({"subject": r["subject"], "op": r["op"], "recorded": r["value"], "current": cur})
    for rel in overlay_docs:
        if overlay_file_rule(inv, rel) is None and rel not in recorded_unclassified:
            failures.append({"subject": f"overlay:{rel}", "op": "unclassified_overlay_file_added", "recorded": None, "current": vdigest(overlay_docs[rel])})
    return failures


# ------------------------------------------------------------------------------------------------ migration operations (23 §11, CR-02)
_OVERLAY_FILE_NAME = re.compile(r"^(?:[A-Z][A-Z0-9_]*\.yaml|plugins/[a-z0-9][a-z0-9-]*\.yaml)$")


def _overlay_key_writable(inv, file, dotted):
    ofr = overlay_file_rule(inv, file)
    if not ofr or not isinstance(dotted, str) or not dotted:
        return False
    kr = overlay_key_rule(ofr, f"{ofr['name']}.{dotted}")
    if kr is None:
        # a key inside a writable subtree
        for k in ofr.get("keys", []):
            if k.get("subtree") and k.get("migration_writable") and (f"{ofr['name']}.{dotted}" + ".").startswith(k["key"] + "."):
                return True
        return False
    return bool(kr.get("migration_writable"))


def migration_op_problems(inv, doc):
    """Default-deny validation of a migration's operations against the Overlay Surface registration."""
    if not isinstance(doc, dict) or not isinstance(doc.get("operations"), list):
        return [{"index": None, "problem": "operations is not a list"}]
    probs = []
    for i, op in enumerate(doc["operations"]):
        kind = op.get("op") if isinstance(op, dict) else None
        if kind in MIGRATION_OPS_NO_TARGET:
            continue
        if kind == "set_lock_field":
            probs.append({"index": i, "op": kind, "problem": "lock operations are not permitted (R-MIG-3): the install transaction writes the RoT-1 lock"})
            continue
        if kind not in MIGRATION_OPS_OVERLAY:
            probs.append({"index": i, "op": kind, "problem": "unknown migration operation"})
            continue
        files = [op.get("from"), op.get("to")] if kind == "rename_overlay_file" else [op.get("file")]
        bad = [f for f in files if not isinstance(f, str) or not _OVERLAY_FILE_NAME.match(f)]
        if bad:
            probs.append({"index": i, "op": kind, "target": bad[0], "problem": "target does not resolve to a registered file directly inside governance/overlay/"})
            continue
        ofr = overlay_file_rule(inv, files[0])
        if ofr is None:
            probs.append({"index": i, "op": kind, "target": files[0], "problem": "overlay file not registered in the Overlay Surface"})
            continue
        if kind == "add_overlay_file_from_template":
            if not ofr.get("migration_add_from_template"):
                probs.append({"index": i, "op": kind, "target": files[0], "problem": "file not registered for creation from template"})
        elif kind == "rename_overlay_file":
            if not (ofr.get("migration_rename") and (overlay_file_rule(inv, files[1]) or {}).get("migration_rename")):
                probs.append({"index": i, "op": kind, "target": files, "problem": "file rename not registered"})
        elif kind in ("set_overlay_key", "delete_overlay_key"):
            if not _overlay_key_writable(inv, files[0], op.get("key")):
                probs.append({"index": i, "op": kind, "target": f"{files[0]}:{op.get('key')}", "problem": "overlay key not registered as migration-writable"})
        elif kind == "rename_overlay_key":
            if not (_overlay_key_writable(inv, files[0], op.get("from")) and _overlay_key_writable(inv, files[0], op.get("to"))):
                probs.append({"index": i, "op": kind, "target": f"{files[0]}:{op.get('from')}->{op.get('to')}", "problem": "overlay key rename not registered as migration-writable"})
        elif kind == "set_overlay_rule":
            lk = op.get("list_key") or "paths"
            if not _overlay_key_writable(inv, files[0], lk):
                probs.append({"index": i, "op": kind, "target": f"{files[0]}:{lk}", "problem": "overlay rule list not registered as migration-writable"})
    return probs


# ------------------------------------------------------------------------------------------------ evaluation of a kernel against the inventory
def evaluate(inv, kdir, embedded_dir=None, named_policy_inv=None):
    """Evaluate a kernel tree against an inventory (the effective TPS surface section): the E7 surface check.

    Returns coverage, required presence, violations and per-leaf effective values. `named_policy_inv` is the surface of the
    TPS named by the release's own `trust_references.trust_policy_version` (floor and precedence registration are judged
    against it; joins and effective precedence use `inv`).
    """
    named = named_policy_inv or inv
    res = {"unclassified_files": [], "ambiguous_files": [], "unclassified_leaves": [], "ambiguous_leaves": [], "structure": [],
           "required_missing": [], "violations": [], "stronger_than_registered": [], "consistency": [], "counts": {}, "effective": {}, "files": {},
           "precedence_unregistered": [], "migration_problems": []}
    present = kernel_files(kdir)
    present_set = set(present)
    kernel_prec = None
    for fr in inv["files"]:
        if fr.get("presence", "required") != "required":
            continue
        for p in registered_paths(fr):
            if p not in present_set:
                res["required_missing"].append({"file": p, "rule": fr.get("path") or fr.get("glob")})
    for rel in present:
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
        if mode == "informational_file":
            res["files"][rel] = {"mode": mode, "digest": fdigest(path)}
            continue
        try:
            doc = load_doc(path)
        except ProfileError as e:
            res["structure"].append({"file": rel, "problem": f"yaml_profile: {e}"})
            continue
        except Exception as e:
            res["structure"].append({"file": rel, "problem": f"unparseable: {e}"})
            continue
        if mode == "transaction_input":
            res["files"][rel] = {"mode": mode, "digest": fdigest(path)}
            if fr.get("digests") is not None and fdigest(path) not in (fr["digests"].get(rel) or []):
                # revision 5 (23 §12): a migration file is a non-join unit registered per release
                res["violations"].append({"file": rel, "class": "transaction_input", "reason": "migration file digest not registered for this release", "digest": fdigest(path)})
            for p in migration_op_problems(inv, doc):
                p["file"] = rel
                res["migration_problems"].append(p)
            continue
        leaves, structure = enumerate_leaves(doc, fr)
        for s in structure:
            s["file"] = rel
        res["structure"] += structure
        res["files"][rel] = {"mode": mode, "leaves": len(leaves)}
        seen_keys = {k for k, _ in leaves}
        for k in required_leaf_keys(fr):
            if k not in seen_keys:
                res["required_missing"].append({"file": rel, "key": k})
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
                if inv.get("registration") and (missing or added):
                    bad = True  # revision 5 (23 §12): the member-id set is a non-join unit fixed exactly per registered release
                if bad:
                    res["violations"].append({"file": rel, "key": key, "class": "members", "op": lr["op"], "missing": missing, "unregistered": added})
                eff = sorted(set(got) & set(reg)) if lr["op"] != "ids_superset" else got
            res["effective"][key] = eff
        if fr.get("name") == "POLICY_PRECEDENCE":
            kernel_prec = doc
    reg = named.get("precedence") or {}
    if reg and kernel_prec is not None:
        mism = precedence_mismatches(kernel_prec, reg)
        res["precedence_unregistered"] = mism
        if mism:
            res["violations"].append({"class": "precedence", "reason": "precedence_unregistered: POLICY_PRECEDENCE differs from its Trust Policy registration",
                                      "mismatches": mism[:12], "count": len(mism)})
    if res["migration_problems"]:
        res["violations"].append({"class": "migration", "reason": "migration_operation_not_permitted", "problems": res["migration_problems"][:12], "count": len(res["migration_problems"])})
    res["effective_precedence"] = "registered rules of the effective Trust Policy (the kernel's POLICY_PRECEDENCE is never an input)"
    res["surface_ok"] = not (res["unclassified_files"] or res["ambiguous_files"] or res["unclassified_leaves"] or res["ambiguous_leaves"]
                             or res["structure"] or res["required_missing"])
    res["eligible_surface"] = res["surface_ok"] and not res["violations"] and not res["stronger_than_registered"]
    return res


def named_file_rule(inv, rel):
    fr = match_file_rule(inv, rel)
    return fr if isinstance(fr, dict) else None


def exception_may_relax(key, registered_rule, kernel_rule=None):
    """Effective exception_relaxable (19 §5.3 revision 4): TPS-registered only (the kernel rule is not an input), and never
    for the compiled prefixes. `kernel_rule` is accepted for call compatibility and must equal the registration (E7)."""
    if key.startswith(NEVER_EXCEPTION_RELAXABLE_PREFIXES):
        return False
    return bool(registered_rule.get("exception_relaxable")) and (kernel_rule is None or bool(kernel_rule.get("exception_relaxable")))


# ------------------------------------------------------------------------------------------------ owner constitutional domain (23 §7.1)
def evaluate_owner_domain(inv, repo_root, registrations):
    """Owner-supplied constitutional files outside the kernel: slots are declared by the Trust Policy; digests are confirmed
    locally (trust gate `owner_constitutional_file`). Absence of a required slot and an unconfirmed or changed digest are
    fail-closed for the slot's consumers on every machine."""
    res = {"missing": [], "unconfirmed": [], "changed": [], "confirmed": []}
    groups = {}
    for slot in inv.get("owner_domain") or []:
        if slot.get("binding_group"):
            groups.setdefault(slot["binding_group"], []).append(slot)
            continue
        p = os.path.join(repo_root, slot["path"])
        reg = (registrations or {}).get(slot["path"])
        if not os.path.isfile(p):
            if slot.get("presence", "required") == "required":
                res["missing"].append({"path": slot["path"], "consumers": slot.get("consumers", [])})
            continue
        d = fdigest(p)
        if reg is None:
            res["unconfirmed"].append({"path": slot["path"], "digest": d, "consumers": slot.get("consumers", [])})
        elif reg != d:
            res["changed"].append({"path": slot["path"], "digest": d, "confirmed": reg, "consumers": slot.get("consumers", [])})
        else:
            res["confirmed"].append(slot["path"])
    # revision 5 (23 §7.2, RV4-L10): a binding group is confirmed and pinned as one set. Its digest is over the sorted
    # (path, file digest) pairs of every member; several valid confirmations or decision pins resolve by exact set match only.
    for name, slots in sorted(groups.items()):
        members, absent = [], []
        for slot in sorted(slots, key=lambda x: x["path"]):
            p = os.path.join(repo_root, slot["path"])
            if os.path.isfile(p):
                members.append([slot["path"], fdigest(p)])
            else:
                absent.append(slot["path"])
        consumers = sorted({c for sl in slots for c in sl.get("consumers", [])})
        if absent:
            res["missing"].append({"group": name, "paths": absent, "consumers": consumers})
            continue
        d = group_digest(members)
        reg = (registrations or {}).get("group:" + name)
        regs = [reg] if isinstance(reg, str) else list(reg or [])
        if not regs:
            res["unconfirmed"].append({"group": name, "digest": d, "members": members, "consumers": consumers})
        elif d not in regs:
            res["changed"].append({"group": name, "digest": d, "confirmed_sets": regs, "members": members, "consumers": consumers})
        else:
            res["confirmed"].append("group:" + name)
    return res


def group_digest(members):
    b = json.dumps(sorted([list(m) for m in members]), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return "sha256:" + hashlib.sha256(b).hexdigest()


# ------------------------------------------------------------------------------------------------ revision 5: release-scoped registration (23 §12)
def registration_multi_valued(inv):
    """Single-valued registration (23 §12.2): a registered digest list with more than one value is malformed
    (REGISTRATION_NOT_SINGLE_VALUED). Revision 4's retention form, several permitted digests for one key, is this shape."""
    out = []
    for f in inv.get("files", []):
        for p, v in (f.get("digests") or {}).items():
            if isinstance(v, list) and len(v) > 1:
                out.append({"unit": "file:" + p, "values": len(v)})
        for l in f.get("leaves") or []:
            for k, v in (l.get("digests") or {}).items():
                if isinstance(v, list) and len(v) > 1:
                    out.append({"unit": "leaf:" + k, "values": len(v)})
    return out


def tree_digest(kdir):
    """Reference kernel tree digest over (path, file digest) of every kernel file (stands in for gov-tree-v2, 07 §5)."""
    h = hashlib.sha256()
    for rel in kernel_files(kdir):
        h.update(rel.encode() + b"\0" + fdigest(os.path.join(kdir, rel)).encode() + b"\n")
    return "sha256:" + h.hexdigest()


def derive_registration_units(inv, kdir):
    """Producer: the non-join units of a kernel under the inventory's classification: every pinned leaf or whole pinned member
    (leaf:<key>), every member-id set (members:<key>), every pinned_file and transaction_input file (file:<path>)."""
    units = {}
    for rel in kernel_files(kdir):
        fr = match_file_rule(inv, rel)
        if not isinstance(fr, dict):
            continue
        path = os.path.join(kdir, rel)
        if fr["mode"] in ("pinned_file", "transaction_input"):
            units["file:" + rel] = fdigest(path)
            continue
        if fr["mode"] != "structured":
            continue
        try:
            doc = load_doc(path)
        except Exception:
            continue
        leaves, _ = enumerate_leaves(doc, fr)
        for key, v in leaves:
            if key.endswith("#structure"):
                continue
            lr = match_leaf_rule(fr, key)
            if not isinstance(lr, dict):
                continue
            if lr["class"] == "pinned":
                units["leaf:" + key] = vdigest(v)
            elif lr["class"] == "members":
                units["members:" + key] = sorted(v) if isinstance(v, list) else v
    return units


def registration_record(inv, kdir, release_id, sequence, final_statement_digest=None, lowering_history=()):
    return {"release_id": release_id, "sequence": sequence, "final_statement_digest": final_statement_digest,
            "kernel_tree_digest": tree_digest(kdir), "units": derive_registration_units(inv, kdir), "lowering_history": list(lowering_history)}


_REG_CONTENT = ("release_id", "sequence", "final_statement_digest", "kernel_tree_digest", "units")


def registration_set_problems(regs):
    """Append-only, single-valued registration set (23 §12.2): one content per release_id (else REGISTRATION_REWRITE),
    one release_id per sequence (else REGISTRATION_SEQUENCE_EQUIVOCATION), one value per unit."""
    probs, by_id, by_seq = [], {}, {}
    for r in regs:
        miss = [k for k in ("release_id", "sequence", "kernel_tree_digest", "units") if k not in r]
        if miss:
            probs.append({"problem": "REGISTRATION_MALFORMED", "release_id": r.get("release_id"), "missing": miss})
            continue
        for u, v in r["units"].items():
            if u.startswith("members:") and not isinstance(v, list):
                probs.append({"problem": "REGISTRATION_MALFORMED", "release_id": r["release_id"], "unit": u})
            if not u.startswith("members:") and not isinstance(v, str):
                probs.append({"problem": "REGISTRATION_NOT_SINGLE_VALUED", "release_id": r["release_id"], "unit": u})
        c = canon({k: r.get(k) for k in _REG_CONTENT})
        if r["release_id"] in by_id and by_id[r["release_id"]] != c:
            probs.append({"problem": "REGISTRATION_REWRITE", "release_id": r["release_id"]})
        by_id.setdefault(r["release_id"], c)
        if r["sequence"] in by_seq and by_seq[r["sequence"]] != r["release_id"]:
            probs.append({"problem": "REGISTRATION_SEQUENCE_EQUIVOCATION", "sequence": r["sequence"], "release_ids": sorted([by_seq[r["sequence"]], r["release_id"]])})
        by_seq.setdefault(r["sequence"], r["release_id"])
    return probs


def project_registration(inv, reg):
    """The surface section with the non-join registrations of exactly one registered release: every pinned leaf, member-id
    set, pinned file and migration file carries the single value registered for that release, and nothing else is registered.
    Ranges, unions and 'latest registered' are never used (23 §12.3)."""
    i = copy.deepcopy(inv)
    i["registration"] = {k: reg.get(k) for k in ("release_id", "sequence", "final_statement_digest", "kernel_tree_digest")}
    units = reg["units"]
    # Presence is release-scoped (23 §12.3 rule 4): a concrete non-join rule whose unit this release does not register is
    # not required of this release; content present without a registration is still unregistered (violation).
    for f in i["files"]:
        if f["mode"] in ("pinned_file", "transaction_input"):
            if f.get("path") and f["mode"] == "pinned_file":
                f["digests"] = {f["path"]: []}
                if "file:" + f["path"] not in units:
                    f["presence"] = "optional"
            else:
                f["digests"] = {}
        for l in f.get("leaves") or []:
            if l["class"] == "pinned":
                l["digests"] = {}
                if "*" not in l["key"] and "leaf:" + l["key"] not in units:
                    l["presence"] = "optional"
            elif l["class"] == "members" and "members:" + l["key"] not in units:
                l["presence"] = "optional"
    for u, v in sorted(units.items()):
        kind, ident = u.split(":", 1)
        if kind == "file":
            fr = match_file_rule(i, ident)
            if isinstance(fr, dict) and fr["mode"] in ("pinned_file", "transaction_input"):
                fr["digests"][ident] = [v]
                if fr.get("path") == ident:
                    fr["presence"] = inv_rule_presence(inv, ident)
        elif kind in ("leaf", "members"):
            name = ident.split(".", 1)[0].split("[", 1)[0]
            for f in i["files"]:
                if f.get("mode") != "structured" or f.get("name") != name:
                    continue
                lr = match_leaf_rule(f, ident)
                if isinstance(lr, dict) and kind == "leaf" and lr["class"] == "pinned":
                    lr["digests"][ident] = [v]
                elif isinstance(lr, dict) and kind == "members" and lr["class"] == "members":
                    lr["registered"] = list(v)
    return i


def inv_rule_presence(inv, path):
    fr = match_file_rule(inv, path)
    return fr.get("presence", "required") if isinstance(fr, dict) else "required"


def _member_direction(inv, key):
    for f in inv.get("files", []) if inv else []:
        for l in f.get("leaves") or []:
            if l.get("class") == "members" and l["key"] == key:
                return l.get("op")
    return None


def registration_reductions(regs, history_subjects=(), inv=None):
    """Computed reductions over an ordered registration set (23 §12.4): a unit of a later registration whose value equals a
    value that an intermediate registration superseded is a registration_reversion. Undeclared reversions exit 6."""
    probs = registration_set_problems(regs)
    if probs:
        return {"exit": 5, "malformed": probs, "reductions": [], "undeclared": []}
    hist, reds = {}, []
    prev = None
    for r in sorted(regs, key=lambda x: x["sequence"]):
        if prev is not None:
            for u in sorted(set(prev["units"]) - set(r["units"])):
                reds.append({"subject": f"registration:{r['release_id']}:{u}", "kind": "registration_unit_removed", "release_id": r["release_id"], "present_in": prev["release_id"]})
            for u in sorted(k for k in set(prev["units"]) & set(r["units"]) if k.startswith("members:")):
                op = _member_direction(inv, u[len("members:"):])
                old, new = set(prev["units"][u]), set(r["units"][u])
                if (op in ("ids_superset", "ids_equal") and old - new) or (op in ("ids_subset", "ids_equal") and new - old):
                    reds.append({"subject": f"registration:{r['release_id']}:{u}", "kind": "registration_members_reduced", "release_id": r["release_id"],
                                 "removed": sorted(old - new), "added": sorted(new - old), "op": op})
        prev = r
        for u, v in sorted(r["units"].items()):
            prior = hist.get(u, [])
            cv = canon(v)
            if prior and cv != canon(prior[-1][1]):
                earlier = [x for x in prior[:-1] if canon(x[1]) == cv]
                if earlier:
                    reds.append({"subject": f"registration:{r['release_id']}:{u}", "kind": "registration_reversion", "release_id": r["release_id"],
                                 "reverts_to_value_of": earlier[-1][2], "supersedes_value_of": prior[-1][2]})
            hist.setdefault(u, []).append((r["sequence"], v, r["release_id"]))
    declared = set(history_subjects) | {h.get("subject") for r in regs for h in (r.get("lowering_history") or [])}
    undeclared = [x for x in reds if x["subject"] not in declared]
    return {"exit": 6 if undeclared else 0, "reductions": reds, "undeclared": undeclared}
