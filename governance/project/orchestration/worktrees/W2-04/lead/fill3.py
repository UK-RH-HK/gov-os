"""Repair round (DEC-1025): fill the td brief with all three spec parts; put the head into the engineer's brief."""
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent / "briefs"
spec = "\n\n".join((HERE / n).read_text(encoding="utf-8").strip() for n in ("spec.md", "spec-add-2.md", "spec-add-3.md"))
td = (HERE / "td-4.md").read_text(encoding="utf-8")
assert td.count("{{SPEC}}") == 1
(HERE / "td-4.filled.md").write_text(td.replace("{{SPEC}}", spec), encoding="utf-8")
head = subprocess.run(["git", "rev-parse", "--short=12", "HEAD"], capture_output=True, text=True, check=True,
                      cwd=HERE).stdout.strip()
eng = (HERE / "eng-6.md").read_text(encoding="utf-8")
assert eng.count("a5a53c60xxxx") == 2
(HERE / "eng-6.filled.md").write_text(eng.replace("a5a53c60xxxx", head), encoding="utf-8")
print("filled td-4 and eng-6; head", head)
