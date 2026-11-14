Probe round 2 failed on one blocking finding, which goes to the owner once with options (DEC-1010). Round 1's three fixes hold. Step 0 passed, and nothing was written to any repository.

**Step 0 (EMG-d4b-launched.md):**
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-184` failed with `OSError: [Errno 30] Read-only file system`. The same happened under the id `DAEO-6f0s`. No file exists.
- (b) `echo sandbox-trial | git hash-object -w --stdin` returned `1ae28402a…` (exit 0), and `git update-index --refresh` exited 0.
- **ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing, at the start and at the end.

---

# Probe of DAEO-6f0s (W2-184), round 2: judgement fail

- **Head probed:** 89edff41ff0f7ae6734ba31af69b0a11b57394bf. `git rev-parse HEAD` matches it. `git status --porcelain` is empty at the start and at the end, and no bytecode cache in the tree is newer than this session's start.
- **Session:** independent-auditor, claude-opus-5-5, effort max. This is the FULL ticket's probe. My own launch record is d4de9d3f: `review_round: 2`, `model_source: promotion`, `effort_source: probe`. Fresh session; I wrote none of the audited files.
- **task:** DAEO-6f0s
- **decisions:** DEC-1120 (1)-(3), DEC-1167 (2), DEC-1126 (3), DEC-1010 (as widened by DEC-1131), DEC-839, DEC-803, DEC-801, DEC-808, DEC-809, DEC-959 item 7, DEC-820
- **What I read:**
  - The ticket, and DEC-1120, DEC-1119, DEC-1167, DEC-1126 (3) and DEC-1010.
  - Round 1's record, and the fix commits fb4144730 and e064e2dd5.
  - `git diff 06801fb31 89edff41f`: `criticality.py`, `role.py`, `launcher.py`, `criticality.yaml` and the change record.
  - `test_w2_184_r1_rows.py`, the acceptance support modules and the case names in S2, S4 and S5.
  - `launch_worker.sh`, and the kernel role files' launch lines.
- **What I ran** (no whole suite; fixtures under `$TMPDIR`; `HOME` set to an empty scratch folder):
  - **In-process, read-only, on the real trees** (worktree `src`):
    - `ticket_criticality` over all 248 tickets.
    - `_promotion` from `W2-184` and from `W2-184-tests`.
    - `read_by_criticality` on the real role files.
    - `_probe_record` over every real probe record.
  - **Read-only:** the shared launch-record folder (39 records), including this ticket's 11.
  - **Git history:** for every test-designer commit made after its ticket's first probe record, whether that record was in the commit's tree (38 tickets, 180 commits).
  - **Fixture probes**, built on W2-184's and W2-60a's acceptance support (stand-in CLI, open gate):
    - `p2.py`: a fixture repository with a ticket worktree and a tests worktree.
    - `p3.py`: a FULL ticket's reviews and resumes.
    - `p4.py`: `--plan`, refusals, and the real tables.
  - **Mutants**, in a `git archive` copy of the needed paths, run with the pinned interpreter and `-p no:cacheprovider -m "not local_only" -k "not real and not green_here and not time_limit and …"`:
    - (a) the hidden-set line deleted from the project's `criticality.yaml`;
    - (b) the round-3 refusal disabled.
- **Refusals:** 1. The guard refused a Bash call whose text named the evaluation sets' hidden-set paths as strings (an fnmatch check plus a ticket survey). DEC-820 (d), DEC-845, DEC-953 item 2. I did not respell it; F3 uses a neutral analogue instead.

## Round 1's findings, judged first

- **F1 (blocking): fixed.**
  - `governance/project/criticality.yaml:18` puts `fixtures/evaluation/*/hidden/*` in C3.
  - W2-93 (DAEO-6y0x) and W2-94 (DAEO-g87r) now resolve to C3.
  - Mutant (a): 10 of the 11 `r1_f1` cases fail. The one that passes is the guard case for this ticket's own paths.
- **F8 (rides along): fixed.**
  - Lines 13-15 add `.claude/settings.local.json`, `governance/project/secrets.yaml` and `governance/project/indep-walls/*`.
  - W2-149 (DAEO-52ku) now resolves to C3. The cases check each path alone and beside a probe-record path.
- **F2 (rides along): fixed.**
  - `src/gov/launch/launcher.py:698-703` refuses review round 3 or later without `--owner-named`, whatever the setting. The refusal names the round and DEC-1010, and also a repeated record when there is one.
  - p3: round 3 is refused with no option and with `--effort xhigh`. With the owner named it is accepted (round 3, Opus max, `probe`).
  - Mutant (b): 4 `r1_f2` cases fail.
- **F3-F7, F9 and F10:** unchanged by the fix; not re-raised.

## Findings

### F1 — S5 and F1 — a test designer's launch never sees the ticket's probe records, so on a promoted ticket it starts on the table's model (blocking)

- **What the KPIs and interface say:**
  - S5: "launches its next round on Opus …; a lower model is refused".
  - The F1 line names "a promotion not applied" as a failure.
  - Interface 5.3: the promotion applies "for every worker role launched on that ticket".
- **What the code does:** it reads probe records only under the launch root. `_probe_files` takes `root / docs/probes / <name>` (`launcher.py:489-497`), called from `_promotion(root, names)` (`launcher.py:639`). This is what 5.1 says ("of the launch root").
- **Why that misses a role:**
  - The kernel's work order keeps the test designer in its own tests worktree, merged into the ticket branch by the lead ("One writer per worktree", `template/governance/kernel/roles/independent-test-designer.md:11` and every other kernel role file).
  - `launch_worker.sh` launches it from there: `cd "$tree"`, then `gov launch` with that tree as root (`launch_worker.sh:55-57`, `W2=${W2%-tests}` at :97).
  - The lead commits probe records on the ticket branch. Nothing brings them into the tests tree.
  - Merging the ticket branch into the tests tree would hand the test designer the engineer's code (DEC-959 item 7).
- **Probe p2** (fixture: two git worktrees, the fail-open record committed on the ticket branch only):
  - Engineer, launched from the ticket worktree: `claude-opus-5-5`, high, `model_source: promotion`, `promotion: {"reason": "a fail-open finding", "record": "docs/probes/DAEO-p2aa/PR-round-1.md"}`.
  - Test designer, launched from the tests worktree: started on `claude-sonnet-5-5`, xhigh (the fixture's C2 entry), `model_source: by criticality`, **`promotion: null`**.
  - Test designer from the tests worktree with `-- --model claude-opus-5-5` (what `launch_worker.sh --promoted` sends): **refused**, "… not the session's model claude-sonnet-5-5 (the independent-test-designer's for criticality C2)". From that tree the promotion cannot be applied at all.
- **On the real trees** (read-only):
  - `_promotion` from `/home/usain/gov-os-worktrees/W2-184` gives `{"reason": "a fail-open finding", "record": "docs/probes/DAEO-6f0s/PR-DAEO-6f0s-round-1.md"}`.
  - From `/home/usain/gov-os-worktrees/W2-184-tests` it gives `None`. That branch holds no `docs/probes/DAEO-6f0s/`, and its tip 24bf5a363 is its merge base with the head.
- **It happened in this ticket's own fix round** (real launch records):
  - 4496a4ad: engineer, 02:17:18Z, root W2-184, `claude-opus-5-5`, `model_source: promotion`.
  - 8c8b3634: test designer for td-4, 02:18:59Z, root W2-184-tests, `claude-sonnet-5-5`.
  - That tests tree still runs pre-W2-184 code, so its record has none of the new keys. Once W2-184 lands, a tests tree runs this code and still has no records, which gives p2's result.
- **Also in W2-42a:**
  - Its round-1 record 62d86f0f8 holds a fail-open finding (F1, in scope, ordinary work yes).
  - Its td-2 batch, 00e0b93e2, was committed 18 minutes later in a tree without that record (62d86f0f8 is not its ancestor).
  - Across the history, 4 of 180 test-designer commits made after their ticket's first probe record had none in their tree: W2-184's td-4, W2-42a's td-2 and td-3, and W2-126's 741f9eddd. All four came after a review.
- **Why the cases miss it:** every S5 case plants its records in the one fixture project it launches from, including `test_s5_a_promotion_applies_to_every_worker_role_at_the_table_s_effort`. No case launches a role from a second checkout of the same repository.
- **What would reverse it:** evidence that every batch launched after a review runs from a tree that holds the ticket's probe records; or an owner reading that S5 binds only the roles launched in the ticket's own worktree.
- `Ordinary work: yes, because the kernel's own work order keeps the test designer in its own tests worktree while the lead commits the probe records on the ticket branch, and a fix round after a fail-open finding starts with a test-design batch launched from there (this ticket's td-4; W2-42a's td-2)`
- `Consequence: fails open` (the session starts on a model the rubric does not give: the table's Sonnet where S5's promotion gives Opus; nothing refuses it, the record says `promotion: null`, and a request for Opus from that tree is refused)
- `Scope: in` (S5; KPI F1, "a promotion not applied"; interface 5.3; the fix lies in `launcher.py`, inside the ticket's paths)

**For the owner (this is the last round, DEC-1010).**

Classification: F1 in scope, ordinary work yes, fails open (blocks). F2 and F4 are rows (ordinary work yes, other). F3 is a row (ordinary work no). F5 is out of scope.

| Option | What it does | Cost | Risk |
|---|---|---|---|
| **(a) Read the records where the ticket's sessions ran** | `_probe_files` also reads `docs/probes/<id>/` under each `root` named by this ticket's launch records in the shared folder (the ticket's worktree among them), merged by root-relative path. | One function in `launcher.py`, a test-design batch (a role launched from a second checkout), a fix batch, then a narrow check. | A tree holding a stale or renamed copy of a record may count it twice. The engineer's code stays out of the test designer's tree. |
| **(b) Fail closed** | Refuse a worker launch when the shared folder holds a fresh auditor launch on the ticket but the launch root holds none of its probe records, naming the missing folder. | Similar to (a). | A review not recorded under `docs/probes/` blocks every later launch on the ticket. Getting a record into a tests tree needs its own commit there. |
| **(c) Process only** | The lead brings the record's commit alone into the tests branch before any batch launched after a review, checked by `launch_worker.sh`. | No product change. | S5 holds only while the rule is kept; an adopted product needs the same rule. |
| **(d) Accept and narrow** | S5 and 5.3 come to mean "every worker role launched in the ticket's own worktree". | None now. | Test designers' fix-round batches stay on the table's model; a Wave 3 row. |

**Recommendation:** (a), with (c) as the stop-gap until it lands.

### F2 — S4 — resuming a resumed review counts as a new round (row)

- **Probe p3** (C2 FULL fixture ticket):
  - Round 1: round 1, Opus high.
  - Resume of round 1: still round 1, Opus high.
  - Resume of that resume: **review_round 2, Opus max, `effort_source: probe`**. Round 1's conversation continues as the probe.
  - After a fresh round 2 (round 2, Opus max), the same resume is refused: "review round 3 of DAEO-p3aa is refused: at most two review rounds (DEC-1010); its setting … repeats the review of session 9534766e…".
  - Resuming round 2 directly stays round 2.
- **Cause:** 6.1 leaves out only the record of the session being resumed (`launcher.py:575`). A resumed session's record names only its parent in `resumes`, so the original is still counted. Each resume forks a new session id, so a second follow-up resumes the fork. This is a sibling of round 1's F3.
- **Expected:** follow `resumes` back to the chain's fresh record and leave the whole chain out of the count.
- **What would reverse it:** a reading that a resume of a resume is a new review.
- `Ordinary work: yes, because a lead may resume a reviewer more than once (a follow-up on a follow-up), and each resume forks a new id`
- `Consequence: other` (it fails closed once round 2 exists; before that, a round-1 continuation gets the probe's max, more effort, not less)
- `Scope: in` (S4). Row.

### F3 — S1 — some path forms miss the C3 globs (row)

- **The matching:** the new hidden-set glob has its wildcard in the middle of the path. With fnmatch tried in both directions, two ticket path forms match it neither way:
  - one set's whole folder with `**` (`fixtures/evaluation/<set>/**`);
  - a folder with no trailing `/` or glob.
- **Neutral analogue** (same structure, nothing protected named): the rule `src/*/core/*` matches neither `src/app/**` nor `src/app/core`, in either direction. `src/app/core/**` and `src/**` do match.
- **Quoted entries:** the loader strips quotes only from a whole entry (`src/gov/util/tickets.py:36-38`). So a quoted entry with a comment tail keeps its leading quote after the tail is cut, and matches nothing.
- **Survey:** none of the 248 tickets uses these forms.
  - W2-93 and W2-94 name the hidden folder with `/**` and now resolve to C3.
  - No quoted entry carries a comment.
  - The one entry with neither a glob nor an extension, `template/governance/kernel/bin/tk`, is matched by the kernel glob anyway.
- **What would reverse it:** a planned ticket written in one of these forms.
- `Ordinary work: no, because no ticket uses these forms, and the hidden halves are kept under the sets root outside the tree (path map, line 619)`
- `Consequence: fails open` (such a ticket would resolve below C3)
- `Scope: in` (S1). Wave 3 row (for example: turn a folder path into `<path>/**`, and strip quotes after cutting the comment tail).

### F4 — S1 — the secrets filter resolves to C2 (row for the CTO)

- `src/gov/secrets/**` holds the pre-index secret filter and the secrets-indexing check (DEC-285 to DEC-290). It matches only `src/*`, so it resolves to C2.
- W1-16, W2-20, W2-43, W2-69, W2-71 and W2-107 resolve to C2. W1-15, W2-50 and W2-150 reach C3 only through another path beside it.
- DEC-1120 (1) gives C2 to "product code outside the controls" and does not name the filter; interface 1.5 does not name it either.
- **What would reverse it:** a CTO or owner reading that the filter is product code outside the controls.
- `Ordinary work: yes, because tickets on src/gov/secrets/** recur (nine so far)`
- `Consequence: other` (a reading; if the filter counts as a control, the effect is the same kind as round 1's F1)
- `Scope: in` (S1). Row.

### F5 — out of scope — an adopted repository with no `criticality.yaml` (my view, as the brief asks)

- **My view:** this is consistent with DEC-1167 (2). W2-184 is no W2-27 gate, and DEC-1126 (3)'s "apply now" became "after the copy starts".
- Routing an adopted product by RUBRIC-2 needs that product's own file. That is an entry criterion of the ticket that turns it on (DEC-803), not of this ticket.
- **One effect to note:** with no file, the floor and the max/`--reason` rule still apply. So in an adopted repository, a max chosen by the launch itself is refused until 7.2's `--reason` reaches the CLI. That fails closed.
- `Ordinary work: yes, because EXAMIN's copy launches with no file`
- `Consequence: other` (decided behaviour)
- `Scope: out`. Row.

### Interface 1.4 as amended (in scope): judged, no new path

- In this repository, `crit.exists(root)` is false only where the launch root's branch lacks the file.
- The code and the file land in the same merge. `launch_worker.sh` runs the tree's own code with that tree as root, and both worktrees of any ticket claimed after the land have the file.
- So with this code, the absent-file branch is reachable only through `LAUNCH_CODE_ROOT`, or a re-pinned `gov` run in a tree not yet merged. That is round 1's F7, which the fix did not change.
- A file that is present but malformed refuses (1.3), as checked.

### What I probed and found sound

- **Criticality matching:** the comment tail is cut; fnmatch works in both directions (`src/**` matches `src/gov/guard/*`); the highest class wins; the ticket's `class` is never read. The 248 tickets resolve to C3 104, C2 135, C1 9.
- **Table parser on the real kernel role files:** engineer and test designer give C3 Opus high, C2 and C1 Sonnet high, C0 Haiku low. qa-engineer's FULL form gives C2 Opus on FULL and Sonnet otherwise. Auditor, research and product-spec have no table.
- **Effort rules:** the floor, max/`--reason` and 3.2a behave as written. A max after `--` with no reason on an engineer is refused, with no record and no CLI call.
- **Model after `--`:** a different model is refused, naming both.
- **Trial on a promoted ticket:** refused, with no record and no CLI call.
- **`--plan`:** still prints the default line. In the fixture it printed `model claude-sonnet-5-5, effort medium` where C3's table says Opus high.
- **Lead launches:** not in the diff.
- **Real records:**
  - This session (d4de9d3f) has all nine keys: Opus max, `promotion` naming round 1's record, `effort_source: probe`, `review_round: 2`, `subagent_model` equal to the final model.
  - Round 1's record (0be7734a): Opus high, round 1.
- **Real probe records:** every `judgement` is `pass` (120) or `fail` (16).

## Per KPI line

- **S1: pass.**
  - Round 1's F1 is fixed and its cases catch the regression (mutant a). The table line, the file's form, the floor, max/`--reason` and 3.2a hold.
  - Amended 1.4 opens no new path; round 1's F7 stands as a row.
  - Rows: F3, F4. Out of scope: F5.
- **S2: pass.**
  - A model after `--` other than the resolved one is refused, naming both; the same model is recorded as `after --`.
  - Trials are judged field by field and recorded.
  - The subagent model is the final model (`launcher.py:741`; real record d4de9d3f).
  - Round 1's F4 is unchanged.
- **S3: pass.** The nine keys are always present, with their values and nulls. The cases assert them whole, and the real records show them.
- **S4: pass.**
  - Round 1 is Opus high; round 2 is the probe (Opus max, `probe`, no `--reason`).
  - The same setting twice is refused, and since the fix any round 3 or later is refused without `--owner-named` (p3, mutant b).
  - Max on any other review needs `--reason`.
  - Row: F2.
- **S5: fail.**
  - In one tree, the promotion works as written: fail-open checked first, two failed reviews, the record's path in sorted order, a lower model and a trial refused.
  - But a test designer launched from its own tests worktree (the kernel's work order) never sees the ticket's probe records. It starts on the table's model with `promotion: null`, and a request for Opus there is refused (F1).
- **F1: fail.** "A promotion not applied" occurs in ordinary work for the test designer (F1). Its other two cases hold: a model below its tier with no trial is refused, and an effort below the floor is refused.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S5", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]}, {"kpi": "F1", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]}]}
```

judgement: fail

---

task: DAEO-6f0s (W2-184), FULL review round 2, the probe (the last round, DEC-1010)

status: done. Judgement fail on one blocking finding (F1, on S5 and KPI F1). Round 1's F1, F8 and F2 are fixed and their cases catch regressions.

work_completed:
- Step 0 passed.
- Judged round 1's fixes first, then the whole ticket against S1-S5, F1 and the interface.
- Read the code and the cases.
- Ran in-process checks on the real trees and read the real launch records (both read-only).
- Surveyed the git history.
- Ran three fixture probes (p2, p3, p4) and two mutants in `$TMPDIR`.
- Re-ran no whole suite.

files_changed: none. No file of any repository was written: `git status --porcelain` is empty at 89edff41f, and no bytecode cache is newer than this session's start. Probes and mutants are only under `$TMPDIR`.

evidence:
- p2: the promotion seen from a ticket worktree and from its tests worktree.
- Real `_promotion`: W2-184 gives a promotion; W2-184-tests gives `None`.
- Real launch records 4496a4ad and 8c8b3634 (this ticket's fix round).
- W2-42a: 62d86f0f8 holds a fail-open finding; 00e0b93e2 was committed without that record in its tree.
- p3: resume chains and the F2 fix.
- p4: `--plan`, refusals leaving nothing, the real tables.
- Mutant (a): 10 of 11 cases fail. Mutant (b): 4 cases fail.
- All 248 tickets' classes; all real probe records' `judgement` values.

tests:
- No suite run.
- Mutant runs of `tests/acceptance/W2-184/test_w2_184_r1_rows.py` with the pinned interpreter (PYTHONUSERBASE set to the user base), `HOME` a scratch folder, `-p no:cacheprovider -m "not local_only" -k "not real and not green_here and not time_limit and r1_f1"` (and `r1_f2`).
  - Mutant (a): 10 failed, 1 passed.
  - Mutant (b): 4 failed, 7 passed.
- The exclusion terms left out nothing in that file. The 27 cases deselected in each run were the other groups' cases.

discoveries:
- The kernel's own "One writer per worktree" line guarantees that a test designer's launch root is a different tree from the one holding the probe records. Every promotion case uses a single root, so the cases cannot show this.
- This session's record shows the probe applied as specified (Opus max, `promotion`/`probe`, round 2).

risks:
- Until 7.2's CLI options land, `gov launch` cannot carry `--owner-named`. So a FULL ticket's third auditor launch, such as the narrow checks the CTO runs routinely (W2-42a, W2-60a, W2-185), is refused. Likewise a max the launch chooses itself, which needs `--reason`. Both fail closed.
- With this code, on a promoted ticket `launch_worker.sh` must pass `--promoted`, or its Sonnet rewrite is refused (fails closed).
- F1 is silent: `promotion: null` in the record is its only trace.

lessons: a launcher rule that reads ticket evidence from "the launch root" has to be checked against every tree the work order puts sessions in. Single-root fixtures cannot show that gap.

proposed_decisions:
- The owner package for F1: options (a) to (d); recommendation (a), with (c) as the stop-gap.
- Rows for the CTO: F2 (with round 1's F3), F3 (Wave 3), F4 (the secrets filter's class).

unresolved: F1 needs the owner's choice. My view on F5 is given: consistent with DEC-1167 (2).

recommended_next_action:
- The lead commits this record as `docs/probes/DAEO-6f0s/PR-DAEO-6f0s.md` and takes F1's package to the owner once (DEC-1010).
- Whatever the choice, land the 7.2 `command.py` package with W2-184 or right after it, so the round cap and `--reason` can be used from `gov launch`.
- Guard refusals: 1, counted and not respelled.