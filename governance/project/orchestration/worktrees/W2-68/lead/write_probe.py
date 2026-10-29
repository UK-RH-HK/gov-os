"""Write the probe record from the reviewer's returned content, with the lead's note (DEC-733)."""
from pathlib import Path

W = Path("/home/usain/gov-os-worktrees/W2-68")
src = (W / ".gov-runtime/scratch/lead/probes-rev-1-result.md").read_text()
start = src.index("```markdown\n") + len("```markdown\n")
end = src.rindex("```")
body = src[start:end]
fm_end = body.index("\n---\n", 4) + len("\n---\n")
front = body[:fm_end].replace(
    "implementer_session: see the lead's note",
    'implementer_session: "0959d62f-294a-4664-8baf-a3a5941301f1, fec0320a-a8ef-4b38-a0bd-e607d45429e7, '
    'ef0d7c9f-042d-44b4-9347-8bc1f38f0ae0"')
assert 'implementer_session: "0959' in front
rest = body[fm_end:]
title_end = rest.index("\n", rest.index("# PR-")) + 1
note = """
## The lead's note

- **Commissioned and judged** by the ticket lead (an orchestrator-role session in this ticket's worktree, DEC-137). The reviewer was a fresh `independent-auditor` session (`7c28b0d3-a218-47a8-ae88-043c99b67f4b`, 2026-10-29), started through `gov launch` under its OS sandbox with the reading tools alone, at effort max. It wrote nothing: the lead's tripwire before and after its session shows no change in this worktree or any other tree.
- **The implementer sessions** (engineer, each through `gov launch`, sandboxed): `0959d62f-294a-4664-8baf-a3a5941301f1` (the fingerprints, the store, the store check, `refresh`), `fec0320a-a8ef-4b38-a0bd-e607d45429e7` (the batch's run, reuse, the close's lines, the red-run hold), `ef0d7c9f-042d-44b4-9347-8bc1f38f0ae0` (the trial). The design note's first two commits were `3d9cc8b7-1915-44f8-96fa-82adf82f338b`; the acceptance tests `d10b6078-8dd1-46ad-8e5d-576e2eff5727` (independent test designer).
- **The lead's verification at the probed head** (`fd88e61072eb`, after a full rebuild, exit 0): `gov.__file__` in this worktree; collection 16,747 of 16,749 tests (2 deselected), no error; `gov check` exit 0 (23 checks, two YELLOW: `core-decision-citations` on older commits' citations, `openspec-validate` with `openspec` not on the check's PATH; no red); the full parallel run in the close's form 16,536 passed, 31 skipped, 0 failed (44:02); the serial-only list's 63 entries alone 180 passed, 0 failed (18:30); the trailer gate 15 commits, 0 lacking.
- **Verdict: pass.** Classification (DEC-809): 0 findings "yes" with "fails open" or "loses work". F1 no / loses work (a row, and package P-W2-68-PRUNE: the batch's regression reaches W2-66's nightly run, which DEC-915 item 4 keeps out of use until row W2-M406's fix; recommended as an entry criterion of switching the close queue to the batch, DEC-803); F2 to F5 yes / other (rows); F6 no / other (feature-gated, DEC-803). The lead's judgement agrees with the reviewer's.
"""
out = front + rest[:title_end] + note + rest[title_end:]
p = W / "docs/probes/DAEO-2gc7/PR-DAEO-2gc7.md"
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(out, encoding="utf-8")
print(out[:900])
