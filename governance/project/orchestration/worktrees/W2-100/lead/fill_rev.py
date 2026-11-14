from pathlib import Path

base = Path("/home/usain/gov-os-worktrees/W2-100")
p = base / ".gov-runtime/scratch/lead/briefs/rev-1.md"
t = p.read_text()
judgement = (base / "governance/project/briefs/JUDGEMENT.md").read_text()
body = judgement.split("\n", 2)[2].strip("\n")  # without its own heading line and the blank line after it
summary = ("lead_verify 2 at b3503e0a3c6d: 16 failed of 6270, the 12 `.claude/skills/` cases (copies ACT) and 4 cases "
           "of W2-100's front-matter case pinning version 1.0.0, revised by the test designer (td-2, `26a1a98ce`, "
           "merged as `f8e7c0fad`); at the probed head `gov accept W2-100`: 222 passed, 8 failed, all 8 the "
           "`.claude/skills/` cases under success-6 and failure-6; the lead's final scoped run (lead_verify 3) runs "
           "beside you")
for slot, value in (("HEAD_TO_PROBE", "f8e7c0fad6c6"), ("LEAD_VERIFY_SUMMARY", summary), ("JUDGEMENT_MD_BODY", body)):
    assert slot in t, slot
    t = t.replace(slot, value)
p.write_text(t)
print("filled", len(t.splitlines()))
