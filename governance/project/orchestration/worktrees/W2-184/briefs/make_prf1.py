"""Write the narrow-check record (DEC-1154, DEC-1177) with its front matter (W2-184 lead scratch)."""
from pathlib import Path

src = Path("/home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/log/rv-f1-result.md").read_text().splitlines()
start = next(i for i, line in enumerate(src) if line.startswith("# Narrow check of DAEO-6f0s"))
end = next(i for i in range(start, len(src)) if src[i].strip() == "judgement: pass")
body = "\n".join(src[start:end + 1]).rstrip() + "\n"
front = """---
type: probe
task: DAEO-6f0s
check: "narrow independent check after review round 2 (DEC-1154: the owner's DEC-1177 (1) and the CTO's P-W2-184-2 (a)); not a review round (DEC-1010)"
reviewer_session: e0e76090-d60a-43ab-9f61-d8749106f10b
implementer_session: 06690070-6c47-4c6d-9496-4b59a88390b0, b8148380-9e1a-43ae-9b7c-f9ebcc2f6bb5
reviewer_wrote_nothing: true
commissioned_by: orchestrator (the W2-184 ticket lead)
judged_by: orchestrator (the W2-184 ticket lead)
judgement: pass
probed_commit: fb2ea8460857c9410e4dcaf63353e07ec75a606f
---

"""
note = """
## The lead's triage (DEC-1010 item 1)

- No finding blocks: none is in scope, ordinary work yes and fails open or loses work.
- F1 (a lead launch takes `--reason`, `--trial` and `--owner-named` silently; ordinary work yes, consequence other),
  F2 (one empty or partial launch record stops every worker launch; ordinary work no, fails closed) and F3 (P-td5-2's
  stale-copy case; ordinary work no): Wave 3 hardening rows, for the CTO.
- The launch of this check: review_round 3, owner_named DEC-1177, model_source promotion, effort high (`after --`).
"""
Path("/home/usain/gov-os-worktrees/W2-184/docs/probes/DAEO-6f0s/PR-DAEO-6f0s-f1.md").write_text(front + body + note)
print("ok", end - start + 1)
