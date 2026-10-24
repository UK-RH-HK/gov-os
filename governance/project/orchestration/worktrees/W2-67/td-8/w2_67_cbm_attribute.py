"""Batch 8: from the tracer's JSON lines, each daemon folder and the case that built its project.

A project under ``popen-gwN/<dir>/`` belongs to the case of worker ``gwN`` whose test name begins with ``<dir>``
less pytest's counter; a project under a session folder (``<name>0`` made by ``mktemp``) is reported as such.
"""

import json
import re
import sys
from collections import defaultdict

by_folder = {}
cases = defaultdict(list)
for path in sys.argv[1:]:
    for line in open(path, encoding="utf-8"):
        row = json.loads(line)
        root = row["root"]
        m = re.search(r"/(popen-gw\d+|pytest-\d+)/([^/]+)/(.*)$", root)
        if not m:
            continue
        worker, folder_dir, rest = m.group(1), m.group(2), m.group(3)
        prefix = re.sub(r"\d+$", "", folder_dir)
        name = row["case"].split("::")[-1]
        own = (row["worker"] == worker.replace("popen-", "") or worker.startswith("pytest-")) and \
            name.startswith(prefix[:30])
        if own and row["folder"] not in by_folder:
            by_folder[row["folder"]] = (row["case"], f"{folder_dir}/{rest}", row["holders"])
        by_folder.setdefault(row["folder"] + "?", (None, f"{worker}/{folder_dir}/{rest}", row["holders"]))
for folder, (case, root, holders) in sorted(by_folder.items(), key=lambda kv: str(kv[1][0])):
    if folder.endswith("?"):
        if folder[:-1] in by_folder:
            continue
        print(f"{folder[:-1]}  (no own sighting)  {root}")
        continue
    cases[case].append((folder, root))
for case, rows in sorted(cases.items()):
    print(case)
    for folder, root in rows:
        print(f"    {folder}  {root}")
print(sum(len(r) for r in cases.values()), "folders,", len(cases), "cases")
