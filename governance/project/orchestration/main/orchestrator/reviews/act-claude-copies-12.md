# ACT-CLAUDE-COPIES-12: the ACT review, round 2 (OPERATOR-AGENT-1 §3, G4)

Reviewer: independent-auditor, a fresh read-only subagent of the Wave 2 CTO session. I am not the ACT's author, and I wrote none of W2-188's files. I worked under the operator's fixed reviewer brief (`~/gov-os-operator/install/reviewer-brief.md`). I re-measured its sha256, `e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a`, and found it as the reviewer-brief line in the install's `APPROVED`. I also applied `governance/project/briefs/JUDGEMENT.md`.
- **Manifest sha256:** `22865f2ae3130452222526bda66ecd9a65982f614b0471c60a7c83cae262fca7`. I re-hashed it, and it equals the last JSON line of `drafts/claude-copies-12/build-r2.out` (failures 0, branch head `790357f0215d`). Round 1's bundle (`d5c8c2e6…`) is void. Its `list.txt` and file bytes equal round 2's; only the rehearsal and the manifest changed.
- **Review bed (order 1):** `b1`, a fresh `--no-hardlinks` clone of `w2/integrate` at `41ab6597992d`, under my session scratchpad (`rv-c12-r2/`). `refs/heads/w2/W2-188` at `790357f0215d` was merged in one `--no-ff` commit.
  - The merge was clean: merge base `bf04ed69c893`, 17 files brought, none under `.claude/`.
  - A window bed, `b3`, is a clone of `b1` at the merge commit, before the copy.
- **Review bed (order 2):** `b2`, a second fresh clone at the same integrate head. The bundle was applied on plain integrate (check 2 red) and committed in the package's §4 by-hand form (`Task: DAEO-zlog`, `Role: owner`). Then `w2/W2-188` was merged `--no-ff`, and it was clean.
- **HOME and crontab:** HOME was planted at an empty folder for every apply, undo, check, portability and rulesync step. It was still empty after each. The pytest runs used a third planted HOME, which also stayed empty. `apply.sh` reads only `list.txt`, accepts only the root `repo`, and has no crontab or HOME step.
- **Pytest:** every run went through `heavy_slot.sh`, with `-p no:cacheprovider`, `PYTHONUSERBASE=/home/usain/.local` and TMPDIR inside the bed.
- **Heads:** integrate (`41ab6597992d`) and `w2/W2-188` (`790357f0215d`) did not move during the review.
  - The rehearsal used integrate `f2f28ed4ef40`. `git diff f2f28ed4e 41ab65979` over `.claude`, `.rulesync`, `template/.rulesync` and the kernel adopt skill is empty.
- **Refused calls: 1, a Bash read, and not an ACT matter.** An unscoped `git -C <bed> diff` (no path) was refused: "git cannot say whether a revision holds the hidden part". I did not repeat it. I read the diff of the one named path, `.claude/skills/adopt/SKILL.md`, and the `--stat` of `.claude/settings.json`, which are the forms the brief gives.
  - Refused reads: 0.
  - Nothing under the sets root, held-out material, secrets or `~/gov-os-workbench` was read.

task: ACT-CLAUDE-COPIES-12 (W2-188, DAEO-zlog)
decisions: DEC-315, DEC-1112 (3), DEC-1181 (1), DEC-1166 (4), DEC-1179, CAP-33, DEC-1104, DEC-1106, DEC-861, DEC-801, DEC-808, DEC-1010, DEC-1014, DEC-820

Classification: 0 blocking. F1 to F5 are rows (consequence other); none fails open or loses work.

