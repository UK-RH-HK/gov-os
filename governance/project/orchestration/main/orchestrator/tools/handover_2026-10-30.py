"""The handover of 2026-10-30: the checkpoint's RESUME HERE heading line (line 3, grown to thousands of characters) is
replaced by the compact handover in drafts/RESUME-2026-10-30.md; the old line is appended to CHECKPOINT-ARCHIVE.md."""
import pathlib

O = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
cp = O / "CHECKPOINT.md"
lines = cp.read_text(encoding="utf-8").split("\n")
assert lines[2].startswith("## RESUME HERE"), lines[2][:40]
old = lines[2]
new = (O / "drafts/RESUME-2026-10-30.md").read_text(encoding="utf-8").rstrip("\n").split("\n")
lines[2:3] = new
cp.write_text("\n".join(lines), encoding="utf-8")
with open(O / "CHECKPOINT-ARCHIVE.md", "a", encoding="utf-8") as f:
    f.write("\n\n## Archived RESUME HERE line (replaced 2026-10-30 13:15)\n\n" + old + "\n")
print("handover written; old line archived (%d characters)" % len(old))
