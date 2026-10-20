"""Resolve the one STANDALONE_TYPES conflict in src/gov/check/schema.py to the ticket's side (DEC-872 step 1).

The ticket's hunk names every type both sides name ("probe", "audit-report") and adds its own; the
AUDIT_REPORT_DIR line W2-54 added already stands, once, after the hunk on the ticket's side.
"""
import re
import sys

path = sys.argv[1]
text = open(path).read()
resolved, n = re.subn(r"<<<<<<< HEAD\n(.*?)=======\n.*?>>>>>>> w2/integrate\n", lambda m: m.group(1), text, flags=re.S)
assert n == 1, f"expected one conflict hunk, found {n}"
assert "<<<<<<<" not in resolved and ">>>>>>>" not in resolved
open(path, "w").write(resolved)
print("resolved 1 hunk")
