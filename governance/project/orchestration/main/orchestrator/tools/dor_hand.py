"""DEC-944 item 2, by hand until W2-82 lands: the six readiness conditions for each ticket id given. Prints READY or
NOT READY with each failing condition; exits 1 if any ticket is not ready. Run with PYTHONPATH=<main tree>/src."""
import re
import sys
from pathlib import Path

from gov.tasks.tickets import frontmatter

ROOT = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
REG = (ROOT / "docs/DECISION_REGISTER.md").read_text(encoding="utf-8")
ID = re.compile(r"\b(DEC|CAP|AR|MR|ADR)-[0-9A-Za-z.]+")


def resolves(src):
    if src.startswith("DEC-"):
        return "### " + src + " " in REG
    return bool(ID.fullmatch(src))  # Contract ids: form only here; W2-82 resolves them against the store


bad_any = False
for tid in sys.argv[1:]:
    fm = frontmatter(ROOT / ".tickets" / (tid + ".md")) or {}
    why = []
    srcs = [str(s) for s in fm.get("sources") or []]
    if not srcs or not all(resolves(s) for s in srcs):
        why.append("SOURCES_UNRESOLVED " + str([s for s in srcs if not resolves(s)] or "empty"))
    paths = fm.get("allowed_paths") or []
    if not paths or any(p.startswith(("/", "~")) or ".." in p or "$" in p for p in paths):
        why.append("PATHS_INVALID")
    k = fm.get("kpis") or {}
    if not k.get("success") or not k.get("failure") or not any(ID.search(str(l)) for l in k.get("success")):
        why.append("KPIS_INCOMPLETE")
    if fm.get("profile") not in ("LITE", "STANDARD", "FULL"):
        why.append("PROFILE_MISSING")
    at = fm.get("acceptance_tests") or {}
    if not (str(at.get("path", "")).startswith("tests/acceptance/") or at.get("evidence")):
        why.append("ACCEPTANCE_PATH_MISSING")
    for dep in list(fm.get("depends_on") or []) + list(fm.get("deps") or []):
        dfm = frontmatter(ROOT / ".tickets" / (str(dep) + ".md")) or {}
        if dfm.get("status") != "closed":
            why.append("DEPENDENCY_OPEN " + str(dep) + " (" + str(dfm.get("status")) + ")")
    print(tid, fm.get("wbs_id"), "READY" if not why else "NOT READY: " + "; ".join(why))
    bad_any = bad_any or bool(why)
sys.exit(1 if bad_any else 0)
