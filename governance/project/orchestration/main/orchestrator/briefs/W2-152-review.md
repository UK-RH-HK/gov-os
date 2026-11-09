# W2-152 — the independent review (DAEO-o5x1)

You are a fresh, read-only independent reviewer. Review **W2-152** (`.tickets/DAEO-o5x1.md`: read it in full, with
its body's "Interface" and "Clarified after the test design"): `gov brief`, a filled brief from the ticket and the
facts file, refused when the ticket is not READY by code (DEC-1050, DEC-1052, DEC-1083, DEC-1088 (3)). The design is
`governance/project/orchestration/packages/LIFT-1/R3-TEMPLATES.md` §B ("Filling") and §D TPL-3 and TPL-5. The
templates it fills are `template/governance/kernel/templates/`.

## What to review
- **The branch:** `w2/W2-152` in `/home/usain/gov-os-worktrees/W2-152` at `16d052d2fda7`, against `w2/integrate`:
  `src/gov/brief/` (`build.py`, `command.py`), `tests/unit/brief/`, the `ready.new_since` key in
  `governance/project/facts.yaml` and its schema, `docs/changes/W2-152-evidence.md`, and the designer's cases
  `tests/acceptance/W2-152/` (TESTS-READY `b08ede6890c6`).
- **The runs (the CTO's, outside the sandbox):** `gov accept W2-152` 56/56; `gov accept W2-128` 92/92; unit tests
  12/12. A real run, `gov brief engineer W2-153`, refused with `KPI_NO_VERIFY F1, F2`: that ticket's failure lines
  carry no `Verify:`. Structural pass: links NOTICE, 44 planted fixture ids in the cases (W2-129 S17's row).

## Check
- Each KPI line S1 to S10 and failure line F1 to F3 against the code, not only the cases. Could the code pass the
  cases and still miss a line? In particular:
  - S1 and F1: is the output deterministic (ordering, paths, the environment)?
  - S4: no role-template text leaks into the brief.
  - S5: the "until <ticket>" refusal, for both a template line and a `--part` line.
  - S8 and S9: the ready check's required and advisory split follows DEC-1083, and `ready.new_since` follows
    DEC-1088 (3).
  - F3: read-only.
- **What it means in ordinary use.** DEC-1083 makes a KPI line without a verify a refusal. Count how many open and
  in-progress tickets in `.tickets/` `gov brief` would refuse today, and for what. Say whether that is the decision
  working as written or a gap, and what evidence would settle it. Do not change anything.
- Robustness: a malformed ticket, a missing facts key, a missing template, an unknown role. Each should be a named
  refusal, never a traceback.
- Does it read or write anything beyond the interface's inputs?

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`, and the evidence that would reverse it
(DEC-1014).

## Write and return
- **You write nothing** in any tree, and run nothing that writes: tests read-only with `-p no:cacheprovider`, only
  `tests/acceptance/W2-152`, `tests/unit/brief` and `gov brief` itself. Single simple Bash commands (DEC-1080). The
  hidden-half rule holds: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **Search again once (DEC-1092 (1)):** if a search does not answer, search once more in your own words. Then answer
  from both, with path and lines, or say "not found".
- **Your record is your session's final message**, in full:
  - the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
  - your verdict per line, and every finding with its lines and `scope: in|out`;
  - at the end, the fenced `verdict` block in DEC-1010's form, one entry per line (S1 to S10, F1 to F3):
    `{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ...]}`
