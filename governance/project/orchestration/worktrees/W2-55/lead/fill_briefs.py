from pathlib import Path

base = Path("/home/usain/gov-os-worktrees/W2-55/.gov-runtime/scratch/lead/briefs")
spec = (base / "interface-spec.md").read_text(encoding="utf-8").strip()
for name in ("td-1", "eng-1"):
    text = (base / f"{name}.md").read_text(encoding="utf-8")
    assert text.count("{{SPEC}}") == 1, name
    (base / f"{name}.filled.md").write_text(text.replace("{{SPEC}}", spec), encoding="utf-8")
    print(name, "filled")
