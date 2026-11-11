"""Lead's check of the delta: stop sentence byte-equal to brief.md, sha256 vs CIT-P, prose sizes at BASE and HEAD."""
import hashlib, subprocess, sys, re
from pathlib import Path
TREE = Path("/home/usain/gov-os-worktrees/W2-175")
BASE = "7709021ad6cc"
sys.path.insert(0, str(TREE / "tests/acceptance/W2-128"))
import w2_128_support as S  # noqa: E402

T = TREE / "template/governance/kernel/templates"
names = ["role-cto", "role-engineer", "role-lead", "role-product-spec", "role-research", "role-reviewer", "role-test-designer"]
brief = (T / "brief.md").read_text(encoding="utf-8")
stop_lines = [l for l in brief.splitlines() if l.startswith("Refused twice")]
stop = stop_lines[0].strip()
print("brief stop:", repr(stop))
cit = (TREE / "docs/changes/W2-175-CIT-P.md").read_text(encoding="utf-8")
for n in names:
    p = T / f"{n}.md"
    head = p.read_text(encoding="utf-8")
    base = subprocess.run(["git", "-C", str(TREE), "show", f"{BASE}:{p.relative_to(TREE)}"], capture_output=True, text=True, check=True).stdout
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    hb = hashlib.sha256(base.encode("utf-8")).hexdigest()
    pb = len(S.prose(S.split(base)[1]))
    ph = len(S.prose(S.split(head)[1]))
    budget = S.BUDGET.get(n)
    print(f"{n}: stop_in={stop in head} count={head.count(stop)} new_sha_in_cit={h in cit} base_sha_in_cit={hb in cit} "
          f"prose {pb}->{ph} of {budget} base12={hb[:12]} new12={h[:12]}")
