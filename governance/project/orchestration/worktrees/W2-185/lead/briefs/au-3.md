# Brief: independent auditor, W2-185 (DAEO-qyt2), the narrow independent check of run 3's test revision only (DEC-1156 (7))

You are a fresh independent auditor (role independent-auditor), ticket DAEO-qyt2 (W2-185), profile STANDARD, class C2.
Read-only: you change nothing in any tree; you write only in your sandbox's own `$TMPDIR`. Headless: only your last
message is read, and the lead copies its verdict block into the probe record as you wrote it.

## What you judge
Branch `w2/W2-185` at head **997e25f1e9c670b17c7db880319d96c2119e4a44** (quote `git -C /home/usain/gov-os-worktrees/W2-185 rev-parse HEAD`),
in `/home/usain/gov-os-worktrees/W2-185` (read it there; never write there). **Only the revision:**
`git -C /home/usain/gov-os-worktrees/W2-185 diff 6b4bafb71..997e25f1e` (one file,
`tests/acceptance/W1-38/test_w1_38_hooks_command_line.py`; base 6b4bafb71 = the ticket's build and run 2's revision,
already judged PASS in `docs/probes/DAEO-qyt2/` (round 1 at 1180e4ec5, run 2's narrow check at 16bddf807), with
w2/integrate e2a0d6191 merged). The ticket, read it whole, with both widening notes:
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-qyt2.md`. Decisions, grep the register by id only
(`/home/usain/gov-os-worktrees/W2-185/docs/DECISION_REGISTER.md`): DEC-1167 (4), DEC-917, DEC-1156 (7).

The revision: a fresh independent test designer (td-4, session 5a4643b6-9496-4788-bcdf-48ce6fc31844) revised the two
`[PostToolUse]` cases that still expected one entry under PostToolUse where DEC-1167 (4) adds the context watch beside
the guard's entry:
- `tests/acceptance/W1-38/test_w1_38_hooks_command_line.py::TestGeneratedCommandLines::test_the_generated_command_line_is_the_kernel_template_s[PostToolUse]`
- `tests/acceptance/W1-38/test_w1_38_hooks_command_line.py::test_the_source_s_command_line_is_the_kernel_template_s_form[PostToolUse]`
One commit, 4808016acb5c, with `Rewrite-Reason: DEC-1167 (4), DEC-1156 (7) (W2-185 run 3)`; merged by 997e25f1e (the
lead). A new helper `_the_guard_line` picks the guard's entry by its program and holds any other entry to be the context
watch's, under PostToolUse only. Before: 2 failed, 17 passed at 6b4bafb71 (the file, with the opt-in suites).

Judge:
1. **Each revised case keeps its point**: exactly one guard entry under each guard event (two entries running the guard
   program, or none, still red); that entry's line equals the kernel template's exit-mapping line exactly (DEC-917);
   under a lifecycle event one entry in DEC-608's plain form; and it now pins DEC-1167 (4) rather than the old one-entry
   behaviour. Entry picked by program, not by index or count. No lowering: no skip, xfail, flaky or rerun mark; no
   weakened assertion beyond what the decided behaviour needs. Say whether the other parametrised ids (PreToolUse,
   PostToolUseFailure, the four lifecycle events) assert at least what they asserted before, and whether the helper's
   new strictness (no other entry under a guard event but PostToolUse; under PostToolUse exactly the context watch
   beside the guard) is what DEC-1167 (4) decides or goes beyond it.
2. **Plants** (in your copy): at least (a) a second entry running `posttooluse.py` under the template's `postToolUse`
   turns both revised cases red; (b) the guard entry's command changed by one character turns both red; (c) the guard
   entry removed (only the context watch left) turns both red. Green unplanted, red planted. (The test designer could
   not read `template/.rulesync/hooks.jsonc` under the guard and planted at function level only; you plant in the
   template file of your copy, so the generated case runs through rulesync.)
3. **Scope and trailers:** only the widened file; `Task: DAEO-qyt2`, `Role: independent-test-designer`, `Implements:`
   from `sources:` only, `Rewrite-Reason:` present, trailers in one final paragraph.

S1, S2, S3 and F1 were judged PASS on the code and the code has not changed since in this ticket (`git diff 16bddf807
997e25f1e -- src template` shows only w2/integrate's changes, if any; check it). Your verdict per KPI line is on whether
the revision keeps each line's guarding cases sound.

The lead's runs on 997e25f1e (in the tree, `.gov-runtime/scratch/lead/log/`): `gov accept W2-185` pass, 18 passed 0
failed (`accept-997e25f1e.txt`); the file and its siblings with the opt-in suites (`cases-997e25f1e.txt`, when present);
lead_verify (`verify/summary.txt`, when present).

Work in a **copy** of the tree in your `$TMPDIR` (`git -C /home/usain/gov-os-worktrees/W2-185 archive HEAD | tar -x -C
"$TMPDIR/copy"`; never `git worktree add`, never a write in the tree). Where a plant or run cannot run in your sandbox,
say so with the exact refusal and judge by reading, naming which you did.

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

## How you run tests
Every pytest through the heavy slot, TMPDIR your sandbox's own `$TMPDIR` (outside the repository and outside ~/gov-os-runs):
```
env PYTHONUSERBASE=/home/usain/.local HOME=<an empty folder in $TMPDIR> PYTHONPATH=<the copy>/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest --optin lifted,breadth <node id or file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
Run each case from the copy's root. A resource gate's refusal is a wait: wait and retry; it does not count as a refusal.

## Searching and forms
No `gov retrieve` and no `gov context` in the sandbox: Read and Grep; search again once in different words if needed.
Never open the evaluation sets' root, held-out material or any hidden or memory-verdict folder. Scripts longer than one
line go in `$TMPDIR`. Refused twice for the same call: stop and say so; never work around a refusal. No commit, merge or push.

## Return (your last message; nothing else is read)
The twelve fields first, each a labelled line ("none" where nothing):
task: / status: (PASS or FAIL) / work_completed: / files_changed: none / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then, for each of the three points: the verdict, the commands you ran and their result lines (each plant: green unplanted, red planted, the failing assertion).
Then each finding, with `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.
Then the fenced verdict block, one entry per KPI line of the ticket, ids S1, S2, S3, F1, in this exact form:
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": []}, ...]}
```
Then: guard_refusals: none or a line each.
