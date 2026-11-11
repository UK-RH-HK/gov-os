"""Whether the selection keeps the suites this ticket's change must reach."""
import json
import sys

d = json.load(open(sys.argv[1]))
ign = d.get("ignore", [])
desel = d.get("deselect", [])
print("keys:", sorted(d))
print("ignore:", len(ign), "deselect:", len(desel))
for want in ("tests/unit/gitenv/", "tests/acceptance/W2-05/", "tests/acceptance/W2-150/", "tests/acceptance/W2-13/",
             "tests/unit/retrieval/test_w2_13_role_filter.py", "tests/unit/guard/test_role_paths.py",
             "tests/unit/util/test_w2_150_role_paths_register.py", "tests/unit/accept/"):
    hit = [i for i in ign if want.startswith(i) or i.startswith(want)]
    print(want, "IGNORED" if any(want.startswith(i) for i in hit) else ("partly ignored" if hit else "kept"))
