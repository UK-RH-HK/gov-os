"""Assemble run 5's probe record from the last reviewer's returned body (DEC-733): frontmatter and a header by the
lead, then the reviewer's body as returned."""
from pathlib import Path

LEAD = Path("/home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead")
OUT = Path("/home/usain/gov-os-worktrees/W2-54/docs/probes/DAEO-0rfi/PR-DAEO-0rfi-run5.md")

result = (LEAD / "log" / "rv3-result.md").read_text(encoding="utf-8")
body = result[result.index("Verdict: pass"):].strip() + "\n"

head = """---
type: probe
task: DAEO-0rfi
reviewer_session: 4a232e30-2b53-42df-b683-5b231525a33f
implementer_session: cf375c20-03b8-446b-8581-07b1bb46be39
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: ed2037fd6a5821f7c4e96e0dae4d25cc75b96c06
---

# Probe record: W2-54 (DAEO-0rfi), run 5 (DEC-874), the second and last review (DEC-413)

- **What was probed.** Head `ed2037fd6a5821f7c4e96e0dae4d25cc75b96c06` of `w2/W2-54` (CP-DAEO-0rfi-0034): run 5's
  whole change since `226ec458` — the merge-back `de42a87d` of `w2/integrate` (`a2e7b691`), the corrections of
  the four cases on W2-02's other types to KPI S4's meaning (DEC-874 item 1: W2-54's own commits bring in no
  schema file and no type of W2-02's beyond `audit-report`, before and after W2-02 merges) — the test designer's
  `49f1f81e` (session `14884e7b-5fd9-499f-9cc9-acf07e39ece4`), the engineer's `40909d21` (session
  `cf375c20-03b8-446b-8581-07b1bb46be39`, the builder test) — and the second test-design batch `92ba6f02` (session
  `4aff6f98-dca6-4884-826d-ab2b54a8788a`), which answered the first review's finding that one case did not read
  the history it named. The code is unchanged since the probe of `7661402c` (`PR-DAEO-0rfi.md`).
- **Who probed.** A fresh read-only reviewer (role `independent-auditor`, session
  `4a232e30-2b53-42df-b683-5b231525a33f`, 2026-10-20), started through `gov launch` under its OS sandbox with the
  reading tools alone; commissioned and judged by the orchestrator (DEC-137). It wrote nothing in the repository:
  the lead's tripwire before and after its session shows no change in this worktree. The first review of run 5
  (session `0f50d90c-c613-4241-8e21-a5c7f594e5bb`, head `0ccafe25`) passed with four rows; its record stays a
  draft, as the head changed after it.
- **Threat model (DEC-801, DEC-808).** Reviewers and probes judge against ADR-0001's threat model: honest agent
  mistakes and plausible accidents in ordinary work, not deliberate adversaries. Every finding carries two lines,
  `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`; only "yes" with "fails open"
  or "loses work" fails the probe. The orchestrator's judgement: no finding is both; R1 to R5 are rows.

## The reviewer's record

"""
OUT.write_text(head + body, encoding="utf-8")
print(OUT, len(head + body))
