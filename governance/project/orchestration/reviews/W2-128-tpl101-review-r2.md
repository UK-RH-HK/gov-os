# The review of the kernel ticket template 1.0.1, round 2 (DEC-1121; W2-128, DAEO-t8mp), C3

- Brief: `.gov-runtime/scratch/orchestrator/briefs/W2-128-tpl101-review-r2.md`; branch `w2/W2-128-tpl101` at `0aa20ac0c`; template sha256 `bbfc068e58e2…`; reviewer (Opus, high, C3) log `/home/usain/gov-os-worktrees/W2-128-tpl101/.gov-runtime/scratch/lead/log/W2-128-tpl101-review-r2.json`
- verdict.py: (True, [])

# Round 2 review of the kernel ticket template 1.0.1 (DEC-1121; W2-128, DAEO-t8mp), C3

The verdict is **pass**. All three round-1 findings are resolved. I found one new problem, F4: it only makes the close refuse a ticket, so it doesn't block. The test run gave the same result as round 1: 355 passed and 1 failed, the known path-map fault. I wrote nothing in any tree.

**Sandbox check (step 0, launch_worker.sh / EMG-d4b): passed.**
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-128` was refused with `OSError: [Errno 30] Read-only file system`, as it should be.
- (b) `git hash-object -w --stdin` worked (`1ae28402a109`) and `git update-index --refresh` exited 0. These two git writes are step 0's own; I wrote nothing else.

**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` printed nothing, so no model server of mine is running.

