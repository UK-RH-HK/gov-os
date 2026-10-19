"""DEC-595, DEC-596, DEC-603: build one dev-tier clone with the kernel and generated settings (step 1).

In the session scratchpad only: a clone of the b-dev tier (by exact path, as the suites' clone_tier does) in a
folder whose name holds a space, a temporary template source (copier.yml and template/ of this repository,
file by file, as W1-39's support does), copier copy, the adapter generation step.
"""
import os
import shutil
import subprocess

REPO = "/home/usain/Dynamic-Agentic-Engineering-OS"
BASE = "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/45f2a529-6746-474d-b738-e1df6781c663/scratchpad/dev-tier-exp"
TIER = "/home/usain/gov-os-workbench/synthetic/b-dev"
CLONE = os.path.join(BASE, "b dev clone")
SOURCE = os.path.join(BASE, "template-source")
GIT_ID = ["-c", "user.name=experiment", "-c", "user.email=experiment@example.invalid"]


def run(argv, cwd, check=True, **more):
    done = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, **more)
    print("$", " ".join(argv)[:150], "->", done.returncode)
    tail = (done.stdout + done.stderr).strip().splitlines()[-12:]
    for line in tail:
        print("   ", line[:200])
    if check and done.returncode != 0:
        raise SystemExit(1)
    return done


shutil.rmtree(BASE, ignore_errors=True)
os.makedirs(BASE)
run(["git", "clone", "-q", TIER, CLONE], BASE)
listing = subprocess.run(["git", "-C", REPO, "ls-files", "-z", "--", "copier.yml", "template"],
                         capture_output=True, text=True, check=True).stdout
for rel in sorted(item for item in listing.split("\0") if item):
    target = os.path.join(SOURCE, rel)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    shutil.copy2(os.path.join(REPO, rel), target)
run(["git", "init", "-q", "-b", "main"], SOURCE)
run(["git", "add", "-A"], SOURCE)
run(["git", *GIT_ID, "commit", "-q", "-m", "template source"], SOURCE)
run(["git", "tag", "v0.1.0"], SOURCE)
print("clone: commits", subprocess.run(["git", "-C", CLONE, "rev-list", "--count", "HEAD"], capture_output=True,
                                       text=True).stdout.strip(),
      "tracked files", len(subprocess.run(["git", "-C", CLONE, "ls-files"], capture_output=True,
                                          text=True).stdout.splitlines()))
print("top level:", sorted(os.listdir(CLONE)))
run(["/home/usain/.local/bin/copier", "copy", "--trust", "--defaults", SOURCE, CLONE], BASE, check=False)
print("top level after copy:", sorted(os.listdir(CLONE)))
run(["git", "status", "--short"], CLONE, check=False)
