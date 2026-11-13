# The prompt's §0 edit for DEC-1158 (the emergency lifted) — for the owner's operator

**File:** `governance/project/prompts/w2-orchestrator.md` (the owner's alone to change; prompt line 7). **One bullet in §0 replaced; nothing else.**
**Commit:** by the owner's operator, with `Role: owner`, `Decided-by: owner (chat, 2026-11-13)`, `Implements: DEC-1158, DEC-1157, DEC-1159`.

## Replace exactly this line (§0, line 52 at e93d846a8)

```
- **The emergency (DEC-1047, DEC-1049, DEC-1051, DEC-1052), until the owner lifts it:** only the plan's steps run (`governance/project/orchestration/packages/LIFT-1/P1-PLAN.md`, its DEC-1052 section first), with in-session agents of their role, scoped test runs through `tools/heavy_slot.sh`, record commits and the restarts on the list's class list. No lead, landing or queue run; nothing scheduled but the dispatcher, with its ready list empty; no nightly and no full suite until the owner's word (D-10); no `gov close`; no gitleaks scan (DEC-1045). Where each stopped item resumes: `.gov-runtime/scratch/orchestrator/log/emergency-stops-20261102.md`.
```

## With this line

```
- **The emergency of 2026-11-02 is lifted (DEC-1158, 2026-11-13):** DEC-1032's freeze, DEC-1033 (1) and (4), DEC-1047 (1) and (2), DEC-1049, DEC-1050 (5) and DEC-1051 are superseded; leads, landings, the queue, closes, the nightly (beside the leads, DEC-1159 (1)) and the full suite run as DECISIONS-IN-FORCE states. What still holds or delays work is only what protects the machine and the governance (DEC-1157 (14)): the memory floor, the 5 GB hold, `mem_guard` and the OOM trip; the guard's refusals; the spend brake; the brief checks; review rounds, the kernel gate and the owner's approval of kernel bytes; new tickets and splits to the owner; the idle check's record. The gitleaks scan stays off by configuration (DEC-1045) until the owner decides otherwise.
```

## Check after the edit

```
cd /home/usain/Dynamic-Agentic-Engineering-OS
grep -c "The emergency of 2026-11-02 is lifted (DEC-1158" governance/project/prompts/w2-orchestrator.md   # expect 1
grep -c "until the owner lifts it:\*\* only the plan's steps run" governance/project/prompts/w2-orchestrator.md   # expect 0
git diff --stat   # 1 file changed, 1 insertion(+), 1 deletion(-)
```

The CTO's follow-ons of DEC-1158 (4) (DECISIONS-IN-FORCE refreshed, START-NEXT-SESSION rewritten) are the CTO's commits, not part of this edit.
