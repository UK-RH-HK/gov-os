#!/usr/bin/env python3
"""Structural checker for a held-out demonstration oracle (govbridge-oracle/1).

Run BR-AR-0002, DAG node TA. Stdlib + PyYAML only. Generic: nothing in this checker is specific to Review 8. The
case-specific inputs are read from files at run time:

  * ARCHITECTURE/schemas/oracle.yaml            -- field list, anchor kinds, allowed packet sections
  * ARCHITECTURE/demonstration-queries.yaml     -- the chain stages (in order) and the public query ids
  * ORCHESTRATOR_STATE.yaml                     -- mandatory_bridge_inputs (items and their authority classes)

It enforces node TA's acceptance checks (IMPLEMENTATION_DAG.yaml):
  1. every chain has exactly the 11 chain stages, in order;
  2. exactly one is_enforcement_point per chain;
  3. one authority_expectations row per mandatory_bridge_inputs item, with the class verbatim;
  4. every anchor has kind, commit and path (kind from the schema's list, commit a full 40-hex id);
and, additionally: required top-level keys and types, why-fields on traps/wrong/alternative anchors, consumer
process/production flags, coverage of every public query id, and a lint that must_state text asserts no F2/F3
classification and no disposition (the schema's prohibited_content).

Per-fact binding (run BR-AR-0021, REPAIR-1 node R1-TA2; GATES/BR-ARCH-RULING-2 D-2). A must_state entry is either a
plain string (the run-1 form, still accepted) or a mapping ``{fact: <text>, binding: <scope>}`` naming WHERE the
rubric grader must find the fact:

  * inside a chain stage, ``binding`` must equal that stage's own name -- D-2: "[R] Each must_state fact is present
    in the stage's claim"; a chain-wide binding is the reading D-2 did NOT adopt, so ``chain`` is refused here;
  * inside a query or control row (and in side_by_side / f1_both_ways, should they carry must_state), ``binding``
    must be ``query`` -- the fact is judged against that query's whole answer (DEMONSTRATION_DESIGN.md section 4 G5).

The oracle is in BOUND mode when any must_state entry is a mapping, or when ``--require-binding`` is given; in bound
mode every must_state entry must be a well-formed mapping (no mixing). The node R1-TA2 acceptance ("every must_state
fact carries a binding") is ``--require-binding``.

Output never echoes oracle content: it prints the file's basename (or --display-name), its sha256, counts, and
structural problems located by key path only. Exit 0 when valid, 1 when invalid, 2 on a usage/IO error.
"""
import argparse
import hashlib
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
DOMAIN = os.path.dirname(os.path.dirname(HERE))
DEFAULT_SCHEMA = os.path.join(DOMAIN, "ARCHITECTURE", "schemas", "oracle.yaml")
DEFAULT_QUERIES = os.path.join(DOMAIN, "ARCHITECTURE", "demonstration-queries.yaml")
DEFAULT_STATE = os.path.join(DOMAIN, "ORCHESTRATOR_STATE.yaml")

HEX40 = re.compile(r"^[0-9a-f]{40}$")
ANCHOR_KEYS = {"kind", "commit", "path", "lines", "symbol", "record_id", "section", "why"}
CONSUMER_EXTRA = {"process", "production"}
FACT_KEYS = {"fact", "binding"}
QUERY_BINDING = "query"

# must_state lint: phrases that would assert an F2/F3 classification or an F1 disposition (schema
# prohibited_content). Deliberately narrow: it must not fire on a statement that something is NOT yet decided.
PROHIBITED = [
    re.compile(r"\bare (?:one|the same|a single) (?:deeper )?(?:defect )?class\b", re.I),
    re.compile(r"\bare (?:two )?(?:different|distinct|separate) (?:defect )?classes\b", re.I),
    re.compile(r"\bare not (?:one|the same) (?:defect )?class\b", re.I),
    re.compile(r"\b(?:should|must|shall) (?:be )?(?:deleted|simplified|repaired|narrowed|retained)\b", re.I),
    re.compile(r"\b(?:we|I) recommend\b", re.I),
    re.compile(r"\brecommendation\s*:", re.I),
    re.compile(r"\bdisposition\s*:\s*(?:DELETE|SIMPLIFY|REPAIR|NARROW|RETAIN)\b"),
]


class UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader, node, deep=False):
    loader.flatten_mapping(node)
    seen = set()
    for k, _ in node.value:
        key = loader.construct_object(k, deep=deep)
        if key in seen:
            raise yaml.constructor.ConstructorError(None, None, f"duplicate key {key!r}", k.start_mark)
        seen.add(key)
    return yaml.SafeLoader.construct_mapping(loader, node, deep)


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def load(path):
    with open(path, "rb") as f:
        data = f.read()
    return data, yaml.load(data.decode("utf-8"), Loader=UniqueKeyLoader)


def _is_fact_mapping(x):
    return isinstance(x, dict)


def _iter_must_state_lists(doc):
    """Every must_state list in the oracle, wherever the schema places one (chain stages, query/control rows, and
    side_by_side / f1_both_ways should they carry one). Used only to decide the binding mode."""
    if not isinstance(doc, dict):
        return
    for ch in doc.get("chains") or []:
        if isinstance(ch, dict):
            for st in ch.get("stages") or []:
                if isinstance(st, dict) and isinstance(st.get("must_state"), list):
                    yield st["must_state"]
    for key in ("queries", "controls"):
        for q in doc.get(key) or []:
            if isinstance(q, dict) and isinstance(q.get("must_state"), list):
                yield q["must_state"]
    for key in ("side_by_side", "f1_both_ways"):
        blk = doc.get(key)
        if isinstance(blk, dict) and isinstance(blk.get("must_state"), list):
            yield blk["must_state"]


