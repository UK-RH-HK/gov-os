"""sha256 rows for the CIT-P: each kernel file of the four skills at HEAD, its line count, and a check that its two
.rulesync copies hold the same bytes (from git objects, not the working tree)."""
import hashlib
import subprocess
import sys

head = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
root = "/home/usain/gov-os-worktrees/W2-100"


def blob(path):
    return subprocess.run(["git", "-C", root, "show", f"{head}:{path}"], capture_output=True, check=True).stdout


names = subprocess.run(["git", "-C", root, "ls-tree", "-r", "--name-only", head, "template/governance/kernel/skills/"],
                       capture_output=True, text=True, check=True).stdout.split()
rows, bad = [], []
for skill in ("backend", "api", "data", "security"):
    for path in sorted(n for n in names if n.startswith(f"template/governance/kernel/skills/{skill}/")):
        data = blob(path)
        sha = hashlib.sha256(data).hexdigest()
        rel = path[len("template/governance/kernel/skills/"):]
        for copy in (f".rulesync/skills/{rel}", f"template/.rulesync/skills/{rel}"):
            if hashlib.sha256(blob(copy)).hexdigest() != sha:
                bad.append(copy)
        rows.append(f"| `{path}` | absent | `{sha}` | {data.count(b'\n')} |")
print("\n".join(rows))
print(f"\n{len(rows)} kernel files; copies differing: {bad or 'none'}", file=sys.stderr)
