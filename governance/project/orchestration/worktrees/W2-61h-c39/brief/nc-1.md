Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-61h-c39/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Narrow independent check: W2-61h (DAEO-h2k3) — the hidden count (39) and S3's floor change only

You are a fresh independent auditor, read-only. Headless: only your last message is read. You write nothing in any
worktree; you may use the sandbox's own `$TMPDIR` for throwaway files. This is a narrow check, not a review round
(DEC-1010).

## What you check (only this)
Tree: /home/usain/gov-os-worktrees/W2-61h-c39, branch w2/W2-61h-c39, head **82b5cf198** (probe exactly this commit;
confirm with `git -C /home/usain/gov-os-worktrees/W2-61h-c39 rev-parse HEAD`).

The change under check, in `tests/acceptance/W2-61h/` only (`w2_61h_support.py`, `test_w2_61h_hidden_form.py`,
`README.md`):
- the count change, `94aa1debc` (merged `00a2f3e25`): `HIDDEN_COUNT` 40 -> 39;
- the floor change, `5cd76ee9d` (merged `82b5cf198`): `R5_RETIRED = {"callers": 1}` beside `R5_SHORT`, S3's floors
  `R5_QUOTAS[name] - R5_SHORT.get(name, 0) - R5_RETIRED.get(name, 0)`, the sum comments, the README lines.
See them with `git -C /home/usain/gov-os-worktrees/W2-61h-c39 diff 31eab2103 82b5cf198 -- tests/acceptance/W2-61h/`.
(`440bc9a6d`, q22's re-anchor, sits in the same range and is **out of scope**: do not judge it.)

Judge against:
1. **DEC-1171 (2)** in `docs/DECISION_REGISTER.md` (grep `### DEC-1171`, item (2) only): h10 retired from the hidden
   half; the count case reads 39 until the walled writer's replacement brings it back to 40; the count case revised by
   a test designer under this item.
2. **The owner's answer of 2026-11-13, option (b)** (to be recorded as DEC-1175; not yet in the register, so judge
   against this text): "h10's category is **callers**, given by the owner's operator from h10's retirement reason line.
   The callers floor drops by one with the count. The CTO confirms the floor two short there: the operator's earlier
   accepted shortfall and h10's retirement each take one place." The order to the test designer: add
   `R5_RETIRED = {"callers": 1}` beside `R5_SHORT` in `w2_61h_support.py`; make S3's floors honour it, so the callers
   floor is two short of the README's stated minimum; keep the twelve categories' sum comment true at 39; no other case
   changes.
3. The ticket's S1 and S3 KPI lines (`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-h2k3.md`, read-only),
   as far as they bear on the count and the floors.

Questions to answer: Is `HIDDEN_COUNT` 39 with a true comment? Is `R5_RETIRED` exactly `{"callers": 1}` beside
`R5_SHORT`? Do S3's floors come out as callers 2, decision 5, code-paraphrase 2 and every other category at its full
minimum, with nothing else loosened? Are the sum comments true (twelve minimums 40; less h10's place 39)? Does any other
case change or lose its point (the test functions' names kept)? Does any output or file in the change print or name a
hidden question, answer or gold path (the category word "callers" is the owner's and may appear)? Are the commits'
trailers (`Task: DAEO-h2k3`, `Role: independent-test-designer` on the designer's commits, `Role: orchestrator` on the
merges) in one final block?

You may run the visible side (the hidden-form module skips without `GOV_EVAL_SETS_ROOT`):
```
cd /home/usain/gov-os-worktrees/W2-61h-c39 && bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-61h-c39/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-61h-c39/src python3 -m pytest tests/acceptance/W2-61h -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
Every pytest through heavy_slot.sh (a resource gate's refusal is a wait). You may plant a throwaway sets root of
**synthetic** files under `$TMPDIR` and run only `test_w2_61h_hidden_form.py` against it with
`GOV_EVAL_SETS_ROOT=<that throwaway root>`, to see S3 green at the floors and red one below; report counts only.

## Rules
- **Never open the evaluation sets' root (`gov-os-eval` under the home folder) or any hidden or retired-hidden folder;
  read no hidden content.** Never set `GOV_EVAL_SETS_ROOT` to anything but a throwaway root you planted.
- Read-only: write nothing in any worktree or the main tree; no commit, no merge.
- Refused twice for the same action by the guard, the sandbox or a hook: stop and say so; never work around a refusal.
- Searching: Read and Grep only (no `gov retrieve`, no `gov context`); search again once, in other words.

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
Your probe record's body, ready for the lead to commit under `docs/probes/DAEO-h2k3/` (the lead adds the front matter):
1. A line `reviewer_session: <your session id if you know it, else "unknown">`.
2. What you probed and found sound, as short bullets (commands and counts, no hidden content).
3. Each finding with its id, scope (in|out), and the two lines `Ordinary work: yes|no, because …` and
   `Consequence: fails open|loses work|other`.
4. `Judgement: pass|fail`.
5. Last, the fenced verdict block, one entry per KPI line you judged (S1 and S3 at least):
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": []}, {"kpi": "S3", "verdict": "pass|fail", "findings": [{"id": "N1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```
