# ACT-CLAUDE-COPIES-10: the ACT review (OPERATOR-AGENT-1 §3, G4)

Reviewer: independent-auditor, a fresh read-only subagent of the Wave 2 CTO session, not the ACT's author. I worked under the operator's fixed reviewer brief (`~/gov-os-operator/install/reviewer-brief.md`), whose sha256 `e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a` I re-measured and found as the one line in the install's `APPROVED`. I also applied `governance/project/briefs/JUDGEMENT.md`.
- Manifest sha256: `f535215e5ba08a366fda4c0e4580e95c0d1cd1cd9150af0329372f107814c6bd`. I re-hashed it, and it is the expected one.
- **Review bed:** a fresh `--no-hardlinks` clone of `w2/integrate` at `f3d3438fcb45`, with `refs/heads/w2/W2-100` at `cdac25763613` merged in one `--no-ff` commit, under my session scratchpad (`rv-c10-*`).
  - The merge was clean: merge base `0a706dc4c2f1`, 72 files brought, none under `.claude/`.
  - HOME was planted at an empty folder for every apply, undo, check, portability and rulesync step. It was still empty at the end, and `crontab -l` was unchanged.
  - Every pytest ran through `heavy_slot.sh` with `-p no:cacheprovider`, `PYTHONUSERBASE=/home/usain/.local` and TMPDIR inside the bed. The bed was removed afterwards.
- **Integrate moved during the review**, to `2b034037a`. Its one new commit touches only `.tickets/DAEO-03ub.md`. The merge of `w2/W2-100` is still clean on the new head (`git merge-tree`). `w2/W2-100` is still at `cdac25763613`. See F1.
- **Refused calls: 2, both Bash, and neither an ACT matter.**
  - A listing that started from a relative `.` after a `cd`. I complied by naming the start folder, as the guard asked.
  - A wait loop with a process substitution that the guard could not parse ("could not decide"). I replaced it with a plain loop.
  - Refused reads: 0. Nothing under the sets root, held-out material, secrets or `~/gov-os-workbench` was read.

task: ACT-CLAUDE-COPIES-10 (W2-100, DAEO-uw5h)
decisions: DEC-315, DEC-1112 (3), CAP-33, DEC-1057, DEC-1104, DEC-616, DEC-861, DEC-801, DEC-808, DEC-1010, DEC-1014

Classification: 0 blocking. F1 to F3 are rows (consequence other).

## Per check
1. **Touched list, generation and path rule: PASS.**
   - **The bundle's files.** Each of the 20 listed files hashes to its manifest value, and so do `list.txt`, `apply.sh` and `rehearsal.log`. The bundle holds no file that is not listed. `list.txt` equals `touched` line for line, in root, path, before (`null`) and after.
   - **No `before/` folder.** Every target is absent on integrate (`f3d3438fc`) and on the merged tree, and no ref in the repository has ever held any of the four `.claude/skills/{backend,api,data,security}/` folders (`git log --all`). So there is no earlier work to lose.
   - **The changed set.** In the bed, `apply` changed exactly the 20 listed files and nothing else in the repository: the untracked set equals `list.txt`, and no tracked file changed. Each file is at its stated after sha256, with mode 644. Nothing changed in HOME or in `crontab -l`.
   - **Independent regeneration (my own run).** I ran rulesync 24.0.0 with portability's own GENERATE arguments, from the bed's root `.rulesync/` into a fresh empty folder, with HOME planted.
     - All five files of each of the four skill folders are byte-equal to `after/` (`diff -r`, four folders).
     - rulesync's only other output that differs from the applied bed is `.claude/settings.json`, which holds the held-out deny (DEC-616). It is not written, as in COPIES-5 to -9.
     - The four non-`SKILL.md` files of each folder are byte-equal to their kernel files.
     - Each `SKILL.md` differs from its kernel source only in front matter, re-folded the way rulesync renders every existing copy (compare `.claude/skills/audit/SKILL.md` with its kernel file): the top-level `version` and `output: none` are dropped, `description` is folded, `metadata.version` is unquoted, and the blank line after the front matter is gone. The versions are backend 1.0.1, api 1.0.2, data 1.0.2 and security 1.0.1, the kernel's own.
   - **The sources.** The sixty source hashes of check 2 equal W2-100's CIT-P §3. I read the CIT-P from the branch head; its sha256 is `7bb4f1ac…`. The commits after the verified product head `f7637bd03e25` touch only `docs/changes/W2-100-CIT-P.md` and the two `docs/probes/DAEO-uw5h/` records.
   - **Portability.** On the applied bed it exits 0 with no finding (63 kernel files, 78 generated files).
   - **Path rule.** `apply.sh` is byte-identical to COPIES-6 to -9 (`84f6f595…`). It reaches its bundle through its own folder, writes only under `$PWD`, and accepts only the root `repo`. Both checks are `sha256sum -c` over relative paths. Neither names a live repository or HOME path, and neither `cd`s. `commands` is empty.
   - **The operator's gates.** I ran `validate_manifest`, `check_act` and `path_rule` read-only, with `-B` so nothing was written to the install. All three pass.
