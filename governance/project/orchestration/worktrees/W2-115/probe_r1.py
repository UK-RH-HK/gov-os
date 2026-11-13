from pathlib import Path

res = Path("/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/lead/log/rev-1.result.md").read_text().splitlines()
start = res.index("verdict: FAIL") - 1          # the opening fence of the reviewer's verdict block
end = max(i for i, l in enumerate(res) if l.strip() == "]}") + 1  # the closing fence follows
blocks = "\n".join(res[start:end + 1])
assert blocks.startswith("```") and blocks.endswith("```"), blocks[-20:]

head = """---
type: probe
task: DAEO-emq1
round: 1
reviewer_session: b85898ea-e991-4c5c-ac8a-97e917b26548
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: fail
probed_commit: 569c2933d33cfb14688fa79f09112018c9e43a18
decisions_applied: DEC-1010, DEC-988, DEC-989, DEC-1083, DEC-1001, DEC-1002, DEC-983
---

# Probe record: W2-115 (DAEO-emq1), the smart close, FULL review round 1 of 2: FAIL

A fresh Independent Auditor session (`b85898ea-e991-4c5c-ac8a-97e917b26548`, claude-opus-5-5, effort high, read-only,
class C3) probed head `569c2933d33c` (the built close of run 2, w2/integrate merged at `6831c6e3a`, td-3's revisions
of W1-39 and W2-77 merged at `569c2933d`) and wrote nothing (`git status --porcelain` empty). This is round 1 of at
most 2 (DEC-1010 item 1). The reviewer's two blocks below are copied unchanged from its return; the lead commits this
record because the reviewer is launched read-only (the reviewer's F-4 is about exactly this).

## What was probed

- The whole change `0aec6e10c..569c2933d33c` (only `allowed_paths:`, `tests/acceptance/W2-115/` and the six td-3
  files; acceptance tests changed only in the test designer's commits 01ececd0b, 0bae231ad, d54172ffb).
- W2-115 acceptance, `tests/unit/close/`, W1-39's revised case, W2-77, W1-30 and W2-07 (the strict close, F4):
  272 passed, through the heavy-slot gate.
- Three planted probes (A: an untrailered commit before the ticket's first trailered one; B: a batch whose culprit's
  red is its own new test; C: integration work merged into the ticket branch breaking a selected test) and six
  mutants of the fail-open paths (S4's timeout match and failure-type match, S11's writer check, S2's refusal, S6's
  two guards): every non-equivalent mutant killed.
- Found sound: S1 (no file is strict; another value refused; the strict path unchanged), S3 (one code path for
  `--select`, `--verify` and the close), F2 (no accepted-reds or load-sensitive list), S8, S10, S13, S11's parsing.

## The lead's check

The lead read `src/gov/close/select.py:529` (`ticket_change`: the base is the first parent of the oldest
Task-trailered non-merge commit) and `select.py:749` (the changed set counted from the newest green record,
`green_base`) at `569c2933d33c`, and confirms F-1's mechanism: a commit between the green base and the first trailered
commit is counted in the change for the selection but sits in the base the reds are judged against.

## The reviewer's verdict

"""
Path("/home/usain/gov-os-worktrees/W2-115/docs/probes/DAEO-emq1").mkdir(parents=True, exist_ok=True)
Path("/home/usain/gov-os-worktrees/W2-115/docs/probes/DAEO-emq1/PR-DAEO-emq1-round-1.md").write_text(
    head + blocks + "\n\n## Judgement\n\n**Fail** (the reviewer's): F-1 is in scope, reachable in ordinary work and "
    "fails open (S4, F1). The fix round and the open calls (F-2 to F-5) go to the CTO in the lead's return.\n")
print("written", len(blocks))
