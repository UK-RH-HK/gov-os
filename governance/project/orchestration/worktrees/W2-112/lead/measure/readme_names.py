"""Which test names the README of an acceptance folder names that no test function in the folder defines."""
import re
import sys
from pathlib import Path

folder = Path(sys.argv[1])
named = set(re.findall(r"`(?:[\w/.]+::)?(test_\w+)(?:\[[^\]]*\])?`", (folder / "README.md").read_text()))
defined = set()
for f in folder.glob("test_*.py"):
    defined |= set(re.findall(r"^def (test_\w+)", f.read_text(), re.M))
print("named but not defined:", sorted(named - defined))
print("defined but not named:", sorted(defined - named))
