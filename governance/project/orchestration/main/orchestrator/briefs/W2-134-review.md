# The review of W2-61h S7 and W2-134 together (the memory measure; DEC-1085 (1), (2))

You are an independent reviewer for the CTO. You read everything and change nothing: your one write is your record,
`.gov-runtime/scratch/orchestrator/reviews/w2-134.md` in the main tree. Read
`.gov-runtime/scratch/orchestrator/briefs/EMG-common.md` for the common rules.

**What to review:** branch `w2/W2-134` at `a543a10f` (worktree `/home/usain/gov-os-worktrees/W2-134`), against
`w2/integrate`.
- The measure code: S7's engineer commit `ab18f6f5`, and W2-134's engineer commit `a543a10f`
  (`src/gov/retrieval/measure.py`, `tests/unit/retrieval/test_w2_134_reanchor.py`, `docs/changes/W2-134-evidence.md`).
- The tickets: `.tickets/DAEO-m4rq.md` (W2-134: S1 to S6 and its failure lines; read its notes) and
  `.tickets/DAEO-h2k3.md` (W2-61h: S7 and the failure line "A family hit counted on a member whose text does not hold
  the gold span's text").
- The previous review of S7, `.gov-runtime/scratch/orchestrator/reviews/w2-61h-s7.md`: check that its F1 and F3 are
  fixed.

Check in particular:
- A commit is never scored against another commit's lines.
- Nothing writes the sets root or a label file.
- An unresolved source prints only the question id and its entry number.
- The floor and the token edges hold, and no `DEC-nnnn:` key is dropped.
- With no families and no moved blocks, the output is today's but for S6's first line.
- **The engineer's stated risk:** a source whose commit is missing from the measured clone is now unresolved, where it
  was scored on its stated lines. Judge whether an honest measure on the D-4b clones hits it. Answer from the code and
  the clones' git history only (`git log` in `~/gov-os-runs/D4B/g1/repo` is allowed). Never open a label.

**Facts the CTO has:**
- The acceptance cases `tests/acceptance/W2-134/` pass 28 of 28 on `a543a10f`. `gov accept` refused only on the
  README's map form, which a designer is fixing.
- The engineer reports: S7's acceptance file 13 passed, `tests/acceptance/W2-61/` 100 passed, and the unit tests 44
  passed.

Re-run what you need through the heavy slot (`tools/heavy_slot.sh`, `PYTHONUSERBASE=/home/usain/.local`). Never run
`test_w2_61h_hidden_form.py`, which reads `~/gov-os-runs`.

**The hidden-half rule:** never open anything under `~/gov-os-eval/`, or any `hidden`, `memory-verdict` or
`memory-verdict-2` folder, and no label file under `~/gov-os-runs`.

**DEC-1080:**
- read with the Read and Grep tools;
- one simple command per Bash call;
- no `cd … &&` chains and no `git -C`;
- one line before any command that will ask for permission.

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

**Your record:** for each of W2-134's S1 to S6, W2-61h's S7, and each failure line (W2-134's `failure-1` to
`failure-4`, W2-61h's `failure-5`), what you checked and the findings. Each finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. End with the fenced `verdict` block
in the form above (one entry per KPI line; `scope` in or out for each finding). Then return the record's path and the
verdict block. Est.: 1.5 hours.
