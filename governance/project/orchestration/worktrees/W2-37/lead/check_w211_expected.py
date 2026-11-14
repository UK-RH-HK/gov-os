"""Checks that the expected copies (root .rulesync = template bytes; .claude = expected-claude-change-SKILL-1.1.0.md)
pass W2-11's four-places version case and its body case for the change skill, using the suite's own helpers."""
import sys
from pathlib import Path

root = Path("/home/usain/gov-os-worktrees/W2-37")
sys.path.insert(0, str(root / "tests/acceptance/W2-11"))
sys.path.insert(0, str(root / "src"))
import w2_11_support as s  # noqa: E402

expected = {
    "template/governance/kernel/skills": (root / "template/governance/kernel/skills/change/SKILL.md").read_text(),
    "template/.rulesync/skills": (root / "template/.rulesync/skills/change/SKILL.md").read_text(),
    ".rulesync/skills": (root / "template/.rulesync/skills/change/SKILL.md").read_text(),
    ".claude/skills": (root / ".gov-runtime/scratch/lead/changes/expected-claude-change-SKILL-1.1.0.md").read_text(),
}
versions, bodies = {}, {}
for base, text in expected.items():
    front, body = s.split_frontmatter(text)
    meta = front.get("metadata") if isinstance(front.get("metadata"), dict) else {}
    versions[base] = meta.get("version") if base == ".claude/skills" else (front.get("version") or meta.get("version"))
    bodies[base] = s.plain(body)
    if base == ".claude/skills":
        print("claude extra keys:", sorted(set(front) - s.CLAUDE_SKILL_KEYS))
print("versions:", versions, "one version:", len({str(v) for v in versions.values()}) == 1)
kernel = bodies["template/governance/kernel/skills"]
print("bodies equal kernel:", {b: v == kernel for b, v in bodies.items()})
