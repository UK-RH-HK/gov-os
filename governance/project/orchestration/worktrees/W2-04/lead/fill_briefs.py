"""Put the shared specification into each brief: briefs/<name>.md -> briefs/<name>.filled.md."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent / "briefs"
spec = (HERE / "spec.md").read_text(encoding="utf-8").strip()
for name in sys.argv[1:]:
    text = (HERE / f"{name}.md").read_text(encoding="utf-8")
    assert text.count("{{SPEC}}") == 1, name
    (HERE / f"{name}.filled.md").write_text(text.replace("{{SPEC}}", spec), encoding="utf-8")
    print(name, "filled", len(text.replace("{{SPEC}}", spec)))
