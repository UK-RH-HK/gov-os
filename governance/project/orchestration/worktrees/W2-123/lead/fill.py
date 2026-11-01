"""Fill {{INTERFACE_SPEC}} in a brief: fill.py <brief.md> <spec.md> <out.md>."""
import sys
from pathlib import Path

brief, spec, out = (Path(p) for p in sys.argv[1:4])
text = brief.read_text()
assert "{{INTERFACE_SPEC}}" in text
Path(out).write_text(text.replace("{{INTERFACE_SPEC}}", spec.read_text().strip()))
print(f"wrote {out}")
