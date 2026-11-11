---
id: RUBRIC-2-APPLY
type: research-record
date: 2026-11-10
role: research (Sonnet, high, by RUBRIC-2 itself)
decisions: [DEC-1120]
sources: [DEC-839, DEC-866, DEC-957, DEC-1014, DEC-1112, DEC-1113, DEC-1118, DEC-1119, DEC-1120, DEC-1121]
---
# RUBRIC-2-APPLY: RUBRIC-2 checked against this week's work, the DEC-866 sweep, and the deltas for W2-33 and W2-60a

**Question.** Which class (C3/C2/C1/C0) does each ticket and ACT since 2026-11-08 09:00 fall in, what does RUBRIC-2 (DEC-1120) give each
role on it against what was used, what still enforces DEC-839 (1)-(3), and what replaces W2-33's and W2-60a's KPI lines?
**Feeds:** DEC-1120 (5): apply in practice now and into the product before EXAMIN's copy. **Stop rule:** the files named in the
brief read once, one search per question; no run of any suite; stopped when each of the four parts had its table.
**Method.** Read DEC-1120, DEC-839, DEC-866, DEC-957, DEC-1118, DEC-1119, DEC-1121; `spend.jsonl` (211 rows from 11-08 09:00; a script in
the scratchpad summed it); `git log --since=2026-11-08` (150 commits); the tickets' `profile`/`allowed_paths`; the ACT packages (23) and
`governance/project/operator/class-rules.yaml`; grep with line numbers over the paths the brief names; the Claude Code sub-agent
docs for precedence. **Commands run:** read-only grep, git log and two summing scripts only. No suite, install or commit.

## 1. This week's work, classed
Legend: O Opus, S Sonnet, H Haiku; h high, m max; des test designer, eng engineer, rev reviewer. RUBRIC-2 gives per class
(through D-10, engineers on C2/C1 stay Oh): **C3** des Oh, eng Oh, rev Oh (Om only for a FULL ticket's probe or after a fail-open
finding); **C2** des Sh, eng Sh, rev Oh if FULL else Sh; **C1** all Sh; **C0** Haiku or deterministic. Product-spec and research Sh,
auditors and adjudicators Oh always. **Used:** `spend.jsonl` records no model; every launch took launch_worker.sh's default
`claude-opus-5-5` (DEC-839), so "O" below is inferred, not measured. Effort is recorded only from 11-10 11:47 (and in some `what` text).

