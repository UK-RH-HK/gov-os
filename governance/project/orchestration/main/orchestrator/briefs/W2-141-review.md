# W2-141 — the independent review (DAEO-xwro), round 1

You are a fresh, read-only independent reviewer. Review **W2-141** (`.tickets/DAEO-xwro.md`: read it in full, with "The
hook side" and "The designer's round-2 points settled"): the guard refuses an engineer's Grep, Glob or recursive Bash
search that can reach its own ticket's acceptance folder unless the call excludes it, and the refusal says how
(DEC-1093 (2), DEC-1102). This is guard code: judge it as such.

## What to review
- **The branch:** `w2/W2-141` in `/home/usain/gov-os-worktrees/W2-141`, against `w2/integrate`
  (`git diff w2/integrate...w2/W2-141`):
  - the decide side, `src/gov/guard/reads.py` (+487 / −16);
  - the staged hook copies for the operator's ACT, `docs/changes/W2-141-hook/role_reads.py`, `pretooluse.py` (only
    `"Glob"` added to the G-14 tool list) and `README.md` (the diffs against the live `.claude/hooks/` files and their
    sha256): compare each copy with the live file in the main tree;
  - the unit tests `tests/unit/guard/test_w2_141_search.py`, the revised rows of `tests/unit/guard/test_reads.py` and
    the one case of `tests/unit/hooks/test_live_hook.py`;
  - the designer's cases `tests/acceptance/W2-141/` (both rounds); `docs/changes/W2-141-evidence.md`.
- **The runs:** the CTO's `gov accept W2-141` outside the sandbox: 182/182. The engineer's: `tests/unit/guard
  tests/unit/hooks tests/acceptance/W2-84`, 352 passed standard and 1,349 passed with every opt-in row, 0 failed.

## Check
- **S1 and S2:** each route (Grep, Glob with `**`, recursive grep, rg, ag, ack, find with a reading action, listings
  piped to a reader) refused when it can reach `tests/acceptance/<T>/` and allowed when it excludes it, by each tool's
  own exclusion rules (grep's `--exclude-dir` is a base name; rg's and Grep's last-matching glob; find's `-prune` and
  negated `-path`); the refusal names the folder and the exclusion.
- **S3 and the failure lines:** nothing else newly refused: other tickets' tests readable; other roles unaffected;
  names-only listings and a grep for the tests' names by pattern still let through; direct reads keep the old
  refusal; a target the guard cannot resolve keeps today's behaviour; no decision made to fail open.
- **The hook copy:** does `role_reads.py`'s copy do on the live hook's routes what `reads.py` does on decide's? Is the
  duplicated block identical (the engineer's test says byte for byte)? Does anything in the copy change behaviour
  beyond W2-141's searches? Is the README enough for the operator to apply it, and to roll it back?
- **Ordinary work:** would an honest engineer's normal searches (in its own `src/` folder, a named file, other
  tickets' tests) now be refused falsely? Name any false refusal you find, with the call.
- `git grep` and other forms "the like" in S2 might cover: what does the code do with them?

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.

## Write and return
- **You write nothing** in any tree; run nothing that writes (tests read-only, `-p no:cacheprovider`, through the
  heavy slot, your real HOME). Single simple Bash commands (DEC-1080). The hidden-half rule holds: never open anything
  under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder.
- **Search again once (DEC-1092 (1)):** if a search does not answer, search once more in your own words; then answer
  from both, with path and lines, or say "not found".
- **Your record is your session's final message**, in full (the launcher keeps it; the CTO transcribes it): the twelve
  labelled fields of `EMG-common.md` (sandbox and `ps` checks first), your verdict per line, every finding with its two
  lines and `scope: in|out`, and at the end the fenced `verdict` block:
  `{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ... "S2", "S3"]}`.
