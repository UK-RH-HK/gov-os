# W2-181 (DAEO-ywb5): the narrow check of W2-157's F4 revision (DEC-1156 (6), (7); DEC-1154), pass

Probed head `499543a836d3` of `w2/W2-181`; a fresh read-only independent auditor, Opus high, class C1, session `f5c5004e-0bd8-4c8f-927d-dd9377b04881`, 2026-11-12, through `gov launch`; commissioned and judged by the CTO. Kept here because W2-181's allowed paths hold no probe folder (its F2 forbids any other path); a LITE land needs no review record.

task: DAEO-ywb5 (W2-181)
decisions: [DEC-1156, DEC-1154, DEC-866, DEC-801, DEC-808, DEC-1010, DEC-1014, DEC-953]
role: independent-auditor (narrow check, read-only); head 499543a836d3, branch w2/W2-181

# W2-181: narrow check of the revision to W2-157's F4 case

Sandbox check: (a) refused as it should be (EROFS); (b) `git hash-object -w` and `git update-index --refresh` worked. No model servers ran.

## What I probed and found sound
1. **Scope.** The diff from the merge-base with `w2/integrate` to HEAD lists only `tests/acceptance/W2-157/{README.md,test_w2_157_nothing_else.py}`. Nothing changed in `src/`. Commit 120474643 carries `Role: independent-test-designer` and `Rewrite-Reason:`.
2. **The judgement.**
   - It judges only `refs/heads/w2/W2-157`, reading the branch from the repository it is given.
   - It skips with its reason on another branch, on a detached HEAD, on `w2/integrate` itself, and where `w2/integrate` or the ticket file is absent. The checks for the missing reference and ticket file match W2-180's F5.
   - My planted probes:
     - On `w2/W2-157`, a change to another ticket's tests fails, and so does an edit to its own ticket file.
     - On `w2/W2-157`, inside-only changes with `w2/integrate` merged in pass. The same branch plus an outside change after that merge fails.
     - `w2/W2-157-tests` skips naming the branch, and a detached HEAD skips.
     - The real `w2/W2-157` head (30e969875) passes.
   - S5 is unchanged.
3. **Runs.**
   - On the head, through `heavy_slot.sh`: 121 passed, 1 skipped (F4: "this is the branch w2/W2-181").
   - On the candidate merge (`--no-ff`) onto `w2/integrate` 7d8c2d524, on a detached HEAD in a clone: F4 skips with "this is a detached HEAD", and the six planted cases pass.

## Findings
**F1: on W2-157's own branch, a missing ticket file makes F4 skip instead of fail.**
- What was done: on `w2/W2-157`, the engineer's branch deletes `.tickets/DAEO-ozyt.md` and also changes a path outside the ticket's paths (planted probe P6).
- What happened: F4 is skipped with "needs the ticket file". The outside change goes unjudged.
- What should have happened: on its own branch, F4 should fail, naming the deleted ticket file as an outside change.
- Ordinary work: no, because the engineer would have to delete its own ticket file, and the guard refuses an engineer's writes to `.tickets/`. The skip on an absent ticket file is the form W2-180 used and the brief asks for (a plain clone).
- Consequence: fails open
- scope: in. It is a recorded row for the Wave 3 hardening pass, not a round (DEC-801, DEC-1010).
- What would reverse it: evidence that an engineer session can delete or rename its ticket file in ordinary work without the guard refusing it, and that the close does not catch the deletion some other way.

Classification: 1 finding: in scope, ordinary work no, fails open → a row. No round.
Recommendation: land W2-181.

```verdict
{"kpis": [{"kpi": "w2-181-fix-check", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}]}
```
