"""Lead's check: on the ACT's parent map, does an acceptance .py reach W1-50's case or W1-28's file at all?"""
import subprocess
import sys

import yaml

sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-66c-tests/src")
from gov.close import select  # noqa: E402

TREE = "/home/usain/gov-os-worktrees/W2-66c-tests"
for rev in ("795d97c7cd44", "8038e0ee648c"):
    text = subprocess.run(["git", "-C", TREE, "show", f"{rev}:governance/project/test-map.yaml"],
                          capture_output=True, text=True, check=True).stdout
    m = yaml.safe_load(text)
    for path in ("tests/acceptance/W3-98/test_w3_98_planted.py", "tests/acceptance/W3-98/conftest.py",
                 "tests/acceptance/W3-98/notes_planted.md"):
        targets = [t for c in m.get("couplings") or [] if any(select.match(path, p) for p in c.get("paths") or [])
                   for t in c.get("suites") or []]
        w150 = [t for t in targets if "W1-50" in t]
        w128 = [t for t in targets if "W1-28" in t]
        w101 = [t for t in targets if "W1-01" in t]
        print(rev, path.rsplit("/", 1)[1], "W1-50:", w150, "W1-28:", w128, "W1-01:", w101)
