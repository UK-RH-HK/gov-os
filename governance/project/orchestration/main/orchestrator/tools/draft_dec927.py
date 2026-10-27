"""Draft DEC-927 (P-TRACE-IMPL-1): accepted-history entries for the commits on w2/integrate whose `Implements:` names a
role, not an id. Writes, under drafts/DEC-927/: the path map with the entries, the register with the entry, the patch,
and the list. Applies nothing to the tree."""
import re
import subprocess
from pathlib import Path

ROOT = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
OUT = ROOT / ".gov-runtime/scratch/orchestrator/drafts/DEC-927"
OUT.mkdir(parents=True, exist_ok=True)
RECORDS = (".tickets/", "docs/checkpoints/", "docs/close/", "docs/probes/", "docs/DECISION_REGISTER.md", "docs/plan/",
           "governance/project/orchestration/")
ID = re.compile(r"(DEC|CAP|AR|MR|ADR|W\d+-[A-Z]*\d+|F-|P-)")


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout


fmt = "%H|%(trailers:key=Task,valueonly,separator=%x2C)|%(trailers:key=Implements,valueonly,separator=%x2C)|%(trailers:key=Role,valueonly,separator=%x2C)"
rows = []
for line in git("log", "w2/integrate", "--since=2026-10-01", f"--format={fmt}").splitlines():
    sha, task, impl, role = (line.split("|") + ["", "", ""])[:4]
    if impl and not ID.search(impl):
        paths = git("show", "--name-only", "--format=", sha).split()
        record_only = all(p.startswith(RECORDS) for p in paths)
        rows.append((sha, task, impl, role, record_only, paths))
rows.sort(key=lambda r: (r[1], not r[4], r[0]))

path_map = (ROOT / "governance/project/path-map.yaml").read_text()
anchor = '  - commit: "611955faffaa3aad8e3b4da8579d114e79c922b3"\n    decision: DEC-924\n'
assert anchor in path_map, "the path map's last accepted_history entry moved"
entries = "".join(f'  - commit: "{sha}"\n    decision: DEC-927\n' for sha, *_ in rows)
(OUT / "path-map.yaml").write_text(path_map.replace(anchor, anchor + entries))

lines = []
for sha, task, impl, role, record_only, paths in rows:
    kind = "record-only" if record_only else "code, tests or notes"
    shown = ", ".join(f"`{p}`" for p in paths[:6]) + (f" and {len(paths) - 6} more" if len(paths) > 6 else "")
    lines.append(f"       - `{sha}` ({task}, Role: {role}, `Implements: {impl}`; {kind}): {shown}")
n_rec = sum(1 for r in rows if r[4])
listing = "\n".join(lines)
entry = f"""
### DEC-927 — P-TRACE-IMPL-1: the {len(rows)} commits whose `Implements:` names a role are accepted as history, by the owner's own commit; briefs fill `Implements:` with ids only
- **Status:** ACCEPTED (owner, 2026-10-27, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-27)`) · **Under:** DEC-734, DEC-891, DEC-895, DEC-862 (a), DEC-925 item 2, DEC-861 · **Basis:** package P-TRACE-IMPL-1 (`governance/project/orchestration/packages/P-TRACE-IMPL-1.md`). After W2-70's close (2026-10-27, exit 0), gate (b) went red on product traceability: closed tickets' commits must name ids the store resolves, and seven of W2-70's carry `Implements: independent-test-designer`. The lead briefs' `IMPL` slot had been filled with a role, so leads and their workers wrote a role there in {len(rows)} commits of seven tickets.
- **Decision:**
  1. **These {len(rows)} commits are accepted as history,** each `{{commit: <full id>, decision: DEC-927}}` in the path map's `accepted_history`, by the owner's own `Role: owner` commit ({n_rec} change only records, {len(rows) - n_rec} change code, tests or notes; DEC-891). Validated with the pinned judge's readers before the ACT (DEC-895). The commits, with their changed paths (`git show --name-only`):
{listing}
  2. **Briefs fill `Implements:` with ids only:** `tools/build_lead_brief.py` refuses an `IMPL` that is not a decision or Contract id. W2-57's two lead commits with `Implements: engineer` are listed by a further entry when W2-57 merges.
- **Where it goes:** this register; the path map (the owner's commit); `tools/build_lead_brief.py`; RESUME HERE; the daily digest.
- Next free id: DEC-928.

| Version | Date | Change |
|---|---|---|
| 0.313 | 2026-10-27 | Owner (recorded by the orchestrator, DEC-861): DEC-927 (P-TRACE-IMPL-1: {len(rows)} commits whose Implements names a role accepted as history by the owner's commit; briefs fill Implements with ids only). Next free id: DEC-928. |
"""
register = (ROOT / "docs/DECISION_REGISTER.md").read_text()
(OUT / "DECISION_REGISTER.md").write_text(register.rstrip("\n") + "\n" + entry)
(OUT / "entry.md").write_text(entry)
patch = subprocess.run(["diff", "-u", "--label", "a/governance/project/path-map.yaml", "--label",
                        "b/governance/project/path-map.yaml", str(ROOT / "governance/project/path-map.yaml"),
                        str(OUT / "path-map.yaml")], capture_output=True, text=True).stdout
(OUT / "accepted-history-implements.patch").write_text(patch)
print(f"{len(rows)} commits: {n_rec} record-only, {len(rows) - n_rec} other; tickets: "
      + ", ".join(sorted({r[1] for r in rows})))
