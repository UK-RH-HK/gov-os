---
type: probe
task: DAEO-6f0s
reviewer_session: 0be7734a-cd16-45a5-b114-c45bdb7ed5df
implementer_session: 0f3225ba-d30e-41de-a030-d0f7a296c833, 7846bd54-f3ac-4fa5-87b0-9ac81474f9c4, 13dc87dc-9efc-4adb-8e6b-51b22c9bf937
reviewer_wrote_nothing: true
commissioned_by: orchestrator (the W2-184 ticket lead)
judged_by: orchestrator (the W2-184 ticket lead)
judgement: fail
probed_commit: 8830dece08be86f18486d7f4a6d00058a917df2f
---

# Probe of DAEO-6f0s (W2-184), round 1: judgement fail

- **Head probed:** 8830dece08be86f18486d7f4a6d00058a917df2f (`git -C /home/usain/gov-os-worktrees/W2-184 rev-parse HEAD`, which matches). The tree was clean at the start and is clean at the end (`git status --porcelain` is empty).
- **Session:** independent-auditor, model claude-opus-5-5, effort high. Fresh session; I wrote none of the audited files.
- **task:** DAEO-6f0s
- **decisions:** DEC-1120 (1)-(3), DEC-1167 (2), DEC-1126 (3), DEC-1010, DEC-839, DEC-801, DEC-808
- **Ticket diff:** I reviewed `git diff 235fc1cc6 8830dece0`. 235fc1cc6 is the integrate tip that cbf647a11 actually merged in. The brief's base, 1fd0066e1, also brings in W2-116 and other tickets' files (51 files against 21).
- **What I ran (whole suites not re-run; all fixtures in `$TMPDIR/probe`, `HOME` set to an empty scratch folder):**
  - Read the code: `criticality.py`, `role.py`, the diff of `launcher.py`, `criticality.yaml`, the ticket, DEC-1167, DEC-1126, DEC-1120 and DEC-1010, the case names of the acceptance and unit tests, `launch_worker.sh`, and the path map's hidden-set entries.
  - In-process against the real tree (worktree `src`, pinned interpreter):
    - `launcher._promotion` over every one of the 72 real `docs/probes/*` folders.
    - `criticality.ticket_criticality` over all 248 real tickets, plus synthetic tickets.
    - `role.read_by_criticality` over the real kernel role files.
  - `$TMPDIR/probe/p1.py`: six launch scenarios built on the acceptance fixtures (`w2_184_support`, the stand-in CLI and an open gate), each in a fresh sandbox: `resume_round1_after_round2`, `wbs`, `nofile_c3`, `probe_high`, `trial_on_probe`, `tables_off`.

## Findings

