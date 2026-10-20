"""Step 2: the copy with the product's own .gitignore kept, the adapter generation step, a commit, the hooks."""
import json
import os
import subprocess

BASE = "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/45f2a529-6746-474d-b738-e1df6781c663/scratchpad/dev-tier-exp"
CLONE = os.path.join(BASE, "b dev clone")
SOURCE = os.path.join(BASE, "template-source")
GIT_ID = ["-c", "user.name=experiment", "-c", "user.email=experiment@example.invalid"]
GENERATE = "rulesync generate --targets claudecode,agentsmd --features rules,hooks,permissions,subagents,commands,skills"


def run(argv, cwd, check=True, **more):
    done = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, **more)
    print("$", " ".join(argv)[:150], "->", done.returncode)
    for line in (done.stdout + done.stderr).strip().splitlines()[-10:]:
        print("   ", line[:200])
    if check and done.returncode != 0:
        raise SystemExit(1)
    return done


run(["/home/usain/.local/bin/copier", "copy", "--trust", "--defaults", "--skip", ".gitignore", SOURCE, CLONE], BASE)
with open(os.path.join(CLONE, ".gitignore"), "a") as f:
    f.write("\n# added for the kernel (the template's two lines; the copy stopped at this file)\n.gov-runtime/\n__pycache__/\n")
print("top level after copy:", sorted(os.listdir(CLONE)))
run(["git", "add", "-A"], CLONE)
run(["git", *GIT_ID, "commit", "-q", "-m", "kernel installed by copier copy"], CLONE)
run(GENERATE.split(), CLONE, check=False)
run(["git", "status", "--short"], CLONE, check=False)
run(["git", "add", "-A"], CLONE)
run(["git", *GIT_ID, "commit", "-q", "-m", "adapter generation step"], CLONE, check=False)
settings = json.load(open(os.path.join(CLONE, ".claude", "settings.json")))
for event, groups in settings.get("hooks", {}).items():
    for group in groups:
        for entry in group.get("hooks", []):
            print(event, "| matcher", group.get("matcher"), "| timeout", entry.get("timeout"), "|", entry.get("command"))
print("permissions keys:", list(settings.get("permissions", {}).keys()))
