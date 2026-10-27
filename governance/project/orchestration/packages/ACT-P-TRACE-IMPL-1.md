# ACT-P-TRACE-IMPL-1 — the owner's commit of 39 accepted-history entries (DEC-927)

**When:** only after the orchestrator has committed DEC-927 to the register on `w2/integrate`. The entries name DEC-927, and the close reads them only under that ACCEPTED owner decision. The orchestrator confirms in the chat that DEC-927 is committed and gives its sha.

**Where:** a plain terminal, not a Claude session, with no close queue running.

**The entries are corrections (owner, DEC-927 condition 1):** each holds `commit`, `decision: DEC-927` and `should_implement`, the decision ids the commit should have named, taken from its Task ticket's sources.

**Re-validated (2026-10-27), with the patch and DEC-927 applied to the tree, then restored:**
- the pinned judge's readers (`tools/validate_entry.py`, DEC-895): all 39 entries pass, 0 failed;
- `gov.close.traceability` (pinned): exit 0, no findings;
- `record_checks.sh`: core-pathmap, core-schema, core-mutation, core-authority, core-graph and context-reproducibility all exit 0, and the record-reading suites pass, 132;
- gate (e) (`tools/trailer_gate.py`, now checking `Implements:`): 0 lacking and 0 unresolved for W2-70, W2-67, W2-66, W2-65, W2-07 and W2-69.

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
- `git diff --stat` shows `governance/project/path-map.yaml | 117 +` (39 entries of three lines).
- `git log -1` shows the new commit.

**Then** tell the orchestrator the commit's sha. It re-runs gate (b) and restarts the queue with W2-66.
