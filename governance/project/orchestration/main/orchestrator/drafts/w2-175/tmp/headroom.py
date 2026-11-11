"""Read-only: prose size of each role template on w2/integrate against its budget (W2-128's measure)."""
import hashlib
import subprocess

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS"
BUDGET = {"role-cto": 6000, "role-lead": 8000}


def prose(text):
    kept, fenced = [], False
    for line in text.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if fenced or stripped.startswith("|"):
            continue
        kept.append(line)
    return "\n".join(kept)


for stem in ("role-cto", "role-engineer", "role-lead", "role-product-spec", "role-research", "role-reviewer", "role-test-designer"):
    blob = subprocess.run(["git", "-C", ROOT, "show", f"w2/integrate:template/governance/kernel/templates/{stem}.md"],
                          capture_output=True, check=True).stdout
    text = blob.decode()
    size = len(prose(text.split("---", 2)[2] if text.startswith("---") else text))
    budget = BUDGET.get(stem, 3500)
    print(f"{stem:20s} prose {size:5d} budget {budget:5d} headroom {budget - size:5d} sha256 {hashlib.sha256(blob).hexdigest()[:12]}")
