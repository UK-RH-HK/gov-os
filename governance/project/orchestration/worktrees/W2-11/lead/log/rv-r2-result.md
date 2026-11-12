I've finished reading. I'm writing up the return now: every ticket line passes and no finding blocks, so the record is a pass with six non-blocking rows.

task: Independent review, round 2, of the W2-11 CIT-P (`docs/changes/W2-11-CIT-P.md`, CAP-33) at head 646850506819, against ticket lines S1 to S16, F1, F2 and CAP-33
status: DONE: the verdict is pass on all 18 lines; six findings, none blocking (none is in scope, reachable in ordinary work, and fails open or loses work)
work_completed: Read the ticket, the CIT-P, the kernel diff 4e265aabe..646850506819 and its round-1 range, the four skills, `skill.md`, the role file and the revised W2-128, W2-142 and W2-11 tests; checked the `.rulesync` copies byte for byte; measured both skill bodies; read the lead's verify summary, its junit failures and `accept-r7.txt`; read DEC-1137, DEC-1112 (3), DEC-851, DEC-1052 and DEC-1057 in the register
files_changed: none
evidence: `git status --porcelain` was empty at the end. `body_tokens.py`: orchestration 9,981 chars = 2,496 tokens, OK; test-design 5,671 chars = 1,418 tokens, OK. `git diff --no-index` shows the kernel orchestration and test-design folders identical to `.rulesync/` and `template/.rulesync/`. The rewrite commits 9410f5e7e27b, 8d0873fcf, 83aab41fd carry `Role: independent-test-designer` and `Rewrite-Reason: DEC-866, DEC-981, DEC-1137; DEC-1112 (3) …`. The lead's suite: 4,646 tests, 13 failed (the 7 W2-11 copy cases and 6 W2-96 unit cases on signals and timeouts). `gov accept`: 186 passed, 7 failed, 1 skipped.
tests: none run (DEC-959 item 1); I read the lead's results only
discoveries: The anti-drift kit cites DEC-851's five places without DEC-1052's narrowing for templates (R1). The CIT-P's list of copies to regenerate leaves out discovery and retrieval (R2). The role file still teaches a per-round `gov checkpoint` on DEC-511, which DEC-1057 changed (R4).
risks: If the CTO's copies step regenerates only the four files the CIT-P lists, two copy cases stay red. That fails closed.
lessons: The CIT-P's figures go stale with each repair run; re-measure them at the head under review.
proposed_decisions: none (R1 to R6 are rows; R1's and R3's fixes can ride along at no extra round, DEC-802; confidence high)
unresolved: The CTO to confirm in one line that "pins" in P-W2-11-R6-2 (c) covers the section and unit halves of W2-128's two skill guards (R6)
recommended_next_action: The lead commits the record below as `docs/probes/DAEO-k7hz/CITP-REVIEW-r2.md`; R1 to R3 ride along if the ticket resumes, otherwise they land as rows

**Sandbox check:** (a) the write outside the worktree failed with `OSError: [Errno 30] Read-only file system`. (b) `git hash-object -w` worked (`1ae28402a109…`), and so did `git update-index --refresh`. `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-k7hz`; top level `/home/usain/gov-os-worktrees/W2-11`, branch `w2/W2-11`. All as expected.
**gov retrieve:** used once. It answered (DEC-511, "Changed by: DEC-1057"), so no second search; the register was then read by id.
guard_refusals: none
brief_gaps: The verdict block takes findings only per KPI line, so findings that rest on CAP-33 or DEC-1112 (3) and on no KPI line (R3, R6) have no place in it | the brief's record form | 5 minutes, estimated

````
---
type: probe
ticket: DAEO-k7hz
probed_commit: 6468505068196e55e7872692752d383a99610cce
reviewer: independent-auditor (fresh session)
verdict: pass
date: 2026-11-11
---
# CIT-P review, W2-11 round 2

## Scope
This reviews round 2 of W2-11's CIT-P (`docs/changes/W2-11-CIT-P.md`, status PROPOSED) for the combined K3 CIT-P (DEC-954 Q7), at the head above. That head comes after round 1's verified head `c9f99b28b88b`, the merge of `w2/integrate` (`4e265aabed5c`), the DEC-1137 restore, round 2's text and run r7's repairs.

