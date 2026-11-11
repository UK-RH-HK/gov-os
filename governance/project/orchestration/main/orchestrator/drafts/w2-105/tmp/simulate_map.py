"""Read-only: run the live map reader (parse_map, _report) on W2-105's README and the 28 collected case ids, all passed."""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-105/src")
from pathlib import Path
from gov.accept import runner

root = Path("/home/usain/gov-os-worktrees/W2-105")
text = (root / "tests/acceptance/W2-105/README.md").read_text(encoding="utf-8")
try:
    mapping = runner.parse_map(text)
except Exception as exc:  # noqa: BLE001
    print("parse_map raised", type(exc).__name__, exc)
    sys.exit(0)
for name in runner.ordered(mapping):
    print(name, len(mapping[name]), "items; first:", mapping[name][:2])
ids = [line.strip() for line in Path(sys.argv[1]).read_text().splitlines() if "::" in line]
cases = []
for line in ids:
    path, rest = line.split("::", 1)
    cases.append(runner.Case(path, rest, "passed"))
result, code = runner._report("DAEO-zpdj", mapping, cases)
print("exit", code, "outcome", result["outcome"], "totals", result["totals"], "unmapped", result["unmapped"])
for line in result["lines"]:
    print(line)
missing_items = sorted({item for items in mapping.values() for item in items
                        if runner.names_a_test(item) and not any(runner.matches(item, c) for c in cases)})
print("items that name a test and match no case:")
for item in missing_items:
    print("  ", item)
