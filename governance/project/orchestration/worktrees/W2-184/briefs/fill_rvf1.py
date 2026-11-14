"""Fill the narrow-check auditor brief (W2-184 lead scratch)."""
from pathlib import Path
b = Path("/home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/briefs")
head = b.joinpath("rv-f1.head.md").read_text()
judgement = Path("/home/usain/gov-os-worktrees/W2-184/governance/project/briefs/JUDGEMENT.md").read_text()
reps = {"HEADPROBE": "fb2ea8460857c9410e4dcaf63353e07ec75a606f",
        "ENGCOMMITS": "The engineer's commit fb2ea8460 (`git show`; `src/gov/launch/command.py`, `tests/unit/launch/test_w2_184_command.py`, `docs/changes/W2-184-CIT-E.md` section 8)",
        "VERIFYLINE": "GREEN (8,037 tests, 0 failed, 29 skipped)",
        "ACCEPTCOUNT": "507/507 at fb2ea8460",
        "JUDGEMENTTEXT": judgement.rstrip("\n")}
for k, v in reps.items():
    assert k in head, k
    head = head.replace(k, v)
text = head + b.joinpath("INTERFACE.md").read_text()
for k in reps:
    assert k not in text, k
b.joinpath("rv-f1.md").write_text(text)
print("ok", len(text))
