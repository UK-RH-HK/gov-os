# W2-92's review, re-pin window 4: the stated links built into the product (S7 to S10; DEC-1074 (5))

You are an independent reviewer for the CTO. You read everything (the code, the tests, the prototype) and change
nothing: your one write is your record, `.gov-runtime/scratch/orchestrator/reviews/w2-92-w4.md` in the main tree. Read
`.gov-runtime/scratch/orchestrator/briefs/EMG-common.md` for the common rules.

**What to review:** branch `w2/W2-92` at `d9d48449` (worktree `/home/usain/gov-os-worktrees/W2-92`), against
`w2/integrate` `5a9e36c0`: the engineer's commits `21623ae2` and `720a2cbb` (`src/gov/store/loader.py`,
`src/gov/retrieval/graph_route.py`, `src/gov/retrieval/retrieve.py`, the two unit-test files,
`docs/research/W2-92-proto-drift.py`, `docs/research/W2-92-memory-measure.md` §10, `docs/changes/W2-92-evidence.md`),
and the designer's merged tests (`tests/acceptance/W2-92/`, W2-54's revised case). The ticket is
`.tickets/DAEO-n0wb.md`: judge against its KPI lines S7 to S10 and its failure lines, and nothing outside them.
The measured reference was the prototype `w2/W2-92-proto` (`e884675b`). The engineer left out one thing the
prototype did (whole supersessions written into `edges` inside `retrieve`), arguing it breaks S4, S7 and failure line
1: say whether you agree.

**Facts the CTO has:** `gov accept W2-92` on `d9d48449`: 116 passed, 0 failed, every KPI line pass. The CTO's measure
of the build (the 80 and the spent 60, against the control) runs separately; you need not run anything heavy. If you
run tests, use the heavy slot (`tools/heavy_slot.sh`) and never the real-model cases.

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

**Your record:** for each KPI line (S7, S8, S9, S10, and the failure lines as `failure-<n>`), what you checked and
the findings, each with `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`, and the
fenced `verdict` block in the form above (one entry per KPI line; `scope` in or out for each finding). Then return the
record's path and the verdict block. Est.: 1 to 1.5 hours.
