"""Build the round-2 auditor brief head from round 1's (W2-184 lead scratch)."""
from pathlib import Path

b = Path("/home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/briefs")
t = b.joinpath("rv-1.head.md").read_text()
reps = [
    ("# Brief: independent auditor, W2-184 (DAEO-6f0s), FULL review round 1\n\n"
     "You are a fresh, read-only independent auditor (Opus, effort high).",
     "# Brief: independent auditor, W2-184 (DAEO-6f0s), FULL review round 2 (the probe; the last round, DEC-1010)\n\n"
     "You are a fresh, read-only independent auditor (Opus, effort max: a FULL ticket's second review is the probe, "
     "and the\nticket is promoted by round 1's fail-open finding)."),
    ("`git -C /home/usain/gov-os-worktrees/W2-184 diff 1fd0066e1 HEADPROBE` (1fd0066e1 is the\n  integration tip merged in;",
     "`git -C /home/usain/gov-os-worktrees/W2-184 diff 06801fb31 HEADPROBE` (06801fb31 is the\n  integration tip last merged in;"),
    ("(the independent test designer's 413 cases)", "(the independent test designer's 451 cases)"),
    ("`gov accept W2-184` 413/413", "`gov accept W2-184` ACCEPTCOUNT"),
    ("# Probe of DAEO-6f0s (W2-184), round 1: judgement pass|fail",
     "# Probe of DAEO-6f0s (W2-184), round 2: judgement pass|fail"),
]
for old, new in reps:
    assert old in t, old[:70]
    t = t.replace(old, new)
extra = b.joinpath("rv-2.extra.md").read_text()
marker = "## Known, and judged by the lead"
assert marker in t
t = t.replace(marker, extra.rstrip("\n") + "\n\n" + marker)
b.joinpath("rv-2.head.md").write_text(t)
print("ok", len(t))
