"""Write the bootstrap note of the adoption from the saved check output and git: adoption-note.md in scratch."""
import json
import subprocess

S = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/"
ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS"
checks = json.load(open(S + "log/check-after-ctx-data.json"))["error"]["details"]["checks"]
found = next(c for c in checks if c["id"] == "product-traceability-trailers")["findings"]
rows = []
for f in found:
    words = f["message"].split()
    commit, ticket = words[1], words[3]
    subject = subprocess.run(["git", "-C", ROOT, "show", "-s", "--format=%ad %s", "--date=short", commit],
                             capture_output=True, text=True, check=True).stdout.strip()
    rows.append(f"| `{commit}` | `{ticket}` | {subject.replace('|', '/')} |")
stages = subprocess.run(["git", "-C", ROOT, "log", "--reverse", "--format=| `%h` | %s |", "8b23e345..1c33dd28"],
                        capture_output=True, text=True, check=True).stdout.strip()
text = f"""
## This repository adopted (2026-10-11; for the exit auditor; DEC-615, DEC-617, DEC-624, DEC-625)

`gov adopt --lite` ran its eight stages on `w1/integrate`. The path map moves nothing; the 116 tracked files of the old `cli/` tree were deleted from the active tree in one batch, after a fresh independent auditor's verdict (`docs/audit/wave-1/adoption-path-map-verdict.md`, pass). They stay in history, at the backup ref `refs/gov/adoption/backup/8b23e345a02b` and at the rollback ref `refs/gov/adoption/rollback/batch-1`. Stage A8 retired nothing; the adapter generation that follows it is the owner's step (DEC-616).

**The adoption's commits.** The stage commits are the tool's own and carry no trailers; the verdict's commit carries `Task:` and the auditor's role alone, as stage A5 demands.

| Commit | Subject |
|---|---|
{stages}

**The trailers base is now `1c33dd28`** (the adoption's last commit; before: `429815b5`). The check `product-traceability-trailers` reported these {len(rows)} commits without `Implements:` at the last run before the move (`gov check` on the real store at `4e636645`); every one was named at its ticket's close:

| Commit | Ticket | Date and subject |
|---|---|---|
{chr(10).join(rows)}

**The auditor's findings, on the Wave 2 list:** a unit case that skips for good now that its origin is gone (`tests/unit/retrieval/test_lexical.py`); documents that point to `cli/` as present (`README.md`, `docs/SOURCES.md`, ADR-0002, one line of the work breakdown); the `carried-code` namespace's `cli/**` pattern and retention text; dead entries in the gitleaks configuration, the doctor's list of historical paths and one closed ticket. The kernel has no record type for an audit report (the verdict is typed `research`).
"""
open(S + "adoption-note.md", "w", encoding="utf-8").write(text)
print(len(rows), "rows;", len(text), "chars")