2. **Undo: PASS.**
   - In the bed, `undo` removed all 20 files, and `git status` was clean again: the before-state, absent, restored exactly. The four emptied folders stay behind, which git does not see; the package says so in §5.
   - Portability then read the window's 20 `GENERATED_DIFFERS`, and `apply.sh check` passed again.
   - The re-apply gave the same 20 hashes.
   - The rehearsal log shows the undo, the re-apply and the stage, commit, undo, commit sequence ending in an empty diff.
3. **Rehearsal: PASS.**
   - **The log is the run of this `apply.sh`.** The builder writes the bundle's `apply.sh` from COPIES-9's bytes, after asserting they are COPIES-7's too. `drafts/claude-copies-10/build.out` equals `rehearsal.log` line for line, apart from its final JSON line, which states the same manifest sha256, failures 0.
   - The runs used fresh clones, with HOME planted, and the log ends with `failures: 0`.
   - **The window reds the log names are the evidence files' reds.** The twelve cases are W2-100's four claude-copy cases and four generated-drift cases, and W2-11's four four-places cases (`evidence/red-merged-window.txt`). After the ACT, `evidence/red-merged-landed.txt` is empty.
4. **Checks: PASS.**
   - Check 1 (20 files): exit 1 before the apply, with 20 `FAILED`; exit 0 after, with 20 `OK`.
   - Check 2 (60 files): exit 0 before and after on the merged bed, with 60 `OK`.
   - On plain integrate, none of the sixty sources exists (`git ls-tree` at `f3d3438fc`), so check 2 is red there while `apply.sh check` passes. The operator's G8 runs the checks after its dry-run apply, so a run queued before the hand merge is refused: the order is held, and it fails closed.
   - `apply.sh check` after the apply exits 3 with `moved: .claude/skills/api/SKILL.md`, so G7 refuses a second run on an applied tree.
   - The exits match the manifest's `exit: 0` for both checks, and `count` is null.
5. **Class: (b).**
   - The operator's own `act_class.classify`, run read-only on the bundle, gives class `b`, row `agents-skills-kernel` for all 20 files, with no hits.
   - The new skill text governs engineer sessions once it is loaded.
   - Nothing in it is the owner's (O) beyond the yes: no sudo, push, tag, Windows step or operator file, and the undo is tested.
6. **Guard replay: not applicable.** No path-map or deny entry is added, so `replay_refused` is empty.

