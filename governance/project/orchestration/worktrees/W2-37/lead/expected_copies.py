"""Expected after-hashes of the CTO's two copies if the generation is plain: the root .rulesync copy is a byte copy
of template/.rulesync; the .claude copy keeps its own frontmatter (rulesync's form) and takes the template's body."""
import hashlib
from pathlib import Path

root = Path("/home/usain/gov-os-worktrees/W2-37")
tpl = (root / "template/.rulesync/skills/change/SKILL.md").read_bytes()
claude_now = (root / ".claude/skills/change/SKILL.md").read_bytes()


def split(data: bytes):
    assert data.startswith(b"---\n")
    end = data.index(b"\n---\n", 4) + 5
    return data[:end], data[end:]


_, tpl_body = split(tpl)
claude_front, claude_body = split(claude_now)
old_tpl = (root / ".rulesync/skills/change/SKILL.md").read_bytes()  # the root copy, unchanged = template before
_, old_body = split(old_tpl)
print("claude body now == template body before (after normalising one leading newline):",
      claude_body.lstrip(b"\n") == old_body.lstrip(b"\n"))
lead = claude_body[: len(claude_body) - len(claude_body.lstrip(b"\n"))]
new_claude = claude_front + lead + tpl_body.lstrip(b"\n")
print(".rulesync/skills/change/SKILL.md expected after:", hashlib.sha256(tpl).hexdigest())
print(".claude/skills/change/SKILL.md expected after:  ", hashlib.sha256(new_claude).hexdigest())
print(".claude now:", hashlib.sha256(claude_now).hexdigest())
