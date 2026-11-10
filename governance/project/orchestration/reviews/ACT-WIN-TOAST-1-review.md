# The review of ACT-WIN-TOAST-1 (DEC-1112 (3))

- Brief: `.gov-runtime/scratch/orchestrator/briefs/ACT-WIN-TOAST-1-review.md`; reviewer log `/home/usain/gov-os-worktrees/ACT-win-toast-review/.gov-runtime/scratch/lead/log/ACT-WIN-TOAST-1-review.json`.
- Round 1, verdict.py: READY (no blocking finding). F1 answered (class (b)); F2 and F3 fixed and re-rehearsed.

I ran no `apply` on the live tree and wrote nothing in any tree. Here is my record.

**Sandbox check (Step 0):** passed. (a) The write to `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-r30l` failed with `OSError: [Errno 30] Read-only file system` (exit 1). (b) `echo sandbox-trial | git hash-object -w --stdin` gave `1ae28402a109…` (exit 0), and `git update-index --refresh` exited 0.

**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` printed nothing.

- **task:** DAEO-r30l, the independent review of ACT-WIN-TOAST-1 (KPI `act-win-toast-1`).
- **decisions:** DEC-1104 (2), DEC-1112 (3), DEC-1106 (1), DEC-1027 B, DEC-1050, DEC-801, DEC-1010.
- **status:** DONE.
- **work_completed:**
  - Read the package, the five drafts, the live map, `select.py`, the merge queue's map reader, the fingerprint rules, `class-rules.yaml`, `act_class.py`, `operator_run.py` (G4, G6 and undo), `verdict.py`, the D-10 review and ACT-SELECT-FIXES-1 (the precedent).
  - Recomputed the hashes, compared the two maps, and placed every tracked path under both maps.
  - Ran the merge queue's reader and the operator agent's classifier on both maps.
  - Ran W2-66's live-map suite on a scratch clone holding the candidate.
  - Reproduced F2 and F3 in that clone, then deleted it.
- **files_changed:** none in any tree.
  - `git status --porcelain` of the review tree is empty.
  - The live map still hashes to `42e22dd70a05…`, and the live drafts folder has no `backup/`.
  - The only other writes: Step 0 (b) put one loose blob in the shared object store and refreshed the review tree's index, as the check requires.
- **evidence:**
  - Live map `42e22dd70a05…a665`, which matches the package's before hash. The last commit to change it is `8038e0ee6`.
  - Candidate `45e785d12b14…d348`, which matches the package's after hash.
  - HEAD is `98d503412b05` in both the review tree and the main tree.
  - W2-66's suite: 89 passed in 2.47 s.
  - Classifier vote: `('b', 'a change the row does not allow as (a)')`.
  - Scratch use peaked at 54 MB and 4,468 files and folders, all removed.
- **tests:**
  - Command: `HOME=<empty scratch> PYTHONUSERBASE=/home/usain/.local TMPDIR=<scratch> PYTHONPATH=<clone>/src bash …/heavy_slot.sh python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed --rootdir=<clone> --optin=lifted,breadth <clone>/tests/acceptance/W2-66/test_w2_66_live_test_map.py` gave 89 passed.
  - I ran one file, not a folder, so I added no `-m`/`-k` exclusion; that keeps the count comparable with the rehearsal's. The file only reads the map. Its one case with "real" in the name only reads the map and starts no model.
  - `PYTHONPATH` pointed at the clone's `src`, not the review tree's. The suite takes its root from its own file's location, so it had to run from the clone holding the candidate. Both are commit `98d503412b05`.
- **discoveries:**
  1. **The operator agent's G4 needs a different review form.** It reads `review.md` from the frozen bundle and needs `manifest_sha256`, `class`, `reviewer`, `reviewer_brief_sha256` and `time`, with every KPI marked pass (`operator_run.py:462-479`). This record uses verdict.py's form, as briefed. The drafts have no `manifest.json`, `before/` or `after/` yet.
  2. **The Write tool refused a file in my TMPDIR**, because it is outside the session's working folders. Per EMG-common's rule on false refusals, I ran the same read-only code inline with `python3 -B -c`, which writes no file.
  3. **This `apply.sh` dropped two guards** that ACT-SELECT-FIXES-1's script had (F2, F3).
  4. **The heavy slot works in this sandbox:** its lock files in `/tmp` exist and open read-only.
- **risks:**
  - Queued as (a), the ACT will stop at G6 (F1).
  - A hand-run undo after a later map ACT would silently drop that ACT's lines (F2).
- **lessons:**
  - Run the operator agent's classifier on an ACT's claimed class rather than judging by effect alone.
  - Diff a new `apply.sh` against the last reviewed one.
- **proposed_decisions:** none. F1's option (ii) is the owner's (O) choice, and I do not recommend it for one ACT.
- **unresolved:** whether the queue step builds the operator bundle and its operator-form review (discovery 1).
- **recommended_next_action:** READY per verdict.py.
  - Queue the ACT as (b): get the owner's `yes ACT-WIN-TOAST-1 <sha8>`, as DEC-1112 (3) reserves.
  - F2 and F3 ride along only if the bundle is rebuilt anyway (DEC-802); otherwise they are Wave 3 rows.

## Answers to the checks

**1. The change is exactly what the package says: yes.**
- The diff has one hunk. The `record_only` line becomes a three-line comment: the decision, the reason, and the old line kept. That is 3 lines added and 1 removed.
- Both maps are valid against the test-map schema. The top-level keys are the same and in the same order. Only `record_only` differs: 17 entries become 16, with exactly `win_toast.ps1` removed and the other 16 in their old order.
- Both sha256s match the package's.

**2. It only tightens: yes.**
- **What `select.py` does with it:** after the ACT, a change to `win_toast.ps1` is unplaced, so the close runs the full regression (`select.py:371-375`).
  - No `shared_core`, `record_only` or coupling pattern matches it.
  - The only ticket whose paths hold it is DAEO-sdxk (W2-00), and that ticket has no suite.
  - Before the ACT, the same change got a scoped run: `tests/unit`, `record_reading` and `every_close`.
- **Other readers of `record_only` also tighten:**
  - The merge queue's YAML-less reader reads 16 entries from the candidate, the same as the YAML list, so the comment is skipped. A head move by this file no longer gets the light rerun.
  - The code fingerprint now covers the file, so a change to it ends batch reuse.
- **No other path is affected:** of 3,857 tracked paths, only `win_toast.ps1` changes placement.
- **W2-66's suite stays green:** 89 passed at `98d503412b05`. The three commits since the rehearsal's `c906619646da` touch only a ticket file, a review record and `serial-only.txt`.
- **One limit:** "unplaced, so full" holds only while no ticket with a suite holds `tools/**`.

**3. `apply.sh`:**
- **`check` changes nothing:** it only hashes and prints. It also verifies the candidate against the after hash.
- **`apply` refuses a map in an unknown state:** yes, it needs the before hash; a missing map counts as unknown. But it does not re-check the candidate, and it exits 0 whatever state it leaves (F3).
- **`undo` restores byte for byte and checks the backup's hash:** yes. The hash it checks was written at apply time, and apply only runs from the before state, so it equals the before hash. But it does not check that the map is still as this ACT left it (F2).
- **It works only in its own tree:**
  - It finds the root from its own location, five folders up. It names no live path and does no `cd`.
  - In my clone it changed only the clone's map and its own backup.
  - The classifier finds no script hits.
- **Is class (a) right?** Not as the operator agent will apply it (F1).

**4. The operator's commit line:** `Role: owner` and `Task: decision-record` are both there, and the `-- governance/project/test-map.yaml` pathspec commits that file alone. It has no `Implements: DEC-1112`, although the precedent ACT commits carried one. Nothing checks this for `decision-record` commits, so it is traceability only, not a finding.

## Findings

Classification: F1 in/yes/other; F2 in/no/loses work; F3 in/no/fails open. None is in scope, reachable in ordinary work, and failing open or losing work, so no round is proposed.

**F1. The package routes the ACT as class (a), but the operator agent will classify it (b) and hold it for the owner's yes** (scope: in)
- **What was done:** the package says "Class: (a) by effect (DEC-1104 (2))", and the ACT goes to the queue as (a).
- **What happens:**
  - The approved rule table's `test-map` row makes any removal (b).
  - I ran the classifier on the live map and the candidate, and it votes (b).
  - G6 applies the highest of three votes: the classifier's, the package's claim and the reviewer's (`operator_run.py:501-523`).
  - Without the owner's yes line after the review, G6 refuses the ACT and sends the owner a P1 that the votes disagree.
  - DEC-1112 (3) also keeps the yes on class (b) ACTs with the owner.
- **What should happen:**
  - In effect the edit only tightens, which is DEC-1104 (2)'s test for (a); the table's row is cruder here and errs on the closed side.
  - So the package should name the class the operator will apply: (b). Either (i) queue it as (b) and ask the owner for the yes line, or (ii) the owner amends the row, an (O) change.
- Ordinary work: yes, because queuing the ACT as its package states is the next step.
- Consequence: other. It fails closed: a refusal, a P1 and a round trip to the owner. Nothing is applied and nothing is lost.
- **Reversed by:** an amended `test-map` row, or evidence that this ACT will not pass through G6.

**F2. `undo` writes the backup over whatever the map holds, and reports success** (scope: in)
- **What was done (reproduced in the clone):**
  - Ran `apply`, then added a line to the map, as a later ACT would.
  - `check` then said the map had changed (exit 1).
  - `undo` restored the backup anyway, printed "state before" and exited 0. The later line was gone, with no warning.
- **What should happen:** `undo` should refuse, or at least warn, unless the map is as this ACT left it. ACT-SELECT-FIXES-1's script warned.
- Ordinary work: no, because it needs this ACT undone by hand after another map change has landed. The operator agent's own undo refuses when a later ACT changed the same file (`operator_run.py:1607-1612`), and `git revert` is the package's other undo.
- Consequence: loses work.
- **Reversed by:** a flow where this script's undo is the normal rollback, run without the operator agent.

**F3. `apply` installs whatever the candidate holds, and reports success even when the result is not the reviewed map** (scope: in)
- **What was done (reproduced in the clone):** after `check`, I altered the candidate copy. `apply` installed it, printed "state unknown (de5979fe0007…)" and exited 0.
- **What should happen:** `apply` should check the candidate against the after hash before copying it, and fail unless the result is the applied state. ACT-SELECT-FIXES-1's script checked the result.
- Ordinary work: no, because in §3 `check` runs just before `apply`, and the operator agent applies from a frozen copy whose hashes it checks.
- Consequence: fails open.
- **Reversed by:** a flow that runs `apply` without `check` immediately before it, on a candidate that can change in between.

## Probed and found sound
- The diff, the hashes and schema validity, and that the YAML-less reader skips the comment.
- Every tracked path's placement, and that the selection, the merge queue and the fingerprints all move toward more testing.
- The suite, the absence of script hits, the root detection, and that `check` writes nothing.
- The authority:
  - DEC-1112 (3) is ACCEPTED and standing.
  - `deadman.py` runs the script through PowerShell (`deadman.py:41`, `deadman.py:94-95`).
  - The ACT now matches DEC-1027 B, which says the script is code. It drops D-4's entry made under DEC-1061 (D-10 review F2).

```verdict
{"kpis": [{"kpi": "act-win-toast-1", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "loses work"}, {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}]}
```

## Round 2

- Brief: `.gov-runtime/scratch/orchestrator/briefs/ACT-WIN-TOAST-1-review-r2.md`; reviewer log `/home/usain/gov-os-worktrees/ACT-win-toast-review/.gov-runtime/scratch/lead/log/ACT-WIN-TOAST-1-review-r2.json`. verdict.py: READY; round 1's F1-F3 closed; two new rows (F1 the by-hand form vs the operator agent's form, F2 apply.sh's tree rule) to settle before the queue.

# ACT-WIN-TOAST-1 review, round 2 of 2: READY by verdict.py

F2 and F3 are fixed: I reproduced both closed in my own scratch clone. Class (b) is right. One new problem, which doesn't block:
- The package says the ACT goes to the operator agent.
- But its §3 steps and its `apply.sh` are written for a by-hand run, and the agent would refuse them.

That fails closed (a refusal, nothing applied, nothing lost), so it is recorded as F1 and F2 below. I wrote nothing in any tree and never ran `apply` on the live map.

**Sandbox check (Step 0): passed.**
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-r30l` failed with `OSError: [Errno 30] Read-only file system` (exit 1).
- (b) `echo sandbox-trial | git hash-object -w --stdin` gave `1ae28402a109…` (exit 0), and `git update-index --refresh` exited 0.

**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` printed nothing.

- **task:** DAEO-r30l, round 2 of 2 of the independent review of ACT-WIN-TOAST-1 (KPI `act-win-toast-1`).
- **decisions:** DEC-1010, DEC-1104 (2) and (4), DEC-1106 (4), DEC-1112 (3), DEC-801, DEC-808.
- **status:** DONE.
- **work_completed:**
  - Read round 1's record, the changed `apply.sh`, `rehearse.sh`, `rehearsal.log` and the package.
  - Read how the operator agent runs an ACT:
    - `operator_run.py`: G1, G3, G4, G6, G7, G8, the apply and its commit;
    - its settings, `act_class.py`, the rule table, its reviewer brief and its own brief.
  - Compared the package with ACT-CLAUDE-COPIES-2 and ACT-DEADMAN-WAKE-1 (agent route) and ACT-SELECT-FIXES-1 (by hand).
  - Reproduced F2 and F3 in a scratch clone at `13f15785f91f`.
  - Ran the installed classifier, and a `check` the way G7 runs it, on a bundle planted in my TMPDIR. Then deleted all of it.
- **files_changed:** none in any tree.
  - The review tree's `git status --porcelain` is empty.
  - The live map still hashes `42e22dd70a05…`.
  - The live drafts are unchanged (`apply.sh` `1eb37b056cc6…`, candidate `45e785d12b14…`) and have no `backup/`.
  - The only other writes were Step 0 (b)'s loose blob and index refresh, and my TMPDIR scratch, now removed.
- **evidence:**
  - The live map matches the package's before hash; the candidate matches its after hash.
  - The review tree's HEAD is `98d503412b05`. The main tree and `w2/integrate` are at `13f15785f91f`; the five commits in between are W2-153's and none touches the map.
  - The classifier on the planted bundle gave `"class": "b"`, row `test-map`, "a change the row does not allow as (a)", and `hits: []`.
  - The G7-style `check`, run from outside the tree with the clone as the working folder, printed `sha256sum: /tmp/gov-launch-rnnkteee/governance/project/test-map.yaml: No such file or directory`, then `state unknown ()`, and exited 1.
  - Scratch use peaked at 193 MB and 10,576 files and folders; all removed.
- **tests:** I ran no pytest.
  - Round 1 and the re-run rehearsal at `13f15785f91f` each got 89 passed on W2-66's suite, and the candidate hasn't changed, so I didn't run it again.
  - So there is no `-m`/`-k` exclusion to report.
- **discoveries:**
  1. **There are two operators, and the package names both.**
     - The owner's operator is a console session that acts only on the owner's typed instructions (`~/gov-os-operator/CLAUDE.md`).
     - The operator agent is `operator_run.py`, gates G1 to G9, run from a queue.
  2. **The installed `operator_run.py` is older than the tracked one** (`41271992…` against `fe2e2f42…`). Everything I rely on works the same in both. `act_class.py` and `class-rules.yaml` are identical.
  3. **No copy of round 1's `apply.sh` survives**, so I couldn't diff it.
- **risks:**
  - Queued for the agent as written, the ACT is refused (F1, F2). That means a round trip, plus a P1 if it gets as far as G7.
  - Wrapped unchanged into a bundle and rehearsed the way the existing builder does it, the script would briefly change the live map rather than the clone's (F2).
- **lessons:**
  - Keep the reviewed script, or at least its hash, beside the drafts so the next round can diff it.
  - Check a package's route against the operator agent's code, not just its class.
- **proposed_decisions:** none. Choosing the route is the CTO's call (DEC-1104 (4), DEC-1112 (3)).
- **unresolved:** which route the CTO intends: by hand through the owner's operator, or the operator agent.
- **recommended_next_action:** READY per verdict.py.
  - I recommend route (i), by hand. Reword the class line to "(b): the owner's yes is the owner telling their operator to run §3". Optionally:
    - add `sha256sum $D/apply.sh` (expect `1eb37b056cc6…`) to §3;
    - update the commit named in §2.

    Everything §3 does is verified.
  - Take route (ii), the agent, only with a rebuilt bundle (see F2) and its own review under the operator's reviewer brief.
  - Confidence: high on the facts, medium on which route the CTO wants.

## Answers to the checks

**1. F1 to F3 are closed, and nothing else changed meaning: yes.**
- **F3 is closed; I reproduced both guards.**
  - First guard: after `check` passed, I put the record-only line back into the clone's candidate. `apply` printed "the candidate is not the reviewed one; nothing changed" and exited 1. It wrote no backup and left the map untouched.
  - Second guard: I needed a candidate that passes the hash check but changes before the copy lands. A `cp` stand-in on PATH altered the map only when it copied the candidate. `apply` printed "the result is not the reviewed map; restored the backup" and exited 1. The map hashed as before, and the clone was clean.
- **F2 is closed.**
  - After a normal `apply` (exit 0), I added a record-only line, as a later ACT would. `check` exited 1.
  - `undo` printed "the map is not as this ACT left it (unknown (0b1af2d1fd7a…)): a later change would be lost; nothing changed (use git revert)" and exited 1. The later line survived, and the map's hash didn't change.
  - With the map back in the applied state, `undo` restored it byte for byte: clean status, exit 0.
  - A second `undo` refused (exit 1) and changed nothing.
- **F1 is closed as round 1 asked.**
  - The package says (b) with the owner's yes, and the installed classifier votes (b) with no script hits.
  - The new "(use git revert)" text sits inside an `echo`, so the classifier doesn't count it as a git command.
- **Nothing else changed meaning.**
  - I compared the script line by line with round 1's record of how it behaved.
  - Today's script is that behaviour plus exactly three refusals:
    - the candidate checked before copying;
    - the result checked, with the backup restored if it is wrong;
    - `undo` refusing unless the map is in the applied state.
  - The usage comment for `undo` doesn't mention the new refusal. That is cosmetic.
- **The rehearsal's two new negative steps are right**, and the log matches what I reproduced.
  - The log's clone is today's `13f15785f91f`, but the package's §2 still names `c906619646da`.
  - §2 lists only the positive steps; the negative ones are in §4. Cosmetic.

**2. The class and the steps match what the operator agent will do: the class does, the steps don't.**
- **Class (b) is right.** G6 takes the highest of three votes: the code's, the package's claim and the review's. With all three at (b), the agent needs the owner's `yes ACT-WIN-TOAST-1 <sha8>` (DEC-1112 (3)).
- **The steps don't match the agent (F1, F2).** They are the by-hand route, and for that route they are right:
  - run in place in the main tree, the script finds the right map and all its guards work;
  - the commit line matches earlier by-hand ACTs (`Role: owner`).

## Findings

Classification: F1 in/yes/other; F2 in/yes/other. Neither fails open or loses work, so neither blocks. No round is proposed, and this was round 2 of 2.

**F1. The package sends the ACT to the operator agent but ships it in the by-hand form, which the agent cannot run** (scope: in)
- **What was done:**
  - The class line says "queued as (b): the owner's yes, then the operator agent".
  - The header says "For: the owner's operator".
  - §3 gives by-hand commands in the main tree, ending in a commit with `Task: decision-record` and `Role: owner`.
- **What happens if it is queued as the class line says:**
  - There is no bundle in the agent's queue folder and no manifest, so G1 refuses.
  - Without a manifest sha, the owner has no `yes ACT-WIN-TOAST-1 <sha8>` to type.
  - If these drafts are wrapped into a bundle as they are:
    - G3 refuses: the rehearsal log ends "== done", not "failures: 0".
    - G4 refuses: both review records use verdict.py's form, with no manifest sha, class, reviewer, brief sha or time.
    - G7 refuses: the script's `check` fails (F2).
  - Even when it runs, the agent commits with its own subject and trailers (`Role: operator`, `Act`, `Act-sha`, `Class`, `Review`, `Approved-by: owner`), never §3's commit line.
- **What should happen:** the package names one route.
  - (i) By hand: the owner tells their operator to run §3, and that instruction is the yes (DEC-1104 (4)). ACT-CLAUDE-COPIES-2 offers the same "or by hand" route.
  - (ii) The agent: a bundle with its manifest, a rehearsal ending "failures: 0", a review under the operator's reviewer brief, then the owner's yes with the manifest's sha8.
- Ordinary work: yes, because queuing the ACT as its class line says is the next step.
- Consequence: other. It fails closed: a refusal (a P1 to the owner only if it gets as far as G7) and a round trip. Nothing is applied and nothing is lost.
- **Reversed by:** the CTO confirming the ACT goes by hand (then only the class line's wording is off), or a builder that turns these drafts into the agent's form.

**F2. `apply.sh` changes the tree it sits in, not the tree it is run in, which is the opposite of the operator agent's path rule** (scope: in)
- **What was done (reproduced):**
  - I put the script in a bundle folder outside any tree.
  - I ran `check` with my clone as the working folder, as G7 and G8 run it.
  - It looked for the map under `/tmp/gov-launch-rnnkteee/`, printed "state unknown ()" and exited 1, although the clone's map was in the before state.
- **What happens:**
  - **From the agent's frozen copy** (`~/gov-os-operator/acts/ACT-WIN-TOAST-1-<sha12>/`), five folders up is `/`, so G7 refuses with "apply.sh check exited 1".
  - **From a bundle folder in the live scratch** (`.gov-runtime/scratch/orchestrator/acts/ACT-WIN-TOAST-1/`), five folders up is the live repository.
    - The existing builder rehearses by running the bundle's script from that folder, with a clone as the working folder.
    - This script would change the live map instead of the clone's, and leave a `backup/` inside the bundle.
    - The builder's own undo step and its "live files unchanged" step would restore it and flag it.
- **What should happen:**
  - Before going into any bundle, the script should change files under its working folder and read its own files from its own folder, as ACT-DEADMAN-WAKE-1's does, keeping the F2 and F3 guards.
  - For the by-hand route it is right as it stands.
- Ordinary work: yes, because copying the reviewed script unchanged into a bundle is the natural step if the agent route is taken.
- Consequence: other.
  - In the agent it fails closed at G7.
  - In a builder's rehearsal, the live map briefly holds the reviewed tightening and the undo puts it back. Nothing is lost and no test is skipped.
- Scope note: the lines that locate the repository haven't changed since round 1, but this revision's class line is what sends the script to the agent.
- **Reversed by:** evidence that the agent runs the script from a folder five levels inside the repository, or that the ACT goes by hand only.

## Probed and found sound
- The live map, candidate and clone hashes. The ACT's effect itself (the candidate is unchanged from round 1).
- The three new refusals, the normal apply and undo cycle, a second undo, and that a refused apply writes no backup.
- The classifier's vote, and that the new message text raises no script hit. The installed classifier and rule table are byte-identical to the tracked ones.
- The re-run rehearsal's clone commit, and that no commit since round 1 touches the map.

```verdict
{"kpis": [{"kpi": "act-win-toast-1", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```