What was read: W2-11's own diff `4e265aabe..HEAD` (30 files), the four kernel skills, `templates/skill.md`, `roles/orchestrator.md`, the revised tests of W2-11, W2-128 and W2-142 and their READMEs, and the lead's `verify/summary.txt`, `parallel.xml` and `accept-r7.txt`.

Nothing was re-run. Measuring used `body_tokens.py`. The judgement follows ADR-0001's threat model and DEC-1010.

## The ticket's lines (S1 to S16, F1, F2: met by what, or not)
- **S1** is met. `skills/test-design/SKILL.md`, "How much is enough": "2,980 test lines for 713 code lines is out of proportion; tests far larger than the change … are cut back to the minimum that shows each KPI line and each failure line (DEC-951 item 5)".
- **S2** is met. `skills/orchestration/SKILL.md`, Briefs: "Every return starts with the twelve fields … Any payload comes after them. Stop after two identical refusals and return (AR-6)". The detail is in `briefs-and-returns.md`, "The return".
- **S3** is met. The SKILL.md read rule: "Reads are open … except secrets and keys, the held-out material's contents (its file names may be seen), the counterpart's work on the same ticket and the hidden half of an evaluation set (DEC-820, DEC-525, DEC-1052)". The Decisions section: "the orchestrator's decision-record commit, never `Role: owner` (MR-6, DEC-861, DEC-862)". Both rules are stated in full in `briefs-and-returns.md`.
- **S4** is met. `briefs-and-returns.md`, "The exit audit's reading of MR-3 (DEC-430)", matches the audit skill's wording (`skills/audit/SKILL.md`: "The exit audit must state DEC-430 …"), the parallel work order included.
- **S5** is met as in round 1 (W2-L256, e.g. DEC-371 in place of DEC-183). No loose citation was found in the new text.
- **S6** is met in the sources:
  - no `LEAD_CHECKPOINT`;
  - "it does not stop for context" (DEC-250) and "A checkpoint is written at every handover (DEC-837 item 3)";
  - reads open;
  - "No fixed number of tickets in flight … (DEC-847)";
  - decision-record commits;
  - the role file's DEC-866 sentences (the held-out refusal "replaced" by DEC-820; the lead's return; "full window … checkpoint at every handover").

  The `.rulesync` and `template/.rulesync` copies are byte-identical. The `.claude/` copies are stale by design until the copies ACT (DEC-315). Outside this line, see R4.
- **S7** is met. `test-design/SKILL.md`, "Kinds and cost", and `test-kinds.md`: the six kinds, a run-time limit measured from the runner's per-test durations, no whole-tree copies, and repository-state tests declared.
- **S8** is met. `test_w2_11_brief_gaps.py` builds a brief today for each fixed gap. `gov accept` success-8: 11 passed, 1 skipped.
- **S9** is met. `templates/skill.md` carries:
  - front matter closed to `name`, `version`, `description` and `output`, with `metadata.version` as the one carried repeat (P-b);
  - "No other key stands. A permission field never stands … no `allowed-tools`, `permissions`, `paths`, `network`, `model` or `effort` (DEC-995, DEC-996)";
  - in the Never section: "This skill changes no role's reads or writes. Work that needs other writes goes back as a package for the role that holds them";
  - the sections in the KPI's order, the 150-line body, reference files one level deep, three scenarios first, and imports licence-checked.
- **S10** is met. `test-design/SKILL.md`: "The work order in parallel", "Red against the ticket's base", the four black-box techniques, the proportion rule, and "The README map" in the form `gov accept` reads.
- **S11** is met. `orchestration/integration-queue.md`, `nightly-sheriff.md` and `incident-response.md` are linked from the body. The `qa-review/` folder holds `SKILL.md` and `scenarios.md`.
- **S12** is met as re-scoped. Its first half's subject (`brief_gaps:` as the template's) was retired by DEC-1137 (1) into W2-128's `brief.md` return. Its second half is tagged Wave 3 (DEC-1083). No text is expected; the README maps no case, saying so.
- **S13** is met. `briefs-and-returns.md`, "The anti-drift kit": a fresh session every morning from a handover (checkpoint, RESUME HERE, the decisions in force); the digest loaded at start; every rule in its five places (DEC-851). See R1.
- **S14** is met. `briefs-and-returns.md`, "Scope control: a new ticket is a P1": the WBS ticket goes to the owner as a P1 with a recommendation "before it is filed"; a lead names the ticket it needs and never files one (DEC-974).
- **S16 (skill half, P-a)** is met. `briefs-and-returns.md`, "Approvals: the orchestrator's own allow list":
  - the allow list is read at session start, including the host's `.claude/` check;
  - each command is classified;
  - such a call is never chained;
  - by day, the owner is notified first, then the call runs;
  - inside `<quiet hours>` the call never runs and is queued for the morning package;
  - one scenario each for day, night and a chained command.
