# W2-61h's review: S7, the source families in the memory measure (DEC-1078 (4), DEC-1079, DEC-1085 (1))

You are an independent reviewer for the CTO. You read everything (the code, the tests) and change nothing: your one
write is your record, `.gov-runtime/scratch/orchestrator/reviews/w2-61h-s7.md` in the main tree. Read
`.gov-runtime/scratch/orchestrator/briefs/EMG-common.md` for the common rules.

**What to review:** branch `w2/W2-61h-s7` at `9e85fb97` (worktree `/home/usain/gov-os-worktrees/W2-61h-s7`), against
`w2/integrate`. The engineer's commit is `ab18f6f5` (`src/gov/retrieval/measure.py`, `governance/project/path-map.yaml`,
`tests/unit/retrieval/test_w2_61h_families*`). The designer's S7 cases were merged as `8e6f79b7` (from
`w2/W2-61h-tests` `353b4937`). The ticket is `.tickets/DAEO-h2k3.md`. Judge against **S7** and the failure line "A
family hit counted on a member whose text does not hold the gold span's text", nothing else. The interface the CTO
stated before the engineer started is in the ticket's notes (`dc3ff3ce`).

Check in particular:
- with no `evaluation_families:` declared, every score and every per-question line is byte for byte today's;
- a family hit needs the gold span's normalised text in the member's evidence text, never the path alone;
- each family hit is named in the per-question line;
- `--kept` re-scores kept outputs without a retriever, and gives the same result as a live measure would on the same
  outputs;
- the measure never writes the sets root or a label file.

**Facts:** the S7 cases pass on the branch (the CTO's earlier run). Run the S7 acceptance cases and the unit tests
through the heavy slot (`tools/heavy_slot.sh`), and record their counts. No GPU, no real model, no `gov retrieve` on the
real repository, no measure on real sets.

**The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
`memory-verdict` or `memory-verdict-2` folder. The tests plant their own sets.

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

**Your record:** for S7 and the failure line (`failure-5`), what you checked, the test counts, and the findings, each
with `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`, and the fenced `verdict` block
in the form above (one entry per KPI line; `scope` in or out for each finding). Then return the record's path and the
verdict block. Est.: 1 hour.
