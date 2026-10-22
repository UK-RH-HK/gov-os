"""Plant a one-hour sleep as the first statement of ``def run(...)`` in a module of a trial clone (never the repository)."""
import re
import sys

path = sys.argv[1]
assert "/gov-os-runs/" in path, "only in a trial clone under ~/gov-os-runs"
text = open(path).read()
m = re.search(r"^def run\(.*?\)\s*(->[^:\n]*)?:\s*\n", text, re.M | re.S)
assert m, f"no run() in {path}"
body = text[m.end():]
doc = re.match(r'(\s+)("""[\s\S]*?"""\n)', body)  # keep a docstring first
indent = re.match(r"(\s+)", body).group(1).split("\n")[-1]
insert = f"{indent}import time; time.sleep(3600)  # tool trial a: a planted hang in a child-only path\n"
at = m.end() + (doc.end() if doc else 0)
open(path, "w").write(text[:at] + insert + text[at:])
print("planted at offset", at)
