# W2-60a (`DAEO-cv58`) and RUBRIC-2: three costed options (DEC-105)

By the product-spec helper for the CTO (Sonnet, high, class C1), 2026-11-11, from head `9bb497925ed7`. DEC-1125 (3) (iii) c.
**M** means measured (the file named); **E** means my judgement. Nothing in W2-60a was edited: its ticket file, its
branch and its tests are as they were.

## 1. The question for the owner

W2-60a is an approved specification (FULL, in progress, three review rounds on its branch). Two of its lines follow
DEC-839: success line 3 (the role's one default model and effort) and line 4 (a model after `--` that is not the
role's is refused). DEC-1120 (2)-(3) changed DEC-839 (1)-(3): the model and effort now depend on the role **and** the
ticket's criticality class, with a trial exception and a promotion rule. DEC-1120 (5) and DEC-1119 (2) say RUBRIC-2
goes into the product through W2-33's role defaults and W2-60a's launch, **before EXAMIN's copy**. So the approved
lines and the owner's later decision disagree. That is a contradiction with a closed specification, so DEC-105 gives
three costed options and the owner chooses. It is not mine or the CTO's call: option 3 would change one of the owner's
standing decisions (DEC-1112 (3)).

Sources: `packages/RUBRIC-2-APPLY.md` §3 (the replacement lines), `packages/AUDIT-NIGHT-1/d-tools.md` P-2 (the same
finding, found independently, as one compact line), `.tickets/DAEO-cv58.md` (M), `packages/LIFT-1/P1-PLAN.md` row P1-18.

## 2. The lines RUBRIC-2 would add

From RUBRIC-2-APPLY §3, in the ticket's form. Replace success lines 3 and 4; amend lines 8 and 9; add one failure
line. The `Verify:` clauses of S4' and S9' are mine (RUBRIC-2-APPLY gives none for them).

**Replaces line 3 (was: "The role's default model and effort, read from its role file's default line ... [DEC-839 items 1, 2 and 5 ...]"):**
> S3' The session's model and effort are RUBRIC-2's for its role and criticality: read from the role file's `Launch default` line and its `Launch by criticality` line (C3, C2, C1, C0), the ticket's criticality derived from its profile and `allowed_paths` by `governance/project/criticality.yaml` (never from the ticket's `class`, which is its kind); applied on the launch line and recorded with `tier`, `criticality` and `model_source` (role default, by criticality, after `--`, trial, promotion); a missing or malformed line refuses; an effort below high for a judgement role, or max with no `--reason`, is refused. Verify: a case per role and criticality on fixture role files [DEC-1120 (2)-(3)]

**Replaces line 4 (was: "A model given after -- that is not the role's is refused ... [DEC-839 items 1 and 3 ...]"):**
> S4' A model after `--` that is not the resolved tier's is refused, naming both, unless `--trial <id>` names a recorded trial (role, criticality, model and effort, two or more tickets that include this one, its Opus reviewer) and the launch records the trial id. The subagent model is the session's tier model, as the default for spawns that name none, recorded; a spawn that names its own wins (CLI above 2.1.251). Verify: a planted trial record: the launch is accepted and records the id; a model after `--` with no trial: refused naming both [DEC-1120 (3)]

**Adds:**
> S4'' A ticket whose review records show two failed reviews or a fail-open finding launches its next round on Opus at the table's effort, recorded as `promotion` with the reason and the record's path; a lower model is refused. Verify: planted review records: one with two failed reviews, one with a fail-open finding, one with neither [DEC-1120 (3)]

**Replaces line 9 (was DEC-1014 item 1: a different setting for the second review):**
> S9' On a FULL ticket the second review is the probe, Opus max, and the first is Opus high; the record shows both; the same setting twice is refused unless the owner named it; max on any other review needs `--reason`. Verify: a planted FULL ticket: the two launch records differ as stated; the same setting twice is refused [DEC-1014 item 1, DEC-1120 (2)]

**Amends line 8 (the launch record):** its fields gain `tier`, `criticality`, `model_source`, the trial id and the promotion
reason, each null when not given.

**Adds a failure line:** "A model below its tier with no trial; a promotion not applied; an effort below the floor."

For comparison, d-tools P-2 puts the same change as one line (the table, a refusal unless a promotion with its reason
is given, a launch record with class, tier and reason). It has no trial and no probe rule, so RUBRIC-2-APPLY's set is
the fuller and DEC-1120 (3) needs the trial. I used RUBRIC-2-APPLY's.

## 3. Three things the lines leave open (found while reading; each is in every option that builds them)

1. **`governance/project/criticality.yaml` does not exist** (M: not in `governance/project/`), and no ticket writes it.
   W2-60a's paths hold `launcher.py`, `role.py` and `record.py` only. The apply option needs one path added (the file,
   and a small reader beside `role.py`). My simplest reading: the file is a project table of paths and profiles to
   C0-C3, read by `role.py`. About 1 lead-hour of the figures below.
2. **W2-60a's body (line 72) says it merges after "W2-11's widening writes" the role files' default lines.** W2-11's own
   ticket says the role file "stays limited to DEC-866's sweep sentences (W2-33 holds the rest)" (`DAEO-k7hz` body, DEC-981). RUBRIC-2-APPLY §3
   puts the lines in **W2-33**, and tonight's line in `DAEO-lrre` is there. The body sentence should read W2-33; it is prose, not a KPI, so I left it.
