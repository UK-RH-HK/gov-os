# W2-32's review, re-pin window 4: S11, the candidate pool v456 (DEC-1074 (5))

You are an independent reviewer for the CTO. You read everything (the code, the tests, the research harness) and
change nothing: your one write is your record, `.gov-runtime/scratch/orchestrator/reviews/w2-32-s11.md` in the main
tree. Read `.gov-runtime/scratch/orchestrator/briefs/EMG-common.md` for the common rules.

**What to review:** branch `w2/W2-32` at `a4c5e9c4` (worktree `/home/usain/gov-os-worktrees/W2-32`), against
`w2/integrate` `5a9e36c0`: the engineer's commit `30c39e3b` (`src/gov/config/loader.py`, `src/gov/retrieval/pool.py`,
`src/gov/retrieval/retrieve.py`, `lexical.py`, `semantic.py`, `tests/unit/retrieval/test_w2_32_pool.py`, the S11 row of
`docs/changes/W2-32-evidence.md`) and the designer's merged S11 cases (`tests/acceptance/W2-32/test_w2_32_s11_pool.py`,
`w2_32_pool.py`). The ticket is `.tickets/DAEO-0pyc.md`: judge against S11 and its two failure lines, nothing else.
The measured reference is the research harness's v456 (`/home/usain/gov-os-worktrees/research-retrieval/docs/research/EXP-003/retrieval-survey/night/harness/rx.py`:
`sem_uncut`, `sem_k`/`lex_k`, `depth`, `perfile`, `dedup`). Check in particular: absent or 0 settings leave every
search exactly as today; `route_depth` is per search and never changes the modules' `TOP_K` for the process; every
rerank request of the pool keeps the padded bound; the engineer's stated gap (a failed pool rerank is not retried,
where the harness scores the page again) and the S8-after-per-file placement it notes.

**Facts the CTO has:** `gov accept W2-32` on `a4c5e9c4`: 257 passed, 0 failed, 2 skipped. The CTO's measure (the
product with the pool on against the harness's v456, question for question) runs separately; you need not run anything
heavy. If you run tests, use the heavy slot (`tools/heavy_slot.sh`) and never the real-model cases.

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

**Your record:** for S11 and each failure line (`failure-1`, `failure-2`), what you checked and the findings, each
with `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`, and the fenced `verdict` block
in the form above (one entry per KPI line; `scope` in or out for each finding). Then return the record's path and the
verdict block. Est.: 1 hour.
