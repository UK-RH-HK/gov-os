#!/usr/bin/env python3
"""W2-187 (DAEO-0cd2) PACKAGE W2-187-P1 (a), a path case by the CTO (DEC-1156 (7)). Run from the repo root."""
p = '.tickets/DAEO-0cd2.md'
t = open(p, encoding='utf-8').read()


def one(o, n):
    global t
    assert t.count(o) == 1, o[:50]
    t = t.replace(o, n)


one("- tests/acceptance/W2-171/w2_171_scenario.py\n",
    "- tests/acceptance/W2-171/w2_171_scenario.py\n"
    "- tests/acceptance/W2-171/test_w2_171_cli_layout_ledger.py\n"
    "- tests/acceptance/W2-171/test_w2_171_s5_misses_f2.py\n")
one("W2-171''s S5 case passes unchanged'",
    "W2-171''s S5 case passes with only its bar value revised (W2-187-P1 (a), DEC-1156 (7))'")
t = t.rstrip('\n') + '\n\n' + (
    "**Path case 2026-11-14 by the CTO (DEC-1156 (7); listed for the owner's reading): W2-187-P1 (a).** Two more W2-171 "
    "acceptance files pin the 85 % bar (`test_w2_171_cli_layout_ledger.py:120-121`, `test_w2_171_s5_misses_f2.py:82`; "
    "`docs/probes/DAEO-0cd2/PACKAGE-W2-187-P1.md`). Both are added to `allowed_paths` for the independent test designer "
    "(bar values only, `Rewrite-Reason: DEC-1179 (2)`), and F5's \"W2-171's S5 case passes unchanged\" now reads \"with "
    "only its bar value revised\", as it already did for W2-170. The behaviour guarded is unchanged; a narrow check "
    "covers it.") + '\n'
open(p, 'w', encoding='utf-8').write(t)
print('ok')
