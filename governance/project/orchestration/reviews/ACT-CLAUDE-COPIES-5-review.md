# ACT-CLAUDE-COPIES-5: the ACT review (OPERATOR-AGENT-1 §3, G4)

Reviewer: independent-auditor, a fresh read-only session in DAEO-k7hz's launch sandbox; not the ACT's author. Manifest sha256 `e602d5960dccf62100cb8bc151ae3363fe3e8eb4d96ed8c9e29fe045450f0c91`.

## Summary
- All five checks pass. Class (b).
- Three findings, none blocking. F1 and F2 are package text, in scope, consequence other. F3 is in scope but needs a construction ordinary work doesn't reach (ordinary work no), so it is a row.
- The six files are rulesync 24.0.0's output. I regenerated them in my own clone: today's integrate `b7a4e93a574a` with `w2/W2-11` `58ac442d6820` merged in.

## Per check
1. **Bytes: PASS.**
   - All 16 hashes match the package, `list.txt` and the manifest; so do check 2's six source hashes.
   - `before/` equals the blobs at `w2/W2-11` `58ac442d6820` and at `dca382f3069f` (that commit only changes the CIT-P file).
   - The root `.rulesync`, `template/.rulesync` and kernel sources are byte-equal.
   - My regeneration differs from the tree in exactly the six files, each equal to `after/`. The only other difference is `.claude/settings.json`, the held-out deny line (DEC-616).
   - Portability with W2-11 merged reports exactly these six as `GENERATED_DIFFERS`.
2. **Nothing else, nothing weaker: PASS, with F1.**
   - Six files only, none shared with ACT-4's 19.
   - Diff sizes: discovery and retrieval change only their version line; test-kinds changes one body line; orchestration +25/−20; briefs-and-returns +52/−0; test-design +40/−13.
   - The only front-matter change is an added `metadata.version: 1.4.0`. No copy has a tool list, before or after.
3. **Order and window: PASS, with F2.**
   - *Sound:* yes. The ACT before W2-11's merge gives 4 conflicts (reproduced), and `check` refuses on plain integrate (exit 3, `moved: .claude/skills/discovery/SKILL.md`, reproduced).
   - *Bounded:* yes, by the CTO's hold on the queue and nightly, with the undo named as the abort and W2-11's revert as the full close.
   - *Better order:* none while DEC-315 holds.
   - *Window, reproduced:* W2-11 gives exactly the 7 named failures (186 passed, 1 skipped) and portability gives 6 `GENERATED_DIFFERS`.
   - *After the ACT, reproduced:* W2-11 193 passed, 1 skipped; portability exit 0.
4. **apply.sh: PASS, with F3.**
   - `check` only reads.
   - `apply` and `undo` stop with exit 4 on a failed step.
   - `undo` restored the six files byte for byte (tree clean).
   - ACT-4's F2, F3 and F5 are fixed; so are F1 (the undo is named as the abort) and F4 (the two-commit reason now cites DEC-315).
   - The path rule holds: `$PWD` and the bundle folder only, no live paths, `commands: []`.
   - The checks run relative to the repository: sha256 lists of the six copies and the six root sources.
5. **Class and route: PASS.** Row `agents-skills-kernel` matches `.claude/skills/**`, class b. No earlier (O) row matches. The operator's own `act_class.py` gives b, no hits. The route is the operator agent on `yes ACT-CLAUDE-COPIES-5 e602d596`.

## Findings (none blocks)
- **F1** (package §1, scope in): the test-kinds.md row says "version line 1.0.0 to 1.1.0". The file has no version line; the change rewrites the load-sensitive row to measure the work under test (DEC-979 item 1 D2, DEC-983).
  - Ordinary work: yes, because the row was written by analogy with the two version-only files.
  - Consequence: other.
  - What would reverse it: a test-kinds.md diff showing a version line.
- **F2** (package §2, scope in): the six-step sequence does not place W2-175 between ACT-4 and W2-11's merge. W2-175 appears only in fact 3 and §5, so ACT-4's window and this one could overlap.
  - Ordinary work: yes, because a reader following only the six steps could interleave them.
  - Consequence: other.
  - What would reverse it: a sequence line, here or in ACT-4's package, that lands W2-175 before step 2.
- **F3** (apply.sh, scope in): `apply` and `undo` don't check the state they start from. The by-hand undo in §4 would overwrite any later change to the six files. The operator's undo refuses in that case (DEC-1107).
  - Ordinary work: no, because changing these files inside the held window needs another ACT (DEC-315).
  - Consequence: loses work.
  - What would reverse it: an ordinary-work route that changes these files in the window.

## What I probed and found sound
- Hashes, before/after bytes, the source equality, and the regeneration.
- Portability in all three states: plain integrate, the window, and the ACT applied.
- Apply, undo and re-check in a clone.
- The negative control on plain integrate, and the conflict count for the other order.
- The class.
- ACT-4's F1–F5 fixes.
- Integrate's 7 commits since the build: none touches a path the ACT depends on.

Not re-run here: W2-128, W2-142, W1-35, W2-153, `tests/unit/adapters` (the bundle's log shows them green). Scratch: 205M, 10,467 inodes, removed.

```verdict
{"kpis": [{"kpi": "act-claude-copies-5", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "loses work"}]}],
 "manifest_sha256": "e602d5960dccf62100cb8bc151ae3363fe3e8eb4d96ed8c9e29fe045450f0c91",
 "class": "b",
 "reviewer": "independent-auditor, fresh read-only session under ticket DAEO-k7hz's launch sandbox; not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-12T01:06:17+00:00",
 "replay_refused": []}
```
