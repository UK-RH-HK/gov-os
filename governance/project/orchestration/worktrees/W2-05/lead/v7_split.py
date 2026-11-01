"""Run 7: split select_tests.py's selected targets into the parallel run's parts, so that each part names exactly the
selected targets under it (pytest applies --ignore only while it walks a folder, never to a path named on its command
line: the first run's globs ran folders the selection leaves out). argv: <selection.json> <out folder>.
Writes targets-unit.txt, targets-w1.txt, targets-w2.txt (one target a line) and prints the counts."""
import json
import sys
from pathlib import Path

selection = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
out = Path(sys.argv[2])
parts = {"unit": [], "w1": [], "w2": []}
for item in selection["selected"]:
    target = item["target"]
    if target.startswith("tests/unit"):
        parts["unit"].append(target)
    elif target.startswith("tests/acceptance/W1-"):
        parts["w1"].append(target)
    elif target.startswith("tests/acceptance/W2-"):
        parts["w2"].append(target)
    else:
        sys.exit(f"a target in no part: {target}")
for name, targets in parts.items():
    (out / f"targets-{name}.txt").write_text("".join(f"{t}\n" for t in targets), encoding="utf-8")
    print(name, len(targets))
