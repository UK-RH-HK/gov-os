#!/usr/bin/env python3
"""Compare test function names and assert counts per file between two commits."""
import re
import subprocess
import sys

base, head = sys.argv[1], sys.argv[2]
files = subprocess.run(["git", "diff", "--name-only", base, head, "--", "tests/acceptance"],
                       capture_output=True, text=True, check=True).stdout.split()
for path in files:
    if not path.endswith(".py"):
        continue
    def show(rev):
        r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, text=True)
        return r.stdout if r.returncode == 0 else ""
    a, b = show(base), show(head)
    da = set(re.findall(r"^def (test_\w+)", a, re.M))
    db = set(re.findall(r"^def (test_\w+)", b, re.M))
    print(f"{path}: tests {len(da)} -> {len(db)}; asserts {a.count('assert ')} -> {b.count('assert ')}; "
          f"skip/xfail {len(re.findall(r'skip|xfail', a))} -> {len(re.findall(r'skip|xfail', b))}; "
          f"gone={sorted(da - db)}")
