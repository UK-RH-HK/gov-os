"""Which README-map items of W2-05 name a test that no collected case matches (why gov accept fails a line)."""
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-05/src")
from gov.accept import runner  # noqa: E402

root = Path("/home/usain/gov-os-worktrees/W2-05")
folder = root / "tests/acceptance/W2-05"
mapping = runner.parse_map((folder / "README.md").read_text(encoding="utf-8"))
print("lines:", {k: len(v) for k, v in mapping.items()})
print("needed optins:", runner.needed_optins(root, folder, mapping))
env = dict(os.environ, GOV_TESTS_OPTIN="breadth", PYTHONPATH=str(root / "src"))
out = subprocess.run([sys.executable, "-m", "pytest", str(folder), "--collect-only", "-q", "-p", "no:cacheprovider"],
                     capture_output=True, text=True, cwd=root, env=env).stdout
cases = []
for line in out.splitlines():
    if "::" in line:
        path, _, name = line.partition("::")
        cases.append(runner.Case(path, name, "passed"))
print("collected:", len(cases))
for name, items in mapping.items():
    for item in items:
        if runner.names_a_test(item) and not any(runner.matches(item, c) for c in cases):
            print("MISSING", name, repr(item))
