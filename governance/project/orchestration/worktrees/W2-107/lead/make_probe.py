"""Writes docs/probes/DAEO-kiar/PR-DAEO-kiar.md from the second reviewer's return: its record whole, the sessions
filled in, and the lead's judgement before it (DEC-733)."""
from pathlib import Path

LEAD = Path("/home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead")
text = (LEAD / "probes/rev-2-return.md").read_text(encoding="utf-8")
start = text.index("```\n---\ntype: probe")
record = text[start + 4:text.rindex("```")].rstrip() + "\n"
record = record.replace("reviewer_session: lead fills", "reviewer_session: 9734e4d7-6a4f-4607-b316-dbb9eb71ccf1")
record = record.replace("implementer_session: b13fb711-df4f-4b90-8459-574321099009",
                        "implementer_session: 50ab8c74-3103-4e33-ac76-7f6c3db37e74")
head, body = record.split("\n---\n", 1)
assert "probed_commit: 654fd0e3e26c3fa92feb6d106254b35d183ee853" in head and "judgement: pass" in head
judgement = """
# Probe record: W2-107 (DAEO-kiar), the second and last review (DEC-413)

## The lead's judgement

- **Who probed.** A fresh read-only reviewer: role `independent-auditor`, session `9734e4d7-6a4f-4607-b316-dbb9eb71ccf1`, 2026-10-31, effort max, started through `gov launch` under its OS sandbox with the reading tools alone. It wrote nothing in the repository: the lead's tripwire before and after its session shows no change in this worktree, the tests worktree or the main tree by it.
- **What was probed.** Head `654fd0e3e26c` of `w2/W2-107`. The ticket's code is round 1's `94ac4110b469` and `39186c5a9b73` (engineer session `b13fb711-df4f-4b90-8459-574321099009`) and round 2's `07ae41c63d12` (engineer session `50ab8c74-3103-4e33-ac76-7f6c3db37e74`, the last implementer). Its acceptance tests are `83fdd88d43f7`, `4f94f5bf5b68` and `03b7bcddc935`, by independent test designers; the rest are the lead's merges and checkpoint records.
- **The first review** (session `f9562598-f40e-41ef-b83d-85b313082ca8`, head `a6c459c59221`) failed on F-1, F-2 and F-3 (each "yes" and "fails open"); R-1 rode along. Round 2 fixed them: a test design batch from the findings as behaviours (DEC-136), then an engineer. Its record is kept as a draft, not committed (DEC-733).
- **Judged by the threat model (DEC-801, DEC-808).** Only "yes" with "fails open" or "loses work" fails a probe. No finding below is both. R-A, R-C, R-D and R-E are rows for the Wave 3 hardening pass. R-B is "other" (speed). The declared residual of a gitleaks upgraded behind a shim during one process's run is judged a residual, not a round: within that one process the old release's verdicts answer only texts that the same rebuild's lexical index already took under that release's own verdict, and the next process asks the version again and forgets them all.
- **Judgement: pass.**

## The reviewer's record
"""
out = Path("/home/usain/gov-os-worktrees/W2-107/docs/probes/DAEO-kiar/PR-DAEO-kiar.md")
out.parent.mkdir(parents=True, exist_ok=True)
body = body.replace("# Probe record: W2-107 (DAEO-kiar)\n", "", 1)
out.write_text(head + "\n---\n" + judgement + body, encoding="utf-8")
print(out, len(out.read_text().splitlines()), "lines")
