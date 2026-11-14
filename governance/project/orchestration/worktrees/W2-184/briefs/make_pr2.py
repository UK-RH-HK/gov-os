"""Write the round-2 probe record (the FULL ticket's probe) with its front matter (W2-184 lead scratch)."""
from pathlib import Path

src = Path("/home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/log/rv-2-result.md").read_text().splitlines()
start = next(i for i, line in enumerate(src) if line.startswith("# Probe of DAEO-6f0s"))
end = next(i for i in range(start, len(src)) if src[i].strip() == "judgement: fail")
body = "\n".join(src[start:end + 1]).rstrip() + "\n"
front = """---
type: probe
task: DAEO-6f0s
reviewer_session: d4de9d3f-1794-4f4a-b076-ad0cb504f3fa
implementer_session: 0f3225ba-d30e-41de-a030-d0f7a296c833, 7846bd54-f3ac-4fa5-87b0-9ac81474f9c4, 13dc87dc-9efc-4adb-8e6b-51b22c9bf937, 4496a4ad-8bc9-4963-9bb4-3c43f952e9ef
reviewer_wrote_nothing: true
commissioned_by: orchestrator (the W2-184 ticket lead)
judged_by: orchestrator (the W2-184 ticket lead)
judgement: fail
probed_commit: 89edff41ff0f7ae6734ba31af69b0a11b57394bf
---

"""
note = """
## The lead's triage (DEC-1010 item 1: the last round; the blocking finding goes to the owner once, with options)

- F1: blocks (in scope, ordinary work yes, fails open). Not fixed in this run: no third round (DEC-1010). The owner's
  package (the reviewer's options (a) to (d)) is in the lead's return; the lead's recommendation is (a), with (c) as
  the stop-gap.
- F2 (a resume of a resume counted as a new round), F4 (`src/gov/secrets/**` at C2): rows for the CTO.
- F3: Wave 3 row (path forms that match no C3 glob; no ticket uses them).
- F5: out of scope; the lead's reading of DEC-1167 (2) stands.
- Round 1's F1, F8 and F2: fixed, as judged above.
"""
Path("/home/usain/gov-os-worktrees/W2-184/docs/probes/DAEO-6f0s/PR-DAEO-6f0s.md").write_text(front + body + note)
print("ok", end - start + 1)
