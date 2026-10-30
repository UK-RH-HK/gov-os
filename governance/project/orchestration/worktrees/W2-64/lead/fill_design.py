"""Put the design note's text into a brief in place of the <<<DESIGN>>> mark (lead's scratch)."""
import sys
from pathlib import Path

brief, design = Path(sys.argv[1]), Path(sys.argv[2])
text = brief.read_text(encoding="utf-8")
note = design.read_text(encoding="utf-8").strip()
assert text.count("<<<DESIGN>>>") == 1, "the mark must appear once"
brief.write_text(text.replace("<<<DESIGN>>>", note), encoding="utf-8")
print("filled", brief)
