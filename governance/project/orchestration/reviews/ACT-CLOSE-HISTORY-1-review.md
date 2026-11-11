---
task: ACT-CLOSE-HISTORY-1
type: review
reviewer: independent-auditor (fresh session, round 1, read-only)
commit: bb9d29093fd5627f4945460b07bf26131e006665   # main tree HEAD when the re-run below was made (first read at 0c815d1e3)
pack_sha256: none given; brief sha256 3e99ceae76fceed9b52fafc5f4b4931bce2b1c599555ed663154c3a9669e83f4
inputs_sha256:
  ACT-CLOSE-HISTORY-1.md: d2e571fd8a6bdb29cf68f58bece1216f35b69bfc85d5649cf39bf793a0282cc2
  path-map-edit.diff: 176bdf6829f2ba8d89d3d0e05cfd0762275873f40cb55575367b00e07c340ea9
  DEC-1127-draft.md: 7661db61e041be40fbd4065b4297d2617434cfcd94e780b11e4b63daea4179ee
  rehearse.sh: 440e324686dff6d224ca72743a48e59da0f9ac5bb9c7ef897659c0845d223988
decisions: [DEC-734, DEC-757, DEC-762, DEC-868, DEC-906, DEC-923, DEC-953, DEC-1052, DEC-1061, DEC-1057, DEC-1123, DEC-1125, DEC-1126, DEC-1128, DEC-137, DEC-757, DEC-801, DEC-1010, DEC-105]
verdict: READY WITH FIXES
---

# Independent review: ACT-CLOSE-HISTORY-1 and DEC-1127 (PROPOSED)

**Classification:** 1 blocking finding (F1: in scope, ordinary work, fails open), 8 recorded rows (F2 to F9: other or
fails closed). **Recommendation:** READY WITH FIXES. Fix F1 before the owner's commit. Correct F2, F5 and F6 in the
package the owner reads. F3, F4, F7, F8 and F9 are corrections and rows.

## Is this a guard rule (DEC-1128 (2))?
No. No code of the guard or the hooks reads `accepted_history`, `load_sensitive` or `acceptance_exemptions`. Their only
readers are `gov close` (`src/gov/close/{command,gates,history,ratchet}.py`, the plugin `gov_close_results.py`) and the
product-traceability report (`src/gov/close/traceability.py`). The edit loosens what the close refuses and adds no
refusal. Item (4) of the draft is a working practice, and no hook or guard enforces it (F8). DEC-1128 (2)'s 100 % bar
does not apply.

## What I probed and found sound
- **The 18 merges (check 1).** I checked them on a fresh clone at `bb9d29093`. All 18 are two-parent merges with no `Task:`,
  `Role:` or `Implements:` trailer, and all are reachable from `w2/integrate`. In **17 of them the merge has no change of
  its own**: git's own merge of the two parents gives exactly the commit's tree. **`ffbf0392d236`** is the one with a
  conflict, in `src/gov/retrieval/retrieve.py`. It was resolved by keeping both sides' docstring lines. Its combined diff
  holds no line that is in neither parent, so it has no line of its own. None of the 18 carries real work of its own.
  The ticket commits they brought in stay in each ticket's range and are still judged one by one. `decision_records`
  takes out only the merge commit itself. So listing them loses no work and passes no unmeasured change.
- **`08c31e7ffee0`.** Its full subject ends "(not for merge)", yet it reached integrate through W2-96-d10b. It adds
  nothing of its own, so accepting it is harmless. It is a trace of a process slip, noted in F7.
- **The W1-19 `load_sensitive` entry.** The whole file `tests/acceptance/W1-19/test_w1_19_real_models.py` is routed to
  `nightly` in `tests/acceptance/serial-only.txt`, so no close runs it. Even if a close ran it, a counted entry only
  sends a red to be run again alone, and a red that fails alone refuses (`LOAD_SENSITIVE_FAILED_ALONE`). The entry
  cannot hide a red; it fails closed. The draft's text names both the file and the test name as whole words, which is
  the ratchet's R-2 rule. The owner's commit, with `Role: owner` in its final trailer block, is the commit that "adds"
  the `(test, DEC-1127)` pair, which is R-3. `fixed_by: W2-155` is DEC-1125 (1)'s performance ticket (`DAEO-ar89`).
- **The three re-pointed exemptions.** W1-01 reads only whether `decision` has the form `DEC-<n>`
  (`w1_01_support.py:342`), so W1-01's rule does not change. In the close, `owner_listed` now takes these three commits
  out of the work-without-a-task check, but none of them can trigger that check anyway: `c9a086786444` carries
  `Task: decision-record` and `Role: owner`, `ab169d051b82` carries `Task: DAEO-0pyc`, and `15952bbfa576` carries
  `Task: DAEO-sdxk`. Nothing new is cleared in any lift ticket's range.
