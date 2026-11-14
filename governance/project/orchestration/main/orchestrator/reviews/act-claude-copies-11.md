# ACT-CLAUDE-COPIES-11: the ACT review (OPERATOR-AGENT-1 §3, G4)

Reviewer: independent-auditor, a fresh read-only subagent of the Wave 2 CTO session. I am not the ACT's author. I worked under the operator's fixed reviewer brief (`~/gov-os-operator/install/reviewer-brief.md`). I re-measured its sha256, `e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a`, and found it as the one line in the install's `APPROVED`. I also applied `governance/project/briefs/JUDGEMENT.md`.
- Manifest sha256: `3b4e462f1e1fdbb3fefef7559ae2c83de03eb6ba534da34cf85d40815ffde7ba`. I re-hashed it, and it is the expected one.
- **Review bed (order 1):** a fresh `--no-hardlinks` clone of `w2/integrate` at `2b034037a4b6`, with `refs/heads/w2/W2-101` at `3bf1c96b47c1` merged in one `--no-ff` commit. It sat under my session scratchpad (`rv-c11/`).
  - The merge was clean: merge base `aeee743e9e41`, 57 files brought, none under `.claude/`.
- **Review bed (order 2):** a second fresh clone at the same integrate head.
  - `w2/W2-100` at `cdac25763613` was merged `--no-ff`, and it was clean.
  - COPIES-10 (manifest `f535215e…`) was applied by its own `apply.sh` and committed, with both of its checks green.
  - Then `w2/W2-101` was merged `--no-ff`, and it was clean: 57 files brought, none under `.claude/`.
  - Then this bundle was applied.
- **HOME and crontab:** HOME was planted at an empty folder for every apply, undo, check, portability and rulesync step, and it was still empty after each.
  - I re-ran order 2's undo, check, apply, both checks and portability under a second fresh HOME, and it stayed empty.
  - `crontab -l` was unchanged.
  - The pytest runs also used the planted HOME. W2-101's own guard-decision cases wrote a guard-call log there, under the fake session `w2-101`. That log is the tests' output, not the ACT's.
- **Pytest:** every run went through `heavy_slot.sh` with `-p no:cacheprovider`, `PYTHONUSERBASE=/home/usain/.local` and TMPDIR inside the bed. The bed was removed afterwards.
- **Heads:** integrate (`2b034037a4b6`) and `w2/W2-101` (`3bf1c96b47c1`) did not move during the review. Both are the heads the bundle was built and rehearsed on.
- **Refused calls: 1, a Bash call, and not an ACT matter.** It was a listing that started from a relative `.` after a `cd`. I complied by naming the start folder, as the guard asked.
  - Refused reads: 0.
  - Nothing under the sets root, held-out material, secrets or `~/gov-os-workbench` was read.

task: ACT-CLAUDE-COPIES-11 (W2-101, DAEO-6icv)
decisions: DEC-315, DEC-1112 (3), CAP-33, DEC-1057, DEC-1104, DEC-616, DEC-861, DEC-801, DEC-808, DEC-1010, DEC-1014

Classification: 0 blocking. F1 and F2 are rows (consequence other).

