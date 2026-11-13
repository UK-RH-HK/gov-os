---
type: probe
task: DAEO-2bdu
round: narrow check after round 2 (DEC-1154's practice; the owner's P1-W2-88-RV2-1 (a))
reviewer_session: fa647d9d-1cf1-4be9-adfc-2a44e4261318
implementer_session: d26e2156-1ea7-4775-a5e2-c945729f2ca0 (eng-4, run 5's fix); test designer td-7 258e165e-ea7b-472c-a781-058a60a89bad
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: fail
probed_commit: 8f9571c7919d512cc4928b9bbafd4e19a67b6460
decisions_applied: [DEC-1154, DEC-1010, DEC-136, DEC-820, DEC-1052, DEC-1120, DEC-801, DEC-808]
---

# Probe record: W2-88 (DAEO-2bdu), narrow independent check of the RV2-1/RV2-2 fix: FAIL

Round 2 (the last, DEC-1010) is `PR-DAEO-2bdu-round-2.md`; round 1 is `PR-DAEO-2bdu-round-1.md`. This record is the narrow check the owner's decision P1-W2-88-RV2-1 (a) called for: only the change since a15de913e8c4.

## The lead's judgement and triage

- **Who checked.** A fresh, read-only Independent Auditor (`fa647d9d-1cf1-4be9-adfc-2a44e4261318`, claude-opus-5-5, effort high, class C2), started through `launch_worker.sh` / `gov launch` under the OS sandbox on 2026-11-13. Its brief carried `governance/project/briefs/JUDGEMENT.md` word for word and the run-5 interface (`.gov-runtime/scratch/lead/briefs/run5-interface.md`). Step 0 held. HEAD was 8f9571c7919d and `git status --porcelain` was empty at the start and at the end. Its tripwire shows no change in this ticket's trees.
- **What it checked.** The engineer's commit af046b331e27 (`fabric.py`, `refactor_plan.py`, `tests/unit/adopt/test_w2_88_rv2.py`) and td-7's cases 3923bf8469f7, merged at 8f9571c7919d (`test_w2_88_rv2_undo.py`, `standin_rv2/`, two cases in `test_w2_88_s2_plan.py`, the README's "Run 5 revisions"), against RV2-1's and RV2-2's stated behaviour.
- **Refusals the checker met, each once, not retried in the same form:** the Write tool for files in its TMPDIR (the auditor's tool list holds no Write), and a shell `while read` loop. It wrote its probe scripts in its TMPDIR with `printf` from Bash, the probe channel its brief names (DEC-1144 (7)).
- **The lead's verification at the head** (outside the sandbox): `gov accept W2-88`: outcome pass, every KPI line pass, 214 passed, 0 failed, 0 skipped (`.gov-runtime/scratch/lead/log/accept-5.txt`). td-7's cases were red on a15de913e8c4 for the reasons the README states (td-7's return); 8 of them fail on the unfixed code, and Case D and the RV2-2 one-line form are guards. The rebuild was ok (complete, `not_built` empty, four digests; `log/rebuild-5.txt`). lead_verify (scoped, DEC-968) at 8f9571c7919d: RED, parallel 6,258 tests, 1 failed, 11 skipped, in 2,565 s; serial 3 passed (`.gov-runtime/scratch/lead/log/verify/parallel.xml`, `serial.xml`). The one failure is `tests/acceptance/W2-23/test_w2_23_space.py:94` (`context_watch.py` not in the settings' hook lines): a known red of the environment and integrate's, red in rounds 1 and 2 too, not this branch's (the CTO's, DEC-1156 (7)).
- **The verdict stands as FAIL** (never decided away). RV2-2 is fixed. RV2-1 is fixed for every case its stated behaviour and the interface name. NC-1 is a second route to the same loss. The triage:

| finding | severity | triage | the fix, as a described behaviour for the test designer (DEC-136) |
|---|---|---|---|
| NC-1: a refused A9 record commit still runs `git reset --hard`. A9 commits through `run.finish` → W2-23's `project.commit` (`stages.py:54`). On a failed commit, `project.commit` calls `project.restore` (`project.py:144-145` → `:114`) before A9's undo runs. Confirmed by the lead from the code. | blocker (in scope: RV2-1's own words, "when A9 refuses … after installing the kernel files"; ordinary work: yes, a pre-commit hook or signing that refuses the record commit; consequence: loses work) | to the owner via the CTO (the rounds are spent, DEC-1010; the owner decided (a) for RV2-1 with W2-23's `project.restore` unchanged, and NC-1's fixes either keep that or change it): package P-W2-88-NC-1 | when A9's own record commit is refused (a `pre-commit` hook exits 1), A9 runs no `git reset --hard`. It unstages only what it staged (its copies and its record), deletes only the files it wrote whose bytes are still its own, keeps a tracked file edited during the run and a file staged during the run, and refuses by name (the commit's refusal) with HEAD unmoved and no `reset` in the reflog |
| NC-2: a Ctrl-C between `install`'s `git add` and its listing leaves A9's copies staged (`fabric.py:209-215`) | minor (ordinary work: no, a window of milliseconds; consequence: other) | a row; it rides along with NC-1's fix if the owner chooses (a) (DEC-802) | an interrupt at any point after A9's `git add` leaves no copy of A9's in the index; an index entry whose blob is A9's own bytes counts as staged by A9 |
| note: `project.commit` takes whatever is staged, so a file someone staged during the run goes into A9's adoption commit | note (ordinary work: yes; consequence: other, nothing lost) | a row, with NC-1 | — |

The checker's report follows, unchanged.

# W2-88 (DAEO-2bdu): narrow independent check of the RV2-1/RV2-2 fix
probed_commit: 8f9571c7919d512cc4928b9bbafd4e19a67b6460
base: a15de913e8c4

## Sandbox and identity
- **Step 0 (EMG-d4b-launched.md):**
  - (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-2bdu','w')…"` failed with `OSError: [Errno 30] Read-only file system`, and no file was made.
  - (b) `echo sandbox-trial | git hash-object -w --stdin` gave `1ae28402a109…` (exit 0); `git update-index --refresh` exited 0.
- **Identity:** `printenv GOV_ROLE GOV_TICKET` gave `independent-auditor`, `DAEO-2bdu`.
- **Head and status:** HEAD was `8f9571c7919d512cc4928b9bbafd4e19a67b6460` at the start and at the end. `git status --porcelain` was empty at the start and at the end.
- **No model process:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing.
- **Write tool refused:** the Write tool was refused once for files in TMPDIR. I wrote the probe scripts there with `printf` from Bash instead, the channel the brief sanctions (DEC-1144 (7)).
- **Guard refused one form:** a shell `while read` loop over file names was refused (DEC-820/DEC-953). I did not retry it in another form; I used two plain greps instead.

## RV2-1 and RV2-2
| Item of the stated behaviour | Result | file:line | How probed |
|---|---|---|---|
| 1. Index: unstage only what A9 staged, only while the entry is still A9's blob | fixed | fabric.py:248-259 | E-add-all (`git add -A` during the run): only `mine.txt` stays staged. C-edit-copy-restaged: stays `A` with the user's blob. A-gov: `new.md` stays staged. |
| 2. Tree: delete only A9's bytes; folders only when empty | fixed | fabric.py:260-276 | C-edit-copy leaves `?? SKILL.md` (bytes changed). F-in-a9-dir: the folder holding a user file is kept and the other folders are removed. |
| 2. A replaced tracked file is put back, never deleted | fixed | fabric.py:268-270 | D-replaced and D-replaced-ctrlc: the file holds `own` and the status is clean. D-replaced-edited: the user's bytes stay (status ` M`). |
| 3. No reset, no checkout; edit, untracked file and branch kept | partly | fabric.py:233-279; **stages.py:54 → project.py:145 → project.py:114** | A-gov, A-ctrlc and G-untracked keep the edit and the untracked file, with no `reset` in the reflog. **J-commit-refused-by-hook: `reset: moving to 5232eb7`, the edit is lost and the staged `new.md` is deleted (NC-1).** |
| 4. `HEAD_MOVED`: message, details, branch kept, copies the new HEAD holds left | fixed | fabric.py:281-293 | B-notes: message names both full hashes and says "nothing was reset"; details are `{started, now, cause: "REBUILD_FAILED"}`; reflog is `commit: during` with no reset. B-notes-ctrlc: cause `KeyboardInterrupt`. B-all: all 5 copies stay in the tree and the index, status clean. |
| 5. HEAD unmoved: own code kept, an interrupt stays an interrupt | fixed | fabric.py:216-218, 634-636 | A-gov gives `REBUILD_FAILED`. A-ctrlc and D-replaced-ctrlc give `KeyboardInterrupt`. |
| 6. `project.restore` unchanged | fixed | — | `git diff a15de913e8c4 8f9571c7919d -- src/gov/adopt/project.py` gives 0 lines |
| RV2-2: partial list on its own lines after `Unscanned paths:` | fixed | refactor_plan.py:172-177 | `plan()` with two skipped paths (one with a space) gives `Unscanned paths:`, then ``- `big one.txt` `` and ``- `docs/huge.txt` `` |
| RV2-2: `all <n> tracked files` stays one line | fixed | refactor_plan.py:172 | `secrets_scanned=False` gives `Unscanned paths: all 3 tracked files` |

## What I probed and found sound
1. **Round 2's case A (edit plus staged new file, then `REBUILD_FAILED` or Ctrl-C):** status ` M a.md`, `A  new.md`. No copy is left in the index; no folder of A9's is left; HEAD unmoved; reflog only `commit (initial)`. (`$TMPDIR/probe/cases1.py`, A-gov and A-ctrlc.)
2. **Round 2's case B (`git commit -- notes.md`, then a refusal):** `HEAD_MOVED` with `started` and `now` as full hashes. The branch stays at the new commit, `notes.md` is in the tree, status is clean, and the newest reflog entry is the commit (B-notes).
3. **A copy committed during the run (B-all):** left in the index and the tree, judged against the new HEAD (fabric.py:251-252, 266-267).
4. **A repository's own `retrieval.yaml` (H-own-retrieval):** not written, kept as `own: 1`, status clean.
5. **`install`'s failure path:**
   - an `OSError` on the third write leaves a clean tree and index;
   - a held `index.lock` makes `git add` fail with `ADOPT_GIT_FAILED`, and the tree is clean (I-oserror-third-write, I-index-locked).
6. **`HEAD_MOVED` is chained from the original exception** (`from exc`, fabric.py:288-292). The unit test asserts `__cause__` (test_w2_88_rv2.py:119, 141).
7. **The tests assert the stated behaviour, not accidents of the code.**
   - Each acceptance case first checks that the copies were written and staged when the stand-in acted (test_w2_88_rv2_undo.py:104-108).
   - Then it checks the code, HEAD, porcelain, index and reflog.
   - The S2 cases check the line holding only the header, a list item per path, and the one-line form.
8. **README "Run 5 revisions":** all 9 node ids it names exist as `def test_…` in test_w2_88_rv2_undo.py and test_w2_88_s2_plan.py.
9. **Scope of the commits:**
   - **af046b331 (engineer):** touches fabric.py, refactor_plan.py and tests/unit/adopt/test_w2_88_rv2.py, all in `allowed_paths`.
   - **3923bf846 (test designer):** touches tests/acceptance/W2-88/** only, the designer's own scope.
   - **Trailers:** both carry `Task: DAEO-2bdu` and `Implements: DEC-954, CAP-44.f, CAP-44.g, DEC-1098`, all in the ticket's `sources:`.

## Findings

**NC-1 (success-16; reached through success-3), blocker. When A9's record commit is refused, the work done in the repository during the run is still thrown away.**
- **What is wrong:** A9 commits its record through `run.finish` and W2-23's `project.commit` (stages.py:54). That commit runs the repository's hooks and signing. If git refuses it (exit ≠ 0), `project.commit` calls `project.restore`, which is `git reset --hard <head>` (project.py:144-145, 114). That happens before A9's new undo runs.
  - It throws away tracked edits made during the run.
  - It deletes from the tree a new file someone staged during the run.
  - The reflog gains `reset`.
  - The refusal comes back as `ADOPT_GIT_FAILED`.
- **Damage window:** the trigger is the commit, but the loss covers everything done during the run, which can last up to an hour.
- **Reproduce:** a planted repository with `core.hooksPath` naming a `pre-commit` that exits 1. Run `fabric.install`, then edit `a.md` and `git add new.md`, then `project.commit(root, "…A9…", {"governance/adoption/A9.md": …})`, routed through `fabric.undone` as `a9` does (`$TMPDIR/probe/cases3.py`).
  - Result: `ADOPT_GIT_FAILED`, `a.md` holds `alpha` again, `new.md` does not exist, and the reflog is `['reset: moving to 5232eb7…', 'commit (initial): init']`.
- **Behaviour it should have (RV2-1's own words):** "When A9 refuses or is interrupted after installing the kernel files", a refused record commit included:
  - no `git reset --hard`;
  - unstage only what A9 staged and wrote (the copies and its record);
  - delete only files whose bytes are still A9's;
  - a tracked file edited during the run keeps its edit;
  - a file staged during the run stays staged.
- **Options for the owner:**
  - (a) In fabric.py: A9 commits through its own step, whose failure runs `fabric.undo` and adds the record to `written`/`staged`.
  - (b) In project.py (in the ticket's `allowed_paths`): make `project.commit`'s failure path non-destructive. This changes W2-23's behaviour for every stage, against interface item 6's "unchanged".
  - (c) Record it as a row for W2-23 or Wave 3, with a rule stated in A9's output that the repository is not touched while A9 runs.
- Ordinary work: yes, because round 2 accepted work in the repository during a long A9 as ordinary. A record commit refused by a pre-commit hook is ordinary in repositories that use hooks (for example a whitespace or markdown hook on the four new `.md` copies that A1–A8 never staged), and so is a signing pinentry that times out after an hour-long run. No deliberate construction is needed.
- Consequence: loses work
- **What reverses it:**
  - a ruling that interface item 6 ("only A9's undo changes") takes the commit's own failure path out of RV2-1, which makes it a W2-23 row; or
  - a ruling that a record commit refused at A9, after A1–A8's commits passed the same hooks, is not ordinary work.

**NC-2 (success-16), minor. A Ctrl-C inside `install`, between its `git add` and its listing, leaves A9's copies staged.**
- **What is wrong:** `copies["staged"]` is filled only after the `ls-files` that follows `git add` (fabric.py:209-215). An exception in that gap reaches `undone` with `staged` empty. The undo then deletes the copies from the tree but leaves them in the index: status `AD` for all five. Where a copy replaced a tracked file, the status is `MM`, with A9's blob staged over the repository's own file.
- **Reproduce:** `$TMPDIR/probe/cases2.py`, I-ctrlc-during-ls-files and I-ctrlc-during-ls-files-replaced (a `KeyboardInterrupt` raised on that `ls-files`).
- **Behaviour it should have:** an interrupt at any point after A9's `git add` leaves no copy of A9's in the index. A path whose index entry is the blob of A9's own bytes counts as staged by A9.
- Ordinary work: no, because the gap is one `git ls-files` subprocess of milliseconds; a Ctrl-C has to land exactly there.
- Consequence: other (the copies are left in the index, nothing is lost; the user's next commit would take them).
- **What reverses it:** a ruling that a Ctrl-C at any instant is in scope regardless of window width.

## Notes, not findings
- **The engineer's second point (`project.commit` takes whatever is staged):** a file someone staged during the run goes into A9's adoption commit. Nothing is lost and the user can amend. Ordinary work: yes. Consequence: other. It belongs as a row with NC-1's option (a) or (b).
- **If the undo itself fails** (for example `update-index` meets an `index.lock` from a concurrent git), it raises `ADOPT_GIT_FAILED` chained to the original. The copies stay and it is still a refusal: not fail-open, and the same as before the change.
- **A Ctrl-C after A9's own `git commit` succeeds but before `a9` returns** would produce `HEAD_MOVED` naming A9's own commit as the new one, with the copies left committed. The window is milliseconds; nothing is lost and nothing fails open.
- **The engineer's statement that `project.py` is "not in this run's paths"** may be true of eng-4's brief. The ticket's `allowed_paths` do list `src/gov/adopt/project.py`.
- **Coverage gap:** no acceptance case covers a refused record commit (NC-1) or `install`'s own gap (NC-2). Both are beyond the interface's plant.

```verdict
{"kpis": [{"kpi": "success-2", "verdict": "pass", "findings": [{"id": "RV2-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-3", "verdict": "fail", "findings": [{"id": "NC-1", "scope": "in", "ordinary_work": "yes", "consequence": "loses work"}]}, {"kpi": "success-16", "verdict": "fail", "findings": [{"id": "RV2-1", "scope": "in", "ordinary_work": "yes", "consequence": "loses work"}, {"id": "NC-1", "scope": "in", "ordinary_work": "yes", "consequence": "loses work"}, {"id": "NC-2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}], "overall": "fail"}
```
