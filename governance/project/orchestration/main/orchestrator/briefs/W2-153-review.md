# W2-153 — the independent review (DAEO-8s85)

You are a fresh, read-only independent reviewer. Review **W2-153** (`.tickets/DAEO-8s85.md`: read it in full, with
its "Interface" and "Decided after the build"): the role template delivered at launch (W2-128 TPL-4; DEC-1050). The
design is `R3-TEMPLATES.md` §B ("Delivery") and §D TPL-4. The copies ACT it lands with is
`governance/project/orchestration/packages/ACT-CLAUDE-COPIES-1.md`.

## What to review
- **The branch:** `w2/W2-153` in `/home/usain/gov-os-worktrees/W2-153` at `96e600d65`, against `w2/integrate`. It
  holds `src/gov/launch/launcher.py`, `src/gov/adapters/portability.py`, the dispatcher's `launch_now.sh`, the six
  `.rulesync/subagents/*.md` sources and the template's copies, the four launcher unit test files' fixtures, the
  evidence file, and the designer's cases `tests/acceptance/W2-153/` (TESTS-READY `0c73fd5a2cbe`, then
  `2737423ba017`).
- **Untracked in that tree:** `.claude/templates/` holds eight byte copies the CTO placed, so the branch's own
  launcher could start its workers. They are not part of the change.
- **The runs (the CTO's, outside the sandbox):** `gov accept W2-153` 51/51; W2-128 92/92; `tests/unit/launch` and
  `tests/unit/adapters` 207 passed, 0 failed.

## Check
- S1 to S5, F1 and F2 against the code. In particular:
  - Is the refusal unconditional (F1)?
  - Is the flag the only change to the argv, for workers and for leads alike (F2)?
  - Is the role → template map one constant, reused by the portability check?
  - Does the dispatcher's form refuse before calling `claude`?
- **S3:** the composition (rulesync front matter as on integrate, plus `claudecode.skills`, plus the role template's
  body). Do the generated agents carry their skills? Generate on a temporary copy with
  `rulesync generate --targets claudecode --features subagents --input-roots <copy>/.rulesync` into an empty folder.
  The test designer's `test-design` rule (D-5): is it stated, and will it switch when W2-128's round 2a lands?
- **S4:** `--write-templates`: the eight files, byte for byte, nothing else written.
- **The landing order (S5):** after this merges and before the ACT installs the copies, every `gov launch` in a tree
  without `.claude/templates/` is refused. Say what that means for live work, and what must land together. The
  CTO's plan: merge only at the ACT. Is that enough?
- The four unit test files: only the fixtures and the one assert changed?

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`, and the evidence that would reverse it
(DEC-1014).

## Write and return
- **You write nothing** in any tree, and run nothing that writes there: tests read-only with
  `-p no:cacheprovider`; rulesync only into a temporary folder. Single simple Bash commands (DEC-1080). Never start
  a real session. The hidden-half rule holds: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any
  `hidden`, `memory-verdict` or `memory-verdict-2` folder.
- **Search again once (DEC-1092 (1)):** if a search does not answer, search once more in your own words. Then answer
  from both, with path and lines, or say "not found".
- **Your record is your session's final message**, in full:
  - the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
  - your verdict per line, and every finding with its lines and `scope: in|out`;
  - at the end, the fenced `verdict` block in DEC-1010's form, one entry per line (S1 to S5, F1, F2):
    `{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ...]}`
