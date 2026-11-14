"""sha256 rows for W2-101's CIT-P, from git objects at a commit: kernel files, before (at the base) and after; and
a check that each .rulesync copy has the same bytes as its kernel file.  python3 citp_sha.py <base> <head>"""
import hashlib
import subprocess
import sys

ROOT = "/home/usain/gov-os-worktrees/W2-101"
base, head = sys.argv[1], sys.argv[2]
SKILLS = ("frontend", "ui-ux", "devops")
FILES = ("SKILL.md", "check_domain_skill.py", "scenario-records.yaml", "scenario-summaries.md", "scenarios.md")


def blob(rev, path):
    r = subprocess.run(["git", "-C", ROOT, "show", f"{rev}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None


tree = subprocess.run(["git", "-C", ROOT, "ls-tree", "-r", "--name-only", head, "template/governance/kernel/skills/"],
                      capture_output=True, text=True).stdout.split()
extra = [p for p in tree if p.split("/")[4] in SKILLS and p.split("/")[-1] not in FILES]
assert not extra, f"files not in the table: {extra}"
bad = []
print("| File | Before | After (sha256) | Lines |\n|---|---|---|---|")
for s in SKILLS:
    for f in FILES:
        k = f"template/governance/kernel/skills/{s}/{f}"
        after, before = blob(head, k), blob(base, k)
        assert after is not None, k
        b = "absent" if before is None else f"`{hashlib.sha256(before).hexdigest()}`"
        lines = after.count(b"\n")
        print(f"| `{k}` | {b} | `{hashlib.sha256(after).hexdigest()}` | {lines} |")
        for c in (f".rulesync/skills/{s}/{f}", f"template/.rulesync/skills/{s}/{f}"):
            if blob(head, c) != after:
                bad.append(c)
    for root in (".rulesync/skills", "template/.rulesync/skills"):
        names = subprocess.run(["git", "-C", ROOT, "ls-tree", "-r", "--name-only", head, f"{root}/{s}/"],
                               capture_output=True, text=True).stdout.split()
        bad += [n for n in names if n.split("/")[-1] not in FILES]
    claude = subprocess.run(["git", "-C", ROOT, "ls-tree", "-r", "--name-only", head, f".claude/skills/{s}/"],
                            capture_output=True, text=True).stdout.split()
    bad += [f"(present) {n}" for n in claude]
print("\ncopies:", "all byte-equal, no extra file, nothing under .claude/skills" if not bad else f"DIFFER {bad}")