## Per check
1. **Touched list, generation and path rule: PASS.**
   - **The bundle's files.**
     - Each of the 15 `after/` files hashes to its manifest value, and so do `list.txt`, `apply.sh` and `rehearsal.log`.
     - The bundle holds no file that is not listed.
     - `list.txt` equals `touched` line for line, in root, path, before (`null`) and after.
     - Each `touched` after equals its `files` entry.
   - **No `before/` folder.**
     - Every target is absent on integrate and on the merged tree.
     - No ref in the repository has ever held any of `.claude/skills/{frontend,ui-ux,devops}/` (`git log --all`).
     - So there is no earlier work to lose.
   - **The changed set.** In the bed, `apply` changed exactly the 15 listed files and nothing else:
     - the untracked set equals `list.txt`, and no tracked file changed;
     - each file is at its stated after sha256, with mode 644, the kernel files' git mode;
     - nothing changed in HOME or in `crontab -l`.
   - **Independent regeneration (my own run).** I ran rulesync 24.0.0 with portability's own GENERATE arguments, from the bed's root `.rulesync/` into a fresh empty folder, with HOME planted.
     - All five files of each of the three skill folders are byte-equal to `after/` (`diff -r`, three folders).
     - rulesync's only other output that differs from the applied bed is `.claude/settings.json`. It holds the held-out deny (DEC-616) and is not written, as in COPIES-5 to -10.
     - The four non-`SKILL.md` files of each folder are byte-equal to their kernel files.
     - Each `SKILL.md` differs from its kernel source only in front matter, re-folded the way rulesync renders every existing copy:
       - the top-level `version` and `output` are dropped;
       - `description` is folded;
       - `metadata.version` is unquoted;
       - the blank line after the front matter is gone.
     - The versions are frontend 1.2.0, ui-ux 1.1.0 and devops 1.1.0, the kernel's own.
     - In order 2 (W2-100 and COPIES-10 first), rulesync gives the same bytes for the three folders. So the bundle is order-independent.
   - **The sources.**
     - I compared the 45 hashes of check 2 mechanically with the 15 rows of W2-101's CIT-P §3, read from the branch head (sha256 `42c1cc38…`). All 45 agree: each `.rulesync` and `template/.rulesync` copy carries its kernel file's hash.
     - The one commit after the verified product head `1ef54a70037a` touches only `docs/changes/W2-101-CIT-P.md` and `docs/probes/DAEO-6icv/PR-DAEO-6icv-r2.md`.
   - **Portability.** On the applied bed it exits 0 with no finding (58 kernel files, 73 generated files). In order 2 it also exits 0 with no finding (78 kernel files, 93 generated files, all seven skills).
   - **Path rule.**
     - `apply.sh` is byte-identical to COPIES-6 to -10 (`84f6f595…`, eight bundles).
     - It reaches its bundle through its own folder, writes only under `$PWD`, and accepts only the root `repo`.
     - Both checks are `sha256sum -c` over relative paths. Neither names a live repository or HOME path, and neither `cd`s.
     - `commands` is empty.
   - **The operator's gates.** I ran `validate_manifest`, `check_act` and `path_rule` from a script in my bed, with `-B`, so nothing was written to the install (its `__pycache__` is unchanged). All three pass.
2. **Undo: PASS.**
   - In the bed, `undo` removed all 15 files, and `git status` was clean again: the before-state, absent, restored exactly.
   - The three emptied folders stay behind, which git does not see. The package says so in §5.
   - Portability then read the window's 15 `GENERATED_DIFFERS`, and `apply.sh check` passed again.
   - The re-apply gave the same 15 hashes.
   - In order 2 (committed), undo and re-apply returned the tree to its committed state.
   - The rehearsal log shows the undo, the re-apply and the stage, commit, undo, commit sequence ending in an empty diff.
3. **Rehearsal: PASS.**
   - **The log is the run of this `apply.sh`.**
     - The builder writes the bundle's `apply.sh` from COPIES-10's bytes, after asserting they are COPIES-9's and COPIES-7's too.
     - `drafts/claude-copies-11/build.out` equals `rehearsal.log` line for line. The only exception is its trailing lines: the final JSON (the same manifest sha256, failures 0) and the operator-gate output.
   - The runs used fresh clones, with HOME planted, and the log ends with `failures: 0`.
   - **The window reds the log names are the evidence files' reds.**
     - The nine cases are listed in `evidence/red-merged-window.txt`: W2-101's three claude-copy cases and three generated-drift cases, and W2-11's three four-places cases.
     - After the ACT, `evidence/red-merged-landed.txt` is empty.
     - My own window run of the named cases (the merged tree without the ACT) gave exactly these 9 FAILED. The four-places case for the other 10 skills PASSED.
4. **Checks: PASS.**
   - Check 1 (15 files): exit 1 before the apply, with 15 `FAILED`; exit 0 after, with 15 `OK`.
   - Check 2 (45 files): exit 0 before and after on the merged bed, with 45 `OK`.
   - **Plain integrate:** none of the 45 sources exists there, so check 2 is red (no `OK` line, exit 1) while `apply.sh check` passes. The same holds after W2-100 and COPIES-10 without W2-101 (exit 1).
     - The operator's G8 runs the checks after its dry-run apply, so a run queued before the hand merge is refused.
     - So the order is held, and it fails closed.
   - `apply.sh check` after the apply exits 3 with `moved: .claude/skills/devops/SKILL.md`, so G7 refuses a second run on an applied tree.
   - In order 2, COPIES-10's two checks stay green after this ACT.
   - The exits match the manifest's `exit: 0` for both checks, and `count` is null.
5. **Class: (b).**
   - The operator's own `act_class.classify`, run read-only on the bundle, gives class `b`, row `agents-skills-kernel` for all 15 files, with no hits.
   - The new skill text governs engineer sessions once it is loaded.
   - Nothing in it is the owner's (O) beyond the yes: no sudo, push, tag, Windows step or operator file, and the undo is tested.