- **Order of the gates.** I checked `run()` in `command.py`. The probe, trailer, accepted-history, unmeasured-work and
  ratchet checks all run before the tests and are uncounted (DEC-868 (3)). The containment check comes after the
  pre-close gate and its refusal is counted. The package describes this correctly, and its warning not to run
  `gov close` on W2-126 and W2-92 is right. A `gov close` of W2-96 would stop at the uncounted probe gate first.
- **The rehearsal (check 2).** I repeated its steps on my own clone of `w2/integrate` at `bb9d29093` (three register
  commits after the package's `8c18fa300`, all of them record-only and carrying a task). Results:
  - Before and after, every ticket's findings match `rehearsal.log` exactly: 7/11/14/15/7/5/5/5, then 0 everywhere
    except W2-96's probe gate.
  - Containment is unchanged: W2-126 has 2 findings, W2-92 has 7 and W2-96 has 2.
  - The diff I regenerated has the same changed lines as the package's diff, and the regenerated draft is
    byte-identical to `DEC-1127-draft.md`.
  - The package's diff applies cleanly: 1 file, 45 insertions, 5 deletions. The YAML check prints exactly the line the
    ACT expects.
  - The lists check: `load_sensitive` 24 of 24 count, `accepted_history` 18 of 18 are accepted, and all 7
    `acceptance_exemptions` entries clear their commit.
  - I did not re-run W1-01's folder (the brief says no test suite). The package logs 54 passed.
- **Containment for W2-92 and W2-96, and W2-96's probe gate (check 4).** The package's account matches the code and the
  commits:
  - W2-92: six engineer commits of `docs/changes/W2-92-evidence.md`, a path outside the ticket's `allowed_paths`, and
    `5fc7681a1214`, a test designer's commit of `tests/conftest.py`.
  - W2-96: the commits `65fa76dc3cf2` and `6bcbbcdd5511` are inside W2-96's `allowed_paths` but were made in the test
    designer's role.
  - The probe gate: the independent-auditor commits `3f975a3e6ea5` and `efb8acb1b596` lie in W2-96's range, and
    `1905b29699a7` changes the ticket file plus another path after the probed commit `8f6e66a17572`.

## Findings

**F1: Re-running the survey before the owner's commit can turn real work that no ticket measured into accepted history.**
Step 2 of "Before the owner's commit" tells the CTO to run `rehearse.sh`, which rebuilds `entries.yaml`, the diff and
the DEC-1127 draft from the survey. The generator (`gen_entries.py`) takes **every** commit that a work-without-a-task
finding names. It does not check that the commit is a merge, or that the merge has no change of its own. Two kinds of
commit could therefore enter the list:
- a non-merge commit that changes a lift ticket's paths and has no trailer, or a mistyped `Task:`;
- a `Task: decision-record` commit that the decision-record rule does not cover, for example one that names a decision
  that is still PROPOSED, or that touches a path outside the records.

The regenerated decision text would still say "Each is a merge…", and the owner would sign it. The close then takes
that commit out "whatever it changes" (DEC-923 (2)), for every ticket, for good. The run also writes over the reviewed
`path-map-edit.diff` and `DEC-1127-draft.md` in place.

The order of the steps adds a second fault. DEC-1127 is committed in step 1, before the re-survey in step 2. A commit
found in step 2 is then not named by the committed decision, so its entry would be refused. That failure is closed, but
the run is broken: `insert_dec.py`'s check fails and the script, which has no `set -e`, carries on.
- Scope: in (check 1, "an entry that exempts a commit with real unreviewed work of its own"; check 5, the procedure).
- Ordinary work: yes, because the step is part of the ACT's own procedure, and slips in commit trailers are what
  produced these 18 commits in the first place.
- Consequence: fails open.
- Fix:
  - The generator keeps only two-parent merges whose tree equals git's own merge, or whose combined diff has no line of
    its own. Any other commit stops the run and goes to the owner by name.
  - The re-survey runs **before** DEC-1127 is committed.
  - The rebuilt files go to a new folder and are compared with the reviewed ones; any difference is reviewed again.
  - `set -e` in the script.
- What would reverse this: the generator already filters to merges with no change of their own, or the ACT forbids
  using rebuilt files without a new review. Neither is true in the files with the hashes above.

**F2: The owner is not told that the refusing gates were already lifted by an owner decision, nor that DEC-1127 (1)
brings back a list that an owner decision deleted.**
- DEC-1052 approved Q-8: trailers, `WORK_WITHOUT_TASK` and `accepted_history` "lifted as refusals", with
  `accepted_history` and `trailers_base` **deleted** from the path map. The deletion was made by `c5e9d9625` under
  DEC-1061 (9).
- `DECISIONS-IN-FORCE.md` (the "Lifted" section, DEC-953) lists "the work-without-a-task gate, containment and trailers
  as refusals, the ratchet lists and their owner commits, probe staleness" as lifted here.
- The pinned close still enforces them. The draft cites DEC-1052 only for Q-10 and calls `accepted_history` "a new
  list". It neither names Q-8 or DEC-1061 (9), nor says that it changes them.
- The ACT also says the repair ticket's KPI lines "cannot be met by a code fix". That is not accurate. Seventeen of the
  18 merges have no change of their own. A work-without-a-task check that treats such merges the way the trailer check
  already does (`adds_nothing`) would clear them for every ticket, now and in future.
- The owner also has an option the package leaves out: close all eight by DEC-953's practices, with `tk close` and a
  close record. Option B already does this for three of them.
- Scope: in (check 3, "anything the owner must be told").
- Ordinary work: yes, because the owner decides from the package as written.
- Consequence: other. No gate fails open; the owner's choice is not fully informed, and the register gains a decision
  that contradicts DEC-1052 Q-8 without a "Changes:" line.
- Fix:
  - The draft's Under or Changes line names DEC-1052 (Q-8) and DEC-1061 (9), with: "accepted_history re-added for the
    lift's closes until Q-8's lift lands in the close".
  - The ACT corrects "cannot be met by a code fix" and lists the merge-aware gate as part of option A.
  - The DEC-1128 (1) list of switched-off controls names "the close's trailer and work-without-a-task refusals:
    decided off (Q-8), still on in the code".
- What would reverse this: a later owner decision that restored these gates as refusals for the formal closes. I found
  none; DEC-1039 (4) asks for formal closes, not for these gates.

**F3: The package explains W2-126's containment findings wrongly.**
The package says the two merges `15c80ebb72b7` and `b32fdb80f5fc` have an own change "not git's own merge of their
parents". Both **are** git's own merge: the tree is equal and there is no conflict. The judgement refuses them for a
different reason. Each merge has **two merge bases**, and the containment check accepts a merge's change to a ticket
file or an acceptance test only where the merge has one base. In addition, the commits that brought those versions in
fail when judged alone. Examples are `816e86dd30ae` and `0922aa7646e6`, W2-54's acceptance-test revisions, refused with
"names a closed ticket, not before its close commit".

Option A as worded ("containment reads accepted_history") would not clear W2-126 unless those commits were also listed.
So the claim that A "clears all containment findings for every ticket" is not established.
- Scope: in (check 4).
- Ordinary work: yes (the owner sizes option A from this).
- Consequence: other.
- Fix: correct the row, and add to A "accept a merge's change where the merge has more than one base, when it equals
  git's own merge".
- What would reverse this: a judgement trace showing these merges refused for a change of their own.

**F4: Option B's change of W2-96 to the STANDARD profile is redundant and weakens a control.**
Under B, W2-96 closes by `tk close` anyway: its two containment findings remain, and a `tk close` runs no probe gate.
Re-baselining the profile therefore clears nothing. It edits a reviewed ticket file, which the package itself says
DEC-757 (6) forbids when it discusses W2-92's `allowed_paths`. It also turns off DEC-137's probe gate on a FULL ticket.
- Scope: in (check 4).
- Ordinary work: yes.
- Consequence: other.
- Fix: drop the profile change. W2-96 closes by `tk close`, naming its four passing probe records and the three
  probe-gate findings for the exit auditor.
- What would reverse this: a route in which W2-96 closes by `gov close`, the probe gate being the only thing left.

**F5: The rollback is not an exact command.**
The ACT says "`git revert <the owner's commit>` as the owner (`Role: owner` in the revert's trailers)". But `git revert`
takes no `--trailer` option. A plain revert has no `Role: owner` and no `Task:` on a path that only the owner may change
(class O), and the landing check would flag it.
- Scope: in (check 5).
- Ordinary work: yes.
- Consequence: other.
- Fix, as one line:
  `git revert --no-commit <sha> && git commit -m "Revert ACT-CLOSE-HISTORY-1 (DEC-1127)" --trailer "Task: decision-record" --trailer "Implements: DEC-1127" --trailer "Role: owner" -- governance/project/path-map.yaml`.
  It must be a single line, so that no half-done revert is left in the shared tree.
- What would reverse this: the ACT already gives an exact revert command with these trailers. It does not.

**F6: The owner's commit is six separate commands, typed in a tree where the CTO commits every few minutes.**
Four commits landed between 14:05 and 14:21. If the CTO runs `git commit -a` or `git add -A` between the owner's
`git apply` and `git commit`, the path-map change would be swept into a `Role: orchestrator` commit. Then the ratchet
refuses the W1-19 entry ("added without Role: owner"), and a non-owner commit has changed an owner-only path.
- Scope: in (check 5, "safe, one command").
- Ordinary work: yes, plausibly.
- Consequence: fails closed.
- Fix:
  - The CTO writes a stand-by note and holds its commits while the owner commits.
  - Apply and commit run as one chain:
    `git apply --check D && git apply D && git commit … -- governance/project/path-map.yaml`.
  - The YAML check and `git log -1` come after the commit.
- What would reverse this: a commit hold that is already part of the ACT. It is not.

**F7: The draft's wording.**
- The commit subjects quoted in item (1) contain other commit ids: `74f8dbea4761` and `f3c15908d`. Any later
  `accepted_history` or `acceptance_exemptions` entry that cites DEC-1127 for those commits would be accepted. That needs
  an owner commit on the path map. Ordinary work: no; a Wave 3 row.
- "Their work was merged and reviewed with the tickets that made it" can be replaced by a measured fact anyone can
  check: 17 equal git's own merge, and `ffbf0392d236` keeps both sides' lines with no line of its own.
- "Made before the trailer rule was kept" is ambiguous. R-12 (DEC-1057) required `Task:` on every commit from 11-03,
  and most of these merges are from 11-06 to 11-10. Say "made while the rule was not kept for merges".
- The Basis line names code, not the basis question that DEC-1052's standing practice asks every new rule to state.
- Scope: in (check 3).
- Ordinary work: no for the ids; yes for the wording.
- Consequence: other.
- Fix: cut ids out of the subject excerpts and state the measured fact.
- What would reverse this: none needed; this is wording.

**F8: Item (4), "merges carry `Task:` from now", has nothing that enforces it.**
It agrees with the "Merge Task trailer" practice and is wider than it: it covers merges into ticket branches as well as
merges into integrate. But the only git hook is `reference-transaction` (the store refresh and the commit freeze), and
`landing_check.py` only flags commits whose only `Task:` is DAEO-sdxk on control paths. Nothing refuses a merge without
a task. The item's remedy, "its own owner entry", spends the owner's time on every slip.
- Scope: in (check 3).
- Ordinary work: yes.
- Consequence: fails closed (a future slip refuses a close again).
- Fix: keep (4) as a practice and say it is not enforced. File the merge-aware work-without-a-task check (see F2) as a
  ticket after the lift, so that a clean merge never needs an entry.
- What would reverse this: a hook or guard rule that requires `Task:` on merges.

**F9: Leftovers from the rehearsal.**
`rehearse.sh` clones the whole repository **inside** the main tree (`drafts/lift-close-blockers/rehearsal/`). The folder
is ignored by git, but a full second copy sits in scratch, where search tools that ignore `.gitignore` may read it.
`rehearsal.log` also prints "diff: 0 files changed", while the diff is 1 file, 45 insertions and 5 deletions (my re-run).
- Scope: out.
- Ordinary work: yes.
- Consequence: other.
- Fix: delete `rehearsal/` after the closes, clone under /tmp, and correct the line in the log.
- What would reverse this: none needed.

## Options for what no edit clears (check 4): my recommendation
1. **For W2-122, W2-123 and D-10's three:** fix F1, then make the owner's commit, then close them with `gov close`. This
   is the first half of option C. Their tests and the pre-close gate were not surveyed, so the first counted refusal
   could still come from a test.
2. **For W2-126, W2-92 and W2-96:** take **B without the change of profile (F4)**. They close by `tk close`, named for
   the exit auditor, under DEC-953 (1)'s practices. An owner decision names the containment commits and W2-96's three
   probe-gate findings. Confidence: medium.
3. **After the lift, file A as one ticket**, re-scoped by F2 and F3, because these are false refusals the product would
   also hit:
   - a merge-aware work-without-a-task check;
   - containment accepting merges with more than one base that equal git's own merge;
   - the probe gate's reviewer-role refusal limited to commits that name the ticket.

```verdict
{"kpis": [
 {"kpi": "C1 the code: the edit clears exactly what it says; no entry clears real unreviewed work", "verdict": "pass", "findings": []},
 {"kpi": "C2 the rehearsal re-run on a fresh clone matches rehearsal.log", "verdict": "pass", "findings": [{"id": "F9", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "C3 the decision text: exact, in the register's form, item (4) consistent, nothing hidden", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F7", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F8", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "C4 what no edit clears and options A/B/C", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "C5 the commit command, its procedure and the rollback", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}
]}
```

Note on the block: F6 and F8 fail closed, and the block has no value for that, so both are recorded as "other". The
only blocking finding is F1.

Scratch: `/tmp/gov-os-emg-review-ch1/` (clone at `bb9d29093`, my copies of the package's scripts, `out/`). Nothing was
written in the main tree; `git status --porcelain` is empty.
