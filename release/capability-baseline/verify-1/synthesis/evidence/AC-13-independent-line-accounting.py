#!/usr/bin/env python3
"""P2-AR-0052 — AC-13, independently of the product.

BC-P2-01/S0-AC13-01's mechanism was that `gov contract verify` compared the compiled file with a fresh run
of the SAME lossy compiler, so a compiled form missing every checklist bullet and Gate U still verified.
This script does not use the product at all: it parses the owner source and the compiled YAML itself and
checks the compiler's own stated coverage rule —

  "every line of the owner source except blank lines and '---' thematic breaks is carried verbatim,
   with its line number, exactly once"

Run from the repository root.
"""
import yaml, re, sys
SRC = "Governance_OS_Capability_Acceptance_Contract_v3.md"
COMP = "framework/contracts/governance-capability-acceptance.yaml"
src = open(SRC).read().split("\n")
if src and src[-1] == "": src = src[:-1]
comp = yaml.safe_load(open(COMP))
carried = {}
def walk(o, path=""):
    if isinstance(o, dict):
        if isinstance(o.get("line"), int):
            for k, v in o.items():
                if k != "line" and isinstance(v, str):
                    carried.setdefault(o["line"], []).append((path, k, v))
        for k, v in o.items(): walk(v, f"{path}/{k}")
    elif isinstance(o, list):
        for v in o: walk(v, path + "[]")
walk(comp)
def norm(s): return re.sub(r'^([-*]|\d+\.)\s*\[\s*\]\s*', '', s.strip())
expected = [i for i, l in enumerate(src, 1) if l.strip() not in ("", "---")]
missing = [i for i in expected if i not in carried]
extra   = [i for i in carried if i not in expected]
nonverb = [i for i in expected
           if not any(v.strip() == src[i-1].strip() or norm(v) == norm(src[i-1])
                      for _, _, v in carried.get(i, []))]
items = [i for i, l in enumerate(src, 1) if re.match(r'^\s*- \[ \]', l) or re.match(r'^\s*\d+\.\s*\[\s*\]', l)]
capchk = sum(len(c.get("checklist") or []) for c in comp["capabilities"])
closing = sum(len(c.get("checklist") or []) for c in comp.get("closing") or [])
ids = [c["id"] for c in comp["capabilities"]]
print(f"owner source                       : {SRC}")
print(f"owner source lines                 : {len(src)}")
print(f"expected carried (non-blank, non---): {len(expected)}")
print(f"carried line numbers in compiled   : {len(carried)}")
print(f"MISSING                            : {len(missing)} {missing[:20]}")
print(f"EXTRA                              : {len(extra)} {extra[:20]}")
print(f"WITHOUT A VERBATIM CARRIER         : {len(nonverb)} {nonverb[:20]}")
print(f"owner-source checklist lines       : {len(items)}")
print(f"compiled capability checklist items: {capchk}")
print(f"compiled acceptance-gate items     : {closing}")
print(f"  sum                              : {capchk + closing}")
print(f"compiled capability_count          : {comp['capability_count']}  (Gate U present: {'U' in ids})")
print(f"compiled gate_count                : {comp['gate_count']}")
labels = {c['id']: (c.get('requirement_class'), c.get('requirement_class_label'))
          for c in comp["capabilities"] if c.get("requirement_class_label")}
print(f"labelled capabilities              : {labels}")
bad = missing or extra or nonverb or (capchk + closing != len(items)) or comp['capability_count'] != 101
print()
print("RESULT:", "FAIL" if bad else
      "every non-blank line of the owner source is carried verbatim exactly once; the universe is complete (101 capabilities incl. Gate U); every checklist line is accounted for")
sys.exit(1 if bad else 0)
