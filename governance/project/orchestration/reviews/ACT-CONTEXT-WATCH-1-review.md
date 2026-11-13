# Review: ACT-CONTEXT-WATCH-1 (manifest sha256 `487c93c13e1b6ee2f223c5386fbb5cc38101737be200e94e4583aeb52350e58f`)

task: DAEO-ktiw
decisions: [DEC-1140, DEC-1104, DEC-1118, DEC-315, DEC-1010, DEC-801, DEC-808, DEC-1014, DEC-105]
reviewer: independent-auditor, fresh read-only session, sandbox check passed
W2-176 heads: `3a580a4b4d42` at the build; `ad13a5b36c65` at the end of this review

## Classification
Three findings, all in scope, none fails open or loses work (F1 ordinary yes, F2 ordinary no, F3 ordinary yes). None blocks; all three are recorded rows. Recommendation: rebuild the bundle with W2-176's current hook hash before the owner's yes line, unless W2-176 merges at `3a580a4b4d42`.

## Checks
1. **Hashes and scope.** Every hash recomputes. The before copies equal w2/integrate (`6e46f985b0a7`) and the main tree. The after copies add one block in each file (12 and 8 lines), nothing else. None of tonight's other ACTs' files is touched.
2. **Fail safe.**
   - No permission, allow rule or decision field is added.
   - The hook catches every error and exits 0 with no output.
   - With the hook file missing, the registered command exits 2 (reproduced). That is not a fail-closed block: the Bash call has already run, and the model sees an error after each call (F2).
   - `check` refuses (exit 6) on today's main tree, which lacks the hook file.
3. **Matcher and reach.** `Bash` keeps the portability check clean, and every role runs Bash often. The CTO is recognised by `class: coordination` on `DAEO-sdxk`. Sessions in worktrees that have not taken integrate miss the reminder (F3).
4. **Rehearsal.** Own clone with W2-176 at `3a580a4b4d42` merged:
   - check, apply and verify all exit 0; two files changed, modes kept at 644.
   - The five manifest checks match the manifest (counts 6 and 7).
   - The portability check gives `findings: []`.
   - Undo restores both files byte for byte.
   - pytest: `tests/unit/hooks` 165 passed / 2 skipped; `tests/unit/adapters` 94 passed; `tests/unit/gitenv` 60 passed; `tests/acceptance/W2-05` 29 passed / 1 failed (the sandbox's read-only `/tmp` blocks the rebuild lock).
   - Class (b); route: the owner's operator by hand.

## Findings
### F1: the pinned hook hash is no longer the approved one (in scope)
The ACT allows apply only when `context_watch.py` hashes as `c6dabb5e…`. W2-176 has since fixed R8 at `4dec7ec3c72c`. The file now hashes as `ed17fbb0e2b3aadbe141403860c914e3a1b14555647c7ab09e2840743e14c731`, and the CIT-P's section 2 names only that hash. Against the new head, manifest check 2 fails and check 3 passes. After a merge of the new head, `check` and `apply` refuse with exit 6 and nothing is applied. Section 7's R8 row is also out of date.
- Ordinary work: yes, because the ticket moved on during ordinary work while the ACT was being prepared.
- Consequence: other (fails closed: exit 6, nothing written).
- Reversed by: W2-176 merging at `3a580a4b4d42`.

### F2: the missing-file exit 2 is described as blocking (in scope)
For PostToolUse, exit 2 shows its error to the model after the call has run. It neither blocks nor undoes the call.
- Ordinary work: no, because the apply refuses until the file exists, and the registration and the file travel through the same branch history afterwards.
- Consequence: other.
- Reversed by: documentation or a live session showing a PostToolUse exit 2 blocking or withdrawing the tool's result.

### F3: "every session" overstates the reach (in scope)
Sessions load hooks from their own worktree's settings. The launcher's settings carry no hooks. Leads and workers on branches without the ACT commit get no reminder until their branch takes integrate.
- Ordinary work: yes, because ticket branches commonly lag integrate.
- Consequence: other (the PreCompact line still stands).
- Reversed by: launched sessions taking hooks from the main tree's settings.

## Sound
Hashes; scope; refusal before any write; atomic writes; frozen-copy checks; the entry check; undo; no weaker control; the hook silent on every error; markers ignored by git; portability; class (b).

## Hygiene
Nothing written in any tree. The scratch clone (251 MB) is removed. No embedder or model was started.

```verdict
{"kpis": [{"kpi": "act-context-watch-1", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```
