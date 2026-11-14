"""Apply the base's .rulesync -> .claude transform (as seen at 5336a6fca) to HEAD's .rulesync adopt skill; print sha256s."""
import hashlib
import subprocess

def show(rev, path):
    return subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, check=True).stdout.decode()

def transform(text, desc_folded):
    lines = text.split("\n")
    out, i = [], 0
    assert lines[0] == "---"
    out.append(lines[0])
    i = 1
    while lines[i] != "---":
        if lines[i].startswith("description: "):
            out.extend(desc_folded)
        elif lines[i].startswith("version: "):
            pass
        else:
            out.append(lines[i])
        i += 1
    out.append("---")
    i += 1
    if lines[i] == "":
        i += 1
    out.extend(lines[i:])
    return "\n".join(out)

base_claude = show("5336a6fca", ".claude/skills/adopt/SKILL.md")
folded = base_claude.split("\n")[2:5]
base_rs = show("5336a6fca", ".rulesync/skills/adopt/SKILL.md")
assert transform(base_rs, folded) == base_claude, "transform does not reproduce the base"
new = transform(show("HEAD", ".rulesync/skills/adopt/SKILL.md"), folded)
print("base reproduced; new sha256", hashlib.sha256(new.encode()).hexdigest())
print("expected      ", "65d6abd920ddb6180e734a124ea53b02a0c5386126d09490c231b87b9eb75dbc")
