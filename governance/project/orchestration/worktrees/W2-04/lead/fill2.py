"""Round 2: put the run-1 specification and its addendum into each brief."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent / "briefs"
spec = (HERE / "spec.md").read_text(encoding="utf-8").strip()
add = (HERE / "spec-add-2.md").read_text(encoding="utf-8").strip()
both = spec + "\n\n" + add
for name in sys.argv[1:]:
    text = (HERE / f"{name}.md").read_text(encoding="utf-8")
    assert text.count("{{SPEC}}") == 1, name
    (HERE / f"{name}.filled.md").write_text(text.replace("{{SPEC}}", both), encoding="utf-8")
    print(name, "filled", len(text.replace("{{SPEC}}", both)))
