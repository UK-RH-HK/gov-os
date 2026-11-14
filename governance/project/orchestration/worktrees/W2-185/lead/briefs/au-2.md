# Brief: independent auditor, W2-185 (DAEO-qyt2), the narrow independent check of run 2's test revision only (DEC-1156 (7))

You are a fresh independent auditor (role independent-auditor), ticket DAEO-qyt2 (W2-185), profile STANDARD, class C2.
Read-only: you change nothing in any tree; you write only in your sandbox's own `$TMPDIR`. Headless: only your last
message is read, and the lead copies its verdict block into the probe record as you wrote it.

## What you judge
Branch `w2/W2-185` at head **16bddf80782449573cedd7373544533d79d2a326** (quote `git -C /home/usain/gov-os-worktrees/W2-185 rev-parse HEAD`),
in `/home/usain/gov-os-worktrees/W2-185` (read it there; never write there). **Only the revision:**
`git -C /home/usain/gov-os-worktrees/W2-185 diff 0c7e4d68f..16bddf807` (8 files; base 0c7e4d68f = the ticket's build,
already judged PASS at 1180e4ec5 in `docs/probes/DAEO-qyt2/PR-DAEO-qyt2.md`, with w2/integrate merged). The ticket, read
it whole, with its widening note: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-qyt2.md`. Decisions, grep
the register by id only (`/home/usain/gov-os-worktrees/W2-185/docs/DECISION_REGISTER.md`): DEC-1167 (4), DEC-971
item 3, DEC-1156 (7).

The revision: a fresh independent test designer (td-3, session 0298f2b5-6127-4da2-b447-a810a9ee8e3e) revised the 18
cases the round-1 probe record named (lines 41-57) to the decided behaviour of DEC-1167 (4): the template wires
`context_watch.py` in `postToolUse` beside `posttooluse.py`, and the lift exemption is per hook (the template's
`posttooluse.py` entries only). Commits, one per file, each with `Rewrite-Reason: DEC-1167 (4), DEC-1156 (7) (W2-185 run 2)`:
2ad99213c (`tests/acceptance/W1-38/w1_38_hooks_support.py`), 8ee2c6dc4 (`test_w1_38_hooks_any_folder.py`), 6cb684972
(`test_w1_38_hooks_source.py`), 00b56d2f2 (`tests/acceptance/W2-59/test_w2_59_hook_lines.py`), 80841a0c6
(`test_w2_59_hook_lines_worker_env.py`), 1689ecce8 (`tests/unit/hooks/test_w2_106_template_hook_lines.py`), 86a7e7480
(`tests/acceptance/W2-05/test_w2_05_hooks_source.py`), e54b383f8 (`tests/unit/gitenv/test_hooks_lifted.py`); merged by
16bddf807 (the lead). It kept every id, deleted no case, added 16 cases (176 → 192 with the opt-in suites).

Judge:
1. **Each revised case keeps its point** (the probe record's 18 ids, plus `test_w1_38_hooks_source.py::TestRulesyncPassesBothThrough::test_a_limit_and_a_failed_tool_call_entry_of_the_source_reach_the_generated_settings`
   and the two `*_carries_the_time_limit` cases the default `-k` hides, which the same S1 line turned red): what it
   guarded before still fails when broken, and it now pins DEC-1167 (4) rather than the old one-entry or whole-event
   behaviour. Entries picked by program, not by index or count. No lowering: no skip, xfail, flaky or rerun mark; no
   weakened assertion beyond what the decided behaviour needs. Where the test designer could not read
   `portability.py` (the counterpart's work), its new unit cases accept `HOOKS_EVENT_DIFFERS` or `HOOKS_MATCHER_DIFFERS`:
   say whether that leaves any face unpinned.
2. **Plants** (in your copy): at least (a) the template without its `context_watch.py` entry turns the W2-59
   seven-lines case, the W2-106 pair case and the W1-38 context-watch cases red; (b) a non-exempt extra template entry in
   `postToolUse` (another program) gives a portability finding in the W2-05 / `test_hooks_lifted.py` cases' sense; (c)
   the template's `context_watch.py` given another matcher than the root's is a finding. Green unplanted, red planted.
3. **The five `PreCompact` cases** (`test_w1_38_hooks_any_folder.py` `[PreCompact-*]` and the space case `[PreCompact]`),
   outside the 18: red on 0c7e4d68f because `precompact.py` writes its read-first line as text before its JSON (W2-176,
   13fd1dd34, already in the claim base 31eab2103), not because of this ticket. The support's `_json` now reads the last
   JSON line. Judge whether the case still asserts the program's own "no state block" message, and whether this hunk
   belongs in this revision (allowed path; its `Rewrite-Reason` names DEC-1167 (4) though its cause is W2-176).
4. **Scope and trailers:** only the eight widened files; `Task: DAEO-qyt2`, `Role: independent-test-designer`,
   `Implements:` from `sources:` only, `Rewrite-Reason:` on each, trailers in one final paragraph.

S1, S2, S3 and F1 were judged PASS on the code at 1180e4ec5 and the code has not changed since (`git diff 1180e4ec5
16bddf807 -- src template` shows only w2/integrate's changes, if any; check it). Your verdict per KPI line is on whether
the revision keeps each line's guarding cases sound.

The lead's runs on 16bddf807 (in the tree, `.gov-runtime/scratch/lead/log/`): `gov accept W2-185` pass, 18 passed 0
failed (`accept-16bddf807.txt`); the eight files with the opt-in suites (`reds-post-16bddf807.txt`, when present);
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
Then, for each of the four points: the verdict, the commands you ran and their result lines (each plant: green unplanted, red planted, the failing assertion).
Then each finding, with `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.
Then the fenced verdict block, one entry per KPI line of the ticket, ids S1, S2, S3, F1, in this exact form:
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": []}, ...]}
```
Then: guard_refusals: none or a line each.