| id | what | class and reason | roles that worked it | RUBRIC-2 | used |
|---|---|---|---|---|---|
| W2-13 (+d10b serial-only gate) | pathmap/loader/role_paths, D-10 gate | **C3**: path map, guard (FULL) | des, rev | Oh; probe Om | O; des h, rev **max** (FULL: allowed) |
| W2-96 (d10a/b, lift maps) | `gov accept` reader, hidden-test wall (DEC-820 c) | **C3**: wall on hidden tests, verdict reader (FULL) | des x5, eng x2, rev x4 | Oh; Om probe | O; des h x3, **low x2**, eng h, rev max x2, high, **low** |
| W2-149 + ACT-W2-149-INSTALL-1 | set-up A's walls, kinds.yaml, tree-exclude | **C3**: walls, hidden sets, class (O) ACT (FULL) | des x2, eng x4, rev x6 | Oh; Om probe | O; h; rev max x4 on 11-10 |
| W2-128 / W1-08 | kernel templates, schemas, role files | **C3**: kernel | des, prod-spec, rev (rounds 1-2b, D-10) | des Oh, spec Sh, rev Oh | O; "medium" on 7 revision rounds |
| W2-139 + W2-140 (batch) | Contract text; W2-49 tests to it | **C3** (batch takes the higher: docs/contract; W2-140 alone is C2) | spec, des, 1 batch rev | spec Sh, rev Oh | O; effort not recorded |
| W2-141, W2-150, W2-56 | guard reads/hook; guard util/decide; sandbox, launcher env | **C3**: guard, hooks, permissions (W2-56 FULL) | des, eng, rev (W2-56: des x3, eng x2, rev) | Oh; Om probe W2-56 | O; "medium" on 2 revision rounds |
| W2-148 + operator agent | operator ACT runner (FULL) | **C3**: operator agent | des x3, eng x4, narrow rev x5 | Oh | O; effort not recorded |
| W2-142, W2-151 | retrieval/discovery SKILL.md; MR-1..6 regenerated | **C3**: kernel skills; Contract (W2-151 mechanical) | spec, rev | Sh spec, Oh rev | O |
| W2-05 (D-10 maps, lefthook) | git-env lines, hooks | **C3**: hooks (FULL) | rev only (map fixes) | Oh | O |
| W2-153, W2-129, W2-92, W2-55, W2-152, W2-147 | launch templates; links; store/retrieval; decisions; brief/facts; plan | **C2**: product code, launch, plan, schema (all STANDARD; W2-153 composes kernel role bodies but edits code) | des, eng, rev | des Sh, eng **Oh to D-10**, rev Sh | O; h, with "medium/low" on ~9 fix rounds |
| W2-145 | rerank service (FULL) | **C2**, FULL | des x3, eng x3, rev x3 | des Sh, eng Oh (D-10), rev **Oh** | O |
| W2-20 (d10d, gate, ACT-WIN-TOAST-1 reviews) | resource gate, pinned-gov fixtures | **C2** (secrets/__init__.py a C3 sliver) | des x9, eng x4, rev x8 | des Sh, rev Sh | O; rev **max x5** (STANDARD: not allowed) |
| W2-140, W2-66c, W2-154 (filed only) | acceptance edits; test-map cases; close serial | **C2** (test maps, close) | des | des Sh | O |
| W2-130, W2-88 edit, ticket drafts | register/link clean-up, STANDARD edit, W2-145 draft, ADR-0002, Q07/Q14 | **C1**: records, tickets, docs | spec, research, general-purpose, 2 rev | all Sh; rev Sh | O (inferred; helper models not logged) |
| FRESH-80 (6 experiments, 7 readiness reviews, sandbox experiment) | measurements, store/hook/roles checks | **C3**: measurement verdicts, hidden sets | research, auditors, graders | auditors Oh; research Sh | O; $109 costed |
| helper-watch, sentinel, dead-man, brake | watching | **C0** | none logged | H | dead-man Haiku (deadman.py:100), operator Sonnet (opcommon.py:108): already RUBRIC-2 |

