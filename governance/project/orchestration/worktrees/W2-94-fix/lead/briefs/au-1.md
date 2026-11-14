# W2-94 fix flow — the independent review of the launch script's one-question fix flow, the auditor's brief (DAEO-g87r)

You are a fresh, read-only independent auditor under **W2-94** (`DAEO-g87r`; the ticket, read-only:
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-g87r.md`; its text is at the end). You write nothing in the
repository. Your final message is the probe record's body; the lead commits it as
`docs/probes/DAEO-g87r/PR-DAEO-g87r-fix.md`.

## What you check (head `fac8d2026c732e5a2a47e6f2811b0870b53756d4` of `w2/W2-94-fix`, worktree `/home/usain/gov-os-worktrees/W2-94-fix`, base `340cd0efb`)
The owner decided **DEC-1180 (2)** (P-Q02-RUN-1 (a)): "the launch script gains a one-question fix flow that runs the
owner's approved q02 variant (0703aebf, DEC-1178 (5)) byte for byte unchanged: it stages only `q02.yaml`, the check's
reason code and round 1's sample, and replaces only `hidden/q02.yaml`." The ticket's KPI lines S6 to S12 and failure
lines F4 to F6 state it; the lead made the interface exact (below) before the work started.

- **The change under review:** `git diff 340cd0efb fac8d2026c732e5a2a47e6f2811b0870b53756d4 -- governance/project/orchestration/tools/indep_launch.py tests/unit/orchestration/test_w2_94_fix_flow_unit.py`
  (engineer commits `e48c99a67`, `560293740` (session `8ad38fe1-a1ed-4122-bb7c-2e684744584f`) and `fac8d2026`
  (session `ccf43198-9304-4f8f-a23e-26ed4e54856b`)).
- **The acceptance cases:** written first by the independent test designer (session
  `da4a1f0a-e7a6-4757-b070-fa7d0d63f36e`, commit `8a6beb7e4`, merged at `94e2ad773`):
  `tests/acceptance/W2-94/test_w2_94_fix_flow.py`, `w2_94_fix_support.py`, the README rows, and the variant fixture
  `tests/acceptance/W2-94/fixtures/EXAMIN-writer-q02-fix.md` (a byte copy of the approved variant, sha256
  `0703aebf69522cbb853d77f4e134e03843f1d961307b46c77ceaa575fa469173`).
- **The variant:** read the fixture above in full (front matter; sections 1 to 5).

## Questions to answer, each as findings with the two lines below
1. **Code against the lines.** Does the diff implement S6 to S12 and F4 to F6 exactly? For each line, say where (file
   and line) and whether a case covers it. Name anything the diff changes outside the fix flow (S12: every flow
   without `--fix` behaves as before).
2. **The variant and the flow agree.** Its front matter is accepted as written (no `sample:`; `rounds: 1` and
   `variant_of`); the wall gives it what its section 2 and 3 name (`input/q02.yaml`, `input/verdict.txt`,
   `input/sample.json`) and delivers what its section 5 names (`out/q02.yaml`, `out/result.json`, `out/conflicts.md`
   only on a stop). Also judge this: the variant tells the writer that the **fixed writer brief's** sections 3, 4, 5, 7
   and 9 apply to it in full, but the wall's tree leaves out `governance/project/indep-briefs/**` (the template's
   `tree-exclude.txt`), and only the variant is staged as `brief.md`. Can the walled writer read the fixed brief's
   rules at all? If not, what is the consequence for q02's run, and is it something this ticket's flow could or should
   fix within S7's "exactly three inputs", or a residual for the owner?
3. **Nothing hidden beyond the one question reaches the wall**, its result, its counts, the launch log, stdout or
   stderr (F4): read `plan_fix`, `round1_sample` and the staging in `build_and_run`; check that no other file of the
   set or the sets root is copied, and that the round-1 sample (paths of EXAMIN's tree, from the round-1 run's own
   archive) is the only thing read from the earlier run.
4. **The set is never left changed** except `hidden/<id>.yaml` on delivery (F5): read `deliver_fix`, `pack` and the
   refusal paths (`_after_refusal`); a refusal at any stage leaves every set file byte-unchanged; the old file is in
   the run's tar at `<run>/replaced-hidden/<id>.yaml` and nowhere under the set.
5. **Fail open?** Could a result or an `out/` of an honest but wrong session be delivered when it should be refused
   (S8, S9), or could the flow replace the wrong file?
6. **Points the lead names for your judgement:** (a) `out/conflicts.md` beside a good (not stopped) result refuses 20
   (the KPI lists conflicts.md among the files `out/` may hold; the variant says "only if you stop"); (b) to keep
   W2-149's pinned count of 10 documented `python3 ` lines, the `--dry` usage line was folded into prose and `--fix`/
   `--reason` are hidden from `--help`'s option list (`argparse.SUPPRESS`); (c) the counts schema
   `indep-schemas/indep-counts.schema.json` is closed and outside the ticket's paths, so a fix run's counts (with
   `fix`) do not validate against it (`finish()` logs "counts schema failed"; `--counts-only` of a fix run refuses
   17); (d) `fix` appears in the counts from the argument check on, `action` null until the result passes.

You may run the suites on their planted stand-ins only, from your sandbox's `$TMPDIR`:
`env HOME=<an empty folder under your $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-94-fix/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/orchestration/test_w2_149_indep_launch.py tests/unit/orchestration/test_w2_173_indep_launch.py tests/unit/orchestration/test_w2_178_indep_launch.py tests/unit/orchestration/test_w2_94_fix_flow_unit.py tests/acceptance/W2-94/test_w2_94_fix_flow.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --tb=short`
(the engineer's run at this head: 187 passed; if the slot tool cannot run in your sandbox, run the same pytest without
it and say so; a resource gate's refusal is a wait). You may copy the script into your `$TMPDIR`, change one thing
there, and point the acceptance cases at the copy with env `W2_94_FIX_SCRIPT=<copy>` to see a case turn red.

## Walls (hard)
Never open, list, grep or print anything under `/home/usain/gov-os-eval/`, `/home/usain/gov-os-runs/`, any folder
named `hidden` outside your `$TMPDIR`, any `fixtures/evaluation/examin/visible` or `hidden` folder of any tree, the
owner's EXAMIN copy or EXAMIN's real repository. You need none of them. No GPU, model, network or installs; no real
`claude` session. One simple command per Bash call; longer things in a script file under your sandbox's `$TMPDIR`
(`/tmp` is read-only in the sandbox). Refused twice for the same call by the guard, the sandbox or a hook: stop and say
so; never work around a refusal. No `gov retrieve` or `gov context`: search with Read and Grep, and search again once in
different words if the first does not answer.

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

## The fix flow's interface, as the lead gave it to the test designer and the engineer

Script: `governance/project/orchestration/tools/indep_launch.py`. Names below: `<root>` the sets root, `<set>` the
`--set` name, `<runs>` the runs dir (`GOV_INDEP_RUNS_DIR`, default `~/gov-os-runs`), `<walls>` = `<root>/indep-walls`,
`<setdir>` = `<root>/fixtures/evaluation/<set>`.

1. **Flags (S6).** `--fix <id> --reason <code>`. Valid only together, only with `--kind writer --round 2`, never with
   `--counts-only`. `<id>` fully matches `q[0-9]{2}`. `<code>` is exactly one of `SOURCE_IS_SCAFFOLD`,
   `SOURCE_PATH_ABSENT`, `SOURCE_NOT_TEXT`, `SPAN_OUT_OF_FILE`, `HEADING_NOT_FOUND`, `ANSWER_NOT_IN_SPANS`,
   `NONEXISTENT_NAME_FOUND`, `NONEXISTENT_NO_NAME`. Any other form (either flag alone, another kind, round 1 or no
   `--round`, a bad id such as `q2`, `Q02`, `q002`, `q0a`, an unknown or lower-case code) exits **17** with nothing built:
   no wall, no tree, no run folder under `<runs>/indep/`, no SEEDS.log line (the existing `nothing_built` state).
2. **The brief's front matter (S10).** A fix run accepts the approved variant's front matter as written: it names
   `kind: writer`, `version`, `variant_of`, `rounds: 1`, `tools`, `model`, `effort`, `result_schema`, `budget_usd`,
   `timeout_s`, and **no `sample:`**. In a fix run a front matter without `sample:` is accepted (the wall's own
   `input/selection.json`, a fixed file, then has an empty `sample`); `rounds` and `variant_of` are not judged. The
   brief is still checked as today: its bytes at `--commit` equal `--brief-sha256`, and the sets root's
   `indep-walls/APPROVED` has its `brief` line for kind writer (else 10). Without `--fix` nothing about front matter
   changes.
3. **Staging (S7, F4).** Read and checked before anything is written (a refusal here is **10** with nothing built):
   - `input/<id>.yaml`: a byte copy of `<setdir>/hidden/<id>.yaml`; absent, a folder, or a link (the file or any folder
     on its way) refuses 10.
   - `input/verdict.txt`: exactly the bytes `<id> <code>\n` (one line, one trailing newline).
   - `input/sample.json`: a JSON object `{"sample": [...]}` whose list is, in order, the `sample` list of
     `input/selection.json` as staged in the **latest delivered round-1 writer run of the same set**. Found thus: every
     `<runs>/indep/writer/<rid>/counts.json` whose object has `"status": "delivered"`, `"round": 1`, `"set": <set>`
     (and `<rid>` matching the script's run-id form for that set and round 1); the latest is the greatest `<rid>` (the
     run id starts with its UTC time). That run's own record is its archive `<walls>/writer/<rid>.tar`; the list is read
     from its member `<rid>/input/selection.json` (a regular member, size-capped, parsed strictly; its `sample` a list
     of strings). No such run, no archive, no member, or a member that does not parse to that form refuses 10. Tests
     compare the parsed object, not the bytes.
   - Nothing else of the set or the sets root is staged: no `input/set/`, no `input/notes.md`, no other question, no
     `DRAW.txt`, no `XCHECK-r*.md`. The wall after staging holds exactly the 7 fixed files (`seed.txt`, `brief.md`,
     `CLAUDE.md`, `WALL.json`, `input/selection.json`, `.claude/settings.json`, `.claude/wall_hook.py`), these three,
     and an empty `out/`.
4. **Delivery (S8, F5).** After the session, `out/` may hold only `out/<id>.yaml`, `out/result.json` and (only on a
   stop) `out/conflicts.md`; any other entry (another file, a folder, a link) refuses **20**. `out/<id>.yaml` must be a
   regular file (not a link) whose YAML parses (safe load) to a mapping with `id` equal to `<id>`, else 20. On delivery
   only `<setdir>/hidden/<id>.yaml` is replaced by `out/<id>.yaml`'s bytes; every other entry under `<setdir>` (both
   halves, `hidden/visible/`, `visible/`, `DRAW.txt`, `hidden/dropped/`, any `XCHECK-r*.md`, `.release-visible.record`)
   is byte-unchanged and no entry is added (no temporary name left). The replaced file is packed into the run's
   archive `<walls>/writer/<run>.tar` as the member `<run>/replaced-hidden/<id>.yaml` (the existing `replaced-hidden`
   folder of `pack()`), and is not left anywhere under `<setdir>`. Every refusal (20, 21, or any other code) leaves
   every file under `<setdir>` byte-unchanged, `hidden/<id>.yaml` included.
5. **The result (S9).** `out/result.json` is the writer schema's (`questions`, `by_kind`, `by_area`, optional
   `stopped`) plus `action`, one of `corrected` or `replaced`. A result whose `stopped` is present and not `none`
   delivers nothing: **21** (as today). Otherwise each of these refuses **20**, nothing delivered: `action` absent or
   another word; `questions` not exactly the integer 1; the numbers of `by_kind`, or of `by_area`, not summing to 1;
   the schema failing.
6. **The counts (S9, F4).** A fix run's counts object (stdout's last line and `counts.json`) carries
   `"fix": {"id": <id>, "code": <code>, "action": <action>}`, where `action` is the result's word once the result has
   passed its checks and `null` otherwise; nothing of the question's content (no question, answer, path, span or
   heading text) appears anywhere in the counts, the launch log or stdout/stderr. A run without `--fix` has no `fix`
   key (S12). Known gap, carried by the lead as a package: `indep-schemas/indep-counts.schema.json` is closed
   (`additionalProperties: false`) and outside the ticket's paths, so a fix run's counts do not validate against it;
   do not assert that schema on a fix run's counts (assert the keys and values instead), and do not edit the schema.
7. **The usage line (S11).** The script's docstring gains one usage line for the fix flow, naming only `--sets-root
   <root>` as a path, in the form of the existing lines, e.g. `python3 governance/project/orchestration/tools/indep_launch.py
   --sets-root ~/gov-os-eval --kind writer --brief <path> --brief-sha256 <sha> --commit <commit> --set examin --round 2
   --fix q02 --reason ANSWER_NOT_IN_SPANS`.
8. **Unchanged (S12, F6).** Without `--fix`, every existing flow behaves exactly as before; `governance/project/indep-walls/**`,
   `governance/project/indep-briefs/**` and `indep-schemas/**` are not changed. The variant runs at sha256
   `0703aebf69522cbb853d77f4e134e03843f1d961307b46c77ceaa575fa469173`, byte for byte.

## Return (your final message, in full)
The twelve labelled fields (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons,
proposed_decisions, unresolved, recommended_next_action; sandbox and `ps` checks first), then **the probe record's
body** (no front matter; the lead adds it): what you probed (head `fac8d2026c732e5a2a47e6f2811b0870b53756d4`), how, each finding (id, the KPI line,
what and where with file and line, `Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`,
scope in|out), and, last, the fenced `verdict` block in this form:
```verdict
{"kpis": [{"kpi": "S6", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ...]}
```
covering S6, S7, S8, S9, S10, S11, S12, F4, F5 and F6, and S1 to S5 and F1 to F3 as `pass` only if you find nothing in
this change against them (they were reviewed before; this change does not touch their files). Your overall judgement:
`pass` or `fail`.

## The decisions it applies (from the register, by id)
- DEC-1180 (2): quoted above. DEC-1178 (5): "`approve q02 variant 0703aebf`: the writer's fix brief for hidden question
  q02 (`drafts/q02-writer-r2/EXAMIN-writer-q02-fix.md`); then the writer's round 2, the checker and `check_gold`
  (expect 20 of 20) by the owner's operator." (DEC-1180 (2) later: no checker run.) DEC-820: reads are open; only
  secrets, the held-out material's contents, the counterpart's work and the hidden half of an evaluation set are refused.
  Read any other id in `/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md` by grepping its id.

## The ticket (read-only copy)
```
---
id: DAEO-g87r
status: in_progress
deps: [DAEO-m1u3]
links: []
created: 2026-10-30T22:14:09Z
type: task
priority: 1
assignee: independent-auditor
external-ref: W2-94
tags: [wave-2, audit, evaluation, held-out, standard, examin-minimum]
wbs_id: W2-94
title: 'EXAMIN''s question set: memory questions with gold sources about the owner''s copy, a visible and a hidden half, by a session independent of the adopting team, before W2-27'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: [DAEO-m1u3]
allowed_paths:
- tests/acceptance/W2-94/**  # its acceptance tests, form only (CTO, DEC-1167 (3): the close)
- fixtures/evaluation/examin/check_gold.py  # S4's counts-only script, by the independent test designer, run by the CTO with --sets-root
- docs/probes/DAEO-g87r/**  # the probe record
- fixtures/evaluation/examin/visible/**
- fixtures/evaluation/examin/hidden/**
- governance/project/orchestration/tools/indep_launch.py  # the one-question fix flow (reopen 2026-11-14, DEC-1180 (3))
- tests/unit/orchestration/test_w2_94_fix_flow_unit.py  # the engineer's unit tests of the fix flow
kpis:
  success:
  - 'Between 10 and 20 questions about EXAMIN''s code and governance, each with its gold answer and the source or sources an answer must cite (file and section or line), in the form W2-61''s visible half takes; after writing, a recorded seeded draw, stratified by category, splits the set into a development half (`hidden/visible/`) and a hidden half, both written by the walled writer inside the hidden folder; the owner''s release step (`release_visible.sh`) then copies the development half into `visible/` Verify: a planted stand-in set: a count outside 10 to 20 is refused; the record holds the seed and the draw; the two halves each hold half (within one) with each category in both halves; the release step copies exactly the development half into `visible/` and refuses a second release [DEC-957, DEC-828 items 3 and 4, DEC-954 Q9f]'
  - 'Written by the walled writer from the wall''s tree, `git archive` of the CTO''s launch clone of the owner''s copy, made by exact path under ~/gov-os-runs/W2-94/examin/ with one scaffold commit (the walls'' template files, `COPY-HEAD.txt`, a path map holding only `sets_root_hidden`, the brief); the copy is only read by that clone; nothing written in the workbench or in EXAMIN''s real repository Verify: the record names the clone''s path under `~/gov-os-runs/W2-94/examin/` and `COPY-HEAD.txt` names the copy''s commit; after the run `git status` in the workbench and in EXAMIN''s real repository shows no change, and the owner''s copy''s file times are unchanged [DEC-723, DEC-728]'
  - 'Written by the walled writer session (the approved brief `governance/project/indep-briefs/examin-sets/EXAMIN-writer.md`; no shell or network; counts only returned), independent of the adopting team: no session of W2-26, W2-27, W2-88 or a retrieval ticket writes or reads the hidden half; nothing hidden quoted in a commit message, a return, a log or a ticket note Verify: the walls'' launch log names the approved brief''s sha256; the guard''s log shows no session of W2-26, W2-27, W2-88 or a retrieval ticket opened the hidden folder; a grep of commit messages, return, log and ticket notes for a planted unique question word finds 0 hits [DEC-820 (d), DEC-845]'
  - 'Every gold source exists at the copy''s recorded commit and holds the answer Verify: a counts-only script, written by the ticket''s independent test designer and run by the CTO with `--sets-root` (the writer has no shell), prints only counts and ids: for each question, its gold source exists at the copy''s recorded commit and holds the answer ("n of n hold"); a planted source that is absent or does not hold its answer is reported by id [DEC-828 item 4]'
  - 'W2-61''s KPI 6 ("the same split for EXAMIN''s set") is met by this ticket; W2-61''s close record names it as moved here Verify: a grep of W2-61''s close record finds KPI 6 named as moved to W2-94; this ticket''s visible and hidden folders hold the split of S1 [DEC-954, DEC-957]'
  - 'S6 A writer round 2 run with `--fix <id> --reason <code>` (`--kind writer --round 2` only; `<id>` matches `q` and two digits; `<code>` is one of check_gold.py''s per-question failure codes SOURCE_IS_SCAFFOLD, SOURCE_PATH_ABSENT, SOURCE_NOT_TEXT, SPAN_OUT_OF_FILE, HEADING_NOT_FOUND, ANSWER_NOT_IN_SPANS, NONEXISTENT_NAME_FOUND, NONEXISTENT_NO_NAME) is the one-question fix flow; either flag alone, another kind or round, a bad id or an unknown code refuses 17 with nothing built. Verify: planted runs of each wrong form, exit 17, no wall and no run folder made'
  - 'S7 The fix flow stages exactly three inputs: `input/<id>.yaml` (a byte copy of the set''s `hidden/<id>.yaml`; absent or a link refuses 10), `input/verdict.txt` (the one line `<id> <code>`), and `input/sample.json` (`{"sample": [...]}`, the ordered `sample` list of the selection staged in the latest delivered round-1 writer run of the same set, read from that run''s own record; none found refuses 10); besides the wall''s fixed files, nothing else of the set or the sets root is staged (no `input/set/`, no `input/notes.md`). Verify: a planted set of several questions, the wall''s file list and bytes after staging'
  - 'S8 The fix flow delivers only `out/<id>.yaml`: a plain file whose YAML parses to a mapping with `id` equal to `<id>`, else 20 and nothing lands; any file in `out/` other than it, `result.json` and `conflicts.md` refuses 20. On delivery it replaces `hidden/<id>.yaml` alone; every other file under the set''s folder (both halves, `DRAW.txt`, `hidden/dropped/`, any `XCHECK-r*.md`, the release record) is byte-unchanged; the replaced file is packed into the run''s archive and removed from the set. Verify: sha256 of every planted file before and after; the archive holds the old file'
  - 'S9 The fix flow''s result is the writer schema''s (`questions`, `by_kind`, `by_area`, optional `stopped`) plus `action`, one of `corrected` or `replaced`; `questions` is 1 and each of `by_kind` and `by_area` sums to 1, else 20; a stopped result delivers nothing (21, as today). The counts object records `fix: {"id": <id>, "code": <code>, "action": <action>}` and nothing of the question''s content. Verify: planted results of each wrong form; the counts object''s keys'
  - 'S10 The owner''s approved variant (`EXAMIN-writer-q02-fix.md`, sha256 0703aebf69522cbb853d77f4e134e03843f1d961307b46c77ceaa575fa469173) launches through the fix flow end to end, byte for byte unchanged, on a planted sets root and launch clone with the fake session: its front matter is accepted as written. Verify: the planted end-to-end run, exit 0, the delivered file in place'
  - 'S11 The script''s docstring gains the fix flow''s usage line; `governance/project/indep-walls/**` and `governance/project/indep-briefs/**` are unchanged (the owner''s class O). Verify: `git diff --stat` of the branch names only the ticket''s paths'
  - 'S12 Without `--fix`, every existing flow behaves as before. Verify: the W2-149, W2-173 and W2-178 launcher unit suites pass unchanged'
  failure:
  - 'A hidden question or answer readable by a measured session by a route an honest agent takes in ordinary work. Verify: a planted stand-in hidden file: a read, a grep and a `git log` from a measured session''s sandbox (the guard''s path map) are refused or find it 0 times'
  - 'A write in the workbench, the owner''s copy or EXAMIN''s real repository; a clone outside ~/gov-os-runs/W2-94/. Verify: `git status` in the workbench, the owner''s copy and EXAMIN''s real repository shows no change after the run; a `find` for a clone of the copy outside `~/gov-os-runs/W2-94/` finds none'
  - 'A gold source that does not hold its answer. Verify: the S4 script on a planted source that does not hold its answer reports that question''s id as failing'
  - 'F4 A hidden file other than the fixed question reaches the fix flow''s wall, its result or its counts. Verify: S7''s planted wall listing; a grep of the counts object for planted content markers'
  - 'F5 A fix run changes, moves or removes any set file other than `hidden/<id>.yaml`, or leaves the set changed after a refusal. Verify: S8''s sha256 comparison, also after a planted refusal at delivery'
  - 'F6 The fix flow needs a change to the approved variant''s bytes or to the walls'' class O files to run. Verify: S10 runs the variant at its approved sha256; S11''s diff'
profile: STANDARD
sources:
- DEC-957
- DEC-1175
- DEC-1178
- DEC-1180
- DEC-954
- DEC-828
- DEC-820
- DEC-845
- DEC-723
- DEC-728
est_loc: 0
acceptance_tests:
  path: tests/acceptance/W2-94/
  author: independent-test-designer (MR-3); form only (count, fields, sources named), never printing a question or an answer
track: B
list_rows: []
---
# W2-94 EXAMIN's question set

Card: MEMORY-SPEC-MAP gap 7, resolved by the owner in DEC-957; W2-61's KPI 6 moves here. The set measures memory on EXAMIN's copy at W2-27 (with W2-88's tools) and W2-15b.

- **Before it starts, the orchestrator adds an `evaluation_sets` entry** `examin` to the path map (`visible: fixtures/evaluation/examin/visible/**`, `hidden: fixtures/evaluation/examin/hidden/**`, `measures` by tickets: W2-26, W2-27, W2-88, W2-15b and the retrieval tickets), so the guard refuses the hidden half from every worktree (W2-84).
- **The clone:** made by the orchestrator or the auditor by exact path, `git clone --no-hardlinks` from the owner's copy (DEC-723, DEC-728); removed at the end.
- **Started by the orchestrator,** never by an adoption or retrieval ticket's lead.
- **Verify re-worded (CTO, 2026-11-13, DEC-1157 (12), DEC-1167 (3)):** S3's brief path is where it is installed; S4's script is the test designer's, run by the CTO (the walled writer has no shell); the KPI text before each Verify unchanged except the brief's path.

**Role changed 2026-11-13 (P-W2-94-GOLD-2 (A), the CTO):** class audit -> implementation and role independent-auditor -> engineer, so the launcher lets the engineer the owner's W2-94 GOLD (a) names change `check_gold.py`; the walled writers' delivery is done, and the narrow check stays independent.

**Reopened 2026-11-14 (DEC-1180 (3), the owner's P-Q02-RUN-1 (a): "run today, as soon as it is built and reviewed").** Hidden question q02 fails the gold check (ANSWER_NOT_IN_SPANS). The owner approved the writer's fix variant 0703aebf (DEC-1178 (5)), but the launch script's writer round 2 stages the whole set plus a checker's notes (EXAMIN's round 1 had none) and replaces the whole hidden folder, so the variant cannot run. S6-S12 add a one-question fix flow to `indep_launch.py`, which changes by a ticket (the class rules' catch-all), not an ACT; the walls' `kinds.yaml` and the briefs stay unchanged. After the land, the owner's operator installs the variant (its APPROVED line), commits it into the launch clone, runs the fix flow and `check_gold.py` (expected 20 of 20). No checker run: round 1 had none (FOR-THE-OWNER C8), and `check_gold` is the bar. The same flow can later carry the weekly re-anchor request (DECIDED-NOT-DONE row 203).
```
