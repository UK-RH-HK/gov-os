Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-61h-c39/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Narrow independent check: W2-61h (DAEO-h2k3) — the N2 (b) and N1 revision only (DEC-1180 (1), (4); DEC-1154)

You are a fresh independent auditor, read-only. Headless: only your last message is read. You write nothing in any
worktree; you may use the sandbox's own `$TMPDIR` for throwaway files. This is a narrow check of one revision, not a
review round (DEC-1010, DEC-1154).

## What you check (only this)
Tree: /home/usain/gov-os-worktrees/W2-61h-c39, branch w2/W2-61h-c39, head **dbe1236733f9d63ccccf8fc5435fbdba41617603**
(probe exactly this commit; confirm with `git -C /home/usain/gov-os-worktrees/W2-61h-c39 rev-parse HEAD`).

The change under check, in `tests/acceptance/W2-61h/` only: the test designer's commit `70aa3a6b7ba3` (merged at
`dbe123673`), files `w2_61h_support.py`, `test_w2_61h_hidden_form.py` (docstring only), `test_w2_61h_visible_new.py`,
`README.md`. See it with `git -C /home/usain/gov-os-worktrees/W2-61h-c39 diff 494d5c933 dbe123673 -- tests/acceptance/W2-61h/`.
(`494d5c933` is w2/integrate, which already holds the previous revision, DEC-1178 (1), checked and passed as
`docs/probes/DAEO-h2k3/PR-DAEO-h2k3-f3.md` if present, else the commit `40f997704`.) Everything else is out of scope.

Judge against:
1. **DEC-1180 (1) and (4)** in `docs/DECISION_REGISTER.md` (grep `### DEC-1180`).
2. **The ticket's S4 success line and F3's failure line** (the 4th success line and the 4th failure line) in
   `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-h2k3.md` (read-only), and its last two paragraphs,
   "Reopened 2026-11-14" and "N2 (b), 2026-11-14".
3. **The revision's outcomes:**
   - **(e)** a heading-cited source whose section text (from its heading line to the next heading of the same or a
     higher level, or the end of the file) differs between the source's own commit and HEAD is **listed** by question
     id and entry number only, though its heading is still found at HEAD; never failed, never blocking a close;
   - **(f)** a heading-cited section that moved unchanged is **not listed**;
   - **(g)** an entry with two or more changed alternatives is **listed once** (row N1);
   - **(a)-(d) unchanged:** (a) a block moved unchanged passes, not listed; (b) a lines-cited block changed passes,
     listed; (c) a source that never held its answer at its own commit is red, named by file name and entry number
     only; (d) a control passes, not listed;
   - **no case, message, warning or README line leaks** a question, answer, category, gold path or span text (file
     names and entry numbers only).

Questions to answer: Do (e), (f), (g) each get the outcome above, in the visible planted case and in the hidden-form
S4 case on a throwaway root? Do (a)-(d) keep their outcomes (compare with the diff: did any earlier assertion weaken)?
Is the designer's "text differs" rule (trailing whitespace stripped per line, trailing blank lines dropped; a non-`#`
heading compared over its stated width) a fair reading of "section text differs", or does it hide a real change an
honest editor makes? Would the planted (e) and (g) proofs have been red under the previous rule (the designer says it
ran the new tests against the old support; you may check the same with a copy under `$TMPDIR`)? Does the hidden-form
module still skip without `GOV_EVAL_SETS_ROOT` and under a measured `GOV_ROLE` (the path map's `measures.roles`)? Are
test function names kept, and does the planted visible case still run in the full run
(`tests/optin-lifted-breadth.txt` keeps only a parametrised function's first row)? Are the trailers in one final block
(`Task: DAEO-h2k3`, `Role: independent-test-designer`, `Rewrite-Reason: DEC-1180 (1)` on the designer's commit;
`Task: DAEO-h2k3`, `Role: orchestrator` on the merge)?

You may run the visible side (the hidden-form module skips without `GOV_EVAL_SETS_ROOT`):
```
cd /home/usain/gov-os-worktrees/W2-61h-c39 && bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env PYTHONUSERBASE=/home/usain/.local HOME=$TMPDIR PYTHONPATH=/home/usain/gov-os-worktrees/W2-61h-c39/src python3 -m pytest tests/acceptance/W2-61h -q -rA -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
Every pytest through heavy_slot.sh (a resource gate's refusal is a wait). You may plant a throwaway sets root under
`$TMPDIR` (a `fixtures/evaluation/memory-retrieval/hidden/` folder of planted YAML questions citing real commits and
real non-evaluation files of this repository, with a copy of `governance/project/path-map.yaml` under
`governance/project/`) and run only `test_w2_61h_hidden_form.py -k s4 -rA` against it with
`env -u GOV_ROLE -u GOV_TICKET GOV_EVAL_SETS_ROOT=<that throwaway root>`; report outcomes and counts only. (A
heading-cited section rewritten under the same heading: a Markdown file of this repository whose section changed
between an older commit and HEAD; a section moved unchanged: one with text inserted above it since.)

## Rules
- **Never open the evaluation sets' root (`gov-os-eval` under the home folder) or any hidden, retired-hidden or
  memory-verdict folder; read no hidden content.** Never set `GOV_EVAL_SETS_ROOT` to anything but a throwaway root you
  planted.
- Read-only: write nothing in any worktree or the main tree; no commit, no merge.
- Refused twice for the same action by the guard, the sandbox or a hook: stop and say so; never work around a refusal.
- Searching: Read and Grep only (no `gov retrieve`, no `gov context`); search again once, in other words.

## Judgement rules: `governance/project/briefs/JUDGEMENT.md`, word for word

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
Your probe record's body, ready for the lead to commit as `docs/probes/DAEO-h2k3/PR-DAEO-h2k3-n2.md` (the lead adds
the front matter):
1. A line `reviewer_session: <your session id if you know it, else "unknown">`.
2. What you probed and found sound, as short bullets (commands and counts, no hidden content).
3. Each finding with its id, scope (in|out), and the two lines `Ordinary work: yes|no, because …` and
   `Consequence: fails open|loses work|other`.
4. `Judgement: pass|fail`.
5. Last, the fenced verdict block, one entry per KPI line you judged (S4 and F3 at least):
```verdict
{"kpis": [{"kpi": "S4", "verdict": "pass|fail", "findings": []}, {"kpi": "F3", "verdict": "pass|fail", "findings": [{"id": "N1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```