- **S15** is met. `test-design/SKILL.md`, "Kinds and cost": "A timing test measures the work under test: its process's CPU time, or its time against a quiet reference run beside it, never the wall time of a loaded machine, and at the same bound". The load-sensitive row in `test-kinds.md` is made consistent with it.
- **F1** is met:
  - No front-matter key from the permission list in any of the 13 kernel `SKILL.md` files, nor in the template (grep of the kernel; the template names them only in its writer's comment).
  - No step widens a role's writes in the new text.
  - The write-step half holds skills that declare `output` (P-W2-11-R6-1 (b)). No kernel skill declares one today, so on the real kernel the case guards new text only; the planted cases show the check. The CIT-P §7.1 "Not done, by design" records this.
- **F2** is met. The supersession cases stand, with the planted and clean files (`gov accept` failure-2: 7 passed). The one red supersession case is the stale `.claude/skills/orchestration/SKILL.md` copy, by design.

## Superseded rules, grants, repository-scoped text
- **Superseded rules (DEC-866)** in the four skills, `templates/skill.md` and their two `.rulesync` sources:
  - none of `LEAD_CHECKPOINT`, a context-limit stop, a listing refusal, a fixed ceiling, owner commits, or anything marked "SUPERSEDED by" or "Changed by";
  - "tests first" survives only in the vendored TDD skill's own table (not a work-order rule).
- **DEC-851** is cited in its unnarrowed form (R1).
- **The role file** carries two later-changed sentences outside DEC-866's (R4).
- **Grants:** each skill states that it grants nothing (CAP-24.b). The approvals section states "the settings and the host decide what needs approval". No permission field anywhere in the kernel skills.
- **Repository-scoped text:**
  - No W2 ticket id, `w2/` branch, `.gov-runtime` or `tools/` path appears in the orchestration, test-design, qa-review or audit folders, nor in `skill.md`.
  - Project values stand as placeholders (`<quiet hours>`, `<the approval queue>`, `<the decision register>`).
  - The test-design read rule now names "the integration branch" generically, not `w2/integrate`.
  - One exception: the heading "Followed by hand (Wave 2)" (R5).

## Other tickets' tests revised under P-W2-11-R6-2 (c)
- **`test_w2_128_round2a.py` / `round2b.py`:**
  - The read rule is found by `read_rule`, the one section whose heading names reading (not the README) or the work order, cut to its reading units. It may name the integration branch generically. The permitting sentence, the bar on this ticket's implementation, DEC-963, CAP-38.c and the absence of CAP-38.b and DEC-136 all still stand. Nothing is lowered.
  - The version case moves from "== 1.2.0" to "≥ one minor above integrate's base, semver, one version in `version` and `metadata.version` of the kernel skill and its template rulesync copy". That is the pin the decision names. The added equality check holds more than before.
  - The front-matter guards set aside `metadata` only when it holds `version` alone, equal to `version`; every other front-matter change still fails. This is what the decision allows.
  - **The section and unit halves of both skill guards** now read the skill at W2-128's own merge (`w2_128_merge`, found from history; it fails, never skips, if no such merge exists or the clone is shallow). They no longer read the current skill at all. My reading:
    - Before W2-11, these halves held every later ticket's text to the pre-W2-128 base, i.e. they acted as pins on later tickets.
    - Read at W2-128's merge, they keep exactly W2-128's claim (its own change touched only the named parts).
    - W2-128's positive cases (pointers to the kernel templates, no glob bar, F2's lines, CAP-38.c) still read the skill now, and the front matter is still read now.
    - So nothing W2-128 meant is lowered. The reading is sound in intent but goes past the decision's words ("pins, front-matter guards … and the placeholder"); see R6.
