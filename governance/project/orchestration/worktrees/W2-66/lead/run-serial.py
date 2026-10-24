"""The lead's serial-only run, in the close's form (DEC-889 items 6 and 12, DEC-905).

Reads tests/acceptance/serial-only.txt (entries without their comments), sets GOV_CLOSE_SERIAL_ONLY_GIVEN to the
entries one per line, and runs them without -n, with the retention option and JUnit XML. The caller holds the lock.
"""
import os
import sys

root = "/home/usain/gov-os-worktrees/W2-66"
entries = []
with open(os.path.join(root, "tests/acceptance/serial-only.txt"), encoding="utf-8") as f:
    for line in f:
        entry = line.split("#", 1)[0].strip() if not line.lstrip().startswith("#") else ""
        if entry:
            entries.append(entry)
print(f"{len(entries)} serial-only entries", flush=True)
env = dict(os.environ)
env["GOV_CLOSE_SERIAL_ONLY_GIVEN"] = "\n".join(entries)
cmd = [sys.executable, "-m", "pytest", *entries, "-q", "-p", "no:cacheprovider", "-p", "gov_close_serial_only",
       "-o", "tmp_path_retention_policy=failed", "-rs",
       f"--junitxml={root}/.gov-runtime/scratch/lead/log/{sys.argv[1] if len(sys.argv) > 1 else 'serial'}.xml"]
os.chdir(root)
os.execve(sys.executable, cmd, env)
