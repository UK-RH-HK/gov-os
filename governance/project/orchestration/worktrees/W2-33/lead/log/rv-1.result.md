Step 0, the sandbox check (launch_worker.sh): (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-lrre` failed with `OSError: [Errno 30] Read-only file system`, as it should, and no file exists. (b) `git hash-object -w --stdin` worked (blob `1ae28402a109…`) and `git update-index --refresh` exited 0. `GOV_TICKET=DAEO-lrre`. The `ps` check for ollama/llama-server shows nothing of mine.

task: DAEO-lrre (W2-33), review round 1, STANDARD, read-only probe of `3b3a90d74c3e0c5478f366453b07cb921c0c6f88`

status: DONE

work_completed: `git rev-parse HEAD` agrees with the brief and the tree was clean at the start and at the end. I read the ticket in full (S1–S9, F1, F2, `## Interface`), ROLES-SPEC-1 §3.0–3.10, §5, §6.2, §8 and §10, and DEC-957, DEC-959, DEC-1010 and DEC-1119/1120. I read all nine role files at HEAD and their diffs from `3df1ac2deb1b`, the acceptance folder (README, the support module, the four test files), W1-35's diff, `portability.py` (`compose`, `_kernel_findings`, `ROLE_SKILLS`), `launcher.ROLE_TEMPLATES`, the guard's `KNOWN_ROLES` and `install.cto_install`, the `qa-review` skill and RUBRIC-2-APPLY. I ran the W2-33 folder, the W1-35 file and the W2-153 sources and unit cases. I recomputed every sha256 in the CIT-P and ran the S6 planted brief as a probe.

files_changed: none (`git status --porcelain` is empty; the only write was step 0's blob in the object store, as the step requires).

evidence:
- All 9 kernel sha256 values before (`3df1ac2deb1b`) and after (`4c6a47d8c`), and the rulesync source's, equal the CIT-P's table (`docs/changes/W2-33-CIT-P.md:42-51`). HEAD equals `4c6a47d8c` for all ten files.
- `git diff --numstat` gives the same lines +/- as the CIT-P.
- `compose(root,'orchestrator') == template/.rulesync/subagents/orchestrator.md`: True (11658 bytes each).
- Its `claudecode.skills` is `['orchestration']`. The kernel file's Skills line is `orchestration, planning, checkpoint, change, retrieval`. They are not equal (R4).
- The guard's install rule (`src/gov/guard/install.py:323-354`, wired in `template/governance/kernel/hooks/pretooluse.py:261`) matches `orchestrator.md:22`, except the wording point in R6.

tests:
- `tests/acceptance/W2-33` through `heavy_slot.sh`: **96 passed in 0.39s**.
  - `/tmp/gov-w2-33-rv` could not be made (read-only), so TMPDIR was the sandbox's own.
  - The heavy slot printed "Read-only file system" for its own prio and wait-log files; that came from the sandbox, not the guard.
  - The exclusion left nothing out (the README says no case is local_only, real, green_here or time_limit).
- `tests/acceptance/W1-35/test_w1_35_orchestration.py` + `tests/acceptance/W2-153/test_w2_153_sources.py` + `tests/unit/adapters/test_w2_153_portability.py` through the heavy slot: **24 failed, 47 passed, 33 deselected**.
  - All W1-35 cases passed.
  - The 24 failures are W2-153's: the source body and fields cases for the six roles in `.rulesync` and `template/.rulesync` (all but the orchestrator's template copy), `test_s3_guard_the_check_finds_no_role_source_drift_in_this_repository` and the unit case `test_this_repositorys_sources_are_the_composition`.
- To reproduce R1, I exported the base tree with `git archive 3df1ac2deb1b` into `$TMPDIR` and ran the same W2-153 files there outside the heavy slot (0.5 s): **12 failed, 38 passed**.
  - All 12 failures are git-baseline artefacts of an export with no `.git` ("not a git repository").
  - The body, fields, drift-guard and composition cases pass at the base.
  - The export was then removed.
- One single-case unit run (`-k template_sources`, 0.14 s) also ran outside the heavy slot: 1 passed, 24 deselected.

discoveries:
- **The guard does not know two of the new role ids.** `qa-engineer` and `senior-engineer` are not in `KNOWN_ROLES` (`src/gov/guard/decide.py:18-23`), so a session under either id is refused every call (`decide.py:1162-1163`). This fails closed. Both files describe the guard as it will be after W2-60b, which CIT-P §4 says.
- **The C0 value is a reading, not the table.** C0 is "Haiku low" for engineer, test designer and QA. It rests on RUBRIC-2-APPLY.md:23 ("C0 Haiku or deterministic") and DEC-1120 (3) ("low or medium for C0"). DEC-1120 (2) itself says "Engineers: Sonnet, high" for every class but C3. CIT-P §3 discloses this, so it is for the owner to confirm at approval.
- **Two skill names are stand-ins.** The lead and the Senior Engineer name `orchestration` in place of ROLES-SPEC-1's `ticket-loop` and `stream-orchestration`, which do not exist yet (CIT-P §3 says so). `qa-engineer.md` names only `qa-review` (no `retrieval`).
- **The Interface numbers the generation-drift clause F1, but it is in F2.** The Interface says "F1's 'the generation check names it as drifted' → W2-153". In the ticket's failure list that clause is the second line (F2); F1 is the old install wording.
- **W1-33's agent roster case is pinned at six.** `tests/acceptance/W1-33/test_w1_33_agent_definitions.py:86-90` pins `.claude/agents/` at six definitions plus research. It will need revising when the copies ACT adds the three new roles. The CIT-P does not mention it.

risks:
- The land: once this merges, W2-153's 24 repository cases are red until the copies ACT, and the CIT-P does not list them (R1).
- The generated orchestrator agent opens with the ticket-lead template (R4).

lessons:
- A CIT-P's list of the reds a change brings should be built by running every test that reads the changed files on the real tree (here `grep -rl` over `tests/` for the roles folder and `portability`), not from memory.

proposed_decisions: none

unresolved: none

recommended_next_action:
- Land as is: no finding blocks.
- Before the owner approves, the lead corrects CIT-P §4 to name the W2-153 reds (R1); this is a records commit, with no round.
- R2–R7 go in as recorded rows.
- The CTO pairs the copies ACT, together with W2-153's `ROLE_TEMPLATES` and `ROLE_SKILLS` (R4), with the land.

---

**Findings** (in scope = the ticket's KPI lines or Interface items; DEC-801 and DEC-808 judgement lines on each)

**R1: CIT-P §4 leaves out reds the merge brings.** `docs/changes/W2-33-CIT-P.md:75-79`. Severity medium. In scope (the Interface's CIT-P item), not blocking.
- What happens: the CIT-P tells the owner that until the copies ACT only W1-33's kernel-equals-generated cases and W1-38's field agreement stay red. On HEAD, 23 W2-153 acceptance cases and one unit case also fail; all of them pass on the base tree. The CIT-P should list them, so the owner's approval and the land plan cover every red.
- The cause: the kernel bodies changed while the root `.rulesync` sources and five template sources did not.
- Ordinary work: yes, because the owner approves on this list and a land or merge-queue run meets the unlisted reds.
- Consequence: other.
- What would reverse it: those cases passing on HEAD in a git-backed run, or failing on the base in the real tree.

**R2: the CTO's file states no brief contents.** `template/governance/kernel/roles/orchestrator.md` (no Brief item; compare ROLES-SPEC-1 §3.1:244-254). Severity low. In scope (S8's main text), not blocking.
- What happens: S8's text gives the CTO's file "reads and writes, skills, model, brief contents and handover". The file has all of these but brief contents (C1–C12, the read-first list, streams, watchers, the delegation rule, close practices, the resource gate, the morning sequence).
- The S8 test for the CTO (`tests/acceptance/W2-33/test_w2_33_files.py:103-107`) passes on any file that says "CTO" and keeps `GOV_ROLE=orchestrator`.
- Ordinary work: yes, because a CTO or adopter reading the role file finds no brief checklist.
- Consequence: other.
- What would reverse it: reading S8's Verify clause as the whole requirement. That clause asks brief contents only of `senior-engineer.md`.

**R3: the ticket lead's file limits QA to FULL tickets.** `template/governance/kernel/roles/ticket-lead.md:12`; compare `qa-engineer.md:13` and DEC-959 item 3. Severity low. A Wave 3 row.
- What happens: the lead's file says a fresh QA engineer probes before the merge "for a FULL ticket". The QA file and DEC-959 say core tickets are checked one by one before they merge whatever their profile, and the others in batches. `senior-engineer.md` names no duty to start the batched QA.
- A lead following its file could return a STANDARD core ticket without its individual QA.
- Ordinary work: yes, because a lead going by its role file alone would do this.
- Consequence: other (a review step missed; nothing the guard decides opens).
- What would reverse it: a decision that limits per-ticket QA to FULL, or the lead brief template carrying the per-stream rule.

**R4: the orchestrator's generated copy disagrees with the CTO's file.** `template/.rulesync/subagents/orchestrator.md:7,10`; `src/gov/launch/launcher.py:78`; `src/gov/adapters/portability.py:61-68`. Severity low. A Wave 3 row, routed to W2-153 and W2-60b.
- The skills: the source's preloaded skills are `orchestration` alone, while the kernel file's Skills line names five.
- The opening: the body starts "You are the ticket lead for {ID}", because `ROLE_TEMPLATES` maps `orchestrator` to `role-lead` even though `role-cto.md` exists. It is then followed by the CTO's role file.
- The effect: an `orchestrator` subagent would be told at once that it is a ticket lead and that it is the CTO. The source is exactly `compose()` and W2-153 pins this list, so the ticket followed its rules correctly.
- Ordinary work: yes, for anyone who spawns the orchestrator subagent.
- Consequence: other (DEC-178 holds such a subagent to its ticket's paths).
- What would reverse it: W2-153 or the owner deciding that the orchestrator agent keeps the lead template.

**R5: the engineer's reads sentence has a misleading qualifier.** `template/governance/kernel/roles/engineer.md:18-20`. Severity low. A Wave 3 row.
- What happens: "never reads the test designer's work … before they are merged and ready, and then only runs them" can be read as allowing reads after the merge. DEC-957 says the engineer never reads them.
- The guard refuses those reads anyway (`src/gov/guard/reads.py:108`), so this fails closed.
- Ordinary work: yes, because the wording is in the file the engineer reads.
- Consequence: other.
- What would reverse it: a decision that allows reads after the merge.

**R6: the install-refusal description says more than the refusal does.** `orchestrator.md:22`; `src/gov/guard/install.py:335-340`. Severity low. A Wave 3 row.
- What happens: the file says that when the key is missing "the refusal names `GOV_TICKET`". The guard's refusal names the key, the roster and how to set it, but not `GOV_TICKET`.
- Ordinary work: yes. Consequence: other.
- What would reverse it: the hook adding `GOV_TICKET` to that text elsewhere.

**R7: the dropped W1-35 roster half is only partly covered for `template/.rulesync`.** `src/gov/adapters/portability.py:253-292` and `tests/unit/adapters/test_w2_153_portability.py:115-118`. Severity low. A Wave 3 row.
- What is covered: `_kernel_findings` checks kernel roles against the root `.rulesync` sources both ways (a source missing, or a source with no kernel file).
- What is not: `template/.rulesync/subagents` is pinned to the root copy only for the six `ROLE_SKILLS` roles. A missing or extra template source for the three new roles is flagged by nothing in this repository; it would be caught in an adopted repository.
- Ordinary work: yes (the copies ACT could miss the template tree). Consequence: other.
- What would reverse it: the copies ACT's own check covering `template/.rulesync`.

**Per-KPI verdict**
- S1: pass. `ticket-lead.md` holds Reads, Writes and Handover, and `orchestrator.md` has no lead heading.
- S2: pass. All nine files have Version, Launch default and Skills; all skills exist; the CTO and Senior Engineer are at effort high. The launcher's plan is W2-60a's.
- S3: pass. `qa-engineer.md` exists and `independent-reviewer.md` does not; the access and per-stream statements are there; the auditor keeps the milestone audits. The guard refusal is W2-60b's.
- S4: pass. The work-order sentence is word for word in all nine; the engineer's and test designer's files deny the counterpart's reads (R5).
- S5: pass. The one-writer sentence is in all nine. The launcher refusal is W2-60b's.
- S6: pass. The four heads are there and the probe below passes.
- S7: pass. The values equal the table, there is no D-10 rule, and the C0 value is disclosed (see discoveries).
- S8: pass. R2 bears on it.
- S9: pass. Both copies state the CTO-only rule, the key and `GOV_TICKET` (R6).
- F1: pass. Neither copy has the old wording.
- F2: pass on the line rules. R3, R4 and R7 bear on it; generation drift is W2-153's.

**Q1 / Q2: tests that would pass on a broken file, and spec fidelity**
- The S1 and S8 content checks need only five words under a Reads, Writes or Handover head (eight under Brief), and the S8 CTO case needs only the word "CTO".
- F2's "departs from the roles spec" is tested only on the line rules (the README says so). A role file that stated a wrong permission in prose would pass. Spec fidelity was therefore judged by reading.
- No file grants a permission that the spec, a decision or the guard does not support. The SE and QA permission lists describe W2-60b's guard, and today's guard fails closed for both ids.

**Q3: fail-open statements.** None found.
- The QA engineer writes only its findings report (`qa-engineer.md:12,18,19`).
- The lead "never merges into the integration branch" (`ticket-lead.md:13`).
- The counterpart's reads are denied in both files.
- Installs are refused to every non-CTO session (`ticket-lead.md:31`, `senior-engineer.md:25`, `orchestrator.md:22`).

**Q4: the three revised W1-35 cases**

Compared with `3df1ac2de`, the changes are the three cases plus their support (lines 205-231: `TICKET_LEAD_REL`, `NINE_ROLE_FILES`, `DEFAULTS_LINE_PREFIXES`, `_ticket_lead_text`) and the class rename with a Rewrite-Reason docstring (233-236). Nothing else in the file changed.

1. **The lead's own file** (`TestTicketLeadSection` → `TestTicketLeadRoleFile`, `_section()` at :237).
   - Change: it now reads the body of `ticket-lead.md`.
   - Point kept: the five intent cases (what a lead is, does, never does, returns, cites) are unchanged and pass against the new file. That is DEC-1156 (3) and DEC-957 Q2's point.
   - Rewrite-Reason: :205-207 and :233-236.
2. **`test_the_section_adds_no_labelled_field_to_the_role` → `test_the_orchestrator_role_holds_no_ticket_lead_section`** (:279-291).
   - Old point: the lead stayed prose inside `orchestrator.md`, so it added no labelled field to the orchestrator's agent.
   - Why it changed: that point is moot now the lead has its own file.
   - New point: it asserts the decision's other half, that `orchestrator.md` holds no lead section and names `ticket-lead.md`.
   - Rewrite-Reason: :275-278.
3. **`test_the_roster_stays_at_the_same_roles` → `test_the_roles_folder_holds_the_nine_role_files`** (:296-303).
   - New check: exactly the nine files, and no `independent-reviewer.md`.
   - Rewrite-Reason: :292-295.
   - What the dropped half guarded: "`template/.rulesync/subagents/` holds exactly the six", meaning no rulesync subagent appears for a role the kernel lacks, and the source roster equals the kernel roster.
   - Where that guard lives now: W2-153's `_kernel_findings` (`portability.py:253-292`) flags a kernel role with no source and a source with no kernel role, against `.rulesync`. It runs on the real tree in `test_w2_153_sources.py`'s drift guard and in the unit composition case, and both are red on HEAD (R1), so that guard is live.
   - The remainder: W1-33's `.claude/agents` roster case and W1-38's field agreement cover the generated side. Only the `template/.rulesync` copy for the three new roles is unguarded here (R7).
   - Also changed: `TestWording._texts` reads the lead file and leaves out the defaults lines (Rewrite-Reason :386-390).
- Result: all W1-35 cases pass on HEAD.

**Q5: S6's planted review brief, triaged with `qa-engineer.md` as my role**

The brief: ticket X, STANDARD, KPI S1 "the CLI prints the version", round 2 just ended, findings F-a and F-b.

1. Triage. `qa-engineer.md:14`: "**Moderator:** it triages every finding against the ticket's own scope and KPIs". F-a is in scope, because S1's printed version lacks its patch number. F-b is out of scope, because help-text colours are not in S1.
2. F-b. `qa-engineer.md:15`: "**Wave 3 row:** a finding out of scope, or needing an unusual construction, is a Wave 3 row, never a round". F-b is listed as a Wave 3 row.
3. Verdict. `qa-engineer.md:16`: "**Verdict:** it returns the structured verdict per KPI: pass or fail for each KPI line, and each finding's scope and classification". With `:22` (each finding's two judgement lines): S1 fails on F-a, "Ordinary work: yes" and "Consequence: other". Under the loaded skill (`qa-review/SKILL.md:45`) that makes F-a a P2, not a blocker.
4. No third round. `qa-engineer.md:17`: "**Rounds:** at most two review rounds per ticket". Round 2 has ended, so no third round starts.
5. Where F-a goes. `qa-engineer.md:21`: "an unresolved bug goes to the stream's Senior Engineer, then the CTO and the owner". F-a goes up that line; the skill says it is fixed at the ticket's next resume (DEC-802).

The structured verdict returned:
```verdict
{"kpis": [{"kpi": "S1", "verdict": "fail", "findings": [{"id": "F-a", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F-b", "scope": "out", "ordinary_work": "yes", "consequence": "other", "disposition": "Wave 3 row"}]}], "next_round": "none (two-round limit reached); F-a escalated to the Senior Engineer"}
```
Result: F-b is listed as a Wave 3 row and no third round starts, so S6's probe passes.

**Q6:** the composed text equals the source byte for byte. Its `claudecode.skills` does not equal the kernel file's Skills line, and its opening is the lead template (R4).

**Q7:** every sha256 in the CIT-P matches. Its only misstatement is the incomplete list of reds in §4 (R1).

**What I probed and found sound:** no work lost; every ticket commit stays inside `allowed_paths`; no implementer touched acceptance tests (the W1-35 revision is the test designer's, with `Role: independent-test-designer` and a Rewrite-Reason); no guard or gate fails open; no `Role: owner` or `Decided-by:` on any ticket commit.

Classification of the findings: 0 blocking; 1 in scope but not blocking (R1, consequence other); 6 recorded rows (R2–R7, consequence other); none fails open or loses work.

```verdict
verdict: PASS
probed_commit: 3b3a90d74c3e0c5478f366453b07cb921c0c6f88
findings: 7
```

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": [{"id": "R3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S4", "verdict": "pass", "findings": [{"id": "R5", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S5", "verdict": "pass", "findings": []}, {"kpi": "S6", "verdict": "pass", "findings": []}, {"kpi": "S7", "verdict": "pass", "findings": []}, {"kpi": "S8", "verdict": "pass", "findings": [{"id": "R2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S9", "verdict": "pass", "findings": [{"id": "R6", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": [{"id": "R1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "R4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "R7", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```

guard_refusals: none (the heavy slot's "Read-only file system" messages on its own prio and log files came from the sandbox's write limits, not the guard; `/tmp/gov-w2-33-rv` could not be made for the same reason).