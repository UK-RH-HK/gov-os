# W2-61h's independent test designer: S7, the source families (DEC-1078 (4), DEC-1079)

You are W2-61h's independent test designer (`DAEO-h2k3`), launched by `gov launch` under that ticket's id. The CTO acts
as the ticket's lead (no lead runs, DEC-1051).

**Read first, whole:** `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/EMG-d4b-launched.md`
(the launched workers' rules; its "Test designer" paragraph is your job's form), `EMG-common.md` beside it,
`governance/project/orchestration/INTENT-DEC-1052.md`, and the ticket `.tickets/DAEO-h2k3.md`: its KPI line **S7**, the
new failure line, and the note "DEC-1079 placed here" at its end. For the register, grep `### DEC-1078` and
`### DEC-1079`. The measure's matching rule is in `src/gov/retrieval/measure.py`'s docstring and in
`docs/research/memory-measure-audit/RUBRIC.md` section 1 item 2 (the integrated code is readable, DEC-963).

**Never read:** any hidden set (`~/gov-os-eval/`), any run output (`~/gov-os-runs/`); write from S7's text, never from an
implementation of it (none exists yet).

**Your worktree:** `/home/usain/gov-os-worktrees/W2-61h-tests` (branch `w2/W2-61h-tests`, today's integrate). Write only
`tests/acceptance/W2-61h/**`.

**What to test, from S7:** on a planted repository and planted question sets (in temporary folders; never this
repository's sets), with a stand-in retriever that returns chosen evidence:
- a family declared in a planted path map (`evaluation_families:`), and an evidence item in another member whose text
  holds the gold span's text: a hit, named as a family hit in the per-question line;
- the same member whose text does **not** hold the gold span's text: no hit (the failure line);
- a hit by path alone, on a file outside the family: no hit;
- normalisation: the same text with other whitespace, or as a YAML value against Markdown prose, still matches;
- no family declared: every score exactly as today (hit@5, full evidence, MRR);
- re-scoring kept outputs (the measure's kept ranked outputs, the form of `~/gov-os-eval/runs/<point>/<name>-run1/`) with
  families gives the family-aware figures without running a retriever again.
Name in the README map, with full node ids, which case covers which part of S7. Show each red on today's integrated code.

**Runs and commits:** through the heavy slot where the sandbox allows it, else your own files one at a time; with
`PYTHONPATH=/home/usain/gov-os-worktrees/W2-61h-tests/src`, an empty `HOME`, `PYTHONUSERBASE=/home/usain/.local`,
`-o tmp_path_retention_policy=failed -p no:cacheprovider`. Commits: `Task: DAEO-h2k3`, `Implements: DEC-1078, DEC-1079`,
`Role: independent-test-designer`, `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Return: the sandbox and
`ps` checks, the twelve labelled fields, then `TESTS-READY` text. Est.: 2 hours.
