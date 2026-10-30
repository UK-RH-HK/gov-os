"""The rules in force (owner, standing, DEC-952 item 5): generated from the register, only ACCEPTED, standing,
non-superseded decisions, grouped by topic, one line each with its id; at most about 8,000 characters. Regenerated
with every register commit. Writes governance/project/orchestration/RULES-IN-FORCE.md and prints its size.
A decision counts as standing when its status or title says "standing"; superseded when its status says so."""
import pathlib
import re
import sys

ROOT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
OUT = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "governance/project/orchestration/RULES-IN-FORCE.md")
LIMIT = 8000
TOPICS = [
    ("Priorities and plan", r"priorit|re-plan|EXAMIN|minimum|parking|cut|target|keystone"),
    ("Leads, the gate and capacity", r"lead|gate|capacity|memory gate|floor|parallel|launch|slot"),
    ("Closes, verification and the nightly", r"close|verif|nightly|scoped|suite|lock|re-pin|test"),
    ("The owner's contact and reports", r"package|ping|report|morning|digest|status block|daytime|decisions reach"),
    ("Records, rules and drift", r"record|register|rule|drift|brief|gap|handover|session"),
]
text = (ROOT / "docs/DECISION_REGISTER.md").read_text(encoding="utf-8")
rows = []
for entry in re.split(r"\n(?=### DEC-\d+ )", text):
    m = re.match(r"### (DEC-\d+) — (.*)", entry)
    if not m:
        continue
    status = re.search(r"- \*\*Status:\*\* ([^\n]*)", entry)
    status = status.group(1) if status else ""
    title = m.group(2).strip()
    if not status.startswith("ACCEPTED") or "standing" not in (status + title).lower():
        continue
    if "superseded by" in status.lower() or status.startswith("SUPERSEDED"):
        continue
    short = re.sub(r"\s*\((standing|owner)[^)]*\)\s*$", "", title)
    short = short if len(short) <= 150 else short[:147].rsplit(" ", 1)[0] + "…"
    rows.append((m.group(1), short))
groups = {name: [] for name, _ in TOPICS}
groups["Other"] = []
for did, short in rows:
    for name, pat in TOPICS:
        if re.search(pat, short, re.I):
            groups[name].append((did, short))
            break
    else:
        groups["Other"].append((did, short))
lines = ["# Rules in force", "",
         "Generated from `docs/DECISION_REGISTER.md` by the orchestrator's `tools/rules_digest.py`: only ACCEPTED, "
         "standing, non-superseded decisions, one line each. The register is the authority; read the entry for the "
         "full rule. Regenerated with every register commit (DEC-952).", ""]
for name, items in groups.items():
    if not items:
        continue
    lines += ["## " + name, ""] + ["- **%s** %s" % (d, s) for d, s in sorted(items, key=lambda x: int(x[0][4:]))] + [""]
out = "\n".join(lines)
if len(out) > LIMIT:
    print("over the limit: %d characters" % len(out))
OUT.write_text(out, encoding="utf-8")
print("%s: %d rules, %d characters" % (OUT.relative_to(ROOT), len(rows), len(out)))
sys.exit(0)
