# W2-129 — the narrow review of S17, planted ids in test fixtures (D-6 part 2; DEC-1109 (2)) (DAEO-q7lk)

You are a fresh, read-only independent reviewer. **Narrow scope: one line, S17,** and its new failure line, in
`.tickets/DAEO-q7lk.md` (read the line, the failure line and the "D-6 part 2 placed here" note). The rest of W2-129 was
reviewed READY and merged; it is not re-opened here. READY is computed by `verdict.py` from your block.

S17, briefly: in a Python test file (`tests/**/*.py`) that parses, an id inside a string literal that is not a
docstring is a planted fixture id. It gives no UNKNOWN_ID, and its ENFORCES_SUPERSEDED (from W2-55's propagation) is
carried only when the old id also stands on the line outside such a literal. Comments, docstrings, non-Python test
files and files that do not parse are judged as today. W2-55's module is unchanged.

## What to review
- **The branch:** `w2/W2-129-d6` in `/home/usain/gov-os-worktrees/W2-129-d6`, head `0eb83d9ad`, made from
  `w2/integrate` at `26c3133aa`. Read `git diff 26c3133aa..0eb83d9ad`.
  - The designer's cases: `tests/acceptance/W2-129/test_w2_129_fixtures.py` and the README's S17 line (`7255284a`,
    merged at `7940fad46`).
  - The engineer's change: `99d54ecee` (`src/gov/links/**`, `tests/unit/links/` with 5 new cases) and `0eb83d9ad`
    (`docs/research/W2-129-links.md` §9).
- **The runs:** the CTO's run, outside the sandbox at `0eb83d9ad` with a scratch HOME: `gov accept W2-129` passes
  150/0, success-17 8/0, failure-7 7/0. The engineer's: unit `tests/unit/links` 66/66. `gov links --all`: UNKNOWN_ID
  for the test designer 560 → 60, ENFORCES_SUPERSEDED 73 → 45, nothing else changed, 3.15 s → 3.84 s.

## Check
1. **No real citation dropped:** read the code paths, not only the tests. Look at comments, docstrings (module,
   class, function, async function), non-Python files, files that do not parse, and a line holding the id both in a
   literal and outside it. Look also at f-strings (3.12 tokenizing) and at implicit concatenation. Could an honest
   test author's citation be lost?
2. **Every planted literal quiet:** a planted literal id that is still reported, and that would matter at today's
   counts. The engineer says 27 of the "29" are dropped, and 2 sit in docstrings and are judged as the KPI says.
3. **The embedded-program case:** a `#` line inside a raw triple-quoted string is treated as planted (DEC-798 at
   `tests/acceptance/W2-54/test_w2_54_sandboxed_worker.py:87`). Is that S17's reading?
4. **W2-55 unchanged:** `src/gov/decisions/**` untouched. The filter is only in links' carrying, and the value hits
   are carried as before.
5. **Cost:** parsing each test file once per run; S15 holds (under 10 s).

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding is `scope: in` only if it
concerns S17 or its failure line.

## Write and return
- **You write nothing** in any tree.
- You may run tests read-only (`-p no:cacheprovider`) through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-129-d6/src` and an empty scratch HOME (`PYTHONUSERBASE=/home/usain/.local`
  so pytest is found).
- No GPU. Single simple Bash commands (DEC-1080).
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them.
- **Search again once (DEC-1092 (1)).**
- **Your record is your session's final message**, in full. It holds:
  - the twelve labelled fields of `EMG-common.md` (the sandbox and `ps` checks first);
  - your answers to checks 1-5;
  - every finding, with its two lines and its scope;
  - at the end, the fenced `verdict` block:
    `{"kpis": [{"kpi": "S17", "verdict": "pass|fail", "findings": [...]}, {"kpi": "F7", "verdict": "pass|fail", "findings": [...]}]}`,
    each finding `{"id", "scope", "ordinary_work", "consequence"}`.