## Per check
1. **Touched list, generation and path rule: PASS.**
   - **The bundle's files.**
     - `before/`, `after/`, `list.txt`, `apply.sh` and `rehearsal.log` each hash to their manifest values.
     - The bundle holds no file that is not listed.
     - `list.txt` equals `touched` (root `repo`, the one path, before `77faaa13…`, after `65d6abd9…`).
   - **The changed set.** In `b1`, `apply` changed exactly `.claude/skills/adopt/SKILL.md`, which was the only line in `git status --porcelain`. The file has mode 644, its git mode, and nothing changed in HOME.
   - **Earlier work.** The before-bytes `77faaa13…` are integrate's tracked copy, which W2-188 does not touch. `before/` holds them, so the undo loses nothing.
   - **Independent regeneration.** I ran rulesync 24.0.0 in place in the window bed `b1`, from its root `.rulesync/`, with the builder's GENERATE arguments and HOME planted.
     - `git status --porcelain` showed two files: `.claude/skills/adopt/SKILL.md` and `.claude/settings.json`.
     - The rendered adopt copy hashes to `65d6abd920ddb6180e734a124ea53b02a0c5386126d09490c231b87b9eb75dbc`, and `cmp` finds it byte-equal to the bundle's `after/`.
     - Its diff against the tracked copy is body-only: step 6 rewritten, the weekly-audit paragraph added, and DEC-1101, DEC-1125 and DEC-1179 added to the sources line. The front matter is unchanged.
     - `.claude/settings.json` is not this ACT's. Rulesync rewrites it in the same way on plain integrate (I ran it on `b2` before any apply): it drops the held-out deny (DEC-616), as in COPIES-5 to -11.
     - In order 2 (copy committed, then the merge), rulesync in place changed only `.claude/settings.json`. So the adopt rendering is order-independent.
   - **No `version`.** The copy's front matter keys are `name` and `description` (folded), with no top-level `version` and no `metadata.version`. That matches the tracked copy and COPIES-9's rendering. The kernel's `version: "1.1.0"` is dropped as rulesync does for every copy. My W2-11 run (241 passed, 1 skipped, landed) confirms that its version case leaves adopt out.
   - **The sources.** The three adopt sources are at `6a884cf1…9489` on the merged tree. That is the sha256 the owner approved in DEC-1181 (1) (ACCEPTED), and the CIT-P's `owner_approval:` line names it (`docs/changes/W2-188-CIT-P.md` at 790357f02, sha256 `0b7b023c…`, as the package states).
   - **Path rule.**
     - `apply.sh` is byte-identical to COPIES-6 to -11 (`84f6f595…`). It reaches its bundle through its own folder and writes only under `$PWD`.
     - Both checks are `sha256sum -c` over relative paths. Neither names a live path or HOME, and neither `cd`s.
     - `commands` is empty.
   - **The operator's gates.** I ran the draft's `operator_gates.py` with `python3 -B -I`, writing its output to my scratchpad. `validate_manifest`, `check_act` and `path_rule` pass, there are no hash mismatches and nothing unnamed, and `act_class` gives class `b`, row `agents-skills-kernel`, no hits. The install's `__pycache__` is unchanged. This equals `evidence/operator_gates.txt`.
2. **Undo: PASS.**
   - In `b1`, `undo` restored `77faaa13…`, and `git status --porcelain` was empty.
   - Portability then read the window's one `GENERATED_DIFFERS` on the adopt copy again, and `apply.sh check` passed.
   - The re-apply gave `65d6abd9…` again, with the same changed set.
   - The rehearsal log shows the undo, the re-apply, and the stage, commit, undo, commit sequence ending in an empty diff.
3. **Rehearsal: PASS.**
   - **The log is the run of this `apply.sh`.**
     - The builder writes `apply.sh` from COPIES-11's bytes after asserting that they are COPIES-9's too.
     - `build-r2.out` ends with the log's `failures: 0` and the manifest's JSON line.
   - **The window and landed runs.** The log's counts are in the evidence files. My own runs agree:
     - W2-188: 54 passed in the window (`b3`);
     - W2-188: 54 passed landed in order 1, committed in the operator's form (`b1`);
     - W2-188: 54 passed landed in order 2, by-hand form (`b2`);
     - W2-11: 241 passed, 1 skipped, landed.
   - Two rows, F2 and F4.
4. **Checks: PASS.**
   - **Check 1:**
     - exit 1 before the apply (one `FAILED`);
     - exit 0 after it (one `OK`), in both orders.
   - **Check 2:** exit 0 with three `OK` on the merged tree, before and after the apply.
   - **Plain integrate (`b2` before the merge):**
     - `apply.sh check` passes, but check 2 exits 1 with three `FAILED`.
     - I read the operator's G8 (`operator_run.py`, the dry run): it runs every manifest check after its dry-run apply and refuses on a red one. So a run queued before the hand merge is refused, the order is held, and it fails closed.
   - **After the apply:** `apply.sh check` exits 3 with `moved: .claude/skills/adopt/SKILL.md`, so a second run is refused at G7.
   - The exits match the manifest's `exit: 0` for both checks, and `count` is null.