**ACTs (22, by file date and mtime):** **C3 x20.** Class b stated: DEADMAN-WAKE-1, OPERATOR-1, CLAUDE-COPIES-1/2/3, PATHMAP-NS-2, WIN-TOAST-1,
EFFORT-HIGH-1, SETS-GLOBS-1. Class O stated: OPERATOR-2, STOP-IDLE-1, W2-149-INSTALL-1. Class not stated, read from the rule table
(`class-rules.yaml`, est.): GUARD-SETS-1, SELECT-HOOK-1, INDEP-WALLS-1, GUARD-CALLLOG-1, GATE-CONFIG-1/2 (machine-gate row, b). Path map and hidden sets
are C3 by (1) whatever the class: PATHMAP-NS-1 (a stated) and SANDBOX-SEAL-1 (a by the table). **C2 x2:** SELECT-FIXES-1, D4-RESTORE-1 (a: test map, opt-in lists).
Preparers Sh; the 8 ACT reviews on 11-10 all ran at max (DEADMAN-WAKE-1 x2, WIN-TOAST-1 x2, PATHMAP-NS-2, EFFORT-HIGH-1, INSTALL-1 x2).
**Tally: tickets C3 12, C2 10 (+W2-154 filed only), C1 1 + 3 grouped record items, C0 0 logged; ACTs C3 20, C2 2.** Roles per row are counts of spend
rows by their `what` text (est.).
**Measurements.** Costed rows 162 of 211, $679.53 at list price: des $196.66, eng $180.41, rev/auditor $175.35, experiments $109.05,
prod-spec $18.06. Effort `max` on 14 rows (12 costed, $67.64): 7 on FULL tickets (allowed as probes), 7 outside (W2-20 x5, DEADMAN-WAKE-1 x2:
no FULL, no fail-open finding recorded). Effort medium or low on 21 rows (judgement work; RUBRIC-2's floor is high). Not re-priced here (the next
report's, DEC-1120 (5)); est. the Sonnet-eligible share is the C2/C1 designers and, after D-10, engineers: the largest two rows above.

## 2. Conflicts with standing decisions (the DEC-866 sweep, by id and by value)
Route: **REC** CTO record edit (C1); **KPI** ticket KPI change; **ACT**; **KEEP** with a reason.
| path:line | enforces | class | route |
|---|---|---|---|
| DECISION_REGISTER.md:9146-9164 (DEC-839) | Opus for every role; effort table; max auditors/synthesiser; SUBAGENT_MODEL | C1 | KEEP: status line already "Changed by DEC-1120" (9146) |
| DECISION_REGISTER.md:14228-14231 (DEC-1118 (1)C "reviews staying on Opus", (2)E/F trials) and 14254-14258 (DEC-1119 (3)) | Sonnet designers/reviewers only as trials after the lift | C1 | **REC**: DEC-1120's header names only DEC-839 and DEC-1119 (1); RUBRIC-2 makes Sonnet C2/C1 designers and non-FULL reviewers standing, so E and F are no longer trials: add "Changed by DEC-1120" (DEC-866 (1)) |
| DECISION_REGISTER.md:11966 (DEC-957), 14259 (DEC-1119 (4)) | effort high; highest only reviewers/auditors when needed | C1 | KEEP: RUBRIC-2 is "Under" DEC-957 and sharpens it |
| DECISIONS-IN-FORCE.md:424 (DEC-1112 (3) delegated) | "model claude-opus-5-5 for every kind" (set-up A) | C1 | **REC** after the row below is decided |
| indep-walls/kinds.yaml:15,22,29,36; ACT-W2-149-INSTALL-1.md:59,64,122,248; tests/unit/orchestration/test_w2_149_setup_a.py:224,226,242 | writer, checker, auditor, labeller all Opus; hash-bound in a class (O) ACT awaiting the owner's yes | C3 | **KEEP** for set-up A's first run: a declared experiment (A5), the owner approved the five briefs (DEC-1113); RUBRIC-2 puts writers and labellers on Sonnet (checkers, auditors Opus). Changing it is a fifth rebuild, re-review and a new yes. Bring it to the owner as one line; est. the saving is small beside the delay |
| prompts/w2-orchestrator.md:145 | DEC-839's paragraph: Opus every role, max auditors/probes/synthesiser, xhigh designer trial | C1 | **REC**: replace by a pointer to rule 11 (line 38-45, already RUBRIC-2) |
| prompts/w2-orchestrator.md:143; tools/dispatch/launch_now.sh:16-18; scratch launch_when_gate_opens.sh:14-16; tests/unit/launch/test_w2_153_template.py:189-193 | lead launch: Opus high, SUBAGENT_MODEL Opus | C1 / test | KEEP: leads are Oh in RUBRIC-2; the env is only a default for spawns naming none |
| briefs/LEAD-w2-common.md:29, 93, 96, 97 | `--model claude-opus-5-5` literal, xhigh designer, max FULL reviewer, SUBAGENT_MODEL | C1 | **REC**: `<model> <effort>` from the role-by-class table; xhigh and the max-on-every-FULL-review lines out |
| briefs/LEAD-w2-common.md:108; scratch EMG-common.md:9; EMG-d4b-launched.md:31 | trailer `Co-Authored-By: Claude Opus 5.5` for every worker | C1 | **REC**: `<your model's name>`; `close/command.py:526-534` and `telemetry/counter.py:299` report the model from this trailer |
| briefs/AUDITOR-common.md:7 | "You run at --effort max" | C1 | **REC**: high; max only when the launch names a reason (RUBRIC-2 (3)) |
| briefs/JUDGEMENT.md | no model or effort value | C1 | none |
| template/governance/kernel/roles/*.md:14-17 (6) and template/.rulesync/subagents/*.md (6) | "Model tier: standard; the orchestrator may name another model after `--`"; no default line exists | **C3** | **KPI** (W2-33), then **ACT** (class b) for the generated copies; W1-33, W1-46 and W2-153 S3 require the `Model tier` field, so it stays and points to the new line |
| .claude/agents/*.md | no `model` or `effort` front matter, so an in-session spawn of a named agent runs on the SUBAGENT_MODEL default (Opus) | C3 | **ACT** with the copies above (docs: front matter sits above the env default); only for roles whose tier is one value (spec, research, auditor, orchestrator) |
| src/gov/launch/launcher.py (main tree) | no model or effort logic: arguments after `--` pass verbatim | C2 (C3, section 3) | **KPI** (W2-60a); its branch already has the subagent env (launcher.py:439) and record (:457-459) in the worktree |
| w2/W2-60a worktree: tests/acceptance/W2-60a/w2_60a_support.py:93-105; test_w2_60a_model_and_effort.py:33-42, 59-67, 101-114, 143-158; test_w2_60a_kept_out.py:79; test_w2_60a_launch_record.py:49,75; README S3, S4, 201-206 | one default per role (O/O/Om/S-medium/O-low fixtures); a Sonnet or Haiku engineer refused; subagent model = session model; record fields | C3 | **KPI** then designer revision (section 3). Main tree has no `tests/acceptance/W2-33` or `W2-60a` |
| `.tickets/DAEO-cv58.md`:33, 34, 40, 69, 72; `.tickets/DAEO-lrre.md`:27 | role default, "a model not the role's refused", second review; DEC-839 items | C1 | **KPI** (section 3) |
| `.tickets/DAEO-ecac.md`:28 (W2-60b) | session record: model, effort, task class from W2-60a's record | C2 | **KPI**: add tier, criticality, promotion (record only) |
| launch_worker.sh:16, 37, 40, 69-71; test_launch_worker.sh:84, 86 | Opus default for every role; effort low..max positional; role list lacks a purpose | C1 scratch | **REC** (section 4) |
| ~/.claude/settings.json:3 (`CLAUDE_CODE_SUBAGENT_MODEL` opus), :24 (`effortLevel` xhigh), :25-27 | default for spawns that name none; default effort | owner | KEEP the env (a per-invocation `model` and `effort` win on CLI 2.1.292, > 2.1.251, per the docs); effort by **ACT-EFFORT-HIGH-1** (pending) |
| tests/acceptance/W1-49/README.md:226; W2-62 test:22; W2-60a README 203-204 | live harness tests on Haiku at low (DEC-839's last row) | C3 tests | KEEP: C0 by nature (a case only checks a report); RUBRIC-2 is silent on it, so record that reason |
| WAVE_2_REVISED_PLAN.md, WAVE_2_WBS.md, packages (ROLES-SPEC-1, MODEL-TIERS-1, RUBRIC-1, W2-88-STANDARD-1:109), LIFT-1 declarations | history that cites DEC-839 or the reader's model | C1 | KEEP (append-only) |
**Other decisions touched:** DEC-957's floor and DEC-1118 C are consistent; DEC-1119 (2)-(3) is what this package executes; DEC-1014 item 1
(second FULL review a different setting) fits RUBRIC-2 only if it is the probe at Om after a first at Oh; DEC-839 (4) agent teams off is untouched.
**Count (21 rows): REC 7, KPI 4, KPI then ACT 1, ACT 1 (and ACT-EFFORT-HIGH-1, already drafted, under KEEP), KEEP 7, none 1.** No C3 row is a CTO edit; the three C3 rows (roles, agents, W2-60a's tests) go by ticket or ACT.

## 3. W2-33 and W2-60a: the deltas
**Classes.** **W2-33 (DAEO-lrre, open, STANDARD): C3** (`template/governance/kernel/roles/**` is the kernel; the handoff schema alone would be C2).
Writer product-spec **Sh**; its designer **Oh** (C3); reviewer **Oh** (not max unless a fail-open finding); an engineer, if one is needed, Oh.
Kernel change goes by CAP-33: evidence, review, owner approval and hash, then a class (b) ACT for `.claude/agents/**` (DEC-315).
**W2-60a (DAEO-cv58, in_progress, FULL): C3 recommended** (the ticket says it rewrites the CLI line and the settings that carry the sandbox and
keeps connectors out, "fails open in ordinary work", DEC-801; by path alone launch is C2). Next rounds: product-spec KPI edit **Sh**; test
designer (revises the 3-round tests) **Oh**; engineer **Oh** (C3, and D-10); first review **Oh**; second review the FULL probe **Om**
(DEC-1014 item 1: a different setting). Its branch has had three review rounds, so promotion to Opus is met anyway. If the CTO classes it C2,
the designer is Sh and the rest unchanged (FULL reviewers are Oh).

**W2-60a KPI lines that conflict, and their replacements** (replace success lines 3 and 4; amend 8 and 9; add one):
- Now (3): "role's default model and effort, read from its role file's default line ... [DEC-839 items 1, 2 and 5]". Now (4): "A model given after --
  that is not the role's is refused ... subagent model is set to the session's model [DEC-839 items 1 and 3]".
- **S3'** The session's model and effort are RUBRIC-2's for its role and criticality: read from the role file's `Launch default` line and its
  `Launch by criticality` line (C3, C2, C1, C0 overrides), the ticket's criticality derived from its profile and `allowed_paths` by
  `governance/project/criticality.yaml` (never from the ticket's `class`, which is its kind); applied on the line and recorded with `tier`,
  `criticality` and `model_source` (role default, by criticality, after --, trial, promotion); a missing or malformed line refuses; an effort below
  high for a judgement role, or max with no `--reason`, is refused [DEC-1120 (2)-(3)]. Verify: a case per role x criticality on fixture role files.
- **S4'** A model after `--` that is not the resolved tier's is refused naming both, unless `--trial <id>` names a recorded trial (role, criticality,
  model and effort, two or more tickets that include this one, its Opus reviewer) and the launch records the trial id. The subagent model is the
  session's tier model, as the default for spawns that name none, recorded; a spawn that names its own wins (CLI above 2.1.251) [DEC-1120 (3)].
- **S4''** (promotion) A ticket whose review records show two failed reviews or a fail-open finding launches its next round on Opus at the table's
  effort, recorded as `promotion` with the reason and the record's path; a lower model is refused. Verify: planted review records.
- **S9'** (was DEC-1014 item 1) On a FULL ticket the second review is the probe, Opus max, the first Opus high; the record shows both; the same setting
  twice is refused unless the owner named it; max on any other review needs `--reason` [DEC-1014, DEC-1120 (2)].
- Failure line: add "a model below its tier with no trial; a promotion not applied; an effort below the floor". W2-60b's record (DAEO-ecac:28) takes tier,
  criticality, promotion from this record (a one-line KPI; its model field stays the log's own).

**W2-33 line that conflicts and its replacement.** Now: "Machine-readable defaults per role (model, effort, skills) in each role file, read by W2-60a's launcher; effort high for the CTO and the Senior Engineers [DEC-839 item 5, DEC-957]". Replace: "Each role file carries
`Launch default: model <m>, effort <e>` and, where the table varies by class, `Launch by criticality: C3 ..., C2 ..., C1 ..., C0 ...`, with RUBRIC-2's values:
orchestrator, leads, senior engineers Oh; engineer Sh (C3 Oh); test designer C3 Oh, else Sh; QA engineer (the reviewer) C3 Oh, C2 Oh if FULL else Sh, C1 Sh;
independent auditor Oh; product-spec, research Sh; the `Model tier` field stays and names the line [DEC-1120 (2), W1-33]. The through-D-10 rule is not
written into a role file; it is the CTO's launch practice until the lift ends. Verify: a test per role file reads both lines and the values equal the table; the
generated agents carry the same [W2-153 S3]." (The QA engineer's split from the auditor, already in W2-33's KPI 3, is what lets reviews vary by class.)

**Tests to revise (DEC-866).** W2-60a's acceptance tests (worktree files above): `DEFAULTS` becomes the table by criticality; the "Sonnet or Haiku engineer refused"
cases (`test_w2_60a_model_and_effort.py:105-114`) become "refused unless trial or tier"; the subagent-model, launch-record (tier, criticality, promotion)
and README rows S3, S4, 201-206 follow. By an independent test designer (Opus high), in the tests worktree, `Rewrite-Reason: DEC-1120`, never the
engineer. Unit tests the engineer revises: `test_w2_153_template.py:189-193` stays; `test_w2_149_setup_a.py` only if kinds.yaml changes. W2-33 has no tests yet:
its designer writes them to RUBRIC-2 from the start. W1-33/W1-46 stay (they need the field only).

## 4. Practice gaps (smallest fix and route)
| gap | smallest fix | route |
|---|---|---|
| launch_worker.sh:37 defaults every role to Opus; effort is positional with no class (:69-71) | `<role> <criticality> <brief>` resolving model and effort from a table; `--trial`, `--reason`; refuse below high and max without a reason | CTO scratch edit and its test (C1) |
| spend.jsonl has no model, tier, criticality or promotion; effort only on launched rows | spend.py already takes `--extra key=value`: pass `model= tier= criticality= promotion=` from launch_worker.sh and in the helper rows | CTO (C1), no code change |
| Agent-tool helpers that name no model take `CLAUDE_CODE_SUBAGENT_MODEL` (Opus) and the session effort | every Agent call passes `model` (alias sonnet, opus, haiku) and, on 2.1.292, `effort`; rule 11 already says so; check by the spend log | CTO practice |
| no criticality field: `class` is the ticket's kind (DEC-1121 adds that same name to template 1.0.1; W2-60a KPI 8 says "ticket's class") | name the new one `criticality`, derived from `criticality.yaml` (profile + paths); no template change | W2-60a KPI (S3'), file is C2 |
| no role file has a default line (grep none); W2-60a's merge waits on them (cv58:72) | W2-33's replacement line | KPI |
| trailers name Opus; counter and close report the model from them | `<your model's name>` in the three briefs | CTO (C1) |
| `max` used on 7 reviews outside the rule; medium/low on 21 judgement rounds | brief and script changes above; the CTO writes the reason when it uses max | CTO |
| ~/.claude xhigh default (Sonnet's levels may differ: "available levels depend on the model") | ACT-EFFORT-HIGH-1, awaiting the owner | ACT |
| the independent-auditor role serves reviews and audits | until W2-33 splits the QA engineer, the spend row's `what` names the purpose and the brief the tier | CTO |

## Verdict
RUBRIC-2 fits this week's work cleanly: 12 C3 and 10 C2 tickets, 20 C3 and 2 C2 ACTs; the one real value conflict in a hash-bound file is set-up A's all-Opus kinds (keep, with a reason).
Tooling cannot express RUBRIC-2 yet: `gov launch` has no model logic in the main tree, no role file has a default line, and only the briefs, prompt and launch script (C1) can move today.
## Draft KPI lines (the CTO's next report; `verify` on each)
- "Every launch this week after 11-10 names model, effort, tier, criticality" — verify: count of `spend.jsonl` rows with all four, divided by launched rows.
- "No `max` without a recorded reason" — verify: rows with effort max and no reason, from the same log.
## Residuals
Nine ACT packages state no class (read from the rule table, est.); RUBRIC-2 names no class for ACT class a (taken here by what it touches); the Haiku id differs
(`claude-haiku-5-5` in deadman.py:100 and opcommon.py:109, `claude-haiku-4-5-20251001` in W2-60a's tests): verify against `claude --help` before the KPI. W2-60a's code branch
is unreviewed against RUBRIC-2 and 2026-11-01-old: it needs a merge of integrate. Re-pricing this week by tier is not done here. Continue-from: none.