**The suites the package names, on the bed with the bundle applied and committed (my runs; equal to the rehearsal's "landed" lines):**
- `tests/acceptance/W2-100`: 230 passed. The generated-drift cases ran with rulesync present and were not skipped.
- `tests/acceptance/W2-11`: 223 passed, 1 skipped.
- `tests/unit/adapters`: 110 passed (40 deselected), with `PYTHONPATH` at the bed's `src`, as the builder runs it. My first run without it stopped at collection (no `gov` module), which was a fault in my environment, not the ACT's.
- `tests/acceptance/W1-33`: 112 passed (2 deselected).
- `tests/acceptance/W1-38`: 46 passed (162 deselected).
- `tests/acceptance/W2-153`: 137 passed, 18 skipped.
- `tests/acceptance/W2-98`: 502 passed.
- `tests/acceptance/W2-88a`: 35 passed.
- `tests/acceptance/W2-52`: 65 passed.
- `tests/acceptance/W2-37`: 120 passed.

The ACT makes the window's twelve reds green and brings no new red.

## Findings (none blocks)
- **F1** (check 3, scope in): the real run will apply on a later head than the one rehearsed and reviewed.
  - The rehearsal and the bed both measured integrate `f3d3438fcb45`. Integrate is now `2b034037a`, and the hand merge of W2-100 has not happened.
  - The one new commit touches only a ticket file, the merge is still clean, and G7 and G8 re-read the targets and the sixty sources at run time.
  - Ordinary work: yes, because integrate moves between a bundle's build and its apply.
  - Consequence: other (a moved target or source fails closed at G7 or G8).
  - What would reverse it: any of the 20 targets or 60 sources differing on the head the operator sees after the hand merge, or the merge of `w2/W2-100` no longer being clean on that head.
- **F2** (check 1, scope in): the authority the ACT rests on is still pending.
  - W2-100's CIT-P (`docs/changes/W2-100-CIT-P.md` at `cdac25763613`) has `status: PROPOSED` and `owner_approval: 'pending'`. The package says so. The manifest's `dec` names DEC-315, DEC-1112 (3) and CAP-33, which are both ACCEPTED in the register (DEC-1112 (3) is the standing rule that the owner's yes is needed on class (b) ACTs), but not the CIT-P approval.
  - The ACT cannot run before W2-100's sources are on integrate, because check 2 is red there, and the merge is itself the step that needs the approval. So the order holds in the machinery. The gap is only in the record.
  - Ordinary work: yes, because an ACT is built and reviewed before the approval it follows is given.
  - Consequence: other.
  - What would reverse it: the owner's `yes W2-100-CIT-P 7bb4f1ac` recorded before the hand merge closes the row. A merge of `w2/W2-100` without that approval would make it a P1, but a P1 of the merge, not of this ACT.
- **F3** (out of scope): the package's §6 still lists P-W2-100-F2 as open, but integrate has already settled it.
  - P-W2-100-F2 is the skill-evaluation harness copying `scenario-summaries.md` into the evaluated session.
  - On integrate, W2-104 (`ac18ac2ab`, merged at `e133afea4`) has the harness leave `scenarios.md`, the records and the summaries out of the session's copy of the skill folder. So the `.claude` copies carrying those files has no harness effect.
  - An ordinary session in the main tree can still read them in `.claude/skills/<skill>/`, as the CIT-P §6 states. That was accepted there.
  - Ordinary work: yes, because the package was written from the CIT-P, which predates W2-104's merge.
  - Consequence: other.
  - What would reverse it: the harness on integrate copying any of those three files into a session folder.

```verdict
{"kpis": [{"kpi": "check 1", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "check 2", "verdict": "pass", "findings": []}, {"kpi": "check 3", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "check 4", "verdict": "pass", "findings": []}, {"kpi": "check 5", "verdict": "pass", "findings": []}, {"kpi": "check 6", "verdict": "pass", "findings": []}],
 "manifest_sha256": "f535215e5ba08a366fda4c0e4580e95c0d1cd1cd9150af0329372f107814c6bd",
 "class": "b",
 "reviewer": "independent-auditor, fresh read-only subagent of the Wave 2 CTO session; not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-14T05:07:12+00:00",
 "replay_refused": []}
```
