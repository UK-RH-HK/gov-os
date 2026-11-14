# Brief qa-1: QA engineer for DAEO-0cd2 (W2-187), profile FULL, class C2

You are a fresh QA engineer for ticket DAEO-0cd2 (W2-187: the memory audit's standing hidden set, judged every week at
95 %, counts only; the monthly check against fitting; the weekly maintenance pass; the audit's state per repository; the
schedule's code; the weekly secret scan and push). Use your skill `qa-review` (`.claude/skills/qa-review/SKILL.md`,
with its `scenarios.md`) step by step, at profile FULL: trace every KPI line, check tests and code against the spec,
probe the final head, judge each finding, and write the findings report. You change no test, no code and no ticket.

## Where you work
| what | path |
|---|---|
| the tree (read; write only your report) | /home/usain/gov-os-worktrees/W2-187 |
| branch, head to review | w2/W2-187 at 5b82d1d53 |
| your report (the only file you write and commit) | docs/probes/DAEO-0cd2/QA-DAEO-0cd2.md |
| the ticket: KPI lines S1-S12 and F1-F7, the Approach, the method, the Interface I1-I13 (I13 near the end), the CTO's routings and amendments | /home/usain/gov-os-worktrees/W2-187/.tickets/DAEO-0cd2.md |
| the change to review | `git diff 5336a6fca..5b82d1d53 -- src/gov/memaudit src/gov/adopt/memory_sets.py governance/project/orchestration/tools/memaudit_cron.sh tests/unit/memaudit tests/unit/adopt tests/acceptance/W2-170 tests/acceptance/W2-171 tests/acceptance/W2-172 tests/acceptance/W2-187 docs/changes/W2-187-evidence.md` (the merges of `w2/integrate` bring other tickets' files; ignore those) |
| the acceptance suite and its map | tests/acceptance/W2-187/ (README.md) |
| the engineer's evidence | docs/changes/W2-187-evidence.md |
| the packages and the CTO's answers | docs/probes/DAEO-0cd2/PACKAGE-W2-187-P1.md, PACKAGE-W2-187-S12.md |
| the threat model | docs/adr/ADR-0001-threat-model.md |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1182, DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1098, DEC-1097, DEC-1092, DEC-1074, DEC-1072, DEC-1156, DEC-1157 |

**Readings the lead or the CTO settled (judge the code against them, not against the older text):**
- The CTO accepted the I13 reading under DEC-1157 (3). A no-declaration `push` prints `PUSH none: no declaration`,
  exits 0 and writes nothing, and that line reaches the wrapper's own stdout. A declared push writes its own
  `cron.log` line (the six keys, step `push`) and the DIGEST last line. The wrapper calls `push` after any started
  audit step, on the live path and on today's path, and its exit stays the last audit step's. W2-172 S9's files are
  unchanged.
- I3 reading for S1: a used set's own run's `misses.jsonl` and `miss-classes.json` are skipped. A Wave 0 set lacking
  its record, or at another commit, is then `STANDING_SPENT 0`.
- The O8 (a) split of S10 and S11 was not taken. The designer's size estimate was under the trigger, and S10 and S11
  were built by then.

**The lead's results of the one scoped run** (do not re-run the ticket's suites; DEC-959 item 1):
- `gov accept W2-187` passes: 205 passed, 0 failed, every line `success-1` to `success-12` and `failure-1` to
  `failure-7` pass.
- `tests/acceptance/W2-170` 184 passed; `W2-171` 140 passed; `W2-172` 162 passed; `W2-173` 91 passed; `W2-88` 215
  passed; `tests/unit/memaudit` 354 passed.
- The lead's `lead_verify` (the scoped selection) runs in parallel with you; its result is not yours to wait for.

## Rules
- Probes are small runs of the code under `tmp_path`-style scratch folders in your sandbox's `$TMPDIR`. Every planted
  thing is yours (sets roots, repositories, a bare remote, a fake gitleaks, a fake `gov`, a fake `claude`). Any pytest
  you run goes through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=<an empty folder in $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-187/src python3 -m pytest <one file or case> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
  with a Bash timeout of 3600000 ms. A heavy-slot refusal is a wait.
- Look hard at:
  - counts only (S4, F1, F7): no id, question, gold, answer, citation, path or secret leaves a run folder or reaches a
    line, log or digest;
  - the one judged path (S3, F4): no second copy of the reader path;
  - the week rule (S2, F2);
  - `maintain` never a gate, and never changing a setting (S10, F6);
  - the scan-then-push order (S12, F7);
  - fresh-path behaviour unchanged without `--week` and with no live set.
- Held-out rules (DEC-820): never open the real sets root (`~/gov-os-eval`), the real runs folder (`~/gov-os-runs`, any
  `indep/` under it), any hidden half or memory-verdict folder, the real crontab. Never a real model call, a real
  search, a real push to a real remote, or a real gitleaks over a real repository. Never print any hidden set's ids or
  text.
- Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words
  (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.
- **The report** starts with YAML front matter. Quote every value that holds `: ` or `#`, or `gov launch` refuses the
  probe folder:
  ```
  ---
  type: qa
  task: DAEO-0cd2
  qa_session: "<your session id, or n/a>"
  reviewed_commit: <the full 40-hex sha of 5b82d1d53>
  verdict: "pass|fail"
  ---
  ```
  Then one row per KPI line (traced or not), then each finding as a described behaviour (never code), each with
  `Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other` and a severity P1/P2/P3. Check it parses
  (`python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]).read().split('---')[1])" <report>`).
- **Commit** your report only, the trailers in ONE final paragraph:
  `git commit -m "W2-187 (DAEO-0cd2): QA findings report at 5b82d1d53" --trailer "Task: DAEO-0cd2" --trailer "Role: qa-engineer" --trailer "Implements: DEC-1179, DEC-1182" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- docs/probes/DAEO-0cd2/QA-DAEO-0cd2.md`
  (`git add` it first; it is a new file.) No merge, no push, no other file.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)). A permission denial is a refusal too.

## Judgement rules (governance/project/briefs/JUDGEMENT.md, word for word)

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

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status / work_completed / files_changed /
evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action; then the
report's path; then `commits:` (hash12, subject, trailers) and `guard_refusals:` (none, or each: time | form | the
hook's reason | true or false-positive).
