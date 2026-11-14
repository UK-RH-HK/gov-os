# W2-188 (DAEO-zlog): independent review, round 1 (brief au-1, from the ticket lead)

You are a fresh, read-only independent auditor for ticket **DAEO-zlog (W2-188)**, profile STANDARD, class C2, a kernel
skill change by the CIT-P route (CAP-33): your verdict is what the owner reads before approving the skill's bytes. Use
your skill `audit`. You wrote none of this work. You write nothing in the tree: you return your record as text and the
lead commits it as `docs/probes/DAEO-zlog/PR-DAEO-zlog.md`.

## What you probe
| what | value |
|---|---|
| tree | /home/usain/gov-os-worktrees/W2-188 (branch w2/W2-188) |
| probed commit | b75472d4825cece64936451f21b259787b5ecf97 |
| base | 5336a6fca (w2/integrate at claim) |
| the ticket (KPI lines S1-S5, F1-F3, non-goals, Interface I1-I6) | /home/usain/gov-os-worktrees/W2-188/.tickets/DAEO-zlog.md |
| the change | `git diff 5336a6fca b75472d48 -- template/governance/kernel/skills/adopt/SKILL.md .rulesync/skills/adopt/SKILL.md template/.rulesync/skills/adopt/SKILL.md docs/research/W2-88-memory-practice.md docs/changes/W2-188-CIT-P.md docs/probes/DAEO-zlog/` |
| the decision | `docs/DECISION_REGISTER.md`, `### DEC-1179` (grep by id only; the register is 1.6 MB); also DEC-1176 (1), DEC-1101, DEC-1125 (2), DEC-1098 (1), DEC-1074 (1) and (4), DEC-1072 (2), DEC-105 |
| the package | governance/project/orchestration/packages/MEMORY-AUDIT-P1.md (§2.1 the method, §2.4 the monthly check, §5.1 R1-R9) |
| the implementers | product-spec ps-1 1b67d74f-70d7-418e-970e-99b8f12aee8d (d782640de), ps-2 f7f2e9bc-d577-49b8-a2a6-15a5e99b3b47 (8aa930660, 857e5b3bf, 8ee9b7c36), ps-3 7eb0249a-85dc-48a5-8121-b3bdf82c22ac (be8b99ccb, 8c2e5d7ff, b75472d48); tests by the independent test designer td-1 50730df3-4f6a-4ad2-8788-d3ac8363236e (3c5167c47, merged 599fa2a22) |

## What you judge
1. The skill's text against S1, S2, S4 and F1, F3, and against DEC-1179 (1)-(6) as recorded: does step 6 say what
   DEC-1179 decided, and nothing it did not (no permission granted, no `gov.memaudit` subcommand, no mode the product
   lacks, the reader never called a second reranking model, the standing set never used to choose, judge, adopt or reject
   a fix, no question id printed or read)? Are the three copies byte-equal, the version 1.1.0, and exactly four hunks in
   the kernel copy's diff (version, step 6, the paragraph after step 7, the sources line)? Are A9's other six steps and
   the Verify section unchanged?
2. The practice record against S3 and F3: §3, §5 item 6 and §6 step 6 re-worded; §9 with each element S3 names; §9's
   below-95 text equal to the register's DEC-1179 (4) line (from `**Below 95 %:**` to its closing `.`), byte for byte;
   W2-88 S10's second reranking model still forbidden; no contradiction with the rest of the record.
3. The CIT-P record against S5 and DEC-105: hashes before and after (the after equal to the kernel copy as committed),
   the counts against the real diff, the old and new text of each changed place equal to the files, the three options,
   the impact table **true** (check each claim against the tests it names). Note: the ticket's S5 and I6 say W2-11's
   body case `test_every_copy_carries_the_kernel_skills_body[adopt]` goes red until the copies ACT; the record says that
   case does not exist. Check which is true in `tests/acceptance/W2-11/test_w2_11_skills.py` and say whether anything in
   the suite does catch the `.claude/skills/adopt/SKILL.md` drift.
4. F2: no commit of the ticket's implementers touches `.claude/` or `tests/`.
5. Trailers: every implementer commit carries `Task: DAEO-zlog` and an `Implements:` naming only ids in the ticket's
   `sources:`.
Its review cases are not yours to fix; the `verdict:` and `owner_approval:` lines of the CIT-P are not written yet by
design (the lead adds your verdict; the CTO writes the approval after the owner's yes).

You may run read-only commands (`git`, `grep`, `sha256sum`, `python3` scripts that only read, written in the sandbox's own
`$TMPDIR`), and `python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/adopt` with
`PYTHONPATH=/home/usain/gov-os-worktrees/W2-188/src`. A pytest run, if any, goes through
`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh` with
`PYTHONUSERBASE=/home/usain/.local -p no:cacheprovider -o tmp_path_retention_policy=failed`, `HOME` an empty folder in
`$TMPDIR`. Never open the evaluation sets' root (`~/gov-os-eval`), any hidden or memory-verdict folder, or secrets.
Refused twice for the same action: stop and say so; never work around it.

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

## Return (your last message; only it is read)
The sandbox check first, then the twelve fields as labelled lines (task, status, work_completed, files_changed,
evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), then **the probe
record's full text** for `docs/probes/DAEO-zlog/PR-DAEO-zlog.md`: front matter with `type: probe`, `task: DAEO-zlog`,
`reviewer_session` (yours, in full), `implementer_session` (the sessions above, in full), `reviewer_wrote_nothing: true`,
`probed_commit: b75472d4825cece64936451f21b259787b5ecf97`, `judgement: pass|fail`; then your checks with their
evidence, each finding with its two lines, and at the end the fenced `verdict` block (one entry per KPI line S1-S5,
F1-F3), and one line `verdict: PASS` or `verdict: FAIL`.