### F1 — S1 — hidden sets are missing from the project's `criticality.yaml`; tickets on them resolve to C1 or C2, not C3 (blocking)
- **What the interface says:** 1.5 writes C3 for "the guard …, permissions, the path map, **hidden sets**, the operator agent, the kernel and the Contract" (from DEC-1120 (1)).
- **What the file has:** `governance/project/criticality.yaml:8-17` lists `governance/project/held-out.yaml` and nothing for hidden sets. The change record (`docs/changes/W2-184-CIT-E.md:24`) shows "held-out" was read as standing for hidden sets.
- **Where hidden sets live:** the path map (`governance/project/path-map.yaml:545-594`) puts them at `fixtures/evaluation/<set>/hidden/**`.
- **Probes:**
  - `ticket_criticality` on `{STANDARD, [fixtures/evaluation/examin/hidden/**]}` gives **C2**.
  - With a probe-record path added (`docs/probes/X/**  # rec`) it gives **C1**.
  - Real tickets: W2-93 (DAEO-6y0x, allowed `fixtures/evaluation/adoption-proving-ground/hidden/**`) gives **C1**; W2-94 (DAEO-g87r, in_progress, EXAMIN's `check_gold.py` and `visible/**`) gives **C1**.
- **Effect:** with the kernel tables, an engineer or test designer on such a ticket launches on claude-sonnet-5-5, high. RUBRIC-2's C3 gives claude-opus-5-5, high. No trial is involved and nothing is refused; the record says `criticality: C1`.
- **Why the cases miss it:** the unit case `tests/unit/launch/test_w2_184_criticality.py:170-178` checks the named C3 paths but has no hidden-set path.
- **Expected:** a hidden-set glob in the C3 rule, e.g. `fixtures/evaluation/*/hidden/*` (with `*` crossing `/`, this matches both ways).
- **What would reverse it:** a CTO or owner reading that DEC-1120 (1)'s "hidden sets" means `held-out.yaml` only. Or evidence that no ticket naming a `fixtures/evaluation/*/hidden/**` path, or a hidden half's checker, is ever launched through `gov launch` as a worker role.
- `Ordinary work: yes, because tickets that write or check a set's hidden half are planned routinely (W2-93 closed, W2-94 in progress) and carry exactly these paths`
- `Consequence: fails open` (the launch starts on a model the table does not give for the ticket's class)
- `Scope: in` (S1, and interface 1.5's file is in this ticket's `allowed_paths`)

### F2 — S4 — a third review is admitted without `--owner-named` when round 2 ran on a non-max effort
- **Probe** (`probe_high`, C2 FULL ticket):
  - Round 1: Opus high.
  - Round 2 launched with `-- --effort xhigh`: accepted (review_round 2, Opus xhigh, `after --`), as 6.2 allows.
  - Round 3 with no options: **accepted** (review_round 3, Opus max, `probe`), because its setting equals neither earlier record.
- **Why it matters:** 6.3's "so a third review is refused without the owner's decision" holds only when round 2 was the probe's max. DEC-1010 caps reviews at two rounds.
- **Expected:** refuse round ≥ 3 without `--owner-named` whatever the setting. Alternatively, keep the probe's max when an effort is given on round 2.
- **What would reverse it:** a reading that the same-setting rule alone is the intended cap.
- `Ordinary work: no, because it needs the lead to override round 2's probe max with a different effort of at least high, departing from S4's own setting`
- `Consequence: fails open`
- `Scope: in` (S4). A Wave 3 row, or a ride-along fix if the ticket resumes (DEC-802).

### F3 — S4 — resuming round 1 after round 2 has started is refused
- **Probe** (`resume_round1_after_round2`): round 1, then round 2, then `--resume <round 1 session>`. The resume is refused as "the same setting as session <round 2>": round 2's record is counted, the resumed one is left out, so the resume computes round 2 and gets the probe's Opus max. Resuming round 2 is accepted (review_round 2).
- **What would reverse it:** a reading that resuming an earlier review once a later one exists should need the owner.
- `Ordinary work: no, because resuming an older review after the next one has started is unusual`
- `Consequence: other` (it fails closed)
- `Scope: in` (S4). Row.

### F4 — S2/S4 — a trial replaces a FULL ticket's probe
- **Probe** (`trial_on_probe`): round 1 Opus high. Round 2 with a trial planted for the auditor (Haiku, low) is admitted: Haiku low, `trial`, review_round 2.
- This follows section 8's precedence (trial before probe) and 4.3 (a trial's effort below the floor is accepted).
- **What would reverse it:** none needed; it is as specified. The question is whether a trial may replace S4's probe at all.
- `Ordinary work: no, because it needs a planted trial file naming the auditor role and this ticket`
- `Consequence: other` (a recorded exception under DEC-1120 (3))
- `Scope: in`. Row for the CTO.

### F5 — S5 — five real probe folders have verdict blocks the parser refuses
- `_promotion` refuses DAEO-2bdu, f6x3, fd0p, g29a and lrre.
- Their blocks are YAML (`verdict: PASS …`) or JSON whose findings are plain strings (`"findings": ["RV1-8"]`).
- All five tickets are closed. Any worker launch on one of them, if reopened, is refused until the record is rewritten (as 5.2 requires).
- **What would reverse it:** the CTO rewriting the five blocks, or a reading that legacy blocks are skipped.
- `Ordinary work: yes, because a closed ticket may be reopened`
- `Consequence: other` (it fails closed)
- `Scope: in`. Row.

### F6 — S5 — promotion fires on any `fails open` finding, including ones judged out of scope or not ordinary work
- 17 of the 72 real folders would promote "a fail-open finding". Most of those findings are Wave 3 rows (`ordinary_work: no`), e.g. DAEO-03ub, 0z8c and 61vm.
- This is as written in 5.2 (a) and the KPI ("any fail-open finding"). The cost is Opus on every later round of those tickets.
- This record's own F2 is a "fails open" row, so W2-184's next round will be promoted.
- **What would reverse it:** the owner confirming that "any fail-open finding" includes rows.
- `Ordinary work: yes`
- `Consequence: other` (over-promotion; it fails closed)
- `Scope: in`. Row for the CTO.

### F7 — S1/1.4 — the amended 1.4 can launch this repository off the table if the code tree and the launch root differ
- **How launches run here:** `launch_worker.sh` runs a tree's own code (`PYTHONPATH=<tree>/src`) with root equal to that tree, and the code and `criticality.yaml` arrive in the same merge. So a tree with the new code has the file.
- **Remaining paths:** `LAUNCH_CODE_ROOT` (the CTO's word only), a re-pinned `gov` on PATH run in a tree not yet merged with integrate, or an honest deletion of the file.
- **Effect on those paths:** the launch is silently "as before". A C3 engineer gets Sonnet (probe `nofile_c3`: claude-sonnet-5-5 medium, `role default`, criticality null). A FULL ticket's second auditor launch is not the probe and is not refused (probe: r2 equals r1).
- Only the record shows it (`criticality: null`).
- **Suggestion:** one stderr line when the file is absent but the role file has a table.
- **What would reverse it:** evidence that a pinned `gov` is never used for worker launches in this repository.
- `Ordinary work: no, because this repository's launches run the tree's own code, which lands together with the file`
- `Consequence: fails open`
- `Scope: in`. Row.

### F8 — S1 — guard inputs other than the named ones resolve below C3
- `governance/project/secrets.yaml` and `.claude/settings.local.json` resolve to C2. `governance/project/indep-walls/**` with a probe path resolves to C1.
- Whether these count as DEC-1120 (1)'s "permissions" is a reading. Interface 1.5 names only `.claude/settings.json`.
- **What would reverse it:** the CTO confirming that "permissions" means `.claude/settings.json` alone.
- `Ordinary work: no, because no current ticket names these paths and the interface names no such glob`
- `Consequence: fails open`
- `Scope: in`. Row (could ride along with F1's fix).

### F9 — S1 — a probe-record path lowers an unlisted-area ticket from C2 to C1
- This is the highest-matching-rule semantics. The default class applies only when no rule matches, so adding `docs/probes/<id>/**` makes, for example, a `tests/**` or `fixtures/**` STANDARD ticket C1.
- With today's kernel tables C1 and C2 give the same model and effort for every role that has a table, except qa-engineer on FULL, where the profile rule keeps C2.
- **What would reverse it:** none; as specified.
- `Ordinary work: yes`
- `Consequence: other` (no model change today)
- `Scope: in`. Row.

### F10 — out of scope — an adopted repository with no `criticality.yaml` does not route by RUBRIC-2
- My view: this is consistent with DEC-1167 (2). DEC-1167 (2) moved DEC-1126 (3)'s "apply now" to "after the copy starts", and the copy runs on `Launch default`.
- Routing an adopted product by RUBRIC-2 needs an adopted `criticality.yaml`. That is an entry criterion of the ticket that turns it on (DEC-803), not of this ticket.
- `Ordinary work: yes`
- `Consequence: other` (decided behaviour)
- `Scope: out`. Row.

### What I probed and found sound
- **Criticality matching:**
  - The comment tail is stripped.
  - fnmatch works in either direction: `src/**` hits `src/gov/guard/*`.
  - The highest class wins.
  - The ticket's `class` is never read.
  - This ticket resolves to C2.
  - All 248 real tickets resolve.
- **Table parser on the real kernel role files:** engineer, test designer and qa-engineer, including qa-engineer's FULL form, parse to the right pairs. Roles with no table give `None`.
- **Floor and max:** the floor, max/`--reason` and 3.2a are as written.
- **Model after `--`:** a different model is refused naming both; the same model is recorded as `after --`.
- **Trial:** every field, the wbs_id, and refusal on a promoted ticket all behave as written.
- **Promotion:**
  - Fail-open is checked first.
  - Promotion applies on two failed reviews.
  - The record path is root-relative and taken in sorted order.
  - A lower model is refused.
- **Review count:**
  - Rounds 1 and 2 give Opus high, then Opus max with `effort_source: probe` (probe `wbs`).
  - A launch by wbs_id counts.
  - Resumes are excluded.
  - Other roles and other tickets are not counted.
  - A launch record that is not JSON is refused.
- **Same setting:** the same setting twice, and round 3, are refused without `--owner-named`.
- **Record:** has all nine keys.
- **Subagent model:** equals the final model (`launcher.py:735`).
- **Ordering:** every refusal happens in `_worker_plan`, before `exclude_placeholders`, the gate and the record.
- **Unchanged paths:** `--plan` and lead launches are not in the diff and are untouched.
- **Known item:** the `command.py` wiring was already judged by the lead (interface 7.2); I found nothing else missing.

## Per KPI line

- **S1: fail.**
  - Sound: the table line, the floor, max/`--reason` and the record fields work as the line and interface say, and the cases cover them well (comment tail, broad path, `class` ignored, FULL form, 1.4's no-file cases).
  - Fails: the project's `criticality.yaml` leaves out DEC-1120 (1)'s hidden sets (F1). Tickets that write or check a hidden half resolve to C1 or C2 and launch on Sonnet where C3 gives Opus. The cases do not catch it, because the project-file unit case lists no hidden-set path.
  - Rows: F7, F8, F9.
- **S2: pass.**
  - A model after `--` other than the resolved one is refused naming both; the same one is accepted as `after --`.
  - Trials are checked field by field (role, criticality, model, effort, two or more distinct tickets including this one by id or wbs_id, an Opus reviewer) and recorded.
  - `CLAUDE_CODE_SUBAGENT_MODEL` and the record's `subagent_model` are the final model.
  - F4 is a row.
- **S3: pass.** The nine keys are always present. A launch by criticality, a trial, a promotion and a plain launch each record their values and their nulls, as the cases assert whole (`assert_session`).
- **S4: pass.**
  - On a FULL ticket, round 1 is Opus high and round 2 is the probe (Opus max, `probe`, no `--reason`); both records show it.
  - The same setting twice and a third max are refused without `--owner-named`.
  - Max on any other review needs `--reason`.
  - Counting by wbs_id, excluding resumes, and ignoring other roles and tickets all hold.
  - F2 (a third round admitted after a non-max round 2) and F3 are rows.
- **S5: pass.**
  - Two failed reviews, or a fail-open finding (checked first), promote every worker role to `criticality.yaml`'s Opus at the table's or probe's effort, recorded with the reason and the root-relative record path in sorted order.
  - A lower model and a trial are refused; neither condition means no promotion.
  - F5 and F6 are rows on real records.
- **F1: pass.** A model below the tier with no trial is refused, a promotion is recorded and applied, and an effort below high for a judgement role is refused, each with its cases.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F7", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F8", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F9", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F10", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S2", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S5", "verdict": "pass", "findings": [{"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "F1", "verdict": "pass", "findings": []}]}
```

judgement: fail

## The lead's triage (DEC-1010 item 1; the moderator until the three layers is the CTO, this is the lead's proposal)

- F1: blocks (in scope, ordinary work yes, fails open). Fix batch: hidden sets in the C3 rule (`fixtures/evaluation/*/hidden/*`), test-design batch first.
- F2: row, rides along (DEC-802): a review round 3 or later is refused without `--owner-named`, whatever its setting (DEC-1010).
- F8: row, rides along (DEC-802): `.claude/settings.local.json`, `governance/project/secrets.yaml`, `governance/project/indep-walls/*` in the C3 rule (stricter only).
- F3, F4, F5, F6, F7, F9: rows, for the CTO (F5: five closed tickets' legacy verdict blocks; F6: whether promotion should skip rows; F4: whether a trial may replace a FULL probe).
- F10: out of scope; the lead's reading of DEC-1167 (2) stands.
