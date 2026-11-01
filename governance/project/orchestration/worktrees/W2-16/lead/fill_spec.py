"""Put the round's specification into a brief in place of SPEC_PLACEHOLDER."""
import sys
from pathlib import Path

briefs = Path("/home/usain/gov-os-worktrees/W2-16/.gov-runtime/scratch/lead/briefs")
spec = (briefs / "spec-dec772.md").read_text(encoding="utf-8").strip()
for name in sys.argv[1:]:
    path = briefs / name
    text = path.read_text(encoding="utf-8")
    assert text.count("SPEC_PLACEHOLDER") == 1, name
    text = text.replace("SPEC_PLACEHOLDER", spec)
    text = text.replace(" TMPDIR=<your session's temp folder>", "")
    path.write_text(text, encoding="utf-8")
    print(name, "filled")
