#!/usr/bin/env python3
"""Negative-control self-test for check_oracle.py (run BR-AR-0002, DAG node TA).

Loads a VALID oracle, applies structural mutations in memory only (nothing is written anywhere), and checks that
check_oracle.Checker accepts the unmodified oracle and rejects every mutation. Prints one line per case,
`<case> expected=<VALID|INVALID> got=<VALID|INVALID> <PASS|FAIL>`, and never echoes oracle content. Generic: the
mutations are structural (a removed or reordered stage, a second enforcement point, a missing or re-classed authority
row, an anchor without a commit, an uncovered query, and must_state text asserting a classification or a
disposition). Exit 0 iff every case behaves as expected.
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
         m(lambda d: d["queries"][0]["must_state"].append("F2 and F3 are one deeper class"))),
        ("disposition asserted", "INVALID",
         m(lambda d: d["queries"][0]["must_state"].append("the exemption should be deleted"))),
    ]


def main():
    if len(sys.argv) != 2:
        print("usage: selftest_check_oracle.py <valid oracle>")
        return 2
    with open(sys.argv[1], "rb") as f:
        base = yaml.safe_load(f.read().decode("utf-8"))
    _, schema = co.load(co.DEFAULT_SCHEMA)
    _, queries = co.load(co.DEFAULT_QUERIES)
    _, state = co.load(co.DEFAULT_STATE)
    failures = 0
    for name, expected, doc in mutations(base):
        c = co.Checker(schema, queries, state)
        c.run(doc)
        got = "INVALID" if c.problems else "VALID"
        ok = got == expected
        failures += 0 if ok else 1
        print(f"{name}: expected={expected} got={got} {'PASS' if ok else 'FAIL'}")
    print(f"RESULT: {'ALL PASS' if failures == 0 else f'{failures} FAIL'}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
