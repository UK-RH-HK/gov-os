"""Read-only: the merged tree of (synthetic pre-merge commit, w2/integrate): the version lines of every skill in its
four places (kernel source, .rulesync, template/.rulesync, .claude copy).  Usage: check_versions.py <synthetic> <integrate>"""
import re
import subprocess
import sys

REPO = "/home/usain/Dynamic-Agentic-Engineering-OS"
A, B = sys.argv[1], sys.argv[2]
out = subprocess.run(["git", "-C", REPO, "merge-tree", "--write-tree", A, B], capture_output=True, text=True).stdout
tree = out.splitlines()[0].strip()
print("merged tree", tree[:12])
places = {"kernel": "template/governance/kernel/skills/%s/SKILL.md", "rulesync": ".rulesync/skills/%s/SKILL.md",
          "t.rulesync": "template/.rulesync/skills/%s/SKILL.md", "claude": ".claude/skills/%s/SKILL.md"}
ls = subprocess.run(["git", "-C", REPO, "ls-tree", "-r", "--name-only", tree, "template/governance/kernel/skills/"],
                    capture_output=True, text=True).stdout.split()
skills = sorted({p.split("/")[4] for p in ls if p.endswith("SKILL.md")})


def versions(path):
    r = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (tree, path)], capture_output=True, text=True)
    if r.returncode:
        return None
    head = r.stdout.split("\n---", 1)[0]
    top = re.findall(r"^version:\s*\"?([\w.]+)\"?\s*$", head, re.M)
    meta = re.findall(r"^\s+version:\s*\"?([\w.]+)\"?\s*$", head, re.M)
    marker = "<<<<<<<" in r.stdout
    return (top[0] if top else "-", meta[0] if meta else "-", "MARKERS" if marker else "")


print("%-14s %-22s %-22s %-22s %-22s" % ("skill", *places))
for s in skills:
    row = [versions(p % s) for p in places.values()]
    cells = ["absent" if v is None else "%s/%s%s" % (v[0], v[1], " " + v[2] if v[2] else "") for v in row]
    flag = ""
    vals = {c.split()[0] for c in cells if c != "absent"}
    if len(vals) > 1:
        flag = "  <-- differs"
    print("%-14s %-22s %-22s %-22s %-22s%s" % (s, *cells, flag))