- **`test_w2_142_unchanged.py`:** a `metadata:` block holding only `version`, equal to the version line, is set aside. A new planted case shows that an unequal version, or a block holding another key (e.g. `allowed-tools`), still fails. This is within the decision.
- **F1's case in `test_w2_11_round2.py`:** a skill without `output` is no failure. One that declares it must name `none` or a path class, and its steps are held to it. A new planted case shows both. This is as P-W2-11-R6-1 (b) decides.
- **Trailers:** all three commits are by the independent test designer, with `Rewrite-Reason:`.

## The CIT-P against the diff
- **Evidence (§1, §7.2), change (§7.1), tests (§4, §7.2 and §7.3), options and rollback (§7.4), and what is open (§6, §7.5)** are present. Status is PROPOSED.
- **§7.1 matches the diff.** It covers:
  - `skill.md`'s front matter, writing rule and Never line;
  - the three new sections in `briefs-and-returns.md`;
  - the timing rule in test-design and `test-kinds.md`;
  - the r7 repairs ("except", the "(Wave 2)" heading, CAP-38.c, the description restored, "none of this ticket's implementation").

  It does not mention that discovery and retrieval gained `metadata.version` in the restore (§7 points to the restore commits).
- **Accuracy** is covered by R2 and R3: the copy list, stale figures, the version baseline, and the head's results.
- **Known and packaged, agreed:** the seven red `.claude/` copy cases until the copies ACT (DEC-315); the five `brief-*.md` pointers (DEC-1137); the role templates' refusals, record rule and stop, which belong to W2-175.

## Findings (each: id, what, where, scope in|out, Ordinary work: …, Consequence: …, blocks: yes|no)
- **R1:**
  - **What:** The anti-drift kit tells the orchestrator to write every rule into its five places, "any other brief template it affects" included, citing DEC-851. DEC-851 is marked "Changed by: DEC-1052 (item 1), DEC-1057". DEC-1052 narrowed it for templates: a line only where it changes what is done, one owner, product-spec writes and the CTO approves. The text teaches the unnarrowed rule (DEC-851, DEC-1052).
  - **Where:** `skills/orchestration/briefs-and-returns.md`, "The anti-drift kit", third bullet (and its two copies).
  - **Scope:** in (S13).
  - Ordinary work: yes, because an orchestrator recording a rule would write it into each brief template itself.
  - Consequence: other (template bloat and a bypassed template route; the guard still bounds writes).
  - **Blocks:** no.
  - **What would reverse it:** a register entry showing that DEC-1052's narrowing does not reach the kernel's templates, or a sentence elsewhere in the skill carrying it.
- **R2:**
  - **What:** The CIT-P's list of copies for the CTO to regenerate names four files. Two of the seven red copy cases are for `.claude/skills/discovery/SKILL.md` and `retrieval/SKILL.md`, whose copies still state `1.0.0` while their sources state `1.1.0` with `metadata.version`. A step done from the list alone leaves them stale.
  - **Where:** CIT-P §7.3 e.
  - **Scope:** out (the copies are the CTO's step, outside the ticket's paths).
  - Ordinary work: yes, because an operator follows the listed files.
  - Consequence: other (fails closed: the copy cases stay red).
  - **Blocks:** no.
  - **What would reverse it:** the copies ACT being defined as a full rulesync regeneration regardless of the list.
- **R3:**
  - **What:** The CIT-P's figures do not describe the head reviewed:
    - §7.2 gives 9,976 chars = 2,494 tokens and 5,623 = 1,406, where 9,981 = 2,496 and 5,671 = 1,418 are measured (§7.1 says 2,496);
    - the front matter's `round2_head: c96136eb62c8` is the pre-round-2 test commit;
    - §7.1 gives the versions as 1.3.0 → 1.4.0, but 1.3.0 never merged: integrate's 1.2.0 is the before;
    - §7.3 b gives only the pre-round-2 accept (99 passed, 7 failed, 1 skipped), not the head's (186, 7, 1);
    - the lead's suite (4,646 tests, 13 failed: the 7 copy cases and 6 W2-96 unit cases on signals and timeouts, in files W2-11 does not touch) is not stated.
  - **Where:** CIT-P front matter, §7.1, §7.2, §7.3.
  - **Scope:** out (CAP-33 accuracy; no KPI line).
  - Ordinary work: yes, because each repair run moves the figures.
  - Consequence: other.
  - **Blocks:** no.
  - **What would reverse it:** a CIT-P revision at this head carrying these figures.
