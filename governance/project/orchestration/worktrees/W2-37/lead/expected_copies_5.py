"""Expected after-hashes of the CTO's two copies at version 1.1.0, if the generation is plain: the root .rulesync copy
is a byte copy of template/.rulesync; the .claude copy keeps rulesync's frontmatter form (folded description, metadata
version unquoted, no blank line after the closing ---) with the version 1.1.0, then the template's body.
Usage: python3 expected_copies_5.py <tree with the .claude copy to read>"""
import hashlib
import sys
from pathlib import Path

root = Path("/home/usain/gov-os-worktrees/W2-37")
copy_tree = Path(sys.argv[1]) if len(sys.argv) > 1 else root
tpl = (root / "template/.rulesync/skills/change/SKILL.md").read_bytes()
claude_now = (copy_tree / ".claude/skills/change/SKILL.md").read_bytes()


def split(data: bytes):
    assert data.startswith(b"---\n")
    end = data.index(b"\n---\n", 4) + 5
    return data[:end], data[end:]


tpl_front, tpl_body = split(tpl)
assert b'version: "1.1.0"' in tpl_front, tpl_front
claude_front, claude_body = split(claude_now)
assert claude_front.count(b"  version: 1.0.0\n") == 1, claude_front
new_front = claude_front.replace(b"  version: 1.0.0\n", b"  version: 1.1.0\n")
lead = claude_body[: len(claude_body) - len(claude_body.lstrip(b"\n"))]
new_claude = new_front + lead + tpl_body.lstrip(b"\n")
print("copy tree:", copy_tree)
print(".claude now:", hashlib.sha256(claude_now).hexdigest())
print("template/.rulesync (and kernel) now:", hashlib.sha256(tpl).hexdigest())
print(".rulesync/skills/change/SKILL.md expected after:", hashlib.sha256(tpl).hexdigest())
print(".claude/skills/change/SKILL.md expected after:  ", hashlib.sha256(new_claude).hexdigest())
out = root / ".gov-runtime/scratch/lead/changes/expected-claude-change-SKILL-1.1.0.md"
out.write_bytes(new_claude)
print("written:", out)
