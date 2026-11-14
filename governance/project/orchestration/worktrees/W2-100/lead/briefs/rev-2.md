# W2-100 (DAEO-uw5h), independent auditor: the narrow check of the follow-up to the first check's F1 and F3

**Role:** independent-auditor, a fresh read-only session. Write nothing in any tree; your verdict goes in your return.
**Worktree:** `/home/usain/gov-os-worktrees/W2-100`, branch `w2/W2-100`. **Probe:** head `f7637bd03e25`.
**Ticket:** `DAEO-uw5h` (W2-100), profile STANDARD, class C2: four kernel skills (backend, api, data, security), each
the engineer's skill for its area. Its text, with its twelve KPI lines and its `## Interface`, is
`/home/usain/gov-os-worktrees/W2-100/.tickets/DAEO-uw5h.md`; its sources DEC-959, DEC-957, DEC-832, DEC-616, DEC-645,
CAP-24.b, DEC-315, DEC-1112 (read each by id in `/home/usain/gov-os-worktrees/W2-100/docs/DECISION_REGISTER.md`, grep
only by id). The lead's reading of the interface:
`/home/usain/gov-os-worktrees/W2-100/.gov-runtime/scratch/lead/briefs/interface-reading.md`.

## Why this check

A first narrow check (a fresh independent auditor, session `ed998176-b05d-4462-acf4-bb4a4ede09e4`) probed
`f8e7c0fad6c6`: all twelve KPI lines pass, no blocking finding. Its in-scope rows: **F1** run 5's twelve passes were
made with `scenario-summaries.md` in the session's skill folder (the harness copies every file but `scenarios.md` and
the record), not disclosed; **F3** api scenario 2 had one clean fail and one borderline clean pass. (F2, the harness
handing future runs the summaries, is out of scope: a package to the CTO. F4 and F5 are rows.) Its record:
`/home/usain/gov-os-worktrees/W2-100/.gov-runtime/scratch/lead/log/rev-1.json` (`result`).

The lead's follow-up, and only this is under review (`git log f8e7c0fad6c6..f7637bd03e25`):
1. **Clean run 6** (03:17-03:21 UTC, all four skills at 1.0.1), every `scenario-summaries.md` moved out of the four
   skill folders for the run and put back after (`.gov-runtime/scratch/lead/run6_clean.sh`; the folders' listing
   during the run in `.gov-runtime/scratch/lead/skilleval/summaries-aside/folders-during-run.txt`): backend and
   security 3/3; api scenario 2 and data scenario 2 judged FAIL (the session's and the judge's full replies:
   `.gov-runtime/scratch/lead/skilleval/fail-api-2-run6.md`, `fail-data-2-run6.md`).
2. `3318e42f6` (product-spec, fix batch 3, given the failing output only): api and data to 1.0.2: a breaking change
   asked for within a published version is made additive where it can be, with a backward-compatibility test naming
   the old client and shape; the return names each test with its input.
