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

import yaml  # noqa: E402

register_text = (ROOT / "docs/DECISION_REGISTER.md").read_text()
held = set(re.findall(r"^### (DEC-\d+) ", register_text, flags=re.M))


def should_implement(task: str) -> list[str]:
    """The decision ids the commit should have named (owner, DEC-927 condition 1): its Task ticket's sources that
    the register holds, in the ticket's order."""
    text = (ROOT / ".tickets" / f"{task}.md").read_text()
    front = yaml.safe_load(text.split("---")[1]) or {}
    return [s for s in (front.get("sources") or []) if isinstance(s, str) and s in held]


should = {task: should_implement(task) for task in {r[1] for r in rows}}
assert all(should.values()), f"a ticket has no source the register holds: {should}"
path_map = (ROOT / "governance/project/path-map.yaml").read_text()
anchor = '  - commit: "611955faffaa3aad8e3b4da8579d114e79c922b3"\n    decision: DEC-924\n'
assert anchor in path_map, "the path map's last accepted_history entry moved"
entries = "".join(f'  - commit: "{sha}"\n    decision: DEC-927\n    should_implement: [{", ".join(should[task])}]\n'
                  for sha, task, *_ in rows)
(OUT / "path-map.yaml").write_text(path_map.replace(anchor, anchor + entries))

lines = []
for sha, task, impl, role, record_only, paths in rows:
    kind = "record-only" if record_only else "code, tests or notes"
    shown = ", ".join(f"`{p}`" for p in paths[:6]) + (f" and {len(paths) - 6} more" if len(paths) > 6 else "")
    lines.append(f"       - `{sha}` ({task}, Role: {role}, `Implements: {impl}`; should have named "
                 f"{', '.join(should[task])}; {kind}): {shown}")
n_rec = sum(1 for r in rows if r[4])
listing = "\n".join(lines)
entry = f"""
### DEC-927 — P-TRACE-IMPL-1 (a) with two conditions: the {len(rows)} commits whose `Implements:` names a role are accepted as history as corrections, by the owner's own commit; a wrong `Implements:` is caught within the ticket (standing)
- **Status:** ACCEPTED (owner, 2026-10-27, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-27)`; item 2 standing) · **Under:** DEC-734, DEC-891, DEC-895, DEC-862 (a), DEC-925 item 2, DEC-851, DEC-861 · **Basis:** package P-TRACE-IMPL-1 (`governance/project/orchestration/packages/P-TRACE-IMPL-1.md`). After W2-70's close (2026-10-27, exit 0), gate (b) went red on product traceability: a closed ticket's commits must name ids the store resolves, and seven of W2-70's carry `Implements: independent-test-designer`. The lead briefs' `IMPL` slot had been filled with a role, so leads and their workers wrote a role there in {len(rows)} commits of six tickets on `w2/integrate` (and two on W2-57's branch).
- **Decision:**
  1. **(a), one `Role: owner` commit of all {len(rows)} entries, each a correction, not a bare exemption.** Each entry in the path map's `accepted_history` is `{{commit: <full id>, decision: DEC-927, should_implement: [<ids>]}}`. `should_implement` holds the decision ids the commit should have named in `Implements:`, taken from its Task ticket's `sources` that the register holds.
     - {n_rec} of the commits change only records, and {len(rows) - n_rec} change code, tests or notes (DEC-891).
     - The entries are validated with the pinned judge's readers and the record suites, and the ACT file is updated (DEC-895, DEC-925 item 2).
     - The commits, each with its correction and its changed paths (`git show --name-only`):
{listing}
     - W2-57's two lead commits (`Implements: engineer`) are handled the same way when W2-57 is ready to close.
  2. **Caught at the source (owner, standing; the rule about rules, DEC-851).**
     - **Each lead** checks its own commits' trailers before it returns: every `Implements:` item must be a decision id that the register holds.
     - **Gate (e)** (`tools/trailer_gate.py`) checks the same, so a wrong `Implements:` is caught within the ticket, not at close time. A lead runs it on its own worktree: `trailer_gate.py <ticket id> <worktree>`.
     - **The orchestrator's reading, for the owner to overturn:** a Contract id that the record store holds (`CAP-n`) is also accepted, as the judge resolves it. W2-59's four commits name `CAP-33`. A role, a row or any other word is refused.
     - **`tools/build_lead_brief.py`** refuses an `IMPL` that is not a decision or Contract id.
- **Where it goes (DEC-851):**
  - this register;
  - the path map (the owner's commit);
  - the prompt §15 (gate (e)), v3.30;
  - `LEAD-w2-common.md` (the check before a return);
  - `tools/trailer_gate.py` and `tools/build_lead_brief.py`;
  - RESUME HERE;
  - the daily digest.
- Next free id: DEC-928.

| Version | Date | Change |
|---|---|---|
| 0.313 | 2026-10-27 | Owner (recorded by the orchestrator, DEC-861): DEC-927 (P-TRACE-IMPL-1 (a): {len(rows)} commits whose Implements names a role accepted as history by the owner's commit, each entry a correction naming the decision ids it should have implemented; standing: each lead checks its commits' Implements before it returns and gate (e) checks the same; briefs fill Implements with ids only). Next free id: DEC-928. |
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