class Checker:
    def __init__(self, schema, queries, state, require_binding=False):
        self.problems = []
        self.anchor_count = 0
        self.require_binding = require_binding
        self.bound_mode = require_binding
        self.fact_counts = {"stage": 0, "query": 0, "unbound": 0}
        # anchor kinds, from the schema's own anchor definition
        kinds = str((schema.get("anchor") or {}).get("kind", ""))
        self.kinds = {k.strip() for k in kinds.split("|") if k.strip()} or {"code", "test", "record", "contract", "evidence"}
        fields = schema.get("fields") or {}
        self.required_top = [k for k, v in fields.items() if isinstance(v, dict) and v.get("required")]
        self.const_schema = ((fields.get("schema") or {}).get("value")) or "govbridge-oracle/1"
        ae = str(((fields.get("authority_expectations") or {}).get("type")) or "")
        m = re.search(r"sections:\s*\[([^\]]+)\]", ae)
        self.sections = {s.strip() for s in m.group(1).split("|")} if m else {
            "A", "B", "C", "D.1", "D.2", "D.3", "E", "F", "G", "H"}
        self.stages = list(queries.get("chain_stages") or [])
        self.query_ids = {q["id"]: q.get("kind") for q in (queries.get("queries") or [])}
        mbi = (state.get("mandatory_bridge_inputs") or {})
        self.mandatory = {i["id"]: i["class"] for i in (mbi.get("items") or [])}
        self.class_vocab = set((mbi.get("authority_classes") or {}).keys())

    def err(self, where, msg):
        self.problems.append(f"{where}: {msg}")

    # ---------------------------------------------------------------------------------------------- primitives
    def anchor(self, a, where, need_why=False, consumer=False):
        self.anchor_count += 1
        if not isinstance(a, dict):
            self.err(where, "anchor is not a mapping")
            return
        allowed = ANCHOR_KEYS | (CONSUMER_EXTRA if consumer else set())
        extra = set(a) - allowed
        if extra:
            self.err(where, f"unknown anchor keys {sorted(extra)}")
        for k in ("kind", "commit", "path"):
            if not a.get(k):
                self.err(where, f"anchor lacks {k}")
        if a.get("kind") and a["kind"] not in self.kinds:
            self.err(where, f"anchor kind not in {sorted(self.kinds)}")
        if a.get("commit") and not HEX40.match(str(a["commit"])):
            self.err(where, "anchor commit is not a full 40-hex id")
        if a.get("path") is not None and (not isinstance(a["path"], str) or a["path"].startswith("/")):
            self.err(where, "anchor path must be a repository-relative string")
        if "lines" in a:
            ln = a["lines"]
            if not (isinstance(ln, list) and len(ln) == 2 and all(isinstance(x, int) for x in ln)
                    and 1 <= ln[0] <= ln[1]):
                self.err(where, "lines must be [start, end] with 1 <= start <= end")
        elif a.get("kind") in ("code", "test"):
            self.err(where, "code/test anchor lacks lines")
        elif not (a.get("record_id") or a.get("section")):
            self.err(where, "anchor without lines must name a record_id or section")
        for k in ("symbol", "record_id", "section", "why"):
            if k in a and not (isinstance(a[k], str) and a[k].strip()):
                self.err(where, f"{k} must be a non-empty string")
        if need_why and not (isinstance(a.get("why"), str) and a["why"].strip()):
            self.err(where, "anchor requires a why")
        if consumer:
            if a.get("process") not in ("in", "cross"):
                self.err(where, "consumer anchor process must be 'in' or 'cross'")
            if not isinstance(a.get("production"), bool):
                self.err(where, "consumer anchor production must be a bool")

    def anchor_list(self, lst, where, need_why=False, allow_empty=True, consumer=False):
        if not isinstance(lst, list):
            self.err(where, "must be a list")
            return
        if not lst and not allow_empty:
            self.err(where, "must not be empty")
        for i, a in enumerate(lst):
            self.anchor(a, f"{where}[{i}]", need_why=need_why, consumer=consumer)

    def id_or_anchor_list(self, lst, where, need_why=False, allow_empty=True):
        if not isinstance(lst, list):
            self.err(where, "must be a list")
            return
        if not lst and not allow_empty:
            self.err(where, "must not be empty")
        for i, x in enumerate(lst):
            if isinstance(x, str):
                if not x.strip():
                    self.err(f"{where}[{i}]", "empty id")
            else:
                self.anchor(x, f"{where}[{i}]", need_why=need_why)

    def lint(self, text, where):
        for pat in PROHIBITED:
            if pat.search(text):
                self.err(where, "asserts a classification or disposition (prohibited_content)")
                return

    def must_state(self, lst, where, expected_binding, allow_empty=True):
        """A must_state list. Each entry is a non-empty string (unbound, run-1 form) or, in bound mode, a mapping
        {fact, binding} whose binding equals ``expected_binding`` (the containing stage's name, or ``query``)."""
        if not isinstance(lst, list):
            self.err(where, "must be a list")
            return
        if not lst and not allow_empty:
            self.err(where, "must not be empty")
        scope = "query" if expected_binding == QUERY_BINDING else "stage"
        for i, s in enumerate(lst):
            w = f"{where}[{i}]"
            if isinstance(s, str):
                if not s.strip():
                    self.err(w, "must be a non-empty string or a {fact, binding} mapping")
                    continue
                if self.bound_mode:
                    self.err(w, "unbound fact: in bound mode every must_state entry is a {fact, binding} mapping "
                                "(BR-ARCH-RULING-2 D-2)")
                self.fact_counts["unbound"] += 1
                self.lint(s, w)
                continue
            if not _is_fact_mapping(s):
                self.err(w, "must be a non-empty string or a {fact, binding} mapping")
                continue
            extra = set(s) - FACT_KEYS
            if extra:
                self.err(w, f"unknown fact keys {sorted(extra)}")
            fact, binding = s.get("fact"), s.get("binding")
            if not (isinstance(fact, str) and fact.strip()):
                self.err(w, "fact must be a non-empty string")
            else:
                self.lint(fact, w)
            if not (isinstance(binding, str) and binding.strip()):
                self.err(w, "binding must be a non-empty string")
            elif binding != expected_binding:
                if scope == "stage":
                    self.err(w, "binding must name the containing stage itself (BR-ARCH-RULING-2 D-2: a must_state "
                                "fact is bound to its stage, never to the chain)")
                else:
                    self.err(w, f"binding must be '{QUERY_BINDING}' for a query-level fact")
            else:
                self.fact_counts[scope] += 1

    # ---------------------------------------------------------------------------------------------- sections
    def top(self, doc):
        if not isinstance(doc, dict):
            self.err("<root>", "oracle is not a mapping")
            return False
        for k in self.required_top:
            if k not in doc:
                self.err("<root>", f"missing required key {k}")
        if doc.get("schema") != self.const_schema:
            self.err("schema", f"must be {self.const_schema}")
        if not isinstance(doc.get("oracle_id"), str) or not doc["oracle_id"].strip():
            self.err("oracle_id", "must be a non-empty string")
        au = doc.get("author")
        if not isinstance(au, dict) or not all(au.get(k) for k in ("run_id", "role", "model_observed")):
            self.err("author", "must carry run_id, role and model_observed")
        elif au.get("role") != "test-author":
            self.err("author.role", "must be test-author")
        co = doc.get("commits")
        if not isinstance(co, dict) or not all(HEX40.match(str(co.get(k, ""))) for k in ("product", "records", "evidence")):
            self.err("commits", "must carry product, records and evidence as full 40-hex ids")
        if "line_tolerance" in doc and not (isinstance(doc["line_tolerance"], int) and doc["line_tolerance"] >= 0):
            self.err("line_tolerance", "must be a non-negative int")
        self.anchor_list(doc.get("written_from"), "written_from", allow_empty=False)
        return True

    def chains(self, chains):
        if not isinstance(chains, list) or not chains:
            self.err("chains", "must be a non-empty list")
            return set()
        seen = set()
        for ci, ch in enumerate(chains):
            w = f"chains[{ci}]"
            if not isinstance(ch, dict):
                self.err(w, "not a mapping")
                continue
            qid = ch.get("query_id")
            seen.add(qid)
            if self.query_ids.get(qid) != "chain":
                self.err(f"{w}.query_id", "not a public chain query id")
            stages = ch.get("stages")
            if not isinstance(stages, list):
                self.err(f"{w}.stages", "must be a list")
                continue
            names = [s.get("stage") if isinstance(s, dict) else None for s in stages]
            if names != self.stages:
                self.err(f"{w}.stages", f"must be exactly the {len(self.stages)} chain stages in order")
            enforcement = 0
            for si, st in enumerate(stages):
                sw = f"{w}.stages[{si}]"
                if not isinstance(st, dict):
                    self.err(sw, "not a mapping")
                    continue
                for k in ("stage", "required", "is_enforcement_point", "anchors", "must_state", "traps", "wrong"):
                    if k not in st:
                        self.err(sw, f"missing {k}")
                if not isinstance(st.get("required"), bool):
                    self.err(f"{sw}.required", "must be a bool")
                if not isinstance(st.get("is_enforcement_point"), bool):
                    self.err(f"{sw}.is_enforcement_point", "must be a bool")
                elif st["is_enforcement_point"]:
                    enforcement += 1
                    if not st.get("traps"):
                        self.err(f"{sw}.traps", "the enforcement stage must list its upstream-representation traps")
                an = st.get("anchors")
                if not isinstance(an, dict) or len(an) != 1 or next(iter(an)) not in ("any_of", "all_of"):
                    self.err(f"{sw}.anchors", "must be exactly one of {any_of: [...]} or {all_of: [...]}")
                else:
                    self.anchor_list(next(iter(an.values())), f"{sw}.anchors.{next(iter(an))}", allow_empty=False)
                self.must_state(st.get("must_state"), f"{sw}.must_state",
                                st.get("stage") if isinstance(st.get("stage"), str) else "<unnamed stage>")
                self.anchor_list(st.get("traps", []), f"{sw}.traps", need_why=True)
                self.anchor_list(st.get("wrong", []), f"{sw}.wrong", need_why=True)
            if enforcement != 1:
                self.err(w, f"has {enforcement} enforcement points; exactly one is required")
            self.anchor_list(ch.get("acceptable_alternative_enforcement_points", []),
                             f"{w}.acceptable_alternative_enforcement_points", need_why=True)
            eb = ch.get("effective_behaviour")
            if not isinstance(eb, dict) or not all(k in eb for k in ("subject", "attribute", "before", "after", "evidence")):
                self.err(f"{w}.effective_behaviour", "must carry subject, attribute, before, after, evidence")
            else:
                for k in ("subject", "attribute", "before", "after"):
                    if not isinstance(eb[k], str) or not eb[k].strip():
                        self.err(f"{w}.effective_behaviour.{k}", "must be a non-empty string")
                self.anchor(eb["evidence"], f"{w}.effective_behaviour.evidence")
        return seen

    def side_by_side(self, sbs):
        w = "side_by_side"
        if not isinstance(sbs, dict):
            self.err(w, "must be a mapping")
            return None
        if self.query_ids.get(sbs.get("query_id")) != "side_by_side":
            self.err(f"{w}.query_id", "not the public side-by-side query id")
        self.anchor_list(sbs.get("shared_points"), f"{w}.shared_points", allow_empty=False)
        self.anchor_list(sbs.get("differing_points"), f"{w}.differing_points", allow_empty=False)
        if "must_state" in sbs:
            self.must_state(sbs.get("must_state"), f"{w}.must_state", QUERY_BINDING)
        return sbs.get("query_id")

    def both_ways(self, bw):
        w = "f1_both_ways"
        if not isinstance(bw, dict):
            self.err(w, "must be a mapping")
            return None
        if self.query_ids.get(bw.get("query_id")) != "both_ways":
            self.err(f"{w}.query_id", "not the public both-ways query id")
        self.anchor_list(bw.get("purpose_anchors"), f"{w}.purpose_anchors", allow_empty=False)
        self.anchor_list(bw.get("consumer_anchors"), f"{w}.consumer_anchors", allow_empty=False, consumer=True)
        if "must_state" in bw:
            self.must_state(bw.get("must_state"), f"{w}.must_state", QUERY_BINDING)
        return bw.get("query_id")

    def query_rows(self, rows, where, kinds):
        seen = set()
        if not isinstance(rows, list):
            self.err(where, "must be a list")
            return seen
        for i, q in enumerate(rows):
            w = f"{where}[{i}]"
            if not isinstance(q, dict):
                self.err(w, "not a mapping")
                continue
            qid = q.get("query_id")
            if qid in seen:
                self.err(f"{w}.query_id", "duplicate query id")
            seen.add(qid)
            if self.query_ids.get(qid) not in kinds:
                self.err(f"{w}.query_id", f"not a public query id of kind {sorted(kinds)}")
            for k in ("required", "forbidden", "must_state"):
                if k not in q:
                    self.err(w, f"missing {k}")
            self.id_or_anchor_list(q.get("required", []), f"{w}.required", allow_empty=False)
            self.id_or_anchor_list(q.get("forbidden", []), f"{w}.forbidden", need_why=True)
            self.must_state(q.get("must_state", []), f"{w}.must_state", QUERY_BINDING, allow_empty=False)
        return seen

    def authority(self, rows):
        w = "authority_expectations"
        if not isinstance(rows, list):
            self.err(w, "must be a list")
            return
        count = {}
        for i, r in enumerate(rows):
            rw = f"{w}[{i}]"
            if not isinstance(r, dict) or not all(k in r for k in ("item", "sections", "class")):
                self.err(rw, "must carry item, sections and class")
                continue
            count[r["item"]] = count.get(r["item"], 0) + 1
            if r["item"] not in self.mandatory:
                self.err(rw, "item is not a mandatory_bridge_inputs item")
            elif r["class"] != self.mandatory[r["item"]]:
                self.err(rw, "class differs from the mandatory_bridge_inputs class (must be verbatim)")
            if self.class_vocab and r["class"] not in self.class_vocab:
                self.err(rw, "class is not in mandatory_bridge_inputs.authority_classes")
            secs = r["sections"]
            if not isinstance(secs, list) or not secs or not all(s in self.sections for s in secs):
                self.err(rw, f"sections must be a non-empty list drawn from {sorted(self.sections)}")
        for item in self.mandatory:
            if count.get(item, 0) != 1:
                self.err(w, f"mandatory item {item} has {count.get(item, 0)} rows; exactly one is required")

    def run(self, doc):
        if not self.top(doc):
            return
        # bound mode: forced by --require-binding, or declared by the oracle itself using any {fact, binding} entry
        if not self.bound_mode:
            self.bound_mode = any(_is_fact_mapping(x) for lst in _iter_must_state_lists(doc) for x in lst)
        covered = set()
        covered |= self.chains(doc.get("chains"))
        covered.add(self.side_by_side(doc.get("side_by_side")))
        covered.add(self.both_ways(doc.get("f1_both_ways")))
        covered |= self.query_rows(doc.get("queries"), "queries", {"query_class", "authority"})
        covered |= self.query_rows(doc.get("controls"), "controls", {"control"})
        self.authority(doc.get("authority_expectations"))
        missing = sorted(q for q in self.query_ids if q not in covered)
        if missing:
            self.err("<coverage>", f"public query ids with no oracle entry: {missing}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("oracle")
    ap.add_argument("--schema", default=DEFAULT_SCHEMA)
    ap.add_argument("--queries", default=DEFAULT_QUERIES)
    ap.add_argument("--state", default=DEFAULT_STATE)
    ap.add_argument("--display-name", default=None, help="name printed for the oracle file (default: its basename)")
    ap.add_argument("--require-binding", action="store_true",
                    help="every must_state fact must carry a binding (BR-ARCH-RULING-2 D-2; node R1-TA2 acceptance)")
    args = ap.parse_args()
    try:
        data, doc = load(args.oracle)
        _, schema = load(args.schema)
        _, queries = load(args.queries)
        _, state = load(args.state)
    except (OSError, yaml.YAMLError) as e:
        print(f"CHECK_ORACLE ERROR: {type(e).__name__}: {str(e).splitlines()[0]}")
        return 2
    c = Checker(schema, queries, state, require_binding=args.require_binding)
    c.run(doc)
    name = args.display_name or os.path.basename(args.oracle)
    print(f"oracle: {name}")
    print(f"sha256: {hashlib.sha256(data).hexdigest()}")
    if isinstance(doc, dict):
        chains = doc.get("chains") or []
        print(f"chains: {len(chains)} (stages per chain: {[len(ch.get('stages') or []) for ch in chains if isinstance(ch, dict)]})")
        print(f"enforcement points per chain: "
              f"{[sum(1 for s in (ch.get('stages') or []) if isinstance(s, dict) and s.get('is_enforcement_point') is True) for ch in chains if isinstance(ch, dict)]}")
        print(f"queries: {len(doc.get('queries') or [])}; controls: {len(doc.get('controls') or [])}")
        print(f"authority_expectations: {len(doc.get('authority_expectations') or [])} rows for "
              f"{len(c.mandatory)} mandatory_bridge_inputs items")
    print(f"binding mode: {'BOUND' if c.bound_mode else 'UNBOUND'}"
          f"{' (required by --require-binding)' if c.require_binding else ''}")
    print(f"must_state facts: bound to their stage {c.fact_counts['stage']}; bound to their query "
          f"{c.fact_counts['query']}; unbound {c.fact_counts['unbound']}")
    print(f"anchors checked: {c.anchor_count}")
    if c.problems:
        print(f"RESULT: INVALID ({len(c.problems)} problems)")
        for p in c.problems:
            print(f" - {p}")
        return 1
    print("RESULT: VALID")
    return 0


if __name__ == "__main__":
    sys.exit(main())
