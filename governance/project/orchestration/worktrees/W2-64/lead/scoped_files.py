"""Print the test files run 2's scoped run takes (DEC-954): every test file the test designer changed since the
run-2 merge, the two whose support it changed, this ticket's own folder and the unit check tests (lead's scratch)."""
import subprocess
from pathlib import Path

W = Path("/home/usain/gov-os-worktrees/W2-64")
SERIAL = W / "tests/acceptance/serial-only.txt"
changed = subprocess.run(["git", "-C", str(W), "diff", "--name-only", "24d70ca7", "HEAD"],
                         capture_output=True, text=True, check=True).stdout.split()
files = [p for p in changed if Path(p).name.startswith("test_") and p.endswith(".py")]
# the two cases whose support module changed (W2-54's box, W2-57's list support)
files += ["tests/acceptance/W2-54/test_w2_54_audit_report.py", "tests/acceptance/W2-57/test_w2_57_nightly_route.py"]
files += ["tests/acceptance/W2-64", "tests/unit/check"]
serial = set()
for line in SERIAL.read_text(encoding="utf-8").splitlines():
    entry = line.split(" #", 1)[0].strip()
    if entry and not entry.startswith("#"):
        serial.add(entry.split("::", 1)[0])
seen = []
for f in files:
    if f not in seen and not any(f.startswith(p) for p in ["tests/unit/check/"]):
        seen.append(f)
for f in seen:
    if f in serial:
        print("# serial-only:", f)
    else:
        print(f)
