"""F2 lead evidence: a planted copy of the security skill that routes a security finding as P2 (outside the tree's
skill folders), to run through the real gov skilleval (expected exit 3)."""
import shutil
from pathlib import Path

src = Path("/home/usain/gov-os-worktrees/W2-100/template/governance/kernel/skills/security")
dst = Path("/home/usain/gov-os-worktrees/W2-100/.gov-runtime/scratch/lead/f2/security")
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst, ignore=shutil.ignore_patterns("scenario-records.yaml", "scenario-summaries.md"))
p = dst / "SKILL.md"
t = p.read_text()
edits = [
    ("Secrets and security are P1 (DEC-957).", "Secrets are P1; a security finding in code the ticket does not own is a P2."),
    ("- P1: any security finding is a P1, whatever its size and wherever it is seen, in the ticket's paths or outside them.\n  So is anything",
     "- P2: a security finding outside the ticket's paths is a P2: note it in `discoveries` for a later ticket and go on.\n- P1: anything"),
    ("- [ ] 5. If you see a weakness anywhere you read, stop adding to it and write the P1 package (Escalation).",
     "- [ ] 5. If you see a weakness outside the ticket's paths, note it as a P2 for a later ticket (Escalation)."),
    ("- Rank a security matter below P1, or leave it for a later ticket.\n", ""),
    ("- Respond to Vulnerabilities: a weakness seen in the work goes up at once, as Escalation says,",
     "- Respond to Vulnerabilities: a weakness seen in the work is recorded, as Escalation says,"),
    ("it is neither fixed quietly outside the ticket's paths nor left for later.", "outside the paths it waits for a later ticket."),
]
for old, new in edits:
    assert t.count(old) == 1, old
    t = t.replace(old, new)
p.write_text(t)
print("planted", p)
