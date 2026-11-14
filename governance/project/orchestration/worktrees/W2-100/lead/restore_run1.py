"""Put run 1's record entries back, ahead of any later ones, so each skill's record holds every real run (W2-100)."""
from pathlib import Path

base = Path("/home/usain/gov-os-worktrees/W2-100")
run1 = base / ".gov-runtime/scratch/lead/skilleval/run1-records"
for skill in ("backend", "api", "data", "security"):
    old = (run1 / f"{skill}.yaml").read_text(encoding="utf-8")
    assert old.startswith("records:\n"), skill
    target = base / "template/governance/kernel/skills" / skill / "scenario-records.yaml"
    if target.exists():
        new = target.read_text(encoding="utf-8")
        assert new.startswith("records:\n"), skill
        text = old + new[len("records:\n"):]
    else:
        text = old
    target.write_text(text, encoding="utf-8")
    print(skill, text.count("\n- skill:"), "entries")
