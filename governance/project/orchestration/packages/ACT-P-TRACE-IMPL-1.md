# ACT-P-TRACE-IMPL-1 — the owner's commit of 39 accepted-history entries (DEC-927)

**When:** only after the orchestrator has committed DEC-927 to the register on `w2/integrate`. The entries name DEC-927, and the close reads them only under that ACCEPTED owner decision. The orchestrator confirms in the chat that DEC-927 is committed and gives its sha.

**Where:** a plain terminal, not a Claude session, with no close queue running.

**Validated:** the pinned judge's readers (`tools/validate_entry.py`, DEC-895) passed all 39 entries against the register as it will stand. With the patch applied, `gov.close.traceability` exits 0 with no findings, and the record-reading suites pass.

```
cd /home/usain/Dynamic-Agentic-Engineering-OS
git status --short
git apply governance/project/orchestration/packages/ACT-P-TRACE-IMPL-1.patch
git diff --stat -- governance/project/path-map.yaml
git commit -m "Owner decision DEC-927: accepted history for the 39 commits whose Implements names a role (P-TRACE-IMPL-1 (a))" --trailer "Task: decision-record" --trailer "Implements: DEC-927" --trailer "Role: owner" -- governance/project/path-map.yaml
git log -1 --format='%h %s'
```

**What to see at each step:**
- `git status --short` prints nothing before the apply.
- `git diff --stat` shows `governance/project/path-map.yaml | 78 +` (39 entries of two lines).
- `git log -1` shows the new commit.

**Then** tell the orchestrator the commit's sha. It re-runs gate (b) and restarts the queue with W2-66.
