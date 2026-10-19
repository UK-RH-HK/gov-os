"""DEC-617: the proposal for stage A3 of this repository's adoption. It moves nothing. It names the files of the
old cli/ tree for deletion from the active tree, in one batch; everything it does not name is kept by the tool."""
import subprocess
import yaml

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS"
OUT = "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/45f2a529-6746-474d-b738-e1df6781c663/scratchpad/adopt-proposal.yaml"
files = subprocess.run(["git", "-C", ROOT, "ls-files", "-z", "cli"], capture_output=True, check=True).stdout.decode().split("\0")
files = [f for f in files if f]
doc = {"artefacts": [{"path": f, "action": "DELETE_FROM_ACTIVE_TREE", "batch": 1} for f in files]}
with open(OUT, "w", encoding="utf-8") as f:
    yaml.safe_dump(doc, f, sort_keys=False)
print(len(files), "files named in", OUT)