5. **Class: (b).**
   - The operator's `act_class.classify` gives class `b`, row `agents-skills-kernel`.
   - The skill text governs sessions once it is loaded.
   - Nothing in it is the owner's (O) beyond the yes: no sudo, push, tag, Windows step or operator file, and the undo is tested. The by-hand route's `Role: owner` commit is the owner's own route (§4), not the operator's.
6. **Guard replay: not applicable.** No path-map or deny entry is added, so `replay_refused` is empty.

## The case the brief names: `test_f2_the_claude_copy_of_the_skill_equals_the_base`
- That case no longer exists at `790357f0215d`. The test designer's commit 1734f7422 (`Role: independent-test-designer`, `Task: DAEO-zlog`) replaced it with `test_f2_the_claude_copy_of_the_skill_equals_the_base_or_the_copies_acts_after_bytes`. The new case passes when the copy is the base's bytes or exactly sha256 `65d6abd9…dbc`, and fails on any other bytes.
- The same commit revised the commit case, `test_f2_no_commit_of_the_ticket_outside_the_test_designer_or_the_copies_act_touches_claude_or_tests`. A commit carrying `Task: DAEO-zlog` may now touch `.claude/` only with `Role: owner` and a subject naming `ACT-CLAUDE-COPIES-`.
- **Result:** this ACT does not turn either case red. Both PASSED in the window, in landed order 1 (operator form) and in landed order 2 (by-hand form), in my runs and in the rehearsal.
- **The tests were not changed by an implementer.** The revision is the test designer's (DEC-136, MR-3), merged by the lead (7604a3b0b).
- **Classification:** round 1's red is resolved; it is no finding in round 2. The excuse is tight (one exact hash, and a `Role: owner` commit an honest worker does not write, DEC-861), so it does not fail open. F5 below is the row it leaves.

## The package's §3 claim on the operator's commit form: confirmed
- `operator_run.py`'s `git_commit` writes the subject `<ACT>: applied by the operator agent, class (<cls>)` with the trailers `Role: operator`, `Act:`, `Act-sha:`, `Class:`, `Review:` and, for (b), `Approved-by:`. It writes no `Task:`.
- e437c799c, 0f11752ce and 10c0ca52b (COPIES-9 to -11) carry exactly that form.
- W2-188's commit case skips every commit that does not carry `Task: DAEO-zlog`, so it never reads the operator's commit. In `b1` I committed the apply in the operator's form, and the case passed.
- The `Role: owner` excuse is needed only for the by-hand route, which `b2` exercised, and the case passed there too.