6. **Guard replay: not applicable.** No path-map or deny entry is added, so `replay_refused` is empty.

**The suites, on the order-1 bed with the bundle applied and committed (my runs; equal to the rehearsal's "landed" lines):**
- `tests/acceptance/W2-101`: 277 passed. The generated-drift cases ran with rulesync present and were not skipped.
- `tests/acceptance/W2-11`: 217 passed, 1 skipped.
- `tests/unit/adapters`: 110 passed (40 deselected).
- `tests/acceptance/W1-33`: 112 passed (2 deselected).
- `tests/acceptance/W1-38`: 46 passed (162 deselected).
  - My first run gave 43 passed and 3 errors. The three OpenSpec cases look for `openspec` under `~/.nvm`, which the planted HOME lacks. That was a fault in my environment.
  - The re-run with `OPENSPEC_BIN` naming the registered binary passed all 46.
- `tests/acceptance/W2-153`: 137 passed, 18 skipped.
- `tests/acceptance/W2-88a`: 35 passed.
- `tests/acceptance/W2-52`: 65 passed.
- I did not re-run W2-98 or W2-37. They read no skill folder, and the rehearsal gives them green in both the window and landed.

**Order 2 (W2-100, COPIES-10, W2-101, then this ACT):**
- `tests/acceptance/W2-100`: 230 passed.
- `tests/acceptance/W2-101`: 277 passed.
- `tests/acceptance/W2-11`: 241 passed, 1 skipped.
- `tests/unit/adapters`: 110 passed.

The ACT makes the window's nine reds green and brings no new red, in either order.

## Findings (none blocks)
- **F1** (check 1, scope in): the authority the ACT rests on is still pending.
  - W2-101's CIT-P (`docs/changes/W2-101-CIT-P.md` at `3bf1c96b47c1`) has `status: PROPOSED` and `owner_approval: 'pending'`. The package says so (§0).
  - The manifest's `dec` names DEC-315, DEC-1112 (3) and CAP-33. All are ACCEPTED in the register; DEC-1112 (3) is the standing rule that class (b) ACTs need the owner's yes. The `dec` field does not name the CIT-P approval, and no register entry yet names `W2-101-CIT-P`.
  - The ACT cannot run before W2-101's sources are on integrate, because check 2 is red there, and the merge is itself the step that needs the approval. So the order holds in the machinery; the gap is only in the record.
  - Ordinary work: yes, because an ACT is built and reviewed before the approval it follows is given.
  - Consequence: other.
  - What would reverse it: the owner's `yes W2-101-CIT-P 42c1cc38`, recorded before the hand merge, closes the row. A merge of `w2/W2-101` without that approval would be a P1 of the merge, not of this ACT.
- **F2** (check 3, scope in): the real run will apply on a later head than the one rehearsed and reviewed.
  - The rehearsal and both beds measured integrate `2b034037a4b6`. The hand merge of W2-101 has not happened yet.
  - G7 and G8 re-read the 15 targets and the 45 sources at run time.
  - Ordinary work: yes, because integrate moves between a bundle's build and its apply.
  - Consequence: other (a moved target or source fails closed at G7 or G8).
  - What would reverse it: any of the following on the head the operator sees after the hand merge:
    - any of the 15 targets present;
    - any of the 45 sources differing;
    - the merge of `w2/W2-101` no longer clean;
    - rulesync rendering different bytes from that head's root `.rulesync/`.

Probed and found sound:
- the apply's changed set, and nothing outside the repository;
- no earlier work at the targets;
- the regeneration being byte-exact and order-independent;
- check 2 holding the order, failing closed on plain integrate and after COPIES-10 alone;
- G7's moved-target refusal after an apply;
- the undo restoring absence;
- COPIES-10 staying green beside this ACT;
- the package's §6 statement on the harness, which matches integrate since W2-104 (no stale claim, unlike COPIES-10's F3).

```verdict
{"kpis": [{"kpi": "check 1", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "check 2", "verdict": "pass", "findings": []}, {"kpi": "check 3", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "check 4", "verdict": "pass", "findings": []}, {"kpi": "check 5", "verdict": "pass", "findings": []}, {"kpi": "check 6", "verdict": "pass", "findings": []}],
 "manifest_sha256": "3b4e462f1e1fdbb3fefef7559ae2c83de03eb6ba534da34cf85d40815ffde7ba",
 "class": "b",
 "reviewer": "independent-auditor, fresh read-only subagent of the Wave 2 CTO session; not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-14T05:39:20+00:00",
 "replay_refused": []}
```