3. **The acceptance tests in `w2/W2-60a`** fix one default per role (a Sonnet or Haiku engineer is refused). They are the
   test designer's and must be revised by an independent designer (Opus high, `Rewrite-Reason: DEC-1120`), never the
   engineer (RUBRIC-2-APPLY §3, DEC-866). The branch is also unreviewed against RUBRIC-2 and needs a merge of integrate
   (RUBRIC-2-APPLY residuals).

## 4. The three options

Figures are lead-hours (E), from P1-18 (W2-60a 5-8 more) and FORECAST-W2-3 (the RUBRIC-2 chain and W2-115 add 7-10 to
EXAMIN's path). Under usage (A) (DEC-1122 (2)) nothing here launches before the reset (11-15 09:00), so the cost
counts from then; the KPI edit alone is a short product-spec session.

| | 1. Apply now | 2. Defer | 3. Re-baseline |
|---|---|---|---|
| What happens | The lines of §2 go into W2-60a's KPIs; the designer revises the tests; the engineer builds on the branch after a merge of integrate; two C3 reviews. | W2-60a merges as specified (DEC-839: one default per role, a model that is not the role's refused). A follow-up ticket (new id, after W2-60a) takes §2's lines. CIT-E records the deferral. | W2-60a's spec is revised to what is built: one default per role; the launch record gains `criticality`, `tier` and any promotion reason as record-only fields; no new refusal. RUBRIC-2 runs through `launch_worker.sh` and W2-33's role lines. CIT-E records the new baseline. |
| Cost to W2-60a | **5-8 lead-h** more: KPI edit 1-1.5, test revision 1.5-2.5, build (with `criticality.yaml`) 2-3, two reviews 1-2 (E) | 0 more; it merges on its branch after the integrate merge (0.5-1) | **1-2** (KPI edit, small test change) |
| Cost elsewhere | None beyond W2-60b's one line (0.5), already written tonight | A new ticket: its own design, build and two reviews, 8-11 in all (E); part of W2-60a's refusal code is rewritten at once (2-3 wasted) | The product is not RUBRIC-2 until a later ticket: the full 8-11 comes back when it is wanted (W3), plus a second KPI change |
| Before EXAMIN's copy (DEC-1120 (5)) | Yes, in W2-60a (already in W2-27's closure) | Only if the follow-up lands first: one more ticket on the critical path, one more merge and close cycle (about 1 lead-day, E) | No. This is a change to the owner's DEC-1120 (5) and to DEC-1119 (2) |
| What `gov launch` does meanwhile | RUBRIC-2's table, promotion and trial | The role's one default; a Sonnet engineer on C2 refused | The role's one default; a Sonnet engineer on C2 refused |
| Main risk | W2-60a has had three review rounds; DEC-1010's two-round cap may need an owner word (as DEC-1105 gave W2-20). I read the new lines as a new scope, so the count restarts (E) | The dispatcher (W2-121) and every launch route by DEC-839 until the follow-up lands; a wrong tier is not refused | The owner's standing decision unmet in the product; EXAMIN's agents run on one model per role |

## 5. Recommendation

**Option 1, apply now. Confidence 75 %** (d-tools P-2 said 70 %; I raise it by five points because the branch needs a merge of integrate and a test revision in any case, so the lines cost little extra to build now).

Why:
- W2-60a is still in progress and already on EXAMIN's path, so the lines cost 5-8 lead-hours there and no new ticket.
- Option 2 spends 8-11 to get the same result, rewrites code that has just merged, and adds a ticket before EXAMIN's copy.
- Option 3 contradicts DEC-1120 (5) and DEC-1119 (2), which name W2-60a and the date. It is the cheapest now and the dearest later.
- The one thing that could change my mind: the owner reads DEC-1010's two-round cap as binding on W2-60a. Then option 1 needs one exception round, as DEC-1105 gave W2-20.

What I am least sure of: the hours (E, plus or minus 40 %); and whether `criticality.yaml` should be a project file or a kernel one (it holds this repository's paths, so I read it as a project file).

## 6. If the owner picks option 1: the steps (not done tonight)

1. A product-spec session replaces lines 3, 4 and 9, amends line 8, adds S4'' and the failure line, adds `governance/project/criticality.yaml` and its reader to `allowed_paths`, adds DEC-1119, DEC-1120 and DEC-1014 to `sources`, and fixes the body's "W2-11" to "W2-33". Marks: `[changed, DEC-1120 (5)]`. Commit trailers `Implements: DEC-1120, DEC-105`.
2. The independent test designer revises `tests/acceptance/W2-60a/` (`Rewrite-Reason: DEC-1120`).
3. Merge integrate into `w2/W2-60a`; the engineer builds; two C3 reviews (Opus high, then the probe at max).
4. W2-33's role-file lines (landed in `DAEO-lrre` tonight) and W2-60b's three keys (landed in `DAEO-ecac` tonight) already match; W2-60a before W2-60b, W2-33 before both.
