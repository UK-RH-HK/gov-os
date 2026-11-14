# W2-94 S13: the narrow independent check of the counts schema's fix object and the --help epilog fix, the auditor's brief (DAEO-g87r)

You are a fresh, read-only independent auditor under **W2-94** (`DAEO-g87r`; the ticket, read-only:
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-g87r.md`; read its last paragraph and KPI line S13). This is a
**narrow independent check of this change only** (DEC-1156 (7)): the fix flow itself was reviewed and passed at
`fac8d2026` (`docs/probes/DAEO-g87r/PR-DAEO-g87r-fix.md`); do not re-review it. You write nothing in the repository.
Your final message is the probe record's body; the lead commits it as `docs/probes/DAEO-g87r/PR-DAEO-g87r-s13.md`.

## What you check (head `ff6ba10be89a` of `w2/W2-94-fix`, worktree `/home/usain/gov-os-worktrees/W2-94-fix`, base `5285ef173`, the merge of `w2/integrate`)
**DEC-1180 (4)**, standing (quoted from the register): "Do now everything that can be done now. Nothing waits for the
next morning, the next digest or a later batch, and a defect spotted is fixed in the same flow." Under it the CTO kept
W2-94 open and added **S13** for the fix-flow review's finding P4 (the closed counts schema refused the fix flow's `fix`
key):

> S13 The counts schema takes the fix flow's `fix` key (rv P4, 2026-11-14): `indep-counts.schema.json` allows an
> optional `fix` object with exactly `id` (a question id), `code` (the reason code) and `action` (`corrected` or
> `replaced`), and nothing else; a fix run's counts validate, so `finish()` no longer logs "counts schema failed" and
> `--counts-only` of a fix run no longer refuses with 17; every other flow's counts validate as before. Verify: a fix
> run's counts with `fix` validate; a `fix` with an extra key or another action is refused; the W2-149 counts cases pass
> unchanged.

The change under review: `git diff 5285ef173 ff6ba10be89a`:
- **The acceptance cases**, written first by a fresh independent test designer (session
  `8cce39f1-b5c5-48c4-95cc-4ed74716dd19`, commit `0af5f2e1f`, merged at `382924bd3`):
  `tests/acceptance/W2-94/test_w2_94_s13_counts_fix.py` (new), the revised S11/F6 diff case in
  `tests/acceptance/W2-94/test_w2_94_fix_flow.py`, and the README rows. 36 of them were red on the merged base.
- **The schema change**, by a fresh engineer given only the failing output (session
  `ba14df3b-d2a2-4bf0-b9a5-713521dc78e6`, commit `46eb8bf11`):
  `governance/project/orchestration/tools/indep-schemas/indep-counts.schema.json`.
- **The `--help` epilog fix**, by a second fresh engineer given only the failing output (session
  `f081d54b-ed1e-4af7-9f60-596c543e16a5`, commit `ff6ba10be`): `governance/project/orchestration/tools/indep_launch.py`
  `parse_args`. The red it fixes was `tests/acceptance/W2-149/test_w2_149_seed_content.py::test_s5_the_argument_parser_offers_no_path_or_path_list_option`
  ("options beyond the interface's: ['--fix', '--reason']"). It came in with the fix flow at 0b43625da: the docstring's
  fix-flow usage line starts with `python3 ` and the epilog copied it. The fix-flow review and the lead's earlier scoped
  run missed it.

## Questions to answer, each as findings with the two lines below
1. **The schema against S13.** Does `fix` take exactly `id`, `code`, `action`, all required, nothing else? Is `id` a
   question id (`q` and two digits), `code` exactly check_gold.py's eight per-question failure codes (the same list as
   the launcher's), `action` `corrected`, `replaced` or `null`? Does every counts object without `fix` validate as
   before?
2. **The lead's reading of `action: null`.** The lead made the interface exact before the pair started: `null` is
   allowed, because the landed fix flow writes `action: null` until the result has passed its checks (a dry run, a
   refusal at the result, a stop). The KPI says "`action` (`corrected` or `replaced`)" and also "a fix run's counts
   validate, so `finish()` no longer logs 'counts schema failed'". Judge whether allowing `null` is the right reading.
   If it is not, what follows (a dry or refused fix run's counts would fail the schema)?
3. **The cases.** Do the S13 cases check each part of the KPI line (validate, refused forms, as before, the log line,
   `--counts-only`)? Is each red for the stated reason on the base? Is the S11/F6 revision (only
   `indep-counts.schema.json` may differ under `indep-schemas/`) exactly what S13 needs and no wider?
4. **The epilog fix.** Does `--help` now name no fix-flow flag, while the docstring keeps the fix-flow usage line (S11)
   and the W2-149 unit cases that pin the documented lines and the option list still pass? Does any flow without
   `--fix` change (S12)?
5. **The open path case (judge it; the lead sends it to the CTO).** `tests/unit/orchestration/test_w2_149_indep_launch.py::test_counts_schema_closes_every_object_and_string`
   is red after the schema change: it requires every root property to be in `required`, except the keys in a hard-coded
   `optional` map, so any optional root key fails it. That file is outside W2-94's allowed paths. The engineer did not
   restructure the schema to get round the check (for example, `fix` under `patternProperties` would be
   schema-equivalent but outside the case's `properties` walk). The lead's proposal: a one-line revision of that case,
   `optional` gaining `id(whole): {"fix"}`, made through the CTO's path case. Judge (a) whether S13 makes that case's
   pin a contradiction that needs a test revision, (b) whether the one-line revision is the narrowest correct one, and
   (c) whether the `patternProperties` form would be acceptable or would defeat the case's purpose.

You may run the suites on their planted stand-ins only, from your sandbox's `$TMPDIR`:
`env HOME=<an empty folder under your $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-94-fix/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-94/ tests/acceptance/W2-149/ tests/acceptance/W2-173/ tests/unit/orchestration/test_w2_149_indep_launch.py tests/unit/orchestration/test_w2_173_indep_launch.py tests/unit/orchestration/test_w2_178_indep_launch.py tests/unit/orchestration/test_w2_94_fix_flow_unit.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --tb=short`
(the engineer's run at this head: 952 passed, 1 failed (the case of question 5), 37 skipped; if the slot tool cannot
run in your sandbox, run the same pytest without it and say so; a resource gate's refusal is a wait). You may copy the
schema or the script into your `$TMPDIR`, change one thing there, and point the W2-94 fix cases at the copy with env
`W2_94_FIX_SCRIPT=<copy of indep_launch.py>` (its `indep-schemas/` folder must sit beside it) to see a case turn red.

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


## Return (your final message, in full)
The twelve labelled fields (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons,
proposed_decisions, unresolved, recommended_next_action; sandbox and `ps` checks first), then **the probe record's
body** (no front matter; the lead adds it): what you probed (head `ff6ba10be89a`), how, each finding (id, the KPI line,
what and where with file and line, `Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`,
scope in|out), your judgement on question 5's path case, and, last, the fenced `verdict` block in this form:
```verdict
{"kpis": [{"kpi": "S13", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ...]}
```
covering S13, S11 and S12 (the epilog fix and the S11/F6 case revision touch them), and the other lines (S1 to S10, F1
to F6) as `pass` only if you find nothing in this change against them (they were reviewed before; this change does not
touch their code). Your overall judgement: `pass` or `fail`.

## The decisions it applies (from the register, by id)
- DEC-1180 (4): quoted above. DEC-1180 (2): the launch script gains a one-question fix flow (reviewed at fac8d2026).
  DEC-1156 (7): a narrow independent check of a change made after a ticket's review. DEC-136: tests written from
  described behaviour. DEC-820: reads are open; only secrets, the held-out material's contents, the counterpart's work
  and the hidden half of an evaluation set are refused. Read any other id in
  `/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md` by grepping its id.
