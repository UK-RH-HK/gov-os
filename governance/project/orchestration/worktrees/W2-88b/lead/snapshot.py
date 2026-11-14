"""F2 snapshot: every path's mtime, size and mode under an original the proofs read, plus `git status --porcelain`
and HEAD, as one digest and a JSON file. Usage: python3 snapshot.py <root> <out.json>. Reads only."""
import hashlib
import json
import os
import subprocess
import sys

root, out = sys.argv[1], sys.argv[2]
rows = []
for base, dirs, files in os.walk(root):
    dirs.sort()
    for name in sorted(dirs + files):
        path = os.path.join(base, name)
        try:
            st = os.lstat(path)
        except OSError:
            continue
        rows.append(f"{os.path.relpath(path, root)}\t{st.st_mtime_ns}\t{st.st_size}\t{st.st_mode}")
st = os.lstat(root)
rows.append(f".\t{st.st_mtime_ns}\t{st.st_size}\t{st.st_mode}")
env = {**os.environ, "GIT_OPTIONAL_LOCKS": "0"}  # git status never refreshes the original's index (no write there)
status = subprocess.run(["git", "-C", root, "status", "--porcelain=v1", "--untracked-files=all"],
                        capture_output=True, text=True, env=env).stdout
head = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], capture_output=True, text=True, env=env).stdout.strip()
digest = hashlib.sha256("\n".join(rows).encode()).hexdigest()
record = {"root": root, "paths": len(rows), "mtime_digest": digest, "head": head,
          "git_status_sha256": hashlib.sha256(status.encode()).hexdigest(), "git_status_lines": len(status.splitlines())}
with open(out, "w", encoding="utf-8") as handle:
    json.dump(record, handle, indent=1)
print(json.dumps(record))
