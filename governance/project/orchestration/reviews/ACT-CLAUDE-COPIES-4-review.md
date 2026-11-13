# ACT-CLAUDE-COPIES-4: the ACT review (OPERATOR-AGENT-1 §3, G4)

Reviewer: a fresh, read-only independent-auditor session (ticket DAEO-wahn's launch sandbox), not the ACT's author. Under DEC-1139 (1); judged by JUDGEMENT.md (DEC-801, DEC-808, DEC-1010).

## Summary
- Manifest sha256 `6ab06e85cae2d566c9da540c9ef0ec60c9edc366b6d5e5ccb7401a7d6d99fd17`, reviewed against integrate `a3b35c0afaf1` and `w2/W2-175` `4c0c73472fd8`.
- All five checks pass. Class (b). Five findings, none blocking: F1 and F4 are in scope with consequence other; F2, F3 and F5 are out of scope.

## Per check
1. **The bytes are the approved ones: PASS.**
   - The 13 template and source copies in `after/` equal CIT-P §2 and the files at `4c0c73472fd8`.
   - The six agents equal the reviewer's own rulesync 24.0.0 output.
   - `before/` equals the live tree and integrate `a3b35c0afaf1`.
   - All 41 manifest hashes, `list.txt` and the package table recompute as stated.
2. **Nothing else, and nothing weaker: PASS.**
   - Exactly 19 files change. The agents and sources only gain lines (+8 or +6, none removed); the templates gain 5 to 9 lines and their version line goes from 1.0.0 to 1.0.1.
   - There are exactly 7 distinct added lines: P2 (DEC-820), C-E, C-D, C-R, REC (DEC-861), STOP (DEC-1137) and the version line.
   - No front matter, tool or permission field changes.
3. **Order and window: PASS, with F1 and F4.**
   - ACT first is the only order in which W2-175's S6 is green at its merge.
   - Window state, reproduced: portability exit 1 with 13 findings; exactly the nine named cases red (W2-153 7, `tests/unit/adapters` 2).
   - Merged state: portability exit 0, W2-153 66 passed.
   - The window is bounded only by the sitting; the package should name the operator's undo line as the abort.
4. **apply.sh: PASS.**
   - `check` changes nothing.
   - `apply` copies only the frozen `after/` bytes, behind `check &&` and the operator's G7 and G8.
   - `undo` restored all 19 files byte for byte; the operator's undo step refuses if a file is not the ACT's own (DEC-1107).
   - ACT-3's F2 and F3 are still harmless.
5. **Class and route: PASS, (b).**
   - `act_class.py`: `claude-rest` 7, `agents-skills-kernel` 6, `rulesync-other` 6, no hits.
   - The yes line `yes ACT-CLAUDE-COPIES-4 6ab06e85` matches the operator's expected form.

## Findings (none blocks)
- **F1** (check 3, scope in): the package names no abort if S6 or portability in `w2/W2-175` does not read as measured, or if the sitting breaks off. The nine red cases and the held queue then have no stated end. The abort should be `undo ACT-CLAUDE-COPIES-4 6ab06e85`.
  - Ordinary work: yes, because integrate moves and sessions end in the middle of a sitting.
  - Consequence: other.
  - Reversed by: a package line naming the undo as the abort.
- **F2** (check 4, scope out): `apply.sh` does not stop on a failed step. The operator's comparison of all 19 after hashes, and the two checks over exactly those 19 files, catch it.
  - Ordinary work: no, because only a full disk or an I/O error causes it.
  - Consequence: other.
  - Reversed by: an apply route without the after-hash comparison.
- **F3** (check 4, scope out): the undo's leftover `rmdir .claude/templates`. The folder holds 8 tracked files, so the call fails silently.
  - Ordinary work: no, because it needs an empty folder at undo.
  - Consequence: other.
  - Reversed by: an empty `.claude/templates/` at undo time.
- **F4** (package text, scope in): "two trees that must change in two commits" overstates it. One commit could carry both and remove the window; the real reason for two commits is DEC-1116's route.
  - Ordinary work: yes, because the owner weighs the window on that sentence.
  - Consequence: other.
  - Reversed by: a rule that an ACT may not write `template/governance/kernel/**`.
- **F5** (builder history, scope out): one draft rebuild logged `ok` for S6 with zero cases (manifest `34a30ba1…`). The builder was then made to require more than zero passed, and the bundle's log shows 254 passed.
  - Ordinary work: yes, because the heavy slot's output can defeat the parser.
  - Consequence: fails open, for that log only; already fixed.
  - Reversed by: a bundle whose rehearsal log shows 0 passed.

```verdict
{"kpis": [{"kpi": "act-claude-copies-4", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "F3", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}]}],
 "manifest_sha256": "6ab06e85cae2d566c9da540c9ef0ec60c9edc366b6d5e5ccb7401a7d6d99fd17",
 "class": "b",
 "reviewer": "independent-auditor, fresh read-only session under ticket DAEO-wahn's launch sandbox; not the author",
 "time": "2026-11-11"}
```
