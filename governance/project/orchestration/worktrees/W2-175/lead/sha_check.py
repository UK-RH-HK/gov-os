import hashlib, sys
from pathlib import Path
root = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/usain/gov-os-worktrees/W2-175")
d = root / "template/governance/kernel/templates"
expect = {
    "role-cto.md": "1b1745571c51",
    "role-engineer.md": "7f18eebbe711",
    "role-lead.md": "827916852210",
    "role-product-spec.md": "66d556c0ff90",
    "role-research.md": "6f63e5b23b21",
    "role-reviewer.md": "bec50839cad9",
    "role-test-designer.md": "3a0bfd4abbee",
    "brief.md": "004ce0fc8f09",
}
bad = 0
for name, pre in expect.items():
    h = hashlib.sha256((d / name).read_bytes()).hexdigest()[:12]
    ok = h == pre
    bad += not ok
    print(f"{name} {h} expect {pre} {'OK' if ok else 'DIFFERS'}")
print("ALL-OK" if not bad else f"MISMATCH {bad}")
