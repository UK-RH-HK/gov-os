"""Builds docs/probes/DAEO-weh2/PR-DAEO-weh2.md: front matter, the lead's summary, the reviewer's record verbatim
(from its 'task: DAEO-weh2' line on), with the body's full commit id shortened under row W2-L423's rule."""
from pathlib import Path

ROOT = Path("/home/usain/gov-os-worktrees/W2-180")
FULL = "0d98914dc37f3705beed02d72d98500ea9e48fd4"
res = (ROOT / ".gov-runtime/scratch/lead/log/rv-1.result.md").read_text(encoding="utf-8")
lines = res.splitlines()
start = next(i for i, l in enumerate(lines) if l.strip() == "task: DAEO-weh2")
body = "\n".join(lines[start:]).replace(
    "probed_commit: " + FULL,
    "probed_commit: 0d98914dc37f (the full id is in the front matter; the lead shortened it here under row W2-L423's rule)")
assert FULL not in body

head = f"""---
type: probe
task: DAEO-weh2
reviewer_session: ecc7954f-bc80-4434-80f4-42135b62d88e
implementer_session: 64909468-8787-4179-a0b0-7ea52ce69641, 622b2f28-a79e-470e-967c-58151c382c96
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: {FULL}
decisions_applied: [DEC-866, DEC-253, DEC-966, DEC-989]
---

# Probe record: W2-180 (DAEO-weh2), the LITE review of the branch-scope revision of W2-170's F5 and W2-173's F3/F4 path cases

- **What was probed.** Head `0d98914dc37f` of `w2/W2-180`, against base `6c9a5bb525ee`, the merge-base with `w2/integrate`, which holds the ticket's "Widened" section. It holds two independent test designer commits, each merged by the ticket lead:
  - `e3ff31fc5f87` (td-1, session `64909468-8787-4179-a0b0-7ea52ce69641`): W2-170's `test_f5_the_branch_changes_only_paths_the_ticket_allows` now goes through `judge_f5_paths(root)`. It judges only when HEAD is `refs/heads/w2/W2-170` and is skipped, with its reason, on any other checkout. Six planted cases go with it.
  - `56f401a86c90` (td-2, session `622b2f28-a79e-470e-967c-58151c382c96`): W2-173's F3 and F4 now go through `judge_f3_paths` and `judge_f4_paths`, which judge only on `w2/W2-173`. Planted cases go with them.
  - Both READMEs are updated. Both commits carry the Rewrite-Reason (DEC-866).
  - Both designers were Sonnet at effort high, class C1.
- **Who probed.** A fresh read-only reviewer, role `independent-auditor`, session `ecc7954f-bc80-4434-80f4-42135b62d88e`, Opus at effort high, class C1, 2026-11-12. It was started through `gov launch` under its OS sandbox, and the ticket lead commissioned and judged it.
  - The lead's tripwire shows no change in this ticket's trees during its session, and `git status --porcelain` stayed empty.
- **Step 0.**
  - The write outside the worktree was refused: read-only file system.
  - `git hash-object -w` and `git update-index --refresh` worked.
  - `gov.__file__` = `/home/usain/gov-os-worktrees/W2-180/src/gov/__init__.py`.
  - One Write-tool refusal for a probe script under TMPDIR, taken and not retried. The verdict does not rest on it.
- **The lead's runs beside it, all on `0d98914dc37f`.**
  - Clone check (`.gov-runtime/scratch/lead/log/clone-check.txt`): a clone under `/tmp`, with the head checked out three ways.
    - As the branch `w2/W2-170`: F5 fails on `tests/acceptance/W2-173/*` (outside W2-170's paths), and F3 and F4 skip with their reason.
    - As `w2/W2-173`: F4 fails on `tests/acceptance/W2-170/*`, F3 passes, and F5 skips with its reason.
    - Detached: all three skip with "this is a detached HEAD".
    - The clone is removed.
  - `gov accept W2-180`: pass, 184 passed, 0 failed, 1 skipped (the real F5 on `w2/W2-180`).
  - `lead_verify`: RED, 4,062 tests, 6 failed. All six are W2-96's shared base reds:
    - four fail on `w2/integrate`'s head `d02e957ba35a` (`.gov-runtime/scratch/lead/log/base-red.txt`);
    - the other two pass when run alone on this head (`rerun-alone.txt`, load-sensitive).
  - The designers' folder runs: W2-170 184 passed, 1 skipped; W2-173 91 passed, 2 skipped. The skips are the real path cases on the tests branch.
- **Threat model (DEC-801, DEC-808).** The review judges against ADR-0001's threat model: honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries.
- **Verdict: pass.** Classification (DEC-809): yes and fails open or loses work 0; yes and other 0; rows 2 (RV1, RV2). The lead's judgement agrees:
  - RV1 is a row. If the judge itself were later revised to skip on the own branch, the planted "must fail" and "must pass" cases would only skip, not go red. This needs a further wrong revision, which would itself be reviewed.
  - RV2 is a row. On a reopened W2-170 or W2-173, the queue's candidate-merge run no longer judges the paths. This is the CTO's ruling, and both tickets are closed.
  - Both are returned to the orchestrator as residuals.

## The reviewer's record (verbatim)

"""
out = ROOT / "docs/probes/DAEO-weh2/PR-DAEO-weh2.md"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(head + body.rstrip() + "\n", encoding="utf-8")
print(out, len(out.read_text().splitlines()))
