#!/usr/bin/env python3
"""Negative-control self-test for check_oracle.py (run BR-AR-0002, DAG node TA; binding cases added by run
BR-AR-0021, node R1-TA2).

Loads a VALID oracle, applies structural mutations in memory only (nothing is written anywhere), and checks that
check_oracle.Checker accepts the unmodified oracle and rejects every mutation. Prints one line per case,
`<case> expected=<VALID|INVALID> got=<VALID|INVALID> <PASS|FAIL>`, and never echoes oracle content. Generic: the
mutations are structural (a removed or reordered stage, a second enforcement point, a missing or re-classed authority
row, an anchor without a commit, an uncovered query, and must_state text asserting a classification or a
disposition). When the oracle is in BOUND mode (BR-ARCH-RULING-2 D-2 per-fact binding, see check_oracle.py) the
binding cases also run: an unbound fact, a stage fact bound to another stage, a stage fact bound to the whole chain,
a query fact bound to a stage, an unknown fact key, and a bound fact asserting a classification. Pass
`--require-binding` to run every case under that flag too. Exit 0 iff every case behaves as expected.
"""
import copy
import os
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_oracle as co  # noqa: E402


def mutations(base):
    def m(fn):
        d = copy.deepcopy(base)
        fn(d)
        return d

    def first_anchor(d):
        st = d["chains"][0]["stages"][0]["anchors"]
        return next(iter(st.values()))[0]

    def swap(d):
        s = d["chains"][0]["stages"]
        s[0], s[1] = s[1], s[0]

    def second_enforcement(d):
        for s in d["chains"][0]["stages"]:
            if not s["is_enforcement_point"]:
                s["is_enforcement_point"] = True
                return

    def reclass(d):
        row = d["authority_expectations"][0]
        row["class"] = "DERIVED_NOT_A_MANDATORY_CLASS"

    return [
        ("unmodified", "VALID", copy.deepcopy(base)),
        ("stage removed", "INVALID", m(lambda d: d["chains"][0]["stages"].pop(3))),
        ("stages out of order", "INVALID", m(swap)),
        ("second enforcement point", "INVALID", m(second_enforcement)),
        ("no enforcement point", "INVALID",
         m(lambda d: [s.__setitem__("is_enforcement_point", False) for s in d["chains"][1]["stages"]])),
        ("authority row missing", "INVALID", m(lambda d: d["authority_expectations"].pop())),
        ("authority row duplicated", "INVALID",
         m(lambda d: d["authority_expectations"].append(copy.deepcopy(d["authority_expectations"][0])))),
        ("authority class not verbatim", "INVALID", m(reclass)),
        ("anchor lacks commit", "INVALID", m(lambda d: first_anchor(d).pop("commit"))),
        ("anchor lacks path", "INVALID", m(lambda d: first_anchor(d).pop("path"))),
        ("anchor commit abbreviated", "INVALID", m(lambda d: first_anchor(d).__setitem__("commit", "3c880d8"))),
        ("trap without why", "INVALID",
         m(lambda d: [s["traps"][0].pop("why") for s in d["chains"][0]["stages"] if s["traps"]][:1])),
        ("control query uncovered", "INVALID", m(lambda d: d["controls"].pop())),
        ("classification asserted", "INVALID",
         m(lambda d: add_fact(d["queries"][0]["must_state"], "F2 and F3 are one deeper class", "query"))),
        ("disposition asserted", "INVALID",
         m(lambda d: add_fact(d["queries"][0]["must_state"], "the exemption should be deleted", "query"))),
    ] + (binding_cases(base, m) if bound(base) else [])


def bound(base):
    return any(isinstance(x, dict) for lst in co._iter_must_state_lists(base) for x in lst)


def add_fact(lst, text, binding):
    """Append a fact in the shape the list already uses (a {fact, binding} mapping in bound mode)."""
    if any(isinstance(x, dict) for x in lst):
        lst.append({"fact": text, "binding": binding})
    else:
        lst.append(text)


def binding_cases(base, m):
    def first_bound_stage(d):
        for ch in d["chains"]:
            for i, st in enumerate(ch["stages"]):
                if st.get("must_state"):
                    return ch["stages"], i
        raise AssertionError("bound oracle has no stage fact")

    def unbind(d):
        stages, i = first_bound_stage(d)
        stages[i]["must_state"][0] = stages[i]["must_state"][0]["fact"]

    def other_stage(d):
        stages, i = first_bound_stage(d)
        other = stages[(i + 1) % len(stages)]["stage"]
        stages[i]["must_state"][0] = dict(stages[i]["must_state"][0], binding=other)

    def chain_bound(d):
        stages, i = first_bound_stage(d)
        stages[i]["must_state"][0] = dict(stages[i]["must_state"][0], binding="chain")

    def query_to_stage(d):
        q = d["queries"][0]
        q["must_state"][0] = dict(q["must_state"][0], binding=d["chains"][0]["stages"][0]["stage"])

    def extra_key(d):
        q = d["queries"][0]
        q["must_state"][0] = dict(q["must_state"][0], note="x")

    def bound_classification(d):
        stages, i = first_bound_stage(d)
        stages[i]["must_state"].append({"fact": "F2 and F3 are one deeper class", "binding": stages[i]["stage"]})

    def strip_all(d):
        for lst in co._iter_must_state_lists(d):
            lst[:] = [x["fact"] if isinstance(x, dict) else x for x in lst]

    return [
        # the run-1 (unbound) form stays valid unless --require-binding is given (backward compatibility)
        ("bound: every fact unbound (run-1 form)", "INVALID" if REQUIRE_BINDING else "VALID", m(strip_all)),
        ("bound: fact without binding", "INVALID", m(unbind)),
        ("bound: stage fact bound to another stage", "INVALID", m(other_stage)),
        ("bound: stage fact bound to the chain (D-2 not adopted)", "INVALID", m(chain_bound)),
        ("bound: query fact bound to a stage", "INVALID", m(query_to_stage)),
        ("bound: unknown fact key", "INVALID", m(extra_key)),
        ("bound: stage fact asserting a classification", "INVALID", m(bound_classification)),
    ]


REQUIRE_BINDING = "--require-binding" in sys.argv[1:]


def main():
    args = [a for a in sys.argv[1:] if a != "--require-binding"]
    require_binding = REQUIRE_BINDING
    if len(args) != 1:
        print("usage: selftest_check_oracle.py <valid oracle> [--require-binding]")
        return 2
    with open(args[0], "rb") as f:
        base = yaml.safe_load(f.read().decode("utf-8"))
    _, schema = co.load(co.DEFAULT_SCHEMA)
    _, queries = co.load(co.DEFAULT_QUERIES)
    _, state = co.load(co.DEFAULT_STATE)
    print(f"binding mode of the base oracle: {'BOUND' if bound(base) else 'UNBOUND'}; "
          f"--require-binding: {require_binding}")
    failures = 0
    for name, expected, doc in mutations(base):
        c = co.Checker(schema, queries, state, require_binding=require_binding)
        c.run(doc)
        got = "INVALID" if c.problems else "VALID"
        ok = got == expected
        failures += 0 if ok else 1
        print(f"{name}: expected={expected} got={got} {'PASS' if ok else 'FAIL'}")
    print(f"RESULT: {'ALL PASS' if failures == 0 else f'{failures} FAIL'}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
