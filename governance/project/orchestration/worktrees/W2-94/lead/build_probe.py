src = open("/home/usain/gov-os-worktrees/W2-94/.gov-runtime/scratch/lead/log/au-1.result.md", encoding="utf-8").read().splitlines()
body = src[30:]  # from "# Probe record" on, verbatim
body[0] = "## The reviewer's record (verbatim)"
head = """---
type: probe
task: DAEO-g87r
reviewer_session: 4d20a5e0-e8b9-4a32-9832-e533a200e6b5
implementer_session: f6cf7588-3c00-4822-8a4d-c4cdcc2afb3b
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 69b1233aff3dc13adfbdb4e6b3f8251ba6e170b9
decisions_applied: [DEC-957, DEC-954, DEC-828, DEC-820, DEC-845]
---

# Probe record: W2-94 (DAEO-g87r), the narrow independent check of the counts-only gold check and its acceptance cases

## Summary

- **What was probed.** Head `69b1233aff3dc13adfbdb4e6b3f8251ba6e170b9` of `w2/W2-94`: `fixtures/evaluation/examin/check_gold.py`
  and `tests/acceptance/W2-94/` (commits `83beeb8f6311` and `ad1fd021f83a` by the independent test designer, merged at
  `532429c31` and `69b1233af`). The question set itself is not in the tree; neither the lead, the test designer nor the
  reviewer read it.
- **Who wrote it.** The independent test designer: session `f6cf7588-3c00-4822-8a4d-c4cdcc2afb3b` (`83beeb8f6311`, the script
  and the cases) and session `487d0580-e970-455f-8e5f-77156e1d3a33` (`ad1fd021f83a`, one README map cell).
- **Who probed.** A fresh read-only reviewer: role `independent-auditor`, session `4d20a5e0-e8b9-4a32-9832-e533a200e6b5`,
  2026-11-13, started through `gov launch` under its OS sandbox with Bash, Read, Grep and Glob only; commissioned by the
  ticket lead for the orchestrator and judged by the lead under the orchestrator's rules. It wrote nothing in the
  repository: the lead's tripwire shows no change in this worktree and `git status` is empty after its session.
- **Threat model (DEC-801, DEC-808).** Every finding carries `Ordinary work: yes|no, because ...` and
  `Consequence: fails open|loses work|other`; only "yes" with "fails open" or "loses work" fails the probe.
- **The lead's judgement: pass.** Classification: 6 findings; A, B, C, D, F in scope, ordinary work yes, consequence other
  (each fails closed); E in scope, ordinary work no, fails open (a Wave 3 row, DEC-801). No finding is in scope, ordinary
  work yes and fails open or loses work, so none blocks and no round follows (DEC-1010 item 1). The rows ride along if the
  ticket resumes (DEC-802).
- **Rows for the CTO's real run.** A (a `DRAW.txt` line written with a literal `SEED+k=`, as the brief's own wording and
  the CTO's launch rehearsal write it, is refused as `DRAW_LINE_BAD` / `DRAW_LINES_MISMATCH`) and B (an alternative
  source without `lines`, shaped like the brief's section 7 example, refuses the whole set as `SOURCE_NO_LINES`) can make
  the CTO's run on the real delivery fail closed falsely. If either code appears, the ticket resumes with a test-design
  batch for A and B (option (ii) for B) and a narrow check; no other finding needs action before the CTO's run.

"""
open("/home/usain/gov-os-worktrees/W2-94/docs/probes/DAEO-g87r/PR-DAEO-g87r.md", "w", encoding="utf-8").write(head + "\n".join(body) + "\n")
