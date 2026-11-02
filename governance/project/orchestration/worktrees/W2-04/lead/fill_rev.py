"""Fill the reviewer brief: head, short head, the specification with its addendum, the lead's results."""
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent / "briefs"
head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
spec = (HERE / "spec.md").read_text(encoding="utf-8").strip()
add = (HERE / "spec-add-2.md").read_text(encoding="utf-8").strip()
res = (HERE / "rev-1.results.part").read_text(encoding="utf-8").strip()
text = (HERE / "rev-1.md").read_text(encoding="utf-8")
for key in ("{{SPEC}}", "{{RESULTS}}"):
    assert text.count(key) == 1, key
text = text.replace("{{HEAD}}", head[:12] + " (its full id: `git rev-parse HEAD`)").replace("{{HEAD12}}", head[:12])
text = text.replace("{{SPEC}}", spec + "\n\n" + add).replace("{{RESULTS}}", res)
assert "{{" not in text
(HERE / "rev-1.filled.md").write_text(text, encoding="utf-8")
print("filled", head[:12], len(text))
