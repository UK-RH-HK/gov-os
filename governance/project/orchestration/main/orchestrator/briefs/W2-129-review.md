# W2-129's review: `gov links` (DEC-1073 (5)(b), DEC-1087 (4), DEC-1088 (6))

You are an independent reviewer for the CTO. You read everything and change nothing: your one write is your record,
`.gov-runtime/scratch/orchestrator/reviews/w2-129.md` in the main tree. Read
`.gov-runtime/scratch/orchestrator/briefs/EMG-common.md` for the common rules.

**What to review:** branch `w2/W2-129` (worktree `/home/usain/gov-os-worktrees/W2-129`) against `w2/integrate`.
- **The engineer's commits:** `src/gov/links/**`, `tests/unit/links/**`, `docs/research/W2-129-links.md`.
- **The ticket:** `.tickets/DAEO-q7lk.md`. Judge against its success lines S1 to S16 (numbered in the ticket's order;
  S16 is the line marked `[added, DEC-1088]`) and its failure lines, and its notes: TESTS-READY, the points settled.
- **The design:** `governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md` §4.
- **The S9 form the CTO accepted:** a commit's finding names its bare `Role:` in the text line's role field, and the
  landed lead in the JSON (`lead`).

Check in particular:
- it writes nothing but its mark: no record changed, no model, network or GPU;
- it is never a gate: nothing in close, the queue, landing, launch, claim, readiness or hooks calls it;
- one pattern set: it imports the loader's `register_statements` and does not copy it;
- PROPOSED is never counted as current;
- the incremental range and the mark, so no finding older than the mark is lost (listed or counted);
- S16:
  - a closed ticket is judged by its status in the commit's parent;
  - an open ticket's changed fields with no decision id are flagged;
  - status, assignee or links alone are not flagged;
- every finding has its code, ids, path and line, role and fix, and free-text findings are marked `(text)`;
- "not applicable" on a repository without a register or tickets.

**Facts the CTO has:**
- `gov accept W2-129` 135/135;
- unit tests 55 passed;
- `--all` 2.80 s and `--since HEAD~1` 2.83 s on the engineer's worktree (median of five);
- 210 S16 findings on this repository's history (117 closed-ticket edits, 93 unmarked changes, 72 tickets, 60
  commits): records to clean, not a tool fault, unless you find otherwise.

Re-run what you need through the heavy slot (`HOME=/home/usain`). Run `gov links --all` read-only from the worktree.

**The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
`memory-verdict` or `memory-verdict-2` folder.

**DEC-1080:**
- read with the Read and Grep tools;
- one simple command per Bash call;
- no `cd … &&` chains and no `git -C`;
- one line before any command that will ask for permission.

**The judgement rules:** `governance/project/briefs/JUDGEMENT.md`, word for word. Each finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.

**Your record:** per KPI line (S1 to S16, `failure-1` to `failure-6`), what you checked and the findings. End with the
fenced `verdict` block:
`{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`.
Then return the record's path and the verdict block. Est.: 1.5 hours.
