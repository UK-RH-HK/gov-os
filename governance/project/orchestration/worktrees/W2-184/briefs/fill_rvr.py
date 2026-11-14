"""Fill the R1-R3 narrow-check auditor brief (W2-184 lead scratch)."""
from pathlib import Path
b = Path("/home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/briefs")
head = b.joinpath("rv-r.head.md").read_text()
judgement = Path("/home/usain/gov-os-worktrees/W2-184/governance/project/briefs/JUDGEMENT.md").read_text()
reps = {"HEADPROBE": "90e657a3583bf4e8edfd40e69a0591e981097dfa",
        "BASEPROBE": "bbe1510f899b4599222a1cfc6939bf13b5350222",
        "ENGCOMMITS": "f2f76a154 (`src/gov/launch/command.py`, `src/gov/launch/launcher.py`, `src/gov/launch/record.py`, `docs/changes/W2-184-CIT-E.md` section 9, `tests/unit/launch/test_w2_184_r_engineer.py`) and 90e657a35 (two earlier builder unit cases of P-td5-2 in `tests/unit/launch/test_w2_184_launch.py` revised to 10.3); `git show` each",
        "VERIFYLINE": "the full verification at 90e657a35 GREEN (8,118 tests, 0 failed, 29 skipped)",
        "ACCEPTCOUNT": "507/507, outcome pass, at 90e657a35",
        "UNITCOUNT": "with `test_w2_184_r_engineer.py` and `test_w2_184_launch.py`: 218 passed at 90e657a35",
        "JUDGEMENTTEXT": judgement.rstrip("\n")}
for k, v in reps.items():
    assert k in head, k
    head = head.replace(k, v)
text = head + b.joinpath("INTERFACE.md").read_text() + "\n" + b.joinpath("INTERFACE-R.md").read_text()
for k in reps:
    assert k not in text, k
b.joinpath("rv-r.md").write_text(text)
print("ok", len(text))
