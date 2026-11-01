"""Says whether the held-out list file is tracked, without printing its path or contents."""
import subprocess
import sys

sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-91/src")
from gov.guard.heldout import CONFIG_REL  # noqa: E402

out = subprocess.run(["git", "-C", "/home/usain/gov-os-worktrees/W2-91", "ls-files", "--", CONFIG_REL],
                     capture_output=True, text=True).stdout.strip()
print("held-out list file tracked:", bool(out))
print("under governance/:", CONFIG_REL.startswith("governance/"))