- **R4:**
  - **What:** The role file's lead section still says "tests first by a fresh test designer … then a fresh implementer", where DEC-959 item 7 sets the parallel order. It says "It runs `gov checkpoint` at each round boundary of its ticket (DEC-511)", where DEC-511 is "Changed by: DEC-1057" (no committed record per round), against the skill's own Checkpoints line (DEC-511, DEC-1057; DEC-959). It says "from the matching brief template", where those are now pointers. These sentences are outside the DEC-866 sweep that W2-11 holds in this file (DEC-981; W2-33 holds the rest). §6 records "tests first" for W2-33, but not the DEC-511 line.
  - **Where:** `template/governance/kernel/roles/orchestrator.md`, "What a lead does" (and its two `subagents` copies).
  - **Scope:** out.
  - Ordinary work: yes, because a lead reading its role file would write a checkpoint record each round.
  - Consequence: other.
  - **Blocks:** no.
  - **What would reverse it:** W2-33's paths or KPI lines already holding these sentences.
- **R5:**
  - **What:** A kernel skill's heading names this repository's wave, "Followed by hand (Wave 2)" (DEC-539). It is integrate's own text, put back by r7 to satisfy W2-128's section guard. Since 83aab41fd that guard reads the sections at W2-128's merge, so the restore's reason has passed.
  - **Where:** `skills/orchestration/SKILL.md`, last heading (and copies).
  - **Scope:** out.
  - Ordinary work: yes, because an adopted project reads it.
  - Consequence: other.
  - **Blocks:** no.
  - **What would reverse it:** a decision keeping wave names in kernel skill headings.
- **R6:**
  - **What:** The section and unit halves of W2-128's two skill guards were moved to read W2-128's own merge. I judge that within the intent of P-W2-11-R6-2 (c) (they pinned later tickets' text; W2-128's claim and positive cases still stand). The decision's words, though, name only pins, front-matter guards and the placeholder (DEC-1112 (3), DEC-957 P2).
  - **Where:** `tests/acceptance/W2-128/test_w2_128_round2a.py`, the two `test_s11_guard_*` cases.
  - **Scope:** out.
  - Ordinary work: yes, because a later revision could cite this reading as precedent for wider ones.
  - Consequence: other.
  - **Blocks:** no.
  - **What would reverse it:** the CTO's line, in the ticket or the digest, that "pins" covers these halves (it would close the row), or one saying it does not (that would make this a lowering to undo).

Classification: six findings, all rows. None is in scope with ordinary work yes and fails open or loses work.

## What was sound
- **Copies and sizes:** the kernel files and both `.rulesync` copies are byte-identical, and both skill bodies are under their caps (2,496 and 1,418 tokens).
- **Nothing lost against integrate:**
  - every rule of integrate's orchestration skill survives in the body or in `briefs-and-returns.md`;
  - removals are compressions (e.g. the package's parts, now DEC-818's six parts in the reference file);
  - each change of rule is supersession-driven: the ceiling, LEAD_CHECKPOINT, the decision trailer, tests first.
- **Approvals section:** it is a method, not a grant, and names the host's `.claude/` check without widening any write.
- **Front matter and test revisions:** the closed front matter and its Never line are carried into the template only, as §7.1 states. The W2-142 and F1 revisions are tight, each with planted cases proving the check still fails what it should.
- **Lead's suite failures:** the six non-W2-11 failures in the lead's suite are W2-96 unit cases timing out on signals, in files this ticket does not change.
- **Worktree:** it was clean at the end.

## Verdict
pass

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": [{"id": "R5", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S6", "verdict": "pass", "findings": [{"id": "R2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "R4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S7", "verdict": "pass", "findings": []}, {"kpi": "S8", "verdict": "pass", "findings": []}, {"kpi": "S9", "verdict": "pass", "findings": []}, {"kpi": "S10", "verdict": "pass", "findings": []}, {"kpi": "S11", "verdict": "pass", "findings": []}, {"kpi": "S12", "verdict": "pass", "findings": []}, {"kpi": "S13", "verdict": "pass", "findings": [{"id": "R1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S14", "verdict": "pass", "findings": []}, {"kpi": "S15", "verdict": "pass", "findings": []}, {"kpi": "S16", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": [{"id": "R6", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "F2", "verdict": "pass", "findings": [{"id": "R3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```
(R3 rests on CAP-33 and R6 on DEC-1112 (3), not on a KPI line. They are placed under F2 and F1, the lines nearest them, so that they are counted; neither blocks.)
````