3. `05fcc8f2e` (product-spec, fix batch 4, the lead's call before any run at 1.0.2): the two examples fix 3 added had
   quoted the scenarios' own nouns (`/v1/orders/{id}`, `total`, `shipment_id`); replaced with neutral ones; still 1.0.2.
4. **Clean runs 7 and 8** of api and data at 1.0.2 (`run_clean.sh 7 api data`, `run_clean.sh 8 api data`; listings in
   `skilleval/summaries-aside-7/` and `-8/`): 3/3 each, both runs.
5. `f7637bd03` (product-spec, summaries batch 4): the records of runs 6-8 (the harness's output) and their summaries;
   each summaries file's opening paragraph now states F1 and that runs from 6 on were clean; the `.rulesync` copies.

Run envelopes: `.gov-runtime/scratch/lead/skilleval/<skill>-<run>.json`; the captured replies (pass-through `claude`
on `PATH`): `skilleval/transcripts/`; the index the summaries were written from: `skilleval/transcripts-index.md`.

## Check

1. **The 1.0.2 text** (`git diff f8e7c0fad6c6 f7637bd03e25 -- template/governance/kernel/skills/api/SKILL.md template/governance/kernel/skills/data/SKILL.md`):
   is it method guidance an engineer in the area should follow anyway, not wording aimed at the judge? Does any
   phrase in any of the four SKILL.md files carry a scenario's specific endpoint, field, table, file or value (compare
   with each `scenarios.md`)? Each SKILL.md still passes its own `check_domain_skill.py` (PASS), the validator
   (`python3 -m gov.check.skill_validator`, this tree's `src/`) exits 0 on the four folders, the template's sections and
   the five parts and named points stand, body within about 150 lines, `version` equal to `metadata.version` (api and
   data 1.0.2; backend and security 1.0.1, unchanged since `121c99a44`), no permission line, security untouched.
2. **Clean runs:** the summaries were out of the skill folders during runs 6, 7 and 8 (the listings; the run times
   against the records' `run_at`), and no run 6-8 session reply mentions reading `scenario-summaries.md` (search the
   transcripts by time: stems from `20261114T0317` on).
3. **Records:** the committed records equal the envelopes of runs 6-8 in content and order, appended after the earlier
   entries, which are unchanged since `b3503e0a3`; run 6's two fails stand in the record and their summaries.
4. **Summaries:** each new entry matches its record entry (scenario, title, verdict, run_at), three lines, and agrees
   with the captured reply and, for a fail, the judge's reason (sample at least api 2 and data 2 of runs 6 and 7, and
   one backend and one security entry of run 6); the opening paragraph states F1 truthfully; earlier entries unchanged.
5. **F1 and F3 settled?** For each skill, is there now a clean run at the skill's current version with three passes
   (backend and security: run 6 at 1.0.1; api and data: runs 7 and 8 at 1.0.2)? Is api scenario 2 still borderline?
6. **Copies and scope:** `diff -r` of each skill folder against both `.rulesync` copies is empty; `python3 -m
   gov.adapters.portability` (in the tree) gives no `SOURCE_*` finding (its `GENERATED_DIFFERS` are the `.claude/skills/`
   copies of the copies ACT); `git diff --stat f8e7c0fad6c6 f7637bd03e25` touches only the four skills' folders and
   their copies; every commit carries `Task: DAEO-uw5h`, `Role: product-spec`, `Implements:` naming only the ticket's
   sources, all trailers in one final block.
7. **Tests (optional; the lead runs them):** if you run any, use a `--no-hardlinks` clone of the tree at the probed
   head in your own TMPDIR, through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
   with `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`, and
   `-m "not local_only" -k "not real and not green_here and not time_limit"`; remove the clone at the end (`chmod -R u+w`
   first). Never a model call.

Out of scope: everything the first check probed at `f8e7c0fad6c6` and did not flag, and the harness (F2).

KPI id for the verdict block: `w2-100-narrow-2` (one entry).

## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.
- **How reviews converge (owner, standing, DEC-1010 item 1; in force for the CTO, every lead, reviewer and QA engineer):**
  - **A moderator, not a circle of reviewers:** the QA engineer (or the Senior Engineer; until the three layers start, the CTO) triages every finding against the ticket's own scope and KPIs. A finding outside the scope, or one that needs an unusual construction, becomes a Wave 3 row, never a round.
  - **A finding blocks only if it is in scope, reachable in ordinary work, and fails open or loses work.** Everything else lands as a recorded row.
  - **At most two review rounds.** If something still blocks after that, it goes to the owner once, with options; no more routine exceptions.
  - **READY is computed by code, not declared by an agent:** each reviewer returns a structured verdict per KPI line, a fenced `verdict` block in the probe record: `{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`; the close (and the merge queue's pre-check) computes READY from it: no finding that is in scope, ordinary work yes and fails open or loses work. A lead never writes a verdict over a reviewer's.

Every finding also carries `scope: in` only if it concerns the follow-up under review (items 1 to 5 above).

## Write and return
- You write nothing in any tree (your own TMPDIR only, and only by Bash; if a write is refused, do the work in memory
  and report the refusal). Single simple Bash commands. No shell variable or `$(…)` as a write target, no
  here-document, no `bash -c`. Every wait by pid only.
- Reads (DEC-820): open, except secrets and keys (never read or printed), the held-out qualification material's
  contents, and the hidden half of any evaluation set: never open anything under `~/gov-os-eval/`, an evaluation set's
  root, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder. You search with the Read and Grep tools, naming
  the folder a search starts at; search once more in other words if the first does not answer, then say "not found".
- Refused twice for the same call: stop and say so; never work around a refusal by another tool or form.
- Commit hashes as 12 digits, never the full 40. There is no token cap.
- **Your record is your session's final message**, in full: the twelve labelled fields first (task, status,
  work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved,
  recommended_next_action), your session id and the probed commit in `evidence`; your answers to checks 1 to 6 (and 7
  if run); every finding with its two lines and scope; then `REVIEW_MD_BEGIN`, the review record in markdown,
  `REVIEW_MD_END`; at the end the fenced `verdict` block
  `{"kpis": [{"kpi": "w2-100-narrow-2", "verdict": "pass|fail", "findings": [...]}]}`, each finding
  `{"id", "scope", "ordinary_work", "consequence"}` (ids from N1).
- Estimate: 30 minutes.