- **task:** DAEO-t8mp (W2-128). Round 2 of the C3 review of the ticket template 1.0.1, covering the whole change `905b82a3b..0aa20ac0c`. I ran as the independent-auditor. The worktree's HEAD is `0aa20ac0c8f7`.
- **status:** DONE. Verdict **pass**.
- **work_completed:** Each round-1 finding judged; checks 1–5; one test run; read-only otherwise.
- **files_changed:** none. `git -C /home/usain/gov-os-worktrees/W2-128-tpl101 status --porcelain` is empty.
- **evidence:**
  - I recomputed the template's sha256: `bbfc068e58e20020483fa5019e4bfc88951f9b5b7b79c373185faf9a0231ab60`, which matches the brief.
  - Scratch folder (the sandbox's TMPDIR): `du -sh` 32K, `du -s --inodes` 12.
- **tests:** One run, the brief's exact command through `heavy_slot.sh`: **355 passed, 1 failed** in 80.6 s.
  - The one failure is `tests/acceptance/W1-08/test_w1_08_path_map.py::test_every_tracked_path_matches_exactly_one_namespace`. Five files under `governance/project/indep-briefs/sgx1/` belong to no namespace. That is the known fault ACT-PATHMAP-NS-2 fixes, and it is the same result as round 1.
  - The brief gave the command verbatim, so the EMG-d4b exclusions (`-m "not local_only" -k …`) were not added. Nothing was left out of the run.
- **discoveries:**
  - The kernel never tells an author that the evidence classes need `acceptance_tests.evidence` (F4).
  - `src/gov/util/role_paths.py:164` compares `class` case-sensitively, while the close lowercases it (`gates.py:53`). This has nothing to do with this revision, and every ticket in `.tickets/` uses lowercase. It is a note, not a finding.
- **risks:** none from this revision that fails open or loses work.
- **lessons:** Round 2 took the comment's list from the code's constants (`EVIDENCE_CLASSES`, `SPECIFICATION_CLASS`, the close's default), as round 1 recommended, and that resolved the fail-open.
- **proposed_decisions:** none.
- **unresolved:** none for this review.
- **recommended_next_action:**
  1. The CTO brings the hash `bbfc068e58e2…` to the owner for approval.
  2. After approval, the CTO adds the 1.0.1 line to `TEMPLATES-APPROVAL-1.md`, notes it in `docs/changes/W2-128-CIT-P.md`, and updates DECIDED-NOT-DONE row 108.
  3. F4 goes in as a recorded row. A one-line hint in the template's "Filling it in" section, in a later revision, would close it.

## Round-1 findings

- **F1 (fails open): resolved.** The comment now names `specification`, together with what the close does for it (checks its readiness record). It also names `research`, `audit`, `integration` and `coordination` as the classes the close judges on evidence. That is exactly `SPECIFICATION_CLASS` (`src/gov/close/gates.py:26`) and `EVIDENCE_CLASSES` (`gates.py:25`), as used at `src/gov/close/command.py:224-226,236`. A specification ticket filed from the template is now offered `specification`, so it gets the DEC-307 gate.
- **F2 (other): resolved.** `discovery` and `data` are gone. The "also in use" list matches `.tickets/*.md`. I recounted from `^class:`: test-revision about 15, skill 6, config 5, test-design 3, ops 3, template 3, schema 3, tool 2, role-definition 2, documentation 1.
- **F3 (other): resolved in the record.** Round 2's commit message corrects round 1's: the default came from W1-08's template (`079d73742`) and was removed in `a6c83d497`. Round 1's message is left as it is, since amending is not allowed.

## Checks

**1. Two changes.** `diff 905b82a3b 0aa20ac0c` touches one file, `template/governance/kernel/templates/ticket.md`: 4 insertions, 1 deletion.
- `version: 1.0.0` became `1.0.1`.
- A three-line `class: implementation` entry, with its comment, was added after `type` and before `role`.
- Nothing else changed in either commit, and the sha256 matches.

**2. The values.**
- The schema only requires `class` to be non-empty text: no enum, no pattern, and the field is optional (round 1 read the property). Every value in the comment is valid.
- `src/gov` keys on these:
  - `specification` and the four evidence classes, in the close;
  - `coordination`, for linked tests (`role_paths.py:162-164`, `:440`);
  - `audit`, which the readiness checker creates (`readiness/checker.py:53,222,231`);
  - a missing class, which closes as `implementation` (`command.py:298`).
- The comment names every one of these. `implementation` is the right default.
- `tasks/bridge.py:70` requires `class` on tasks derived from openspec. That is consistent with the template now carrying `class`.
- The planning, ready and guard code read no other value.
- Placement is right, and the comment starts at the same column as the others in the block.
  - The continuation lines are comment-only, which is valid YAML: the S10 and S19 tests parse the skeleton and pass.
  - Line 21 is a little longer than the `profile` line. That is a style nit, not a finding.
- No confusion with RUBRIC-2's criticality class. Every value is a kind of work, none looks like C0–C3, and the comment never mentions criticality. DEC-1120 takes criticality from the profile, the paths and the ACT's class, not from this field.

**3. Pins.**
- Only `governance/project/orchestration/packages/LIFT-1/TEMPLATES-APPROVAL-1.md:23` pins the ticket template, at 1.0.0 `fd97779d…`. That is correct for 1.0.0; the 1.0.1 line is the CTO's to add after the owner approves.
- Nothing pins the version or hash in `tests/acceptance/W2-128/`, `keys.yaml` or the facts file. `class:` is not a `{KEY}` placeholder.
- The W2-128 tests that read the template all pass: S1, S2's prose budget, S10, S14, S19 and its `commented or explained` check.

**4. The run:** 355 passed, 1 failed (see tests).

**5. Trailers.** `0aa20ac0c` has `Task: DAEO-t8mp`, `Implements: DEC-1121`, `Role: product-spec` and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. All four are present, and the Opus trailer is truthful (round 2 ran on Opus).

**Probed and found sound:**
- the diff's scope and the hash;
- each code line the commit message cites (`command.py:298,224-226,236`, `gates.py:25-26`, `role_paths.py:164,440`), each read in the worktree;
- the comment's list against the code and against the tickets in `.tickets/`;
- no conflict with the criticality class, and no pin that breaks;
- the trailers;
- the worktree left clean.

## Findings

**F4: the comment lists the evidence classes, but the skeleton has no `evidence:` key and nothing in the kernel says one is needed.**
- What happens: an author files a research, audit, integration or coordination ticket from the template. They pick the class from the comment and keep `acceptance_tests: {path: …}` as the skeleton shows it. `gov close` then refuses with `EVIDENCE_REFUSED`: "names no evidence record under acceptance_tests.evidence" (`gates.py:81-83`).
- What should happen: the template says that these classes name their evidence record under `acceptance_tests.evidence`.
- Decisions: DEC-1121, DEC-892 (W2-H045).
- Ordinary work: yes, because filing a research or audit ticket from the template is routine, and the comment now points authors at those classes.
- Consequence: other. The close fails closed, with a message that names the missing key. No gate is skipped and no work is lost.
- Reversal: this finding falls if the kernel (the template body, the planning skill or the schema's description) already tells authors to add `acceptance_tests.evidence` for these classes. I searched `template/governance/kernel/` and found no such line.
- scope: in. It concerns the classes this revision's comment introduces.

Classification: 1 finding. F4 is in scope, reachable in ordinary work, with consequence other, so it is a recorded row and not a blocker. I propose no further round (this was round 2 of 2).

```verdict
{"kpis": [{"kpi": "ticket-template-1-0-1", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```
