"""KPI 4's measure: the fixed core-pathmap's judgement applied to a commit's own tree and path map (read from git)."""
import subprocess
import sys

import yaml

from gov.check import pathmap

ROOT = "/home/usain/gov-os-worktrees/W2-95"
ref = sys.argv[1]
head = subprocess.run(["git", "-C", ROOT, "rev-parse", "--short=12", ref], capture_output=True, text=True).stdout.strip()
text = subprocess.run(["git", "-C", ROOT, "show", f"{ref}:{pathmap.PATH_MAP_REL}"], capture_output=True, text=True,
                      check=True).stdout
spaces = pathmap._namespaces(yaml.safe_load(text))
if isinstance(spaces, str):
    print("PATH_MAP_INVALID", spaces)
    sys.exit(1)
out = subprocess.run(["git", "-C", ROOT, "ls-tree", "-r", "--name-only", "-z", ref], capture_output=True,
                     encoding="utf-8", errors="surrogateescape", check=True).stdout
tracked = [f for f in out.split("\0") if f]
none, two = [], []
for path in tracked:
    matched = [name for name, patterns in spaces if any(pathmap._matches(path, p) for p in patterns)]
    if not matched:
        none.append(path)
    elif len(matched) > 1:
        two.append((path, matched))
print(f"ref {ref} at {head}: {len(tracked)} tracked paths, {len(spaces)} namespaces")
print(f"in no namespace: {len(none)}")
for path in none:
    print("  NONE", path)
print(f"in two or more: {len(two)}")
for path, matched in two:
    print("  TWO ", path, matched)
