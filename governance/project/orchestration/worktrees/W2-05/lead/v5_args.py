"""Run 5: turn select_tests.py's JSON into the arguments of the close-form runs (DEC-952, DEC-889 items 6 and 12).

argv: <selection.json> <out folder>. Writes, one item per line:
  parallel-opts.txt  the selection's pytest_options (for the parallel run over `tests`)
  serial-given.txt   every `serial` entry of tests/acceptance/serial-only.txt (GOV_CLOSE_SERIAL_ONLY_GIVEN)
  serial-args.txt    those entries that fall inside the selection and are not left out by its options
"""
import json
import sys
from pathlib import Path

ROOT = Path("/home/usain/gov-os-worktrees/W2-05")
selection = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
out = Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
options = list(selection.get("pytest_options") or [])
(out / "parallel-opts.txt").write_text("".join(f"{o}\n" for o in options), encoding="utf-8")

entries = []
for line in (ROOT / "tests/acceptance/serial-only.txt").read_text(encoding="utf-8").splitlines():
    if not line.strip() or line.lstrip().startswith("#"):
        continue
    entry, _, comment = line.partition(" #")
    if comment.strip().startswith("serial"):
        entries.append(entry.strip())
(out / "serial-given.txt").write_text("".join(f"{e}\n" for e in entries), encoding="utf-8")

targets = [s["target"] for s in selection["selected"]]
ignored = [o.split("=", 1)[1] for o in options if o.startswith("--ignore=")]
deselected = [o.split("=", 1)[1] for o in options if o.startswith("--deselect=")]


def inside(entry):
    file_part = entry.split("::", 1)[0]
    absolute = str(ROOT / file_part)
    if any(absolute == i or absolute.startswith(i.rstrip("/") + "/") for i in ignored):
        return False
    if any(entry == d or str(ROOT / entry) == d or entry.startswith(d.replace(str(ROOT) + "/", "") + "[") for d in deselected):
        return False
    for target in targets:
        t = target.rstrip("/")
        if "::" in t:
            if entry == t or entry.startswith(t + "[") or t.startswith(entry + "::") or t == entry:
                return True
        elif file_part == t or file_part.startswith(t + "/"):
            return True
    return False


chosen = [e for e in entries if inside(e)]
(out / "serial-args.txt").write_text("".join(f"{e}\n" for e in chosen), encoding="utf-8")
print(f"options {len(options)}; serial entries {len(entries)}; serial in the selection {len(chosen)}")
for e in chosen:
    print("  ", e)
