"""Fill the round-2 auditor brief: head, accept count, JUDGEMENT.md word for word, the interface (W2-184 lead scratch)."""
from pathlib import Path

b = Path("/home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/briefs")
head = b.joinpath("rv-2.head.md").read_text()
judgement = Path("/home/usain/gov-os-worktrees/W2-184/governance/project/briefs/JUDGEMENT.md").read_text()
probe_head = "89edff41ff0f7ae6734ba31af69b0a11b57394bf"
text = (head.replace("HEADPROBE", probe_head).replace("ACCEPTCOUNT", "451/451")
        .replace("JUDGEMENTTEXT", judgement.rstrip("\n")) + b.joinpath("INTERFACE.md").read_text())
for slot in ("HEADPROBE", "ACCEPTCOUNT", "JUDGEMENTTEXT"):
    assert slot not in text, slot
b.joinpath("rv-2.md").write_text(text)
print("ok", len(text), probe_head in text, "round 2" in text)
