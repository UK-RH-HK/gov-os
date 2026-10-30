"""W2-85 lead check: the two W2-54 cases are routed to the nightly by this worktree's code (DEC-732)."""
import sys
from pathlib import Path

ROOT = Path("/home/usain/gov-os-worktrees/W2-85")
sys.path.insert(0, str(ROOT / "src"))

import gov  # noqa: E402
from gov.close import serial  # noqa: E402
from gov.close.pytest_plugin import gov_close_serial_only as plugin  # noqa: E402

TWO = [
    "tests/acceptance/W2-54/test_w2_54_time_limit.py::test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit",
    "tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_context_reproducibility_green_here",
]

print("gov:", gov.__file__)
entries = plugin.entries(ROOT)
routed = serial.nightly(ROOT)
kept = serial.phase(ROOT, entries)
print("list entries:", len(entries))
print("nightly entries:", len(routed))
print("serial-phase entries:", len(kept))
ok = True
for case in TWO:
    in_list = case in entries
    in_nightly = case in routed
    in_phase = case in kept
    print(f"{case}\n  in list {in_list}, routed to the nightly {in_nightly}, in the serial phase {in_phase}")
    ok = ok and in_list and in_nightly and not in_phase
print("RESULT:", "OK" if ok else "WRONG")
sys.exit(0 if ok else 1)
