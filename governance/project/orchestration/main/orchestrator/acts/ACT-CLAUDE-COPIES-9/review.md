# ACT-CLAUDE-COPIES-9: the ACT review (OPERATOR-AGENT-1 §3, G4)

Reviewer: independent-auditor, a fresh read-only subagent of the Wave 2 CTO session, not the ACT's author. Worked under the operator's fixed reviewer brief (`~/gov-os-operator/install/reviewer-brief.md`, sha256 `e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a`, the hash in the install's `APPROVED`) and `governance/project/briefs/JUDGEMENT.md`.
- Manifest sha256: `224deee3dfa544f924e686ebb52e0d6e58586c846c96fa0a6de8a81e1b78dd79` (re-hashed; it is the expected one).
- Review bed: a fresh `--no-hardlinks` clone of `w2/integrate` at `79159cd44` with `w2/W2-37` at `7bde87727b0f` merged in one `--no-ff` commit (clean), under `/tmp/claude-1000/rv-c9-OVlyMk/`. HOME was planted at an empty folder for every apply, undo and check step. Every pytest ran through `heavy_slot.sh` with `-p no:cacheprovider` and TMPDIR inside the bed. The bed was removed afterwards.
- Integrate moved to `b97d9604b` during the review. None of the 21 commits since the rehearsal base `95a55bfcac9b` touches the three targets or the five check-2 files, and W2-37 is not merged yet (F1).
- Refused reads: 0. The guard refused four Bash calls during the review (two listings, complied with by naming the start folder; two wait loops it could not parse) and the first write of this record to the ACT folder. None was an ACT matter.

task: ACT-CLAUDE-COPIES-9 (W2-37, DAEO-6n5k)
decisions: DEC-1166 (4), DEC-1163 (8), DEC-315, DEC-1112 (3), DEC-1156 (3), DEC-1057, DEC-1104, DEC-616, DEC-861, DEC-801, DEC-808, DEC-1010, DEC-1014, CAP-33

Classification: 0 blocking. F1 to F4 are rows (consequence other).

## Per check
1. **Touched list, generation and path rule: PASS.**
   - Each of the 9 listed files hashes to its manifest value. The bundle holds nothing that is not listed (no `__pycache__`, no stray file). `list.txt` equals `touched` line for line. Each `before/` and `after/` hash equals the touched entry's.
   - The `before/` bytes are integrate's bytes today, both at `79159cd44` and at `b97d9604b`. W2-37 does not touch the three targets: they are equal at `7bde87727b0f`.
   - **Independent regeneration (the reviewer's own run):** in a second clone of the bed, the five sources were first confirmed at the expected hashes: the two change-skill template files at `cdf43a49…` and the three adopt sources at `16fd341f…`. Portability then read exactly two findings: `SOURCE_DIFFERS` for `.rulesync/skills/change/SKILL.md` and `GENERATED_DIFFERS` for `.claude/skills/adopt/SKILL.md`. The kernel change skill was copied to the root `.rulesync/`, and rulesync 24.0.0 was run with portability's own GENERATE arguments from the root `.rulesync/` into a fresh folder. The results:
     - it renders `.claude/skills/change/SKILL.md` as `dc4d01de…` and `.claude/skills/adopt/SKILL.md` as `77faaa13…`;
     - all three regenerated files are byte-equal to `after/`;
     - rulesync's only other differing output is `.claude/settings.json` (the tracked file keeps the held-out deny, DEC-616), which is not written, as in COPIES-5 to -8;
     - after the three copies, portability exits 0 with no findings (43 kernel files, 58 generated files).
   - The lead's expected file `expected-claude-change-SKILL-1.1.0.md` is also `dc4d01de…`.
   - The before→after differences are what they should be:
     - the change copy goes from version 1.0.0 to 1.1.0 and takes the `gov impact` section in place of `gov closure`;
     - the root `.rulesync` change file becomes the template's bytes;
     - the adopt copy gains W2-88a's "A9: Wave 0 memory practice" and "Verify clauses for adopted tickets" sections and their DEC ids.
   - This is drift catch-up, not lost work: `.claude/skills/adopt/SKILL.md` last changed at `faef6fa9c` (W2-52), before W2-88a's `f1ae5fecb` changed its sources. No later edit of the copy is overwritten.
   - Path rule: `apply.sh` (byte-identical to COPIES-6 and -8, `84f6f595…`) reaches its bundle through its own folder and writes only under `$PWD`. Neither check names a live repository or HOME path, and neither `cd`s; `commands` is empty. The operator's `validate_manifest`, `check_act` and `path_rule` pass when run read-only by the reviewer.
2. **Undo: PASS.** In the bed, `apply` changed exactly the three files with no mode change, and `undo` restored all three byte for byte to `before/`, leaving a clean tree. Portability then read the merged tree's own two findings again, and `apply.sh check` passed once more. The rehearsal log shows the undo, the re-apply with the same bytes, and the stage, commit, undo, commit sequence ending in an empty diff (F2 is about its wording).
3. **Rehearsal: PASS.** The log is the run of this `apply.sh`:
   - the builder writes the bundle's `apply.sh` from COPIES-6's bytes, the same hash as in the manifest;
   - `build.out` equals `rehearsal.log` line for line, apart from the final JSON line, which states the same manifest sha256;
   - the runs are in fresh clones with a planted HOME;
   - the log ends with `failures: 0`.
   The window reds it names (W2-37 `[claude-copy]` routing and W2-11 `[change]` four places) are what the evidence files show (F1 and F2).
4. **Checks: PASS.**
   - Check 1 (3 files): exit 1 before the apply; exit 0 after, with 3 `OK` lines.
   - Check 2 (5 files): exit 0 before and after on the merged bed, with 5 `OK` lines.
   - On plain integrate, check 2 is red (exit 1, the two change-skill template sources `FAILED`) while `apply.sh check` passes and nothing is changed. The operator's G8 runs the checks after its dry-run apply, so a run queued before the hand merge is refused (fails closed).
   - `apply.sh check` refuses a moved target: after the apply, check exits 3 with `moved:`. This is the same script as COPIES-1 to -8, so a second `apply` is idempotent and G7's check stands before it.
   - The exits match the manifest's `exit: 0` for both checks, and `count` is null.
5. **Class: (b).** The operator's own `act_class.classify`, run read-only on the bundle, gives class `b` with no hits:
   - row `agents-skills-kernel` for the two `.claude/skills/` copies;
   - row `rulesync-other` for `.rulesync/skills/change/SKILL.md`.
   The skill text governs agents, and the change alters it. Nothing is the owner's (O) beyond the yes (no sudo, push, Windows step or operator file).
6. **Guard replay: not applicable.** No path-map or deny entry is added, so `replay_refused` is empty.

**The suites the package names, on the bed with the bundle applied and committed (reviewer's runs; equal to the rehearsal's "landed" lines):**
- `tests/acceptance/W2-37`: 99 passed, 21 skipped.
- `tests/unit/impact`: 42 passed.
- `tests/unit/adapters`: 102 passed (40 deselected).
- `tests/acceptance/W1-33`: 112 passed (2 deselected).
- `tests/acceptance/W1-38`: 42 passed (159 deselected).
- `tests/acceptance/W2-153`: 66 passed.
- `tests/acceptance/W2-11`: 199 passed, 1 skipped.
- `tests/acceptance/W2-98`: 502 passed.
- `tests/acceptance/W2-88a`: 35 passed.
- `tests/acceptance/W2-52`: 65 passed.

All ten exit 0. The ACT makes the window's two reds green and brings no new red.

## Findings (none blocks)
- **F1** (check 3, scope in): the rehearsal measured integrate `95a55bfcac9b` and the reviewer's bed `79159cd44`. Integrate is now `b97d9604b`, and the hand merge of W2-37 has not happened yet. The real run will apply on a later head. None of the commits since `95a55bfcac9b` touches the three targets or the five check-2 files, and G7 and G8 re-read them at run time.
  - Ordinary work: yes, because integrate moves between a bundle's build and its apply.
  - Consequence: other (a moved file fails closed at G7 or G8).
  - What would reverse it: any target or check-2 file differing on the head the operator sees after the hand merge, or the merge of `w2/W2-37` no longer being clean on that head.
- **F2** (check 3, scope in): two lines of the rehearsal log say "both files" or "both targets" ("undo: both files byte for byte back", "both targets are at the same before bytes there"), though the ACT touches three files. The steps behind those lines compare the whole touched list, and the reviewer's undo restored all three. The wording is left over from the superseded two-file version. Also, the rehearsal's by-hand commit used `Task: DAEO-sdxk`, while the package's §4 gives `Task: DAEO-6n5k`. The operator commits with its own trailers, so this affects only the by-hand route's text.
  - Ordinary work: yes, because the builder was adapted from a two-file version and from COPIES-7's builder.
  - Consequence: other.
  - What would reverse it: the undo or the plain-integrate step comparing only two of the three files (they do not: both iterate over the touched list).
- **F3** (check 1, scope in): the adopt copy rests on W2-88a's approval. The manifest's `dec` names DEC-1166 (4), W2-37's approval, but not the adopt authority; the package cites DEC-1163 (8). That register item records W2-88a's sections as "the owner approves after reading their text", which is conditional. The explicit approval of `16fd341f…` at `ba400b94e738` stands in the orchestrator's `tools/kernel-approved.txt` ("DEC-1163 W2-88a's CIT-P approved at ba400b94e738 (owner, 2026-11-13)"). The reviewer found no register line or decision-record commit stating it. The copy only follows sources that are already on integrate in all three places, so the ACT is right in substance; the gap is in the record.
  - Ordinary work: yes, because an approval given in the chat can be recorded in one list and not the other.
  - Consequence: other.
  - What would reverse it: a register line or decision-record commit recording the owner's approval of W2-88a's adopt bytes at `ba400b94e738`, which closes the row. If instead there is evidence the owner did not approve those bytes, the adopt copy leaves this ACT, and W2-88a's landing goes to the owner.
- **F4** (check 1, scope out): W2-88a added two sections to the adopt skill, but its version line stays `1.0.0` in all four places. W2-11's four-places case holds, because it checks agreement, not change. The ACT is right to carry 1.0.0, since no other version was approved. Whether W2-88a's CIT-P should have moved the version is W2-88a's question under CAP-33, not this ACT's.
  - Ordinary work: yes, because a text change approved by its bytes can omit the version line.
  - Consequence: other.
  - What would reverse it: a decision that W2-88a's CIT-P set a version other than 1.0.0 (then the sources and this copy would both be rebuilt).

```verdict
{"kpis": [{"kpi": "check 1", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "check 2", "verdict": "pass", "findings": []}, {"kpi": "check 3", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "check 4", "verdict": "pass", "findings": []}, {"kpi": "check 5", "verdict": "pass", "findings": []}, {"kpi": "check 6", "verdict": "pass", "findings": []}],
 "manifest_sha256": "224deee3dfa544f924e686ebb52e0d6e58586c846c96fa0a6de8a81e1b78dd79",
 "class": "b",
 "reviewer": "independent-auditor, fresh read-only subagent of the Wave 2 CTO session; not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-13T16:18:17+00:00",
 "replay_refused": []}
```
