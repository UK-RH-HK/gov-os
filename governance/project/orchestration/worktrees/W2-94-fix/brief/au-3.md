Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-94: the narrow independent check of the W2-149 counts-schema pin's one-map revision, the auditor's brief (DAEO-g87r)

You are a fresh, read-only independent auditor under **W2-94** (`DAEO-g87r`; the ticket, read-only:
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-g87r.md`; read KPI lines S12 and S13 and the ticket body's
"Path case 2026-11-14 18:05" paragraph). This is a **narrow independent check of one test revision only** (DEC-1154,
DEC-1156 (7)): S13 itself was checked and passed at `ff6ba10be89a` (`docs/probes/DAEO-g87r/PR-DAEO-g87r-s13.md`, its
finding F1 being this path case); the fix flow was reviewed at `fac8d2026`. Do not re-review either. You write nothing in
the repository. Your final message is the probe record's body; the lead commits it as
`docs/probes/DAEO-g87r/PR-DAEO-g87r-s13b.md`.

## What you check (head `900035fdd51c1e469038feb48510483cd095a1e0` of `w2/W2-94-fix`, worktree `/home/usain/gov-os-worktrees/W2-94-fix`, base `f192e50da`)
The CTO's answer to the path case P-W2-94-S13-1 was (a) (DEC-1156 (7), written in the ticket at `02f08dac1`): the ticket
gains `tests/unit/orchestration/test_w2_149_indep_launch.py`, and S12's and S13's "the W2-149 cases pass unchanged" now
read "unchanged except this one entry". The revision: in `test_counts_schema_closes_every_object_and_string`, the
hard-coded `optional` map gains `fix` for the whole schema's root (`id(whole): {"fix"}`, or the file's own form for the
root), because S13 added the optional root property `fix` to
`governance/project/orchestration/tools/indep-schemas/indep-counts.schema.json`. Nothing else in that file or any other
file was to change. It was made by a fresh engineer given only the failing output (session `95f607d7-91f2-4012-b906-bac113e476b0`, commit
`900035fdd51c1e469038feb48510483cd095a1e0`). Between `f192e50da` and that commit the branch also holds the merge of `w2/integrate` at `820f5d3ab`
(which brought the ticket's path case `02f08dac1` and other tickets' integrated work); that merge is not under review.

## The three things you confirm, each as findings with the two lines below
1. **The diff is that one map only.** `git diff 820f5d3ab 900035fdd51c1e469038feb48510483cd095a1e0` (the branch's own change since the merge) and
   `git diff f192e50da 900035fdd51c1e469038feb48510483cd095a1e0 -- tests/unit/orchestration/test_w2_149_indep_launch.py` touch only the `optional` map in
   `test_counts_schema_closes_every_object_and_string`, adding `fix` for the root and nothing else; no other line,
   comment, case, import or file of the branch's own changes. Check the commit's trailers too (`Task: DAEO-g87r`,
   `Role: engineer`, `Implements:` only ids in the ticket's `sources:`, all trailers in one final paragraph).
2. **The case still refuses.** The revised case still fails for an unrequired root key other than `fix`, and still
   fails if `fix` itself lost `additionalProperties: false` or a required key of its own (`id`, `code`, `action`). Show it:
   copy the schema into your `$TMPDIR`, change one thing there (for example, add an optional root property `extra`, or
   drop `action` from `fix`'s `required`), and run the case against the copy (the case reads the schema through the
   module's `schema()` helper; point it at the copy by the file's own means, or monkeypatch in a one-off script under
   your `$TMPDIR`); each must turn the case red, and the real schema keeps it green.
3. **The suites pass.** S13's file (`tests/acceptance/W2-94/test_w2_94_s13_counts_fix.py`) and the W2-149 suites
   (`tests/acceptance/W2-149/` and `tests/unit/orchestration/test_w2_149_indep_launch.py`) pass at the head, with the
   W2-173, W2-178 and W2-94 fix-flow unit suites as S12's check.

Run the suites on their planted stand-ins only, from your sandbox's `$TMPDIR`:
`env HOME=<an empty folder under your $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-94-fix/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-94/test_w2_94_s13_counts_fix.py tests/acceptance/W2-149/ tests/unit/orchestration/test_w2_149_indep_launch.py tests/unit/orchestration/test_w2_173_indep_launch.py tests/unit/orchestration/test_w2_178_indep_launch.py tests/unit/orchestration/test_w2_94_fix_flow_unit.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --tb=short`
(run it from the worktree; if the slot tool cannot run in your sandbox, run the same pytest without it and say so; a
resource gate's refusal is a wait).

## Walls (hard)
Never open, list, grep or print anything under `/home/usain/gov-os-eval/`, `/home/usain/gov-os-runs/`, any folder
named `hidden` outside your `$TMPDIR`, any `fixtures/evaluation/examin/visible` or `hidden` folder of any tree, the
owner's EXAMIN copy or EXAMIN's real repository. You need none of them. No GPU, model, network or installs; no real
`claude` session. One simple command per Bash call; longer things in a script file under your sandbox's `$TMPDIR`
(`/tmp` is read-only in the sandbox). Refused twice for the same call by the guard, the sandbox or a hook: stop and say
so; never work around a refusal. No `gov retrieve` or `gov context`: search with Read and Grep, and search again once in
different words if the first does not answer.

## How you judge (the committed governance/project/briefs/JUDGEMENT.md, word for word)
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

## The decisions it applies (from the register, by id)
- DEC-1154: a change decided after a ticket's review gets a narrow independent check of that change; the ticket lands on
  it. DEC-1156 (7): own-branch path cases and decided-behaviour test revisions, the CTO routes them, a narrow check.
  DEC-1180 (4): a defect spotted is fixed in the same flow (S13). DEC-1010: how reviews converge. DEC-820: reads are open;
  only secrets, the held-out material's contents, the counterpart's work and the hidden half of an evaluation set are
  refused. Read any other id in `/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md` by grepping its id.

## Return (your final message, in full)
The twelve labelled fields (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons,
proposed_decisions, unresolved, recommended_next_action; sandbox and `ps` checks first), then **the probe record's
body** (no front matter; the lead adds it): what you probed (head `900035fdd51c1e469038feb48510483cd095a1e0`), how, each of the three confirmations with
its evidence (the diff, the red-on-copy runs, the suite counts), each finding (id, the KPI line, what and where with file
and line, `Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`, scope in|out), your overall
judgement (`pass` or `fail`), and, last, the fenced `verdict` block. It covers S12 and S13 (the revision touches their
checks), and the other lines (S1 to S11, F1 to F6) as `pass` only if you find nothing in this change against them (they
were reviewed before; this change does not touch their code). Its form:
```verdict
{"kpis": [{"kpi": "S13", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ...]}
```
