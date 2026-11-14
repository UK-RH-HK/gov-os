"""Write the R1-R3 narrow-check record (DEC-1154, DEC-1180 (4)) with its front matter (W2-184 lead scratch)."""
from pathlib import Path

src = Path("/home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/log/rv-r-result.md").read_text().splitlines()
start = next(i for i, line in enumerate(src) if line.startswith("# Narrow check of DAEO-6f0s"))
end = next(i for i in range(start, len(src)) if src[i].strip() == "judgement: pass")
body = "\n".join(src[start:end + 1]).rstrip() + "\n"
front = """---
type: probe
task: DAEO-6f0s
check: "narrow independent check of R1-R3 after the reopening (DEC-1154; the CTO under DEC-1180 (4)); not a review round (DEC-1010)"
reviewer_session: 7fa5e020-b064-4384-b7eb-bb47b6ff6ca0
implementer_session: fddda06e-4efb-484e-8335-6d322d560d40, cee1beef-a9fe-4ce9-8989-4aa186043e0a
reviewer_wrote_nothing: true
commissioned_by: orchestrator (the W2-184 ticket lead)
judged_by: orchestrator (the W2-184 ticket lead)
judgement: pass
probed_commit: 90e657a3583bf4e8edfd40e69a0591e981097dfa
base_commit: bbe1510f899b4599222a1cfc6939bf13b5350222
---

"""
note = """
## The lead's triage (DEC-1010 item 1)

- No finding blocks: none is in scope with ordinary work yes and a consequence that fails open or loses work.
- F1 (no hard links in the record folder's file system: every worker launch refused, fails closed; ordinary work no)
  and F2 (an unlink failing in the microseconds after the link can leave a whole record under a refusal; ordinary work
  no, consequence other): for the CTO, who decides under DEC-1180 (4) whether they are fixed in this flow or are
  rows.
- The launch of this check: review_round 4, owner_named DEC-1180, model_source promotion (a fail-open finding,
  `docs/probes/DAEO-6f0s/PR-DAEO-6f0s-f1.md`), effort high (`after --`).
"""
Path("/home/usain/gov-os-worktrees/W2-184/docs/probes/DAEO-6f0s/PR-DAEO-6f0s-r.md").write_text(front + body + note)
print("ok", end - start + 1)
