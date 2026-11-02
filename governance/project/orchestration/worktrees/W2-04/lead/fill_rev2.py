"""Fill review 2's brief: head, the specification with both addenda, the lead's results, JUDGEMENT.md word for word."""
import subprocess
from pathlib import Path

TREE = Path("/home/usain/gov-os-worktrees/W2-04")
HERE = TREE / ".gov-runtime/scratch/lead/briefs"
head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True, cwd=TREE).stdout.strip()
spec = "\n\n".join((HERE / n).read_text(encoding="utf-8").strip() for n in ("spec.md", "spec-add-2.md", "spec-add-3.md"))
res = (HERE / "rev-2.results.part").read_text(encoding="utf-8").strip()
judge = (TREE / "governance/project/briefs/JUDGEMENT.md").read_text(encoding="utf-8").strip()
text = (HERE / "rev-2.md").read_text(encoding="utf-8")
for key in ("{{SPEC}}", "{{RESULTS}}", "{{JUDGEMENT}}"):
    assert text.count(key) == 1, key
text = text.replace("{{HEAD}}", head[:12] + " (its full id: `git rev-parse HEAD`)").replace("{{HEAD12}}", head[:12])
text = text.replace("{{SPEC}}", spec).replace("{{RESULTS}}", res).replace("{{JUDGEMENT}}", judge)
assert "{{" not in text
(HERE / "rev-2.filled.md").write_text(text, encoding="utf-8")
print("filled", head[:12], len(text))
