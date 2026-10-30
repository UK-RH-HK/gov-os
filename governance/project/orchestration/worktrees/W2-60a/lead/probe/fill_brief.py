"""Fill the test designer's brief with the CIT-E's behaviour sections (A) and the test classification (C)."""
from pathlib import Path

ROOT = Path("/home/usain/gov-os-worktrees/W2-60a")
note = (ROOT / "docs/changes/W2-60a-CIT-E.md").read_text(encoding="utf-8").splitlines()
start = note.index("## A. Behaviour")
end = note.index("## B. The split with W2-56 in `launcher.py` (DEC-786; W2-56's \"Beside W2-60a\")")
c_start = note.index("## C. The existing tests the change touches")
d_start = note.index("## D. What W2-11 must write (for the orchestrator to carry)")
behaviour = "\n".join(line.replace("## A. Behaviour", "### The design's behaviour sections, word for word")
                      .replace("### Behaviour", "#### Behaviour") for line in note[start:end]).rstrip()
earlier = "\n".join(line.replace("## C. The existing tests", "#### The design's classification of the existing tests")
                    for line in note[c_start:d_start]).rstrip()
brief_path = ROOT / ".gov-runtime/scratch/lead/briefs/b2-test-designer.md"
brief = brief_path.read_text(encoding="utf-8")
extra = (ROOT / ".gov-runtime/scratch/lead/briefs/b2-extra.md").read_text(encoding="utf-8").rstrip()
brief = brief.replace("@@BEHAVIOUR@@", behaviour + "\n\n" + extra)
brief = brief.replace("@@EARLIER@@", "The design classifies them as follows (its own counts; check them):\n\n"
                      + earlier + "\n\n")
brief_path.write_text(brief, encoding="utf-8")
print("filled", len(brief.splitlines()), "lines")