## Findings (none blocks)
- **F1** (check 1, scope in): the manifest's `dec` does not name the approval of these bytes.
  - The manifest names DEC-315, DEC-1112 (3), DEC-1166 (4), DEC-1179 and CAP-33. DEC-1166 (4) is the owner's approval of W2-37's CIT-P, followed by a copies ACT: a precedent, not this ACT's authority.
  - DEC-1181 (1), the owner's `yes W2-188 adopt skill 6a884cf1` (ACCEPTED), is cited in the package (§0) but not in the manifest.
  - Separately, the CIT-P's own `status:` line still reads `PROPOSED: … the owner's approval … come before the merge` while its `owner_approval:` line is filled in. That is a record lag in W2-188, not in this ACT.
  - Ordinary work: yes, because a builder adapted from an earlier copies ACT keeps its `dec` list.
  - Consequence: other. The machinery holds the order: check 2 is red until the approved bytes are on integrate.
  - What would reverse it: the operator or the owner reading DEC-1166 (4) as the standing rule for every copies ACT after a hand merge, or a rebuilt manifest naming DEC-1181 (1).
- **F2** (check 3, scope in): the rehearsal's portability and rulesync runs did not plant HOME.
  - The builder plants HOME only in its apply, undo, check and commit steps.
  - Its portability runs and its rulesync generation inherit the builder's own HOME.
  - So the log's final line ("nothing written to the planted HOME") does not speak for them.
  - My own portability and rulesync runs, all with HOME planted, gave the same findings and the same bytes, and they left HOME empty. So the readings stand.
  - Ordinary work: yes, because a builder that passes its own environment to a helper is an easy slip.
  - Consequence: other.
  - What would reverse it: a portability or rulesync run under a planted HOME that gives other findings or bytes, or writes into HOME.
- **F3** (check 2, scope in): the by-hand undo in §5 gives no commit subject, and W2-188's commit case reads the subject.
  - §5 says to commit the undo "with `Role: owner`".
  - If that commit also carries `Task: DAEO-zlog` and a subject that does not name `ACT-CLAUDE-COPIES-`, W2-188's commit case counts it as a ticket commit touching `.claude/` and turns red.
  - **Reproduced** in `b2` (order 2, landed), on a throwaway branch. I ran `undo`, then committed with `Task: DAEO-zlog`, `Role: owner` and the subject "Undo the generated adopt copy (5)". The copies file then gave 1 failed, 10 passed: the commit case FAILED, and the copy case PASSED (base bytes).
  - The operator's own undo (`Role: operator`, no `Task:`) is not affected. The rehearsal's own by-hand undo subject, `ACT-CLAUDE-COPIES-12 undone`, is excused.
  - Ordinary work: yes, because the owner following §5 by hand could reuse §4's trailers with a plain subject.
  - Consequence: other. A red test fails closed, and the full rollback reverts the merge anyway.
  - What would reverse it: §5 giving a subject that names the ACT, or no `Task:` trailer on the undo commit.
- **F4** (check 3, scope in): the real run will apply on a later head than the one rehearsed.
  - The rehearsal used integrate `f2f28ed4ef40`, and I used `41ab6597992d`. The adopt paths are unchanged between them.
  - G7 (`apply.sh check`) and G8 (the checks) re-read the target and the three sources at run time.
  - Ordinary work: yes, because integrate moves between a bundle's build and its apply.
  - Consequence: other. A moved target or source fails closed at G7 or G8.
  - What would reverse it: any of the following on the head the operator sees after the hand merge:
    - the adopt copy not at `77faaa13…`;
    - a source not at `6a884cf1…`;
    - the merge no longer clean;
    - rulesync rendering other bytes from that head's root `.rulesync/`.
- **F5** (check 4, scope out: W2-188's test design, not this ACT): W2-188's copy case pins this ACT's after-bytes.
  - Once landed, any later legitimate re-rendering of the adopt copy turns W2-188's copy case red wherever that suite still runs. Examples are a later adopt-skill change and a rulesync upgrade that re-folds the front matter.
  - The base-pin cases of S4 already behave this way.
  - Ordinary work: yes, because the adopt skill and rulesync both change in ordinary work.
  - Consequence: other. It fails closed and calls for a test revision, never a silent pass.
  - What would reverse it: W2-188's suite dropping out of every gate after the ticket closes, or the owner treating the pin as intended (the copy must not change without a new ticket).

Probed and found sound:
- the apply's changed set (one file, mode kept, nothing in HOME);
- the before-bytes kept in `before/`, so nothing is lost;
- a fresh in-place rulesync rendering byte-equal to `after/` in both orders;
- no `version` in the copy's front matter;
- check 2 holding the order and failing closed on plain integrate through G8;
- G7's moved-target refusal after an apply;
- the undo restoring the before-bytes and the window's one finding;
- portability clearing in both orders;
- the revised F2 cases being the test designer's, tight, and green in both commit forms;
- the package's §3 statement on the operator's commit form.

```verdict
{"kpis": [{"kpi": "check 1", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "check 2", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "check 3", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "check 4", "verdict": "pass", "findings": [{"id": "F5", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "check 5", "verdict": "pass", "findings": []}, {"kpi": "check 6", "verdict": "pass", "findings": []}],
 "manifest_sha256": "22865f2ae3130452222526bda66ecd9a65982f614b0471c60a7c83cae262fca7",
 "class": "b",
 "reviewer": "independent-auditor, fresh read-only subagent of the Wave 2 CTO session; not the author",
 "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a",
 "time": "2026-11-14T17:48:30+00:00",
 "replay_refused": []}
```
