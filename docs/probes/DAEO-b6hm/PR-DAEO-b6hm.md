---
type: probe
task: DAEO-b6hm
reviewer_session: feb0b4a5-fff9-4bf6-a063-c7aeb0d4e74b
implementer_session: "3744d76e-6b0c-4aef-b9db-70d7c469b0da"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: e96abbef25975bb180235f0413730a4aaebfccde
---

# PR-DAEO-b6hm: probe of W2-77 (the nightly's clean-up removes only its own clone, by its exact path)

## The lead's note

- **Commissioned and judged** by the ticket lead (an orchestrator-role session in this ticket's worktree, DEC-137). The reviewer was a fresh `independent-auditor` session (`feb0b4a5-fff9-4bf6-a063-c7aeb0d4e74b`, 2026-10-29). It was started through `gov launch` under its OS sandbox, with the reading tools alone and at effort max, and was given the lead's design note as text. It wrote nothing. The lead's tripwire before and after its session shows no change in this worktree. In other trees only the heads of W2-05 and W2-61 moved, through their own sessions.
- **The implementer session** (engineer, through `gov launch`, sandboxed) was `3744d76e-6b0c-4aef-b9db-70d7c469b0da`, commit `e9b233772142`. The acceptance tests were written by `b1ce7fec-f768-4a63-9a0f-430e25ae5622` (independent test designer, sandboxed, effort xhigh), commit `7e03022cdd17`, and were red first: 13 failed and 11 passed on the base, each for the README's reason, as checked by the lead.
- **The lead's verification of the code at `e9b233772142`.** The probed head adds only the lead's checkpoint record. The checks ran after a full rebuild (exit 0, every store recreated), with `gov.__file__` in this worktree:
  - **`gov check`:** exit 0. Two checks were YELLOW: `core-decision-citations`, on older commits' citations, and `openspec-validate`, with nothing to validate. None was red.
  - **The full parallel run in the close's form:** 16,567 passed, 31 skipped and 1 failed in 1:18:07. The red is W2-54's green-here case: context-reproducibility passed its 600 s limit under load (row W2-L429).
  - **The serial-only list's entries alone:** 156 passed, 1 failed and 23 errors in 29:44. The failure is W1-19's warm p95 (0.623 s against 0.5 s). The errors are W1-46's live-session setup errors: the launched session ran its step without its `cd` (row W2-M364). All of these are on the owner's `load_sensitive` list, and they are re-run alone as the lead's return states.
- **Verdict: pass.** Classification (DEC-809): 0 findings "yes" with "fails open" or "loses work". F1 is no / other (a row). F2 is yes / other (a row). F3 is no / loses work, outside the change (git's own automatic gc after the batch's commits), and is a row for the Wave 3 hardening pass. The lead's judgement agrees with the reviewer's.

## Head probed

`w2/W2-77` at `e96abbef2597` (the lead's checkpoint), branched from `w2/integrate` at `23079f92a6fa`. The change is `7e03022cdd17` (the acceptance tests) and `e9b233772142` (the clean-up). Every run used the worktree's own `src/` (`gov.__file__` = `/home/usain/gov-os-worktrees/W2-77/src/gov/__init__.py`). The reviewer's session id is taken from the session's own result. The machine ran git 2.43.0 and Python 3.12.3.

## Method

- **Read:**
  - the ticket file (its KPI lines and allowed paths) and its card in `docs/plan/WAVE_2_WBS.md`;
  - row W2-M406, W2-68's probe F1 and W2-66's probe R8;
  - DEC-939 item 5, DEC-915 item 4 and DEC-866, with section 14's judgement rules;
  - the change against `w2/integrate`: the clean-up in `src/gov/close/nightly.py`, its builder tests, and the acceptance tests and README;
  - the batch's route (`_measure`, `_commit`, `run`), the git helper in `src/gov/close/repo.py`, and the close's `_started`.
  - `gov retrieve` was used once. Both facets answered "stale" and it returned nothing, so the named files were read directly.
- **Ran:**
  - `tests/acceptance/W2-77` with `tests/unit/close/test_nightly_cleanup.py`: 28 passed (24 and 4) in 165 s;
  - `tests/acceptance/W2-66/test_w2_66_nightly.py` with `tests/unit/close/test_nightly.py`: 7 passed in 32 s.
- **Probed** on temporary repositories built from scratch in the session's temporary folder. W2-77's and W2-68's acceptance support was imported, never copied.
  - **A. Whole nights.** One green night and one red night with its bisect, with three worktrees out of view for the whole night: a folder moved aside, a folder at mode 0, and a parent folder at mode 0. Beside them stood a visible worktree whose folder is also `tree`, and a stale registration.
    - The repository was set so that any automatic gc would run and prune at once: `gc.auto` 1, `gc.worktreePruneExpire` now, gc's background mode off, and three loose objects where git samples them.
    - The support's stand-in git logged every git call of the night.
    - One commit was run afterwards as the control.
  - **B. The clean-up called on its own** after a failed or partial removal:
    - a read-only folder inside the clone;
    - the clone's `.git` file deleted, or unreadable when the clone was added;
    - the entry already gone, or the folder already gone;
    - a locked clone whose entry is unknown;
    - `GIT_DIR` in the caller's environment naming another repository;
    - `GIT_INDEX_FILE` naming the main worktree's index;
    - another worktree whose folder is `tree` (entry `tree`), out of view, and an earlier dead clone (entry `tree1`), beside a locked clone (`tree2`);
    - the root itself a linked worktree whose folder is `tree`;
    - a temporary path through a symbolic link.
  - **C. Signals.** One night was ended by SIGTERM, and another by SIGINT, after its clone was added. Then the dead clone's folder was deleted and a second night was run.
  - **D. Bisects in progress.** A red night ran while the main worktree had a bisect in progress (no checkout) and another linked worktree had one with checkout.
  - **E. Two nights at once** on one repository, with another worktree called `tree` and a stale registration.
  - **F. The batch** (`python3 -m gov.close.batch run`, W2-68's fixture), with a worktree moved aside for the whole batch, under the same gc setting. Then the same with commits' automatic maintenance off.
  - **G. `git worktree add --detach --force`** at a path that holds a stale registration.
  - **On this repository, read only:** 28 registrations, the oldest `gitdir` file dated 2026-10-16; 1,569 loose objects; no gc, maintenance or worktree setting.

## Found sound

- **No prune.** There is no `git worktree prune` in `src/`.
  - The night's git calls are:
    - `rev-parse`, `merge-base` and `rev-list` against the project;
    - one `worktree add --detach --force <fresh path> <head>`;
    - the bisect's `start`, `run` and `reset` inside the clone;
    - one `worktree remove --force <that path>`.
  - Under the immediate-prune gc setting, neither the green night nor the red night started an automatic gc. Every worktree out of view kept its registration, its administrative folder and its staged index, and the stale registration stayed.
  - The control commit pruned at once, so the trap was live.
- **By its exact path.** In every probe the removal named only the clone and never removed another worktree.
- **The entry, never guessed.**
  - With another worktree holding `tree` and a dead clone holding `tree1`, the clone was `tree2`, and only `tree2` went.
  - Two nights at once took `tree1` and `tree2`, and each removed only its own.
- **The fallback** removed the clone's own entry, and nothing else, in each of these cases:
  - the clone's `.git` file deleted;
  - the clone locked;
  - `GIT_DIR` naming another repository (that repository's worktree untouched);
  - the root a linked worktree whose folder is `tree` (the root's own entry untouched);
  - a temporary path through a symbolic link.

  Where the entry was unknown (the `.git` file unreadable at the start) or not confirmed (its `gitdir` names something else, as in the builder test), nothing was removed. The failure was reported, with `entry: null` or `entry_removed: false`.
- **Other cases.**
  - The clone's folder already gone: git removes the registration, exits 0, and there is no `cleanup` field.
  - `GIT_INDEX_FILE` naming the main index: the main worktree's staged index is unchanged.
  - SIGINT: the clean-up runs, the clone is removed, and the interruption is kept.
- **The bisect.** It left the main worktree's bisect in progress and the other worktree's bisect unchanged (its log, `HEAD`, `refs/bisect` and `BISECT_HEAD`), and it found the culprit.
- **`add --force` at the start.** It replaces a registration only at exactly the fresh path. That would need a fresh temporary folder's random name to equal a dead clone's.
- **Nothing else changed.**
  - The diff touches only the clean-up, and adds the `cleanup` field when the removal fails. A missing space before `f"` in the record's path line is cosmetic.
  - The verdict, the exit code and the envelope are unchanged in the acceptance cases, in W2-66's nightly cases and in the probes.
  - The batch's record carries the night's `cleanup` field.

## Findings

### F1: A removal that git completes only in part is reported with the clone's entry "left in place" after git has removed it (low)

- **What was done.** A clone held a folder at mode 555 with a file inside it, and then the clean-up ran. Separately, the clone's entry was removed before the clean-up.
- **What happened.**
  - git's removal failed ("failed to delete ... Permission denied"), yet git still dropped the clone's registration and its administrative entry.
  - The record's `cleanup` said `entry_removed: false`, and the standard-error line said the entry was "left in place". Neither was true any more.
  - The clone's folder stayed in the temporary folder, unregistered, as on the base.
  - With the entry already gone before the clean-up, the record and the line used the same wording.
- **What should have happened.** The record and the line say what holds afterwards: the registration and the entry are gone, and the folder is left. The two sources read `entry_removed: false` differently:
  - the acceptance case `test_the_clone_s_own_entry_is_gone_or_the_record_says_it_is_not` reads it as "the entry is still there";
  - the design note's item 5 reads it as "the fallback did not remove it".
- `Ordinary work: no, because it needs a file or folder in the clone that the night's own process cannot delete (a test leaving a read-only folder in the tree it ran in, with its restore skipped); the night's runs keep their temporary files outside the tree.`
- `Consequence: other` (the failure is reported, not hidden; only the entry's state is misstated; nothing is lost and no other worktree is touched.)

### F2: A night ended by SIGTERM leaves its clone registered, with no line and no record, and later nights no longer sweep it (low)

- **What was done.** A night with a 12-second test was sent SIGTERM after its clone was added. The clone's folder was then deleted, as a temporary-folder clean-up would delete it, and a second night was run.
- **What happened.**
  - The exit was -15, with nothing on standard error and no record.
  - The clone stayed registered, with its entry (`tree`) and its folder.
  - After the second night (whose own clone was `tree1`, and was removed), the dead registration was still there, and prunable.
  - On the base, the kill leaves the same clone, but the next night's prune would have dropped its registration once the folder was gone.
  - With SIGINT, the clean-up runs.
- **What should have happened.** A night ended by SIGTERM cleans up and writes its line, as a night that ends in an exception does. Otherwise dead clone registrations pile up and are named nowhere. Clearing them by hand with a repo-wide prune would bring back the very risk this ticket removes.
- `Ordinary work: yes, because a long night or batch ended by a time limit, the end of the session that started it, or a restart of the machine is a plausible accident.`
- `Consequence: other` (the dead clone's registration, index and folder stay behind; no other worktree is touched and nothing is lost.)

### F3 (outside the change): The batch's own commits can drop a hidden worktree through git's automatic gc (low today)

- **What was done.** The batch ran on W2-68's fixture, with a second worktree holding a staged change moved aside for the whole batch, in a repository set so that git's automatic gc runs and prunes at once. Then the same was run with commits' automatic maintenance off. Probe A had run the night alone under the same setting.
- **What happened.**
  - The batch passed and closed its ticket, and the hidden worktree lost its registration, its administrative folder and its staged index.
  - With automatic maintenance off, it kept them.
  - The night alone kept every hidden worktree.
  - So the prune came from git's automatic maintenance after the batch's own `git commit`s (its run record, then the close), not from the nightly.
  - Under git's defaults, that maintenance prunes only registrations older than three months whose folder is out of view when it runs, and only once about 6,700 loose objects have built up. Every `git commit` of any session runs the same maintenance; probe A's control commit pruned in the same way.
- **What should have happened.** A worktree out of view keeps its registration, whatever commit runs meanwhile.
- `Ordinary work: no, because under git's defaults it needs a registration older than three months whose folder is out of view at the moment an automatic gc runs; this repository's oldest registration is from 2026-10-16, so none qualifies before mid-January 2027.`
- `Consequence: loses work` (the hidden worktree's index and its link to the repository.)
- **Routing.** A row for the Wave 3 hardening pass (DEC-801). It is not the nightly's code, it lies outside this ticket's allowed paths, and it does not stand in the way of switching on the batch. It becomes reachable from 2027-01-16 for the registrations made on 2026-10-16.

## Classification

- F1: ordinary work no, other. A row.
- F2: ordinary work yes, other. A row.
- F3: ordinary work no, loses work. Outside the change; a row for the Wave 3 hardening pass.

No finding is both ordinary work and fails open or loses work, so the probe passes.

## Notes for the lead and the auditor

- **`entry_removed`.** The design note and the acceptance case give it different meanings (F1). One meaning should be chosen and stated in the README. In no probe did either meaning hide a failure.
- **Not reproduced (feature-gated, DEC-803).** With git 2.48 or later and relative worktree paths switched on, the entry's `gitdir` file holds a relative path. The fallback's comparison then cannot confirm the entry, so nothing would be removed and the failure would be reported: it fails safe. This machine's git is 2.43.0, which has no such setting.
- **The removal's environment.** The removal runs with the caller's environment, unlike the git helper. The design note keeps that on purpose (W2-05's ground). With `GIT_DIR` naming another repository, the fallback still removed the right entry (probe B).
- **Not probed.** Two nights at the same head started within the same second share W2-66's record name and runtime folder. The probe staggered its two nights.
- **Machine and session.**
  - The untracked dot-files that `git status` shows at the worktree's root are the sandbox's placeholder devices.
  - There was no guard read refusal.
  - There were two permission refusals, both on removing the probe's temporary folder.
- **The probe's temporary folder.** `/tmp/gov-launch-independent-auditor-te84yja1/claude-1000/w277p` (102 MB, 7,695 files and folders) could not be removed. Its removal was refused twice, so it was not tried a third time (AR-6). At the end the whole temporary folder held 102 MB and 7,703 files and folders, inside the 3 GB and 150,000 share.
