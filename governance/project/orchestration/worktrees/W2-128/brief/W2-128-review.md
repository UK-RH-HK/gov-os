Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-128/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-128 round 1 — the independent review (DAEO-t8mp)

You are a fresh, read-only independent reviewer. Review **W2-128**'s round 1 (`.tickets/DAEO-t8mp.md`: read it in
full, especially the body's "Interface and rounds" section, which says what round 1 holds and what is round 2). The
design is `governance/project/orchestration/packages/LIFT-1/R3-TEMPLATES.md` (§B, §B′, §C, §D, the Appendix); the
link lines `LINK-INTEGRITY.md` §5; the rows `D5-ROWS.md` 1-17.

## What to review
- **The branch:** `w2/W2-128` in `/home/usain/gov-os-worktrees/W2-128`, against `w2/integrate`
  (`git diff w2/integrate...w2/W2-128`): the nine templates and `keys.yaml`, the record templates, the `brief-*.md`
  pointers, `roles/engineer.md` line 5, `governance/project/facts.yaml`, the four schemas, `docs/changes/W2-128-CIT-P.md`,
  and the designer's cases `tests/acceptance/W2-128/`.
- **The runs:** the CTO's `gov accept W2-128` outside the sandbox: 92 passed, 0 failed, every mapped line (TESTS-READY `bd7732def530`; branch head `a6c83d497035`); the schema check: `{"ok": true, "records_validated": 970}` (the worker's run). Known: four W1-35 cases on `brief-*.md` go red by TPL-1 S4 (the CTO confirmed; a test designer's revision under DEC-866 before any merge): judge whether anything else in the tree still depends on the retired brief texts.

## Check
- Each round-1 line (S1-S6's round-1 parts, S8, S10's S1-S2, S14-S21, F1, F7) against the branch, not only against the
  tests: do the cases prove the line, or could a template pass them and still miss it?
- **Contradictions:** does any template state a rule that a kernel role file, a kernel skill or the project briefs
  state differently for the same step (TPL-6 F1's question, by reading; `/doctor prompt-audit` is round 2)? Does any
  template restate a superseded rule (DEC-957, DEC-959, DEC-963, DEC-1010, DEC-1050), or cite a decision that is not
  ACCEPTED?
- **Budget and use:** is each line one that changes what a session does (DEC-1052's narrowing of DEC-851 and DEC-943),
  or history and restatement? Are the `facts.yaml` command forms the ones that work today (the three scripts' real
  usage lines; `gov links --since`), and is every `check:` safe in the sandbox?
- **Old records:** do every existing ticket, lesson, failure and research record stay valid under the schemas?

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`, and the evidence that would reverse it
(DEC-1014).

## Write and return
- **You write nothing** in any tree; run nothing that writes (tests read-only with `-p no:cacheprovider`, only
  `tests/acceptance/W2-128`). Single simple Bash commands (DEC-1080). The hidden-half rule holds: never open anything
  under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder.
- **Search again once (DEC-1092 (1)):** if a search does not answer, search once more in your own words; then answer
  from both, with path and lines, or say "not found".
- **Your record is your session's final message**, in full: the twelve labelled fields of `EMG-common.md` (sandbox and
  `ps` checks first), your verdict per round-1 line, every finding with its lines and `scope: in|out`, and at the end
  the fenced `verdict` block in DEC-1010's form:
  `{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ...]}`
  with one entry per round-1 line.
